import random
from typing import Iterable, Optional

from helpers.sparse_fisher_yates import sparse_fisher_yates_iter
from interfaces.ilocal_move import ILocalMove
from interfaces.local_optimization import LocalOptimization

Objective = int


class LocalMoveShiftInsert(ILocalMove):
    def __init__(self, city_index: int, destination_index: int):
        self.city_index: int = city_index
        self.destination_index: int = destination_index

    def __str__(self):
        return (
            f"city_index: {self.city_index}"
            f"destination_index: {self.destination_index}"
        )


class AtspShiftInsert(LocalOptimization):
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

    def local_moves(self) -> Iterable[ILocalMove]:
        """
        Return an iterable (generator, iterator, or iterable object)
        over all local moves that can be applied to the solution
        """

        for city_id in range(self.problem.dimension):
            for destination in range(self.problem.dimension):
                # returns all valid local moves
                if self._is_move_valid(city_id, destination):
                    yield LocalMoveShiftInsert(city_id, destination)

    def random_local_move(self) -> Optional[ILocalMove]:
        """
        Return a random local move that can be applied to the solution.

        Note: repeated calls to this method may return the same
        local move.
        """
        city_index = random.randint(0, self.problem.dimension - 1)

        dest = random.randint(0, self.problem.dimension - 1)
        final_dest = (city_index + dest) % self.problem.dimension

        local_move = LocalMoveShiftInsert(city_index, final_dest)

        while not self._is_move_valid(city_index, final_dest):
            dest = random.randint(0, self.problem.dimension - 1)
            final_dest = (city_index + dest) % self.problem.dimension

            local_move = LocalMoveShiftInsert(city_index, final_dest)

        return local_move

    def random_local_moves_wor(self) -> Iterable[ILocalMove]:
        """
        Return an iterable (generator, iterator, or iterable object)
        over all local moves (in random order) that can be applied to
        the solution.
        """
        local_moves = list(self.local_moves())
        for i in sparse_fisher_yates_iter(len(local_moves)):
            yield local_moves[i]

    def step(self, lmove: ILocalMove) -> None:
        """
        Apply a local move to the solution.

        Note: this invalidates any previously generated components and
        local moves.
        """
        # invalidate lower bound
        self.lower_bound_value = -1

        city = self.visited_cities[lmove.city_index]
        prev_city = self.visited_cities[(lmove.city_index - 1) % self.problem.dimension]
        next_city = self.visited_cities[(lmove.city_index + 1) % self.problem.dimension]

        dest = self.visited_cities[lmove.destination_index]
        prev_dest = self.visited_cities[lmove.destination_index - 1]

        self.total_distance = self._calculate_local_move_distance(
            city, prev_city, next_city, dest, prev_dest, self.total_distance
        )

        # remove city from initial index
        self.visited_cities.pop(lmove.city_index)

        # insert city in destination index
        self.visited_cities.insert(lmove.destination_index, city)

    def _calculate_local_move_distance(
        self,
        city: int,
        prev_city: int,
        next_city: int,
        dest: int,
        prev_dest: int,
        total_distance: int,
    ) -> int:
        """
        Calculate the distance of a local move and update the passed in total_distance
        """
        # get distance between city and prev
        city_prev_dist = self.problem.distance_matrix[prev_city][city]
        # remove distance between city and prev
        total_distance -= city_prev_dist

        # get distance between city and next
        city_next_dist = self.problem.distance_matrix[city][next_city]
        # remove distance between city and next
        total_distance -= city_next_dist

        # get distance between prev and next
        post_dist = self.problem.distance_matrix[prev_city][next_city]
        # add distance between prev and next
        total_distance += post_dist

        # get distance between city before dest and city in dest
        dest_dist = self.problem.distance_matrix[prev_dest][dest]
        # remove distance between city before dest and city in dest
        total_distance -= dest_dist

        # get distance between city and dest
        dest_city_dist = self.problem.distance_matrix[city][dest]
        # add distance between city and dest
        total_distance += dest_city_dist

        # get distance between prev dest and city
        dest_prev_dist = self.problem.distance_matrix[prev_dest][city]
        # add distance between prev dest and city
        total_distance += dest_prev_dist

        return total_distance

    def objective_incr_local(self, lmove: ILocalMove) -> Optional[Objective]:
        """
        Return the objective value increment resulting from applying a
        local move. If the objective value is not defined after
        applying the local move return None.
        """
        city = self.visited_cities[lmove.city_index]
        prev_city = self.visited_cities[(lmove.city_index - 1) % self.problem.dimension]
        next_city = self.visited_cities[(lmove.city_index + 1) % self.problem.dimension]

        dest = self.visited_cities[lmove.destination_index]
        prev_dest = self.visited_cities[
            (lmove.destination_index - 1) % self.problem.dimension
        ]

        total_distance = self.total_distance

        result = self._calculate_local_move_distance(
            city, prev_city, next_city, dest, prev_dest, total_distance
        )

        return self.total_distance - result
