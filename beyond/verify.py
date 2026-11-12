"""Verificador de soluciones y clasificador de clase (1 / 2)."""
import numpy as np
from .geometry import EPS, DELTA, uncovered, turns


def n_segments(path):
    return len(path) - 1


def is_valid(points, path, k, eps=EPS):
    """Válida: ≤ k trazos y todos los puntos cubiertos."""
    return 2 <= len(path) <= k + 1 and not uncovered(points, path, eps)


def invented_turns(points, path, delta=DELTA):
    pts = np.asarray(points, float)
    out = []
    for i in turns(path):
        if np.linalg.norm(pts - np.asarray(path[i], float), axis=1).min() > delta:
            out.append(i)
    return out


def solution_class(points, path, delta=DELTA):
    """1 si todos los giros están sobre puntos dados; 2 si hay alguno inventado."""
    return 2 if invented_turns(points, path, delta) else 1
