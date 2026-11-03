# -*- coding: utf-8 -*-
"""Let hidden web pages sleep.

Every QWebEngineView keeps a Chromium renderer process (often 50–400 MB)
alive.  A page whose view has been hidden for a while is frozen (no CPU, it
keeps its memory and state) and, where that is safe, later discarded: Chromium
frees the renderer, the view keeps its URL, and the page reloads when it is
shown again.  Pages that play sound are never touched, so music and videos go
on in the background.

    web_sleep.watch(view)                         # freeze only
    web_sleep.watch(view, discard_after=600)      # and discard after 10 min

Qt builds without page lifecycle states (they came with Qt 5.14) simply
skip all of this.
"""
from __future__ import annotations

import time
import weakref
from typing import Callable, Optional

from aqt.qt import QEvent, QObject, QTimer

try:
    from PyQt6 import sip
    from PyQt6.QtWebEngineCore import QWebEnginePage
except ImportError:  # pragma: no cover
    sip = None
    QWebEnginePage = None  # type: ignore

# Seconds a view must stay hidden before its page is frozen.  Long enough for
# a page's own delayed saves (editors debounce their writes) to run first.
FREEZE_AFTER = 60
CHECK_EVERY_MS = 15000


def _states():
    try:
        return QWebEnginePage.LifecycleState
    except AttributeError:
        return None


def state(page) -> Optional[str]:
    """"Active", "Frozen", "Discarded" or None (not supported)."""
    try:
        return page.lifecycleState().name
    except (AttributeError, RuntimeError, TypeError):
        return None


def set_state(page, name: str) -> bool:
    states = _states()
    if states is None or page is None:
        return False
    try:
        if page.lifecycleState().name == name:
            return True
        page.setLifecycleState(getattr(states, name))
        # Qt refuses some changes (e.g. freezing a visible page) with a warning.
        return page.lifecycleState().name == name
    except (AttributeError, RuntimeError, TypeError):
        return False


def audible(page) -> bool:
    try:
        return bool(page.recentlyAudible())
    except (AttributeError, RuntimeError):
        return False


def wake(view) -> None:
    """Make a sleeping view's page active again (a discarded page reloads)."""
    if not _alive(view):
        return
    page = view.page()
    if page is not None and state(page) not in (None, "Active"):
        set_state(page, "Active")


def _alive(obj) -> bool:
    try:
        return obj is not None and not (sip and sip.isdeleted(obj))
    except Exception:
        return False


class _Watch(QObject):
    def __init__(self, view, discard_after, can_discard, keep_awake):
        super().__init__(view)
        self.view = weakref.ref(view)
        self.discard_after = discard_after
        self.can_discard = can_discard
        self.keep_awake = keep_awake
        self.hidden_at = None if view.isVisible() else time.monotonic()
        view.installEventFilter(self)

    def eventFilter(self, obj, event):
        kind = event.type()
        if kind == QEvent.Type.Hide:
            self.hidden_at = time.monotonic()
            _start()
        elif kind == QEvent.Type.Show:
            self.hidden_at = None
            wake(obj)
        return False

    def check(self, now: float) -> None:
        view = self.view()
        if self.hidden_at is None or not _alive(view):
            return
        page = view.page()
        if page is None:
            return
        # A hidden view whose page Qt still treats as visible is kept awake on
        # purpose (sound in the background, picture in picture).
        current = state(page)
        if current in (None, "Discarded"):
            return  # unsupported, or nothing left to free (leave it alone)
        if page.isVisible() or audible(page) or (self.keep_awake and self.keep_awake()):
            return
        if current == "Active" and page.url().isEmpty():
            return  # nothing loaded, nothing to free
        hidden_for = now - self.hidden_at
        if (self.discard_after is not None and hidden_for >= self.discard_after
                and (self.can_discard is None or self.can_discard())):
            set_state(page, "Discarded")
        elif hidden_for >= FREEZE_AFTER and current == "Active":
            set_state(page, "Frozen")


_watches = []
_timer: Optional[QTimer] = None


def watch(view, discard_after: Optional[float] = None,
          can_discard: Optional[Callable[[], bool]] = None,
          keep_awake: Optional[Callable[[], bool]] = None) -> None:
    """Let `view` sleep while it is hidden.  discard_after (seconds): also
    unload it after that long; only for pages that come back by themselves
    when reloaded.  keep_awake(): True while the page must stay active."""
    if _states() is None or not _alive(view) or getattr(view, "_ss_sleep", None) is not None:
        return
    view._ss_sleep = _Watch(view, discard_after, can_discard, keep_awake)
    _watches.append(view._ss_sleep)
    _start()


def _start() -> None:
    global _timer
    if _timer is None:
        _timer = QTimer()
        _timer.setInterval(CHECK_EVERY_MS)
        _timer.timeout.connect(_check)
    if not _timer.isActive():
        _timer.start()


def _check() -> None:
    now = time.monotonic()
    for item in list(_watches):
        if not _alive(item) or item.view() is None or not _alive(item.view()):
            _watches.remove(item)
            continue
        item.check(now)
    if not any(w.hidden_at is not None for w in _watches if _alive(w)):
        _timer.stop()  # nothing hidden: no need to look


def stop() -> None:
    """On profile close."""
    if _timer is not None:
        _timer.stop()
    _watches.clear()
