# -*- coding: utf-8 -*-

import json
import os
import traceback
import copy
import uuid
from typing import Dict, Optional, List, TYPE_CHECKING
from datetime import date, datetime

from aqt import mw
from aqt.qt import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QAbstractItemView, QHeaderView, QPushButton, QLineEdit, QTimeEdit, QTime,
    QLabel, QDialogButtonBox, QMessageBox, QWidget, Qt, QTimer, QShortcut, QKeySequence,
    QCalendarWidget, QDate, QCheckBox, QDateEdit, QFrame,
    QFormLayout,
    QSizePolicy,
    QFont, QColor, QPainter, QPen, QBrush, QRectF, QIcon, QToolButton,
    QTextEdit, QTextCharFormat,
    QApplication,
    QDesktopServices, QUrl
)
from aqt.utils import showInfo, tooltip

# --- Addon Imports ---
try:
    from .gamification import ADDON_NAME, GamificationManager
except ImportError:
    ADDON_NAME = "GamificationPlusDailyWidgets_ConfigImportFailed"; GamificationManager = None

try:
    from .deadline_bar import DeadlineManager, DEADLINE_CONFIG_KEY
except ImportError:
    DeadlineManager = None; DEADLINE_CONFIG_KEY = "deadline_import_fail"

is_night_mode = False
try:
    if mw.pm.night_mode():
        is_night_mode = True
except Exception:
    pass

# --- Translation ---
try:
    from .locales import _
except ImportError:
    def _(text): return text  # type: ignore

# --- Theme ---
try:
    from .theme import dialog_palette as _palette, FONT_FAMILY as _FONT_FAMILY
except ImportError:
    def _palette(night): return {}  # type: ignore
    _FONT_FAMILY = "sans-serif"

# --- Stylesheets ---

def _build_style(night: bool) -> str:
    c = _palette(night)
    return f"""
    QDialog {{
        background-color: {c['bg']};
        font-family: {_FONT_FAMILY};
        font-size: 13px;
        color: {c['text']};
    }}

    QFrame#CardFrame {{
        background-color: {c['surface']};
        border-radius: 12px;
        border: 1px solid {c['grey_light']};
    }}

    QLabel {{ color: {c['text']}; }}
    QLabel#HeaderLabel {{ font-size: 16px; font-weight: 700; color: {c['text']}; margin-bottom: 4px; }}
    QLabel#SubLabel {{ color: {c['text_muted']}; font-size: 12px; }}

    QLineEdit, QTimeEdit, QDateEdit, QTextEdit {{
        background-color: {c['surface']}; border: 1px solid {c['grey_mid']}; border-radius: 8px; padding: 6px 8px; color: {c['text']};
    }}
    QLineEdit:focus, QTimeEdit:focus, QDateEdit:focus, QTextEdit:focus {{ border: 2px solid {c['blue_bright']}; }}

    QPushButton {{
        background-color: {c['blue']}; color: white; border-radius: 8px; padding: 6px 16px; font-weight: 600; border: {c['blue_border']};
    }}
    QPushButton:hover {{ background-color: {c['blue_hover']}; }}
    QPushButton:pressed {{ background-color: {c['blue_pressed']}; }}
    QPushButton:disabled {{ background-color: {c['grey_light']}; color: {c['text_faint']}; border: none; }}

    QPushButton#SecondaryButton {{ background-color: {c['grey_light']}; color: {c['text']}; border: {c['red_border'].replace('A00000','404040') if night else 'none'}; }}
    QPushButton#SecondaryButton:hover {{ background-color: {c['grey_mid']}; }}

    QPushButton#DangerButton {{ background-color: {c['red']}; color: white; border: {c['red_border']}; }}
    QPushButton#DangerButton:hover {{ background-color: {c['red_hover']}; }}

    QTableWidget {{
        background-color: {c['surface']}; border: 1px solid {c['grey_light']}; border-radius: 8px; color: {c['text']};
        selection-background-color: {c['selection_bg']}; selection-color: {c['blue_bright']}; gridline-color: {c['grey_light']};
    }}
    QHeaderView::section {{
        background-color: {c['surface']}; border: none; border-bottom: 1px solid {c['grey_light']};
        padding: 6px; font-weight: bold; color: {c['text_muted']};
    }}

    QCalendarWidget {{ background-color: {c['surface']}; border: none; }}
    QCalendarWidget QWidget {{ alternate-background-color: {c['surface']}; background-color: {c['surface']}; color: {c['text']}; }}
    QCalendarWidget QWidget#qt_calendar_navigationbar {{
        background-color: {c['surface']}; border-bottom: 1px solid {c['hover_subtle']};
    }}
    QCalendarWidget QToolButton {{
        color: {c['text']}; background-color: transparent; border: none;
        border-radius: 7px; padding: 3px 7px;
    }}
    QCalendarWidget QToolButton:hover {{ background-color: {c['hover_subtle']}; }}
    QCalendarWidget QToolButton:pressed {{ background-color: {c['grey_light']}; }}
    QCalendarWidget QToolButton#qt_calendar_prevmonth,
    QCalendarWidget QToolButton#qt_calendar_nextmonth {{
        color: {c['text_muted']}; border-radius: 14px; padding: 0;
        font-size: 24px; font-weight: 400;
    }}
    QCalendarWidget QToolButton#qt_calendar_prevmonth:hover,
    QCalendarWidget QToolButton#qt_calendar_nextmonth:hover {{
        color: {c['blue_accent']}; background-color: {c['hover_subtle']};
    }}
    QCalendarWidget QToolButton#qt_calendar_monthbutton,
    QCalendarWidget QToolButton#qt_calendar_yearbutton {{
        color: {c['text']}; font-size: 14px; font-weight: 600;
    }}
    QCalendarWidget QToolButton::menu-indicator {{ image: none; }}
    QCalendarWidget QSpinBox {{
        color: {c['text']}; background: {c['surface']}; border: 1px solid {c['grey_mid']};
        border-radius: 6px; padding: 2px 5px;
        selection-background-color: {c['selection_bg']}; selection-color: {c['text']};
    }}
    QCalendarWidget QAbstractItemView:enabled {{
        color: {c['text']}; background-color: {c['surface']};
        selection-background-color: transparent; selection-color: {c['text']};
        border: none; outline: none;
    }}
    QCalendarWidget QAbstractItemView:disabled {{ color: {c['text_faint']}; }}

    QCheckBox {{ color: {c['text']}; }}
"""



# ─────────────────────────────────────────────────────────────────────────────
# DeadlineConfigDialog — manage (add / remove / pin) multiple deadlines
# ─────────────────────────────────────────────────────────────────────────────

class DeadlineConfigDialog(QDialog):
    """Popup for adding, removing, and pinning deadlines."""

    def __init__(self, deadline_manager, parent=None):
        super().__init__(parent)
        self.deadline_manager = deadline_manager
        # Edit a detached copy. Add/remove/pin actions therefore remain
        # reversible until the user presses Done, and Cancel/window-close
        # cannot leak partial changes into collection configuration.
        self._working_data = copy.deepcopy(deadline_manager.data) if deadline_manager else {
            "deadlines": [], "pinned_id": None, "enabled": True,
        }
        self.setWindowTitle(_("Configure Deadlines"))
        self.resize(660, 460)
        self.setMinimumSize(520, 360)
        self.setStyleSheet(_build_style(is_night_mode))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # ── Enable checkbox ──────────────────────────────────────────────
        top_row = QHBoxLayout()
        lbl = QLabel(_("Deadlines"))
        lbl.setObjectName("HeaderLabel")
        self.enabled_cb = QCheckBox(_("Enable deadline bar"))
        self.enabled_cb.setCursor(Qt.CursorShape.PointingHandCursor)
        self.enabled_cb.setChecked(self._working_data.get("enabled", True))
        top_row.addWidget(lbl)
        top_row.addStretch()
        top_row.addWidget(self.enabled_cb)
        layout.addLayout(top_row)

        # ── Table ────────────────────────────────────────────────────────
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Name", "Start", "End", "Default"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 60)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        layout.addWidget(self.table)

        hint_lbl = QLabel(_("If no deadline is set as default, the nearest upcoming one is shown automatically."))
        hint_lbl.setObjectName("SubLabel")
        hint_lbl.setWordWrap(True)
        layout.addWidget(hint_lbl)

        # ── Add row ──────────────────────────────────────────────────────
        add_frame = QFrame()
        add_frame.setObjectName("CardFrame")
        add_layout = QHBoxLayout(add_frame)
        add_layout.setContentsMargins(10, 8, 10, 8)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(_("Name"))
        self.start_edit = QDateEdit(QDate.currentDate())
        self.start_edit.setCalendarPopup(True)
        self.start_edit.setDisplayFormat("yyyy-MM-dd")
        self.start_edit.setFixedWidth(105)
        self.end_edit = QDateEdit(QDate.currentDate().addMonths(3))
        self.end_edit.setCalendarPopup(True)
        self.end_edit.setDisplayFormat("yyyy-MM-dd")
        self.end_edit.setFixedWidth(105)
        add_btn = QPushButton(_("+ Add"))
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setFixedWidth(64)
        add_btn.clicked.connect(self._add_deadline)
        self.name_input.returnPressed.connect(self._add_deadline)
        add_layout.addWidget(self.name_input)
        add_layout.addWidget(QLabel(_("Start:")))
        add_layout.addWidget(self.start_edit)
        add_layout.addWidget(QLabel(_("End:")))
        add_layout.addWidget(self.end_edit)
        add_layout.addWidget(add_btn)
        layout.addWidget(add_frame)

        # ── Bottom buttons ───────────────────────────────────────────────
        btn_row = QHBoxLayout()
        self.remove_btn = QPushButton(_("Remove Selected"))
        self.remove_btn.setObjectName("SecondaryButton")
        self.remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.remove_btn.setEnabled(False)
        self.remove_btn.clicked.connect(self._remove_deadline)
        btn_row.addWidget(self.remove_btn)
        btn_row.addStretch()
        cancel_btn = QPushButton(_("Cancel"))
        cancel_btn.setObjectName("SecondaryButton")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        close_btn = QPushButton(_("Done"))
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self._save_and_close)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

        self.table.itemSelectionChanged.connect(
            lambda: self.remove_btn.setEnabled(bool(self.table.selectionModel().selectedRows()))
        )

        self._refresh_table()

    def _refresh_table(self):
        deadlines = sorted(
            self._working_data.get("deadlines", []),
            key=lambda deadline: deadline.get("end_date", "9999-12-31"),
        )
        pinned_id = self._working_data.get("pinned_id")
        self.table.setRowCount(0)
        for dl in deadlines:
            row = self.table.rowCount()
            self.table.insertRow(row)
            item0 = QTableWidgetItem(dl.get("name", ""))
            item0.setData(Qt.ItemDataRole.UserRole, dl.get("id"))
            self.table.setItem(row, 0, item0)
            self.table.setItem(row, 1, QTableWidgetItem(dl.get("start_date", "")))
            self.table.setItem(row, 2, QTableWidgetItem(dl.get("end_date", "")))
            dl_id = dl.get("id")
            is_pinned = (dl_id == pinned_id)
            pin_cb = QCheckBox()
            pin_cb.setChecked(is_pinned)
            pin_cb.setToolTip(_("Always show this deadline (uncheck = auto-select nearest upcoming)"))
            pin_cb.setCursor(Qt.CursorShape.PointingHandCursor)
            pin_cb.stateChanged.connect(lambda state, did=dl_id: self._toggle_pin(did, state == 0))
            # Center the checkbox in the cell
            cell_widget = QWidget()
            cell_layout = QHBoxLayout(cell_widget)
            cell_layout.addWidget(pin_cb)
            cell_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cell_layout.setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(row, 3, cell_widget)
        self.table.resizeRowsToContents()

    def _toggle_pin(self, deadline_id: str, currently_pinned: bool):
        self._working_data["pinned_id"] = None if currently_pinned else deadline_id
        self._refresh_table()

    def _add_deadline(self):
        name = self.name_input.text().strip()
        if not name:
            return
        if self.start_edit.date() > self.end_edit.date():
            showInfo(_("The start date must not be after the end date."), parent=self)
            return
        self._working_data.setdefault("deadlines", []).append({
            "id": str(uuid.uuid4())[:8],
            "name": name[:120],
            "start_date": self.start_edit.date().toString(Qt.DateFormat.ISODate),
            "end_date": self.end_edit.date().toString(Qt.DateFormat.ISODate),
        })
        self.name_input.clear()
        self._refresh_table()

    def _remove_deadline(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return
        item = self.table.item(rows[0].row(), 0)
        if item:
            dl_id = item.data(Qt.ItemDataRole.UserRole)
            if dl_id:
                self._working_data["deadlines"] = [
                    deadline for deadline in self._working_data.get("deadlines", [])
                    if deadline.get("id") != dl_id
                ]
                if self._working_data.get("pinned_id") == dl_id:
                    self._working_data["pinned_id"] = None
                self._refresh_table()

    def _save_and_close(self):
        if self.deadline_manager:
            self._working_data["enabled"] = self.enabled_cb.isChecked()
            self.deadline_manager.data = copy.deepcopy(self._working_data)
            self.deadline_manager.save_data()
        self.accept()




# ─────────────────────────────────────────────────────────────────────────────
# DeadlineViewerDialog — read-only overview of all deadlines with progress bars
# ─────────────────────────────────────────────────────────────────────────────

class DeadlineViewerDialog(QDialog):
    """Shows all deadlines as progress cards — read-only overview."""

    def __init__(self, deadline_manager, parent=None):
        super().__init__(parent)
        self.deadline_manager = deadline_manager
        self.setWindowTitle(_("Deadlines"))
        self.resize(480, 400)
        self.setMinimumSize(360, 260)
        self.setStyleSheet(_build_style(is_night_mode))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        header = QLabel(_("Your Deadlines"))
        header.setObjectName("HeaderLabel")
        layout.addWidget(header)

        from aqt.qt import QScrollArea, QProgressBar
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        inner = QWidget()
        inner_layout = QVBoxLayout(inner)
        inner_layout.setSpacing(10)
        inner_layout.setContentsMargins(0, 0, 8, 0)

        c = _palette(is_night_mode)

        if deadline_manager:
            from datetime import date as _date, datetime as _dt, timedelta as _td
            DATE_FMT = "%Y-%m-%d"
            deadlines = deadline_manager.get_all_deadlines()
            pinned_id = deadline_manager.data.get("pinned_id")

            if not deadlines:
                lbl = QLabel(_("No deadlines configured yet.\nUse 'Configure Deadlines' to add one."))
                lbl.setObjectName("SubLabel")
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                inner_layout.addWidget(lbl)
            else:
                for dl in deadlines:
                    card = QFrame()
                    card.setObjectName("CardFrame")
                    card_layout = QVBoxLayout(card)
                    card_layout.setContentsMargins(14, 12, 14, 12)
                    card_layout.setSpacing(6)

                    # Title row
                    title_row = QHBoxLayout()
                    name_lbl = QLabel(dl.get("name", _("Deadline")))
                    name_lbl.setObjectName("HeaderLabel")
                    name_font = name_lbl.font()
                    name_font.setPointSize(13)
                    name_lbl.setFont(name_font)
                    title_row.addWidget(name_lbl)
                    title_row.addStretch()
                    if dl.get("id") == pinned_id:
                        pin_lbl = QLabel(_("default"))
                        pin_lbl.setStyleSheet(
                            f"color: {c.get('blue_bright','#007AFF')}; font-size: 11px; "
                            f"background: {c.get('hover_subtle','#e8f0fe')}; "
                            f"border-radius: 4px; padding: 2px 6px;"
                        )
                        title_row.addWidget(pin_lbl)
                    card_layout.addLayout(title_row)

                    # Progress calculation
                    try:
                        today = _date.today()
                        start = _dt.strptime(dl["start_date"], DATE_FMT).date()
                        end   = _dt.strptime(dl["end_date"],   DATE_FMT).date()
                        total = (end - start).days
                        elapsed = (today - start).days
                        if today < start:
                            progress = 0
                            days_lbl_txt = _("Starts in {} day(s)").format((start - today).days)
                        elif today > end:
                            progress = 100
                            days_lbl_txt = _("Ended {} day(s) ago").format((today - end).days)
                        else:
                            progress = max(0, min(100, int(max(0, elapsed) / max(1, total) * 100)))
                            days_lbl_txt = _("{} day(s) remaining").format((end - today).days)
                    except Exception:
                        progress = 0
                        days_lbl_txt = _("Invalid date")

                    bar = QProgressBar()
                    bar.setRange(0, 100)
                    bar.setValue(progress)
                    bar.setTextVisible(False)
                    bar.setFixedHeight(10)
                    bar.setStyleSheet(
                        f"QProgressBar {{ background: {c.get('grey_light','#e0e0e0')}; border-radius: 5px; border: none; }}"
                        f"QProgressBar::chunk {{ background: {c.get('blue','#007AFF')}; border-radius: 5px; }}"
                    )
                    card_layout.addWidget(bar)

                    # Dates + days label
                    info_row = QHBoxLayout()
                    date_lbl = QLabel(f"{dl.get('start_date','')}  →  {dl.get('end_date','')}")
                    date_lbl.setObjectName("SubLabel")
                    days_lbl = QLabel(days_lbl_txt)
                    days_lbl.setObjectName("SubLabel")
                    info_row.addWidget(date_lbl)
                    info_row.addStretch()
                    info_row.addWidget(days_lbl)
                    card_layout.addLayout(info_row)

                    inner_layout.addWidget(card)

        inner_layout.addStretch()
        scroll.setWidget(inner)
        layout.addWidget(scroll)

        # Bottom row
        btn_row = QHBoxLayout()
        config_btn = QPushButton(_("Configure Deadlines"))
        config_btn.setObjectName("SecondaryButton")
        config_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        config_btn.clicked.connect(self._open_config)
        btn_row.addWidget(config_btn)
        btn_row.addStretch()
        close_btn = QPushButton(_("Close"))
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

    def _open_config(self):
        if DeadlineConfigDialog(self.deadline_manager, parent=self).exec():
            self.accept()  # Close viewer; user can reopen to see updated list
