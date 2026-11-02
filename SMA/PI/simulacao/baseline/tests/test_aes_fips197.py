"""Valida o alvo A contra os vetores do FIPS-197 e a inversão do escalonamento de chave."""
import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from aes_target import (bytes_to_hex, encrypt, encrypt_states, hex_to_bytes,  # noqa: E402
                        invert_key_schedule, key_expansion)


class TestAes(unittest.TestCase):
    def test_fips197_c1(self):
        key = hex_to_bytes("000102030405060708090a0b0c0d0e0f")
        pt = hex_to_bytes("00112233445566778899aabbccddeeff")
        ct = encrypt(pt[None, :], key)[0]
        self.assertEqual(bytes_to_hex(ct), "69c4e0d86a7b0430d8cdb78070b4c55a")

    def test_fips197_a1_key_schedule(self):
        key = hex_to_bytes("2b7e151628aed2a6abf7158809cf4f3c")
        rks = key_expansion(key)
        self.assertEqual(bytes_to_hex(rks[10]), "d014f9a8c9ee2589e13f0cc8b6630ca6")

    def test_invert_key_schedule(self):
        rng = np.random.default_rng(3)
        for _ in range(20):
            key = rng.integers(0, 256, 16, dtype=np.uint8)
            k10 = key_expansion(key)[10]
            self.assertTrue((invert_key_schedule(k10) == key).all())

    def test_states_shape_and_last_state_is_ciphertext(self):
        key = hex_to_bytes("000102030405060708090a0b0c0d0e0f")
        pt = np.random.default_rng(1).integers(0, 256, (5, 16), dtype=np.uint8)
        st = encrypt_states(pt, key)
        self.assertEqual(st.shape, (5, 11, 16))
        self.assertTrue((st[:, 10] == encrypt(pt, key)).all())
        self.assertTrue((st[:, 0] == (pt ^ key)).all())


if __name__ == "__main__":
    unittest.main()
