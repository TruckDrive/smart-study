# -*- coding: utf-8 -*-
"""Building blocks for Qt dialogs in Smart Study's look.

Matches the web settings window: a large title with a muted subtitle,
rounded groups of rows (bold title, muted description, control on the
right) and a footer with a grey and a blue pill button.  Colours come from
theme.dialog_palette, so colour themes and dark mode apply.
"""
from __future__ import annotations

from typing import List, Optional, Sequence

from aqt import mw
from aqt.qt import (QAbstractButton, QButtonGroup, QColor, QDialog, QFrame,
                    QHBoxLayout, QLabel, QPainter, QPushButton, QRectF,
                    QScrollArea, QSize, QSizePolicy, Qt, QVBoxLayout, QWidget)

from ..theme import dialog_palette


def night() -> bool:
    try:
        from aqt.theme import theme_manager
        return bool(theme_manager.night_mode)
    except Exception:
        return False


def colors() -> dict:
    return dialog_palette(night())


def stylesheet() -> str:
    c = colors()
    return f"""
    QDialog#ssDialog {{ background: {c['bg']}; }}
    QWidget#ssBody {{ background: {c['bg']}; }}
    QLabel {{ color: {c['text']}; background: transparent; }}
    QLabel#ssTitle {{ font-size: 22px; font-weight: 700; }}
    QLabel#ssSubtitle, QLabel#ssRowText, QLabel#ssNote {{ color: {c['text_muted']}; }}
    QLabel#ssRowText {{ font-size: 12px; }}
    QLabel#ssNote {{ font-size: 11px; }}
    QLabel#ssRowTitle {{ font-weight: 600; }}
    QLabel#ssSection {{ color: {c['text_muted']}; font-size: 11px; font-weight: 600; }}
    QFrame#ssGroup {{ background: {c['surface']}; border: 1px solid {c['grey_light']}; border-radius: 12px; }}
    QFrame#ssLine {{ background: {c['grey_light']}; border: none; max-height: 1px; min-height: 1px; }}
    QFrame#ssFooter {{ background: {c['bg']}; border-top: 1px solid {c['grey_light']}; }}
    QPushButton#ssPrimary, QPushButton#ssSecondary {{
        border-radius: 8px; padding: 8px 16px; font-weight: 600; border: none; }}
    QPushButton#ssPrimary {{ background: {c['blue']}; color: white; }}
    QPushButton#ssPrimary:hover {{ background: {c['blue_hover']}; }}
    QPushButton#ssSecondary {{ background: {c['grey_light']}; color: {c['text']}; }}
    QPushButton#ssSecondary:hover {{ background: {c['grey_mid']}; }}
    QPushButton#ssLink {{ border: none; background: transparent; color: {c['blue_accent']};
        font-size: 12px; padding: 2px 0; text-align: left; }}
    QPushButton#ssLink:hover {{ text-decoration: underline; }}
    QPushButton#ssSegment {{ border: none; background: transparent; color: {c['text_muted']};
        border-radius: 6px; padding: 5px 11px; font-size: 12px; font-weight: 600; }}
    QPushButton#ssSegment:checked {{ background: {c['surface']}; color: {c['text']}; }}
    QFrame#ssSegments {{ background: {c['grey_light']}; border-radius: 8px; }}
    QScrollArea {{ background: transparent; border: none; }}
    """


class Toggle(QAbstractButton):
    """A switch like the ones in the settings window."""

    def __init__(self, checked: bool = False, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setChecked(checked)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def sizeHint(self) -> QSize:
        return QSize(42, 24)

    def paintEvent(self, _event) -> None:
        c = colors()
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(c["blue"] if self.isChecked() else c["grey_mid"]))
        p.drawRoundedRect(QRectF(0, 0, 42, 24), 12, 12)
        p.setBrush(QColor("white"))
        x = 20 if self.isChecked() else 2
        p.drawEllipse(QRectF(x, 2, 20, 20))
        p.end()


class Segments(QFrame):
    """A small segmented control; value() is the index of the chosen segment."""

    def __init__(self, labels: Sequence[str], current: int = 0, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("ssSegments")
        row = QHBoxLayout(self)
        row.setContentsMargins(3, 3, 3, 3)
        row.setSpacing(2)
        self.group = QButtonGroup(self)
        for i, label in enumerate(labels):
            button = QPushButton(label)
            button.setObjectName("ssSegment")
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            self.group.addButton(button, i)
            row.addWidget(button)
        self.group.button(current).setChecked(True)

    def value(self) -> int:
        return self.group.checkedId()


def label(text: str, name: str, *, rich: bool = False) -> QLabel:
    widget = QLabel(text)
    widget.setObjectName(name)
    widget.setWordWrap(True)
    if rich:
        widget.setTextFormat(Qt.TextFormat.RichText)
        widget.setOpenExternalLinks(True)
    return widget


class Group(QFrame):
    """Rounded card holding rows separated by thin lines."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("ssGroup")
        self.box = QVBoxLayout(self)
        self.box.setContentsMargins(0, 0, 0, 0)
        self.box.setSpacing(0)
        self._rows = 0

    def add_row(self, title: str, text: str = "", control: Optional[QWidget] = None,
                extra: Optional[QWidget] = None) -> QWidget:
        if self._rows:
            line = QFrame()
            line.setObjectName("ssLine")
            self.box.addWidget(line)
        self._rows += 1
        row = QWidget()
        h = QHBoxLayout(row)
        h.setContentsMargins(16, 12, 16, 12)
        h.setSpacing(14)
        texts = QVBoxLayout()
        texts.setSpacing(2)
        if title:
            texts.addWidget(label(title, "ssRowTitle"))
        if text:
            texts.addWidget(label(text, "ssRowText", rich="<a " in text))
        if extra is not None:
            texts.addWidget(extra, 0, Qt.AlignmentFlag.AlignLeft)
        h.addLayout(texts, 1)
        if control is not None:
            h.addWidget(control, 0, Qt.AlignmentFlag.AlignVCenter)
        self.box.addWidget(row)
        return row


class Dialog(QDialog):
    """Title, subtitle, scrollable body and a footer with pill buttons."""

    def __init__(self, title: str, subtitle: str = "", parent=None, width: int = 600):
        super().__init__(parent or mw)
        self.setObjectName("ssDialog")
        self.setWindowTitle(f"Smart Study – {title}")
        self.setStyleSheet(stylesheet())
        self.setMinimumWidth(width)
        self._width = width

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self.scroll = scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        body = QWidget()
        body.setObjectName("ssBody")
        self.body = QVBoxLayout(body)
        self.body.setContentsMargins(28, 24, 28, 20)
        self.body.setSpacing(14)
        self.body.addWidget(label(title, "ssTitle"))
        if subtitle:
            self.body.addWidget(label(subtitle, "ssSubtitle"))
        self.body.addSpacing(4)
        scroll.setWidget(body)
        outer.addWidget(scroll, 1)

        self.footer_frame = footer = QFrame()
        footer.setObjectName("ssFooter")
        self.footer = QHBoxLayout(footer)
        self.footer.setContentsMargins(20, 12, 20, 12)
        self.footer.addStretch(1)
        outer.addWidget(footer)

    def section(self, text: str) -> None:
        self.body.addWidget(label(text.upper(), "ssSection"))

    def group(self) -> Group:
        group = Group()
        self.body.addWidget(group)
        return group

    def note(self, text: str) -> None:
        self.body.addWidget(label(text, "ssNote", rich="<a " in text))

    def button(self, text: str, primary: bool = False, slot=None) -> QPushButton:
        button = QPushButton(text.replace("&", "&&"))  # no shortcut mnemonics
        button.setObjectName("ssPrimary" if primary else "ssSecondary")
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        if slot:
            button.clicked.connect(slot)
        if primary:
            button.setDefault(True)
        self.footer.addWidget(button)
        return button

    def finish(self, height: Optional[int] = None) -> None:
        """Sizes the window to its content, at most `height` or the main window."""
        self.body.addStretch(1)
        content = self.body.totalHeightForWidth(self._width) + self.footer_frame.sizeHint().height() + 2
        limit = height or (mw.height() - 80 if mw else 700)
        self.resize(self._width, min(content, max(limit, 300)))


def link_button(text: str, slot) -> QPushButton:
    button = QPushButton(text)
    button.setObjectName("ssLink")
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    button.clicked.connect(slot)
    return button


def ask_restart(parent=None) -> None:
    """Styled replacement for askUser(): restart now or later."""
    from .strings import tr
    dialog = Dialog(tr("Restart Anki"), tr("The change takes effect after restarting Anki."), parent, width=420)
    dialog.button(tr("Later"), slot=dialog.reject)
    dialog.button(tr("Close Anki now"), primary=True, slot=dialog.accept)
    dialog.finish()
    if dialog.exec():
        mw.close()
