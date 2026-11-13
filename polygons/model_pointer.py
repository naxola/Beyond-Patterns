"""Modelo de puntero: elige el siguiente punto entre los dados.

Ninguna parte usa el índice de paso ni el número de puntos N (sin codificación posicional,
contexto = media del grafo + primer punto + último punto), de modo que el tamaño no está
fijado por construcción y puede aplicarse a más puntos de los entrenados.
"""
import math
import torch
import torch.nn as nn
import torch.nn.functional as F

NF = 6


def fourier(xy):
    f = (2.0 ** torch.arange(NF, device=xy.device)) * math.pi
    a = xy.unsqueeze(-1) * f
    return torch.cat([xy, torch.sin(a).flatten(-2), torch.cos(a).flatten(-2)], -1)


class PointerModel(nn.Module):
    def __init__(self, d=128, heads=4, layers=3):
        super().__init__()
        self.d = d
        self.embed = nn.Sequential(nn.Linear(2 + 4 * NF, d), nn.GELU(), nn.Linear(d, d))
        enc = nn.TransformerEncoderLayer(d, heads, 4 * d, 0.0, batch_first=True, norm_first=True, activation="gelu")
        self.enc = nn.TransformerEncoder(enc, layers, enable_nested_tensor=False)
        self.start = nn.Parameter(torch.randn(d) * 0.1)
        self.ctx = nn.Linear(3 * d, d)
        self.glimpse = nn.MultiheadAttention(d, heads, batch_first=True)
        self.q = nn.Linear(d, d)
        self.k = nn.Linear(d, d)

    def encode(self, pts, n):
        M = pts.shape[1]
        valid = torch.arange(M, device=pts.device)[None] < n[:, None]
        h = self.enc(self.embed(fourier(pts)), src_key_padding_mask=~valid)
        return h, valid

    def step_logits(self, h, valid, visited, first, last, graph):
        c = self.ctx(torch.cat([graph, first, last], -1))[:, None]
        blocked = visited | ~valid
        blocked = blocked & ~blocked.all(1, keepdim=True)          # filas sin nada libre: no enmascarar
        g, _ = self.glimpse(c, h, h, key_padding_mask=blocked)
        s = (self.q(g) @ self.k(h).transpose(1, 2)).squeeze(1) / math.sqrt(self.d)
        s = 10 * torch.tanh(s)
        return s.masked_fill(blocked, float("-inf"))

    def forward(self, pts, n, tours=None, steps=None):
        """Con `tours`: forzado del maestro, devuelve (logits por paso). Sin `tours`: decodificación voraz."""
        B, M, _ = pts.shape
        h, valid = self.encode(pts, n)
        graph = (h * valid[..., None]).sum(1) / n[:, None].float()
        visited = torch.zeros(B, M, dtype=torch.bool, device=pts.device)
        first = last = self.start.expand(B, -1)
        steps = steps or (tours.shape[1] if tours is not None else int(n.max()))
        out, picks = [], []
        ar = torch.arange(B, device=pts.device)
        for t in range(steps):
            lg = self.step_logits(h, valid, visited, first, last, graph)
            out.append(lg)
            nxt = tours[:, t] if tours is not None else lg.argmax(-1)
            picks.append(nxt)
            if t == 0:
                first = h[ar, nxt]
            last = h[ar, nxt]
            visited = visited.clone(); visited[ar, nxt] = True
        return torch.stack(out, 1), torch.stack(picks, 1)

    @torch.no_grad()
    def predict(self, pts, n=None):
        n = n if n is not None else torch.full((pts.shape[0],), pts.shape[1], dtype=torch.long)
        return self(pts, n)[1]


def tour_loss(logits, tours, n):
    """Entropía cruzada por paso; solo cuentan los pasos < n de cada muestra."""
    B, T, M = logits.shape
    w = (torch.arange(T, device=logits.device)[None] < n[:, None]).float()
    lp = F.log_softmax(logits.clamp(min=-1e4), -1)
    nll = -lp.gather(-1, tours.unsqueeze(-1)).squeeze(-1)
    return (nll * w).sum() / w.sum()
