#!/usr/bin/env python3
"""Sketchman v2: colored flat scenes + Ken Burns slideshow + natural voice.
Usage: python generate.py --format long|short [--topic N]"""
import argparse, json, os, subprocess
from PIL import Image, ImageDraw, ImageFont

import art
import thumbnails
import topics
import voice

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 15
LONG_SIZE, SHORT_SIZE = (1280, 720), (720, 1280)
STATE = os.path.join(HERE, "state.json")

def font(size):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/System/Library/Fonts/Helvetica.ttc",
              "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except Exception: pass
    return ImageFont.load_default()

def probe_dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", path], capture_output=True, text=True)
    return float(r.stdout.strip())

def render_beat(scene_key, caption, dur, W, H, seg_path):
    base_fn = art.SCENES.get(scene_key, art.s_grind)
    n = max(1, int(dur * FPS))
    frames_dir = seg_path + "_f"
    os.makedirs(frames_dir, exist_ok=True)
    fnt = font(int(W / 24))
    if H > W:
        # vertical: landscape ink panel centered upper-middle on black,
        # caption pill beneath it (art is composed 16:9, never stretch it)
        bw, bh = int(W * 1.2), int(W * 1.2 * 9 / 16)
        base = base_fn(bw, bh)
        panel_h = int(W * 9 / 16)
        py = int(H * 0.30 - panel_h / 2)
        for f in range(n):
            t = f / max(1, n - 1)          # slow zoom-in across the beat
            zw, zh = int(bw - (bw - W) * t), int(bh - (bh - panel_h) * t)
            left, top = (bw - zw) // 2, (bh - zh) // 2
            panel = base.crop((left, top, left + zw, top + zh)).resize((W, panel_h), Image.LANCZOS)
            frame = Image.new("RGB", (W, H), (250, 248, 242))
            frame.paste(panel, (0, py))
            dr = ImageDraw.Draw(frame)
            bb = dr.textbbox((0, 0), caption, font=fnt)
            tw, th = bb[2] - bb[0] + 44, bb[3] - bb[1] + 26
            x0 = (W - tw) / 2
            cy = py + panel_h + 40
            dr.rounded_rectangle([x0, cy, x0 + tw, cy + th], radius=18, fill=(255, 255, 255), outline=(30, 30, 40), width=3)
            dr.text((x0 + 22, cy + 13 - bb[1]), caption, font=fnt, fill=(30, 30, 40))
            frame.save(f"{frames_dir}/f{f:05d}.png")
    else:
        base = base_fn(int(W * 1.3), int(H * 1.3))
        bw, bh = base.size
        for f in range(n):
            t = f / max(1, n - 1)          # slow zoom-in across the beat
            zw, zh = int(bw - (bw - W) * t), int(bh - (bh - H) * t)
            left, top = (bw - zw) // 2, (bh - zh) // 2
            frame = base.crop((left, top, left + zw, top + zh)).resize((W, H), Image.LANCZOS)
            dr = ImageDraw.Draw(frame)
            bb = dr.textbbox((0, 0), caption, font=fnt)
            tw, th = bb[2] - bb[0] + 44, bb[3] - bb[1] + 26
            x0 = (W - tw) / 2
            dr.rounded_rectangle([x0, H - th - 26, x0 + tw, H - 26], radius=18, fill=(255, 255, 255), outline=(30, 30, 40), width=3)
            dr.text((x0 + 22, H - th - 26 + 13 - bb[1]), caption, font=fnt, fill=(30, 30, 40))
            frame.save(f"{frames_dir}/f{f:05d}.png")
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
    print(f"Topic: {t['title']}", flush=True)
    segs, auds = [], []
    for b, beat in enumerate(t["beats"]):
        a = os.path.join(work, f"b{b}.mp3")
        voice.tts_sync(beat[0], a)
        dur = probe_dur(a) + 0.5
        v = os.path.join(work, f"b{b}.mp4")
        render_beat(beat[1], beat[2], dur, W, H, v)
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
    thumb = os.path.join(HERE, f"{fmt}-{topic_idx}-thumb.png")
    thumbnails.make(t["title"], t["beats"][0][1], thumb)
    json.dump({"title": t["title"], "file": out, "thumbnail": thumb,
               "description": f"{t['title']}\n\nWhiteboard money-mindset series. New video every week.\n#money #mindset #finance",
               "tags": "money mindset,finance,personal finance,motivation"},
              open(os.path.join(HERE, f"{fmt}-{topic_idx}.json"), "w"))
    print(f"DONE: {out} ({probe_dur(out):.0f}s) + {thumb}", flush=True)
    return out

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--format", choices=["long", "short"], required=True)
    ap.add_argument("--topic", type=int, default=None)
    a = ap.parse_args()
    build(a.format, a.topic)
