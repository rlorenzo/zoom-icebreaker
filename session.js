// Pure, deterministic ordering helpers for a roster's participants. Shared by
// the in-browser live engine (engine.js) and the demo session (demo.js) so the
// two reorder identically and the logic lives in exactly one place — and so it
// stays a faithful port of tracker.py's State.set_order / State.randomize. No
// DOM, no globals, no persistence: every function returns new data and never
// mutates its input (see tests via demo.test.js and engine.test.js).

// The id of the participant flagged host, or null (manual/hosted mode flags no
// one). Shared so demo and engine resolve it identically.
export const findHostId = (participants) => participants.find((p) => p.is_host)?.id ?? null;

// Only present, not-yet-introduced non-hosts can be dragged or nudged into a
// new slot. Shared by rendering (roster.js) and the reorder handlers (app.js)
// so the draggable affordance and the accepted moves can never disagree.
export const isReorderable = (p) => !p.is_host && p.present && !p.introduced;

// Rebuild the full id order with the reorderable participants permuted into
// `reorderedIds`, while everyone else (host, introduced, departed) keeps their
// backend slot. This is what keeps position numbers sticky (see
// roster.js assignPositions): reordering the waiting people never shifts the
// slots of those who already went.
export function permuteReorderable(participants, reorderedIds) {
  let k = 0;
  return participants.map((p) => (isReorderable(p) ? reorderedIds[k++] : p.id));
}

// A deep-enough copy of the roster for snapshots, so callers can't mutate state.
export const cloneRoster = (participants) => participants.map((p) => ({ ...p }));

// Fisher-Yates with an injectable RNG so callers stay testable. Returns a new
// array; never mutates the input.
function shuffled(items, rng) {
  const a = [...items];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

// Return a new id list with `hostId` pinned to index 0 (no-op when absent, as
// in manual/hosted mode where no one is flagged host).
function pinHost(ids, hostId) {
  if (hostId == null) return [...ids];
  return [hostId, ...ids.filter((id) => id !== hostId)];
}

// Map an id order back onto participant objects, host-pinned. Unknown ids drop
// and any omitted ids tack on at the end in their current order. Mirrors
// State.set_order.
export function applyOrder(participants, orderList, hostId) {
  const known = new Set(participants.map((p) => p.id));
  const seen = new Set();
  const next = [];
  for (const id of orderList) {
    if (known.has(id) && !seen.has(id)) {
      seen.add(id);
      next.push(id);
    }
  }
  for (const p of participants) if (!seen.has(p.id)) next.push(p.id);
  const order = pinHost(next, hostId);
  const byId = new Map(participants.map((p) => [p.id, p]));
  return order.map((id) => byId.get(id));
}

// Shuffle only the still-to-go non-hosts; introduced people keep their slot and
// the host stays pinned. Mirrors State.randomize.
export function randomizeOrder(participants, hostId, rng) {
  const nonHost = participants.filter((p) => p.id !== hostId);
  const pool = shuffled(
    nonHost.filter((p) => !p.introduced).map((p) => p.id),
    rng,
  );
  let k = 0;
  const reordered = nonHost.map((p) => (p.introduced ? p.id : pool[k++]));
  const order = pinHost(reordered, hostId);
  const byId = new Map(participants.map((p) => [p.id, p]));
  return order.map((id) => byId.get(id));
}
