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