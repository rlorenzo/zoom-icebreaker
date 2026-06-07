import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { vi } from "vitest";

// Shared setup for the jsdom integration suites (app.test.js, app.local.test.js)
// so the markup fixture and the jsdom shims live in one place.
const here = path.dirname(fileURLToPath(import.meta.url));
const indexHtml = fs.readFileSync(path.resolve(here, "../index.html"), "utf8");

// The page's <body> with the module <script> stripped, so tests render against
// the same DOM the browser sees while driving the module directly.
export const BODY = indexHtml
  .match(/<body>([\s\S]*?)<\/body>/)[1]
  .replace(/<script[\s\S]*?<\/script>/g, "");

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
  window.matchMedia = vi.fn().mockReturnValue({ matches: false });
  // jsdom doesn't implement the Web Animations API used by playReorder().
  if (!Element.prototype.animate) Element.prototype.animate = () => ({});
}
