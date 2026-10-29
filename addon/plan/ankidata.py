# Everything that reads data from the Anki collection or creates decks.
# Functions take the collection as an argument (in Anki: mw.col) so they
# also work with a test collection.
import html
import random
import re
from datetime import date, datetime, timedelta

from anki.utils import ids2str

from . import planner
from .planner import tr

FILTER_PREFIX = "Smart Study"


def today(col):
    """Anki day (day rollover as set in preferences, usually 4 am)."""
    return (datetime.fromtimestamp(col.sched.day_cutoff) - timedelta(days=1)).date()


def day_of(col, ms):
    """Anki date of a revlog timestamp (ms)."""
    ago = (col.sched.day_cutoff - 1 - ms // 1000) // 86400
    return today(col) - timedelta(days=int(ago))


def day_start_ms(col, d):
    return (col.sched.day_cutoff - 86400 * ((today(col) - d).days + 1)) * 1000


def deck_names(col):
    return sorted(d.name for d in col.decks.all_names_and_ids() if not col.decks.is_filtered(d.id))


def counts(col, qs):
    out = {}
    for q in qs:
        try:
            ids = col.find_cards(q)
            new = col.find_cards(f"({q}) is:new -is:suspended") if ids else []
            out[q] = {"total": len(ids), "new": len(new)}
        except Exception:  # invalid search (e.g. deleted deck)
            out[q] = {"total": 0, "new": 0, "error": True}
    return out


def plan_query(plan):
    qs = [planner.src_query(s) for s in planner.anki_sources(plan) if planner.src_query(s)]
    return "(" + " OR ".join(qs) + ")" if qs else None


def stats(col, plan):
    """Numbers for evaluate(): due, ratings per day, counts per search."""
    q = plan_query(plan)
    t = today(col)
    st = {"today": t.isoformat(), "due": 0, "rated": {}, "counts": {}, "decks": {}}
    if not q:
        return st
    rq = planner.review_query(plan, t.isoformat())
    st["due"] = len(col.find_cards(f"{rq} is:due -is:suspended -is:buried")) if rq else 0
    st["counts"] = counts(col, planner.queries(plan))
    for s in planner.anki_sources(plan):
        if planner.src_query(s):
            st["decks"][s["id"]] = st["counts"].get(planner.src_query(s), {"total": 0, "new": 0})
    start = min(planner.s2d(plan["start"]), t)
    cids = col.find_cards(q)
    if cids:
        for ms, in col.db.all(f"select id from revlog where id >= ? and ease > 0 and cid in {ids2str(cids)}",
                              day_start_ms(col, start)):
            k = day_of(col, ms).isoformat()
            st["rated"][k] = st["rated"].get(k, 0) + 1
    return st


def candidates(col, decks):
    """Subdecks and tags of a source's decks as possible topic links."""
    if isinstance(decks, str):
        decks = [decks]
    out = []
    for deck in decks:
        did = col.decks.id_for_name(deck)
        if not did:
            continue
        pre = deck.split("::")[-1] + " › " if len(decks) > 1 else ""
        for name, _ in col.decks.children(did):
            out.append({"label": pre + (name[len(deck) + 2:] or name), "query": planner.deck_query(name), "kind": "deck"})
    if not decks:
        return out
    tags = set()
    cids = col.find_cards(" OR ".join(planner.deck_query(d) for d in decks))
    if cids:
        for tagstr, in col.db.all(f"select distinct n.tags from notes n join cards c on c.nid = n.id where c.id in {ids2str(cids)}"):
            tags.update(tagstr.split())
    for tg in sorted(tags, key=str.lower):
        out.append({"label": "#" + tg.split("::")[-1] if "::" in tg else "#" + tg, "query": 'tag:"%s"' % tg,
                    "kind": "tag", "full": tg})
    return out


def deck_info(col, deck):
    did = col.decks.id_for_name(deck)
    if not did:
        return None
    q = planner.deck_query(deck)
    c = counts(col, [q])[q]
    conf = col.decks.config_dict_for_deck_id(did)
    kids = [n[len(deck) + 2:] for n, _ in col.decks.children(did) if n.count("::") == deck.count("::") + 1]
    return {"deck": deck, "total": c["total"], "new": c["new"], "perDay": conf.get("new", {}).get("perDay"),
            "children": kids}


def weak(col, plan):
    """Per topic: mistakes (Again) since the plan started, lapses, number of weak cards."""
    since = day_start_ms(col, min(planner.s2d(plan["start"]), today(col)))
    out = []
    for t in plan.get("topics", []):
        cids = set()
        for src in planner.anki_sources(plan):
            q = planner.topic_query(plan, t, src)
            if q:
                try:
                    cids.update(col.find_cards(q))
                except Exception:
                    pass
        if not cids:
            continue
        s = ids2str(cids)
        again = dict(col.db.all(f"select cid, count() from revlog where ease = 1 and id >= ? and cid in {s} group by cid", since))
        lapses = dict(col.db.all(f"select id, lapses from cards where id in {s}"))
        weak_cards = [c for c in cids if again.get(c, 0) >= 2 or lapses.get(c, 0) >= 3]
        n_again = sum(again.values())
        if n_again or weak_cards:
            out.append({"topic": t["id"], "name": t["name"], "agains": n_again,
                        "lapses": sum(lapses.values()), "cards": len(weak_cards),
                        "score": n_again + len(weak_cards) * 2})
    out.sort(key=lambda w: -w["score"])
    return out


def weak_search(col, plan, topic_ids=None):
    days = (today(col) - planner.s2d(plan["start"])).days + 1
    parts = []
    for t in plan.get("topics", []):
        if topic_ids and t["id"] not in topic_ids:
            continue
        for src in planner.anki_sources(plan):
            q = planner.topic_query(plan, t, src)
            if q:
                parts.append(f"({q})")
    base = f"({' OR '.join(parts)})" if parts else plan_query(plan)
    if not base:
        return None
    return f"{base} -is:new -is:suspended (prop:lapses>=3 OR rated:{max(1, min(days, 365))}:1)"


def study_target(col, plan, item):
    """Where "▶ study" leads: the topic's subdeck if it has one, otherwise the source's deck.
    No filtered deck is created, so the cards stay in their normal decks."""
    tq = ""
    if item.get("kind") != "reviews":
        topic = next((t for t in plan.get("topics", []) if t["id"] == item.get("topic")), None)
        tq = (topic or {}).get("anki", {}).get(item.get("source"), "")
    src = next(iter(planner.anki_sources(plan)), None) if item.get("kind") == "reviews" else \
        next((s for s in planner.anki_sources(plan) if s["id"] == item.get("source")), None)
    m = re.fullmatch(r'deck:"((?:[^"\\]|\\.)+)"', tq.strip())
    name = m.group(1).replace('\\"', '"') if m else next(iter(planner.src_decks(src)), None) if src else None
    did = col.decks.id_for_name(name) if name else None
    return (did, None) if did else (None, 0)


def mock_cards(col, plan, n):
    """Random, already studied cards from the plan decks. They are shown in the add-on,
    so no card is moved anywhere."""
    q = plan_query(plan)
    cids = col.find_cards(f"{q} -is:new -is:suspended -is:buried") if q else []
    out = []
    for cid in random.sample(cids, min(n, len(cids))):
        card = col.get_card(cid)
        out.append({"cid": cid, "q": _plain(card.question()), "a": _plain(card.answer().split("<hr id=answer>")[-1])})
    return out


def _plain(page):
    text = re.sub(r"<style.*?</style>|<script.*?</script>", "", page, flags=re.S)
    text = re.sub(r"<br\s*/?>|</div>|</p>", "\n", text)
    return html.unescape(re.sub(r"<[^>]+>", "", text)).strip()


def sim_result(col, plan, sim):
    """Right/wrong answers of the mock exam as marked in the add-on, split by topic."""
    cids = sim.get("cards") or []
    if not cids:
        return None
    answers = {int(k): bool(v) for k, v in (sim.get("answers") or {}).items()}
    per = []
    for t in plan.get("topics", []):
        ids = set()
        for src in planner.anki_sources(plan):
            q = planner.topic_query(plan, t, src)
            if q:
                ids.update(col.find_cards(q))
        hit = [c for c in answers if c in ids]
        if hit:
            per.append({"name": t["name"], "n": len(hit), "ok": sum(1 for c in hit if answers[c])})
    per.sort(key=lambda p: p["ok"] / p["n"])
    return {"total": len(cids), "answered": len(answers), "ok": sum(answers.values()), "topics": per}


def forecast(col, plan):
    """Due reviews per day from today (negative = overdue) and minutes per review.
    Only cards and periods according to planner.review_scopes()."""
    t = today(col)
    due, seen = {}, set()
    for q, frm, until in planner.review_scopes(plan):
        cids = [c for c in col.find_cards(f"({q}) -is:new -is:suspended -is:buried") if c not in seen]
        seen.update(cids)
        last = (planner.s2d(until) - t).days
        first = (planner.s2d(frm) - t).days if frm else None
        for queue, d in col.db.all(f"select queue, due from cards where id in {ids2str(cids)} and queue in (1, 2, 3)"):
            k = 0 if queue == 1 else d - col.sched.today  # queue 1: learning step, due is a timestamp from today
            if first is not None and first > 0 and k < first:
                k = first  # no reviews before – the card is due on that day then
            if max(k, 0) > last:
                continue
            due[k] = due.get(k, 0) + 1
    since = day_start_ms(col, t - timedelta(days=30))

    def per_review(where):
        n, ms = col.db.first(f"select count(), coalesce(sum(min(time, 60000)), 0) from revlog "
                             f"where type = 1 and id >= ? {where}", since)
        return ms / 60000 / n if n >= 50 else None

    m = (seen and per_review(f"and cid in {ids2str(seen)}")) or per_review("") or planner.REVIEW_MIN
    return {"due": due, "min": round(m, 2)}


def time_stats(col, plan):
    """Actual Anki time since the plan started and minutes per new card from that."""
    q = plan_query(plan)
    if not q:
        return None
    cids = col.find_cards(q)
    if not cids:
        return None
    since = day_start_ms(col, planner.s2d(plan["start"]))
    s = ids2str(cids)
    secs = col.db.scalar(f"select coalesce(sum(time), 0) from revlog where id >= ? and cid in {s}", since) / 1000
    introduced = col.db.scalar(
        f"select count() from (select cid, min(id) m from revlog where ease > 0 and cid in {s} group by cid) where m >= ?", since)
    return {"minutes": round(secs / 60), "newCards": introduced,
            "minPerNew": round(secs / 60 / introduced, 2) if introduced else None}


def activity(col, days=371):
    """Ratings per day across the whole collection (for heatmap and streak)."""
    t = today(col)
    out = {}
    for ms, in col.db.all("select id from revlog where id >= ? and ease > 0", day_start_ms(col, t - timedelta(days=days))):
        k = day_of(col, ms).isoformat()
        out[k] = out.get(k, 0) + 1
    return out


def find_decks(col, title, query, exclude=()):
    """Deck suggestions (by plan name) or search results, with card counts."""
    names = [n for n in deck_names(col) if n not in exclude]
    out = planner.rank_decks(title, names, query)
    for r in out:
        q = planner.deck_query(r["name"])
        r["total"] = len(col.find_cards(q))
        r["new"] = len(col.find_cards(f"{q} is:new -is:suspended")) if r["total"] else 0
    return out


def plan_dids(col, plan):
    dids = []
    for s in planner.anki_sources(plan):
        for deck in planner.src_decks(s):
            did = col.decks.id_for_name(deck)
            if did:
                dids.append(did)
                dids.extend(d for _, d in col.decks.children(did))
    return list(dict.fromkeys(dids))


def maintenance(col, plan, on):
    """Maintenance mode: own options preset (0 new, max. 50 reviews/day) for the plan's
    decks. The previous presets are remembered and restored when switching it off."""
    m = plan.setdefault("maintenance", {})
    if on:
        if m.get("on"):
            return m
        name = tr(f"{FILTER_PREFIX} · Erhaltung ({plan['title']})", f"{FILTER_PREFIX} · Maintenance ({plan['title']})")
        conf = next((c for c in col.decks.all_config() if c["name"] == name), None)
        if not conf:
            first = plan_dids(col, plan)
            base = col.decks.config_dict_for_deck_id(first[0]) if first else None
            conf = col.decks.get_config(col.decks.add_config_returning_id(name, base))
        conf["new"]["perDay"] = 0
        conf["rev"]["perDay"] = int(m.get("reviewsPerDay", 50))
        col.decks.update_config(conf)
        prev = {}
        for did in plan_dids(col, plan):
            d = col.decks.get(did)
            if d and not d.get("dyn"):
                prev[str(did)] = d["conf"]
                d["conf"] = conf["id"]
                col.decks.save(d)
        m.update(on=True, conf=conf["id"], previous=prev)
    else:
        for did, conf_id in m.get("previous", {}).items():
            d = col.decks.get(int(did), default=False)
            if d and col.decks.get_config(conf_id):
                d["conf"] = conf_id
                col.decks.save(d)
        m.update(on=False, previous={})
    return m
