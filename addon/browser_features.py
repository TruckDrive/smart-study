# -*- coding: utf-8 -*-
"""Extras of the Smart Study browser.

Video control from anywhere in Anki (keyboard shortcuts and controller),
picture in picture, study-plan videos that resume and check themselves off,
cards from pages and videos, tab groups, a focus mode and SponsorBlock.

Settings live in the profile's SmartStudy_Data/website_state.json under
"browser" and are edited on the "Browser" page of the Smart Study settings.
"""
from __future__ import annotations

import hashlib
import html
import json
import os
import re
import time
import urllib.parse
import urllib.request
from typing import Callable, Dict, List, Optional

from aqt import mw
from aqt.qt import (QApplication, QFrame, QHBoxLayout, QInputDialog, QKeySequence,
                    QLabel, QMenu, QPushButton, QShortcut, QSizeGrip, QTimer,
                    QUrl, QVBoxLayout, QWidget, Qt)
from aqt.utils import tooltip

try:
    from PyQt6.QtWebEngineCore import QWebEngineContextMenuRequest, QWebEngineScript
except ImportError:  # pragma: no cover
    QWebEngineContextMenuRequest = QWebEngineScript = None  # type: ignore

try:
    from .locales import _
except ImportError:  # pragma: no cover
    def _(text):  # type: ignore
        return text


# ── Settings ──────────────────────────────────────────────────────────────

# key, label, default, where it works ("app": everywhere in Anki, also while
# reviewing; "browser": while the browser has the focus)
SHORTCUT_ACTIONS = [
    ("play_pause", "Video: play / pause", "Ctrl+Alt+P", "app"),
    ("back", "Video: 10 s back", "Ctrl+Alt+Left", "app"),
    ("forward", "Video: 10 s forward", "Ctrl+Alt+Right", "app"),
    ("slower", "Video: slower", "Ctrl+Alt+Down", "app"),
    ("faster", "Video: faster", "Ctrl+Alt+Up", "app"),
    ("pip", "Video: picture in picture", "Ctrl+Alt+I", "app"),
    ("video_card", "Card at this point of the video", "Ctrl+Alt+N", "app"),
    ("selection_card", "Card from selected text", "Ctrl+Alt+K", "browser"),
    ("new_tab", "New tab", "Ctrl+T", "browser"),
    ("close_tab", "Close tab", "Ctrl+W", "browser"),
    ("next_tab", "Next tab", "Ctrl+Tab", "browser"),
    ("prev_tab", "Previous tab", "Ctrl+Shift+Tab", "browser"),
    ("address_bar", "Address bar", "Ctrl+L", "browser"),
]
FOCUS_YOUTUBE = [
    ("shorts", "YouTube Shorts"),
    ("home", "Recommendations on the YouTube start page"),
    ("related", "Suggestions next to and after a video"),
    ("comments", "YouTube comments"),
]
FOCUS_SITES = [
    ("instagram.com", "Instagram"), ("tiktok.com", "TikTok"), ("facebook.com", "Facebook"),
    ("x.com", "X / Twitter"), ("reddit.com", "Reddit"), ("netflix.com", "Netflix"),
    ("twitch.tv", "Twitch"),
]
SPONSOR_CATEGORIES = [
    ("sponsor", "Sponsors"), ("selfpromo", "Self-promotion"),
    ("interaction", "Reminders to like or subscribe"), ("intro", "Intros"),
    ("outro", "Outros and end cards"), ("music_offtopic", "Non-music parts of music videos"),
]
DEFAULTS = {
    # Study-plan videos and PDFs: True = system browser / PDF app, False = Smart Study browser tab.
    "plan_external": True,
    "resume_videos": True,
    "done_percent": 90,
    "restore_tabs": True,
    "shortcuts": {key: default for key, _l, default, _w in SHORTCUT_ACTIONS},
    "focus_mode": "off",            # off | always | pomodoro
    "focus_youtube": ["shorts", "home"],
    "focus_sites": ["instagram.com", "tiktok.com"],
    "focus_custom": "",
    "sponsorblock": True,
    "sponsor_categories": ["sponsor", "selfpromo", "interaction", "music_offtopic"],
}


def _ws():
    from . import website_sidebar
    return website_sidebar


def load_settings() -> Dict:
    raw = _ws()._load_website_state().get("browser")
    raw = raw if isinstance(raw, dict) else {}
    s = json.loads(json.dumps(DEFAULTS))
    for key, default in DEFAULTS.items():
        if key in raw and type(raw[key]) is type(default):
            s[key] = raw[key]
    shortcuts = dict(DEFAULTS["shortcuts"])
    for key, value in (raw.get("shortcuts") or {}).items():
        if key in shortcuts and isinstance(value, str):
            shortcuts[key] = value
    s["shortcuts"] = shortcuts
    if s["focus_mode"] not in ("off", "always", "pomodoro"):
        s["focus_mode"] = "off"
    s["done_percent"] = min(100, max(50, int(s["done_percent"])))
    return s


def save_settings(values: Dict) -> None:
    clean = {}
    for key, default in DEFAULTS.items():
        value = values.get(key, default)
        clean[key] = value if type(value) is type(default) else default
    clean["shortcuts"] = {k: str(v) for k, v in (values.get("shortcuts") or {}).items()
                          if k in DEFAULTS["shortcuts"]}
    clean["focus_custom"] = str(clean["focus_custom"])[:4000]
    ws = _ws()
    state = ws._load_website_state()
    state["browser"] = clean
    ws._save_website_state(state)
    apply_settings()


def settings_payload() -> Dict:
    """For the settings page."""
    return {
        "values": load_settings(),
        "shortcuts": [{"key": k, "label": label, "default": d, "where": w}
                      for k, label, d, w in SHORTCUT_ACTIONS],
        "focusYoutube": [{"key": k, "label": label} for k, label in FOCUS_YOUTUBE],
        "focusSites": [{"key": k, "label": label} for k, label in FOCUS_SITES],
        "sponsorCategories": [{"key": k, "label": label} for k, label in SPONSOR_CATEGORIES],
    }


def apply_settings() -> None:
    """After a change: shortcuts, focus mode."""
    apply_shortcuts()
    _focus_changed(force=True)


# ── Shortcuts ─────────────────────────────────────────────────────────────

_shortcuts: List = []


def _actions() -> Dict[str, Callable[[], None]]:
    ws = _ws()
    return {
        "play_pause": lambda: video_command("play_pause"),
        "back": lambda: video_command("seek", -10),
        "forward": lambda: video_command("seek", 10),
        "slower": lambda: video_command("rate", -1),
        "faster": lambda: video_command("rate", 1),
        "pip": toggle_pip,
        "video_card": video_card,
        "selection_card": lambda: card_from_selection(ws.sidebar_webview),
        "new_tab": lambda: ws.new_tab(ws._home_url()),
        "close_tab": lambda: ws.tab_bar is not None and ws.close_tab(ws.tab_bar.currentIndex()),
        "next_tab": lambda: ws._step_tab(1),
        "prev_tab": lambda: ws._step_tab(-1),
        "address_bar": ws.focus_address_bar,
    }


def run_action(key: str) -> None:
    """For the controller (Contanki) and other callers."""
    action = _actions().get(key)
    if action:
        action()


def apply_shortcuts() -> None:
    for shortcut in _shortcuts:
        try:
            shortcut.setEnabled(False)
            shortcut.setParent(None)
            shortcut.deleteLater()
        except RuntimeError:
            pass
    _shortcuts.clear()
    if mw is None:
        return
    keys = load_settings()["shortcuts"]
    actions = _actions()
    container = _ws().browser_container
    for key, _label, _default, where in SHORTCUT_ACTIONS:
        sequence = keys.get(key, "")
        if not sequence:
            continue
        parent = mw if where == "app" else container
        if parent is None:
            continue
        shortcut = QShortcut(QKeySequence.fromString(sequence, QKeySequence.SequenceFormat.PortableText), parent)
        shortcut.setContext(Qt.ShortcutContext.WindowShortcut if where == "app"
                            else Qt.ShortcutContext.WidgetWithChildrenShortcut)
        shortcut.activated.connect(actions[key])
        _shortcuts.append(shortcut)


# ── Finding and controlling the video ─────────────────────────────────────

# The largest video of a document that has data.
_PICK = ("function(){var best=null,area=-1;document.querySelectorAll('video').forEach(function(v){"
         "var r=v.getBoundingClientRect(),a=r.width*r.height;if(v.readyState>0&&a>area){best=v;area=a;}});"
         "return best;}")
_AREA_JS = "(function(){var v=(%s)();if(!v)return 0;var r=v.getBoundingClientRect();return Math.max(1,r.width*r.height);})()" % _PICK
_APP_WORLD = 1


def _world():
    return QWebEngineScript.ScriptWorldId.ApplicationWorld if QWebEngineScript else 0


def _frames(page) -> list:
    """All frames of a page (Qt 6.8+); [None] = only the main document."""
    try:
        root = page.mainFrame()
    except AttributeError:
        return [None]
    frames, queue = [], [root]
    while queue:
        frame = queue.pop(0)
        if frame.isValid():
            frames.append(frame)
            queue.extend(frame.children())
    return frames or [None]


def _run(page, frame, script: str, callback=None) -> None:
    if frame is None:
        if callback: page.runJavaScript(script, _world(), callback)
        else: page.runJavaScript(script, _world())
    else:
        if callback: frame.runJavaScript(script, _APP_WORLD, callback)
        else: frame.runJavaScript(script, _APP_WORLD)


def _with_video(view, body: str, callback: Callable) -> None:
    """Run `body` (JS with `v` = the video) in the frame that has the largest
    video; callback(result) or callback(None) when there is none."""
    page = view.page()
    frames = _frames(page)
    areas: Dict[int, float] = {}

    def measured(index, area):
        areas[index] = area or 0
        if len(areas) < len(frames):
            return
        best = max(areas, key=lambda i: areas[i])
        if not areas[best]:
            callback(None)
            return
        script = "(function(){var v=(%s)();if(!v)return null;%s})()" % (_PICK, body)
        _run(page, frames[best], script, callback)

    for index, frame in enumerate(frames):
        _run(page, frame, _AREA_JS, lambda area, i=index: measured(i, area))


def _video_view():
    """The browser tab with the video to control: picture in picture first,
    then a tab that plays sound, then the current tab."""
    if _pip is not None:
        return _pip.view
    ws = _ws()
    views = [v for v in ws.all_tab_views() if v is not None]
    for view in views:
        try:
            if view.page().recentlyAudible():
                return view
        except RuntimeError:
            pass
    return ws.sidebar_webview


def _clock(seconds: float) -> str:
    seconds = int(seconds or 0)
    h, rest = divmod(seconds, 3600)
    return "%d:%02d:%02d" % (h, rest // 60, rest % 60) if h else "%d:%02d" % (rest // 60, rest % 60)


_RATES = [0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 2.5, 3]


def video_command(kind: str, amount: float = 0) -> None:
    view = _video_view()
    if view is None:
        tooltip(_("No video in the Smart Study browser"))
        return
    if kind == "play_pause":
        body = "if(v.paused){v.play();return 'play';}v.pause();return 'pause';"
    elif kind == "seek":
        body = ("v.currentTime=Math.max(0,Math.min(isFinite(v.duration)?v.duration-0.5:1e9,v.currentTime+%d));"
                "return v.currentTime;" % amount)
    else:
        body = ("var r=%s,c=v.playbackRate,i=0;while(i<r.length-1&&r[i]<c-0.01)i++;"
                "i=Math.max(0,Math.min(r.length-1,i+(%d)));v.playbackRate=r[i];return r[i];"
                % (json.dumps(_RATES), 1 if amount > 0 else -1))

    def done(result):
        if result is None:
            tooltip(_("No video in the Smart Study browser"))
        elif kind == "play_pause":
            tooltip("▶" if result == "play" else "⏸", period=700)
        elif kind == "seek":
            tooltip(("−10 s" if amount < 0 else "+10 s") + "  ·  " + _clock(result), period=900)
        else:
            tooltip(("%g×" % result).replace(".", ","), period=900)
    _with_video(view, body, done)


# ── Picture in picture ────────────────────────────────────────────────────

_PIP_CSS = (".ss-pip-video{position:fixed!important;inset:0!important;width:100vw!important;"
            "height:100vh!important;max-width:none!important;max-height:none!important;"
            "z-index:2147483647!important;background:#000!important;margin:0!important;}"
            "video.ss-pip-video{object-fit:contain!important;}"
            "html.ss-pip,html.ss-pip body{overflow:hidden!important;}")
_PIP_ON = ("var s=document.getElementById('ss-pip-style');if(!s){s=document.createElement('style');"
           "s.id='ss-pip-style';s.textContent=%s;document.documentElement.appendChild(s);}"
           "document.documentElement.classList.add('ss-pip');var p=document.getElementById('movie_player');"
           "(p&&p.contains(v)?p:v).classList.add('ss-pip-video');"
           "setTimeout(function(){window.dispatchEvent(new Event('resize'));},50);return true;") % json.dumps(_PIP_CSS)
# For a video inside an iframe: the iframe fills the page as well.
_PIP_FRAME_ON = ("(function(){var best=null,area=0;document.querySelectorAll('iframe').forEach(function(f){"
                 "var r=f.getBoundingClientRect();if(r.width*r.height>area){best=f;area=r.width*r.height;}});"
                 "if(!best)return;var v=best;" + _PIP_ON + "})()")
_PIP_OFF = ("(function(){document.documentElement.classList.remove('ss-pip');"
            "document.querySelectorAll('.ss-pip-video').forEach(function(e){e.classList.remove('ss-pip-video');});"
            "var s=document.getElementById('ss-pip-style');if(s)s.remove();"
            "setTimeout(function(){window.dispatchEvent(new Event('resize'));},50);})()")


class _PipWindow(QFrame):
    """A small window over Anki (also over the reviewer) with one browser tab
    whose video fills it.  Drag it by its bar, resize it at the corner."""

    def __init__(self, view):
        super().__init__(mw)
        self.view = view
        self.setObjectName("smartstudyPip")
        self.setStyleSheet("#smartstudyPip{background:#000;border:1px solid rgba(255,255,255,0.25);border-radius:8px;}"
                           "#smartstudyPip QLabel{color:#ddd;font-size:11px;}"
                           "#smartstudyPip QPushButton{background:transparent;color:#ddd;border:none;padding:0 6px;font-size:14px;}"
                           "#smartstudyPip QPushButton:hover{color:#fff;}")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(0)
        self.bar = QWidget(self)
        bar_layout = QHBoxLayout(self.bar)
        bar_layout.setContentsMargins(8, 2, 2, 2)
        self.title = QLabel(view.title() or _("Video"))
        self.title.setMinimumWidth(0)
        from aqt.qt import QSizePolicy
        self.title.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        bar_layout.addWidget(self.title, 1)
        back = QPushButton("⤢")
        back.setToolTip(_("Back to the browser"))
        back.clicked.connect(lambda: close_pip(show_browser=True))
        close = QPushButton("×")
        close.setToolTip(_("Close picture in picture"))
        close.clicked.connect(lambda: close_pip())
        bar_layout.addWidget(back)
        bar_layout.addWidget(close)
        layout.addWidget(self.bar)
        layout.addWidget(view, 1)
        view.show()  # the browser's stack hid it when it was taken out
        grip_row = QHBoxLayout()
        grip_row.setContentsMargins(0, 0, 0, 0)
        grip_row.addStretch(1)
        grip_row.addWidget(QSizeGrip(self))
        layout.addLayout(grip_row)
        self.setMinimumSize(240, 160)
        self.resize(480, 300)
        self.move(max(0, mw.width() - self.width() - 24), max(0, mw.height() - self.height() - 48))
        self._drag = None
        self.bar.installEventFilter(self)
        self.show()
        self.raise_()

    def eventFilter(self, obj, event):
        kind = event.type()
        if kind == event.Type.MouseButtonPress:
            self._drag = event.globalPosition().toPoint() - self.pos()
            return True
        if kind == event.Type.MouseMove and self._drag is not None:
            pos = event.globalPosition().toPoint() - self._drag
            pos.setX(max(0, min(pos.x(), mw.width() - 60)))
            pos.setY(max(0, min(pos.y(), mw.height() - 40)))
            self.move(pos)
            return True
        if kind == event.Type.MouseButtonRelease:
            self._drag = None
            return True
        return False


_pip: Optional[_PipWindow] = None


def toggle_pip() -> None:
    if _pip is not None:
        close_pip()
        return
    view = _video_view()
    if view is None:
        tooltip(_("No video in the Smart Study browser"))
        return

    def found(ok):
        if not ok:
            tooltip(_("No video in the Smart Study browser"))
            return
        open_pip(view)
    _with_video(view, _PIP_ON, found)


def open_pip(view) -> None:
    global _pip
    ws = _ws()
    if _pip is not None or view is None:
        return
    # The video may sit in an iframe: let that iframe fill the page too.
    _run(view.page(), None, _PIP_FRAME_ON)
    ws.detach_view(view)
    _pip = _PipWindow(view)
    view._ss_pip = True
    try:
        view.page().setVisible(True)  # keep it playing although the browser may be hidden
    except Exception:
        pass


def close_pip(show_browser: bool = False) -> None:
    global _pip
    if _pip is None:
        return
    window, _pip = _pip, None
    view = window.view
    view._ss_pip = False
    for frame in _frames(view.page()):
        _run(view.page(), frame, _PIP_OFF)
    _ws().attach_view(view, show=show_browser)
    window.hide()
    window.deleteLater()


# ── Study-plan videos: resume and check off ───────────────────────────────

def video_key(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    host = (parsed.hostname or "").lower()
    if host.endswith("youtube.com"):
        vid = urllib.parse.parse_qs(parsed.query).get("v", [""])[0]
        if vid:
            return "yt:" + vid
    if host == "youtu.be" and parsed.path.strip("/"):
        return "yt:" + parsed.path.strip("/")
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, parsed.query, ""))


def _positions() -> Dict:
    value = _ws()._load_website_state().get("video_positions")
    return value if isinstance(value, dict) else {}


def _save_position(key: str, t: float, d: float) -> None:
    ws = _ws()
    state = ws._load_website_state()
    positions = state.get("video_positions") if isinstance(state.get("video_positions"), dict) else {}
    positions[key] = {"t": round(t, 1), "d": round(d, 1), "at": int(time.time())}
    if len(positions) > 300:  # keep the newest
        for old in sorted(positions, key=lambda k: positions[k].get("at", 0))[:len(positions) - 300]:
            positions.pop(old, None)
    state["video_positions"] = positions
    ws._save_website_state(state)


def open_plan_pdf(path: str, page: int) -> bool:
    """Opens a study-plan PDF at a page in a browser tab; False → open it elsewhere."""
    try:
        import importlib
        package = importlib.import_module(__package__)
        if not getattr(package, "addon_settings", {}).get("website_viewer_enabled", True):
            return False
    except Exception:
        pass
    if load_settings()["plan_external"]:
        return False
    if _ws().open_local_pdf(path, page) is None:
        return False
    if mw is not None:
        mw.activateWindow()
        mw.raise_()
    return True


def open_plan_video(url: str, plan_id: str, item_id: str) -> bool:
    """Opens a study-plan link in a browser tab; False → open it elsewhere."""
    try:
        import importlib
        package = importlib.import_module(__package__)
        if not getattr(package, "addon_settings", {}).get("website_viewer_enabled", True):
            return False
    except Exception:
        pass
    if load_settings()["plan_external"]:
        return False
    ws = _ws()
    key = video_key(url)
    view = next((v for v in ws.all_tab_views() if v is not None and video_key(v.url().toString()) == key), None)
    if not ws.show_browser():
        return False
    if view is not None:
        ws.tab_bar.setCurrentIndex(ws._tab_index(view))
    else:
        saved = _positions().get(key) or {}
        t, d = float(saved.get("t") or 0), float(saved.get("d") or 0)
        if key.startswith("yt:") and load_settings()["resume_videos"] and t >= 15 and not (d and t > d - 20):
            url = _time_link(url, int(t))  # YouTube starts there by itself
        view = ws.new_tab(url)
        if view is None:
            return False
    view._ss_plan = (plan_id, item_id, key)
    view._ss_resumed = None
    if not getattr(view, "_ss_pending", None) and video_key(view.url().toString()) == key:
        _resume(view)  # already open: no load will follow
    _tracker.start()
    return True


def _resume(view) -> None:
    """Jump to where a study-plan video was left (once per page)."""
    plan = getattr(view, "_ss_plan", None)
    if not plan or not load_settings()["resume_videos"]:
        return
    key = video_key(view.url().toString())
    if key != plan[2] or getattr(view, "_ss_resumed", None) == key:
        return
    view._ss_resumed = key
    saved = _positions().get(key) or {}
    t, d = float(saved.get("t") or 0), float(saved.get("d") or 0)
    if t < 15 or (d and t > d - 20):
        return
    # The video may load only when it is started (YouTube without a click).
    script = ("(function(t){var done=false;function go(v){if(done||!(v instanceof HTMLVideoElement))return;"
              "done=true;if(v.currentTime<t-5)v.currentTime=t;}var v=(%s)();if(v&&v.readyState>0)go(v);"
              "['loadedmetadata','playing'].forEach(function(e){document.addEventListener(e,function(ev){go(ev.target);},true);});})(%f)"
              % (_PICK, t))
    for frame in _frames(view.page()):
        _run(view.page(), frame, script)
    tooltip(_("Continuing at {}").format(_clock(t)), period=1500)


def _check_off(plan_id: str, item_id: str) -> None:
    try:
        from .plan import store
        plan = store.load(plan_id)
        done = plan.setdefault("done", {})
        if item_id in done:
            return
        done[item_id] = time.strftime("%Y-%m-%dT%H:%M")
        store.save(plan)
        from . import plan as plan_module
        window = getattr(plan_module, "_win", None)
        if window is not None:
            window.refresh_soon()
        tooltip(_("✓ Video checked off in the study plan"), period=2500)
    except Exception as e:
        print(f"Smart Study browser: could not check off video: {e}")


def _track() -> None:
    ws = _ws()
    views = [v for v in ws.all_tab_views() if v is not None and getattr(v, "_ss_plan", None)]
    if _pip is not None and getattr(_pip.view, "_ss_plan", None) and _pip.view not in views:
        views.append(_pip.view)
    if not views:
        _tracker.stop()
        return
    percent = load_settings()["done_percent"]
    for view in views:
        plan_id, item_id, key = view._ss_plan
        if video_key(view.url().toString()) != key:
            continue

        def got(info, view=view, plan_id=plan_id, item_id=item_id, key=key):
            if not info or not info[1]:
                return
            t, d, paused = info
            last = getattr(view, "_ss_last_saved", -100)
            if abs(t - last) >= 4:
                view._ss_last_saved = t
                _save_position(key, t, d)
            if t / d * 100 >= percent:
                _check_off(plan_id, item_id)
        _with_video(view, "return [v.currentTime, isFinite(v.duration)?v.duration:0, v.paused];", got)


_tracker = QTimer()
_tracker.setInterval(5000)
_tracker.timeout.connect(_track)


# ── Cards from the browser ────────────────────────────────────────────────

def _io_kind() -> int:
    from anki.models import StockNotetype
    return StockNotetype.OriginalStockKind.ORIGINAL_STOCK_KIND_IMAGE_OCCLUSION


def _add_dialog():
    """Anki's Add window, or None when it already holds unsaved text."""
    import aqt
    addcards = aqt.dialogs.open("AddCards", mw)
    note = getattr(getattr(addcards, "editor", None), "note", None)
    if note is not None and any(field.strip() for field in note.fields):
        tooltip(_("The Add window already contains a note. Add or clear it first."), period=3000)
        return None
    return addcards


def _text_notetype(addcards):
    """The notetype open in the Add window, or a standard one when that is
    image occlusion."""
    current = addcards.editor.note.note_type() if addcards.editor.note else None
    if current and current.get("originalStockKind", 0) != _io_kind():
        return current
    for entry in mw.col.models.all_names_and_ids():
        model = mw.col.models.get(entry.id)
        if model and model.get("originalStockKind", 0) != _io_kind() and len(model["flds"]) >= 2:
            return model
    return current


def _fill_new_note(back_html: str) -> None:
    addcards = _add_dialog()
    if addcards is None:
        return
    model = _text_notetype(addcards)
    note = mw.col.new_note(model)
    if len(note.fields) >= 2:
        note.fields[1] = back_html
    else:
        note.fields[0] = back_html
    addcards.set_note(note)
    addcards.activateWindow()


def _source(url: str, title: str) -> str:
    return '<br><br><small>%s: <a href="%s">%s</a></small>' % (
        html.escape(_("Source")), html.escape(url, quote=True), html.escape(title or url))


def card_from_selection(view, text: Optional[str] = None) -> None:
    if view is None:
        return
    text = (text if text is not None else view.selectedText()).strip()
    if not text:
        tooltip(_("Select some text on the page first."))
        return
    body = "<br>".join(html.escape(line) for line in text.splitlines())
    _fill_new_note(body + _source(view.url().toString(), view.title()))


def _time_link(url: str, seconds: int) -> str:
    parsed = urllib.parse.urlsplit(url)
    if video_key(url).startswith("yt:"):
        query = [(k, v) for k, v in urllib.parse.parse_qsl(parsed.query) if k != "t"]
        query.append(("t", "%ds" % seconds))
        return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path,
                                        urllib.parse.urlencode(query), ""))
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, parsed.query, "t=%d" % seconds))


def video_card(view=None) -> None:
    """Pauses the video and opens a new card with a link to this moment."""
    view = view or _video_view()
    if view is None:
        tooltip(_("No video in the Smart Study browser"))
        return

    def got(t):
        if t is None:
            tooltip(_("No video in the Smart Study browser"))
            return
        seconds = int(t)
        link = _time_link(view.url().toString(), seconds)
        title = re.sub(r"\s+-\s+YouTube$", "", view.title() or "") or link
        _fill_new_note('▶ <a href="%s">%s – %s</a>' % (
            html.escape(link, quote=True), html.escape(title), _clock(seconds)))
    _with_video(view, "v.pause();return v.currentTime;", got)


def occlusion_from_image(view) -> None:
    """Copies the image under the mouse and opens it in Anki's image
    occlusion editor."""
    clipboard = QApplication.clipboard()
    waited = {"done": False}

    def copied():
        if waited["done"]:
            return
        image = clipboard.image()
        if image.isNull():
            return
        waited["done"] = True
        try: clipboard.dataChanged.disconnect(copied)
        except Exception: pass
        from anki.utils import tmpdir
        path = os.path.join(tmpdir(), "smartstudy-occlusion-%d.png" % int(time.time() * 1000))
        image.save(path, "PNG")
        _open_occlusion(path)

    def give_up():
        if not waited["done"]:
            waited["done"] = True
            try: clipboard.dataChanged.disconnect(copied)
            except Exception: pass
            tooltip(_("Could not copy the image."))

    clipboard.dataChanged.connect(copied)
    view.page().triggerAction(view.page().WebAction.CopyImageToClipboard)
    QTimer.singleShot(5000, give_up)


def _open_occlusion(path: str) -> None:
    kind = _io_kind()
    model = next((m for m in (mw.col.models.get(e.id) for e in mw.col.models.all_names_and_ids())
                  if m and m.get("originalStockKind", 0) == kind), None)
    if model is None:
        mw.col.add_image_occlusion_notetype()
        model = next((m for m in (mw.col.models.get(e.id) for e in mw.col.models.all_names_and_ids())
                      if m and m.get("originalStockKind", 0) == kind), None)
    if model is None:
        tooltip(_("Image occlusion is not available in this Anki version."))
        return
    addcards = _add_dialog()
    if addcards is None:
        return
    addcards.set_note(mw.col.new_note(model))
    addcards.activateWindow()
    QTimer.singleShot(700, lambda: addcards.editor.setup_mask_editor(path))


# ── Context menu of a browser tab ─────────────────────────────────────────

def show_context_menu(view, pos) -> None:
    menu = view.createStandardContextMenu()
    request = view.lastContextMenuRequest()
    extra = []
    selected = request.selectedText() if request else ""
    if selected.strip():
        extra.append((_("Create card from selection"), lambda: card_from_selection(view, selected)))
    if request and QWebEngineContextMenuRequest is not None:
        media = request.mediaType()
        if media == QWebEngineContextMenuRequest.MediaType.MediaTypeImage:
            extra.append((_("Image occlusion from this image"), lambda: occlusion_from_image(view)))
        if media == QWebEngineContextMenuRequest.MediaType.MediaTypeVideo or video_key(view.url().toString()).startswith("yt:"):
            extra.append((_("Card at this point of the video"), lambda: video_card(view)))
            extra.append((_("Picture in picture"), lambda: (open_pip(view) if _pip is None else close_pip())))
    if extra:
        from aqt.qt import QAction
        first = menu.actions()[0] if menu.actions() else None
        for label, action in extra:
            act = QAction(label, menu)
            act.triggered.connect(lambda _=False, a=action: QTimer.singleShot(0, a))
            menu.insertAction(first, act)
        if first is not None:
            menu.insertSeparator(first)
    menu.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
    menu.popup(view.mapToGlobal(pos))


# ── Tab groups ────────────────────────────────────────────────────────────

def _groups() -> List[Dict]:
    value = _ws()._load_website_state().get("tab_groups")
    return [g for g in value if isinstance(g, dict) and g.get("name")] if isinstance(value, list) else []


def _save_groups(groups: List[Dict]) -> None:
    ws = _ws()
    state = ws._load_website_state()
    state["tab_groups"] = groups
    ws._save_website_state(state)


def fill_groups_menu(menu) -> None:
    ws = _ws()
    menu.clear()
    menu.addAction(_("Save open tabs as a group…")).triggered.connect(lambda: QTimer.singleShot(0, _save_group))
    groups = _groups()
    if groups:
        menu.addSeparator()
    for index, group in enumerate(groups):
        tabs = group.get("tabs") or []
        sub = menu.addMenu("%s  (%d)" % (group["name"], len(tabs)))
        sub.addAction(_("Open")).triggered.connect(lambda _=False, g=group: ws.open_tabs(g.get("tabs") or []))
        sub.addAction(_("Open instead of the open tabs")).triggered.connect(
            lambda _=False, g=group: ws.open_tabs(g.get("tabs") or [], replace=True))
        sub.addSeparator()
        sub.addAction(_("Replace with the open tabs")).triggered.connect(lambda _=False, i=index: _update_group(i))
        sub.addAction(_("Rename…")).triggered.connect(lambda _=False, i=index: QTimer.singleShot(0, lambda: _rename_group(i)))
        sub.addAction(_("Delete")).triggered.connect(lambda _=False, i=index: _delete_group(i))


def _save_group() -> None:
    tabs = _ws().open_tab_entries()
    if not tabs:
        return
    name, ok = QInputDialog.getText(mw, _("Tab group"), _("Name of the group:"))
    name = (name or "").strip()[:60]
    if not ok or not name:
        return
    groups = [g for g in _groups() if g["name"] != name]
    groups.append({"name": name, "tabs": tabs})
    _save_groups(groups)
    tooltip(_("Group “{}” saved ({} tabs)").format(name, len(tabs)))


def _update_group(index: int) -> None:
    groups = _groups()
    if 0 <= index < len(groups):
        groups[index]["tabs"] = _ws().open_tab_entries()
        _save_groups(groups)
        tooltip(_("Group “{}” saved ({} tabs)").format(groups[index]["name"], len(groups[index]["tabs"])))


def _rename_group(index: int) -> None:
    groups = _groups()
    if not 0 <= index < len(groups):
        return
    name, ok = QInputDialog.getText(mw, _("Tab group"), _("Name of the group:"), text=groups[index]["name"])
    name = (name or "").strip()[:60]
    if ok and name:
        groups[index]["name"] = name
        _save_groups(groups)


def _delete_group(index: int) -> None:
    groups = _groups()
    if 0 <= index < len(groups):
        groups.pop(index)
        _save_groups(groups)


# ── Focus mode ────────────────────────────────────────────────────────────

_FOCUS_CSS = {
    "shorts": ("ytd-reel-shelf-renderer,ytd-rich-shelf-renderer[is-shorts],"
               "ytd-rich-section-renderer:has(ytd-rich-shelf-renderer[is-shorts]),"
               "ytd-guide-entry-renderer:has(a[title='Shorts']),ytd-mini-guide-entry-renderer[aria-label='Shorts'],"
               "ytd-rich-item-renderer:has(a[href^='/shorts/']),ytd-video-renderer:has(a[href^='/shorts/']),"
               "grid-shelf-view-model,ytm-shorts-lockup-view-model,ytm-shorts-lockup-view-model-v2,"
               "yt-tab-shape[tab-title='Shorts']"),
    "home": "ytd-browse[page-subtype='home'] ytd-rich-grid-renderer,ytd-browse[page-subtype='home'] #chips-wrapper",
    "related": ("#related,ytd-watch-next-secondary-results-renderer,.ytp-endscreen-content,.ytp-ce-element,"
                ".html5-endscreen,.ytp-autonav-endscreen-countdown-overlay"),
    "comments": "ytd-comments#comments,#comments",
}
_FOCUS_JS = ("(function(css){if(!/(^|\\.)youtube\\.com$/.test(location.hostname))return;"
             "function put(){var s=document.getElementById('ss-focus-style');"
             "if(!css){if(s)s.remove();return;}"
             "if(!s){s=document.createElement('style');s.id='ss-focus-style';(document.head||document.documentElement).appendChild(s);}"
             "s.textContent=css;}"
             "if(document.documentElement)put();else document.addEventListener('readystatechange',put,{once:true});})(%s);")
_FOCUS_SCRIPT = "smartstudy-focus"
_focus_state = {"active": None}


def focus_active() -> bool:
    mode = load_settings()["focus_mode"]
    if mode == "always":
        return True
    if mode == "pomodoro":
        try:
            from . import constants, pomodoro
            return pomodoro.current_state == constants.STATE_WORK
        except Exception:
            return False
    return False


def _focus_hosts(s: Dict) -> List[str]:
    hosts = list(s["focus_sites"])
    if "x.com" in hosts:
        hosts.append("twitter.com")
    for part in re.split(r"[\s,;]+", s["focus_custom"]):
        part = part.strip().lower()
        if not part:
            continue
        host = urllib.parse.urlsplit(part if "://" in part else "https://" + part).hostname or ""
        if host.startswith("www."):
            host = host[4:]
        if "." in host:
            hosts.append(host)
    return hosts


def focus_blocks(url: QUrl) -> bool:
    if url.scheme() not in ("http", "https") or not focus_active():
        return False
    s = load_settings()
    host = url.host().lower()
    if any(host == h or host.endswith("." + h) for h in _focus_hosts(s)):
        return True
    return ("shorts" in s["focus_youtube"] and (host == "youtube.com" or host.endswith(".youtube.com"))
            and url.path().startswith("/shorts"))


def show_blocked(view, url: QUrl) -> None:
    from .website_sidebar import _toolbar_palette
    c = _toolbar_palette()
    page = ("<html><body style='margin:0;display:flex;align-items:center;justify-content:center;height:100vh;"
            "background:%s;color:%s;font-family:sans-serif;text-align:center'><div style='max-width:340px;padding:20px'>"
            "<div style='font-size:42px'>🎯</div><h2 style='margin:10px 0'>%s</h2><p style='opacity:.75;line-height:1.5'>%s</p>"
            "</div></body></html>") % (
        c["bar"], c["text"], html.escape(_("Focus mode")),
        html.escape(_("{} is blocked while you study. Change this under Smart Study → Settings → Browser.").format(url.host())))
    view.setHtml(page)


def _focus_css() -> str:
    if not focus_active():
        return ""
    keys = load_settings()["focus_youtube"]
    return "\n".join(_FOCUS_CSS[k] + "{display:none!important}" for k in keys if k in _FOCUS_CSS)


def _focus_changed(force: bool = False) -> None:
    active = focus_active()
    if not force and active == _focus_state["active"]:
        return
    _focus_state["active"] = active
    ws = _ws()
    profile = ws.website_profile
    css = _focus_css()
    source = _FOCUS_JS % json.dumps(css)
    if profile is not None and QWebEngineScript is not None:
        scripts = profile.scripts()
        for old in scripts.find(_FOCUS_SCRIPT):
            scripts.remove(old)
        if css:
            script = QWebEngineScript()
            script.setName(_FOCUS_SCRIPT)
            script.setSourceCode(source)
            script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentReady)
            script.setWorldId(QWebEngineScript.ScriptWorldId.ApplicationWorld)
            script.setRunsOnSubFrames(False)
            scripts.insert(script)
    for view in ws.all_tab_views() + ([_pip.view] if _pip is not None else []):
        if view is None:
            continue
        _run(view.page(), None, source)
        if active and focus_blocks(view.url()):
            show_blocked(view, view.url())


_focus_timer = QTimer()
_focus_timer.setInterval(2000)
_focus_timer.timeout.connect(_focus_changed)


# ── SponsorBlock ──────────────────────────────────────────────────────────

_SB_API = "https://sponsor.ajay.app/api/skipSegments/%s?categories=%s&actionTypes=%s"
_segments: Dict[str, list] = {}
_SB_JS = ("(function(id,segs,labels){window.__ssSB=window.__ssSB||{};window.__ssSB[id]=segs;"
          "if(window.__ssSBon)return;window.__ssSBon=true;"
          "function toast(text){var d=document.createElement('div');d.textContent=text;"
          "d.style.cssText='position:fixed;left:50%%;bottom:72px;transform:translateX(-50%%);z-index:2147483647;"
          "background:rgba(0,0,0,.8);color:#fff;padding:7px 14px;border-radius:16px;font:13px sans-serif;pointer-events:none';"
          "document.documentElement.appendChild(d);setTimeout(function(){d.remove();},1800);}"
          "document.addEventListener('timeupdate',function(e){var v=e.target;if(!(v instanceof HTMLVideoElement))return;"
          "var id=new URLSearchParams(location.search).get('v');var list=window.__ssSB[id];if(!list)return;"
          "var t=v.currentTime;for(var i=0;i<list.length;i++){var s=list[i];"
          "if(t>=s[0]&&t<s[1]-0.5){v.currentTime=s[1];toast(labels[s[2]]||labels['']);break;}}},true);})(%s,%s,%s)")


def _youtube_id(url: QUrl) -> str:
    host = url.host().lower()
    if not (host == "youtube.com" or host.endswith(".youtube.com")) or url.path() != "/watch":
        return ""
    return urllib.parse.parse_qs(url.query()).get("v", [""])[0]


def _fetch_segments(vid: str, categories: List[str]) -> list:
    prefix = hashlib.sha256(vid.encode()).hexdigest()[:4]
    url = _SB_API % (prefix, urllib.parse.quote(json.dumps(categories)),
                     urllib.parse.quote(json.dumps(["skip"])))
    request = urllib.request.Request(url, headers={"User-Agent": "Smart Study"})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return []  # no segments for these videos
        raise
    for entry in data:
        if entry.get("videoID") == vid:
            return [[float(s["segment"][0]), float(s["segment"][1]), s.get("category", "")]
                    for s in entry.get("segments", []) if s.get("actionType", "skip") == "skip"]
    return []


def _sponsor_labels() -> Dict[str, str]:
    labels = {key: _("Skipped: {}").format(_(label)) for key, label in SPONSOR_CATEGORIES}
    labels[""] = _("Skipped")
    return labels


def _sponsorblock(view, url: QUrl) -> None:
    s = load_settings()
    vid = _youtube_id(url)
    if not vid or not s["sponsorblock"] or not s["sponsor_categories"]:
        return

    def inject(segments):
        if segments:
            try:
                _run(view.page(), None, _SB_JS % (json.dumps(vid), json.dumps(segments), json.dumps(_sponsor_labels())))
            except RuntimeError:
                pass

    cache_key = vid + "|" + ",".join(sorted(s["sponsor_categories"]))
    if cache_key in _segments:
        inject(_segments[cache_key])
        return

    def fetched(future):
        try:
            segments = future.result()
        except Exception as e:
            print(f"Smart Study browser: SponsorBlock not reached: {e}")
            return
        _segments[cache_key] = segments
        inject(segments)
    mw.taskman.run_in_background(lambda: _fetch_segments(vid, s["sponsor_categories"]), fetched)


# ── Wiring for each tab ───────────────────────────────────────────────────

def setup_view(view) -> None:
    """Called by the browser for every new tab."""
    view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    view.customContextMenuRequested.connect(lambda pos: show_context_menu(view, pos))
    view.urlChanged.connect(lambda url: on_url_changed(view, url))
    view.loadFinished.connect(lambda ok: ok and _resume(view))
    # A full page load starts a new document; URL changes within YouTube don't.
    view.loadFinished.connect(lambda ok: ok and _sponsorblock(view, view.url()))


def on_url_changed(view, url: QUrl) -> None:
    # YouTube changes pages without loading them, so check every URL change.
    if focus_blocks(url):
        QTimer.singleShot(0, lambda: show_blocked(view, url))
        return
    _sponsorblock(view, url)
    if getattr(view, "_ss_plan", None):
        QTimer.singleShot(1500, lambda: _resume(view))


def start() -> None:
    """When the browser has been created."""
    apply_shortcuts()
    _focus_changed(force=True)
    _focus_timer.start()


def stop() -> None:
    close_pip()
    _tracker.stop()
    _focus_timer.stop()
    for shortcut in _shortcuts:
        try:
            shortcut.setParent(None)
            shortcut.deleteLater()
        except RuntimeError:
            pass
    _shortcuts.clear()
