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


def test_merge(base):
    """Ticks made on two devices before they synced are both kept; an untick made later stays."""
    col = Collection(os.path.join(base, "merge.anki2"))
    sys.modules["aqt"].mw = types.SimpleNamespace(col=col)
    a, b = device("pc2", base, col), device("laptop2", base, col)
    plan = a.new_plan("Merge", "2026-12-01", "2026-11-01", {})
    plan["days"] = [{"d": "2026-11-12", "items": [{"id": i, "kind": "custom", "custom": True, "text": i} for i in ("x1", "x2", "x3")]}]
    a.save(plan)
    pid = plan["id"]
    b.load(pid)  # the laptop has its copy

    # the laptop ticks x2 while offline: only its file knows
    lap = json.load(open(b._path(pid), encoding="utf-8"))
    lap["done"]["x2"] = "2026-11-10T10:00:00"
    lap["savedAt"] = time.time() - 60
    json.dump(lap, open(b._path(pid), "w", encoding="utf-8"))
    # meanwhile the pc ticks x1 and syncs: the collection carries the pc's (newer) plan
    p = a.load(pid)
    a.set_done(p, "x1", True)
    a.save(p)
    merged = b.load(pid)
    assert set(merged["done"]) == {"x1", "x2"}, merged["done"]
    assert set(a.load(pid)["done"]) == {"x1", "x2"}, "and the pc gets the laptop's tick back"
    print("ticks from two devices are both kept ok")

    # the pc unticks x2; an old laptop copy that still has the tick must not bring it back
    stale = json.load(open(b._path(pid), encoding="utf-8"))
    time.sleep(1.1)
    p = a.load(pid)
    a.set_done(p, "x2", False)
    a.save(p)
    stale["savedAt"] = time.time() - 30
    json.dump(stale, open(b._path(pid), "w", encoding="utf-8"))
    merged = b.load(pid)
    assert set(merged["done"]) == {"x1"}, merged["done"]
    print("an untick is not undone by an older copy ok")

    # the laptop unticks x1 offline (older copy, but its untick is later than the tick)
    lap = json.load(open(b._path(pid), encoding="utf-8"))
    time.sleep(1.1)
    b.set_done(lap, "x1", False)
    lap["savedAt"] = time.time() - 5
    json.dump(lap, open(b._path(pid), "w", encoding="utf-8"))
    p = a.load(pid)
    p["title"] = "Merge 2"  # the pc changes something else and is the newer copy
    time.sleep(0.01)
    a.save(p)
    merged = b.load(pid)
    assert merged["title"] == "Merge 2" and merged["done"] == {}, merged["done"]
    print("an untick from the other device arrives ok")

    # ticks of items the newer plan no longer has (replanned) are not carried over
    lap = json.load(open(b._path(pid), encoding="utf-8"))
    lap["done"]["gone"] = "2026-11-12T11:00:00"
    lap["savedAt"] = time.time() - 5
    json.dump(lap, open(b._path(pid), "w", encoding="utf-8"))
    p = a.load(pid)
    time.sleep(0.01)
    a.save(p)
    assert "gone" not in b.load(pid)["done"]
    col.close()
    print("ticks of removed items are dropped ok")


if __name__ == "__main__":
    if len(sys.argv) != 2 or os.listdir(sys.argv[1]):
        sys.exit("usage: python -I tests/test_store.py <empty folder>")
    test_sync(sys.argv[1])
    test_merge(sys.argv[1])
    print("ALL TESTS OK")
