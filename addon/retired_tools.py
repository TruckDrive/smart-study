# -*- coding: utf-8 -*-
"""Notebook (notes, to-dos, PDFs) and mind map were removed in Smart Study 3.1.

Nothing a user saved is deleted: the files stay in the Anki profile folder.
Whoever used one of the tools is told once per profile where the data is and
how to get the tools back (install 3.0.5 again).
"""
import os

from aqt import mw
from aqt.qt import QTimer
from aqt.utils import showInfo, tooltip

from .locales import _

NOTICE_KEY = "retired_tools_notice"
LAST_VERSION_URL = "github.com/TruckDrive/smart-study/releases/tag/v3.0.5"

# Path inside the profile folder -> what it holds (English source text).
DATA_FILES = (
    ("notebook.sqlite", "Notes, to-dos and linked PDFs"),
    ("mindmap_recovery.json", "Mind maps"),
    (os.path.join("SmartStudy_Data", "roadmaps.sqlite3"), "Free maps"),
)


def found_data(profile_folder):
    """The data files of the removed tools that exist in this profile."""
    found = []
    for name, label in DATA_FILES:
        path = os.path.join(profile_folder, name)
        try:
            if os.path.getsize(path) > 0:
                found.append((path, label))
        except OSError:
            continue
    return found


def notify_once(settings, save):
    """Tell a former user of the tools, once per profile, where the data is."""
    if not mw or not mw.pm or not mw.pm.profileFolder():
        return
    seen = settings.get(NOTICE_KEY)
    seen = list(seen) if isinstance(seen, list) else []
    profile = mw.pm.name
    if profile in seen:
        return
    seen.append(profile)
    settings[NOTICE_KEY] = seen
    save()
    found = found_data(mw.pm.profileFolder())
    if not found:
        return
    lines = "\n".join(f"{_(label)}:\n{path}" for path, label in found)
    text = _(
        "The notebook (notes, to-dos, PDFs) and the mind map were removed in Smart Study 3.1.\n\n"
        "Your data was not deleted. It is still here:\n\n{}\n\n"
        "To keep using these tools, install Smart Study 3.0.5 again from:\n{}"
    ).format(lines, LAST_VERSION_URL)
    QTimer.singleShot(1500, lambda: showInfo(text, title=_("Notebook and mind map were removed")))


def pdf_link_clicked():
    """A card made from a PDF by the removed notebook still carries its link."""
    tooltip(_("This PDF link belonged to the notebook, which was removed in Smart Study 3.1."), period=4000)
