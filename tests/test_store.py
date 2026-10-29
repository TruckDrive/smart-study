# python -I tests/test_store.py <empty folder>  – two "devices" share one throwaway collection, never your real one
import importlib
import json
import os
import shutil
import sys
import time
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from anki.collection import Collection  # noqa: E402


def device(name, base, col):
    """A copy of the add-on with its own user_files, as on a second computer."""
    folder = os.path.join(base, name)
    shutil.copytree(os.path.join(ROOT, "addon", "plan"), folder, ignore=shutil.ignore_patterns("__pycache__", "user_files"))
    pkg = types.ModuleType(name)
    pkg.__path__ = [folder]
    sys.modules[name] = pkg
    return importlib.import_module(name + ".store")


def test_sync(base):
    col = Collection(os.path.join(base, "collection.anki2"))
    aqt = types.ModuleType("aqt")
    aqt.mw = types.SimpleNamespace(col=col)  # store.py takes the collection from mw
    sys.modules["aqt"] = aqt
    a, b = device("pc", base, col), device("laptop", base, col)

    plan = a.new_plan("Anatomy", "2026-11-05", "2026-10-27", {})
    a.save(plan)
    pid = plan["id"]
    assert [p["id"] for p in b.list_plans()] == [pid]
    assert os.path.exists(b._path(pid)), "the laptop keeps its own file"
    print("new plan reaches the other device ok")

    p = b.load(pid)
    p["done"]["x1"] = "2026-10-27T12:00"
    time.sleep(0.01)
    b.save(p)
    assert "x1" in a.load(pid)["done"]
    with open(a._path(pid), encoding="utf-8") as f:
        assert "x1" in json.load(f)["done"], "the file is updated too"
    print("newer copy wins ok")

    with open(a._path(pid), encoding="utf-8") as f:  # a script writes the file directly
        q = json.load(f)
    q["title"], q["savedAt"] = "Anatomy (by script)", time.time()
    with open(a._path(pid), "w", encoding="utf-8") as f:
        json.dump(q, f)
    a.list_plans()  # what happens on start / before a sync
    assert b.load(pid)["title"] == "Anatomy (by script)"
    print("files written by other tools ok")

    legacy = {"id": "old", "title": "Old", "exam": "2026-12-01", "start": "2026-11-01"}  # from before 0.3.0: no savedAt
    with open(os.path.join(os.path.dirname(a._path(pid)), "old.json"), "w", encoding="utf-8") as f:
        json.dump(legacy, f)
    a.list_plans()
    assert "old" in [p["id"] for p in b.list_plans()]
    print("plans from older versions ok")

    a.delete(pid)
    assert pid not in [p["id"] for p in b.list_plans()] and not os.path.exists(b._path(pid))
    print("delete everywhere ok")

    prof = a.profile()
    prof["minutesPerDay"] = 300
    a.save_profile(prof)
    assert b.profile()["minutesPerDay"] == 300
    print("profile ok")
    col.close()


if __name__ == "__main__":
    if len(sys.argv) != 2 or os.listdir(sys.argv[1]):
        sys.exit("usage: python -I tests/test_store.py <empty folder>")
    test_sync(sys.argv[1])
    print("ALL TESTS OK")
