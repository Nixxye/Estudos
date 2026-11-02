"""
Experimentos do baseline (alvo estático sem proteção).  Uso:
    python run_experiments.py            # completo (alguns minutos)
    python run_experiments.py --fast     # versão rápida, para conferir o fluxo

Saídas: results/experiments_<alvo>.json e results/*.png
"""
import argparse
import json
import os
import time

import numpy as np

from aes_target import hex_to_bytes
from metrics import rank_curve, success_curve, traces_to_disclosure, tvla

KEY = hex_to_bytes("000102030405060708090a0b0c0d0e0f")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fast", action="store_true")
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--sigma", type=float, default=10.0, help="ruído do caso base")
    args = ap.parse_args()

    os.makedirs(OUT, exist_ok=True)
    rng = np.random.default_rng(args.seed)
    ns = [50, 100, 200, 400, 800, 1600, 3200, 6400]
    reps = 8 if args.fast else 40
    reps_small = 5 if args.fast else 20
    res = {"seed": args.seed, "sigma_base": args.sigma, "ns": ns, "reps": reps}
    t0 = time.time()

    def log(msg):
        print(f"[{time.time() - t0:6.1f}s] {msg}", flush=True)

    # E1 caso base
    sr, bytes_ok = success_curve(KEY, args.sigma, ns, reps, rng)
    res["E1_base"] = {"sr": sr.tolist(), "bytes_ok": bytes_ok.tolist(),
                      "ttd90": traces_to_disclosure(ns, sr)}
    log(f"E1 base sigma={args.sigma}: SR={np.round(sr, 2).tolist()} TTD90={res['E1_base']['ttd90']}")
    res["E1_rank"] = rank_curve(KEY, args.sigma, ns, reps_small, rng).tolist()

    # E2 varredura de ruído
    res["E2_sigma"] = {}
    for s in (0.0, 5.0, 10.0, 20.0):
        sr_s, _ = success_curve(KEY, s, ns, reps_small, rng)
        res["E2_sigma"][str(s)] = {"sr": sr_s.tolist(), "ttd90": traces_to_disclosure(ns, sr_s)}
        log(f"E2 sigma={s}: TTD90={res['E2_sigma'][str(s)]['ttd90']}")

    # E3 modelo certo contra errado (HD contra HW)
    sr_w, _ = success_curve(KEY, args.sigma, ns, reps_small, rng, wrong_model=True)
    res["E3_wrong_model"] = {"sr": sr_w.tolist(), "ttd90": traces_to_disclosure(ns, sr_w)}
    log(f"E3 modelo errado (HW em vez de HD): TTD90={res['E3_wrong_model']['ttd90']}")

    # E4 carga inicial (K0) contra última rodada (K10)
    sr_f, _ = success_curve(KEY, args.sigma, ns, reps_small, rng, attack="first")
    res["E4_first_round"] = {"sr": sr_f.tolist(), "ttd90": traces_to_disclosure(ns, sr_f)}
    log(f"E4 carga inicial (K0): TTD90={res['E4_first_round']['ttd90']}")

    # E5 quantização do conversor
    res["E5_quant"] = {}
    for b in (8, 4, 2):
        sr_q, _ = success_curve(KEY, args.sigma, ns, reps_small, rng, quant_bits=b)
        res["E5_quant"][str(b)] = {"sr": sr_q.tolist(), "ttd90": traces_to_disclosure(ns, sr_q)}
        log(f"E5 {b} bits: TTD90={res['E5_quant'][str(b)]['ttd90']}")

    # E6 TVLA
    t = tvla(KEY, args.sigma, 2000, rng)
    res["E6_tvla"] = {"t_per_cycle": np.round(t, 2).tolist(), "max_abs_t": float(np.abs(t).max())}
    log(f"E6 TVLA max|t|={res['E6_tvla']['max_abs_t']:.1f} (limite 4,5)")

    name = "fast" if args.fast else "full"
    with open(os.path.join(OUT, f"experiments_python_{name}.json"), "w") as f:
        json.dump(res, f, indent=2)
    plot(res, name)
    log("concluído")


def plot(res, name):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ns = res["ns"]
    fig, ax = plt.subplots(1, 3, figsize=(15, 4))
    ax[0].semilogx(ns, res["E1_base"]["sr"], "o-", label=f"σ={res['sigma_base']}")
    for s, d in res["E2_sigma"].items():
        ax[0].semilogx(ns, d["sr"], ".--", label=f"σ={s}")
    ax[0].set(xlabel="nº de traços", ylabel="taxa de sucesso (chave inteira)", title="E1/E2: ruído")
    ax[0].legend()
    ax[1].semilogx(ns, res["E1_base"]["sr"], "o-", label="última rodada, HD (base)")
    ax[1].semilogx(ns, res["E3_wrong_model"]["sr"], "s--", label="última rodada, modelo HW (errado)")
    ax[1].semilogx(ns, res["E4_first_round"]["sr"], "^--", label="carga inicial (K0)")
    ax[1].set(xlabel="nº de traços", title="E3/E4: modelo e ponto de ataque")
    ax[1].legend()
    for b, d in res["E5_quant"].items():
        ax[2].semilogx(ns, d["sr"], "o--", label=f"{b} bits")
    ax[2].semilogx(ns, res["E1_base"]["sr"], "k-", label="sem quantização")
    ax[2].set(xlabel="nº de traços", title="E5: quantização")
    ax[2].legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, f"baseline_python_{name}.png"), dpi=130)


if __name__ == "__main__":
    main()
