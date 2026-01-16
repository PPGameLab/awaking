"""
Интерактивная визуализация карты (с кликами)
"""
import sys
from pathlib import Path

# Добавляем src в путь для импортов
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.world import World
from utils.map_visualizer_interactive import InteractiveMapVisualizer


def main():
    """Интерактивная визуализация карты"""
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("=== Interactive Map Visualization ===")
    print("Instructions:")
    print("  1st click: Select start node")
    print("  2nd click: Select goal node (path will be calculated)")
    print("  3rd click: Reset")
    print()
    
    # Загружаем карту
    world = World(load_saved=True)
    
    if len(world.nodes) == 0:
        print("Error: No map loaded. Run 'python generate_map.py' first.")
        return
    
    print(f"Loaded map: {len(world.nodes)} nodes, {len(world.edges)} edges")
    print("Click on the map to select nodes...")
    print()
    
    # Создаём интерактивный визуализатор
    visualizer = InteractiveMapVisualizer(world)
    visualizer.show()


if __name__ == "__main__":
    main()
