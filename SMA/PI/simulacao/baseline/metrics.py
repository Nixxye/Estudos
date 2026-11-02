"""Métricas de avaliação: taxa de sucesso, traços até divulgação, classificação da chave e TVLA."""
import numpy as np

from aes_target import encrypt_states, key_expansion
from cpa import best_key, key_ranks, scores_first_round, scores_last_round
from leakage import make_traces


def random_plaintexts(n, rng):
    return rng.integers(0, 256, (n, 16), dtype=np.uint8)


def success_curve(key, sigma, ns, reps, rng, attack="last", model="hd", quant_bits=None,
                  wrong_model=False):
    """Para cada N em `ns`, fração de repetições em que a chave (K10 ou K0) foi recuperada
    por inteiro, e nº médio de bytes corretos. Cada repetição usa textos e ruído novos."""
    true = key_expansion(key)[10 if attack == "last" else 0]
    n_max = max(ns)
    full = np.zeros(len(ns))
    bytes_ok = np.zeros(len(ns))
    for _ in range(reps):
        pt = random_plaintexts(n_max, rng)
        st = encrypt_states(pt, key)
        tr = make_traces(st, sigma, rng, model=model, quant_bits=quant_bits)
        ct = st[:, 10]
        for i, n in enumerate(ns):
            if attack == "last":
                sc = scores_last_round(ct[:n], tr[:n], wrong_model=wrong_model)
            else:
                sc = scores_first_round(pt[:n], tr[:n])
            guess = best_key(sc)
            ok = guess == true
            full[i] += ok.all()
            bytes_ok[i] += ok.sum()
    return full / reps, bytes_ok / reps


def traces_to_disclosure(ns, sr, target=0.9):
    """Menor N da grade com taxa de sucesso >= target (None se nenhum alcançar)."""
    for n, s in zip(ns, sr):
        if s >= target:
            return n
    return None


def rank_curve(key, sigma, ns, reps, rng):
    """Classificação média (0 = melhor) do byte correto de K10, média sobre bytes e repetições."""
    true = key_expansion(key)[10]
    n_max = max(ns)
    out = np.zeros(len(ns))
    for _ in range(reps):
        pt = random_plaintexts(n_max, rng)
        st = encrypt_states(pt, key)
        tr = make_traces(st, sigma, rng)
        for i, n in enumerate(ns):
            out[i] += key_ranks(scores_last_round(st[:n, 10], tr[:n]), true).mean()
    return out / reps


def tvla(key, sigma, n, rng, fixed_pt=None):
    """TVLA fixo contra aleatório: estatística t de Welch por ciclo. |t| > 4,5 indica vazamento."""
    if fixed_pt is None:
        fixed_pt = np.zeros(16, dtype=np.uint8)
    pt_f = np.tile(fixed_pt, (n, 1))
    pt_r = random_plaintexts(n, rng)
    tr_f = make_traces(encrypt_states(pt_f, key), sigma, rng)
    tr_r = make_traces(encrypt_states(pt_r, key), sigma, rng)
    mf, mr = tr_f.mean(0), tr_r.mean(0)
    vf, vr = tr_f.var(0, ddof=1), tr_r.var(0, ddof=1)
    return (mf - mr) / np.sqrt(vf / n + vr / n + 1e-12)
