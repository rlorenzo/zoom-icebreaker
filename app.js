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
import { isReorderable, permuteReorderable } from "./session.js";

// ---- state cache & helpers --------------------------------------
let state = { participants: [], prompt: "", startedAt: Date.now() };
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
      duration: 200,
      easing: "cubic-bezier(0.22, 1, 0.36, 1)",
    });
  }
}

// First launch on this browser gets a welcome that explains the surface and
// offers the demo; after that, a clearing (e.g. reset between rounds) shows a
// light line with the demo still one quiet click away. onboard.md: "First use"
// vs "User cleared".
function emptyStateHtml() {
  // An <li>, because it renders inside the roster's <ul>.
  if (hasSeen()) {
    return `
      <li class="empty">
        <p class="empty-lede">No one here yet. As people join, they&rsquo;ll appear on their own, or add someone below.</p>
        <button class="text-link" type="button" data-act="demo">Try the demo</button>
      </li>`;
  }
  return `
    <li class="empty first-run">
      <h2 class="empty-title">Welcome. Your attendance list is here.</h2>
      <p class="empty-body">As people join, names fill in from Zoom automatically, or you add them by hand. You mark each person introduced as they speak, so the whole room can see who has gone and who is up next.</p>
      <button class="btn" type="button" data-act="demo">Try a demo</button>
      <p class="empty-foot">Opens a sample meeting you can click around. Nothing is saved, and leaving it clears the slate.</p>
    </li>`;
}

// ---- render ------------------------------------------------------
// Snapshot what we need from the PREVIOUS render before `state` is overwritten:
// which rows were introduced, who was up next, and where each row sat — so the
// new render can detect transitions and FLIP-animate moves.
function capturePrev() {
  const prev = state.participants || [];
  return {
    prevParticipants: prev,
    prevIntroduced: new Set(prev.filter((p) => p.introduced && p.present).map((p) => p.id)),
    prevUpNextPid: findUpNextPid(prev),
    oldTops: captureRowTops(roster),
    focus: captureFocus(),
  };
}

function updateStats(participants) {
  const present = participants.filter((p) => p.present);
  const waiting = present.filter((p) => !p.introduced);
  $("s-present").textContent = present.length;
  $("s-done").textContent = present.length - waiting.length;
  $("s-wait").textContent = waiting.length;
  // Only rewrite the callout when it actually changes: a rewrite replays its
  // one-shot settle animation, and in auto mode the Zoom poller re-renders
  // every few seconds whether or not anything happened.
  const box = $("calloutBox");
  const callout = calloutHtml(present, waiting);
  if (box.innerHTML !== callout) box.innerHTML = callout;
}

function renderRoster(participants, ctx, oldTops) {
  if (!participants.length) {
    roster.innerHTML = emptyStateHtml();
    return;
  }
  roster.innerHTML = participants.map((p) => rowHtml(p, ctx)).join("");
  playReorder(roster, oldTops);
}

// Every render replaces the roster subtree, which silently drops keyboard focus
// to the document. That is not only a reorder problem: in auto mode the Zoom
// poller re-renders on its own schedule, so a host tabbing through the roster
// was thrown back to the top by a background read they never initiated. Capture
// which person had focus and which control on their row, then put it back.
function captureFocus() {
  const el = document.activeElement;
  if (!el || !roster.contains(el)) return null;
  const row = el.closest(".row[data-pid]");
  if (!row) return null;
  return { pid: row.dataset.pid, act: el === row ? null : el.dataset.act };
}

function restoreFocus(snap) {
  if (!snap) return;
  // Matched by property rather than by selector so a pid never has to be
  // escaped into one.
  const row = [...roster.querySelectorAll(".row[data-pid]")].find(
    (r) => r.dataset.pid === snap.pid,
  );
  if (!row) return;
  // The row itself is only focusable while it is still reorderable; once the
  // person is introduced it drops out of the tab order, so land on their toggle
  // instead of losing the place entirely.
  const rowTarget = row.hasAttribute("tabindex") ? row : row.querySelector(".toggle");
  const target = snap.act ? row.querySelector(`[data-act="${snap.act}"]`) : rowTarget;
  // preventScroll because marking someone introduced re-ranks their row below
  // everyone still waiting, and a bare focus() scrolls that new position into
  // view — one click threw the shared screen to the bottom of the roster
  // mid-meeting. Focus still moves for the keyboard; the viewport stays put.
  target?.focus({ preventScroll: true });
}

// One sentence per change, for assistive tech. The roster is no longer a live
// region — it is rewritten wholesale, so announcing it re-read every name on
// every frame. This says only what actually changed.
export function describeChange(prev, next) {
  const before = new Map(prev.map((p) => [p.id, p]));
  const waiting = next.filter((p) => p.present && !p.introduced).length;

  // Only someone already on the roster can have been marked. A name whose very
  // first frame shows them introduced arrived that way — the opening snapshot,
  // or entering the demo, whose sample roster seeds two people as done — and is
  // reported as a join below rather than as a toggle nobody performed.
  const known = next.filter((p) => before.has(p.id));

  const introduced = known.find((p) => p.introduced && !before.get(p.id).introduced);
  if (introduced) return `${introduced.name} introduced. ${waiting} still to go.`;

  const undone = known.find((p) => !p.introduced && before.get(p.id).introduced);
  if (undone) return `${undone.name} marked not introduced. ${waiting} still to go.`;

  const joined = next.filter((p) => !before.has(p.id));
  if (joined.length === 1) return `${joined[0].name} joined.`;
  if (joined.length > 1) return `${joined.length} people joined.`;

  // "Removed" is off the roster entirely, which is not the same as p.present —
  // someone who leaves the call stays listed, greyed, and is not announced.
  const stillListed = new Set(next.map((p) => p.id));
  const removed = prev.filter((p) => !stillListed.has(p.id));
  if (removed.length === 1) return `${removed[0].name} removed.`;
  if (removed.length > 1) return `${removed.length} people removed.`;

  return "";
}

export function render(s) {
  // Seeing real participants (not the demo) means this host is past first run.
  if (!inDemo() && s.participants.length > 0) markSeen();

  const positionByPid = assignPositions(s.participants);
  const displayList = sortForDisplay(s.participants);
  const { prevParticipants, prevIntroduced, prevUpNextPid, oldTops, focus } = capturePrev();

  // Keep `state` in BACKEND order. The reorder handlers derive the posted
  // order from it, and posting the display-sorted list would renumber
  // introduced rows — their sticky positions come from their backend slots.
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
  renderRoster(displayList, ctx, oldTops);
  restoreFocus(focus);

  const message = describeChange(prevParticipants, s.participants);
  if (message) $("srStatus").textContent = message;
}

// ---- drag and drop helpers --------------------------------------
function clearDropIndicators() {
  for (const el of document.querySelectorAll(".row.drop-before, .row.drop-after")) {
    el.classList.remove("drop-before", "drop-after");
  }
}

// Resolve the focused, reorderable row from a keyboard event, or null
// (a participant may have left while their row held focus).
function focusedReorderRow(e) {
  const row = e.target.closest(".row");
  if (!row || row !== e.target) return null;
  const p = stateById(row.dataset.pid);
  if (!p || !isReorderable(p)) return null;
  return { pid: row.dataset.pid };
}

// Compute the id order after nudging `pid` one visible slot up or down among
// the reorderable rows, or null when the move falls off either end. Host,
// introduced, and departed rows are skipped entirely, so their backend slots
// (and sticky position numbers) never shift. Pure, so the guard logic stays
// unit-testable and the handler stays flat.
function keyboardReorder(pid, delta) {
  const sub = state.participants.filter(isReorderable).map((p) => p.id);
  const fromIdx = sub.indexOf(pid);
  const toIdx = fromIdx + delta;
  if (fromIdx < 0 || toIdx < 0 || toIdx >= sub.length) return null;
  sub.splice(fromIdx, 1);
  sub.splice(toIdx, 0, pid);
  return permuteReorderable(state.participants, sub);
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
    if (!p || !isReorderable(p)) {
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
    // Valid drop targets are reorderable rows, plus the host row (interpreted
    // as "after host"). Introduced and departed rows are skipped: dropping
    // next to one would shift backend slots with no meaningful visible move.
    if (!target || !(isReorderable(target) || target.is_host)) return;
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

    // Move within the reorderable rows only, then map back onto the full
    // backend order so host/introduced/departed slots stay untouched.
    const sub = state.participants.filter(isReorderable).map((p) => p.id);
    const fromIdx = sub.indexOf(moving);
    if (fromIdx < 0) return;
    sub.splice(fromIdx, 1);
    let toIdx;
    if (stateById(targetPid)?.is_host) {
      toIdx = 0; // dropping on the host row means "first after the host"
    } else {
      const t = sub.indexOf(targetPid);
      if (t < 0) return;
      toIdx = dropBefore ? t : t + 1;
    }
    sub.splice(toIdx, 0, moving);
    postOrder(permuteReorderable(state.participants, sub));
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
    // No bookkeeping needed: the row is focused right now, so the render's own
    // focus capture already knows where to put it back.
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
