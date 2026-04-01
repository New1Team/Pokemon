from pydantic import BaseModel
from typing import Optional, Dict, Union, List
import ollama
import json
import re
import os
import pprint
from requests import get
from bs4 import BeautifulSoup as bs
import ast


# ---------------------------
# 지식 그래프 기본 모델 정의
# ---------------------------

# 속성 타입 정의 (문자열, 숫자, bool, None)
PropertyValue = Union[str, int, float, bool, None]

class Node(BaseModel):
  id: str  # 노드 ID (예: N0)
  label: str  # 노드 타입 (예: "인간")
  properties: Optional[Dict[str, PropertyValue]] = None  # 속성 딕셔너리

class Relationship(BaseModel):
  type: str  # 관계 유형
  start_node_id: Optional[str]=None # 시작 노드 ID
  end_node_id: Optional[str]=None  # 끝 노드 ID
  properties: Optional[Dict[str, PropertyValue]] = None  # 관계 속성

class GraphResponse(BaseModel):
    nodes: List[Node]
    relationships: List[Relationship]

# ----------------------------------------
# LLM에 전달되는 템플릿: 노드와 관계 생성
# ----------------------------------------

UPDATED_TEMPLATE = """
# Role
너는 복잡한 비정형 데이터에서 핵심 정보를 추출하여 구조화된 형태로 정리하는 **탑티어 데이터 관리자(Data Administrator)**이다. 너의 주 업무는 제공된 텍스트를 분석하여 지정된 스키마에 따라 정확한 데이터를 수집하고 전달하는 것이다.

# Goal
제공되는 [원본 데이터]를 바탕으로 아래의 [데이터 수집 가이드라인]을 엄격히 준수하여 데이터를 추출하라. 추출된 결과는 반드시 Python 파일(`.py`) 형식으로 반환해야 한다.

# 데이터 수집 가이드라인 (Internal Logic)

1. **Strict Entity Mapping (한글화):**
   - 추출된 모든 `name`은 `KOREAN_NODE_MAP`을 참조하여 반드시 **한글**로 변환하여 저장한다.
   - 매핑 테이블에 없는 이름은 추출 대상에서 제외하거나, 반드시 기존 `NODES` 리스트의 형식을 유지한다.

2. **1:1 ID-Name Integrity:**
   - 동일한 인물/포켓몬은 텍스트 내에서 여러 번 등장하더라도 반드시 **하나의 고유 ID**(`N0`, `N1` 등)만 부여해야 한다.
   - 새로운 노드가 발견될 경우 기존 ID 체계를 이어받아 순차적으로 부여한다.

3. **Relationship Filtering:**
   - `RELATIONSHIP_TYPES`에 정의된 관계만 추출한다.
   - 관계의 `start_node_id`와 `end_node_id` 중 하나라도 누락된 관계는 절대 생성하지 않는다.

4. **Zero-Null Policy:**
   - `properties` 내에 값이 `None`, `null`, 또는 알 수 없는 경우 해당 Key를 아예 생성하지 않는다.

5. **Output Format:**
   - 결과물은 다른 파이썬 파일에서 바로 `import` 할 수 있도록 `nodes = [...]`, `relationships = [...]` 형태의 유효한 Python 코드로 작성한다.

# 출력 예시
```
NODES = [
    { "id": "N0", "label": "인간", "properties": { "name": "Ash Ketchum" } },
    { "id": "N1", "label": "인간", "properties": { "name": "Ash" } },
    { "id": "N2", "label": "인간", "properties": { "name": "Misty" } }]
    ,
KOREAN_NODE_MAP = {
    "Ash Ketchum": "지우",
    "Pikachu": "피카츄",
    "Misty": "이슬"
    }
RELATIONSHIP_EXAMPLES = [
    {
        "type": "OWNS",
        "start_node_id": "N0",
        "end_node_id": "N16",
        "properties": {"since": "Episode 1", "comment": "Ash and Pikachu's first meeting"}
    },
    {
        "type": "BATTLES",
        "start_node_id": "N16",
        "end_node_id": "N20",
        "properties": {"outcome": "victory", "context": "Pikachu vs Lt. Surge's Raichu"}
    }]
RELATIONSHIP_TYPES = [
    "OWNS", "BATTLES", "BATTLES_TRAINER"]
```
"""

# ---------------------------
# Ollama LLM 호출 함수
# ---------------------------
def llm_call_structured(prompt: str, model: str = "qwen2.5:7b"):

  final_prompt = UPDATED_TEMPLATE + "\n\n[원본 데이터]\n" + prompt + """
    Return ONLY valid Python code. Do NOT include explanations.
    Do NOT wrap the entire output in quotes or triple quotes.
    Start directly with NODES = [...], etc.
    """

  # Ollama에 LLM 요청
  response = ollama.chat(
    model=model,
    messages=[{"role": "user", "content": final_prompt}]
  )

  # 모델 응답 텍스트 추출
  text = response["message"]["content"]
  print("text: ", text)
  clean_text = text.replace('```python','').replace('```','')
  return clean_text

#   def extract_var(var_name, clean_text, default_value):
#     clean_text = clean_text.replace('```', '').strip()
#     pattern = rf"{var_name}\s*=\s*([\[{{].*?[\]}}])"
#     match = re.search(pattern, clean_text, re.S)
#     if match:
#         content = match.group(1).strip()
#         try:
# #             # ast.literal_eval 시도
#             return ast.literal_eval(content)
#         except (SyntaxError, ValueError) as e:
# #             # 괄호가 안 닫혔을 경우 (SyntaxError) 등 처리
#             print(f"⚠️ {var_name} 파싱 실패 (문법 오류): {e}")
            
# #             # [임시 방편] 괄호가 안 닫혔다면 강제로 닫아보는 시도 (선택 사항)
# #             if "was never closed" in str(e):
# #                 if content.startswith('['): content += ']'
# #                 elif content.startswith('{'): content += '}'
# #                 try:
# #                     print(ast.literal_eval(content))
# #                     return ast.literal_eval(content)
# #                 except:
# #                     return default_value
#             return default_value
#     return default_value
    
    # return ast.literal_eval(match.group(1)) if match else None

#   return {
#     "nodes": extract_var("NODES", text, []),
#     "korean_node_map": extract_var("KOREAN_NODE_MAP", text, {}),
#     "relationship_examples": extract_var("RELATIONSHIP_EXAMPLES", text, []),
#     "relationship_types": extract_var("RELATIONSHIP_TYPES", text, [])}



# ------------------------------------------------------
# 위키피디아 에피소드 데이터 수집
# ------------------------------------------------------
def fetch_episode(link: str) -> List[dict]:
  # 에피소드 명 팔로우 위한 코드
  match = re.search(r"mon:_([^#\s?]+)", link)
  if match:
    season = match.group(1)
    print(f"Fetching Season {season} from: {link}")
  else:
    season = "Unknown_Season"
  headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}  # 요청 헤더
  response = get(link, headers=headers)  # GET 요청
  
  soup = bs(response.text, "html.parser")  # HTML 파싱
  table = soup.select_one("table.wikitable.plainrowheaders.wikiepisodetable")  # 에피소드 테이블 찾기

  episodes = []
  rows = table.select("tr.vevent.module-episode-list-row")  # 각 에피소드 row

  for i, row in enumerate(rows, start=1):  # 에피소드 번호 생성
    synopsis = None
    synopsis_row = row.find_next_sibling("tr", class_="expand-child")  # 시놉시스 row 찾기
    if synopsis_row:
      synopsis_cell = synopsis_row.select_one("td.description div.shortSummaryText")
      synopsis = synopsis_cell.get_text(strip=True) if synopsis_cell else None

    episodes.append({
      "season": season,
      "episode_in_season": i,
      "synopsis": synopsis,
    })
  
  return episodes

# ------------------------------------------------------
# 출력 파일 저장
# ------------------------------------------------------

def save_output(clean_text):
# def save_output(extracted_data: Dict):
  print("=== 결과 저장 ===")
  os.makedirs("data2", exist_ok=True)  # 폴더 생성
#   with open("data2/1_원본데이터.py", "w", encoding="utf-8") as f:
#       f.write("# -*- coding: utf-8 -*-\n")
#       f.write(pprint.pformat(episodes, indent=2, sort_dicts=False))
#   print("원본 데이터 저장: data2/1_원본데이터.py")
  
  with open("data2/지식그래프_최종.py", "w", encoding="utf-8") as f:
      f.write(clean_text)
    #   f.write(f"NODES = {pprint.pformat(extracted_data.get('nodes',[]), indent=2, sort_dicts=False)}\n")
    #   f.write(f"KOREAN_NODE_MAP = {pprint.pformat(extracted_data.get('korean_node_map',{}), indent=2, sort_dicts=False)}\n")
    #   f.write(f"RELATIONSHIP_EXAMPLES = {pprint.pformat(extracted_data.get('relationship_examples', []), indent=2, sort_dicts=False)}\n")
    #   f.write(f"RELATIONSHIP_TYPES = {pprint.pformat(extracted_data.get('relationship_types', []), indent=2, sort_dicts=False)}\n")
  print("최종 지식그래프 저장: data2/지식그래프_최종.py")



def main():
  try:
    episode_links = [
      "https://en.wikipedia.org/wiki/Pok%C3%A9mon:_Indigo_League#References",
      # "https://en.wikipedia.org/wiki/Demon_Slayer:_Kimetsu_no_Yaiba_season_2",
      # "https://en.wikipedia.org/wiki/Demon_Slayer:_Kimetsu_no_Yaiba_season_3",
      # "https://en.wikipedia.org/wiki/Demon_Slayer:_Kimetsu_no_Yaiba_season_4",
    ]
    all_episodes = []
    for link in episode_links:
      try:
        episodes = fetch_episode(link)
        all_episodes.extend(episodes)
      except Exception as e:
        print(f"Error fetching data from {link}: {e}")
        continue
    # print(f"총 {len(all_episodes)}개 에피소드 수집 완료")
    summary_text = "\n".join([f"Ep {e['episode_in_season']}: {e['synopsis']}" for e in all_episodes[:5]]) # 테스트용 5개만
    extracted_result = llm_call_structured(summary_text)
    # save_output(all_episodes, extracted_result)
    save_output(extracted_result)
    # final_graph = process_data(all_episodes)
    # save_output(episodes)  # 결과 저장
        
    print("=" * 50)
    print("✅ 지식그래프 생성 완료!")
    # print(f"📊 총 노드 수: {len(final_graph.nodes)}")
    # print(f"🔗 총 관계 수: {len(final_graph.relationships)}")    
  except Exception as e:
    print(f"오류 발생: {e}")
    return 1
  return 0

# ------------------------------------------------------
# 프로그램 실행
# ------------------------------------------------------
if __name__ == "__main__":
  exit(main())


## 발표 이슈
## 5개정도 단위로 끊지 않고 82개 에피소드 다 긁어오면 ai가 자체적으로 요약해버림