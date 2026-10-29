# -*- coding: utf-8 -*-
"""Stand-in for ``mw.addonManager`` inside bundled add-ons.

Bundled add-ons live in ``smart_study/integrations/<key>/``.  Anki resolves an
add-on's config from the first part of the module name, so a bundled add-on
calling ``mw.addonManager.getConfig(__name__)`` would get Smart Study's config.
Each bundled add-on uses ``manager(key)`` instead: config is read from the
add-on's own ``config.json`` and saved to ``smart_study/user_files/``, which
Anki keeps when Smart Study is updated.
"""
from __future__ import annotations

import json
import os
from typing import Any, Callable, Dict, Optional

from aqt import mw

PACKAGE = __name__.split(".")[0]
HERE = os.path.dirname(__file__)
ADDON_DIR = os.path.dirname(HERE)
STORE_DIR = os.path.join(ADDON_DIR, "user_files", "integrations")


def _defaults(key: str) -> Dict[str, Any]:
    try:
        with open(os.path.join(HERE, key, "config.json"), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _store_path(key: str) -> str:
    return os.path.join(STORE_DIR, f"{key}.json")


class AddonManagerProxy:
    """Forwards to Anki's add-on manager, but keeps config per bundled add-on."""

    def __init__(self, key: str):
        self.key = key
        self._config_action: Optional[Callable[[], Any]] = None
        self._update_action: Optional[Callable[[Any], Any]] = None

    # --- config -----------------------------------------------------------
    def getConfig(self, _module: str = "") -> Dict[str, Any]:
        conf = _defaults(self.key)
        try:
            with open(_store_path(self.key), encoding="utf-8") as f:
                conf.update(json.load(f))
        except (OSError, ValueError):
            pass
        return conf

    def writeConfig(self, _module: str, conf: Dict[str, Any]) -> None:
        os.makedirs(STORE_DIR, exist_ok=True)
        tmp = _store_path(self.key) + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(conf, f, indent=2, ensure_ascii=False)
        os.replace(tmp, _store_path(self.key))
        if self._update_action:
            self._update_action(conf)

    def addonConfigDefaults(self, _dir: str = "") -> Dict[str, Any]:
        return _defaults(self.key)

    def setConfigAction(self, _module: str, fn: Callable[[], Any]) -> None:
        self._config_action = fn

    def setConfigUpdatedAction(self, _module: str, fn: Callable[[Any], Any]) -> None:
        self._update_action = fn

    def open_config(self) -> bool:
        """Opens the bundled add-on's own settings, if it registered any."""
        if self._config_action:
            self._config_action()
            return True
        return False

    # --- paths and web exports ---------------------------------------------
    def addonFromModule(self, _module: str) -> str:
        return PACKAGE

    def web_base(self) -> str:
        """URL prefix for files of this bundled add-on (see setWebExports in __init__)."""
        return f"/_addons/{PACKAGE}/integrations/{self.key}"

    def setWebExports(self, _module: str, _pattern: str) -> None:
        # Smart Study exports integrations/<key>/web/... itself; one pattern per add-on.
        pass

    def __getattr__(self, name: str) -> Any:
        return getattr(mw.addonManager, name)


_proxies: Dict[str, AddonManagerProxy] = {}


def manager(key: str) -> AddonManagerProxy:
    if key not in _proxies:
        _proxies[key] = AddonManagerProxy(key)
    return _proxies[key]
