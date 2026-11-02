"""
Alvo A: AES-128 iterativo (uma rodada por ciclo) modelado em Python.

O alvo expõe o valor do REGISTRADOR DE ESTADO a cada ciclo, que é a fonte de vazamento
usada no restante do projeto (distância de Hamming entre valores sucessivos do registrador).

Convenções (iguais às do FIPS-197):
  - bloco de 16 bytes, índice i = linha + 4*coluna (ordem de coluna);
  - estados[:, 0]  = plaintext XOR K0   (carga inicial)
  - estados[:, t]  = saída da rodada t, t = 1..10
  - estados[:, 10] = texto cifrado
Todas as funções trabalham em lote: o primeiro eixo é o nº de cifragens.
"""
import numpy as np


# --- S-box e tabelas auxiliares ------------------------------------------------------
def _gf_mul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        if a & 0x100:
            a ^= 0x11B
        b >>= 1
    return r


def _make_sbox():
    sbox = []
    for x in range(256):
        inv = 0
        if x:
            inv = next(y for y in range(1, 256) if _gf_mul(x, y) == 1)
        s = inv
        for i in range(1, 5):
            s ^= ((inv << i) | (inv >> (8 - i))) & 0xFF
        sbox.append(s ^ 0x63)
    return np.array(sbox, dtype=np.uint8)


SBOX = _make_sbox()
INV_SBOX = np.zeros(256, dtype=np.uint8)
INV_SBOX[SBOX] = np.arange(256, dtype=np.uint8)
HW = np.array([bin(v).count("1") for v in range(256)], dtype=np.uint8)
RCON = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36]

# ShiftRows: novo[p] = antigo[SR_SRC[p]]   (p = linha + 4*coluna)
SR_SRC = np.array([(p % 4) + 4 * (((p // 4) + (p % 4)) % 4) for p in range(16)])

assert SBOX[0x00] == 0x63 and SBOX[0x53] == 0xED
assert (INV_SBOX[SBOX] == np.arange(256)).all()


# --- Escalonamento de chave -------------------------------------------------------------
def key_expansion(key):
    """key: 16 bytes. Devolve array (11, 16) com as chaves de rodada K0..K10."""
    key = np.asarray(bytearray(key) if isinstance(key, (bytes, bytearray)) else key, dtype=np.uint8)
    w = [key[4 * i:4 * i + 4].copy() for i in range(4)]
    for i in range(4, 44):
        t = w[i - 1].copy()
        if i % 4 == 0:
            t = np.roll(t, -1)
            t = SBOX[t]
            t[0] ^= RCON[i // 4 - 1]
        w.append(w[i - 4] ^ t)
    return np.array([np.concatenate(w[4 * r:4 * r + 4]) for r in range(11)], dtype=np.uint8)


def invert_key_schedule(k10):
    """Recupera a chave mestra (K0) a partir da chave da última rodada (K10)."""
    cur = [np.asarray(k10, dtype=np.uint8)[4 * i:4 * i + 4].copy() for i in range(4)]
    for r in range(10, 0, -1):
        w0, w1, w2, w3 = cur
        p3 = w3 ^ w2
        p2 = w2 ^ w1
        p1 = w1 ^ w0
        t = SBOX[np.roll(p3, -1)].copy()
        t[0] ^= RCON[r - 1]
        p0 = w0 ^ t
        cur = [p0, p1, p2, p3]
    return np.concatenate(cur)


# --- Rodada ------------------------------------------------------------------------------
def _xtime(a):
    a = a.astype(np.uint16) << 1
    a = np.where(a & 0x100, a ^ 0x11B, a)
    return a.astype(np.uint8)


def _mix_columns(s):
    out = np.empty_like(s)
    for c in range(4):
        a0, a1, a2, a3 = (s[:, 4 * c + r] for r in range(4))
        x0, x1, x2, x3 = _xtime(a0), _xtime(a1), _xtime(a2), _xtime(a3)
        out[:, 4 * c + 0] = x0 ^ (x1 ^ a1) ^ a2 ^ a3
        out[:, 4 * c + 1] = a0 ^ x1 ^ (x2 ^ a2) ^ a3
        out[:, 4 * c + 2] = a0 ^ a1 ^ x2 ^ (x3 ^ a3)
        out[:, 4 * c + 3] = (x0 ^ a0) ^ a1 ^ a2 ^ x3
    return out


def encrypt_states(plaintexts, key):
    """plaintexts: (N,16) uint8. Devolve estados (N, 11, 16) uint8 (ver cabeçalho)."""
    pt = np.asarray(plaintexts, dtype=np.uint8)
    rks = key_expansion(key)
    n = pt.shape[0]
    st = np.empty((n, 11, 16), dtype=np.uint8)
    cur = pt ^ rks[0]
    st[:, 0] = cur
    for r in range(1, 11):
        cur = SBOX[cur][:, SR_SRC]
        if r != 10:
            cur = _mix_columns(cur)
        cur = cur ^ rks[r]
        st[:, r] = cur
    return st


def encrypt(plaintexts, key):
    return encrypt_states(plaintexts, key)[:, 10]


def hex_to_bytes(h):
    return np.frombuffer(bytes.fromhex(h), dtype=np.uint8)


def bytes_to_hex(b):
    return bytes(np.asarray(b, dtype=np.uint8).tolist()).hex()
