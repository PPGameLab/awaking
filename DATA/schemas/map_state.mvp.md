# MapState (MVP DATA)

## 1) Идентификаторы

- **NodeId**
- **EdgeId**
- **MapEntityId**
- **POIId**

---

## 2) Graph

**Node**
- `id`: NodeId

*Инцидентные рёбра узла выводятся из Edge по полям a/b. При необходимости индекс по узлам можно строить на уровне MapGraph при загрузке.*

**Edge**
- `id`: EdgeId
- `a`: NodeId
- `b`: NodeId
- `length`: float (топологическая длина; не геометрия)

**MapGraph**
- `nodesById`: Dictionary<NodeId, Node>
- `edgesById`: Dictionary<EdgeId, Edge>

*length нужен для дистанции по графу. Даже если не "км", это вес ребра.*

---

## 3) POI Anchors (POI не сущность)

**POIAnchor**
- `id`: POIId
- `kind`: string|enum (тип POI — город/лагерь/руины…; можно строкой в MVP)
- `anchor`: POIAnchorRef

**POIAnchorRef** (одно из)
- `NodeAnchor` { `nodeId`: NodeId }
- `AreaAnchor` { `nodeIds`: NodeId[] } (минимальный MVP-вариант "области" без геометрии)

**POIIndex**
- `poisById`: Dictionary<POIId, POIAnchor>
- `poiIdsByNodeId`: Dictionary<NodeId, POIId[]> (ускоритель событий входа/выхода)

*poiIdsByNodeId включает: POI с NodeAnchor(nodeId); POI с AreaAnchor, содержащим данный nodeId. Закрывает вопросы при обнаружении/входе/выходе.*

*POI привязана к узлу/области, несколько POI на одном узле — покрыто.*

---

## 4) EntitiesOnMap (только зарегистрированные)

**MapEntity**
- `id`: MapEntityId
- `controllerId`: string (или отдельный ControllerId при необходимости)
- `status`: MapEntityStatus (Idle | Moving | Engaged | Disabled)
- `position`: MapPosition
- `isMovement`: bool — true когда status === Moving
- `movement`: MovementState (валидно при isMovement === true)

*Инвариант: isMovement === (status === Moving). Дублирование осознанное: быстрые проверки, проще сериализация, удобно для ECS.*
- `isDetectionProfile`: bool — true когда задан профиль для правил обнаружения (детали позже)
- `detectionProfile`: DetectionProfile (валидно при isDetectionProfile === true)

**MapEntityStatus** (MVP)
- **Idle**
- **Moving**
- **Engaged**
- **Disabled**

---

## 5) Position (только топология)

**MapPosition** (одно из)
- `AtNode` { `nodeId`: NodeId }
- `OnEdge` { `edgeId`: EdgeId, `progress`: float } (0..1)

*Любая текущая позиция — допустимая точка продолжения движения.*

*Инвариант: если position имеет вид OnEdge, то position.edgeId === movement.edgeId обязательно (при isMovement === true).*

---

## 6) MovementState (минимум для исполнения движения картой)

**MovementState**
- `edgeId`: EdgeId
- `direction`: EdgeDirection (A→B или B→A)
- `speed`: float (∆progress per tick; знак не нужен, знак = direction)
- `isRoute`: bool — true когда движение по маршруту (иначе ручное)
- `route`: Route (валидно при isRoute === true)
- `isTarget`: bool — true когда цель контролёра задана
- `target`: Target (валидно при isTarget === true)
- `isStartedAtTick`: bool — true для диагностики (опционально)
- `startedAtTick`: long (валидно при isStartedAtTick === true)

**EdgeDirection**
- AtoB
- BtoA

---

## 7) Target (часть намерения; карта хранит активную цель движения)

**Target** (MVP) (одно из)
- `TargetNode` { `nodeId`: NodeId }
- `TargetEntity` { `entityId`: MapEntityId }
- `TargetPOI` { `poiId`: POIId }

---

## 8) Route (строит карта, валиден от текущей позиции)

**Route**
- `nodes`: NodeId[] (последовательность узлов) — **источник истины**
- `edges`: EdgeId[] (параллельная последовательность рёбер; производное от nodes)
- `validFrom`: MapPosition (позиция, откуда построен; для инвалидирования)

*Route.edges — производное представление маршрута. Источник истины — Route.nodes.*

*На ребре допускается только выбор направления — проверяется логикой; DATA форму поддерживает.*

---

## 9) MapState (итоговый контейнер)

**MapState**
- `tick`: long (время карты в тиках)
- `graph`: MapGraph
- `pois`: POIIndex
- `entitiesById`: Dictionary<MapEntityId, MapEntity>
