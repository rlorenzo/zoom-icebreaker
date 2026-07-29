"""End-to-end tests for the HTTP handler — spin up the real server on an
ephemeral port and hit it with urllib (no extra deps)."""

import json
import re
import threading
import urllib.error
import urllib.request

import pytest

import tracker
from tracker import STATE, Handler, QuietHTTPServer


@pytest.fixture
def server():
    """Run the real handler on 127.0.0.1:<random> for the test, then tear down.

    QuietHTTPServer (not a bare ThreadingHTTPServer) because that is what
    serve() runs: a plain one prints a traceback when an SSE client hangs up
    mid-stream, which is exactly the disconnect it exists to swallow.
    """
    STATE.reset()
    STATE.set_prompt("")
    srv = QuietHTTPServer(("127.0.0.1", 0), Handler)
    port = srv.server_address[1]
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        srv.shutdown()
        srv.server_close()
        t.join(timeout=2)


def _open(req):
    """urlopen, but only over http(s) so a stray file:/// or ftp:// URL can't
    reach the local filesystem (the reason bandit flags urlopen as B310)."""
    url = req.full_url if isinstance(req, urllib.request.Request) else req
    if not url.startswith(("http://", "https://")):
        raise ValueError(f"refusing non-http(s) URL: {url}")
    return urllib.request.urlopen(req, timeout=5)  # nosec B310 — scheme checked above


def _req(method, url, body=None):
    data = None
    headers = {}
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with _open(req) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def _post(url, body=None):
    code, raw = _req("POST", url, body or {})
    return code, (json.loads(raw) if raw else None)


def _get(url):
    code, raw = _req("GET", url)
    return code, raw


def _get_full(url):
    """GET returning (status, content-type, body) for asset/header checks."""
    req = urllib.request.Request(url, method="GET")
    with _open(req) as resp:
        return resp.status, resp.headers.get("Content-Type"), resp.read()


class TestGetRoot:
    def test_serves_index_html(self, server):
        code, raw = _get(server + "/")
        assert code == 200
        assert b"<html" in raw.lower() or b"<!doctype" in raw.lower()

    def test_index_path_alias(self, server):
        code, _ = _get(server + "/index.html")
        assert code == 200

    def test_unknown_get_returns_404(self, server):
        code, _ = _get(server + "/api/bogus")
        assert code == 404

    def test_missing_index_html(self, server, monkeypatch):
        # A missing index.html (no preloaded bytes) yields a controlled 500.
        monkeypatch.setattr(tracker, "INDEX_BYTES", None)
        code, raw = _get(server + "/")
        assert code == 500
        assert b"index.html missing" in raw


class TestStaticAssets:
    def test_serves_app_js(self, server):
        code, ctype, raw = _get_full(server + "/app.js")
        assert code == 200
        assert "javascript" in ctype
        assert raw  # non-empty body

    def test_serves_roster_js(self, server):
        code, ctype, raw = _get_full(server + "/roster.js")
        assert code == 200
        assert "javascript" in ctype
        assert raw

    def test_serves_demo_js(self, server):
        code, ctype, raw = _get_full(server + "/demo.js")
        assert code == 200
        assert "javascript" in ctype
        assert raw

    def test_serves_engine_js(self, server):
        code, ctype, raw = _get_full(server + "/engine.js")
        assert code == 200
        assert "javascript" in ctype
        assert raw

    def test_serves_session_js(self, server):
        code, ctype, raw = _get_full(server + "/session.js")
        assert code == 200
        assert "javascript" in ctype
        assert raw

    def test_serves_styles_css(self, server):
        code, ctype, raw = _get_full(server + "/styles.css")
        assert code == 200
        assert "css" in ctype
        assert raw

    @pytest.mark.parametrize(
        "path",
        [
            "/fonts/atkinson-next-var-latin.woff2",
            "/fonts/atkinson-mono-var-latin.woff2",
        ],
    )
    def test_serves_self_hosted_fonts(self, server, path):
        # The typeface ships from this repo rather than a CDN (see styles.css).
        # If these stop being served the page silently drops to system-ui and
        # the documented type system quietly stops existing — which is exactly
        # the bug the self-hosting was introduced to fix.
        code, ctype, raw = _get_full(server + path)
        assert code == 200
        assert ctype == "font/woff2"
        assert raw[:4] == b"wOF2"  # real woff2 magic bytes, not an error page

    def test_stylesheet_requests_no_third_party_font(self, server):
        # Every url() has to be repo-relative, not just the first one: the
        # README promises nothing leaves your machine, and one CDN @font-face
        # further down the file would break that just as thoroughly.
        _, _, raw = _get_full(server + "/styles.css")
        css = raw.decode()
        assert "@font-face" in css  # the face is actually delivered...
        urls = re.findall(r"url\(\s*['\"]?([^'\")]+)", css)
        assert urls  # ...and the regex is really finding the references
        assert all(not u.startswith(("http:", "https:", "//")) for u in urls), urls

    def test_missing_static_asset_returns_404(self, server, monkeypatch):
        # A safelisted route whose asset failed to load (no bytes) 404s.
        monkeypatch.setitem(tracker.PAGES, "/app.js", (None, tracker.JS_CONTENT_TYPE))
        code, _ = _get(server + "/app.js")
        assert code == 404

    def test_only_exact_safelisted_paths_are_served(self, server):
        # Dispatch is exact-match: source files and near-miss paths are never
        # served, so there is no arbitrary-file-read surface.
        for path in (
            "/tracker.py",
            "/ax_dump.py",
            "/app.jsx",
            "/styles.cssx",
            "/roster",
        ):
            code, _ = _get(server + path)
            assert code == 404, path

    def test_serves_static_asset_with_query_string(self, server):
        # Cache-busting query params must not bypass the static handler.
        code, ctype, raw = _get_full(server + "/app.js?v=123")
        assert code == 200
        assert "javascript" in ctype
        assert raw

    def test_serves_index_with_query_string(self, server):
        code, raw = _get(server + "/?v=1")
        assert code == 200
        assert b"<html" in raw.lower() or b"<!doctype" in raw.lower()

    def test_loader_returns_none_on_io_error(self):
        # _load_bytes degrades missing/unreadable files to None (served as a
        # controlled 404/500) instead of raising. A directory triggers an
        # OSError (IsADirectoryError); a nonexistent path a FileNotFoundError.
        assert tracker._load_bytes(tracker.HERE) is None
        assert tracker._load_bytes(tracker.HERE + "/does-not-exist.xyz") is None


class TestPostQueryString:
    def test_post_route_ignores_query_string(self, server):
        code, body = _post(server + "/api/randomize?x=1")
        assert code == 200
        assert body == {"ok": True}


class TestPostAddParticipant:
    def test_adds_manual_participant(self, server):
        code, body = _post(server + "/api/participant", {"name": "Alice"})
        assert code == 200
        assert body == {"ok": True}
        names = [p["name"] for p in STATE.snapshot()["participants"]]
        assert "Alice" in names

    def test_empty_name_returns_400(self, server):
        code, body = _post(server + "/api/participant", {"name": "   "})
        assert code == 400
        assert body == {"error": "name required"}

    def test_missing_name_returns_400(self, server):
        code, _ = _post(server + "/api/participant", {})
        assert code == 400


class TestPostPrompt:
    def test_sets_prompt(self, server):
        code, body = _post(server + "/api/prompt", {"prompt": "Pets?"})
        assert code == 200
        assert body == {"ok": True}
        assert STATE.snapshot()["prompt"] == "Pets?"


class TestPostOrder:
    def test_rejects_non_list_order(self, server):
        code, body = _post(server + "/api/order", {"order": "not-a-list"})
        assert code == 400
        assert "list" in body["error"]

    def test_applies_order(self, server):
        STATE.add_manual("Alice")
        STATE.add_manual("Bob")
        snap = STATE.snapshot()["participants"]
        ids_reversed = [p["id"] for p in reversed(snap)]
        code, _ = _post(server + "/api/order", {"order": ids_reversed})
        assert code == 200
        new_names = [p["name"] for p in STATE.snapshot()["participants"]]
        assert new_names == ["Bob", "Alice"]


class TestPostRandomizeAndReset:
    def test_randomize(self, server):
        STATE.add_manual("Alice")
        code, body = _post(server + "/api/randomize")
        assert code == 200
        assert body == {"ok": True}

    def test_reset(self, server):
        STATE.add_manual("Alice")
        code, body = _post(server + "/api/reset")
        assert code == 200
        assert body == {"ok": True}
        assert STATE.snapshot()["participants"] == []


class TestParticipantRoutes:
    def test_set_introduced(self, server):
        STATE.add_manual("Alice")
        pid = STATE.snapshot()["participants"][0]["id"]
        code, body = _post(
            f"{server}/api/participant/{pid}/introduced", {"introduced": True}
        )
        assert code == 200
        assert body == {"ok": True}
        assert STATE.snapshot()["participants"][0]["introduced"] is True

    def test_set_introduced_unknown_pid_returns_404(self, server):
        code, body = _post(
            server + "/api/participant/nope/introduced", {"introduced": True}
        )
        assert code == 404
        assert body == {"ok": False}

    def test_set_host_promotes_to_first(self, server):
        STATE.add_manual("Alice")
        STATE.add_manual("Bob")
        bob_pid = STATE.snapshot()["participants"][1]["id"]
        code, _ = _post(f"{server}/api/participant/{bob_pid}/host", {"host": True})
        assert code == 200
        names = [p["name"] for p in STATE.snapshot()["participants"]]
        assert names[0] == "Bob"

    def test_remove(self, server):
        STATE.add_manual("Alice")
        pid = STATE.snapshot()["participants"][0]["id"]
        code, body = _post(f"{server}/api/participant/{pid}/remove")
        assert code == 200
        assert body == {"ok": True}
        assert STATE.snapshot()["participants"] == []

    def test_unknown_action_returns_404(self, server):
        STATE.add_manual("Alice")
        pid = STATE.snapshot()["participants"][0]["id"]
        code, _ = _post(f"{server}/api/participant/{pid}/dance")
        assert code == 404


class TestMalformedRequests:
    def test_malformed_json_falls_back_to_empty_body(self, server):
        # The handler swallows JSON errors and treats the body as {}.
        # On /api/prompt, this means the prompt becomes "".
        STATE.set_prompt("seeded")
        req = urllib.request.Request(
            server + "/api/prompt",
            data=b"not json",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:  # nosec B310
            assert resp.status == 200
        assert STATE.snapshot()["prompt"] == ""


class TestSSE:
    def test_events_endpoint_sends_initial_snapshot(self, server):
        STATE.add_manual("Alice")
        # Open the SSE stream and read just the initial frame, then bail.
        with urllib.request.urlopen(server + "/events", timeout=5) as resp:  # nosec B310
            assert resp.status == 200
            assert resp.headers["Content-Type"] == "text/event-stream"
            # The handler writes the initial snapshot immediately.
            line = resp.readline()
            assert line.startswith(b"data: ")
            payload = json.loads(line[len(b"data: ") :].strip())
            names = [p["name"] for p in payload["participants"]]
            assert "Alice" in names

    def test_live_update_reaches_an_already_connected_client(self, server):
        # The initial frame is the easy half. This covers State.broadcast():
        # a client that is already streaming must receive later mutations.
        with urllib.request.urlopen(server + "/events", timeout=5) as resp:  # nosec B310
            first = json.loads(resp.readline()[len(b"data: ") :].strip())
            assert first["participants"] == []
            STATE.add_manual("Bob")
            # Frames are "data: {...}\n\n", so read past the blank separator.
            line = resp.readline()
            while line in (b"\n", b"\r\n"):
                line = resp.readline()
            pushed = json.loads(line[len(b"data: ") :].strip())
            assert [p["name"] for p in pushed["participants"]] == ["Bob"]


class TestRequestOriginGuard:
    """Binding to 127.0.0.1 stops other machines, not other pages: any site the
    host has open can post to localhost, and a text/plain body dodges the CORS
    preflight entirely. See tracker.ALLOWED_HOSTS."""

    def _raw(self, url, headers, body=b"{}"):
        req = urllib.request.Request(url, data=body, method="POST", headers=headers)
        try:
            with _open(req) as resp:
                return resp.status
        except urllib.error.HTTPError as e:
            return e.code

    def test_cross_origin_post_is_rejected(self, server):
        code = self._raw(
            server + "/api/participant",
            {"Content-Type": "text/plain", "Origin": "https://evil.example"},
            body=json.dumps({"name": "CSRF"}).encode(),
        )
        assert code == 403
        assert STATE.snapshot()["participants"] == []

    def test_forged_host_header_is_rejected(self, server):
        # The DNS-rebinding shape: resolve an attacker domain to 127.0.0.1 and
        # the page becomes same-origin with us, able to read the roster too.
        code = self._raw(server + "/api/reset", {"Host": "attacker.test"})
        assert code == 403

    def test_same_origin_post_still_works(self, server):
        code = self._raw(
            server + "/api/participant",
            {"Content-Type": "application/json", "Origin": server},
            body=json.dumps({"name": "Legit"}).encode(),
        )
        assert code == 200
        assert [p["name"] for p in STATE.snapshot()["participants"]] == ["Legit"]

    def test_same_host_different_port_origin_is_rejected(self, server):
        # localhost:<other> is a different *origin*, so some other local dev
        # server must not be able to drive our POST API just by being on
        # 127.0.0.1. Content-Type: text/plain skips the CORS preflight, which
        # is exactly how such a page would reach us.
        port = int(server.rsplit(":", 1)[1])
        code = self._raw(
            server + "/api/participant",
            {"Content-Type": "text/plain", "Origin": f"http://localhost:{port + 1}"},
            body=json.dumps({"name": "Neighbour"}).encode(),
        )
        assert code == 403
        assert STATE.snapshot()["participants"] == []

    @pytest.mark.parametrize(
        "origin",
        [
            "https://localhost:{port}",  # right host and port, wrong scheme
            "http://localhost",  # implicit :80, which is not us
            "null",  # sandboxed iframe / privacy shim
            "http://[malformed",  # unparseable is untrusted, not a crash
        ],
    )
    def test_other_mismatched_origins_are_rejected(self, server, origin):
        port = server.rsplit(":", 1)[1]
        code = self._raw(server + "/api/reset", {"Origin": origin.format(port=port)})
        assert code == 403

    def test_localhost_form_is_accepted_when_host_agrees(self, server):
        # 127.0.0.1 and localhost are both names for the socket we are bound
        # to, so a page reached by either must keep working -- as long as the
        # page and the request it makes use the same one. See ALLOWED_HOSTS.
        port = server.rsplit(":", 1)[1]
        code = self._raw(
            server + "/api/participant",
            {"Host": f"localhost:{port}", "Origin": f"http://localhost:{port}"},
            body=json.dumps({"name": "Loopback"}).encode(),
        )
        assert code == 200
        assert [p["name"] for p in STATE.snapshot()["participants"]] == ["Loopback"]

    @pytest.mark.parametrize("alias", ["localhost", "[::1]"])
    def test_mismatched_loopback_alias_origin_is_rejected(self, server, alias):
        # The loopback names are not aliases of one another as far as the
        # browser is concerned: ::1:<port> can be a different server than
        # 127.0.0.1:<port>, and this request is addressed to the latter. A
        # page on the neighbour must not be able to drive our POST API, so
        # matching the port alone is not enough.
        port = server.rsplit(":", 1)[1]
        code = self._raw(
            server + "/api/participant",
            {"Content-Type": "text/plain", "Origin": f"http://{alias}:{port}"},
            body=json.dumps({"name": "Neighbour"}).encode(),
        )
        assert code == 403
        assert STATE.snapshot()["participants"] == []

    def test_uppercase_host_is_accepted(self, server):
        # Host names are case-insensitive, so "LOCALHOST:1234" is this server
        # and must not be locked out of its own UI.
        port = server.rsplit(":", 1)[1]
        code = self._raw(
            server + "/api/participant",
            {"Host": f"LOCALHOST:{port}"},
            body=json.dumps({"name": "Shouty"}).encode(),
        )
        assert code == 200
        assert [p["name"] for p in STATE.snapshot()["participants"]] == ["Shouty"]

    @pytest.mark.parametrize(
        ("header", "expected"),
        [
            ("localhost:8000", "localhost"),
            ("LOCALHOST:8000", "localhost"),
            ("127.0.0.1", "127.0.0.1"),
            ("[::1]:8000", "::1"),
            ("[::1]", "::1"),  # no port — brackets still have to come off
            ("http://localhost:8000", "localhost"),  # an Origin, not a Host
            ("", None),
            ("[malformed", None),  # unparseable is untrusted, not a crash
        ],
    )
    def test_hostname_parsing_covers_the_awkward_shapes(self, header, expected):
        assert Handler._hostname(header) == expected

    def test_request_without_an_origin_still_works(self, server):
        # Address-bar navigation and curl send no Origin; only a *mismatched*
        # one means another site is driving us.
        code, _ = _post(server + "/api/participant", {"name": "Typed In"})
        assert code == 200

    def test_get_is_guarded_too(self, server):
        req = urllib.request.Request(server + "/", headers={"Host": "attacker.test"})
        try:
            with _open(req) as resp:
                code = resp.status
        except urllib.error.HTTPError as e:
            code = e.code
        assert code == 403
