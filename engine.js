// engine.js -- the live session, in the browser.
//
// On localhost, tracker.py holds the session in memory and streams it over SSE.
// With no backend (e.g. served statically from GitHub Pages), this engine plays
// the same role entirely client-side: it holds the roster, applies every UI
// action, and persists to localStorage so a refresh mid-meeting keeps the slate.
// app.js picks between this and the server transport at startup.
//
// It is a faithful port of tracker.py's State for the operations the UI drives:
// add / remove / introduced / prompt / order / randomize / reset. Zoom
// auto-reading has no browser equivalent, so hosted mode is manual-entry only —
// there is no host flag, which the shared ordering helpers already handle.
//
// No DOM or globals are touched, so it is deterministic and unit-testable (see
// tests/engine.test.js). subscribe(fn) calls back immediately with the current
// snapshot and again after every mutation, mirroring the SSE echo.

import { applyOrder, cloneRoster, findHostId, randomizeOrder } from "./session.js";

const STORE_KEY = "icebreaker.session.v1";

// A stored participant is usable if it looks like what commit() writes.
// Anything else — nulls or foreign shapes from a corrupted write, or another
// page sharing this origin's localStorage (e.g. project sites on
// username.github.io) — is dropped rather than adopted and re-persisted, since
// a null entry would make every later mutation throw on `p.id`.
const isParticipant = (p) =>
  p !== null && typeof p === "object" && typeof p.id === "string" && typeof p.name === "string";

// localStorage may be blocked (private mode, embedded contexts). Both helpers
// degrade silently: a blocked read starts a fresh session, a blocked write just
// means this session won't survive a reload — the meeting still works.
function loadSaved(key) {
  try {
    const data = JSON.parse(localStorage.getItem(key) || "null");
    if (!data || !Array.isArray(data.participants)) return null;
    return {
      startedAt: typeof data.startedAt === "number" ? data.startedAt : null,
      prompt: typeof data.prompt === "string" ? data.prompt : "",
      participants: data.participants.filter(isParticipant),
    };
  } catch {
    return null;
  }
}
function persist(key, data) {
  try {
    localStorage.setItem(key, JSON.stringify(data));
  } catch {
    /* storage unavailable — session simply won't survive a reload */
  }
}

export function createEngine({ key = STORE_KEY, now = Date.now } = {}) {
  const saved = loadSaved(key);
  let startedAt = saved?.startedAt ?? now();
  let prompt = saved?.prompt ?? "";
  let participants = saved?.participants ?? [];
  let seq = 0;
  const listeners = new Set();

  // No one is flagged host in manual/hosted mode, but resolve it anyway so the
  // ordering helpers stay correct if a saved session ever carried one.
  const hostId = () => findHostId(participants);
  const snapshot = () => ({ startedAt, prompt, participants: cloneRoster(participants) });

  const emit = () => {
    const snap = snapshot();
    for (const fn of listeners) fn(snap);
    return snap;
  };

  // Save, then echo the new snapshot to every subscriber — the local stand-in
  // for tracker.py's broadcast(). Returns the snapshot for direct callers/tests.
  const commit = () => {
    persist(key, { startedAt, prompt, participants });
    return emit();
  };

  // Another tab of this origin may commit to the same key (the host often
  // opens one tab to screen-share and one to drive). Adopt those writes so a
  // stale tab reflects them instead of clobbering them with its own old state
  // on its next action. The storage event only fires in the tabs that did NOT
  // write, so this never loops.
  if (typeof window !== "undefined") {
    window.addEventListener("storage", (e) => {
      if (e.key !== key) return;
      const next = loadSaved(key);
      if (!next) return;
      startedAt = next.startedAt ?? startedAt;
      prompt = next.prompt;
      participants = next.participants;
      emit();
    });
  }

  return {
    snapshot,

    subscribe(fn) {
      listeners.add(fn);
      fn(snapshot());
    },

    add(name) {
      const nm = String(name ?? "").trim();
      if (nm) {
        participants.push({
          id: `m${now().toString(36)}${(seq++).toString(36)}`,
          name: nm,
          joinTime: now(),
          leftTime: null,
          present: true,
          introduced: false,
          is_host: false,
        });
      }
      return commit();
    },

    remove(pid) {
      participants = participants.filter((p) => p.id !== pid);
      return commit();
    },

    setIntroduced(pid, val) {
      const p = participants.find((x) => x.id === pid);
      if (p) p.introduced = Boolean(val);
      return commit();
    },

    setPrompt(next) {
      prompt = String(next ?? "").trim();
      return commit();
    },

    setOrder(orderList) {
      participants = applyOrder(participants, orderList ?? [], hostId());
      return commit();
    },

    randomize() {
      participants = randomizeOrder(participants, hostId(), Math.random);
      return commit();
    },

    // Clean slate for the next round; keep the prompt, like State.reset.
    reset() {
      startedAt = now();
      participants = [];
      return commit();
    },
  };
}
