"""
Система времени игры
"""
from dataclasses import dataclass
from typing import Callable, List


@dataclass
class Calendar:
    """Календарь игры"""
    day: int = 1
    week: int = 1
    month: int = 1
    year: int = 1
    
    def __str__(self):
        return f"День {self.day}, Неделя {self.week}, Месяц {self.month}, Год {self.year}"


class GameTime:
    """Система времени игры (непрерывное время с тиками)"""
    
    def __init__(self):
        self.total_time: float = 0.0  # Общее время в секундах
        self.calendar = Calendar()
        
        # Константы времени
        self.SECONDS_PER_DAY = 60.0  # 1 игровой день = 60 секунд реального времени
        self.DAYS_PER_WEEK = 7
        self.WEEKS_PER_MONTH = 4
        self.MONTHS_PER_YEAR = 12
        
        # События календаря
        self.weekly_callbacks: List[Callable] = []
        self.daily_callbacks: List[Callable] = []
    
    def tick(self, delta_time: float):
        """Обновление времени (вызывается каждый кадр)"""
        self.total_time += delta_time
        
        # Обновляем календарь
        days_passed = self.total_time / self.SECONDS_PER_DAY
        new_day = int(days_passed) + 1
        
        if new_day > self.calendar.day:
            # Прошёл новый день
            old_week = self.calendar.week
            self.calendar.day = new_day
            
            # Проверяем, прошла ли неделя
            if self.calendar.day > self.DAYS_PER_WEEK:
                self.calendar.day = 1
                self.calendar.week += 1
                
                # Вызываем еженедельные события
                for callback in self.weekly_callbacks:
                    callback()
            
            # Проверяем, прошёл ли месяц
            if self.calendar.week > self.WEEKS_PER_MONTH:
                self.calendar.week = 1
                self.calendar.month += 1
            
            # Проверяем, прошёл ли год
            if self.calendar.month > self.MONTHS_PER_YEAR:
                self.calendar.month = 1
                self.calendar.year += 1
            
            # Вызываем ежедневные события
            for callback in self.daily_callbacks:
                callback()
    
    def get_current_day(self) -> int:
        """Возвращает текущий день"""
        return int(self.total_time / self.SECONDS_PER_DAY) + 1
    
    def add_weekly_callback(self, callback: Callable):
        """Добавляет функцию, вызываемую каждую неделю"""
        self.weekly_callbacks.append(callback)
    
    def add_daily_callback(self, callback: Callable):
        """Добавляет функцию, вызываемую каждый день"""
        self.daily_callbacks.append(callback)
