"""Where the Smart Study browser is shown.

* sidebar     – the normal dock beside Anki
* split       – the same dock at half of Anki's width (cards | browser)
* main        – the browser fills Anki's main area (the embedded view)
* window      – the dock as a window of its own: any size, snap it beside Anki
                with Meta+←/→ or move it to another screen

The own window is the floating dock with normal window decorations, so
everything that shows the browser (study plan, search, launcher) keeps
working without knowing about it.
"""
from __future__ import annotations

from aqt import mw
from aqt.qt import QDockWidget, QEvent, QObject, Qt, QTimer

try:
    from .locales import _
except ImportError:  # pragma: no cover
    def _(text):  # type: ignore
        return text

_GEOM_KEY = "smartstudy_browser_window"
_window_mode = False


def _ws():
    from . import website_sidebar
    return website_sidebar


def _dock():
    return _ws().sidebar_dock


def is_window() -> bool:
    dock = _dock()
    return bool(_window_mode and dock is not None and dock.isFloating())


def mode() -> str:
    ws = _ws()
    if ws.website_window is not None:
        return "main"
    if is_window():
        return "window"
    dock = _dock()
    if dock is not None and dock.isVisible() and mw is not None and dock.width() >= mw.width() * 0.42:
        return "split"
    return "sidebar"


def fill_menu(menu) -> None:
    menu.clear()
    current = mode()
    for key, label in (("sidebar", _("Sidebar")),
                       ("split", _("Split view (cards | browser)")),
                       ("main", _("Main window")),
                       ("window", _("Own window"))):
        action = menu.addAction(label)
        action.setCheckable(True)
        action.setChecked(key == current)
        action.triggered.connect(lambda _c=False, k=key: QTimer.singleShot(0, lambda: set_mode(k)))


def set_mode(target: str) -> None:
    ws = _ws()
    if not ws.show_browser():
        return
    dock = _dock()
    current = mode()
    if current == "main" and target != "main":
        ws.close_website_window()
    if current == "window" and target != "window":
        _leave_window()
    if target == "main":
        if current != "main":
            ws.open_website_window()
    elif target == "window":
        if current != "window":
            _enter_window()
        bring_forward()
    else:
        dock.show()
        dock.raise_()
        width = max(dock.minimumWidth(), mw.width() // 2) if target == "split" else 400
        QTimer.singleShot(60, lambda: _set_width(width))


def _set_width(width: int) -> None:
    dock = _dock()
    if dock is None or dock.isFloating() or not dock.isVisible():
        return
    tracker = getattr(dock, "_smartstudy_width", None)
    if tracker is not None:
        tracker.widths[tracker.feature] = width  # restore() keeps the centre usable
        tracker.restore()
    else:
        mw.resizeDocks([dock], [width], Qt.Orientation.Horizontal)


class _GeometryKeeper(QObject):
    """Remembers the own window's size and place when it is hidden."""

    def eventFilter(self, obj, event):
        if event.type() in (QEvent.Type.Hide, QEvent.Type.Close) and is_window():
            _save_geometry()
        return False


_keeper = None


def _save_geometry() -> None:
    try:
        from aqt.utils import saveGeom
        saveGeom(_dock(), _GEOM_KEY)
    except Exception:
        pass


def _enter_window() -> None:
    global _window_mode, _keeper
    dock = _dock()
    if dock is None:
        return
    _window_mode = True
    dock.setFloating(True)
    # A real window: title bar, maximise, taskbar entry, window snapping.
    dock.setWindowFlags(Qt.WindowType.Window)
    dock.setWindowTitle("Smart Study – " + _("Browser"))
    if _keeper is None:
        _keeper = _GeometryKeeper(dock)
        dock.installEventFilter(_keeper)
    try:
        from aqt.utils import restoreGeom
        restoreGeom(dock, _GEOM_KEY, default_size=(1100, 800))
    except TypeError:
        dock.resize(1100, 800)
    except Exception:
        pass
    dock.show()


def _leave_window() -> None:
    global _window_mode
    dock = _dock()
    if dock is None:
        _window_mode = False
        return
    if dock.isVisible():
        _save_geometry()
    _window_mode = False
    dock.setFloating(False)  # Qt gives it the dock flags back
    if mw.dockWidgetArea(dock) not in (Qt.DockWidgetArea.LeftDockWidgetArea, Qt.DockWidgetArea.RightDockWidgetArea):
        mw.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
    dock.show()


def bring_forward() -> bool:
    """Raise the own browser window; False when the browser lives in Anki."""
    dock = _dock()
    if not is_window() or dock is None:
        return False
    if dock.isMinimized():
        dock.showNormal()
    dock.show()
    dock.raise_()
    dock.activateWindow()
    return True


def cleanup() -> None:
    """Before the browser is destroyed (profile switch)."""
    global _window_mode, _keeper
    if is_window():
        _save_geometry()
    _window_mode = False
    _keeper = None
