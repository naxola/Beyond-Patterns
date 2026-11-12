import argparse, json, math, os, time
import numpy as np
import torch
from beyond.model import TrajModel, soft_ce
from beyond.train_utils import load, augment, to_tensors, evaluate

ap = argparse.ArgumentParser()
ap.add_argument("--epochs", type=int, default=40)
ap.add_argument("--batch", type=int, default=128)
ap.add_argument("--lr", type=float, default=5e-4)
ap.add_argument("--d", type=int, default=128)
ap.add_argument("--layers", type=int, default=3)
ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--no-augment", action="store_true")
ap.add_argument("--out", default="results/model.pt")
ap.add_argument("--final-control", action="store_true", help="evalúa el control UNA vez al final")
a = ap.parse_args()

torch.manual_seed(a.seed); rng = np.random.default_rng(a.seed)
tr, val = load("train"), load("val")
model = TrajModel(a.d, 4, a.layers, a.layers)
print("parámetros:", sum(p.numel() for p in model.parameters()))
opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=0.01)
N = len(tr["n"]); steps = a.epochs * (N // a.batch); step = 0; best = -1
os.makedirs(os.path.dirname(a.out), exist_ok=True)
for ep in range(a.epochs):
    model.train(); perm = rng.permutation(N); t0 = time.time(); tot = 0
    for b in range(N // a.batch):
        idx = perm[b * a.batch:(b + 1) * a.batch]
        pts, path = tr["points"][idx], tr["path"][idx]
        if not a.no_augment:
            pts, path = augment(pts, tr["n"][idx], path, tr["k"][idx], rng)
        P, n, k, tgt, mask = to_tensors(pts, tr["n"][idx], tr["k"][idx], path)
        lr = a.lr * min(1, step / 300) * 0.5 * (1 + math.cos(math.pi * step / steps))
        for g in opt.param_groups: g["lr"] = lr
        loss = soft_ce(model(P, n, k, tgt), tgt, mask)
        opt.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step()
        tot += loss.item(); step += 1
    if ep % 2 == 1 or ep == a.epochs - 1:
        r = evaluate(model, val, 500)
        print(f"ep {ep+1:3d} loss {tot/(N//a.batch):.3f} val válidas {r['valid']:.1%} por K {r['per_k']} ({time.time()-t0:.0f}s/ep)", flush=True)
        if r["valid"] > best:
            best = r["valid"]; torch.save(model.state_dict(), a.out)
    else:
        print(f"ep {ep+1:3d} loss {tot/(N//a.batch):.3f} ({time.time()-t0:.0f}s/ep)", flush=True)
print("mejor val:", best)
if a.final_control:
    model.load_state_dict(torch.load(a.out))
    r = evaluate(model, load("control"))
    print("CONTROL (competencia, un intento):", r)
    json.dump(r, open(os.path.splitext(a.out)[0] + "_control.json", "w"), indent=1)
