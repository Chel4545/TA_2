import pytest

from pythonProject1.logic.NFAclass import NFA, State, Edge, Fragment
from pythonProject1.logic.ASTclass import Literal, Epsilon, Concat, Or, Plus, Repeat, Group, BackRef, AST
from pythonProject1.logic.Tokenizer import Tokenizer


def test_new_state():
    nfa = NFA()

    first = nfa.new_state()
    second = nfa.new_state()
    third = nfa.new_state()

    assert first == 0
    assert second == 1
    assert third == 2
    assert nfa.next_id == 3

def test_add_edge():
    nfa = NFA()

    from_state = nfa.new_state()
    to_state_1 = nfa.new_state()
    to_state_2 = nfa.new_state()

    # Переход по символу
    nfa.add_edge(from_state, to_state_1, "a")

    # Epsilon-переход
    nfa.add_edge(from_state, to_state_2)

    assert nfa.states[from_state].edges == [
        Edge(to_state=to_state_1, symbol="a"),
        Edge(to_state=to_state_2, symbol=None),
    ]

def test_mark_accepting():
    nfa = NFA()

    state_1 = nfa.new_state()
    state_2 = nfa.new_state()

    nfa.mark_accepting(state_1)

    assert nfa.states[state_1].is_accepting is True
    assert nfa.states[state_2].is_accepting is False

def test_validate_fragment_errors():
    nfa = NFA()

    with pytest.raises(ValueError):
        nfa.validate_fragment(None)

    with pytest.raises(ValueError):
        nfa.validate_fragment("not fragment")

    with pytest.raises(ValueError):
        nfa.validate_fragment(Fragment(start=None, accept=1))

    with pytest.raises(ValueError):
        nfa.validate_fragment(Fragment(start=0, accept=None))

def test_build_literal():
    nfa = NFA()

    fragment = nfa.build_literal(Literal("a"))

    assert fragment == Fragment(start=0, accept=1)

    assert fragment.start in nfa.states
    assert fragment.accept in nfa.states

    assert nfa.states[fragment.start].edges == [
        Edge(to_state=fragment.accept, symbol="a")
    ]

def test_build_epsilon():
    nfa = NFA()

    fragment = nfa.build_epsilon()

    assert fragment == Fragment(start=0, accept=1)

    assert fragment.start in nfa.states
    assert fragment.accept in nfa.states

    assert nfa.states[fragment.start].edges == [
        Edge(to_state=fragment.accept, symbol=None)
    ]

def test_apply_concat():
    nfa = NFA()

    left = nfa.build_literal(Literal("a"))
    right = nfa.build_literal(Literal("b"))

    result = nfa.apply_concat(left, right)


    assert result == Fragment(
        start=left.start,
        accept=right.accept,
    )

    assert nfa.states[left.start].edges == [
        Edge(to_state=left.accept, symbol="a")
    ]

    assert nfa.states[left.accept].edges == [
        Edge(to_state=right.start, symbol=None)
    ]

    assert nfa.states[right.start].edges == [
        Edge(to_state=right.accept, symbol="b")
    ]

def test_apply_union():
    nfa = NFA()

    left = nfa.build_literal(Literal("a"))
    right = nfa.build_literal(Literal("b"))

    result = nfa.apply_union(left, right)

    assert result.start not in {
        left.start,
        left.accept,
        right.start,
        right.accept,
    }

    assert result.accept not in {
        left.start,
        left.accept,
        right.start,
        right.accept,
    }

    assert nfa.states[result.start].edges == [
        Edge(to_state=left.start, symbol=None),
        Edge(to_state=right.start, symbol=None)
    ]

    assert nfa.states[left.start].edges == [
        Edge(to_state=left.accept, symbol="a")
    ]
    assert nfa.states[right.start].edges == [
        Edge(to_state=right.accept, symbol="b")
    ]

    assert nfa.states[left.accept].edges == [
        Edge(to_state=result.accept, symbol=None)
    ]
    assert nfa.states[right.accept].edges == [
        Edge(to_state=result.accept, symbol=None)
    ]

def test_apply_plus():
    nfa = NFA()

    inner = nfa.build_literal(Literal("a"))

    result = nfa.apply_plus(inner)

    assert result.start not in {
        inner.start,
        inner.accept
    }

    assert result.accept not in {
        inner.start,
        inner.accept,
    }

    assert nfa.states[result.start].edges == [
        Edge(to_state=inner.start, symbol=None),
    ]

    assert nfa.states[inner.start].edges == [
        Edge(to_state=inner.accept, symbol="a")
    ]

    assert nfa.states[inner.accept].edges == [
        Edge(to_state=inner.start, symbol=None),
        Edge(to_state=result.accept, symbol=None)
    ]

def test_apply_star():
    nfa = NFA()

    inner = nfa.build_literal(Literal("a"))

    result = nfa.apply_star(inner)

    assert result.start not in {
        inner.start,
        inner.accept,
    }

    assert result.accept not in {
        inner.start,
        inner.accept,
    }

    assert nfa.states[result.start].edges == [
        Edge(to_state=inner.start, symbol=None),
        Edge(to_state=result.accept, symbol=None),
    ]

    assert nfa.states[inner.start].edges == [
        Edge(to_state=inner.accept, symbol="a")
    ]

    assert nfa.states[inner.accept].edges == [
        Edge(to_state=inner.start, symbol=None),
        Edge(to_state=result.accept, symbol=None),
    ]

def test_copy_fragment():
    nfa = NFA()

    original = nfa.build_nfa(
        Or(
            left=Concat(
                left=Literal("a"),
                right=Literal("b"),
            ),
            right=Literal("c"),
        )
    )

    copy = nfa.copy_fragment(original)

    assert copy.start != original.start
    assert copy.accept != original.accept

    # orig 0 - 7
    # copy 8 - 15
    assert copy == Fragment(start=8, accept=14)

    assert nfa.states[8].edges == [
        Edge(to_state=9, symbol=None),
        Edge(to_state=10, symbol=None),
    ]

    assert nfa.states[9].edges == [
        Edge(to_state=11, symbol="a"),
    ]

    assert nfa.states[10].edges == [
        Edge(to_state=12, symbol="c"),
    ]

    assert nfa.states[11].edges == [
        Edge(to_state=13, symbol=None),
    ]

    assert nfa.states[12].edges == [
        Edge(to_state=14, symbol=None),
    ]

    assert nfa.states[13].edges == [
        Edge(to_state=15, symbol="b"),
    ]

    assert nfa.states[14].edges == []

    assert nfa.states[15].edges == [
        Edge(to_state=14, symbol=None),
    ]

def test_apply_optional():
    nfa = NFA()

    inner = nfa.build_literal(Literal("a"))

    result = nfa.apply_optional(inner)

    assert result.start not in {
        inner.start,
        inner.accept,
    }

    assert result.accept not in {
        inner.start,
        inner.accept,
    }

    assert nfa.states[result.start].edges == [
        Edge(to_state=inner.start, symbol=None),
        Edge(to_state=result.accept, symbol=None),
    ]

    assert nfa.states[inner.start].edges == [
        Edge(to_state=inner.accept, symbol="a")
    ]

    assert nfa.states[inner.accept].edges == [
        Edge(to_state=result.accept, symbol=None)
    ]

    assert nfa.states[result.accept].edges == []


def test_apply_min_repeat():
    nfa = NFA()

    inner = nfa.build_literal(Literal("a"))

    result = nfa.apply_min_repeat(inner, 3)

    assert result == Fragment(start=inner.start, accept=5)

    # 0 -a-> 1
    assert nfa.states[0].edges == [
        Edge(to_state=1, symbol="a")
    ]

    # 1 -e-> 2
    assert nfa.states[1].edges == [
        Edge(to_state=2, symbol=None)
    ]

    # 2 -a-> 3
    assert nfa.states[2].edges == [
        Edge(to_state=3, symbol="a")
    ]

    # 3 -e-> 4
    assert nfa.states[3].edges == [
        Edge(to_state=4, symbol=None)
    ]

    # 4 -a-> 5
    assert nfa.states[4].edges == [
        Edge(to_state=5, symbol="a")
    ]

    assert nfa.states[5].edges == []

    with pytest.raises(ValueError):
        nfa.apply_min_repeat(inner, -1)

def test_apply_max_repeat():
    nfa = NFA()

    inner = nfa.build_literal(Literal("a"))

    result = nfa.apply_min_repeat(inner, 2)

    result = nfa.apply_max_repeat(
        result=result,
        inner=inner,
        diff=2,
    )

    assert result == Fragment(start=0, accept=11)

    # первая обязательная a
    assert nfa.states[0].edges == [
        Edge(to_state=1, symbol="a")
    ]

    # concat
    assert nfa.states[1].edges == [
        Edge(to_state=2, symbol=None)
    ]

    # вторая обязательная a
    assert nfa.states[2].edges == [
        Edge(to_state=3, symbol="a")
    ]

    # concat к первому optional(a)
    assert nfa.states[3].edges == [
        Edge(to_state=6, symbol=None)
    ]

    assert nfa.states[4].edges == [
        Edge(to_state=5, symbol="a")
    ]

    assert nfa.states[5].edges == [
        Edge(to_state=7, symbol=None)
    ]

    assert nfa.states[6].edges == [
        Edge(to_state=4, symbol=None),
        Edge(to_state=7, symbol=None),
    ]

    # concat ко второму optional(a)
    assert nfa.states[7].edges == [
        Edge(to_state=10, symbol=None)
    ]

    assert nfa.states[8].edges == [
        Edge(to_state=9, symbol="a")
    ]

    assert nfa.states[9].edges == [
        Edge(to_state=11, symbol=None)
    ]

    assert nfa.states[10].edges == [
        Edge(to_state=8, symbol=None),
        Edge(to_state=11, symbol=None),
    ]

    assert nfa.states[11].edges == []

    with pytest.raises(ValueError):
        nfa.apply_max_repeat(
            result=result,
            inner=inner,
            diff=-1,
        )

def test_apply_repeat():
    nfa = NFA()

    # проверка a{1:2}
    inner = nfa.build_literal(Literal("a"))

    result = nfa.apply_repeat(
        inner=inner,
        min_count=1,
        max_count=2,
    )

    assert result == Fragment(start=0, accept=5)

    assert nfa.states[0].edges == [
        Edge(to_state=1, symbol="a")
    ]

    assert nfa.states[1].edges == [
        Edge(to_state=4, symbol=None)
    ]

    assert nfa.states[2].edges == [
        Edge(to_state=3, symbol="a")
    ]

    assert nfa.states[3].edges == [
        Edge(to_state=5, symbol=None)
    ]

    assert nfa.states[4].edges == [
        Edge(to_state=2, symbol=None),
        Edge(to_state=5, symbol=None),
    ]

    assert nfa.states[5].edges == []

    # min_count < 0
    with pytest.raises(ValueError):
        nfa.apply_repeat(
            inner=inner,
            min_count=-1,
            max_count=2,
        )

    # max_count < min_count
    with pytest.raises(ValueError):
        nfa.apply_repeat(
            inner=inner,
            min_count=3,
            max_count=2,
        )

    # min_count == 0: a{0,1} = ^.a?
    nfa = NFA()
    inner = nfa.build_literal(Literal("a"))

    result = nfa.apply_repeat(
        inner=inner,
        min_count=0,
        max_count=1,
    )

    assert result == Fragment(start=2, accept=7)

    assert nfa.states[0].edges == [
        Edge(to_state=1, symbol="a")
    ]

    assert nfa.states[2].edges == [
        Edge(to_state=3, symbol=None)
    ]

    assert nfa.states[4].edges == [
        Edge(to_state=5, symbol="a")
    ]

    assert nfa.states[3].edges == [
        Edge(to_state=6, symbol=None)
    ]

    assert nfa.states[5].edges == [
        Edge(to_state=7, symbol=None)
    ]

    assert nfa.states[6].edges == [
        Edge(to_state=4, symbol=None),
        Edge(to_state=7, symbol=None),
    ]

    assert nfa.states[7].edges == []

    # max_count is None: a{1,} = a.a*
    nfa = NFA()
    inner = nfa.build_literal(Literal("a"))

    result = nfa.apply_repeat(
        inner=inner,
        min_count=1,
        max_count=None,
    )

    assert result == Fragment(start=0, accept=5)

    assert nfa.states[0].edges == [
        Edge(to_state=1, symbol="a")
    ]

    assert nfa.states[2].edges == [
        Edge(to_state=3, symbol="a")
    ]

    assert nfa.states[4].edges == [
        Edge(to_state=2, symbol=None),
        Edge(to_state=5, symbol=None),
    ]

    assert nfa.states[3].edges == [
        Edge(to_state=2, symbol=None),
        Edge(to_state=5, symbol=None),
    ]


    assert nfa.states[1].edges == [
        Edge(to_state=4, symbol=None)
    ]

    assert nfa.states[5].edges == []

def test_apply_group():
    nfa = NFA()

    inner = nfa.build_literal(Literal("a"))

    result = nfa.apply_group(
        inner=inner,
        group_num=1,
    )

    assert result == Fragment(start=2, accept=3)

    assert nfa.states[0].edges == [
        Edge(to_state=1, symbol="a")
    ]

    assert nfa.states[2].edges == [
        Edge(to_state=0, symbol=None, group_start=1)
    ]

    assert nfa.states[1].edges == [
        Edge(to_state=3, symbol=None, group_end=1)
    ]

    assert nfa.states[3].edges == []

CASES = {
    "None -> ValueError": (
        None,
        None,
        None,
        ValueError,
    ),

    "a -> NFA for literal a": (
        "a",
        Fragment(start=0, accept=1),
        [
            (0, [Edge(to_state=1, symbol="a")]),
            (1, []),
        ],
        None,
    ),

    "^ -> NFA for epsilon": (
        "^",
        Fragment(start=0, accept=1),
        [
            (0, [Edge(to_state=1, symbol=None)]),
            (1, []),
        ],
        None,
    ),

    "a|b -> NFA for union": (
        "a|b",
        Fragment(start=4, accept=5),
        [
            (0, [Edge(to_state=1, symbol="a")]),
            (1, [Edge(to_state=5, symbol=None)]),
            (2, [Edge(to_state=3, symbol="b")]),
            (3, [Edge(to_state=5, symbol=None)]),
            (4, [
                Edge(to_state=0, symbol=None),
                Edge(to_state=2, symbol=None),
            ]),
            (5, []),
        ],
        None,
    ),

    "ab -> NFA for concat": (
        "ab",
        Fragment(start=0, accept=3),
        [
            (0, [Edge(to_state=1, symbol="a")]),
            (1, [Edge(to_state=2, symbol=None)]),
            (2, [Edge(to_state=3, symbol="b")]),
            (3, []),
        ],
        None,
    ),

    "a+ -> NFA for plus": (
        "a+",
        Fragment(start=2, accept=3),
        [
            (0, [Edge(to_state=1, symbol="a")]),
            (1, [
                Edge(to_state=0, symbol=None),
                Edge(to_state=3, symbol=None),
            ]),
            (2, [Edge(to_state=0, symbol=None)]),
            (3, []),
        ],
        None,
    ),

    "a{1,2} -> NFA for repeat": (
        "a{1,2}",
        Fragment(start=0, accept=5),
        [
            (0, [Edge(to_state=1, symbol="a")]),
            (1, [Edge(to_state=4, symbol=None)]),
            (2, [Edge(to_state=3, symbol="a")]),
            (3, [Edge(to_state=5, symbol=None)]),
            (4, [
                Edge(to_state=2, symbol=None),
                Edge(to_state=5, symbol=None),
            ]),
            (5, []),
        ],
        None,
    ),

    "(1:a) -> NFA for capture group": (
        "(1:a)",
        Fragment(start=2, accept=3),
        [
            (0, [Edge(to_state=1, symbol="a")]),
            (1, [Edge(to_state=3, symbol=None, group_end=1)]),
            (2, [Edge(to_state=0, symbol=None, group_start=1)]),
            (3, []),
        ],
        None,
    ),
}


@pytest.mark.parametrize("case_name", CASES.keys())
def test_build_nfa(case_name):
    nfa = NFA()

    regex, expected_fragment, expected_edges, expected_error = CASES[case_name]

    if expected_error is not None:
        with pytest.raises(expected_error):
            if regex is None:
                nfa.build_nfa(None)
            else:
                tokenizer = Tokenizer(regex)

                ast = AST()
                ast_root = ast.parse(tokenizer.tokens)

                nfa.build_nfa(ast_root)
        return

    tokenizer = Tokenizer(regex)

    ast = AST()
    ast_root = ast.parse(tokenizer.tokens)

    result = nfa.build_nfa(ast_root)

    assert result == expected_fragment

    assert nfa.start == expected_fragment.start
    assert nfa.accept == expected_fragment.accept

    assert nfa.states[nfa.accept].is_accepting is True

    for state_id, expected_state_edges in expected_edges:
        assert nfa.states[state_id].edges == expected_state_edges

def test_transition_returns_edges():
    nfa = NFA()

    state_0 = nfa.new_state()
    state_1 = nfa.new_state()
    state_2 = nfa.new_state()
    state_3 = nfa.new_state()

    nfa.add_edge(state_0, state_1, "a")
    nfa.add_edge(state_0, state_2, "a")
    nfa.add_edge(state_0, state_3, None, group_start=1)

    result = nfa.transition(state_0, "a")

    assert result == [
        Edge(to_state=state_1, symbol="a"),
        Edge(to_state=state_2, symbol="a"),
    ]

    result = nfa.transition(state_0, None)

    assert result == [
        Edge(to_state=state_3, symbol=None, group_start=1),
    ]

    result = nfa.transition(state_0, "b")

    assert result == []

CASES_SEARCH = {
    "(1:a)": (
        "(1:a)",
        "xxay",
        (2, 3, "a"),
        {1: "a"},
    ),

    "a(1:b+)c": (
        "a(1:b+)c",
        "xxabbbcabbbbccb",
        (2, 7, "abbbc"),
        {1: "bbb"},
    ),

    "(1:a+)(2:b+)": (
        "(1:a+)(2:b+)",
        "xxaaabbbzz",
        (2, 8, "aaabbb"),
        {1: "aaa", 2: "bbb"},
    ),

    "(1:a(2:b+)c)": (
        "(1:a(2:b+)c)",
        "xxabbbczz",
        (2, 7, "abbbc"),
        {1: "abbbc", 2: "bbb"},
    ),

    "a(1:^)b": (
        "a(1:^)b",
        "xab",
        (1, 3, "ab"),
        {1: ""},
    ),

    "(1:a) no match": (
        "(1:a)",
        "xxby",
        None,
        {},
    ),

    "^+ E cycle": (
        "(1:^+)",
        "",
        (0, 0, ""),
        {1: ""},
    ),
    "aaaaa": (
        "(1:a+)(2:a+)a",
        "aaaaa",
        (0, 5, "aaaaa"),
        {1: "aaa", 2: "a"}
    ),
    "2": (
        "((1:a+)|(2:a+b))b",
        "aaab",
        (0, 4, "aaab"),
        {1: "aaa"}
    ),
    "3": (
        "((1:a+)|(2:a+b))b",
        "aaabb",
        (0, 5, "aaabb"),
        {2: "aaab"}
    ),
    "4": (
        "((1:aaa)|(2:a+))a",
        "aaaa",
        (0, 4, "aaaa"),
        {1: "aaa"}
    ),
    "5": (
        "((1:aaa)|(2:a+))a",
        "aaa",
        (0, 3, "aaa"),
        {2: "aa"}
    ),
    "6": (
        "((1:aaa)|(2:a+))a",
        "aaaaa",
        (0, 5, "aaaaa"),
        {2: "aaaa"}
    )
}

@pytest.mark.parametrize("case_name", CASES_SEARCH.keys())
def test_search(case_name):
    (
        regex,
        data,
        expected_result,
        expected_groups,
    ) = CASES_SEARCH[case_name]

    tokenizer = Tokenizer(regex)

    ast = AST()
    ast_root = ast.parse(tokenizer.tokens)

    nfa = NFA()
    nfa.build_nfa(ast_root)

    result = nfa.search_with_groups(data)

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

    for group_num, group_value in expected_groups.items():
        assert result.group(group_num) == group_value
        assert result[group_num] == group_value

    assert list(result) == [
        expected_groups[group_num]
        for group_num in sorted(expected_groups)
    ]