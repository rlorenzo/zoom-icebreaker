import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { vi } from "vitest";

// Shared setup for the jsdom integration suites (app.test.js, app.local.test.js)
// so the markup fixture and the jsdom shims live in one place.
const here = path.dirname(fileURLToPath(import.meta.url));
const indexHtml = fs.readFileSync(path.resolve(here, "../index.html"), "utf8");

// The page's <body> with the module <script> removed, so tests render against
// the same DOM the browser sees while driving the module directly. Parsed via
// the DOM (the suites run in jsdom) rather than regex, so script removal is the
// real thing — no incomplete-sanitization or catastrophic-backtracking traps.
function bodyWithoutScripts(html) {
  const doc = new DOMParser().parseFromString(html, "text/html");
  for (const s of doc.body.querySelectorAll("script")) s.remove();
  return doc.body.innerHTML;
}

export const BODY = bodyWithoutScripts(indexHtml);

// Stubs for the browser APIs jsdom doesn't implement that both suites rely on.
export function installDomStubs() {
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
  // Stub via vi.stubGlobal (not a direct window assignment) so vi.unstubAllGlobals()
  // restores it between suites. app.js only reads .matches.
  vi.stubGlobal(
    "matchMedia",
    vi.fn(() => ({ matches: false })),
  );
  // jsdom doesn't implement the Web Animations API used by playReorder().
  if (!Element.prototype.animate) Element.prototype.animate = () => ({});
}
