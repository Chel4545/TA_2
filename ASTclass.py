from dataclasses import dataclass
from tokenizer import Token

class Node:
    pass

# r
@dataclass
class Literal(Node): #alpha
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
class Union(Node):
    left: Node
    right: Node

# +
@dataclass
class Plus(Node):
    expr: Node

# {х, y}
@dataclass
class Repeat(Node):
    expr: Node
    min: int
    max: int | None

# (n:)
@dataclass
class Group(Node): # (n:r)
    num: int
    expr: Node

# \n
@dataclass
class BackRef(Node):
    num: int


class AST:
    def __init__(self):
        pass

    def is_atom_end(self, token: Token) -> bool:
        return token.type in {
            'LITERAL', 'BACKREF', 'EPSILON', 'RPAREN', 'PLUS', 'RANGE'
        }

    def is_atom_start(self, token: Token) -> bool:
        return token.type in {
            'LITERAL', 'BACKREF', 'EPSILON', 'LPAREN', 'GROUP_START'
        }

    def insert_concat_tokens(self, tokens: list[Token]) -> list[Token]:
        result: list[Token] = []

        filtered = [t for t in tokens if t.type != 'EOF']

        for i, token in enumerate(filtered):
            result.append(token)

            if i + 1 < len(filtered):
                nxt = filtered[i + 1]
                if self.is_atom_end(token) and self.is_atom_start(nxt):
                    result.append(Token('CONCAT'))

        result.append(Token('EOF'))
        return result


    def apply_op(self, op: Token, nodes: list[Node]) -> None:
        if op.type == 'OR':
            if len(nodes) < 2:
                raise ValueError("Недостаточно операндов для оператора '|'")
            right = nodes.pop()
            left = nodes.pop()
            nodes.append(Union(left, right))
            return

        if op.type == 'CONCAT':
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

        if token.type == 'PLUS':
            nodes.append(Plus(expr))
            return

        if token.type == 'RANGE':
            x, y = token.value
            nodes.append(Repeat(expr, x, y))
            return

        raise ValueError(f"Неизвестный постфиксный оператор: {token.type}")

    def precedence(self, token: Token) -> int:
        if token.type == 'OR':
            return 1
        if token.type == 'CONCAT':
            return 2
        return 0

    def parse(self, tokens: list[Token]) -> Node:
        tokens = self.insert_concat_tokens(tokens)

        nodes: list[Node] = []
        ops: list[Token] = []

        i = 0
        while i < len(tokens):
            token = tokens[i]

            if token.type == 'LITERAL':
                nodes.append(Literal(token.value))

            elif token.type == 'EPSILON':
                nodes.append(Epsilon())

            elif token.type == 'BACKREF':
                nodes.append(BackRef(token.value))

            elif token.type in {'PLUS', 'RANGE'}:
                self.apply_postfix(token, nodes)

            elif token.type == 'LPAREN':
                ops.append(token)

            elif token.type == 'GROUP_START':
                ops.append(token)

            elif token.type in {'OR', 'CONCAT'}:
                while (
                    ops and ops[-1].type not in {'LPAREN', 'GROUP_START'}
                        and self.precedence(ops[-1]) >= self.precedence(token)
                ):
                    self.apply_op(ops.pop(), nodes)
                ops.append(token)

            elif token.type == 'RPAREN':
                while ops and ops[-1].type not in {'LPAREN', 'GROUP_START'}:
                    self.apply_op(ops.pop(), nodes)

                if not ops:
                    raise ValueError("Лишняя закрывающая скобка")

                open_token = ops.pop()

                if open_token.type == 'GROUP_START':
                    if not nodes:
                        raise ValueError("Пустая группа захвата")
                    expr = nodes.pop()
                    nodes.append(Group(open_token.value, expr))

            elif token.type == 'EOF':
                break

            else:
                raise ValueError(f"Неизвестный токен: {token.type}")

            i += 1

        while ops:
            if ops[-1].type in {'LPAREN', 'GROUP_START'}:
                raise ValueError("Незакрытая скобка")
            self.apply_op(ops.pop(), nodes)

        if len(nodes) != 1:
            raise ValueError("Некорректное выражение")

        return nodes[0]

    def analyze_capture_groups(self, tokens: list[Token]) -> bool:
        for token in tokens:
            if token.type == 'GROUP_START':
                return True

        return False

    def analyze_backreferences(self, tokens: list[Token]) -> bool:
        for token in tokens:
            if token.type == 'BACKREF':
                return True

        return False