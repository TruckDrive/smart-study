# -*- coding: utf-8 -*-
"""Pages visited in the Smart Study browser, for suggestions in the address field,
and the icons of sites, so tabs restored after a restart show them at once.

Everything stays on this computer, in the Anki profile (SmartStudy_Data/):
browser_history.json and favicons/<host>.png. "Clear browsing history" in the
browser's options removes both. No Qt in the ranking, so it can be tested alone.
"""

from __future__ import annotations

import json
import os
import re
import time
from typing import Dict, List, Optional
from urllib.parse import urlsplit

MAX_ENTRIES = 800
MAX_ICONS = 300
_entries: Optional[Dict[str, dict]] = None  # {url: {"t": title, "n": visits, "at": last visit}}
_folder: Optional[str] = None
_dirty = False


def set_folder(folder: Optional[str]) -> None:
    """The profile's data folder; a different folder (another profile) starts fresh."""
    global _folder, _entries, _dirty
    if folder != _folder:
        save()
        _folder, _entries, _dirty = folder, None, False


def _path() -> Optional[str]:
    return os.path.join(_folder, "browser_history.json") if _folder else None


def _load() -> Dict[str, dict]:
    global _entries
    if _entries is None:
        _entries = {}
        path = _path()
        try:
            if path and os.path.isfile(path):
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    _entries = {u: e for u, e in data.items() if isinstance(u, str) and isinstance(e, dict)}
        except (OSError, ValueError):
            _entries = {}
    return _entries


def save() -> None:
    global _dirty
    path = _path()
    if not _dirty or not path or _entries is None:
        return
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(_entries, f, ensure_ascii=False)
        os.replace(tmp, path)
        _dirty = False
    except OSError as e:
        print(f"Smart Study browser: history not saved: {e}")


def _wanted(url: str) -> bool:
    return url.startswith(("http://", "https://")) and len(url) <= 2000


def add(url: str, title: str = "", now: Optional[float] = None) -> None:
    """Counts a visit. Only web pages; logins, tokens in the address and the like are not treated specially,
    which is why clearing the history must stay one click away."""
    global _dirty
    if not _wanted(url):
        return
    entries = _load()
    e = entries.setdefault(url, {"t": "", "n": 0, "at": 0})
    e["n"] = int(e.get("n", 0)) + 1
    e["at"] = now if now is not None else time.time()
    if title:
        e["t"] = title[:200]
    if len(entries) > MAX_ENTRIES:  # forget what was visited least recently
        for old in sorted(entries, key=lambda u: entries[u].get("at", 0))[:len(entries) - MAX_ENTRIES + 50]:
            del entries[old]
    _dirty = True


def set_title(url: str, title: str) -> None:
    global _dirty
    e = _load().get(url)
    if e is not None and title and e.get("t") != title[:200]:
        e["t"] = title[:200]
        _dirty = True


def clear() -> None:
    global _entries, _dirty
    _entries, _dirty = {}, True
    save()
    folder = _icon_folder()
    try:
        if folder and os.path.isdir(folder):
            for name in os.listdir(folder):
                if name.endswith(".png"):
                    os.remove(os.path.join(folder, name))
    except OSError as e:
        print(f"Smart Study browser: icons not removed: {e}")


def short(url: str) -> str:
    """The address without https:// and www., as it is typed and shown."""
    s = re.sub(r"^https?://", "", url)
    s = s[4:] if s.startswith("www.") else s
    return s[:-1] if s.endswith("/") and s.count("/") == 1 else s


def suggest(text: str, extra: Optional[List[dict]] = None, limit: int = 7, now: Optional[float] = None,
            history: bool = True) -> List[dict]:
    """Pages matching what was typed, best first: [{"url", "title"}].
    extra: favourites and open tabs [{"url", "title"}], which count like often-visited pages.
    A match at the start of the address beats one inside it, which beats one in the title;
    among equals the page visited more often and more recently wins."""
    words = [w for w in re.sub(r"^https?://(www\.)?", "", text.strip().lower()).split() if w]
    if not words:
        return []
    now = now if now is not None else time.time()
    pool: Dict[str, dict] = {}
    for url, e in (_load() if history else {}).items():  # history off: only favourites and open tabs
        pool[url] = {"url": url, "title": e.get("t", ""), "n": int(e.get("n", 1)), "at": float(e.get("at", 0))}
    for x in extra or []:
        url = x.get("url") or ""
        if not _wanted(url):
            continue
        p = pool.setdefault(url, {"url": url, "title": "", "n": 0, "at": 0.0})
        p["n"] += 5
        p["title"] = p["title"] or x.get("title", "")
    scored = []
    for p in pool.values():
        addr, title = short(p["url"]).lower(), p["title"].lower()
        if not all(w in addr or w in title for w in words):
            continue
        first = words[0]
        if addr.startswith(first):
            rank = 3.0
        elif any(part.startswith(first) for part in re.split(r"[./_?=&-]+", addr)):
            rank = 2.0
        elif first in addr:
            rank = 1.5
        else:
            rank = 1.0
        age_days = max(0.0, (now - p["at"]) / 86400) if p["at"] else 365.0
        weight = min(p["n"], 30) / 30 + 1 / (1 + age_days / 7)  # 0 … 2
        depth = addr.count("/")  # the site itself before its sub-pages
        scored.append((-(rank * 10 + weight - min(depth, 5) * 0.2), len(addr), p))
    scored.sort(key=lambda x: (x[0], x[1]))
    return [{"url": p["url"], "title": p["title"]} for _, _, p in scored[:limit]]


# ── Site icons ────────────────────────────────────────────────────────────

def _icon_folder() -> Optional[str]:
    return os.path.join(_folder, "favicons") if _folder else None


def _host(url: str) -> str:
    try:
        host = (urlsplit(url).hostname or "").lower()
    except ValueError:
        return ""
    return host if re.fullmatch(r"[a-z0-9.-]{1,120}", host) else ""  # only what is safe as a file name


def icon_path(url: str) -> Optional[str]:
    folder, host = _icon_folder(), _host(url)
    return os.path.join(folder, host + ".png") if folder and host else None


def save_icon(url: str, icon) -> None:
    """Keeps a site's icon (a QIcon) as a small PNG, once a day at most."""
    path = icon_path(url)
    if not path or icon is None or icon.isNull():
        return
    try:
        if os.path.isfile(path) and time.time() - os.path.getmtime(path) < 86400:
            return
        os.makedirs(os.path.dirname(path), exist_ok=True)
        names = os.listdir(os.path.dirname(path))
        if len(names) > MAX_ICONS:
            full = [os.path.join(os.path.dirname(path), n) for n in names]
            for old in sorted(full, key=os.path.getmtime)[:len(full) - MAX_ICONS + 30]:
                os.remove(old)
        pixmap = icon.pixmap(32, 32)
        if not pixmap.isNull():
            pixmap.save(path, "PNG")
    except Exception as e:
        print(f"Smart Study browser: icon not kept: {e}")


def load_icon(url: str):
    """The kept icon of the address's site as a QIcon, or None."""
    path = icon_path(url)
    if not path or not os.path.isfile(path):
        return None
    try:
        from aqt.qt import QIcon
        icon = QIcon(path)
        return None if icon.isNull() else icon
    except Exception:
        return None
