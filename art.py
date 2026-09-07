"""Scene functions: literal illustrations of each beat's nouns.
Each draws exactly what the narration describes — no abstraction.
One scene function per concrete visual need. Topics reference these
by key so scenes stay in sync with the script."""
from PIL import Image, ImageDraw
import math

PAPER = (250, 248, 242)
INK = (30, 30, 40)
FAINT = (160, 160, 170)
GOLD = (205, 145, 15)
GOLD_SOFT = (255, 225, 150)
GREEN, RED = (46, 160, 110), (210, 80, 80)
BLUE_SOFT = (170, 210, 235)
LW = 4


def _u(W, H, s=1.0): return min(W, H) / 100 * s


def _base(W, H):
    return Image.new("RGB", (W, H), PAPER), ImageDraw.Draw(Image.new("RGB", (W, H), PAPER))


# ---------- primitives ----------

def face(dr, X, Y, u, mood='neutral'):
    r = 4 * u
    dr.ellipse([X - r, Y - r, X + r, Y + r], outline=INK, width=LW)  # head
    re = max(1.5, 0.6 * u)
    for sgn in (-1, 1):  # dot eyes
        dr.ellipse([X + sgn * 0.9 * u - re, Y - 1.3 * u - re,
                    X + sgn * 0.9 * u + re, Y - 1.3 * u + re], fill=INK)
    if mood == 'happy':
        dr.arc([X - 2 * u, Y + 0.5 * u, X + 2 * u, Y + 3.5 * u], 10, 170, fill=INK, width=2)
    elif mood == 'sad':
        dr.arc([X - 2 * u, Y + 1.5 * u, X + 2 * u, Y + 3.5 * u], 190, 350, fill=INK, width=2)
    else:
        dr.line([(X - 1.5 * u, Y + 2.4 * u), (X + 1.5 * u, Y + 2.4 * u)], fill=INK, width=2)
    # nose
    dr.line([X, Y - 1.3 * u, X, Y - 0.6 * u], fill=INK, width=2)


def person(dr, X, Y, u, pose='stand', mood='neutral'):
    face(dr, X, Y - 18 * u, u, mood)  # head is 18u above body origin
    dr.line([X, Y - 16 * u, X, Y - 2 * u], fill=INK, width=LW)  # neck
    if pose == 'arms_up':
        arms = [(X - 8 * u, Y - 22 * u), (X + 8 * u, Y - 22 * u)]
        legs = [(X - 5 * u, Y + 8 * u), (X + 5 * u, Y + 8 * u)]
    elif pose == 'walk':
        arms = [(X - 7 * u, Y - 10 * u), (X + 6 * u, Y - 6 * u)]
        legs = [(X - 7 * u, Y + 8 * u), (X + 4 * u, Y + 8 * u)]
    else:
        arms = [(X - 7 * u, Y - 8 * u), (X + 7 * u, Y - 8 * u)]
        legs = [(X - 5 * u, Y + 8 * u), (X + 5 * u, Y + 8 * u)]
    for ax, ay in arms:
        dr.line([X, Y - 13 * u, ax, ay], fill=INK, width=LW)
        dr.ellipse([ax - 1.2 * u, ay - 1.2 * u, ax + 1.2 * u, ay + 1.2 * u], fill=INK)
    for lx, ly in legs:
        dr.line([X, Y - 2 * u, lx, ly], fill=INK, width=LW)
        dr.ellipse([lx - 1.3 * u, ly - 1.3 * u, lx + 1.3 * u, ly + 1.3 * u], fill=INK)


def coin(dr, X, Y, u):
    dr.ellipse([X - 5 * u, Y - 5 * u, X + 5 * u, Y + 5 * u],
               fill=GOLD_SOFT, outline=GOLD, width=LW)
    dr.ellipse([X - 2.5 * u, Y - 2.5 * u, X + 2.5 * u, Y + 2.5 * u],
               outline=GOLD, width=2)
    dr.text((X - 2 * u, Y - 0.8 * u), "$", fill=GOLD)


def bag(dr, X, Y, u):
    pts = [(X - 3 * u, Y - 12 * u), (X + 3 * u, Y - 12 * u),
           (X + 8 * u, Y - 4 * u), (X + 7 * u, Y + 8 * u),
           (X - 7 * u, Y + 8 * u), (X - 8 * u, Y - 4 * u)]
    dr.polygon(pts, fill=GOLD_SOFT, outline=GOLD, width=LW)
    dr.text((X - 3.5 * u, Y - 3 * u), "$$$", fill=GOLD)


def pct(dr, X, Y, val, u, r=18):
    """Draw '10%' style text literally."""
    d = ImageDraw.Draw(dr._image) if hasattr(dr, '_image') else dr
    d.text((X - 7 * u, Y - 4 * u), f"{val}%", fill=GREEN, font_size=int(16 * u / 4))


def horizon(dr, W, H, frac=0.76):
    dr.line([(0, H * frac), (W, H * frac)], fill=FAINT, width=2)


def hatch(dr, x0, y0, x1, y1, col, w=3, space=8):
    """Diagonal hatch fill for bars/charts."""
    if y1 < y0: y0, y1 = y1, y0
    x = x0
    while x < x1:
        dr.line([(x, y0), (x - (y1 - y0), y1)], fill=col, width=w)
        x += space + w * 2


# ---------- concrete scene drawings ----------

def s_bed_alarm(W, H):
    """Beat: alarm rings, snooze, scroll phone."""
    img, dr = _base(W, H)
    horizon(dr, W, H, 0.7)
    # bed: two pillows + blanket rolls
    py = H * 0.58
    dr.rectangle([W * 0.15, py, W * 0.85, py + 18], fill=BLUE_SOFT, outline=INK, width=LW)
    for px in (0.3, 0.5, 0.7):
        dr.ellipse([W * px - 22, py - 14, W * px + 22, py + 4], outline=INK, width=LW)  # pillow
    dr.line([(W * 0.15, py + 12), (W * 0.85, py + 12)], fill=INK, width=2)
    # alarm clock on nightstand
    dr.rectangle([W * 0.28, py - 34, W * 0.36, py - 18], outline=INK, width=LW)
    dr.text((W * 0.30, py - 30), "7:00", fill=INK)
    dr.line([(W * 0.36, py - 28), (W * 0.44, py - 26)], fill=INK, width=3)  # snooze button
    # phone in hand
    px_phone, py_phone = W * 0.68, py - 38
    dr.rectangle([px_phone, py_phone, px_phone + 18, py_phone + 32], outline=INK, width=LW)
    dr.arc([px_phone + 3, py_phone + 4, px_phone + 15, py_phone + 28], 20, 160, fill=INK, width=3)
    return img


def s_sleep_plan(W, H):
    """Beat: wake early, plan, move."""
    img, dr = _base(W, H)
    horizon(dr, W, H, 0.72)
    sun_x, sun_y = W * 0.85, H * 0.12
    dr.ellipse([sun_x - 18, sun_y - 18, sun_x + 18, sun_y + 18], outline=INK, width=3)
    person(dr, W * 0.3, H * 0.66, 0.8, 'stand', 'happy')
    # journal + pen
    dr.rectangle([W * 0.18, H * 0.48, W * 0.32, H * 0.58], fill=(245, 245, 240), outline=INK, width=LW)
    dr.line([(W * 0.24, H * 0.48), (W * 0.25, H * 0.51), (W * 0.30, H * 0.51)], fill=INK, width=2)
    dr.line([W * 0.29, H * 0.50, W * 0.31, H * 0.48], fill=INK, width=2)  # pen
    dr.arc([W * 0.62, H * 0.52, W * 0.76, H * 0.66], 0, 180, fill=FAINT, width=2)  # arc path walking
    return img


def s_split_income(W, H):
    """Beat: same salary, split lives — two wallets."""
    img, dr = _base(W, H)
    horizon(dr, W, H, 0.72)
    mid = W * 0.5
    # Left wallet: empty
    wx, wy = W * 0.18, H * 0.58
    dr.ellipse([wx - 28, wy - 32, wx + 34, wy + 18], fill=(245, 245, 240), outline=INK, width=LW)
    dr.arc([wx, wy - 18, wx + 18, wy - 2], 0, 180, fill=INK, width=2)
    dr.text((wx - 6, wy + 8), "0", fill=RED)
    # Right wallet: full
    wx2 = W * 0.76
    dr.ellipse([wx2 - 28, wy - 32, wx2 + 34, wy + 18], fill=(245, 245, 240), outline=INK, width=LW)
    dr.arc([wx2 - 18, wy - 18, wx2 + 0, wy - 2], 0, 180, fill=INK, width=2)
    for i in range(4):
        coin(dr, wx2 - 10 + i * 8, wy - 8, 0.5)
    person(dr, W * 0.22, H * 0.66, 0.7, 'stand', 'neutral')
    person(dr, W * 0.72, H * 0.66, 0.7, 'stand', 'happy')
    return img


def s_pay_first(W, H):
    """Beat: pay yourself first — salary split, 10% box."""
    img, dr = _base(W, H)
    horizon(dr, W, H, 0.8)
    # salary envelope → two piles
    ex = W * 0.48
    dr.ellipse([ex - 28, H * 0.30, ex + 28, H * 0.40], fill=(245, 245, 240), outline=INK, width=LW)
    dr.text((ex - 6, H * 0.34), "Salary", fill=INK)
    # left arrow → savings jar (10%)
    dr.line([(ex + 28, H * 0.36), (W * 0.70, H * 0.36)], fill=INK, width=3)
    dr.ellipse([W * 0.66, H * 0.28, W * 0.78, H * 0.44], fill=GOLD_SOFT, outline=GOLD, width=LW)
    dr.text((W * 0.70, H * 0.34), "10%", fill=GOLD)
    # right arrow → spend pile
    dr.line([(ex - 28, H * 0.36), (W * 0.28, H * 0.36)], fill=INK, width=3)
    dr.ellipse([W * 0.24, H * 0.26, W * 0.36, H * 0.42], fill=BLUE_SOFT, outline=INK, width=LW)
    dr.text((W * 0.28, H * 0.34), "90%", fill=INK)
    person(dr, ex, H * 0.52, 0.85)
    return img


def s_compound(W, H):
    """Beat: small money compounds — piggy bank + growing pile."""
    img, dr = _base(W, H)
    horizon(dr, W, H, 0.76)
    bx, by = W * 0.30, H * 0.52
    dr.ellipse([bx - 30, by - 38, bx + 30, by + 10], fill=(245, 245, 240), outline=INK, width=LW)
    dr.text((bx - 8, by - 14), "Piggy", fill=INK)
    dr.arc([bx - 18, by - 22, bx + 18, by - 4], 200, 340, fill=INK, width=3)  # slot
    # coins falling from sky
    for i in range(4):
        coin(dr, bx + 0.62 * (i - 2) * 28, by - 12 - i * 8, 0.4)
    # growing pile under
    base_y = by + 10
    for i in range(6):
        coin(dr, bx - 24 + i * 10, base_y + i * 2, 0.35)
    # chart rising
    x0, y0, w, h = W * 0.58, H * 0.62, W * 0.36, H * 0.22
    pts = [(x0 + t * w, y0 - (t ** 1.7) * h) for t in [i / 5 for i in range(6)]]
    dr.line(pts, fill=GREEN, width=7, joint="curve")
    return img


def s_compare(W, H):
    """Beat: two people, different outcome — one working, one free."""
    img, dr = _base(W, H)
    horizon(dr, W, H, 0.74)
    person(dr, W * 0.28, H * 0.60, 0.85, 'walk', 'neutral')  # grinding
    person(dr, W * 0.62, H * 0.60, 0.85, 'arms_up', 'happy')  # free
    dr.line([(W * 0.22, H * 0.64), (W * 0.28, H * 0.52)], fill=INK, width=3)  # bag strap
    dr.line([(W * 0.68, H * 0.44), (W * 0.72, H * 0.60)], fill=FAINT, width=4)  # sunhat/cloud
    return img


def s_choice_forks(W, H):
    """Beat: rich vs broke mindset — two paths."""
    img, dr = _base(W, H)
    horizon(dr, W, H, 0.8)
    px, py = W * 0.5, H * 0.72
    person(dr, px, H * 0.52, 0.8)
    dr.line([(px, H * 0.68), (W * 0.2, H * 0.30)], fill=GREEN, width=8)   # up
    dr.line([(px, H * 0.68), (W * 0.8, H * 0.30)], fill=RED, width=8)    # down
    return img


def s_buy_time(W, H):
    """Beat: buy back time vs buy stuff — two receipts."""
    img, dr = _base(W, H)
    horizon(dr, W, H, 0.72)
    person(dr, W * 0.30, H * 0.6, 0.8, 'stand', 'neutral')
    # receipt fading
    dr.rectangle([W * 0.10, H * 0.40, W * 0.26, H * 0.46], outline=FAINT, width=2)
    dr.text((W * 0.12, H * 0.41), "stuff...", fill=FAINT)
    # receipt paying
    dr.rectangle([W * 0.66, H * 0.40, W * 0.88, H * 0.46], outline=GOLD, width=LW)
    dr.text((W * 0.70, H * 0.41), "time", fill=GOLD)
    return img


def s_start_now(W, H):
    """Beat: start today with pocket change."""
    img, dr = _base(W, H)
    horizon(dr, W, H, 0.76)
    person(dr, W * 0.50, H * 0.60, 1.0, 'stand', 'neutral')
    # coins in hand
    for i, off in enumerate([-14, -6, 2, 10]):
        coin(dr, W * 0.42 + off, H * 0.54, 0.4)
    return img


def s_bank_diary(W, H):
    """Beat: bank statement as diary."""
    img, dr = _base(W, H)
    horizon(dr, W, H, 0.8)
    # ledger book
    bx, by = W * 0.40, H * 0.40
    dr.rectangle([bx - 36, by, bx + 36, by + 60], fill=(245, 245, 240), outline=INK, width=LW)
    for i in range(6):
        dr.line([(bx - 28, by + 10 + i * 9), (bx + 28, by + 10 + i * 9)], fill=FAINT, width=2)
    dr.text((bx - 6, by + 64), "Diary", fill=INK)
    person(dr, W * 0.48, H * 0.62, 0.8)
    return img


def s_phone_scroll(W, H):
    """Beat: open phone, see subscriptions."""
    img, dr = _base(W, H)
    ph_x, ph_y = W * 0.50, H * 0.40
    dr.rectangle([ph_x - 26, ph_y, ph_x + 26, ph_y + 52], fill=(245, 245, 240), outline=INK, width=LW)
    dr.rounded_rectangle([ph_x - 22, ph_y + 6, ph_x + 22, ph_y + 46], radius=4, fill=(240, 240, 245))
    # three subscription pills
    for i, col in enumerate([RED, GREEN, BLUE_SOFT]):
        sy = ph_y + 14 + i * 10
        dr.ellipse([ph_x - 16, sy - 4, ph_x + 16, sy + 4], fill=col)
    person(dr, W * 0.50, H * 0.70, 0.9, 'stand', 'neutral')
    return img


def s_spreadsheet(W, H):
    """Beat: forty columns blink."""
    img, dr = _base(W, H)
    horizon(dr, W, H, 0.8)
    sx, sy = W * 0.50, H * 0.34
    sw, sh = W * 0.52, H * 0.42
    dr.rectangle([sx - sw / 2, sy, sx + sw / 2, sy + sh], fill=(245, 245, 240), outline=INK, width=LW)
    cols = 14
    for i in range(cols):
        cx = sx - sw / 2 + (i + 1) * sw / (cols + 1)
        dr.line([(cx, sy + 6), (cx, sy + sh - 6)], fill=FAINT, width=2)
    rows = 4
    for i in range(rows):
        ry = sy + 10 + i * (sh - 20) / (rows + 1)
        dr.line([(sx - sw / 2 + 6, ry), (sx + sw / 2 - 6, ry)], fill=FAINT, width=2)
    person(dr, W * 0.40, H * 0.72, 0.8, 'stand', 'neutral')
    return img


def s_three_lines(W, H):
    """Beat: tear up spreadsheet, three lines on paper."""
    img, dr = _base(W, H)
    horizon(dr, W, H, 0.82)
    # crumpled spreadsheet in trash
    dr.rectangle([W * 0.70, H * 0.28, W * 0.86, H * 0.52], fill=(240, 240, 245), outline=RED, width=2)
    dr.text((W * 0.74, H * 0.30), "X", fill=RED)  # torn
    # clean paper with 3 lines
    px, py = W * 0.40, H * 0.46
    dr.rectangle([px - 32, py, px + 32, py + 44], fill=(250, 248, 242), outline=INK, width=LW)
    dr.line([(px - 24, py + 9), (px + 24, py + 9)], fill=INK, width=3)  # income
    dr.line([(px - 24, py + 22), (px + 24, py + 22)], fill=INK, width=3)  # expenses
    dr.line([(px - 24, py + 35), (px + 24, py + 35)], fill=INK, width=3)  # savings
    dr.text((px - 6, py + 9), "I", fill=INK)
    dr.text((px - 6, py + 22), "E", fill=INK)
    dr.text((px + 16, py + 35), "$", fill=GREEN)
    return img


def s_leak(W, H):
    """Beat: leak in budget — drip from pipe into bucket."""
    img, dr = _base(W, H)
    horizon(dr, W, H, 0.82)
    # bucket catching drip
    bx, by = W * 0.34, H * 0.50
    dr.ellipse([bx - 30, by, bx + 30, by + 24], fill=BLUE_SOFT, outline=INK, width=LW)
    dr.line([bx - 24, by + 8, bx + 24, by + 8], fill=INK, width=2)
    dr.line([(bx, by + 8), (bx, by + 24)], fill=INK, width=3)  # handle
    # drip
    dr.ellipse([bx - 3, by + 22, bx + 3, by + 28], fill=BLUE_SOFT)
    # pipe overhead leaking
    dr.line([(W * 0.20, H * 0.30), (W * 0.80, H * 0.30)], fill=FAINT, width=4)
    dr.line([(W * 0.55, H * 0.30), (W * 0.55, H * 0.50)], fill=FAINT, width=3)
    dr.arc([W * 0.48, H * 0.44, W * 0.62, H * 0.56], 0, 180, fill=GOLD, width=3)  # leak splat
    return img


def s_stock_vs_index(W, H):
    """Beat: hot stock up then down vs steady index up."""
    img, dr = _base(W, H)
    horizon(dr, W, H, 0.82)
    x0, y0, w, h = W * 0.20, H * 0.58, W * 0.26, H * 0.18
    # stock line: spike then crash
    pts = [(x0, y0), (x0 + w * 0.3, y0 - h), (x0 + w * 0.5, y0 + h * 0.4),
           (x0 + w, y0 + h * 0.2)]
    dr.line(pts, fill=RED, width=7, joint="curve")
    # index line: slow climb
    ix0, iy0 = W * 0.60, H * 0.58
    ipts = [(ix0 + t * w * 0.8, iy0 - (t ** 1.7) * h * 0.5) for t in [i / 4 for i in range(5)]]
    dr.line(ipts, fill=GREEN, width=7, joint="curve")
    # labels
    dr.text((x0 + w * 0.45, y0 - h - 16), "Stock", fill=RED)
    dr.text((ix0 + 4, iy0 - 4), "Index", fill=GREEN)
    return img


def s_reminder(W, H):
    """Beat: set one calendar reminder."""
    img, dr = _base(W, H)
    horizon(dr, W, H, 0.84)
    # phone showing calendar
    px, py = W * 0.52, H * 0.26
    dr.rectangle([px - 26, py, px + 26, py + 48], fill=(245, 245, 240), outline=INK, width=LW)
    dr.text((px - 4, py + 6), "Cal", fill=INK)
    dr.ellipse([px, py + 16, px + 20, py + 32], fill=GOLD)
    dr.text((px + 2, py + 18), "!", fill=INK)
    dr.text((px + 4, py + 36), "1x", fill=INK)  # reminder badge
    person(dr, W * 0.34, H * 0.68, 0.85, 'stand', 'neutral')
    return img


def s_clock_min(W, H):
    """Beat: nine minutes a day — clock face with 9 highlighted."""
    img, dr = _base(W, H)
    horizon(dr, W, H, 0.72)
    cx, cy, R = W * 0.50, H * 0.48, 40
    dr.ellipse([cx - R, cy - R, cx + R, cy + R], outline=INK, width=LW)
    dr.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=INK)  # center
    for h in range(12):
        import math
        a = math.radians(h * 30 - 90)
        dr.line([(cx + (R - 6) * math.cos(a), cy + (R - 6) * math.sin(a)),
                 (cx + R * math.cos(a), cy + R * math.sin(a))], fill=INK, width=2)
    # highlight 9
    a9 = math.radians(9 * 30 - 90)
    dr.ellipse([cx + (R + 4) * math.cos(a9) - 8, cy + (R + 4) * math.sin(a9) - 8,
                cx + (R + 4) * math.cos(a9) + 8, cy + (R + 4) * math.sin(a9) + 8],
               outline=GOLD, width=3)
    return img


def s_walk_away(W, H):
    """Beat: walking away / choosing."""
    img, dr = _base(W, H)
    horizon(dr, W, H, 0.68)
    person(dr, W * 0.44, H * 0.56, 0.85, 'walk', 'neutral')
    # TV remote on couch
    dr.rectangle([W * 0.20, H * 0.74, W * 0.32, H * 0.86], fill=(240, 240, 245), outline=INK, width=LW)
    dr.ellipse([W * 0.28, H * 0.78, W * 0.31, H * 0.81], fill=INK)
    return img


def s_door(W, H):
    """Beat: exit door behind TV remote."""
    img, dr = _base(W, H)
    horizon(dr, W, H, 0.78)
    person(dr, W * 0.50, H * 0.56, 0.85, 'stand', 'neutral')
    # door
    dx, dy = W * 0.42, H * 0.36
    dr.rectangle([dx - 24, dy, dx + 24, dy + 48], fill=BLUE_SOFT, outline=INK, width=LW)
    dr.arc([dx - 18, dy + 6, dx + 18, dy + 42], 180, 0, fill=INK, width=3)  # open arc
    return img


def s_empty_wallet(W, H):
    """Beat: wallet with nothing left — alarm bells."""
    img, dr = _base(W, H)
    horizon(dr, W, H, 0.80)
    bx, by = W * 0.50, H * 0.50
    dr.ellipse([bx - 34, by - 36, bx + 34, by + 12], fill=(245, 245, 240), outline=INK, width=LW)
    dr.text((bx - 4, by - 8), "0.00", fill=RED)
    dr.text((bx - 8, by + 6), "0.00", fill=RED)
    person(dr, W * 0.46, H * 0.62, 0.85, 'stand', 'sad')
    # alarm bells
    for bx2 in (W * 0.64, W * 0.72):
        dr.arc([bx2 - 12, H * 0.34, bx2 + 12, H * 0.50], 30, 150, fill=INK, width=3)
        dr.ellipse([bx2 - 2, H * 0.30, bx2 + 2, H * 0.34], fill=INK)
    return img


def s_cheat_sheet(W, H):
    """Beat: 9-minute habit cheat sheet — simple card."""
    img, dr = _base(W, H)
    horizon(dr, W, H, 0.86)
    cx, cy = W * 0.50, H * 0.42
    dr.rectangle([cx - 42, cy - 26, cx + 42, cy + 26], fill=(250, 248, 242), outline=GREEN, width=LW)
    dr.text((cx - 30, cy - 14), "9 min", fill=GREEN)
    dr.text((cx - 26, cy - 2), "write", fill=INK)
    dr.text((cx - 22, cy + 8), "rupees", fill=INK)
    dr.text((cx - 28, cy + 18), "save first", fill=GREEN)
    person(dr, W * 0.46, H * 0.66, 0.85, 'stand', 'neutral')
    return img


def s_chart_up_money(W, H):
    """Beat: money growing — coins + upward chart."""
    img, dr = _base(W, H)
    horizon(dr, W, H, 0.76)
    x0, y0, w, h = W * 0.48, H * 0.56, W * 0.40, H * 0.20
    pts = [(x0 + t * w, y0 - (t ** 1.7) * h) for t in [i / 5 for i in range(6)]]
    dr.line(pts, fill=GREEN, width=7, joint="curve")
    for i in range(5):
        coin(dr, W * 0.30 + i * 12, y0 - 4, 0.3)
    return img


def s_chart_down(W, H):
    """Beat: decline — downward chart."""
    img, dr = _base(W, H)
    horizon(dr, W, H, 0.76)
    x0, y0, w, h = W * 0.40, H * 0.52, W * 0.48, H * 0.22
    pts = [(x0 + t * w, y0 + (t ** 1.3) * h) for t in [i / 5 for i in range(6)]]
    dr.line(pts, fill=RED, width=7, joint="curve")
    dr.ellipse([pts[-1][0] - 8, pts[-1][1] - 8, pts[-1][0] + 8, pts[-1][1] + 8],
               fill=RED)
    return img


def s_raise(W, H):
    """Beat: raises feed lifestyle — paycheck spent."""
    img, dr = _base(W, H)
    horizon(dr, W, H, 0.78)
    ex = W * 0.50
    dr.ellipse([ex - 30, H * 0.30, ex + 30, H * 0.42], fill=(245, 245, 240), outline=GREEN, width=LW)
    dr.text((ex - 6, H * 0.34), "+$500", fill=GREEN)
    # arrows going to lifestyle icons
    person(dr, ex, H * 0.48, 0.8)
    # shopping bag
    bag(dr, ex + 40, H * 0.42, 0.7)
    # phone upgrade
    dr.rectangle([ex + 60, H * 0.34, ex + 78, H * 0.50], fill=BLUE_SOFT, outline=INK, width=3)
    dr.arc([ex + 64, H * 0.38, ex + 74, H * 0.48], 30, 150, fill=INK, width=2)  # camera
    return img


def s_subscriptions(W, H):
    """Beat: subscriptions list on phone."""
    img, dr = _base(W, H)
    sx, sy = W * 0.52, H * 0.32
    dr.rectangle([sx - 26, sy, sx + 26, sy + 52], fill=(245, 245, 240), outline=INK, width=LW)
    # pills
    for i, col in enumerate([RED, GOLD, GREEN]):
        sy2 = sy + 8 + i * 12
        dr.ellipse([sx - 18, sy2 - 4, sx + 18, sy2 + 4], fill=col)
        dr.text((sx - 12, sy2 - 3), ["NF", "Spotify", "Gym"][i], fill=INK)
    person(dr, W * 0.42, H * 0.66, 0.85, 'stand', 'worried')
    return img


def s_money_account(W, H):
    """Beat: 10% auto-transfer — separate account grows."""
    img, dr = _base(W, H)
    horizon(dr, W, H, 0.8)
    # two account jars
    ax1, ax2 = W * 0.30, W * 0.68
    ay = H * 0.52
    for ax, col, label in [(ax1, RED, "Spend"), (ax2, GOLD, "Save 10%")]:
        dr.ellipse([ax - 30, ay - 30, ax + 30, ay + 8], fill=(245, 245, 240), outline=INK, width=LW)
        coin_x = ax - 22
        for i in range(3):
            coin(dr, coin_x, ay - 8, 0.35)
            coin_x += 16
        dr.text((ax - 14, ay + 12), label, fill=col)
    # transfer arrow
    dr.line([(ax1 + 34, ay - 6), (ax2 - 26, ay - 6)], fill=INK, width=3)
    dr.polygon([(ax2 - 30, ay - 10), (ax2 - 22, ay - 8), (ax2 - 30, ay - 6)], fill=INK)
    return img


def s_countdown(W, H):
    """Beat: 21-day interest clock counting down."""
    img, dr = _base(W, H)
    horizon(dr, W, H, 0.80)
    cx, cy = W * 0.50, H * 0.42
    dr.ellipse([cx - 50, cy - 50, cx + 50, cy + 50], outline=INK, width=LW)
    # numbers 1-23 around edge, 21 highlighted
    import math
    for d in range(1, 24):
        a = math.radians(d * 15 - 90)
        txt = str(d)
        col = RED if d == 21 else FAINT
        dr.text((cx + 40 * math.cos(a) - 6, cy + 40 * math.sin(a) - 6), txt, fill=col)
    dr.text((cx - 8, cy - 12), "21", fill=GOLD)
    dr.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=RED)  # alarm dot
    return img


def s_calendar_grid(W, H):
    """Beat: calendar grid / thirty days traded for one payday."""
    img, dr = _base(W, H)
    horizon(dr, W, H, 0.82)
    cx, cy = W * 0.48, H * 0.42
    gw, gh, cells = W * 0.44, H * 0.18, 7
    dr.rectangle([cx - gw / 2, cy - gh / 2, cx + gw / 2, cy + gh / 2],
                 fill=(245, 245, 240), outline=INK, width=LW)
    for i in range(1, cells):
        dr.line([(cx - gw / 2 + i * gw / cells, cy - gh / 2),
                 (cx - gw / 2 + i * gw / cells, cy + gh / 2)], fill=FAINT, width=2)
    for i in range(1, 3):
        dr.line([(cx - gw / 2, cy - gh / 2 + i * gh / 3),
                 (cx + gw / 2, cy - gh / 2 + i * gh / 3)], fill=FAINT, width=2)
    dr.text((cx - 6, cy + 1), "1 Payday", fill=GOLD)
    person(dr, cx, H * 0.60, 0.8)
    return img


def s_brick(W, H):
    """Beat: building exit-bricks one at a time."""
    img, dr = _base(W, H)
    horizon(dr, W, H, 0.84)
    bx = [W * 0.22, W * 0.38, W * 0.54, W * 0.70]
    by = H * 0.58
    for i, b in enumerate(bx):
        # brick shape (rounded rect)
        dr.rounded_rectangle([b - 32, by - 18, b + 32, by + 18], radius=6,
                             fill=GOLD_SOFT, outline=GOLD, width=LW)
        dr.text((b - 6, by - 2), str(i + 1), fill=GOLD)
    dr.line([(bx[3] + 32, by), (bx[3] + 60, by - 6)], fill=INK, width=3)  # mortar
    return img


def s_leash(W, H):
    """Beat: salary as a leash — one boss controls all income."""
    img, dr = _base(W, H)
    horizon(dr, W, H, 0.80)
    person(dr, W * 0.46, H * 0.58, 0.85, 'stand', 'worried')
    # boss figure with leash line
    dr.ellipse([W * 0.76 - 18, H * 0.38 - 18, W * 0.76 + 18, H * 0.38 + 18],
               outline=INK, width=LW)  # boss head
    dr.line([(W * 0.76, H * 0.40), (W * 0.46, H * 0.42)], fill=INK, width=5)  # leash
    dr.rectangle([W * 0.72, H * 0.52, W * 0.80, H * 0.66], fill=(240, 240, 245), outline=INK, width=3)  # payslip sign
    dr.text((W * 0.73, H * 0.56), "$", fill=INK)
    return img


def s_remote_door(W, H):
    """Beat: exit door behind the TV remote — hidden opportunity."""
    img, dr = _base(W, H)
    horizon(dr, W, H, 0.80)
    person(dr, W * 0.50, H * 0.56, 0.85, 'stand', 'neutral')
    # TV / remote in foreground left
    dr.rectangle([W * 0.12, H * 0.66, W * 0.34, H * 0.88], fill=(235, 235, 240), outline=INK, width=LW)
    dr.ellipse([W * 0.20, H * 0.76, W * 0.28, H * 0.82], fill=INK)  # screen
    dr.ellipse([W * 0.26, H * 0.80, W * 0.31, H * 0.85], fill=0)  # button glow
    # open door in background right
    dx = W * 0.74
    dr.rectangle([dx - 4, H * 0.30, dx + 30, H * 0.78], fill=BLUE_SOFT, outline=INK, width=LW)
    dr.arc([dx - 2, H * 0.30, dx + 28, H * 0.78], 180, 0, fill=FAINT, width=2)  # door swing gap
    return img


def s_freedom(W, H):
    """Beat: person free, arms up, sun + birds (climax scene)."""
    img, dr = _base(W, H)
    _sx_s, _sy_s = W * 0.85, H * 0.12
    dr.ellipse([_sx_s - 18, _sy_s - 18, _sx_s + 18, _sy_s + 18], outline=FAINT, width=LW)
    for a in (0, 30, 60, 90):  # sun rays
        import math
        c, sn = math.cos(math.radians(a)), math.sin(math.radians(a))
        dr.line([(_sx_s + c * 24, _sy_s + sn * 24),
                 (_sx_s + c * 36, _sy_s + sn * 36)], fill=FAINT, width=2)
    horizon(dr, W, H, 0.72)
    person(dr, W * 0.44, H * 0.56, 1.0, 'arms_up', 'happy')
    bag(dr, W * 0.72, H * 0.44, 0.9)
    return img


SCENES = {
    'bed_alarm': s_bed_alarm,
    'sleep_plan': s_sleep_plan,
    'split_income': s_split_income,
    'pay_first': s_pay_first,
    'compound': s_compound,
    'compare': s_compare,
    'choice_forks': s_choice_forks,
    'buy_time': s_buy_time,
    'start_now': s_start_now,
    'bank_diary': s_bank_diary,
    'phone_scroll': s_phone_scroll,
    'spreadsheet': s_spreadsheet,
    'three_lines': s_three_lines,
    'leak': s_leak,
    'stock_vs_index': s_stock_vs_index,
    'reminder': s_reminder,
    'clock_min': s_clock_min,
    'walk_away': s_walk_away,
    'door': s_door,
    'empty_wallet': s_empty_wallet,
    'cheat_sheet': s_cheat_sheet,
    'chart_up': s_chart_up_money,
    'chart_down': s_chart_down,
    'raise': s_raise,
    'subscriptions': s_subscriptions,
    'money_account': s_money_account,
    'countdown': s_countdown,
    'calendar_grid': s_calendar_grid,
    'brick': s_brick,
    'leash': s_leash,
    'remote_door': s_remote_door,
    'freedom': s_freedom,
}

BEAT_WALK = ("bed_alarm",)  # fallback scene key alias
