import random

from collections.abc import Iterable
from typing import Dict


def sparse_fisher_yates_iter(n: int) -> Iterable[int]:
    p: Dict[int, int] = {}

    for i in range(n - 1, -1, -1):
        r = random.randrange(i + 1)

        yield p.get(r, r)

        if i != r:
            p[r] = p.get(i, i)
