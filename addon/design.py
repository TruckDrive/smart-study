# -*- coding: utf-8 -*-
"""Smart Study's own look: one set of colour tokens for Qt and for web pages.

Every new surface (the side panel, the Today page, the standard theme) reads
its colours from here, so a change in one place reaches all of them.
"""
from typing import Dict

STANDARD_THEME = "standard.css"

DARK: Dict[str, str] = {
    "page": "#26282B", "card": "#1D1F22", "line": "#3A3D42", "raised": "#34373C",
    "hover": "#2B2E32", "accent": "#56BAC6", "on_accent": "#06181B",
    "ink": "#F0F0F0", "muted": "#B4B4B4", "zero": "#8A8A8A", "barmute": "#5A5D62",
    "new": "#6BA8FF", "learn": "#FF7B6B", "due": "#4CC96A",
}

LIGHT: Dict[str, str] = {
    "page": "#F1F1EF", "card": "#FFFFFF", "line": "#D9D9D5", "raised": "#E8E8E5",
    "hover": "#F3F3F1", "accent": "#0B6570", "on_accent": "#FFFFFF",
    "ink": "#1C1D1F", "muted": "#55585C", "zero": "#74777C", "barmute": "#B4B7BB",
    "new": "#1D5FD0", "learn": "#B8342A", "due": "#1C7437",
}

def on_accent(color: str) -> str:
    """Dark or white text, whichever reads better on the accent colour."""
    try:
        h = color.lstrip("#")
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        def lin(v):
            return v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4
        r, g, b = (lin(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4))
        return "#14100E" if .2126 * r + .7152 * g + .0722 * b > .19 else "#FFFFFF"
    except Exception:
        return "#FFFFFF"


def tokens(night: bool) -> Dict[str, str]:
    """The colour tokens for dark or light, with the accent colour the user chose."""
    t = dict(DARK if night else LIGHT)
    try:
        from . import theme
        if theme.get_active_theme() != "petrol":
            p = theme.palette(night)
            t["accent"] = p["blue_accent"] if night else p["blue"]
            t["on_accent"] = on_accent(t["accent"])
    except Exception:
        pass
    return t


def css_vars(night: bool) -> str:
    """The tokens as CSS custom properties (--ss-page, --ss-card, ...)."""
    return "".join(f"--ss-{k.replace('_', '-')}:{v};" for k, v in tokens(night).items())
