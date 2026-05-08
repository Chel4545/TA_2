from pythonProject1.logic.DFAclass import DFA, DFAEdge


def test_make_complete():
    dfa = DFA()

    state_0 = dfa.new_state(is_accepting=False)
    state_1 = dfa.new_state(is_accepting=True)

    dfa.start = state_0
    dfa.alphabet = {"a", "b"}

    dfa.add_edge(state_0, state_1, "a")

    dfa.make_complete()

    sink_id = 2

    assert dfa.alphabet == {"a", "b"}
    assert sink_id in dfa.states
    assert dfa.states[sink_id].is_accepting is False

    assert dfa.states[state_0].edges == [
        DFAEdge(to_state=state_1, symbol="a"),
        DFAEdge(to_state=sink_id, symbol="b"),
    ]

    assert dfa.states[state_1].edges == [
        DFAEdge(to_state=sink_id, symbol="a"),
        DFAEdge(to_state=sink_id, symbol="b"),
    ]

    assert dfa.states[sink_id].edges == [
        DFAEdge(to_state=sink_id, symbol="a"),
        DFAEdge(to_state=sink_id, symbol="b"),
    ]

def test_clone():
    dfa = DFA()

    state_0 = dfa.new_state(is_accepting=False)
    state_1 = dfa.new_state(is_accepting=True)

    dfa.start = state_0
    dfa.alphabet = {"a"}

    dfa.add_edge(state_0, state_1, "a")
    dfa.add_edge(state_1, state_1, "a")

    cloned = dfa.clone()

    assert cloned is not dfa

    assert cloned.start == dfa.start
    assert cloned.next_id == dfa.next_id
    assert cloned.alphabet == dfa.alphabet

    assert cloned.states == dfa.states

    # копии вершин
    assert cloned.states[state_0] is not dfa.states[state_0]
    assert cloned.states[state_1] is not dfa.states[state_1]

    # копии ребер
    assert cloned.states[state_0].edges[0] is not dfa.states[state_0].edges[0]
    assert cloned.states[state_1].edges[0] is not dfa.states[state_1].edges[0]

    assert cloned.states[state_0].edges == [
        DFAEdge(to_state=state_1, symbol="a")
    ]

    assert cloned.states[state_1].edges == [
        DFAEdge(to_state=state_1, symbol="a")
    ]

def test_negate():
    dfa = DFA()

    state_0 = dfa.new_state(is_accepting=False)
    state_1 = dfa.new_state(is_accepting=True)

    dfa.start = state_0
    dfa.alphabet = {"a", "b"}

    dfa.add_edge(state_0, state_1, "a")
    dfa.add_edge(state_1, state_1, "a")

    negated = dfa.negate()

    assert negated is not dfa

    sink_id = 2

    assert negated.start == state_0
    assert negated.alphabet == {"a", "b"}
    assert sink_id in negated.states

    assert negated.states[state_0].is_accepting is True
    assert negated.states[state_1].is_accepting is False
    assert negated.states[sink_id].is_accepting is True

def test_union():
    def build_dfa_for_single_char(char: str) -> DFA:
        dfa = DFA()

        state_0 = dfa.new_state(is_accepting=False)
        state_1 = dfa.new_state(is_accepting=True)

        dfa.start = state_0
        dfa.alphabet = {char}

        dfa.add_edge(state_0, state_1, char)

        return dfa

    dfa_a = build_dfa_for_single_char("a")
    dfa_b = build_dfa_for_single_char("b")

    result = dfa_a.union(dfa_b)

    assert result.alphabet == {"a", "b"}

    assert result.search("a") == (0, 1, "a")
    assert result.search("b") == (0, 1, "b")

    assert result.search("c") is None
    assert result.search("") is None