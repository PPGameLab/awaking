"""
Скрипт для тестирования производительности игры
Можно запускать параллельно в консоли для мониторинга производительности
"""
import sys
import time
import random
import tracemalloc
import json
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import io

# Добавляем src в путь для импортов
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.world import World
from utils.map_data import CAPITALS, CENTER_POS, RING_ORDER
from utils.map_visualizer import MapVisualizer
from utils.map_visualizer_bb import BattleBrothersStyleVisualizer


class PerformanceBenchmark:
    """Класс для тестирования производительности"""
    
    def __init__(self):
        self.results: Dict[str, float] = {}
        self.world: World = None
        self.pathfinding_iterations: int = 100  # По умолчанию
        self.output_file: str = "scripts/benchmark_results.json"
        
    def run_all_tests(self, generate_new: bool = False, test_visualization: bool = True):
        """Запускает все тесты"""
        print("=" * 60)
        print("PERFORMANCE BENCHMARK")
        print("=" * 60)
        print()
        
        # Тест 1: Генерация карты
        if generate_new:
            self.test_map_generation()
        else:
            self.test_map_loading()
        
        # Тест 2: Pathfinding
        if self.world and len(self.world.nodes) > 0:
            self.test_pathfinding(iterations=self.pathfinding_iterations)
        
        # Тест 3: Визуализация
        if test_visualization and self.world and len(self.world.nodes) > 0:
            self.test_visualization()
        
        # Тест 4: Память
        self.test_memory()
        
        # Выводим результаты
        self.print_results()
        
        # Сохраняем результаты в файл
        self.save_results()
    
    def test_map_generation(self):
        """Тест генерации карты"""
        print("📊 Тест 1: Генерация карты...")
        
        # Замеряем память до
        tracemalloc.start()
        start_memory = tracemalloc.get_traced_memory()[0]
        
        # Генерируем карту
        start_time = time.perf_counter()
        self.world = World(load_saved=False)
        nodes_count, edges_count = self.world.generate_from_config(
            capitals=CAPITALS,
            center_pos=CENTER_POS,
            ring_order=RING_ORDER,
            save_map=False  # Не сохраняем для чистоты теста
        )
        end_time = time.perf_counter()
        
        # Замеряем память после
        end_memory = tracemalloc.get_traced_memory()[0]
        tracemalloc.stop()
        
        generation_time = (end_time - start_time) * 1000  # в мс
        memory_used = (end_memory - start_memory) / 1024  # в KB
        
        self.results["map_generation_time_ms"] = generation_time
        self.results["map_generation_memory_kb"] = memory_used
        self.results["nodes_count"] = nodes_count
        self.results["edges_count"] = edges_count
        
        print(f"  ✅ Время генерации: {generation_time:.2f} мс")
        print(f"  ✅ Память: {memory_used:.2f} KB")
        print(f"  ✅ Узлов: {nodes_count}, Рёбер: {edges_count}")
        print()
    
    def test_map_loading(self):
        """Тест загрузки карты"""
        print("📊 Тест 1: Загрузка карты...")
        
        # Замеряем память до
        tracemalloc.start()
        start_memory = tracemalloc.get_traced_memory()[0]
        
        # Загружаем карту
        start_time = time.perf_counter()
        self.world = World(load_saved=True)
        end_time = time.perf_counter()
        
        # Замеряем память после
        end_memory = tracemalloc.get_traced_memory()[0]
        tracemalloc.stop()
        
        load_time = (end_time - start_time) * 1000  # в мс
        memory_used = (end_memory - start_memory) / 1024  # в KB
        
        self.results["map_load_time_ms"] = load_time
        self.results["map_load_memory_kb"] = memory_used
        self.results["nodes_count"] = len(self.world.nodes)
        self.results["edges_count"] = len(self.world.edges)
        
        print(f"  ✅ Время загрузки: {load_time:.2f} мс")
        print(f"  ✅ Память: {memory_used:.2f} KB")
        print(f"  ✅ Узлов: {len(self.world.nodes)}, Рёбер: {len(self.world.edges)}")
        print()
    
    def test_pathfinding(self, iterations: int = 100):
        """Тест pathfinding (A* алгоритм)"""
        print(f"📊 Тест 2: Pathfinding ({iterations} итераций)...")
        
        if not self.world or len(self.world.nodes) < 2:
            print("  ⚠️  Недостаточно узлов для теста")
            return
        
        node_ids = list(self.world.nodes.keys())
        times = []
        
        # Выполняем множественные запросы pathfinding
        for i in range(iterations):
            start_id = random.choice(node_ids)
            goal_id = random.choice(node_ids)
            
            # Пропускаем одинаковые узлы
            while goal_id == start_id:
                goal_id = random.choice(node_ids)
            
            start_time = time.perf_counter()
            path = self.world.find_path(start_id, goal_id)
            end_time = time.perf_counter()
            
            times.append((end_time - start_time) * 1000)  # в мс
        
        # Статистика
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        total_time = sum(times)
        
        self.results["pathfinding_avg_ms"] = avg_time
        self.results["pathfinding_min_ms"] = min_time
        self.results["pathfinding_max_ms"] = max_time
        self.results["pathfinding_total_ms"] = total_time
        self.results["pathfinding_iterations"] = iterations
        
        print(f"  ✅ Среднее время: {avg_time:.3f} мс")
        print(f"  ✅ Минимум: {min_time:.3f} мс")
        print(f"  ✅ Максимум: {max_time:.3f} мс")
        print(f"  ✅ Общее время ({iterations} итераций): {total_time:.2f} мс")
        print()
    
    def test_visualization(self, test_simple: bool = True, test_bb: bool = True):
        """Тест визуализации"""
        print("📊 Тест 3: Визуализация карты...")
        
        if not self.world or len(self.world.nodes) == 0:
            print("  ⚠️  Карта не загружена")
            return
        
        # Простая визуализация
        if test_simple:
            print("  Тест простой визуализации...")
            visualizer = MapVisualizer()
            
            start_time = time.perf_counter()
            visualizer.draw_map(self.world.nodes, self.world.edges)
            end_time = time.perf_counter()
            
            simple_time = (end_time - start_time) * 1000  # в мс
            self.results["visualization_simple_ms"] = simple_time
            print(f"    ✅ Простая визуализация: {simple_time:.2f} мс")
        
        # Battle Brothers стиль
        if test_bb:
            print("  Тест Battle Brothers стиля...")
            visualizer_bb = BattleBrothersStyleVisualizer()
            
            start_time = time.perf_counter()
            visualizer_bb.draw_map(self.world.nodes, self.world.edges)
            end_time = time.perf_counter()
            
            bb_time = (end_time - start_time) * 1000  # в мс
            self.results["visualization_bb_ms"] = bb_time
            print(f"    ✅ Battle Brothers стиль: {bb_time:.2f} мс")
        
        print()
    
    def test_memory(self):
        """Тест использования памяти"""
        print("📊 Тест 4: Использование памяти...")
        
        tracemalloc.start()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        current_kb = current / 1024
        peak_kb = peak / 1024
        
        self.results["memory_current_kb"] = current_kb
        self.results["memory_peak_kb"] = peak_kb
        
        print(f"  ✅ Текущая память: {current_kb:.2f} KB")
        print(f"  ✅ Пиковая память: {peak_kb:.2f} KB")
        print()
    
    def print_results(self):
        """Выводит результаты в таблице"""
        print("=" * 60)
        print("РЕЗУЛЬТАТЫ")
        print("=" * 60)
        print()
        
        # Генерация/Загрузка
        if "map_generation_time_ms" in self.results:
            print(f"Генерация карты:")
            print(f"  Время: {self.results['map_generation_time_ms']:.2f} мс")
            print(f"  Память: {self.results['map_generation_memory_kb']:.2f} KB")
        elif "map_load_time_ms" in self.results:
            print(f"Загрузка карты:")
            print(f"  Время: {self.results['map_load_time_ms']:.2f} мс")
            print(f"  Память: {self.results['map_load_memory_kb']:.2f} KB")
        
        print()
        
        # Статистика карты
        if "nodes_count" in self.results:
            print(f"Статистика карты:")
            print(f"  Узлов: {self.results['nodes_count']}")
            print(f"  Рёбер: {self.results['edges_count']}")
            print()
        
        # Pathfinding
        if "pathfinding_avg_ms" in self.results:
            print(f"Pathfinding ({self.results['pathfinding_iterations']} итераций):")
            print(f"  Среднее: {self.results['pathfinding_avg_ms']:.3f} мс")
            print(f"  Минимум: {self.results['pathfinding_min_ms']:.3f} мс")
            print(f"  Максимум: {self.results['pathfinding_max_ms']:.3f} мс")
            print(f"  Общее: {self.results['pathfinding_total_ms']:.2f} мс")
            print()
        
        # Визуализация
        if "visualization_simple_ms" in self.results:
            print(f"Визуализация:")
            print(f"  Простая: {self.results['visualization_simple_ms']:.2f} мс")
        if "visualization_bb_ms" in self.results:
            if "visualization_simple_ms" not in self.results:
                print(f"Визуализация:")
            print(f"  Battle Brothers: {self.results['visualization_bb_ms']:.2f} мс")
        
        if "visualization_simple_ms" in self.results or "visualization_bb_ms" in self.results:
            print()
        
        # Память
        if "memory_current_kb" in self.results:
            print(f"Память:")
            print(f"  Текущая: {self.results['memory_current_kb']:.2f} KB")
            print(f"  Пиковая: {self.results['memory_peak_kb']:.2f} KB")
            print()
        
        # Оценка производительности
        self.print_performance_rating()
    
    def print_performance_rating(self):
        """Выводит оценку производительности"""
        print("=" * 60)
        print("ОЦЕНКА ПРОИЗВОДИТЕЛЬНОСТИ")
        print("=" * 60)
        print()
        
        ratings = []
        
        # Оценка pathfinding
        if "pathfinding_avg_ms" in self.results:
            avg = self.results["pathfinding_avg_ms"]
            if avg < 1:
                rating = "🟢 Отлично"
            elif avg < 5:
                rating = "🟢 Хорошо"
            elif avg < 10:
                rating = "🟡 Приемлемо"
            else:
                rating = "🔴 Медленно"
            print(f"Pathfinding: {rating} ({avg:.3f} мс)")
            ratings.append(("Pathfinding", rating, avg))
        
        # Оценка визуализации
        if "visualization_bb_ms" in self.results:
            bb_time = self.results["visualization_bb_ms"]
            if bb_time < 40:
                rating = "🟢 Отлично"
            elif bb_time < 80:
                rating = "🟢 Хорошо"
            elif bb_time < 150:
                rating = "🟡 Приемлемо"
            else:
                rating = "🔴 Медленно"
            print(f"Визуализация: {rating} ({bb_time:.2f} мс)")
            ratings.append(("Визуализация", rating, bb_time))
        elif "visualization_simple_ms" in self.results:
            simple_time = self.results["visualization_simple_ms"]
            if simple_time < 20:
                rating = "🟢 Отлично"
            elif simple_time < 40:
                rating = "🟢 Хорошо"
            elif simple_time < 80:
                rating = "🟡 Приемлемо"
            else:
                rating = "🔴 Медленно"
            print(f"Визуализация: {rating} ({simple_time:.2f} мс)")
            ratings.append(("Визуализация", rating, simple_time))
        
        # Оценка генерации/загрузки
        if "map_generation_time_ms" in self.results:
            gen_time = self.results["map_generation_time_ms"]
            if gen_time < 200:
                rating = "🟢 Отлично"
            elif gen_time < 500:
                rating = "🟢 Хорошо"
            elif gen_time < 1500:
                rating = "🟡 Приемлемо"
            else:
                rating = "🔴 Медленно"
            print(f"Генерация карты: {rating} ({gen_time:.2f} мс)")
            ratings.append(("Генерация", rating, gen_time))
        elif "map_load_time_ms" in self.results:
            load_time = self.results["map_load_time_ms"]
            if load_time < 50:
                rating = "🟢 Отлично"
            elif load_time < 100:
                rating = "🟢 Хорошо"
            elif load_time < 200:
                rating = "🟡 Приемлемо"
            else:
                rating = "🔴 Медленно"
            print(f"Загрузка карты: {rating} ({load_time:.2f} мс)")
            ratings.append(("Загрузка", rating, load_time))
        
        print()
        print("=" * 60)
    
    def save_results(self, filename: str = None):
        """Сохраняет результаты в JSON файл"""
        if filename is None:
            filename = self.output_file
        results_with_meta = {
            "timestamp": datetime.now().isoformat(),
            "results": self.results
        }
        
        results_file = Path(filename)
        all_results = []
        
        # Загружаем существующие результаты, если есть
        if results_file.exists():
            try:
                with open(results_file, 'r', encoding='utf-8') as f:
                    all_results = json.load(f)
            except:
                all_results = []
        
        # Добавляем новые результаты
        all_results.append(results_with_meta)
        
        # Сохраняем (оставляем только последние 10 результатов)
        all_results = all_results[-10:]
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Результаты сохранены в {filename}")
        print()


def main():
    """Главная функция"""
    import argparse
    
    # Устанавливаем UTF-8 для вывода
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    parser = argparse.ArgumentParser(description="Benchmark производительности игры")
    parser.add_argument(
        "--generate",
        action="store_true",
        help="Генерировать новую карту вместо загрузки"
    )
    parser.add_argument(
        "--no-viz",
        action="store_true",
        help="Не тестировать визуализацию (быстрее)"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=100,
        help="Количество итераций pathfinding (по умолчанию: 100)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="scripts/benchmark_results.json",
        help="Файл для сохранения результатов (по умолчанию: scripts/benchmark_results.json)"
    )
    
    args = parser.parse_args()
    
    # Запускаем бенчмарк
    benchmark = PerformanceBenchmark()
    # Сохраняем количество итераций для pathfinding
    benchmark.pathfinding_iterations = args.iterations
    benchmark.output_file = args.output
    benchmark.run_all_tests(
        generate_new=args.generate,
        test_visualization=not args.no_viz
    )


if __name__ == "__main__":
    main()
