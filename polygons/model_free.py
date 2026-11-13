"""Modelo B: genera coordenadas libres (x, y) por vértice y un símbolo FIN.

Sin máscara de visitados, sin N, sin límite de vértices fijado por parámetros (posición de
salida sinusoidal). Puede inventar vértices, repetir puntos o parar cuando quiera.
"""
import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from .model_pointer import fourier

BINS = 256
END = BINS            # id del símbolo FIN (solo en posiciones x)
BOS = BINS + 1
MAX_VERT = 24


def sinusoid(idx, d):
    """idx (...,) enteros -> (..., d)"""
    i = torch.arange(d // 2, device=idx.device)
    ang = idx.unsqueeze(-1).float() / (10000 ** (2 * i / d))
    return torch.cat([torch.sin(ang), torch.cos(ang)], -1)


class FreeModel(nn.Module):
    def __init__(self, d=128, heads=4, enc_layers=3, dec_layers=3):
        super().__init__()
        self.d = d
        self.embed = nn.Sequential(nn.Linear(2 + 4 * 6, d), nn.GELU(), nn.Linear(d, d))
        enc = nn.TransformerEncoderLayer(d, heads, 4 * d, 0.0, batch_first=True, norm_first=True, activation="gelu")
        self.enc = nn.TransformerEncoder(enc, enc_layers, enable_nested_tensor=False)
        self.tok = nn.Embedding(BINS + 2, d)
        self.xy = nn.Embedding(2, d)
        dec = nn.TransformerDecoderLayer(d, heads, 4 * d, 0.0, batch_first=True, norm_first=True, activation="gelu")
        self.dec = nn.TransformerDecoder(dec, dec_layers)
        self.norm = nn.LayerNorm(d)
        self.head = nn.Linear(d, BINS + 1)           # 256 niveles + FIN

    def encode(self, pts, n):
        M = pts.shape[1]
        valid = torch.arange(M, device=pts.device)[None] < n[:, None]
        return self.enc(self.embed(fourier(pts)), src_key_padding_mask=~valid), ~valid

    def decode(self, mem, pad, inp):
        T = inp.shape[1]
        pos = torch.arange(T, device=inp.device)
        h = self.tok(inp) + sinusoid(pos // 2, self.d)[None] + self.xy(pos % 2)[None]
        causal = torch.triu(torch.ones(T, T, dtype=torch.bool, device=inp.device), 1)
        lg = self.head(self.norm(self.dec(h, mem, tgt_mask=causal, memory_key_padding_mask=pad)))
        odd = (pos % 2 == 1)[None, :, None]            # FIN solo puede salir en posiciones x
        mask = torch.zeros_like(lg); mask[..., END] = float("-inf")
        return torch.where(odd, lg + mask, lg)

    def forward(self, pts, n, target):
        mem, pad = self.encode(pts, n)
        inp = torch.cat([torch.full_like(target[:, :1], BOS), target[:, :-1].clamp(min=0)], 1)
        return self.decode(mem, pad, inp)

    @torch.no_grad()
    def generate(self, pts, n=None, max_vert=MAX_VERT):
        n = n if n is not None else torch.full((pts.shape[0],), pts.shape[1], dtype=torch.long)
        mem, pad = self.encode(pts, n)
        toks = torch.full((pts.shape[0], 1), BOS, dtype=torch.long)
        done = torch.zeros(pts.shape[0], dtype=torch.bool)
        for _ in range(2 * max_vert + 1):
            nxt = self.decode(mem, pad, toks)[:, -1].argmax(-1)
            nxt = torch.where(done, torch.full_like(nxt, END), nxt)
            done = done | (nxt == END)
            toks = torch.cat([toks, nxt[:, None]], 1)
            if done.all():
                break
        return toks[:, 1:]


def soft_loss(logits, target, weight, sigma=1.0):
    """Objetivo gaussiano sobre bins vecinos; FIN es un objetivo duro."""
    b = torch.arange(BINS + 1, device=logits.device)[None, None]
    soft = torch.exp(-0.5 * ((b - target.unsqueeze(-1)) / sigma) ** 2)
    soft[..., END] = 0
    soft = torch.where((target == END).unsqueeze(-1), (b == END).float().expand_as(soft), soft)
    soft = soft / soft.sum(-1, keepdim=True)
    lp = F.log_softmax(logits, -1).clamp(min=-30)
    return (-(soft * lp).sum(-1) * weight).sum() / weight.sum()


def tours_to_targets(points, tours, n):
    """(B, M, 2), (B, M), (B,) -> objetivos (B, 2*M+1) y pesos; la lista termina en FIN."""
    B, M, _ = points.shape
    T = 2 * M + 1
    tgt = torch.zeros(B, T, dtype=torch.long); w = torch.zeros(B, T)
    for i in range(B):
        k = int(n[i])
        v = points[i][tours[i, :k]]
        tgt[i, :2 * k] = (v.clamp(0, 1 - 1e-6) * BINS).long().reshape(-1)
        tgt[i, 2 * k] = END
        w[i, :2 * k + 1] = 1
    return tgt, w


def tokens_to_vertices(tokens):
    """(L,) -> (vértices (m,2) en [0,1], terminó)."""
    t = tokens.tolist()
    xs = []
    for k in range(0, len(t) - 1, 2):
        if t[k] == END:
            return _pairs(xs), True
        xs += [t[k], t[k + 1] if t[k + 1] != END else 0]
    return _pairs(xs), False


def _pairs(xs):
    import numpy as np
    a = (np.array(xs, float) + 0.5) / BINS
    return a.reshape(-1, 2)
