from collections.abc import Iterable
from typing import List, Optional, Tuple

from interfaces.construction import Construction
from interfaces.icomponent import IComponent

Objective = int | float


class Component(IComponent):
    def __init__(self, source: int, dest: int):
        self.arc = (source, dest)

    def __str__(self):
        return f"source: {self.arc[0]} - dest: {self.arc[1]}"


class SimpleLb(Construction):
    def components(self) -> Iterable[IComponent]:
        """
        Returns an iterable to the components of a solution
        """
        for i in range(0, len(self.visited_cities) - 1):
            yield Component(self.visited_cities[i], self.visited_cities[i + 1])

    def lower_bound(self) -> Optional[Objective]:
        """
        Return the lower bound value for this solution if defined,
        otherwise return None
        """
        return self.lower_bound_value

    def add_moves(self) -> Iterable[IComponent]:
        """
        Return an iterable (generator, iterator, or iterable object)
        over all components that can be added to the solution
        """

        for city in self.unvisited_cities:
            yield Component(self.visited_cities[-1], city)

    def heuristic_add_move(self) -> Optional[IComponent]:
        """
        Return the next component to be added based on some heuristic
        rule.
        """
        raise NotImplementedError

    def add(self, component: IComponent) -> None:
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

        if len(self.unvisited_cities) == 0:
            self.total_distance += self.problem.distance_matrix[city_id][0]
            self.lower_bound_value += self.problem.distance_matrix[city_id][0]

    def objective_incr_add(self, component: IComponent) -> Optional[Objective]:
        """
        Return the objective value increment resulting from adding a
        component. If the objective value is not defined after adding the
        component, return None.
        """
        return self.problem.distance_matrix[component.arc[0]][component.arc[1]]

    def lower_bound_incr_add(self, component: IComponent) -> Optional[Objective]:
        """
        Return the lower bound increment resulting from adding a
        component. If the lower bound is not defined after adding the
        component, return None.
        """
        return self.problem.distance_matrix[component.arc[0]][component.arc[1]]
