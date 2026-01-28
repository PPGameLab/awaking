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
    base_path = Path(__file__).parent.parent.parent
    data_path = base_path / "game_data" / "map_structure.mvp.json"
    
    if not data_path.exists():
        raise FileNotFoundError(f"Файл map_structure.mvp.json не найден в game_data/")
    
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_game_mechanics() -> dict:
    """Загружает механику игры"""
    base_path = Path(__file__).parent.parent.parent
    data_path = base_path / "game_data" / "game_mechanics.mvp.json"
    
    if not data_path.exists():
        raise FileNotFoundError(f"Файл game_mechanics.mvp.json не найден в game_data/")
    
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_attributes() -> dict:
    """Загружает характеристики и параметры"""
    base_path = Path(__file__).parent.parent.parent
    data_path = base_path / "game_data" / "attributes.mvp.json"
    
    if not data_path.exists():
        raise FileNotFoundError(f"Файл attributes.mvp.json не найден в game_data/")
    
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_kingdoms() -> dict:
    """Загружает данные о королевствах"""
    return load_json("kingdoms.json")
