from __future__ import annotations

from dataclasses import dataclass
from math import hypot
from random import Random
from typing import List, Sequence


@dataclass
class Location:
    id: int
    x: float
    y: float


@dataclass
class Route:
    order: List[int]
    total_distance: float


def _distance(a: Location, b: Location) -> float:
    return hypot(a.x - b.x, a.y - b.y)


def _route_length(route: Sequence[int], locations: Sequence[Location]) -> float:
    if not route:
        return 0.0
    dist = 0.0
    for i in range(len(route) - 1):
        dist += _distance(locations[route[i]], locations[route[i + 1]])
    return dist


def _greedy_randomized_construction(
    locations: Sequence[Location],
    alpha: float,
    rnd: Random,
) -> List[int]:
    """Build a route using a GRASP-style greedy randomized construction."""
    remaining = list(range(len(locations)))
    route: List[int] = [remaining.pop(0)]  # start from depot (index 0)

    while remaining:
        last = route[-1]
        costs = [
            (idx, _distance(locations[last], locations[idx])) for idx in remaining
        ]
        costs.sort(key=lambda x: x[1])

        min_cost = costs[0][1]
        max_cost = costs[-1][1]
        threshold = min_cost + alpha * (max_cost - min_cost)
        rcl = [idx for idx, cost in costs if cost <= threshold]

        chosen = rnd.choice(rcl)
        route.append(chosen)
        remaining.remove(chosen)

    return route


def _two_opt(route: List[int], locations: Sequence[Location]) -> List[int]:
    """Simple 2-opt local search (VND neighbourhood)."""
    improved = True
    best_route = route
    best_length = _route_length(best_route, locations)

    while improved:
        improved = False
        for i in range(1, len(best_route) - 2):
            for j in range(i + 1, len(best_route)):
                if j - i == 1:
                    continue
                new_route = best_route[:]
                new_route[i:j] = reversed(new_route[i:j])
                new_length = _route_length(new_route, locations)
                if new_length < best_length:
                    best_length = new_length
                    best_route = new_route
                    improved = True
                    break
            if improved:
                break

    return best_route


def compute_route(
    locations: Sequence[Location],
    iterations: int = 50,
    alpha: float = 0.3,
    seed: int | None = None,
) -> Route:
    """
    Compute a near-optimal single-vehicle route using GRASP + VND (2-opt).

    Args:
        locations: List of locations; index 0 is treated as the depot.
        iterations: GRASP iterations.
        alpha: Greediness/randomness parameter (0 = greedy, 1 = random).
    """
    if len(locations) <= 1:
        return Route(order=list(range(len(locations))), total_distance=0.0)

    rnd = Random(seed)
    best_route: List[int] | None = None
    best_length = float("inf")

    for _ in range(iterations):
        initial = _greedy_randomized_construction(locations, alpha, rnd)
        improved = _two_opt(initial, locations)
        length = _route_length(improved, locations)
        if length < best_length:
            best_length = length
            best_route = improved

    assert best_route is not None
    return Route(order=best_route, total_distance=best_length)

