-- Projeto estatico (static design) do teste de DFX. E&S estreitas (poucos pinos)
-- para caber no pacote do XC7Z020 e permitir implementacao com bitstream completo.
-- Instancia rm_inst: regiao reconfiguravel (entidade rm_block, trocada entre
-- rm_variant_a e rm_variant_b pelas configuracoes).
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
  component rm_block is
    port (
      clk    : in  std_logic;
      rst    : in  std_logic;
      din    : in  std_logic_vector(7 downto 0);
      dvalid : in  std_logic;
      dout   : out std_logic_vector(7 downto 0);
      done   : out std_logic
    );
  end component;
begin
  rm_inst : rm_block
    port map (clk => clk, rst => rst, din => din, dvalid => dvalid, dout => dout, done => done);
end architecture rtl;
