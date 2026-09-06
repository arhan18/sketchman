#!/usr/bin/env python3
"""Sketchman generator: stick-figure whiteboard videos + TTS + captions.
Usage: python generate.py --format long|short [--topic N] [--out out.mp4]
State (used topics) kept in state.json next to this file."""
import argparse, asyncio, json, math, os, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

import figures
import topics

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 15
LONG_SIZE, SHORT_SIZE = (1280, 720), (720, 1280)
VOICE = "en-IN-PrabhatNeural"
STATE = os.path.join(HERE, "state.json")

random.seed()

def font(size):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/System/Library/Fonts/Helvetica.ttc",
              "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except Exception: pass
    return ImageFont.load_default()

def wobble_pts(x1, y1, x2, y2, amp=0.6):
    dx, dy = x2 - x1, y2 - y1
    dist = math.hypot(dx, dy) or 1
    n = max(2, int(dist / 3))
    nx, ny = -dy / dist, dx / dist
    pts = []
    for i in range(n + 1):
        t = i / n
        off = math.sin(t * math.pi * 2 + (x1 + y1)) * amp * math.sin(t * math.pi)
        pts.append((x1 + dx * t + nx * off, y1 + dy * t + ny * off))
    return pts

def flatten(strokes, W, H):
    """Strokes -> ordered point-paths in pixels (wobbled)."""
    paths = []
    for s in strokes:
        if s[0] == 'line':
            _, x1, y1, x2, y2 = s
            paths.append(wobble_pts(x1 / 100 * W, y1 / 100 * H, x2 / 100 * W, y2 / 100 * H))
        else:
            _, cx, cy, r = s
            cx, cy, r = cx / 100 * W, cy / 100 * H, r / 100 * min(W, H)
            paths.append([(cx + r * math.cos(t), cy + r * math.sin(t))
                          for t in [i * 0.25 for i in range(int(2 * math.pi / 0.25) + 1)]])
    return paths

def draw_partial(dr, paths, frac, W, H, width):
    total = sum(len(p) - 1 for p in paths)
    target = int(total * min(1.0, frac))
    done = 0
    for p in paths:
        for i in range(len(p) - 1):
            if done >= target: return
            dr.line([p[i], p[i + 1]], fill=(20, 20, 20), width=width)
            done += 1

async def tts(text, path):
    import edge_tts
    await edge_tts.Communicate(text, VOICE).save(path)

def probe_dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", path], capture_output=True, text=True)
    return float(r.stdout.strip())

def render_beat(scene_key, caption, dur, W, H, seg_path, fnt, small):
    strokes = figures.SCENES.get(scene_key, figures.SCENES['grind'])
    paths = flatten(strokes, W, H * 0.82)
    n = max(1, int(dur * FPS))
    draw_n = max(6, int(n * 0.35))
    width = max(2, W // 320)
    frames_dir = seg_path + "_f"
    os.makedirs(frames_dir, exist_ok=True)
    cap_h = int(H * 0.16)
    for f in range(n):
        img = Image.new("RGB", (W, H), (253, 252, 247))
        dr = ImageDraw.Draw(img)
        draw_partial(dr, paths, (f + 1) / draw_n, W, H, width)
        # caption strip
        dr.rectangle([0, H - cap_h, W, H], fill=(20, 20, 20))
        bb = dr.textbbox((0, 0), caption, font=fnt)
        tw = bb[2] - bb[0]
        dr.text(((W - tw) / 2, H - cap_h + (cap_h - (bb[3] - bb[1])) / 2),
                caption, font=fnt, fill=(255, 255, 255))
        img.save(f"{frames_dir}/f{f:05d}.png")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS),
                    "-i", f"{frames_dir}/f%05d.png", "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", seg_path], check=True)
    for f in os.listdir(frames_dir): os.remove(os.path.join(frames_dir, f))
    os.rmdir(frames_dir)

def build(fmt, topic_idx=None):
    vertical = (fmt == "short")
    W, H = SHORT_SIZE if vertical else LONG_SIZE
    topics_in = topics.SHORT_TOPICS if vertical else topics.LONG_TOPICS
    st = json.load(open(STATE)) if os.path.exists(STATE) else {"long": [], "short": []}
    if topic_idx is None:
        avail = [i for i in range(len(topics_in)) if i not in st[fmt]] or list(range(len(topics_in)))
        if len(avail) == len(topics_in): st[fmt] = []
        topic_idx = avail[0]
    st[fmt].append(topic_idx)
    json.dump(st, open(STATE, "w"))
    t = topics_in[topic_idx % len(topics_in)]
    work = os.path.join(HERE, "work")
    os.makedirs(work, exist_ok=True)
    fnt = font(int(W / 22))
    segs, auds = [], []
    print(f"Topic: {t['title']}", flush=True)
    for b, beat in enumerate(t["beats"]):
        a = os.path.join(work, f"b{b}.mp3")
        asyncio.run(tts(beat[0], a))
        dur = probe_dur(a) + 0.5
        v = os.path.join(work, f"b{b}.mp4")
        render_beat(beat[1], beat[2], dur, W, H, v, fnt, vertical)
        segs.append(v); auds.append(a)
        print(f"  beat {b + 1}/{len(t['beats'])}: {dur:.1f}s", flush=True)
    listf = os.path.join(work, "list.txt")
    with open(listf, "w") as f:
        for s in segs: f.write(f"file '{s}'\n")
    alist = os.path.join(work, "alist.txt")
    with open(alist, "w") as f:
        for a in auds: f.write(f"file '{a}'\n")
    vcat = os.path.join(work, "video.mp4")
    acat = os.path.join(work, "audio.mp3")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                    "-i", listf, "-c", "copy", vcat], check=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                    "-i", alist, "-c", "copy", acat], check=True)
    out = os.path.join(HERE, f"{fmt}-{topic_idx}.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", vcat, "-i", acat,
                    "-c:v", "copy", "-c:a", "aac", "-shortest", out], check=True)
    meta = {"title": t["title"], "file": out,
            "description": f"{t['title']}\n\nWhiteboard money-mindset series. New video every week.\n#money #mindset #finance",
            "tags": "money mindset,finance,personal finance,motivation"}
    json.dump(meta, open(os.path.join(HERE, f"{fmt}-{topic_idx}.json"), "w"))
    print(f"DONE: {out} ({probe_dur(out):.0f}s)", flush=True)
    return out

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--format", choices=["long", "short"], required=True)
    ap.add_argument("--topic", type=int, default=None)
    a = ap.parse_args()
    build(a.format, a.topic)
