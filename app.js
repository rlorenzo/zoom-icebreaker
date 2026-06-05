// ---- icons (inline so a single file ships) -----------------------
const ICON_CHECK = `<svg class="check" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 8.5l3 3 7-7" pathLength="100"/></svg>`;
const ICON_X = `<svg viewBox="0 0 16 16" width="12" height="12" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" aria-hidden="true"><path d="M4 4l8 8M12 4l-8 8"/></svg>`;

// ---- formatters --------------------------------------------------
const fmtTime = (ts) => new Date(ts).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });

function escapeHtml(s) {
  return String(s).replace(
    /[&<>"']/g,
    (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c],
  );
}

// ---- state cache & helpers --------------------------------------
let state = { participants: [], prompt: "", startedAt: Date.now() };
let lastFocusPid = null; // re-focus this row after the next render
let dragPid = null;
let dropTargetPid = null;
let dropBefore = true;

const $ = (id) => document.getElementById(id);
const stateById = (pid) => state.participants.find((p) => p.id === pid);
const hostFirst = () => state.participants[0]?.is_host;

// ---- API ---------------------------------------------------------
async function post(url, body) {
  return fetch(url, {
    method: "POST",
    headers: body ? { "Content-Type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined,
  });
}
const postOrder = (order) => post("/api/order", { order });
const setIntroduced = (id, v) => post(`/api/participant/${id}/introduced`, { introduced: v });
const removeP = (id) => post(`/api/participant/${id}/remove`);
const sendPrompt = (prompt) => post("/api/prompt", { prompt });
const randomize = () => post("/api/randomize");
const resetSession = () => post("/api/reset");
const addPerson = (name) => post("/api/participant", { name });

// ---- prompt textarea --------------------------------------------
const promptEl = $("prompt");
function autosize(el) {
  el.style.height = "auto";
  el.style.height = `${el.scrollHeight}px`;
}
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
const promptSticky = $("promptSticky");
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

// Sort: host (not yet introduced) first, then waiting,
// then anyone introduced (including the host), then people who've
// left. Stable, so backend order is preserved within each bucket.
function sortForDisplay(participants) {
  const rank = (p) => {
    if (!p.present) return 3;
    if (p.introduced) return 2;
    if (p.is_host) return 0;
    return 1;
  };
  return [...participants].sort((a, b) => rank(a) - rank(b));
}

// Up-next = the first present, not-yet-introduced person (the host
// counts if they haven't gone yet). Used both for row styling and
// for the baton-pass cue between renders.
function findUpNextPid(participants) {
  const up = participants.find((p) => p.present && !p.introduced);
  return up ? up.id : null;
}

const reduceMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// FLIP: capture row top offsets before innerHTML rewrites the roster,
// then after the new DOM lands, animate each surviving row from its
// old position to its new one. Web Animations API bypasses the row's
// CSS transition, which we want — it would otherwise fight the slide.
function captureRowTops(roster) {
  const m = new Map();
  for (const r of roster.querySelectorAll(".row[data-pid]")) {
    m.set(r.dataset.pid, r.getBoundingClientRect().top);
  }
  return m;
}
function playReorder(roster, oldTops) {
  if (reduceMotion()) return;
  for (const r of roster.querySelectorAll(".row[data-pid]")) {
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

// ---- markup builders ---------------------------------------------
// Stable position numbers from the BACKEND order (host first, then
// non-host in arrival/drag order). Once a person has a number it
// sticks even after they introduce themselves and fall to the bottom
// — so "the host went first" still reads as "1".
function assignPositions(participants) {
  const positionByPid = new Map();
  let pos = 0;
  for (const p of participants) {
    if (p.present) positionByPid.set(p.id, ++pos);
  }
  return positionByPid;
}

function calloutHtml(present, waiting) {
  if (waiting.length === 0) {
    return present.length > 0
      ? `<div class="callout">Everyone has introduced themselves.</div>`
      : "";
  }
  const lead = escapeHtml(waiting[0].name);
  const rest = waiting.slice(1).map((p) => escapeHtml(p.name));
  let body;
  if (rest.length === 0) body = `<b>${lead}</b>.`;
  else if (rest.length === 1) body = `<b>${lead}</b>, then ${rest[0]}.`;
  else body = `<b>${lead}</b>, then ${rest.join(", ")}.`;
  return `<div class="callout"><span class="lead">Coming up:</span>${body}</div>`;
}

function rowClass(p, { isUpNext, upNextChanged, justIntroduced }) {
  return [
    "row",
    p.is_host ? "host" : "",
    p.introduced ? "introduced" : "",
    p.present ? "" : "left",
    isUpNext ? "up-next" : "",
    isUpNext && upNextChanged ? "just-cued" : "",
    justIntroduced ? "just-introduced" : "",
  ]
    .filter(Boolean)
    .join(" ");
}

// Only present, not-yet-introduced non-hosts can be reordered.
function rowDragAttrs(p) {
  const reorderable = !p.is_host && p.present && !p.introduced;
  return reorderable ? 'draggable="true" tabindex="0"' : "";
}

function toggleLabelHtml(p) {
  return p.introduced ? `${ICON_CHECK}<span>Introduced</span>` : `<span>Mark introduced</span>`;
}

function rowHtml(p, { positionByPid, upNextPid, upNextChanged, prevIntroduced }) {
  const num = positionByPid.get(p.id) ?? "";
  const isUpNext = p.id === upNextPid;
  const justIntroduced = p.introduced && p.present && !prevIntroduced.has(p.id);
  const cls = rowClass(p, { isUpNext, upNextChanged, justIntroduced });
  const hostBit = p.is_host ? `<span class="host-pill">host</span>` : "";
  const leftTag = p.present ? "" : `<span class="tag">left</span>`;
  const upNextTag = isUpNext && !p.is_host ? `<span class="up-next-tag">up next</span>` : "";
  return `
    <div class="${cls}" data-pid="${p.id}" ${rowDragAttrs(p)}>
      <div class="pos">${num}</div>
      <div class="name">
        <span class="who">${escapeHtml(p.name)}</span>
        ${hostBit}
        ${upNextTag}
        ${leftTag}
      </div>
      <div class="when">${fmtTime(p.joinTime)}</div>
      <button class="toggle ${p.introduced ? "on" : ""}" type="button"
              data-act="toggle" data-pid="${p.id}" data-val="${!p.introduced}">
        ${toggleLabelHtml(p)}
      </button>
      <button class="x" type="button" data-act="remove" data-pid="${p.id}"
              aria-label="Remove ${escapeHtml(p.name)}">${ICON_X}</button>
    </div>`;
}

// ---- render ------------------------------------------------------
function render(s) {
  const positionByPid = assignPositions(s.participants);

  s = { ...s, participants: sortForDisplay(s.participants) };

  // Diff against the previous state BEFORE we overwrite it — that's
  // how we know which rows just transitioned and where they came from.
  const prevIntroduced = new Set(
    (state.participants || []).filter((p) => p.introduced && p.present).map((p) => p.id),
  );
  const prevUpNextPid = findUpNextPid(state.participants || []);
  const roster = $("roster");
  const oldTops = captureRowTops(roster);

  state = s;

  $("since").textContent = fmtTime(s.startedAt);

  if (document.activeElement !== promptEl) {
    promptEl.value = s.prompt || "";
    autosize(promptEl);
  }

  const present = s.participants.filter((p) => p.present);
  const done = s.participants.filter((p) => p.introduced && p.present);
  const waiting = present.filter((p) => !p.introduced);

  $("s-present").textContent = present.length;
  $("s-done").textContent = done.length;
  $("s-wait").textContent = waiting.length;

  $("calloutBox").innerHTML = calloutHtml(present, waiting);

  // Roster
  const upNextPid = findUpNextPid(s.participants);
  const upNextChanged = upNextPid && upNextPid !== prevUpNextPid;
  if (!s.participants.length) {
    roster.innerHTML = `<div class="empty">No one yet. Joins will appear automatically, or add someone below.</div>`;
  } else {
    const ctx = { positionByPid, upNextPid, upNextChanged, prevIntroduced };
    roster.innerHTML = s.participants.map((p) => rowHtml(p, ctx)).join("");
    playReorder(roster, oldTops);
  }

  // Restore focus to row moved by keyboard
  if (lastFocusPid) {
    const el = document.querySelector(`.row[data-pid="${lastFocusPid}"]`);
    if (el) el.focus();
    lastFocusPid = null;
  }
}

// ---- click delegation -------------------------------------------
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
  }
});
// ---- drag and drop ----------------------------------------------
const roster = $("roster");

function clearDropIndicators() {
  for (const el of document.querySelectorAll(".row.drop-before, .row.drop-after")) {
    el.classList.remove("drop-before", "drop-after");
  }
}

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

// ---- keyboard reorder -------------------------------------------
// Resolve the focused, reorderable row from a keyboard event, or null.
function focusedReorderRow(e) {
  const row = e.target.closest(".row");
  if (!row || row !== e.target) return null;
  const p = stateById(row.dataset.pid);
  if (!p || p.is_host || p.introduced) return null;
  return { pid: row.dataset.pid };
}

roster.addEventListener("keydown", (e) => {
  const delta = e.key === "ArrowUp" ? -1 : e.key === "ArrowDown" ? 1 : 0;
  if (!delta) return;
  const target = focusedReorderRow(e);
  if (!target) return;
  e.preventDefault();
  const order = state.participants.map((x) => x.id);
  const fromIdx = order.indexOf(target.pid);
  const toIdx = fromIdx + delta;
  const minIdx = hostFirst() ? 1 : 0;
  if (toIdx < minIdx || toIdx >= order.length) return;
  order.splice(fromIdx, 1);
  order.splice(toIdx, 0, target.pid);
  lastFocusPid = target.pid;
  postOrder(order);
});

// ---- footer actions ---------------------------------------------
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
  if (confirm("Clear all participants and start over? The prompt is kept.")) resetSession();
});

// ---- live stream -------------------------------------------------
let last = null;
const es = new EventSource("/events");
es.onmessage = (e) => {
  last = JSON.parse(e.data);
  render(last);
};
es.onerror = () => {
  $("live").textContent = "reconnecting";
};
es.onopen = () => {
  $("live").textContent = "live";
};
