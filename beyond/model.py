"""Transformer codificador-decodificador: conjunto de puntos + K -> trayectoria de coordenadas libres.

- El codificador NO usa codificación posicional: el orden de los puntos no importa.
- El decodificador genera K+1 vértices como pares (x, y) discretizados en BINS niveles por eje.
  La salida son coordenadas libres: el modelo no elige entre los puntos dados.
- K entra como un token extra; no hay símbolo de fin porque el número de vértices es K+1.
"""
import math
import torch
import torch.nn as nn
import torch.nn.functional as F

BINS = 256
MAX_K = 4
MAX_V = MAX_K + 1
L = 2 * MAX_V            # tokens de salida (x0,y0,x1,y1,...)
BOS = BINS               # id del token de inicio
NFREQ = 8


def fourier(xy):
    """(..., 2) -> (..., 2 + 4*NFREQ): coordenadas + senos/cosenos para precisión fina."""
    f = (2.0 ** torch.arange(NFREQ, device=xy.device)) * math.pi
    a = xy.unsqueeze(-1) * f                      # (..., 2, NFREQ)
    return torch.cat([xy, torch.sin(a).flatten(-2), torch.cos(a).flatten(-2)], -1)


class TrajModel(nn.Module):
    def __init__(self, d=128, heads=4, enc_layers=3, dec_layers=3, drop=0.0):
        super().__init__()
        self.d = d
        self.pt = nn.Sequential(nn.Linear(2 + 4 * NFREQ, d), nn.GELU(), nn.Linear(d, d))
        self.k_emb = nn.Embedding(MAX_K + 1, d)
        enc = nn.TransformerEncoderLayer(d, heads, 4 * d, drop, batch_first=True, norm_first=True, activation="gelu")
        self.enc = nn.TransformerEncoder(enc, enc_layers, enable_nested_tensor=False)
        self.tok = nn.Embedding(BINS + 1, d)
        self.pos = nn.Embedding(L, d)
        dec = nn.TransformerDecoderLayer(d, heads, 4 * d, drop, batch_first=True, norm_first=True, activation="gelu")
        self.dec = nn.TransformerDecoder(dec, dec_layers)
        self.norm = nn.LayerNorm(d)
        self.head = nn.Linear(d, BINS)

    def encode(self, pts, n, k):
        B, M, _ = pts.shape
        valid = torch.arange(M, device=pts.device)[None] < n[:, None]
        x = torch.cat([self.pt(fourier(pts)), self.k_emb(k)[:, None]], 1)
        pad = torch.cat([~valid, torch.zeros(B, 1, dtype=torch.bool, device=pts.device)], 1)
        return self.enc(x, src_key_padding_mask=pad), pad

    def decode(self, mem, pad, k, tokens):
        """tokens: (B, T) con BOS al principio -> logits (B, T, BINS)."""
        T = tokens.shape[1]
        h = self.tok(tokens) + self.pos(torch.arange(T, device=tokens.device))[None] + self.k_emb(k)[:, None]
        causal = torch.triu(torch.ones(T, T, dtype=torch.bool, device=tokens.device), 1)
        h = self.dec(h, mem, tgt_mask=causal, memory_key_padding_mask=pad)
        return self.head(self.norm(h))

    def forward(self, pts, n, k, target_tokens):
        mem, pad = self.encode(pts, n, k)
        inp = torch.cat([torch.full_like(target_tokens[:, :1], BOS), target_tokens[:, :-1].clamp(min=0)], 1)
        return self.decode(mem, pad, k, inp)

    @torch.no_grad()
    def generate(self, pts, n, k, sample=False, temperature=1.0):
        """Decodificación voraz (o muestreo). Devuelve coordenadas (B, MAX_V, 2) en [0,1]."""
        mem, pad = self.encode(pts, n, k)
        toks = torch.full((pts.shape[0], 1), BOS, dtype=torch.long, device=pts.device)
        for _ in range(L):
            logits = self.decode(mem, pad, k, toks)[:, -1]
            if sample:
                nxt = torch.multinomial(F.softmax(logits / temperature, -1), 1)
            else:
                nxt = logits.argmax(-1, keepdim=True)
            toks = torch.cat([toks, nxt], 1)
        return tokens_to_coords(toks[:, 1:])


def coords_to_tokens(path):
    """(B, MAX_V, 2) en [0,1] -> (B, L) enteros."""
    return (path.clamp(0, 1 - 1e-6) * BINS).long().reshape(path.shape[0], L)


def tokens_to_coords(tokens):
    return ((tokens.float() + 0.5) / BINS).reshape(tokens.shape[0], MAX_V, 2)


def soft_ce(logits, target, mask, sigma=1.0):
    """Entropía cruzada con objetivo gaussiano sobre bins vecinos (los bins son ordinales)."""
    b = torch.arange(BINS, device=logits.device)[None, None]
    soft = torch.exp(-0.5 * ((b - target.unsqueeze(-1)) / sigma) ** 2)
    soft = soft / soft.sum(-1, keepdim=True)
    loss = -(soft * F.log_softmax(logits, -1)).sum(-1)
    return (loss * mask).sum() / mask.sum()
