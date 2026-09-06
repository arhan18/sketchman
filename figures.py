"""Stick-figure scene library. Each scene = list of strokes.
Stroke = ('line', x1,y1,x2,y2) | ('circle', cx,cy,r) in 0-100 coords.
Hand-drawn feel added at render (wobble subdivision)."""
import math

def man(x, y, s=1.0, pose='stand'):
    """Stick man centered at (x,y). s = scale."""
    h = 8 * s
    parts = [('circle', x, y - h - 4 * s, 4 * s)]
    parts.append(('line', x, y - h, x, y))  # body
    if pose == 'stand':
        parts += [('line', x, y - h + 1, x - 6 * s, y - h + 6 * s),
                  ('line', x, y - h + 1, x + 6 * s, y - h + 6 * s),
                  ('line', x, y, x - 5 * s, y + 9 * s),
                  ('line', x, y, x + 5 * s, y + 9 * s)]
    elif pose == 'walk':
        parts += [('line', x, y - h + 1, x - 7 * s, y - h + 4 * s),
                  ('line', x, y - h + 1, x + 6 * s, y - h + 7 * s),
                  ('line', x, y, x - 7 * s, y + 8 * s),
                  ('line', x, y, x + 4 * s, y + 9 * s)]
    elif pose == 'think':
        parts += [('line', x, y - h + 1, x - 6 * s, y - h + 6 * s),
                  ('line', x, y - h + 1, x + 2 * s, y - h - 2 * s),
                  ('line', x, y, x - 5 * s, y + 9 * s),
                  ('line', x, y, x + 5 * s, y + 9 * s),
                  ('circle', x + 10 * s, y - h - 8 * s, 1.2 * s),
                  ('circle', x + 13 * s, y - h - 12 * s, 1.8 * s)]
    elif pose == 'arms_up':
        parts += [('line', x, y - h + 1, x - 7 * s, y - h - 5 * s),
                  ('line', x, y - h + 1, x + 7 * s, y - h - 5 * s),
                  ('line', x, y, x - 5 * s, y + 9 * s),
                  ('line', x, y, x + 5 * s, y + 9 * s)]
    return parts

def money_bag(x, y, s=1.0):
    return [('circle', x, y, 9 * s),
            ('line', x - 4 * s, y - 9 * s, x - 2 * s, y - 14 * s),
            ('line', x + 4 * s, y - 9 * s, x + 2 * s, y - 14 * s),
            ('line', x - 2 * s, y - 14 * s, x + 2 * s, y - 14 * s),
            ('line', x - 3 * s, y - 2 * s, x + 3 * s, y - 2 * s)]

def chart_up(x0, y0, w=40, h=25):
    pts = [(x0 + i * w / 4, y0 - (i ** 1.6) * h / 10) for i in range(5)]
    lines = [('line', pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1]) for i in range(4)]
    lines.append(('line', x0 - 3, y0 + 3, x0 + w + 3, y0 + 3))
    ax, ay = pts[-1]
    lines += [('line', ax, ay, ax - 4, ay + 1), ('line', ax, ay, ax - 1, ay + 4)]
    return lines

def chart_down(x0, y0, w=40, h=20):
    pts = [(x0 + i * w / 4, y0 - h + (i ** 1.4) * h / 8) for i in range(5)]
    lines = [('line', pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1]) for i in range(4)]
    lines.append(('line', x0 - 3, y0 + 3, x0 + w + 3, y0 + 3))
    return lines

def house(x, y, s=1.0):
    return [('line', x - 10 * s, y, x, y - 10 * s),
            ('line', x, y - 10 * s, x + 10 * s, y),
            ('line', x - 8 * s, y, x - 8 * s, y + 8 * s),
            ('line', x + 8 * s, y, x + 8 * s, y + 8 * s),
            ('line', x - 8 * s, y + 8 * s, x + 8 * s, y + 8 * s)]

def clock(x, y, s=1.0):
    return [('circle', x, y, 9 * s),
            ('line', x, y, x, y - 6 * s),
            ('line', x, y, x + 4 * s, y + 2 * s)]

def trap_box(x, y, s=1.0):
    return [('line', x - 10 * s, y - 8 * s, x + 10 * s, y - 8 * s),
            ('line', x - 10 * s, y - 8 * s, x - 10 * s, y + 8 * s),
            ('line', x + 10 * s, y - 8 * s, x + 10 * s, y + 8 * s),
            ('line', x - 10 * s, y + 8 * s, x - 4 * s, y + 8 * s),
            ('line', x + 4 * s, y + 8 * s, x + 10 * s, y + 8 * s)]

SCENES = {
    'intro': man(50, 55, 1.4, 'arms_up') + money_bag(78, 60, 1.0),
    'think': man(40, 55, 1.4, 'think') + [('circle', 70, 35, 12)] + money_bag(70, 35, 0.8),
    'grind': man(30, 55, 1.2, 'walk') + man(55, 55, 1.2, 'walk') + clock(80, 35, 1.0),
    'trap': man(50, 45, 1.2, 'stand') + trap_box(50, 62, 1.2),
    'chart_up': man(25, 60, 1.1, 'stand') + chart_up(45, 70),
    'chart_down': man(25, 60, 1.1, 'think') + chart_down(45, 65),
    'freedom': man(35, 60, 1.3, 'arms_up') + house(70, 55, 1.0),
    'habit': clock(30, 45, 1.2) + man(65, 58, 1.2, 'walk'),
    'money': money_bag(40, 55, 1.4) + money_bag(65, 60, 1.0),
    'choice': man(50, 40, 1.1, 'stand') + chart_up(15, 80, 25, 15) + chart_down(62, 78, 25, 12),
}
