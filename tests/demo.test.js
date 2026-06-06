import { describe, expect, it } from "vitest";
import { createDemoSession } from "../demo.js";

// A fixed clock so seeded times are deterministic; a fixed RNG so randomize()
// is reproducible (returns 0 -> Fisher-Yates leaves the pool order untouched).
const NOW = Date.UTC(2024, 0, 1, 12, 0, 0);
const noShuffle = () => 0;

const ids = (snap) => snap.participants.map((p) => p.id);
const names = (snap) => snap.participants.map((p) => p.name);
const byName = (snap, n) => snap.participants.find((p) => p.name === n);

describe("createDemoSession seed", () => {
  it("seeds six present people with the host pinned first", () => {
    const snap = createDemoSession(NOW).snapshot();
    expect(snap.participants).toHaveLength(6);
    expect(snap.participants.every((p) => p.present)).toBe(true);
    expect(snap.participants[0].is_host).toBe(true);
    expect(snap.participants.filter((p) => p.is_host)).toHaveLength(1);
  });

  it("teaches both states at a glance: host gone, two introduced, four waiting", () => {
    const snap = createDemoSession(NOW).snapshot();
    const introduced = snap.participants.filter((p) => p.introduced);
    expect(introduced.map((p) => p.name)).toEqual(["Maya Chen", "Tom Becker"]);
    expect(byName(snap, "Maya Chen").is_host).toBe(true);
    expect(snap.participants.filter((p) => !p.introduced)).toHaveLength(4);
  });

  it("carries a sample prompt and a started time in the past", () => {
    const snap = createDemoSession(NOW).snapshot();
    expect(snap.prompt).toMatch(/\?$/);
    expect(snap.startedAt).toBeLessThan(NOW);
  });

  it("snapshot is a copy — callers cannot mutate internal state", () => {
    const d = createDemoSession(NOW);
    d.snapshot().participants[0].name = "Hacked";
    expect(d.snapshot().participants[0].name).toBe("Maya Chen");
  });
});

describe("transitions", () => {
  it("toggles introduced on a single participant", () => {
    const d = createDemoSession(NOW);
    const pid = byName(d.snapshot(), "Priya Anand").id;
    expect(byName(d.toggleIntroduced(pid, true), "Priya Anand").introduced).toBe(true);
    expect(byName(d.toggleIntroduced(pid, false), "Priya Anand").introduced).toBe(false);
  });

  it("adds a manual, non-host, not-yet-introduced participant at the end", () => {
    const d = createDemoSession(NOW);
    const snap = d.add("Zoe Tan");
    const last = snap.participants.at(-1);
    expect(last.name).toBe("Zoe Tan");
    expect(last.is_host).toBe(false);
    expect(last.introduced).toBe(false);
    expect(snap.participants).toHaveLength(7);
  });

  it("ignores a blank manual add", () => {
    const d = createDemoSession(NOW);
    expect(d.add("   ").participants).toHaveLength(6);
  });

  it("removes a participant by id", () => {
    const d = createDemoSession(NOW);
    const pid = byName(d.snapshot(), "Wei Zhang").id;
    expect(names(d.remove(pid))).not.toContain("Wei Zhang");
  });

  it("trims the prompt on set", () => {
    const d = createDemoSession(NOW);
    expect(d.setPrompt("  Pets?  ").prompt).toBe("Pets?");
  });
});

describe("setOrder", () => {
  it("keeps the host pinned to the front even if asked otherwise", () => {
    const d = createDemoSession(NOW);
    const reversed = [...ids(d.snapshot())].reverse(); // host would land last
    expect(d.setOrder(reversed).participants[0].name).toBe("Maya Chen");
  });

  it("drops unknown ids and appends any omitted ones", () => {
    const d = createDemoSession(NOW);
    const original = ids(d.snapshot());
    const out = d.setOrder([original[2], "ghost"]);
    expect(out.participants[0].name).toBe("Maya Chen"); // host still pinned
    expect(ids(out).slice().sort()).toEqual(original.slice().sort()); // same set
  });
});

describe("randomize", () => {
  it("keeps introduced people in their slots and the host pinned", () => {
    const d = createDemoSession(NOW, noShuffle);
    const before = d.snapshot();
    const after = d.randomize();
    expect(after.participants[0].name).toBe("Maya Chen");
    // Introduced rows (Tom Becker here) must not move out of their backend slot.
    const slot = (snap, n) => snap.participants.findIndex((p) => p.name === n);
    expect(slot(after, "Tom Becker")).toBe(slot(before, "Tom Becker"));
  });

  it("preserves the full membership set", () => {
    const d = createDemoSession(NOW, noShuffle);
    const before = names(d.snapshot()).slice().sort();
    expect(names(d.randomize()).slice().sort()).toEqual(before);
  });
});
