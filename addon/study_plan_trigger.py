# -*- coding: utf-8 -*-

import traceback
from typing import Optional, Callable

# --- Anki Imports ---
try:
    from aqt import mw
    from aqt.utils import tooltip
except ImportError:
    mw = None
    tooltip = lambda s: print(f"Tooltip (aqt unavailable): {s}")

try:
    from .locales import _
except ImportError:
    def _(text):  # type: ignore
        return text

# --- Global function references (set during addon init) ---
_trigger_gamification_sidebar_func: Optional[Callable] = None


def set_gamification_sidebar_trigger_function(func: Callable):
    """Wird von __init__.py aufgerufen, um die Funktion zum Umschalten der Sidebar zu übergeben."""
    global _trigger_gamification_sidebar_func
    _trigger_gamification_sidebar_func = func


# --- Trigger-Funktionen, die vom Launcher-Button aufgerufen werden ---

def trigger_gamification_sidebar_action():
    """Löst das Anzeigen/Verstecken der Gamification-Sidebar aus."""
    print("\n--- Triggering Gamification Sidebar ---")
    if _trigger_gamification_sidebar_func and callable(_trigger_gamification_sidebar_func):
        try:
            _trigger_gamification_sidebar_func()
        except Exception as e:
            msg = _("Error triggering Gamification Sidebar action: {}").format(e)
            print(f"ERROR: {msg}")
            traceback.print_exc()
            tooltip(msg)
    else:
        msg = _("Cannot trigger Gamification Sidebar: Function not initialized by main addon.")
        print(f"ERROR: {msg}")
        tooltip(msg)