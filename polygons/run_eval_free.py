"""python3 -m polygons.run_eval_free modelo.pt [...] -> polygons/results/eval_free.json"""
import json, sys
from collections import Counter
import numpy as np
from .analyze_free import run, load_model, CATS
from .evaluate import load
from .generate import LEVELS

SIZES = [4, 5, 6, 7, 8, 9, 10, 12, 16]


def main(paths, count=1000, out="polygons/results/eval_free.json"):
    res = {}
    for p in paths:
        m = load_model(p); res[p] = {}
        for n in SIZES:
            d = load(f"control_n{n}") if n in (4, 7) else load(f"test_n{n}")
            d = {k: v[:count] for k, v in d.items()}
            cats, k = run(m, d)
            r = {"n": len(cats), "cats": {c: int((cats == c).sum()) for c in CATS},
                 "emitidos": {int(a): int(b) for a, b in Counter(k.tolist()).items()}, "por_nivel": {}}
            for i, lv in enumerate(LEVELS):
                mk = d["level"] == i
                if mk.any():
                    r["por_nivel"][lv] = {c: int((cats[mk] == c).sum()) for c in CATS}
            res[p][n] = r
            print(p.split("/")[-1], "N =", n, "->", {c: v for c, v in r["cats"].items() if v}, flush=True)
        json.dump(res, open(out, "w"), indent=1)
    return res


if __name__ == "__main__":
    main(sys.argv[1:])
