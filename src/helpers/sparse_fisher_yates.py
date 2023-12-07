import random


def sparse_fisher_yates_iter(n):
    p: dict = {}

    for i in range(n - 1, -1, -1):
        r = random.randrange(i + 1)

        yield p.get(r, r)

        if i != r:
            p[r] = p.get(i, i)
