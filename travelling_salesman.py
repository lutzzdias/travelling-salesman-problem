#!/usr/bin/env python3
#
# Copyright (C) 2023 Alexandre Jesus <https://adbjesus.com>, Carlos M. Fonseca <cmfonsec@dei.uc.pt>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations

from sys import stdin
from typing import TextIO, Optional, Any, Set, List, Tuple
from collections.abc import Iterable, Hashable

Objective = Any


class Component:
    def __init__(self, source: int, dest: int):
        self.arc = (source, dest)

    def __str__(self):
        return f"source: {self.arc[0]}" f"dest: {self.arc[1]}"

    @property
    def cid(self) -> Hashable:
        raise NotImplementedError


class LocalMove:
    ...


class Solution:
    def __init__(
        self,
        problem: Problem,
        visited_cities: List[int],
        unvisited_cities: Set[int],
        total_distance: int,
        lower_bound: int,
    ):
        self.problem: Problem = problem
        self.visited_cities: List[int] = visited_cities
        self.unvisited_cities: Set[int] = unvisited_cities
        self.total_distance: int = total_distance
        self.lower_bound_value: int = lower_bound

    def __str__(self):
        return f"distance: {self.total_distance}\npath: {self.visited_cities}\n"

    def output(self) -> str:
        """
        Generate the output string for this solution
        """
        raise NotImplementedError

    def copy(self) -> Solution:
        """
        Return a copy of this solution.

        Note: changes to the copy must not affect the original
        solution. However, this does not need to be a deepcopy.
        """
        raise NotImplementedError

    def is_feasible(self) -> bool:
        """
        Return whether the solution is feasible or not
        """
        raise NotImplementedError

    def objective(self) -> Optional[Objective]:
        """
        Return the objective value for this solution if defined, otherwise
        should return None
        """
        raise NotImplementedError

    def lower_bound(self) -> Optional[Objective]:
        """
        Return the lower bound value for this solution if defined,
        otherwise return None
        """
        return self.lower_bound_value

    def add_moves(self) -> Iterable[Component]:
        """
        Return an iterable (generator, iterator, or iterable object)
        over all components that can be added to the solution
        """

        for city in self.unvisited_cities:
            yield Component(self.visited_cities[-1], city)

    def local_moves(self) -> Iterable[LocalMove]:
        """
        Return an iterable (generator, iterator, or iterable object)
        over all local moves that can be applied to the solution
        """
        raise NotImplementedError

    def random_local_move(self) -> Optional[LocalMove]:
        """
        Return a random local move that can be applied to the solution.

        Note: repeated calls to this method may return the same
        local move.
        """
        raise NotImplementedError

    def random_local_moves_wor(self) -> Iterable[LocalMove]:
        """
        Return an iterable (generator, iterator, or iterable object)
        over all local moves (in random order) that can be applied to
        the solution.
        """
        raise NotImplementedError

    def heuristic_add_move(self) -> Optional[Component]:
        """
        Return the next component to be added based on some heuristic
        rule.
        """
        raise NotImplementedError

    def add(self, component: Component) -> None:
        """
        Add a component to the solution.

        Note: this invalidates any previously generated components and
        local moves.
        """

        city_id: int = component.arc[1]

        self.visited_cities.append(city_id)

        self.unvisited_cities.remove(city_id)

        distance: int = self.problem.distance_matrix[component.arc[0]][city_id]

        self.total_distance += distance

        self.lower_bound_value = (
            self.lower_bound_value
            - self.problem.lower_bound // self.problem.dimension
            + distance
        )

    def step(self, lmove: LocalMove) -> None:
        """
        Apply a local move to the solution.

        Note: this invalidates any previously generated components and
        local moves.
        """
        raise NotImplementedError

    def objective_incr_local(self, lmove: LocalMove) -> Optional[Objective]:
        """
        Return the objective value increment resulting from applying a
        local move. If the objective value is not defined after
        applying the local move return None.
        """
        raise NotImplementedError

    def objective_incr_add(self, component: Component) -> Optional[Objective]:
        """
        Return the objective value increment resulting from adding a
        component. If the objective value is not defined after adding the
        component, return None.
        """
        raise NotImplementedError

    def lower_bound_incr_add(self, component: Component) -> Optional[Objective]:
        """
        Return the lower bound increment resulting from adding a
        component. If the lower bound is not defined after adding the
        component, return None.
        """
        return self.problem.distance_matrix[component.arc[0]][component.arc[1]]

    def perturb(self, ks: int) -> None:
        """
        Perturb the solution in place. The amount of perturbation is
        controlled by the parameter ks (kick strength)
        """
        raise NotImplementedError

    def components(self) -> Iterable[Component]:
        """
        Returns an iterable to the components of a solution
        """
        raise NotImplementedError


class Problem:
    def __init__(self, dimension: int, distance_matrix: Tuple[Tuple[int, ...], ...]):
        self.dimension = dimension  # Number of cities
        # Distance matrix where distance_matrix[i][j] is the distance between city i and city j
        self.distance_matrix = distance_matrix

        self.lower_bound: int = self._initialize_lower_bound()

    def _initialize_lower_bound(self) -> int:
        """
        Initialize the lower bound for the problem
        """
        # find the smallest possible distance between two cities and multiply it
        # by the number of cities

        # get the min of every row, get the min of the minimums and multiply by the number of cities
        return min(min(row) for row in self.distance_matrix) * self.dimension

    def __str__(self):
        string = f"dimension: {self.dimension}\ndistance matrix:\n"

        for line in range(self.dimension):
            for column in range(self.dimension):
                string += str(self.distance_matrix[line][column]) + " "
            string += "\n"

        return string

    @classmethod
    def from_textio(cls, f: TextIO) -> Problem:
        """
        Create a problem from a text I/O source `f`
        """

        dimension: int = 0

        file_data = [str(i) for i in f.read().split()]
        file_iterator = iter(file_data)

        for data in file_iterator:
            if data == "DIMENSION:":
                dimension = int(next(file_iterator))
            if data == "EDGE_WEIGHT_SECTION":
                break

        # creates a tuple matrix with dimension x dimension
        distance_matrix = tuple(
            tuple(int(next(file_iterator)) for _ in range(dimension))
            for __ in range(dimension)
        )

        return cls(dimension, distance_matrix)

    def empty_solution(self) -> Solution:
        """
        Create an empty solution (i.e. with no components).
        """
        return Solution(
            problem=self,
            visited_cities=[0],
            unvisited_cities=set(range(1, self.dimension)),
            total_distance=0,
            lower_bound=self.lower_bound,
        )


if __name__ == "__main__":
    problem = Problem.from_textio(stdin)
    # print(problem)

    solution = problem.empty_solution()
    # print(solution)

    print(solution.lower_bound_value)
