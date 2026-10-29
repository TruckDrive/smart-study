"""Generates every image and sound that ships in addon/ (except bundled libraries).

All artwork is drawn here from simple shapes plus Lucide icon geometry
(ISC license, bundled in addon/web_roadmap/icons/). Sounds are synthesized.
Run from the repo root:  python -I tools/make_assets.py
Needs: Pillow (with WebP), rsvg-convert, ffmpeg.
"""
import array
import json
import math
import os
import random
import shutil
import subprocess
import sys
import tempfile
import wave

from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADDON = os.path.join(ROOT, "addon")
MEDIA = os.path.join(ADDON, "media")
ONB = os.path.join(ADDON, "onboarding")
IMAGES = os.path.join(ADDON, "images")
FONT = "Inter, 'Noto Sans', 'DejaVu Sans', sans-serif"
BRAND = "#0071d3"  # logo_utils.py recolours exactly this value to the active theme accent
THEMES = {  # light-mode accents from theme.py, in onboarding order
    "ocean": "#0071D3", "horizon": "#6183A9", "forest": "#619971",
    "dusty": "#5A9491", "deluge": "#7961A9", "orchid": "#E95ACC",
}
TMP = tempfile.mkdtemp()
random.seed(7)


# ── helpers ───────────────────────────────────────────────────────────────────

def _lucide():
    with open(os.path.join(ADDON, "web_roadmap", "icons", "catalog.js"), encoding="utf-8") as f:
        s = f.read()
    data = json.loads(s[s.index("{"):s.rindex("}") + 1])
    return {i["id"].removeprefix("lucide-"): i["nodes"] for i in data["icons"]}


LUCIDE = _lucide()

# Simple glyphs not in the bundled Lucide subset, drawn on the same 24px grid.
OWN = {
    "play": '<path d="M7 4.5v15l12.5-7.5z"/>',
    "pause": '<rect x="6" y="4.5" width="4" height="15" rx="1"/><rect x="14" y="4.5" width="4" height="15" rx="1"/>',
    "rotate-ccw": '<path d="M3 12a9 9 0 1 0 3-6.7"/><path d="M3 4v5h5"/>',
    "skip-forward": '<path d="M5 4.5v15L16 12z"/><path d="M19.5 5v14"/>',
    "panel-left-close": '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M9 3v18"/><path d="M16 15l-3-3 3-3"/>',
    "panel-left-open": '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M9 3v18"/><path d="M14 9l3 3-3 3"/>',
    "sparkle": '<path d="M12 3l1.9 5.6L19.5 10.5l-5.6 1.9L12 18l-1.9-5.6L4.5 10.5l5.6-1.9z"/>',
}


def glyph(name):
    if name in OWN:
        return OWN[name]
    out = []
    for tag, attrs in LUCIDE[name]:
        a = " ".join(f'{k}="{v}"' for k, v in attrs.items() if k != "key")
        out.append(f"<{tag} {a}/>")
    return "".join(out)


def gear():
    pts = []
    for i in range(16):
        ang = math.pi * 2 * i / 16
        r = 9.5 if i % 2 == 0 else 7.2
        for d in (-0.13, 0.13):
            pts.append(f"{12 + r * math.cos(ang + d):.2f},{12 + r * math.sin(ang + d):.2f}")
    return f'<polygon points="{" ".join(pts)}"/><circle cx="12" cy="12" r="3"/>'


def icon_svg(inner, stroke, width, view=24):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{view}" height="{view}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{stroke}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round">{inner}</svg>\n')


def place(name, x, y, size, color="#ffffff", width=2.0):
    """A glyph scaled into a box at (x, y) of *size* px."""
    k = size / 24
    return (f'<g transform="translate({x},{y}) scale({k})" fill="none" stroke="{color}" stroke-width="{width}" '
            f'stroke-linecap="round" stroke-linejoin="round">{glyph(name)}</g>')


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def render(svg, w, h):
    """SVG text → RGBA image."""
    src = os.path.join(TMP, "r.svg")
    dst = os.path.join(TMP, "r.png")
    write(src, svg)
    subprocess.run(["rsvg-convert", "-w", str(w), "-h", str(h), "-o", dst, src], check=True)
    return Image.open(dst).convert("RGBA")


def png(svg, path, w, h):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    render(svg, w, h).save(path, optimize=True)


def grad(id_, a, b, x2=0, y2=1):
    return (f'<linearGradient id="{id_}" x1="0" y1="0" x2="{x2}" y2="{y2}">'
            f'<stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>')


def mix(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


def clean():
    """Removes the previous artwork and sounds (bundled libraries stay)."""
    for d in (os.path.join(MEDIA, "Achievements"), os.path.join(MEDIA, "example_wallpapers")):
        shutil.rmtree(d, ignore_errors=True)
    for folder, exts in ((MEDIA, (".png", ".gif", ".svg", ".mp3", ".wav", ".webp")),
                         (ONB, (".png",)), (IMAGES, (".png", ".svg"))):
        for f in os.listdir(folder):
            if f.endswith(exts):
                os.remove(os.path.join(folder, f))


# ── logo ──────────────────────────────────────────────────────────────────────

def logo_inner(accent=BRAND, fg="#ffffff"):
    """The logo on an 800 px grid: a rounded tile with an open book and a spark."""
    return (f'<rect x="40" y="40" width="720" height="720" rx="190" fill="{accent}"/>'
            + place("book-open", 160, 190, 480, fg, 1.9)
            + place("sparkle", 500, 90, 200, fg, 1.6).replace('fill="none"', f'fill="{fg}"'))


def logo_svg(accent=BRAND):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 800">\n{logo_inner(accent)}\n</svg>\n'


def make_logos():
    write(os.path.join(MEDIA, "logo.svg"), logo_svg())
    write(os.path.join(MEDIA, "logo_1.svg"), logo_svg())
    for name, color in THEMES.items():
        if name != "ocean":
            write(os.path.join(MEDIA, f"logo_{name}.svg"), logo_svg(color.lower()))
    png(logo_svg(), os.path.join(MEDIA, "logo_about.png"), 512, 512)


# ── launcher and control icons ────────────────────────────────────────────────

def make_icons():
    pairs = {"ai_tool": "brain-circuit", "website": "globe", "notes": "notebook-pen", "mindmap": "network",
             "game": "trophy", "music": "music", "timer": "timer", "study_plan": "calendar-check"}
    for fname, g in pairs.items():
        write(os.path.join(MEDIA, f"{fname}.svg"), icon_svg(glyph(g), "#888888", 1.25))
        write(os.path.join(MEDIA, f"{fname}_white.svg"), icon_svg(glyph(g), "#ffffff", 1.5))
    for fname, g in {"start": "play", "pause": "pause", "reset": "rotate-ccw", "skip": "skip-forward"}.items():
        write(os.path.join(MEDIA, f"{fname}.svg"), icon_svg(glyph(g), "#888888", 1.75))
    write(os.path.join(MEDIA, "check.svg"),
          '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" '
          f'stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">{glyph("check")}</svg>\n')
    write(os.path.join(MEDIA, "settings.svg"), icon_svg(gear(), "currentColor", 1.6))
    write(os.path.join(MEDIA, "sidebar_icon_open.svg"), icon_svg(glyph("panel-left-close"), "#292d32", 1.6))
    write(os.path.join(MEDIA, "sidebar_icon_closed.svg"), icon_svg(glyph("panel-left-open"), "#292d32", 1.6))
    write(os.path.join(IMAGES, "deadline.svg"), icon_svg(glyph("flag"), "#808080", 1.25))


# ── gamification: ranks and achievements ──────────────────────────────────────

TIERS = [  # light, dark, glyph
    ("#F2B98A", "#A0592A", "sprout"), ("#EEF2F6", "#8E9BA8", "leaf"), ("#FFE58A", "#D08E12", "book-open"),
    ("#8FE8B4", "#1E8A57", "graduation-cap"), ("#8CC2FF", "#1F4FCC", "brain"),
    ("#D3B2FF", "#6A35C9", "rocket"), ("#FF9DAE", "#B3123A", "trophy"),
]
HEX = "60,6 106,32 106,88 60,114 14,88 14,32"


def star(cx, cy, r):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.45
        a = -math.pi / 2 + i * math.pi / 5
        pts.append(f"{cx + rr * math.cos(a):.2f},{cy + rr * math.sin(a):.2f}")
    return f'<polygon points="{" ".join(pts)}" fill="#ffffff" stroke="none"/>'


def rank_svg(rank):
    light, dark, g = TIERS[(rank - 1) // 3]
    level = (rank - 1) % 3 + 1
    stars = "".join(star(60 + (i - (level - 1) / 2) * 15, 92, 5.5) for i in range(level))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120">
<defs>{grad("g", light, dark)}</defs>
<polygon points="{HEX}" fill="url(#g)" stroke="{dark}" stroke-width="3" stroke-linejoin="round"/>
<polygon points="60,14 99,36 99,84 60,106 21,84 21,36" fill="none" stroke="#ffffff" stroke-opacity=".45" stroke-width="2" stroke-linejoin="round"/>
{place(g, 37, 26, 46, "#ffffff", 2.0)}
{stars}
</svg>
'''


def to_gif_frame(im):
    """RGBA → palette frame with a transparent background (index 255)."""
    alpha = im.getchannel("A").point(lambda a: 255 if a >= 110 else 0)
    p = im.convert("RGB").quantize(colors=255)
    p.putpalette(((p.getpalette() or []) + [0] * 768)[:768])
    p.paste(255, mask=ImageChops.invert(alpha))
    return p


def make_ranks():
    for rank in range(1, 22):
        svg = rank_svg(rank)
        png(svg, os.path.join(MEDIA, f"rang{rank}.png"), 138, 138)
        base = render(svg, 500, 500)
        frames = []
        for i in range(18):  # a light sweep across the badge, then it rests
            band = Image.new("L", base.size, 0)
            x = -260 + i * 50
            ImageDraw.Draw(band).polygon([(x, 500), (x + 90, 500), (x + 590, 0), (x + 500, 0)], fill=120)
            band = band.filter(ImageFilter.GaussianBlur(18))
            shine = ImageChops.multiply(band, base.getchannel("A"))
            f = base.copy()
            f.paste((255, 255, 255, 255), mask=shine)
            f.putalpha(base.getchannel("A"))
            frames.append(to_gif_frame(f))
        frames += [to_gif_frame(base)] * 2
        frames[0].save(os.path.join(MEDIA, f"rang{rank}.gif"), save_all=True, append_images=frames[1:],
                       duration=[60] * 18 + [600, 1000], loop=0, transparency=255, disposal=2, optimize=False)


MEDALS = {"bronze": ("#F2B98A", "#A0592A"), "silver": ("#F1F4F7", "#8E9BA8"), "gold": ("#FFE58A", "#D08E12"),
          "diamond": ("#C8F3FF", "#3C9FD8"), "earned": ("#9BE8B9", "#23955D"), "locked": ("#E3E5E8", "#A3A9B1")}
CATEGORY = {"challenges": "target", "comeback": "repeat", "days": "calendar-days", "reviews": "layers", "streak": "flame"}


def medal_svg(kind, g):
    light, dark = MEDALS[kind]
    inner = place("lock" if kind == "locked" else g, 36, 36, 48, "#ffffff", 2.2)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120">
<defs>{grad("m", light, dark)}</defs>
<circle cx="60" cy="60" r="54" fill="url(#m)" stroke="{dark}" stroke-width="3"/>
<circle cx="60" cy="60" r="44" fill="none" stroke="#ffffff" stroke-opacity=".5" stroke-width="2"/>
{inner}
</svg>
'''


def make_achievements():
    for cat, g in CATEGORY.items():
        kinds = ("earned", "locked") if cat == "comeback" else ("bronze", "silver", "gold", "diamond", "locked")
        for kind in kinds:
            write(os.path.join(MEDIA, "Achievements", cat, f"{kind}.svg"), medal_svg(kind, g))


# ── deck overview, mode, music covers ─────────────────────────────────────────

def disc_svg(color, g, size=120):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120">
<defs>{grad("d", mix(color, "#ffffff", .25), color)}</defs>
<circle cx="60" cy="60" r="56" fill="url(#d)"/>
{place(g, 30, 30, 60, "#ffffff", 2.0)}
</svg>
'''


def make_deck_icons():
    for name, color, g, size in (("easy", "#22A06B", "face-grinning", 297), ("medium", "#E8A317", "face-neutral", 297),
                                 ("hard", "#E5484D", "face-slightly-frowning", 297),
                                 ("hardcards", "#E5484D", "triangle-alert", 297),
                                 ("learned", "#22A06B", "circle-check", 297), ("retention", BRAND, "brain", 64)):
        png(disc_svg(color, g), os.path.join(MEDIA, f"{name}.png"), size, size)


def make_mode():
    chips = "".join(f'<rect x="{6 + i * 52}" y="6" width="46" height="40" rx="12" fill="#ffffff" fill-opacity="{.95 if i == 0 else .25}"/>'
                    f'{place(g, 17 + i * 52, 12, 24, BRAND if i == 0 else "#ffffff", 2.0)}'
                    for i, g in enumerate(("target", "zap", "list-checks")))
    png(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 162 52">
<defs>{grad("b", "#4FACFE", BRAND, 1, 0)}</defs>
<rect width="162" height="52" rx="16" fill="url(#b)"/>{chips}</svg>''', os.path.join(MEDIA, "mode.png"), 162, 52)


def cover_svg(a, b, g):
    circles = "".join(f'<circle cx="{random.randint(0, 533)}" cy="{random.randint(0, 416)}" r="{random.randint(40, 140)}" '
                      f'fill="#ffffff" fill-opacity="{random.uniform(.04, .12):.2f}"/>' for _ in range(7))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 533 416">
<defs>{grad("c", a, b, 1, 1)}</defs>
<rect width="533" height="416" fill="url(#c)"/>{circles}
{place(g, 186, 128, 160, "#ffffff", 1.6)}
</svg>
'''


def make_covers():
    for name, a, b, g in (("alpha", "#4FACFE", "#1F4FCC", "waves-horizontal"), ("beta", "#FFB55A", "#E5484D", "zap"),
                          ("library", "#C7A27C", "#6B4A2B", "library-big"), ("jazz", "#B48CFF", "#4B2A99", "music"),
                          ("rain", "#8FB3D9", "#34506E", "cloud-rain"), ("cozy", "#FFC27A", "#B4532A", "coffee"),
                          ("own", "#B8C0CC", "#5B6573", "headphones")):
        png(cover_svg(a, b, g), os.path.join(MEDIA, f"{name}.png"), 533, 416)


# ── banner, wallpapers ────────────────────────────────────────────────────────

def make_banner():
    chips = "".join(
        f'<g transform="translate({760 + i * 250},700)"><rect width="220" height="150" rx="28" fill="#ffffff" fill-opacity=".16"/>'
        f'{place(g, 74, 18, 72, "#ffffff", 1.8)}'
        f'<text x="110" y="128" font-family="{FONT}" font-size="26" font-weight="600" fill="#ffffff" text-anchor="middle">{t}</text></g>'
        for i, (g, t) in enumerate((("calendar-check", "Plan"), ("brain", "Learn"), ("notebook-pen", "Notes"), ("trophy", "Progress"))))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1800 1000">
<defs>{grad("bg", "#4FACFE", "#0B3E91", 1, 1)}</defs>
<rect width="1800" height="1000" fill="url(#bg)"/>
<circle cx="1650" cy="120" r="320" fill="#ffffff" fill-opacity=".07"/><circle cx="120" cy="980" r="260" fill="#ffffff" fill-opacity=".06"/>
<g transform="translate(140,250) scale(0.62)">{logo_inner("#ffffff", BRAND)}</g>
<text x="760" y="390" font-family="{FONT}" font-size="132" font-weight="800" fill="#ffffff">Smart Study</text>
<text x="764" y="480" font-family="{FONT}" font-size="48" fill="#ffffff" fill-opacity=".9">Your study plan and workspace, inside Anki.</text>
{chips}
</svg>
'''
    png(svg, os.path.join(MEDIA, "news-banner.png"), 1800, 1000)


def blobs(size, base, colors, n, blur):
    w, h = size
    im = Image.new("RGB", size, base)
    layer = Image.new("RGB", size, base)
    d = ImageDraw.Draw(layer)
    for i in range(n):
        r = random.randint(h // 4, h // 2)
        x, y = random.randint(0, w), random.randint(0, h)
        d.ellipse([x - r, y - r, x + r, y + r], fill=colors[i % len(colors)])
    return Image.blend(im, layer.filter(ImageFilter.GaussianBlur(blur)), .85)


def make_wallpapers():
    out = os.path.join(MEDIA, "example_wallpapers")
    os.makedirs(out, exist_ok=True)
    size = (1672, 941)
    blobs(size, (241, 245, 252), [(205, 225, 255), (230, 214, 255), (210, 244, 236)], 6, 160).save(
        os.path.join(out, "smartstudy_starter_light.webp"), quality=86)
    blobs(size, (14, 20, 36), [(28, 52, 110), (58, 34, 96), (16, 70, 84)], 6, 170).save(
        os.path.join(out, "smartstudy_starter_dark.webp"), quality=86)
    blobs(size, (40, 60, 140), [(79, 172, 254), (233, 90, 204), (255, 181, 90), (97, 153, 113)], 9, 140).save(
        os.path.join(out, "smartstudy_starter_abstract.webp"), quality=86)


# ── onboarding ────────────────────────────────────────────────────────────────

def panel_svg(w, h, main, chips, a="#4FACFE", b=BRAND):
    chip = "".join(
        f'<g transform="translate({x},{y})"><rect width="128" height="128" rx="32" fill="#ffffff" fill-opacity=".18"/>'
        f'{place(g, 32, 32, 64, "#ffffff", 1.8)}</g>'
        for (x, y), g in zip(((w * .12, h * .62), (w * .5, h * .7), (w * .26, h * .8)), chips))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">
<defs>{grad("p", a, b, .4, 1)}</defs>
<rect width="{w}" height="{h}" fill="url(#p)"/>
<circle cx="{w * .85}" cy="{h * .08}" r="{w * .35}" fill="#ffffff" fill-opacity=".07"/>
<circle cx="{w * .1}" cy="{h * .95}" r="{w * .3}" fill="#ffffff" fill-opacity=".06"/>
<circle cx="{w / 2}" cy="{h * .33}" r="{w * .28}" fill="#ffffff" fill-opacity=".14"/>
{main}
{chip}
</svg>
'''


def make_onboarding():
    logo = logo_inner()
    png(panel_svg(760, 1120, f'<g transform="translate(190,180) scale(0.475)">{logo}</g>',
                  ("calendar-check", "brain", "timer")), os.path.join(ONB, "img_welcome.png"), 760, 1120)
    for i, (g, chips) in enumerate((("languages", ("globe", "message-circle", "book-open")),
                                    ("graduation-cap", ("stethoscope", "scale", "laptop")),
                                    ("compass", ("users", "megaphone", "star"))), 1):
        main = place(g, 280 - 110, 1120 * .33 - 110, 220, "#ffffff", 1.5)
        png(panel_svg(560, 1120, main, chips), os.path.join(ONB, f"img_sidebar_{i}.png"), 560, 1120)
    for i, (name, color) in enumerate(THEMES.items(), 1):
        lines = "".join(f'<rect x="150" y="{120 + k * 46}" width="{170 - k * 30}" height="18" rx="9" fill="#ffffff" fill-opacity=".85"/>'
                        for k in range(4))
        png(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">
<defs>{grad("t", mix(color, "#ffffff", .35), color, 1, 1)}</defs>
<rect width="400" height="400" rx="56" fill="url(#t)"/>
<rect x="64" y="64" width="64" height="272" rx="20" fill="#ffffff" fill-opacity=".9"/>
{"".join(f'<circle cx="96" cy="{108 + k * 56}" r="14" fill="{color}" fill-opacity="{1 if k == 0 else .45}"/>' for k in range(4))}
{lines}
<rect x="150" y="300" width="120" height="36" rx="18" fill="#ffffff"/>
</svg>''', os.path.join(ONB, f"img_theme_{i}.png"), 400, 400)
    # Where the settings are: the logo at the top of the launcher bar, highlighted.
    launcher_icons = "".join(place(g, 46, 176 + k * 58, 34, "#888888", 1.6)
                             for k, g in enumerate(("brain-circuit", "globe", "notebook-pen", "network")))
    png(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1160 440">
<rect width="1160" height="440" rx="36" fill="#F3F5F8"/>
<rect x="24" y="24" width="1112" height="392" rx="22" fill="#ffffff" stroke="#DDE2E8" stroke-width="2"/>
<rect x="24" y="24" width="1112" height="56" rx="22" fill="#EEF1F5"/>
{"".join(f'<circle cx="{60 + k * 30}" cy="52" r="9" fill="{c}"/>' for k, c in enumerate(("#FF5F57", "#FEBC2E", "#28C840")))}
<rect x="24" y="80" width="100" height="336" fill="#F7F8FA"/>
<circle cx="63" cy="118" r="36" fill="none" stroke="{BRAND}" stroke-width="5" stroke-dasharray="10 8"/>
<g transform="translate(40,95) scale(0.058)">{logo}</g>
{launcher_icons}
{"".join(f'<rect x="170" y="{120 + k * 60}" width="{760 - k * 120}" height="28" rx="14" fill="#E9EDF2"/>' for k in range(5))}
<path d="M150 150 C 260 150, 330 100, 420 110" fill="none" stroke="{BRAND}" stroke-width="5" stroke-linecap="round"/>
<path d="M150 150 l22 -16 M150 150 l24 10" fill="none" stroke="{BRAND}" stroke-width="5" stroke-linecap="round"/>
<g transform="translate(440,74) scale(3)" fill="none" stroke="{BRAND}" stroke-width="1.6" stroke-linejoin="round">{gear()}</g>
</svg>''', os.path.join(ONB, "img_settings_tip.png"), 1160, 440)
    stars = "".join(f'<g transform="translate({140 + k * 150},40)"><rect width="120" height="120" rx="30" fill="#FFF4D6"/>'
                    f'{star(60, 62, 34).replace("#ffffff", "#F5B301")}</g>' for k in range(5))
    png(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 200">{stars}</svg>',
        os.path.join(ONB, "img_support.png"), 1000, 200)


# ── sounds ────────────────────────────────────────────────────────────────────

def write_wav(path, samples, rate=44100):
    peak = max(1e-9, max(abs(s) for s in samples))
    data = array.array("h", (int(s / peak * 0.85 * 32767) for s in samples))
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(data.tobytes())


def bell(seconds, partials, rate=44100):
    n = int(seconds * rate)
    out = []
    for i in range(n):
        t = i / rate
        out.append(sum(a * math.exp(-t * d) * math.sin(2 * math.pi * f * t) for f, a, d in partials)
                   * min(1, t * 400))
    return out


def make_alerts():
    base = 660
    write_wav(os.path.join(MEDIA, "bells.wav"),
              bell(2.4, [(base, 1, 1.6), (base * 2.76, .5, 2.4), (base * 5.4, .25, 3.5), (base * 8.93, .12, 5)]))
    a = bell(1.6, [(1318.5, 1, 2.2), (2637, .2, 3)])
    b = bell(2.2, [(1046.5, 1, 1.8), (2093, .2, 2.6)])
    gap = int(0.22 * 44100)
    write_wav(os.path.join(MEDIA, "chime.wav"),
              [(a[i] if i < len(a) else 0) + (b[i - gap] if gap <= i < gap + len(b) else 0)
               for i in range(gap + len(b))])


def ffmpeg(args, out):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *args, "-ac", "2", "-ar", "44100",
                    "-c:a", "libmp3lame", "-b:a", "96k", out], check=True)


def jazz_loop(path, rate=22050):
    """Soft ii–V–I–VI chord loop with walking bass and brushes, about 55 s."""
    beat = 60 / 72
    prog = [(62, [62, 65, 69, 72]), (55, [59, 62, 65, 67]), (60, [60, 64, 67, 71]), (57, [61, 64, 67, 69])] * 4
    total = int(len(prog) * 4 * beat * rate) + rate
    buf = [0.0] * total
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)

    def note(start, freq, dur, amp, decay, harm=.25):
        s = int(start * rate)
        for i in range(int(dur * rate)):
            if s + i >= total:
                break
            t = i / rate
            env = min(1, t * 120) * math.exp(-t * decay)
            buf[s + i] += amp * env * (math.sin(2 * math.pi * freq * t) + harm * math.sin(4 * math.pi * freq * t))

    for bar, (root, chord) in enumerate(prog):
        t0 = bar * 4 * beat
        for hit in (0, 1.66):  # swung comping
            for m in chord:
                note(t0 + hit * beat, hz(m), 2.2, .11, 1.6)
        walk = [root, root + 4, root + 7, root + 9 if bar % 2 else root + 5]
        for k, m in enumerate(walk):
            note(t0 + k * beat, hz(m - 24), beat * .95, .32, 3.2, .4)
        for k in (1, 3):  # brushes on 2 and 4
            s = int((t0 + k * beat) * rate)
            for i in range(int(.18 * rate)):
                if s + i < total:
                    buf[s + i] += random.uniform(-1, 1) * .05 * math.exp(-i / rate * 22)
    wav = os.path.join(TMP, "jazz.wav")
    write_wav(wav, buf, rate)
    ffmpeg(["-i", wav, "-af", "lowpass=f=6000"], path)


def make_ambience():
    d = "90"
    ffmpeg(["-f", "lavfi", "-i", f"aevalsrc=0.25*sin(2*PI*200*t)|0.25*sin(2*PI*210*t):s=44100:d={d}",
            "-f", "lavfi", "-i", f"anoisesrc=c=pink:a=0.04:d={d}", "-filter_complex", "amix=inputs=2:normalize=0"],
           os.path.join(MEDIA, "alpha_waves.mp3"))
    ffmpeg(["-f", "lavfi", "-i", f"aevalsrc=0.25*sin(2*PI*220*t)|0.25*sin(2*PI*238*t):s=44100:d={d}",
            "-f", "lavfi", "-i", f"anoisesrc=c=pink:a=0.04:d={d}", "-filter_complex", "amix=inputs=2:normalize=0"],
           os.path.join(MEDIA, "beta_waves.mp3"))
    ffmpeg(["-f", "lavfi", "-i", f"anoisesrc=c=pink:a=0.5:d={d}", "-f", "lavfi", "-i", f"anoisesrc=c=brown:a=0.35:d={d}",
            "-filter_complex", "[0]highpass=f=400,lowpass=f=7000[a];[1]lowpass=f=900[b];[a][b]amix=inputs=2:normalize=0,volume=0.8"],
           os.path.join(MEDIA, "rain.mp3"))
    ffmpeg(["-f", "lavfi", "-i", f"anoisesrc=c=brown:a=0.25:d={d}",
            "-af", "lowpass=f=450,highpass=f=40,volume=0.7"], os.path.join(MEDIA, "library_sounds.mp3"))
    ffmpeg(["-f", "lavfi", "-i", f"anoisesrc=c=brown:a=0.4:d={d}",
            "-f", "lavfi", "-i", f"aevalsrc=if(lt(random(0)\\,0.0006)\\,(random(1)-0.5)*1.6\\,0):s=44100:d={d}",
            "-filter_complex", "[0]lowpass=f=1100[a];[1]highpass=f=1200,lowpass=f=6000[b];[a][b]amix=inputs=2:normalize=0"],
           os.path.join(MEDIA, "cozy.mp3"))
    jazz_loop(os.path.join(MEDIA, "jazz.mp3"))


if __name__ == "__main__":
    clean()
    make_logos()
    make_icons()
    make_ranks()
    make_achievements()
    make_deck_icons()
    make_mode()
    make_covers()
    make_banner()
    make_wallpapers()
    make_onboarding()
    make_alerts()
    make_ambience()
    shutil.rmtree(TMP, ignore_errors=True)
    print("assets done", file=sys.stderr)
