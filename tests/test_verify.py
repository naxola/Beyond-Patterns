from beyond.geometry import point_segment_distance
from beyond.verify import is_valid, solution_class, invented_turns
from beyond.brute import min_class1, has_class1_solution


def s(x, y):
    """Rejilla 3x3 escalada a [0,1]²; admite índices fuera de la rejilla."""
    return (0.1 + 0.2 * x, 0.1 + 0.2 * y)


GRID = [s(x, y) for x in range(3) for y in range(3)]
# Solución clásica de 4 trazos: giros en (3,0) y (0,3), fuera de la rejilla.
CLASSIC = [s(0, 0), s(3, 0), s(0, 3), s(0, 0), s(2, 2)]


def test_distance():
    assert abs(point_segment_distance((0.5, 0.1), (0, 0), (1, 0)) - 0.1) < 1e-12
    assert abs(point_segment_distance((2, 0), (0, 0), (1, 0)) - 1) < 1e-12


def test_classic_solution_is_valid_class2():
    assert is_valid(GRID, CLASSIC, 4)
    assert solution_class(GRID, CLASSIC) == 2
    assert len(invented_turns(GRID, CLASSIC)) == 2


def test_too_few_segments_invalid():
    assert not is_valid(GRID, CLASSIC[:4], 4)   # deja puntos sin cubrir
    assert not is_valid(GRID, CLASSIC, 3)       # excede K


def test_class1_needs_5_on_grid():
    assert not has_class1_solution(GRID, 4)
    k, idx = min_class1(GRID, 5)
    assert k == 5
    path = [GRID[i] for i in idx]
    assert is_valid(GRID, path, 5)
    assert solution_class(GRID, path) == 1


def test_zigzag_class1():
    pts = [(0.1, 0.1), (0.5, 0.1), (0.9, 0.1), (0.5, 0.5), (0.1, 0.9)]
    k, _ = min_class1(pts, 4)
    assert k <= 3


def test_duplicate_vertices_do_not_hide_turns():
    dup = [s(0, 0), s(3, 0), s(3, 0), s(0, 3), s(0, 3), s(0, 0), s(2, 2)]
    assert solution_class(GRID, dup) == 2
    assert len(invented_turns(GRID, dup)) == 2
