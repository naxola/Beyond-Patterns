import numpy as np
import torch
from .metrics import is_valid_polygon, same_cycle, is_convex
from .generate import LEVELS


def load(name):
    z = np.load(f"polygons/data/{name}.npz")
    return {k: z[k] for k in z.files}


def score(points, tours, ref, level):
    """Por problema: válido, coincidencia exacta. Resumen global y por nivel."""
    valid = np.array([is_valid_polygon(p, t) for p, t in zip(points, tours)])
    exact = np.array([same_cycle(t, r) for t, r in zip(tours, ref)])
    res = {"valid": valid.mean(), "exact": exact.mean(), "n": len(points)}
    for i, name in enumerate(LEVELS):
        m = level == i
        if m.any():
            res[name] = {"valid": valid[m].mean(), "exact": exact[m].mean()}
    return res, valid


def run_model(model, data, batch=500):
    model.eval()
    out = []
    for s in range(0, len(data["points"]), batch):
        pts = torch.as_tensor(data["points"][s:s + batch])
        out.append(model.predict(pts).numpy())
    return np.concatenate(out)


def run_baseline(fn, data, seed=0):
    rng = np.random.default_rng(seed)
    return np.array([fn(p.astype(float), rng) for p in data["points"]])
