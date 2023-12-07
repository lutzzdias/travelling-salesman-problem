from collections.abc import Iterable, Hashable
from typing import TextIO, Optional, Any, Set, List, Tuple
import random
import multiprocessing

from interfaces.local_move import LocalMove
from interfaces.local_optimization import LocalOptimization


Objective = Any


class LocalMove3Aco(LocalMove):
    def __init__(self, path: List[int], distance: int):
        self.path: List[int] = path
        self.distance: int = distance

    def __str__(self):
        return f"distance: {self.distance}\npath: {self.path}\n"


class Atsp3Aco(LocalOptimization):
    def __init__(self, ants_per_iteration=200, degradation_factor=0.9):
        self.pheromones: List[List[float]] = [
            [0.0] * self.problem.dimension
        ] * self.problem.dimension
        self.ants_per_iteration: int = ants_per_iteration
        self.degradation_factor = degradation_factor

    def _local_move(self, _):
        ALPHA: int = 0.9
        BETA: int = 1.5

        dimension: int = self.problem.dimension

        first_city: int = random.randint(0, dimension - 1)

        # originally no nodes have been visited
        visited = [0] * dimension

        # except the initial/source node.
        visited[first_city] = 1

        cycle = [first_city]
        steps = 0
        current = first_city
        total_length = 0

        while steps < dimension - 1:
            jumps_neighbors = []
            jumps_values = []

            for node in range(dimension):
                if visited[node] != 1:
                    # constant added to encourage exploration
                    pheromone_level = max(self.pheromones[current][node], 1e-5)

                    v = (pheromone_level**ALPHA) / (
                        self.problem.distance_matrix[current][node] ** BETA
                        if self.problem.distance_matrix[current][node] != 0
                        else 1
                    )

                    jumps_neighbors.append(node)
                    jumps_values.append(v)

            # weighted (normalized) choice
            next_node = random.choices(jumps_neighbors, weights=jumps_values)[0]

            total_length += self.problem.distance_matrix[current][next_node]

            visited[next_node] = 1
            current = next_node
            cycle.append(current)

            steps += 1

        total_length += self.problem.distance_matrix[current][cycle[0]]

        return LocalMove3Aco(cycle, total_length)

    def local_moves(self) -> Iterable[LocalMove3Aco]:
        """
        Return an iterable (generator, iterator, or iterable object)
        over all local moves that can be applied to the solution
        """

        with multiprocessing.Pool() as pool:
            return list(pool.map(self._local_move, range(self.ants_per_iteration)))

    def step(self, lmoves: List[LocalMove3Aco]) -> None:
        """
        Apply a local move to the solution.

        Note: this invalidates any previously generated components and
        local moves.
        """

        self.visited_cities = lmoves[0].path

        self.total_distance = lmoves[0].distance
        self.lower_bound_value = lmoves[0].distance

        Q: int = 10

        dimension: int = self.problem.dimension

        # pheromone update
        for lmove in lmoves:
            delta = 10 / lmove.distance

            for i in range(dimension - 1):
                self.pheromones[lmove.path[i]][lmove.path[i + 1]] += delta

            self.pheromones[lmove.path[dimension - 1]][lmove.path[0]] += delta
            self.pheromones = [
                [
                    self.pheromones[i][j] * self.degradation_factor
                    for j in range(dimension)
                ]
                for i in range(dimension)
            ]

    def objective_incr_local(self, lmove: LocalMove3Aco) -> Optional[Objective]:
        """
        Return the objective value increment resulting from applying a
        local move. If the objective value is not defined after
        applying the local move return None.
        """

        return self.objective - lmove.distance
