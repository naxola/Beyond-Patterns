import numpy as np
from polygons.analyze_free import classify

SQ = np.array([[0.2, 0.2], [0.8, 0.2], [0.8, 0.8], [0.2, 0.8]])


def test_categories():
    assert classify(SQ, SQ[[0, 1, 2, 3]], True)[0] == "Correcto"
    assert classify(SQ, SQ[[0, 2, 1, 3]], True)[0] == "Cruces"
    assert classify(SQ, SQ[[0, 1, 2]], True) == ("Para antes", 3)
    assert classify(SQ, SQ[[0, 1, 2, 3, 0]], True)[0] == "Repite o se pasa"
    assert classify(SQ, SQ[[0, 1, 1, 3]], True)[0] == "Repite o se pasa"
    assert classify(SQ, np.vstack([SQ[:3], [[0.5, 0.5]]]), True)[0] == "Inventa vértice"
    assert classify(SQ, SQ[[0, 1, 2, 3]], False)[0] == "No termina"


def test_tolerance():
    near = SQ + 0.008   # distancia 0,0113 <= 0,012
    assert classify(SQ, near, True)[0] == "Correcto"
    far = SQ + 0.02
    assert classify(SQ, far, True)[0] == "Inventa vértice"
