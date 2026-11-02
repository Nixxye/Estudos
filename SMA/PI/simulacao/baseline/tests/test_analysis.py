"""Testes das funções de análise da rodada noturna (hipóteses, ataque e leitura do CSV do Vivado)."""
import csv
import os
import sys
import tempfile
import unittest

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from aes_target import HW, SBOX, encrypt_states, hex_to_bytes, key_expansion  # noqa: E402
from analyze_overnight import attack, corr_cols, hypotheses, load_power, n_from_rho  # noqa: E402

KEY = hex_to_bytes("000102030405060708090a0b0c0d0e0f")


def _data(n, seed):
    rng = np.random.default_rng(seed)
    pts = rng.integers(0, 256, (n, 16), dtype=np.uint8)
    st = encrypt_states(pts, KEY)
    return pts, st


class TestAnalysis(unittest.TestCase):
    def test_sbox_load_hypothesis_recovers_k0_on_synthetic_leak(self):
        pts, st = _data(1500, 1)
        # vazamento sintético: saída da S-box muda de SB(0)=0x63 para SB(pt^k), soma dos 16 bytes + ruído
        y = HW[SBOX[st[:, 0]] ^ 0x63].sum(axis=1).astype(float)
        y += np.random.default_rng(2).normal(0, 2.0, len(y))
        hyp = hypotheses(pts, st[:, 10])
        win, true, fn = hyp["sbox_load"]
        Hs = [fn(p) for p in range(16)]
        guess = attack(Hs, y, np.arange(len(y)))
        self.assertEqual(win, 1)
        self.assertTrue((guess == true).all())

    def test_reg_last_hypothesis_recovers_k10_on_synthetic_leak(self):
        pts, st = _data(1500, 3)
        y = HW[st[:, 9] ^ st[:, 10]].sum(axis=1).astype(float)
        y += np.random.default_rng(4).normal(0, 2.0, len(y))
        hyp = hypotheses(pts, st[:, 10])
        win, true, fn = hyp["reg_last"]
        Hs = [fn(p) for p in range(16)]
        guess = attack(Hs, y, np.arange(len(y)))
        self.assertEqual(win, 11)
        self.assertTrue((guess == true).all())
        self.assertTrue((true == key_expansion(KEY)[10]).all())

    def test_shuffled_power_does_not_recover_key(self):
        pts, st = _data(1500, 5)
        y = HW[SBOX[st[:, 0]] ^ 0x63].sum(axis=1).astype(float)
        y = np.random.default_rng(6).permutation(y)
        hyp = hypotheses(pts, st[:, 10])
        _, true, fn = hyp["sbox_load"]
        guess = attack([fn(p) for p in range(16)], y, np.arange(len(y)))
        self.assertLess(int((guess == true).sum()), 3)

    def test_load_power_reads_requested_window_only(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "power.csv")
            with open(path, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["enc", "win", "vccint_dyn_A", "vccint_total_A", "vccbram_dyn_A"])
                for e in range(4):
                    w.writerow([e, 1, 0.01 * (e + 1), 0.0, 0.0])
                    w.writerow([e, 11, 0.5, 0.0, 0.0])
            y, ok = load_power(path, 1, 6)
            self.assertEqual(int(ok.sum()), 4)
            self.assertAlmostEqual(y[2], 0.03)
            self.assertTrue(np.isnan(y[5]))

    def test_corr_cols_matches_numpy(self):
        rng = np.random.default_rng(9)
        H = rng.integers(0, 9, (200, 5)).astype(float)
        y = rng.normal(size=200)
        ref = np.array([np.corrcoef(H[:, i], y)[0, 1] for i in range(5)])
        self.assertTrue(np.allclose(corr_cols(H, y), ref, atol=1e-9))

    def test_n_from_rho_is_monotonic(self):
        self.assertGreater(n_from_rho(0.05), n_from_rho(0.2))
        self.assertGreater(n_from_rho(0.2), n_from_rho(0.5))


if __name__ == "__main__":
    unittest.main()
