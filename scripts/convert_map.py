"""
Конвертер карты из старого формата в новый (world_v1)
"""
import sys
import io
import json
import argparse
from pathlib import Path
from datetime import datetime

# Устанавливаем UTF-8 для вывода
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Добавляем корень проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def convert_legacy_map(input_path: Path, output_path: Path, km_per_unit: float = 0.1):
    """Конвертирует карту из старого формата в новый"""
    
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Извлекаем данные
    old_nodes = data.get("nodes", [])
    old_edges = data.get("edges", [])
    old_metadata = data.get("metadata", {})
    
    # Конвертируем узлы (из list в dict)
    new_nodes = {}
    for node in old_nodes:
        node_id = node.get("id")
        if not node_id:
            continue
        
        # Конвертируем в новый формат (id - это ключ, не поле)
        # ui и meta не добавляем - будут использоваться дефолты
        new_node = {
            "name": node.get("name", node_id),
            "pos": node.get("pos", [0.0, 0.0]),
            "tags": [],
            "owner_id": node.get("kingdom")
        }
        
        # Добавляем ui/meta только если они отличаются от дефолтов
        # (пока не реализовано, можно добавить позже)
        
        # Конвертируем старые поля в tags
        if node.get("node_type"):
            new_node["tags"].append(node.get("node_type").lower())
        if node.get("role"):
            new_node["tags"].append(node.get("role").lower())
        
        new_nodes[node_id] = new_node
    
    # Вычисляем границы
    if new_nodes:
        x_coords = [node["pos"][0] for node in new_nodes.values()]
        y_coords = [node["pos"][1] for node in new_nodes.values()]
        bounds = {
            "min_x": min(x_coords),
            "max_x": max(x_coords),
            "min_y": min(y_coords),
            "max_y": max(y_coords)
        }
    else:
        bounds = {
            "min_x": 0.0,
            "max_x": 1000.0,
            "min_y": 0.0,
            "max_y": 1000.0
        }
    
    # Конвертируем рёбра
    new_edges = []
    for edge in old_edges:
        if isinstance(edge, list) and len(edge) >= 2:
            from_id = edge[0]
            to_id = edge[1]
        elif isinstance(edge, dict):
            from_id = edge.get("from") or edge.get("from_id")
            to_id = edge.get("to") or edge.get("to_id")
        else:
            continue
        
        if not from_id or not to_id:
            continue
        
        new_edge = {
            "from": from_id,
            "to": to_id,
            "road_type": None,  # По умолчанию
            "biome": None,
            "tags": []
        }
        
        # Если в старом формате был road_type
        if isinstance(edge, dict) and "road_type" in edge:
            new_edge["road_type"] = edge["road_type"]
        
        new_edges.append(new_edge)
    
    # Создаём новую структуру
    new_data = {
        "metadata": {
            "version": "1.0",
            "schema_version": "1",
            "created_at": datetime.now().isoformat() + "Z",
            "updated_at": datetime.now().isoformat() + "Z",
            "bounds": bounds,
            "km_per_unit": km_per_unit,
            "defaults": {
                "node_ui": {
                    "icon": None,
                    "color": None,
                    "size": None
                },
                "node_meta": {
                    "importance": None,
                    "lore": None
                }
            },
            "auto_bounds": True,
            "entities": {
                "owners": {},
                "road_types": {
                    "main": {},
                    "secondary": {},
                    "path": {},
                    "center": {}
                },
                "biomes": {},
                "node_tags": {}
            },
            "notes": f"Converted from {input_path.name}"
        },
        "nodes": new_nodes,
        "edges": new_edges
    }
    
    # Сохраняем
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)
    
    print(f"Converted {len(new_nodes)} nodes and {len(new_edges)} edges")
    print(f"Output: {output_path}")


def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(description="Convert map from legacy format to world_v1")
    parser.add_argument("input", help="Input map file (legacy format)")
    parser.add_argument("--output", "-o", help="Output file (default: input_world_v1.json)")
    parser.add_argument("--km-per-unit", type=float, default=0.1,
                       help="Kilometers per world unit (default: 0.1)")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    if not input_path.exists():
        input_path = project_root / "data" / "maps" / f"{args.input}.json"
        if not input_path.exists():
            print(f"Error: Input file not found: {args.input}")
            sys.exit(1)
    
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.parent / f"{input_path.stem}_world_v1.json"
    
    convert_legacy_map(input_path, output_path, args.km_per_unit)


if __name__ == "__main__":
    main()
