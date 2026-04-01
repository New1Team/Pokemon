
NODES = [
    { "id": "N0", "label": "인간", "properties": { "name": "지우" } },
    { "id": "N1", "label": "포켓몬", "properties": { "name": "피카츄" } },
    { "id": "N2", "label": "인간", "properties": { "name": "이슬" } },
    { "id": "N3", "label": "포켓몬", "properties": { "name": "스pearow" } },
    { "id": "N4", "label": "포켓몬", "properties": { "name": "스피어로" } },
    { "id": "N5", "label": "인간", "properties": { "name": "가이 오크" } },
    { "id": "N6", "label": "포켓몬", "properties": { "name": "루시즈의 라이치로" } },
    { "id": "N7", "label": "인간", "properties": { "name": "불꽃나무" } },
    { "id": "N8", "label": "포켓몬", "properties": { "name": "카터피" } },
    { "id": "N9", "label": "포켓몬", "properties": { "name": "버터프리" } },
    { "id": "N10", "label": "포켓몬", "properties": { "name": "피지고또" } },
    { "id": "N11", "label": "구조체", "properties": { "name": "로키스터" } },
    { "id": "N12", "label": "포켓몬", "properties": { "name": "메탈로드" } },
    { "id": "N13", "label": "포켓몬", "properties": { "name": "메타포드" } },
    { "id": "N14", "label": "구조체", "properties": { "name": "메트로드" } },
    { "id": "N15", "label": "구조체", "properties": { "name": "베드릴" } },
    { "id": "N16", "label": "포켓몬", "properties": { "name": "메타부플러" } }
]

KOREAN_NODE_MAP = {
    "Ash Ketchum": "지우",
    "Pikachu": "피카츄",
    "Misty": "이슬"
}

RELATIONSHIP_EXAMPLES = [
    {
        "type": "OWNS",
        "start_node_id": "N0",
        "end_node_id": "N1",
        "properties": { "since": "Ep 1", "comment": "피카츄를 끌고 다니며 Pikachu와의 첫 만남" }
    },
    {
        "type": "BATTLES",
        "start_node_id": "N16",
        "end_node_id": "N5",
        "properties": { "outcome": "defeat", "context": "피카츄와 루시즈의 라이치로의 싸움" }
    },
    {
        "type": "OWNS",
        "start_node_id": "N2",
        "end_node_id": "N8",
        "properties": { "since": "Ep 3", "comment": "피카츄와 카터피를 소유하며 첫 만남" }
    },
    {
        "type": "BATTLES",
        "start_node_id": "N16",
        "end_node_id": "N5",
        "properties": { "outcome": "victory", "context": "메탈로드와의 싸움에서 승리" }
    },
    {
        "type": "OWNS",
        "start_node_id": "N0",
        "end_node_id": "N9",
        "properties": { "since": "Ep 3", "comment": "버터프리를 소유하며 카터피와의 첫 만남" }
    },
    {
        "type": "OWNS",
        "start_node_id": "N0",
        "end_node_id": "N10",
        "properties": { "since": "Ep 3", "comment": "피지고또를 소유하며 카터피와의 첫 만남" }
    },
    {
        "type": "BATTLES",
        "start_node_id": "N9",
        "end_node_id": "N15",
        "properties": { "outcome": "defeat", "context": "베드릴과 카터피의 싸움에서 패배" }
    },
    {
        "type": "EVOLVES_INTO",
        "start_node_id": "N8",
        "end_node_id": "N9",
        "properties": { "since": "Ep 3", "comment": "카터피가 버터프리로 진화" }
    },
    {
        "type": "OWNS",
        "start_node_id": "N0",
        "end_node_id": "N16",
        "properties": { "since": "Ep 4", "comment": "메타부플러를 소유하며 메탈로드와의 첫 만남" }
    },
    {
        "type": "BATTLES",
        "start_node_id": "N16",
        "end_node_id": "N5",
        "properties": { "outcome": "victory", "context": "메타부플러, 피카츄와 루시즈의 라이치로와의 싸움에서 승리" }
    },
    {
        "type": "OWNS",
        "start_node_id": "N0",
        "end_node_id": "N16",
        "properties": { "since": "Ep 5", "comment": "메타부플러를 소유하며 브로크와의 싸움에서 피카츄가 그를 도우며 승리" }
    },
    {
        "type": "BATTLES",
        "start_node_id": "N16",
        "end_node_id": "N5",
        "properties": { "outcome": "defeat", "context": "메타부플러와 루시즈의 라이치로와의 싸움에서 패배" }
    },
    {
        "type": "BATTLES",
        "start_node_id": "N16",
        "end_node_id": "N5",
        "properties": { "outcome": "victory", "context": "메타부플러와 루시즈의 라이치로와의 다시 한 번의 싸움에서 승리" }
    }
]

RELATIONSHIP_TYPES = [
    "OWNS", "BATTLES", "EVOLVES_INTO"
]
