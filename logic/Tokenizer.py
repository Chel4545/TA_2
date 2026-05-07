from dataclasses import dataclass
from enum import StrEnum


class TokenType(StrEnum):
    LITERAL = "LITERAL"
    OR = "OR"
    CONCAT = "CONCAT"
    PLUS = "PLUS"
    RANGE = "RANGE"
    EPSILON = "EPSILON"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    GROUP_START = "GROUP_START"
    BACKREF = "BACKREF"
    EOF = "EOF"

    @property #убрать скобки
    def is_atom_end(self) -> bool:
        return self in {
            TokenType.LITERAL,
            TokenType.BACKREF,
            TokenType.EPSILON,
            TokenType.RPAREN,
            TokenType.PLUS,
            TokenType.RANGE,
        }

    @property
    def is_atom_start(self) -> bool:
        return self in {
            TokenType.LITERAL,
            TokenType.BACKREF,
            TokenType.EPSILON,
            TokenType.LPAREN,
            TokenType.GROUP_START,
        }

@dataclass
class Token:
    type: TokenType
    value: any = None

class Tokenizer:

    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.tokens = self.tokenize()

    def current(self) -> str | None:
        if self.pos >= len(self.text):
            return None
        return self.text[self.pos]

    def advance(self, step: int = 1):
        self.pos += step

    def read_number(self) -> int:
        if self.current() is None or not self.current().isdigit():
            raise ValueError(f"Ожидалось число на позиции {self.pos}")

        start = self.pos
        while self.current() is not None and self.current().isdigit():
            self.advance()

        return int(self.text[start:self.pos])

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []

        while self.pos < len(self.text):
            c = self.current()

            # экранирование
            if c == '#':
                self.advance()
                if self.current() is None:
                    raise ValueError("После '#' нет символа")
                tokens.append(Token(TokenType.LITERAL, self.current()))
                self.advance()
                continue

            # \n
            if c == '\\':
                self.advance()
                num = self.read_number()
                tokens.append(Token(TokenType.BACKREF, num))
                continue

            # встретили (
            if c == '(':
                saved_pos = self.pos
                self.advance()

                # нумерованная группа захвата
                if self.current() is not None and self.current().isdigit():
                    num = self.read_number()
                    if self.current() == ':':
                        self.advance()
                        tokens.append(Token(TokenType.GROUP_START, num))
                        continue

                # обычная группа
                self.pos = saved_pos
                tokens.append(Token(TokenType.LPAREN))
                self.advance()
                continue

            # заверщающая скобка ')'
            if c == ')':
                tokens.append(Token(TokenType.RPAREN))
                self.advance()
                continue

            # range {x,y}
            if c == '{':
                self.advance()

                x = self.read_number()
                if self.current() != ',':
                    raise ValueError(f"Ожидалась ',' в диапазоне на позиции {self.pos}")
                self.advance()

                y = None
                if self.current() is not None and self.current().isdigit():
                    y = self.read_number()

                if self.current() != '}':
                    raise ValueError(f"Ожидалась '}}' в диапазоне на позиции {self.pos}")
                self.advance()

                tokens.append(Token(TokenType.RANGE, (x, y)))
                continue


            # Операторы
            if c == '|':
                tokens.append(Token(TokenType.OR))
                self.advance()
                continue

            if c == '+':
                tokens.append(Token(TokenType.PLUS))
                self.advance()
                continue

            if c == '.':
                tokens.append(Token(TokenType.CONCAT))
                self.advance()
                continue

            if c == '^':
                tokens.append(Token(TokenType.EPSILON))
                self.advance()
                continue

            # Обычный символ
            tokens.append(Token(TokenType.LITERAL, c))
            self.advance()

        tokens.append(Token(TokenType.EOF))
        return tokens