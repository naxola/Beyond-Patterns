import sys, time
import numpy as np
from beyond.baselines import exact_class2, random_uniform, random_lines, copy_nearest
from beyond.brute import min_class1
from beyond.verify import is_valid, solution_class

N = int(sys.argv[1]) if len(sys.argv) > 1 else 200
D = {n: np.load(f"data/{n}.npz") for n in ["train", "control", "test_pure", "test_graded"]}
tr = D["train"]


def prob(d, i):
    return d["points"][i, :d["n"][i]].astype(float), int(d["k"][i])


def rate(name, d, fn, want_class2):
    ok = ok1 = 0
    t = time.time()
    for i in range(N):
        P, k = prob(d, i)
        path = fn(P, k, i)
        if path is not None and is_valid(P, path, k):
            c = solution_class(P, path)
            ok += (c == 2) if want_class2 else 1
            ok1 += (c == 1)
    print(f"  {name:34s} válidas-{'clase2' if want_class2 else 'ok'}: {ok/N:6.1%}   válidas clase1: {ok1/N:6.1%}   ({time.time()-t:.0f}s)")


def c1(P, k, i):
    r = min_class1(P, k)
    return None if r is None else P[r[1]]


rng = np.random.default_rng(0)
for name in ["control", "test_pure", "test_graded"]:
    d = D[name]; w = name != "control"
    print(f"\n== {name} (n={N}) ==")
    rate("solucionador clase 1 (exacto)", d, c1, w)
    if w:
        rate("solucionador exacto clase 2 (techo)", d, lambda P, k, i: exact_class2(P, k), True)
    rate("copia del vecino de train", d, lambda P, k, i: copy_nearest(P, k, tr["points"], tr["n"], tr["k"], tr["path"]), w)
    for M in (100, 1000):
        rate(f"azar uniforme, M={M}", d, lambda P, k, i: random_uniform(P, k, rng, M), w)
    for M in (100, 10000):
        rate(f"azar sobre rectas de puntos, M={M}", d, lambda P, k, i: random_lines(P, k, rng, M), w)
