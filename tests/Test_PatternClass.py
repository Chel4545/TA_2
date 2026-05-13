import pytest

from pythonProject1.PatternClass import Pattern


def test_init():
    pattern = Pattern("a")

    assert pattern.regex == "a"
    assert pattern.tokens is None
    assert pattern.ast is None
    assert pattern.nfa is None
    assert pattern.dfa is None
    assert pattern.min_dfa is None
    assert pattern.has_capture_groups is False
    assert pattern.has_backreferences is False

@pytest.mark.parametrize(
    "regex, has_capture_groups, has_backreferences",
    [
        ("a", False, False),
        ("a+", False, False),
        ("a|b", False, False),
        ("ab", False, False),
        ("a{2,4}", False, False),
        ("^", False, False),
        ("(1:a)", True, False),
    ],
)
def test_compile(regex, has_capture_groups, has_backreferences):
    pattern = Pattern.compile(regex)

    assert pattern.regex == regex
    assert pattern.tokens is not None
    assert pattern.ast is not None
    assert pattern.nfa is not None
    assert pattern.dfa is not None
    assert pattern.min_dfa is not None
    assert pattern.has_capture_groups is has_capture_groups
    assert pattern.has_backreferences is has_backreferences

@pytest.mark.parametrize(
    "regex, data, expected_result",
    [
        ("a", "xxay", (2, 3, "a")),
        ("a", "bbb", None),

        ("a+", "xxaaab", (2, 5, "aaa")),
        ("a+", "bbb", None),

        ("ab", "xxabyy", (2, 4, "ab")),
        ("ab", "acb", None),

        ("a|b", "xxb", (2, 3, "b")),
        ("a|b", "ccc", None),

        ("a{2,4}", "xaaaay", (1, 5, "aaaa")),
        ("a{2,4}", "xay", None),

        ("^", "abc", (0, 0, "")),
    ],
)
def test_search(regex, data, expected_result):
    pattern = Pattern.compile(regex)

    result = pattern.search(data)

    if expected_result is None:
        assert result is None
        return

    expected_start, expected_end, expected_value = expected_result

    assert result is not None
    assert result.start == expected_start
    assert result.end == expected_end
    assert result.value == expected_value

    assert result.group(0) == expected_value
    assert result[0] == expected_value
    assert result.group(1) is None

@pytest.mark.parametrize(
    "regex, data, expected_bool",
    [
        ("a", "a", True),
        ("a", "bbb", False),

        ("a+", "aaaa", True),
        ("a+", "", False),

        ("ab", "ab", True),
        ("ab", "acb", False),

        ("a|b", "b", True),
        ("a|b", "ccc", False),

        ("a{2,4}", "aaaa", True),
        ("a{2,4}", "a", False),
    ],
)
def test_accepts(regex, data, expected_bool):
    pattern = Pattern.compile(regex)

    assert pattern.accepts(data) is expected_bool

@pytest.mark.parametrize(
    "regex, expected_restored",
    [
        ("a", "a"),
        ("ab", "(ab)"),
        ("a|b", "(a|b)"),
        ("^", "^"),
        ("a+", "a(a*)"),
    ],
)
def test_to_regex(regex, expected_restored):
    pattern = Pattern.compile(regex)

    result = pattern.to_regex()

    assert result == expected_restored

@pytest.mark.parametrize(
    "regex, rejected_data, accepted_data",
    [
        ("a", "a", ""),
        ("a", "a", "aa"),

        ("a+", "aaa", ""),

        ("ab", "ab", "a"),
        ("ab", "ab", ""),
        ("ab", "ab", "aba"),

        ("a|b", "a", ""),
        ("a|b", "b", "ab"),
        ("a|b", "a", "aa"),
    ],
)
def test_negate(regex, rejected_data, accepted_data):
    pattern = Pattern.compile(regex)

    result = pattern.negate()

    assert result.dfa is not None
    assert result.min_dfa is not None

    assert result.accepts(rejected_data) is False
    assert result.accepts(accepted_data) is True

@pytest.mark.parametrize(
    "regex_a, regex_b, accepted_data, rejected_data",
    [
        ("a+", "aa", "a", "aa"),
        ("a+", "aa", "aaa", "aa"),
        ("a+", "aa", "aaaa", "aa"),

        ("ab+", "abb", "ab", "abb"),
        ("ab+", "abb", "abbb", "abb"),

        ("(ab)+", "ab", "abab", "ab"),
        ("(ab)+", "ab", "ababab", "ab"),

        ("a{2,4}", "aaa", "aa", "aaa"),
        ("a{2,4}", "aaa", "aaaa", "aaa"),

        ("a{2,4}b", "aaab", "aab", "aaab"),
        ("a{2,4}b", "aaab", "aaaab", "aaab"),

        ("(a|b)c+", "ac", "acc", "ac"),
        ("(a|b)c+", "ac", "bc", "ac"),
    ],
)
def test_diff(regex_a, regex_b, accepted_data, rejected_data):
    pattern_a = Pattern.compile(regex_a)
    pattern_b = Pattern.compile(regex_b)

    result = pattern_a.diff(pattern_b)

    assert result.dfa is not None

    assert result.accepts(accepted_data) is True
    assert result.accepts(rejected_data) is False