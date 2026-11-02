# Roteiro com o Vivado instalado: simulação de energia o mais próxima do real

Premissas do grupo: **Vivado ML Standard 2025.2** (sem licença), alvo **XC7Z020**, **sem placa**, preferência por **usar recursos do próprio Vivado** em vez de escrever software à parte. Os scripts abaixo são em **Tcl** (linguagem do Vivado) e o ataque reutiliza o que já existe em `PI/simulacao/baseline/cpa.py`.

Legenda de confiança: **[V]** conferido na documentação da AMD; **[B]** vem de resultado de busca; **[?]** não confirmado, deve ser testado.

---

## 0. A ideia central: qual é o "mais próximo do real" que o Vivado permite

O que o Vivado tem de mais físico, sem placa, é a combinação de:

1. **Atrasos reais de roteamento** da compilação escolhida (SDF) [V];
2. **Simulação temporizada**, que captura **glitches** [V];
3. **Modelo de potência da AMD** (`report_power`), que usa a atividade medida na simulação (SAIF) e as características do dispositivo [V].

Isso é mais fiel do que o nosso modelo de "bits que mudam com pesos iguais", porque cada rede tem sua carga e cada transição acontece no seu instante.

**Dois limites que definem o roteiro (conferidos):**
- **`report_power` dá potência média**, não uma curva. A lista de opções do comando (UG835) não tem `-saif` nem `-vcd` nem relatório por rede; o SAIF é lido antes, com `read_saif` [V]. Uma "curva" precisa ser montada como **uma sequência de janelas de tempo**, cada uma com seu SAIF e seu `report_power`.
- **A simulação temporizada só existe em Verilog** [V]. O projeto pode ficar em VHDL, mas a simulação com atrasos roda no netlist Verilog gerado, com testbench em Verilog.

**O que continua fora do Vivado:** a rede de alimentação, a indutância da placa, o ruído do osciloscópio e o efeito de outros blocos. Isso só se obtém com hardware. Declare isso no texto.

---

## Fase 0: instalação e verificação (1 hora)

| Passo | Resultado esperado |
|-------|--------------------|
| Help → Manage License | Edição ML Standard, sem pedir licença |
| Criar projeto para `xc7z020` e sintetizar `PI/simulacao/vhdl/aes_iter.vhd` | Síntese concluída. Se o Vivado reclamar da sintaxe, usar a opção de VHDL-2008 nos arquivos **[?]** |
| Conferir o menu **Dynamic Function eXchange** | Presente (documentação diz que não exige licença [V]) |
| No Tcl: `help write_sdf`, `help log_saif`, `help open_saif`, `help report_power` | Anotar as **opções exatas** da sua versão (pontos [?] abaixo dependem disso) |

---

## Fase 1: projeto base e custo por variante (reports do próprio Vivado)

**Recursos do Vivado:** síntese, implementação, `report_utilization`, `report_timing_summary`.

1. Sintetizar e implementar o `aes_iter` para o XC7Z020 com um clock de teste (por exemplo, 10 MHz).
2. Registrar: **LUTs, FFs, BRAMs, Fmax** (a partir do WNS).
3. Repetir para cada variante de RTL (Fase 2) e cada compilação (Fase 3).

**Saída:** coluna de **área e frequência** da tabela de variantes (a mesma tabela S1 do plano). **Critério:** números reproduzíveis ao rodar de novo.

---

## Fase 2: variantes de RTL dos estágios

**Recursos do Vivado:** só a síntese. As variantes são **módulos VHDL com a mesma interface e a mesma função**, por exemplo para a camada SubBytes:
- S-box por **tabela** (ROM/LUT), que é o que já temos;
- S-box por **lógica combinacional** de outra estrutura (por exemplo, campo composto);
- opcionalmente, versões **pipeline** (registrador no meio).

**Verificação funcional:** o mesmo testbench do GHDL (já instalado) confere que todas as variantes cifram igual ao `aes_target.py` (vetor FIPS-197 e comparação ciclo a ciclo). **Critério:** estados idênticos ao alvo Python em todos os ciclos, como já fizemos para o `aes_iter`.

---

## Fase 3: várias compilações do mesmo circuito (diversidade física)

**Recursos do Vivado:** diretivas e estratégias de implementação (UG904).
- `place_design -directive ...`: o guia lista diretivas como **Explore**, **ExtraNetDelay_high/low** e **AltSpreadLogic_high/medium/low**, que espalham ou agrupam a lógica de formas diferentes [B]. Os nomes exatos da 2025.2 devem ser conferidos em `help place_design`.
- `route_design -directive ...` e `phys_opt_design`, com as diretivas da sua versão **[?]**.
- **Estratégias prontas** de implementação (por exemplo, a de desempenho e a de congestionamento) [B].
- **Restrições de posição** (Pblock ou LOC) para forçar o circuito em regiões diferentes do chip, se as diretivas não variarem o bastante.

**Verificação de que as compilações realmente diferem:** comparar, por exemplo, a posição das células (`LOC`) e o roteamento entre as execuções. Se duas compilações saem idênticas, descarte uma. **Critério:** pelo menos K compilações (começar com 5) com posicionamento ou roteamento distintos, e função idêntica.

**Expectativa:** ganho modesto (a ordem de 2x reportada no resumo de Hettwer et al.).

---

## Fase 4: netlist temporizado e SDF por compilação

**Recursos do Vivado:** após a implementação (placed and routed):
```
write_verilog -mode timesim -sdf_anno true <netlist>.v      [V]
write_sdf <arquivo>.sdf                                      [?] opções a conferir com help write_sdf
```

Gerar um par netlist + SDF para **cada** variante e compilação. **Critério:** os arquivos são gerados e o simulador os aceita (Fase 5).

---

## Fase 5: simulação temporizada no simulador do Vivado (xsim)

**Recursos do Vivado:** xsim, em modo batch.

- **Testbench em Verilog** (não em VHDL): aplica N plaintexts aleatórios com uma **chave fixa**, zera o registrador entre cifragens (como no modelo) e roda os 11 ciclos de cada cifragem.
- O xsim lê o SDF junto com o netlist temporizado **[?]** (a anotação automática foi citada em buscas; confirmar no seu fluxo).
- **Captura de atividade:** `open_saif`, `log_saif`, `close_saif` [B]. O UG835 diz que **só um SAIF pode estar aberto por vez** na simulação [B], então janelas de tempo se obtêm **fechando e abrindo** um SAIF novo a cada janela **[?]**.
- Para o netlist temporizado, o xsim registra as redes (*wires*) internas [B], o que viabiliza a atividade por rede com glitches.
- Opcional: dump de VCD com comandos equivalentes (`open_vcd`, `log_vcd`) **[?]**.

**Critério:** com 10 cifragens, o testbench produz SAIF por janela e o texto cifrado do vetor FIPS-197 confere.

---

## Fase 6: energia pelo modelo do Vivado, por janela de tempo

**Recursos do Vivado:** `read_saif`, `report_power`.

Procedimento para **uma cifragem**:
1. Dividir a cifragem em janelas (por exemplo, **duas ou quatro por ciclo de clock**, 22 a 44 janelas).
2. Para cada janela, gerar um SAIF e rodar `read_saif` seguido de `report_power -return_string` (ou `-file`). Extrair a **potência dinâmica total** [V para o comando; o formato de saída deve ser conferido].
3. A sequência das potências por janela é o **traço** daquela cifragem.

Isso usa o modelo de potência da AMD (capacitâncias por rede, glitches, estimativa de lógica não coberta) em vez da nossa heurística.

**Restrições que precisam ser medidas antes de apostar nesta fase:**
- **Custo de tempo:** cada `report_power` leva um tempo que **não medi** **[?]**. Com 2.000 cifragens × 22 janelas, seriam 44.000 relatórios. Se cada um levar alguns segundos, são **dezenas de horas**. **Primeiro passo da fase: cronometrar um `report_power`** e decidir o tamanho possível do experimento.
- **Cobertura do SAIF:** o tutorial pede verificar que **100% das redes** casaram com o projeto; redes sem dados recebem atividade estimada, o que adiciona ruído de modelo [V].
- **Ruído:** os traços são **sem ruído de medição**. Será preciso somar ruído, e o valor continua sendo uma escolha do grupo, como no baseline.

**Estratégia recomendada (recursos do Vivado primeiro, o mínimo de código depois):**

| Etapa | Ferramenta | Volume |
|-------|-----------|--------|
| 6a. Potência por janela do Vivado | Tcl em xsim + `report_power` | **Pequeno** (por exemplo, 100 a 300 cifragens por compilação): é o "padrão-ouro" dentro do Vivado |
| 6b. Verificar o ataque sobre esse traço | `cpa.py` existente (só lê um CSV) | Pequeno |
| 6c. Se o volume de 6a bastar para ver tendências | Usar só isso | — |
| 6d. Se precisar de milhares de traços | Calibrar um modelo por rede contra 6a (opcional, fora do escopo do roteiro) | — |

Como a CPA sobre traços **sem ruído** exige bem menos traços (o nosso baseline sem ruído caiu com 800 traços), é possível que **centenas de cifragens bastem** para comparar compilações. Isso precisa ser verificado.

---

## Fase 7: custo por variante (potência média)

**Recursos do Vivado:** `report_power` com SAIF da simulação temporizada [V].
- Uma execução por variante e compilação, com atividade de um conjunto de cifragens.
- Registrar a **potência dinâmica e total** como coluna de custo.
- Observação do guia: simulação funcional não capta glitches, a temporizada capta [V]. Por isso o custo deve vir do SAIF **temporizado**.

---

## Fase 8: DFX para organizar as variantes (opcional, sem placa)

**Recursos do Vivado:** Dynamic Function eXchange, que não exige código de licença em nenhuma edição [V].
- Criar um projeto DFX com **uma partição reconfigurável** (o estágio que varia) e **vários módulos reconfiguráveis** (as variantes).
- O Vivado implementa cada **configuração** com roteamento próprio e gera os netlists correspondentes. Os atrasos e o posicionamento ficam consistentes com a situação real de troca.
- Não é necessário ter placa: só se usa a parte de implementação e os netlists, para simular como nas Fases 4 a 6.

**Quando vale:** se o grupo quiser que as variantes de cada estágio sejam implementadas **como numa troca real**. Para o estudo estatístico, as Fases 3 a 6 bastam.

---

## Fase 9: validação cruzada com o modelo do baseline

Com os traços de 6a em mãos:
1. **Correlação** entre a potência por janela do Vivado e o sinal do nosso modelo (distância de Hamming do registrador). Mostra o quanto a heurística se aproxima do modelo da AMD.
2. **CPA e TVLA** sobre os traços do Vivado, comparados com os do modelo.
3. **Comparar compilações:** a diferença entre os traços de duas compilações com entradas iguais mostra se a diversidade física muda o vazamento.

**Critério de utilidade:** se a CPA sobre os traços do Vivado recupera a chave com um nº de traços na mesma ordem do modelo, a heurística é defensável. Se a ordem diferir muito, usar os traços do Vivado como referência e ajustar a heurística.

---

## Fase 10: o que só a placa faria (fora do escopo, para registrar)

- Medição real com osciloscópio e shunt, ou com sensor interno (Sysmon).
- Efeitos da rede de alimentação, do acoplamento e do ruído real.
- Validação do número de traços em silício.

---

## Resumo: o que o Vivado entrega e o que falta

| Necessidade | Fornecido pelo Vivado | Falta |
|-------------|----------------------|-------|
| Variantes de RTL | Síntese e relatórios | Escrever os módulos VHDL (design, não software) |
| Compilações diferentes | Diretivas, estratégias e restrições de posição | Conferir que realmente diferem |
| Atrasos reais | SDF da implementação | — |
| Glitches | Simulação temporizada (Verilog) | Testbench em Verilog |
| Energia por janela | `read_saif` + `report_power` | **Medir o custo de tempo** e montar o laço em Tcl |
| Custo por variante | `report_utilization`, timing e `report_power` | — |
| Ataque | — | Reutilizar `cpa.py` (já existe) |

## Pontos a confirmar no Vivado instalado (os [?])

1. Opções exatas de `write_sdf` e de `log_saif` na 2025.2.
2. Se o xsim anota o SDF automaticamente no netlist temporizado.
3. Se dá para abrir e fechar vários SAIF numa mesma simulação (janelas).
4. Tempo de um `report_power` neste projeto.
5. Opções de diretiva do `route_design` e do `phys_opt_design`.
6. Se o Vivado aceita o VHDL do `aes_pkg.vhd` sem opções extras.

## Ordem prática sugerida

1. Fases 0 e 1 (instalar, sintetizar, reports).
2. Fase 5 com 10 cifragens, só para ver se SAIF e SDF funcionam.
3. Cronometrar um `report_power` (Fase 6) e decidir o volume.
4. Fases 3 e 4 (várias compilações) e 6a com as compilações.
5. Fase 9 (comparações) e só depois, se sobrar tempo, Fase 8 (DFX).

**Prazo:** o PI vence em 30/10. Instalar e rodar as Fases 0 e 1 já é possível, e o resto fica para o PF.

---

## Atualização (21/10/2026): o que foi **confirmado na prática** com o Vivado 2025.2 instalado

Instalação em `C:\AMDDesignTools\2025.2`. Tudo rodou em modo batch (`vivado.bat -mode batch`), sem pedir licença. Arquivos em `PI/simulacao/vivado/`.

| Item que estava como [?] | Resultado |
|--------------------------|-----------|
| Vivado ML Standard 2025.2 instala e roda sem licença | **Sim** (versão 2025.2, build de 14/11/2025) |
| Dispositivo XC7Z020 disponível | **Sim** (8 variantes de pacote; usei `xc7z020clg400-1`) |
| `aes_iter.vhd` sintetiza com `read_vhdl -vhdl2008` | **Sim**, sem erros. Fica em modo *out-of-context* (sem pinos), porque as portas de 128 bits excedem os pinos do pacote |
| `write_sdf` | Opções confirmadas: `-process_corner slow|fast`, `-mode timesim|sta`, `-cell`, `-force`, entre outras |
| `write_verilog -mode timesim -sdf_anno true -sdf_file ...` | **Sim.** Gera o netlist com `$sdf_annotate` embutido |
| `place_design`/`route_design`/`phys_opt_design -directive` | **Existem.** Diretivas listadas na ajuda da 2025.2 (ver abaixo) |
| xsim simula o netlist temporizado com SDF | **Sim.** Compila com `xvlog`, elabora com `xelab -L simprims_ver -L unisims_ver` e roda com `xsim` |
| Estados da simulação temporizada = modelo Python | **Sim.** 20 cifragens: iguais em todos os 11 ciclos |
| `open_saif`/`log_saif`/`close_saif` e **várias janelas na mesma simulação** | **Sim.** Abrir e fechar um SAIF novo a cada janela funciona (228 arquivos em 10 s) |
| `read_saif` + `report_power` | **Sim.** `read_saif -strip_path tb_timing/dut <arquivo>`; ~0,05 a 0,1 s para ler, ~0,2 a 0,5 s para o relatório |
| **Custo de tempo por janela** | **≈ 0,2 s** (228 janelas em 46 s). 2.000 cifragens × 12 janelas ≈ 80 min |
| **Resolução numérica** | O relatório de texto só tem 3 casas (mW). O **XML** (`-format xml -file`) traz a corrente por trilho com **6 casas (µA)**, o que basta. É o formato usado |
| Cobertura do SAIF | 1.180 de 1.557 redes casadas (76%); as demais recebem estimativa por propagação |

### Resultados do projeto base (`aes_iter`, XC7Z020, clock de 10 ns, diretivas padrão)

| Medida | Valor |
|--------|-------|
| LUTs / FFs / BRAM | 748 / 278 / 4,5 tiles (a S-box foi para **BRAM**) |
| WNS (10 ns) | +1,93 ns (Fmax ≈ 120 MHz) |
| Potência vetorless | 0,154 W (estática 0,104; dinâmica 0,051), confiança "Medium" |
| Compilação (síntese + implementação) | ≈ 1,5 min |

Observações do `route_design` e do `place_design`: `place_design` lista **Explore, AggressiveExplore, RuntimeOptimized, Quick e Default**; `route_design` lista **Explore, AggressiveExplore, NoTimingRelaxation, MoreGlobalIterations, HigherDelayCost, AdvancedSkewModeling, RuntimeOptimized, Quick e Default** (AlternateCLBRouting é só UltraScale); `phys_opt_design` lista variantes de Explore e de replicação. Os nomes mais antigos (`ExtraNetDelay_*`, `AltSpreadLogic_*`) **não aparecem** na ajuda da 2025.2 e precisam ser testados antes de serem usados.

### Primeira medição de vazamento com o modelo de potência do Vivado (19 cifragens, 12 janelas cada)

Janelas de 10 ns alinhadas às bordas de clock: 0 = limpeza do registrador, 1 = carga, 2 a 11 = rodadas 1 a 10. Variável: corrente dinâmica do trilho Vccint.

- Média por janela: 51 a 59 mA; desvio entre cifragens: **0,7 a 3,5 mA** (muito acima da resolução de 1 µA).
- Correlação com a distância de Hamming do registrador de estado:
  - janela 0 (limpeza): **0,90**;
  - janela 1 (carga): **0,60**;
  - janelas das rodadas: **de −0,02 a 0,41** (fraca).
- Inclinação global ≈ 134 µA por bit que muda.
- **Interpretação (com ressalva de que são só 19 cifragens por janela):** o modelo de potência da AMD indica que, nas rodadas, **o consumo dependente dos dados vem em boa parte de outros lugares** (lógica combinacional e a BRAM da S-box), não só do registrador de estado, que é o que o nosso modelo usa. Isso é exatamente o tipo de diferença que a simulação mais física deveria mostrar.

### Resultado do lote de 499 cifragens (corrente dinâmica Vccint, 12 janelas por cifragem)

- Lote concluído: **5.988 janelas** (499 × 12), 1.418 s de `report_power` (≈ 0,24 s por janela). A primeira tentativa havia falhado (o `cmd` partiu `-generic_top NENC=500`); corrigida e reexecutada.
- **CPA com as hipóteses do baseline (distância de Hamming da faixa do registrador na última rodada) NÃO recuperou a chave com 499 traços.** Melhor caso: 1 byte de 16 certo (nível de acaso), correlação média do palpite certo ≈ 0,02 e posição mediana do byte certo ≈ 115 a 148 de 256 (acaso = 128).
- Outras hipóteses testadas sobre os mesmos traços (também sem sucesso com 499 traços):

| Hipótese | Janela | Bytes certos | Posição mediana do certo | Correlação média do certo |
|----------|--------|--------------|--------------------------|---------------------------|
| K10: HD(s9, s10) da faixa | 10 | 1/16 | 116 | +0,006 |
| K10: HD(s9, s10) da faixa | 11 | 1/16 | 147 | +0,023 |
| K10: HW(s9) da faixa | 11 | 0/16 | 116 | +0,001 |
| **K0: HW(pt ⊕ k) por byte (carga)** | **1** | 1/16 | **25,5** | **+0,091** |
| K0: HW(S-box(pt ⊕ k)) | 2 e 3 | 0/16 | 115 e 164 | ≈ 0 |
| K0: HD(pt⊕k, S-box(pt⊕k)) | 2 | 0/16 | 63,5 | +0,020 |
| K10: HW(ct ⊕ k10) | 11 | 0/16 | 112 | +0,014 |

- **Leitura:** só a hipótese da **carga inicial** mostra sinal acima do acaso (posição mediana 25,5 contra 128 esperados ao acaso), mas ainda sem recuperar a chave. Na última rodada **não há sinal detectável** com 499 traços. No modelo de potência da AMD, o consumo dependente dos dados vem em grande parte de outras fontes (lógica combinacional, BRAM da S-box), e o **vazamento da faixa de 8 bits fica diluído**. Isso contradiz a premissa do nosso modelo simples, em que o registrador de estado domina.
- **Limites desta conclusão:** só 499 traços (o modelo simples sem ruído precisou de ~800); um único alvo e uma única compilação; as hipóteses testadas foram as clássicas, e uma hipótese melhor ajustada à lógica sintetizada (S-box em BRAM) pode funcionar; o modelo de potência do Vivado é uma estimativa, não uma medição.
- **Próximos passos possíveis:** (1) mais traços só nas janelas que importam (1 e 11), que reduz o custo de 12 para 2 janelas por cifragem; (2) olhar a divisão do consumo por hierarquia/rail (`report_power -hier all`, Vccbram separado) para saber de onde vem a variação; (3) rodar a CPA sobre a corrente da BRAM.

### Correção do resultado anterior: com hipóteses sobre a **S-box combinacional**, os traços do Vivado vazam

O resultado negativo acima valia só para hipóteses sobre o **registrador**. Testando hipóteses sobre a **saída combinacional da S-box** (a lógica que reavalia a S-box quando o registrador muda), nos mesmos 499 traços:

| Hipótese | Janela | Bytes certos | Posição mediana do certo | Correlação do certo |
|----------|--------|--------------|--------------------------|---------------------|
| K0: HD(0x63, S-box[pt ⊕ g]) (S-box passa de SB(0) para SB(pt ⊕ k) na carga) | 1 | **12/16** | **0** | +0,175 |
| K0: HW(pt ⊕ g) + HD(0x63, S-box[pt ⊕ g]) | 1 | 10/16 | 0 | +0,172 |
| K10: HW((ct_p ⊕ g) ⊕ S-box[ct_j]) (S-box passa de SB(s9) para SB(ct)) | 11 | 5/16 (0, 1, 3, 5 com N = 100, 200, 300, 499) | 2 | +0,166 |
| K10: soma registrador + S-box | 11 | 3/16 | 8 | +0,132 |

- **Leitura:** no modelo de potência da AMD, o vazamento forte dos dados está na **lógica combinacional da S-box**, não no registrador. A corrente do trilho da BRAM (`Vccbram`) é **constante** (desvio zero em todas as janelas): o modelo do Vivado não faz o consumo da BRAM depender dos dados. Toda a variação está em `Vccint` (desvio ≈ 1,2 mA por janela).
- **Consequência para o projeto:** o modelo simples do baseline (só o registrador) **não** representa bem o que o Vivado estima. Os ataques e as variantes devem usar hipóteses sobre a saída da S-box.
- **Limites:** só 499 traços; uma compilação; as hipóteses foram escolhidas depois de ver os dados (devem ser confirmadas na rodada noturna, com mais traços e outras compilações); o modelo de potência é uma estimativa.

### Rodada noturna automatizada (pronta e testada em escala pequena)

Pasta `PI/simulacao/vivado/overnight/` (ver `LEIA-ME.md` e `variants.conf`):
- 5 variantes: `base`, `explore`, `aggressive`, `quick` (diretivas de posicionamento e roteamento) e `nobram` (síntese com `-max_bram 0`, S-box em LUTs; a opção foi aceita pela 2025.2).
- 5.000 cifragens por variante, janelas 1 (carga) e 11 (última rodada), 4 hipóteses, bootstrap, comparação entre variantes.
- Teste de fumaça (60 cifragens, 2 variantes) passou ponta a ponta: estados do netlist temporizado iguais ao modelo Python, potência por janela e análise.
- Dois erros encontrados e corrigidos no teste: o `cmd` do Windows trata a vírgula como separador de argumentos (janelas agora passam com `_`) e o caminho relativo do arquivo de variantes.
