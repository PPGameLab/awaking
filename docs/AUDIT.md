# Аудит файлов проекта

**Дата:** 2025-01-25  
**Цель:** Классификация всех файлов проекта по категориям

---

## Категории

- **runtime** — игра читает прямо сейчас
- **lore** — мир/термины/канон
- **spec** — планы/обсуждения/архитектура, не обязательно читается игрой
- **tools** — dev tooling и data pipeline (генерируют/валидируют runtime данные)
- **trash/legacy** — устарело, но пока не удаляем

---

## 📁 runtime

### Исходный код (`src/`)
```
src/
├── __init__.py                    [runtime]
├── core/
│   ├── __init__.py                [runtime]
│   ├── game.py                    [runtime]
│   ├── time.py                    [runtime]
│   └── world.py                   [runtime]
├── entities/
│   ├── __init__.py                [runtime]
│   ├── node.py                    [runtime]
│   └── unit.py                    [runtime]
├── mechanics/
│   └── __init__.py                [runtime]
├── ui/
│   ├── __init__.py                [runtime]
│   ├── game_window.py             [runtime]
│   └── map_renderer.py           [runtime]
└── utils/
    ├── __init__.py                [runtime]
    ├── loader.py                  [runtime]
    ├── map_data.py                [runtime]
    ├── map_generator.py           [runtime]
    ├── map_loader.py              [runtime]
    ├── map_storage.py             [runtime]
    ├── map_visualizer_bb.py       [runtime]
    ├── map_visualizer_interactive.py [runtime]
    └── map_visualizer.py          [runtime]
```

### Точки входа
```
main.py                            [runtime]
main_pygame.py                     [runtime]
```

### Runtime данные (`game_data/`)
```
game_data/
├── README.md                      [spec] (документация, не спека системы)
├── attributes.mvp.json            [runtime]
├── game_mechanics.mvp.json       [runtime]
├── magic_system.mvp.json          [runtime]
├── map_config.mvp.json            [runtime]
└── map_structure.mvp.json         [runtime]
```

### Статические карты (`data/maps/`)
```
data/maps/
├── README.md                      [spec]
├── map_coordinates.json           [runtime]
├── simple_map.json                [runtime]
└── world_v1.json                  [runtime]
```

### Зависимости
```
requirements.txt                   [runtime]
```

---

## 📚 lore

### Канон (`lore/canon/`)
```
lore/canon/
└── README.md                      [lore]
```

### Глоссарий (`lore/glossary/`)
```
lore/glossary/
├── README.md                      [lore]
└── TEMPLATE.md                    [lore]
```

### Таблицы (`lore/tables/`)
```
lore/tables/
└── README.md                      [lore]
```

### Метаданные (`lore/meta/`)
```
lore/meta/
├── README.md                      [lore]
├── RULES.md                       [lore]
└── STRUCTURE_PLAN.md              [lore]
```

### Черновики (`lore/drafts/`)
```
lore/drafts/
└── README.md                      [lore]
```

---

## 📋 spec

**Примечание:** README файлы в runtime-папках — это документация (spec), но не "спеки систем".  
Спеки систем находятся в `design/`, а README описывают структуру и использование.

### Документация (`docs/`)
```
docs/
├── AI_WORKFLOW_GUIDE.md           [spec]
├── ARCHITECTURE_ANALYSIS.md        [spec]
├── AZGAAR_MAP_PROMPT.md           [spec]
├── AUDIT.md                       [spec] (этот файл)
├── BATTLE_BROTHERS_FEASIBILITY.md [spec]
├── BENCHMARK_README.md            [spec]
├── DEPRECATED_DOCUMENTS.md        [spec]
├── KINGDOMS_TABLE_ANALYSIS.md     [spec]
├── KINGDOMS_TABLE_STRUCTURE.md    [spec]
├── MAP_DATA_STRUCTURE.md          [spec]
├── MAP_ENTITIES_PROPERTIES.md     [spec]
├── MOVEMENT_AND_ENCOUNTERS.md     [spec]
├── PROJECT_KNOWLEDGE_BASE.md      [spec]
├── PROJECT_STRUCTURE.md           [spec]
└── STATIC_MAP_IMPLEMENTATION_PLAN.md [spec]
```

### Вопросы (`questions/`)
```
questions/
├── answered.md                    [spec]
├── mvp_global.md                 [spec]
├── open.md                       [spec]
├── questions.md                  [spec]
└── static_map_questions.md       [spec]
```

### Дизайн (`design/`)
```
design/
└── README.md                      [spec]
```

### Скрипты (`scripts/`)
```
scripts/
├── README.md                      [spec]
├── benchmark_performance.py       [tools]
├── benchmark_results.json         [tools]
├── convert_kingdoms_from_sheets.py [tools] (data pipeline)
├── convert_map.py                 [tools] (data pipeline)
├── test.py                        [tools]
├── view_map.py                    [tools] (data pipeline)
├── visualize_map_bb.py           [tools]
├── visualize_map_interactive.py   [tools]
└── visualize_map.py               [tools]
```

### Утилиты генерации
```
generate_map.py                    [tools] (data pipeline)
```

### README файлы
```
README.md                          [spec]
data/README.md                     [spec]
data/maps/README.md                [spec]
assets/maps/README.md              [spec]
game_data/README.md                [spec]
design/README.md                   [spec]
scripts/README.md                   [spec]
```

---

## 🗑️ trash/legacy

### Legacy лор (`lore/drafts/legacy/`)
```
lore/drafts/legacy/
├── glossary_legacy.json           [trash/legacy]
├── glossary_legacy.README.md      [trash/legacy]
├── KINGDOM_LORE_2026-01-19.md    [trash/legacy]
├── kingdoms_legacy.json           [trash/legacy]
├── kingdoms_legacy.README.md      [trash/legacy]
└── WORLD_LORE_legacy.md          [trash/legacy]
```

**Примечание:** Все legacy файлы находятся только в `lore/drafts/legacy/`.

### Сгенерированные файлы (gitignored, но существуют)
```
data/generated_map.json            [trash/legacy]
```

---

## 📊 Статистика

| Категория | Количество файлов |
|-----------|------------------|
| **runtime** | ~35 |
| **lore** | ~10 |
| **spec** | ~40 |
| **tools** | ~10 |
| **trash/legacy** | ~6 |
| **Всего** | ~101 |

---

## 🔍 Примечания

### Runtime файлы
- Все файлы в `src/` — код игры
- Все `.mvp.json` в `game_data/` — runtime данные
- Статические карты в `data/maps/` — загружаются игрой
- `requirements.txt` — зависимости для запуска

### Lore файлы
- Структура `lore/` организована по назначению
- Legacy файлы вынесены в `lore/drafts/legacy/`
- Метаданные и правила в `lore/meta/`

### Spec файлы
- Вся документация в `docs/` — планы и описания
- Вопросы в `questions/` — обсуждения
- README файлы — описания структуры (не "спеки систем", а документация)

### Tools файлы
- Dev tooling скрипты — визуализация, конвертация, бенчмарки
- Data pipeline скрипты — генерируют/валидируют runtime данные (критичны для поддержки)

### Legacy файлы
- Все файлы в `lore/drafts/legacy/` помечены как legacy
- Сгенерированные файлы (gitignored) — временные артефакты

---

## ✅ Рекомендации

1. **Runtime:** Все файлы на месте, структура правильная
2. **Lore:** Legacy файлы правильно вынесены в `lore/drafts/legacy/`, структура организована
3. **Spec:** Документация актуальна, вопросы структурированы
4. **Legacy:** Можно рассмотреть удаление после полного переноса данных

---

## 📌 Что ещё есть

- **`uwuking.map`** в корне проекта — исходная карта из [Azgaar's Fantasy Map Generator](https://azgaar.github.io/Fantasy-Map-Generator/), хранится здесь как источник для переноса в статическую карту (`data/maps/`). Не удалять.
- **Код загрузки:** `src/utils/loader.py` и др. — при добавлении загрузки механик из `game_data/` нужно указывать пути к `game_data/*.mvp.json` (часть уже использует `game_data/`, см. `map_generator.py`).

---

**Последнее обновление:** 2025-01-27
