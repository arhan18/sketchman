"""Headless-Chrome scene renderer.

Clips are captured one frame at a time and piped straight into ffmpeg, so an
8-10 minute episode never writes thousands of PNGs to disk. Animation is fully
deterministic: clips carry explicit start/end times, and runtime.seek(t)
pauses every CSS animation in the page and sets its currentTime, so frame N is
byte-identical across machines and reruns (unlike wall-clock playback).

A clip is a dict:
    scene     scene kind, e.g. "chart" (see scenes/<style>.html)
    props     scene-specific data dict
    caption   burned-in subtitle text for this clip
    narr      narration spoken during this clip (used for audio only)
    duration  spoken length in seconds, measured from the TTS output
"""
from __future__ import annotations

import json
import os
import subprocess
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Tuple

import binpath

HERE = os.path.dirname(os.path.abspath(__file__))
SCENES_DIR = os.path.join(HERE, "scenes")
WORK = os.path.join(HERE, "work")

FPS = 15
LONG_SIZE = (1280, 720)
SHORT_SIZE = (720, 1280)

LOG_LEVELS = {"debug": 0, "info": 1, "warn": 2, "error": 3, "fail": 4}
CURRENT_LOG_LEVEL = LOG_LEVELS.get(os.getenv("LOG_LEVEL", "info").lower(), 1)


def _log(level: str, msg: str, **kwargs) -> None:
    if LOG_LEVELS.get(level, 1) >= CURRENT_LOG_LEVEL:
        kv = " ".join(f"{k}={v}" for k, v in kwargs.items())
        ts = datetime.utcnow().isoformat() + "Z"
        print(f"[{ts}] [{level.upper()}] {msg} {kv}".strip(), flush=True)


def with_timing(clips: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Attach start/end seconds to each clip from its duration."""
    out: List[Dict[str, Any]] = []
    t = 0.0
    for clip in clips:
        item = dict(clip)
        item["start"] = round(t, 3)
        t += max(0.2, float(item.get("duration", 1.0)))
        item["end"] = round(t, 3)
        out.append(item)
    return out


def _read(name: str) -> str:
    with open(os.path.join(SCENES_DIR, name)) as f:
        return f.read()


def page_html(series, clips: Sequence[Dict[str, Any]], size: Tuple[int, int]) -> str:
    """Build the self-contained HTML document Chromium will render."""
    payload = {
        "series": {
            "id": series.id,
            "host": series.host,
            "show": series.show,
            "background": series.background,
            "surface": series.surface,
            "ink": series.ink,
            "accent": series.accent,
            "muted": series.muted,
            "signoff": series.signoff,
        },
        "size": {"w": size[0], "h": size[1]},
        "fps": FPS,
        "clips": with_timing(clips),
    }
    html = _read(f"{series.style}.html")
    html = html.replace("/*__BASECSS__*/", _read("base.css"))
    html = html.replace("/*__RUNTIME__*/", _read("runtime.js"))
    if "/*__FLAT__*/" in html:
        html = html.replace("/*__FLAT__*/", _read("flat.js"))
    return html.replace("/*__PAYLOAD__*/", json.dumps(payload))


def concat_audio(parts: Sequence[str], out_path: str) -> str:
    """Join per-sentence narration into one AAC track.

    Re-encodes instead of stream-copying because consecutive sentences can come
    from different TTS engines (Kokoro wav->mp3 vs Edge mp3) with different
    sample rates; stream copy would glitch at those joins.
    """
    if not parts:
        raise ValueError("concat_audio: no audio parts")
    if len(parts) == 1:
        subprocess.run([binpath.FFMPEG, "-y", "-v", "error", "-i", parts[0],
                        "-c:a", "aac", "-b:a", "192k", out_path], check=True)
        return out_path
    os.makedirs(WORK, exist_ok=True)
    listing = os.path.join(WORK, "audio-list.txt")
    with open(listing, "w") as f:
        for part in parts:
            f.write(f"file '{os.path.abspath(part)}'\n")
    subprocess.run([binpath.FFMPEG, "-y", "-v", "error", "-f", "concat",
                    "-safe", "0", "-i", listing, "-c:a", "aac", "-b:a", "192k",
                    out_path], check=True)
    return out_path


def render(series, clips: Sequence[Dict[str, Any]], audio_path: str,
           out_path: str, size: Tuple[int, int] = LONG_SIZE,
           fps: int = FPS, progress_every: int = 300) -> str:
    """Render clips + audio into a single mp4."""
    from playwright.sync_api import sync_playwright

    if not clips:
        raise ValueError("render: no clips")
    os.makedirs(WORK, exist_ok=True)
    page_path = os.path.join(WORK, "scene.html")
    with open(page_path, "w") as f:
        f.write(page_html(series, clips, size))

    total = sum(max(1, int(round(float(c["duration"]) * fps))) for c in clips)
    cmd = [
        binpath.FFMPEG, "-y", "-v", "error",
        "-f", "image2pipe", "-framerate", str(fps), "-i", "-",
        "-i", audio_path,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-r", str(fps),
        "-c:a", "aac", "-b:a", "192k", "-shortest",
        out_path,
    ]
    _log("info", "render start", style=series.style, series=series.id,
         clips=len(clips), frames=total, size=f"{size[0]}x{size[1]}")
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    started = time.time()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(args=[
                "--force-color-profile=srgb",
                "--disable-lcd-text",
                "--hide-scrollbars",
                "--font-render-hinting=none",
            ])
            page = browser.new_page(
                viewport={"width": size[0], "height": size[1]},
                device_scale_factor=1,
            )
            page.goto(f"file://{page_path}")
            page.wait_for_function("window.SKETCHMAN_READY === true", timeout=30000)
            for i in range(total):
                page.evaluate("t => window.seek(t)", i / fps)
                proc.stdin.write(page.screenshot(type="png"))
                if progress_every and (i + 1) % progress_every == 0:
                    rate = (i + 1) / max(time.time() - started, 1e-6)
                    _log("info", "frames", done=i + 1, total=total,
                         render_fps=round(rate, 1),
                         eta_s=int((total - i - 1) / max(rate, 1e-6)))
            browser.close()
    finally:
        if proc.stdin and not proc.stdin.closed:
            proc.stdin.close()
    rc = proc.wait()
    if rc != 0:
        raise RuntimeError(f"ffmpeg failed (exit {rc}) while encoding {out_path}")
    _log("info", "render done", out=out_path,
         seconds=round(time.time() - started, 1))
    return out_path


def capture_still(series, clip: Dict[str, Any], out_png: str,
                  size: Tuple[int, int] = LONG_SIZE, t: float = 0.0) -> str:
    """Single-frame capture (scene design review / thumbnails)."""
    from playwright.sync_api import sync_playwright

    os.makedirs(WORK, exist_ok=True)
    page_path = os.path.join(WORK, "still.html")
    timed = with_timing([dict(clip, duration=max(1.0, float(clip.get("duration", 1.0))))])
    with open(page_path, "w") as f:
        f.write(page_html(series, timed, size))
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--force-color-profile=srgb",
                                          "--hide-scrollbars"])
        page = browser.new_page(viewport={"width": size[0], "height": size[1]},
                                device_scale_factor=1)
        page.goto(f"file://{page_path}")
        page.wait_for_function("window.SKETCHMAN_READY === true", timeout=30000)
        page.evaluate("t => window.seek(t)", t)
        page.screenshot(path=out_png, type="png")
        browser.close()
    return out_png
