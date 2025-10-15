"""ChatGPT Desktop bridge (macOS) for Monkey Paw runtime.

Clean, async-safe helpers to:
  • Detect ChatGPT desktop (Work with Apps)
  • Send a message
  • Copy last response
  • Export current conversation
  • Provide a guard wrapper used elsewhere in the app

Design rules:
  - No broad 'except:'; catch specific exceptions where obvious.
  - No logging f-strings; use lazy % formatting.
  - Async functions use asyncio subprocess/file ops.
  - Optional deps (persistence/config) are gated.
  - ≤100-char lines.
"""
from __future__ import annotations

import asyncio
import contextlib
import inspect
import logging
import pathlib
from dataclasses import dataclass
from datetime import UTC, datetime  # type: ignore[attr-defined]
from typing import Any

try:
    # Optional imports from the same package (grouped to satisfy linters).
    from monkeypaw.config import config as mp_config  # type: ignore
    from monkeypaw.runtime.persistence import persistence as persistence_store  # type: ignore
except ImportError:
    mp_config = None  # type: ignore[assignment]
    persistence_store = None  # type: ignore[assignment]

try:
    # Optional dependency for async file IO
    import aiofiles as aiofiles_mod  # type: ignore
except ImportError:
    aiofiles_mod = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)
HAS_ASYNCIO_TIMEOUT = hasattr(asyncio, "timeout")  # type: ignore[attr-defined]


def _now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


@dataclass
class _Cfg:
    desktop_inter_send_delay_s: float = 0.35
    desktop_script_timeout_s: float = 15.0
    app_name: str = "ChatGPT"


def _safe_cfg() -> _Cfg:
    """Best-effort configuration; falls back to sane defaults."""
    _c = mp_config
    if _c is None:
        return _Cfg()
    return _Cfg(
        desktop_inter_send_delay_s=getattr(
            _c, "desktop_inter_send_delay_s", _Cfg.desktop_inter_send_delay_s,
        ),
        desktop_script_timeout_s=getattr(
            _c, "desktop_script_timeout_s", _Cfg.desktop_script_timeout_s,
        ),
        app_name=getattr(_c, "desktop_app_name", _Cfg.app_name),
    )


class ChatGPTDesktopClient:
    """Thin async wrapper around AppleScript access to ChatGPT desktop."""

    def __init__(self, cfg: _Cfg | None = None) -> None:
        self.cfg = cfg or _safe_cfg()
        self._running: bool | None = None
        logger.info("Desktop client ready for %s", self.cfg.app_name)

    async def _osascript(self, script: str) -> tuple[int, str, str]:
        """Run an AppleScript snippet via `osascript` asynchronously.

        Note: Callers must enforce timeouts using an asyncio timeout context,
        e.g., `async with asyncio.timeout(5): await self._osascript(script)`.
        This function is cancellation-aware and will terminate the subprocess
        if the surrounding timeout cancels this task.
        """
        proc = await asyncio.create_subprocess_exec(
            "osascript",
            "-e",
            script,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            out_b, err_b = await proc.communicate()
        except asyncio.CancelledError:
            # If the caller's timeout cancels us, ensure the subprocess is terminated.
            with contextlib.suppress(ProcessLookupError):
                proc.kill()
            raise
        code = proc.returncode if proc.returncode is not None else 1
        return code, (out_b or b"").decode(), (err_b or b"").decode()

    async def check_running(self) -> bool:
        """Return True if ChatGPT desktop process is visible to System Events."""
        app = self.cfg.app_name
        script = f"""
        tell application "System Events"
            set runningApps to name of every process
            if "{app}" is in runningApps then
                return "running"
            else
                return "not_running"
            end if
        end tell
        """
        try:
            code, out, err = await asyncio.wait_for(self._osascript(script), timeout=5)
        except TimeoutError:
            self._running = False
            logger.debug("check_running: osascript timed out after 5s")
            return False
        self._running = code == 0 and "running" in out
        if not self._running and err:
            logger.debug("check_running stderr: %s", err.strip())
        return bool(self._running)

    async def send_message(self, message: str) -> dict[str, Any]:
        """Type a message into ChatGPT and press Enter."""
        if not await self.check_running():
            return {"status": "error", "error": "ChatGPT is not running", "timestamp": _now_iso()}

        # small pacing to avoid UI thrash
        await asyncio.sleep(self.cfg.desktop_inter_send_delay_s)

        # Escape quotes and backslashes for AppleScript string literal
        msg = message.replace("\\", "\\\\").replace('"', '\\"')
        app = self.cfg.app_name
        script = f"""
        tell application "{app}" to activate
        delay 0.4
        tell application "System Events"
            tell process "{app}"
                set frontmost to true
                try
                    if (exists text area 1 of window 1) then
                        set targetField to text area 1 of window 1
                    else
                        set targetField to text area 1 of scroll area 2 of group 2 ¬
                            of splitter group 1 of group 1 of window "{app}"
                    end if
                    click targetField
                    delay 0.2
                    keystroke "{msg}"
                    delay 0.25
                    key code 36
                    return "success"
                on error errMsg
                    return "error: " & errMsg
                end try
            end tell
        end tell
        """
        try:
            code, out, err = await asyncio.wait_for(
                self._osascript(script), timeout=self.cfg.desktop_script_timeout_s,
            )
        except TimeoutError:
            logger.warning("Send failed: osascript timeout after %.1fs", self.cfg.desktop_script_timeout_s)
            return {"status": "error", "error": f"osascript timeout after {self.cfg.desktop_script_timeout_s:.1f}s", "timestamp": _now_iso()}
        if code == 0 and out.strip().startswith("success"):
            logger.info("Message sent to desktop (%s chars)", len(message))
            if persistence_store:
                with contextlib.suppress(Exception):
                    meta = {
                        "chatgpt": True,
                        "diagnostic": message.startswith("[diagnostic]"),
                    }
                    persistence_store.record_chat_message(
                        "user",
                        message,
                        conversation_id="chatgpt",
                        meta=meta,
                    )
            return {"status": "success", "timestamp": _now_iso()}
        error_msg = out.strip() or err.strip() or "unknown error"
        logger.warning("Send failed: %s", error_msg)
        return {"status": "error", "error": error_msg, "timestamp": _now_iso()}

    async def copy_last_response_to_clipboard(self) -> dict[str, Any]:
        """Click the last message and copy to clipboard via Cmd+C."""
        app = self.cfg.app_name
        script = f"""
        tell application "System Events"
            tell process "{app}"
                try
                    set theWin to window 1
                    set candidate to text area 1 of theWin
                    try
                        click candidate
                        delay 0.2
                        keystroke "a" using command down
                        delay 0.1
                        keystroke "c" using command down
                        return "success"
                    on error errMsg
                        return "error: " & errMsg
                    end try
                on error errMsg
                    return "error: " & errMsg
                end try
            end tell
        end tell
        """
        try:
            code, out, err = await asyncio.wait_for(self._osascript(script), timeout=10)
        except TimeoutError:
            return {"status": "error", "error": "osascript timeout after 10.0s", "timestamp": _now_iso()}
        if not (code == 0 and "success" in out):
            return {"status": "error", "error": out or err, "timestamp": _now_iso()}

        # Read clipboard
        proc = await asyncio.create_subprocess_exec(
            "pbpaste", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        out_b, err_b = await proc.communicate()
        if proc.returncode == 0:
            return {
                "status": "success",
                "response": (out_b or b"").decode(),
                "timestamp": _now_iso(),
            }
        return {"status": "error", "error": (err_b or b"").decode(), "timestamp": _now_iso()}

    async def get_last_response(self) -> dict[str, Any]:
        """Convenience wrapper that copies the last response and records it."""
        res = await self.copy_last_response_to_clipboard()
        if res.get("status") == "success" and persistence_store:
            with contextlib.suppress(Exception):
                persistence_store.record_chat_message(
                    "assistant",
                    res["response"],
                    conversation_id="desktop",
                )  # type: ignore[index]
        return res

    async def export_conversation_to_file(self, path: str) -> dict[str, Any]:
        """Best-effort export: uses clipboard from the currently focused message list."""
        res = await self.copy_last_response_to_clipboard()
        if res.get("status") != "success":
            return res
        try:
            # Avoid synchronous file APIs in user-flow: use aiofiles if present.
            text = res.get("response", "")
            if aiofiles_mod:
                async with aiofiles_mod.open(  # type: ignore[attr-defined]
                    path, "w", encoding="utf-8",
                ) as f:
                    await f.write(text)  # type: ignore[union-attr]
            else:
                # tiny write, acceptable fallback
                pathlib.Path(path).write_text(text, encoding="utf-8")
            return {"status": "success", "file": path, "timestamp": _now_iso()}
        except OSError as exc:
            return {"status": "error", "error": str(exc), "timestamp": _now_iso()}


# Global instance
_CLIENT = ChatGPTDesktopClient()


async def send_to_chatgpt(message: str) -> dict[str, Any]:
    """Public helper used elsewhere."""
    return await _CLIENT.send_message(message)


async def check_chatgpt_running() -> bool:
    """Public helper used elsewhere."""
    return await _CLIENT.check_running()


# ---- Guard wrapper replacing undefined apply helper -----------------------
async def mp_apply_last_reply_to_files() -> dict[str, Any]:
    """Shim for older code that expects `apply_last_code_blocks_to_files`.

    If a global callable by that exact name exists, we call it; otherwise
    return a structured error so callers can degrade gracefully.
    """
    helper = globals().get("apply_last_code_blocks_to_files")
    if callable(helper):
        res = helper(
            default_dir=".",
            default_filename="applied_patch.py",
            open_in_editor="Cursor",
        )
        return await res if inspect.isawaitable(res) else res  # type: ignore[no-any-return]
    return {"status": "error", "error": "apply_last_code_blocks_to_files not found"}


if __name__ == "__main__":

    async def _demo() -> None:
        ok = await check_chatgpt_running()
        print("Desktop running:", ok)
        if ok:
            resp = await send_to_chatgpt("Hello from Monkey Paw runtime.")
            print("Send:", resp)

    asyncio.run(_demo())
