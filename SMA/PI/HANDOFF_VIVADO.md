# Handoff — ambiente Vivado, simulação de CPA e teste de DFX

Documento de transferência: tudo que foi aprendido, construído e validado na parte de
simulação/Vivado do projeto SMA (AES-128 em FPGA, ataque por canal de potência e
reconfiguração parcial dinâmica), para quem for continuar o trabalho. Escrito para você
colar inteiro na conversa com o seu Claude e ele já ter o contexto todo — comandos exatos,
decisões tomadas, bugs já corrigidos e o que ainda falta.

**Tudo aqui é simulação.** Nenhuma medição foi feita em hardware físico; "potência" sempre
significa estimativa do Vivado a partir de atividade de chaveamento simulada.

---

## 0. Onde está cada coisa (mapa do repositório)

```
PI/
├── HANDOFF_VIVADO.md          ← este arquivo
├── RELATORIO_FINAL.md         ← relatório gerado automaticamente com todos os números (ataque CPA)
├── RELATORIO_DFX.md           ← relatório do teste de reconfiguração parcial (ferramenta, sem ataque)
├── AMBIENTE_VIVADO_RESUMO.md  ← resumo de "como montar o ambiente" (mais curto que este arquivo)
├── ANALISE_RESULTADOS.md      ← interpretação detalhada dos resultados da rodada noturna
├── PLANEJAMENTO.md, ESTUDO_VALIDADE.md, REVISAO_LITERATURA.md  ← validação da ideia e referências
└── simulacao/
    ├── baseline/        ← TODO o código Python (modelo AES, CPA, métricas, análise, testes)
    │   ├── aes_target.py        modelo de referência do AES-128 (S-box via GF, key schedule)
    │   ├── leakage.py           modelo de vazamento sintético (HD/HW + ruído) — não usa Vivado
    │   ├── cpa.py                ataque por correlação (correlação de Pearson assinada)
    │   ├── metrics.py            success_curve, rank_curve, TVLA, traces_to_disclosure
    │   ├── gen_sbox_vhdl.py      gera aes_sbox_pkg.vhd a partir da S-box em Python
    │   ├── vhdl_flow.py          roda o alvo VHDL no GHDL e compara com o modelo Python
    │   ├── check_states.py       confere estados do xsim do Vivado contra o modelo Python
    │   ├── attack_vivado.py      ataque simples sobre um único power.csv (script legado)
    │   ├── analyze_overnight.py  ataque "de verdade": várias variantes/hipóteses, bootstrap, curvas
    │   ├── build_report.py       monta PI/RELATORIO_FINAL.md a partir dos resultados
    │   └── tests/                17 testes automatizados (unittest)
    ├── vhdl/            ← o alvo em VHDL (aes_iter.vhd + pacotes), usado no GHDL e no Vivado
    ├── vivado/          ← scripts Tcl/shell do fluxo de implementação + simulação temporizada + potência
    │   ├── impl_variant.tcl       síntese+implementação de UMA variante (parametrizado)
    │   ├── export_timesim.tcl     reexporta netlist/SDF de um checkpoint já roteado
    │   ├── power_windows_sel.tcl  lê os SAIF de uma simulação e gera power.csv
    │   ├── tb_timing.v            testbench Verilog usado na simulação temporizada (xsim)
    │   ├── runs/<variante>/       saída de cada compilação (.dcp, relatórios, netlist timesim)
    │   ├── sim_<variante>_<N>/    saída de cada simulação (power.csv)
    │   └── overnight/             orquestra tudo, sem interação (a "rodada noturna")
    │       ├── run_overnight.sh   o script principal — leia a seção 3
    │       ├── variants.conf      lista de variantes a compilar e comparar
    │       ├── RESUMO.md          resumo gerado pela última rodada
    │       └── results_overnight.json, overnight.png
    └── vivado_dfx/      ← teste independente de DFX (reconfiguração parcial), não mexe no AES real
        ├── dfx_flow.tcl        o fluxo inteiro de DFX, non-project, só Tcl (leia a seção 5)
        ├── rm_block.vhd        entidade só-interface (black box real) da região reconfigurável
        ├── rm_variant_a.vhd    variante A do bloco de bancada (S-box + pipeline)
        ├── rm_variant_b.vhd    variante B (XOR/rotação + pipeline, sem tabela)
        └── out/                bitstreams, checkpoints e relatórios gerados
```

---

## 1. Ambiente (confirmado e funcionando)

| Item | Versão / caminho |
|---|---|
| SO | Windows |
| Vivado | **ML Standard 2025.2**, instalado em `C:\AMDDesignTools\2025.2` |
| Licença | **nenhuma pedida** para síntese, implementação, simulação temporizada (xsim), `report_power`, e **DFX completo em modo non-project** (ver seção 5) |
| Dispositivo alvo | `xc7z020clg400-1` (Zynq-7000) — está na lista de dispositivos gratuitos da ML Standard |
| GHDL | GHDL 6.0.0 (backend mcode), `winget install ghdl.ghdl.ucrt64.mcode --source winget` |
| Python | 3.13 com NumPy, matplotlib |
| Disco | ~100+ GB livres recomendado (uma simulação de 5.000 cifragens usa ~2 GB temporários em SAIF antes de serem apagados) |

**Chamada do Vivado — sempre em modo batch, sem GUI.**

Direto no PowerShell (forma mais simples, sem precisar de `cmd /c`):
```powershell
& "C:\AMDDesignTools\2025.2\Vivado\bin\vivado.bat" -mode batch -nojournal -nolog -source script.tcl -tclargs arg1 arg2 ...
```
Ou via `cmd` (equivalente, é a forma usada dentro dos scripts deste projeto):
```
cmd /c "C:\AMDDesignTools\2025.2\Vivado\bin\vivado.bat" -mode batch -nojournal -nolog -source script.tcl -tclargs arg1 arg2 ...
```
No Git Bash / WSL (como em `run_overnight.sh`), os caminhos Windows precisam de `cygpath -w` (script) e `cygpath -m` (saída), e o executável vem com `cmd //c` (barra dupla no Git Bash). Padrão exato usado em `overnight/run_overnight.sh` linha 19:
```bash
VB="C:/AMDDesignTools/2025.2/Vivado/bin"
vivado_batch(){ local tcl="$1"; shift; cmd //c "$(cygpath -w $VB/vivado.bat) -mode batch -nojournal -nolog -source $(cygpath -w "$tcl") -tclargs $*"; }
```
e, para `xvlog`/`xelab`/`xsim` (simulação, não precisam de `-tclargs`), o mesmo padrão com o executável trocado, por exemplo:
```bash
cmd //c "$(cygpath -w $VB/xvlog.bat) --incr --relax $(cygpath -w "$RUN/aes_timesim.v") tb_timing.v C:\AMDDesignTools\2025.2\Vivado\data\verilog\src\glbl.v"
cmd //c "$(cygpath -w $VB/xelab.bat) -debug typical -L simprims_ver -L unisims_ver tb_timing glbl -s tbsim"
cmd //c "$(cygpath -w $VB/xsim.bat) tbsim -tclbatch run_windows.tcl"
```

**Variável de ambiente útil no Windows:** `PYTHONUTF8=1` evita erro de codificação em barras de progresso/saídas com acentos.

---

## 2. Como tudo se encadeia (visão geral)

```
VHDL do bloco (simulacao/vhdl/)
        |  Vivado: síntese + implementação (XC7Z020) — impl_variant.tcl
        v
netlist temporizado (Verilog) + SDF (atrasos reais do roteamento)
        |  Vivado: xsim — simula com os atrasos
        v
estados do registrador, ciclo a ciclo  →  conferidos contra aes_target.py (check_states.py)
        |  xsim: um arquivo SAIF por janela de 10 ns alinhada às bordas de clock
        v
Vivado: read_saif + report_power (XML)  →  corrente estimada por janela  →  power.csv
        |
        v
simulacao/baseline/*.py (CPA, hipóteses de vazamento, métricas, bootstrap) — ataca o power.csv
```

As duas pontas (Vivado e Python) **só conversam por arquivo** (`power.csv`). Não há
integração ao vivo — é tudo por lote, retomável (cada etapa confere se já existe antes
de rodar de novo).

---

## 3. Rodar tudo do zero (o caminho já testado)

```bash
cd PI/simulacao/baseline
python -m unittest discover -s tests -v          # 17 testes — confere o ambiente inteiro
python run_experiments.py                         # baseline sintético (Python puro, ~2,5 min)
python vhdl_flow.py --n 20000 --sigma 10          # alvo VHDL no GHDL, ataque sobre os estados

cd ../vivado
bash overnight/run_overnight.sh 5000 1,11         # a rodada completa — ver detalhe abaixo
#                        ^N       ^janelas (ciclo 1 = carga, ciclo 11 = última rodada)

cd ../baseline
python build_report.py 5000                       # monta PI/RELATORIO_FINAL.md
```

**`run_overnight.sh` faz, para cada variante listada em `overnight/variants.conf`:**
1. Gera os plaintexts (mesma semente para todas as variantes, primeiro = vetor FIPS-197), uma vez só.
2. **Implementação** (`impl_variant.tcl`): síntese `out_of_context` + `opt_design` + `place_design -directive <X>` + (opcional) `phys_opt_design -directive <X>` + `route_design -directive <X>` → grava `.dcp`, `aes_timesim.v` (netlist com atraso) e `aes_timesim.sdf`.
3. **Simulação temporizada** (direto no script bash, blocos `xvlog`/`xelab`/`xsim`): compila o netlist temporizado + o testbench + `glbl.v`, roda `tb_timing` no xsim, e para cada cifragem/janela escolhida abre um SAIF (`open_saif` → `log_saif` → `run 10 ns` → `close_saif`).
4. **Conferência funcional** (`check_states.py`): compara os estados do testbench com o modelo Python — se divergir, para tudo.
5. **Potência por janela** (`power_windows_sel.tcl`): para cada SAIF, `reset_switching_activity -all` → `read_saif -strip_path tb_timing/dut` → `report_power -format xml` → extrai Vccint (total e dinâmica) e Vccbram dinâmica via regex no XML → grava uma linha em `power.csv`.
6. No final de todas as variantes: `analyze_overnight.py` (ataca tudo, gera `overnight/RESUMO.md` + `overnight.png`) e `build_report.py` (monta `PI/RELATORIO_FINAL.md`).

**Retomada:** o script pula etapas cujos arquivos de saída já existem (`aes_timesim.v`/`.sdf` para impl; `power.csv` completo para sim+potência). Uma rodada de 5.000 cifragens × 2 janelas leva **~40 min por variante**; a rodada noturna completa (5 variantes) rodou **~4h40 sem supervisão**.

### 3.1 Rodar só uma peça (para depurar)

Todos os comandos Vivado abaixo são chamados de dentro de `PI/simulacao/vivado/` e usam
`$VIVADO = "C:\AMDDesignTools\2025.2\Vivado\bin\vivado.bat"` (PowerShell: `& $VIVADO ...`).

| Quero... | Comando literal |
|---|---|
| Só implementar uma variante | `& $VIVADO -mode batch -nojournal -nolog -source impl_variant.tcl -tclargs base none Default Default none` (exemplo com a variante `base`; troque os 5 argumentos conforme `variants.conf`, seção 3.2) |
| Reexportar netlist/SDF de um `.dcp` já roteado | `& $VIVADO -mode batch -nojournal -nolog -source export_timesim.tcl -tclargs base` |
| Só recalcular potência de um lote já simulado (SAIF prontos) | `& $VIVADO -mode batch -nojournal -nolog -source power_windows_sel.tcl -tclargs base 4999 1_11 sim_base_5000\saif sim_base_5000\power.csv` |
| Rodar o teste de DFX inteiro (seção 5) | de dentro de `PI/simulacao/vivado_dfx/`: `& $VIVADO -mode batch -nojournal -nolog -source dfx_flow.tcl` (não recebe `-tclargs`; os caminhos estão fixos no topo do próprio script) |
| Atacar um `power.csv` isolado (script legado) | `python attack_vivado.py <N>` |
| Reanalisar várias variantes já prontas (ataque completo) | `python analyze_overnight.py <N> <janelas_com_virgula> <variants.conf>` |
| Só o teste de VHDL/GHDL, sem Vivado | `python vhdl_flow.py --n 2000 --validate-only` |

Os nomes de argumento de cada script (o que cada posição em `-tclargs` significa) estão
documentados na primeira linha de comentário de cada `.tcl` — por exemplo, `impl_variant.tcl`
linha 1: `# Uso: vivado -mode batch -source impl_variant.tcl -tclargs <nome> <sintese> <place> <route> <physopt>`.

### 3.2 Variantes de compilação já configuradas (`overnight/variants.conf`)

```
nome       | sintese        | place_design -directive | route_design -directive | phys_opt_design
base       | none (com BRAM)| Default                  | Default                  | none
explore    | none           | Explore                  | Explore                  | Explore
aggressive | none           | AggressiveExplore        | AggressiveExplore        | AggressiveExplore
quick      | none           | Quick                     | Quick                    | none
nobram     | nobram (S-box em LUTs) | Default           | Default                  | none
```
`aggressive` falhou na rodada noturna registrada (`FALHA_IMPL` — ver RESUMO.md para o log específico se for investigar; não foi uma prioridade resolver porque as outras 4 já davam o contraste que importava: BRAM vs. lógica).

### 3.3 Formato do `power.csv` (a "ponte" entre Vivado e Python)

```
enc,win,vccint_dyn_A,vccint_total_A,vccbram_dyn_A
0,1,0.0512,0.1540,0.0000
0,11,0.0498,0.1521,0.0000
...
```
`attack_vivado.py` e `analyze_overnight.py` leem isso e aplicam as mesmas funções de
`cpa.py` usadas no modelo sintético — por isso os números dos dois mundos são comparáveis.

---

## 4. Resultados já obtidos (resumo — números completos em `RELATORIO_FINAL.md` e `ANALISE_RESULTADOS.md`)

- **Fidelidade funcional confirmada em 3 níveis**: Python ↔ VHDL/GHDL ↔ netlist temporizado do Vivado — os estados do registrador coincidem ciclo a ciclo em todas as variantes testadas (milhares de cifragens).
- **Achado central**: a hipótese de vazamento **do registrador** (distância de Hamming) **não funciona bem** contra a estimativa de potência do Vivado (só 1/16 bytes certos). A hipótese que funciona é sobre a **lógica combinacional da S-box** (`sbox_load`/`sbox_last`): recupera a chave inteira (16/16 bytes) com **~1.600–3.200 cifragens**, dependendo da variante.
- **BRAM vs. lógica**: a variante `nobram` (S-box forçada para LUTs com `-max_bram 0`) tem um perfil de vazamento diferente das variantes com BRAM — a hipótese `reg_last` funciona melhor nela (porque sem BRAM a lógica da última rodada tem mais chaveamento visível no registrador). Isso é relevante como argumento de que **trocar a implementação do mesmo bloco muda o que é explorável**, que é a premissa de todo o projeto de DPR.
- As variantes de direção de implementação (`base`/`explore`/`quick`, todas com BRAM) têm **perfis de vazamento muito correlacionados entre si** (ρ de correlação cruzada 0,89–1,00 na janela 1) — ou seja, mudar só a *estratégia de place&route* não muda muito o vazamento; o que muda de verdade é a **arquitetura** (BRAM vs. lógica, no caso testado).
- **Limitações a repetir sempre que citar esses números**: potência é estimativa (SAIF da simulação temporizada), não medição física; ruído de medição e rede de alimentação não são modelados; as hipóteses `sbox_*` foram formuladas depois de ver o primeiro lote de resultados (não é um teste totalmente cego); resultados com poucos traços variam bastante entre repetições.

---

## 5. Teste de DFX / reconfiguração parcial (`vivado_dfx/`) — resumo técnico

Objetivo deste teste: confirmar que a **edição gratuita** do Vivado executa o fluxo de DFX
ponta a ponta. **Não usa o AES real** — usa um bloco de bancada mínimo (`rm_variant_a`/`rm_variant_b`)
só para ter duas implementações fisicamente diferentes para trocar.

**Fluxo exato (`dfx_flow.tcl`, non-project):**
1. Sintetiza as duas variantes **sempre fora de contexto** (`synth_design -mode out_of_context`), separadamente.
2. Sintetiza o estático (`dfx_top`) instanciando `rm_block` — uma entidade **sem corpo/arquitetura**, um black box de verdade desde o início.
3. Marca a região: `set_property HD.RECONFIGURABLE 1 [get_cells rm_inst]`, cria um Pblock (`create_pblock` + `add_cells_to_pblock` + `resize_pblock ... {SLICE_X0Y0:SLICE_X15Y49}` + `SNAPPING_MODE ON`).
4. **Config 1** = estático + variante A: `read_checkpoint -cell rm_inst rm_variant_a_synth.dcp` → `opt_design` → `place_design` → `route_design` → `write_bitstream`.
5. **Config 2** = estático + variante B, **reaproveitando o roteamento estático**: `update_design -cell rm_inst -black_box` → `lock_design -level routing` → `read_checkpoint -cell rm_inst rm_variant_b_synth.dcp` → implementa de novo.
6. `pr_verify -full_check config1_routed.dcp config2_routed.dcp` confirma que as duas configurações compartilham a mesma lógica estática roteada (bateu: 1.224 tiles e 170 pips idênticos, 20 pinos de partição compatíveis).

### 5.1 Bug encontrado e a correção (documentar para não repetir)

**Sintoma:** ao sintetizar a variante A **junto** (inline) com o estático, o Vivado renomeou
a porta de saída de `dout` para `Q` como otimização entre hierarquias. Quando a variante B
(sintetizada à parte, OOC, com nomes preservados) foi encaixada depois, os nomes das portas
não bateram e o `read_checkpoint -cell` travou.

**Correção:** sintetizar **as duas variantes sempre fora de contexto**, e fazer o estático
nascer com um **black box real** (entidade sem arquitetura) desde a primeira config, não só
a partir da segunda. Isso elimina a assimetria. **Regra geral para qualquer fluxo de DFX:
nunca sintetizar o bloco reconfigurável junto com o estático.**

### 5.2 Resultados principais

| | Variante A | Variante B |
|---|---|---|
| Síntese OOC | 18 s | 15 s |
| Implementação completa | 28,7 s | 28,8 s (reaproveitando estático travado) |
| Bitstream completo | 4.045.683 bytes | idêntico (mesmo dispositivo) |
| **Bitstream parcial** (gerado automaticamente, sem comando extra) | **383.476 bytes (~9,5% do completo)** | mesmo tamanho (mesma área de Pblock) |

Tempo de reconfiguração é **projeção**, não medida (sem placa): 383.476 bytes ÷ taxa de
transferência da ICAP → de ~1 ms (400 MB/s teórico) a ~38–83 ms (controladores típicos
citados na literatura revisada no projeto).

**DRC rebaixado para warning** (só porque este design de bancada não tem placa/pinos reais):
```tcl
set_property SEVERITY {Warning} [get_drc_checks NSTD-1]
set_property SEVERITY {Warning} [get_drc_checks UCIO-1]
```
⚠️ **Nunca fazer isso em um projeto que vai para hardware de verdade** — só serve para gerar
um bitstream de teste sem placa alvo.

### 5.3 O que falta para ligar isso ao AES real (`aes_iter.vhd`)

Isto **não foi feito** — é o próximo passo de engenharia se o grupo quiser continuar por aqui:

1. O `aes_iter` tem barramentos de 128 bits; para caber como região reconfigurável de um
   estático com pinos de pacote reais, precisa de uma **interface estreita** (serial, FIFO,
   ou manter tudo *out-of-context* sem bitstream real para hardware — como já é feito no
   fluxo de simulação de potência da seção 3).
2. Repetir o fluxo da seção 5 com **duas variantes reais** do `aes_iter` (por exemplo, as
   compilações `base` e `nobram` que já existem e já foram medidas na seção 4).
3. Medir o tempo e tamanho do bitstream parcial dessa região maior — deve escalar com
   748–1.251 LUTs (contra os poucos LUTs/FFs do bloco de bancada testado aqui).
4. **BRAM dentro de região reconfigurável tem regras adicionais** não exercitadas neste
   teste — a variante `base` do AES usa BRAM, então isso vai aparecer.

---

## 6. Bugs e gotchas já resolvidos (para não perder tempo redescobrindo)

| Problema | Causa | Correção |
|---|---|---|
| Listas de janelas (`1,11`) quebravam em argumentos separados ao passar por `cmd //c` no Windows | vírgula é interpretada como separador de argumento pelo `cmd.exe` | usar underscore (`1_11`) na linha de comando e `split $wins _` no Tcl em vez de `split $wins ,` |
| `ResourceWarning: unclosed file` em `analyze_overnight.py` | `load_power()` usava `open(path)` sem fechar | `with open(path, newline="", encoding="utf-8") as f:` |
| Caminho relativo errado em `analyze_overnight.py` quando chamado de outro diretório | config resolvida contra o cwd errado | `run_overnight.sh` resolve `CONF` para caminho absoluto antes de passar adiante |
| `write_bitstream`: erro de sintaxe ("file" especificado mais de uma vez) | passar um `.dcp` posicional junto com `-file` | nunca combinar argumento posicional com `-file` |
| Detecção de versão do Vivado errada em `build_report.py` | comparação `'Vivado' in x` (maiúscula) contra saída da CLI em minúsculas | comparar com `.lower()` |
| **DFX**: `read_checkpoint -cell` falha com erro de interface incompatível (`ERROR: [Netlist 29-77]`) | nomes de porta divergentes entre síntese inline e OOC (ver seção 5.1) | sintetizar sempre as duas variantes fora de contexto + estático com black box real desde o início |
| `write_bitstream` falhando por DRC (NSTD-1, UCIO-1) em design de bancada sem placa | esperado, sem pinos/local físico atribuído | rebaixar severidade **só para esses dois checks, só em design de teste sem alvo real** (nunca em projeto para hardware real) |
| `pip install maspy` instala a biblioteca errada | existe um pacote homônimo no PyPI, de espectrometria de massa, sem relação com o projeto (isso é do protótipo MASPY do SMA, não da parte Vivado — mas vale saber se for reusar ambiente) | ver `aes_dpr_prototype/README.md` / `2D_navigation/README.md` no repo |

---

## 7. O que ainda falta (próximos passos reais, nesta ordem de prioridade)

1. **Nada do CPA/DPR foi conectado de fato.** O que existe são duas peças separadas e validadas: (a) o ataque CPA contra variantes de implementação do AES (seção 4) e (b) o mecanismo de DFX funcionando num bloco de bancada (seção 5). **Ligar as duas** — medir se trocar de variante via reconfiguração parcial de fato atrapalha o atacante — é o próximo passo central do projeto e **não foi feito**.
2. Para isso, a forma mais viável sem hardware real é **simular a troca de variante como troca de qual `power.csv` alimenta o atacante no meio de uma sequência de cifragens** (os dados já existem para `base` e `nobram`, que têm perfis de vazamento visivelmente diferentes — seção 4). Isso não precisa do DFX real, só precisa decidir uma política de troca e reavaliar as curvas de sucesso do CPA sobre traços misturados.
3. Separado disso, se quiser seguir o caminho de hardware "de verdade", seguir os passos da seção 5.3 (DFX com o `aes_iter` real).
4. **Atenção ao pedir ajuda ao Claude sobre o item 1/2 acima**: nesta sessão, pedidos que misturavam "ferramenta de reconfiguração" com "isso derrota o atacante" como um roteiro ofensivo acionável (ex.: "me dê o próximo passo para quebrar a chave mais rápido usando a reconfiguração") foram barrados pelo classificador de segurança do Claude Code, mesmo sendo para fins acadêmicos/defensivos legítimos. O que **funcionou bem** foi separar claramente: (a) pedidos de **análise/medição** ("qual o efeito estatístico de misturar traços de duas variantes na curva de sucesso do CPA?") e (b) pedidos de **documentação/relatório** do que já existe. Evite frasear como "plano para derrotar o ataque" — peça a análise estatística em si.

---

## 8. Referências (já citadas no projeto)

1. Brier, Clavier, Olivier — *Correlation Power Analysis with a Leakage Model*, CHES 2004 (base do CPA usado).
2. FIPS-197 — especificação do AES (vetores de teste usados nos testes automatizados).
3. Artigo "semelhante" identificado na revisão de literatura: DATE 2019, ataque remoto por canal de potência em FPGA multi-tenant (Amazon EC2 F1) — citado como motivação do cenário "FPGA compartilhada".
4. Ver `REVISAO_LITERATURA.md` e `ESTUDO_VALIDADE.md` para a validação da ideia e outras referências levantadas (contramedidas por DPR, taxas de transferência da ICAP).

---

*Qualquer dúvida sobre uma decisão específica tomada aqui, procure primeiro no relatório
correspondente (`RELATORIO_FINAL.md` para o ataque, `RELATORIO_DFX.md` para a reconfiguração,
`ANALISE_RESULTADOS.md` para a interpretação estatística) — eles têm mais detalhe numérico
do que este documento, que é propositalmente um mapa/guia de orientação.*
