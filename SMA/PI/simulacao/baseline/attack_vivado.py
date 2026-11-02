"""
Ataque CPA sobre os TRAÇOS GERADOS PELO VIVADO (potência por janela via report_power).

Entrada:  ../vivado/sim<N>/power_windows.csv  (enc, win, vccint_dyn_A, ...)
          ../vivado/sim<N>/states_timing.txt   (estados do registrador, só para conferir/derivar o texto cifrado)
Janelas por cifragem: 0 = limpeza (reset), 1 = carga (ciclo 0), 2..11 = rodadas 1..10.
Uso:  python attack_vivado.py 500 [coluna]      (coluna padrão: vccint_dyn_A)
"""
import csv
import os
import sys

import numpy as np

from aes_target import HW, INV_SBOX, SR_SRC, encrypt_states, hex_to_bytes, invert_key_schedule, key_expansion
from cpa import GUESSES, _corr_columns

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = hex_to_bytes("000102030405060708090a0b0c0d0e0f")


def load(n, col="vccint_dyn_A"):
    d = os.path.join(HERE, "..", "vivado", f"sim{n}")
    pts = np.array([hex_to_bytes(l.strip()) for l in open(os.path.join(d, "pts.hex")) if l.strip()])
    rows = list(csv.DictReader(open(os.path.join(d, "power_windows.csv"))))
    ne = max(int(r["enc"]) for r in rows) + 1
    P = np.zeros((ne, 12))
    for r in rows:
        P[int(r["enc"]), int(r["win"])] = float(r[col if col in r else "vccint_dyn_A"])
    return pts[:ne], P


def attack_window(ct, traces, win, n):
    """CPA na última rodada usando uma janela; devolve K10 candidata e correlação do palpite vencedor."""
    tr = traces[:n, [win]]
    guess = np.zeros(16, dtype=np.uint8)
    for p in range(16):
        j = SR_SRC[p]
        prev = INV_SBOX[ct[:n, p][:, None] ^ GUESSES[None, :]]
        hyp = HW[prev ^ ct[:n, j][:, None]].astype(np.float64)
        guess[p] = _corr_columns(hyp, tr).ravel().argmax()
    return guess


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 500
    col = sys.argv[2] if len(sys.argv) > 2 else "vccint_dyn_A"
    pts, P = load(n, col)
    ne = len(pts)
    st = encrypt_states(pts, KEY)
    ct = st[:, 10]
    k10 = key_expansion(KEY)[10]
    print(f"{ne} cifragens, coluna {col}")
    print("janela | bytes de K10 corretos com N =", [50, 100, 200, 300, ne])
    for win in range(12):
        row = []
        for nn in (50, 100, 200, 300, ne):
            nn = min(nn, ne)
            g = attack_window(ct, P, win, nn)
            row.append(int((g == k10).sum()))
        print(f"  {win:2d}   | {row}")
    best = attack_window(ct, P, 11, ne)
    print("K10 recuperada na janela 11:", bytes(best.tolist()).hex(), "| correta:", bytes(k10.tolist()).hex())
    print("chave mestra recuperada:", bytes(invert_key_schedule(best).tolist()).hex(),
          "| correta:", bytes(KEY.tolist()).hex())


if __name__ == "__main__":
    main()
