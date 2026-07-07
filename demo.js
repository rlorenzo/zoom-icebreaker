// Demo mode: a self-contained, in-memory sample session that lets a first-time
// host try the whole UI before a real meeting — set a prompt, mark people
// introduced, reorder, randomize — without a Zoom call and without touching the
// server. State lives only in this tab; exiting demo drops it and the page falls
// back to the (clean) live session. See app.js for the wiring.
//
// The transitions here mirror tracker.py's State so the demo behaves exactly
// like the real thing: host pinned to the top, randomize shuffles only the
// still-to-go people, introduced rows keep their slot. The ordering logic is
// shared with the live local engine (session.js), so demo and a real hosted
// session reorder identically. No DOM or globals are touched, so every method
// is deterministic and unit-testable (see tests/demo.test.js). app.js feeds
// each snapshot() straight into render().

import { applyOrder, cloneRoster, findHostId, randomizeOrder } from "./session.js";

// The sample prompt + roster. Picked to teach the interface in one glance:
// the host has already gone (so a non-host carries the visible "up next" cue),
// two people are introduced (showing the dimmed + checkmark treatment), and one
// long name exercises the row's truncation. Counts read 6 in the room / 2
// introduced / 4 still to go the instant demo opens.
const SAMPLE_PROMPT = "What's a highlight from your week?";

const SAMPLE_PEOPLE = [
  { name: "Maya Chen", is_host: true, introduced: true, joinOffset: 0 },
  { name: "Daniel Okonkwo-Williams", introduced: false, joinOffset: 41 },
  { name: "Priya Anand", introduced: false, joinOffset: 73 },
  { name: "Tom Becker", introduced: true, joinOffset: 96 },
  { name: "Sofia Marchetti", introduced: false, joinOffset: 128 },
  { name: "Wei Zhang", introduced: false, joinOffset: 164 },
];

// The demo presents as a meeting that began 9 minutes ago, so the seeded join
// times read as a plausible spread across the session so far.
const SESSION_AGE_MS = 9 * 60 * 1000;

// Build the seeded participant list, offsetting each join from the shared
// `startedAt` so the demo's timeline stays consistent with the snapshot.
function seedParticipants(startedAt) {
  return SAMPLE_PEOPLE.map((p, i) => ({
    id: `demo-${i}`,
    name: p.name,
    joinTime: startedAt + p.joinOffset * 1000,
    leftTime: null,
    present: true,
    introduced: Boolean(p.introduced),
    is_host: Boolean(p.is_host),
  }));
}

// A demo session holds the same fields the server snapshot exposes:
// { startedAt, prompt, participants }. Participants stay in BACKEND order
// (host first, then arrival/drag order); render() re-sorts for display and
// numbers positions from this order, so the host keeps "1" even after going.
// `now` is a clock function (like engine.js takes) so manual adds get the time
// they happen, not the time the demo opened.
export function createDemoSession(now = Date.now, rng = Math.random) {
  const startedAt = now() - SESSION_AGE_MS;
  let prompt = SAMPLE_PROMPT;
  let participants = seedParticipants(startedAt);
  let manualSeq = 0;

  const find = (pid) => participants.find((p) => p.id === pid);
  const hostId = () => findHostId(participants);
  const snapshot = () => ({ startedAt, prompt, participants: cloneRoster(participants) });

  return {
    snapshot,

    setPrompt(next) {
      prompt = String(next ?? "").trim();
      return snapshot();
    },

    toggleIntroduced(pid, val) {
      const p = find(pid);
      if (p) p.introduced = Boolean(val);
      return snapshot();
    },

    add(name) {
      const nm = String(name ?? "").trim();
      if (nm) {
        participants.push({
          id: `demo-m${manualSeq++}`,
          name: nm,
          joinTime: now(),
          leftTime: null,
          present: true,
          introduced: false,
          is_host: false,
        });
      }
      return snapshot();
    },

    remove(pid) {
      participants = participants.filter((p) => p.id !== pid);
      return snapshot();
    },

    // Apply a host-pinned order. Unknown ids drop; any omitted ids tack on at
    // the end — mirrors State.set_order so drag/keyboard reorder feels identical.
    setOrder(orderList) {
      participants = applyOrder(participants, orderList, hostId());
      return snapshot();
    },

    // Shuffle only the still-to-go non-hosts; introduced people keep their slot,
    // the host stays pinned. Mirrors State.randomize.
    randomize() {
      participants = randomizeOrder(participants, hostId(), rng);
      return snapshot();
    },
  };
}
