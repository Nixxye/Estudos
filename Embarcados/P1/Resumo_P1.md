# ELEW32 – Sistemas Embarcados – Resumo da P1

Prof. Douglas Renaux (UTFPR). Este resumo cobre tudo que está na pasta `Slides` e liga cada assunto à **Tabela da prova** (`Tabela Prova/QRC0001_UAL.pdf`, o "ARM and Thumb-2 Instruction Set – Quick Reference Card").

## Como ler as referências

| Marca | Significa |
|---|---|
| **(slide 3h, p.190)** | Arquivo `3h_exceptions.pdf`, slide cujo rodapé diz "Page 3.190". Nos outros arquivos o número é o "Page N" do rodapé. |
| **[Tabela p.2]** | Página física (1 a 6) do PDF da Tabela da prova. Ver o mapa em [§0.2](#s0-2). |
| **🧩 Complemento** | Conteúdo que a prova cobra mas que **não está no texto dos slides** da pasta (assembly, AAPCS, ThreadX). Escrevi a partir do padrão ARM/Keil. Confira com suas anotações de aula. |
| **[Resumo §X]** | Nos gabaritos, aponta para cá. Bom para estudar o que errou. |

> Limitação: extraí o texto dos slides. Figuras (diagramas de blocos, tabelas em imagem) só conferi nos slides de exceção (pilha de entrada e EXC_RETURN). O resto está descrito pelo texto ao redor.

## Índice

0. [Mapa da disciplina, da prova e da Tabela](#s0)
1. [Sistemas embarcados: definição e características](#s1)
2. [Segmentos de mercado e IoT](#s2)
3. [Arquitetura genérica de um sistema embarcado (9 camadas)](#s3)
4. [Gerações de computadores, RISC × CISC, pipeline](#s4)
5. [Economia de circuitos integrados](#s5)
6. [História da ARM e famílias Cortex](#s6)
7. [Características do Cortex-M](#s7)
8. [ISA do Cortex-M4: dados, modos, registradores, flags](#s8)
9. [🧩 Assembly Thumb-2 (usa a Tabela)](#s9), com [IT em detalhe (§9.9)](#s9-9) e [condições compostas (§9.10)](#s9-10)
10. [🧩 AAPCS e sub-rotinas](#s10)
11. [Exceções e interrupções](#s11)
12. [NVIC e CMSIS](#s12)
13. [Timers e SysTick](#s13), com [passo a passo (§13.4)](#s13-4) e [exemplos em C com handler (§13.5)](#s13-5)
14. [Modelagem: máquinas de estados (Statecharts/UML)](#s14)
15. [FORA DA P1: Concorrência, RTOS e ThreadX (só referência para a P2)](#s15)
16. [Convenções do professor (resumo para a prova)](#s16)
17. [O que acontece antes da `main()` (reset e inicialização)](#s17)

---

<a id="s0"></a>
## 0. Mapa da disciplina, da prova e da Tabela

<a id="s0-1"></a>
### 0.1 Disciplina (slide 1a aula)

- Temas: arquitetura de embarcados, arquitetura ARM Cortex (diagrama em blocos, registradores, **assembly**, acesso à memória), **interrupções**, **modelagem**, processo de desenvolvimento, concorrência, RTOS, escalonamento, conflito de recursos.
- Pesos: Prova 1 = 27%, Prova 2 = 33%, Projeto final = 25%, Labs 1-6 = 5%, avaliações semanais = 10%.
- Prova 1 marcada para 05-10 (data no slide "Calendário").
- Placa dos labs: Tiva (Cortex-M4), ferramenta Keil uVision (compilador v6). O montador é o **armasm** da Keil.

<a id="s0-2"></a>
### 0.2 A Tabela da prova (QRC0001 – 6 páginas)

| Página | Conteúdo | Use para |
|---|---|---|
| **p.1** | Operandos `Key to tables`; **ADD, ADC, SUB, SBC, RSB, ADR**, aritmética paralela, saturação | Somas, subtrações, 64 bits (ADDS + ADC), RSB para `3 - x` |
| **p.2** | **MUL, MLA, MLS, UMULL, SMULL, SDIV/UDIV**, **MOV, MVN, MOVT, MOV wide**, **ASR/LSL/LSR/ROR/RRX**, CLZ, **CMP, CMN, TST, TEQ, AND, EOR, ORR, ORN, BIC** | Quase todos os exercícios de aritmética, lógica, bits |
| **p.3** | Bit field (**BFC, BFI, SBFX, UBFX**), pack/extend (**SXTB, UXTB…**), **REV, REV16, RBIT**, select, **IT** (If-Then), desvios (**B, BL, BX, CBZ/CBNZ**) | Manipular bytes/bits, execução condicional |
| **p.4** | **LDR/STR** (+B, H, SB, SH, D), modos de endereçamento e **Notas 1-10** (limites do Thumb-2), **LDM/STM, PUSH/POP**, LDREX/STREX | Memória, pilha, vetores |
| **p.5** | Coprocessador, SWP, SRS/RFE, BKPT (praticamente não usado no Cortex-M) | – |
| **p.6** | **Condition Field** (EQ, NE, CS/HS, CC/LO, MI, PL, VS, VC, HI, LS, GE, LT, GT, LE, AL), **Flexible Operand 2**, tipos de shift, modos do processador | IT, desvios condicionais, `Rm, LSL #n` |

Pegadinha: a Tabela mistura ARM clássico e Thumb-2. As **Notas da p.4** dizem o que o Thumb-2 (Cortex-M) **não** permite (ex.: pós-indexado com registrador). Ver [§9.5](#s9-5).

---

<a id="s1"></a>
## 1. Sistemas embarcados: definição e características (slide 1a slides, p.5-11)

**Definição:** sistema computacional **embutido** em um dispositivo maior (equipamento, sistema ou veículo). Costuma ser **específico da aplicação**, com **restrições de tempo real**, e é muito usado em **malhas de controle** (lê sensores → processa → gera saídas). **Máquinas de estados finitas** são usadas para modelar seu comportamento (p.6).

**Características típicas (p.7-10):**

1. Baseado em microcontrolador: processador + memória não volátil (Flash) + RAM + muitas E/S e canais de comunicação.
2. Custo (arquiteturas guiadas por custo).
3. Eficiência energética (bateria; tendência de *energy harvesting*).
4. Heterogeneidade (grande variedade de HW e SW, ao contrário do desktop).
5. Restrições: **físicas** (tamanho, peso, temperatura, vibração, poeira, água), **recursos computacionais** (velocidade, memória, RAM, E/S), **tempo de resposta**.
6. Interconectado (IoT).
7. **Reliability** (confiabilidade): funcionar sob condições dadas por um período.
8. **Availability** (disponibilidade): funcionar em um instante/intervalo específico.
9. **Maintainability**: quão fácil e rápido restaurar após falha.
10. **Testability**: facilidade de estabelecer critérios de teste e verificá-los.
11. **Scalability**: suportar mais carga adicionando componentes.
12. **Safety**: não causar dano a pessoas, ambiente ou bens.
13. **Security**: proteger integridade e confidencialidade.

Cuidado com confundir: *reliability* (não falhar ao longo do tempo) × *availability* (estar operacional quando preciso) × *safety* (não causar dano) × *security* (proteção de informação).

---

<a id="s2"></a>
## 2. Segmentos de mercado e IoT (slide 1b, p.12-26)

Segmentos: eletrônica de consumo (telefones, consoles, impressoras, câmeras, TV, players), eletrodomésticos (máquina de lavar, lava-louças, ar-condicionado, micro-ondas), telecomunicações (roteadores, switches, telefones satélite), automação residencial, automação industrial, **transporte** (aviônica – *glass cockpit*, navegação – GPS e bússola eletrônica, automotivo – ADAS e veículos elétricos, eVTOL em 2024), defesa, **equipamento médico** (tomógrafo, ECG, glicosímetro, medidor de pressão, analisador de composição corporal) e novas áreas.

- **ADAS** = *Advanced Driver Assistance System*, associado aos níveis de autonomia de direção (p.22-23).
- **IoT** (p.25) aumenta a interconexão dos dispositivos.

---

<a id="s3"></a>
## 3. Arquitetura genérica de um sistema embarcado (slide 1c, p.27-39)

O modelo (Renaux e Stadzisz, 2007) é genérico porque **não existe um modelo verdadeiramente único**; serve para entender conceitos. São **9 camadas**: 2 de hardware e 7 de software.

| Camada | Nome | Ideia-chave |
|---|---|---|
| 1 | **Hardwired HW** | MCU, memória, E/S, conectores; ligação definida pelas trilhas da PCB (não muda depois de fabricado). Grande parte já está no SoC. |
| 2 | **Soft-wired HW** | Ligação programável: FPGA, CPLD, GAL, PAL, PLA, até ROM. |
| 3 | **HAL** (Hardware Abstraction Layer) | Funções que acessam diretamente o HW (*device drivers*). API padronizada facilita trocar SPI por I2C. Exemplo: SSP da Renesas. |
| 4 | **Adaptation Layer** (wrapper) | Traduz interfaces irregulares de drivers diferentes para uma padronizada, muitas vezes em tempo de compilação. |
| 5 e 6 | **RTOS** (2 camadas) | Parte dependente da arquitetura + parte independente (modularidade e portabilidade). Pequeno *footprint*, suporte a tempo real. |
| 7 | **RTOS Adaptation Layer** | Traduz a API do RTOS para um padrão (ex.: **CMSIS-RTOS**), permitindo reuso de Serviços e Aplicação. |
| 8 | **Services** | Bibliotecas prontas: TCP/IP, USB, protocolos, navegação, segurança, armazenamento. |
| 9 | **Application** | Funcionalidade específica; várias **tarefas concorrentes** cooperando, gerenciadas pelo RTOS. |

Características do **software embarcado** (p.33): (1) o toolchain gera **um único binário** com drivers, bibliotecas (RTOS, serviços) e aplicação; (2) tipicamente **uma única aplicação multitarefa** por toda a vida do dispositivo.

---

<a id="s4"></a>
## 4. Gerações, RISC × CISC, pipeline (slides 2a, p.40-60 e p.70-71)

### 4.1 Gerações (p.41-43)

0 = "computador" como pessoa/dispositivo que calcula; 1 = mecânicos e eletromecânicos; 2 = válvulas (anos 40: ENIAC, Colossus); 3 = transistores (50: PDP-1); 4 = CIs SSI (60: Apollo, IBM/360, VAX); 5 = microprocessador (70). Especulação para 2010+: quântico/orgânico/óptico, IA.

### 4.2 Por que surgiu o RISC (p.47-50)

- O hardware evoluiu e a arquitetura ficou **cada vez mais complexa**: instruções com alto conteúdo semântico para reduzir a **lacuna semântica** para linguagens de alto nível. Resultado: **microcódigo** (um "microprocessador dentro do processador" interpretando cada instrução).
- Pesquisa em programas reais mostrou que: (a) instruções complexas eram pouco usadas; (b) uma única instrução complexa pode **baixar o clock** de todo o processador; (c) sem sequência de execução regular, **pipeline era quase impossível**.
- Tese RISC: instruções simples e regulares → **pipeline** → maior desempenho.

### 4.3 Características RISC (p.51)

- Poucas instruções, simples.
- Arquitetura **Load/Store**: somente LD e ST (e variantes) acessam a memória. Todo o resto opera em **registradores**.
- **Muitos** registradores de uso geral.
- Mesma sequência lógica de execução para todas → pipeline; tipicamente **1 instrução por ciclo**.

### 4.4 Pipeline (p.52-57)

Requisitos: todas as instruções com as mesmas etapas e **regularidade** em tamanho, modos de endereçamento, decodificação e operandos.

Exemplo de 5 estágios: **1 Fetch; 2 Decode e leitura de operandos; 3 ALU (executa ou calcula endereço); 4 Acesso à memória; 5 Escrita no banco de registradores.** Nem toda instrução usa os estágios 4 e 5. Cada instrução leva 5 ciclos, mas, com o pipeline cheio, **uma termina a cada clock**.

**Limitações** (fazem a média ficar abaixo de 1 instrução/clock):

- **Data hazard:** instrução precisa de um valor produzido pela anterior, que só grava no estágio 5. Soluções: **stall**, **bypassing/forwarding** (usa o resultado do estágio 3), ou **reordenar** instruções.
- **Control hazard:** desvio muda o fluxo → o pipeline é **descarregado (flush)**; instruções já buscadas são descartadas.

### 4.5 RISC × CISC (p.58-60)

| | RISC | CISC |
|---|---|---|
| Nº de instruções | reduzido | grande |
| Complexidade | simples | alto conteúdo semântico |
| Registradores | muitos | poucos |
| Tamanho da instrução | fixo | variável (bytes) |
| Decodificação | simples (tabela em ROM) | complexa |
| Execução | simples, regular, ~1 ciclo | microprogramada, tempo varia muito |
| Pipeline | favorável (ganho ~N vezes, N = estágios) | pouco favorável |

Compilando o **mesmo programa**: no RISC o nº de instruções e o **tamanho em bytes** costumam ser **maiores**, mas o **desempenho** costuma ser **melhor**. O projeto do RISC é mais simples: ciclo de projeto menor, menos transistores, menos área.

### 4.6 RISC × CISC hoje (p.70-71)

Convergência (ainda sem nome): conjunto grande de instruções, **instruções regulares** (pipeline), pipelines de **3 a 20 estágios**, **sem microcódigo**. O conjunto do Cortex-M (incluindo M23 e M33) é um exemplo.

---

<a id="s5"></a>
## 5. Economia de circuitos integrados (slide 2b, p.61-69)

- Custo do chip depende de: **custo do die** (custo do wafer ÷ dies bons), **testes** (no die e após encapsulamento), **encapsulamento** e **yield** (% de chips funcionais).
- O custo por transistor cai **exponencialmente** com a tecnologia.
- Quanto maior o chip, **menor o yield** → custo **não** cresce linearmente com a área. Existe uma **faixa de área com menor custo por transistor** ("sweet spot").
- Em 2018 a tecnologia mais econômica era **20 nm**.
- **Decisão-chave (p.68):** com T milhões de transistores no sweet spot, usar em (1) núcleo CISC + pouca cache/memória/periféricos, ou (2) **núcleo RISC + muita cache/memória/periféricos**. **A maioria dos fabricantes escolhe a opção 2.**
- Tendência (p.69): MCUs ficam ~5 anos atrás do estado da arte.

---

<a id="s6"></a>
## 6. História da ARM e famílias Cortex (slides 3a e 3b, p.72-121)

### 6.1 Linha do tempo

| Ano | Fato |
|---|---|
| 1981 | Acorn Computer lança o **BBC Micro** (CPU 6502 de 2 MHz, 8 bits). |
| 1984 | Novos requisitos para substituir o 6502. Intel e Motorola 68000 avaliados; o 68000 tinha **resposta a interrupção lenta demais**. Inspirados no RISC de Patterson (Berkeley) e MIPS (Hennessy, Stanford), decidem projetar seu próprio RISC de 32 bits. |
| 1985 | **ARM1** (abril). ARM = *Acorn RISC Machine*. Frase de Hauser: equipe sem dinheiro e sem gente → "manter simples". |
| 1987 | ARM2 (BBC Archimedes 300, até 16 MB). |
| 1990 | Fundação da **ARM** = *Advanced RISC Machines* (apoio da VLSI, Acorn e Apple). Modelo de negócio: **empresa de IP**, só projeta processadores (licencia). |
| 1994 | **ARM7TDMI**, grande sucesso. |
| 2004 | Lançadas as séries **Cortex-M, Cortex-R e Cortex-A**. |
| 2016 | Cortex-M23 e M33 (nota: o slide diz 2016). |
| 2018 | Cortex-M35P. |

ARM pertence ao SoftBank (na época do slide, negociação com NVidia desde 2020). Para cada versão de arquitetura (ARMv1…ARMv8.3-A) há várias implementações.

### 6.2 Famílias

- **Cortex-A** (aplicação): 32/64 bits, ARMv8-A (64 bits). Exemplos: Raspberry Pi 3 (BCM2837, Cortex-A53 quad, 1,2 GHz), Pi 4 (BCM2711, Cortex-A72 quad, 1,5 GHz), NVIDIA Tegra/Orin, Qualcomm Snapdragon.
- **Cortex-R** (tempo real).
- **Cortex-M** (microcontroladores): M0, M0+, M3, M4, M7, M23, M33, M35P, M55.

Versões de arquitetura por núcleo (p.81): M0/M0+/M23 → mais simples; **M3/M4/M7 → ARMv7-M**; M23/M33 → ARMv8-M.

---

<a id="s7"></a>
## 7. Características do Cortex-M (slide 3b, p.122-136)

Lista central (p.122), **decore**:

1. **Pipeline de 3 estágios** (Fetch, Decode, Execute), exceto M7 e M55.
2. **Arquitetura Harvard** (barramentos separados de código e dados), exceto M0 e M0+.
3. Projetado para **eficiência energética** (inclui deep sleep de baixíssimo consumo).
4. Conjunto **Thumb-2** = mistura de instruções de 16 e 32 bits.
5. **NVIC** definido na própria arquitetura: interrupção vetorada de baixa latência.
6. **Tail-chaining** e **late arrival** ([§11.7](#s11-7)).
7. **Bit-banding**: acesso rápido a bits de memória e de periféricos mapeados.
8. **MPU** (Memory Protection Unit).
9. A maioria das instruções pode ser **condicional** (via IT).

**ARM7TDMI × Cortex-M (p.123):** o ARM7TDMI tinha dois conjuntos, **ARM** (32 bits, mais desempenho, menor densidade) e **Thumb** (16 bits, menor desempenho, maior densidade). O Cortex-M tem **só Thumb-2**: densidade de código do Thumb e desempenho parecido com o ARM.

**Pipeline (p.130-135):** duas sequências de execução: (1) Fetch → Decode → Execute (lógica/aritmética) ou (2) Fetch → Decode → Execute (cálculo de endereço) → Acesso à memória de dados. Desvio indireto causa **flush** (sem forwarding). A Harvard permite acesso simultâneo a código e dados.

---

<a id="s8"></a>
## 8. ISA do Cortex-M4 (slide 3c, p.137-153)

A ISA é a visão do programador: tipos de dados, modos, registradores, conjunto de instruções, acesso à memória, processamento de exceções.

### 8.1 Tipos de dados (p.139)

| Tipo | Tamanho | Observação |
|---|---|---|
| bit | 1 | *bit-banding* |
| byte | 8 | cada byte da memória é endereçável |
| half-word | 16 | endereço = endereço do byte menos significativo |
| word | 32 | idem |
| double-word | 64 | par de registradores, ex.: **R1:R0 (R1 = mais significativo)**; endereço = do byte menos significativo |

Consequência para 64 bits em memória (little-endian): **word baixa no endereço menor, word alta em endereço+4**. Usado na Q3 da prova 2022 ([Gabarito P2022 §Q3](Gabarito_Prova2022.md#q3)).

### 8.2 Modos do processador e pilhas (p.140-141)

| Modo | Para quê |
|---|---|
| **Privileged Thread** | execução do SO |
| **Unprivileged Thread** | código de aplicação |
| **Privileged Handler** | tratamento de exceções |

Duas pilhas: **MSP** (Main SP: SO e handlers) e **PSP** (Process SP: threads da aplicação). Só uma ativa por vez, escolhida no registrador **CONTROL**; **R13 (SP)** aponta para a ativa. Em Handler mode o bit SPSEL é sempre 0 (usa MSP).

### 8.3 Registradores (p.143-153)

- **R0-R12**: uso geral, 32 bits. **R0-R7** = *low*, **R8-R15** = *high*.
- **R13 = SP** (topo da pilha), **R14 = LR** (endereço de retorno), **R15 = PC** (próxima instrução a buscar).
- Um registrador guarda inteiro sem sinal 0 a 4.294.967.295 ou com sinal −2.147.483.648 a 2.147.483.647. Em hexa: 8 dígitos. Endereços são de 32 bits, então um registrador guarda um endereço.
- **Ponto flutuante** (opcional no M4): S0-S31 (32 bits) ou D0-D15 (64 bits, D0 = S1:S0).
- **Especiais:** xPSR (= APSR + IPSR + EPSR), PRIMASK, FAULTMASK, BASEPRI, CONTROL.

### 8.4 APSR – flags (p.148) **(usado o tempo todo com a Tabela)**

| Flag | Bit | Significado |
|---|---|---|
| **N** | 31 | **Negativo** (resultado negativo em complemento de 2). |
| **Z** | 30 | **Zero.** Após comparação: valores iguais. |
| **C** | 29 | **Carry.** Soma sem sinal com estouro. Em subtração sem sinal, indica "underflow" no texto do slide (ver nota abaixo). |
| **V** | 28 | **Overflow** em operação aritmética **com sinal**. |
| Q | 27 | Saturação (DSP). |
| GE | 19:16 | ≥ para instruções SIMD. |

Nota sobre o **C na subtração** 🧩: no ARM, `SUBS`/`CMP` deixam **C = 1 quando NÃO há empréstimo** (Rn ≥ Rm sem sinal) e **C = 0 quando há empréstimo**. É por isso que "unsigned higher or same" = CS/HS. Usado no [Gabarito Ex.5](Gabarito_Exercicios.md#ex5).

Como calcular flags de `ADDS` / `SUBS`:

- **Z**: resultado = 0. **N**: bit 31 do resultado.
- **C (soma)**: houve vai-um do bit 31. **C (subtração)**: 1 se sem empréstimo.
- **V**: dois operandos de mesmo sinal (soma) ou de sinais diferentes (subtração) produzem resultado de sinal "errado". Regra prática: `+ + → −` ou `− − → +` na soma.

### 8.5 IPSR e EPSR (p.149-150)

- **IPSR[8:0]** = nº da exceção ativa. **0 = nenhuma → Thread mode; ≠ 0 → Handler mode.**
- **EPSR:** **T (bit 24) = Thumb.** No Cortex-M **deve ser sempre 1**, senão ocorre exceção. Também ICI/IT (bits 26:25, 15:10) para instruções multi-ciclo interrompidas e blocos IT.

### 8.6 Registradores de máscara e CONTROL (p.151-152)

| Registro | Efeito |
|---|---|
| **PRIMASK[0]** | 1 = mascara exceções de prioridade configurável (prioridade 0 e "menores"). |
| **FAULTMASK[0]** | 1 = mascara também HardFault (nível −1); todas as exceções da 3 em diante mascaradas. |
| **BASEPRI[7:0]** | Nível mínimo de prioridade para preempção; bloqueia exceções com valor **maior ou igual** ao BASEPRI (valor maior = prioridade menor). 0 = sem efeito. |
| **CONTROL.nPRIV** (bit 0) | Em Thread mode: 0 privilegiado, 1 não privilegiado. |
| **CONTROL.SPSEL** (bit 1) | 0 = MSP, 1 = PSP. |
| **CONTROL.FPCA** (bit 2) | 1 = salvar contexto de ponto flutuante na exceção. |

### 8.7 Reset (p.154)

Após reset: o SP inicial e o PC vêm da tabela de vetores ([§11.5](#s11-5)). Fluxo completo até a `main` em [§17](#s17).

---

<a id="s9"></a>
## 9. 🧩 Assembly Thumb-2 (Keil armasm) – com a Tabela

Os slides fornecidos param antes da parte de assembly, mas as listas de exercícios e a prova são de assembly. Esta seção é o mínimo para resolvê-las usando a Tabela.

<a id="s9-1"></a>
### 9.1 Formato e convenções

```
rotulo      MNEMONICO   destino, origem1, origem2   ; comentário
```
- Mnemônicos e registradores em maiúsculas ou minúsculas (o laboratório usa ambos). Labels na coluna 1, instruções recuadas.
- Sufixo **S** (`ADDS`, `SUBS`) **atualiza as flags** (coluna "S updates" da Tabela p.1-2). Sem S, as flags não mudam.
- Sufixo de condição (`EQ`, `NE`…) só em instruções dentro de um bloco **IT** ([§9.6](#s9-6)) ou em desvios (`BEQ`).
- Diretivas do armasm (do lab): `PRESERVE8`, `THUMB`, `AREA |.text|, CODE, READONLY, ALIGN=2`, `EXPORT nome`, `nome PROC … ENDP`, `END`.

<a id="s9-2"></a>
### 9.2 Aritmética e lógica **[Tabela p.1-2]**

| Quero | Instrução | Observação |
|---|---|---|
| Soma | `ADD Rd, Rn, <Op2>` / `ADDS` | Op2 pode ter shift: `ADD R0, R1, R1, LSL #2` = R1×5 |
| Soma com carry | `ADC Rd, Rn, <Op2>` | base para **64 bits** |
| Subtração | `SUB Rd, Rn, <Op2>` | |
| Subtração invertida | `RSB Rd, Rn, <Op2>` | `RSB R0,R1,#0` = −R1; `RSB R0,R1,#3` = 3 − R1 |
| Multiplicação | `MUL Rd, Rm, Rs` | 32 bits menos significativos |
| Mult. e soma / subtração | `MLA Rd,Rm,Rs,Rn` (Rn + Rm×Rs); `MLS Rd,Rm,Rs,Rn` (Rn − Rm×Rs) | MLS calcula **resto**: `r = a − (a/b)×b` |
| Divisão | `UDIV` / `SDIV Rd, Rn, Rm` | Rd = Rn / Rm |
| Cópia | `MOV Rd,<Op2>`, `MVN` (NOT) | |
| Constante 16 bits / 32 bits | `MOV Rd,#imm16` (wide), `MOVT Rd,#imm16` | par MOVW+MOVT monta 32 bits |
| Deslocamentos | `LSL`, `LSR`, `ASR`, `ROR`, `RRX` | LSR: lógico (sem sinal). **ASR: aritmético (com sinal)** |
| Comparações | `CMP` (Rn − Op2), `CMN` (Rn + Op2), `TST` (Rn AND Op2), `TEQ` (Rn EOR Op2) | só mudam flags |
| Lógicas | `AND`, `ORR`, `EOR`, `ORN`, `BIC` (Rn AND NOT Op2) | |
| Contar zeros à esquerda | `CLZ Rd, Rm` | |

**Flexible Operand 2 [Tabela p.6]:** ou uma **constante imediata** ou um registrador com shift opcional. No Thumb-2 a constante imediata deve ser: um byte deslocado de qualquer quantidade, ou padrões `0x00XY00XY`, `0xXY00XY00`, `0xXYXYXYXY`. Ex.: `#0xFF00` vale; `#0xFFFF` **não** vale (usar `MOVW`, `BFC`, ou duas instruções).

**Truques que aparecem em prova:**

- Multiplicar por constante sem MUL: `×5 = ADD Rd,Rn,Rn,LSL #2`; `×9 = ADD Rd,Rn,Rn,LSL #3`; `×2ⁿ = LSL`; `×10 = ×5 então LSL #1`; `×100 = ×5, ×5, LSL #2`.
- Dividir por 2ⁿ: `LSR` (sem sinal) ou `ASR` (com sinal, arredonda para −∞). Resto de 2ⁿ: `AND #(2ⁿ−1)` ou `UBFX`.
- `RSB` resolve "constante − variável".

<a id="s9-3"></a>
### 9.3 Manipulação de bits **[Tabela p.2 e p.3]**

| Quero | Instrução |
|---|---|
| Limpar bits | `BIC Rd, Rn, #máscara` ou `BFC Rd, #lsb, #largura` (p.3) |
| Setar bits | `ORR Rd, Rn, #máscara` |
| Inverter bits | `EOR Rd, Rn, #máscara` |
| Extrair campo | `UBFX Rd, Rn, #lsb, #largura` (p.3) |
| Inserir campo | `BFI Rd, Rn, #lsb, #largura` (p.3): copia os bits [largura-1:0] de Rn para Rd a partir de lsb |
| Inverter ordem de bytes | `REV` (32 bits), `REV16`; inverter bits: `RBIT` (p.3) |
| Estender byte/half | `UXTB`, `UXTH`, `SXTB`, `SXTH` (p.3) |

Convenção little-endian do enunciado: **bit 0 é o LSb**; "primeiro byte" = bits 7:0, "último byte" = bits 31:24.

<a id="s9-4"></a>
### 9.4 Acesso à memória (Load/Store) **[Tabela p.4]**

Como o Cortex-M é **RISC load/store** ([§4.3](#s4)), só `LDR`/`STR` (e variantes) tocam a memória.

| Variante | Tamanho |
|---|---|
| `LDR/STR` | word (32) |
| `LDRB/STRB`, `LDRSB` | byte (sem/com extensão de sinal) |
| `LDRH/STRH`, `LDRSH` | half-word |
| `LDRD/STRD Rd1, Rd2, [Rn]` | double-word em 2 registradores (Rd1 = endereço baixo) |
| `LDM/STM`, `PUSH/POP` | múltiplos registradores |

**Pseudo-instrução:** `LDR Rd, =constante_ou_rótulo` carrega uma constante de 32 bits (o assembler escolhe MOV/MVN ou *literal pool*). A sintaxe com `=` é **diferente** da instrução real `LDR Rd,[Rn]`. Ver [Gabarito Ex.17](Gabarito_Exercicios.md#ex17).

<a id="s9-5"></a>
### 9.5 Modos de endereçamento **[Tabela p.4 e Notas 1-10]**

| Modo | Sintaxe | Endereço usado | Rn depois |
|---|---|---|---|
| Offset imediato | `[Rn, #off]` | Rn + off | inalterado |
| **Pré-indexado** | `[Rn, #off]!` | Rn + off | Rn + off |
| **Pós-indexado** | `[Rn], #off` | Rn | Rn + off |
| Offset por registrador | `[Rn, Rm{, LSL #n}]` | Rn + (Rm << n) | inalterado |
| Pós-indexado por registrador | `[Rn], Rm` | Rn | Rn + Rm |

Limites do **Thumb-2** (Cortex-M), da Tabela p.4:

- Offset imediato: −255 a +4095 sem write-back; **−255 a +255** com write-back (Nota 1).
- Offset por registrador: shift restrito a **`LSL #0` a `#3`** (Nota 3).
- **Pós-indexado por registrador não existe no Thumb-2** (Nota 4, coluna Thumb-2 = "Not available"). E, na prática, register-offset com `!` também não é aceito no Cortex-M 🧩.
- Word alinhado em 4 bytes: `[Rn,#4*i]`; vetor de words: `[Rn, Ri, LSL #2]`.

<a id="s9-6"></a>
### 9.6 Execução condicional (IT) e desvios **[Tabela p.3 e p.6]**

- Condições **[Tabela p.6, Condition Field]**: `EQ` (Z=1), `NE`, `CS/HS` (C=1, sem sinal ≥), `CC/LO` (sem sinal <), `MI` (N=1), `PL`, `VS`, `VC`, `HI` (sem sinal >), `LS` (sem sinal ≤), `GE`, `LT`, `GT`, `LE` (com sinal), `AL`.
- **Com sinal → GE/LT/GT/LE. Sem sinal → HS/LO/HI/LS.** Erro comum: usar o par errado.
- **IT** (If-Then, Tabela p.3): `IT{x{y{z}}} cond` torna condicionais as 1 a 4 instruções seguintes. `T` = então (mesma condição), `E` = senão (condição inversa). **Detalhes completos em [§9.9](#s9-9); condições compostas em [§9.10](#s9-10).**

```
CMP   R1, #9
ITE   LT           ; se R1 < 9 ... senão
ADDLT R1, R1, #1   ;   então
MOVGE R1, #0       ;   senão (GE é o inverso de LT)
```
- Desvios: `B rótulo`, `BEQ/BNE/BGT…` (condicionais), `BL` (chamada, grava LR), `BX LR` (retorno), `CBZ/CBNZ Rn,rótulo` (só para frente, faixa curta; não altera flags).
- **Pipeline:** cada desvio tomado causa flush ([§4.4](#s4)). Por isso IT é bom para trechos curtos.

Padrões de tradução:

| C | Assembly |
|---|---|
| `if (x==0) x+=3;` | `CMP R1,#0` / `IT EQ` / `ADDEQ R1,R1,#3` |
| `while` com contador | `SUBS R1,R1,#1` / `BNE loop` |
| `a || b` | encadear `CMP` e `CMPNE` em bloco IT, ou desviar |
| faixa `lo ≤ x ≤ hi` | `SUB R3,R1,#lo` / `CMP R3,#hi-lo` / unsigned `LS` |

O truque da **faixa com uma só comparação sem sinal** funciona porque, se x < lo, `x − lo` vira um número sem sinal enorme.

<a id="s9-7"></a>
### 9.7 Pilha, PUSH/POP **[Tabela p.4]**

- Pilha **cheia e decrescente**: `PUSH` decrementa SP e depois grava; `POP` lê e depois incrementa.
- `PUSH {lista}` = `STMDB SP!, {lista}`; `POP {lista}` = `LDMIA SP!, {lista}`.
- **A ordem escrita na lista NÃO importa.** O hardware guarda o **registrador de menor número no menor endereço**. `PUSH {R4,R5}` e `PUSH {R5,R4}` são iguais.
- `POP {..., PC}` faz retorno (equivale a `BX LR` se o `PUSH` tiver salvo LR). O bit 0 do valor carregado no PC deve ser 1 (Thumb); se for 0 ocorre falha por estado inválido ([§8.5](#s8), [§11.5](#s11-5)).

<a id="s9-8"></a>
### 9.8 Aritmética de 64 bits

Soma (ver [Gabarito P2022 Q3](Gabarito_Prova2022.md#q3)):

```
ADDS R1, R1, #1     ; parte baixa +1, C = vai-um
ADC  R2, R2, #0     ; parte alta + carry
```
`ADC` = Rd := Rn + Op2 + C **[Tabela p.1]**. Dados de 64 bits em memória little-endian: baixa no endereço menor ([§8.1](#s8)). `LDRD R1,R2,[R0]` / `STRD R1,R2,[R0]` **[Tabela p.4]** carregam/gravam os dois words de uma vez.

<a id="s9-8b"></a>
### 9.8.1 Inteiros de 64 bits em detalhe (soma, memória, comparação)

**Por que existe:** o registrador tem 32 bits, mas um contador de tempo (milissegundos desde o boot, por exemplo) pode estourar 32 bits. Guarda-se o valor em **dois words**. Todo o truque é **propagar o carry (vai-um)** da word baixa para a alta.

**1) Como o número fica na memória (little-endian).** Um `uint64_t` no endereço `A` ocupa 8 bytes:

| Endereço | Conteúdo | No registrador |
|---|---|---|
| `A` | **word baixa** (bits 31:0) | Rlo |
| `A + 4` | **word alta** (bits 63:32) | Rhi |

A word **baixa fica no endereço menor**. Exemplo: o valor `0x0000_0001_FFFF_FFFF` fica com `[A] = 0xFFFFFFFF` e `[A+4] = 0x00000001`.

**2) Ler e gravar com uma instrução [Tabela p.4].**

```
LDRD  R1, R2, [R0]        ; R1 <- [R0] (baixa), R2 <- [R0+4] (alta)
STRD  R1, R2, [R0]        ; [R0] <- R1,  [R0+4] <- R2
```
O 1º registrador da lista recebe o endereço menor. O endereço precisa ser alinhado em 4 bytes. O offset imediato permitido é múltiplo de 4 (até ±1020).

**3) Somar com carry [Tabela p.1].**

| Operação (64 bits) | Instruções | Por quê |
|---|---|---|
| `x + 1` | `ADDS Rlo,Rlo,#1` / `ADC Rhi,Rhi,#0` | `ADDS` (com **S**) grava o carry na flag C; `ADC` soma o C à parte alta. |
| `x + y` | `ADDS Xlo,Xlo,Ylo` / `ADC Xhi,Xhi,Yhi` | idem |
| `x − y` | `SUBS Xlo,Xlo,Ylo` / `SBC Xhi,Xhi,Yhi` | `SBC` = Rn − Op2 − (1 − C): usa o "empréstimo" que `SUBS` deixou |

**Regras:** (a) a primeira instrução **precisa ter o S** (senão o carry não é atualizado); (b) o `ADC`/`SBC` **não precisa de S** (só se quiser flags do resultado de 64 bits); (c) **nada** pode alterar C entre as duas.

**4) Teste de mesa (sempre faça).**

| Caso | R1 (baixa) | R2 (alta) | Depois de `ADDS R1,R1,#1` | Depois de `ADC R2,R2,#0` |
|---|---|---|---|---|
| comum | 0x00000005 | 0x00000000 | R1 = 6, **C = 0** | R2 = 0 + 0 + 0 = 0 → **0x0000_0000_0000_0006** |
| estouro da baixa | 0xFFFFFFFF | 0x00000000 | R1 = 0, **C = 1** (e Z = 1) | R2 = 0 + 0 + 1 = 1 → **0x0000_0001_0000_0000** |
| estouro total | 0xFFFFFFFF | 0xFFFFFFFF | R1 = 0, C = 1 | R2 = 0 (volta a zero; 64 bits cheios) |

Ordem de grandeza: se o contador soma 1 a cada 2 ms, os 32 bits baixos estouram em ~99 dias, e os 64 bits só em ~1,2 bilhão de anos. O carry é raro, mas o código **precisa estar correto**.

**5) Comparar 64 bits sem sinal (extra).** Compare a parte alta primeiro; se for igual, compare a baixa:
```
CMP    R2, R4          ; alta de x com alta de y
IT     EQ
CMPEQ  R1, R3          ; só se as altas forem iguais, compara as baixas
; agora HS/LO/HI/LS valem para o valor de 64 bits (sem sinal)
```

**Erros comuns:** `ADD` no lugar de `ADDS`; `ADD` no lugar de `ADC` na parte alta; inverter alta e baixa na memória; esquecer o alinhamento em 4 do `LDRD`.

<a id="s9-9"></a>
### 9.9 🧩 A instrução IT (If-Then) em detalhe **[Tabela p.3 (If-Then) e p.6 (Condition Field)]**

**Para que serve:** executar de 1 a 4 instruções **condicionalmente, sem desvio**. Em vez de `BNE pula / ADD ... / pula:` (que faz o pipeline dar *flush*, [§4.4](#s4)), o `IT` deixa as instruções entrarem no pipeline e simplesmente **não têm efeito** se a condição for falsa. É a resposta padrão para "não utilize instruções de salto" ([Gabarito Ex.3-4](Gabarito_Exercicios.md#ex3)).

**Sintaxe:** `IT{x{y{z}}} cond`

- `cond` = qualquer código da Tabela p.6 (EQ, NE, HS, LO, MI, PL, VS, VC, HI, LS, GE, LT, GT, LE).
- Cada letra opcional `x`, `y`, `z` é **T** (*Then*: executa se `cond` for verdadeira) ou **E** (*Else*: executa se `cond` for falsa, ou seja, com a condição **inversa**).
- A 1ª instrução do bloco é sempre "Then". Logo o bloco tem 1 a 4 instruções: `IT`, `ITT`, `ITE`, `ITTT`, `ITTE`, `ITET`, `ITEE`, `ITTTT`, ... (o nº de letras = nº de instruções).
- O `IT` é uma instrução extra de 16 bits; ela mesma não faz nada além de definir o bloco.

**Regra de ouro:** cada instrução do bloco leva o **sufixo da condição correspondente** à sua letra. `T` usa `cond`; `E` usa a **inversa**.

| cond | inversa | | cond | inversa |
|---|---|---|---|---|
| EQ | NE | | HI | LS |
| HS (CS) | LO (CC) | | GE | LT |
| MI | PL | | GT | LE |
| VS | VC | | AL | (não usar) |

**Exemplos**

```
        ; if (x == 0) x += 3;                 -> 1 instrução condicional
        CMP     R1, #0
        IT      EQ
        ADDEQ   R1, R1, #3

        ; if (x < 9) x++; else x = 0;         -> ITE: 1 "then" + 1 "else"
        CMP     R1, #9
        ITE     LT
        ADDLT   R1, R1, #1                    ; T: condição LT
        MOVGE   R1, #0                        ; E: inversa de LT = GE

        ; R0 = max(R0, R1)  (com sinal)
        CMP     R0, R1
        IT      LT
        MOVLT   R0, R1

        ; R0 = |R0|
        CMP     R0, #0
        IT      LT
        RSBLT   R0, R0, #0                    ; 0 - R0

        ; if (a) {p; q;} else {r;}            -> ITTE (3 instruções)
        CMP     R1, R2
        ITTE    GT
        ADDGT   R3, R3, #1                    ; T
        SUBGT   R4, R4, #1                    ; T
        MOVLE   R5, #0                        ; E (inversa de GT)
```

**Detalhes que pegam em prova**

1. **Escolha do par sem sinal × com sinal:** números com sinal → `GE/LT/GT/LE`; sem sinal → `HS/LO/HI/LS` ([§9.6](#s9-6)). O `IT` não conserta a escolha errada.
2. **As flags são lidas em cada instrução do bloco**, não só no `IT`. Se uma instrução dentro do bloco atualiza as flags (ex.: `CMPNE`), as seguintes veem as flags **novas**. Isso é o que permite encadear testes (`||`) no [Ex.4a](Gabarito_Exercicios.md#ex4): `CMP` / `ITT NE` / `CMPNE` / `CMPNE`. Cuidado quando não for essa a intenção.
3. **Instruções sem `S` não mexem nas flags.** Por isso o `SUBHI` seguido de `CMPHI` no [Ex.4b](Gabarito_Exercicios.md#ex4) mantém a condição `HI` válida.
4. **Desvio dentro de IT:** só é permitido como **última** instrução do bloco. Em geral prefira `BEQ`/`BNE` normais fora do bloco quando o corpo for grande.
5. **Limite de 4 instruções.** Corpo maior ou com laços → use desvio. Vale a pena o IT quando o corpo é curto (1 a 2 instruções): custa 1 ciclo do `IT` + 1 ciclo por instrução (**executada ou não**), sem *flush*. Um desvio tomado custa o *flush* do pipeline.
6. **Condição do `IT` = condição do sufixo.** Escrever `IT EQ` e depois `ADDNE` é erro (o montador reclama, ou a instrução fica com a condição errada).
7. **`AL`/omitido:** não faz sentido dentro de IT.
8. **Interrupção no meio do bloco:** o estado do IT é guardado nos bits **ICI/IT do EPSR** ([§8.5](#s8)) e salvo no empilhamento em xPSR ([§11.7](#s11-7)); o bloco continua corretamente depois do retorno da ISR. Você não precisa tratar isso.
9. **Sem IT, nada é condicional:** em Thumb-2 uma instrução como `ADDEQ` sozinha, sem `IT` antes, não é válida (o armasm pode inserir o `IT` automaticamente em alguns modos, mas **escreva sempre o `IT` explicitamente** na prova).

**Receita para traduzir um `if`:** (1) `CMP`/`TST` que gera as flags; (2) escolha `cond` para o ramo "then"; (3) `IT` com `T` para cada instrução do then e `E` para cada do else, nessa ordem; (4) escreva cada instrução com o sufixo certo (`cond` ou inversa). Se o total passar de 4 instruções ou houver `if` aninhado, use desvios ([Ex.3e](Gabarito_Exercicios.md#ex3)).

<a id="s9-10"></a>
### 9.10 🧩 Múltiplas condições em um `if` (`&&`, `||`, faixas) **[Tabela p.2 (CMP, TST, SUB), p.3 (IT), p.6 (condições)]**

Ideia central: o processador só tem **um conjunto de flags** (N, Z, C, V). Uma condição composta precisa ser quebrada em **testes sucessivos**. Há quatro técnicas; escolha pela situação.

| Técnica | Quando usar | Custo |
|---|---|---|
| **A. Desvios em curto-circuito** | Serve para **qualquer** combinação (`&&`, `||`, mistas, corpo grande) | Desvios tomados causam *flush* ([§4.4](#s4)) |
| **B. Cadeia com IT** | Só quando os testes são de **igualdade** (`==` / `!=`) e o corpo é curto | Sem desvios |
| **C. Faixa com uma comparação sem sinal** | `lo <= x <= hi` | 2 instruções |
| **D. Máscara + comparação** | Testar vários bits de uma vez | 2 instruções |

#### A. Desvios em curto-circuito (método geral e sempre correto)

Regra: traduza como o C avalia (da esquerda para a direita, parando assim que o resultado é conhecido).

- **`if (A && B) corpo`**: se `A` for falso, pule para o fim; se `B` for falso, pule para o fim. Desvie com a condição **inversa** do teste.
- **`if (A || B) corpo`**: se `A` for verdadeiro, pule para o corpo; se `B` for falso, pule para o fim. (Desvie com a condição **direta** de `A` e a **inversa** de `B`.)

```
        ; if (x > 5 && y < 3) z = 1;        (todos com sinal)
        CMP     R1, #5
        BLE     fim              ; A falso (inversa de GT = LE) -> fim
        CMP     R2, #3
        BGE     fim              ; B falso (inversa de LT = GE) -> fim
        MOV     R0, #1           ; corpo
fim

        ; if (x == 1 || y > 10) z = 1;
        CMP     R1, #1
        BEQ     corpo            ; A verdadeiro -> corpo
        CMP     R2, #10
        BLE     fim              ; B falso -> fim
corpo   MOV     R0, #1
fim

        ; if ((x > 0 && x < 10) || x == 20) z = 1;    (mista: E dentro do OU)
        CMP     R1, #0
        BLE     testa20          ; primeiro E falhou -> ainda pode ser 20
        CMP     R1, #10
        BLT     corpo            ; 0 < x < 10 verdadeiro
testa20 CMP     R1, #20
        BNE     fim
corpo   MOV     R0, #1
fim
```
Como montar as mistas: cada termo E vira uma sequência de testes que, ao falhar, **cai no próximo termo do OU**; ao passar por inteiro, **vai ao corpo**. O último termo do OU, se falhar, vai ao **fim**.

#### B. Cadeia com IT (só para igualdades)

Como o `CMP` dentro do bloco IT atualiza as flags para as instruções seguintes ([§9.9](#s9-9), item 2), dá para encadear.

```
        ; y = (x==0x20 || x==0x22 || x==0x15) ? 1 : 0;        (OU de igualdades)
        MOV     R2, #0
        CMP     R1, #0x20
        ITT     NE               ; só continua testando enquanto ainda for diferente
        CMPNE   R1, #0x22
        CMPNE   R1, #0x15
        IT      EQ               ; EQ ao final = algum teste bateu
        MOVEQ   R2, #1

        ; y = (a == 1 && b == 2) ? 1 : 0;                      (E de igualdades)
        MOV     R2, #0
        CMP     R0, #1
        IT      EQ               ; só testa b se a == 1
        CMPEQ   R1, #2
        IT      EQ               ; EQ ao final = os dois bateram
        MOVEQ   R2, #1
```
**Armadilha (por isso B só vale para igualdades):** se o 1º teste falhar, as instruções condicionais são puladas e as **flags continuam as do 1º teste**. No `&&`/`||` de igualdades isso é benigno: falhou o 1º ⇒ flags NE ⇒ o teste final `EQ` é falso. Mas com desigualdades ela **engana**: em `if (a > 5 && b < 3)`, se `a = 2` o 1º `CMP` deixa as flags em **LT**, e um teste final `LT` (que era para ser o de `b < 3`) seria verdadeiro por engano. Nesses casos use a técnica A (ou C).

#### C. Faixa `lo <= x <= hi` com **uma** comparação sem sinal

Em vez de `x >= lo && x <= hi` (dois testes), use `(x - lo) <= (hi - lo)` **sem sinal**. Se `x < lo`, `x - lo` vira um número sem sinal enorme e o teste falha sozinho.

```
        ; if (0x10 <= x && x <= 0x29) y = 1;
        SUB     R3, R1, #0x10    ; x - lo
        CMP     R3, #0x19        ; hi - lo = 0x29 - 0x10
        IT      LS               ; LS = sem sinal <=
        MOVLS   R2, #1
```
Duas faixas (OU): teste a 1ª; **se fora** (`HI`), teste a 2ª; ao final `LS` = dentro de alguma. Esse é o [Ex.4b](Gabarito_Exercicios.md#ex4):
```
        SUB     R3, R1, #0x10
        CMP     R3, #0x19
        ITT     HI               ; fora da 1ª faixa -> testa a 2ª
        SUBHI   R3, R1, #0x31    ; (sem S: não altera flags, HI continua valendo)
        CMPHI   R3, #0x2B        ; 0x5C - 0x31
        IT      LS
        MOVLS   R2, #1
```
Isto funciona com a mesma razão da armadilha acima só que ao contrário: se a 1ª faixa acerta (`LS`), o `ITT HI` é pulado e as flags `LS` seguem valendo para o teste final.

#### D. Vários bits com máscara

```
        ; if (x & 0x05) == 0x05   (bits 0 e 2 ambos em 1)
        AND     R3, R1, #0x05
        CMP     R3, #0x05
        IT      EQ
        ...

        ; if (x & 0x05)           (algum dos bits 0 ou 2)
        TST     R1, #0x05        ; flags de x AND 0x05; Z = 1 se nenhum bit setado
        IT      NE
        ...
```
`TST` é o `AND` que só atualiza flags e não guarda resultado (Tabela p.2).

#### Como escolher e conferir

1. Há só igualdades e o corpo cabe em 1-2 instruções? **B**. É uma faixa? **C**. Testa bits? **D**. Caso contrário **A**.
2. Para desvio de curto-circuito, é preciso saber a **inversa** de cada condição (tabela em [§9.9](#s9-9)): GT↔LE, LT↔GE, HI↔LS, HS↔LO, EQ↔NE.
3. **Sinal:** variável com sinal → GT/LT/GE/LE; sem sinal → HI/LO/HS/LS ([§9.6](#s9-6)).
4. **Teste de mesa:** rode mentalmente os valores das bordas (x = lo−1, lo, hi, hi+1) e o caso "1º termo falha".
5. Se o enunciado disser **"não utilize instruções de salto"**, A não vale: use B, C ou D (as questões 4a-4c são desenhadas para isso).

<a id="s9-11"></a>
### 9.11 🧩 Constantes de 32 bits e endereços de periféricos **[Tabela p.2, p.4 e p.6]**

**Problema:** instruções têm 16 ou 32 bits, então uma constante de 32 bits (como o endereço `0xE000E010` do SysTick) **não cabe dentro** de uma instrução comum. Há quatro maneiras de colocá-la em um registrador.

**1) Constante imediata "modified" [Tabela p.6, Flexible Operand 2].** Vale em `MOV`, `ADD`, `CMP`, `AND`... só se for **um byte deslocado** ou os padrões `0x00XY00XY`, `0xXY00XY00`, `0xXYXYXYXY`.

| Valor | Cabe? | Motivo |
|---|---|---|
| `0x07` (7) | sim | um byte |
| `0x20000000` | sim | byte `0x20` deslocado de 24 bits |
| `0xFF00` | sim | byte `0xFF` deslocado |
| `0x20000050` | **não** | dois bytes diferentes de zero longe um do outro (`0x20` e `0x50`) |
| `0xE000E010` | **não** | vários bytes não nulos |
| `199999` (`0x30D3F`) | **não** | 18 bits significativos que não formam um byte |

**2) `MOVW` / `MOVT` [Tabela p.2].** `MOVW Rd,#imm16` carrega 16 bits (e zera o resto). `MOVT Rd,#imm16` carrega os 16 bits **altos** sem mexer nos baixos. Dois comandos = 32 bits quaisquer, **sem acessar memória**:
```
MOVW  R0, #0xE010
MOVT  R0, #0xE000          ; R0 = 0xE000E010
```
A pseudo-instrução **`MOV32 R0,#0xE000E010`** gera exatamente esse par.

**3) `LDR Rd, =constante` (pseudo-instrução do armasm).** O montador escolhe: se cabe em `MOV`/`MVN`, usa isso; senão guarda a constante numa **literal pool** (4 bytes no código, perto) e gera `LDR Rd,[PC,#off]`. Uma instrução, mas faz um **acesso à memória**. É a forma mais usada nas respostas ([Gabarito Ex.9, 17](Gabarito_Exercicios.md#ex17)).

**4) Endereço de rótulo/variável:** `LDR Rd,=rotulo` ou `ADR Rd,rotulo`.

**Reduzindo instruções com base + offset.** Os registradores de um periférico ficam em endereços vizinhos. Carregue **uma vez** a base e use offsets imediatos:

| Instrução | Offset imediato permitido [Tabela p.4] |
|---|---|
| `LDR/STR Rt,[Rn,#imm]` | 0 a 4095 (ou −255 a −1 com `!`) |
| `LDRD/STRD Rt,Rt2,[Rn,#imm]` | múltiplo de 4, ±1020 |

Exemplo (SysTick): `LDR R0,=0xE000E010` e depois `STR R1,[R0,#4]` (RVR), `STR R1,[R0,#8]` (CVR), `STR R1,[R0]` (CSR). Uma base serve para os três registradores.

**Truque para variável em RAM:** se o endereço for `0x2000_0050`, a constante `0x20000000` cabe em `MOV` (sem literal pool) e o `0x50` vai no offset: `MOV R0,#0x20000000` / `LDRD R1,R2,[R0,#0x50]`.

---

<a id="s10"></a>
## 10. 🧩 AAPCS e sub-rotinas

**AAPCS** = *ARM Architecture Procedure Call Standard* (citado no slide 3h p.193 e exigido em exercícios/prova).

| Regra | Detalhe |
|---|---|
| **Argumentos** | R0, R1, R2, R3 (nesta ordem). Excedentes vão para a pilha. |
| **Retorno** | R0 (64 bits: R1:R0). |
| **Registradores "de rascunho"** (caller-saved) | **R0-R3 e R12**: a função pode destruir sem salvar. |
| **Registradores preservados** (callee-saved) | **R4-R11**: se a função usar, deve `PUSH` na entrada e `POP` na saída. |
| **SP, LR, PC** | SP alinhado em **8 bytes** nas fronteiras de chamada (por isso `PUSH` de nº par de registradores; `PRESERVE8`). |
| **Retorno** | `BX LR`, ou `POP {..., PC}` se LR foi empilhado. |
| **Quem chama outra função** | precisa salvar **LR** (`PUSH {..., LR}`), pois `BL` sobrescreve LR. |

Por que qualquer função C serve como ISR (slide 3h p.193): a entrada em exceção empilha **R0-R3, R12, LR, PC, xPSR** – exatamente os registradores que o AAPCS permite destruir. Então um handler que segue AAPCS não precisa de código especial.

Modelo de função (do lab, `histogram.s`): `PRESERVE8` / `THUMB` / `AREA |.text|, CODE, READONLY, ALIGN=2` / `EXPORT f` / `f PROC` … `BX LR` / `ENDP` / `END`, com comentário indicando o mapeamento de parâmetros para registradores.

**Planejamento de função (como a prova pede, "3a" e "3b"):** (a) descreva o algoritmo em passos ou fluxograma; (b) faça uma tabela "variável → registrador" respeitando o AAPCS (parâmetros em R0-R3; temporários em R0-R3/R12; só use R4-R11 se realmente faltar registrador, e então salve/restaure).

---

<a id="s11"></a>
## 11. Exceções e interrupções (slide 3h, p.169-198 e 232-233)

### 11.1 Conceito (p.170-173)

**Exceção** = evento que muda o fluxo de execução fora da sequência normal programada. Causas: **interrupção de hardware**, **falha (fault)** (acesso inválido à memória, divisão por zero, instrução inválida), **exceção gerada por software**. São normais em sistemas embarcados. Ocorrem de forma **assíncrona**, em pontos diferentes a cada execução, e precisam de uma rotina de tratamento: *exception handler*, *ISR* ou *interrupt handler*.

**Interrupção × polling:** com interrupção, o periférico avisa o processador quando precisa de serviço. Sem interrupção, o processador teria de consultar periodicamente (**polling**), o que é ineficiente (p.174).

### 11.2 Sequência básica (p.175)

1. Periférico ativa o pedido de interrupção.
2. Processador suspende a tarefa em execução.
3. Executa a ISR e, se necessário, **limpa o pedido por software**.
4. Retoma a tarefa suspensa.

### 11.3 Vetorada × não vetorada, latência, nível × borda (p.176-178)

- **Não vetorada:** uma única ISR consulta o controlador para descobrir a fonte (overhead, uma ISR só).
- **Vetorada:** o controlador informa ao processador o **endereço do handler**. No Cortex-M4 há uma tabela de endereços a partir de 0x0.
- **Latência:** tempo do sinal de IRQ até o início do handler. Inclui: detecção, processamento no controlador, **término da instrução corrente**, período em que IRQs estão mascaradas, handlers de prioridade maior em execução. **Tempo de resposta (pior caso)** = maior latência + pior tempo de execução da ISR.
- **Nível × borda:** o Cortex-M4 aceita ambos, sem configuração. O **estado pendente é limpo automaticamente** quando o handler inicia.

<a id="s11-4"></a>
### 11.4 Numeração (p.179)

- Exceções numeradas de 1 a 255. **1-15 = exceções de sistema; 16 em diante = IRQ0 a IRQ239.**
- **Cuidado com a diferença de 16** entre nº da exceção e nº da interrupção (`exceção = IRQn + 16`). O nº da exceção fica em **IPSR**.

Exceções do sistema (CMSIS, p.186; nº da exceção entre parênteses):

| Nome | IRQn | Exc. | Observação |
|---|---|---|---|
| Reset | −15 | 1 | Power up e warm reset |
| NMI | −14 | 2 | Não mascarável, não pode ser parada nem preemptada |
| HardFault | −13 | 3 | Todas as classes de falha |
| MemManage | −12 | 4 | Violação da MPU / execução em região XN |
| BusFault | −11 | 5 | Erro de barramento (prefetch/data abort) |
| UsageFault | −10 | 6 | Instrução inválida, estado inválido |
| SVCall | −5 | 11 | `SVC`: serviços do SO para tarefas |
| DebugMonitor | −4 | 12 | Breakpoints/watchpoints por software |
| PendSV | −2 | 14 | Pedido pendente de serviço; **troca de contexto** |
| SysTick | −1 | 15 | Timer do sistema |

Falhas (p.181): **HardFault** (ex.: erro de barramento na leitura de vetor), **Bus fault**, **Memory management fault**, **Usage fault**, **Debug monitor**.

<a id="s11-5"></a>
### 11.5 Tabela de vetores (p.180, 203-204)

- Endereço inicial **0x0** por padrão; pode ser deslocado com **VTOR** (p.222).
- **Primeira entrada = valor inicial do SP.** Próximas 15 = exceções do sistema (Reset … SysTick). Depois até 240 entradas IRQ0…IRQ239.
- Cada entrada tem 31 bits de endereço; o **bit 0 deve ser sempre 1** (estado Thumb).
- Exemplo: `endereço da entrada de IRQn = VTOR + 4 × (16 + n)`.
- Na Renesas S7G2, a **ICU** fica entre periféricos e NVIC.

### 11.6 Prioridade e estados

**Prioridade (p.185):** maior prioridade **preempta** menor. **Número maior = prioridade menor.** Prioridades fixas: **−3 (Reset), −2 (NMI), −1 (HardFault)**; programáveis: 0…255 (implementação define quantos bits).

**Estados de uma exceção (p.188, 205):** *Inactive* → (pedido) → *Pending* → (serviço inicia) → *Active* → (serviço termina) → *Inactive*. Se novo pedido chega enquanto ativa: *Active and Pending*.

**Tipos de handler (p.187):** ISRs (IRQ0-xx), fault handlers, system handlers (NMI, PendSV, SVCall, SysTick e falhas). Falhas são um subconjunto dos system handlers.

<a id="s11-7"></a>
### 11.7 Processo detalhado de atendimento (p.189-198) – **decore a sequência**

1. **Periférico** pede interrupção ao **controlador de interrupção** (NVIC tem até 240 entradas, sensíveis a nível ou borda).
2. O **controlador** verifica: (a) a entrada está **mascarada**? (b) já há outro pedido sendo enviado ao core? Se não está mascarada e tem **prioridade maior** que a do pedido em curso (ou não há pedido em curso), encaminha ao processador.
3. O **processador** verifica se a prioridade é suficiente: (a) **PRIMASK/FAULTMASK/BASEPRI** (b) se há exceção ativa, só uma de **prioridade maior** pode preemptá-la. Se ok, o atendimento começa **ao fim da instrução corrente**.
4. **Empilhamento (stacking): 8 registradores** vão para a pilha ativa: **xPSR, PC, LR, R12, R3, R2, R1, R0** (R0 no topo, no menor endereço; possível *aligner* para 8 bytes). A exceção passa a **Active**.
5. **LR recebe um valor EXC_RETURN** (região de endereços onde não pode haver código), conforme o estado:

   | EXC_RETURN | Volta para | Pilha |
   |---|---|---|
   | **0xFFFFFFF1** | Handler mode | MSP |
   | **0xFFFFFFF9** | Thread mode | MSP |
   | **0xFFFFFFFD** | Thread mode | PSP |
   | 0xFFFFFFE1 / E9 / ED | idem, com contexto de ponto flutuante | |

6. **Leitura do vetor:** o processador lê da tabela o endereço do handler e carrega no **PC**; o handler começa. O bit 0 do endereço deve ser 1 (Thumb-2).
7. **Serviço:** o handler deve, no mínimo, (1) **desativar o pedido** de interrupção (senão é atendida para sempre); (2) **salvar dados voláteis** (ex.: byte recebido na UART); (3) salvar/restaurar qualquer registrador **além dos empilhados** que ele usar (R4-R11).
8. **Retorno:** `BX LR` ou `POP {...,PC}` (se a entrada foi `PUSH {...,LR}`). Carregar um valor como **0xFFFFFFF1** no PC é reconhecido como EXC_RETURN → o processador **desempilha** os 8 registradores e retoma o código interrompido.

**Otimizações (p.232-233):** **Tail-chaining** = evita `POP` seguido de `PUSH` quando uma exceção é atendida logo após outra. **Late arrival** = uma interrupção de prioridade maior que chega durante o empilhamento de uma menor é atendida primeiro.

Hardware, software, controlador, core e memória (o que a Q2a da prova pede) estão distribuídos assim: HW = periférico/GPIO; controlador = NVIC (passos 2 e 4 de arbitragem); core = passo 3, empilhamento e busca do vetor; memória = pilha (escrita, passo 4) e tabela de vetores (leitura, passo 6); software = ISR (passo 7) e retorno (passo 8).

<a id="s11-7b"></a>
### 11.7.1 Glossário: o porquê de cada passo do atendimento

Os 8 passos de [§11.7](#s11-7) são fáceis de decorar e difíceis de explicar. Esta tabela diz **o que cada palavra significa** e **por que aquele passo existe**.

| Termo | Significado | Por que existe |
|---|---|---|
| **Pedido de interrupção (IRQ)** | Sinal elétrico do periférico dizendo "preciso de atenção". | Evita *polling*: o processador só para o que está fazendo quando há algo a fazer. |
| **Habilitar (enable) no periférico** | Bit do próprio GPIO/timer que deixa o periférico gerar o pedido. | Cada periférico decide se quer interromper. |
| **Habilitar no NVIC (ISER)** | Bit da linha no controlador. `NVIC_EnableIRQ()`. | O sistema escolhe quais fontes valem. |
| **Pendente (pending)** | O NVIC "lembra" que o pedido chegou, mesmo que o core ainda não possa atender. | Um pulso curto não pode ser perdido enquanto uma ISR mais prioritária executa. |
| **Mascarar (PRIMASK, FAULTMASK, BASEPRI)** | O core ignora temporariamente exceções (todas, ou abaixo de um nível). | Proteger trechos críticos. |
| **Prioridade** | Número da ISR (0 = maior). | Define quem pode interromper quem (**preempção**). |
| **Latência** | Tempo entre o IRQ e a 1ª instrução da ISR. | Mede a rapidez de resposta; depende da instrução corrente, de máscaras e de ISRs maiores. No Cortex-M4 sem espera costuma ser **12 ciclos** de hardware 🧩. |
| **Empilhamento (stacking)** | Hardware salva 8 registradores na pilha. | Permite voltar ao código interrompido como se nada tivesse acontecido, **sem código extra**. |
| **Por que justamente R0-R3, R12, LR, PC, xPSR** | São os registradores que a **AAPCS** permite a uma função destruir (R0-R3, R12) + os de controle de fluxo. | Por isso uma função C comum serve de ISR. |
| **EXC_RETURN** (`0xFFFFFFF1/F9/FD`) | Valor mágico colocado em **LR**. | Ao carregá-lo no PC o hardware sabe que é um **retorno de exceção** (e para qual modo/pilha). |
| **Tabela de vetores** | Vetor de endereços de handlers, a partir de `0x0` (ou VTOR). | O hardware encontra o handler sem software (**vetorada**). |
| **Bit 0 = 1 no vetor** | Indica Thumb. | O Cortex-M só executa Thumb; sem isso há *UsageFault* ([§8.5](#s8)). |
| **Harvard** | Barramentos separados para código (Flash) e dados (SRAM). | Permite empilhar (SRAM) e ler o vetor (Flash) **ao mesmo tempo**. |
| **Handler mode × Thread mode** | Modo da ISR × modo do código normal. | Handler sempre usa a pilha **MSP**; threads de RTOS usam **PSP**. |
| **Pending → Active → Inactive** | Estados da exceção. | O NVIC sabe se há outra do mesmo tipo em andamento. |

**Exemplo numérico de empilhamento.** Suponha `SP = 0x2000_8000` quando o pedido é aceito. A pilha cresce para baixo, então 8 words (32 bytes = 0x20) são escritos de `0x2000_7FE0` a `0x2000_7FFC`:

| Endereço | Conteúdo |
|---|---|
| `0x2000_7FFC` | xPSR |
| `0x2000_7FF8` | PC (endereço da próxima instrução do código interrompido) |
| `0x2000_7FF4` | LR |
| `0x2000_7FF0` | R12 |
| `0x2000_7FEC` | R3 |
| `0x2000_7FE8` | R2 |
| `0x2000_7FE4` | R1 |
| `0x2000_7FE0` | **R0** (novo SP) |

Se o SP não estivesse alinhado em 8 bytes, o hardware insere uma word de preenchimento (*aligner*) e marca o fato no xPSR para desfazer depois. No retorno, o `EXC_RETURN` faz o hardware ler essas 8 words de volta e o SP volta a `0x2000_8000`.

<a id="s11-8"></a>
### 11.8 Escrevendo uma ISR (C e assembly)

**Checklist (nesta ordem):**

1. **Cabeçalho:** `void NOME(void)`. Sem parâmetros (ninguém os passa) e sem retorno (o hardware não tem a quem devolver). Nome **igual ao símbolo da tabela de vetores** no arquivo de startup (ex.: `SysTick_Handler`, `GPIOA_Handler`, `IRQ_nn_Handler`). Se o nome não coincidir, o vetor aponta para um handler padrão (laço infinito).
2. **Não precisa de nenhum atributo especial no Cortex-M:** como o hardware empilha R0-R3, R12, LR, PC e xPSR e a função C respeita a AAPCS (preserva R4-R11), uma função C comum **já é** uma ISR válida. O retorno (`BX LR`, com LR = EXC_RETURN) é gerado pelo compilador.
3. **Limpar o pedido no periférico** (flag do GPIO/timer) **logo no início**. Se não, o pedido continua ativo, e a ISR é chamada de novo assim que retornar, para sempre. *Exceções:* o SysTick não precisa disso (o flag COUNTFLAG é zerado ao ler o CSR, e a pendência é limpa automaticamente ao iniciar o handler).
4. **Salvar dados voláteis** (byte recebido da UART, valor lido do ADC) antes que sejam sobrescritos.
5. **Fazer o mínimo:** só sinalizar (evento/mensagem/flag) ou atualizar um contador. Sem laços longos, sem espera, sem `printf`. Tempo de resposta (pior caso) = maior latência + tempo de execução da ISR ([§11.3](#s11)).
6. **Variáveis compartilhadas com o código normal:** declare `volatile`.
7. **Preservar R4-R11** se usar assembly (PUSH/POP). A ISR C faz isso sozinha.

**Modelo em C (genérico):**
```c
volatile uint32_t botao_pressionado;       /* volatile: o main lê, a ISR escreve */

void BotaoISR(void)                        /* nome = símbolo do vetor */
{
    gpio_limpa_interrupcao(PINO_BOTAO);    /* 1º: baixa o pedido no periférico */
    botao_pressionado = 1;                 /* 2º: sinaliza (ou tx_event_flags_set(...)) */
}
```

**Modelo em assembly (SysTick com contador de 64 bits):**
```
SysTick_Handler PROC
        LDR   R0, =contador
        LDRD  R1, R2, [R0]
        ADDS  R1, R1, #1
        ADC   R2, R2, #0
        STRD  R1, R2, [R0]
        BX    LR                 ; LR = EXC_RETURN (o hardware sabe voltar)
        ENDP
```
(Só usa R0-R2, que estão entre os que o hardware já salvou; não há PUSH/POP.)

**Inicialização que antecede qualquer interrupção (software):**
```c
gpio_config_entrada(PINO_BOTAO);           /* pino como entrada */
gpio_config_borda(PINO_BOTAO, DESCIDA);    /* tipo de borda */
gpio_habilita_interrupcao(PINO_BOTAO);     /* habilita no periférico */
NVIC_SetPriority(IRQ_BOTAO, 4);            /* prioridade (0 = maior) */
NVIC_EnableIRQ(IRQ_BOTAO);                 /* habilita a linha no NVIC (ISER) */
__enable_irq();                            /* PRIMASK = 0 (normalmente já é) */
```
E o endereço do handler (com LSb = 1) já está na **tabela de vetores** do startup. Faltou qualquer item da lista: a interrupção **não ocorre**.

---

<a id="s12"></a>
## 12. NVIC e CMSIS (slide 3h, p.199-231 e 234-240)

### 12.1 NVIC (p.200-202)

*Nested Vectored Interrupt Controller*, parte integrante da arquitetura (todo Cortex-M4 tem o mesmo). Funções: detectar pedidos nas entradas e combiná-los em **um** pedido ao core, **mascarar** qualquer entrada, associar **prioridades**. Suporta:

- **Nested exceptions** (aninhamento por prioridade),
- **Vectored exceptions** (tabela de vetores, sem atraso de identificação),
- **Interrupt masking** por entrada.

### 12.2 Registradores do NVIC (p.208-211)

Nº de linhas depende da implementação (informado por **ICTR.INTLINESNUM**). Na S7G2: INTLINESNUM = 2 → 3 registradores de cada tipo (índices 0-2), 96 linhas.

| Registrador | Escrever 1 | Ler |
|---|---|---|
| **ISER** | habilita (*set-enable*) | 1 = habilitada |
| **ICER** | desabilita (*clear-enable*) | 1 = habilitada |
| **ISPR** | coloca como **pendente** | 1 = pendente |
| **ICPR** | limpa pendência | 1 = pendente |
| **IABR** | (somente leitura) | 1 = ativa |
| **IPR[k]** | prioridade (8 bits por IRQ; 4 IRQs por registrador) | |

Escrever 0 em ISER/ICER/ISPR/ICPR **não tem efeito**. ISER[0] cobre IRQ0-31, ISER[1] IRQ32-63, ISER[2] IRQ64-95.

### 12.3 Prioridades (p.212-214, 235-239)

- ARM define 8 bits (256 níveis). Fabricante implementa menos: S7G2 tem **4 bits → 16 níveis, alinhados à esquerda** (valores 0x00, 0x10, …, 0xF0). **0 = maior prioridade, 15 = menor.**
- Os bits se dividem em **grupo** (define **preempção**) e **subgrupo** (desempate quando duas IRQ estão pendentes ao mesmo tempo). Configurado por **AIRCR.PRIGROUP** (0…7). Na S7G2: PRIGROUP 0-3 → 4 bits para grupo, 0 para subgrupo; PRIGROUP 4 → 3.1; 5 → 2.2.
- **Preempção é baseada só na prioridade de grupo.**
- Exceções de sistema têm prioridade definida no **SCB**.
- **BASEPRI** (p.240): valor ≠ 0 bloqueia exceções de prioridade igual ou menor (valor maior).

### 12.4 Funções CMSIS-CORE (p.215-221)

| Função | O que faz |
|---|---|
| `__enable_irq()` | zera PRIMASK (permite atendimento) |
| `__disable_irq()` | seta PRIMASK (bloqueia exceções configuráveis) |
| `NVIC_EnableIRQ(IRQn)` / `NVIC_DisableIRQ(IRQn)` | habilita/mascara uma linha |
| `NVIC_GetPendingIRQ / SetPendingIRQ / ClearPendingIRQ` | lê/seta/limpa pendência |
| `NVIC_SetPriority(IRQn, prio)` / `NVIC_GetPriority` | prioridade (faixa 0…2ᴺ−1; S7G2: 0…15) |
| `NVIC_GetActive(IRQn)` | lê estado ativo |

Exemplo do professor: `NVIC_SetPriority(SysTick_IRQn, 4);`. **IRQn negativo** identifica exceções de sistema (`SysTick_IRQn = −1`).

Fontes de interrupção possíveis (p.223): até **240 linhas IRQ**, **NMI** (ex.: brown-out) e **SysTick**.

---

<a id="s13"></a>
## 13. Timers e SysTick (slide 5, p.354-372)

### 13.1 Periféricos (p.355-356)

Sistema com processador = **microprocessador + memória + periféricos**. Periféricos dão a capacidade de sentir, atuar e comunicar. Classes: E/S digital, E/S analógica, **temporização**, armazenamento, comunicação (RS-232, SPI, I2C, CAN, USB, Ethernet), IHM, imagem, gerenciamento do sistema (clock, **watchdog**, energia).

### 13.2 Timers/Counters (p.357-358, 365)

Circuito contador. **Timer** conta pulsos de clock; **Counter** conta pulsos de um sinal de entrada. Usos: medir tempo, contar eventos, RTC, gerar **PWM**, gerar interrupções periódicas (**clock do SO**), disparar conversão A/D, **watchdog** (reinicia a MCU se o software não o reiniciar).

Variam em: borda usada, direção (up/down/ambas), o que contam, periódico × *one-shot*, ação ao fim (mudar GPIO, IRQ, parar, recarregar), número de bits (32 em ARM tipicamente) e **prescaler** (reduz a frequência de entrada para estender o período máximo).

**Timer simples (p.365):** contador decrementa a cada borda positiva do clock; o processador faz *load* + *start*; ao chegar em 0 a saída **Z** dispara: muda GPIO, gera IRQ, para ou recarrega.

### 13.3 SysTick (p.369-372)

- Timer presente em **todo Cortex-M**; contador **decrescente de 24 bits com recarga automática**. Interface padronizada pela ARM (independente do fabricante). Uso principal: **tick do SO**.
- **Período = RVR + 1 ciclos de clock** (recarrega no clock seguinte ao 0). Exemplo do slide: RVR = 2 → CVR: 2, 1, 0, 2, 1, 0 → período de **3 ciclos**.

| Registrador | Função |
|---|---|
| **SYST_CSR** | controle: **ENABLE** (bit 0), **TICKINT** (bit 1: gera IRQ ao chegar em 0), **CLKSOURCE** (bit 2: 1 = clock do processador; 0 = referência), **COUNTFLAG** (bit 16: foi a 0 desde a última leitura; **zerado ao ler o CSR**) |
| **SYST_RVR** | valor de recarga (24 bits). **Escrever 0 desabilita o SysTick.** |
| **SYST_CVR** | valor atual. **Escrever qualquer valor zera.** |
| **SYST_CALIB** | valores de fábrica; **TENMS** = valor de recarga para 10 ms na clock de referência (se disponível) |

🧩 Endereços (padrão ARMv7-M, não constam no texto dos slides): **CSR = 0xE000E010, RVR = 0xE000E014, CVR = 0xE000E018, CALIB = 0xE000E01C.**

**Receita para um período T com clock f:** `RVR = T × f − 1` (T em segundos). Ex.: 2 ms a 100 MHz → 200 000 − 1 = **199 999** (0x30D3F, cabe em 24 bits). Depois: zerar CVR e `CSR = 0b111` (CLKSOURCE=1, TICKINT=1, ENABLE=1). A interrupção é a exceção 15 (`SysTick_Handler`).

<a id="s13-4"></a>
### 13.4 SysTick passo a passo (configurar, usar, conferir)

**Os três registradores e os bits (leia com a [Tabela de registradores §13.3](#s13)):**

| Registrador | Endereço 🧩 | Bits importantes |
|---|---|---|
| **SYST_CSR** | `0xE000E010` | bit 0 **ENABLE**; bit 1 **TICKINT**; bit 2 **CLKSOURCE**; bit 16 **COUNTFLAG** |
| **SYST_RVR** | `0xE000E014` | bits 23:0 = valor de recarga |
| **SYST_CVR** | `0xE000E018` | bits 23:0 = valor atual (escrever qualquer coisa zera) |

Valores de `CSR`: `0b001` = só contando, sem interrupção, clock de referência; `0b101` = contando com o clock do processador, sem interrupção (consulta o COUNTFLAG); **`0b111` = clock do processador + interrupção + ligado** (o usual).

**Como funciona o contador:** carrega `RVR`, decrementa a cada clock até **0**, e **no clock seguinte recarrega**. Por isso são `RVR + 1` ciclos por período. Quando chega em 0: seta COUNTFLAG e, se TICKINT = 1, gera a exceção 15.

**Receita (para qualquer período):**

1. **Ciclos por período** `N = T × f_clock`.
2. **RVR = N − 1**. Verifique `RVR ≤ 0xFFFFFF` (16 777 215). Se passar, não cabe: use um período menor e conte as ocorrências em software, ou use outro timer.
3. Escreva `RVR`.
4. Escreva qualquer valor em `CVR` (zera o contador).
5. Escreva `CSR = 0b111` (ou o valor desejado).
6. A ISR `SysTick_Handler` roda a cada período.

**Exemplos de conta:**

| Período | Clock | N = T × f | RVR = N − 1 | Cabe em 24 bits? |
|---|---|---|---|---|
| **2 ms** | 100 MHz | 200 000 | **199 999 = 0x30D3F** | sim |
| 1 ms | 100 MHz | 100 000 | 99 999 = 0x1869F | sim |
| 10 ms | 16 MHz | 160 000 | 159 999 = 0x270FF | sim |
| 1 s | 100 MHz | 100 000 000 | 99 999 999 | **não** (> 16,7 M): use 100 ms e conte 10 interrupções |

Período máximo com 24 bits a 100 MHz: 16 777 216 / 100 MHz ≈ **167,8 ms**.

**Equivalente em C com CMSIS:** `SysTick_Config(200000)` faz exatamente: `RVR = ticks − 1`, prioridade mais baixa do SysTick, `CVR = 0`, `CSR = 0b111`. Retorna 1 (erro) se `ticks − 1` não couber em 24 bits.

**Escrita em C bit a bit (compare com o assembly):**
```c
SysTick->LOAD = 200000 - 1;     /* RVR */
SysTick->VAL  = 0;              /* CVR: zera o contador */
SysTick->CTRL = SysTick_CTRL_CLKSOURCE_Msk | SysTick_CTRL_TICKINT_Msk | SysTick_CTRL_ENABLE_Msk;   /* = 7 */
```

**Erros comuns:**

- Usar `RVR = N` em vez de `N − 1` (período 1 ciclo mais longo, resposta errada na prova).
- Esquecer **CLKSOURCE = 1** (usa a referência externa, que pode ter outra frequência) ou **TICKINT = 1** (sem interrupção).
- Escrever `RVR = 0` (desabilita o SysTick).
- Esquecer de implementar a ISR com o nome correto (`SysTick_Handler`).
- Ler `CSR` sem querer: isso **zera** o COUNTFLAG.

<a id="s13-5"></a>
### 13.5 🧩 SysTick em C: configuração completa, handler e usos típicos

Os slides descrevem os registradores ([§13.3](#s13)); o CMSIS os expõe na estrutura `SysTick` com os campos `CTRL`, `LOAD`, `VAL`, `CALIB` (= SYST_CSR, RVR, CVR, CALIB). As máscaras `SysTick_CTRL_ENABLE_Msk`, `SysTick_CTRL_TICKINT_Msk` e `SysTick_CTRL_CLKSOURCE_Msk` valem os bits 0, 1 e 2.

#### a) Configuração no nível dos registradores (equivale à Q3 da prova de 2022)

```c
#include <stdint.h>
#include "TM4C1294NCPDT.h"      /* ou o cabeçalho CMSIS do seu chip: define SysTick, SysTick_IRQn... */

#define F_CPU   100000000UL     /* clock do processador em Hz (a prova usa 100 MHz) */
#define T_MS    2UL             /* período desejado em ms */

volatile uint32_t ticks = 0;    /* volatile: alterada na ISR, lida no main */

void systick_config(void)
{
    uint32_t reload = (F_CPU / 1000UL) * T_MS - 1UL;   /* 100e6/1000*2 - 1 = 199 999 */

    SysTick->CTRL = 0;                 /* 1. desliga antes de configurar            */
    SysTick->LOAD = reload;            /* 2. RVR = período em ciclos - 1 (24 bits)  */
    SysTick->VAL  = 0;                 /* 3. qualquer escrita zera o contador atual */
    NVIC_SetPriority(SysTick_IRQn, 4); /* 4. prioridade (0 = maior; S7G2: 0..15)    */
    SysTick->CTRL = SysTick_CTRL_CLKSOURCE_Msk   /* clock do processador (bit 2)  */
                  | SysTick_CTRL_TICKINT_Msk     /* gera interrupção ao chegar a 0 (bit 1) */
                  | SysTick_CTRL_ENABLE_Msk;     /* liga o contador (bit 0)       */
}
```
Pontos de conferência:
- `LOAD = ciclos - 1`, porque o período é `RVR + 1` ([§13.3](#s13)).
- `LOAD` tem **24 bits**: `reload <= 0xFFFFFF` (16 777 215). A 100 MHz o período máximo é ~167 ms. Acima disso é preciso contar ticks em software.
- `CTRL = 0x7` é o mesmo que o `MOVS R1,#7` do gabarito em assembly.
- Não precisa `NVIC_EnableIRQ`: o SysTick é uma **exceção de sistema** (nº 15), sempre habilitada pelo `TICKINT` ([§11.4](#s11-4)).

#### b) Configuração com a função do CMSIS

```c
#include "TM4C1294NCPDT.h"

extern uint32_t SystemCoreClock;       /* mantida por SystemInit/SystemCoreClockUpdate */

int main(void)
{
    SystemCoreClockUpdate();                       /* garante o valor atual do clock */

    if (SysTick_Config(SystemCoreClock / 1000UL)) /* 1 ms; retorna 1 se o valor não cabe em 24 bits */
        while (1) { }                              /* erro de configuração */

    NVIC_SetPriority(SysTick_IRQn, 4);             /* SysTick_Config deixa a prioridade mais baixa; ajuste se precisar */
    /* ... */
    while (1) { }
}
```
`SysTick_Config(n)` faz tudo da versão (a): `LOAD = n - 1`, prioridade mais baixa, `VAL = 0`, `CTRL = CLKSOURCE | TICKINT | ENABLE`. O argumento é o **número de ciclos do período**, não o tempo.

#### c) Handler (ISR) do SysTick

O nome vem do **vetor de exceção** da tabela do startup (exceção 15): `SysTick_Handler`. Se o nome diferir, o handler **não é chamado** (o startup usa o `[WEAK]` padrão, que é um laço infinito).

```c
volatile uint32_t ticks = 0;           /* contador de ticks (a cada 1 ms, por exemplo) */
volatile uint64_t total = 0;           /* contador de 64 bits, como na prova de 2022   */

void SysTick_Handler(void)             /* void(void): sem parâmetros nem retorno (AAPCS, §10) */
{
    ticks++;                           /* não é preciso limpar o pedido: a IRQ do SysTick é limpa ao iniciar o handler */
    total++;
}
```
- Não há flag de pendência a limpar no periférico (diferente de um GPIO, [§11.7](#s11-7), passo 7). O `COUNTFLAG` é limpo ao **ler** o CTRL, mas a ISR não depende dele.
- ISR **curta**: só atualiza contadores/flags. Sem laços de espera.
- Variáveis compartilhadas com o `main` devem ser `volatile`. Em `uint64_t`, a leitura no `main` **não é atômica** (são dois `LDR`): leia com a interrupção desabilitada (`__disable_irq(); v = total; __enable_irq();`) ou compare duas leituras.

#### d) Usos típicos

```c
/* delay em ms bloqueante (base de 1 ms) */
void delay_ms(uint32_t ms)
{
    uint32_t inicio = ticks;
    while ((ticks - inicio) < ms) { }      /* a subtração sem sinal resolve o estouro do contador */
}

/* piscar um LED a cada 500 ms sem bloquear: o handler só marca, o main age */
volatile uint8_t flag500 = 0;
void SysTick_Handler(void)
{
    static uint16_t n = 0;                 /* static: guarda o valor entre chamadas */
    ticks++;
    if (++n >= 500) { n = 0; flag500 = 1; }
}

int main(void)
{
    systick_config();                       /* 1 ms por tick */
    while (1) {
        if (flag500) { flag500 = 0; led_toggle(); }   /* trabalho "pesado" fora da ISR */
    }
}
```
Cálculo mental rápido: `RVR = f_CPU × T − 1`. Ex.: 120 MHz e 1 ms → 119 999 (0x1D4BF). Se o RVR passar de 24 bits, use um período menor e conte N ticks.

---

<a id="s14"></a>
## 14. Modelagem: máquinas de estados e Statecharts (slide 9 fsm, p.543-610)

### 14.1 Sistemas reativos (p.544)

**Reativos** reagem a eventos externos (contrário de *transformacionais*), podem gerar eventos internos e reagir a eles. "Reagir" = muda de estado, muda variáveis internas, executa ações, produz saída.

### 14.2 FSM e Statecharts (p.546-549)

- **Máquina de estados finita:** ferramenta de modelagem do comportamento **dinâmico** de sistemas reativos, representada por diagrama de estados. Número de estados **finito**; transições em geral por eventos externos. Pode modelar em vários níveis: classes, casos de uso, componentes, subsistemas, sistemas.
- **Statecharts** (David Harel, 1984) contribuem para a FSM com **hierarquia**, **histórico** e **concorrência**.
- **UML**: Booch, Rumbaugh, Jacobson; padrão OMG em 1998; versão 2.5.1 (2017); linguagem visual não proprietária.
- Dois tipos de FSM em UML 2.x: **comportamental** e de **protocolo**.

### 14.3 Conceitos (p.567-569)

- **Estado:** condição estável do sistema; nome = **substantivo ou particípio presente** (ex.: `Idle`, `Locked`).
- **Evento:** ocorrência relevante e "instantânea"; externa ou interna.
- **Transição:** muda de um estado para outro (ou o mesmo); causas: evento, condição, fim de atividade…

**Notação da transição (p.568-569):**

```
evento [guarda] / ações
```
- **Todos os três campos são opcionais.**
- **evento**: identificador. **guarda**: expressão lógica (true/false). **ações**: lista separada por ponto e vírgula, **instantâneas**.
- **Semântica (RTC – run-to-completion):** estando em S1, ocorre o evento; a guarda é avaliada; se verdadeira, as ações são executadas em sequência; então o estado passa a S2.
- **Gatilhos (triggers):** evento externo, evento interno, **evento de tempo**, guarda se tornando verdadeira, fim de atividade em um estado.

### 14.4 Ações e comportamento no estado (p.574)

| Palavra | Significado |
|---|---|
| **entry** | ações ao **entrar** no estado |
| **exit** | ações ao **sair** |
| **evento** | ações ao ocorrer o evento, **sem** mudar de estado (sem exit/reentry) |
| **do** | atividade contínua enquanto no estado (com duração, limitada ou não) |

### 14.5 Pseudo-estados (p.575-582)

Sem duração; origem/destino de transições: **inicial**, **final**, **junction** (junção estática; usa `else`), **choice** (decisão dinâmica), **terminate** (equivale a `exit()`, ex.: watchdog), **fork/join** (concorrência), **histórico**.

- `else` é palavra-chave em uma saída de decisão.

### 14.6 Eventos de tempo (p.584-585)

- **`after(T)`**: tempo **relativo** desde a última entrada no estado.
- **`at(t)`**: tempo **absoluto**.
- Palavras-chave adicionais: `in` (estado).

Muito útil para: timeout de 40 min, piscar a cada 1 s, etc.

### 14.7 Hierarquia (p.586-596)

- **Superestado OR:** só **um** subestado ativo por vez; costuma ter estado inicial e, opcionalmente, final. Entrada: pela **borda** (vai ao inicial) ou direto a um estado interno. Saída: pela borda (vale para qualquer subestado) ou de um estado interno.
- Transições: **interna × local × externa** (p.594-595). Interna não sai nem reentra.
- **Histórico raso (shallow, H)**: retorna ao último subestado do nível; **profundo (deep, H\*)**: reconstitui todo o caminho de subestados aninhados (p.598-599).

### 14.8 Concorrência (p.600-605)

**Superestado AND:** dividido por linhas tracejadas em **regiões**; cada região é uma FSM concorrente → **vários estados ativos ao mesmo tempo (um por região)**. **Fork** e **join** sincronizam.

### 14.9 Como codificar uma FSM (p.606-610)

Três estratégias:

1. **Seleção por estado** (`switch(state)`, depois testa o evento).
2. **Seleção por evento** (`switch(event)`, depois testa o estado).
3. **Matriz Estado × Evento**: cada célula é um ponteiro de função (uma função por transição): `state = mee[state][event](state);` com `States (*mee[N][M])(States) = {{f1,f2,f3},{f1,f5,f4},…};`

Considerações (p.607): `state` é uma variável que guarda o estado corrente de um superestado OR; **eventos externos** são detectados por HW/ISR e **informados ao código por um mecanismo do RTOS** (mensagem ou evento). Exemplo do professor (p.608): `enum States {...}; void Th1(Card32 p) { PutMsgStr pm; States state = B11; while (1) { Receive(&pm, sizeof(pm)); switch (state) { case B11: ... } } }`.

---

<a id="s15"></a>
## 15. FORA DA P1: Concorrência, RTOS e ThreadX

> **Não cai na P1** (confirmado por você). Pode pular esta seção; fica só como base para a P2.

Nota antiga: a pasta `Slides` **não contém** os slides de concorrência/RTOS/ThreadX, mas a **Prova 2022 Q1** cobra isso. O calendário da disciplina (slide 1a) lista Concorrência, Design de Concorrência, RTOS, Escalonamento e Conflito de Recursos. Confirme com o professor/colegas se entram na sua P1. O que segue é o mínimo necessário para o gabarito.

Contexto nos slides: o **RTOS** é a camada que gerencia a concorrência da aplicação ([§3](#s3), camadas 5-6 e 9); eventos externos detectados por ISR são informados às tarefas por **mensagem ou evento** ([§14.9](#s14)).

### 15.1 Conceitos

- **Tarefa/thread:** fluxo de execução com sua própria pilha e prioridade; o escalonador escolhe a de maior prioridade pronta.
- **ISR:** roda no contexto de interrupção; deve ser **curta**, só sinaliza (evento/mensagem) e deixa o trabalho para a tarefa.
- **Fila de mensagens (queue):** comunicação com dados (FIFO). **Event flags:** sinalização (bits) sem dados. **Timer:** chama uma função de expiração após N ticks (uma vez ou periodicamente).

### 15.2 API ThreadX usada nos gabaritos (prototipos)

```c
UINT tx_thread_create(TX_THREAD *t, CHAR *nome, VOID (*entrada)(ULONG), ULONG param,
                      VOID *pilha, ULONG tam_pilha, UINT prio, UINT preempt_thr,
                      ULONG time_slice, UINT auto_start);   /* TX_AUTO_START */
UINT tx_queue_create(TX_QUEUE *q, CHAR *nome, UINT tam_msg_em_ULONGs,
                     VOID *area, ULONG tam_area_bytes);
UINT tx_queue_send   (TX_QUEUE *q, VOID *origem, ULONG espera);   /* TX_NO_WAIT, TX_WAIT_FOREVER */
UINT tx_queue_receive(TX_QUEUE *q, VOID *destino, ULONG espera);
UINT tx_event_flags_create(TX_EVENT_FLAGS_GROUP *g, CHAR *nome);
UINT tx_event_flags_set(TX_EVENT_FLAGS_GROUP *g, ULONG flags, UINT opcao);   /* TX_OR */
UINT tx_event_flags_get(TX_EVENT_FLAGS_GROUP *g, ULONG pedidos, UINT opcao,
                        ULONG *atuais, ULONG espera);  /* TX_OR_CLEAR, TX_AND_CLEAR */
UINT tx_timer_create(TX_TIMER *t, CHAR *nome, VOID (*expira)(ULONG), ULONG param,
                     ULONG ticks_iniciais, ULONG ticks_repeticao, UINT ativa);
                     /* TX_AUTO_ACTIVATE / TX_NO_ACTIVATE; repeticao = 0 -> one-shot */
UINT tx_timer_activate(TX_TIMER *t);  UINT tx_timer_deactivate(TX_TIMER *t);
VOID tx_application_define(VOID *primeira_memoria_livre);   /* cria os objetos */
```
Retornos relevantes: `TX_SUCCESS`, `TX_NO_EVENTS` (timeout ao esperar evento). `TX_TIMER_TICKS_PER_SECOND` converte segundos em ticks. O tamanho da mensagem da fila é em **palavras de 32 bits** (1 a 16).

### 15.3 Padrão ISR → evento → tarefa → filas → tarefas de saída

1. A ISR só faz `tx_event_flags_set`.
2. Uma tarefa "gerente" espera o evento, mantém a **FSM** ([§14](#s14)) e envia **comandos** por filas.
3. Tarefas "de saída" (LEDs, aquecedor) consomem comandos e mexem no hardware. Assim o acesso ao hardware fica concentrado em uma tarefa (evita conflito de recursos).

---

<a id="s16"></a>
## 16. Convenções do professor (resumo para a prova)

O que se repete nos slides, listas e prova, e como aplicar:

1. **Use a AAPCS "rigorosamente"** ([§10](#s10)): argumentos R0-R3, retorno R0, preserve R4-R11, `BX LR`.
2. **Sempre planeje antes de codificar** (prova 2022 Q3: 3a planejamento, 3b alocação de registradores, 3c código). Faça a tabela "variável → registrador".
3. **"Menor número possível de instruções"**: aproveite shift no Operand2 ([§9.2](#s9-2)), `MLS`, `BFI/BFC/UBFX`, `IT`, endereçamento pós/pré-indexado.
4. **"Não utilize instruções de salto"** → use `IT` com sufixos de condição ([§9.6](#s9-6)).
5. **Comentários** em cada linha explicando o efeito (o lab usa `; r4 = índice do pixel`).
6. **Little-endian**, bit 0 = LSb; 64 bits = par de registradores, word baixa no endereço menor.
7. **Diagramas de estado** com a notação `evento [guarda] / ações`, estados nomeados por substantivos/particípios, estado inicial, `entry/exit/do` quando necessário ([§14](#s14)).
8. **UML** na disciplina: objetos/classes com estereótipos, filas de mensagens e eventos entre tarefas ([§15](#s15)); na prova, **defina os comandos** trafegados nas filas.
9. **Interrupção "detalhada"**: descreva na ordem HW → controlador → core → memória → software, em passos numerados ([§11.7](#s11-7)).
10. **Prova sem consulta e sem calculadora** (2022); a **Tabela** é o material permitido na prova atual. Treine somas/shifts em hexadecimal à mão.
11. Palavras que ele pune: confundir **sem sinal × com sinal** (HS/LO × GE/LT), esquecer de salvar R4-R11, esquecer de limpar o pedido de interrupção, esquecer o bit Thumb (LSb = 1) no vetor.

<a id="s17"></a>
## 17. 🧩 O que acontece antes da `main()` (reset e inicialização)

Os slides têm só o título "RESET" (slide 3c p.154) e a tabela de vetores ([§11.5](#s11-5)). O restante abaixo é o fluxo padrão do Cortex-M com o **startup do Keil**, o mesmo arquivo `startup_TM4C129.s` do seu repositório (Lab1-4a).

### 17.1 Sequência completa

| # | Quem | O que acontece |
|---|---|---|
| 1 | **Hardware** | Energia estabiliza (*power-on reset*) ou ocorre um reset (botão, watchdog, software). O core entra em **reset**: registradores indefinidos, **Thread mode privilegiado**, pilha **MSP**, bit **T = 1**. As interrupções ficam habilitáveis, mas nenhuma periférica está configurada. |
| 2 | **Core (hardware)** | Lê a **tabela de vetores** em `VTOR` = **0x00000000** (padrão após o reset, [§11.5](#s11-5)): **palavra 0 → MSP** (valor inicial da pilha, `__initial_sp`); **palavra 1 → PC** (endereço do `Reset_Handler`; o bit 0 = 1 é descartado e mantém o estado Thumb). |
| 3 | **Core** | Começa a buscar instruções em `Reset_Handler`. **Não existe `main` ainda**, nem variáveis inicializadas, nem pilha C configurada além do MSP. |
| 4 | **`Reset_Handler`** (assembly do startup) | `LDR R0,=SystemInit` / `BLX R0` chama **`SystemInit`**; depois `LDR R0,=__main` / `BX R0` salta para **`__main`**. |
| 5 | **`SystemInit`** (C, do CMSIS/fabricante) | Configura o **clock do sistema** (oscilador, PLL, divisores; ex.: 120 MHz no TM4C129) e, se existir, a unidade de ponto flutuante e flash/cache. É por isso que o clock real só vale depois desse ponto. |
| 6 | **`__main`** (biblioteca C da ARM, não é a sua `main`) | Prepara o ambiente C: **copia** os dados inicializados (*RW*, `.data`) da **Flash para a RAM**; **zera** a área *ZI* (`.bss`, variáveis globais sem valor inicial); configura pilha e *heap* (`__user_setup_stackheap`) e inicializa a biblioteca (`__rt_lib_init`: stdio, `malloc`...). |
| 7 | **`__rt_entry`** | Finalmente chama **`main()`**. |
| 8 | **Seu código** | `main()` configura periféricos, NVIC, SysTick e entra no laço principal. |

Resumo em uma linha: **reset → lê SP e PC da tabela de vetores → `Reset_Handler` → `SystemInit` (clock) → `__main` (copia `.data`, zera `.bss`, heap e pilha) → `main()`.**

### 17.2 Por que cada etapa existe

- **SP primeiro:** o `Reset_Handler` e as funções C que ele chama precisam de pilha antes de qualquer outra coisa. Por isso a palavra 0 da tabela é o SP e não um vetor ([§11.5](#s11-5)).
- **Copiar `.data`:** variáveis globais com valor inicial (`int x = 5;`) ficam gravadas na **Flash** (não volátil) e precisam ser copiadas para a **RAM** para poderem mudar. Isso é feito antes da `main` e é coisa do linker/`__main`.
- **Zerar `.bss`:** o C garante que globais sem valor inicial valem 0; a RAM, ao ligar, tem lixo.
- **`SystemInit` antes:** o clock afeta timers, UART e SysTick (o cálculo do `RVR` da prova depende da frequência, [§13.3](#s13)).
- **Tudo isso é anterior ao `main`:** por isso uma global usada sem `.data`/`.bss` inicializados daria valores errados, e por isso uma ISR chamada antes do vetor estar no lugar leva a HardFault.

### 17.3 Itens do arquivo `startup_TM4C129.s` (reconhecer na prova ou no lab)

| Trecho | Significado |
|---|---|
| `Stack_Size EQU 0x200` / `AREA STACK, NOINIT, READWRITE` | reserva 512 bytes de RAM para a pilha; `__initial_sp` é o endereço do topo (pilha cresce para baixo) |
| `Heap_Size EQU 0` | tamanho do *heap* (0 = sem `malloc`) |
| `AREA RESET, DATA, READONLY` com `__Vectors DCD __initial_sp, Reset_Handler, NMI_Handler, ...` | a **tabela de vetores** na Flash a partir do endereço 0 |
| `Reset_Handler PROC` ... `BLX SystemInit` ... `BX __main` | o código executado logo após o reset |
| `[WEAK]` | símbolo fraco: pode ser **substituído** por uma função sua com o mesmo nome (ex.: `SysTick_Handler`) |
| handlers padrão (`NMI_Handler`, `HardFault_Handler`...) | cada um é um laço infinito `B .` até você definir o seu |

### 17.4 Estado do processador quando a `main` começa

- Thread mode, privilegiado, usando **MSP** (a menos que você mude o CONTROL).
- **Interrupções não habilitadas na NVIC** (nenhuma linha está ligada); PRIMASK = 0 (não mascara), mas nada pede interrupção ainda.
- Clock já configurado por `SystemInit`; periféricos ainda desligados.
- Globais inicializadas; `.bss` zerada.

