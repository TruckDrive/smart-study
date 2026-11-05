"""Smoother feel for Anki and the Smart Study browser.

* Kinetic scrolling: on Linux, Qt WebEngine stops dead when the fingers leave
  the touchpad. After a quick swipe the page now keeps gliding and slows down,
  like in Firefox or on a phone – in the browser and in Anki's own pages.
* Sidebars slide in and out (a picture of them moves, the page is laid out once).
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
from aqt.qt import (QApplication, QDockWidget, QEvent, QEasingCurve, QGraphicsOpacityEffect, QLabel,
                    QObject, QPoint, QPointF, QPropertyAnimation, Qt, QTimer,
                    QWheelEvent)

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
    TAU_MS = 420.0      # how quickly the glide slows down (like iOS / Firefox)
    MIN_SPEED = 0.25    # px/ms at release needed to start gliding
    STOP_SPEED = 0.02   # px/ms: glide ends below this
    MAX_SPEED = 14.0    # fast swipes may cross several PDF pages

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


# ── Animated sidebars ─────────────────────────────────────────────────────

class _DockSlide(QObject):
    """Sidebars (browser, AI chat, notebook, mind map, music …) slide in from
    the side when they open and out when they close.

    The sidebar itself is laid out once at its final width; only a picture
    of it moves (cheap, so it stays smooth – resizing web pages every frame
    is what made it jerky)."""

    MS_IN = 230
    MS_OUT = 190

    def __init__(self):
        super().__init__()
        self.pictures = {}  # id(dock) → last picture of it

    def eventFilter(self, obj, event):
        kind = event.type()
        if kind not in (QEvent.Type.Show, QEvent.Type.Hide):
            return False
        if not isinstance(obj, QDockWidget) or mw is None or obj.parent() is not mw:
            return False
        if kind == QEvent.Type.Show:
            QTimer.singleShot(0, lambda: self._slide_in(obj))
        else:
            self._slide_out(obj)
        return False

    @staticmethod
    def _side(dock) -> int:
        """+1 right sidebar, -1 left, 0 not a docked sidebar."""
        try:
            if dock.isFloating():
                return 0
            area = mw.dockWidgetArea(dock)
        except RuntimeError:
            return 0
        if area == Qt.DockWidgetArea.RightDockWidgetArea:
            return 1
        if area == Qt.DockWidgetArea.LeftDockWidgetArea:
            return -1
        return 0

    def _overlay(self, dock, picture, fill: bool):
        """A plain widget over the sidebar's place holding its picture."""
        from aqt.qt import QWidget
        geo = dock.geometry()
        frame = QWidget(mw)
        frame.setGeometry(geo)
        frame.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        if fill:
            frame.setAutoFillBackground(True)
            pal = frame.palette()
            pal.setColor(frame.backgroundRole(), mw.palette().window().color())
            frame.setPalette(pal)
        label = QLabel(frame)
        label.setPixmap(picture)
        label.setGeometry(0, 0, geo.width(), geo.height())
        frame.show()
        frame.raise_()
        return frame, label

    def _move(self, frame, label, start_x: int, end_x: int, ms: int, curve) -> None:
        anim = QPropertyAnimation(label, b"pos", frame)
        anim.setStartValue(QPoint(start_x, 0))
        anim.setEndValue(QPoint(end_x, 0))
        anim.setDuration(ms)
        anim.setEasingCurve(curve)
        anim.finished.connect(frame.deleteLater)
        anim.start()

    def _slide_in(self, dock) -> None:
        try:
            side = self._side(dock)
            if not side or not dock.isVisible():
                return
            tracker = getattr(dock, "_smartstudy_width", None)
            if tracker is not None:  # settle at its remembered width first
                tracker.timer.stop()
                tracker.restore()
            width = dock.width()
            if width < 120:
                return
            picture = self.pictures.get(id(dock))
            if picture is None or picture.size() != dock.size():
                picture = dock.grab()
        except RuntimeError:
            return
        frame, label = self._overlay(dock, picture, fill=True)
        start = width if side > 0 else -width
        label.move(start, 0)
        self._move(frame, label, start, 0, self.MS_IN, QEasingCurve.Type.OutCubic)

    def _slide_out(self, dock) -> None:
        try:
            side = self._side(dock)
            if not side or dock.width() < 120 or dock.height() < 60:
                return
            picture = dock.grab()  # still holds its last frame
        except RuntimeError:
            return
        if picture.isNull():
            return
        self.pictures[id(dock)] = picture
        frame, label = self._overlay(dock, picture, fill=False)
        end = dock.width() if side > 0 else -dock.width()
        self._move(frame, label, 0, end, self.MS_OUT, QEasingCurve.Type.InCubic)


_dock_slide: Optional[_DockSlide] = None


# ── Browser tabs: cross-fade ──────────────────────────────────────────────

def crossfade(stack, old) -> None:
    """Fade the previous tab out over the new one (180 ms)."""
    try:
        if old is None or not old.isVisible() or stack.width() < 20:
            return
        picture = old.grab()
    except Exception:
        return
    cover = QLabel(stack)
    cover.setPixmap(picture)
    cover.setGeometry(old.geometry())
    cover.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    effect = QGraphicsOpacityEffect(cover)
    effect.setOpacity(1.0)
    cover.setGraphicsEffect(effect)
    cover.show()
    cover.raise_()
    anim = QPropertyAnimation(effect, b"opacity", cover)
    anim.setStartValue(1.0)
    anim.setEndValue(0.0)
    anim.setDuration(180)
    anim.setEasingCurve(QEasingCurve.Type.OutQuad)
    anim.finished.connect(cover.deleteLater)
    anim.start()


# ── Anki pages: fade in, smooth wheel, compact deck list ──────────────────

_FADE = ("<style id='ss-fade'>@keyframes ssFadeIn{from{opacity:0;transform:translateY(6px)}"
         "to{opacity:1;transform:none}}body{animation:ssFadeIn .18s ease-out both}"
         "@media (prefers-reduced-motion: reduce){body{animation:none}}</style>")

COMPACT_CSS = """<style id="ss-compact">
/* Narrow main area (browser beside Anki): the deck list fits the width. */
@media (max-width: @NARROW@px) {
  html:not(#ss-a):not(#ss-b) .sp-min-deadline-box, html:not(#ss-a):not(#ss-b) .sp-min-statistics, html:not(#ss-a):not(#ss-b) .rh-container, html:not(#ss-a):not(#ss-b) .sp-min-plan-fact-row { display: none !important; }
  html:not(#ss-a):not(#ss-b) .sp-min-overview { padding: 6px 8px !important; margin-bottom: 6px !important; }
  html:not(#ss-a):not(#ss-b) center { display: block; width: 100%; padding: 0 8px; box-sizing: border-box; }
  html:not(#ss-a):not(#ss-b) center > table, html:not(#ss-a):not(#ss-b) .decks-container, html:not(#ss-a):not(#ss-b) .decks-container table, html:not(#ss-a):not(#ss-b) .sp-min-box {
    box-sizing: border-box !important; width: 100% !important; max-width: 100% !important;
    min-width: 0 !important; margin-left: 0 !important; margin-right: 0 !important; }
  /* the deck name takes the room, the counts only what they need */
  /* Anki caps the name at 100vw - 300px: almost nothing when narrow. */
  html:not(#ss-a):not(#ss-b) td.decktd, html:not(#ss-a):not(#ss-b) th.decktd { min-width: 0 !important; max-width: none !important; width: auto !important; white-space: nowrap !important; overflow: hidden; }
  html:not(#ss-a):not(#ss-b) td.decktd a.deck { white-space: normal !important; overflow-wrap: break-word; display: inline !important; min-width: 0 !important; }
  html:not(#ss-a):not(#ss-b) .count { min-width: 0 !important; }
  /* fixed columns: the counts get what they need, the name the rest */
  html:not(#ss-a):not(#ss-b) center > table { table-layout: fixed !important; }
  html:not(#ss-a):not(#ss-b) center > table th.count { width: 4.4em !important; font-size: .86em; overflow: hidden; text-overflow: ellipsis; }
  html:not(#ss-a):not(#ss-b) center > table td[align="end"], html:not(#ss-a):not(#ss-b) center > table th.count { white-space: nowrap !important; padding-left: 3px !important; padding-right: 3px !important; }
  html:not(#ss-a):not(#ss-b) center > table th.optscol { width: 26px !important; }
  html:not(#ss-a):not(#ss-b) center > table td.opts { padding: 0 2px !important; }
  html:not(#ss-a):not(#ss-b) center > table th[colspan] { width: auto !important; }
  html:not(#ss-a):not(#ss-b), html:not(#ss-a):not(#ss-b) body { overflow-x: hidden; }
}
</style>""" .replace("@NARROW@", str(NARROW_WIDTH - 1))

_TOOLBAR_CSS = """<style id="ss-toolbar-narrow">
@media (max-width: 900px) {
  /* Anki's three equal columns squeeze the links: give them the middle. */
  .header { grid-template-columns: auto minmax(0, 1fr) auto !important; }
  .toolbar { display: flex !important; justify-content: safe center !important; justify-self: stretch !important;
             min-width: 0 !important; width: auto !important; max-width: 100% !important;
             white-space: nowrap; overflow-x: auto !important; scrollbar-width: none; }
  .toolbar::-webkit-scrollbar { display: none; }
  .hitem { padding-left: 6px !important; padding-right: 6px !important; flex: none; }
}
@media (max-width: 600px) { .hitem { font-size: 92% !important; } }
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
    if isinstance(context, DeckBrowser):
        web_content.head += COMPACT_CSS  # takes effect only while narrow
    if type(context).__name__ in ("Toolbar", "TopToolbar"):
        web_content.head += _TOOLBAR_CSS


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
    global _kinetic, _dock_slide
    app = QApplication.instance()
    if _kinetic is None and app is not None:
        _kinetic = _Kinetic()
        app.installEventFilter(_kinetic)
    if _dock_slide is None and app is not None:
        _dock_slide = _DockSlide()
        app.installEventFilter(_dock_slide)
    gui_hooks.webview_will_set_content.append(_on_content)
    gui_hooks.main_window_did_init.append(_setup_main_web)
    if getattr(mw, "web", None) is not None:
        _setup_main_web()
