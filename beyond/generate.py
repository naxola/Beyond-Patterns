"""Generadores de problemas a partir de una trayectoria oculta de K trazos.

Cada problema = (puntos, K, trayectoria oculta). La trayectoria oculta demuestra que
tiene solución. Los vértices "dados" se incluyen como puntos; los "inventados" no.
Los extremos siempre son puntos dados (forma canónica: trayectoria recortada).
"""
from dataclasses import dataclass
import numpy as np
from .geometry import DELTA
from .verify import solution_class
from .brute import min_class1

NMIN, NMAX = 6, 12
MIN_PT_DIST = 0.03
MIN_SEG_LEN = 0.25
END_MARGIN = 0.07          # distancia mínima de un punto interior a los vértices de su trazo
MIN_TURN, MAX_TURN = 30.0, 165.0   # ángulo de giro en grados


@dataclass
class Problem:
    points: np.ndarray      # (N, 2)
    k: int
    path: np.ndarray        # (K+1, 2) trayectoria oculta canónica
    n_invented: int         # giros sin punto en la solución oculta
    kind: str               # "train" | "test"


def _sample_path(rng, k):
    for _ in range(1000):
        v = rng.uniform(0.05, 0.95, size=(k + 1, 2))
        d = np.diff(v, axis=0)
        L = np.linalg.norm(d, axis=1)
        if L.min() < MIN_SEG_LEN:
            continue
        ok = True
        for i in range(k - 1):
            c = d[i] @ d[i + 1] / (L[i] * L[i + 1])
            ang = np.degrees(np.arccos(np.clip(c, -1, 1)))
            if not (MIN_TURN <= ang <= MAX_TURN):
                ok = False
                break
        if ok:
            return v
    raise RuntimeError("no path")


def _canonical(v):
    return v if (v[0, 0], v[0, 1]) <= (v[-1, 0], v[-1, 1]) else v[::-1].copy()


def make_problem(rng, k, n_invented, kind):
    """n_invented giros interiores sin punto (elegidos al azar)."""
    assert 0 <= n_invented <= k - 1
    v = _sample_path(rng, k)
    invented = set(rng.choice(np.arange(1, k), size=n_invented, replace=False)) if n_invented else set()
    given = [i for i in range(k + 1) if i not in invented]
    pts = [v[i] for i in given]
    on_seg = [sum((i in given) for i in (s, s + 1)) for s in range(k)]
    need = [max(0, 2 - c) for c in on_seg]
    min_n = len(given) + sum(need)
    n = int(rng.integers(max(NMIN, min_n, 2 * k), NMAX + 1))  # mismo N mínimo por K en train y test
    extras = need[:]
    for _ in range(n - min_n):
        extras[int(rng.integers(0, k))] += 1
    for s in range(k):
        a, b = v[s], v[s + 1]
        L = np.linalg.norm(b - a)
        lo, hi = END_MARGIN / L, 1 - END_MARGIN / L
        for _ in range(extras[s]):
            pts.append(a + rng.uniform(lo, hi) * (b - a))
    pts = np.array(pts)
    perm = rng.permutation(len(pts))
    return Problem(pts[perm], k, _canonical(v), n_invented, kind)


def audit(p, eps=None):
    """Devuelve lista de fallos (vacía = problema válido para su tipo)."""
    from .verify import is_valid, invented_turns
    errs = []
    P = p.points
    if not (NMIN <= len(P) <= NMAX):
        errs.append("N fuera de rango")
    dm = np.linalg.norm(P[:, None] - P[None], axis=2) + np.eye(len(P))
    if dm.min() < MIN_PT_DIST:
        errs.append("puntos demasiado juntos")
    if P.min() < 0 or P.max() > 1:
        errs.append("fuera de [0,1]")
    if not is_valid(P, p.path, p.k):
        errs.append("trayectoria oculta no válida")
    n_inv = len(invented_turns(P, p.path))
    if n_inv != p.n_invented:
        errs.append("giros inventados != esperado")
    if p.kind == "train":
        if solution_class(P, p.path) != 1:
            errs.append("entrenamiento con solución de clase 2")
        r = min_class1(P, p.k)
        if r is None or r[0] != p.k:
            errs.append("k1 != K (K no es el mínimo de clase 1)")
    else:
        if p.n_invented < 1:
            errs.append("prueba sin giro inventado")
        if min_class1(P, p.k) is not None:
            errs.append("existe solución de clase 1 con <= K trazos")
    return errs


def generate(seed, kind, n_invented_fn, ks=(2, 3, 4), max_tries=200):
    rng = np.random.default_rng(seed)
    k = int(rng.choice(ks))
    ni = n_invented_fn(rng, k)
    for _ in range(max_tries):
        p = make_problem(rng, k, ni, kind)
        if not audit(p):
            return p
    return None
