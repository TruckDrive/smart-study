"""Starts Anki for the GUI smoke test: no first-run language question."""
import faulthandler
import os
import sys

faulthandler.dump_traceback_later(int(os.environ.get("SS_DUMP", "150")), exit=False)
import aqt.profiles  # noqa: E402

aqt.profiles.ProfileManager.setDefaultLang = lambda self, idx: self.setLang("en_US")
from aqt import run  # noqa: E402

sys.argv[0] = "anki"
run()
