# python -I tests/test_robust.py <empty folder>
# Things that must not break a plan: files damaged on disk, plans with missing
# fields (old versions, scripts, other devices), days without free time, and
# the day counting done by the database. Uses a throwaway collection only.
import importlib
import json
import os
import random
import shutil
import sys
import types
from datetime import timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
base = sys.argv[1]

from anki.collection import Collection  # noqa: E402

folder = os.path.join(base, "dev")
shutil.copytree(os.path.join(ROOT, "addon", "plan"), folder, ignore=shutil.ignore_patterns("__pycache__", "user_files"))
pkg = types.ModuleType("dev")
pkg.__path__ = [folder]
sys.modules["dev"] = pkg
aqt = types.ModuleType("aqt")
aqt.mw = types.SimpleNamespace(col=None)
sys.modules["aqt"] = aqt
store = importlib.import_module("dev.store")
P = importlib.import_module("dev.planner")
A = importlib.import_module("dev.ankidata")
P.LANG = "de"


def test_normalize():
    bare = store.normalize({"id": "p1", "minutesPerDay": "abc", "status": "weird", "sources": [
        {"id": "s1", "type": "videos"}, {"type": "pages"}, "junk", {"id": "s9", "type": "unknown"}],
        "topics": [{"id": "t1"}, None], "days": [{"d": "2026-11-12", "items": [{"text": "x"}, 5]}, {"items": []}, "junk",
                                                 {"d": "2026-11-11"}], "done": None, "milestones": [{"date": "2026-11-20"}]})
    assert bare["minutesPerDay"] == 180 and bare["status"] == "active" and bare["done"] == {} and bare["autoDone"] == {}
    assert [s["id"] for s in bare["sources"]] == ["s1"] and bare["sources"][0]["videos"] == []
    assert bare["topics"] == [{"id": "t1", "name": "", "pages": {}, "videos": {}, "tasks": {}, "anki": {}}]
    assert [d["d"] for d in bare["days"]] == ["2026-11-11", "2026-11-12"], "sorted, days without a date dropped"
    it = bare["days"][1]["items"][0]
    assert it["id"] and it["kind"] == "custom" and len(bare["days"][1]["items"]) == 1
    assert bare["milestones"][0]["id"] and bare["exam"] == "" and bare["title"] == ""
    # everything the planner touches works on such a plan
    assert P.progress(bare, {}) == (1, 1) or P.progress(bare, {}) == (0, 1)
    assert P.queries(bare) == [] and P.overdue(bare, {}, "2026-11-13") == [it["id"]]
    full = store.new_plan("A", "2026-12-01", "2026-11-01", {})
    before = json.dumps(full, sort_keys=True)
    assert json.dumps(store.normalize(full), sort_keys=True) == before, "a complete plan is left alone"
    print("plans with missing fields are completed ok")


def test_broken_file():
    plan = store.new_plan("Anatomy", "2026-12-01", "2026-11-01", {})
    store.save(plan)
    path = store._path(plan["id"])
    with open(path, "w", encoding="utf-8") as f:
        f.write('{"id": "' + plan["id"] + '", "title": "Anat')  # cut off, as after a power cut
    assert store.list_plans() == []
    left = os.listdir(store.PLANS)
    assert not os.path.exists(path) and any(".broken-" in n for n in left), left
    with open(os.path.join(store.PLANS, "list.json"), "w", encoding="utf-8") as f:
        f.write("[1, 2]")  # JSON, but no plan
    with open(os.path.join(store.PLANS, "evil.json"), "w", encoding="utf-8") as f:
        json.dump({"id": "../../x", "title": "t"}, f)  # an id that would leave the folder
    assert store.list_plans() == []
    assert not [n for n in os.listdir(store.PLANS) if n.endswith(".tmp")], "no half-written file stays behind"
    prof = store.profile()
    assert prof["rates"] == P.DEFAULT_RATES and prof["history"] == []
    with open(store.PROFILE, "w", encoding="utf-8") as f:
        json.dump({"rates": {"pages": -1, "anki": "x"}, "history": 3}, f)
    prof = store.profile()
    assert prof["rates"] == P.DEFAULT_RATES and prof["history"] == [], prof
    print("damaged files are put aside, nothing crashes ok")


def test_split_minutes():
    assert P.split_minutes("Altfragen 2023 45 min") == (45, "Altfragen 2023")
    assert P.split_minutes("Altfragen 2023") == (None, "Altfragen 2023"), "a year is no duration"
    assert P.split_minutes("Skript lesen (1,5 h)") == (90, "Skript lesen")
    assert P.split_minutes("Kapitel 3") == (None, "Kapitel 3")
    assert P.split_minutes("20 min") == (None, "20 min"), "nothing left as a name"
    print("durations in custom items ok")


def test_no_free_time():
    """Reviews eat every minute: the material is still spread over the days, not piled on the last one."""
    plan = store.new_plan("Voll", "2026-11-20", "2026-11-10", {})
    plan["minutesPerDay"] = 30
    plan["sources"] = [{"id": "hb", "type": "pages", "name": "Buch", "minPerUnit": 5},
                       {"id": "ab", "type": "anki", "name": "Karten", "decks": ["X"], "minPerUnit": 1}]
    plan["topics"] = [{"id": "t1", "name": "A", "pages": {"hb": [1, 40]}, "videos": {}, "tasks": {}, "anki": {}}]
    forecast = {"due": {str(k): 500 for k in range(0, 11)}, "min": 0.4}  # 200 min of reviews a day
    notes = P.build(plan, {}, P.s2d("2026-11-10"), forecast=forecast)
    per_day = {d["d"]: sum(it["pages"][1] - it["pages"][0] + 1 for it in d["items"] if it["kind"] == "pages") for d in plan["days"]}
    assert sum(per_day.values()) == 40
    assert max(per_day.values()) <= 12, per_day
    assert notes, "and the plan says that it is too full"
    print("no free time: spread evenly ok")


def test_ratings_per_day():
    col = Collection(os.path.join(base, "r.anki2"))
    m = col.models.by_name("Basic")
    did = col.decks.id("D")
    for i in range(6):
        n = col.new_note(m)
        n["Front"] = f"q{i}"
        col.add_note(n, did)
    cids = col.find_cards("deck:D")
    rnd = random.Random(7)
    cutoff = col.sched.day_cutoff
    rows = []
    for i in range(400):
        ms = (cutoff - rnd.randint(1, 40 * 86400)) * 1000 + i  # unique ids over 40 days, also right at the day borders
        rows.append((ms, rnd.choice(cids), rnd.choice([0, 1, 2, 3, 4])))
    rows += [((cutoff - 1) * 1000 + 999, cids[0], 3), ((cutoff - 86400) * 1000 + 401, cids[1], 3), ((cutoff - 86400 - 1) * 1000 + 402, cids[2], 3)]
    for ms, cid, ease in rows:
        col.db.execute("insert into revlog values (?, ?, -1, ?, 1, 1, 2500, 5000, 1)", ms, cid, ease)
    since = A.day_start_ms(col, A.today(col) - timedelta(days=30))
    want_all, want_some, some = {}, {}, set(cids[:3])
    for ms, cid, ease in rows:
        if ms >= since and ease > 0:
            k = A.day_of(col, ms).isoformat()
            want_all[k] = want_all.get(k, 0) + 1
            if cid in some:
                want_some[k] = want_some.get(k, 0) + 1
    assert A.ratings_per_day(col, since) == want_all
    assert A.ratings_per_day(col, since, some) == want_some
    assert A.ratings_per_day(col, since, []) == {}
    assert A.activity(col, 30) == want_all
    plan = store.normalize({"id": "p", "exam": (A.today(col) + timedelta(days=5)).isoformat(), "start": "not a date",
                            "sources": [{"id": "a", "type": "anki", "decks": ["D", 'gone "deck"']}]})
    st = A.stats(col, plan)  # a start that is no date and a deck that does not exist
    assert st["decks"]["a"]["total"] == 6 and isinstance(st["rated"], dict)
    assert A.weak(col, plan) == [] and A.time_stats(col, plan)["minutes"] >= 0
    col.close()
    print("ratings per day: database counts like Python ok")


if __name__ == "__main__":
    test_normalize()
    test_broken_file()
    test_split_minutes()
    test_no_free_time()
    test_ratings_per_day()
    print("ALL TESTS OK")
