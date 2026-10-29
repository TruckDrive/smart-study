# -*- coding: utf-8 -*-
"""Your AnkiWeb add-ons on every device.

Each device that switched this on puts the AnkiWeb add-ons it has installed
into the collection config, so the normal AnkiWeb sync carries the list to
your other devices.  There Smart Study offers to install what is missing.
An add-on removed on one device is removed from the list, so the others are
no longer asked about it (they keep their copy).

Collection config key ``smartstudy_addons``: ``{"addons": {id: name}}``

Per device (Smart Study settings, never synced): whether this is switched on,
whether the user was asked, which add-ons this device reported last time and
which ones the user did not want here.
"""
from __future__ import annotations

import traceback
from typing import Callable, Dict, Iterable, List, Optional

CONF_KEY = "smartstudy_addons"
ENABLED = "addon_sync_enabled"
ASKED = "addon_sync_asked"
KNOWN = "addon_sync_known"
SKIPPED = "addon_sync_skipped"
LOCAL_KEYS = {ENABLED, ASKED, KNOWN, SKIPPED}

# Smart Study itself (AnkiWeb id) is updated by Anki, not by this list.
OWN_IDS = {"1726163334"}


# --- pure logic (also used by tests) --------------------------------------------
def merge(remote: Dict[str, str], installed: Dict[str, str], known: Iterable[str]) -> Dict[str, str]:
    """The new shared list after this device reports what it has installed."""
    result = {k: v for k, v in remote.items() if k not in set(known) - set(installed)}
    result.update(installed)
    return result


def missing(remote: Dict[str, str], installed: Iterable[str], skipped: Iterable[str]) -> Dict[str, str]:
    """Add-ons from the shared list that this device should be offered."""
    leave_out = set(installed) | set(skipped) | OWN_IDS
    return {k: v for k, v in remote.items() if k not in leave_out}


def valid_code(code: str) -> Optional[str]:
    code = (code or "").strip()
    return code if code.isdigit() and 0 < len(code) <= 12 else None


# --- Anki --------------------------------------------------------------------------
def _mw():
    try:
        from aqt import mw
    except ImportError:
        return None
    return mw


def installed_addons() -> Dict[str, str]:
    """AnkiWeb add-ons installed here (enabled or not): {id: name}."""
    mw = _mw()
    out: Dict[str, str] = {}
    if not mw:
        return out
    for meta in mw.addonManager.all_addon_meta():
        aid = meta.ankiweb_id()
        if aid is not None and str(aid) not in OWN_IDS:
            out[str(aid)] = meta.human_name()
    return out


def _remote() -> Optional[Dict[str, str]]:
    mw = _mw()
    col = getattr(mw, "col", None) if mw else None
    if not col:
        return None
    try:
        value = col.get_config(CONF_KEY, None) or {}
        addons = value.get("addons") if isinstance(value, dict) else None
        return {str(k): str(v) for k, v in (addons or {}).items()}
    except Exception:
        traceback.print_exc()
        return None


def _store(addons: Dict[str, str]) -> None:
    mw = _mw()
    if mw and getattr(mw, "col", None):
        try:
            mw.col.set_config(CONF_KEY, {"addons": addons})
        except Exception:
            traceback.print_exc()


def push(settings: Dict, save: Callable[[], None]) -> Dict[str, str]:
    """Reports this device's add-ons; returns the shared list."""
    remote = _remote()
    if remote is None or not settings.get(ENABLED):
        return remote or {}
    installed = installed_addons()
    shared = merge(remote, installed, settings.get(KNOWN) or [])
    if shared != remote:
        _store(shared)
    if sorted(installed) != sorted(settings.get(KNOWN) or []):
        settings[KNOWN] = sorted(installed)
        save()
    return shared


def install(ids: List[str], settings: Dict, save: Callable[[], None], parent=None) -> None:
    """Downloads and installs add-ons from AnkiWeb, then updates the shared list."""
    mw = _mw()
    if not mw or not ids:
        return
    from aqt.addons import download_addons, show_log_to_user

    def done(log) -> None:
        show_log_to_user(parent or mw, log, title="Smart Study")
        push(settings, save)

    download_addons(parent or mw, mw.addonManager, [int(i) for i in ids], done)


def check(settings: Dict, save: Callable[[], None]) -> None:
    """After opening the profile or a sync: offer add-ons from other devices."""
    if not settings.get(ENABLED):
        return
    shared = push(settings, save)
    offer = missing(shared, installed_addons(), settings.get(SKIPPED) or [])
    if offer:
        OfferDialog(offer, settings, save).exec()


def ask_if_needed(settings: Dict, save: Callable[[], None]) -> None:
    """Asks once per device whether add-ons should sync (also after the update)."""
    if settings.get(ASKED):
        return
    from .integrations.strings import tr
    from .integrations.ui import Dialog
    dialog = Dialog(tr("Sync your add-ons?"),
                    tr("Smart Study can keep the same AnkiWeb add-ons on all your devices. "
                       "Your add-on list then travels with the normal AnkiWeb sync, and on your other "
                       "devices Smart Study offers to install what is missing."), width=480)
    dialog.note(tr("You can change this any time under Settings → Add-ons."))
    dialog.button(tr("No thanks"), slot=dialog.reject)
    dialog.button(tr("Sync add-ons"), primary=True, slot=dialog.accept)
    dialog.finish()
    settings[ENABLED] = bool(dialog.exec())
    settings[ASKED] = True
    save()
    if settings[ENABLED]:
        check(settings, save)


def _offer_dialog_class():
    from .integrations.strings import tr
    from .integrations.ui import Dialog, Toggle

    class _OfferDialog(Dialog):
        """Add-ons installed on another device but not here."""

        def __init__(self, offer: Dict[str, str], settings: Dict, save: Callable[[], None]):
            super().__init__(tr("Add-ons from your other devices"),
                             tr("These add-ons are installed on another device. Install them here too?"),
                             width=520)
            self.settings, self.save = settings, save
            self.toggles: Dict[str, Toggle] = {}
            group = self.group()
            for aid, name in sorted(offer.items(), key=lambda item: item[1].lower()):
                toggle = Toggle(True)
                self.toggles[aid] = toggle
                group.add_row(name, tr("Code {code}").format(code=aid), toggle)
            self.note(tr("Switched off add-ons are not offered again on this device."))
            self.button(tr("Not now"), slot=self.reject)
            self.button(tr("Install"), primary=True, slot=self.accept)
            self.finish()

        def accept(self) -> None:
            chosen = [aid for aid, t in self.toggles.items() if t.isChecked()]
            skipped = set(self.settings.get(SKIPPED) or [])
            skipped.update(aid for aid, t in self.toggles.items() if not t.isChecked())
            self.settings[SKIPPED] = sorted(skipped)
            self.save()
            super().accept()
            install(chosen, self.settings, self.save)

    return _OfferDialog


def OfferDialog(offer: Dict[str, str], settings: Dict, save: Callable[[], None]):
    return _offer_dialog_class()(offer, settings, save)
