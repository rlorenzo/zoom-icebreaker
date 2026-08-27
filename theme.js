// theme.js -- the theme preference, and the picker that sets it.
//
// Four skies over one system: every component reads the same token roles, so a
// theme is just a data-theme attribute on <html> selecting a palette block in
// styles.css. "sky" (Clear Sky) is the default and is expressed as NO
// attribute — the :root tokens — so the markup's resting state and the
// default theme can never disagree.
//
// The choice is a UI preference, not meeting data: it persists to
// localStorage (like the first-run flag, and unlike anything that implies
// meeting history) and a blocked localStorage degrades to "default theme
// every load", which is fine. index.html carries a tiny inline mirror of
// loadTheme() so a saved theme lands before first paint.
//
// No DOM is touched at import time (init() wires the picker), so the pure
// parts stay unit-testable — see tests/theme.test.js.

const THEME_KEY = "icebreaker.theme";
const DEFAULT_THEME = "sky";

export const THEMES = ["sky", "dawn", "dusk", "night"];

// Anything that isn't one of the four named skies — a corrupted write, a
// foreign page sharing this origin's storage, an old id from a future
// rename — falls back to the default rather than landing on <html> as an
// attribute no stylesheet answers to.
export const normalizeTheme = (value) => (THEMES.includes(value) ? value : DEFAULT_THEME);

export function loadTheme() {
  try {
    return normalizeTheme(localStorage.getItem(THEME_KEY));
  } catch {
    return DEFAULT_THEME;
  }
}

export function saveTheme(theme) {
  try {
    localStorage.setItem(THEME_KEY, normalizeTheme(theme));
  } catch {
    /* storage unavailable — the choice just won't survive a reload */
  }
}

export function applyTheme(theme, root = document.documentElement) {
  const t = normalizeTheme(theme);
  if (t === DEFAULT_THEME) delete root.dataset.theme;
  else root.dataset.theme = t;
}

// Wire the picker. The chips are native radio inputs, so the browser already
// owns the group semantics — one tab stop, arrow keys, click-to-check — and
// this module only has two jobs: apply + persist a change, and keep the
// checked input honest when the theme changes from elsewhere. "Elsewhere"
// includes another tab of this origin — the host often opens one tab to
// screen-share and one to drive, and the two skies should not disagree (same
// rationale as engine.js's storage listener; the storage event only fires in
// the tabs that did NOT write, so no loop).
export function initTheme(bar = document.getElementById("themeBar")) {
  if (!bar) return () => {};
  const radios = [...bar.querySelectorAll('input[name="theme"]')];

  const sync = (theme) => {
    for (const radio of radios) radio.checked = radio.value === theme;
  };

  bar.addEventListener("change", (e) => {
    if (!e.target.matches('input[name="theme"]')) return;
    const t = normalizeTheme(e.target.value);
    applyTheme(t);
    saveTheme(t);
    sync(t); // re-assert, in case the markup carried an unknown value
  });

  // Abortable so a caller (tests re-importing app.js under a shared jsdom
  // window, mainly) can tear the listener down instead of accumulating one
  // stale copy per module reset.
  const ac = new AbortController();
  window.addEventListener(
    "storage",
    (e) => {
      if (e.key !== THEME_KEY) return;
      const t = normalizeTheme(e.newValue);
      applyTheme(t);
      sync(t);
    },
    { signal: ac.signal },
  );

  // The head script already set the attribute pre-paint; this aligns the
  // picker's checked state with it (and re-asserts the attribute, which is a
  // no-op when they agree).
  const saved = loadTheme();
  applyTheme(saved);
  sync(saved);
  return () => ac.abort();
}
