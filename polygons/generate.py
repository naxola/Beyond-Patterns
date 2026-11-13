"""Generador de problemas: N puntos barajados + recorrido de referencia (polígono)."""
from dataclasses import dataclass
import numpy as np

LEVELS = ("regular", "irregular", "noconvexo", "estrecho")
MIN_DIST = 0.04


@dataclass
class Problem:
    points: np.ndarray   # (N, 2), barajados
    tour: np.ndarray     # (N,) índices en `points`, forma canónica
    level: str


def _canonical(points, order):
    """Empieza en el punto de menor x (desempate y) y gira en sentido antihorario."""
    order = list(order)
    start = min(order, key=lambda i: (points[i, 0], points[i, 1]))
    i = order.index(start)
    order = order[i:] + order[:i]
    P = points[order]
    area2 = np.sum(P[:, 0] * np.roll(P[:, 1], -1) - np.roll(P[:, 0], -1) * P[:, 1])
    if area2 < 0:
        order = [order[0]] + order[1:][::-1]
    return np.array(order)


def make_problem(rng, n, level):
    assert level in LEVELS and n >= 3
    gap = 2 * np.pi / n
    for _ in range(1000):
        jit = 0.05 if level == "regular" else 0.35
        ang = rng.uniform(0, 2 * np.pi) + gap * (np.arange(n) + rng.uniform(-jit, jit, n))
        r = rng.uniform(0.20, 0.40)
        rad = np.full(n, r)
        if level == "regular":
            rad = r * rng.uniform(0.97, 1.03, n)
        elif level == "noconvexo":
            rad = r * rng.uniform(0.55, 1.0, n)
        v = np.stack([rad * np.cos(ang), rad * np.sin(ang)], 1)
        if level in ("irregular", "estrecho"):        # elipse: sigue siendo convexo
            v[:, 1] *= rng.uniform(0.6, 1.0) if level == "irregular" else rng.uniform(0.12, 0.30)
            t = rng.uniform(0, 2 * np.pi)
            v = v @ np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]]).T
        lo, hi = v.min(0), v.max(0)
        c = rng.uniform(0.05 - lo, 0.95 - hi)          # el polígono cabe en [0.05, 0.95]²
        v = v + c
        d = np.linalg.norm(v[:, None] - v[None], axis=2) + np.eye(n)
        if d.min() < MIN_DIST:
            continue
        perm = rng.permutation(n)
        pts = v[perm]
        inv = np.argsort(perm)                         # vértice generado i -> índice en pts
        return Problem(pts, _canonical(pts, inv), level)
    raise RuntimeError("no se pudo generar")


def build(n, count, levels, seed):
    rng = np.random.default_rng(seed)
    probs = [make_problem(rng, n, levels[i % len(levels)]) for i in range(count)]
    return dict(points=np.array([p.points for p in probs], np.float32),
                tour=np.array([p.tour for p in probs], np.int16),
                level=np.array([LEVELS.index(p.level) for p in probs], np.int8))
