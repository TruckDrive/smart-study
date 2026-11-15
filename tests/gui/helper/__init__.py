"""Helper add-on of the GUI smoke test (tests/gui/run.sh). Never install it by hand.

It drives the real add-on in a throwaway profile: main window, settings,
study plan, a review in focus mode. Every check prints "CHECK ok ..." or
"CHECK FAIL ..."; screenshots go to $SS_SHOTS. The run ends with "SMOKE DONE".
"""
import datetime
import importlib
import json
import os
import traceback

from aqt import gui_hooks, mw
from aqt.qt import QApplication, QTimer, QToolBar

OUT = os.environ.get("SS_SHOTS", ".")
ME = __name__.split(".")[0]
steps = []


def addon():
    return importlib.import_module(next(m for m in mw.addonManager.allAddons() if m != ME))


def check(ok, what):
    print(("CHECK ok   " if ok else "CHECK FAIL ") + what, flush=True)


def grab(widget, name):
    try:
        widget.grab().save(os.path.join(OUT, name + ".png"))
    except Exception:
        traceback.print_exc()


def later(ms, fn):
    def run():
        try:
            fn()
        except Exception:
            traceback.print_exc()
            print("CHECK FAIL the test step raised", flush=True)
            nxt()
    QTimer.singleShot(ms, run)


def nxt():
    if steps:
        later(300, steps.pop(0))
    else:
        print("SMOKE DONE", flush=True)
        QTimer.singleShot(300, lambda: os._exit(0))


def rail_visible():
    return [bar.isVisible() for bar in mw.findChildren(QToolBar, "SmartStudyRail")]


def step_main():
    mw.resize(1500, 950)
    def look():
        check(rail_visible() == [True], "the rail is shown on the home screen")
        check(mw.toolbarWeb.isVisible(), "Anki's top bar is shown on the home screen")
        grab(mw, "main")
        nxt()
    later(2500, look)


def step_settings():
    root = addon()
    web = importlib.import_module(root.__name__ + ".web_settings_dialog")
    errors = []
    original = web._SettingsPage.javaScriptConsoleMessage

    def spy(self, level, message, line, source):
        text = str(message)
        if text.startswith("SMARTSTUDY_SETTINGS:err") or "Uncaught" in text:
            errors.append(text[:300])
        return original(self, level, message, line, source)
    web._SettingsPage.javaScriptConsoleMessage = spy

    def dialog():
        return next((w for w in QApplication.topLevelWidgets()
                     if type(w).__name__ == "WebSettingsDialog" and w.isVisible()), None)

    probe = """(function(){
      function rows(id){var e=document.getElementById(id);return e?e.children.length:-1}
      var logo=document.getElementById('brandLogo');
      return JSON.stringify({
        logo: !!(logo && logo.src && logo.src.length > 30),
        swatches: document.querySelectorAll('.sw').length,
        browserRows: rows('browserVideoGroup') + rows('browserTabGroup'),
        changelog: document.querySelectorAll('.cl-items li').length,
        deckOverview: typeof renderDeckOverviewSettings === 'function',
        pages: document.querySelectorAll('section.page').length});})()"""
    save = """(function(){var sw=document.querySelector('.sw[data-key="forest"]'); if(sw) sw.click();
      document.getElementById('sidebar_visibility').value='focus_review'; save(); return !!sw;})()"""

    def look():
        d = dialog()
        check(d is not None, "the settings window opens")
        if d is None:
            return
        def seen(result):
            info = json.loads(result or "{}")
            check(info.get("logo"), "settings: the logo is shown")
            check(info.get("swatches", 0) >= 8, "settings: the accent colours are listed")
            check(info.get("browserRows", 0) >= 4, "settings: the Browser tab has its switches")
            check(info.get("changelog", 0) >= 3, "settings: the changelog has entries")
            check(info.get("deckOverview"), "settings: the page loaded its own script file")
            check(not errors, "settings: the page reported no error " + "; ".join(errors))
            grab(d, "settings")
            d._page.runJavaScript(save)
        d._page.runJavaScript(probe, seen)
    later(4000, look)
    root.show_settings_dialog()  # returns after Save closed the window
    check(root.addon_settings.get("active_color_theme") == "forest", "settings: Save stores a new accent colour")
    check(root.addon_settings.get("sidebar_visibility_mode") == "focus_review", "settings: Save stores the focus mode")
    nxt()


def step_plan():
    plan = importlib.import_module(addon().__name__ + ".plan")
    today = datetime.date.today()
    p = plan.handle("create", {"title": "Smoke test exam", "exam": str(today + datetime.timedelta(days=6)), "start": str(today)})
    p["sources"] = [{"id": "s2", "type": "tasks", "name": "Tasks", "minPerUnit": 20,
                     "tasks": [{"id": "a", "name": "Exercise sheet 1"}, {"id": "b", "name": "Exercise sheet 2"}]}]
    plan.handle("savePlan", {"plan": p})
    plan.handle("generate", {"id": p["id"]})
    plan.open_window()
    web = plan._win.web
    tick = "(function(){var c=document.querySelector('input[type=checkbox]'); if(c) c.click(); return !!c;})()"
    menu = "(function(){var b=document.querySelector('.more-btn'); if(!b) return -1; b.click(); return document.querySelectorAll('.more-list button').length;})()"

    def open_plan():
        web.eval(f"LP.go('plan', {json.dumps(p['id'])})")
        later(3500, lambda: web.evalWithCallback(tick, ticked))

    def ticked(found):
        check(bool(found), "study plan: today's item can be ticked")
        later(3000, lambda: web.evalWithCallback(menu, opened))

    def opened(count):
        check((count or 0) >= 3, "study plan: the menu still opens after the page refreshed")
        grab(plan._win, "plan")
        plan._win.close()
        nxt()
    later(3000, open_plan)


def step_review():
    col = mw.col
    note = col.new_note(col.models.by_name("Basic"))
    note["Front"], note["Back"] = "Smoke test question", "Smoke test answer"
    col.add_note(note, 1)
    mw.reset()
    col.decks.select(1)
    mw.moveToState("review")

    def reviewing():
        check(mw.state == "review", "a review starts")
        check(rail_visible() == [False], "focus mode: the rail is hidden while reviewing")
        check(not mw.toolbarWeb.isVisible(), "focus mode: Anki's top bar is hidden while reviewing")
        grab(mw, "review")
        mw.moveToState("deckBrowser")
        later(2000, back)

    def back():
        check(rail_visible() == [True], "focus mode: the rail is back after the review")
        check(mw.toolbarWeb.isVisible(), "focus mode: Anki's top bar is back after the review")
        nxt()
    later(3000, reviewing)


def start():
    steps.extend([step_main, step_settings, step_plan, step_review])
    later(int(os.environ.get("SS_WAIT", "7000")), nxt)


gui_hooks.main_window_did_init.append(start)
