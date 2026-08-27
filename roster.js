// Pure markup / formatting helpers for the roster. No DOM or global state is
// touched here, so every function is deterministic and unit-testable on its
// own (see tests/roster.test.js). app.js imports these for rendering.

import { isReorderable } from "./session.js";

// ---- icons (inline so a single file ships) -----------------------
const ICON_CHECK = `<svg class="check" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 8.5l3 3 7-7" pathLength="100"/></svg>`;
const ICON_X = `<svg viewBox="0 0 16 16" width="12" height="12" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" aria-hidden="true"><path d="M4 4l8 8M12 4l-8 8"/></svg>`;

// ---- formatters --------------------------------------------------
export const fmtTime = (ts) =>
  new Date(ts).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });

function escapeHtml(s) {
  return String(s).replace(
    /[&<>"']/g,
    (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c],
  );
}

// Sort: host (not yet introduced) first, then waiting, then anyone introduced
// (including the host), then people who've left. Stable, so backend order is
// preserved within each bucket.
export function sortForDisplay(participants) {
  const rank = (p) => {
    if (!p.present) return 3;
    if (p.introduced) return 2;
    if (p.is_host) return 0;
    return 1;
  };
  return [...participants].sort((a, b) => rank(a) - rank(b));
}

// Up-next = the first present, not-yet-introduced person (the host counts if
// they haven't gone yet). Used both for row styling and for the baton-pass cue
// between renders.
export function findUpNextPid(participants) {
  const up = participants.find((p) => p.present && !p.introduced);
  return up ? up.id : null;
}

// Stable position numbers from the BACKEND order (host first, then non-host in
// arrival/drag order). Once a person has a number it sticks even after they
// introduce themselves and fall to the bottom — so "the host went first" still
// reads as "1".
export function assignPositions(participants) {
  const positionByPid = new Map();
  let pos = 0;
  for (const p of participants) {
    if (p.present) positionByPid.set(p.id, ++pos);
  }
  return positionByPid;
}

// The roster's up-next row already shows who's next, so the only callout we
// surface is the completion state — when everyone present has introduced
// themselves. Listing "Coming up: …" here just duplicated the list.
export function calloutHtml(present, waiting) {
  if (waiting.length === 0 && present.length > 0) {
    return `<div class="callout">Everyone has introduced themselves. Enjoy the meeting!</div>`;
  }
  return "";
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

// A reorderable row is focusable, so it has to say what focusing it buys you.
// Without the description it announced as an unlabelled group and the arrow-key
// reorder was reachable but undiscoverable.
function rowDragAttrs(p) {
  return isReorderable(p) ? 'draggable="true" tabindex="0" aria-describedby="reorderHint"' : "";
}

function toggleLabelHtml(p) {
  return p.introduced ? `${ICON_CHECK}<span>Introduced</span>` : `<span>Mark introduced</span>`;
}

export function rowHtml(p, { positionByPid, upNextPid, upNextChanged, prevIntroduced }) {
  const num = positionByPid.get(p.id) ?? "";
  const isUpNext = p.id === upNextPid;
  const justIntroduced = p.introduced && p.present && !prevIntroduced.has(p.id);
  const cls = rowClass(p, { isUpNext, upNextChanged, justIntroduced });
  const hostBit = p.is_host ? `<span class="host-pill">host</span>` : "";
  const leftTag = p.present ? "" : `<span class="tag">left</span>`;
  // "you're up next" speaks to the person reading their own name off the
  // shared screen; the tests pin the "up next" substring, which it keeps.
  const upNextTag =
    isUpNext && !p.is_host ? `<span class="up-next-tag">you&rsquo;re up next</span>` : "";
  return `
    <li class="${cls}" data-pid="${p.id}" ${rowDragAttrs(p)}>
      <div class="pos">${num}</div>
      <div class="name">
        <span class="who">${escapeHtml(p.name)}</span>
        ${hostBit}
        ${upNextTag}
        ${leftTag}
      </div>
      <div class="when">${fmtTime(p.joinTime)}</div>
      <button class="toggle ${p.introduced ? "on" : ""}" type="button"
              data-act="toggle" data-pid="${p.id}" data-val="${!p.introduced}"
              aria-pressed="${p.introduced}">
        ${toggleLabelHtml(p)}
      </button>
      <button class="x" type="button" data-act="remove" data-pid="${p.id}"
              aria-label="Remove ${escapeHtml(p.name)}">${ICON_X}</button>
    </li>`;
}
