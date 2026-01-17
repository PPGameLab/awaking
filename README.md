# Awaking - Фэнтези стратегия

Игра в жанре гибрид стратегии и тактики, ориентированная на Battle Brothers и Mount & Blade.

## Текущее состояние

**Статус:** В разработке MVP

**Готовность:** ~80% (определены все критичные механики)

## Структура проекта

```
awaking/
├── data/              # JSON данные (лор, механики)
├── src/               # Исходный код
│   ├── core/         # Ядро игры
│   ├── entities/     # Сущности (юниты, узлы)
│   ├── mechanics/    # Механики (экономика, бой)
│   └── utils/        # Утилиты
├── scripts/          # Скрипты для запуска
│   ├── benchmark_performance.py  # Тест производительности
│   ├── visualize_map.py         # Визуализация карты
│   ├── visualize_map_bb.py      # Визуализация в стиле Battle Brothers
│   └── visualize_map_interactive.py  # Интерактивная визуализация
├── docs/             # Документация
│   ├── DEVELOPMENT_PLAN.md
│   ├── MVP_STATUS.md
│   └── ...           # Другая документация
├── questions/        # Вопросы и обсуждения
└── tests/            # Тесты
```

## Установка

```bash
pip install -r requirements.txt
```

## Запуск

### Основные команды:

```bash
# Запуск игры
python main.py

# Генерация карты
python generate_map.py

# Визуализация карты
python scripts/visualize_map.py
python scripts/visualize_map_bb.py  # Battle Brothers стиль
python scripts/visualize_map_interactive.py  # Интерактивная

# Тест производительности
python scripts/benchmark_performance.py
```

## Основные механики

- **Карта:** Узловая система, 8 королевств по кругу + Центр
- **Юниты:** Отряды 1-50 человек
- **Бой:** Пошаговый, гексагональная карта (MVP: автоматически)
- **Время:** Непрерывное с тиками, календарь (дни/недели)
- **Экономика:** Специализированные узлы, календарное обновление
- **Прогрессия:** Развитие персонажа, отряда, захват узлов

## Документация

- `docs/MVP_STATUS.md` - статус разработки MVP
- `docs/DEVELOPMENT_PLAN.md` - план разработки
- `questions/mvp_global.md` - глобальные вопросы
- `data/` - JSON файлы с данными игры

Полная документация находится в папке `docs/`.

## Git Commit Guidelines

**Коммиты должны быть:**
- На английском языке (латиница)
- Кратко и лаконично
- Описывать суть изменений

**Примеры:**
- ✅ `Add map generation script`
- ✅ `Fix pathfinding performance`
- ✅ `Organize project structure`
- ❌ `Организация структуры проекта: перемещение документации...`
