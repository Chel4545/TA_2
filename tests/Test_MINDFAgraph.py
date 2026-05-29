import pytest

from pythonProject1.logic.ASTclass import Literal, Epsilon, Concat, Or, Plus, Repeat, Group, BackRef, AST
from pythonProject1.logic.NFAclass import NFA

from pythonProject1.logic.DFAclass import DFA, DFAState, DFAEdge
from pythonProject1.logic.Tokenizer import Tokenizer

def test_get_states_by_accepting():
    dfa = DFA()

    state_0 = dfa.new_state(is_accepting=False)
    state_1 = dfa.new_state(is_accepting=True)
    state_2 = dfa.new_state(is_accepting=True)
    state_3 = dfa.new_state(is_accepting=False)
    dfa.start = state_0

    accepting_states = dfa.get_states_by_accepting(True)

    assert accepting_states == {
        state_1,
        state_2,
    }

    non_accepting_states = dfa.get_states_by_accepting(False)

    assert non_accepting_states == {
        state_0,
        state_3,
    }

def test_get_partition_index():
    dfa = DFA()

    state_0 = dfa.new_state(is_accepting=False)
    state_1 = dfa.new_state(is_accepting=False)
    state_2 = dfa.new_state(is_accepting=False)
    state_3 = dfa.new_state(is_accepting=False)
    state_4 = dfa.new_state(is_accepting=False)
    state_5 = dfa.new_state(is_accepting=False)
    dfa.start = state_0

    partitions = [
        {state_0, state_1, state_2},
        {state_3, state_4},
        {state_5},
    ]

    result = dfa.get_partition_index(0, partitions)
    assert result == 0

    result = dfa.get_partition_index(2, partitions)
    assert result == 0

    result = dfa.get_partition_index(3, partitions)
    assert result == 1

    result = dfa.get_partition_index(4, partitions)
    assert result == 1

    result = dfa.get_partition_index(5, partitions)
    assert result == 2

    with pytest.raises(ValueError):
        dfa.get_partition_index(999, partitions)

def test_refine_partitions():
    dfa = DFA()

    # Создаём состояния:
    # 0, 1, 2 — непринимающие
    # 3, 4 — принимающие
    state_0 = dfa.new_state(is_accepting=False)
    state_1 = dfa.new_state(is_accepting=False)
    state_2 = dfa.new_state(is_accepting=False)
    state_3 = dfa.new_state(is_accepting=True)
    state_4 = dfa.new_state(is_accepting=True)

    dfa.start = state_0
    dfa.alphabet = {"0", "1"}

    partitions = [
        {state_0, state_1, state_2},
        {state_3, state_4},
    ]

    # state_0:
    # 0 -> {0,1,2}
    # 1 -> {0,1,2}
    dfa.add_edge(state_0, state_1, "0")
    dfa.add_edge(state_0, state_2, "1")

    # state_1:
    # 0 -> {0,1,2}
    # 1 -> {3,4}
    dfa.add_edge(state_1, state_2, "0")
    dfa.add_edge(state_1, state_3, "1")

    # state_2:
    # 0 -> {0,1,2}
    # 1 -> {3,4}
    dfa.add_edge(state_2, state_0, "0")
    dfa.add_edge(state_2, state_4, "1")

    # state_3:
    # 0 -> {3,4}
    # 1 -> {3,4}
    dfa.add_edge(state_3, state_3, "0")
    dfa.add_edge(state_3, state_4, "1")

    # state_4:
    # 0 -> {3,4}
    # 1 -> {3,4}
    dfa.add_edge(state_4, state_3, "0")
    dfa.add_edge(state_4, state_4, "1")

    result = dfa.refine_partitions(partitions)

    assert result == [
        {state_0},
        {state_1, state_2},
        {state_3, state_4},
    ]

def test_get_partition_transitions():
    dfa = DFA()

    state_0 = dfa.new_state(is_accepting=False)
    state_1 = dfa.new_state(is_accepting=False)
    state_2 = dfa.new_state(is_accepting=False)
    state_3 = dfa.new_state(is_accepting=True)
    state_4 = dfa.new_state(is_accepting=True)

    dfa.start = state_0
    dfa.alphabet = {"a", "b"}

    partitions = [
        {state_0},
        {state_1, state_2},
        {state_3, state_4},
    ]

    dfa.add_edge(state_1, state_3, "a")
    dfa.add_edge(state_1, state_2, "b")

    result = dfa.get_partition_transitions(
        group={state_1, state_2},
        partitions=partitions,
    )

    assert result == {
        "a": 2,
        "b": 1,
    }


CASES_BUILD_MIN_DFA = {
    "a|b -> merge two accepting states": (
        "a|b",
        {"a", "b"},
        3,
        2,
        ["a", "b"],
        ["", "ab", "aa", "bb", "c"],
        "min_dfa_a_or_b",
    ),

    "a+ -> already minimal": (
        "a+",
        {"a"},
        2,
        2,
        ["a", "aa", "aaa", "aaaa"],
        ["", "b", "ab"],
        "min_dfa_a_plus",
    ),

    "ab|ac -> merge final accepting states": (
        "ab|ac",
        {"a", "b", "c"},
        4,
        3,
        ["ab", "ac"],
        ["", "a", "b", "c", "abc", "aa"],
        "min_dfa_ab_or_ac",
    ),

    "(a|b)+ -> nonempty words over a,b": (
        "(a|b)+",
        {"a", "b"},
        3,
        2,
        ["a", "b", "ab", "ba", "abba"],
        ["", "c", "abc"],
        "min_dfa_a_or_b_plus",
    ),

    "^|a -> epsilon or a": (
        "^|a",
        {"a"},
        2,
        2,
        ["", "a"],
        ["aa", "b"],
        "min_dfa_epsilon_or_a",
    ),

    "a{2,4} -> bounded repeat": (
        "a{2,4}",
        {"a"},
        5,
        5,
        ["aa", "aaa", "aaaa"],
        ["", "a", "aaaaa", "b"],
        "min_dfa_a_2_4",
    ),
}

@pytest.mark.parametrize("case_name", CASES_BUILD_MIN_DFA.keys())
def test_build_min_dfa(case_name):
    (
        regex,
        expected_alphabet,
        expected_dfa_state_count,
        expected_min_dfa_state_count,
        accepted_data,
        rejected_data,
        filename,
    ) = CASES_BUILD_MIN_DFA[case_name]

    tokenizer = Tokenizer(regex)

    ast = AST()
    ast_root = ast.parse(tokenizer.tokens)

    nfa = NFA()
    nfa.build_nfa(ast_root)

    dfa = DFA()
    dfa.build_dfa(nfa)

    min_dfa = dfa.build_min_dfa()

    assert dfa.alphabet == expected_alphabet
    assert min_dfa.alphabet == expected_alphabet

    assert len(dfa.states) == expected_dfa_state_count
    assert len(min_dfa.states) == expected_min_dfa_state_count

    assert dfa.is_equivalent(min_dfa) is True

    for data in accepted_data:
        assert dfa.accepts(data) is True
        assert min_dfa.accepts(data) is True

    for data in rejected_data:
        assert dfa.accepts(data) is False
        assert min_dfa.accepts(data) is False