# python -I tests/test_ankidata.py <leerer Ordner>  – nutzt eine Wegwerf-Sammlung, nie die echte
import os
import sys
import types
from datetime import timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pkg = types.ModuleType("lp")  # Add-on-Ordner als Paket laden, ohne __init__ (braucht mw)
pkg.__path__ = [os.path.join(ROOT, "addon")]
sys.modules["lp"] = pkg

from anki.collection import Collection  # noqa: E402

from lp import ankidata as A, planner as P  # noqa: E402

base = sys.argv[1]
path = os.path.join(base, "test.anki2")
if os.path.exists(path):
    os.remove(path)
col = Collection(path)
m = col.models.by_name("Basic")
for sub, n in (("Leber", 12), ("Peritoneum", 8), ("Sonstiges", 5)):
    did = col.decks.id(f"SEKU::Bauch::{sub}")
    for i in range(n):
        note = col.new_note(m)
        note["Front"], note["Back"] = f"{sub} {i}", "x"
        note.tags = ["Bauch", "Leistenkanal"] if sub == "Sonstiges" else ["Bauch"]
        col.add_note(note, did)

today = A.today(col)
plan = {"id": "p1", "title": "Bauch", "exam": (today + timedelta(days=9)).isoformat(), "start": today.isoformat(),
        "minutesPerDay": 120, "offWeekdays": [], "dayMinutes": {}, "order": "auto", "done": {}, "days": [],
        "sources": [{"id": "ab", "type": "anki", "name": "Bauch", "deck": "SEKU::Bauch", "minPerUnit": 1, "maxNew": 10}],
        "topics": [{"id": "t1", "name": "Leber", "anki": {}}, {"id": "t2", "name": "Peritoneum", "anki": {}},
                   {"id": "t3", "name": "Leistenkanal", "anki": {}}]}

print("decks", A.deck_names(col))
info = A.deck_info(col, "SEKU::Bauch")
assert info["new"] == 25 and sorted(info["children"]) == ["Leber", "Peritoneum", "Sonstiges"], info
cands = {"ab": A.candidates(col, "SEKU::Bauch")}
assert any(c["query"] == 'tag:"Leistenkanal"' for c in cands["ab"]), cands
P.apply_suggestions(plan, P.suggest(plan, cands))
assert plan["topics"][0]["anki"]["ab"] == 'deck:"SEKU::Bauch::Leber"', plan["topics"]
assert plan["topics"][2]["anki"]["ab"] == 'tag:"Leistenkanal"', plan["topics"]

st = A.stats(col, plan)
assert st["counts"][P.rest_query(plan, plan["sources"][0])]["new"] == 0  # alles ist einem Thema zugeordnet
P.build(plan, st["counts"], today, P.evaluate(plan, st))
cards_items = [it for d in plan["days"] for it in d["items"] if it["kind"] == "cards"]
assert sum(it["cards"] for it in cards_items) == 25, cards_items

# 10 Leber-Karten lernen, davon 4 mal "Nochmal"
col.decks.select(col.decks.id_for_name("SEKU::Bauch::Leber"))
col.sched.extend_limits(0, 0)
answered = 0
for i in range(10):
    c = col.sched.getCard()
    if not c:
        break
    col.sched.answerCard(c, 1 if i < 4 else 3)
    answered += 1
for _ in range(8):  # die Nochmal-Karten noch einmal falsch
    c = col.sched.getCard()
    if not c:
        break
    col.sched.answerCard(c, 1)
st = A.stats(col, plan)
ev = P.evaluate(plan, st)
print("rated", st["rated"], "due", st["due"])
assert st["rated"][today.isoformat()] >= 10
first = next(it for it in cards_items if "Leber" in it["text"])
assert ev[first["id"]]["done"] or ev[first["id"]]["text"].startswith(str(min(first["cards"], 10))), (first, ev[first["id"]])

w = A.weak(col, plan)
assert w and w[0]["name"] == "Leber" and w[0]["agains"] >= 4, w
items = P.weak_items(plan, w)
assert "Leber" in items[0]["text"]

did, n = A.weak_deck(col, plan)
print("weak deck", n)
did2, n2, cids = A.sim_deck(col, plan, 5)
assert n2 <= 5
did3, n3 = A.ahead_deck(col, plan)
print("ahead", n3, "sim", n2)
col.sched.empty_filtered_deck(did2)
ts = A.time_stats(col, plan)
assert ts["newCards"] >= answered, ts
assert A.activity(col)[today.isoformat()] >= 10
fc = A.forecast(col, plan)
assert sum(fc["due"].values()) >= 10 and fc["min"] > 0, fc
P.build(plan, A.stats(col, plan)["counts"], today, forecast=fc)

conf_before = col.decks.get(col.decks.id_for_name("SEKU::Bauch::Leber"))["conf"]
A.maintenance(col, plan, True)
d = col.decks.get(col.decks.id_for_name("SEKU::Bauch::Leber"))
assert d["conf"] != conf_before and col.decks.config_dict_for_deck_id(d["id"])["new"]["perDay"] == 0
A.maintenance(col, plan, False)
assert col.decks.get(col.decks.id_for_name("SEKU::Bauch::Leber"))["conf"] == conf_before
col.close()
print("ANKIDATA OK")

# „▶ lernen“: einzelnes Unterdeck direkt, sonst gefiltertes Deck
col = Collection(path)
P.build(plan, A.stats(col, plan)["counts"], A.today(col))
items = [it for d in plan["days"] for it in d["items"]]
card_it = next(it for it in items if it["kind"] == "cards" and it.get("topic") == "t2")
did, n = A.study_target(col, plan, card_it)
assert did == col.decks.id_for_name("SEKU::Bauch::Peritoneum") and n is None, (did, n)
tag_it = next((it for it in items if it["kind"] == "cards" and it.get("topic") == "t3"), None)
if tag_it:
    did, n = A.study_target(col, plan, tag_it)
    assert col.decks.is_filtered(did) and n > 0, (did, n)
rev = next(it for it in items if it["kind"] == "reviews")
did, n = A.study_target(col, plan, rev)
assert did == col.decks.id_for_name("SEKU::Bauch")
col.close()
print("STUDY OK")
