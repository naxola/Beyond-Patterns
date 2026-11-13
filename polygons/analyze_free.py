"""Clasifica la salida del modelo de coordenadas libres en las categorías prerregistradas."""
import numpy as np
import torch
from .metrics import is_simple
from .model_free import FreeModel, tokens_to_vertices

TOL = 0.012
CATS = ["Correcto", "Cruces", "Para antes", "Repite o se pasa", "Inventa vértice", "No termina"]


def classify(points, verts, ended, tol=TOL):
    """Devuelve (categoría, nº de vértices emitidos). Prioridad: inventa > no termina > resto."""
    n, m = len(points), len(verts)
    if m:
        d = np.linalg.norm(verts[:, None] - points[None], axis=2)
        idx = np.where(d.min(1) <= tol, d.argmin(1), -1)
    else:
        idx = np.array([], int)
    if (idx < 0).any():
        return "Inventa vértice", m
    if not ended:
        return "No termina", m
    dup = len(set(idx.tolist())) < m
    if m > n or dup:
        return "Repite o se pasa", m
    if m < n:
        return "Para antes", m
    return ("Correcto" if is_simple(points, idx) else "Cruces"), m


def run(model, data, batch=500):
    model.eval()
    cats, counts = [], []
    for s in range(0, len(data["points"]), batch):
        P = torch.as_tensor(data["points"][s:s + batch])
        toks = model.generate(P)
        for j in range(len(P)):
            v, ended = tokens_to_vertices(toks[j])
            c, m = classify(data["points"][s + j].astype(float), v, ended)
            cats.append(c); counts.append(m)
    return np.array(cats), np.array(counts)


def load_model(path):
    m = FreeModel(); m.load_state_dict(torch.load(path)); m.eval()
    return m
