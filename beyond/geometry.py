"""Geometría básica de trayectorias poligonales en el plano."""
import numpy as np

EPS = 0.01          # tolerancia de cobertura
DELTA = 0.05        # umbral de giro inventado
MIN_TURN_DEG = 5.0  # ángulo mínimo para considerar un vértice como giro


def point_segment_distance(p, a, b):
    p, a, b = (np.asarray(v, float) for v in (p, a, b))
    ab = b - a
    n = float(ab @ ab)
    if n == 0.0:
        return float(np.linalg.norm(p - a))
    t = min(1.0, max(0.0, float((p - a) @ ab) / n))
    return float(np.linalg.norm(p - (a + t * ab)))


def covered(point, path, eps=EPS):
    return any(point_segment_distance(point, path[i], path[i + 1]) <= eps
               for i in range(len(path) - 1))


def uncovered(points, path, eps=EPS):
    return [i for i, p in enumerate(points) if not covered(p, path, eps)]


def turns(path, min_deg=MIN_TURN_DEG):
    """Vértices interiores donde la trayectoria gira de verdad."""
    out = []
    for i in range(1, len(path) - 1):
        u = np.asarray(path[i], float) - np.asarray(path[i - 1], float)
        v = np.asarray(path[i + 1], float) - np.asarray(path[i], float)
        nu, nv = np.linalg.norm(u), np.linalg.norm(v)
        if nu == 0 or nv == 0:
            continue
        ang = np.degrees(np.arccos(np.clip(u @ v / (nu * nv), -1, 1)))
        if ang > min_deg:
            out.append(i)
    return out
