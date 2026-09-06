"""Voice v3: free human-sounding TTS first, Edge fallback.
Primary: Kokoro-82M via kokoro-onnx (Apache 2.0, local, $0).
Voice am_adam @0.93 speed = calm male storyteller, closest free match
to the Ink Explainer reference (slow, intimate, ~135 wpm).
Fallback: Edge ChristopherNeural if kokoro model/deps are missing,
so CI/local never breaks. Indian-money text normalized so the
voice never reads symbols literally."""
import os
import re
import subprocess
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


def _ensure_models():
    os.makedirs(MODEL_DIR, exist_ok=True)
    onnx_p = os.path.join(MODEL_DIR, "kokoro-v1.0.onnx")
    voices_p = os.path.join(MODEL_DIR, "voices-v1.0.bin")
    for path, url in ((onnx_p, ONNX_URL), (voices_p, VOICES_URL)):
        if not os.path.exists(path):
            print(f"  downloading {os.path.basename(path)} (~100MB, one-time)...",
                  flush=True)
            urllib.request.urlretrieve(url, path)
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


async def _edge_save(text, path):
    import edge_tts
    await edge_tts.Communicate(pace(text), EDGE_VOICE, rate=EDGE_RATE).save(path)


def tts_sync(text, path):
    """Free Kokoro first, Edge fallback. Output is always mp3 at `path`."""
    wav_tmp = path + ".kokoro.wav"
    try:
        _kokoro_wav(text, wav_tmp)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", wav_tmp,
                        "-codec:a", "libmp3lame", "-q:a", "3", path], check=True)
        os.remove(wav_tmp)
        print("  voice: kokoro/am_adam", flush=True)
    except Exception as e:
        print(f"  voice: kokoro unavailable ({e}) -> edge fallback", flush=True)
        if os.path.exists(wav_tmp):
            os.remove(wav_tmp)
        import asyncio
        asyncio.run(_edge_save(text, path))
