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
LEVEL_NAMES = {0: "casi regular", 1: "irregular (convexo)", 2: "no convexo"}
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


if __name__ == "__main__":
    import os
    os.makedirs(OUT, exist_ok=True)
    what = sys.argv[1] if len(sys.argv) > 1 else "datasets"
    if what == "datasets":
        datasets(); example()
        print("ok:", f"{OUT}/datasets.png", f"{OUT}/ejemplo_entrada_salida.png")
