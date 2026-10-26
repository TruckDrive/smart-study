# Planungslogik ohne Anki-Abhängigkeit (testbar mit plain Python).
# Ein Plan besteht aus Quellen (Seiten, Videos, Aufgaben, Anki-Decks) und Themen,
# die Teile dieser Quellen bündeln. build() verteilt alles, was noch offen ist,
# auf die Tage bis zur Prüfung; Erledigtes und eigene Punkte bleiben erhalten.
import difflib
import random
import re
import unicodedata
from datetime import date, datetime, timedelta

DEFAULT_RATES = {"pages": 6.0, "videos": 20.0, "tasks": 30.0, "anki": 1.0}  # Minuten pro Einheit
NO_CHECK = ("note", "weakround", "sim")  # Punkte ohne Häkchen-Pflicht


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


def all_items(plan):
    for day in plan.get("days", []):
        for it in day["items"]:
            yield day, it


def anki_sources(plan):
    return [s for s in plan.get("sources", []) if s["type"] == "anki"]


def deck_query(name):
    return 'deck:"%s"' % name.replace('"', '\\"')


def rest_query(plan, src):
    """Karten des Decks, die keinem Thema zugeordnet sind."""
    qs = [t["anki"][src["id"]] for t in plan.get("topics", []) if t.get("anki", {}).get(src["id"])]
    base = deck_query(src["deck"])
    return base if not qs else f"{base} -({' OR '.join('(' + q + ')' for q in qs)})"


def topic_query(plan, topic, src):
    q = topic.get("anki", {}).get(src["id"])
    return f"{deck_query(src['deck'])} ({q})" if q else None


def queries(plan):
    """Alle Anki-Suchen, deren Zahlen build() und evaluate() brauchen."""
    out = set()
    for src in anki_sources(plan):
        out.add(deck_query(src["deck"]))
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
    """Etappen (z. B. Testate) nach Datum; die Prüfung selbst ist immer die letzte."""
    ms = sorted((m for m in plan.get("milestones", []) if m.get("date") and m["date"] < plan["exam"]),
                key=lambda m: m["date"])
    return ms + [{"id": None, "name": "Prüfung", "date": plan["exam"], "time": plan.get("examTime", ""), "final": True}]


def ordered_topics(plan):
    """Automatisch: nach Termin der Etappe, dann nach Seite. Sonst wie in der Liste."""
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
    """Liste der noch offenen Arbeitseinheiten in Lernreihenfolge."""
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
            if q and counts.get(q, {}).get("new"):
                units.append({"kind": "cards", "topic": t["id"], "source": src["id"], "query": q,
                              "n": counts[q]["new"], "cost": rate(src), "split": True,
                              "seen": counts[q]["total"] - counts[q]["new"]})
    # Unverplante Videos/Aufgaben (keinem Thema zugeordnet) und Anki-Rest zum Schluss
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
        if counts.get(q, {}).get("new"):
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


def build(plan, counts, today, ev=None):
    """(Neu-)Planung ab heute. Vergangene Tage bleiben als Verlauf stehen; offene
    Punkte von dort werden als 'verschoben' markiert und neu verteilt.
    counts: {query: {"total", "new"}}; ev: Ergebnis von evaluate() (Auto-Häkchen).
    Gibt eine Liste von Hinweisen zurück (z. B. Überlastung)."""
    ev = ev or {}
    exam = s2d(plan["exam"])
    start = max(today, s2d(plan["start"]))
    if start > exam:
        plan["notes"] = ["Die Prüfung ist schon vorbei – nichts mehr zu verteilen."]
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
                        carry.append(it)  # eigener Punkt wandert mit
                        continue
                    it["moved"] = True
                keep.append(it)
            elif done or it.get("custom"):
                keep.append(it)
        day["items"] = keep
    for d in daterange(start, exam):
        days.setdefault(d2s(d), {"d": d2s(d), "items": []})
    days[d2s(start)]["items"][0:0] = carry

    # Etappen: jedes Testat bekommt ein eigenes Zeitfenster bis zu seinem Termin.
    # Stoff eines vergangenen Testats wird nicht mehr eingeplant.
    ms = milestones(plan)
    ms_open = [m for m in ms if s2d(m["date"]) >= start]
    ms_date = {m["id"]: m["date"] for m in ms if m["id"]}
    units = []
    groups = [[] for _ in ms_open]
    for u in remaining_work(plan, counts, ev):
        t = topics.get(u["topic"])
        due = ms_date.get(t.get("milestone")) if t else None
        due = due or plan["exam"]
        if due < d2s(start):
            continue
        j = next(j for j, m in enumerate(ms_open) if m["date"] >= due)
        groups[j].append(u)
        units.append(u)

    used_today = sum(it.get("min", 0) for it in days[d2s(start)]["items"]
                     if is_done(plan, it, ev) and it.get("kind") != "reviews")
    has_anki = bool(anki_sources(plan))
    generated, reserve_map = {}, {}
    new_per_day, seen_so_far = {}, {}
    notes = []
    multi = len(ms_open) > 1

    def fill(units, content, cap, m):
        budget_total = sum(cap)
        work = sum(u["n"] * u["cost"] for u in units)
        label = "zur Prüfung" if m.get("final") else f"zu „{m['name']}“"
        if work > budget_total * 1.02:
            notes.append(f"Bis {label} ist der Plan zu voll: {round((work - budget_total) / 60, 1)} h mehr Stoff als Lernzeit. "
                         "Mehr Zeit pro Tag eintragen oder Stoff streichen.")
        scale = work / budget_total if budget_total else 0
        budget = [c * scale for c in cap]
        st = {"i": 0, "rem": budget[0] if budget else 0}

        def next_day():
            if st["i"] < len(content) - 1:
                st["i"] += 1
                st["rem"] = budget[st["i"]]
                return True
            return False

        def emit(u, k):
            t = topics.get(u["topic"])
            tname = t["name"] if t else None
            src = srcs[u["source"]]
            day = d2s(content[st["i"]])
            it = {"id": new_id(), "kind": u["kind"], "topic": u["topic"], "source": u["source"], "min": round(k * u["cost"])}
            if multi:
                it["for"] = "Prüfung" if m.get("final") else m["name"]
            if u["kind"] == "pages":
                a = u["from"]
                it["pages"] = [a, a + k - 1]
                rng = f"S. {a}" if k == 1 else f"S. {a}–{a + k - 1}"
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
                it["text"] = f"{k} neue Karten" + (f" · {tname}" if tname else " · übrige Karten")
                new_per_day[(day, u["source"])] = new_per_day.get((day, u["source"]), 0) + k
            generated.setdefault(day, []).append(it)
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
                    if st["rem"] < u["cost"] * 0.5 and st["rem"] < budget[st["i"]] and next_day():
                        continue
                    emit(u, 1)
                    if st["rem"] <= 0:
                        next_day()

    prev = start - timedelta(days=1)
    for j, m in enumerate(ms_open):
        deadline = s2d(m["date"])
        avail = [d for d in daterange(prev + timedelta(days=1), deadline - timedelta(days=1)) if capacity(plan, d) > 0]
        r = reserve_count(len(avail)) if m.get("final") else (1 if len(avail) >= 3 else 0)
        content, reserve = avail[:len(avail) - r], avail[len(avail) - r:]
        if not content:
            content, reserve = avail, []
        for k, d in enumerate(reserve):
            reserve_map[d2s(d)] = reserve_items(plan, k, len(reserve)) if m.get("final") else [
                {"id": new_id(), "kind": "note", "text": f"Wiederholen für „{m['name']}“: Themen dieser Etappe laut erklären, "
                                                         "Schwachstellen anschauen, nichts Neues."}]
        if groups[j] and not content:
            if j + 1 < len(ms_open):
                notes.append(f"Vor „{m['name']}“ ist keine Lernzeit mehr – der Stoff dafür rutscht in die nächste Etappe.")
                groups[j + 1][0:0] = groups[j]
            else:
                notes.append("Bis zur Prüfung ist keine Lernzeit mehr eingetragen.")
        elif groups[j]:
            cap = [max(0, capacity(plan, d) - (used_today if d == start else 0)) for d in content]
            fill(groups[j], content, cap, m)
        prev = deadline
    lim = {s["id"]: s.get("maxNew") for s in anki_sources(plan)}
    if any(lim.get(sid) and n > int(lim[sid]) for (_, sid), n in new_per_day.items()):
        notes.append("Das Tageslimit für neue Karten reicht nicht; am letzten Lerntag vor einem Termin liegen mehr neue Karten.")

    # Tage zusammensetzen: Wiederholungen zuerst, dann der Stoff
    by_date = {m["date"]: m for m in ms_open}
    for d in daterange(start, exam):
        s = d2s(d)
        items = days[s]["items"]
        gen = reserve_map.get(s) or generated.get(s, [])
        m = by_date.get(s)
        if m:
            when = f" um {m['time']}" if m.get("time") else ""
            gen = [{"id": new_id(), "kind": "note", "text": f"Prüfung{when}: nur leicht wiederholen, vorher etwas essen."
                    if m.get("final") else f"{m['name']}{when}: vorher kurz wiederholen. Viel Erfolg!"}]
        if has_anki and (capacity(plan, d) > 0 or m) and not any(x.get("kind") == "reviews" for x in items):
            gen.insert(0, {"id": new_id(), "kind": "reviews", "text": "Fällige Wiederholungen", "auto": {"type": "reviews"}})
        days[s]["items"] = items + [g for g in gen if not any(x.get("kind") == g["kind"] and g["kind"] in NO_CHECK
                                                              for x in items)]
    plan["days"] = [days[k] for k in sorted(days)]
    plan["generatedAt"] = datetime.now().isoformat(timespec="minutes")
    plan["notes"] = notes
    return notes


def reserve_items(plan, ix, n):
    """Reservetage vor der Prüfung: Schwachstellen → Probeprüfung → Wiederholen."""
    kinds = {3: ["weakround", "sim", "final"], 2: ["sim", "final"], 1: ["final"]}[n]
    kind = kinds[ix]
    if kind == "weakround":
        return [{"id": new_id(), "kind": "weakround", "text": "Schwachstellen-Runde: die schwächsten Themen gezielt wiederholen"}]
    if kind == "sim":
        return [{"id": new_id(), "kind": "sim", "text": "Probeprüfung: gemischte Karten auf Zeit + zufällige Themen frei erklären"}]
    return [{"id": new_id(), "kind": "note", "text": "Letzter Tag: nur wiederholen, Schwachstellen kurz anschauen, nichts Neues. Früh schlafen."}]


def evaluate(plan, st):
    """Auto-Häkchen aus Anki-Daten. st: {today, due, rated:{day:n}, counts:{q:{total,new}}}."""
    out = {}
    for day, it in all_items(plan):
        a = it.get("auto")
        if not a or not st:
            continue
        if a["type"] == "reviews":
            n = st["rated"].get(day["d"], 0)
            if day["d"] < st["today"]:
                out[it["id"]] = {"done": n > 0, "text": "erledigt" if n else "nicht gemacht"}
            elif day["d"] == st["today"]:
                out[it["id"]] = {"done": st["due"] == 0, "text": "alles erledigt" if st["due"] == 0 else f"noch {st['due']} fällig"}
        elif a["type"] == "seen":
            c = st["counts"].get(a["query"])
            if not c:
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


# --- Zuordnung Themen <-> Unterdecks/Tags/Videos ---------------------------------

def norm(s):
    s = s.lower().replace("ß", "ss")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


STOP = {"und", "der", "die", "das", "des", "mit", "von", "im", "in", "teil", "the", "and", "of", "a", "m", "a"}


def tokens(s):
    return [t for t in norm(s).split() if t not in STOP and len(t) > 1]


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
    """Vorschläge pro Thema. anki_candidates: {source_id: [{label, query}]}.
    Gibt {topic_id: {source_id: [ {score, label, query|video} ]}} zurück."""
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
    """Übernimmt den besten Vorschlag überall, wo noch nichts zugeordnet ist.
    Videos/Aufgaben: alle Treffer ≥ 0.7, jedes Video nur bei einem Thema."""
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


# --- Eingaben parsen ------------------------------------------------------------

def parse_minutes(s):
    s = s.strip()
    m = re.fullmatch(r"(\d+):(\d{2})(?::(\d{2}))?", s)
    if m:
        h, mi, se = m.groups()
        total = int(h) * 60 + int(mi) + int(se) / 60 if se else int(h) + int(mi) / 60  # h:mm:ss oder mm:ss
        return int(total + 0.5)
    m = re.fullmatch(r"(\d+(?:[.,]\d+)?)\s*(min|m|minuten|h|std)?", s.lower())
    if m:
        v = float(m.group(1).replace(",", "."))
        return round(v * 60) if m.group(2) in ("h", "std") else round(v)
    return None


def parse_list(text):
    """Eine Zeile pro Video/Aufgabe, optional Dauer und Link:
    'Name | 25', 'Name (25 min)', 'Name 12:30', 'Name | 25 | https://…'."""
    out = []
    for line in text.splitlines():
        line = line.strip().lstrip("-•*").strip()
        url = None
        m = re.search(r"https?://\S+", line)
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
            re.match(r"(.+?)\s*\(([\d:.,]+\s*(?:min|m|minuten|h|std)?)\)$", line, re.I) or \
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
    """Inhaltsverzeichnis: 'Leistenkanal ..... 78', '78 Leistenkanal', 'Leistenkanal 78–81'.
    Ende eines Themas = Anfang des nächsten − 1 (wenn nicht angegeben)."""
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(r"(.+?)[\s.·…_-]+(\d+)\s*(?:[-–—]\s*(\d+))?$", line)
        if m:
            rows.append([m.group(1).strip(" .-–"), int(m.group(2)), int(m.group(3)) if m.group(3) else None])
            continue
        m = re.match(r"(?:S\.?\s*)?(\d+)\s*(?:[-–—]\s*(\d+))?[\s.:)]+(.+)$", line)
        if m:
            rows.append([m.group(3).strip(), int(m.group(1)), int(m.group(2)) if m.group(2) else None])
    for j, r in enumerate(rows):
        if r[2] is None:
            nxt = rows[j + 1][1] if j + 1 < len(rows) else None
            r[2] = max(r[1], nxt - 1) if nxt and nxt > r[1] else r[1]
    return [{"name": n, "from": a, "to": b} for n, a, b in rows]


# --- Schwachstellen & Rückblick --------------------------------------------------

def weak_items(plan, weak, limit=5):
    """Aus Schwachstellen-Daten (weak: [{topic, agains, lapses, cards}]) konkrete Punkte bauen."""
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
                parts.append(f"{srcs[sid]['name']} S. {r[0]}–{r[1]} nochmal lesen")
        for sid, vs in t.get("videos", {}).items():
            names = [v["name"] for v in srcs.get(sid, {}).get("videos", []) if v["id"] in vs]
            if names:
                parts.append(", ".join(names[:2]) + " nochmal anschauen")
        parts.append(f"{w['cards']} schwache Karten wiederholen")
        items.append({"id": new_id(), "kind": "weak", "topic": t["id"], "min": 30,
                      "text": f"{t['name']}: {w['agains']} Fehler → " + " + ".join(parts)})
    return items


def review_stats(plan, ev):
    """Rückblick: geplant vs. geschafft, pünktlich vs. verspätet, pro Quelle."""
    srcs = {s["id"]: s for s in plan.get("sources", [])}
    per = {}
    late_days = set()
    planned = done = on_time = 0
    for day, it in all_items(plan):
        if it.get("kind") in NO_CHECK or it.get("moved") or it.get("kind") == "reviews":
            continue
        planned += 1
        name = srcs[it["source"]]["name"] if it.get("source") in srcs else ("Eigene Punkte" if it.get("custom") else "Sonstiges")
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
    """active_days: Menge von ISO-Daten mit Lernaktivität. Heute zählt, wenn aktiv;
    sonst zählt die Serie bis gestern (der Tag ist ja noch nicht vorbei)."""
    d = s2d(today)
    if d2s(d) not in active_days:
        d -= timedelta(days=1)
    n = 0
    while d2s(d) in active_days:
        n += 1
        d -= timedelta(days=1)
    return n
