import argparse, math, os, time
import numpy as np
import torch
from .model_free import FreeModel, soft_loss, tours_to_targets
from .evaluate import load

ap = argparse.ArgumentParser()
ap.add_argument("--epochs", type=int, default=40)
ap.add_argument("--batch", type=int, default=256)
ap.add_argument("--lr", type=float, default=1e-3)
ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--train-sizes", default="4,7")
ap.add_argument("--out", default="polygons/results/free_s0.pt")
a = ap.parse_args()
torch.manual_seed(a.seed); rng = np.random.default_rng(a.seed)
sizes = [int(s) for s in a.train_sizes.split(",")]
names = {4: "dataset1_n4", 7: "dataset2_n7"}
M = max(sizes)
pts, tours, ns = [], [], []
for s in sizes:
    d = load(names[s]); p = np.zeros((len(d["points"]), M, 2), np.float32); p[:, :s] = d["points"]
    t = np.zeros((len(p), M), np.int64); t[:, :s] = d["tour"]
    pts.append(p); tours.append(t); ns.append(np.full(len(p), s))
pts, tours, ns = np.concatenate(pts), np.concatenate(tours), np.concatenate(ns)
P, Tt, Nn = torch.as_tensor(pts), torch.as_tensor(tours), torch.as_tensor(ns)
tgt, w = tours_to_targets(P, Tt, Nn)
model = FreeModel()
print("parámetros:", sum(p.numel() for p in model.parameters()), "| entrenamiento:", sizes, flush=True)
opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=0.01)
N = len(P); spe = N // a.batch; total = a.epochs * spe; step = 0
os.makedirs(os.path.dirname(a.out), exist_ok=True)
for ep in range(a.epochs):
    model.train(); perm = torch.as_tensor(rng.permutation(N)); tot = 0; t0 = time.time()
    for b in range(spe):
        i = perm[b * a.batch:(b + 1) * a.batch]
        lr = a.lr * min(1, step / 300) * 0.5 * (1 + math.cos(math.pi * step / total))
        for g in opt.param_groups: g["lr"] = lr
        loss = soft_loss(model(P[i], Nn[i], tgt[i]), tgt[i], w[i])
        opt.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step()
        tot += loss.item(); step += 1
    print(f"ep {ep+1:3d} loss {tot/spe:.4f} ({time.time()-t0:.0f}s/ep)", flush=True)
    torch.save(model.state_dict(), a.out)
