import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { BODY, installDomStubs } from "./helpers.js";

const P = (over = {}) => ({
  id: "p1",
  name: "Pat",
  is_host: false,
  present: true,
  introduced: false,
  joinTime: Date.now(),
  ...over,
});

const trio = () => [
  P({ id: "h", name: "Ann", is_host: true }),
  P({ id: "b", name: "Bob" }),
  P({ id: "c", name: "Cy" }),
];

let app;
let fetchMock;
let esInstances;

beforeEach(async () => {
  vi.resetModules();
  document.body.innerHTML = BODY;
  // jsdom shares localStorage across tests; clear it so the first-run empty
  // state is deterministic (the demo "seen" flag lives there).
  localStorage.clear();

  // The /events probe decides the transport: an event-stream response selects
  // the server transport these tests exercise (POST to /api/*). Everything else
  // resolves as a plain ok for the action POSTs.
  fetchMock = vi.fn((url) =>
    String(url).includes("events")
      ? Promise.resolve({
          ok: true,
          headers: { get: () => "text/event-stream" },
          body: { cancel() {} },
        })
      : Promise.resolve({ ok: true }),
  );
  vi.stubGlobal("fetch", fetchMock);

  esInstances = [];
  vi.stubGlobal(
    "EventSource",
    class {
      constructor(url) {
        this.url = url;
        this.onmessage = null;
        this.onerror = null;
        this.onopen = null;
        esInstances.push(this);
      }
      close() {}
    },
  );
  installDomStubs();

  // Importing runs init() against the prepared DOM (auto-bootstrap at module end).
  app = await import("../app.js");
});

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

const dragEvent = (type, extra = {}) => {
  const e = new Event(type, { bubbles: true, cancelable: true });
  e.dataTransfer = { effectAllowed: "", setData: vi.fn(), getData: vi.fn() };
  return Object.assign(e, extra);
};

const postedUrls = () => fetchMock.mock.calls.map((c) => c[0]);

describe("render", () => {
  it("renders rows and stats, with the up-next cue in the roster", () => {
    app.render({
      startedAt: Date.now(),
      prompt: "Q?",
      participants: [P({ id: "h", name: "Ann", is_host: true }), P({ id: "b", name: "Bob" })],
    });
    expect(document.querySelectorAll("#roster .row")).toHaveLength(2);
    expect(document.getElementById("s-present").textContent).toBe("2");
    expect(document.getElementById("s-wait").textContent).toBe("2");
    expect(document.getElementById("s-done").textContent).toBe("0");
    // The "who's next" signal lives on the roster row now, not a separate callout.
    expect(document.querySelector("#roster .row.up-next")).not.toBeNull();
    expect(document.getElementById("calloutBox").textContent).toBe("");
  });

  it("shows the completion callout once everyone present has introduced", () => {
    app.render({
      startedAt: Date.now(),
      prompt: "Q?",
      participants: [P({ id: "h", name: "Ann", is_host: true, introduced: true })],
    });
    expect(document.getElementById("calloutBox").textContent).toContain("Everyone has introduced");
  });

  it("shows the empty state when there are no participants", () => {
    app.render({ startedAt: Date.now(), prompt: "", participants: [] });
    expect(document.querySelector("#roster .empty")).not.toBeNull();
    expect(document.getElementById("calloutBox").textContent).toBe("");
  });

  it("reflects the prompt into the textarea when it is not focused", () => {
    app.render({ startedAt: Date.now(), prompt: "Hello?", participants: [] });
    expect(document.getElementById("prompt").value).toBe("Hello?");
  });
});

describe("roster interactions", () => {
  const seed = () => app.render({ startedAt: Date.now(), prompt: "", participants: trio() });

  // Pick up `fromPid`'s row and hover it over `toPid`'s (whose rect is stubbed
  // to top 100 / height 40, so clientY < 120 means the upper half).
  const dragOver = (fromPid, toPid, clientY) => {
    const from = document.querySelector(`.row[data-pid="${fromPid}"]`);
    const to = document.querySelector(`.row[data-pid="${toPid}"]`);
    to.getBoundingClientRect = () => ({ top: 100, height: 40, bottom: 140 });
    from.dispatchEvent(dragEvent("dragstart"));
    to.dispatchEvent(dragEvent("dragover", { clientY }));
    return { from, to };
  };

  it("POSTs introduced when a toggle is clicked", () => {
    seed();
    document.querySelector('.toggle[data-pid="b"]').click();
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/participant/b/introduced",
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("POSTs remove when the remove button is clicked", () => {
    seed();
    document.querySelector('.x[data-pid="b"]').click();
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/participant/b/remove",
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("POSTs a new order on ArrowDown", () => {
    seed();
    const row = document.querySelector('.row[data-pid="b"]');
    row.focus();
    row.dispatchEvent(new KeyboardEvent("keydown", { key: "ArrowDown", bubbles: true }));
    expect(postedUrls()).toContain("/api/order");
  });

  it("ignores an ArrowUp that would cross the host boundary", () => {
    seed();
    const row = document.querySelector('.row[data-pid="b"]'); // first non-host
    row.focus();
    row.dispatchEvent(new KeyboardEvent("keydown", { key: "ArrowUp", bubbles: true }));
    expect(postedUrls()).not.toContain("/api/order");
  });

  it("ignores keyboard reorder for a participant who has left", () => {
    // b and c are both non-host; without the presence guard, reordering the
    // (absent) c up past b would be in-bounds and POST — the guard blocks it.
    app.render({
      startedAt: Date.now(),
      prompt: "",
      participants: [P({ id: "b", name: "Bob" }), P({ id: "c", name: "Cy", present: false })],
    });
    const row = document.querySelector('.row[data-pid="c"]');
    row.dispatchEvent(new KeyboardEvent("keydown", { key: "ArrowUp", bubbles: true }));
    expect(postedUrls()).not.toContain("/api/order");
  });

  it("ignores keyboard reorder into an introduced participant's slot", () => {
    // Bob is waiting; Cy has introduced and sorts below him. ArrowDown on Bob
    // is in-bounds but its only destination is the introduced row, which would
    // shuffle backend slots with no visible move — the guard blocks it.
    app.render({
      startedAt: Date.now(),
      prompt: "",
      participants: [
        P({ id: "h", name: "Ann", is_host: true }),
        P({ id: "b", name: "Bob" }),
        P({ id: "c", name: "Cy", introduced: true }),
      ],
    });
    const row = document.querySelector('.row[data-pid="b"]');
    row.focus();
    row.dispatchEvent(new KeyboardEvent("keydown", { key: "ArrowDown", bubbles: true }));
    expect(postedUrls()).not.toContain("/api/order");
  });

  it("keeps introduced participants' backend slots when reordering (sticky positions)", () => {
    // Backend order: Ann(host), Bob(introduced), Cy, Dan — display sinks Bob
    // to the bottom. Dragging Dan above Cy must not renumber Bob: the posted
    // order keeps him in slot 2 and only permutes the waiting rows.
    app.render({
      startedAt: Date.now(),
      prompt: "",
      participants: [
        P({ id: "h", name: "Ann", is_host: true }),
        P({ id: "b", name: "Bob", introduced: true }),
        P({ id: "c", name: "Cy" }),
        P({ id: "d", name: "Dan" }),
      ],
    });
    const { to } = dragOver("d", "c", 105); // upper half -> drop-before
    to.dispatchEvent(dragEvent("drop"));

    const call = fetchMock.mock.calls.find((c) => c[0] === "/api/order");
    expect(call).toBeTruthy();
    expect(JSON.parse(call[1].body).order).toEqual(["h", "b", "d", "c"]);
  });

  it("ignores a drag onto a participant who has left", () => {
    app.render({
      startedAt: Date.now(),
      prompt: "",
      participants: [P({ id: "b", name: "Bob" }), P({ id: "c", name: "Cy", present: false })],
    });
    const { to } = dragOver("b", "c", 130);
    expect(to.classList.contains("drop-after")).toBe(false);
    to.dispatchEvent(dragEvent("drop"));
    expect(postedUrls()).not.toContain("/api/order");
  });

  it("reorders via dragstart/dragover/drop and clears indicators on dragend", () => {
    seed();
    const { from, to } = dragOver("b", "c", 130); // lower half -> drop-after
    expect(to.classList.contains("drop-after")).toBe(true);
    to.dispatchEvent(dragEvent("drop"));
    expect(postedUrls()).toContain("/api/order");

    from.dispatchEvent(dragEvent("dragend"));
    expect(document.querySelector(".drop-after")).toBeNull();
  });
});

describe("prompt + footer", () => {
  it("POSTs the prompt on blur when it changed", () => {
    const prompt = document.getElementById("prompt");
    prompt.value = "Brand new prompt";
    prompt.dispatchEvent(new FocusEvent("blur"));
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/prompt",
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("does not POST the prompt on blur when unchanged", () => {
    const prompt = document.getElementById("prompt");
    prompt.value = "";
    prompt.dispatchEvent(new FocusEvent("blur"));
    expect(postedUrls()).not.toContain("/api/prompt");
  });

  it("adds a participant on form submit and clears the field", () => {
    const input = document.getElementById("addName");
    input.value = "Zoe";
    document
      .getElementById("addForm")
      .dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/participant",
      expect.objectContaining({ method: "POST" }),
    );
    expect(input.value).toBe("");
  });

  it("randomizes and resets via the footer buttons", () => {
    document.getElementById("randomBtn").click();
    document.getElementById("resetBtn").click();
    const urls = postedUrls();
    expect(urls).toContain("/api/randomize");
    expect(urls).toContain("/api/reset");
  });
});

describe("demo mode", () => {
  const empty = () => app.render({ startedAt: Date.now(), prompt: "", participants: [] });

  it("offers the demo on the first-run empty state", () => {
    empty();
    const cta = document.querySelector('#roster .empty.first-run [data-act="demo"]');
    expect(cta).not.toBeNull();
    expect(cta.textContent).toMatch(/demo/i);
  });

  it("shows the lighter empty state once first run has been seen", () => {
    localStorage.setItem("icebreaker.firstrun.seen", "1");
    empty();
    expect(document.querySelector("#roster .empty.first-run")).toBeNull();
    expect(document.querySelector('#roster .text-link[data-act="demo"]')).not.toBeNull();
  });

  it("enters demo: reveals the bar and seeds the sample roster", () => {
    empty();
    document.querySelector('[data-act="demo"]').click();
    expect(document.getElementById("demoBar").hidden).toBe(false);
    expect(document.querySelectorAll("#roster .row")).toHaveLength(6);
    expect(document.getElementById("s-done").textContent).toBe("2");
  });

  it("applies actions locally while in demo (DOM updates without an SSE echo)", () => {
    // Live, a toggle only POSTs and waits for the server echo — the count would
    // not move synchronously. In demo it changes immediately, which is the proof
    // the action was applied locally.
    empty();
    document.querySelector('[data-act="demo"]').click();
    document.querySelector(".row:not(.introduced) .toggle").click();
    expect(document.getElementById("s-done").textContent).toBe("3");
  });

  it("exits demo back to a clean slate and hides the bar", () => {
    empty();
    document.querySelector('[data-act="demo"]').click();
    document.querySelector('[data-act="exit-demo"]').click();
    expect(document.getElementById("demoBar").hidden).toBe(true);
    expect(document.querySelectorAll("#roster .row")).toHaveLength(0);
    expect(document.querySelector("#roster .empty")).not.toBeNull();
  });
});

describe("live stream", () => {
  it("renders on an EventSource message", () => {
    esInstances[0].onmessage({
      data: JSON.stringify({
        startedAt: Date.now(),
        prompt: "",
        participants: [P({ id: "b", name: "Bob" })],
      }),
    });
    expect(document.querySelectorAll("#roster .row")).toHaveLength(1);
  });

  it("updates the live indicator on error and open", () => {
    esInstances[0].onerror();
    expect(document.getElementById("live").textContent).toBe("reconnecting");
    esInstances[0].onopen();
    expect(document.getElementById("live").textContent).toBe("live");
  });
});

// Every render replaces the roster subtree. These cover what that used to cost:
// keyboard focus, and a live region that re-read every name on every frame.
describe("accessibility of dynamic updates", () => {
  const seed = () => app.render({ startedAt: Date.now(), prompt: "", participants: trio() });
  const renderWith = (participants) =>
    app.render({ startedAt: Date.now(), prompt: "", participants });
  const introduce = (pid) => trio().map((p) => (p.id === pid ? { ...p, introduced: true } : p));

  it("keeps focus on the same person when an unrelated re-render lands", () => {
    seed();
    document.querySelector('.row[data-pid="b"]').focus();
    // A frame the host did not initiate — the Zoom poller adding someone.
    renderWith([...trio(), P({ id: "d", name: "Dee" })]);
    expect(document.activeElement.closest(".row").dataset.pid).toBe("b");
  });

  it("returns focus to the same control, not merely the same row", () => {
    seed();
    document.querySelector('.toggle[data-pid="c"]').focus();
    renderWith(trio());
    expect(document.activeElement.dataset.act).toBe("toggle");
    expect(document.activeElement.dataset.pid).toBe("c");
  });

  it("falls back to the toggle when the focused row leaves the tab order", () => {
    seed();
    document.querySelector('.row[data-pid="b"]').focus();
    renderWith(introduce("b")); // introduced rows are no longer reorderable
    expect(document.activeElement.closest(".row").dataset.pid).toBe("b");
    expect(document.activeElement.className).toContain("toggle");
  });

  it("leaves focus alone when it was never inside the roster", () => {
    seed();
    document.getElementById("addName").focus();
    renderWith(trio());
    expect(document.activeElement.id).toBe("addName");
  });

  it("drops focus quietly when the focused person is gone", () => {
    seed();
    document.querySelector('.row[data-pid="b"]').focus();
    renderWith(trio().filter((p) => p.id !== "b"));
    expect(document.activeElement).toBe(document.body);
  });

  it("ignores focus that is inside the roster but on no one", () => {
    // The empty state puts a button inside the roster that belongs to no row.
    renderWith([]);
    document.querySelector('#roster [data-act="demo"]').focus();
    renderWith([]);
    expect(document.activeElement).toBe(document.body);
  });

  it("points each row's reorder hint at real text on the page", () => {
    seed();
    const hintId = document.querySelector('.row[data-pid="b"]').getAttribute("aria-describedby");
    expect(document.getElementById(hintId)?.textContent).toMatch(/arrow key/i);
  });

  it("announces only what changed", () => {
    seed();
    renderWith(introduce("b"));
    expect(document.getElementById("srStatus").textContent).toBe("Bob introduced. 2 still to go.");
  });

  it("does not make the roster or the counts live regions", () => {
    seed();
    const roster = document.getElementById("roster");
    expect(roster.getAttribute("aria-live")).toBeNull();
    expect(roster.tagName).toBe("UL");
    expect(roster.querySelectorAll(":scope > li.row")).toHaveLength(3);
    expect(document.querySelector(".stats").getAttribute("aria-live")).toBeNull();
  });
});

describe("describeChange", () => {
  const A = P({ id: "a", name: "Ann" });
  const B = P({ id: "b", name: "Bob" });

  it("names a newly introduced person and what is left", () => {
    expect(app.describeChange([A, B], [A, { ...B, introduced: true }])).toBe(
      "Bob introduced. 1 still to go.",
    );
  });

  it("reports a person unmarked by mistake", () => {
    expect(app.describeChange([A, { ...B, introduced: true }], [A, B])).toBe(
      "Bob marked not introduced. 2 still to go.",
    );
  });

  it("names a single joiner and counts a crowd", () => {
    expect(app.describeChange([A], [A, B])).toBe("Bob joined.");
    expect(app.describeChange([A], [A, B, P({ id: "c", name: "Cy" })])).toBe("2 people joined.");
  });

  it("reports removals", () => {
    expect(app.describeChange([A, B], [A])).toBe("Bob removed.");
    expect(app.describeChange([A, B], [])).toBe("2 people removed.");
  });

  it("announces a toggle on someone who has already left the meeting", () => {
    const gone = { ...B, present: false };
    expect(app.describeChange([A, gone], [A, { ...gone, introduced: true }])).toBe(
      "Bob introduced. 1 still to go.",
    );
  });

  it("reads a wholesale roster swap as joins, not as a toggle nobody made", () => {
    // Entering the demo replaces the roster with a sample where people are
    // already introduced; announcing one of them as "just introduced" would
    // describe an action the host never took.
    expect(app.describeChange([], [{ ...A, introduced: true }, B])).toBe("2 people joined.");
  });

  it("stays silent when nothing material changed", () => {
    expect(app.describeChange([A, B], [A, B])).toBe("");
    expect(app.describeChange([A, B], [B, A])).toBe("");
  });
});
