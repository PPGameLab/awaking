"""
Загрузка данных из JSON файлов
"""
import json
import os
from pathlib import Path


def load_json(filename: str) -> dict:
    """Загружает JSON файл из папки data/"""
    base_path = Path(__file__).parent.parent.parent
    data_path = base_path / "data" / filename
    
    if not data_path.exists():
        raise FileNotFoundError(f"Файл {filename} не найден в папке data/")
    
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_map_structure() -> dict:
    """Загружает структуру карты"""
    return load_json("map_structure.json")


def load_game_mechanics() -> dict:
    """Загружает механику игры"""
    return load_json("game_mechanics.json")


def load_attributes() -> dict:
    """Загружает характеристики и параметры"""
    return load_json("attributes.json")


def load_kingdoms() -> dict:
    """Загружает данные о королевствах"""
    return load_json("kingdoms.json")
