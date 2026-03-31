NODES = [
    { "id": "N0", "label": "인간", "properties": { "name": "Ash Ketchum" } },
    { "id": "N2", "label": "인간", "properties": { "name": "Misty" } },
    { "id": "N3", "label": "인간", "properties": { "name": "Brock" } },
    { "id": "N4", "label": "인간", "properties": { "name": "Jessie" } },
    { "id": "N5", "label": "인간", "properties": { "name": "James" } },
    { "id": "N6", "label": "인간", "properties": { "name": "Giovanni" } },
    { "id": "N7", "label": "인간", "properties": { "name": "Professor Oak" } },
    { "id": "N8", "label": "인간", "properties": { "name": "Gary Oak" } },
    { "id": "N9", "label": "인간", "properties": { "name": "Nurse Joy" } },
    { "id": "N10", "label": "인간", "properties": { "name": "Officer Jenny" } },
    { "id": "N11", "label": "포켓몬", "properties": { "name": "Bulbasaur" } },
    { "id": "N12", "label": "포켓몬", "properties": { "name": "Charmander" } },
    { "id": "N13", "label": "포켓몬", "properties": { "name": "Squirtle" } },
    { "id": "N14", "label": "포켓몬", "properties": { "name": "Meowth" } },
    { "id": "N15", "label": "포켓몬", "properties": { "name": "Mewtwo" } },
    { "id": "N16", "label": "포켓몬", "properties": { "name": "Pikachu" } },
    { "id": "N17", "label": "포켓몬", "properties": { "name": "Charizard" } },
    { "id": "N18", "label": "포켓몬", "properties": { "name": "Blastoise" } },
    { "id": "N19", "label": "포켓몬", "properties": { "name": "Butterfree" } },
    { "id": "N20", "label": "포켓몬", "properties": { "name": "Raichu" } },
    { "id": "N21", "label": "포켓몬", "properties": { "name": "Ninetales" } },
    { "id": "N22", "label": "포켓몬", "properties": { "name": "Jigglypuff" } },
    { "id": "N23", "label": "포켓몬", "properties": { "name": "Parasect" } },
    { "id": "N24", "label": "포켓몬", "properties": { "name": "Diglett" } },
    { "id": "N25", "label": "포켓몬", "properties": { "name": "Dugtrio" } },
    { "id": "N26", "label": "포켓몬", "properties": { "name": "Psyduck" } },
    { "id": "N27", "label": "포켓몬", "properties": { "name": "Slowpoke" } },
    { "id": "N28", "label": "포켓몬", "properties": { "name": "Haunter" } },
    { "id": "N29", "label": "포켓몬", "properties": { "name": "Gengar" } },
    { "id": "N30", "label": "포켓몬", "properties": { "name": "Voltorb" } },
    { "id": "N31", "label": "포켓몬", "properties": { "name": "Cubone" } },
    { "id": "N32", "label": "포켓몬", "properties": { "name": "Weezing" } },
    { "id": "N33", "label": "포켓몬", "properties": { "name": "Starmie" } },
    { "id": "N34", "label": "포켓몬", "properties": { "name": "Mr. Mime" } },
    { "id": "N35", "label": "포켓몬", "properties": { "name": "Jynx" } },
    { "id": "N36", "label": "포켓몬", "properties": { "name": "Pinsir" } },
    { "id": "N37", "label": "포켓몬", "properties": { "name": "Magikarp" } },
    { "id": "N38", "label": "포켓몬", "properties": { "name": "Gyarados" } },
    { "id": "N39", "label": "포켓몬", "properties": { "name": "Ditto" } },
    { "id": "N40", "label": "포켓몬", "properties": { "name": "Eevee" } },
    { "id": "N41", "label": "포켓몬", "properties": { "name": "Snorlax" } },
    { "id": "N42", "label": "포켓몬", "properties": { "name": "Dragonite" } },
    { "id": "N43", "label": "포켓몬", "properties": { "name": "Mew" } }
]

#  영어 이름 → 한글 이름 변환 매핑 테이블
KOREAN_NODE_MAP = {
    "Ash Ketchum": "지우",
    "Pikachu": "피카츄",
    "Misty": "이슬",
    "Brock": "웅",
    "Jessie": "로사",
    "James": "로이",
    "Meowth": "나옹",
    "Professor Oak": "오박사",
    "Gary Oak": "바람",
    "Nurse Joy": "간호순",
    "Officer Jenny": "여경",
    "Bulbasaur": "이상해씨",
    "Charmander": "파이리",
    "Squirtle": "꼬부기",
    "Giovanni": "비주기",
    "Mewtwo": "뮤츠",
    "Charizard": "리자몽",
    "Blastoise": "거북왕",
    "Butterfree": "버터플",
    "Raichu": "라이츄",
    "Ninetales": "나인테일",
    "Jigglypuff": "푸린",
    "Parasect": "파라섹트",
    "Diglett": "디그다",
    "Dugtrio": "닥트리오",
    "Psyduck": "고라파덕",
    "Slowpoke": "야돈",
    "Haunter": "고우스트",
    "Gengar": "팬텀",
    "Voltorb": "찌리리공",
    "Cubone": "탕구리",
    "Weezing": "또도가스",
    "Starmie": "아쿠스타",
    "Mr. Mime": "마임맨",
    "Jynx": "루주라",
    "Pinsir": "쁘사이저",
    "Magikarp": "잉어킹",
    "Gyarados": "갸라도스",
    "Ditto": "메타몽",
    "Eevee": "이브이",
    "Snorlax": "잠만보",
    "Dragonite": "망나뇽",
    "Mew": "뮤"
}

# AI에게 관계 추출 방식을 알려주기 위한 예시 데이터
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
    },
    {
        "type": "BATTLES_TRAINER",
        "start_node_id": "N0",
        "end_node_id": "N8",
        "properties": {"outcome": "rivalry", "context": "Ash vs Gary's constant competition"}
    },
    {
        "type": "EVOLVES_TO",
        "start_node_id": "N12",
        "end_node_id": "N17",
        "properties": {"method": "level_up", "context": "Charmander evolves into Charizard"}
    },
    {
        "type": "CAPTURES",
        "start_node_id": "N0",
        "end_node_id": "N11",
        "properties": {"location": "Hidden Village", "pokemon": "Bulbasaur"}
    },
    {
        "type": "RELEASES",
        "start_node_id": "N0",
        "end_node_id": "N19",
        "properties": {"reason": "mating_season", "context": "Bye Bye Butterfree"}
    },
    {
        "type": "TEAMS_UP",
        "start_node_id": "N4",
        "end_node_id": "N5",
        "properties": {"group": "Team Rocket", "goal": "Stealing Pikachu"}
    }
]

# 프롬프트에서 사용할 관계 타입 정의 (리스트 형태)
RELATIONSHIP_TYPES = [
    "OWNS", "BATTLES", "BATTLES_TRAINER", 
    "EVOLVES_TO", "CAPTURES", "RELEASES", "TEAMS_UP"
]