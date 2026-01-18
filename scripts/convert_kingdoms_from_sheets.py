"""
Конвертер данных королевств из Google Sheets в JSON формат
Поддерживает экспорт CSV из Google Sheets
"""
import sys
import io
import csv
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional

# Устанавливаем UTF-8 для вывода
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Добавляем корень проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def parse_kingdoms_csv(csv_path: Path) -> Dict:
    """Парсит CSV файл из Google Sheets и конвертирует в структуру королевств"""
    
    kingdoms = {}
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Определяем колонки (1-8 для королевств)
        kingdom_columns = [f"{i}" for i in range(1, 9)]
        
        # Читаем все строки
        rows = list(reader)
        
        # Находим блоки
        current_block = None
        block_data = {}
        
        for row in rows:
            field = row.get("Поле", "").strip()
            if not field:
                continue
            
            # Определяем блок
            if "БЛОК 1" in field or "ИДЕНТИФИКАЦИЯ" in field:
                current_block = "identification"
            elif "БЛОК 2" in field or "ВЕРА" in field:
                current_block = "belief"
            elif "БЛОК 3" in field or "БИОЛОГИЯ" in field:
                current_block = "biology"
            elif "БЛОК 4" in field or "МАГИЯ" in field:
                current_block = "magic"
            elif "БЛОК 5" in field or "ОБЩЕСТВО" in field:
                current_block = "society"
            elif "БЛОК 6" in field or "ВОЙНА" in field:
                current_block = "military"
            elif "БЛОК 7" in field or "ЭКОНОМИКА" in field:
                current_block = "economy"
            elif "БЛОК 8" in field or "СРЕДА" in field:
                current_block = "geography"
            elif "БЛОК 9" in field or "ВИЗУАЛ" in field:
                current_block = "visual"
            elif "БЛОК 10" in field or "ИГРОВОЙ" in field:
                current_block = "gameplay"
            elif "БЛОК 11" in field or "МЕТА" in field:
                current_block = "meta"
            else:
                # Это поле данных
                if current_block:
                    for col in kingdom_columns:
                        value = row.get(col, "").strip()
                        if value:
                            kingdom_id = None
                            
                            # Определяем ID королевства из первой строки
                            if field.lower() == "id":
                                kingdom_id = value
                                if kingdom_id not in kingdoms:
                                    kingdoms[kingdom_id] = {}
                            
                            # Сохраняем данные
                            if kingdom_id:
                                if current_block not in kingdoms[kingdom_id]:
                                    kingdoms[kingdom_id][current_block] = {}
                                
                                # Нормализуем имя поля
                                field_key = field.lower().replace(" ", "_").replace("/", "_")
                                kingdoms[kingdom_id][current_block][field_key] = value
    
    return kingdoms


def convert_to_entities_format(kingdoms: Dict) -> Dict:
    """Конвертирует структуру в формат entities.owners"""
    
    entities_owners = {}
    
    for kingdom_id, data in kingdoms.items():
        entity = {
            "name": data.get("identification", {}).get("название", kingdom_id),
            "theme": data.get("identification", {}).get("тема_/_архетип", ""),
            "location": data.get("identification", {}).get("расположение", "")
        }
        
        # Биология
        if "biology" in data:
            bio = data["biology"]
            entity["biology"] = {
                "physical_features": bio.get("физические_особенности", ""),
                "genetic_mutations": bio.get("генетические_мутации", ""),
                "magic_predisposition": bio.get("предрасположенность_к_магии", ""),
                "body_attitude": bio.get("отношение_к_телу", ""),
                "primary_attribute": bio.get("почитаемая_характеристика", "").lower() if bio.get("почитаемая_характеристика") else None
            }
        
        # Магия
        if "magic" in data:
            magic = data["magic"]
            entity["magic"] = {
                "tradition": magic.get("магическая_традиция", ""),
                "predisposition": magic.get("магическая_предрасположенность", "")
            }
        
        # Общество
        if "society" in data:
            soc = data["society"]
            entity["society"] = {
                "government": soc.get("тип_правительства", ""),
                "structure": soc.get("структура_общества", ""),
                "elite": soc.get("правящая_элита", ""),
                "laws": soc.get("законы", ""),
                "guilds": soc.get("гильдии_/_ордена", ""),
                "foreigners_attitude": soc.get("отношение_к_иноверцам", "")
            }
        
        # Военное
        if "military" in data:
            mil = data["military"]
            entity["military"] = {
                "doctrine": mil.get("военная_доктрина", ""),
                "typical_troops": [t.strip() for t in mil.get("типичные_войска", "").split(",") if t.strip()],
                "typical_enemies": [e.strip() for e in mil.get("типичные_враги", "").split(",") if e.strip()],
                "internal_conflicts": [c.strip() for c in mil.get("внутренние_конфликты", "").split(",") if c.strip()],
                "threat_level": mil.get("степень_угрозы_миру", "")
            }
        
        # Экономика
        if "economy" in data:
            econ = data["economy"]
            entity["economy"] = {
                "type": econ.get("экономика", ""),
                "unique_resources": [r.strip() for r in econ.get("уникальные_ресурсы", "").split(",") if r.strip()],
                "exports": [e.strip() for e in econ.get("экспорт", "").split(",") if e.strip()],
                "imports": [i.strip() for i in econ.get("импорт", "").split(",") if i.strip()],
                "crafts": [c.strip() for c in econ.get("основные_ремёсла", "").split(",") if c.strip()]
            }
        
        # География
        if "geography" in data:
            geo = data["geography"]
            entity["geography"] = {
                "terrain": geo.get("география", ""),
                "climate": geo.get("климат", ""),
                "daily_life": geo.get("повседневная_жизнь", ""),
                "settlements": geo.get("поселения", ""),
                "transport": geo.get("транспорт", "")
            }
        
        # Визуал
        if "visual" in data:
            vis = data["visual"]
            colors_str = vis.get("цвета", "")
            colors = [c.strip() for c in colors_str.split(",") if c.strip()] if colors_str else []
            
            entity["visual"] = {
                "appearance": vis.get("внешний_образ", ""),
                "architecture": vis.get("архитектура", ""),
                "colors": colors,
                "symbols": [s.strip() for s in vis.get("символы", "").split(",") if s.strip()],
                "heraldry": vis.get("геральдика", "")
            }
        
        entities_owners[kingdom_id] = entity
    
    return entities_owners


def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(description="Convert kingdoms from Google Sheets CSV to JSON")
    parser.add_argument("csv_file", help="CSV file exported from Google Sheets")
    parser.add_argument("--output", "-o", help="Output JSON file (default: data/kingdoms_from_sheets.json)")
    parser.add_argument("--update-world", action="store_true", help="Update world_v1.json entities.owners")
    
    args = parser.parse_args()
    
    csv_path = Path(args.csv_file)
    if not csv_path.exists():
        print(f"Error: CSV file not found: {csv_path}")
        sys.exit(1)
    
    # Парсим CSV
    print(f"Parsing CSV: {csv_path}")
    kingdoms = parse_kingdoms_csv(csv_path)
    
    if not kingdoms:
        print("Warning: No kingdoms found in CSV")
        sys.exit(1)
    
    # Конвертируем в формат entities
    entities_owners = convert_to_entities_format(kingdoms)
    
    # Сохраняем
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = project_root / "data" / "kingdoms_from_sheets.json"
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    result = {
        "version": "1.0",
        "source": "Google Sheets",
        "entities": {
            "owners": entities_owners
        }
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Converted {len(entities_owners)} kingdoms")
    print(f"Output: {output_path}")
    
    # Обновляем world_v1.json если нужно
    if args.update_world:
        world_path = project_root / "data" / "maps" / "world_v1.json"
        if world_path.exists():
            with open(world_path, 'r', encoding='utf-8') as f:
                world_data = json.load(f)
            
            # Обновляем entities.owners
            if "entities" not in world_data["metadata"]:
                world_data["metadata"]["entities"] = {}
            world_data["metadata"]["entities"]["owners"] = entities_owners
            
            with open(world_path, 'w', encoding='utf-8') as f:
                json.dump(world_data, f, ensure_ascii=False, indent=2)
            
            print(f"Updated: {world_path}")


if __name__ == "__main__":
    main()
