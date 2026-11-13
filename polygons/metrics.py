"""Validez de polígonos: recorrido completo, sin cruces, y comparación de ciclos."""
import numpy as np


def _ccw(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def segments_cross(p1, p2, p3, p4):
    """Cruce propio entre los segmentos p1p2 y p3p4 (no cuenta tocar en un extremo)."""
    d1, d2 = _ccw(p3, p4, p1), _ccw(p3, p4, p2)
    d3, d4 = _ccw(p1, p2, p3), _ccw(p1, p2, p4)
    return (d1 * d2 < 0) and (d3 * d4 < 0)


def is_permutation(tour, n):
    return len(tour) == n and sorted(int(t) for t in tour) == list(range(n))


def is_simple(points, tour):
    """Ningún par de lados no adyacentes del polígono cerrado se cruza."""
    P = np.asarray(points, float)[list(tour)]
    n = len(P)
    for i in range(n):
        for j in range(i + 1, n):
            if j == i + 1 or (i == 0 and j == n - 1):
                continue
            if segments_cross(P[i], P[(i + 1) % n], P[j], P[(j + 1) % n]):
                return False
    return True


def is_valid_polygon(points, tour):
    return is_permutation(tour, len(points)) and is_simple(points, tour)


def is_convex(points, tour):
    P = np.asarray(points, float)[list(tour)]
    n = len(P)
    s = [_ccw(P[i], P[(i + 1) % n], P[(i + 2) % n]) for i in range(n)]
    return all(x > 0 for x in s) or all(x < 0 for x in s)


def same_cycle(a, b):
    """Mismo recorrido cerrado, sin importar el punto de inicio ni el sentido."""
    a, b = [int(x) for x in a], [int(x) for x in b]
    if len(a) != len(b) or sorted(a) != sorted(b):
        return False
    n = len(a)
    i = b.index(a[0])
    fwd = [b[(i + j) % n] for j in range(n)]
    bwd = [b[(i - j) % n] for j in range(n)]
    return a == fwd or a == bwd
