# -*- coding: utf-8 -*-

try:
    from .quiet import ignored as _ignored
except ImportError:  # the module is loaded on its own (tests)
    def _ignored(*_args):
        pass

from .constants import is_night as _is_night
from datetime import datetime, timedelta
from aqt import mw

try:
    from .theme import palette as _palette
except ImportError:
    def _palette(night): return {"blue": "#0B6570", "blue_bright": "#40A5FF" if night else "#1A8A98"}  # type: ignore

try:
    from .locales import _
except ImportError:
    def _(text):  # type: ignore
        return text

_statistics_cache = {}


def invalidate_statistics_cache(*_args) -> None:
    """Drop all cached dashboard snapshots (profile/review boundary)."""
    _statistics_cache.clear()


def _on_operation_did_execute(changes, _handler=None) -> None:
    if getattr(changes, "card", False):
        _statistics_cache.clear()


try:
    from aqt import gui_hooks as _gui_hooks
    _gui_hooks.operation_did_execute.append(_on_operation_did_execute)
    _gui_hooks.state_did_reset.append(invalidate_statistics_cache)
    _gui_hooks.collection_did_load.append(invalidate_statistics_cache)
except Exception:
    _ignored()

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


DEFAULT_CHART_DAYS = 30


def show_statistics_info_dialog(parent=None, stats_days=7, chart_days=DEFAULT_CHART_DAYS):
    """Info dialog for the dashboard statistics widget ("i" button).

    Explains every statistic shown in the widget. Opened from the deck
    browser via pycmd ('smartstudy:stats_info'), see __init__.py.
    """
    from aqt.qt import QDialog, QVBoxLayout, QLabel, QDialogButtonBox, QScrollArea, QWidget, QFrame, Qt

    if not isinstance(stats_days, int) or stats_days < 1:
        stats_days = 7
    if stats_days == 1:
        period_text = _("Last 24 hours")
    else:
        period_text = _("Last {} days").format(stats_days)
    if chart_days not in (7, 30, 365):
        chart_days = DEFAULT_CHART_DAYS
    chart_period_text = _("the last year") if chart_days == 365 else _("the last {} days").format(chart_days)

    sections = [
        (_("Consistency"),
         _("Your reviews per day over {}. The curve is relative "
           "to this period: the day with the most reviews forms the peak, days "
           "without reviews sit on the baseline. The dot marks today.").format(chart_period_text)),
        (_("Efficiency (Eff.)"),
         _("How many cards you answer correctly per minute of study time "
           "({}). A full bar equals 7.5 correct cards per minute. Time per "
           "card is capped at 45 seconds so breaks don't distort the "
           "value.").format(period_text)),
        (_("Accuracy (Acc.)"),
         _("The percentage of all answered cards you got right ({}). The bar "
           "is scaled for readability — hover over it to see the exact "
           "value.").format(period_text)),
        (_("Retention"),
         _("The percentage of correct answers on review cards ({}) — cards "
           "you had already learned. This shows how well you retain content "
           "long-term.").format(period_text)),
        (_("New Cards"),
         _("The percentage of cards in your active collection that you have "
           "never studied.")),
    ]

    footer = _("Use the gear button on the statistics widget to change periods and visible insights.")
    dialog = QDialog(parent)
    dialog.setObjectName("smartstudyStatisticsInfo")
    dialog.setWindowTitle(_("Smart Study - Statistics"))
    dialog.resize(560, 640)
    dialog.setMinimumSize(320, 300)
    night = bool(mw and _is_night())
    colors = _palette(night)
    dialog.setStyleSheet(f"""
        QDialog#smartstudyStatisticsInfo {{ background:{colors['bg']};color:{colors['text']}; }}
        QLabel {{ color:{colors['text']};background:transparent; }}
        QLabel#infoHeading {{ font-size:24px;font-weight:600; }}
        QLabel#infoSubtitle {{ color:{colors['text']}; }}
        QScrollArea,QWidget#infoContent {{ border:0;background:transparent; }}
        QFrame#infoSection {{ background:{colors['surface']};border:1px solid {colors['grey_light']};border-radius:12px; }}
        QLabel#infoSectionTitle {{ font-weight:600; }}
        QPushButton {{ background:{colors['surface']};color:{colors['text']};border:1px solid {colors['grey_light']};border-radius:8px;padding:7px 16px; }}
        QPushButton:focus {{ border:1px solid {colors['blue']}; }}
        QPushButton:hover {{ background:{colors['bg']}; }}
    """)
    layout = QVBoxLayout(dialog)
    layout.setContentsMargins(20, 20, 20, 16)
    layout.setSpacing(14)
    heading = QLabel(_("Your statistics, explained"))
    heading.setObjectName("infoHeading")
    heading.setWordWrap(True)
    layout.addWidget(heading)
    subtitle = QLabel(_("Understand the insights on your dashboard."))
    subtitle.setObjectName("infoSubtitle")
    subtitle.setWordWrap(True)
    layout.addWidget(subtitle)
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    content = QWidget()
    content.setObjectName("infoContent")
    rows = QVBoxLayout(content)
    rows.setContentsMargins(0, 0, 6, 0)
    rows.setSpacing(10)
    for title, text in sections:
        card = QFrame()
        card.setObjectName("infoSection")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 14, 16, 14)
        card_layout.setSpacing(6)
        title_label = QLabel(title)
        title_label.setObjectName("infoSectionTitle")
        title_label.setWordWrap(True)
        description = QLabel(text)
        description.setTextFormat(Qt.TextFormat.PlainText)
        description.setWordWrap(True)
        description.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.TextSelectableByKeyboard)
        card_layout.addWidget(title_label)
        card_layout.addWidget(description)
        rows.addWidget(card)
    rows.addStretch(1)
    scroll.setWidget(content)
    layout.addWidget(scroll, 1)
    footer_label = QLabel(footer)
    footer_label.setWordWrap(True)
    layout.addWidget(footer_label)
    button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
    from .locales import translate_standard_buttons
    translate_standard_buttons(button_box)
    button_box.rejected.connect(dialog.reject)
    layout.addWidget(button_box)
    button_box.button(QDialogButtonBox.StandardButton.Close).setFocus()
    dialog.exec()
