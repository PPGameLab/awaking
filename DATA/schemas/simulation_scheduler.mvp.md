# SimulationTime + Scheduler Contracts (MVP DATA)

## 1) Общий принцип

**TickSource** (или SimulationLoop) — внешний источник тиков.

**Scheduler** — внешний планировщик задач/команд по тикам.

Карта принимает тик и исполняет только пространственную логику.

Внешний слой (Simulation) может:
- регистрировать/дерегистрировать сущности,
- пушить намерения контролёров,
- инициировать вход/выход из POI,
- применять эффекты (если они уже есть),
- запускать "внешние процессы" (бой и т.п.) — но не внутри карты.

---

## 2) SimulationTime

**SimulationTime**
- `tick`: long

*Монотонный счётчик. Источник истины по времени — SimulationLoop.*

---

## 3) Scheduler (планировщик)

### 3.1 ScheduledItem

**ScheduledItem**
- `id`: string
- `dueTick`: long
- `command`: SimulationCommand
- `isTag`: bool
- `tag`: string (валидно при isTag === true; для группировки/отмены)

*tag удобно для "отменить все задачи этого квеста/POI/контролёра".*

### 3.2 SchedulerState

**SchedulerState**
- `items`: ScheduledItem[]

*MVP допускает любой внутренний формат (list/heap); DATA контракт фиксируем как набор.*

### 3.3 SchedulerTickResult

**SchedulerTickResult**
- `tick`: long
- `commands`: SimulationCommand[]

*На каждом тике Scheduler отдаёт все команды, у которых dueTick <= tick.*

---

## 4) SimulationCommand (внешние команды, НЕ решения карты)

**SimulationCommand** (одно из)
- MapCommand (прямые операции над картой)
- ControllerCommand (команды контролёрам)
- WorldCommand (операции сущностей мира вне карты — опционально для MVP)

---

## 5) MapCommand (операции над картой)

**MapCommand** (одно из)
- RegisterEntityCommand
- DeregisterEntityCommand
- EnterPOICommand
- ExitPOICommand
- SetEntityStatusCommand
- SetEntityPositionCommand

### 5.1 RegisterEntityCommand

**RegisterEntityCommand**
- `type`: "RegisterEntity"
- `entity`: MapEntity

*Регистрация — "сущность мира стала сущностью на карте".*

### 5.2 DeregisterEntityCommand

**DeregisterEntityCommand**
- `type`: "DeregisterEntity"
- `entityId`: MapEntityId
- `isReason`: bool
- `reason`: DeregisterReason (валидно при isReason === true)
- `isPOI`: bool
- `poiId`: POIId (валидно при isPOI === true)

**DeregisterReason** (MVP)
- EnterPOI
- RemovedFromWorld
- Other

### 5.3 EnterPOICommand / ExitPOICommand

**EnterPOICommand**
- `type`: "EnterPOI"
- `entityId`: MapEntityId
- `poiId`: POIId

**ExitPOICommand**
- `type`: "ExitPOI"
- `entityId`: MapEntityId
- `poiId`: POIId
- `spawnPosition`: MapPosition

*ExitPOI должен указать, где сущность появляется на карте (узел или ребро+progress).*

### 5.4 SetEntityStatusCommand

**SetEntityStatusCommand**
- `type`: "SetEntityStatus"
- `entityId`: MapEntityId
- `status`: MapEntityStatus

*Например: внешний бой завершён → поставить Idle или Disabled.*

### 5.5 SetEntityPositionCommand

**SetEntityPositionCommand**
- `type`: "SetEntityPosition"
- `entityId`: MapEntityId
- `position`: MapPosition

*Это не "движение", это административная коррекция (телепорт, восстановление, дебаг, special-case).*

---

## 6) ControllerCommand (намерения контролёров)

**ControllerCommand** (одно из)
- PushIntentCommand
- CancelIntentCommand

### 6.1 PushIntentCommand

**PushIntentCommand**
- `type`: "PushIntent"
- `controllerId`: string
- `intent`: ControllerIntent

**ControllerIntent** (MVP) — минимальный payload для PushIntent; полный контракт (policy, timeout, FSM, условия успеха) — `controller_intent.mvp.md`.

- `id`: string
- `kind`: IntentKind (например: MoveToTarget)
- `policy`: IntentPolicy (ReplaceActive, Queue)
- `isTarget`: bool, `target`: Target (валидно при isTarget === true)
- `isSpeed`: bool, `speed`: float (валидно при isSpeed === true; ∆progress per tick)
- `isTimeoutTicks`: bool, `timeoutTicks`: long (валидно при isTimeoutTicks === true)
- `isMeta`: bool, `meta`: Dictionary<string, string> (валидно при isMeta === true)

### 6.2 CancelIntentCommand

**CancelIntentCommand**
- `type`: "CancelIntent"
- `controllerId`: string
- `intentId`: string
- `isReason`: bool
- `reason`: string (валидно при isReason === true)

---

## 7) WorldCommand (опционально для MVP)

*Если в одном месте хранить "внешние" команды мира (не карты), можно добавить:*

**WorldCommand** (одно из)
- SpawnWorldEntity
- DespawnWorldEntity
- StartExternalProcess (бой/событие; карта не участвует)

*Для MVP можно не фиксировать; достаточно MapCommand и ControllerCommand.*

---

## 8) Инварианты (MVP, текстом)

- SimulationLoop увеличивает SimulationTime.tick монотонно.
- На каждом тике:
  - Scheduler выдаёт SimulationCommand[]
  - Команды применяются к миру/контролёрам/карте (внешним слоем)
  - Карта исполняет MapTickResult = Map.Tick(tick)
  - События карты (MapEvent[]) обрабатываются внешними системами
- Scheduler не принимает решений "что планировать", он только доставляет по времени.
