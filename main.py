from PatternClass import Pattern
from GraphicTree import ASTGraphviz, NFAGraphviz

def main():
    regex = Pattern.compile("a+")
    #print(regex.tokens)
    gAST = ASTGraphviz()
    gAST.build(regex.ast)
    gAST.dot.save("ast_tree.dot")

    gNFA = NFAGraphviz()
    gNFA.build(regex.nfa)
    gNFA.dot.save("nfa_tree.dot")

if __name__ == '__main__':
    main()
