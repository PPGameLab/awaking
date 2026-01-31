# MapTickResult / MapEvents (MVP DATA)

## 1) Общий принцип

Карта обрабатывает один тик и возвращает список фактов (MapEvent[]).

Карта не принимает решений и не исполняет внешние процессы.

Все события в MapEvent[] относятся к конкретному tick.

---

## 2) MapTickResult

**MapTickResult**
- `tick`: long
- `events`: MapEvent[]

---

## 3) MapEvent (union)

**MapEvent** (одно из)
- EncounterEvent
- DetectionEvent
- POIEvent
- RouteEvent
- TargetEvent
- EntityEvent

*POIEvent здесь — пространственные факты (вошёл/вышел/достиг якоря), а не "внутренние события POI".*

---

## 4) EncounterEvent (встреча)

**EncounterEvent**
- `type`: "Encounter"
- `tick`: long
- `a`: MapEntityId
- `b`: MapEntityId
- `location`: EncounterLocation
- `kind`: EncounterKind

**EncounterLocation** (одно из)
- `AtNode` { `nodeId`: NodeId }
- `OnEdge` { `edgeId`: EdgeId, `progress`: float } (0..1)

**EncounterKind** (MVP)
- SameNode
- SameEdgeProgress

---

## 5) DetectionEvent (обнаружение)

**DetectionEvent**
- `type`: "Detection"
- `tick`: long
- `spotterId`: MapEntityId
- `target`: DetectionTarget
- `kind`: DetectionKind
- `distance`: float (топологическая дистанция; единицы = length графа)
- `isAsymmetric`: bool (true если срабатывание одностороннее по правилам)
- `isRuleId`: bool
- `ruleId`: string (валидно при isRuleId === true; ID правила/профиля для логов)

**DetectionTarget** (одно из)
- `EntityTarget` { `entityId`: MapEntityId }
- `POITarget` { `poiId`: POIId }

**DetectionKind** (MVP)
- EntityDetected
- POIEnteredZone
- POIExitedZone

*distance — для дебага/аналитики; карта не интерпретирует его как решение.*

---

## 6) POIEvent (пространственные факты, связанные с POI)

**POIEvent**
- `type`: "POI"
- `tick`: long
- `entityId`: MapEntityId
- `poiId`: POIId
- `kind`: POIEventKind
- `anchor`: POIAnchorRef

**POIEventKind** (MVP)
- ReachedAnchor
- EnteredPOI (после этого сущность дерегистрируется)
- ExitedPOI (после этого сущность регистрируется)

*EnteredPOI/ExitedPOI — факт смены присутствия на карте, не "что происходит внутри POI".*

---

## 7) RouteEvent (маршрут)

**RouteEvent**
- `type`: "Route"
- `tick`: long
- `entityId`: MapEntityId
- `kind`: RouteEventKind
- `isReason`: bool
- `reason`: RouteEventReason (валидно при isReason === true)

**RouteEventKind** (MVP)
- Built
- Invalidated

**RouteEventReason** (MVP)
- GraphDisconnected
- RouteNoLongerValidFromPosition
- TargetMissing
- POIAnchorMissing
- EntityNotOnMap
- Other

---

## 8) TargetEvent (цель недостижима / потеряна)

**TargetEvent**
- `type`: "Target"
- `tick`: long
- `entityId`: MapEntityId
- `target`: Target
- `kind`: TargetEventKind
- `isReason`: bool
- `reason`: TargetEventReason (валидно при isReason === true)

**TargetEventKind** (MVP)
- Unreachable
- Lost

**TargetEventReason** (MVP)
- NoPath
- TargetMissing
- POIAnchorMissing
- EntityNotOnMap
- Other

---

## 9) EntityEvent (регистрация / дерегистрация / смена статуса)

**EntityEvent**
- `type`: "Entity"
- `tick`: long
- `entityId`: MapEntityId
- `kind`: EntityEventKind
- `isFromStatus`: bool
- `fromStatus`: MapEntityStatus (валидно при isFromStatus === true)
- `isToStatus`: bool
- `toStatus`: MapEntityStatus (валидно при isToStatus === true)
- `isPosition`: bool
- `position`: MapPosition (валидно при isPosition === true)
- `isPOI`: bool
- `poiId`: POIId (валидно при isPOI === true)

**EntityEventKind** (MVP)
- Registered
- Deregistered
- StatusChanged
- PositionChanged

*Карта может эмитить EntityEvent(kind=PositionChanged, isPosition=true, position=...) при изменении позиции сущности (в т.ч. достижение узла).*

*Здесь же фиксируется "движение остановлено и статус стал Idle/Engaged/Disabled" — без отдельного MovementResult.*

---

## 10) Инварианты (MVP, текстом)

- Каждый MapEvent.tick равен MapTickResult.tick.
- EncounterEvent приводит к остановке движения у участников и переводу в устойчивое состояние (обычно Engaged); бой не часть карты.
- POIEvent.EnteredPOI ⇒ сущность после тика отсутствует в entitiesById.
- POIEvent.ExitedPOI ⇒ сущность после тика присутствует в entitiesById.
- RouteEvent.Invalidated и TargetEvent.Unreachable ⇒ карта прекращает движение сущности и уведомляет контролёр через события.
