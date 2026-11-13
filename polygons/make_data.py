"""python3 -m polygons.make_data  ->  polygons/data/*.npz"""
import os
import numpy as np
from .generate import build

OUT = "polygons/data"
TRAIN_LEVELS = ("regular", "irregular", "estrecho")
os.makedirs(OUT, exist_ok=True)
jobs = [("dataset1_n4", 4, 20000, TRAIN_LEVELS, 1), ("dataset2_n7", 7, 20000, TRAIN_LEVELS, 2),
        ("control_n4", 4, 2000, TRAIN_LEVELS, 11), ("control_n7", 7, 2000, TRAIN_LEVELS, 12)]
for i, n in enumerate((5, 6, 8, 9, 10, 12, 16)):
    jobs.append((f"test_n{n}", n, 3000, ("regular", "irregular", "estrecho", "noconvexo"), 100 + i))
for name, n, count, levels, seed in jobs:
    np.savez_compressed(f"{OUT}/{name}.npz", **build(n, count, levels, seed))
    print(name, count)
