"""Colored flat-style illustration scenes (v2). Full-frame art, no draw-on.
Each function paints a complete WxH scene. Coordinates in 0-100 space."""
from PIL import Image, ImageDraw

SKIN = (242, 200, 155)
INK = (30, 30, 40)
SHIRTS = [(58, 134, 255), (255, 122, 89), (46, 196, 134), (155, 89, 255)]
GOLD, GREEN, RED = (255, 190, 40), (46, 196, 134), (235, 87, 87)
PAPER = (255, 251, 240)
SKY = (214, 240, 255)

def _sx(x, W): return x / 100 * W
def _sy(y, H): return y / 100 * H

def person(dr, W, H, x, y, s=1.0, shirt=0, pose='stand'):
    c = SHIRTS[shirt % len(SHIRTS)]
    X, Y = _sx(x, W), _sy(y, H)
    u = min(W, H) / 100 * s
    dr.ellipse([X - 4 * u, Y - 22 * u, X + 4 * u, Y - 14 * u], fill=SKIN, outline=INK, width=2)
    dr.line([X, Y - 14 * u, X, Y - 2 * u], fill=c, width=int(5 * u))
    if pose == 'stand':
        arms = [(X - 7 * u, Y - 8 * u), (X + 7 * u, Y - 8 * u)]
        legs = [(X - 5 * u, Y + 8 * u), (X + 5 * u, Y + 8 * u)]
    elif pose == 'arms_up':
        arms = [(X - 8 * u, Y - 20 * u), (X + 8 * u, Y - 20 * u)]
        legs = [(X - 5 * u, Y + 8 * u), (X + 5 * u, Y + 8 * u)]
    else:  # walk
        arms = [(X - 7 * u, Y - 10 * u), (X + 6 * u, Y - 6 * u)]
        legs = [(X - 7 * u, Y + 8 * u), (X + 4 * u, Y + 8 * u)]
    for ax, ay in arms: dr.line([X, Y - 13 * u, ax, ay], fill=c, width=int(4 * u))
    for lx, ly in legs: dr.line([X, Y - 2 * u, lx, ly], fill=INK, width=int(4 * u))

def bag(dr, W, H, x, y, s=1.0):
    X, Y = _sx(x, W), _sy(y, H)
    u = min(W, H) / 100 * s
    dr.polygon([(X - 3 * u, Y - 12 * u), (X + 3 * u, Y - 12 * u),
                (X + 8 * u, Y - 4 * u), (X + 7 * u, Y + 8 * u),
                (X - 7 * u, Y + 8 * u), (X - 8 * u, Y - 4 * u)], fill=GOLD, outline=INK)
    dr.line([X - 3 * u, Y - 12 * u, X + 3 * u, Y - 12 * u], fill=INK, width=3)
    dr.text((X - 4 * u, Y - 4 * u), "$", fill=INK)

def coin(dr, W, H, x, y, s=1.0):
    X, Y = _sx(x, W), _sy(y, H)
    u = min(W, H) / 100 * s
    dr.ellipse([X - 5 * u, Y - 5 * u, X + 5 * u, Y + 5 * u], fill=GOLD, outline=(180, 130, 20), width=2)

def sun(dr, W, H):
    dr.ellipse([W * .82, H * .04, W * .97, H * .04 + W * .15], fill=(255, 205, 60))

def ground(dr, W, H, frac=0.78, color=(200, 235, 190)):
    dr.rectangle([0, H * frac, W, H], fill=color)

def chart(dr, W, H, up=True):
    x0, y0, w, h = W * .42, H * .62, W * .45, H * .3
    col = GREEN if up else RED
    n = 6
    pts = []
    for i in range(n):
        t = i / (n - 1)
        v = (t ** 1.7 if up else 1 - t ** 1.3) * h
        pts.append((x0 + t * w, y0 - v))
    dr.line(pts, fill=col, width=7, joint="curve")
    dr.ellipse([pts[-1][0] - 7, pts[-1][1] - 7, pts[-1][0] + 7, pts[-1][1] + 7], fill=col)

def base(W, H, sky=True):
    img = Image.new("RGB", (W, H), SKY if sky else PAPER)
    return img, ImageDraw.Draw(img)

def s_intro(W, H):
    img, dr = base(W, H); sun(dr, W, H); ground(dr, W, H)
    person(dr, W, H, 38, 62, 1.5, 0, 'arms_up')
    bag(dr, W, H, 68, 66, 1.2); coin(dr, W, H, 80, 40, 1.0); coin(dr, W, H, 22, 30, 0.8)
    return img

def s_think(W, H):
    img, dr = base(W, H, False); ground(dr, W, H, 0.8, (235, 228, 210))
    person(dr, W, H, 32, 64, 1.5, 1, 'stand')
    dr.ellipse([W * .55, H * .12, W * .92, H * .5], fill=(255, 255, 255), outline=INK, width=3)
    bag(dr, W, H, 73, 32, 1.0); coin(dr, W, H, 84, 22, 0.7)
    return img

def s_grind(W, H):
    img, dr = base(W, H)
    for i, bx in enumerate([0.08, 0.3, 0.62, 0.84]):
        bh = [0.5, 0.62, 0.45, 0.58][i]
        dr.rectangle([W * bx, H * bh, W * (bx + 0.14), H * 0.78], fill=(180, 195, 215), outline=INK, width=2)
    ground(dr, W, H)
    person(dr, W, H, 30, 66, 1.3, 2, 'walk'); person(dr, W, H, 62, 66, 1.3, 3, 'walk')
    return img

def s_trap(W, H):
    img, dr = base(W, H, False); ground(dr, W, H, 0.8, (235, 228, 210))
    dr.ellipse([W * .48, H * .7, W * .88, H * .95], fill=(60, 50, 55))
    dr.ellipse([W * .52, H * .73, W * .84, H * .88], fill=(25, 20, 25))
    person(dr, W, H, 30, 60, 1.2, 1, 'stand')
    return img

def s_chart_up(W, H):
    img, dr = base(W, H, False)
    chart(dr, W, H, True)
    person(dr, W, H, 20, 62, 1.3, 2, 'arms_up')
    coin(dr, W, H, 85, 20, 1.0); coin(dr, W, H, 72, 14, 0.7)
    return img

def s_chart_down(W, H):
    img, dr = base(W, H, False)
    chart(dr, W, H, False)
    person(dr, W, H, 20, 62, 1.3, 1, 'stand')
    return img

def s_freedom(W, H):
    img, dr = base(W, H); sun(dr, W, H)
    dr.rectangle([0, H * .62, W, H], fill=(255, 225, 150))
    dr.rectangle([0, H * .72, W, H], fill=(110, 190, 235))
    person(dr, W, H, 40, 58, 1.5, 0, 'arms_up')
    bag(dr, W, H, 72, 60, 1.1)
    return img

def s_habit(W, H):
    img, dr = base(W, H, False); ground(dr, W, H, 0.8, (235, 228, 210))
    dr.rectangle([W * .12, H * .15, W * .44, H * .6], fill=(255, 255, 255), outline=INK, width=3)
    for i in range(4):
        y = H * (0.24 + i * 0.1)
        dr.rectangle([W * .17, y, W * .22, y + H * .04], outline=GREEN, width=3)
        if i < 3: dr.line([W * .175, y + H * .02, W * .19, y + H * .035, W * .215, y + H * .005], fill=GREEN, width=3)
        dr.line([W * .25, y + H * .02, W * .4, y + H * .02], fill=(200, 200, 200), width=4)
    person(dr, W, H, 68, 62, 1.4, 3, 'walk')
    return img

def s_money(W, H):
    img, dr = base(W, H, False)
    bag(dr, W, H, 38, 55, 1.6); bag(dr, W, H, 65, 60, 1.1)
    for cx, cy, s in [(20, 25, .8), (80, 25, .9), (55, 15, .7), (88, 45, .6)]:
        coin(dr, W, H, cx, cy, s)
    return img

def s_choice(W, H):
    img, dr = base(W, H, False); ground(dr, W, H, 0.8, (235, 228, 210))
    dr.line([(W * .5, H * .8), (W * .2, H * .3)], fill=GREEN, width=8)
    dr.line([(W * .5, H * .8), (W * .8, H * .3)], fill=RED, width=8)
    person(dr, W, H, 50, 66, 1.3, 0, 'stand')
    coin(dr, W, H, 20, 22, 1.0)
    return img

SCENES = {'intro': s_intro, 'think': s_think, 'grind': s_grind, 'trap': s_trap,
          'chart_up': s_chart_up, 'chart_down': s_chart_down, 'freedom': s_freedom,
          'habit': s_habit, 'money': s_money, 'choice': s_choice,
          'walk': s_grind, 'clock': s_habit}
