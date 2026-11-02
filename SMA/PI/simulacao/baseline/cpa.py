"""
Ataques CPA contra o alvo AES iterativo (modelo de vazamento: distância de Hamming do
registrador de estado). O atacante conhece o algoritmo, os textos de entrada, os textos
cifrados e os traços. Não conhece a chave.

Dois pontos de ataque:
  - última rodada (ciclo 10): recupera K10 byte a byte e inverte o escalonamento de chave;
  - carga inicial (ciclo 0):  recupera K0 (a chave mestra) diretamente.
"""
import numpy as np

from aes_target import HW, INV_SBOX, SR_SRC, invert_key_schedule

GUESSES = np.arange(256, dtype=np.uint8)


def _corr_columns(hyp, traces):
    """Correlação de Pearson entre cada coluna de hyp (N,G) e cada coluna de traces (N,S)."""
    h = hyp - hyp.mean(axis=0)
    t = traces - traces.mean(axis=0)
    h /= np.sqrt((h ** 2).sum(axis=0)) + 1e-12
    t /= np.sqrt((t ** 2).sum(axis=0)) + 1e-12
    return h.T @ t  # (G, S)


def scores_last_round(ct, traces, samples=(10,), wrong_model=False):
    """Pontuação (16, 256): para cada byte de K10 e cada palpite, a maior correlação (com sinal).
    Usar o sinal (consumo cresce com o nº de bits que mudam) elimina a ambiguidade g contra ~g.
    ct: (N,16) textos cifrados; traces: (N, nº de ciclos)."""
    tr = traces[:, list(samples)]
    scores = np.empty((16, 256))
    for p in range(16):
        j = SR_SRC[p]
        prev_lane = INV_SBOX[ct[:, p][:, None] ^ GUESSES[None, :]]  # byte j do estado da rodada 9
        if wrong_model:   # atacante usa HW em vez de HD (modelo errado)
            hyp = HW[prev_lane]
        else:
            hyp = HW[prev_lane ^ ct[:, j][:, None]]
        scores[p] = _corr_columns(hyp.astype(np.float64), tr).max(axis=1)
    return scores


def scores_first_round(pt, traces, samples=(0,)):
    """Pontuação (16, 256) para K0 usando a carga inicial: HW(pt XOR K0) no ciclo 0."""
    tr = traces[:, list(samples)]
    scores = np.empty((16, 256))
    for p in range(16):
        hyp = HW[pt[:, p][:, None] ^ GUESSES[None, :]].astype(np.float64)
        scores[p] = _corr_columns(hyp, tr).max(axis=1)
    return scores


def best_key(scores):
    return scores.argmax(axis=1).astype(np.uint8)


def recover_master_key(ct, traces, **kw):
    """Ataque completo à última rodada: devolve (K10 candidata, chave mestra candidata)."""
    k10 = best_key(scores_last_round(ct, traces, **kw))
    return k10, invert_key_schedule(k10)


def key_ranks(scores, true_key):
    """Posição (0 = melhor) do palpite correto em cada byte."""
    order = np.argsort(-scores, axis=1)
    return np.array([int(np.where(order[p] == true_key[p])[0][0]) for p in range(16)])
