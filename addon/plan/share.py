# Share a study plan with friends: as a file or as a code that fits into a chat
# message. Only the plan itself is shared – no progress (ticks, mock exams,
# retrospective) and no paths to files on this computer. A plan from someone
# else is cleaned before it is stored. No Anki needed (tested in tests/test_share.py).
import base64
import json
import re
import zlib

KIND = "smart-study-plan"
VERSION = 1
PREFIX = "SSP1:"
MAX_BYTES = 4 * 1024 * 1024  # plenty for a plan of a whole semester

# What a friend gets; everything else (done, autoDone, sim, simHistory,
# review, maintenance, notes, savedAt, status, id) stays private.
SHARED_KEYS = ("title", "subtitle", "exam", "examTime", "start", "minutesPerDay", "offWeekdays",
               "dayMinutes", "dayNotes", "order", "milestones", "sources", "topics", "days")
PRIVATE_SOURCE_KEYS = ("file",)  # a PDF path only exists on the sender's computer
SOURCE_TYPES = ("pages", "videos", "tasks", "anki")
_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
END = "~"  # ends the code, so text after it in a chat message is not part of it
_CODE = re.compile(re.escape(PREFIX) + r"\s*([A-Za-z0-9_\-\s]+?)\s*(?:" + re.escape(END) + r"|$)")


class ShareError(ValueError):
    pass


def export_plan(plan):
    """The shareable part of a plan, wrapped with a marker and version."""
    out = {k: json.loads(json.dumps(plan[k])) for k in SHARED_KEYS if k in plan}
    for s in out.get("sources") or []:
        if isinstance(s, dict):
            for k in PRIVATE_SOURCE_KEYS:
                s.pop(k, None)
    return {"kind": KIND, "v": VERSION, "plan": out}


def encode(payload):
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return PREFIX + base64.urlsafe_b64encode(zlib.compress(raw, 9)).decode("ascii").rstrip("=") + END


def decode(text):
    """A plan code (also inside a longer chat message) or the JSON of a plan file."""
    text = (text or "").strip()
    if text.startswith("﻿"):
        text = text[1:]
    if text.startswith("{"):
        if len(text.encode("utf-8")) > MAX_BYTES:
            raise ShareError("too large")
        try:
            data = json.loads(text)
        except ValueError:
            raise ShareError("not a plan")
    else:
        m = _CODE.search(text)
        if not m:
            raise ShareError("no code")
        code = re.sub(r"\s+", "", m.group(1)).rstrip("=")
        try:
            packed = base64.urlsafe_b64decode(code + "=" * (-len(code) % 4))
            inflater = zlib.decompressobj()
            raw = inflater.decompress(packed, MAX_BYTES + 1)
            if len(raw) > MAX_BYTES or inflater.unconsumed_tail:
                raise ShareError("too large")
            data = json.loads(raw.decode("utf-8"))
        except ShareError:
            raise
        except Exception:
            raise ShareError("broken code")
    if not isinstance(data, dict) or data.get("kind") != KIND or not isinstance(data.get("plan"), dict):
        raise ShareError("not a plan")
    if not isinstance(data.get("v"), int) or data["v"] > VERSION:
        raise ShareError("newer version")
    return data


def _clean(x, depth=0):
    """Plain JSON with sane sizes; links only to web pages, no file paths."""
    if depth > 12:
        return None
    if isinstance(x, dict):
        out = {}
        for k, v in list(x.items())[:500]:
            if not isinstance(k, str) or len(k) > 64:
                continue
            if k in PRIVATE_SOURCE_KEYS:
                continue
            if k == "url" and not (isinstance(v, str) and v.startswith(("http://", "https://")) and len(v) <= 4000):
                continue
            v = _clean(v, depth + 1)
            if v is not None:
                out[k] = v
        return out
    if isinstance(x, list):
        return [c for c in (_clean(v, depth + 1) for v in x[:5000]) if c is not None]
    if isinstance(x, str):
        return x[:5000]
    if isinstance(x, bool) or x is None:
        return x
    if isinstance(x, (int, float)):
        return x if abs(x) < 1e9 else None
    return None


def import_plan(data, base):
    """Fills *base* (a new empty plan of this user) with the shared plan."""
    shared = _clean(data["plan"])
    plan = dict(base)
    for k in SHARED_KEYS:
        if k not in shared:
            continue
        v = shared[k]
        if k in plan and plan[k] is not None and type(plan[k]) is not type(v) \
                and not (isinstance(plan[k], (int, float)) and isinstance(v, (int, float))):
            continue
        plan[k] = v
    title = str(plan.get("title") or "").strip()
    if not title:
        raise ShareError("not a plan")
    plan["title"] = title[:200]
    for k in ("exam", "start"):
        if plan.get(k) and not _DATE.match(str(plan[k])):
            plan[k] = base.get(k, "")
    if not isinstance(plan.get("minutesPerDay"), (int, float)) or not 0 < plan["minutesPerDay"] <= 24 * 60:
        plan["minutesPerDay"] = base.get("minutesPerDay", 180)
    plan["minutesPerDay"] = int(plan["minutesPerDay"])
    plan["sources"] = [s for s in plan.get("sources") or []
                       if isinstance(s, dict) and _ID.match(str(s.get("id", ""))) and s.get("type") in SOURCE_TYPES
                       and isinstance(s.get("name", ""), str)]
    for s in plan["sources"]:
        s.setdefault("name", "")
        if "decks" in s:
            s["decks"] = [d for d in s["decks"] if isinstance(d, str)] if isinstance(s["decks"], list) else []
        if "deck" in s and not isinstance(s["deck"], str):
            s.pop("deck")
        for k in ("videos", "tasks"):
            if k in s:
                s[k] = [x for x in s[k] if isinstance(x, dict)] if isinstance(s[k], list) else []
    plan["topics"] = [t for t in plan.get("topics") or [] if isinstance(t, dict) and _ID.match(str(t.get("id", "")))]
    plan["milestones"] = [m for m in plan.get("milestones") or [] if isinstance(m, dict)]
    days, seen = [], set()
    for d in plan.get("days") or []:
        if not isinstance(d, dict) or not _DATE.match(str(d.get("d", ""))) or d["d"] in seen:
            continue
        items = [it for it in d.get("items") or [] if isinstance(it, dict) and _ID.match(str(it.get("id", "")))
                 and isinstance(it.get("text", ""), str)]
        for it in items:
            it.setdefault("text", "")
            if it.get("kind") == "pages" and not (isinstance(it.get("pages"), list) and len(it["pages"]) == 2
                                                  and all(isinstance(n, int) for n in it["pages"])):
                it.pop("pages", None)
                it["kind"] = "custom"
        seen.add(d["d"])
        days.append({"d": d["d"], "items": items})
    plan["days"] = sorted(days, key=lambda d: d["d"])
    for k in ("offWeekdays",):
        plan[k] = [w for w in plan.get(k) or [] if isinstance(w, int) and 0 <= w <= 6]
    plan["dayMinutes"] = {d: int(v) for d, v in (plan.get("dayMinutes") or {}).items()
                          if _DATE.match(d) and isinstance(v, (int, float)) and not isinstance(v, bool) and 0 <= v <= 24 * 60}
    plan["dayNotes"] = {d: v for d, v in (plan.get("dayNotes") or {}).items() if _DATE.match(d) and isinstance(v, str)}
    plan["done"], plan["autoDone"], plan["notes"] = {}, {}, []
    plan["status"] = "active"
    return plan


def file_name(title):
    safe = "".join(ch for ch in str(title) if ch not in '<>:"/\\|?*' and ord(ch) >= 32).strip(" .")[:80]
    return (safe or "Plan") + ".smartstudy.json"
