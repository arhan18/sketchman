"""Bold hook thumbnails: high-contrast bg + short punch text + art crop."""
import os
from PIL import Image, ImageDraw, ImageFont
import art

W, H = 1280, 720

def font(size):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/System/Library/Fonts/Helvetica.ttc"]:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except Exception: pass
    return ImageFont.load_default()

def hook(title, n=4):
    words = [w for w in title.replace("?", "").replace("!", "").split() if w.lower() not in
             ("and", "the", "a", "an", "of", "to", "in", "vs", "is", "it")]
    return " ".join(words[:n]).upper()

def make(title, scene_key, path):
    img = Image.new("RGB", (W, H), (13, 13, 18))
    dr = ImageDraw.Draw(img)
    dr.rectangle([0, H - 130, W, H], fill=(255, 190, 40))
    scene = art.SCENES.get(scene_key, art.s_intro)(620, 350)
    img.paste(scene, (620, 180))
    dr.rectangle([612, 172, 620 + 628, 188 + 358], outline=(255, 255, 255), width=6)
    f = font(92)
    txt = hook(title)
    words, lines, cur = txt.split(), [], ""
    for w_ in words:
        if len(cur) + len(w_) + 1 > 9 and cur: lines.append(cur); cur = w_
        else: cur = (cur + " " + w_).strip()
    lines.append(cur); lines = lines[:3]
    y = 110
    for ln in lines:
        dr.text((48, y), ln, font=f, fill=(255, 255, 255),
                stroke_width=3, stroke_fill=(0, 0, 0))
        y += 112
    img.save(path)
    return path
