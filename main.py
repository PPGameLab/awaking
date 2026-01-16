"""
Главный файл для запуска игры
"""
import sys
from pathlib import Path

# Добавляем src в путь для импортов
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.game import Game


def main():
    """Главная функция"""
    import sys
    import io
    # Устанавливаем UTF-8 для вывода
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("=== Awaking - Fantasy Strategy ===")
    print("Starting game...")
    
    game = Game()
    
    # Инициализируем игру (загружает или генерирует карту)
    game.initialize(generate_map=True)
    
    # Создаём начальный отряд игрока
    game.start_new_game()
    
    print(f"\nGame initialized!")
    print(f"Time: {game.time.calendar}")
    print(f"World: {len(game.world.nodes)} nodes, {len(game.world.edges)} edges")
    print(f"Kingdoms: {len(game.world.kingdoms)}")
    if game.player_squad:
        print(f"\nPlayer squad: {game.player_squad.name}")
        print(f"Squad size: {game.player_squad.size}")
        print(f"Health: {game.player_squad.total_health:.1f}")
        print(f"Damage: {game.player_squad.total_damage:.1f}")
        print(f"Speed: {game.player_squad.average_speed:.1f}")
        if game.player_squad.current_node_id:
            current_node = game.world.get_node(game.player_squad.current_node_id)
            if current_node:
                print(f"Location: {current_node.name} ({game.player_squad.current_node_id})")
    
    # Показываем пример поиска пути
    if len(game.world.nodes) > 2:
        node_ids = list(game.world.nodes.keys())
        start = node_ids[0]
        goal = node_ids[-1] if len(node_ids) > 1 else node_ids[0]
        path = game.world.find_path(start, goal)
        if path:
            print(f"\nExample path from {start} to {goal}: {len(path)} nodes")
    
    print("\nGame ready for development!")
    print("\nTo visualize map:")
    print("  python visualize_map.py          - Simple visualization")
    print("  python visualize_map_bb.py        - Battle Brothers style (recommended)")
    print("  python visualize_map_interactive.py - Interactive (click to find paths)")


if __name__ == "__main__":
    main()
