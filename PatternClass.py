from __future__ import annotations #для типа класса внутри класса
from tokenizer import Tokenizer
from ASTclass import AST
from NFAclass import NFA
from DFAclass import DFA
from MINDFAclass import MinDFA

class Pattern:
    def __init__(self, regex: str):
        self.regex = regex
        self.tokens = None
        self.ast = None
        self.nfa = None
        self.dfa = None
        self.min_dfa = None
        self.has_capture_groups = False
        self.has_backreferences = False

    def search(self, data: str):
        res = None
        if self.has_backreferences:
            pass #использовать nfa
        else:
            if self.min_dfa is not None:
                res = self.min_dfa.search(data)
            elif self.dfa is not None:
                res = self.dfa.search(data)
            else:
                pass

        return True if res is not None else False

    def restoration(self) -> str:
        pass

    def subtraction(self, b: Pattern) -> Pattern:
        newPattern = Pattern(self.regex)
        newPattern.dfa = self.dfa.subtraction(b.dfa)
        return newPattern

    def complement(self) -> Pattern:
        newPattern = Pattern(self.regex)
        newPattern.dfa = self.dfa.complement()
        return newPattern

    @classmethod
    def compile(cls, regex: str) -> Pattern:
        pattern = cls(regex)

        tokenizer = Tokenizer(regex)
        pattern.tokens = tokenizer.tokens

        ASTmaker = AST()
        pattern.ast = ASTmaker.parse(pattern.tokens)
        pattern.has_capture_groups = ASTmaker.analyze_capture_groups(pattern.tokens)
        pattern.has_backreferences = ASTmaker.analyze_backreferences(pattern.tokens)

        nfa = NFA()
        nfa.build_nfa(pattern.ast)
        pattern.nfa = nfa

        dfa = DFA()
        dfa.build_dfa(pattern.nfa)
        pattern.dfa = dfa

        mindfa = MinDFA()
        mindfa.build_min_dfa(pattern.dfa)
        pattern.min_dfa = mindfa

        return pattern