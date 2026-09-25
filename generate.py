#!/usr/bin/env python3
"""Sketchman v3: JSON scripts -> per-series Chrome scenes + natural voice.

One script sentence becomes one TTS clip, one measured duration, one burned-in
caption and one continuous frame stream piped into ffmpeg. Frames are rendered
deterministically (renderer.seek), so reruns are identical.

Usage: python generate.py --format long|short [--script arjun/quiet-ledger]
"""
import argparse
import json
import os
import subprocess
from datetime import datetime

import binpath
import renderer
import script as script_mod
import series as series_mod
import voice

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "work")

LOG_LEVELS = {"debug": 0, "info": 1, "warn": 2, "error": 3, "fail": 4}
CURRENT_LOG_LEVEL = LOG_LEVELS.get(os.getenv("LOG_LEVEL", "info").lower(), 1)


def _log(level: str, msg: str, **kwargs) -> None:
    if LOG_LEVELS.get(level, 1) >= CURRENT_LOG_LEVEL:
        kv = " ".join(f"{k}={v}" for k, v in kwargs.items())
        ts = datetime.utcnow().isoformat() + "Z"
        print(f"[{ts}] [{level.upper()}] {msg} {kv}".strip(), flush=True)


def probe_dur(path: str) -> float:
    r = subprocess.run([binpath.FFPROBE, "-v", "error", "-show_entries",
                        "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def narrate(clips, series_id: str) -> list:
    """Speak every clip, then record its real duration."""
    os.makedirs(WORK, exist_ok=True)
    parts = []
    for i, clip in enumerate(clips):
        path = os.path.join(WORK, f"narration-{i:04d}.mp3")
        voice.tts_sync(clip["narr"], path, series_id=series_id)
        clip["duration"] = probe_dur(path)
        parts.append(path)
    return parts


def output_name(fmt: str, script) -> str:
    slug = os.path.basename(script["_key"])
    return f"{fmt}-{script['series']}-{slug}"


def make_thumbnail(script, series, base: str) -> str:
    thumb_spec = script.get("thumbnail") or {}
    clip = {
        "scene": thumb_spec.get("scene", script["shots"][0]["scene"]),
        "props": thumb_spec.get("props", script["shots"][0].get("props", {})),
        "caption": thumb_spec.get("headline", script["title"]),
        "duration": 3.0,
    }
    return renderer.capture_still(series, clip, f"{base}-thumb.png", t=1.2)


def build(fmt: str, script_key: str = None) -> str:
    script = script_mod.pick(fmt, script_key)
    series = series_mod.get(script["series"])
    _log("info", "building", format=fmt, series=series.id, script=script["_key"],
         words=script_mod.word_count(script))

    clips = script_mod.clips(script)
    repeats = script_mod.check_variety(script)
    if repeats:
        for line in repeats:
            _log("warn", "repeated visual", script=script["_key"], detail=line)
    parts = narrate(clips, series.id)
    size = renderer.SHORT_SIZE if fmt == "short" else renderer.LONG_SIZE

    base = output_name(fmt, script)
    audio = renderer.concat_audio(parts, os.path.join(WORK, "audio.m4a"))
    out = renderer.render(series, clips, audio, f"{base}.mp4", size=size)

    thumb = make_thumbnail(script, series, base)
    duration = probe_dur(out)
    if duration < 5:
        raise RuntimeError(f"{out} is only {duration:.1f}s — script too short")
    if os.path.getsize(out) < 50_000:
        raise RuntimeError(f"{out} is suspiciously small")

    meta = {
        "title": script["title"],
        "file": f"{base}.mp4",
        "thumbnail": os.path.basename(thumb),
        "description": script.get("description", ""),
        "tags": script.get("tags", ""),
    }
    meta_path = f"{base}.json"
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2, sort_keys=True)

    manifest = {
        "format": fmt,
        "series": series.id,
        "script": script["_key"],
        "video": os.path.basename(out),
        "meta": os.path.basename(meta_path),
        "thumbnail": os.path.basename(thumb),
        "rendered_at": datetime.utcnow().isoformat() + "Z",
        "duration_seconds": round(duration, 2),
        "file_size": os.path.getsize(out),
    }
    tmp = "latest.json.tmp"
    with open(tmp, "w") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
    os.replace(tmp, "latest.json")

    _log("info", "build done", video=out, seconds=round(duration, 1),
         clips=len(clips))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--format", choices=["long", "short"], required=True)
    ap.add_argument("--script", default=None,
                    help="script key or filename slug, e.g. arjun/quiet-ledger")
    args = ap.parse_args()
    build(args.format, args.script)


if __name__ == "__main__":
    main()
