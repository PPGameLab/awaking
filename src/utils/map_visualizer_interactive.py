"""
Интерактивная визуализация карты (с кликами для выбора пути)
"""
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional
from entities.node import Node
from core.world import World


class InteractiveMapVisualizer:
    """Интерактивная визуализация карты с возможностью выбора пути кликами"""
    
    def __init__(self, world: World):
        self.world = world
        self.fig = None
        self.ax = None
        self.start_node = None
        self.goal_node = None
        self.current_path = None
        
        self.node_styles = {
            "Center": {"marker": "X", "size": 220, "color": "red"},
            "Capital": {"marker": "s", "size": 140, "color": "blue"},
            "City": {"marker": "o", "size": 110, "color": "green"},
            "BorderCastle": {"marker": "^", "size": 90, "color": "orange"},
            "Outpost": {"marker": ".", "size": 70, "color": "gray"},
        }
    
    def _nearest_node(self, x: float, y: float, threshold: float = 10.0) -> Optional[str]:
        """Находит ближайший узел к координатам клика"""
        best = None
        best_d = float('inf')
        
        for node_id, node in self.world.nodes.items():
            dx = node.pos[0] - x
            dy = node.pos[1] - y
            d = (dx * dx + dy * dy) ** 0.5
            
            if d < best_d:
                best_d = d
                best = node_id
        
        return best if best_d <= threshold else None
    
    def _draw_map(self):
        """Рисует карту"""
        if self.ax is None:
            return
        
        self.ax.clear()
        
        # Рисуем рёбра
        for edge_from, edge_to in self.world.edges:
            if edge_from in self.world.nodes and edge_to in self.world.nodes:
                node_from = self.world.nodes[edge_from]
                node_to = self.world.nodes[edge_to]
                self.ax.plot(
                    [node_from.pos[0], node_to.pos[0]],
                    [node_from.pos[1], node_to.pos[1]],
                    'k-',
                    linewidth=0.5,
                    alpha=0.3
                )
        
        # Выделяем путь
        if self.current_path and len(self.current_path) > 1:
            path_x = [self.world.nodes[n].pos[0] for n in self.current_path if n in self.world.nodes]
            path_y = [self.world.nodes[n].pos[1] for n in self.current_path if n in self.world.nodes]
            if path_x and path_y:
                self.ax.plot(path_x, path_y, 'r-', linewidth=4, alpha=0.7, label='Path')
        
        # Рисуем узлы по типам
        for node_type, style in self.node_styles.items():
            x_coords = []
            y_coords = []
            
            for node in self.world.nodes.values():
                if node.node_type == node_type:
                    x_coords.append(node.pos[0])
                    y_coords.append(node.pos[1])
            
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
        
        # Выделяем начальный узел
        if self.start_node and self.start_node in self.world.nodes:
            node = self.world.nodes[self.start_node]
            self.ax.scatter(
                [node.pos[0]], [node.pos[1]],
                s=300, marker='o', facecolors='none',
                edgecolors='blue', linewidths=3, label='Start'
            )
        
        # Выделяем целевой узел
        if self.goal_node and self.goal_node in self.world.nodes:
            node = self.world.nodes[self.goal_node]
            self.ax.scatter(
                [node.pos[0]], [node.pos[1]],
                s=300, marker='s', facecolors='none',
                edgecolors='red', linewidths=3, label='Goal'
            )
        
        # Подписи для важных узлов
        for node_id, node in self.world.nodes.items():
            if node.node_type in ["Center", "Capital"]:
                self.ax.text(
                    node.pos[0] + 5, node.pos[1] + 5,
                    node.name,
                    fontsize=8,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7)
                )
        
        # Инструкция
        instruction = "Click nodes: 1st=start, 2nd=goal, 3rd=reset"
        if self.start_node:
            instruction = f"Start: {self.start_node}. Click goal node."
        if self.goal_node:
            instruction = f"Path found! Click anywhere to reset."
        
        self.ax.set_title(f"Interactive Map - {instruction}", fontsize=12, fontweight='bold')
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.grid(True, alpha=0.3)
        self.ax.axis('equal')
        
        if self.start_node or self.goal_node:
            self.ax.legend(loc='upper right')
        
        self.fig.canvas.draw()
    
    def _on_click(self, event):
        """Обработчик клика мыши"""
        if event.xdata is None or event.ydata is None:
            return
        
        node_id = self._nearest_node(event.xdata, event.ydata)
        if node_id is None:
            return
        
        if self.start_node is None:
            # Первый клик - выбираем старт
            self.start_node = node_id
            self.goal_node = None
            self.current_path = None
        elif self.goal_node is None:
            # Второй клик - выбираем цель и ищем путь
            self.goal_node = node_id
            if self.start_node != self.goal_node:
                self.current_path = self.world.find_path(self.start_node, self.goal_node)
                if self.current_path:
                    print(f"Path found: {len(self.current_path)} nodes")
                    print(f"  {' -> '.join(self.current_path[:10])}{'...' if len(self.current_path) > 10 else ''}")
                else:
                    print("No path found")
        else:
            # Третий клик - сброс
            self.start_node = None
            self.goal_node = None
            self.current_path = None
        
        self._draw_map()
    
    def show(self):
        """Показывает интерактивную карту"""
        self.fig, self.ax = plt.subplots(figsize=(12, 12))
        self._draw_map()
        self.fig.canvas.mpl_connect("button_press_event", self._on_click)
        plt.show()
    
    def close(self):
        """Закрывает визуализацию"""
        if self.fig:
            plt.close(self.fig)
            self.fig = None
            self.ax = None
