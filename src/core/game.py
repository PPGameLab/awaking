"""
Главный игровой цикл
"""
from typing import Optional
from core.world import World
from entities.unit import Squad
from core.time import GameTime


class Game:
    """Главный класс игры"""
    
    def __init__(self):
        self.world = World()
        self.time = GameTime()
        self.player_squad: Optional[Squad] = None
        self.is_paused = False
        self.speed_multiplier = 1.0  # Множитель скорости времени
    
    def initialize(self, generate_map: bool = True):
        """
        Инициализация игры
        
        Args:
            generate_map: Если True и карта не загружена, генерирует новую карту
        """
        from utils.map_data import CAPITALS, CENTER_POS, RING_ORDER
        
        # Если карта не загружена и нужно сгенерировать
        if generate_map and len(self.world.nodes) == 0:
            print("Генерация карты...")
            nodes_count, edges_count = self.world.generate_from_config(
                capitals=CAPITALS,
                center_pos=CENTER_POS,
                ring_order=RING_ORDER,
                save_map=True
            )
            print(f"Карта сгенерирована: {nodes_count} узлов, {edges_count} рёбер")
    
    def start_new_game(self):
        """Начинает новую игру"""
        # Герой начинает одним персонажем в центре
        from entities.unit import Character, Squad, UnitType
        
        leader = Character(
            strength=5, dexterity=5, endurance=5,
            spirit=5, greed=5, luck=5, intelligence=5, wisdom=5
        )
        
        self.player_squad = Squad(
            id="player_squad",
            name="Отряд игрока",
            leader=leader,
            unit_type=UnitType.INFANTRY
        )
        
        # Размещаем отряд в центре
        center_node = self.world.get_node("Center")
        if center_node:
            self.player_squad.current_node_id = "Center"
            print(f"Отряд размещён в узле: {center_node.name}")
        else:
            # Если центр не найден, берём первый доступный узел
            if len(self.world.nodes) > 0:
                first_node_id = list(self.world.nodes.keys())[0]
                self.player_squad.current_node_id = first_node_id
                print(f"Центр не найден, отряд размещён в узле: {first_node_id}")
            else:
                print("Ошибка: карта пуста, невозможно разместить отряд")
    
    def update(self, delta_time: float):
        """Обновление игрового состояния"""
        if self.is_paused:
            return
        
        # Обновляем время
        actual_delta = delta_time * self.speed_multiplier
        self.time.tick(actual_delta)
        
        # Обновляем отряды
        if self.player_squad:
            self._update_squad(self.player_squad, actual_delta)
    
    def _update_squad(self, squad: Squad, delta_time: float):
        """Обновляет состояние отряда"""
        # TODO: Движение по карте, расход ресурсов, события
        pass
    
    def pause(self):
        """Ставит игру на паузу"""
        self.is_paused = True
    
    def resume(self):
        """Возобновляет игру"""
        self.is_paused = False
    
    def set_speed(self, multiplier: float):
        """Устанавливает множитель скорости времени"""
        self.speed_multiplier = max(0.0, min(10.0, multiplier))  # Ограничение 0-10x
