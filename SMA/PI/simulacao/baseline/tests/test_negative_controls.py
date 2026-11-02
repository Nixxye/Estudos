"""Controles negativos: o ataque NÃO pode acertar quando não há vazamento utilizável."""
import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from aes_target import encrypt_states, hex_to_bytes, key_expansion  # noqa: E402
from cpa import best_key, scores_first_round, scores_last_round  # noqa: E402
from leakage import make_traces  # noqa: E402
from metrics import random_plaintexts, tvla  # noqa: E402

KEY = hex_to_bytes("000102030405060708090a0b0c0d0e0f")


class TestNegativeControls(unittest.TestCase):
    def setUp(self):
        self.rng = np.random.default_rng(11)
        self.n = 1000
        self.pt = random_plaintexts(self.n, self.rng)
        self.st = encrypt_states(self.pt, KEY)

    def test_positive_control_recovers_key(self):
        tr = make_traces(self.st, 2.0, self.rng)
        k10 = best_key(scores_last_round(self.st[:, 10], tr))
        self.assertTrue((k10 == key_expansion(KEY)[10]).all())

    def test_shuffled_traces_do_not_leak(self):
        tr = make_traces(self.st, 2.0, self.rng)
        tr = tr[self.rng.permutation(self.n)]          # quebra a associação texto-traço
        k10 = best_key(scores_last_round(self.st[:, 10], tr))
        self.assertLess(int((k10 == key_expansion(KEY)[10]).sum()), 3)

    def test_huge_noise_few_traces_fails(self):
        st = self.st[:50]
        tr = make_traces(st, 500.0, self.rng)
        k10 = best_key(scores_last_round(st[:, 10], tr))
        self.assertLess(int((k10 == key_expansion(KEY)[10]).sum()), 3)

    def test_other_device_key_is_not_matched(self):
        """Traços de OUTRA chave: o ataque não pode devolver a chave do alvo original."""
        other = hex_to_bytes("ffeeddccbbaa99887766554433221100")
        st2 = encrypt_states(self.pt, other)
        tr = make_traces(st2, 2.0, self.rng)
        k10 = best_key(scores_last_round(st2[:, 10], tr))
        self.assertLess(int((k10 == key_expansion(KEY)[10]).sum()), 3)
        self.assertTrue((k10 == key_expansion(other)[10]).all())

    def test_first_round_wrong_cycle_fails(self):
        tr = make_traces(self.st, 2.0, self.rng)
        k0 = best_key(scores_first_round(self.pt, tr, samples=(5,)))
        self.assertLess(int((k0 == KEY).sum()), 3)

    def test_tvla_detects_leak_and_not_null(self):
        t = tvla(KEY, 5.0, 2000, self.rng)
        self.assertGreater(np.abs(t).max(), 4.5)
        # nulo: mesmas distribuições (ambos aleatórios) não deve exceder muito 4,5
        a = make_traces(encrypt_states(random_plaintexts(2000, self.rng), KEY), 5.0, self.rng)
        b = make_traces(encrypt_states(random_plaintexts(2000, self.rng), KEY), 5.0, self.rng)
        tn = (a.mean(0) - b.mean(0)) / np.sqrt(a.var(0, ddof=1) / 2000 + b.var(0, ddof=1) / 2000)
        self.assertLess(np.abs(tn).max(), 4.5)


if __name__ == "__main__":
    unittest.main()
