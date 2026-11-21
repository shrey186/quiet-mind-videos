"""Vibrant 'cosmic transformation' thumbnail style for The Quiet Mind.

Layout (1280x720): cosmic purple/blue nebula, gold particles; LEFT a dim, hunched
'before' silhouette in cold light; a glowing gold arrow; RIGHT a backlit 'after'
silhouette in a radiant gold aura with energy swirls; huge 2-line text at the
bottom (line 1 yellow, line 2 white) with thick black outline + 3D drop.
"""
import math, sys
import numpy as np
import skia
from scipy.ndimage import gaussian_filter, zoom

W, H = 1280, 720
ANTON = skia.Typeface.MakeFromFile("/usr/share/fonts/truetype/google-fonts/ofl/anton/Anton-Regular.ttf")
YELLOW = skia.Color(255, 214, 10)
WHITE = skia.Color(250, 250, 250)
GOLD = skia.Color(255, 196, 60)


def paint(color, a=1.0, blur=0, style=None, width=0):
    p = skia.Paint(AntiAlias=True, Color=skia.ColorSetA(color, int(255 * max(0, min(1, a)))))
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if style == "stroke":
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(width)
        p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join)
    return p


def nebula(seed=1):
    rng = np.random.default_rng(seed)
    def fbm():
        acc = np.zeros((H, W))
        for o, amp in [(6, 1.0), (12, 0.5), (24, 0.25), (48, 0.12), (96, 0.06)]:
            n = rng.random((o * H // W + 2, o + 2))
            up = zoom(n, (H / n.shape[0], W / n.shape[1]), order=3)[:H, :W]
            acc += amp * up
        acc -= acc.min(); acc /= acc.max()
        return acc
    a, b, c = fbm(), fbm(), fbm()
    xs = np.linspace(0, 1, W)[None, :]
    base = np.zeros((H, W, 3))
    deep = np.array([10, 8, 40]); blue = np.array([30, 60, 200]); purple = np.array([120, 40, 190]); magenta = np.array([200, 60, 170])
    mix = (a[..., None] ** 2)
    base = deep * (1 - mix) + (blue * (1 - xs[..., None]) + purple * xs[..., None]) * mix
    base += (magenta * (b ** 4)[..., None]) * 0.55 * xs[..., None]
    base += (np.array([60, 120, 255]) * (c ** 5)[..., None]) * 0.5 * (1 - xs[..., None])
    # stars
    st = np.zeros((H, W))
    idx = rng.integers(0, H * W, 900)
    st.flat[idx] = rng.uniform(0.4, 1.0, 900)
    st = gaussian_filter(st, 0.7) * 6
    base += st[..., None] * 255
    base = np.clip(base * 0.95, 0, 255).astype(np.uint8)
    rgba = np.dstack([base, np.full((H, W), 255, np.uint8)])
    return skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType)


def silhouette(cx, feet, h, hunched=False):
    """A more natural standing human silhouette path."""
    s = h / 100.0
    p = skia.Path()
    head_y = feet - 92 * s + (9 * s if hunched else 0)
    hx = cx + (6 * s if hunched else 0)
    p.addOval(skia.Rect(hx - 6.2 * s, head_y - 7.5 * s, hx + 6.2 * s, head_y + 7.5 * s))
    b = skia.Path()
    sh = feet - 80 * s + (4 * s if hunched else 0)
    b.moveTo(cx - 2.6 * s, sh - 3 * s)
    b.lineTo(cx + 2.6 * s, sh - 3 * s)
    b.cubicTo(cx + 13 * s, sh - 1 * s, cx + 17 * s, sh + 2 * s, cx + 17 * s, sh + 9 * s)  # right shoulder
    b.lineTo(cx + 18 * s, sh + 38 * s)   # right arm outer
    b.lineTo(cx + 14 * s, sh + 40 * s)
    b.lineTo(cx + 12 * s, sh + 14 * s)
    b.lineTo(cx + 11 * s, sh + 42 * s)   # torso right
    b.lineTo(cx + 10 * s, feet - 1 * s)  # right leg
    b.lineTo(cx + 3 * s, feet - 1 * s)
    b.lineTo(cx + 1 * s, sh + 50 * s)
    b.lineTo(cx - 1 * s, sh + 50 * s)
    b.lineTo(cx - 3 * s, feet - 1 * s)   # left leg
    b.lineTo(cx - 10 * s, feet - 1 * s)
    b.lineTo(cx - 11 * s, sh + 42 * s)
    b.lineTo(cx - 12 * s, sh + 14 * s)
    b.lineTo(cx - 14 * s, sh + 40 * s)
    b.lineTo(cx - 18 * s, sh + 38 * s)
    b.lineTo(cx - 17 * s, sh + 9 * s)
    b.cubicTo(cx - 17 * s, sh + 2 * s, cx - 13 * s, sh - 1 * s, cx - 2.6 * s, sh - 3 * s)
    b.close()
    p.addPath(b)
    return p


def swirls(c, cx, cy, r, n=9, seed=4):
    rng = np.random.default_rng(seed)
    for k in range(n):
        path = skia.Path()
        a0 = rng.uniform(0, 2 * math.pi); turns = rng.uniform(0.6, 1.3)
        rr = r * rng.uniform(0.55, 1.1); squash = rng.uniform(0.35, 0.8)
        for i in range(120):
            u = i / 119
            ang = a0 + u * turns * 2 * math.pi
            rad = rr * (0.4 + 0.6 * u)
            x = cx + math.cos(ang) * rad * squash; y = cy + math.sin(ang) * rad
            (path.moveTo if i == 0 else path.lineTo)(x, y)
        c.drawPath(path, paint(GOLD, 0.35, blur=6, style="stroke", width=7))
        c.drawPath(path, paint(skia.Color(255, 240, 190), 0.9, style="stroke", width=2))


def sparks(c, cx, cy, r, n, seed=5, color=GOLD):
    rng = np.random.default_rng(seed)
    for _ in range(n):
        a = rng.uniform(0, 2 * math.pi); d = r * rng.uniform(0, 1) ** 0.6
        x, y = cx + math.cos(a) * d * 0.8, cy + math.sin(a) * d
        sz = rng.uniform(0.8, 3.2)
        c.drawCircle(x, y, sz * 2.5, paint(color, 0.25, blur=3))
        c.drawCircle(x, y, sz, paint(skia.Color(255, 245, 210), rng.uniform(0.6, 1)))


def big_text(c, line, y, size, fill_color, x=None):
    f = skia.Font(ANTON, size)
    w = f.measureText(line)
    x = (W - w) / 2 if x is None else x
    # 3D drop (stacked offsets), thick black outline, then fill with slight top-light gradient
    for d in range(10, 0, -1):
        c.drawString(line, x + d * 0.6, y + d, f, paint(skia.Color(0, 0, 0), 0.9))
    c.drawString(line, x, y, f, paint(skia.Color(0, 0, 0), 1, style="stroke", width=18))
    grad = skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear(
        [(0, y - size * 0.8), (0, y)],
        [fill_color, skia.Color(int(skia.ColorGetR(fill_color) * 0.85), int(skia.ColorGetG(fill_color) * 0.8), int(skia.ColorGetB(fill_color) * 0.7))]))
    c.drawString(line, x, y, f, grad)
    return w


def ornament(c, y):
    c.drawLine(W / 2 - 170, y, W / 2 - 20, y, paint(GOLD, 0.9, style="stroke", width=2))
    c.drawLine(W / 2 + 20, y, W / 2 + 170, y, paint(GOLD, 0.9, style="stroke", width=2))
    p = skia.Path(); p.moveTo(W / 2, y - 12); p.lineTo(W / 2 + 12, y); p.lineTo(W / 2, y + 12); p.lineTo(W / 2 - 12, y); p.close()
    c.drawPath(p, paint(GOLD))
    c.drawCircle(W / 2, y, 22, paint(GOLD, 0.4, blur=10))


def make(line1, line2, out, before_prop=None, seed=1):
    surf = skia.Surface(W, H); c = surf.getCanvas()
    c.drawImage(nebula(seed), 0, 0)
    # BEFORE (left): cold, dim, hunched, behind a fence
    bx, bfeet = 300, 500
    c.drawOval(skia.Rect(bx - 220, bfeet - 380, bx + 220, bfeet + 40), paint(skia.Color(60, 110, 255), 0.35, blur=60))
    c.drawPath(silhouette(bx, bfeet, 300, hunched=True), paint(skia.Color(14, 14, 30)))
    c.drawPath(silhouette(bx, bfeet, 300, hunched=True), paint(skia.Color(120, 150, 255), 0.55, style="stroke", width=2))
    if before_prop == "fence":
        for k in range(-3, 4):
            x = bx + k * 70
            c.drawLine(x, bfeet - 300, x, bfeet + 30, paint(skia.Color(10, 10, 20), 1, style="stroke", width=9))
        for j in range(5):
            yy = bfeet - 40 - j * 55
            c.drawLine(bx - 260, yy, bx + 260, yy + 6, paint(skia.Color(150, 160, 190), 0.75, style="stroke", width=2.5))
    # AFTER (right): radiant gold aura
    ax, afeet = 960, 520
    c.drawCircle(ax, afeet - 190, 330, paint(skia.Color(255, 150, 40), 0.35, blur=90))
    c.drawCircle(ax, afeet - 190, 200, paint(GOLD, 0.65, blur=60))
    c.drawCircle(ax, afeet - 200, 110, paint(skia.Color(255, 245, 210), 0.9, blur=40))
    # rays
    for k in range(28):
        a = k / 28 * 2 * math.pi
        c.drawLine(ax, afeet - 200, ax + math.cos(a) * 420, afeet - 200 + math.sin(a) * 420, paint(skia.Color(255, 220, 140), 0.10, blur=4, style="stroke", width=10))
    swirls(c, ax, afeet - 190, 230)
    sparks(c, ax, afeet - 190, 300, 160)
    c.drawPath(silhouette(ax, afeet, 360), paint(skia.Color(8, 6, 10)))
    c.drawPath(silhouette(ax, afeet, 360), paint(skia.Color(255, 230, 160), 0.9, style="stroke", width=3))
    # golden arrow from before -> after
    arr = skia.Path(); arr.moveTo(450, 330); arr.cubicTo(560, 270, 660, 280, 760, 320)
    c.drawPath(arr, paint(GOLD, 0.5, blur=10, style="stroke", width=26))
    c.drawPath(arr, paint(skia.Color(255, 236, 160), 1, style="stroke", width=10))
    head = skia.Path(); head.moveTo(800, 336); head.lineTo(742, 292); head.lineTo(752, 348); head.close()
    c.drawPath(head, paint(skia.Color(255, 236, 160)))
    sparks(c, 600, 300, 120, 40, seed=9)
    # gold dust bottom-left
    sparks(c, 120, 640, 200, 70, seed=11)
    # darken bottom for text
    c.drawRect(skia.Rect(0, H * 0.55, W, H), skia.Paint(Shader=skia.GradientShader.MakeLinear([(0, H * 0.55), (0, H)], [skia.Color(0, 0, 0, 0), skia.Color(0, 0, 0, 170)])))
    big_text(c, line1, 545, 118, YELLOW)
    big_text(c, line2, 672, 118, WHITE)
    ornament(c, 700)
    surf.makeImageSnapshot().save(out, skia.kPNG)


if __name__ == "__main__":
    make(sys.argv[1], sys.argv[2], sys.argv[3], before_prop=(sys.argv[4] if len(sys.argv) > 4 else None))
