---
name: Zoom Icebreaker Tracker
description: A per-meeting utility that shows a whole room who has and hasn't introduced themselves yet.
colors:
  paper: "#faf7f2"
  surface: "#f3eee5"
  hairline: "#ddd3c2"
  soft-line: "#c8bca6"
  hint-ink: "#9a8e79"
  muted-ink: "#756b5c"
  dim-ink: "#4a4036"
  ink: "#28201a"
  clay: "#c9573a"
  clay-deep: "#a44128"
  up-next-tint: "oklch(96.5% 0.04 44)"
typography:
  display:
    fontFamily: "Atkinson Hyperlegible Next, system-ui, sans-serif"
    fontSize: "clamp(2rem, 3.4vw, 2.75rem)"
    fontWeight: 600
    lineHeight: 1.05
    letterSpacing: "-0.015em"
  headline:
    fontFamily: "Atkinson Hyperlegible Next, system-ui, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 500
    lineHeight: 1.2
    letterSpacing: "-0.01em"
  title:
    fontFamily: "Atkinson Hyperlegible Next, system-ui, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 500
    lineHeight: 1.3
    letterSpacing: "-0.005em"
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
    lineHeight: 1.4
    letterSpacing: "0"
  label:
    fontFamily: "Atkinson Hyperlegible Next, system-ui, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 500
    lineHeight: 1.3
    letterSpacing: "0.04em"
  label-loud:
    fontFamily: "Atkinson Hyperlegible Next, system-ui, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 600
    lineHeight: 1.3
    letterSpacing: "0.05em"
  numeric:
    fontFamily: "Atkinson Hyperlegible Mono, ui-monospace, monospace"
    fontSize: "2.25rem"
    fontWeight: 500
    lineHeight: 1
    letterSpacing: "-0.01em"
    fontFeature: "'tnum' 1"
  numeric-compact:
    fontFamily: "Atkinson Hyperlegible Mono, ui-monospace, monospace"
    fontSize: "1.75rem"
    fontWeight: 500
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
    fontWeight: 600
    lineHeight: 1
    fontFeature: "'tnum' 1"
  numeric-caption:
    fontFamily: "Atkinson Hyperlegible Mono, ui-monospace, monospace"
    fontSize: "0.8125rem"
    fontWeight: 400
    lineHeight: 1.4
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
  button-primary:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    typography: "{typography.label}"
    rounded: "{rounded.xs}"
    padding: "10px 16px"
  button-primary-hover:
    backgroundColor: "{colors.dim-ink}"
    textColor: "{colors.paper}"
  button-ghost:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.dim-ink}"
    typography: "{typography.label}"
    rounded: "{rounded.xs}"
    padding: "10px 16px"
  button-ghost-hover:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
  toggle-default:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.muted-ink}"
    typography: "{typography.label}"
    rounded: "{rounded.xs}"
    padding: "8px 14px"
  toggle-hover:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
  toggle-introduced:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    typography: "{typography.label}"
    rounded: "{rounded.xs}"
    padding: "8px 14px"
  roster-row:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: "14px 18px"
  roster-row-introduced:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.muted-ink}"
  roster-row-up-next:
    backgroundColor: "{colors.up-next-tint}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: "18px 18px"
  roster-row-left:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.dim-ink}"
  up-next-tag:
    backgroundColor: "{colors.clay-deep}"
    textColor: "{colors.paper}"
    typography: "{typography.label-loud}"
    rounded: "{rounded.xs}"
    padding: "3px 9px"
  host-label:
    textColor: "{colors.clay}"
    typography: "{typography.label}"
    padding: "4px 6px"
  tag-left:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.muted-ink}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "2px 8px"
  stat-tile:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: "16px 20px"
  input-field:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.xs}"
    padding: "10px 14px"
  callout-waiting:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.dim-ink}"
    rounded: "{rounded.sm}"
    padding: "14px 20px"
  demo-bar:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: "12px 16px"
  empty-state:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.muted-ink}"
    rounded: "{rounded.sm}"
    padding: "48px 24px"
  empty-state-first-run:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.dim-ink}"
    rounded: "{rounded.sm}"
    padding: "48px 32px"
  text-link:
    textColor: "{colors.clay-deep}"
    typography: "{typography.caption}"
    padding: "2px 4px"
  live-dot:
    backgroundColor: "{colors.clay}"
    rounded: "{rounded.pill}"
    size: "7px"
---

# Design System: Zoom Icebreaker Tracker

## Overview

### Creative North Star: "The Quiet Operator"

A small, considered utility that helps the host of a meeting without performing. Every choice on the page is in service of two simultaneous audiences: the host clicking up close, and the whole room watching the screen-share from across a Zoom feed. Nothing is decorative; nothing competes with the conversation in the room.

The system is light, warm, and restrained. Paper-coded neutrals (faintly warm, never bleached white) carry the canvas. A single sans-serif (Atkinson Hyperlegible Next) handles every text role; tabular numerics use its matching mono. One accent, clay terracotta, exists for moments of attention (live indicator, focus outlines, identity badges) and is deliberately absent from the state vocabulary itself. State is read through fill density and weight, not color. The design wants to be remembered for *not* getting in the way.

This system explicitly rejects the gravitational pulls of its category: the dark-navy-and-amber dashboard look the current tracker shipped with, the gamified leaderboard chrome (avatars, points, badges), and the generic SaaS hero-metric template. It also rejects the obvious icebreaker-orange reflex; the warm accent here is clay, not pumpkin.

### Key Characteristics

- Light theme, warm paper neutrals, never `#fff`
- Single sans family (Atkinson Hyperlegible Next), single mono (Atkinson Hyperlegible Mono) for numerics
- Type is self-hosted, never fetched: the face is part of the build, not a CDN request
- One accent (clay), used sparingly and never as a state carrier
- Flat by default: no shadows, tonal layering only
- Restrained motion: state transitions, plus three short completion gestures — never decoration
- Screen-share legibility is the design's first audience

### Motion

Two easing tokens carry every interaction, both on the same curve so the system moves as one object:

- **`--t-fast`** (`140ms cubic-bezier(0.22, 1, 0.36, 1)`): the default. Hover, focus, toggle, border, and drop-indicator changes.
- **`--t-medium`** (`200ms cubic-bezier(0.22, 1, 0.36, 1)`): row transforms, where a slightly longer settle reads as deliberate rather than twitchy.

The curve is **ease-out-quint** — front-loaded, arriving early and settling slowly. Beyond those two, exactly four named animations exist, all documented with the components they belong to: the live-dot `pulse` (2.4s, infinite), and the three completion gestures `mark-flash` (3s), `draw-check` (1s after an 800ms delay), and `pos-cue` (520ms).

**The One Curve Rule.** Every transition and animation in the system uses `cubic-bezier(0.22, 1, 0.36, 1)`. A second easing curve is a second voice; add duration instead.

**Reduced motion removes the movement, never the message.** Every state this system animates is also carried by fill, weight, an icon, or a label, so under `prefers-reduced-motion` durations collapse and the change simply lands instantly. Two details make that true rather than merely intended: **delays are zeroed along with durations** — `draw-check` waits 800ms, so zeroing only its duration left the checkmark invisible for those 800ms, hiding the confirmation from exactly the people who asked for it plainly — and the checkmark is explicitly set to its drawn state rather than trusting an animation's fill mode.

> An earlier version of this section carried a "150–200ms, opacity/colour/transform only" band that three shipped animations already broke. The band was the thing that was wrong, not the animations: on a surface watched through compressed video, a 3s settle is what makes a change survive the codec. The four named animations are now sanctioned by name in the Don'ts below, and a fifth requires retiring that rule rather than quietly widening it.

## Colors

A small, hand-picked palette tuned for daylight rooms and compressed video. Every neutral is tinted toward the clay accent's hue family (~40° in OKLCH) so the system reads as one warm object rather than a stack of gray rectangles.

### Primary

- **Clay** (`#c9573a`): the single accent. Used for the live indicator dot, focus outlines, the active "host" badge, the drag insertion line, and ≤10% of any surface. Never carries state on its own. Never used as decoration.
- **Clay Deep** (`#a44128`): the pressed and active state for clay-tinted controls, the hover treatment for clay borders, and any place clay must sit *behind* paper-colored text — the up-next tag and the text link both step down to clay-deep so their text clears 4.5:1, which plain clay would not.

### Neutral

- **Paper** (`#faf7f2`): canvas. Page background and the default row surface. Warm enough to read as paper, never sterile.
- **Surface** (`#f3eee5`): the second tonal layer. Stat tiles, the "waiting" callout, the demo-mode bar, and the introduced-row treatment. Sits 2% darker than paper; depth without elevation.
- **Hairline** (`#ddd3c2`): default 1px borders. Visible at desktop, recedes gracefully under compressed video. A border colour only — at 1.39:1 it can never carry text.
- **Soft Line** (`#c8bca6`): emphasized borders. The host row ring, the demo bar, and any divider that needs to read from the back of a conference room. **Borders only.** It previously doubled as the "quieted numeral" ink and the display-size placeholder, where it measured 1.62–1.75:1 and effectively erased the text it set.
- **Hint Ink** (`#9a8e79`): the lightest ink the system allows, at 3.01:1 on paper. It is licensed for exactly three jobs, all of which answer to the 3:1 floor rather than 4.5:1 — the display-size prompt placeholder (large text), the remove glyph (a graphical control), and the input's boundary. Never body text.
- **Muted Ink** (`#756b5c`): secondary text. Timestamps, labels, position numbers, the introduced-row name colour. Set at the lightest value that still clears 4.5:1 on *surface* (4.53:1), which is the tighter of its two backgrounds; on paper it reads 4.90:1.
- **Dim Ink** (`#4a4036`): tertiary text and ghost-button text. Always paired with a paper or surface background.
- **Ink** (`#28201a`): primary text and the primary-button fill. Never `#000`. The brown undertone is what makes the page feel warm even in monochrome moments.

### State Tint

- **Up-Next Tint** (`oklch(96.5% 0.04 44)`): the warm wash behind the up-next roster row, and the only surface in the system that carries chroma above the neutral ceiling. It exists because the room — not the host — has to find the next speaker instantly through compressed video, where a tonal step alone is the first thing the codec eats. Paired with a clay border and a larger position number, never load-bearing on its own.

### Named Rules: Colors

**The Restrained Accent Rule.** Clay covers ≤10% of any rendered screen. If you find yourself reaching for a second accent, you're solving the wrong problem. Add weight, label, or tone instead.

**The Tinted-Neutral Rule.** Every *neutral* carries chroma between **0.007 and 0.033** in OKLCH, in a **hue band of 59–83** — warmer and yellower than clay itself, which sits at hue 35. Pure-gray neutrals are forbidden; they break the warm-paper feel and read as cold against the accent. The Up-Next Tint (chroma 0.04, hue 44) is the one sanctioned exception and is not a neutral: it is a state surface, and adding a second one requires retiring this rule rather than quietly widening it.

> These numbers are measured from the hex tokens, which are normative. An earlier version of this file stated a 0.005–0.022 band at hue 40–50; that was written from intent and never checked, and it excluded three of the very neutrals it governed. If you change a token, re-measure rather than re-estimate — the palette does not sit where a first guess puts it.

**The No-Hue-Borne-State Rule.** Introduced vs. waiting is never carried by hue alone. State pairs fill density (paper vs. surface), weight (regular vs. medium), and an explicit icon. A deuteranopic viewer must distinguish the two on first glance.

**The Clay-Deep-For-Text Rule.** Wherever clay meets text — behind it or *as* it — the darker step does the work. Paper text on plain clay fails 4.5:1, and plain clay as 12px text is 4.00:1, which is the same failure wearing the other hat. Clay-deep passes both directions (5.84:1 on paper), and the two are close enough in hue that nothing reads as a second accent. Plain clay is therefore reserved for what it was always for: borders, the live dot, focus rings, and the up-next numeral at display size, where the 3:1 floor applies.

**The Three-Ink Floor Rule.** Text answers to exactly three inks, and which one is legal depends only on size and role: **ink** and **dim-ink** anywhere, **muted-ink** for anything secondary, and **hint-ink** only for large text or a graphical control. Hairline and soft-line are borders. If a design needs a fourth, lighter ink, what it actually needs is less text.

## Typography

**Display Font:** Atkinson Hyperlegible Next (with system-ui, sans-serif fallback)
**Body Font:** Atkinson Hyperlegible Next (same family, regular weight)
**Numeric Font:** Atkinson Hyperlegible Mono (with ui-monospace fallback) for counts, times, and other tabular data

**Character:** A single humanist sans carries every text role. Atkinson Hyperlegible was drawn by the Braille Institute for readers with low vision, which makes it unusually well suited to a surface whose primary audience is watching through compressed video: the characters that collapse into each other in most sans faces — `I` / `l` / `1`, `O` / `0`, `b` / `d` — are drawn apart on purpose. It reads as warm and slightly informal rather than clinical, which suits a page that sits in the corner of a meeting. The matching mono provides tabular alignment for the counts (3 / 7 / 4) without introducing a second voice.

Both faces ship as variable fonts declaring the full `wght` axis (200–800), so no weight the face can render is clamped away, and both use `font-display: swap` — the roster is readable before the typeface arrives.

### Hierarchy

- **Display** (Atkinson Next, 600, `clamp(2rem, 3.4vw, 2.75rem)`, line-height 1.05, letter-spacing -0.015em): the icebreaker prompt at the top of the page, which doubles as the page title. One per page, ever. It is an editable `textarea` styled to look like nothing — transparent background, no border, no resize handle — so the host types directly into the headline.
- **Headline** (Atkinson Next, 500, 1.25rem, line-height 1.2): the name on the up-next row (at 600), and the first-run welcome title (at 500). Sized up so the room reads the next speaker before the host says anything.
- **Title** (Atkinson Next, 500, 1.0625rem / 17px, line-height 1.3): the roster names. Two points above body because these are the words the room actually reads through a compressed feed; every other text role can afford to be quieter, this one cannot.
- **Body** (Atkinson Next, 400, 0.9375rem / 15px, line-height 1.5): prose — empty-state copy, the coming-up callout, the demo-bar title (at 600). Default for any non-numeric text that isn't a name. Measure is capped between 42ch and 50ch wherever prose runs more than a line.
- **Caption** (Atkinson Next, 400, 0.8125rem / 13px, line-height 1.4): the header meta line, the demo-bar note, empty-state footnotes. Secondary information the host may want and the room can ignore.
- **Label** (Atkinson Next, 500, 0.75rem / 12px, letter-spacing 0.04em): the small roles on stat tiles, buttons, and the introduced toggle. Never used as long-form text. Two tracked variants exist for identity tags: the host label (lowercase, 0.06em) and the `[left]` tag (0.06em).
- **Label Loud** (Atkinson Next, 600, 0.75rem / 12px, letter-spacing 0.05em, uppercase): reserved for the up-next tag, the one uppercase string in the system. Uppercase is the signal of last resort here, used once.
- **Numeric** (Atkinson Mono, 500, 2.25rem / 36px, line-height 1, font-feature `tnum`): the big counts on stat tiles. Tabular figures so widths don't reflow when numbers update. Drops to **Numeric Compact** (1.75rem / 28px) below 640px, where three full-size counts would crowd the row.
- **Numeric Row** (Atkinson Mono, 500, 1.125rem / 18px, font-feature `tnum`): the standing position number on each roster row, right-aligned in its column and `user-select: none` so dragging a row never starts a text selection.
- **Numeric Emphasis** (Atkinson Mono, 600, 1.5rem / 24px, font-feature `tnum`): the position number on the up-next row only. The size step is half the up-next signal; the tint is the other half.
- **Numeric Caption** (Atkinson Mono, 400, 0.8125rem / 13px, font-feature `tnum`): the joined-at timestamp on each row. Mono because it is a number that updates, caption-sized because only the host needs it — and it is the first thing dropped below 640px.

### Named Rules: Typography

**The One-Family Rule.** Atkinson Hyperlegible Next (plus Atkinson Hyperlegible Mono for numerics) is the entire type system. No serif display, no second sans, no icon font carrying glyph weight. Two pairings are retired and must not return: Fraunces + IBM Plex Mono, and the Geist pair that replaced it — the latter was declared but never actually delivered, so the design only existed on machines that happened to have it installed.

**The Tabular Numerics Rule.** Every number that updates live (counts on stat tiles, position numbers, the joined-at timestamp) is rendered in Atkinson Mono with `font-feature-settings: 'tnum'`. Numbers must not reflow their container when they tick.

**The Self-Hosted Type Rule.** The face ships from this repo (`fonts/`, latin subset, ~50KB) and is never fetched from a CDN. Two reasons, and both are binding: a webfont request would break the promise that nothing leaves your machine, and a face that is merely *named* renders only for whoever already has it. If you change the typeface, you ship the file — declaring a family you do not deliver is the bug this rule exists to prevent.

**The Screen-Share Floor Rule.** Body type never goes below 15px. Labels never go below 12px. Anything smaller dies in the 1080p video pipeline. Test by downsampling a screenshot to 1280×720 and reading from 2m away.

**The One Uppercase Rule.** Exactly one string in the system is uppercase: the up-next tag. Uppercase is a shout, and a page shared into a meeting gets one.

## Layout

A single centered column, sized to be read from across a room rather than to fill a monitor.

**Container.** `max-width: 880px`, centered, inside a viewport-relative page gutter of `5vh 5vw` (`4vh 4vw` below 640px). The measure is deliberately narrow for a "dashboard": the room is reading names, and a wider column would push the position number and the name apart until they stopped reading as one row.

**Vertical rhythm.** The page is a stack of blocks separated by generous, deliberately uneven space: header 40px, meta line 22px, stats 28px, callout 22px, demo bar 24px, footer 32px, sponsor bar 32px. Roster rows sit 8px apart — tight enough to read as one list, loose enough that each row keeps its own border.

**The spacing scale** (4 / 8 / 12 / 16 / 20 / 24 / 32 / 48) covers padding and gaps. Several block margins (10, 14, 18, 22, 28, 40) sit off that scale, inherited from tuning against a real screen-share rather than from the token list. Treat the scale as the default for anything new and the off-scale values as measured exceptions, not precedent.

**Grids.** Three grids carry the page, and each collapses once:

- **Stats:** `repeat(3, 1fr)` with a 14px gap; below 640px the gap tightens to 8px, tile padding drops to 12px 14px, and the numerals step down to Numeric Compact. The three counts stay side by side at every width — they are the summary, and stacking them would bury the third.
- **Roster row:** `40px 1fr auto auto auto` (position, name, timestamp, toggle, remove) with a 14px gap. Below 640px it becomes `28px 1fr auto auto`: the position column narrows, the gap tightens to 10px, padding drops to 12px 14px, and the timestamp is dropped outright rather than wrapped.
- **Footer:** `1fr auto` (add-form, actions) with a 20px gap, collapsing to a single column below 640px with the actions left-aligned under the input.

**Sticky prompt.** The prompt sits in a `position: sticky` band at `top: 0` (`z-index: 10`) filled with paper, with a negative top margin so it aligns flush when unpinned. Its bottom border is transparent until the band actually pins, then transitions to hairline — the only chrome that appears on scroll, and the only thing in the system that announces its own stickiness.

**Truncation and measure.** Names truncate with an ellipsis on one line rather than wrapping — a two-line name would break the row grid the room is scanning. Prose is capped by measure, not by pixels: 42ch for the empty lede, 46ch for the footnote, 50ch for the first-run body, with `text-wrap: pretty` on the longest block.

### Named Rules: Layout

**The One Breakpoint Rule.** The system has exactly one breakpoint: 640px. Everything above it is one layout that flexes; everything below is the same layout with one column removed per grid. A second breakpoint means the column was never right.

**The Row-Never-Wraps Rule.** A roster row is one line at every width. When space runs out, drop something — never wrap, never shrink the name below Title size. The give-up order is fixed: **timestamp first, then the up-next tag**, and the name never. Anything `flex: none` sitting inside the name column is a candidate for that list, because it does not shrink — it evicts.

## Elevation & Depth

Flat by default, and now literally so: the stylesheet contains **no `box-shadow` declarations at all**. Depth is conveyed entirely through tonal layering: the canvas is paper, the second layer is surface (a 2% darker warm neutral), and that is the full vocabulary. The previous tracker leaned on radial-gradient atmosphere; that, too, is retired.

The live dot's halo used to be the single exception — an animated `box-shadow` spreading to 9px. It now rides a pseudo-element that scales and fades instead (`scale(1)` → `scale(3.6)`, opacity 0.45 → 0), which looks identical and composites on the GPU rather than repainting the dot every frame. That distinction earns its keep on this surface specifically: the page is screen-shared, and a region that repaints forever denies the video encoder anything static to skip.

### Named Rules: Elevation

**The Flat-By-Default Rule.** Surfaces are flat at rest. If something needs to read as raised, switch its background from paper to surface (tonal layering), don't apply a shadow.

**The No-Decorative-Glow Rule.** Backdrop blurs, soft radial-gradient bloom behind hero text, "glow-on-hover" effects: forbidden. They survive a Figma file; they don't survive a screen-share.

## Shapes

Two radii and one hairline do all the work. The form language is rectangular and calm: nothing is circular except the two status dots, and nothing is sharp-cornered at all.

- **10px (`{rounded.sm}`)** — *containers*: roster rows, stat tiles, the coming-up callout, the demo-mode bar, the empty state. Anything that holds content.
- **6px (`{rounded.xs}`)** — *controls*: buttons, the introduced toggle, the input, the remove button, the text link's focus ring, the up-next tag. Anything you click, plus the one tag that reads as a control-sized object.
- **999px (`{rounded.pill}`)** — used exactly twice: the `[left]` tag, where a pill reads as an annotation rather than a control, and the 7px/8px status dots.

**Borders carry more meaning than radius here.** Every border is 1px, and its color is the signal:

- **Hairline** — the default edge: rows, toggles, inputs, tags, the sponsor link.
- **Soft Line** — emphasis: the host row's ring, the demo-mode bar, and the hover state of a toggle or ghost button.
- **Clay** — attention: the up-next row, a focused input, the drag insertion line, the sponsor link on hover.
- **Dashed hairline** — the one dashed edge in the system: the ordinary empty roster, where a dashed container reads as "space waiting to be filled". The first-run welcome deliberately switches to a *solid* border, because it is content, not an absence.

### Named Rules: Shapes

**The Two-Radius Rule.** Containers get 10px, controls get 6px. A third radius means a component is confused about which it is. The pill is reserved for annotations and dots.

**The Border-Carries-State Rule.** Reach for border color before background color when marking attention: hairline → soft-line → clay is the escalation ladder, and it survives compressed video better than a fill change of the same magnitude.

## Components

### Roster Row

The signature component. One row per participant.

- **Shape:** 10px radius (`{rounded.sm}`), 1px hairline border.
- **Default state:** paper background, ink name, muted-ink timestamp. Reads as a plain ledger entry.
- **Introduced state:** surface background (the 2% darker tonal layer), name shifts to muted-ink with a leading checkmark icon, and the position number and timestamp hold at muted-ink. *No green border, no celebratory color.* The shift in tone is enough to read across the room. The numerals used to drop to soft-line, which read as quieting but measured 1.62:1 — quieting a number until it cannot be read is deleting it.
- **Left state:** paper background, name in dim-ink with a `[left]` pill tag to the right. No opacity tricks.
- **Up-next state:** up-next tint background, clay border, vertical padding grows to 18px, the position number steps to Numeric Emphasis in clay, the name steps to 1.25rem/600, and an uppercase clay-deep tag sits at the end of the row. The roster carries the whole "who's next" signal — this row is why the page needs no separate up-next callout. **The tag is dropped below 640px**: it is `flex: none` inside the name column, so on a narrow row it took the entire column and left the up-next person nameless — the one row that cannot afford it. The tint, the border and the enlarged numeral already say "up next" three times; the name is the part that cannot be inferred.
- **Internal padding:** 14px vertical, 18px horizontal. Column gap: 14px.
- **Host row treatment:** a 1px soft-line ring instead of hairline, plus a small lowercase "host" label in clay-deep after the name, and `cursor: default` because the host is never reorderable. Identity, not status. The ring is reinforcement — the word "host" is what actually carries it — which is why the ring is allowed to sit below the 3:1 non-text floor while the remove glyph is not.
- **Reorder affordance:** reorderable rows carry `cursor: grab` (`grabbing` while dragging) and drop to 40% opacity while lifted. The drop target draws a 2px clay insertion line 5px above or below itself via a pseudo-element that only fades its opacity — the line never displaces a row.
- **Focus:** 2px clay outline at 2px offset, since rows are keyboard-reorderable with ↑/↓.

### Toggle (Mark Introduced)

The host's primary interaction. Always reachable, always cheap.

- **Shape:** 6px radius (`{rounded.xs}`), 1px hairline border, 8px / 14px padding (7px / 10px below 640px).
- **Default:** paper background, muted-ink "Mark introduced" label, label typography (12px, medium weight).
- **Hover:** border darkens to soft-line, text shifts to ink. No color change.
- **On (introduced):** ink fill, paper text and checkmark, ink border. Hover deepens to dim-ink. *The act of marking is unmistakable; the color is neutral.*
- **Focus:** 2px clay outline at 2px offset. Visible against any surface in the system.

### Completion Gesture

The one moment of celebration the system allows, and it is deliberately slow rather than loud. Marking someone introduced fires three coordinated animations:

- **`mark-flash`** (3000ms): the row's background settles from clay-mixed surface (16% clay in OKLAB) through 7% to plain surface. A warm breath, not a flash — long enough that a viewer watching compressed video at 15fps still catches which row changed.
- **`draw-check`** (1000ms, 800ms delay): the checkmark draws itself by animating `stroke-dashoffset` from 100 to 0, landing after the background has begun to settle.
- **`pos-cue`** (520ms, delayed 1800ms): on the row that *becomes* up-next, the position number scales 1 → 1.22 → 1 from its right edge while rising from 55% to full opacity. The delay is what makes this the *third* beat rather than a simultaneous one — it waits out the checkmark (800ms delay + 1000ms draw) instead of racing it. The delay is scoped with `:has(.just-introduced)` to renders that actually contain an introduction, because up-next also changes on a reorder or a departure, and those carry no checkmark to follow: an unconditional delay would strand the cue 1.8s after the gesture that caused it.

**The Sequenced-Not-Simultaneous Rule.** These three fire in a staggered order (background, then check, then the next row's cue). Firing them together would read as a single blink; staggering them lets the room follow the handoff.

### Stat Tile

Three tiles at the top: present count, introduced count, still-to-go count.

- **Shape:** 10px radius, surface background (not paper, so it reads as data rather than a duplicate row).
- **Number:** numeric typography (Atkinson Mono, 36px, tabular). Always ink color; never tinted to match status.
- **Label:** label typography 10px below the number, muted-ink, sentence case.
- **No border.** Tonal contrast with paper is the only delimiter. *Bordered stat tiles read as dashboard; these read as a ledger summary.*
- **Internal padding:** 16px vertical, 20px horizontal (12px / 14px below 640px).

### Buttons

- **Primary (`Add`):** ink fill, ink border, paper text, 6px radius, 10px / 16px padding, label typography. Hover: dim-ink fill and border.
- **Ghost (`Randomize order`, `Reset session`, `Exit demo`):** paper background, dim-ink text, 1px hairline border. Hover: surface background, ink text, soft-line border.
- **Icon-only (remove):** no background or border, 6px padding at every width, which puts the target at exactly 24px. The glyph is hint-ink on a paper row, and **steps up to muted-ink on the introduced and up-next fills** — hint-ink is 3.01:1 on paper but only 2.79:1 on surface and 2.81:1 on the tint, so a single value cannot serve all three. Hover shifts the glyph to clay-deep over a **paper** chip: on those two rows the surface chip is invisible, because surface *is* the row, and the tint sits within 1% of its luminance. The only place a destructive action gets warm, and it stays a tint rather than a red.
- **No fourth button variant.** If you need another level of emphasis, use the text link.

### Text Link

The third emphasis level, used to re-offer the demo after first run.

- **Style:** clay-deep text at caption size (13px, 500), underlined with a 3px underline offset, no background or border, 4px padding — enough to put the hit area at 28px, clear of the 24px minimum.
- **Hover:** darkens to ink, the same direction the sponsor link travels. It used to brighten to clay, which dropped it to 4.00:1 — a hover state should not be the moment a link stops being readable. **Focus:** 2px clay outline at 2px offset.

### Inputs

- **Shape:** 6px radius, 1px **hint-ink** border, paper background. Unlike a button, which announces itself with its own label and fill, a field's boundary is the only thing saying "type here" — so it answers to the 3:1 non-text floor that hairline (1.39:1) cannot meet. This is the one place the system uses a border darker than soft-line.
- **Default:** ink text at body size, muted-ink placeholder, 10px / 14px padding.
- **Focus:** border shifts to clay; no outline ring. The single color shift is the entire focus treatment.
- **Prompt (display-size input):** the exception. A borderless, transparent, non-resizable `textarea` at Display size with a soft-line placeholder at weight 500. Because it has no border to shift, its focus treatment is a 2px clay outline at a generous 6px offset — the ring has to clear 44px-tall type without touching it.
- **No error or disabled states yet** because the surface has no form validation; document them when added.

### Waiting Callout

The "coming up" frame naming who has not been introduced yet.

- **Shape:** 10px radius, surface background (not clay-tinted; that would spotlight the people listed). No border — the tonal step is the whole delimiter, consistent with the stat tiles.
- **Padding:** 14px vertical, 20px horizontal.
- **Text:** body typography in dim-ink. The lead phrase is neutral and present-tense ("Coming up:"), names follow inline at weight 500. Comma-separated; never bulleted.
- **No counter, no time-elapsed, no warning glyph.** This is a prompt to the host, not a public shame board.

### Demo-Mode Bar

A banner that makes sample data unmistakable, so the room never mistakes a demo for a real meeting.

- **Shape:** 10px radius, surface background, 1px **soft-line** border — the emphasized weight, because this is the one message that must not be missed from the back of the room.
- **Content:** an 8px clay dot, a body-size 600-weight title ("Demo mode"), and a caption-size muted-ink note ("Sample data you can play with. Nothing is saved."), with a ghost button to exit at the far end.
- **Padding:** 12px / 16px, 24px below the bar. Wraps rather than truncates on narrow screens.
- *No clay background.* The accent rule holds even here: the dot and the border weight carry the warning.

### Empty & First-Run State

The empty roster is the onboarding surface; it has two forms.

- **Ordinary empty** (a session with nobody in it yet): centered column, muted-ink body text, 48px / 24px padding, 12px gap, and a **dashed** hairline border — space waiting to be filled. Lede capped at 42ch.
- **First run** (this browser has never seen the page): the same block switches to a **solid** hairline border and 48px / 32px padding, because it is content rather than an absence. It carries a headline-size title at weight 500, a dim-ink body at 50ch with `text-wrap: pretty` and a slightly opened 1.55 line-height, a 46ch caption footnote, and the demo call to action.

### Live Dot

- **Shape:** 7px circle, clay fill.
- **Behavior:** a pseudo-element halo scales from the dot to 3.6× and fades out (2.4s loop, ease-out-quint). The only intentional ambient motion in the system, and the only thing on the page that moves without being asked.
- **Composited, not painted.** Transform and opacity keep the halo off the paint path. See Elevation & Depth for why that is a design decision here and not a micro-optimisation.
- **Reduced motion:** the halo is removed entirely and the dot stays solid. Nothing is lost — connection state is also in the adjacent word ("live" / "reconnecting"), which is the only reason the halo is allowed to be decorative in the first place.

### Sponsor Link

- **Style:** a caption-size, 500-weight muted-ink link in a 6px-radius hairline-bordered pill (6px / 12px padding), centered on its own line 32px below the footer.
- **Hover:** text to ink, border to clay.
- **Plain link only.** Never the GitHub sponsors iframe: an embed phones home on every page load, which the privacy promise rules out.

## Do's and Don'ts

### Do

- **Do** use Paper (`#faf7f2`) for the canvas and default row; Surface (`#f3eee5`) as the only second tonal layer. That two-step palette is the entire elevation system.
- **Do** carry the introduced-vs-waiting distinction in *fill density + weight + icon* (paper→surface, regular→muted-ink, no checkmark→checkmark). The state must be legible on a deuteranopic monitor.
- **Do** keep Clay accent under 10% of any rendered screen. Use it for the live dot, focus outlines, the host identity label, the up-next border, and the drag insertion line. Nowhere else.
- **Do** step clay down to clay-deep wherever clay meets text, in either direction — behind paper-coloured text, or set as text itself.
- **Do** measure a colour against the surface it will actually sit on, not against paper by default. Muted-ink reads 4.90:1 on paper but 4.53:1 on surface, and surface is the constraint that sets its value.
- **Do** protect the name before any badge that decorates it. A `flex: none` tag inside the name column does not shrink, it evicts.
- **Do** render every live-updating number in Atkinson Mono with `font-feature-settings: 'tnum'`. Numbers must not reflow their container.
- **Do** keep every transition and animation on `cubic-bezier(0.22, 1, 0.36, 1)`. One curve, varying durations.
- **Do** drop a column before wrapping a roster row: the timestamp goes first, the name never shrinks below Title size.
- **Do** test every screen by downsampling a screenshot to 1280×720 and reading it from 2m away. If you can't read a row name or a count, the type is too small.
- **Do** treat reduced-motion as a hard mode switch: the live dot loses its halo, and every animation and transition is cut to 0.001ms — **delays included** — so the roster updates instantly rather than gently. Check that each animated element's *end* state is what remains; an animation whose meaning lives in its final frame must be pinned there, not left to a fill mode.

### Don't

- **Don't** ship a dark theme variant. The page is screen-shared into lit conference rooms during business hours; dark-mode-by-default is the previous tracker's mistake and a category reflex.
- **Don't** use `#fff` or `#000`. Every neutral is tinted toward the clay hue (chroma 0.005–0.022). Pure gray reads cold against the accent.
- **Don't** use the green-vs-amber state vocabulary the previous tracker shipped with. Color-blind viewers can't distinguish them.
- **Don't** reach for the generic SaaS dashboard idioms PRODUCT.md names: hero-metric tiles with gradient accents, identical icon+heading+text card grids, navy-and-indigo reflex palette.
- **Don't** introduce gamified-leaderboard chrome: avatars, points, badges, "🎉 first to introduce!" animations, ordering by speed. Introductions are not a race; PRODUCT.md is explicit.
- **Don't** mimic Zoom or Slack chrome. The page is shared *inside* Zoom; it should feel like a separate, calmer artifact, not an extension of the host app's UI.
- **Don't** use `border-left` or `border-right` greater than 1px as a colored stripe on rows or callouts. Use full hairline borders or tonal background shifts instead.
- **Don't** put the "still to go" people in a warning-colored frame. PRODUCT.md's "No spotlight on absence" principle forbids it.
- **Don't** add a second breakpoint or a second easing curve. One of each is the system.
- **Don't** animate layout properties, and keep ordinary state transitions in the 140–200ms band. The four named animations (`pulse`, `mark-flash`, `draw-check`, `pos-cue`) are the only sanctioned exceptions to that band, and adding a fifth requires retiring this rule rather than quietly widening it.
- **Don't** uppercase a second string. The up-next tag holds that slot.
- **Don't** set text in hairline or soft-line. They are border colours (1.39:1 and 1.75:1). If text needs to recede, muted-ink is the floor, and hint-ink only when the text is large or the mark is a control.
- **Don't** add an icon font, decorative SVG illustration, or hero image. The page is text and state, by design.
