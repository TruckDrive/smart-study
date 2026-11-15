# -*- coding: utf-8 -*-
"""
SmartStudy – AI Assistant Sidebar
=================================
ChatGPT, Claude, Gemini and NotebookLM as websites, used with your own account.
"""

try:
    from .quiet import ignored as _ignored
except ImportError:  # the module is loaded on its own (tests)
    def _ignored(*_args):
        pass

import os
import traceback
from typing import Any, Optional

# ── Local imports ─────────────────────────────────────────────────────────────
try:
    from . import constants
except ImportError:
    class MockConstants:
        ADDON_NAME_LAUNCHER = "Launcher_Sidebar"
        addon_path = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else "."
    constants = MockConstants()  # type: ignore[assignment]

try:
    from .locales import _
except ImportError:
    def _(t):  # type: ignore[misc]
        return t

# ── PyQt imports ──────────────────────────────────────────────────────────────
_qt_ok = False
try:
    from aqt.qt import QWidget, QDockWidget, Qt
    _qt_ok = True
    print("AI Assistant: Qt6 loaded OK")
except ImportError as _e:
    print(f"AI Assistant: Qt import FAILED – {_e}")
    QWidget = QDockWidget = Qt = object  # type: ignore[misc,assignment]

# ── Anki imports ──────────────────────────────────────────────────────────────
_anki_ok = False
try:
    from aqt import mw
    from aqt.utils import showWarning
    _anki_ok = True
    print("AI Assistant: Anki imports OK")
except ImportError as _e:
    print(f"AI Assistant: Anki import FAILED – {_e}")
    mw = None  # type: ignore[assignment]
    def showWarning(msg, *a, **k): print(f"[warning] {msg}")

# ── Module constants ──────────────────────────────────────────────────────────
DOCK_NAME     = "AIAssistantSidebarDock_Integrated_v1"

# ── Config keys ───────────────────────────────────────────────────────────────
_PFX          = f"addon_{constants.ADDON_NAME_LAUNCHER}_AIv2_"
CK_WEB_SITE   = _PFX + "web_site"   # "api" or a website from AI_SITES

# ── Module globals ────────────────────────────────────────────────────────────
_dock:            Optional[Any] = None
_sites_panel:     Optional[Any] = None

# Websites usable with the user's own account instead of an API key.
AI_SITES = [
    ("chatgpt", "ChatGPT", "https://chatgpt.com/"),
    ("claude", "Claude", "https://claude.ai/new"),
    ("gemini", "Gemini", "https://gemini.google.com/app"),
    ("notebooklm", "NotebookLM", "https://notebooklm.google.com/"),
]
try:
    from .integrations.strings import tr as _web_tr
except Exception:  # pragma: no cover
    def _web_tr(text: str) -> str:
        return text


# ══════════════════════════════════════════════════════════════════════════════
# Config helpers
# ══════════════════════════════════════════════════════════════════════════════


# Older versions had their own API chat and kept its keys in
# SmartStudy_Data/ai_secrets.json and, before that, in the collection.
# The chat is gone: remove the keys (once; afterwards nothing is left).
_OLD_API_KEYS = ("key_openai", "key_gemini", "key_openrouter", "key_anthropic",
                 "key_deepseek", "key_llama")


def remove_old_api_keys() -> None:
    if not (_anki_ok and mw and mw.pm):
        return
    try:
        folder = os.path.join(mw.pm.profileFolder(), "SmartStudy_Data")
        for name in ("ai_secrets.json", "ai_secrets.json.tmp"):
            path = os.path.join(folder, name)
            if os.path.isfile(path):
                os.remove(path)
                print(f"AI Assistant: removed old API keys ({name})")
    except Exception:
        _ignored()
    try:
        if mw.col:
            for name in _OLD_API_KEYS:
                if mw.col.get_config(_PFX + name, None) is not None:
                    mw.col.remove_config(_PFX + name)
    except Exception:
        _ignored()


def _cfg_get(key: str, default: Any = "") -> Any:
    if _anki_ok and mw and mw.col:
        try:
            return mw.col.get_config(key, default)
        except Exception as e:
            print(f"AI Assistant: config read error for '{key}': {e}")
    return default

def _cfg_set(key: str, value: Any) -> None:
    if _anki_ok and mw and mw.col:
        try:
            mw.col.set_config(key, value)
        except Exception as e:
            print(f"AI Assistant: config write error for '{key}': {e}")


def _setup_sidebar() -> bool:
    global _dock

    if _dock is not None:
        print("AI Assistant: sidebar already set up")
        return True
    if not _qt_ok:
        print("AI Assistant: cannot setup – Qt not available")
        return False
    if not _anki_ok:
        print("AI Assistant: cannot setup – Anki not available")
        return False

    print("AI Assistant: setting up sidebar…")

    try:
        # Dock
        _dock = QDockWidget(_("AI Assistant"), mw)
        _dock.setObjectName(DOCK_NAME)
        _dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        _dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetClosable
        )
        _dock.setTitleBarWidget(QWidget())
        _dock.setMinimumWidth(340)
        # Tabs: ChatGPT/Claude/Gemini/NotebookLM with your own account.
        global _sites_panel
        from .web_accounts import AccountSitesPanel
        _sites_panel = AccountSitesPanel(
            list(AI_SITES), picker=True,
            hint=_web_tr("Sign in with your own account – no API key needed. Use your e-mail address: Google does not allow “Sign in with Google” inside apps like Anki. Gemini and NotebookLM use your Google sign-in from the Smart Study browser: sign in to Google there once."),
            remember=lambda key: _cfg_set(CK_WEB_SITE, key),
        )
        _sites_panel.show_site(_cfg_get(CK_WEB_SITE, "chatgpt") or "chatgpt")  # an old "api" falls back to the first site
        _dock.setWidget(_sites_panel)
        _dock.setVisible(False)
        from .sidebar_widths import attach
        attach(mw, _dock, "ai")
        mw.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, _dock)
        _register_layout()

        print("AI Assistant: sidebar setup complete ✓")
        return True

    except Exception as e:
        print(f"AI Assistant: CRITICAL setup error: {e}")
        traceback.print_exc()
        showWarning(_("AI Assistant setup error: {}").format(e))
        _dock = None
        return False


def _show_for_layout() -> bool:
    if _dock is None and not _setup_sidebar():
        return False
    if _dock is None:
        return False
    _dock.show()
    _dock.raise_()
    return True


def _register_layout() -> None:
    """Sidebar / split view / own window, like the browser (⧉ in the tab bar)."""
    try:
        from . import dock_layout
        dock_layout.register("ai", lambda: _dock, _show_for_layout, _("AI Assistant"))
        if _sites_panel is not None and getattr(_sites_panel, "external", None) is not None:
            row = _sites_panel.external.parentWidget().layout()
            if row is not None:
                row.addWidget(dock_layout.menu_button("ai"))
    except Exception as e:
        print(f"AI Assistant: no layout button: {e}")


def toggle_ai_assistant_dock() -> None:
    """Show or hide the AI Assistant sidebar. Called by launcher_widget.py."""
    global _dock

    if not _qt_ok or not _anki_ok:
        showWarning(_("AI Assistant is not available (missing Qt/Anki components)."))
        return

    if _dock is None:
        print("AI Assistant: first toggle – running setup")
        if not _setup_sidebar():
            return

    if _dock is None:
        return

    try:
        if _dock.isHidden():
            print("AI Assistant: showing dock")
            _dock.show()
            _dock.raise_()
        else:
            print("AI Assistant: hiding dock")
            _dock.hide()
    except Exception as e:
        print(f"AI Assistant: toggle error: {e}")
        traceback.print_exc()


def cleanup_ai_assistant_sidebar() -> None:
    """Called by __init__.py on profile close / add-on unload."""
    global _dock

    print("AI Assistant: cleanup starting…")

    global _sites_panel
    if _sites_panel:
        try: _sites_panel.cleanup()
        except Exception: _ignored()
        _sites_panel = None

    if _dock:
        try:
            if mw:
                mw.removeDockWidget(_dock)
            _dock.deleteLater()
        except Exception as e:
            print(f"AI Assistant: cleanup dock error: {e}")

    _dock = None
    print("AI Assistant: cleanup done ✓")


# ── Module load ───────────────────────────────────────────────────────────────
print(
    f"=== AI Assistant v2 module loaded ==="
    f"  Qt=6"
    f"  qt_ok={_qt_ok}"
    f"  anki_ok={_anki_ok}"
    f"  addon_path={getattr(constants,'addon_path','?')}"
)
