import argparse, time
from beyond.dataset import build, save

ap = argparse.ArgumentParser()
ap.add_argument("--train", type=int, default=20000)
ap.add_argument("--control", type=int, default=2000)
ap.add_argument("--test", type=int, default=1000)
ap.add_argument("--val", type=int, default=2000)
ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--only", nargs="*", default=None)
a = ap.parse_args()
# semillas base distintas por conjunto para que no compartan problemas
for i, (name, n) in enumerate([("train", a.train), ("control", a.control),
                               ("test_pure", a.test), ("test_graded", a.test), ("val", a.val)]):
    if a.only and name not in a.only:
        continue
    t = time.time()
    probs = build(name, n, a.seed * 100 + i + 1)
    save(name, probs)
    print(f"{name}: {len(probs)}/{n} problemas ({time.time()-t:.0f}s)")
