# Lernplan: Lernpläne bis zur Prüfung aus Handbuch, Videos, Aufgaben und Anki-Decks.
# Öffnen über Extras → Lernplan oder den Link „Lernplan“ in der oberen Leiste.
# Anki-Punkte hakt der Plan selbst ab; alles andere per Klick.
import json
import time
import traceback

from aqt import gui_hooks, mw
from aqt.qt import QAction, QDialog, QTimer, QVBoxLayout, Qt
from aqt.utils import openLink, restoreGeom, saveGeom
from aqt.webview import AnkiWebView

from . import ankidata, planner, store

VERSION = "0.1.0"
MODULE = __name__
FOLDER = MODULE.split(".")[0]
mw.addonManager.setWebExports(MODULE, r"web/.*\.(js|css)")


def today():
    return ankidata.today(mw.col)


def view(pid):
    """Alles, was die Seite für einen Plan braucht."""
    plan = store.load(pid)
    st = ankidata.stats(mw.col, plan)
    ev = planner.evaluate(plan, st)
    t = st["today"]
    now = time.strftime("%Y-%m-%dT%H:%M")
    changed = False
    for iid, r in ev.items():  # Zeitpunkt merken, an dem Anki einen Punkt erledigt hat (für den Rückblick)
        if r["done"] and iid not in plan.setdefault("autoDone", {}):
            plan["autoDone"][iid] = now
            changed = True
    if changed:
        store.save(plan)
    done, tot = planner.progress(plan, ev)
    phase = "after" if t > plan["exam"] else ("early" if tot and done == tot else "active")
    if not plan.get("days"):
        phase = "setup"
    out = {"plan": plan, "ev": ev, "stats": {k: st[k] for k in ("today", "due", "decks")},
           "progress": [done, tot], "overdue": planner.overdue(plan, ev, t), "phase": phase}
    if plan.get("sim", {}).get("started"):
        out["simResult"] = ankidata.sim_result(mw.col, plan, plan["sim"])
    return out


def home():
    t = today().isoformat()
    plans = []
    active = set()
    for p in store.list_plans():
        ev = planner.evaluate(p, ankidata.stats(mw.col, p)) if p.get("status") == "active" else {}
        plans.append({"id": p["id"], "title": p["title"], "exam": p["exam"], "status": p.get("status", "active"),
                      "progress": planner.progress(p, ev), "start": p["start"]})
        for ts in list(p.get("done", {}).values()) + list(p.get("autoDone", {}).values()):
            active.add(ts[:10])
    act = ankidata.activity(mw.col)
    heat = dict(act)
    for d in active:
        heat[d] = heat.get(d, 0) + 1
    plans.sort(key=lambda p: (p["status"] != "active", p["exam"] if p["status"] == "active" else "~" + p["exam"]))
    return {"plans": plans, "today": t, "heat": heat, "streak": planner.streak(set(heat), t),
            "profile": store.profile(), "version": VERSION}


SETUP_KEYS = ("title", "exam", "examTime", "start", "minutesPerDay", "offWeekdays", "dayMinutes", "dayNotes",
              "order", "sources", "topics", "subtitle", "milestones")


def handle(cmd, a):
    col = mw.col
    if cmd == "home":
        return home()
    if cmd == "open":
        return view(a["id"])
    if cmd == "decks":
        return ankidata.deck_names(col)
    if cmd == "deckInfo":
        return ankidata.deck_info(col, a["deck"])
    if cmd == "create":
        prof = store.profile()
        if a.get("from"):  # nächster Plan mit den Quellen-Arten des alten
            old = store.load(a["from"])
            plan = store.new_plan(a["title"], a["exam"], a["start"], prof)
            plan["minutesPerDay"] = old.get("minutesPerDay", plan["minutesPerDay"])
            plan["offWeekdays"] = old.get("offWeekdays", [])
            for s in old.get("sources", []):
                ns = {"id": s["id"], "type": s["type"], "name": s["name"],
                      "minPerUnit": prof["rates"].get(s["type"], s.get("minPerUnit"))}
                if s["type"] == "videos":
                    ns["videos"], ns["defaultMin"] = [], s.get("defaultMin")
                if s["type"] == "tasks":
                    ns["tasks"] = []
                if s["type"] == "anki":
                    ns["deck"], ns["maxNew"] = "", s.get("maxNew")
                plan["sources"].append(ns)
        else:
            plan = store.new_plan(a["title"], a["exam"], a["start"], prof)
        store.save(plan)
        return plan
    if cmd == "savePlan":
        plan = store.load(a["plan"]["id"])
        for k in SETUP_KEYS:
            if k in a["plan"]:
                plan[k] = a["plan"][k]
        store.save(plan)
        return True
    if cmd == "generate":
        plan = store.load(a["id"])
        st = ankidata.stats(col, plan)
        notes = planner.build(plan, st["counts"], today(), planner.evaluate(plan, st))
        store.save(plan)
        return {"notes": notes}
    if cmd == "toggle":
        plan = store.load(a["id"])
        if a["on"]:
            plan.setdefault("done", {})[a["item"]] = time.strftime("%Y-%m-%dT%H:%M")
        else:
            plan.get("done", {}).pop(a["item"], None)
        store.save(plan)
        return True
    if cmd == "addCustom":
        plan = store.load(a["id"])
        day = next((d for d in plan["days"] if d["d"] == a["day"]), None)
        if not day:
            day = {"d": a["day"], "items": []}
            plan["days"].append(day)
            plan["days"].sort(key=lambda d: d["d"])
        day["items"].append({"id": planner.new_id(), "kind": "custom", "custom": True, "text": a["text"],
                             "min": int(a.get("min") or 0)})
        store.save(plan)
        return True
    if cmd == "delItem":
        plan = store.load(a["id"])
        for d in plan["days"]:
            d["items"] = [it for it in d["items"] if it["id"] != a["item"]]
        store.save(plan)
        return True
    if cmd == "candidates":
        plan = a["plan"]
        return {s["id"]: ankidata.candidates(col, s["deck"]) for s in planner.anki_sources(plan) if s.get("deck")}
    if cmd == "suggest":
        plan = a["plan"]
        cands = {s["id"]: ankidata.candidates(col, s["deck"]) for s in planner.anki_sources(plan) if s.get("deck")}
        sugg = planner.suggest(plan, cands)
        if a.get("apply"):
            n = planner.apply_suggestions(plan, sugg)
            return {"plan": plan, "changed": n}
        return sugg
    if cmd == "parseList":
        return planner.parse_list(a["text"])
    if cmd == "parseToc":
        return planner.parse_toc(a["text"])
    if cmd == "weak":
        plan = store.load(a["id"])
        w = ankidata.weak(col, plan)
        return {"weak": w, "items": planner.weak_items(plan, w)}
    if cmd == "addWeak":
        plan = store.load(a["id"])
        items = planner.weak_items(plan, ankidata.weak(col, plan))
        t = today().isoformat()
        target = next((d for d in plan["days"] if d["d"] >= t and any(i.get("kind") == "weakround" for i in d["items"])), None) \
            or next((d for d in plan["days"] if d["d"] == t), None)
        if not target:
            target = {"d": t, "items": []}
            plan["days"].append(target)
            plan["days"].sort(key=lambda d: d["d"])
        have = {i.get("topic") for i in target["items"] if i.get("kind") == "weak"}
        target["items"].extend(i for i in items if i["topic"] not in have)
        store.save(plan)
        return {"day": target["d"], "n": len(items)}
    if cmd == "filtered":
        plan = store.load(a["id"])
        if a["kind"] == "ahead":
            did, n = ankidata.ahead_deck(col, plan)
        elif a["kind"] == "weak":
            did, n = ankidata.weak_deck(col, plan, a.get("topics"))
        else:
            did, n, cids = ankidata.sim_deck(col, plan, int(a.get("n", 50)))
            plan["sim"] = {"started": int(time.time() * 1000), "cards": cids, "minutes": int(a.get("minutes", 30)),
                           "deck": did}
            store.save(plan)
        mw.reset()
        return {"did": did, "count": n}
    if cmd == "openLink":
        if not str(a["url"]).startswith(("http://", "https://")):
            raise ValueError("nur Web-Links")
        openLink(a["url"])
        return True
    if cmd == "study":
        col.decks.select(a["did"])
        mw.moveToState("overview")
        mw.activateWindow()
        mw.raise_()
        return True
    if cmd == "simStop":
        plan = store.load(a["id"])
        plan.setdefault("sim", {})["stopped"] = int(time.time() * 1000)
        res = ankidata.sim_result(col, plan, plan["sim"])
        plan["sim"]["result"] = res
        plan.setdefault("simHistory", []).append({"at": time.strftime("%Y-%m-%d"), "result": res})
        plan["sim"]["started"] = None
        store.save(plan)
        return res
    if cmd == "review":
        plan = store.load(a["id"])
        st = ankidata.stats(col, plan)
        ev = planner.evaluate(plan, st)
        return {"stats": planner.review_stats(plan, ev), "time": ankidata.time_stats(col, plan),
                "profile": store.profile(), "review": plan.get("review", {}), "maintenance": plan.get("maintenance", {}),
                "simHistory": plan.get("simHistory", [])}
    if cmd == "saveReview":
        plan = store.load(a["id"])
        plan["review"] = a["review"]
        prof = store.profile()
        for k, v in (a.get("rates") or {}).items():
            if v:
                prof["rates"][k] = float(v)
        if a.get("minutesPerDay"):
            prof["minutesPerDay"] = int(a["minutesPerDay"])
        prof["history"] = [h for h in prof["history"] if h.get("plan") != plan["id"]] + [
            {"plan": plan["id"], "title": plan["title"], "exam": plan["exam"], "rates": a.get("rates"),
             "grade": a["review"].get("grade")}]
        store.save_profile(prof)
        store.save(plan)
        return True
    if cmd == "archive":
        plan = store.load(a["id"])
        plan["status"] = "archived" if a["on"] else "active"
        store.save(plan)
        return True
    if cmd == "delete":
        store.delete(a["id"])
        return True
    if cmd == "maintenance":
        plan = store.load(a["id"])
        plan.setdefault("maintenance", {})["reviewsPerDay"] = int(a.get("reviewsPerDay") or 50)
        m = ankidata.maintenance(col, plan, a["on"])
        store.save(plan)
        mw.reset()
        return m
    raise ValueError(f"unbekannter Befehl {cmd}")


class LernplanWindow(QDialog):
    def __init__(self):
        super().__init__(None, Qt.WindowType.Window)
        self.setWindowTitle("Lernplan")
        self.setMinimumSize(420, 500)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self.web = AnkiWebView(self, title="lernplan")
        self.web.set_bridge_command(self.on_bridge, self)
        lay.addWidget(self.web)
        restoreGeom(self, "lernplan", default_size=(980, 860))
        base = f"/_addons/{FOLDER}/web/"
        self.web.stdHtml('<div id="app"></div>', css=[base + "lernplan.css"], js=[base + "lernplan.js"], context=self)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(lambda: self.web.eval("window.LP && LP.refresh()"))

    def on_bridge(self, msg):
        if not msg.startswith("lp:"):
            return None
        data = json.loads(msg[3:])
        try:
            return {"ok": True, "data": handle(data["cmd"], data.get("args") or {})}
        except Exception as e:
            traceback.print_exc()
            return {"ok": False, "error": str(e)}

    def refresh_soon(self):
        self._timer.start(1500)

    def reject(self):
        saveGeom(self, "lernplan")
        super().reject()

    def closeEvent(self, evt):
        saveGeom(self, "lernplan")
        super().closeEvent(evt)


_win = None


def open_window():
    global _win
    if not mw.col:
        return
    if _win is None or not _win.isVisible():
        _win = LernplanWindow()
        _win.finished.connect(_closed)
    _win.show()
    _win.raise_()
    _win.activateWindow()


def _closed(*_):
    global _win
    if _win:
        _win.web.cleanup()
        _win.deleteLater()
    _win = None


def _changed(*_):
    if _win is not None and _win.isVisible():
        _win.refresh_soon()


def _toolbar(links, toolbar):
    links.append(toolbar.create_link("lernplan", "Lernplan", open_window, tip="Lernplan öffnen", id="lernplan"))


def _profile_closing():
    if _win is not None:
        _win.close()


action = QAction("Lernplan…", mw)
action.triggered.connect(open_window)
mw.form.menuTools.addAction(action)
gui_hooks.top_toolbar_did_init_links.append(_toolbar)
gui_hooks.reviewer_did_answer_card.append(_changed)
gui_hooks.operation_did_execute.append(lambda changes, handler: _changed())
gui_hooks.profile_will_close.append(_profile_closing)
