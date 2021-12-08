# Advent of Code Parsers

[![pyversions](https://img.shields.io/pypi/pyversions/aocp)](https://www.python.org/)


A collection of convenient Python parsers for Advent of Code problems.


## Installation

```bash
pip install aocp
```

## Quickstart

You can import parsers from the base module. There are two main types of parsers:
 * Iterable parsers, which return a sequence of elements from parsing a `str`, such as `list`, `tuple` or `dict`
 * Transform parsers, which return a single object from parsing a `str`, such as an `int`, `bool` or another `str`

Iterable parsers can be composed with other parsers nested within, including Transform parsers and other Iterable parsers. They can also be nested with some base types such as `int`.

Transform parsers cannot have nested parsers, but they can be composed with other parsers in a sequence using `ChainParser`.

This way, the structure of the output data mirrors that of the expression used to instantiate the parser transform.

Here is a basic usage example:

```python
raw_data = "46,79,77,45,57,34,44,13,32,88,86,82,91,97"
parser = ListParser(IntParser)
parser.parse(raw_data)
```

Which results in:
```
[46, 79, 77, 45, 57, 34, 44, 13, 32, 88, 86, 82, 91, 97]
```

And here is a more advanced example, from [AoC 2021 day 4](https://adventofcode.com/2021/day/4):
```python
raw_data = """7,4,9,5,11,17,23,2,0,14,21,24,10,16,13,6,15,25,12,22,18,20,8,19,3,26,1

22 13 17 11  0
 8  2 23  4 24
21  9 14 16  7
 6 10  3 18  5
 1 12 20 15 19

 3 15  0  2 22
 9 18 13 17  5
19  8  7 25 23
20 11 10 24  4
14 21 16 12  6

14 21 17 24  4
10 16 15  9 19
18  8 23 26 20
22 11 13  6  5
 2  0 12  3  7"""
parser = TupleParser(
    (
        IntListParser(),
        ListParser(ListParser(IntListParser())),
    )
)
parser.parse(raw_data)
```

Which results in:
```
(
    [7, 4, 9, 5, 11, 17, 23, 2, 0, 14, 21, 24, 10, 16, 13, 6, 15, 25, 12, 22, 18, 20, 8, 19, 3, 26, 1], 
    [[[22, 13, 17, 11, 0],
     [8, 2, 23, 4, 24],
     [21, 9, 14, 16, 7],
     [6, 10, 3, 18, 5],
     [1, 12, 20, 15, 19]],
    [[3, 15, 0, 2, 22],
     [9, 18, 13, 17, 5],
     [19, 8, 7, 25, 23],
     [20, 11, 10, 24, 4],
     [14, 21, 16, 12, 6]],
    [[14, 21, 17, 24, 4],
     [10, 16, 15, 9, 19],
     [18, 8, 23, 26, 20],
     [22, 11, 13, 6, 5],
     [2, 0, 12, 3, 7]]]
)
```

By default, the splitting elements in an iterable are guessed from the string provided. However, you can provide them through the `splitter` argument. This can be a strings or a sequence of strings, which will all act as splitters.

A notebook with more examples from Aoc 2021 is available [here](./examples/aoc-2021.ipynb).

## To be done
 * Full testing coverage
 * Documentation page (full docstrings are available, though)
 * More examples from other previous years
 * Regex Parser
 * Defaults in tuple parser in case of missing components in origin string
## Source code

[https://github.com/miguel-bm/advent-of-code-parsers](https://github.com/miguel-bm/advent-of-code-parsers)