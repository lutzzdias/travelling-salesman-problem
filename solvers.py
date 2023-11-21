import math
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


if __name__ == "__main__":
    problem = Problem.from_textio(stdin)

    solution = greedy_construction(problem)

    print(solution.lower_bound_value)
