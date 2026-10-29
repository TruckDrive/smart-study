# -*- coding: utf-8 -*-
"""Windows for the bundled add-ons: settings, double-install question."""
from __future__ import annotations

from typing import Dict, List

from aqt import mw
from aqt.qt import (QButtonGroup, QCheckBox, QDialog, QDialogButtonBox,
                    QFrame, QHBoxLayout, QLabel, QPushButton, QRadioButton,
                    QScrollArea, QVBoxLayout, QWidget, Qt)
from aqt.utils import askUser, tooltip

from . import (BY_KEY, INTEGRATIONS, errors, has_options, is_enabled, load_state,
               loaded, open_options, save_state, standalone_folder)
from .strings import tr


def _take_over_config(key: str, folder: str) -> None:
    """Copies the separate add-on's settings, unless the built-in one has its own."""
    import os
    from ._shim import _store_path, manager
    if os.path.exists(_store_path(key)):
        return
    try:
        conf = mw.addonManager.getConfig(folder)
    except Exception:
        conf = None
    if conf:
        manager(key).writeConfig(key, conf)


def _restart_hint(parent) -> None:
    if askUser(tr("The change takes effect after restarting Anki. Close Anki now?"), parent=parent):
        mw.close()


def _label(text: str, *, bold: bool = False, small: bool = False) -> QLabel:
    label = QLabel(text)
    label.setWordWrap(True)
    label.setTextFormat(Qt.TextFormat.RichText)
    label.setOpenExternalLinks(True)
    style = []
    if bold:
        style.append("font-weight:600")
    if small:
        from aqt.theme import theme_manager
        style.append("font-size:11px; color: %s" % ("#a1a1a6" if theme_manager.night_mode else "#6e6e73"))
    if style:
        label.setStyleSheet(";".join(style))
    return label


class IntegrationsDialog(QDialog):
    """Tools → Smart Study → Built-in add-ons…"""

    def __init__(self, parent=None):
        super().__init__(parent or mw)
        self.setWindowTitle(tr("Built-in add-ons"))
        self.resize(620, 640)
        self.state = load_state()
        self.boxes: Dict[str, QCheckBox] = {}

        outer = QVBoxLayout(self)
        outer.addWidget(_label(tr("Smart Study includes these add-ons, so you do not have to install them separately. Switch off what you do not need. Changes take effect after restarting Anki.")))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        body = QWidget()
        rows = QVBoxLayout(body)
        rows.setSpacing(14)
        for integration in INTEGRATIONS:
            rows.addWidget(self._row(integration))
        rows.addStretch(1)
        scroll.setWidget(body)
        outer.addWidget(scroll, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok
                                   | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        outer.addWidget(buttons)

    def _row(self, integration) -> QWidget:
        key = integration.key
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(frame)

        top = QHBoxLayout()
        box = QCheckBox(tr(integration.title))
        box.setStyleSheet("font-weight:600")
        box.setChecked(is_enabled(key, self.state))
        self.boxes[key] = box
        top.addWidget(box, 1)
        if loaded.get(key) and has_options(key):
            options = QPushButton(tr("Options…"))
            options.clicked.connect(lambda _=False, k=key: open_options(k))
            top.addWidget(options)
        layout.addLayout(top)

        layout.addWidget(_label(tr(integration.summary)))
        folder = standalone_folder(key)
        if folder:
            layout.addWidget(_label(tr("A separately installed copy is active, so the built-in one stays off. You can turn it off under Tools → Add-ons."), small=True))
        elif key in errors:
            layout.addWidget(_label(tr("Could not be started. Details are in the Anki console."), small=True))
        if integration.credit != "Smart Study":
            layout.addWidget(_label(integration.credit, small=True))
        if key == "contanki" and loaded.get(key):
            reset = QPushButton(tr("Forget which controller I picked"))
            reset.clicked.connect(self._forget_controllers)
            layout.addWidget(reset, 0, Qt.AlignmentFlag.AlignLeft)
        return frame

    def _forget_controllers(self) -> None:
        from .contanki.controller import CHOICES_FILE
        import os
        try:
            os.remove(CHOICES_FILE)
        except OSError:
            pass
        tooltip(tr("Done. You will be asked again when the controller connects."))

    def accept(self) -> None:
        changed = False
        for key, box in self.boxes.items():
            if box.isChecked() != is_enabled(key, self.state):
                self.state["enabled"][key] = box.isChecked()
                changed = True
        save_state(self.state)
        super().accept()
        if changed:
            _restart_hint(mw)


class ConflictDialog(QDialog):
    """Shown when a bundled add-on is also installed separately."""

    def __init__(self, parent, keys: List[str]):
        super().__init__(parent)
        self.keys = keys
        self.setWindowTitle(tr("Add-ons already installed"))
        self.setMinimumWidth(560)
        self.groups: Dict[str, QButtonGroup] = {}

        layout = QVBoxLayout(self)
        layout.addWidget(_label(tr("Smart Study now includes these add-ons. You also have them installed separately. Only one copy can run – which one do you want?")))
        for key in keys:
            integration = BY_KEY[key]
            frame = QFrame()
            frame.setFrameShape(QFrame.Shape.StyledPanel)
            rows = QVBoxLayout(frame)
            rows.addWidget(_label(tr(integration.title), bold=True))
            group = QButtonGroup(frame)
            builtin = QRadioButton(tr("Use the version built into Smart Study (recommended) – your separate add-on is switched off"))
            keep = QRadioButton(tr("Keep my separate add-on – the built-in version stays off"))
            builtin.setChecked(True)
            group.addButton(builtin, 0)
            group.addButton(keep, 1)
            rows.addWidget(builtin)
            rows.addWidget(keep)
            self.groups[key] = group
            layout.addWidget(frame)
        layout.addWidget(_label(tr("Your settings are kept either way. You can change this later under Tools → Smart Study → Built-in add-ons."), small=True))

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)

    def accept(self) -> None:
        state = load_state()
        switched_off = False
        for key, group in self.groups.items():
            if group.checkedId() == 0:
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
            _restart_hint(mw)

    def reject(self) -> None:
        # Closing without a choice: ask again next start, nothing changes now.
        super().reject()
