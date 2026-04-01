
NODES = [
    { "id": "N0", "label": "인간", "properties": { "name": "지우" } },
    { "id": "N1", "label": "포켓몬", "properties": { "name": "피카츄" } },
    { "id": "N2", "label": "인간", "properties": { "name": "이슬" } },
    { "id": "N3", "label": "포켓몬", "properties": { "name": "스PEAROW" } },
    { "id": "N4", "label": "포켓몬", "properties": { "name": "스피어오위" } },
    { "id": "N5", "label": "포켓몬", "properties": { "name": "피케트피" } },
    { "id": "N6", "label": "포켓몬", "properties": { "name": "메탈로드" } },
    { "id": "N7", "label": "포켓몬", "properties": { "name": "미터파드" } },
    { "id": "N8", "label": "포켓몬", "properties": { "name": "비글또토" } },
    { "id": "N9", "label": "조커", "properties": { "name": "제시" } },
    { "id": "N10", "label": "조커", "properties": { "name": "자임스" } },
    { "id": "N11", "label": "포켓몬", "properties": { "name": "메오와치" } },
    { "id": "N12", "label": "포켓몬", "properties": { "name": "부테프라이" } },
    { "id": "N13", "label": "포켓몬", "properties": { "name": "메타포드" } },
    { "id": "N14", "label": "인간", "properties": { "name": "가리오ak" } },
    { "id": "N15", "label": "과학자", "properties": { "name": "올 프로포셔날 아 Ook" } },
    { "id": "N16", "label": "인간", "properties": { "name": "지우" } },
    { "id": "N17", "label": "도시", "properties": { "name": "비규리안 시티" } },
    { "id": "N18", "label": "도시", "properties": { "name": "피봇 시티" } }
]

KOREAN_NODE_MAP = {
    "지우": "Ash Ketchum",
    "피카츄": "Pikachu",
    "이슬": "Misty",
    "스PEAROW": "Spearow",
    "스피어오위": "Spearow",
    "메탈로드": "Metapod",
    "미터파드": "Caterpie",
    "비글또토": "Pidgeotto",
    "제시": "Jessie",
    "자임스": "James",
    "메오와치": "Meowth",
    "부테프라이": "Butterfree",
    "가리오ak": "Gary Oak",
    "올 프로포셔날 아 Ook": "Professor Samuel Oak"
}

RELATIONSHIPS = [
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
    }
]

RELATIONSHIP_TYPES = [
    "OWNS", "BATTLES", "BATTLES_TRAINER"
]
