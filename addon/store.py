# Pläne liegen als JSON in user_files/ (bleibt bei Add-on-Updates erhalten).
import json
import os
import re

from . import planner

DIR = os.path.join(os.path.dirname(__file__), "user_files")
PLANS = os.path.join(DIR, "plans")
PROFILE = os.path.join(DIR, "profile.json")


def _write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def _path(pid):
    if not re.fullmatch(r"[A-Za-z0-9_-]+", pid):
        raise ValueError("ungültige Plan-ID")
    return os.path.join(PLANS, pid + ".json")


def list_plans():
    out = []
    if os.path.isdir(PLANS):
        for f in sorted(os.listdir(PLANS)):
            if f.endswith(".json"):
                try:
                    with open(os.path.join(PLANS, f), encoding="utf-8") as fh:
                        out.append(json.load(fh))
                except (OSError, ValueError):
                    pass
    return out


def load(pid):
    with open(_path(pid), encoding="utf-8") as f:
        return json.load(f)


def save(plan):
    _write(_path(plan["id"]), plan)


def delete(pid):
    os.remove(_path(pid))


def new_plan(title, exam, start, profile):
    return {
        "id": planner.new_id("p"), "title": title, "exam": exam, "examTime": "", "start": start,
        "status": "active", "minutesPerDay": int(profile.get("minutesPerDay", 180)), "offWeekdays": [],
        "dayMinutes": {}, "dayNotes": {}, "order": "auto", "milestones": [], "sources": [], "topics": [], "days": [],
        "done": {}, "autoDone": {}, "notes": [],
    }


def profile():
    try:
        with open(PROFILE, encoding="utf-8") as f:
            p = json.load(f)
    except (OSError, ValueError):
        p = {}
    p.setdefault("rates", dict(planner.DEFAULT_RATES))
    p.setdefault("history", [])
    return p


def save_profile(p):
    _write(PROFILE, p)
