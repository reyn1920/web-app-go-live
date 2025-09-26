from __future__ import annotations

import re
from pathlib import Path


def main() -> None:
    p = Path("mypy.ini")
    if not p.exists():
        return
    txt = p.read_text(encoding="utf-8")
    seen: set[str] = set()
    blocks = re.split(r"(\[\[mypy-overrides\]\])", txt)
    out: list[str] = []
    i = 0
    while i < len(blocks):
        if blocks[i] == "[[mypy-overrides]]":
            block = blocks[i] + blocks[i + 1]
            modm = re.search(r"module\s*=\s*([^\n]+)", blocks[i + 1])
            mod = modm.group(1).strip() if modm else ""
            if mod in seen:
                i += 2
                continue
            seen.add(mod)
            out.append(block)
            i += 2
        else:
            out.append(blocks[i])
            i += 1
    cleaned = "\n".join([b for b in out if b.strip() != "[[mypy-overrides]]"])
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    if cleaned != txt:
        p.write_text(cleaned, encoding="utf-8")
        print("mypy.ini sanitized")
    else:
        print("mypy.ini already clean")


if __name__ == "__main__":
    main()
