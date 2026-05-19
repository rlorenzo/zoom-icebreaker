# PLAN

Working log of what's been done and what's still open. Update as we go.

## Done (on `main`)

### Host detection, reorderable roster, round prompt (commit `6d78f51`)

Auto-detects the meeting host from the Zoom AX panel and pins them to the
top of the list; drag-to-reorder and shuffle for still-to-go participants;
icebreaker prompt shown as the page title and preserved across resets.

### pytest test suite

90 tests, ~71% coverage of `tracker.py`. Covers the name-cleaning helpers,
the `State` class (host promotion, ordering, randomize, sync, reset), and
the HTTP routes via an in-process server. The macOS AX reader and CLI
entry are intentionally uncovered (need real hardware / Zoom).

### CI runs tests

Added a `pytest` step to `.github/workflows/ci.yml`, right after dependency
install so test failures surface before the slower lint steps.

### CI security hardening

- Workflow-level `permissions: contents: read` (least-privilege
  `GITHUB_TOKEN`).
- Third-party actions pinned to SHAs with the version as a trailing
  comment (Dependabot-compatible format).

### Pre-commit hook fixes

- Bandit excludes `tests/` (assertions are pytest's required idiom).
- Cleaned up markdown style in `CONTRIBUTING.md`,
  `.github/PULL_REQUEST_TEMPLATE.md`, and the bug-report issue template
  so the pymarkdown hook passes.

### Repo metadata

Updated GitHub description and topics for discoverability (zoom,
icebreaker, meeting-tools, macos, python, accessibility, self-hosted, sse,
web-ui).

## In flight (this PR)

### Windows support via UI Automation

- `uiautomation>=2.0` added as a Windows-only dependency
  (`sys_platform == 'win32'`).
- Reader refactored into platform-specific functions
  (`_read_zoom_participants_ax`, `_read_zoom_participants_uia`) behind a
  public `read_zoom_participants(args, exclude_re)` dispatcher that
  selects by `sys.platform`.
- `_decide_reader_mode` now produces platform-appropriate error messages
  for macOS, Windows, and unsupported platforms.
- README updated with a Windows install section.

Needs verification on a real Windows machine. The structural pattern
mirrors macOS, but Zoom's exact UIA tree shape (which `ControlTypeName`
values its participant rows expose, exact window `ClassName`, anchor regex
tuning) is something only real testing will confirm. Likely tweaks needed:
the `UIA_TEXT_TYPES` set, the "zoom" substring matching in
`_uia_zoom_windows`, possibly the `--anchor-regex` default.

## Open / next up

### Enable Dependabot

For the `github-actions` ecosystem so the SHA-pinned actions don't go
stale. Minimal config:

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
```

### Possible CLI rename

`--no-ax` is macOS-flavored. A cross-platform name like `--no-auto-read`
or `--manual-only` would read better on Windows. Leave as-is for now to
avoid churn; revisit if Windows users surface confusion.

### Oversize POST body handling

Found during HTTP testing: the handler's `_read_json` checks
`Content-Length > 1MB` but doesn't drain the body before responding, which
resets the client connection. Cosmetic; not exploitable.

### Linux support (AT-SPI)

Deferred unless requested. Zoom's Linux client is less polished and AT-SPI
coverage varies by distro.
