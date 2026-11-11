# -*- coding: utf-8 -*-

import json
import html
import traceback
from functools import partial
from typing import Optional, List, Dict, Tuple
import os
import urllib.parse

BROWSER_HOME_URL = "https://duckduckgo.com/"  # default; see _home_url()

# --- Local Imports ---
from . import constants, diagnostics
from .browser_fallback import is_google_url, needs_search_help, duckduckgo_url
from . import browser_search
from .browser_adblock import AdBlocker, FilteringPage, install_youtube_pruner
from . import browser_features, web_sleep
from . import browser_layout, browser_passwords
from . import browser_chrome, browser_history

try:
    from .locales import _
except ImportError:
    def _(text):  # type: ignore
        return text

# --- PyQt Imports ---
_qt_available = False
try:
    from aqt.qt import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                        QInputDialog, QDockWidget, QSizePolicy, QMessageBox,
                        QMenu, QAction, QIcon, QPixmap, QPainter, QUrl, QTimer,
                        QSize, Qt, QByteArray, QDesktopServices, QEvent, QObject,
                        QTabBar, QStackedWidget, QShortcut, QKeySequence,
                        QLineEdit, QFileDialog, QStandardPaths, QApplication,
                        QCompleter, QStandardItemModel, QStandardItem, QModelIndex)
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage, QWebEngineSettings
    from PyQt6 import sip
    WebAction = QWebEnginePage.WebAction
    print("Website Sidebar: Using Qt6 components")
    _qt_available = True
except ImportError as e:
    print(f"Website Sidebar Error: Could not import necessary PyQt components. {e}")
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton = object, object, object, object
    QInputDialog, QDockWidget, QSizePolicy, QMessageBox = object, object, object, object
    QUrl, QTimer, QSize, Qt = object, object, object, None
    QDesktopServices = object; QEvent = object; QObject = object
    QByteArray = object; QIcon = object; QPixmap = object; QPainter = object
    QWebEngineView, QWebEngineProfile, QWebEnginePage, QWebEngineSettings = object, object, object, object
    QAction = object; WebAction = object; QMenu = object
    QTabBar = QStackedWidget = QShortcut = QKeySequence = object
    QLineEdit = QFileDialog = QStandardPaths = object
    QApplication = object
    QCompleter = QStandardItemModel = QStandardItem = QModelIndex = object

# QtSvg is optional – used only to render crisp toolbar icons. A failure here
# must never break the rest of the module, so it gets its own guarded import.
_svg_available = False
try:
    from PyQt6.QtSvg import QSvgRenderer
    _svg_available = True
except Exception as _e_svg:
    QSvgRenderer = object  # type: ignore
    print(f"Website Sidebar: QtSvg unavailable, using glyph fallback. {_e_svg}")


# --- Anki Imports ---
try:
    from aqt import mw, gui_hooks
    from aqt.utils import showInfo, tooltip, qconnect, showWarning
except ImportError:
    print("Website Sidebar Error: Could not import aqt modules.")
    mw = None; showInfo = lambda *a, **k: print("Info:", a); tooltip = lambda *a, **k: print("Tooltip:", a)
    qconnect = lambda *a: None; showWarning = lambda *a, **k: print("Warning:", a)
    gui_hooks = None


# --- Button Stylesheets ---
# Moderner Look: Kein Rahmen, leichter Schlagschatten (via border-bottom) und Klick-Animation

def _toolbar_palette() -> dict:
    """Colours of the browser's bars (theme-aware)."""
    return browser_chrome.palette()


def _get_blue_button_style() -> str:
    return browser_chrome.chip()


def _get_icon_button_style() -> str:
    """Square icon button of the bars (back, forward, reload, new tab …)."""
    return browser_chrome.icon_button()


def _get_raised_text_button_style() -> str:
    """A saved site or Home in the favourites row."""
    return browser_chrome.chip()


def _get_raised_icon_button_style() -> str:
    return browser_chrome.small_icon_button()


def _get_delete_button_style() -> str:
    return browser_chrome.small_icon_button()


# Backwards-compatible alias (still referenced in a few places).
WHITE_BUTTON_STYLE = _get_delete_button_style()


# Same "open in main window" glyph used by the Mindmap / Notebook nav bars:
# a window frame (rectangle with a title-bar line).
_WINDOW_ICON_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" '
    'fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<rect x="3" y="3" width="18" height="18" rx="2"></rect>'
    '<line x1="3" y1="9" x2="21" y2="9"></line>'
    '</svg>'
)

# Variant shown while the embedded main-window view is active: the same
# window frame with a small dash inside ("close window" state, identical to
# the Mindmap / Notebook nav bars).
_WINDOW_CLOSE_ICON_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" '
    'fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<rect x="3" y="3" width="18" height="18" rx="2"></rect>'
    '<line x1="3" y1="9" x2="21" y2="9"></line>'
    '<line x1="9" y1="15" x2="15" y2="15"></line>'
    '</svg>'
)


def _make_window_icon(size: int = 16, active: bool = False):
    """Render the window-frame SVG into a crisp QIcon (theme-aware). None on failure.

    ``active`` selects the "close window" variant (frame with a dash) shown
    while the embedded main-window view is open.
    """
    if not _svg_available or QIcon is object or QPixmap is object or QPainter is object:
        return None
    try:
        color = _toolbar_palette()["text"]
        scale = 2  # render at 2x for retina crispness
        template = _WINDOW_CLOSE_ICON_SVG if active else _WINDOW_ICON_SVG
        svg = template.format(s=size, c=color)
        renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
        pm = QPixmap(QSize(size * scale, size * scale))
        pm.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pm)
        renderer.render(painter)
        painter.end()
        try:
            pm.setDevicePixelRatio(float(scale))
        except Exception:
            pass
        return QIcon(pm)
    except Exception as e:
        print(f"WS Warn: could not build window icon: {e}")
        return None


def _apply_window_icon(btn, active: bool = False) -> None:
    """Put the layout icon on ``btn`` (falls back to the ⧉ glyph).

    ``active`` shows the "close window" variant while the embedded view is on.
    """
    if btn is None:
        return
    try:
        browser_chrome.set_icon(btn, "layout-close" if active else "layout")
        return
    except Exception:
        pass
    icon = _make_window_icon(16, active=active)
    if icon is not None:
        try:
            btn.setText("")
            btn.setIcon(icon)
            btn.setIconSize(QSize(16, 16))
            return
        except Exception:
            pass
    try:
        btn.setText("⧉")  # ⧉ fallback glyph
    except Exception:
        pass

# --- Module Globals ---
sidebar_dock: Optional[QDockWidget] = None
sidebar_webview: Optional[QWebEngineView] = None
website_profile: Optional[QWebEngineProfile] = None
ad_blocker = None  # browser_adblock.AdBlocker of the current profile
button_container_layout: Optional[QHBoxLayout] = None
nav_button_layout: Optional[QHBoxLayout] = None
add_button_widget: Optional[QPushButton] = None
home_button_widget: Optional[QPushButton] = None
back_button: Optional[QPushButton] = None
forward_button: Optional[QPushButton] = None
refresh_button: Optional[QPushButton] = None
window_button: Optional[QPushButton] = None
custom_button_containers: List[QWidget] = []
# Tabs: sidebar_webview is always the view of the current tab.
tab_bar = None        # QTabBar
tab_stack = None      # QStackedWidget with one QWebEngineView per tab
search_help = None    # the "Google is having trouble" hint above the views
load_bar = None       # browser_chrome.LoadBar under the bars
pip_placeholder = None  # shown for a tab whose video plays in picture in picture
browser_container = None  # the browser's content widget (for its shortcuts)
MAX_TABS = 20

# Embedded view (inside the Anki main window) that borrows the dock content.
website_main_layout: Optional[QVBoxLayout] = None
website_window = None  # truthy marker while an embedded view is active
website_embedded_content: Optional[QWidget] = None  # the dock body while embedded

# --- Configuration Management ---
def get_default_sites_if_empty() -> List[Dict[str, str]]:
    """Returns Notion as a default suggestion if no sites are configured."""
    return [
        {"name": "YouTube", "url": "https://www.youtube.com/"}
    ]


def _website_state_path() -> Optional[str]:
    try:
        root = mw.pm.profileFolder() if mw and mw.pm else None
        if not root:
            return None
        folder = os.path.join(root, "SmartStudy_Data")
        os.makedirs(folder, exist_ok=True)
        return os.path.join(folder, "website_state.json")
    except Exception:
        return None


def _load_website_state() -> Dict:
    path = _website_state_path()
    if path and os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as handle:
                value = json.load(handle)
            return value if isinstance(value, dict) else {}
        except Exception as exc:
            print(f"WS Warn: Could not read local website state: {exc}")

    # Migrate older collection-synced browser metadata into profile-local data.
    state: Dict = {}
    if mw and mw.col:
        try:
            raw_sites = mw.col.get_config(constants.CONFIG_KEY_CUSTOM_SITES)
            if isinstance(raw_sites, str):
                parsed = json.loads(raw_sites)
                if isinstance(parsed, list):
                    state["custom_sites"] = parsed
            raw_url = mw.col.get_config(constants.CONFIG_KEY_LAST_OPENED_URL)
            if isinstance(raw_url, str):
                state["last_url"] = raw_url
            if not _save_website_state(state, verify=True):
                return state
            for key in (constants.CONFIG_KEY_CUSTOM_SITES,
                        constants.CONFIG_KEY_LAST_OPENED_URL):
                remover = getattr(mw.col, "remove_config", None)
                if callable(remover): remover(key)
                else: mw.col.set_config(key, None)
        except Exception as exc:
            print(f"WS Warn: Could not migrate website state: {exc}")
    return state


def _save_website_state(state: Dict, *, verify: bool = False) -> bool:
    path = _website_state_path()
    if not path:
        return False
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as handle:
            json.dump(state, handle, indent=2, ensure_ascii=False)
            if verify:
                handle.flush()
                os.fsync(handle.fileno())
        os.replace(tmp, path)
        if verify:
            with open(path, "r", encoding="utf-8") as handle:
                return json.load(handle) == state
        return True
    except Exception as exc:
        print(f"WS Warn: Could not save local website state: {exc}")
        try:
            if os.path.exists(tmp): os.remove(tmp)
        except OSError: pass
        return False

def load_custom_sites() -> List[Dict[str, str]]:
    sites = _load_website_state().get("custom_sites")
    if isinstance(sites, list):
        clean = [
            {"name": str(site.get("name", ""))[:80], "url": str(site.get("url", ""))[:8192]}
            for site in sites if isinstance(site, dict) and site.get("name") and site.get("url")
        ]
        if clean:
            return clean[:constants.MAX_CUSTOM_SITES]
    return get_default_sites_if_empty()


def save_custom_sites(sites: List[Dict[str, str]]):
    if len(sites) > constants.MAX_CUSTOM_SITES: sites = sites[:constants.MAX_CUSTOM_SITES]
    state = _load_website_state()
    state["custom_sites"] = sites
    _save_website_state(state)

def save_last_opened_url(url: str):
    if not isinstance(url, str) or len(url) > 8192:
        return
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return
    state = _load_website_state()
    state["last_url"] = url
    _save_website_state(state)

def load_last_opened_url() -> Optional[str]:
    value = _load_website_state().get("last_url")
    return value if isinstance(value, str) and len(value) <= 8192 else None


# --- UI Actions ---
def _search_engine() -> str:
    return browser_search.engine_key(_load_website_state().get("search_engine"))


def _home_url() -> str:
    return browser_search.home_url(_search_engine())


def _adblock_on() -> bool:
    return _load_website_state().get("adblock", True) is not False


def _set_browser_option(key: str, value) -> None:
    state = _load_website_state()
    state[key] = value
    _save_website_state(state)


def _choose_search_engine(key: str) -> None:
    _set_browser_option("search_engine", key)
    if sidebar_webview is not None:
        load_url_in_webview(sidebar_webview, browser_search.home_url(key))


def _toggle_adblock(on: bool) -> None:
    _set_browser_option("adblock", bool(on))
    if ad_blocker is not None:
        ad_blocker.enabled = bool(on)
    _apply_youtube_pruner()
    if sidebar_webview is not None:
        sidebar_webview.reload()


def _apply_youtube_pruner() -> None:
    """YouTube ad pruning follows the ad-blocker switches; the streaming
    sidebar (YouTube Music) uses it too."""
    on = _adblock_on()
    off = ad_blocker.allowed_sites if ad_blocker is not None else ()
    try:
        if website_profile is not None:
            install_youtube_pruner(website_profile, on, off)
        from .web_accounts import account_profile
        install_youtube_pruner(account_profile(), on, off)
    except Exception as e:
        print(f"WS Warn: YouTube ad pruning not available: {e}")


def _toggle_adblock_site(host: str, on: bool) -> None:
    """Switch the blocker off for one site that breaks with it."""
    if ad_blocker is None:
        return
    (ad_blocker.allowed_sites.discard if on else ad_blocker.allowed_sites.add)(host)
    _set_browser_option("adblock_off_sites", sorted(ad_blocker.allowed_sites))
    _apply_youtube_pruner()
    if sidebar_webview is not None:
        sidebar_webview.reload()


def _open_browser_settings() -> None:
    try:
        import importlib
        importlib.import_module(__package__).show_settings_dialog("browser")
    except Exception as e:
        print(f"WS Warn: settings not opened: {e}")


def _history_on() -> bool:
    return bool(_load_website_state().get("history", True))


def _clear_history() -> None:
    browser_history.clear()
    tooltip(_("Browsing history cleared."))


_history_timer = None


def _remember_visit(view, ok: bool = True) -> None:
    """A loaded page goes into the history (if that is switched on); saved a few seconds later."""
    global _history_timer
    try:
        if not ok or sip.isdeleted(view) or not _history_on():
            return
        browser_history.add(view.url().toString(), getattr(view, "_ss_title", "") or "")
        if _history_timer is None:
            _history_timer = QTimer(mw)
            _history_timer.setSingleShot(True)
            _history_timer.setInterval(5000)
            qconnect(_history_timer.timeout, browser_history.save)
        _history_timer.start()
    except Exception as e:
        print(f"WS Info: history: {e}")


_URL_ROLE = 0x0100 + 1  # Qt.ItemDataRole.UserRole + 1


def _suggestion_style() -> str:
    c = _toolbar_palette()
    return f"""
    QListView {{ background: {c['field']}; color: {c['text']}; border: 1px solid {c['line']}; border-radius: 8px;
        padding: 4px; outline: 0; font-size: 12.5px; }}
    QListView::item {{ padding: 5px 8px; border-radius: 6px; }}
    QListView::item:selected, QListView::item:hover {{ background: {c['hover']}; color: {c['text']}; }}
    """


def _setup_suggestions(bar) -> None:
    """While you type, the address field offers pages you visited, favourites and open tabs."""
    if QCompleter is object:
        return
    model = QStandardItemModel(bar)
    completer = QCompleter(model, bar)
    completer.setCompletionMode(QCompleter.CompletionMode.UnfilteredPopupCompletion)  # we do the matching
    completer.setCompletionRole(_URL_ROLE)
    completer.setMaxVisibleItems(7)
    completer.popup().setStyleSheet(_suggestion_style())
    bar.setCompleter(completer)
    bar._ss_completer = completer

    def fill(text: str) -> None:
        model.clear()
        extra = [{"url": s.get("url", ""), "title": s.get("name", "")} for s in load_custom_sites()]
        for view in all_tab_views():
            if view is not None and view is not sidebar_webview and not sip.isdeleted(view):
                extra.append({"url": getattr(view, "_ss_pending", None) or view.url().toString(), "title": getattr(view, "_ss_title", "")})
        for hit in browser_history.suggest(text, extra, history=_history_on()):
            shown = browser_history.short(hit["url"])
            item = QStandardItem(f"{hit['title']}  —  {shown}" if hit["title"] else shown)
            item.setData(hit["url"], _URL_ROLE)
            item.setToolTip(hit["url"])
            icon = browser_history.load_icon(hit["url"]) or browser_chrome.icon("globe", 14)
            if icon is not None:
                item.setIcon(icon)
            model.appendRow(item)

    def chosen(index) -> None:
        url = index.data(_URL_ROLE)
        if url:
            bar.setText(url)
            bar.setModified(True)
            QTimer.singleShot(0, _address_entered)

    qconnect(bar.textEdited, fill)
    completer.activated[QModelIndex].connect(chosen)


def _fill_options_menu(menu) -> None:
    menu.clear()
    menu.addAction(_("Browser settings…")).triggered.connect(lambda: QTimer.singleShot(0, _open_browser_settings))
    menu.addAction(_("Open PDF file…")).triggered.connect(lambda: QTimer.singleShot(0, open_pdf_file))
    menu.addSeparator()
    engines = menu.addMenu(_("Search engine"))
    current = _search_engine()
    for key, (name, _home, _base, _param) in browser_search.ENGINES.items():
        action = engines.addAction(name)
        action.setCheckable(True)
        action.setChecked(key == current)
        qconnect(action.triggered, lambda _=False, k=key: _choose_search_engine(k))
    browser_passwords.menu_entries(menu)
    menu.addSeparator()
    remember = menu.addAction(_("Suggest visited pages in the address field"))
    remember.setCheckable(True)
    remember.setChecked(_history_on())
    qconnect(remember.toggled, lambda on: _set_browser_option("history", bool(on)))
    menu.addAction(_("Clear browsing history")).triggered.connect(_clear_history)
    if ad_blocker is not None:
        menu.addSeparator()
        block = menu.addAction(_("Block ads and trackers"))
        block.setCheckable(True)
        block.setChecked(ad_blocker.enabled)
        qconnect(block.toggled, _toggle_adblock)
        host = sidebar_webview.url().host() if sidebar_webview is not None else ""
        if ad_blocker.enabled and host:
            here = menu.addAction(_("Block on {}").format(host))
            here.setCheckable(True)
            here.setChecked(host not in ad_blocker.allowed_sites)
            qconnect(here.toggled, lambda on, h=host: _toggle_adblock_site(h, on))
            count = ad_blocker.blocked.get(host, 0)
            info = menu.addAction(_("{} blocked on this page").format(count)
                                  if ad_blocker.engine is not None else _("Loading filter lists…"))
            info.setEnabled(False)


def open_add_site_dialog():
    if not mw or QInputDialog is object or not _qt_available: return
    current_sites = load_custom_sites()
    if len(current_sites) >= constants.MAX_CUSTOM_SITES:
        showWarning(_("Limit of {} custom sites reached.").format(constants.MAX_CUSTOM_SITES)); return

    new_name, ok_name = QInputDialog.getText(mw, _("Add Website"), _("Name for the new button:"), text="")
    if not ok_name or not new_name.strip(): return
    new_name = new_name.strip()

    new_url, ok_url = QInputDialog.getText(mw, _("Add Website"), _("URL for '{}':").format(new_name), text="https://")
    if not ok_url or not new_url.strip(): return
    new_url = new_url.strip()

    if not new_url.startswith("http://") and not new_url.startswith("https://"):
        new_url = "https://" + new_url
        tooltip(_("URL automatically prefixed with https://"))

    if "." not in new_url or "://" not in new_url:
        showWarning(_("URL '{}' seems invalid.").format(new_url)); return

    current_sites.append({"name": new_name, "url": new_url})
    save_custom_sites(current_sites)
    tooltip(_("Site '{}' added.").format(new_name))
    rebuild_custom_buttons_ui()

def delete_custom_site(index_to_delete: int):
    current_sites = load_custom_sites()
    if 0 <= index_to_delete < len(current_sites):
        deleted_site = current_sites.pop(index_to_delete)
        save_custom_sites(current_sites)
        tooltip(_("Site '{}' removed.").format(deleted_site.get('name')))
        rebuild_custom_buttons_ui()
    else:
        showWarning(_("Could not delete site: Invalid index."))

def _is_local_pdf(url) -> bool:
    """A PDF file on this computer (the only local files the browser shows)."""
    try:
        return bool(url.isLocalFile() and url.toLocalFile().lower().endswith(".pdf"))
    except Exception:
        return False


def _restorable(url: str) -> bool:
    """Web pages and local PDFs that still exist can be reopened as tabs."""
    url = str(url or "")
    if url.startswith(("http://", "https://")):
        return True
    if url.startswith("file://") and QUrl is not object:
        q = QUrl(url)
        return _is_local_pdf(q) and os.path.isfile(q.toLocalFile())
    return False


def load_url_in_webview(webview: Optional[QWebEngineView], url_str: str):
    if not webview or QWebEngineView is object or QUrl is object or not _qt_available: return
    url = QUrl.fromUserInput(url_str)
    webview._ss_pending = None  # a tab waiting for its page gets this one instead
    if url.isValid() and (url.scheme() in ["http", "https"] or _is_local_pdf(url)):
        webview.setUrl(url)
    else:
        safe_url = html.escape(str(url_str), quote=True)
        error_html = _("""
        <body style='font-family: sans-serif; padding: 20px; color: #333; background-color: #f9f9f9;'>
            <h2 style='color: #d32f2f;'>Invalid URL</h2>
            <p>The URL you tried to open seems to be invalid or is not a standard web URL (http/https).</p>
            <p>Attempted URL: <code>{url_str}</code></p>
        </body>""").format(url_str=safe_url)
        webview.setHtml(error_html)

# --- UI Construction Helpers ---
def _open_browser_url(url: str) -> None:
    if not _qt_available or QDesktopServices is object:
        return
    target = QUrl(url)
    if target.isValid() and target.scheme() in ("http", "https") and target.host():
        if not QDesktopServices.openUrl(target):
            showWarning(_("Could not open the system browser."))


def open_current_in_browser() -> None:
    if sidebar_webview is None:
        return
    if _is_local_pdf(sidebar_webview.url()):  # a PDF: open it in the PDF app
        QDesktopServices.openUrl(QUrl.fromLocalFile(sidebar_webview.url().toLocalFile()))
        return
    url = sidebar_webview.url().toString()
    # Use Google's original destination instead of moving its CAPTCHA/session
    # token to another browser, where that challenge may no longer be valid.
    parsed = urllib.parse.urlsplit(url)
    host = (parsed.hostname or "").lower()
    if host in ("www.google.com", "google.com") and parsed.path.startswith("/sorry/"):
        candidate = urllib.parse.parse_qs(parsed.query).get("continue", [""])[0]
        destination = urllib.parse.urlsplit(candidate)
        if destination.scheme in ("http", "https") and destination.hostname in ("www.google.com", "google.com"):
            url = candidate
    _open_browser_url(url)


def search_in_browser(text: str) -> None:
    if text and QTimer is not object:
        url = browser_search.search_url(_search_engine(), text)
        QTimer.singleShot(0, lambda: _open_browser_url(url))


# --- Address bar ---
address_bar = None  # QLineEdit above the page


if QLineEdit is not object:
    class _AddressBar(QLineEdit):
        """Selects everything on click, Esc puts the page's address back."""

        def focusInEvent(self, event):
            super().focusInEvent(event)
            full = getattr(self, "_ss_full", "")
            if full and not self.isModified():
                self.setText(full)  # the whole address to edit or copy
                self.setModified(False)
            QTimer.singleShot(0, self.selectAll)

        def focusOutEvent(self, event):
            super().focusOutEvent(event)
            if not self.isModified():
                QTimer.singleShot(0, show_address)

        def keyPressEvent(self, event):
            if event.key() == Qt.Key.Key_Escape:
                self.setModified(False)
                show_address()
                if sidebar_webview is not None:
                    sidebar_webview.setFocus()
                return
            super().keyPressEvent(event)
else:
    _AddressBar = object


def _address_style() -> str:
    return browser_chrome.address()


def _display_url(url: str) -> str:
    if not url or url == "about:blank" or url.startswith("data:"):
        return ""
    q = QUrl(url)
    if _is_local_pdf(q):
        return q.toLocalFile()  # a path reads better than file:///…%20…
    return q.toDisplayString()


def _short_url(url: str) -> str:
    """How the address reads while it is not being edited: without https:// and www.,
    a PDF on this computer by its file name. http:// stays visible (not encrypted)."""
    full = _display_url(url)
    if not full:
        return ""
    q = QUrl(url)
    if _is_local_pdf(q):
        return os.path.basename(q.toLocalFile())
    if full.startswith("https://"):
        full = full[8:]
        if full.startswith("www."):
            full = full[4:]
    return full[:-1] if full.endswith("/") and full.count("/") == 1 else full


def show_address(view=None) -> None:
    """Show the current tab's address (not while the user is typing)."""
    if address_bar is None or sip.isdeleted(address_bar):
        return
    view = view or sidebar_webview
    if view is None or view is not sidebar_webview or sip.isdeleted(view):
        return
    if address_bar.hasFocus() and address_bar.isModified():
        return
    url = getattr(view, "_ss_pending", None) or view.url().toString()
    if not url or url == "about:blank":
        url = getattr(view, "_ss_requested", None) or ""
    address_bar._ss_full = _display_url(url)
    address_bar.setText(address_bar._ss_full if address_bar.hasFocus() else _short_url(url))
    address_bar.setCursorPosition(0)
    address_bar.setModified(False)


def _address_entered() -> None:
    if address_bar is None:
        return
    target = browser_search.address_target(address_bar.text(), _search_engine())
    if not target:
        return
    address_bar.setModified(False)
    diagnostics.record('browser.address')
    view = sidebar_webview
    if view is None:
        new_tab(target)
        return
    view._ss_requested = target
    load_url_in_webview(view, target)
    view.setFocus()


def focus_address_bar() -> None:
    if address_bar is None or not show_browser():
        return
    address_bar.setFocus(Qt.FocusReason.ShortcutFocusReason)
    address_bar.selectAll()


# --- PDFs ---
def open_pdf_file() -> None:
    """Choose a PDF on this computer and open it in a new tab."""
    if QFileDialog is object or mw is None:
        return
    start = _load_website_state().get("last_pdf_folder") or os.path.expanduser("~")
    path, _sel = QFileDialog.getOpenFileName(mw, _("Open PDF file…"), start, _("PDF Files (*.pdf)"))
    if not path:
        return
    _set_browser_option("last_pdf_folder", os.path.dirname(path))
    open_local_pdf(path)


def open_local_pdf(path: str, page: int = 0, view=None):
    """Show a local PDF in the browser (at a page); returns the tab or None."""
    if not path or not os.path.isfile(path) or not show_browser():
        return None
    url = QUrl.fromLocalFile(os.path.abspath(path))
    if page and page > 1:
        url.setFragment(f"page={int(page)}")
    target = url.toString()
    if view is None:
        same = QUrl.fromLocalFile(os.path.abspath(path)).toString()
        view = next((v for v in all_tab_views() if v is not None and not getattr(v, "_ss_pending", None)
                     and v.url().toString(QUrl.UrlFormattingOption.RemoveFragment) == same), None)
    if view is None:
        return new_tab(target)
    tab_bar.setCurrentIndex(_tab_index(view))
    view._ss_requested = target
    if view.url().toString(QUrl.UrlFormattingOption.RemoveFragment) == target.split("#")[0]:
        # Same file: a new #page only reaches the PDF viewer with a reload.
        view.setUrl(QUrl(target))
        QTimer.singleShot(0, lambda: not sip.isdeleted(view) and view.reload())
    else:
        load_url_in_webview(view, target)
    view.setFocus()
    return view


def _pdf_folder() -> str:
    base = ""
    try:
        if QStandardPaths is not object:
            base = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DownloadLocation)
    except Exception:
        base = ""
    if not base or not os.path.isdir(base):
        root = mw.pm.profileFolder() if mw and getattr(mw, "pm", None) else os.path.expanduser("~")
        return os.path.join(root, "SmartStudy_Data", "pdf_downloads")
    return os.path.join(base, "Smart Study PDFs")


def _pdf_file_name(url: str, suggested: str, folder: str) -> str:
    """The same link keeps its file (a newer download replaces it);
    another file with the same name gets " (2)" etc."""
    state = _load_website_state()
    known = state.get("pdf_downloads") if isinstance(state.get("pdf_downloads"), dict) else {}
    name = known.get(url)
    if not name:
        stem = os.path.splitext(os.path.basename(suggested or ""))[0]
        stem = "".join(ch for ch in stem if ch not in '<>:"/\\|?*' and ord(ch) >= 32).strip(" .")[:120] or "document"
        taken = set(known.values())
        name, n = stem + ".pdf", 2
        while name in taken or os.path.exists(os.path.join(folder, name)):
            name, n = f"{stem} ({n}).pdf", n + 1
        known[url] = name
        if len(known) > 300:
            known = dict(list(known.items())[-300:])
        state["pdf_downloads"] = known
        _save_website_state(state)
    return name


def _on_download_requested(download) -> None:
    """PDFs that a site sends as a download open right away in a tab;
    other downloads are left alone as before."""
    try:
        name = download.downloadFileName() or ""
        mime = (download.mimeType() or "").lower()
        if mime != "application/pdf" and not name.lower().endswith(".pdf"):
            return
        url = download.url().toString()
        folder = _pdf_folder()
        os.makedirs(folder, exist_ok=True)
        file_name = _pdf_file_name(url, name, folder)
        download.setDownloadDirectory(folder)
        download.setDownloadFileName(file_name)
        page = download.page()
        view = getattr(page, "_ss_view", None) if page is not None else None
        path = os.path.join(folder, file_name)

        def finished():
            if not download.isFinished():
                return
            from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest
            completed = QWebEngineDownloadRequest.DownloadState.DownloadCompleted
            if download.state() != completed or not os.path.isfile(path):
                tooltip(_("The PDF could not be downloaded."))
                return
            # A link that opened an empty tab for the download shows the PDF there.
            target = view if view is not None and not sip.isdeleted(view) and _is_blank(view) else None
            open_local_pdf(path, view=target)
        download.isFinishedChanged.connect(finished)
        download.accept()
        tooltip(_("Opening PDF…"), period=1500)
    except Exception as e:
        print(f"WS Warn: PDF download not opened: {e}")
        traceback.print_exc()


def create_button_pair(name: str, url: str, index: int) -> Optional[QWidget]:
    """A saved site in the favourites row. Click: open here; middle click or Ctrl+click:
    new tab; right click: open in a new tab or remove."""
    if QWidget is object or QPushButton is object or QSizePolicy is object or not _qt_available:
        return None
    site_button = QPushButton(name)
    site_button.setObjectName("smartstudySiteChip")
    site_button.setStyleSheet(_get_raised_text_button_style())
    site_button.setToolTip(url)
    site_button.setCursor(Qt.CursorShape.PointingHandCursor)
    site_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
    site_button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

    def open_here(_checked=False):
        mods = QApplication.keyboardModifiers() if QApplication is not object else Qt.KeyboardModifier.NoModifier
        if mods & Qt.KeyboardModifier.ControlModifier or sidebar_webview is None:
            new_tab(url)
        else:
            load_url_in_webview(sidebar_webview, url)

    def menu(pos):
        m = QMenu(site_button)
        m.addAction(_("Open in new tab"), lambda: new_tab(url))
        m.addSeparator()
        m.addAction(_("Remove '{}'").format(name), partial(delete_custom_site, index_to_delete=index))
        m.exec(site_button.mapToGlobal(pos))

    qconnect(site_button.clicked, open_here)
    qconnect(site_button.customContextMenuRequested, menu)
    site_button.installEventFilter(_middle_click)
    site_button._ss_middle = lambda: new_tab(url, background=True)
    return site_button


class _MiddleClick(QObject if QObject is not object else object):
    """Middle click on a favourite opens it in a background tab; on a tab it closes the tab."""

    def eventFilter(self, obj, event):
        try:
            if event.type() == QEvent.Type.MouseButtonRelease and event.button() == Qt.MouseButton.MiddleButton:
                if obj is tab_bar:
                    index = tab_bar.tabAt(event.position().toPoint())
                    if index >= 0:
                        QTimer.singleShot(0, lambda: close_tab(index))
                        return True
                action = getattr(obj, "_ss_middle", None)
                if action is not None:
                    QTimer.singleShot(0, action)
                    return True
        except Exception as e:
            print(f"WS Info: middle click: {e}")
        return False


_middle_click = _MiddleClick() if QObject is not object else None


def rebuild_custom_buttons_ui():
    """Favourites row: Home, the saved sites, then + (add). Always in this order."""
    global button_container_layout, custom_button_containers, add_button_widget
    if not button_container_layout or QHBoxLayout is object or QWidget is object or QPushButton is object or not _qt_available:
        return

    for container in custom_button_containers:
        button_container_layout.removeWidget(container)
        container.deleteLater()
    custom_button_containers.clear()

    custom_sites = load_custom_sites()
    first = 0
    if home_button_widget is not None:
        first = max(0, button_container_layout.indexOf(home_button_widget)) + 1

    for i, site_info in enumerate(custom_sites):
        pair_widget = create_button_pair(site_info['name'], site_info['url'], index=i)
        if pair_widget:
            button_container_layout.insertWidget(first + len(custom_button_containers), pair_widget)
            custom_button_containers.append(pair_widget)

    if add_button_widget:
        can_add_more = len(custom_sites) < constants.MAX_CUSTOM_SITES
        add_button_widget.setVisible(can_add_more)
        add_button_widget.setEnabled(can_add_more)
        add_button_widget.setToolTip(_("Add new website") if can_add_more else _("Maximum {} custom sites reached").format(constants.MAX_CUSTOM_SITES))


# --- Main Dock Creation ---
def create_website_dock() -> Optional[QDockWidget]:
    global sidebar_dock, sidebar_webview, website_profile, button_container_layout, add_button_widget
    global home_button_widget
    global back_button, forward_button, refresh_button, nav_button_layout
    global custom_button_containers
    global website_main_layout, window_button

    if not _qt_available or QDockWidget is object or QWidget is object or QVBoxLayout is object or QHBoxLayout is object or QWebEngineView is object or QWebEngineProfile is object or QPushButton is object or mw is None:
        print("WS Error: Essential Qt/Anki components missing for dock creation.")
        return None

    existing_dock = mw.findChild(QDockWidget, constants.WEBSITE_DOCK_OBJECT_NAME)
    if existing_dock:
        sidebar_dock = existing_dock
        found_webview = sidebar_dock.findChild(QWebEngineView)
        if found_webview and isinstance(found_webview, QWebEngineView):
             sidebar_webview = found_webview
             if sidebar_webview.page() and sidebar_webview.page().profile():
                 current_profile = sidebar_webview.page().profile()
                 if not website_profile or website_profile != current_profile:
                     website_profile = current_profile
             if qconnect and not hasattr(sidebar_webview, '_urlChangedConnected_ws'):
                 qconnect(sidebar_webview.urlChanged, on_webview_url_changed)
                 sidebar_webview._urlChangedConnected_ws = True
        
        rebuild_custom_buttons_ui()
        print(f"WS Info: Re-using existing dock '{constants.WEBSITE_DOCK_OBJECT_NAME}'.")
        return sidebar_dock

    print(f"WS Info: Creating new dock '{constants.WEBSITE_DOCK_OBJECT_NAME}'.")
    try:
        if not constants.addon_path:
            print("WS Error: Addon path not set in constants. Cannot create profile directory.")
            return None

        profile_root = mw.pm.profileFolder() if mw and mw.pm else None
        if not profile_root:
            raise RuntimeError("Anki profile folder is unavailable")
        profile_dir = os.path.join(
            profile_root, "SmartStudy_Data", "web_profiles", "website")
        profile_name = f"profile_{constants.ADDON_NAME_LAUNCHER}_Website_v2"
        try:
            os.makedirs(profile_dir, exist_ok=True)
            website_profile = QWebEngineProfile(profile_name, mw)
            website_profile.setPersistentStoragePath(profile_dir)
            # Force: also keep session cookies (Moodle, Shibboleth/SSO logins),
            # so a login survives restarting Anki until the site ends it.
            website_profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
            website_profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
            from .web_accounts import keep_youtube_theme_fixed, share_login_from
            keep_youtube_theme_fixed(website_profile)
            share_login_from(website_profile)
            print(f"WS Info: Created/Using persistent profile: {profile_name} at {profile_dir}")
            if AdBlocker is not None:
                global ad_blocker
                ad_blocker = AdBlocker(website_profile)
                ad_blocker.enabled = _adblock_on()
                ad_blocker.allowed_sites = set(_load_website_state().get("adblock_off_sites", []))
                ad_blocker.start(os.path.dirname(os.path.dirname(profile_dir)))
                website_profile.setUrlRequestInterceptor(ad_blocker)
                _apply_youtube_pruner()
        except Exception as e_profile:
            print(f"WS Warn: Could not create persistent profile (Error: {e_profile}). Falling back to an off-the-record profile.")
            if mw: website_profile = QWebEngineProfile(mw)
            else: website_profile = QWebEngineProfile()
            if not website_profile.isOffTheRecord():
                 print("WS Warn: Fallback profile was not off-the-record. Using global default profile.")
                 website_profile = QWebEngineProfile.defaultProfile()
            else: print("WS Info: Using off-the-record (in-memory) profile.")

        if not website_profile:
            print("WS FATAL: Could not obtain any QWebEngineProfile.")
            return None
        try:
            website_profile.downloadRequested.connect(_on_download_requested)
        except Exception as e_dl:
            print(f"WS Warn: PDF downloads will not open in the browser: {e_dl}")

        sidebar_dock = QDockWidget(_("Web Sidebar"), mw)
        sidebar_dock.setObjectName(constants.WEBSITE_DOCK_OBJECT_NAME)
        sidebar_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        sidebar_dock.setMinimumWidth(350)
        
        title_bar_widget = QWidget(); title_bar_widget.setFixedHeight(0)
        sidebar_dock.setTitleBarWidget(title_bar_widget)
        
        sidebar_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable)

        container_widget = QWidget()
        main_layout = QVBoxLayout(container_widget)
        main_layout.setContentsMargins(0, 0, 0, 0); main_layout.setSpacing(0)
        website_main_layout = main_layout

        # Clean grey toolbar bar (matches the Notebook nav bar look).
        _pal = _toolbar_palette()
        toolbar_widget = QWidget()
        toolbar_widget.setObjectName("smartstudyWebToolbar")
        toolbar_widget.setStyleSheet(browser_chrome.toolbar())
        toolbar_layout = QVBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(6, 2, 6, 4); toolbar_layout.setSpacing(2)

        # Favourites: Home, saved sites, + (below the address row).
        button_container_layout = QHBoxLayout(); button_container_layout.setSpacing(1)
        button_container_layout.setContentsMargins(2, 0, 2, 0)
        toolbar_layout.addLayout(button_container_layout)

        add_button_widget = QPushButton("+")
        add_button_widget.setObjectName("AddButton")
        add_button_widget.setStyleSheet(_get_raised_icon_button_style())
        browser_chrome.set_icon(add_button_widget, "plus", 13)
        add_button_widget.setToolTip(_("Add new website"))
        add_button_widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        if qconnect: qconnect(add_button_widget.clicked, open_add_site_dialog)
        else: add_button_widget.setEnabled(False)

        home_button_widget = QPushButton(_("Home"))
        home_button_widget.setObjectName("HomeButton")
        home_button_widget.setStyleSheet(_get_raised_text_button_style())
        home_button_widget.setToolTip(_("Home (Smart Study Browser)"))
        home_button_widget.setCursor(Qt.CursorShape.PointingHandCursor)
        home_button_widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        nav_button_layout = QHBoxLayout(); nav_button_layout.setSpacing(1)
        _icon_style = _get_icon_button_style()
        back_button = QPushButton("←"); back_button.setToolTip(_("Go Back")); back_button.setEnabled(False)
        forward_button = QPushButton("→"); forward_button.setToolTip(_("Go Forward")); forward_button.setEnabled(False)
        refresh_button = QPushButton("↻"); refresh_button.setToolTip(_("Reload Page"))
        window_button = QPushButton("⧉"); window_button.setToolTip(_("Open in main window"))
        for _btn, _name in ((back_button, "back"), (forward_button, "forward"), (refresh_button, "reload"), (window_button, "layout")):
            _btn.setStyleSheet(_icon_style)
            browser_chrome.set_icon(_btn, _name)
        _apply_window_icon(window_button)
        nav_button_layout.addWidget(back_button); nav_button_layout.addWidget(forward_button)
        nav_button_layout.addWidget(refresh_button)
        global address_bar
        address_bar = _AddressBar()
        address_bar.setObjectName("smartstudyAddressBar")
        address_bar.setPlaceholderText(_("Search or enter address"))
        address_bar.setAccessibleName(_("Address bar"))
        address_bar.setToolTip(_("Address bar") + " (Ctrl+L)")
        address_bar.setClearButtonEnabled(False)  # a click selects everything, typing replaces it
        address_bar.setMinimumWidth(60)
        address_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        address_bar.setStyleSheet(_address_style())
        qconnect(address_bar.returnPressed, _address_entered)
        try:
            _state_path = _website_state_path()
            browser_history.set_folder(os.path.dirname(_state_path) if _state_path else None)
            _setup_suggestions(address_bar)
        except Exception as e_sugg:
            print(f"WS Warn: no address suggestions: {e_sugg}")
        nav_button_layout.addSpacing(4)
        nav_button_layout.addWidget(address_bar, 1)
        nav_button_layout.addSpacing(4)
        external_button = QPushButton("↗")
        external_button.setObjectName("smartstudyOpenBrowser")
        external_button.setStyleSheet(_icon_style)
        browser_chrome.set_icon(external_button, "external")
        external_button.setToolTip(_("Open in browser"))
        external_button.setAccessibleName(_("Open in browser"))
        qconnect(external_button.clicked, open_current_in_browser)
        options_button = QPushButton("⚙")
        options_button.setObjectName("smartstudyBrowserOptions")
        options_button.setStyleSheet(_icon_style)
        browser_chrome.set_icon(options_button, "options")
        options_button.setToolTip(_("Search engine and ad blocker"))
        options_button.setAccessibleName(_("Search engine and ad blocker"))
        options_menu = QMenu(options_button)
        qconnect(options_menu.aboutToShow, lambda: _fill_options_menu(options_menu))
        options_button.setMenu(options_menu)
        nav_button_layout.addWidget(options_button)
        nav_button_layout.addWidget(external_button)
        nav_button_layout.addWidget(window_button)
        toolbar_layout.insertLayout(0, nav_button_layout)  # address row above the favourites
        main_layout.addWidget(toolbar_widget)
        global load_bar
        load_bar = browser_chrome.LoadBar(container_widget)
        main_layout.addWidget(load_bar)
        if window_button:
            # One button for where the browser sits: sidebar, split, main window, own window.
            window_button.setToolTip(_("Browser layout"))
            window_button.setAccessibleName(_("Browser layout"))
            layout_menu = QMenu(window_button)
            qconnect(layout_menu.aboutToShow, lambda: browser_layout.fill_menu(layout_menu))
            window_button.setMenu(layout_menu)

        fallback = QWidget(container_widget)
        fallback.setObjectName("smartstudySearchHelp")
        hint_layout = QVBoxLayout(fallback)
        hint_layout.setContentsMargins(12, 10, 12, 10)
        hint_layout.setSpacing(8)
        hint = QLabel(_("Google is having trouble loading or requests verification. You can try DuckDuckGo instead. Home stays unchanged."))
        hint.setWordWrap(True)
        hint.setMinimumWidth(0)
        hint.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        hint_layout.addWidget(hint)
        actions = QHBoxLayout()
        switch_button = QPushButton(_("Try DuckDuckGo"))
        dismiss_button = QPushButton("×")
        dismiss_button.setAccessibleName(_("Dismiss"))
        dismiss_button.setToolTip(_("Dismiss"))
        dismiss_button.setFixedWidth(28)
        actions.addWidget(switch_button)
        actions.addStretch(1)
        actions.addWidget(dismiss_button)
        hint_layout.addLayout(actions)
        fallback.setStyleSheet(_search_help_style())
        fallback.hide()
        global search_help, tab_bar, tab_stack
        search_help = fallback
        def switch_search():
            if sidebar_webview is not None:
                load_url_in_webview(sidebar_webview, duckduckgo_url(sidebar_webview.url().toString()))
        def dismiss_hint():
            if sidebar_webview is not None:
                sidebar_webview._smartstudy_dismissed_url = sidebar_webview.url().toString()
            fallback.hide()
        qconnect(switch_button.clicked, switch_search)
        qconnect(dismiss_button.clicked, dismiss_hint)

        tab_row = QWidget()
        tab_row.setObjectName("smartstudyWebTabs")
        tab_row.setStyleSheet(_tab_row_style())
        tab_row_layout = QHBoxLayout(tab_row)
        tab_row_layout.setContentsMargins(6, 5, 6, 1); tab_row_layout.setSpacing(2)
        tab_bar = browser_chrome.Tabs(tab_row)
        tab_row.installEventFilter(tab_bar)
        tab_bar.on_refit = _show_close_buttons
        tab_bar.setDocumentMode(True)
        tab_bar.setExpanding(False)
        tab_bar.setMovable(True)
        # With many tabs they all get narrower (down to their icon), as in any browser.
        tab_bar.setElideMode(Qt.TextElideMode.ElideRight)
        tab_bar.setDrawBase(False)
        tab_bar.setIconSize(QSize(14, 14))
        tab_bar.installEventFilter(_middle_click)
        tab_row_layout.addWidget(tab_bar, 0)
        new_tab_button = QPushButton("+")
        new_tab_button.setObjectName("smartstudyNewTab")
        new_tab_button.setStyleSheet(_get_icon_button_style())
        browser_chrome.set_icon(new_tab_button, "plus")
        new_tab_button.setToolTip(_("New tab") + " (Ctrl+T)")
        new_tab_button.setAccessibleName(_("New tab"))
        qconnect(new_tab_button.clicked, lambda: new_tab(_home_url()))
        tab_row_layout.addWidget(new_tab_button)
        tab_row_layout.addStretch(1)  # the + sits right after the last tab
        groups_button = QPushButton("▤")
        groups_button.setObjectName("smartstudyTabGroups")
        groups_button.setStyleSheet(_get_icon_button_style())
        browser_chrome.set_icon(groups_button, "groups")
        groups_button.setToolTip(_("Tab groups"))
        groups_button.setAccessibleName(_("Tab groups"))
        groups_menu = QMenu(groups_button)
        qconnect(groups_menu.aboutToShow, lambda: browser_features.fill_groups_menu(groups_menu))
        groups_button.setMenu(groups_menu)
        tab_row_layout.addWidget(groups_button)
        main_layout.insertWidget(0, tab_row)  # tabs on top, like in any browser
        main_layout.addWidget(fallback)
        tab_stack = QStackedWidget()
        tab_stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout.addWidget(tab_stack)
        global pip_placeholder, browser_container
        pip_placeholder = QWidget()
        pip_layout = QVBoxLayout(pip_placeholder)
        pip_layout.addStretch(1)
        pip_label = QLabel(_("This video plays in picture in picture."))
        pip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pip_label.setWordWrap(True)
        pip_layout.addWidget(pip_label)
        pip_back = QPushButton(_("Back to the browser"))
        qconnect(pip_back.clicked, lambda: browser_features.close_pip(show_browser=True))
        pip_layout.addWidget(pip_back, 0, Qt.AlignmentFlag.AlignCenter)
        pip_layout.addStretch(1)
        tab_stack.addWidget(pip_placeholder)
        browser_container = container_widget
        qconnect(tab_bar.currentChanged, _on_tab_changed)
        qconnect(tab_bar.tabCloseRequested, close_tab)
        qconnect(tab_bar.tabMoved, lambda *_a: _schedule_save_tabs())
        _restore_tabs()

        if qconnect:
             qconnect(home_button_widget.clicked, lambda: load_url_in_webview(sidebar_webview, _home_url()))
        else:
             home_button_widget.setEnabled(False)

        button_container_layout.addWidget(home_button_widget)
        button_container_layout.addWidget(add_button_widget)
        button_container_layout.addStretch(1)
        rebuild_custom_buttons_ui()

        # Navigation goes through the view and the button state is read from
        # the history after each URL change.  Connecting Python slots to the
        # page's Back/Forward QAction.changed signals crashed Anki (SIGSEGV
        # inside QWebEnginePagePrivate::updateNavigationActions) while searching.
        if qconnect and back_button and forward_button and refresh_button:
            qconnect(back_button.clicked, lambda: diagnostics.record('browser.back'))
            qconnect(forward_button.clicked, lambda: diagnostics.record('browser.forward'))
            qconnect(refresh_button.clicked, lambda: diagnostics.record('browser.reload'))
            qconnect(back_button.clicked, lambda: sidebar_webview and sidebar_webview.back())
            qconnect(forward_button.clicked, lambda: sidebar_webview and sidebar_webview.forward())
            qconnect(refresh_button.clicked, _reload_or_stop)

        sidebar_dock.setWidget(container_widget)
        sidebar_dock.setVisible(False)
        from .sidebar_widths import attach
        attach(mw, sidebar_dock, "website", lambda: website_window is not None)
        mw.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, sidebar_dock)
        browser_features.start()
        print(f"WS Info: New dock created and added successfully.")

    except Exception as e:
        print(f"WS FATAL: Error during new dock creation: {e}")
        traceback.print_exc()
        if sidebar_dock: sidebar_dock.deleteLater(); sidebar_dock = None
        sidebar_webview = None; website_profile = None; button_container_layout = None; nav_button_layout = None
        add_button_widget = None; home_button_widget = None
        back_button = None; forward_button = None; refresh_button = None
        custom_button_containers.clear()
    return sidebar_dock


# --- Tabs ---
def _tab_row_style() -> str:
    return browser_chrome.tab_row()


if FilteringPage is not None:
    _PageBase = FilteringPage
else:
    _PageBase = QWebEnginePage if QWebEnginePage is not object else object


class _TabPage(_PageBase):
    """Links that want a new window or tab (middle click, Ctrl+click,
    target=_blank, "Open link in new tab") get a new tab."""

    def createWindow(self, kind):
        background = kind == QWebEnginePage.WebWindowType.WebBrowserBackgroundTab
        view = new_tab(None, background=background)
        return view.page() if view is not None else None

    def acceptNavigationRequest(self, url, nav_type, is_main_frame):
        view = getattr(self, "_ss_view", None)
        if is_main_frame and url.isLocalFile() and not _is_local_pdf(url):
            return False  # of the files on this computer, only PDFs are shown
        if is_main_frame and view is not None and browser_features.focus_blocks(url):
            QTimer.singleShot(0, lambda: browser_features.show_blocked(view, url))
            return False
        return super().acceptNavigationRequest(url, nav_type, is_main_frame)

    def javaScriptConsoleMessage(self, level, message, line, source):  # type: ignore[override]
        try:
            if browser_passwords.console_message(self, message):
                return  # a sent login, reported by our isolated page script
        except Exception as e:
            print(f"Smart Study passwords: {e}")
        try:
            super().javaScriptConsoleMessage(level, message, line, source)
        except Exception:
            pass


def _make_tab_view():
    view = QWebEngineView()
    view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    if FilteringPage is not None:
        page = _TabPage(website_profile, view, ad_blocker)
    else:
        page = _TabPage(website_profile, view)
    view.setPage(page)
    page._ss_view = view
    diagnostics.attach_webview(view)
    settings = view.settings()
    # PluginsEnabled + PdfViewerEnabled: PDFs show in the tab (Chromium's
    # built-in viewer) instead of being offered as a download.
    attrs_to_set = [
        ("JavascriptEnabled", True),
        ("LocalStorageEnabled", True),
        ("ScrollAnimatorEnabled", True),
        ("PluginsEnabled", True),
        ("PdfViewerEnabled", True),
        ("FullScreenSupportEnabled", True), ]
    for name, value in attrs_to_set:
        attr = getattr(QWebEngineSettings.WebAttribute, name, None)
        if attr is None:
            continue
        try: settings.setAttribute(attr, value)
        except (AttributeError, TypeError): pass
    view._smartstudy_dismissed_url = None

    def offer_fallback(url=None, ok=True):
        if sidebar_webview is not view or search_help is None:
            return
        current = view.url().toString()
        if url is not None:
            view._smartstudy_dismissed_url = None
        search_help.setVisible(current != view._smartstudy_dismissed_url and needs_search_help(current, ok))
    def inspect_loaded_page(ok):
        offer_fallback(ok=ok)
        current = view.url().toString()
        if not ok or not is_google_url(current):
            return
        # One small check after a Google load, not a polling loop or a
        # text scan of search results that might merely discuss CAPTCHAs.
        def inspected(blocked):
            if sidebar_webview is not view or search_help is None:
                return
            if current == view.url().toString() and current != view._smartstudy_dismissed_url:
                search_help.setVisible(needs_search_help(current, ok, bool(blocked)))
        view.page().runJavaScript("Boolean(document.querySelector('form[action*=\"/sorry/\"], #captcha-form, .g-recaptcha, iframe[src*=\"recaptcha/api2/anchor\"]'))", inspected)
    view._ss_loading, view._ss_progress = False, 0
    qconnect(view.loadStarted, lambda: _on_load(view, True, 0))
    qconnect(view.loadProgress, lambda pct: _on_load(view, pct < 100 and view._ss_loading, pct))
    qconnect(view.loadFinished, lambda *_a: _on_load(view, False, 100))
    qconnect(view.urlChanged, offer_fallback)
    qconnect(view.loadFinished, inspect_loaded_page)
    qconnect(view.urlChanged, lambda *_a: _sync_nav_buttons(view))
    qconnect(view.loadFinished, lambda *_a: _sync_nav_buttons(view))
    # Kept from the signals: asking a page that is waking up from Discarded
    # for its icon crashed Qt (WebContentsAdapter::icon).
    view._ss_title, view._ss_icon = "", None
    qconnect(view.titleChanged, lambda t: (setattr(view, "_ss_title", t), _update_tab_label(view),
                                           browser_history.set_title(view.url().toString(), t)))
    qconnect(view.iconChanged, lambda i: (setattr(view, "_ss_icon", i), _update_tab_label(view),
                                          browser_history.save_icon(view.url().toString(), i)))
    qconnect(view.loadFinished, lambda ok: _remember_visit(view, ok))
    qconnect(view.urlChanged, lambda url: sidebar_webview is view and on_webview_url_changed(url))
    qconnect(view.urlChanged, lambda *_a: show_address(view))
    view._urlChangedConnected_ws = True
    qconnect(view.urlChanged, lambda *_a: _schedule_save_tabs())
    qconnect(view.titleChanged, lambda *_a: _schedule_save_tabs())
    _keep_audio_playing(view)
    browser_features.setup_view(view)
    # Tabs not looked at for 10 minutes give their memory back; a tab playing
    # sound or shown in picture in picture is never unloaded.
    web_sleep.watch(view, discard_after=600, keep_awake=lambda: bool(getattr(view, "_ss_pip", False)))
    return view


def _on_load(view, loading: bool, percent: int) -> None:
    """Remembers how far a tab has loaded and shows it for the current one:
    the line under the bars fills, and Reload turns into Stop meanwhile."""
    try:
        if sip.isdeleted(view):
            return
        view._ss_loading, view._ss_progress = bool(loading), int(percent)
        if view is sidebar_webview:
            _show_load_state(view)
    except Exception as e:
        print(f"WS Info: load state: {e}")


def _show_load_state(view) -> None:
    loading = bool(getattr(view, "_ss_loading", False))
    if load_bar is not None and not sip.isdeleted(load_bar):
        load_bar.set_progress(getattr(view, "_ss_progress", 0), loading)
    if refresh_button is not None and not sip.isdeleted(refresh_button):
        want = "stop" if loading else "reload"
        if getattr(refresh_button, "_ss_icon_name", None) != want:
            browser_chrome.set_icon(refresh_button, want)
            refresh_button.setToolTip(_("Stop loading") if loading else _("Reload Page"))


def _reload_or_stop() -> None:
    view = sidebar_webview
    if view is None:
        return
    if getattr(view, "_ss_loading", False):
        view.stop()
    else:
        view.reload()


def new_tab(url: Optional[str] = None, background: bool = False, pending: Optional[Dict] = None,
            at_end: bool = False):
    """Open a tab (url None: the page fills it, e.g. a link's new window).
    pending {"url", "title"}: a tab that loads only when it is first shown."""
    if tab_bar is None or tab_stack is None:
        return None
    if tab_bar.count() >= MAX_TABS:
        tooltip(_("Up to {} tabs").format(MAX_TABS))
        return None
    view = _make_tab_view()
    index = tab_bar.count() if at_end or not tab_bar.count() else tab_bar.currentIndex() + 1
    tab_stack.addWidget(view)
    tab_bar.insertTab(index, (pending or {}).get("title") or _("New tab"))
    tab_bar.setTabData(index, view)
    view._ss_pending = (pending or {}).get("url")
    _default_tab_icon(index, view._ss_pending or url or "")
    close = QPushButton("×")
    close.setObjectName("smartstudyCloseTab")
    close.setFixedSize(16, 16)
    close.setCursor(Qt.CursorShape.PointingHandCursor)
    close.setToolTip(_("Close tab"))
    close.setAccessibleName(_("Close tab"))
    qconnect(close.clicked, lambda: close_tab(_tab_index(view)))
    tab_bar.setTabButton(index, QTabBar.ButtonPosition.RightSide, close)
    _show_close_buttons()
    if url:
        if url == "about:blank": view.setUrl(QUrl(url))
        else:
            view._ss_requested = url
            load_url_in_webview(view, url)
    _schedule_save_tabs()
    if not background:
        if tab_bar.currentIndex() == index:
            _on_tab_changed(index)  # the first tab became current before its data was set
        else:
            tab_bar.setCurrentIndex(index)
        if url and url != "about:blank":
            view.setFocus()
    return view


def close_tab(index: int) -> None:
    if tab_bar is None or tab_stack is None or tab_bar.count() <= 1:
        return
    view = _tab_view(index)
    if view is None:
        return
    if getattr(view, "_ss_pip", False):
        browser_features.close_pip()
    tab_stack.removeWidget(view)
    tab_bar.removeTab(index)  # emits currentChanged for the new tab
    _show_close_buttons()
    _schedule_save_tabs()
    try: view.setUrl(QUrl("about:blank"))
    except Exception: pass
    view.deleteLater()


def _tab_view(index: int):
    """The view of a tab; the stack's order does not follow moved tabs."""
    return tab_bar.tabData(index) if tab_bar is not None and index >= 0 else None


def _tab_index(view) -> int:
    for index in range(tab_bar.count() if tab_bar is not None else 0):
        if tab_bar.tabData(index) is view:
            return index
    return -1


def all_tab_views() -> list:
    return [_tab_view(i) for i in range(tab_bar.count())] if tab_bar is not None else []


def _show_close_buttons() -> None:
    """The last tab cannot be closed, so it shows no ×. While the tabs are narrow only
    the current one keeps its ×, so the others have room for their title
    (a middle click closes any tab)."""
    count = tab_bar.count()
    roomy = tab_bar.roomy() if hasattr(tab_bar, "roomy") else count <= 4
    fits = tab_bar.close_fits() if hasattr(tab_bar, "close_fits") else True  # icon-sized tabs: middle click or Ctrl+W
    for index in range(count):
        button = tab_bar.tabButton(index, QTabBar.ButtonPosition.RightSide)
        if button is not None:
            button.setVisible(count > 1 and (roomy or (fits and index == tab_bar.currentIndex())))


def _step_tab(step: int) -> None:
    if tab_bar is not None and tab_bar.count() > 1:
        tab_bar.setCurrentIndex((tab_bar.currentIndex() + step) % tab_bar.count())


def _on_tab_changed(index: int, load: bool = True) -> None:
    global sidebar_webview
    if tab_stack is None or index < 0:
        return
    view = _tab_view(index)
    if view is None:
        return
    target = pip_placeholder if getattr(view, "_ss_pip", False) and pip_placeholder is not None else view
    old = tab_stack.currentWidget()
    if old is not None and old is not target:
        try:  # cover with a picture of the old tab, which then fades out
            from .smooth_ui import crossfade
            crossfade(tab_stack, old)
        except Exception as e:
            print(f"WS Info: no tab fade: {e}")
    tab_stack.setCurrentWidget(target)
    sidebar_webview = view
    if load:
        _load_pending(view)
    _schedule_save_tabs()
    if search_help is not None:
        search_help.hide()
    _sync_nav_buttons(view)
    _show_close_buttons()
    _show_load_state(view)
    on_webview_url_changed(view.url())
    if address_bar is not None and not sip.isdeleted(address_bar):
        address_bar.setModified(False)
    show_address(view)


def show_browser() -> bool:
    """Make the browser visible (sidebar or main window); False if it
    cannot be created."""
    global sidebar_dock
    if sidebar_dock is None:
        sidebar_dock = create_website_dock()
    if sidebar_dock is None or tab_bar is None:
        return False
    if website_window is None and not sidebar_dock.isVisible():
        sidebar_dock.show()
        sidebar_dock.raise_()
        _notify_launcher_dock_opened()
    browser_layout.bring_forward()  # only when it is its own window
    return True


def _is_blank(view) -> bool:
    return (view is not None and view.url().toString() in ("", "about:blank")
            and not getattr(view, "_ss_requested", None) and not getattr(view, "_ss_pending", None))


def detach_view(view) -> None:
    """Take a tab's view out of the browser (for picture in picture)."""
    if tab_stack is None:
        return
    tab_stack.removeWidget(view)
    view._ss_pip = True
    if sidebar_webview is view and pip_placeholder is not None:
        tab_stack.setCurrentWidget(pip_placeholder)
    _update_tab_label(view)


def attach_view(view, show: bool = False) -> None:
    """Put a view back after picture in picture."""
    if tab_stack is None or sip.isdeleted(view):
        return
    view._ss_pip = False
    tab_stack.addWidget(view)
    index = _tab_index(view)
    if sidebar_webview is view:
        tab_stack.setCurrentWidget(view)
    _update_tab_label(view)
    if show and index >= 0 and show_browser():
        tab_bar.setCurrentIndex(index)


def open_tab_entries() -> List[Dict[str, str]]:
    """The open tabs as {"url", "title"} (for groups and the next start)."""
    entries = []
    for view in all_tab_views():
        if view is None:
            continue
        url = getattr(view, "_ss_pending", None) or view.url().toString()
        if not _restorable(url):
            continue
        index = _tab_index(view)
        entries.append({"url": url, "title": tab_bar.tabText(index)[:200] if index >= 0 else ""})
    return entries


def open_tabs(entries: List[Dict], replace: bool = False) -> None:
    """Open saved tabs; only the first one loads right away."""
    entries = [e for e in entries if isinstance(e, dict) and _restorable(e.get("url", ""))]
    if not entries or not show_browser():
        return
    old = all_tab_views() if replace else []
    room = MAX_TABS - (0 if replace else tab_bar.count())
    if len(entries) > room:
        tooltip(_("Up to {} tabs").format(MAX_TABS))
        entries = entries[:max(1, room)]
    first = None
    for entry in entries:
        view = new_tab(None, background=True, pending={"url": entry["url"], "title": entry.get("title", "")}, at_end=True)
        if view is not None and first is None:
            first = view
    if first is not None:
        tab_bar.setCurrentIndex(_tab_index(first))
    for view in old:
        index = _tab_index(view)
        if index >= 0:
            close_tab(index)


def _restore_tabs() -> None:
    saved = _load_website_state().get("open_tabs")
    entries = saved.get("tabs") if isinstance(saved, dict) else None
    if not browser_features.load_settings()["restore_tabs"] or not isinstance(entries, list) or not entries:
        _new_home_tab()
        return
    for entry in entries[:MAX_TABS]:
        if isinstance(entry, dict) and _restorable(entry.get("url", "")):
            new_tab(None, background=True, pending={"url": entry["url"], "title": str(entry.get("title", ""))}, at_end=True)
    if tab_bar.count() == 0:
        _new_home_tab()
        return
    current = saved.get("current") if isinstance(saved.get("current"), int) else 0
    current = min(max(0, current), tab_bar.count() - 1)
    if tab_bar.currentIndex() == current:
        _on_tab_changed(current)
    else:
        tab_bar.setCurrentIndex(current)


def _new_home_tab() -> None:
    """The first tab: no renderer until the browser is shown or another
    page is opened in it."""
    new_tab(None, background=True, pending={"url": _home_url(), "title": _("New tab")}, at_end=True)
    _on_tab_changed(tab_bar.count() - 1, load=False)


def _load_pending(view) -> None:
    if view is not None and getattr(view, "_ss_pending", None):
        url, view._ss_pending = view._ss_pending, None
        view._ss_requested = url
        load_url_in_webview(view, url)


_save_tabs_timer = None


def _schedule_save_tabs() -> None:
    global _save_tabs_timer
    if tab_bar is None or QTimer is object:
        return
    if _save_tabs_timer is None:
        _save_tabs_timer = QTimer()
        _save_tabs_timer.setSingleShot(True)
        _save_tabs_timer.setInterval(1500)
        _save_tabs_timer.timeout.connect(_save_tabs)
    _save_tabs_timer.start()


def _save_tabs() -> None:
    if tab_bar is None:
        return
    entries = open_tab_entries()
    current = sidebar_webview
    urls = [e["url"] for e in entries]
    current_url = (getattr(current, "_ss_pending", None) or current.url().toString()) if current is not None else ""
    state = _load_website_state()
    state["open_tabs"] = {"tabs": entries, "current": urls.index(current_url) if current_url in urls else 0}
    _save_website_state(state)


def _default_tab_icon(index: int, url: str = "") -> None:
    """A globe (or a sheet for PDFs) until the page brings its own icon, so a
    narrow tab is never blank."""
    try:
        name = "file" if url.lower().split("#")[0].split("?")[0].endswith(".pdf") else "globe"
        icon = browser_history.load_icon(url) or browser_chrome.icon(name, 14)  # the site's icon from last time
        if icon is not None:
            tab_bar.setTabIcon(index, icon)
    except Exception as e:
        print(f"WS Info: tab icon: {e}")


def _update_tab_label(view) -> None:
    if tab_bar is None or sip.isdeleted(view):
        return
    index = _tab_index(view)
    if index < 0:
        return
    if getattr(view, "_ss_pending", None) or web_sleep.state(view.page()) == "Discarded":
        return  # keeps its title while it is not loaded
    url = view.url()
    title = view._ss_title or url.host() or _("New tab")
    if url.toString() in ("", "about:blank"):
        title = _("New tab")
    if getattr(view, "_ss_pip", False):
        title = "⧉ " + title
    tab_bar.setTabText(index, title)
    tab_bar.setTabToolTip(index, title)
    if view._ss_icon is not None and not view._ss_icon.isNull():
        tab_bar.setTabIcon(index, view._ss_icon)
    elif tab_bar.tabIcon(index).isNull() or _is_local_pdf(url):
        _default_tab_icon(index, url.toString())


def _sync_nav_buttons(view) -> None:
    # Deferred, so the page has finished updating its history.
    def apply():
        if sidebar_webview is not view or sip.isdeleted(view):
            return
        buttons = (back_button, forward_button)
        if any(b is None or sip.isdeleted(b) for b in buttons):
            return
        history = view.history()
        back_button.setEnabled(history.canGoBack())
        forward_button.setEnabled(history.canGoForward())
    QTimer.singleShot(0, apply)


class _AudioKeeper(QObject):
    """Keeps sound (YouTube, podcasts, …) playing while the browser is hidden,
    e.g. when another sidebar such as the AI chat opens.  Qt marks a hidden
    view's page invisible and Chromium then throttles it, which stalls
    streams.  Only a page that is playing sound stays "visible", and only
    until it has been silent for a while, so a hidden browser costs nothing."""

    SILENCE_MS = 30000

    def __init__(self, view):
        super().__init__(view)
        self.view = view
        self.silence = QTimer(self)
        self.silence.setSingleShot(True)
        self.silence.setInterval(self.SILENCE_MS)
        qconnect(self.silence.timeout, self._let_sleep)
        qconnect(view.page().recentlyAudibleChanged, self._audible_changed)
        view.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj is self.view and event.type() == QEvent.Type.Hide:
            # After Qt has propagated the hidden state to the page.
            QTimer.singleShot(0, self._keep_awake)
        return False

    def _keep_awake(self):
        if sip.isdeleted(self.view) or self.view.isVisible():
            return
        page = self.view.page()
        if page is None or not page.recentlyAudible():
            return
        page.setVisible(True)
        try:
            page.setLifecycleState(QWebEnginePage.LifecycleState.Active)
        except (AttributeError, TypeError):
            pass  # older Qt builds; visibility alone is the important part

    def _audible_changed(self, audible):
        if audible:
            self.silence.stop()
        elif not sip.isdeleted(self.view) and not self.view.isVisible():
            self.silence.start()

    def _let_sleep(self):
        if sip.isdeleted(self.view) or self.view.isVisible():
            return
        page = self.view.page()
        if page is not None and not page.recentlyAudible():
            page.setVisible(False)


def _keep_audio_playing(view) -> None:
    try:
        view._smartstudy_audio = _AudioKeeper(view)
    except Exception as e:
        print(f"WS Warn: background audio not available: {e}")


def on_webview_url_changed(url: QUrl):
    if not sidebar_webview or QUrl is object or not _qt_available: return
    current_url_str = url.toString()
    if current_url_str and current_url_str != "about:blank" and not current_url_str.startswith("data:text/html"):
        save_last_opened_url(current_url_str)

# --- Embedded View (inside the Anki main window) ---
from . import embedded_window


def toggle_website_window():
    """Toggle the embedded main-window view on/off (the ⧉ button)."""
    if website_window is not None and embedded_window.is_active():
        close_website_window()
    else:
        open_website_window()


def open_website_window():
    """Embed the whole dock body into Anki's main content area.

    We borrow the dock's *content widget* (its own toolbar + the webview),
    not just the webview, so the navigation bar – including the ⧉ button –
    stays visible and provides the way back to the sidebar. No extra header
    bar is drawn (show_header=False).
    """
    global website_window, sidebar_dock, sidebar_webview, website_embedded_content
    if not _qt_available or QWidget is object:
        return

    if sidebar_dock is None:
        sidebar_dock = create_website_dock()
    if not sidebar_webview or not sidebar_dock:
        if callable(showWarning):
            showWarning(_("Sidebar Browser not initialized."))
        return

    # Already embedded → nothing to do.
    if website_window is not None or embedded_window.is_active():
        return

    # Make sure a real page is loaded (not about:blank).
    try:
        cur = sidebar_webview.url().toString() if QUrl is not object else ""
    except Exception:
        cur = ""
    if getattr(sidebar_webview, "_ss_pending", None):
        _load_pending(sidebar_webview)
    elif (not cur or cur == "about:blank" or cur.startswith("data:text/html")) and _is_blank(sidebar_webview):
        load_url_in_webview(sidebar_webview, _home_url())

    # Detach the dock's content widget and hide the (now empty) dock.
    content = sidebar_dock.widget()
    if content is None:
        return
    content.setParent(None)
    sidebar_dock.hide()

    ok = embedded_window.embed(content, close_website_window, _("Web"),
                               show_header=False)
    if not ok:
        # Embedding failed – put the content back and abort.
        sidebar_dock.setWidget(content)
        sidebar_dock.show()
        sidebar_dock.raise_()
        return
    website_embedded_content = content
    website_window = True  # marker: an embedded view is active
    if window_button is not None:
        try:
            window_button.setToolTip(_("Browser layout"))
        except Exception:
            pass
        # Flip the icon to the "close window" state (frame with a dash).
        _apply_window_icon(window_button, active=True)


def close_website_window():
    """Leave the embedded view and return the content to the dock."""
    global website_window, sidebar_dock, website_embedded_content
    content = website_embedded_content
    if content is not None and sidebar_dock is not None:
        try:
            sidebar_dock.setWidget(content)  # reparents out of the embed container
        except Exception:
            pass
    embedded_window.restore()
    website_embedded_content = None
    website_window = None
    if window_button is not None:
        try:
            window_button.setToolTip(_("Browser layout"))
        except Exception:
            pass
        # Restore the normal "open in main window" icon.
        _apply_window_icon(window_button, active=False)
    if sidebar_dock is not None:
        try:
            sidebar_dock.show()
            sidebar_dock.raise_()
        except Exception:
            pass


# --- Toggle Function ---
def toggle_website_dock():
    global sidebar_dock, sidebar_webview
    if not _qt_available:
        if callable(showWarning): showWarning(_("Website Sidebar: Qt components not available.")); return

    if sidebar_dock is None:
        sidebar_dock = create_website_dock()

    if sidebar_dock is None or QDockWidget is object:
        if callable(showWarning): showWarning(_("{}:\nCould not create or find the website sidebar.").format(constants.ADDON_NAME_WEBSITE)); return
    
    if sidebar_webview is None:
        temp_webview = sidebar_dock.findChild(QWebEngineView)
        if temp_webview and isinstance(temp_webview, QWebEngineView):
            sidebar_webview = temp_webview
            if qconnect and not hasattr(sidebar_webview, '_urlChangedConnected_ws'):
                 qconnect(sidebar_webview.urlChanged, on_webview_url_changed)
                 sidebar_webview._urlChangedConnected_ws = True
    try:
        if sidebar_dock.isVisible():
            sidebar_dock.hide()
        else:
            rebuild_custom_buttons_ui() 

            sidebar_dock.show()
            sidebar_dock.raise_()

            if getattr(sidebar_webview, "_ss_pending", None):
                _load_pending(sidebar_webview)
            elif _is_blank(sidebar_webview):
                load_url_in_webview(sidebar_webview, _home_url())
            elif not sidebar_webview:
                print("WS Warn: Sidebar webview not available on toggle show.")
    except Exception as e:
        print(f"WS Error toggling dock visibility: {e}")
        traceback.print_exc()

# --- Theme Refresh Function ---
def _search_help_style():
    c = _toolbar_palette()
    return f"""
    QWidget#smartstudySearchHelp {{ background:{c['bar']}; border:1px solid {c['line']}; border-radius:8px; }}
    QWidget#smartstudySearchHelp QLabel {{ background:transparent; color:{c['text']}; border:0; }}
    QWidget#smartstudySearchHelp QPushButton {{ background:{c['select_bg']}; color:{c['text']}; border:1px solid {c['line']}; border-radius:6px; padding:5px; min-height:18px; }}
    QWidget#smartstudySearchHelp QPushButton:hover {{ background:{c['hover']}; }}
    QWidget#smartstudySearchHelp QPushButton:focus {{ border:1px solid {c['text']}; }}
    """


def refresh_website_theme() -> None:
    """Re-apply the bars' colours and icons after a colour-theme change."""
    icon_style = _get_icon_button_style()
    if search_help is not None:
        search_help.setStyleSheet(_search_help_style())
    if address_bar is not None and not sip.isdeleted(address_bar):
        address_bar.setStyleSheet(_address_style())
        completer = getattr(address_bar, "_ss_completer", None)
        if completer is not None:
            completer.popup().setStyleSheet(_suggestion_style())
    if sidebar_dock is not None:
        row = sidebar_dock.findChild(QWidget, "smartstudyWebTabs")
        if row is not None:
            row.setStyleSheet(_tab_row_style())
        for name in ("smartstudyOpenBrowser", "smartstudyBrowserOptions", "smartstudyNewTab", "smartstudyTabGroups"):
            button = sidebar_dock.findChild(QPushButton, name)
            if button is not None:
                button.setStyleSheet(icon_style)
                browser_chrome.refresh_icon(button)
    if home_button_widget is not None:
        try: home_button_widget.setStyleSheet(_get_raised_text_button_style())
        except Exception: pass
    if add_button_widget is not None:
        try:
            add_button_widget.setStyleSheet(_get_raised_icon_button_style())
            browser_chrome.refresh_icon(add_button_widget)
        except Exception: pass
    for _btn in (back_button, forward_button, refresh_button, window_button):
        if _btn is not None:
            try:
                _btn.setStyleSheet(icon_style)
                browser_chrome.refresh_icon(_btn)
            except Exception: pass
    if window_button is not None:
        # Keep the "close window" variant while the embedded view is active.
        try: _apply_window_icon(window_button, active=(website_window is not None))
        except Exception: pass
    try:
        if mw is not None:
            bar = mw.findChild(QWidget, "smartstudyWebToolbar")
            if bar is not None:
                bar.setStyleSheet(browser_chrome.toolbar())
        if load_bar is not None and not sip.isdeleted(load_bar):
            load_bar.update()
    except Exception: pass
    # Rebuild custom site buttons so their styles refresh too.
    try: rebuild_custom_buttons_ui()
    except Exception: pass

# --- Cleanup Function ---
def cleanup_website_sidebar():
    global sidebar_dock, sidebar_webview, website_profile, button_container_layout, nav_button_layout, add_button_widget
    global home_button_widget
    global back_button, forward_button, refresh_button
    global custom_button_containers
    global website_main_layout, website_window, window_button
    global tab_bar, tab_stack, search_help, pip_placeholder, browser_container
    global load_bar
    load_bar = None
    try: browser_history.save()
    except Exception: pass

    diagnostics.record('browser.cleanup')
    try: browser_layout.cleanup()
    except Exception as e: print(f"WS Info: browser window not reset: {e}")
    try: browser_features.stop()
    except Exception as e: print(f"WS Info: browser extras not stopped: {e}")
    if _save_tabs_timer is not None and _save_tabs_timer.isActive():
        _save_tabs_timer.stop()
        _save_tabs()

    # Only close the embedded Browser owned by this module.  A Notebook or
    # Mind Map may be the active embedded tool; restoring its container here
    # would leave that tool's own state flag out of sync with the main layout.
    if website_window is not None:
        try: close_website_window()
        except Exception:
            try: embedded_window.restore()
            except Exception: pass
        website_window = None

    # Anki's main window survives profile switches. Destroy the Qt objects so
    # a page, cookie store, or signal from the old profile cannot remain live.
    for view in all_tab_views() or [sidebar_webview]:
        if view is None:
            continue
        try: view.setUrl(QUrl("about:blank"))
        except Exception: pass
        try: view.deleteLater()
        except Exception: pass
    tab_bar = None; tab_stack = None; search_help = None; pip_placeholder = None; browser_container = None
    global address_bar
    address_bar = None
    if sidebar_dock is not None:
        try: mw.removeDockWidget(sidebar_dock)
        except Exception: pass
        try: sidebar_dock.deleteLater()
        except Exception: pass
    if website_profile is not None:
        try: website_profile.setUrlRequestInterceptor(None)
        except Exception: pass
        try: website_profile.deleteLater()
        except Exception: pass
    global ad_blocker
    ad_blocker = None

    sidebar_dock = None; sidebar_webview = None; website_profile = None; button_container_layout = None; nav_button_layout = None
    add_button_widget = None; home_button_widget = None; back_button = None; forward_button = None; refresh_button = None
    window_button = None; website_main_layout = None
    custom_button_containers.clear()
    print(f"{constants.ADDON_NAME_WEBSITE}: Cleaned up references.")

def search_in_sidebar(text: str):
    """
    1. Öffnet die Sidebar (falls geschlossen).
    2. Googelt den Text.

    IMPORTANT: This function must NOT be called synchronously from within a
    context-menu callback while the WebView is still processing the event.
    Doing so can create a QWebEngineView / addDockWidget call on top of an
    active WebEngine event, which causes a silent C++ crash with no Python
    traceback. Always defer via QTimer.singleShot(0, …) instead.
    """
    if not text or not mw or not getattr(mw, "col", None): return
    collection = mw.col
    # Defer the actual work to the next event-loop tick so that Qt has fully
    # closed the context menu and the WebView is no longer in an active event
    # handler. This prevents the silent C++ crash.
    if QTimer is not object:
        QTimer.singleShot(0, lambda: _execute_search_in_sidebar(text)
                          if getattr(mw, "col", None) is collection else None)
    else:
        _execute_search_in_sidebar(text)


def _notify_launcher_dock_opened():
    """Ask the launcher sidebar to highlight the Website icon.

    The search path opens the dock without going through the launcher button,
    so the launcher never wires up its visibility listener on its own. Poke it
    here so the icon reflects the now-open dock (no-op if the launcher or its
    hook isn't available)."""
    try:
        import importlib
        pkg = importlib.import_module(__package__)
        inst = getattr(pkg, "sidebar_widget_instance", None)
        if inst is not None and hasattr(inst, "sync_dock_button"):
            inst.sync_dock_button(constants.WEBSITE_DOCK_OBJECT_NAME)
    except Exception as e:
        print(f"WS Info: could not notify launcher about dock open: {e}")


def _execute_search_in_sidebar(text: str):
    """Internal helper – runs the actual search after the event loop has ticked."""
    if not text: return

    search_url = browser_search.search_url(_search_engine(), text)

    global sidebar_dock, sidebar_webview
    try:
        if not sidebar_dock:
            sidebar_dock = create_website_dock()

        if sidebar_dock:
            if not sidebar_dock.isVisible():
                sidebar_dock.show()
            sidebar_dock.raise_()
            _notify_launcher_dock_opened()

            if sidebar_webview:
                load_url_in_webview(sidebar_webview, search_url)
            else:
                if callable(showWarning): showWarning(_("Sidebar Browser not initialized."))
    except Exception as e:
        print(f"WS Search Error: {e}")
        import traceback; traceback.print_exc()

def on_context_menu(webview, menu):
    """
    Wird aufgerufen, wenn man Rechtsklick im Editor oder Reviewer macht.
    Fügt die "Search in Sidebar" Option hinzu, wenn Text markiert ist.

    NOTE: search_in_sidebar() uses QTimer.singleShot(0, …) internally so
    that dock creation / WebEngine operations happen after this callback
    returns – avoiding the silent C++ crash that occurs when a new
    QWebEngineView is added while the current WebView is still processing
    the context-menu event.
    """
    try:
        # The context-menu hooks remain registered for Anki's lifetime.
        import importlib
        package = importlib.import_module(__package__)
        if not getattr(package, "addon_settings", {}).get("website_viewer_enabled", True):
            return
        selected_text = webview.selectedText()
    except (AttributeError, RuntimeError):
        return

    if selected_text and len(selected_text.strip()) > 0:
        display_text = (selected_text[:20] + '...') if len(selected_text) > 20 else selected_text

        action = menu.addAction(_("Search '{}' in Sidebar").format(display_text))

        # Capture selected_text in the closure explicitly to avoid late-binding issues.
        qconnect(action.triggered, lambda checked=False, t=selected_text: search_in_sidebar(t))
        browser_action = menu.addAction(_("Search '{}' in browser").format(display_text))
        qconnect(browser_action.triggered, lambda checked=False, t=selected_text: search_in_browser(t))

# --- Hooks registrieren ---
if gui_hooks:
    gui_hooks.editor_will_show_context_menu.append(on_context_menu)
    gui_hooks.webview_will_show_context_menu.append(on_context_menu)

print(f"{constants.ADDON_NAME_WEBSITE}: Module Loaded (Updated with Search)")
