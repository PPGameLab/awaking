"""
Юниты и отряды (Unit/Squad)
"""
from typing import List, Optional
from dataclasses import dataclass, field
from enum import Enum


class UnitType(Enum):
    """Типы юнитов"""
    INFANTRY = "пехота"  # MVP: только пехота


@dataclass
class Character:
    """Один персонаж в отряде"""
    # Характеристики (из attributes.json)
    strength: int = 1
    dexterity: int = 1
    endurance: int = 1
    spirit: int = 1
    greed: int = 1
    luck: int = 1
    intelligence: int = 1
    wisdom: int = 1
    
    # Параметры (вычисляются из характеристик)
    health: float = 0.0
    damage: float = 0.0
    speed: float = 0.0
    
    level: int = 1
    
    def calculate_parameters(self):
        """Вычисляет параметры на основе характеристик"""
        # Здоровье: Выносливость × 3.0, Сила × 1.0, Дух × 0.5, Удача × 0.01, Жадность × 0.1 × условие
        self.health = (
            self.endurance * 3.0 +
            self.strength * 1.0 +
            self.spirit * 0.5 +
            self.luck * 0.01 +
            self.greed * 0.1  # TODO: условие для жадности
        )
        
        # Урон: Сила × 4.0, Ловкость × 2.0, Удача × 0.01, Жадность × 0.1 × условие
        self.damage = (
            self.strength * 4.0 +
            self.dexterity * 2.0 +
            self.luck * 0.01 +
            self.greed * 0.1  # TODO: условие для жадности
        )
        
        # Скорость: Ловкость × 3.0, Удача × 0.01, Жадность × 0.1 × условие
        self.speed = (
            self.dexterity * 3.0 +
            self.luck * 0.01 +
            self.greed * 0.1  # TODO: условие для жадности
        )


@dataclass
class Squad:
    """Отряд (юнит на глобальной карте)"""
    id: str
    name: str
    leader: Character  # Лидер отряда
    members: List[Character] = field(default_factory=list)  # Члены отряда
    unit_type: UnitType = UnitType.INFANTRY
    
    # Ресурсы
    food: float = 0.0  # Еда (тратится ежедневно)
    money: float = 0.0  # Деньги (зарплата еженедельно)
    
    # Позиция
    current_node_id: Optional[str] = None
    target_node_id: Optional[str] = None
    path: List[str] = field(default_factory=list)  # Путь к цели
    
    def __post_init__(self):
        """Инициализация после создания"""
        # Вычисляем параметры для всех персонажей
        self.leader.calculate_parameters()
        for char in self.members:
            char.calculate_parameters()
    
    @property
    def total_health(self) -> float:
        """Общее здоровье отряда"""
        return sum(char.health for char in [self.leader] + self.members)
    
    @property
    def total_damage(self) -> float:
        """Общий урон отряда"""
        return sum(char.damage for char in [self.leader] + self.members)
    
    @property
    def average_speed(self) -> float:
        """Средняя скорость отряда"""
        speeds = [char.speed for char in [self.leader] + self.members]
        return sum(speeds) / len(speeds) if speeds else 0.0
    
    @property
    def size(self) -> int:
        """Размер отряда"""
        return 1 + len(self.members)  # Лидер + члены
    
    def add_member(self, character: Character):
        """Добавляет члена в отряд"""
        if self.size >= 50:  # Максимум 50 человек
            raise ValueError("Отряд достиг максимального размера (50 человек)")
        character.calculate_parameters()
        self.members.append(character)
    
    def remove_member(self, character: Character):
        """Удаляет члена из отряда"""
        if character == self.leader:
            raise ValueError("Нельзя удалить лидера отряда")
        self.members.remove(character)
