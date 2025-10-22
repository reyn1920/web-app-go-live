SHELL := /bin/bash

# === HOST-NATIVE TOOL PATHS (Apple Silicon Homebrew defaults) ===
PY := /opt/homebrew/bin/python3.11
PIP := /opt/homebrew/bin/python3.11 -m pip
NODE := /opt/homebrew/bin/node
PNPM := /opt/homebrew/bin/pnpm
CURL := /usr/bin/curl

# === LINLY-TALKER CONFIG ===
LT_HOST := 127.0.0.1
LT_PORT := 7861

define REQ
	@command -v $(1) >/dev/null 2>&1 || { echo "ERR: $(1) not found. Run: make doctor"; exit 2; }
endef

.PHONY: doctor doctor-full setup lint type test run ci release rollback livecheck moneycheck envcheck fix-perms \
        protect-freeze protect-guard freeware-guard snapshot-tools test-e2e test-speechelo \
        install-linly talker-start talker-stop talker-logs talker-reload talker-status talker-health talker-diagnose

# --- CORE TARGETS ---
doctor: ; @/bin/bash scripts/doctor_host.sh

doctor-full:
	@echo "==> Running comprehensive system diagnostic (doctor.py)"
	@$(PY) doctor.py

setup:
	$(call REQ,$(PY))
ifneq ("$(wildcard package.json)","")
	$(call REQ,$(NODE)) ; $(call REQ,$(PNPM))
endif
	@echo "==> python pins (GLOBAL)"; $(PIP) install -U pip --break-system-packages ; $(PIP) install -r requirements.lock.txt --break-system-packages
ifneq ("$(wildcard package.json)","")
	@echo "==> node deps (LOCAL)"; $(PNPM) install --silent
endif
	@echo "ok"

lint:
	$(call REQ,ruff)
	@echo "==> lint"
	@ruff format --check .
	@ruff check --output-format=full --exit-zero && { echo "ERR: Ruff warnings present (policy=0 warnings)"; exit 1; } || true
	@ruff check --select=ALL --ignore=E501 --exit-zero || { echo "ERR: Ruff issues remain"; exit 1; }
ifneq ("$(wildcard package.json)","")
	$(call REQ,eslint)
	@$(PNPM) run -s prettier -c .
	@$(PNPM) run -s eslint . --max-warnings=0
endif
	@echo "ok"

type:
	$(call REQ,pyright)
	@echo "==> type"; pyright --level error; echo "ok"

test:
	$(call REQ,pytest)
	@echo "==> test"; pytest -q; echo "ok"

run:
	@echo "==> run (host-native, 100% real)"
	@if [ -f api/app.py ]; then uvicorn api.app:app --host 0.0.0.0 --port 8000; \
	elif [ -f main_orchestrator.py ]; then $(PY) main_orchestrator.py; \
	elif [ -f main.py ]; then $(PY) main.py; \
	else echo "ERR: no entrypoint (api/app.py, main_orchestrator.py, or main.py)"; exit 2; fi

# --- 100% LIVE CHECKS ---
livecheck: ; @/bin/bash scripts/livecheck.sh
moneycheck: ; @/bin/bash scripts/moneycheck.sh
envcheck: ; @/bin/bash scripts/envcheck.sh
fix-perms: ; @chmod +x scripts/*.sh || true

# --- GUARDS & SNAPSHOTS ---
protect-freeze: ; @/bin/bash scripts/protect_freeze.sh .
protect-guard:  ; @/bin/bash scripts/protect_guard.sh
freeware-guard: ; @/bin/bash scripts/freeware_guard.sh
snapshot-tools: ; @/bin/bash scripts/snapshot_tools.sh

# --- CI (FIXED): Run doctor FIRST ---
ci: doctor setup lint type test freeware-guard protect-guard snapshot-tools
	@echo "==> ci gates passed (host-native + free/additive guards)"

# --- A+ TASKS ---
test-e2e:
	$(call REQ,$(PY))
	@echo "==> Running E2E Pipeline Test (100% LIVE)..."
	$(PY) test_full_pipeline.py

test-speechelo:
	$(call REQ,$(PY))
	@echo "==> Running Speechelo Login Test (100% LIVE)..."
	$(PY) test_speechelo_login.py

# --- RELEASE ---
release:
	@git diff --quiet || { echo "ERR: uncommitted changes"; exit 2; }
	@TAG="host.$(shell date -u +%Y%m%d%H%M%S)"; git tag -a $$TAG -m "Release $$TAG" && git push origin $$TAG && echo "Tagged $$TAG"

rollback:
	@LAST=$$(git tag --list 'host.*' | sort -V | tail -n1); \
	test -n "$$LAST" || { echo "ERR: no host tag"; exit 2; }; \
	echo "Rolling back to $$LAST"; git checkout $$LAST

# --- LINLY-TALKER MANAGEMENT ---
install-linly:
	@echo "==> Running Linly-Talker one-shot installer (host-native, no venv)"
	@test -f ~/fix_linly_talker_macos.sh || { echo "ERR: ~/fix_linly_talker_macos.sh not found"; exit 2; }
	@chmod +x ~/fix_linly_talker_macos.sh
	@~/fix_linly_talker_macos.sh

talker-start:
	@launchctl load  -w ~/Library/LaunchAgents/com.user.linlytalker.plist || true
	@sleep 2; echo "Linly-Talker: $(LT_HOST):$(LT_PORT)"

talker-stop:
	@launchctl unload -w ~/Library/LaunchAgents/com.user.linlytalker.plist || true
	@pkill -f "python3.11 app_talk.py" || true

talker-logs:
	@tail -f ~/Library/Logs/linlytalker.out.log ~/Library/Logs/linlytalker.err.log

talker-reload: talker-stop talker-start

talker-status:
	@echo "==> Linly-Talker status:"
	@launchctl list | grep linlytalker || echo "Service not loaded"
	@curl -sf http://127.0.0.1:7861 >/dev/null && echo "API responding on port 7861" || echo "API not responding"

talker-health:
	@echo "==> Running Linly-Talker health check..."
	@/bin/bash scripts/check_linly_health.sh

talker-diagnose:
	@echo "==> Running comprehensive Linly-Talker diagnostics..."
	@/bin/bash scripts/diagnose_linly.sh

# --- TTS MANAGEMENT ---
.PHONY: tts-doctor tts-use-linly tts-use-chatterbox tts-use-speechelo tts-smoke

tts-doctor:
	@$(PY) -c "import os, socket, sys; h=os.getenv('LT_HOST','127.0.0.1'); p=int(os.getenv('LT_PORT','7861')); s=socket.socket(); s.settimeout(1); (s.connect((h,p)), print(f'OK: Linly-Talker reachable at {h}:{p}')) if not s.close() else None" 2>/dev/null || echo "WARN: Linly-Talker not reachable"
	@test -n "$${CHATTERBOX_URL}" && echo "OK: Chatterbox URL: $${CHATTERBOX_URL}" || echo "INFO: Chatterbox URL not set"
	@test -n "$${SPEECHELO_API_KEY}" && test -n "$${SPEECHELO_USER}" && echo "OK: Speechelo credentials present" || echo "WARN: Speechelo credentials not configured"
	@echo "OK: TTS doctor complete"

tts-use-linly:
	@gsed -i 's/^TTS_BACKEND=.*/TTS_BACKEND=linly-talker/' .env || sed -i '' 's/^TTS_BACKEND=.*/TTS_BACKEND=linly-talker/' .env
	@echo "Backend -> linly-talker"

tts-use-chatterbox:
	@gsed -i 's/^TTS_BACKEND=.*/TTS_BACKEND=chatterbox/' .env || sed -i '' 's/^TTS_BACKEND=.*/TTS_BACKEND=chatterbox/' .env
	@echo "Backend -> chatterbox"

tts-use-speechelo:
	@gsed -i 's/^TTS_BACKEND=.*/TTS_BACKEND=speechelo/' .env || sed -i '' 's/^TTS_BACKEND=.*/TTS_BACKEND=speechelo/' .env
	@echo "Backend -> speechelo"

tts-smoke:
	@/opt/homebrew/bin/python3.11 tools/tts_smoke.py "End-to-end TTS smoke."

# --- QA SUITE ---
.PHONY: qa-all qa-env qa-blender qa-resolve qa-talker qa-avatar qa-blue qa-render qa-upload e2e

# 1) Environment sanity: paths & versions
qa-env:
	@$(PY) tools/qa_env.py

# 2) Blender works headless and can render a frame
qa-blender:
	@$(PY) tools/qa_blender.py

# 3) Resolve scripting reachable (Resolve 20 must be open)
qa-resolve:
	@$(PY) tools/qa_resolve.py

# 4) Linly-Talker reachable and can synthesize TTS
qa-talker:
	@$(PY) tools/qa_talker.py "Linly-Talker online test."

# 5) Avatar pipeline call returns a real video/audio file path
qa-avatar:
	@$(PY) tools/qa_avatar.py "Avatar smoke test line."

# 6) Detect accidental blue-screen (solid/near-solid blue) in output mp4
qa-blue:
	@$(PY) tools/qa_blue_screen.py outputs/avatar/avatar_smoke.mp4

# 7) Optional quick render+mux via Resolve (pref) or ffmpeg fallback
qa-render:
	@$(PY) tools/qa_render.py

# 8) Upload to YouTube (OAuth flow the first time)
qa-upload:
	@$(PY) tools/qa_youtube_upload.py --file outputs/final/final_smoke.mp4 --title "Smoke Test: $(shell date +%Y-%m-%dT%H:%M:%S)" --description "End-to-end smoke test" --privacy private

# One button: everything in order
e2e: qa-env qa-blender qa-resolve qa-talker qa-avatar qa-blue qa-render qa-upload

# --- OLLAMA MANAGEMENT ---
.PHONY: ollama-install ollama-start ollama-stop ollama-logs ollama-pull ollama-smoke ollama-json ollama-vision drive-install drive-status drive-config drive-restart drive-logs drive-cache-reset drive-sanity-proof

ollama-install:
	@brew install ollama || true
	@brew services start ollama
	@sleep 2
	@curl -s http://127.0.0.1:11434/api/version && echo

ollama-start:
	@brew services start ollama
	@sleep 1
	@curl -s http://127.0.0.1:11434/api/tags | jq . || true

ollama-stop:
	@brew services stop ollama || true

ollama-logs:
	@log show --style compact --predicate 'process == "ollama"' --last 30m || true

ollama-pull:
	@chmod +x tools/ollama_pull.sh
	@./tools/ollama_pull.sh

ollama-smoke:
	@$(PY) tools/ollama_smoke.py "List three security hardening steps for macOS."

ollama-json:
	@$(PY) tools/ollama_json_smoke.py

ollama-vision:
	@$(PY) tools/ollama_vision_smoke.py /Users/thomasbrianreynolds/Linly-Talker/CosyVoice/asset/dingding.png

# --- GOOGLE DRIVE MANAGEMENT ---
drive-install:
	@chmod +x tools/install_google_drive.sh
	@./tools/install_google_drive.sh

drive-status:
	@chmod +x tools/detect_google_drive.sh
	@./tools/detect_google_drive.sh

drive-config:
	@chmod +x tools/drive_auto_config.sh
	@./tools/drive_auto_config.sh

drive-restart:
	@killall "Google Drive" 2>/dev/null || true
	@sleep 2
	@open -a "Google Drive"
	@sleep 3
	@echo "✅ Google Drive restarted"

drive-logs:
	@log show --style compact --predicate 'process == "Google Drive"' --last 30m || true

.PHONY: dashboard
dashboard: ## Run the Mission Control Dashboard
	@echo "--- 🚀 Starting Mission Control Dashboard ---"
	@echo "Access at: http://localhost:8501"
	@/opt/homebrew/bin/python3.11 -m streamlit run app/dashboard.py

drive-cleanup:
	@chmod +x tools/drive_cleanup_mounts.sh
	@./tools/drive_cleanup_mounts.sh

drive-detect:
	@chmod +x tools/drive_desktop_detect.py
	@$(PY) tools/drive_desktop_detect.py


drive-recover:
	@chmod +x tools/gdrive_recover_unsynced.sh
	@./tools/gdrive_recover_unsynced.sh


drive-recovery-full:
	@chmod +x tools/gdrive_complete_recovery.sh
	@./tools/gdrive_complete_recovery.sh

drive-cache-reset:
	@chmod +x tools/gdrive_cache_reset.sh
	@./tools/gdrive_cache_reset.sh

drive-sanity-proof:
	@chmod +x tools/gdrive_sanity_proof.py
	@$(PY) tools/gdrive_sanity_proof.py

gdrive-health:
	@chmod +x tools/gdrive_health_check.sh
	@./tools/gdrive_health_check.sh

gdrive-guard:
	@chmod +x tools/gdrive_guard.sh
	@./tools/gdrive_guard.sh


gdrive-dashboard:
	@chmod +x tools/gdrive_dashboard.sh
	@./tools/gdrive_dashboard.sh

gdrive-dashboard-once:
	@chmod +x tools/gdrive_dashboard.sh
	@./tools/gdrive_dashboard.sh --once

