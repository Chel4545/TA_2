import pytest

from pythonProject1.logic.ASTclass import Literal, Epsilon, Concat, Or, Plus, Repeat, Group, BackRef, AST
from pythonProject1.logic.NFAclass import NFA
from pythonProject1.logic.Tokenizer import Tokenizer
from pythonProject1.visualization.GraphvizVisualizer import GraphvizVisualizer
from pythonProject1.PatternClass import Pattern

from pythonProject1.logic.DFAclass import DFA, DFAState, DFAEdge


def test_new_state():
    dfa = DFA()

    state_1 = dfa.new_state(is_accepting=False)
    state_2 = dfa.new_state(is_accepting=True)

    assert state_1 == 0
    assert state_2 == 1
    assert dfa.next_id == 2

    assert dfa.states[0] == DFAState(
        id=0,
        is_accepting=False,
    )

    assert dfa.states[1] == DFAState(
        id=1,
        is_accepting=True,
    )

    assert dfa.states[0].edges == []
    assert dfa.states[1].edges == []

def test_add_edge():
    dfa = DFA()

    state_0 = dfa.new_state(is_accepting=False)
    state_1 = dfa.new_state(is_accepting=True)
    state_2 = dfa.new_state(is_accepting=False)

    dfa.add_edge(state_0, state_1, "a")
    dfa.add_edge(state_0, state_2, "b")

    assert dfa.states[state_0].edges == [
        DFAEdge(to_state=state_1, symbol="a"),
        DFAEdge(to_state=state_2, symbol="b"),
    ]

    assert dfa.states[state_1].edges == []
    assert dfa.states[state_2].edges == []

def test_get_alphabet():
    tokenizer = Tokenizer("a|b")

    ast = AST()
    ast_root = ast.parse(tokenizer.tokens)

    nfa = NFA()
    nfa.build_nfa(ast_root)

    dfa = DFA()

    result = dfa.get_alphabet(nfa)

    assert result == {"a", "b"}

def test_epsilon_closure():
    tokenizer = Tokenizer("^a")

    ast = AST()
    ast_root = ast.parse(tokenizer.tokens)

    nfa = NFA()
    nfa.build_nfa(ast_root)

    dfa = DFA()

    result = dfa.epsilon_closure(nfa, {nfa.start})

    assert result == frozenset({
        0,
        1,
        2,
    })

def test_is_accepting_subset():
    tokenizer = Tokenizer("a|b")

    ast = AST()
    ast_root = ast.parse(tokenizer.tokens)

    nfa = NFA()
    nfa.build_nfa(ast_root)

    dfa = DFA()

    result = dfa.is_accepting_subset(
        nfa,
        frozenset({nfa.start, nfa.accept}),
    )

    assert result is True

    result = dfa.is_accepting_subset(
        nfa,
        frozenset({nfa.start}),
    )

    assert result is False


def test_move():
    tokenizer = Tokenizer("a|b")

    ast = AST()
    ast_root = ast.parse(tokenizer.tokens)

    nfa = NFA()
    nfa.build_nfa(ast_root)

    dfa = DFA()

    start_closure = dfa.epsilon_closure(nfa, {nfa.start})

    result = dfa.move(
        nfa=nfa,
        state_ids=start_closure,
        symbol="a",
    )

    assert result == {1}

    result = dfa.move(
        nfa=nfa,
        state_ids=start_closure,
        symbol="b",
    )

    assert result == {3}

    result = dfa.move(
        nfa=nfa,
        state_ids=start_closure,
        symbol="c",
    )

    assert result == set()

CASES_BUILD_DFA = {
    "a -> DFA for literal a": (
        "a",
        {"a"},
        2,
        {
            0: False,
            1: True,
        },
        {
            0: [DFAEdge(to_state=1, symbol="a")],
            1: [],
        },
        "build_dfa_literal_a",
    ),

    "^ -> DFA for epsilon": (
        "^",
        set(),
        1,
        {
            0: True,
        },
        {
            0: [],
        },
        "build_dfa_epsilon",
    ),

    "ab -> DFA for concat": (
        "ab",
        {"a", "b"},
        3,
        {
            0: False,
            1: False,
            2: True,
        },
        {
            0: [DFAEdge(to_state=1, symbol="a")],
            1: [DFAEdge(to_state=2, symbol="b")],
            2: [],
        },
        "build_dfa_concat_ab",
    ),

    "a|b -> DFA for union": (
        "a|b",
        {"a", "b"},
        3,
        {
            0: False,
            1: True,
            2: True,
        },
        {
            0: [
                DFAEdge(to_state=1, symbol="a"),
                DFAEdge(to_state=2, symbol="b"),
            ],
            1: [],
            2: [],
        },
        "build_dfa_union_a_or_b",
    ),

    "a+ -> DFA for plus": (
        "a+",
        {"a"},
        2,
        {
            0: False,
            1: True,
        },
        {
            0: [DFAEdge(to_state=1, symbol="a")],
            1: [DFAEdge(to_state=1, symbol="a")],
        },
        "build_dfa_plus_a",
    ),

    "a{1,2} -> DFA for repeat": (
        "a{1,2}",
        {"a"},
        3,
        {
            0: False,
            1: True,
            2: True,
        },
        {
            0: [DFAEdge(to_state=1, symbol="a")],
            1: [DFAEdge(to_state=2, symbol="a")],
            2: [],
        },
        "build_dfa_repeat_a_1_2",
    ),

    "(1:a) -> DFA for capture group": (
        "(1:a)",
        {"a"},
        2,
        {
            0: False,
            1: True,
        },
        {
            0: [DFAEdge(to_state=1, symbol="a")],
            1: [],
        },
        "build_dfa_group_1_a",
    ),
}


@pytest.mark.parametrize("case_name", CASES_BUILD_DFA.keys())
def test_build_dfa(case_name):
    (
        regex,
        expected_alphabet,
        expected_state_count,
        expected_accepting,
        expected_edges,
        filename,
    ) = CASES_BUILD_DFA[case_name]

    tokenizer = Tokenizer(regex)

    ast = AST()
    ast_root = ast.parse(tokenizer.tokens)

    nfa = NFA()
    nfa.build_nfa(ast_root)

    dfa = DFA()
    result = dfa.build_dfa(nfa)

    visualizer = GraphvizVisualizer()

    dfa_graph = visualizer.dfa_to_graph(dfa)
    visualizer.render(
        dfa_graph,
        filename,
        subdir="tests/dfa",
    )

    assert result is dfa

    assert dfa.alphabet == expected_alphabet
    assert dfa.start == 0
    assert len(dfa.states) == expected_state_count

    for state_id, is_accepting in expected_accepting.items():
        assert dfa.states[state_id].is_accepting is is_accepting

    for state_id, edges in expected_edges.items():
        assert dfa.states[state_id].edges == edges

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

CASES_ACCEPTS = {
    "literal a": (
        "a",
        ["a"],
        ["", "b", "aa", "ba"],
    ),

    "concat ab": (
        "ab",
        ["ab"],
        ["", "a", "b", "abc", "xаб"],
    ),

    "plus a": (
        "a+",
        ["a", "aa", "aaa"],
        ["", "b", "ab", "ba"],
    ),

    "union a_or_b": (
        "a|b",
        ["a", "b"],
        ["", "ab", "aa", "bb", "c"],
    ),

    "bounded repeat": (
        "a{2,4}",
        ["aa", "aaa", "aaaa"],
        ["", "a", "aaaaa", "b"],
    ),

    "epsilon": (
        "^",
        [""],
        ["a", "aa", "b"],
    ),

    "epsilon_or_a": (
        "^|a",
        ["", "a"],
        ["aa", "b", "ab"],
    ),
}


@pytest.mark.parametrize("case_name", CASES_ACCEPTS.keys())
def test_accepts(case_name):
    regex, accepted_data, rejected_data = CASES_ACCEPTS[case_name]

    pattern = Pattern.compile(regex)
    dfa = pattern.min_dfa or pattern.dfa

    for data in accepted_data:
        assert dfa.accepts(data) is True

    for data in rejected_data:
        assert dfa.accepts(data) is False

CASES_SEARCH = {
    "find literal a": (
        "a",
        "xxay",
        (2, 3, "a"),
    ),

    "find concat ab": (
        "ab",
        "xxabyy",
        (2, 4, "ab"),
    ),

    "find a_plus longest from first start": (
        "a+",
        "xxaaab",
        (2, 5, "aaa"),
    ),

    "find union": (
        "a|b",
        "xxb",
        (2, 3, "b"),
    ),

    "find bounded repeat longest": (
        "a{2,4}",
        "xaaaay",
        (1, 5, "aaaa"),
    ),

    "epsilon matches at zero position": (
        "^",
        "abc",
        (0, 0, ""),
    ),

    "epsilon_or_a returns empty first": (
        "^|a",
        "abc",
        (0, 1, "a"),
    ),

    "no match": (
        "ab",
        "acb",
        None,
    ),

    "first occurrence before later longer one": (
        "a+",
        "baaa",
        (1, 4, "aaa"),
    ),

    "leftmost start wins": (
        "ab|abc",
        "xxabc",
        (2, 5, "abc"),
    ),
}


@pytest.mark.parametrize("case_name", CASES_SEARCH.keys())
def test_search(case_name):
    regex, data, expected_result = CASES_SEARCH[case_name]

    pattern = Pattern.compile(regex)
    dfa = pattern.min_dfa or pattern.dfa

    result = dfa.search(data)

    assert result == expected_result