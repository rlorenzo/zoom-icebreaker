import { createDemoSession } from "./demo.js";
import { createEngine } from "./engine.js";
import {
  assignPositions,
  calloutHtml,
  findUpNextPid,
  fmtTime,
  rowHtml,
  sortForDisplay,
} from "./roster.js";

// ---- state cache & helpers --------------------------------------
let state = { participants: [], prompt: "", startedAt: Date.now() };
let lastFocusPid = null; // re-focus this row after the next render
let dragPid = null;
let dropTargetPid = null;
let dropBefore = true;

// Demo mode: when set, the page renders this in-memory sample session instead of
// the live session, and every action mutates it locally. The live session (from
// whichever transport is active) keeps arriving and is cached in `lastLiveState`
// so exiting demo can snap straight back to the clean live session. See demo.js.
let demo = null;
let lastLiveState = { participants: [], prompt: "", startedAt: Date.now() };
const inDemo = () => demo !== null;

// One small UI-preference flag (not meeting data): whether this browser has seen
// the first-run welcome. It only decides which empty state to show, so a
// blocked/unavailable localStorage degrades to "always first-run", which is fine.
const SEEN_KEY = "icebreaker.firstrun.seen";
const hasSeen = () => {
  try {
    return localStorage.getItem(SEEN_KEY) === "1";
  } catch {
    return false;
  }
};
const markSeen = () => {
  try {
    localStorage.setItem(SEEN_KEY, "1");
  } catch {
    /* storage unavailable — first-run prompt simply stays available */
  }
};

// DOM handles resolved in init() so importing this module has no side effects
// (keeps it unit/integration testable; the browser entry calls init() below).
let promptEl;
let promptSticky;
let roster;
let demoBar;

const $ = (id) => document.getElementById(id);
const stateById = (pid) => state.participants.find((p) => p.id === pid);
const hostFirst = () => state.participants[0]?.is_host;

// ---- transport ---------------------------------------------------
// The UI speaks one verb: post(url, body). Two transports answer it. On
// localhost, tracker.py serves an SSE stream at /events and mutates its session
// via the /api/* POSTs (serverTransport). Served statically with no backend
// (e.g. GitHub Pages), there is no server, so the same calls route into a local
// engine that holds the session in the browser (localTransport). init() probes
// once at startup and picks one; nothing below has to know which is live.
let activeTransport = null;
let markTransportReady;
const transportReady = new Promise((resolve) => {
  markTransportReady = resolve;
});
function post(url, body) {
  return activeTransport
    ? activeTransport.post(url, body)
    : transportReady.then((t) => t.post(url, body));
}

function serverTransport() {
  return {
    post: (url, body) =>
      fetch(url, {
        method: "POST",
        headers: body ? { "Content-Type": "application/json" } : {},
        body: body ? JSON.stringify(body) : undefined,
      }),
    subscribe(onSnapshot) {
      const es = new EventSource("/events");
      es.onmessage = (e) => onSnapshot(JSON.parse(e.data));
      es.onerror = () => {
        $("live").textContent = "reconnecting";
      };
      es.onopen = () => {
        $("live").textContent = "live";
      };
    },
  };
}

// The same /api/* paths the server handles, mapped to engine methods. Pure data,
// so the routing stays a flat table rather than a switch.
const LOCAL_ROUTES = [
  [/^\/api\/participant$/, (e, _m, b) => e.add(b.name)],
  [/^\/api\/participant\/([^/]+)\/introduced$/, (e, m, b) => e.setIntroduced(m[1], b.introduced)],
  [/^\/api\/participant\/([^/]+)\/remove$/, (e, m) => e.remove(m[1])],
  [/^\/api\/prompt$/, (e, _m, b) => e.setPrompt(b.prompt)],
  [/^\/api\/order$/, (e, _m, b) => e.setOrder(b.order)],
  [/^\/api\/randomize$/, (e) => e.randomize()],
  [/^\/api\/reset$/, (e) => e.reset()],
];

function localTransport(engine) {
  return {
    post(url, body) {
      const path = new URL(url, "http://local").pathname;
      const b = body || {};
      for (const [re, run] of LOCAL_ROUTES) {
        const m = re.exec(path);
        if (m) {
          run(engine, m, b);
          break;
        }
      }
      return Promise.resolve();
    },
    subscribe(onSnapshot) {
      engine.subscribe(onSnapshot);
      $("live").textContent = "live";
    },
  };
}

// Probe for a real backend: only tracker.py answers /events with an event-stream.
// A 404 page (GitHub Pages), an HTML index, or a network error all mean "no
// server, use the local engine". The body is cancelled so the probe never holds
// the stream open.
async function hasServer() {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 1500);
  try {
    const res = await fetch("events", { signal: ctrl.signal });
    const ct = res.headers.get("content-type") || "";
    res.body?.cancel?.();
    return res.ok && ct.includes("text/event-stream");
  } catch {
    return false;
  } finally {
    clearTimeout(timer);
  }
}
const postOrder = (order) =>
  inDemo() ? render(demo.setOrder(order)) : post("/api/order", { order });
const setIntroduced = (id, v) =>
  inDemo()
    ? render(demo.toggleIntroduced(id, v))
    : post(`/api/participant/${id}/introduced`, { introduced: v });
const removeP = (id) =>
  inDemo() ? render(demo.remove(id)) : post(`/api/participant/${id}/remove`);
const sendPrompt = (prompt) =>
  inDemo() ? render(demo.setPrompt(prompt)) : post("/api/prompt", { prompt });
const randomize = () => (inDemo() ? render(demo.randomize()) : post("/api/randomize"));
const addPerson = (name) =>
  inDemo() ? render(demo.add(name)) : post("/api/participant", { name });
// Reset means "clean slate". In demo that's just leaving demo; live it clears
// the server session.
const resetSession = () => (inDemo() ? exitDemo() : post("/api/reset"));

// ---- demo mode ---------------------------------------------------
function enterDemo() {
  markSeen();
  demo = createDemoSession();
  if (demoBar) demoBar.hidden = false;
  document.body.classList.add("is-demo");
  render(demo.snapshot());
}

function exitDemo() {
  demo = null;
  if (demoBar) demoBar.hidden = true;
  document.body.classList.remove("is-demo");
  render(lastLiveState); // snap back to the clean live session
}

// ---- DOM helpers -------------------------------------------------
function autosize(el) {
  el.style.height = "auto";
  el.style.height = `${el.scrollHeight}px`;
}

const reduceMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// FLIP: capture row top offsets before innerHTML rewrites the roster, then
// after the new DOM lands, animate each surviving row from its old position to
// its new one. Web Animations API bypasses the row's CSS transition, which we
// want — it would otherwise fight the slide.
function captureRowTops(rosterEl) {
  const m = new Map();
  for (const r of rosterEl.querySelectorAll(".row[data-pid]")) {
    m.set(r.dataset.pid, r.getBoundingClientRect().top);
  }
  return m;
}
function playReorder(rosterEl, oldTops) {
  if (reduceMotion()) return;
  for (const r of rosterEl.querySelectorAll(".row[data-pid]")) {
    const oldTop = oldTops.get(r.dataset.pid);
    if (oldTop == null) continue;
    const dy = oldTop - r.getBoundingClientRect().top;
    if (Math.abs(dy) < 2) continue;
    r.animate([{ transform: `translateY(${dy}px)` }, { transform: "translateY(0)" }], {
      duration: 2400,
      easing: "cubic-bezier(0.22, 1, 0.36, 1)",
    });
  }
}

// First launch on this browser gets a welcome that explains the surface and
// offers the demo; after that, a clearing (e.g. reset between rounds) shows a
// light line with the demo still one quiet click away. onboard.md: "First use"
// vs "User cleared".
function emptyStateHtml() {
  if (hasSeen()) {
    return `
      <div class="empty">
        <p class="empty-lede">No one yet. Joins appear automatically, or add someone below.</p>
        <button class="text-link" type="button" data-act="demo">Try the demo</button>
      </div>`;
  }
  return `
    <div class="empty first-run">
      <p class="empty-title">Your roster shows up here</p>
      <p class="empty-body">As people join, names fill in from Zoom automatically, or you add them by hand. You mark each person introduced as they speak, so the whole room can see who has gone and who is up next.</p>
      <button class="btn" type="button" data-act="demo">Try a demo</button>
      <p class="empty-foot">Opens a sample meeting you can click around. Nothing is saved, and leaving it clears the slate.</p>
    </div>`;
}

// ---- render ------------------------------------------------------
// Snapshot what we need from the PREVIOUS render before `state` is overwritten:
// which rows were introduced, who was up next, and where each row sat — so the
// new render can detect transitions and FLIP-animate moves.
function capturePrev() {
  const prev = state.participants || [];
  return {
    prevIntroduced: new Set(prev.filter((p) => p.introduced && p.present).map((p) => p.id)),
    prevUpNextPid: findUpNextPid(prev),
    oldTops: captureRowTops(roster),
  };
}

function updateStats(participants) {
  const present = participants.filter((p) => p.present);
  const waiting = present.filter((p) => !p.introduced);
  $("s-present").textContent = present.length;
  $("s-done").textContent = present.length - waiting.length;
  $("s-wait").textContent = waiting.length;
  $("calloutBox").innerHTML = calloutHtml(present, waiting);
}

function renderRoster(participants, ctx, oldTops) {
  if (!participants.length) {
    roster.innerHTML = emptyStateHtml();
    return;
  }
  roster.innerHTML = participants.map((p) => rowHtml(p, ctx)).join("");
  playReorder(roster, oldTops);
}

// Re-focus a row moved by keyboard, once it has re-rendered.
function restoreFocus() {
  if (!lastFocusPid) return;
  document.querySelector(`.row[data-pid="${lastFocusPid}"]`)?.focus();
  lastFocusPid = null;
}

export function render(s) {
  // Seeing real participants (not the demo) means this host is past first run.
  if (!inDemo() && s.participants.length > 0) markSeen();

  const positionByPid = assignPositions(s.participants);
  s = { ...s, participants: sortForDisplay(s.participants) };
  const { prevIntroduced, prevUpNextPid, oldTops } = capturePrev();

  state = s;

  $("since").textContent = fmtTime(s.startedAt);
  if (document.activeElement !== promptEl) {
    promptEl.value = s.prompt || "";
    autosize(promptEl);
  }

  updateStats(s.participants);

  const upNextPid = findUpNextPid(s.participants);
  const ctx = {
    positionByPid,
    upNextPid,
    upNextChanged: upNextPid && upNextPid !== prevUpNextPid,
    prevIntroduced,
  };
  renderRoster(s.participants, ctx, oldTops);
  restoreFocus();
}

// ---- drag and drop helpers --------------------------------------
function clearDropIndicators() {
  for (const el of document.querySelectorAll(".row.drop-before, .row.drop-after")) {
    el.classList.remove("drop-before", "drop-after");
  }
}

// Resolve the focused, reorderable row from a keyboard event, or null.
function focusedReorderRow(e) {
  const row = e.target.closest(".row");
  if (!row || row !== e.target) return null;
  const p = stateById(row.dataset.pid);
  // Mirror the drag handler: only present, non-host, not-yet-introduced rows
  // are reorderable (a participant may have left while their row held focus).
  if (!p || p.is_host || !p.present || p.introduced) return null;
  return { pid: row.dataset.pid };
}

// Compute the id order after nudging `pid` by `delta`, or null if the move is
// out of bounds or would land on a non-reorderable (host/introduced/absent)
// row. Pure, so the guard logic stays unit-testable and the handler stays flat.
function keyboardReorder(pid, delta) {
  const order = state.participants.map((x) => x.id);
  const fromIdx = order.indexOf(pid);
  const toIdx = fromIdx + delta;
  const minIdx = hostFirst() ? 1 : 0;
  if (toIdx < minIdx || toIdx >= order.length) return null;
  // Mirror the drag handler: don't reorder past an introduced (or absent) row.
  // Swapping with one shifts backend slot numbering with no visible move, since
  // sortForDisplay keeps introduced rows below waiting ones.
  const dest = state.participants[toIdx];
  if (!dest?.present || dest.introduced) return null;
  order.splice(fromIdx, 1);
  order.splice(toIdx, 0, pid);
  return order;
}

// ---- event wiring ------------------------------------------------
function wirePrompt() {
  promptEl.addEventListener("input", () => autosize(promptEl));
  promptEl.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      promptEl.blur();
    }
    if (e.key === "Escape") {
      promptEl.value = state.prompt || "";
      autosize(promptEl);
      promptEl.blur();
    }
  });
  promptEl.addEventListener("blur", () => {
    const next = promptEl.value.trim();
    if (next === (state.prompt || "").trim()) return;
    sendPrompt(next);
  });
  window.addEventListener("resize", () => autosize(promptEl));

  // Toggle a subtle hairline under the sticky prompt only when pinned.
  const pinSentinel = document.createElement("div");
  // Keep the sentinel in normal flow right before the sticky prompt so it
  // leaves the viewport exactly when the prompt becomes stuck (top:0), rather
  // than at the top of the document as an absolutely-positioned element would.
  pinSentinel.style.cssText = "height:1px;";
  promptSticky.before(pinSentinel);
  new IntersectionObserver(
    ([entry]) => promptSticky.classList.toggle("is-pinned", !entry.isIntersecting),
    { threshold: 0 },
  ).observe(pinSentinel);
}

function wireRosterActions() {
  // ---- click delegation -----------------------------------------
  document.addEventListener("click", (e) => {
    const t = e.target.closest("[data-act]");
    if (!t) return;
    const pid = t.dataset.pid;
    switch (t.dataset.act) {
      case "toggle":
        setIntroduced(pid, t.dataset.val === "true");
        break;
      case "remove":
        removeP(pid);
        break;
      case "demo":
        enterDemo();
        break;
      case "exit-demo":
        exitDemo();
        break;
    }
  });

  // ---- drag and drop --------------------------------------------
  roster.addEventListener("dragstart", (e) => {
    const row = e.target.closest(".row");
    if (!row) return;
    const pid = row.dataset.pid;
    const p = stateById(pid);
    if (!p || p.is_host || !p.present || p.introduced) {
      e.preventDefault();
      return;
    }
    dragPid = pid;
    e.dataTransfer.effectAllowed = "move";
    e.dataTransfer.setData("text/plain", pid);
    row.classList.add("dragging");
  });

  roster.addEventListener("dragend", (e) => {
    const row = e.target.closest(".row");
    if (row) row.classList.remove("dragging");
    clearDropIndicators();
    dragPid = null;
    dropTargetPid = null;
  });

  roster.addEventListener("dragover", (e) => {
    if (!dragPid) return;
    const row = e.target.closest(".row");
    if (!row) return;
    e.preventDefault();
    const pid = row.dataset.pid;
    if (pid === dragPid) return;
    const target = stateById(pid);
    if (!target || (target.introduced && !target.is_host)) return;
    clearDropIndicators();
    // Dropping on the host row is always interpreted as "after host".
    const rect = row.getBoundingClientRect();
    const before = target.is_host ? false : e.clientY < rect.top + rect.height / 2;
    row.classList.add(before ? "drop-before" : "drop-after");
    dropTargetPid = pid;
    dropBefore = before;
  });

  roster.addEventListener("drop", (e) => {
    if (!dragPid) return;
    e.preventDefault();
    clearDropIndicators();
    const targetPid = dropTargetPid;
    const moving = dragPid;
    dragPid = null;
    dropTargetPid = null;
    if (!targetPid) return;

    const order = state.participants.map((p) => p.id);
    const fromIdx = order.indexOf(moving);
    if (fromIdx < 0) return;
    order.splice(fromIdx, 1);
    const toIdx = order.indexOf(targetPid);
    if (toIdx < 0) return;
    order.splice(dropBefore ? toIdx : toIdx + 1, 0, moving);
    postOrder(order);
  });

  // ---- keyboard reorder -----------------------------------------
  roster.addEventListener("keydown", (e) => {
    const delta = e.key === "ArrowUp" ? -1 : e.key === "ArrowDown" ? 1 : 0;
    if (!delta) return;
    const target = focusedReorderRow(e);
    if (!target) return;
    e.preventDefault();
    const order = keyboardReorder(target.pid, delta);
    if (!order) return;
    lastFocusPid = target.pid;
    postOrder(order);
  });
}

function wireFooter() {
  $("addForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const input = $("addName");
    const name = input.value.trim();
    if (!name) return;
    input.value = "";
    await addPerson(name);
  });
  $("randomBtn").addEventListener("click", () => randomize());
  $("resetBtn").addEventListener("click", () => {
    // No real data to lose while in demo — just leave it (the demo bar's
    // "Exit demo" does the same). Live, confirm before clearing the session.
    if (inDemo()) return exitDemo();
    if (confirm("Clear all participants and start over? The prompt is kept.")) resetSession();
  });
}

// Cache every live snapshot so exiting demo can snap straight to it; only paint
// it when the demo isn't overriding the view.
function onLiveSnapshot(snap) {
  lastLiveState = snap;
  if (!inDemo()) render(snap);
}

// ---- bootstrap ---------------------------------------------------
export async function init() {
  promptEl = $("prompt");
  promptSticky = $("promptSticky");
  roster = $("roster");
  demoBar = $("demoBar");
  wirePrompt();
  wireRosterActions();
  wireFooter();
  activeTransport = (await hasServer()) ? serverTransport() : localTransport(createEngine());
  markTransportReady(activeTransport);
  activeTransport.subscribe(onLiveSnapshot);
}

await init();
