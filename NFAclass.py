from dataclasses import dataclass, field
from ASTclass import Literal, Epsilon, Concat, Union, Plus, Repeat, Group, BackRef

@dataclass
class Edge:
    to_state: int
    symbol: str | None = None


@dataclass
class State:
    id: int
    is_accepting: bool = False
    edges: list[Edge] = field(default_factory=list)


@dataclass
class Fragment:
    start: int
    accept: int

class NFA:
    def __init__(self):
        self.states: dict[int, State] = {}
        self.next_id = 0
        self.start: int | None = None
        self.accept: int | None = None
        self.postorder_nodes = []

    # создание элементов графа
    def new_state(self) -> int:
        state_id = self.next_id
        self.next_id += 1
        self.states[state_id] = State(state_id)
        return state_id

    def add_edge(self, from_state: int, to_state: int, symbol: str | None = None):
        self.states[from_state].edges.append(Edge(to_state, symbol))

    def mark_accepting(self, state_id: int):
        self.states[state_id].is_accepting = True


    # рекурсивный обход
    def postorder(self, node):
        if node is None:
            return

        if isinstance(node, (Concat, Union)):
            self.postorder(node.left)
            self.postorder(node.right)
            self.postorder_nodes.append(node)

        elif isinstance(node, (Plus, Repeat, Group)):
            self.postorder(node.expr)
            self.postorder_nodes.append(node)

        elif isinstance(node, (Literal, Epsilon, BackRef)):
            self.postorder_nodes.append(node)

        else:
            raise ValueError(f"Неизвестный тип узла: {type(node).__name__}")

    #делаем массив всех узолв дерева в нужном порядке
    def get_postorder(self, ast_root):
        self.postorder_nodes = []
        self.postorder(ast_root)
        return self.postorder_nodes

    #делаем пары как в лекции
    def build_literal(self, node: Literal) -> Fragment:
        s = self.new_state()
        f = self.new_state()
        self.add_edge(s, f, node.char)
        return Fragment(s, f)

    def build_epsilon(self) -> Fragment:
        s = self.new_state()
        f = self.new_state()
        self.add_edge(s, f, None)
        return Fragment(s, f)


    #патерны для операций
    def apply_concat(self, left: Fragment, right: Fragment) -> Fragment:
        self.add_edge(left.accept, right.start, None)
        return Fragment(left.start, right.accept)

    def apply_union(self, left: Fragment, right: Fragment) -> Fragment:
        s = self.new_state()
        f = self.new_state()

        self.add_edge(s, left.start, None)
        self.add_edge(s, right.start, None)

        self.add_edge(left.accept, f, None)
        self.add_edge(right.accept, f, None)

        return Fragment(s, f)

    def apply_plus(self, inner: Fragment) -> Fragment:
        s = self.new_state()
        f = self.new_state()

        self.add_edge(s, inner.start, None)
        self.add_edge(inner.accept, inner.start, None)
        self.add_edge(inner.accept, f, None)

        return Fragment(s, f)

    #создание графа
    def build_nfa(self, ast_root) -> Fragment:
        order = self.get_postorder(ast_root)
        stack: list[Fragment] = []

        for node in order:
            if isinstance(node, Literal):
                stack.append(self.build_literal(node))

            elif isinstance(node, Epsilon):
                stack.append(self.build_epsilon())

            elif isinstance(node, Concat):
                if len(stack) < 2:
                    raise ValueError("Недостаточно фрагментов для Concat")
                right = stack.pop()
                left = stack.pop()
                stack.append(self.apply_concat(left, right))

            elif isinstance(node, Union):
                if len(stack) < 2:
                    raise ValueError("Недостаточно фрагментов для Union")
                right = stack.pop()
                left = stack.pop()
                stack.append(self.apply_union(left, right))

            elif isinstance(node, Plus):
                if not stack:
                    raise ValueError("Недостаточно фрагментов для Plus")
                inner = stack.pop()
                stack.append(self.apply_plus(inner))

            elif isinstance(node, Group):
                # Группа захвата пока не меняет НКА
                if not stack:
                    raise ValueError("Недостаточно фрагментов для Group")
                inner = stack.pop()
                stack.append(inner)

            elif isinstance(node, BackRef):
                raise ValueError("BackRef нельзя компилировать в NFA")

            elif isinstance(node, Repeat):
                raise NotImplementedError("Repeat пока не реализован")

            else:
                raise ValueError(f"Неизвестный тип узла: {type(node).__name__}")

        if len(stack) != 1:
            raise ValueError("Ошибка построения NFA: на стеке остался не один фрагмент")

        result = stack.pop()
        self.start = result.start
        self.accept = result.accept
        self.mark_accepting(self.accept)

        return result

