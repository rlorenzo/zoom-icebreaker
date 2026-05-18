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


def read_zoom_names(bundle, anchor_regex, exclude_re, min_len, debug=False):
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
    names, seen = [], set()
    for t in raw:
        n = clean_name(t)
        if looks_like_name(n, exclude_re, min_len) and n.lower() not in seen:
            seen.add(n.lower())
            names.append(n)
    return names


# --- State -----------------------------------------------------------------
class State:
    def __init__(self):
        self.lock = threading.Lock()
        self.started_at = time.time() * 1000
        self.participants = {}  # id -> dict
        self.clients = set()  # queue.Queue per SSE client

    @staticmethod
    def _id(prefix, name):
        h = hashlib.sha1(name.lower().encode(), usedforsecurity=False).hexdigest()[:12]
        return prefix + h

    def _upsert(self, pid, name):
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
        }
        return True

    def snapshot(self):
        with self.lock:
            return {
                "startedAt": self.started_at,
                "meetingId": None,
                "meetingTopic": None,
                "participants": sorted(
                    (dict(p) for p in self.participants.values()),
                    key=lambda x: x["joinTime"],
                ),
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

    def sync_names(self, names):
        changed = False
        now = time.time() * 1000
        with self.lock:
            seen = set()
            for raw in names:
                nm = str(raw or "").strip()
                if not nm:
                    continue
                pid = self._id("a", nm)
                seen.add(pid)
                if self._upsert(pid, nm):
                    changed = True
            for pid, p in self.participants.items():
                if pid.startswith("a") and pid not in seen and p["present"]:
                    p["present"] = False
                    p["leftTime"] = now
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

    def remove(self, pid):
        with self.lock:
            self.participants.pop(pid, None)
        self.broadcast()

    def reset(self):
        with self.lock:
            self.started_at = time.time() * 1000
            self.participants.clear()
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

    def do_POST(self):
        p = self.path
        if p == "/api/participant":
            name = str(self._read_json().get("name", "")).strip()
            if not name:
                return self._json(400, {"error": "name required"})
            STATE.add_manual(name)
            return self._json(200, {"ok": True})

        if p == "/api/sync":
            names = self._read_json().get("names", [])
            STATE.sync_names(names if isinstance(names, list) else [])
            return self._json(200, {"ok": True, "received": len(names)})

        m = re.match(r"^/api/participant/([^/]+)/introduced$", p)
        if m:
            val = bool(self._read_json().get("introduced"))
            ok = STATE.set_introduced(m.group(1), val)
            return self._json(200 if ok else 404, {"ok": ok})

        m = re.match(r"^/api/participant/([^/]+)/remove$", p)
        if m:
            STATE.remove(m.group(1))
            return self._json(200, {"ok": True})

        if p == "/api/reset":
            STATE.reset()
            return self._json(200, {"ok": True})

        self._json(404, {"error": "not found"})


# --- AX poller thread ------------------------------------------------------
def poller(args, exclude_re):
    pat_warned = False
    while True:
        try:
            names = read_zoom_names(
                args.bundle,
                args.anchor_regex,
                exclude_re,
                args.min_len,
                args.debug,
            )
            if names is None and not pat_warned:
                sys.stderr.write("[ax] Zoom not running yet; will keep checking.\n")
                pat_warned = True
            elif names:
                pat_warned = False
                STATE.sync_names(names)
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
