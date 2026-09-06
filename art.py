"""Hand-ink explainer scenes (v4, Ink Explainer formula).
Same API as before: each function paints a complete WxH scene.
Style rules learned from the reference:
- warm white paper, dark ink strokes, flat muted accent fills
- figures WITH faces: dot eyes, brows, mood mouths, hair tufts
- depth in 3 layers: distant (faint hills/city/sky) / midground (actors+props)
  / foreground (corner grass, dust, frame ticks)
- one accent meaning per scene (gold = money, green/red = direction)
Coordinates in 0-100 space. Original compositions — no copied assets."""
from PIL import Image, ImageDraw

PAPER = (250, 248, 242)    # warm white paper
INK = (30, 30, 40)         # ink lines + faces
FAINT = (178, 178, 188)    # distant layer
GOLD = (205, 145, 15)      # money accent (dark enough for white paper)
GOLD_SOFT = (255, 225, 150)
GREEN, RED = (46, 160, 110), (210, 80, 80)
BLUE_SOFT = (170, 210, 235)

LW = 4  # master ink width


def _sx(x, W): return x / 100 * W
def _sy(y, H): return y / 100 * H
def _u(W, H, s=1.0): return min(W, H) / 100 * s


# ---------- depth layers ----------

def distant_hills(dr, W, H):
    dr.arc([W * -0.1, H * 0.35, W * 0.45, H * 0.95], 180, 360, fill=FAINT, width=3)
    dr.arc([W * 0.35, H * 0.42, W * 0.8, H * 1.0], 180, 360, fill=FAINT, width=3)
    dr.arc([W * 0.7, H * 0.38, W * 1.15, H * 0.98], 180, 360, fill=FAINT, width=3)


def distant_city(dr, W, H):
    for i, (bx, bh) in enumerate([(0.03, 0.30), (0.13, 0.42), (0.80, 0.38), (0.90, 0.30)]):
        dr.rectangle([W * bx, H * bh, W * (bx + 0.07), H * 0.62],
                     outline=FAINT, width=3)
        dr.line([W * bx, H * (bh + 0.06), W * (bx + 0.07), H * (bh + 0.06)],
                fill=FAINT, width=2)


def sky_birds(dr, W, H):
    for bx, by, s in [(0.2, 0.15, 1.0), (0.3, 0.22, 0.7), (0.72, 0.12, 0.9)]:
        X, Y, u = _sx(bx, W), _sy(by, H), _u(W, H, s)
        dr.arc([X - 4 * u, Y - 2 * u, X, Y + 2 * u], 200, 340, fill=FAINT, width=3)
        dr.arc([X, Y - 2 * u, X + 4 * u, Y + 2 * u], 200, 340, fill=FAINT, width=3)


def foreground_grass(dr, W, H):
    for gx in (0.03, 0.09, 0.90, 0.96):
        X = _sx(gx, W)
        for k, (dx, h) in enumerate([(-8, 26), (0, 36), (8, 24)]):
            dr.line([(X + dx, H - 4), (X + dx - 6, H - 4 - h)], fill=INK, width=3)
    for dx, dy in [(0.15, 0.7), (0.85, 0.65), (0.5, 0.2)]:
        dr.ellipse([_sx(dx, W) - 2, _sy(dy, H) - 2,
                    _sx(dx, W) + 2, _sy(dy, H) + 2], fill=FAINT)


def ground(dr, W, H, frac=0.78):
    dr.line([(0, H * frac), (W, H * frac)], fill=INK, width=LW)
    x = 0
    while x < W:  # hatch ticks below the line
        dr.line([(x, H * frac), (x - 12, H * frac + 14)], fill=FAINT, width=2)
        x += 90


# ---------- actors & props ----------

def face(dr, X, Y, u, mood='neutral'):
    r = 4 * u
    ex, ey, er = 1.6 * u, -0.5 * u, max(1.5, 0.45 * u)
    for sgn in (-1, 1):  # dot eyes
        dr.ellipse([X + sgn * ex - er, Y + ey - er,
                    X + sgn * ex + er, Y + ey + er], fill=INK)
    for sgn in (-1, 1):  # brows
        dr.line([(X + sgn * ex - er, Y + ey - 3 * er),
                 (X + sgn * ex + er, Y + ey - 2.4 * er)], fill=INK, width=2)
    if mood == 'happy':
        dr.arc([X - 2 * u, Y + 0.5 * u, X + 2 * u, Y + 3.5 * u], 10, 170, fill=INK, width=2)
    elif mood == 'sad':
        dr.arc([X - 2 * u, Y + 1.5 * u, X + 2 * u, Y + 4 * u], 190, 350, fill=INK, width=2)
    elif mood == 'worried':
        dr.line([(X - 2 * u, Y + 2.4 * u), (X + 2 * u, Y + 2.4 * u)], fill=INK, width=2)
    else:
        dr.line([(X - 1.5 * u, Y + 2.4 * u), (X + 1.5 * u, Y + 2.4 * u)], fill=INK, width=2)


def hair(dr, X, Y, u, style=0):
    r = 4 * u
    if style == 0:  # short tufts
        for a in (210, 250, 290, 330):
            import math
            c, sn = math.cos(math.radians(a)), math.sin(math.radians(a))
            dr.line([(X + (r - 1) * c, Y - 18 * u + (r - 1) * sn),
                     (X + (r + 1.1 * u) * c, Y - 18 * u + (r + 1.1 * u) * sn)],
                    fill=INK, width=2)
    else:  # side-part cap arc
        dr.arc([X - r, Y - 22 * u, X + r, Y - 14 * u], 180, 360, fill=INK, width=3)


def person(dr, W, H, x, y, s=1.0, shirt=0, pose='stand', mood='neutral', hairstyle=0):
    X, Y = _sx(x, W), _sy(y, H)
    u = _u(W, H, s)
    dr.ellipse([X - 4 * u, Y - 22 * u, X + 4 * u, Y - 14 * u], outline=INK, width=LW)
    face(dr, X, Y - 18 * u, u, mood)
    hair(dr, X, Y, u, hairstyle)
    dr.line([X, Y - 14 * u, X, Y - 2 * u], fill=INK, width=LW)
    if pose == 'stand':
        arms = [(X - 7 * u, Y - 8 * u), (X + 7 * u, Y - 8 * u)]
        legs = [(X - 5 * u, Y + 8 * u), (X + 5 * u, Y + 8 * u)]
    elif pose == 'arms_up':
        arms = [(X - 8 * u, Y - 20 * u), (X + 8 * u, Y - 20 * u)]
        legs = [(X - 5 * u, Y + 8 * u), (X + 5 * u, Y + 8 * u)]
    else:  # walk
        arms = [(X - 7 * u, Y - 10 * u), (X + 6 * u, Y - 6 * u)]
        legs = [(X - 7 * u, Y + 8 * u), (X + 4 * u, Y + 8 * u)]
    for ax, ay in arms:
        dr.line([X, Y - 13 * u, ax, ay], fill=INK, width=LW)
        dr.ellipse([ax - 1.2 * u, ay - 1.2 * u, ax + 1.2 * u, ay + 1.2 * u], fill=INK)
    for lx, ly in legs: dr.line([X, Y - 2 * u, lx, ly], fill=INK, width=LW)


def bag(dr, W, H, x, y, s=1.0):
    X, Y = _sx(x, W), _sy(y, H)
    u = _u(W, H, s)
    dr.polygon([(X - 3 * u, Y - 12 * u), (X + 3 * u, Y - 12 * u),
                (X + 8 * u, Y - 4 * u), (X + 7 * u, Y + 8 * u),
                (X - 7 * u, Y + 8 * u), (X - 8 * u, Y - 4 * u)],
               fill=GOLD_SOFT, outline=GOLD, width=LW)
    dr.line([X - 3 * u, Y - 12 * u, X + 3 * u, Y - 12 * u], fill=GOLD, width=LW)
    dr.line([X - 6 * u, Y - 1 * u, X + 6 * u, Y - 1 * u], fill=GOLD, width=2)  # stitch
    dr.text((X - 4 * u, Y - 4 * u), "$", fill=GOLD)


def coin(dr, W, H, x, y, s=1.0):
    X, Y = _sx(x, W), _sy(y, H)
    u = _u(W, H, s)
    dr.ellipse([X - 5 * u, Y - 5 * u, X + 5 * u, Y + 5 * u],
               fill=GOLD_SOFT, outline=GOLD, width=LW)
    dr.ellipse([X - 2.5 * u, Y - 2.5 * u, X + 2.5 * u, Y + 2.5 * u], outline=GOLD, width=2)
    dr.line([X - 4 * u, Y - 6.5 * u, X - 2 * u, Y - 8 * u], fill=GOLD, width=2)  # shine


def sun(dr, W, H):
    X0, Y0, R = W * .895, H * .04 + W * .075, W * .075
    dr.ellipse([X0 - R, Y0 - R, X0 + R, Y0 + R], outline=FAINT, width=LW)
    for a in (0, 45, 90, 135, 180, 225, 270, 315):
        import math
        c, sn = math.cos(math.radians(a)), math.sin(math.radians(a))
        dr.line([(X0 + (R + 4) * c, Y0 + (R + 4) * sn),
                 (X0 + (R + 14) * c, Y0 + (R + 14) * sn)], fill=FAINT, width=3)


def chart(dr, W, H, up=True):
    col = GREEN if up else RED
    x0, y0, w, h = W * .42, H * .62, W * .45, H * .3
    for i in range(0, 20, 2):  # dashed axes
        t = i / 20
        dr.point([(x0 + t * w, y0), (x0, y0 - t * h)], fill=FAINT)
    pts = []
    for i in range(6):
        t = i / 5
        v = (t ** 1.7 if up else 1 - t ** 1.3) * h
        pts.append((x0 + t * w, y0 - v))
    dr.line(pts, fill=col, width=7, joint="curve")
    dr.ellipse([pts[-1][0] - 8, pts[-1][1] - 8, pts[-1][0] + 8, pts[-1][1] + 8], fill=col)


def base(W, H, sky=True):
    img = Image.new("RGB", (W, H), PAPER)
    return img, ImageDraw.Draw(img)


def s_intro(W, H):
    img, dr = base(W, H)
    distant_hills(dr, W, H); sky_birds(dr, W, H); sun(dr, W, H); ground(dr, W, H)
    person(dr, W, H, 38, 62, 1.5, 0, 'arms_up', 'happy', 0)
    bag(dr, W, H, 68, 66, 1.2); coin(dr, W, H, 80, 40, 1.0); coin(dr, W, H, 22, 30, 0.8)
    foreground_grass(dr, W, H)
    return img


def s_think(W, H):
    img, dr = base(W, H, False)
    distant_city(dr, W, H); ground(dr, W, H, 0.8)
    person(dr, W, H, 32, 64, 1.5, 1, 'stand', 'neutral', 1)
    X, Y = _sx(32, W), _sy(64, H) - _u(W, H, 1.5) * 24  # bubble trail from head
    for i, (bx, by, r) in enumerate([(0.44, 0.30, 4), (0.48, 0.24, 6)]):
        dr.ellipse([_sx(bx, W) - r, _sy(by, H) - r,
                    _sx(bx, W) + r, _sy(by, H) + r], outline=INK, width=3)
    dr.ellipse([W * .55, H * .12, W * .92, H * .5], fill=(255, 255, 255), outline=INK, width=LW)
    bag(dr, W, H, 73, 32, 1.0); coin(dr, W, H, 84, 22, 0.7)
    foreground_grass(dr, W, H)
    return img


def s_grind(W, H):
    img, dr = base(W, H)
    for i, bx in enumerate([0.08, 0.3, 0.62, 0.84]):
        bh = [0.5, 0.62, 0.45, 0.58][i]
        x0, y0, x1 = W * bx, H * bh, W * (bx + 0.14)  # building with windows + door
        dr.rectangle([x0, y0, x1, H * 0.78], fill=BLUE_SOFT, outline=INK, width=LW)
        for r in range(2):
            for c in range(2):
                wx, wy = x0 + (x1 - x0) * (0.22 + 0.5 * c), y0 + (H * 0.78 - y0) * (0.2 + 0.35 * r)
                dr.rectangle([wx - 8, wy - 8, wx + 8, wy + 8], outline=INK, width=2)
        dr.rectangle([(x0 + x1) / 2 - 12, H * 0.78 - 34, (x0 + x1) / 2 + 12, H * 0.78],
                     outline=INK, width=3)
    ground(dr, W, H)
    person(dr, W, H, 30, 66, 1.3, 2, 'walk', 'worried', 0)
    person(dr, W, H, 62, 66, 1.3, 3, 'walk', 'neutral', 1)
    foreground_grass(dr, W, H)
    return img


def s_trap(W, H):
    img, dr = base(W, H, False)
    distant_hills(dr, W, H); ground(dr, W, H, 0.8)
    dr.ellipse([W * .48, H * .7, W * .88, H * .95], outline=INK, width=LW + 1)
    dr.ellipse([W * .52, H * .73, W * .84, H * .88], outline=FAINT, width=3)
    for cx in (0.44, 0.92):  # cracks around the pit
        dr.line([(_sx(cx, W), H * .8), (_sx(cx, W) - 24, H * .68)], fill=INK, width=3)
        dr.line([(_sx(cx, W) - 24, H * .68), (_sx(cx, W) - 40, H * .70)], fill=INK, width=3)
    person(dr, W, H, 30, 60, 1.2, 1, 'stand', 'worried', 1)
    foreground_grass(dr, W, H)
    return img


def s_chart_up(W, H):
    img, dr = base(W, H, False)
    sky_birds(dr, W, H)
    chart(dr, W, H, True)
    ground(dr, W, H, 0.86)
    person(dr, W, H, 20, 74, 1.3, 2, 'arms_up', 'happy', 0)
    coin(dr, W, H, 85, 20, 1.0); coin(dr, W, H, 72, 14, 0.7)
    foreground_grass(dr, W, H)
    return img


def s_chart_down(W, H):
    img, dr = base(W, H, False)
    chart(dr, W, H, False)
    ground(dr, W, H, 0.86)
    person(dr, W, H, 20, 74, 1.3, 1, 'stand', 'sad', 1)
    foreground_grass(dr, W, H)
    return img


def s_freedom(W, H):
    img, dr = base(W, H)
    sun(dr, W, H); sky_birds(dr, W, H)
    dr.line([(0, H * .62), (W, H * .62)], fill=INK, width=3)  # sea horizon
    for i in range(3):  # waves
        y = H * (0.72 + i * 0.06)
        x = 0
        while x < W:
            dr.arc([x, y - 8, x + 44, y + 8], 180, 360, fill=FAINT, width=2)
            x += 48
    ground(dr, W, H, 0.62)
    person(dr, W, H, 40, 58, 1.5, 0, 'arms_up', 'happy', 0)
    bag(dr, W, H, 72, 60, 1.1)
    foreground_grass(dr, W, H)
    return img


def s_habit(W, H):
    img, dr = base(W, H, False)
    distant_city(dr, W, H); ground(dr, W, H, 0.8)
    dr.rectangle([W * .12, H * .15, W * .44, H * .6], fill=(255, 255, 255), outline=INK, width=LW)
    for i in range(4):
        y = H * (0.24 + i * 0.1)
        dr.rectangle([W * .17, y, W * .22, y + H * .04], outline=GREEN, width=3)
        if i < 3: dr.line([W * .175, y + H * .02, W * .19, y + H * .035, W * .215, y + H * .005], fill=GREEN, width=3)
        else: dr.line([W * .25, y + H * .02, W * .4, y + H * .02], fill=GOLD, width=5)
        dr.line([W * .25, y + H * .02, W * .4, y + H * .02], fill=FAINT, width=4)
    person(dr, W, H, 68, 62, 1.4, 3, 'walk', 'neutral', 0)
    foreground_grass(dr, W, H)
    return img


def s_money(W, H):
    img, dr = base(W, H, False)
    sky_birds(dr, W, H)
    bag(dr, W, H, 38, 55, 1.6); bag(dr, W, H, 65, 60, 1.1)
    for cx, cy, s in [(20, 25, .8), (80, 25, .9), (55, 15, .7), (88, 45, .6)]:
        coin(dr, W, H, cx, cy, s)
    ground(dr, W, H, 0.9)
    foreground_grass(dr, W, H)
    return img


def s_choice(W, H):
    img, dr = base(W, H, False)
    distant_hills(dr, W, H); ground(dr, W, H, 0.8)
    dr.line([(W * .5, H * .8), (W * .2, H * .3)], fill=GREEN, width=8)
    dr.line([(W * .5, H * .8), (W * .8, H * .3)], fill=RED, width=8)
    for px, col in [(0.2, GREEN), (0.8, RED)]:  # signposts, no text
        dr.line([(_sx(px, W), _sy(0.3, H)), (_sx(px, W), _sy(0.3, H) - 60)], fill=INK, width=LW)
        dr.rectangle([_sx(px, W) - 44, _sy(0.3, H) - 96, _sx(px, W) + 44, _sy(0.3, H) - 60],
                     fill=(255, 255, 255), outline=col, width=3)
    person(dr, W, H, 50, 66, 1.3, 0, 'stand', 'neutral', 1)
    coin(dr, W, H, 20, 22, 1.0)
    foreground_grass(dr, W, H)
    return img

SCENES = {'intro': s_intro, 'think': s_think, 'grind': s_grind, 'trap': s_trap,
          'chart_up': s_chart_up, 'chart_down': s_chart_down, 'freedom': s_freedom,
          'habit': s_habit, 'money': s_money, 'choice': s_choice,
          'walk': s_grind, 'clock': s_habit}
