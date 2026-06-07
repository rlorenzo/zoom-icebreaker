import { beforeEach, describe, expect, it, vi } from "vitest";
import { createEngine } from "../engine.js";

// A fixed clock so ids/joinTimes are deterministic. The engine reads and writes
// localStorage, which jsdom shares across tests, so each test uses a unique key
// (and we clear storage) to stay isolated.
const NOW = Date.UTC(2024, 0, 1, 12, 0, 0);
const clock = () => NOW;
let n = 0;
const freshKey = () => `test.session.${n++}`;

const names = (snap) => snap.participants.map((p) => p.name);
const ids = (snap) => snap.participants.map((p) => p.id);
const byName = (snap, name) => snap.participants.find((p) => p.name === name);

beforeEach(() => {
  localStorage.clear();
});

describe("a fresh engine", () => {
  it("starts empty with a started time and no prompt", () => {
    const snap = createEngine({ key: freshKey(), now: clock }).snapshot();
    expect(snap.participants).toHaveLength(0);
    expect(snap.prompt).toBe("");
    expect(snap.startedAt).toBe(NOW);
  });

  it("snapshot is a copy — callers cannot mutate internal state", () => {
    const e = createEngine({ key: freshKey(), now: clock });
    e.add("Pat");
    e.snapshot().participants[0].name = "Hacked";
    expect(e.snapshot().participants[0].name).toBe("Pat");
  });
});

describe("transitions", () => {
  it("adds a manual, non-host, not-yet-introduced participant", () => {
    const e = createEngine({ key: freshKey(), now: clock });
    const last = e.add("Zoe Tan").participants.at(-1);
    expect(last).toMatchObject({
      name: "Zoe Tan",
      is_host: false,
      introduced: false,
      present: true,
    });
  });

  it("ignores a blank add", () => {
    const e = createEngine({ key: freshKey(), now: clock });
    expect(e.add("   ").participants).toHaveLength(0);
  });

  it("gives each add a distinct id even within the same millisecond", () => {
    const e = createEngine({ key: freshKey(), now: clock });
    e.add("A");
    const snap = e.add("B");
    expect(new Set(ids(snap)).size).toBe(2);
  });

  it("toggles introduced and removes by id", () => {
    const e = createEngine({ key: freshKey(), now: clock });
    const pid = e.add("Pat").participants[0].id;
    expect(byName(e.setIntroduced(pid, true), "Pat").introduced).toBe(true);
    expect(byName(e.setIntroduced(pid, false), "Pat").introduced).toBe(false);
    expect(e.remove(pid).participants).toHaveLength(0);
  });

  it("trims the prompt on set", () => {
    const e = createEngine({ key: freshKey(), now: clock });
    expect(e.setPrompt("  Pets?  ").prompt).toBe("Pets?");
  });
});

describe("order and randomize (no host in hosted mode)", () => {
  const seed = () => {
    const e = createEngine({ key: freshKey(), now: clock });
    for (const nm of ["Ann", "Bob", "Cy"]) e.add(nm);
    return e;
  };

  it("reorders to an explicit order, dropping unknowns and appending omitted", () => {
    const e = seed();
    const [a, b, c] = ids(e.snapshot());
    const out = e.setOrder([c, "ghost", a]); // b omitted
    expect(ids(out)).toEqual([c, a, b]);
  });

  it("randomize keeps introduced people in their slot and preserves membership", () => {
    const e = seed();
    const [, b] = ids(e.snapshot());
    e.setIntroduced(b, true);
    const before = names(e.snapshot());
    const after = e.randomize();
    expect(after.participants[1].name).toBe("Bob"); // introduced row holds slot
    expect(names(after).slice().sort()).toEqual(before.slice().sort());
  });

  it("reset clears participants, keeps the prompt, and restarts the clock", () => {
    const e = seed();
    e.setPrompt("Q?");
    const out = e.reset();
    expect(out.participants).toHaveLength(0);
    expect(out.prompt).toBe("Q?");
    expect(out.startedAt).toBe(NOW);
  });
});

describe("subscribe", () => {
  it("calls back immediately and on every mutation", () => {
    const e = createEngine({ key: freshKey(), now: clock });
    const fn = vi.fn();
    e.subscribe(fn);
    expect(fn).toHaveBeenCalledTimes(1); // immediate snapshot
    e.add("Pat");
    expect(fn).toHaveBeenCalledTimes(2);
    expect(fn.mock.lastCall[0].participants).toHaveLength(1);
  });
});

describe("persistence", () => {
  it("restores a saved session into a new engine on the same key", () => {
    const key = freshKey();
    const a = createEngine({ key, now: clock });
    a.add("Pat");
    a.setPrompt("Hello?");
    // A second engine on the same key (a page reload) sees the saved session.
    const b = createEngine({ key, now: clock }).snapshot();
    expect(names(b)).toEqual(["Pat"]);
    expect(b.prompt).toBe("Hello?");
  });

  it("starts fresh when stored data is malformed", () => {
    const key = freshKey();
    localStorage.setItem(key, "{ not json");
    expect(createEngine({ key, now: clock }).snapshot().participants).toHaveLength(0);
  });
});
