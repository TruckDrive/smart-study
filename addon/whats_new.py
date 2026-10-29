# -*- coding: utf-8 -*-
"""The "What's new" window, shown once after Smart Study was updated.

It lists the changes since the version the user saw last.  Changes that
switched something on come with a switch, so the user can say "keep it" or
"no thanks" right there instead of hunting through the settings.
"""
from __future__ import annotations

from typing import Callable, Dict, List

from aqt import mw
from aqt.qt import (QCheckBox, QDialog, QDialogButtonBox, QFrame, QLabel,
                    QScrollArea, QVBoxLayout, QWidget, Qt)

from .changelog import CHANGELOG
from .integrations import is_enabled, load_state, save_state
from .integrations.strings import tr


def _version_tuple(version: str):
    return tuple(int(p) if p.isdigit() else 0 for p in version.split("."))


def entries_since(last_seen: str) -> List[dict]:
    seen = _version_tuple(last_seen)
    return [e for e in CHANGELOG if _version_tuple(e["version"]) > seen]


class WhatsNewDialog(QDialog):
    def __init__(self, entries: List[dict], parent=None):
        super().__init__(parent or mw)
        self.setWindowTitle(tr("What's new in Smart Study"))
        self.resize(600, 560)
        self.state = load_state()
        self.switches: Dict[str, QCheckBox] = {}

        layout = QVBoxLayout(self)
        intro = QLabel(tr("Smart Study was updated. Here is what changed – where something new was switched on, you can keep it or switch it off right here."))
        intro.setWordWrap(True)
        layout.addWidget(intro)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        body = QWidget()
        rows = QVBoxLayout(body)
        for entry in entries:
            heading = QLabel(f"<b>{entry['version']}</b> · {entry.get('date', '')}")
            rows.addWidget(heading)
            for item in entry["items"]:
                key = item.get("integration")
                text = f"<b>{tr(item['tag'])}:</b> {tr(item['text'])}"
                if key and key not in self.switches:
                    box = QCheckBox()
                    box.setChecked(is_enabled(key, self.state))
                    box.setText(tr("Keep switched on") if box.isChecked() else tr("Switch on"))
                    label = QLabel(text)
                    label.setWordWrap(True)
                    rows.addWidget(label)
                    rows.addWidget(box)
                    self.switches[key] = box
                else:
                    label = QLabel("• " + text)
                    label.setWordWrap(True)
                    label.setTextFormat(Qt.TextFormat.RichText)
                    rows.addWidget(label)
            rows.addSpacing(10)
        rows.addStretch(1)
        scroll.setWidget(body)
        layout.addWidget(scroll, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)

    def accept(self) -> None:
        changed = False
        for key, box in self.switches.items():
            if box.isChecked() != is_enabled(key, self.state):
                self.state["enabled"][key] = box.isChecked()
                changed = True
        save_state(self.state)
        super().accept()
        if changed:
            from aqt.utils import askUser
            if askUser(tr("The change takes effect after restarting Anki. Close Anki now?"), parent=mw):
                mw.close()


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
    if entries:
        WhatsNewDialog(entries).exec()
