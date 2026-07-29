#!/usr/bin/env python3
"""
tracker.py  --  Icebreaker tracker, single local process.

One command. Reads participant names from Zoom's Participants panel via the
macOS Accessibility API and serves the web UI that shows who has introduced
themselves. No Node, no browser automation, no Zoom credentials.

    python3 tracker.py                 # serve UI + auto-read Zoom (if on Mac)
    python3 tracker.py --no-ax         # manual entry only (no Zoom reading)
    python3 tracker.py --interval 5    # re-read the panel every 5s
    python3 tracker.py --port 3000
    python3 tracker.py --anchor-regex 'participants|attendees'
    python3 tracker.py --exclude "pin,spotlight" --debug

Then open http://localhost:3000 and screen-share that browser tab.

If pyobjc is missing or Accessibility permission is not granted, it prints a
notice and runs in manual-only mode. The web UI is fully usable either way.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import queue
import random
import re
import sys
import threading
import time
from collections.abc import Callable, Iterable
from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer
from typing import Any, ClassVar, TypedDict, cast
from urllib.parse import urlsplit

# --- Optional accessibility support (degrades gracefully) ------------------
# macOS: pyobjc + ApplicationServices (AX*)
# Windows: uiautomation (UI Automation / UIA)
# Either backend is optional; if neither is available the app runs in
# manual-only mode (still fully usable).
AX_AVAILABLE = False
try:
    from AppKit import NSWorkspace
    from ApplicationServices import (
        AXIsProcessTrusted,
        AXUIElementCopyAttributeValue,
        AXUIElementCreateApplication,
    )

    AX_AVAILABLE = True
except ImportError:
    pass

UIA_AVAILABLE = False
try:
    import uiautomation as _uia

    UIA_AVAILABLE = True
except ImportError:
    pass


class Person(TypedDict):
    name: str
    is_host: bool


class Participant(TypedDict):
    id: str
    name: str
    joinTime: float
    leftTime: float | None
    present: bool
    introduced: bool
    is_host: bool


DEFAULT_BUNDLE = "us.zoom.xos"
DEFAULT_WIN_PROCESS = "Zoom.exe"
HERE = os.path.dirname(os.path.abspath(__file__))
INDEX_HTML = os.path.join(HERE, "index.html")

# Static assets referenced by index.html, by fixed module-constant absolute path.
APP_JS = os.path.join(HERE, "app.js")
ROSTER_JS = os.path.join(HERE, "roster.js")
DEMO_JS = os.path.join(HERE, "demo.js")
ENGINE_JS = os.path.join(HERE, "engine.js")
SESSION_JS = os.path.join(HERE, "session.js")
STYLES_CSS = os.path.join(HERE, "styles.css")
# Self-hosted so the page makes no third-party request; see styles.css.
FONT_SANS = os.path.join(HERE, "fonts", "atkinson-next-var-latin.woff2")
FONT_MONO = os.path.join(HERE, "fonts", "atkinson-mono-var-latin.woff2")
JS_CONTENT_TYPE = "text/javascript; charset=utf-8"
CSS_CONTENT_TYPE = "text/css; charset=utf-8"
WOFF2_CONTENT_TYPE = "font/woff2"


def _load_bytes(path: str) -> bytes | None:
    """Read a file's bytes once at startup, or None if missing/unreadable.

    Catching OSError here means a missing or unreadable asset degrades to a
    controlled 404/500 at request time instead of raising.
    """
    try:
        with open(path, "rb") as f:
            return f.read()
    except OSError:
        return None


# Every served file is read once, at import, from a constant path. Request
# handling then serves from memory, so no file is ever opened in response to a
# request and no request-derived value can reach a filesystem call (which also
# means there is no path-injection surface at all). Route -> (bytes or None if
# the file was missing/unreadable, content type).
PAGES: dict[str, tuple[bytes | None, str]] = {
    "/app.js": (_load_bytes(APP_JS), JS_CONTENT_TYPE),
    "/roster.js": (_load_bytes(ROSTER_JS), JS_CONTENT_TYPE),
    "/demo.js": (_load_bytes(DEMO_JS), JS_CONTENT_TYPE),
    "/engine.js": (_load_bytes(ENGINE_JS), JS_CONTENT_TYPE),
    "/session.js": (_load_bytes(SESSION_JS), JS_CONTENT_TYPE),
    "/styles.css": (_load_bytes(STYLES_CSS), CSS_CONTENT_TYPE),
    "/fonts/atkinson-next-var-latin.woff2": (
        _load_bytes(FONT_SANS),
        WOFF2_CONTENT_TYPE,
    ),
    "/fonts/atkinson-mono-var-latin.woff2": (
        _load_bytes(FONT_MONO),
        WOFF2_CONTENT_TYPE,
    ),
}
INDEX_BYTES: bytes | None = _load_bytes(INDEX_HTML)

# --- Name cleaning / filtering --------------------------------------------
# Zoom appends the roles a person holds, and it combines them freely:
# "(Host, me)", "(Co-host, Guest)", "(Guest)". Match any comma-separated run of
# role words rather than a fixed list of pairs — an unmatched combination is
# not cosmetic, because the leftover "co-host" then hits DEFAULT_EXCLUDE and
# the attendee is dropped from the roster entirely. Pronouns like "(he/him)"
# deliberately do not match and are preserved.
_ROLE_WORD = r"(?:co-?host|host|guest|panelist|attendee|me|you)"
ANNOT = re.compile(
    rf"\s*\(\s*{_ROLE_WORD}(?:\s*,\s*{_ROLE_WORD})*\s*\)\s*$",
    re.IGNORECASE,
)
ROLEWORD = re.compile(r"\b(host|co-?host|guest|me|you)\b\s*$", re.IGNORECASE)
# Trailing "(N)" counts appear on chat panel section headers
# ("Joined (1)", "Not joined (0)") — not on real names.
COUNT_TAIL = re.compile(r"\s*\(\d+\)\s*$")
# Detects the primary host (not cohost): "(host)" or "(host, me)".
HOST_DETECT = re.compile(r"\(host(?:\s*,\s*me)?\)", re.IGNORECASE)

DEFAULT_EXCLUDE = [
    "mute",
    "unmute",
    "more",
    "invite",
    "raise hand",
    "lower hand",
    "participants",
    "search",
    "chat",
    "share",
    "record",
    "reactions",
    "ask to unmute",
    "rename",
    "remove",
    "host",
    "co-host",
    "cohost",
    "guest",
    "waiting room",
    "admit",
    "everyone",
    "stop video",
    "start video",
    "security",
    "apps",
    "speaker view",
    "gallery view",
    "leave",
    "end meeting",
    "raise",
    "allow",
    "deny",
    "close",
    "pop out",
    "mute all",
    "unmute all",
    # Zoom chat panel chrome that can leak in if the chat panel is
    # adjacent to or shares a subtree with the participants panel.
    "joined",
    "not joined",
    "who can see your messages",
    "see your messages",
    "in this meeting",
    "send to",
    # "participants" alone wouldn't catch "participant(s) sent" — Zoom's
    # delivery indicator. The singular form does, because `(` is a word
    # boundary in regex.
    "participant",
    "panelist",
    "panelists",
]


def build_exclude_re(terms: Iterable[str]) -> re.Pattern[str]:
    ordered = sorted(set(terms), key=len, reverse=True)
    return re.compile(
        r"\b(?:" + "|".join(re.escape(t) for t in ordered) + r")\b",
        re.IGNORECASE,
    )


def clean_name(raw: str) -> str:
    s = raw.strip()
    s = COUNT_TAIL.sub("", s)
    s = ANNOT.sub("", s)
    s = ROLEWORD.sub("", s).strip(" ,-")
    return s.strip()


def looks_like_name(s: str, exclude_re: re.Pattern[str], min_len: int) -> bool:
    if len(s) < min_len:
        return False
    if exclude_re.search(s):
        return False
    if re.fullmatch(r"[\d\W_]+", s):
        return False
    return len(s) <= 60


# --- Accessibility reading -------------------------------------------------
TEXT_ROLES = {"AXStaticText", "AXCell", "AXButton", "AXRow", "AXTextField"}

# Zoom tags every row in the participants panel with what that row *is*, which
# is the only reliable way to tell a person in the meeting from someone merely
# invited. The panel has two sections — "Joined (7)" and "Not joined (2)" — and
# each invitee row carries their RSVP as a sibling text node, so a flattened
# read yields "Emmanuel Arinze" immediately followed by "Accepted", both
# looking exactly like names. Prune these subtrees instead: the section headers
# because they are chrome, the invitees because they are not in the meeting.
#
# Rows we keep are `ZMHCTableItemType_PANELIST`. If Zoom ever renames these,
# pruning simply stops matching and the reader degrades to its old behaviour
# rather than breaking; `--debug` will show the node count jump.
SKIP_CELL_IDS = frozenset(
    {
        "ZMHCTableItemType_Invitee",  # a person who has NOT joined
        "ZMHCTableItemType_Invitee_Group",  # the "Not joined (N)" header
        "ZMHCTableItemType_PANELIST_Group",  # the "Joined (N)" header
    }
)

# Zoom's chat panel has a recipient picker that mentions "participants",
# so it can match the participant anchor regex. We reject anchors that
# look like chat so the harvester doesn't slurp up chat-panel labels
# (e.g. "Joined (N)", "Who can see your messages") as participant names.
CHAT_HINT_RE = re.compile(r"\bchat\b", re.IGNORECASE)


def _attr(el: Any, name: str) -> Any:
    err, val = AXUIElementCopyAttributeValue(el, name, None)
    return None if err != 0 else val


def _find_pid(bundle_id: str) -> int | None:
    for app in NSWorkspace.sharedWorkspace().runningApplications():
        if app.bundleIdentifier() == bundle_id:
            return int(app.processIdentifier())
    return None


def _node_text(el: Any) -> str:
    for a in ("AXValue", "AXTitle", "AXDescription"):
        v = _attr(el, a)
        if v is not None and str(v).strip():
            return str(v).strip()
    return ""


def _is_chat_anchor_ax(el: Any) -> bool:
    # Match the same attribute set _collect_anchors builds `hay` from, so a
    # "chat" hint in AXDescription/AXHelp also rejects the anchor.
    for a in (
        "AXTitle",
        "AXDescription",
        "AXRoleDescription",
        "AXHelp",
        "AXIdentifier",
    ):
        v = _attr(el, a)
        if v and CHAT_HINT_RE.search(str(v)):
            return True
    return False


def _collect_anchors(
    el: Any,
    pat: re.Pattern[str],
    found: list[Any],
    depth: int = 0,
    counter: list[int] | None = None,
) -> None:
    counter = counter or [0]
    if counter[0] >= 8000 or depth > 40:
        return
    counter[0] += 1
    hay = " ".join(
        str(_attr(el, a) or "")
        for a in (
            "AXTitle",
            "AXDescription",
            "AXRoleDescription",
            "AXHelp",
            "AXIdentifier",
        )
    )
    if pat.search(hay) and not _is_chat_anchor_ax(el):
        found.append(el)
        return
    for c in _attr(el, "AXChildren") or []:
        _collect_anchors(c, pat, found, depth + 1, counter)


def _collect_texts(
    el: Any,
    out: list[str],
    depth: int = 0,
    counter: list[int] | None = None,
) -> None:
    counter = counter or [0]
    if counter[0] >= 6000 or depth > 40:
        return
    counter[0] += 1
    if str(_attr(el, "AXIdentifier") or "") in SKIP_CELL_IDS:
        return
    if _attr(el, "AXRole") in TEXT_ROLES:
        t = _node_text(el)
        if t:
            out.append(t)
    for c in _attr(el, "AXChildren") or []:
        _collect_texts(c, out, depth + 1, counter)


def _filter_and_dedupe(
    raw: Iterable[str], exclude_re: re.Pattern[str], min_len: int
) -> list[Person]:
    """Common post-processing: clean names, detect host, dedupe.

    Host detection runs on the raw text BEFORE cleaning, since the
    "(host)" / "(host, me)" annotations are stripped by clean_name.

    KNOWN LIMITATION: the dedupe is global across the harvested nodes, so two
    real participants sharing a display name arrive downstream as one person.
    It cannot simply be dropped: TEXT_ROLES spans row, cell and static-text
    nodes, so a single participant is normally harvested several times over
    and a raw list would multiply everybody. Telling "same person, three
    nodes" apart from "two people, one name" needs a row-aware harvest, which
    is the fix this layer is missing — State._assign_ax_pids already keeps
    repeated names on separate rows once they get past here.
    """
    people: list[Person] = []
    seen: dict[str, int] = {}  # lowercased name -> index into `people`
    for t in raw:
        is_host = bool(HOST_DETECT.search(t))
        n = clean_name(t)
        if not looks_like_name(n, exclude_re, min_len):
            continue
        idx = seen.get(n.lower())
        if idx is None:
            seen[n.lower()] = len(people)
            people.append({"name": n, "is_host": is_host})
        elif is_host:
            # Only one of the nodes harvested for a row carries "(host)", and
            # it is not reliably the first one: an AXRow whose own text is the
            # bare name can precede the AXStaticText that has the annotation.
            # Keeping the flag here stops node order from deciding who's host.
            people[idx]["is_host"] = True
    return people


def _read_zoom_participants_ax(
    args: argparse.Namespace, exclude_re: re.Pattern[str]
) -> list[Person] | None:
    """macOS reader. Returns list[Person] or None if Zoom isn't running."""
    pid = _find_pid(args.bundle)
    if pid is None:
        return None
    app_el = AXUIElementCreateApplication(pid)
    pat = re.compile(args.anchor_regex, re.IGNORECASE)
    anchors: list[Any] = []
    _collect_anchors(app_el, pat, anchors)
    if not anchors:
        # No participants panel anywhere in the tree. Harvesting the whole app
        # instead would scrape Zoom's own chrome: with no meeting open, every
        # toolbar button ("History", "Create new", "Open activity center") is
        # an AXButton with a description, and AXButton is a text role — so the
        # roster fills with the app's UI. No panel means no participants, and
        # an exclude list can never keep up with one vendor's button labels.
        if args.debug:
            sys.stderr.write("[ax] no participants panel found; reporting none\n")
        return []
    raw: list[str] = []
    for r in anchors:
        _collect_texts(r, raw)
    if args.debug:
        sys.stderr.write(f"[ax] {len(anchors)} anchor(s), {len(raw)} raw nodes\n")
    return _filter_and_dedupe(raw, exclude_re, args.min_len)


# --- Windows UI Automation reading -----------------------------------------
# UIA control types whose Name is typically a participant or text label.
UIA_TEXT_TYPES = {
    "TextControl",
    "ListItemControl",
    "DataItemControl",
    "ButtonControl",
    "EditControl",
}


def _uia_zoom_windows() -> list[Any]:
    """Return top-level Zoom windows. Empty if Zoom isn't running."""
    try:
        desktop = _uia.GetRootControl()
    except Exception:
        return []
    found: list[Any] = []
    for w in desktop.GetChildren():
        try:
            cls = (w.ClassName or "").lower()
            name = (w.Name or "").lower()
            if "zoom" in cls or "zoom" in name:
                found.append(w)
        except Exception:  # nosec B112 — UIA/COM can raise on some windows; skip them
            continue
    return found


def _uia_node_text(el: Any) -> str:
    """Best-effort text extraction from a UIA element."""
    for attr in ("Name", "AutomationId"):
        v = getattr(el, attr, None)
        if v and str(v).strip():
            return str(v).strip()
    return ""


def _is_chat_anchor_uia(el: Any) -> bool:
    # Match the same attribute set _uia_collect_anchors builds `hay` from, so a
    # "chat" hint in HelpText also rejects the anchor.
    for a in ("Name", "LocalizedControlType", "AutomationId", "HelpText"):
        v = getattr(el, a, None)
        if v and CHAT_HINT_RE.search(str(v)):
            return True
    return False


def _uia_collect_anchors(
    el: Any,
    pat: re.Pattern[str],
    found: list[Any],
    depth: int = 0,
    counter: list[int] | None = None,
) -> None:
    counter = counter or [0]
    if counter[0] >= 8000 or depth > 40:
        return
    counter[0] += 1
    hay = " ".join(
        str(getattr(el, a, "") or "")
        for a in ("Name", "LocalizedControlType", "AutomationId", "HelpText")
    )
    if pat.search(hay) and not _is_chat_anchor_uia(el):
        found.append(el)
        return
    try:
        children = el.GetChildren()
    except Exception:
        return
    for c in children:
        _uia_collect_anchors(c, pat, found, depth + 1, counter)


def _uia_collect_texts(
    el: Any,
    out: list[str],
    depth: int = 0,
    counter: list[int] | None = None,
) -> None:
    counter = counter or [0]
    if counter[0] >= 6000 or depth > 40:
        return
    counter[0] += 1
    ctrl_type = getattr(el, "ControlTypeName", "") or ""
    if ctrl_type in UIA_TEXT_TYPES:
        t = _uia_node_text(el)
        if t:
            out.append(t)
    try:
        children = el.GetChildren()
    except Exception:
        return
    for c in children:
        _uia_collect_texts(c, out, depth + 1, counter)


def _read_zoom_participants_uia(
    args: argparse.Namespace, exclude_re: re.Pattern[str]
) -> list[Person] | None:
    """Windows reader. Returns list[Person] or None if Zoom isn't running."""
    windows = _uia_zoom_windows()
    if not windows:
        return None
    pat = re.compile(args.anchor_regex, re.IGNORECASE)
    anchors: list[Any] = []
    for w in windows:
        _uia_collect_anchors(w, pat, anchors)
    if not anchors:
        # Same reasoning as the macOS reader: no panel means no participants,
        # not "scrape the whole window".
        if args.debug:
            sys.stderr.write("[uia] no participants panel found; reporting none\n")
        return []
    raw: list[str] = []
    for r in anchors:
        _uia_collect_texts(r, raw)
    if args.debug:
        sys.stderr.write(f"[uia] {len(anchors)} anchor(s), {len(raw)} raw nodes\n")
    return _filter_and_dedupe(raw, exclude_re, args.min_len)


# --- Reader dispatch -------------------------------------------------------
def read_zoom_participants(
    args: argparse.Namespace, exclude_re: re.Pattern[str]
) -> list[Person] | None:
    """Dispatch to the right backend based on platform. None == Zoom not running."""
    if sys.platform == "darwin" and AX_AVAILABLE:
        return _read_zoom_participants_ax(args, exclude_re)
    if sys.platform == "win32" and UIA_AVAILABLE:
        return _read_zoom_participants_uia(args, exclude_re)
    return None


# --- State -----------------------------------------------------------------
# A participant id carries its origin in the first character: "a" for a name
# read off Zoom's panel, "m" for one typed in by hand. Only auto-read rows are
# reconciled against a panel read — a manual row must never be marked left just
# because Zoom cannot see it.
AX_PREFIX = "a"
MANUAL_PREFIX = "m"


class State:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.started_at = time.time() * 1000
        self.participants: dict[str, Participant] = {}  # id -> participant
        self.order: list[str] = []  # list of pids in display order
        self.prompt = ""  # the icebreaker question shown as page title
        self.clients: set[queue.Queue[str]] = set()  # one Queue per SSE client
        self._broadcast_lock = threading.Lock()  # serialises snapshot -> fan-out
        self._seq = 0  # monotonic counter behind every participant id

    @staticmethod
    def _is_ax(pid: str) -> bool:
        """Whether `pid` was read off Zoom's panel rather than typed in."""
        return pid.startswith(AX_PREFIX)

    def _new_id(self, prefix: str) -> str:
        """Mint a fresh participant id (see AX_PREFIX / MANUAL_PREFIX).

        Deliberately NOT derived from the name. Zoom's panel is only a list of
        display names, so hashing the name made the name the identity: two
        people called "John Smith" collapsed onto one row, and renaming
        yourself mid-meeting replaced your row with a stranger's. The counter
        is never reset (not even by reset()) so an id is never reused.

        The duplicate-name half of that only holds from sync_participants()
        inward. The AX/UIA readers still collapse repeated names before they
        reach here (see _filter_and_dedupe), so a second "John Smith" arrives
        today only via a manual add or a direct API call.
        """
        self._seq += 1
        return f"{prefix}{self._seq:x}"

    def _ax_name_pool(self) -> dict[str, list[str]]:
        """Existing auto-read participants, bucketed by lowercased name."""
        pool: dict[str, list[str]] = {}
        for pid, p in self.participants.items():
            if self._is_ax(pid):
                pool.setdefault(p["name"].lower(), []).append(pid)
        return pool

    def _vanished_present(self, claimed: set[str]) -> list[str]:
        """Present auto-read participants who did not show up in this read."""
        return [
            pid
            for pid, p in self.participants.items()
            if self._is_ax(pid) and pid not in claimed and p["present"]
        ]

    def _apply_rename(self, paired: list[tuple[str | None, str]]) -> None:
        """Rebind the one new name that is really a rename, if there is one.

        Only a one-for-one swap counts: exactly one present participant
        vanished from the panel and exactly one unfamiliar name took their
        place, leaving a single possible pairing. With two or more on either
        side the pairing would be a guess, and guessing wrong carries
        somebody's introduced checkmark over to the wrong person — so those
        are left alone as an ordinary leave plus join.

        Even the one-for-one case is a judgement call: one person leaving and
        a different one joining inside the same poll is indistinguishable from
        a rename here. Renames are much the commoner event at this
        granularity, so they win, and the cost of being wrong is a single
        checkmark on the wrong row that the host can clear.
        """
        claimed = {pid for pid, _ in paired if pid is not None}
        vanished = self._vanished_present(claimed)
        fresh = [i for i, (pid, _) in enumerate(paired) if pid is None]
        if len(vanished) == 1 and len(fresh) == 1:
            paired[fresh[0]] = (vanished[0], paired[fresh[0]][1])

    def _assign_ax_pids(self, names: list[str]) -> list[str]:
        """Resolve each panel name to a stable participant id.

        Names are matched against existing auto-read participants one-for-one
        and each match is consumed, so repeated display names stay on separate
        rows instead of collapsing. Whoever is left over is either a rename
        (see _apply_rename) or genuinely new.
        """
        pool = self._ax_name_pool()
        paired: list[tuple[str | None, str]] = []
        for nm in names:
            bucket = pool.get(nm.lower())
            paired.append((bucket.pop(0) if bucket else None, nm))
        self._apply_rename(paired)
        return [pid or self._new_id(AX_PREFIX) for pid, _ in paired]

    @staticmethod
    def _named_entries(people: list[Person]) -> list[tuple[Person, str]]:
        """Drop blank names, pairing each surviving entry with its clean name."""
        named: list[tuple[Person, str]] = []
        for entry in people:
            nm = str(entry.get("name") or "").strip()
            if nm:
                named.append((entry, nm))
        return named

    def _upsert_read(
        self, named: list[tuple[Person, str]], pids: list[str]
    ) -> tuple[bool, set[str], str | None]:
        """Insert or refresh everyone in one panel read.

        Returns (anything changed, the ids seen this read, the host's id).
        """
        changed = False
        seen: set[str] = set()
        host_pid: str | None = None
        for (entry, nm), pid in zip(named, pids, strict=True):
            seen.add(pid)
            if entry.get("is_host"):
                host_pid = pid
            if self._upsert(pid, nm):
                changed = True
        return changed, seen, host_pid

    def _upsert(self, pid: str, name: str) -> bool:
        """Insert or refresh a participant. Order is appended to on first sight."""
        p = self.participants.get(pid)
        if p:
            changed = bool(
                not p["present"]
                or p["leftTime"] is not None
                or (name and name != p["name"])
            )
            p["present"] = True
            p["leftTime"] = None
            if name:
                p["name"] = name
            return changed
        self.participants[pid] = {
            "id": pid,
            "name": name or "Guest",
            "joinTime": time.time() * 1000,
            "leftTime": None,
            "present": True,
            "introduced": False,
            "is_host": False,
        }
        if pid not in self.order:
            self.order.append(pid)
        return True

    def _current_host(self) -> str | None:
        return next(
            (pid for pid, p in self.participants.items() if p.get("is_host")),
            None,
        )

    def _settle_host(self, host_pid: str) -> bool:
        """Promote `host_pid` to sole host (most-recent wins) and pin to order[0]."""
        changed = False
        for ppid, p in self.participants.items():
            should_be = ppid == host_pid
            if bool(p.get("is_host")) != should_be:
                p["is_host"] = should_be
                changed = True
        if host_pid in self.order and self.order[0] != host_pid:
            self.order.remove(host_pid)
            self.order.insert(0, host_pid)
            changed = True
        return changed

    def _mark_missing_as_left(self, seen_pids: set[str], now: float) -> bool:
        """Mark AX-tracked participants no longer in the panel as left."""
        changed = False
        for pid, p in self.participants.items():
            if self._is_ax(pid) and pid not in seen_pids and p["present"]:
                p["present"] = False
                p["leftTime"] = now
                changed = True
        return changed

    def snapshot(self) -> dict[str, object]:
        with self.lock:
            by_id = {pid: dict(p) for pid, p in self.participants.items()}
            ordered = [by_id[pid] for pid in self.order if pid in by_id]
            # Defensive: include any participant not in order at the end.
            # (Set membership: `pid in self.order` per participant would make
            # every snapshot O(n^2) under the lock.)
            in_order = set(self.order)
            for pid, p in by_id.items():
                if pid not in in_order:
                    ordered.append(p)
            return {
                "startedAt": self.started_at,
                "prompt": self.prompt,
                "meetingId": None,
                "meetingTopic": None,
                "participants": ordered,
            }

    def broadcast(self) -> None:
        # One broadcast at a time, end to end. Taking the snapshot and handing
        # it to the clients are two separate lock acquisitions, so without this
        # a poller sync and a host's click can interleave: the newer snapshot
        # reaches a queue first and the older one lands behind it, leaving that
        # client displaying stale state. It does not self-heal either, because
        # sync_participants only broadcasts when something actually changed —
        # a quiet meeting would keep the wrong roster on screen indefinitely.
        #
        # A separate lock rather than making self.lock reentrant: broadcast is
        # always called with self.lock released, so the order here is only ever
        # _broadcast_lock -> lock, and self.lock keeps its non-reentrant
        # discipline (holding it across a broadcast would deadlock, loudly).
        with self._broadcast_lock:
            data = "data: " + json.dumps(self.snapshot()) + "\n\n"
            # Copy under the lock: handler threads add/discard clients
            # concurrently, so iterating the live set could raise "set changed
            # size during iteration".
            with self.lock:
                clients = list(self.clients)
            for q in clients:
                # Make room by dropping the OLDEST frame: every message is a
                # full snapshot, so the newest is the only one that matters and
                # discarding it would leave the client stale forever.
                with contextlib.suppress(queue.Empty, queue.Full):
                    if q.full():
                        q.get_nowait()
                    q.put_nowait(data)

    def add_manual(self, name: str) -> None:
        with self.lock:
            self._upsert(self._new_id(MANUAL_PREFIX), name)
        self.broadcast()

    def sync_participants(self, people: list[Person]) -> bool:
        """`people` is a list of {"name": str, "is_host": bool}."""
        now = time.time() * 1000
        with self.lock:
            named = self._named_entries(people)
            pids = self._assign_ax_pids([nm for _, nm in named])
            changed, seen, host_pid = self._upsert_read(named, pids)
            if host_pid is not None and self._settle_host(host_pid):
                changed = True
            if self._mark_missing_as_left(seen, now):
                changed = True
        if changed:
            self.broadcast()
        return changed

    def set_introduced(self, pid: str, val: bool) -> bool:
        with self.lock:
            p = self.participants.get(pid)
            if not p:
                return False
            p["introduced"] = bool(val)
        self.broadcast()
        return True

    def set_host(self, pid: str, val: bool) -> bool:
        with self.lock:
            if pid not in self.participants:
                return False
            if val:
                self._settle_host(pid)
            else:
                self.participants[pid]["is_host"] = False
        self.broadcast()
        return True

    def set_prompt(self, prompt: str) -> None:
        with self.lock:
            self.prompt = str(prompt or "").strip()
        self.broadcast()

    def _pin_host(self, order: Iterable[str]) -> list[str]:
        """Return a new list with the current host pinned to index 0."""
        host_pid = self._current_host()
        if host_pid is None:
            return list(order)
        return [host_pid] + [pid for pid in order if pid != host_pid]

    def set_order(self, order_list: list[str]) -> bool:
        """Apply a host-pinned order. Unknown ids drop; missing ids tack on."""
        with self.lock:
            # dict.fromkeys() filters to known pids and dedups in one pass.
            filtered = dict.fromkeys(
                pid for pid in order_list if pid in self.participants
            )
            for pid in self.participants:
                filtered.setdefault(pid, None)
            self.order = self._pin_host(filtered)
        self.broadcast()
        return True

    def randomize(self) -> None:
        """Shuffle still-to-go participants only; introduced people keep slots."""
        with self.lock:
            host_pid = self._current_host()
            non_host = [pid for pid in self.order if pid != host_pid]
            pool = [
                pid for pid in non_host if not self.participants[pid].get("introduced")
            ]
            random.shuffle(pool)
            it = iter(pool)
            shuffled = [
                pid if self.participants[pid].get("introduced") else next(it)
                for pid in non_host
            ]
            self.order = ([host_pid] if host_pid else []) + shuffled
        self.broadcast()

    def remove(self, pid: str) -> None:
        with self.lock:
            self.participants.pop(pid, None)
            if pid in self.order:
                self.order.remove(pid)
        self.broadcast()

    def reset(self) -> None:
        """Clear participants and order; keep the prompt across rounds."""
        with self.lock:
            self.started_at = time.time() * 1000
            self.participants.clear()
            self.order = []
        self.broadcast()


STATE = State()


# --- HTTP + SSE ------------------------------------------------------------
# Binding to 127.0.0.1 keeps other machines out, but not other *pages*: while
# the tracker is running, any site open in the host's browser can post to
# localhost, and a text/plain body skips the CORS preflight that would
# otherwise block it. A forged Host header is the DNS-rebinding version of the
# same trick, and would expose the roster to a read as well. So every request
# has to name this server in Host, and any Origin it carries must be our exact
# origin -- scheme, host and port, since the port is what separates us from
# whatever else the user has running on localhost.
ALLOWED_HOSTS = frozenset({"localhost", "127.0.0.1", "::1"})

# Each SSE message is a complete snapshot, so a backed-up client only ever
# needs the newest one. Bounding the queue stops a stalled reader (a laptop
# asleep with the tab open) from growing it without limit.
SSE_QUEUE_MAX = 32


class QuietHTTPServer(ThreadingHTTPServer):
    """ThreadingHTTPServer that ignores benign client-disconnect errors.

    Browsers refresh, SSE clients navigate away, and tabs close: any of
    these can tear a socket while the server is mid-read. Python's stock
    `BaseHTTPRequestHandler.handle_one_request` lets the resulting
    ConnectionResetError / BrokenPipeError bubble up to the server's
    error handler, which prints a noisy traceback. These aren't bugs.
    """

    def handle_error(self, request: Any, client_address: Any) -> None:
        exc = sys.exc_info()[1]
        if isinstance(exc, (ConnectionResetError, BrokenPipeError, TimeoutError)):
            return
        super().handle_error(request, client_address)


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    # Bound after the class body (handlers must exist as attributes first).
    _STATIC_POST: ClassVar[dict[str, Callable[[Handler], None]]]

    def log_message(self, format: str, *args: Any) -> None:
        pass  # quiet

    @staticmethod
    def _hostname(value: str) -> str | None:
        """Host out of a `Host:` authority or an `Origin:` URL, or None.

        urlsplit already does the port-stripping, IPv6 de-bracketing and
        case-folding that hand-rolled splitting keeps getting wrong
        ("[::1]:8000", "LOCALHOST"). A malformed header raises ValueError;
        anything we cannot parse is treated as untrusted.
        """
        with contextlib.suppress(ValueError):
            return urlsplit(value if "//" in value else f"//{value}").hostname
        return None

    def _origin_is_ours(self, origin: str) -> bool:
        """Whether an `Origin:` URL is this exact server, port included.

        A browser origin is (scheme, host, port), so hostname alone is not
        enough: http://localhost:9999 is some *other* local app, and matching
        on "localhost" would hand it our whole POST API. The loopback names
        are not interchangeable either -- 127.0.0.1 and ::1 are distinct
        origins that can hold distinct servers on the same port -- so the
        Origin host must be the very name this request was addressed to
        rather than merely an allowed one. Host is only trusted for that
        comparison because _is_local_request() has already pinned it to
        ALLOWED_HOSTS; the port is still taken from the socket we are bound
        to, never from the client's claim. Origin carries no port when it is
        the scheme default, hence the 80 fallback.
        """
        with contextlib.suppress(ValueError):
            parts = urlsplit(origin)
            host = self._hostname(self.headers.get("Host", ""))
            if parts.scheme != "http" or host is None or parts.hostname != host:
                return False
            # self.server is typed as the generic BaseServer; every server we
            # construct is an HTTPServer, which is what defines server_port.
            return (parts.port or 80) == cast(HTTPServer, self.server).server_port
        return False

    def _is_local_request(self) -> bool:
        """Whether this request really came from a page this server served.

        See ALLOWED_HOSTS. Requests without an Origin (a plain address-bar
        navigation, curl, EventSource reconnects on some browsers) are fine;
        it is a *mismatched* Origin that means another site is driving us.
        """
        if self._hostname(self.headers.get("Host", "")) not in ALLOWED_HOSTS:
            return False
        origin = self.headers.get("Origin")
        return origin is None or self._origin_is_ours(origin)

    def _json(self, code: int, obj: object) -> None:
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_ok_bytes(self, body: bytes, content_type: str) -> None:
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict[str, Any]:
        try:
            n = int(self.headers.get("Content-Length", 0))
            if n > 1024 * 1024:  # 1MB limit
                # Body is left unread; close the connection so the unconsumed
                # bytes can't desync the next request on this keep-alive socket.
                self.close_connection = True
                return {}
            data = json.loads(self.rfile.read(n) or b"{}")
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _serve_index(self) -> bool:
        if self.path != "/" and not self.path.startswith("/index"):
            return False
        if INDEX_BYTES is None:
            self._json(500, {"error": "index.html missing"})
        else:
            self._send_ok_bytes(INDEX_BYTES, "text/html; charset=utf-8")
        return True

    def _serve_static(self) -> bool:
        page = PAGES.get(self.path)
        if page is None:
            return False
        body, content_type = page
        if body is None:
            self._json(404, {"error": "not found"})
        else:
            self._send_ok_bytes(body, content_type)
        return True

    def do_GET(self) -> None:
        # self.path includes any query string (e.g. "/app.js?v=123"); match on
        # the path component only so cache-busting params don't 404 the UI.
        self.path = urlsplit(self.path).path
        if not self._is_local_request():
            return self._json(403, {"error": "forbidden"})
        if self._serve_index() or self._serve_static():
            return

        if self.path == "/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            q: queue.Queue[str] = queue.Queue(maxsize=SSE_QUEUE_MAX)
            with STATE.lock:
                STATE.clients.add(q)
            try:
                self.wfile.write(
                    ("data: " + json.dumps(STATE.snapshot()) + "\n\n").encode()
                )
                self.wfile.flush()
                while True:
                    try:
                        msg = q.get(timeout=15)
                        self.wfile.write(msg.encode())
                    except queue.Empty:
                        self.wfile.write(b": keepalive\n\n")
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError, OSError):
                pass
            finally:
                with STATE.lock:
                    STATE.clients.discard(q)
            return

        self._json(404, {"error": "not found"})

    PARTICIPANT_ROUTE = re.compile(
        r"^/api/participant/([^/]+)/(introduced|host|remove)$"
    )

    def do_POST(self) -> None:
        # Strip any query string before route matching (see do_GET).
        self.path = urlsplit(self.path).path
        if not self._is_local_request():
            return self._json(403, {"error": "forbidden"})
        handler = self._STATIC_POST.get(self.path)
        if handler:
            return handler(self)
        m = self.PARTICIPANT_ROUTE.match(self.path)
        if m:
            return self._participant_action(m.group(1), m.group(2))
        self._json(404, {"error": "not found"})

    def _post_add_participant(self) -> None:
        name = str(self._read_json().get("name", "")).strip()
        if not name:
            return self._json(400, {"error": "name required"})
        STATE.add_manual(name)
        self._json(200, {"ok": True})

    def _post_prompt(self) -> None:
        STATE.set_prompt(str(self._read_json().get("prompt", "")))
        self._json(200, {"ok": True})

    def _post_randomize(self) -> None:
        STATE.randomize()
        self._json(200, {"ok": True})

    def _post_order(self) -> None:
        order = self._read_json().get("order", [])
        if not isinstance(order, list):
            return self._json(400, {"error": "order must be a list"})
        STATE.set_order([str(x) for x in order])
        self._json(200, {"ok": True})

    def _post_reset(self) -> None:
        STATE.reset()
        self._json(200, {"ok": True})

    def _participant_action(self, pid: str, action: str) -> None:
        if action == "introduced":
            ok = STATE.set_introduced(pid, bool(self._read_json().get("introduced")))
        elif action == "host":
            ok = STATE.set_host(pid, bool(self._read_json().get("host")))
        else:  # remove
            STATE.remove(pid)
            ok = True
        self._json(200 if ok else 404, {"ok": ok})


# Bind route table after the class body so handlers exist as attributes.
Handler._STATIC_POST = {
    "/api/participant": Handler._post_add_participant,
    "/api/prompt": Handler._post_prompt,
    "/api/randomize": Handler._post_randomize,
    "/api/order": Handler._post_order,
    "/api/reset": Handler._post_reset,
}


# --- Reader poller thread --------------------------------------------------
# One empty read is ambiguous: the meeting may have ended (everyone should be
# marked as left), but the host may also have just closed the participants
# panel or Zoom repainted mid-read. Require a few consecutive empty reads
# before treating "no names" as authoritative; a reopened panel revives
# everyone on the next non-empty read either way.
EMPTY_READS_TO_CLEAR = 3


def poller(args: argparse.Namespace, exclude_re: re.Pattern[str]) -> None:
    pat_warned = False
    empty_reads = 0
    while True:
        try:
            people = read_zoom_participants(args, exclude_re)
            if people is None:
                # Zoom not running is not an empty panel: only truly
                # consecutive empty successful reads may clear the roster.
                empty_reads = 0
                if not pat_warned:
                    sys.stderr.write(
                        "[reader] Zoom not running yet; will keep checking.\n"
                    )
                    pat_warned = True
            else:
                pat_warned = False
                empty_reads = 0 if people else empty_reads + 1
                if people or empty_reads >= EMPTY_READS_TO_CLEAR:
                    STATE.sync_participants(people)
        except Exception as e:
            empty_reads = 0  # a failed read says nothing about the panel
            sys.stderr.write(f"[reader] read error: {e}\n")
        time.sleep(args.interval)


def _decide_reader_mode(no_ax: bool) -> bool:
    """Decide whether to start the auto-reader thread.

    Returns True if a per-platform accessibility backend is available and
    permission has been granted; False (with a stderr explainer) otherwise.
    """
    if no_ax:
        return False
    if sys.platform == "darwin":
        if not AX_AVAILABLE:
            sys.stderr.write(
                "\n[ax] pyobjc not available. Manual-only mode.\n"
                "     For auto-reading: uv sync\n"
            )
            return False
        if not AXIsProcessTrusted():
            sys.stderr.write(
                "\n[ax] Accessibility permission NOT granted. Running in "
                "manual-only mode.\n"
                "     Grant it in System Settings > Privacy & Security > "
                "Accessibility\n"
                "     to the app you run this from (Terminal/iTerm), then "
                "reopen it.\n"
            )
            return False
        return True
    if sys.platform == "win32":
        if not UIA_AVAILABLE:
            sys.stderr.write(
                "\n[uia] uiautomation not available. Manual-only mode.\n"
                "     For auto-reading: uv sync\n"
            )
            return False
        return True
    sys.stderr.write(
        "\n[reader] Auto-read is only supported on macOS and Windows. "
        "Running in manual-only mode.\n"
    )
    return False


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=3000)
    ap.add_argument("--bundle", default=DEFAULT_BUNDLE)
    ap.add_argument("--interval", type=float, default=5.0)
    ap.add_argument("--anchor-regex", default="participant")
    ap.add_argument("--exclude", default="")
    ap.add_argument("--min-len", type=int, default=2)
    ap.add_argument(
        "--no-ax", action="store_true", help="manual entry only; do not read Zoom"
    )
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args()

    exclude_re = build_exclude_re(
        DEFAULT_EXCLUDE + [x.strip() for x in args.exclude.split(",") if x.strip()]
    )

    reader_on = _decide_reader_mode(args.no_ax)
    if reader_on:
        threading.Thread(target=poller, args=(args, exclude_re), daemon=True).start()

    mode = (
        f"AUTO (reading Zoom every {args.interval:g}s) + manual"
        if reader_on
        else "MANUAL only"
    )
    srv = QuietHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"\n  Icebreaker tracker:  http://localhost:{args.port}")
    print(f"  Mode: {mode}")
    print("  Open the URL and screen-share that tab. Ctrl-C to stop.\n")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
