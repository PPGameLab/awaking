"""
Узлы карты (Node)
"""
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class Node:
    """Узел на карте"""
    id: str
    name: str
    pos: tuple[float, float]  # (x, y)
    node_type: str  # Capital, City, BorderCastle, Outpost, Center
    kingdom: Optional[str] = None  # ID королевства, None для Center
    role: Optional[str] = None  # Farm, Mine, Lumber, TradePost, Ruin, GateToCenter, etc.
    
    def __post_init__(self):
        """Проверка данных после инициализации"""
        if self.node_type == "Center" and self.kingdom is not None:
            raise ValueError("Center не может принадлежать королевству")
    
    def is_connected_to(self, other: 'Node') -> bool:
        """Проверяет, соединён ли узел с другим (нужна информация о рёбрах)"""
        # Это будет реализовано в World классе
        pass
    
    def distance_to(self, other: 'Node') -> float:
        """Вычисляет расстояние до другого узла"""
        import math
        dx = self.pos[0] - other.pos[0]
        dy = self.pos[1] - other.pos[1]
        return math.hypot(dx, dy)
