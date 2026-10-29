# Planning logic without any Anki dependency (testable with plain Python).
# A plan consists of sources (pages, videos, tasks, Anki decks) and topics that
# bundle parts of those sources. build() spreads everything still open over the
# days until the exam; finished items and custom items are kept.
import difflib
import random
import re
import unicodedata
from datetime import date, datetime, timedelta

DEFAULT_RATES = {"pages": 6.0, "videos": 20.0, "tasks": 30.0, "anki": 1.0}  # minutes per unit
NO_CHECK = ("note", "weakround", "sim")
PREP_DAYS = 7  # preparation for a lab session starts this many days before it
REVIEW_MIN = 0.4  # minutes per review until real timings are available
REVIEW_STEPS = (1, 3, 7, 14, 30)  # rough: a new card comes back on these days after first study
BACKLOG_DAYS = 4  # overdue reviews are spread over this many days
LANG = "en"  # set from Anki's interface language in __init__.py


def tr(de, en):
    return de if LANG == "de" else en


def d2s(d):
    return d.isoformat()


def s2d(s):
    return date.fromisoformat(s)


def new_id(prefix="i"):
    return f"{prefix}{random.getrandbits(40):010x}"


def daterange(a, b):
    while a <= b:
        yield a
        a += timedelta(days=1)


def capacity(plan, d):
    s = d2s(d)
    if s in plan.get("dayMinutes", {}):
        return max(0, int(plan["dayMinutes"][s]))
    if d.weekday() in plan.get("offWeekdays", []):
        return 0
    return int(plan.get("minutesPerDay", 180))


def budget_capacity(budget, d):
    """Total study time of the day across all plans (profile); None = no limit."""
    if not budget:
        return None
    s = d2s(d)
    if s in budget.get("dayMinutes", {}):
        return max(0, int(budget["dayMinutes"][s]))
    return int(budget.get("minutesPerDay", 360))


def day_load(plan, today):
    """Minutes this plan takes up per day from today on (including reviews)."""
    out = {}
    for day, it in all_items(plan):
        if day["d"] >= d2s(today) and not it.get("moved") and it.get("kind") != "note":
            out[day["d"]] = out.get(day["d"], 0) + it.get("min", 0)
    return out


def review_load(forecast, start, exam, study_days, returns=None, backlog_days=BACKLOG_DAYS):
    """Expected reviews per day: due according to Anki (overdue ones spread out)
    plus the return of the newly scheduled cards."""
    out = {}
    if forecast:
        late = sum(n for k, n in forecast["due"].items() if int(k) < 0)
        spread = study_days[:backlog_days] or [start]
        for d in spread:
            out[d2s(d)] = out.get(d2s(d), 0) + late / len(spread)
        for k, n in forecast["due"].items():
            d = start + timedelta(days=max(0, int(k)))
            if int(k) >= 0 and d <= exam:
                out[d2s(d)] = out.get(d2s(d), 0) + n
    for (s, until), n in (returns or {}).items():
        for step in REVIEW_STEPS:
            d = s2d(s) + timedelta(days=step)
            if d <= min(exam, s2d(until)):
                out[d2s(d)] = out.get(d2s(d), 0) + n
    return out


def review_scopes(plan):
    """(search, from, until): which studied cards are reviewed in which period.
    onceOnly: one-off units – a topic's cards only until its date.
    reviewsFrom on a source: its cards only from that day on (e.g. after your own test)."""
    if plan.get("onceOnly"):
        due = {m["id"]: m["date"] for m in milestones(plan) if m["id"]}
        return [(q, None, due.get(t.get("milestone"), plan["exam"]))
                for t in plan.get("topics", []) for src in anki_sources(plan)
                for q in [topic_query(plan, t, src)] if q]
    return [(src_query(src), src.get("reviewsFrom"), plan["exam"]) for src in anki_sources(plan) if src_query(src)]


def review_query(plan, today):
    """Search for the cards that should be reviewed today (for 'X still due')."""
    qs = [q for q, a, b in review_scopes(plan) if (not a or a <= today) and b >= today]
    return "(" + " OR ".join("(" + q + ")" for q in qs) + ")" if qs else None


def all_items(plan):
    for day in plan.get("days", []):
        for it in day["items"]:
            yield day, it


def anki_sources(plan):
    return [s for s in plan.get("sources", []) if s["type"] == "anki"]


def deck_query(name):
    return 'deck:"%s"' % name.replace('"', '\\"')


def src_decks(src):
    """Decks of an Anki source (formerly a single "deck", now a list "decks")."""
    if src.get("decks"):
        return list(src["decks"])
    return [src["deck"]] if src.get("deck") else []


def src_query(src):
    qs = [deck_query(d) for d in src_decks(src)]
    if not qs:
        return None
    return qs[0] if len(qs) == 1 else "(" + " OR ".join(qs) + ")"


def rest_query(plan, src):
    """Cards of the source that are not assigned to any topic."""
    base = src_query(src)
    if not base:
        return None
    qs = [t["anki"][src["id"]] for t in plan.get("topics", []) if t.get("anki", {}).get(src["id"])]
    return base if not qs else f"{base} -({' OR '.join('(' + q + ')' for q in qs)})"


def topic_query(plan, topic, src):
    q = topic.get("anki", {}).get(src["id"])
    base = src_query(src)
    return f"{base} ({q})" if q and base else None


def queries(plan):
    """All Anki searches whose counts build() and evaluate() need."""
    out = set()
    for src in anki_sources(plan):
        if not src_query(src):
            continue
        out.add(src_query(src))
        out.add(rest_query(plan, src))
        for t in plan.get("topics", []):
            q = topic_query(plan, t, src)
            if q:
                out.add(q)
    for _, it in all_items(plan):
        a = it.get("auto") or {}
        if a.get("query"):
            out.add(a["query"])
    return sorted(out)


def milestones(plan):
    """Milestones (e.g. partial tests) by date; the exam itself always comes last."""
    ms = sorted((m for m in plan.get("milestones", []) if m.get("date") and m["date"] < plan["exam"]),
                key=lambda m: m["date"])
    return ms + [{"id": None, "name": tr("Prüfung", "Exam"), "date": plan["exam"], "time": plan.get("examTime", ""),
                  "final": True}]


def ordered_topics(plan):
    """Automatic: by milestone date, then by page. Otherwise as listed."""
    topics = list(plan.get("topics", []))
    if plan.get("order", "auto") != "auto":
        return topics
    psrc = [s["id"] for s in plan.get("sources", []) if s["type"] == "pages"]
    due = {m["id"]: m["date"] for m in milestones(plan) if m["id"]}

    def key(ix_t):
        ix, t = ix_t
        d = due.get(t.get("milestone"), plan["exam"])
        for sid in psrc:
            r = t.get("pages", {}).get(sid)
            if r:
                return (d, 0, int(r[0]), ix)
        return (d, 1, 0, ix)

    return [t for _, t in sorted(enumerate(topics), key=key)]


def segments(nums):
    """[3,4,5,9,10] -> [(3,5),(9,10)]"""
    out = []
    for n in sorted(nums):
        if out and n == out[-1][1] + 1:
            out[-1][1] = n
        else:
            out.append([n, n])
    return [tuple(s) for s in out]


def is_done(plan, it, ev=None):
    if it["id"] in plan.get("done", {}):
        return True
    return bool(ev and ev.get(it["id"], {}).get("done"))


def remaining_work(plan, counts, ev):
    """List of the work units still open, in study order."""
    srcs = {s["id"]: s for s in plan.get("sources", [])}
    done_pages, done_videos, done_tasks = {}, set(), set()
    for _, it in all_items(plan):
        if not is_done(plan, it, ev):
            continue
        if it.get("kind") == "pages":
            a, b = it["pages"]
            done_pages.setdefault((it.get("topic"), it["source"]), set()).update(range(a, b + 1))
        elif it.get("kind") == "video":
            done_videos.add((it["source"], it["video"]))
        elif it.get("kind") == "task":
            done_tasks.add((it["source"], it["task"]))

    units = []

    def rate(src):
        return float(src.get("minPerUnit") or DEFAULT_RATES[src["type"]])

    for t in ordered_topics(plan):
        for sid, r in t.get("pages", {}).items():
            src = srcs.get(sid)
            if not src or not r:
                continue
            left = set(range(int(r[0]), int(r[1]) + 1)) - done_pages.get((t["id"], sid), set())
            for a, b in segments(left):
                units.append({"kind": "pages", "topic": t["id"], "source": sid, "from": a, "n": b - a + 1,
                              "cost": rate(src), "split": True})
        for sid, vids in t.get("videos", {}).items():
            src = srcs.get(sid)
            if not src:
                continue
            byid = {v["id"]: v for v in src.get("videos", [])}
            for vid in vids:
                if vid in byid and (sid, vid) not in done_videos:
                    v = byid[vid]
                    units.append({"kind": "video", "topic": t["id"], "source": sid, "video": vid, "n": 1,
                                  "cost": float(v.get("min") or src.get("defaultMin") or DEFAULT_RATES["videos"]),
                                  "split": False})
        for sid, tids in t.get("tasks", {}).items():
            src = srcs.get(sid)
            if not src:
                continue
            byid = {x["id"]: x for x in src.get("tasks", [])}
            for tid in tids:
                if tid in byid and (sid, tid) not in done_tasks:
                    units.append({"kind": "task", "topic": t["id"], "source": sid, "task": tid, "n": 1,
                                  "cost": float(byid[tid].get("min") or DEFAULT_RATES["tasks"]), "split": False})
        for src in anki_sources(plan):
            q = topic_query(plan, t, src)
            if q and counts.get(q, {}).get("new") and not src.get("reviewOnly"):
                units.append({"kind": "cards", "topic": t["id"], "source": src["id"], "query": q,
                              "n": counts[q]["new"], "cost": rate(src), "split": True,
                              "seen": counts[q]["total"] - counts[q]["new"]})
    # Unassigned videos/tasks (no topic) and the remaining Anki cards go last
    used_v = {(sid, v) for t in plan.get("topics", []) for sid, vs in t.get("videos", {}).items() for v in vs}
    used_t = {(sid, x) for t in plan.get("topics", []) for sid, xs in t.get("tasks", {}).items() for x in xs}
    for src in plan.get("sources", []):
        if src["type"] == "videos":
            for v in src.get("videos", []):
                if (src["id"], v["id"]) not in used_v and (src["id"], v["id"]) not in done_videos:
                    units.append({"kind": "video", "topic": None, "source": src["id"], "video": v["id"], "n": 1,
                                  "cost": float(v.get("min") or src.get("defaultMin") or DEFAULT_RATES["videos"]),
                                  "split": False})
        elif src["type"] == "tasks":
            for x in src.get("tasks", []):
                if (src["id"], x["id"]) not in used_t and (src["id"], x["id"]) not in done_tasks:
                    units.append({"kind": "task", "topic": None, "source": src["id"], "task": x["id"], "n": 1,
                                  "cost": float(x.get("min") or DEFAULT_RATES["tasks"]), "split": False})
    for src in anki_sources(plan):
        q = rest_query(plan, src)
        if q and counts.get(q, {}).get("new") and not src.get("reviewOnly"):
            units.append({"kind": "cards", "topic": None, "source": src["id"], "query": q,
                          "n": counts[q]["new"], "cost": rate(src), "split": True,
                          "seen": counts[q]["total"] - counts[q]["new"]})
    return units


def reserve_count(n_days):
    if n_days >= 7:
        return 3
    if n_days >= 4:
        return 2
    return 1 if n_days >= 2 else 0


def build(plan, counts, today, ev=None, forecast=None, taken=None, budget=None):
    """(Re)plan from today. Past days stay as history; their open items are
    marked as 'moved' and distributed again.
    counts: {query: {"total", "new"}}; ev: result of evaluate() (auto checkmarks).
    forecast: {"due": {days from today: count}, "min": minutes per review} from Anki –
    reviews get their own time with it. taken: {date: minutes} already used by plans
    with an earlier exam; budget: study time of all plans together (profile).
    Returns a list of notes (e.g. overload)."""
    ev = ev or {}
    taken = taken or {}
    exam = s2d(plan["exam"])
    start = max(today, s2d(plan["start"]))
    if start > exam:
        plan["notes"] = [tr("Die Prüfung ist schon vorbei – nichts mehr zu verteilen.",
                            "The exam is already over – nothing left to schedule.")]
        return plan["notes"]
    srcs = {s["id"]: s for s in plan.get("sources", [])}
    topics = {t["id"]: t for t in plan.get("topics", [])}

    days = {d["d"]: d for d in plan.get("days", [])}
    carry = []
    for s, day in sorted(days.items()):
        keep = []
        for it in day["items"]:
            done = is_done(plan, it, ev)
            if s < d2s(start):
                if not done and it.get("kind") not in NO_CHECK and it.get("kind") != "reviews":
                    if it.get("custom"):
                        carry.append(it)  # custom items move along
                        continue
                    it["moved"] = True
                keep.append(it)
            elif done or it.get("custom"):
                keep.append(it)
        day["items"] = keep
    for d in daterange(start, exam):
        days.setdefault(d2s(d), {"d": d2s(d), "items": []})
    days[d2s(start)]["items"][0:0] = carry

    used_today = sum(it.get("min", 0) for it in days[d2s(start)]["items"]
                     if is_done(plan, it, ev) and it.get("kind") != "reviews")
    has_anki = bool(anki_sources(plan))
    rev_min = float((forecast or {}).get("min") or REVIEW_MIN)

    def room(d):
        """Study time of this plan on a day (its own limit and what the total budget still allows)."""
        c = capacity(plan, d)
        b = budget_capacity(budget, d)
        return c if b is None else min(c, max(0, b - taken.get(d2s(d), 0)))

    study = [d for d in daterange(start, exam) if room(d) > 0]

    # Milestones: every partial test gets its own window up to its date.
    # Material of a past test is not scheduled anymore.
    # Lab sessions (prep) are soft milestones: until then only reading + video,
    # the topic's cards keep running until the next real date.
    ms = milestones(plan)
    ms_open = [m for m in ms if s2d(m["date"]) >= start]
    ms_by_id = {m["id"]: m for m in ms if m["id"]}
    multi = len(ms_open) > 1

    def allocate(rev):
        """Distributes the open material; rev = expected reviews per day (time for them is reserved)."""
        groups = [[] for _ in ms_open]

        def target(due, hard):
            return next(j for j, m in enumerate(ms_open) if m["date"] >= due and not (hard and m.get("prep")))

        for u in remaining_work(plan, counts, ev):
            t = topics.get(u["topic"])
            m = ms_by_id.get(t.get("milestone")) if t else None
            due = m["date"] if m else plan["exam"]
            prep = bool(m and m.get("prep"))
            if due < d2s(start) and not prep:
                continue
            groups[target(max(due, d2s(start)), prep and u["kind"] == "cards")].append(u)

        generated, reserve_map, used = {}, {}, {}
        new_per_day, seen_so_far, returns = {}, {}, {}
        notes = []

        def fill(units, content, cap, m):
            budget_total = sum(cap)
            work = sum(u["n"] * u["cost"] for u in units)
            label = tr("zur Prüfung", "the exam") if m.get("final") else tr(f"zu „{m['name']}“", f"“{m['name']}”")
            if m.get("prep") and work > budget_total * 1.02:
                notes.append(tr(f"Vor dem Präpsaal „{m['name']}“ ist die Vorbereitung knapp ({round(work / 60, 1)} h Lesen/Videos, "
                                f"{round(budget_total / 60, 1)} h Zeit).",
                                f"Preparation for the lab session “{m['name']}” is tight ({round(work / 60, 1)} h reading/videos, "
                                f"{round(budget_total / 60, 1)} h available)."))
            elif work > budget_total * 1.02:
                notes.append(tr(f"Bis {label} ist der Plan zu voll: {round((work - budget_total) / 60, 1)} h mehr Stoff als Lernzeit "
                                "(Wiederholungen schon abgezogen). Mehr Zeit pro Tag eintragen oder Stoff streichen.",
                                f"The plan up to {label} is too full: {round((work - budget_total) / 60, 1)} h more material than "
                                "study time (reviews already subtracted). Add more time per day or cut material."))
            scale = work / budget_total if budget_total else 0
            budget_ = [c * scale for c in cap]
            st = {"i": 0, "rem": budget_[0] if budget_ else 0}

            def next_day():
                if st["i"] < len(content) - 1:
                    st["i"] += 1
                    st["rem"] = budget_[st["i"]]
                    return True
                return False

            def emit(u, k):
                t = topics.get(u["topic"])
                tname = t["name"] if t else None
                src = srcs[u["source"]]
                day = d2s(content[st["i"]])
                it = {"id": new_id(), "kind": u["kind"], "topic": u["topic"], "source": u["source"], "min": round(k * u["cost"])}
                if multi:
                    it["for"] = tr("Prüfung", "exam") if m.get("final") else m["name"]
                if u["kind"] == "pages":
                    a = u["from"]
                    it["pages"] = [a, a + k - 1]
                    p = tr("S.", "p.") if k == 1 else tr("S.", "pp.")
                    rng = f"{p} {a}" if k == 1 else f"{p} {a}–{a + k - 1}"
                    it["text"] = f"{rng}" + (f" · {tname}" if tname else "")
                    u["from"] += k
                elif u["kind"] in ("video", "task"):
                    key = "videos" if u["kind"] == "video" else "tasks"
                    x = next(x for x in src[key] if x["id"] == u[u["kind"]])
                    it[u["kind"]] = u[u["kind"]]
                    it["text"] = x["name"]
                    if x.get("url"):
                        it["url"] = x["url"]
                else:
                    base = seen_so_far.setdefault(u["query"], u["seen"])
                    seen_so_far[u["query"]] = base + k
                    it["cards"] = k
                    it["auto"] = {"type": "seen", "query": u["query"], "target": base + k}
                    it["text"] = tr(f"{k} neue Karten", f"{k} new cards") + (
                        f" · {tname}" if tname else tr(" · übrige Karten", " · remaining cards"))
                    new_per_day[(day, u["source"])] = new_per_day.get((day, u["source"]), 0) + k
                    until = m["date"] if plan.get("onceOnly") else plan["exam"]
                    returns[(day, until)] = returns.get((day, until), 0) + k
                generated.setdefault(day, []).append(it)
                used[day] = used.get(day, 0) + k * u["cost"]
                st["rem"] -= k * u["cost"]
                u["n"] -= k

            for u in units:
                while u["n"] > 0:
                    last = st["i"] == len(content) - 1
                    if u["split"]:
                        k = u["n"] if last else min(u["n"], int(st["rem"] / u["cost"] + 0.5))
                        if u["kind"] == "cards" and not last:
                            mx = srcs[u["source"]].get("maxNew")
                            if mx:
                                k = min(k, int(mx) - new_per_day.get((d2s(content[st["i"]]), u["source"]), 0))
                        if k <= 0:
                            if not next_day():
                                emit(u, u["n"])
                            continue
                        emit(u, k)
                        if st["rem"] < u["cost"] * 0.5:
                            next_day()
                    else:
                        if st["rem"] < u["cost"] * 0.5 and st["rem"] < budget_[st["i"]] and next_day():
                            continue
                        emit(u, 1)
                        if st["rem"] <= 0:
                            next_day()

        def caps(content):
            return [max(0, room(d) - rev.get(d2s(d), 0) * rev_min - (used_today if d == start else 0) - used.get(d2s(d), 0))
                    for d in content]

        prev = start - timedelta(days=1)
        pj = 0
        for j, m in enumerate(ms_open):
            if m.get("prep"):
                continue
            deadline = s2d(m["date"])
            avail = [d for d in daterange(prev + timedelta(days=1), deadline - timedelta(days=1)) if room(d) > 0]
            r = reserve_count(len(avail)) if m.get("final") else (1 if len(avail) >= 3 else 0)
            content, reserve = avail[:len(avail) - r], avail[len(avail) - r:]
            if not content:
                content, reserve = avail, []
            for k, d in enumerate(reserve):
                reserve_map[d2s(d)] = reserve_items(plan, k, len(reserve)) if m.get("final") else [
                    {"id": new_id(), "kind": "note", "text": tr(
                        f"Wiederholen für „{m['name']}“: Themen dieser Etappe laut erklären, Schwachstellen anschauen, nichts Neues.",
                        f"Review for “{m['name']}”: explain this milestone's topics out loud, look at weak spots, nothing new.")}]
            for k in range(pj, j):  # lab sessions in this window first
                pm, pdl = ms_open[k], s2d(ms_open[k]["date"])
                # Prepare in the week before (not scattered over weeks, not all on the day before)
                sub = [d for d in content if d < pdl and (pdl - d).days <= PREP_DAYS] or [d for d in content if d < pdl]
                if groups[k] and sub:
                    fill(groups[k], sub, caps(sub), pm)
                elif groups[k]:
                    groups[k + 1][0:0] = groups[k]
            pj = j + 1
            if groups[j] and not content:
                if j + 1 < len(ms_open):
                    notes.append(tr(f"Vor „{m['name']}“ ist keine Lernzeit mehr – der Stoff dafür rutscht in die nächste Etappe.",
                                    f"There is no study time left before “{m['name']}” – its material moves to the next milestone."))
                    groups[j + 1][0:0] = groups[j]
                else:
                    notes.append(tr("Bis zur Prüfung ist keine Lernzeit mehr eingetragen.",
                                    "There is no study time left before the exam."))
            elif groups[j]:
                fill(groups[j], content, caps(content), m)
            prev = deadline
        lim = {s["id"]: s.get("maxNew") for s in anki_sources(plan)}
        if any(lim.get(sid) and n > int(lim[sid]) for (_, sid), n in new_per_day.items()):
            notes.append(tr("Das Tageslimit für neue Karten reicht nicht; am letzten Lerntag vor einem Termin liegen mehr neue Karten.",
                            "The daily limit for new cards is too low; the last study day before a date gets extra new cards."))
        return generated, reserve_map, returns, notes

    # Spread overdue reviews so they take at most half of the free time.
    late = sum(n for k, n in (forecast or {}).get("due", {}).items() if int(k) < 0) * rev_min
    nb = BACKLOG_DAYS
    while nb < len(study) and late / nb > 0.5 * sum(room(d) for d in study[:nb]) / nb:
        nb += 1

    # Reviews depend on when new cards are scheduled – a few rounds until it settles.
    rev = review_load(forecast, start, exam, study, None, nb) if has_anki else {}
    for _ in range(3):
        generated, reserve_map, returns, notes = allocate(rev)
        rev = review_load(forecast, start, exam, study, returns, nb) if has_anki else {}
    full = [d for d in study if rev.get(d2s(d), 0) * rev_min > room(d) + 5]
    if full:
        notes.append(tr(f"An {len(full)} Tag(en) brauchen die Wiederholungen allein schon mehr Zeit als frei ist "
                        f"(z. B. {full[0].strftime('%d.%m.')}). Weniger neue Karten oder mehr Lernzeit.",
                        f"On {len(full)} day(s) the reviews alone need more time than is available "
                        f"(e.g. {full[0].strftime('%d.%m.')}). Fewer new cards or more study time."))

    # Assemble the days: reviews first, then the material
    by_date = {m["date"]: m for m in ms_open}
    for d in daterange(start, exam):
        s = d2s(d)
        items = days[s]["items"]
        gen = reserve_map.get(s) or generated.get(s, [])
        m = by_date.get(s)
        if m and m.get("prep"):
            when = tr(f" ab {m['time']}", f" from {m['time']}") if m.get("time") else ""
            gen = [{"id": new_id(), "kind": "note", "text": tr(f"Präpsaal{when}: {m['name']}", f"Lab session{when}: {m['name']}")}] + gen
        elif m:
            when = tr(f" um {m['time']}", f" at {m['time']}") if m.get("time") else ""
            gen = [{"id": new_id(), "kind": "note", "text": tr(f"Prüfung{when}: nur leicht wiederholen, vorher etwas essen.",
                                                               f"Exam{when}: only light review, eat something before.")
                    if m.get("final") else tr(f"{m['name']}{when}: vorher kurz wiederholen. Viel Erfolg!",
                                              f"{m['name']}{when}: quick review beforehand. Good luck!")}]
        if has_anki and (room(d) > 0 or m) and not any(x.get("kind") == "reviews" for x in items):
            n = round(rev.get(s, 0))
            gen.insert(0, {"id": new_id(), "kind": "reviews", "auto": {"type": "reviews"}, "reviews": n,
                           "min": round(n * rev_min),
                           "text": tr(f"Wiederholungen (ca. {n})", f"Reviews (about {n})") if n
                           else tr("Fällige Wiederholungen", "Due reviews")})
        days[s]["items"] = items + [g for g in gen if not any(x.get("kind") == g["kind"] and g["kind"] in NO_CHECK
                                                              for x in items)]
    plan["days"] = [days[k] for k in sorted(days)]
    plan["generatedAt"] = datetime.now().isoformat(timespec="minutes")
    plan["notes"] = notes
    return notes


def reserve_items(plan, ix, n):
    """Reserve days before the exam: weak spots → mock exam → review."""
    kinds = {3: ["weakround", "sim", "final"], 2: ["sim", "final"], 1: ["final"]}[n]
    kind = kinds[ix]
    if kind == "weakround":
        return [{"id": new_id(), "kind": "weakround", "min": 60, "text": tr(
            "Schwachstellen-Runde: die schwächsten Themen gezielt wiederholen",
            "Weak spots round: go over your weakest topics")}]
    if kind == "sim":
        return [{"id": new_id(), "kind": "sim", "min": 60, "text": tr(
            "Probeprüfung: gemischte Karten auf Zeit + zufällige Themen frei erklären",
            "Mock exam: mixed cards against the clock + explain random topics freely")}]
    return [{"id": new_id(), "kind": "note", "text": tr(
        "Letzter Tag: nur wiederholen, Schwachstellen kurz anschauen, nichts Neues. Früh schlafen.",
        "Last day: only review, glance at weak spots, nothing new. Go to bed early.")}]


def evaluate(plan, st):
    """Auto checkmarks from Anki data. st: {today, due, rated:{day:n}, counts:{q:{total,new}}}."""
    out = {}
    for day, it in all_items(plan):
        a = it.get("auto")
        if not a or not st:
            continue
        if a["type"] == "reviews":
            n = st["rated"].get(day["d"], 0)
            if day["d"] < st["today"]:
                out[it["id"]] = {"done": n > 0, "text": tr("erledigt", "done") if n else tr("nicht gemacht", "not done")}
            elif day["d"] == st["today"]:
                out[it["id"]] = {"done": st["due"] == 0, "text": tr("alles erledigt", "all done") if st["due"] == 0
                                 else tr(f"noch {st['due']} fällig", f"{st['due']} still due")}
        elif a["type"] == "seen":
            c = st["counts"].get(a["query"])
            if not c or not c["total"]:  # no cards: deck deleted/renamed, not "finished"
                continue
            seen = c["total"] - c["new"]
            k = it.get("cards", 0)
            got = max(0, min(k, seen - (a["target"] - k)))
            out[it["id"]] = {"done": seen >= a["target"] or c["new"] == 0, "text": f"{got}/{k}"}
    return out


def progress(plan, ev):
    tot = done = 0
    for _, it in all_items(plan):
        if it.get("kind") in NO_CHECK or it.get("moved") or it.get("kind") == "reviews":
            continue
        tot += 1
        done += is_done(plan, it, ev)
    return done, tot


def overdue(plan, ev, today):
    out = []
    for day, it in all_items(plan):
        if day["d"] < today and it.get("kind") not in NO_CHECK and it.get("kind") != "reviews" \
                and not it.get("moved") and not is_done(plan, it, ev):
            out.append(it["id"])
    return out


# --- Matching topics <-> subdecks/tags/videos -----------------------------------

def norm(s):
    s = s.lower().replace("ß", "ss")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


STOP = {"und", "der", "die", "das", "des", "mit", "von", "im", "in", "teil", "the", "and", "of", "a", "m", "a"}
ROMAN = {r: str(i) for i, r in enumerate(
    "i ii iii iv v vi vii viii ix x xi xii xiii xiv xv xvi xvii xviii xix xx".split(), 1) if r != "i"}
GENERIC = {"testat", "pruefung", "prufung", "klausur", "lernplan", "smart", "plan", "exam", "sip", "anki", "deck",
           "test", "final", "midterm", "study"}


def tokens(s):
    """Normalized words; 'PM8' -> pm 8, 'VIII' -> 8."""
    s = re.sub(r"(?<=[a-z])(?=\d)|(?<=\d)(?=[a-z])", " ", norm(s))
    out = []
    for t in s.split():
        t = ROMAN.get(t, t)
        if t not in STOP and (len(t) > 1 or t.isdigit()):
            out.append(t)
    return out


def _tok_match(x, y):
    return x == y or (len(x) >= 5 and len(y) >= 5 and (x[:5] == y[:5] or x in y or y in x))


def rank_decks(title, names, query="", limit=15):
    """Decks matching the plan name (without search text) or the search.
    Parent decks first, so a whole subject can be added with one click."""
    out = []
    if query.strip():
        want = tokens(query) or [norm(query)]
        for n in names:
            nt = tokens(n)
            if all(any(_tok_match(w, t) or t.startswith(w) for t in nt) for w in want):
                out.append((1.0, n))
    else:
        want = [t for t in dict.fromkeys(tokens(title)) if t not in GENERIC]
        if not want:
            return []
        for n in names:
            nt = tokens(n)
            hit = sum(1 for w in want if any(_tok_match(w, t) for t in nt))
            if hit:
                out.append((hit / len(want), n))
    out.sort(key=lambda x: (-x[0], x[1].count("::"), x[1].lower()))
    return [{"name": n, "score": round(sc, 2)} for sc, n in out[:limit]]


def similarity(a, b):
    na, nb = norm(a), norm(b)
    if not na or not nb:
        return 0.0
    if na == nb:
        return 1.0
    ta, tb = tokens(a), tokens(b)
    hit = 0
    for x in ta:
        if any(x == y or (len(x) >= 5 and len(y) >= 5 and (x[:5] == y[:5] or x in y or y in x)) for y in tb):
            hit += 1
    tok = hit / max(1, min(len(ta), len(tb))) if ta and tb else 0
    tok *= 0.6 + 0.4 * (min(len(ta), len(tb)) / max(len(ta), len(tb), 1))
    return max(tok, difflib.SequenceMatcher(None, na, nb).ratio() * 0.9)


def best_matches(name, candidates, key=lambda c: c, limit=3, threshold=0.55):
    scored = sorted(((similarity(name, key(c)), c) for c in candidates), key=lambda x: -x[0])
    return [(round(s, 2), c) for s, c in scored[:limit] if s >= threshold]


def suggest(plan, anki_candidates):
    """Suggestions per topic. anki_candidates: {source_id: [{label, query}]}.
    Returns {topic_id: {source_id: [ {score, label, query|video} ]}}."""
    out = {}
    for t in plan.get("topics", []):
        per = {}
        for src in plan.get("sources", []):
            if src["type"] == "anki":
                cands = anki_candidates.get(src["id"], [])
                m = best_matches(t["name"], cands, key=lambda c: c["label"].split("::")[-1])
                per[src["id"]] = [{"score": s, "label": c["label"], "query": c["query"]} for s, c in m]
            elif src["type"] in ("videos", "tasks"):
                lst = src.get(src["type"], [])
                m = best_matches(t["name"], lst, key=lambda v: v["name"], limit=4)
                per[src["id"]] = [{"score": s, "label": v["name"], "id": v["id"]} for s, v in m]
        out[t["id"]] = per
    return out


def apply_suggestions(plan, sugg):
    """Takes the best suggestion wherever nothing is assigned yet.
    Videos/tasks: all matches ≥ 0.7, each video for one topic only."""
    used = {(sid, v) for t in plan.get("topics", []) for key in ("videos", "tasks")
            for sid, vs in t.get(key, {}).items() for v in vs}
    srcs = {s["id"]: s for s in plan.get("sources", [])}
    changed = 0
    for t in plan.get("topics", []):
        for sid, lst in sugg.get(t["id"], {}).items():
            src = srcs.get(sid)
            if not src or not lst:
                continue
            if src["type"] == "anki":
                if not t.setdefault("anki", {}).get(sid):
                    t["anki"][sid] = lst[0]["query"]
                    changed += 1
            else:
                key = src["type"]
                cur = t.setdefault(key, {}).setdefault(sid, [])
                for m in lst:
                    if (m["score"] >= 0.7 or m is lst[0]) and (sid, m["id"]) not in used:
                        cur.append(m["id"])
                        used.add((sid, m["id"]))
                        changed += 1
    return changed


# --- Parsing input --------------------------------------------------------------

def parse_minutes(s):
    s = s.strip()
    m = re.fullmatch(r"(\d+):(\d{2})(?::(\d{2}))?", s)
    if m:
        h, mi, se = m.groups()
        total = int(h) * 60 + int(mi) + int(se) / 60 if se else int(h) + int(mi) / 60  # h:mm:ss or mm:ss
        return int(total + 0.5)
    m = re.fullmatch(r"(\d+(?:[.,]\d+)?)\s*(min|m|minuten|minutes|h|std)?", s.lower())
    if m:
        v = float(m.group(1).replace(",", "."))
        return round(v * 60) if m.group(2) in ("h", "std") else round(v)
    return None


def parse_list(text):
    """One video/task per line, optionally with duration and link:
    'Name | 25', 'Name (25 min)', 'Name 12:30', 'Name | 25 | https://…'."""
    out = []
    for line in text.splitlines():
        line = line.strip().lstrip("-•*").strip()
        url = None
        m = re.search(r"(?:https?|file)://\S+", line)
        if m:
            url = m.group(0)
            line = (line[:m.start()] + line[m.end():]).strip().rstrip("|;").strip()
        if not line:
            if url:
                line = url
            else:
                continue
        mins = None
        m = re.match(r"(.+?)\s*[|;\t]\s*([\d:.,]+\s*\w*)$", line) or \
            re.match(r"(.+?)\s*\(([\d:.,]+\s*(?:min|m|minuten|minutes|h|std)?)\)$", line, re.I) or \
            re.match(r"(.+?)\s+(\d{1,2}:\d{2}(?::\d{2})?)$", line)
        if m:
            mins = parse_minutes(m.group(2))
            if mins is not None:
                line = m.group(1).strip()
        item = {"name": line, "min": mins}
        if url:
            item["url"] = url
        out.append(item)
    return out


def parse_toc(text):
    """Table of contents: 'Inguinal canal ..... 78', '78 Inguinal canal', 'Inguinal canal 78–81'.
    A topic ends one page before the next one starts (unless given)."""
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(r"(.+?)[\s.·…_-]+(\d+)\s*(?:[-–—]\s*(\d+))?$", line)
        if m:
            rows.append([m.group(1).strip(" .-–"), int(m.group(2)), int(m.group(3)) if m.group(3) else None])
            continue
        m = re.match(r"(?:[SPp]\.?\s*)?(\d+)\s*(?:[-–—]\s*(\d+))?[\s.:)]+(.+)$", line)
        if m:
            rows.append([m.group(3).strip(), int(m.group(1)), int(m.group(2)) if m.group(2) else None])
    for j, r in enumerate(rows):
        if r[2] is None:
            nxt = rows[j + 1][1] if j + 1 < len(rows) else None
            r[2] = max(r[1], nxt - 1) if nxt and nxt > r[1] else r[1]
    return [{"name": n, "from": a, "to": b} for n, a, b in rows]


# --- Weak spots & retrospective -------------------------------------------------

def weak_items(plan, weak, limit=5):
    """Builds concrete items from weak spot data (weak: [{topic, agains, lapses, cards}])."""
    srcs = {s["id"]: s for s in plan.get("sources", [])}
    topics = {t["id"]: t for t in plan.get("topics", [])}
    items = []
    for w in weak[:limit]:
        t = topics.get(w["topic"])
        if not t:
            continue
        parts = []
        for sid, r in t.get("pages", {}).items():
            if r and sid in srcs:
                parts.append(tr(f"{srcs[sid]['name']} S. {r[0]}–{r[1]} nochmal lesen",
                                f"reread {srcs[sid]['name']} pp. {r[0]}–{r[1]}"))
        for sid, vs in t.get("videos", {}).items():
            names = [v["name"] for v in srcs.get(sid, {}).get("videos", []) if v["id"] in vs]
            if names:
                parts.append(tr(", ".join(names[:2]) + " nochmal anschauen", "rewatch " + ", ".join(names[:2])))
        parts.append(tr(f"{w['cards']} schwache Karten wiederholen", f"review {w['cards']} weak cards"))
        items.append({"id": new_id(), "kind": "weak", "topic": t["id"], "min": 30,
                      "text": tr(f"{t['name']}: {w['agains']} Fehler → ", f"{t['name']}: {w['agains']} mistakes → ")
                      + " + ".join(parts)})
    return items


def review_stats(plan, ev):
    """Retrospective: planned vs. done, on time vs. late, per source."""
    srcs = {s["id"]: s for s in plan.get("sources", [])}
    per = {}
    late_days = set()
    planned = done = on_time = 0
    for day, it in all_items(plan):
        if it.get("kind") in NO_CHECK or it.get("moved") or it.get("kind") == "reviews":
            continue
        planned += 1
        name = srcs[it["source"]]["name"] if it.get("source") in srcs else (
            tr("Eigene Punkte", "Custom items") if it.get("custom") else tr("Sonstiges", "Other"))
        p = per.setdefault(name, {"planned": 0, "done": 0, "min": 0, "late": 0})
        p["planned"] += 1
        stamp = plan.get("done", {}).get(it["id"]) or plan.get("autoDone", {}).get(it["id"])
        if is_done(plan, it, ev):
            done += 1
            p["done"] += 1
            p["min"] += it.get("min", 0)
            if stamp and stamp[:10] > day["d"]:
                p["late"] += 1
                late_days.add(day["d"])
            else:
                on_time += 1
    moved = sum(1 for _, it in all_items(plan) if it.get("moved"))
    return {"planned": planned, "done": done, "onTime": on_time, "moved": moved,
            "lateDays": len(late_days), "perSource": per}


def streak(active_days, today):
    """active_days: set of ISO dates with study activity. Today counts if active;
    otherwise the streak counts up to yesterday (the day isn't over yet)."""
    d = s2d(today)
    if d2s(d) not in active_days:
        d -= timedelta(days=1)
    n = 0
    while d2s(d) in active_days:
        n += 1
        d -= timedelta(days=1)
    return n
