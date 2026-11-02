"""Segmentacao classica (PDI): fundo por mediana temporal -> gaussiano -> Otsu -> morfologia."""
import numpy as np
from scipy import ndimage as ndi

from common import clean_and_label, load_frame, n_frames


def otsu(img):
    """Limiar de Otsu (maximiza a variancia entre classes) para imagem uint8."""
    hist = np.bincount(img.ravel(), minlength=256).astype(float)
    p = hist / hist.sum()
    w0 = np.cumsum(p)
    mu = np.cumsum(p * np.arange(256))
    sb = (mu[-1] * w0 - mu) ** 2 / np.maximum(w0 * (1 - w0), 1e-12)
    return int(np.argmax(sb))


def estimate_background(seq, n=40):
    """Os vermes se movem, a placa nao: a mediana de varios quadros remove os vermes."""
    idx = np.linspace(0, n_frames(seq) - 1, n).astype(int)
    return np.median(np.stack([load_frame(seq, k) for k in idx]), axis=0).astype(np.float32)


def segment(frame, bg, sigma=1.0):
    """Mascara binaria dos vermes (escuros sobre fundo claro)."""
    diff = np.clip(bg - frame.astype(np.float32), 0, 255)  # so o que ficou mais escuro
    diff = ndi.gaussian_filter(diff, sigma)
    d8 = np.clip(diff * 4, 0, 255).astype(np.uint8)  # realce de contraste antes do Otsu
    t = max(otsu(d8), 40)  # piso evita limiar absurdo em quadros sem vermes
    return d8 > t


def run(seq, k, bg):
    mask = segment(load_frame(seq, k), bg)
    return clean_and_label(mask)
