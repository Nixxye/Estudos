-- Variante B da regiao reconfiguravel: MESMA interface e MESMA entidade logica
-- (rm_block), implementacao estruturalmente diferente (sem tabela: XOR/rotacoes
-- encadeadas, profundidade de pipeline diferente). Serve so para o fluxo de DFX
-- ter duas implementacoes fisicas distintas para trocar. Nao e um S-box valido.
library ieee;
use ieee.std_logic_1164.all;

entity rm_variant_b is
  port (
    clk    : in  std_logic;
    rst    : in  std_logic;
    din    : in  std_logic_vector(7 downto 0);
    dvalid : in  std_logic;
    dout   : out std_logic_vector(7 downto 0);
    done   : out std_logic
  );
end entity rm_variant_b;

architecture rtl of rm_variant_b is
  signal r1, r2, r3, r4 : std_logic_vector(7 downto 0) := (others => '0');
  signal v1, v2, v3, v4 : std_logic := '0';
  constant K1 : std_logic_vector(7 downto 0) := x"5A";
  constant K2 : std_logic_vector(7 downto 0) := x"3C";
begin
  process (clk)
  begin
    if rising_edge(clk) then
      if rst = '1' then
        r1 <= (others => '0'); r2 <= (others => '0');
        r3 <= (others => '0'); r4 <= (others => '0');
        v1 <= '0'; v2 <= '0'; v3 <= '0'; v4 <= '0';
      else
        r1 <= din xor K1;
        v1 <= dvalid;
        r2 <= r1(3 downto 0) & r1(7 downto 4);           -- rotacao de nibble
        v2 <= v1;
        r3 <= r2 xor K2;
        v3 <= v2;
        r4 <= r3(0) & r3(7 downto 1);                    -- rotacao de 1 bit
        v4 <= v3;
      end if;
    end if;
  end process;
  dout <= r4;
  done <= v4;
end architecture rtl;
