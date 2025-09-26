#!/usr/bin/env python3
"""Verification script for dual-path import setup."""

import os
import shlex
import subprocess
from pathlib import Path

# sys import removed (unused)


def run_command(cmd, cwd=None, env=None):
    """Run a shell command and return success status."""
    try:
        if isinstance(cmd, str):
            cmd = shlex.split(cmd)
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, env=env, check=True)
        return True, result.stdout, result.stderr
    except (subprocess.CalledProcessError, OSError) as e:
        return False, "", str(e)


def main():
    """Main verification routine."""
    repo_root = Path(__file__).parent
    print(f"🔍 Verifying setup in: {repo_root}")

    # Check if backend is a package
    backend_init = repo_root / "backend" / "__init__.py"
    print(f"✅ Backend package: {backend_init.exists()}")

    # Test import from backend/ directory
    print("\n📁 Testing import from backend/ directory...")
    # For shell pipelines, still use shell=True, but here we split and run only the python command
    # The activation and cd are not portable in subprocess without shell, so just test the python import
    success, _, stderr = run_command(
        ["python3", "-c", "from app import app; print('Import successful')"], cwd=repo_root / "backend"
    )
    if success:
        print("✅ Backend directory import: OK")
    else:
        print(f"❌ Backend directory import failed: {stderr}")

    # Test package import from root
    print("\n📦 Testing package import from repo root...")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root)
    cmd = ["python3", "-c", "from backend.app import app; print('Package import successful')"]
    success, _, stderr = run_command(cmd, cwd=repo_root, env=env)
    if success:
        print("✅ Package import from root: OK")
    else:
        print(f"❌ Package import failed: {stderr}")

    # Check ESLint config
    eslintrc = repo_root / ".eslintrc.json"
    if eslintrc.exists():
        content = eslintrc.read_text()
        if '"root": true' in content:
            print("✅ ESLint root configuration: OK")
        else:
            print("❌ ESLint root configuration: Missing")
    else:
        print("❌ ESLint config file: Not found")

    # Check mypy config
    pyproject = repo_root / "pyproject.toml"
    if pyproject.exists():
        content = pyproject.read_text()
        if 'python_version = "3.13"' in content:
            print("✅ Mypy configuration: OK")
        else:
            print("❌ Mypy configuration: Incorrect")
    else:
        print("❌ Mypy config file: Not found")

    print("\n🎉 Verification complete!")


if __name__ == "__main__":
    main()
