"""Tests for the State class in tracker.py."""

import json
import queue
import random

import pytest

import tracker
from tracker import SSE_QUEUE_MAX, State


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

    def test_reset_clears_participants_but_keeps_prompt(self, state, monkeypatch):
        state.set_prompt("Favorite color?")
        state.sync_participants(
            [
                {"name": "Alice", "is_host": False},
                {"name": "Bob", "is_host": False},
            ]
        )
        started_at_before = state.snapshot()["startedAt"]
        # Pin the clock a minute ahead so "refreshed" is a strict change. The
        # old assertion used >= to tolerate sub-ms resolution, which meant it
        # also passed when reset() never touched the clock at all.
        monkeypatch.setattr(tracker.time, "time", lambda: started_at_before / 1000 + 60)
        state.reset()
        snap = state.snapshot()
        assert snap["participants"] == []
        assert snap["prompt"] == "Favorite color?"
        assert snap["startedAt"] > started_at_before


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


class TestAutoReadIdentity:
    """Zoom's panel is only a list of display names, so identity has to be
    reconstructed across reads. These pin the behaviour that name-derived ids
    used to get wrong."""

    def test_same_display_name_twice_stays_two_people(self, state):
        # Two guests genuinely called the same thing must not collapse onto one
        # row — whoever collapsed away would silently never be tracked.
        state.sync_participants(
            [
                {"name": "John Smith", "is_host": False},
                {"name": "John Smith", "is_host": False},
                {"name": "Ana", "is_host": False},
            ]
        )
        assert _names(state.snapshot()) == ["John Smith", "John Smith", "Ana"]
        ids = [p["id"] for p in state.snapshot()["participants"]]
        assert len(set(ids)) == 3

    def test_repeated_names_do_not_multiply_across_reads(self, state):
        people = [
            {"name": "John Smith", "is_host": False},
            {"name": "John Smith", "is_host": False},
        ]
        state.sync_participants(people)
        before = [p["id"] for p in state.snapshot()["participants"]]
        state.sync_participants(people)
        assert [p["id"] for p in state.snapshot()["participants"]] == before

    def test_rename_keeps_the_row_and_its_introduced_flag(self, state):
        state.sync_participants(
            [
                {"name": "Alex", "is_host": False},
                {"name": "Bo", "is_host": False},
            ]
        )
        alex = _pid_of(state, "Alex")
        state.set_introduced(alex, True)
        state.sync_participants(
            [
                {"name": "Alex Rivera", "is_host": False},
                {"name": "Bo", "is_host": False},
            ]
        )
        snap = state.snapshot()
        assert _names(snap) == ["Alex Rivera", "Bo"]
        renamed = _by_name(state, "Alex Rivera")
        assert renamed["id"] == alex  # same row, not a ghost + a stranger
        assert renamed["introduced"] is True
        assert renamed["present"] is True

    def test_ambiguous_swap_is_not_guessed_at(self, state):
        # Two out and two in at once has no single possible pairing, so
        # carrying anyone's checkmark across would be a coin flip. Treat it as
        # an ordinary leave plus join instead.
        state.sync_participants(
            [{"name": "P", "is_host": False}, {"name": "Q", "is_host": False}]
        )
        state.sync_participants(
            [{"name": "X", "is_host": False}, {"name": "Y", "is_host": False}]
        )
        by_name = {p["name"]: p for p in state.snapshot()["participants"]}
        assert by_name["P"]["present"] is False
        assert by_name["Q"]["present"] is False
        assert by_name["X"]["present"] is True
        assert by_name["Y"]["present"] is True

    def test_a_plain_arrival_is_not_mistaken_for_a_rename(self, state):
        # Nobody left, so the newcomer can't be anyone's new name. The rename
        # rebind must stay off unless a present row actually vanished.
        state.sync_participants([{"name": "Alex", "is_host": False}])
        alex = _pid_of(state, "Alex")
        state.set_introduced(alex, True)
        state.sync_participants(
            [{"name": "Alex", "is_host": False}, {"name": "Sam", "is_host": False}]
        )
        assert _names(state.snapshot()) == ["Alex", "Sam"]
        assert _by_name(state, "Sam")["id"] != alex
        assert _by_name(state, "Sam")["introduced"] is False
        assert _by_name(state, "Alex")["introduced"] is True

    def test_manual_rows_are_never_claimed_by_a_panel_name(self, state):
        # A hand-typed row is not part of the panel's identity space: an
        # auto-read "Carol" must get her own row rather than adopting (and
        # later marking absent) the manual one.
        state.add_manual("Carol")
        manual = _pid_of(state, "Carol")
        state.sync_participants([{"name": "Carol", "is_host": False}])
        ids = [p["id"] for p in state.snapshot()["participants"]]
        assert len(ids) == 2
        assert manual in ids
        assert all(p["present"] for p in state.snapshot()["participants"])

    def test_ids_are_never_reused_after_reset(self, state):
        # reset() clears the roster but not the counter: a stale SSE frame or
        # an in-flight click must not land on a new round's participant.
        state.sync_participants([{"name": "Alice", "is_host": False}])
        state.add_manual("Manual")
        before = {p["id"] for p in state.snapshot()["participants"]}
        state.reset()
        state.sync_participants([{"name": "Alice", "is_host": False}])
        state.add_manual("Manual")
        after = {p["id"] for p in state.snapshot()["participants"]}
        assert before.isdisjoint(after)

    def test_rejoining_under_the_same_name_reuses_the_row(self, state):
        state.sync_participants([{"name": "Alice", "is_host": False}])
        alice = _pid_of(state, "Alice")
        state.set_introduced(alice, True)
        state.sync_participants([])  # panel empties (Alice drops off)
        state.sync_participants([{"name": "Alice", "is_host": False}])
        again = _by_name(state, "Alice")
        assert again["id"] == alice
        assert again["introduced"] is True


class TestBroadcastQueueBound:
    def test_slow_client_keeps_the_newest_frame(self, state):
        q = queue.Queue(maxsize=SSE_QUEUE_MAX)
        state.clients.add(q)
        for i in range(SSE_QUEUE_MAX * 4):
            state.add_manual(f"p{i}")
        # The queue is capped, and the frame a stalled reader would see next
        # time it drains is the CURRENT one — old frames are dropped, not new.
        assert q.qsize() == SSE_QUEUE_MAX
        newest = json.loads(list(q.queue)[-1].removeprefix("data: "))
        assert len(newest["participants"]) == SSE_QUEUE_MAX * 4
