"""Where the Smart Study browser is shown: sidebar, split view, main window
or its own window. The work is done by dock_layout, shared with the other
sidebars; this keeps the browser's names for it."""
from __future__ import annotations

from . import dock_layout

try:
    from .locales import _
except ImportError:  # pragma: no cover
    def _(text):  # type: ignore
        return text

KEY = "website"


def _ws():
    from . import website_sidebar
    return website_sidebar


def _register() -> None:
    if KEY in dock_layout._targets:
        return
    dock_layout.register(
        KEY, lambda: _ws().sidebar_dock, lambda: _ws().show_browser(), _("Browser"),
        is_main=lambda: _ws().website_window is not None,
        enter_main=lambda: _ws().open_website_window(),
        exit_main=lambda: _ws().close_website_window())


def is_window() -> bool:
    _register()
    return dock_layout.is_window(KEY)


def mode() -> str:
    _register()
    return dock_layout.mode(KEY)


def fill_menu(menu) -> None:
    _register()
    dock_layout.fill_menu(menu, KEY)


def set_mode(target: str) -> None:
    _register()
    dock_layout.set_mode(KEY, target)


def bring_forward() -> bool:
    _register()
    return dock_layout.bring_forward(KEY)


def cleanup() -> None:
    dock_layout.cleanup(KEY)
