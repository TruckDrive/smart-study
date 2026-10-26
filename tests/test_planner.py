# python -I tests/test_planner.py  (no Anki needed)
import os
import sys
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "addon"))
import planner as P  # noqa: E402

P.LANG = "de"  # the assertions check the German texts


def sample():
    return {
        "id": "pt", "title": "Bauch", "exam": "2026-11-06", "start": "2026-10-26", "minutesPerDay": 180,
        "offWeekdays": [6], "dayMinutes": {"2026-10-28": 60}, "order": "auto", "done": {}, "days": [],
        "sources": [
            {"id": "hb", "type": "pages", "name": "Handbuch", "minPerUnit": 6},
            {"id": "pv", "type": "videos", "name": "Präpvideos", "defaultMin": 20,
             "videos": [{"id": "v1", "name": "Bauchsitus 1 – Allgemeines", "min": 25}, {"id": "v2", "name": "Leber", "min": 18},
                        {"id": "v3", "name": "Unterbauchgefäße"}, {"id": "v4", "name": "Extra Bonus"}]},
            {"id": "ab", "type": "anki", "name": "AnkiBuddy", "deck": "SEKU::Bauch", "minPerUnit": 1, "maxNew": 60},
        ],
        "topics": [
            {"id": "t2", "name": "Leber", "pages": {"hb": [82, 85]}, "videos": {"pv": ["v2"]}, "anki": {"ab": 'deck:"SEKU::Bauch::Leber"'}},
            {"id": "t1", "name": "Peritoneum", "pages": {"hb": [78, 81]}, "videos": {"pv": ["v1"]}, "anki": {"ab": 'deck:"SEKU::Bauch::Peritoneum"'}},
            {"id": "t3", "name": "Unterbauch", "pages": {"hb": [86, 91]}, "videos": {"pv": ["v3"]}},
        ],
    }


def counts_for(plan, new):
    out = {}
    for q in P.queries(plan):
        n = new.get(q, 0)
        out[q] = {"total": n + 10, "new": n}
    return out


def flat(plan):
    return [(d["d"], it) for d in plan["days"] for it in d["items"]]


def test_build():
    plan = sample()
    tq = P.topic_query(plan, plan["topics"][1], plan["sources"][2])
    lq = P.topic_query(plan, plan["topics"][0], plan["sources"][2])
    rq = P.rest_query(plan, plan["sources"][2])
    c = counts_for(plan, {tq: 120, lq: 80, rq: 40})
    notes = P.build(plan, c, date(2026, 10, 26))
    items = flat(plan)
    days = [d["d"] for d in plan["days"]]
    assert days[0] == "2026-10-26" and days[-1] == "2026-11-06", days
    # automatic order by page: Peritoneum (78) before Leber (82)
    pages = [it for _, it in items if it["kind"] == "pages"]
    assert pages[0]["pages"][0] == 78, pages[0]
    assert sum(it["pages"][1] - it["pages"][0] + 1 for it in pages) == 14
    # all videos included, also the unassigned one
    assert sorted(it["video"] for _, it in items if it["kind"] == "video") == ["v1", "v2", "v3", "v4"]
    # all new cards distributed, targets cumulative
    cards = [it for _, it in items if it["kind"] == "cards"]
    assert sum(it["cards"] for it in cards) == 240
    per_q = {}
    for it in cards:
        per_q.setdefault(it["auto"]["query"], []).append(it["auto"]["target"])
    for q, ts in per_q.items():
        assert ts == sorted(ts), ts
    assert per_q[tq][-1] == 10 + 120
    # daily limit of 60 new cards
    by_day = {}
    for d, it in items:
        if it["kind"] == "cards":
            by_day[d] = by_day.get(d, 0) + it["cards"]
    assert max(by_day.values()) <= 60, by_day
    # Sunday off, no content; reserve days at the end
    assert not [it for d, it in items if d == "2026-11-01" and it["kind"] not in ("reviews",)]
    kinds = {d: {it["kind"] for it in plan["days"][i]["items"]} for i, d in enumerate(days)}
    assert "final" not in kinds
    assert "sim" in kinds["2026-11-04"] and "weakround" in kinds["2026-11-03"], kinds
    assert kinds["2026-11-06"] >= {"note", "reviews"}
    # for every topic: reading before cards
    order = [it["kind"] for _, it in items if it.get("topic") == "t1"]
    assert order.index("pages") < order.index("cards"), order
    print("build ok", notes, by_day)
    return plan, c


def test_replan():
    plan, c = test_build()
    # day 1 half done: first page unit checked, rest open
    first = [it for d, it in flat(plan) if d == "2026-10-26" and it["kind"] == "pages"][0]
    plan["done"][first["id"]] = "2026-10-26T18:00"
    tq = P.topic_query(plan, plan["topics"][1], plan["sources"][2])
    c[tq]["new"] -= 30
    P.build(plan, c, date(2026, 10, 27))
    items = flat(plan)
    assert first["id"] in [it["id"] for _, it in items]
    moved = [it for d, it in items if it.get("moved")]
    assert moved and all(d == "2026-10-26" for d, _ in [(d, it) for d, it in items if it.get("moved")])
    pages = [it for d, it in items if it["kind"] == "pages" and not it.get("moved")]
    covered = sum(it["pages"][1] - it["pages"][0] + 1 for it in pages)
    assert covered == 14, covered  # done + redistributed = every page exactly once
    nums = [n for it in pages for n in range(it["pages"][0], it["pages"][1] + 1)]
    assert len(nums) == len(set(nums))
    assert P.overdue(plan, {}, "2026-10-27") == []
    print("replan ok")


def test_evaluate():
    plan, c = test_build()
    st = {"today": "2026-10-26", "due": 0, "rated": {}, "counts": c}
    ev = P.evaluate(plan, st)
    rv = [it for d, it in flat(plan) if d == "2026-10-26" and it["kind"] == "reviews"][0]
    assert ev[rv["id"]]["done"]
    first_cards = [it for _, it in flat(plan) if it["kind"] == "cards"][0]
    assert not ev[first_cards["id"]]["done"]
    q = first_cards["auto"]["query"]
    c[q]["new"] -= first_cards["cards"]
    assert P.evaluate(plan, st)[first_cards["id"]]["done"]
    c[q] = {"total": 0, "new": 0}  # deck deleted/renamed: don't count as done
    assert first_cards["id"] not in P.evaluate(plan, st)
    print("evaluate ok")


def test_parse_and_match():
    toc = P.parse_toc("Peritoneum ........ 78\nLeistenkanal 82–84\n85 Dünndarm\nColon 88")
    assert toc == [{"name": "Peritoneum", "from": 78, "to": 81}, {"name": "Leistenkanal", "from": 82, "to": 84},
                   {"name": "Dünndarm", "from": 85, "to": 87}, {"name": "Colon", "from": 88, "to": 88}], toc
    lst = P.parse_list("Bauchsitus 1 – Allgemeines | 25\nLeber (18 min)\nOberbauchgefäße 12:30\n- Becken")
    assert [x["min"] for x in lst] == [25, 18, 13, None], lst
    assert lst[2]["name"] == "Oberbauchgefäße"
    plan = sample()
    cands = {"ab": [{"label": "Leber & Gallenwege", "query": "q1"}, {"label": "Peritoneum", "query": "q2"},
                    {"label": "Canalis inguinalis", "query": "q3"}]}
    for t in plan["topics"]:
        t["anki"] = {}
        t["videos"] = {}
    s = P.suggest(plan, cands)
    assert s["t2"]["ab"][0]["query"] == "q1", s["t2"]
    assert s["t1"]["ab"][0]["query"] == "q2"
    assert s["t3"]["pv"][0]["id"] == "v3", s["t3"]
    n = P.apply_suggestions(plan, s)
    assert plan["topics"][0]["videos"]["pv"] == ["v2"] and n >= 4, (n, plan["topics"])
    assert P.similarity("Leistenkanal", "Canalis inguinalis") < 0.55
    print("parse/match ok")


def test_milestones():
    plan = sample()
    plan["sources"].append({"id": "vmc", "type": "tasks", "name": "VMC", "tasks": [
        {"id": "x1", "name": "VMC Niere 1", "min": 40, "url": "https://vmc.example/niere1"}]})
    plan["milestones"] = [{"id": "m1", "name": "Testat Leber", "date": "2026-10-30", "time": "13:15"}]
    plan["topics"][0]["milestone"] = "m1"          # Leber (p. 82) comes first although Peritoneum has p. 78
    plan["topics"][0]["tasks"] = {"vmc": ["x1"]}
    assert [t["id"] for t in P.ordered_topics(plan)] == ["t2", "t1", "t3"]
    lq = P.topic_query(plan, plan["topics"][0], plan["sources"][2])
    c = counts_for(plan, {lq: 50})
    P.build(plan, c, date(2026, 10, 26))
    items = flat(plan)
    leber = [(d, it) for d, it in items if it.get("topic") == "t2" and it["kind"] != "reviews"]
    assert leber and all(d < "2026-10-30" for d, _ in leber), leber
    assert any(it.get("url") for _, it in leber)
    assert all(it.get("for") == "Testat Leber" for _, it in leber)
    notes = [it["text"] for d, it in items if d == "2026-10-30" and it["kind"] == "note"]
    assert notes and "Testat Leber um 13:15" in notes[0], notes
    assert [it for d, it in items if d == "2026-10-29" and it["kind"] == "note"], "review day before the test is missing"
    other = [d for d, it in items if it.get("topic") in ("t1", "t3") and it["kind"] in ("pages", "video")]
    assert other and min(other) > "2026-10-30", other
    # test is over: its material is no longer scheduled
    P.build(plan, c, date(2026, 10, 31))
    assert not [it for d, it in flat(plan) if d >= "2026-10-31" and it.get("topic") == "t2" and it["kind"] != "reviews"]
    lst = P.parse_list("VMC Endokrinologie 2 | 35 | https://vmc.x/abc\nhttps://vmc.x/only")
    assert lst[0] == {"name": "VMC Endokrinologie 2", "min": 35, "url": "https://vmc.x/abc"}, lst
    assert lst[1]["url"] == "https://vmc.x/only"
    print("milestones ok")


def test_prep():
    plan = sample()
    plan["milestones"] = [{"id": "s1", "name": "Leber präparieren", "date": "2026-10-28", "prep": True}]
    plan["topics"][0]["milestone"] = "s1"
    lq = P.topic_query(plan, plan["topics"][0], plan["sources"][2])
    c = counts_for(plan, {lq: 50})
    P.build(plan, c, date(2026, 10, 26))
    items = flat(plan)
    prep = [(d, it) for d, it in items if it.get("topic") == "t2" and it["kind"] in ("pages", "video")]
    assert prep and all(d < "2026-10-28" for d, _ in prep), prep
    cards = [d for d, it in items if it.get("topic") == "t2" and it["kind"] == "cards"]
    assert sum(it["cards"] for d, it in items if it.get("topic") == "t2" and it["kind"] == "cards") == 50
    assert [it for d, it in items if d == "2026-10-28" and it["kind"] == "note" and "Präpsaal" in it["text"]]
    assert not [it for d, it in items if d == "2026-10-27" and it["kind"] == "note"], "no review day before a lab session"
    # lab session over, preparation still open: scheduled anyway
    P.build(plan, c, date(2026, 10, 29))
    assert [it for d, it in flat(plan) if d >= "2026-10-29" and it.get("topic") == "t2" and it["kind"] == "pages"]
    print("prep ok")


def test_misc():
    assert P.streak({"2026-10-24", "2026-10-23", "2026-10-21"}, "2026-10-24") == 2
    assert P.streak({"2026-10-23", "2026-10-22"}, "2026-10-24") == 2
    plan, c = test_build()
    w = P.weak_items(plan, [{"topic": "t1", "agains": 9, "lapses": 4, "cards": 5}])
    assert "Peritoneum: 9 Fehler" in w[0]["text"] and "S. 78–81" in w[0]["text"], w
    rs = P.review_stats(plan, {})
    assert rs["planned"] > 0 and rs["done"] == 0
    # exam is over
    P.build(plan, c, date(2026, 11, 10))
    print("misc ok")


def test_reviews_and_budget():
    plan = sample()
    tq = P.topic_query(plan, plan["topics"][1], plan["sources"][2])
    c = counts_for(plan, {tq: 120})
    fc = {"due": {-3: 200, 0: 40, 2: 30}, "min": 0.5}
    P.build(plan, c, date(2026, 10, 26), forecast=fc)
    rev = {d["d"]: it for d in plan["days"] for it in d["items"] if it["kind"] == "reviews"}
    # 200 overdue spread over 4 days + 40 today
    assert rev["2026-10-26"]["reviews"] >= 90 and rev["2026-10-26"]["min"] == round(rev["2026-10-26"]["reviews"] * 0.5), rev["2026-10-26"]
    # new cards come back: there are reviews the day after
    load = P.day_load(plan, date(2026, 10, 26))
    for s, m in load.items():
        cap = P.capacity(plan, P.s2d(s))
        assert m <= cap + 30, (s, m, cap)
    # total budget: another plan already uses 150 of 200 minutes
    plan2 = sample()
    budget = {"minutesPerDay": 200, "dayMinutes": {}}
    taken = {d: 150 for d in ("2026-10-26", "2026-10-27", "2026-10-29", "2026-10-30")}
    P.build(plan2, c, date(2026, 10, 26), budget=budget, taken=taken)
    l2 = P.day_load(plan2, date(2026, 10, 26))
    assert l2.get("2026-10-26", 0) <= 55 and l2.get("2026-10-31", 0) > 55, l2
    print("reviews/budget ok")


def test_once_and_review_only():
    plan = sample()
    plan["onceOnly"] = True
    plan["milestones"] = [{"id": "m1", "name": "Einheit 1", "date": "2026-10-29"}]
    plan["topics"][1]["milestone"] = "m1"
    sc = P.review_scopes(plan)
    assert any(b == "2026-10-29" for _, _, b in sc) and any(b == plan["exam"] for _, _, b in sc), sc
    assert P.review_query(plan, "2026-11-02") and "Peritoneum" not in P.review_query(plan, "2026-11-02")
    # returning new cards stop at the unit's date
    rl = P.review_load(None, date(2026, 10, 26), date(2026, 11, 6), [], {("2026-10-27", "2026-10-29"): 10})
    assert rl == {"2026-10-28": 10}, rl
    plan2 = sample()
    plan2["sources"][2]["reviewOnly"] = True
    plan2["sources"][2]["reviewsFrom"] = "2026-11-01"
    tq = P.topic_query(plan2, plan2["topics"][1], plan2["sources"][2])
    P.build(plan2, counts_for(plan2, {tq: 50}), date(2026, 10, 26))
    assert not [it for d in plan2["days"] for it in d["items"] if it["kind"] == "cards"]
    assert P.review_scopes(plan2)[0][1] == "2026-11-01" and P.review_query(plan2, "2026-10-27") is None
    print("once/reviewOnly ok")


if __name__ == "__main__":
    test_build()
    test_replan()
    test_evaluate()
    test_parse_and_match()
    test_misc()
    test_milestones()
    test_prep()
    test_reviews_and_budget()
    test_once_and_review_only()
    print("ALL TESTS OK")
