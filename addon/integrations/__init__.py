# -*- coding: utf-8 -*-
"""Add-ons bundled with Smart Study.

Each bundled add-on can be switched on or off (Tools → Smart Study →
Built-in add-ons…).  A bundled add-on never runs next to a separately
installed copy of the same add-on: when both are present, the user decides
once which one to keep.

State lives in ``smart_study/user_files/integrations/state.json`` (kept on
add-on updates):

    {"enabled": {key: bool}, "choice": {key: "builtin" | "standalone"}}

The "enabled" switches are mirrored into the collection (settings_sync.py), so
AnkiWeb sync takes them to other devices; "choice" depends on what is
installed on each device and stays local.

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
        key="heatmap",
        title="Review heatmap",
        short="Your reviews and streak as a calendar on the deck list.",
        credit='Based on the Anki add-on <a href="https://github.com/glutanimate/review-heatmap/">Review Heatmap</a> by Glutanimate. <a href="https://glutanimate.com/support-my-work/">Click here to support Glutanimate\'s work.</a> AGPL-3.0, modified for Smart Study.',
        standalone=["1771074083", "review_heatmap", "review-heatmap", "1722241614", "723520343"],
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
    Integration(
        key="lifedrain",
        title="Life Drain",
        short="A life bar that drains while you think about a card.",
        credit='Based on <a href="https://github.com/Yutsuten/anki-lifedrain">Life Drain</a> by Yutsuten. AGPL-3.0, modified for Smart Study.',
        standalone=["715575551", "lifedrain", "anki-lifedrain"],
        default=False,
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
    state.setdefault("enabled", {})
    state.setdefault("choice", {})
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
    state = state or load_state()
    return bool(state["enabled"].get(key, BY_KEY[key].default))


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
