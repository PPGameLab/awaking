# Awaking - Фэнтези стратегия

Игра в жанре гибрид стратегии и тактики, ориентированная на Battle Brothers и Mount & Blade.

## Текущее состояние

**Статус:** В разработке MVP

**Готовность:** ~80% (определены все критичные механики)

## Структура проекта

```
awaking/
├── data/              # JSON данные (лор, механики)
│   └── maps/         # Данные карт (координаты, структура)
├── assets/            # Ресурсы игры
│   └── maps/         # Графические ресурсы для карты
├── src/               # Исходный код
│   ├── core/         # Ядро игры
│   ├── entities/     # Сущности (юниты, узлы)
│   ├── mechanics/    # Механики (экономика, бой)
│   └── utils/        # Утилиты
│       └── map_loader.py  # Загрузчик карт из файлов
├── scripts/          # Скрипты для запуска
│   ├── benchmark_performance.py  # Тест производительности
│   ├── visualize_map.py         # Визуализация карты
│   ├── visualize_map_bb.py      # Визуализация в стиле Battle Brothers
│   └── visualize_map_interactive.py  # Интерактивная визуализация
├── docs/             # Документация
│   ├── MAP_DATA_STRUCTURE.md    # Структура данных карты
│   └── ...           # Другая документация
├── questions/        # Вопросы и обсуждения
└── tests/            # Тесты
```

### Данные карты

- **`data/maps/`** - JSON файлы с данными карт:
  - `simple_map.json` - простая тестовая карта (3 узла)
  - `map_coordinates.json` - координаты столиц и центра для генерации
  - `generated_map.json` - сгенерированная карта (автоматически)
- **`assets/maps/`** - графические ресурсы (иконки, текстуры)
- **`src/utils/map_loader.py`** - загрузчик карт из файлов

## Установка

```bash
pip install -r requirements.txt
```

## Запуск

### Основные команды:

```bash
# Запуск игры (pygame версия)
python main_pygame.py

# Запуск игры (старая версия)
python main.py

# Генерация карты
python generate_map.py

# Визуализация карты
python scripts/visualize_map.py
python scripts/visualize_map_bb.py  # Battle Brothers стиль
python scripts/visualize_map_interactive.py  # Интерактивная

# Статическая карта (world_v1)
python scripts/view_map.py world_v1  # Просмотр карты
python scripts/view_map.py world_v1 --validate  # Валидация
python scripts/view_map.py world_v1 --interactive  # Интерактивный режим
python scripts/view_map.py world_v1 --export map.png  # Экспорт изображения
python scripts/convert_map.py simple_map  # Конвертация из старого формата

# Тест производительности
python scripts/benchmark_performance.py
```

### Управление в pygame версии:

- **Пробел** - Пауза
- **+/-** - Ускорение/замедление времени
- **R** - Сброс скорости
- **ЛКМ** - Выбрать узел/Установить цель движения
- **Колесо мыши** - Масштаб
- **ESC** - Выход

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
