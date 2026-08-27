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
  deep-blue: "#005581"
  deep-blue-hover: "#0069a0"
  on-deep: "#ffffff"
  on-deep-dim: "rgba(255, 255, 255, 0.35)"
  bright-blue: "#1295d8"
  sky-text: "#9adcf9"
  gold: "#ffb511"
  gold-bright: "#ffd200"
  gold-wash: "#fff3ce"
  sun-ink: "#8a5b00"
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
    backgroundColor: "{colors.deep-blue}"
    textColor: "#ffffff"
    padding: "22px 0 18px"
  prompt-input:
    backgroundColor: "transparent"
    textColor: "#ffffff"
    typography: "{typography.display}"
    padding: "0"
  button-primary:
    backgroundColor: "{colors.deep-blue}"
    textColor: "#ffffff"
    typography: "{typography.label-strong}"
    rounded: "{rounded.xs}"
    padding: "10px 16px"
  button-primary-hover:
    backgroundColor: "{colors.deep-blue-hover}"
    textColor: "#ffffff"
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
    backgroundColor: "{colors.deep-blue}"
    textColor: "#ffffff"
    typography: "{typography.label}"
    rounded: "{rounded.xs}"
    padding: "8px 14px"
  toggle-on-hover:
    backgroundColor: "{colors.deep-blue-hover}"
    textColor: "#ffffff"
  roster-row:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: "14px 18px"
  roster-row-introduced:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.muted-ink}"
  roster-row-up-next:
    backgroundColor: "{colors.gold-wash}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: "17px"
  roster-row-left:
    backgroundColor: "{colors.card}"
    textColor: "{colors.dim-ink}"
  up-next-tag:
    backgroundColor: "{colors.gold}"
    textColor: "{colors.ink}"
    typography: "{typography.label-loud}"
    rounded: "{rounded.xs}"
    padding: "3px 9px"
  host-pill:
    textColor: "{colors.deep-blue}"
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
    textColor: "{colors.deep-blue}"
    rounded: "{rounded.sm}"
    padding: "14px 20px"
  input-field:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
    rounded: "{rounded.xs}"
    padding: "10px 14px"
  callout:
    backgroundColor: "{colors.gold-wash}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: "14px 20px"
  demo-bar:
    backgroundColor: "{colors.gold-wash}"
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
    textColor: "{colors.deep-blue}"
    typography: "{typography.caption}"
    padding: "4px"
  live-dot:
    backgroundColor: "{colors.gold}"
    rounded: "{rounded.pill}"
    size: "7px"
---

# Design System: Zoom Icebreaker Tracker

## Overview

### Creative North Star: "Clear Sky, Gold Baton"

A round-robin tracker rebuilt as a clear California day. One deep-blue masthead — the band that holds the live indicator and the icebreaker prompt — bleeds full-width across the top of the page and owns every primary control below it. Gold appears nowhere as decoration; it exists for exactly one job, marking whoever holds the baton right now: the up-next row, the completion callout, the demo-mode bar, text selection. Everything else on the page is sky-tinted blue-on-white, calm enough to sit in the corner of a meeting without competing with the conversation in the room.

This system explicitly retires two prior worlds rather than blending with either: the beige-ledger warm-paper system it replaced (clay accent, paper neutrals, no blue at all), and the navy-dashboard reflex the category defaults to. Neither survives in any token here. The palette is airy and blue rather than warm and paper-toned; the accent is a genuine gold rather than a clay terracotta; and for the first time the system gives its primary color — deep blue — a full-bleed structural role (the masthead) rather than confining it to small controls.

State is still never read through hue alone. Introduced vs. waiting pairs a fill change with an ink-color shift and a checkmark icon; up-next pairs a wash, a 2px deep-blue frame, and larger type, three signals at once. Motion carries exactly two curves: a glide that moves every piece of state, and a spring reserved for precisely two celebration animations. The design wants the room to find the next speaker in one glance and the host to never wonder what a color means.

### Key Characteristics

- Sky-tinted ground (`#f4f9fd`), never gray, never warm paper
- Full-bleed deep-blue masthead owns the live indicator, the prompt, and every primary button
- Gold is reserved for happy moments only: up-next, completion, demo mode, selection — never a default UI color
- Single sans family (Atkinson Hyperlegible Next), single mono (Atkinson Hyperlegible Mono) for numerics, both self-hosted
- One functional shadow in the entire stylesheet (the pinned prompt band); everything else is flat
- Two motion curves: glide for all state, spring for exactly two one-shot celebrations
- No dark theme, ever — the page ships `color-scheme: only light` specifically to stop browsers from force-inverting it
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

An airy, blue-tinted palette built around a single structural role reversal: deep blue is no longer a small accent, it is the field the masthead and every primary control sit on. Gold is the accent, and it is licensed for happy moments only.

### Primary

- **Deep Blue** (`#005581`): the committed field. Fills the full-bleed masthead and sticky prompt band, every primary button, the "on" state of the introduced toggle, the up-next row's 2px frame, focus rings on everything except the prompt itself, and the drag-drop insertion line. Text on deep blue uses the **On Deep** token (`#ffffff`, 8:1) with **On Deep Dim** (`rgba(255,255,255,.35)`) for separators; white-on-blue is a named role, never a literal.
- **Deep Blue Hover** (`#0069a0`): the pressed/hover step for every deep-blue-filled control — the primary button, the "on" toggle.

### Secondary

- **Gold** (`#ffb511`): the baton. Reserved for happy-moment surfaces and marks: the live dot (on deep blue, 4.5:1), the up-next tag's fill (with ink text at 9.5:1), and nothing that isn't a moment of attention.
- **Gold Bright** (`#ffd200`): the prompt's placeholder text and caret (5.5:1 on deep blue, clearing the 3:1 large-text floor) and the system's text-selection background. A step brighter than plain gold because it has to read as an invitation against the masthead's deep field, not just as a mark.
- **Gold Wash** (`#fff3ce`): the celebration surface — the up-next row's background, the completion callout, and the demo-mode bar. The one place besides deep blue where a whole surface (not just a mark) carries the accent.
- **Sun Ink** (`#8a5b00`): a small, deliberately scoped ink for gold-wash content that needs a border or a mark rather than the body's default ink color — currently the demo-mode bar's dot and border only. It is not the default text color on gold surfaces: the completion callout and the up-next row both set body text in plain `ink`, and the up-next row's border is deep-blue, not sun-ink. Reach for sun-ink specifically when gold itself would be illegible on a gold ground (a gold dot on a gold wash is 1.5:1), not as a general "text on gold" rule.
- **Bright Blue** (`#1295d8`): declared in `:root` with a documented 3.1:1 non-text-floor intent ("live accents on white") but not yet consumed by any selector in the stylesheet. Treat it as reserved, not load-bearing — do not point new work at it as though it already carries a role.

### Neutral

- **Ground** (`#f4f9fd`): the page canvas. Airy and faintly blue, never gray, never the old system's warm paper. Ink measures 15.8:1 on it.
- **Card** (`#ffffff`): true white, reserved for roster rows and every other content surface sitting on the sky-tinted ground — the crispness reads as "content" against the softer canvas.
- **Surface** (`#e3eef7`): the second tonal layer. The count band, the introduced-row fill. A step darker than ground, depth without elevation.
- **Hairline** (`#c9dcea`): default 1px borders. Border-only — 1.4:1, cannot carry text.
- **Soft Line** (`#9ec1d9`): emphasized borders — the host row's ring, the themed scrollbar. Border-only — 1.8:1.
- **Hint Ink** (`#5b7a8c`): the lightest text-capable ink, 4.3:1 on ground. Licensed for the remove-glyph icon (a graphical control, answering the 3:1 floor) and the regular input's border, which — unlike a button with its own label — needs to clear the 3:1 non-text floor on its own.
- **Muted Ink** (`#44616f`): secondary text — timestamps, labels, position numbers, the introduced-row's name color, the count band's labels. 5.6:1 on surface, 6.2:1 on ground.
- **Dim Ink** (`#1e3e4f`): tertiary text and ghost-button text.
- **Ink** (`#002033`): primary text, and the deep end of the sky palette. Never `#000`.
- **Sky Text** (`#9adcf9`): meta text set directly on the deep-blue masthead band (5.3:1) — the "Started ·· ago" line and its separator.

### Named Rules: Colors

**The Gold-Under-Ink Rule.** Gold never carries text on a light ground by itself. It is either a surface that ink sits on top of (the wash, the tag fill), or a mark against deep blue (the dot, the placeholder, the caret) — never the text color itself against a light background.

**The No-Hue-Alone Rule.** Introduced vs. waiting vs. up-next is never read through color alone. Introduced pairs a fill change (card → surface) with an ink-color shift (ink → muted-ink) and a checkmark icon on the toggle. Up-next pairs a wash, a 2px deep-blue frame, and larger type (name steps to 1.25rem/700, position number to `numeric-emphasis`) — three simultaneous signals, never the wash alone.

**Blue Owns the Structure, Gold Owns the Moment.** Deep blue is the default state of every primary control and the masthead field; it is present on the page at rest, in every session, whether or not anyone has been marked introduced yet. Gold only ever appears in response to something happening — someone becomes up next, everyone finishes, a sample session is loaded. If a new element needs a color and nothing has happened yet, reach for deep blue or a neutral, never gold.

**The Three-Ink Floor Rule.** Text answers to exactly three inks depending on role: **ink** and **dim-ink** anywhere, **muted-ink** for secondary text, and **hint-ink** only for a graphical control glyph or where the 3:1 (not 4.5:1) floor applies. Hairline and soft-line are borders only.

## Typography

**Display Font:** Atkinson Hyperlegible Next (with system-ui, sans-serif fallback)
**Body Font:** Atkinson Hyperlegible Next (same family, regular weight)
**Numeric Font:** Atkinson Hyperlegible Mono (with ui-monospace fallback) for every number that updates live

**Character:** A single humanist sans, drawn by the Braille Institute for readers with low vision, carries every text role. The characters that collapse into each other in most sans faces — `I` / `l` / `1`, `O` / `0`, `b` / `d` — are drawn apart on purpose, which matters directly to a page whose primary audience reads it through a compressed 720p video pipeline. The matching mono gives the counts and position numbers tabular alignment without introducing a second voice. Both faces are variable, declaring the full `wght` axis (200–800) so no renderable weight is clamped away, and both use `font-display: swap`.

### Hierarchy

- **Display** (Atkinson Next, 700, `clamp(2rem, 3.4vw, 2.75rem)`, line-height 1.05, letter-spacing -0.015em): the icebreaker prompt, set in white on the deep-blue masthead band. A borderless, transparent `textarea` the host types directly into. One per page.
- **Headline** (Atkinson Next, 600, 1.25rem, line-height 1.2, letter-spacing -0.01em): the first-run welcome title only.
- **Title** (Atkinson Next, 500, 1.0625rem / 17px): the roster names at rest — the words the room actually reads through a compressed feed.
- **Body** (Atkinson Next, 400, 0.9375rem / 15px, line-height 1.5): prose — empty-state copy, the completion callout, the demo-bar title (which steps up to 600 weight for emphasis within body size).
- **Caption** (Atkinson Next, 400, 0.8125rem / 13px): the masthead's meta line ("live · Started ··"), the demo-bar note, the first-run footnote.
- **Label** (Atkinson Next, 500, 0.75rem / 12px, letter-spacing 0.04em): the count band's labels, the toggle's default text. The host pill uses the same size and weight at a wider 0.06em tracking; the `[left]` tag uses the same size at 0.06em tracking but regular (400) weight.
- **Label Strong** (Atkinson Next, 600, 0.75rem / 12px, letter-spacing 0.04em): button text — primary and ghost alike.
- **Label Loud** (Atkinson Next, 700, 0.75rem / 12px, letter-spacing 0.05em, uppercase): the up-next tag only. The one uppercase string in the system, and the boldest label weight in the type scale.
- **Numeric** (Atkinson Mono, 600, 2.25rem / 36px, tabular): the count band's three big figures, set in deep-blue rather than ink — the counts carry the brand color directly instead of a border or a background shift. Drops to **Numeric Compact** (1.75rem / 28px) below 640px.
- **Numeric Row** (Atkinson Mono, 500, 1.125rem / 18px, tabular): the standing position number on each roster row, right-aligned, `user-select: none`.
- **Numeric Emphasis** (Atkinson Mono, 700, 1.5rem / 24px, tabular): the position number on the up-next row only, in deep-blue. Bolder than the base numeric-row weight — the size step and the weight step both say "this one."
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

**The full-bleed masthead.** `header` and `.prompt-sticky` share a `background: var(--deep-blue)` with a `margin-inline: calc(50% - 50vw)` / `padding-inline: calc(50vw - 50%)` pair that cancels the centered column, so the fill spans the full viewport width while the live-meta line and the prompt text stay aligned to the 880px grid. This is the system's one full-bleed device, and it exists for a single reason: the masthead is a structural commitment, not a decorated header.

**Sticky prompt band.** `.prompt-sticky` is `position: sticky; top: 0; z-index: 10`, filled with the same deep blue as the masthead so the two read as one continuous band as the page scrolls. Its `box-shadow` starts fully transparent (`rgba(0, 32, 51, 0)`) and transitions to `rgba(0, 32, 51, 0.18)` only once `.is-pinned` is toggled by an `IntersectionObserver` watching a 1px sentinel placed just above it — **the only shadow in the entire stylesheet**, and it is functional (it announces that the band has detached from normal flow), not decorative.

**Vertical rhythm.** Roughly: masthead 22px top padding, prompt band 10px/18px padding with 28px margin below, count band 14px/20px padding with 28px margin below, callout 14px/20px padding with 22px margin below, demo bar 12px/16px padding with 16px margin above and below, roster rows 8px apart, footer 32px above, sponsor line 32px above that.

**The spacing scale** (4 / 8 / 12 / 16 / 20 / 24 / 32 / 48) covers the round values that recur. A number of block measurements (10, 14, 17–18, 22, 28) sit off that scale, tuned against a real screen-share rather than pulled from the token list — treat the scale as the default for new work and the off-scale values as measured exceptions.

**Grids.** Three grids carry the page, each collapsing once at the single breakpoint:

- **Count band:** a single flex row (`justify-content: space-between; align-items: baseline`), not a grid of tiles — see the Named Rule below. Below 640px each count stacks its label under its numeral, but the three stay in one shared surface and one row.
- **Roster row:** `40px 1fr auto auto auto` (position, name, timestamp, toggle, remove) with a 14px gap. Below 640px it becomes `28px 1fr auto auto`: the position column narrows, the gap tightens to 10px, and the timestamp is dropped outright.
- **Footer:** `1fr auto` (add-form, actions) with a 20px gap, collapsing to a single stacked column below 640px.

**Truncation and measure.** Names truncate with an ellipsis on one line rather than wrapping. Prose is capped by measure: 42ch for the empty-state lede, 46ch for its footnote, 50ch for the first-run body, with `text-wrap: pretty` on the longest block.

### Named Rules: Layout

**The Counts-Are-a-Band Rule.** The three counts render as one continuous flex row on a shared baseline, never as three separate tiles. This is a direct rejection of PRODUCT.md's named anti-reference — "hero metric tiles with gradient accents" is exactly the generic-SaaS-dashboard look the product explicitly refuses.

**The One Breakpoint Rule.** The system has exactly one breakpoint: 640px. Above it, one layout flexes; below it, the same layout drops columns.

**The Row-Never-Wraps Rule.** A roster row stays one line at every width. Below 640px, the timestamp and the up-next tag are both dropped (simultaneously — there is no intermediate width where only one goes) so the row keeps its shape; the name never shrinks below Title size and never wraps.

## Elevation & Depth

Flat by default, with one narrowly-scoped exception. The stylesheet contains exactly one `box-shadow` pair — the sticky prompt band's pinned state — and nothing else. Depth everywhere else is tonal: ground → surface → card is the entire layering vocabulary, plus the gold wash as a fourth, chroma-carrying surface reserved for celebration.

The live dot's halo is not a shadow: it rides a pseudo-element that scales and fades (`scale(1) → scale(3.6)`, opacity `0.45 → 0`), which composites on the GPU instead of repainting the dot every frame. That distinction matters specifically because this page is screen-shared — a region that repaints forever denies the video encoder a static area to skip.

### Named Rules: Elevation

**The One Functional Shadow Rule.** The system's only shadow exists to announce that the sticky prompt band has detached from normal flow. It is not decorative, it does not appear anywhere else, and a second shadow anywhere in the system needs to justify itself the same way this one does — as a signal, not a lighting effect.

**The No-Decorative-Glow Rule.** Backdrop blurs, ambient bloom behind hero text, hover glows: none survive a screen-share, so none are in the system.

## Shapes

Two radii and a hairline-first border system.

- **10px (`{rounded.sm}`)** — *containers*: roster rows, the count band, the callout, the demo-mode bar, the empty state.
- **6px (`{rounded.xs}`)** — *controls*: buttons, the toggle, inputs, the up-next tag, the focus radius on the prompt.
- **999px (`{rounded.pill}`)** — used twice: the `[left]` tag and the live/demo dots.

**Borders escalate in three steps**, and the color is the signal:

- **Hairline** — the default edge: rows, toggles, inputs, tags.
- **Soft Line** — emphasis: the host row's ring, the scrollbar thumb.
- **Deep Blue** — attention and structure: the up-next row's 2px frame, every focus ring except the prompt's, the drag insertion line.
- **Dashed hairline** — the ordinary empty roster only, reading as "space waiting to be filled"; the first-run state switches to solid because it is content, not an absence.

### Named Rules: Shapes

**The Two-Radius Rule.** Containers get 10px, controls get 6px. The pill is reserved for annotations and dots.

**The Border Escalation Rule.** Reach for border color before background color when marking attention: hairline → soft-line → deep-blue is the fixed ladder. Up-next skips straight to deep-blue at 2px because it is the page's single most important signal, not an incremental emphasis.

## Components

### Masthead & Sticky Prompt Band

The signature device. A full-bleed deep-blue field carries the live-status meta line and the display-size editable prompt as one continuous band, with a single functional shadow that appears only once the band pins to the top of the viewport on scroll. Placeholder and caret are gold-bright; the live dot is gold on the blue field with a composited pulse halo. See Layout for the full-bleed mechanism and Elevation for the shadow.

### Roster Row

One row per participant, and every state pairs at least two signals.

- **Shape:** 10px radius, 1px hairline border, `card` background.
- **Default:** card background, ink name, muted-ink timestamp.
- **Introduced:** surface background, name and numerals shift to muted-ink, and the toggle shows a drawn checkmark. No hue change; fill + ink + icon carry it.
- **Left:** card background stays, name shifts to dim-ink, a `[left]` pill tag appears. No opacity trick.
- **Up-next:** gold-wash background, 2px deep-blue border, padding compensates to 17px (18px minus the extra border pixel so rows stay visually aligned), position number steps to Numeric Emphasis in deep-blue, name steps to 1.25rem/700, and an uppercase gold-filled tag reads "you're up next." Dropped below 640px along with the timestamp.
- **Host:** a 1px soft-line ring instead of hairline, a lowercase "host" label in deep-blue after the name, `cursor: default` (never reorderable).
- **Reorder affordance:** `cursor: grab`/`grabbing`, 40% opacity while lifted, a 2px deep-blue insertion line drawn 5px above or below the drop target via a pseudo-element that only fades opacity.
- **Focus:** 2px deep-blue outline, 2px offset — rows are keyboard-reorderable with ↑/↓.

### Toggle (Mark Introduced)

- **Shape:** 6px radius, 1px hairline border, 8px/14px padding (7px/10px below 640px).
- **Default:** card background, muted-ink "Mark introduced" label.
- **Hover:** border to soft-line, text to ink.
- **On:** deep-blue fill, white text and checkmark, deep-blue border; hover deepens to deep-blue-hover.
- **Focus:** 2px deep-blue outline, 2px offset.

### Completion Gesture

The per-person celebration. Marking someone introduced fires three coordinated beats — see Motion for exact timings: `mark-flash` on the row background, `draw-check` on the toggle's checkmark path, and — only when a new up-next emerges — `pos-cue` on their position number plus `tag-pop` on their tag, both delayed to land as the third beat.

### Completion Callout

The one whole-room celebration. When everyone present has introduced themselves, a gold-wash callout appears with a one-shot 1200ms `callout-settle` arrival (fading in from a richer gold-mixed tint to the flat wash). `app.js` only rewrites the callout's `innerHTML` when its content actually changes, so the settle never replays on a poller re-render that changed nothing.

### Count Band

- **Shape:** 10px radius, surface background, no border — tonal contrast is the only delimiter.
- **Layout:** one flex row, three groups, shared baseline. Never three separate tiles — see the Counts-Are-a-Band Rule.
- **Number:** Numeric typography, deep-blue (not ink) — the counts carry the brand color directly.
- **Label:** Label typography, muted-ink, below the number (beside it, stacked, below 640px).

### Buttons

- **Primary (`Add`):** deep-blue fill and border, white text, 6px radius, 10px/16px padding, Label Strong typography. Hover: deep-blue-hover.
- **Ghost (`Randomize order`, `Reset session`, `Exit demo`):** card background, dim-ink text, hairline border. Hover: surface background, ink text, soft-line border.
- **Icon-only (remove):** no fill or border, 6px padding around the 12px glyph (24px visual target, the WCAG 2.5.8 minimum). On coarse pointers an invisible `::after` extension grows the hit area to 44px without moving the visual chip or the row layout.
- **No third button variant.** The text link covers the next emphasis level down.

### Text Link

Re-offers the demo after first run.

- **Style:** deep-blue text at caption size, underlined with a 3px offset, 4px padding (28px hit area, clear of the 24px minimum).
- **Hover:** darkens to ink. **Focus:** 2px deep-blue outline, 2px offset.

### Inputs

- **Shape:** 6px radius, 1px hint-ink border (not hairline — a bare field's boundary is its only "type here" signal, so it answers to the 3:1 non-text floor that hairline's 1.4:1 can't meet), card background.
- **Default:** ink text, muted-ink placeholder, 10px/14px padding.
- **Focus:** border shifts to deep-blue on any focus; keyboard focus (`:focus-visible`) additionally gets the system's full 2px deep-blue ring at 2px offset — the border shift alone was thinner than the system's own focus bar.
- **Prompt (display-size):** the exception. Borderless, transparent, non-resizable, gold-bright placeholder and caret, a 2px gold-bright outline at a 6px offset on focus (wide enough to clear 44px-tall type without touching it).

### Demo-Mode Bar

- **Shape:** 10px radius, gold-wash background, 1px sun-ink border — the one border in the system that isn't hairline/soft-line/deep-blue, because this message must not be missed.
- **Content:** an 8px sun-ink dot (gold itself would be invisible on the gold wash, 1.5:1), a 600-weight body-size title, a caption-size muted-ink note, a ghost "Exit demo" button.

### Empty & First-Run State

- **Ordinary empty:** centered column, muted-ink body, 48px/24px padding, dashed hairline border — space waiting to be filled.
- **First run:** solid hairline border, 48px/32px padding, a Headline-size title, a dim-ink body at 50ch/1.55 line-height, a 46ch caption footnote, and the demo call-to-action button.

### Live Dot

- **Shape:** 7px circle, gold fill on the deep-blue masthead (4.5:1).
- **Behavior:** a composited pseudo-element halo scales to 3.6× and fades, 2.4s loop on glide.
- **Reduced motion:** the halo is removed; the dot stays solid. Connection state is also carried by the adjacent word ("live" / "reconnecting").

### Sponsor Link

A caption-size, muted-ink link in a hairline-bordered pill, centered below the footer. Hover: text to ink, border to deep-blue. Plain link only — never an embedded iframe, which would phone home on every load.

## Do's and Don'ts

### Do

- **Do** use Ground (`#f4f9fd`) for the canvas and Card (`#ffffff`) for content surfaces; Surface (`#e3eef7`) is the only second tonal layer.
- **Do** carry introduced-vs-waiting-vs-up-next through at least two non-hue signals together: fill + ink color + icon, or wash + border + size.
- **Do** treat gold as a response to something happening, never a resting-state color. Deep blue is what the page looks like when nothing has happened yet.
- **Do** keep every state transition on `--glide`. Reserve `--spring` for `tag-pop` and `pos-cue` only.
- **Do** render every live-updating number in Atkinson Mono with tabular figures.
- **Do** drop the timestamp and the up-next tag together below 640px; the name never shrinks below Title size.
- **Do** zero animation *delays* as well as durations under reduced motion, and pin any animation whose meaning lives in its end state (the drawn checkmark) explicitly rather than trusting fill-mode.
- **Do** test every screen downsampled to 1280×720, read from 2m away.

### Don't

- **Don't** ship a dark theme. `color-scheme: only light` is set specifically to stop the browser from force-inverting the palette.
- **Don't** use gold as a default UI color on any surface that isn't tied to a happy moment (up-next, completion, demo mode, selection).
- **Don't** set text in hairline or soft-line — they are border-only colors (1.4:1 and 1.8:1).
- **Don't** reach for `--bright-blue`; it is declared but unused in the shipped stylesheet. Give it a real role before treating it as part of the working palette.
- **Don't** put a warning color, countdown, or shaming microcopy on anyone still "to go." PRODUCT.md's no-spotlight-on-absence principle forbids it.
- **Don't** reach for the generic SaaS dashboard idioms PRODUCT.md names by name: hero-metric tiles, identical icon+heading+text card grids, a navy-and-indigo reflex palette.
- **Don't** introduce gamified-leaderboard chrome: avatars, points, badges, celebration animations tied to speed. Introductions are not a race.
- **Don't** mimic Zoom or Slack chrome. The page is shared *inside* Zoom; it should feel like a separate artifact.
- **Don't** add a second breakpoint, a third border-escalation color, or a third motion curve. One of each beyond what's documented here means a component is confused about its own role.
- **Don't** add a shadow anywhere but the pinned prompt band without first asking whether it's signaling something or just decorating.
