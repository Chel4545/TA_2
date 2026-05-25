from dataclasses import dataclass, field

from pygments.lexers.robotframework import Variable

from pythonProject1.logic.ASTclass import Literal, Epsilon, Concat, Or, Plus, Repeat, Group, BackRef, Node
from pythonProject1.logic.MatchResult import MatchResult
from collections import deque

@dataclass
class Edge:
    to_state: int
    symbol: str | None = None
    group_start: int | None = None
    group_end: int | None = None

@dataclass
class State:
    id: int
    is_accepting: bool = False
    edges: list[Edge] = field(default_factory=list) #синтаксис для создания независимых list


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

    # создание элементов графа
    def new_state(self) -> int:
        state_id = self.next_id
        self.next_id += 1
        self.states[state_id] = State(state_id)
        return state_id

    def add_edge(
            self,
            from_state: int,
            to_state: int,
            symbol: str | None = None,
            group_start: int | None = None,
            group_end: int | None = None):
        self.states[from_state].edges.append(
            Edge(
                to_state=to_state,
                symbol=symbol,
                group_start=group_start,
                group_end=group_end,
            )
        )

    def mark_accepting(self, state_id: int):
        self.states[state_id].is_accepting = True

    # проверки
    @staticmethod
    def validate_nfa(nfa):
        if nfa is None:
            raise ValueError("NFA None")

        if nfa.states is None:
            raise ValueError("NFA.states None")

        if nfa.start is None:
            raise ValueError("NFA не имеет стартового состояния")

    @staticmethod
    def validate_fragment(fragment: Fragment) -> None:
        if fragment is None:
            raise ValueError(f"не может быть None")

        if not isinstance(fragment, Fragment):
            raise ValueError(f"должен быть Fragment")

        if fragment.start is None:
            raise ValueError(f"start не может быть None")

        if fragment.accept is None:
            raise ValueError(f"accept не может быть None")

    #патерны для операций
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

    # a.b
    def apply_concat(self, left: Fragment, right: Fragment) -> Fragment:
        self.validate_fragment(left)
        self.validate_fragment(right)

        self.add_edge(left.accept, right.start, None)
        return Fragment(left.start, right.accept)

    # a|b
    def apply_union(self, left: Fragment, right: Fragment) -> Fragment:
        self.validate_fragment(left)
        self.validate_fragment(right)

        s = self.new_state()
        f = self.new_state()

        self.add_edge(s, left.start, None)
        self.add_edge(s, right.start, None)

        self.add_edge(left.accept, f, None)
        self.add_edge(right.accept, f, None)

        return Fragment(s, f)

    # r+
    def apply_plus(self, inner: Fragment) -> Fragment:
        self.validate_fragment(inner)

        s = self.new_state()
        f = self.new_state()

        self.add_edge(s, inner.start, None)
        self.add_edge(inner.accept, inner.start, None)
        self.add_edge(inner.accept, f, None)

        return Fragment(s, f)

    # r*
    def apply_star(self, inner: Fragment) -> Fragment:
        self.validate_fragment(inner)

        s = self.new_state()
        f = self.new_state()

        self.add_edge(s, inner.start, None)

        self.add_edge(s, f, None)

        self.add_edge(inner.accept, inner.start, None)

        self.add_edge(inner.accept, f, None)

        return Fragment(s, f)

    # r?
    def apply_optional(self, inner: Fragment) -> Fragment:
        self.validate_fragment(inner)

        s = self.new_state()
        f = self.new_state()

        self.add_edge(s, inner.start, None)
        self.add_edge(inner.accept, f, None)

        self.add_edge(s, f, None)

        return Fragment(s, f)

    # copy
    def copy_fragment(self, fragment: Fragment) -> Fragment:
        self.validate_fragment(fragment)

        mapping: dict[int, int] = {}

        def get_or_create_copy(old_state: int) -> int:
            if old_state not in mapping:
                mapping[old_state] = self.new_state()
            return mapping[old_state]

        # создаём копию стартового состояния
        get_or_create_copy(fragment.start)

        queue = deque([fragment.start])
        visited: set[int] = set()

        while queue:
            old_from = queue.popleft()

            if old_from in visited:
                continue

            visited.add(old_from)

            new_from = get_or_create_copy(old_from)

            if old_from == fragment.accept:
                continue

            for edge in self.states[old_from].edges:
                old_to = edge.to_state
                new_to = get_or_create_copy(old_to)

                self.add_edge(
                    from_state=new_from,
                    to_state=new_to,
                    symbol=edge.symbol,
                    group_start=edge.group_start,
                    group_end=edge.group_end,
                )

                if old_to not in visited:
                    queue.append(old_to)

        return Fragment(
            start=mapping[fragment.start],
            accept=mapping[fragment.accept],
        )

    # функции для r{}
    # {x:} нижняя граница
    def apply_min_repeat(self, inner: Fragment, min_count: int) -> Fragment:
        self.validate_fragment(inner)

        if min_count < 0:
            raise ValueError("Нижняя граница Repeat не может быть отрицательной")

        result = inner

        for _ in range(1, min_count):
            copied = self.copy_fragment(inner)
            result = self.apply_concat(result, copied)

        return result

    # {:y} верхняя граница
    def apply_max_repeat(self, result: Fragment, inner: Fragment, diff: int) -> Fragment:
        self.validate_fragment(result)
        self.validate_fragment(inner)

        if diff < 0:
            raise ValueError("Разность max - min не может быть отрицательной")

        for _ in range(diff):
            copied = self.copy_fragment(inner)
            optional = self.apply_optional(copied)
            result = self.apply_concat(result, optional)

        return result

    # main {x:y}
    def apply_repeat(self, inner: Fragment, min_count: int, max_count: int | None) -> Fragment:
        self.validate_fragment(inner)

        if min_count < 0:
            raise ValueError("Нижняя граница Repeat не может быть отрицательной")

        if max_count is not None and max_count < min_count:
            raise ValueError("Верхняя граница Repeat меньше нижней")

        if min_count == 0:
            result = self.build_epsilon()
        else:
            # делаем минимум
            result = self.apply_min_repeat(inner, min_count)

        # r{x,}
        if max_count is None:
            copied = self.copy_fragment(inner)
            star = self.apply_star(copied)
            return self.apply_concat(result, star)

        # r{x,y}
        diff = max_count - min_count

        return self.apply_max_repeat(
            result=result,
            inner=inner,
            diff=diff,
        )

    # (n:r)
    def apply_group(self, inner: Fragment, group_num: int) -> Fragment:
        self.validate_fragment(inner)

        s = self.new_state()
        f = self.new_state()

        self.add_edge(
            from_state=s,
            to_state=inner.start,
            symbol=None,
            group_start=group_num,
        )

        self.add_edge(
            from_state=inner.accept,
            to_state=f,
            symbol=None,
            group_end=group_num,
        )

        return Fragment(s, f)

    #создание графа
    def build_nfa(self, ast_root) -> Fragment:
        if ast_root is None:
            raise ValueError("AST не может быть None")
        if not isinstance(ast_root, Node):
            raise ValueError("AST не правильной структуры данных")

        def visit(node) -> Fragment:
            if node is None:
                raise ValueError("AST не может быть None")
            if not isinstance(ast_root, Node):
                raise ValueError("AST не правильной структуры данных")

            if isinstance(node, Literal):
                return self.build_literal(node)

            if isinstance(node, Epsilon):
                return self.build_epsilon()

            if isinstance(node, Concat):
                left = visit(node.left)
                right = visit(node.right)
                return self.apply_concat(left, right)

            if isinstance(node, Or):
                left = visit(node.left)
                right = visit(node.right)
                return self.apply_union(left, right)

            if isinstance(node, Plus):
                inner = visit(node.expr)
                return self.apply_plus(inner)

            if isinstance(node, Group):
                inner = visit(node.expr)
                return self.apply_group(inner, node.num)

            if isinstance(node, BackRef):
                raise ValueError("BackRef нельзя компилировать в NFA")

            if isinstance(node, Repeat):
                inner = visit(node.expr)
                return self.apply_repeat(inner, node.min, node.max)

            raise ValueError(f"Неизвестный тип узла: {type(node).__name__}")

        result = visit(ast_root)

        self.start = result.start
        self.accept = result.accept
        self.mark_accepting(self.accept)

        return result


    # поиск(если есть группа захвата)

    def transition(self, state_id: int, symbol: str | None) -> list[Edge]:
        result: list[Edge] = []

        for edge in self.states[state_id].edges:
            if edge.symbol == symbol:
                result.append(edge)

        return result

    def search_from_position(self, data: str, start_pos: int):
        visited = set()
        best_result = None

        def dfs(state_id: int,
                pos: int,
                group_starts: dict[int, int],
                groups: dict[int, str],
        ):
            nonlocal best_result

            # фикс циклов только из E
            key = (
                state_id,
                pos,
                tuple(sorted(group_starts.items())),
                tuple(sorted(groups.items())),
            )

            if key in visited:
                return

            visited.add(key)

            state = self.states[state_id]

            # Если состояние принимающее — обновляем лучший результат
            if state.is_accepting:
                current_result = MatchResult(
                    start=start_pos,
                    end=pos,
                    value=data[start_pos:pos],
                    groups=dict(groups),
                )

                if best_result is None or current_result.end > best_result.end:
                    best_result = current_result

            # E переходы включая
            for edge in self.transition(state_id, None):
                new_group_starts = dict(group_starts)
                new_groups = dict(groups)

                # добавляем 3 параметр - начало группы захвата
                if edge.group_start is not None:
                    new_group_starts[edge.group_start] = pos

                # получили переход с выходом из группы
                if edge.group_end is not None:
                    group_num = edge.group_end

                    if group_num not in new_group_starts:
                        continue

                    group_start_pos = new_group_starts[group_num]
                    new_groups[group_num] = data[group_start_pos:pos]

                dfs(edge.to_state, pos, new_group_starts, new_groups)

            # переходы по текущему символу
            if pos < len(data):
                current_symbol = data[pos]

                for edge in self.transition(state_id, current_symbol):
                    dfs(
                        edge.to_state,
                        pos + 1,
                        dict(group_starts),
                        dict(groups),
                    )

        dfs(self.start, start_pos,{},{})

        return best_result

    def search_with_groups(self, data: str):
        if self.start is None:
            return None

        for start_pos in range(len(data) + 1):
            result = self.search_from_position(data, start_pos)

            if result is not None:
                return result

        return None

