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

from typing import TextIO, Optional, Any, Set, List, Tuple
from collections.abc import Iterable, Hashable
from copy import deepcopy
import random
import time

Objective = Any


def sparse_fisher_yates_iter(n):
    p: dict = {}

    for i in range(n - 1, -1, -1):
        r = random.randrange(i + 1)

        yield p.get(r, r)

        if i != r:
            p[r] = p.get(i, i)


class Component:
    def __init__(self, source: int, dest: int):
        self.arc = (source, dest)

    def __str__(self):
        return f"source: {self.arc[0]}" f"dest: {self.arc[1]}"

    @property
    def cid(self) -> Hashable:
        raise NotImplementedError


class LocalMove:
    def __init__(self, X1: int, X2: int, Y1: int, Y2: int, Z1: int, Z2: int):
        self.X1: int = X1
        self.X2: int = X2
        self.Y1: int = Y1
        self.Y2: int = Y2
        self.Z1: int = Z1
        self.Z2: int = Z2

    def __str__(self):
        return f"permutation {X2}->...->{Y1} <--> {Y2}->...->{Z1}"


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
        return deepcopy(self)

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
        return self.total_distance

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

    # https://tsp-basics.blogspot.com/2017/03/3-opt-iterative-general-idea.html
    def local_moves(self) -> Iterable[LocalMove]:
        """
        Return an iterable (generator, iterator, or iterable object)
        over all local moves that can be applied to the solution
        """
        dimension: int = self.problem.dimension

        for i in range(dimension - 5):
            X1 = self.visited_cities[i]
            X2 = self.visited_cities[i + 1]

            for j in range(i + 2, dimension - 3):
                Y1 = self.visited_cities[j]
                Y2 = self.visited_cities[j + 1]

                for k in range(j + 2, dimension - 1):
                    Z1 = self.visited_cities[k]
                    Z2 = self.visited_cities[k + 1]

                    local_move = LocalMove(X1, X2, Y1, Y2, Z1, Z2)

                    expected_gain = self.objective_incr_local(local_move)

                    if expected_gain > 0:
                        yield local_move

    def random_local_move(self) -> Optional[LocalMove]:
        """
        Return a random local move that can be applied to the solution.

        Note: repeated calls to this method may return the same
        local move.
        """
        dimension: int = self.problem.dimension

        tic = time.perf_counter_ns()

        # 10 ms
        while time.perf_counter_ns - tic < 10000000:
            X1_id = random.randint(0, dimension - 5)
            Y1_id = random.randint(X1_id + 2, dimension - 3)
            Z1_id = random.randint(Y1_id + 2, dimension - 1)

            X1 = visited_cities[X1_id]
            X2 = visited_cities[X1_id + 1]

            Y1 = visited_cities[Y1_id]
            Y2 = visited_cities[Y1_id + 1]

            Z1 = visited_cities[Z1_id]
            Z2 = visited_cities[Z1_id + 1]

            local_move = LocalMove(X1, X2, Y1, Y2, Z1, Z2)

            expected_gain = self.objective_incr_local(local_move)

            if expected_gain > 0:
                return local_move

        return None

    def random_local_moves_wor(self) -> Iterable[LocalMove]:
        """
        Return an iterable (generator, iterator, or iterable object)
        over all local moves (in random order) that can be applied to
        the solution.
        """

        local_moves = list(self.local_moves())

        random_indexes = sparse_fisher_yates_iter(len(local_moves))

        for i in random_indexes:
            yield local_moves[i]

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
        self.lower_bound_value += distance

    def step(self, lmove: LocalMove) -> None:
        """
        Apply a local move to the solution.

        Note: this invalidates any previously generated components and
        local moves.
        """

        borders: Tuple[int] = (
            lmove.X1,
            lmove.X2,
            lmove.Y1,
            lmove.Y2,
            lmove.Z1,
            lmove.Z2,
        )

        indexes = list(map(lambda x: self.visited_cities.index(x), borders))

        # abc -> acb
        updated_visited_cities = (
            self.visited_cities[: indexes[0] + 1]
            + self.visited_cities[indexes[3] : indexes[4] + 1]
            + self.visited_cities[indexes[1] : indexes[2] + 1]
            + self.visited_cities[indexes[5] :]
        )

        distance_difference = self.objective_incr_local(lmove)

        self.visited_cities = updated_visited_cities

        self.total_distance -= distance_difference
        self.lower_bound_value -= distance_difference

    def objective_incr_local(self, lmove: LocalMove) -> Optional[Objective]:
        """
        Return the objective value increment resulting from applying a
        local move. If the objective value is not defined after
        applying the local move return None.
        """
        distance_matrix = self.problem.distance_matrix

        add_distance: int = (
            distance_matrix[lmove.X1][lmove.Y2]
            + distance_matrix[lmove.Y1][lmove.Z2]
            + distance_matrix[lmove.Z1][lmove.X2]
        )

        del_distance: int = (
            distance_matrix[lmove.X1][lmove.X2]
            + distance_matrix[lmove.Y1][lmove.Y2]
            + distance_matrix[lmove.Z1][lmove.Z2]
        )

        return del_distance - add_distance

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

        return 0

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
