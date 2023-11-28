import math
import operator
import random
import time
from sys import stdin
from travelling_salesman import Problem, Solution


def greedy_construction(problem: Problem) -> Solution:
    solution = problem.empty_solution()

    components_iterator = solution.add_moves()

    current_component = next(components_iterator, None)  # type: ignore

    while current_component is not None:
        best_component = current_component

        best_increment = solution.lower_bound_incr_add(current_component)

        best_increment = best_increment if best_increment is not None else math.inf

        for component in components_iterator:
            increment = solution.lower_bound_incr_add(component)

            increment = increment if increment is not None else math.inf

            if increment < best_increment:
                best_component = component

                best_increment = increment

        solution.add(best_component)

        components_iterator = solution.add_moves()

        current_component = next(components_iterator, None)  # type: ignore

    return solution


# random greedy construction -> will pick randomly if there is a tie
def greedy_construction_random_tie_break(problem):
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
            elif incr == best_incr:
                best_component.append(component)

        solution.add(random.choice(best_component))

        components_iterator = solution.add_moves()

        component = next(components_iterator, None)

    return solution


# random adaptive greedy construction -> will pick randomly among the components that are within a certain threshold
def greedy_randomized_adaptive_construction(problem, alpha=0):
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

        # components lower then the threshold
        restricted_components = [
            component for increment, component in components if increment <= threshold
        ]

        # pick random
        solution.add(random.choice(restricted_components))

        components = get_components()

    return solution


# grasp -> will run the greedy_randomized_adaptive_construction for a certain amount of time and return the best solution
def grasp(problem, budget, alpha=0):
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


if __name__ == "__main__":
    problem = Problem.from_textio(stdin)

    solution1 = greedy_construction(problem)

    solution2 = greedy_randomized_adaptive_construction(problem, alpha=0.1)

    solution3 = grasp(problem, 10, alpha=0.1)

    print(solution1.lower_bound_value)
    print(solution2.lower_bound_value)
    print(solution3.lower_bound_value)
