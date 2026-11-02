
library ieee;
use ieee.std_logic_1164.all;

entity dfx_top is
  port (
    clk    : in  std_logic;
    rst    : in  std_logic;
    din    : in  std_logic_vector(7 downto 0);
    dvalid : in  std_logic;
    dout   : out std_logic_vector(7 downto 0);
    done   : out std_logic
  );
end entity dfx_top;

architecture rtl of dfx_top is
begin
  -- rm_block (so a entidade, sem arquitetura): nasce como BLACK BOX de verdade,
  -- para que config1 e config2 sejam stitched do MESMO jeito (sem assimetria de nomes).
  rm_inst : entity work.rm_block
    port map (clk => clk, rst => rst, din => din, dvalid => dvalid, dout => dout, done => done);
end architecture rtl;

