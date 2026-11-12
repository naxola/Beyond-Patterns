"""Construcción de conjuntos de datos en paralelo y guardado en .npz."""
from multiprocessing import Pool
import numpy as np
from .generate import generate

MAXN, MAXV = 12, 5


def _train_ni(rng, k):
    return 0


def _pure_ni(rng, k):
    return k - 1


def _graded_ni(rng, k):
    return int(rng.integers(1, k))


FNS = {"train": ("train", _train_ni, (2, 3, 4)),
       "control": ("train", _train_ni, (2, 3, 4)),
       "test_pure": ("test", _pure_ni, (2, 3, 4)),
       "test_graded": ("test", _graded_ni, (2, 3, 4))}


def _work(args):
    name, seed = args
    kind, fn, ks = FNS[name]
    return generate(seed, kind, fn, ks)


def build(name, n, base_seed, procs=4):
    seeds = [(name, int(s)) for s in np.random.SeedSequence(base_seed).generate_state(n)]
    with Pool(procs) as pool:
        probs = [p for p in pool.map(_work, seeds, chunksize=32) if p is not None]
    return probs


def to_arrays(probs):
    m = len(probs)
    pts = np.zeros((m, MAXN, 2), np.float32)
    n = np.zeros(m, np.int16)
    k = np.zeros(m, np.int16)
    path = np.zeros((m, MAXV, 2), np.float32)
    ninv = np.zeros(m, np.int16)
    for i, p in enumerate(probs):
        pts[i, :len(p.points)] = p.points
        n[i], k[i], ninv[i] = len(p.points), p.k, p.n_invented
        path[i, :p.k + 1] = p.path
    return dict(points=pts, n=n, k=k, path=path, n_invented=ninv)


def save(name, probs, out_dir="data"):
    import os
    os.makedirs(out_dir, exist_ok=True)
    np.savez_compressed(f"{out_dir}/{name}.npz", **to_arrays(probs))
