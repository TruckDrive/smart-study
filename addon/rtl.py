# -*- coding: utf-8 -*-
"""Right-to-left layout for Smart Study's own windows and pages.

Smart Study's language can differ from Anki's, so the direction is set per
surface instead of for the whole application.
"""
from __future__ import annotations

from .locales import _, is_rtl

try:
    from aqt import mw
    from aqt.qt import QEvent, QObject, Qt, QWidget
    from aqt.utils import askUser, tooltip
except ImportError:  # outside Anki
    mw = None
    QObject = object  # type: ignore

ANKI_PERSIAN = "fa_IR"
_PACKAGE = __name__.split(".")[0]
_SCRIPT_NAME = "smartstudy-rtl"
PAGE_CSS = (
    "input,textarea,[contenteditable]{unicode-bidi:plaintext;text-align:start}"
    "code,pre,kbd,.katex,.MathJax{direction:ltr;unicode-bidi:isolate}"
)
_PAGE_SCRIPT = """(() => {
  const apply = () => {
    const root = document.documentElement;
    if (!root) return;
    root.dir = 'rtl';
    root.lang = 'fa';
    if (document.head && !document.getElementById('smartstudy-rtl')) {
      const style = document.createElement('style');
      style.id = 'smartstudy-rtl';
      style.textContent = %r;
      document.head.appendChild(style);
    }
  };
  apply();
  document.addEventListener('DOMContentLoaded', apply);
})();""" % PAGE_CSS


def dir_attribute() -> str:
    """` dir="rtl"` for HTML that Smart Study places inside Anki's own pages."""
    if is_rtl():
        return ' dir="rtl"'
    import anki.lang
    return ' dir="ltr"' if anki.lang.is_rtl(anki.lang.current_lang or "") else ""


def prepare_view(view) -> None:
    """Call before a page loads: keeps a web view's pages in the add-on's direction."""
    try:
        from PyQt6.QtWebEngineCore import QWebEngineScript
    except ImportError:
        return
    scripts = view.page().scripts()
    for script in scripts.find(_SCRIPT_NAME):
        scripts.remove(script)
    if is_rtl():
        script = QWebEngineScript()
        script.setName(_SCRIPT_NAME)
        script.setSourceCode(_PAGE_SCRIPT)
        script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentCreation)
        script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
        script.setRunsOnSubFrames(True)
        scripts.insert(script)


class _DirectionFilter(QObject):
    """Flips Smart Study's own Qt widgets; Anki's windows keep Anki's direction."""

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.Polish and is_rtl() and isinstance(obj, QWidget):
            if type(obj).__module__.split(".")[0] == _PACKAGE:
                obj.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        return False


_filter = None


def install() -> None:
    global _filter
    if _filter is None and mw is not None:
        _filter = _DirectionFilter(mw)
        mw.app.installEventFilter(_filter)


def offer_anki_language(previous: str) -> None:
    """After switching Smart Study to Persian, offer to switch Anki itself too."""
    import anki.lang
    if previous == "fa" or not is_rtl() or (anki.lang.current_lang or "").startswith("fa"):
        return
    if askUser(_("Switch Anki itself to Persian too? Anki needs a restart for this."), parent=mw):
        mw.pm.setLang(ANKI_PERSIAN)
        tooltip(_("The change takes effect after restarting Anki."), parent=mw)
