# Контракт намерений контролёра (MVP)

## 1) Общий принцип

Контролёр принимает решения и формирует намерения (Intent).

Карта исполняет только пространственные процессы и возвращает MapEvent[].

Намерение считается выполненным/проваленным только через факты карты.

---

## 2) Владелец и адресация

- Каждая MapEntity управляется ровно одним активным controllerId.
- Все команды контролёрам адресуются по controllerId.
- В MVP у контролёра может быть много intent'ов, но активным считается один.
- **В MVP controllerId управляет ровно одной MapEntityId (1:1).** (Если позже будет "контролёр-отряд" — расширим.)

---

## 3) Состояния intent (FSM)

**IntentStatus** (MVP)
- Pending
- Active
- Succeeded
- Failed
- Cancelled

**IntentFailureReason** (MVP)
- TargetUnreachable
- RouteInvalidated
- TargetLost
- InterruptedByEncounter
- InterruptedByPOIEnter
- EntityNotOnMap
- Other

---

## 4) DATA: ControllerIntent

**ControllerIntent**
- `id`: string
- `kind`: IntentKind
- `policy`: IntentPolicy
- `isTarget`: bool
- `target`: Target (валидно при isTarget === true)
- `isSpeed`: bool
- `speed`: float (валидно при isSpeed === true; ∆progress per tick)
- `isTimeoutTicks`: bool
- `timeoutTicks`: long (валидно при isTimeoutTicks === true)
- `isMeta`: bool
- `meta`: Dictionary<string, string> (валидно при isMeta === true)

**IntentKind** (MVP)
- MoveToTarget
- Stop
- HoldPosition
- (опционально) EngageEntity

*Использование полей: isTarget — для MoveToTarget/EngageEntity = true, для Stop/HoldPosition = false. isSpeed — для MoveToTarget может быть true/false, для Stop/Hold обычно false.*

**IntentPolicy** (MVP)
- ReplaceActive
- Queue

*Queue: intent сохраняется в очереди контролёра и не применяется к карте, пока активный intent не завершён (Succeeded/Failed/Cancelled/timeout).*

*Полная форма ControllerIntent используется в ControllerCommand.PushIntent (см. simulation_scheduler.mvp.md).*

---

## 4a) IntentKind: семантика (MVP)

### MoveToTarget

**Зачем:** основное перемещение к цели (узел/POI/сущность).

**Успех:** по правилам §7 — Node → позиция AtNode; POI → POIEvent(ReachedAnchor); Entity → EncounterEvent с целью.

**Поля:** isTarget/target, isSpeed/speed, policy, timeoutTicks.

---

### Stop

**Зачем:** явная остановка движения без "магии". Нужна и игроку, и AI, и для реакций.

**Эффект при применении (внешний слой):** MapEntity.status = Idle, MapEntity.isMovement = false. movement может оставаться как структура, но считается невалидной при isMovement === false.

**Успех:** мгновенно на том же тике, где команда применена (контролёр переводит intent в Succeeded).

**Поля:** целевые не нужны (isTarget = false).

---

### HoldPosition

**Зачем:** "стоять и наблюдать" как устойчивое намерение (в отличие от Stop, которое одноразовое). Контролёр хочет, чтобы сущность оставалась в текущей позиции до отмены/события.

**Поведение:** сущность должна быть Idle (или Disabled — тогда intent должен fail/cancel по политике контролёра). Карта может генерировать DetectionEvent; встречи возможны, если кто-то придёт.

**Успех:** обычно не имеет "естественного успеха"; завершается Cancelled (заменили новым intent) или Failed (EntityNotOnMap, InterruptedByEncounter — на усмотрение).

**Поля:** timeoutTicks полезен; target не нужен.

---

### EngageEntity (опционально)

**Зачем:** отличать "просто двигайся к сущности" от "намеренно вступи в контакт". Упрощает логику контролёров/UI. Без него можно жить одним MoveToTarget(TargetEntity).

**Успех:** EncounterEvent с целью (как у Entity-цели); семантика намерения — "хочу контакт".

**Поля:** target обязателен, должен быть TargetEntity.

*Если цель исчезла/не на карте (TargetEvent.Lost, EntityNotOnMap), то EngageEntity → Failed(reason=TargetLost | EntityNotOnMap). MoveToTarget(TargetEntity) может быть интерпретирован контролёром мягче (перепланировать или ждать).*

*Рекомендация: добавлять только если MoveToTarget(Entity) начинает смешивать два смысла.*

---

## 4b) IntentKind не в MVP (отложено)

Пока не фиксировать в каноне:

- PatrolRoute (патрули, циклы)
- Flee / Evade
- FollowEntity
- InvestigatePOI
- EnterPOI / ExitPOI как intent (действие на якоре, не цель движения)
- Scout / Hide (модификаторы правил обнаружения, не intent карты)

---

## 4c) Рекомендованный MVP-профиль

**Минимум:** MoveToTarget, Stop, HoldPosition.

**Опционально:** EngageEntity — только если "MoveToTarget(Entity)" начинает смешивать два смысла.

---

## 5) Применение intent к карте (контролёр → внешний слой → карта)

### 5.1 PushIntent

Контролёр отправляет:
- **ControllerCommand.PushIntent**
- `controllerId`: string
- `intent`: ControllerIntent

### 5.2 MoveToTarget: применение к MapState (Pipeline шаг Apply Commands)

Внешний слой применяет intent к сущности контролёра:

- MapEntity.status = Moving
- MapEntity.isMovement = true
- MapEntity.movement.speed = intent.speed (если intent.isSpeed)
- MapEntity.movement.isTarget = true
- MapEntity.movement.target = intent.target
- MapEntity.movement.isRoute = true
- MapEntity.movement.route инициализируется как "пустой маршрут" (см. ниже)

### 5.3 Stop: применение к MapState

Внешний слой обязан:
- MapEntity.status = Idle
- MapEntity.isMovement = false
- MapEntity.movement.isTarget = false
- MapEntity.movement.isRoute = false
- MapEntity.movement.route.nodes = [], route.edges = []

*При isMovement === false движение не исполняется независимо от содержимого movement; сброс флагов устраняет "призраки" в дебаге.*

### 5.4 HoldPosition

Ничего не меняется в MapState при применении; сущность уже должна быть Idle. Intent остаётся активным до Cancelled/Failed/timeout.

### 5.5 EngageEntity (опционально): применение к MapState

Как MoveToTarget с target = TargetEntity (те же шаги, что в §5.2).

---

## 6) Построение маршрута (цель — от контролёра, маршрут — от карты)

В рамках "без nullable" фиксируем:

**Route**
- `nodes`: NodeId[]
- `edges`: EdgeId[]
- `validFrom`: MapPosition

**Правило MVP:** route.nodes = [] означает "маршрут ещё не построен".

Если у сущности isMovement === true и movement.isRoute === true и route.nodes = [],
то карта строит маршрут в Map.Tick(T) и выдаёт:
- RouteEvent(kind=Built), или
- RouteEvent(kind=Invalidated), если невозможно построить.

---

## 7) Условия успеха (канон)

### 7.1 Target = Node

Intent MoveToTarget считается **Succeeded**, если карта в ходе тика фиксирует, что сущность стала:
- position = AtNode(nodeId) для TargetNode(nodeId).

*Для определения успеха по узлу контролёр может использовать EntityEvent(kind=PositionChanged) с position=AtNode.*

### 7.2 Target = POI

Intent MoveToTarget считается **Succeeded** при событии:
- POIEvent(kind=ReachedAnchor, poiId)

*EnteredPOI не считается успехом: на якоре возможны разные действия (мирные/враждебные/условные).*

### 7.3 Target = Entity

Intent MoveToTarget считается **Succeeded** при событии:
- EncounterEvent(a, b), где один из участников = target.entityId.

---

## 8) Реакция на события карты (минимум для MVP)

Контролёр обязан обработать:

### 8.1 RouteEvent

- RouteEvent(kind=Invalidated) ⇒ intent → Failed(reason=RouteInvalidated)

### 8.2 TargetEvent

- TargetEvent(kind=Unreachable) ⇒ intent → Failed(reason=TargetUnreachable)
- TargetEvent(kind=Lost) ⇒ intent → Failed(reason=TargetLost)

### 8.3 EncounterEvent

- если цель = Entity и encounter с целью ⇒ intent → Succeeded
- иначе ⇒ intent → Failed(reason=InterruptedByEncounter) (или Cancelled — решает контролёр)

### 8.4 POIEvent

- ReachedAnchor с нужным poiId ⇒ intent → Succeeded
- EnteredPOI (если случилось по решению внешнего слоя) ⇒ активный intent обычно завершается как Cancelled или Failed(reason=InterruptedByPOIEnter) — решает контролёр/внешний слой

---

## 9) Timeout (опционально)

Если isTimeoutTicks === true и intent дольше timeoutTicks в статусе Active:
- intent → Failed(reason=Other) (или отдельный reason позже)

*Таймаут считается от момента перехода в Active (tickActiveStart): T - tickActiveStart >= timeoutTicks. tickActiveStart — внутреннее поле контролёра, не карты.*

---

## 10) Инварианты (MVP)

- policy = ReplaceActive: новый intent отменяет текущий активный (Cancelled) и становится активным.
- isMovement === (MapEntity.status === Moving).
- movement.isRoute === true ⇒ route присутствует и валиден по схеме; route.nodes = [] допустим как "не построен".
- Success/fail определяется только по MapEvent[]; карта не сообщает "успех intent" напрямую.
