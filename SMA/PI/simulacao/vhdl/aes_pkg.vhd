-- Funcoes do AES-128 sobre vetores de 128 bits.
-- Convencao: o byte 0 (primeiro byte do bloco) ocupa os bits 127..120.
-- Indice de byte i = linha + 4*coluna (igual ao FIPS-197).
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.aes_sbox_pkg.all;

package aes_pkg is
  subtype word128 is std_logic_vector(127 downto 0);

  function get_byte(v : word128; i : natural) return std_logic_vector;
  function sub_bytes(s : word128) return word128;
  function shift_rows(s : word128) return word128;
  function mix_columns(s : word128) return word128;
  function next_round_key(k : word128; rnd : natural) return word128;
end package aes_pkg;

package body aes_pkg is

  type rcon_t is array (1 to 10) of std_logic_vector(7 downto 0);
  constant RCON : rcon_t := (x"01", x"02", x"04", x"08", x"10",
                             x"20", x"40", x"80", x"1b", x"36");

  function get_byte(v : word128; i : natural) return std_logic_vector is
  begin
    return v(127 - 8 * i downto 120 - 8 * i);
  end function;

  function sbox_f(b : std_logic_vector(7 downto 0)) return std_logic_vector is
  begin
    return SBOX(to_integer(unsigned(b)));
  end function;

  function xtime(b : std_logic_vector(7 downto 0)) return std_logic_vector is
    variable r : std_logic_vector(7 downto 0);
  begin
    r := b(6 downto 0) & '0';
    if b(7) = '1' then
      r := r xor x"1b";
    end if;
    return r;
  end function;

  function sub_bytes(s : word128) return word128 is
    variable r : word128;
  begin
    for i in 0 to 15 loop
      r(127 - 8 * i downto 120 - 8 * i) := sbox_f(get_byte(s, i));
    end loop;
    return r;
  end function;

  -- novo[p] = antigo[(p mod 4) + 4*(((p/4) + (p mod 4)) mod 4)]
  function shift_rows(s : word128) return word128 is
    variable r   : word128;
    variable src : natural;
  begin
    for p in 0 to 15 loop
      src := (p mod 4) + 4 * (((p / 4) + (p mod 4)) mod 4);
      r(127 - 8 * p downto 120 - 8 * p) := get_byte(s, src);
    end loop;
    return r;
  end function;

  function mix_columns(s : word128) return word128 is
    variable r                : word128;
    variable a0, a1, a2, a3   : std_logic_vector(7 downto 0);
    variable b0, b1, b2, b3   : std_logic_vector(7 downto 0);
  begin
    for c in 0 to 3 loop
      a0 := get_byte(s, 4 * c);
      a1 := get_byte(s, 4 * c + 1);
      a2 := get_byte(s, 4 * c + 2);
      a3 := get_byte(s, 4 * c + 3);
      b0 := xtime(a0) xor (xtime(a1) xor a1) xor a2 xor a3;
      b1 := a0 xor xtime(a1) xor (xtime(a2) xor a2) xor a3;
      b2 := a0 xor a1 xor xtime(a2) xor (xtime(a3) xor a3);
      b3 := (xtime(a0) xor a0) xor a1 xor a2 xor xtime(a3);
      r(127 - 8 * (4 * c)     downto 120 - 8 * (4 * c))     := b0;
      r(127 - 8 * (4 * c + 1) downto 120 - 8 * (4 * c + 1)) := b1;
      r(127 - 8 * (4 * c + 2) downto 120 - 8 * (4 * c + 2)) := b2;
      r(127 - 8 * (4 * c + 3) downto 120 - 8 * (4 * c + 3)) := b3;
    end loop;
    return r;
  end function;

  -- Chave da rodada rnd (1..10) a partir da chave da rodada anterior.
  function next_round_key(k : word128; rnd : natural) return word128 is
    variable w0, w1, w2, w3, t : std_logic_vector(31 downto 0);
    variable n0, n1, n2, n3    : std_logic_vector(31 downto 0);
  begin
    w0 := k(127 downto 96);
    w1 := k(95 downto 64);
    w2 := k(63 downto 32);
    w3 := k(31 downto 0);
    -- RotWord e SubWord sobre w3
    t := sbox_f(w3(23 downto 16)) & sbox_f(w3(15 downto 8)) &
         sbox_f(w3(7 downto 0))   & sbox_f(w3(31 downto 24));
    t(31 downto 24) := t(31 downto 24) xor RCON(rnd);
    n0 := w0 xor t;
    n1 := w1 xor n0;
    n2 := w2 xor n1;
    n3 := w3 xor n2;
    return n0 & n1 & n2 & n3;
  end function;

end package body aes_pkg;
