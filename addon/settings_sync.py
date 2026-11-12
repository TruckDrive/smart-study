# -*- coding: utf-8 -*-
"""Smart Study's settings travel with the Anki collection.

The settings file in the profile folder and the switches for the built-in
add-ons (``user_files/integrations/state.json``) stay the local copies.  A
mirror of both is kept in the collection config, so the normal AnkiWeb sync
takes them to your other devices.  Of two copies, the newer one wins: every
local change that differs from the collection gets a new time stamp.

Collection config key ``smartstudy_settings``::

    {"settings": {...}, "settingsAt": float,
     "integrations": {key: bool}, "integrationsAt": float}
"""
from __future__ import annotations

import time
import traceback
from typing import Any, Dict, Optional

CONF_KEY = "smartstudy_settings"
# Local stamp of the settings copy that was last pushed or pulled.
STAMP_KEY = "_synced_at"
# Per device: "What's new" was seen here, the launcher was opened here, and
# the add-on sync choices of this device (see addon_sync.py).
LOCAL_KEYS = {STAMP_KEY, "last_seen_version", "launcher_sidebar_open",
              "addon_sync_enabled", "addon_sync_asked", "addon_sync_known", "addon_sync_skipped"}


def _col():
    try:
        from aqt import mw
    except ImportError:
        return None
    return getattr(mw, "col", None) if mw else None


def _remote() -> Optional[Dict[str, Any]]:
    col = _col()
    if not col:
        return None
    try:
        value = col.get_config(CONF_KEY, None)
    except Exception:
        traceback.print_exc()
        return None
    return dict(value) if isinstance(value, dict) else {}


def _store(remote: Dict[str, Any]) -> None:
    col = _col()
    if col:
        try:
            col.set_config(CONF_KEY, remote)
        except Exception:
            traceback.print_exc()


def _synced(settings: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in settings.items() if k not in LOCAL_KEYS}


# --- add-on settings ----------------------------------------------------------
def push_settings(settings: Dict[str, Any]) -> None:
    """Puts the settings into the collection if they differ from its copy."""
    remote = _remote()
    if remote is None:
        return
    values = _synced(settings)
    if remote.get("settings") == values:
        return
    now = time.time()
    remote["settings"] = values
    remote["settingsAt"] = now
    settings[STAMP_KEY] = now
    _store(remote)


def pull_settings(settings: Dict[str, Any]) -> Dict[str, Any]:
    """Takes a newer copy from the collection into ``settings``.

    Returns the keys that changed (empty if nothing came in).  A local copy
    that is newer, or that the collection does not have yet, is pushed.
    """
    remote = _remote()
    if remote is None:
        return {}
    values = remote.get("settings")
    if isinstance(values, dict) and float(remote.get("settingsAt") or 0) > float(settings.get(STAMP_KEY) or 0):
        changed = {k: v for k, v in values.items() if k not in LOCAL_KEYS and settings.get(k) != v}
        settings.update(changed)
        settings[STAMP_KEY] = float(remote["settingsAt"])
        return changed
    push_settings(settings)
    return {}


# --- built-in add-on switches -------------------------------------------------
def push_integrations(state: Dict[str, Any]) -> None:
    remote = _remote()
    if remote is None:
        return
    enabled = dict(state.get("enabled") or {})
    if remote.get("integrations") == enabled:
        return
    now = time.time()
    remote["integrations"] = enabled
    remote["integrationsAt"] = now
    state[STAMP_KEY] = now
    _store(remote)


def pull_integrations(state: Dict[str, Any]) -> bool:
    """Like pull_settings for the add-on switches; True if they changed."""
    remote = _remote()
    if remote is None:
        return False
    enabled = remote.get("integrations")
    if isinstance(enabled, dict) and float(remote.get("integrationsAt") or 0) > float(state.get(STAMP_KEY) or 0):
        changed = enabled != state.get("enabled")
        state["enabled"] = dict(enabled)
        state[STAMP_KEY] = float(remote["integrationsAt"])
        return changed
    push_integrations(state)
    return False


# --- controller profiles (built-in Contanki) ----------------------------------
# The button layouts live as files in user_files/integrations/contanki.  The
# same newer-wins rule applies; the local stamp is kept in a file next to them.
CONTROLLER_KEY = "controller"
CONTROLLER_AT = "controllerAt"
_CONTROLLER_FILES = ("controllers", "controller_choices.json")
_CONTROLLER_DIRS = ("profiles", "custom_controllers")


def _controller_dir() -> str:
    import os
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "user_files", "integrations", "contanki")


def _read_controller_files() -> Dict[str, str]:
    import os
    base = _controller_dir()
    files: Dict[str, str] = {}
    names = list(_CONTROLLER_FILES)
    for folder in _CONTROLLER_DIRS:
        path = os.path.join(base, folder)
        if os.path.isdir(path):
            names += [f"{folder}/{n}" for n in sorted(os.listdir(path))
                      if os.path.isfile(os.path.join(path, n))]
    for name in names:
        try:
            with open(os.path.join(base, name), encoding="utf-8") as f:
                files[name] = f.read()
        except OSError:
            pass
    return files


def _stamp_path() -> str:
    import os
    return os.path.join(_controller_dir(), ".synced_at")


def _local_controller_stamp() -> float:
    try:
        with open(_stamp_path(), encoding="utf-8") as f:
            return float(f.read().strip() or 0)
    except (OSError, ValueError):
        return 0.0


def _set_local_controller_stamp(value: float) -> None:
    import os
    os.makedirs(_controller_dir(), exist_ok=True)
    with open(_stamp_path(), "w", encoding="utf-8") as f:
        f.write(repr(value))


def push_controller() -> None:
    """Puts the controller layouts into the collection if they changed here."""
    import os
    if not os.path.isdir(_controller_dir()):
        return
    remote = _remote()
    if remote is None:
        return
    files = _read_controller_files()
    if not files or remote.get(CONTROLLER_KEY) == files:
        return
    now = time.time()
    remote[CONTROLLER_KEY] = files
    remote[CONTROLLER_AT] = now
    _store(remote)
    _set_local_controller_stamp(now)


def pull_controller() -> bool:
    """Takes newer controller layouts from the collection; True if files changed."""
    import os
    remote = _remote()
    if remote is None:
        return False
    files = remote.get(CONTROLLER_KEY)
    remote_at = float(remote.get(CONTROLLER_AT) or 0)
    if not isinstance(files, dict) or remote_at <= _local_controller_stamp():
        push_controller()
        return False
    base = _controller_dir()
    changed = False
    for name, text in files.items():
        parts = name.split("/")
        allowed = (name in _CONTROLLER_FILES or
                   (len(parts) == 2 and parts[0] in _CONTROLLER_DIRS and parts[1] not in ("", ".", "..")))
        if not allowed or not isinstance(text, str):
            continue
        path = os.path.join(base, *parts)
        try:
            with open(path, encoding="utf-8") as f:
                if f.read() == text:
                    continue
        except OSError:
            pass
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        changed = True
    _set_local_controller_stamp(remote_at)
    # Layouts that exist only here are added to the synced copy.
    if _read_controller_files() != files:
        push_controller()
    return changed
