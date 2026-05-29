import pytest

from pythonProject1.logic.DFAclass import DFA, DFAEdge
from pythonProject1.PatternClass import Pattern

CASES_IS_EQUIVALENT = {
    "a == a": (
        "a",
        "a",
        True,
        "equiv_a_a",
    ),

    "a|b == b|a": (
        "a|b",
        "b|a",
        True,
        "equiv_a_or_b_b_or_a",
    ),

    "ab|ac == a(b|c)": (
        "ab|ac",
        "a(b|c)",
        True,
        "equiv_ab_or_ac_a_group_b_or_c",
    ),

    "a+ == a{1,}": (
        "a+",
        "a{1,}",
        True,
        "equiv_a_plus_a_1_none",
    ),

    "(ab)+ == (ab){1,}": (
        "(ab)+",
        "(ab){1,}",
        True,
        "equiv_ab_plus_ab_1_none",
    ),

    "a{2,4} == aa|aaa|aaaa": (
        "a{2,4}",
        "aa|aaa|aaaa",
        True,
        "equiv_a_2_4_expanded",
    ),

    "^|a == a|^": (
        "^|a",
        "a|^",
        True,
        "equiv_epsilon_or_a_a_or_epsilon",
    ),

    "a != b": (
        "a",
        "b",
        False,
        "equiv_a_b_false",
    ),

    "a+ != aa": (
        "a+",
        "aa",
        False,
        "equiv_a_plus_aa_false",
    ),

    "a+ != a{2,}": (
        "a+",
        "a{2,}",
        False,
        "equiv_a_plus_a_2_none_false",
    ),

    "a{1,3} != a{2,4}": (
        "a{1,3}",
        "a{2,4}",
        False,
        "equiv_range_1_3_range_2_4_false",
    ),

    "ab|ac != ab|bc": (
        "ab|ac",
        "ab|bc",
        False,
        "equiv_ab_or_ac_ab_or_bc_false",
    ),

    "^ != a": (
        "^",
        "a",
        False,
        "equiv_epsilon_a_false",
    ),

    "^|a != a|b": (
        "^|a",
        "a|b",
        False,
        "equiv_epsilon_or_a_a_or_b_false",
    ),
}


@pytest.mark.parametrize("case_name", CASES_IS_EQUIVALENT.keys())
def test_is_equivalent(case_name):
    regex_a, regex_b, expected_result, filename = CASES_IS_EQUIVALENT[case_name]


    pattern_a = Pattern.compile(regex_a)
    pattern_b = Pattern.compile(regex_b)

    dfa_a = pattern_a.dfa
    dfa_b = pattern_b.dfa

    min_dfa_a = pattern_a.min_dfa
    min_dfa_b = pattern_b.min_dfa

    assert dfa_a.is_equivalent(dfa_b) is expected_result
    assert dfa_b.is_equivalent(dfa_a) is expected_result

    assert min_dfa_a.is_equivalent(min_dfa_b) is expected_result
    assert min_dfa_b.is_equivalent(min_dfa_a) is expected_result

    # Дополнительно проверяем, что минимизация не изменила язык
    assert dfa_a.is_equivalent(min_dfa_a) is True
    assert dfa_b.is_equivalent(min_dfa_b) is True

CASES_IS_ISOMORPHIC = {
    "a == a": (
        "a",
        "a",
        True,
        True,
        "isomorphic_a_a",
    ),

    "a|b == b|a": (
        "a|b",
        "b|a",
        True,
        True,
        "isomorphic_a_or_b_b_or_a",
    ),

    "a+ == a{1,}": (
        "a+",
        "a{1,}",
        False,
        True,
        "isomorphic_a_plus_a_1_none",
    ),

    "(ab)+ == (ab){1,}": (
        "(ab)+",
        "(ab){1,}",
        False,
        True,
        "isomorphic_ab_plus_ab_1_none",
    ),

    "a != b": (
        "a",
        "b",
        False,
        False,
        "not_isomorphic_a_b",
    ),

    "a+ != aa": (
        "a+",
        "aa",
        False,
        False,
        "not_isomorphic_a_plus_aa",
    ),

    "a{1,3} != a{2,4}": (
        "a{1,3}",
        "a{2,4}",
        False,
        False,
        "not_isomorphic_range_1_3_range_2_4",
    ),

    "ab|ac != ab|bc": (
        "ab|ac",
        "ab|bc",
        False,
        False,
        "not_isomorphic_ab_or_ac_ab_or_bc",
    ),

    "^ != a": (
        "^",
        "a",
        False,
        False,
        "not_isomorphic_epsilon_a",
    ),

    "^|a != a|b": (
        "^|a",
        "a|b",
        False,
        False,
        "not_isomorphic_epsilon_or_a_a_or_b",
    ),
}


@pytest.mark.parametrize("case_name", CASES_IS_ISOMORPHIC.keys())
def test_is_isomorphic(case_name):
    (
        regex_a,
        regex_b,
        expected_dfa_isomorphic,
        expected_min_dfa_isomorphic,
        filename,
    ) = CASES_IS_ISOMORPHIC[case_name]

    pattern_a = Pattern.compile(regex_a)
    pattern_b = Pattern.compile(regex_b)

    dfa_a = pattern_a.dfa
    dfa_b = pattern_b.dfa

    min_dfa_a = pattern_a.min_dfa
    min_dfa_b = pattern_b.min_dfa

    assert dfa_a.is_isomorphic(dfa_b) is expected_dfa_isomorphic
    assert dfa_b.is_isomorphic(dfa_a) is expected_dfa_isomorphic

    assert min_dfa_a.is_isomorphic(min_dfa_b) is expected_min_dfa_isomorphic
    assert min_dfa_b.is_isomorphic(min_dfa_a) is expected_min_dfa_isomorphic

CASES_MAKE_COMPLETE = {
    "a over alphabet a,b": (
        "a",
        {"a", "b"},
        ["a"],
        ["", "b", "aa", "ab", "ba"],
        "make_complete_a_ab",
    ),

    "ab over alphabet a,b": (
        "ab",
        {"a", "b"},
        ["ab"],
        ["", "a", "b", "aa", "bb", "aba"],
        "make_complete_ab_ab",
    ),

    "a+ over alphabet a,b": (
        "a+",
        {"a", "b"},
        ["a", "aa", "aaa"],
        ["", "b", "ab", "ba"],
        "make_complete_a_plus_ab",
    ),

    "a|b over alphabet a,b": (
        "a|b",
        {"a", "b"},
        ["a", "b"],
        ["", "aa", "bb", "ab", "ba"],
        "make_complete_a_or_b_ab",
    ),

    "a{2,4} over alphabet a,b": (
        "a{2,4}",
        {"a", "b"},
        ["aa", "aaa", "aaaa"],
        ["", "a", "aaaaa", "b", "aab"],
        "make_complete_a_2_4_ab",
    ),

    "^ over alphabet a,b": (
        "^",
        {"a", "b"},
        [""],
        ["a", "b", "aa"],
        "make_complete_epsilon_ab",
    ),
}


@pytest.mark.parametrize("case_name", CASES_MAKE_COMPLETE.keys())
def test_make_complete(case_name):
    regex, alphabet, accepted_data, rejected_data, filename = CASES_MAKE_COMPLETE[case_name]

    pattern = Pattern.compile(regex)

    dfa = pattern.min_dfa or pattern.dfa
    original = dfa.clone()

    dfa.make_complete(alphabet)

    assert dfa.alphabet == alphabet

    # язык не должен измениться
    assert dfa.is_equivalent(original) is True
    assert original.is_equivalent(dfa) is True

    # структура должна измениться
    assert dfa.is_isomorphic(original) is False
    assert original.is_isomorphic(dfa) is False

    for data in accepted_data:
        assert dfa.accepts(data) is True
        assert original.accepts(data) is True

    for data in rejected_data:
        assert dfa.accepts(data) is False
        assert original.accepts(data) is False

CASES_CLONE = {
    "clone a": (
        "a",
        ["a"],
        ["", "b", "aa"],
        "clone_a",
    ),

    "clone ab": (
        "ab",
        ["ab"],
        ["", "a", "b", "aa", "aba"],
        "clone_ab",
    ),

    "clone a+": (
        "a+",
        ["a", "aa", "aaa"],
        ["", "b", "ab", "ba"],
        "clone_a_plus",
    ),

    "clone a|b": (
        "a|b",
        ["a", "b"],
        ["", "aa", "bb", "ab"],
        "clone_a_or_b",
    ),

    "clone a{2,4}": (
        "a{2,4}",
        ["aa", "aaa", "aaaa"],
        ["", "a", "aaaaa", "b"],
        "clone_a_2_4",
    ),

    "clone epsilon": (
        "^",
        [""],
        ["a", "aa", "b"],
        "clone_epsilon",
    ),

    "clone ab|ac": (
        "ab|ac",
        ["ab", "ac"],
        ["", "a", "b", "abc", "aa"],
        "clone_ab_or_ac",
    ),
}


@pytest.mark.parametrize("case_name", CASES_CLONE.keys())
def test_clone(case_name):
    regex, accepted_data, rejected_data, filename = CASES_CLONE[case_name]

    pattern = Pattern.compile(regex)

    dfa = pattern.dfa
    cloned = dfa.clone()

    assert cloned is not dfa

    assert cloned.start == dfa.start
    assert cloned.next_id == dfa.next_id
    assert cloned.alphabet == dfa.alphabet
    assert cloned.states == dfa.states

    # состояния новые объекы
    for state_id in dfa.states:
        assert cloned.states[state_id] is not dfa.states[state_id]

        assert cloned.states[state_id].id == dfa.states[state_id].id
        assert cloned.states[state_id].is_accepting == dfa.states[state_id].is_accepting
        assert cloned.states[state_id].edges == dfa.states[state_id].edges

        for edge_index in range(len(dfa.states[state_id].edges)):
            assert cloned.states[state_id].edges[edge_index] is not dfa.states[state_id].edges[edge_index]

    # язык
    assert cloned.is_equivalent(dfa) is True
    assert dfa.is_equivalent(cloned) is True

    # cтруктура
    assert cloned.is_isomorphic(dfa) is True
    assert dfa.is_isomorphic(cloned) is True

    for data in accepted_data:
        assert dfa.accepts(data) is True
        assert cloned.accepts(data) is True

    for data in rejected_data:
        assert dfa.accepts(data) is False
        assert cloned.accepts(data) is False

CASES_NEGATE = {
    "negate a over alphabet a,b": (
        "a",
        {"a", "b"},
        ["", "b", "aa", "ab", "ba"],
        ["a"],
        "negate_a_ab",
    ),

    "negate ab over alphabet a,b": (
        "ab",
        {"a", "b"},
        ["", "a", "b", "aa", "bb", "aba"],
        ["ab"],
        "negate_ab_ab",
    ),

    "negate a+ over alphabet a,b": (
        "a+",
        {"a", "b"},
        ["", "b", "ab", "ba"],
        ["a", "aa", "aaa"],
        "negate_a_plus_ab",
    ),

    "negate a|b over alphabet a,b": (
        "a|b",
        {"a", "b"},
        ["", "aa", "bb", "ab", "ba"],
        ["a", "b"],
        "negate_a_or_b_ab",
    ),

    "negate a{2,4} over alphabet a,b": (
        "a{2,4}",
        {"a", "b"},
        ["", "a", "aaaaa", "b", "aab"],
        ["aa", "aaa", "aaaa"],
        "negate_a_2_4_ab",
    ),

    "negate epsilon over alphabet a,b": (
        "^",
        {"a", "b"},
        ["a", "b", "aa", "ab"],
        [""],
        "negate_epsilon_ab",
    ),
    "negate ((me)+)|p|hi{2,5} over alphabet m,e,p,h,i": (
        "((me)+)|p|hi{2,5}",
        {"m", "e", "p", "h", "i"},
        ["m", "e", "hiiiiii", "pp", "mem"],
        ["me", "memememe", "p", "hiiii"],
        "negate_me_plus_or_p_or_hi_2_5",
    ),
}


@pytest.mark.parametrize("case_name", CASES_NEGATE.keys())
def test_negate(case_name):
    regex, alphabet, accepted_by_negated, rejected_by_negated, filename = CASES_NEGATE[case_name]

    pattern = Pattern.compile(regex)

    dfa = pattern.min_dfa or pattern.dfa
    original = dfa.clone()

    negated = dfa.negate(alphabet)

    assert negated is not dfa
    assert negated.alphabet == alphabet

    assert negated.is_equivalent(original) is False
    assert original.is_equivalent(negated) is False

    assert negated.is_isomorphic(original) is False
    assert original.is_isomorphic(negated) is False

    for data in accepted_by_negated:
        assert negated.accepts(data) is True
        assert original.accepts(data) is False

    for data in rejected_by_negated:
        assert negated.accepts(data) is False
        assert original.accepts(data) is True

    double_negated = negated.negate(alphabet)

    # двойное отрицание
    assert double_negated.is_equivalent(original) is True
    assert original.is_equivalent(double_negated) is True

CASES_UNION = {
    "a union b = a|b": (
        "a",
        "b",
        "a|b",
        ["a", "b"],
        ["", "ab", "aa", "bb"],
        "union_a_b",
    ),

    "ab union ac = ab|ac": (
        "ab",
        "ac",
        "ab|ac",
        ["ab", "ac"],
        ["", "a", "b", "abc", "aa"],
        "union_ab_ac",
    ),

    "a+ union b+ = a+|b+": (
        "a+",
        "b+",
        "a+|b+",
        ["a", "aa", "aaa", "b", "bb", "bbb"],
        ["", "ab", "ba", "aba"],
        "union_a_plus_b_plus",
    ),

    "a{2,4} union b = a{2,4}|b": (
        "a{2,4}",
        "b",
        "a{2,4}|b",
        ["aa", "aaa", "aaaa", "b"],
        ["", "a", "aaaaa", "ab", "bb"],
        "union_a_2_4_b",
    ),

    "^ union a = ^|a": (
        "^",
        "a",
        "^|a",
        ["", "a"],
        ["aa", "b", "ab"],
        "union_epsilon_a",
    ),

    "ab union c+ = ab|c+": (
        "ab",
        "c+",
        "ab|c+",
        ["ab", "c", "cc", "ccc"],
        ["", "a", "b", "abc", "ac"],
        "union_ab_c_plus",
    ),
}


@pytest.mark.parametrize("case_name", CASES_UNION.keys())
def test_union(case_name):
    (
        regex_a,
        regex_b,
        expected_regex,
        accepted_data,
        rejected_data,
        filename,
    ) = CASES_UNION[case_name]

    pattern_a = Pattern.compile(regex_a)
    pattern_b = Pattern.compile(regex_b)
    expected_pattern = Pattern.compile(expected_regex)

    dfa_a = pattern_a.min_dfa or pattern_a.dfa
    dfa_b = pattern_b.min_dfa or pattern_b.dfa
    expected_dfa = expected_pattern.min_dfa or expected_pattern.dfa

    result = dfa_a.union(dfa_b)

    result_min = result.build_min_dfa()

    expected_complete = expected_dfa.clone()
    expected_complete.make_complete(result.alphabet)

    expected_min = expected_complete.build_min_dfa()

    assert result.alphabet == set(dfa_a.alphabet) | set(dfa_b.alphabet)
    assert result_min.alphabet == expected_min.alphabet

    assert result_min.is_equivalent(expected_min) is True
    assert expected_min.is_equivalent(result_min) is True

    assert result_min.is_isomorphic(expected_min) is True
    assert expected_min.is_isomorphic(result_min) is True

    for data in accepted_data:
        assert result_min.accepts(data) is True
        assert expected_min.accepts(data) is True

    for data in rejected_data:
        assert result_min.accepts(data) is False
        assert expected_min.accepts(data) is False

CASES_INTERSECTION = {
    "a|b intersection b|c = b": (
        "a|b",
        "b|c",
        "b",
        ["b"],
        ["", "a", "c", "ab", "bc"],
        "intersection_a_or_b_b_or_c",
    ),

    "a+ intersection aa = aa": (
        "a+",
        "aa",
        "aa",
        ["aa"],
        ["", "a", "aaa", "b"],
        "intersection_a_plus_aa",
    ),

    "a{1,3} intersection a{2,4} = a{2,3}": (
        "a{1,3}",
        "a{2,4}",
        "a{2,3}",
        ["aa", "aaa"],
        ["", "a", "aaaa", "b"],
        "intersection_ranges_1_3_and_2_4",
    ),

    "ab|ac intersection ac|ad = ac": (
        "ab|ac",
        "ac|ad",
        "ac",
        ["ac"],
        ["", "ab", "ad", "a", "abc"],
        "intersection_ab_or_ac_ac_or_ad",
    ),

    "^|a intersection a|b = a": (
        "^|a",
        "a|b",
        "a",
        ["a"],
        ["", "b", "aa"],
        "intersection_epsilon_or_a_a_or_b",
    ),

    "a+|b intersection b|c = b": (
        "a+|b",
        "b|c",
        "b",
        ["b"],
        ["", "a", "aa", "c", "ab"],
        "intersection_a_plus_or_b_b_or_c",
    ),

    "ab|c+ intersection c{2,} = c{2,}": (
        "ab|c+",
        "c{2,}",
        "c{2,}",
        ["cc", "ccc", "cccc"],
        ["", "c", "ab", "ac"],
        "intersection_ab_or_c_plus_c_2_none",
    ),
}


@pytest.mark.parametrize("case_name", CASES_INTERSECTION.keys())
def test_intersection(case_name):
    (
        regex_a,
        regex_b,
        expected_regex,
        accepted_data,
        rejected_data,
        filename,
    ) = CASES_INTERSECTION[case_name]


    pattern_a = Pattern.compile(regex_a)
    pattern_b = Pattern.compile(regex_b)
    expected_pattern = Pattern.compile(expected_regex)

    dfa_a = pattern_a.min_dfa or pattern_a.dfa
    dfa_b = pattern_b.min_dfa or pattern_b.dfa
    expected_dfa = expected_pattern.min_dfa or expected_pattern.dfa

    result = dfa_a.intersection(dfa_b)

    result_min = result.build_min_dfa()

    expected_complete = expected_dfa.clone()
    expected_complete.make_complete(result.alphabet)

    expected_min = expected_complete.build_min_dfa()


    assert result.alphabet == set(dfa_a.alphabet) | set(dfa_b.alphabet)
    assert result_min.alphabet == expected_min.alphabet

    assert result_min.is_equivalent(expected_min) is True
    assert expected_min.is_equivalent(result_min) is True

    assert result_min.is_isomorphic(expected_min) is True
    assert expected_min.is_isomorphic(result_min) is True

    for data in accepted_data:
        assert result_min.accepts(data) is True
        assert expected_min.accepts(data) is True

    for data in rejected_data:
        assert result_min.accepts(data) is False
        assert expected_min.accepts(data) is False

CASES_DIFF = {
    "a|b minus b = a": (
        "a|b",
        "b",
        "a",
        ["a"],
        ["", "b", "ab", "aa", "bb"],
        "diff_a_or_b_minus_b",
    ),

    "a|b minus a = b": (
        "a|b",
        "a",
        "b",
        ["b"],
        ["", "a", "ab", "bb", "aa"],
        "diff_a_or_b_minus_a",
    ),

    "ab|ac minus ab = ac": (
        "ab|ac",
        "ab",
        "ac",
        ["ac"],
        ["", "a", "ab", "abc", "aa"],
        "diff_ab_or_ac_minus_ab",
    ),

    "ab|ac minus ac = ab": (
        "ab|ac",
        "ac",
        "ab",
        ["ab"],
        ["", "a", "ac", "abc", "aa"],
        "diff_ab_or_ac_minus_ac",
    ),

    "a+ minus aa = a|aaa+": (
        "a+",
        "aa",
        "a|aaa+",
        ["a", "aaa", "aaaa", "aaaaa"],
        ["", "aa", "b", "ab"],
        "diff_a_plus_minus_aa",
    ),

    "ab+ minus abb = ab|abbb+": (
        "ab+",
        "abb",
        "ab|abbb+",
        ["ab", "abbb", "abbbb"],
        ["", "a", "abb", "b", "aba"],
        "diff_ab_plus_minus_abb",
    ),

    "^|a minus ^ = a": (
        "^|a",
        "^",
        "a",
        ["a"],
        ["", "aa", "b"],
        "diff_epsilon_or_a_minus_epsilon",
    ),

    "a+ minus a+ = empty": (
        "a+",
        "a+",
        None,
        [],
        ["", "aa", "b"],
        "diff_a_plus_a_plus_empty",
    ),

    "a|b minus a|b = empty": (
        "a|b",
        "a|b",
        None,
        [],
        ["", "aa", "b"],
        "diff_a_or_b_a_or_b_empty",
    ),
}


@pytest.mark.parametrize("case_name", CASES_DIFF.keys())
def test_diff(case_name):
    (
        regex_a,
        regex_b,
        expected_regex,
        accepted_data,
        rejected_data,
        filename,
    ) = CASES_DIFF[case_name]

    pattern_a = Pattern.compile(regex_a)
    pattern_b = Pattern.compile(regex_b)

    dfa_a = pattern_a.min_dfa or pattern_a.dfa
    dfa_b = pattern_b.min_dfa or pattern_b.dfa

    result = dfa_a.diff(dfa_b)

    result_min = result.build_min_dfa()

    assert result.alphabet == set(dfa_a.alphabet) | set(dfa_b.alphabet)

    if expected_regex is None:
        assert accepted_data == []

        for state in result_min.states.values():
            assert state.is_accepting is False

        for data in rejected_data:
            assert result_min.accepts(data) is False

        return

    expected_pattern = Pattern.compile(expected_regex)
    expected_dfa = expected_pattern.min_dfa or expected_pattern.dfa

    expected_complete = expected_dfa.clone()
    expected_complete.make_complete(result.alphabet)

    expected_min = expected_complete.build_min_dfa()

    assert result_min.alphabet == expected_min.alphabet

    assert result_min.is_equivalent(expected_min) is True
    assert expected_min.is_equivalent(result_min) is True

    assert result_min.is_isomorphic(expected_min) is True
    assert expected_min.is_isomorphic(result_min) is True

    for data in accepted_data:
        assert dfa_a.accepts(data) is True
        assert dfa_b.accepts(data) is False

        assert result_min.accepts(data) is True
        assert expected_min.accepts(data) is True

    for data in rejected_data:
        assert result_min.accepts(data) is False
        assert expected_min.accepts(data) is False