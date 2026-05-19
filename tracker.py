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
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# --- Optional macOS Accessibility support (degrades gracefully) ------------
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

DEFAULT_BUNDLE = "us.zoom.xos"
HERE = os.path.dirname(os.path.abspath(__file__))
INDEX_HTML = os.path.join(HERE, "index.html")

# --- Name cleaning / filtering --------------------------------------------
ANNOT = re.compile(
    r"\s*\((?:host|co-?host|me|guest|you|host,\s*me|cohost,\s*me)\)\s*$",
    re.IGNORECASE,
)
ROLEWORD = re.compile(r"\b(host|co-?host|guest|me|you)\b\s*$", re.IGNORECASE)
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
]


def build_exclude_re(terms):
    ordered = sorted(set(terms), key=len, reverse=True)
    return re.compile(
        r"\b(?:" + "|".join(re.escape(t) for t in ordered) + r")\b",
        re.IGNORECASE,
    )


def clean_name(raw):
    s = raw.strip()
    s = ANNOT.sub("", s)
    s = ROLEWORD.sub("", s).strip(" ,-")
    return s.strip()


def looks_like_name(s, exclude_re, min_len):
    if len(s) < min_len:
        return False
    if exclude_re.search(s):
        return False
    if re.fullmatch(r"[\d\W_]+", s):
        return False
    return len(s) <= 60


# --- Accessibility reading -------------------------------------------------
TEXT_ROLES = {"AXStaticText", "AXCell", "AXButton", "AXRow", "AXTextField"}


def _attr(el, name):
    err, val = AXUIElementCopyAttributeValue(el, name, None)
    return None if err != 0 else val


def _find_pid(bundle_id):
    for app in NSWorkspace.sharedWorkspace().runningApplications():
        if app.bundleIdentifier() == bundle_id:
            return app.processIdentifier()
    return None


def _node_text(el):
    for a in ("AXValue", "AXTitle", "AXDescription"):
        v = _attr(el, a)
        if v is not None and str(v).strip():
            return str(v).strip()
    return ""


def _collect_anchors(el, pat, found, depth=0, counter=None):
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
    if pat.search(hay):
        found.append(el)
        return
    for c in _attr(el, "AXChildren") or []:
        _collect_anchors(c, pat, found, depth + 1, counter)


def _collect_texts(el, out, depth=0, counter=None):
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


def read_zoom_participants(bundle, anchor_regex, exclude_re, min_len, debug=False):
    """Return list of {"name": str, "is_host": bool} or None if Zoom isn't running.

    Host detection runs on the raw AX text BEFORE cleaning, since the
    "(host)" / "(host, me)" annotations are stripped by clean_name.
    """
    pid = _find_pid(bundle)
    if pid is None:
        return None  # Zoom not running
    app_el = AXUIElementCreateApplication(pid)
    pat = re.compile(anchor_regex, re.IGNORECASE)
    anchors = []
    _collect_anchors(app_el, pat, anchors)
    roots = anchors if anchors else [app_el]
    raw = []
    for r in roots:
        _collect_texts(r, raw)
    if debug:
        sys.stderr.write(f"[debug] {len(anchors)} anchor(s), {len(raw)} raw nodes\n")
    people, seen = [], set()
    for t in raw:
        is_host = bool(HOST_DETECT.search(t))
        n = clean_name(t)
        if looks_like_name(n, exclude_re, min_len) and n.lower() not in seen:
            seen.add(n.lower())
            people.append({"name": n, "is_host": is_host})
    return people


# --- State -----------------------------------------------------------------
class State:
    def __init__(self):
        self.lock = threading.Lock()
        self.started_at = time.time() * 1000
        self.participants = {}  # id -> dict
        self.order = []  # list of pids in display order
        self.prompt = ""  # the icebreaker question shown as page title
        self.clients = set()  # queue.Queue per SSE client

    @staticmethod
    def _id(prefix, name):
        h = hashlib.sha1(name.lower().encode(), usedforsecurity=False).hexdigest()[:12]
        return prefix + h

    def _upsert(self, pid, name):
        """Insert or refresh a participant. Order is appended to on first sight."""
        p = self.participants.get(pid)
        if p:
            changed = (
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

    def _current_host(self):
        return next(
            (pid for pid, p in self.participants.items() if p.get("is_host")),
            None,
        )

    def _settle_host(self, host_pid):
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

    def _mark_missing_as_left(self, seen_pids, now):
        """Mark AX-tracked participants no longer in the panel as left."""
        changed = False
        for pid, p in self.participants.items():
            if pid.startswith("a") and pid not in seen_pids and p["present"]:
                p["present"] = False
                p["leftTime"] = now
                changed = True
        return changed

    def snapshot(self):
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

    def broadcast(self):
        data = "data: " + json.dumps(self.snapshot()) + "\n\n"
        for q in list(self.clients):
            with contextlib.suppress(Exception):
                q.put_nowait(data)

    def add_manual(self, name):
        with self.lock:
            self._upsert(self._id("m", name + str(time.time())), name)
        self.broadcast()

    def sync_participants(self, people):
        """`people` is a list of {"name": str, "is_host": bool}."""
        changed = False
        now = time.time() * 1000
        with self.lock:
            seen = set()
            host_pid = None
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

    def set_introduced(self, pid, val):
        with self.lock:
            p = self.participants.get(pid)
            if not p:
                return False
            p["introduced"] = bool(val)
        self.broadcast()
        return True

    def set_host(self, pid, val):
        with self.lock:
            if pid not in self.participants:
                return False
            if val:
                self._settle_host(pid)
            else:
                self.participants[pid]["is_host"] = False
        self.broadcast()
        return True

    def set_prompt(self, prompt):
        with self.lock:
            self.prompt = str(prompt or "").strip()
        self.broadcast()

    def _pin_host(self, order):
        """Return a new list with the current host pinned to index 0."""
        host_pid = self._current_host()
        if host_pid is None:
            return list(order)
        return [host_pid] + [pid for pid in order if pid != host_pid]

    def set_order(self, order_list):
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

    def randomize(self):
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

    def remove(self, pid):
        with self.lock:
            self.participants.pop(pid, None)
            if pid in self.order:
                self.order.remove(pid)
        self.broadcast()

    def reset(self):
        """Clear participants and order; keep the prompt across rounds."""
        with self.lock:
            self.started_at = time.time() * 1000
            self.participants.clear()
            self.order = []
        self.broadcast()


STATE = State()


# --- HTTP + SSE ------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass  # quiet

    def _json(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            if n > 1024 * 1024:  # 1MB limit
                return {}
            return json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return {}

    def do_GET(self):
        if self.path == "/" or self.path.startswith("/index"):
            try:
                with open(INDEX_HTML, "rb") as f:
                    body = f.read()
            except FileNotFoundError:
                return self._json(500, {"error": "index.html missing"})
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if self.path == "/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            q = queue.Queue()
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
                STATE.clients.discard(q)
            return

        self._json(404, {"error": "not found"})

    PARTICIPANT_ROUTE = re.compile(
        r"^/api/participant/([^/]+)/(introduced|host|remove)$"
    )

    def do_POST(self):
        handler = self._STATIC_POST.get(self.path)
        if handler:
            return handler(self)
        m = self.PARTICIPANT_ROUTE.match(self.path)
        if m:
            return self._participant_action(m.group(1), m.group(2))
        self._json(404, {"error": "not found"})

    def _post_add_participant(self):
        name = str(self._read_json().get("name", "")).strip()
        if not name:
            return self._json(400, {"error": "name required"})
        STATE.add_manual(name)
        self._json(200, {"ok": True})

    def _post_prompt(self):
        STATE.set_prompt(str(self._read_json().get("prompt", "")))
        self._json(200, {"ok": True})

    def _post_randomize(self):
        STATE.randomize()
        self._json(200, {"ok": True})

    def _post_order(self):
        order = self._read_json().get("order", [])
        if not isinstance(order, list):
            return self._json(400, {"error": "order must be a list"})
        STATE.set_order([str(x) for x in order])
        self._json(200, {"ok": True})

    def _post_reset(self):
        STATE.reset()
        self._json(200, {"ok": True})

    def _participant_action(self, pid, action):
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


# --- AX poller thread ------------------------------------------------------
def poller(args, exclude_re):
    pat_warned = False
    while True:
        try:
            people = read_zoom_participants(
                args.bundle,
                args.anchor_regex,
                exclude_re,
                args.min_len,
                args.debug,
            )
            if people is None and not pat_warned:
                sys.stderr.write("[ax] Zoom not running yet; will keep checking.\n")
                pat_warned = True
            elif people:
                pat_warned = False
                STATE.sync_participants(people)
        except Exception as e:
            sys.stderr.write(f"[ax] read error: {e}\n")
        time.sleep(args.interval)


def _decide_ax_mode(no_ax):
    if no_ax:
        return False
    if not AX_AVAILABLE:
        sys.stderr.write(
            "\n[ax] pyobjc not available (not on macOS or not installed). "
            "Manual-only mode.\n"
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


def main():
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

    ax_on = _decide_ax_mode(args.no_ax)
    if ax_on:
        threading.Thread(target=poller, args=(args, exclude_re), daemon=True).start()

    mode = (
        f"AUTO (reading Zoom every {args.interval:g}s) + manual"
        if ax_on
        else "MANUAL only"
    )
    srv = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"\n  Icebreaker tracker:  http://localhost:{args.port}")
    print(f"  Mode: {mode}")
    print("  Open the URL and screen-share that tab. Ctrl-C to stop.\n")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
