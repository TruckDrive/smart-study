# Plans are stored as JSON in user_files/ (kept across add-on updates) and,
# while a collection is open, also in its config: AnkiWeb sync then carries them
# to your other devices. Of two copies of a plan, the newer one (savedAt) wins.
import json
import os
import re
import time
import traceback

from . import planner

DIR = os.path.join(os.path.dirname(__file__), "user_files")
PLANS = os.path.join(DIR, "plans")
PROFILE = os.path.join(DIR, "profile.json")
CONF_PLANS = "lernplan_plans"  # {plan id: plan}
CONF_DELETED = "lernplan_deleted"  # {plan id: time of deletion}, so other devices delete it too
CONF_PROFILE = "lernplan_profile"


def _write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def _read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _path(pid):
    if not re.fullmatch(r"[A-Za-z0-9_-]+", pid):
        raise ValueError("invalid plan id")
    return os.path.join(PLANS, pid + ".json")


def _col():
    try:
        from aqt import mw
    except ImportError:
        return None
    return mw.col if mw else None


def _get_conf(key):
    col = _col()
    if not col:
        return None
    try:
        return col.get_config(key, None)
    except Exception:
        traceback.print_exc()
        return None


def _set_conf(key, val):
    col = _col()
    if col:
        try:
            col.set_config(key, val)
        except Exception:
            traceback.print_exc()


def _stamp(x):
    return -1 if x is None else float(x.get("savedAt") or 0)


def _files():
    out = {}
    if os.path.isdir(PLANS):
        for f in sorted(os.listdir(PLANS)):
            if f.endswith(".json"):
                p = _read(os.path.join(PLANS, f))
                if p and p.get("id"):
                    out[p["id"]] = p
    return out


def _reconcile():
    """Brings files and collection in line and returns all plans {id: plan}."""
    files = _files()
    conf = _get_conf(CONF_PLANS)
    if conf is None and not _col():
        return files
    conf = dict(conf or {})
    deleted = _get_conf(CONF_DELETED) or {}
    out, changed = {}, False
    for pid in sorted(set(files) | set(conf)):
        f, c = files.get(pid), conf.get(pid)
        if pid in deleted and max(_stamp(f), _stamp(c)) <= float(deleted[pid]):
            if f:
                os.remove(_path(pid))
            if c:
                del conf[pid]
                changed = True
            continue
        if _stamp(f) > _stamp(c):
            conf[pid] = f
            changed = True
            out[pid] = f
        elif _stamp(c) > _stamp(f):
            _write(_path(pid), c)
            out[pid] = c
        else:
            out[pid] = f
    if changed:
        _set_conf(CONF_PLANS, conf)
    return out


def list_plans():
    return list(_reconcile().values())


def load(pid):
    plans = _reconcile()
    if pid not in plans:
        raise FileNotFoundError(f"plan {pid} not found")
    return plans[pid]


def save(plan):
    plan["savedAt"] = time.time()
    _write(_path(plan["id"]), plan)
    if _col():
        conf = dict(_get_conf(CONF_PLANS) or {})
        conf[plan["id"]] = plan
        _set_conf(CONF_PLANS, conf)


def delete(pid):
    if os.path.exists(_path(pid)):
        os.remove(_path(pid))
    if _col():
        conf = dict(_get_conf(CONF_PLANS) or {})
        conf.pop(pid, None)
        _set_conf(CONF_PLANS, conf)
        deleted = dict(_get_conf(CONF_DELETED) or {})
        deleted[pid] = time.time()
        _set_conf(CONF_DELETED, deleted)


def new_plan(title, exam, start, profile):
    return {
        "id": planner.new_id("p"), "title": title, "exam": exam, "examTime": "", "start": start,
        "status": "active", "minutesPerDay": int(profile.get("minutesPerDay", 180)), "offWeekdays": [],
        "dayMinutes": {}, "dayNotes": {}, "order": "auto", "milestones": [], "sources": [], "topics": [], "days": [],
        "done": {}, "autoDone": {}, "notes": [],
    }


def profile():
    f, c = _read(PROFILE), _get_conf(CONF_PROFILE)
    if _stamp(c) > _stamp(f):
        _write(PROFILE, c)
        p = c
    else:
        if f is not None and _col() and _stamp(f) > _stamp(c):
            _set_conf(CONF_PROFILE, f)
        p = f or {}
    p.setdefault("rates", dict(planner.DEFAULT_RATES))
    p.setdefault("history", [])
    return p


def save_profile(p):
    p["savedAt"] = time.time()
    _write(PROFILE, p)
    _set_conf(CONF_PROFILE, p)
