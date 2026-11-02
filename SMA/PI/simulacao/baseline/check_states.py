"""Confere se os estados gravados pela simulação temporizada batem com o modelo Python."""
import sys
import numpy as np
from aes_target import encrypt_states, hex_to_bytes

KEY = hex_to_bytes("000102030405060708090a0b0c0d0e0f")
states_file, pts_file = sys.argv[1], sys.argv[2]
pts = np.array([hex_to_bytes(l.strip()) for l in open(pts_file) if l.strip()])
rows = [l.split() for l in open(states_file) if l.strip()]
got = np.array([[np.frombuffer(bytes.fromhex(h), dtype=np.uint8) for h in r] for r in rows])
ref = encrypt_states(pts[:len(got)], KEY)
ok = bool((got == ref).all())
print(f"{len(got)} cifragens; estados iguais ao modelo Python em todos os ciclos: {ok}")
sys.exit(0 if ok else 1)
