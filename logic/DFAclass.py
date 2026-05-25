from dataclasses import dataclass, field

from pythonProject1.logic.NFAclass import NFA


#надо будет нфа сделать полем
@dataclass
class DFAEdge:
    to_state: int
    symbol: str

#зачем хранить несколько id
@dataclass
class DFAState:
    id: int
    is_accepting: bool = False
    edges: list[DFAEdge] = field(default_factory=list)

class DFA:
    def __init__(self):
        self.states: dict[int, DFAState] = {}
        self.start: int | None = None
        self.next_id = 0
        self.alphabet: set[str] = set()

    @staticmethod
    def validate_dfa(dfa):
        if dfa is None:
            raise ValueError("DFA None")

        if dfa.states is None:
            raise ValueError("DFA.states None")

        if dfa.start is None:
            raise ValueError("DFA не имеет стартового состояния")

    # собираем алфавит
    def get_alphabet(self, nfa) -> set[str]:
        NFA.validate_nfa(nfa)

        alphabet = set()

        for state in nfa.states.values():
            for edge in state.edges:
                if edge.symbol is not None:
                    alphabet.add(edge.symbol)

        return alphabet

    # проходимся из текущего множества по E
    def epsilon_closure(self, nfa, state_ids: set[int]) -> frozenset[int]:
        NFA.validate_nfa(nfa)
        if state_ids is None:
            raise ValueError("Отсутствуют вершины с E переходами")

        stack = list(state_ids)
        closure = set(state_ids)

        while stack:
            current = stack.pop()

            for edge in nfa.states[current].edges:
                if edge.symbol is None and edge.to_state not in closure:
                    closure.add(edge.to_state)
                    stack.append(edge.to_state)

        return frozenset(closure)

    # проверка на принимающее состояние
    def is_accepting_subset(self, nfa, subset: frozenset[int]) -> bool:
        NFA.validate_nfa(nfa)
        if subset is None:
            raise ValueError("Отсутствует множество вершин с проверкой на принимаеющие")

        for state_id in subset:
            if nfa.states[state_id].is_accepting:
                return True
        return False

    # создаем вершину нового графа
    def new_state(self, is_accepting: bool) -> int:
        state_id = self.next_id
        self.next_id += 1

        self.states[state_id] = DFAState(
            id=state_id,
            is_accepting=is_accepting
        )

        return state_id

    def add_edge(self, from_state: int, to_state: int, symbol: str):
        self.states[from_state].edges.append(DFAEdge(to_state, symbol))

    # получить множество достижимых состояний с символом
    def move(self, nfa, state_ids: set[int], symbol: str) -> set[int]:
        NFA.validate_nfa(nfa)
        if state_ids is None or symbol is None:
            raise ValueError("Отсутствуют данные для получения множества достижимых состояний")

        result = set()

        for state_id in state_ids:
            for edge in nfa.states[state_id].edges:
                if edge.symbol == symbol:
                    result.add(edge.to_state)

        return result

    def build_dfa(self, nfa):
        NFA.validate_nfa(nfa)

        #получаем алфавит текущего регулярного выражения
        self.alphabet = self.get_alphabet(nfa)

        # таблица: subset NFA -> id состояния DFA
        subset_to_dfa_id: dict[frozenset[int], int] = {}

        #готовим start
        start_subset = self.epsilon_closure(nfa, {nfa.start})
        start_is_accepting = self.is_accepting_subset(nfa, start_subset)

        start_dfa_id = self.new_state(start_is_accepting)
        self.start = start_dfa_id

        unprocessed: list[frozenset[int]] = [start_subset]

        subset_to_dfa_id[start_subset] = start_dfa_id

        # обходим граф
        while unprocessed:
            # достаем множество вершин NFA
            current_subset = unprocessed.pop(0)
            # получаем индекст вершины DFA
            current_dfa_id = subset_to_dfa_id[current_subset]

            for symbol in sorted(self.alphabet):
                moved = self.move(nfa, set(current_subset), symbol)

                if not moved:
                    continue

                next_subset = self.epsilon_closure(nfa, moved)

                if next_subset not in subset_to_dfa_id:
                    next_is_accepting = self.is_accepting_subset(nfa, next_subset)

                    next_dfa_id = self.new_state(next_is_accepting)
                    subset_to_dfa_id[next_subset] = next_dfa_id

                    unprocessed.append(next_subset)

                next_dfa_id = subset_to_dfa_id[next_subset]
                self.add_edge(current_dfa_id, next_dfa_id, symbol)

        return self

    # обход посимвольный(найти если есть)
    def transition(self, state_id: int, symbol: str) -> int | None:
        if state_id < 0:
            raise ValueError("неверный id вершины")
        if symbol is None:
            raise ValueError("не передан символ")
        if symbol == "":
            raise ValueError("пустой символ перехода")

        for edge in self.states[state_id].edges:
            if edge.symbol == symbol:
                return edge.to_state
        return None

    # сама логика поиска, сначала ищем потенциальный старт, потом проходимся внутри него
    def search(self, data: str):
        DFA.validate_dfa(self)
        if data is None:
            raise ValueError("переданная строка None")

        for start_pos in range(len(data) + 1):
            current_state = self.start
            last_accept_pos = None

            if self.states[current_state].is_accepting:
                last_accept_pos = start_pos

            pos = start_pos
            while pos < len(data):
                next_state = self.transition(current_state, data[pos])
                if next_state is None:
                    break

                current_state = next_state
                pos += 1

                if self.states[current_state].is_accepting:
                    last_accept_pos = pos

            if last_accept_pos is not None:
                return (start_pos, last_accept_pos, data[start_pos:last_accept_pos])

        return None

    def accepts(self, data: str) -> bool:
        DFA.validate_dfa(self)
        if data is None:
            raise ValueError("переданная строка None")

        current_state = self.start

        for symbol in data:
            next_state = self.transition(current_state, symbol)

            if next_state is None:
                return False

            current_state = next_state

        return self.states[current_state].is_accepting

    #операции над языками

    # дополнение автомата до полного
    def make_complete(self, alphabet: set[str] | None = None):
        DFA.validate_dfa(self)

        # дополняем до разных алфавитов
        if alphabet is None:
            alphabet = set(self.alphabet)
        else:
            alphabet = set(alphabet)

        self.alphabet = set(alphabet)

        sink_id = None

        #проходимся по всем элементам графа
        for state_id in list(self.states.keys()):
            #получаем литералы по которым есть переходы
            existing_symbols = {edge.symbol for edge in self.states[state_id].edges}

            for symbol in sorted(alphabet):
                if symbol not in existing_symbols:
                    # создаем одн раз вершину
                    if sink_id is None:
                        sink_id = self.new_state(False)

                    self.add_edge(state_id, sink_id, symbol)

        # замыкаем на самой  себе по всем символам
        if sink_id is not None:
            for symbol in sorted(alphabet):
                self.add_edge(sink_id, sink_id, symbol)

    # клонируем
    def clone(self):
        DFA.validate_dfa(self)

        new_dfa = DFA()
        new_dfa.start = self.start
        new_dfa.next_id = self.next_id
        new_dfa.alphabet = set(self.alphabet)

        for state_id, state in self.states.items():
            new_state = DFAState(
                id=state.id,
                is_accepting=state.is_accepting,
                edges=[DFAEdge(edge.to_state, edge.symbol) for edge in state.edges]
            )
            new_dfa.states[state_id] = new_state

        return new_dfa

    # дополнение(инверсия принимающих состояний)
    def negate(self, alphabet: set[str] | None = None):
        DFA.validate_dfa(self)

        result = self.clone()
        result.make_complete(alphabet)

        for state in result.states.values():
            state.is_accepting = not state.is_accepting

        return result

    # объединение языков
    def union(self, other):
        DFA.validate_dfa(self)
        DFA.validate_dfa(other)

        # создаем новые автоматы
        dfa1 = self.clone()
        dfa2 = other.clone()

        # получаем общий алфавит
        alphabet = set(dfa1.alphabet) | set(dfa2.alphabet)

        # дополняем оба
        dfa1.make_complete(alphabet)
        dfa2.make_complete(alphabet)

        # автомат результата
        result = DFA()
        result.alphabet = set(alphabet)

        pair_to_id = {}

        #готовим стартовую пару
        start_pair = (dfa1.start, dfa2.start)
        start_accepting = (
                dfa1.states[dfa1.start].is_accepting
                or
                dfa2.states[dfa2.start].is_accepting
        )

        start_id = result.new_state(start_accepting)
        result.start = start_id
        pair_to_id[start_pair] = start_id

        unprocessed = [start_pair]

        while unprocessed:
            # получаем пару
            current_pair = unprocessed.pop(0)
            q1, q2 = current_pair
            current_result_id = pair_to_id[current_pair]

            # получаем пару вершин в которые можно перейти по текущему символу
            for symbol in sorted(alphabet):
                next_q1 = dfa1.transition(q1, symbol)
                next_q2 = dfa2.transition(q2, symbol)

                next_pair = (next_q1, next_q2)

                # создаем пару если ее не было
                if next_pair not in pair_to_id:
                    next_accepting = (
                            dfa1.states[next_q1].is_accepting
                            or # and
                            dfa2.states[next_q2].is_accepting
                    )

                    new_id = result.new_state(next_accepting)
                    pair_to_id[next_pair] = new_id
                    unprocessed.append(next_pair)

                # создаем ребро
                result.add_edge(
                    current_result_id,
                    pair_to_id[next_pair],
                    symbol
                )

        return result

    # union только принимающее через and
    def intersection(self, other):
        DFA.validate_dfa(self)
        DFA.validate_dfa(other)

        dfa1 = self.clone()
        dfa2 = other.clone()

        alphabet = set(dfa1.alphabet) | set(dfa2.alphabet)

        dfa1.make_complete(alphabet)
        dfa2.make_complete(alphabet)

        result = DFA()
        result.alphabet = set(alphabet)

        pair_to_id = {}

        start_pair = (dfa1.start, dfa2.start)

        start_accepting = (
                dfa1.states[dfa1.start].is_accepting
                and
                dfa2.states[dfa2.start].is_accepting
        )

        start_id = result.new_state(start_accepting)
        result.start = start_id
        pair_to_id[start_pair] = start_id

        unprocessed = [start_pair]

        while unprocessed:
            current_pair = unprocessed.pop(0)
            q1, q2 = current_pair
            current_result_id = pair_to_id[current_pair]

            for symbol in sorted(alphabet):
                next_q1 = dfa1.transition(q1, symbol)
                next_q2 = dfa2.transition(q2, symbol)

                next_pair = (next_q1, next_q2)

                if next_pair not in pair_to_id:
                    next_accepting = (
                            dfa1.states[next_q1].is_accepting
                            and
                            dfa2.states[next_q2].is_accepting
                    )

                    new_id = result.new_state(next_accepting)
                    pair_to_id[next_pair] = new_id
                    unprocessed.append(next_pair)

                result.add_edge(
                    current_result_id,
                    pair_to_id[next_pair],
                    symbol,
                )

        return result

    def diff(self, other):
        DFA.validate_dfa(self)
        DFA.validate_dfa(other)

        alphabet = set(self.alphabet) | set(other.alphabet)
        return self.intersection(other.negate(alphabet))

    # изоморфность - равенство графов
    def is_isomorphic(self, other) -> bool:
        DFA.validate_dfa(self)
        DFA.validate_dfa(other)

        # сравнение алфавитов(мб нет)
        if set(self.alphabet) != set(other.alphabet):
            return False

        # словарь переходов от вершины
        def transition_map(dfa, state_id: int) -> dict[str, int] | None:
            result: dict[str, int] = {}

            for edge in dfa.states[state_id].edges:
                if edge.symbol in result:
                    # 2 перехода по 1 символу
                    return None

                result[edge.symbol] = edge.to_state

            return result

        mapping_self_to_other: dict[int, int] = {}
        mapping_other_to_self: dict[int, int] = {}

        queue: list[tuple[int, int]] = [
            (self.start, other.start)
        ]

        mapping_self_to_other[self.start] = other.start
        mapping_other_to_self[other.start] = self.start

        while queue:
            state_a_id, state_b_id = queue.pop(0)

            state_a = self.states[state_a_id]
            state_b = other.states[state_b_id]

            # принимаемость
            if state_a.is_accepting != state_b.is_accepting:
                return False

            # переходы
            transitions_a = transition_map(self, state_a_id)
            transitions_b = transition_map(other, state_b_id)

            if transitions_a is None or transitions_b is None:
                return False

            # одинаковые переходы по символам
            if set(transitions_a.keys()) != set(transitions_b.keys()):
                return False

            for symbol in sorted(transitions_a.keys()):
                next_a = transitions_a[symbol]
                next_b = transitions_b[symbol]

                # если next_a уже сопоставлен, он должен вести именно в next_b
                if next_a in mapping_self_to_other:
                    if mapping_self_to_other[next_a] != next_b:
                        return False
                    continue
                else:
                    mapping_self_to_other[next_a] = next_b

                # обратная проверка: next_b не может соответствовать двум разным next_a
                if next_b in mapping_other_to_self:
                    if mapping_other_to_self[next_b] != next_a:
                        return False
                    continue
                else:
                    mapping_other_to_self[next_b] = next_a

                # добавляем новую пару
                queue.append((next_a, next_b))
        return True

    # эквивалентность языков
    def is_equivalent(self, other) -> bool:
        DFA.validate_dfa(self)
        DFA.validate_dfa(other)

        dfa1 = self.clone()
        dfa2 = other.clone()

        alphabet = set(dfa1.alphabet) | set(dfa2.alphabet)

        dfa1.make_complete(alphabet)
        dfa2.make_complete(alphabet)

        visited = set()
        queue = [(dfa1.start, dfa2.start)]

        while queue:
            q1, q2 = queue.pop(0)

            if (q1, q2) in visited:
                continue

            visited.add((q1, q2))

            accepting_1 = dfa1.states[q1].is_accepting
            accepting_2 = dfa2.states[q2].is_accepting

            if accepting_1 != accepting_2:
                return False

            for symbol in sorted(alphabet):
                next_q1 = dfa1.transition(q1, symbol)
                next_q2 = dfa2.transition(q2, symbol)

                queue.append((next_q1, next_q2))

        return True

    #минимальный автомат

    #получить одно из множеств
    def get_states_by_accepting(self, is_accepting: bool) -> set[int]:
        DFA.validate_dfa(self)

        result: set[int] = set()

        for state_id, state in self.states.items():
            if state.is_accepting == is_accepting:
                result.add(state_id)

        return result

    #инициализация множеств
    def get_initial_partitions(self) -> list[set[int]]:
        DFA.validate_dfa(self)

        partitions: list[set[int]] = []

        non_accepting = self.get_states_by_accepting(False)
        accepting = self.get_states_by_accepting(True)

        if non_accepting:
            partitions.append(non_accepting)

        if accepting:
            partitions.append(accepting)

        return partitions

    # возвращаем индекс множества, в котором содержиться вершина
    def get_partition_index(self, state_id: int, partitions: list[set[int]]) -> int:
        DFA.validate_dfa(self)
        if state_id < 0:
            raise ValueError("Индекс вершины меньше 0")
        if partitions is None:
            raise ValueError("Множество None")

        for index, group in enumerate(partitions):
            if state_id in group:
                return index

        raise ValueError(f"{state_id} не найдено")

    # получаем разные множества
    def refine_partitions(self, partitions: list[set[int]]) -> list[set[int]]:
        DFA.validate_dfa(self)
        if partitions is None:
            raise ValueError("Отсутствуют текущие переданные вершины")

        new_partitions: list[set[int]] = []

        #множества
        for group in partitions:
            buckets = {}

            # вершины множества
            for state_id in sorted(group):
                signature: list[int | None] = []

                # алфавит по вершине
                for symbol in sorted(self.alphabet):
                    #получаем ребро куда попали
                    next_state = self.transition(state_id, symbol)

                    if next_state is None:
                        signature.append(None)
                    else:
                        #индекс множества в котором находиться данная вершина
                        partition_index = self.get_partition_index(
                            next_state,
                            partitions,
                        )
                        signature.append(partition_index)

                # (сигнатуры, куда можно попасть из данной вершины), множества
                signature_key = tuple(signature)

                # создаем множество для данного ключа, если его еще не было
                if signature_key not in buckets:
                    buckets[signature_key] = set()

                # добавляем вершину по этому ключу
                buckets[signature_key].add(state_id)

            # добавляем только значения(множество вершин)
            new_partitions.extend(buckets.values())

        return sorted(new_partitions, key=lambda part: min(part))

    # получаем номер множества и символ по которому можно перейти из текущего
    def get_partition_transitions(self, group: set[int], partitions: list[set[int]]) -> dict[str, int]:

        if not group:
            raise ValueError("Пустое множество состояний")

        representative = min(group)

        transit: dict[str, int] = {}

        for symbol in sorted(self.alphabet):
            next_state = self.transition(representative, symbol)

            if next_state is None:
                continue

            target_partition_index = self.get_partition_index(
                next_state,
                partitions,
            )

            transit[symbol] = target_partition_index

        return transit

    #общий метод минимизации
    def build_min_dfa(self):
        DFA.validate_dfa(self)

        # начальное разбиение
        partitions = self.get_initial_partitions()

        # разбиваем пока не будут меняться множества
        while True:
            new_partitions = self.refine_partitions(partitions)

            if {frozenset(group) for group in partitions} == {frozenset(group) for group in new_partitions}:
                break

            partitions = new_partitions

        # cоздаём новый минимальный DFA
        min_dfa = DFA()
        min_dfa.alphabet = set(self.alphabet)

        # устанавливаем принимающие состояния
        for group in partitions:
            is_accepting = any(self.states[state_id].is_accepting for state_id in group)

            min_dfa.new_state(is_accepting)

        # установка стартовой вершины
        min_dfa.start = self.get_partition_index(
            self.start,
            partitions,
        )

        # восстанавливаем рёбра между новыми вершинами
        for group_index, group in enumerate(partitions):
            transitions = self.get_partition_transitions(
                group,
                partitions,
            )

            for symbol, target_group_index in transitions.items():
                min_dfa.add_edge(
                    from_state=group_index,
                    to_state=target_group_index,
                    symbol=symbol,
                )

        return min_dfa