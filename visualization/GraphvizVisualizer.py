from pathlib import Path
from graphviz import Digraph
import re

from pythonProject1.logic.ASTclass import (
    Literal,
    Epsilon,
    Concat,
    Or,
    Plus,
    Repeat,
    Group,
    BackRef,
)


class GraphvizVisualizer:
    def __init__(self, output_dir: str | Path | None = None):

        if output_dir is None:
            self.output_dir = Path(__file__).resolve().parent / "output"
        else:
            self.output_dir = Path(output_dir)

        self.output_dir.mkdir(parents=True, exist_ok=True)


    def safe_filename(self, filename: str) -> str:
        filename = str(filename)

        replacements = {
            "\\": "backslash",
            "/": "_",
            "|": "_or_",
            ":": "",
            ">": "to",
            "<": "",
            '"': "",
            "?": "",
            "*": "",
        }

        for old, new in replacements.items():
            filename = filename.replace(old, new)

        filename = re.sub(r"[\s,()]+", "_", filename)
        filename = re.sub(r"_+", "_", filename)
        filename = filename.strip("._ ")

        if filename == "":
            return "graph"

        return filename

    def ast_to_graph(self, root) -> Digraph:
        graph = Digraph("AST")
        graph.attr(rankdir="TB")

        counter = 0

        def new_id():
            nonlocal counter
            node_id = f"node_{counter}"
            counter += 1
            return node_id

        def visit(node):
            node_id = new_id()

            if isinstance(node, Literal):
                label = f"Literal({node.char})"

            elif isinstance(node, Epsilon):
                label = "Epsilon(^)"

            elif isinstance(node, Concat):
                label = "Concat(.)"

            elif isinstance(node, Or):
                label = "Or(|)"

            elif isinstance(node, Plus):
                label = "Plus(+)"

            elif isinstance(node, Repeat):
                label = f"Repeat({node.min},{node.max})"

            elif isinstance(node, Group):
                label = f"Group({node.num})"

            elif isinstance(node, BackRef):
                label = f"BackRef({node.num})"

            else:
                label = type(node).__name__

            graph.node(node_id, label)

            if isinstance(node, Concat) or isinstance(node, Or):
                left_id = visit(node.left)
                right_id = visit(node.right)

                graph.edge(node_id, left_id, "left")
                graph.edge(node_id, right_id, "right")

            elif isinstance(node, Plus):
                expr_id = visit(node.expr)
                graph.edge(node_id, expr_id)

            elif isinstance(node, Repeat):
                expr_id = visit(node.expr)
                graph.edge(node_id, expr_id)

            elif isinstance(node, Group):
                expr_id = visit(node.expr)
                graph.edge(node_id, expr_id)

            return node_id

        visit(root)

        return graph

    def nfa_to_graph(self, nfa) -> Digraph:
        graph = Digraph("NFA")
        graph.attr(rankdir="LR")

        graph.node("start", "", shape="none")

        for state_id, state in nfa.states.items():
            shape = "doublecircle" if state.is_accepting else "circle"
            graph.node(str(state_id), str(state_id), shape=shape)


        for from_state_id, state in nfa.states.items():
            for edge in state.edges:
                if edge.symbol is None:
                    label = "^"

                    if edge.group_start is not None:
                        label += f" / start({edge.group_start})"

                    if edge.group_end is not None:
                        label += f" / end({edge.group_end})"
                else:
                    label = edge.symbol

                graph.edge(
                    str(from_state_id),
                    str(edge.to_state),
                    label=label,
                )

        return graph

    def dfa_to_graph(self, dfa) -> Digraph:
        graph = Digraph("DFA")
        graph.attr(rankdir="LR")

        graph.node("start", "", shape="none")

        for state_id, state in dfa.states.items():
            shape = "doublecircle" if state.is_accepting else "circle"
            graph.node(str(state_id), str(state_id), shape=shape)


        for from_state_id, state in dfa.states.items():
            for edge in state.edges:
                graph.edge(
                    str(from_state_id),
                    str(edge.to_state),
                    label=edge.symbol,
                )

        return graph

    def pattern_to_graph(self, pattern, target: str = "min_dfa") -> Digraph:
        if target == "ast":
            if pattern.ast is None:
                raise ValueError("У Pattern нет AST")
            return self.ast_to_graph(pattern.ast)

        if target == "nfa":
            if pattern.nfa is None:
                raise ValueError("У Pattern нет NFA")
            return self.nfa_to_graph(pattern.nfa)

        if target == "dfa":
            if pattern.dfa is None:
                raise ValueError("У Pattern нет DFA")
            return self.dfa_to_graph(pattern.dfa)

        if target == "min_dfa":
            if pattern.min_dfa is None:
                raise ValueError("У Pattern нет min_dfa")
            return self.dfa_to_graph(pattern.min_dfa)

        raise ValueError(f"Неизвестный target: {target}")

    def render(
        self,
        graph: Digraph,
        filename: str,
        format: str = "png",
        subdir: str | Path | None = None,
    ) -> Path:

        if subdir is None:
            output_dir = self.output_dir
        else:
            output_dir = self.output_dir / subdir

        output_dir.mkdir(parents=True, exist_ok=True)

        filename_path = Path(self.safe_filename(filename))

        # Если случайно передали "ast.png", убираем расширение,
        # потому что graphviz сам добавит .png
        if filename_path.suffix == f".{format}":
            filename_path = filename_path.with_suffix("")

        output_path = output_dir / filename_path

        rendered_path = graph.render(
            str(output_path),
            format=format,
            cleanup=True,
        )

        return Path(rendered_path)