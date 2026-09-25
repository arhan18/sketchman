"""Voice v4: free human-sounding TTS first, Edge fallback.
Primary: Kokoro-82M via kokoro-onnx (Apache 2.0, local, $0).
Voice am_adam @0.93 speed = calm male storyteller, closest free match
to the Ink Explainer reference (slow, intimate, ~135 wpm).
Fallback: Edge ChristopherNeural if kokoro model/deps are missing, OR
if the espeak-ng phonemizer hard-fails (probing in a throwaway subprocess
catches native espeak-ng exit(1) that no Python except can see), so
CI/local never breaks. Indian-money text normalized so the
voice never reads symbols literally.
"""
import asyncio
import os
import re
import subprocess
import sys
import urllib.request
import time
from datetime import datetime
from typing import Optional

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(HERE, "models")
ONNX_URL = ("https://github.com/thewh1teagle/kokoro-onnx/"
            "releases/download/model-files-v1.0/kokoro-v1.0.onnx")
VOICES_URL = ("https://github.com/thewh1teagle/kokoro-onnx/"
              "releases/download/model-files-v1.0/voices-v1.0.bin")

KOKORO_LANG = "en-us"

# Edge's socket can stall indefinitely on a bad connection, so every call is
# hard-capped; the retry loop below then does its job instead of hanging the run.
EDGE_TIMEOUT = int(os.getenv("EDGE_TIMEOUT", "45"))

# One TTS identity per series id (see series.py). Kokoro runs locally and
# costs nothing; Edge is the fallback and carries the Indian-English accent,
# so a fallback episode still sounds like the same country. Only two en-IN
# Edge voices exist, so arjun/kabir share Prabhat and separate by rate+pitch.
DEFAULT_PROFILE = "default"
VOICE_PROFILES = {
    "default": {
        "kokoro": "am_adam", "speed": 0.93,
        "edge": "en-US-ChristopherNeural", "edge_rate": "-8%", "edge_pitch": "+0Hz",
    },
    "arjun": {
        "kokoro": "am_adam", "speed": 0.93,
        "edge": "en-IN-PrabhatNeural", "edge_rate": "-6%", "edge_pitch": "+0Hz",
    },
    "mira": {
        "kokoro": "af_bella", "speed": 0.97,
        "edge": "en-IN-NeerjaNeural", "edge_rate": "-4%", "edge_pitch": "+2Hz",
    },
    "kabir": {
        "kokoro": "am_michael", "speed": 0.90,
        "edge": "en-IN-PrabhatNeural", "edge_rate": "-10%", "edge_pitch": "-6Hz",
    },
}


def _profile(series_id: Optional[str]) -> dict:
    """Voice settings for a series id, falling back to the default narrator."""
    return VOICE_PROFILES.get(series_id or DEFAULT_PROFILE,
                              VOICE_PROFILES[DEFAULT_PROFILE])

_kokoro = None
_kokoro_probe_ok = None   # None=unknown, True/False cached once per process

# Structured logging
LOG_LEVELS = {"debug": 0, "info": 1, "warn": 2, "error": 3, "fail": 4}
CURRENT_LOG_LEVEL = LOG_LEVELS.get(os.getenv("LOG_LEVEL", "info").lower(), 1)


def _log(level: str, msg: str, **kwargs) -> None:
    """Structured logging with optional key-value pairs."""
    if LOG_LEVELS.get(level, 1) >= CURRENT_LOG_LEVEL:
        kv = " ".join(f"{k}={v}" for k, v in kwargs.items())
        ts = datetime.utcnow().isoformat() + "Z"
        print(f"[{ts}] [{level.upper()}] {msg} {kv}".strip(), flush=True)


def normalize(t: str) -> str:
    t = t.replace("₹", " rupees ")
    t = re.sub(r"Rs\.?\s*([\d,]+)", r"\1 rupees", t)
    t = t.replace("%", " percent ")
    t = t.replace("&", " and ")
    t = re.sub(r"\b([A-Z]{2,})\b", lambda m: " ".join(m.group(1)), t)  # SIP -> S I P
    t = re.sub(r"\s+", " ", t).strip()
    return t


def pace(text: str) -> str:
    """Short sentences + explicit pauses. Ink-style: never a wall of text.
    ' ... ' renders as a real pause in both Kokoro and Edge."""
    parts = re.split(r"(?<=[.!?])\s+", normalize(text))
    return " ... ".join(p for p in parts if p)


def _download(url: str, dest: str, tries: int = 3) -> None:
    """Streaming download to <dest>.part, atomic rename on success. Retries."""
    part = dest + ".part"
    for attempt in range(1, tries + 1):
        try:
            with urllib.request.urlopen(url, timeout=120) as r, open(part, "wb") as f:
                total = int(r.headers.get("Content-Length") or 0)
                _log("debug", "downloading model", url=url, dest=dest,
                     size_mb=round(total / 1024 / 1024, 1) if total else "unknown")
                while True:
                    chunk = r.read(1 << 16)
                    if not chunk:
                        break
                    f.write(chunk)
            os.replace(part, dest)
            _log("info", "model downloaded", dest=dest)
            return
        except Exception as e:
            if os.path.exists(part):
                try:
                    os.remove(part)
                except Exception:
                    pass
            if attempt == tries:
                _log("fail", "model download failed", url=url, error=str(e))
                raise RuntimeError(f"download failed after {tries} tries: {e}")
            _log("warn", "download retry", attempt=attempt, max_tries=tries,
                 error=str(e), wait_seconds=5 * attempt)
            time.sleep(5 * attempt)


def _ensure_models() -> tuple[str, str]:
    os.makedirs(MODEL_DIR, exist_ok=True)
    onnx_p = os.path.join(MODEL_DIR, "kokoro-v1.0.onnx")
    voices_p = os.path.join(MODEL_DIR, "voices-v1.0.bin")
    for path, url in ((onnx_p, ONNX_URL), (voices_p, VOICES_URL)):
        if os.path.exists(path):
            # Verify file size (should be > 10MB)
            size = os.path.getsize(path)
            if size < 10_000_000:
                _log("warn", "model file too small, re-downloading",
                     file=os.path.basename(path), size_bytes=size)
                os.remove(path)
            else:
                _log("debug", "model file OK", file=os.path.basename(path),
                     size_mb=round(size / 1024 / 1024, 1))
                continue
        _log("info", "downloading model", file=os.path.basename(path))
        _download(url, path)
        # Verify download
        if not os.path.exists(path) or os.path.getsize(path) < 10_000_000:
            _log("fail", "model download verification failed", file=path)
            raise RuntimeError(f"Model download verification failed for {path}")
    return onnx_p, voices_p


def _kokoro_wav(text: str, wav_path: str, prof: dict) -> bool:
    """Returns True on success. Raises on any failure -> caller falls back."""
    global _kokoro
    from kokoro_onnx import Kokoro
    if _kokoro is None:
        onnx_p, voices_p = _ensure_models()
        _kokoro = Kokoro(onnx_p, voices_p)
    samples, sample_rate = _kokoro.create(
        pace(text), voice=prof["kokoro"], speed=prof["speed"], lang=KOKORO_LANG)
    import soundfile as sf
    sf.write(wav_path, samples, sample_rate)
    _log("info", "kokoro model loaded", voice=prof["kokoro"], speed=prof["speed"])
    return True


def _kokoro_probe() -> bool:
    """Verify kokoro's espeak-ng phonemizer in a THROWAWAY SUBPROCESS.

    The phonemizer's bundled espeak-ng dylib can call exit(1) from C when its
    data dir is missing (e.g. a baked-in CI build path). A native abort is
    NOT catchable by a Python except in this process, so the designed
    Kokoro->Edge fallback never fires and the whole run dies. Probing in a
    subprocess turns that hard abort into an observable non-zero exit (or an
    'Error processing file' stderr) -> 'kokoro unavailable' -> Edge fallback.

    The probe exercises the exact same wiring kokoro's Tokenizer uses
    (espeakng_loader path + EspeakWrapper), but skips the ~200MB ONNX model,
    so it is cheap (~1-3s) and runs once per process (cached). Model-load
    failures stay in _kokoro_wav where they are already Python-catchable."""
    global _kokoro_probe_ok
    if _kokoro_probe_ok is not None:
        return _kokoro_probe_ok
    probe_code = (
        "import espeakng_loader\n"
        "import phonemizer\n"
        "from phonemizer.backend.espeak.wrapper import EspeakWrapper\n"
        "EspeakWrapper.set_data_path(espeakng_loader.get_data_path())\n"
        "EspeakWrapper.set_library(espeakng_loader.get_library_path())\n"
        "phonemizer.phonemize('probe.', language='en-us')\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", probe_code],
                           capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        r = None
    ok = bool(r is not None and r.returncode == 0
              and "Error processing file" not in (r.stderr or ""))
    _kokoro_probe_ok = ok
    if ok:
        _log("info", "kokoro probe ok (phonemizer usable)")
    else:
        if r is not None and (r.stderr or "").strip():
            tail = r.stderr.strip().splitlines()[-1]
        elif r is None:
            tail = "probe timed out after 60s"
        else:
            tail = f"exit {r.returncode}"
        _log("warn", "kokoro probe FAILED, will use Edge fallback", detail=tail)
    return _kokoro_probe_ok


async def _edge_save(text: str, path: str, prof: dict) -> None:
    import edge_tts
    await asyncio.wait_for(
        edge_tts.Communicate(
            pace(text), prof["edge"],
            rate=prof["edge_rate"], pitch=prof["edge_pitch"],
        ).save(path),
        timeout=EDGE_TIMEOUT,
    )


def _try_kokoro(text: str, path: str, prof: dict) -> bool:
    """Local Kokoro path. Returns True on success; never raises."""
    import binpath
    wav_tmp = path + ".kokoro.wav"
    try:
        _kokoro_wav(text, wav_tmp, prof)
        subprocess.run([binpath.FFMPEG, "-y", "-v", "error", "-i", wav_tmp,
                        "-codec:a", "libmp3lame", "-q:a", "3", path], check=True)
        os.remove(wav_tmp)
        _log("info", "TTS generated with Kokoro", voice=prof["kokoro"], output=path)
        return True
    except Exception as e:
        if os.path.exists(wav_tmp):
            try:
                os.remove(wav_tmp)
            except Exception:
                pass
        _log("warn", "kokoro failed", error=str(e))
        return False


def tts_sync(text: str, path: str, series_id: Optional[str] = None) -> None:
    """Free Kokoro first, Edge fallback. Output is always mp3 at `path`.

    series_id selects the host voice profile (see VOICE_PROFILES); omitted
    means the default narrator.

    Set TTS_ENGINE=edge to force Edge TTS (skip Kokoro entirely).
    Set TTS_ENGINE=kokoro to force Kokoro (no fallback).
    Default: auto-detect with fallback.
    """
    import asyncio
    import binpath
    prof = _profile(series_id)
    engine_override = os.getenv("TTS_ENGINE", "").strip().lower()

    # If forced to Edge, skip Kokoro entirely
    if engine_override == "edge":
        _log("info", "TTS_ENGINE=edge forced, skipping Kokoro", voice=prof["edge"])
        last: Optional[Exception] = None
        for attempt in (1, 2, 3):
            try:
                asyncio.run(_edge_save(text, path, prof))
                _log("info", "TTS generated with Edge (forced)", voice=prof["edge"], output=path)
                return
            except Exception as e:
                last = e
                if attempt < 3:
                    delay = 5 * attempt
                    _log("warn", "edge TTS attempt failed, retrying",
                         attempt=attempt, max_attempts=3, delay=delay, error=str(e))
                    time.sleep(delay)
                else:
                    _log("error", "edge TTS failed after retries", error=str(e))
        _log("fail", "Edge TTS failed (forced mode)", last_error=str(last))
        raise RuntimeError(f"TTS failed (edge forced): {last}")

    # Try Kokoro first (unless forced to skip)
    if engine_override != "kokoro" and _kokoro_probe():
        if _try_kokoro(text, path, prof):
            return

    # Edge fallback with retries
    _log("info", "using Edge TTS fallback", voice=prof["edge"])
    last: Optional[Exception] = None
    for attempt in (1, 2, 3):
        try:
            asyncio.run(_edge_save(text, path, prof))
            _log("info", "TTS generated with Edge", voice=prof["edge"], output=path)
            return
        except Exception as e:
            last = e
            if attempt < 3:
                delay = 5 * attempt
                _log("warn", "edge TTS attempt failed, retrying",
                     attempt=attempt, max_attempts=3, delay=delay, error=str(e))
                time.sleep(delay)
            else:
                _log("error", "edge TTS failed after retries", error=str(e))

    # Edge is down or hanging: one last attempt on the local engine.
    if engine_override != "edge" and _kokoro_probe() and _try_kokoro(text, path, prof):
        return

    _log("fail", "BOTH kokoro and edge TTS failed", last_error=str(last))
    raise RuntimeError(
        f"TTS failed for text {text[:48]!r}: kokoro unavailable and edge_tts "
        f"failed ({last}). Check network / edge-tts. This run will NOT upload "
        f"anything.")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("text")
    ap.add_argument("output")
    ap.add_argument("--series", default=None)
    args = ap.parse_args()
    tts_sync(args.text, args.output, args.series)