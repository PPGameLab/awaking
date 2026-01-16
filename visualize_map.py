"""
Скрипт для визуализации карты
"""
import sys
from pathlib import Path

# Добавляем src в путь для импортов
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.world import World
from utils.map_visualizer import MapVisualizer


def main():
    """Визуализирует карту"""
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("=== Map Visualization ===")
    
    # Загружаем карту
    world = World(load_saved=True)
    
    if len(world.nodes) == 0:
        print("Error: No map loaded. Run 'python generate_map.py' first.")
        return
    
    print(f"Loaded map: {len(world.nodes)} nodes, {len(world.edges)} edges")
    
    # Создаём визуализатор
    visualizer = MapVisualizer()
    
    # Пример: находим путь между двумя узлами
    node_ids = list(world.nodes.keys())
    if len(node_ids) >= 2:
        start = node_ids[0]
        goal = node_ids[-1]
        path = world.find_path(start, goal)
        
        print(f"\nPath from {start} to {goal}:")
        if path:
            print(f"  Length: {len(path)} nodes")
            print(f"  Path: {' -> '.join(path[:5])}{'...' if len(path) > 5 else ''}")
        else:
            print("  No path found")
        
        # Рисуем карту с путём
        visualizer.draw_map(
            world.nodes,
            world.edges,
            path=path,
            start_node=start,
            goal_node=goal
        )
    else:
        # Рисуем просто карту
        visualizer.draw_map(world.nodes, world.edges)
    
    # Сохраняем и показываем
    visualizer.save("map_visualization.png")
    print("\nMap visualization ready!")
    print("Close the window to exit.")
    visualizer.show()


if __name__ == "__main__":
    main()
