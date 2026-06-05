"""End-to-end tests for the HTTP handler — spin up the real server on an
ephemeral port and hit it with urllib (no extra deps)."""

import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

import tracker
from tracker import STATE, Handler


@pytest.fixture
def server():
    """Run the real handler on 127.0.0.1:<random> for the test, then tear down."""
    STATE.reset()
    STATE.set_prompt("")
    srv = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    port = srv.server_address[1]
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        srv.shutdown()
        srv.server_close()
        t.join(timeout=2)


def _req(method, url, body=None):
    data = None
    headers = {}
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:  # nosec B310
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
    with urllib.request.urlopen(req, timeout=5) as resp:  # nosec B310
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

    def test_missing_index_html(self, server, monkeypatch, tmp_path):
        # Point INDEX_HTML to a nonexistent file and verify the 500 response.
        monkeypatch.setattr(tracker, "INDEX_HTML", str(tmp_path / "nope.html"))
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

    def test_serves_styles_css(self, server):
        code, ctype, raw = _get_full(server + "/styles.css")
        assert code == 200
        assert "css" in ctype
        assert raw

    def test_missing_static_asset_returns_404(self, server, monkeypatch):
        # Safelisted path whose file is absent should 404, not 500. The handler
        # applies os.path.basename() and joins with HERE, so a bare filename
        # reflects actual server behavior (arbitrary directories are ignored).
        monkeypatch.setitem(
            tracker.STATIC_FILES,
            "/app.js",
            ("gone.js", "text/javascript"),
        )
        code, _ = _get(server + "/app.js")
        assert code == 404

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

    def test_unreadable_static_asset_returns_500(self, server, monkeypatch):
        # A path that exists but can't be read as a file (here, a directory)
        # should yield a controlled JSON 500, not drop the connection.
        monkeypatch.setitem(
            tracker.STATIC_FILES,
            "/app.js",
            ("tests", "text/javascript"),
        )
        code, raw = _get(server + "/app.js")
        assert code == 500
        assert b"could not read file" in raw


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
