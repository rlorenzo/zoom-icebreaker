"""Tests for the State class in tracker.py."""

import random

import pytest

from tracker import State


def _names(snapshot):
    return [p["name"] for p in snapshot["participants"]]


def _by_name(state, name):
    """Return the participant dict matching `name` (case-insensitive)."""
    with state.lock:
        for p in state.participants.values():
            if p["name"].lower() == name.lower():
                return p
    raise KeyError(name)


def _pid_of(state, name):
    return _by_name(state, name)["id"]


@pytest.fixture
def state():
    return State()


class TestSyncParticipants:
    def test_adds_new_participants_in_order(self, state):
        state.sync_participants(
            [
                {"name": "Alice", "is_host": False},
                {"name": "Bob", "is_host": False},
            ]
        )
        assert _names(state.snapshot()) == ["Alice", "Bob"]

    def test_ignores_blank_names(self, state):
        state.sync_participants(
            [
                {"name": "Alice", "is_host": False},
                {"name": "  ", "is_host": False},
                {"name": "", "is_host": False},
            ]
        )
        assert _names(state.snapshot()) == ["Alice"]

    def test_is_idempotent_for_same_input(self, state):
        people = [{"name": "Alice", "is_host": False}]
        assert state.sync_participants(people) is True
        # Second sync with identical input shouldn't claim a change.
        assert state.sync_participants(people) is False

    def test_marks_missing_as_left_then_returning_makes_present(self, state):
        state.sync_participants(
            [
                {"name": "Alice", "is_host": False},
                {"name": "Bob", "is_host": False},
            ]
        )
        # Bob disappears from panel.
        state.sync_participants([{"name": "Alice", "is_host": False}])
        bob = _by_name(state, "Bob")
        assert bob["present"] is False
        assert bob["leftTime"] is not None
        # Bob comes back.
        state.sync_participants(
            [
                {"name": "Alice", "is_host": False},
                {"name": "Bob", "is_host": False},
            ]
        )
        bob = _by_name(state, "Bob")
        assert bob["present"] is True
        assert bob["leftTime"] is None

    def test_manual_entries_are_not_marked_left_when_missing_from_ax(self, state):
        # Manual entries get id prefix "m" so the AX-tracking pass leaves them.
        state.add_manual("Carol")
        state.sync_participants([{"name": "Alice", "is_host": False}])
        carol = _by_name(state, "Carol")
        assert carol["present"] is True
        assert carol["leftTime"] is None


class TestHostHandling:
    def test_host_is_pinned_to_first_slot(self, state):
        state.sync_participants(
            [
                {"name": "Alice", "is_host": False},
                {"name": "Bob", "is_host": True},
                {"name": "Carol", "is_host": False},
            ]
        )
        assert _names(state.snapshot())[0] == "Bob"

    def test_most_recent_host_wins(self, state):
        state.sync_participants(
            [
                {"name": "Alice", "is_host": True},
                {"name": "Bob", "is_host": False},
            ]
        )
        assert _by_name(state, "Alice")["is_host"]
        # Host changes to Bob.
        state.sync_participants(
            [
                {"name": "Alice", "is_host": False},
                {"name": "Bob", "is_host": True},
            ]
        )
        assert _by_name(state, "Bob")["is_host"]
        assert not _by_name(state, "Alice")["is_host"]
        assert _names(state.snapshot())[0] == "Bob"

    def test_only_one_host_at_a_time(self, state):
        state.sync_participants(
            [
                {"name": "Alice", "is_host": True},
                {"name": "Bob", "is_host": True},
            ]
        )
        hosts = [p["name"] for p in state.snapshot()["participants"] if p["is_host"]]
        assert len(hosts) == 1
        # The "last write wins" — Bob came second, so Bob is the host.
        assert hosts == ["Bob"]

    def test_set_host_manually_promotes_and_pins(self, state):
        state.sync_participants(
            [
                {"name": "Alice", "is_host": False},
                {"name": "Bob", "is_host": False},
                {"name": "Carol", "is_host": False},
            ]
        )
        carol_pid = _pid_of(state, "Carol")
        assert state.set_host(carol_pid, True) is True
        snap = state.snapshot()
        assert snap["participants"][0]["name"] == "Carol"
        assert snap["participants"][0]["is_host"]

    def test_set_host_false_demotes(self, state):
        state.sync_participants([{"name": "Alice", "is_host": True}])
        pid = _pid_of(state, "Alice")
        state.set_host(pid, False)
        assert not _by_name(state, "Alice")["is_host"]

    def test_set_host_on_unknown_pid_returns_false(self, state):
        assert state.set_host("nope", True) is False


class TestIntroduced:
    def test_set_introduced_toggles_flag(self, state):
        state.add_manual("Alice")
        pid = _pid_of(state, "Alice")
        assert state.set_introduced(pid, True) is True
        assert _by_name(state, "Alice")["introduced"] is True
        state.set_introduced(pid, False)
        assert _by_name(state, "Alice")["introduced"] is False

    def test_set_introduced_unknown_pid_returns_false(self, state):
        assert state.set_introduced("nope", True) is False


class TestSetOrder:
    def test_reorders_to_requested_sequence(self, state):
        state.sync_participants(
            [
                {"name": "Alice", "is_host": False},
                {"name": "Bob", "is_host": False},
                {"name": "Carol", "is_host": False},
            ]
        )
        a, b, c = (_pid_of(state, n) for n in ("Alice", "Bob", "Carol"))
        state.set_order([c, a, b])
        assert _names(state.snapshot()) == ["Carol", "Alice", "Bob"]

    def test_unknown_ids_are_dropped(self, state):
        state.sync_participants([{"name": "Alice", "is_host": False}])
        a = _pid_of(state, "Alice")
        state.set_order(["bogus", a])
        assert _names(state.snapshot()) == ["Alice"]

    def test_missing_ids_are_appended(self, state):
        state.sync_participants(
            [
                {"name": "Alice", "is_host": False},
                {"name": "Bob", "is_host": False},
            ]
        )
        a = _pid_of(state, "Alice")
        # Only Alice is in the requested order; Bob should be tacked on the end.
        state.set_order([a])
        assert _names(state.snapshot()) == ["Alice", "Bob"]

    def test_host_stays_pinned_even_if_user_tries_to_move_them(self, state):
        state.sync_participants(
            [
                {"name": "Host", "is_host": True},
                {"name": "Alice", "is_host": False},
                {"name": "Bob", "is_host": False},
            ]
        )
        h, a, b = (_pid_of(state, n) for n in ("Host", "Alice", "Bob"))
        # Try to put the host last.
        state.set_order([a, b, h])
        names = _names(state.snapshot())
        assert names[0] == "Host"


class TestRandomize:
    def test_introduced_participants_keep_their_slots(self, state):
        state.sync_participants(
            [{"name": n, "is_host": False} for n in ["A", "B", "C", "D", "E"]]
        )
        b_pid = _pid_of(state, "B")
        d_pid = _pid_of(state, "D")
        state.set_introduced(b_pid, True)
        state.set_introduced(d_pid, True)
        # Seed for determinism.
        random.seed(42)
        state.randomize()
        names = _names(state.snapshot())
        # B stayed in slot 1, D stayed in slot 3.
        assert names[1] == "B"
        assert names[3] == "D"
        # The other slots hold A, C, E in *some* order.
        assert set([names[0], names[2], names[4]]) == {"A", "C", "E"}

    def test_host_stays_at_top(self, state):
        state.sync_participants(
            [
                {"name": "Host", "is_host": True},
                {"name": "A", "is_host": False},
                {"name": "B", "is_host": False},
                {"name": "C", "is_host": False},
            ]
        )
        random.seed(1)
        state.randomize()
        assert _names(state.snapshot())[0] == "Host"

    def test_with_no_unintroduced_participants_is_a_noop(self, state):
        state.sync_participants([{"name": n, "is_host": False} for n in ["A", "B"]])
        for n in ("A", "B"):
            state.set_introduced(_pid_of(state, n), True)
        before = _names(state.snapshot())
        state.randomize()
        assert _names(state.snapshot()) == before


class TestRemoveAndReset:
    def test_remove_drops_participant_from_order_and_dict(self, state):
        state.sync_participants(
            [
                {"name": "Alice", "is_host": False},
                {"name": "Bob", "is_host": False},
            ]
        )
        pid = _pid_of(state, "Alice")
        state.remove(pid)
        names = _names(state.snapshot())
        assert names == ["Bob"]
        with state.lock:
            assert pid not in state.participants

    def test_remove_unknown_pid_is_safe(self, state):
        # Should not raise.
        state.remove("nope")

    def test_reset_clears_participants_but_keeps_prompt(self, state):
        state.set_prompt("Favorite color?")
        state.sync_participants(
            [
                {"name": "Alice", "is_host": False},
                {"name": "Bob", "is_host": False},
            ]
        )
        started_at_before = state.snapshot()["startedAt"]
        state.reset()
        snap = state.snapshot()
        assert snap["participants"] == []
        assert snap["prompt"] == "Favorite color?"
        # startedAt should be refreshed (>=, since clock may not have advanced
        # at sub-ms resolution).
        assert snap["startedAt"] >= started_at_before


class TestPromptAndSnapshot:
    def test_set_prompt_strips_whitespace(self, state):
        state.set_prompt("  hello  ")
        assert state.snapshot()["prompt"] == "hello"

    def test_set_prompt_none_becomes_empty_string(self, state):
        state.set_prompt(None)
        assert state.snapshot()["prompt"] == ""

    def test_snapshot_is_a_deep_copy(self, state):
        state.add_manual("Alice")
        snap1 = state.snapshot()
        snap1["participants"][0]["name"] = "Mutated"
        snap2 = state.snapshot()
        assert snap2["participants"][0]["name"] == "Alice"


class TestAddManual:
    def test_creates_participant_marked_present(self, state):
        state.add_manual("Alice")
        p = _by_name(state, "Alice")
        assert p["present"] is True
        assert p["leftTime"] is None
        assert p["introduced"] is False
        assert p["is_host"] is False

    def test_each_manual_add_creates_a_distinct_entry(self, state):
        # Manual ids include the timestamp, so the same name added twice
        # should produce two participants (not collapse).
        state.add_manual("Alice")
        state.add_manual("Alice")
        names = [p["name"] for p in state.snapshot()["participants"]]
        assert names.count("Alice") == 2
