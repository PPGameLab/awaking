"""
Рендеринг карты в pygame
"""
import pygame
from typing import Tuple, List, Optional
from ..core.world import World
from ..entities.unit import Squad


class MapRenderer:
    """Рендерер карты для pygame"""
    
    def __init__(self, screen: pygame.Surface, world: World):
        self.screen = screen
        self.world = world
        self.camera_x = 0.0
        self.camera_y = 0.0
        self.zoom = 1.0
        
        # Цвета для узлов
        self.node_colors = {
            "Capital": (0, 0, 255),      # Синий
            "City": (0, 255, 0),         # Зелёный
            "BorderCastle": (255, 165, 0), # Оранжевый
            "Outpost": (128, 128, 128),  # Серый
            "Center": (255, 0, 0)        # Красный
        }
        
        # Цвета для рёбер
        self.edge_color = (100, 100, 100)  # Серый
    
    def world_to_screen(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """Преобразует мировые координаты в экранные"""
        screen_x = int((world_x - self.camera_x) * self.zoom + self.screen.get_width() / 2)
        screen_y = int((world_y - self.camera_y) * self.zoom + self.screen.get_height() / 2)
        return (screen_x, screen_y)
    
    def screen_to_world(self, screen_x: int, screen_y: int) -> Tuple[float, float]:
        """Преобразует экранные координаты в мировые"""
        world_x = (screen_x - self.screen.get_width() / 2) / self.zoom + self.camera_x
        world_y = (screen_y - self.screen.get_height() / 2) / self.zoom + self.camera_y
        return (world_x, world_y)
    
    def center_on_node(self, node_id: str):
        """Центрирует камеру на узле"""
        node = self.world.get_node(node_id)
        if node:
            self.camera_x = node.pos[0]
            self.camera_y = node.pos[1]
    
    def render_edges(self):
        """Рендерит рёбра карты"""
        for edge in self.world.edges:
            # Поддержка старого формата (from, to) и нового (from, to, type)
            if len(edge) >= 2:
                edge_from, edge_to = edge[0], edge[1]
            else:
                continue
            
            node_from = self.world.get_node(edge_from)
            node_to = self.world.get_node(edge_to)
            
            if node_from and node_to:
                start = self.world_to_screen(node_from.pos[0], node_from.pos[1])
                end = self.world_to_screen(node_to.pos[0], node_to.pos[1])
                pygame.draw.line(self.screen, self.edge_color, start, end, 2)
    
    def render_nodes(self):
        """Рендерит узлы карты"""
        for node in self.world.nodes.values():
            screen_pos = self.world_to_screen(node.pos[0], node.pos[1])
            
            color = self.node_colors.get(node.node_type, (128, 128, 128))
            size = 10 if node.node_type == "Capital" else 8
            
            pygame.draw.circle(self.screen, color, screen_pos, size)
            pygame.draw.circle(self.screen, (0, 0, 0), screen_pos, size, 2)  # Обводка
    
    def render_squad(self, squad: Squad):
        """Рендерит отряд"""
        if not squad.current_node_id:
            return
        
        node = self.world.get_node(squad.current_node_id)
        if not node:
            return
        
        screen_pos = self.world_to_screen(node.pos[0], node.pos[1])
        
        # Отряд - красный круг
        pygame.draw.circle(self.screen, (255, 0, 0), screen_pos, 12)
        pygame.draw.circle(self.screen, (0, 0, 0), screen_pos, 12, 2)
    
    def render_path(self, squad: Squad):
        """Рендерит путь отряда"""
        if not squad.path or len(squad.path) < 2:
            return
        
        # Начинаем с текущего узла
        if squad.current_node_id:
            current_node = self.world.get_node(squad.current_node_id)
            if current_node:
                path_points = [current_node.pos]
            else:
                path_points = []
        else:
            path_points = []
        
        # Добавляем узлы пути
        for node_id in squad.path:
            node = self.world.get_node(node_id)
            if node:
                path_points.append(node.pos)
        
        # Рисуем линии пути
        if len(path_points) >= 2:
            for i in range(len(path_points) - 1):
                start = self.world_to_screen(path_points[i][0], path_points[i][1])
                end = self.world_to_screen(path_points[i+1][0], path_points[i+1][1])
                pygame.draw.line(self.screen, (255, 0, 0), start, end, 3)
    
    def render(self, squads: List[Squad]):
        """Рендерит всю карту"""
        # Фон
        self.screen.fill((240, 240, 240))
        
        # Рендеринг
        self.render_edges()
        self.render_nodes()
        
        # Путь и отряд поверх
        for squad in squads:
            self.render_path(squad)
            self.render_squad(squad)
    
    def get_node_at_screen_pos(self, screen_x: int, screen_y: int, threshold: float = 15.0) -> Optional[str]:
        """Возвращает ID узла в указанной экранной позиции"""
        world_pos = self.screen_to_world(screen_x, screen_y)
        
        best_node = None
        best_distance = float('inf')
        
        for node in self.world.nodes.values():
            distance = ((node.pos[0] - world_pos[0]) ** 2 + (node.pos[1] - world_pos[1]) ** 2) ** 0.5
            distance_screen = distance * self.zoom
            
            if distance_screen < threshold and distance_screen < best_distance:
                best_distance = distance_screen
                best_node = node.id
        
        return best_node
