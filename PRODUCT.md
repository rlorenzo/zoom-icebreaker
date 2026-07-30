# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Two audiences simultaneously, and the design has to serve both:

- **The host** starts the tracker — `uv run tracker.py` locally, or just opening the hosted page — then screen-shares it. They are the only person who clicks anything: toggling "introduced" as each person speaks, occasionally adding a name manually, hitting reset at the end. They are scanning at desktop distance under meeting-attention split.
- **The room** sees the same page via Zoom's screen-share pipeline. They cannot interact; they read. They want to know who has gone, who hasn't, and whether they're up next. Their view is compressed video at 720p–1080p, often on laptops, sometimes on phones.

The host is operating; the room is orienting. Neither is an afterthought.

## Product Purpose

Kill the round-robin awkwardness. In meetings where everyone is expected to introduce themselves, somebody always asks "wait, has Alex gone yet?" and the room loses thirty seconds. This tool makes the answer visible to everyone at once: a live roster, who has been marked introduced, who is still to come.

No Zoom credentials, no SaaS, no account, no history. State lives for the meeting and goes away with it. That ephemerality is deliberate: this is a per-meeting utility, not a CRM.

Success looks like: the host never has to verbally check who's left, the room can self-pace, and the tool is forgotten ten minutes after the meeting ends.

## Positioning

Every neighboring tool that knows who is in a meeting gets there through Zoom's API or SDK — an account, an app registration, OAuth, a marketplace listing standing between the host and their own roster. This one reads the participant list out of the operating system's accessibility tree instead: macOS AX, Windows UI Automation, the same interface a screen reader uses. There is no Zoom account, credential, API key, or app approval anywhere in the product, and nothing leaves the host's machine.

The other half of the position is what it refuses to automate. Marking somebody introduced stays a judgement the host makes as people actually speak. The tool reads presence, never speech; its job is to hold the list, not to decide when a turn is over.

## Operating Context

- A live meeting where introductions go around the room. The host opens the page in a browser and screen-shares that tab; the room reads it through Zoom's compressed video pipeline.
- **Two delivery modes, equal footing.** `uv run tracker.py` serves `http://localhost:3000`, fills the roster from Zoom, and pushes updates to every watching browser over SSE. The same page also runs with no backend at all at `https://rlorenzo.github.io/zoom-icebreaker/`, where names are typed in by hand and held in that browser. Manual entry is a first-class path, not a degraded one.
- Auto-reading requires Zoom's Participants panel to be **open** — that panel is what the reader targets. With it closed the roster stays empty rather than guessing at whatever else is on screen.
- macOS needs Accessibility permission granted to the terminal the command runs from. Windows UIA needs no prompt. Neither platform is a port of the other's behavior; both are supported paths.
- Zoom's accessibility tree is undocumented and changes between versions. Tuning happens at the CLI (`--anchor-regex`, `--exclude`, `--min-len`, `--debug`); diagnosis with `ax_dump.py` on macOS, `tracker.py --debug` on Windows.
- The meeting is the unit of work. A session lasts minutes, and being forgotten afterward is the intended outcome.

## Capabilities and Constraints

Confirmed capabilities:

- A live roster with three counts (in the room / introduced / still to go), one-tap **Mark introduced** per person, and a highlighted up-next row.
- An icebreaker prompt (240 characters) set by the host for the room to answer.
- Order control over the people still to go: drag a row, focus it and press ↑/↓, or **Randomize order**. Anyone already introduced keeps their number.
- Manual add and remove alongside auto-reading; the two mix freely, and `--no-ax` turns reading off entirely.
- **Reset session** clears the roster for the next meeting and keeps the prompt.
- Demo mode with sample data for trying the page without a meeting; leaving it restores the live session.

Constraints future work must preserve:

- **Presence, not speech.** The reader knows who is in the panel, never who has spoken. Transcript ingest is **not planned** — the offer to add one has been removed from the README, and it should not return as a product direction. The host's manual judgement is the feature, not a gap waiting to be automated.
- **No Zoom API or SDK, ever.** The accessibility tree is the only input. This is what keeps the product free of accounts, credentials, and app review.
- Reading an undocumented tree is inherently brittle, and the docs say so rather than papering over it: virtualized participant lists may expose only the names scrolled into view, dial-in participants can appear as phone numbers, and a Zoom redesign can break the matcher.
- **No accounts, history, analytics, or exports.** Nothing is sent anywhere from either delivery mode.
- Terminology is binding: *host*, *the room*, *introduced*, *up next*, *still to go*, *left*. "Introduced" is the state verb — not "done", not "spoken", not "complete".

## Brand Commitments

- **Name:** Icebreaker Tracker in user-facing copy; `zoom-icebreaker` as the repository. The product claims no Zoom affiliation and uses none of Zoom's API, SDK, or branding.
- **Personality:** warm, considered, opinionated. Three words: **calm, deliberate, hospitable.**
- **Voice:** confident and minimal, the way the README reads ("by design", "judgement call", "no Node, no Zoom account, no credentials"). Microcopy frames the experience for the room, not just the host: "coming up next" beats "still hasn't gone."
- **The privacy promise is a build constraint, not a marketing line.** The page makes no third-party request in either delivery mode: the typeface is vendored rather than fetched from a CDN, and sponsorship is a plain text link rather than GitHub's sponsors iframe, which would phone home on every page load.
- MIT licensed. The bundled Atkinson Hyperlegible faces are OFL 1.1.

## Anti-references

- **Generic SaaS dashboard.** Hero metric tiles, gradient accents, identical icon-heading-text card grids, navy-and-indigo reflex palette. Anything that screams "we put your data in a Tremor template."
- **Chat or gamified leaderboard.** Avatars, points, badges, "🎉 first to introduce!" animations, sorting by speed. This tool is the opposite of competitive; introductions are not a race.
- **Zoom / Slack chrome mimicry.** The page is screen-shared inside Zoom, but it should feel like a separate, calmer artifact, not an extension of the host app's UI.

## Evidence on Hand

- `docs/demo.webm` (VP9, generated from demo mode by `npm run record:demo`) and `docs/screenshot-desktop.png` — the README's only visuals, both produced from sample data rather than a real meeting.
- Demo mode's sample roster in `demo.js`, fictional and labelled as such in the UI ("Sample data you can play with. Nothing is saved.").
- Name-filtering tests built from real accessibility captures of live meetings (`tests/test_name_filtering.py`), which is the closest thing the project has to field data.
- Public documents that already state the product's promises: `README.md`, `DESIGN.md`, `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`.
- **Absent, and not to be fabricated:** no user or install counts, no testimonials, no case studies, no press, no customer names or logos, no benchmarks, no pricing or plans (the project is free and MIT), and no sponsors to name.

## Product Principles

1. **Two audiences, one screen — and screen-share is the canonical view.** Every layout, type-scale, and color decision is checked against both the host clicking up close and the room watching through compressed video. When the two conflict, the room wins: desktop legibility comes for free if screen-share works, and the reverse is not true.

2. **No spotlight on absence.** People who haven't introduced themselves yet are "coming up", not "delinquent". No countdown of how long they've waited, no warning colors on their row, no shaming microcopy. The interface helps the host move things along without making anyone feel late.

3. **Per-meeting ephemerality is a feature.** In the local app, state is in memory and resets on process exit. In the backend-less browser build it is kept in that one browser's `localStorage`, so a mid-meeting refresh doesn't lose the slate and **Reset session** clears it — the ceiling is still the meeting you're in. The UI must not imply more than that: no history affordances, no "previous meetings" links, no analytics, no exports. Anything that hints at durable persistence is a lie.

4. **Both ways in are the product.** The zero-install browser build and the local auto-reading app are one product in two delivery modes, not a product and its demo. A change that only works when Zoom can be read is not finished.

5. **One opinionated path.** The host's flow is fixed: roster appears, toggle introduced, reset. Resist settings, modes, and configuration that dilute that flow. CLI flags exist for matcher tuning; the UI itself stays single-purpose.

## Accessibility & Inclusion

- **WCAG AA contrast baseline.** All text and meaningful UI hits 4.5:1 (3:1 for large text), evaluated against the actual surface color, not assumed against black.
- **Color-blind safe state signaling.** Introduced vs. waiting is never carried by green-vs-amber alone. State pairs color with shape, weight, label, or position so a deuteranopic viewer reads it instantly.
- **Screen-share legibility.** The compressed-video pipeline drops fine detail and crushes blacks. Type stays at sizes that survive that loss; thin weights and 1px hairlines are tested against a downsampled preview before they ship.
- **Reduced motion** is honored where motion exists, but motion is never the only carrier of state change. The roster updates are legible without animation.
