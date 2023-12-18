import math
import operator
import random
import time
from sys import stdin

from travelling_salesman import Problem, Solution


def random_construction(problem: Problem) -> Solution:
    solution = problem.empty_solution()
    components = list(solution.add_moves())

    while len(components) > 0:
        solution.add(random.choice(components))
        components = list(solution.add_moves())

    return solution


def greedy_construction(problem: Problem) -> Solution:
    solution = problem.empty_solution()
    components_iterator = solution.add_moves()

    component = next(components_iterator, None)

    while component is not None:
        best_component = component
        best_increment = solution.lower_bound_incr_add(component)

        best_increment = best_increment if best_increment is not None else math.inf

        for component in components_iterator:
            increment = solution.lower_bound_incr_add(component)

            increment = increment if increment is not None else math.inf

            if increment < best_increment:
                best_component = component
                best_increment = increment

        solution.add(best_component)
        components_iterator = solution.add_moves()
        component = next(components_iterator, None)  # type: ignore

    return solution


# random greedy construction -> will pick randomly if there is a tie
def greedy_construction_random_tie_break(problem) -> Solution:
    solution = problem.empty_solution()
    components_iterator = solution.add_moves()

    component = next(components_iterator, None)  # None if empty

    while component is not None:
        best_component = [component]
        best_increment = solution.lower_bound_incr_add(component)

        for component in components_iterator:
            increment = solution.lower_bound_incr_add(component)

            if increment < best_increment:
                best_component = [component]
                best_increment = increment

            # tie
            elif increment == best_increment:
                best_component.append(component)

        solution.add(random.choice(best_component))
        components_iterator = solution.add_moves()
        component = next(components_iterator, None)

    return solution


# random adaptive greedy construction -> will pick randomly among the components that are within a certain threshold
def greedy_randomized_adaptive_construction(problem, alpha=0) -> Solution:
    solution: Solution = problem.empty_solution()

    get_components = lambda: [
        (solution.lower_bound_incr_add(component), component)
        for component in solution.add_moves()
    ]
    components = get_components()

    while components:
        # get the component with the lowest lower bound
        min_component = min(components, key=operator.itemgetter(0))[0]

        # get the component with the biggest lower bound
        max_component = max(components, key=operator.itemgetter(0))[0]

        # calculate threshold
        threshold = min_component + alpha * (max_component - min_component)

        # components lower than the threshold
        restricted_components = [
            component for increment, component in components if increment <= threshold
        ]

        # pick random
        solution.add(random.choice(restricted_components))

        components = get_components()

    return solution


# grasp -> will run the greedy_randomized_adaptive_construction for a certain amount of time and return the best solution
def grasp(problem, budget, alpha=0) -> Solution:
    # budget is the amount of time it will be allowed to run
    start = time.perf_counter()

    best_solution = greedy_randomized_adaptive_construction(problem, alpha)
    best_objective = best_solution.objective()

    while time.perf_counter() - start < budget:  # while there is time left
        solution = greedy_randomized_adaptive_construction(problem, alpha)
        objective = solution.objective()

        if objective < best_objective:  # curr solution is better than best solution
            best_solution = solution
            best_objective = objective

    return best_solution


# TODO: Check this
def beam_search(problem, beam_width=10):
    solution = problem.empty_solution()

    best_solution, best_objective = (
        (solution, solution.objective()) if solution.is_feasible() else (None, None)
    )

    current = [(solution.lower_bound(), solution)]  # root node

    while True:
        children = []

        for lower_bound, solution in current:  # breadth-first search
            for component in solution.add_moves():
                children.append(
                    (
                        lower_bound + solution.lower_bound_incr_add(component),
                        solution,
                        component,
                    )
                )

        if children == []:
            return best_solution

        children.sort(key=operator.itemgetter(0))

        current = []

        for lower_bound, solution, ccomponent in children[:beam_width]:  # next level
            solution = solution.copy()

            solution.add(component)

            if solution.is_feasible():
                objective = solution.objective()

                if best_objective is None or objective < best_objective:
                    best_solution = solution

                    best_objective = objective

            current.append((lower_bound, solution))

    return best_solution


def local_search_first(solution: Solution) -> Solution:
    available_local_moves = solution.random_local_moves_wor()
    move = next(available_local_moves, None)

    while move is not None:
        increment = solution.objective_incr_local(move)

        if increment < 0:
            solution.step(move)
            available_local_moves = solution.random_local_moves_wor()

        move = next(available_local_moves, None)

    return solution


def local_search_best(solution: Solution) -> Solution:
    available_local_moves = solution.random_local_moves_wor()
    move = next(available_local_moves, None)

    while move is not None:
        best_move = move
        best_increment = solution.objective_incr_local(best_move)

        for move in available_local_moves:
            increment = solution.objective_incr_local(move)

            if increment < best_increment:
                best_move = move
                best_increment = increment

        if best_increment < 0:
            solution.step(best_move)
            available_local_moves = solution.random_local_moves_wor()

        move = next(available_local_moves, None)

    return solution


# def ACO(solution: Solution) -> Solution:
#     best_solution = solution.copy()
#
#     ITERATIONS: int = 50
#
#     for iteration in range(ITERATIONS):
#         cycles = list(solution.local_moves())
#
#         # elitism
#         cycles.append(LocalMove3Aco(solution.visited_cities, solution.objective()))
#
#         cycles.sort(key=lambda x: x.distance)
#
#         # select cycles for the step
#         cycles = cycles[: solution.ants_per_iteration // 2]
#
#         solution.step(cycles)
#
#         if solution.objective() < best_solution.objective():
#             best_solution = solution.copy()
#
#     return best_solution


if __name__ == "__main__":
    problem = Problem.from_textio(stdin)

    solution = random_construction(problem)
    print(solution.output())
