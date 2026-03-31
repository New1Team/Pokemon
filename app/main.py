from ollama import Client
import json
import re
import os
import time
import csv
from typing import List, Optional, Dict, Union
from requests import get
from bs4 import BeautifulSoup as bs
from pydantic import BaseModel
from utils.data import KOREAN_NODE_MAP, NODES
from settings import settings
import unicodedata

# 속성 타입 정의 (문자열, 숫자, bool, None)
PropertyValue = Union[str, int, float, bool, None]


# ---------------------------
# 지식 그래프 기본 모델 정의
# ---------------------------
class Node(BaseModel):
    id: str
    label: str
    properties: Optional[Dict[str, PropertyValue]] = None


class Relationship(BaseModel):
    type: str
    start_node_id: str
    end_node_id: str
    properties: Optional[Dict[str, PropertyValue]] = None


class GraphResponse(BaseModel):
    nodes: List[Node]
    relationships: List[Relationship]

# [추가] 라벨 정규화 함수
# 이유: LLM이 "포켓몬", "포ケット몬", "Pokemon"처럼 흔들리게 출력해도
# 파이썬에서 최종적으로 "인간" / "포켓몬" 두 값으로 강제 통일하기 위해
def normalize_label(label: str) -> str:
    if not label:
        return "기타"

    raw = unicodedata.normalize("NFKC", label).strip().lower()

    if any(keyword in raw for keyword in ["포켓", "pokemon", "pokémon", "ポケモン", "켓몬", "포ケ"]):
        return "포켓몬"

    if any(keyword in raw for keyword in ["인간", "human", "person", "trainer", "character"]):
        return "인간"

    return label.strip()


# [추가] 이름 비교용 정규화 함수
# 이유: 공백, 대소문자, 악센트 차이, 특수문자 차이 때문에 번역 테이블 매칭이 깨지는 걸 줄이기 위해
def normalize_name_key(name: str) -> str:
    if not name:
        return ""

    text = unicodedata.normalize("NFKC", name).strip().lower()
    text = text.replace("’", "'").replace("`", "'")
    text = re.sub(r"[^a-zA-Z0-9가-힣 ]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# [추가] 번역/별칭 매핑 함수
# 이유: KOREAN_NODE_MAP이 완전일치만으로는 부족해서,
# 공백/대소문자/부분차이까지 흡수하며 한국어 이름으로 최대한 통일하기 위해
def canonicalize_name(raw_name: str) -> str:
    if not raw_name:
        return ""

    cleaned = raw_name.strip()
    cleaned_key = normalize_name_key(cleaned)

    # 1차: 완전 일치 매핑
    for eng, kor in KOREAN_NODE_MAP.items():
        if cleaned_key == normalize_name_key(eng):
            return kor

    # 2차: 포함/부분 매칭
    for eng, kor in KOREAN_NODE_MAP.items():
        eng_key = normalize_name_key(eng)
        if cleaned_key == eng_key or cleaned_key in eng_key or eng_key in cleaned_key:
            return kor

    # 3차: 이미 한글이면 그대로 사용
    if re.search(r"[가-힣]", cleaned):
        return cleaned

    # 4차: 끝까지 매칭 안 되면 원문 유지

    return cleaned


# [추가] 노드용 canonical key 생성
# 이유: LLM이 매번 N0, N1 같은 임시 ID를 주므로,
# 실제 통합 기준은 "정규화된 라벨 + 정규화된 이름"으로 잡아야 하기 때문
def make_node_canonical_key(node: Node) -> str:
    label = normalize_label(node.label)
    name = canonicalize_name((node.properties or {}).get("name", ""))
    return f"{label}::{normalize_name_key(name)}"


# [추가] 노드/관계 데이터 클리닝 함수
# 이유: 에피소드별로 받은 그래프를 저장하기 전에
# 라벨/이름/ID를 먼저 정리해야 중복과 관계 꼬임을 줄일 수 있기 때문
def clean_graph_response(graph_response: GraphResponse) -> GraphResponse:
    canonical_node_map = {}
    old_to_new_id_map = {}

    for node in graph_response.nodes:
        if node.properties is None:
            node.properties = {}

        # [추가] 라벨 정규화
        # 이유: "포ケット몬", "Pokemon", "포켓몬" 등 흔들리는 라벨 통합
        node.label = normalize_label(node.label)

        raw_name = node.properties.get("name", "")
        canonical_name = canonicalize_name(raw_name)

        # [추가] 이름 한국어 기준 통일
        # 이유: 영어/한자/혼합 표기를 하나의 대표 이름으로 통합
        node.properties["name"] = canonical_name

        canonical_key = make_node_canonical_key(node)
        canonical_id = f"NODE_{abs(hash(canonical_key))}"

        old_to_new_id_map[node.id] = canonical_id

        if canonical_key not in canonical_node_map:
            canonical_node_map[canonical_key] = Node(
                id=canonical_id,
                label=node.label,
                properties=node.properties.copy()
            )

    cleaned_relationships = []
    seen_relationships = set()

    for rel in graph_response.relationships:
        start_id = old_to_new_id_map.get(rel.start_node_id)
        end_id = old_to_new_id_map.get(rel.end_node_id)

        # [추가] 존재하지 않는 노드를 가리키는 관계 제거
        # 이유: LLM이 관계는 만들었는데 해당 노드가 정규화 과정에서 탈락/통합될 수 있기 때문
        if not start_id or not end_id:
            continue

        rel_props = rel.properties or {}

        cleaned_rel = Relationship(
            type=rel.type.strip().upper(),
            start_node_id=start_id,
            end_node_id=end_id,
            properties=rel_props
        )

        rel_key = (
            cleaned_rel.type,
            cleaned_rel.start_node_id,
            cleaned_rel.end_node_id,
            json.dumps(cleaned_rel.properties, ensure_ascii=False, sort_keys=True)
        )

        # [추가] 관계 중복 제거
        # 이유: 같은 에피소드 안에서 동일 관계가 중복 출력될 수 있기 때문
        if rel_key not in seen_relationships:
            seen_relationships.add(rel_key)
            cleaned_relationships.append(cleaned_rel)

    return GraphResponse(
        nodes=list(canonical_node_map.values()),
        relationships=cleaned_relationships
    )

# [추가] 벤치마크 CSV 저장 함수
# 이유: 모델별/에피소드별 처리시간, 성공률, 응답량을 누적 저장해야
# 나중에 성능 비교를 수치로 할 수 있기 때문
def append_benchmark_row(row: dict, csv_path: str = "output/model_benchmark_results.csv"):
    os.makedirs("output", exist_ok=True)

    file_exists = os.path.exists(csv_path)

    with open(csv_path, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


# [추가] 실패한 LLM 원문 저장 함수
# 이유: JSON 파싱 실패 원인을 나중에 모델별로 다시 비교/분석할 수 있게 하기 위해
def save_failed_response(episode_no: str, model_name: str, raw_text: str):
    os.makedirs("output/failed_responses", exist_ok=True)
    safe_model_name = model_name.replace(":", "_").replace("/", "_")
    path = f"output/failed_responses/{episode_no}_{safe_model_name}.txt"

    with open(path, "w", encoding="utf-8") as f:
        f.write(raw_text if raw_text else "응답 없음")


# ----------------------------------------
# LLM에 전달되는 템플릿: 노드와 관계 추출 규칙
# ----------------------------------------
UPDATED_TEMPLATE = f"""
You are a top-tier algorithm designed for extracting information in structured formats to build a knowledge graph.
Extract the entities (nodes) and specify their type from the following text, but you MUST select nodes ONLY from the following predefined set.
Do not create any new nodes or use names that do not exactly match one in the NODES list.

Also extract the relationships between these nodes. Return the result as JSON using the following format:

{{
  "nodes": [
    {{"id": "N0", "label": "인간", "properties": {{"name": "Ash Ketchum"}}}}
  ],
  "relationships": [
    {{"type": "BATTLES", "start_node_id": "N0", "end_node_id": "N3", "properties": {{"outcome": "victory", "badge": "Boulder Badge"}}}}
  ]
}}

Additional rules:
- Use only nodes from the NODES list. Do not invent or substitute nodes.
- Skip any relationship if one of its entities is not in NODES.
- Only output valid relationships where both endpoints exist in NODES and the direction matches their types.
- Return ONLY valid JSON.
- Do NOT include explanations, markdown code blocks, or extra text.
- Every key and every string value must use double quotes.
- label must be one of: "인간", "포켓몬"

### ALLOWED NODES LIST:
{json.dumps(NODES, ensure_ascii=False)}
"""


# ---------------------------
# Ollama LLM 호출 함수
# ---------------------------
def llm_call_structured(prompt: str, model: str = "gemma3:4b"):
    print(f"DEBUG: 현재 접속 시도 중인 서버 주소 -> {settings.ollama_host}")
    client = Client(host=settings.ollama_host)

    benchmark = {
        "model": model,
        "success": False,
        "llm_time_sec": None,
        "parse_time_sec": None,
        "total_time_sec": None,
        "response_chars": 0,
        "nodes_count": 0,
        "relationships_count": 0,
        "error": None,
        "raw_response": None,
    }
    # [추가] raw_response 보관
    # 이유: 실패했을 때 원문 저장/분석용으로 필요

    total_start = time.perf_counter()

    try:
        llm_start = time.perf_counter()
        response = client.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        llm_end = time.perf_counter()

        text = response["message"]["content"]
        benchmark["raw_response"] = text
        benchmark["llm_time_sec"] = round(llm_end - llm_start, 4)
        benchmark["response_chars"] = len(text)

        parse_start = time.perf_counter()

        json_match = re.search(r"\{.*\}", text, re.S)
        if not json_match:
            raise Exception("모델 응답에서 JSON 구조({ })를 찾지 못했습니다.")

        clean_json_text = json_match.group(0)
        parsed = json.loads(clean_json_text)
        graph_response = GraphResponse(**parsed)

        parse_end = time.perf_counter()
        benchmark["parse_time_sec"] = round(parse_end - parse_start, 4)
        benchmark["nodes_count"] = len(graph_response.nodes)
        benchmark["relationships_count"] = len(graph_response.relationships)
        benchmark["success"] = True

        return graph_response, benchmark

    except Exception as e:
        benchmark["error"] = str(e)
        print("\n❌ JSON 파싱 에러 발생!")
        print(f"에러 메시지: {e}")
        print(f"LLM 응답 원문:\n{benchmark['raw_response'] if benchmark['raw_response'] else '응답 없음'}\n")
        # [수정] raw_response를 benchmark에 저장해둔 값을 사용
        # 이유: 예외 상황에서도 동일한 방식으로 원문 접근 가능하게 하기 위해
        raise

    finally:
        total_end = time.perf_counter()
        benchmark["total_time_sec"] = round(total_end - total_start, 4)
        print(
            f"⏱ 모델={benchmark['model']} | "
            f"LLM={benchmark['llm_time_sec']}초 | "
            f"Parse={benchmark['parse_time_sec']}초 | "
            f"Total={benchmark['total_time_sec']}초"
        )


# ------------------------------------------------------
# 여러 에피소드 그래프를 통합하기 위한 함수
# ------------------------------------------------------
# [수정] 에피소드별 그래프 통합 함수
# 이유: LLM의 임시 node.id는 전역적으로 안정적이지 않으므로,
# 통합 기준을 정규화된 label + name 기준으로 바꿔야 같은 인물/포켓몬을 제대로 합칠 수 있기 때문
def combine_chunk_graphs(chunk_graphs: List[GraphResponse]) -> GraphResponse:
    unique_nodes = {}
    all_relationships = []
    seen_relationships = set()

    for chunk_graph in chunk_graphs:
        for node in chunk_graph.nodes:
            node_key = make_node_canonical_key(node)

            if node_key not in unique_nodes:
                unique_nodes[node_key] = node

        for rel in chunk_graph.relationships:
            rel_key = (
                rel.type,
                rel.start_node_id,
                rel.end_node_id,
                json.dumps(rel.properties or {}, ensure_ascii=False, sort_keys=True)
            )
            if rel_key not in seen_relationships:
                seen_relationships.add(rel_key)
                all_relationships.append(rel)

    return GraphResponse(
        nodes=list(unique_nodes.values()),
        relationships=all_relationships
    )


# ------------------------------------------------------
# 수집된 데이터를 LLM으로 처리하여 그래프 생성
# ------------------------------------------------------
def process_data(episodes: List[dict], model_name: str = "gemma3:4b") -> GraphResponse:
    print("=== 데이터 처리 시작 ===")

    chunk_graphs: List[GraphResponse] = []

    for episode in episodes:
        if not episode.get("synopsis"):
            print(f"에피소드 S{episode['season']}E{episode['episode_in_season']:02d}: 시놉시스가 없어 건너뜀")
            continue

        episode_no = f"S{episode['season']}E{episode['episode_in_season']:02d}"
        print(f"에피소드 처리 중: 시즌 {episode['season']}, 에피소드 {episode['episode_in_season']}")

        episode_start = time.perf_counter()
        prompt = UPDATED_TEMPLATE + f"\n\n입력값:\n{episode['synopsis']}"

        try:
            graph_response, benchmark = llm_call_structured(prompt, model=model_name)

            # [수정] LLM 응답을 바로 쓰지 않고 먼저 클리닝
            # 이유: 영어/한자/일본어 혼합 이름, 흔들리는 라벨, 임시 ID를
            # 파이썬에서 통일한 뒤 저장해야 데이터 품질이 올라가기 때문
            graph_response = clean_graph_response(graph_response)

            for relationship in graph_response.relationships:
                if relationship.properties is None:
                    relationship.properties = {}
                relationship.properties["episode_number"] = episode_no

            chunk_graphs.append(graph_response)

            episode_end = time.perf_counter()

            row = {
                "episode_no": episode_no,
                "model": model_name,
                "success": True,
                "input_chars": len(episode["synopsis"]),
                "llm_time_sec": benchmark["llm_time_sec"],
                "parse_time_sec": benchmark["parse_time_sec"],
                "llm_total_time_sec": benchmark["total_time_sec"],
                "episode_total_time_sec": round(episode_end - episode_start, 4),
                "response_chars": benchmark["response_chars"],
                "nodes_count": benchmark["nodes_count"],
                "relationships_count": benchmark["relationships_count"],
                "error": "",
            }
            append_benchmark_row(row)

        except Exception as e:
            episode_end = time.perf_counter()

            # [추가] 실패 응답 원문 저장
            # 이유: 어떤 모델이 어떤 형태로 JSON을 깨는지 사후 비교 가능하게 하기 위해
            if "benchmark" in locals() and isinstance(benchmark, dict):
                save_failed_response(
                    episode_no=episode_no,
                    model_name=model_name,
                    raw_text=benchmark.get("raw_response", "")
                )

            row = {
                "episode_no": episode_no,
                "model": model_name,
                "success": False,
                "input_chars": len(episode["synopsis"]),
                "llm_time_sec": benchmark["llm_time_sec"] if "benchmark" in locals() else None,
                "parse_time_sec": benchmark["parse_time_sec"] if "benchmark" in locals() else None,
                "llm_total_time_sec": benchmark["total_time_sec"] if "benchmark" in locals() else None,
                "episode_total_time_sec": round(episode_end - episode_start, 4),
                "response_chars": benchmark["response_chars"] if "benchmark" in locals() else 0,
                "nodes_count": 0,
                "relationships_count": 0,
                "error": str(e),
            }
            # [수정] 실패 시에도 benchmark 값이 있으면 기록
            # 이유: 실패한 케이스도 호출 시간 비교에 포함해야 모델 안정성 비교가 가능하기 때문

            append_benchmark_row(row)

            print(f"  - 에피소드 처리 중 오류 발생: {e}")
            continue

    if not chunk_graphs:
        raise Exception("그래프를 성공적으로 추출하지 못했습니다.")

    print(f"총 {len(chunk_graphs)}개 에피소드 처리 완료")
    return combine_chunk_graphs(chunk_graphs)


# ------------------------------------------------------
# 위키피디아 에피소드 데이터 수집
# ------------------------------------------------------
def fetch_episode(link: str, season: int) -> List[dict]:
    print(f"Fetching Season {season} from: {link}")

    headers = {"User-Agent": "Mozilla/5.0"}
    response = get(link, headers=headers)
    response.raise_for_status()
    # [추가] HTTP 에러 즉시 확인
    # 이유: HTML 구조 문제로 착각하지 않고 요청 실패를 바로 분리하기 위해

    soup = bs(response.text, "html.parser")
    table = soup.select_one("table.wikitable.plainrowheaders.wikiepisodetable")

    if table is None:
        raise Exception(f"에피소드 테이블을 찾지 못했습니다: {link}")
    # [추가] 테이블 존재 여부 명시 확인
    # 이유: 위키 구조가 바뀌었을 때 원인을 바로 알 수 있게 하기 위해

    episodes = []
    rows = table.select("tr.vevent.module-episode-list-row")

    for i, row in enumerate(rows, start=1):
        synopsis = None
        synopsis_row = row.find_next_sibling("tr", class_="expand-child")
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

    os.makedirs("output", exist_ok=True)

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
            {"url": "https://en.wikipedia.org/wiki/Pok%C3%A9mon:_Indigo_League#References", "season": 1},
        ]
        all_episodes = []

        for link in episode_links:
            try:
                episodes = fetch_episode(link["url"], link["season"])
                all_episodes.extend(episodes)
            except Exception as e:
                print(f"Error fetching data from {link}: {e}")
                continue

        print(f"총 {len(all_episodes)}개 에피소드 수집 완료")

        model_name = "gemma3:4b"
        final_graph = process_data(all_episodes, model_name=model_name)

        save_output(all_episodes, final_graph)

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