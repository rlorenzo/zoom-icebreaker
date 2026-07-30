import { describe, expect, it } from "vitest";
import {
  assignPositions,
  calloutHtml,
  findUpNextPid,
  fmtTime,
  rowHtml,
  sortForDisplay,
} from "../roster.js";

// Factory for a participant with sensible defaults.
const P = (over = {}) => ({
  id: "p1",
  name: "Pat",
  is_host: false,
  present: true,
  introduced: false,
  joinTime: Date.UTC(2020, 0, 1, 9, 5),
  ...over,
});

describe("fmtTime", () => {
  it("formats a timestamp as a non-empty time string", () => {
    expect(typeof fmtTime(Date.now())).toBe("string");
    expect(fmtTime(Date.UTC(2020, 0, 1, 9, 5))).toMatch(/\d/);
  });
});

describe("sortForDisplay", () => {
  it("orders host-first, then waiting, then introduced, then left (stable)", () => {
    const host = P({ id: "h", is_host: true });
    const waiting = P({ id: "w" });
    const introduced = P({ id: "i", introduced: true });
    const left = P({ id: "l", present: false });
    const out = sortForDisplay([left, introduced, waiting, host]);
    expect(out.map((p) => p.id)).toEqual(["h", "w", "i", "l"]);
  });

  it("does not mutate the input array", () => {
    const arr = [P({ id: "a" }), P({ id: "b", is_host: true })];
    const snapshot = [...arr];
    sortForDisplay(arr);
    expect(arr).toEqual(snapshot);
  });
});

describe("findUpNextPid", () => {
  it("returns the first present, not-introduced id", () => {
    expect(findUpNextPid([P({ id: "a", introduced: true }), P({ id: "b" })])).toBe("b");
  });

  it("returns null when everyone is introduced or absent", () => {
    expect(findUpNextPid([P({ introduced: true }), P({ present: false })])).toBeNull();
  });
});

describe("assignPositions", () => {
  it("numbers present participants 1..n in backend order, skipping absent", () => {
    const m = assignPositions([P({ id: "a" }), P({ id: "x", present: false }), P({ id: "b" })]);
    expect(m.get("a")).toBe(1);
    expect(m.get("b")).toBe(2);
    expect(m.has("x")).toBe(false);
  });
});

describe("calloutHtml", () => {
  it("is empty when no one is present", () => {
    expect(calloutHtml([], [])).toBe("");
  });

  it("announces completion when present but none waiting", () => {
    expect(calloutHtml([P()], [])).toContain("Everyone has introduced");
  });

  it("is empty while anyone is still waiting (the roster shows who's next)", () => {
    expect(calloutHtml([P(), P({ name: "Ann" })], [P({ name: "Ann" })])).toBe("");
    expect(calloutHtml([], [P({ name: "Ann" }), P({ name: "Bo" })])).toBe("");
  });
});

describe("rowHtml", () => {
  const ctx = (over = {}) => ({
    positionByPid: new Map([["p1", 1]]),
    upNextPid: "p1",
    upNextChanged: false,
    prevIntroduced: new Set(),
    ...over,
  });

  it("renders a waiting non-host as reorderable with an up-next tag", () => {
    const html = rowHtml(P(), ctx());
    expect(html).toContain('data-pid="p1"');
    expect(html).toContain('draggable="true"');
    expect(html).toContain("up next");
    expect(html).toContain("up-next");
  });

  it("marks the host and omits drag affordances and the up-next tag", () => {
    const html = rowHtml(P({ is_host: true }), ctx());
    expect(html).toContain("host-pill");
    expect(html).not.toContain('draggable="true"');
    expect(html).not.toContain("up next");
  });

  it("shows the introduced toggle state with a check label", () => {
    const html = rowHtml(P({ introduced: true }), ctx({ upNextPid: null }));
    expect(html).toContain("Introduced");
    expect(html).toContain("toggle on");
    expect(html).toContain("just-introduced");
  });

  it("renders a 'left' tag for absent participants", () => {
    const html = rowHtml(P({ present: false }), ctx({ upNextPid: null }));
    expect(html).toContain('class="tag">left');
  });

  it("adds just-cued when up-next has just changed", () => {
    expect(rowHtml(P(), ctx({ upNextChanged: true }))).toContain("just-cued");
  });

  it("escapes participant names (XSS guard)", () => {
    const html = rowHtml(P({ name: "<img src=x onerror=alert(1)>" }), ctx());
    expect(html).toContain("&lt;img");
    expect(html).not.toContain("<img");
  });

  it("shows a blank position when the participant has no number", () => {
    const html = rowHtml(P({ id: "ghost" }), ctx({ upNextPid: null }));
    expect(html).toContain('<div class="pos"></div>');
  });
});

describe("rowHtml accessibility", () => {
  const ctx = (over = {}) => ({
    positionByPid: new Map([["p1", 1]]),
    upNextPid: "p1",
    upNextChanged: false,
    prevIntroduced: new Set(),
    ...over,
  });

  it("renders every row as a native list item", () => {
    const html = rowHtml(P(), ctx()).trim();
    expect(html.startsWith("<li")).toBe(true);
    expect(html.endsWith("</li>")).toBe(true);
  });

  it("exposes the introduced state through aria-pressed", () => {
    expect(rowHtml(P(), ctx())).toContain('aria-pressed="false"');
    expect(rowHtml(P({ introduced: true }), ctx({ upNextPid: null }))).toContain(
      'aria-pressed="true"',
    );
  });

  it("describes the reorder affordance only where reordering is possible", () => {
    expect(rowHtml(P(), ctx())).toContain('aria-describedby="reorderHint"');
    // The host is pinned, so its row is not reorderable and gets no hint.
    expect(rowHtml(P({ is_host: true }), ctx({ upNextPid: null }))).not.toContain(
      "aria-describedby",
    );
  });
});
