# -*- coding: utf-8 -*-
"""Windows for the bundled add-ons: settings, double-install question."""
from __future__ import annotations

import os
from typing import Dict, List

from aqt import mw
from aqt.qt import QHBoxLayout, QWidget
from aqt.utils import tooltip

from . import (BY_KEY, INTEGRATIONS, errors, has_options, is_enabled, load_state,
               loaded, open_options, save_state, standalone_folder)
from .strings import tr
from .ui import Dialog, Segments, Toggle, ask_restart, link_button


def _take_over_config(key: str, folder: str) -> None:
    """Copies the separate add-on's settings, unless the built-in one has its own."""
    from ._shim import _store_path, manager
    if os.path.exists(_store_path(key)):
        return
    try:
        conf = mw.addonManager.getConfig(folder)
    except Exception:
        conf = None
    if conf:
        manager(key).writeConfig(key, conf)


def _forget_controllers() -> None:
    from .contanki.controller import CHOICES_FILE
    try:
        os.remove(CHOICES_FILE)
    except OSError:
        pass
    tooltip(tr("Done. You will be asked again when the controller connects."))


class IntegrationsDialog(Dialog):
    """Tools → Smart Study → Built-in add-ons…"""

    def __init__(self, parent=None):
        super().__init__(tr("Built-in add-ons"),
                         tr("Included in Smart Study – no separate installs. Changes apply after restarting Anki."),
                         parent)
        self.state = load_state()
        self.toggles: Dict[str, Toggle] = {}

        group = self.group()
        for integration in INTEGRATIONS:
            key = integration.key
            toggle = Toggle(is_enabled(key, self.state))
            self.toggles[key] = toggle
            text = tr(integration.short)
            if standalone_folder(key):
                text += " " + tr("Your separately installed copy is active.")
            elif key in errors:
                text += " " + tr("Could not be started.")
            group.add_row(tr(integration.title), text, toggle, self._links(key))

        self.section(tr("Credits"))
        self.note("<br>".join(i.credit for i in INTEGRATIONS if i.credit != "Smart Study"))

        self.button(tr("Cancel"), slot=self.reject)
        self.button(tr("Save"), primary=True, slot=self.accept)
        self.finish()

    def _links(self, key: str):
        links = []
        if loaded.get(key) and has_options(key):
            links.append(link_button(tr("Options…"), lambda: open_options(key)))
        if key == "contanki" and loaded.get(key):
            links.append(link_button(tr("Forget which controller I picked"), _forget_controllers))
        if not links:
            return None
        box = QWidget()
        row = QHBoxLayout(box)
        row.setContentsMargins(0, 2, 0, 0)
        row.setSpacing(16)
        for link in links:
            row.addWidget(link)
        row.addStretch(1)
        return box

    def accept(self) -> None:
        changed = False
        for key, toggle in self.toggles.items():
            if toggle.isChecked() != is_enabled(key, self.state):
                self.state["enabled"][key] = toggle.isChecked()
                changed = True
        save_state(self.state)
        super().accept()
        if changed:
            ask_restart()


class ConflictDialog(Dialog):
    """Shown when a bundled add-on is also installed separately."""

    def __init__(self, parent, keys: List[str]):
        super().__init__(tr("Already installed"),
                         tr("Smart Study now includes these add-ons. Only one copy can run – keep the built-in one or yours?"),
                         parent)
        self.choices: Dict[str, Segments] = {}
        group = self.group()
        for key in keys:
            segments = Segments([tr("Built-in"), tr("Keep mine")], 0)
            self.choices[key] = segments
            group.add_row(tr(BY_KEY[key].title), tr(BY_KEY[key].short), segments)
        self.note(tr("Your settings are kept either way. “Built-in” switches your separate add-on off. Change it any time under Tools → Smart Study → Built-in add-ons."))
        self.button(tr("Continue"), primary=True, slot=self.accept)
        self.finish()

    def accept(self) -> None:
        state = load_state()
        switched_off = False
        for key, segments in self.choices.items():
            if segments.value() == 0:
                folder = standalone_folder(key)
                if folder:
                    _take_over_config(key, folder)
                    mw.addonManager.toggleEnabled(folder, enable=False)
                    switched_off = True
                state["choice"][key] = "builtin"
                state["enabled"][key] = True
            else:
                state["choice"][key] = "standalone"
        save_state(state)
        super().accept()
        if switched_off:
            ask_restart()
