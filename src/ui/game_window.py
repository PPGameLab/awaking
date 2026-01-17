"""
Главное окно игры (pygame)
"""
import pygame
from typing import Optional, List
from ..core.game import Game
from ..entities.unit import Squad
from .map_renderer import MapRenderer


class GameWindow:
    """Главное окно игры"""
    
    def __init__(self, width: int = 1200, height: int = 800):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Awaking")
        self.clock = pygame.time.Clock()
        self.running = True
        self.width = width
        self.height = height
        
        self.game: Optional[Game] = None
        self.renderer: Optional[MapRenderer] = None
        
        # Фонт для текста
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Выбранный узел
        self.selected_node_id: Optional[str] = None
    
    def set_game(self, game: Game):
        """Устанавливает игру"""
        self.game = game
        if game.world:
            self.renderer = MapRenderer(self.screen, game.world)
            # Центрируем камеру на первом узле
            if len(game.world.nodes) > 0:
                first_node_id = list(game.world.nodes.keys())[0]
                self.renderer.center_on_node(first_node_id)
    
    def run(self):
        """Главный цикл игры"""
        if not self.game:
            print("Ошибка: игра не установлена")
            return
        
        while self.running:
            dt = self.clock.tick(60) / 1000.0  # delta time в секундах
            
            # Обработка событий
            self.handle_events()
            
            # Обновление игры
            if not self.game.is_paused:
                self.game.update(dt)
            
            # Рендеринг
            self.render()
            
            pygame.display.flip()
        
        pygame.quit()
    
    def handle_events(self):
        """Обрабатывает события"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_click(event)
            
            elif event.type == pygame.MOUSEWHEEL:
                self.handle_mouse_wheel(event)
    
    def handle_keydown(self, event: pygame.event.Event):
        """Обрабатывает нажатия клавиш"""
        if event.key == pygame.K_SPACE:
            # Пауза
            if self.game.is_paused:
                self.game.resume()
            else:
                self.game.pause()
        
        elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
            # Ускорение
            self.game.set_speed(self.game.speed_multiplier + 0.5)
        
        elif event.key == pygame.K_MINUS:
            # Замедление
            self.game.set_speed(self.game.speed_multiplier - 0.5)
        
        elif event.key == pygame.K_r:
            # Сброс скорости
            self.game.set_speed(1.0)
        
        elif event.key == pygame.K_ESCAPE:
            # Выход
            self.running = False
    
    def handle_mouse_click(self, event: pygame.event.Event):
        """Обрабатывает клики мыши"""
        if not self.renderer:
            return
        
        if event.button == 1:  # ЛКМ
            # Выбор узла или установка цели
            node_id = self.renderer.get_node_at_screen_pos(event.pos[0], event.pos[1])
            if node_id:
                self.selected_node_id = node_id
                
                # Если есть отряд, устанавливаем цель движения
                if self.game.player_squad:
                    self.set_movement_target(node_id)
        
        elif event.button == 3:  # ПКМ
            # Сброс выбора
            self.selected_node_id = None
    
    def handle_mouse_wheel(self, event: pygame.event.Event):
        """Обрабатывает колесо мыши (масштаб)"""
        if not self.renderer:
            return
        
        self.renderer.zoom += event.y * 0.1
        self.renderer.zoom = max(0.1, min(5.0, self.renderer.zoom))
    
    def set_movement_target(self, target_node_id: str):
        """Устанавливает цель движения для отряда"""
        if not self.game.player_squad:
            return
        
        squad = self.game.player_squad
        current_node_id = squad.current_node_id
        
        if not current_node_id:
            return
        
        # Находим путь
        path = self.game.world.find_path(current_node_id, target_node_id)
        if path:
            squad.path = path
            squad.target_node_id = target_node_id
            print(f"Путь установлен: {current_node_id} -> {target_node_id}")
            print(f"Путь: {' -> '.join(path)}")
        else:
            print(f"Путь не найден: {current_node_id} -> {target_node_id}")
    
    def render(self):
        """Рендерит игру"""
        if not self.renderer:
            return
        
        # Рендеринг карты
        squads = []
        if self.game.player_squad:
            squads.append(self.game.player_squad)
        
        self.renderer.render(squads)
        
        # Рендеринг UI
        self.render_ui()
    
    def render_ui(self):
        """Рендерит UI элементы"""
        # Информация о паузе
        if self.game.is_paused:
            pause_text = self.font.render("ПАУЗА", True, (255, 0, 0))
            self.screen.blit(pause_text, (10, 10))
        
        # Скорость времени
        speed_text = self.small_font.render(f"Скорость: {self.game.speed_multiplier:.1f}x", True, (0, 0, 0))
        self.screen.blit(speed_text, (10, 40))
        
        # Время игры
        if self.game.time and self.game.time.calendar:
            time_text = self.small_font.render(
                f"День: {self.game.time.calendar.day}, Неделя: {self.game.time.calendar.week}",
                True, (0, 0, 0)
            )
            self.screen.blit(time_text, (10, 60))
        
        # Информация о выбранном узле
        if self.selected_node_id:
            node = self.game.world.get_node(self.selected_node_id)
            if node:
                info_lines = [
                    f"Узел: {node.name}",
                    f"Тип: {node.node_type}",
                    f"Королевство: {node.kingdom or 'Нет'}"
                ]
                y_offset = 90
                for line in info_lines:
                    text = self.small_font.render(line, True, (0, 0, 0))
                    self.screen.blit(text, (10, y_offset))
                    y_offset += 20
        
        # Управление
        controls = [
            "Пробел - Пауза",
            "+/- - Скорость",
            "R - Сброс скорости",
            "ЛКМ - Выбрать узел/Установить цель",
            "Колесо мыши - Масштаб"
        ]
        y_offset = self.height - len(controls) * 20 - 10
        for control in controls:
            text = self.small_font.render(control, True, (100, 100, 100))
            self.screen.blit(text, (10, y_offset))
            y_offset += 20
