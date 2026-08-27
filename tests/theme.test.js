import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { applyTheme, initTheme, loadTheme, normalizeTheme, saveTheme, THEMES } from "../theme.js";
import { BODY } from "./helpers.js";

const THEME_KEY = "icebreaker.theme";

beforeEach(() => {
  document.body.innerHTML = BODY;
  document.documentElement.removeAttribute("data-theme");
  localStorage.clear();
});

describe("normalizeTheme", () => {
  it("passes each named theme through", () => {
    for (const t of THEMES) expect(normalizeTheme(t)).toBe(t);
  });

  it("falls back to the default for anything else", () => {
    expect(normalizeTheme("neon")).toBe("sky");
    expect(normalizeTheme(null)).toBe("sky");
    expect(normalizeTheme(undefined)).toBe("sky");
    expect(normalizeTheme(42)).toBe("sky");
  });
});

describe("load/save", () => {
  it("round-trips a choice through localStorage", () => {
    saveTheme("night");
    expect(loadTheme()).toBe("night");
    expect(localStorage.getItem(THEME_KEY)).toBe("night");
  });

  it("normalizes a foreign stored value on load", () => {
    localStorage.setItem(THEME_KEY, "hotdog-stand");
    expect(loadTheme()).toBe("sky");
  });

  it("degrades to the default when storage throws", () => {
    const spy = vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
      throw new Error("blocked");
    });
    expect(loadTheme()).toBe("sky");
    spy.mockRestore();
  });

  it("swallows a blocked write", () => {
    const spy = vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new Error("blocked");
    });
    expect(() => saveTheme("dawn")).not.toThrow();
    spy.mockRestore();
  });
});

describe("applyTheme", () => {
  it("sets data-theme for a non-default theme", () => {
    applyTheme("dusk");
    expect(document.documentElement.dataset.theme).toBe("dusk");
  });

  it("removes the attribute for the default theme", () => {
    applyTheme("night");
    applyTheme("sky");
    expect(document.documentElement.hasAttribute("data-theme")).toBe(false);
  });

  it("never lands an unknown value on the root element", () => {
    applyTheme("night");
    applyTheme("hotdog-stand");
    expect(document.documentElement.hasAttribute("data-theme")).toBe(false);
  });
});

describe("initTheme picker", () => {
  const radio = (t) => document.querySelector(`input[name="theme"][value="${t}"]`);
  const checked = () =>
    [...document.querySelectorAll('input[name="theme"]')]
      .filter((r) => r.checked)
      .map((r) => r.value);

  it("checks the saved theme's radio on init", () => {
    localStorage.setItem(THEME_KEY, "dusk");
    initTheme();
    expect(checked()).toEqual(["dusk"]);
    expect(document.documentElement.dataset.theme).toBe("dusk");
  });

  it("applies and persists on change", () => {
    initTheme();
    radio("night").click(); // checks the radio and fires change, like a user
    expect(document.documentElement.dataset.theme).toBe("night");
    expect(localStorage.getItem(THEME_KEY)).toBe("night");
    expect(checked()).toEqual(["night"]);
  });

  it("choosing the default clears the attribute", () => {
    localStorage.setItem(THEME_KEY, "dawn");
    initTheme();
    radio("sky").click();
    expect(document.documentElement.hasAttribute("data-theme")).toBe(false);
    expect(localStorage.getItem(THEME_KEY)).toBe("sky");
  });

  it("normalizes a foreign value arriving through the change event", () => {
    initTheme();
    const rogue = radio("night");
    rogue.value = "hotdog-stand"; // a tampered DOM must not land on <html>
    rogue.click();
    expect(document.documentElement.hasAttribute("data-theme")).toBe(false);
    expect(localStorage.getItem(THEME_KEY)).toBe("sky");
  });

  it("adopts a change written by another tab", () => {
    initTheme();
    window.dispatchEvent(new StorageEvent("storage", { key: THEME_KEY, newValue: "dusk" }));
    expect(document.documentElement.dataset.theme).toBe("dusk");
    expect(checked()).toEqual(["dusk"]);
  });

  it("ignores storage events for other keys", () => {
    initTheme();
    window.dispatchEvent(new StorageEvent("storage", { key: "other", newValue: "night" }));
    expect(document.documentElement.hasAttribute("data-theme")).toBe(false);
  });

  it("does nothing when the bar is absent", () => {
    document.body.innerHTML = "";
    expect(() => initTheme()).not.toThrow();
  });
});

describe("index.html integration", () => {
  const here = path.dirname(fileURLToPath(import.meta.url));
  const indexHtml = fs.readFileSync(path.resolve(here, "../index.html"), "utf8");
  // A real parse, not a regex over markup (CodeQL js/bad-tag-filter — a
  // regex misses case/attribute variants of the tag). Scripts are inert in
  // DOMParser output, so reading the inline one is safe.
  const doc = new DOMParser().parseFromString(indexHtml, "text/html");

  it("pre-paint whitelist covers every non-default theme", () => {
    // index.html's inline head script mirrors THEMES so a saved theme lands
    // before first paint. It cannot import the module (it must run inline and
    // synchronously), so this guards the duplicate list against drift: a
    // theme added to theme.js but not to the inline script would silently
    // reintroduce the default-flash the script exists to prevent.
    const script = doc.querySelector("script:not([src])")?.textContent ?? "";
    for (const t of THEMES.filter((t) => t !== "sky")) {
      expect(script, `inline whitelist is missing "${t}"`).toContain(`"${t}"`);
    }
    // ...and nothing the module no longer knows about, so a rename or a
    // removal cannot leave a dead id landing on <html> before paint.
    const inlineIds = [...script.matchAll(/savedTheme === "([^"]+)"/g)].map(([, id]) => id);
    // Guard the guard: if the inline script is ever rewritten in another
    // shape, fail here rather than passing an empty loop.
    expect(inlineIds, "could not parse the inline whitelist").not.toHaveLength(0);
    for (const id of inlineIds) {
      expect(THEMES, `inline whitelist has stale id "${id}"`).toContain(id);
    }
  });

  it("ships one native radio per theme, with the default checked", () => {
    const radios = [...doc.querySelectorAll('input[name="theme"]')];
    expect(radios.map((r) => r.value)).toEqual(THEMES);
    expect(radios.every((r) => r.type === "radio")).toBe(true);
    expect(radios.filter((r) => r.hasAttribute("checked")).map((r) => r.value)).toEqual(["sky"]);
  });
});
