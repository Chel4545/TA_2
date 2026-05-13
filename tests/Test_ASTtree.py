import pytest

from pythonProject1.logic.Tokenizer import Token, TokenType
from pythonProject1.logic.ASTclass import (
    AST,
    Node,
    Literal,
    Epsilon,
    Concat,
    Or,
    Plus,
    Repeat,
    Group,
    BackRef,
)

CASES = {
    "ab -> a.b": (
        [
            Token(TokenType.LITERAL, "a"),
            Token(TokenType.LITERAL, "b"),
            Token(TokenType.EOF),
        ],
        [
            Token(TokenType.LITERAL, "a"),
            Token(TokenType.CONCAT),
            Token(TokenType.LITERAL, "b"),
            Token(TokenType.EOF),
        ],
    ),

    "a(b) -> a.(b)": (
        [
            Token(TokenType.LITERAL, "a"),
            Token(TokenType.LPAREN),
            Token(TokenType.LITERAL, "b"),
            Token(TokenType.RPAREN),
            Token(TokenType.EOF),
        ],
        [
            Token(TokenType.LITERAL, "a"),
            Token(TokenType.CONCAT),
            Token(TokenType.LPAREN),
            Token(TokenType.LITERAL, "b"),
            Token(TokenType.RPAREN),
            Token(TokenType.EOF),
        ],
    ),

    "(a)b -> (a).b": (
        [
            Token(TokenType.LPAREN),
            Token(TokenType.LITERAL, "a"),
            Token(TokenType.RPAREN),
            Token(TokenType.LITERAL, "b"),
            Token(TokenType.EOF),
        ],
        [
            Token(TokenType.LPAREN),
            Token(TokenType.LITERAL, "a"),
            Token(TokenType.RPAREN),
            Token(TokenType.CONCAT),
            Token(TokenType.LITERAL, "b"),
            Token(TokenType.EOF),
        ],
    ),

    "(a)(b) -> (a).(b)": (
        [
            Token(TokenType.LPAREN),
            Token(TokenType.LITERAL, "a"),
            Token(TokenType.RPAREN),
            Token(TokenType.LPAREN),
            Token(TokenType.LITERAL, "b"),
            Token(TokenType.RPAREN),
            Token(TokenType.EOF),
        ],
        [
            Token(TokenType.LPAREN),
            Token(TokenType.LITERAL, "a"),
            Token(TokenType.RPAREN),
            Token(TokenType.CONCAT),
            Token(TokenType.LPAREN),
            Token(TokenType.LITERAL, "b"),
            Token(TokenType.RPAREN),
            Token(TokenType.EOF),
        ],
    ),

    "a+b -> a+.b": (
        [
            Token(TokenType.LITERAL, "a"),
            Token(TokenType.PLUS),
            Token(TokenType.LITERAL, "b"),
            Token(TokenType.EOF),
        ],
        [
            Token(TokenType.LITERAL, "a"),
            Token(TokenType.PLUS),
            Token(TokenType.CONCAT),
            Token(TokenType.LITERAL, "b"),
            Token(TokenType.EOF),
        ],
    ),

    "a{2,3}b -> a{2,3}.b": (
        [
            Token(TokenType.LITERAL, "a"),
            Token(TokenType.RANGE, (2, 3)),
            Token(TokenType.LITERAL, "b"),
            Token(TokenType.EOF),
        ],
        [
            Token(TokenType.LITERAL, "a"),
            Token(TokenType.RANGE, (2, 3)),
            Token(TokenType.CONCAT),
            Token(TokenType.LITERAL, "b"),
            Token(TokenType.EOF),
        ],
    ),

    "^a -> ^.a": (
        [
            Token(TokenType.EPSILON),
            Token(TokenType.LITERAL, "a"),
            Token(TokenType.EOF),
        ],
        [
            Token(TokenType.EPSILON),
            Token(TokenType.CONCAT),
            Token(TokenType.LITERAL, "a"),
            Token(TokenType.EOF),
        ],
    ),

    r"\1a -> \1.a": (
        [
            Token(TokenType.BACKREF, 1),
            Token(TokenType.LITERAL, "a"),
            Token(TokenType.EOF),
        ],
        [
            Token(TokenType.BACKREF, 1),
            Token(TokenType.CONCAT),
            Token(TokenType.LITERAL, "a"),
            Token(TokenType.EOF),
        ],
    ),

    "a(1:b) -> a.(1:b)": (
        [
            Token(TokenType.LITERAL, "a"),
            Token(TokenType.GROUP_START, 1),
            Token(TokenType.LITERAL, "b"),
            Token(TokenType.RPAREN),
            Token(TokenType.EOF),
        ],
        [
            Token(TokenType.LITERAL, "a"),
            Token(TokenType.CONCAT),
            Token(TokenType.GROUP_START, 1),
            Token(TokenType.LITERAL, "b"),
            Token(TokenType.RPAREN),
            Token(TokenType.EOF),
        ],
    ),

    "(a) -> (a)": (
        [
            Token(TokenType.LPAREN),
            Token(TokenType.LITERAL, "a"),
            Token(TokenType.RPAREN),
            Token(TokenType.EOF),
        ],
        [
            Token(TokenType.LPAREN),
            Token(TokenType.LITERAL, "a"),
            Token(TokenType.RPAREN),
            Token(TokenType.EOF),
        ],
    ),

    "a|b -> a|b": (
        [
            Token(TokenType.LITERAL, "a"),
            Token(TokenType.OR),
            Token(TokenType.LITERAL, "b"),
            Token(TokenType.EOF),
        ],
        [
            Token(TokenType.LITERAL, "a"),
            Token(TokenType.OR),
            Token(TokenType.LITERAL, "b"),
            Token(TokenType.EOF),
        ],
    ),

    "a+ -> a+": (
        [
            Token(TokenType.LITERAL, "a"),
            Token(TokenType.PLUS),
            Token(TokenType.EOF),
        ],
        [
            Token(TokenType.LITERAL, "a"),
            Token(TokenType.PLUS),
            Token(TokenType.EOF),
        ],
    ),

    "a{2,3} -> a{2,3}": (
        [
            Token(TokenType.LITERAL, "a"),
            Token(TokenType.RANGE, (2, 3)),
            Token(TokenType.EOF),
        ],
        [
            Token(TokenType.LITERAL, "a"),
            Token(TokenType.RANGE, (2, 3)),
            Token(TokenType.EOF),
        ],
    ),

    "a.b -> a.b": (
        [
            Token(TokenType.LITERAL, "a"),
            Token(TokenType.CONCAT),
            Token(TokenType.LITERAL, "b"),
            Token(TokenType.EOF),
        ],
        [
            Token(TokenType.LITERAL, "a"),
            Token(TokenType.CONCAT),
            Token(TokenType.LITERAL, "b"),
            Token(TokenType.EOF),
        ],
    ),
}


@pytest.mark.parametrize(
    "input_tokens, expected_tokens",
    CASES.values(),
    ids=CASES.keys(),
)
def test_insert_concat_tokens(input_tokens, expected_tokens):
    ast = AST()

    result = ast.insert_concat_tokens(input_tokens)

    assert result == expected_tokens

def test_apply_op_or_and_concat():
    ast = AST()

    # OR
    nodes = [
        Literal("a"),
        Literal("b"),
    ]

    ast.apply_op(Token(TokenType.OR), nodes)

    assert nodes == [
        Or(
            left=Literal("a"),
            right=Literal("b"),
        )
    ]

    # raises
    with pytest.raises(ValueError):
        ast.apply_op(Token(TokenType.OR), [])

    with pytest.raises(ValueError):
        ast.apply_op(Token(TokenType.OR), [Literal("a")])

    # CONCAT (len(nodes) < 2)
    nodes = [
        Literal("a"),
        Literal("b"),
    ]

    ast.apply_op(Token(TokenType.CONCAT), nodes)

    assert nodes == [
        Concat(
            left=Literal("a"),
            right=Literal("b"),
        )
    ]

    # raises (len(nodes) < 2)
    with pytest.raises(ValueError):
        ast.apply_op(Token(TokenType.CONCAT), [])

    with pytest.raises(ValueError):
        ast.apply_op(Token(TokenType.CONCAT), [Literal("a")])

    # unknown operator
    with pytest.raises(ValueError):
        ast.apply_op(Token(TokenType.EOF), [Literal("a"), Literal("a")])

def test_apply_postfix_plus_and_range():
    ast = AST()

    # PLUS
    nodes = [
        Literal("a"),
    ]

    ast.apply_postfix(Token(TokenType.PLUS), nodes)

    assert nodes == [
        Plus(
            expr=Literal("a"),
        )
    ]

    # raises (void nodes)
    with pytest.raises(ValueError):
        ast.apply_postfix(Token(TokenType.PLUS), [])

    # RANGE
    nodes = [
        Literal("a"),
    ]

    ast.apply_postfix(Token(TokenType.RANGE, (2, 3)), nodes)

    assert nodes == [
        Repeat(
            expr=Literal("a"),
            min=2,
            max=3,
        )
    ]

    # RANGE без верхней границы
    nodes = [
        Literal("a"),
    ]

    ast.apply_postfix(Token(TokenType.RANGE, (2, None)), nodes)

    assert nodes == [
        Repeat(
            expr=Literal("a"),
            min=2,
            max=None,
        )
    ]

    # raises
    with pytest.raises(ValueError):
        ast.apply_postfix(Token(TokenType.RANGE, (2, 3)), [])

    # unknown postfix operator
    with pytest.raises(ValueError):
        ast.apply_postfix(Token(TokenType.EOF), [Literal("a"), Literal("a")])


def test_precedence():
    ast = AST()

    res_or     = ast.precedence(Token(TokenType.OR))
    assert res_or == 1

    res_concat = ast.precedence(Token(TokenType.CONCAT))
    assert res_concat == 2

    res_other  = ast.precedence(Token(TokenType.EOF))
    assert res_other == 0

CASES = {
    "a -> Literal(a)": (
        [
            Token(TokenType.LITERAL, "a"),
            Token(TokenType.EOF),
        ],
        Literal("a"),
        None,
    ),

    "^ -> Epsilon": (
        [
            Token(TokenType.EPSILON),
            Token(TokenType.EOF),
        ],
        Epsilon(),
        None,
    ),

    r"\1 -> BackRef(1)": (
        [
            Token(TokenType.BACKREF, 1),
            Token(TokenType.EOF),
        ],
        BackRef(1),
        None,
    ),

    "a+ -> Plus(a)": (
        [
            Token(TokenType.LITERAL, "a"),
            Token(TokenType.PLUS),
            Token(TokenType.EOF),
        ],
        Plus(
            expr=Literal("a"),
        ),
        None,
    ),

    "( -> ValueError": (
        [
            Token(TokenType.LPAREN),
            Token(TokenType.EOF),
        ],
        None,
        ValueError,
    ),

    "(1: -> ValueError": (
        [
            Token(TokenType.GROUP_START),
            Token(TokenType.EOF),
        ],
        None,
        ValueError,
    ),

    "a|b: -> Or(a, b)" : (
        [
            Token(TokenType.LITERAL, "a"),
            Token(TokenType.OR),
            Token(TokenType.LITERAL, "b"),
            Token(TokenType.EOF),
        ],
        Or(Literal("a"), Literal("b")),
        None,
    ),

    "ab|c: -> Or(Concat(a, b), c)": (
        [
            Token(TokenType.LITERAL, "a"),
            Token(TokenType.LITERAL, "b"),
            Token(TokenType.OR),
            Token(TokenType.LITERAL, "c"),
            Token(TokenType.EOF),
        ],
        Or(
            left=Concat(
                left=Literal("a"),
                right=Literal("b"),
            ),
            right=Literal("c"),
        ),
        None,
    ),

    "a|bc: -> Or(a, Concat(b, c))": (
        [
            Token(TokenType.LITERAL, "a"),
            Token(TokenType.OR),
            Token(TokenType.LITERAL, "b"),
            Token(TokenType.LITERAL, "c"),
            Token(TokenType.EOF),
        ],
        Or(
            left=Literal("a"),
            right=Concat(
                left=Literal("b"),
                right=Literal("c"),
            ),
        ),
        None,
    ),
    ") -> ValueError": (
        [
            Token(TokenType.RPAREN),
            Token(TokenType.EOF),
        ],
        None,
        ValueError,
    ),
    "(ab) -> Concat(a, b)": (
        [
            Token(TokenType.LITERAL, "a"),
            Token(TokenType.CONCAT),
            Token(TokenType.LITERAL, "b"),
            Token(TokenType.EOF),
        ],
        Concat(
            left=Literal("a"),
            right=Literal("b")
        ),
        None,
    ),
    "(1:) -> ValueError": (
        [
            Token(TokenType.GROUP_START, 1),
            Token(TokenType.EOF),
        ],
        None,
        ValueError
    ),
    "(1:ab) -> Group(1, Concat(a, b))": (
        [
            Token(TokenType.GROUP_START, 1),
            Token(TokenType.LITERAL, "a"),
            Token(TokenType.CONCAT),
            Token(TokenType.LITERAL, "b"),
            Token(TokenType.RPAREN),
            Token(TokenType.EOF),
        ],
        Group(
            num=1,
            expr=Concat(
                left=Literal("a"),
                right=Literal("b")
            )
        ),
        None,
    ),
    "(1:b+) -> Group(1, Plus(b))": (
        [
            Token(TokenType.GROUP_START, 1),
            Token(TokenType.LITERAL, "b"),
            Token(TokenType.PLUS),
            Token(TokenType.RPAREN),
            Token(TokenType.EOF),
        ],
        Group(
            num=1,
            expr=Plus(Literal("b")),
        ),
        None,
    ),
    "empty -> ValueError": (
        [
            Token(TokenType.EOF),
        ],
        None,
        ValueError,
    ),

    "() -> ValueError": (
        [
            Token(TokenType.LPAREN),
            Token(TokenType.RPAREN),
            Token(TokenType.EOF),
        ],
        None,
        ValueError,
    ),
}


@pytest.mark.parametrize("case_name", CASES.keys())
def test_parse(case_name):
    ast = AST()

    tokens, expected_ast, expected_error = CASES[case_name]

    if expected_error is not None:
        with pytest.raises(expected_error):
            ast.parse(tokens)
    else:
        result = ast.parse(tokens)
        assert result == expected_ast

def test_analyze_capture_groups():
    ast = AST()

    tokens = [
        Token(TokenType.GROUP_START, 1),
        Token(TokenType.LITERAL, "a"),
        Token(TokenType.RPAREN),
        Token(TokenType.EOF),
    ]

    result = ast.analyze_capture_groups(tokens)

    assert result is True

    tokens = [
        Token(TokenType.LITERAL, "a"),
        Token(TokenType.OR),
        Token(TokenType.LITERAL, "b"),
        Token(TokenType.EOF),
    ]

    result = ast.analyze_capture_groups(tokens)

    assert result is False

def test_analyze_backreferences():
    ast = AST()

    tokens = [
        Token(TokenType.BACKREF, 1),
        Token(TokenType.EOF),
    ]

    result = ast.analyze_backreferences(tokens)

    assert result is True

    tokens = [
        Token(TokenType.LITERAL, "a"),
        Token(TokenType.OR),
        Token(TokenType.LITERAL, "b"),
        Token(TokenType.EOF),
    ]

    result = ast.analyze_backreferences(tokens)

    assert result is False