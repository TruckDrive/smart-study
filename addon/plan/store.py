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
    """Atomic: the old file stays intact until the new one is completely on disk."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.flush()
        try:
            os.fsync(f.fileno())
        except OSError:
            pass
    os.replace(tmp, path)


def _read(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except OSError:
        return None
    except ValueError:
        _quarantine(path)
        return None
    return data if isinstance(data, dict) else None


def _quarantine(path):
    """A file that is no JSON anymore (power cut, full disk, hand edit) is put aside
    instead of being overwritten, so its content can still be rescued."""
    try:
        os.replace(path, f"{path}.broken-{time.strftime('%Y%m%d-%H%M%S')}")
    except OSError:
        pass


_LISTS = ("offWeekdays", "milestones", "sources", "topics", "days", "notes")
_DICTS = ("dayMinutes", "dayNotes", "done", "autoDone")


def normalize(plan):
    """Fills in whatever a plan from an older version, another device or a script
    may lack, so neither the planner nor the page stumbles over a missing field.
    Changes the plan in place and returns it."""
    for k in _LISTS:
        if not isinstance(plan.get(k), list):
            plan[k] = []
    for k in _DICTS:
        if not isinstance(plan.get(k), dict):
            plan[k] = {}
    for k in ("title", "exam", "examTime", "start"):
        if not isinstance(plan.get(k), str):
            plan[k] = "" if plan.get(k) is None else str(plan[k])
    if plan.get("status") not in ("active", "archived"):
        plan["status"] = "active"
    if plan.get("order") not in ("auto", "manual"):
        plan["order"] = "auto"
    try:
        plan["minutesPerDay"] = max(0, int(plan.get("minutesPerDay", 180)))
    except (TypeError, ValueError):
        plan["minutesPerDay"] = 180
    plan["sources"] = [s for s in plan["sources"] if isinstance(s, dict) and s.get("id") and s.get("type") in planner.DEFAULT_RATES]
    for s in plan["sources"]:
        s.setdefault("name", "")
        if s["type"] in ("videos", "tasks") and not isinstance(s.get(s["type"]), list):
            s[s["type"]] = []
    plan["topics"] = [t for t in plan["topics"] if isinstance(t, dict) and t.get("id")]
    for t in plan["topics"]:
        t.setdefault("name", "")
        for k in ("pages", "videos", "tasks", "anki"):
            if not isinstance(t.get(k), dict):
                t[k] = {}
    plan["milestones"] = [m for m in plan["milestones"] if isinstance(m, dict)]
    for m in plan["milestones"]:
        m.setdefault("id", planner.new_id("m"))
        m.setdefault("name", "")
    days = []
    for d in plan["days"]:
        if not isinstance(d, dict) or not isinstance(d.get("d"), str):
            continue
        items = [it for it in d.get("items") or [] if isinstance(it, dict)]
        for it in items:
            if not it.get("id"):
                it["id"] = planner.new_id()
            it.setdefault("kind", "custom")
            it.setdefault("text", "")
        d["items"] = items
        days.append(d)
    plan["days"] = sorted(days, key=lambda d: d["d"])
    return plan


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


def _num(x):
    try:
        return float(x or 0)
    except (TypeError, ValueError):
        return 0.0


def _stamp(x):
    return -1 if x is None else _num(x.get("savedAt"))


def _files():
    out = {}
    if os.path.isdir(PLANS):
        for f in sorted(os.listdir(PLANS)):
            if f.endswith(".json"):
                p = _read(os.path.join(PLANS, f))
                if p and isinstance(p.get("id"), str) and re.fullmatch(r"[A-Za-z0-9_-]+", p["id"]):
                    out[p["id"]] = p
    return out


def _reconcile():
    """Brings files and collection in line and returns all plans {id: plan}."""
    files = _files()
    conf = _get_conf(CONF_PLANS)
    if conf is None and not _col():
        return {pid: normalize(p) for pid, p in files.items()}
    conf = {pid: p for pid, p in (conf if isinstance(conf, dict) else {}).items()
            if isinstance(p, dict) and re.fullmatch(r"[A-Za-z0-9_-]+", str(pid))}
    deleted = _get_conf(CONF_DELETED)
    deleted = deleted if isinstance(deleted, dict) else {}
    out, changed = {}, False
    for pid in sorted(set(files) | set(conf)):
        f, c = files.get(pid), conf.get(pid)
        if pid in deleted and max(_stamp(f), _stamp(c)) <= _num(deleted[pid]):
            if f:
                try:
                    os.remove(_path(pid))
                except OSError:
                    pass
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
    return {pid: normalize(p) for pid, p in out.items()}


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
        cutoff = time.time() - 400 * 86400  # other devices have long synced by then
        deleted = {k: v for k, v in deleted.items() if _num(v) >= cutoff}
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
    if not isinstance(p.get("rates"), dict):
        p["rates"] = {}
    for k, v in planner.DEFAULT_RATES.items():
        if not isinstance(p["rates"].get(k), (int, float)) or p["rates"][k] <= 0:
            p["rates"][k] = v
    if not isinstance(p.get("history"), list):
        p["history"] = []
    return p


def save_profile(p):
    p["savedAt"] = time.time()
    _write(PROFILE, p)
    _set_conf(CONF_PROFILE, p)
