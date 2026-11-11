// Smart Study UI. Data comes from Python via pycmd("lp:{cmd,args}").
(() => {
"use strict";

// ---------- Language ----------
// Set in start() from data-lang (the add-on's language): "de", "en" or "fa".
let LANG = "en";
const L = (de, en, fa) => LANG === "de" ? de : LANG === "fa" && fa !== undefined ? fa : en;
const plural = (n, de1, deN, en1, enN, fa) => n === 1 ? L(de1, en1, fa) : L(deN, enN, fa);
const COMMA = () => L(", ", ", ", "، ");
const days = n => plural(n, "Tag", "Tage", "day", "days", "روز");

// ---------- Helpers ----------
const WD = () => L(["So", "Mo", "Di", "Mi", "Do", "Fr", "Sa"], ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"], ["یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه", "شنبه"]);
const MON = () => LANG === "fa"
  ? ["ژانویه", "فوریه", "مارس", "آوریل", "مه", "ژوئن", "ژوئیه", "اوت", "سپتامبر", "اکتبر", "نوامبر", "دسامبر"]
  : ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const WD_MO = () => [0, 1, 2, 3, 4, 5, 6].map(n => [WD()[(n + 1) % 7], n]); // Python weekdays (Mon = 0)
const TYPES = () => ({ pages: L("Seiten", "Pages", "صفحه‌ها"), videos: L("Videos", "Videos", "ویدیوها"), tasks: L("Aufgaben", "Tasks", "تکلیف‌ها"), anki: "Anki" });
const UNIT = () => ({ pages: L("min/Seite", "min/page", "دقیقه/صفحه"), videos: L("min/video", "min/video", "دقیقه/ویدیو"), tasks: L("min/Aufgabe", "min/task", "دقیقه/تکلیف"), anki: L("min/neue Karte", "min/new card", "دقیقه/کارت جدید") });

// Listeners live in e._on and are reached through one forwarding listener per
// event type. morph() can then hand a kept element the handlers of its fresh
// twin, so no handler ever works with data of an earlier render.
function listen(e, type, fn) {
  if (!e._on) e._on = {};
  if (!(type in e._on)) e.addEventListener(type, ev => { const f = e._on[type]; if (f) return f.call(e, ev); });
  e._on[type] = fn;
}
function h(tag, attrs, ...kids) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v == null || v === false) continue;
    if (k === "class") e.className = v;
    else if (k === "key") e.dataset.key = v;
    else if (k.startsWith("on")) listen(e, k.slice(2), v);
    else if (k === "value") { e.value = v; e._v = String(v); }
    else if (k === "checked") e.checked = !!v;
    else e.setAttribute(k, v === true ? "" : v);
  }
  for (const c of kids.flat(9)) if (c != null && c !== false) e.append(c.nodeType ? c : String(c));
  return e;
}
function svg(tag, attrs, ...kids) {
  const e = document.createElementNS("http://www.w3.org/2000/svg", tag);
  for (const [k, v] of Object.entries(attrs || {})) if (v != null && v !== false) e.setAttribute(k, v);
  for (const c of kids.flat(9)) if (c) e.append(c);
  return e;
}

// ---------- Motion ----------
const EASE = "cubic-bezier(.2, .8, .2, 1)";
const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)");
function motion() {
  return !reducedMotion.matches && !document.hidden
    && !document.documentElement.classList.contains("reduce-motion")
    && !(document.body && document.body.classList.contains("reduce-motion"));
}
function animate(el, frames, opts) {
  if (!motion() || !el.animate) return null;
  try { return el.animate(frames, Object.assign({ duration: 220, easing: EASE }, opts)); } catch { return null; }
}
// Numbers count to their new value instead of jumping.
function tween(node, from, to) {
  const id = node._tw = (node._tw || 0) + 1, t0 = performance.now(), dur = 480;
  if (!motion()) { node.data = String(to); return; }
  const step = now => {
    if (node._tw !== id) return;
    const p = Math.min(1, (now - t0) / dur), e = 1 - Math.pow(1 - p, 3);
    node.data = String(Math.round(from + (to - from) * e));
    if (p < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
  setTimeout(() => { if (node._tw === id) node.data = String(to); }, dur + 120);  // also when frames are paused
}

// ---------- Morph ----------
// render() builds a fresh tree; morph() makes the page look like it while keeping
// the existing elements. So a refresh changes only what really changed: nothing
// flickers, the field you type in keeps focus and text, bars and rings glide to
// their new value, and added or removed rows slide in and out.
const keyOf = n => n.nodeType === 1 && n.dataset ? n.dataset.key : undefined;
const sameKind = (a, b) => a.nodeType === b.nodeType && a.nodeName === b.nodeName;
let morphBudget = 0;  // how many rows may still animate in this pass (a hundred at once would stutter)
function morphInto(root, fresh) {
  morphBudget = 14;
  morphKids(root, fresh);
}
function morphKids(from, to) {
  const keyed = new Map();
  for (const n of from.childNodes) { const k = keyOf(n); if (k !== undefined && !n._leaving) keyed.set(k, n); }
  let cursor = from.firstChild;
  for (const want of [...to.childNodes]) {
    const k = keyOf(want);
    let match = null;
    if (k !== undefined) { const c = keyed.get(k); if (c && sameKind(c, want)) match = c; }
    else {
      let c = cursor;
      while (c && c._leaving) c = c.nextSibling;
      if (c && keyOf(c) === undefined && sameKind(c, want)) match = c;
    }
    if (!match) { from.insertBefore(want, cursor); enter(want); continue; }
    if (match === cursor) cursor = cursor.nextSibling; else from.insertBefore(match, cursor);
    if (want.nodeType === 1 && want.dataset.morph === "replace") match.replaceWith(want);
    else if (!(want.nodeType === 1 && want.dataset.morph === "keep")) morphNode(match, want);
  }
  while (cursor) { const next = cursor.nextSibling; if (!cursor._leaving) leave(cursor); cursor = next; }
}
function morphNode(from, to) {
  if (from.nodeType !== 1) {
    if (from.data !== to.data) {
      const p = from.parentNode;
      if (p && p.dataset && "num" in p.dataset && /^\d+$/.test(from.data) && /^\d+$/.test(to.data)) tween(from, +from.data, +to.data);
      else { from._tw = 0; from.data = to.data; }
    }
    return;
  }
  for (const a of [...from.attributes]) if (!to.hasAttribute(a.name)) from.removeAttribute(a.name);
  for (const a of to.attributes) if (from.getAttribute(a.name) !== a.value) from.setAttribute(a.name, a.value);
  for (const type of new Set([...Object.keys(from._on || {}), ...Object.keys(to._on || {})])) listen(from, type, (to._on || {})[type] || null);
  morphKids(from, to);
  const tag = from.nodeName;
  if (tag === "INPUT" && (from.type === "checkbox" || from.type === "radio")) { if (from.checked !== to.checked) from.checked = to.checked; }
  else if (tag === "SELECT") { if (from.value !== to.value) from.value = to.value; }
  else if ((tag === "INPUT" || tag === "TEXTAREA") && from._v !== to._v) { from.value = to.value; from._v = to._v; }  // only what render() changed; typed text stays
}
const SLIDES = ".item, .day, .card, .row, .topic, .src, .ms-row, .plan-card";
function enter(n) {
  if (n.nodeType !== 1 || !motion()) return;
  if (n.matches(SLIDES) && morphBudget-- > 0) {
    const hgt = n.getBoundingClientRect().height, cs = getComputedStyle(n);
    if (hgt) return animate(n, [
      { height: "0px", opacity: 0, marginTop: "0px", marginBottom: "0px", paddingTop: "0px", paddingBottom: "0px", overflow: "hidden" },
      { height: hgt + "px", opacity: 1, marginTop: cs.marginTop, marginBottom: cs.marginBottom, paddingTop: cs.paddingTop, paddingBottom: cs.paddingBottom, overflow: "hidden" }], { duration: 260 });
  }
  animate(n, [{ opacity: 0 }, { opacity: 1 }], { duration: 200 });
}
function leave(n) {
  if (n.nodeType !== 1 || !motion() || !n.matches(SLIDES) || morphBudget-- <= 0) return n.remove();
  const hgt = n.getBoundingClientRect().height, cs = getComputedStyle(n);
  n._leaving = true;
  n.style.pointerEvents = "none";
  const a = animate(n, [
    { height: hgt + "px", opacity: 1, marginTop: cs.marginTop, marginBottom: cs.marginBottom, paddingTop: cs.paddingTop, paddingBottom: cs.paddingBottom, overflow: "hidden" },
    { height: "0px", opacity: 0, marginTop: "0px", marginBottom: "0px", paddingTop: "0px", paddingBottom: "0px", overflow: "hidden" }], { duration: 220, fill: "forwards" });
  if (!a) return n.remove();
  a.onfinish = a.oncancel = () => n.remove();
}
const dt = s => new Date(s + "T12:00:00");
const fmt = s => { const d = dt(s); return LANG === "de" ? `${WD()[d.getDay()]} ${d.getDate()}.${d.getMonth() + 1}.` : `${WD()[d.getDay()]} ${d.getDate()} ${MON()[d.getMonth()]}`; };
const daysBetween = (a, b) => Math.round((dt(b) - dt(a)) / 864e5);
const addDays = (s, n) => { const d = dt(s); d.setDate(d.getDate() + n); return iso(d); };
const iso = d => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
const uid = p => p + Math.random().toString(16).slice(2, 12);
const clone = o => JSON.parse(JSON.stringify(o));
const dmy = s => s ? `${s.slice(8, 10)}.${s.slice(5, 7)}.${s.slice(0, 4)}` : "";
// Own input fields instead of <input type=date> so it's always DD.MM.YYYY and 24 h
function dateInput(val, onset, attrs) {
  const e = h("input", Object.assign({ type: "text", value: dmy(val), placeholder: L("TT.MM.JJJJ", "DD.MM.YYYY", "DD.MM.YYYY"), style: "width:118px", inputmode: "numeric" }, attrs || {}));
  listen(e, "change", ev => {
    const e = ev.currentTarget, v = e.value.trim();
    if (!v) { onset(""); return; }
    const m = v.match(/^(\d{1,2})[.\/-](\d{1,2})[.\/-]?(\d{2}|\d{4})?$/);
    const y = m && (m[3] ? (m[3].length === 2 ? "20" + m[3] : m[3]) : String(new Date().getFullYear()));
    const out = m && `${y}-${m[2].padStart(2, "0")}-${m[1].padStart(2, "0")}`;
    if (!out || isNaN(dt(out)) || iso(dt(out)) !== out) { toast(L("Datum bitte als TT.MM.JJJJ, z. B. 28.11.2026", "Please enter the date as DD.MM.YYYY, e.g. 28.11.2026", "لطفاً تاریخ را به‌صورت DD.MM.YYYY وارد کنید، مثلاً 28.11.2026")); e.value = dmy(val); return; }
    e.value = dmy(out); val = out; onset(out);
  });
  return e;
}
function timeInput(val, onset) {
  const e = h("input", { type: "text", value: val || "", placeholder: "HH:MM", style: "width:70px", inputmode: "numeric" });
  listen(e, "change", ev => {
    const e = ev.currentTarget, v = e.value.trim();
    if (!v) { onset(""); return; }
    const m = v.match(/^(\d{1,2})(?:[:.h ]?(\d{2}))?$/);
    if (!m || +m[1] > 23 || +(m[2] || 0) > 59) { toast(L("Uhrzeit bitte als HH:MM, z. B. 13:15", "Please enter the time as HH:MM, e.g. 13:15", "لطفاً ساعت را به‌صورت HH:MM وارد کنید، مثلاً 13:15")); e.value = val || ""; return; }
    val = `${m[1].padStart(2, "0")}:${m[2] || "00"}`; e.value = val; onset(val);
  });
  return e;
}
const hm = m => { const H = L("h", "h", "ساعت"), M = L("min", "min", "دقیقه"); return m >= 60 ? `${Math.floor(m / 60)} ${H}${m % 60 ? " " + (m % 60) + " " + M : ""}` : `${m} ${M}`; };

// A thin bar at the top shows that Anki is working (only if it takes noticeably long).
let busyCount = 0, busyTimer = null;
function busy(on) {
  busyCount = Math.max(0, busyCount + (on ? 1 : -1));
  clearTimeout(busyTimer);
  if (busyCount) busyTimer = setTimeout(() => document.documentElement.classList.add("lp-busy"), 180);
  else document.documentElement.classList.remove("lp-busy");
}
function call(cmd, args) {
  busy(true);
  return new Promise((res, rej) => {
    const go = () => pycmd("lp:" + JSON.stringify({ cmd, args }), r => r && r.ok ? res(r.data) : rej(new Error(r ? r.error : L("keine Antwort", "no response", "پاسخی دریافت نشد"))));
    if (typeof pycmd === "function") go();
    else { let n = 0; const t = setInterval(() => { if (typeof pycmd === "function") { clearInterval(t); go(); } else if (++n > 400) { clearInterval(t); rej(new Error(L("keine Verbindung zu Anki", "no connection to Anki", "ارتباط با Anki برقرار نیست"))); } }, 30); }
  }).finally(() => busy(false));
}
// Toasts stack above each other; one may carry an action (e.g. undo).
function toast(msg, ms = 2600, action) {
  let box = document.querySelector(".toasts");
  if (!box) { box = h("div", { class: "toasts", role: "status", "aria-live": "polite" }); document.body.append(box); }
  for (const old of box.children) if (old._msg === msg && !old._closing) old._close();  // the same message twice: show it once
  const t = h("div", { class: "toast" }, h("span", null, msg));
  t._msg = msg;
  let timer = null;
  t._close = () => {
    if (t._closing) return;
    t._closing = true; clearTimeout(timer);
    const a = animate(t, [{ opacity: 1, transform: "none" }, { opacity: 0, transform: "translateY(8px) scale(.96)" }], { duration: 180, fill: "forwards" });
    if (a) a.onfinish = a.oncancel = () => t.remove(); else t.remove();
  };
  if (action) t.append(h("button", { class: "toast-act", onclick: () => { t._close(); action[1](); } }, action[0]));
  box.append(t);
  animate(t, [{ opacity: 0, transform: "translateY(14px) scale(.96)" }, { opacity: 1, transform: "none" }], { duration: 240 });
  const arm = () => { timer = setTimeout(t._close, ms); };
  listen(t, "mouseenter", () => clearTimeout(timer));
  listen(t, "mouseleave", arm);
  arm();
  while (box.children.length > 4) box.firstChild.remove();
  return t;
}
async function run(p) { try { return await p; } catch (e) { toast(L("Fehler: ", "Error: ", "خطا: ") + (e && e.message || e), 5000); throw e; } }
// Dialog: Esc cancels, Enter takes the primary button, Tab stays inside, focus returns afterwards.
function modal(title, body, buttons) {
  return new Promise(res => {
    const before = document.activeElement;
    const bg = h("div", { class: "modal-bg" });
    let closed = false;
    const close = v => {
      if (closed) return;
      closed = true;
      document.removeEventListener("keydown", onKey, true);
      const done = () => { bg.remove(); if (before && before.focus && document.contains(before)) before.focus(); };
      const a = animate(bg, [{ opacity: 1 }, { opacity: 0 }], { duration: 150, fill: "forwards" });
      animate(box, [{ transform: "none" }, { transform: "translateY(8px) scale(.97)" }], { duration: 150, fill: "forwards" });
      if (a) a.onfinish = a.oncancel = done; else done();
      res(v);
    };
    const btns = (buttons || [[L("Abbrechen", "Cancel", "انصراف"), null], [L("OK", "OK", "تأیید"), true, "primary"]]).map(([l, v, c]) => h("button", { class: c, onclick: () => close(typeof v === "function" ? v() : v) }, l));
    const box = h("div", { class: "modal", role: "dialog", "aria-modal": "true", "aria-label": title }, h("h2", null, title), h("div", { style: "margin-top:10px" }, body), h("div", { class: "foot" }, btns));
    bg.append(box);
    const onKey = e => {
      if (document.querySelectorAll(".modal-bg").length && bg !== [...document.querySelectorAll(".modal-bg")].pop()) return;  // only the top dialog
      if (e.key === "Escape") { e.preventDefault(); e.stopPropagation(); close(null); }
      else if (e.key === "Enter" && !e.shiftKey && !(e.target && (e.target.nodeName === "TEXTAREA" || e.target.nodeName === "BUTTON"))) {
        const prim = btns.find(b => b.classList.contains("primary")) || (btns.length === 1 ? btns[0] : null);
        if (prim) { e.preventDefault(); if (e.target && e.target.blur) e.target.blur(); prim.click(); }
      } else if (e.key === "Tab") {
        const f = [...box.querySelectorAll("input,textarea,select,button,a[href]")].filter(x => !x.disabled && x.offsetParent);
        if (!f.length) return;
        const first = f[0], last = f[f.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
        else if (!box.contains(document.activeElement)) { e.preventDefault(); first.focus(); }
      }
    };
    document.addEventListener("keydown", onKey, true);
    let downOnBg = false;  // a drag that starts in a field and ends outside must not close the dialog
    bg.addEventListener("mousedown", e => { downOnBg = e.target === bg; });
    bg.addEventListener("click", e => { if (e.target === bg && downOnBg) close(null); });
    document.body.append(bg);
    animate(bg, [{ opacity: 0 }, { opacity: 1 }], { duration: 160 });
    animate(box, [{ transform: "translateY(14px) scale(.96)", opacity: 0 }, { transform: "none", opacity: 1 }], { duration: 240 });
    const f = box.querySelector("input,textarea,select") || btns.find(b => b.classList.contains("primary")) || btns[0];
    if (f) f.focus();
  });
}
const store = {
  get(k) { try { return JSON.parse(localStorage.getItem("lp." + k)); } catch { return null; } },
  set(k, v) { try { localStorage.setItem("lp." + k, JSON.stringify(v)); } catch {} },
};

// ---------- State ----------
const S = { view: "home", pid: null, data: null, edit: null, editBase: null, showPast: false, simTimer: null, cands: {}, sugg: {},
  deckInfo: {}, epoch: 0, nav: 0, seq: 0, pending: new Map(), mock: null, dayDone: new Map(), cheer: false };
const app = () => document.getElementById("app");
const DEPTH = { home: 0, plan: 1, edit: 2, review: 2 };

const dirty = () => S.view === "edit" && !!S.edit && JSON.stringify(S.edit) !== S.editBase;
async function leaveEdit() {
  if (!dirty()) return true;
  const v = await modal(L("Änderungen speichern?", "Save your changes?", "تغییرات ذخیره شوند؟"),
    h("p", { style: "margin:0" }, L("Du hast diesen Plan bearbeitet, aber noch nicht gespeichert.", "You have edited this plan but not saved it yet.", "این برنامه را ویرایش کرده‌اید اما هنوز ذخیره نکرده‌اید.")),
    [[L("Weiter bearbeiten", "Keep editing", "ادامهٔ ویرایش"), null], [L("Verwerfen", "Discard", "دور ریختن"), "drop", "danger"], [L("Speichern", "Save", "ذخیره"), "save", "primary"]]);
  if (v === "save") { await run(call("savePlan", { plan: S.edit })); S.editBase = JSON.stringify(S.edit); }
  return !!v;
}

async function go(view, pid) {
  if (S.view === "edit" && !(await leaveEdit())) return;
  const nav = ++S.nav, target = pid !== undefined ? pid : S.pid;
  let data = S.data, edit = S.edit;
  if (view === "home") data = await run(call("home"));
  if (view === "plan") data = await run(call("open", { id: target }));
  if (view === "edit") {
    const d = await run(call("open", { id: target }));
    data = d;
    edit = clone(d.plan);
    for (const s of edit.sources) if (s.type === "pages" && d.files && d.files[s.id]) s.file = d.files[s.id];  // the path on this device
    for (const s of edit.sources) if (s.type === "anki" && !s.decks) { s.decks = s.deck ? [s.deck] : []; delete s.deck; }
  }
  if (view === "review") data = await run(call("review", { id: target }));
  if (nav !== S.nav) return;  // another click was faster
  if (view === "plan" && data.phase === "setup") return go("edit", target);  // nothing scheduled yet
  const back = DEPTH[view] < DEPTH[S.view];
  S.pid = target; S.data = data;
  if (S.mock && S.mock.pid !== target) { clearInterval(S.simTimer); S.mock = null; }
  if (view === "edit") { S.edit = edit; S.editBase = JSON.stringify(edit); S.cands = {}; S.sugg = {}; S.deckInfo = {}; S.epoch++; await loadCands(); if (nav !== S.nav) return; }
  S.view = view; S.pending.clear(); S.dayDone.clear();
  transition(back, () => { render(false); window.scrollTo(0, 0); });
}
// Views slide over each other (forwards from the right, back from the left).
function transition(back, fn) {
  if (!motion() || !document.startViewTransition) return fn();
  document.documentElement.dataset.nav = back ? "back" : "fwd";
  try { document.startViewTransition(fn); } catch { fn(); }
}
function apply(kind, data) {
  if (kind !== S.view || (kind === "plan" && data.plan.id !== S.pid)) return false;
  S.data = data;
  render();
  return true;
}
// Fetches the current view again. after(): runs once the answer is there, before drawing.
async function refresh(after) {
  if (S.view !== "plan" && S.view !== "home") { if (after) after(); return; }
  const kind = S.view, seq = ++S.seq, nav = S.nav;
  let data;
  try { data = await call(kind === "plan" ? "open" : "home", { id: S.pid }); }
  finally { if (after) after(); }
  if (seq !== S.seq || nav !== S.nav) return;  // a newer answer is on its way or the view changed
  apply(kind, data);
}
// Python hands over data it collected in the background (after reviews in Anki, a sync …).
function push(kind, data) { apply(kind, data); }
window.LP = { refresh, go, push, dirty: () => dirty() ? S.edit : null, saved: () => { if (S.edit) S.editBase = JSON.stringify(S.edit); } };

// morph = keep the page and change only what differs (default); false = draw anew (after navigation).
function render(morph = true) {
  const root = app();
  const fresh = document.createDocumentFragment();
  const view = S.view;
  ({ home: renderHome, plan: renderPlan, edit: renderEdit, review: renderReview })[view](fresh);
  if (morph && root.dataset.view === view && view !== "review") morphInto(root, fresh);
  else {
    root.replaceChildren(fresh);
    root.dataset.view = view;
    root.classList.remove("lp-in");
    if (motion()) { void root.offsetWidth; root.classList.add("lp-in"); }
  }
  afterRender();
}
function afterRender() {
  // A day that just became complete through your own tick gets a little party.
  for (const el of document.querySelectorAll("#app .day[data-key]")) {
    const k = el.dataset.key, done = el.dataset.complete === "1", was = S.dayDone.get(k);
    if (S.cheer && was === false && done) dayParty(el);
    S.dayDone.set(k, done);
  }
  S.cheer = false;
  watchToday();
}

// ---------- Overview ----------
function renderHome(root) {
  const d = S.data;
  root.append(h("div", { class: "top" },
    h("div", null, h("h1", null, "Smart Study"), h("p", { class: "sub" }, L("Pläne bis zur Prüfung – Anki hakt sich selbst ab.", "Study plans up to your exam – Anki checks itself off.", "برنامهٔ مطالعه تا روز امتحان – Anki موارد را خودش تیک می‌زند."))),
    h("div", { class: "bar-actions" },
      h("button", { onclick: () => importDialog(), title: L("Plan von Freunden übernehmen (Code oder Datei)", "Use a plan from friends (code or file)", "استفاده از برنامهٔ دوستان (کد یا فایل)") }, L("Importieren", "Import", "وارد کردن")),
      h("button", { class: "primary", onclick: () => newPlan() }, L("+ Neuer Plan", "+ New plan", "+ برنامهٔ جدید")))));

  const open = d.plans.filter(p => p.status === "active" && p.today).reduce((a, p) => [a[0] + p.today[0], a[1] + p.today[1], a[2] + p.today[2]], [0, 0, 0]);
  const tiles = h("div", { class: "tiles" },
    tile(L("Lern-Serie", "Study streak", "روزهای پیاپی مطالعه"), String(d.streak), null, days(d.streak) + (d.streak >= 3 ? " 🔥" : "")),
    tile(L("Aktive Pläne", "Active plans", "برنامه‌های فعال"), String(d.plans.filter(p => p.status === "active").length)),
    open[1] ? tile(L("Heute", "Today", "امروز"), String(open[0]), open[0] / open[1], "/ " + open[1] + (open[2] ? ` · ≈ ${hm(open[2])} ${L("offen", "left", "مانده")}` : " ✓")) : null);
  root.append(tiles, heatmap(d.heat, d.today));

  const act = d.plans.filter(p => p.status === "active"), arch = d.plans.filter(p => p.status !== "active");
  root.append(h("h3", null, L("Aktiv", "Active", "فعال")));
  if (!act.length) root.append(h("div", { class: "card muted" }, L("Noch kein Plan. Leg mit „+ Neuer Plan“ los.", "No plan yet. Get started with “+ New plan”.", "هنوز برنامه‌ای ندارید. با «+ برنامهٔ جدید» شروع کنید.")));
  root.append(h("div", { class: "plans" }, act.map(planCard)));
  if (arch.length) {
    root.append(h("details", { open: store.get("archOpen") || null, ontoggle: e => store.set("archOpen", e.target.open) }, h("summary", null, `${L("Archiv", "Archive", "بایگانی")} (${arch.length})`), h("div", { class: "plans" }, arch.map(planCard))));
  }
  root.append(h("p", { class: "muted small", style: "margin-top:30px" }, `Smart Study ${d.version} · ${L("Pläne liegen im Add-on-Ordner unter user_files/plans.", "Plans are stored in the add-on folder under user_files/plans.", "برنامه‌ها در پوشهٔ افزونه، در مسیر user_files/plans ذخیره می‌شوند.")}`));
}
function planCard(p) {
  const left = p.exam ? daysBetween(S.data.today, p.exam) : null, [dn, tot] = p.progress;
  const td = p.status === "active" && p.today && p.today[1] ? p.today : null;
  const openIt = () => go("plan", p.id);
  return h("div", { class: "card plan-card" + (left != null && left >= 0 && left <= 3 && p.status === "active" ? " soon" : ""), key: p.id, tabindex: 0, role: "button", onclick: openIt,
    onkeydown: e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); openIt(); } } },
    h("div", { class: "days-left" }, left == null ? "?" : left > 0 ? String(left) : left === 0 ? L("heute", "today", "امروز") : "✓",
      h("small", null, left == null ? L("Entwurf", "draft", "پیش‌نویس") : left > 0 ? days(left) : left === 0 ? L("Prüfung", "exam", "امتحان") : L("vorbei", "over", "تمام‌شده"))),
    h("div", { class: "grow" }, h("h2", null, p.title),
      h("div", { class: "muted small" }, p.exam ? `${L("Prüfung", "Exam", "امتحان")} ${fmt(p.exam)}${COMMA()}${dmy(p.exam)} · ${dn}/${tot} ${L("erledigt", "done", "انجام‌شده")}` : L("Entwurf – Prüfungsdatum fehlt noch", "Draft – exam date still missing", "پیش‌نویس – تاریخ امتحان هنوز وارد نشده است")),
      h("div", { class: "pbar" + (tot && dn === tot ? " ok" : "") }, h("i", { style: `width:${tot ? 100 * dn / tot : 0}%` }))),
    td ? h("div", { class: "today-chip" + (td[0] === td[1] ? " done" : ""), title: L("Heutige Punkte", "Today's items", "موارد امروز") }, ring(td[0] / td[1], 30),
      h("small", null, td[0] === td[1] ? L("heute fertig", "done today", "امروز تمام") : `${td[0]}/${td[1]} ${L("heute", "today", "امروز")}`)) : null,
    h("span", { class: "chev", "aria-hidden": "true" }, "›"));
}
// Progress ring; a full ring shows a tick.
function ring(frac, size = 22) {
  const r = 9, c = 2 * Math.PI * r, f = Math.max(0, Math.min(1, frac || 0));
  return svg("svg", { class: "ring" + (f >= 1 ? " full" : ""), viewBox: "0 0 24 24", width: size, height: size, "aria-hidden": "true" },
    svg("circle", { cx: 12, cy: 12, r, class: "bg" }),
    svg("circle", { cx: 12, cy: 12, r, class: "fg", "stroke-dasharray": c.toFixed(2), style: `stroke-dashoffset:${(c * (1 - f)).toFixed(2)}` }),
    f >= 1 ? svg("path", { d: "M7.6 12.4l3 3 5.8-6.4", class: "tick" }) : null);
}
function heatmap(heat, today) {
  const vals = Object.values(heat).filter(v => v > 0).sort((a, b) => a - b);
  const q = f => vals.length ? vals[Math.floor((vals.length - 1) * f)] : 1;
  const lv = v => !v ? "" : v <= q(.25) ? "l1" : v <= q(.5) ? "l2" : v <= q(.8) ? "l3" : "l4";
  const end = dt(today), start = new Date(end); start.setDate(end.getDate() - 7 * 26 - ((end.getDay() + 6) % 7));
  const grid = h("div", { class: "heat" });
  let n = 0;
  for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
    const s = iso(d), v = heat[s] || 0;
    grid.append(h("i", { class: lv(v) + (s === today ? " td" : ""), style: `--c:${Math.floor(n++ / 7)}`, title: `${fmt(s)}: ${v} ${L("Bewertungen/Häkchen", "ratings/checkmarks", "ارزیابی/تیک")}` }));
  }
  return h("div", { class: "card" }, h("div", { class: "muted small", style: "margin-bottom:6px" }, L("Letzte 6 Monate (Anki-Bewertungen + abgehakte Punkte)", "Last 6 months (Anki ratings + checked items)", "6 ماه گذشته (ارزیابی‌های Anki + موارد تیک‌خورده)")), grid);
}
async function newPlan(from) {
  const t = S.data.today || iso(new Date());
  const title = h("input", { type: "text", placeholder: L("z. B. Kopf-Hals-Testat", "e.g. Head & neck exam", "مثلاً امتحان سر و گردن"), style: "width:100%" });
  let examV = "", startV = t;
  const exam = dateInput("", v => { examV = v; }), start = dateInput(t, v => { startV = v; });
  const ok = await modal(from ? L("Nächsten Plan anlegen", "Create next plan", "ساخت برنامهٔ بعدی") : L("Neuer Plan", "New plan", "برنامهٔ جدید"), h("div", { class: "form" },
    h("label", null, L("Name", "Name", "نام")), title, h("label", null, L("Prüfungsdatum", "Exam date", "تاریخ امتحان")), h("div", { class: "inline" }, exam, h("span", { class: "muted small" }, L("leer lassen, wenn noch unbekannt", "leave empty if not known yet", "اگر هنوز مشخص نیست، خالی بگذارید"))), h("label", null, L("Start", "Start", "شروع")), start,
    from ? h("p", { class: "muted small", style: "grid-column:1/-1" }, L("Die Quellen-Arten (Handbuch, Videos, Anki …) und dein Tempo werden übernommen. Decks, Seiten und Themen trägst du neu ein.", "Your source types (book, videos, Anki …) and your pace are carried over. You enter decks, pages and topics anew.", "نوع منابع (کتاب، ویدیو، Anki …) و سرعت شما منتقل می‌شوند. دسته‌ها، صفحه‌ها و موضوع‌ها را از نو وارد می‌کنید.")) : null));
  if (!ok) return;
  exam.dispatchEvent(new Event("change")); start.dispatchEvent(new Event("change"));
  if (!title.value.trim()) return toast(L("Bitte einen Namen eingeben.", "Please enter a name.", "لطفاً یک نام وارد کنید."));
  if (examV && examV <= startV) return toast(L("Die Prüfung muss nach dem Start liegen.", "The exam has to be after the start.", "امتحان باید بعد از تاریخ شروع باشد."));
  const p = await run(call("create", { title: title.value.trim(), exam: examV, start: startV, from }));
  go("edit", p.id);
}

function tile(k, v, frac, sub) {
  const t = h("div", { class: "tile" }, h("div", { class: "k" }, k), h("div", { class: "v" }, h("span", { "data-num": "" }, v), sub ? h("small", null, " " + sub) : null));
  if (frac != null) t.append(h("div", { class: "pbar" + (frac >= 1 ? " ok" : "") }, h("i", { style: `width:${Math.min(100, 100 * frac)}%` })));
  return t;
}

// ---------- Plan view ----------
function itemDone(it) {
  const d = S.data;
  if (S.pending.has(it.id)) return S.pending.get(it.id) || !!(d.ev[it.id] && d.ev[it.id].done);  // your click counts at once
  return !!(d.plan.done[it.id] || (d.ev[it.id] && d.ev[it.id].done));
}

function renderPlan(root) {
  const { plan, stats, progress, phase, overdue } = S.data;
  const today = stats.today, left = daysBetween(today, plan.exam);
  if (phase === "setup") { setTimeout(() => { if (S.view === "plan") go("edit"); }); return; }
  root.append(h("div", { class: "top" },
    h("div", null, h("a", { class: "small", onclick: () => go("home") }, L("← Alle Pläne", "← All plans", "→ همهٔ برنامه‌ها")), h("h1", null, plan.title),
      h("p", { class: "sub" }, `${L("Prüfung", "Exam", "امتحان")} ${fmt(plan.exam)} ${plan.exam.slice(0, 4)}${plan.examTime ? COMMA() + plan.examTime + L(" Uhr", "", "") : ""}${plan.subtitle ? " · " + plan.subtitle : ""}`)),
    h("div", { class: "bar-actions" },
      h("button", { onclick: () => go("edit") }, L("Bearbeiten", "Edit", "ویرایش")),
      h("button", { onclick: () => replan() }, L("Neu planen", "Replan", "برنامه‌ریزی دوباره")),
      h("button", { onclick: () => go("review") }, L("Rückblick", "Retrospective", "جمع‌بندی")),
      h("button", { onclick: () => shareDialog() }, L("Teilen", "Share", "اشتراک‌گذاری")))));

  (plan.notes || []).forEach((n, i) => root.append(h("div", { class: "card warn", key: "note" + i }, n)));

  // Tiles
  const tiles = h("div", { class: "tiles" });
  tiles.append(tile(L("Bis zur Prüfung", "Until the exam", "تا امتحان"), left > 0 ? String(left) : left === 0 ? L("heute", "today", "امروز") : L("vorbei", "over", "تمام‌شده"), null, left > 0 ? days(left) : ""));
  const nextMs = (plan.milestones || []).filter(m => !m.prep && m.date && m.date >= today && m.date < plan.exam).sort((a, b) => a.date.localeCompare(b.date))[0];
  if (nextMs) { const n = daysBetween(today, nextMs.date); tiles.append(tile(nextMs.name || L("Nächste Etappe", "Next milestone", "مرحلهٔ بعدی"), n ? String(n) : L("heute", "today", "امروز"), null, n ? days(n) : "")); }
  tiles.append(tile(L("Plan erledigt", "Plan done", "انجام‌شده از برنامه"), `${progress[0]}`, progress[1] ? progress[0] / progress[1] : 0, "/ " + progress[1]));
  for (const s of plan.sources) {
    if (s.type === "anki" && stats.decks[s.id]) {
      const c = stats.decks[s.id], seen = c.total - c.new;
      tiles.append(tile(s.name, String(seen), c.total ? seen / c.total : 0, "/ " + c.total + L(" gesehen", " seen", " دیده‌شده")));
    } else if (s.type !== "anki") {
      const its = allItems(plan).filter(([, it]) => it.source === s.id && !it.moved);
      if (s.type === "pages") {
        const pg = its.reduce((a, [, it]) => a + it.pages[1] - it.pages[0] + 1, 0), dn = its.filter(([, it]) => itemDone(it)).reduce((a, [, it]) => a + it.pages[1] - it.pages[0] + 1, 0);
        tiles.append(tile(s.name, String(dn), pg ? dn / pg : 0, "/ " + pg + L(" S.", " pp.", " ص.")));
      } else {
        const dn = its.filter(([, it]) => itemDone(it)).length;
        tiles.append(tile(s.name, String(dn), its.length ? dn / its.length : 0, "/ " + its.length));
      }
    }
  }
  if (plan.sources.some(s => s.type === "anki")) tiles.append(tile(L("Jetzt fällig", "Due now", "موعد رسیده"), String(stats.due), null, stats.due === 0 ? "✓" : L("Karten", "cards", "کارت")));
  root.append(tiles);

  if (S.mock) root.append(mockPanel());

  if (overdue.length) root.append(h("div", { class: "card warn", key: "overdue" }, h("h2", null, L(`${overdue.length} Punkte von vergangenen Tagen offen`, `${overdue.length} items from past days still open`, `${overdue.length} مورد از روزهای گذشته هنوز باز است`)),
    h("p", { class: "small", style: "margin:4px 0 8px" }, L("„Neu planen“ verteilt sie (und alles andere, was noch offen ist) auf die Tage bis zur Prüfung.", "“Replan” spreads them (and everything else still open) over the days until the exam.", "«برنامه‌ریزی دوباره» آن‌ها را (و هر چیز دیگری که هنوز باز است) روی روزهای باقی‌مانده تا امتحان پخش می‌کند.")),
    h("button", { class: "primary", onclick: () => replan() }, L("Jetzt neu planen", "Replan now", "همین حالا دوباره برنامه‌ریزی کنید"))));

  if (phase === "early") {
    root.append(h("div", { class: "card okc", key: "early" }, h("h2", null, L(`Alles geschafft – noch ${left} ${days(left)} bis zur Prüfung 🎉`, `All done – ${left} ${days(left)} left until the exam 🎉`, `همه‌چیز انجام شد – ${left} ${days(left)} تا امتحان مانده است 🎉`)),
      h("p", { class: "small", style: "margin:4px 0 0" }, L("Jetzt nicht ausruhen auf dem Plan, sondern festigen:", "Don't rest on the plan now, consolidate instead:", "حالا به برنامه بسنده نکنید، آموخته‌ها را تثبیت کنید:")), toolsPanel(true)));
    celebrate(plan.id);
  } else if (phase === "after") {
    root.append(h("div", { class: "card hl", key: "after" }, h("h2", null, L("Die Prüfung ist vorbei", "The exam is over", "امتحان تمام شد")),
      h("p", { class: "small", style: "margin:4px 0 8px" }, L("Schau dir den Rückblick an: Was hat geklappt, wie schnell warst du wirklich? Das Tempo fließt in den nächsten Plan ein.", "Have a look at the retrospective: what worked, how fast were you really? Your pace feeds into the next plan.", "نگاهی به جمع‌بندی بیندازید: چه چیزی خوب پیش رفت و سرعت واقعی شما چقدر بود؟ این سرعت در برنامهٔ بعدی لحاظ می‌شود.")),
      h("div", { class: "bar-actions" }, h("button", { class: "primary", onclick: () => go("review") }, L("Zum Rückblick", "Open retrospective", "رفتن به جمع‌بندی")),
        h("button", { onclick: async () => { await run(call("archive", { id: plan.id, on: true })); toast(L("Archiviert.", "Archived.", "بایگانی شد.")); go("home"); } }, L("Archivieren", "Archive", "بایگانی")))));
  } else {
    root.append(h("details", { key: "tools", open: store.get("toolsOpen") || null, ontoggle: e => store.set("toolsOpen", e.target.open) },
      h("summary", null, L("Werkzeuge: Schwachstellen · Probeprüfung", "Tools: weak spots · mock exam", "ابزارها: نقاط ضعف · امتحان آزمایشی")), toolsPanel(false)));
  }
  if (progress[1] && progress[0] === progress[1] && phase !== "after") celebrate(plan.id);

  // Days
  const past = plan.days.filter(d => d.d < today), rest = plan.days.filter(d => d.d >= today);
  if (past.length) root.append(h("p", { key: "pasttoggle" }, h("a", { class: "small", onclick: () => { S.showPast = !S.showPast; render(); } },
    S.showPast ? L("Vergangene Tage ausblenden", "Hide past days", "پنهان کردن روزهای گذشته") : `${L("Vergangene Tage zeigen", "Show past days", "نمایش روزهای گذشته")} (${past.length})`)));
  for (const day of S.showPast ? plan.days : rest) root.append(dayCard(day, today));
  root.append(h("p", { class: "muted small", key: "legend", style: "margin-top:20px" }, L("Punkte mit ", "Items marked ", "مواردی که با "), h("span", { class: "chip ok" }, "Anki"),
    L(" hakt der Plan selbst ab, sobald du in Anki lernst. Alles andere per Klick.", " are checked off by the plan as soon as you study in Anki. Everything else with a click.", " مشخص شده‌اند، به‌محض مطالعه در Anki خودکار تیک می‌خورند. بقیه را با یک کلیک تیک بزنید.")));
}
function allItems(plan) { return plan.days.flatMap(d => d.items.map(it => [d, it])); }

function groupLabel(it, plan) {
  if (it.kind === "reviews" || it.kind === "cards") { const s = plan.sources.find(s => s.id === it.source); return it.kind === "reviews" ? "Anki" : (s ? s.name : "Anki"); }
  if (it.source) { const s = plan.sources.find(s => s.id === it.source); if (s) return s.name; }
  return { custom: L("Eigene", "Custom", "شخصی"), weak: L("Schwachstellen", "Weak spots", "نقاط ضعف"), weakround: L("Schwachstellen", "Weak spots", "نقاط ضعف"), sim: L("Probeprüfung", "Mock exam", "امتحان آزمایشی"), note: L("Hinweis", "Note", "یادداشت") }[it.kind] || L("Sonst", "Other", "سایر");
}

function dayCard(day, today) {
  const { plan } = S.data;
  const isToday = day.d === today, isExam = day.d === plan.exam;
  const sec = h("section", { key: day.d, class: "day" + (isToday ? " today" : day.d < today ? " past" : "") + (isExam || (plan.milestones || []).some(m => m.date === day.d && !m.prep) ? " exam" : "") });
  const mins = day.items.filter(it => !it.moved && it.kind !== "note").reduce((a, it) => a + (it.min || 0), 0);
  const note = [plan.dayNotes && plan.dayNotes[day.d], mins ? "≈ " + hm(mins) : null].filter(Boolean).join(" · ");
  const msDay = (plan.milestones || []).find(m => m.date === day.d);
  const h2 = h("h2", null, fmt(day.d), isToday ? h("span", { class: "badge" }, L("HEUTE", "TODAY", "امروز")) : null, isExam ? h("span", { class: "badge warn" }, L("PRÜFUNG", "EXAM", "امتحان")) : null,
    msDay && !isExam ? h("span", { class: "badge" + (msDay.prep ? "" : " warn") }, msDay.prep ? L("PRÄPSAAL", "LAB", "جلسهٔ عملی") : (msDay.name || L("ETAPPE", "MILESTONE", "مرحله")).toUpperCase()) : null);
  const head = h("div", { class: "dhead" }, h("div", null, h2, h("div", { class: "note" }, note)));
  sec.append(head);
  const groups = new Map();
  for (const it of day.items) { const g = groupLabel(it, plan); if (!groups.has(g)) groups.set(g, []); groups.get(g).push(it); }
  let tot = 0, dn = 0;
  let openMin = 0;
  for (const [g, its] of groups) {
    const box = h("div", { class: "items" });
    for (const it of its) {
      box.append(itemEl(it, day));
      if (!["note", "weakround", "sim"].includes(it.kind) && !it.moved) { tot++; if (itemDone(it)) dn++; else openMin += it.min || 0; }
    }
    sec.append(h("div", { class: "row", key: "g:" + g }, h("div", { class: "label" }, g), box));
  }
  if (tot) {
    sec.dataset.complete = dn === tot ? "1" : "0";
    head.append(h("span", { class: "dprog" + (dn === tot ? " done" : ""), key: "prog" }, ring(dn / tot),
      h("span", null, dn === tot ? L("alles erledigt", "all done", "همه انجام شد") : `${dn}/${tot} ${L("erledigt", "done", "انجام‌شده")}${isToday && openMin ? ` · ≈ ${hm(openMin)} ${L("offen", "left", "مانده")}` : ""}`)));
  }
  if (day.d >= today) {
    // The field belongs to the page, not to this render: read it from the event.
    const add = async e => {
      const inp = e.currentTarget.closest(".add-row").querySelector("input"), text = inp.value.trim();
      if (!text || inp.disabled) return;
      inp.disabled = true;
      try { await run(call("addCustom", { id: plan.id, day: day.d, text })); inp.value = ""; await refresh(); }
      finally { inp.disabled = false; inp.focus(); }
    };
    sec.append(h("div", { class: "add-row", key: "add" },
      h("input", { type: "text", maxlength: 500, onkeydown: e => { if (e.key === "Enter") add(e); }, placeholder: L("Eigener Punkt, z. B. „Altfragen 2023 durchgehen 45 min“", "Custom item, e.g. “Go through the 2023 past questions 45 min”", "مورد دلخواه، مثلاً «مرور سؤال‌های سال 2023 45 min»") }),
      h("button", { onclick: add, title: L("Hinzufügen", "Add", "افزودن") }, "+")));
  }
  return sec;
}

function itemEl(it, day) {
  const { plan, ev } = S.data;
  if (it.kind === "note") return h("div", { class: "plain", key: it.id }, it.text);
  if (it.kind === "weakround") return h("div", { key: it.id }, h("div", { class: "plain" }, it.text), h("div", { class: "bar-actions", style: "margin-top:5px" },
    h("button", { onclick: () => weakDialog() }, L("Schwachstellen ansehen & einplanen", "View & schedule weak spots", "دیدن و برنامه‌ریزی نقاط ضعف")), h("button", { onclick: () => weakBrowse() }, L("Schwache Karten lernen", "Study weak cards", "مطالعهٔ کارت‌های ضعیف"))));
  if (it.kind === "sim") return h("div", { key: it.id }, h("div", { class: "plain" }, it.text), h("div", { class: "bar-actions", style: "margin-top:5px" },
    h("button", { class: "primary", onclick: () => simStart() }, L("Probeprüfung starten", "Start mock exam", "شروع امتحان آزمایشی"))));
  const r = ev[it.id], auto = !!it.auto, done = itemDone(it);
  const cb = h("input", { type: "checkbox", checked: done, disabled: it.moved || null, onchange: async e => {
    const box = e.currentTarget, on = box.checked;
    if (auto && r && r.done && !plan.done[it.id]) { box.checked = true; return toast(L("Das hakt Anki ab.", "Anki checks this off.", "این مورد را Anki خودش تیک می‌زند.")); }
    S.pending.set(it.id, on); S.cheer = on;
    render();  // shows the tick at once; Anki confirms right after
    try { await call("toggle", { id: plan.id, item: it.id, on }); }
    catch (err) { S.pending.delete(it.id); render(); toast(L("Fehler: ", "Error: ", "خطا: ") + err.message, 5000); refresh(); return; }
    S.cheer = on;
    await refresh(() => S.pending.delete(it.id));
  } });
  const t = h("span", { class: "t" }, h("span", { class: "tx" }, it.text));
  if (auto) t.append(h("span", { class: "chip" + (r && r.done ? " ok" : "") }, r && r.text ? "Anki · " + r.text : "Anki"));
  if (it.moved) t.append(h("span", { class: "chip info" }, L("→ neu eingeplant", "→ rescheduled", "← دوباره برنامه‌ریزی شد")));
  if (it.min && !auto && !it.moved) t.append(h("span", { class: "chip info" }, hm(it.min)));
  if (it.for) t.append(h("span", { class: "chip info" }, L("für ", "for ", "برای ") + it.for));
  const act = (label, fn) => t.append(h("a", { class: "small", style: "margin-inline-start:6px;white-space:nowrap", onclick: e => { e.preventDefault(); e.stopPropagation(); fn(); } }, label));
  if ((it.kind === "cards" || it.kind === "reviews") && !it.moved) act(L("▶ lernen", "▶ study", "▶ مطالعه"), async () => {
    const r = await run(call("studyItem", { id: plan.id, item: it.id }));
    if (r && r.ok === false) toast(L("Keine passenden Karten (mehr) gefunden.", "No matching cards (left).", "کارت مناسبی (دیگر) پیدا نشد."));
  });
  const psrc = it.kind === "pages" && plan.sources.find(s => s.id === it.source);
  if (psrc && (psrc.file || psrc.fileName)) act(L("📖 öffnen", "📖 open", "📖 باز کردن"), async () => { const r = await run(call("openPages", { id: plan.id, item: it.id })); if (r && r.cancelled) return; if (r && r.noPage) toast(L(`Kein Okular gefunden – bitte selbst zu Seite ${r.page} blättern.`, `Okular not found – please go to page ${r.page} yourself.`, `Okular پیدا نشد – لطفاً خودتان به صفحهٔ ${r.page} بروید.`)); });
  if (it.url) t.append(h("a", { class: "small", style: "margin-inline-start:6px", title: it.url, onclick: e => { e.preventDefault(); run(call("openLink", { url: it.url, id: plan.id, item: it.id })); } }, L("öffnen ↗", "open ↗", "باز کردن ↖")));
  if (it.custom && !done && day.d >= S.data.stats.today && day.d < plan.exam) act(L("→ morgen", "→ tomorrow", "← فردا"), async () => {
    await run(call("moveItem", { id: plan.id, item: it.id, day: addDays(day.d, 1) })); refresh();
  });
  const row = h("label", { key: it.id, class: "item" + (done ? " checked" : "") + (it.moved ? " moved" : "") }, cb, t);
  if (it.custom || it.kind === "weak") row.append(h("button", { class: "ghost", title: L("Entfernen", "Remove", "حذف"), onclick: async e => {
    e.preventDefault();
    const gone = await run(call("delItem", { id: plan.id, item: it.id }));
    await refresh();
    if (gone) toast(L("Punkt entfernt.", "Item removed.", "مورد حذف شد."), 6000, [L("Rückgängig", "Undo", "واگرد"), async () => { await run(call("restoreItem", { id: plan.id, gone })); refresh(); }]);
  } }, "✕"));
  return row;
}

// ---------- Share ----------
function planText(plan) {
  const lines = [`${plan.title}`, `${L("Prüfung", "Exam", "امتحان")}: ${plan.exam ? fmt(plan.exam) + " " + plan.exam.slice(0, 4) : "–"}${plan.examTime ? COMMA() + plan.examTime + L(" Uhr", "", "") : ""}`, ""];
  for (const day of plan.days) {
    const its = day.items.filter(it => !it.moved && it.text && !["weakround", "sim"].includes(it.kind));
    if (!its.length) continue;
    const mins = its.filter(it => it.kind !== "note").reduce((a, it) => a + (it.min || 0), 0);
    lines.push(`${fmt(day.d)}${mins ? " (≈ " + hm(mins) + ")" : ""}`);
    for (const it of its) lines.push(`  • ${it.text}${it.url ? " – " + it.url : ""}`);
    lines.push("");
  }
  lines.push(L("Erstellt mit Smart Study für Anki", "Made with Smart Study for Anki", "ساخته‌شده با Smart Study برای Anki"));
  return lines.join("\n");
}
async function shareDialog() {
  const { plan } = S.data;
  const copyCode = async () => {
    const r = await run(call("shareCode", { id: plan.id }));
    const msg = L(`Mein Lernplan „${plan.title}“${plan.exam ? " (Prüfung " + dmy(plan.exam) + ")" : ""}\nSo übernimmst du ihn: Anki → Study Plan → Importieren → diese ganze Nachricht einfügen.\n(Braucht das Anki-Add-on „Smart Study“.)\n\n`,
      `My study plan “${plan.title}”${plan.exam ? " (exam " + dmy(plan.exam) + ")" : ""}\nTo use it: Anki → Study Plan → Import → paste this whole message.\n(Needs the Anki add-on “Smart Study”.)\n\n`,
      `برنامهٔ مطالعهٔ من «${plan.title}»${plan.exam ? " (امتحان " + dmy(plan.exam) + ")" : ""}\nبرای استفاده: Anki ← Study Plan ← وارد کردن ← کل این پیام را جای‌گذاری کنید.\n(به افزونهٔ Anki «Smart Study» نیاز دارد.)\n\n`) + r.code;
    await run(call("copyText", { text: msg }));
    toast(L("Kopiert – jetzt z. B. in WhatsApp, Signal oder eine Mail einfügen.", "Copied – now paste it into WhatsApp, Signal or an email, for example.", "کپی شد – حالا مثلاً در واتس‌اپ، سیگنال یا ایمیل جای‌گذاری کنید."), 4000);
  };
  const saveFile = async () => {
    const path = await run(call("exportFile", { id: plan.id }));
    if (path) toast(L("Gespeichert: ", "Saved: ", "ذخیره شد: ") + path + L(" – die Datei kannst du jetzt verschicken.", " – you can send this file now.", " – اکنون می‌توانید این فایل را بفرستید."), 5000);
  };
  const copyText = async () => {
    await run(call("copyText", { text: planText(plan) }));
    toast(L("Übersicht kopiert – zum Lesen, auch ohne Anki.", "Overview copied – for reading, also without Anki.", "خلاصه کپی شد – برای خواندن، حتی بدون Anki."), 4000);
  };
  const opt = (label, hint, fn, cls) => h("div", { style: "display:flex;gap:10px;align-items:center;margin:8px 0" },
    h("button", { class: cls, style: "min-width:170px", onclick: fn }, label), h("span", { class: "muted small" }, hint));
  await modal(L("Plan teilen", "Share plan", "اشتراک‌گذاری برنامه"), h("div", null,
    h("p", { class: "small", style: "margin:0 0 6px" }, L("Deine Freunde bekommen den Plan mit allen Tagen, Themen und Video-Links – aber nicht deinen Fortschritt und keine Dateipfade von deinem Computer.",
      "Your friends get the plan with all days, topics and video links – but not your progress and no file paths from your computer.",
      "دوستانتان برنامه را با همهٔ روزها، موضوع‌ها و لینک‌های ویدیو دریافت می‌کنند – اما نه پیشرفت شما و نه مسیر فایل‌های رایانهٔ شما را.")),
    opt(L("Code kopieren", "Copy code", "کپی کد"), L("Für WhatsApp & Co. – einfügen und senden.", "For WhatsApp & co. – paste and send.", "برای واتس‌اپ و غیره – جای‌گذاری و ارسال."), copyCode, "primary"),
    opt(L("Als Datei speichern", "Save as file", "ذخیره به‌صورت فایل"), L("Zum Mailen oder für einen Cloud-Ordner.", "For email or a cloud folder.", "برای ایمیل یا پوشهٔ ابری."), saveFile),
    opt(L("Als Text kopieren", "Copy as text", "کپی به‌صورت متن"), L("Lesbare Übersicht für alle ohne Smart Study.", "Readable overview for anyone without Smart Study.", "خلاصهٔ خوانا برای کسانی که Smart Study ندارند."), copyText)),
    [[L("Schließen", "Close", "بستن"), null]]);
}
async function importDialog() {
  const box = h("textarea", { placeholder: L("Nachricht mit dem Code (SSP1:…) hier einfügen", "Paste the message with the code (SSP1:…) here", "پیام حاوی کد (SSP1:…) را اینجا جای‌گذاری کنید"), style: "min-height:120px" });
  const how = await modal(L("Plan importieren", "Import plan", "وارد کردن برنامه"), h("div", null,
    h("p", { class: "small", style: "margin:0 0 8px" }, L("Füge die Nachricht ein, die dir jemand mit „Teilen“ geschickt hat – oder wähle die Plan-Datei.", "Paste the message someone sent you with “Share” – or choose the plan file.", "پیامی را که کسی با «اشتراک‌گذاری» برایتان فرستاده جای‌گذاری کنید – یا فایل برنامه را انتخاب کنید.")), box),
    [[L("Abbrechen", "Cancel", "انصراف"), null], [L("Datei wählen…", "Choose file…", "انتخاب فایل…"), "file"], [L("Importieren", "Import", "وارد کردن"), "code", "primary"]]);
  if (!how) return;
  if (how === "code" && !box.value.trim()) return toast(L("Bitte zuerst den Code einfügen.", "Please paste the code first.", "لطفاً ابتدا کد را جای‌گذاری کنید."));
  const r = await run(call(how === "file" ? "importFile" : "importCode", { text: box.value }));
  if (!r) return;
  const hints = [];
  if (r.missingDecks.length) hints.push(L("Diese Decks fehlen bei dir: ", "You don't have these decks: ", "این دسته‌ها را ندارید: ") + r.missingDecks.join(", "));
  if (r.pdfs) hints.push(L("PDF-Datei unter Bearbeiten → Quellen wählen.", "Choose the PDF file under Edit → Sources.", "فایل PDF را از ویرایش ← منابع انتخاب کنید."));
  toast(L(`„${r.title}“ übernommen.`, `“${r.title}” imported.`, `«${r.title}» وارد شد.`) + (hints.length ? " " + hints.join(" ") : ""), hints.length ? 7000 : 3000);
  go("plan", r.id);
}

async function replan() {
  if (S.replanning) return;
  S.replanning = true;
  let r;
  try { r = await run(call("generate", { id: S.pid })); } finally { S.replanning = false; }
  toast(r.notes.length ? L("Neu geplant – mit Hinweis, siehe oben.", "Replanned – with a note, see above.", "دوباره برنامه‌ریزی شد – با یک نکته، بالا را ببینید.") : L("Neu geplant: offener Stoff ist auf die Tage bis zur Prüfung verteilt.", "Replanned: open material is spread over the days until the exam.", "دوباره برنامه‌ریزی شد: مطالب باز روی روزهای باقی‌مانده تا امتحان پخش شدند."));
  go("plan");
}

// ---------- Tools ----------
function toolsPanel(early) {
  return h("div", { class: "panel-tools" },
    h("div", { class: "tool" }, h("b", null, L("Schwachstellen-Runde", "Weak spots round", "دور نقاط ضعف")), h("p", null, L("Findet die Themen mit den meisten Fehlern in Anki und plant Handbuch, Video und schwache Karten dafür neu ein.", "Finds the topics with the most mistakes in Anki and schedules the book pages, video and weak cards for them again.", "موضوع‌هایی را که بیشترین اشتباه را در Anki دارند پیدا می‌کند و صفحه‌های کتاب، ویدیو و کارت‌های ضعیف آن‌ها را دوباره در برنامه می‌گذارد.")),
      h("button", { class: early ? "primary" : null, onclick: () => weakDialog() }, L("Schwachstellen ansehen", "View weak spots", "دیدن نقاط ضعف"))),
    h("div", { class: "tool" }, h("b", null, L("Probeprüfung", "Mock exam", "امتحان آزمایشی")), h("p", null, L("Zufällige Karten aus allen Decks auf Zeit, ohne Kapitel-Hinweis, plus Themen zum freien Erklären.", "Random cards from all decks against the clock, without chapter hints, plus topics to explain freely.", "کارت‌های تصادفی از همهٔ دسته‌ها با زمان محدود و بدون اشاره به فصل، به‌علاوهٔ موضوع‌هایی برای توضیح آزاد.")),
      h("button", { onclick: () => simStart() }, L("Probeprüfung starten", "Start mock exam", "شروع امتحان آزمایشی"))));
}

async function weakDialog() {
  const r = await run(call("weak", { id: S.pid }));
  if (!r.weak.length) return modal(L("Schwachstellen", "Weak spots", "نقاط ضعف"), h("p", null, L("Noch keine Fehler in den Themen-Karten seit Planbeginn – entweder läuft es super, oder die Themen sind noch nicht mit Anki-Unterdecks/Tags verknüpft (Bearbeiten → Themen).", "No mistakes in the topic cards since the plan started – either it's going great, or the topics aren't linked to Anki subdecks/tags yet (Edit → Topics).", "از آغاز برنامه اشتباهی در کارت‌های موضوع‌ها نبوده است – یا همه‌چیز عالی پیش می‌رود، یا موضوع‌ها هنوز به زیردسته‌ها/برچسب‌های Anki وصل نشده‌اند (ویرایش ← موضوع‌ها).")), [[L("OK", "OK", "تأیید"), true, "primary"]]);
  const body = h("div", null, h("table", null, h("tr", null, h("th", null, L("Thema", "Topic", "موضوع")), h("th", null, L("Fehler", "Mistakes", "اشتباه")), h("th", null, L("schwache Karten", "weak cards", "کارت ضعیف"))),
    r.weak.slice(0, 8).map(w => h("tr", null, h("td", null, w.name), h("td", null, String(w.agains)), h("td", null, String(w.cards))))),
    h("h3", null, L("Wird eingeplant", "Will be scheduled", "در برنامه قرار می‌گیرد")), h("ul", { class: "weak-list" }, r.items.map(i => h("li", null, i.text))));
  const v = await modal(L("Schwachstellen seit Planbeginn", "Weak spots since the plan started", "نقاط ضعف از آغاز برنامه"), body, [[L("Schließen", "Close", "بستن"), null], [L("Nur Karten lernen", "Only study cards", "فقط مطالعهٔ کارت‌ها"), "cards"], [L("Einplanen", "Schedule", "برنامه‌ریزی"), "plan", "primary"]]);
  if (v === "plan") { const x = await run(call("addWeak", { id: S.pid })); toast(L(`Eingeplant am ${fmt(x.day)}.`, `Scheduled on ${fmt(x.day)}.`, `برای ${fmt(x.day)} برنامه‌ریزی شد.`)); refresh(); }
  if (v === "cards") weakBrowse();
}

async function weakBrowse() {
  const b = await run(call("weakBrowse", { id: S.pid }));
  if (!b.ok) toast(L("Keine schwachen Karten gefunden.", "No weak cards found.", "کارت ضعیفی پیدا نشد."));
}
async function simStart() {
  const n = h("input", { type: "number", value: 50, min: 5, max: 500 }), m = h("input", { type: "number", value: 30, min: 5, max: 240 });
  const ok = await modal(L("Probeprüfung", "Mock exam", "امتحان آزمایشی"), h("div", null, h("div", { class: "form" }, h("label", null, L("Karten", "Cards", "تعداد کارت")), n, h("label", null, L("Zeit (Minuten)", "Time (minutes)", "زمان (دقیقه)")), m),
    h("p", { class: "muted small" }, L("Zufällige, schon gelernte Karten werden hier gezeigt. Nichts wird in deinen Decks verschoben. Antwort zeigen, dann richtig oder falsch markieren.", "Random, already studied cards are shown here. Nothing is moved in your decks. Show the answer, then mark it right or wrong.", "کارت‌های تصادفی که قبلاً مطالعه کرده‌اید اینجا نمایش داده می‌شوند. چیزی در دسته‌های شما جابه‌جا نمی‌شود. پاسخ را ببینید، سپس آن را درست یا نادرست علامت بزنید."))), [[L("Abbrechen", "Cancel", "انصراف"), null], [L("Starten", "Start", "شروع"), true, "primary"]]);
  if (!ok) return;
  const r = await run(call("mockStart", { id: S.pid, n: +n.value, minutes: +m.value }));
  if (!r.cards.length) return toast(L("Noch keine gelernten Karten in den Plan-Decks.", "No studied cards in the plan decks yet.", "هنوز کارت مطالعه‌شده‌ای در دسته‌های برنامه نیست."));
  S.mock = { pid: S.pid, cards: r.cards, i: 0, shown: false, ok: 0, started: Date.now(), minutes: r.minutes };
  render();
  const el = document.querySelector(".mock"); if (el) el.scrollIntoView({ behavior: motion() ? "smooth" : "auto", block: "start" });
}
async function mockAnswer(cur, right) {
  const m = S.mock;
  if (!m || m.busy || m.cards[m.i] !== cur) return;  // a double click must not skip a card
  m.busy = true;
  try { await run(call("mockAnswer", { id: m.pid, cid: cur.cid, ok: right })); } finally { m.busy = false; }
  if (S.mock !== m) return;
  m.i++; m.shown = false; if (right) m.ok++;
  render();
}
async function mockStop() {
  const m = S.mock;
  if (!m || m.stopping) return;
  m.stopping = true;
  let r;
  try { r = await run(call("mockStop", { id: m.pid })); } catch (e) { m.stopping = false; throw e; }
  clearInterval(S.simTimer); S.mock = null; render();
  modal(L("Probeprüfung – Ergebnis", "Mock exam – result", "امتحان آزمایشی – نتیجه"), simTable(r), [[L("OK", "OK", "تأیید"), true, "primary"]]);
}
function mockPanel() {
  const m = S.mock, cur = m.cards[m.i];
  const card = h("div", { class: "card hl mock", key: "mock" });
  const end = m.started + m.minutes * 60e3, total = m.minutes * 60;
  const timer = h("div", { class: "timer", key: "timer", "data-morph": "keep" });
  const bar = h("div", { class: "pbar", key: "timebar", "data-morph": "keep" }, h("i", { style: "width:100%" }));
  // The clock is kept across renders; it looks its elements up in the page each second.
  const tick = () => {
    const live = document.querySelector(".mock .timer") || timer, liveBar = document.querySelector(".mock .pbar[data-key=timebar] i") || bar.firstChild;
    const s = Math.max(0, Math.round((end - Date.now()) / 1000));
    live.textContent = `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
    live.classList.toggle("low", s <= 60);
    liveBar.style.width = `${100 * s / total}%`;
    if (!s && S.mock === m && !m.timeUp) { m.timeUp = true; toast(L("Zeit abgelaufen – Auswertung.", "Time is up – evaluating.", "زمان تمام شد – ارزیابی."), 4000); mockStop(); }
  };
  tick(); clearInterval(S.simTimer); S.simTimer = setInterval(() => S.mock === m ? tick() : clearInterval(S.simTimer), 1000);
  card.append(h("h2", null, L("Probeprüfung läuft", "Mock exam running", "امتحان آزمایشی در حال انجام است")), timer,
    bar, h("div", { class: "small muted" }, cur ? L(`Karte ${m.i + 1} von ${m.cards.length} · ${m.ok} richtig bisher`, `Card ${m.i + 1} of ${m.cards.length} · ${m.ok} right so far`, `کارت ${m.i + 1} از ${m.cards.length} · تا اینجا ${m.ok} درست`) : L(`Alle ${m.cards.length} Karten durch · ${m.ok} richtig`, `All ${m.cards.length} cards done · ${m.ok} right`, `هر ${m.cards.length} کارت تمام شد · ${m.ok} درست`)));
  if (cur) {
    card.append(h("p", { class: "mock-q", key: "q" + m.i, style: "white-space:pre-wrap" }, cur.q));
    if (m.shown) card.append(h("p", { class: "mock-a", key: "a" + m.i, style: "white-space:pre-wrap" }, cur.a), h("div", { class: "bar-actions", key: "rate" },
      h("button", { class: "primary", onclick: () => mockAnswer(cur, true), title: L("Taste 1 oder →", "Key 1 or →", "کلید 1 یا →") }, L("Richtig", "Right", "درست")), h("button", { onclick: () => mockAnswer(cur, false), title: L("Taste 2 oder ←", "Key 2 or ←", "کلید 2 یا ←") }, L("Falsch", "Wrong", "نادرست"))));
    else card.append(h("div", { class: "bar-actions", key: "show" }, h("button", { class: "primary", onclick: () => { m.shown = true; render(); }, title: L("Leertaste", "Space", "کلید فاصله") }, L("Antwort zeigen", "Show answer", "نمایش پاسخ"))));
  }
  card.append(h("div", { class: "bar-actions", key: "stop", style: "margin-top:10px" }, h("button", { onclick: mockStop }, L("Beenden & auswerten", "Finish & evaluate", "پایان و ارزیابی"))));
  return card;
}

function simTable(r) {
  if (!r || !r.answered) return h("p", { class: "muted" }, L("Keine Antworten gefunden.", "No answers found.", "پاسخی پیدا نشد."));
  return h("div", null, h("p", null, `${r.ok}/${r.answered} ${L("richtig", "correct", "درست")} (${Math.round(100 * r.ok / r.answered)} %)`),
    r.topics.length ? h("table", null, h("tr", null, h("th", null, L("Thema", "Topic", "موضوع")), h("th", null, L("richtig", "correct", "درست"))),
      r.topics.map(t => h("tr", null, h("td", null, t.name), h("td", null, `${t.ok}/${t.n}`)))) : null);
}

// ---------- Confetti ----------
const PARTY = ["#2f7d4f", "#2f5d9e", "#e3a64a", "#b3372b", "#8db4ee", "#6cc18e"];
// Paper snippets with gravity, drag and spin. origin: {x, y} in px for a burst; none = rain from the top.
function confetti(count, origin) {
  if (!motion()) return;
  const c = h("canvas", { class: "confetti" }); document.body.append(c);
  const dpr = Math.min(2, window.devicePixelRatio || 1), W = innerWidth, H = innerHeight;
  c.width = W * dpr; c.height = H * dpr;
  const x = c.getContext("2d"); x.scale(dpr, dpr);
  const ps = Array.from({ length: count }, () => {
    const ang = origin ? -Math.PI / 2 + (Math.random() - .5) * 2.2 : Math.PI / 2 + (Math.random() - .5) * .6, v = origin ? 5 + Math.random() * 7 : 2 + Math.random() * 3;
    return { x: origin ? origin.x : Math.random() * W, y: origin ? origin.y : -20 - Math.random() * H / 2, vx: Math.cos(ang) * v, vy: Math.sin(ang) * v,
      w: 5 + Math.random() * 5, hh: 3 + Math.random() * 5, rot: Math.random() * 6.3, vr: (Math.random() - .5) * .4, c: PARTY[Math.floor(Math.random() * PARTY.length)], ph: Math.random() * 6.3 };
  });
  const t0 = performance.now(), life = origin ? 1500 : 3800;
  let last = t0;
  (function step(now) {
    const dt = Math.min(2.5, (now - last) / 16.7), age = now - t0; last = now;
    x.clearRect(0, 0, W, H);
    x.globalAlpha = Math.max(0, Math.min(1, (life - age) / 500));
    let alive = false;
    for (const p of ps) {
      p.vy += (origin ? .32 : .05) * dt; p.vx *= Math.pow(.985, dt); p.vy *= Math.pow(.992, dt);
      p.x += (p.vx + Math.sin(age / 260 + p.ph) * .6) * dt; p.y += p.vy * dt; p.rot += p.vr * dt;
      if (p.y < H + 20) alive = true;
      x.save(); x.translate(p.x, p.y); x.rotate(p.rot); x.scale(1, Math.cos(age / 130 + p.ph)); x.fillStyle = p.c; x.fillRect(-p.w / 2, -p.hh / 2, p.w, p.hh); x.restore();
    }
    if (alive && age < life) requestAnimationFrame(step); else c.remove();
  })(t0);
  setTimeout(() => c.remove(), life + 2000);  // also if the window was hidden meanwhile
}
function dayParty(el) {
  const r = (el.querySelector(".dprog") || el).getBoundingClientRect();
  confetti(36, { x: r.left + r.width / 2, y: r.top + r.height / 2 });
  animate(el, [{ transform: "scale(1)" }, { transform: "scale(1.012)" }, { transform: "scale(1)" }], { duration: 420 });
}
function celebrate(pid) {
  if (store.get("party." + pid)) return;
  store.set("party." + pid, true);
  confetti(160);
  toast(L("Alles abgehakt – stark! 🎉", "Everything checked off – great job! 🎉", "همه تیک خورد – عالی بود! 🎉"), 3500);
}

// "Today" button: appears when today's card is out of sight.
let todayWatch = null;
function watchToday() {
  if (todayWatch) { todayWatch.disconnect(); todayWatch = null; }
  let fab = document.querySelector(".fab-today");
  const card = S.view === "plan" ? document.querySelector("#app .day.today") : null;
  if (!card) { if (fab) fab.remove(); return; }
  if (!fab) {
    fab = h("button", { class: "fab-today", onclick: () => { const c = document.querySelector("#app .day.today"); if (c) c.scrollIntoView({ behavior: motion() ? "smooth" : "auto", block: "start" }); } });
    document.body.append(fab);
  }
  if (!("IntersectionObserver" in window)) return;
  todayWatch = new IntersectionObserver(es => {
    const e = es[es.length - 1];
    fab.textContent = (e.boundingClientRect.top < 0 ? "↑ " : "↓ ") + L("Heute", "Today", "امروز");
    fab.classList.toggle("show", !e.isIntersecting);
  });
  todayWatch.observe(card);
}

// ---------- Edit ----------
async function loadCands() {
  for (const s of S.edit.sources) if (s.type === "anki" && (s.decks || []).length && !S.cands[s.id]) {
    const r = await call("candidates", { plan: { sources: [s] } });
    S.cands[s.id] = r[s.id] || [];
  }
}
async function suggestNow() {
  S.sugg = await run(call("suggest", { plan: S.edit }));
}
function renderEdit(root) {
  const p = S.edit;
  const saveLabel = p.days.length ? L("Speichern & neu planen", "Save & replan", "ذخیره و برنامه‌ریزی دوباره") : L("Plan erstellen", "Create plan", "ساخت برنامه");
  root.append(h("div", { class: "top" },
    h("div", null, h("a", { class: "small", onclick: () => go(p.days.length && p.exam ? "plan" : "home") }, p.days.length ? L("← Zurück zum Plan", "← Back to the plan", "→ بازگشت به برنامه") : L("← Alle Pläne", "← All plans", "→ همهٔ برنامه‌ها")), h("h1", null, p.title || L("Neuer Plan", "New plan", "برنامهٔ جدید")),
      h("p", { class: "sub" }, L("1. Eckdaten → 2. Quellen → 3. Themen → Plan erstellen", "1. Basics → 2. Sources → 3. Topics → Create plan", "1. اطلاعات پایه ← 2. منابع ← 3. موضوع‌ها ← ساخت برنامه"))),
    h("div", { class: "bar-actions" }, h("button", { onclick: saveEdit }, L("Speichern", "Save", "ذخیره")), h("button", { class: "primary", onclick: () => saveEdit(true) }, saveLabel))));

  // 1. Basics
  const f = h("div", { class: "form" });
  const field = (lab, el) => f.append(h("label", null, lab), el);
  const bind = (key, type = "text", attrs = {}) => h("input", Object.assign({ type, value: p[key] ?? "", onchange: e => { p[key] = type === "number" ? +e.target.value : e.target.value; if (["exam", "start", "minutesPerDay"].includes(key)) render(); } }, attrs));
  field(L("Name", "Name", "نام"), bind("title", "text", { style: "width:100%" }));
  field(L("Zusatzzeile", "Subtitle", "زیرعنوان"), bind("subtitle", "text", { style: "width:100%", placeholder: L("z. B. Fach, weitere Termine", "e.g. subject, other dates", "مثلاً درس، تاریخ‌های دیگر") }));
  field(L("Prüfung", "Exam", "امتحان"), h("div", { class: "inline" }, dateInput(p.exam, v => { p.exam = v; render(); }), timeInput(p.examTime, v => { p.examTime = v; }), h("span", { class: "muted small" }, L("Datum · Uhrzeit", "date · time", "تاریخ · ساعت"))));
  field(L("Start", "Start", "شروع"), dateInput(p.start, v => { p.start = v; render(); }));
  field(L("Lernzeit pro Tag", "Study time per day", "زمان مطالعه در روز"), h("div", { class: "inline" }, bind("minutesPerDay", "number", { min: 0, step: 15 }), h("span", { class: "muted small" }, L("Minuten (einzelne Tage unten anpassen)", "minutes (adjust single days below)", "دقیقه (روزها را جداگانه در پایین تنظیم کنید)"))));
  field(L("Freie Wochentage", "Days off", "روزهای تعطیل"), h("div", { class: "inline" }, WD_MO().map(([l, n]) => h("label", { class: "wd" }, h("input", { type: "checkbox", checked: p.offWeekdays.includes(n),
    onchange: e => { p.offWeekdays = e.target.checked ? [...p.offWeekdays, n] : p.offWeekdays.filter(x => x !== n); render(); } }), l))));
  root.append(h("div", { class: "card" }, h("h2", null, L("1 · Eckdaten", "1 · Basics", "1 · اطلاعات پایه")), h("div", { style: "margin-top:10px" }, f), milestonesEl(p), calendar(p)));

  // 2. Sources
  const srcBox = h("div", { style: "margin-top:10px" }, p.sources.map(s => sourceEl(s)));
  root.append(h("div", { class: "card" }, h("h2", null, L("2 · Quellen", "2 · Sources", "2 · منابع")),
    h("p", { class: "muted small", style: "margin:2px 0 0" }, L("Alles, womit du lernst. Anki-Decks werden automatisch verfolgt; Seiten, Videos und Aufgaben hakst du ab.", "Everything you study with. Anki decks are tracked automatically; you check off pages, videos and tasks yourself.", "هر چیزی که با آن مطالعه می‌کنید. دسته‌های Anki خودکار دنبال می‌شوند؛ صفحه‌ها، ویدیوها و تکلیف‌ها را خودتان تیک می‌زنید.")),
    srcBox, h("div", { class: "tools" },
      h("button", { onclick: () => addSource("pages") }, L("+ Buch / Skript / Folien (Seiten)", "+ Book / script / slides (pages)", "+ کتاب / جزوه / اسلاید (صفحه)")),
      h("button", { onclick: () => addSource("videos") }, L("+ Videos / Vorlesungen", "+ Videos / lectures", "+ ویدیو / کلاس")),
      h("button", { onclick: () => addSource("anki") }, L("+ Anki-Deck", "+ Anki deck", "+ دستهٔ Anki")),
      h("button", { onclick: () => addSource("tasks") }, L("+ Liste (VMC-Module, Altfragen, Übungen …)", "+ List (online modules, past questions, exercises …)", "+ فهرست (دوره‌های آنلاین، سؤال‌های سال‌های قبل، تمرین‌ها …)"))),
    h("p", { class: "muted small" }, L("Quellen, auf die der Plan keinen Zugriff hat (VMC, YouTube, Moodle, Bücher), trägst du als Liste ein – mit Link, wenn du willst. Der Plan verteilt sie trotzdem; abhaken tust du sie selbst.", "Sources the plan can't access (YouTube, Moodle, online courses, books) go in as a list – with a link if you like. The plan still schedules them; you check them off yourself.", "منابعی که برنامه به آن‌ها دسترسی ندارد (YouTube، Moodle، دوره‌های آنلاین، کتاب‌ها) را به‌صورت فهرست وارد کنید – اگر خواستید با لینک. برنامه باز هم آن‌ها را زمان‌بندی می‌کند؛ تیک زدنشان با خودتان است."))));

  // 3. Topics
  root.append(topicsCard(p));
  root.append(h("div", { class: "bar-actions", style: "justify-content:flex-end" },
    p.days.length ? h("button", { class: "danger", onclick: delPlan }, L("Plan löschen", "Delete plan", "حذف برنامه")) : null,
    h("button", { onclick: saveEdit }, L("Speichern", "Save", "ذخیره")), h("button", { class: "primary", onclick: () => saveEdit(true) }, saveLabel)));
}

function milestonesEl(p) {
  p.milestones = p.milestones || [];
  const box = h("div", { style: "margin-top:12px" }, h("h3", null, L("Etappen / Testate vor der Prüfung", "Milestones / tests before the exam", "مرحله‌ها / آزمون‌های پیش از امتحان")),
    h("p", { class: "muted small", style: "margin:0 0 6px" }, L("Zwischentermine (Testate, Teilprüfungen) hier eintragen und bei jedem Thema wählen, wozu es gehört: der Stoff ist dann vor dem Termin fertig – egal in welcher Reihenfolge er im Buch steht. Mit „Präpsaal“ markierte Termine sind weich: bis dahin nur Lesen + Video, die Karten laufen bis zum nächsten Testat weiter.", "Enter intermediate dates (tests, partial exams) here and pick for each topic where it belongs: its material is then finished before that date – no matter where it is in the book. Dates marked “Lab” are soft: only reading + video until then, the cards keep running until the next test.", "تاریخ‌های میانی (آزمون‌ها، امتحان‌های بخشی) را اینجا وارد کنید و برای هر موضوع مشخص کنید به کدام‌یک تعلق دارد: مطالب آن پیش از همان مهلت تمام می‌شود – هر جای کتاب که باشد. تاریخ‌هایی که با «جلسهٔ عملی» مشخص شده‌اند انعطاف‌پذیرند: تا آن موقع فقط خواندن + ویدیو، و کارت‌ها تا آزمون بعدی ادامه دارند.")));
  for (const m of p.milestones.slice().sort((a, b) => (a.date || "").localeCompare(b.date || ""))) {
    box.append(h("div", { class: "inline ms-row", key: m.id, style: "margin-bottom:5px" },
      h("input", { type: "text", value: m.name, placeholder: L("z. B. Testat Becken", "e.g. Pelvis test", "مثلاً آزمون لگن"), style: "flex:1;min-width:180px", onchange: e => { m.name = e.target.value; } }),
      dateInput(m.date, v => { m.date = v; render(); }),
      timeInput(m.time, v => { m.time = v; }),
      h("label", { class: "wd", title: L("Präpsaal-Termin: bis dahin nur lesen + Video, Karten laufen bis zum Testat weiter, kein Wiederholungstag davor", "Lab session: only reading + video until then, cards keep running until the test, no review day before it", "جلسهٔ عملی: تا آن موقع فقط خواندن + ویدیو، کارت‌ها تا آزمون ادامه دارند، بدون روز مرور پیش از آن") },
        h("input", { type: "checkbox", checked: !!m.prep, onchange: e => { m.prep = e.target.checked; render(); } }), L("Präpsaal", "Lab", "جلسهٔ عملی")),
      h("button", { class: "ghost danger", title: L("Etappe löschen", "Delete milestone", "حذف مرحله"), onclick: () => { p.milestones = p.milestones.filter(x => x !== m); for (const t of p.topics) if (t.milestone === m.id) delete t.milestone; render(); } }, "✕")));
  }
  box.append(h("button", { onclick: () => { p.milestones.push({ id: uid("m"), name: "", date: "", time: "" }); render(); } }, L("+ Etappe / Testat", "+ Milestone / test", "+ مرحله / آزمون")));
  return box;
}

function calendar(p) {
  const cal = h("div", { class: "cal" });
  if (!p.start || !p.exam || p.exam < p.start) return cal;
  for (let d = p.start; d <= p.exam; d = addDays(d, 1)) {
    const wd = (dt(d).getDay() + 6) % 7, has = d in p.dayMinutes;
    const val = has ? p.dayMinutes[d] : (p.offWeekdays.includes(wd) ? 0 : p.minutesPerDay);
    const exam = d === p.exam, ms = (p.milestones || []).find(m => m.date === d);
    cal.append(h("div", { key: d, class: "c" + (val ? "" : " off") + (exam || ms ? " exam" : "") },
      h("div", null, h("b", null, fmt(d)), exam ? " · " + L("Prüfung", "Exam", "امتحان") : ms ? " · " + (ms.name || L("Etappe", "Milestone", "مرحله")) : ""),
      exam ? null : h("div", { class: "inline" }, h("input", { type: "number", min: 0, step: 15, value: val, title: L("Minuten an diesem Tag", "Minutes on this day", "دقیقه در این روز"),
        onchange: e => { const v = +e.target.value; const def = p.offWeekdays.includes(wd) ? 0 : p.minutesPerDay; if (v === def) delete p.dayMinutes[d]; else p.dayMinutes[d] = v; render(); } }), h("span", { class: "muted" }, L("min", "min", "دقیقه"))),
      h("input", { type: "text", placeholder: L("Notiz", "Note", "یادداشت"), value: (p.dayNotes || {})[d] || "", onchange: e => { p.dayNotes = p.dayNotes || {}; if (e.target.value) p.dayNotes[d] = e.target.value; else delete p.dayNotes[d]; } })));
  }
  return h("details", { key: "cal", open: store.get("calOpen") === false ? null : true, ontoggle: e => store.set("calOpen", e.target.open) }, h("summary", null, L("Einzelne Tage (Minuten · Notiz wie „Präpsaal 13–17 Uhr“)", "Single days (minutes · note like “Lab 1–5 pm”)", "روزها به‌صورت جداگانه (دقیقه · یادداشت مانند «جلسهٔ عملی 13–17»)")), cal);
}

function addSource(type) {
  const s = { id: uid("s"), type, name: { pages: L("Skript", "Script", "جزوه"), videos: L("Videos", "Videos", "ویدیوها"), anki: "", tasks: L("Liste", "List", "فهرست") }[type], minPerUnit: null };
  if (type === "videos") { s.videos = []; s.defaultMin = 20; }
  if (type === "tasks") s.tasks = [];
  if (type === "anki") { s.decks = []; s.maxNew = null; s.pick = true; }
  S.edit.sources.push(s); render();
}

function sourceEl(s) {
  const p = S.edit;
  const rm = async () => {
    const ok = await modal(L("Quelle entfernen?", "Remove source?", "منبع حذف شود؟"), h("p", { style: "margin:0" }, L(`„${s.name || TYPES()[s.type]}“ und ihre Verknüpfungen in den Themen werden entfernt.`, `“${s.name || TYPES()[s.type]}” and its links in the topics will be removed.`, `«${s.name || TYPES()[s.type]}» و پیوندهای آن در موضوع‌ها حذف می‌شوند.`)),
      [[L("Abbrechen", "Cancel", "انصراف"), null], [L("Entfernen", "Remove", "حذف"), true, "danger"]]);
    if (!ok) return;
    p.sources = p.sources.filter(x => x !== s); for (const t of p.topics) for (const k of ["pages", "videos", "tasks", "anki"]) if (t[k]) delete t[k][s.id]; render();
  };
  const box = h("div", { class: "src", key: s.id }, h("div", { class: "src-head" }, h("span", { class: "type" }, TYPES()[s.type]),
    h("input", { class: "name", type: "text", value: s.name, placeholder: L("Name", "Name", "نام"), onchange: e => { s.name = e.target.value; } }),
    h("button", { class: "ghost danger", onclick: rm }, L("Entfernen", "Remove", "حذف"))));
  const rate = h("span", { class: "inline small" }, h("input", { type: "number", step: "0.5", min: 0, value: s.minPerUnit ?? "", placeholder: String(defaultRate(s.type)),
    onchange: e => { s.minPerUnit = e.target.value ? +e.target.value : null; } }), h("span", { class: "muted" }, UNIT()[s.type]));
  if (s.type === "pages") {
    const file = h("input", { type: "text", value: s.file || "", placeholder: L("PDF-Datei (optional) – dann öffnet der Plan direkt die richtige Seite", "PDF file (optional) – then the plan opens the right page directly", "فایل PDF (اختیاری) – در این صورت برنامه مستقیم صفحهٔ درست را باز می‌کند"), style: "flex:1;min-width:240px", onchange: e => { s.file = e.target.value.trim(); } });
    box.append(h("div", { class: "inline small" }, L("Tempo:", "Pace:", "سرعت:"), rate, h("span", { class: "muted" }, L("· Seitenbereiche trägst du bei den Themen ein.", "· Page ranges go into the topics.", "· بازهٔ صفحه‌ها را در موضوع‌ها وارد می‌کنید."))),
      h("div", { class: "inline small", style: "margin-top:6px" }, file,
        h("button", { onclick: async () => { const f = await run(call("pickFile")); if (f) { s.file = f; render(); } } }, L("Datei wählen …", "Choose file …", "انتخاب فایل …"))),
      h("div", { class: "inline small", style: "margin-top:4px" }, L("PDF-Seite = Buchseite +", "PDF page = book page +", "صفحهٔ PDF = صفحهٔ کتاب +"),
        h("input", { type: "number", value: s.pageOffset || 0, style: "width:60px", onchange: e => { s.pageOffset = +e.target.value || 0; } }),
        h("span", { class: "muted" }, L("(z. B. 4, wenn Buchseite 17 im PDF auf Seite 21 liegt)", "(e.g. 4 if book page 17 is page 21 in the PDF)", "(مثلاً 4، اگر صفحهٔ 17 کتاب در PDF صفحهٔ 21 باشد)"))));
  }
  if (s.type === "anki") {
    const info = h("div", { class: "small muted", style: "margin-top:4px" }, deckInfoText(s));
    const mx = h("input", { type: "number", min: 0, value: s.maxNew ?? "", placeholder: "∞", onchange: e => { s.maxNew = e.target.value ? +e.target.value : null; } });
    const chips = h("div", null, s.decks.map(d => h("span", { class: "pill", title: d }, h("span", { class: "muted" }, d.split("::").slice(0, -1).join(" › ") + (d.includes("::") ? " › " : "")), d.split("::").pop(),
      h("button", { title: L("Deck entfernen", "Remove deck", "حذف دسته"), onclick: () => { s.decks = s.decks.filter(x => x !== d); delete S.cands[s.id]; render(); } }, "×"))));
    box.append(chips, deckPicker(s), h("div", { class: "inline small", style: "margin-top:6px" }, L("Tempo:", "Pace:", "سرعت:"), rate, h("span", { class: "muted" }, L("· max. neue/Tag:", "· max. new/day:", "· حداکثر جدید/روز:")), mx), info);
  }
  if (s.type === "videos" || s.type === "tasks") {
    const key = s.type, list = s[key];
    const ta = h("textarea", { placeholder: key === "videos"
      ? L("Ein Video pro Zeile, Dauer und Link optional:\nBauchsitus 1 – Allgemeines | 25\nNiere Histologie (18 min)\nVMC Endokrinologie 1 | 40 | https://…", "One video per line, duration and link optional:\nAbdomen 1 – Overview | 25\nKidney histology (18 min)\nEndocrinology lecture 1 | 40 | https://…", "هر ویدیو در یک خط، مدت و لینک اختیاری:\nشکم 1 – کلیات | 25\nبافت‌شناسی کلیه (18 min)\nکلاس غدد 1 | 40 | https://…")
      : L("Ein Eintrag pro Zeile, Dauer und Link optional:\nVMC-Modul Niere | 45 | https://…\nAltfragen Embryo 2023 | 60", "One entry per line, duration and link optional:\nKidney module | 45 | https://…\nEmbryology past questions 2023 | 60", "هر مورد در یک خط، مدت و لینک اختیاری:\nدورهٔ کلیه | 45 | https://…\nسؤال‌های جنین‌شناسی 2023 | 60") });
    ta.value = list.map(v => v.name + (v.min ? " | " + v.min : "") + (v.url ? " | " + v.url : "")).join("\n");
    ta._v = ta.value;
    listen(ta, "change", async ev => {
      const parsed = await run(call("parseList", { text: ev.currentTarget.value }));
      const old = new Map(list.map(v => [v.name, v]));
      s[key] = parsed.map(x => Object.assign(old.get(x.name) || { id: uid(key === "videos" ? "v" : "t") }, { name: x.name, min: x.min, url: x.url || null }));
      const ids = new Set(s[key].map(v => v.id));
      for (const t of p.topics) if (t[key] && t[key][s.id]) t[key][s.id] = t[key][s.id].filter(i => ids.has(i));
      S.sugg = {}; render();
    });
    box.append(ta, h("div", { class: "inline small", style: "margin-top:4px" }, L(`${list.length} Einträge · Standarddauer:`, `${list.length} entries · default duration:`, `${list.length} مورد · مدت پیش‌فرض:`),
      h("input", { type: "number", min: 1, value: s.defaultMin ?? (key === "videos" ? 20 : 30), onchange: e => { s.defaultMin = +e.target.value; } }), h("span", { class: "muted" }, L("min (wenn keine Dauer angegeben)", "min (if no duration is given)", "دقیقه (اگر مدتی وارد نشده باشد)"))));
  }
  return box;
}
// Numbers of an Anki source's decks. They are fetched once and kept in S.deckInfo,
// so a redraw shows them again without asking Anki.
function deckInfoText(s) {
  if (!s.decks.length) return "";
  const infos = s.decks.map(d => S.deckInfo[d]);
  if (infos.some(i => i === undefined)) { loadDeckInfo(s); return "…"; }
  let n = 0, tot = 0; const per = [];
  for (const i of infos) { if (!i) continue; n += i.new; tot += i.total; if (i.perDay) per.push(i.perDay); }
  return L(`${n} neue von ${tot} Karten`, `${n} new of ${tot} cards`, `${n} کارت جدید از ${tot} کارت`) + (per.length ? L(` · Anki-Limit ${Math.min(...per)} neue/Tag`, ` · Anki limit ${Math.min(...per)} new/day`, ` · محدودیت Anki: ${Math.min(...per)} جدید/روز`) : "");
}
const infoLoading = new Set();
async function loadDeckInfo(s) {
  if (infoLoading.has(s.id)) return;
  infoLoading.add(s.id);
  const epoch = S.epoch;
  try {
    for (const d of s.decks.slice()) if (S.deckInfo[d] === undefined) { const i = await call("deckInfo", { deck: d }).catch(() => null); if (epoch !== S.epoch) return; S.deckInfo[d] = i || null; }
    const per = s.decks.map(d => S.deckInfo[d]).filter(i => i && i.perDay).map(i => i.perDay);
    if (s.maxNew == null && per.length) { const was = dirty(); s.maxNew = Math.min(...per); if (!was) S.editBase = JSON.stringify(S.edit); }  // Anki's own limit as the default is no edit of yours
  } finally { infoLoading.delete(s.id); }
  if (S.view === "edit" && epoch === S.epoch) render();
}
// Deck picker: without search text suggestions matching the plan name, otherwise search results.
// It loads its list by itself, so a redraw keeps the live one (data-morph=keep) until the decks change.
function deckPicker(s) {
  const wrap = h("div", { style: "margin-top:6px", key: `pick|${S.epoch}|${s.decks.join("\u0001")}`, "data-morph": "keep" });
  const q = h("input", { type: "text", placeholder: s.decks.length ? L("+ weiteres Deck suchen …", "+ search another deck …", "+ جستجوی دستهٔ دیگر …") : L("Deck suchen, z. B. „altfragen pm“ …", "Search a deck, e.g. “past questions” …", "جستجوی دسته، مثلاً «سؤال‌های سال‌های قبل» …"), style: "width:100%" });
  const list = h("div", { class: "deck-list" });
  let timer = null, open = !!s.pick || !s.decks.length;
  let asked = 0;
  const load = async () => {
    const mine = ++asked;
    const r = await call("findDecks", { title: S.edit.title, q: q.value, exclude: s.decks }).catch(() => []);
    if (mine !== asked) return;  // an answer to an older search text
    list.replaceChildren();
    if (!q.value.trim() && r.length) list.append(h("div", { class: "muted small", style: "padding:2px 4px" }, L(`Passend zu „${S.edit.title}“:`, `Matching “${S.edit.title}”:`, `متناسب با «${S.edit.title}»:`)));
    if (!r.length) list.append(h("div", { class: "muted small", style: "padding:2px 4px" }, q.value.trim() ? L("Kein Deck gefunden.", "No deck found.", "دسته‌ای پیدا نشد.") : L("Kein passendes Deck zum Namen – einfach oben suchen.", "No deck matches the name – just search above.", "دسته‌ای با این نام هماهنگ نیست – کافی است بالا جستجو کنید.")));
    for (const d of r) {
      const parts = d.name.split("::"), depth = parts.length - 1;
      list.append(h("div", { class: "deck-row", onclick: () => { s.decks.push(d.name); delete S.cands[s.id]; if (!s.name || s.name === "Anki") s.name = parts[parts.length - 1]; s.pick = false; loadCands().then(render); } },
        h("span", { class: "dname" }, h("span", { class: "muted" }, parts.slice(0, -1).join(" › ") + (depth ? " › " : "")), h("b", null, parts[depth])),
        h("span", { class: "muted small" }, L(`${d.new} neu / ${d.total}`, `${d.new} new / ${d.total}`, `${d.new} جدید / ${d.total}`)), h("span", { class: "add" }, "+")));
    }
  };
  listen(q, "input", () => { clearTimeout(timer); timer = setTimeout(load, 200); });
  listen(q, "focus", () => { if (!list.childElementCount) load(); });
  wrap.append(q, list);
  if (open) load();
  return wrap;
}
function defaultRate(t) { const prof = (S.data && S.data.profile) || {}; return (prof.rates || {})[t] ?? { pages: 6, videos: 20, tasks: 30, anki: 1 }[t]; }

function topicsCard(p) {
  const card = h("div", { class: "card" }, h("h2", null, L("3 · Themen", "3 · Topics", "3 · موضوع‌ها")),
    h("p", { class: "muted small", style: "margin:2px 0 0" }, L("Ein Thema bündelt, was zusammengehört: Handbuchseiten + Unterdeck/Tag + Videos. Der Plan arbeitet die Themen nacheinander ab: erst lesen, dann Video, dann Karten zum selben Thema.", "A topic bundles what belongs together: book pages + subdeck/tag + videos. The plan works through the topics one after another: first read, then the video, then the cards for the same topic.", "هر موضوع چیزهای مرتبط را کنار هم می‌گذارد: صفحه‌های کتاب + زیردسته/برچسب + ویدیوها. برنامه موضوع‌ها را یکی پس از دیگری جلو می‌برد: اول خواندن، بعد ویدیو، بعد کارت‌های همان موضوع.")));
  const ankiSrc = p.sources.filter(s => s.type === "anki" && (s.decks || []).length), pageSrc = p.sources.filter(s => s.type === "pages");
  card.append(h("div", { class: "tools" },
    pageSrc.length ? h("button", { onclick: tocDialog }, L("Inhaltsverzeichnis einfügen", "Paste table of contents", "چسباندن فهرست مطالب")) : null,
    ankiSrc.length ? h("button", { onclick: fromDecks }, L("Themen aus Unterdecks", "Topics from subdecks", "موضوع‌ها از زیردسته‌ها")) : null,
    h("button", { onclick: () => { p.topics.push({ id: uid("k"), name: "", pages: {}, videos: {}, tasks: {}, anki: {} }); render(); } }, L("+ Thema", "+ Topic", "+ موضوع")),
    p.topics.length ? h("button", { class: "primary", onclick: autoAssign }, L("Zuordnung automatisch vorschlagen", "Suggest links automatically", "پیشنهاد خودکار پیوندها")) : null,
    h("span", { class: "inline small", style: "margin-inline-start:auto" }, L("Reihenfolge:", "Order:", "ترتیب:"),
      h("select", { onchange: e => { p.order = e.target.value; render(); } }, h("option", { value: "auto", selected: p.order === "auto" || null }, L("automatisch (nach Testat, dann Seiten)", "automatic (by test, then pages)", "خودکار (بر اساس آزمون، سپس صفحه)")), h("option", { value: "manual", selected: p.order === "manual" || null }, L("wie in der Liste", "as listed", "به ترتیب فهرست"))))));
  const list = p.order === "auto" ? sortedTopics(p) : p.topics;
  list.forEach((t, ix) => card.append(topicEl(t, ix, list.length)));
  // unassigned videos/tasks
  const used = new Set(p.topics.flatMap(t => [...Object.values(t.videos || {}), ...Object.values(t.tasks || {})].flat()));
  const free = p.sources.filter(s => s.videos || s.tasks).flatMap(s => (s.videos || s.tasks).filter(v => !used.has(v.id)).map(v => v.name));
  if (free.length && p.topics.length) card.append(h("p", { class: "muted small" }, L(`${free.length} Einträge sind keinem Thema zugeordnet und kommen ans Ende: `, `${free.length} entries aren't assigned to a topic and go at the end: `, `${free.length} مورد به موضوعی اختصاص ندارد و به انتها می‌رود: `) + `${free.slice(0, 6).join(COMMA())}${free.length > 6 ? " …" : ""}`));
  if (ankiSrc.length) card.append(h("p", { class: "muted small" }, L("Anki-Karten ohne Thema werden als „übrige Karten“ nach den Themen eingeplant.", "Anki cards without a topic are scheduled as “remaining cards” after the topics.", "کارت‌های Anki بدون موضوع، به‌عنوان «کارت‌های باقی‌مانده» بعد از موضوع‌ها در برنامه قرار می‌گیرند.")));
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
  const box = h("div", { class: "topic", key: t.id }, h("div", { class: "topic-head" }, h("span", { class: "muted small" }, String(ix + 1) + "."),
    h("input", { type: "text", value: t.name, placeholder: L("Thema, z. B. Leistenkanal", "Topic, e.g. Inguinal canal", "موضوع، مثلاً کانال اینگوینال"), onchange: e => { t.name = e.target.value; S.sugg = {}; } }),
    manual ? h("button", { class: "ghost", onclick: () => move(-1), title: L("nach oben", "move up", "انتقال به بالا") }, "↑") : null,
    manual ? h("button", { class: "ghost", onclick: () => move(1), title: L("nach unten", "move down", "انتقال به پایین") }, "↓") : null,
    h("button", { class: "ghost danger", onclick: () => { p.topics = p.topics.filter(x => x !== t); render(); }, title: L("Thema löschen", "Delete topic", "حذف موضوع") }, "✕")));
  const tl = h("div", { class: "tl" });
  const sg = (S.sugg[t.id] || {});
  if ((p.milestones || []).length) tl.append(h("span", null, L("Gehört zu", "Belongs to", "مربوط به")), h("select", { onchange: e => { if (e.target.value) t.milestone = e.target.value; else delete t.milestone; render(); } },
    h("option", { value: "" }, L("Prüfung (Ende)", "Exam (end)", "امتحان (پایان)")), p.milestones.slice().sort((a, b) => (a.date || "").localeCompare(b.date || "")).map(m => h("option", { value: m.id, selected: t.milestone === m.id || null }, `${m.prep ? L("Präpsaal ", "Lab ", "جلسهٔ عملی ") : ""}${m.date ? fmt(m.date) + " · " : ""}${m.name || L("Etappe", "Milestone", "مرحله")}`))));
  for (const s of p.sources) {
    if (s.type === "pages") {
      t.pages = t.pages || {};
      const r = t.pages[s.id] || ["", ""];
      const upd = (i, v) => { const cur = t.pages[s.id] || ["", ""]; cur[i] = v ? +v : ""; if (cur[0] && !cur[1]) cur[1] = cur[0]; t.pages[s.id] = cur[0] ? [cur[0], Math.max(cur[0], cur[1] || cur[0])] : null; if (!t.pages[s.id]) delete t.pages[s.id]; };
      tl.append(h("span", null, s.name || L("Seiten", "Pages", "صفحه‌ها")), h("div", { class: "inline" }, L("S.", "pp.", "ص."), h("input", { type: "number", min: 0, value: r[0], onchange: e => { upd(0, e.target.value); render(); } }), "–",
        h("input", { type: "number", min: 0, value: r[1], onchange: e => { upd(1, e.target.value); render(); } })));
    } else if (s.type === "anki") {
      t.anki = t.anki || {};
      const cands = S.cands[s.id] || [], cur = t.anki[s.id] || "";
      const best = (sg[s.id] || []).map(x => x.query);
      const opts = [h("option", { value: "" }, L("— keine Verknüpfung —", "— not linked —", "— بدون پیوند —"))];
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
        h("option", { value: "" }, L("+ hinzufügen …", "+ add …", "+ افزودن …")),
        items.filter(v => !cur.includes(v.id)).sort((a, b) => (bestIds.includes(b.id) - bestIds.includes(a.id)))
          .map(v => h("option", { value: v.id }, (bestIds.includes(v.id) ? "★ " : "") + v.name + (usedElse.has(v.id) ? L(" (schon zugeordnet)", " (already assigned)", " (قبلاً اختصاص داده شده)") : ""))));
      tl.append(h("span", null, s.name || TYPES()[key]), h("div", null, cur.map(id => { const v = items.find(v => v.id === id); return v ? h("span", { class: "pill" }, v.name, h("button", { onclick: () => { t[key][s.id] = cur.filter(x => x !== id); render(); } }, "×")) : null; }), items.length ? sel : h("span", { class: "muted small" }, L("Liste oben ausfüllen", "Fill in the list above", "فهرست بالا را پر کنید"))));
    }
  }
  box.append(tl);
  return box;
}

async function autoAssign() {
  await suggestNow();
  const r = await run(call("suggest", { plan: S.edit, apply: true }));
  S.edit = r.plan; S.epoch++;
  toast(r.changed ? L(`${r.changed} Zuordnungen übernommen – bitte kurz prüfen (★ = Vorschlag).`, `${r.changed} links applied – please check them quickly (★ = suggestion).`, `${r.changed} پیوند اعمال شد – لطفاً سریع بررسی کنید (★ = پیشنهاد).`) : L("Keine neuen Treffer gefunden. Namen von Themen, Unterdecks und Videos ähneln sich zu wenig.", "No new matches found. The names of topics, subdecks and videos are too different.", "مورد جدیدی پیدا نشد. نام موضوع‌ها، زیردسته‌ها و ویدیوها زیادی با هم فرق دارند."), 4000);
  render();
}

async function tocDialog() {
  const p = S.edit, pageSrc = p.sources.filter(s => s.type === "pages");
  const ta = h("textarea", { style: "min-height:180px", placeholder: L("Aus dem Inhaltsverzeichnis kopieren, z. B.\nPeritoneum ............ 78\nLeistenkanal 82–84\n85 Dünndarm", "Copy from the table of contents, e.g.\nPeritoneum ............ 78\nInguinal canal 82–84\n85 Small intestine", "از فهرست مطالب کپی کنید، مثلاً\nصفاق ............ 78\nکانال اینگوینال 82–84\n85 روده باریک") });
  const sel = h("select", null, pageSrc.map(s => h("option", { value: s.id }, s.name)));
  const msSel = h("select", null, h("option", { value: "" }, L("Prüfung (Ende)", "Exam (end)", "امتحان (پایان)")), (p.milestones || []).map(m => h("option", { value: m.id }, m.name || L("Etappe", "Milestone", "مرحله"))));
  const ok = await modal(L("Inhaltsverzeichnis einfügen", "Paste table of contents", "چسباندن فهرست مطالب"), h("div", null, pageSrc.length > 1 ? h("div", { class: "inline", style: "margin-bottom:6px" }, L("Für:", "For:", "برای:"), sel) : null,
    (p.milestones || []).length ? h("div", { class: "inline", style: "margin-bottom:6px" }, L("Diese Kapitel gehören zu:", "These chapters belong to:", "این فصل‌ها مربوط‌اند به:"), msSel) : null, ta,
    h("p", { class: "muted small" }, L("Eine Zeile pro Kapitel mit Seitenzahl. Endet ein Kapitel nicht mit einer Angabe, geht es bis eine Seite vor dem nächsten. Vorhandene Themen mit gleichem Namen bekommen die Seiten.", "One line per chapter with its page number. If a chapter has no end page, it runs until one page before the next. Existing topics with the same name get the pages.", "برای هر فصل یک خط با شمارهٔ صفحه. اگر فصلی صفحهٔ پایان نداشته باشد، تا یک صفحه پیش از فصل بعدی ادامه دارد. موضوع‌های موجود با همان نام این صفحه‌ها را می‌گیرند."))),
    [[L("Abbrechen", "Cancel", "انصراف"), null], [L("Übernehmen", "Apply", "اعمال"), true, "primary"]]);
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
  toast(L(`${rows.length} Kapitel erkannt, ${added} neue Themen.`, `${rows.length} chapters found, ${added} new topics.`, `${rows.length} فصل پیدا شد، ${added} موضوع جدید.`));
  render();
}

async function fromDecks() {
  const p = S.edit, srcs = p.sources.filter(s => s.type === "anki" && (s.decks || []).length);
  const sel = h("select", null, srcs.flatMap(s => s.decks.map((d, i) => h("option", { value: s.id + "|" + i }, (s.name || "Anki") + " – " + d.split("::").pop()))));
  const ok = await modal(L("Themen aus Unterdecks", "Topics from subdecks", "موضوع‌ها از زیردسته‌ها"), h("div", null, h("div", { class: "inline" }, L("Deck:", "Deck:", "دسته:"), sel),
    h("p", { class: "muted small" }, L("Für jedes direkte Unterdeck entsteht ein Thema, das schon mit dem Unterdeck verknüpft ist. Danach „Zuordnung automatisch vorschlagen“ für Videos.", "Every direct subdeck becomes a topic that is already linked to it. Afterwards use “Suggest links automatically” for videos.", "هر زیردستهٔ مستقیم به موضوعی تبدیل می‌شود که از پیش به آن وصل است. سپس برای ویدیوها از «پیشنهاد خودکار پیوندها» استفاده کنید."))),
    [[L("Abbrechen", "Cancel", "انصراف"), null], [L("Erstellen", "Create", "ساختن"), true, "primary"]]);
  if (!ok) return;
  const [sid, di] = (sel.value || srcs[0].id + "|0").split("|");
  const s = srcs.find(s => s.id === sid), deck = s.decks[+di];
  const info = await run(call("deckInfo", { deck }));
  let added = 0;
  for (const child of info.children) {
    const q = `deck:"${(deck + "::" + child).replace(/"/g, '\\"')}"`;
    if (p.topics.some(t => (t.anki || {})[s.id] === q)) continue;
    let t = p.topics.find(t => t.name.trim().toLowerCase() === child.toLowerCase());
    if (!t) { t = { id: uid("k"), name: child, pages: {}, videos: {}, tasks: {}, anki: {} }; p.topics.push(t); added++; }
    t.anki = t.anki || {}; t.anki[s.id] = q;
  }
  toast(info.children.length ? L(`${added} Themen aus ${info.children.length} Unterdecks.`, `${added} topics from ${info.children.length} subdecks.`, `${added} موضوع از ${info.children.length} زیردسته.`) : L("Dieses Deck hat keine Unterdecks. Tags kannst du pro Thema auswählen.", "This deck has no subdecks. You can pick tags per topic.", "این دسته زیردسته ندارد. می‌توانید برای هر موضوع برچسب انتخاب کنید."));
  render();
}

function validate(p) {
  if (!p.title.trim()) return L("Bitte einen Namen eingeben.", "Please enter a name.", "لطفاً یک نام وارد کنید.");
  if (!p.exam) return L("Bitte das Prüfungsdatum eintragen.", "Please enter the exam date.", "لطفاً تاریخ امتحان را وارد کنید.");
  if (!p.start || p.exam <= p.start) return L("Die Prüfung muss nach dem Start liegen.", "The exam has to be after the start.", "امتحان باید بعد از تاریخ شروع باشد.");
  if (!p.sources.length) return L("Füge mindestens eine Quelle hinzu (z. B. ein Anki-Deck oder das Handbuch).", "Add at least one source (e.g. an Anki deck or your book).", "دست‌کم یک منبع اضافه کنید (مثلاً یک دستهٔ Anki یا کتابتان).");
  if ((p.milestones || []).some(m => !m.date || m.date <= p.start || m.date >= p.exam)) return L("Jede Etappe braucht ein Datum zwischen Start und Prüfung.", "Every milestone needs a date between the start and the exam.", "هر مرحله باید تاریخی بین شروع و امتحان داشته باشد.");
  const bad = p.sources.find(s => s.type === "anki" && !(s.decks || []).length);
  if (bad) return L("Bei einer Anki-Quelle fehlt noch das Deck.", "An Anki source is still missing its deck.", "یکی از منابع Anki هنوز دسته ندارد.");
  return null;
}
async function saveEdit(plan) {
  const p = S.edit;
  for (const t of p.topics) if (!t.name.trim()) t.name = L("Thema", "Topic", "موضوع");
  if (plan === true) { const err = validate(p); if (err) return toast(err, 4000); }
  if (S.saving) return;
  S.saving = true;
  try { await run(call("savePlan", { plan: p })); } finally { S.saving = false; }
  S.editBase = JSON.stringify(p);
  if (plan === true) { await replan(); } else toast(L("Gespeichert.", "Saved.", "ذخیره شد."));
}
async function delPlan() {
  const v = await modal(L("Plan löschen?", "Delete plan?", "برنامه حذف شود؟"), h("p", null, L(`„${S.edit.title}“ wird endgültig gelöscht. Anki-Karten bleiben unberührt. Lieber archivieren? Das geht im Rückblick.`, `“${S.edit.title}” will be deleted for good. Your Anki cards stay untouched. Rather archive it? You can do that in the retrospective.`, `«${S.edit.title}» برای همیشه حذف می‌شود. کارت‌های Anki شما دست‌نخورده می‌مانند. ترجیح می‌دهید بایگانی‌اش کنید؟ این کار در جمع‌بندی ممکن است.`)), [[L("Abbrechen", "Cancel", "انصراف"), null], [L("Löschen", "Delete", "حذف"), true, "danger"]]);
  if (!v) return;
  await run(call("delete", { id: S.edit.id })); S.editBase = JSON.stringify(S.edit); go("home");
}

// ---------- Retrospective ----------
function renderReview(root) {
  const { stats: st, time, profile, review, maintenance, simHistory } = S.data;
  root.append(h("div", { class: "top" }, h("div", null, h("a", { class: "small", onclick: () => go("plan") }, L("← Zurück zum Plan", "← Back to the plan", "→ بازگشت به برنامه")), h("h1", null, L("Rückblick", "Retrospective", "جمع‌بندی")),
    h("p", { class: "sub" }, L("Was hat geklappt – und was lernt der nächste Plan daraus?", "What worked – and what does the next plan learn from it?", "چه چیزی خوب پیش رفت – و برنامهٔ بعدی از آن چه یاد می‌گیرد؟")))));
  const onTime = st.done ? st.onTime / st.done : 0;
  root.append(h("div", { class: "tiles" },
    tile(L("Geschafft", "Done", "انجام‌شده"), String(st.done), st.planned ? st.done / st.planned : 0, "/ " + st.planned),
    tile(L("Pünktlich", "On time", "سر وقت"), Math.round(100 * onTime) + " %", onTime, ""),
    tile(L("Tage mit Verzug", "Days behind", "روزهای با تأخیر"), String(st.lateDays)),
    tile(L("Verschoben", "Moved", "جابه‌جاشده"), String(st.moved), null, L("Punkte", "items", "مورد")),
    time ? tile(L("Zeit in Anki", "Time in Anki", "زمان در Anki"), hm(time.minutes), null, "") : null));

  root.append(h("div", { class: "card" }, h("h2", null, L("Pro Quelle", "Per source", "به تفکیک منبع")), h("table", { style: "margin-top:8px" },
    h("tr", null, h("th", null, L("Quelle", "Source", "منبع")), h("th", null, L("geschafft", "done", "انجام‌شده")), h("th", null, L("davon verspätet", "of which late", "با تأخیر")), h("th", null, L("geplante Zeit", "planned time", "زمان برنامه‌ریزی‌شده"))),
    Object.entries(st.perSource).map(([n, s]) => h("tr", null, h("td", null, n), h("td", null, `${s.done}/${s.planned}`), h("td", null, String(s.late)), h("td", null, hm(s.min)))))));

  // Pace
  const rates = Object.assign({}, profile.rates);
  const measured = time && time.minPerNew;
  const inputs = {};
  const rateRow = (k, label, hint) => { inputs[k] = h("input", { type: "number", step: "0.1", min: 0, value: k === "anki" && measured ? measured : rates[k] }); return [h("label", null, label), h("div", { class: "inline" }, inputs[k], h("span", { class: "muted small" }, hint))]; };
  const suggestMin = onTime < .8 && st.done ? Math.round((profile.minutesPerDay || 180) * Math.max(.6, onTime) / 15) * 15 : null;
  const mpd = h("input", { type: "number", step: 15, min: 0, value: suggestMin || profile.minutesPerDay || 180 });
  const grade = h("input", { type: "text", value: review.grade || "", placeholder: L("z. B. bestanden / 2", "e.g. passed / B", "مثلاً قبول / 18") });
  const feel = h("select", null, ["", L("😣 schlecht", "😣 bad", "😣 بد"), L("😕 eher schlecht", "😕 rather bad", "😕 نسبتاً بد"), L("😐 ok", "😐 ok", "😐 معمولی"), L("🙂 gut", "🙂 good", "🙂 خوب"), L("😄 sehr gut", "😄 very good", "😄 خیلی خوب")].map((l, i) => h("option", { value: i || "", selected: String(review.feeling || "") === String(i || "") || null }, l || "—")));
  const note = h("textarea", { placeholder: L("Was würdest du nächstes Mal anders machen?", "What would you do differently next time?", "دفعهٔ بعد چه کاری را متفاوت انجام می‌دهید؟") }); note.value = review.note || "";
  root.append(h("div", { class: "card" }, h("h2", null, L("Dein echtes Tempo", "Your real pace", "سرعت واقعی شما")),
    h("p", { class: "muted small" }, L("Diese Werte nimmt der nächste Plan als Standard. Anki misst die Zeit selbst; für Seiten und Videos schätzt du kurz.", "The next plan uses these values as defaults. Anki measures its time itself; for pages and videos you make a quick estimate.", "برنامهٔ بعدی از این مقادیر به‌عنوان پیش‌فرض استفاده می‌کند. Anki زمان خودش را اندازه می‌گیرد؛ برای صفحه‌ها و ویدیوها یک تخمین سریع بزنید.")),
    h("div", { class: "form", style: "margin-top:8px" },
      rateRow("pages", L("Minuten pro Seite", "Minutes per page", "دقیقه برای هر صفحه"), L("Handbuch/Skript", "book/script", "کتاب/جزوه")),
      rateRow("videos", L("Minuten pro Video", "Minutes per video", "دقیقه برای هر ویدیو"), L("falls keine Dauer angegeben", "if no duration is given", "اگر مدتی وارد نشده باشد")),
      rateRow("anki", L("Minuten pro neue Karte", "Minutes per new card", "دقیقه برای هر کارت جدید"), measured ? L(`gemessen: ${measured} (inkl. Wiederholungen)`, `measured: ${measured} (incl. reviews)`, `اندازه‌گیری‌شده: ${measured} (با احتساب مرورها)`) : L("inkl. späterer Wiederholungen", "incl. later reviews", "با احتساب مرورهای بعدی")),
      h("label", null, L("Lernzeit pro Tag", "Study time per day", "زمان مطالعه در روز")), h("div", { class: "inline" }, mpd, h("span", { class: "muted small" }, suggestMin ? L(`Vorschlag, weil nur ${Math.round(100 * onTime)} % pünktlich waren`, `suggested because only ${Math.round(100 * onTime)} % were on time`, `پیشنهاد، چون فقط ${Math.round(100 * onTime)} % سر وقت بودند`) : L("Minuten", "minutes", "دقیقه"))),
      h("label", null, L("Ergebnis", "Result", "نتیجه")), grade, h("label", null, L("Gefühl", "Feeling", "حس شما")), feel),
    h("div", { style: "margin-top:8px" }, note),
    h("div", { class: "bar-actions", style: "margin-top:8px" }, h("button", { class: "primary", onclick: async () => {
      await run(call("saveReview", { id: S.pid, review: { grade: grade.value, feeling: +feel.value || null, note: note.value }, rates: Object.fromEntries(Object.entries(inputs).map(([k, i]) => [k, +i.value])), minutesPerDay: +mpd.value }));
      toast(L("Gespeichert – der nächste Plan nutzt dieses Tempo.", "Saved – the next plan uses this pace.", "ذخیره شد – برنامهٔ بعدی از این سرعت استفاده می‌کند."));
    } }, L("Speichern", "Save", "ذخیره")))));

  if (simHistory.length) root.append(h("div", { class: "card" }, h("h2", null, L("Probeprüfungen", "Mock exams", "امتحان‌های آزمایشی")), simHistory.map(s => h("div", null, h("h3", null, fmt(s.at)), simTable(s.result)))));

  // Afterwards
  const rpd = h("input", { type: "number", min: 5, step: 5, value: maintenance.reviewsPerDay || 50 });
  root.append(h("div", { class: "card" }, h("h2", null, L("Und jetzt?", "What now?", "حالا چه کنیم؟")), h("div", { class: "panel-tools" },
    h("div", { class: "tool" }, h("b", null, L("Erhaltungsmodus", "Maintenance mode", "حالت نگهداری")), h("p", null, L("Die Decks laufen weiter, aber ohne neue Karten und mit gedeckelten Wiederholungen – damit bis zur großen Prüfung nichts verloren geht. Ausschalten stellt die alten Deck-Optionen wieder her.", "The decks keep running, but without new cards and with capped reviews – so nothing gets lost until the big exam. Switching it off restores the old deck options.", "دسته‌ها ادامه دارند، اما بدون کارت جدید و با سقف مرور – تا چیزی تا امتحان اصلی از یاد نرود. با خاموش کردن، تنظیمات قبلی دسته‌ها برمی‌گردند.")),
      maintenance.on ? h("button", { onclick: async () => { await run(call("maintenance", { id: S.pid, on: false })); toast(L("Erhaltungsmodus aus, alte Optionen zurück.", "Maintenance mode off, old options restored.", "حالت نگهداری خاموش شد، تنظیمات قبلی برگشتند.")); go("review"); } }, L("Erhaltungsmodus ausschalten", "Turn off maintenance mode", "خاموش کردن حالت نگهداری"))
        : h("div", { class: "inline" }, rpd, h("span", { class: "muted small" }, L("Wdh./Tag", "reviews/day", "مرور/روز")), h("button", { class: "primary", onclick: async () => { await run(call("maintenance", { id: S.pid, on: true, reviewsPerDay: +rpd.value })); toast(L("Erhaltungsmodus an.", "Maintenance mode on.", "حالت نگهداری روشن شد.")); go("review"); } }, L("Einschalten", "Turn on", "روشن کردن")))),
    h("div", { class: "tool" }, h("b", null, L("Archivieren", "Archive", "بایگانی")), h("p", null, L("Der Plan wandert ins Archiv und bleibt abrufbar, z. B. für die Gesamtprüfung.", "The plan moves to the archive and stays available, e.g. for the final exam.", "برنامه به بایگانی می‌رود و در دسترس می‌ماند، مثلاً برای امتحان نهایی.")),
      h("button", { onclick: async () => { await run(call("archive", { id: S.pid, on: true })); toast(L("Archiviert.", "Archived.", "بایگانی شد.")); go("home"); } }, L("Archivieren", "Archive", "بایگانی"))),
    h("div", { class: "tool" }, h("b", null, L("Nächster Plan", "Next plan", "برنامهٔ بعدی")), h("p", null, L("Übernimmt deine Quellen-Arten und dein Tempo. Du gibst nur Fach, Stoff und Prüfungsdatum ein.", "Takes over your source types and your pace. You only enter the subject, material and exam date.", "نوع منابع و سرعت شما را منتقل می‌کند. فقط درس، مطالب و تاریخ امتحان را وارد می‌کنید.")),
      h("button", { class: "primary", onclick: async () => { S.data.today = (await call("home")).today; newPlan(S.pid); } }, L("Nächsten Plan anlegen", "Create next plan", "ساخت برنامهٔ بعدی"))))));
}

// ---------- Keys ----------
function onKey(e) {
  if (e.defaultPrevented || e.ctrlKey || e.metaKey || e.altKey) return;
  const typing = e.target && /^(INPUT|TEXTAREA|SELECT)$/.test(e.target.nodeName);
  if (e.key === "Escape") {
    e.preventDefault();  // Esc must not close the whole window
    if (typing) e.target.blur();
    return;
  }
  if (typing || document.querySelector(".modal-bg")) return;
  const m = S.view === "plan" && S.mock;
  if (m && m.cards[m.i]) {
    const cur = m.cards[m.i];
    if (!m.shown && (e.key === " " || e.key === "Enter")) { e.preventDefault(); m.shown = true; return render(); }
    if (m.shown && (e.key === "1" || e.key === "ArrowRight")) { e.preventDefault(); return mockAnswer(cur, true); }
    if (m.shown && (e.key === "2" || e.key === "ArrowLeft")) { e.preventDefault(); return mockAnswer(cur, false); }
  }
  if (S.view === "plan" && (e.key === "t" || e.key === "h")) { const c = document.querySelector("#app .day.today"); if (c) { e.preventDefault(); c.scrollIntoView({ behavior: motion() ? "smooth" : "auto", block: "start" }); } }
}

// ---------- Start ----------
function start() {
  const lang = app().dataset.lang || "";
  LANG = lang.startsWith("de") ? "de" : lang.startsWith("fa") ? "fa" : "en";
  document.documentElement.lang = LANG;
  if (LANG === "fa") document.documentElement.dir = "rtl";
  document.addEventListener("keydown", onKey);
  window.addEventListener("unhandledrejection", e => e.preventDefault());  // run() already told the user
  go("home").catch(() => app().replaceChildren(h("div", { class: "card warn" }, L("Der Lernplan konnte nicht geladen werden. Fenster schließen und erneut öffnen.", "The study plan could not be loaded. Close the window and open it again.", "برنامهٔ مطالعه بارگیری نشد. پنجره را ببندید و دوباره باز کنید."))));
  // Once a minute (a new day may have begun); the page keeps what you are typing.
  setInterval(() => { if (!document.hidden && (S.view === "plan" || S.view === "home") && !document.querySelector(".modal-bg") && !S.pending.size) refresh().catch(() => {}); }, 60000);
  document.addEventListener("visibilitychange", () => { if (!document.hidden && (S.view === "plan" || S.view === "home")) refresh().catch(() => {}); });
}
if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start); else start();
})();
