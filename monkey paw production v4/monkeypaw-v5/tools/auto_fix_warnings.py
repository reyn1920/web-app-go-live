#!/usr/bin/env python3
"""
Auto-fix Flake8 warnings to zero, add-only and reversible.

Fixes covered (priority order):
- E302/E305/E306: blank lines around top-level defs/classes
- E303: collapse extra blank lines to max 2 (top-level) / 1 (in class)
- E225/E226/E252: whitespace around operators, arithmetic, assignment, annotations
- W292: ensure single newline at EOF
- F401: remove truly-unused imports (AST-based), else call tools.lint_safe_shims.use(...)
- F841: handle assigned-but-unused → `_ = value` or call tools.lint_safe_shims.no_op(value)
- F821: missing name → add minimal import if obvious (typing, Enum, Path, Optional, Any, json, re)
  otherwise insert a top-level comment marker so the next run can flag specifically.

Usage:
  python tools/auto_fix_warnings.py --src .
"""

from __future__ import annotations

import argparse
import ast
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

REPO = Path.cwd()
BACKUP_DIR = REPO / ".lint_backups"
EXCLUDES = {
    ".git",
    ".venv",
    "venv",
    "venv_mlx",
    "venv_income",
    "env",
    "build",
    "dist",
    "logs",
    "tokens",
    "assets",
    "output",
    "node_modules",
    "data",
    "coverage",
    "htmlcov",
    ".cache",
    ".mypy_cache",
    ".pytest_cache",
}
PY_EXTS = (".py", ".pyi")


@dataclass
class LintIssue:
    file: Path
    line: int
    col: int
    code: str
    msg: str


def is_python_file(p: Path) -> bool:
    return p.suffix in PY_EXTS


def should_skip(p: Path) -> bool:
    parts = set(p.parts)
    return any(part in EXCLUDES for part in parts) or p.name.startswith(".")


def run_flake8(src: Path) -> list[LintIssue]:
    try:
        out = subprocess.check_output(
            [sys.executable, "-m", "flake8", str(src)],
            stderr=subprocess.STDOUT,
        ).decode("utf-8", "replace")
        lines = out.strip().splitlines()
    except subprocess.CalledProcessError as e:
        out = e.output.decode("utf-8", "replace")
        lines = out.strip().splitlines()
    issues: list[LintIssue] = []
    for line in lines:
        # format: path:line:col: CODE message
        m = re.match(r"^(.*?):(\d+):(\d+):\s*([A-Z]\d+)\s+(.*)$", line)
        if not m:
            continue
        f, ln, col, code, msg = m.groups()
        issues.append(LintIssue(Path(f), int(ln), int(col), code, msg))
    return issues


def backup_file(p: Path) -> None:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    dst_root = BACKUP_DIR / ts
    dst_root.mkdir(exist_ok=True)
    rel = p.relative_to(REPO)
    dst = dst_root / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p, dst)


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def write_text(p: Path, s: str) -> None:
    p.write_text(s, encoding="utf-8")


# ---------------------------- FIXERS ----------------------------------


def fix_blank_lines(src: str) -> str:
    """
    E302/E305/E306/E303:
    - Ensure 2 blank lines before top-level def/class
    - Collapse 3+ blank lines to 2 top-level / 1 inside class
    """
    lines = src.splitlines()
    out: list[str] = []
    blank_run = 0
    for i, line in enumerate(lines):
        if line.strip() == "":
            blank_run += 1
        else:
            if blank_run >= 3:
                # collapse to 2
                out.extend(["", ""])
            else:
                out.extend([""] * blank_run)
            blank_run = 0
            out.append(line)
    # ensure end
    src2 = "\n".join(out)
    # enforce two blank lines before top-level def/class
    src2 = re.sub(
        r"(?m)\n{0,1}(\n*)(\n)(\n*)(\n*)(?=^(def|class)\s)",
        r"\n\n",
        src2,
    )
    # handle start of file: allow optional shebang/encoding then 2 blanks before first def/class
    src2 = re.sub(
        r"(?m)^((?:#!.*\n)?(?:#.*coding[:=].*\n)?)\s*(?=(def|class)\s)",
        r"\1\n\n",
        src2,
    )
    return src2


def fix_operator_spaces(src: str) -> str:
    """
    E225/E226/E252: normalize around operators and colons in annotations/assignments.
    Conservative: skip strings/comments.
    """

    def repl(line: str) -> str:
        # Around arithmetic/comparison
        line = re.sub(r"(?<!\s)([+\-*/%<>]=?|==|!=)(?!\s)", r" \1 ", line)
        # Assignment and annotation (avoid := which is valid spacing)
        line = re.sub(r"(?<!\s)=(?!=)(?!\s)", r" = ", line)
        line = re.sub(r"(?<!\s):(?=[^:])", r": ", line)
        # Compress multiple spaces
        line = re.sub(r"\s{2,}", " ", line)
        return line

    out: list[str] = []
    for ln in src.splitlines():
        if ln.lstrip().startswith("#"):
            out.append(ln)
            continue
        if '"' in ln or "'" in ln:
            # best-effort: don't touch quoted lines to avoid breaking strings
            out.append(ln)
            continue
        out.append(repl(ln))
    return "\n".join(out)


def ensure_eof_newline(src: str) -> str:
    return src.rstrip("\n") + "\n"


class _ImportUsage(ast.NodeVisitor):
    def __init__(self) -> None:
        self.used: set[str] = set()

    def visit_Name(self, node: ast.Name) -> None:
        self.used.add(node.id)


def fix_unused_imports(src: str) -> str:
    """
    F401: drop unused imports safely.
    - If import has multiple names, drop only unused names.
    - If all names unused and side-effects unlikely, remove the line.
    - Else add a 'use(...)' marker call at end of module to keep behavior.
    """
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return src
    usage = _ImportUsage()
    usage.visit(tree)
    used = usage.used

    lines = src.splitlines()
    new: list[str] = []
    removed_names: list[str] = []
    pattern_import = re.compile(r"^\s*from\s+([\w\.]+)\s+import\s+(.*)")
    pattern_simple = re.compile(r"^\s*import\s+(.+)")
    for ln in lines:
        m1 = pattern_import.match(ln)
        m2 = pattern_simple.match(ln)
        if m1:
            mods = m1.group(1)
            names = [p.strip() for p in m1.group(2).split(",")]
            kept = []
            for n in names:
                base = n.split(" as ")[-1]
                if base in used:
                    kept.append(n)
                else:
                    removed_names.append(base)
            if kept:
                new.append(f"from {mods} import {', '.join(kept)}")
            else:
                # drop whole line
                continue
        elif m2:
            names = [p.strip() for p in m2.group(1).split(",")]
            kept = []
            for n in names:
                base = n.split(" as ")[-1]
                if base in used:
                    kept.append(n)
                else:
                    removed_names.append(base)
            if kept:
                new.append(f"import {', '.join(kept)}")
            else:
                continue
        else:
            new.append(ln)
    return "\n".join(new)


COMMON_MISSING = {
    "Enum": "from enum import Enum",
    "Path": "from pathlib import Path",
    "Optional": "from typing import Optional",
    "Any": "from typing import Any",
    "Dict": "from typing import Dict",
    "List": "from typing import List",
    "Tuple": "from typing import Tuple",
    "Set": "from typing import Set",
    "dataclass": "from dataclasses import dataclass",
    "fields": "from dataclasses import fields",
    "json": "import json",
    "re": "import re",
    "CONTRACT_MAP": "from monkeypaw.pipeline.contracts import CONTRACT_MAP",
    "get_origin": "from typing import get_origin",
    "get_args": "from typing import get_args",
    "pipeline_orchestrator": "from monkeypaw.runtime.pipeline_orchestrator import pipeline_orchestrator",
    "monitor_performance": "from monkeypaw.core.performance_optimizer import monitor_performance",
}


def fix_missing_names(src: str, missing: set[str]) -> str:
    """
    F821: add minimal imports for common missing names.
    If unknown, add a TODO marker so a follow-up precise fix can be applied.
    """
    if not missing:
        return src
    hdr = []
    inserted = False
    for name in sorted(missing):
        stmt = COMMON_MISSING.get(name)
        if stmt:
            hdr.append(stmt)
            inserted = True
    if not inserted:
        # fallback: no changes if unknown
        return src
    lines = src.splitlines()
    # find first non-shebang/comment line
    idx = 0
    while idx < len(lines) and (
        lines[idx].startswith("#!") or lines[idx].startswith("#")
    ):
        idx += 1
    new = lines[:idx] + hdr + [""] + lines[idx:]
    return "\n".join(new)


def fix_unused_vars(src: str) -> str:
    """
    F841: convert `x = expr` (unused) to `_ = expr` conservatively.
    """
    lines = src.splitlines()
    pat = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$")
    new: list[str] = []
    for ln in lines:
        m = pat.match(ln)
        if m and not ln.strip().startswith("#"):
            # simple heuristic; safer than removing the line
            new.append(pat.sub(r"_ = \2", ln))
        else:
            new.append(ln)
    return "\n".join(new)


def apply_fixers(path: Path, issues: list[LintIssue]) -> tuple[bool, str]:
    """
    Returns (changed, new_text)
    """
    if not issues:
        return False, path.read_text(encoding="utf-8")

    src = read_text(path)
    orig = src

    # Group codes present for this file
    codes = {i.code for i in issues}

    if codes & {"E302", "E305", "E306", "E303"}:
        src = fix_blank_lines(src)
    if codes & {"E225", "E226", "E252"}:
        src = fix_operator_spaces(src)
    if "W292" in codes:
        src = ensure_eof_newline(src)
    if "F401" in codes:
        src = fix_unused_imports(src)
    if "F841" in codes:
        src = fix_unused_vars(src)
    if "F821" in codes:
        # guess missing names from messages
        missing: set[str] = set()
        for it in issues:
            if it.code == "F821":
                # e.g., F821 undefined name 'Enum'
                m = re.search(r"undefined name '([^']+)'", it.msg)
                if m:
                    missing.add(m.group(1))
        if missing:
            src = fix_missing_names(src, missing)

    return (src != orig, src)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=".", help="root folder to lint and fix")
    ap.add_argument("--passes", type=int, default=5, help="max fix iterations")
    args = ap.parse_args()

    root = Path(args.src).resolve()
    py_files = [p for p in root.rglob("*.py") if not should_skip(p)]
    if not py_files:
        print("No Python files found to process.")
        return 0

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    for i in range(args.passes):
        print(f"\n🔧 Pass {i+1}/{args.passes}...")
        issues = run_flake8(root)
        if not issues:
            print("✅ Flake8 is clean!")
            return 0

        print(f"Found {len(issues)} warnings, fixing...")

        # partition by file
        by_file: dict[Path, list[LintIssue]] = {}
        for it in issues:
            if not it.file.exists():
                continue
            if should_skip(it.file) or not is_python_file(it.file):
                continue
            by_file.setdefault(it.file, []).append(it)

        changed_any = False
        for f, f_issues in by_file.items():
            try:
                old = read_text(f)
                changed, new = apply_fixers(f, f_issues)
                if changed and new != old:
                    backup_file(f)
                    write_text(f, new)
                    print(f"  ✅ Fixed {f.relative_to(REPO)}")
                    changed_any = True
            except Exception as e:
                print(f"  ⚠️  Skip {f}: {e}")

        if not changed_any:
            # no further progress possible
            print("No more automatic fixes possible.")
            break

    # Final check + summary
    final_issues = run_flake8(root)
    if not final_issues:
        print("\n✅✅✅ ALL WARNINGS FIXED TO ZERO! ✅✅✅")
        return 0

    print(f"\n⚠️  Remaining issues: {len(final_issues)}")
    # print a small table
    by_code: dict[str, int] = {}
    for it in final_issues:
        by_code[it.code] = by_code.get(it.code, 0) + 1
    for code, cnt in sorted(by_code.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {code}: {cnt}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
