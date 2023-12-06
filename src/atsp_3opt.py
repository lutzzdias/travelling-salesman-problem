from collections.abc import Iterable, Hashable
from typing import TextIO, Optional, Any, Set, List, Tuple
import random

from helpers.sparse_fisher_yates import sparse_fisher_yates_iter
from interfaces.local_move import LocalMove
from interfaces.local_optimization import LocalOptimization

Objective = Any


class LocalMove3Opt(LocalMove):
    def __init__(self, X1: int, X2: int, Y1: int, Y2: int, Z1: int, Z2: int):
        self.X1: int = X1
        self.X2: int = X2
        self.Y1: int = Y1
        self.Y2: int = Y2
        self.Z1: int = Z1
        self.Z2: int = Z2

    def __str__(self):
        return f"permutation {X2}->...->{Y1} <--> {Y2}->...->{Z1}"


class Atsp3Opt(LocalOptimization):
    def local_moves(self) -> Iterable[LocalMove3Opt]:
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

                    local_move = LocalMove3Opt(X1, X2, Y1, Y2, Z1, Z2)

                    yield local_move

    def random_local_move(self) -> Optional[LocalMove3Opt]:
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

            local_move = LocalMove3Opt(X1, X2, Y1, Y2, Z1, Z2)

            return local_move

        return None

    def random_local_moves_wor(self) -> Iterable[LocalMove3Opt]:
        """
        Return an iterable (generator, iterator, or iterable object)
        over all local moves (in random order) that can be applied to
        the solution.
        """

        local_moves = list(self.local_moves())

        random_indexes = sparse_fisher_yates_iter(len(local_moves))

        for i in random_indexes:
            yield local_moves[i]

    def step(self, lmove: LocalMove3Opt) -> None:
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

    def objective_incr_local(self, lmove: LocalMove3Opt) -> Optional[Objective]:
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
