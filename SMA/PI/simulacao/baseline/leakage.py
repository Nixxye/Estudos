"""
Gerador de traços sintéticos para o alvo AES iterativo.

Modelo: em cada ciclo t o consumo é a distância de Hamming entre o valor anterior e o novo
do registrador de estado de 128 bits, mais ruído gaussiano de desvio `sigma`.
O registrador é zerado antes de cada cifragem, então o ciclo 0 vale HW(plaintext XOR K0).

IMPORTANTE: a simulação não tem ruído natural. `sigma` é escolhido por nós; os números
absolutos de "traços até divulgação" dependem dele. Só comparações relativas são robustas.
"""
import numpy as np

from aes_target import HW

N_CYCLES = 11  # ciclos 0..10


def hd_signal(states):
    """states: (N, 11, 16). Devolve (N, 11) = HD do registrador a cada ciclo (sem ruído)."""
    prev = np.concatenate([np.zeros_like(states[:, :1]), states[:, :-1]], axis=1)
    return HW[states ^ prev].sum(axis=2).astype(np.float64)


def hw_signal(states):
    """Modelo alternativo (mais pobre): peso de Hamming do valor do registrador."""
    return HW[states].sum(axis=2).astype(np.float64)


def make_traces(states, sigma, rng, model="hd", quant_bits=None):
    sig = hd_signal(states) if model == "hd" else hw_signal(states)
    traces = sig + rng.normal(0.0, sigma, sig.shape)
    if quant_bits is not None:
        traces = quantize(traces, quant_bits)
    return traces


def quantize(traces, bits, lo=-30.0, hi=160.0):
    """Imita um conversor analógico-digital de `bits` bits com faixa fixa [lo, hi]."""
    levels = 2 ** bits - 1
    x = np.clip(traces, lo, hi)
    q = np.round((x - lo) / (hi - lo) * levels)
    return q / levels * (hi - lo) + lo
