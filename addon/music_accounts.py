# -*- coding: utf-8 -*-
"""Music from streaming services: YouTube Music in a sidebar, Spotify outside.

YouTube Music plays inside Anki without signing in (Google refuses sign-ins
in embedded browsers).  Spotify's web player needs the Widevine
copy protection, which Anki's built-in browser does not have, so the Spotify
tab opens the Spotify app (or open.spotify.com in the normal browser) instead.
The sidebar keeps playing when it is hidden; closing the Anki profile stops it.
"""
from __future__ import annotations

from typing import Optional

from aqt import mw
from aqt.qt import (QDesktopServices, QDockWidget, QLabel, QPushButton, Qt,
                    QUrl, QVBoxLayout, QWidget)

from .integrations.strings import tr
from .web_accounts import AccountSitesPanel

DOCK_NAME = "SmartStudyMusicAccountsDock"
_dock: Optional[QDockWidget] = None
_panel: Optional[AccountSitesPanel] = None


def _remember(key: str) -> None:
    if mw.col:
        mw.col.set_config("smartstudy_music_account_site", key)


def _spotify_page() -> QWidget:
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(18, 18, 18, 18)
    layout.setSpacing(10)
    text = QLabel(tr("Spotify only plays in its own app or a normal browser: its web player needs a copy protection (Widevine) that Anki's built-in browser does not include. Start your music there – it keeps playing while you study."))
    text.setWordWrap(True)
    layout.addWidget(text)
    app = QPushButton(tr("Open the Spotify app"))
    app.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("spotify:")))
    web = QPushButton(tr("Open Spotify in the browser"))
    web.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://open.spotify.com/")))
    layout.addWidget(app)
    layout.addWidget(web)
    layout.addStretch(1)
    return page


def toggle_music_accounts() -> None:
    """Shows or hides the music sidebar (created on first use)."""
    global _dock, _panel
    if _dock is None:
        _panel = AccountSitesPanel(
            [("ytmusic", "YouTube Music", "https://music.youtube.com/"),
             ("spotify", "Spotify", _spotify_page())],
            hint=tr("YouTube Music plays here without signing in. Google does not allow signing in inside apps like Anki – for your own playlists, open YouTube Music in your browser with ↗."),
            remember=_remember,
        )
        _dock = QDockWidget(tr("Music"), mw)
        _dock.setObjectName(DOCK_NAME)
        _dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        _dock.setTitleBarWidget(QWidget())
        _dock.setMinimumWidth(360)
        _dock.setWidget(_panel)
        mw.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, _dock)
        site = mw.col.get_config("smartstudy_music_account_site", "ytmusic") if mw.col else "ytmusic"
        _panel.show_site(site)
        _dock.show()
        return
    _dock.setVisible(not _dock.isVisible())


def cleanup_music_accounts() -> None:
    global _dock, _panel
    if _panel is not None:
        _panel.cleanup()
        _panel = None
    if _dock is not None:
        mw.removeDockWidget(_dock)
        _dock.deleteLater()
        _dock = None
