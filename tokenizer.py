from dataclasses import dataclass
from typing import Any

@dataclass
class Token:
    type: str
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
                tokens.append(Token('LITERAL', self.current()))
                self.advance()
                continue

            # \n
            if c == '\\':
                self.advance()
                num = self.read_number()
                tokens.append(Token('BACKREF', num))
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
                        tokens.append(Token('GROUP_START', num))
                        continue

                # обычная группа
                self.pos = saved_pos
                tokens.append(Token('LPAREN'))
                self.advance()
                continue

            # заверщающая скобка ')'
            if c == ')':
                tokens.append(Token('RPAREN'))
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

                tokens.append(Token('RANGE', (x, y)))
                continue


            # Операторы
            if c == '|':
                tokens.append(Token('OR'))
                self.advance()
                continue

            if c == '+':
                tokens.append(Token('PLUS'))
                self.advance()
                continue

            if c == '.':
                tokens.append(Token('CONCAT'))
                self.advance()
                continue

            if c == '^':
                tokens.append(Token('EPSILON'))
                self.advance()
                continue

            # Обычный символ
            tokens.append(Token('LITERAL', c))
            self.advance()

        tokens.append(Token('EOF'))
        return tokens