# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from aqt import mw

# ── Review activity helpers ───────────────────────────────────────────────────
def _get_rollover_hour() -> int:
    """Anki's day-rollover hour (default 4 a.m.)."""
    try:
        return int(mw.col.get_config("rollover", 4) or 4)
    except Exception:
        return 4


def anki_today():
    """Today as an 'Anki day' (a day runs from rollover to rollover)."""
    return (datetime.now() - timedelta(hours=_get_rollover_hour())).date()


def get_daily_review_counts(since_days=None):
    """Reviews per day, keyed by ISO date string, respecting the rollover hour.

    since_days=None returns the whole collection history; an int restricts
    the query for cheap dashboard renders.
    """
    if not mw or not mw.col:
        return {}
    offset = _get_rollover_hour() * 3600
    try:
        if since_days is None:
            rows = mw.col.db.all(
                "SELECT strftime('%Y-%m-%d', id/1000 - ?, 'unixepoch', 'localtime') AS d, "
                "COUNT(*) FROM revlog WHERE type != 4 GROUP BY d",
                offset,
            )
        else:
            start = datetime.now() - timedelta(days=int(since_days))
            rows = mw.col.db.all(
                "SELECT strftime('%Y-%m-%d', id/1000 - ?, 'unixepoch', 'localtime') AS d, "
                "COUNT(*) FROM revlog WHERE id >= ? AND type != 4 GROUP BY d",
                offset,
                int(start.timestamp()) * 1000,
            )
        return {r[0]: r[1] for r in rows}
    except Exception as e:
        print(f"SmartStudy: review activity query failed: {e}")
        return {}
