from pythonProject1.logic.DFAclass import DFA


class GNFA:
    def __init__(self):
        self.matrix = []
        self.size = 0
        self.start_index = None
        self.end_index = None

        self.INF = "inf"
        self.EPS = "^"

    def is_inf(self, value):
        return value == self.INF

    def is_eps(self, value):
        return value == self.EPS

    def wrap(self, value):
        if value == self.INF or value == self.EPS:
            return value

        if len(value) == 1:
            return value

        return f"({value})"

    def regex_or(self, a, b):
        if self.is_inf(a):
            return b

        if self.is_inf(b):
            return a

        if a == b:
            return a

        return f"{self.wrap(a)}|{self.wrap(b)}"

    def regex_concat(self, *parts):
        result = ""

        for part in parts:
            if self.is_inf(part):
                return self.INF

            if self.is_eps(part):
                continue

            result += self.wrap(part)

        if result == "":
            return self.EPS

        return result

    def regex_star(self, value):
        if self.is_inf(value):
            return self.EPS

        if self.is_eps(value):
            return self.EPS

        positive = f"{self.wrap(value)}+"

        return self.regex_or(self.EPS, positive)

    def build_matrix(self, dfa):
        DFA.validate_dfa(dfa)

        n = len(dfa.states)

        # start и end
        self.start_index = n
        self.end_index = n + 1

        self.size = n + 2

        # создаём матрицу
        matrix = [[self.INF for _ in range(self.size)] for _ in range(self.size)]

        # переносим переходы DFA
        for from_state_id, state in dfa.states.items():
            for edge in state.edges:
                old_value = matrix[from_state_id][edge.to_state]
                new_value = edge.symbol

                matrix[from_state_id][edge.to_state] = self.regex_or(old_value, new_value)

        # добавляем старт по ε
        matrix[self.start_index][dfa.start] = self.EPS

        # добавляем принимающие по ε
        for state_id, state in dfa.states.items():
            if state.is_accepting:
                matrix[state_id][self.end_index] = self.EPS

        return matrix

    def build_regex(self, dfa):
        DFA.validate_dfa(dfa)

        self.matrix = self.build_matrix(dfa)
        active = set(range(self.size))

        for k in range(len(dfa.states)):
            for i in list(active):
                if i == k:
                    continue

                for j in list(active):
                    if j == k:
                        continue

                    Rij = self.matrix[i][j]
                    Rik = self.matrix[i][k]
                    Rkk = self.matrix[k][k]
                    Rkj = self.matrix[k][j]

                    through_k = self.regex_concat(
                        Rik,
                        self.regex_star(Rkk),
                        Rkj,
                    )

                    self.matrix[i][j] = self.regex_or(
                        Rij,
                        through_k,
                    )

            active.remove(k)

            for x in range(self.size):
                self.matrix[k][x] = self.INF
                self.matrix[x][k] = self.INF

        result = self.matrix[self.start_index][self.end_index]

        if self.is_inf(result):
            return None

        return result
