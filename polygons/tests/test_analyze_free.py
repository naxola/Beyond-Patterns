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


def test_tokens_to_vertices_end_detection():
    import torch
    from polygons.model_free import tokens_to_vertices, END
    v, ended = tokens_to_vertices(torch.tensor([10, 20, 30, 40, END]))
    assert ended and v.shape == (2, 2)
    v, ended = tokens_to_vertices(torch.tensor([10, 20, 30, 40]))
    assert not ended and v.shape == (2, 2)
    v, ended = tokens_to_vertices(torch.tensor([END]))
    assert ended and v.shape == (0, 2)
