from PatternClass import Pattern
from pythonProject1.visualization.GraphvizVisualizer import GraphvizVisualizer

def main():
    pattern = Pattern.compile("(a|b)c+")

    visualizer = GraphvizVisualizer()

    ast_graph = visualizer.pattern_to_graph(pattern, "ast")
    nfa_graph = visualizer.pattern_to_graph(pattern, "nfa")
    dfa_graph = visualizer.pattern_to_graph(pattern, "dfa")
    min_dfa_graph = visualizer.pattern_to_graph(pattern, "min_dfa")

    visualizer.render(ast_graph, "ast")
    visualizer.render(nfa_graph, "nfa")
    visualizer.render(dfa_graph, "dfa")
    visualizer.render(min_dfa_graph, "min_dfa")

if __name__ == '__main__':
    main()
