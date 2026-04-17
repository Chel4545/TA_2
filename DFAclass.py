from dataclasses import dataclass, field


@dataclass
class DFAEdge:
    to_state: int
    symbol: str


@dataclass
class DFAState:
    id: int
    nfa_states: frozenset[int]
    is_accepting: bool = False
    edges: list[DFAEdge] = field(default_factory=list)

class DFA:
    def __init__(self):
        self.states: dict[int, DFAState] = {}
        self.start: int | None = None
        self.next_id = 0
        self.alphabet: set[str] = set()

        self.subset_to_dfa_id: dict[frozenset[int], int] = {}

    # собираем алфавит
    def get_alphabet(self, nfa) -> set[str]:
        alphabet = set()

        for state in nfa.states.values():
            for edge in state.edges:
                if edge.symbol is not None:
                    alphabet.add(edge.symbol)

        return alphabet

    # проходимся из текущего множества по E
    def epsilon_closure(self, nfa, state_ids: set[int]) -> frozenset[int]:
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
        for state_id in subset:
            if nfa.states[state_id].is_accepting:
                return True
        return False

    # создаем вершину нового графа
    def new_state(self, nfa_states: frozenset[int], is_accepting: bool) -> int:
        state_id = self.next_id
        self.next_id += 1

        self.states[state_id] = DFAState(
            id=state_id,
            nfa_states=nfa_states,
            is_accepting=is_accepting
        )

        self.subset_to_dfa_id[nfa_states] = state_id
        return state_id

    def add_edge(self, from_state: int, to_state: int, symbol: str):
        self.states[from_state].edges.append(DFAEdge(to_state, symbol))

    # получить множество достижимых состояний с символом
    def move(self, nfa, state_ids: set[int], symbol: str) -> set[int]:
        result = set()

        for state_id in state_ids:
            for edge in nfa.states[state_id].edges:
                if edge.symbol == symbol:
                    result.add(edge.to_state)

        return result

    def build_dfa(self, nfa):
        self.alphabet = self.get_alphabet(nfa)

        start_subset = self.epsilon_closure(nfa, {nfa.start})
        start_is_accepting = self.is_accepting_subset(nfa, start_subset)

        start_dfa_id = self.new_state(start_subset, start_is_accepting)
        self.start = start_dfa_id

        unprocessed: list[frozenset[int]] = [start_subset]

        while unprocessed:
            current_subset = unprocessed.pop(0)
            current_dfa_id = self.subset_to_dfa_id[current_subset]

            for symbol in sorted(self.alphabet):
                moved = self.move(nfa, set(current_subset), symbol)

                if not moved:
                    continue

                next_subset = self.epsilon_closure(nfa, moved)

                if next_subset not in self.subset_to_dfa_id:
                    next_is_accepting = self.is_accepting_subset(nfa, next_subset)
                    self.new_state(next_subset, next_is_accepting)
                    unprocessed.append(next_subset)

                next_dfa_id = self.subset_to_dfa_id[next_subset]
                self.add_edge(current_dfa_id, next_dfa_id, symbol)

        return self

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

    # дополнение автомата до полного
    def make_complete(self, alphabet: set[str] | None = None):
        if alphabet is None:
            alphabet = set(self.alphabet)
        else:
            alphabet = set(alphabet)

        self.alphabet = set(alphabet)

        sink_id = None

        for state_id in list(self.states.keys()):
            existing_symbols = {edge.symbol for edge in self.states[state_id].edges}

            for symbol in alphabet:
                if symbol not in existing_symbols:
                    if sink_id is None:
                        sink_id = self.next_id
                        self.next_id += 1
                        self.states[sink_id] = DFAState(
                            id=sink_id,
                            nfa_states=frozenset(),
                            is_accepting=False
                        )

                    self.add_edge(state_id, sink_id, symbol)

        if sink_id is not None:
            for symbol in alphabet:
                self.add_edge(sink_id, sink_id, symbol)

    # клонируем
    def clone(self):
        new_dfa = DFA()
        new_dfa.start = self.start
        new_dfa.next_id = self.next_id
        new_dfa.alphabet = set(self.alphabet)
        new_dfa.subset_to_dfa_id = dict(self.subset_to_dfa_id)

        for state_id, state in self.states.items():
            new_state = DFAState(
                id=state.id,
                nfa_states=state.nfa_states,
                is_accepting=state.is_accepting,
                edges=[DFAEdge(edge.to_state, edge.symbol) for edge in state.edges]
            )
            new_dfa.states[state_id] = new_state

        return new_dfa

    # дополнение
    def complement(self, alphabet: set[str] | None = None):
        print(alphabet)
        result = self.clone()
        result.make_complete(alphabet)

        for state in result.states.values():
            state.is_accepting = not state.is_accepting

        return result

    # объединение языков
    def union(self, other):
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
                or
                dfa2.states[dfa2.start].is_accepting
        )

        start_id = result.next_id
        result.next_id += 1
        result.states[start_id] = DFAState(
            id=start_id,
            nfa_states=frozenset(),
            is_accepting=start_accepting
        )
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
                            or
                            dfa2.states[next_q2].is_accepting
                    )

                    new_id = result.next_id
                    result.next_id += 1
                    result.states[new_id] = DFAState(
                        id=new_id,
                        nfa_states=frozenset(),
                        is_accepting=next_accepting
                    )

                    pair_to_id[next_pair] = new_id
                    unprocessed.append(next_pair)

                result.add_edge(
                    current_result_id,
                    pair_to_id[next_pair],
                    symbol
                )

        return result

    def subtraction(self, other):
        alphabet = set(self.alphabet) | set(other.alphabet)
        print(alphabet)
        return self.complement(alphabet).union(other).complement(alphabet)

