"""Referencias: solucionador exacto (techo), búsqueda aleatoria, copia del vecino, ruido."""
import itertools
import numpy as np
from .geometry import EPS
from .verify import is_valid, solution_class


# ---------- candidatos de recta ----------
def _lines(P, eps):
    """Rectas por pares de puntos, deduplicadas por el conjunto de puntos que cubren."""
    n = len(P)
    seen, out = set(), []
    for i in range(n):
        for j in range(i + 1, n):
            d = P[j] - P[i]
            L = np.linalg.norm(d)
            nrm = np.array([-d[1], d[0]]) / L
            dist = np.abs((P - P[i]) @ nrm)
            mask = frozenset(np.nonzero(dist <= eps)[0].tolist())
            if mask in seen:
                continue
            seen.add(mask)
            out.append((P[i].copy(), d / L, mask))
    return out


def _intersect(l1, l2):
    (p, u, _), (q, v, _) = l1, l2
    den = u[0] * v[1] - u[1] * v[0]
    if abs(den) < 1e-9:
        return None
    t = ((q[0] - p[0]) * v[1] - (q[1] - p[1]) * v[0]) / den
    return p + t * u


def _end_options(P, line, vtx, eps):
    """Extremos posibles de un trazo extremo: punto de la recta más lejano de vtx por cada lado."""
    p, u, mask = line
    idx = sorted(mask)
    t_v = (vtx - p) @ u
    ts = [(P[i] - p) @ u for i in idx]
    opts = []
    for sgn in (1, -1):
        c = [t for t in ts if (t - t_v) * sgn > 0]
        if c:
            far = max(c, key=lambda t: abs(t - t_v))
            opts.append(p + far * u)
    return opts


def exact_class2(points, k, eps=EPS, collect=None):
    """Búsqueda exhaustiva sobre rectas por >=2 puntos. Devuelve el camino de menos trazos
    <= k que cubre todo (puede girar fuera de los puntos), o None.
    Exacta para problemas donde cada trazo de alguna solución contiene >=2 puntos."""
    P = np.asarray(points, float)
    n = len(P)
    lines = _lines(P, eps)
    maxc = max(len(l[2]) for l in lines)
    full = frozenset(range(n))
    for kk in range(2, k + 1):
        def dfs(seq, cov):
            d = len(seq)
            if d == kk:
                r = _build(P, seq, kk, eps)
                if r is not None and collect is not None:
                    collect.append(r)
                    return None   # seguir enumerando todas
                return r
            if len(cov) + (kk - d) * maxc < n:
                return None
            for l in lines:
                if d and _intersect(seq[-1], l) is None:
                    continue
                if l[2] <= cov:
                    continue
                r = dfs(seq + [l], cov | l[2])
                if r is not None:
                    return r
            return None
        r = dfs([], frozenset())
        if r is not None:
            return r
    return None


def all_solutions(points, k, eps=EPS):
    """Todas las soluciones válidas (<= k trazos) formadas por rectas que pasan por >=2 puntos."""
    out = []
    exact_class2(points, k, eps, collect=out)
    return out


def _build(P, seq, k, eps):
    vs = [_intersect(seq[i], seq[i + 1]) for i in range(k - 1)]
    if any(v is None for v in vs):
        return None
    for s in _end_options(P, seq[0], vs[0], eps):
        for e in _end_options(P, seq[-1], vs[-1], eps):
            path = [s] + vs + [e]
            if is_valid(P, path, k, eps):
                return np.array(path)
    return None


# ---------- referencias aleatorias ----------
def random_uniform(points, k, rng, tries):
    """Vértices uniformes en [0,1]². Referencia mínima."""
    for _ in range(tries):
        path = rng.uniform(0, 1, size=(k + 1, 2))
        if is_valid(points, path, k):
            return path
    return None


def random_lines(points, k, rng, tries, eps=EPS):
    """Azar informado: K rectas por pares de puntos elegidos al azar, unidas por sus cortes
    y recortadas con las mismas reglas que el solucionador exacto."""
    P = np.asarray(points, float)
    n = len(P)
    for _ in range(tries):
        seq = []
        for _ in range(k):
            i, j = rng.choice(n, 2, replace=False)
            d = P[j] - P[i]
            u = d / np.linalg.norm(d)
            dist = np.abs((P - P[i]) @ np.array([-u[1], u[0]]))
            seq.append((P[i], u, frozenset(np.nonzero(dist <= eps)[0].tolist())))
        path = _build(P, seq, k, eps)
        if path is not None:
            return path
    return None


def copy_nearest(points, k, train_points, train_n, train_k, train_path):
    """Copia la trayectoria del problema de entrenamiento más parecido (Chamfer, mismo K)."""
    P = np.asarray(points, float)
    best, bi = 1e9, None
    for i in np.nonzero(train_k == k)[0]:
        Q = train_points[i, :train_n[i]].astype(float)
        D = np.linalg.norm(P[:, None] - Q[None], axis=2)
        c = D.min(1).mean() + D.min(0).mean()
        if c < best:
            best, bi = c, i
    return train_path[bi, :k + 1].astype(float)


def add_noise(path, sigma, rng):
    """Referencia de ruido: perturba una salida del modelo (se usa desde la fase 5)."""
    return np.asarray(path, float) + rng.normal(0, sigma, np.shape(path))
