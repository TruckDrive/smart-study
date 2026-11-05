"""Where a Smart Study sidebar is shown – for the browser, AI assistant,
notebook and mind map alike.

* sidebar – the normal dock beside Anki
* split   – the dock at half of Anki's width (cards | tool)
* main    – the tool fills Anki's main area (only tools that have this view)
* window  – the dock as a window of its own: any size, snap it beside Anki
            (Meta+←/→ on KDE/Windows) or move it to another screen

The own window is the floating dock with normal window decorations, so the
code that shows or hides a tool keeps working without knowing about it.
"""
from __future__ import annotations

from typing import Callable, Dict, Optional

from aqt import mw
from aqt.qt import QCursor, QEvent, QMenu, QObject, QPushButton, Qt, QTimer

try:
    from .locales import _
except ImportError:  # pragma: no cover
    def _(text):  # type: ignore
        return text


class _Target:
    def __init__(self, key, dock, show, title, is_main=None, enter_main=None, exit_main=None):
        self.key = key
        self.dock: Callable = dock        # → the QDockWidget or None
        self.show: Callable = show        # makes the tool visible (creates it if needed) → truthy
        self.title = title
        self.is_main = is_main
        self.enter_main = enter_main
        self.exit_main = exit_main
        self.window = False
        self.keeper = None


_targets: Dict[str, _Target] = {}


def register(key: str, dock: Callable, show: Callable, title: str,
             is_main: Optional[Callable] = None, enter_main: Optional[Callable] = None,
             exit_main: Optional[Callable] = None) -> None:
    _targets[key] = _Target(key, dock, show, title, is_main, enter_main, exit_main)


def _dock(key):
    target = _targets.get(key)
    try:
        return target.dock() if target else None
    except Exception:
        return None


def is_window(key: str) -> bool:
    target = _targets.get(key)
    dock = _dock(key)
    try:
        return bool(target and target.window and dock is not None and dock.isFloating())
    except RuntimeError:
        return False


def dock_is_own_window(dock) -> bool:
    """For code that closes other tools: leave own windows alone."""
    return any(is_window(key) and _dock(key) is dock for key in _targets)


def mode(key: str) -> str:
    target = _targets.get(key)
    if target is None:
        return "sidebar"
    try:
        if target.is_main and target.is_main():
            return "main"
    except Exception:
        pass
    if is_window(key):
        return "window"
    dock = _dock(key)
    if dock is not None and dock.isVisible() and mw is not None and dock.width() >= mw.width() * 0.42:
        return "split"
    return "sidebar"


def fill_menu(menu, key: str) -> None:
    menu.clear()
    target = _targets.get(key)
    current = mode(key)
    split = _("Split view (cards | browser)") if key == "website" else _("Split view")
    choices = [("sidebar", _("Sidebar")), ("split", split)]
    if target is not None and target.enter_main is not None:
        choices.append(("main", _("Main window")))
    choices.append(("window", _("Own window")))
    for choice, label in choices:
        action = menu.addAction(label)
        action.setCheckable(True)
        action.setChecked(choice == current)
        action.triggered.connect(lambda _c=False, c=choice: QTimer.singleShot(0, lambda: set_mode(key, c)))


def menu_button(key: str, style: str = "", parent=None) -> QPushButton:
    """A ⧉ button that offers the layouts of this tool."""
    button = QPushButton("⧉", parent)
    button.setToolTip(_("Layout"))
    button.setAccessibleName(_("Layout"))
    if style:
        button.setStyleSheet(style)
    menu = QMenu(button)
    menu.aboutToShow.connect(lambda: fill_menu(menu, key))
    button.setMenu(menu)
    return button


def show_menu_at_cursor(key: str) -> None:
    menu = QMenu(mw)
    fill_menu(menu, key)
    menu.exec(QCursor.pos())


def set_mode(key: str, choice: str) -> None:
    target = _targets.get(key)
    if target is None:
        return
    current = mode(key)
    if current == "main" and choice != "main" and target.exit_main:
        target.exit_main()
    if current == "window" and choice != "window":
        _leave_window(target)
    if choice == "main":
        if current != "main" and target.enter_main:
            target.enter_main()  # creates the tool when needed
        return
    if not target.show():
        return
    dock = _dock(key)
    if dock is None:
        return
    if choice == "window":
        if current != "window":
            _enter_window(target, dock)
        bring_forward(key)
        return
    dock.show()
    dock.raise_()
    width = max(dock.minimumWidth(), mw.width() // 2) if choice == "split" else 400
    QTimer.singleShot(60, lambda: _set_width(dock, width))


def _set_width(dock, width: int) -> None:
    try:
        if dock.isFloating() or not dock.isVisible():
            return
    except RuntimeError:
        return
    tracker = getattr(dock, "_smartstudy_width", None)
    if tracker is not None:
        tracker.widths[tracker.feature] = width  # remembered for the next show
    center = mw.centralWidget()
    center_min = max(160, center.minimumSizeHint().width()) if center else 160
    width = min(width, max(dock.minimumWidth(), mw.contentsRect().width() - center_min - 12))
    # One step: resizing web pages frame by frame looks jerky.
    mw.resizeDocks([dock], [width], Qt.Orientation.Horizontal)


class _GeometryKeeper(QObject):
    """Remembers the own window's size and place when it is hidden."""

    def __init__(self, target, dock):
        super().__init__(dock)
        self.target = target

    def eventFilter(self, obj, event):
        if event.type() in (QEvent.Type.Hide, QEvent.Type.Close) and is_window(self.target.key):
            _save_geometry(self.target)
        return False


def _geom_key(target) -> str:
    return "smartstudy_%s_window" % target.key


def _save_geometry(target) -> None:
    try:
        from aqt.utils import saveGeom
        saveGeom(_dock(target.key), _geom_key(target))
    except Exception:
        pass


def _enter_window(target, dock) -> None:
    target.window = True
    dock.setFloating(True)
    # A real window: title bar, maximise, taskbar entry, window snapping.
    dock.setWindowFlags(Qt.WindowType.Window)
    dock.setWindowTitle("Smart Study – " + target.title)
    if target.keeper is None:
        target.keeper = _GeometryKeeper(target, dock)
        dock.installEventFilter(target.keeper)
    try:
        from aqt.utils import restoreGeom
        restoreGeom(dock, _geom_key(target), default_size=(1100, 800))
    except TypeError:
        dock.resize(1100, 800)
    except Exception:
        pass
    dock.show()


def _leave_window(target) -> None:
    dock = _dock(target.key)
    if dock is None:
        target.window = False
        return
    if dock.isVisible():
        _save_geometry(target)
    target.window = False
    dock.setFloating(False)  # Qt gives it the dock flags back
    if mw.dockWidgetArea(dock) not in (Qt.DockWidgetArea.LeftDockWidgetArea, Qt.DockWidgetArea.RightDockWidgetArea):
        mw.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
    dock.show()


def bring_forward(key: str) -> bool:
    """Raise the tool's own window; False when it lives inside Anki."""
    dock = _dock(key)
    if not is_window(key) or dock is None:
        return False
    if dock.isMinimized():
        dock.showNormal()
    dock.show()
    dock.raise_()
    dock.activateWindow()
    return True


def cleanup(key: str) -> None:
    """Before the tool's dock is destroyed (profile switch)."""
    target = _targets.get(key)
    if target is None:
        return
    if is_window(key):
        _save_geometry(target)
    target.window = False
    target.keeper = None
