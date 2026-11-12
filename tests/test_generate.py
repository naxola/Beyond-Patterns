import numpy as np
from beyond.generate import generate, audit
from beyond.verify import solution_class


def test_train_problems_are_class1_with_k_equals_k1():
    for s in range(30):
        p = generate(s, "train", lambda r, k: 0)
        assert p is not None and audit(p) == []
        assert solution_class(p.points, p.path) == 1


def test_test_problems_have_no_class1_solution():
    for s in range(30):
        p = generate(s, "test", lambda r, k: k - 1)
        assert p is not None and audit(p) == []
        assert p.n_invented == p.k - 1


def test_audit_catches_bad_problem():
    p = generate(1, "train", lambda r, k: 0)
    p.kind = "test"
    assert audit(p)       # un problema de clase 1 no sirve como prueba


def test_test_problems_have_no_near_class1_solution():
    from beyond.baselines import all_solutions
    for s in range(12):
        p = generate(s, "test", lambda r, k: k - 1)
        assert all(solution_class(p.points, x) == 2 for x in all_solutions(p.points, p.k))
