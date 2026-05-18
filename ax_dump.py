#!/usr/bin/env python3
"""
ax_dump.py  --  Reconnaissance tool.

Prints the macOS Accessibility (AX) tree of the running Zoom app so you can
SEE where (and whether) participant names are exposed before writing an
extractor against them. Zoom's tree is undocumented and changes between
versions, so always run this first.

Usage:
    python3 ax_dump.py                 # dump Zoom, default depth 14
    python3 ax_dump.py --depth 20
    python3 ax_dump.py --bundle us.zoom.xos
    python3 ax_dump.py --grep -i part  # only print branches matching a regex
    python3 ax_dump.py --max-nodes 8000

Tips:
    1. Start/join a meeting and OPEN the Participants panel first.
    2. Run this, then search the output for a name you can see on screen.
    3. Note the chain of AXRole / AXIdentifier / AXDescription values that
       leads to the names. That chain is what ax_participants.py targets.
"""

import argparse
import re
import sys

try:
    from AppKit import NSWorkspace
    from ApplicationServices import (
        AXIsProcessTrusted,
        AXUIElementCopyAttributeValue,
        AXUIElementCreateApplication,
    )
except ImportError:
    sys.exit(
        "pyobjc is not installed. From this folder run:\n"
        "  python3 -m venv .venv && source .venv/bin/activate\n"
        "  pip install -r requirements.txt\n"
    )

DEFAULT_BUNDLE = "us.zoom.xos"

# Attributes worth showing for each node. Strings are used directly so this
# works across pyobjc versions without importing kAX* constants.
SHOW_ATTRS = [
    "AXRole",
    "AXSubrole",
    "AXRoleDescription",
    "AXTitle",
    "AXDescription",
    "AXValue",
    "AXIdentifier",
    "AXHelp",
    "AXSelectedText",
]


def get_attr(element, name):
    err, value = AXUIElementCopyAttributeValue(element, name, None)
    if err != 0:
        return None
    return value


def find_pid(bundle_id):
    for app in NSWorkspace.sharedWorkspace().runningApplications():
        if app.bundleIdentifier() == bundle_id:
            return app.processIdentifier()
    return None


def short(v, limit=120):
    s = str(v).replace("\n", " ").strip()
    return s if len(s) <= limit else s[: limit - 1] + "…"


def describe(element):
    parts = []
    for a in SHOW_ATTRS:
        v = get_attr(element, a)
        if v is not None and str(v).strip() != "":
            parts.append(f"{a}={short(v)!r}")
    return "  ".join(parts) if parts else "(no readable attributes)"


def walk(element, depth, max_depth, counter, max_nodes, pattern, lines, prefix=""):
    if counter[0] >= max_nodes or depth > max_depth:
        return
    counter[0] += 1
    line = f"{prefix}{describe(element)}"
    lines.append((depth, line))
    children = get_attr(element, "AXChildren") or []
    for child in children:
        walk(
            child,
            depth + 1,
            max_depth,
            counter,
            max_nodes,
            pattern,
            lines,
            prefix + "  ",
        )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", default=DEFAULT_BUNDLE)
    ap.add_argument("--depth", type=int, default=14)
    ap.add_argument("--max-nodes", type=int, default=6000)
    ap.add_argument(
        "--grep",
        nargs="+",
        default=None,
        help="only print nodes whose line matches this regex "
        "(prefix -i for case-insensitive, e.g. --grep -i participant)",
    )
    args = ap.parse_args()

    if not AXIsProcessTrusted():
        sys.exit(
            "\nThis process is NOT trusted for Accessibility.\n"
            "Grant it in: System Settings > Privacy & Security > Accessibility\n"
            "Add the app you run this FROM (Terminal, iTerm, or your Python\n"
            "binary), toggle it on, then fully quit and reopen that app.\n"
        )

    pid = find_pid(args.bundle)
    if pid is None:
        sys.exit(
            f"No running app with bundle id {args.bundle!r}. "
            "Is Zoom open and in a meeting?"
        )

    app_el = AXUIElementCreateApplication(pid)
    lines = []
    walk(app_el, 0, args.depth, [0], args.max_nodes, None, lines)

    pattern = None
    if args.grep:
        toks = list(args.grep)
        flags = 0
        if toks and toks[0] == "-i":
            flags = re.IGNORECASE
            toks = toks[1:]
        pattern = re.compile(" ".join(toks), flags)

    printed = 0
    for _depth, line in lines:
        if pattern is None or pattern.search(line):
            print(line)
            printed += 1

    sys.stderr.write(
        f"\n[{len(lines)} nodes scanned, {printed} printed. "
        f"Search this output for a participant's visible name.]\n"
    )


if __name__ == "__main__":
    main()
