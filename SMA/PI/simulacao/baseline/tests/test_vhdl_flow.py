"""Valida o alvo B (VHDL no GHDL) contra o alvo A. Pula se o GHDL não estiver disponível."""
import glob
import os
import shutil
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import vhdl_flow  # noqa: E402
from aes_target import encrypt_states, hex_to_bytes  # noqa: E402


def _ghdl():
    cands = [os.environ.get("GHDL"), shutil.which("ghdl")]
    cands += glob.glob(os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\ghdl*\bin\ghdl.exe"))
    for c in cands:
        if c and os.path.exists(c):
            return c
    return None


@unittest.skipIf(_ghdl() is None, "GHDL não encontrado")
class TestVhdl(unittest.TestCase):
    def test_vhdl_states_equal_python_states(self):
        key = hex_to_bytes(vhdl_flow.KEY_HEX)
        pts = np.random.default_rng(5).integers(0, 256, (200, 16), dtype=np.uint8)
        pts[0] = hex_to_bytes("00112233445566778899aabbccddeeff")
        got = vhdl_flow.run_vhdl(_ghdl(), vhdl_flow.KEY_HEX, pts)
        ref = encrypt_states(pts, key)
        self.assertTrue((got == ref).all())
        self.assertEqual(bytes(got[0, 10]).hex(), "69c4e0d86a7b0430d8cdb78070b4c55a")


if __name__ == "__main__":
    unittest.main()
