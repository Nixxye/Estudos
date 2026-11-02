"""
Análise da rodada noturna: ataques CPA sobre os traços de potência do Vivado, por variante.

Uso:  python analyze_overnight.py <N> <janelas separadas por vírgula> <variants.conf>
Entrada:  ../vivado/sim_<variante>_<N>/power.csv
Saída:    ../vivado/overnight/RESUMO.md, results_overnight.json, overnight.png

Hipóteses (todas usam só plaintext/ciphertext conhecidos e um palpite g para um byte da chave):
  K0 @ janela 1  (carga):
     reg_load  : HW(pt ^ g)                      -> distância de Hamming do registrador (0 -> pt^k)
     sbox_load : HW(SBOX[pt ^ g] ^ 0x63)         -> saída combinacional da S-box (SB(0)=0x63 -> SB(pt^k))
  K10 @ janela 11 (última rodada):
     reg_last  : HD(s9, s10) da faixa            -> hipótese do baseline (registrador)
     sbox_last : HW((ct_p ^ g) ^ SBOX[ct_j])     -> saída da S-box passa de SB(s9) para SB(ct)
"""
import csv
import json
import os
import sys

import numpy as np

from aes_target import HW, INV_SBOX, SBOX, SR_SRC, encrypt_states, hex_to_bytes, key_expansion

HERE = os.path.dirname(os.path.abspath(__file__))
VIV = os.path.normpath(os.path.join(HERE, "..", "vivado"))
KEY = hex_to_bytes("000102030405060708090a0b0c0d0e0f")
G = np.arange(256, dtype=np.uint8)
GRID = [100, 200, 400, 800, 1600, 3200, 5000, 8000]
BOOT = 20


def load_power(path, win, n):
    P = np.full(n, np.nan)
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if int(r["win"]) == win and int(r["enc"]) < n:
                P[int(r["enc"])] = float(r["vccint_dyn_A"])
    ok = ~np.isnan(P)
    return P, ok


def hypotheses(pts, ct):
    """Devolve {nome: (janela, chave_verdadeira, função p -> matriz (N,256))}."""
    k0 = KEY
    k10 = key_expansion(KEY)[10]
    h = {}
    h["reg_load"] = (1, k0, lambda p: HW[pts[:, p][:, None] ^ G[None, :]])
    h["sbox_load"] = (1, k0, lambda p: HW[SBOX[pts[:, p][:, None] ^ G[None, :]] ^ 0x63])
    h["reg_last"] = (11, k10, lambda p: HW[INV_SBOX[ct[:, p][:, None] ^ G[None, :]] ^ ct[:, SR_SRC[p]][:, None]])
    h["sbox_last"] = (11, k10, lambda p: HW[(ct[:, p][:, None] ^ G[None, :]) ^ SBOX[ct[:, SR_SRC[p]]][:, None]])
    return h


def corr_cols(H, y):
    h = H.astype(np.float64)
    h -= h.mean(0)
    yy = y - y.mean()
    num = h.T @ yy
    den = np.sqrt((h ** 2).sum(0) * (yy ** 2).sum()) + 1e-18
    return num / den


def attack(Hs, y, idx):
    return np.array([corr_cols(Hs[p][idx], y[idx]).argmax() for p in range(16)])


def n_from_rho(rho, z=3.719):
    rho = max(min(rho, 0.999), 1e-6)
    return 3 + 8 * (z / np.log((1 + rho) / (1 - rho))) ** 2


def main():
    n = int(sys.argv[1])
    wins = [int(x) for x in sys.argv[2].split(",")]
    conf = sys.argv[3]
    names = []
    for line in open(conf):
        line = line.strip()
        if line and not line.startswith("#"):
            names.append(line.split("|")[0].strip())
    pts = np.array([hex_to_bytes(l.strip()) for l in open(os.path.join(VIV, "overnight", f"pts_{n}.hex")) if l.strip()])
    st = encrypt_states(pts, KEY)
    ct = st[:, 10]
    hyp = hypotheses(pts, ct)
    rng = np.random.default_rng(7)
    res = {}
    series = {}
    for name in names:
        path = os.path.join(VIV, f"sim_{name}_{n}", "power.csv")
        if not os.path.exists(path):
            continue
        res[name] = {}
        for hname, (win, true, fn) in hyp.items():
            if win not in wins:
                continue
            y, ok = load_power(path, win, n)
            idx_all = np.where(ok)[0]
            if len(idx_all) < 50:
                continue
            Hs = [fn(p) for p in range(16)]
            yy = y.copy()
            yy[~ok] = 0
            # força do vazamento: correlação do palpite certo (com todas as cifragens)
            rho = np.array([corr_cols(Hs[p][idx_all], yy[idx_all])[true[p]] for p in range(16)])
            guess = attack(Hs, yy, idx_all)
            rank_ok = int((guess == true).sum())
            curve = {}
            for g in GRID:
                if g > len(idx_all):
                    continue
                if g == len(idx_all):
                    subs = [idx_all]
                else:
                    subs = [rng.choice(idx_all, g, replace=False) for _ in range(BOOT)]
                full, byt = 0, 0
                for s in subs:
                    gs = attack(Hs, yy, s)
                    full += int((gs == true).all())
                    byt += int((gs == true).sum())
                curve[g] = (full / len(subs), byt / len(subs))
            ttd = next((g for g, (f, _) in curve.items() if f >= 0.9), None)
            res[name][hname] = {
                "janela": win, "n_usado": int(len(idx_all)),
                "rho_medio": float(rho.mean()), "rho_min": float(rho.min()),
                "bytes_certos_total": rank_ok,
                "N_estimado_rho_medio": float(n_from_rho(rho.mean())),
                "N_estimado_rho_min": float(n_from_rho(rho.min())),
                "curva_N_sucesso_bytes": {str(k): v for k, v in curve.items()},
                "TTD90": ttd,
            }
            series[(name, hname)] = curve
            print(name, hname, "rho=%.3f" % rho.mean(), "bytes certos:", rank_ok, "TTD90:", ttd, flush=True)
        # estatística do traço
        for win in wins:
            y, ok = load_power(path, win, n)
            res[name][f"stat_janela_{win}"] = {"media_A": float(np.nanmean(y)), "desvio_A": float(np.nanstd(y)),
                                              "valores_distintos": int(len(set(np.round(y[ok], 7))))}
    # correlação entre variantes nas mesmas cifragens (efeito da compilação)
    cross = {}
    for win in wins:
        cols = {}
        for name in res:
            y, ok = load_power(os.path.join(VIV, f"sim_{name}_{n}", "power.csv"), win, n)
            cols[name] = (y, ok)
        for a in cols:
            for b in cols:
                if a < b:
                    ok = cols[a][1] & cols[b][1]
                    if ok.sum() > 10:
                        cross[f"{a} x {b} (janela {win})"] = float(np.corrcoef(cols[a][0][ok], cols[b][0][ok])[0, 1])
    out = os.path.join(VIV, "overnight")
    os.makedirs(out, exist_ok=True)
    json.dump({"n": n, "janelas": wins, "resultados": res, "correlacao_entre_variantes": cross},
              open(os.path.join(out, "results_overnight.json"), "w"), indent=2)

    # resumo em Markdown
    L = ["# Resumo da rodada noturna", "", f"Cifragens por variante: {n}. Janelas: {wins}. Métrica de potência: corrente dinâmica Vccint (A).", ""]
    L.append("## Força do vazamento e ataque, por variante e hipótese")
    L.append("")
    L.append("| variante | hipótese | janela | ρ médio do palpite certo | ρ mínimo | bytes certos (todas as cifragens) | N estimado (ρ médio) | N estimado (ρ mín.) | TTD90 (grade) |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for name, d in res.items():
        for hname, v in d.items():
            if hname.startswith("stat"):
                continue
            L.append(f"| {name} | {hname} | {v['janela']} | {v['rho_medio']:+.3f} | {v['rho_min']:+.3f} | {v['bytes_certos_total']}/16 | {v['N_estimado_rho_medio']:.0f} | {v['N_estimado_rho_min']:.0f} | {v['TTD90']} |")
    L += ["", "## Variação da corrente entre cifragens (mesma janela)", "", "| variante | janela | média (mA) | desvio (µA) | valores distintos |", "|---|---|---|---|---|"]
    for name, d in res.items():
        for k, v in d.items():
            if k.startswith("stat"):
                L.append(f"| {name} | {k.split('_')[-1]} | {v['media_A']*1e3:.3f} | {v['desvio_A']*1e6:.1f} | {v['valores_distintos']} |")
    L += ["", "## Correlação entre variantes nas mesmas cifragens", "", "| par | correlação |", "|---|---|"]
    for k, v in cross.items():
        L.append(f"| {k} | {v:+.3f} |")
    L += ["", "## Curvas (taxa de sucesso da chave inteira por N e bytes certos médios)", ""]
    for (name, hname), curve in series.items():
        L.append(f"- **{name} / {hname}**: " + ", ".join(f"N={g}: {f:.2f} ({b:.1f}/16)" for g, (f, b) in curve.items()))
    L += ["", "Leitura: ρ é a correlação do palpite certo; 'N estimado' usa N ≈ 3 + 8·(z/ln((1+ρ)/(1−ρ)))² com z = 3,719 e vale só como ordem de grandeza (hipótese gaussiana).",
          "Todos os resultados vêm da estimativa de potência do Vivado (SAIF da simulação temporizada), não de medição física."]
    open(os.path.join(out, "RESUMO.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 2, figsize=(13, 4.5))
        for (name, hname), curve in series.items():
            tgt = ax[0] if hname.endswith("_load") else ax[1]
            if hname.startswith("sbox"):
                tgt.semilogx(list(curve.keys()), [b for _, b in curve.values()], "o-", label=f"{name}")
        ax[0].set(title="K0 (carga), hipótese S-box: bytes certos", xlabel="nº de cifragens", ylabel="bytes certos de 16")
        ax[1].set(title="K10 (última rodada), hipótese S-box: bytes certos", xlabel="nº de cifragens")
        ax[0].legend(); ax[1].legend()
        fig.tight_layout(); fig.savefig(os.path.join(out, "overnight.png"), dpi=120)
    except Exception as e:  # noqa: BLE001
        print("gráfico não gerado:", e)
    print("OK ->", os.path.join(out, "RESUMO.md"))


if __name__ == "__main__":
    main()
