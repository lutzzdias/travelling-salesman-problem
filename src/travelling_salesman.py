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

import random
from collections.abc import Iterable
from typing import Any, List, Optional, Set, TextIO, Tuple, TypeVar

from helpers.sparse_fisher_yates import sparse_fisher_yates_iter

from construction.new_lb_constructor import NewLbConstructor
from local_solvers.atsp_3opt import Atsp3Opt
from local_solvers.atsp_aco import AtspAco

Objective = Any


class BaseSolution:
    def __init__(self, *args, **kwargs):
        self.problem: Problem = kwargs["problem"]
        self.visited_cities: List[int] = kwargs["visited_cities"]
        self.unvisited_cities: Set[int] = kwargs["unvisited_cities"]
        self.total_distance: int = kwargs["total_distance"]
        self.lower_bound_value: float = kwargs["lower_bound"]
        self.current_shortest_in: List[int] = [0 for _ in range(self.problem.dimension)]
        self.current_shortest_out: List[int] = [
            0 for _ in range(self.problem.dimension)
        ]

    def __str__(self):
        return f"distance: {self.total_distance}" f"path: {self.visited_cities}"

    def output(self) -> str:
        """
        Generate the output string for this solution
        """
        path: str = (
            "->".join(map(str, self.visited_cities))
            + f"->{str(self.visited_cities[0])}"
        )

        return f"The shortest path is: \n{path}\n with a total distance of {self.total_distance}."

    def is_feasible(self) -> bool:
        """
        Return whether the solution is feasible or not
        """
        return len(self.unvisited_cities) == 0

    def objective(self) -> Optional[Objective]:
        """
        Return the objective value for this solution if defined, otherwise
        should return None
        """
        if self.is_feasible():
            return self.total_distance
        else:
            return None

    def perturb(self, ks: int) -> None:
        """
        Perturb the solution in place. The amount of perturbation is
        controlled by the parameter ks (kick strength)
        """
        # TODO
        # Generate random aleatory moves (for ILS)
        raise NotImplementedError


class SolutionNewLb3Opt(BaseSolution, NewLbConstructor, Atsp3Opt):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def copy(self) -> SolutionNewLb3Opt:
        """
        Return a copy of this solution.

        Note: changes to the copy must not affect the original
        solution. However, this does not need to be a deepcopy.
        """
        return SolutionNewLb3Opt(
            problem=self.problem,
            visited_cities=self.visited_cities.copy(),
            unvisited_cities=self.unvisited_cities.copy(),
            total_distance=self.total_distance,
            lower_bound=self.lower_bound_value,
        )


class SolutionNewLbAco(BaseSolution, NewLbConstructor, AtspAco):
    def __init__(self, *args, **kwargs):
        self.pheromones: List[List[float]] = [
            [0.0] * kwargs["problem"].dimension
        ] * kwargs["problem"].dimension
        self.ants_per_iteration: int = 200
        self.degradation_factor = 0.9
        super().__init__(*args, **kwargs)

    def copy(self) -> SolutionNewLbAco:
        """
        Return a copy of this solution.

        Note: changes to the copy must not affect the original
        solution. However, this does not need to be a deepcopy.
        """
        return SolutionNewLbAco(
            problem=self.problem,
            visited_cities=self.visited_cities.copy(),
            unvisited_cities=self.unvisited_cities.copy(),
            total_distance=self.total_distance,
            lower_bound=self.lower_bound_value,
        )


class Problem:
    def __init__(self, dimension: int, distance_matrix: Tuple[Tuple[int, ...], ...]):
        # Number of cities
        self.dimension = dimension
        # Distance matrix where distance_matrix[i][j] is the distance between city i and city j
        self.distance_matrix = distance_matrix

        # list with ordered index of cities by distance
        self.shortest_out: List[List[int]] = []
        self.shortest_in: List[List[int]] = []

        # initial lower bound
        self.lower_bound: float = self._initialize_lower_bound()

    def __str__(self):
        string = f"dimension: {self.dimension}\ndistance matrix:\n"

        for line in range(self.dimension):
            for column in range(self.dimension):
                string += str(self.distance_matrix[line][column]) + " "
            string += "\n"

        return string

    def _initialize_lower_bound(self) -> float:
        """
        Initialize the lower bound for the problem
        """

        raw_lower_bound: int = 0

        for i in range(self.dimension):
            row = list(self.distance_matrix[i])
            sorted_row = sorted(enumerate(row), key=lambda x: x[1])
            self.shortest_out.append([index for index, _ in sorted_row])

            column = [row[i] for row in self.distance_matrix]
            sorted_column = sorted(enumerate(column), key=lambda x: x[1])
            self.shortest_in.append([index for index, _ in sorted_column])

            raw_lower_bound += (
                self.distance_matrix[i][self.shortest_out[i][0]]
                + self.distance_matrix[self.shortest_in[i][0]][i]
            )

        lower_bound = raw_lower_bound / 2

        return lower_bound

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

    def empty_solution(self, imp: int) -> Solution:
        """
        Create an empty solution (i.e. with no components).
        """

        match imp:
            case 1:
                return SolutionNewLb3Opt(
                    problem=self,
                    visited_cities=[0],
                    unvisited_cities=set(range(1, self.dimension)),
                    total_distance=0,
                    lower_bound=self.lower_bound,
                )
            case 2:
                return SolutionNewLbAco(
                    problem=self,
                    visited_cities=[0],
                    unvisited_cities=set(range(1, self.dimension)),
                    total_distance=0,
                    lower_bound=self.lower_bound,
                )
