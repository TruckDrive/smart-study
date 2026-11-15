# -*- coding: utf-8 -*-
"""Add-ons Smart Study suggests instead of shipping them.

Review Heatmap and Life Drain used to be built in.  Now Smart Study only
suggests the original add-ons and installs them from AnkiWeb in one click
(Settings → Add-ons, Tools → Smart Study → Built-in add-ons…).

Users who had the built-in copy switched on are asked once per device, after
the update, whether to install the originals (see ``to_offer``).

Pure logic only, so tests can use it without Anki.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# Key in integrations/state.json: the one-time question after the update was handled.
ASKED_KEY = "suggested_after_unbundle"


@dataclass
class Suggestion:
    key: str          # the former built-in key in state.json ("enabled")
    title: str
    short: str
    author: str
    code: str         # AnkiWeb code
    # Folder names an installed copy can have (AnkiWeb ids, GitHub names).
    standalone: List[str] = field(default_factory=list)
    # Whether the former built-in copy was on when the user never switched it.
    builtin_default: bool = False

    @property
    def url(self) -> str:
        return f"https://ankiweb.net/shared/info/{self.code}"


SUGGESTED: List[Suggestion] = [
    Suggestion(
        key="heatmap",
        title="Review Heatmap",
        short="Your reviews and streak as a calendar on the deck list.",
        author="Glutanimate",
        code="1771074083",
        standalone=["1771074083", "review_heatmap", "review-heatmap", "1722241614", "723520343"],
        builtin_default=True,
    ),
    Suggestion(
        key="lifedrain",
        title="Life Drain",
        short="A life bar that drains while you think about a card.",
        author="Yutsuten",
        code="715575551",
        standalone=["715575551", "lifedrain", "anki-lifedrain"],
        builtin_default=False,
    ),
]

SUGGESTED_BY_KEY: Dict[str, Suggestion] = {s.key: s for s in SUGGESTED}


def installed_copy(suggestion: Suggestion, folders: Dict[str, bool]) -> Optional[Tuple[str, bool]]:
    """(folder, enabled) of an installed copy; an enabled copy wins. None if none."""
    found = None
    for folder in suggestion.standalone:
        if folder in folders:
            if folders[folder]:
                return folder, True
            found = found or (folder, False)
    return found


def was_builtin_on(suggestion: Suggestion, state: dict) -> bool:
    enabled = state.get("enabled") if isinstance(state, dict) else None
    if not isinstance(enabled, dict):
        enabled = {}
    return bool(enabled.get(suggestion.key, suggestion.builtin_default))


def to_offer(state: dict, folders: Dict[str, bool]) -> List[Tuple[str, str]]:
    """What the one-time question after the update offers: [(key, action)].

    ``folders`` maps every installed add-on folder to whether it is enabled.
    action "install": the built-in copy was on and no copy is installed.
    action "enable": the built-in copy was on and the user's own copy is
    installed but switched off (Smart Study switched it off when the user
    chose the built-in one).  Nothing once the question was handled.
    """
    if isinstance(state, dict) and state.get(ASKED_KEY):
        return []
    offer = []
    for suggestion in SUGGESTED:
        if not was_builtin_on(suggestion, state):
            continue
        copy = installed_copy(suggestion, folders)
        if copy is None:
            offer.append((suggestion.key, "install"))
        elif not copy[1]:
            offer.append((suggestion.key, "enable"))
    return offer


def startup_plan(state: dict, folders: Dict[str, bool], onboarded: bool, first_start: bool) -> Tuple[List[Tuple[str, str]], bool]:
    """(what to offer now, whether to remember the question as handled).

    A new user (setup wizard on this start) never had the built-in copies:
    remember without asking.  A profile that has not finished the setup is
    skipped for now.  Otherwise offer what ``to_offer`` finds; nothing to
    offer counts as handled too.
    """
    if isinstance(state, dict) and state.get(ASKED_KEY):
        return [], False
    if first_start:
        return [], True
    if not onboarded:
        return [], False
    offer = to_offer(state, folders)
    return offer, not offer
