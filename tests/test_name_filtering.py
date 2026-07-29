"""Tests for the pure name-cleaning / filtering helpers in tracker.py."""

import argparse

import pytest

import tracker
from tracker import (
    CHAT_HINT_RE,
    DEFAULT_EXCLUDE,
    HOST_DETECT,
    _is_chat_anchor_uia,
    build_exclude_re,
    clean_name,
    looks_like_name,
)


class TestCleanName:
    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("Alice", "Alice"),
            ("  Alice  ", "Alice"),
            ("Alice (host)", "Alice"),
            ("Alice (Host)", "Alice"),
            ("Alice (co-host)", "Alice"),
            ("Alice (cohost)", "Alice"),
            ("Alice (me)", "Alice"),
            ("Alice (you)", "Alice"),
            ("Alice (guest)", "Alice"),
            ("Alice (host, me)", "Alice"),
            ("Alice (cohost, me)", "Alice"),
            # Trailing role-word without parens is also stripped.
            ("Alice host", "Alice"),
            ("Alice cohost", "Alice"),
            ("Alice  guest", "Alice"),
        ],
    )
    def test_strips_role_annotations(self, raw, expected):
        assert clean_name(raw) == expected

    def test_preserves_internal_role_words(self):
        # Only trailing role words are stripped.
        assert clean_name("Hosting Hostetler") == "Hosting Hostetler"

    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("Joined (1)", "Joined"),
            ("Joined (12)", "Joined"),
            ("Not joined (0)", "Not joined"),
            ("Alice (3)", "Alice"),
        ],
    )
    def test_strips_trailing_paren_counts(self, raw, expected):
        # Chat-panel section headers like "Joined (12)" carry a count
        # in parens; strip it so the exclude list can catch the header.
        assert clean_name(raw) == expected

    def test_trims_trailing_separators(self):
        assert clean_name("Alice,") == "Alice"
        assert clean_name("Alice - ") == "Alice"

    def test_empty_input(self):
        assert clean_name("") == ""
        assert clean_name("   ") == ""


class TestLooksLikeName:
    @pytest.fixture
    def exclude_re(self):
        return build_exclude_re(DEFAULT_EXCLUDE)

    @pytest.mark.parametrize(
        "name",
        ["Alice", "Bob Smith", "X Y", "Renée Müller", "Jean-Luc"],
    )
    def test_accepts_real_names(self, name, exclude_re):
        assert looks_like_name(name, exclude_re, min_len=2)

    def test_rejects_too_short(self, exclude_re):
        assert not looks_like_name("A", exclude_re, min_len=2)

    def test_rejects_excluded_terms(self, exclude_re):
        assert not looks_like_name("Mute", exclude_re, min_len=2)
        assert not looks_like_name("Participants", exclude_re, min_len=2)
        assert not looks_like_name("Start Video", exclude_re, min_len=2)

    def test_rejects_chat_panel_chrome(self, exclude_re):
        # These are post-COUNT_TAIL strings; the count strip happens in
        # clean_name, but the chrome words themselves must also be excluded.
        assert not looks_like_name("Joined", exclude_re, min_len=2)
        assert not looks_like_name("Not joined", exclude_re, min_len=2)
        assert not looks_like_name("Who can see your messages", exclude_re, min_len=2)
        # Zoom's delivery indicator: "1 participant(s) sent..."
        # `(` is a regex word boundary, so \bparticipant\b matches.
        assert not looks_like_name("1 participant(s) sent...", exclude_re, min_len=2)
        assert not looks_like_name("1 panelist sent", exclude_re, min_len=2)

    def test_rejects_excluded_as_substring_word(self, exclude_re):
        # "host" alone is excluded, but it must match as a whole word.
        assert not looks_like_name("host", exclude_re, min_len=2)
        # "Hostetler" should still pass — it contains "host" but not as a word.
        assert looks_like_name("Hostetler", exclude_re, min_len=2)

    def test_rejects_punctuation_or_digits_only(self, exclude_re):
        assert not looks_like_name("123", exclude_re, min_len=2)
        assert not looks_like_name("---", exclude_re, min_len=2)
        assert not looks_like_name("__", exclude_re, min_len=2)

    def test_rejects_overly_long_strings(self, exclude_re):
        assert not looks_like_name("x" * 61, exclude_re, min_len=2)
        assert looks_like_name("x" * 60, exclude_re, min_len=2)

    def test_min_len_is_inclusive(self, exclude_re):
        assert looks_like_name("Al", exclude_re, min_len=2)
        assert not looks_like_name("Al", exclude_re, min_len=3)


class TestBuildExcludeRe:
    def test_matches_whole_words_case_insensitive(self):
        r = build_exclude_re(["mute", "raise hand"])
        assert r.search("Mute")
        assert r.search("please raise hand now")
        assert not r.search("Hammer")
        assert not r.search("commuter")  # "mute" is a substring; \b prevents match

    def test_orders_longest_first(self):
        # If "host" came first, "co-host" would never get a chance to match —
        # but we sort by length descending. The pattern just needs to match the
        # longer term anywhere in the string.
        r = build_exclude_re(["host", "co-host"])
        assert r.search("co-host")
        assert r.search("host")

    def test_escapes_regex_metacharacters(self):
        r = build_exclude_re(["a.b", "x+y"])
        assert r.search("a.b")
        assert not r.search("axb")  # the "." was escaped
        assert r.search("x+y")

    def test_deduplicates(self):
        # Duplicates should not blow up or cause issues.
        r = build_exclude_re(["mute", "mute", "MUTE"])
        assert r.search("mute")


class TestHostDetect:
    @pytest.mark.parametrize(
        "raw",
        [
            "Alice (host)",
            "Alice (Host)",
            "Alice (host, me)",
            "Alice (host,me)",
            "Alice (HOST, ME)",
        ],
    )
    def test_matches_primary_host_markers(self, raw):
        assert HOST_DETECT.search(raw)

    @pytest.mark.parametrize(
        "raw",
        [
            "Alice (co-host)",
            "Alice (cohost)",
            "Alice (cohost, me)",
            "Alice (me)",
            "Alice (guest)",
            "Alice",
        ],
    )
    def test_does_not_match_non_host_markers(self, raw):
        assert not HOST_DETECT.search(raw)


class _FakeUIAElement:
    """Minimal stand-in for a UIA element: just the attrs the detector reads."""

    def __init__(self, **attrs):
        self.__dict__.update(attrs)


class TestChatAnchorDetection:
    @pytest.mark.parametrize(
        "text",
        ["Chat", "chat", "Meeting Chat", "Chat panel"],
    )
    def test_chat_hint_matches_whole_word(self, text):
        assert CHAT_HINT_RE.search(text)

    @pytest.mark.parametrize(
        "text",
        ["Participants", "Chatham House", "Chatterjee"],
    )
    def test_chat_hint_ignores_substrings_and_non_chat(self, text):
        # \bchat\b must match "chat" as a word, not inside "Chatterjee".
        assert not CHAT_HINT_RE.search(text)

    def test_uia_anchor_flagged_when_any_attr_mentions_chat(self):
        assert _is_chat_anchor_uia(_FakeUIAElement(Name="Chat"))
        assert _is_chat_anchor_uia(_FakeUIAElement(AutomationId="meeting chat"))
        assert _is_chat_anchor_uia(_FakeUIAElement(LocalizedControlType="chat list"))

    def test_uia_anchor_camelcase_id_is_not_caught(self):
        # CHAT_HINT_RE is \bchat\b, so identifier-style values with no word
        # boundary ("ChatPanel") are NOT flagged — only "chat" as a word is.
        assert not _is_chat_anchor_uia(_FakeUIAElement(AutomationId="ChatPanel"))

    def test_uia_anchor_not_flagged_for_participant_panel(self):
        el = _FakeUIAElement(Name="Participants (3)", AutomationId="ParticipantsList")
        assert not _is_chat_anchor_uia(el)


class TestNoPanelMeansNoParticipants:
    """Regression: Zoom running but NOT in a meeting must yield an empty roster.

    The readers used to fall back to the whole application when no participants
    panel matched the anchor regex. Zoom's home window is full of AXButton /
    ButtonControl nodes ("History", "Create new", "Open activity center"), and
    those roles are harvested as text — so the roster filled up with the app's
    own toolbar. Verified against a real idle Zoom: 322 nodes in the tree, zero
    matching the anchor.
    """

    @staticmethod
    def _args():
        return argparse.Namespace(
            bundle="us.zoom.xos", anchor_regex="participant", min_len=2, debug=False
        )

    def test_ax_reader_returns_empty_when_no_panel(self, monkeypatch):
        texts_called = []
        monkeypatch.setattr(tracker, "_find_pid", lambda bundle: 4242)
        monkeypatch.setattr(
            tracker, "AXUIElementCreateApplication", lambda pid: "APP", raising=False
        )
        # Anchor search finds nothing — exactly the idle-Zoom case.
        monkeypatch.setattr(
            tracker, "_collect_anchors", lambda *a, **k: None, raising=False
        )
        monkeypatch.setattr(
            tracker,
            "_collect_texts",
            lambda *a, **k: texts_called.append(a),
            raising=False,
        )
        exclude_re = build_exclude_re(DEFAULT_EXCLUDE)
        assert tracker._read_zoom_participants_ax(self._args(), exclude_re) == []
        # The whole-app scrape must not happen at all.
        assert texts_called == []

    def test_uia_reader_returns_empty_when_no_panel(self, monkeypatch):
        texts_called = []
        monkeypatch.setattr(tracker, "_uia_zoom_windows", lambda: ["WIN"])
        monkeypatch.setattr(
            tracker, "_uia_collect_anchors", lambda *a, **k: None, raising=False
        )
        monkeypatch.setattr(
            tracker,
            "_uia_collect_texts",
            lambda *a, **k: texts_called.append(a),
            raising=False,
        )
        exclude_re = build_exclude_re(DEFAULT_EXCLUDE)
        assert tracker._read_zoom_participants_uia(self._args(), exclude_re) == []
        assert texts_called == []

    def test_zoom_not_running_is_distinct_from_empty_panel(self, monkeypatch):
        # None ("can't read") must stay distinct from [] ("read it, nobody
        # there"): the poller only clears the roster on consecutive empty reads.
        monkeypatch.setattr(tracker, "_find_pid", lambda bundle: None)
        exclude_re = build_exclude_re(DEFAULT_EXCLUDE)
        assert tracker._read_zoom_participants_ax(self._args(), exclude_re) is None


class TestReaderDedupe:
    """Pins where duplicate display names are still lost: the reader, not State.

    State._assign_ax_pids keeps two "John Smith"s on two rows, but the readers
    hand it a single John — both platforms funnel their harvest through
    _filter_and_dedupe, which drops every later occurrence of a name. The
    dedupe is load-bearing (TEXT_ROLES harvests each participant from its row,
    cell and static-text nodes alike), so fixing this means harvesting per row,
    not deleting the dedupe. These tests document today's behavior; the
    duplicate assertion is expected to flip when a row-aware harvest lands.
    """

    @staticmethod
    def _exclude():
        return build_exclude_re(DEFAULT_EXCLUDE)

    def test_repeated_nodes_for_one_participant_collapse(self):
        # Why the dedupe exists: one participant, harvested three times.
        people = tracker._filter_and_dedupe(
            ["Ana Costa", "Ana Costa", "Ana Costa"], self._exclude(), 2
        )
        assert [p["name"] for p in people] == ["Ana Costa"]

    def test_two_real_participants_sharing_a_name_also_collapse(self):
        # KNOWN LIMITATION, not a desired outcome: these are two people.
        people = tracker._filter_and_dedupe(
            ["John Smith", "John Smith", "Ana Costa"], self._exclude(), 2
        )
        assert [p["name"] for p in people] == ["John Smith", "Ana Costa"]

    def test_host_annotation_survives_whatever_order_nodes_arrive_in(self):
        # Regression: the flag used to come from whichever node was harvested
        # first, so a row whose bare-name node preceded its "(host)" node lost
        # the host marker entirely — and then State._settle_host had nobody to
        # promote, leaving a stale host pinned to the top of the roster.
        plain_first = tracker._filter_and_dedupe(
            ["Alice Chen", "Alice Chen (host)"], self._exclude(), 2
        )
        annotated_first = tracker._filter_and_dedupe(
            ["Alice Chen (host)", "Alice Chen"], self._exclude(), 2
        )
        assert (
            plain_first == annotated_first == [{"name": "Alice Chen", "is_host": True}]
        )

    def test_non_host_duplicate_does_not_clear_an_established_host(self):
        people = tracker._filter_and_dedupe(
            ["Alice Chen (host)", "Alice Chen", "Alice Chen"], self._exclude(), 2
        )
        assert people == [{"name": "Alice Chen", "is_host": True}]

    def test_case_and_annotation_variants_count_as_the_same_name(self):
        # Dedupe keys on the cleaned, lowercased name, so "(host)" / casing
        # differences do not sneak a second row in.
        people = tracker._filter_and_dedupe(
            ["Ana Costa (host)", "ana costa", "ANA COSTA"], self._exclude(), 2
        )
        assert [p["name"] for p in people] == ["Ana Costa"]
        assert people[0]["is_host"] is True


class _FakeAX:
    """A stand-in AX element: attribute dict plus children."""

    def __init__(self, attrs=None, children=()):
        self.attrs = attrs or {}
        self.children = list(children)


def _fake_attr(el, name):
    if name == "AXChildren":
        return el.children
    return el.attrs.get(name)


def _cell(item_type, *texts):
    kids = [_FakeAX({"AXRole": "AXStaticText", "AXValue": t}) for t in texts]
    return _FakeAX(
        {"AXRole": "AXRow", "AXSubrole": "AXTableRow"},
        [_FakeAX({"AXRole": "AXCell", "AXIdentifier": item_type}, kids)],
    )


class TestInviteesAreNotParticipants:
    """Regression: only people who actually joined belong on the roster.

    Zoom's panel has a "Joined (N)" section and a "Not joined (N)" section, and
    every invitee row carries their RSVP as a sibling text node. Flattened, that
    reads as a name followed by another name — which is how "Accepted" and
    "No response" ended up on a live roster. Structure mirrors a real capture:
    each row's cell is tagged with a ZMHCTableItemType_* identifier.
    """

    @staticmethod
    def _panel():
        return _FakeAX(
            {"AXRole": "AXOutline", "AXDescription": "Participants list"},
            [
                _cell("ZMHCTableItemType_PANELIST_Group", "Joined (4)"),
                _cell("ZMHCTableItemType_PANELIST", "Rex Lorenzo (Host, me)"),
                _cell("ZMHCTableItemType_PANELIST", "JJMatashi (Co-host, Guest)"),
                _cell("ZMHCTableItemType_PANELIST", "Chris Loza"),
                _cell("ZMHCTableItemType_PANELIST", "Rob Knight (he/him) (Guest)"),
                _cell("ZMHCTableItemType_Invitee_Group", "Not joined (2)"),
                _cell("ZMHCTableItemType_Invitee", "Jeffrey Williams", "No response"),
                _cell(
                    "ZMHCTableItemType_Invitee", "Emmanuel Arinze (Guest)", "Accepted"
                ),
            ],
        )

    def _read(self, monkeypatch):
        monkeypatch.setattr(tracker, "_attr", _fake_attr)
        raw = []
        tracker._collect_texts(self._panel(), raw)
        exclude_re = build_exclude_re(DEFAULT_EXCLUDE)
        return tracker._filter_and_dedupe(raw, exclude_re, 2)

    def test_only_joined_people_are_returned(self, monkeypatch):
        people = self._read(monkeypatch)
        assert [p["name"] for p in people] == [
            "Rex Lorenzo",
            "JJMatashi",
            "Chris Loza",
            "Rob Knight (he/him)",
        ]

    def test_rsvp_statuses_never_become_participants(self, monkeypatch):
        names = [p["name"] for p in self._read(monkeypatch)]
        for status in ("Accepted", "No response", "Declined"):
            assert status not in names

    def test_people_who_have_not_joined_are_excluded(self, monkeypatch):
        names = [p["name"] for p in self._read(monkeypatch)]
        assert "Emmanuel Arinze" not in names

    def test_section_headers_are_not_participants(self, monkeypatch):
        names = [p["name"] for p in self._read(monkeypatch)]
        assert not any(n.startswith(("Joined", "Not joined")) for n in names)

    def test_combined_role_annotation_keeps_the_person(self, monkeypatch):
        # "(Co-host, Guest)" used to survive cleaning, then hit `co-host` in
        # DEFAULT_EXCLUDE and drop the attendee off the roster entirely.
        names = [p["name"] for p in self._read(monkeypatch)]
        assert "JJMatashi" in names

    def test_host_is_still_detected(self, monkeypatch):
        people = self._read(monkeypatch)
        assert [p["name"] for p in people if p["is_host"]] == ["Rex Lorenzo"]
