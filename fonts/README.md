# Bundled typefaces

Both faces are vendored here on purpose. The README promises that nothing
leaves your machine, so the page must not fetch a webfont from a CDN — and
a font declared but never delivered is worse than no font at all, because
the design then only exists on machines that happen to have it installed.

Atkinson Hyperlegible was drawn by the Braille Institute for readers with
low vision: characters that blur together in most sans faces (I/l/1, O/0,
b/d) are deliberately drawn apart. A compressed 720p screen-share degrades
type in much the same way, which is why it is the face here.

| File | Family | Axis | Subset |
| --- | --- | --- | --- |
| `atkinson-next-var-latin.woff2` | Atkinson Hyperlegible Next | `wght` 200–800 | latin |
| `atkinson-mono-var-latin.woff2` | Atkinson Hyperlegible Mono | `wght` 200–800 | latin |

Variable, latin-subset only, ~50 KB for the pair.

## License

Both are licensed under the SIL Open Font License 1.1 — see `OFL.txt`.

- Copyright 2020-2024 The Atkinson Hyperlegible Next Project Authors (https://github.com/googlefonts/atkinson-hyperlegible-next)
- Copyright 2020-2024 The Atkinson Hyperlegible Mono Project Authors (https://github.com/googlefonts/atkinson-hyperlegible-next-mono)

## Updating

Pull the latin woff2 from the Google Fonts `css2` endpoint with a modern
browser User-Agent, then re-vendor. Update the routes in `tracker.py`
(`PAGES`) and the `cp -R fonts` line in `.github/workflows/pages.yml` if the
filenames change.
