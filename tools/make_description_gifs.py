"""Draws the animated images of the AnkiWeb description into docs/description/.

AnkiWeb strips styles and scripts from add-on descriptions, so animation has to
come from the images. Run from the repo root:  python -I tools/make_description_gifs.py
Needs: Pillow with Raqm, and the Vazirmatn font for the Persian text.
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "description")
BOLD = "/usr/share/fonts/vazirmatn/Vazirmatn-Bold.ttf"
REGULAR = "/usr/share/fonts/vazirmatn/Vazirmatn-Regular.ttf"
SCALE = 2  # drawn larger, then reduced for smooth edges

BG_TOP, BG_BOTTOM = (10, 14, 34), (20, 34, 74)
PANEL, LINE = (30, 41, 74), (58, 72, 118)
TEXT, MUTED = (240, 244, 255), (160, 174, 210)
BLUE, CYAN, ORANGE, GREEN, PINK = (64, 150, 255), (72, 214, 232), (255, 150, 60), (84, 214, 138), (236, 100, 200)


def font(size, bold=True):
    return ImageFont.truetype(BOLD if bold else REGULAR, size * SCALE)


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def mix(a, b, t):
    return tuple(int(x + (y - x) * t) for x, y in zip(a, b))


def background(w, h):
    img = Image.new("RGB", (w * SCALE, h * SCALE))
    d = ImageDraw.Draw(img)
    for y in range(h * SCALE):
        d.line([(0, y), (w * SCALE, y)], fill=mix(BG_TOP, BG_BOTTOM, y / (h * SCALE)))
    return img


def glow(img, x, y, r, color, strength):
    layer = Image.new("RGB", img.size, (0, 0, 0))
    ImageDraw.Draw(layer).ellipse([(x - r) * SCALE, (y - r) * SCALE, (x + r) * SCALE, (y + r) * SCALE], fill=color)
    layer = layer.filter(ImageFilter.GaussianBlur(r * SCALE * 0.6))
    return Image.blend(img, Image.fromarray(_add(img, layer, strength)), 1.0)


def _add(a, b, s):
    import numpy as np
    return np.clip(np.asarray(a, dtype="int16") + (np.asarray(b, dtype="int16") * s).astype("int16"), 0, 255).astype("uint8")


def rect(d, box, radius, **kw):
    d.rounded_rectangle([v * SCALE for v in box], radius=radius * SCALE, **kw)


def text(d, xy, s, f, fill, anchor="la", **kw):
    d.text((xy[0] * SCALE, xy[1] * SCALE), s, font=f, fill=fill, anchor=anchor, **kw)


def save(name, frames, ms):
    """Shares one palette across frames, which keeps gradients calm and files small."""
    small = [f.resize((f.width // SCALE, f.height // SCALE), Image.LANCZOS) for f in frames]
    sheet = Image.new("RGB", (small[0].width, small[0].height * min(8, len(small))))
    for i in range(min(8, len(small))):
        sheet.paste(small[i * len(small) // min(8, len(small))], (0, i * small[0].height))
    palette = sheet.quantize(colors=200, method=Image.Quantize.MEDIANCUT)
    frames_p = [f.quantize(palette=palette, dither=Image.Dither.NONE) for f in small]
    path = os.path.join(OUT, name)
    frames_p[0].save(path, save_all=True, append_images=frames_p[1:], duration=ms, loop=0, optimize=True, disposal=1)
    print(name, len(frames), "frames", os.path.getsize(path) // 1024, "KiB")


def hero():
    w, h, n = 720, 250, 60
    random.seed(7)
    dots = [(random.uniform(0, w), random.uniform(0, h), random.uniform(1, 2.6), random.choice((BLUE, CYAN, ORANGE, PINK)),
             random.randint(1, 2) * random.choice((-1, 1))) for _ in range(46)]
    words = [("Your whole study workflow", False), ("همهٔ مطالعهٔ شما در یک افزونه", True), ("Dein ganzes Lernen", False)]
    base = background(w, h)
    frames = []
    for i in range(n):
        t = i / n
        img = glow(base, 150 + 40 * math.sin(t * math.tau), 110, 120, BLUE, 0.28)
        img = glow(img, 590 - 40 * math.sin(t * math.tau), 150, 110, ORANGE, 0.16)
        d = ImageDraw.Draw(img)
        for x, y, r, c, v in dots:
            yy = (y + v * t * h) % h
            a = 0.45 + 0.55 * abs(math.sin(t * math.tau + x))
            col = mix(BG_BOTTOM, c, a)
            d.ellipse([(x - r) * SCALE, (yy - r) * SCALE, (x + r) * SCALE, (yy + r) * SCALE], fill=col)
        # logo: an open book that gently floats
        cy = 72 + 4 * math.sin(t * math.tau)
        rect(d, (w / 2 - 28, cy - 28, w / 2 + 28, cy + 28), 14, fill=BLUE)
        pts = lambda s: [((w / 2) * SCALE, (cy - 13) * SCALE), ((w / 2 + s * 18) * SCALE, (cy - 18) * SCALE),
                         ((w / 2 + s * 18) * SCALE, (cy + 12) * SCALE), ((w / 2) * SCALE, (cy + 17) * SCALE)]
        d.line(pts(1) + [pts(1)[0]], fill=TEXT, width=3 * SCALE, joint="curve")
        d.line(pts(-1) + [pts(-1)[0]], fill=TEXT, width=3 * SCALE, joint="curve")
        text(d, (w / 2, 118), "Smart Study", font(40), TEXT, "ma")
        # cycling tagline
        k = int(t * len(words))
        local = t * len(words) - k
        fade = ease(local / 0.18) * ease((1 - local) / 0.18)
        s, rtl = words[k]
        col = mix(BG_BOTTOM, CYAN, fade)
        kw = {"direction": "rtl", "language": "fa"} if rtl else {}
        text(d, (w / 2, 182 + (1 - fade) * 6), s, font(22, False), col, "ma", **kw)
        # shimmer line
        lx = (t * 1.4 - 0.2) * w
        d.line([(w / 2 - 150) * SCALE, 224 * SCALE, (w / 2 + 150) * SCALE, 224 * SCALE], fill=LINE, width=SCALE)
        if w / 2 - 150 < lx < w / 2 + 150:
            d.line([(max(w / 2 - 150, lx - 60)) * SCALE, 224 * SCALE, min(w / 2 + 150, lx) * SCALE, 224 * SCALE], fill=CYAN, width=2 * SCALE)
        frames.append(img)
    save("hero.gif", frames, 70)


def persian_flip():
    w, h, n = 720, 270, 64
    base = background(w, h)
    rows = [("Study plan", "برنامهٔ مطالعه"), ("Notebook", "دفترچه"), ("Mind map", "نقشهٔ ذهنی"), ("Statistics", "آمار")]
    frames = []
    for i in range(n):
        t = i / n
        flip = ease((t - 0.2) / 0.16) * (1 - ease((t - 0.82) / 0.14))  # 0 = English, 1 = Persian
        img = base.copy()
        d = ImageDraw.Draw(img)
        x0, y0, x1, y1 = 40, 24, w - 40, h - 24
        rect(d, (x0, y0, x1, y1), 16, fill=PANEL, outline=LINE, width=SCALE)
        side_w = 180
        sx = x0 + 10 + flip * (x1 - x0 - side_w - 20)
        rect(d, (sx, y0 + 10, sx + side_w, y1 - 10), 10, fill=(23, 32, 62))
        fa = flip > 0.5
        local = abs(flip - 0.5) * 2
        for r, (en, per) in enumerate(rows):
            y = y0 + 22 + r * 46
            active = r == (i // 16) % 4
            if active:
                rect(d, (sx + 8, y, sx + side_w - 8, y + 38), 8, fill=BLUE)
            col = mix(PANEL, TEXT, local)
            if fa:
                d.ellipse([(sx + side_w - 34) * SCALE, (y + 13) * SCALE, (sx + side_w - 22) * SCALE, (y + 25) * SCALE], fill=col)
                text(d, (sx + side_w - 44, y + 7), per, font(15), col, "ra", direction="rtl", language="fa")
            else:
                d.ellipse([(sx + 22) * SCALE, (y + 13) * SCALE, (sx + 34) * SCALE, (y + 25) * SCALE], fill=col)
                text(d, (sx + 44, y + 9), en, font(14), col)
        cx0 = x0 + 10 + (1 - flip) * (side_w + 10) + 10
        cx1 = cx0 + (x1 - x0 - side_w - 50)
        col = mix(PANEL, TEXT, local)
        sub = mix(PANEL, MUTED, local)
        if fa:
            text(d, (cx1, y0 + 20), "زبان فارسی اضافه شد", font(24), col, "ra", direction="rtl", language="fa")
            text(d, (cx1, y0 + 62), "همه‌چیز از راست به چپ", font(15, False), sub, "ra", direction="rtl", language="fa")
        else:
            text(d, (cx0, y0 + 22), "Now in Persian", font(24), col)
            text(d, (cx0, y0 + 64), "The whole layout flips right to left", font(15, False), sub)
        for r in range(3):
            y = y0 + 110 + r * 34
            fill = 0.35 + 0.2 * r + 0.15 * math.sin(t * math.tau + r)
            rect(d, (cx0, y, cx1, y + 16), 8, fill=(23, 32, 62))
            bar = (cx1 - cx0) * fill
            if fa:
                rect(d, (cx1 - bar, y, cx1, y + 16), 8, fill=(BLUE, CYAN, ORANGE)[r])
            else:
                rect(d, (cx0, y, cx0 + bar, y + 16), 8, fill=(BLUE, CYAN, ORANGE)[r])
        frames.append(img)
    save("persian.gif", frames, 75)


def tiles():
    w, h, n = 720, 210, 70
    base = background(w, h)
    labels = ["Study plan", "Review heatmap", "Focus timer", "Level up"]
    tile_w = (w - 20 * 5) / 4
    frames = []
    random.seed(3)
    heat = [[random.random() for _ in range(7)] for _ in range(10)]
    for i in range(n):
        t = i / n
        img = base.copy()
        d = ImageDraw.Draw(img)
        for k, label in enumerate(labels):
            x = 20 + k * (tile_w + 20)
            rect(d, (x, 20, x + tile_w, h - 20), 14, fill=PANEL, outline=LINE, width=SCALE)
            text(d, (x + tile_w / 2, h - 50), label, font(14), TEXT, "ma")
            cx, cy = x + tile_w / 2, 84
            if k == 0:  # items tick themselves off
                for r in range(4):
                    y = 40 + r * 24
                    done = t > 0.1 + r * 0.17
                    pop = ease((t - 0.1 - r * 0.17) / 0.06)
                    d.ellipse([(x + 18) * SCALE, y * SCALE, (x + 34) * SCALE, (y + 16) * SCALE],
                              fill=mix(PANEL, GREEN, pop) if done else PANEL, outline=GREEN if done else LINE, width=2 * SCALE)
                    if done:
                        d.line([(x + 22) * SCALE, (y + 8) * SCALE, (x + 25) * SCALE, (y + 12) * SCALE, (x + 30) * SCALE, (y + 5) * SCALE],
                               fill=TEXT, width=2 * SCALE)
                    rect(d, (x + 44, y + 4, x + 44 + 60 + (r * 17) % 30, y + 12), 4, fill=mix(LINE, GREEN, pop * 0.5) if done else LINE)
            elif k == 1:  # calendar fills
                size = 11
                gx = cx - 5 * (size + 2)
                for c in range(10):
                    for r in range(7):
                        p = ease((t * 1.5 - (c + r * 0.3) / 12) / 0.1)
                        col = mix(BLUE, CYAN, heat[c][r]) if heat[c][r] > 0.25 else mix(PANEL, BLUE, 0.3)
                        fill = mix((23, 32, 62), col, p)
                        rect(d, (gx + c * (size + 2), 36 + r * (size + 2), gx + c * (size + 2) + size, 36 + r * (size + 2) + size), 2, fill=fill)
            elif k == 2:  # timer ring
                r = 44
                box = [(cx - r) * SCALE, (cy - r + 2) * SCALE, (cx + r) * SCALE, (cy + r + 2) * SCALE]
                d.arc(box, 0, 360, fill=(23, 32, 62), width=8 * SCALE)
                d.arc(box, -90, -90 + 360 * (1 - t), fill=ORANGE, width=8 * SCALE)
                m = int(25 * (1 - t))
                s = int((25 * (1 - t) - m) * 60)
                text(d, (cx, cy - 12), f"{m:02d}:{s:02d}", font(19), TEXT, "ma")
            else:  # XP bar, level pops
                fill = min(1, t / 0.7)
                level = 12 if fill < 1 else 13
                pop = ease((t - 0.7) / 0.08) * (1 - ease((t - 0.82) / 0.12))
                size = 30 + int(8 * pop)
                text(d, (cx, cy - 34 - 3 * pop), str(level), font(size), mix(TEXT, ORANGE, pop), "ma")
                rect(d, (x + 18, cy + 18, x + tile_w - 18, cy + 30), 6, fill=(23, 32, 62))
                bar_w = (tile_w - 36) * (fill if fill < 1 else (t - 0.7) / 0.3 * 0.2)
                if bar_w > 3:
                    rect(d, (x + 18, cy + 18, x + 18 + bar_w, cy + 30), 6, fill=PINK)
        frames.append(img)
    save("tools.gif", frames, 70)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    hero()
    persian_flip()
    tiles()
