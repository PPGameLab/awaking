"""
Загрузка карты из файлов данных
"""
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from ..entities.node import Node


class MapLoader:
    """Загрузчик карт из файлов данных"""
    
    def __init__(self, maps_dir: str = "data/maps"):
        self.maps_dir = Path(maps_dir)
    
    def load_map(self, map_name: str) -> Tuple[Dict[str, Node], List[Tuple[str, str]], Optional[Dict]]:
        """
        Загружает карту из файла
        
        Args:
            map_name: Имя карты (без расширения .json)
        
        Returns:
            Tuple[Dict[str, Node], List[Tuple[str, str]], Optional[Dict]]: (узлы, рёбра, метаданные)
        """
        map_path = self.maps_dir / f"{map_name}.json"
        
        if not map_path.exists():
            raise FileNotFoundError(f"Карта {map_name} не найдена: {map_path}")
        
        with open(map_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Десериализуем узлы
        nodes = {}
        for node_data in data["nodes"]:
            node = Node(
                id=node_data["id"],
                name=node_data["name"],
                pos=tuple(node_data["pos"]),
                node_type=node_data["node_type"],
                kingdom=node_data.get("kingdom"),
                role=node_data.get("role")
            )
            nodes[node.id] = node
        
        # Рёбра
        edges = [tuple(edge) for edge in data["edges"]]
        
        # Метаданные
        metadata = data.get("metadata")
        
        return nodes, edges, metadata
    
    def load_coordinates(self) -> Dict:
        """
        Загружает координаты для генерации карты
        
        Returns:
            Dict с координатами center, capitals, ring_order
        """
        coords_path = self.maps_dir / "map_coordinates.json"
        
        if not coords_path.exists():
            raise FileNotFoundError(f"Файл координат не найден: {coords_path}")
        
        with open(coords_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_maps(self) -> List[str]:
        """Возвращает список доступных карт"""
        maps = []
        for file in self.maps_dir.glob("*.json"):
            if file.name != "map_coordinates.json":
                maps.append(file.stem)
        return maps
