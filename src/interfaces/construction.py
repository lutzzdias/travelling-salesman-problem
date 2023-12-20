from collections.abc import Iterable
from typing import Any, Optional

from interfaces.icomponent import IComponent

Objective = Any


class Construction:
    def add_moves(self) -> Iterable[IComponent]:
        """
        Return an iterable (generator, iterator, or iterable object)
        over all components that can be added to the solution
        """
        pass

    def heuristic_add_move(self) -> Optional[IComponent]:
        """
        Return the next component to be added based on some heuristic
        rule.
        """
        pass

    def add(self, component: IComponent) -> None:
        """
        Add a component to the solution.

        Note: this invalidates any previously generated components and
        local moves.
        """
        pass

    def objective_incr_add(self, component: IComponent) -> Optional[Objective]:
        """
        Return the objective value increment resulting from adding a
        component. If the objective value is not defined after adding the
        component, return None.
        """
        pass

    def lower_bound_incr_add(self, component: IComponent) -> Optional[Objective]:
        """
        Return the lower bound increment resulting from adding a
        component. If the lower bound is not defined after adding the
        component, return None.
        """
        pass

    def components(self) -> Iterable[IComponent]:
        """
        Returns an iterable to the components of a solution
        """
        pass
