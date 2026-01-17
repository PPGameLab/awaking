"""
Главный файл для запуска игры в pygame
"""
import sys
import io

# Устанавливаем UTF-8 для вывода
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import sys
from pathlib import Path

# Добавляем корень проекта в путь для импортов
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Импортируем из src
from src.core.game import Game
from src.core.world import World
from src.ui.game_window import GameWindow


def main():
    """Главная функция"""
    print("=== Awaking - Pygame Version ===")
    print()
    
    # Создаём игру
    game = Game()
    
    # Создаём простую карту (3 узла треугольником)
    print("Создание простой карты...")
    game.world.create_simple_map()
    
    # Инициализируем игру
    game.initialize(generate_map=False)  # Не генерируем из конфига
    
    # Создаём отряд
    game.start_new_game()
    
    # Размещаем отряд в первом узле
    if game.player_squad and len(game.world.nodes) > 0:
        first_node_id = list(game.world.nodes.keys())[0]
        game.player_squad.current_node_id = first_node_id
        print(f"Отряд размещён в узле: {first_node_id}")
    
    # Создаём окно
    window = GameWindow(width=1200, height=800)
    window.set_game(game)
    
    print()
    print("Запуск игры...")
    print("Управление:")
    print("  Пробел - Пауза")
    print("  +/- - Скорость времени")
    print("  R - Сброс скорости")
    print("  ЛКМ - Выбрать узел/Установить цель движения")
    print("  Колесо мыши - Масштаб")
    print("  ESC - Выход")
    print()
    
    # Запускаем главный цикл
    window.run()


if __name__ == "__main__":
    main()
