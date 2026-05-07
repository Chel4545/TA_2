import pytest

from pythonProject1.logic.ASTclass import Literal, Epsilon, Concat, Or, Plus, Repeat, Group, BackRef
from pythonProject1.logic.NFAclass import NFA

from pythonProject1.logic.DFAclass import DFA, DFAState, DFAEdge

def test_get_states_by_accepting():
    dfa = DFA()

    state_0 = dfa.new_state(is_accepting=False)
    state_1 = dfa.new_state(is_accepting=True)
    state_2 = dfa.new_state(is_accepting=True)
    state_3 = dfa.new_state(is_accepting=False)

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

    partitions = [
        {0, 1, 2},
        {3, 4},
        {5},
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

    dfa.alphabet = {"0", "1"}

    # Было разбиение:
    # {0, 1, 2} — непринимающие
    # {3, 4}    — принимающие
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

    # state_3 и state_4 ведут себя одинаково:
    # 0 -> {3,4}
    # 1 -> {3,4}
    dfa.add_edge(state_3, state_3, "0")
    dfa.add_edge(state_3, state_4, "1")

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

    dfa = DFA()

    with pytest.raises(ValueError):
        dfa.get_partition_transitions(
            group=set(),
            partitions=[],
        )

def test_build_min_dfa():
    dfa = DFA()

    state_0 = dfa.new_state(is_accepting=False)
    state_1 = dfa.new_state(is_accepting=False)
    state_2 = dfa.new_state(is_accepting=False)
    state_3 = dfa.new_state(is_accepting=True)
    state_4 = dfa.new_state(is_accepting=True)

    dfa.start = state_0
    dfa.alphabet = {"0", "1"}


    dfa.add_edge(state_0, state_1, "0")
    dfa.add_edge(state_0, state_2, "1")

    dfa.add_edge(state_1, state_2, "0")
    dfa.add_edge(state_1, state_3, "1")

    dfa.add_edge(state_2, state_1, "0")
    dfa.add_edge(state_2, state_4, "1")

    dfa.add_edge(state_3, state_3, "0")
    dfa.add_edge(state_3, state_4, "1")

    dfa.add_edge(state_4, state_3, "0")
    dfa.add_edge(state_4, state_4, "1")

    min_dfa = dfa.build_min_dfa()

    assert min_dfa.start == 0
    assert min_dfa.alphabet == {"0", "1"}
    assert len(min_dfa.states) == 3

    assert min_dfa.states[0].is_accepting is False
    assert min_dfa.states[0].edges == [
        DFAEdge(to_state=1, symbol="0"),
        DFAEdge(to_state=1, symbol="1"),
    ]

    assert min_dfa.states[1].is_accepting is False
    assert min_dfa.states[1].edges == [
        DFAEdge(to_state=1, symbol="0"),
        DFAEdge(to_state=2, symbol="1"),
    ]

    assert min_dfa.states[2].is_accepting is True
    assert min_dfa.states[2].edges == [
        DFAEdge(to_state=2, symbol="0"),
        DFAEdge(to_state=2, symbol="1"),
    ]