from PatternClass import Pattern
from GraphicTree import ASTGraphviz, NFAGraphviz, DFAGraphviz, MinDFAGraphviz, OperationDFAGraphviz

def main():
    pass
#    regex = Pattern.compile("ab")
#    #print(regex.tokens)
#    gAST = ASTGraphviz()
#    gAST.build(regex.ast)
#    gAST.dot.save("ast_tree.dot")

#    gNFA = NFAGraphviz()
#    gNFA.build(regex.nfa)
#    gNFA.dot.save("nfa_tree.dot")

#   gDFA = DFAGraphviz()
#    gDFA.build(regex.dfa)
#    gDFA.dot.save("dfa_tree.dot")

#    minDFA = MinDFAGraphviz()
#    minDFA.build(regex.min_dfa)
#    minDFA.dot.save("min_dfa_tree.dot")

#    print(type(regex))

#    p = Pattern.compile("^")
#    p_comp = p.complement()
#    g = OperationDFAGraphviz()
#    g.build(p_comp.dfa, title="Complement of a+")
#    g.dot.save("complement_a_plus.dot")
#    print(p_comp.search("a"))


#    p1 = Pattern.compile("a")
#    p2 = Pattern.compile("b")
#    union_pattern = p1.subtraction(p2)
#    print(union_pattern.search("b"))

#    g_union = OperationDFAGraphviz()
#    g_union.build(union_pattern.dfa, title="Union of 'a' and 'b'")
#    g_union.dot.save("union_dfa.dot")

#    p = Pattern.compile("ab")
#    print(p.restoration())

if __name__ == '__main__':
    main()
