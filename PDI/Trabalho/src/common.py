"""Utilidades compartilhadas: dados, pos-processamento, rastreador e desenho."""
import glob
import os

import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.optimize import linear_sum_assignment
from skimage.morphology import skeletonize

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "Datasets", "csb-1_dataset", "csb-1_dataset")
CACHE = os.path.join(ROOT, "cache")
TEST_SEQ = "24_2_1_1"  # sequencia de teste do CSB-1 (nao usada no treino)


def sequences():
    return sorted(os.listdir(os.path.join(DATA, "images")))


def n_frames(seq):
    return len(glob.glob(os.path.join(DATA, "images", seq, "*.png")))


def load_frame(seq, k):
    """Quadro em tons de cinza (uint8)."""
    p = os.path.join(DATA, "images", seq, f"{k}.png")
    return np.asarray(Image.open(p).convert("L"))


def load_gt(seq, k):
    """Uniao das mmascaras por verme -> mascara binaria de verme."""
    out = None
    for f in glob.glob(os.path.join(DATA, "masks", seq, f"{k}_*.png")):
        m = np.asarray(Image.open(f)) > 0
        out = m if out is None else out | m
    return out


def clean_and_label(mask, min_area=80):
    """Abertura leve + remocao de componentes pequenos + rotulagem."""
    mask = ndi.binary_opening(mask, structure=np.ones((2, 2)))
    lab, n = ndi.label(mask, structure=np.ones((3, 3)))  # vizinhanca-8
    if n == 0:
        return lab, 0
    areas = ndi.sum(mask, lab, index=np.arange(1, n + 1))
    keep = np.zeros(n + 1, bool)
    keep[1:] = areas >= min_area
    lab = np.where(keep[lab], lab, 0)
    lab, n = ndi.label(lab > 0, structure=np.ones((3, 3)))
    return lab, n


def centroids(lab, n):
    if n == 0:
        return np.zeros((0, 2))
    return np.array(ndi.center_of_mass(lab > 0, lab, index=np.arange(1, n + 1)))


def dice(a, b):
    inter = (a & b).sum()
    return 2 * inter / max(a.sum() + b.sum(), 1)


def skeleton_ends(lab, n):
    """Para cada componente, as duas pontas do esqueleto (candidatas a cabeca/cauda), em (linha, coluna).

    Esqueletiza a mascara; pontas = pixels do esqueleto com 1 so vizinho. Se houver mais de duas
    (ramos espurios), usa o par mais distante. Se nao houver (verme enrolado), usa os pontos do
    esqueleto mais afastados entre si.
    """
    out = []
    for j, sl in enumerate(ndi.find_objects(lab)[:n], start=1):
        r0, c0 = sl[0].start, sl[1].start
        m = np.pad(lab[sl] == j, 1)
        sk = skeletonize(m)
        pts = np.argwhere(sk)
        if len(pts) == 0:
            pts = np.argwhere(m)
        nb = ndi.convolve(sk.astype(int), np.ones((3, 3), int), mode="constant") - 1
        ends = np.argwhere(sk & (nb == 1))
        cand = ends if len(ends) >= 2 else pts
        if len(cand) > 60:  # limita o custo do par mais distante
            cand = cand[:: len(cand) // 60 + 1]
        d = np.linalg.norm(cand[:, None] - cand[None], axis=2)
        a, b = np.unravel_index(np.argmax(d), d.shape)
        out.append(np.array([cand[a], cand[b]], float) - 1 + [r0, c0])
    return out


class Tracker:
    """Associacao quadro a quadro (algoritmo hungaro, distancia entre centroides).

    Cada trilha guarda o historico completo de uma ponta do verme (ancora), nao do centroide.
    A ponta escolhida em cada quadro e a mais proxima da ancora anterior, mantendo a mesma ponta.
    Trilhas encerradas vao para `finished` e continuam desenhadas.
    """

    def __init__(self, max_dist=40.0, max_missed=5):
        self.max_dist, self.max_missed = max_dist, max_missed
        self.tracks = {}  # id -> dict(pos, missed, trail)
        self.finished = []  # trajetorias de trilhas encerradas: (id, [pontos])
        self.next_id = 1

    def update(self, cents, ends):
        ids = list(self.tracks)
        assigned = {}
        if ids and len(cents):
            cost = np.linalg.norm(
                np.array([self.tracks[i]["pos"] for i in ids])[:, None] - cents[None], axis=2
            )
            r, c = linear_sum_assignment(cost)
            for i, j in zip(r, c):
                if cost[i, j] <= self.max_dist:
                    assigned[j] = ids[i]
        for j, c in enumerate(cents):
            if j in assigned:
                t = self.tracks[assigned[j]]
                prev = t["trail"][-1]
                anchor = min(ends[j], key=lambda e: np.linalg.norm(e - prev))
                t["pos"], t["missed"] = c, 0
            else:
                assigned[j] = self.next_id
                anchor = ends[j][0]
                self.tracks[self.next_id] = dict(pos=c, missed=0, trail=[])
                self.next_id += 1
            self.tracks[assigned[j]]["trail"].append(anchor)
        used = set(assigned.values())
        for i in ids:
            if i not in used:
                self.tracks[i]["missed"] += 1
                if self.tracks[i]["missed"] > self.max_missed:
                    self.finished.append((i, self.tracks.pop(i)["trail"]))
        return assigned  # indice do componente -> id
