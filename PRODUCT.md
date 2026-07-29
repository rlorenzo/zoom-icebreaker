# Product

## Register

product

## Users

Two audiences simultaneously, and the design has to serve both:

- **The host** runs `uv run tracker.py` (or just opens the hosted page), then screen-shares it. They are the only person who clicks anything: toggling "introduced" as each person speaks, occasionally adding a name manually, hitting reset at the end. They are scanning at desktop distance under meeting-attention split.
- **The room** sees the same page via Zoom's screen-share pipeline. They cannot interact; they read. They want to know who has gone, who hasn't, and whether they're up next. Their view is compressed video at 720p–1080p, often on laptops, sometimes on phones.

The host is operating; the room is orienting. Neither is an afterthought.

## Product Purpose

Kill the round-robin awkwardness. In meetings where everyone is expected to introduce themselves, somebody always asks "wait, has Alex gone yet?" and the room loses thirty seconds. This tool makes the answer visible to everyone at once: a live roster, who has been marked introduced, who is still to come.

It runs as one local process — or, for a host who won't install anything, as the same page served statically with no backend at all, where the roster is typed in by hand instead of read from Zoom. Either way: no Zoom credentials, no SaaS, no account, no history. State lives for the meeting and goes away with it. That ephemerality is deliberate: this is a per-meeting utility, not a CRM.

Success looks like: the host never has to verbally check who's left, the room can self-pace, and the tool is forgotten ten minutes after the meeting ends.

## Brand Personality

Warm, considered, opinionated. Three words: **calm, deliberate, hospitable.**

Voice: confident and minimal, the way the README already reads ("by design", "judgement call", "no Node, no Zoom account, no credentials"). Microcopy frames the experience for the room, not just the host: "coming up next" beats "still hasn't gone."

Aesthetic direction: Linear / Vercel polish, but warmer. Modern tool feel, rounded type, generous air. Not terminal-coded; not editorial-magazine; not corporate dashboard. Closer to a tasteful product page that happens to be functional during a meeting.

## Anti-references

- **Generic SaaS dashboard.** Hero metric tiles, gradient accents, identical icon-heading-text card grids, navy-and-indigo reflex palette. Anything that screams "we put your data in a Tremor template."
- **Chat or gamified leaderboard.** Avatars, points, badges, "🎉 first to introduce!" animations, sorting by speed. This tool is the opposite of competitive; introductions are not a race.
- **Zoom / Slack chrome mimicry.** The page is screen-shared inside Zoom, but it should feel like a separate, calmer artifact, not an extension of the host app's UI.

## Design Principles

1. **Two audiences, one screen.** Every layout, type-scale, and color decision is checked against both the host clicking up close and the room watching via compressed video. If a choice only works for one, it isn't done.

2. **No spotlight on absence.** People who haven't introduced themselves yet are "coming up", not "delinquent". No countdown of how long they've waited, no warning colors on their row, no shaming microcopy. The interface helps the host move things along without making anyone feel late.

3. **Screen-share is the canonical view.** Optimize for what survives the 720p–1080p compressed video pipeline first: large type, generous contrast, state changes that don't rely on motion. Desktop legibility comes for free if screen-share works.

4. **Per-meeting ephemerality is a feature.** In the local app, state is in memory and resets on process exit. In the backend-less browser build it is kept in that one browser's `localStorage`, so a mid-meeting refresh doesn't lose the slate and **Reset session** clears it — the ceiling is still the meeting you're in. The UI must not imply more than that: no history affordances, no "previous meetings" links, no analytics, no exports. Anything that hints at durable persistence is a lie.

5. **One opinionated path.** The host's flow is fixed: roster appears, toggle introduced, reset. Resist settings, modes, and configuration that dilute that flow. CLI flags exist for matcher tuning; the UI itself stays single-purpose.

## Accessibility & Inclusion

- **WCAG AA contrast baseline.** All text and meaningful UI hits 4.5:1 (3:1 for large text), evaluated against the actual surface color, not assumed against black.
- **Color-blind safe state signaling.** Introduced vs. waiting is never carried by green-vs-amber alone. State pairs color with shape, weight, label, or position so a deuteranopic viewer reads it instantly.
- **Screen-share legibility.** The compressed-video pipeline drops fine detail and crushes blacks. Type stays at sizes that survive that loss; thin weights and 1px hairlines are tested against a downsampled preview before they ship.
- **Reduced motion** is honored where motion exists, but motion is never the only carrier of state change. The roster updates are legible without animation.
