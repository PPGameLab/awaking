from __future__ import annotations

import argparse
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple


PROMPTS_DIR_NAME = "PROMPTS"
INDEX_FILE_NAME = "INDEX.md"

META_KEYS = ["COMMAND", "DESC", "READS", "WRITES", "SAFE"]
META_LINE_RE = re.compile(r"^\s*([A-Z_]+)\s*:\s*(.+?)\s*$")


@dataclass
class PromptInfo:
    filename: str
    command: str
    desc: str
    reads: str
    writes: str
    safe: str


def read_file_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_meta(text: str) -> Dict[str, str]:
    meta: Dict[str, str] = {}
    for line in text.splitlines()[:40]:  # meta is expected at the top; 40 lines is enough
        m = META_LINE_RE.match(line)
        if not m:
            # Stop early when meta block ends (first blank line after having meta)
            if meta and not line.strip():
                break
            continue
        key, value = m.group(1), m.group(2)
        meta[key] = value
    return meta


def load_prompts(prompts_dir: Path) -> Tuple[List[PromptInfo], List[str]]:
    infos: List[PromptInfo] = []
    errors: List[str] = []

    for path in sorted(prompts_dir.glob("*.md")):
        if path.name == INDEX_FILE_NAME:
            continue

        text = read_file_text(path)
        meta = parse_meta(text)

        missing = [k for k in META_KEYS if k not in meta]
        if missing:
            errors.append(f"{path.as_posix()}: missing meta keys: {', '.join(missing)}")
            continue

        infos.append(
            PromptInfo(
                filename=path.name,
                command=meta["COMMAND"].strip(),
                desc=meta["DESC"].strip(),
                reads=meta["READS"].strip(),
                writes=meta["WRITES"].strip(),
                safe=meta["SAFE"].strip(),
            )
        )

    # detect duplicate COMMAND
    seen: Dict[str, str] = {}
    for info in infos:
        if info.command in seen:
            errors.append(
                f"Duplicate COMMAND '{info.command}' in {info.filename} and {seen[info.command]}"
            )
        else:
            seen[info.command] = info.filename

    return infos, errors


def make_index_md(infos: List[PromptInfo]) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines: List[str] = []
    lines.append("# PROMPTS INDEX")
    lines.append("")
    lines.append("> Этот файл сгенерирован скриптом `tools/list_prompts.py`.")
    lines.append(f"> Updated: `{now}`")
    lines.append("")
    lines.append("## Как вызывать команды в Cursor")
    lines.append("")
    lines.append("Пиши в чат Cursor строго так:")
    lines.append("")
    lines.append("```")
    lines.append("CMD: <COMMAND>")
    lines.append("```")
    lines.append("")
    lines.append("Пример:")
    lines.append("")
    lines.append("```")
    lines.append("CMD: BUILD_SNAPSHOT")
    lines.append("```")
    lines.append("")
    lines.append("## Список команд")
    lines.append("")

    # Table header
    lines.append("| COMMAND | Описание | Reads | Writes | SAFE | Файл |")
    lines.append("|---|---|---|---|---|---|")

    for info in sorted(infos, key=lambda x: x.command.lower()):
        lines.append(
            f"| `{info.command}` | {escape_pipes(info.desc)} | `{escape_pipes(info.reads)}` | `{escape_pipes(info.writes)}` | `{escape_pipes(info.safe)}` | `{info.filename}` |"
        )

    lines.append("")
    lines.append("## Правила исполнения (для модели)")
    lines.append("")
    lines.append("- Если пользователь написал `CMD: ...`, открой соответствующий файл в `PROMPTS/` и следуй инструкциям буквально.")
    lines.append("- Если команды не существует — выведи ближайшие команды по схожему имени из таблицы выше.")
    lines.append("- Не придумывай новые факты: если данных нет — пиши `TBD` или возвращай список недостающих источников.")
    lines.append("")
    return "\n".join(lines)


def escape_pipes(s: str) -> str:
    return s.replace("|", "\\|")


def print_console_table(infos: List[PromptInfo]) -> None:
    if not infos:
        print("No prompts found.")
        return

    # Pretty-ish aligned output
    cmd_w = max(len(i.command) for i in infos)
    file_w = max(len(i.filename) for i in infos)
    print(f"{'COMMAND'.ljust(cmd_w)}  {'FILE'.ljust(file_w)}  DESC")
    print(f"{'-'*cmd_w}  {'-'*file_w}  {'-'*40}")
    for i in sorted(infos, key=lambda x: x.command.lower()):
        print(f"{i.command.ljust(cmd_w)}  {i.filename.ljust(file_w)}  {i.desc}")


def main() -> int:
    parser = argparse.ArgumentParser(description="List and index prompt commands from PROMPTS/")
    parser.add_argument("--root", default=".", help="Project root (default: current directory)")
    parser.add_argument("--no-write-index", action="store_true", help="Do not update PROMPTS/INDEX.md")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    prompts_dir = root / PROMPTS_DIR_NAME

    if not prompts_dir.exists() or not prompts_dir.is_dir():
        print(f"ERROR: '{PROMPTS_DIR_NAME}/' not found at: {prompts_dir}")
        return 2

    infos, errors = load_prompts(prompts_dir)

    if errors:
        print("ERRORS:")
        for e in errors:
            print(f"  - {e}")
        print("")
        # Still print what we could parse
        if infos:
            print("PARTIAL LIST:")
            print_console_table(infos)
        return 1

    print_console_table(infos)

    if not args.no_write_index:
        index_path = prompts_dir / INDEX_FILE_NAME
        index_path.write_text(make_index_md(infos), encoding="utf-8")
        print(f"\nUpdated: {index_path.as_posix()}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
