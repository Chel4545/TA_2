from dataclasses import dataclass, field


@dataclass
class GNFAEdge:
    to_state: int
    regex: str


@dataclass
class GNFAState:
    id: int
    edges: list[GNFAEdge] = field(default_factory=list)


class GNFA:
    def __init__(self):
        self.states: dict[int, GNFAState] = {}
        self.start: int | None = None
        self.accept: int | None = None
        self.next_id = 0

    def new_state(self) -> int:
        state_id = self.next_id
        self.next_id += 1
        self.states[state_id] = GNFAState(id=state_id)
        return state_id

    def add_edge(self, from_state: int, to_state: int, regex: str):
        self.states[from_state].edges.append(GNFAEdge(to_state, regex))

    def build_regex(self, dfa):
        self.states = {}
        self.start = None
        self.accept = None
        self.next_id = 0

        dfa_to_gnfa: dict[int, int] = {}

        for dfa_state_id in sorted(dfa.states.keys()):
            gnfa_state_id = self.new_state()
            dfa_to_gnfa[dfa_state_id] = gnfa_state_id

        for dfa_state_id, dfa_state in dfa.states.items():
            from_gnfa = dfa_to_gnfa[dfa_state_id]

            for edge in dfa_state.edges:
                to_gnfa = dfa_to_gnfa[edge.to_state]
                self.add_edge(from_gnfa, to_gnfa, edge.symbol)

        new_start = self.new_state()
        new_accept = self.new_state()

        self.add_edge(new_start, dfa_to_gnfa[dfa.start], "^")

        for dfa_state_id, dfa_state in dfa.states.items():
            if dfa_state.is_accepting:
                self.add_edge(dfa_to_gnfa[dfa_state_id], new_accept, "^")

        self.start = new_start
        self.accept = new_accept

        return self.restore_regex()

    # крафтим строки
    def regex_union(self, r1: str | None, r2: str | None) -> str | None:
        if r1 is None:
            return r2
        if r2 is None:
            return r1
        if r1 == r2:
            return r1
        return f"({r1}|{r2})"

    def regex_concat(self, r1: str | None, r2: str | None) -> str | None:
        if r1 is None or r2 is None:
            return None
        if r1 == "^":
            return r2
        if r2 == "^":
            return r1
        return f"{self.wrap_concat_part(r1)}{self.wrap_concat_part(r2)}"

    def regex_star(self, r: str | None) -> str | None:
        if r is None:
            return "^"
        if r == "^":
            return "^"
        if len(r) == 1:
            return f"{r}*"
        if r.endswith("*"):
            return r
        return f"({r})*"

    def wrap_concat_part(self, r: str) -> str:
        if len(r) == 1:
            return r
        if r == "^":
            return r
        if r.endswith("*"):
            return r
        if r.startswith("(") and r.endswith(")"):
            return r
        if "|" in r:
            return f"({r})"
        return r

    def build_label_table(self) -> dict[tuple[int, int], str | None]:
        labels: dict[tuple[int, int], str | None] = {}
        state_ids = list(self.states.keys())

        for i in state_ids:
            for j in state_ids:
                labels[(i, j)] = None

        for from_state_id, state in self.states.items():
            for edge in state.edges:
                current = labels[(from_state_id, edge.to_state)]
                labels[(from_state_id, edge.to_state)] = self.regex_union(current, edge.regex)

        return labels


    def eliminate_state(self, labels: dict[tuple[int, int], str | None], k: int, states_left: list[int]):
        for i in states_left:
            if i == k:
                continue
            for j in states_left:
                if j == k:
                    continue

                rik = labels[(i, k)]
                rkk = labels[(k, k)]
                rkj = labels[(k, j)]
                rij = labels[(i, j)]

                through_k = self.regex_concat(
                    self.regex_concat(rik, self.regex_star(rkk)),
                    rkj
                )

                labels[(i, j)] = self.regex_union(rij, through_k)

        for s in states_left:
            labels[(s, k)] = None
            labels[(k, s)] = None


    def restore_regex(self) -> str:
        if self.start is None or self.accept is None:
            raise ValueError("GNFA еще не построен")

        labels = self.build_label_table()
        states_left = list(self.states.keys())

        removable = [s for s in states_left if s not in {self.start, self.accept}]

        for k in removable:
            self.eliminate_state(labels, k, states_left)
            states_left.remove(k)

        result = labels[(self.start, self.accept)]
        return result if result is not None else "∅"