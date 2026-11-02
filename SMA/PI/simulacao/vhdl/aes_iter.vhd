-- Alvo B: AES-128 iterativo, uma rodada por ciclo, SEM nenhuma protecao.
-- Registrador de estado (state_r) = fonte de vazamento modelada (distancia de Hamming).
-- Ciclo 0 (carga): state_r <= pt xor key.  Ciclos 1..10: uma rodada por ciclo.
-- rst zera state_r e rk_r (o registrador e limpo entre cifragens, como no modelo em Python).
library ieee;
use ieee.std_logic_1164.all;
use work.aes_pkg.all;

entity aes_iter is
  port (
    clk     : in  std_logic;
    rst     : in  std_logic;
    start   : in  std_logic;
    pt      : in  std_logic_vector(127 downto 0);
    key     : in  std_logic_vector(127 downto 0);
    state_o : out std_logic_vector(127 downto 0);
    done    : out std_logic
  );
end entity aes_iter;

architecture rtl of aes_iter is
  signal state_r : word128 := (others => '0');
  signal rk_r    : word128 := (others => '0');
  signal rnd     : natural range 0 to 10 := 0;
  signal busy_r  : std_logic := '0';
  signal done_r  : std_logic := '0';
begin

  process (clk)
    variable nrk : word128;
    variable nst : word128;
  begin
    if rising_edge(clk) then
      done_r <= '0';
      if rst = '1' then
        state_r <= (others => '0');
        rk_r    <= (others => '0');
        rnd     <= 0;
        busy_r  <= '0';
      elsif start = '1' then
        state_r <= pt xor key;
        rk_r    <= key;
        rnd     <= 1;
        busy_r  <= '1';
      elsif busy_r = '1' then
        nrk := next_round_key(rk_r, rnd);
        nst := shift_rows(sub_bytes(state_r));
        if rnd /= 10 then
          nst := mix_columns(nst);
        end if;
        state_r <= nst xor nrk;
        rk_r    <= nrk;
        if rnd = 10 then
          busy_r <= '0';
          done_r <= '1';
          rnd    <= 0;
        else
          rnd <= rnd + 1;
        end if;
      end if;
    end if;
  end process;

  state_o <= state_r;
  done    <= done_r;

end architecture rtl;
