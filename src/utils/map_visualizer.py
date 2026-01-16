"""
Визуализация карты
"""
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional
from entities.node import Node


class MapVisualizer:
    """Визуализация карты через matplotlib"""
    
    def __init__(self):
        self.fig = None
        self.ax = None
        self.node_styles = {
            "Center": {"marker": "X", "size": 220, "color": "red"},
            "Capital": {"marker": "s", "size": 140, "color": "blue"},
            "City": {"marker": "o", "size": 110, "color": "green"},
            "BorderCastle": {"marker": "^", "size": 90, "color": "orange"},
            "Outpost": {"marker": ".", "size": 70, "color": "gray"},
        }
    
    def draw_map(
        self,
        nodes: Dict[str, Node],
        edges: List[Tuple[str, str]],
        path: Optional[List[str]] = None,
        start_node: Optional[str] = None,
        goal_node: Optional[str] = None,
        highlight_nodes: Optional[List[str]] = None
    ):
        """
        Рисует карту
        
        Args:
            nodes: Словарь узлов
            edges: Список рёбер
            path: Путь для выделения (опционально)
            start_node: Начальный узел для выделения
            goal_node: Целевой узел для выделения
            highlight_nodes: Список узлов для выделения
        """
        if self.fig is None:
            self.fig, self.ax = plt.subplots(figsize=(12, 12))
        else:
            self.ax.clear()
        
        # Рисуем рёбра
        for edge_from, edge_to in edges:
            if edge_from in nodes and edge_to in nodes:
                node_from = nodes[edge_from]
                node_to = nodes[edge_to]
                self.ax.plot(
                    [node_from.pos[0], node_to.pos[0]],
                    [node_from.pos[1], node_to.pos[1]],
                    'k-',
                    linewidth=0.5,
                    alpha=0.3
                )
        
        # Выделяем путь
        if path and len(path) > 1:
            path_x = [nodes[n].pos[0] for n in path if n in nodes]
            path_y = [nodes[n].pos[1] for n in path if n in nodes]
            if path_x and path_y:
                self.ax.plot(path_x, path_y, 'r-', linewidth=3, alpha=0.7, label='Path')
        
        # Рисуем узлы по типам
        for node_type, style in self.node_styles.items():
            x_coords = []
            y_coords = []
            node_ids = []
            
            for node_id, node in nodes.items():
                if node.node_type == node_type:
                    x_coords.append(node.pos[0])
                    y_coords.append(node.pos[1])
                    node_ids.append(node_id)
            
            if x_coords:
                self.ax.scatter(
                    x_coords, y_coords,
                    s=style["size"],
                    marker=style["marker"],
                    c=style["color"],
                    alpha=0.7,
                    edgecolors='black',
                    linewidths=0.5
                )
        
        # Выделяем начальный и целевой узлы
        if start_node and start_node in nodes:
            node = nodes[start_node]
            self.ax.scatter(
                [node.pos[0]], [node.pos[1]],
                s=300, marker='o', facecolors='none',
                edgecolors='blue', linewidths=3, label='Start'
            )
        
        if goal_node and goal_node in nodes:
            node = nodes[goal_node]
            self.ax.scatter(
                [node.pos[0]], [node.pos[1]],
                s=300, marker='s', facecolors='none',
                edgecolors='red', linewidths=3, label='Goal'
            )
        
        # Выделяем дополнительные узлы
        if highlight_nodes:
            for node_id in highlight_nodes:
                if node_id in nodes:
                    node = nodes[node_id]
                    self.ax.scatter(
                        [node.pos[0]], [node.pos[1]],
                        s=250, marker='*', facecolors='yellow',
                        edgecolors='black', linewidths=1, alpha=0.8
                    )
        
        # Подписи узлов (только для важных)
        for node_id, node in nodes.items():
            if node.node_type in ["Center", "Capital"]:
                self.ax.text(
                    node.pos[0] + 5, node.pos[1] + 5,
                    node.name,
                    fontsize=8,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7)
                )
        
        self.ax.set_title("Map Visualization", fontsize=14, fontweight='bold')
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.grid(True, alpha=0.3)
        self.ax.axis('equal')
        
        if path or start_node or goal_node:
            self.ax.legend(loc='upper right')
        
        plt.tight_layout()
        return self.fig
    
    def show(self):
        """Показывает карту"""
        if self.fig:
            plt.show()
    
    def save(self, filename: str = "map_visualization.png"):
        """Сохраняет карту в файл"""
        if self.fig:
            self.fig.savefig(filename, dpi=150, bbox_inches='tight')
            print(f"Map saved to {filename}")
    
    def close(self):
        """Закрывает фигуру"""
        if self.fig:
            plt.close(self.fig)
            self.fig = None
            self.ax = None


def visualize_map_from_world(world, path: Optional[List[str]] = None):
    """
    Визуализирует карту из World объекта
    
    Args:
        world: Объект World
        path: Путь для выделения (опционально)
    """
    visualizer = MapVisualizer()
    visualizer.draw_map(world.nodes, world.edges, path=path)
    return visualizer
