"""Smoother feel for Anki and the Smart Study browser.

* Kinetic scrolling: on Linux, Qt WebEngine stops dead when the fingers leave
  the touchpad. After a quick swipe the page now keeps gliding and slows down,
  like in Firefox or on a phone – in the browser and in Anki's own pages.
* Animated browser width when switching between sidebar and split view.
* Anki's deck list and deck overview fade in instead of popping up.
* Compact deck list: when a sidebar leaves Anki's main area narrow (e.g. the
  split view), the dashboard switches to its compact form and the big widgets
  (statistics, heatmap, deadline bar) step aside so the deck list fits.
"""
from __future__ import annotations

import math
import time
from collections import deque
from typing import Optional

from aqt import gui_hooks, mw
from aqt.qt import (QApplication, QEvent, QEasingCurve, QObject, QPoint, QPointF, Qt, QTimer,
                    QVariantAnimation, QWheelEvent)

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
except Exception:  # pragma: no cover
    QWebEngineView = None  # type: ignore

NARROW_WIDTH = 900  # Anki's main area below this → compact deck list


def _kinetic_on() -> bool:
    try:
        from .browser_features import load_settings
        return bool(load_settings().get("kinetic_scroll", True))
    except Exception:
        return True


# ── Kinetic scrolling ─────────────────────────────────────────────────────

class _Kinetic(QObject):
    TAU_MS = 325.0      # how quickly the glide slows down (like iOS / Firefox)
    MIN_SPEED = 0.25    # px/ms at release needed to start gliding
    STOP_SPEED = 0.02   # px/ms: glide ends below this
    MAX_SPEED = 8.0

    def __init__(self):
        super().__init__()
        self.samples = deque(maxlen=12)  # (time ms, dx, dy)
        self.timer = QTimer(self)
        self.timer.setInterval(8)
        self.timer.timeout.connect(self._tick)
        self.target = None
        self.sending = False
        self.v = QPointF()
        self.rest = QPointF()
        self.last = 0.0
        self.pos = QPointF()
        self.gpos = QPointF()
        self.inverted = False
        self.mods = Qt.KeyboardModifier.NoModifier

    @staticmethod
    def _in_web_view(obj) -> bool:
        if QWebEngineView is None or isinstance(obj, QWebEngineView):
            return False
        parent = obj.parent() if hasattr(obj, "parent") else None
        while parent is not None:
            if isinstance(parent, QWebEngineView):
                return True
            parent = parent.parent()
        return False

    def eventFilter(self, obj, event):
        kind = event.type()
        if kind == QEvent.Type.MouseButtonPress or kind == QEvent.Type.KeyPress:
            if self.timer.isActive():
                self.stop()
            return False
        if kind != QEvent.Type.Wheel or self.sending:
            return False
        if not self._in_web_view(obj):
            return False
        phase = event.phase()
        if phase == Qt.ScrollPhase.ScrollBegin:
            self.stop()
            self.samples.clear()
            return False
        if phase == Qt.ScrollPhase.ScrollUpdate:
            delta = event.pixelDelta()
            if delta.isNull():
                return False
            self.samples.append((time.monotonic() * 1000.0, delta.x(), delta.y()))
            return False
        if phase == Qt.ScrollPhase.ScrollEnd:
            if not _kinetic_on():
                return False
            v = self._release_speed()
            if v is None:
                return False
            self.target, self.v, self.rest = obj, v, QPointF()
            self.pos, self.gpos = event.position(), event.globalPosition()
            self.inverted, self.mods = event.inverted(), event.modifiers()
            self.last = time.monotonic() * 1000.0
            self.timer.start()
            return True  # the page gets its ScrollEnd when the glide is over
        if phase == Qt.ScrollPhase.NoScrollPhase and self.timer.isActive():
            self.stop()  # a mouse wheel takes over
        return False

    def _release_speed(self) -> Optional[QPointF]:
        now = time.monotonic() * 1000.0
        recent = [s for s in self.samples if now - s[0] <= 100]
        self.samples.clear()
        if len(recent) < 3 or now - recent[-1][0] > 50:
            return None  # fingers rested before lifting: no glide
        span = max(recent[-1][0] - recent[0][0], 8.0) + 8.0
        vx = sum(s[1] for s in recent) / span
        vy = sum(s[2] for s in recent) / span
        speed = math.hypot(vx, vy)
        if speed < self.MIN_SPEED:
            return None
        if speed > self.MAX_SPEED:
            vx, vy = vx * self.MAX_SPEED / speed, vy * self.MAX_SPEED / speed
        return QPointF(vx, vy)

    def _send(self, dx: int, dy: int, phase) -> None:
        target = self.target
        try:
            from PyQt6 import sip
            if target is None or sip.isdeleted(target):
                return
        except Exception:
            pass
        event = QWheelEvent(self.pos, self.gpos, QPoint(dx, dy), QPoint(dx, dy),
                            Qt.MouseButton.NoButton, self.mods, phase, self.inverted)
        self.sending = True
        try:
            QApplication.sendEvent(target, event)
        finally:
            self.sending = False

    def _tick(self) -> None:
        now = time.monotonic() * 1000.0
        dt = max(1.0, now - self.last)
        self.last = now
        decay = math.exp(-dt / self.TAU_MS)
        # distance travelled in dt with exponential decay
        factor = self.TAU_MS * (1.0 - decay)
        move = QPointF(self.v.x() * factor, self.v.y() * factor) + self.rest
        self.v = QPointF(self.v.x() * decay, self.v.y() * decay)
        dx, dy = int(move.x()), int(move.y())
        self.rest = QPointF(move.x() - dx, move.y() - dy)
        if dx or dy:
            self._send(dx, dy, Qt.ScrollPhase.ScrollUpdate)
        if math.hypot(self.v.x(), self.v.y()) < self.STOP_SPEED:
            self.stop()

    def stop(self) -> None:
        if self.timer.isActive():
            self.timer.stop()
            self._send(0, 0, Qt.ScrollPhase.ScrollEnd)
        self.target = None


_kinetic: Optional[_Kinetic] = None


# ── Animated dock width ───────────────────────────────────────────────────

_width_anim: Optional[QVariantAnimation] = None


def animate_dock_width(dock, width: int, done=None) -> None:
    """Glide a docked sidebar to a new width."""
    global _width_anim
    if _width_anim is not None:
        _width_anim.stop()
    start = dock.width()
    if abs(start - width) < 4:
        mw.resizeDocks([dock], [width], Qt.Orientation.Horizontal)
        if done:
            done()
        return
    anim = QVariantAnimation(mw)
    anim.setStartValue(float(start))
    anim.setEndValue(float(width))
    anim.setDuration(240)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    anim.valueChanged.connect(lambda value: mw.resizeDocks([dock], [int(value)], Qt.Orientation.Horizontal))
    if done:
        anim.finished.connect(done)
    _width_anim = anim
    anim.start()


# ── Anki pages: fade in, smooth wheel, compact deck list ──────────────────

_FADE = ("<style id='ss-fade'>@keyframes ssFadeIn{from{opacity:0;transform:translateY(6px)}"
         "to{opacity:1;transform:none}}body{animation:ssFadeIn .18s ease-out both}"
         "@media (prefers-reduced-motion: reduce){body{animation:none}}</style>")

COMPACT_CSS = """<style id="ss-compact">
/* Narrow main area (browser beside Anki): keep the deck list in view. */
.sp-min-deadline-box, .sp-min-statistics, .rh-container, .sp-min-plan-fact-row { display: none !important; }
.sp-min-overview { padding: 6px 8px !important; margin-bottom: 6px !important; }
center { padding: 0 6px; box-sizing: border-box; }
center > table { width: 100% !important; max-width: 100% !important; }
html { overflow-x: hidden; }
</style>"""

_rendered_compact: Optional[bool] = None


def deck_area_narrow() -> bool:
    web = getattr(mw, "web", None)
    return bool(web is not None and web.width() < NARROW_WIDTH)


def note_rendered(compact: bool) -> None:
    global _rendered_compact
    _rendered_compact = compact


def _on_content(web_content, context) -> None:
    try:
        from aqt.deckbrowser import DeckBrowser
        from aqt.overview import Overview
    except Exception:
        return
    if isinstance(context, (DeckBrowser, Overview)):
        web_content.head += _FADE


class _MainAreaWatcher(QObject):
    """Re-render the deck list when the main area becomes narrow or wide."""

    def __init__(self):
        super().__init__()
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(280)
        self.timer.timeout.connect(self._check)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.Resize:
            self.timer.start()
        return False

    def _check(self) -> None:
        if _rendered_compact is None or getattr(mw, "state", "") != "deckBrowser":
            return
        if deck_area_narrow() != _rendered_compact:
            try:
                mw.deckBrowser.refresh()
            except Exception as e:
                print(f"Smart Study: deck list not refreshed: {e}")


_watcher: Optional[_MainAreaWatcher] = None


def _setup_main_web() -> None:
    global _watcher
    web = getattr(mw, "web", None)
    if web is None:
        return
    try:
        from PyQt6.QtWebEngineCore import QWebEngineSettings
        web.settings().setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, True)
    except Exception:
        pass
    if _watcher is None:
        _watcher = _MainAreaWatcher()
        web.installEventFilter(_watcher)


def setup() -> None:
    global _kinetic
    if _kinetic is None and QApplication.instance() is not None:
        _kinetic = _Kinetic()
        QApplication.instance().installEventFilter(_kinetic)
    gui_hooks.webview_will_set_content.append(_on_content)
    gui_hooks.main_window_did_init.append(_setup_main_web)
    if getattr(mw, "web", None) is not None:
        _setup_main_web()
