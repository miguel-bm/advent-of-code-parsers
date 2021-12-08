import pytest
from aocp.parsers import IntParser, BoolParser, CustomTransform, SortTransform


class TestIntParser:
    @pytest.mark.parametrize(
        "string,base,expected",
        [
            pytest.param("1", None, 1, id="base case"),
            pytest.param("  1\n", None, 1, id="with whitespace"),
            pytest.param("52634875", None, 52634875, id="long number"),
            pytest.param("\n-2542", None, -2542, id="negative number"),
            pytest.param("101\t", 2, 5, id="different base"),
        ],
    )
    def test_parse(self, string, base, expected):
        parser = IntParser(base=base)
        assert parser.parse(string) == expected


class TestBoolParser:
    @pytest.mark.parametrize(
        "string,true,false,expected",
        [
            pytest.param("1", None, None, True, id="base case true"),
            pytest.param("0", None, None, False, id="base case false"),
            pytest.param("<", "<", ">", True, id="specific case true"),
            pytest.param(">", "<", ">", False, id="specific case false"),
            pytest.param("pos", "pos", "neg", True, id="multichar case true"),
            pytest.param("neg", "pos", "neg", False, id="multichar case false"),
            pytest.param("  1\n", None, None, True, id="with whitespace"),
        ],
    )
    def test_parse(self, string, true, false, expected):
        parser = BoolParser(true=true, false=false)
        assert parser.parse(string) == expected


class TestCustomTransform:
    @pytest.mark.parametrize(
        "string,function,expected",
        [
            pytest.param("ab", lambda x: x + "c", "abc", id="str to str"),
            pytest.param("ab", lambda x: len(x), 2, id="str to int"),
            pytest.param("a,b", lambda x: x.split(","), ["a", "b"], id="str to list"),
        ],
    )
    def test_parse(self, string, function, expected):
        parser = CustomTransform(function=function)
        assert parser.parse(string) == expected


class TestSortTransform:
    @pytest.mark.parametrize(
        "string,reverse,key,expected",
        [
            pytest.param("cba", False, None, "abc", id="no key"),
            pytest.param("bca", True, None, "cba", id="no key"),
        ],
    )
    def test_parse(self, string, reverse, key, expected):
        parser = SortTransform(reverse=reverse, key=key)
        assert parser.parse(string) == expected
