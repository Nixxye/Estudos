-- Entidade da REGIAO RECONFIGURAVEL (reconfigurable partition). Interface fixa:
-- qualquer variante plugada aqui precisa respeitar esta porta.
-- Proposito: teste de FERRAMENTA (DFX), nao e um bloco criptografico real.
library ieee;
use ieee.std_logic_1164.all;

entity rm_block is
  port (
    clk    : in  std_logic;
    rst    : in  std_logic;
    din    : in  std_logic_vector(7 downto 0);
    dvalid : in  std_logic;
    dout   : out std_logic_vector(7 downto 0);
    done   : out std_logic
  );
end entity rm_block;
