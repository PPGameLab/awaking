# PROMPTS INDEX

> Этот файл сгенерирован скриптом `tools/list_prompts.py`.
> Updated: `2026-01-30T16:10:30Z`

## Как вызывать команды в Cursor

Пиши в чат Cursor строго так:

```
CMD: <COMMAND>
```

Пример:

```
CMD: BUILD_SNAPSHOT
```

## Список команд

| COMMAND | Описание | Reads | Writes | SAFE | Файл |
|---|---|---|---|---|---|
| `BUILD_CORE_GLOSSARY` | Пересобирает агрегированный LORE/glossary/_core.md из отдельных терминов | `LORE/glossary/*.md` | `LORE/glossary/_core.md` | `no_invent, no_manual_edit` | `BUILD_CORE_GLOSSARY.md` |
| `BUILD_SNAPSHOT` | Пересобирает WORLD_SNAPSHOT.md из LORE/ и DATA/ | `LORE/**, DATA/**, PROMPTS/**` | `WORLD_SNAPSHOT.md` | `no_invent, no_manual_edit` | `BUILD_SNAPSHOT.md` |
| `CHECK_TERM_IDS` | Проверяет уникальность ID в LORE/glossary и соответствие файла/заголовка/ID | `LORE/glossary/*.md` | `(none)` | `no_invent` | `CHECK_TERM_IDS.md` |
| `LINT_SNAPSHOT` | Проверяет WORLD_SNAPSHOT.md на форму, дубли и запрещённые формулировки | `WORLD_SNAPSHOT.md` | `(none)` | `no_invent` | `LINT_SNAPSHOT.md` |
| `NEW_GLOSSARY_TERM` | Создаёт новый термин в LORE/glossary/ по шаблону (без выдумывания фактов) | `(user input)` | `LORE/glossary/<TERM>.md` | `no_invent, no_manual_edit` | `NEW_GLOSSARY_TERM.md` |
| `VALIDATE_LORE_DATA` | Валидирует согласованность LORE/ и DATA/ и ищет конфликты | `LORE/**, DATA/**` | `(none)` | `no_invent` | `VALIDARY_LORE_DATA.md` |

## Правила исполнения (для модели)

- Если пользователь написал `CMD: ...`, открой соответствующий файл в `PROMPTS/` и следуй инструкциям буквально.
- Если команды не существует — выведи ближайшие команды по схожему имени из таблицы выше.
- Не придумывай новые факты: если данных нет — пиши `TBD` или возвращай список недостающих источников.
