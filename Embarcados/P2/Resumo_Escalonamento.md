# Resumo – Escalonamento (tarefas independentes e recursos compartilhados)

Complemento do [Resumo_P2.md](Resumo_P2.md). Aqui o foco é **escalonamento de tempo real**: como atribuir prioridades e **provar** (ou testar) que os prazos serão cumpridos.

## Aviso importante: o que está e o que não está nos slides

Os três PDFs da P2 (`13_concurrency`, `13_mutual_exclusion`, `14_t threadx_rtos`) **não trazem** escalonamento de tempo real. Só aparecem:

| No slide | O quê |
|---|---|
| conc 13.13, 13.16 | escalonamento é o **4º problema** do ambiente multitarefa; RTOS **preemptivo por prioridade** |
| conc 13.14 | "deadlocks e **inversão de prioridade**" citados como riscos |
| tx 14.29 | prioridades do ThreadX (0 = maior), FIFO, time-slice, *preempt threshold*, **herança de prioridade** nos mutexes |
| tx 14.32, 14.54-14.55 | mutex com **`TX_INHERIT`** |

**Todo o resto deste documento é 🧩 (material complementar, não está nos slides).** Ele segue a teoria clássica (Liu & Layland, Sha et al., Buttazzo). Confirme com o professor **o quanto disso cai**, e use o **Lab 6** como guia: ele mostra o que o professor trabalha na prática (time-slice, preempção, mutex com e sem herança).

## Índice

1. [Conceitos e modelo de tarefas](#e1)
2. [Tarefas independentes: executivo cíclico, RM, DM, EDF](#e2)
3. [Exemplo completo (as tarefas do Lab 6)](#e3)
4. [Recursos compartilhados: bloqueio e inversão de prioridade](#e4)
5. [Protocolos: PIP, PCP, ICPP e outros](#e5)
6. [Análise de escalonabilidade com bloqueio](#e6)
7. [Deadlock](#e7)
8. [No ThreadX](#e8)
9. [Exemplo com recursos (cenários d e e do Lab 6)](#e9)
10. [Exercícios resolvidos](#e10)
11. [Fórmulas e tabelas de revisão rápida](#e11)
12. [Autoteste](#e12)
13. [Para ir além](#e13)

---

<a id="e1"></a>
## 1. Conceitos e modelo de tarefas

**Sistema de tempo real:** a correção depende do **resultado** e do **instante** em que ele sai.

| Tipo | Perder um prazo significa |
|---|---|
| **Hard** (crítico) | falha do sistema (ex.: freio ABS, airbag) |
| **Firm** | o resultado atrasado não serve, mas o sistema segue |
| **Soft** | o resultado atrasado vale menos (ex.: vídeo, interface) |

**Tipos de tarefa:** **periódica** (libera um job a cada período T), **esporádica** (chega em instantes imprevistos, com intervalo mínimo entre chegadas) e **aperiódica** (sem intervalo mínimo).

### Parâmetros de uma tarefa τ_i

| Símbolo | Nome | Significado |
|---|---|---|
| **C_i** | tempo de execução (pior caso, WCET) | CPU que cada job precisa |
| **T_i** | período | intervalo entre liberações |
| **D_i** | prazo relativo (*deadline*) | tempo, a partir da liberação, para terminar (em geral D_i = T_i) |
| **φ_i** | fase | instante da primeira liberação |
| **P_i** | prioridade | número que o escalonador usa |
| **R_i** | tempo de resposta | da liberação ao fim do job; é preciso **R_i ≤ D_i** |
| **U_i = C_i / T_i** | utilização | fração da CPU que a tarefa usa |
| **U = Σ U_i** | utilização total | se **U > 1**, nenhum escalonador consegue |
| **B_i** | tempo de bloqueio | tempo que τ_i espera uma tarefa de **prioridade menor** (aparece com recursos compartilhados) |

**Job** = uma execução (uma instância) de uma tarefa. **Hiperperíodo** = mínimo múltiplo comum dos períodos; o padrão de execução se repete a cada hiperperíodo.

**Tarefas independentes** (modelo mais simples): não compartilham recursos, não têm relação de precedência e nunca bloqueiam uma à outra. Só competem pela CPU. É o que a [seção 2](#e2) trata. A [seção 4](#e4) retira essa hipótese.

**Hipóteses do modelo clássico (Liu & Layland):** tarefas periódicas, D_i = T_i, independentes, C_i constante, preempção instantânea e sem custo (a troca de contexto do ThreadX é ~0,4 µs, tx 14.19, desprezível frente a ms), um processador.

### Classificação dos escalonadores

| Critério | Opções |
|---|---|
| **Quando decide** | **estático** (offline, tabela pronta) ou **dinâmico** (online) |
| **Prioridade** | **fixa** (não muda entre jobs; RM, DM) ou **dinâmica** (muda a cada job; EDF) |
| **Preemptivo?** | preemptivo (maior prioridade tira a CPU) ou não preemptivo ([Resumo P2 §2.2](Resumo_P2.md#s2)) |
| **Ótimo** | um algoritmo é **ótimo** (numa classe) se, sempre que existir um escalonamento viável, ele o encontra |

---

<a id="e2"></a>
## 2. Tarefas independentes

### 2.1 Executivo cíclico (escalonamento estático)

Uma **tabela** pré-calculada diz qual tarefa executa em cada intervalo, repetida a cada hiperperíodo (*major cycle*), dividido em quadros (*minor cycles*, ou *frames*).

- **Vantagens:** determinístico, sem overhead de escalonador, fácil de verificar, sem preempção (nada de recurso compartilhado entre tarefas do mesmo quadro).
- **Desvantagens:** rígido (mudar uma tarefa refaz a tabela), difícil com períodos que não são múltiplos, ruim para tarefas esporádicas.
- Regras comuns para o tamanho do quadro f: **f ≥ máximo C_i**; **f divide o hiperperíodo**; e `2f − mdc(f, T_i) ≤ D_i` para toda tarefa. 🧩

### 2.2 Rate Monotonic (RM)

**Regra:** **quanto menor o período, maior a prioridade** (prioridade fixa).

- É **ótimo entre os algoritmos de prioridade fixa** quando D_i = T_i (Liu & Layland, 1973): se algum conjunto de prioridades fixas funciona, o RM também.
- **Instante crítico:** o pior caso de resposta de uma tarefa ocorre quando ela é liberada **junto com todas as de prioridade maior**. Por isso testa-se o caso em que todas começam em t = 0.

**Teste de utilização (suficiente, não necessário):**

```
U = Σ C_i / T_i  ≤  n · (2^(1/n) − 1)
```

| n | 1 | 2 | 3 | 4 | 5 | 10 | ∞ |
|---|---|---|---|---|---|---|---|
| Limite | 1,000 | 0,828 | **0,780** | 0,757 | 0,743 | 0,718 | **0,693** (= ln 2) |

- Se `U ≤ limite` → **escalonável** garantidamente.
- Se `U > limite` → o teste **não conclui**: pode ou não ser escalonável (use a análise de resposta abaixo).
- Se `U > 1` → **não** é escalonável.
- **Períodos harmônicos** (cada um múltiplo do menor): o limite sobe para **U ≤ 1**.
- **Limite hiperbólico** (mais preciso, Bini et al., 2001): `Π (U_i + 1) ≤ 2`. 🧩

### 2.3 Análise do tempo de resposta (exata, prioridade fixa)

Para a tarefa i, considerando só as de **prioridade maior** (hp(i)):

```
R_i = C_i + Σ_{j ∈ hp(i)} ⌈ R_i / T_j ⌉ · C_j
```

Resolve-se **iterando**: comece com R⁰ = C_i, calcule o lado direito, repita até o valor **parar de mudar** (convergiu) ou **passar de D_i** (não escalonável).

- **Condição:** `R_i ≤ D_i` para **todas** as tarefas. É **necessária e suficiente** (exata) para prioridade fixa com preempção e instante crítico.
- O termo `⌈R_i / T_j⌉ · C_j` é a **interferência**: quantos jobs de τ_j caem dentro da janela de resposta de τ_i.

### 2.4 Deadline Monotonic (DM)

Mesma ideia do RM, mas com **prazo menor que o período (D_i < T_i)**: **quanto menor o prazo, maior a prioridade**. É **ótimo** entre os de prioridade fixa quando D_i ≤ T_i. O teste é o mesmo `R_i ≤ D_i` da análise de resposta.

### 2.5 Earliest Deadline First (EDF)

**Regra:** a tarefa com o **prazo absoluto mais próximo** executa primeiro. Prioridade **dinâmica** (muda a cada job).

- **Ótimo** para um processador com preempção (entre todos os algoritmos).
- **Teste exato** para D_i = T_i: **`U ≤ 1`** (necessário e suficiente).
- Para D_i < T_i usa-se a análise da **demanda de processador** (mais trabalhosa). 🧩
- Em **sobrecarga** (U > 1) o EDF pode piorar tudo (efeito dominó: perde prazos em cadeia). O RM falha de forma mais **previsível**: perdem as tarefas de **menor prioridade**.
- Mais difícil de implementar num RTOS comum (prioridades fixas): exige reordenar a cada liberação.

### 2.6 Outros

- **Least Laxity First (LLF):** executa a tarefa com menor *laxity* (folga = prazo − agora − trabalho restante). Ótimo, mas muda de tarefa com muita frequência.
- **Round-robin / time-slice:** nenhuma garantia de prazo; só reparte a CPU entre tarefas de **mesma prioridade** (tx 14.29).
- **Tarefas aperiódicas:** usam-se **servidores** (*polling*, *deferrable*, *sporadic*) que reservam uma parte da CPU, ou rodam em **background** com a menor prioridade. 🧩

### 2.7 Comparação

| | **RM** | **EDF** |
|---|---|---|
| Prioridade | **fixa** (pelo período) | **dinâmica** (pelo prazo) |
| Limite de utilização | `n(2^(1/n)−1)` → 69,3% | **100%** |
| Teste exato | análise de resposta | `U ≤ 1` (se D = T) |
| Implementação | simples; um RTOS de prioridade fixa já faz | exige suporte a prioridade dinâmica |
| Sob sobrecarga | previsível (perdem as de menor prioridade) | pode perder prazos em cadeia |
| Jitter | baixo nas de alta prioridade | maior |

---

<a id="e3"></a>
## 3. Exemplo completo (as tarefas do Lab 6)

Lab 6: T1 (C = 0,3 s, T = 1 s), T2 (C = 0,5 s, T = 1,5 s), T3 (C = 0,8 s, T = 4 s), prazo = período. Prioridade RM: **T1 > T2 > T3**.

**Utilização**

```
U1 = 0,3/1 = 0,300      U2 = 0,5/1,5 = 0,333      U3 = 0,8/4 = 0,200
U = 0,833
```

**Teste do RM (n = 3):** limite = 0,780. Como **0,833 > 0,780**, o teste **não conclui**. Como **0,833 ≤ 1** não está descartado.

**Análise de resposta (exata):**

| Tarefa | Iteração | R |
|---|---|---|
| T1 | R = C1 | **0,3 s** ≤ 1 ✓ |
| T2 | R⁰ = 0,5; R¹ = 0,5 + ⌈0,5/1⌉·0,3 = 0,8; R² = 0,5 + ⌈0,8/1⌉·0,3 = 0,8 | **0,8 s** ≤ 1,5 ✓ |
| T3 | R⁰ = 0,8; R¹ = 0,8 + ⌈0,8/1⌉·0,3 + ⌈0,8/1,5⌉·0,5 = 1,6; R² = 0,8 + 2·0,3 + 2·0,5 = 2,4; R³ = 0,8 + 3·0,3 + 2·0,5 = 2,7; R⁴ = 2,7 | **2,7 s** ≤ 4 ✓ |

**Conclusão:** é escalonável por RM, mesmo reprovado no teste de utilização. O resultado de T3 (**2,7 s**) coincide com a resposta máxima medida no Lab 6 (cenário c).

**EDF:** `U = 0,833 ≤ 1` → escalonável.

**Linha do tempo do RM (t = 0, todos liberados juntos):**

```
t(s): 0    0,3   0,8  1,0  1,3  1,5   2,0  2,3   2,7
      |-T1-|-T2--|-T3-|-T1-|-T3-|--T2--|-T1-|--T3--|
                  (0,2)       (0,2)            (0,4) -> T3 termina em 2,7
```

T1 é liberada em 0, 1, 2…; T2 em 0, 1,5, 3…. T3 é preemptada duas vezes e só termina em **2,7 s**.

---

<a id="e4"></a>
## 4. Recursos compartilhados

Quando as tarefas **compartilham recursos** (dado global, periférico), o acesso precisa ser **exclusivo** ([Resumo P2 §3-4](Resumo_P2.md#s3)). A tarefa que tenta entrar na seção crítica com o recurso ocupado fica **bloqueada**, e isso pode **quebrar** a análise da seção 2, porque uma tarefa de alta prioridade passa a esperar uma de baixa.

### 4.1 Bloqueio

**Bloqueio** (*blocking*) = uma tarefa de **maior** prioridade espera uma de **menor** prioridade que está na seção crítica. É inevitável se houver exclusão mútua. O que importa é que seja **limitado** e **curto**: o **tempo de bloqueio B_i** (pior caso) entra nas análises de escalonabilidade ([seção 6](#e6)).

### 4.2 Inversão de prioridade

**Cenário clássico** (três tarefas L < M < H em prioridade, H e L compartilham um mutex):

```
1. L entra na seção crítica (pega o mutex).
2. H é liberada, preempta L e tenta pegar o mutex → BLOQUEIA (L tem o mutex).
3. L volta a executar para terminar a seção crítica.
4. M é liberada, e como M > L, M PREEMPTA L. M não usa o mutex.
5. H continua bloqueada enquanto M executar. L só continua quando M acabar.
```

H (alta) esperou M (média), que nem tem relação com ela: **inversão de prioridade**. O problema é que o bloqueio **não tem limite**: podem entrar **muitas** tarefas médias, e H pode perder o prazo.

**Caso real:** em 1997 o robô Mars Pathfinder (VxWorks) reiniciava por inversão de prioridade (tarefa de comunicação média preemptava a de baixa que segurava o mutex da tarefa de gerenciamento do barramento, alta). Foi corrigido ligando a **herança de prioridade** no mutex.

### 4.3 O que não resolve

- **Mais tarefas** ou **mais prioridades**: não resolvem.
- **Semáforo em vez de mutex:** não tem dono, então não tem como herdar prioridade (tx 14.54-14.55; [Resumo P2 §8.5](Resumo_P2.md#s8-5)).

---

<a id="e5"></a>
## 5. Protocolos para limitar o bloqueio

### 5.1 Desabilitar a preempção (ou as interrupções)

A seção crítica **não pode ser interrompida**. Simples, mas **todas** as tarefas (até as não relacionadas) sofrem o bloqueio. Só serve para seções **muito curtas** ([Resumo P2 §4.2](Resumo_P2.md#s4)).

### 5.2 Priority Inheritance Protocol (PIP, herança de prioridade)

**Regra:** enquanto uma tarefa **H está bloqueada** num recurso, a **dona** do recurso (L) **herda a prioridade de H**. Quando L solta o recurso, volta à prioridade original.

- No cenário da [seção 4.2](#e4), L passa a ter a prioridade de H e **M não consegue preemptá-la**.
- A herança é **transitiva** (se L estiver bloqueada em outro recurso, a dona desse também herda).
- **Limite do bloqueio:** uma tarefa pode ser bloqueada **no máximo uma vez por tarefa de prioridade menor** e **uma vez por recurso**. Pode haver **bloqueio em cadeia**.
- **Não evita deadlock** com mutexes aninhados.
- É o que o ThreadX implementa (`TX_INHERIT`, tx 14.29, 14.32).

### 5.3 Priority Ceiling Protocol (PCP)

Cada recurso tem um **teto** (*ceiling*) = a **maior prioridade** entre as tarefas que **podem** usá-lo.

**Regra de entrada:** uma tarefa só pode pegar um recurso se sua prioridade for **maior que o teto de todos os recursos que outras tarefas estão segurando** (o "teto do sistema"). Senão, **bloqueia** (mesmo que o recurso esteja livre). A dona herda a prioridade da bloqueada (como no PIP).

- Uma tarefa é bloqueada **no máximo uma vez**, pela seção crítica mais longa de uma tarefa de menor prioridade.
- **Sem bloqueio em cadeia e sem deadlock.**
- Mais complexo: precisa saber **de antemão** quais tarefas usam quais recursos.

### 5.4 Immediate Ceiling Protocol (ICPP, *highest locker*)

**Regra:** ao **pegar** um recurso, a tarefa **sobe na hora** para a prioridade do **teto** do recurso, e volta ao soltar.

- Mesmas garantias do PCP (**bloqueio no máximo uma vez, sem deadlock** em um processador).
- Mais **simples**: não precisa registrar bloqueios nem herdar dinamicamente.
- Custo: sobe a prioridade mesmo quando ninguém estava esperando.
- Também chamado de *priority protect* (POSIX `PTHREAD_PRIO_PROTECT`) ou *ceiling emulation*.

### 5.5 Stack Resource Policy (SRP)

Variante (Baker) que funciona também com **EDF**: a tarefa só **começa** a executar se todos os recursos que ela pode precisar estiverem disponíveis. Garante bloqueio **no máximo uma vez** e **uma só pilha** para todas as tarefas. 🧩 (só para conhecer)

### 5.6 Resumo dos protocolos

| | Sem protocolo | **PIP** (herança) | **PCP** | **ICPP** |
|---|---|---|---|---|
| Bloqueio limitado? | **não** | sim | sim | sim |
| Máximo de bloqueios | ilimitado | 1 por tarefa menor / por recurso | **1** | **1** |
| Bloqueio em cadeia | sim | **sim** | não | não |
| Evita deadlock | não | **não** | **sim** | **sim** |
| Precisa dos tetos? | não | não | **sim** | **sim** |
| Complexidade | – | baixa | alta | **média** |
| No ThreadX | `TX_NO_INHERIT` | **`TX_INHERIT`** | não nativo | emulável 🧩 |

---

<a id="e6"></a>
## 6. Análise de escalonabilidade com bloqueio

Seja **B_i** o bloqueio de pior caso de τ_i.

**B_i por protocolo** (em ordem de prioridade; "seção crítica" = tempo que uma tarefa **menor** segura o recurso):

- **PCP / ICPP:** B_i = a **maior** seção crítica de uma tarefa de prioridade menor sobre um recurso cujo **teto ≥ prioridade de τ_i**.
- **PIP:** B_i ≤ soma das maiores seções críticas, no máximo **uma por tarefa menor** (e uma por recurso). É um limite superior (pode ser pessimista).

**Análise de resposta com bloqueio (prioridade fixa):**

```
R_i = C_i + B_i + Σ_{j ∈ hp(i)} ⌈ R_i / T_j ⌉ · C_j        e exige  R_i ≤ D_i
```

**Teste de utilização do RM com bloqueio (suficiente):**

```
Para cada i:   Σ_{j ≤ i} C_j/T_j  +  B_i/T_i   ≤   i · (2^(1/i) − 1)
```

(a soma vai até a tarefa i, em ordem de prioridade.)

**EDF com SRP** (suficiente, Baker): para cada i, `Σ_{j : D_j ≤ D_i} C_j/T_j + B_i/D_i ≤ 1`. 🧩

**Passo a passo para uma questão:**
1. Ordene as tarefas por prioridade (RM: menor período primeiro).
2. Identifique os recursos, quem os usa e **a duração de cada seção crítica**.
3. Calcule **B_i** de cada tarefa pelo protocolo dado.
4. Aplique a análise de resposta com B_i (ou o teste de utilização com B_i/T_i).
5. Conclua se algum `R_i > D_i`.

---

<a id="e7"></a>
## 7. Deadlock

**Condições de Coffman** (as 4 precisam valer juntas): (1) **exclusão mútua**, (2) **posse e espera** (segura um recurso e pede outro), (3) **sem preempção do recurso** (só quem tem solta), (4) **espera circular**. Retire **uma** e não há deadlock ([Resumo P2 §3.5](Resumo_P2.md#s3), excl 13.28).

Exemplo: A pega M1 e pede M2; B pega M2 e pede M1.

**Como prevenir:**
- **Ordem global** de aquisição (todos pegam M1 antes de M2): quebra a espera circular.
- Pegar **todos de uma vez**, ou **nenhum**.
- **Timeout** no `get` (tx 14.43) e liberar tudo se estourar.
- Usar **PCP/ICPP**, que evitam deadlock por construção.
- **Evitar** aninhar mutexes.

**Diferença** (excl 13.28): *deadlock* = param para sempre; *livelock* = mudam de estado e não progridem; *starvation* = uma tarefa nunca é atendida.

---

<a id="e8"></a>
## 8. No ThreadX

([Resumo P2 §7.5, §8.5-8.6](Resumo_P2.md#s7))

| Assunto | ThreadX |
|---|---|
| Escalonador | **preemptivo por prioridade fixa**; **0 = maior** (tx 14.29); **FIFO** em prioridades iguais |
| **Atribuir RM** | período menor → **número de prioridade menor** (T1 = 1, T2 = 2, T3 = 3) |
| Prioridade dinâmica (EDF) | **não é nativo**; dá para simular mudando prioridades com `tx_thread_priority_change` 🧩 |
| Time-slice | `time_slice` na criação; alterna threads de **mesma prioridade** (cenário a do Lab 6) |
| Sem preempção | `preempt_threshold` = **a maior prioridade das tarefas** (no Lab 6, **1**) em todas elas: ninguém preempta ninguém. **Não use 0**: a System Timer Thread do ThreadX tem prioridade 0 e travaria (Lab 6, cenário b) |
| **Herança** | `tx_mutex_create(&m, "m", TX_INHERIT)` = **PIP** (tx 14.32, 14.54-14.55) |
| Sem herança | `TX_NO_INHERIT` |
| Teto (ICPP) | não nativo; o **preempt threshold** da thread pode funcionar como um teto (a thread só é preemptada por quem tem prioridade melhor que o threshold) 🧩 |
| Dono do mutex | só **thread** (não ISR nem timer) |
| Tick | período do **SysTick** (`TX_TIMER_TICKS_PER_SECOND`); resolução dos prazos e do `time_slice` |

**Tarefa periódica no ThreadX.** Duas formas:

```c
/* (1) com tx_thread_sleep: o período REAL fica C + sleep (deriva). Não é a recomendada. */
while (1) { trabalho(); tx_thread_sleep(PERIODO); }

/* (2) timer periódico libera um semáforo; a thread espera o semáforo (usada no Lab 6). */
/* timer (período T) -> função de expiração -> tx_semaphore_put(&sem)  */
while (1) { tx_semaphore_get(&sem, TX_WAIT_FOREVER); trabalho(); }
```

A forma (2) mantém o período fixo, e se o job atrasar o semáforo guarda a liberação pendente (**um prazo perdido não faz o período derivar**). Veja [Resumo P2 §8.6](Resumo_P2.md#s8) e [A6 do gabarito Q1](Gabarito_Prova2022_Q1.md#a6).

---

<a id="e9"></a>
## 9. Exemplo com recursos (cenários d e e do Lab 6)

T1 (C = 0,3, T = 1) e T3 (C = 0,8, T = 4) compartilham um mutex; T3 pega no início do job e solta na **metade** do tempo de execução, então a **seção crítica de T3 dura 0,4 s**. T2 não usa o mutex.

**Sem herança (cenário d):**

```
T3 pega o mutex. T1 é liberada, preempta e pede o mutex → bloqueia.
T3 volta para terminar a seção crítica (0,4 s).
T2 é liberada. T2 > T3, então T2 preempta T3 (0,5 s) → T1 espera T3 e T2.
Pior caso: R1 = C1 + (seção de T3) + (um job de T2) = 0,3 + 0,4 + 0,5 = 1,2 s  > D1 = 1 s  → PERDE O PRAZO.
```

Medido no Lab 6: **R1 = 1,10 s**, T1 perde o prazo (11 vezes em ~128 s).

**Com herança (cenário e):**

```
T3 herda a prioridade de T1 enquanto T1 espera. T2 NÃO consegue preemptar T3.
Bloqueio de T1 ≤ seção crítica de T3: B1 = 0,4 s
R1 = C1 + B1 = 0,3 + 0,4 = 0,7 s  ≤ D1 = 1 s  ✓
```

Medido: **R1 = 0,60 s**, sem perdas (o valor medido fica abaixo do limite de 0,7 s porque T3 já podia ter avançado dentro da seção crítica). **Custo:** T2 passou de **0,85 s** para **1,35 s** de resposta, pois T3 (herdando prioridade alta) passou na frente dele.

**Lição:** a herança **limita** o bloqueio de T1 à seção crítica de T3 e tira o efeito de T2, **mas atrasa as tarefas que não usam o mutex**.

---

<a id="e10"></a>
## 10. Exercícios resolvidos

### Ex. 1 – RM: teste e análise de resposta

T1 (C = 1, T = 4), T2 (C = 2, T = 6), T3 (C = 3, T = 12); D = T. Verifique por RM e por EDF.

**U** = 1/4 + 2/6 + 3/12 = 0,25 + 0,333 + 0,25 = **0,833**.
- **RM, teste de utilização:** limite (n = 3) = 0,780 → 0,833 > 0,780 → **não conclui**.
- **RM, resposta** (prioridade T1 > T2 > T3):
  - R1 = **1** ≤ 4 ✓.
  - R2: R⁰ = 2; R¹ = 2 + ⌈2/4⌉·1 = 3; R² = 2 + ⌈3/4⌉·1 = 3 → **3** ≤ 6 ✓.
  - R3: R⁰ = 3; R¹ = 3 + ⌈3/4⌉·1 + ⌈3/6⌉·2 = 6; R² = 3 + ⌈6/4⌉·1 + ⌈6/6⌉·2 = 3 + 2 + 2 = 7; R³ = 3 + ⌈7/4⌉·1 + ⌈7/6⌉·2 = 3 + 2 + 4 = 9; R⁴ = 3 + ⌈9/4⌉·1 + ⌈9/6⌉·2 = 3 + 3 + 4 = 10; R⁵ = 3 + ⌈10/4⌉·1 + ⌈10/6⌉·2 = 3 + 3 + 4 = 10 → **10** ≤ 12 ✓.
  - **Escalonável por RM.**
- **EDF:** U = 0,833 ≤ 1 → **escalonável**.

### Ex. 2 – Teste de utilização: quando o RM falha de verdade

T1 (C = 2, T = 5), T2 (C = 4, T = 7); D = T.
- U = 0,4 + 0,571 = **0,971**; limite (n = 2) = 0,828 → não conclui.
- RM, resposta: R1 = 2 ≤ 5 ✓; R2: R⁰ = 4; R¹ = 4 + ⌈4/5⌉·2 = 6; R² = 4 + ⌈6/5⌉·2 = 8 > 7 → **perde o prazo**. **Não escalonável por RM.**
- EDF: U = 0,971 ≤ 1 → **escalonável por EDF**.
- Moral: acima do limite do RM, o **EDF ainda funciona** (EDF é mais eficiente em CPU).

### Ex. 3 – Bloqueio e herança

T1 (C = 2, T = 8), T2 (C = 3, T = 12), T3 (C = 5, T = 20); prioridade RM T1 > T2 > T3. T1 e T3 usam um mutex. T3 mantém o mutex por **2** unidades de tempo (T1 usa por 1).

**Com herança (PIP):** B1 = seção crítica de T3 = 2; B2 = 2 (T3 herda e atrasa T2 também, se T3 estiver com mutex quando T2 chegar; por segurança usa-se o pior caso).
- R1 = C1 + B1 = 2 + 2 = **4** ≤ 8 ✓.
- R2 = C2 + B2 + ⌈R2/8⌉·2 → R⁰ = 3; R¹ = 3 + 2 + ⌈3/8⌉·2 = 7; R² = 3 + 2 + ⌈7/8⌉·2 = 7 → **7** ≤ 12 ✓.

**Sem herança:** o bloqueio de T1 não tem limite pelo protocolo (T2 pode preemptar T3 várias vezes dentro da seção). Aqui: 2 + (job de T2 = 3) → B1 = 5, e R1 = 2 + 5 = **7** ≤ 8 ainda passa, mas **sem garantia** se T2 tiver C maior ou houver mais tarefas médias.

### Ex. 4 – Conceitual

**(a) Qual a diferença entre RM e EDF quanto à prioridade?** RM: fixa, pelo período. EDF: dinâmica, pelo prazo absoluto mais próximo.
**(b) Por que a herança de prioridade não evita todo deadlock?** Porque ela só ajusta prioridades; se A segura M1 e pede M2 e B segura M2 e pede M1, continuam esperando um ao outro. Só PCP/ICPP, ou uma ordem de aquisição, evitam.
**(c) Por que um semáforo não pode implementar herança?** Não tem dono; sem saber quem segura, não há a quem passar a prioridade.

---

<a id="e11"></a>
## 11. Fórmulas e tabelas de revisão rápida

| O quê | Fórmula |
|---|---|
| Utilização | `U_i = C_i / T_i`, `U = Σ U_i` (U > 1 impossível) |
| Limite RM | `U ≤ n(2^(1/n) − 1)` (n = 3 → 0,780; n → ∞ → 0,693) |
| Limite hiperbólico | `Π (U_i + 1) ≤ 2` |
| Resposta (RM/DM) | `R_i = C_i + Σ_{j∈hp(i)} ⌈R_i/T_j⌉·C_j`, exige `R_i ≤ D_i` |
| Resposta com bloqueio | `R_i = C_i + B_i + Σ ⌈R_i/T_j⌉·C_j` |
| RM com bloqueio | `Σ_{j≤i} C_j/T_j + B_i/T_i ≤ i(2^(1/i) − 1)` |
| EDF (D = T) | `U ≤ 1` |
| Laxity | `prazo − agora − trabalho restante` |

| Pergunta | Resposta curta |
|---|---|
| Prioridade do RM? | menor período = maior prioridade |
| Prioridade do EDF? | prazo absoluto mais próximo |
| RM é ótimo? | entre os de **prioridade fixa** (D = T) |
| EDF é ótimo? | entre **todos**, num processador com preempção |
| Inversão de prioridade | H espera M porque L (com o mutex) foi preemptada por M |
| Herança de prioridade | dona herda a prioridade de quem espera |
| Teto do recurso | maior prioridade de quem usa o recurso |
| PCP e ICPP evitam deadlock? | **sim** (PIP, não) |
| Quantas vezes bloqueia com PCP? | no máximo **uma** |

---

<a id="e12"></a>
## 12. Autoteste (responda antes de ler)

1. **O que é o instante crítico?** Quando uma tarefa é liberada junto com todas as de prioridade maior; é o pior caso de resposta.
2. **U = 0,85 com 3 tarefas e prioridades RM. Dá para garantir pelo teste de utilização?** Não: limite 0,780 < 0,85. É preciso a análise de resposta (que pode aprovar).
3. **U = 1,05 é escalonável?** Não, por nenhum algoritmo (U > 1).
4. **EDF garante sucesso se U = 0,95 e D = T?** Sim (U ≤ 1).
5. **O que o RM faz com prazo ≠ período?** Pode falhar: use **DM** (prioridade pelo prazo).
6. **O que a inversão de prioridade tem de grave?** O bloqueio da alta é **ilimitado** (qualquer tarefa média pode estender).
7. **PIP ou PCP: qual limita o bloqueio a uma vez?** O PCP (e o ICPP).
8. **O que o ThreadX oferece contra inversão?** O mutex com `TX_INHERIT` (herança de prioridade).
9. **Por que `tx_thread_sleep(T)` no fim do job não dá período T?** Porque soma o tempo de execução: o período vira C + T.
10. **Qual a vantagem do ICPP sobre o PIP?** Evita deadlock e bloqueio em cadeia, e é mais simples de implementar; custa subir a prioridade sem necessidade.

---

<a id="e13"></a>
## 13. Para ir além

Material usado como base (fora dos slides):
- C. L. Liu e J. W. Layland, *Scheduling Algorithms for Multiprogramming in a Hard-Real-Time Environment*, JACM, 1973 (RM, EDF, limite de utilização).
- L. Sha, R. Rajkumar e J. Lehoczky, *Priority Inheritance Protocols: An Approach to Real-Time Synchronization*, IEEE Trans. Computers, 1990 (PIP e PCP).
- M. Joseph e P. Pandya, 1986, e N. Audsley et al., 1993 (análise do tempo de resposta).
- G. Buttazzo, *Hard Real-Time Computing Systems*, Springer (livro-texto completo).
- A. Burns e A. Wellings, *Real-Time Systems and Programming Languages*.
- Documentação do ThreadX: serviços `tx_mutex_create` (herança), `tx_thread_priority_change` e `tx_thread_create` (preempt threshold).

Confirme com o professor quais tópicos entram na P2; os mais prováveis, dado o Lab 6, são: **prioridades e preempção**, **inversão de prioridade e herança** (seção 9), e a **análise de resposta/RM** (seção 3).
