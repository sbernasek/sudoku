from functools import reduce
from operator import add
from copy import deepcopy
import numpy as np
from time import time


class Sudoku:
    """
    Sudoku grid.

    Attributes:

        grid (np.ndarray[int]) - sudoku grid, may be incomplete

        depth (int) - recursion depth

        idxs (list of (int, int)) - indices of empty cells

        w (int) - grid width, e.g. 9 in a 2-D puzzle

        s (int) - subgrid width, e.g. 3 in a 2-D puzzle

        options (dict) - possible values for each empty cell

        runtime (float) - solver runtime

    """

    def __init__(self, grid, depth=0):
        """
        Initialize Sudoku grid.

        Args:

            grid (np.ndarray[int]) - sudoku grid, may be incomplete

            depth (int) - recursion depth

        """
        self.grid = np.asarray(grid, dtype=int)
        self.depth = depth
        self.idxs = list(zip(*(self.grid == 0).nonzero()))
        self.w = self.grid.shape[0]
        self.s = int(np.sqrt(self.w))
        self.options = {}
        self.update_options()
        self.runtime = None

    @property
    def ref(self):
        """ Range of reference values. """
        return set(range(1, self.w+1))

    @property
    def complete(self):
        """ Returns True if grid is complete. """
        return np.min(self.grid) > 0

    @staticmethod
    def _check(values):
        """ Check set of values for duplicates. """
        return (np.histogram(values, bins=np.arange(1, 11))[0] > 1).any()

    @property
    def valid(self):
        """ Returns True if grid meets all constraint criteria. """

        for row in self.grid:
            if self._check(row):
                return False
        for column in self.grid.T:
            if self._check(column):
                return False
        for block in np.split(self.grid, self.s):
            for grid in np.split(block, self.s, axis=1):
                if self._check(grid.ravel()):
                    return False

        for k, v in self.options.items():
            if len(v) == 0:
                return False

        return True

    @property
    def success(self):
        """ Returns True if puzzle is complete and valid. """
        return self.complete and self.valid

    def clone(self):
        """ Returns clone of grid. """
        child = self.__class__(deepcopy(self.grid), depth=self.depth+1)
        child.idxs = deepcopy(self.idxs)
        child.options = deepcopy(self.options)
        return child

    def _value(self, i, j):
        """ Returns value from grid position <i, j>. """
        return self.grid[i, j]

    def _complete(self, i, j):
        """ Returns true if value from grid position <i, j> is nonzero. """
        return self._value(i, j) != 0

    def _column(self, j):
        """ Returns column <j> """
        return self.grid[:, j]

    def column(self, j):
        """ Returns set of values appearing in column <j> """
        return set(self._column(j))

    def _row(self, i):
        """ Returns row <i> """
        return self.grid[i]

    def row(self, i):
        """ Returns set of values appearing in row <i> """
        return set(self._row(i))

    def _subgrid(self, i, j):
        """ Returns subgrid containing <i, j> """
        ii, jj = i//self.s, j//self.s
        return self.grid[ii*self.s:(ii+1)*self.s, jj*self.s:(jj+1)*self.s]

    def subgrid(self, *idx):
        """ Returns set of values appearing in the subgrid containing <i, j> """
        return set(self._subgrid(*idx).ravel())

    @property
    def num_missing(self):
        """ Returns number of missing values. """
        return (self.w**2) - self.grid.nonzero()[0].size

    def update_options(self):
        """ Mark all available values for each position. """
        for idx in self.idxs:
            self._update_options(*idx)

    def deduction(self):
        """ Mark all uniquely available values for each position """
        self.changed = False
        for idx in self.idxs:
            self.deduce(*idx)
        if self.changed:
            self.deduction()

    def _update_options(self, i, j):
        """ Induce all available values for <i, j> """

        row = self.compare_with_reference(self.row(i))
        column = self.compare_with_reference(self.column(j))
        grid = self.compare_with_reference(self.subgrid(i, j))
        options = set.intersection(row, column, grid)
        self.options[(i, j)] = options

        if len(options) == 1:
            self.set_value(i, j, options.pop())

    def deduce(self, i, j):
        """ Deduce values that can't go anywhere except <i, j> """

        options = self.options[(i, j)]

        row_idx = self.row_idxs(i, j)
        column_idx = self.column_idxs(i, j)
        grid_idx = self.grid_idxs(i, j)

        # determine unique options
        for idxs in (row_idx, column_idx, grid_idx):
            if len(idxs) > 0:
                values = set.union(*[self.options[idx] for idx in idxs])
                unique = options.difference(values)
            else:
                continue

            if len(unique) > 0:
                self.set_value(i, j, unique.pop())
                break

    def set_value(self, i, j, value):
        """ Set value of grid position <i, j> """
        self.grid[i, j] = value
        _ = self.idxs.remove((i, j))
        if (i, j) in self.options.keys():
            self.options.pop((i, j))
        self.changed = True
        self.update_options()

    def compare_with_reference(self, obj):
        """ Returns missing values in <obj> """
        return self.ref.difference(obj)

    def grid_idxs(self, i, j):
        """ Returns indices of all other cells in subgrid containing <i, j> """
        ii, jj = i//self.s, j//self.s
        idxs = [idx for idx in self.idxs if (idx[0]//self.s == ii and idx[1]//self.s == jj)]
        idxs.remove((i, j))
        return idxs

    def column_idxs(self, i, j):
        """ Returns indices of all other cells in column <j> """
        idxs = [idx for idx in self.idxs if idx[1] == j]
        idxs.remove((i, j))
        return idxs

    def row_idxs(self, i, j):
        """ Returns indices of all other cells in row <i> """
        idxs = [idx for idx in self.idxs if idx[0] == i]
        idxs.remove((i, j))
        return idxs

    def fork(self):
        """ Fork grid by making a random guess. """
        idx, options = sorted(self.options.items(), key=lambda x: len(x[1]))[0]
        for option in options:
            child = self.clone()
            child.set_value(*idx, option)
            solution = child.solve()
            if child.complete and child.valid:
                self.grid = solution
                break

    def solve(self):
        """ Run solver. """
        start = time()

        self.deduction()
        if not self.complete:
            self.fork()

        if self.depth == 0:
            self.runtime = time() - start
            assert self.valid and self.complete, 'Solution not found.'

        return self.grid

