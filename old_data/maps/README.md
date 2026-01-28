# Данные карт

Эта папка содержит данные для карт игры.

## Структура

```
data/maps/
├── simple_map.json          # Простая тестовая карта (3 узла)
├── map_coordinates.json     # Координаты для генерации карты
├── generated_map.json       # Сгенерированная карта (будет перемещена сюда)
└── README.md
```

## Файлы

### `simple_map.json`
Простая тестовая карта с 3 узлами треугольником. Используется для тестирования pygame.

### `map_coordinates.json`
Координаты столиц королевств и центра. Используется для генерации карты.

### `generated_map.json`
Сгенерированная карта (будет перемещена из `data/generated_map.json`).

## Формат файлов

### Формат карты:
```json
{
  "metadata": {
    "version": "1.0",
    "name": "Название карты",
    "description": "Описание"
  },
  "nodes": [
    {
      "id": "Node1",
      "name": "Узел 1",
      "pos": [400.0, 300.0],
      "node_type": "City",
      "kingdom": "Test",
      "role": "City"
    }
  ],
  "edges": [
    ["Node1", "Node2"]
  ]
}
```

### Формат координат:
```json
{
  "center": {
    "pos": [500.0, 500.0]
  },
  "capitals": {
    "KingdomID": {
      "name": "Название",
      "pos": [x, y]
    }
  },
  "ring_order": ["Kingdom1", "Kingdom2", ...]
}
```

## Использование

Карты загружаются через `MapLoader`:
```python
from src.utils.map_loader import MapLoader

loader = MapLoader()
nodes, edges, metadata = loader.load_map("simple_map")
```

Координаты загружаются через `MapLoader`:
```python
coords = loader.load_coordinates()
```
