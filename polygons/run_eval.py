"""python3 -m polygons.run_eval polygons/results/model_s0.pt [...]  -> tabla por N y nivel."""
import json, sys
import numpy as np
import torch
from .model_pointer import PointerModel
from .evaluate import load, run_model, run_baseline, score
from .baselines import BASELINES
from .generate import LEVELS

SIZES = [4, 5, 6, 7, 8, 9, 10, 12, 16]


def dataset(n):
    return load(f"control_n{n}") if n in (4, 7) else load(f"test_n{n}")


def main(paths, count=1500, out="polygons/results/eval.json"):
    res = {"modelo": {}, "baselines": {}}
    data = {n: dataset(n) for n in SIZES}
    data = {n: {k: v[:count] for k, v in d.items()} for n, d in data.items()}
    for path in paths:
        m = PointerModel(); m.load_state_dict(torch.load(path)); m.eval()
        res["modelo"][path] = {}
        for n, d in data.items():
            r, _ = score(d["points"], run_model(m, d), d["tour"], d["level"])
            res["modelo"][path][n] = r
    for b, fn in BASELINES.items():
        res["baselines"][b] = {n: score(d["points"], run_baseline(fn, d), d["tour"], d["level"])[0] for n, d in data.items()}
    json.dump(res, open(out, "w"), indent=1, default=float)
    return res


def table(res, path):
    lv = ["regular", "irregular", "estrecho", "noconvexo"]
    print(f"{'N':>3} | " + " | ".join(f"{l:>10}" for l in lv) + " | global")
    for n in SIZES:
        r = res["modelo"][path][n]
        print(f"{n:>3} | " + " | ".join(f"{(r[l]['valid']*100 if l in r else float('nan')):9.1f}%" for l in lv) + f" | {r['valid']*100:5.1f}%")


if __name__ == "__main__":
    res = main(sys.argv[1:])
    for p in sys.argv[1:]:
        print(p); table(res, p)
    print("\nBaselines (válidos, N=10 / N=12, por nivel):")
    for b, r in res["baselines"].items():
        for n in (10, 12):
            print(f"  {b:20s} N={n}: " + "  ".join(f"{l} {r[n][l]['valid']*100:5.1f}%" for l in ["regular", "irregular", "estrecho", "noconvexo"]))
