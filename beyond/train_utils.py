"""Utilidades de entrenamiento y evaluación (cargar datos, aumento, validez de salidas)."""
import numpy as np
import torch
from .verify import is_valid, solution_class
from .model import coords_to_tokens, MAX_V

# Simetrías del cuadrado unidad (grupo diédrico). Conservan clase 1, validez y alineaciones.
_T = [lambda x, y: (x, y), lambda x, y: (1 - x, y), lambda x, y: (x, 1 - y), lambda x, y: (1 - x, 1 - y),
      lambda x, y: (y, x), lambda x, y: (1 - y, x), lambda x, y: (y, 1 - x), lambda x, y: (1 - y, 1 - x)]


def load(name):
    z = np.load(f"data/{name}.npz")
    return {k: z[k] for k in z.files}


def augment(pts, n, path, k, rng):
    """Una simetría del cuadrado por muestra; recanoniza el camino (empieza por el extremo menor)."""
    pts, path = pts.copy(), path.copy()
    for i in range(len(pts)):
        f = _T[int(rng.integers(8))]
        m = n[i]
        pts[i, :m, 0], pts[i, :m, 1] = f(pts[i, :m, 0], pts[i, :m, 1])
        v = k[i] + 1
        path[i, :v, 0], path[i, :v, 1] = f(path[i, :v, 0], path[i, :v, 1])
        if tuple(path[i, 0]) > tuple(path[i, v - 1]):
            path[i, :v] = path[i, :v][::-1]
    return pts, path


def to_tensors(pts, n, k, path):
    tgt = coords_to_tokens(torch.as_tensor(path))
    mask = torch.zeros_like(tgt, dtype=torch.float32)
    for i, kk in enumerate(k):
        mask[i, : 2 * (kk + 1)] = 1
    return (torch.as_tensor(pts), torch.as_tensor(n).long(), torch.as_tensor(k).long(), tgt, mask)


@torch.no_grad()
def evaluate(model, data, count=None, batch=500, sample=False):
    """Un intento voraz por problema. Devuelve dict con tasa de válidas y de clase 2."""
    model.eval()
    m = len(data["n"]) if count is None else min(count, len(data["n"]))
    ok = c2 = 0
    per_k = {2: [0, 0], 3: [0, 0], 4: [0, 0]}
    for s in range(0, m, batch):
        sl = slice(s, min(s + batch, m))
        pts = torch.as_tensor(data["points"][sl])
        out = model.generate(pts, torch.as_tensor(data["n"][sl]).long(), torch.as_tensor(data["k"][sl]).long(), sample=sample).numpy()
        for j, i in enumerate(range(sl.start, sl.stop)):
            kk = int(data["k"][i]); P = data["points"][i, :data["n"][i]].astype(float)
            path = out[j, :kk + 1].astype(float)
            v = is_valid(P, path, kk)
            per_k[kk][0] += 1; per_k[kk][1] += v
            if v:
                ok += 1
                c2 += solution_class(P, path) == 2
    return {"valid": ok / m, "class2": c2 / m, "n": m,
            "per_k": {k: (v[1] / v[0] if v[0] else None) for k, v in per_k.items()}}
