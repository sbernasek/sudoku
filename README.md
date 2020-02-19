# Sudoku solver

I spent the first half of a very long flight failing to make any progress on a sudoku puzzle. I spent the second half writing this library so I could feel better about myself. It solves sudoku puzzles using a blend of heuristic decisions and, when all else fails, brute force. This implementation should be readily extendable to puzzles of arbitrary dimensionality, but my passport expired so I don't anticipate needing to bide my time with 6-D puzzles any time soon.

Dependencies
============

 - Python 3.6+
 - [NumPy](https://numpy.org)


Usage
=====

Puzzles are represented as integer-valued NumPy arrays. Values of zero denote blank cells. For example:

```

puzzle = [
    [0, 6, 8, 0, 0, 4, 0, 0, 0],
    [0, 0, 0, 5, 1, 9, 8, 6, 7],
    [1, 0, 0, 0, 8, 6, 0, 0, 0],
    [0, 0, 0, 0, 9, 0, 6, 0, 2],
    [0, 0, 0, 0, 3, 1, 7, 0, 0],
    [0, 0, 9, 4, 0, 0, 3, 0, 0],
    [4, 0, 3, 0, 0, 0, 0, 0, 0],
    [8, 5, 1, 9, 4, 3, 2, 7, 6],
    [0, 0, 0, 1, 0, 8, 4, 3, 5]]

```

Then simply use the ```Sudoku.solve``` method:


```

from sudoku import Sudoku

solution = Sudoku(puzzle).solve()

```
