# ELEW32 – Sistemas Embarcados – Resumo da P2

Prof. Douglas Renaux (UTFPR). Cobre os três arquivos de `Slides`: `13_concurrency.pdf`, `13_mutual_exclusion.pdf` e `14_t threadx_rtos.pdf`. Para interrupções, SysTick, assembly e máquinas de estados (que a P2 reaproveita), veja o [Resumo da P1](../P1/Resumo_P1.md).

## Como ler as referências

| Marca | Significa |
|---|---|
| **(conc 13.11)** | `13_concurrency.pdf`, slide com rodapé "Page 13. 11" |
| **(excl 13.28)** | `13_mutual_exclusion.pdf`, slide "Page 13. 28" (a numeração continua a de `conc`: o arquivo de exclusão mútua vai de 13.17 a 13.51) |
| **(tx 14.28)** | `14_t threadx_rtos.pdf`, slide "Page 14. 28" |
| **🧩 Complemento** | Conteúdo que o slide só cita ou mostra em imagem e que expliquei com conhecimento padrão (ThreadX/ARM). Confira com suas anotações de aula. |

Conferi as figuras e os trechos de código dos slides que são imagem (algoritmo de Peterson, diagramas de comunicação, estados do ThreadX, filas, timer, eventos). Não há na pasta slides sobre **escalonamento** (RM, EDF) nem **inversão de prioridade em detalhe**, apesar de aparecerem no índice da disciplina. O que existe sobre esses temas está na [§9](#s9).

## Índice

1. [Por que concorrência (tarefas, threads, processos)](#s1)
2. [Troca de contexto, preempção e prioridade](#s2)
3. [Recursos compartilhados e exclusão mútua](#s3)
4. [Soluções para a exclusão mútua](#s4)
5. [Comunicação por mensagens](#s5)
6. [RTOS: conceitos, estados, CMSIS e planejamento (UML)](#s6)
7. [ThreadX: visão geral, estrutura e inicialização](#s7)
8. [ThreadX: componentes (thread, timer, semáforo, mutex, eventos, filas, memória)](#s8)
9. [🧩 Receitas, armadilhas e erros comuns](#s9)
10. [Tabelas de revisão rápida](#s10)

---

<a id="s1"></a>
## 1. Por que concorrência (conc 13.2-13.10)

**Motivação.** Imagine uma empresa de uma pessoa só: se você escrevesse as tarefas dela como um único roteiro, ele seria cheio de afazeres intercalados e muito complexo. O mesmo ocorre num sistema embarcado (conc 13.3): 3 portas seriais a 115 kbps (1 caractere a cada ~87 µs), USB que exige processamento a cada 125 µs, tela de toque + LCD, e atividades de software com períodos diferentes (A1 a cada 2 ms, A2 a cada 7 ms, A3 a cada 500 µs, A4 a cada 100 ms). Um único código sequencial para tudo seria muito difícil, ainda mais com vários intercalamentos possíveis.

**Solução.** Dividir o programa em **tarefas (tasks)**, cada uma responsável por **uma** atividade. As tarefas executam concorrentemente e **cooperam** entre si ("é trabalho em equipe", conc 13.4).

**Processador virtual (conc 13.5-13.6).** Cada tarefa executa em um "processador virtual" (VP1…VPn). O desempenho somado é aproximadamente o do processador real, porque os VPs **compartilham** processador, memória e periféricos. Quem gerencia esse compartilhamento é o **sistema operacional embarcado (RTOS)**, que fica entre os VPs e o hardware.

### 1.1 Memória de um programa sequencial (conc 13.7)

Flash: `.text` (código), `.const`. RAM: `.data`, `.bss` (dados), **heap**, **stack**. A CPU tem os registradores.

### 1.2 Multithreading (conc 13.8-13.10)

- **Thread** = segmento de programa que executa concorrentemente a outros. Cada thread tem **seu próprio PC, seu próprio conjunto de registradores e sua própria pilha**, e **compartilha** as demais regiões de memória (código, `.data`, `.bss`, heap) com as outras threads.
- Em MCUs, **cada tarefa (conceito abstrato) é implementada por uma thread**.
- **Uso exclusivo** de cada thread: pilha + cópia dos registradores. **Compartilhado:** código, dados globais, heap. O compartilhamento é eficiente, mas **não oferece proteção** entre threads (uma pode corromper o dado da outra).

| | Processo | Thread |
|---|---|---|
| Hardware | Processador **com MMU** | Processador **sem MMU** (típico em Cortex-M) |
| Espaço de endereços | **exclusivo** por tarefa | todos compartilham a memória |
| Observação | pode hospedar várias threads (processos mono ou multithread) | |

**Tarefa** é um conceito lógico: pode ser implementada por um processo ou por uma thread.

---

<a id="s2"></a>
## 2. Troca de contexto, preempção e prioridade (conc 13.11-13.13)

### 2.1 Troca de contexto (*context switch*)

Salvar o estado do processador de uma thread e restaurar o de outra:
1. A tarefa A está executando.
2. **Todos os registradores da CPU são salvos na pilha da tarefa A.**
3. O RTOS executa e **escolhe outra tarefa (B)** conforme a **política de escalonamento**.
4. O estado de B é **restaurado da pilha de B** para os registradores; a execução prossegue no código e na pilha de B.

No Cortex-M com ThreadX, quem faz isso é a exceção **PendSV** ([§7.6](#s7)).

### 2.2 RTOS preemptivo × não preemptivo

| | Preemptivo | Não preemptivo (cooperativo) |
|---|---|---|
| Controle do processador | O RTOS retoma o controle **a qualquer momento** (ex.: thread de **maior prioridade** fica pronta) | O RTOS só retoma quando a thread **libera voluntariamente** |
| Troca | forçada pelo RTOS | só em chamadas de cessão (*yield*), bloqueio ou fim |

### 2.3 Prioridade de tarefa

Cada tarefa tem um nível de prioridade, normalmente **alterável em execução**. Quando uma tarefa de prioridade maior que a em execução fica pronta, o escalonador **preemptivo por prioridade** interrompe a em execução e troca para a de prioridade maior. Quando esta libera o processador, a preemptada **retoma** de onde parou (figura conc 13.13, do CMSIS-RTOS).

### 2.4 Cuidados (conc 13.14-13.16)

- Se as tarefas são **independentes**, basta alocar o processador (escalonamento).
- Se **compartilham recursos** (regiões de memória ou periféricos), é preciso garantir **acesso exclusivo** e evitar **deadlocks** e **inversão de prioridade**.
- Em recursos compartilhados: há **restrições ao acesso concorrente**; a **ordem** dos acessos é crítica e não deve causar erros; a alocação deve considerar a troca de tarefas para **não bloquear o recurso por causa de tarefa suspensa**.
- **Programas concorrentes são difíceis de depurar.**

**Os quatro problemas a tratar em ambiente multitarefa (conc 13.16):**
1. **Comunicação** entre tarefas
2. **Sincronização** entre tarefas
3. **Compartilhamento de recursos e exclusão mútua**
4. **Escalonamento**

---

<a id="s3"></a>
## 3. Recursos compartilhados e exclusão mútua (excl 13.17-13.28)

### 3.1 Conceitos básicos

- **Recurso compartilhado:** objeto de dados, dispositivo ou (generalizando) **região de endereçamento** compartilhada entre tarefas. Geralmente tem **restrições ao acesso concorrente**, daí o requisito de **exclusão mútua** (excl 13.20).
- **Exclusão mútua:** um recurso com essa exigência, compartilhado entre N tarefas, só pode ser usado por **uma tarefa por vez**. Se A está usando e B quer usar, **B espera** A terminar (excl 13.22).
- **Seção crítica (SC, *critical section*):** o trecho de código da tarefa **onde o recurso compartilhado é acessado**. Cada SC está associada a um recurso. Exemplo do slide: recurso = lista circular duplamente encadeada; SCs = código das duas tarefas que a acessam (excl 13.23).

### 3.2 Exemplo de acesso concorrente incorreto (excl 13.24)

Salão com 3 acessos, cada um com sensor e tarefa (Task1, Task2, Task3), que atualizam o **contador de pessoas no salão** (recurso compartilhado). Incrementar o contador em assembly são **3 instruções: `LDR`, `ADD`, `STR`**. Se duas tarefas intercalam essas instruções, **uma atualização se perde**:

| Passo | Tarefa 1 | Tarefa 2 | Contador (memória) |
|---|---|---|---|
| 0 | | | 5 |
| 1 | `LDR R0,[cont]` (R0=5) | | 5 |
| 2 | *(troca de contexto)* | `LDR R0,[cont]` (R0=5) | 5 |
| 3 | | `ADD R0,R0,#1` (6) | 5 |
| 4 | | `STR R0,[cont]` | **6** |
| 5 | `ADD R0,R0,#1` (R0=6) | | 6 |
| 6 | `STR R0,[cont]` | | **6** (devia ser 7) |

Isso é uma **condição de corrida (*race condition*)**: o resultado depende do **tempo relativo** entre as tarefas. A proteção é fazer a sequência `LDR/ADD/STR` ser uma **seção crítica** (ou usar uma operação **atômica**).

### 3.3 Requisitos do problema da exclusão mútua (excl 13.25)

1. Quando uma tarefa executa uma SC, **nenhuma outra** pode estar em SC acessando esses recursos.
2. Uma tarefa **não deve ser atrasada** para entrar na SC se **nenhuma outra** está usando o recurso.
3. O tempo de execução de uma SC é **finito**.
4. **Nenhuma suposição** sobre a velocidade relativa ou a frequência de acesso ao recurso.
5. A solução deve evitar: **deadlock**, **livelock**, **starvation**, e **não pode impor ordem** de acesso (ex.: "revezar" – *taking turns*).

### 3.4 Formalização (Lamport, excl 13.26-13.27)

1. Uma tarefa *i* é uma sequência alternada de seções **não críticas (NCS)** e **críticas (CS)**, todas terminantes.
2. Para quaisquer tarefas distintas *i* e *j*, **nenhum par de CS é concorrente**.
3. O tempo de uma CS é finito.
4. **Não há deadlock**: situação em que uma ou mais tarefas "tentam entrar", mas **nenhuma entra**.
5. **Toda tarefa que tenta entrar na CS deve eventualmente conseguir** (requisito de **justiça**, *fairness*). A condição mais forte é a **fila FCFS** (primeiro a chegar, primeiro a ser atendido). Isso também exclui livelock e starvation.
6. Nenhuma suposição sobre a frequência relativa de entrada (como "revezar").

### 3.5 Glossário (excl 13.28) – **decorar**

| Conceito | Significado |
|---|---|
| **Computação concorrente** | Várias tarefas computacionais que interagem executando no mesmo período |
| **Operação atômica** | Sequência **indivisível** de instruções |
| **Seção crítica** | Trecho de código que engloba o acesso a um recurso compartilhado |
| **Exclusão mútua** | Uma tarefa **não** pode estar na sua SC ao mesmo tempo que outra que usa o mesmo recurso |
| **Deadlock** | Conjunto de tarefas **bloqueadas esperando umas pelas outras** |
| **Livelock** | Tarefas **executando** (vivas), mas **sem conseguir fazer trabalho útil** |
| **Starvation** (inanição) | Uma tarefa pronta é **ignorada** pelo escalonador ou pelo controle de acesso ao recurso; é sempre adiada em favor de outras |
| **Race condition** | Várias tarefas leem e escrevem um recurso compartilhado e o **resultado final depende do tempo relativo** entre elas |

Diferença que cai em prova: **deadlock = todas bloqueadas (paradas)**; **livelock = todas ativas, mas sem progresso**; **starvation = uma específica nunca é atendida** enquanto as demais progridem.

---

<a id="s4"></a>
## 4. Soluções para a exclusão mútua (excl 13.29-13.44)

### 4.1 Mapa das soluções (excl 13.29-13.30)

| Solução | Suporte exigido |
|---|---|
| **Desabilitar interrupções** | instrução especial (`CPSID`/`__disable_irq`) |
| **Baseadas em variáveis compartilhadas** | hardware (instruções atômicas) ou **nenhum** (algoritmos de software) |
| **Baseadas em mensagens entre tarefas** | nenhum |

Arquiteturas-alvo (excl 13.30): **processador único**, **multiprocessador de memória compartilhada**, **multiprocessador distribuído (em rede)**.

### 4.2 Desabilitar interrupções (excl 13.31)

Simples e resolve a exclusão mútua, mas:
- **atrasa** o atendimento de interrupções, inclusive das atividades **não relacionadas**;
- **muitos RTOS não permitem** que tarefas desabilitem interrupções (atrapalha o RTOS);
- se a tarefa **travar** com interrupções desabilitadas, **o sistema inteiro trava**;
- só vale para **processador único**.

Em CMSIS: `__disable_irq()` seta PRIMASK; `__enable_irq()` zera ([Resumo P1 §12.4](../P1/Resumo_P1.md#s12)). `BASEPRI` bloqueia só as de baixa prioridade (menos agressivo).

### 4.3 Instruções especiais (excl 13.32-13.36)

Características: são **atômicas** (não interrompíveis) e executam possivelmente um ciclo de **leitura-modificação-escrita na memória sem interrupção**, mesmo em multiprocessador.
- Exemplos: **test-and-set**, **troca (exchange)**, como a **`SWAP` do ARM7TDMI**.
- Valem para **processador único** e **multiprocessador de memória compartilhada**.

**No Cortex-M: `LDREX` / `STREX`** (excl 13.33-13.36) **[Tabela P1, p.4]**:

| Instrução | O que faz |
|---|---|
| `LDREX Rd,[Rn]` | Lê a palavra e **marca (tag)** o endereço como acesso exclusivo |
| `STREX Rd,Rm,[Rn]` | Tenta gravar `Rm` em `[Rn]`. **`Rd = 0` se conseguiu, `Rd = 1` se falhou** (o `Rd` do `STREX` é o **status**, não o dado) |
| `CLREX` | Limpa a marca de acesso exclusivo local |

Uso do slide (implementar um semáforo com os primitivos de sincronização):
1. `LDREX` para ler do endereço do semáforo e **verificar se está livre**.
2. Se livre, `STREX` para escrever o valor de "tomado".
3. Se o bit de status devolvido pelo `STREX` indica **sucesso**, a SW tomou o semáforo. Se **falhou**, outro processo pode ter tomado depois do passo 1: **tentar de novo**.

**Monitor de acesso exclusivo (local):** máquina de dois estados, **Open Access** e **Exclusive Access**. `LDREX` leva a *Exclusive*. O processador **remove a marca** quando: executa `CLREX`; executa um **Store-Exclusive** (**dê certo ou não**); ou ocorre uma **exceção**. Por isso o `STREX` falha se uma interrupção/troca de tarefa acontecer entre o `LDREX` e o `STREX`: é assim que o Cortex-M resolve conflito de semáforo entre threads. Em multiprocessador há também um **monitor global**.

🧩 Exemplo de trava (*spinlock*) com LDREX/STREX (R0 = endereço da trava; 0 = livre, 1 = tomada):
```
lock    MOV     R1, #1
retry   LDREX   R2, [R0]          ; lê e marca
        CMP     R2, #0
        BNE     retry            ; já tomada: tenta de novo (espera ocupada)
        STREX   R3, R1, [R0]     ; tenta tomar; R3 = 0 sucesso, 1 falha
        CMP     R3, #0
        BNE     retry            ; perdeu a corrida (ou houve exceção): repete
        BX      LR               ; trava obtida
unlock  MOV     R1, #0
        STR     R1, [R0]         ; libera
        BX      LR
```

### 4.4 Semáforo / Mutex (excl 13.39)

Padrão do slide para duas tarefas, A e B, iguais:
```c
Inicializacao();
while (1) {
    NonCriticalRegion();
    if ( MutexGet() == SUCESS ) {   // pede acesso
        CriticalRegion();
        MutexPut();                 // libera
    }
}
```
Estrutura: **NCS → entrada (get) → CS → saída (put) → repete**. A entrada bloqueia se outra tarefa estiver na CS. O ThreadX implementa isso com `tx_mutex_get/put` ([§8.5](#s8)).

### 4.5 Soluções por software, sem hardware especial (excl 13.40-13.43)

Todas usam **dados compartilhados**; valem para processador único e multiprocessador de memória compartilhada. O slide mostra quatro tentativas que **falham** e o algoritmo de Peterson que **funciona** (livro de Stallings). Duas tarefas, P0 e P1.

| Tentativa | Idea | Resultado | Por quê |
|---|---|---|---|
| **1ª: variável `turn`** | `while (turn != 0) ;` SC; `turn = 1;` (P1 simétrico) | **Alternância forçada** | Cada tarefa só entra na sua vez: viola o requisito "não impor ordem". Se uma tarefa não precisa mais entrar, **trava a outra**. |
| **2ª: `flag[i]`** | `while (flag[1]) ;` `flag[0]=true;` SC; `flag[0]=false;` | **Sem exclusão mútua** | As duas testam o flag do outro **antes** de levantar o próprio; ambas veem `false` e entram juntas. |
| **3ª: levantar a flag primeiro** | `flag[0]=true;` `while (flag[1]) ;` SC; `flag[0]=false;` | **Deadlock** | As duas levantam a flag antes de testar; as duas veem `true` e **esperam para sempre**. |
| **4ª: recuar (*back-off*)** | `flag[0]=true;` `while (flag[1]) { flag[0]=false; delay; flag[0]=true; }` | **Possível livelock** | Se as tarefas ficam **sincronizadas** nos recuos, ambas ficam alternando as flags sem entrar. |

**Algoritmo de Peterson** (excl 13.43) – funciona para 2 tarefas:
```c
boolean flag[2];
int turn;

void P0() {
    while (true) {
        flag[0] = true;                 // quero entrar
        turn = 1;                       // cedo a vez ao outro
        while (flag[1] && turn == 1) ;  // espero só se o outro também quer E é a vez dele
        /* seção crítica */
        flag[0] = false;                // saí
        /* resto */
    }
}
void P1() {                             // simétrico
    while (true) {
        flag[1] = true;
        turn = 0;
        while (flag[0] && turn == 0) ;
        /* seção crítica */
        flag[1] = false;
    }
}
void main() { flag[0] = false; flag[1] = false; parbegin(P0, P1); }
```
Por que funciona: `flag` mostra o **interesse**, `turn` **desempata** (quem escreveu `turn` por último cede). Se só uma quer entrar, o `flag` do outro é `false` e ela entra direto (não é atrasada sem necessidade). Se as duas querem, **uma** das condições `turn == x` é falsa e **só uma passa**. Sem deadlock, sem livelock, sem alternância forçada.

🧩 Limites: só para **2 tarefas** (há generalizações para N) e assume que as escritas na memória ocorrem **na ordem do programa**; em processadores modernos exige **barreiras de memória**. Em Cortex-M com RTOS, usa-se o mutex do RTOS.

### 4.6 Monitor (excl 13.44)

Conceito de **encapsulamento** (OO): **todas as rotinas que acessam um recurso compartilhado ficam num único módulo de software**. O acesso a essas rotinas é protegido, por exemplo, por **semáforos**. Diagrama UML do slide: classe `M:Monitor` com `s1: semaphore` (que tem uma fila de tarefas esperando), `v1` (variável pública compartilhada), `q1` (fila de tarefas para acessar `v1`), `pv1` (privada), `Init`, funções privadas `prF` e operações públicas `Oper1`, `Oper2` com **MEx (Mutual EXclusion)**.

---

<a id="s5"></a>
## 5. Comunicação por mensagens (excl 13.45-13.51)

As soluções anteriores exigem **variáveis compartilhadas**, logo **não servem para arquitetura distribuída**. As baseadas em mensagens servem para **as três arquiteturas**.

| Tipo | Como funciona (diagramas excl 13.46-13.48) | Estados |
|---|---|---|
| **Assíncrona** | O remetente **não espera**. A mensagem vai para uma fila (*put*) e o receptor pega quando quiser (*Receive*). | O receptor pode ficar **Blocked on Receive** se a fila estiver vazia. O remetente segue (*Running*). |
| **Síncrona** | A troca só ocorre quando **as duas tarefas querem** (encontro). Os dados podem ir **direto** do remetente ao receptor. | Quem chega primeiro fica **Blocked on Receive** ou **Blocked on Send** até a outra chegar. |
| **Síncrona com resposta** (*Send-Receive-Reply*) | `Send` e `Receive` são **bloqueantes**. O remetente fica **bloqueado** até o servidor responder (*Reply*). | Remetente: *Blocked on Send/Reply*. |

**Mensagens como sequencialização (excl 13.49):** várias tarefas remetentes (Task 1 … Task n) mandam para a **caixa de entrada** de uma **tarefa receptora**. As mensagens são processadas **uma por vez**, o que serializa os acessos: não precisa de variável compartilhada nem de mutex.

**Modelo cliente-servidor (excl 13.50):** evolução do monitor. O **servidor** (tarefa receptora) **encapsula o recurso compartilhado**; as tarefas que querem usá-lo **enviam mensagem**; o servidor **responde com o resultado** da operação.

**Primitivos de sincronização, visão geral (excl 13.51, Stallings):**

| Primitivo | Definição curta |
|---|---|
| **Semáforo** (contador/geral) | Inteiro usado para sinalização; só 3 operações (todas atômicas): inicializar, decrementar (pode **bloquear**), incrementar (pode **desbloquear**) |
| **Semáforo binário** | Só assume 0 e 1 |
| **Mutex** | Parecido com o binário, mas o processo que **trava (valor 0)** deve ser o que **destrava (valor 1)** |
| **Variável de condição** | Bloqueia um processo/thread até que uma condição seja verdadeira |
| **Monitor** | Construção que encapsula variáveis e procedimentos; **só um processo ativo por vez** |
| **Event flags** | Palavra de memória usada para sinalizar; cada **bit** = um evento; espera-se por **um** ou **vários** bits (AND/OR) |
| **Mailboxes/Mensagens** | Meio de trocar informação e sincronizar |
| **Spinlock** | Exclusão mútua em que o processo faz **espera ocupada** num laço lendo uma variável de trava |

---

<a id="s6"></a>
## 6. RTOS: conceitos, estados, CMSIS e planejamento (tx 14.2-14.8)

### 6.1 O que é um RTOS (tx 14.2)

Camada de software **entre o hardware e a aplicação** que permite implementar tarefas concorrentes por **multithreading**. Gerencia o hardware compartilhando recursos entre os "processadores virtuais" (VP1…VPn), de modo que cada thread tem a **ilusão** de ter processador e pilha próprios, enquanto compartilha dados globais, heap, código e periféricos. Compartilha o processador por **troca de contexto** e oferece: **temporização, comunicação e sincronização entre threads, e gerenciamento de threads** (e memória).

Visões da execução (tx 14.3-14.4): em escala de **segundos** parece que todas executam **em paralelo**; em escala de **milissegundos** vê-se o RTOS **alternando** a CPU entre elas.

### 6.2 Estados de uma tarefa (tx 14.5)

| Estado | Significado |
|---|---|
| **Ready** (pronta) | Quer usar o processador e é candidata a ser escalonada |
| **Running** (executando) | Está usando o processador |
| **Waiting** (esperando/bloqueada) | Execução bloqueada por **tempo, sincronização ou comunicação** |

Transições do diagrama (statechart do slide): `Create` leva a Ready; `Scheduling` leva de Ready a Running; `Yield` ou preempção volta de Running a Ready; `Delay` ou espera por `Time/Signal/Message/Mail/Release` leva a Waiting; o evento leva de Waiting a Ready; `Terminate` leva a Inactive. No ThreadX os nomes são outros ([§7.4](#s7)).

### 6.3 CMSIS (tx 14.6-14.7)

*Cortex Microcontroller Software Interface Standard*: v1.0 (2008, API de drivers), v2.0 (biblioteca DSP), v3.0 (2012, **API RTOS** e DAP), v4.0 (2014, CMSIS-Driver e CMSIS-Pack), v5.0 (2016, **CMSIS-RTOS v2**); em março de 2020 estava na 5.6. O **CMSIS-RTOS** é uma API padrão de RTOS, a "camada de adaptação do RTOS" do modelo de 9 camadas ([Resumo P1 §3](../P1/Resumo_P1.md#s3)). A documentação e o código estão no GitHub.

### 6.4 Planejando uma aplicação multithread (UML, tx 14.8 e 14.31/14.41)

O slide mostra um diagrama de classes de uma aplicação (ex.: jogo com joystick, `PacMan`, `Fantasma`, `Labirinto`) com **elementos do RTOS desenhados com estereótipos/símbolos**. Os símbolos da disciplina (tx 14.31 e 14.41):

| Componente ThreadX | Símbolo UML |
|---|---|
| **Thread** | retângulo com estereótipo `«thread»` + nome (ex.: `ThreadName`) |
| **Memory block** (byte pool, block pool) | `«memory block»` |
| **Counting semaphore** | círculo vermelho + `«counting semaphore»` |
| **Mutex** | cadeado + `«mutex»` |
| **Queue** | retângulo com divisórias (fila) |
| **Event flag** | bandeira |
| **Timer** | relógio |

Também aparecem: `«ISR»`, `«HW»` (ex.: `SysTick`), `«GPIO»`, `«global var»` (tx 14.52). Associações têm multiplicidade (1, 2, 4…) e setas com rótulos (`put`, `get`, `call`, `wake`, `increment`, `irq`). **Use estes símbolos nos diagramas da prova.**

---

<a id="s7"></a>
## 7. ThreadX: visão geral, estrutura e inicialização (tx 14.15-14.28, 14.63-14.67)

### 7.1 O que é (tx 14.16-14.19)

RTOS da **Express Logic (1997)**, adquirida pela **Microsoft em 2019** (abril, Azure RTOS), disponível no GitHub. Parte da família **Azure RTOS**: ThreadX, ThreadX SMP, NetX, USBX, FileX, GUIX, NetX Secure, LevelX.

Funcionalidade do kernel (figura tx 14.17): **API do ThreadX**; serviços: **memory pools (byte e block)**, **event flags**, **message queues**, **mutexes**, **semáforos**, **application timers**, **thread services** e núcleo (**core scheduler**); agrupados em *Inter-thread Communication*, *Thread Synchronization*, *Memory Management*, *Timer Services*, *Thread Management*.

**Desempenho** típico a 200 MHz (tx 14.19): suspender/retomar thread 0,6 µs; send/receive de fila 0,3 µs; get/put de semáforo 0,2 µs; **troca de contexto 0,4 µs**; resposta a interrupção 0,0 a 0,6 µs.

### 7.2 Tipos de dado e arquivos (tx 14.20-14.22)

| Tipo ThreadX | Tamanho |
|---|---|
| `INT` / `UINT` | 32 bits |
| `LONG` / `ULONG` | 32 bits |
| `VOID` | – |
| `CHAR` / `UCHAR` | 8 bits |
| `SHORT` / `USHORT` | 16 bits |

(definidos em `tx_port.h` com `typedef`). Arquivos: **`tx_api.h`** (equates, estruturas de dados e protótipos de serviços; deve ser incluído por todo arquivo que use ThreadX), **`tx_port.h`** (definições específicas do compilador/alvo), `tx_user.h` (configuração do usuário, ex.: `TX_TIMER_TICKS_PER_SECOND`) e **`tx.a`/`tx.lib`** (biblioteca binária). Hierarquia: `tx_user.h` é incluído por `tx_port.h`, que é incluído por `tx_api.h`.

### 7.3 Aplicação mínima (tx 14.23)

**Quatro passos:**
1. Incluir `tx_api.h`.
2. Criar a `main()` padrão do C. Ela deve **chamar `tx_kernel_enter()`** para iniciar o ThreadX. Inicializações que **não** envolvam o ThreadX podem ficar antes.
3. Criar **`tx_application_define()`**: aqui se criam os recursos iniciais do sistema (**threads, filas, memory pools, grupos de event flags, mutexes e semáforos**).
4. Compilar e **linkar com a biblioteca `tx.lib`**; gravar na placa.

```c
#include "tx_api.h"
unsigned long my_thread_counter = 0;
TX_THREAD my_thread;

main() {
    tx_kernel_enter();              /* não retorna: entra no escalonador */
}

void tx_application_define(void *first_unused_memory) {
    tx_thread_create(&my_thread, "My Thread", my_thread_entry, 0x1234,
                     first_unused_memory, 1024, 3, 3, TX_NO_TIME_SLICE, TX_AUTO_START);
}

void my_thread_entry(ULONG thread_input) {
    while (1) {                     /* laço infinito */
        my_thread_counter++;
        tx_thread_sleep(1);         /* dorme 1 tick */
    }
}
```
Nota do slide (tx 14.24-14.25): no e² studio/SSP muitos `.h` do ThreadX são **gerados automaticamente** ("Generate Project Content"). **Editar um `#define` num `.h` gerado não tem efeito**: mude pela aba **Properties** (ex.: *Timer Ticks per Second*), gere o conteúdo de novo (o novo valor vai para `tx_src_user.h`) e recompile. É preciso incluir o código-fonte do ThreadX no projeto (HAL/Common).

### 7.4 Estados de uma thread no ThreadX (tx 14.28)

```c
UINT tx_thread_create(
    TX_THREAD *thread_ptr,           // estrutura de controle (alocada por você)
    CHAR *name_ptr,                  // nome ASCII
    VOID (*entry_function)(ULONG),   // função de entrada da thread
    ULONG entry_input,               // argumento passado à função de entrada
    VOID *stack_start,               // início da pilha
    ULONG stack_size,                // tamanho da pilha em BYTES
    UINT priority,                   // 0 = maior prioridade
    UINT preempt_threshold,          // limiar de preempção
    ULONG time_slice,                // fatia de tempo em ticks (TX_NO_TIME_SLICE)
    UINT auto_start);                // TX_AUTO_START ou TX_DONT_START
```

Diagrama de estados (FIGURE 5 do slide):

| Estado | Como se chega |
|---|---|
| **Ready** | `tx_thread_create` com `TX_AUTO_START` (ou `tx_thread_resume` depois de suspensa). Está pronta para executar. |
| **Suspended** | `TX_DONT_START` na criação, ou serviço que **suspende** a thread (espera por get, sleep, `tx_thread_suspend`...). |
| **Executing** | O **escalonador** (*thread scheduling*) a escolheu. |
| **Completed** | **Retornou** da função de entrada (*return from thread entry function*). |
| **Terminated** | `tx_thread_terminate` (self ou por outra) ou serviço de *terminate*. |

(*Self suspend*/*self terminate* = a própria thread executa o serviço.) Só **uma** thread está *Executing* de cada vez.

### 7.5 Prioridades (tx 14.29)

- `TX_MAX_PRIORITIES` = número de níveis. **0 = maior prioridade.**
- A thread **pronta de maior prioridade** executa primeiro. **Threads de mesma prioridade** são ordenadas **FIFO**.
- **Round-robin cooperativo:** cada thread chama `tx_thread_relinquish()` (*yield*).
- **Time-slicing:** define-se um nº de ticks (por thread, na criação); ao expirar, outras threads **de mesma prioridade** executam.
- **Herança de prioridade:** dentro dos serviços de **mutex** ([§8.5](#s8)).
- 🧩 **Preempt threshold:** valor de prioridade abaixo do qual outras threads **não** podem preemptar esta (limita preempções; se igual à prioridade, não há efeito).

### 7.6 Threads e RTOS na execução (tx 14.63)

- **Threads executam em Thread mode, nível privilegiado.** Prioridade mais alta = 0. Preempção quando uma thread de prioridade maior fica pronta.
- **O ThreadX executa em Handler mode, privilegiado.**
- O ThreadX usa **duas exceções**: **SVC** (chamadas **síncronas**) e **PendSV** (**assíncrona**, usada para a **troca de contexto**).

([Resumo P1 §8 e §11](../P1/Resumo_P1.md#s8): modos Thread/Handler, SVC e PendSV.) O **SysTick** gera o tick do RTOS ([Resumo P1 §13](../P1/Resumo_P1.md#s13)).

### 7.7 Inicialização (tx 14.64-14.67)

Fluxo (figura "Initialization Process"):
1. **Vetor de reset**: tabela de exceções (`cstartup_M.s`).
2. **Ponto de entrada** (`__iar_program_start`): inicializa FPU, `.data`, `.bss`.
3. **`main()`**: inicializações da aplicação (clock, periféricos) e **`tx_kernel_enter()`**.
4. `tx_kernel_enter` chama **`tx_application_define(mem_ptr)`**: **cria as threads e os componentes globais do ThreadX**.
5. **Entra no laço do escalonador** (*thread scheduling loop*): executa as funções de entrada das threads.

No ambiente Synergy parte disso é feita pelo **SSP** (reset vector, init, config). Veja o fluxo completo de reset até `main` em [Resumo P1 §17](../P1/Resumo_P1.md#s17).

---

<a id="s8"></a>
## 8. ThreadX: componentes (tx 14.29-14.62)

### 8.1 Visão geral dos componentes (tx 14.31, 14.41-14.42)

| Componente | Estrutura de controle | Create | Usos principais |
|---|---|---|---|
| **Thread** | `TX_THREAD` | `tx_thread_create` | `tx_thread_sleep`, `tx_thread_relinquish`, `tx_thread_resume` |
| **Queue** | `TX_QUEUE` | `tx_queue_create` | `tx_queue_send`, `tx_queue_receive` (B/NB/TO) |
| **Event flags** | `TX_EVENT_FLAGS_GROUP` | `tx_event_flags_create` | `tx_event_flags_get` (B/NB/TO), `tx_event_flags_set` |
| **Timer** | `TX_TIMER` | `tx_timer_create` | `tx_timer_deactivate`, `tx_timer_change` |
| **Semáforo** | `TX_SEMAPHORE` | `tx_semaphore_create` | `tx_semaphore_get` (B/NB/TO), `tx_semaphore_put` |
| **Mutex** | `TX_MUTEX` | `tx_mutex_create` | `tx_mutex_get` (B/NB/TO), `tx_mutex_put` |
| **Block pool** | `TX_BLOCK_POOL` | `tx_block_pool_create` | `tx_block_allocate` (B/NB/TO), `tx_block_release` |
| **Byte pool** | `TX_BYTE_POOL` | `tx_byte_pool_create` | `tx_byte_allocate` (B/NB/TO), `tx_byte_release` |

**B/NB/TO** = *Blocking / Non-Blocking / Timeout* (opções de espera: `TX_NO_WAIT` = 0, `TX_WAIT_FOREVER` = 0xFFFFFFFF, ou nº de ticks de 1 a 0xFFFFFFFE).

### 8.2 Uso dos serviços (tx 14.34-14.36)

Argumentos dos serviços:
- **Estruturas de controle:** tipos predefinidos do ThreadX; **você deve aloca-las previamente** em regiões de memória de dados e passá-las **por ponteiro**.
- **Nomes ASCII:** uma `string` com o nome do elemento.
- **Opções de configuração:** escolhidas entre elementos de uma enumeração/`#define`.
- **Saídas:** normalmente ponteiros para áreas **já alocadas** onde o resultado será gravado.

**Erro clássico (slide tx 14.35 com dois "X" vermelhos):**
```c
void thread_init(void) {                        /* ERRADO 1: ponteiro não inicializado */
    TX_EVENT_FLAGS_GROUP *ptr_event_flags0;     /*   aponta para lixo */
    CHAR *name;
    tx_event_flags_create(ptr_event_flags0, name);
}
void thread_init(void) {                        /* ERRADO 2: variável LOCAL (automática) */
    TX_EVENT_FLAGS_GROUP event_flags0;          /*   vive na pilha e some quando a função retorna */
    CHAR name[] = "Test1";
    tx_event_flags_create(&event_flags0, name);
}
```
A estrutura de controle precisa **existir enquanto o componente existir**: o slide mostra o escopo e o tempo de vida (tx 14.36): variável **global/estática** (`.bss`/`.data`, vive "para sempre"), variável **local** (pilha, vive só na função), **alocação dinâmica** (heap com `new/malloc`, ou ThreadX com byte pool: vive de `alloc` até `free`).

### 8.3 Onde guardar as estruturas de controle (tx 14.39-14.40)

| Onde | Quando |
|---|---|
| **RAM global (`.bss`)** | elementos (threads, filas, eventos...) cuja vida é **todo o tempo de execução** (do power-on ao power-off) |
| **Heap** | igual, **desde que `malloc/new` execute antes de `tx_kernel_enter()`** |
| **Regiões alocadas por `byte_pool`** | se a alocação ocorre **depois de `tx_kernel_enter()`** ou se aloca e libera durante a execução |

**Ciclo de uso (tx 14.40):** (1) alocar as estruturas num lugar adequado (tipicamente global); (2) **inicializar com `create`**; (3) usar as funções principais (ex.: event flags `set` e `get`); (4) usar funções secundárias (desempenho, informação); (5) `delete` (raramente).

### 8.4 Informações importantes (tx 14.43-14.44)

1. **Verifique os valores de retorno** das chamadas.
2. Verifique se a chamada é feita de um **contexto permitido** (ex.: uma thread).
3. Várias chamadas **podem resultar em preempção**.

Muitos parâmetros são ponteiros: alguns são **entrada** (apontam para estruturas já criadas) e outros são **saída** (áreas já alocadas para resultados). O retorno é um **status**; **0 = `TX_SUCCESS`**.
```c
UINT err;
err = tx_thread_create(&hmi_thread, (CHAR*)"HMI Thread", hmi_thread_func,
                       (ULONG)NULL, &hmi_thread_stack, 1024, 1, 1, 10, TX_AUTO_START);
if (TX_SUCCESS != err) { tx_startup_err_callback(&hmi_thread, 0); }
```
Cada serviço na documentação traz **Allowed From** (de onde pode ser chamado: inicialização, threads, timers, ISRs) e **Preemption Possible** (sim/não).

<a id="s8-5"></a>
### 8.5 Semáforo × Mutex (tx 14.32 e 14.54-14.55, 14.45)

| | **Semáforo** (contador) | **Mutex** |
|---|---|---|
| Uso | **Sincronização** entre threads (ex.: sinalizar um evento) | **Exclusão mútua** |
| Valores | 0 a 4G (32 bits) | binário (mas conta até 4G: vários `put` da **mesma** thread) |
| **Dono** | **Não há dono** | **Uma única thread** é dona por vez |
| Operações | `tx_semaphore_get`, `tx_semaphore_put` | `tx_mutex_get`, `tx_mutex_put` |
| Quem faz `put` | **Qualquer** thread (ou ISR) | **Só o dono** |
| `get` com valor 0 | **suspende** a thread | **suspende** a thread |
| Ordem dos suspensos | **FIFO** | **FIFO** |
| Extra | – | pode implementar **protocolo de herança de prioridade** |

**Semáforo:** `get` **decrementa** (suspende se 0, B/NB/TO), `put` **incrementa** (pode **acordar** uma thread suspensa).
**Mutex:** `0` = recurso **livre**; `>0` = **tomado** por uma thread (valor 0..4G). **Só threads** podem ser donas: **não é permitido para ISRs, timers, etc.**

Serviços de mutex: `tx_mutex_create(mutex, nome, inherit)`, `tx_mutex_delete`, `tx_mutex_get(mutex, wait_option)` (**pode suspender a thread**), `tx_mutex_prioritize`, `tx_mutex_put`. Exemplo do slide:
```c
TX_MUTEX my_mutex;
UINT status;
status = tx_mutex_create(&my_mutex, "my_mutex_name", TX_NO_INHERIT);   // ou TX_INHERIT
status = tx_mutex_get(&my_mutex, TX_WAIT_FOREVER);
/* ... seção crítica ... */
status = tx_mutex_put(&my_mutex);
```
`wait_option`: `TX_NO_WAIT` (0), `TX_WAIT_FOREVER` (0xFFFFFFFF) ou **nº de ticks do SO** (timeout). Retornos do mutex: `TX_SUCCESS` (0x00), `TX_DELETED` (0x01), **`TX_NOT_AVAILABLE`** (0x1D, não conseguiu o mutex no tempo dado), `TX_WAIT_ABORTED` (0x1A), `TX_MUTEX_ERROR` (0x1C), `TX_WAIT_ERROR` (0x04), **`TX_CALLER_ERROR`** (0x13, chamado de contexto inválido, como ISR).
Retornos do semáforo: `TX_SUCCESS`, `TX_DELETED`, `TX_NO_INSTANCE` (0x0D, contador estava em 0 e não esperou), `TX_WAIT_ABORTED`, `TX_SEMAPHORE_ERROR` (0x0C), `TX_WAIT_ERROR`.

### 8.6 Timer (tx 14.50-14.53)

- Estrutura: `TX_TIMER`. **Thread associada: *System Timer*** (thread interna do ThreadX).
- **Modos:** **one-shot** (disparo único) ou **periódico**.
- **Efeito:** chama uma **função de expiração**, que **executa no contexto da thread System Timer**. Ela pode **enviar mensagem, setar evento, fazer get/put de semáforo**... **(não pode bloquear)**.
- **Conta regressiva** a partir do valor inicial, em **ticks**. O período do tick vem do **SysTick** e pode ser alterado (`tx_user.h`/`tx_port.h`).
- One-shot **desativa sozinho** ao fim da contagem. O periódico só desativa chamando **`tx_timer_deactivate`**. Uma vez **inativo**, pode ser **reprogramado** com `tx_timer_change`.

```c
UINT tx_timer_create(TX_TIMER *timer_ptr, CHAR *name_ptr,
                     VOID (*expiration_function)(ULONG), ULONG expiration_input,
                     ULONG initial_ticks, ULONG reschedule_ticks, UINT auto_activate);
UINT tx_timer_activate(TX_TIMER *);   UINT tx_timer_deactivate(TX_TIMER *);
UINT tx_timer_change(TX_TIMER *, ULONG initial_ticks, ULONG reschedule_ticks);
UINT tx_timer_delete(TX_TIMER *);     UINT tx_timer_info_get(...);
ULONG tx_time_get(VOID);  VOID tx_time_set(ULONG);     /* relógio do sistema em ticks */
```
`reschedule_ticks = 0` → one-shot; `> 0` → periódico. `auto_activate`: `TX_AUTO_ACTIVATE` ou `TX_NO_ACTIVATE`.

**Funcionamento interno (figura tx 14.52):** o `<<HW>> SysTick` gera `irq` para a `<<ISR>> SysTick`, que **incrementa** a variável global `_tx_timer_system_clock` e **acorda** (*wake*) a thread `<<thread>> SystemTimer`. Esta **chama** (*call*) a **função de expiração** associada ao objeto `:Timer`. "Esta função executa no contexto da thread System Timer; pode usar serviços como fila send, event set, semáforo put, para sincronizar/comunicar com threads."

### 8.7 Event flags (tx 14.56-14.58)

- Sincronização entre threads. **Cada flag é um bit** (levantado = 1, abaixado = 0). A thread A **avisa** a B de um evento levantando a flag; B pode ficar **suspensa** esperando, e **fica pronta quando a flag é setada**.
- **Em grupos de 32 flags**: estrutura `TX_EVENT_FLAGS_GROUP`.
- **`set`**: faz **AND** ou **OR** da palavra com o estado atual do grupo.
- **`get`**: testa flags específicas aplicando **AND** (todas) ou **OR** (qualquer uma); se o teste der certo, as flags **podem ser limpas**. A thread pode pedir para **suspender até** as flags desejadas serem setadas, **com timeout** opcional.

| Opção | Valor | Significado |
|---|---|---|
| `TX_OR` | 0x00 | **set:** OR com o grupo. **get:** qualquer uma das flags pedidas |
| `TX_OR_CLEAR` | 0x01 | **get:** qualquer uma e **limpa** as flags |
| `TX_AND` | 0x02 | **set:** AND (limpa as que não estão na máscara). **get:** **todas** as pedidas |
| `TX_AND_CLEAR` | 0x03 | **get:** todas as pedidas e **limpa** |

Exemplo do slide (tx 14.58): grupo começa em **0x0**. **Thread A** faz `set(0x1, TX_OR)` → grupo = 0x1. **Thread B** faz `set(0x10, TX_OR)` → grupo = **0x11**. **Thread C** fez `get(0x11, TX_AND_CLEAR, TX_WAIT_FOREVER)` e **ficou suspensa** até o grupo valer 0x11; ao ver 0x11, **limpa as flags** (grupo volta a 0x0) e **retoma** a execução.

```c
UINT tx_event_flags_create(TX_EVENT_FLAGS_GROUP *group_ptr, CHAR *name_ptr);
UINT tx_event_flags_set(TX_EVENT_FLAGS_GROUP *, ULONG flags_to_set, UINT set_option);
UINT tx_event_flags_get(TX_EVENT_FLAGS_GROUP *, ULONG requested_flags,
                        UINT get_option, ULONG *actual_flags_ptr, ULONG wait_option);
```
`tx_event_flags_create` retorna `TX_SUCCESS`, `TX_GROUP_ERROR` (0x06, ponteiro inválido) ou `TX_CALLER_ERROR` (0x13). "Allowed From: initialization and threads". 🧩 `tx_event_flags_set` pode ser chamada também de ISR.

### 8.8 Filas de mensagens (tx 14.59-14.62)

- Estrutura `TX_QUEUE`; deve ser **inicializada com o tamanho da mensagem e a capacidade**, além de uma **área de armazenamento**.
- **Tamanho da mensagem: 1 a 16 palavras** (palavra = 32 bits).
- **Send**: **copia** a mensagem para a fila e segue (não bloqueia), **mas bloqueia se a fila estiver cheia**.
- **Receive**: **copia** a mensagem da cabeça da fila e segue; **bloqueia se a fila estiver vazia**.
- Comportamento configurável: **NONBLOCKING** (retorna status de sucesso/erro), **BLOCKING** (espera indefinidamente), **BLOCKING com TIMEOUT** (máximo em ticks).
- **Duas operações de cópia por mensagem**: remetente → fila e fila → receptor (tx 14.60). Isso é **endereçamento indireto** (o remetente não conhece o receptor).

```c
UINT tx_queue_create(TX_QUEUE *queue_ptr, CHAR *name_ptr, UINT message_size,
                     VOID *queue_start, ULONG queue_size);
UINT tx_queue_send   (TX_QUEUE *queue_ptr, VOID *source_ptr,      ULONG wait_option);
UINT tx_queue_receive(TX_QUEUE *queue_ptr, VOID *destination_ptr, ULONG wait_option);
```
**Exemplo do slide (tx 14.61):** `static uint8_t queue_memory_queue_0[20];` (área de **20 bytes**), `message_size = 1` (**1 palavra** de 4 bytes) → **capacidade = 20 / 4 = 5 mensagens**.
```c
TX_QUEUE queue_0;
static uint8_t queue_memory_queue_0[20];
UINT err_queue_0 = tx_queue_create(&queue_0, (CHAR *)"queue 0", 1,
                                   &queue_memory_queue_0, sizeof(queue_memory_queue_0));
/* Remetente */
status = tx_queue_send(&queue_0, &thread_1_messages_sent, TX_WAIT_FOREVER);
if (status != TX_SUCCESS) break;
/* Receptor */
ULONG received_message;
while (1) {
    status = tx_queue_receive(&queue_0, &received_message, TX_WAIT_FOREVER);
    if (status != TX_SUCCESS) break;
}
```
Regra de bolso: **capacidade = `queue_size` (bytes) ÷ (`message_size` × 4)**. Estrutura interna (tx 14.62): `TX_QUEUE` (control struct) aponta para a **área de armazenamento** (`<<storage area>>`/queue storage); `Sender` faz `put`, `Receiver` faz `get`. Outros serviços: `tx_queue_front_send` (envia **na frente**), `tx_queue_flush`, `tx_queue_prioritize`, `tx_queue_info_get`, `tx_queue_send_notify`.

### 8.9 Memória: byte pool × block pool (tx 14.33)

| **Byte pool** | **Block pool** |
|---|---|
| **Versão thread-safe do heap** | Alocador de blocos thread-safe |
| Operações parecidas com `malloc`/`free` | Operações parecidas com `malloc`/`free` |
| Vários pools possíveis | Vários pools possíveis |
| Pool em área definida pelo usuário | Pool em área definida pelo usuário |
| Aloca/libera em **incrementos de byte** | Aloca/libera **um bloco** (tamanho fixo definido na criação) |
| **Pode haver fragmentação** | **Sem fragmentação** |
| Thread pode **suspender** se pedir memória e ela não estiver disponível | Idem |

Dica de prova: **determinismo/tempo de alocação previsível → block pool**; **tamanhos variados e flexibilidade → byte pool**.

---

<a id="s9"></a>
## 9. 🧩 Receitas, armadilhas e erros comuns

### 9.1 Qual primitiva usar

| Preciso de... | Use |
|---|---|
| Proteger um recurso (dado, periférico) **compartilhado** | **Mutex** |
| **Avisar** que algo aconteceu (sem dados) | **Event flags** (vários eventos num grupo) ou **semáforo** (contagem) |
| **Enviar dados** de uma tarefa a outra | **Fila** |
| Esperar um tempo / agir após um tempo | `tx_thread_sleep` / **timer** |
| Memória dinâmica **thread-safe** | **Byte pool** / **block pool** |

### 9.2 Padrão ISR → tarefa

A ISR deve ser **curta**: limpa o pedido de interrupção no periférico ([Resumo P1 §11.7](../P1/Resumo_P1.md#s11-7)) e **sinaliza** uma thread (event set, semáforo put ou fila com `TX_NO_WAIT`). A thread faz o trabalho pesado. **Mutex e chamadas bloqueantes não são permitidos em ISR** (dono do mutex precisa ser uma thread; ver `TX_CALLER_ERROR`).

### 9.3 Uso correto de mutex

```c
tx_mutex_get(&mtx, TX_WAIT_FOREVER);
/* seção crítica: curta, sem esperas longas */
tx_mutex_put(&mtx);              /* SEMPRE devolver; quem pega, devolve */
```
- Cada `get` precisa de um `put` da **mesma** thread (o contador do dono sobe e desce).
- Seção crítica **curta**; nada de `tx_thread_sleep` ou esperas longas dentro dela.
- Verificar o retorno do `get` quando houver timeout (`TX_NOT_AVAILABLE`).

### 9.4 Deadlock, inversão de prioridade (🧩, só citado nos slides)

- **Deadlock com dois mutexes:** a tarefa A pega M1 e pede M2; B pega M2 e pede M1: **as duas esperam para sempre**. Prevenção: todas as tarefas pegam os mutexes **na mesma ordem**; usar **timeout** no `get`; evitar segurar um mutex ao esperar por outro recurso.
- **Inversão de prioridade:** uma tarefa de **baixa** prioridade (L) segura um mutex que a de **alta** (H) quer; uma de prioridade **média** (M) preempta L; resultado: H espera M, sem ter relação com ele. **Herança de prioridade** (`TX_INHERIT` em `tx_mutex_create`): enquanto H espera, L **herda a prioridade de H** e termina a seção crítica logo; com `TX_NO_INHERIT` não há esse mecanismo (tx 14.29, 14.32).
- Os slides só citam "deadlocks e inversão de prioridade" como riscos (conc 13.14) e "priority inheritance" como recurso do mutex; o detalhe acima é complemento.

### 9.5 Erros que a disciplina pune

1. **Estrutura de controle local ou ponteiro não inicializado** ([§8.2](#s8)).
2. **Não checar o retorno** das chamadas ThreadX (tx 14.43).
3. Chamar serviço bloqueante ou mutex de **ISR/timer** ([§8.5](#s8) e [§8.6](#s8)).
4. Usar **semáforo para exclusão mútua** (sem dono, sem herança) em vez de mutex.
5. **Variáveis compartilhadas sem proteção** (`LDR/ADD/STR` interrompido, [§3.2](#s3)).
6. `tx_queue_create` com `message_size` em **bytes** (é em **palavras de 32 bits**) ou com `queue_size` em palavras (é em **bytes**).
7. **Tamanho de pilha** em palavras (o parâmetro é em bytes).
8. Confundir **0 = maior prioridade**.
9. Editar o `.h` gerado pelo SSP e esperar efeito (tx 14.25).
10. Esquecer que `tx_kernel_enter()` **não retorna** e que o `tx_application_define` roda dentro dele.

---

<a id="s10"></a>
## 10. Tabelas de revisão rápida

### 10.1 Exclusão mútua: soluções e limites

| Solução | Funciona em | Pontos fracos |
|---|---|---|
| Desabilitar interrupções | só 1 processador | atrasa tudo; pode travar o sistema; muitos RTOS proíbem |
| Instrução atômica (TAS, SWAP, **LDREX/STREX**) | 1 CPU e memória compartilhada | espera ocupada |
| Algoritmo de software (**Peterson**) | 1 CPU e memória compartilhada | só 2 tarefas; precisa de ordem de memória |
| **Semáforo/mutex** (do RTOS) | 1 CPU e memória compartilhada | risco de deadlock/inversão |
| **Mensagens** | **as três arquiteturas** (inclusive distribuída) | cópia de dados, latência |

### 10.2 Os 4 primitivos de comunicação/sincronização do ThreadX

| Objeto | Sincroniza | Carrega dados? | Dono? |
|---|---|---|---|
| **Fila** | sim | **sim** (1 a 16 palavras por mensagem) | – |
| **Event flags** | sim (AND/OR de 32 bits) | não (só sinais) | – |
| **Semáforo** | sim (contador 0..4G) | não | **não** |
| **Mutex** | exclusão mútua | não | **sim** (só o dono faz `put`) |

### 10.3 Nomes que mudam (conceito × ThreadX)

| Conceito (slide conc/excl) | ThreadX |
|---|---|
| Ready | Ready |
| Running | **Executing** |
| Waiting | **Suspended** |
| Inactive/Terminated | **Completed / Terminated** |
| Mutex/semáforo (get/put) | `tx_mutex_get/put`, `tx_semaphore_get/put` |
| Mensagem assíncrona | **fila** |
| Evento | **event flags group** |
| Tick | período do **SysTick** (`TX_TIMER_TICKS_PER_SECOND`) |

### 10.4 Checklist para uma questão de "projete a aplicação"

1. Liste as **atividades** → uma **thread** por atividade (nome, prioridade).
2. Quem **gera eventos** (botão, timer, dado chegando)? → **ISR** + **event flags**/**semáforo**/**fila**.
3. Quais **dados** passam entre threads? → **filas** (defina as **mensagens/comandos**).
4. Há **recurso compartilhado**? → **mutex** (e qual é a seção crítica).
5. Há **tempo** envolvido? → `tx_thread_sleep`, **timer** (modo e período em ticks) ou **timeout** no `get`.
6. Desenhe o **UML** com os símbolos da disciplina ([§6.4](#s6)).
7. Escreva `tx_application_define`: **criar todos os objetos** (eventos, filas, mutexes, timers, threads) com os parâmetros corretos.
8. Escreva as **funções de entrada**: laço infinito, bloqueando em `get/receive`, **checando retornos**.
9. Confira: contexto permitido, ordem de aquisição dos mutexes, tamanho das mensagens (palavras) e das áreas (bytes).
