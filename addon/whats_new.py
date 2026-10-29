# -*- coding: utf-8 -*-
"""The "What's new" window, shown once after Smart Study was updated.

It lists the changes since the version the user saw last.  Changes that
switched something on come with a switch, so the user can say "keep it" or
"no thanks" right there instead of hunting through the settings.
"""
from __future__ import annotations

from typing import Callable, Dict, List

from .changelog import CHANGELOG
from .integrations import BY_KEY, is_enabled, load_state, save_state
from .integrations.strings import tr
from .integrations.ui import Dialog, Toggle, ask_restart


def _version_tuple(version: str):
    return tuple(int(p) if p.isdigit() else 0 for p in version.split("."))


def entries_since(last_seen: str) -> List[dict]:
    seen = _version_tuple(last_seen)
    return [e for e in CHANGELOG if _version_tuple(e["version"]) > seen]


class WhatsNewDialog(Dialog):
    def __init__(self, entries: List[dict], parent=None):
        super().__init__(tr("What's new in Smart Study {version}").format(version=entries[0]["version"]),
                         tr("Keep what you like – everything with a switch can be turned off right here."),
                         parent)
        self.state = load_state()
        self.toggles: Dict[str, Toggle] = {}

        features = [i for e in entries for i in e["items"] if i.get("integration")]
        others = [i for e in entries for i in e["items"] if not i.get("integration")]
        if features:
            self.section(tr("Built-in add-ons"))
            group = self.group()
            for item in features:
                key = item["integration"]
                if key in self.toggles:
                    continue
                toggle = Toggle(is_enabled(key, self.state))
                self.toggles[key] = toggle
                group.add_row(tr(BY_KEY[key].title), tr(BY_KEY[key].short), toggle)
        if others:
            self.section(tr("Also new"))
            group = self.group()
            for item in others:
                group.add_row("", tr(item["text"]))

        self.button(tr("Done"), primary=True, slot=self.accept)
        self.finish()

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


def show_if_updated(settings: dict, save: Callable[[], None], current: str) -> None:
    """Shows the window once per update; never on a fresh install."""
    last_seen = settings.get("last_seen_version")
    if last_seen == current:
        return
    settings["last_seen_version"] = current
    save()
    if not settings.get("onboarding_completed"):
        return  # first start: the setup wizard introduces everything
    entries = entries_since(last_seen or "2.0.1")
    # Only worth a window when something new arrived, not for fixes alone.
    if any(i.get("tag") in ("New", "Highlight") for e in entries for i in e["items"]):
        WhatsNewDialog(entries).exec()
