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
    # Para cada vértice se usa el anterior y el siguiente vértice *distintos*, de modo que
    # repetir un vértice no pueda ocultar un giro.
    P = [np.asarray(p, float) for p in path]
    for i in range(1, len(P) - 1):
        if np.array_equal(P[i], P[i - 1]):
            continue  # ya contado en su primera aparición
        j = i + 1
        while j < len(P) and np.array_equal(P[j], P[i]):
            j += 1
        if j == len(P):
            continue
        u, v = P[i] - P[i - 1], P[j] - P[i]
        nu, nv = np.linalg.norm(u), np.linalg.norm(v)
        ang = np.degrees(np.arccos(np.clip(u @ v / (nu * nv), -1, 1)))
        if ang > min_deg:
            out.append(i)
    return out
