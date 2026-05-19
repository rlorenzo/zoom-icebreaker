"""Tests for the pure name-cleaning / filtering helpers in tracker.py."""

import pytest

from tracker import (
    DEFAULT_EXCLUDE,
    HOST_DETECT,
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
