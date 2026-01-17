"""
Данные для генерации карты (загружаются из файлов)
"""
from pathlib import Path
from typing import Dict, Tuple

# Загружаем координаты из файла
def _load_coordinates():
    """Загружает координаты из data/maps/map_coordinates.json"""
    coords_path = Path("data/maps/map_coordinates.json")
    
    if not coords_path.exists():
        # Значения по умолчанию (для обратной совместимости)
        return {
            "center": {"pos": [500.0, 500.0]},
            "capitals": {
                "Necro": {"name": "Necropolis", "pos": [500.0, 1000.0]},
                "Steel": {"name": "Steelforge", "pos": [853.0, 853.0]},
                "Body": {"name": "Temple of Body", "pos": [1000.0, 500.0]},
                "Fire": {"name": "Fire Earth", "pos": [853.0, 146.0]},
                "Demons": {"name": "Demons", "pos": [500.0, 0.0]},
                "Nature": {"name": "Nature", "pos": [146.0, 146.0]},
                "Spirit": {"name": "Spirit", "pos": [0.0, 500.0]},
                "Water": {"name": "Water Wind", "pos": [146.0, 853.0]},
            },
            "ring_order": ["Necro", "Steel", "Body", "Fire", "Demons", "Nature", "Spirit", "Water"]
        }
    
    import json
    with open(coords_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Загружаем координаты
_coords = _load_coordinates()

# Позиция центра
CENTER_POS: Tuple[float, float] = tuple(_coords["center"]["pos"])

# Столицы королевств
CAPITALS: Dict[str, Dict] = {}
for kingdom_id, capital_data in _coords["capitals"].items():
    CAPITALS[kingdom_id] = {
        "name": capital_data["name"],
        "pos": tuple(capital_data["pos"])
    }

# Порядок королевств по кругу (по часовой стрелке)
RING_ORDER: list = _coords["ring_order"]

# Маппинг на русские названия (для совместимости с данными)
KINGDOM_NAMES = {
    "Necro": "Королевство Креста",
    "Steel": "Королевство Инженеров",
    "Body": "Королевство Магии Тела",
    "Fire": "Вулканическое Королевство",
    "Demons": "Потустороннее Королевство",
    "Nature": "Край Природных Защитников",
    "Spirit": "Королевство Стойкости и Духа",
    "Water": "Северо-Западный край",
}
