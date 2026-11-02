# Simular cada variante do circuito para atacá-la (pré-silício)

Complemento de [REVISAO_LITERATURA.md](REVISAO_LITERATURA.md). Objetivo: gerar **traços de consumo por simulação** de cada variante de um núcleo AES e rodar CPA/TVLA sobre eles, sem placa, para preencher a tabela "variante → traços até divulgação → custo" que os agentes consultam.

> **Evidência:** buscas web (3 consultas estendidas), leitura do resumo de **Vogls** e de **TOFU** (páginas de resumo) e do texto completo do artigo **Bahrami et al. (SECRYPT 2022)**. O resto são trechos de resultados de busca, marcados como tal. Nenhuma dessas ferramentas foi instalada ou testada por nós.

---

## 1. Fluxo geral (o padrão que aparece na literatura)

Segundo as fontes encontradas, as ferramentas de pré-silício seguem três passos:

1. **Simular o projeto** com entradas conhecidas e **gravar a atividade dos sinais** (arquivo VCD).
2. **Converter a atividade em traços sintéticos de consumo** com um modelo (peso de Hamming, distância de Hamming ou contagem de transições, "toggle count").
3. **Rodar a análise padrão** (CPA, TVLA) sobre esses traços.

```
Variante do circuito (Verilog)
        |  simulador (Verilator / Vogls / Icarus)
        v
Atividade dos sinais (VCD)           <- uma simulação por texto de entrada
        |  conversor de modelo (TOFU ou script próprio)
        v
Traços sintéticos  +  ruído gaussiano    <- ruído é adicionado por nós
        |  CPA / alinhamento / TVLA
        v
Traços até divulgação da chave (por variante)
```

---

## 2. Ferramentas encontradas

| Ferramenta | O que é | O que sabemos | Evidência |
|------------|---------|---------------|-----------|
| **TOFU** (Gruber e Sigl, ePrint 2022/129) | Converte VCD em traços de consumo com modelos de vazamento ajustáveis; propõe fluxo só com ferramentas livres | Validado com CPA em um AES em hardware. A página **não** mostra comparação com medições físicas nem o repositório | resumo |
| **Vogls** (Burghoorn, Buhan, Batina, arXiv 2607.15782, jul/2026) | Simulador Verilog livre para análise de canal lateral. Simula RTL, nível de porta e **nível de porta com temporização completa**. Interface Python para pausar, bifurcar e inspecionar a simulação | 5,9x mais rápido que o Icarus Verilog em AES de nível de porta; ~30% mais lento que o Verilator em RTL (PicoRV32). Caso de estudo: **DPA recupera a chave do AES simulado nos três níveis**. A página **não** menciona validação contra silício. Preprint recente | resumo (lido) |
| **PROLEAD** (TCHES) | Simula o estado de portas e testa se valores sondados são independentes do segredo; **não usa modelo de potência** | Detecta vazamento, inclusive glitches e transições, sem medições | resumo de busca |
| **ELMO** | Simulador de potência para ARM Cortex-M0/M4 | Só para software em ARM, **não serve** para núcleo em FPGA | resumo de busca |
| **SILK** | Primeiro simulador de canal lateral totalmente livre (Veshchikov, 2014) | Alto nível de abstração | citado em Bahrami et al. |
| **Vivado + SAIF** | Simulação pós-roteamento da Xilinx gera atividade (inclusive glitches) para estimativa de potência | O guia UG907 diz que a simulação pós-roteamento informa a atividade interna, incluindo glitches, e é mais precisa que a comportamental | resumo de busca |

**Verilator** é o simulador citado em trabalhos recentes para traços determinísticos, ao custo de ser ruim para muitas coletas curtas com pequenas variações de entrada (argumento do artigo do Vogls).

---

## 3. Níveis de fidelidade e o que os artigos dizem

| Nível | Captura | Limite relatado |
|-------|---------|-----------------|
| **RTL (comportamental)** | Estados de registradores; boa para primeira triagem | Não vê glitches nem atrasos de roteamento |
| **Pós-síntese** | Estrutura de portas | Atrasos de rede ainda não existem |
| **Pós-implementação com SDF** (atrasos anotados) | Glitches e atrasos | Um estudo (OpenRISC em Artix-7, resultado de busca) achou que o vazamento se desloca **cerca de meio ciclo de clock** em relação à pós-síntese |
| **SPICE** | Física analógica | Muito mais lento; é a referência |

**Achado importante (Bahrami et al., SECRYPT 2022, texto completo lido):**
- Comparou toggle count com **HSPICE** em 2 implementações sem proteção e 5 com mascaramento da S-box do cifrador PRESENT.
- **Sem proteção:** os dois níveis concordam qualitativamente.
- **Com mascaramento:** a contagem de transições **deixa de refletir o vazamento real**, porque a máscara aleatória mistura os eventos. Os autores concluem que designs mascarados devem ser analisados em SPICE.
- Se o toggle count acha viés, há vulnerabilidade de fato. Se **não** acha, isso **não** prova segurança.
- Observação deles: com poucos milhares de traços já é possível decidir se há vazamento em algum instante do traço.

**Um survey de 2025 (resultado de busca)** acrescenta que modelos simulados costumam ignorar parasitas, queda de tensão (IR drop) e variação de processo.

**Consequência direta para o projeto:**
- Variantes **sem mascaramento** (diversidade de implementação, desalinhamento): simulação por toggle count é razoável para **comparar** variantes entre si.
- Variantes **com mascaramento dinâmico** (como Kian et al.): a simulação por toggle count **não é confiável**. Usar PROLEAD ou tratar o resultado como não conclusivo.

---

## 4. Quais variantes dá para simular, e como

| Variante | Simulável em RTL/porta? | Como |
|----------|-------------------------|------|
| **S-box com implementações diferentes** (tabela, campo composto, etc.) | Sim | Um módulo Verilog por implementação; mesma função, estrutura de portas diferente |
| **Mascaramento com função trocada (XOR/XNOR)** | Sim, mas com ressalva do §3 | Duas versões do módulo; toggle count pouco confiável para comparar |
| **Clock aleatório (estilo RFTC)** | **Não em RTL puro**: depende de efeitos analógicos do MMCM e jitter | Modelar estatisticamente: o instante do vazamento muda por execução, como na demo `cpa_demo.py` |
| **Placement e routing diferentes** (Hettwer et al.) | Só na pós-implementação com SDF | Exige Vivado: uma implementação por configuração, simulação temporizada de cada uma |
| **Reconfiguração em si** (carregar o bitstream) | **Não** | Simuladores de HDL não modelam o carregamento da configuração |

**Como representar a troca entre variantes:** simular cada variante **separadamente**, gerar um conjunto de traços de cada uma e, no laboratório de ataque, **montar a sequência de traços** que o atacante veria, alternando as variantes conforme a política dos agentes. Isso permite medir o efeito da **política de troca** sobre o atacante, que é o que interessa ao SMA.

---

## 5. Armadilhas específicas desta abordagem

1. **A simulação é sem ruído.** Traços de simulação são deterministas. O ruído de medição precisa ser **adicionado por nós**. Se o ruído for arbitrário, os números absolutos de "traços até divulgação" **não significam nada**. Só comparações **relativas** entre variantes valem. Para ancorar, calibrar o ruído para que a variante sem proteção quebre com ~2.000 traços (o valor do RFTC em placa real), ou declarar explicitamente que só se compara em ordem de grandeza.
2. **Modelo de consumo simplificado.** Distância de Hamming/toggle count trata cada transição como uma unidade de energia. Ferramentas comerciais usam modelos mais detalhados.
3. **Atacante modelado.** O resultado vale para o ataque que vocês implementarem (CPA, com ou sem alinhamento). O RFTC mesmo deixou sliding-window como futuro.
4. **Passar no TVLA simulado não prova segurança** (afirmação do próprio SoK de ferramentas e do artigo SECRYPT).
5. **Sem validação em silício.** Nem o resumo do Vogls nem o de TOFU mostram comparação com medições físicas. É preciso declarar isso como limitação.
6. **Ferramentas novas.** Vogls é de julho de 2026; verifique licença, instalação e maturidade do código antes de depender dele.

---

## 6. De graça, sem placa: custo por variante com Vivado

Para o lado do **custo** da tabela, o Vivado fornece, sem hardware:
- **Área** (LUTs, FFs, BRAMs) por variante, no relatório de utilização;
- **Frequência máxima** a partir do relatório de temporização;
- **Estimativa de potência** (guia UG907), que pode usar atividade da simulação (SAIF).

São estimativas, não medições, mas servem para preencher "tempo/potência/área por variante" com números gerados por ferramenta, em vez de multiplicadores copiados de outro artigo. Conferir a licença do Vivado e se o dispositivo-alvo está na edição gratuita.

---

## 7. Plano mínimo recomendado

1. Escolher **um** núcleo AES livre e iterativo (conferir licença e qualidade) e escrever ou obter 3 variantes de S-box (sem mascaramento).
2. Simular cada variante com **Verilator** (ou Icarus) para N textos aleatórios, com uma chave fixa, e gravar VCD ou a contagem de transições por ciclo.
3. Converter em traços (TOFU ou script próprio de distância de Hamming por ciclo) e **adicionar ruído gaussiano calibrado**.
4. Rodar **CPA** (e TVLA fixo contra aleatório) e registrar **traços até divulgação** por variante, repetindo para reduzir variância.
5. Montar no laboratório de ataque a **sequência temporal** com troca entre variantes e medir o efeito sobre o atacante.
6. Alimentar a tabela de variantes no MASPY, junto com área e Fmax do Vivado.
7. (Opcional) Subir a fidelidade para pós-implementação com SDF em Vivado e/ou Vogls de nível de porta.

**Prazo realista:** nada disso entra no PI (30/10). É trabalho do PF. Para o PI basta o modelo sintético já existente em `PI/simulacao/cpa_demo.py`.

---

## Fontes consultadas (conferir antes de citar)

- [TOFU: Toggle Count Analysis made simple (ePrint 2022/129)](https://eprint.iacr.org/2022/129)
- [Vogls: Fast Interactive Full-timing Simulator for Pre-silicon Power SCA (arXiv 2607.15782)](https://arxiv.org/abs/2607.15782)
- [Bahrami et al., On the Practicality of Relying on Simulations in Different Abstraction Levels (SECRYPT 2022)](https://userpages.cs.umbc.edu/nkarimi/papers/SECRYPT_2022.pdf)
- [PROLEAD: A Probing-Based Hardware Leakage Detection Tool (TCHES)](https://tches.iacr.org/index.php/TCHES/article/view/9822)
- [SoK: Design Tools for Side-Channel-Aware Implementations (arXiv 2104.08593)](https://arxiv.org/pdf/2104.08593)
- [Application-Specific Power Side-Channel Attacks and Countermeasures: A Survey (arXiv 2512.23785)](https://arxiv.org/pdf/2512.23785)
- [Vivado Design Suite User Guide: Power Analysis and Optimization (UG907)](https://www.xilinx.com/support/documents/sw_manuals/xilinx2019_1/ug907-vivado-power-analysis-optimization.pdf)
- [Power Estimation Techniques for FPGAs (Univ. Toronto)](https://janders.eecg.utoronto.ca/pdfs/power_est.pdf)
- [Telescope: Pre-silicon Side-channel Leakage Assessment in SoC (ACM)](https://dl.acm.org/doi/10.1145/3708821.3736216)
- [Side-channel Testing Infrastructures in Pre- and Post-Silicon Settings (WPI)](https://digital.wpi.edu/downloads/1j92gb587)
