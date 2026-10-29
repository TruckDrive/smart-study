# The code of MDS_Time_Left was used.
# MDS_Time_Left
# https://github.com/cjdduarte/MDS_Time_Left

# Copyright:
#       (c) Carlos Duarte 2019-2024 <https://github.com/cjdduarte>
#       (c) Shigeyuki 2024 <https://www.patreon.com/Shigeyuki>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from aqt import mw
from .._shim import manager as _pb_manager_factory
_pb_manager = _pb_manager_factory('progress_bar')  # Smart Study: own config store
from .path_manager import ADDON_NAME
import time

ONE_DAY_SECONDS = 86400
SEC_ONE_MINUTE = 60
CACHE_SECONDS = 600 # Statistik alle 10 min neu berechnen
MIN_SAMPLES = 20    # darunter: Fallback auf einfache Schaetzung

_average_per_card = None
_stats = None
_stats_time = 0


#MARK:reset chache
def reset_cache():
    global _average_per_card, _stats
    _average_per_card = None
    _stats = None


def _get_day_cutoff():
    if hasattr(mw.col.sched, "day_cutoff"):
        return mw.col.sched.day_cutoff
    if hasattr(mw.col.sched, "dayCutoff"):
        return mw.col.sched.dayCutoff
    return None


def _clamp(value, config):
    min_per_card = config.get("sec_min_per_card", 3)
    max_per_card = config.get("sec_max_per_card", 60)
    return min(max_per_card, max(min_per_card, value))


#MARK:study stats
def get_study_stats():
    """Kosten pro Kartentyp aus der eigenen Historie.

    Liefert pro Typ (review / new / learn):
      answers_* = erwartete Anzahl Antworten bis die Karte fuer heute fertig ist
      sec_*     = erwartete Sekunden bis die Karte fuer heute fertig ist
    Ignoriert revlog-Eintraege ohne echte Antwort (type 4/5 = manuell
    verschoben/zurueckgesetzt, time = 0), die vorher den Schnitt verfaelscht haben.
    """
    global _stats, _stats_time

    if _stats is not None and time.time() - _stats_time < CACHE_SECONDS:
        return _stats

    try:
        config = _pb_manager.getConfig(__name__)
        day_cutoff = _get_day_cutoff()
        if day_cutoff is None:
            print(f"[{ADDON_NAME}] Error: day_cutoff not found")
            return None

        days = config.get("days_to_consider", 14)
        msec_cutoff = (day_cutoff - ONE_DAY_SECONDS * days) * 1000

        rows = mw.col.db.all("""
            SELECT type, count(), sum(time) / 1000.0, sum(ease = 1)
            FROM revlog
            WHERE id > ? AND type IN (0, 1, 2, 3) AND time > 0 AND ease > 0
            GROUP BY type
        """, msec_cutoff)
        by_type = {r[0]: (r[1] or 0, r[2] or 0.0, r[3] or 0) for r in rows}

        new_introduced = mw.col.db.scalar("""
            SELECT count(DISTINCT cid) FROM revlog
            WHERE id > ? AND type = 0 AND lastIvl = 0 AND time > 0
        """, msec_cutoff) or 0

        learn_n, learn_t, _ = by_type.get(0, (0, 0.0, 0))
        rev_n, rev_t, rev_fail = by_type.get(1, (0, 0.0, 0))
        cram_n, cram_t, cram_fail = by_type.get(3, (0, 0.0, 0))
        rel_n, rel_t, _ = by_type.get(2, (0, 0.0, 0))
        rev_n += cram_n
        rev_t += cram_t
        rev_fail += cram_fail

        total_n = learn_n + rev_n + rel_n
        if total_n < MIN_SAMPLES:
            _stats = None
            _stats_time = time.time()
            return None

        overall = _clamp((learn_t + rev_t + rel_t) / total_n, config)

        # Review: eine Antwort + bei "Again" die Relearning-Schritte
        sec_rev_answer = _clamp(rev_t / rev_n, config) if rev_n else overall
        lapse_rate = rev_fail / rev_n if rev_n else 0.0
        if rev_fail and rel_n:
            relearn_answers = rel_n / rev_fail
            sec_relearn = _clamp(rel_t / rel_n, config)
        else:
            relearn_answers = 1.0
            sec_relearn = overall
        answers_review = 1 + lapse_rate * relearn_answers
        sec_review = sec_rev_answer + lapse_rate * relearn_answers * sec_relearn

        # Neu: alle Lernschritte bis die Karte heute fertig ist
        sec_step = _clamp(learn_t / learn_n, config) if learn_n else overall
        if new_introduced and learn_n:
            answers_new = max(1.0, learn_n / new_introduced)
        else:
            answers_new = 2.0
        sec_new = answers_new * sec_step

        # Gerade im Lernen: im Schnitt ist ein Teil der Schritte schon erledigt
        answers_learn = max(1.0, answers_new - 1)
        sec_learn = answers_learn * sec_step

        _stats = {
            "answers_review": answers_review, "sec_review": sec_review,
            "answers_new": answers_new, "sec_new": sec_new,
            "answers_learn": answers_learn, "sec_learn": sec_learn,
        }
        _stats_time = time.time()
        return _stats

    except Exception as e:
        print(f"[{ADDON_NAME}] Error in get_study_stats: {e}")
        return None


#MARK:get card time
def get_cards_average_time():
    """Alter, einfacher Schnitt (Fallback), jetzt ohne time=0-Eintraege."""
    try:
        global _average_per_card

        config = _pb_manager.getConfig(__name__)
        day_cutoff = _get_day_cutoff()
        if day_cutoff is None:
            print(f"[{ADDON_NAME}] Error: day_cutoff not found")
            return 0

        days_to_consider = config.get("days_to_consider", 14)
        msec_cutoff = (day_cutoff - ONE_DAY_SECONDS * days_to_consider) * 1000

        done_cards, sum_time = mw.col.db.first("""
            SELECT count(), sum(time) / 1000.0
            FROM revlog
            WHERE id > ? AND time > 0 AND ease > 0
        """, msec_cutoff)

        done_cards = done_cards or 0
        sum_time = sum_time or 0

        if done_cards > 0:
            average_per_card = _clamp(sum_time / done_cards, config)
        else:
            average_per_card = config.get("sec_min_per_card", 3)

        _average_per_card = average_per_card
        return average_per_card

    except Exception as e:
        print(f"[{ADDON_NAME}] Error in get_cards_average_time: {e}")
        return 0


def _format_minutes(seconds):
    minutes = max(0, int(round(seconds / SEC_ONE_MINUTE)))
    if minutes >= 60:
        return f"left {minutes // 60} h {minutes % 60:02d} min"
    return f"left {minutes} min"


#MARK:expected answers
def estimate_answers(review, learn, new):
    """Erwartete Anzahl Antworten (gleiche Einheit wie der 'done'-Zaehler)."""
    stats = get_study_stats()
    if not stats:
        return None
    return (review * stats["answers_review"]
            + learn * stats["answers_learn"]
            + new * stats["answers_new"])


#MARK:estimate
def estimate_time_left(remain_cards, counts=None):
    """counts = (review, learn, new) echte Kartenanzahlen; ohne counts
    wird wie frueher remain_cards * Durchschnitt gerechnet."""
    try:
        global _average_per_card

        if counts is not None:
            stats = get_study_stats()
            if stats:
                review, learn, new = counts
                seconds = (review * stats["sec_review"]
                           + learn * stats["sec_learn"]
                           + new * stats["sec_new"])
                return _format_minutes(seconds)

        if _average_per_card is None:
            average_per_card = get_cards_average_time()
        else:
            average_per_card = _average_per_card

        return _format_minutes(remain_cards * average_per_card)

    except Exception as e:
        print(f"[{ADDON_NAME}] Error: {e}")
        return ""
