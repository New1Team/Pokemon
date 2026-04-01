import ollama
import json
import re
import os
from typing import List, Optional, Dict, Union
from requests import get
from bs4 import BeautifulSoup as bs
from pydantic import BaseModel
from utils.data import KOREAN_NODE_MAP, NODES, RELATIONSHIP_TYPES # 데이터 받아오기

# 속성 타입 정의 (문자열, 숫자, bool, None)
PropertyValue = Union[str, int, float, bool, None]

# ---------------------------
# 지식 그래프 기본 모델 정의
# ---------------------------
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
  nodes: List[Node]  # 노드 리스트
  relationships: List[Relationship]  # 관계 리스트

# ----------------------------------------
# LLM에 전달되는 템플릿: 노드와 관계 추출 규칙
# ----------------------------------------
UPDATED_TEMPLATE = """
### Role
You are a top-tier algorithm designed for extracting information in structured formats to build a rigorous knowledge graph. Your goal is to extract entities (nodes) and their relationships from the provided text, strictly adhering to the following constraints.

### 🚫 CRITICAL CONSTRAINTS (Zero-Tolerance Rules)
1. **Strict Whitelist Only:** You MUST select nodes ONLY from the predefined `NODES`. Do not invent, infer, or substitute any nodes. If a name in the text does not have an exact match in the `NODES` or the `KOREAN_NODE_MAP`, **DO NOT extract it.**
2. **1:1 ID-to-Name Mapping:** Each unique `name` must map to exactly one `id`. You must ensure that the `nodes` list in your JSON output contains **NO DUPLICATES**. If a character appears multiple times in the text, represent them as a single node entry with their assigned unique ID.
3. **Forbidden Names:** Any name not explicitly defined in the `KOREAN_NODE_MAP` must be strictly excluded from the final `nodes` list.
4. **Zero-Null Policy:** In the `properties` object of both nodes and relationships, **DO NOT include any keys with null, empty, or unknown values.** (e.g., If there is no badge mentioned, the `"badge"` key must be entirely omitted from the JSON. Do not write `"badge": null`).
5. **Relationship Filtering:** Skip any relationship if either the `start_node_id` or `end_node_id` is not present in the allowed `NODES_LIST`.

### 🔗 Allowed Relationship Types (REL_TYPES)
<<REL_TYPES>>

### 📋 Predefined Lists (Whitelist)
* **NODES:** <<NODES>>

* **KOREAN_NODE_MAP:** <<KOREAN_NODE_MAP>>

### 📤 Output Format (Strict JSON)
Return the result as a single JSON object. If no valid information is found, return empty lists. **Ensure the final JSON does not contain any null values.**

```json
{
  "nodes": [
    {
      "id": "N0",
      "label": "인간",
      "properties": {
        "name": "지우"
      }
    }
  ],
  "relationships": [
    {
      "type": "BATTLES",
      "start_node_id": "N0",
      "end_node_id": "N16",
      "properties": {
        "outcome": "victory",
        "episode_number": "S01E01"
        /* Notice: "badge" key is omitted here because its value was missing/null */
      }
    }
  ]
}
```
**Final Reminder**: If any entity, relationship, or property value is missing from the provided whitelist or the text, simply ignore it. Accuracy and data integrity are your highest priorities.
"""


# ---------------------------
# Ollama LLM 호출 함수
# ---------------------------
def llm_call_structured(prompt: str, model: str = "mistral-nemo:12b") -> GraphResponse:

  final_prompt = prompt + """
  Return ONLY valid JSON. Do NOT include explanations or commentary.
  """

  # Ollama에 LLM 요청
  response = ollama.chat(
    model=model,
    messages=[{"role": "user", "content": final_prompt}]
  )

  # 모델 응답 텍스트 추출
  text = response["message"]["content"]
  
  # JSON 파싱 시도
  try:
    parsed = json.loads(text)
  except json.JSONDecodeError:
    # 전체 텍스트에서 JSON 블록만 추출
    json_text = re.search(r"\{.*\}", text, re.S)
    if not json_text:
      raise Exception("모델 응답에서 JSON을 찾지 못했습니다.")
    parsed = json.loads(json_text.group(0))
  
  return GraphResponse(**parsed)  # pydantic 모델로 변환 후 반환

# ------------------------------------------------------
# 여러 에피소드 그래프를 통합하기 위한 함수
# ------------------------------------------------------
def combine_chunk_graphs(chunk_graphs: list) -> GraphResponse:
  all_nodes = []  # 모든 노드를 담을 리스트
  for chunk_graph in chunk_graphs:
    for node in chunk_graph.nodes:
      all_nodes.append(node)
  
  all_relationships = []  # 모든 관계를 담을 리스트
  for chunk_graph in chunk_graphs:
    for relationship in chunk_graph.relationships:
      all_relationships.append(relationship)
  
  unique_nodes = []  # 중복 제거된 최종 노드 리스트
  seen = set()  # 노드 중복 체크용

  for node in all_nodes:
    node_key = (node.id, node.label, str(node.properties))  # 노드 고유값 생성
    if node_key not in seen:
      unique_nodes.append(node)
      seen.add(node_key)

  return GraphResponse(nodes=unique_nodes, relationships=all_relationships)

# ------------------------------------------------------
# 수집된 데이터를 LLM으로 처리하여 그래프 생성
# ------------------------------------------------------
def process_data(episodes: List[dict]) -> GraphResponse:
  print("=== 데이터 처리 시작 ===")

  chunk_graphs: List[GraphResponse] = []  # 에피소드별 그래프 저장
  # prompt 변수처리 위한 코드
  full_template = UPDATED_TEMPLATE.replace("<<NODES>>", json.dumps(NODES, ensure_ascii=False))
  full_template = full_template.replace("<<REL_TYPES>>", str(RELATIONSHIP_TYPES))  
  full_template = full_template.replace("<<KOREAN_NODE_MAP>>", str(KOREAN_NODE_MAP))  
  for episode in episodes:
    if not episode.get("synopsis"):
      print(f"에피소드 S{episode['season']}E{episode['episode_in_season']:02d}: 시놉시스가 없어 건너뜀")
      continue
        
    print(f"에피소드 처리 중: 시즌 {episode['season']}, 에피소드 {episode['episode_in_season']}")
    
    try:
      prompt = full_template + f"\n 입력값\n {episode['synopsis']}"  # LLM 입력 프롬프트
      # print("prompt: ", prompt)
      graph_response = llm_call_structured(prompt)  # LLM 호출

      episode_number = f"S{episode['season']}E{episode['episode_in_season']:02d}"  # 에피소드 번호 문자열

      for relationship in graph_response.relationships:
        if relationship.properties is None:
          relationship.properties = {}
        relationship.properties["episode_number"] = episode_number  # 관계에 에피소드 번호 부여
          
      for node in graph_response.nodes:
        if node.properties: # 속성 있을때만 실행
          english_name = node.properties.get("name", "")
          if english_name in KOREAN_NODE_MAP:
            node.properties["name"] = KOREAN_NODE_MAP[english_name]  # 영어 → 한글 변환
      
      chunk_graphs.append(graph_response)  # 결과 저장
        
    except Exception as e:
      print(f"  - 에피소드 처리 중 오류 발생: {e}")
      continue
  
  if not chunk_graphs:
    raise Exception("그래프를 성공적으로 추출하지 못했습니다.")
  
  print(f"총 {len(chunk_graphs)}개 에피소드 처리 완료")
  return combine_chunk_graphs(chunk_graphs)  # 전체 그래프 통합

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

def save_output(episodes: List[dict], final_graph: GraphResponse):
  print("=== 결과 저장 ===")
  
  os.makedirs("output", exist_ok=True)  # output 폴더 생성
  
  with open("output/1_원본데이터.json", "w", encoding="utf-8") as f:
      json.dump(episodes, f, indent=2, ensure_ascii=False)
  print("원본 데이터 저장: output/1_원본데이터.json")
  
  with open("output/지식그래프_최종.json", "w", encoding="utf-8") as f:
      json.dump(final_graph.model_dump(), f, ensure_ascii=False, indent=2)
  print("최종 지식그래프 저장: output/지식그래프_최종.json")

# ------------------------------------------------------
# 메인 실행 함수
# ------------------------------------------------------
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
    print(f"총 {len(all_episodes)}개 에피소드 수집 완료")

    final_graph = process_data(all_episodes)

    save_output(episodes, final_graph)  # 결과 저장
        
    print("=" * 50)
    print("✅ 지식그래프 생성 완료!")
    print(f"📊 총 노드 수: {len(final_graph.nodes)}")
    print(f"🔗 총 관계 수: {len(final_graph.relationships)}")    
  except Exception as e:
    print(f"오류 발생: {e}")
    return 1
  return 0

# ------------------------------------------------------
# 프로그램 실행
# ------------------------------------------------------
if __name__ == "__main__":
  exit(main())
