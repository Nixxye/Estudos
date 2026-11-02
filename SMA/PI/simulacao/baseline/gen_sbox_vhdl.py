"""Gera vhdl/aes_sbox_pkg.vhd a partir da S-box calculada em Python (evita digitar a tabela)."""
import os

from aes_target import SBOX

rows = []
for i in range(0, 256, 8):
    rows.append("    " + ", ".join(f'x"{v:02x}"' for v in SBOX[i:i + 8]))
body = ",\n".join(rows)
text = f"""-- GERADO por baseline/gen_sbox_vhdl.py - nao editar a mao.
library ieee;
use ieee.std_logic_1164.all;

package aes_sbox_pkg is
  type sbox_t is array (0 to 255) of std_logic_vector(7 downto 0);
  constant SBOX : sbox_t := (
{body}
  );
end package aes_sbox_pkg;
"""
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "vhdl", "aes_sbox_pkg.vhd")
with open(out, "w", newline="\n") as f:
    f.write(text)
print("escrito", os.path.normpath(out))
