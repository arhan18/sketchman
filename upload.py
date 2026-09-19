#!/usr/bin/env python3
"""Upload a rendered video to YouTube.

Creds come from env: YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET,
YOUTUBE_REFRESH_TOKEN.  (These are GitHub Actions secrets on CI.)

Usage:
  python upload.py video.mp4 meta.json [--short] [--private] [--thumbnail f.png] [--force]
  python upload.py --verify            # check the refresh token + channel (1 quota unit)

Behavior:
  * DRY_RUN=1 prints what would happen and exits 0.
  * The one-upload-per-day guard reads state.py; pass --force to override.
  * invalid_grant -> precise diagnostics + re-auth pointer, exit 2 (no retries).
  * quota / rate-limit -> retries with exponential backoff (never burns quota
    chasing a 403 after it has already failed).
  * Thumbnail failures (common on unverified channels, 403) are non-fatal.
  * Never logs or prints secrets.
  * Structured logging for observability.
"""
import argparse
import json
import os
import sys
import time
import traceback
from datetime import datetime

import state

RETRYABLE_REASONS = {
    "quotaExceeded": "quota",
    "userRateLimitExceeded": "quota",
    "dailyLimitExceeded": "quota",
    "rateLimitExceeded": "quota",
    "backendError": "backend",
    "internalError": "backend",
    "failedPrecondition": "backend",
}
RETRYABLE_STATUS = (429, 500, 502, 503, 504)

# Structured logging
LOG_LEVELS = {"debug": 0, "info": 1, "warn": 2, "error": 3, "fail": 4}
CURRENT_LOG_LEVEL = LOG_LEVELS.get(os.getenv("LOG_LEVEL", "info").lower(), 1)


def _log(level: str, msg: str, **kwargs) -> None:
    """Structured logging with optional key-value pairs."""
    if LOG_LEVELS.get(level, 1) >= CURRENT_LOG_LEVEL:
        kv = " ".join(f"{k}={v}" for k, v in kwargs.items())
        ts = datetime.utcnow().isoformat() + "Z"
        print(f"[{ts}] [{level.upper()}] {msg} {kv}".strip(), flush=True)


def _p(level: str, msg: str) -> None:
    """Legacy compatibility."""
    _log(level, msg)


def _error_reason(err) -> str:
    reason = getattr(err, "_get_reason", None)
    if callable(reason):
        return reason()
    for m in ("reason", "message", "status"):
        if getattr(err, m, None):
            return str(getattr(err, m))
    return str(err)


def _retry_after(err) -> int | None:
    try:
        ra = err.resp.get("retry-after") if err.resp else None
        if ra:
            return min(int(ra), 600)
    except Exception:
        pass
    return None


def _retry_delay(err, attempt: int) -> int | None:
    """Seconds to sleep, or None if the error is not worth retrying."""
    status = getattr(err, "resp", None).status if getattr(err, "resp", None) else None
    reason = _error_reason(err)
    ra = _retry_after(err)
    kind = RETRYABLE_REASONS.get(reason, "backend" if status in RETRYABLE_STATUS else None)
    if kind is None:
        return None
    if kind == "quota":
        return max(ra or 0, min(60 * (2 ** attempt), 600))
    return max(ra or 0, min(5 * (2 ** attempt), 300))


def _reauth_instructions() -> str:
    return (
        "\nRE-AUTH NEEDED — your YouTube refresh token is dead. Two options:\n"
        "  1) Fastest: run the one-time walkthrough locally ->\n"
        "       python reauth.py --client-id $YOUTUBE_CLIENT_ID "
        "--client-secret $YOUTUBE_CLIENT_SECRET\n"
        "     (you approve the Google consent screen yourself, then it prints the "
        "exact `gh secret set` commands).\n"
        "  2) If tokens keep dying every ~7 days: your OAuth consent screen is still "
        "in 'Testing' mode.\n"
        "     Console.cloud.google.com -> APIs & Services -> OAuth consent screen -> "
        "'Publish app' (Production).\n"
        "     Testing-mode refresh tokens expire after 7 days; that is the classic "
        "cause of `invalid_grant`.\n"
        "  Also possible: the token wasn't used for >6 months, was revoked, or the "
        "client id/secret changed."
    )


def _load_creds() -> tuple[str, str, str]:
    missing = [k for k in ("YOUTUBE_CLIENT_ID", "YOUTUBE_CLIENT_SECRET",
                           "YOUTUBE_REFRESH_TOKEN") if not os.getenv(k)]
    if missing:
        _log("fail", "Missing env vars", vars=", ".join(missing))
        sys.exit(2)
    return (os.environ["YOUTUBE_CLIENT_ID"], os.environ["YOUTUBE_CLIENT_SECRET"],
            os.environ["YOUTUBE_REFRESH_TOKEN"])


def build_creds():
    from google.oauth2.credentials import Credentials
    cid, secret, rt = _load_creds()
    return Credentials(
        None,
        refresh_token=rt,
        client_id=cid,
        client_secret=secret,
        token_uri="https://oauth2.googleapis.com/token",
        scopes=["https://www.googleapis.com/auth/youtube.upload",
                "https://www.googleapis.com/auth/youtube.readonly"],
    )


def refresh(creds):
    from google.auth.transport.requests import Request
    try:
        creds.refresh(Request())
        _log("debug", "OAuth token refreshed successfully")
        return creds
    except Exception as e:
        msg = str(e)
        if "invalid_grant" in msg or "Token has been expired" in msg:
            _log("fail", "OAuth refresh failed: invalid_grant")
            print(_reauth_instructions())
        else:
            _log("fail", "OAuth refresh failed", error=msg)
        sys.exit(2)


def build_yt(creds):
    from googleapiclient.discovery import build
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def verify_creds():
    """Check the token actually works and see the channel. 1 quota unit."""
    _log("info", "verify: checking refresh token + channel...")
    creds = refresh(build_creds())
    yt = build_yt(creds)
    res = yt.channels().list(part="snippet,statistics", mine=True).execute()
    items = res.get("items", [])
    if not items:
        _log("fail", "verify: token is valid but no channel is visible. "
                   "Is the Google account logged into YouTube connected to a "
                   "channel? (sign-in / channel creation may be needed)")
        sys.exit(1)
    ch = items[0]
    _log("info", "verify: channel OK", title=ch['snippet']['title'],
         channel_id=ch['id'], subscribers=ch['statistics'].get('subscriberCount', '?'))
    # Track the 1 quota unit used for verification
    state.record_quota_usage(1)
    return ch


def _upload(yt, title: str, description: str, tags: str, video: str, max_retries: int):
    """Resumable insert with quota-aware retries. Returns response resource."""
    from googleapiclient.http import MediaFileUpload
    from googleapiclient.errors import HttpError
    body = {"snippet": {"title": title[:100], "description": description[:5000],
                        "tags": [t.strip() for t in (tags or "").split(",") if t.strip()],
                        "categoryId": "22"},
            "status": {"privacyStatus": "private", "madeForKids": False}}
    attempt = 0
    while True:
        try:
            req = yt.videos().insert(
                part="snippet,status", body=body,
                media_body=MediaFileUpload(video, resumable=True))
            resp = None
            while resp is None:
                status, resp = req.next_chunk(num_retries=2)
                if status:
                    _log("info", "upload progress", percent=int(status.progress() * 100))
            _log("info", "upload completed", video_id=resp["id"])
            return resp
        except HttpError as e:
            if attempt >= max_retries:
                _log("error", "upload failed after retries", attempts=max_retries,
                     reason=_error_reason(e))
                raise
            delay = _retry_delay(e, attempt)
            if delay is None:
                reason = _error_reason(e)
                if e.resp and e.resp.status in (401, 403) and \
                        any(x in reason for x in ("auth", "forbidden", "denied")):
                    _log("fail", "auth error during upload", reason=reason)
                    print(_reauth_instructions())
                    sys.exit(2)
                _log("error", "non-retryable upload error", reason=reason)
                raise
            _log("warn", "retrying upload", attempt=attempt + 1, max_retries=max_retries,
                 delay=delay, status=getattr(e.resp, 'status', None), reason=_error_reason(e))
            time.sleep(delay)
            attempt += 1


def set_thumbnail(yt, video_id: str, thumb_path: str) -> None:
    """Best-effort thumbnail. Unverified channels can't set custom thumbnails
    (403) — log and keep going, the video stays live."""
    from googleapiclient.http import MediaFileUpload
    try:
        yt.thumbnails().set(videoId=video_id,
                            media_body=MediaFileUpload(thumb_path)).execute()
        _log("info", "THUMBNAIL SET", video_id=video_id)
    except Exception as e:
        msg = _error_reason(e)
        if "403" in str(e) or "forbidden" in msg.lower():
            _log("warn", "THUMBNAIL SKIPPED (non-fatal): custom thumbnails need a "
                       "verified channel", video_id=video_id)
        else:
            _log("warn", "THUMBNAIL SKIPPED (non-fatal)", video_id=video_id, error=msg)
        # Non-fatal: don't exit, just continue


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true",
                    help="check refresh token + channel, then exit")
    ap.add_argument("video", nargs="?")
    ap.add_argument("meta", nargs="?")
    ap.add_argument("--short", action="store_true")
    ap.add_argument("--private", action="store_true")
    ap.add_argument("--thumbnail", default=None)
    ap.add_argument("--force", action="store_true",
                    help="ignore the 1-upload-per-day guard")
    ap.add_argument("--max-retries", type=int, default=3)
    a = ap.parse_args()

    if a.verify:
        verify_creds()
        return

    if not a.video or not a.meta:
        ap.error("video and meta.json are required (or use --verify)")

    meta = json.load(open(a.meta))
    title = meta["title"] + (" #Shorts" if a.short else "")
    fmt = "short" if a.short else "long"

    if os.getenv("DRY_RUN") == "1":
        _log("info", "DRY_RUN: would upload", video=a.video, title=title)
        return

    # Quota guard: one upload per format per calendar day unless --force.
    if not a.force and state.already_uploaded(fmt):
        _log("warn", "already uploaded this format today; skipping (1/day guard)",
             format=fmt)
        _log("info", "Use --force to override")
        sys.exit(0)

    # Additional quota check: don't upload if we'd exceed daily quota
    if not a.force and not state.can_upload():
        remaining = state.quota_remaining()
        _log("warn", "insufficient YouTube quota remaining", remaining=remaining,
             needed=1600)
        _log("info", "Use --force to override")
        sys.exit(0)

    _log("info", "starting upload", title=title, video=a.video, format=fmt)
    creds = refresh(build_creds())
    yt = build_yt(creds)
    try:
        resp = _upload(yt, title, meta.get("description", ""),
                       meta.get("tags", ""), a.video, a.max_retries)
        vid = resp["id"]
        _log("info", "UPLOADED", url=f"https://youtu.be/{vid}")

        thumb = a.thumbnail or meta.get("thumbnail")
        if thumb and os.path.exists(thumb):
            set_thumbnail(yt, vid, thumb)

        topic_key = os.path.basename(a.video).rsplit(".mp4", 1)[0]
        state.record_upload(fmt, topic_key, f"https://youtu.be/{vid}")
        _log("info", "upload recorded in state", topic_key=topic_key, format=fmt)
    except Exception as e:
        _log("fail", "upload failed", error=str(e))
        if os.getenv("DEBUG"):
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()