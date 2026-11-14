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

# The older colour themes keep their accent in the new panel: (dark, light).
THEME_ACCENTS = {
    "orange.css": ("#DD7A5A", "#B4522F"),
    "blue.css": ("#6BA8FF", "#1D5FD0"),
    "green.css": ("#5FC98A", "#1C7437"),
    "pink.css": ("#F08BB4", "#B03468"),
    "purple.css": ("#B59CF5", "#6441C4"),
    "red.css": ("#F27D72", "#B8342A"),
    "turquoise.css": ("#56BAC6", "#0B6570"),
    "yellow.css": ("#E2B94F", "#7D5C00"),
    "medical_theme.css": ("#35B6D8", "#0A7391"),
}

_active_theme = STANDARD_THEME


def set_theme(css_file: str) -> None:
    global _active_theme
    _active_theme = css_file or STANDARD_THEME


def tokens(night: bool) -> Dict[str, str]:
    """The colour tokens for dark or light, with the active theme's accent."""
    t = dict(DARK if night else LIGHT)
    accent = THEME_ACCENTS.get(_active_theme)
    if accent:
        t["accent"] = accent[0 if night else 1]
        t["on_accent"] = "#14100E" if night else "#FFFFFF"
    return t


def css_vars(night: bool) -> str:
    """The tokens as CSS custom properties (--ss-page, --ss-card, ...)."""
    return "".join(f"--ss-{k.replace('_', '-')}:{v};" for k, v in tokens(night).items())
