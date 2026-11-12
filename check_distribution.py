"""Control de distribución: ¿se distinguen las entradas de entrenamiento y de prueba?
Características invariantes a la permutación de puntos. Acierto 0,5 = indistinguibles."""
import sys
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import cross_val_score


def feats(P, n, k, eps=0.01):
    P = P[:n].astype(float)
    d = np.linalg.norm(P[:, None] - P[None], axis=2)[np.triu_indices(n, 1)]
    # número de ternas casi alineadas (estructura "puntos sobre rectas")
    col = 0
    for i in range(n):
        for j in range(i + 1, n):
            u = P[j] - P[i]
            for l in range(j + 1, n):
                w = P[l] - P[i]
                if abs(u[0] * w[1] - u[1] * w[0]) / (np.linalg.norm(u) + 1e-9) < eps:
                    col += 1
    return [n, k, d.mean(), d.min(), d.max(), np.median(d), *P.mean(0), *P.std(0), col]


def load(name):
    z = np.load(f"data/{name}.npz")
    return np.array([feats(z["points"][i], z["n"][i], z["k"][i]) for i in range(len(z["n"]))])


if __name__ == "__main__":
    tr = load("train")[:1500]
    for other in ("control", "test_pure", "test_graded"):
        te = load(other)[:1500]
        m = min(len(tr), len(te))
        X = np.vstack([tr[:m], te[:m]]); y = np.r_[np.zeros(m), np.ones(m)]
        acc = cross_val_score(GradientBoostingClassifier(), X, y, cv=5).mean()
        print(f"train vs {other}: acierto del clasificador = {acc:.3f}")
