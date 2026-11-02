-- Variante A da regiao reconfiguravel: consulta a S-box do AES (tabela ja usada no
-- projeto, aes_sbox_pkg) e passa o resultado por 3 estagios de pipeline.
-- E so uma IMPLEMENTACAO DE TESTE para validar o fluxo de DFX (ferramenta), nao
-- participa de nenhuma cifragem.
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.aes_sbox_pkg.all;

entity rm_variant_a is
  port (
    clk    : in  std_logic;
    rst    : in  std_logic;
    din    : in  std_logic_vector(7 downto 0);
    dvalid : in  std_logic;
    dout   : out std_logic_vector(7 downto 0);
    done   : out std_logic
  );
end entity rm_variant_a;

architecture rtl of rm_variant_a is
  signal s1, s2, s3 : std_logic_vector(7 downto 0) := (others => '0');
  signal v1, v2, v3 : std_logic := '0';
begin
  process (clk)
  begin
    if rising_edge(clk) then
      if rst = '1' then
        s1 <= (others => '0'); s2 <= (others => '0'); s3 <= (others => '0');
        v1 <= '0'; v2 <= '0'; v3 <= '0';
      else
        s1 <= SBOX(to_integer(unsigned(din)));
        v1 <= dvalid;
        s2 <= s1; v2 <= v1;
        s3 <= s2; v3 <= v2;
      end if;
    end if;
  end process;
  dout <= s3;
  done <= v3;
end architecture rtl;
