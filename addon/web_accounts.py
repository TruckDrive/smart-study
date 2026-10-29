# -*- coding: utf-8 -*-
"""Websites with your own account, inside a Smart Study sidebar.

Used by the AI assistant (ChatGPT, Claude, Gemini instead of an API key) and
the music player (YouTube Music, Spotify).  Each Anki profile gets one
persistent browser profile for this, so a sign-in survives restarts and stays
separate from other Anki profiles.  Nothing is sent anywhere by Smart Study;
the page talks to the website directly, as in a normal browser.
"""
from __future__ import annotations

import os
import re
from typing import Callable, List, Optional, Tuple, Union

from aqt import mw
from aqt.qt import (QHBoxLayout, QLabel, QPushButton, QSizePolicy,
                    QStackedWidget, QUrl, QVBoxLayout, QWidget, Qt, QDesktopServices)
from aqt.utils import tooltip

try:
    from PyQt6.QtWebEngineCore import (QWebEnginePage, QWebEngineProfile,
                                       QWebEngineSettings)
    from PyQt6.QtWebEngineWidgets import QWebEngineView
except ImportError:  # pragma: no cover
    QWebEngineView = None  # type: ignore

from .integrations.strings import tr

_profiles: dict = {}


def account_profile() -> "QWebEngineProfile":
    """The persistent browser profile for signed-in websites of this Anki profile."""
    folder = mw.pm.profileFolder()
    if folder in _profiles:
        return _profiles[folder]
    path = os.path.join(folder, "SmartStudy_Data", "web_profiles", "accounts")
    os.makedirs(path, exist_ok=True)
    profile = QWebEngineProfile("SmartStudy_Accounts_" + re.sub(r"\W", "_", mw.pm.name or "default"), mw)
    profile.setPersistentStoragePath(path)
    profile.setCachePath(os.path.join(path, "cache"))
    profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
    profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
    # Some sites refuse browsers that announce "QtWebEngine"; it is Chromium.
    profile.setHttpUserAgent(re.sub(r"\s*QtWebEngine/\S+", "", profile.httpUserAgent()))
    settings = profile.settings()
    attr = QWebEngineSettings.WebAttribute
    settings.setAttribute(attr.JavascriptEnabled, True)
    settings.setAttribute(attr.LocalStorageEnabled, True)
    settings.setAttribute(attr.FullScreenSupportEnabled, True)
    settings.setAttribute(attr.PlaybackRequiresUserGesture, False)
    _profiles[folder] = profile
    return profile


def forget_profiles() -> None:
    """Called when an Anki profile closes; pages must be gone before this."""
    for profile in _profiles.values():
        profile.deleteLater()
    _profiles.clear()


class _Page(QWebEnginePage):
    """Opens pop-up windows (e.g. sign-in) in the same view."""

    def createWindow(self, _type):  # sign-in pop-ups (Google, Apple, …)
        return self


class AccountSitesPanel(QWidget):
    """A row of tab buttons above a stack.  A tab shows either an own widget or
    a website; all websites share one web view."""

    def __init__(self, tabs: List[Tuple[str, str, Union[str, QWidget]]], *,
                 hint: str = "", remember: Optional[Callable[[str], None]] = None,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.tabs = tabs              # (key, label, url or widget)
        self.remember = remember
        self.view: Optional[QWebEngineView] = None
        self.buttons: dict = {}
        self.current = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        bar = QWidget()
        bar.setObjectName("smartstudyAccountBar")
        row = QHBoxLayout(bar)
        row.setContentsMargins(8, 6, 8, 6)
        row.setSpacing(4)
        for key, label, _target in tabs:
            button = QPushButton(label)
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda _=False, k=key: self.show_site(k))
            row.addWidget(button)
            self.buttons[key] = button
        row.addStretch(1)
        self.external = QPushButton("↗")
        self.external.setToolTip(tr("Open in browser"))
        self.external.clicked.connect(self._open_external)
        row.addWidget(self.external)
        layout.addWidget(bar)

        self.hint = QLabel(hint)
        self.hint.setWordWrap(True)
        self.hint.setContentsMargins(10, 4, 10, 6)
        from aqt.theme import theme_manager
        self.hint.setStyleSheet("font-size: 11px; color: %s;" % ("#a1a1a6" if theme_manager.night_mode else "#6e6e73"))
        self.hint.setVisible(False)
        layout.addWidget(self.hint)

        self.stack = QStackedWidget()
        self.stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        for _key, _label, target in tabs:
            if isinstance(target, QWidget):
                self.stack.addWidget(target)
        layout.addWidget(self.stack, 1)
        self._style_bar()

    def _style_bar(self) -> None:
        from aqt.theme import theme_manager
        line = "#3a3a3c" if theme_manager.night_mode else "#d7d7db"
        on = "#2f6fd6"
        self.setStyleSheet(
            f"#smartstudyAccountBar {{ border-bottom: 1px solid {line}; }}"
            f"#smartstudyAccountBar QPushButton {{ padding: 3px 9px; border-radius: 6px; border: 1px solid {line}; }}"
            f"#smartstudyAccountBar QPushButton:checked {{ background: {on}; color: white; border-color: {on}; }}"
        )

    def _ensure_view(self) -> QWebEngineView:
        if self.view is None:
            self.view = QWebEngineView()
            self.view.setPage(_Page(account_profile(), self.view))
            self.stack.addWidget(self.view)
        return self.view

    def show_site(self, key: str) -> None:
        target = next((t for k, _l, t in self.tabs if k == key), None)
        if target is None:
            key, _label, target = self.tabs[0]
        for k, button in self.buttons.items():
            button.setChecked(k == key)
        self.current = key
        if isinstance(target, QWidget):
            self.stack.setCurrentWidget(target)
            self.hint.setVisible(False)
            self.external.setVisible(False)
        else:
            view = self._ensure_view()
            if view.property("site") != key:
                view.setProperty("site", key)
                view.setUrl(QUrl(target))
            self.stack.setCurrentWidget(view)
            self.hint.setVisible(bool(self.hint.text()))
            self.external.setVisible(True)
        if self.remember:
            self.remember(key)

    def _open_external(self) -> None:
        if self.view is not None:
            QDesktopServices.openUrl(self.view.url())

    def cleanup(self) -> None:
        if self.view is not None:
            self.view.setUrl(QUrl("about:blank"))
            page = self.view.page()
            self.view.deleteLater()
            page.deleteLater()
            self.view = None
