-- Testbench: le stim.txt (linha 1 = chave; demais = plaintexts, 32 hex cada) e grava em
-- states.txt, para cada cifragem, o valor do registrador de estado nos ciclos 0..10.
-- Rodar a partir do diretorio que contem stim.txt.
library ieee;
use ieee.std_logic_1164.all;
use std.textio.all;
use std.env.all;

entity tb_aes is
end entity tb_aes;

architecture sim of tb_aes is
  constant T : time := 10 ns;
  signal clk   : std_logic := '0';
  signal rst   : std_logic := '0';
  signal start : std_logic := '0';
  signal pt    : std_logic_vector(127 downto 0) := (others => '0');
  signal key   : std_logic_vector(127 downto 0) := (others => '0');
  signal st    : std_logic_vector(127 downto 0);
  signal done  : std_logic;
begin

  clk <= not clk after T / 2;

  dut : entity work.aes_iter
    port map (clk => clk, rst => rst, start => start, pt => pt, key => key,
              state_o => st, done => done);

  stim : process
    file fin  : text open read_mode  is "stim.txt";
    file fout : text open write_mode is "states.txt";
    variable l  : line;
    variable lo : line;
    variable k  : std_logic_vector(127 downto 0);
    variable p  : std_logic_vector(127 downto 0);
  begin
    readline(fin, l);
    hread(l, k);
    key <= k;
    while not endfile(fin) loop
      readline(fin, l);
      hread(l, p);
      -- limpa o registrador
      rst <= '1';
      wait until rising_edge(clk);
      wait for 1 ns;
      rst <= '0';
      -- carga (ciclo 0)
      pt    <= p;
      start <= '1';
      wait until rising_edge(clk);
      wait for 1 ns;
      start <= '0';
      hwrite(lo, st);
      -- rodadas 1..10
      for r in 1 to 10 loop
        wait until rising_edge(clk);
        wait for 1 ns;
        write(lo, string'(" "));
        hwrite(lo, st);
      end loop;
      writeline(fout, lo);
    end loop;
    finish;
  end process;

end architecture sim;
