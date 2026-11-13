"""Figuras del experimento 2.   python3 -m polygons.visualize datasets"""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
C1, C2 = "#2a78d6", "#eb6834"          # Dataset 1 (azul), Dataset 2 (naranja)
OUT = "polygons/results"
LEVEL_NAMES = {0: "casi regular", 1: "irregular (convexo)", 2: "no convexo", 3: "estrecho (convexo)"}
OK_C, BAD_C = "#0ca30c", "#d03b3b"      # estado: válido / inválido (siempre con ✓ / ✗)
plt.rcParams.update({"font.family": "DejaVu Sans", "text.color": INK, "savefig.facecolor": SURFACE,
                     "figure.facecolor": SURFACE, "axes.facecolor": SURFACE})


def panel(ax, pts, tour=None, color=C1, numbers=False):
    """Un problema: puntos de entrada y, si se da, el recorrido cerrado."""
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color(GRID); s.set_linewidth(1)
    if tour is not None:
        P = pts[list(tour) + [tour[0]]]
        ax.plot(P[:, 0], P[:, 1], color=color, lw=2, solid_joinstyle="round", zorder=2)
        a, b = P[0], P[1]                              # flecha de sentido en el primer lado
        m = a + 0.55 * (b - a)
        ax.annotate("", xy=m, xytext=a + 0.45 * (b - a),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=0, mutation_scale=14), zorder=3)
        ax.scatter(*pts[tour[0]], s=150, facecolor="none", edgecolor=color, lw=2, zorder=3)
    ax.scatter(pts[:, 0], pts[:, 1], s=42, color=INK, edgecolor=SURFACE, lw=1.5, zorder=4)
    if numbers and tour is not None:
        c = pts.mean(0)
        for k, i in enumerate(tour):
            d = pts[i] - c; d = d / (np.linalg.norm(d) + 1e-9)
            ax.text(*(pts[i] + 0.07 * d), str(k + 1), ha="center", va="center", fontsize=8, color=INK2)


def legend(fig, y, colors=(C1, C2)):
    h = [Line2D([], [], marker="o", ls="", color=INK, markersize=6, label="Punto de entrada"),
         Line2D([], [], color=colors[0], lw=2, label="Trayectoria objetivo · Dataset 1 (4 puntos)"),
         Line2D([], [], color=colors[1], lw=2, label="Trayectoria objetivo · Dataset 2 (7 puntos)"),
         Line2D([], [], marker="o", ls="", markerfacecolor="none", markeredgecolor=INK2, markeredgewidth=2,
                markersize=10, label="Inicio (la flecha indica el sentido)")]
    fig.legend(handles=h, loc="upper left", bbox_to_anchor=(0.035, y), ncol=4, frameon=False,
               fontsize=9, labelcolor=INK2, handletextpad=0.6, columnspacing=1.8)


def datasets(cols=6):
    d = [np.load("polygons/data/dataset1_n4.npz"), np.load("polygons/data/dataset2_n7.npz")]
    fig, axes = plt.subplots(4, cols, figsize=(cols * 1.9 + 2.2, 4 * 1.9 + 1.5))
    fig.subplots_adjust(left=0.175, right=0.985, top=0.86, bottom=0.02, wspace=0.08, hspace=0.08)
    for r in range(4):
        ds, lvl = d[r // 2], r % 2
        idx = np.nonzero(ds["level"] == lvl)[0][:cols]
        for c, i in enumerate(idx):
            panel(axes[r, c], ds["points"][i], ds["tour"][i], (C1, C2)[r // 2])
        axes[r, 0].set_ylabel(LEVEL_NAMES[lvl], fontsize=9, color=INK2, rotation=0, ha="right", va="center", labelpad=10)
    for k, (name, col) in enumerate([("Dataset 1\n4 puntos → cuadrilátero", C1), ("Dataset 2\n7 puntos → heptágono", C2)]):
        fig.text(0.012, axes[2 * k, 0].get_position().y1, name, fontsize=10, fontweight="bold", color=INK, va="top")
    fig.text(0.012, 0.965, "Datos de entrenamiento", fontsize=15, fontweight="bold", va="center")
    fig.text(0.012, 0.935, "Cada recuadro es un problema: el modelo recibe los puntos barajados y debe devolver el orden que forma el polígono.",
             fontsize=9.5, color=INK2, va="center")
    legend(fig, 0.915)
    fig.savefig(f"{OUT}/datasets.png", dpi=200)
    plt.close(fig)


def example():
    """Entrada (lo que ve el modelo) frente a salida esperada, un caso por dataset."""
    d = [np.load("polygons/data/dataset1_n4.npz"), np.load("polygons/data/dataset2_n7.npz")]
    fig, axes = plt.subplots(2, 2, figsize=(6.4, 7.2))
    fig.subplots_adjust(left=0.04, right=0.96, top=0.84, bottom=0.03, wspace=0.08, hspace=0.2)
    for r, (ds, col, name) in enumerate(zip(d, (C1, C2), ("Dataset 1 · 4 puntos", "Dataset 2 · 7 puntos"))):
        i = np.nonzero(ds["level"] == 1)[0][3]
        panel(axes[r, 0], ds["points"][i])
        panel(axes[r, 1], ds["points"][i], ds["tour"][i], col, numbers=True)
        axes[r, 0].set_title(f"{name}\nEntrada: puntos sin orden", fontsize=9.5, color=INK2, loc="left")
        axes[r, 1].set_title("\nSalida esperada: orden de recorrido", fontsize=9.5, color=INK2, loc="left")
    fig.text(0.04, 0.955, "Qué recibe y qué debe devolver el modelo", fontsize=14, fontweight="bold")
    fig.text(0.04, 0.92, "Los números indican el orden de visita; el polígono se cierra volviendo al 1.", fontsize=9.5, color=INK2)
    fig.savefig(f"{OUT}/ejemplo_entrada_salida.png", dpi=200)
    plt.close(fig)


def _load_model(path):
    import torch
    from .model_pointer import PointerModel
    m = PointerModel(); m.load_state_dict(torch.load(path)); m.eval()
    return m


def _predict(model, data, idx):
    import torch
    return model.predict(torch.as_tensor(data["points"][idx])).numpy()


def predictions(model_path, sizes=(10, 12), per_level=2, levels=(0, 1, 3, 2)):
    """Predicciones con tamaños nunca vistos. Verde ✓ = polígono válido, rojo ✗ = no válido."""
    from .metrics import is_valid_polygon
    from .evaluate import load
    model = _load_model(model_path)
    cols = per_level * len(levels)
    fig, axes = plt.subplots(len(sizes), cols, figsize=(cols * 1.75 + 1.0, len(sizes) * 1.95 + 1.55))
    fig.subplots_adjust(left=0.08, right=0.99, top=0.80, bottom=0.02, wspace=0.07, hspace=0.07)
    for r, n in enumerate(sizes):
        d = load(f"test_n{n}")
        for li, lv in enumerate(levels):
            idx = np.nonzero(d["level"] == lv)[0][:per_level]
            tours = _predict(model, d, idx)
            for k, (i, t) in enumerate(zip(idx, tours)):
                ax = axes[r, li * per_level + k]
                ok = is_valid_polygon(d["points"][i], t)
                panel(ax, d["points"][i], t, OK_C if ok else BAD_C)
                ax.text(0.04, 0.95, "✓" if ok else "✗", transform=ax.transAxes, fontsize=13, fontweight="bold",
                        color=OK_C if ok else BAD_C, va="top")
        axes[r, 0].set_ylabel(f"{n} puntos", fontsize=11, fontweight="bold", color=INK, rotation=0, ha="right", va="center", labelpad=8)
    for li, lv in enumerate(levels):
        a, b = axes[0, li * per_level].get_position(), axes[0, li * per_level + per_level - 1].get_position()
        fig.text((a.x0 + b.x1) / 2, a.y1 + 0.012, LEVEL_NAMES[lv], ha="center", fontsize=10, color=INK2)
    fig.text(0.012, 0.955, "Predicciones con más puntos de los entrenados", fontsize=15, fontweight="bold")
    fig.text(0.012, 0.922, "Entrenado solo con 4 y 7 puntos. Aquí recibe 10 y 12 y debe unirlos en un polígono sin cruces.", fontsize=9.5, color=INK2)
    h = [Line2D([], [], color=OK_C, lw=2, label="✓ Polígono válido (todos los puntos, sin cruces)"),
         Line2D([], [], color=BAD_C, lw=2, label="✗ No válido")]
    fig.legend(handles=h, loc="upper left", bbox_to_anchor=(0.005, 0.90), ncol=2, frameon=False, fontsize=9, labelcolor=INK2)
    fig.savefig(f"{OUT}/predicciones_10_12.png", dpi=200); plt.close(fig)


def curves(eval_json="polygons/results/eval.json"):
    """Acierto (polígonos válidos) frente al número de puntos, un panel por nivel."""
    import json
    res = json.load(open(eval_json))
    sizes = sorted(int(n) for n in next(iter(res["modelo"].values())))
    names = ["regular", "irregular", "estrecho", "noconvexo"]
    titles = {"regular": "Casi regular", "irregular": "Irregular (convexo)", "estrecho": "Estrecho (convexo)", "noconvexo": "No convexo (solo prueba)"}
    series = [("Modelo", C1, "modelo"), ("Vecino más cercano", C2, "vecino más cercano"), ("Orden angular", "#1baf7a", "orden angular")]
    fig, axes = plt.subplots(1, 4, figsize=(15, 4.4), sharey=True)
    fig.subplots_adjust(left=0.05, right=0.985, top=0.70, bottom=0.14, wspace=0.08)
    for ax, lv in zip(axes, names):
        for n in (4, 7):
            ax.axvspan(n - 0.3, n + 0.3, color="#e9e8e4", zorder=0)
        for label, col, key in series:
            if key == "modelo":
                M = np.array([[res["modelo"][p][str(n)].get(lv, {"valid": np.nan})["valid"] for n in sizes] for p in res["modelo"]]) * 100
                y, lo, hi = np.nanmean(M, 0), np.nanmin(M, 0), np.nanmax(M, 0)
                ax.fill_between(sizes, lo, hi, color=col, alpha=0.18, lw=0)
            else:
                y = np.array([res["baselines"][key][str(n)].get(lv, {"valid": np.nan})["valid"] for n in sizes]) * 100
            if key == "orden angular":      # techo: trazo ancho y claro por debajo, para que se vea el modelo encima
                ax.plot(sizes, y, color=col, lw=7, alpha=0.35, solid_capstyle="round", zorder=2, label=label)
            else:
                ax.plot(sizes, y, color=col, lw=2, marker="o", ms=4.5, mec=SURFACE, mew=1.2, zorder=4 if key == "modelo" else 3, label=label)
        ax.set_ylim(-3, 104); ax.set_xticks(sizes)
        ax.set_title(titles[lv], fontsize=10.5, color=INK, loc="left")
        ax.tick_params(colors=INK2, labelsize=8.5, length=0)
        ax.grid(axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True)
        for sp in ax.spines.values(): sp.set_visible(False)
        ax.set_xlabel("Número de puntos", fontsize=9, color=INK2)
    axes[0].set_ylabel("Polígonos válidos (%)", fontsize=9.5, color=INK2)
    fig.text(0.012, 0.955, "Acierto frente al número de puntos", fontsize=15, fontweight="bold")
    fig.text(0.012, 0.905, "Franjas grises = tamaños de entrenamiento (4 y 7). El resto son tamaños nunca vistos. La banda del modelo es el rango entre semillas.",
             fontsize=9.5, color=INK2)
    ns = len(res["modelo"])
    h = [Line2D([], [], color=C1, lw=2, marker="o", ms=5, label=f"Modelo ({ns} semilla{'s' if ns != 1 else ''})"),
         Line2D([], [], color=C2, lw=2, marker="o", ms=5, label="Vecino más cercano (atajo)"),
         Line2D([], [], color="#1baf7a", lw=7, alpha=0.35, label="Orden angular (techo, 100 %)")]
    fig.legend(handles=h, loc="upper left", bbox_to_anchor=(0.005, 0.865), ncol=3, frameon=False, fontsize=9.5, labelcolor=INK2)
    fig.savefig(f"{OUT}/acierto_vs_n.png", dpi=200); plt.close(fig)


def failures(model_path, cols=6):
    """Los fallos del modelo (cualquier N de prueba): predicción en rojo, referencia en gris."""
    from .metrics import is_valid_polygon
    from .evaluate import load
    model = _load_model(model_path)
    found = []
    for n in (16, 12, 10, 9, 8):
        d = load(f"test_n{n}")
        for s in range(0, 3000, 500):
            idx = np.arange(s, s + 500)
            tours = _predict(model, d, idx)
            for i, t in zip(idx, tours):
                if not is_valid_polygon(d["points"][i], t):
                    found.append((n, d["points"][i], t, d["tour"][i], int(d["level"][i])))
        if len(found) >= cols * 2:
            break
    found = found[: cols * 2]
    if not found:
        print("sin fallos que mostrar"); return
    rows = int(np.ceil(len(found) / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 1.9 + 0.5, rows * 2.2 + 1.3), squeeze=False)
    fig.subplots_adjust(left=0.02, right=0.99, top=0.80, bottom=0.02, wspace=0.07, hspace=0.18)
    for ax in axes.ravel(): ax.axis("off")
    for ax, (n, p, t, ref, lv) in zip(axes.ravel(), found):
        ax.axis("on")
        panel(ax, p)
        R = p[list(ref) + [ref[0]]]; ax.plot(R[:, 0], R[:, 1], color="#a9a8a3", lw=1.5, ls=(0, (3, 3)), zorder=1)
        T = p[list(t) + [t[0]]]; ax.plot(T[:, 0], T[:, 1], color=BAD_C, lw=2, zorder=2)
        ax.set_title(f"{n} puntos · {LEVEL_NAMES[lv].split(' ')[0]}", fontsize=8.5, color=INK2, loc="left")
    fig.text(0.012, 0.955, "Galería de fallos", fontsize=15, fontweight="bold")
    fig.text(0.012, 0.915, "Rojo: recorrido del modelo (no válido). Gris discontinuo: polígono correcto.", fontsize=9.5, color=INK2)
    fig.savefig(f"{OUT}/fallos.png", dpi=200); plt.close(fig)


if __name__ == "__main__":
    import os
    os.makedirs(OUT, exist_ok=True)
    what = sys.argv[1] if len(sys.argv) > 1 else "datasets"
    if what == "predictions":
        predictions(sys.argv[2])
    elif what == "curves":
        curves()
    elif what == "failures":
        failures(sys.argv[2])
    elif what == "datasets":
        datasets(); example()
        print("ok:", f"{OUT}/datasets.png", f"{OUT}/ejemplo_entrada_salida.png")
