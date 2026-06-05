# Icebreaker Tracker

A live webpage that tracks who has introduced themselves in a meeting. It
reads the Zoom Participants panel automatically (macOS and Windows) and
gives you a one-tap "introduced" toggle per person. Screen-share the page
so everyone sees who still needs to go.

One process, one command. No Node, no Zoom account, no credentials.

## Run it

```bash
uv sync
uv run tracker.py
```

Open <http://localhost:3000> and screen-share that browser tab.

- On macOS with Accessibility granted, or on Windows with the UIA backend
  installed, it auto-reads Zoom's Participants panel every few seconds and
  fills the roster for you.
- Anywhere else (or without permission) it runs in manual-only mode: type
  names in yourself. The webpage is identical either way.

You can always mix both: let it auto-read and still add or remove people by
hand. The "introduced" toggle is always manual, by design, because that is a
judgement call only you can make as people speak.

## Auto-reading Zoom (macOS)

Auto-read needs pyobjc and macOS Accessibility permission. Install via
[uv](https://docs.astral.sh/uv/):

```bash
uv sync
```

Grant Accessibility permission to the app you run this FROM (Terminal or
iTerm), in System Settings > Privacy & Security > Accessibility, then reopen
that terminal. Start a meeting, open the Participants panel, then run
`uv run tracker.py`.

Zoom's accessibility tree is undocumented and changes between versions, so
if names do not appear, run the recon tool to see what Zoom exposes and tune
the matcher:

```bash
uv run ax_dump.py --grep '(?i)participant'
uv run tracker.py --anchor-regex 'participants|attendees' --debug
```

Known limitations: virtualized participant lists may only expose names that
are currently scrolled into view, and dial-in users sometimes appear as
phone numbers rather than names.

## Auto-reading Zoom (Windows)

Auto-read on Windows uses [UI Automation](https://learn.microsoft.com/en-us/windows/win32/winauto/entry-uiauto-win32)
via the `uiautomation` Python package, which is installed automatically by
`uv sync`. No additional permission prompt is required (UIA is part of the
standard Windows accessibility stack).

Start a meeting, open the Participants panel, then run `uv run tracker.py`.
The same `--anchor-regex`, `--exclude`, and `--debug` flags work the same
way as on macOS; the `--bundle` flag is macOS-only and is ignored on
Windows (the reader finds the Zoom window by class/title).

## Options

```text
--port N          default 3000
--interval N      seconds between Zoom reads (default 5)
--no-ax           manual entry only, never read Zoom
--anchor-regex    text identifying the participants container
--exclude "a,b"   extra whole-word non-name terms to filter
--min-len N       minimum name length (default 2)
--debug           print anchor/raw-node diagnostics
```

## During a meeting

1. python3 tracker.py, open the URL, share that tab in Zoom.
2. People appear automatically (or add them manually). "Tracking since" is
   when you started the session.
3. Tap "Mark introduced" after each person speaks. The counts and the
   "still waiting on" banner update live for everyone watching the share.
4. "Reset session" clears it for the next meeting.

## Notes

- State is in memory and resets when you stop the process. Intentional for
  a per-meeting tool.
- This only reads your screen's UI tree; it never interacts with Zoom, so
  it does not touch Zoom's API or SDK terms. It can still break if Zoom
  redesigns the panel; re-run ax_dump.py and adjust --anchor-regex.
- Reads who is present, not who has spoken. For an automatic "who has
  actually spoken" signal, a saved Zoom transcript is the better source;
  ask if you want that ingest added.

## Development

```bash
uv sync --dev                # install dev tools
uv run pre-commit install    # enable git hook
uv run pre-commit run --all  # run all checks once
```

Tooling: ruff (lint + format), bandit (security), lizard (complexity),
pymarkdown (markdown). The same checks run on every PR via
[`.github/workflows/ci.yml`](.github/workflows/ci.yml).

The web assets (`index.html`, `app.js`, `roster.js`, `styles.css`) are read
into memory once at startup, so the server never opens a file in response to a
request. The trade-off is that editing any of them requires restarting the
server (Ctrl-C and re-run) to see the change.
