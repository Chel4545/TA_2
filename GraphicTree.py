from graphviz import Digraph
from ASTclass import Literal, Epsilon, Concat, Union, Plus, Repeat, Group, BackRef

class ASTGraphviz:
    def __init__(self):
        self.dot = Digraph()
        self.counter = 0

    def next_id(self):
        self.counter += 1
        return f"n{self.counter}"

    def build(self, node):
        node_id = self.next_id()

        if isinstance(node, Literal):
            label = f"'{node.char}'"
        elif isinstance(node, Epsilon):
            label = "^"
        elif isinstance(node, BackRef):
            label = f"BackRef({node.num})"
        elif isinstance(node, Plus):
            label = "+"
        elif isinstance(node, Repeat):
            label = f"Repeat({node.min},{node.max})"
        elif isinstance(node, Group):
            label = f"Group({node.num})"
        elif isinstance(node, Concat):
            label = "."
        elif isinstance(node, Union):
            label = "|"
        else:
            label = str(node)

        self.dot.node(node_id, label)

        if isinstance(node, Plus):
            child = self.build(node.expr)
            self.dot.edge(node_id, child, label="expr")

        elif isinstance(node, Repeat):
            child = self.build(node.expr)
            self.dot.edge(node_id, child, label="expr")

        elif isinstance(node, Group):
            child = self.build(node.expr)
            self.dot.edge(node_id, child, label="expr")

        elif isinstance(node, Concat):
            left = self.build(node.left)
            right = self.build(node.right)
            self.dot.edge(node_id, left, label="left")
            self.dot.edge(node_id, right, label="right")

        elif isinstance(node, Union):
            left = self.build(node.left)
            right = self.build(node.right)
            self.dot.edge(node_id, left, label="left")
            self.dot.edge(node_id, right, label="right")

        return node_id

class NFAGraphviz:
    def __init__(self):
        self.dot = Digraph()
        self.dot.attr(rankdir='LR')  # слева направо

    def build(self, nfa):
        # специальная невидимая стартовая точка
        self.dot.node("start", label="", shape="point")

        # сначала рисуем все состояния
        for state_id in sorted(nfa.states):
            state = nfa.states[state_id]

            shape = "doublecircle" if state.is_accepting else "circle"
            self.dot.node(str(state.id), label=str(state.id), shape=shape)

        # стрелка из start в начальное состояние автомата
        if nfa.start is not None:
            self.dot.edge("start", str(nfa.start))

        # теперь рисуем все переходы
        for state_id in sorted(nfa.states):
            state = nfa.states[state_id]

            for edge in state.edges:
                label = "ε" if edge.symbol is None else str(edge.symbol)
                self.dot.edge(str(state.id), str(edge.to_state), label=label)

        return self.dot

class DFAGraphviz:
    def __init__(self, show_nfa_subsets: bool = True):
        self.dot = Digraph()
        self.dot.attr(rankdir='LR')
        self.show_nfa_subsets = show_nfa_subsets

    def build_state_label(self, state) -> str:
        if not self.show_nfa_subsets:
            return str(state.id)

        subset = "{" + ",".join(str(x) for x in sorted(state.nfa_states)) + "}"
        return f"{state.id}\\n{subset}"

    def build(self, dfa):
        self.dot.node("start", label="", shape="point")

        for state_id in sorted(dfa.states):
            state = dfa.states[state_id]
            shape = "doublecircle" if state.is_accepting else "circle"
            label = self.build_state_label(state)
            self.dot.node(str(state.id), label=label, shape=shape)

        if dfa.start is not None:
            self.dot.edge("start", str(dfa.start))

        for state_id in sorted(dfa.states):
            state = dfa.states[state_id]
            for edge in state.edges:
                self.dot.edge(str(state.id), str(edge.to_state), label=str(edge.symbol))

        return self.dot

class MinDFAGraphviz:
    def __init__(self, show_original_states: bool = True):
        self.dot = Digraph()
        self.dot.attr(rankdir='LR')
        self.show_original_states = show_original_states

    def build_state_label(self, state) -> str:
        if not self.show_original_states:
            return str(state.id)

        subset = "{" + ",".join(str(x) for x in sorted(state.original_states)) + "}"
        return f"{state.id}\\n{subset}"

    def build(self, min_dfa):
        self.dot.node("start", label="", shape="point")

        for state_id in sorted(min_dfa.states):
            state = min_dfa.states[state_id]
            shape = "doublecircle" if state.is_accepting else "circle"
            label = self.build_state_label(state)
            self.dot.node(str(state.id), label=label, shape=shape)

        if min_dfa.start is not None:
            self.dot.edge("start", str(min_dfa.start))

        for state_id in sorted(min_dfa.states):
            state = min_dfa.states[state_id]
            for edge in state.edges:
                self.dot.edge(str(state.id), str(edge.to_state), label=str(edge.symbol))

        return self.dot

class OperationDFAGraphviz:
    def __init__(self):
        self.dot = Digraph()
        self.dot.attr(rankdir='LR')

    def build_state_label(self, state) -> str:
        # если есть pair от операций над двумя DFA
        if hasattr(state, "source_pair") and state.source_pair is not None:
            return f"{state.id}\\n{state.source_pair}"

        # если это обычный DFA из NFA
        if hasattr(state, "nfa_states") and state.nfa_states:
            subset = "{" + ",".join(str(x) for x in sorted(state.nfa_states)) + "}"
            return f"{state.id}\\n{subset}"

        return str(state.id)

    def build(self, dfa, title: str = "DFA Operation Result"):
        self.dot.attr(label=title, labelloc="t", fontsize="20")
        self.dot.node("start", label="", shape="point")

        for state_id in sorted(dfa.states):
            state = dfa.states[state_id]
            shape = "doublecircle" if state.is_accepting else "circle"
            label = self.build_state_label(state)
            self.dot.node(str(state.id), label=label, shape=shape)

        if dfa.start is not None:
            self.dot.edge("start", str(dfa.start))

        for state_id in sorted(dfa.states):
            state = dfa.states[state_id]
            for edge in state.edges:
                self.dot.edge(str(state.id), str(edge.to_state), label=str(edge.symbol))

        return self.dot