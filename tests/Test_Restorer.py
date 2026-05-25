import pytest

from pythonProject1.PatternClass import Pattern
from pythonProject1.visualization.GraphvizVisualizer import GraphvizVisualizer
from pythonProject1.logic.DFAclass import DFA, DFAState, DFAEdge
from pythonProject1.logic.RegexRestorer import GNFA


def test_is_inf():
    gnfa = GNFA()

    assert gnfa.is_inf("inf") is True
    assert gnfa.is_inf("a") is False


def test_is_eps():
    gnfa = GNFA()

    assert gnfa.is_eps("^") is True
    assert gnfa.is_eps("a") is False


def test_wrap():
    gnfa = GNFA()

    assert gnfa.wrap("a") == "a"
    assert gnfa.wrap("a|b") == "(a|b)"
    assert gnfa.wrap("inf") == "inf"
    assert gnfa.wrap("^") == "^"


def test_regex_or():
    gnfa = GNFA()

    assert gnfa.regex_or("inf", "a") == "a"
    assert gnfa.regex_or("a", "inf") == "a"
    assert gnfa.regex_or("a", "a") == "a"
    assert gnfa.regex_or("a", "b") == "a|b"


def test_regex_concat():
    gnfa = GNFA()

    assert gnfa.regex_concat("a", "b") == "ab"
    assert gnfa.regex_concat("^", "a") == "a"
    assert gnfa.regex_concat("a", "^") == "a"
    assert gnfa.regex_concat("a", "inf") == "inf"
    assert gnfa.regex_concat("a|b", "c") == "(a|b)c"


def test_regex_star():
    gnfa = GNFA()

    assert gnfa.regex_star("inf") == "^"
    assert gnfa.regex_star("^") == "^"
    assert gnfa.regex_star("a") == "^|(a+)"
    assert gnfa.regex_star("a|b") == "^|((a|b)+)"

def test_build_matrix():
    dfa = DFA()

    dfa.start = 0
    dfa.alphabet = {"a", "b"}

    dfa.states = {
        0: DFAState(
            id=0,
            is_accepting=False,
            edges=[
                DFAEdge(to_state=1, symbol="a"),
                DFAEdge(to_state=0, symbol="b"),
            ],
        ),
        1: DFAState(
            id=1,
            is_accepting=True,
            edges=[
                DFAEdge(to_state=1, symbol="a"),
                DFAEdge(to_state=0, symbol="b"),
            ],
        ),
    }

    gnfa = GNFA()

    matrix = gnfa.build_matrix(dfa)

    assert gnfa.start_index == 2
    assert gnfa.end_index == 3
    assert gnfa.size == 4

    expected = [
        ["b", "a", "inf", "inf"],
        ["b", "a", "inf", "^"],
        ["^", "inf", "inf", "inf"],
        ["inf", "inf", "inf", "inf"],
    ]

    assert matrix == expected

CASES_RESTORE_REGEX = {
    "restore empty language": (
        None,
        [],
        ["", "a", "aa", "aaa", "b", "ab"],
        "restore_empty_language",
    ),

    "restore literal a": (
        "a",
        ["a"],
        ["", "b", "aa"],
        "restore_literal_a",
    ),

    "restore concat ab": (
        "ab",
        ["ab"],
        ["", "a", "b", "aba"],
        "restore_concat_ab",
    ),

    "restore union a_or_b": (
        "a|b",
        ["a", "b"],
        ["", "ab", "aa", "bb"],
        "restore_union_a_or_b",
    ),

    "restore bounded repeat a_2_4": (
        "a{2,4}",
        ["aa", "aaa", "aaaa"],
        ["", "a", "aaaaa", "b"],
        "restore_repeat_a_2_4",
    ),

    "restore epsilon": (
        "^",
        [""],
        ["a", "aa", "b"],
        "restore_epsilon",
    ),

    "restore epsilon_or_a": (
        "^|a",
        ["", "a"],
        ["aa", "b", "ab"],
        "restore_epsilon_or_a",
    ),

    "restore ab_or_ac": (
        "ab|ac",
        ["ab", "ac"],
        ["", "a", "b", "abc", "aa"],
        "restore_ab_or_ac",
    ),
}


@pytest.mark.parametrize("case_name", CASES_RESTORE_REGEX.keys())
def test_restore_regex_equivalence(case_name):
    regex, accepted_data, rejected_data, filename = CASES_RESTORE_REGEX[case_name]

    visualizer = GraphvizVisualizer()

    try:
        original_pattern = Pattern.compile(regex)
    except ValueError:
        assert regex is None
        return

    original_dfa = original_pattern.min_dfa or original_pattern.dfa

    original_graph = visualizer.dfa_to_graph(original_dfa)
    visualizer.render(
        original_graph,
        filename + "_original",
        subdir="tests/restore",
    )

    gnfa = GNFA()
    restored_regex = gnfa.build_regex(original_dfa)

    assert restored_regex is not None

    restored_pattern = Pattern.compile(restored_regex)
    restored_dfa = restored_pattern.min_dfa or restored_pattern.dfa

    restored_graph = visualizer.dfa_to_graph(restored_dfa)
    visualizer.render(
        restored_graph,
        filename + "_restored",
        subdir="tests/restore",
    )

    assert original_dfa.is_equivalent(restored_dfa) is True
    assert restored_dfa.is_equivalent(original_dfa) is True

    for data in accepted_data:
        assert original_dfa.accepts(data) is True
        assert restored_dfa.accepts(data) is True

    for data in rejected_data:
        assert original_dfa.accepts(data) is False
        assert restored_dfa.accepts(data) is False