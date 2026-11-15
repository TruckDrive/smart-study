# -*- coding: utf-8 -*-
"""Add-ons bundled with Smart Study, and the ones it only suggests.

Each bundled add-on can be switched on or off (Tools → Smart Study →
Built-in add-ons…).  A bundled add-on never runs next to a separately
installed copy of the same add-on: when both are present, the user decides
once which one to keep.

Review Heatmap and Life Drain are no longer bundled: they are suggested and
installed from AnkiWeb on request (suggested.py).

State lives in ``smart_study/user_files/integrations/state.json`` (kept on
add-on updates):

    {"enabled": {key: bool}, "choice": {key: "builtin" | "standalone"},
     "suggested_after_unbundle": bool}

The "enabled" switches are mirrored into the collection (settings_sync.py), so
AnkiWeb sync takes them to other devices; "choice" depends on what is
installed on each device and stays local.  Entries for the former built-in
"heatmap" and "lifedrain" may still be there; they are ignored, except for
the one-time suggestion after the update.

Switching an add-on on or off takes effect after restarting Anki, because
add-ons register their hooks while Anki starts.
"""
from __future__ import annotations

import importlib
import json
import os
import traceback
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from aqt import gui_hooks, mw

from ._shim import STORE_DIR, manager
from .strings import tr  # noqa: F401  (also used by Smart Study's menu)

STATE_PATH = os.path.join(STORE_DIR, "state.json")


@dataclass
class Integration:
    key: str
    title: str
    short: str
    credit: str
    # Folder names a separately installed copy can have (AnkiWeb id, GitHub name).
    standalone: List[str] = field(default_factory=list)
    default: bool = True


INTEGRATIONS: List[Integration] = [
    Integration(
        key="select2clip",
        title="Copy selections with pictures as an image",
        short="Select part of a card with pictures – it is copied as one image, so ChatGPT or Claude get the pictures when you paste.",
        credit="Smart Study",
        standalone=["select2clip"],
        default=True,
    ),
    Integration(
        key="contanki",
        title="Controller support",
        short="Study with a gamepad, e.g. the 8BitDo Zero 2.",
        credit='Based on <a href="https://github.com/roxgib/anki-contanki">Contanki</a> by Sam Bradshaw. AGPL-3.0, modified for Smart Study (controller detection).',
        standalone=["1898790263", "contanki", "anki-contanki"],
        default=True,
    ),
]

BY_KEY: Dict[str, Integration] = {i.key: i for i in INTEGRATIONS}

loaded: Dict[str, bool] = {}
errors: Dict[str, str] = {}
_pending_conflicts: List[str] = []


# --- state --------------------------------------------------------------------
def load_state() -> dict:
    try:
        with open(STATE_PATH, encoding="utf-8") as f:
            state = json.load(f)
    except (OSError, ValueError):
        state = {}
    if not isinstance(state, dict):
        state = {}
    for name in ("enabled", "choice"):
        if not isinstance(state.get(name), dict):
            state[name] = {}
    return state


def save_state(state: dict, push: bool = True) -> None:
    if push:
        # The switches also live in the collection, so they sync to other devices.
        from .. import settings_sync
        settings_sync.push_integrations(state)
    os.makedirs(STORE_DIR, exist_ok=True)
    tmp = STATE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, STATE_PATH)


def is_enabled(key: str, state: Optional[dict] = None) -> bool:
    """Whether a bundled add-on is on; False for keys that are not bundled (any more)."""
    state = state or load_state()
    integration = BY_KEY.get(key)
    if integration is None:
        return False
    return bool(state["enabled"].get(key, integration.default))


def set_enabled(switches: Dict[str, bool]) -> bool:
    """Saves new on/off switches; True if one of them changed."""
    state = load_state()
    changed = False
    for key, on in switches.items():
        if key in BY_KEY and bool(on) != is_enabled(key, state):
            state["enabled"][key] = bool(on)
            changed = True
    if changed:
        save_state(state)
    return changed


def standalone_folder(key: str) -> Optional[str]:
    """The folder of a separately installed, enabled copy of this add-on."""
    if key not in BY_KEY:
        return None
    addons = set(mw.addonManager.allAddons())
    for folder in BY_KEY[key].standalone:
        if folder in addons and mw.addonManager.isEnabled(folder):
            return folder
    return None


# --- loading ------------------------------------------------------------------
def load_all() -> None:
    """Imports the enabled bundled add-ons. Called once while Anki starts."""
    state = load_state()
    for integration in INTEGRATIONS:
        key = integration.key
        if not is_enabled(key, state):
            continue
        if standalone_folder(key):
            # Never run both copies. Ask unless the user already chose to keep
            # the separate one (asking again if they chose ours but it is back).
            if state["choice"].get(key) != "standalone":
                _pending_conflicts.append(key)
            continue
        try:
            importlib.import_module(f"{__name__}.{key}")
            loaded[key] = True
        except Exception:
            errors[key] = traceback.format_exc()
            print(f"Smart Study: built-in add-on '{key}' failed to load:\n{errors[key]}")
    if _pending_conflicts:
        gui_hooks.main_window_did_init.append(_ask_about_conflicts)


def _ask_about_conflicts() -> None:
    from .dialogs import ConflictDialog
    # After the main window is shown, so the dialog has a parent on screen.
    from aqt.qt import QTimer
    QTimer.singleShot(1500, lambda: ConflictDialog(mw, list(_pending_conflicts)).exec())


def open_settings(parent=None) -> None:
    from .dialogs import IntegrationsDialog
    IntegrationsDialog(parent or mw).exec()


def has_options(key: str) -> bool:
    return manager(key)._config_action is not None


def open_options(key: str) -> bool:
    """Opens a bundled add-on's own settings window; False if it has none."""
    return manager(key).open_config()


# --- suggested add-ons (no longer bundled, installed from AnkiWeb) ------------
_folder_of_id: Dict[str, str] = {}


def installed_folders() -> Dict[str, bool]:
    """Every installed add-on (folder name and AnkiWeb id) -> whether it is enabled."""
    out: Dict[str, bool] = {}
    manager_ = mw.addonManager
    for folder in manager_.allAddons():
        try:
            out[folder] = bool(manager_.isEnabled(folder))
        except Exception:
            out[folder] = False
    try:
        for meta in manager_.all_addon_meta():
            aid = meta.ankiweb_id()
            if aid is not None and str(aid) not in out:
                out[str(aid)] = bool(meta.enabled)
                _folder_of_id[str(aid)] = meta.dir_name
    except Exception:
        pass
    return out


def suggestion_rows() -> List[dict]:
    """The suggested add-ons for the settings windows, with their install state."""
    from .suggested import SUGGESTED, installed_copy
    folders = installed_folders()
    rows = []
    for s in SUGGESTED:
        rows.append({
            "key": s.key,
            "title": s.title,
            "desc": tr(s.short) + " " + tr("By {author}.").format(author=s.author),
            "code": s.code,
            "url": s.url,
            "installed": installed_copy(s, folders) is not None,
        })
    return rows


def install_suggested(codes: List[str], parent=None, on_done=None) -> None:
    """Downloads add-ons from AnkiWeb with Anki's own installer.

    Anki then reports the result and asks for a restart; ``on_done(ok)``
    runs after that."""
    import sys
    from .. import addon_sync
    from ._shim import PACKAGE
    package = sys.modules.get(PACKAGE)
    settings = getattr(package, "addon_settings", None)
    if not isinstance(settings, dict):
        settings = {}
    save = getattr(package, "save_addon_settings", None) or (lambda: None)
    addon_sync.install(list(codes), settings, save, parent=parent, on_done=on_done)


def enable_copy(key: str) -> bool:
    """Switches a separately installed, switched-off copy back on."""
    from .suggested import SUGGESTED_BY_KEY, installed_copy
    copy = installed_copy(SUGGESTED_BY_KEY[key], installed_folders())
    if copy is None or copy[1]:
        return False
    folder = _folder_of_id.get(copy[0], copy[0])
    mw.addonManager.toggleEnabled(folder, enable=True)
    return True


def offer_after_update(onboarded: bool, first_start: bool, attempt: int = 0) -> None:
    """Once per device after this update: offer the originals of the add-ons
    that were built in and switched on.  Never raises."""
    try:
        from .suggested import ASKED_KEY, startup_plan
        state = load_state()
        offer, remember = startup_plan(state, installed_folders(), onboarded, first_start)
        if remember:
            state[ASKED_KEY] = True
            save_state(state, push=False)
        if not offer:
            return
        from aqt.qt import QApplication, QTimer
        if QApplication.activeModalWidget() is not None:
            if attempt < 20:
                QTimer.singleShot(3000, lambda: offer_after_update(onboarded, first_start, attempt + 1))
            return
        # Remember first, so a failing window is not shown again on every start.
        state[ASKED_KEY] = True
        save_state(state, push=False)
        from .dialogs import SuggestedAfterUpdateDialog
        SuggestedAfterUpdateDialog(mw, offer).exec()
    except Exception as exc:
        print(f"Smart Study: suggesting the former built-in add-ons failed: {exc}")
        traceback.print_exc()
