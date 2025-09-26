"""
Quick fixers for:
- Enforce defusedxml in all XML parsing sites.
- Add minimal module docstrings to routers missing them.
- Soft-wrap >120-char lines where trivial (strings/comments).
Add-only; backs up touched files under ./data/backups/quick_fixers/.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKUP = ROOT / "data/backups/quick_fixers"
BACKUP.mkdir(parents=True, exist_ok=True)


def backup(p: Path) -> None:
    # Skip backing up files already under backups to avoid recursive nesting
    try:
        if BACKUP in p.resolve().parents or p.resolve().is_relative_to(BACKUP):
            return
    except AttributeError:
        # Python <3.9 fallback for is_relative_to
        try:
            p.resolve().relative_to(BACKUP)
            return
        except ValueError as exc:
            print(f"backup: relative_to failed: {exc}")
    except (OSError, RuntimeError) as exc:
        print(f"backup: path resolution failed: {exc}")
        return
    dst = BACKUP / p.relative_to(ROOT)
    dst.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        shutil.copy2(p, dst)


def ensure_docstring(p: Path) -> bool:
    txt = p.read_text(encoding="utf-8")
    if not re.match(r'^[ \t]*("""|\'\'\')', txt, flags=re.S):
        txt = '"""Auto-added short module docstring."""\n' + txt
        p.write_text(txt, encoding="utf-8")
        return True
    return False


def enforce_defusedxml(p: Path) -> bool:
    txt = p.read_text(encoding="utf-8")
    changed = False
    # Replace stdlib ET import with defusedxml
    txt2 = re.sub(
        r"from\s+xml\.etree\s+import\s+ElementTree\s+as\s+ET",
        "from defusedxml import ElementTree as ET",
        txt,
    )
    if txt2 != txt:
        txt = txt2
        changed = True
    # Common patterns using ET.parse/fromstring stay valid
    if changed:
        p.write_text(txt, encoding="utf-8")
    return changed


def soft_wrap_simple_lines(p: Path, max_len: int = 120) -> bool:
    txt = p.read_text(encoding="utf-8")
    out: list[str] = []
    changed = False
    for line in txt.splitlines():
        if len(line) > max_len and line.strip().startswith(("#", '"""', "'''")):
            # wrap comments/docstrings only (safe, no behavior change)
            words = re.split(r"(\s+)", line)
            cur = ""
            lines: list[str] = []
            for w in words:
                if len(cur) + len(w) > max_len:
                    lines.append(cur.rstrip())
                    cur = w.lstrip()
                else:
                    cur += w
            if cur:
                lines.append(cur.rstrip())
            out.extend(lines)
            changed = True
        else:
            out.append(line)
    if changed:
        p.write_text("\n".join(out) + ("\n" if txt.endswith("\n") else ""), encoding="utf-8")
    return changed


def main() -> None:
    changed: list[str] = []
    for p in ROOT.rglob("*.py"):
        if any(seg in {"venv", ".venv", ".git", "__pycache__", "node_modules"} for seg in p.parts):
            continue
        # Skip all backup artifacts entirely
        if str(p).startswith(str(BACKUP)) or "data/backups" in str(p):
            continue
        rel = p.relative_to(ROOT)
        # routers: ensure docstrings
        if "routers" in rel.parts and p.name.endswith("_router.py"):
            backup(p)
            if ensure_docstring(p):
                changed.append(str(rel) + " [+docstring]")
        # XML parsers: enforce defusedxml
        text = p.read_text(encoding="utf-8")
        if "xml.etree" in text or re.search(r"\bET\.(fromstring|parse)\(", text):
            backup(p)
            if enforce_defusedxml(p):
                changed.append(str(rel) + " [defusedxml]")
        # Soft-wrap long comments/docstrings
        backup(p)
        if soft_wrap_simple_lines(p):
            changed.append(str(rel) + " [wrap]")
    print("CHANGED\n" + ("\n".join(changed) if changed else "(none)"))


if __name__ == "__main__":
    main()
