"""
Визуализация карты в стиле Battle Brothers
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Circle, Rectangle, FancyBboxPatch
import numpy as np
from typing import Dict, List, Tuple, Optional
from entities.node import Node


class BattleBrothersStyleVisualizer:
    """Визуализация карты в стиле Battle Brothers"""
    
    def __init__(self):
        self.fig = None
        self.ax = None
        
        # Цвета ландшафта
        self.terrain_colors = {
            "grass": "#8B9A5B",  # Травянистые равнины
            "forest": "#2D5016",  # Леса
            "mountain": "#6B6B6B",  # Горы
            "center_dark": "#3A3A3A",  # Тёмный центр
            "water": "#4A90E2",  # Вода (для будущего)
        }
        
        # Стили узлов (иконки)
        self.node_icons = {
            "Center": {"shape": "X", "size": 200, "color": "#8B0000", "bg": "#2A2A2A"},
            "Capital": {"shape": "castle", "size": 180, "color": "#4169E1", "bg": "#F5F5DC"},
            "City": {"shape": "town", "size": 140, "color": "#228B22", "bg": "#FFFACD"},
            "BorderCastle": {"shape": "fort", "size": 120, "color": "#FF8C00", "bg": "#FFE4B5"},
            "Outpost": {"shape": "village", "size": 100, "color": "#808080", "bg": "#F0F0F0"},
        }
        
        # Цвета дорог
        self.road_colors = {
            "main": "#D2B48C",  # Основные дороги (коричневые)
            "secondary": "#C9A961",  # Второстепенные
            "path": "#8B7355",  # Тропы
        }
    
    def _draw_terrain_background(self, nodes: Dict[str, Node], bounds: Tuple[float, float, float, float]):
        """Рисует фон карты с ландшафтом"""
        x_min, x_max, y_min, y_max = bounds
        
        # Расширяем границы для фона
        margin = 50
        self.ax.set_xlim(x_min - margin, x_max + margin)
        self.ax.set_ylim(y_min - margin, y_max + margin)
        
        # Фон - трава
        self.ax.add_patch(Rectangle(
            (x_min - margin, y_min - margin),
            (x_max - x_min) + 2 * margin,
            (y_max - y_min) + 2 * margin,
            facecolor=self.terrain_colors["grass"],
            edgecolor='none',
            zorder=0
        ))
        
        # Леса (случайные области)
        np.random.seed(42)  # Для воспроизводимости
        for _ in range(15):
            x = np.random.uniform(x_min, x_max)
            y = np.random.uniform(y_min, y_max)
            size = np.random.uniform(30, 80)
            circle = Circle((x, y), size, 
                          facecolor=self.terrain_colors["forest"],
                          edgecolor='none',
                          alpha=0.4,
                          zorder=1)
            self.ax.add_patch(circle)
        
        # Центр - тёмная область
        center_node = nodes.get("Center")
        if center_node:
            center_circle = Circle(
                center_node.pos,
                150,
                facecolor=self.terrain_colors["center_dark"],
                edgecolor='#1A1A1A',
                linewidth=2,
                alpha=0.6,
                zorder=2
            )
            self.ax.add_patch(center_circle)
    
    def _draw_road(self, node_from: Node, node_to: Node, road_type: str = "main"):
        """Рисует дорогу между узлами"""
        x1, y1 = node_from.pos
        x2, y2 = node_to.pos
        
        # Толщина дороги зависит от типа
        linewidth = {"main": 3, "secondary": 2, "path": 1}.get(road_type, 2)
        color = self.road_colors.get(road_type, self.road_colors["main"])
        
        # Рисуем дорогу с небольшим размытием для эффекта
        self.ax.plot([x1, x2], [y1, y2],
                     color=color,
                     linewidth=linewidth + 1,
                     alpha=0.3,
                     zorder=3)
        self.ax.plot([x1, x2], [y1, y2],
                     color=color,
                     linewidth=linewidth,
                     alpha=0.7,
                     zorder=4)
    
    def _draw_node_icon(self, node: Node, style: Dict):
        """Рисует иконку узла"""
        x, y = node.pos
        size = style["size"]
        color = style["color"]
        bg_color = style.get("bg", "white")
        shape = style["shape"]
        
        # Фон иконки
        if shape == "castle":
            # Замок - квадрат с башнями
            rect = Rectangle((x - size/2, y - size/2), size, size,
                           facecolor=bg_color, edgecolor=color, linewidth=2, zorder=6)
            self.ax.add_patch(rect)
        elif shape == "town":
            # Город - круг
            circle = Circle((x, y), size/2,
                          facecolor=bg_color, edgecolor=color, linewidth=2, zorder=6)
            self.ax.add_patch(circle)
        elif shape == "fort":
            # Крепость - треугольник
            triangle = mpatches.RegularPolygon((x, y), 3, radius=size/2,
                                             facecolor=bg_color, edgecolor=color, linewidth=2, zorder=6)
            self.ax.add_patch(triangle)
        elif shape == "village":
            # Деревня - маленький круг
            circle = Circle((x, y), size/2,
                          facecolor=bg_color, edgecolor=color, linewidth=1.5, zorder=6)
            self.ax.add_patch(circle)
        elif shape == "X":
            # Центр - крест
            self.ax.scatter([x], [y], s=size*2, marker='X', 
                          c=color, edgecolors='black', linewidths=2, zorder=7)
        
        # Подпись
        if node.node_type in ["Center", "Capital", "City"]:
            self.ax.text(x, y - size/2 - 8, node.name,
                        fontsize=9, ha='center', va='top',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9, edgecolor='black'),
                        zorder=10)
    
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
        Рисует карту в стиле Battle Brothers
        """
        if self.fig is None:
            self.fig, self.ax = plt.subplots(figsize=(16, 16))
        else:
            self.ax.clear()
        
        # Вычисляем границы карты
        if not nodes:
            return
        
        x_coords = [node.pos[0] for node in nodes.values()]
        y_coords = [node.pos[1] for node in nodes.values()]
        bounds = (min(x_coords), max(x_coords), min(y_coords), max(y_coords))
        
        # Рисуем фон с ландшафтом
        self._draw_terrain_background(nodes, bounds)
        
        # Рисуем дороги (рёбра)
        for edge_from, edge_to in edges:
            if edge_from in nodes and edge_to in nodes:
                node_from = nodes[edge_from]
                node_to = nodes[edge_to]
                
                # Определяем тип дороги по типу узлов
                if "Capital" in [node_from.node_type, node_to.node_type]:
                    road_type = "main"
                elif "City" in [node_from.node_type, node_to.node_type]:
                    road_type = "secondary"
                else:
                    road_type = "path"
                
                self._draw_road(node_from, node_to, road_type)
        
        # Выделяем путь (если есть)
        if path and len(path) > 1:
            path_x = [nodes[n].pos[0] for n in path if n in nodes]
            path_y = [nodes[n].pos[1] for n in path if n in nodes]
            if path_x and path_y:
                self.ax.plot(path_x, path_y, 'r-', linewidth=5, alpha=0.8, zorder=5, label='Путь')
        
        # Рисуем узлы по типам
        for node_type in ["Outpost", "BorderCastle", "City", "Capital", "Center"]:
            style = self.node_icons.get(node_type, {})
            if not style:
                continue
            
            for node_id, node in nodes.items():
                if node.node_type == node_type:
                    self._draw_node_icon(node, style)
        
        # Выделяем стартовый узел
        if start_node and start_node in nodes:
            node = nodes[start_node]
            circle = Circle(node.pos, 25, facecolor='none', 
                          edgecolor='blue', linewidth=3, zorder=8)
            self.ax.add_patch(circle)
        
        # Выделяем целевой узел
        if goal_node and goal_node in nodes:
            node = nodes[goal_node]
            circle = Circle(node.pos, 25, facecolor='none', 
                          edgecolor='red', linewidth=3, zorder=8)
            self.ax.add_patch(circle)
        
        # Выделяем дополнительные узлы
        if highlight_nodes:
            for node_id in highlight_nodes:
                if node_id in nodes:
                    node = nodes[node_id]
                    star = mpatches.RegularPolygon(node.pos, 5, radius=20,
                                                 facecolor='yellow', edgecolor='black', 
                                                 linewidth=2, alpha=0.8, zorder=9)
                    self.ax.add_patch(star)
        
        # Заголовок и настройки
        self.ax.set_title("Карта мира - Battle Brothers Style", 
                         fontsize=16, fontweight='bold', pad=20)
        self.ax.set_aspect('equal')
        self.ax.axis('off')  # Убираем оси для более чистого вида
        
        # Легенда
        legend_elements = [
            mpatches.Patch(facecolor=self.node_icons["Capital"]["bg"], 
                          edgecolor=self.node_icons["Capital"]["color"],
                          label='Столица'),
            mpatches.Patch(facecolor=self.node_icons["City"]["bg"], 
                          edgecolor=self.node_icons["City"]["color"],
                          label='Город'),
            mpatches.Patch(facecolor=self.node_icons["BorderCastle"]["bg"], 
                          edgecolor=self.node_icons["BorderCastle"]["color"],
                          label='Замок'),
            mpatches.Patch(facecolor=self.node_icons["Outpost"]["bg"], 
                          edgecolor=self.node_icons["Outpost"]["color"],
                          label='Аванпост'),
        ]
        if path:
            legend_elements.append(plt.Line2D([0], [0], color='red', linewidth=3, label='Путь'))
        
        self.ax.legend(handles=legend_elements, loc='upper left', fontsize=10)
        
        plt.tight_layout()
        return self.fig
    
    def show(self):
        """Показывает карту"""
        if self.fig:
            plt.show()
    
    def save(self, filename: str = "map_bb_style.png"):
        """Сохраняет карту в файл"""
        if self.fig:
            self.fig.savefig(filename, dpi=200, bbox_inches='tight', facecolor='white')
            print(f"Map saved to {filename}")
    
    def close(self):
        """Закрывает фигуру"""
        if self.fig:
            plt.close(self.fig)
            self.fig = None
            self.ax = None
