import pytest

from pythonProject1.logic.Tokenizer import Tokenizer, Token, TokenType

def test_literal():
    tokenizer = Tokenizer("a")

    assert tokenizer.tokens == [
        Token(TokenType.LITERAL, "a"),
        Token("EOF"),
    ]

def test_severel_literals():
    tokenizer = Tokenizer("abc")

    assert tokenizer.tokens == [
        Token(TokenType.LITERAL, "a"),
        Token(TokenType.LITERAL, "b"),
        Token(TokenType.LITERAL, "c"),
        Token(TokenType.EOF),
    ]

def test_or_operator():
    tokenizer = Tokenizer("a|b")

    assert tokenizer.tokens == [
        Token(TokenType.LITERAL, "a"),
        Token(TokenType.OR),
        Token(TokenType.LITERAL, "b"),
        Token(TokenType.EOF),
    ]

def test_plus_operator():
    tokenizer = Tokenizer("a+")

    assert tokenizer.tokens == [
        Token(TokenType.LITERAL, "a"),
        Token(TokenType.PLUS),
        Token(TokenType.EOF),
    ]


def test_concat_operator():
    tokenizer = Tokenizer("a.b")

    assert tokenizer.tokens == [
        Token(TokenType.LITERAL, "a"),
        Token(TokenType.CONCAT),
        Token(TokenType.LITERAL, "b"),
        Token(TokenType.EOF),
    ]

def test_epsilon():
    tokenizer = Tokenizer("^")

    assert tokenizer.tokens == [
        Token(TokenType.EPSILON),
        Token(TokenType.EOF),
    ]

def test_parentheses():
    tokenizer = Tokenizer("(a)")

    assert tokenizer.tokens == [
        Token(TokenType.LPAREN),
        Token(TokenType.LITERAL, "a"),
        Token(TokenType.RPAREN),
        Token(TokenType.EOF),
    ]

def test_capture_group_start():
    tokenizer = Tokenizer("(1:a)")

    assert tokenizer.tokens == [
        Token(TokenType.GROUP_START, 1),
        Token(TokenType.LITERAL, "a"),
        Token(TokenType.RPAREN),
        Token(TokenType.EOF),
    ]

def test_backreference():
    tokenizer = Tokenizer(r"\1")

    assert tokenizer.tokens == [
        Token(TokenType.BACKREF, 1),
        Token(TokenType.EOF),
    ]

def test_range_with_upper_bound():
    tokenizer = Tokenizer("a{2,5}")

    assert tokenizer.tokens == [
        Token(TokenType.LITERAL, "a"),
        Token(TokenType.RANGE, (2, 5)),
        Token(TokenType.EOF),
    ]


def test_range_without_upper_bound():
    tokenizer = Tokenizer("a{2,}")

    assert tokenizer.tokens == [
        Token(TokenType.LITERAL, "a"),
        Token(TokenType.RANGE, (2, None)),
        Token(TokenType.EOF),
    ]


def test_escaped_or():
    tokenizer = Tokenizer("#|")

    assert tokenizer.tokens == [
        Token(TokenType.LITERAL, "|"),
        Token(TokenType.EOF),
    ]


def test_escaped_plus():
    tokenizer = Tokenizer("#+")

    assert tokenizer.tokens == [
        Token(TokenType.LITERAL, "+"),
        Token(TokenType.EOF),
    ]


def test_escaped_hash():
    tokenizer = Tokenizer("##")

    assert tokenizer.tokens == [
        Token(TokenType.LITERAL, "#"),
        Token(TokenType.EOF),
    ]


def test_error_after_hash():
    with pytest.raises(ValueError):
        Tokenizer("#")


def test_error_backreference_without_number():
    with pytest.raises(ValueError):
        Tokenizer(r"\\a")


def test_error_bad_range_without_comma():
    with pytest.raises(ValueError):
        Tokenizer("a{2}")


def test_error_bad_range_without_closing_brace():
    with pytest.raises(ValueError):
        Tokenizer("a{2,5")