#!/usr/bin/env python3
"""Sketchman v2: colored flat scenes + Ken Burns slideshow + natural voice.
Subtitles are the spoken sentences themselves, each timed to its own
voiceover clip, so text and audio can never drift apart.
Usage: python generate.py --format long|short [--topic N]"""
import argparse, json, os, re, subprocess
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

def split_sentences(text):
    """One subtitle per spoken sentence — never show a summary as a subtitle."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]

def wrap(draw, text, fnt, max_w):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def fit_subtitle(draw, text, W, start, minimum=26, max_lines=3, max_w_frac=0.86):
    """Largest font that fits the sentence in <= max_lines wrapped lines."""
    size = start
    while size > minimum:
        fnt = font(size)
        if len(wrap(draw, text, fnt, W * max_w_frac)) <= max_lines:
            return fnt, wrap(draw, text, fnt, W * max_w_frac)
        size -= 2
    fnt = font(minimum)
    return fnt, wrap(draw, text, fnt, W * max_w_frac)[:max_lines]

def pill(dr, cx, y_top, lines, fnt, pad_x=22, pad_y=13):
    """Centered white caption pill; returns bottom edge y."""
    widths = [dr.textbbox((0, 0), ln, font=fnt)[2] for ln in lines]
    heights = [dr.textbbox((0, 0), ln, font=fnt)[3] for ln in lines]
    tw, th = max(widths) + pad_x * 2, sum(heights) + pad_y * 2 + (len(lines) - 1) * 6
    x0 = cx - tw / 2
    dr.rounded_rectangle([x0, y_top, x0 + tw, y_top + th], radius=18,
                         fill=(255, 255, 255), outline=(30, 30, 40), width=3)
    y = y_top + pad_y
    for i, (ln, lh) in enumerate(zip(lines, heights)):
        dr.text((cx - widths[i] / 2, y), ln, font=fnt, fill=(30, 30, 40))
        y += lh + 6
    return y_top + th

def render_segment(scene_key, hook, sentence, dur, W, H, seg_path):
    """One spoken sentence: hook pill on top, the sentence itself as the
    bottom subtitle. Video length == audio length exactly, so muxed
    segments concatenate with zero A/V drift."""
    base_fn = art.SCENES.get(scene_key, art.s_bed_alarm)
    n = max(1, int(round(dur * FPS)))
    frames_dir = seg_path + "_f"
    os.makedirs(frames_dir, exist_ok=True)
    meas = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    hook_fnt = font(max(24, int(W / 40)))
    hook_lines = wrap(meas, hook, hook_fnt, W * 0.86)[:1]
    sub_fnt, sub_lines = fit_subtitle(meas, sentence, W, max(28, int(W / 26)))
    if H > W:
        # vertical: landscape ink panel centered upper-middle on paper,
        # hook pill above it, subtitle pill beneath it (art is composed
        # 16:9, never stretch it)
        bw, bh = int(W * 1.2), int(W * 1.2 * 9 / 16)
        base = base_fn(bw, bh)
        panel_h = int(W * 9 / 16)
        py = int(H * 0.30 - panel_h / 2)
        for f in range(n):
            t = f / max(1, n - 1)          # slow zoom-in across the segment
            zw, zh = int(bw - (bw - W) * t), int(bh - (bh - panel_h) * t)
            left, top = (bw - zw) // 2, (bh - zh) // 2
            panel = base.crop((left, top, left + zw, top + zh)).resize((W, panel_h), Image.LANCZOS)
            frame = Image.new("RGB", (W, H), (250, 248, 242))
            frame.paste(panel, (0, py))
            dr = ImageDraw.Draw(frame)
            pill(dr, W / 2, 28, hook_lines, hook_fnt)
            pill(dr, W / 2, py + panel_h + 24, sub_lines, sub_fnt)
            frame.save(f"{frames_dir}/f{f:05d}.png")
    else:
        base = base_fn(int(W * 1.3), int(H * 1.3))
        bw, bh = base.size
        for f in range(n):
            t = f / max(1, n - 1)          # slow zoom-in across the segment
            zw, zh = int(bw - (bw - W) * t), int(bh - (bh - H) * t)
            left, top = (bw - zw) // 2, (bh - zh) // 2
            frame = base.crop((left, top, left + zw, top + zh)).resize((W, H), Image.LANCZOS)
            dr = ImageDraw.Draw(frame)
            pill(dr, W / 2, 22, hook_lines, hook_fnt)
            widths = [dr.textbbox((0, 0), ln, font=sub_fnt)[2] for ln in sub_lines]
            heights = [dr.textbbox((0, 0), ln, font=sub_fnt)[3] for ln in sub_lines]
            th = sum(heights) + 26 + (len(sub_lines) - 1) * 6
            pill(dr, W / 2, H - th - 24, sub_lines, sub_fnt)
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
    if topic_idx is None:
        topic_idx = topics.pick(fmt)
    t = topics_in[topic_idx % len(topics_in)]
    work = os.path.join(HERE, "work")
    os.makedirs(work, exist_ok=True)
    print(f"Topic: {t['title']}", flush=True)
    segs = []
    for b, beat in enumerate(t["beats"]):
        text, scene, hook = beat[0], beat[1], beat[2]
        for s, sent in enumerate(split_sentences(text)):
            a = os.path.join(work, f"b{b}s{s}.mp3")
            voice.tts_sync(sent, a)
            dur = probe_dur(a)
            v = os.path.join(work, f"b{b}s{s}v.mp4")
            render_segment(scene, hook, sent, dur, W, H, v)
            seg = os.path.join(work, f"b{b}s{s}.mp4")
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", v, "-i", a,
                            "-c:v", "copy", "-c:a", "aac", "-shortest", seg],
                           check=True)
            os.remove(v); os.remove(a)
            segs.append(seg)
            print(f"  beat {b + 1}/{len(t['beats'])} sent {s + 1}: {dur:.1f}s "
                  f"'{sent[:48]}...'", flush=True)
    listf = os.path.join(work, "list.txt")
    with open(listf, "w") as f:
        for s in segs: f.write(f"file '{s}'\n")
    out = os.path.join(HERE, f"{fmt}-{topic_idx}.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                    "-i", listf, "-c", "copy", out], check=True)
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
