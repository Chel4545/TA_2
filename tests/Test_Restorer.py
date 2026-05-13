import pytest

from pythonProject1.logic.DFAclass import DFA, DFAState, DFAEdge
from pythonProject1.logic.RegexRestorer import GNFA


def test_is_inf():
    gnfa = GNFA()

    assert gnfa.is_inf("inf") is True
    assert gnfa.is_inf("a") is False


def test_is_eps():
    gnfa = GNFA()

    assert gnfa.is_eps("ε") is True
    assert gnfa.is_eps("a") is False


def test_wrap():
    gnfa = GNFA()

    assert gnfa.wrap("a") == "a"
    assert gnfa.wrap("a|b") == "(a|b)"
    assert gnfa.wrap("(a|b)") == "(a|b)"
    assert gnfa.wrap("inf") == "inf"
    assert gnfa.wrap("ε") == "ε"


def test_regex_or():
    gnfa = GNFA()

    assert gnfa.regex_or("inf", "a") == "a"
    assert gnfa.regex_or("a", "inf") == "a"
    assert gnfa.regex_or("a", "a") == "a"
    assert gnfa.regex_or("a", "b") == "a|b"


def test_regex_concat():
    gnfa = GNFA()

    assert gnfa.regex_concat("a", "b") == "ab"
    assert gnfa.regex_concat("ε", "a") == "a"
    assert gnfa.regex_concat("a", "ε") == "a"
    assert gnfa.regex_concat("a", "inf") == "inf"
    assert gnfa.regex_concat("a|b", "c") == "(a|b)c"


def test_regex_star():
    gnfa = GNFA()

    assert gnfa.regex_star("inf") == "ε"
    assert gnfa.regex_star("ε") == "ε"
    assert gnfa.regex_star("a") == "a*"
    assert gnfa.regex_star("a|b") == "a|b*"

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
        ["b", "a", "inf", "ε"],
        ["ε", "inf", "inf", "inf"],
        ["inf", "inf", "inf", "inf"],
    ]

    assert matrix == expected

def test_build_regex_for_strings_ending_with_a():
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

    result = gnfa.build_regex(dfa)

    assert result == "((b*)a)(a|(b(b*)a)*)"