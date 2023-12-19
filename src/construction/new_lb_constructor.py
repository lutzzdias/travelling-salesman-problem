from collections.abc import Iterable
from typing import List, Optional, Tuple
from interfaces.component import Component

from interfaces.construction import Construction

Objective = int | float


class NewLbComponent(Component):
    def __init__(self, source: int, dest: int):
        self.arc = (source, dest)

    def __str__(self):
        return f"source: {self.arc[0]}" f"dest: {self.arc[1]}"


class NewLbConstructor(Construction):
    def components(self) -> Iterable[Component]:
        """
        Returns an iterable to the components of a solution
        """
        for i in range(0, len(self.visited_cities) - 1):
            yield NewLbComponent(self.visited_cities[i], self.visited_cities[i + 1])

    def lower_bound(self) -> Optional[Objective]:
        """
        Return the lower bound value for this solution if defined,
        otherwise return None
        """
        return self.lower_bound_value

    def add_moves(self) -> Iterable[NewLbComponent]:
        """
        Return an iterable (generator, iterator, or iterable object)
        over all components that can be added to the solution
        """

        for city in self.unvisited_cities:
            yield NewLbComponent(self.visited_cities[-1], city)

    def heuristic_add_move(self) -> Optional[NewLbComponent]:
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
        if len(self.unvisited_cities) < 1:
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

    def objective_incr_add(self, component: NewLbComponent) -> Optional[Objective]:
        """
        Return the objective value increment resulting from adding a
        component. If the objective value is not defined after adding the
        component, return None.
        """
        return self.problem.distance_matrix[component.arc[0]][component.arc[1]]

    def lower_bound_incr_add(self, component: NewLbComponent) -> Optional[Objective]:
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

        return result[0] - self.lower_bound_value
