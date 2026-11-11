# -*- coding: utf-8 -*-
"""Look of the Smart Study browser's bars: icons, colours, style sheets, load bar.

Kept apart from website_sidebar.py, which builds the widgets and wires them.
Everything here is a pure function of the palette, so a theme change only has
to call the same functions again.
"""

from __future__ import annotations

from typing import Optional

from aqt.qt import QByteArray, QColor, QEvent, QIcon, QPainter, QPixmap, QSize, Qt, QTabBar, QTimer, QWidget

try:
    from PyQt6.QtSvg import QSvgRenderer
except Exception:  # QtSvg missing: buttons fall back to their text glyphs
    QSvgRenderer = None  # type: ignore

from .constants import is_night

ACCENT = "#4a90e2"

# Line icons on a 24 px grid, drawn with round 2 px strokes.
_PATHS = {
    "back": '<path d="M15 5l-7 7 7 7"/>',
    "forward": '<path d="M9 5l7 7-7 7"/>',
    "reload": '<path d="M20 11a8 8 0 1 0-2.3 6.3"/><path d="M20 4v7h-7"/>',
    "stop": '<path d="M6 6l12 12M18 6L6 18"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "home": '<path d="M4 11l8-7 8 7"/><path d="M6 10v9h12v-9"/>',
    "options": '<path d="M4 7h10M18 7h2M4 17h2M10 17h10"/><circle cx="16" cy="7" r="2"/><circle cx="8" cy="17" r="2"/>',
    "external": '<path d="M14 5h5v5"/><path d="M19 5l-8 8"/><path d="M18 14v4a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h4"/>',
    "layout": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M14 4v16"/>',
    "layout-close": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18M9 14.5h6"/>',
    "groups": '<rect x="4" y="4" width="7" height="7" rx="1.5"/><rect x="13" y="4" width="7" height="7" rx="1.5"/><rect x="4" y="13" width="7" height="7" rx="1.5"/><rect x="13" y="13" width="7" height="7" rx="1.5"/>',
    "close": '<path d="M7 7l10 10M17 7L7 17"/>',
    "globe": '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c3 3 3 14 0 17M12 3.5c-3 3-3 14 0 17"/>',
    "file": '<path d="M7 3.5h7l4 4V20a.5.5 0 0 1-.5.5h-10A.5.5 0 0 1 7 20z"/><path d="M14 3.5v4h4"/>',
}
GLYPHS = {"back": "←", "forward": "→", "reload": "↻", "stop": "✕", "plus": "+", "home": "⌂", "options": "⚙",
          "external": "↗", "layout": "⧉", "layout-close": "⧉", "groups": "▤", "close": "×", "globe": "", "file": ""}


def palette() -> dict:
    """Colours of the bars for Anki's light and dark mode."""
    if is_night():
        return {"bar": "#1f1f1f", "line": "rgba(255,255,255,0.09)", "text": "#ececec", "soft": "#b4b4b4",
                "hover": "rgba(255,255,255,0.09)", "pressed": "rgba(255,255,255,0.16)", "muted": "#6f6f6f",
                "select_bg": "#343434", "field": "#2b2b2b", "accent": ACCENT}
    return {"bar": "#f3f3f1", "line": "rgba(0,0,0,0.09)", "text": "#2f2e2b", "soft": "#5f5e5a",
            "hover": "rgba(0,0,0,0.06)", "pressed": "rgba(0,0,0,0.11)", "muted": "#b0aea8",
            "select_bg": "#ffffff", "field": "#ffffff", "accent": ACCENT}


def _pixmap(name: str, color: str, size: int) -> Optional[QPixmap]:
    if QSvgRenderer is None or name not in _PATHS:
        return None
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
           f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{_PATHS[name]}</svg>')
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    if not renderer.isValid():
        return None
    scale = 2  # sharp on high-DPI screens
    pm = QPixmap(QSize(size * scale, size * scale))
    pm.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pm)
    renderer.render(painter)
    painter.end()
    pm.setDevicePixelRatio(float(scale))
    return pm


def icon(name: str, size: int = 16, color: Optional[str] = None) -> Optional[QIcon]:
    """A line icon in the bar's text colour, greyed out while its button is disabled."""
    c = palette()
    normal = _pixmap(name, color or c["soft"], size)
    if normal is None:
        return None
    out = QIcon()
    out.addPixmap(normal, QIcon.Mode.Normal)
    active = _pixmap(name, color or c["text"], size)
    if active is not None:
        out.addPixmap(active, QIcon.Mode.Active)
    disabled = _pixmap(name, c["muted"], size)
    if disabled is not None:
        out.addPixmap(disabled, QIcon.Mode.Disabled)
    return out


def set_icon(button, name: str, size: int = 16) -> None:
    """Puts an icon on a button and remembers which, so a theme change can redraw it."""
    if button is None:
        return
    button._ss_icon_name, button._ss_icon_size = name, size
    ic = icon(name, size)
    if ic is None:
        button.setText(GLYPHS.get(name, ""))
        return
    button.setText("")
    button.setIcon(ic)
    button.setIconSize(QSize(size, size))


def refresh_icon(button) -> None:
    name = getattr(button, "_ss_icon_name", None)
    if name:
        set_icon(button, name, getattr(button, "_ss_icon_size", 16))


# ── Style sheets ──────────────────────────────────────────────────────────

def icon_button() -> str:
    c = palette()
    return f"""
QPushButton {{ background: transparent; color: {c['soft']}; border: none; border-radius: 7px;
    padding: 0; min-width: 28px; max-width: 28px; min-height: 28px; max-height: 28px; font-size: 15px; }}
QPushButton:hover {{ background: {c['hover']}; color: {c['text']}; }}
QPushButton:pressed {{ background: {c['pressed']}; }}
QPushButton:disabled {{ color: {c['muted']}; }}
QPushButton::menu-indicator {{ image: none; width: 0; height: 0; }}
"""


def chip() -> str:
    """A saved site: a small rounded button in the favourites row."""
    c = palette()
    return f"""
QPushButton {{ background: transparent; color: {c['soft']}; border: none; border-radius: 6px;
    padding: 3px 9px; font-size: 12px; }}
QPushButton:hover {{ background: {c['hover']}; color: {c['text']}; }}
QPushButton:pressed {{ background: {c['pressed']}; }}
QPushButton:disabled {{ color: {c['muted']}; }}
"""


def small_icon_button() -> str:
    c = palette()
    return f"""
QPushButton {{ background: transparent; color: {c['soft']}; border: none; border-radius: 6px;
    padding: 0; min-width: 22px; max-width: 22px; min-height: 22px; max-height: 22px; font-size: 13px; }}
QPushButton:hover {{ background: {c['hover']}; color: {c['text']}; }}
QPushButton:pressed {{ background: {c['pressed']}; }}
"""


def address() -> str:
    c = palette()
    return f"""
QLineEdit#smartstudyAddressBar {{ background: {c['field']}; color: {c['text']}; border: 1px solid {c['line']};
    border-radius: 14px; padding: 0 12px; min-height: 26px; max-height: 26px; font-size: 12.5px;
    selection-background-color: {c['accent']}; selection-color: #ffffff; }}
QLineEdit#smartstudyAddressBar:hover {{ border: 1px solid {c['muted']}; }}
QLineEdit#smartstudyAddressBar:focus {{ border: 1px solid {c['accent']}; }}
"""


def toolbar() -> str:
    c = palette()
    return f"#smartstudyWebToolbar {{ background-color: {c['bar']}; border-bottom: 1px solid {c['line']}; }}"


def tab_row() -> str:
    c = palette()
    return f"""
#smartstudyWebTabs {{ background-color: {c['bar']}; }}
#smartstudyWebTabs QTabBar {{ background: transparent; qproperty-drawBase: 0; }}
#smartstudyWebTabs QTabBar::tab {{ background: transparent; color: {c['soft']}; border: none; border-radius: 8px;
    padding: 5px 8px; margin: 0 1px; min-width: 22px; max-width: 180px; font-size: 12px; }}
#smartstudyWebTabs QTabBar::tab:selected {{ background: {c['select_bg']}; color: {c['text']}; }}
#smartstudyWebTabs QTabBar::tab:hover:!selected {{ background: {c['hover']}; color: {c['text']}; }}
#smartstudyWebTabs QPushButton#smartstudyCloseTab {{ background: transparent; color: {c['muted']};
    border: none; border-radius: 8px; padding: 0; font-size: 13px; }}
#smartstudyWebTabs QPushButton#smartstudyCloseTab:hover {{ background: {c['pressed']}; color: {c['text']}; }}
"""


class LoadBar(QWidget):
    """A 2 px line under the bars that fills while the page loads and then fades.
    It repaints only when the progress changes – there is no running animation."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(2)
        self._value = 0
        self._hide = QTimer(self)
        self._hide.setSingleShot(True)
        self._hide.setInterval(260)
        self._hide.timeout.connect(self._clear)

    def set_progress(self, percent: int, loading: bool) -> None:
        if loading and percent < 100:
            self._hide.stop()
            value = max(8, int(percent))  # something shows at once
        else:
            value = 100 if self._value else 0
            if self._value:
                self._hide.start()
        if value != self._value:
            self._value = value
            self.update()

    def _clear(self) -> None:
        self._value = 0
        self.update()

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(palette()["bar"]))
        if self._value:
            painter.fillRect(0, 0, int(self.width() * self._value / 100), self.height(), QColor(ACCENT))
        painter.end()


class Tabs(QTabBar):
    """Tabs share the width of their row: few tabs are wide enough for their title,
    many get narrower together, down to icon size. The row never grows because of
    its tabs (a plain QTabBar without scroll arrows would push the sidebar wider).
    Only when even icon-sized tabs do not fit, the scroll arrows come back."""

    MAX_WIDTH = 180
    MIN_WIDTH = 30
    RESERVED = 84  # the + and tab-group buttons and the row's margins
    ROOMY = 120    # from this width on, every tab shows its own ×
    on_refit = None  # called after the tabs were fitted again

    def roomy(self) -> bool:
        return self._tab_width() >= self.ROOMY

    def close_fits(self) -> bool:
        """Is a tab wide enough for its icon and a × side by side?"""
        return self._tab_width() >= 56

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setUsesScrollButtons(False)

    def _room(self) -> int:
        row = self.parentWidget()
        return max(self.MIN_WIDTH, (row.width() if row is not None else 400) - self.RESERVED)

    def _tab_width(self) -> int:
        return max(self.MIN_WIDTH, min(self.MAX_WIDTH, self._room() // max(1, self.count())))

    def tabSizeHint(self, index):
        return QSize(self._tab_width(), super().tabSizeHint(index).height())

    def minimumTabSizeHint(self, index):
        return QSize(self.MIN_WIDTH, super().minimumTabSizeHint(index).height())

    def minimumSizeHint(self):
        return QSize(self.MIN_WIDTH, super().sizeHint().height())

    def sizeHint(self):
        return QSize(min(self._room(), self._tab_width() * max(1, self.count())), super().sizeHint().height())

    def refit(self) -> None:
        """Call when the number of tabs or the width of the row changed."""
        crowded = self.count() * self.MIN_WIDTH > self._room()
        if crowded != self.usesScrollButtons():
            self.setUsesScrollButtons(crowded)
        self.updateGeometry()
        self.update()
        if self.on_refit is not None:
            try:
                self.on_refit()
            except Exception as e:
                print(f"Smart Study browser: tabs: {e}")

    def tabInserted(self, index):
        super().tabInserted(index)
        self.refit()

    def tabRemoved(self, index):
        super().tabRemoved(index)
        self.refit()

    def eventFilter(self, obj, event):  # installed on the row
        if event.type() == QEvent.Type.Resize:
            QTimer.singleShot(0, self.refit)
        return False
