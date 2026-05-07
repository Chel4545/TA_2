from dataclasses import dataclass
from pythonProject1.logic.Tokenizer import Token, TokenType


class Node:
    pass


# r
@dataclass
class Literal(Node):  # alpha
    char: str


# ^
@dataclass
class Epsilon(Node):
    pass


# .
@dataclass
class Concat(Node):
    left: Node
    right: Node


# |
@dataclass
class Or(Node):
    left: Node
    right: Node


# +
@dataclass
class Plus(Node):
    expr: Node


# {x, y}
@dataclass
class Repeat(Node):
    expr: Node
    min: int
    max: int | None


# (n:r)
@dataclass
class Group(Node):
    num: int
    expr: Node


# \n
@dataclass
class BackRef(Node):
    num: int


class AST:
    def __init__(self):
        pass # мб сюда добавить вершину

    # Добавить операцию конкатенации между стыками
    def insert_concat_tokens(self, tokens: list[Token]) -> list[Token]:
        result: list[Token] = []

        for i, token in enumerate(tokens):
            result.append(token)

            if i + 1 < len(tokens):
                next_token = tokens[i + 1]

                if token.type.is_atom_end and next_token.type.is_atom_start:
                    result.append(Token(TokenType.CONCAT))

        return result

    def apply_op(self, op: Token, nodes: list[Node]) -> None:
        if op.type == TokenType.OR:
            if len(nodes) < 2:
                raise ValueError("Недостаточно операндов для оператора '|'")

            right = nodes.pop()
            left = nodes.pop()
            nodes.append(Or(left, right))
            return

        if op.type == TokenType.CONCAT:
            if len(nodes) < 2:
                raise ValueError("Недостаточно операндов для конкатенации")

            right = nodes.pop()
            left = nodes.pop()
            nodes.append(Concat(left, right))
            return

        raise ValueError(f"Неизвестный оператор: {op.type}")

    def apply_postfix(self, token: Token, nodes: list[Node]) -> None:
        if not nodes:
            raise ValueError(f"Нет операнда для постфиксного оператора {token.type}")

        expr = nodes.pop()

        if token.type == TokenType.PLUS:
            nodes.append(Plus(expr))
            return

        if token.type == TokenType.RANGE:
            x, y = token.value
            nodes.append(Repeat(expr, x, y))
            return

        raise ValueError(f"Неизвестный постфиксный оператор: {token.type}")

    def precedence(self, token: Token) -> int:
        if token.type == TokenType.OR:
            return 1

        if token.type == TokenType.CONCAT:
            return 2

        return 0

    def parse(self, tokens: list[Token]) -> Node:
        tokens = self.insert_concat_tokens(tokens)

        nodes: list[Node] = []
        ops: list[Token] = []

        i = 0

        for token in tokens:
            if token.type == TokenType.EOF:
                break

            if token.type == TokenType.LITERAL:
                nodes.append(Literal(token.value))

            elif token.type == TokenType.EPSILON:
                nodes.append(Epsilon())

            elif token.type == TokenType.BACKREF:
                nodes.append(BackRef(token.value))

            elif token.type in {TokenType.PLUS, TokenType.RANGE}:
                self.apply_postfix(token, nodes)

            elif token.type == TokenType.LPAREN:
                ops.append(token)

            elif token.type == TokenType.GROUP_START:
                ops.append(token)

            elif token.type in {TokenType.OR, TokenType.CONCAT}:
                while (
                    ops
                    and ops[-1].type not in {TokenType.LPAREN, TokenType.GROUP_START}
                    and self.precedence(ops[-1]) >= self.precedence(token)
                ):
                    self.apply_op(ops.pop(), nodes)

                ops.append(token)

            elif token.type == TokenType.RPAREN:
                while ops and ops[-1].type not in {TokenType.LPAREN, TokenType.GROUP_START}:
                    self.apply_op(ops.pop(), nodes)

                if not ops:
                    raise ValueError("Лишняя закрывающая скобка")

                open_token = ops.pop()

                if open_token.type == TokenType.GROUP_START:
                    if not nodes:
                        raise ValueError("Пустая группа захвата")

                    expr = nodes.pop()
                    nodes.append(Group(open_token.value, expr))

            else:
                raise ValueError(f"Неизвестный токен: {token.type}")

            i += 1

        while ops:
            if ops[-1].type in {TokenType.LPAREN, TokenType.GROUP_START}:
                raise ValueError("Незакрытая скобка")

            self.apply_op(ops.pop(), nodes)

        if len(nodes) != 1:
            raise ValueError("Некорректное выражение")

        return nodes[0]

    def analyze_capture_groups(self, tokens: list[Token]) -> bool:
        for token in tokens:
            if token.type == TokenType.GROUP_START:
                return True

        return False

    def analyze_backreferences(self, tokens: list[Token]) -> bool:
        for token in tokens:
            if token.type == TokenType.BACKREF:
                return True

        return False