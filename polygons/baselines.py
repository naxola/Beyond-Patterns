"""Referencias: orden angular (techo en convexos), vecino más cercano y orden aleatorio."""
import numpy as np
from .generate import _canonical


def angular(points, rng=None):
    c = points.mean(0)
    order = np.argsort(np.arctan2(points[:, 1] - c[1], points[:, 0] - c[0]))
    return _canonical(points, order)


def nearest_neighbour(points, rng=None):
    """Empieza en el punto más a la izquierda y va siempre al más cercano sin visitar."""
    n = len(points)
    cur = int(min(range(n), key=lambda i: (points[i, 0], points[i, 1])))
    tour, left = [cur], set(range(n)) - {cur}
    while left:
        cur = min(left, key=lambda j: np.linalg.norm(points[j] - points[cur]))
        tour.append(cur); left.remove(cur)
    return np.array(tour)


def random_order(points, rng):
    return rng.permutation(len(points))


BASELINES = {"orden angular": angular, "vecino más cercano": nearest_neighbour, "orden aleatorio": random_order}
