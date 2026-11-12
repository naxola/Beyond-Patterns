import numpy as np
from beyond.baselines import exact_class2, random_lines, random_uniform, add_noise
from beyond.generate import generate
from beyond.verify import is_valid, solution_class
from tests.test_verify import GRID


def test_exact_solves_nine_dots_with_4_segments():
    path = exact_class2(GRID, 4)
    assert path is not None and is_valid(GRID, path, 4)
    assert solution_class(GRID, path) == 2


def test_exact_solves_generated_test_problems():
    for sd in range(8):
        p = generate(sd, "test", lambda r, k: k - 1)
        path = exact_class2(p.points, p.k)
        assert path is not None and is_valid(p.points, path, p.k)
        assert solution_class(p.points, path) == 2


def test_exact_finds_nothing_when_k_too_small():
    assert exact_class2(GRID, 3) is None


def test_random_baselines_return_valid_or_none():
    rng = np.random.default_rng(0)
    p = generate(3, "test", lambda r, k: k - 1)
    for path in (random_lines(p.points, p.k, rng, 200), random_uniform(p.points, p.k, rng, 200)):
        assert path is None or is_valid(p.points, path, p.k)


def test_noise_changes_path():
    rng = np.random.default_rng(0)
    path = np.zeros((3, 2))
    assert np.abs(add_noise(path, 0.1, rng)).max() > 0
