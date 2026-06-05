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
import hashlib
import json
import os
import queue
import random
import re
import sys
import threading
import time
from collections.abc import Callable, Iterable
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, ClassVar, TypedDict
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

# Static assets referenced by index.html (extracted from the formerly-inline
# page). Safelisted by exact request path -> (filename, content type) so there
# is no path-traversal surface.
STATIC_FILES: dict[str, tuple[str, str]] = {
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/roster.js": ("roster.js", "text/javascript; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
}

# --- Name cleaning / filtering --------------------------------------------
ANNOT = re.compile(
    r"\s*\((?:host|co-?host|me|guest|you|host,\s*me|cohost,\s*me)\)\s*$",
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
    """
    people: list[Person] = []
    seen: set[str] = set()
    for t in raw:
        is_host = bool(HOST_DETECT.search(t))
        n = clean_name(t)
        if looks_like_name(n, exclude_re, min_len) and n.lower() not in seen:
            seen.add(n.lower())
            people.append({"name": n, "is_host": is_host})
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
    roots = anchors if anchors else [app_el]
    raw: list[str] = []
    for r in roots:
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
    roots = anchors if anchors else windows
    raw: list[str] = []
    for r in roots:
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
class State:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.started_at = time.time() * 1000
        self.participants: dict[str, Participant] = {}  # id -> participant
        self.order: list[str] = []  # list of pids in display order
        self.prompt = ""  # the icebreaker question shown as page title
        self.clients: set[queue.Queue[str]] = set()  # one Queue per SSE client

    @staticmethod
    def _id(prefix: str, name: str) -> str:
        h = hashlib.sha1(name.lower().encode(), usedforsecurity=False).hexdigest()[:12]
        return prefix + h

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
            if pid.startswith("a") and pid not in seen_pids and p["present"]:
                p["present"] = False
                p["leftTime"] = now
                changed = True
        return changed

    def snapshot(self) -> dict[str, object]:
        with self.lock:
            by_id = {pid: dict(p) for pid, p in self.participants.items()}
            ordered = [by_id[pid] for pid in self.order if pid in by_id]
            # Defensive: include any participant not in order at the end.
            for pid, p in by_id.items():
                if pid not in self.order:
                    ordered.append(p)
            return {
                "startedAt": self.started_at,
                "prompt": self.prompt,
                "meetingId": None,
                "meetingTopic": None,
                "participants": ordered,
            }

    def broadcast(self) -> None:
        data = "data: " + json.dumps(self.snapshot()) + "\n\n"
        # Copy under the lock: handler threads add/discard clients concurrently,
        # so iterating the live set could raise "set changed size during iteration".
        with self.lock:
            clients = list(self.clients)
        for q in clients:
            with contextlib.suppress(Exception):
                q.put_nowait(data)

    def add_manual(self, name: str) -> None:
        with self.lock:
            self._upsert(self._id("m", name + str(time.time())), name)
        self.broadcast()

    def sync_participants(self, people: list[Person]) -> bool:
        """`people` is a list of {"name": str, "is_host": bool}."""
        changed = False
        now = time.time() * 1000
        with self.lock:
            seen: set[str] = set()
            host_pid: str | None = None
            for entry in people:
                nm = str(entry.get("name") or "").strip()
                if not nm:
                    continue
                pid = self._id("a", nm)
                seen.add(pid)
                if entry.get("is_host"):
                    host_pid = pid
                if self._upsert(pid, nm):
                    changed = True
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

    def _json(self, code: int, obj: object) -> None:
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    @staticmethod
    def _read_bytes(abspath: str) -> bytes | None:
        try:
            with open(abspath, "rb") as f:
                return f.read()
        except FileNotFoundError:
            return None

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

    def _serve_file(
        self, abspath: str, content_type: str, missing_code: int, missing_msg: str
    ) -> None:
        try:
            body = self._read_bytes(abspath)
        except OSError:
            # PermissionError, IsADirectoryError, etc. — return a controlled
            # JSON error instead of letting the exception drop the connection.
            self._json(500, {"error": "could not read file"})
            return
        if body is None:
            self._json(missing_code, {"error": missing_msg})
        else:
            self._send_ok_bytes(body, content_type)

    def _serve_index(self) -> bool:
        if self.path != "/" and not self.path.startswith("/index"):
            return False
        self._serve_file(
            INDEX_HTML, "text/html; charset=utf-8", 500, "index.html missing"
        )
        return True

    def _serve_static(self) -> bool:
        static = STATIC_FILES.get(self.path)
        if static is None:
            return False
        filename, content_type = static
        # filenames come from the STATIC_FILES safelist, but normalize the
        # resolved path and confirm it stays within HERE so no request-derived
        # value can ever escape the app directory. realpath + startswith is the
        # sanitizer CodeQL's path-injection query recognizes.
        root = os.path.realpath(HERE)
        abspath = os.path.realpath(os.path.join(root, filename))
        if not abspath.startswith(root):
            self._json(404, {"error": "not found"})
            return True
        self._serve_file(abspath, content_type, 404, "not found")
        return True

    def do_GET(self) -> None:
        # self.path includes any query string (e.g. "/app.js?v=123"); match on
        # the path component only so cache-busting params don't 404 the UI.
        self.path = urlsplit(self.path).path
        if self._serve_index() or self._serve_static():
            return

        if self.path == "/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            q: queue.Queue[str] = queue.Queue()
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
def poller(args: argparse.Namespace, exclude_re: re.Pattern[str]) -> None:
    pat_warned = False
    while True:
        try:
            people = read_zoom_participants(args, exclude_re)
            if people is None and not pat_warned:
                sys.stderr.write("[reader] Zoom not running yet; will keep checking.\n")
                pat_warned = True
            elif people:
                pat_warned = False
                STATE.sync_participants(people)
        except Exception as e:
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
