import argparse, json, math, os, time
import numpy as np
import torch
from .model_pointer import PointerModel, tour_loss
from .evaluate import load, run_model, score

ap = argparse.ArgumentParser()
ap.add_argument("--epochs", type=int, default=30)
ap.add_argument("--batch", type=int, default=256)
ap.add_argument("--lr", type=float, default=1e-3)
ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--train-sizes", default="4,7", help="p. ej. 4,7  |  4  |  7")
ap.add_argument("--out", default="polygons/results/model_s0.pt")
a = ap.parse_args()
torch.manual_seed(a.seed); rng = np.random.default_rng(a.seed)

sizes = [int(s) for s in a.train_sizes.split(",")]
name = {4: "dataset1_n4", 7: "dataset2_n7"}
parts = [load(name[s]) for s in sizes]
M = max(sizes)


def pad(d):
    n = d["points"].shape[1]
    pts = np.zeros((len(d["points"]), M, 2), np.float32); pts[:, :n] = d["points"]
    tr = np.zeros((len(d["points"]), M), np.int64); tr[:, :n] = d["tour"]
    return pts, tr, np.full(len(pts), n)


P = [pad(d) for d in parts]
pts = np.concatenate([p[0] for p in P]); tours = np.concatenate([p[1] for p in P]); ns = np.concatenate([p[2] for p in P])
controls = {s: load(f"control_n{s}") for s in sizes}
model = PointerModel()
print("parámetros:", sum(p.numel() for p in model.parameters()), "| tamaños de entrenamiento:", sizes, flush=True)
opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=0.01)
N = len(pts); spe = N // a.batch; total = a.epochs * spe; step = 0
os.makedirs(os.path.dirname(a.out), exist_ok=True)
for ep in range(a.epochs):
    model.train(); perm = rng.permutation(N); tot = 0; t0 = time.time()
    for b in range(spe):
        i = perm[b * a.batch:(b + 1) * a.batch]
        n = torch.as_tensor(ns[i]); T = int(n.max())
        lr = a.lr * min(1, step / 200) * 0.5 * (1 + math.cos(math.pi * step / total))
        for g in opt.param_groups: g["lr"] = lr
        lg, _ = model(torch.as_tensor(pts[i]), n, torch.as_tensor(tours[i][:, :T]))
        loss = tour_loss(lg, torch.as_tensor(tours[i][:, :T]), n)
        opt.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step()
        tot += loss.item(); step += 1
    if ep % 5 == 4 or ep == a.epochs - 1:
        msg = []
        for s, c in controls.items():
            r, _ = score(c["points"][:500], run_model(model, {k: v[:500] for k, v in c.items()}), c["tour"][:500], c["level"][:500])
            msg.append(f"control N={s}: válidos {r['valid']:.1%} exactos {r['exact']:.1%}")
        print(f"ep {ep+1:3d} loss {tot/spe:.4f} | " + " | ".join(msg) + f" ({time.time()-t0:.0f}s/ep)", flush=True)
    else:
        print(f"ep {ep+1:3d} loss {tot/spe:.4f}", flush=True)
torch.save(model.state_dict(), a.out)
