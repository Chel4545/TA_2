from __future__ import annotations #для типа класса внутри класса
from tokenizer import Tokenizer
from ASTclass import AST
from NFAclass import NFA

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
        pass

    def restoration(self) -> str:
        pass

    def subtraction(self, b: Pattern) -> Pattern:
        pass

    def supplement(self, b: Pattern) -> Pattern:
        pass

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


        return pattern