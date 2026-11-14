/* Smart Study side panel, "Today" page. Python sends the data, this draws it. */
(function () {
  "use strict";
  var data = null, menu = null, pending = {};

  function send(cmd, args) { pycmd("sspanel:" + JSON.stringify({ cmd: cmd, args: args || {} })); }

  function h(tag, attrs) {
    var el = tag === "svg" || tag === "path" || tag === "circle" || tag === "polyline" || tag === "polygon"
      ? document.createElementNS("http://www.w3.org/2000/svg", tag) : document.createElement(tag);
    for (var k in attrs || {}) {
      var v = attrs[k];
      if (v == null || v === false) continue;
      if (k.slice(0, 2) === "on") el.addEventListener(k.slice(2), v);
      else if (k === "text") el.textContent = v;
      else el.setAttribute(k, v === true ? "" : v);
    }
    for (var i = 2; i < arguments.length; i++) {
      var c = arguments[i];
      if (c == null || c === false) continue;
      el.append(c.nodeType ? c : document.createTextNode(String(c)));
    }
    return el;
  }
  function svg(d, size, width) {
    var s = h("svg", { "aria-hidden": "true", width: size, height: size, viewBox: "0 0 24 24", fill: "none",
      stroke: "currentColor", "stroke-width": width || 2, "stroke-linecap": "round", "stroke-linejoin": "round" });
    s.append(h("path", { d: d }));
    return s;
  }
  function mins(m) {
    if (!m) return "";
    if (m < 60) return m + " min";
    var r = m % 60;
    return Math.floor(m / 60) + " h" + (r ? " " + (r < 10 ? "0" : "") + r : "");
  }
  function num(n) { return Number(n || 0).toLocaleString(); }

  // --- parts ----------------------------------------------------------------
  function head(t) {
    var show = data.show, cd = show.countdown && data.countdown, lv = show.level && data.level != null;
    if (!cd && !lv) return null;
    var row = h("div", { class: "ph" + (show.plan ? " line" : "") });
    if (cd) {
      var d = data.countdown.days;
      row.append(h("button", { type: "button", class: "cd", title: t.openPlan,
        onclick: function () { send("countdown", { source: data.countdown.source }); } },
        h("span", { class: "num" }, d <= 0 ? "0" : d),
        h("span", { class: "what" }, h("span", { class: "m", style: "display:block" }, d <= 0 ? t.examToday : (d === 1 ? t.dayUntil : t.daysUntil)),
          h("span", { class: "title" }, data.countdown.title))));
    }
    if (lv) {
      row.append(h("button", { type: "button", class: "lv", title: (data.rank || "") + (data.xp != null ? " · " + data.xp + "% " + t.xp : ""),
        onclick: function () { send("trophies"); } },
        h("b", null, t.level + " " + data.level), h("span", { class: "m", style: "display:block" }, data.streak + " " + t.streak)));
    }
    return row;
  }

  function planItem(it, t) {
    var done = it.id in pending ? pending[it.id] : it.done;
    var canStudy = (it.kind === "cards" || it.kind === "reviews") && !done;
    var tick = h("button", { type: "button", class: "cb", "aria-pressed": done ? "true" : "false", "aria-label": it.text,
      onclick: function () {
        if (it.byAnki) { toast(t.ankiChecks); return; }
        pending[it.id] = !done;
        draw();
        send("toggle", { plan: it.plan, item: it.id, on: !done });
      } }, h("span", { class: "bx" }, svgTick()));
    var sub = [it.planTitle, it.auto ? (it.note ? "Anki · " + it.note : "Anki") : ""].filter(Boolean).join(" · ");
    return h("div", { class: "ti" + (done ? " done" : "") }, tick,
      h("span", { class: "tx", title: it.text }, it.text, sub ? h("small", null, sub) : null),
      canStudy ? h("button", { type: "button", class: "go", onclick: function () { send("study", { plan: it.plan, item: it.id }); } }, t.study)
        : (it.min && !it.auto ? h("span", { class: "m" }, mins(it.min)) : null));
  }
  function svgTick() {
    var s = h("svg", { "aria-hidden": "true", width: 12, height: 12, viewBox: "0 0 14 14", fill: "none", stroke: "currentColor",
      "stroke-width": 2.4, "stroke-linecap": "round", "stroke-linejoin": "round" });
    s.append(h("path", { d: "M2.5 7.5l3 3 6-7" }));
    return s;
  }

  function plan(t) {
    if (!data.show.plan) return null;
    var p = data.plan, box = h("div", { class: "plan" });
    var summary = "";
    if (p.total) summary = p.done + " " + t.of + " " + p.total + " " + t.done + (p.mins ? ", " + t.about + " " + mins(p.mins) + " " + t.left : "");
    box.append(h("div", { class: "plan-head" }, h("b", null, t.today), h("span", { class: "m" }, summary)));
    if (!p.hasPlans) {
      box.append(h("div", { class: "empty" }, t.noPlanHint));
      box.append(h("button", { type: "button", class: "link", onclick: function () { send("openPlan"); } }, t.openPlan));
      return box;
    }
    if (!p.total) box.append(h("div", { class: "empty" }, t.nothing));
    p.items.forEach(function (it) { box.append(planItem(it, t)); });
    box.append(h("button", { type: "button", class: "link", onclick: function () { send("openPlan"); } },
      p.more > 0 ? p.more + " " + t.more : t.openPlan));
    return box;
  }

  function extras(t) {
    var rows = [];
    var c = data.show.challenge && data.challenge;
    if (c) {
      var reached = c.cur >= c.target;
      rows.push(h("div", { class: "row" },
        h("div", { class: "row-head" }, h("b", null, t.challenge),
          reached ? h("button", { type: "button", class: "pill", style: "margin-inline-start:auto", disabled: c.claimed,
            onclick: function () { send("claim"); } }, c.claimed ? t.claimed : t.claim + " +" + c.xp + " " + t.xp)
            : h("span", { class: "m" }, num(c.cur) + " / " + num(c.target))),
        h("div", { class: "ch-text" }, c.text),
        h("div", { class: "track", role: "progressbar", "aria-valuemin": 0, "aria-valuemax": c.target, "aria-valuenow": c.cur },
          h("i", { style: "width:" + Math.min(100, Math.round(100 * c.cur / Math.max(1, c.target))) + "%" }))));
    }
    if (data.show.fact && data.fact) {
      rows.push(h("div", { class: "row" }, h("div", { class: "row-head" }, h("b", null, t.fact)), h("p", { class: "fact" }, data.fact)));
    }
    return rows;
  }

  function period(which, value, choices, label) {
    var sel = h("select", { class: "chip", "aria-label": label,
      onchange: function (e) { send("period", { which: which, days: Number(e.currentTarget.value) }); } });
    choices.forEach(function (n) {
      var text = n === 365 ? data.t.lastYear : (which === "due" ? data.t.next : data.t.last).replace("{}", n);
      sel.append(h("option", { value: n, selected: n === value }, text));
    });
    return sel;
  }

  function due(t) {
    var d = data.due;
    if (!data.show.due || !d) return null;
    var max = Math.max.apply(null, d.values.concat([1]));
    var bars = h("div", { class: "bars" + (d.values.length <= 14 ? " wide" : ""), "aria-hidden": "true" });
    d.values.forEach(function (v, i) {
      bars.append(h("span", { class: "bar" + (i === 0 ? " now" : ""), title: num(v) + " " + t.cards,
        style: "height:" + Math.max(2, Math.round(44 * v / max)) + "px" }));
    });
    return h("div", { class: "vs" },
      h("div", { class: "sh" }, h("b", null, t.due), period("due", d.days, d.choices, t.due), h("span", { class: "tot" }, num(d.total))),
      bars, h("div", { class: "axis" }, h("span", null, t.todayLower), h("span", null, d.last)));
  }

  function reviews(t) {
    var r = data.reviews;
    if (!data.show.reviews || !r) return null;
    var w = 240, hgt = 48, n = r.values.length, max = Math.max.apply(null, r.values.concat([1]));
    var pts = r.values.map(function (v, i) {
      return (n > 1 ? (w * i / (n - 1)) : w / 2).toFixed(1) + "," + (hgt - 2 - (hgt - 6) * v / max).toFixed(1);
    });
    var chart = h("svg", { class: "spark", role: "img", "aria-label": t.reviews + ": " + num(r.total), viewBox: "0 0 " + w + " " + hgt, preserveAspectRatio: "none" });
    chart.append(h("polygon", { points: "0," + hgt + " " + pts.join(" ") + " " + w + "," + hgt, style: "fill:var(--ss-accent);opacity:.16" }));
    chart.append(h("polyline", { points: pts.join(" "), fill: "none", "stroke-width": 2, "vector-effect": "non-scaling-stroke",
      "stroke-linejoin": "round", style: "stroke:var(--ss-accent)" }));
    return h("div", { class: "vs" },
      h("div", { class: "sh" }, h("b", null, t.reviews), period("reviews", r.days, r.choices, t.reviews), h("span", { class: "tot" }, num(r.total))),
      r.total ? chart : h("div", { class: "m", style: "margin-top:8px" }, t.noData));
  }

  function ring(value, label, color) {
    var c = 2 * Math.PI * 22, shown = value == null ? 0 : value;
    var s = h("svg", { role: "img", "aria-label": (value == null ? "–" : value + " %") + " " + label, width: 48, height: 48, viewBox: "0 0 54 54" });
    s.append(h("circle", { cx: 27, cy: 27, r: 22, fill: "none", "stroke-width": 6.5, style: "stroke:var(--ss-raised)" }));
    if (shown > 0) s.append(h("circle", { cx: 27, cy: 27, r: 22, fill: "none", "stroke-width": 6.5, "stroke-linecap": "round",
      transform: "rotate(-90 27 27)", style: "stroke:" + color + ";stroke-dasharray:" + (c * shown / 100).toFixed(1) + " " + c.toFixed(1) }));
    return h("div", { class: "rg" }, h("div", { class: "rgb" }, s, h("div", { class: "rgv" }, value == null ? "–" : value + "%")),
      h("span", { class: "m" }, label));
  }
  function memory(t) {
    var m = data.memory;
    if (!data.show.memory || !m) return null;
    return h("div", { class: "vs" },
      h("div", { class: "sh" }, h("b", null, t.memory), period("memory", m.days, m.choices, t.memory)),
      h("div", { class: "rings" }, ring(m.retention, t.remembered, "var(--ss-accent)"), ring(m.unseen, t.unseen, "var(--ss-new)")));
  }

  // --- menus ----------------------------------------------------------------
  function tools(t) {
    return h("div", { class: "tools" },
      h("button", { type: "button", class: "ib", "aria-label": t.choose, title: t.choose, "aria-expanded": menu === "show" ? "true" : "false",
        onclick: function (e) { e.stopPropagation(); menu = menu === "show" ? null : "show"; draw(); } },
        (function () { var s = svg("M4 7h9M19 7h1M4 17h1M11 17h9", 16); s.append(h("circle", { cx: 16, cy: 7, r: 2.5 })); s.append(h("circle", { cx: 8, cy: 17, r: 2.5 })); return s; })()),
      h("button", { type: "button", class: "ib", "aria-label": t.info, title: t.info, "aria-expanded": menu === "info" ? "true" : "false",
        onclick: function (e) { e.stopPropagation(); menu = menu === "info" ? null : "info"; draw(); } }, svg("M12 11v6M12 7v.5", 16, 2.2)));
  }
  function popup(t) {
    if (!menu) return null;
    var box = h("div", { class: "pop", onclick: function (e) { e.stopPropagation(); } });
    if (menu === "info") {
      [t.infoDue, t.infoReviews, t.infoMemory].forEach(function (text) {
        var i = text.indexOf(":");
        box.append(h("p", null, h("b", null, text.slice(0, i + 1)), text.slice(i + 1)));
      });
      return box;
    }
    [["countdown", t.showCountdown], ["plan", t.showPlan], ["level", t.showLevel], ["challenge", t.showChallenge], ["fact", t.showFact],
     ["due", t.showDue], ["reviews", t.showReviews], ["memory", t.showMemory]].forEach(function (pair) {
      box.append(h("label", null, h("input", { type: "checkbox", checked: data.show[pair[0]],
        onchange: function (e) { data.show[pair[0]] = e.currentTarget.checked; send("show", { which: pair[0], on: e.currentTarget.checked }); } }), pair[1]));
    });
    box.append(h("hr"));
    box.append(h("button", { type: "button", class: "link", onclick: function () { menu = null; draw(); send("settings"); } }, t.settings));
    return box;
  }

  var toastTimer = null;
  function toast(text) {
    var old = document.getElementById("ss-toast");
    if (old) old.remove();
    var el = h("div", { id: "ss-toast", role: "status", style: "position:fixed;left:50%;bottom:16px;transform:translateX(-50%);background:var(--ss-raised);" +
      "color:var(--ss-ink);padding:8px 14px;border-radius:18px;font-size:13px;z-index:9;max-width:90%" }, text);
    document.body.append(el);
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { el.remove(); }, 2600);
  }

  // --- page -----------------------------------------------------------------
  function draw() {
    if (!data) return;
    var t = data.t, app = document.getElementById("app"), keep = document.scrollingElement.scrollTop;
    var parts = [];
    var top = [head(t), plan(t)].filter(Boolean);
    var first = null;
    if (top.length) { first = h("section", { class: "card", "aria-label": t.today }); top.forEach(function (x) { first.append(x); }); parts.push(first); }
    var ex = extras(t);
    if (ex.length) { var mid = h("section", { class: "card" }); ex.forEach(function (x) { mid.append(x); }); parts.push(mid); }
    var charts = [due(t), reviews(t), memory(t)].filter(Boolean);
    var host;
    if (charts.length) {
      host = h("section", { class: "card has-tools" });
      charts.forEach(function (x) { host.append(x); });
      host.append(tools(t));
      parts.push(host);
    } else {
      host = h("div", { class: "lone", style: "position:relative;height:30px;width:70px" }, tools(t));
      host.querySelector(".tools").style.cssText = "top:0;inset-inline-end:0";
      parts.push(host);
    }
    var pop = popup(t);
    if (pop) { host.style.position = "relative"; host.append(pop); }
    app.replaceChildren.apply(app, parts);
    document.scrollingElement.scrollTop = keep;
    if (pop) pop.scrollIntoView({ block: "nearest" });
  }

  document.addEventListener("click", function () { if (menu) { menu = null; draw(); } });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && menu) { menu = null; draw(); } });
  document.addEventListener("contextmenu", function (e) { e.preventDefault(); });

  window.SSToday = {
    render: function (d) { data = d; pending = {}; draw(); },
  };
  function ready() { if (typeof pycmd === "function") send("ready"); else setTimeout(ready, 50); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", ready); else ready();
})();
