# Travelling Salesman Problem

**Contributors:**

- [Alexandre Andrade](https://github.com/AlexandreAndrade00)
- [Thiago Lütz Dias](https://github.com/lutzzdias)

The Traveling Salesman Problem (TSP) is a classic combinatorial optimization challenge in computer science. It revolves around determining the shortest possible route that visits a set of cities, returning to the starting point while adhering to the constraint that each city must be visited exactly once. In the realm of computational complexity, TSP is classified as an NP-hard problem, which means finding an optimal solution for large instances is a formidable task, often requiring exponential time.

In the traditional TSP, the distances between cities are symmetric, meaning the distance from city A to city B is the same as the distance from city B to city A. In contrast, the ATSP permits asymmetric distances, where the distance from city A to city B may differ from the distance in the opposite direction, from city B to city A. This asymmetry introduces an additional layer of complexity in solving the problem, making the ATSP more challenging and applicable in scenarios where one-way travel or varying transportation costs between cities are involved.

This repo will implement the ATSP following a predetermined API for relations with the outside world. It is the result of the final project from the Heuristic Methods subject in the University of Coimbra.

## Commit pattern

```
tag: what was done (in the imperative verb tense)
```

- feat: new feature
- fix: bug fix
- refactor: rewrite/restructure code but does not change behavior
- perf: performance specific commits
- style: formatting, missing semi colons, white space, formatting, etc
- test: adding missing tests, refactoring tests
- docs: changes to the documentation, TODOs and comments
- build: build components, eg. build tool, ci pipeline, dependencies, etc
- ops: operational components, eg. infrastructure, deployment, recovery, etc
- chore: miscellaneous commits, eg. modifying .gitignore, etc

**Example**

```
feat: implement from_textio within the problem class
```
