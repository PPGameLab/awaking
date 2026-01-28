# План реструктуризации: LORE / DATA / GAME

**Цель:** Три основные папки + шесть файлов в корне.

---

## Целевая структура корня

```
awaking/
├── LORE/           # Мир, канон, черновики, вопросы, дизайн
├── DATA/            # Все данные: карты, механики, конфиги, источники
├── GAME/            # Код, ассеты, скрипты, точки входа
├── LORE.md          # Вход в лор: что в LORE/, как работать
├── DATA.md          # Вход в данные: схемы, источники
├── GAME.md          # Как запускать, структура кода
├── WORKFLOW.md      # Git, коммиты, инструменты
├── WORLD_SNAPSHOT.md # Снимок состояния мира/проекта
├── README.md        # Обзор проекта, ссылки на остальное
├── .gitignore
└── (при необходимости) uwuking.map → DATA/
```

---

## Назначение папок

| Папка | Содержимое |
|-------|------------|
| **LORE** | Мир, канон, черновики, глоссарий, таблицы, дизайн-спеки, вопросы по миру и дизайну |
| **DATA** | Карты (maps), игровые механики (*.mvp.json), конфиги, исходники карт (uwuking.map), схемы и планы по данным |
| **GAME** | Исходный код (src), ассеты, скрипты, main*.py, generate_map.py, requirements.txt, тесты, техдокументация |

---

## Перенос: текущее → целевое

### → LORE/
- `lore/*` → `LORE/` (canon, drafts, glossary, meta, tables)
- `design/*` → `LORE/design/`
- `questions/*` → `LORE/questions/`
- Из `docs/`: `KINGDOMS_TABLE_ANALYSIS.md`, `KINGDOMS_TABLE_STRUCTURE.md`, `AZGAAR_MAP_PROMPT.md` → `LORE/docs/`

### → DATA/
- `data/maps/*` → `DATA/maps/`
- `data/README.md` → `DATA/` (или объединить с DATA.md)
- `game_data/*` → `DATA/` (mvp.json и README в корень DATA/)
- `uwuking.map` → `DATA/uwuking.map`
- Из `docs/`: `MAP_DATA_STRUCTURE.md`, `MAP_ENTITIES_PROPERTIES.md`, `STATIC_MAP_IMPLEMENTATION_PLAN.md` → `DATA/docs/`

### → GAME/
- `src/*` → `GAME/src/`
- `assets/*` → `GAME/assets/`
- `scripts/*` → `GAME/scripts/`
- `main.py`, `main_pygame.py`, `generate_map.py`, `requirements.txt` → `GAME/`
- `tests/` → `GAME/tests/` (если есть)
- Остальные `docs/*` → `GAME/docs/` (AUDIT, ARCHITECTURE, BATTLE_BROTHERS, MOVEMENT_AND_ENCOUNTERS, PROJECT_KNOWLEDGE_BASE, PROJECT_STRUCTURE, AI_WORKFLOW_GUIDE, BENCHMARK_README, DEPRECATED_DOCUMENTS)

---

## Корневые .md

| Файл | Назначение |
|------|------------|
| **README.md** | Название, статус, структура (LORE / DATA / GAME), ссылки на LORE.md, DATA.md, GAME.md, WORKFLOW.md |
| **LORE.md** | Что лежит в LORE/, правила (canon/draft), ссылки на ключевые документы |
| **DATA.md** | Что лежит в DATA/, схемы (карты, mechanics), источники (Azgaar, Sheets), ссылки на docs |
| **GAME.md** | Как запускать (python из GAME/), структура GAME/, зависимости, команды |
| **WORKFLOW.md** | Git, коммиты (EN, кратко), скрипты/инструменты, цикл работы |
| **WORLD_SNAPSHOT.md** | Краткий снимок состояния мира/проекта (канон, границы, ключевые решения) |

---

## Что обновить после переноса

1. **Пути в коде:** `data/maps/` → `DATA/maps/`, `game_data/` → `DATA/` (или сохранить алиасы через константы).
2. **Точка входа:** запуск из корня, напр. `python GAME/main_pygame.py`, и в коде пути от корня репо: `DATA/maps/`, `DATA/attributes.mvp.json`.
3. **Импорты:** если что-то импортирует из `data/` или `game_data/`, обновить на `DATA/`.
4. **.gitignore:** при необходимости добавить `DATA/generated_map.json` и т.п., если пути меняются.
5. **README.md, LORE.md, DATA.md, GAME.md, WORKFLOW.md, WORLD_SNAPSHOT.md** — заполнить по назначению выше.

---

*После выполнения переносов этот план можно перенести в GAME/docs/ или удалить.*
