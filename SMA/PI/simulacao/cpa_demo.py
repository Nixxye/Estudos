"""
Demo didática de CPA (Correlation Power Analysis) sobre traços SINTÉTICOS.

Não há hardware nem dispositivo real: o "dispositivo" é um modelo em que o consumo
num instante é proporcional ao peso de Hamming da saída da S-box do AES, mais ruído.
A contramedida é um desalinhamento aleatório (jitter) do instante do vazamento, que
imita de forma simplificada o efeito de técnicas de tempo aleatório (como o RFTC).

Uso:  python cpa_demo.py
"""
import numpy as np

rng = np.random.default_rng(1)


# --- S-box do AES, calculada (evita digitar a tabela) -------------------------------
def _gf_mul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        if a & 0x100:
            a ^= 0x11B
        b >>= 1
    return r


def _make_sbox():
    sbox = []
    for x in range(256):
        inv = 0
        if x:
            inv = next(y for y in range(1, 256) if _gf_mul(x, y) == 1)
        s = inv
        for i in range(1, 5):
            s ^= ((inv << i) | (inv >> (8 - i))) & 0xFF
        sbox.append(s ^ 0x63)
    return np.array(sbox, dtype=np.uint8)


SBOX = _make_sbox()
HW = np.array([bin(v).count("1") for v in range(256)], dtype=np.float64)
assert SBOX[0x00] == 0x63 and SBOX[0x53] == 0xED  # valores conhecidos do AES

# --- Parâmetros do modelo -----------------------------------------------------------
KEY_BYTE = 0x2B       # byte secreto que o "atacante" tentará descobrir
SIGMA = 2.0           # desvio do ruído gaussiano (quanto maior, mais traços são necessários)
BASE = 8              # posição do vazamento sem jitter
L = 100               # amostras por traço


def capture(n, k):
    """Gera n traços. k = nº de posições possíveis do vazamento (k=1: sem contramedida).
    Devolve (textos, traços, deslocamentos usados)."""
    pt = rng.integers(0, 256, n, dtype=np.uint8)
    leak = HW[SBOX[pt ^ KEY_BYTE]]
    shift = rng.integers(0, k, n)
    traces = rng.normal(0.0, SIGMA, (n, L))
    traces[np.arange(n), BASE + shift] += leak
    return pt, traces, shift


def cpa_best_guess(pt, traces):
    """Para cada um dos 256 palpites, correlaciona o consumo previsto com cada amostra
    do traço e guarda a maior correlação em módulo. Devolve o palpite vencedor."""
    hyp = HW[SBOX[pt[:, None] ^ np.arange(256, dtype=np.uint8)[None, :]]]  # (n, 256)
    h = (hyp - hyp.mean(0)) / (hyp.std(0) + 1e-12)
    t = (traces - traces.mean(0)) / (traces.std(0) + 1e-12)
    corr = (h.T @ t) / len(pt)                                              # (256, L)
    return int(np.argmax(np.abs(corr).max(axis=1)))


def success_rate(n, k, aligned, runs=40):
    ok = 0
    for _ in range(runs):
        pt, tr, shift = capture(n, k)
        if aligned:  # atacante ideal: conhece o deslocamento e realinha antes de correlacionar
            tr = np.stack([np.roll(tr[i], -shift[i]) for i in range(n)])
        ok += cpa_best_guess(pt, tr) == KEY_BYTE
    return ok / runs


def traces_to_disclosure(k, aligned, grid, target=0.9):
    for n in grid:
        if success_rate(n, k, aligned) >= target:
            return n
    return None


if __name__ == "__main__":
    grid = [10, 20, 40, 80, 160, 320, 640, 1280, 2560, 5120, 10240]
    print(f"Ruído sigma={SIGMA}. Byte secreto = 0x{KEY_BYTE:02X}")
    print("Menor nº de traços (da grade) com >=90% de sucesso em 40 repetições\n")
    print(f"{'k (posições)':>13} | {'sem alinhar':>12} | {'atacante alinha':>16}")
    print("-" * 49)
    for k in (1, 4, 16, 64):
        a = traces_to_disclosure(k, aligned=False, grid=grid)
        b = traces_to_disclosure(k, aligned=True, grid=grid)
        f = lambda v: f">{grid[-1]}" if v is None else str(v)
        print(f"{k:>13} | {f(a):>12} | {f(b):>16}")
