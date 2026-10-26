// Oberfläche des Lernplans. Daten kommen über pycmd("lp:{cmd,args}") aus Python.
(() => {
"use strict";

// ---------- Helfer ----------
const WD = ["So", "Mo", "Di", "Mi", "Do", "Fr", "Sa"];
const WD_MO = [["Mo", 0], ["Di", 1], ["Mi", 2], ["Do", 3], ["Fr", 4], ["Sa", 5], ["So", 6]]; // Python-Wochentage
const TYPES = { pages: "Seiten", videos: "Videos", tasks: "Aufgaben", anki: "Anki" };
const UNIT = { pages: "min/Seite", videos: "min/Video", tasks: "min/Aufgabe", anki: "min/neue Karte" };

function h(tag, attrs, ...kids) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v == null || v === false) continue;
    if (k === "class") e.className = v;
    else if (k.startsWith("on")) e.addEventListener(k.slice(2), v);
    else if (k === "value") e.value = v;
    else if (k === "checked") e.checked = !!v;
    else e.setAttribute(k, v === true ? "" : v);
  }
  for (const c of kids.flat(9)) if (c != null && c !== false) e.append(c.nodeType ? c : String(c));
  return e;
}
const dt = s => new Date(s + "T12:00:00");
const fmt = s => { const d = dt(s); return `${WD[d.getDay()]} ${d.getDate()}.${d.getMonth() + 1}.`; };
const daysBetween = (a, b) => Math.round((dt(b) - dt(a)) / 864e5);
const addDays = (s, n) => { const d = dt(s); d.setDate(d.getDate() + n); return iso(d); };
const iso = d => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
const uid = p => p + Math.random().toString(16).slice(2, 12);
const clone = o => JSON.parse(JSON.stringify(o));
const hm = m => m >= 60 ? `${Math.floor(m / 60)} h${m % 60 ? " " + (m % 60) + " min" : ""}` : `${m} min`;

function call(cmd, args) {
  return new Promise((res, rej) => {
    const go = () => pycmd("lp:" + JSON.stringify({ cmd, args }), r => r && r.ok ? res(r.data) : rej(new Error(r ? r.error : "keine Antwort")));
    if (typeof pycmd === "function") go();
    else { const t = setInterval(() => { if (typeof pycmd === "function") { clearInterval(t); go(); } }, 30); }
  });
}
function toast(msg, ms = 2600) {
  const t = h("div", { class: "toast" }, msg);
  document.body.append(t);
  setTimeout(() => t.remove(), ms);
}
async function run(p) { try { return await p; } catch (e) { toast("Fehler: " + e.message, 5000); throw e; } }
function modal(title, body, buttons) {
  return new Promise(res => {
    const bg = h("div", { class: "modal-bg" });
    const close = v => { bg.remove(); res(v); };
    bg.append(h("div", { class: "modal" }, h("h2", null, title), h("div", { style: "margin-top:10px" }, body),
      h("div", { class: "foot" }, (buttons || [["Abbrechen", null], ["OK", true, "primary"]]).map(([l, v, c]) => h("button", { class: c, onclick: () => close(typeof v === "function" ? v() : v) }, l)))));
    bg.addEventListener("click", e => { if (e.target === bg) close(null); });
    document.body.append(bg);
    const f = bg.querySelector("input,textarea,select"); if (f) f.focus();
  });
}
const store = {
  get(k) { try { return JSON.parse(localStorage.getItem("lp." + k)); } catch { return null; } },
  set(k, v) { try { localStorage.setItem("lp." + k, JSON.stringify(v)); } catch {} },
};

// ---------- Zustand ----------
const S = { view: "home", pid: null, data: null, edit: null, showPast: false, simTimer: null, cands: {}, sugg: {} };
const app = () => document.getElementById("app");

async function go(view, pid) {
  S.view = view; if (pid !== undefined) S.pid = pid;
  if (view === "home") S.data = await run(call("home"));
  if (view === "plan") S.data = await run(call("open", { id: S.pid }));
  if (view === "edit") {
    const d = await run(call("open", { id: S.pid }));
    S.edit = clone(d.plan); S.decks = await call("decks"); S.cands = {}; S.sugg = {};
    await loadCands();
  }
  if (view === "review") S.data = await run(call("review", { id: S.pid }));
  render();
  window.scrollTo(0, 0);
}
async function refresh() {
  if (S.view === "plan") { S.data = await call("open", { id: S.pid }); const y = window.scrollY; render(); window.scrollTo(0, y); }
  else if (S.view === "home") { S.data = await call("home"); render(); }
}
window.LP = { refresh, go };

function render() {
  const root = app();
  root.replaceChildren();
  ({ home: renderHome, plan: renderPlan, edit: renderEdit, review: renderReview })[S.view](root);
}

// ---------- Übersicht ----------
function renderHome(root) {
  const d = S.data;
  root.append(h("div", { class: "top" },
    h("div", null, h("h1", null, "Lernplan"), h("p", { class: "sub" }, "Pläne bis zur Prüfung – Anki hakt sich selbst ab.")),
    h("button", { class: "primary", onclick: () => newPlan() }, "+ Neuer Plan")));

  const tiles = h("div", { class: "tiles" },
    tile("Lern-Serie", String(d.streak), null, d.streak === 1 ? "Tag" : "Tage"),
    tile("Aktive Pläne", String(d.plans.filter(p => p.status === "active").length)));
  root.append(tiles, heatmap(d.heat, d.today));

  const act = d.plans.filter(p => p.status === "active"), arch = d.plans.filter(p => p.status !== "active");
  root.append(h("h3", null, "Aktiv"));
  if (!act.length) root.append(h("div", { class: "card muted" }, "Noch kein Plan. Leg mit „+ Neuer Plan“ los."));
  root.append(h("div", { class: "plans" }, act.map(planCard)));
  if (arch.length) {
    root.append(h("details", null, h("summary", null, `Archiv (${arch.length})`), h("div", { class: "plans" }, arch.map(planCard))));
  }
  root.append(h("p", { class: "muted small", style: "margin-top:30px" }, `Lernplan ${d.version} · Pläne liegen im Add-on-Ordner unter user_files/plans.`));
}
function planCard(p) {
  const left = daysBetween(S.data.today, p.exam), [dn, tot] = p.progress;
  return h("div", { class: "card plan-card", onclick: () => go("plan", p.id) },
    h("div", { class: "days-left" }, left > 0 ? String(left) : left === 0 ? "heute" : "✓", h("small", null, left > 0 ? (left === 1 ? "Tag" : "Tage") : left === 0 ? "Prüfung" : "vorbei")),
    h("div", { class: "grow" }, h("h2", null, p.title), h("div", { class: "muted small" }, `Prüfung ${fmt(p.exam)} · ${dn}/${tot} erledigt`),
      h("div", { class: "pbar" + (tot && dn === tot ? " ok" : "") }, h("i", { style: `width:${tot ? 100 * dn / tot : 0}%` }))));
}
function heatmap(heat, today) {
  const vals = Object.values(heat).filter(v => v > 0).sort((a, b) => a - b);
  const q = f => vals.length ? vals[Math.floor((vals.length - 1) * f)] : 1;
  const lv = v => !v ? "" : v <= q(.25) ? "l1" : v <= q(.5) ? "l2" : v <= q(.8) ? "l3" : "l4";
  const end = dt(today), start = new Date(end); start.setDate(end.getDate() - 7 * 26 - ((end.getDay() + 6) % 7));
  const grid = h("div", { class: "heat" });
  for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
    const s = iso(d), v = heat[s] || 0;
    grid.append(h("i", { class: lv(v) + (s === today ? " td" : ""), title: `${fmt(s)}: ${v} Bewertungen/Häkchen` }));
  }
  return h("div", { class: "card" }, h("div", { class: "muted small", style: "margin-bottom:6px" }, "Letzte 6 Monate (Anki-Bewertungen + abgehakte Punkte)"), grid);
}
async function newPlan(from) {
  const t = S.data.today || iso(new Date());
  const title = h("input", { type: "text", placeholder: "z. B. Kopf-Hals-Testat", style: "width:100%" });
  const exam = h("input", { type: "date", value: addDays(t, 14) });
  const start = h("input", { type: "date", value: t });
  const ok = await modal(from ? "Nächsten Plan anlegen" : "Neuer Plan", h("div", { class: "form" },
    h("label", null, "Name"), title, h("label", null, "Prüfungsdatum"), exam, h("label", null, "Start"), start,
    from ? h("p", { class: "muted small", style: "grid-column:1/-1" }, "Die Quellen-Arten (Handbuch, Videos, Anki …) und dein Tempo werden übernommen. Decks, Seiten und Themen trägst du neu ein.") : null));
  if (!ok) return;
  if (!title.value.trim()) return toast("Bitte einen Namen eingeben.");
  if (exam.value <= start.value) return toast("Die Prüfung muss nach dem Start liegen.");
  const p = await run(call("create", { title: title.value.trim(), exam: exam.value, start: start.value, from }));
  go("edit", p.id);
}

function tile(k, v, frac, sub) {
  const t = h("div", { class: "tile" }, h("div", { class: "k" }, k), h("div", { class: "v" }, v, sub ? h("small", null, " " + sub) : null));
  if (frac != null) t.append(h("div", { class: "pbar" + (frac >= 1 ? " ok" : "") }, h("i", { style: `width:${Math.min(100, 100 * frac)}%` })));
  return t;
}

// ---------- Planansicht ----------
function itemDone(it) { const d = S.data; return !!(d.plan.done[it.id] || (d.ev[it.id] && d.ev[it.id].done)); }

function renderPlan(root) {
  const { plan, stats, progress, phase, overdue } = S.data;
  const today = stats.today, left = daysBetween(today, plan.exam);
  if (phase === "setup") { S.view = "edit"; return go("edit"); }
  root.append(h("div", { class: "top" },
    h("div", null, h("a", { class: "small", onclick: () => go("home") }, "← Alle Pläne"), h("h1", null, plan.title),
      h("p", { class: "sub" }, `Prüfung ${fmt(plan.exam)}${plan.examTime ? ", " + plan.examTime : ""}${plan.subtitle ? " · " + plan.subtitle : ""}`)),
    h("div", { class: "bar-actions" },
      h("button", { onclick: () => go("edit") }, "Bearbeiten"),
      h("button", { onclick: () => replan() }, "Neu planen"),
      h("button", { onclick: () => go("review") }, "Rückblick"))));

  for (const n of plan.notes || []) root.append(h("div", { class: "card warn" }, n));

  // Kacheln
  const tiles = h("div", { class: "tiles" });
  tiles.append(tile("Bis zur Prüfung", left > 0 ? String(left) : left === 0 ? "heute" : "vorbei", null, left > 0 ? (left === 1 ? "Tag" : "Tage") : ""));
  const nextMs = (plan.milestones || []).filter(m => m.date && m.date >= today && m.date < plan.exam).sort((a, b) => a.date.localeCompare(b.date))[0];
  if (nextMs) { const n = daysBetween(today, nextMs.date); tiles.append(tile(nextMs.name || "Nächste Etappe", n ? String(n) : "heute", null, n ? (n === 1 ? "Tag" : "Tage") : "")); }
  tiles.append(tile("Plan erledigt", `${progress[0]}`, progress[1] ? progress[0] / progress[1] : 0, "/ " + progress[1]));
  for (const s of plan.sources) {
    if (s.type === "anki" && stats.decks[s.id]) {
      const c = stats.decks[s.id], seen = c.total - c.new;
      tiles.append(tile(s.name, String(seen), c.total ? seen / c.total : 0, "/ " + c.total + " gesehen"));
    } else if (s.type !== "anki") {
      const its = allItems(plan).filter(([, it]) => it.source === s.id && !it.moved);
      if (s.type === "pages") {
        const pg = its.reduce((a, [, it]) => a + it.pages[1] - it.pages[0] + 1, 0), dn = its.filter(([, it]) => itemDone(it)).reduce((a, [, it]) => a + it.pages[1] - it.pages[0] + 1, 0);
        tiles.append(tile(s.name, String(dn), pg ? dn / pg : 0, "/ " + pg + " S."));
      } else {
        const dn = its.filter(([, it]) => itemDone(it)).length;
        tiles.append(tile(s.name, String(dn), its.length ? dn / its.length : 0, "/ " + its.length));
      }
    }
  }
  if (plan.sources.some(s => s.type === "anki")) tiles.append(tile("Jetzt fällig", String(stats.due), null, stats.due === 0 ? "✓" : "Karten"));
  root.append(tiles);

  if (plan.sim && (plan.sim.started || plan.sim.result)) root.append(simPanel());

  if (overdue.length) root.append(h("div", { class: "card warn" }, h("h2", null, `${overdue.length} Punkte von vergangenen Tagen offen`),
    h("p", { class: "small", style: "margin:4px 0 8px" }, "„Neu planen“ verteilt sie (und alles andere, was noch offen ist) auf die Tage bis zur Prüfung."),
    h("button", { class: "primary", onclick: () => replan() }, "Jetzt neu planen")));

  if (phase === "early") {
    root.append(h("div", { class: "card okc" }, h("h2", null, `Alles geschafft – noch ${left} ${left === 1 ? "Tag" : "Tage"} bis zur Prüfung 🎉`),
      h("p", { class: "small", style: "margin:4px 0 0" }, "Jetzt nicht ausruhen auf dem Plan, sondern festigen:"), toolsPanel(true)));
    celebrate(plan.id);
  } else if (phase === "after") {
    root.append(h("div", { class: "card hl" }, h("h2", null, "Die Prüfung ist vorbei"),
      h("p", { class: "small", style: "margin:4px 0 8px" }, "Schau dir den Rückblick an: Was hat geklappt, wie schnell warst du wirklich? Das Tempo fließt in den nächsten Plan ein."),
      h("div", { class: "bar-actions" }, h("button", { class: "primary", onclick: () => go("review") }, "Zum Rückblick"),
        h("button", { onclick: async () => { await run(call("archive", { id: plan.id, on: true })); toast("Archiviert."); go("home"); } }, "Archivieren"))));
  } else {
    root.append(h("details", { open: store.get("toolsOpen") || null, ontoggle: e => store.set("toolsOpen", e.target.open) },
      h("summary", null, "Werkzeuge: Schwachstellen · Vorziehen · Probeprüfung"), toolsPanel(false)));
  }
  if (progress[1] && progress[0] === progress[1] && phase !== "after") celebrate(plan.id);

  // Tage
  const past = plan.days.filter(d => d.d < today), rest = plan.days.filter(d => d.d >= today);
  if (past.length) root.append(h("p", null, h("a", { class: "small", onclick: () => { S.showPast = !S.showPast; render(); } },
    S.showPast ? "Vergangene Tage ausblenden" : `Vergangene Tage zeigen (${past.length})`)));
  for (const day of S.showPast ? plan.days : rest) root.append(dayCard(day, today));
  root.append(h("p", { class: "muted small", style: "margin-top:20px" }, "Punkte mit ", h("span", { class: "chip ok" }, "Anki"),
    " hakt der Plan selbst ab, sobald du in Anki lernst. Alles andere per Klick."));
}
function allItems(plan) { return plan.days.flatMap(d => d.items.map(it => [d, it])); }

function groupLabel(it, plan) {
  if (it.kind === "reviews" || it.kind === "cards") { const s = plan.sources.find(s => s.id === it.source); return it.kind === "reviews" ? "Anki" : (s ? s.name : "Anki"); }
  if (it.source) { const s = plan.sources.find(s => s.id === it.source); if (s) return s.name; }
  return { custom: "Eigene", weak: "Schwachstellen", weakround: "Schwachstellen", sim: "Probeprüfung", note: "Hinweis" }[it.kind] || "Sonst";
}

function dayCard(day, today) {
  const { plan } = S.data;
  const isToday = day.d === today, isExam = day.d === plan.exam;
  const sec = h("section", { class: "day" + (isToday ? " today" : day.d < today ? " past" : "") + (isExam || (plan.milestones || []).some(m => m.date === day.d) ? " exam" : "") });
  const mins = day.items.filter(it => !it.moved && it.kind !== "note").reduce((a, it) => a + (it.min || 0), 0);
  const note = [plan.dayNotes && plan.dayNotes[day.d], mins ? "≈ " + hm(mins) : null].filter(Boolean).join(" · ");
  const msDay = (plan.milestones || []).find(m => m.date === day.d);
  const h2 = h("h2", null, fmt(day.d), isToday ? h("span", { class: "badge" }, "HEUTE") : null, isExam ? h("span", { class: "badge warn" }, "PRÜFUNG") : null,
    msDay && !isExam ? h("span", { class: "badge warn" }, (msDay.name || "ETAPPE").toUpperCase()) : null);
  const head = h("div", { class: "dhead" }, h("div", null, h2, h("div", { class: "note" }, note)));
  sec.append(head);
  const groups = new Map();
  for (const it of day.items) { const g = groupLabel(it, plan); if (!groups.has(g)) groups.set(g, []); groups.get(g).push(it); }
  let tot = 0, dn = 0;
  for (const [g, its] of groups) {
    const box = h("div", { class: "items" });
    for (const it of its) {
      box.append(itemEl(it, day));
      if (!["note", "weakround", "sim"].includes(it.kind) && !it.moved) { tot++; if (itemDone(it)) dn++; }
    }
    sec.append(h("div", { class: "row" }, h("div", { class: "label" }, g), box));
  }
  if (tot) head.append(h("span", { class: "dprog" + (dn === tot ? " done" : "") }, dn === tot ? "✓ alles erledigt" : `${dn}/${tot} erledigt`));
  if (day.d >= today) {
    const inp = h("input", { type: "text", placeholder: "Eigener Punkt, z. B. „Altfragen 2023 durchgehen“" });
    const add = async () => { if (!inp.value.trim()) return; await run(call("addCustom", { id: plan.id, day: day.d, text: inp.value.trim() })); refresh(); };
    inp.addEventListener("keydown", e => { if (e.key === "Enter") add(); });
    sec.append(h("div", { class: "add-row" }, inp, h("button", { onclick: add }, "+")));
  }
  return sec;
}

function itemEl(it, day) {
  const { plan, ev } = S.data;
  if (it.kind === "note") return h("div", { class: "plain" }, it.text);
  if (it.kind === "weakround") return h("div", null, h("div", { class: "plain" }, it.text), h("div", { class: "bar-actions", style: "margin-top:5px" },
    h("button", { onclick: () => weakDialog() }, "Schwachstellen ansehen & einplanen"), h("button", { onclick: () => filtered("weak") }, "Schwache Karten lernen")));
  if (it.kind === "sim") return h("div", null, h("div", { class: "plain" }, it.text), h("div", { class: "bar-actions", style: "margin-top:5px" },
    h("button", { class: "primary", onclick: () => simStart() }, "Probeprüfung starten")));
  const r = ev[it.id], auto = !!it.auto, done = itemDone(it);
  const cb = h("input", { type: "checkbox", checked: done, disabled: it.moved || null });
  cb.addEventListener("change", async () => {
    if (auto && r && r.done && !plan.done[it.id]) { cb.checked = true; return toast("Das hakt Anki ab."); }
    await run(call("toggle", { id: plan.id, item: it.id, on: cb.checked }));
    refresh();
  });
  const t = h("span", { class: "t" }, it.text);
  if (auto) t.append(h("span", { class: "chip" + (r && r.done ? " ok" : "") }, r && r.text ? "Anki · " + r.text : "Anki"));
  if (it.moved) t.append(h("span", { class: "chip info" }, "→ neu eingeplant"));
  if (it.min && !auto && !it.moved) t.append(h("span", { class: "chip info" }, hm(it.min)));
  if (it.for) t.append(h("span", { class: "chip info" }, "für " + it.for));
  if (it.url) t.append(h("a", { class: "small", style: "margin-left:6px", title: it.url, onclick: e => { e.preventDefault(); call("openLink", { url: it.url }); } }, "öffnen ↗"));
  const row = h("label", { class: "item" + (done ? " checked" : "") + (it.moved ? " moved" : "") }, cb, t);
  if (it.custom || it.kind === "weak") row.append(h("button", { class: "ghost", title: "Entfernen", onclick: async e => { e.preventDefault(); await run(call("delItem", { id: plan.id, item: it.id })); refresh(); } }, "✕"));
  return row;
}

async function replan() {
  const r = await run(call("generate", { id: S.pid }));
  toast(r.notes.length ? "Neu geplant – mit Hinweis, siehe oben." : "Neu geplant: offener Stoff ist auf die Tage bis zur Prüfung verteilt.");
  go("plan");
}

// ---------- Werkzeuge ----------
function toolsPanel(early) {
  return h("div", { class: "panel-tools" },
    h("div", { class: "tool" }, h("b", null, "Schwachstellen-Runde"), h("p", null, "Findet die Themen mit den meisten Fehlern in Anki und plant Handbuch, Video und schwache Karten dafür neu ein."),
      h("button", { class: early ? "primary" : null, onclick: () => weakDialog() }, "Schwachstellen ansehen")),
    h("div", { class: "tool" }, h("b", null, "Vorziehen"), h("p", null, "Gefiltertes Deck mit Karten, die erst nach der Prüfung fällig wären – damit du sie vorher noch einmal siehst."),
      h("button", { onclick: () => filtered("ahead") }, "Deck „vorziehen“ erstellen")),
    h("div", { class: "tool" }, h("b", null, "Probeprüfung"), h("p", null, "Zufällige Karten aus allen Decks auf Zeit, ohne Kapitel-Hinweis, plus Themen zum freien Erklären."),
      h("button", { onclick: () => simStart() }, "Probeprüfung starten")));
}

async function weakDialog() {
  const r = await run(call("weak", { id: S.pid }));
  if (!r.weak.length) return modal("Schwachstellen", h("p", null, "Noch keine Fehler in den Themen-Karten seit Planbeginn – entweder läuft es super, oder die Themen sind noch nicht mit Anki-Unterdecks/Tags verknüpft (Bearbeiten → Themen)."), [["OK", true, "primary"]]);
  const body = h("div", null, h("table", null, h("tr", null, h("th", null, "Thema"), h("th", null, "Fehler"), h("th", null, "schwache Karten")),
    r.weak.slice(0, 8).map(w => h("tr", null, h("td", null, w.name), h("td", null, String(w.agains)), h("td", null, String(w.cards))))),
    h("h3", null, "Wird eingeplant"), h("ul", { class: "weak-list" }, r.items.map(i => h("li", null, i.text))));
  const v = await modal("Schwachstellen seit Planbeginn", body, [["Schließen", null], ["Nur Karten lernen", "cards"], ["Einplanen", "plan", "primary"]]);
  if (v === "plan") { const x = await run(call("addWeak", { id: S.pid })); toast(`Eingeplant am ${fmt(x.day)}.`); refresh(); }
  if (v === "cards") filtered("weak");
}

async function filtered(kind, extra) {
  const r = await run(call("filtered", Object.assign({ id: S.pid, kind }, extra || {})));
  if (!r.count) { toast(kind === "ahead" ? "Keine Karten, die erst nach der Prüfung fällig wären." : "Keine passenden Karten gefunden."); return r; }
  if (kind !== "sim") {
    const v = await modal("Deck erstellt", h("p", null, `${r.count} Karten im gefilterten Deck. Es liegt unter „Lernplan“ in deiner Deckliste.`), [["Später", null], ["Jetzt lernen", true, "primary"]]);
    if (v) call("study", { did: r.did });
  }
  return r;
}

async function simStart() {
  const n = h("input", { type: "number", value: 50, min: 5, max: 500 }), m = h("input", { type: "number", value: 30, min: 5, max: 240 });
  const ok = await modal("Probeprüfung", h("div", null, h("div", { class: "form" }, h("label", null, "Karten"), n, h("label", null, "Zeit (Minuten)"), m),
    h("p", { class: "muted small" }, "Es wird ein gefiltertes Deck mit zufälligen, schon gelernten Karten erstellt. Lerne es im Hauptfenster; hier läuft die Uhr. Danach siehst du, welche Themen sitzen.")), [["Abbrechen", null], ["Starten", true, "primary"]]);
  if (!ok) return;
  const r = await filtered("sim", { n: +n.value, minutes: +m.value });
  if (r.count) { await refresh(); call("study", { did: r.did }); }
}

function simPanel() {
  const { plan, simResult } = S.data, sim = plan.sim || {};
  const card = h("div", { class: "card hl" });
  if (sim.started) {
    const end = sim.started + sim.minutes * 60e3;
    const timer = h("div", { class: "timer" });
    const tick = () => { const s = Math.max(0, Math.round((end - Date.now()) / 1000)); timer.textContent = `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`; if (!s) timer.style.color = "var(--bad)"; };
    tick(); clearInterval(S.simTimer); S.simTimer = setInterval(() => document.body.contains(timer) ? tick() : clearInterval(S.simTimer), 1000);
    const topics = plan.topics.slice().sort(() => Math.random() - .5).slice(0, 3);
    card.append(h("h2", null, "Probeprüfung läuft"), timer,
      h("div", { class: "small muted" }, simResult ? `${simResult.answered}/${simResult.total} Karten beantwortet · ${simResult.ok} richtig` : ""),
      topics.length ? h("p", { class: "small" }, "Frei erklären (laut, ohne Unterlagen): ", h("b", null, topics.map(t => t.name).join(" · "))) : null,
      h("div", { class: "bar-actions" }, h("button", { onclick: () => call("study", { did: sim.deck }) }, "Zum Lernen"),
        h("button", { class: "primary", onclick: async () => { const r = await run(call("simStop", { id: plan.id })); showSim(r); refresh(); } }, "Beenden & auswerten")));
  } else if (sim.result) {
    card.append(h("h2", null, "Letzte Probeprüfung"), simTable(sim.result));
  }
  return card;
}
function simTable(r) {
  if (!r || !r.answered) return h("p", { class: "muted" }, "Keine Antworten gefunden.");
  return h("div", null, h("p", null, `${r.ok}/${r.answered} richtig (${Math.round(100 * r.ok / r.answered)} %)`),
    r.topics.length ? h("table", null, h("tr", null, h("th", null, "Thema"), h("th", null, "richtig")),
      r.topics.map(t => h("tr", null, h("td", null, t.name), h("td", null, `${t.ok}/${t.n}`)))) : null);
}
function showSim(r) { modal("Probeprüfung – Ergebnis", simTable(r), [["OK", true, "primary"]]); }

// ---------- Konfetti ----------
function celebrate(pid) {
  if (store.get("party." + pid)) return;
  store.set("party." + pid, true);
  const c = h("canvas", { class: "confetti" }); document.body.append(c);
  const x = c.getContext("2d"); c.width = innerWidth; c.height = innerHeight;
  const cols = ["#2f7d4f", "#2f5d9e", "#e3a64a", "#b3372b", "#8db4ee"];
  const ps = Array.from({ length: 140 }, () => ({ x: Math.random() * c.width, y: -20 - Math.random() * c.height / 2, vy: 2 + Math.random() * 3, vx: Math.random() * 2 - 1, r: Math.random() * 6, c: cols[Math.floor(Math.random() * cols.length)], a: Math.random() * 6 }));
  let f = 0;
  (function step() {
    x.clearRect(0, 0, c.width, c.height);
    for (const p of ps) { p.y += p.vy; p.x += p.vx + Math.sin((f + p.a) / 12); x.fillStyle = p.c; x.fillRect(p.x, p.y, 6, 3 + p.r); }
    if (++f < 220) requestAnimationFrame(step); else c.remove();
  })();
  toast("Alles abgehakt – stark! 🎉", 3500);
}

// ---------- Bearbeiten ----------
async function loadCands() {
  for (const s of S.edit.sources) if (s.type === "anki" && s.deck && !S.cands[s.id]) {
    const r = await call("candidates", { plan: { sources: [s] } });
    S.cands[s.id] = r[s.id] || [];
  }
}
async function suggestNow() {
  S.sugg = await run(call("suggest", { plan: S.edit }));
}
function renderEdit(root) {
  const p = S.edit;
  root.append(h("div", { class: "top" },
    h("div", null, h("a", { class: "small", onclick: () => go(p.days.length ? "plan" : "home") }, p.days.length ? "← Zurück zum Plan" : "← Alle Pläne"), h("h1", null, p.title || "Neuer Plan"),
      h("p", { class: "sub" }, "1. Eckdaten → 2. Quellen → 3. Themen → Plan erstellen")),
    h("div", { class: "bar-actions" }, h("button", { onclick: saveEdit }, "Speichern"), h("button", { class: "primary", onclick: () => saveEdit(true) }, p.days.length ? "Speichern & neu planen" : "Plan erstellen"))));

  // 1. Eckdaten
  const f = h("div", { class: "form" });
  const field = (lab, el) => f.append(h("label", null, lab), el);
  const bind = (key, type = "text", attrs = {}) => h("input", Object.assign({ type, value: p[key] ?? "", onchange: e => { p[key] = type === "number" ? +e.target.value : e.target.value; if (["exam", "start", "minutesPerDay"].includes(key)) render(); } }, attrs));
  field("Name", bind("title", "text", { style: "width:100%" }));
  field("Zusatzzeile", bind("subtitle", "text", { style: "width:100%", placeholder: "z. B. Fach, weitere Termine" }));
  field("Prüfung", h("div", { class: "inline" }, bind("exam", "date"), bind("examTime", "time")));
  field("Start", bind("start", "date"));
  field("Lernzeit pro Tag", h("div", { class: "inline" }, bind("minutesPerDay", "number", { min: 0, step: 15 }), h("span", { class: "muted small" }, "Minuten (einzelne Tage unten anpassen)")));
  field("Freie Wochentage", h("div", { class: "inline" }, WD_MO.map(([l, n]) => h("label", { class: "wd" }, h("input", { type: "checkbox", checked: p.offWeekdays.includes(n),
    onchange: e => { p.offWeekdays = e.target.checked ? [...p.offWeekdays, n] : p.offWeekdays.filter(x => x !== n); render(); } }), l))));
  root.append(h("div", { class: "card" }, h("h2", null, "1 · Eckdaten"), h("div", { style: "margin-top:10px" }, f), milestonesEl(p), calendar(p)));

  // 2. Quellen
  const srcBox = h("div", { style: "margin-top:10px" }, p.sources.map(s => sourceEl(s)));
  root.append(h("div", { class: "card" }, h("h2", null, "2 · Quellen"),
    h("p", { class: "muted small", style: "margin:2px 0 0" }, "Alles, womit du lernst. Anki-Decks werden automatisch verfolgt; Seiten, Videos und Aufgaben hakst du ab."),
    srcBox, h("div", { class: "tools" },
      h("button", { onclick: () => addSource("pages") }, "+ Buch / Skript / Folien (Seiten)"),
      h("button", { onclick: () => addSource("videos") }, "+ Videos / Vorlesungen"),
      h("button", { onclick: () => addSource("anki") }, "+ Anki-Deck"),
      h("button", { onclick: () => addSource("tasks") }, "+ Liste (VMC-Module, Altfragen, Übungen …)")),
    h("p", { class: "muted small" }, "Quellen, auf die der Plan keinen Zugriff hat (VMC, YouTube, Moodle, Bücher), trägst du als Liste ein – mit Link, wenn du willst. Der Plan verteilt sie trotzdem; abhaken tust du sie selbst.")));

  // 3. Themen
  root.append(topicsCard(p));
  root.append(h("div", { class: "bar-actions", style: "justify-content:flex-end" },
    p.days.length ? h("button", { class: "danger", onclick: delPlan }, "Plan löschen") : null,
    h("button", { onclick: saveEdit }, "Speichern"), h("button", { class: "primary", onclick: () => saveEdit(true) }, p.days.length ? "Speichern & neu planen" : "Plan erstellen")));
}

function milestonesEl(p) {
  p.milestones = p.milestones || [];
  const box = h("div", { style: "margin-top:12px" }, h("h3", null, "Etappen / Testate vor der Prüfung"),
    h("p", { class: "muted small", style: "margin:0 0 6px" }, "Hat das Fach Zwischentermine (Testate, Teilprüfungen)? Dann hier eintragen und bei jedem Thema wählen, wozu es gehört. Der Plan macht den Stoff jeder Etappe vor ihrem Termin fertig – egal in welcher Reihenfolge er im Buch steht."));
  for (const m of p.milestones.slice().sort((a, b) => (a.date || "").localeCompare(b.date || ""))) {
    box.append(h("div", { class: "inline", style: "margin-bottom:5px" },
      h("input", { type: "text", value: m.name, placeholder: "z. B. Testat Becken", style: "flex:1;min-width:180px", onchange: e => { m.name = e.target.value; } }),
      h("input", { type: "date", value: m.date || "", onchange: e => { m.date = e.target.value; render(); } }),
      h("input", { type: "time", value: m.time || "", onchange: e => { m.time = e.target.value; } }),
      h("button", { class: "ghost danger", title: "Etappe löschen", onclick: () => { p.milestones = p.milestones.filter(x => x !== m); for (const t of p.topics) if (t.milestone === m.id) delete t.milestone; render(); } }, "✕")));
  }
  box.append(h("button", { onclick: () => { p.milestones.push({ id: uid("m"), name: "", date: "", time: "" }); render(); } }, "+ Etappe / Testat"));
  return box;
}
function msName(p, id) { const m = (p.milestones || []).find(m => m.id === id); return m ? (m.name || "Etappe") : null; }

function calendar(p) {
  const cal = h("div", { class: "cal" });
  if (!p.start || !p.exam || p.exam < p.start) return cal;
  for (let d = p.start; d <= p.exam; d = addDays(d, 1)) {
    const wd = (dt(d).getDay() + 6) % 7, has = d in p.dayMinutes;
    const val = has ? p.dayMinutes[d] : (p.offWeekdays.includes(wd) ? 0 : p.minutesPerDay);
    const exam = d === p.exam, ms = (p.milestones || []).find(m => m.date === d);
    cal.append(h("div", { class: "c" + (val ? "" : " off") + (exam || ms ? " exam" : "") },
      h("div", null, h("b", null, fmt(d)), exam ? " · Prüfung" : ms ? " · " + (ms.name || "Etappe") : ""),
      exam ? null : h("div", { class: "inline" }, h("input", { type: "number", min: 0, step: 15, value: val, title: "Minuten an diesem Tag",
        onchange: e => { const v = +e.target.value; const def = p.offWeekdays.includes(wd) ? 0 : p.minutesPerDay; if (v === def) delete p.dayMinutes[d]; else p.dayMinutes[d] = v; render(); } }), h("span", { class: "muted" }, "min")),
      h("input", { type: "text", placeholder: "Notiz", value: (p.dayNotes || {})[d] || "", onchange: e => { p.dayNotes = p.dayNotes || {}; if (e.target.value) p.dayNotes[d] = e.target.value; else delete p.dayNotes[d]; } })));
  }
  return h("details", { open: true }, h("summary", null, "Einzelne Tage (Minuten · Notiz wie „Präpsaal 13–17 Uhr“)"), cal);
}

function addSource(type) {
  const s = { id: uid("s"), type, name: { pages: "Skript", videos: "Videos", anki: "", tasks: "Liste" }[type], minPerUnit: null };
  if (type === "videos") { s.videos = []; s.defaultMin = 20; }
  if (type === "tasks") s.tasks = [];
  if (type === "anki") { s.deck = ""; s.maxNew = null; }
  S.edit.sources.push(s); render();
}

function sourceEl(s) {
  const p = S.edit;
  const rm = () => { if (!confirm(`Quelle „${s.name || TYPES[s.type]}“ entfernen?`)) return; p.sources = p.sources.filter(x => x !== s); for (const t of p.topics) for (const k of ["pages", "videos", "tasks", "anki"]) if (t[k]) delete t[k][s.id]; render(); };
  const box = h("div", { class: "src" }, h("div", { class: "src-head" }, h("span", { class: "type" }, TYPES[s.type]),
    h("input", { class: "name", type: "text", value: s.name, placeholder: "Name", onchange: e => { s.name = e.target.value; } }),
    h("button", { class: "ghost danger", onclick: rm }, "Entfernen")));
  const rate = h("span", { class: "inline small" }, h("input", { type: "number", step: "0.5", min: 0, value: s.minPerUnit ?? "", placeholder: String(defaultRate(s.type)),
    onchange: e => { s.minPerUnit = e.target.value ? +e.target.value : null; } }), h("span", { class: "muted" }, UNIT[s.type]));
  if (s.type === "pages") box.append(h("div", { class: "inline small" }, "Tempo:", rate, h("span", { class: "muted" }, "· Seitenbereiche trägst du bei den Themen ein.")));
  if (s.type === "anki") {
    const dl = "decks-" + s.id;
    const info = h("div", { class: "small muted", style: "margin-top:4px" });
    const showInfo = async () => {
      if (!s.deck) return;
      const i = await call("deckInfo", { deck: s.deck });
      if (!i) { info.textContent = "Deck nicht gefunden."; return; }
      info.textContent = `${i.new} neue von ${i.total} Karten · ${i.children.length} Unterdecks · Anki-Limit ${i.perDay ?? "?"} neue/Tag`;
      if (!s.name) { s.name = s.deck.split("::").pop(); box.querySelector("input.name").value = s.name; }
      if (s.maxNew == null && i.perDay) { s.maxNew = i.perDay; mx.value = i.perDay; }
    };
    const mx = h("input", { type: "number", min: 0, value: s.maxNew ?? "", placeholder: "∞", onchange: e => { s.maxNew = e.target.value ? +e.target.value : null; } });
    box.append(h("div", { class: "inline" },
      h("input", { type: "text", list: dl, value: s.deck, placeholder: "Deck wählen …", style: "flex:1;min-width:240px",
        onchange: async e => { s.deck = e.target.value; delete S.cands[s.id]; await loadCands(); showInfo(); render(); } }),
      h("datalist", { id: dl }, (S.decks || []).map(n => h("option", { value: n })))),
      h("div", { class: "inline small", style: "margin-top:6px" }, "Tempo:", rate, h("span", { class: "muted" }, "· max. neue/Tag:"), mx), info);
    showInfo();
  }
  if (s.type === "videos" || s.type === "tasks") {
    const key = s.type, list = s[key];
    const ta = h("textarea", { placeholder: key === "videos" ? "Ein Video pro Zeile, Dauer und Link optional:\nBauchsitus 1 – Allgemeines | 25\nNiere Histologie (18 min)\nVMC Endokrinologie 1 | 40 | https://…" : "Ein Eintrag pro Zeile, Dauer und Link optional:\nVMC-Modul Niere | 45 | https://…\nAltfragen Embryo 2023 | 60" });
    ta.value = list.map(v => v.name + (v.min ? " | " + v.min : "") + (v.url ? " | " + v.url : "")).join("\n");
    ta.addEventListener("change", async () => {
      const parsed = await call("parseList", { text: ta.value });
      const old = new Map(list.map(v => [v.name, v]));
      s[key] = parsed.map(x => Object.assign(old.get(x.name) || { id: uid(key === "videos" ? "v" : "t") }, { name: x.name, min: x.min, url: x.url || null }));
      const ids = new Set(s[key].map(v => v.id));
      for (const t of p.topics) if (t[key] && t[key][s.id]) t[key][s.id] = t[key][s.id].filter(i => ids.has(i));
      S.sugg = {}; render();
    });
    box.append(ta, h("div", { class: "inline small", style: "margin-top:4px" }, `${list.length} Einträge · Standarddauer:`,
      h("input", { type: "number", min: 1, value: s.defaultMin ?? (key === "videos" ? 20 : 30), onchange: e => { s.defaultMin = +e.target.value; } }), h("span", { class: "muted" }, "min (wenn keine Dauer angegeben)")));
  }
  return box;
}
function defaultRate(t) { const prof = (S.data && S.data.profile) || {}; return (prof.rates || {})[t] ?? { pages: 6, videos: 20, tasks: 30, anki: 1 }[t]; }

function topicsCard(p) {
  const card = h("div", { class: "card" }, h("h2", null, "3 · Themen"),
    h("p", { class: "muted small", style: "margin:2px 0 0" }, "Ein Thema bündelt, was zusammengehört: Handbuchseiten + Unterdeck/Tag + Videos. Der Plan arbeitet die Themen nacheinander ab: erst lesen, dann Video, dann Karten zum selben Thema."));
  const ankiSrc = p.sources.filter(s => s.type === "anki" && s.deck), pageSrc = p.sources.filter(s => s.type === "pages");
  card.append(h("div", { class: "tools" },
    pageSrc.length ? h("button", { onclick: tocDialog }, "Inhaltsverzeichnis einfügen") : null,
    ankiSrc.length ? h("button", { onclick: fromDecks }, "Themen aus Unterdecks") : null,
    h("button", { onclick: () => { p.topics.push({ id: uid("k"), name: "", pages: {}, videos: {}, tasks: {}, anki: {} }); render(); } }, "+ Thema"),
    p.topics.length ? h("button", { class: "primary", onclick: autoAssign }, "Zuordnung automatisch vorschlagen") : null,
    h("span", { class: "inline small", style: "margin-left:auto" }, "Reihenfolge:",
      h("select", { onchange: e => { p.order = e.target.value; render(); } }, h("option", { value: "auto", selected: p.order === "auto" || null }, "automatisch (nach Testat, dann Seiten)"), h("option", { value: "manual", selected: p.order === "manual" || null }, "wie in der Liste")))));
  const list = p.order === "auto" ? sortedTopics(p) : p.topics;
  list.forEach((t, ix) => card.append(topicEl(t, ix, list.length)));
  // nicht zugeordnete Videos/Aufgaben
  const used = new Set(p.topics.flatMap(t => [...Object.values(t.videos || {}), ...Object.values(t.tasks || {})].flat()));
  const free = p.sources.filter(s => s.videos || s.tasks).flatMap(s => (s.videos || s.tasks).filter(v => !used.has(v.id)).map(v => v.name));
  if (free.length && p.topics.length) card.append(h("p", { class: "muted small" }, `${free.length} Einträge sind keinem Thema zugeordnet und kommen ans Ende: ${free.slice(0, 6).join(", ")}${free.length > 6 ? " …" : ""}`));
  if (ankiSrc.length) card.append(h("p", { class: "muted small" }, "Anki-Karten ohne Thema werden als „übrige Karten“ nach den Themen eingeplant."));
  return card;
}
function sortedTopics(p) {
  const ps = p.sources.filter(s => s.type === "pages").map(s => s.id);
  const due = t => { const m = (p.milestones || []).find(m => m.id === t.milestone && m.date); return m ? m.date : p.exam; };
  const key = t => { for (const id of ps) { const r = (t.pages || {})[id]; if (r && r[0]) return r[0]; } return Infinity; };
  return p.topics.map((t, i) => [t, i]).sort((a, b) => due(a[0]).localeCompare(due(b[0])) || key(a[0]) - key(b[0]) || a[1] - b[1]).map(x => x[0]);
}

function topicEl(t, ix, n) {
  const p = S.edit, manual = p.order !== "auto";
  const move = d => { const i = p.topics.indexOf(t), j = i + d; if (j < 0 || j >= p.topics.length) return; [p.topics[i], p.topics[j]] = [p.topics[j], p.topics[i]]; render(); };
  const box = h("div", { class: "topic" }, h("div", { class: "topic-head" }, h("span", { class: "muted small" }, String(ix + 1) + "."),
    h("input", { type: "text", value: t.name, placeholder: "Thema, z. B. Leistenkanal", onchange: e => { t.name = e.target.value; S.sugg = {}; } }),
    manual ? h("button", { class: "ghost", onclick: () => move(-1), title: "nach oben" }, "↑") : null,
    manual ? h("button", { class: "ghost", onclick: () => move(1), title: "nach unten" }, "↓") : null,
    h("button", { class: "ghost danger", onclick: () => { p.topics = p.topics.filter(x => x !== t); render(); }, title: "Thema löschen" }, "✕")));
  const tl = h("div", { class: "tl" });
  const sg = (S.sugg[t.id] || {});
  if ((p.milestones || []).length) tl.append(h("span", null, "Gehört zu"), h("select", { onchange: e => { if (e.target.value) t.milestone = e.target.value; else delete t.milestone; render(); } },
    h("option", { value: "" }, "Prüfung (Ende)"), p.milestones.map(m => h("option", { value: m.id, selected: t.milestone === m.id || null }, `${m.name || "Etappe"}${m.date ? " · " + fmt(m.date) : ""}`))));
  for (const s of p.sources) {
    if (s.type === "pages") {
      t.pages = t.pages || {};
      const r = t.pages[s.id] || ["", ""];
      const upd = (i, v) => { const cur = t.pages[s.id] || ["", ""]; cur[i] = v ? +v : ""; if (cur[0] && !cur[1]) cur[1] = cur[0]; t.pages[s.id] = cur[0] ? [cur[0], Math.max(cur[0], cur[1] || cur[0])] : null; if (!t.pages[s.id]) delete t.pages[s.id]; };
      tl.append(h("span", null, s.name || "Seiten"), h("div", { class: "inline" }, "S.", h("input", { type: "number", min: 0, value: r[0], onchange: e => upd(0, e.target.value) }), "–",
        h("input", { type: "number", min: 0, value: r[1], onchange: e => { upd(1, e.target.value); if (p.order === "auto") render(); } })));
    } else if (s.type === "anki") {
      t.anki = t.anki || {};
      const cands = S.cands[s.id] || [], cur = t.anki[s.id] || "";
      const best = (sg[s.id] || []).map(x => x.query);
      const opts = [h("option", { value: "" }, "— keine Verknüpfung —")];
      const seen = new Set();
      for (const q of best) { const c = cands.find(c => c.query === q); if (c) { seen.add(q); opts.push(h("option", { value: q, selected: q === cur || null }, "★ " + c.label)); } }
      for (const c of cands) if (!seen.has(c.query)) opts.push(h("option", { value: c.query, selected: c.query === cur || null }, c.label));
      if (cur && !cands.some(c => c.query === cur)) opts.push(h("option", { value: cur, selected: true }, cur));
      tl.append(h("span", null, s.name || "Anki"), h("select", { style: "max-width:100%", onchange: e => { if (e.target.value) t.anki[s.id] = e.target.value; else delete t.anki[s.id]; } }, opts));
    } else if (s.type === "videos" || s.type === "tasks") {
      const key = s.type; t[key] = t[key] || {};
      const cur = t[key][s.id] || [];
      const items = s[key] || [];
      const usedElse = new Set(p.topics.filter(x => x !== t).flatMap(x => (x[key] || {})[s.id] || []));
      const bestIds = (sg[s.id] || []).map(x => x.id);
      const sel = h("select", { onchange: e => { if (!e.target.value) return; t[key][s.id] = [...cur, e.target.value]; render(); } },
        h("option", { value: "" }, "+ hinzufügen …"),
        items.filter(v => !cur.includes(v.id)).sort((a, b) => (bestIds.includes(b.id) - bestIds.includes(a.id)))
          .map(v => h("option", { value: v.id }, (bestIds.includes(v.id) ? "★ " : "") + v.name + (usedElse.has(v.id) ? " (schon zugeordnet)" : ""))));
      tl.append(h("span", null, s.name || TYPES[key]), h("div", null, cur.map(id => { const v = items.find(v => v.id === id); return v ? h("span", { class: "pill" }, v.name, h("button", { onclick: () => { t[key][s.id] = cur.filter(x => x !== id); render(); } }, "×")) : null; }), items.length ? sel : h("span", { class: "muted small" }, "Liste oben ausfüllen")));
    }
  }
  box.append(tl);
  return box;
}

async function autoAssign() {
  await suggestNow();
  const r = await run(call("suggest", { plan: S.edit, apply: true }));
  S.edit = r.plan;
  toast(r.changed ? `${r.changed} Zuordnungen übernommen – bitte kurz prüfen (★ = Vorschlag).` : "Keine neuen Treffer gefunden. Namen von Themen, Unterdecks und Videos ähneln sich zu wenig.", 4000);
  render();
}

async function tocDialog() {
  const p = S.edit, pageSrc = p.sources.filter(s => s.type === "pages");
  const ta = h("textarea", { style: "min-height:180px", placeholder: "Aus dem Inhaltsverzeichnis kopieren, z. B.\nPeritoneum ............ 78\nLeistenkanal 82–84\n85 Dünndarm" });
  const sel = h("select", null, pageSrc.map(s => h("option", { value: s.id }, s.name)));
  const msSel = h("select", null, h("option", { value: "" }, "Prüfung (Ende)"), (p.milestones || []).map(m => h("option", { value: m.id }, m.name || "Etappe")));
  const ok = await modal("Inhaltsverzeichnis einfügen", h("div", null, pageSrc.length > 1 ? h("div", { class: "inline", style: "margin-bottom:6px" }, "Für:", sel) : null,
    (p.milestones || []).length ? h("div", { class: "inline", style: "margin-bottom:6px" }, "Diese Kapitel gehören zu:", msSel) : null, ta,
    h("p", { class: "muted small" }, "Eine Zeile pro Kapitel mit Seitenzahl. Endet ein Kapitel nicht mit einer Angabe, geht es bis eine Seite vor dem nächsten. Vorhandene Themen mit gleichem Namen bekommen die Seiten.")),
    [["Abbrechen", null], ["Übernehmen", true, "primary"]]);
  if (!ok || !ta.value.trim()) return;
  const rows = await run(call("parseToc", { text: ta.value }));
  const sid = sel.value || pageSrc[0].id;
  let added = 0;
  for (const r of rows) {
    let t = p.topics.find(t => t.name.trim().toLowerCase() === r.name.toLowerCase());
    if (!t) { t = { id: uid("k"), name: r.name, pages: {}, videos: {}, tasks: {}, anki: {} }; p.topics.push(t); added++; }
    t.pages = t.pages || {}; t.pages[sid] = [r.from, r.to];
    if (msSel.value) t.milestone = msSel.value;
  }
  toast(`${rows.length} Kapitel erkannt, ${added} neue Themen.`);
  render();
}

async function fromDecks() {
  const p = S.edit, srcs = p.sources.filter(s => s.type === "anki" && s.deck);
  const sel = h("select", null, srcs.map(s => h("option", { value: s.id }, s.name || s.deck)));
  const ok = await modal("Themen aus Unterdecks", h("div", null, h("div", { class: "inline" }, "Deck:", sel),
    h("p", { class: "muted small" }, "Für jedes direkte Unterdeck entsteht ein Thema, das schon mit dem Unterdeck verknüpft ist. Danach „Zuordnung automatisch vorschlagen“ für Videos.")),
    [["Abbrechen", null], ["Erstellen", true, "primary"]]);
  if (!ok) return;
  const s = srcs.find(s => s.id === sel.value) || srcs[0];
  const info = await run(call("deckInfo", { deck: s.deck }));
  let added = 0;
  for (const child of info.children) {
    const q = `deck:"${(s.deck + "::" + child).replace(/"/g, '\\"')}"`;
    if (p.topics.some(t => (t.anki || {})[s.id] === q)) continue;
    let t = p.topics.find(t => t.name.trim().toLowerCase() === child.toLowerCase());
    if (!t) { t = { id: uid("k"), name: child, pages: {}, videos: {}, tasks: {}, anki: {} }; p.topics.push(t); added++; }
    t.anki = t.anki || {}; t.anki[s.id] = q;
  }
  toast(info.children.length ? `${added} Themen aus ${info.children.length} Unterdecks.` : "Dieses Deck hat keine Unterdecks. Tags kannst du pro Thema auswählen.");
  render();
}

function validate(p) {
  if (!p.title.trim()) return "Bitte einen Namen eingeben.";
  if (!p.exam || !p.start || p.exam <= p.start) return "Die Prüfung muss nach dem Start liegen.";
  if (!p.sources.length) return "Füge mindestens eine Quelle hinzu (z. B. ein Anki-Deck oder das Handbuch).";
  if ((p.milestones || []).some(m => !m.date || m.date <= p.start || m.date >= p.exam)) return "Jede Etappe braucht ein Datum zwischen Start und Prüfung.";
  const bad = p.sources.find(s => s.type === "anki" && !s.deck);
  if (bad) return "Bei einer Anki-Quelle fehlt noch das Deck.";
  return null;
}
async function saveEdit(plan) {
  const p = S.edit;
  for (const t of p.topics) if (!t.name.trim()) t.name = "Thema";
  if (plan === true) { const err = validate(p); if (err) return toast(err, 4000); }
  await run(call("savePlan", { plan: p }));
  if (plan === true) { await replan(); } else toast("Gespeichert.");
}
async function delPlan() {
  const v = await modal("Plan löschen?", h("p", null, `„${S.edit.title}“ wird endgültig gelöscht. Anki-Karten bleiben unberührt. Lieber archivieren? Das geht im Rückblick.`), [["Abbrechen", null], ["Löschen", true, "danger"]]);
  if (!v) return;
  await run(call("delete", { id: S.edit.id })); go("home");
}

// ---------- Rückblick ----------
function renderReview(root) {
  const { stats: st, time, profile, review, maintenance, simHistory } = S.data;
  root.append(h("div", { class: "top" }, h("div", null, h("a", { class: "small", onclick: () => go("plan") }, "← Zurück zum Plan"), h("h1", null, "Rückblick"),
    h("p", { class: "sub" }, "Was hat geklappt – und was lernt der nächste Plan daraus?"))));
  const onTime = st.done ? st.onTime / st.done : 0;
  root.append(h("div", { class: "tiles" },
    tile("Geschafft", String(st.done), st.planned ? st.done / st.planned : 0, "/ " + st.planned),
    tile("Pünktlich", Math.round(100 * onTime) + " %", onTime, ""),
    tile("Tage mit Verzug", String(st.lateDays)),
    tile("Verschoben", String(st.moved), null, "Punkte"),
    time ? tile("Zeit in Anki", hm(time.minutes), null, "") : null));

  root.append(h("div", { class: "card" }, h("h2", null, "Pro Quelle"), h("table", { style: "margin-top:8px" },
    h("tr", null, h("th", null, "Quelle"), h("th", null, "geschafft"), h("th", null, "davon verspätet"), h("th", null, "geplante Zeit")),
    Object.entries(st.perSource).map(([n, s]) => h("tr", null, h("td", null, n), h("td", null, `${s.done}/${s.planned}`), h("td", null, String(s.late)), h("td", null, hm(s.min)))))));

  // Tempo
  const rates = Object.assign({}, profile.rates);
  const measured = time && time.minPerNew;
  const inputs = {};
  const rateRow = (k, label, hint) => { inputs[k] = h("input", { type: "number", step: "0.1", min: 0, value: k === "anki" && measured ? measured : rates[k] }); return [h("label", null, label), h("div", { class: "inline" }, inputs[k], h("span", { class: "muted small" }, hint))]; };
  const suggestMin = onTime < .8 && st.done ? Math.round((profile.minutesPerDay || 180) * Math.max(.6, onTime) / 15) * 15 : null;
  const mpd = h("input", { type: "number", step: 15, min: 0, value: suggestMin || profile.minutesPerDay || 180 });
  const grade = h("input", { type: "text", value: review.grade || "", placeholder: "z. B. bestanden / 2" });
  const feel = h("select", null, ["", "😣 schlecht", "😕 eher schlecht", "😐 ok", "🙂 gut", "😄 sehr gut"].map((l, i) => h("option", { value: i || "", selected: String(review.feeling || "") === String(i || "") || null }, l || "—")));
  const note = h("textarea", { placeholder: "Was würdest du nächstes Mal anders machen?" }); note.value = review.note || "";
  root.append(h("div", { class: "card" }, h("h2", null, "Dein echtes Tempo"),
    h("p", { class: "muted small" }, "Diese Werte nimmt der nächste Plan als Standard. Anki misst die Zeit selbst; für Seiten und Videos schätzt du kurz."),
    h("div", { class: "form", style: "margin-top:8px" },
      rateRow("pages", "Minuten pro Seite", "Handbuch/Skript"),
      rateRow("videos", "Minuten pro Video", "falls keine Dauer angegeben"),
      rateRow("anki", "Minuten pro neue Karte", measured ? `gemessen: ${measured} (inkl. Wiederholungen)` : "inkl. späterer Wiederholungen"),
      h("label", null, "Lernzeit pro Tag"), h("div", { class: "inline" }, mpd, h("span", { class: "muted small" }, suggestMin ? `Vorschlag, weil nur ${Math.round(100 * onTime)} % pünktlich waren` : "Minuten")),
      h("label", null, "Ergebnis"), grade, h("label", null, "Gefühl"), feel),
    h("div", { style: "margin-top:8px" }, note),
    h("div", { class: "bar-actions", style: "margin-top:8px" }, h("button", { class: "primary", onclick: async () => {
      await run(call("saveReview", { id: S.pid, review: { grade: grade.value, feeling: +feel.value || null, note: note.value }, rates: Object.fromEntries(Object.entries(inputs).map(([k, i]) => [k, +i.value])), minutesPerDay: +mpd.value }));
      toast("Gespeichert – der nächste Plan nutzt dieses Tempo.");
    } }, "Speichern"))));

  if (simHistory.length) root.append(h("div", { class: "card" }, h("h2", null, "Probeprüfungen"), simHistory.map(s => h("div", null, h("h3", null, fmt(s.at)), simTable(s.result)))));

  // Danach
  const rpd = h("input", { type: "number", min: 5, step: 5, value: maintenance.reviewsPerDay || 50 });
  root.append(h("div", { class: "card" }, h("h2", null, "Und jetzt?"), h("div", { class: "panel-tools" },
    h("div", { class: "tool" }, h("b", null, "Erhaltungsmodus"), h("p", null, "Die Decks laufen weiter, aber ohne neue Karten und mit gedeckelten Wiederholungen – damit bis zur großen Prüfung nichts verloren geht. Ausschalten stellt die alten Deck-Optionen wieder her."),
      maintenance.on ? h("button", { onclick: async () => { await run(call("maintenance", { id: S.pid, on: false })); toast("Erhaltungsmodus aus, alte Optionen zurück."); go("review"); } }, "Erhaltungsmodus ausschalten")
        : h("div", { class: "inline" }, rpd, h("span", { class: "muted small" }, "Wdh./Tag"), h("button", { class: "primary", onclick: async () => { await run(call("maintenance", { id: S.pid, on: true, reviewsPerDay: +rpd.value })); toast("Erhaltungsmodus an."); go("review"); } }, "Einschalten"))),
    h("div", { class: "tool" }, h("b", null, "Archivieren"), h("p", null, "Der Plan wandert ins Archiv und bleibt abrufbar, z. B. für die Gesamtprüfung."),
      h("button", { onclick: async () => { await run(call("archive", { id: S.pid, on: true })); toast("Archiviert."); go("home"); } }, "Archivieren")),
    h("div", { class: "tool" }, h("b", null, "Nächster Plan"), h("p", null, "Übernimmt deine Quellen-Arten und dein Tempo. Du gibst nur Fach, Stoff und Prüfungsdatum ein."),
      h("button", { class: "primary", onclick: async () => { S.data.today = (await call("home")).today; newPlan(S.pid); } }, "Nächsten Plan anlegen")))));
}

// ---------- Start ----------
function start() {
  go("home");
  setInterval(() => { if (!document.hidden && S.view === "plan" && !document.querySelector(".modal-bg")) refresh(); }, 60000);
}
if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start); else start();
})();
