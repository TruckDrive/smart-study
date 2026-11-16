# -*- coding: utf-8 -*-

try:
    from .quiet import ignored as _ignored
except ImportError:  # the module is loaded on its own (tests)
    def _ignored(*_args):
        pass

import traceback
import uuid
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

# --- Anki/Qt Imports ---
from aqt import mw

# Importing __init__ from here creates a circular dependency during add-on
# startup. Resolve the immutable package path/name directly instead.
ADDON_NAME = __name__.split('.')[0]

try:
    from .locales import _
except ImportError:
    def _(text):  # type: ignore
        return text

# --- Konstanten ---
DEADLINE_CONFIG_KEY = f"addon_{ADDON_NAME}_deadline_data"


# ---------------------------------------------------------------------------
# DeadlineManager
# ---------------------------------------------------------------------------

class DeadlineManager:
    DATE_FORMAT = "%Y-%m-%d"

    def __init__(self):
        self.data: Dict = self._default_data()
        self.load_data()

    # ── Defaults & Migration ────────────────────────────────────────────────

    def _default_data(self) -> Dict:
        return {
            "deadlines": [],
            "pinned_id": None,
            "enabled": True,
        }

    def _migrate_old_format(self, conf: dict) -> dict:
        """Convert single-deadline format (pre-multi) to list format."""
        if "title" in conf or "start_date" in conf:
            deadline = {
                "id": str(uuid.uuid4())[:8],
                "name": conf.get("title", _("My Deadline")),
                "start_date": conf.get("start_date", date.today().strftime(self.DATE_FORMAT)),
                "end_date": conf.get("end_date", (date.today() + timedelta(days=7)).strftime(self.DATE_FORMAT)),
            }
            return {
                "deadlines": [deadline],
                "pinned_id": None,
                "enabled": conf.get("enabled", True),
            }
        return conf

    # ── Persistence ─────────────────────────────────────────────────────────

    def load_data(self):
        if not mw or not mw.col:
            self.data = self._default_data()
            return
        conf = mw.col.conf.get(DEADLINE_CONFIG_KEY)
        if conf and isinstance(conf, dict):
            conf = self._migrate_old_format(conf)
            merged = self._default_data()
            merged.update(conf)
            self.data = merged
        else:
            self.data = self._default_data()
            if conf is None:
                self.save_data()

    def save_data(self):
        if mw and mw.col:
            try:
                mw.col.conf[DEADLINE_CONFIG_KEY] = self.data
            except Exception as e:
                print(f"{ADDON_NAME} (Deadline): ERROR saving: {e}")
                traceback.print_exc()
        else:
            print(f"{ADDON_NAME} (Deadline): WARN - Cannot save, mw.col not available.")

    # ── Multi-Deadline CRUD ─────────────────────────────────────────────────

    def get_all_deadlines(self) -> List[Dict]:
        """Return deadlines sorted by end_date ascending."""
        deadlines = self.data.get("deadlines", [])
        try:
            return sorted(deadlines, key=lambda d: d.get("end_date", "9999-12-31"))
        except Exception:
            return list(deadlines)

    def get_active_deadline(self) -> Optional[Dict]:
        """Return pinned deadline, or nearest upcoming, or most recent past."""
        deadlines = self.get_all_deadlines()
        if not deadlines:
            return None

        pinned_id = self.data.get("pinned_id")
        if pinned_id:
            for d in deadlines:
                if d.get("id") == pinned_id:
                    return d
            # Pinned ID no longer exists — fall through to auto
            self.data["pinned_id"] = None

        # Auto: nearest upcoming (end_date >= today)
        today = date.today()
        upcoming = []
        for d in deadlines:
            try:
                if datetime.strptime(d["end_date"], self.DATE_FORMAT).date() >= today:
                    upcoming.append(d)
            except Exception:
                _ignored()
        if upcoming:
            return upcoming[0]  # sorted by end_date, so first = nearest
        return deadlines[-1]   # all past → show most recent

    # ── Progress Calculation ─────────────────────────────────────────────────

    def get_deadline_info(self) -> Optional[Dict]:
        if not self.data.get("enabled", False):
            return None
        return self.get_active_deadline()

    def calculate_progress(self) -> Optional[Dict]:
        info = self.get_deadline_info()
        if not info:
            return None
        try:
            today = date.today()
            start = datetime.strptime(info["start_date"], self.DATE_FORMAT).date()
            end   = datetime.strptime(info["end_date"],   self.DATE_FORMAT).date()
            title_display = info.get("name") or _("Deadline")

            if start > end:
                return {"title": _("Deadline Error"), "progress": 0,
                        "tooltip": _("Error: Start date is after end date")}

            total_days   = (end - start).days
            elapsed_days = (today - start).days

            if today < start:
                progress      = 0
                days_remaining = (end - today).days
                start_delta   = (start - today).days
                tip = _("{} | Starts in {} day(s) | Ends in {} day(s)").format(
                    title_display, start_delta, days_remaining)
            elif today > end:
                progress      = 100
                days_remaining = 0
                end_delta     = (today - end).days
                tip = _("{} | Ended {} day(s) ago").format(title_display, end_delta)
            else:
                days_remaining = (end - today).days
                if total_days <= 0:
                    progress = 100 if today >= start else 0
                else:
                    progress = max(0, min(100, int((max(0, elapsed_days) / total_days) * 100)))
                tip = _("{} | {} day(s) remaining").format(title_display, days_remaining)

            return {
                "title": title_display, "progress": progress,
                "tooltip": tip, "days_remaining": days_remaining,
                "deadline_id": info.get("id"),
            }
        except (ValueError, TypeError, KeyError) as e:
            return {"title": _("Deadline Error"), "progress": 0,
                    "tooltip": _("Error: Invalid date configuration ({})").format(e)}
        except Exception as e:
            traceback.print_exc()
            return {"title": _("Deadline Error"), "progress": 0,
                    "tooltip": _("Error: {}").format(e)}
