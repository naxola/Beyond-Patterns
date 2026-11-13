import numpy as np
from polygons.generate import make_problem
from polygons.metrics import is_valid_polygon, is_convex, same_cycle, is_simple


def test_reference_tours_are_valid_polygons():
    rng = np.random.default_rng(0)
    for n in (4, 7, 10, 12, 16):
        for level in ("regular", "irregular", "estrecho", "noconvexo"):
            for _ in range(40):
                p = make_problem(rng, n, level)
                assert p.points.min() >= 0 and p.points.max() <= 1
                assert is_valid_polygon(p.points, p.tour)
                if level != "noconvexo":
                    assert is_convex(p.points, p.tour)


def test_canonical_start_and_direction():
    rng = np.random.default_rng(1)
    for _ in range(50):
        p = make_problem(rng, 7, "irregular")
        assert p.tour[0] == min(range(7), key=lambda i: (p.points[i, 0], p.points[i, 1]))
        P = p.points[p.tour]
        assert np.sum(P[:, 0] * np.roll(P[:, 1], -1) - np.roll(P[:, 0], -1) * P[:, 1]) > 0


def test_metrics():
    sq = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], float)
    assert is_valid_polygon(sq, [0, 1, 2, 3])
    assert not is_simple(sq, [0, 2, 1, 3])            # lados cruzados
    assert not is_valid_polygon(sq, [0, 1, 2])        # falta un punto
    assert not is_valid_polygon(sq, [0, 1, 1, 3])     # repite un punto
    assert same_cycle([0, 1, 2, 3], [2, 3, 0, 1]) and same_cycle([0, 1, 2, 3], [1, 0, 3, 2])
    assert not same_cycle([0, 1, 2, 3], [0, 2, 1, 3])
