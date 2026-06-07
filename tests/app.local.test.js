import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { BODY, installDomStubs } from "./helpers.js";

// Integration tests for the BACKEND-LESS path: when /events is not an SSE stream
// (GitHub Pages, any static host), app.js falls back to the local engine. Actions
// must then take effect in the browser with no /api/* POST, and survive a reload
// via localStorage. The server-transport path is covered in app.test.js.
let fetchMock;

beforeEach(() => {
  vi.resetModules();
  document.body.innerHTML = BODY;
  localStorage.clear();

  // Probe answers with a plain page (not text/event-stream), so hasServer() is
  // false and the local engine is selected.
  fetchMock = vi.fn(() =>
    Promise.resolve({ ok: true, headers: { get: () => "text/html" }, body: { cancel() {} } }),
  );
  vi.stubGlobal("fetch", fetchMock);
  installDomStubs();
});

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

const postedUrls = () => fetchMock.mock.calls.map((c) => String(c[0]));
const addPerson = (name) => {
  const input = document.getElementById("addName");
  input.value = name;
  document
    .getElementById("addForm")
    .dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
};

describe("local (backend-less) mode", () => {
  it("starts on the empty state and never opens an SSE stream", async () => {
    const seen = [];
    vi.stubGlobal(
      "EventSource",
      class {
        constructor(url) {
          seen.push(url);
        }
      },
    );
    await import("../app.js");
    expect(document.querySelector("#roster .empty")).not.toBeNull();
    expect(seen).toHaveLength(0); // no server transport
    expect(postedUrls()).toEqual(["events"]); // only the probe
  });

  it("adds a participant locally with no /api POST", async () => {
    await import("../app.js");
    addPerson("Zoe");
    expect(document.querySelectorAll("#roster .row")).toHaveLength(1);
    expect(document.getElementById("s-present").textContent).toBe("1");
    expect(postedUrls().some((u) => u.includes("/api/"))).toBe(false);
  });

  it("marks introduced locally, moving the live counts", async () => {
    await import("../app.js");
    addPerson("Zoe");
    document.querySelector(".row:not(.introduced) .toggle").click();
    expect(document.getElementById("s-done").textContent).toBe("1");
  });

  it("resets back to the empty state", async () => {
    await import("../app.js");
    addPerson("Zoe");
    document.getElementById("resetBtn").click();
    expect(document.querySelectorAll("#roster .row")).toHaveLength(0);
  });

  it("persists the session across a reload", async () => {
    await import("../app.js");
    addPerson("Zoe");
    expect(localStorage.getItem("icebreaker.session.v1")).toContain("Zoe");

    // A reload: re-evaluate the module against the same localStorage.
    vi.resetModules();
    document.body.innerHTML = BODY;
    await import("../app.js");
    const rows = document.querySelectorAll("#roster .row");
    expect(rows).toHaveLength(1);
    expect(rows[0].querySelector(".who").textContent).toBe("Zoe");
  });
});
