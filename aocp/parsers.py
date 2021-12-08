from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any, Callable, TypeVar, Sequence, Mapping, Union
import parse
import re

X = TypeVar("X")


class BaseAoCParser(ABC):
    SPLITTER_PRIORITY = ["\n\n", "\n", "|", "->", ";", ",", " ", ":"]

    @staticmethod
    def _find_integers(string: str, base: int = 10) -> list[int]:
        """Find all integers present in a string and return as a list.

        Args:
            string (str): The string to search for integers
            base (int, optional): The base to use when interpreting integers. Defaults to 10.

        Returns:
            list[int]: A list of integers found in the string.
        """
        return [int(x, base) for x in re.findall(r"-?\d+", string)]

    @abstractmethod
    def parse(self, string: str) -> Any:
        pass

    def __call__(self, string: str) -> Any:
        return self.parse(string)


class BaseTransformParser(BaseAoCParser, ABC):
    pass


class IntParser(BaseTransformParser):
    def __init__(self, base: int = 10):
        """Initializes a parser which finds the first integer in a string.

        Args:
            base (int, optional): The base of the integers to parse. Defaults to 10.
        """
        self.base = base

    def parse(self, string: str) -> int:
        all_integers = self._find_integers(string)
        return int(all_integers[0], self.base)


class BoolParser(BaseTransformParser):
    def __init__(self, true: str = None, false: str = None):
        self.true = true or "1"
        self.false = false or "0"

    def parse(self, string: str) -> bool:
        string = string.strip()
        if string == self.true:
            return True
        elif string == self.false:
            return False
        else:
            raise ValueError(f"{string} is not a boolean")


class CustomTransform(BaseTransformParser):
    def __init__(self, function: Callable[[str], X]):
        self.function = function

    def parse(self, string: str) -> X:
        return self.function(string)


class SortTransform(BaseTransformParser):
    def __init__(self, reverse: bool = False, key: Callable[[X], Any] = None):
        self.reverse = reverse
        self.key = key

    def parse(self, string: str) -> str:
        return "".join(sorted(string, reverse=self.reverse, key=self.key))


class MapTransform(BaseTransformParser):
    def __init__(self, mapping: Mapping[str, X]):
        self.mapping = mapping

    def parse(self, string: str) -> X:
        return self.mapping[string]


class ReplaceTransform(BaseTransformParser):
    def __init__(self, mapping: Mapping[str, str]):
        self.mapping = mapping

    def parse(self, string: str) -> str:
        for key, value in self.mapping.items():
            string = string.replace(key, value)
        return string


class ChainParser(BaseTransformParser):
    def __init__(self, parsers: list[BaseAoCParser]):
        self.parsers = parsers

    @classmethod
    def _chain_parsers(cls, string: str, parsers: list[BaseAoCParser]):
        if not parsers:
            return string
        parsed_content = parsers[0].parse(string)
        return cls._chain_parsers(parsed_content, parsers[1:])

    def parse(self, string: str):
        return self._chain_parsers(string, self.parsers)


class BaseIterableParser(BaseAoCParser):
    def __init__(
        self,
        subparser: Union[BaseAoCParser, Callable] = None,
        splitter: Union[str, Sequence[str]] = None,
    ):
        self.splitter = splitter
        self.subparser = subparser or str

    @classmethod
    def _decide_splitter(cls, string: str, priority: list[str] = None) -> str:
        """
        Returns the splitter that is most likely to be used in the string.
        """
        priority = priority or cls.SPLITTER_PRIORITY
        for s in priority:
            if s in string.strip():
                return s
        return None

    @classmethod
    def _split(
        cls, string: str, splitter: Union[str, Sequence[str]], count: int = None
    ) -> Sequence[str]:
        if not splitter:
            return (c for c in string)
        if isinstance(splitter, str):
            return string.split(splitter, count) if count else string.split(splitter)
        else:
            for s in splitter:
                string = (
                    string.replace(s, "__split__", count)
                    if count
                    else string.replace(s, "__split__")
                )
            return cls._split(string, "__split__", count)

    @classmethod
    def _iterable_parse(
        cls,
        string: str,
        splitter: Union[str, Sequence[str]],
        subparser: Union[
            BaseAoCParser, Callable, Sequence[Union[BaseAoCParser, Callable]]
        ],
        count: int = None,
    ) -> Sequence:
        splitter = splitter or cls._decide_splitter(string)
        if isinstance(subparser, Iterable):
            count = len(subparser) - 1 if count is None else count
        sequence = cls._split(string, splitter, count)
        if isinstance(subparser, Iterable):
            assert len(subparser) == len(
                sequence
            ), "Length of subparsers provided and resulting sequence must match"
            return (p(s.strip()) for p, s in zip(subparser, sequence))
        return (subparser(s.strip()) for s in sequence if s.strip())

    @abstractmethod
    def parse(self, string: str) -> Sequence:
        pass


class ListParser(BaseIterableParser):
    def parse(self, string: str) -> list:
        return list(self._iterable_parse(string.strip(), self.splitter, self.subparser))


class SetParser(BaseIterableParser):
    def parse(self, string: str) -> set:
        return set(self._iterable_parse(string.strip(), self.splitter, self.subparser))


class IntListParser(BaseIterableParser):
    def __init__(self, base: int = 10):
        """Initializes a parser which parses a string into a list of integers.

        Args:
            base (int, optional): The base to use when parsing the integers. Defaults to 10.
        """
        self.base = base

    def parse(self, string: str) -> list[int]:
        return self._find_integers(string, self.base)


class TupleParser(BaseIterableParser):
    def __init__(
        self,
        subparser: Union[
            BaseAoCParser, Callable, Sequence[Union[BaseAoCParser, Callable]]
        ] = None,
        splitter: Union[str, Sequence[str]] = None,
        format: str = None,
        dataclass=None,
    ):
        assert (format is None) or (
            splitter is None
        ), "Cannot specify both splitter and parse format"
        self.subparser = subparser or str
        self.splitter = splitter
        self.format = format
        self.dataclass = dataclass

    def _format_parse(
        format: str,
        string: str,
        subparser: Union[
            BaseAoCParser, Callable, Sequence[Union[BaseAoCParser, Callable]]
        ],
    ) -> tuple:
        sequence = parse.parse(format, string)
        if isinstance(subparser, Iterable):
            assert len(subparser) == len(
                sequence
            ), "Length of subparsers provided and resulting sequence must match"
            return (p(s) for p, s in zip(sequence, subparser))
        return (subparser(e) for e in sequence)

    def parse(self, string: str) -> tuple:
        if self.format:
            sequence = self._format_parse(self.format, string, self.subparser)
        else:
            sequence = self._iterable_parse(
                string.strip(), self.splitter, self.subparser
            )
        if self.dataclass:
            return self.dataclass(*sequence)
        return tuple(sequence)


class DictParser(BaseIterableParser):
    def __init__(
        self,
        key_parser: Union[BaseAoCParser, Callable] = None,
        value_parser: Union[BaseAoCParser, Callable] = None,
        sequence_splitter: str = None,
        key_value_splitter: str = None,
    ):
        self.sequence_splitter = sequence_splitter
        self.key_value_splitter = key_value_splitter
        self.key_parser = key_parser or str
        self.value_parser = value_parser or str
        self.tuple_parser = TupleParser(
            self.key_value_splitter, [self.key_parser, self.value_parser]
        )

    def parse(self, string: str) -> dict:
        sequence = self._iterable_parse(string, self.sequence_splitter, str)
        return dict(self.tuple_parser.parse(s) for s in sequence)
