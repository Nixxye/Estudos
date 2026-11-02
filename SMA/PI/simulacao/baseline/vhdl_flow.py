"""
Fluxo do alvo B (VHDL): simula o AES em GHDL, lê o estado do registrador a cada ciclo,
valida contra o alvo A (Python) e roda o MESMO ataque sobre os estados vindos do VHDL.

Uso (a partir desta pasta):
    python vhdl_flow.py --n 2000 --validate-only
    python vhdl_flow.py --n 20000 --sigma 10 --reps 40

Requer o GHDL no PATH (ou --ghdl caminho\\ghdl.exe, ou variável de ambiente GHDL).
Os arquivos temporários ficam em build_vhdl/.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time

import numpy as np

from aes_target import bytes_to_hex, encrypt_states, hex_to_bytes
from cpa import best_key, scores_last_round
from leakage import make_traces
from metrics import random_plaintexts, traces_to_disclosure

HERE = os.path.dirname(os.path.abspath(__file__))
VHDL_DIR = os.path.normpath(os.path.join(HERE, "..", "vhdl"))
BUILD = os.path.join(HERE, "build_vhdl")
RESULTS = os.path.join(HERE, "results")
SOURCES = ["aes_sbox_pkg.vhd", "aes_pkg.vhd", "aes_iter.vhd", "tb_aes.vhd"]
KEY_HEX = "000102030405060708090a0b0c0d0e0f"


def find_ghdl(explicit=None):
    cands = [explicit, os.environ.get("GHDL"), shutil.which("ghdl")]
    for c in cands:
        if c and os.path.exists(c):
            return c
        if c and shutil.which(c):
            return shutil.which(c)
    sys.exit("GHDL não encontrado. Instale-o ou passe --ghdl <caminho>.")


def run_vhdl(ghdl, key_hex, pts):
    """Simula o VHDL para os plaintexts `pts` (N,16) e devolve estados (N, 11, 16) uint8."""
    os.makedirs(BUILD, exist_ok=True)
    work = os.path.join(BUILD, "work")
    os.makedirs(work, exist_ok=True)
    with open(os.path.join(BUILD, "stim.txt"), "w") as f:
        f.write(key_hex + "\n")
        for p in pts:
            f.write(bytes_to_hex(p) + "\n")
    srcs = [os.path.join(VHDL_DIR, s) for s in SOURCES]
    base = [ghdl]
    opts = ["--std=08", f"--workdir={work}"]

    def run(args):
        r = subprocess.run(base + args, cwd=BUILD, capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(f"GHDL falhou ({' '.join(args)}):\n{r.stdout}\n{r.stderr}")
        return r

    run(["-a"] + opts + srcs)
    run(["-e"] + opts + ["tb_aes"])
    run(["-r"] + opts + ["tb_aes"])
    states = np.empty((len(pts), 11, 16), dtype=np.uint8)
    with open(os.path.join(BUILD, "states.txt")) as f:
        lines = [ln.split() for ln in f if ln.strip()]
    if len(lines) != len(pts):
        sys.exit(f"esperava {len(pts)} linhas em states.txt, vieram {len(lines)}")
    for i, parts in enumerate(lines):
        if len(parts) != 11:
            sys.exit(f"linha {i}: {len(parts)} estados em vez de 11")
        for t, h in enumerate(parts):
            states[i, t] = np.frombuffer(bytes.fromhex(h), dtype=np.uint8)
    return states


def success_curve_pool(pool_pt, pool_states, key, sigma, ns, reps, rng):
    """Como metrics.success_curve, mas sorteando subconjuntos de um conjunto fixo de
    estados vindos do VHDL (ruído novo em cada repetição)."""
    from aes_target import key_expansion
    true = key_expansion(key)[10]
    n_max = max(ns)
    full = np.zeros(len(ns))
    for _ in range(reps):
        idx = rng.choice(len(pool_pt), n_max, replace=False)
        st = pool_states[idx]
        tr = make_traces(st, sigma, rng)
        for i, n in enumerate(ns):
            ok = best_key(scores_last_round(st[:n, 10], tr[:n])) == true
            full[i] += ok.all()
    return full / reps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ghdl", default=None)
    ap.add_argument("--n", type=int, default=20000, help="nº de cifragens simuladas em VHDL")
    ap.add_argument("--sigma", type=float, default=10.0)
    ap.add_argument("--reps", type=int, default=40)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--validate-only", action="store_true")
    args = ap.parse_args()

    ghdl = find_ghdl(args.ghdl)
    key = hex_to_bytes(KEY_HEX)
    rng = np.random.default_rng(args.seed)
    pts = random_plaintexts(args.n, rng)
    # inclui o vetor do FIPS-197 como primeira entrada
    pts[0] = hex_to_bytes("00112233445566778899aabbccddeeff")

    t0 = time.time()
    st_vhdl = run_vhdl(ghdl, KEY_HEX, pts)
    print(f"[{time.time() - t0:5.1f}s] VHDL simulado: {args.n} cifragens")
    print("texto cifrado do vetor FIPS-197:", bytes_to_hex(st_vhdl[0, 10]),
          "(esperado 69c4e0d86a7b0430d8cdb78070b4c55a)")
    st_py = encrypt_states(pts, key)
    equal = (st_vhdl == st_py).all()
    print("estados VHDL == estados Python em TODOS os ciclos:", bool(equal))
    if not equal:
        bad = np.argwhere((st_vhdl != st_py).any(axis=2))
        sys.exit(f"divergência (primeiros casos: {bad[:5].tolist()})")
    if args.validate_only:
        return

    ns = [50, 100, 200, 400, 800, 1600, 3200, 6400]
    ns = [n for n in ns if n <= args.n]
    sr = success_curve_pool(pts, st_vhdl, key, args.sigma, ns, args.reps, rng)
    ttd = traces_to_disclosure(ns, sr)
    print(f"alvo B (VHDL), sigma={args.sigma}: SR={np.round(sr, 2).tolist()} TTD90={ttd}")
    os.makedirs(RESULTS, exist_ok=True)
    with open(os.path.join(RESULTS, "experiments_vhdl.json"), "w") as f:
        json.dump({"sigma": args.sigma, "ns": ns, "reps": args.reps, "pool": args.n,
                   "sr": sr.tolist(), "ttd90": ttd, "states_equal_python": bool(equal)}, f, indent=2)


if __name__ == "__main__":
    main()
