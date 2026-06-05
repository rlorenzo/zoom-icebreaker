import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

// Reuse the real markup so the integration tests render against the same DOM
// the browser sees (minus the module <script>, which we drive directly).
const here = path.dirname(fileURLToPath(import.meta.url));
const indexHtml = fs.readFileSync(path.resolve(here, "../index.html"), "utf8");
const BODY = indexHtml
  .match(/<body>([\s\S]*?)<\/body>/)[1]
  .replace(/<script[\s\S]*?<\/script>/g, "");

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

  fetchMock = vi.fn(() => Promise.resolve({ ok: true }));
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
  vi.stubGlobal(
    "IntersectionObserver",
    class {
      observe() {}
      unobserve() {}
      disconnect() {}
    },
  );
  vi.stubGlobal(
    "confirm",
    vi.fn(() => true),
  );
  window.matchMedia = vi.fn().mockReturnValue({ matches: false });
  // jsdom doesn't implement the Web Animations API used by playReorder().
  if (!Element.prototype.animate) Element.prototype.animate = () => ({});

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
  it("renders rows, stats and the coming-up callout", () => {
    app.render({
      startedAt: Date.now(),
      prompt: "Q?",
      participants: [P({ id: "h", name: "Ann", is_host: true }), P({ id: "b", name: "Bob" })],
    });
    expect(document.querySelectorAll("#roster .row")).toHaveLength(2);
    expect(document.getElementById("s-present").textContent).toBe("2");
    expect(document.getElementById("s-wait").textContent).toBe("2");
    expect(document.getElementById("s-done").textContent).toBe("0");
    expect(document.getElementById("calloutBox").textContent).toContain("Coming up");
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

  it("reorders via dragstart/dragover/drop and clears indicators on dragend", () => {
    seed();
    const rowB = document.querySelector('.row[data-pid="b"]');
    const rowC = document.querySelector('.row[data-pid="c"]');
    rowC.getBoundingClientRect = () => ({ top: 100, height: 40, bottom: 140 });

    rowB.dispatchEvent(dragEvent("dragstart"));
    rowC.dispatchEvent(dragEvent("dragover", { clientY: 130 })); // lower half -> drop-after
    expect(rowC.classList.contains("drop-after")).toBe(true);
    rowC.dispatchEvent(dragEvent("drop"));
    expect(postedUrls()).toContain("/api/order");

    rowB.dispatchEvent(dragEvent("dragend"));
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
