from dataclasses import dataclass, field

@dataclass
class MinDFAEdge:
    to_state: int
    symbol: str


@dataclass
class MinDFAState:
    id: int
    original_states: frozenset[int]
    is_accepting: bool = False
    edges: list[MinDFAEdge] = field(default_factory=list)

class MinDFA:
    def __init__(self):
        self.states: dict[int, MinDFAState] = {}
        self.start: int | None = None
        self.alphabet: set[str] = set()
        self.next_id = 0

    def new_state(self, original_states: frozenset[int], is_accepting: bool) -> int:
        state_id = self.next_id
        self.next_id += 1
        self.states[state_id] = MinDFAState(
            id=state_id,
            original_states=original_states,
            is_accepting=is_accepting
        )
        return state_id

    def add_edge(self, from_state: int, to_state: int, symbol: str):
        self.states[from_state].edges.append(MinDFAEdge(to_state, symbol))

    # возврат состояния,из которого можно перейти по символу
    def get_transition(self, dfa, state_id: int, symbol: str) -> int | None:
        for edge in dfa.states[state_id].edges:
            if edge.symbol == symbol:
                return edge.to_state
        return None

    # возвращаем достижимые состояния из старта
    def reachable_states(self, dfa) -> set[int]:
        if dfa.start is None:
            return set()

        visited = set()
        stack = [dfa.start]

        while stack:
            current = stack.pop()
            if current in visited:
                continue

            visited.add(current)

            for edge in dfa.states[current].edges:
                if edge.to_state not in visited:
                    stack.append(edge.to_state)

        return visited

    # строим сигнатуры (тип состояния, и по алфавиту куда можно перейти)
    def build_signature(self, dfa, state_id: int, partition: list[set[int]]) -> tuple:
        state = dfa.states[state_id]

        # Для каждого символа смотрим, в какой класс попадает переход
        signature = [state.is_accepting]

        for symbol in sorted(dfa.alphabet):
            target = self.get_transition(dfa, state_id, symbol)

            if target is None:
                signature.append(None)
            else:
                block_index = None
                for i, block in enumerate(partition):
                    if target in block:
                        block_index = i
                        break
                signature.append(block_index)

        return tuple(signature)

    #создание новой группы по сигнатуре
    def refine_partition(self, dfa, partition: list[set[int]]) -> list[set[int]]:
        new_partition = []

        for block in partition:
            groups_by_signature: dict[tuple, set[int]] = {}

            for state_id in block:
                signature = self.build_signature(dfa, state_id, partition)

                if signature not in groups_by_signature:
                    groups_by_signature[signature] = set()

                groups_by_signature[signature].add(state_id)

            for group in groups_by_signature.values():
                new_partition.append(group)

        return new_partition

    #основной алгоритм
    def build_min_dfa(self, dfa):
        self.alphabet = set(dfa.alphabet)

        reachable = self.reachable_states(dfa)

        accepting = {s for s in reachable if dfa.states[s].is_accepting}
        non_accepting = {s for s in reachable if not dfa.states[s].is_accepting}

        partition = []
        if non_accepting:
            partition.append(non_accepting)
        if accepting:
            partition.append(accepting)

        while True:
            new_partition = self.refine_partition(dfa, partition)

            old_norm = {frozenset(block) for block in partition}
            new_norm = {frozenset(block) for block in new_partition}

            if old_norm == new_norm:
                break

            partition = new_partition


        block_to_min_id: dict[frozenset[int], int] = {}
        state_to_block_index: dict[int, int] = {}

        for i, block in enumerate(partition):
            for state_id in block:
                state_to_block_index[state_id] = i

        for block in partition:
            representative = next(iter(block))
            is_accepting = dfa.states[representative].is_accepting
            min_id = self.new_state(frozenset(block), is_accepting)
            block_to_min_id[frozenset(block)] = min_id

        # стартовое состояние
        for block in partition:
            if dfa.start in block:
                self.start = block_to_min_id[frozenset(block)]
                break

        # переходы
        for block in partition:
            representative = next(iter(block))
            from_min_id = block_to_min_id[frozenset(block)]

            for symbol in sorted(self.alphabet):
                target = self.get_transition(dfa, representative, symbol)
                if target is None:
                    continue

                target_block = partition[state_to_block_index[target]]
                to_min_id = block_to_min_id[frozenset(target_block)]

                # чтобы не дублировать одно и то же ребро
                already_exists = any(
                    edge.symbol == symbol and edge.to_state == to_min_id
                    for edge in self.states[from_min_id].edges
                )

                if not already_exists:
                    self.add_edge(from_min_id, to_min_id, symbol)


    def transition(self, state_id: int, symbol: str) -> int | None:
        for edge in self.states[state_id].edges:
            if edge.symbol == symbol:
                return edge.to_state
        return None

    def search(self, data: str):
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