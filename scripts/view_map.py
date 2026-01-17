"""
Просмотрщик статической карты
Позволяет визуализировать и проверять карту без запуска игры
"""
import sys
import io
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Устанавливаем UTF-8 для вывода
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Добавляем корень проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.widgets import Button
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib not installed. Visualization disabled.")


class MapViewer:
    """Просмотрщик карты"""
    
    def __init__(self, map_path: Path):
        self.map_path = map_path
        self.data = self._load_map()
        self.metadata = self.data.get("metadata", {})
        self.defaults = self.metadata.get("defaults", {})
        
        # Применяем дефолты к узлам
        self.nodes = self._apply_node_defaults(self.data.get("nodes", {}))
        self.edges = self.data.get("edges", [])
    
    def _apply_node_defaults(self, nodes: Dict) -> Dict:
        """Применяет дефолты к узлам"""
        node_ui_default = self.defaults.get("node_ui", {})
        node_meta_default = self.defaults.get("node_meta", {})
        
        result = {}
        for node_id, node_data in nodes.items():
            node = node_data.copy()
            
            # Применяем дефолты для ui
            if "ui" not in node:
                node["ui"] = node_ui_default.copy()
            else:
                # Мержим с дефолтами
                ui = node_ui_default.copy()
                ui.update(node.get("ui", {}))
                node["ui"] = ui
            
            # Применяем дефолты для meta
            if "meta" not in node:
                node["meta"] = node_meta_default.copy()
            else:
                # Мержим с дефолтами
                meta = node_meta_default.copy()
                meta.update(node.get("meta", {}))
                node["meta"] = meta
            
            result[node_id] = node
        
        return result
        
    def _load_map(self) -> Dict:
        """Загружает карту из JSON"""
        if not self.map_path.exists():
            raise FileNotFoundError(f"Map file not found: {self.map_path}")
        
        with open(self.map_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Валидирует карту"""
        errors = []
        warnings = []
        
        # Получаем словарь допустимых значений
        dictionary = self.metadata.get("dictionary", {})
        allowed_owners = set(dictionary.get("owners", []))
        allowed_road_types = set(dictionary.get("road_types", []))
        allowed_biomes = set(dictionary.get("biomes", []))
        allowed_node_tags = set(dictionary.get("node_tags", []))
        
        # Проверка узлов
        node_ids = set()
        for node_id, node_data in self.nodes.items():
            # Уникальность ID (ключ в словаре)
            if node_id in node_ids:
                errors.append(f"Duplicate node ID: {node_id}")
            node_ids.add(node_id)
            
            # Обязательные поля (id не нужен, он уже в ключе)
            if "name" not in node_data:
                errors.append(f"Node {node_id} missing 'name'")
            if "pos" not in node_data:
                errors.append(f"Node {node_id} missing 'pos'")
            elif len(node_data["pos"]) != 2:
                errors.append(f"Node {node_id} invalid 'pos' (must be [x, y])")
            
            # Валидация owner_id по словарю
            owner_id = node_data.get("owner_id")
            if owner_id is not None:
                if allowed_owners and owner_id not in allowed_owners:
                    errors.append(f"Node {node_id} has invalid owner_id '{owner_id}'. Allowed: {sorted(allowed_owners)}")
            
            # Валидация tags по словарю
            tags = node_data.get("tags", [])
            if allowed_node_tags:
                for tag in tags:
                    if tag not in allowed_node_tags:
                        warnings.append(f"Node {node_id} has unknown tag '{tag}'. Allowed: {sorted(allowed_node_tags)}")
        
        # Проверка рёбер
        edge_set = set()
        for i, edge in enumerate(self.edges):
            from_id = edge.get("from")
            to_id = edge.get("to")
            
            if not from_id or not to_id:
                errors.append(f"Edge {i} missing 'from' or 'to'")
                continue
            
            # Проверка существования узлов
            if from_id not in self.nodes:
                errors.append(f"Edge {i} references non-existent node: {from_id}")
            if to_id not in self.nodes:
                errors.append(f"Edge {i} references non-existent node: {to_id}")
            
            # Валидация road_type по словарю
            road_type = edge.get("road_type")
            if road_type is not None:
                if allowed_road_types and road_type not in allowed_road_types:
                    errors.append(f"Edge {i} ({from_id} -> {to_id}) has invalid road_type '{road_type}'. Allowed: {sorted(allowed_road_types)}")
            
            # Валидация biome по словарю
            biome = edge.get("biome")
            if biome is not None:
                if allowed_biomes and biome not in allowed_biomes:
                    warnings.append(f"Edge {i} ({from_id} -> {to_id}) has unknown biome '{biome}'. Allowed: {sorted(allowed_biomes)}")
            
            # Проверка дубликатов (A-B == B-A)
            canonical = tuple(sorted([from_id, to_id]))
            if canonical in edge_set:
                warnings.append(f"Duplicate edge: {from_id} <-> {to_id}")
            edge_set.add(canonical)
        
        # Проверка связности
        if self.nodes and self.edges:
            components = self._find_connected_components()
            if len(components) > 1:
                warnings.append(f"Map has {len(components)} disconnected components")
        
        return len(errors) == 0, errors + warnings
    
    def _find_connected_components(self) -> List[set]:
        """Находит компоненты связности"""
        # Строим граф
        graph = {node_id: set() for node_id in self.nodes.keys()}
        for edge in self.edges:
            from_id = edge.get("from")
            to_id = edge.get("to")
            if from_id and to_id and from_id in graph and to_id in graph:
                graph[from_id].add(to_id)
                graph[to_id].add(from_id)
        
        # DFS для поиска компонент
        visited = set()
        components = []
        
        for node_id in graph:
            if node_id not in visited:
                component = set()
                stack = [node_id]
                while stack:
                    current = stack.pop()
                    if current not in visited:
                        visited.add(current)
                        component.add(current)
                        stack.extend(graph[current] - visited)
                components.append(component)
        
        return components
    
    def get_statistics(self) -> Dict:
        """Возвращает статистику карты"""
        # Статистика узлов
        node_count = len(self.nodes)
        owners = {}
        tags_count = {}
        
        for node_data in self.nodes.values():
            owner = node_data.get("owner_id")
            if owner:
                owners[owner] = owners.get(owner, 0) + 1
            
            for tag in node_data.get("tags", []):
                tags_count[tag] = tags_count.get(tag, 0) + 1
        
        # Статистика рёбер
        edge_count = len(self.edges)
        road_types = {}
        for edge in self.edges:
            road_type = edge.get("road_type", "unknown")
            road_types[road_type] = road_types.get(road_type, 0) + 1
        
        # Степень узлов
        node_degrees = {node_id: 0 for node_id in self.nodes.keys()}
        for edge in self.edges:
            from_id = edge.get("from")
            to_id = edge.get("to")
            if from_id in node_degrees:
                node_degrees[from_id] += 1
            if to_id in node_degrees:
                node_degrees[to_id] += 1
        
        degrees = list(node_degrees.values())
        min_degree = min(degrees) if degrees else 0
        max_degree = max(degrees) if degrees else 0
        avg_degree = sum(degrees) / len(degrees) if degrees else 0
        
        # Границы
        bounds = self.metadata.get("bounds", {})
        
        return {
            "nodes": {
                "total": node_count,
                "by_owner": owners,
                "tags": tags_count
            },
            "edges": {
                "total": edge_count,
                "by_road_type": road_types
            },
            "connectivity": {
                "min_degree": min_degree,
                "max_degree": max_degree,
                "avg_degree": round(avg_degree, 2)
            },
            "bounds": bounds
        }
    
    def visualize(self, interactive: bool = False, export_path: Optional[Path] = None):
        """Визуализирует карту"""
        if not HAS_MATPLOTLIB:
            print("Cannot visualize: matplotlib not installed")
            return
        
        fig, ax = plt.subplots(figsize=(12, 10))
        ax.set_aspect('equal')
        
        # Получаем границы
        bounds = self.metadata.get("bounds", {})
        if bounds:
            ax.set_xlim(bounds.get("min_x", 0), bounds.get("max_x", 1000))
            ax.set_ylim(bounds.get("min_y", 0), bounds.get("max_y", 1000))
        else:
            # Автоматически вычисляем границы
            if self.nodes:
                x_coords = [node["pos"][0] for node in self.nodes.values()]
                y_coords = [node["pos"][1] for node in self.nodes.values()]
                margin = 50
                ax.set_xlim(min(x_coords) - margin, max(x_coords) + margin)
                ax.set_ylim(min(y_coords) - margin, max(y_coords) + margin)
        
        # Рисуем рёбра
        road_type_colors = {
            "main": "#8B4513",
            "secondary": "#A0522D",
            "path": "#CD853F",
            "center": "#FF6347",
            None: "#808080"
        }
        
        for edge in self.edges:
            from_id = edge.get("from")
            to_id = edge.get("to")
            
            if from_id not in self.nodes or to_id not in self.nodes:
                continue
            
            from_pos = self.nodes[from_id]["pos"]
            to_pos = self.nodes[to_id]["pos"]
            
            road_type = edge.get("road_type")
            color = road_type_colors.get(road_type, road_type_colors[None])
            
            # Толщина линии зависит от типа дороги
            linewidth = 2.0 if road_type == "main" else 1.5 if road_type == "secondary" else 1.0
            
            ax.plot(
                [from_pos[0], to_pos[0]],
                [from_pos[1], to_pos[1]],
                color=color,
                linewidth=linewidth,
                alpha=0.6,
                zorder=1
            )
        
        # Рисуем узлы
        for node_id, node_data in self.nodes.items():
            pos = node_data["pos"]
            owner = node_data.get("owner_id")
            
            # Цвет узла зависит от владельца
            if owner:
                # Простой хэш для цвета
                color_hash = hash(owner) % 360
                color = plt.cm.hsv(color_hash / 360)
            else:
                color = "#FFD700"  # Золотой для нейтральных
            
            ax.scatter(
                pos[0], pos[1],
                s=100,
                c=[color],
                edgecolors='black',
                linewidths=2,
                zorder=2,
                picker=True
            )
            
            # Подписи узлов
            ax.annotate(
                node_data.get("name", node_id),
                (pos[0], pos[1]),
                xytext=(5, 5),
                textcoords='offset points',
                fontsize=8,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7)
            )
        
        ax.set_xlabel("X (world units)")
        ax.set_ylabel("Y (world units)")
        ax.set_title(f"Map: {self.map_path.name}")
        ax.grid(True, alpha=0.3)
        
        # Статистика
        stats = self.get_statistics()
        stats_text = (
            f"Nodes: {stats['nodes']['total']}\n"
            f"Edges: {stats['edges']['total']}\n"
            f"Avg degree: {stats['connectivity']['avg_degree']}"
        )
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        if export_path:
            plt.savefig(export_path, dpi=150, bbox_inches='tight')
            print(f"Map exported to: {export_path}")
        
        if interactive:
            def on_pick(event):
                if event.artist != ax:
                    return
                ind = event.ind[0]
                # Находим узел по координатам
                for node_id, node_data in self.nodes.items():
                    pos = node_data["pos"]
                    if abs(pos[0] - event.mouseevent.xdata) < 10 and \
                       abs(pos[1] - event.mouseevent.ydata) < 10:
                        print(f"\nNode: {node_id}")
                        print(f"  Name: {node_data.get('name')}")
                        print(f"  Position: {pos}")
                        print(f"  Owner: {node_data.get('owner_id', 'None')}")
                        print(f"  Tags: {node_data.get('tags', [])}")
                        break
            
            fig.canvas.mpl_connect('pick_event', on_pick)
            plt.show()
        elif not export_path:
            plt.show()


def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(description="View and validate static map")
    parser.add_argument("map_name", help="Map name (without .json extension)")
    parser.add_argument("--interactive", "-i", action="store_true",
                       help="Interactive mode (click nodes to see info)")
    parser.add_argument("--export", "-e", type=str,
                       help="Export map to image file")
    parser.add_argument("--validate", "-v", action="store_true",
                       help="Validate map and show statistics")
    
    args = parser.parse_args()
    
    # Путь к карте
    map_path = project_root / "data" / "maps" / f"{args.map_name}.json"
    
    if not map_path.exists():
        print(f"Error: Map file not found: {map_path}")
        sys.exit(1)
    
    # Загружаем карту
    viewer = MapViewer(map_path)
    
    # Валидация
    if args.validate:
        is_valid, messages = viewer.validate()
        stats = viewer.get_statistics()
        
        print(f"\n=== Map Validation: {args.map_name} ===")
        if is_valid:
            print("✓ Map is valid")
        else:
            print("✗ Map has errors")
        
        if messages:
            print("\nMessages:")
            for msg in messages:
                print(f"  {msg}")
        
        print(f"\n=== Statistics ===")
        print(f"Nodes: {stats['nodes']['total']}")
        print(f"Edges: {stats['edges']['total']}")
        print(f"Connectivity: min={stats['connectivity']['min_degree']}, "
              f"max={stats['connectivity']['max_degree']}, "
              f"avg={stats['connectivity']['avg_degree']}")
        
        if stats['nodes']['by_owner']:
            print(f"\nNodes by owner:")
            for owner, count in stats['nodes']['by_owner'].items():
                print(f"  {owner}: {count}")
        
        if stats['edges']['by_road_type']:
            print(f"\nEdges by road type:")
            for road_type, count in stats['edges']['by_road_type'].items():
                print(f"  {road_type}: {count}")
    
    # Визуализация
    export_path = Path(args.export) if args.export else None
    viewer.visualize(interactive=args.interactive, export_path=export_path)


if __name__ == "__main__":
    main()
