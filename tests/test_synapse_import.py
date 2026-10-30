# python -I tests/test_synapse_import.py  – Synapse's level is taken over once when it is ahead
import copy
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OLD_KEY = "addon_GamificationPlusDailyWidgets_SynapsePro1_data"


class FakeCol:
    def __init__(self, conf=None):
        self.conf = dict(conf or {})

    def get_config(self, key, default=None):
        return copy.deepcopy(self.conf.get(key, default))


def load(col, profile):
    tips = []
    aqt = types.ModuleType("aqt")
    aqt.mw = types.SimpleNamespace(col=col, pm=types.SimpleNamespace(
        profileFolder=lambda: profile, night_mode=lambda: False))
    utils = types.ModuleType("aqt.utils")
    utils.showInfo = utils.askUser = utils.QMessageBox = None
    utils.tooltip = lambda text, period=0: tips.append(text)
    qt = types.ModuleType("aqt.qt")
    qt.QTimer = types.SimpleNamespace(singleShot=lambda ms, fn: fn())
    sys.modules.update({"aqt": aqt, "aqt.utils": utils, "aqt.qt": qt})
    pkg = types.ModuleType("ss")
    pkg.__path__ = [os.path.join(ROOT, "addon")]
    sys.modules["ss"] = pkg
    ach = types.ModuleType("ss.achievements")
    ach.BADGES, ach.ReviewHistory, ach.update_achievements = [], object, None
    sys.modules["ss.achievements"] = ach
    spec = importlib.util.spec_from_file_location("ss.gamification", os.path.join(ROOT, "addon", "gamification.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    def init(self):
        self.data = {}
        self.load_data()
    module.GamificationManager.__init__ = init
    return module, tips


def run(conf, synapse_file=None):
    profile = tempfile.mkdtemp()
    try:
        if synapse_file:
            os.makedirs(os.path.join(profile, "SynapsePro_Data"))
            with open(os.path.join(profile, "SynapsePro_Data", "gamification_data.json"), "w") as f:
                json.dump(synapse_file, f)
        col = FakeCol(conf)
        module, tips = load(col, profile)
        manager = module.GamificationManager()
        again = module.GamificationManager()
        return manager.data, again.data, tips, col.conf[module.CONFIG_KEY]
    finally:
        shutil.rmtree(profile)


synapse = {"level": 53, "xp": 40, "streak": 9, "version": 4,
           "study_xp_ledger": {"start_ms": 1, "paid": 7}}

# Fresh Smart Study, Synapse data in the collection
data, again, tips, stored = run({OLD_KEY: synapse})
assert data["level"] == 53 and data["xp"] == 40 and data["study_xp_ledger"]["paid"] == 7
assert data["synapse_import_done"] and stored["level"] == 53
assert len(tips) == 1 and "53" in tips[0], tips
assert again["level"] == 53

# Only the profile backup left
data, *_ = run({}, synapse_file=synapse)
assert data["level"] == 53

# Smart Study already ahead: keep it, never ask again
ss_key = "addon_GamificationPlusDailyWidgets_SmartStudy1_data"
data, again, tips, _ = run({OLD_KEY: synapse, ss_key: {"level": 60, "xp": 0, "version": 4}})
assert data["level"] == 60 and data["synapse_import_done"] and not tips

# Imported once: later Synapse data does not overwrite progress
done = {"level": 2, "xp": 0, "version": 4, "synapse_import_done": True}
data, *_ = run({OLD_KEY: synapse, ss_key: done})
assert data["level"] == 2

# No Synapse at all: defaults, flag stays unset for a later sync
data, _, tips, _ = run({})
assert data["level"] == 1 and "synapse_import_done" not in data and not tips

print("ok")
