---
name: Zoom Icebreaker Tracker
description: A per-meeting utility that shows a whole room who has and hasn't introduced themselves yet.
colors:
  ground: "#f4f9fd"
  card: "#ffffff"
  surface: "#e3eef7"
  hairline: "#c9dcea"
  soft-line: "#9ec1d9"
  hint-ink: "#5b7a8c"
  muted-ink: "#44616f"
  dim-ink: "#1e3e4f"
  ink: "#002033"
  field: "#005581"
  field-hover: "#0069a0"
  on-deep: "#ffffff"
  on-deep-dim: "rgba(255, 255, 255, 0.35)"
  bright-blue: "#1295d8"
  field-text: "#9adcf9"
  baton: "#ffb511"
  baton-bright: "#ffd200"
  baton-wash: "#fff3ce"
  baton-ink: "#8a5b00"
  accent-ink: "#005581"
  on-gold: "#002033"
  pin-shadow: "rgba(0, 32, 51, 0.18)"
typography:
  display:
    fontFamily: "Atkinson Hyperlegible Next, system-ui, sans-serif"
    fontSize: "clamp(2rem, 3.4vw, 2.75rem)"
    fontWeight: 700
    lineHeight: 1.05
    letterSpacing: "-0.015em"
  headline:
    fontFamily: "Atkinson Hyperlegible Next, system-ui, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "-0.01em"
  title:
    fontFamily: "Atkinson Hyperlegible Next, system-ui, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 500
    lineHeight: 1.5
    letterSpacing: "0"
  body:
    fontFamily: "Atkinson Hyperlegible Next, system-ui, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "0"
  caption:
    fontFamily: "Atkinson Hyperlegible Next, system-ui, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "0"
  label:
    fontFamily: "Atkinson Hyperlegible Next, system-ui, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 500
    lineHeight: 1.5
    letterSpacing: "0.04em"
  label-strong:
    fontFamily: "Atkinson Hyperlegible Next, system-ui, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 600
    lineHeight: 1.5
    letterSpacing: "0.04em"
  label-loud:
    fontFamily: "Atkinson Hyperlegible Next, system-ui, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 700
    lineHeight: 1.5
    letterSpacing: "0.05em"
  numeric:
    fontFamily: "Atkinson Hyperlegible Mono, ui-monospace, monospace"
    fontSize: "2.25rem"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "-0.01em"
    fontFeature: "'tnum' 1"
  numeric-compact:
    fontFamily: "Atkinson Hyperlegible Mono, ui-monospace, monospace"
    fontSize: "1.75rem"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "-0.01em"
    fontFeature: "'tnum' 1"
  numeric-row:
    fontFamily: "Atkinson Hyperlegible Mono, ui-monospace, monospace"
    fontSize: "1.125rem"
    fontWeight: 500
    lineHeight: 1
    fontFeature: "'tnum' 1"
  numeric-emphasis:
    fontFamily: "Atkinson Hyperlegible Mono, ui-monospace, monospace"
    fontSize: "1.5rem"
    fontWeight: 700
    lineHeight: 1
    fontFeature: "'tnum' 1"
  numeric-caption:
    fontFamily: "Atkinson Hyperlegible Mono, ui-monospace, monospace"
    fontSize: "0.8125rem"
    fontWeight: 400
    lineHeight: 1.5
    fontFeature: "'tnum' 1"
rounded:
  xs: "6px"
  sm: "10px"
  pill: "999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "20px"
  xxl: "24px"
  gutter: "32px"
  section: "48px"
components:
  masthead-band:
    backgroundColor: "{colors.field}"
    textColor: "{colors.on-deep}"
    padding: "22px 0 18px"
  prompt-input:
    backgroundColor: "transparent"
    textColor: "{colors.on-deep}"
    typography: "{typography.display}"
    padding: "0"
  button-primary:
    backgroundColor: "{colors.field}"
    textColor: "{colors.on-deep}"
    typography: "{typography.label-strong}"
    rounded: "{rounded.xs}"
    padding: "10px 16px"
  button-primary-hover:
    backgroundColor: "{colors.field-hover}"
    textColor: "{colors.on-deep}"
  button-ghost:
    backgroundColor: "{colors.card}"
    textColor: "{colors.dim-ink}"
    typography: "{typography.label-strong}"
    rounded: "{rounded.xs}"
    padding: "10px 16px"
  button-ghost-hover:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
  toggle-default:
    backgroundColor: "{colors.card}"
    textColor: "{colors.muted-ink}"
    typography: "{typography.label}"
    rounded: "{rounded.xs}"
    padding: "8px 14px"
  toggle-hover:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
  toggle-on:
    backgroundColor: "{colors.field}"
    textColor: "{colors.on-deep}"
    typography: "{typography.label}"
    rounded: "{rounded.xs}"
    padding: "8px 14px"
  toggle-on-hover:
    backgroundColor: "{colors.field-hover}"
    textColor: "{colors.on-deep}"
  roster-row:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: "14px 18px"
  roster-row-introduced:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.muted-ink}"
  roster-row-up-next:
    backgroundColor: "{colors.baton-wash}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: "17px"
  roster-row-left:
    backgroundColor: "{colors.card}"
    textColor: "{colors.dim-ink}"
  up-next-tag:
    backgroundColor: "{colors.baton}"
    textColor: "{colors.on-gold}"
    typography: "{typography.label-loud}"
    rounded: "{rounded.xs}"
    padding: "3px 9px"
  host-pill:
    textColor: "{colors.accent-ink}"
    typography: "{typography.label}"
    padding: "4px 6px"
  tag-left:
    backgroundColor: "{colors.card}"
    textColor: "{colors.muted-ink}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "2px 8px"
  count-band:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.accent-ink}"
    rounded: "{rounded.sm}"
    padding: "14px 20px"
  input-field:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
    rounded: "{rounded.xs}"
    padding: "10px 14px"
  callout:
    backgroundColor: "{colors.baton-wash}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: "14px 20px"
  demo-bar:
    backgroundColor: "{colors.baton-wash}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: "12px 16px"
  empty-state:
    backgroundColor: "{colors.card}"
    textColor: "{colors.muted-ink}"
    rounded: "{rounded.sm}"
    padding: "48px 24px"
  empty-state-first-run:
    backgroundColor: "{colors.card}"
    textColor: "{colors.dim-ink}"
    rounded: "{rounded.sm}"
    padding: "48px 32px"
  text-link:
    textColor: "{colors.accent-ink}"
    typography: "{typography.caption}"
    padding: "4px"
  live-dot:
    backgroundColor: "{colors.baton}"
    rounded: "{rounded.pill}"
    size: "7px"
  theme-chip:
    backgroundColor: "transparent"
    textColor: "{colors.muted-ink}"
    typography: "{typography.label}"
    rounded: "{rounded.xs}"
    padding: "6px 10px"
  theme-chip-hover:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
  theme-chip-selected:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.xs}"
    padding: "6px 10px"
  theme-swatch:
    rounded: "{rounded.pill}"
    size: "14px"
---

# Design System: Zoom Icebreaker Tracker

## Overview

### Creative North Star: "Clear Sky, Gold Baton"

A round-robin tracker rebuilt as a clear California day. One deep-blue masthead — the band that holds the live indicator and the icebreaker prompt — bleeds full-width across the top of the page and owns every primary control below it. Gold appears nowhere as decoration; it exists for exactly one job, marking whoever holds the baton right now: the up-next row, the completion callout, the demo-mode bar, text selection. Everything else on the page is sky-tinted blue-on-white, calm enough to sit in the corner of a meeting without competing with the conversation in the room.

The two nouns in the north star are now the two token names. What was `--deep-blue` is `--field` — the committed structural fill — and what was `--gold` is `--baton` — the mark that moves. The rename happened when the world grew from one sky into four (Clear Sky, Dawn, Golden Hour, After Dark), because at dawn the field is plum and the baton is rose: the hue is a theme's business, the role is the system's. Everything below describes roles first and Clear Sky's values second.

This system explicitly retires two prior worlds rather than blending with either: the beige-ledger warm-paper system it replaced (clay accent, paper neutrals, no blue at all), and the navy-dashboard reflex the category defaults to. Neither survives in any token here. The palette is airy and blue rather than warm and paper-toned; the accent is a genuine gold rather than a clay terracotta; and for the first time the system gives its primary color — deep blue — a full-bleed structural role (the masthead) rather than confining it to small controls.

State is still never read through hue alone — which is what makes four skies affordable in the first place. Introduced vs. waiting pairs a fill change with an ink-color shift and a checkmark icon; up-next pairs a wash, a 2px accent-ink frame, and larger type, three signals at once. Motion carries exactly two curves: a glide that moves every piece of state, and a spring reserved for precisely two celebration animations. The design wants the room to find the next speaker in one glance and the host to never wonder what a color means.

### Key Characteristics

- Sky-tinted ground (`#f4f9fd`), never gray, never warm paper
- Full-bleed field-colored masthead owns the live indicator, the prompt, and every primary button
- The baton is reserved for happy moments only: up-next, completion, demo mode, selection — never a default UI color
- Four themes on one day-cycle arc (Clear Sky, Dawn, Golden Hour, After Dark), all re-lit from the same token roles — no theme adds a selector
- Single sans family (Atkinson Hyperlegible Next), single mono (Atkinson Hyperlegible Mono) for numerics, both self-hosted
- One functional shadow in the entire stylesheet (the pinned prompt band); everything else is flat
- Two motion curves: glide for all state, spring for exactly two one-shot celebrations
- No *forced* dark, ever — `:root` declares `color-scheme: only light` so browsers cannot force-invert whichever sky is chosen; dark exists only as the deliberately authored After Dark theme, whose block opts back in with `color-scheme: dark`
- Screen-share legibility at 720p is the design's first audience

### Motion

Two easing tokens, and they answer to different jobs rather than different durations:

- **`--glide`** (`cubic-bezier(0.22, 1, 0.36, 1)`, ease-out-quint): every state transition in the system — hover, focus, toggle, border, drop-indicator, the row-position glide, the completion gesture's three beats, the live-dot pulse, the callout's one-shot settle. `--t-fast` (140ms) and `--t-medium` (200ms) both ride this curve.
- **`--spring`** (`cubic-bezier(0.34, 1.56, 0.64, 1)`, back-out overshoot): reserved for exactly two animations, both tied to the baton arriving at the next person — `tag-pop` (420ms, the up-next tag) and `pos-cue` (520ms, the up-next position number). Nothing else in the stylesheet references `--spring`.

**The Glide-Everywhere, Spring-Once Rule.** If it isn't `tag-pop` or `pos-cue`, it moves on glide. A third animation reaching for spring needs a reason as strong as "the baton just landed here" — spring is a celebration signature, not a general-purpose bounce.

The app's one piece of JavaScript-driven motion — the FLIP roster-reorder glide in `app.js`'s `playReorder` — uses the identical values as `--t-medium`: `200ms`, `cubic-bezier(0.22, 1, 0.36, 1)`. The Web Animations API call bypasses the row's own CSS transition on purpose (it would otherwise fight the slide), but the curve and duration stay the same token in spirit, so a row settling into a new position reads as the same object moving as a hover state changing.

Named, sequenced animations beyond the two curve tokens: `pulse` (2.4s, infinite, the live dot's halo), `mark-flash` (3000ms, the just-introduced row's background settle), `draw-check` (1000ms, 800ms delay, the toggle's checkmark draw), `pos-cue` (520ms, 1800ms delay), `tag-pop` (420ms), and `callout-settle` (1200ms, the whole-room completion callout's one-shot arrival).

**The Sequenced-Not-Simultaneous Rule.** Marking someone introduced fires three beats in order, not at once: the row's background settles (`mark-flash`), then the checkmark draws (`draw-check`, 800ms in), then — only if a new person becomes up-next — their position number and tag animate in (`pos-cue` / `tag-pop`, both delayed to 1800ms). The 1800ms delay is scoped with `:has(.just-introduced)` so it only applies to a render that actually contains an introduction; up-next also changes on a plain reorder or a departure, and an unconditional delay would strand the cue 1.8s after a gesture that never happened.

**Reduced motion removes the movement, never the message.** Every state this system animates is also carried by fill, ink color, or an icon, so under `prefers-reduced-motion` durations collapse and the change lands instantly. Two details make that true rather than merely intended: **animation delays are zeroed along with durations** (`draw-check` waits 800ms before it starts — zeroing only the duration would leave the checkmark invisible for that entire window), and the checkmark path is explicitly forced to its drawn state (`stroke-dashoffset: 0`) rather than trusting an animation's fill mode to hold it there. The JS-driven FLIP reorder checks the same media query and skips the animation call outright rather than relying on CSS to neutralize it.

## Colors

An airy, blue-tinted palette built around a single structural role reversal: the field color is no longer a small accent, it is the surface the masthead and every primary control sit on. The baton is the accent, and it is licensed for happy moments only.

### Themes: Four Skies, One System

The palette ships as four themes on a day-cycle arc, selected by `data-theme` on `<html>` and picked from a quiet row of native radio chips below the footer: **Clear Sky** (the default — the `:root` palette below, expressed as *no* attribute, so the markup's resting state and the default theme cannot disagree), **Dawn** (`data-theme="dawn"`: lavender air, plum field `#6d2d80`, rose baton `#ff8fb2`), **Golden Hour** (`data-theme="dusk"`: warm cream, rust field `#9c4907`, amber baton `#ffa02e`), and **After Dark** (`data-theme="night"`: lifted blue-black ground `#0e1c26`, the field kept deep-blue, the baton kept gold, `color-scheme: dark`). A theme overrides color tokens only — structure, radii, type, spacing, and motion never change, and no theme introduces a selector of its own — and every themed value is contrast-checked against the same floors as the default (4.5:1 text, 3:1 large text and non-text), on the surface it actually sits on. The choice persists per browser in `localStorage` (`icebreaker.theme`, a UI preference, not meeting data) and is re-applied before first paint by an inline script in `index.html`; a blocked `localStorage` degrades to Clear Sky.

Three tokens exist because of the theme system — each one a role that only splits apart once the ground goes dark:

- **`--accent-ink`**: the field color's *other* job — text, borders, focus rings, and the caret on light surfaces (host pill, the three counts, the up-next frame, text links, the drop-indicator line, the remove glyph's hover, every focus ring except the prompt's). Aliases `--field` in all three light skies; After Dark rebinds it to a bright sky blue (`#6cc4f5`, 9:1 on the night ground) so the role stays legible while the filled masthead stays deep.
- **`--on-gold`**: ink sitting on the baton's own fill (the up-next tag, text selection). Aliases `--ink` in the light skies; After Dark rebinds it to the night ground itself (`#0e1c26`, 9.8:1 on gold), because its ink is near-white and would vanish there.
- **`--pin-shadow`**: the color of the pinned prompt band's one functional shadow — ink-tinted by day (`rgba(0, 32, 51, 0.18)`), true black at `0.55` after dark, where an ink-tinted drop reads as nothing at all.

After Dark also inverts one thing the light skies share, and it is worth stating plainly: **rows step *lighter* than the ground**, not darker. Ground `#0e1c26` → card `#16293a` → surface `#213950` climbs away from the canvas, where the light skies run card `#ffffff` *above* their ground and surface `#e3eef7` *below* it. The invariant is tonal *separation* between the three layers, not its direction. Two more night-specific decisions: the ground is a lifted blue-black rather than `#000`, because crushed blacks die in the screen-share pipeline; and `--baton-wash` becomes a warm ember (`#524012`) rather than a muddy brown, luminous enough that the celebration surface still reads as a happy moment instead of a caution strip.

**The Re-Lit, Never Re-Built Rule.** A theme may change what a role's color *is*, never what the role *does*. The baton stays the happy-moment mark in every sky (gold at midday and midnight, rose at dawn, amber at golden hour); the field stays the committed structural fill; state keeps all of its non-hue carriers in all four themes. A theme that needs a new selector rather than a new token value is not a theme.

### Theme Picker

A `.theme-bar` fieldset of **native radio inputs** between the footer and the sponsor link — a page preference, not a session control, so it sits below the working surface. Four chips, each a label wrapping an invisible radio stretched over the whole chip (the input is the real control: the browser owns the single tab stop, the arrow keys, and the checked state, all working before any script runs) and a 14px "horizon disc" swatch: the theme's field over its ground split on the horizon (a two-stop linear gradient), its baton as a 5px sun sitting on the line, in **pinned preview colors** keyed per chip so each disc shows its own sky whatever theme is currently active. The disc carries a soft-line border rather than a hairline, because its light half otherwise disappears into the page. Chips use the control vocabulary (6px radius, Label typography, `--t-fast` transitions), read their state through `:has()`, and are transparent-bordered at rest so only the chosen sky carries a visible edge: hover brings ink text and a hairline border, and the chip holding the checked input earns a card fill and an accent-ink border. theme.js listens only for `change`, applying and persisting the value; choices sync across tabs of the same origin via the `storage` event — the host often screen-shares one tab and drives from another, and the two skies must not disagree.

### Primary

- **Field — Deep Blue** (`--field`, `#005581`): the committed field, and the token the whole masthead device is named for. Fills the full-bleed masthead and sticky prompt band, every primary button, and the "on" state of the introduced toggle. Text on the field uses the **On Deep** token (`#ffffff`, 8:1 on Clear Sky's blue and re-checked in each sky — 6.2:1 on Golden Hour's rust) with **On Deep Dim** (`rgba(255,255,255,.35)`) for separators; white-on-field is a named role, never a literal.
- **Field Hover** (`--field-hover`, `#0069a0`): the pressed/hover step for every field-filled control — the primary button, the "on" toggle.
- **Accent Ink** (`--accent-ink`, `#005581` in Clear Sky): the field color's *other* job, the one that has to survive a dark ground. Everything the field does as a *mark on a light surface* rather than a fill: the up-next row's 2px frame, every focus ring except the prompt's, the drag-drop insertion line, the host pill, the three counts, text links, the body caret, the input's focused border, the remove glyph's hover. Aliases `--field` in the three light skies; After Dark rebinds it (`#6cc4f5`).

### Secondary

- **Baton — Gold** (`--baton`, `#ffb511`): the baton. Reserved for happy-moment surfaces and marks: the live dot (on the field, 4.5:1), the up-next tag's fill (with on-gold text at 9.5:1), and nothing that isn't a moment of attention.
- **Baton Bright** (`--baton-bright`, `#ffd200`): the prompt's placeholder text, its caret and its focus ring (5.5:1 on the field, clearing the 3:1 large-text floor), and the system's text-selection background. A step brighter than the plain baton because it has to read as an invitation against the masthead's deep field, not just as a mark.
- **Baton Wash** (`--baton-wash`, `#fff3ce`): the celebration surface — the up-next row's background, the completion callout, and the demo-mode bar. The one place besides the field where a whole surface (not just a mark) carries the accent. After Dark swaps it for a warm ember (`#524012`) — the one wash that is darker than its card, because a pale tint at night would blow a hole in the roster.
- **Baton Ink** (`--baton-ink`, `#8a5b00`): a small, deliberately scoped ink for baton-wash content that needs a border or a mark rather than the body's default ink color — currently the demo-mode bar's dot and border only. It is not the default text color on baton surfaces: the completion callout and the up-next row both set body text in plain `ink`, and the up-next row's border is accent-ink, not baton-ink. Reach for baton-ink specifically when the baton itself would be illegible on its own wash (a gold dot on a gold wash is 1.5:1), not as a general "text on gold" rule.
- **On Gold** (`--on-gold`, `#002033` in Clear Sky): the ink that sits *on* the baton's fill — the up-next tag's label, the text-selection foreground. Aliases `--ink` in the light skies; After Dark rebinds it to the night ground (`#0e1c26`) so the tag survives on an unchanged gold.
- **Bright Blue** (`--bright-blue`, `#1295d8`): declared in `:root` with a documented 3.1:1 non-text-floor intent ("live accents on white") but not yet consumed by any selector in the stylesheet, and not re-themed by any of the three theme blocks. Treat it as reserved, not load-bearing — do not point new work at it as though it already carries a role.

### Neutral

- **Ground** (`#f4f9fd`): the page canvas. Airy and faintly blue, never gray, never the old system's warm paper. Ink measures 15.8:1 on it.
- **Card** (`#ffffff`): true white, reserved for roster rows and every other content surface sitting on the sky-tinted ground — the crispness reads as "content" against the softer canvas. After Dark it is a lifted blue-slate (`#16293a`) *above* its ground rather than below it.
- **Surface** (`#e3eef7`): the second tonal layer. The count band, the introduced-row fill, the ghost button's hover. A step darker than ground, depth without elevation.
- **Hairline** (`#c9dcea`): default 1px borders. Border-only — 1.4:1, cannot carry text.
- **Soft Line** (`#9ec1d9`): emphasized borders — the host row's ring, the themed scrollbar. Border-only — 1.8:1.
- **Hint Ink** (`#5b7a8c`): the lightest text-capable ink, 4.3:1 on ground. Licensed for the remove-glyph icon (a graphical control, answering the 3:1 floor) and the regular input's border, which — unlike a button with its own label — needs to clear the 3:1 non-text floor on its own.
- **Muted Ink** (`#44616f`): secondary text — timestamps, labels, position numbers, the introduced-row's name color, the count band's labels. 5.6:1 on surface, 6.2:1 on ground.
- **Dim Ink** (`#1e3e4f`): tertiary text and ghost-button text.
- **Ink** (`#002033`): primary text, and the deep end of the sky palette. Never `#000` — and never `#fff` after dark either, where it is a near-white `#eef6fc` at 15.9:1.
- **Field Text** (`--field-text`, `#9adcf9`): meta text set directly on the masthead band (5.3:1) — the "Started ·· ago" line and its separator. Re-lit per sky (`#e5b8f0` at dawn, `#ffd9b0` at golden hour) because it is the one ink that never sits on the ground.

### Named Rules: Colors

**The Gold-Under-Ink Rule.** The baton never carries text on a light ground by itself. It is either a surface that ink sits on top of (the wash, the tag fill under `--on-gold`), or a mark against the field (the dot, the placeholder, the caret) — never the text color itself against a light background.

**The No-Hue-Alone Rule.** Introduced vs. waiting vs. up-next is never read through color alone. Introduced pairs a fill change (card → surface) with an ink-color shift (ink → muted-ink) and a checkmark icon on the toggle. Up-next pairs a wash, a 2px accent-ink frame, and larger type (name steps to 1.25rem/700, position number to `numeric-emphasis`) — three simultaneous signals, never the wash alone. This rule is what makes four skies affordable: a theme can re-light every hue on the page without touching a single one of these carriers.

**Blue Owns the Structure, Gold Owns the Moment.** The field is the default state of every primary control and the masthead band; it is present on the page at rest, in every session, whether or not anyone has been marked introduced yet. The baton only ever appears in response to something happening — someone becomes up next, everyone finishes, a sample session is loaded. If a new element needs a color and nothing has happened yet, reach for the field, accent-ink, or a neutral, never the baton. (The rule keeps its Clear Sky name because Clear Sky is the default; at dawn read it as "plum owns the structure, rose owns the moment.")

**The Three-Ink Floor Rule.** Text answers to exactly three inks depending on role: **ink** and **dim-ink** anywhere, **muted-ink** for secondary text, and **hint-ink** only for a graphical control glyph or where the 3:1 (not 4.5:1) floor applies. Hairline and soft-line are borders only.

## Typography

**Display Font:** Atkinson Hyperlegible Next (with system-ui, sans-serif fallback)
**Body Font:** Atkinson Hyperlegible Next (same family, regular weight)
**Numeric Font:** Atkinson Hyperlegible Mono (with ui-monospace fallback) for every number that updates live

**Character:** A single humanist sans, drawn by the Braille Institute for readers with low vision, carries every text role. The characters that collapse into each other in most sans faces — `I` / `l` / `1`, `O` / `0`, `b` / `d` — are drawn apart on purpose, which matters directly to a page whose primary audience reads it through a compressed 720p video pipeline. The matching mono gives the counts and position numbers tabular alignment without introducing a second voice. Both faces are variable, declaring the full `wght` axis (200–800) so no renderable weight is clamped away, and both use `font-display: swap`.

### Hierarchy

- **Display** (Atkinson Next, 700, `clamp(2rem, 3.4vw, 2.75rem)`, line-height 1.05, letter-spacing -0.015em): the icebreaker prompt, set in On Deep on the masthead band. A borderless, transparent `textarea` the host types directly into. One per page.
- **Headline** (Atkinson Next, 600, 1.25rem, line-height 1.2, letter-spacing -0.01em): the first-run welcome title only.
- **Title** (Atkinson Next, 500, 1.0625rem / 17px): the roster names at rest — the words the room actually reads through a compressed feed.
- **Body** (Atkinson Next, 400, 0.9375rem / 15px, line-height 1.5): prose — empty-state copy, the completion callout, the demo-bar title (which steps up to 600 weight for emphasis within body size).
- **Caption** (Atkinson Next, 400, 0.8125rem / 13px): the masthead's meta line ("live · Started ··"), the demo-bar note, the first-run footnote.
- **Label** (Atkinson Next, 500, 0.75rem / 12px, letter-spacing 0.04em): the count band's labels, the toggle's default text, the theme picker's chips and its "Theme" caption. The host pill uses the same size and weight at a wider 0.06em tracking; the `[left]` tag uses the same size at 0.06em tracking but regular (400) weight.
- **Label Strong** (Atkinson Next, 600, 0.75rem / 12px, letter-spacing 0.04em): button text — primary and ghost alike.
- **Label Loud** (Atkinson Next, 700, 0.75rem / 12px, letter-spacing 0.05em, uppercase): the up-next tag only. The one uppercase string in the system, and the boldest label weight in the type scale.
- **Numeric** (Atkinson Mono, 600, 2.25rem / 36px, tabular): the count band's three big figures, set in accent-ink rather than ink (6.8:1 on surface) — the page's only big numerals carry the theme's accent directly instead of a border or a background shift. Drops to **Numeric Compact** (1.75rem / 28px) below 640px.
- **Numeric Row** (Atkinson Mono, 500, 1.125rem / 18px, tabular): the standing position number on each roster row, right-aligned, `user-select: none`.
- **Numeric Emphasis** (Atkinson Mono, 700, 1.5rem / 24px, tabular): the position number on the up-next row only, in accent-ink. Bolder than the base numeric-row weight — the size step and the weight step both say "this one."
- **Numeric Caption** (Atkinson Mono, 400, 0.8125rem / 13px, tabular): the joined-at timestamp. First thing dropped below 640px.

### Named Rules: Typography

**The One-Family Rule.** Atkinson Hyperlegible Next plus Atkinson Hyperlegible Mono is the entire type system. No serif, no second sans, no icon font carrying glyph weight.

**The Tabular Numerics Rule.** Every number that updates live — the three counts, both position-number roles, the timestamp — renders in Atkinson Mono with `font-feature-settings: 'tnum' 1'`. Numbers must not reflow their container.

**The Self-Hosted Type Rule.** Both faces ship from `fonts/` as the latin subset, `crossorigin`-preloaded from `index.html`, and are never fetched from a CDN — PRODUCT.md's no-third-party-request promise is a build constraint, not a marketing line, and a webfont request would break it silently.

**The Screen-Share Floor Rule.** Body type never goes below 15px; labels never go below 12px. Test by downsampling a screenshot to 1280×720 and reading it from 2m away.

**The One Uppercase Rule.** Exactly one string in the system is uppercase: the up-next tag. It is also the single heaviest label weight (700) in the scale — uppercase and maximum weight are spent together, once, on the moment that matters most.

## Layout

A single centered column with a full-bleed exception at the very top.

**Container.** `max-width: 880px`, centered, inside a viewport-relative gutter of `5vw` horizontally and `5vh 0` vertically below the masthead (`4vw 4vh` under 640px). Body carries no top padding — the masthead bleeds flush to the viewport edge, then the centered column resumes underneath it.

**The full-bleed masthead.** `header` and `.prompt-sticky` share a `background: var(--field)` with a `margin-inline: calc(50% - 50vw)` / `padding-inline: calc(50vw - 50%)` pair that cancels the centered column, so the fill spans the full viewport width while the live-meta line and the prompt text stay aligned to the 880px grid. This is the system's one full-bleed device, and it exists for a single reason: the masthead is a structural commitment, not a decorated header.

**Sticky prompt band.** `.prompt-sticky` is `position: sticky; top: 0; z-index: 10`, filled with the same field color as the masthead so the two read as one continuous band as the page scrolls. Its geometry never changes: the band always carries `box-shadow: 0 4px 16px`, whose color is `transparent` at rest and becomes `var(--pin-shadow)` only once `.is-pinned` is toggled by an `IntersectionObserver` watching a 1px sentinel placed just above it. Transitioning the color rather than the whole shadow keeps the blur from animating, and per-theme `--pin-shadow` lets the drop stay ink-tinted by day and true black after dark. This is **the only shadow in the entire stylesheet**, and it is functional (it announces that the band has detached from normal flow), not decorative.

**Vertical rhythm.** Roughly: masthead 22px top padding, prompt band 10px/18px padding with 28px margin below, count band 14px/20px padding with 28px margin below, callout 14px/20px padding with 22px margin below, demo bar 12px/16px padding with 16px margin above and below, roster rows 8px apart, footer 32px above, theme picker 24px above that, sponsor line 32px above that again.

**The spacing scale** (4 / 8 / 12 / 16 / 20 / 24 / 32 / 48) covers the round values that recur. A number of block measurements (10, 14, 17–18, 22, 28) sit off that scale, tuned against a real screen-share rather than pulled from the token list — treat the scale as the default for new work and the off-scale values as measured exceptions.

**Grids.** Three grids carry the page, each collapsing once at the single breakpoint:

- **Count band:** a single flex row (`justify-content: space-between; align-items: baseline`), not a grid of tiles — see the Named Rule below. Below 640px each count stacks its label under its numeral, but the three stay in one shared surface and one row.
- **Roster row:** `40px 1fr auto auto auto` (position, name, timestamp, toggle, remove) with a 14px gap. Below 640px it becomes `28px 1fr auto auto`: the position column narrows, the gap tightens to 10px, and the timestamp is dropped outright.
- **Footer:** `1fr auto` (add-form, actions) with a 20px gap, collapsing to a single stacked column below 640px.

**Truncation and measure.** Names truncate with an ellipsis on one line rather than wrapping. Prose is capped by measure: 42ch for the empty-state lede, 46ch for its footnote, 50ch for the first-run body, with `text-wrap: pretty` on the longest block.

### Named Rules: Layout

**The Counts-Are-a-Band Rule.** The three counts render as one continuous flex row on a shared baseline, never as three separate tiles. This is a direct rejection of PRODUCT.md's named anti-reference — "hero metric tiles with gradient accents" is exactly the generic-SaaS-dashboard look the product explicitly refuses.

**The One Breakpoint Rule.** The system has exactly one breakpoint: 640px. Above it, one layout flexes; below it, the same layout drops columns.

**The Row-Never-Wraps Rule.** A roster row stays one line at every width. Below 640px, the timestamp and the up-next tag are both dropped (simultaneously — there is no intermediate width where only one goes) so the row keeps its shape; the name never shrinks below Title size. Ordinary rows ellipsize a long name rather than wrapping; the **up-next row is the one exception** — its name wraps instead of truncating, at every width, because it is the row the whole room is reading for exactly that name. Truncating there would defeat the same reasoning that drops the tag.

## Elevation & Depth

Flat by default, with one narrowly-scoped exception. The stylesheet contains exactly one `box-shadow` pair — the sticky prompt band's pinned state — and nothing else. Depth everywhere else is tonal: ground, surface, and card are the entire layering vocabulary, plus the baton wash as a fourth, chroma-carrying surface reserved for celebration.

Tonal layering is the one part of the system a theme genuinely rearranges. In the three light skies the ladder reads ground → card *up* (white), surface *down*; After Dark it climbs in one direction — ground `#0e1c26` → card `#16293a` → surface `#213950`, rows stepping lighter than the canvas rather than darker. What every sky preserves is that the three layers stay distinguishable from each other at 720p; the direction of the step is a lighting decision, the separation is the system.

The live dot's halo is not a shadow: it rides a pseudo-element that scales and fades (`scale(1) → scale(3.6)`, opacity `0.45 → 0`), which composites on the GPU instead of repainting the dot every frame. That distinction matters specifically because this page is screen-shared — a region that repaints forever denies the video encoder a static area to skip.

### Named Rules: Elevation

**The One Functional Shadow Rule.** The system's only shadow is `0 4px 16px var(--pin-shadow)` on `.prompt-sticky.is-pinned`, and it exists to announce that the band has detached from normal flow. The geometry is constant and only the color moves — `transparent` at rest, `--pin-shadow` when pinned (`rgba(0, 32, 51, 0.18)` in the light skies, `rgba(0, 0, 0, 0.55)` after dark). It is not decorative, it does not appear anywhere else, and a second shadow anywhere in the system needs to justify itself the same way this one does — as a signal, not a lighting effect. A new shadow also owes every sky a value: hard-coding an ink-tinted rgba is exactly the thing `--pin-shadow` exists to prevent.

**The No-Decorative-Glow Rule.** Backdrop blurs, ambient bloom behind hero text, hover glows: none survive a screen-share, so none are in the system.

## Shapes

Two radii and a hairline-first border system.

- **10px (`{rounded.sm}`)** — *containers*: roster rows, the count band, the callout, the demo-mode bar, the empty state.
- **6px (`{rounded.xs}`)** — *controls*: buttons, the toggle, inputs, the up-next tag, the theme chips, the focus radius on the prompt.
- **999px (`{rounded.pill}`)** — annotations and discs: the `[left]` tag, the live/demo dots, and the theme picker's horizon swatch with its 5px sun.

**Borders escalate in three steps**, and the color is the signal:

- **Hairline** — the default edge: rows, toggles, inputs, tags, the sponsor pill, a hovered theme chip.
- **Soft Line** — emphasis: the host row's ring, the scrollbar thumb, the theme swatch's edge (a hairline lets its light half dissolve into the page).
- **Accent Ink** — attention and structure: the up-next row's 2px frame, every focus ring except the prompt's, the drag insertion line, the selected theme chip, the focused input's border.
- **Dashed hairline** — the ordinary empty roster only, reading as "space waiting to be filled"; the first-run state switches to solid because it is content, not an absence.
- **Transparent** — a real rung, used once: theme chips carry a 1px transparent border at rest so only the chosen sky shows an edge and no chip shifts by a pixel when it becomes selected.

### Named Rules: Shapes

**The Two-Radius Rule.** Containers get 10px, controls get 6px. The pill is reserved for annotations and dots.

**The Border Escalation Rule.** Reach for border color before background color when marking attention: hairline → soft-line → accent-ink is the fixed ladder. Up-next skips straight to accent-ink at 2px because it is the page's single most important signal, not an incremental emphasis. The demo bar's baton-ink border is the ladder's one documented exception (see Components), not a fourth rung.

## Components

### Masthead & Sticky Prompt Band

The signature device. A full-bleed field carries the live-status meta line and the display-size editable prompt as one continuous band, with a single functional shadow that appears only once the band pins to the top of the viewport on scroll. Placeholder, caret, and focus ring are baton-bright; the live dot is the baton on the field with a composited pulse halo; the meta line is field-text. See Layout for the full-bleed mechanism and Elevation for the shadow.

### Roster Row

One row per participant, and every state pairs at least two signals.

- **Shape:** 10px radius, 1px hairline border, `card` background.
- **Default:** card background, ink name, muted-ink timestamp.
- **Introduced:** surface background, name and numerals shift to muted-ink, and the toggle shows a drawn checkmark. No hue change; fill + ink + icon carry it.
- **Left:** card background stays, name shifts to dim-ink, a `[left]` pill tag appears. No opacity trick.
- **Up-next:** baton-wash background, 2px accent-ink border (7.3:1 on the wash), padding compensates to 17px (18px minus the extra border pixel so rows stay visually aligned), position number steps to Numeric Emphasis in accent-ink, name steps to 1.25rem/700, and an uppercase baton-filled tag under on-gold reads "you're up next." The tag is dropped below 640px along with the timestamp.
- **Host:** a 1px soft-line ring instead of hairline, a lowercase "host" label in accent-ink after the name, `cursor: default` (never reorderable).
- **Reorder affordance:** `cursor: grab`/`grabbing`, 40% opacity while lifted, a 2px accent-ink insertion line drawn 5px above or below the drop target via a pseudo-element that only fades opacity.
- **Focus:** 2px accent-ink outline, 2px offset — rows are keyboard-reorderable with ↑/↓.

### Toggle (Mark Introduced)

- **Shape:** 6px radius, 1px hairline border, 8px/14px padding (7px/10px below 640px).
- **Default:** card background, muted-ink "Mark introduced" label.
- **Hover:** border to soft-line, text to ink.
- **On:** field fill, On Deep text and checkmark, field border; hover steps to field-hover.
- **Focus:** 2px accent-ink outline, 2px offset.

### Completion Gesture

The per-person celebration. Marking someone introduced fires three coordinated beats — see Motion for exact timings: `mark-flash` on the row background, `draw-check` on the toggle's checkmark path, and — only when a new up-next emerges — `pos-cue` on their position number plus `tag-pop` on their tag, both delayed to land as the third beat.

### Completion Callout

The one whole-room celebration. When everyone present has introduced themselves, a baton-wash callout appears with a one-shot 1200ms `callout-settle` arrival (fading in from a richer gold-mixed tint to the flat wash). `app.js` only rewrites the callout's `innerHTML` when its content actually changes, so the settle never replays on a poller re-render that changed nothing.

### Count Band

- **Shape:** 10px radius, surface background, no border — tonal contrast is the only delimiter.
- **Layout:** one flex row, three groups, shared baseline. Never three separate tiles — see the Counts-Are-a-Band Rule.
- **Number:** Numeric typography, accent-ink (not ink) — the counts carry the theme's accent directly.
- **Label:** Label typography, muted-ink, below the number (beside it, stacked, below 640px).

### Buttons

- **Primary (`Add`):** field fill and border, On Deep text, 6px radius, 10px/16px padding, Label Strong typography. Hover: field-hover. Focus: 2px accent-ink outline, 2px offset.
- **Ghost (`Randomize order`, `Reset session`, `Exit demo`):** card background, dim-ink text, hairline border. Hover: surface background, ink text, soft-line border.
- **Icon-only (remove):** no fill or border, hint-ink glyph (the glyph is the control's only label, so it answers the 3:1 non-text floor), 6px padding around the 12px glyph (24px visual target, the WCAG 2.5.8 minimum). Hover paints the glyph accent-ink on a surface chip — swapped to the card step on the introduced and up-next rows, where surface is already the row fill or would smudge the wash. On coarse pointers an invisible `::after` extension grows the hit area to 44px without moving the visual chip or the row layout.
- **Chip (theme picker):** transparent-bordered at rest, card fill and accent-ink border when selected — documented with the picker in Colors.
- **No further button variant.** The text link covers the next emphasis level down.

### Text Link

Re-offers the demo after first run.

- **Style:** accent-ink text at caption size, underlined with a 3px offset, 4px padding (28px hit area, clear of the 24px minimum).
- **Hover:** darkens to ink. **Focus:** 2px accent-ink outline, 2px offset.

### Inputs

- **Shape:** 6px radius, 1px hint-ink border (not hairline — a bare field's boundary is its only "type here" signal, so it answers to the 3:1 non-text floor that hairline's 1.4:1 can't meet), card background.
- **Default:** ink text, muted-ink placeholder, 10px/14px padding.
- **Focus:** border shifts to accent-ink on any focus; keyboard focus (`:focus-visible`) additionally gets the system's full 2px accent-ink ring at 2px offset — the border shift alone was thinner than the system's own focus bar.
- **Prompt (display-size):** the exception. Borderless, transparent, non-resizable, baton-bright placeholder and caret, a 2px baton-bright outline at a 6px offset on focus (wide enough to clear 44px-tall type without touching it). The prompt is the one control whose focus ring is not accent-ink, because it sits on the field rather than beside it.

### Demo-Mode Bar

- **Shape:** 10px radius, baton-wash background, 1px baton-ink border — the one border in the system that isn't hairline/soft-line/accent-ink, because this message must not be missed.
- **Content:** an 8px baton-ink dot (the baton itself would be invisible on its own wash, 1.5:1), a 600-weight body-size title, a caption-size muted-ink note (5.95:1 on the wash), a ghost "Exit demo" button.

### Empty & First-Run State

- **Ordinary empty:** centered column, muted-ink body, 48px/24px padding, dashed hairline border — space waiting to be filled.
- **First run:** solid hairline border, 48px/32px padding, a Headline-size title, a dim-ink body at 50ch/1.55 line-height, a 46ch caption footnote, and the demo call-to-action button.

### Live Dot

- **Shape:** 7px circle, baton fill on the masthead field (4.5:1).
- **Behavior:** a composited pseudo-element halo scales to 3.6× and fades, 2.4s loop on glide.
- **Reduced motion:** the halo is removed; the dot stays solid. Connection state is also carried by the adjacent word ("live" / "reconnecting").

### Sponsor Link

A label-size, muted-ink link in a hairline-bordered 6px chip, centered below the theme picker with an inline 12px SVG heart. Hover: text to ink, border to accent-ink. Plain link only — never an embedded iframe, which would phone home on every load.

## Do's and Don'ts

### Do

- **Do** reach for a role token, never a literal: `--ground` for the canvas, `--card` for content surfaces, `--surface` as the only second tonal layer, `--field` for structural fills, `--accent-ink` for marks and rings on light surfaces. A hard-coded hex is a bug in three of the four skies.
- **Do** check any new surface in all four themes before calling it done — especially After Dark, where the tonal ladder climbs instead of descending and every derived role (`--accent-ink`, `--on-gold`, `--pin-shadow`) has a different value than it aliases by day.
- **Do** carry introduced-vs-waiting-vs-up-next through at least two non-hue signals together: fill + ink color + icon, or wash + border + size.
- **Do** treat the baton as a response to something happening, never a resting-state color. The field is what the page looks like when nothing has happened yet.
- **Do** keep every state transition on `--glide`. Reserve `--spring` for `tag-pop` and `pos-cue` only.
- **Do** render every live-updating number in Atkinson Mono with tabular figures.
- **Do** drop the timestamp and the up-next tag together below 640px; the name never shrinks below Title size.
- **Do** zero animation *delays* as well as durations under reduced motion, and pin any animation whose meaning lives in its end state (the drawn checkmark) explicitly rather than trusting fill-mode.
- **Do** test every screen downsampled to 1280×720, read from 2m away.

### Don't

- **Don't** let the browser invent a dark theme. `:root` sets `color-scheme: only light` specifically to stop Chrome's Auto Dark Theme force-inverting whichever sky the host chose; the only dark rendition is the authored After Dark theme, which opts back in with `color-scheme: dark` on its own block, over a lifted blue-black ground with re-checked contrast throughout.
- **Don't** add a theme by adding a selector. A new sky is a `:root[data-theme="…"]` block of token values and a chip with pinned preview colors — nothing more. If a sky needs a rule of its own, the component is reading a color it should be reading as a role.
- **Don't** use the baton as a default UI color on any surface that isn't tied to a happy moment (up-next, completion, demo mode, selection).
- **Don't** set text in hairline or soft-line — they are border-only colors (1.4:1 and 1.8:1).
- **Don't** reach for `--bright-blue`; it is declared but unused in the shipped stylesheet. Give it a real role before treating it as part of the working palette.
- **Don't** put a warning color, countdown, or shaming microcopy on anyone still "to go." PRODUCT.md's no-spotlight-on-absence principle forbids it.
- **Don't** reach for the generic SaaS dashboard idioms PRODUCT.md names by name: hero-metric tiles, identical icon+heading+text card grids, a navy-and-indigo reflex palette.
- **Don't** introduce gamified-leaderboard chrome: avatars, points, badges, celebration animations tied to speed. Introductions are not a race.
- **Don't** mimic Zoom or Slack chrome. The page is shared *inside* Zoom; it should feel like a separate artifact.
- **Don't** add a second breakpoint, a third border-escalation color, or a third motion curve. One of each beyond what's documented here means a component is confused about its own role.
- **Don't** add a shadow anywhere but the pinned prompt band without first asking whether it's signaling something or just decorating.
