from collections.abc import Iterable
from typing import Any, Optional

from .ilocal_move import ILocalMove

Objective = Any


class LocalOptimization:
    def local_moves(self) -> Iterable[ILocalMove]:
        """
        Return an iterable (generator, iterator, or iterable object)
        over all local moves that can be applied to the solution
        """
        pass

    def random_local_move(self) -> Optional[ILocalMove]:
        """
        Return a random local move that can be applied to the solution.

        Note: repeated calls to this method may return the same
        local move.
        """
        pass

    def random_local_moves_wor(self) -> Iterable[ILocalMove]:
        """
        Return an iterable (generator, iterator, or iterable object)
        over all local moves (in random order) that can be applied to
        the solution.
        """

        pass

    def step(self, lmove: ILocalMove) -> None:
        """
        Apply a local move to the solution.

        Note: this invalidates any previously generated components and
        local moves.
        """

        pass

    def objective_incr_local(self, lmove: ILocalMove) -> Optional[Objective]:
        """
        Return the objective value increment resulting from applying a
        local move. If the objective value is not defined after
        applying the local move return None.
        """
        pass
