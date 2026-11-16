# -*- coding: utf-8 -*-

try:
    from .quiet import ignored as _ignored
except ImportError:  # the module is loaded on its own (tests)
    def _ignored(*_args):
        pass

import json
import random
import os
import time
from datetime import date, datetime, timedelta
import traceback
from typing import Union, List, Dict, Optional, Any
from .achievements import BADGES, ReviewHistory, update_achievements

from aqt import mw
from aqt.utils import tooltip

try:
    from . import constants
    ADDON_FOLDER_NAME = constants.addon_package_name
except (ImportError, AttributeError):
    ADDON_FOLDER_NAME = "SmartStudy1"

try:
    from .locales import _
except ImportError:
    def _(text):  # type: ignore
        return text


ADDON_NAME = "GamificationPlusDailyWidgets_" + ADDON_FOLDER_NAME
CONFIG_KEY = f"addon_{ADDON_NAME}_data"
# Where Synapse (package "SynapsePro1") kept the same data; imported once
SYNAPSE_CONFIG_KEY = "addon_GamificationPlusDailyWidgets_SynapsePro1_data"

# --- Gamification Balancing ---
XP_PER_MINUTE_STUDIED = 10
XP_FOR_DAILY_CHALLENGE_BASE = 120
XP_FOR_DAILY_CHALLENGE_PER_LEVEL = 5
XP_PER_STREAK_DAY = 20
XP_LEVEL_BASE = 100
XP_LEVEL_FACTOR = 1.065

# --- Rank Struktur mit .gif ---
RANKS: List[Dict[str, Any]] = [
    {"level": 0,   "name": "Anki<br>Starter",          "image": "rang1.gif"},
    {"level": 5,   "name": "Card<br>Crawler",       "image": "rang2.gif"},
    {"level": 10,  "name": "Note<br>Nerd",        "image": "rang3.gif"},
    {"level": 15,  "name": "Deck<br>Diver",         "image": "rang4.gif"},
    {"level": 20,  "name": "Review<br>Rookie",      "image": "rang5.gif"},
    {"level": 25,  "name": "Recall<br>Rabbit",     "image": "rang6.gif"},
    {"level": 30,  "name": "Memory<br>Mover",       "image": "rang7.gif"},
    {"level": 35,  "name": "Recall<br>Ranger",      "image": "rang8.gif"},
    {"level": 40,  "name": "Smart Study<br>Scout",      "image": "rang9.gif"},
    {"level": 45,  "name": "Fact<br>Ferret",        "image": "rang10.gif"},
    {"level": 50,  "name": "Focus<br>Falcon",       "image": "rang11.gif"},
    {"level": 55,  "name": "Recall<br>Raider",      "image": "rang12.gif"},
    {"level": 60,  "name": "Cognition<br>Crafter", "image": "rang13.gif"},
    {"level": 65,  "name": "Focus<br>Forager",     "image": "rang14.gif"},
    {"level": 70,  "name": "Knowledge<br>Knight",  "image": "rang15.gif"},
    {"level": 75,  "name": "Memory<br>Mage",       "image": "rang16.gif"},
    {"level": 80,  "name": "Review<br>Rocket",       "image": "rang17.gif"},
    {"level": 85,  "name": "Study<br>Samurai",     "image": "rang18.gif"},
    {"level": 90,  "name": "Flashcard<br>Fanatic", "image": "rang19.gif"},
    {"level": 95,  "name": "Neuro<br>Ninja",       "image": "rang20.gif"},
    {"level": 100, "name": "Anki<br>Admiral",      "image": "rang21.gif"}
]
DEFAULT_RANK_INFO = RANKS[0]

# --- Daily Challenges ---
# Every challenge is MEASURABLE from Anki's review log, so completion can be
# verified automatically. "type" selects the metric, "target" the goal.
# Text templates are translated via locales.py; "{}" receives the target.
CHALLENGE_TEXT_TEMPLATES: Dict[str, str] = {
    "reviews":    "Review {} cards today.",
    "new_cards":  "Learn {} new cards today.",
    "study_time": "Study for {} minutes today.",
    "decks":      "Review cards from {} different decks today.",
}

DAILY_CHALLENGES: List[Dict[str, Any]] = [
    {"type": "reviews",    "target": 30},
    {"type": "reviews",    "target": 50},
    {"type": "reviews",    "target": 75},
    {"type": "reviews",    "target": 100},
    {"type": "reviews",    "target": 150},
    {"type": "reviews",    "target": 200},
    {"type": "new_cards",  "target": 5},
    {"type": "new_cards",  "target": 10},
    {"type": "new_cards",  "target": 15},
    {"type": "new_cards",  "target": 20},
    {"type": "study_time", "target": 10},
    {"type": "study_time", "target": 15},
    {"type": "study_time", "target": 30},
    {"type": "study_time", "target": 45},
    {"type": "study_time", "target": 60},
    {"type": "decks",      "target": 2},
    {"type": "decks",      "target": 3},
]


def _anki_today() -> date:
    """Current scheduler day, respecting the collection rollover hour."""
    try:
        rollover = max(0, min(23, int(mw.col.conf.get("rollover", 4))))
    except Exception:
        rollover = 4
    return (datetime.now() - timedelta(hours=rollover)).date()


def _anki_today_int() -> int:
    return int(_anki_today().strftime("%Y%m%d"))

def calculate_streak_from_revlog(rules=None) -> int:
    """
    Berechnet den aktuellen Streak dynamisch aus der revlog-Tabelle.

    Performance: The revlog is read in bounded windows, newest first: 30, 60,
    120 and 160 days (370 together), then one year at a time. As soon as the
    first missing day ends the streak, older history is never touched, so a
    short streak costs a month of rows instead of a year. Still exact.

    WICHTIG (Bugfix): Die Tageszuordnung nutzt SQLites 'localtime'-Modifier,
    der für jeden Zeitstempel die *damals* gültige Zeitzonenregel (Sommer-/
    Winterzeit) anwendet. Die frühere Variante hat den AKTUELLEN DST-Offset
    auf die gesamte Historie angewendet — dadurch verschob sich die Tages-
    grenze für alle Winterdaten um eine Stunde (effektiv Rollover 3 Uhr statt
    4 Uhr), und Reviews zwischen 3 und 4 Uhr nachts rutschten auf den
    Folgetag. Ergebnis: fälschlich gerissene Streaks, z. B. exakt am
    Jahreswechsel bei einer Lernsession in der Silvesternacht.

    Regeln:
    - Konfigurierbare Mindestzahl echter Reviews (ease > 0), kein Rescheduling
    - Optional alternativ eine Mindestzahl erstellter, noch vorhandener Karten
    - Ankis Rollover-Stunde + historisch korrekte lokale Zeitzone
    - Streak = aufeinanderfolgende Lerntage endend bei heute/gestern
    - Wenn letzter Lerntag vorgestern oder früher → Streak = 0
    """
    if not mw or not mw.col:
        return 0
    try:
        from datetime import date as _date

        rules = rules or {}
        minimum = max(1, min(10000, int(rules.get("reviews", 1))))
        creation_minimum = max(1, min(10000, int(rules.get("cards", 1))))
        rollover = int(mw.col.conf.get("rollover", 4))

        # "Today" as an Anki day (datetime.now() is already correct local time).
        today_anki_date = (datetime.now() - timedelta(hours=rollover)).date()
        chunk_days = 30
        later_chunks = iter((60, 120, 160))
        chunk_end = today_anki_date + timedelta(days=1)
        chunk_start = chunk_end - timedelta(days=chunk_days)

        def load_days(start_day, end_day):
            # Bounds use local rollover datetimes, while SQL retains the same
            # historical localtime/DST bucketing as the previous implementation.
            start_dt = datetime.combine(start_day, datetime.min.time()) + timedelta(hours=rollover)
            end_dt = datetime.combine(end_day, datetime.min.time()) + timedelta(hours=rollover)
            rows = mw.col.db.all(
                "SELECT strftime('%Y-%m-%d', id / 1000, "
                "'unixepoch', 'localtime', ?) AS d "
                "FROM revlog WHERE ease > 0 AND id >= ? AND id < ? "
                "GROUP BY d HAVING count(*) >= ?",
                f"-{rollover} hours",
                int(start_dt.timestamp() * 1000),
                int(end_dt.timestamp() * 1000),
                minimum,
            )
            if rules.get("allowCards", False):
                rows += mw.col.db.all(
                    "SELECT strftime('%Y-%m-%d', id / 1000, 'unixepoch', 'localtime', ?) AS d "
                    "FROM cards WHERE id >= ? AND id < ? GROUP BY d HAVING count(*) >= ?",
                    f"-{rollover} hours", int(start_dt.timestamp() * 1000),
                    int(end_dt.timestamp() * 1000), creation_minimum,
                )
            return {_date.fromisoformat(r[0]) for r in rows if r and r[0]}

        study_days = load_days(chunk_start, chunk_end)
        if today_anki_date in study_days:
            check_day = today_anki_date
        elif today_anki_date - timedelta(days=1) in study_days:
            check_day = today_anki_date - timedelta(days=1)
        else:
            return 0

        streak = 0
        while True:
            if check_day < chunk_start:
                chunk_end = chunk_start
                chunk_days = next(later_chunks, 370)
                chunk_start = chunk_end - timedelta(days=chunk_days)
                study_days = load_days(chunk_start, chunk_end)
            if check_day not in study_days:
                break
            streak += 1
            check_day -= timedelta(days=1)
        return streak

    except Exception as e:
        print(f"SmartStudy: Fehler bei Streak-Berechnung aus revlog: {e}")
        traceback.print_exc()
        return 0


class GamificationManager:
    """Handles all gamification logic: XP, levels, ranks, streaks, challenges."""

    def __init__(self, addon_path: Optional[str]):
        self.data: Dict = {}
        self.load_data()
        self._streak_cache: Optional[int] = None
        self._streak_source_key = None
        self._challenge_progress_cache = None
        self._badge_history = ReviewHistory()
        self._todays_challenge: Optional[Dict] = None
        challenge_id = self.data.get("current_challenge_id")
        if challenge_id is not None:
             try: self._todays_challenge = DAILY_CHALLENGES[int(challenge_id)]
             except (IndexError, ValueError, TypeError): self._todays_challenge = None; self.data["current_challenge_id"] = None

    def _default_data(self) -> Dict:
        yest = int((_anki_today() - timedelta(days=1)).strftime("%Y%m%d"))
        return {"level": 1, "xp": 0, "streak": 0, "last_login_day": 0,
                "last_time_xp_check_day": yest, "current_challenge_id": None,
                "challenge_completed_day": 0, "version": 4}

    # ------------------------------------------------------------------
    # JSON backup helpers (resilient against Anki schema upgrades that
    # can wipe mw.col.conf entries)
    # ------------------------------------------------------------------

    def _get_profile_data_path(self) -> Optional[str]:
        """Returns the path to the profile-specific JSON backup file."""
        try:
            profile_folder = mw.pm.profileFolder()
            data_folder = os.path.join(profile_folder, "SmartStudy_Data")
            os.makedirs(data_folder, exist_ok=True)
            return os.path.join(data_folder, "gamification_data.json")
        except Exception:
            return None

    def _load_from_json_backup(self) -> Optional[Dict]:
        """Try to load gamification data from the JSON backup file."""
        try:
            path = self._get_profile_data_path()
            if path and os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    print(f"{ADDON_NAME}: Loaded gamification data from JSON backup.")
                    return data
        except Exception as e:
            print(f"{ADDON_NAME}: Could not read JSON backup: {e}")
        return None

    def _save_to_json_backup(self):
        """Save gamification data to the JSON backup file (profile folder)."""
        tmp_path = None
        try:
            path = self._get_profile_data_path()
            if path:
                # Write beside the destination and replace atomically. If Anki
                # or the computer stops mid-write, the previous valid backup
                # remains intact instead of becoming a truncated JSON file.
                tmp_path = path + ".tmp"
                with open(tmp_path, 'w', encoding='utf-8') as f:
                    json.dump(self.data, f, indent=2)
                os.replace(tmp_path, path)
        except Exception as e:
            print(f"{ADDON_NAME}: Could not write JSON backup: {e}")
            if tmp_path:
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass

    def load_data(self):
        # Defensive: if no collection is loaded yet, fall back to the JSON
        # backup (or defaults) instead of crashing on mw.col being None.
        if not mw or not mw.col:
            base = self._default_data()
            backup = self._load_from_json_backup()
            if isinstance(backup, dict):
                base.update(backup)
            self.data = base
            return
        conf = mw.col.conf.get(CONFIG_KEY)
        defaults = self._default_data()
        loaded_from_col = False

        if conf and isinstance(conf, dict):
            self.data = conf
            loaded_from_col = True
        else:
            # mw.col.conf had no data — this happens after an Anki update that
            # performs a schema migration or resets collection config.
            # Fall back to the JSON backup stored in the profile folder.
            backup = self._load_from_json_backup()
            if backup and isinstance(backup, dict):
                self.data = backup
                # Restore into col.conf so future saves are consistent.
                try:
                    mw.col.conf[CONFIG_KEY] = self.data
                except Exception:
                    _ignored()
                print(f"{ADDON_NAME}: Restored gamification data from JSON backup after col.conf loss.")
            else:
                self.data = defaults

        imported_level = self._import_synapse_progress()

        # Fill in any missing keys from a newer version of the addon.
        updated = imported_level is not None
        for k, v in defaults.items():
            if k not in self.data:
                self.data[k] = v
                updated = True
        if self.data.get("version", 0) < defaults["version"]:
            self.data["version"] = defaults["version"]
            updated = True

        if updated or not loaded_from_col:
            self.save_data()
        if imported_level is not None:
            from aqt.qt import QTimer
            QTimer.singleShot(1500, lambda: tooltip(
                _("Your Synapse level {} was carried over to Smart Study.").format(imported_level),
                period=8000))

    def _load_synapse_data(self) -> Optional[Dict]:
        """Level data Synapse left behind: collection config first, then its profile backup."""
        try:
            data = mw.col.get_config(SYNAPSE_CONFIG_KEY, None)
        except Exception:
            data = None
        if not isinstance(data, dict):
            try:
                path = os.path.join(mw.pm.profileFolder(), "SynapsePro_Data", "gamification_data.json")
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                return None
        return data if isinstance(data, dict) else None

    def _import_synapse_progress(self) -> Optional[int]:
        """Takes over Synapse's level once if it is ahead; returns the imported level.

        Removing an add-on keeps its collection config and profile files, so a
        Synapse user switching to Smart Study would otherwise start again at 1.
        The XP ledger comes along, so time studied since then is still paid.
        """
        if self.data.get("synapse_import_done"):
            return None
        old = self._load_synapse_data()
        if not old:
            return None  # nothing yet; may arrive with a later sync
        try:
            old_rank = (int(old.get("level", 1)), int(old.get("xp", 0)))
        except (TypeError, ValueError):
            return None
        ahead = old_rank > (int(self.data.get("level", 1)), int(self.data.get("xp", 0)))
        if ahead:
            self.data = dict(old)
        self.data["synapse_import_done"] = True
        return old_rank[0] if ahead else None

    def save_data(self):
        if mw.col:
            try:
                mw.col.conf[CONFIG_KEY] = self.data
            except Exception as e:
                print(f"{ADDON_NAME} ERROR saving gamification data to col.conf: {e}")
                traceback.print_exc()
        # Always write the JSON backup so data survives future collection migrations.
        self._save_to_json_backup()

    def get_xp_for_level(self, level: int) -> Union[int, float]:
        if level < 1: return 0
        try:
            needed = round(XP_LEVEL_BASE * (XP_LEVEL_FACTOR ** (level - 1)))
            return max(1, needed)
        except OverflowError:
            return float('inf')

    def get_rank_info_for_level(self, level_to_check: int) -> Dict[str, Any]:
        selected_rank = DEFAULT_RANK_INFO
        for rank_info in reversed(RANKS):
            if level_to_check >= rank_info["level"]:
                selected_rank = rank_info
                break
        return selected_rank

    def get_current_rank_info(self) -> Dict[str, Any]:
        return self.get_rank_info_for_level(self.data.get("level", 1))

    def get_rank_name(self) -> str:
        return self.get_current_rank_info().get("name", DEFAULT_RANK_INFO["name"])

    def get_all_ranks(self) -> List[Dict[str, Any]]:
        return RANKS

    def get_rank_image_path(self, image_filename: Optional[str]) -> Optional[str]:
        if not image_filename or not hasattr(constants, 'icons_folder'):
            return None
        try:
            return os.path.join(constants.icons_folder, image_filename)
        except Exception:
            return None

    def add_xp(self, amount: int, reason: str = "", *, persist: bool = True) -> bool:
        if amount <= 0: return False
        current_xp = self.data.get("xp", 0)
        current_level = self.data.get("level", 1)
        new_total_xp_at_level = current_xp + amount
        needed_for_current_level = self.get_xp_for_level(current_level)
        levels_gained = 0
        while needed_for_current_level != float('inf') and new_total_xp_at_level >= needed_for_current_level:
            new_total_xp_at_level -= needed_for_current_level
            current_level += 1
            levels_gained += 1
            needed_for_current_level = self.get_xp_for_level(current_level)
        if levels_gained > 0:
            self.data["level"] = current_level
            # Dashboard celebrations respect the user's per-event preferences.
        self.data["xp"] = int(round(new_total_xp_at_level))
        if persist:
            self.save_data()
        return True

    def credit_study_xp(self, session_start_ms=None) -> int:
        """Credit only the unpaid total since the legacy finalized-day boundary.

        Aggregate rather than use a last-review cursor: late synced reviews can
        have older IDs. Keep a high-water mark so repeated callbacks, restarts
        and review undo cannot pay the same accumulated time twice. Fractions
        carry between sessions. No per-review writes or extra tables required.
        """
        if not mw.col:
            return 0
        from copy import deepcopy
        old_data = deepcopy(self.data)
        self.data = deepcopy(old_data)
        try:
            ledger = self.data.get("study_xp_ledger")
            if ledger is None:
                try:
                    first_day = datetime.strptime(str(self.data.get(
                        "last_time_xp_check_day", 0)), "%Y%m%d").date()
                except (TypeError, ValueError):
                    first_day = _anki_today() - timedelta(days=1)
                if first_day > _anki_today():
                    raise ValueError("Future study XP boundary")
                start = datetime.combine(first_day, datetime.min.time()) + timedelta(
                    hours=self._get_rollover_hour())
                ledger = {"start_ms": int(start.timestamp() * 1000), "paid": 0}
            start_ms, paid = int(ledger["start_ms"]), int(ledger["paid"])
            if start_ms < 0 or paid < 0:
                raise ValueError("Invalid study XP ledger")
            now_ms = int(time.time() * 1000)
            session_ms = int(session_start_ms) if session_start_ms is not None else now_ms + 1
            row = mw.col.db.first(
                "SELECT COALESCE(SUM(t), 0), "
                "COALESCE(SUM(CASE WHEN id >= ? THEN t ELSE 0 END), 0) "
                "FROM (SELECT id, CASE WHEN time > 45000 THEN 45000 "
                "WHEN time < 0 THEN 0 ELSE time END AS t FROM revlog "
                "WHERE ease > 0 AND id >= ? AND id <= ?)",
                session_ms, start_ms, now_ms)
            total_ms, session_time_ms = row
            earned = int(total_ms) * XP_PER_MINUTE_STUDIED // 60000
            gain = max(0, earned - paid)
            ledger = {"start_ms": start_ms, "paid": max(paid, earned)}
            self.data["study_xp_ledger"] = ledger
            if gain:
                self.add_xp(gain, "Study Time", persist=False)
            if self.data != old_data:
                # XP and its receipt are one config value. A failed write must
                # leave both unchanged, allowing a later callback to retry.
                mw.col.conf[CONFIG_KEY] = deepcopy(self.data)
                self._save_to_json_backup()
            if session_start_ms is not None:
                if getattr(self, "_study_session_start", None) != session_ms:
                    self._study_session_start = session_ms
                    self._study_session_xp = 0
                before_session = (int(total_ms) - int(session_time_ms)) * XP_PER_MINUTE_STUDIED // 60000
                self._study_session_xp += min(gain, max(0, earned - before_session))
            return gain
        except Exception as exc:
            self.data = old_data
            print(f"SmartStudy: Study XP not credited; will retry: {exc}")
            return 0

    def _get_rollover_hour(self) -> int:
        """
        Returns Anki's configured day-rollover hour (default 4).
        Reviews before this hour count as the *previous* calendar day in Anki's
        scheduler. We need to account for this when checking streak boundaries.
        """
        try:
            return int(mw.col.conf.get("rollover", 4))
        except Exception:
            return 4

    def check_and_update_streak_and_time_xp(self) -> bool:
        today_int = _anki_today_int()
        last_login_day = self.data.get("last_login_day", 0)
        xp_gain_streak = 0
        streak_reason = ""
        data_changed = False

        if today_int > last_login_day:
            data_changed = True

            # Recalculate streak from revlog (not from stored config counter).
            current_streak = calculate_streak_from_revlog(self.data.get("streak_rules"))
            self._streak_cache = current_streak

            # Keep data["streak"] in sync for compatibility.
            self.data["streak"] = current_streak

            if current_streak > 1:
                xp_gain_streak = current_streak * XP_PER_STREAK_DAY
                streak_reason = f"Daily Streak: Day {current_streak} (+{xp_gain_streak} XP)"
                tooltip(_("Streak: {} days!\n+{} XP Bonus").format(current_streak, xp_gain_streak), period=4000)
            else:
                # No active streak: award base daily login XP.
                xp_gain_streak = XP_PER_STREAK_DAY
                streak_reason = f"Daily Login (+{xp_gain_streak} XP)"

            self.assign_new_daily_challenge()
            self.data["last_login_day"] = today_int
        
        if xp_gain_streak > 0:
            self.add_xp(xp_gain_streak, streak_reason)
        elif data_changed:
            self.save_data()
        # Reconcile today's reviews too; never finalize an unread time range.
        return self.credit_study_xp() > 0 or data_changed

    def assign_new_daily_challenge(self):
        if not DAILY_CHALLENGES: return
        self._challenge_progress_cache = None
        self.data["challenge_completed_day"] = 0
        challenge_index = random.randrange(len(DAILY_CHALLENGES))
        self.data["current_challenge_id"] = challenge_index
        try:
            self._todays_challenge = DAILY_CHALLENGES[challenge_index]
        except IndexError:
            self._todays_challenge = None
            self.data["current_challenge_id"] = None

    def _get_valid_challenge(self) -> Optional[Dict[str, Any]]:
        """Return today's challenge dict, assigning a fresh one if needed."""
        challenge_id = self.data.get("current_challenge_id")
        if isinstance(challenge_id, int) and 0 <= challenge_id < len(DAILY_CHALLENGES):
            return DAILY_CHALLENGES[challenge_id]
        # Missing / legacy / out-of-range id → assign a new measurable one.
        self.assign_new_daily_challenge()
        self.save_data()
        return self._todays_challenge

    @staticmethod
    def _challenge_text(challenge: Optional[Dict[str, Any]]) -> str:
        if not challenge:
            return _("No challenge available.")
        tpl = CHALLENGE_TEXT_TEMPLATES.get(challenge.get("type", ""), "")
        if not tpl:
            return _("No challenge available.")
        return _(tpl).format(challenge.get("target", 0))

    def get_current_challenge(self) -> tuple[str, int]:
        return self._challenge_text(self._get_valid_challenge()), 0

    def _day_start_ms(self) -> int:
        """Epoch ms of the start of the current Anki day (respects rollover)."""
        try:
            cutoff = None
            sched = getattr(mw.col, "sched", None)
            if sched is not None:
                cutoff = getattr(sched, "day_cutoff", None)   # modern Anki
                if cutoff is None:
                    cutoff = getattr(sched, "dayCutoff", None)  # legacy Anki
            if cutoff:
                return (int(cutoff) - 86400) * 1000
        except Exception:
            _ignored()
        # Fallback: derive the configured rollover boundary locally.
        start = (datetime.combine(_anki_today(), datetime.min.time())
                 + timedelta(hours=self._get_rollover_hour()))
        return int(start.timestamp() * 1000)

    def get_challenge_progress(self) -> tuple[int, int]:
        """Return (current, target) for today's challenge, measured from revlog."""
        challenge = self._get_valid_challenge()
        if not challenge or not mw or not mw.col:
            return 0, 1
        ctype  = challenge.get("type", "")
        target = max(1, int(challenge.get("target", 1)))
        start_ms = self._day_start_ms()
        cache_key = (
            self.data.get("current_challenge_id"), ctype, target, start_ms)
        cached = self._challenge_progress_cache
        now = time.monotonic()
        # The dashboard asks for the same value back-to-back during one
        # render. Coalesce only that
        # tiny burst; review boundaries explicitly invalidate the cache.
        if cached and cached[0] == cache_key and now - cached[1] <= 0.5:
            return cached[2]
        try:
            if ctype == "reviews":
                current = mw.col.db.scalar(
                    "SELECT COUNT(*) FROM revlog WHERE id >= ? AND ease > 0", start_ms) or 0
            elif ctype == "new_cards":
                # Cards that had a learning-step review today (revlog type 0).
                current = mw.col.db.scalar(
                    "SELECT COUNT(DISTINCT cid) FROM revlog WHERE id >= ? AND type = 0",
                    start_ms) or 0
            elif ctype == "study_time":
                total_ms = mw.col.db.scalar(
                    "SELECT SUM(time) FROM revlog WHERE id >= ?", start_ms) or 0
                current = int(total_ms / 60000)
            elif ctype == "decks":
                current = mw.col.db.scalar(
                    "SELECT COUNT(DISTINCT c.did) FROM revlog r "
                    "JOIN cards c ON r.cid = c.id WHERE r.id >= ?", start_ms) or 0
            else:
                current = 0
        except Exception as e:
            print(f"{ADDON_NAME}: challenge progress query error: {e}")
            current = 0
        result = (min(int(current), target), target)
        self._challenge_progress_cache = (cache_key, now, result)
        return result

    def invalidate_dashboard_cache(self, full=False) -> None:
        """Invalidate values that may have changed during a review session."""
        self._streak_cache = None
        self._challenge_progress_cache = None
        self._badge_history.invalidate(full=full)

    def get_achievements(self):
        """Use existing profile persistence and award each tier only once."""
        if not mw or not mw.col:
            return []
        try:
            today = _anki_today()
            counts = self._badge_history.read(mw.col.db, today, self._get_rollover_hour())
            badges, changed = update_achievements(
                self.data, counts, today,
                self.is_challenge_completed_today() or self.is_challenge_achieved(), _)
            if changed:
                self.save_data()
            return badges
        except Exception as exc:
            print(f"SmartStudy: achievement refresh failed: {exc}")
            return []

    def mark_achievement_seen(self, badge_id: str) -> bool:
        """Mark every currently earned tier of one badge as viewed."""
        valid_ids = {badge[0] for badge in BADGES}
        if badge_id not in valid_ids:
            return False
        state = self.data.setdefault("achievements", {"earned": {}, "challenge_days": []})
        earned = state.setdefault("earned", {}).get(badge_id, {})
        seen = state.setdefault("seen", {})
        current = seen.get(badge_id, [])
        viewed = sorted(key for key in earned if str(key).isdigit()) if isinstance(earned, dict) else []
        if current == viewed:
            return False
        seen[badge_id] = viewed
        self.save_data()
        return True

    def toggle_favorite_achievement(self, badge_id: str) -> bool:
        """Select one earned badge as the profile favorite, or clear it."""
        badges = self.get_achievements()
        badge = next((item for item in badges if item.get("id") == badge_id), None)
        if not badge or badge.get("tier", -1) < 0:
            return False
        state = self.data.setdefault("achievements", {"earned": {}, "challenge_days": []})
        state["favorite"] = None if state.get("favorite") == badge_id else badge_id
        self.save_data()
        return True

    def refresh_streak_cache(self, persist: bool = False) -> int:
        """Recalculate the streak once and optionally persist it for restarts."""
        streak = calculate_streak_from_revlog(self.data.get("streak_rules"))
        self._streak_cache = streak
        if self.data.get("streak") != streak:
            self.data["streak"] = streak
            if persist:
                self.save_data()
        return streak

    def is_challenge_achieved(self) -> bool:
        """True if today's challenge goal has actually been reached."""
        current, target = self.get_challenge_progress()
        return current >= target

    def get_daily_challenge_xp(self) -> int:
        return int(XP_FOR_DAILY_CHALLENGE_BASE + (self.get_level() * XP_FOR_DAILY_CHALLENGE_PER_LEVEL))

    def is_challenge_completed_today(self) -> bool:
        return self.data.get("challenge_completed_day", 0) == _anki_today_int()

    def on_complete_challenge(self):
        if self.is_challenge_completed_today():
            tooltip(_("Challenge already completed today!"))
            return
        # Server-side validation: XP can only be claimed once the goal is met.
        self._challenge_progress_cache = None
        current, target = self.get_challenge_progress()
        if current < target:
            tooltip(_("Challenge not completed yet ({}/{}).").format(current, target))
            return
        xp_reward = self.get_daily_challenge_xp()
        today_int = _anki_today_int()
        self.data["challenge_completed_day"] = today_int
        self.get_achievements()
        self.add_xp(xp_reward, "Daily Challenge")
        tooltip(_("Challenge complete! +{} XP").format(xp_reward), period=3500)
        self._force_refresh("on_complete_challenge")

    # ------------------------------------------------------------------
    # Celebration events (deck-browser popup)
    # ------------------------------------------------------------------
    def get_celebration_events(self) -> Dict[str, Any]:
        """New level-up / rank-up / challenge events since the last check.

        Compares the current state against 'celebrated_*' markers stored in
        the gamification data and advances the markers immediately, so every
        event is reported exactly once. Called by the deck-browser render
        hook; returns {} when nothing new happened.
        """
        self.get_achievements()
        events: Dict[str, Any] = {}
        try:
            level = self.get_level()
            rank_now = self.get_rank_info_for_level(level)
            changed = False

            cel_level = self.data.get("celebrated_level")
            cel_rank_img = self.data.get("celebrated_rank_image")
            if cel_level is None or cel_rank_img is None:
                # First run after install/update: initialise silently so the
                # user's existing level/rank doesn't trigger a popup.
                self.data["celebrated_level"] = level
                self.data["celebrated_rank_image"] = rank_now.get("image")
                self.save_data()
                return {}

            # Level-up (a lowered level, e.g. after a reset, just re-syncs).
            if level > int(cel_level):
                events["level"] = {"old": int(cel_level), "new": level}
                self.data["celebrated_level"] = level
                changed = True
            elif level < int(cel_level):
                self.data["celebrated_level"] = level
                changed = True

            # Rank-up — only celebrate an ascent, never a reset.
            if rank_now.get("image") != cel_rank_img:
                old_rank = next(
                    (r for r in RANKS if r.get("image") == cel_rank_img), None)
                if old_rank is None or rank_now["level"] > old_rank["level"]:
                    events["rank"] = {
                        "old_name":  old_rank.get("name") if old_rank else None,
                        "old_image": old_rank.get("image") if old_rank else None,
                        "new_name":  rank_now.get("name"),
                        "new_image": rank_now.get("image"),
                        "level":     level,
                    }
                self.data["celebrated_rank_image"] = rank_now.get("image")
                changed = True

            # Daily challenge achieved (independent of claiming the XP).
            today = _anki_today_int()
            if (self.is_challenge_achieved()
                    and self.data.get("challenge_celebrated_day") != today):
                text, _unused = self.get_current_challenge()
                events["challenge"] = {"text": text,
                                       "claimed": self.is_challenge_completed_today(),
                                       "xp": self.get_daily_challenge_xp()}
                self.data["challenge_celebrated_day"] = today
                changed = True

            if changed:
                self.save_data()
        except Exception as e:
            print(f"SmartStudy: celebration event check failed: {e}")
            return {}
        return events

    def get_level(self) -> int: return self.data.get("level", 1)
    def set_streak_rules(self, rules) -> bool:
        if not isinstance(rules, dict) or type(rules.get("allowCards")) is not bool:
            return False
        if any(type(rules.get(key)) is not int or not 1 <= rules[key] <= 10000
               for key in ("reviews", "cards")):
            return False
        self.data["streak_rules"] = {key: rules[key] for key in ("reviews", "cards", "allowCards")}
        self.refresh_streak_cache()
        self.save_data()
        return True

    def get_streak(self) -> int:
        # Card creation/deletion and day rollover also change eligibility.
        key = (_anki_today_int(),)
        if self.data.get("streak_rules", {}).get("allowCards") and mw and mw.col:
            key += tuple(mw.col.db.first("SELECT count(*), max(id) FROM cards"))
        if getattr(self, "_streak_source_key", None) != key:
            self._streak_cache = None
            self._streak_source_key = key
        if self._streak_cache is None:
            return self.refresh_streak_cache(persist=False)
        return self._streak_cache

    def get_progress_percentage(self) -> int:
        needed = self.get_xp_for_level(self.get_level())
        if needed == float('inf') or needed <= 0:
            return 100 if needed == float('inf') else 0
        return min(100, int((self.data.get("xp", 0) / needed) * 100))

    def get_remaining_xp(self) -> Union[int, float]:
        needed = self.get_xp_for_level(self.get_level())
        if needed == float('inf'): return 0
        return max(0, int(needed - self.data.get("xp", 0)))

    def _force_refresh(self, reason: str = ""):
        try:
            if mw.state == "deckBrowser":
                mw.deckBrowser.refresh()
            elif mw.state == "review":
                # Never yank the user out of an active review (debug helpers
                # used to switch to the deck browser here). The new state is
                # picked up on the next deck-browser visit anyway.
                pass
            else:
                mw.moveToState("deckBrowser")
        except Exception:
            _ignored()
