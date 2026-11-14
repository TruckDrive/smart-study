# -*- coding: utf-8 -*-
"""The Smart Study side panel: one column on the right of Anki.

On top sits a small header (Pomodoro, music, settings and the tabs), below it
either the "Today" page or one of the tools. The tools keep their own docks
and their own layout menu (sidebar, split, main window, own window); the
panel only decides which of them is shown and marks the matching tab.
"""
from __future__ import annotations

import json
import time
import traceback
from datetime import date, datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

from aqt import gui_hooks, mw
from aqt.operations import QueryOp
from aqt.qt import (
    QByteArray, QColor, QDockWidget, QEvent, QFrame, QHBoxLayout, QIcon, QLabel, QMenu,
    QObject, QPainter, QPixmap, QPushButton, QSize, QSizePolicy, Qt, QTimer, QToolBar, QToolButton,
    QVBoxLayout, QWidget,
)
from aqt.webview import AnkiWebView

from . import constants, design
from .constants import is_night

try:
    from .locales import _
except ImportError:  # pragma: no cover
    def _(text):  # type: ignore
        return text

try:
    from PyQt6.QtSvg import QSvgRenderer
except ImportError:  # pragma: no cover
    QSvgRenderer = None  # type: ignore

TITLE_WRAP = "SmartStudyPanelTitle"
RAIL_BAR = "SmartStudyRail"
RAIL_WIDTH = 84
SEPARATOR_MARK = "/* smart study panel */"
TODAY_DOCK = "SmartStudyPanelToday"
PANEL_WIDTH = 372
BRIDGE = "sspanel:"

DUE_CHOICES = (7, 14, 30)
REVIEW_CHOICES = (7, 30, 365)
MEMORY_CHOICES = (1, 7, 30, 90, 365)

# Which setting shows which part of the Today page.
SHOW_KEYS = {
    "countdown": "deadline_bar_enabled",
    "plan": "panel_show_plan",
    "level": "gamification_widgets_enabled",
    "challenge": "panel_show_challenge",
    "fact": "panel_show_fact",
    "due": "panel_show_due",
    "reviews": "stats_show_consistency",
    "memory": "stats_show_retention",
}

DEFAULTS = {
    "home_layout": "panel", "panel_open": True, "panel_show_plan": True,
    "panel_show_challenge": True, "panel_show_fact": False, "panel_show_due": True, "panel_due_days": 7,
    "panel_plan_items": 4, "panel_tabs_side": "right", "panel_rail_open": True,
}

ICONS = {
    "today": '<path d="M5 6h14v14H5zM5 10h14M9 3v4M15 3v4"/>',
    "ai": '<path d="M5 6h14v10H10l-5 4z"/>',
    "website": '<circle cx="12" cy="12" r="8"/><path d="M4 12h16M12 4c3 3 3 13 0 16M12 4c-3 3-3 13 0 16"/>',
    "notebook": '<path d="M7 4h11v16H7zM4 8h3M4 12h3M4 16h3M10 9h5M10 13h5"/>',
    "mindmap": '<path d="M10 4h4v4h-4zM4 16h4v4H4zM16 16h4v4h-4zM12 8v4M6 16v-4h12v4"/>',
    "trophies": '<path d="M8 4h8v5a4 4 0 0 1-8 0zM8 6H5a3 3 0 0 0 3 4M16 6h3a3 3 0 0 1-3 4M12 13v4M9 20h6"/>',
    "play": '<path d="M8 5.5v13l10-6.5z"/>',
    "pause": '<path d="M9 6v12M15 6v12"/>',
    "music": '<path d="M9 18V6l10-2v12"/><circle cx="6.5" cy="18" r="2.5"/><circle cx="16.5" cy="16" r="2.5"/>',
    "hide": '<path d="M4 5h16v14H4zM14 5v14"/>',
    "gear": '<circle cx="12" cy="12" r="3"/><path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1"/>',
}


def icon(name: str, color: str, size: int = 22, active: Optional[str] = None) -> QIcon:
    """A line icon in the given colour; ``active`` is the colour while checked."""
    result = QIcon()
    if QSvgRenderer is None:
        return result
    ratio = mw.devicePixelRatioF() if mw else 1.0
    for tint, state in ((color, QIcon.State.Off), (active or color, QIcon.State.On)):
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{tint}" '
               f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg>')
        pixmap = QPixmap(int(size * ratio), int(size * ratio))
        pixmap.fill(QColor(0, 0, 0, 0))
        painter = QPainter(pixmap)
        QSvgRenderer(QByteArray(svg.encode())).render(painter)
        painter.end()
        pixmap.setDevicePixelRatio(ratio)
        result.addPixmap(pixmap, QIcon.Mode.Normal, state)
    return result


class _Tool:
    def __init__(self, key, label, setting, dock_name, toggle, layout_key=None):
        self.key, self.label, self.setting = key, label, setting
        self.dock_name, self.toggle, self.layout_key = dock_name, toggle, layout_key


def _tools(toggle_trophies: Callable) -> List[_Tool]:
    def lazy(module, name):
        def run():
            import importlib
            getattr(importlib.import_module(f"{__package__}.{module}"), name)()
        return run
    return [
        _Tool("ai", _("Assistant"), "ai_assistant_enabled", constants.AI_ASSISTANT_DOCK_OBJECT_NAME,
              lazy("ai_assistant", "toggle_ai_assistant_dock"), "ai"),
        _Tool("website", _("Browser"), "website_viewer_enabled", constants.WEBSITE_DOCK_OBJECT_NAME,
              lazy("website_sidebar", "toggle_website_dock"), "website"),
        _Tool("notebook", _("Notebook"), "notebook_enabled", constants.NOTEBOOK_DOCK_OBJECT_NAME,
              lazy("notebook_sidebar", "toggle_notebook_dock"), "notebook"),
        _Tool("mindmap", _("Mind map"), "mindmap_enabled", constants.MINDMAP_DOCK_OBJECT_NAME,
              lazy("mindmap_sidebar", "toggle_mindmap_dock"), "mindmap"),
        _Tool("trophies", _("Trophies"), "gamification_sidebar_enabled", "GamificationSidebar",
              toggle_trophies),
    ]


def logo_icon(size: int) -> QIcon:
    """The Smart Study logo in the colour of the chosen accent."""
    result = QIcon()
    if QSvgRenderer is None:
        return result
    try:
        import os
        from . import theme
        names = {"orchid": "logo_orchid.svg", "forest": "logo_forest.svg", "deluge": "logo_deluge.svg",
                 "horizon": "logo_horizon.svg", "dusty": "logo_dusty.svg", "orange": "logo_orange.svg"}
        folder = getattr(constants, "icons_folder", "")
        name = theme.get_active_theme()
        path = os.path.join(folder, names.get(name, "logo.svg"))
        if not os.path.exists(path):
            path = os.path.join(folder, "logo.svg")
        if name in ("petrol", "custom"):
            from .logo_utils import recoloured_brand_svg_bytes
            data = QByteArray(recoloured_brand_svg_bytes(path, theme.palette(False).get("blue", "#0B6570")))
        else:
            with open(path, "rb") as handle:
                data = QByteArray(handle.read())
        ratio = mw.devicePixelRatioF() if mw else 1.0
        pixmap = QPixmap(int(size * ratio), int(size * ratio))
        pixmap.fill(QColor(0, 0, 0, 0))
        painter = QPainter(pixmap)
        QSvgRenderer(data).render(painter)
        painter.end()
        pixmap.setDevicePixelRatio(ratio)
        result.addPixmap(pixmap)
    except Exception as error:
        print(f"SmartStudy: logo could not be drawn: {error}")
    return result


class _LogoButton(QToolButton):
    """The logo opens the settings; while the pointer is on it, it shows a gear."""

    def __init__(self, open_settings: Callable):
        super().__init__()
        self.setObjectName("ssLogo")
        self.setToolTip(_("Open Add-on Settings"))
        self.setAccessibleName(_("Open Add-on Settings"))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setFixedSize(48, 48)
        self.setIconSize(QSize(40, 40))
        self.clicked.connect(lambda _checked=False: open_settings())
        self._logo = QIcon()
        self._gear = QIcon()

    def set_icons(self, logo: QIcon, gear: QIcon) -> None:
        self._logo, self._gear = logo, gear
        self.setIcon(self._gear if self.underMouse() else self._logo)
        self.setIconSize(QSize(26, 26) if self.underMouse() else QSize(40, 40))

    def enterEvent(self, event):
        self.setIcon(self._gear)
        self.setIconSize(QSize(26, 26))
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setIcon(self._logo)
        self.setIconSize(QSize(40, 40))
        super().leaveEvent(event)


class Header(QWidget):
    """Pomodoro, music, settings and the tabs: as a bar on top of the column,
    or upright as a rail at the edge of the window."""

    def __init__(self, panel: "Panel", vertical: bool = False):
        super().__init__()
        self.panel = panel
        self.vertical = vertical
        self.setObjectName("ssHeader")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.tab_buttons: Dict[str, QToolButton] = {}
        self.time_button: Optional[QPushButton] = None
        self.play_button: Optional[QToolButton] = None
        self.music_button: Optional[QToolButton] = None
        settings = panel.settings
        outer = QVBoxLayout(self)
        Line = QVBoxLayout if vertical else QHBoxLayout

        self.tabs = QFrame()
        self.tabs.setObjectName("ssTabs")
        tab_row = Line(self.tabs)
        tab_row.setContentsMargins(4, 4, 4, 4)
        tab_row.setSpacing(2)
        self._tab("today", _("Today"), tab_row)
        for tool in panel.tools:
            if settings.get(tool.setting, True):
                self._tab(tool.key, tool.label, tab_row)

        self.pill = QFrame()
        self.pill.setObjectName("ssPill")
        row = Line(self.pill)
        row.setSpacing(0)
        if settings.get("pomodoro_enabled", True):
            self.time_button = QPushButton("25:00")
            self.time_button.setObjectName("ssTime")
            self.time_button.setCursor(Qt.CursorShape.PointingHandCursor)
            self.time_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.time_button.setToolTip(_("Pomodoro: reset, skip, settings"))
            self.time_button.clicked.connect(self._pomodoro_menu)
            row.addWidget(self.time_button)
            self.play_button = self._round("play", _("Start/Pause Timer"), self._start_pause, flat=True)
            row.addWidget(self.play_button, 0, Qt.AlignmentFlag.AlignHCenter)
        if settings.get("music_player_enabled", True):
            self.music_button = self._round("music", _("Play Music"), self._music, flat=True)
            row.addWidget(self.music_button, 0, Qt.AlignmentFlag.AlignHCenter)

        if vertical:
            outer.setContentsMargins(6, 10, 6, 10)
            outer.setSpacing(10)
            row.setContentsMargins(2, 6, 2, 6)
            self.gear = _LogoButton(panel.ctx["show_settings"])
            outer.addWidget(self.gear, 0, Qt.AlignmentFlag.AlignHCenter)
            outer.addWidget(self.tabs)
            outer.addStretch(1)
            outer.addWidget(self.pill)
            self.hide_button = self._round("hide", _("Show or hide the side panel"), panel.collapse, flat=True)
            row.addWidget(self.hide_button, 0, Qt.AlignmentFlag.AlignHCenter)
            self.setFixedWidth(RAIL_WIDTH)
        else:
            outer.setContentsMargins(4, 12, 12, 8)
            outer.setSpacing(12)
            row.setContentsMargins(6, 2, 4, 2)
            top = QHBoxLayout()
            top.setSpacing(8)
            self.gear = _LogoButton(panel.ctx["show_settings"])
            top.addWidget(self.gear)
            top.addStretch(1)
            self.hide_button = self._round("hide", _("Hide side panel"), panel.toggle, flat=True)
            row.addWidget(self.hide_button)
            top.addWidget(self.pill)
            outer.addLayout(top)
            outer.addWidget(self.tabs)
        self.restyle()

    def _round(self, name, tip, slot, flat=False) -> QToolButton:
        button = QToolButton()
        button.setObjectName("ssFlat" if flat else "ssRound")
        button.setProperty("ssIcon", name)
        button.setToolTip(tip)
        button.setAccessibleName(tip)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setFixedSize(40, 40)
        button.setIconSize(QSize(18, 18))
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # Space and Enter stay with the card
        button.clicked.connect(lambda _checked=False: slot())
        return button

    def _tab(self, key, label, layout) -> None:
        button = QToolButton()
        button.setObjectName("ssTab")
        button.setProperty("ssIcon", key)
        button.setText(label)
        button.setCheckable(True)
        button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        button.setIconSize(QSize(22, 22))
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        if self.vertical:
            button.setFixedSize(RAIL_WIDTH - 22, 54)
        else:
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            button.setFixedHeight(52)
            button.setMinimumWidth(0)
        button.clicked.connect(lambda _checked=False, k=key: self.panel.select(k))
        if key != "today":
            button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            button.customContextMenuRequested.connect(lambda _pos, k=key: self.panel.layout_menu(k))
        layout.addWidget(button)
        self.tab_buttons[key] = button

    def restyle(self) -> None:
        c = design.tokens(is_night())
        self.setStyleSheet(f"""
        QWidget#ssHeader {{ background: {c['page']}; }}
        QFrame#ssPill {{ background: {c['card']}; border: 1px solid {c['line']}; border-radius: {14 if self.vertical else 22}px; }}
        QFrame#ssTabs {{ background: {c['card']}; border: 1px solid {c['line']}; border-radius: 14px; }}
        QPushButton#ssTime {{ background: transparent; border: none; color: {c['ink']};
            font-size: {14 if self.vertical else 16}px; font-weight: 700;
            padding: {'0' if self.vertical else '0 8px 0 10px'}; min-height: {30 if self.vertical else 40}px; }}
        QPushButton#ssTime:hover {{ color: {c['accent']}; }}
        QToolButton#ssFlat {{ background: transparent; border: none; border-radius: 20px; }}
        QToolButton#ssFlat:hover {{ background: {c['raised']}; }}
        QToolButton#ssRound {{ background: {c['card']}; border: 1px solid {c['line']}; border-radius: 20px; }}
        QToolButton#ssRound:hover {{ background: {c['raised']}; }}
        QToolButton#ssTab {{ background: transparent; border: none; border-radius: 10px; color: {c['muted']};
            font-size: 11px; padding: 3px 0 1px; }}
        QToolButton#ssTab:hover {{ background: {c['hover']}; color: {c['ink']}; }}
        QToolButton#ssTab:checked {{ background: {c['raised']}; color: {c['accent']}; }}
        QToolButton#ssLogo {{ background: transparent; border: none; border-radius: 12px; }}
        QToolButton#ssLogo:hover {{ background: {c['raised']}; }}
        QToolButton:focus {{ outline: none; }}
        """)
        self.gear.set_icons(logo_icon(40), icon("gear", c["accent"], 26))
        for button in self.findChildren(QToolButton):
            name = button.property("ssIcon")
            if name:
                size = 22 if button.objectName() == "ssTab" else 18
                button.setIcon(icon(name, c["muted"], size, c["accent"]))
        self.update_timer()

    # -- Pomodoro and music --------------------------------------------------
    def _pomodoro(self):
        from . import pomodoro
        return pomodoro

    def _start_pause(self) -> None:
        self._pomodoro().start_pause_action()

    def _pomodoro_menu(self) -> None:
        pomodoro = self._pomodoro()
        menu = QMenu(self)
        running = pomodoro.current_state in (constants.STATE_WORK, constants.STATE_SHORT_BREAK,
                                             constants.STATE_LONG_BREAK)
        # Lambdas: Qt would hand the action's "checked" flag to the functions.
        menu.addAction(_("Pause") if running else _("Start")).triggered.connect(lambda *_a: pomodoro.start_pause_action())
        menu.addAction(_("Reset Timer")).triggered.connect(lambda *_a: pomodoro.reset_action())
        menu.addAction(_("Skip current phase")).triggered.connect(lambda *_a: pomodoro.skip_action())
        menu.addSeparator()
        menu.addAction(_("Timer Settings")).triggered.connect(lambda *_a: pomodoro.open_pomodoro_config())
        corner = self.time_button.rect().topLeft() if self.vertical else self.time_button.rect().bottomLeft()
        menu.exec(self.time_button.mapToGlobal(corner))

    def _music(self) -> None:
        from . import background_music
        background_music.toggle_music_menu(self.music_button)

    def update_timer(self) -> None:
        """Called by the Pomodoro whenever its state changes."""
        if not self.time_button or not self.play_button:
            return
        try:
            pomodoro = self._pomodoro()
            state = pomodoro.current_state
            running = state in (constants.STATE_WORK, constants.STATE_SHORT_BREAK, constants.STATE_LONG_BREAK)
            c = design.tokens(is_night())
            self.play_button.setIcon(icon("pause" if running else "play", c["accent"] if running else c["muted"], 18))
            shown = state if state != constants.STATE_PAUSED else pomodoro.previous_state
            if shown == constants.STATE_IDLE:
                shown = pomodoro.intended_next_state or constants.STATE_WORK
            phase = _("Break") if shown in (constants.STATE_SHORT_BREAK, constants.STATE_LONG_BREAK) else _("Pomodoro")
            self.time_button.setAccessibleName(phase)
            self._phase = phase
            self.update_label()
        except Exception as error:
            print(f"SmartStudy: timer display failed: {error}")

    def update_label(self) -> None:
        if not self.time_button:
            return
        try:
            pomodoro = self._pomodoro()
            seconds = pomodoro.time_remaining or pomodoro.get_current_phase_duration()
            phase = getattr(self, "_phase", "")
            clock = pomodoro.format_time(seconds)
            self.time_button.setText(clock if self.vertical else f"{clock}  {phase}")
            if self.vertical:
                self.time_button.setToolTip(f"{phase}: " + _("Pomodoro: reset, skip, settings"))
        except Exception:
            pass

    # launcher_widget API that the Pomodoro expects
    update_timer_ui = update_timer
    update_timer_label_only = update_label


class _DockWatcher(QObject):
    """Notices tools that are created later (they are built on first use)."""

    def __init__(self, panel: "Panel"):
        super().__init__(mw)
        self.panel = panel
        mw.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj is mw and event.type() == QEvent.Type.ChildAdded:
            QTimer.singleShot(0, self.panel.wire)
            QTimer.singleShot(700, self.panel.wire)
        return False


class Panel(QObject):
    def __init__(self, settings: Dict[str, Any], ctx: Dict[str, Callable]):
        super().__init__(mw)
        self.settings = settings
        self.ctx = ctx
        self.tools = _tools(ctx["toggle_trophies"])
        self._wired: Dict[str, Any] = {}
        self._busy = False
        self._again = False
        self._loaded = False
        self._last_json = ""
        self._closing = False

        self._open = bool(settings.get("panel_open", True))
        self._force_today = False
        self.headers: List[Header] = []
        side = settings.get("panel_tabs_side", "right")
        self.side = side if side in ("right", "left", "top") else "right"
        self.rail_bar: Optional[QToolBar] = None

        self.web = AnkiWebView(mw, title="smart study today")
        self.web.set_bridge_command(self._on_bridge, self)
        self.today_dock = self._dock(TODAY_DOCK, self.web)
        if self.side == "top":
            self.header = self._new_header()
            self.today_dock.setTitleBarWidget(self.header)
        else:
            self.header = self._new_header(vertical=True)
            self._build_rail()
        self.today_dock.setMinimumWidth(300)
        mw.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.today_dock)
        self._style_window()
        try:
            from . import web_sleep
            web_sleep.watch(self.web)
        except Exception:
            pass
        self._load_page()
        self.today_dock.visibilityChanged.connect(self._today_shown)

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._collect)
        self._watcher = _DockWatcher(self)
        self._hooks = [
            (gui_hooks.reviewer_did_answer_card, lambda *_a: self.refresh(4000)),
            (gui_hooks.state_did_change, lambda *_a: (setattr(self, "_force_today", False), self.sync(), self.refresh(150))),
            (gui_hooks.sync_did_finish, lambda *_a: self.refresh(300)),
            (gui_hooks.operation_did_execute, lambda *_a: self.refresh(1500)),
            (gui_hooks.theme_did_change, self.restyle),
        ]
        for hook, fn in self._hooks:
            hook.append(fn)

        self.today_dock.setVisible(self._open)
        QTimer.singleShot(0, lambda: self._set_width(PANEL_WIDTH))
        self.wire()
        self.sync()

    # -- building --------------------------------------------------------------
    def _dock(self, name: str, widget: QWidget) -> QDockWidget:
        old = mw.findChild(QDockWidget, name)
        if old is not None:
            old.setVisible(False)
            old.deleteLater()
        dock = QDockWidget("", mw)
        dock.setObjectName(name)
        dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        dock.setTitleBarWidget(QWidget())
        dock.setWidget(widget)
        return dock

    def _build_rail(self) -> None:
        """The tabs as an upright rail at the edge of the window, outside the docks."""
        old = mw.findChild(QToolBar, RAIL_BAR)
        if old is not None:
            mw.removeToolBar(old)
            old.deleteLater()
        bar = QToolBar(mw)
        bar.setObjectName(RAIL_BAR)
        bar.setMovable(False)
        bar.setFloatable(False)
        bar.toggleViewAction().setVisible(False)
        bar.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)
        bar.addWidget(self.header)
        area = Qt.ToolBarArea.LeftToolBarArea if self.side == "left" else Qt.ToolBarArea.RightToolBarArea
        mw.addToolBar(area, bar)
        bar.setVisible(bool(self.settings.get("panel_rail_open", True)))
        self.rail_bar = bar

    def _new_header(self, vertical: bool = False) -> Header:
        header = Header(self, vertical)
        self.headers.append(header)
        return header

    def _alive_headers(self) -> List[Header]:
        alive = []
        for header in self.headers:
            try:
                header.objectName()
                alive.append(header)
            except RuntimeError:
                pass
        self.headers = alive
        return alive

    def update_timer_ui(self) -> None:
        for header in self._alive_headers():
            header.update_timer()

    def update_timer_label_only(self) -> None:
        for header in self._alive_headers():
            header.update_label()

    def _wrap(self, dock: QDockWidget) -> None:
        """Put the panel header above the tool's own title bar."""
        if self.side != "top":
            return
        current = dock.titleBarWidget()
        if current is not None and current.objectName() == TITLE_WRAP:
            old = current.findChild(Header)
            header = self._new_header()
            current.layout().insertWidget(0, header)
            if old is not None:
                old.setParent(None)
                old.deleteLater()
            return
        box = QWidget()
        box.setObjectName(TITLE_WRAP)
        layout = QVBoxLayout(box)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._new_header())
        if current is not None:
            layout.addWidget(current)
        dock.setTitleBarWidget(box)
        if current is not None:
            current.show()

    def _style_window(self) -> None:
        c = design.tokens(is_night())
        self.today_dock.setStyleSheet(f"QDockWidget {{ background: {c['page']}; border: none; }}")
        # The line between Anki and the panel takes the panel's colour.
        rule = f"{SEPARATOR_MARK}QMainWindow::separator {{ background: {c['page']}; width: 6px; height: 6px; image: none; }}"
        rule += f" QToolBar#{RAIL_BAR} {{ background: {c['page']}; border: none; padding: 0; spacing: 0; }}"
        mw.setStyleSheet(mw.styleSheet().split(SEPARATOR_MARK)[0] + rule)
        try:
            self.web.page().setBackgroundColor(QColor(c["page"]))
        except Exception:
            pass

    def _today_shown(self, visible: bool) -> None:
        if visible and not self._closing:
            self.refresh()
            # A tool in split view leaves the column wide; Today takes its own width again.
            QTimer.singleShot(0, lambda: self._set_width(PANEL_WIDTH))

    def _set_width(self, width: int) -> None:
        try:
            if self.today_dock.isVisible():
                mw.resizeDocks([self.today_dock], [width], Qt.Orientation.Horizontal)
        except RuntimeError:
            pass

    def _load_page(self) -> None:
        folder = mw.addonManager.addonFromModule(__name__)
        base = f"/_addons/{folder}/web_panel/"
        night = is_night()
        head = f"<style id='ss-tokens'>:root{{{design.css_vars(night)}}}</style>"
        self._loaded = False
        self._last_json = ""
        self.web.stdHtml(f'<div id="app" class="{"" if self.side == "top" else "rail"}"></div>', css=[base + "today.css"], js=[base + "today.js"],
                         head=head, context=self)

    def restyle(self, *_args) -> None:
        if self._closing:
            return
        for header in self._alive_headers():
            header.restyle()
        self._style_window()
        self._load_page()

    apply_stylesheet = restyle  # name the settings code calls after a change

    # -- which tab is shown ----------------------------------------------------
    def _find(self, tool: _Tool) -> Optional[QDockWidget]:
        try:
            return mw.findChild(QDockWidget, tool.dock_name)
        except RuntimeError:
            return None

    def wire(self) -> None:
        """Follow the visibility of every tool dock that exists by now."""
        if self._closing:
            return
        for tool in self.tools:
            dock = self._find(tool)
            if dock is None or self._wired.get(tool.key) is dock:
                continue
            self._wired[tool.key] = dock
            self._wrap(dock)
            dock.visibilityChanged.connect(lambda _visible, self=self: QTimer.singleShot(0, self.sync))
            dock.topLevelChanged.connect(lambda _floating, self=self: QTimer.singleShot(0, self.sync))
        self.sync()

    def sync_dock_button(self, _dock_name=None) -> None:  # name used by the tools
        self.wire()

    def _in_column(self, tool: _Tool) -> bool:
        """The tool is open inside the right column (not as its own window)."""
        dock = self._wired.get(tool.key)
        try:
            return bool(dock is not None and dock.isVisible() and not dock.isFloating())
        except RuntimeError:
            self._wired.pop(tool.key, None)
            return False

    def _fills_anki(self, tool: _Tool) -> bool:
        """The tool is shown as "Main window": it replaces Anki's middle part."""
        if not tool.layout_key:
            return False
        try:
            from . import dock_layout
            return tool.layout_key in dock_layout._targets and dock_layout.mode(tool.layout_key) == "main"
        except Exception:
            return False

    def active(self) -> str:
        for tool in self.tools:
            if self._in_column(tool) or self._fills_anki(tool):
                return tool.key
        return "today"

    def _resting(self) -> bool:
        """While reviewing the Today page stays away; it belongs to the home screen."""
        return getattr(mw, "state", "") == "review" and not self._force_today

    def sync(self) -> None:
        if self._closing:
            return
        try:
            key = self.active()
            reviewing = getattr(mw, "state", "") == "review"
            if self.rail_bar is not None:
                hidden = reviewing and self.settings.get("sidebar_visibility_mode") == "hide_review"
                self.rail_bar.setVisible(bool(self.settings.get("panel_rail_open", True)) and not hidden)
            self.today_dock.setVisible(self._open and key == "today" and not self._resting())
            shown = key if key != "today" else ("today" if self.today_dock.isVisible() else "")
            for header in self._alive_headers():
                for name, button in header.tab_buttons.items():
                    button.setChecked(name == shown)
            for tool in self.tools:  # an own window keeps only the tool's own bar
                dock = self._wired.get(tool.key)
                bar = dock.titleBarWidget() if dock is not None else None
                inner = bar.findChild(Header) if bar is not None and bar.objectName() == TITLE_WRAP else None
                if inner is not None:
                    inner.setVisible(not dock.isFloating())
            self.ctx["panel_changed"]()
        except RuntimeError:
            pass

    def _close_tools(self, keep: Optional[str] = None) -> None:
        for tool in self.tools:
            if tool.key != keep and self._fills_anki(tool):
                try:
                    from . import dock_layout
                    dock_layout._targets[tool.layout_key].exit_main()
                    self.wire()
                    if self._in_column(tool):  # leaving the main window puts it back into the column
                        tool.toggle()
                except Exception as error:
                    print(f"SmartStudy: could not leave the main window of {tool.key}: {error}")
            elif tool.key != keep and self._in_column(tool):
                try:
                    tool.toggle()
                except Exception as error:
                    print(f"SmartStudy: could not close {tool.key}: {error}")

    def select(self, key: str) -> None:
        self.wire()
        current = self.active()
        if key == "today" and current == "today" and self.today_dock.isVisible() and self.rail_bar is not None:
            self._set_open(False)  # a second click on the rail folds the page away
            return
        if key == "today" or key == current:
            self._open = True  # leaving a tool always lands on Today
            self._force_today = key == "today"
            self._close_tools()
            QTimer.singleShot(0, self.sync)
            return
        tool = next(t for t in self.tools if t.key == key)
        self._close_tools(keep=key)
        try:
            if tool.layout_key:
                from . import dock_layout
                if dock_layout.bring_forward(tool.layout_key):
                    self.sync()
                    return
            tool.toggle()
        except Exception as error:
            print(f"SmartStudy: could not open {key}: {error}")
            traceback.print_exc()
        self.wire()
        QTimer.singleShot(0, self.wire)

    def layout_menu(self, key: str) -> None:
        tool = next((t for t in self.tools if t.key == key), None)
        if tool is None or not tool.layout_key:
            return
        from . import dock_layout
        if tool.layout_key == "website":
            from . import browser_layout
            browser_layout._register()
        if tool.layout_key not in dock_layout._targets:
            # The tool is built on first use; open it once, then offer its layouts.
            if self.active() != key:
                self.select(key)
            QTimer.singleShot(400, lambda: tool.layout_key in dock_layout._targets
                              and dock_layout.show_menu_at_cursor(tool.layout_key))
            return
        dock_layout.show_menu_at_cursor(tool.layout_key)

    def content_open(self) -> bool:
        try:
            return self.today_dock.isVisible() or self.active() != "today"
        except RuntimeError:
            return False

    def is_open(self) -> bool:
        """What the button in Anki's top bar shows: the rail, or the column without a rail."""
        try:
            if self.rail_bar is not None:
                return self.rail_bar.isVisible()
        except RuntimeError:
            return False
        return self.content_open()

    def _set_open(self, open_: bool) -> None:
        if not open_:
            self._close_tools()
        self._open = open_
        self._force_today = False
        self.settings["panel_open"] = open_
        self.ctx["save"]()
        QTimer.singleShot(0, self.sync)
        if open_:
            QTimer.singleShot(0, lambda: self._set_width(PANEL_WIDTH))

    def collapse(self) -> None:
        """The rail's own button: fold the column away, the rail stays."""
        if self.content_open():
            self._set_open(False)
        else:
            self._force_today = True
            self._set_open(True)
            self._force_today = True

    def toggle(self) -> None:
        """The button in Anki's top bar: everything away, or back."""
        if self.rail_bar is None:
            self._set_open(not self.content_open())
            return
        show = not self.rail_bar.isVisible()
        self.settings["panel_rail_open"] = show
        if not show:
            self._close_tools()
            self._open = False
        else:
            self._open = True
        self.settings["panel_open"] = self._open
        self.ctx["save"]()
        QTimer.singleShot(0, self.sync)

    # -- Today page ------------------------------------------------------------
    def refresh(self, delay: int = 0) -> None:
        if self._closing:
            return
        if not self._timer.isActive() or delay < self._timer.remainingTime():
            self._timer.start(delay)

    def _collect(self) -> None:
        if self._closing or not mw.col or not self._loaded:
            return
        try:
            if not self.today_dock.isVisible():
                return
        except RuntimeError:
            return
        if self._busy:
            self._again = True
            return
        self._busy = True
        settings = dict(self.settings)

        def done(data):
            self._busy = False
            if self._closing:
                return
            try:
                self._finish(data)
            finally:
                if self._again:
                    self._again = False
                    self.refresh(200)

        def failed(error):
            self._busy = False
            print(f"SmartStudy: Today page could not be filled: {error}")

        QueryOp(parent=mw, op=lambda col: collect(col, settings), success=done).failure(
            failed).run_in_background()

    def _finish(self, data: Dict[str, Any]) -> None:
        settings = self.settings
        data["show"] = {name: bool(settings.get(key, True)) for name, key in SHOW_KEYS.items()}
        manager = getattr(mw, "gamification_manager", None)
        if manager:
            try:
                data["level"] = manager.get_level()
                data["streak"] = manager.get_streak()
                data["rank"] = _(manager.get_rank_name())
                data["xp"] = manager.get_progress_percentage()
                current, target = manager.get_challenge_progress()
                data["challenge"] = {
                    "text": manager.get_current_challenge()[0], "cur": current, "target": target,
                    "claimed": manager.is_challenge_completed_today(), "xp": manager.get_daily_challenge_xp(),
                }
            except Exception as error:
                print(f"SmartStudy: level display failed: {error}")
        if data.get("countdown") is None:
            data["countdown"] = self._deadline()
        if data["show"]["fact"]:
            try:
                from . import daily_widgets
                data["fact"] = daily_widgets.todays_fact(settings.get("fact_theme", "Medical"))
            except Exception as error:
                print(f"SmartStudy: daily fact failed: {error}")
        data["t"] = texts()
        payload = json.dumps(data, ensure_ascii=False)
        if payload == self._last_json:
            return
        self._last_json = payload
        self.web.eval(f"SSToday.render({payload});")

    def _deadline(self) -> Optional[Dict[str, Any]]:
        manager = getattr(mw, "deadline_manager", None)
        try:
            info = manager.calculate_progress() if manager else None
            if info and "days_remaining" in info:
                return {"days": info["days_remaining"], "title": info["title"], "source": "deadline"}
        except Exception:
            pass
        return None

    def _on_bridge(self, message: str) -> Any:
        if message == "domDone":
            return None
        if not message.startswith(BRIDGE):
            return None
        try:
            data = json.loads(message[len(BRIDGE):])
            result = self._command(data.get("cmd"), data.get("args") or {})
            if data.get("cmd") in ("toggle", "period", "show", "claim"):
                # Anki's own keys (Space, numbers, shortcuts) keep working after a click here.
                QTimer.singleShot(0, lambda: mw.web.setFocus() if mw.web.isVisible() else None)
            return result
        except Exception as error:
            traceback.print_exc()
            from aqt.utils import tooltip
            tooltip(str(error) or type(error).__name__)
            self._last_json = ""
            self.refresh()
            return None

    def _command(self, cmd: str, a: Dict[str, Any]) -> Any:
        settings = self.settings
        if cmd == "ready":
            self._loaded = True
            self.refresh()
        elif cmd == "toggle":
            from . import plan
            plan.handle("toggle", {"id": a["plan"], "item": a["item"], "on": bool(a["on"])})
            plan._changed()
            self.refresh()
        elif cmd == "study":
            from . import plan
            result = plan.handle("studyItem", {"id": a["plan"], "item": a["item"]})
            if isinstance(result, dict) and result.get("ok") is False:
                from aqt.utils import tooltip
                tooltip(_("No matching cards (left)."))
        elif cmd == "openPlan":
            self.ctx["open_plan"]()
        elif cmd == "countdown":
            if a.get("source") == "deadline":
                self.ctx["open_deadlines"]()
            else:
                self.ctx["open_plan"]()
        elif cmd == "period":
            key, choices = {"due": ("panel_due_days", DUE_CHOICES), "reviews": ("stats_consistency_days", REVIEW_CHOICES),
                            "memory": ("stats_time_range", MEMORY_CHOICES)}[a["which"]]
            days = int(a["days"])
            if days in choices:
                settings[key] = days
                self.ctx["save"]()
                self.ctx["stats_changed"]()
                self.refresh()
        elif cmd == "show":
            key = SHOW_KEYS[a["which"]]
            settings[key] = bool(a["on"])
            self.ctx["save"]()
            self._last_json = ""
            self.refresh()
        elif cmd == "claim":
            manager = getattr(mw, "gamification_manager", None)
            if manager:
                manager.on_complete_challenge()
            self.refresh()
        elif cmd == "trophies":
            self.select("trophies")
        elif cmd == "settings":
            self.ctx["show_settings"]()
        return None

    # -- end -------------------------------------------------------------------
    def cleanup(self) -> None:
        self._closing = True
        for hook, fn in self._hooks:
            try:
                hook.remove(fn)
            except ValueError:
                pass
        try:
            mw.removeEventFilter(self._watcher)
            self._timer.stop()
        except RuntimeError:
            pass
        try:
            mw.setStyleSheet(mw.styleSheet().split(SEPARATOR_MARK)[0])
        except RuntimeError:
            pass
        for dock in list(self._wired.values()):  # give the tools their own title bar back
            try:
                bar = dock.titleBarWidget()
                if bar is not None and bar.objectName() == TITLE_WRAP:
                    original = bar.layout().itemAt(1).widget() if bar.layout().count() > 1 else QWidget()
                    dock.setTitleBarWidget(original)
                    original.show()
                    bar.deleteLater()
            except RuntimeError:
                pass
        if self.rail_bar is not None:
            try:
                mw.removeToolBar(self.rail_bar)
                self.rail_bar.deleteLater()
            except RuntimeError:
                pass
        for dock in (self.today_dock,):
            try:
                dock.setVisible(False)
                mw.removeDockWidget(dock)
                dock.deleteLater()
            except RuntimeError:
                pass
        try:
            self.web.cleanup()
        except Exception:
            pass


def texts() -> Dict[str, str]:
    return {
        "daysUntil": _("days until"), "dayUntil": _("day until"), "today": _("Today"), "level": _("Level"),
        "streak": _("day streak"), "done": _("done"), "of": _("of"), "left": _("left"), "about": _("about"),
        "more": _("more, open plan"), "openPlan": _("Open study plan"), "noPlan": _("No study plan yet"),
        "noPlanHint": _("Create a plan and today's items appear here."), "nothing": _("Nothing planned for today."),
        "allDone": _("Everything for today is done."), "due": _("Due"), "reviews": _("Reviews"),
        "memory": _("Memory"), "next": _("next {} days"), "last": _("last {} days"), "lastYear": _("last year"), "lastDay": _("last 24 hours"),
        "todayLower": _("today"), "remembered": _("remembered"), "unseen": _("still unseen"),
        "challenge": _("Daily challenge"), "claim": _("Claim"), "claimed": _("Done"), "fact": _("Daily fact"),
        "choose": _("Choose what this page shows"), "info": _("What do these numbers mean?"),
        "ankiChecks": _("Anki checks this off."), "study": _("Study"), "examToday": _("Exam today"),
        "showCountdown": _("Countdown"), "showPlan": _("Today's plan"), "showLevel": _("Level and streak"),
        "showChallenge": _("Daily challenge"), "showFact": _("Daily fact"), "showDue": _("Due"),
        "showReviews": _("Reviews"), "showMemory": _("Memory"), "settings": _("All settings"),
        "infoDue": _("Due: reviews that are waiting today or become due on each of the next days. New cards are not counted."),
        "infoReviews": _("Reviews: how many cards you answered per day."),
        "infoMemory": _("Remembered: share of review cards you answered correctly. Still unseen: share of your cards you have never studied."),
        "noData": _("No reviews in this period."), "cards": _("cards"), "xp": _("XP"),
    }


# ── Data, collected in the background ─────────────────────────────────────────
def _plan_part(col, settings) -> Dict[str, Any]:
    from .plan import ankidata, planner, store
    today = ankidata.today(col).isoformat()
    plans = [p for p in store.list_plans() if p.get("status", "active") == "active"]
    running = [p for p in plans if p.get("days") and p.get("exam") and p["exam"] >= today]
    running.sort(key=lambda p: (p["exam"], p["id"]))
    out: Dict[str, Any] = {"hasPlans": bool(plans), "items": [], "done": 0, "total": 0, "mins": 0, "more": 0}
    countdown = None
    if running:
        first = running[0]
        days = (date.fromisoformat(first["exam"]) - date.fromisoformat(today)).days
        countdown = {"days": days, "title": first["title"], "source": "plan", "plan": first["id"]}
    done_items, open_items = [], []
    for plan in running:
        try:
            ev = planner.evaluate(plan, ankidata.stats(col, plan))
        except Exception:  # one broken plan must not hide the others
            traceback.print_exc()
            ev = {}
        for day in plan.get("days", []):
            if day["d"] != today:
                continue
            for it in day["items"]:
                if it.get("kind") in planner.NO_CHECK or it.get("moved"):
                    continue
                result = ev.get(it["id"], {})
                by_anki = bool(result.get("done")) and it["id"] not in plan.get("done", {})
                done = planner.is_done(plan, it, ev)
                row = {"plan": plan["id"], "id": it["id"], "text": it.get("text", ""), "min": it.get("min") or 0,
                       "done": done, "auto": bool(it.get("auto")), "byAnki": by_anki,
                       "kind": it.get("kind"), "note": result.get("text") or "",
                       "planTitle": plan["title"] if len(running) > 1 else ""}
                out["total"] += 1
                if done:
                    out["done"] += 1
                    done_items.append(row)
                else:
                    out["mins"] += row["min"]
                    open_items.append(row)
    limit = max(1, int(settings.get("panel_plan_items", 4) or 4))
    shown_open = open_items[:limit]
    room = limit - len(shown_open)
    shown_done = done_items[-room:] if room > 0 else []
    out["items"] = shown_done + shown_open
    out["more"] = out["total"] - len(out["items"])
    return {"plan": out, "countdown": countdown}


def _pick(value, choices, default):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return default
    return value if value in choices else default


def _stats_part(col, settings) -> Dict[str, Any]:
    from . import statistics_widget
    out: Dict[str, Any] = {}
    due_days = _pick(settings.get("panel_due_days"), DUE_CHOICES, 7)
    today = col.sched.today
    values = [0] * due_days
    for offset, count in col.db.all(
            "SELECT CASE WHEN due < ? THEN 0 ELSE due - ? END AS d, COUNT(*) FROM cards "
            "WHERE queue IN (2, 3) AND due < ? GROUP BY d", today, today, today + due_days):
        if 0 <= offset < due_days:
            values[int(offset)] += count
    values[0] += col.db.scalar("SELECT COUNT(*) FROM cards WHERE queue = 1") or 0
    start = statistics_widget.anki_today()
    out["due"] = {"start": start.isoformat(), "days": due_days, "choices": list(DUE_CHOICES), "values": values, "total": sum(values),
                  "last": (start + timedelta(days=due_days - 1)).strftime("%a" if due_days <= 7 else "%d.%m.")}

    review_days = _pick(settings.get("stats_consistency_days"), REVIEW_CHOICES, 30)
    counts = statistics_widget.get_daily_review_counts(since_days=review_days + 2)
    series = [counts.get((start - timedelta(days=review_days - 1 - i)).isoformat(), 0) for i in range(review_days)]
    out["reviews"] = {"end": start.isoformat(), "days": review_days, "choices": list(REVIEW_CHOICES), "values": series, "total": sum(series)}

    memory_days = _pick(settings.get("stats_time_range"), MEMORY_CHOICES, 7)
    since = int((datetime.now() - timedelta(days=memory_days)).timestamp()) * 1000
    right, total = col.db.first(
        "SELECT SUM(CASE WHEN type = 1 AND ease > 1 THEN 1 ELSE 0 END), SUM(CASE WHEN type = 1 THEN 1 ELSE 0 END) "
        "FROM revlog WHERE id > ? AND ease > 0", since) or (0, 0)
    active, new = col.db.first(
        "SELECT SUM(CASE WHEN queue != -1 THEN 1 ELSE 0 END), SUM(CASE WHEN queue = 0 THEN 1 ELSE 0 END) FROM cards"
    ) or (0, 0)
    out["memory"] = {"days": memory_days, "choices": list(MEMORY_CHOICES),
                     "retention": round(100 * (right or 0) / total) if total else None,
                     "unseen": round(100 * (new or 0) / active) if active else None}
    return out


def collect(col, settings) -> Dict[str, Any]:
    data: Dict[str, Any] = {"countdown": None}
    try:
        data.update(_plan_part(col, settings))
    except Exception:
        traceback.print_exc()
        data["plan"] = {"hasPlans": False, "items": [], "done": 0, "total": 0, "mins": 0, "more": 0}
    try:
        data.update(_stats_part(col, settings))
    except Exception:
        traceback.print_exc()
    return data
