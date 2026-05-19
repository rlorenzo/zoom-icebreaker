---
name: Zoom Icebreaker Tracker
description: A per-meeting utility that shows a whole room who has and hasn't introduced themselves yet.
colors:
  paper: "#faf7f2"
  surface: "#f3eee5"
  hairline: "#ddd3c2"
  soft-line: "#c8bca6"
  muted-ink: "#807666"
  dim-ink: "#4a4036"
  ink: "#28201a"
  clay: "#c9573a"
  clay-deep: "#a44128"
typography:
  display:
    fontFamily: "Geist, Inter, system-ui, sans-serif"
    fontSize: "clamp(2rem, 3.4vw, 2.75rem)"
    fontWeight: 600
    lineHeight: 1.05
    letterSpacing: "-0.015em"
  headline:
    fontFamily: "Geist, Inter, system-ui, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 500
    lineHeight: 1.2
    letterSpacing: "-0.01em"
  body:
    fontFamily: "Geist, Inter, system-ui, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "0"
  label:
    fontFamily: "Geist, Inter, system-ui, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 500
    lineHeight: 1.3
    letterSpacing: "0.04em"
  numeric:
    fontFamily: "Geist Mono, ui-monospace, monospace"
    fontSize: "2.25rem"
    fontWeight: 500
    lineHeight: 1
    letterSpacing: "-0.01em"
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
    padding: "14px 18px"
---

# Design System: Zoom Icebreaker Tracker

## 1. Overview

### Creative North Star: "The Quiet Operator"

A small, considered utility that helps the host of a meeting without performing. Every choice on the page is in service of two simultaneous audiences: the host clicking up close, and the whole room watching the screen-share from across a Zoom feed. Nothing is decorative; nothing competes with the conversation in the room.

The system is light, warm, and restrained. Paper-coded neutrals (faintly warm, never bleached white) carry the canvas. A single sans-serif (Geist) handles every text role; tabular numerics use the matching mono. One accent, clay terracotta, exists for moments of attention (live indicator, focus outlines, identity badges) and is deliberately absent from the state vocabulary itself. State is read through fill density and weight, not color. The design wants to be remembered for *not* getting in the way.

This system explicitly rejects the gravitational pulls of its category: the dark-navy-and-amber dashboard look the current tracker shipped with, the gamified leaderboard chrome (avatars, points, badges), and the generic SaaS hero-metric template. It also rejects the obvious icebreaker-orange reflex; the warm accent here is clay, not pumpkin.

### Key Characteristics

- Light theme, warm paper neutrals, never `#fff`
- Single sans family (Geist), single mono (Geist Mono) for numerics
- One accent (clay), used sparingly and never as a state carrier
- Flat by default: no shadows, tonal layering only
- Restrained motion: state transitions only, never decorative
- Screen-share legibility is the design's first audience

## 2. Colors: The Paper-and-Clay Palette

A small, hand-picked palette tuned for daylight rooms and compressed video. Every neutral is tinted toward the clay accent's hue family (~40° in OKLCH) so the system reads as one warm object rather than a stack of gray rectangles.

### Primary

- **Clay** (`#c9573a` / `oklch(58% 0.14 38)`): the single accent. Used for the live indicator dot, focus outlines, the active "host" badge, and ≤10% of any surface. Never carries state. Never used as decoration.
- **Clay Deep** (`#a44128` / `oklch(48% 0.14 38)`): the pressed and active state for clay-tinted controls. Hover treatment for clay borders.

### Neutral

- **Paper** (`#faf7f2` / `oklch(98% 0.005 50)`): canvas. Page background and the default row surface. Warm enough to read as paper, never sterile.
- **Surface** (`#f3eee5` / `oklch(96% 0.008 50)`): the second tonal layer. Stat tiles, the "waiting" callout, the introduced-row treatment. Sits 2% darker than paper; depth without elevation.
- **Hairline** (`#ddd3c2` / `oklch(88% 0.012 50)`): default 1px borders. Visible at desktop, recedes gracefully under compressed video.
- **Soft Line** (`#c8bca6` / `oklch(80% 0.015 50)`): emphasized borders. Used for the "host" badge ring and any divider that needs to read from the back of a conference room.
- **Muted Ink** (`#807666` / `oklch(50% 0.02 50)`): secondary text. Timestamps, labels, the introduced-row name color.
- **Dim Ink** (`#4a4036` / `oklch(35% 0.018 40)`): tertiary text and ghost-button text. Always paired with a paper or surface background.
- **Ink** (`#28201a` / `oklch(20% 0.022 40)`): primary text and the primary-button fill. Never `#000`. The brown undertone is what makes the page feel warm even in monochrome moments.

### Named Rules: Colors

**The Restrained Accent Rule.** Clay covers ≤10% of any rendered screen. If you find yourself reaching for a second accent, you're solving the wrong problem. Add weight, label, or tone instead.

**The Tinted-Neutral Rule.** Every neutral has chroma between 0.005 and 0.022 in the clay hue family. Pure-gray neutrals are forbidden; they break the warm-paper feel and read as cold against the accent.

**The No-Hue-Borne-State Rule.** Introduced vs. waiting is never carried by hue alone. State pairs fill density (paper vs. surface), weight (regular vs. medium), and an explicit icon. A deuteranopic viewer must distinguish the two on first glance.

## 3. Typography

**Display Font:** Geist (with Inter, system-ui, sans-serif fallback)
**Body Font:** Geist (same family, regular weight)
**Numeric Font:** Geist Mono (with ui-monospace fallback) for counts, times, and other tabular data

**Character:** A single modern humanist sans carries every text role. Geist has wide apertures and a neutral-warm voice; it survives screen-share compression where geometric fonts collapse. The matching mono provides tabular alignment for the meeting counts (3 / 7 / 4) without introducing a second voice.

### Hierarchy

- **Display** (Geist, 600, `clamp(2rem, 3.4vw, 2.75rem)`, line-height 1.05, letter-spacing -0.015em): the page title ("Who's gone yet?"). One per page, ever.
- **Headline** (Geist, 500, 1.25rem, line-height 1.2): used for the "Still to go" callout's lead phrase, when something needs to read between display and body.
- **Body** (Geist, 400, 0.9375rem / 15px, line-height 1.5): the roster names, the waiting list copy. Default for any non-numeric text.
- **Label** (Geist, 500, 0.75rem / 12px, letter-spacing 0.04em): the small uppercase or sentence-case roles on stat tiles, tags, and buttons. Never used as long-form text.
- **Numeric** (Geist Mono, 500, 2.25rem / 36px, line-height 1, font-feature `tnum`): the big counts on stat tiles. Tabular figures so widths don't reflow when numbers update.

### Named Rules: Typography

**The One-Family Rule.** Geist (plus Geist Mono for numerics) is the entire type system. No serif display, no second sans, no icon font carrying glyph weight. The previous Fraunces + IBM Plex Mono pairing is retired; that combination served a different brief.

**The Tabular Numerics Rule.** Every number that updates live (counts on stat tiles, the joined-at timestamp) is rendered in Geist Mono with `font-feature-settings: 'tnum'`. Numbers must not reflow their container when they tick.

**The Screen-Share Floor Rule.** Body type never goes below 15px. Labels never go below 12px. Anything smaller dies in the 1080p video pipeline. Test by downsampling a screenshot to 1280×720 and reading from 2m away.

## 4. Elevation

Flat by default. There are no `box-shadow` declarations in this system. Depth is conveyed entirely through tonal layering: the canvas is paper, the second layer is surface (a 2% darker warm neutral), and that is the full vocabulary. The previous tracker leaned on radial-gradient atmosphere; that, too, is retired.

The only exception is the live-indicator dot, which uses an animated `box-shadow` to draw a pulsing halo. That is a motion treatment for state ("the feed is connected"), not an elevation treatment for hierarchy.

### Named Rules: Elevation

**The Flat-By-Default Rule.** Surfaces are flat at rest. If something needs to read as raised, switch its background from paper to surface (tonal layering), don't apply a shadow.

**The No-Decorative-Glow Rule.** Backdrop blurs, soft radial-gradient bloom behind hero text, "glow-on-hover" effects: forbidden. They survive a Figma file; they don't survive a screen-share.

## 5. Components

### Roster Row

The signature component. One row per participant.

- **Shape:** 10px radius (`{rounded.sm}`), 1px hairline border.
- **Default state:** paper background, ink name, muted-ink timestamp. Reads as a plain ledger entry.
- **Introduced state:** surface background (the 2% darker tonal layer), name shifts to muted-ink with a leading checkmark icon. *No green border, no celebratory color.* The shift in tone is enough to read across the room.
- **Left state:** paper background, name in dim-ink with a `[left]` label tag to the right. No opacity tricks.
- **Internal padding:** 14px vertical, 18px horizontal. Gap between name and trailing controls: 16px.
- **Host row treatment:** a 1px soft-line ring instead of hairline, plus a small "host" clay-text label after the name. Identity, not status.

### Toggle (Mark Introduced)

The host's primary interaction. Always reachable, always cheap.

- **Shape:** 6px radius (`{rounded.xs}`), 1px hairline border, 8px / 14px padding.
- **Default:** paper background, muted-ink "Mark introduced" label, label-typography (12px, medium weight).
- **Hover:** border darkens to soft-line, text shifts to ink. No color change.
- **On (introduced):** ink fill, paper text, leading checkmark glyph. *The act of marking is unmistakable; the color is neutral.*
- **Focus:** 2px clay outline at 2px offset. Visible against any surface in the system.

### Stat Tile

Three tiles at the top: present count, introduced count, still-to-go count.

- **Shape:** 10px radius, surface background (not paper, so it reads as data rather than a duplicate row).
- **Number:** numeric typography (Geist Mono, 36px, tabular). Always ink color; never tinted to match status.
- **Label:** label typography below the number, muted-ink, sentence case.
- **No border.** Tonal contrast with paper is the only delimiter. *Bordered stat tiles read as dashboard; these read as a ledger summary.*
- **Internal padding:** 16px vertical, 20px horizontal.

### Buttons

- **Primary (`Add`, `Reset`):** ink fill, paper text, 6px radius, 10px / 16px padding, label typography. Hover: dim-ink fill. Active: ink fill, slight opacity reduction.
- **Ghost (`Reset session` in low-emphasis contexts):** paper background, dim-ink text, 1px hairline border. Hover: surface background, ink text.
- **No third button variant.** If you need a third level of emphasis, use a text link instead.

### Inputs

- **Shape:** 6px radius, 1px hairline border, paper background.
- **Default:** ink text, muted-ink placeholder, 10px / 14px padding.
- **Focus:** border shifts to clay; no outline ring. The single color shift is the entire focus treatment.
- **No error or disabled states yet** because the surface has no form validation; document them when added.

### Waiting Callout

The "still to go" frame that lists names not yet introduced.

- **Shape:** 10px radius, surface background (not clay-tinted; that would spotlight the people listed), 1px hairline border on the bottom edge only as a separator from any content beneath.
- **Lead phrase:** headline typography ("Coming up: "). Neutral, present-tense.
- **Names:** body weight 500, ink. Comma-separated; never bulleted.
- **No counter, no time-elapsed, no warning glyph.** This is a prompt to the host, not a public shame board.

### Live Dot

- **Shape:** 7px circle, clay fill.
- **Behavior:** pulses via animated `box-shadow` halo (2s loop). The only intentional ambient motion in the system.
- **Reduced motion:** halo animation removed; the dot stays solid. Connection state is also reflected in the adjacent text ("live" / "reconnecting").

## 6. Do's and Don'ts

### Do

- **Do** use Paper
 (`#faf7f2`) for the canvas and default row; Surface (`#f3eee5`) as the only second tonal layer. That two-step palette is the entire elevation system.
- **Do** carry the introduced-vs-waiting distinction in *fill density + weight + icon* (paper→surface, regular→muted-ink, no checkmark→checkmark). The state must be legible on a deuteranopic monitor.
- **Do** keep Clay accent under 10% of any rendered screen. Use it for the live dot, focus outlines, and the host identity label. Nowhere else.
- **Do** render every live-updating number in Geist Mono with `font-feature-settings: 'tnum'`. Numbers must not reflow their container.
- **Do** test every screen by downsampling a screenshot to 1280×720 and reading it from 2m away. If you can't read a row name or a count, the type is too small.
- **Do** treat reduced-motion as a hard mode switch: the live dot stops pulsing, transitions drop to opacity-only, and the roster updates without animation.

### Don't

- **Don't** ship a dark theme variant.
 The page is screen-shared into lit conference rooms during business hours; dark-mode-by-default is the previous tracker's mistake and a category reflex.
- **Don't** use `#fff` or `#000`. Every neutral is tinted toward the clay hue (chroma 0.005–0.022). Pure gray reads cold against the accent.
- **Don't** use the green-vs-amber state vocabulary the previous tracker shipped with. Color-blind viewers can't distinguish them.
- **Don't** reach for the generic SaaS dashboard idioms PRODUCT.md names: hero-metric tiles with gradient accents, identical icon+heading+text card grids, navy-and-indigo reflex palette.
- **Don't** introduce gamified-leaderboard chrome: avatars, points, badges, "🎉 first to introduce!" animations, ordering by speed. Introductions are not a race; PRODUCT.md is explicit.
- **Don't** mimic Zoom or Slack chrome. The page is shared *inside* Zoom; it should feel like a separate, calmer artifact, not an extension of the host app's UI.
- **Don't** use `border-left` or `border-right` greater than 1px as a colored stripe on rows or callouts. Use full hairline borders or tonal background shifts instead.
- **Don't** put the "still to go" people in a warning-colored frame. PRODUCT.md's "No spotlight on absence" principle forbids it.
- **Don't** animate layout properties. Transitions are opacity, color, and transform only, with ease-out-quart at 150–200ms.
- **Don't** add an icon font, decorative SVG illustration, or hero image. The page is text and state, by design.
