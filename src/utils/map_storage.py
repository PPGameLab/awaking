"""
Хранение и загрузка карты
"""
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from entities.node import Node


class MapStorage:
    """Хранение и загрузка карты в/из JSON"""
    
    def __init__(self, save_path: str = "data/generated_map.json"):
        self.save_path = Path(save_path)
    
    def save_map(
        self,
        nodes: Dict[str, Node],
        edges: List[Tuple[str, str]],
        metadata: Optional[Dict] = None
    ):
        """
        Сохраняет карту в JSON файл
        
        Args:
            nodes: Словарь узлов {node_id: Node}
            edges: Список рёбер [(node_id_from, node_id_to), ...]
            metadata: Дополнительные метаданные (версия, дата генерации и т.д.)
        """
        data = {
            "metadata": metadata or {
                "version": "MVP",
                "description": "Сгенерированная карта"
            },
            "nodes": [],
            "edges": edges
        }
        
        # Сериализуем узлы
        for node in nodes.values():
            node_data = {
                "id": node.id,
                "name": node.name,
                "pos": list(node.pos),
                "node_type": node.node_type,
                "kingdom": node.kingdom,
                "role": node.role
            }
            data["nodes"].append(node_data)
        
        # Сохраняем в файл
        self.save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.save_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_map(self) -> Tuple[Dict[str, Node], List[Tuple[str, str]], Optional[Dict]]:
        """
        Загружает карту из JSON файла
        
        Returns:
            Tuple[Dict[str, Node], List[Tuple[str, str]], Optional[Dict]]: (узлы, рёбра, метаданные)
        """
        if not self.save_path.exists():
            raise FileNotFoundError(f"Файл карты {self.save_path} не найден")
        
        with open(self.save_path, 'r', encoding='utf-8') as f:
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
    
    def map_exists(self) -> bool:
        """Проверяет, существует ли сохранённая карта"""
        return self.save_path.exists()
