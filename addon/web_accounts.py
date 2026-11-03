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
    keep_youtube_theme_fixed(profile)
    _profiles[folder] = profile
    _copy_saved_login(os.path.join(folder, "SmartStudy_Data", "web_profiles", "website"), profile)
    return profile


# Google refuses most sign-ins inside Anki's sidebars, but a sign-in in the
# Smart Study browser works.  Gemini, NotebookLM and YouTube Music then use
# that same sign-in: these cookies are copied to the account profile.
_SHARED_LOGIN = ("google.com", "youtube.com")


def _shares_login(domain: str) -> bool:
    domain = domain.lstrip(".")
    return any(domain == d or domain.endswith("." + d) for d in _SHARED_LOGIN)


def _copy_saved_login(website_folder: str, target) -> None:
    """Copy the browser's saved Google/YouTube cookies (read from its file,
    as Qt hands them out only once pages load)."""
    import sqlite3
    from PyQt6.QtCore import QDateTime
    from PyQt6.QtNetwork import QNetworkCookie
    path = os.path.join(website_folder, "Cookies")
    if not os.path.exists(path):
        return
    try:
        db = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        try:
            rows = db.execute(
                "SELECT host_key, name, value, path, expires_utc, is_secure, is_httponly"
                " FROM cookies WHERE value != ''").fetchall()
        finally:
            db.close()
    except sqlite3.Error:
        return
    store = target.cookieStore()
    for host, name, value, cookie_path, expires, secure, httponly in rows:
        if not _shares_login(host):
            continue
        cookie = QNetworkCookie(name.encode("latin-1", "replace"), value.encode("latin-1", "replace"))
        if host.startswith("."):
            cookie.setDomain(host)  # without a dot it is host-only (__Host- cookies)
        cookie.setPath(cookie_path or "/")
        cookie.setSecure(bool(secure))
        cookie.setHttpOnly(bool(httponly))
        if expires:
            # Chromium time: microseconds since 1601.
            cookie.setExpirationDate(QDateTime.fromSecsSinceEpoch(
                max(0, expires // 1_000_000 - 11_644_473_600)))
        store.setCookie(cookie, QUrl("https://" + host.lstrip(".")))


def share_login_from(website_profile) -> None:
    """Pass later sign-ins in the browser on to the account profile."""
    def added(cookie):
        if _shares_login(cookie.domain()) and mw.pm.profileFolder() in _profiles:
            target = _profiles[mw.pm.profileFolder()].cookieStore()
            target.setCookie(cookie, QUrl("https://" + cookie.domain().lstrip(".")))
    website_profile.cookieStore().cookieAdded.connect(added)


# YouTube's theme flags in its PREF cookie (f6, hex).  With "device theme" the
# server cannot know the colour scheme, renders light, and the page then loads
# itself a second time (…&themeRefresh=1): seconds lost on every video.
_YT_DEVICE, _YT_DARK, _YT_LIGHT = 0x40000000, 0x400, 0x80000


def _fixed_youtube_pref(value: str) -> Optional[str]:
    """The PREF cookie value with light or dark instead of "device theme",
    or None when it needs no change."""
    fields = value.split("&")
    for i, field in enumerate(fields):
        if field.startswith("f6="):
            try:
                flags = int(field[3:], 16)
            except ValueError:
                return None
            if not flags & _YT_DEVICE:
                return None
            from aqt.theme import theme_manager
            flags &= ~(_YT_DEVICE | _YT_DARK | _YT_LIGHT)
            flags |= _YT_DARK if theme_manager.night_mode else _YT_LIGHT
            fields[i] = "f6=%x" % flags
            return "&".join(fields)
    return None


def keep_youtube_theme_fixed(profile) -> None:
    """Replace YouTube's "device theme" by light or dark as in Anki."""
    import sqlite3
    from PyQt6.QtCore import QDateTime
    from PyQt6.QtNetwork import QNetworkCookie
    store = profile.cookieStore()

    def put(cookie: "QNetworkCookie", value: str) -> None:
        cookie.setValue(value.encode("latin-1"))
        store.setCookie(cookie, QUrl("https://www.youtube.com"))

    # Qt hands out saved cookies only once pages load, too late for the
    # first one, so read the saved cookie straight from the profile.
    path = os.path.join(profile.persistentStoragePath(), "Cookies")
    try:
        db = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        try:
            row = db.execute(
                "SELECT value, expires_utc FROM cookies WHERE host_key = '.youtube.com'"
                " AND name = 'PREF' AND path = '/'").fetchone()
        finally:
            db.close()
    except sqlite3.Error:
        row = None
    if row and _fixed_youtube_pref(row[0]):
        cookie = QNetworkCookie(b"PREF")
        cookie.setDomain(".youtube.com")
        cookie.setPath("/")
        cookie.setSecure(True)
        # Chromium time: microseconds since 1601.
        cookie.setExpirationDate(QDateTime.fromSecsSinceEpoch(
            max(0, row[1] // 1_000_000 - 11_644_473_600)))
        put(cookie, _fixed_youtube_pref(row[0]))

    def added(cookie):
        if bytes(cookie.name()) == b"PREF" and cookie.domain().endswith("youtube.com"):
            value = _fixed_youtube_pref(bytes(cookie.value()).decode("latin-1"))
            if value:
                put(QNetworkCookie(cookie), value)

    store.cookieAdded.connect(added)


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
            # Music keeps playing when the sidebar closes.
            from .website_sidebar import _keep_audio_playing
            _keep_audio_playing(self.view)
            # ChatGPT, Gemini, YouTube Music … keep their state on their
            # servers: after 10 min hidden (and silent) the page is unloaded.
            from . import web_sleep
            web_sleep.watch(self.view, discard_after=600)
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
