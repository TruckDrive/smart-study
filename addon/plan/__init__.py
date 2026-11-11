# Smart Study study plan: plans up to the exam from books, videos, tasks and Anki decks.
# Open it via Tools → Smart Study → Study Plan or the "Study Plan" link in the top bar.
# The plan checks off Anki items by itself; everything else with a click.
import copy
import json
import os
import shutil
import subprocess
import time
import traceback

from anki.lang import current_lang
from aqt import dialogs, gui_hooks, mw
from aqt.qt import QApplication, QDesktopServices, QDialog, QFileDialog, QMessageBox, QTimer, QUrl, QVBoxLayout, Qt
from aqt.utils import openLink, restoreGeom, saveGeom
from aqt.webview import AnkiWebView

from . import ankidata, files, planner, share, store
from .planner import tr
from ..constants import ADDON_VERSION as VERSION
from ..locales import _current_lang

NAME = "Smart Study"
MODULE = __name__
FOLDER = MODULE.split(".")[0]


def _sync_lang():
    """Follows the add-on's language setting, which is only loaded at profile open."""
    if _current_lang() == "fa":
        planner.LANG = "fa"
    else:
        planner.LANG = "de" if (current_lang or "").startswith("de") else "en"


_sync_lang()


def today():
    return ankidata.today(mw.col)


def _item(plan, iid):
    """An item of the plan by id; a clear message if it is gone (e.g. after replanning on another device)."""
    for _, it in planner.all_items(plan):
        if it["id"] == iid:
            return it
    raise ValueError(tr("Diesen Punkt gibt es nicht mehr – der Plan wurde inzwischen geändert.",
                        "This item no longer exists – the plan has changed in the meantime.",
                        "این مورد دیگر وجود ندارد – برنامه در این فاصله تغییر کرده است."))


def view(pid, st=None):
    """Everything the page needs for one plan. st: Anki numbers that were already
    collected in the background (otherwise they are collected now)."""
    plan = store.load(pid)
    if st is None:
        st = ankidata.stats(mw.col, plan)
    ev = planner.evaluate(plan, st)
    t = st["today"]
    now = time.strftime("%Y-%m-%dT%H:%M")
    changed = False
    for iid, r in ev.items():  # remember when Anki finished an item (for the retrospective)
        if r["done"] and iid not in plan.setdefault("autoDone", {}):
            plan["autoDone"][iid] = now
            changed = True
    if changed:
        store.save(plan)
    done, tot = planner.progress(plan, ev)
    phase = "after" if plan["exam"] and t > plan["exam"] else ("early" if tot and done == tot else "active")
    if not plan.get("days") or not plan["exam"]:
        phase = "setup"
    out = {"plan": plan, "ev": ev, "stats": {k: st[k] for k in ("today", "due", "decks")},
           "progress": [done, tot], "overdue": planner.overdue(plan, ev, t), "phase": phase}
    out["files"] = {s["id"]: files.known(plan, s) for s in plan.get("sources", []) if s.get("type") == "pages"}
    out["profile"] = store.profile()
    return out


def open_pdf(path, page):
    """Open a PDF at a page: Okular/Evince can jump there directly, otherwise the default app."""
    path = os.path.expanduser(path)
    if not os.path.isfile(path):
        raise ValueError(tr("PDF nicht gefunden – unter Bearbeiten → Quellen die Datei wählen.",
                            "PDF not found – choose the file under Edit → Sources.",
                            "فایل PDF پیدا نشد – از ویرایش ← منابع فایل را انتخاب کنید."))
    page = max(1, page)
    try:  # first choice: a tab of the Smart Study browser, at that page
        from .. import browser_features
        if browser_features.open_plan_pdf(path, page):
            return {"ok": True, "page": page, "browser": True}
    except Exception:
        traceback.print_exc()
    for prog, args in (("okular", ["-p", str(page)]), ("evince", ["-i", str(page)])):
        if shutil.which(prog):
            subprocess.Popen([prog, *args, path], start_new_session=True,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return {"ok": True, "page": page}
    QDesktopServices.openUrl(QUrl.fromLocalFile(path))
    return {"ok": True, "page": page, "noPage": True}


def ask_for_pdf(plan, src):
    """The PDF is not on this device where it was, and the search found nothing:
    ask where it is, remember the answer here and keep it for the other devices."""
    name = src.get("fileName") or files.base_name(src.get("file")) or src.get("name") or "PDF"
    start = os.path.dirname(os.path.expanduser(src.get("file") or ""))
    if not os.path.isdir(start):
        start = os.path.expanduser("~")
    path, _ = QFileDialog.getOpenFileName(
        _win, tr(f"Wo hast du „{name}“ gespeichert?", f"Where did you save “{name}”?", f"«{name}» را کجا ذخیره کرده‌اید؟"),
        start, tr("PDF (*.pdf);;Alle Dateien (*)", "PDF (*.pdf);;All files (*)", "PDF (*.pdf);;همهٔ فایل‌ها (*)"))
    if not path:
        return ""
    files.remember(plan["id"], src["id"], path)
    src["file"] = path
    files.describe(src, path)
    store.save(plan)
    return path


def _today_load(plan, ev, t):
    """[done, total, open minutes] of today's checkable items – for the overview."""
    done = tot = mins = 0
    for day in plan.get("days", []):
        if day["d"] != t:
            continue
        for it in day["items"]:
            if it.get("kind") in planner.NO_CHECK or it.get("moved"):
                continue
            tot += 1
            if planner.is_done(plan, it, ev):
                done += 1
            else:
                mins += it.get("min", 0) or 0
    return [done, tot, mins]


def home(stats=None, act=None):
    """The overview. stats {plan id: Anki numbers} and act (ratings per day) may
    come from the background; whatever is missing is collected now."""
    t = today().isoformat()
    plans = []
    active = set()
    for p in store.list_plans():
        ev = {}
        if p.get("status") == "active":
            try:
                st = (stats or {}).get(p["id"]) or ankidata.stats(mw.col, p)
                ev = planner.evaluate(p, st)
            except Exception:  # one broken plan must not hide all the others
                traceback.print_exc()
        plans.append({"id": p["id"], "title": p["title"], "exam": p["exam"], "status": p.get("status", "active"),
                      "progress": planner.progress(p, ev), "start": p["start"], "today": _today_load(p, ev, t),
                      "draft": not p.get("days")})
        for ts in list(p.get("done", {}).values()) + list(p.get("autoDone", {}).values()):
            if isinstance(ts, str):
                active.add(ts[:10])
    if act is None:
        act = ankidata.activity(mw.col)
    heat = dict(act)
    for d in active:
        heat[d] = heat.get(d, 0) + 1
    plans.sort(key=lambda p: (p["status"] != "active", (p["exam"] or "9999") if p["status"] == "active" else "~" + p["exam"]))
    return {"plans": plans, "today": t, "heat": heat, "streak": planner.streak(set(heat), t),
            "profile": store.profile(), "version": VERSION, "name": NAME}


def generate_all(pid):
    """Replans all running plans because they share the study time: the nearest
    exam first, every further plan gets what is still free on that day.
    Returns the notes of the requested plan."""
    t = today()
    budget = store.profile().get("budget")
    if not store.load(pid).get("exam"):
        raise ValueError(tr("Bitte zuerst das Prüfungsdatum eintragen.", "Please enter the exam date first.",
                            "لطفاً ابتدا تاریخ امتحان را وارد کنید."))
    plans = [p for p in store.list_plans() if p["id"] == pid or (
        p.get("status") == "active" and p.get("days") and p.get("exam") and p["exam"] >= t.isoformat())]
    plans.sort(key=lambda p: (p["exam"], p["id"]))
    taken, notes = {}, []
    for plan in plans:
        try:
            st = ankidata.stats(mw.col, plan)
            n = planner.build(plan, st["counts"], t, planner.evaluate(plan, st),
                              forecast=ankidata.forecast(mw.col, plan), taken=taken, budget=budget)
        except Exception:
            if plan["id"] == pid:
                raise
            traceback.print_exc()  # another plan is broken: the requested one is still planned
            continue
        store.save(plan)
        for d, m in planner.day_load(plan, t).items():
            taken[d] = taken.get(d, 0) + m
        if plan["id"] == pid:
            notes = n
    return notes


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
    if cmd == "findDecks":
        return ankidata.find_decks(col, a.get("title", ""), a.get("q", ""), a.get("exclude") or ())
    if cmd == "deckInfo":
        return ankidata.deck_info(col, a["deck"])
    if cmd == "create":
        prof = store.profile()
        if a.get("from"):  # next plan with the source types of the old one
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
                    ns["decks"], ns["maxNew"] = [], s.get("maxNew")
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
        files.update_sources(plan)
        store.save(plan)
        return True
    if cmd == "generate":
        return {"notes": generate_all(a["id"])}
    if cmd == "toggle":
        plan = store.load(a["id"])
        _item(plan, a["item"])
        if a["on"]:
            plan.setdefault("done", {})[a["item"]] = time.strftime("%Y-%m-%dT%H:%M")
        else:
            plan.get("done", {}).pop(a["item"], None)
        store.save(plan)
        return True
    if cmd == "addCustom":
        plan = store.load(a["id"])
        planner.s2d(a["day"])  # refuses anything that is not a date
        text = " ".join(str(a.get("text", "")).split())[:500]
        if not text:
            return None
        mins, text = planner.split_minutes(text)
        day = next((d for d in plan["days"] if d["d"] == a["day"]), None)
        if not day:
            day = {"d": a["day"], "items": []}
            plan["days"].append(day)
            plan["days"].sort(key=lambda d: d["d"])
        it = {"id": planner.new_id(), "kind": "custom", "custom": True, "text": text,
              "min": max(0, min(24 * 60, int(a.get("min") or mins or 0)))}
        day["items"].append(it)
        store.save(plan)
        return it["id"]
    if cmd == "delItem":
        plan = store.load(a["id"])
        gone = None
        for d in plan["days"]:
            for ix, it in enumerate(d["items"]):
                if it["id"] == a["item"] and (it.get("custom") or it.get("kind") == "weak"):
                    gone = {"day": d["d"], "index": ix, "item": it, "done": plan.get("done", {}).pop(it["id"], None)}
            d["items"] = [it for it in d["items"] if not (gone and it is gone["item"])]
        if gone:
            store.save(plan)
        return gone
    if cmd == "restoreItem":  # undo of delItem
        plan = store.load(a["id"])
        g = a["gone"]
        it = g["item"]
        if not isinstance(it, dict) or not (it.get("custom") or it.get("kind") == "weak"):
            raise ValueError("only removed items can be restored")
        if any(i["id"] == it.get("id") for _, i in planner.all_items(plan)):
            return True
        planner.s2d(g["day"])
        day = next((d for d in plan["days"] if d["d"] == g["day"]), None)
        if not day:
            day = {"d": g["day"], "items": []}
            plan["days"].append(day)
            plan["days"].sort(key=lambda d: d["d"])
        day["items"].insert(max(0, min(len(day["items"]), int(g.get("index") or 0))), it)
        if g.get("done"):
            plan.setdefault("done", {})[it["id"]] = g["done"]
        store.save(plan)
        return True
    if cmd == "moveItem":  # a custom item to another day
        plan = store.load(a["id"])
        planner.s2d(a["day"])
        it = _item(plan, a["item"])
        if not it.get("custom"):
            raise ValueError("only custom items can be moved")
        for d in plan["days"]:
            d["items"] = [i for i in d["items"] if i is not it]
        day = next((d for d in plan["days"] if d["d"] == a["day"]), None)
        if not day:
            day = {"d": a["day"], "items": []}
            plan["days"].append(day)
            plan["days"].sort(key=lambda d: d["d"])
        day["items"].append(it)
        store.save(plan)
        return True
    if cmd == "simResult":
        plan = store.load(a["id"])
        return ankidata.sim_result(col, plan, plan.get("sim") or {})
    if cmd == "candidates":
        plan = a["plan"]
        return {s["id"]: ankidata.candidates(col, planner.src_decks(s)) for s in planner.anki_sources(plan)
                if planner.src_decks(s)}
    if cmd == "suggest":
        plan = a["plan"]
        cands = {s["id"]: ankidata.candidates(col, planner.src_decks(s)) for s in planner.anki_sources(plan)
                if planner.src_decks(s)}
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
    if cmd == "weakBrowse":
        plan = store.load(a["id"])
        search = ankidata.weak_search(col, plan, a.get("topics"))
        if not search:
            return {"ok": False}
        browser = dialogs.open("Browser", mw)
        browser.search_for(search)
        return {"ok": True}
    if cmd == "mockStart":
        plan = store.load(a["id"])
        cards = ankidata.mock_cards(col, plan, max(1, min(500, int(a.get("n") or 50))))
        minutes = max(1, min(600, int(a.get("minutes") or 30)))
        if not cards:
            return {"cards": [], "minutes": minutes}
        plan["sim"] = {"started": int(time.time() * 1000), "cards": [c["cid"] for c in cards], "answers": {}, "minutes": minutes}
        store.save(plan)
        return {"cards": cards, "minutes": minutes}
    if cmd == "mockAnswer":
        plan = store.load(a["id"])
        sim = plan.get("sim") or {}
        if not sim.get("started"):
            raise ValueError(tr("Die Probeprüfung läuft nicht mehr.", "The mock exam is no longer running.",
                                "امتحان آزمایشی دیگر در جریان نیست."))
        sim.setdefault("answers", {})[str(int(a["cid"]))] = bool(a["ok"])
        store.save(plan)
        return True
    if cmd == "openLink":
        if not str(a["url"]).startswith(("http://", "https://", "file://")):
            raise ValueError(tr("nur Web-Links oder Dateien", "only web links or files", "فقط لینک وب یا فایل"))
        if a.get("id") and a.get("item") and str(a["url"]).startswith(("http://", "https://")):
            from .. import browser_features
            if browser_features.open_plan_video(a["url"], a["id"], a["item"]):
                return True
        openLink(a["url"])
        return True
    if cmd == "studyItem":
        plan = store.load(a["id"])
        it = _item(plan, a["item"])
        did, n = ankidata.study_target(col, plan, it)
        if not did:
            return {"ok": False}
        mw.reset()
        a = {"did": did}
        cmd = "study"
    if cmd == "openPages":
        plan = store.load(a["id"])
        it = _item(plan, a["item"])
        src = next((s for s in plan["sources"] if s["id"] == it.get("source")), None)
        if not src or not it.get("pages"):
            raise ValueError(tr("Zu diesem Punkt gehört keine PDF-Quelle mehr.", "This item no longer has a PDF source.",
                                "این مورد دیگر منبع PDF ندارد."))
        path = files.resolve(plan, src)
        if not path:
            path = ask_for_pdf(plan, src)
            if not path:
                return {"ok": False, "cancelled": True}
        return open_pdf(path, int(it["pages"][0]) + int(src.get("pageOffset") or 0))
    if cmd == "pickFile":
        path, _ = QFileDialog.getOpenFileName(_win, tr("Datei wählen", "Choose file", "انتخاب فایل"), os.path.expanduser("~"),
                                              tr("PDF (*.pdf);;Alle Dateien (*)", "PDF (*.pdf);;All files (*)", "PDF (*.pdf);;همهٔ فایل‌ها (*)"))
        return path or None
    if cmd == "study":
        col.decks.select(a["did"])
        mw.moveToState("overview")
        mw.activateWindow()
        mw.raise_()
        return True
    if cmd == "mockStop":
        plan = store.load(a["id"])
        sim = plan.get("sim") or {}
        if not sim.get("started"):
            return sim.get("result")
        res = ankidata.sim_result(col, plan, sim)
        sim["result"] = res
        if res and res.get("answered"):
            plan.setdefault("simHistory", []).append({"at": today().isoformat(), "result": res})
        sim["started"] = None
        plan["sim"] = sim
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
            if k in planner.DEFAULT_RATES and v and float(v) > 0:
                prof["rates"][k] = float(v)
        if a.get("minutesPerDay") and int(a["minutesPerDay"]) > 0:
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
    if cmd == "shareCode":
        return {"code": share.encode(share.export_plan(store.load(a["id"])))}
    if cmd == "copyText":
        QApplication.clipboard().setText(str(a.get("text", ""))[:500000])
        return True
    if cmd == "exportFile":
        plan = store.load(a["id"])
        start = os.path.join(os.path.expanduser("~"), share.file_name(plan["title"]))
        path, _ = QFileDialog.getSaveFileName(_win, tr("Plan als Datei speichern", "Save plan as file", "ذخیرهٔ برنامه به‌صورت فایل"),
                                              start, tr("Smart-Study-Plan (*.json)", "Smart Study plan (*.json)", "برنامهٔ Smart Study (*.json)"))
        if not path:
            return None
        with open(path, "w", encoding="utf-8") as f:
            json.dump(share.export_plan(plan), f, ensure_ascii=False, indent=1)
        return path
    if cmd in ("importCode", "importFile"):
        if cmd == "importFile":
            path, _ = QFileDialog.getOpenFileName(_win, tr("Plan importieren", "Import plan", "وارد کردن برنامه"), os.path.expanduser("~"),
                                                  tr("Smart-Study-Plan (*.json);;Alle Dateien (*)", "Smart Study plan (*.json);;All files (*)",
                                                     "برنامهٔ Smart Study (*.json);;همهٔ فایل‌ها (*)"))
            if not path:
                return None
            if os.path.getsize(path) > share.MAX_BYTES:
                raise ValueError(tr("Die Datei ist zu groß.", "The file is too large.", "فایل بیش از حد بزرگ است."))
            with open(path, encoding="utf-8-sig", errors="replace") as f:
                text = f.read()
        else:
            text = a.get("text", "")
        try:
            data = share.decode(text)
            t = today().isoformat()
            plan = share.import_plan(data, store.new_plan("", "", t, store.profile()))
        except share.ShareError as e:
            raise ValueError({
                "newer version": tr("Dieser Plan kommt aus einer neueren Smart-Study-Version – bitte Add-on aktualisieren.",
                                    "This plan comes from a newer Smart Study version – please update the add-on.",
                                    "این برنامه از نسخهٔ جدیدتر Smart Study است – لطفاً افزونه را به‌روز کنید."),
                "too large": tr("Der Plan ist zu groß.", "The plan is too large.", "برنامه بیش از حد بزرگ است."),
            }.get(str(e), tr("Das ist kein gültiger Smart-Study-Plan (Code unvollständig kopiert?).",
                             "This is not a valid Smart Study plan (code copied incompletely?).",
                             "این یک برنامهٔ معتبر Smart Study نیست (شاید کد کامل کپی نشده است؟).")))
        if not plan.get("start"):
            plan["start"] = t
        store.save(plan)
        missing = [d for s in planner.anki_sources(plan) for d in planner.src_decks(s) if d not in set(ankidata.deck_names(col))]
        return {"id": plan["id"], "title": plan["title"], "pdfs": sum(1 for s in plan["sources"] if s["type"] == "pages"),
                "missingDecks": missing[:10]}
    if cmd == "maintenance":
        plan = store.load(a["id"])
        plan.setdefault("maintenance", {})["reviewsPerDay"] = int(a.get("reviewsPerDay") or 50)
        m = ankidata.maintenance(col, plan, a["on"])
        store.save(plan)
        mw.reset()
        return m
    raise ValueError(f"unknown command {cmd}")


class StudyPlanWindow(QDialog):
    # Defaults on the class: Qt already sends events while __init__ is still running.
    current = None  # plan the page shows; None = overview
    _showing = "home"
    _busy = _stale = _close_checked = _close_asking = False

    def __init__(self):
        _sync_lang()
        super().__init__(None, Qt.WindowType.Window)
        self.setWindowTitle(NAME)
        self.setMinimumSize(420, 500)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self.web = AnkiWebView(self, title="lernplan")
        self.web.set_bridge_command(self.on_bridge, self)
        lay.addWidget(self.web)
        restoreGeom(self, "lernplan", default_size=(980, 860))
        base = f"/_addons/{FOLDER}/plan/web/"
        skeleton = ('<div class="skel" style="height:54px;width:55%"></div><div class="skel" style="height:64px"></div>'
                    '<div class="skel" style="height:110px"></div><div class="skel" style="height:86px"></div>')
        self.web.stdHtml(f'<div id="app" data-lang="{planner.LANG}">{skeleton}</div>', css=[base + "lernplan.css"],
                         js=[base + "lernplan.js"], context=self)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._refresh)

    def on_bridge(self, msg):
        if not msg.startswith("lp:"):
            return None
        try:
            data = json.loads(msg[3:])
            cmd, args = data["cmd"], data.get("args") or {}
            if not mw.col:
                raise ValueError(tr("Die Sammlung ist gerade nicht geöffnet.", "The collection is not open right now.",
                                    "مجموعه در حال حاضر باز نیست."))
            out = handle(cmd, args)
            if cmd in ("open", "home", "review"):
                self._showing = cmd
                self.current = args.get("id") if cmd != "home" else None
            return {"ok": True, "data": out}
        except Exception as e:
            traceback.print_exc()
            return {"ok": False, "error": str(e) or type(e).__name__}

    def refresh_soon(self):
        """Anki changed something. While the window is minimised nothing is computed;
        it catches up as soon as it is shown again."""
        if self.isMinimized() or not self.isVisible():
            self._stale = True
            return
        self._timer.start(1500)

    def changeEvent(self, evt):
        super().changeEvent(evt)
        if self._stale and not self.isMinimized() and self.isVisible():
            self._stale = False
            self._timer.start(150)

    def _refresh(self):
        """Collects the Anki numbers in the background, so reviewing never stutters
        because of the plan window, and hands the finished data to the page."""
        if not mw.col or self._showing == "review":
            return
        if self._busy:
            self._stale = True
            return
        pid, showing = self.current, self._showing
        try:
            plans = [store.load(pid)] if pid else [p for p in store.list_plans() if p.get("status") == "active"]
        except FileNotFoundError:
            return
        except Exception:
            traceback.print_exc()
            return
        snap = copy.deepcopy(plans)  # the background thread reads only its own copy
        stamps = {p["id"]: p.get("savedAt") for p in plans}

        def collect(col):
            return ({p["id"]: ankidata.stats(col, p) for p in snap}, None if pid else ankidata.activity(col))

        def done(res):
            self._busy = False
            try:
                if not mw.col or not self.isVisible() or (self.current, self._showing) != (pid, showing):
                    return
                stats, act = res
                if pid:
                    if store.load(pid).get("savedAt") != stamps[pid]:
                        return self._timer.start(300)  # the plan changed meanwhile: count again
                    data = view(pid, st=stats[pid])
                else:
                    data = home(stats=stats, act=act)
                self.web.eval(f"window.LP && LP.push({json.dumps('plan' if pid else 'home')}, {json.dumps(data)})")
            except RuntimeError:  # window closed meanwhile
                pass
            except Exception:
                traceback.print_exc()
            finally:
                if self._stale and not self._busy:
                    self._stale = False
                    self.refresh_soon()

        def failed(exc):
            self._busy = False
            print("Smart Study: refresh failed:", exc)

        try:
            from aqt.operations import QueryOp
            self._busy = True
            QueryOp(parent=self, op=collect, success=done).failure(failed).run_in_background()
        except Exception:  # very old Anki: ask the page to fetch the data itself
            self._busy = False
            traceback.print_exc()
            self.web.eval("window.LP && LP.refresh()")

    def keyPressEvent(self, evt):
        if evt.key() == Qt.Key.Key_Escape:  # Esc belongs to the page (dialogs, fields), it must not close the window
            evt.accept()
            return
        super().keyPressEvent(evt)

    def reject(self):
        self.close()

    def closeEvent(self, evt):
        """Asks before unsaved edits of a plan are lost."""
        if self._close_checked or not mw.col:
            saveGeom(self, "lernplan")
            evt.accept()
            QDialog.reject(self)  # hides and emits finished → _closed()
            return
        evt.ignore()
        if self._close_asking:
            return
        self._close_asking = True
        answered = []

        def go(edit):
            if answered:
                return
            answered.append(True)
            self._close_asking = False
            if isinstance(edit, dict) and edit.get("id"):
                box = QMessageBox(self)
                box.setWindowTitle(NAME)
                box.setIcon(QMessageBox.Icon.Question)
                box.setText(tr("Du hast diesen Plan bearbeitet, aber noch nicht gespeichert.",
                               "You have edited this plan but not saved it yet.",
                               "این برنامه را ویرایش کرده‌اید اما هنوز ذخیره نکرده‌اید."))
                save = box.addButton(tr("Speichern", "Save", "ذخیره"), QMessageBox.ButtonRole.AcceptRole)
                drop = box.addButton(tr("Verwerfen", "Discard", "دور ریختن"), QMessageBox.ButtonRole.DestructiveRole)
                box.addButton(tr("Weiter bearbeiten", "Keep editing", "ادامهٔ ویرایش"), QMessageBox.ButtonRole.RejectRole)
                box.exec()
                if box.clickedButton() is save:
                    try:
                        handle("savePlan", {"plan": edit})
                    except Exception as e:
                        traceback.print_exc()
                        QMessageBox.warning(self, NAME, str(e))
                        return
                elif box.clickedButton() is not drop:
                    return
            self._close_checked = True
            self.close()

        try:
            self.web.evalWithCallback("window.LP && LP.dirty ? LP.dirty() : null", go)
            QTimer.singleShot(1500, lambda: go(None))  # a page that does not answer must not keep the window open
        except Exception:
            go(None)


_win = None


def open_window():
    global _win
    if not mw.col:
        return
    if _win is None or not _win.isVisible():
        _win = StudyPlanWindow()
        _win.finished.connect(_closed)
    if _win.isMinimized():
        _win.showNormal()
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
    try:
        if _win is not None and _win.isVisible():
            _win.refresh_soon()
    except RuntimeError:  # the window is already gone
        pass


def _toolbar(links, toolbar):
    _sync_lang()
    link = toolbar.create_link("lernplan", tr("Study Plan", "Study Plan", "برنامهٔ مطالعه"), open_window,
                               tip=tr(f"{NAME} öffnen", f"Open {NAME}", f"باز کردن {NAME}"), id="lernplan")
    # Anki adds "sync" before this hook runs; keep it as the rightmost link
    i = next((i for i, x in enumerate(links) if 'id="sync"' in x), len(links))
    links.insert(i, link)


def _profile_closing():
    if _win is not None:
        try:
            _win._close_checked = True  # no question while Anki is shutting down
            _win.close()
        except RuntimeError:
            pass


gui_hooks.top_toolbar_did_init_links.append(_toolbar)
gui_hooks.reviewer_did_answer_card.append(_changed)
gui_hooks.sync_did_finish.append(_changed)  # plans may have arrived from another device


def _store_plans(*_):
    """Puts plans that were written as files (e.g. by a script) into the collection, so the sync takes them along."""
    try:
        store.list_plans()
        store.profile()
    except Exception:
        traceback.print_exc()


gui_hooks.sync_will_start.append(_store_plans)


def _rename_legacy_decks(*_):
    """Old "Study Plan" / "Lernplan" filtered decks get one clear name (also after a sync)."""
    try:
        if mw.col and ankidata.rename_legacy_decks(mw.col) and mw.state == "deckBrowser":
            mw.deckBrowser.refresh()
    except Exception:
        traceback.print_exc()


gui_hooks.profile_did_open.append(_rename_legacy_decks)
gui_hooks.sync_did_finish.append(_rename_legacy_decks)
gui_hooks.profile_did_open.append(_store_plans)
gui_hooks.operation_did_execute.append(lambda changes, handler: _changed())
gui_hooks.profile_will_close.append(_profile_closing)
