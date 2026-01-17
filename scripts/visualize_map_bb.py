"""
Визуализация карты в стиле Battle Brothers
"""
import sys
from pathlib import Path

# Добавляем src в путь для импортов
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.world import World
from utils.map_visualizer_bb import BattleBrothersStyleVisualizer


def main():
    """Визуализирует карту в стиле Battle Brothers"""
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("=== Map Visualization (Battle Brothers Style) ===")
    
    # Загружаем карту
    world = World(load_saved=True)
    
    if len(world.nodes) == 0:
        print("Error: No map loaded. Run 'python generate_map.py' first.")
        return
    
    print(f"Loaded map: {len(world.nodes)} nodes, {len(world.edges)} edges")
    
    # Создаём визуализатор
    visualizer = BattleBrothersStyleVisualizer()
    
    # Пример: находим путь между двумя узлами
    node_ids = list(world.nodes.keys())
    if len(node_ids) >= 2:
        start = "Center"
        goal = node_ids[-1] if node_ids[-1] != "Center" else node_ids[-2]
        
        if start in world.nodes and goal in world.nodes:
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
    else:
        # Рисуем просто карту
        visualizer.draw_map(world.nodes, world.edges)
    
    # Сохраняем и показываем
    visualizer.save("map_bb_style.png")
    print("\nMap visualization ready!")
    print("Close the window to exit.")
    visualizer.show()


if __name__ == "__main__":
    main()
