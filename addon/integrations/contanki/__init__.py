"""An add-on for Anki, adding support for controllers and gamepads"""
# Modified for Smart Study (bundled copy of Contanki 1.0.2): config and user
# files live in smart_study/user_files, profiles of a separately installed
# Contanki are taken over once, and controller detection was reworked
# (see controller.js and controller.py).

import os
import shutil

from aqt import mw
from .utils import user_files_path, user_profile_path, user_controllers_path

assert mw is not None


def _take_over_standalone_files() -> None:
    """Copies profiles and custom controllers of a standalone Contanki once."""
    if os.path.isdir(user_files_path):
        return
    for folder in ("1898790263", "contanki", "anki-contanki"):
        old = os.path.join(mw.addonManager.addonsFolder(), folder, "user_files")
        if os.path.isdir(old):
            shutil.copytree(old, user_files_path, dirs_exist_ok=True)
            return


_take_over_standalone_files()
# controller.py lists these folders on import.
os.makedirs(user_profile_path, exist_ok=True)
os.makedirs(user_controllers_path, exist_ok=True)
# Controller → profile assignments; Contanki ships this file in its own user_files.
if not os.path.exists(os.path.join(user_files_path, "controllers")):
    with open(os.path.join(user_files_path, "controllers"), "w", encoding="utf8") as f:
        f.write("{}")

from .contanki import Contanki  # noqa: E402

mw.contanki = Contanki(mw) # type: ignore
