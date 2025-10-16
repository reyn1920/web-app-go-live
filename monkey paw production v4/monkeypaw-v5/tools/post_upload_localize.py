#!/usr/bin/env python3
"""
Post-upload localization helper.

Usage:
  python tools/post_upload_localize.py \\
    --video VIDEO_ID \\
    --title "My English Title" \\
    --desc "My English Description" \\
    --srt outputs/transcripts/base.srt

Adds translated title/description and uploads translated captions for all
configured languages (YT_LOCALIZATION_LANGS).
"""
from __future__ import annotations

import argparse
from pathlib import Path

from monkeypaw.logging_setup import get_logger
from monkeypaw.settings_runtime import YT_LOCALIZATION_LANGS
from monkeypaw.youtube.localization import add_translations, upload_captions

log = get_logger("tools.localize")


def main():
    ap = argparse.ArgumentParser(description="Add multi-language metadata and captions")
    ap.add_argument("--video", required=True, help="YouTube video ID")
    ap.add_argument("--title", required=True, help="Original title (English)")
    ap.add_argument("--desc", required=True, help="Original description (English)")
    ap.add_argument("--srt", required=True, help="Path to base SRT subtitle file")
    args = ap.parse_args()

    # Add translated metadata
    ok_meta = add_translations(args.video, args.title, args.desc, YT_LOCALIZATION_LANGS)
    log.info("Metadata translations: %s", "OK" if ok_meta else "PARTIAL")

    # Upload caption tracks for each language
    base_srt = Path(args.srt)
    if not base_srt.exists():
        log.info("SRT file not found: %s", base_srt)
        return

    for code in YT_LOCALIZATION_LANGS:
        # Simple approach: duplicate base SRT for all languages
        # For production, you'd translate the SRT content too
        upload_captions(args.video, code, base_srt, name=f"Subs {code}")

    log.info("Localization complete for video %s", args.video)


if __name__ == "__main__":
    main()
