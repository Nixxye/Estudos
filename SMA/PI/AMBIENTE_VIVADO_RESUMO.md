# Resumo: como montar o ambiente Vivado que alimenta o código de análise

Isto documenta o que **já está construído e testado** (rodada noturna + testes automatizados), reorganizado como guia de ambiente. Não inclui nada novo de ataque — é só "como ligar as peças que já existem".

## 1. Visão geral do encadeamento

```
VHDL do bloco (PI/simulacao/vhdl/)
        |  Vivado: síntese + implementação (XC7Z020)
        v
netlist temporizado (Verilog) + SDF
        |  Vivado: xsim (simulação com atrasos reais)
        v
estados do registrador, ciclo a ciclo  →  conferidos contra o modelo Python (aes_target.py)
        |  xsim: SAIF por janela de tempo
        v
Vivado: read_saif + report_power  →  corrente estimada por janela (CSV)
        |
        v
PI/simulacao/baseline/*.py  (CPA, hipóteses, métricas) — o "algoritmo" já escrito
```

As duas pontas (Vivado e o código Python) já conversam por **arquivos**: o Vivado produz `power.csv`; o Python lê esse CSV. Não há integração ao vivo, é por lote.

## 2. Instalação do Vivado (o que já está confirmado)

- **Versão:** Vivado ML Standard **2025.2**, instalada em `C:\AMDDesignTools\2025.2`.
- **Licença:** nenhuma pedida, para o fluxo usado (síntese, implementação, simulação temporizada, `report_power`, DFX não-projeto — ver `RELATORIO_DFX.md`).
- **Dispositivo:** XC7Z020, pacote `clg400-1` (está na lista de dispositivos gratuitos da ML Standard).
- **Chamada:** sempre em modo batch, sem interface gráfica:
  ```
  cmd /c "C:\AMDDesignTools\2025.2\Vivado\bin\vivado.bat" -mode batch -nojournal -nolog -source script.tcl
  ```

## 3. Estrutura de pastas

```
PI/simulacao/
├── vhdl/                 # o bloco sob teste (aes_iter.vhd + pacotes)
├── baseline/              # TODO O CÓDIGO DE ANÁLISE (Python)
│   ├── aes_target.py      # modelo de referência do AES (conferência)
│   ├── cpa.py              # ataque por correlação
│   ├── leakage.py          # modelo de vazamento sintético (sem Vivado)
│   ├── metrics.py          # taxa de sucesso, TTD90, TVLA
│   ├── attack_vivado.py    # lê power.csv do Vivado e ataca
│   ├── analyze_overnight.py # analisa várias variantes de uma vez
│   ├── build_report.py     # monta o relatório final em Markdown
│   └── tests/               # 17 testes automatizados
├── vivado/
│   ├── impl_variant.tcl     # síntese+implementação de uma variante
│   ├── power_windows_sel.tcl # read_saif + report_power por janela
│   ├── runs/<variante>/      # saída de cada compilação (.dcp, relatórios, netlist)
│   ├── sim_<variante>_<N>/   # saída da simulação (power.csv)
│   └── overnight/             # orquestra tudo, sem interação
└── vivado_dfx/              # teste de DFX (reconfiguração), independente do resto
```

## 4. Passo a passo para rodar do zero

### 4.1 Pré-requisitos já verificados
- Vivado 2025.2 instalado (`C:\AMDDesignTools\2025.2`).
- Python 3.13 com NumPy e matplotlib.
- 100+ GB de disco livre (cada simulação de 5.000 cifragens usa ~2 GB temporários).

### 4.2 Rodar tudo (o caminho já testado)

```bash
cd PI/simulacao/baseline
python -m unittest discover -s tests -v        # confere o ambiente (17 testes)

cd ../vivado
bash overnight/run_overnight.sh 5000 1,11       # implementa, simula, mede potência, analisa

cd ../baseline
python build_report.py 5000                      # monta PI/RELATORIO_FINAL.md
```

O script `run_overnight.sh` já encadeia, por variante (lidas de `overnight/variants.conf`):
1. síntese + implementação (`impl_variant.tcl`);
2. exportação do netlist temporizado + SDF;
3. simulação no xsim com captura de SAIF por janela;
4. `read_saif` + `report_power` por janela (`power_windows_sel.tcl`) → `power.csv`;
5. no final, `analyze_overnight.py` lê todos os `power.csv` e ataca.

### 4.3 Rodar só uma peça (para depurar)

| Quero... | Comando |
|---|---|
| Só implementar uma variante | `vivado -mode batch -source impl_variant.tcl -tclargs <nome> <synth> <place> <route> <physopt>` |
| Só simular (depois de implementar) | ver `overnight/run_overnight.sh`, bloco `xvlog`/`xelab`/`xsim` |
| Só recalcular potência de um lote já simulado | `vivado -mode batch -source power_windows_sel.tcl -tclargs <run> <N> <janelas> <pasta_saif> <saida.csv>` |
| Só atacar um `power.csv` já pronto | `python attack_vivado.py <N>` (lê `vivado/sim<N>/power.csv`) |
| Só reanalisar várias variantes já prontas | `python analyze_overnight.py <N> <janelas> <variants.conf>` |

### 4.4 Como o Python "conversa" com o Vivado

Não há chamada direta — a ponte é o arquivo `power.csv`, com colunas:
```
enc, win, vccint_dyn_A, vccint_total_A, vccbram_dyn_A
```
`attack_vivado.py` e `analyze_overnight.py` leem esse CSV e aplicam as mesmas funções de ataque (`cpa.py`) usadas no modelo sintético — por isso os resultados dos dois mundos (sintético e Vivado) são comparáveis.

## 5. O que já está validado neste ambiente

- **Fidelidade funcional:** os estados do registrador na simulação temporizada (com atrasos reais do roteamento) batem, ciclo a ciclo, com o modelo Python de referência — em todas as variantes testadas.
- **Custo de tempo:** cerca de 0,2 a 0,25 s por `read_saif`+`report_power`; uma rodada de 5.000 cifragens × 2 janelas leva ~40 min por variante.
- **Robustez:** o pipeline tolera reinício (pula etapas já concluídas) e roda sem interação (testado numa rodada de ~4h40 sem supervisão).

## 6. Limitações a lembrar

- A potência é **estimada pelo Vivado** (a partir da atividade de chaveamento simulada), não medida em hardware.
- O ruído de medição real, a rede de alimentação e efeitos analógicos não estão no modelo.
- Resultados completos e a interpretação: ver `PI/RELATORIO_FINAL.md` e `PI/ANALISE_RESULTADOS.md`.
