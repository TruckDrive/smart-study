"""Sharing study plans: export, code, import of someone else's plan (no Anki needed)."""
import importlib.util
import json
import os
import sys
import types

ADDON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "addon", "plan")
spec = importlib.util.spec_from_file_location("share", os.path.join(ADDON, "share.py"))
share = importlib.util.module_from_spec(spec)
spec.loader.exec_module(share)

plan = {
    "id": "p123", "title": "Kopf-Hals-Testat", "exam": "2026-12-10", "examTime": "09:00", "start": "2026-11-05",
    "status": "active", "minutesPerDay": 200, "offWeekdays": [6], "dayMinutes": {"2026-11-08": 60},
    "dayNotes": {"2026-11-09": "Präpsaal"}, "order": "auto", "milestones": [],
    "sources": [
        {"id": "s1", "type": "pages", "name": "Skript", "file": "/home/me/Uni/skript.pdf", "pageOffset": 2},
        {"id": "s2", "type": "videos", "name": "Moodle", "videos": [{"title": "V1", "url": "https://moodle.example/v1"},
                                                                     {"title": "bad", "url": "file:///etc/passwd"}]},
        {"id": "s3", "type": "anki", "name": "AnKing", "decks": ["AnKing::Anatomie", 5]},
    ],
    "topics": [{"id": "t1", "name": "Hals"}],
    "days": [{"d": "2026-11-06", "items": [
        {"id": "i1", "kind": "pages", "source": "s1", "pages": [1, 10], "text": "Skript S. 1–10", "min": 60},
        {"id": "i2", "kind": "videos", "source": "s2", "text": "V1", "url": "https://moodle.example/v1"},
        {"id": "i3", "kind": "custom", "custom": True, "text": "Link", "url": "javascript:alert(1)"},
    ]}],
    "done": {"i1": "2026-11-06T10:00"}, "autoDone": {"x": "y"}, "sim": {"started": 1}, "review": {"grade": "1"},
    "savedAt": 123.0, "notes": ["intern"],
}

payload = share.export_plan(plan)
shared = payload["plan"]
assert payload["kind"] == "smart-study-plan" and payload["v"] == 1
for private in ("id", "done", "autoDone", "sim", "review", "savedAt", "notes", "status"):
    assert private not in shared, private
assert "file" not in shared["sources"][0] and shared["sources"][0]["pageOffset"] == 2
assert "file" in plan["sources"][0], "the own plan stays unchanged"

code = share.encode(payload)
assert code.startswith("SSP1:") and len(code) < 2000
message = "Hier mein Lernplan 📚\nSmart Study → Importieren:\n\n" + code + "\n\nViel Erfolg!"
assert share.decode(message) == payload
# Chat apps sometimes break long lines.
assert share.decode(code[:30] + "\n" + code[30:]) == payload
assert share.decode(json.dumps(payload)) == payload
assert share.decode("﻿" + json.dumps(payload)) == payload

for bad in ("", "hallo", "SSP1:abc", '{"kind": "other", "v": 1, "plan": {}}', "{kaputt",
            json.dumps({"kind": "smart-study-plan", "v": 99, "plan": {}})):
    try:
        share.decode(bad)
    except share.ShareError:
        pass
    else:
        raise AssertionError(bad)

# A zip bomb is refused.
import base64, zlib
bomb = "SSP1:" + base64.urlsafe_b64encode(zlib.compress(b'{"a":"' + b"x" * (share.MAX_BYTES + 10) + b'"}')).decode()
try:
    share.decode(bomb)
except share.ShareError as e:
    assert str(e) == "too large"
else:
    raise AssertionError("bomb")

base = {"id": "pNEW", "title": "", "exam": "", "examTime": "", "start": "2026-11-05", "status": "active",
        "minutesPerDay": 180, "offWeekdays": [], "dayMinutes": {}, "dayNotes": {}, "order": "auto", "milestones": [],
        "sources": [], "topics": [], "days": [], "done": {}, "autoDone": {}, "notes": []}
mine = share.import_plan(share.decode(code), base)
assert mine["id"] == "pNEW" and mine["title"] == "Kopf-Hals-Testat" and mine["exam"] == "2026-12-10"
assert mine["minutesPerDay"] == 200 and mine["done"] == {} and mine["status"] == "active"
assert mine["sources"][2]["decks"] == ["AnKing::Anatomie"]
assert [v["title"] for v in mine["sources"][1]["videos"]] == ["V1", "bad"]
assert "url" not in mine["sources"][1]["videos"][1], "only web links"
items = mine["days"][0]["items"]
assert items[1]["url"] == "https://moodle.example/v1" and "url" not in items[2]
assert mine["dayMinutes"] == {"2026-11-08": 60} and mine["dayNotes"] == {"2026-11-09": "Präpsaal"}

# Junk from a broken or hostile file does not get through.
junk = {"kind": "smart-study-plan", "v": 1, "plan": {
    "title": "X", "exam": "morgen", "minutesPerDay": "viel", "offWeekdays": [1, 9, "a"],
    "dayMinutes": {"2026-11-08": "abc", "x": 5}, "sources": [{"id": "../../evil", "type": "pages"}, {"id": "ok", "type": "nope"}, "s"],
    "days": [{"d": "2026-11-07", "items": [{"id": "a", "kind": "pages", "pages": "1-3", "text": "t"}, {"kind": "custom"}]},
             {"d": "kaputt", "items": []}, {"d": "2026-11-07", "items": []}],
}}
mine = share.import_plan(junk, base)
assert mine["exam"] == "" and mine["minutesPerDay"] == 180 and mine["offWeekdays"] == [1]
assert mine["dayMinutes"] == {} and mine["sources"] == []
assert len(mine["days"]) == 1 and mine["days"][0]["items"] == [{"id": "a", "kind": "custom", "text": "t"}]
try:
    share.import_plan({"kind": "smart-study-plan", "v": 1, "plan": {"title": "  "}}, base)
except share.ShareError:
    pass
else:
    raise AssertionError("plan without a name")

assert share.file_name('Kopf/Hals: "Testat"') == "KopfHals Testat.smartstudy.json"
assert share.file_name("") == "Plan.smartstudy.json"
# Short chat code (v2): no generated days, topic searches as deck index, empties dropped.
plan["sources"][2]["decks"] = ["AnKing::Anatomie", 'AnKing::"Kopf"']
plan["topics"] = [{"id": "t1", "name": "Hals", "pages": {}, "anki": {"s3": 'deck:"AnKing::\\"Kopf\\""'}},
                  {"id": "t2", "name": "Arm", "anki": {"s3": 'deck:"Andere"'}}]
short = share.export_plan(plan, short=True)
assert short["v"] == 2
assert short["plan"]["days"] == [{"d": "2026-11-06", "items": [
    {"id": "i3", "kind": "custom", "custom": True, "text": "Link", "url": "javascript:alert(1)"}]}], "only own items"
assert short["plan"]["topics"][0]["anki"] == {"s3": 1} and "pages" not in short["plan"]["topics"][0]
assert short["plan"]["topics"][1]["anki"] == {"s3": 'deck:"Andere"'}, "own searches stay"
code2 = share.encode(short)
assert len(code2) < len(share.encode(share.export_plan(plan)))
got = share.decode("Plan:\n" + code2 + " danke! ~ bis bald")
assert got == short, "text after the end mark is not part of the code"
mine = share.import_plan(got, base)
assert [t["anki"] for t in mine["topics"]] == [{"s3": 'deck:"AnKing::\\"Kopf\\""'}, {"s3": 'deck:"Andere"'}]
assert [it["id"] for d in mine["days"] for it in d["items"]] == ["i3"] and "url" not in mine["days"][0]["items"][0]
bad = json.loads(json.dumps(short))
bad["plan"]["topics"][0]["anki"] = {"s3": 7, "s9": 0, "s2": True}
assert share.import_plan(bad, base)["topics"][0]["anki"] == {}, "broken deck index is dropped"
# 3.0.0 only knows v1: it says "please update" instead of importing an empty plan.
share.VERSION = 1
try:
    share.decode(code2)
except share.ShareError as e:
    assert str(e) == "newer version"
else:
    raise AssertionError("old version must refuse v2")
share.VERSION = 2
print("share ok")
