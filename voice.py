"""Voice v2: natural delivery + pronunciation fixes.
ChristopherNeural (warm male) with SSML pacing; Indian-money text normalized
so the voice never reads symbols literally."""
import asyncio, re

VOICE = "en-US-ChristopherNeural"
RATE = "-8%"

def normalize(t):
    t = t.replace("₹", " rupees ")
    t = re.sub(r"Rs\.?\s*([\d,]+)", r"\1 rupees", t)
    t = t.replace("%", " percent ")
    t = t.replace("&", " and ")
    t = re.sub(r"\b([A-Z]{2,})\b", lambda m: " ".join(m.group(1)), t)  # SIP -> S I P
    t = re.sub(r"\s+", " ", t).strip()
    return t

def speak_text(text):
    """Plain text with natural pauses. No SSML (Edge mis-parses it into slow-mo)."""
    parts = re.split(r"(?<=[.!?])\s+", normalize(text))
    return " ... ".join(p for p in parts if p)

async def speak(text, path):
    import edge_tts
    await edge_tts.Communicate(speak_text(text), VOICE, rate=RATE).save(path)

def tts_sync(text, path):
    asyncio.run(speak(text, path))
