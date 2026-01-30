COMMAND: BUILD_CORE_GLOSSARY
DESC: Пересобирает агрегированный LORE/glossary/_core.md из отдельных терминов
READS: LORE/glossary/*.md
WRITES: LORE/glossary/_core.md
SAFE: no_invent, no_manual_edit

Пересобери `LORE/glossary/_core.md` как агрегированный список терминов.

Правила:
- НЕ придумывай новых терминов.
- Для каждого файла термина возьми: Заголовок, Status, "Кратко" (или первую краткую дефиницию).
- Отсортируй термины по алфавиту (русский алфавит).
- В начале `_core.md` кратко опиши, что это агрегатор.

Выход: полностью переписанный `LORE/glossary/_core.md`.
