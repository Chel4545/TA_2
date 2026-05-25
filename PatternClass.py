from __future__ import annotations #для типа класса внутри класса

from pythonProject1.logic.Tokenizer import Tokenizer
from pythonProject1.logic.ASTclass import AST
from pythonProject1.logic.NFAclass import NFA
from pythonProject1.logic.DFAclass import DFA
from pythonProject1.logic.RegexRestorer import GNFA
from pythonProject1.logic.MatchResult import MatchResult

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
        if self.has_backreferences:
            pass #доп

        if self.has_capture_groups:
            if self.nfa is None:
                return None

            return self.nfa.search_with_groups(data)

        dfa = self.min_dfa or self.dfa

        if dfa is None:
            return None

        result = dfa.search(data)

        if result is None:
            return None

        start, end, value = result
        return MatchResult(
            start=start,
            end=end,
            value=value,
        )

    def accepts(self, data: str):
        if self.has_backreferences:
            pass #доп

        dfa = self.min_dfa or self.dfa

        if dfa is None:
            return None

        return dfa.accepts(data)

    def to_regex(self) -> str | None:
        dfa = self.min_dfa or self.dfa

        if dfa is None:
            return None

        gnfa = GNFA()
        return gnfa.build_regex(dfa)

    def diff(self, b: Pattern) -> Pattern:
        dfa_a = self.min_dfa or self.dfa
        dfa_b = b.min_dfa or b.dfa

        if dfa_a is None or dfa_b is None:
            raise ValueError("Оба Pattern должны быть скомпилированы")

        new_pattern = Pattern("")
        new_pattern.dfa = dfa_a.diff(dfa_b)
        return new_pattern

    def negate(self) -> Pattern:
        dfa = self.min_dfa or self.dfa

        if dfa is None:
            raise ValueError("Pattern должен быть скомпилирован")

        new_pattern = Pattern("")
        new_pattern.dfa = dfa.negate(dfa.alphabet)
        new_pattern.min_dfa = new_pattern.dfa.build_min_dfa()

        return new_pattern

    @classmethod
    def compile(cls, regex: str) -> Pattern | None:
        pattern = cls(regex) #создание объекта класса

        tokenizer = Tokenizer(regex)
        pattern.tokens = tokenizer.tokens

        ast_maker  = AST()
        pattern.ast = ast_maker.parse(pattern.tokens)
        pattern.has_capture_groups = ast_maker.analyze_capture_groups(pattern.tokens)
        pattern.has_backreferences = ast_maker.analyze_backreferences(pattern.tokens)

        nfa = NFA()
        nfa.build_nfa(pattern.ast)
        pattern.nfa = nfa

        dfa = DFA()
        dfa.build_dfa(pattern.nfa)
        pattern.dfa = dfa

        pattern.min_dfa = dfa.build_min_dfa()

        return pattern