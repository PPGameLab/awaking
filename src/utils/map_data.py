"""
Данные для генерации карты (из test.py)
"""
from typing import Dict

# Позиция центра
CENTER_POS = (500.0, 500.0)

# Столицы королевств
CAPITALS = {
    "Necro": {"name": "Necropolis", "pos": (500.0, 1000.0)},
    "Steel": {"name": "Steelforge", "pos": (853.0, 853.0)},
    "Body": {"name": "Temple of Body", "pos": (1000.0, 500.0)},
    "Fire": {"name": "Fire Earth", "pos": (853.0, 146.0)},
    "Demons": {"name": "Demons", "pos": (500.0, 0.0)},
    "Nature": {"name": "Nature", "pos": (146.0, 146.0)},
    "Spirit": {"name": "Spirit", "pos": (0.0, 500.0)},
    "Water": {"name": "Water Wind", "pos": (146.0, 853.0)},
}

# Порядок королевств по кругу (по часовой стрелке)
RING_ORDER = ["Necro", "Steel", "Body", "Fire", "Demons", "Nature", "Spirit", "Water"]

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
