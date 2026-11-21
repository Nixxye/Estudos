# Resumo dos Labs: o que o professor pediu e o que quis ensinar

Resumo dos **Labs 1 a 6 e do Projeto Final** da disciplina ELEW32 (Prof. Douglas Renaux). Para cada um: o que foi **pedido**, o que ele **quis ensinar**, as **decisões e resultados** que valem lembrar e **onde isso cai na prova** (com links para o [Resumo P1](P1/Resumo_P1.md) e o [Compilado P2](P2/Compilado_P2.md)).

**Como este resumo foi feito.** Li os relatórios (`README.md`) de cada pasta do repositório, o enunciado do Lab 3 (PDF do professor) e os documentos do Projeto Final. **O que o professor "quis ensinar" é inferido dos objetivos de aprendizado, dos requisitos do enunciado e das perguntas que ele pediu para responder**: confirme com ele o que realmente cobra. Só o Lab 3 tem o enunciado original na pasta; para os demais, os relatórios reproduzem os requisitos "conforme o enunciado".

## Mapa rápido

| Lab | Tema | Placa e periféricos | Conteúdo da disciplina que treina | Prova |
|---|---|---|---|---|
| **1** | Ambiente de debug (Keil) e símbolos pré-definidos | – | Ferramentas, `volatile`, arquitetura ARMv7-M | P1 (leve) |
| **2** | Jogo de tempo de reação | GPIO, SysTick, UART | **Interrupções, SysTick, boot, VTOR**, FSM | **P1** |
| **3** | Histograma em **assembly** (AAPCS) | UART, DWT | **Assembly, AAPCS, LDR/STR**, desempenho | **P1** |
| **4a** | Joystick, LED RGB, UART | ADC, PWM, Timer, UART | Periféricos, **ISR curta**, timer disparando o ADC | P1 / projeto |
| **4b** | 1000 pulsos: C × TivaWare × assembly | GPIO, SysTick, UART | **Custo de abstração**, medida em ciclos | P1 |
| **5a** | Estudo do `demo_threadx.c` | – | **ThreadX**: objetos, memória, UML | **P2** |
| **5b** | Teste da temporização do ThreadX | SysTick, DWT | **Tick do RTOS**, boot do ThreadX | **P2** |
| **6a** | Escalonamento: 3 tarefas periódicas | LEDs | **Escalonamento, prioridades, inversão de prioridade** | **P2** |
| **Projeto** | Filtro digital parametrizado | ADC, PWM, LCD, joystick | **Tudo**, em tempo real, com ThreadX | Projeto (25%) |

Peso na nota (slide da primeira aula): Labs 1 a 6 = **5%**, Projeto Final = **25%** ([Resumo P1 §0.1](P1/Resumo_P1.md#s0-1)).

## O que se repete em todos os labs

O professor impõe a **mesma metodologia** a cada lab (Lab 3, slide "Um projeto bem elaborado deve seguir uma sequência de atividades", e a estrutura dos relatórios):

1. **Planejamento das fases** do processo de desenvolvimento.
2. **Definição do problema**, **sem falar da solução** (Lab 2: "como medir de forma confiável...").
3. **Especificação da solução**: requisitos **funcionais (RF)** e **não funcionais (RNF)**.
4. **Estudo da plataforma de HW** (placa Tiva, processador, clock, pinos) e **de SW** (TivaWare, CMSIS, ThreadX).
5. **Projeto (design)**: estruturas de dados, passagem de parâmetros, **algoritmo e alocação de registradores**, diagramas (estado, sequência, objetos UML).
6. **Configuração do projeto** na IDE (µVision).
7. **Edição do código**.
8. **Teste e depuração**, com plano de testes e caso de erro.
9. **Avaliação de desempenho** (medida em **ciclos de clock**).
10. **Entrega**: código e relatório `README.md` no GitHub (4 a 8 páginas, no modelo do Lab 2).

Convenções que aparecem como requisito: **código próprio separado** do de terceiros (`src_my/`), **não copiar bibliotecas** (caminho relativo), **0 erros e 0 warnings**, **clock de 120 MHz** conferido, resolução de **1 ciclo** nas medidas.

---

## Lab 1: Símbolos pré-definidos e ambiente de debug

**O que foi pedido.** Configurar o projeto no Keil µVision (dispositivo TM4C1294NCPDT com FPU, depurador Stellaris ICDI, rodando **na placa**, não no simulador) e **capturar os valores dos símbolos pré-definidos** do compilador no depurador.

**O que quis ensinar**
- Usar o **ambiente de desenvolvimento e depuração**: breakpoints, passo a passo (F10/F11), janelas Registers, Memory, Watch, Locals e System Viewer.
- Saber que **macros do pré-processador desaparecem na compilação**: para vê-las no debug é preciso atribuí-las a variáveis, e essas variáveis precisam ser **`volatile`** para o compilador não as descartar como "código morto".
- Conhecer o que são os símbolos (`__DATE__`, `__TIME__`, `__FILE__`, `__LINE__`, `__STDC__`, `__ARMCC_VERSION`, **`__ARM_ARCH` = 7**, **`__ARM_ARCH_PROFILE` = 'M'**) e sua **utilidade** (rastreabilidade de build, `ASSERT`, portabilidade, verificação de ambiente).
- Papel de **Options for Target**, **Manage Run-Time Environment** e **Pack Installer**, e a dependência **Device:Startup → CMSIS:CORE**.
- Por que **nem toda variável pode ser vista**: escopo/tempo de vida e **otimização** (a variável vai para registrador ou é eliminada).

**Resultados que valem lembrar.** `__ARM_ARCH = 7` e perfil `'M'` confirmam **ARMv7-M**; `__ARMCC_VERSION` indica ArmClang 6; removendo o CMSIS o build quebra (`core_cm4.h`, `SysTick_Config`, `NVIC_*`, `SystemCoreClock`).

**Na prova:** `volatile` e otimização ([Resumo P1 §11.8](P1/Resumo_P1.md#s11-8), item 6); arquitetura ARMv7-M ([§6-7](P1/Resumo_P1.md#s6)).

---

## Lab 2: Interagindo com a placa Tiva (jogo de tempo de reação)

**O que foi pedido.** Com a **TivaWare**, uma aplicação que usa **interrupções** e I/O: o jogo acende o **LED D1** em instante imprevisível (< 1 s do início), o jogador aperta **SW1**, e o programa mede o tempo **em clocks** e em ms e o envia à **UART**. **Requisitos:** limite de **3 s** (RNF1), **SysTick** como temporizador (RNF2), funções da **TivaWare** (RNF3), interrupção **obrigatória de GPIO** e opcional do SysTick (RNF4), e o **vetor de exceções na Flash**, não na RAM (**RNF5**). O enunciado também pede **respostas a questões**: papel do **VTOR**, onde está, quais funções do TivaWare mudam o vetor e o conteúdo dos registradores no início da `main`.

**O que quis ensinar**
- **Inicialização antes da `main`** (reset → vetor → `Reset_Handler` → `SystemInit` → `__main` → `main`), executando passo a passo até em assembly.
- **SysTick como temporizador de alta resolução** e seu limite: 24 bits a 120 MHz alcançam só **≈ 139,8 ms**; para 3 s usa-se uma **interrupção de 1 ms + contador de software** combinado com o valor corrente do SysTick (leitura dupla contra *race condition*).
- **Interrupção de GPIO** (borda de descida) com ISR curta; **debounce** (a ISR desabilita a interrupção na primeira borda válida).
- **Vetor estático (Flash) × relocado (RAM):** `IntRegister()` e atalhos (`GPIOIntRegister`, `SysTickIntRegister`) **copiam a tabela para a RAM e reprogramam o VTOR**; para cumprir RNF5 **não se chama essas funções** e define-se as ISRs **pelo nome** (`SysTick_Handler`, `GPIOJ_Handler`), que substituem os símbolos `WEAK` do startup.
- **Máquina de estados** de uma rodada (ARMING → WAITING_PRESS → DONE) e diagrama de sequência.
- Acesso a periféricos **só por biblioteca** (contraste com o Lab 1, que usava registradores).

**Respostas e fatos que valem lembrar**
- **VTOR** (Vector Table Offset Register) guarda o **endereço base da tabela de vetores**; o núcleo busca o handler em `VTOR + 4×N`. Fica no SCB/NVIC, endereço **`0xE000_ED08`**. Valor `0x0000_0000` = tabela na **Flash**; dentro de `0x2000_0000-0x2003_FFFF` = RAM.
- Início da `main` (na placa): **VTOR = 0**, **CONTROL = 0x4** (privilegiado, **MSP**, FPCA = 1), **xPSR = 0x21000000** (**T = 1**, IPSR = 0 → **Thread mode**), **MSP = 0x20000280** (topo da área de 512 bytes de pilha).
- O **C** veio setado em xPSR: **as flags não são zeradas por hardware** na entrada da `main`.
- Delay aleatório de 200 a 900 ms (LCG semeado pelo SysTick), pausa de 1,5 s entre rodadas, sem `printf`.

**Na prova:** exceções, NVIC, tabela de vetores, VTOR, ISR, SysTick, boot ([Resumo P1 §11-13, §17](P1/Resumo_P1.md#s11)); FSM ([§14](P1/Resumo_P1.md#s14)); e a questão de **registradores da CPU** ([§8.3-8.6](P1/Resumo_P1.md#s8)).

---

## Lab 3: Programação em assembly e AAPCS (histograma)

**O que foi pedido (enunciado original).** Uma rotina em **assembly** chamada de C/C++ que constrói o **histograma de uma imagem em tons de cinza de 8 bits**:

```c
uint16_t EightBitHistogram(uint16_t width, uint16_t height, uint8_t *p_image, uint16_t *p_histogram);
```

- `p_histogram` aponta um vetor de **256 posições de 16 bits sem sinal**, **sem dados válidos** na chamada: a rotina **zera** antes de usar.
- **Retorno:** número de pixels processados (16 bits); **0 se a imagem passar de 64K pixels** (e o histograma **não** é modificado).
- Percorrer a imagem **como um vetor linear**, lendo **cada pixel uma só vez**.
- **2 casos de teste** (uma imagem 3×4 para passo a passo e uma 160×120), **validação** (sugestão: a mesma função em C++) e **medida de desempenho em ciclos** com o **DWT** (resolução de 1 ciclo).
- Relatório com: algoritmo (diagrama de atividades UML), **alocação de variáveis a registradores**, **diagrama da alocação da imagem e do histograma na memória, com a largura de cada elemento**, e escolha do formato **LD/ST** em cada trecho.

**O que quis ensinar**
- **Escrever uma rotina em assembly Thumb-2** e integrá-la a C/C++.
- **AAPCS/ATPCS:** parâmetros em R0-R3, retorno em R0, **R4-R11 preservados** (se usar além de R0-R3 e R12, **salvar na pilha** e restaurar).
- **Largura de dados:** `LDRB` para o pixel (8 bits), `LDRH`/`STRH` para o histograma (16 bits), `STRH` nas contagens; o diagrama de memória decide a instrução.
- **Planejar antes de codificar** (algoritmo, tabela variável → registrador).
- **Medir desempenho** em ciclos (DWT_CYCCNT; exige `DEMCR.TRCENA = 1`).
- Tratamento de **erro** (retorno 0) e **validação cruzada** asm × C++.

**Resultados:** soma dos bins = 19.200 (160×120) e **igual à versão C++**; caso de erro (65535 × 2) retornou 0 com histograma intacto; **≈ 308.830 ciclos** (**16,08 ciclos/pixel**).

**Na prova:** é o **treino direto da Q3 de 2022** (planejar, alocar registradores, codificar com AAPCS e instruções eficientes) ([Gabarito 2022 Q3](P1/Gabarito_Prova2022.md#q3), [Resumo P1 §9-10](P1/Resumo_P1.md#s9)). Reveja: `LDRB`/`LDRH`/`STRH`, modos de endereçamento, `PUSH`/`POP` de R4-R11, multiplicação `width × height` (`MUL`/`UMULL`), `CMP` com sem sinal.

---

## Lab 4a: Joystick, LED RGB e UART

**O que foi pedido.** Com a **BoosterPack BOOSTXL-EDUMKII**, ler o **joystick** (eixos X e Y por **ADC** e o botão), enviar os valores pela **UART0 (115200 8N1) a cada 200 ms** e acionar o **LED RGB** com **cores relativas** ao valor lido (**PWM** por cor).

**O que quis ensinar**
- Integrar **entrada analógica (ADC)**, **saída PWM** e **serial** no mesmo projeto.
- Usar um **timer como disparo de hardware do ADC**: período **exato e sem jitter** (sem depender da latência de uma ISR).
- Tratar **uma interrupção** registrando a ISR **no vetor em Flash** (sem `IntRegister()`, como no Lab 2).
- Aplicar a **ordem correta de inicialização** de periféricos (`SysCtlPeripheralEnable`, `SysCtlPeripheralReady` antes de acessar).
- **Arquitetura ISR + laço de fundo:** a ISR do ADC lê as amostras, atualiza o PWM e sinaliza `g_nova`; **a impressão fica no laço principal**, nunca na ISR.

**Resultados e decisões:** Timer0A a 5 Hz → ADC0 SS2 (AIN9 = X, AIN0 = Y) → ADC0SS2_Handler (IRQ 16); **calibração** dos eixos (mínimo, centro, máximo medidos) e mapeamento de cor sobre a faixa útil.

**Na prova:** **ISR curta**, limpar o pedido, variáveis `volatile`, timers ([Resumo P1 §11.8, §13](P1/Resumo_P1.md#s11-8)); no Projeto Final é a base do ADC por timer.

---

## Lab 4b: Geração de pulsos, assembly × C × C+TivaWare

**O que foi pedido.** **1000 pulsos** no pino do LED1 (PN1) por **três técnicas**: **C+TivaWare** (`GPIOPinWrite`), **C puro** (escrita `volatile` direta em `GPIODATA`, endereço mascarado) e **assembly** (AAPCS, desenrolado ×8, 16 `STR` por iteração). **Medir o tempo de cada uma em ciclos com o SysTick** e enviar uma **tabela comparativa** pela UART. Restrições: **frequência mais alta possível**, **sem I/O serial no trecho medido**, **overhead da medida calibrado e descontado**, detectar **estouro** do SysTick de 24 bits.

**O que quis ensinar**
- Acessar um periférico em **três níveis de abstração** e **entender o custo de cada um**.
- Escrever assembly **AAPCS otimizado para velocidade** (desenrolar o laço).
- Usar o **SysTick como instrumento de medida** em ciclos, controlando o próprio **overhead** da medida.
- **Relacionar o código gerado (disassembly) com o desempenho**.

**Resultados:** assembly **2.432 ciclos (20,26 µs)**; C puro **2.804 ciclos (23,36 µs)**; C+TivaWare **22.057 ciclos (183,80 µs)**. O assembly foi **9,06× mais rápido** que a TivaWare e **1,15× mais rápido** que o C puro. **O custo da abstração** (chamadas de função da biblioteca) domina; **a otimização do compilador aproxima o C do assembly**.

**Na prova:** SysTick e `RVR` de 24 bits ([Resumo P1 §13](P1/Resumo_P1.md#s13)); AAPCS ([§10](P1/Resumo_P1.md#s10)); idéia de "usar o conjunto de instruções com eficiência".

---

## Lab 5a: Estudo do `demo_threadx.c` e porte do ThreadX para a Tiva

**O que foi pedido.** **Obter o ThreadX** (6.5.2, GitHub eclipse-threadx), **compilar como biblioteca** (ARMCM4 com FPU, ArmClang 6, C99, `-O2`) e portar o **`ThreadX_Demo` do professor**. **Entregáveis:** **Tabela 1** (as **8 threads**: nome, função de entrada, pilha, prioridade, auto start, time slice), **Tabela 2** (os **7 objetos**: estrutura de controle, tamanho da estrutura, dados adicionais, **onde ficam na memória**) e o **diagrama de objetos UML** na notação do slide 5 do enunciado.

**O que quis ensinar**
- **Ler a documentação dos serviços** do ThreadX e reconhecer, no código, **o objeto, a estrutura de controle e a memória adicional** que cada um exige.
- Relacionar cada objeto com o **segmento de memória** (`.bss` × *pool* do ThreadX).
- **Atributos da thread**: prioridade, *preemption-threshold*, **time-slice**, auto start.
- A **notação UML da disciplina** (thread com barras laterais, semáforo, mutex, event flag, bloco de memória).
- Compilar com **bibliotecas externas sem copiar** (caminho relativo).

**Resultados que valem lembrar**
- **Tabela 1:** thread 0 (prio 1, sem fatia), threads 1 e 2 (prio 16, **time-slice de 4 ticks**), 3 e 4 (prio 8, **mesmo código** `thread_3_and_4_entry`, diferenciadas por `thread_input`), 5 (prio 4), 6 e 7 (prio 8). **Todas com pilha de 1024 B** e *threshold* igual à prioridade (sem limiar efetivo).
- **Tabela 2 (tamanho das estruturas, ARMv7-M de 32 bits):** byte pool **52 B**, block pool **48 B**, semáforo **32 B**, mutex **52 B**, fila **60 B**, event flags **40 B**, thread **180 B** (45 palavras). **Todas em `.bss`** (variáveis globais); a **memória adicional** (pilhas, mensagens, área do block pool) vem de um **byte pool de 9120 B**. Nenhuma em `.data`, pilha ou heap (heap = 0 B).
- Comportamento confirmado: 10/s para `thread_0` e `thread_5`; 25/s para cada thread dos pares de semáforo e mutex.

**Na prova:** **estruturas de controle globais**, byte pool × block pool, `tx_thread_create`, UML ([Compilado §3](P2/Compilado_P2.md#c3), [§1.1 memória](P2/Compilado_P2.md#c1-mem), [Gabarito Q1](P2/Gabarito_Prova2022_Q1.md#a7)). A pergunta "onde fica a estrutura de controle?" (tx 14.35-14.40) vem direto deste lab.

---

## Lab 5b: Teste de temporização do ThreadX

**O que foi pedido.** Um projeto próprio (`Lab5`) com **uma única thread** que **pisca o LED1 a cada 2 s** (1 s aceso, 1 s apagado) com `tx_thread_sleep`, no clock de **120 MHz**, para **verificar que a temporização do RTOS está correta**. **RF4:** em **30 s** o LED deve piscar **15 vezes**. **RF5:** **explicar o processo de inicialização**, do vetor de Reset à primeira instrução de uma thread. Requisitos: **coerência** do clock, **sem espera ativa** (com nenhuma thread pronta o escalonador executa `WFI`), pilha de 1024 B, teste **na placa**, 0 warnings.

**O que quis ensinar**
- Como o ThreadX **assume o SysTick, o PendSV e o SVC** do Cortex-M4.
- Por que o período do tick depende da **coerência entre quatro valores** que o RTOS **não confere** entre si:
  - clock do núcleo = **120 MHz**;
  - `SYSTEM_CLOCK` do arquivo `.s`;
  - `SYSTICK_CYCLES = SYSTEM_CLOCK/100 − 1` (**RVR = 1.199.999** → tick de **10 ms**);
  - `TX_TIMER_TICKS_PER_SECOND = 100`.
  Se não concordarem, **todos os tempos ficam errados na mesma proporção, sem aviso**.
- **Seguir o caminho do Reset até a primeira thread** instrução a instrução.

**Fluxo de inicialização (resumo do lab):** reset → o core lê **MSP** e **PC** da tabela em `0x0` → `Reset_Handler` → `SystemInit` (libera a FPU) → `__main` (copia `.data`, zera `.bss`) → `main` (clock de 120 MHz, LED) → **`tx_kernel_enter()`** (não retorna) → `_tx_initialize_low_level` (desabilita interrupções, VTOR, DWT, **programa o SysTick**, prioridades de SysTick e PendSV) → `_tx_initialize_high_level` (estruturas internas e a **System Timer Thread**) → **`tx_application_define`** → `_tx_thread_schedule` (habilita interrupções e dispara o **PendSV**) → o PendSV restaura o contexto da thread de maior prioridade → `_tx_thread_shell_entry` chama a função de entrada.

**Resultados:** `g_timing_ok = 1`; cada fase = **120.000.000 ciclos (±4)** e 100 ticks; o cronômetro do PC mediu **0,9997 s** por fase; **15 piscadas em 30 s**.

**Na prova:** **boot de uma aplicação ThreadX** e o tick do SysTick ([Compilado §3.2](P2/Compilado_P2.md#c3), tx 14.63-14.67; [Resumo P1 §17](P1/Resumo_P1.md#s17)); SysTick e `RVR` ([§13](P1/Resumo_P1.md#s13)); PendSV e SVC ([§11.4](P1/Resumo_P1.md#s11-4)).

---

## Lab 6a: Escalonamento no ThreadX

**O que foi pedido.** **3 tarefas periódicas**, cada uma com um LED e prazo igual ao período, executadas sob **5 condições de escalonamento** (relatando se os períodos e prazos são cumpridos):

| Tarefa | Período | Execução | Prioridade |
|---|---:|---:|---|
| T1 | 1 s | 300 ms | alta |
| T2 | 1,5 s | 500 ms | média |
| T3 | 4 s | 800 ms | baixa |

- **(a)** *time-slice* de 50 ms, mesma prioridade; **(b)** sem time-slice e **sem preempção**, com as prioridades da tabela; **(c)** **preemptivo por prioridade**; **(d)** T1 e T3 compartilham um **mutex sem herança**; **(e)** idem **com herança de prioridade**.
- Rotina **`blink_led(led, repetitions)` reentrante** (tempo de execução conhecido e ajustável), calibrada para 300, 500 e 800 ms.
- **Orientação do professor:** **não usar `tx_thread_sleep` para o período**; usar **timers ou mensagens** (aqui, um `TX_TIMER` periódico por tarefa que libera um semáforo).

**O que quis ensinar**
- **Relacionar o comportamento observado com a teoria:** preempção, seção crítica, exclusão mútua, **inversão de prioridade** e **herança de prioridade**.
- Usar `tx_thread_create` com **prioridade, *preemption-threshold* e time-slice**, `tx_timer_create`, `tx_semaphore_create`, `tx_time_get` e `tx_mutex_create` (`TX_INHERIT` × `TX_NO_INHERIT`).
- **Validar medidas por fontes independentes** (ciclos do núcleo, ticks do ThreadX, cronômetro do PC).

**Resultados (resposta máxima em ms):**

| Cen. | R1 | R2 | R3 | Perdas de prazo | Lição |
|---|---:|---:|---:|---|---|
| a (time-slice) | 1000,05 | 1500,11 | 2350,14 | T1 e T2 por **µs** | divide a CPU em fatias iguais; **sem garantia** de prazo |
| b (sem preempção) | 900,36 | 1400,32 | 1600,31 | nenhuma (fase medida) | o bloqueio de 0,8 s de T3 causa muito **jitter** |
| c (preemptivo) | **300,10** | 800,17 | **2700,51** | nenhuma | T1 regular; T3 paga a interferência |
| d (mutex **sem** herança) | 1100,30 | 850,30 | 2700,59 | **T1 perde (≈ 1 a cada 12 s)** | **inversão de prioridade** |
| e (mutex **com** herança) | 600,22 | 1350,37 | 2700,60 | nenhuma | a herança elimina a perda; **T2 paga** (0,85 → 1,35 s) |

**Pegadinhas do lab:** para "sem preempção" usa-se **`threshold = 1`, não 0** (a System Timer Thread tem prioridade 0 e travaria); a inversão **só aparece** se T3 já está na seção crítica quando T1 chega e T2 é liberada durante a espera; o ThreadX tomou **HardFault no primeiro instante ocioso** sob o depurador, contornado com uma **thread de fundo**.

**Na prova:** é o **laboratório do escalonamento** da P2: [Compilado §4](P2/Compilado_P2.md#c4), [G1 (escalonar)](P2/Compilado_P2.md#g1), [G2 (testes)](P2/Compilado_P2.md#g2) e [G3 (inversão de prioridade, PIP)](P2/Compilado_P2.md#g3). **Confira:** o R3 = 2,7 s medido é **exatamente** o que o Teorema 3 / análise de resposta prevê para esse conjunto (U = 0,833; [Resumo_Escalonamento §3](P2/Resumo_Escalonamento.md#e3)), e R1 = 0,6 s e 1,1 s são os cenários e/d de [Resumo_Escalonamento §9](P2/Resumo_Escalonamento.md#e9).

---

## Projeto Final: Filtro Digital Parametrizado

**O que foi pedido.** Um **sistema que recebe um sinal analógico, aplica em tempo real um filtro digital escolhido pelo usuário e devolve um sinal analógico**. O usuário muda o **tipo** (passa-baixa, passa-alta, passa-faixa, corta-faixa) e a **frequência de corte** por uma **IHM** (display, joystick e botões do BoosterPack). A **ordem** é fixa (4). Entregas em **duas fases**: **Documento 1** (CONOPS, domínio do problema e especificação) e **Documento 2** (estudo da plataforma e design); depois o projeto.

**O que quis ensinar**
- **Engenharia de requisitos**: **CONOPS** (stakeholders, necessidades N-xx, cenários), **SysML** (diagrama de contexto e de blocos), e **especificação funcional e não funcional testável** (RF-xx, RNF-xx, restrições R-xx), cada um com **forma de verificação**.
- **Domínio do problema** (processamento de sinais): amostragem e **aliasing**, filtros digitais, **quantização**, reconstrução (PWM + **filtro RC passivo**), **medição e verificação** com gerador e osciloscópio.
- **Design em tempo real**: escolha dos canais do ADC, condicionamento, **taxa de amostragem** (≥ 2,4 × f_max), **planejamento temporal** e **planejamento do escalonamento**.
- **Arquitetura em UML** com a notação do curso (a mesma do Lab 5a) e o uso do ThreadX.

**Decisões de projeto (Documento 2)**
- **ADC disparado por timer** (Timer0 a **50 kHz**, sem CPU e sem jitter) com interrupção ao fim da conversão; **PWM a 250 kHz** + filtro RC como DAC.
- **Blocos de 50 amostras = 1 ms:** a **ISR** (20 µs por amostra, ≈ 1 µs de execução) grava e lê duas metades alternadas de `buffer_amostras`, e ao completar um bloco faz `put` no semáforo `bloco_pronto`.
- **Threads (menor número = maior prioridade):** `FilterThread` (**2**, tempo real rígido, 1 ms), `SupervisorThread` (8, 100 ms), `IhmThread` (10, 10 ms), `DisplayThread` (12, sob demanda), `IdleThread` (31, evita o HardFault do escalonador ocioso, **aprendizado do Lab 6**).
- **Objetos ThreadX:** semáforo de contagem `bloco_pronto`, **event flags** `evento_config` e `evento_tela`, **mutex com herança** `mutex_config` (posse de poucos µs).
- **Compartilhamento sem mutex no caminho crítico:** as duas metades do buffer são usadas **alternadamente** (nunca a mesma ao mesmo tempo) e os contadores de aviso têm **um único escritor** cada.
- **Escalonamento:** prioridades **por taxa** (rate monotonic: o mais frequente tem a maior prioridade), **sem preemption-threshold** (para não bloquear a timer thread), resposta de pior caso da `FilterThread` ≈ 80 µs (33 µs + 43 µs de recálculo + interferência da ISR) contra o prazo de 1 ms; ISR (≈ 5%) + filtro (3,3%) ≈ 8% da CPU.
- Perguntas do roteiro de estudo respondidas: **o ADC pode ser disparado por timer** (benefício: **instantes sem jitter**) e **avisa o fim da conversão por interrupção** do sequenciador (`ADC_CTL_IE`).

**Na prova:** é praticamente **a P2 inteira aplicada**: [ThreadX e UML (G6)](P2/Compilado_P2.md#g6), [Rate Monotonic e Teoremas (G2)](P2/Compilado_P2.md#g2), [exclusão mútua e compartilhamento sem mutex](P2/Compilado_P2.md#c1-mem), [cliente-servidor e mensagens (G5)](P2/Compilado_P2.md#g5). A decisão "**ISR curta + thread que trabalha**" é a mesma da IST (sch 15.11).

---

## O fio condutor entre os labs

| Lab | Faz com... | Para o próximo lab |
|---|---|---|
| 1 | ferramentas e `volatile` | base de tudo |
| 2 | **interrupção + SysTick + vetor** | ISR de GPIO; boot |
| 3 | **assembly e AAPCS** | medida em ciclos (DWT) |
| 4a | ADC + PWM + **timer disparando o ADC** | reaparece no **Projeto** |
| 4b | **custo da abstração** e **SysTick medindo ciclos** | mesma técnica de medida |
| 5a | **objetos ThreadX e onde ficam na memória** | tabelas e UML |
| 5b | **tick e boot do ThreadX** | base do Lab 6 e do projeto |
| 6a | **escalonamento, inversão de prioridade** | planejamento do projeto |
| Projeto | **tudo, em tempo real** | – |

## Perguntas que os labs permitem fazer na prova (estimativa)

Estas **não são garantidas**; são o que o conteúdo dos labs naturalmente permite cobrar.

1. **Por que o SysTick sozinho não mede 3 s a 120 MHz? Como contornar?** (Lab 2; [Resumo P1 §13.4](P1/Resumo_P1.md#s13-4)).
2. **Qual o papel do VTOR e como saber se o vetor está na Flash ou na RAM?** (Lab 2).
3. **Quais registradores estão preservados pela AAPCS e como se escolhe `LDRB`/`LDRH`/`LDR`?** (Lab 3).
4. **Escreva a função de histograma (ou parte dela) em assembly, com planejamento e tabela de registradores.** (Lab 3 = Q3 de 2022).
5. **Por que o ADC deve ser disparado por timer em vez de por software?** (Lab 4a e Projeto).
6. **Por que a impressão fica fora da ISR?** (Lab 4a).
7. **Por que o C+TivaWare é bem mais lento que o C puro e o assembly?** (Lab 4b).
8. **Onde ficam as estruturas de controle de uma thread, uma fila e um mutex? E a pilha da thread?** (Lab 5a; tx 14.35-14.40).
9. **Quais valores precisam concordar para o tick do ThreadX estar certo?** (Lab 5b).
10. **Descreva o caminho do reset até a primeira thread.** (Lab 5b; Resumo P1 §17 e tx 14.64-14.67).
11. **Desenhe a execução de T1, T2, T3 com preempção; calcule R3; mostre a inversão de prioridade e como a herança resolve.** (Lab 6a; [Compilado G1-G3](P2/Compilado_P2.md#c6)).
12. **Por que `threshold = 0` não pode ser usado para impedir preempção?** (Lab 6a).
13. **Desenhe a arquitetura UML do projeto (ISR, threads, semáforo, evento, mutex).** (Lab 5a e Projeto; [G6](P2/Compilado_P2.md#g6)).

---

**Para estudar:** refaça, **sem olhar**, a explicação do **boot** (Labs 2 e 5b), a tabela de **cenários do Lab 6** (com o motivo de cada resultado), a **lista de requisitos de cada lab** e as **respostas do Lab 2** sobre VTOR e registradores.
