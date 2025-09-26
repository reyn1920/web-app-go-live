.PHONY: setup dev run run-dev lint fix mdfix test clean kill

PY=python3

setup:
	pip install -U pip
	pip install -r requirements-dev.txt

run:
	uvicorn backend.app:app --host 127.0.0.1 --port 8000

run-dev:
	uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload \
	  --reload-dir backend \
	  --reload-include 'backend/**/*.py' \
	  --reload-exclude 'scripts/*' --reload-exclude 'tools/*' \
	  --reload-exclude '_backup/*' --reload-exclude '.mp_fix_backups/*' \
	  --reload-exclude 'node_modules/*' --reload-exclude 'venv/*' \
	  --reload-exclude '*.md'

lint:
	ruff check .
	mypy backend tools scripts || true

fix:
	ruff check . --fix
	ruff format .

mdfix:
	$(PY) tools/markdown_fixer.py --path . --verbose

test:
	pytest -q

clean:
	rm -rf _backup .mp_fix_backups **/__pycache__ dist build .pytest_cache

kill:
	lsof -nP -iTCP:8000 | awk 'NR>1{print $$2}' | xargs -r kill -9
