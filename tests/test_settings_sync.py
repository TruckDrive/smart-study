# python -I tests/test_settings_sync.py  – two "devices" share one fake collection config
import copy
import importlib.util
import os
import sys
import time
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class FakeCol:
    """Collection config as Anki stores it: JSON values, copied on get and set."""

    def __init__(self):
        self.conf = {}

    def get_config(self, key, default=None):
        return copy.deepcopy(self.conf.get(key, default))

    def set_config(self, key, value):
        self.conf[key] = copy.deepcopy(value)


def load_module(col):
    aqt = types.ModuleType("aqt")
    aqt.mw = types.SimpleNamespace(col=col)
    sys.modules["aqt"] = aqt
    spec = importlib.util.spec_from_file_location("settings_sync", os.path.join(ROOT, "addon", "settings_sync.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_settings():
    col = FakeCol()
    sync = load_module(col)
    pc = {"language": "de", "active_color_theme": "forest", "launcher_sidebar_open": False, "last_seen_version": "2.2.0"}
    laptop = {"language": "en", "active_color_theme": "ocean", "launcher_sidebar_open": True}

    assert sync.pull_settings(pc) == {}, "nothing in the collection yet: the pc pushes"
    stored = col.conf[sync.CONF_KEY]["settings"]
    assert "launcher_sidebar_open" not in stored and "last_seen_version" not in stored and sync.STAMP_KEY not in stored
    print("first device pushes, device-only keys stay local ok")

    changed = sync.pull_settings(laptop)
    assert changed == {"language": "de", "active_color_theme": "forest"}, changed
    assert laptop["launcher_sidebar_open"] is True, "device-only key untouched"
    print("second device takes the settings ok")

    stamp = col.conf[sync.CONF_KEY]["settingsAt"]
    sync.push_settings(laptop)
    assert col.conf[sync.CONF_KEY]["settingsAt"] == stamp, "unchanged settings are not pushed again"
    laptop["launcher_sidebar_open"] = False
    sync.push_settings(laptop)
    assert col.conf[sync.CONF_KEY]["settingsAt"] == stamp, "a device-only change is not pushed"
    print("no push without a real change ok")

    time.sleep(0.01)
    laptop["language"] = "fr"
    sync.push_settings(laptop)
    assert sync.pull_settings(pc) == {"language": "fr"}
    assert sync.pull_settings(pc) == {}, "already up to date"
    print("change on the laptop reaches the pc ok")


def test_integrations():
    col = FakeCol()
    sync = load_module(col)
    pc = {"enabled": {"heatmap": False}, "choice": {"heatmap": "standalone"}}
    laptop = {"enabled": {}, "choice": {}}
    assert sync.pull_integrations(pc) is False
    assert col.conf[sync.CONF_KEY]["integrations"] == {"heatmap": False}
    assert sync.pull_integrations(laptop) is True
    assert laptop["enabled"] == {"heatmap": False} and laptop["choice"] == {}, "choice stays per device"
    assert sync.pull_integrations(laptop) is False
    print("add-on switches sync, the choice of copy does not ok")


def test_no_collection():
    sync = load_module(None)
    settings = {"language": "de"}
    assert sync.pull_settings(settings) == {}
    sync.push_settings(settings)
    assert sync.STAMP_KEY not in settings
    print("without a collection nothing happens ok")


if __name__ == "__main__":
    test_settings()
    test_integrations()
    test_no_collection()
