"""Solucionador exacto de clase 1: giros solo sobre puntos dados."""
import numpy as np
from .geometry import EPS, point_segment_distance


def _cover_masks(points, eps):
    n = len(points)
    m = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            mask = 0
            for q in range(n):
                if point_segment_distance(points[q], points[i], points[j]) <= eps:
                    mask |= 1 << q
            m[i][j] = mask
    return m


def min_class1(points, kmax, eps=EPS):
    """Devuelve (k, índices de vértices) con el mínimo k ≤ kmax girando solo en puntos,
    o None si no existe. Los extremos también son puntos dados (forma canónica)."""
    n = len(points)
    full = (1 << n) - 1
    masks = _cover_masks(points, eps)
    best = [None]

    def dfs(path, cov, depth, limit):
        if cov == full:
            best[0] = list(path)
            return True
        if depth == limit:
            return False
        last = path[-1]
        for j in range(n):
            if j != last and masks[last][j] | cov != cov:
                path.append(j)
                if dfs(path, cov | masks[last][j], depth + 1, limit):
                    return True
                path.pop()
        return False

    for k in range(1, kmax + 1):
        for s in range(n):
            if dfs([s], 0, 0, k):
                return k, best[0]
    return None


def has_class1_solution(points, k, eps=EPS):
    return min_class1(points, k, eps) is not None
