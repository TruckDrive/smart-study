# -*- coding: utf-8 -*-
"""Errors that are ignored on purpose, without hiding them.

Many places carry on when something small fails (a widget that is already
gone, an optional feature, a setting from an older version).  ``ignored()``
is called in such an ``except`` block instead of a bare ``pass``: the add-on
behaves exactly as before, but the error is printed once per place and kept
for the diagnostics, so a real bug no longer disappears without a trace.
"""
import os
import sys
import traceback
from collections import deque
from typing import Deque, List, Set, Tuple

_seen: Set[Tuple[str, int]] = set()
_recent: Deque[str] = deque(maxlen=100)


def ignored(note: str = "") -> None:
    """Call inside an ``except`` block.  Never raises."""
    try:
        kind, error, tb = sys.exc_info()
        frame = sys._getframe(1)
        place = (frame.f_code.co_filename, frame.f_lineno)
        if place in _seen:
            return
        _seen.add(place)
        where = f"{os.path.basename(place[0])}:{place[1]}"
        name = kind.__name__ if kind else "error"
        line = f"Smart Study: ignored {name} in {where}: {error}" + (f" ({note})" if note else "")
        if tb is not None:
            last = traceback.extract_tb(tb)[-1]
            line += f" [raised at {os.path.basename(last.filename)}:{last.lineno}]"
        _recent.append(line)
        print(line)
    except Exception:
        pass  # reporting must never become the problem


def recent() -> List[str]:
    """The last ignored errors, oldest first (for the diagnostics window)."""
    return list(_recent)
