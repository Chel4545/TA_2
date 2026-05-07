from pythonProject1.logic.ASTclass import Literal, Epsilon, Concat, Or, Plus, Repeat, Group, BackRef
from pythonProject1.logic.NFAclass import NFA

from pythonProject1.logic.DFAclass import DFA, DFAState, DFAEdge


def test_new_state():
    dfa = DFA()

    subset_1 = frozenset({0, 1, 2})
    subset_2 = frozenset({3, 4})

    state_1 = dfa.new_state(
        nfa_states=subset_1,
        is_accepting=False,
    )

    state_2 = dfa.new_state(
        nfa_states=subset_2,
        is_accepting=True,
    )

    assert state_1 == 0
    assert state_2 == 1
    assert dfa.next_id == 2

    assert dfa.states[0] == DFAState(
        id=0,
        nfa_states=frozenset({0, 1, 2}),
        is_accepting=False,
    )

    assert dfa.states[1] == DFAState(
        id=1,
        nfa_states=frozenset({3, 4}),
        is_accepting=True,
    )

    assert dfa.subset_to_dfa_id[frozenset({0, 1, 2})] == 0
    assert dfa.subset_to_dfa_id[frozenset({3, 4})] == 1

def test_add_edge():
    dfa = DFA()

    state_0 = dfa.new_state(
        nfa_states=frozenset({0}),
        is_accepting=False,
    )

    state_1 = dfa.new_state(
        nfa_states=frozenset({1}),
        is_accepting=True,
    )

    state_2 = dfa.new_state(
        nfa_states=frozenset({2}),
        is_accepting=False,
    )

    dfa.add_edge(state_0, state_1, "a")
    dfa.add_edge(state_0, state_2, "b")

    assert dfa.states[state_0].edges == [
        DFAEdge(to_state=state_1, symbol="a"),
        DFAEdge(to_state=state_2, symbol="b"),
    ]

    assert dfa.states[state_1].edges == []
    assert dfa.states[state_2].edges == []

def test_get_alphabet():
    nfa = NFA()

    state_0 = nfa.new_state()
    state_1 = nfa.new_state()
    state_2 = nfa.new_state()
    state_3 = nfa.new_state()

    nfa.add_edge(state_0, state_1, "a")
    nfa.add_edge(state_1, state_2, None)  # не должен попасть в алфавит
    nfa.add_edge(state_2, state_3, "b")
    nfa.add_edge(state_3, state_0, "a")   # повтор не должен дублироваться

    dfa = DFA()

    result = dfa.get_alphabet(nfa)

    assert result == {"a", "b"}

def test_epsilon_closure():
    nfa = NFA()

    state_0 = nfa.new_state()
    state_1 = nfa.new_state()
    state_2 = nfa.new_state()
    state_3 = nfa.new_state()
    state_4 = nfa.new_state()
    state_5 = nfa.new_state()

    nfa.add_edge(state_0, state_1, None)
    nfa.add_edge(state_1, state_2, None)
    nfa.add_edge(state_0, state_3, None)

    #цикл
    nfa.add_edge(state_2, state_0, None)

    nfa.add_edge(state_2, state_4, "a")
    nfa.add_edge(state_3, state_5, "b")

    dfa = DFA()

    result = dfa.epsilon_closure(nfa, {state_0})

    assert result == frozenset({
        state_0,
        state_1,
        state_2,
        state_3,
    })

def test_is_accepting_subset():
    nfa = NFA()

    state_0 = nfa.new_state()
    state_1 = nfa.new_state()
    state_2 = nfa.new_state()

    nfa.mark_accepting(state_2)

    dfa = DFA()

    #есть принимающие в наборе
    result = dfa.is_accepting_subset(
        nfa,
        frozenset({state_0, state_2}),
    )

    assert result is True

    #нет принимающего в наборе
    result = dfa.is_accepting_subset(
        nfa,
        frozenset({state_0, state_1}),
    )

    assert result is False

def test_move():
    nfa = NFA()

    state_0 = nfa.new_state()
    state_1 = nfa.new_state()
    state_2 = nfa.new_state()
    state_3 = nfa.new_state()
    state_4 = nfa.new_state()


    nfa.add_edge(state_0, state_1, "a")
    nfa.add_edge(state_2, state_3, "a")

    nfa.add_edge(state_0, state_4, "b")

    nfa.add_edge(state_1, state_4, None)

    dfa = DFA()

    result = dfa.move(
        nfa=nfa,
        state_ids={state_0, state_2},
        symbol="a",
    )

    assert result == {state_1, state_3}

    result = dfa.move(
        nfa=nfa,
        state_ids={state_0, state_2},
        symbol="b",
    )

    assert result == {state_4}

    result = dfa.move(
        nfa=nfa,
        state_ids={state_0, state_2},
        symbol="c",
    )

    assert result == set()

def test_build_dfa_for_a_or_b():
    nfa = NFA()

    nfa.build_nfa(
        Or(
            left=Literal("a"),
            right=Literal("b"),
        )
    )

    dfa = DFA()

    result = dfa.build_dfa(nfa)

    assert result is dfa

    assert dfa.alphabet == {"a", "b"}
    assert dfa.start == 0

    assert len(dfa.states) == 3

    # стартовое
    assert dfa.states[0].is_accepting is False

    # Из стартового состояния:
    # в принимающее состояние 1
    # в принимающее состояние 2
    assert dfa.states[0].edges == [
        DFAEdge(to_state=1, symbol="a"),
        DFAEdge(to_state=2, symbol="b"),
    ]

    assert dfa.states[1].is_accepting is True
    assert dfa.states[1].edges == []

    assert dfa.states[2].is_accepting is True
    assert dfa.states[2].edges == []

def test_transition():
    dfa = DFA()

    state_0 = dfa.new_state(is_accepting=False)
    state_1 = dfa.new_state(is_accepting=True)
    state_2 = dfa.new_state(is_accepting=False)

    dfa.add_edge(state_0, state_1, "a")
    dfa.add_edge(state_0, state_2, "b")

    result = dfa.transition(state_0, "a")
    assert result == state_1

    result = dfa.transition(state_0, "b")
    assert result == state_2

    result = dfa.transition(state_0, "c")
    assert result is None

    assert dfa.states[state_0].edges == [
        DFAEdge(to_state=state_1, symbol="a"),
        DFAEdge(to_state=state_2, symbol="b"),
    ]

def test_search_for_a_plus():
    nfa = NFA()
    nfa.build_nfa(
        Plus(
            expr=Literal("a"),
        )
    )

    dfa = DFA()
    dfa.build_dfa(nfa)

    result = dfa.search("xxaaab")
    assert result == (2, 5, "aaa")

    result = dfa.search("bbb")
    assert result is None