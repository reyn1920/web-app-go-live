#!/usr/bin/env python3
"""
YouTube Thumbnail A/B Testing Tool (FREE)

Automatically swaps between two thumbnail variants at regular intervals
to test which performs better. Monitor CTR in YouTube Analytics.

Usage:
  python tools/yt_thumb_ab.py \\
    --video VIDEO_ID \\
    --a outputs/thumbs/variant_a.jpg \\
    --b outputs/thumbs/variant_b.jpg \\
    --period 3600

This will swap thumbnails every hour (3600 seconds).
Press Ctrl+C to stop.
"""
from __future__ import annotations

import argparse
import importlib
import time
from pathlib import Path

from monkeypaw.logging_setup import get_logger

log = get_logger("tools.thumb_ab")


def _get_youtube_service():
    """Get YouTube API service using existing credentials."""
    try:
        discovery = importlib.import_module("googleapiclient.discovery")
        try:
            from app_backend.google_auth import get_user_credentials  # type: ignore

            creds = get_user_credentials(readonly=False)
        except ImportError:
            import os

            from google.oauth2.credentials import Credentials  # type: ignore

            creds = Credentials(
                token=os.getenv("YOUTUBE_ACCESS_TOKEN"),
                refresh_token=os.getenv("YOUTUBE_REFRESH_TOKEN"),
                token_uri="https://oauth2.googleapis.com/token",
                client_id=os.getenv("YOUTUBE_CLIENT_ID"),
                client_secret=os.getenv("YOUTUBE_CLIENT_SECRET"),
            )
        return discovery.build(
            "youtube", "v3", credentials=creds, cache_discovery=False,
        )
    except Exception as e:
        log.info("Failed to create YouTube service: %s", repr(e))
        return None


def set_thumbnail(video_id: str, image_path: Path) -> bool:
    """Upload a thumbnail for the specified video."""
    try:
        http = importlib.import_module("googleapiclient.http")
        svc = _get_youtube_service()
        if not svc:
            return False
        media = http.MediaFileUpload(str(image_path), mimetype="image/jpeg")
        svc.thumbnails().set(videoId=video_id, media_body=media).execute()
        log.info("Thumbnail set: %s -> %s", video_id, image_path.name)
        return True
    except Exception as e:
        log.info("Failed to set thumbnail: %s", repr(e))
        return False


def main():
    ap = argparse.ArgumentParser(description="A/B test YouTube thumbnails")
    ap.add_argument("--video", required=True, help="YouTube video ID")
    ap.add_argument("--a", required=True, help="Path to thumbnail variant A")
    ap.add_argument("--b", required=True, help="Path to thumbnail variant B")
    ap.add_argument(
        "--period",
        type=int,
        default=3600,
        help="Seconds between swaps (default: 3600 = 1 hour)",
    )
    args = ap.parse_args()

    a, b = Path(args.a), Path(args.b)
    if not a.exists():
        log.info("Thumbnail A not found: %s", a)
        return
    if not b.exists():
        log.info("Thumbnail B not found: %s", b)
        return

    log.info("Starting A/B test for video %s", args.video)
    log.info("Variant A: %s", a)
    log.info("Variant B: %s", b)
    log.info("Swap period: %d seconds", args.period)
    log.info("Press Ctrl+C to stop")

    try:
        while True:
            log.info("Setting thumbnail A...")
            set_thumbnail(args.video, a)
            time.sleep(args.period)

            log.info("Setting thumbnail B...")
            set_thumbnail(args.video, b)
            time.sleep(args.period)
    except KeyboardInterrupt:
        log.info("A/B test stopped by user")


if __name__ == "__main__":
    main()
