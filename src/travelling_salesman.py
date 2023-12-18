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

from collections.abc import Iterable
from typing import Any, List, Optional, Set, TextIO, Tuple

from helpers.sparse_fisher_yates import sparse_fisher_yates_iter

Objective = Any


class Component:
    def __init__(self, source: int, dest: int):
        self.arc = (source, dest)

    def __str__(self):
        return f"source: {self.arc[0]}" f"dest: {self.arc[1]}"


class LocalMove:
    def __init__(self, city_id: int, destination_index: int):
        self.city_id: int = city_id
        self.destination_index: int = destination_index

    def __str__(self):
        return f"city_id: {self.city_id}" f"destination_index: {self.destination_index}"


class Solution:
    def __init__(
        self,
        problem: Problem,
        visited_cities: List[int],
        unvisited_cities: Set[int],
        total_distance: int,
        lower_bound: float,
    ):
        self.problem: Problem = problem
        self.visited_cities: List[int] = visited_cities
        self.unvisited_cities: Set[int] = unvisited_cities
        self.total_distance: int = total_distance
        self.lower_bound_value: float = lower_bound
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

    def copy(self) -> Solution:
        """
        Return a copy of this solution.

        Note: changes to the copy must not affect the original
        solution. However, this does not need to be a deepcopy.
        """
        return Solution(
            self.problem,
            self.visited_cities.copy(),
            self.unvisited_cities.copy(),
            self.total_distance,
            self.lower_bound_value,
        )

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

    def _is_move_valid(self, city_index: int, dest: int) -> bool:
        """
        A move is valid if the destination is not the city itself,
        the previous city or the next city (redundant)
        """

        return (
            city_index != dest
            and (city_index - 1) % self.problem.dimension != dest
            and (city_index - 2) % self.problem.dimension != dest
        )

    def local_moves(self) -> Iterable[LocalMove]:
        """
        Return an iterable (generator, iterator, or iterable object)
        over all local moves that can be applied to the solution
        """
        for city_id in range(self.problem.dimension):
            for destination in range(self.problem.dimension):
                # returns all valid local moves
                if self._is_move_valid(city_id, destination):
                    yield LocalMove(city_id, destination)

    def random_local_move(self) -> Optional[LocalMove]:
        """
        Return a random local move that can be applied to the solution.

        Note: repeated calls to this method may return the same
        local move.
        """
        # TODO
        # Get random value (0 - n-1) - city_index
        # Get random value (1 - n-3) - dest
        # dest = (city_index + dest) % n
        raise NotImplementedError

    def random_local_moves_wor(self) -> Iterable[LocalMove]:
        """
        Return an iterable (generator, iterator, or iterable object)
        over all local moves (in random order) that can be applied to
        the solution.
        """
        local_moves = list(self.local_moves())
        for i in sparse_fisher_yates_iter(len(local_moves)):
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

        (
            self.lower_bound_value,
            self.current_shortest_in,
            self.current_shortest_out,
        ) = self._update_lower_bound(
            component.arc,
            self.lower_bound_value,
            self.current_shortest_in,
            self.current_shortest_out,
        )

        if len(self.unvisited_cities) == 0:
            self.total_distance += self.problem.distance_matrix[city_id][0]

    def _update_lower_bound(
        self,
        arc: Tuple[int, int],
        lb: float,  # lower bound
        csi: List[int],  # current shortest in
        cso: List[int],  # current shortest out
    ) -> Tuple[float, List[int], List[int]]:
        """ "
        Calculate lower bound after adding a component, does not change the solution,
        only the parameters passed in.
        """
        # Get shortest in of the added city
        si = self.problem.shortest_in[arc[1]][csi[arc[1]]]
        # Get shortest out of the previously last city
        so = self.problem.shortest_out[arc[0]][cso[arc[0]]]

        # Get distance of shortest in and out of respective cities
        sid = self.problem.distance_matrix[si][arc[1]]
        sod = self.problem.distance_matrix[arc[0]][so]

        # Remove previous idealistic values from lower bound
        lb -= (sid + sod) / 2

        # Get real distance
        d = self.problem.distance_matrix[arc[0]][arc[1]]

        # update lower bound with real distance
        lb += d

        # update shortest out for arc[1]
        # nso = next shortest out
        nso = self.problem.shortest_out[arc[1]][cso[arc[1]]]

        # it is the last city, shortest_out being 0 is correct
        if len(self.unvisited_cities) <= 1 and nso == 0:
            return lb, csi, cso

        # shortest out for arc[1] is invalid
        elif nso == arc[0] or nso == 0:
            # remove invalid value from lower bound
            lb -= self.problem.distance_matrix[arc[1]][nso] / 2

            # update current shortest out
            nso = self.problem.shortest_out[arc[1]][cso[arc[1]]]

            # while the new shortest out is invalid, move to the next
            while nso in self.visited_cities:
                cso[arc[1]] += 1
                nso = self.problem.shortest_out[arc[1]][cso[arc[1]]]

            # add new valid value to lower bound
            lb += self.problem.distance_matrix[arc[1]][nso] / 2

        # zero shortest in
        zsi = self.problem.shortest_in[0][csi[0]]

        # it is the last city, shortest_in for 0 being arc[1] is correct
        if len(self.unvisited_cities) == 0 and zsi == arc[1]:
            return lb, csi, cso

        # shortest in for 0 is invalid (arc[1])
        if self.problem.shortest_in[0][csi[0]] == arc[1]:
            # remove invalid value from lower bound
            lb -= self.problem.distance_matrix[zsi][0] / 2

            # update current shortest in for zero
            # nzsi = next zero shortest in
            nzsi = self.problem.shortest_in[0][csi[0]]

            # while the new shortest in is invalid, move to the next
            while nzsi in self.visited_cities:
                csi[0] += 1
                nzsi = self.problem.shortest_in[0][csi[0]]

            # add new valid value to lower bound
            lb += self.problem.distance_matrix[nzsi][0] / 2

        # for every city not visited yet
        for city in self.unvisited_cities:
            # * arc[0] was shortest in -> invalid
            # if current shortest in is arc[0] it is invalid
            if self.problem.shortest_in[city][csi[city]] == arc[0]:
                # get shortest in (invalid)
                # isi = invalid shortest in
                isi = self.problem.shortest_in[city][csi[city]]

                # subtract invalid shortest in from lower bound
                lb -= self.problem.distance_matrix[isi][city] / 2

                # update current shortest in
                csi[city] += 1

                # get new shortest in
                # nsi = new shortest in
                nsi = self.problem.shortest_in[city][csi[city]]

                # while the new shortest in is invalid, move to the next
                while nsi in self.visited_cities:
                    csi[city] += 1
                    nsi = self.problem.shortest_in[city][csi[city]]

                # add new valid value to lower bound
                lb += self.problem.distance_matrix[nsi][city] / 2

            # * arc[1] was shortest out -> invalid
            # if current shortest out is arc[1] it is invalid
            if self.problem.shortest_out[city][cso[city]] == arc[1]:
                # get shortest out (invalid)
                # iso = invalid shortest out
                iso = self.problem.shortest_out[city][cso[city]]

                # subtract invalid shortest out from lower bound
                lb -= self.problem.distance_matrix[city][iso] / 2

                # update current shortest out
                cso[city] += 1

                # get new shortest out
                # nso = new shortest out
                nso = self.problem.shortest_out[city][cso[city]]

                # while the new shortest out is invalid, move to the next
                # 0 is always valid
                while nso in self.visited_cities and nso != 0:
                    cso[city] += 1
                    nso = self.problem.shortest_out[city][cso[city]]

                # add new valid value to lower bound
                lb += self.problem.distance_matrix[city][nso] / 2

        return lb, csi, cso

    def step(self, lmove: LocalMove) -> None:
        """
        Apply a local move to the solution.

        Note: this invalidates any previously generated components and
        local moves.
        """
        # TODO
        # invalidate bound (NONE)
        # update total distance instead
        city_index = self.visited_cities.index(lmove.city_id)
        prev_city = self.visited_cities[city_index - 1]
        next_city = self.visited_cities[city_index + 1]

        dest_city = self.visited_cities[lmove.destination_index]
        prev_dest = self.visited_cities[lmove.destination_index - 1]

        # get distance between city and prev
        city_prev_dist = self.problem.distance_matrix[prev_city][city_index]
        # remove distance between city and prev
        self.lower_bound_value -= city_prev_dist / 2

        # get distance between city and next
        city_next_dist = self.problem.distance_matrix[city_index][next_city]
        # remove distance between city and next
        self.lower_bound_value -= city_next_dist / 2

        # get distance between prev and next
        post_dist = self.problem.distance_matrix[prev_city][next_city]
        # add distance between prev and next
        self.lower_bound_value += post_dist / 2

        # get distance between city before dest and city in dest
        dest_dist = self.problem.distance_matrix[prev_dest][dest_city]
        # remove distance between city before dest and city in dest
        self.lower_bound_value -= dest_dist / 2

        # get distance between city and dest
        dest_city_dist = self.problem.distance_matrix[city_index][dest_city]
        # add distance between city and dest
        self.lower_bound_value += dest_city_dist / 2

        # get distance between prev dest and city
        dest_prev_dist = self.problem.distance_matrix[prev_dest][city_index]
        # add distance between prev dest and city
        self.lower_bound_value += dest_prev_dist / 2

        # remove city from initial index
        removed_city = self.visited_cities.pop(city_index)
        # insert city in destination index
        self.visited_cities.insert(lmove.destination_index, removed_city)

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
        return self.problem.distance_matrix[component.arc[0]][component.arc[1]]

    def lower_bound_incr_add(self, component: Component) -> Optional[Objective]:
        """
        Return the lower bound increment resulting from adding a
        component. If the lower bound is not defined after adding the
        component, return None.
        """
        arc = component.arc
        lb = self.lower_bound_value
        csi = self.current_shortest_in.copy()
        cso = self.current_shortest_out.copy()

        result = self._update_lower_bound(
            arc,
            lb,
            csi,
            cso,
        )

        return result[0] - lb

    def perturb(self, ks: int) -> None:
        """
        Perturb the solution in place. The amount of perturbation is
        controlled by the parameter ks (kick strength)
        """
        # TODO
        # Generate random aleatory moves (for ILS)
        raise NotImplementedError

    def components(self) -> Iterable[Component]:
        """
        Returns an iterable to the components of a solution
        """
        for i in range(0, len(self.visited_cities) - 1):
            yield Component(self.visited_cities[i], self.visited_cities[i + 1])


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
