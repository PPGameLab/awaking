"""
Мир и карта
"""
from typing import Dict, List, Optional, Tuple
from ..entities.node import Node
from ..utils.loader import load_map_structure
import math


class World:
    """Мир игры - карта с узлами и рёбрами"""
    
    def __init__(self, load_saved: bool = False):
        """
        Инициализация мира
        
        Args:
            load_saved: Если True, пытается загрузить сохранённую карту, иначе создаёт пустую
        """
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Tuple[str, str]] = []  # (node_id_from, node_id_to)
        self.kingdoms: Dict[str, List[str]] = {}  # kingdom_id -> [node_ids]
        
        if load_saved:
            self._try_load_saved_map()
    
    def _try_load_saved_map(self):
        """Пытается загрузить сохранённую карту"""
        from utils.map_storage import MapStorage
        
        storage = MapStorage()
        if storage.map_exists():
            try:
                nodes, edges, metadata = storage.load_map()
                
                # Добавляем узлы
                for node in nodes.values():
                    self.add_node(node)
                
                # Добавляем рёбра
                for edge in edges:
                    if len(edge) >= 2:
                        self.add_edge(edge[0], edge[1])
                
                print(f"Карта загружена из {storage.save_path}")
                if metadata:
                    print(f"Версия: {metadata.get('version', 'unknown')}")
            except Exception as e:
                print(f"Ошибка загрузки карты: {e}. Создана пустая карта.")
    
    def load_map_from_file(self, map_name: str = "simple_map"):
        """
        Загружает карту из файла данных
        
        Args:
            map_name: Имя карты (без расширения .json)
        """
        from ..utils.map_loader import MapLoader
        
        # Очищаем текущую карту
        self.nodes.clear()
        self.edges.clear()
        self.kingdoms.clear()
        
        # Загружаем карту
        loader = MapLoader()
        nodes, edges, metadata = loader.load_map(map_name)
        
        # Добавляем узлы
        for node in nodes.values():
            self.add_node(node)
        
        # Добавляем рёбра
        for edge in edges:
            if len(edge) >= 2:
                self.add_edge(edge[0], edge[1])
        
        print(f"Map loaded: {map_name}")
        if metadata:
            print(f"  Name: {metadata.get('name', 'N/A')}")
            # Description may contain non-ASCII, skip for now
    
    def create_simple_map(self):
        """Создаёт простую карту (3 узла треугольником) - использует load_map_from_file"""
        self.load_map_from_file("simple_map")
    
    def generate_from_config(
        self,
        capitals: Dict[str, Dict],
        center_pos: Tuple[float, float] = (500.0, 500.0),
        ring_order: Optional[List[str]] = None,
        save_map: bool = True
    ):
        """
        Генерирует карту на основе конфигурации
        
        Args:
            capitals: Словарь столиц {kingdom_id: {"name": str, "pos": (x, y)}}
            center_pos: Позиция центра
            ring_order: Порядок королевств по кругу (если None, используется порядок из capitals)
            save_map: Сохранять ли карту после генерации
        """
        from ..utils.map_generator import MapGenerator
        from ..utils.map_storage import MapStorage
        
        # Очищаем текущую карту
        self.nodes.clear()
        self.edges.clear()
        self.kingdoms.clear()
        
        # Генерируем карту
        generator = MapGenerator()
        
        if ring_order is None:
            ring_order = list(capitals.keys())
        
        nodes, edges = generator.generate_map(capitals, center_pos, ring_order)
        
        # Добавляем узлы
        for node in nodes.values():
            self.add_node(node)
        
        # Добавляем рёбра
        for edge in edges:
            if len(edge) >= 2:
                self.add_edge(edge[0], edge[1])
        
        # Сохраняем карту
        if save_map:
            storage = MapStorage()
            metadata = {
                "version": "MVP",
                "description": "Сгенерированная карта из конфигурации",
                "nodes_count": len(nodes),
                "edges_count": len(edges),
                "kingdoms_count": len(self.kingdoms)
            }
            storage.save_map(nodes, edges, metadata)
            print(f"Карта сохранена в {storage.save_path}")
        
        return len(nodes), len(edges)
    
    def add_node(self, node: Node):
        """Добавляет узел на карту"""
        self.nodes[node.id] = node
        
        # Добавляем в список узлов королевства
        if node.kingdom:
            if node.kingdom not in self.kingdoms:
                self.kingdoms[node.kingdom] = []
            self.kingdoms[node.kingdom].append(node.id)
    
    def add_edge(self, node_id_from: str, node_id_to: str):
        """Добавляет ребро между узлами (ненаправленный граф, хранится один раз)"""
        if node_id_from not in self.nodes or node_id_to not in self.nodes:
            raise ValueError(f"Узлы {node_id_from} или {node_id_to} не существуют")
        
        # Храним в каноническом виде (от меньшего к большему) для избежания дубликатов
        canonical = (min(node_id_from, node_id_to), max(node_id_from, node_id_to))
        if canonical not in self.edges:
            self.edges.append(canonical)
    
    def get_neighbors(self, node_id: str) -> List[str]:
        """Возвращает список соседних узлов"""
        neighbors = []
        for edge_from, edge_to in self.edges:
            if edge_from == node_id:
                neighbors.append(edge_to)
            elif edge_to == node_id:
                neighbors.append(edge_from)
        return neighbors
    
    def find_path(self, start_id: str, goal_id: str) -> Optional[List[str]]:
        """Поиск пути между узлами (A* алгоритм)"""
        if start_id not in self.nodes or goal_id not in self.nodes:
            return None
        
        def heuristic(node_id: str) -> float:
            """Эвристика для A*"""
            node = self.nodes[node_id]
            goal = self.nodes[goal_id]
            return node.distance_to(goal)
        
        import heapq
        
        open_heap = []
        heapq.heappush(open_heap, (heuristic(start_id), start_id))
        
        came_from = {}
        gscore = {start_id: 0.0}
        in_open = {start_id}
        
        while open_heap:
            _, current = heapq.heappop(open_heap)
            in_open.discard(current)
            
            if current == goal_id:
                # Восстанавливаем путь
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return path
            
            for neighbor in self.get_neighbors(current):
                neighbor_node = self.nodes[neighbor]
                current_node = self.nodes[current]
                edge_weight = current_node.distance_to(neighbor_node)
                
                tentative = gscore[current] + edge_weight
                if tentative < gscore.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    gscore[neighbor] = tentative
                    if neighbor not in in_open:
                        heapq.heappush(open_heap, (tentative + heuristic(neighbor), neighbor))
                        in_open.add(neighbor)
        
        return None  # Путь не найден
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """Возвращает узел по ID"""
        return self.nodes.get(node_id)
    
    def visualize(self, path: Optional[List[str]] = None, save: bool = False, style: str = "bb"):
        """
        Визуализирует карту
        
        Args:
            path: Путь для выделения (опционально)
            save: Сохранять ли карту в файл
            style: Стиль визуализации ("bb" для Battle Brothers, "simple" для простой)
        
        Returns:
            MapVisualizer объект
        """
        if style == "bb":
            from ..utils.map_visualizer_bb import BattleBrothersStyleVisualizer
            visualizer = BattleBrothersStyleVisualizer()
        else:
            from ..utils.map_visualizer import MapVisualizer
            visualizer = MapVisualizer()
        
        visualizer.draw_map(self.nodes, self.edges, path=path)
        
        if save:
            visualizer.save()
        
        return visualizer
