"""Voice v4: free human-sounding TTS first, Edge fallback.
Primary: Kokoro-82M via kokoro-onnx (Apache 2.0, local, $0).
Voice am_adam @0.93 speed = calm male storyteller, closest free match
to the Ink Explainer reference (slow, intimate, ~135 wpm).
Fallback: Edge ChristopherNeural if kokoro model/deps are missing, OR
if the espeak-ng phonemizer hard-fails (probing in a throwaway subprocess
catches native espeak-ng exit(1) that no Python except can see), so
CI/local never breaks. Indian-money text normalized so the
voice never reads symbols literally."""
import os
import re
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(HERE, "models")
ONNX_URL = ("https://github.com/thewh1teagle/kokoro-onnx/"
            "releases/download/model-files-v1.0/kokoro-v1.0.onnx")
VOICES_URL = ("https://github.com/thewh1teagle/kokoro-onnx/"
              "releases/download/model-files-v1.0/voices-v1.0.bin")

KOKORO_VOICE = "am_adam"   # calm male narrator; alt: af_bella (female)
KOKORO_SPEED = 0.93        # slightly slow = human, not rushed
KOKORO_LANG = "en-us"

EDGE_VOICE = "en-US-ChristopherNeural"
EDGE_RATE = "-8%"

_kokoro = None
_kokoro_probe_ok = None   # None=unknown, True/False cached once per process


def normalize(t):
    t = t.replace("₹", " rupees ")
    t = re.sub(r"Rs\.?\s*([\d,]+)", r"\1 rupees", t)
    t = t.replace("%", " percent ")
    t = t.replace("&", " and ")
    t = re.sub(r"\b([A-Z]{2,})\b", lambda m: " ".join(m.group(1)), t)  # SIP -> S I P
    t = re.sub(r"\s+", " ", t).strip()
    return t


def pace(text):
    """Short sentences + explicit pauses. Ink-style: never a wall of text.
    ' ... ' renders as a real pause in both Kokoro and Edge."""
    parts = re.split(r"(?<=[.!?])\s+", normalize(text))
    return " ... ".join(p for p in parts if p)


def _download(url, dest, tries=3):
    """Streaming download to <dest>.part, atomic rename on success. Retries."""
    import time as _t
    part = dest + ".part"
    for attempt in range(1, tries + 1):
        try:
            with urllib.request.urlopen(url, timeout=120) as r, open(part, "wb") as f:
                total = int(r.headers.get("Content-Length") or 0)
                while True:
                    chunk = r.read(1 << 16)
                    if not chunk:
                        break
                    f.write(chunk)
            os.replace(part, dest)
            return
        except Exception as e:
            if os.path.exists(part):
                os.remove(part)
            if attempt == tries:
                raise RuntimeError(f"download failed after {tries} tries: {e}")
            print(f"  retry {attempt}: {os.path.basename(dest)} download error "
                  f"({e}); sleeping...", flush=True)
            _t.sleep(5 * attempt)


def _ensure_models():
    os.makedirs(MODEL_DIR, exist_ok=True)
    onnx_p = os.path.join(MODEL_DIR, "kokoro-v1.0.onnx")
    voices_p = os.path.join(MODEL_DIR, "voices-v1.0.bin")
    for path, url in ((onnx_p, ONNX_URL), (voices_p, VOICES_URL)):
        if os.path.exists(path):
            continue
        print(f"  downloading {os.path.basename(path)} (~100MB, one-time) "
              f"— a .part file means an earlier attempt is being finished...",
              flush=True)
        _download(url, path)
    return onnx_p, voices_p


def _kokoro_wav(text, wav_path):
    """Returns True on success. Raises on any failure -> caller falls back."""
    global _kokoro
    from kokoro_onnx import Kokoro
    if _kokoro is None:
        onnx_p, voices_p = _ensure_models()
        _kokoro = Kokoro(onnx_p, voices_p)
    samples, sample_rate = _kokoro.create(
        pace(text), voice=KOKORO_VOICE, speed=KOKORO_SPEED, lang=KOKORO_LANG)
    import soundfile as sf
    sf.write(wav_path, samples, sample_rate)
    return True


def _kokoro_probe():
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
        print("  voice: kokoro probe ok (phonemizer usable)", flush=True)
    else:
        if r is not None and (r.stderr or "").strip():
            tail = r.stderr.strip().splitlines()[-1]
        elif r is None:
            tail = "probe timed out after 60s"
        else:
            tail = f"exit {r.returncode}"
        print(f"  voice.kokoro_failed: kokoro probe FAILED ({tail}) -> "
              f"fallback=edge", flush=True)
    return _kokoro_probe_ok


async def _edge_save(text, path):
    import edge_tts
    await edge_tts.Communicate(pace(text), EDGE_VOICE, rate=EDGE_RATE).save(path)


def tts_sync(text, path):
    """Free Kokoro first, Edge fallback. Output is always mp3 at `path`."""
    import asyncio
    wav_tmp = path + ".kokoro.wav"
    if _kokoro_probe():
        try:
            _kokoro_wav(text, wav_tmp)
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", wav_tmp,
                            "-codec:a", "libmp3lame", "-q:a", "3", path], check=True)
            os.remove(wav_tmp)
            print("  voice: kokoro/am_adam", flush=True)
            return
        except Exception as e:
            if os.path.exists(wav_tmp):
                os.remove(wav_tmp)
            print(f"  voice: kokoro unusable in-process ({e}) -> edge fallback",
                  flush=True)
    # Edge path: one retry, then fail loud (a silent pipeline bug is worse
    # than a failed run that emails you).
    last = None
    for attempt in (1, 2):
        try:
            asyncio.run(_edge_save(text, path))
            print("  voice: edge/ChristopherNeural", flush=True)
            return
        except Exception as e:
            last = e
            if attempt == 1:
                import time as _t
                print(f"  voice: edge attempt {attempt} failed ({e}); retry in "
                      f"3s", flush=True)
                _t.sleep(3)
    print(f"  voice: BOTH kokoro and edge failed ({last})", flush=True)
    raise RuntimeError(
        f"TTS failed for text {text[:48]!r}: kokoro unavailable and edge_tts "
        f"failed ({last}). Check network / edge-tts. This run will NOT upload "
        f"anything.")
