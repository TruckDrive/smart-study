# -*- coding: utf-8 -*-
"""Ad and tracker blocking for the Smart Study browser.

Requests to known ad, tracker and malware servers are refused before they
leave the computer.  The server list is Steven Black's unified hosts file
(MIT licence), downloaded when the browser first opens and refreshed weekly;
it is kept in the profile's SmartStudy_Data folder.  Like any server list it
cannot remove ads that a site serves from its own servers (e.g. YouTube's
video ads).
"""
from __future__ import annotations

import os
import time
import urllib.request
from typing import Iterable, Optional, Set

LIST_URL = "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts"
MAX_AGE = 7 * 24 * 3600
_IGNORED = {"localhost", "localhost.localdomain", "local", "broadcasthost",
            "ip6-localhost", "ip6-loopback", "0.0.0.0"}


def parse_hosts(lines: Iterable[str]) -> Set[str]:
    """Server names from a hosts file ("0.0.0.0 ads.example.com")."""
    hosts = set()
    for line in lines:
        parts = line.split("#", 1)[0].split()
        if len(parts) >= 2 and parts[0] in ("0.0.0.0", "127.0.0.1"):
            hosts.update(h.lower() for h in parts[1:] if h.lower() not in _IGNORED)
    return hosts


def is_blocked(host: str, blocked: Set[str]) -> bool:
    """True for a listed server or any server below it (x.ads.example.com)."""
    host = host.lower().rstrip(".")
    while host:
        if host in blocked:
            return True
        host = host.partition(".")[2]
    return False


def load_list(path: str) -> Set[str]:
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return parse_hosts(f)
    except OSError:
        return set()


def needs_refresh(path: str) -> bool:
    try:
        return time.time() - os.path.getmtime(path) > MAX_AGE
    except OSError:
        return True


def download_list(path: str) -> Set[str]:
    request = urllib.request.Request(LIST_URL, headers={"User-Agent": "Smart Study"})
    with urllib.request.urlopen(request, timeout=60) as response:
        text = response.read().decode("utf-8", "replace")
    hosts = parse_hosts(text.splitlines())
    if len(hosts) < 1000:
        raise ValueError("ad-block list looks incomplete")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)
    return hosts


try:
    from PyQt6.QtWebEngineCore import (QWebEngineUrlRequestInfo,
                                       QWebEngineUrlRequestInterceptor)

    class AdBlocker(QWebEngineUrlRequestInterceptor):
        """Runs on Chromium's IO thread; only reads the current set."""

        def __init__(self, parent=None):
            super().__init__(parent)
            self.enabled = True
            self.blocked: Set[str] = set()

        def interceptRequest(self, info):
            if not self.enabled or not self.blocked:
                return
            # Never block a page the user opens on purpose.
            if info.resourceType() == QWebEngineUrlRequestInfo.ResourceType.ResourceTypeMainFrame:
                return
            if is_blocked(info.requestUrl().host(), self.blocked):
                info.block(True)

        def start(self, folder: str) -> None:
            """Use the saved list now and fetch a fresh one in the background."""
            from aqt import mw
            path = os.path.join(folder, "adblock_hosts.txt")
            self.blocked = load_list(path)
            if not needs_refresh(path):
                return

            def done(future):
                try:
                    self.blocked = future.result()
                except Exception as e:
                    print(f"Smart Study browser: ad-block list not updated: {e}")
            mw.taskman.run_in_background(lambda: download_list(path), done)

except ImportError:  # pragma: no cover
    AdBlocker = None  # type: ignore
