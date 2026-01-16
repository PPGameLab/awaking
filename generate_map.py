"""
Скрипт для генерации и сохранения карты
"""
import sys
from pathlib import Path

# Добавляем src в путь для импортов
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.world import World
from utils.map_data import CAPITALS, CENTER_POS, RING_ORDER


def main():
    """Генерирует и сохраняет карту"""
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("=== Map Generation ===")
    
    world = World(load_saved=False)  # Не загружаем сохранённую карту
    
    print(f"Capitals: {len(CAPITALS)}")
    print(f"Center: {CENTER_POS}")
    print(f"Ring order: {RING_ORDER}")
    print()
    
    nodes_count, edges_count = world.generate_from_config(
        capitals=CAPITALS,
        center_pos=CENTER_POS,
        ring_order=RING_ORDER,
        save_map=True
    )
    
    print()
    print(f"Map generated successfully!")
    print(f"  Nodes: {nodes_count}")
    print(f"  Edges: {edges_count}")
    print(f"  Kingdoms: {len(world.kingdoms)}")
    
    # Статистика по типам узлов
    node_types = {}
    for node in world.nodes.values():
        node_types[node.node_type] = node_types.get(node.node_type, 0) + 1
    
    print()
    print("Node types statistics:")
    for node_type, count in sorted(node_types.items()):
        print(f"  {node_type}: {count}")


if __name__ == "__main__":
    main()
