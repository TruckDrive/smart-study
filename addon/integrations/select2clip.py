# -*- coding: utf-8 -*-
"""Copy a selection with pictures as one image.

Selecting part of a card in the reviewer (mouse, Ctrl+A, Shift+arrows) that
contains pictures puts the selection on the clipboard as a single PNG, text and
pictures together.  Chat apps such as ChatGPT or Claude drop the pictures when
HTML is pasted, but take an image.  Selections without pictures are left alone.
"""
from __future__ import annotations

import json
import os
import re
from urllib.parse import unquote, urlparse

from aqt import gui_hooks, mw
from aqt.qt import (QImage, QMimeData, QPainter, QTextCursor, QTextDocument,
                    QTimer, QUrl, Qt)
from aqt.utils import tooltip
from anki.utils import is_mac

from .strings import tr

WIDTH = 900   # layout width in px
SCALE = 2     # render factor for sharp text

JS = """
(() => {
  if (window.__smartstudySelect2clip) return;
  window.__smartstudySelect2clip = true;
  let last = "";
  const grab = () => setTimeout(() => {
    const sel = window.getSelection();
    if (!sel || sel.isCollapsed) return;
    const box = document.createElement("div");
    for (let i = 0; i < sel.rangeCount; i++) box.appendChild(sel.getRangeAt(i).cloneContents());
    const imgs = box.querySelectorAll("img");
    if (!imgs.length) return;
    imgs.forEach(img => img.setAttribute("src", new URL(img.getAttribute("src"), location.href).href));
    if (box.innerHTML === last) return;
    last = box.innerHTML;
    pycmd("smartstudy_select2clip:" + JSON.stringify({html: box.innerHTML}));
  }, 150);
  // mouse and keyboard (Ctrl+A, Shift+arrows)
  document.addEventListener("mouseup", grab);
  document.addEventListener("keyup", grab);
})();
"""

_PREFIX = "smartstudy_select2clip:"


def _local_src(src: str) -> str:
    """Points a picture at its file in the collection's media folder."""
    if src.startswith("data:") or not mw.col:
        return src
    name = unquote(os.path.basename(urlparse(src).path))
    path = os.path.join(mw.col.media.dir(), name)
    return QUrl.fromLocalFile(path).toString() if os.path.isfile(path) else src


def _clean(html: str) -> str:
    # The card's own <style> (e.g. white text in night mode) must not apply.
    html = re.sub(r"<(style|script)\b.*?</\1>", "", html, flags=re.S | re.I)
    html = re.sub(r'\s(style|class|id|width|height|color|bgcolor)="[^"]*"', "", html)
    html = re.sub(r'<input[^>]*type="?checkbox[^>]*>', "☐ ", html)
    html = re.sub(r'<input[^>]*type="?radio[^>]*>', "○ ", html)
    return re.sub(r'<img[^>]*?src="([^"]+)"[^>]*>',
                  lambda m: f'<br><img src="{_local_src(m.group(1))}"><br>', html)


def render(html: str) -> QImage:
    """Renders card HTML (text and pictures) to an image."""
    doc = QTextDocument()
    doc.setDefaultStyleSheet("body{font-family:sans-serif;font-size:17px;color:#111}"
                             "td{padding:4px}")
    doc.setDocumentMargin(24)
    doc.setTextWidth(WIDTH)
    doc.setHtml(_clean(html))

    # Scale pictures wider than the page down.
    block = doc.begin()
    while block.isValid():
        it = block.begin()
        while not it.atEnd():
            frag = it.fragment()
            fmt = frag.charFormat()
            if fmt.isImageFormat():
                image_format = fmt.toImageFormat()
                image = doc.resource(QTextDocument.ResourceType.ImageResource,
                                     QUrl(image_format.name()))
                if image is not None and hasattr(image, "width") and image.width() > WIDTH - 48:
                    image_format.setWidth(WIDTH - 48)
                    image_format.setHeight(image.height() * (WIDTH - 48) / image.width())
                    cursor = QTextCursor(doc)
                    cursor.setPosition(frag.position())
                    cursor.setPosition(frag.position() + frag.length(),
                                       QTextCursor.MoveMode.KeepAnchor)
                    cursor.setCharFormat(image_format)
            it += 1
        block = block.next()

    # As narrow as the content allows, so short selections have no empty margin.
    doc.setTextWidth(min(WIDTH, doc.idealWidth() + 2 * doc.documentMargin()))
    size = doc.size()
    out = QImage(int(size.width() * SCALE), int(size.height() * SCALE),
                 QImage.Format.Format_RGB32)
    out.fill(Qt.GlobalColor.white)
    painter = QPainter(out)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    painter.scale(SCALE, SCALE)
    doc.drawContents(painter)
    painter.end()
    return out


def _inject(*_args) -> None:
    if mw.reviewer and mw.reviewer.web:
        mw.reviewer.web.eval(JS)


def _on_js(handled, message, _context):
    if not isinstance(message, str) or not message.startswith(_PREFIX):
        return handled
    html = json.loads(message[len(_PREFIX):])["html"]
    data = QMimeData()
    data.setImageData(render(html))
    # Short delay so a clipboard manager syncing the (text-only) selection
    # does not overwrite the image right afterwards.
    QTimer.singleShot(100, lambda: mw.app.clipboard().setMimeData(data))
    tooltip(tr("Copied as image – paste it with {keys}.").format(keys="Cmd+V" if is_mac else "Ctrl+V"), period=1500)
    return (True, None)


gui_hooks.reviewer_did_show_question.append(_inject)
gui_hooks.reviewer_did_show_answer.append(_inject)
gui_hooks.webview_did_receive_js_message.append(_on_js)
