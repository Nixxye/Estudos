# Camada de Transporte — do zero até dominar ACKs e tratamento de problemas

> **Objetivo:** que você consiga, sozinho, (1) explicar o que a camada de transporte faz, (2) desenhar qualquer diagrama de tempo com perda/atraso/ACK, (3) calcular seq/ACK/RTT/cwnd, e (4) responder qualquer pergunta de prova sobre isso.
> Como ler: a ordem foi pensada para **construir o raciocínio**. Cada parte usa só o que foi explicado antes. Onde algo vai **além dos slides**, está marcado com *(além dos slides)* — entra para você entender, mas a prova segue os slides.
> Complementos: [Resumo_P1_Redes.md](Resumo_P1_Redes.md) (fórmulas), [Gabarito_P1_Redes.md](Gabarito_P1_Redes.md) (provas resolvidas), [Temas_Importantes_Referencias.md](Temas_Importantes_Referencias.md) (o que cai).

## Índice
1. O problema que o transporte resolve
2. Portas, sockets e demultiplexação
3. UDP (o transporte "mínimo")
4. Por que entrega confiável é difícil: o catálogo de problemas
5. Construindo a confiabilidade passo a passo (rdt 1.0 → 3.0)
6. Pipelining: GBN e SR
7. TCP: ACKs, números de sequência e timers
8. TCP: **todos os cenários de problema** (diagramas)
9. Fluxo e congestionamento vistos pelos ACKs
10. Tabela-mestra: problema → detecção → reação
11. Como a prova pergunta isso (e como resolver) + exercícios resolvidos
12. Checklist final e armadilhas

---

# 1. O problema que o transporte resolve

## 1.1 A situação
Dois programas (processos) em computadores distantes querem conversar. Entre eles há a **rede**: roteadores e enlaces que só sabem uma coisa — **tentar** levar pacotes de um host a outro. Essa rede é **"best effort" (melhor esforço)**: ela *tenta*, mas não promete nada. Um pacote pode:
- **chegar corrompido** (bits trocados),
- **se perder** (fila de roteador cheia → descartado),
- **chegar duplicado**,
- **chegar fora de ordem**,
- **demorar** muito (atraso variável).

## 1.2 O que a camada de transporte adiciona
| Camada | Responsabilidade | "Escopo" |
|---|---|---|
| **Rede (IP)** | levar o pacote **do host A ao host B** (best effort) | host‑a‑host |
| **Transporte (TCP/UDP)** | levar os dados **do processo X ao processo Y** | processo‑a‑processo |

Analogia dos slides: 12 crianças da casa A trocam cartas com 12 da casa B. **Correios** (rede) levam as cartas de casa a casa e só leem o endereço da **casa**. **Ana e Pedro** (transporte) recolhem as cartas dos irmãos e as entregam em mãos a cada criança (**multiplexação/demultiplexação**) — e, se quisessem, poderiam ainda garantir que nenhuma carta se perdeu (**confiabilidade**).

O transporte roda **só nos sistemas finais** (hosts). Roteadores não leem cabeçalho de transporte.

## 1.3 Dois serviços na Internet
- **UDP**: só multiplexa/demultiplexa e detecta erro. Nada de garantia.
- **TCP**: multiplexa **e** transforma o canal ruim em um **tubo confiável e ordenado**, com controle de fluxo e de congestionamento.
Nenhum dos dois garante **atraso máximo** nem **vazão mínima**.

---

# 2. Portas, sockets e demultiplexação

## 2.1 Socket
O **socket** é a "porta" por onde o processo entrega/recebe mensagens do transporte. Fica na fronteira: acima, o programador manda; abaixo, o sistema operacional cuida do TCP/UDP.

## 2.2 Portas
Número de **16 bits** (0–65535) que identifica o socket **dentro do host**. Faixas: 0–1023 conhecidas (80 HTTP, 443 HTTPS, 53 DNS, 25 SMTP, 22 SSH, 21 FTP), 1024–49151 registradas, 49152–65535 efêmeras (o cliente recebe uma delas).
**Um processo é identificado por IP + porta.**

## 2.3 Cabeçalho comum
Todo segmento (UDP ou TCP) começa com **porta de origem** e **porta de destino** (16 bits cada). O receptor usa isso para **demultiplexar**.
- **Multiplexação (emissor):** vários sockets entregam dados ao transporte; ele coloca portas de origem/destino em cada segmento.
- **Demultiplexação (receptor):** olha as portas (e IPs) e entrega ao socket certo.

## 2.4 Demux UDP × TCP
| | UDP | TCP |
|---|---|---|
| Socket identificado por | **(IP destino, porta destino)** | **quádrupla** (IP origem, porta origem, IP destino, porta destino) |
| Vários clientes → mesma porta | **mesmo socket** (efeito funil) | **sockets diferentes** (um por conexão) |
| Como o processo sabe quem enviou | `recvfrom()` devolve IP+porta de origem | cada socket já é de um cliente |

**Exemplo TCP (servidor B, porta 80):** (A,9157,B,80) → socket 1; (C,5775,B,80) → socket 2; (C,9157,B,80) → socket 3. Sockets 1 e 3 têm a mesma porta de cliente (9157), mas IP diferente → sockets diferentes.
**Resposta do servidor:** portas e IPs **invertidos**: (B,80 → A,9157).

## 2.5 Sockets no código (para responder prova)
- **UDP:** servidor `socket(SOCK_DGRAM) → bind(porta) → recvfrom → sendto`. **Um** socket atende todos.
- **TCP:** servidor `socket(SOCK_STREAM) → bind → listen → accept`. O `accept()` devolve **novo socket de conexão**. Servidor tem **welcoming socket + 1 por cliente** (n clientes ⇒ **n+1**). Cliente: `connect()` dispara o handshake.
- TCP: servidor tem que subir **antes** (alguém precisa aceitar o SYN). UDP: cliente pode subir antes.

---

# 3. UDP — o transporte mínimo

**Cabeçalho de 8 bytes:** porta origem | porta destino | comprimento | checksum.

## 3.1 O que o UDP faz
- Multiplexa/demultiplexa por porta.
- **Detecta** erros com checksum (não corrige).
- Entrega **datagramas independentes**: sem conexão, sem estado, sem ordem garantida, sem retransmissão.

## 3.2 Por que existe (decorar para a prova)
1. **Sem handshake** → sem atraso inicial (uma transação = 1 RTT).
2. **Sem estado de conexão** no servidor → atende mais clientes.
3. **Cabeçalho pequeno** (8 B vs 20+ B).
4. **Sem controle de congestionamento** → a aplicação controla a taxa.
5. Útil quando **atraso importa mais que perda** (voz, vídeo ao vivo, jogos) ou a troca é curta (DNS).
6. Se a aplicação quiser confiabilidade, **implementa por conta própria** (ex.: QUIC, retransmissão de consulta DNS).

## 3.3 Checksum da Internet — o cálculo
1. Divida o conteúdo (cabeçalho + pseudo‑cabeçalho IP + dados) em **palavras de 16 bits**.
2. **Some** tudo. Se houver "vai‑um" além do 16º bit, **some-o de volta** na posição menos significativa (*wraparound*).
3. **Inverta todos os bits** do resultado → este é o checksum.

**Exemplo do slide:**
```
  1110011001100110
+ 1101010101010101
= 1 1011101110111011    ← 17 bits (o '1' à esquerda é o carry)
+                 1     ← soma o carry de volta
= 1011101110111100      ← soma com wraparound
  0100010001000011      ← NOT (checksum) = o valor transmitido
```
**Receptor:** soma as palavras **incluindo** o checksum: `1011101110111100 + 0100010001000011 = 1111111111111111`. Se for **todo 1**, aceita; qualquer 0 → erro.
**Limites:** só detecta; erros que se compensam podem passar. O que acontece com um segmento corrompido? É **descartado em silêncio** — para o remetente isso é igual a uma **perda** (guarde essa ideia, ela é central).

---

# 4. Por que entrega confiável é difícil: o catálogo de problemas

Antes de construir a solução, liste o que pode dar errado entre A e B. **Cada mecanismo que vamos estudar existe para resolver um destes problemas.**

| # | Problema | Exemplo | Quem percebe e como |
|---|---|---|---|
| P1 | **Dado corrompido** | bit trocado no meio do caminho | receptor, pelo **checksum** |
| P2 | **Dado perdido** | fila de roteador cheia | **ninguém avisa**; remetente percebe pela **falta de ACK** (timeout) ou por **ACKs duplicados** |
| P3 | **ACK perdido** | o dado chegou, mas o ACK se perdeu | remetente: falta de ACK → timeout (ou ACK posterior cobre) |
| P4 | **ACK corrompido** | checksum do ACK falha | remetente trata como ACK perdido/desconhecido |
| P5 | **Duplicata** | retransmissão desnecessária; rede duplicou | receptor, pelo **nº de sequência** |
| P6 | **Fora de ordem** | caminhos diferentes | receptor, pelo **nº de sequência** |
| P7 | **Atraso grande** (timeout prematuro) | ACK demora mais que o timer | remetente (erra, pensando em perda) → vira duplicata (P5) |
| P8 | **Receptor lento** | buffer cheio | receptor avisa com `rwnd` (controle de fluxo) |
| P9 | **Rede congestionada** | muitas fontes | remetente infere por perda/atraso (controle de congestionamento) |

**Ideia‑chave:** o remetente **só enxerga duas coisas**: *chegou um ACK* ou *o tempo passou sem ACK*. A partir disso ele tem que **deduzir** o que aconteceu. Por isso um ACK precisa dizer **exatamente o que foi recebido**.

---

# 5. Construindo a confiabilidade passo a passo (rdt)

*rdt = reliable data transfer.* Vamos construir o protocolo **do mais simples ao completo**, e a cada passo perguntar: **"o que o canal fez de errado e que informação o receptor/remetente precisa para perceber isso?"**. O resultado final, o **rdt 3.0**, é o **bit alternante**.

**Notação das FSMs (máquinas de estados):** `evento / ação`. Interface: `rdt_send()` (aplicação → protocolo), `udt_send()` (protocolo → rede), `rdt_rcv()` (rede → protocolo), `deliver_data()` (protocolo → aplicação).
**Dois tipos de pacote** vão aparecer: **DATA** (leva dados) e **ACK/NAK** (leva só o feedback). Ambos viajam pela rede e **ambos podem se corromper ou se perder**.

| Versão | Canal | O que ficou faltando | O que se acrescenta |
|---|---|---|---|
| **1.0** | perfeito | — | nada |
| **2.0** | erros de bit | como saber que o dado chegou ruim? | checksum + **ACK/NAK** + retransmissão |
| **2.1** | idem, mas ACK/NAK também corrompem | **duplicatas** | **número de sequência** (0/1) |
| **2.2** | idem | simplificar | **ACK carrega o nº de seq** (sem NAK) |
| **3.0** | erros **e perdas** | pacote/ACK **sumiram** | **temporizador** |

## 5.1 rdt 1.0 — canal perfeito
Sem erros e sem perdas. Remetente: pega o dado, monta o pacote, envia. Receptor: recebe, extrai, entrega. **Um estado só**; nada de ACK.

## 5.2 rdt 2.0 — canal com erros de bit
**O que o canal faz de errado:** troca bits dentro do pacote.
**Novos mecanismos:**
1. **Detecção de erro** — o remetente calcula um **checksum** e o inclui no pacote; o receptor recalcula e compara.
2. **Feedback do receptor** — pacote especial de volta: **ACK** ("recebi bem") ou **NAK** ("veio com erro, repita").
3. **Retransmissão (ARQ)** — ao receber NAK, o remetente reenvia o mesmo pacote.

**Remetente (2 estados):**
- *Esperar chamada de cima:* pega o dado, monta `DATA(dados, checksum)`, envia → vai a *Esperar ACK/NAK*.
- *Esperar ACK/NAK:* se chega **NAK** → reenvia o `DATA` e continua esperando; se chega **ACK** → volta a *Esperar chamada de cima*.
**Receptor (1 estado):** recebe `DATA`; **corrompido** → envia NAK; **íntegro** → entrega e envia ACK.

> É o **pare‑e‑espere (stop‑and‑wait)**: o remetente **não aceita dado novo** da aplicação enquanto não obtiver ACK.

## 5.3 rdt 2.1 — o número de sequência (e por que ele é necessário)

### 5.3.1 O defeito do 2.0: o ACK/NAK também pode se corromper
O remetente recebe algo ilegível e **não sabe** o que o receptor concluiu. Opções:
- **Não reenviar** → se era um NAK, o dado se perde para sempre. ✘
- **Reenviar** → se era um ACK, o receptor recebe **o mesmo dado duas vezes**. ✘ (a menos que consiga reconhecer a duplicata)

**A única saída segura é reenviar — e dar ao receptor um meio de reconhecer a duplicata.**

### 5.3.2 Cenário que quebra o 2.0 (veja o problema com seus olhos)
```
Rem.                                         Receptor
 DATA("A") ───────────────────────────────►  íntegro → entrega "A" → ACK
 X◄────────────────── ACK (CORROMPIDO) ───   remetente não entende
 (não sabe se "A" chegou; reenvia por segurança)
 DATA("A") ───────────────────────────────►  íntegro → entrega "A" de NOVO ✘ (duplicata!)
```
A aplicação do destino recebe "A", "A". O receptor **não tem como saber** se o 2º pacote é um dado novo (que por acaso é igual) ou uma retransmissão.

### 5.3.3 A solução: numerar os pacotes
O remetente coloca no cabeçalho do pacote um **número de sequência (`seq`)**. Cada **dado novo** recebe o número "seguinte"; uma **retransmissão repete o mesmo número**.
- **Dado novo** → `seq` **diferente** do pacote anterior.
- **Retransmissão** → `seq` **igual** ao do pacote anterior.
Assim o receptor distingue: "esse `seq` é o que eu espero (novo)" × "esse `seq` é o do pacote que eu já entreguei (duplicata)".

### 5.3.4 Por que **1 bit** (0 ou 1) basta no pare‑e‑espere
No pare‑e‑espere só existe **um pacote "em jogo"** de cada vez: o remetente só avança para o próximo depois de ter certeza do ACK. Portanto, o receptor só pode receber **duas** coisas:
1. o pacote **que espera** (novo), ou
2. **uma cópia do pacote anterior** (retransmissão).
Nunca recebe "dois pacotes à frente". Com **dois números alternados (0,1,0,1,…)** já dá para diferenciar "o esperado" de "o anterior". Por isso o nome **bit alternante**.

**Sequência dos números:** primeiro dado: `seq = 0`; próximo dado: `seq = 1`; próximo: `seq = 0`; … Só **alterna quando o remetente tem certeza** de que o anterior foi recebido (chegou o ACK correto).

### 5.3.5 O receptor passa a ter **estado**
Ele guarda **qual `seq` espera** (dois estados: *Esperar 0* e *Esperar 1*).

**Regra do receptor 2.1 (estado "Esperar `s`"):**
| Chega... | O receptor... | Novo estado |
|---|---|---|
| **Pacote íntegro com `seq = s`** (o esperado) | **entrega** à aplicação; envia **ACK** | passa a esperar `1−s` |
| **Pacote íntegro com `seq ≠ s`** (duplicata do anterior) | **NÃO entrega**; envia **ACK** (para o remetente avançar) | continua em `s` |
| **Pacote corrompido** | envia **NAK** | continua em `s` |

**Remetente 2.1:** (4 estados: *Esperar chamada 0*, *Esperar ACK/NAK 0*, *Esperar chamada 1*, *Esperar ACK/NAK 1*). Ao chegar **NAK ou ACK/NAK ilegível** → **reenvia** o mesmo pacote (mesmo `seq`). Ao chegar **ACK íntegro** → passa ao próximo número.

## 5.4 rdt 2.2 — sem NAK, ACK com número (**como identificar o ACK**)

### 5.4.1 A ideia
Em vez de ACK **e** NAK, usa‑se só **ACK**, mas agora o ACK **diz qual pacote confirma**: leva o **número de sequência do último pacote recebido corretamente**.
- Pacote bom com `seq = 0` → receptor envia **`ACK(0)`**.
- Pacote bom com `seq = 1` → receptor envia **`ACK(1)`**.
- Chegou algo ruim (corrompido) ou duplicata → o receptor envia de novo o **`ACK` do último pacote bom** (o "ACK antigo").

### 5.4.2 Como o remetente interpreta (esta é a chave!)
Se o remetente acabou de enviar o pacote com `seq = s`, ele espera `ACK(s)`:
| O que chega | Interpretação |
|---|---|
| **`ACK(s)`** íntegro (número **igual** ao `seq` que enviei) | **Confirmação!** o pacote `s` foi recebido → próximo dado |
| **`ACK(1−s)`** íntegro (número **diferente**, o do pacote anterior) | **ACK duplicado/antigo** ≡ **NAK**: o receptor me diz "o último que recebi bem foi o anterior" → **o pacote `s` NÃO chegou bem** → reenvia |
| ACK **corrompido** | não dá para confiar → reenvia |

> **Resumo:** o ACK é **identificado pelo número que carrega**. O remetente compara esse número com o `seq` do pacote **que está esperando confirmar**. **Igual → confirmado. Diferente → repete.**

> **Esta é a origem de "ACK duplicado como sinal de problema"**, que reaparece no GBN e no TCP (fast retransmit).

## 5.5 rdt 3.0 — canal com erros **e perdas** = **BIT ALTERNANTE**

### 5.5.1 O que faltava
Se o **pacote DATA** ou o **ACK** simplesmente **sumir** (perda), o receptor não tem o que fazer e o remetente fica **esperando para sempre**: não chega NAK, não chega nada. **Solução: um temporizador (timer).**

### 5.5.2 Formato dos dois pacotes (o que viaja)
```
DATA:  [ seq (1 bit: 0 ou 1) | checksum | dados ]
ACK :  [ ack (1 bit: 0 ou 1) | checksum ]          ← o 'ack' é o seq do pacote confirmado
```
- `seq` do DATA = número do **pacote** (o remetente atribui; alterna a cada dado novo).
- `ack` do ACK = **cópia do `seq`** do pacote que o receptor acabou de **receber bem** (**não** é "o próximo esperado" — veja a comparação com o TCP em §5.5.9).

### 5.5.3 Remetente — a máquina de 4 estados
| Estado | Evento | Ação | Próximo estado |
|---|---|---|---|
| **Esperar chamada 0** | `rdt_send(dado)` | monta `DATA(seq=0)`, envia, **liga timer** | Esperar ACK 0 |
| **Esperar ACK 0** | chega **`ACK(0)`** íntegro | **para o timer** | Esperar chamada 1 |
| | chega **`ACK(1)`** ou **ACK corrompido** | **ignora** (nada faz; o timer cuida) | Esperar ACK 0 |
| | **timeout** | **reenvia** `DATA(seq=0)`, **religa o timer** | Esperar ACK 0 |
| **Esperar chamada 1** | `rdt_send(dado)` | monta `DATA(seq=1)`, envia, **liga timer** | Esperar ACK 1 |
| **Esperar ACK 1** | chega **`ACK(1)`** íntegro | **para o timer** | Esperar chamada 0 |
| | chega **`ACK(0)`** ou corrompido | **ignora** | Esperar ACK 1 |
| | **timeout** | reenvia `DATA(seq=1)`, religa o timer | Esperar ACK 1 |

**Pontos a notar**
- O remetente só "enxerga" **uma** variável: **qual `seq` está pendente**. Isso define quais ACKs ele aceita.
- **Alternar o bit** acontece **somente** ao receber o ACK correto.
- No rdt 3.0 do livro, ACK errado/corrompido é **ignorado** (não reenvia na hora); o **timeout** faz a retransmissão. *(Reenviar na hora, como no 2.2, também seria correto, mas geraria cópias a mais.)*
- Enquanto está em "Esperar ACK", **recusa** novos dados da aplicação (pare‑e‑espere).

### 5.5.4 Receptor — a máquina de 2 estados
Estado = **qual `seq` espera** (`s`). Regra (idêntica ao 2.2):
| Chega... | Ação | Estado |
|---|---|---|
| **Pacote íntegro com `seq = s`** | **entrega** dado à aplicação; envia **`ACK(s)`** | → `1−s` |
| **Pacote íntegro com `seq = 1−s`** (**duplicata**) | **não entrega**; reenvia **`ACK(1−s)`** (o ACK do último bom) | fica em `s` |
| **Pacote corrompido** | **não entrega**; reenvia **`ACK(1−s)`** (o ACK do último bom) | fica em `s` |

### 5.5.5 Como o receptor identifica uma **duplicata**
Ele compara o **`seq` do pacote recebido** com o **`seq` que espera**: se for **diferente do esperado e íntegro**, é uma cópia do **pacote que ele já entregou** → descarta (não entrega duas vezes) mas **responde com o ACK desse pacote** para que o remetente (que não recebeu o ACK anterior) possa avançar.

### 5.5.6 Como o remetente identifica um **ACK** (resumo prático)
| Remetente está em... | `ACK(0)` íntegro | `ACK(1)` íntegro | ACK corrompido | Timeout |
|---|---|---|---|---|
| **Esperar ACK 0** (acabou de enviar seq 0) | ✔ **confirmado** → manda o próximo (seq 1) | ✘ **ignora** (ACK velho, do pacote anterior) | ✘ ignora | **reenvia** seq 0 |
| **Esperar ACK 1** (acabou de enviar seq 1) | ✘ ignora | ✔ **confirmado** → manda o próximo (seq 0) | ✘ ignora | **reenvia** seq 1 |

**Regra de bolso:** *"O ACK vale se o número dele for igual ao `seq` do pacote que estou esperando confirmar."*

### 5.5.7 Os cenários — passo a passo, com estados
Convenção de cada linha: `t` = instante; **Rem.** = remetente; **Rec.** = receptor (e o `seq` que espera).

**① Sem perda**
| t | Evento | Estado Rem. | Rec. espera | Na rede |
|---|---|---|---|---|
| 0 | app dá dado "A" | Esperar chamada 0 → **Esperar ACK 0** (timer ligado) | 0 | `DATA(0,"A")` → |
| 1 | Rec.: seq 0 = esperado → entrega "A" | | 0 → **1** | ← `ACK(0)` |
| 2 | Rem.: ACK(0) = seq pendente (0) → para o timer | → **Esperar chamada 1** | 1 | |
| 3 | app dá "B" | → **Esperar ACK 1** | 1 | `DATA(1,"B")` → |
| 4 | Rec.: seq 1 = esperado → entrega "B" | | 1 → **0** | ← `ACK(1)` |
| 5 | Rem.: ACK(1) = pendente (1) → para o timer | → Esperar chamada 0 | 0 | |

**② Pacote DATA perdido**
| t | Evento | Estado Rem. | Rec. espera | Na rede |
|---|---|---|---|---|
| 0 | Rem. envia `DATA(0,"A")` (timer on) | Esperar ACK 0 | 0 | `DATA(0)` → **X (perdido)** |
| 1 | nada chega; o timer corre | Esperar ACK 0 | 0 | |
| 2 | **timeout** → reenvia `DATA(0,"A")`, religa timer | Esperar ACK 0 | 0 | `DATA(0)` → |
| 3 | Rec.: seq 0 = esperado → entrega, **ACK(0)** | | 0 → 1 | ← `ACK(0)` |
| 4 | Rem.: ACK(0) correto → para timer | → Esperar chamada 1 | 1 | |

**③ ACK perdido** (o dado **chegou**, o receptor já avançou)
| t | Evento | Estado Rem. | Rec. espera | Na rede |
|---|---|---|---|---|
| 0 | Rem. envia `DATA(0,"A")` | Esperar ACK 0 | 0 | → |
| 1 | Rec.: entrega "A", envia `ACK(0)` | | 0 → **1** | ← `ACK(0)` **X (perdido)** |
| 2 | **timeout** (Rem. não sabe se "A" chegou) → reenvia `DATA(0,"A")` | Esperar ACK 0 | 1 | `DATA(0)` → |
| 3 | Rec.: seq 0 ≠ esperado (1) → **DUPLICATA**: **não entrega**; reenvia **`ACK(0)`** | | 1 | ← `ACK(0)` |
| 4 | Rem.: ACK(0) correto → para timer | → Esperar chamada 1 | 1 | |
**O seq impediu a aplicação de receber "A" duas vezes.**

**④ DATA corrompido** (o checksum falha no receptor)
| t | Evento | Rec. espera | Na rede |
|---|---|---|---|
| 0 | Rem. envia `DATA(0,"A")`; chega com bits trocados | 0 | |
| 1 | Rec.: checksum falha → **não entrega**; reenvia o ACK do último bom (**`ACK(1)`**, pois o último bom foi o seq 1 anterior) | 0 | ← `ACK(1)` |
| 2 | Rem. (esperando ACK 0) recebe `ACK(1)` → **número errado → ignora** | | |
| 3 | **timeout** → reenvia `DATA(0,"A")` | 0 | → |
| 4 | Rec.: íntegro, seq 0 → entrega, `ACK(0)` | 0 → 1 | ← |
*(No início da comunicação, o "último bom" pode ser tratado como `ACK(1)` por convenção.)*

**⑤ ACK corrompido**
| t | Evento | Estado Rem. |
|---|---|---|
| 0 | `DATA(0)` entregue; Rec. envia `ACK(0)`, que chega **corrompido** | Esperar ACK 0 |
| 1 | Rem.: checksum do ACK falha → **ignora** | Esperar ACK 0 |
| 2 | **timeout** → reenvia `DATA(0)` | |
| 3 | Rec.: duplicata → não entrega, `ACK(0)` | |
| 4 | Rem.: ACK(0) correto → avança | → Esperar chamada 1 |

**⑥ Timeout prematuro** (o timer foi curto demais; nada se perdeu, só demorou)
| t | Evento | Estado Rem. | Rec. espera |
|---|---|---|---|
| 0 | Rem. envia `DATA(0)` | Esperar ACK 0 | 0 |
| 1 | Rec.: entrega, `ACK(0)` (ainda a caminho) | | 0 → 1 |
| 2 | **timeout prematuro** → reenvia `DATA(0)` | Esperar ACK 0 | 1 |
| 3 | chega o **1º `ACK(0)`**: correto → avança, **envia `DATA(1)`** | → Esperar ACK 1 | |
| 4 | Rec.: recebe a **cópia** `DATA(0)`: duplicata → `ACK(0)` | | 1 |
| 5 | Rem. (esperando ACK 1) recebe o **2º `ACK(0)`**: **número errado → ignora** | Esperar ACK 1 | |
| 6 | Rec.: recebe `DATA(1)` → entrega, `ACK(1)` | | → 0 |
**Resultado:** correto, mas **gastou banda** com retransmissão e ACK desnecessários. É o custo de um timer curto.

### 5.5.8 O que acontece se tirarmos cada mecanismo (para fixar o porquê)
| Sem... | Falha |
|---|---|
| **checksum** | dado corrompido seria entregue |
| **ACK** | o remetente não sabe se chegou |
| **nº de seq** | cenários ③ e ⑤ entregam o dado **duas vezes** |
| **número no ACK** | o remetente não sabe **qual pacote** o ACK confirma (cenários ④ e ⑥ ficam ambíguos) |
| **timer** | cenários ② e ③ travam para sempre (perda não gera nenhum evento) |

### 5.5.9 Comparação: número no ACK do bit alternante × número no ACK do TCP
| | **Bit alternante** | **TCP** |
|---|---|---|
| O que o `ack` contém | o **`seq` do pacote confirmado** (do último bom) | o **próximo byte esperado** |
| Numera | **pacotes** (0/1) | **bytes** (32 bits) |
| Tipo | individual (um pacote por vez) | **cumulativo** |
| Identificar duplicata no receptor | `seq` ≠ esperado | `seq` < próximo byte esperado |
| Identificar ACK válido no remetente | `ack == seq` pendente | `ack > SendBase` (novo); `ack == SendBase` (duplicado) |

### 5.5.10 Limite do bit alternante *(além dos slides)*
Só 2 números significam que um **ACK extremamente atrasado** (que "dá a volta" no ciclo 0→1→0) poderia ser confundido com o ACK de um pacote novo de mesmo número. O protocolo **assume** que a rede **não atrasa** pacotes por tanto tempo (ou que o timer é bem escolhido). Numeração maior e janelas (GBN/SR) aumentam essa preocupação (§6.4).

## 5.6 O desempenho do pare‑e‑espere
Utilização do remetente: `U = (L/R) / (RTT + L/R)`.
Exemplo: R = 1 Gbps, L = 8000 bits, RTT = 30 ms → `L/R = 8 µs` → `U = 0,008 / 30,008 ≈ 0,00027 = 0,027 %`. O enlace fica quase todo parado esperando ACK. **Solução: pipelining (§6).**

## 5.7 Exercícios sobre o bit alternante

**E1.** O remetente enviou `DATA(1)` e está em *Esperar ACK 1*. Chega `ACK(0)` íntegro. O que faz? **R:** ignora (número ≠ `seq` pendente). Continua esperando; se o timer vencer, reenvia `DATA(1)`.

**E2.** O receptor espera `seq = 1` e recebe `DATA(0)` íntegro. O que faz? **R:** é duplicata → **não entrega**; envia `ACK(0)`; continua esperando 1.

**E3.** Por que o receptor envia ACK para uma duplicata em vez de ignorá‑la? **R:** o ACK anterior pode ter se perdido; sem esse ACK o remetente reenviaria **para sempre**.

**E4.** Por que o remetente não alterna o bit logo ao enviar? **R:** só alterna ao receber o ACK correto; antes disso o pacote pode ter de ser retransmitido **com o mesmo número**.

**E5.** Por que 1 bit é suficiente aqui, mas não com pipelining? **R:** com 1 pacote em jogo, o receptor só vê "o esperado" ou "o anterior". Com vários pacotes em voo, a numeração precisa distinguir muitos pacotes e retransmissões de ciclos anteriores (§6.4).

**E6.** Descreva o que ocorre se o timer for **menor que o RTT**. **R:** timeouts prematuros: retransmissões desnecessárias; o receptor descarta as duplicatas (pelo `seq`) e re‑ACKa; o remetente ignora o ACK velho (número errado). Correto, mas desperdiça banda (cenário ⑥).

**E7.** Verdadeiro ou falso: "Se o ACK é corrompido, o dado se perde." **R:** Falso. O remetente reenvia por timeout e o receptor descarta a duplicata pelo `seq`.

**E8.** Dada a sequência na rede `DATA(0) → ACK(0) → DATA(1) → [DATA(1) perdido] → timeout → DATA(1) → ACK(1) → DATA(0)`, quantos dados a aplicação do destino recebe? **R:** 3 (os `seq` 0, 1 e 0 novos); a perda de `DATA(1)` não gerou duplicata.

---

# 6. Pipelining: Go‑Back‑N e Selective Repeat

> **Pré‑requisito:** seção 5 (bit alternante). Aqui o raciocínio é: "o pare‑e‑espere é correto, mas lento; como enviar **vários** pacotes de uma vez **sem perder a confiabilidade**?" A resposta tem duas variantes — **GBN** e **SR** — que diferem em **como o ACK é interpretado** e **o que se retransmite quando algo dá errado**.

## 6.0 Por que pipelining (a intuição)

**Pare‑e‑espere** = um caminhão sai com **uma** caixa, viaja, entrega, e só quando o recibo volta o próximo caminhão sai. A estrada fica quase vazia.
**Pipelining** = vários caminhões saem um atrás do outro; a estrada fica "cheia".

Em números (exemplo do slide): `R = 1 Gbps`, `L = 8000 bits` (`L/R = 8 µs`), `RTT = 30 ms`.
- Pare‑e‑espere: `U = 8 µs / (30 ms + 8 µs) ≈ 0,027 %`.
- Com **N** pacotes em voo: `U = N · 8 µs / 30,008 ms`.
- Para ocupar **100 %** do enlace: `N ≈ 30,008 ms / 0,008 ms ≈ 3751` pacotes em voo ("encher o cano": é o **produto banda × atraso**).

**O preço do pipelining** (o que fica mais difícil):
1. Os **números de sequência** precisam de uma faixa maior (não basta 0/1).
2. O **remetente** precisa **guardar** (buffer) os pacotes enviados e ainda não confirmados, porque pode ter que reenviá‑los.
3. O **receptor** pode precisar de buffer (no SR) para os pacotes que chegam fora de ordem.
4. Surge a pergunta central: **se um pacote no meio do "trem" se perde, o que fazemos com os que vieram depois dele?** — é isso que separa GBN de SR.

---

## 6.1 Ideias comuns a GBN e SR

### 6.1.1 A janela deslizante do remetente
O remetente tem uma **janela de tamanho N**: o número máximo de pacotes que podem estar **enviados e ainda não confirmados** ao mesmo tempo. Ele enxerga a faixa de números de sequência dividida em **quatro regiões**:

```
 já enviados            enviados,          autorizados,          não
 e confirmados      ainda SEM ACK         ainda não enviados   autorizados
 ──────────────┬─────────────────────┬─────────────────────┬──────────────
   ... 0 1 2 3 │ 4  5  6             │ 7  8                │ 9 10 11 ...
               ▲                     ▲
             base               nextseqnum
               └────── janela de tamanho N = 6 ─────────────┘
```
- **`base`**: número do pacote **mais antigo** ainda sem ACK (início da janela).
- **`nextseqnum`**: número do **próximo pacote** a ser enviado.
- Pacotes em voo = `nextseqnum − base` (no GBN). A janela está **cheia** quando `nextseqnum = base + N`; nesse caso o remetente **recusa novos dados da aplicação** até a janela andar.
- A janela **desliza** para a direita quando chegam ACKs que confirmam o pacote `base`. Cada deslize "libera" números novos (os que estavam em "não autorizados" passam a "autorizados").

### 6.1.2 O que o ACK significa muda tudo
| | GBN | SR |
|---|---|---|
| `ACK(n)` quer dizer | "**todos até n** chegaram em ordem" (**cumulativo**) | "o pacote **n** chegou" (**individual**) |
| Perder um ACK | muitas vezes **inofensivo** (o seguinte cobre) | o remetente **não sabe** do pacote → seu timer vai estourar |
| Informação que o remetente tem | só o "maior prefixo contínuo" | exatamente **quais** pacotes foram recebidos |

### 6.1.3 Sinais que o remetente interpreta
- **Chegou ACK novo** → a janela anda (e, se houver dados, ele envia mais).
- **Chegou ACK repetido (duplicado)** → no GBN significa "o receptor continua esperando o mesmo pacote" (há um buraco); o GBN **não age** com isso (só o timeout age).
- **Timer estourou** → houve perda (ou atraso excessivo) → retransmitir. **Aqui GBN e SR diferem.**

### 6.1.4 Por que é necessário numerar com mais de 0/1
Com vários pacotes em voo, um número ambíguo faria o receptor confundir dados (ver §6.4).

---

## 6.2 Go‑Back‑N (GBN)

**Nome:** quando algo falha, o remetente "**volta N**" — recomeça a partir do pacote com problema e **reenvia tudo o que estava na janela**.

### 6.2.1 O remetente — três eventos
1. **Dados da aplicação** (`rdt_send`):
   - se a janela **não está cheia** (`nextseqnum < base + N`): monta o pacote com `nextseqnum`, envia, e **se `base == nextseqnum` (era o primeiro em voo) liga o timer**; depois `nextseqnum++`;
   - se está **cheia**: recusa/segura os dados (a aplicação precisa esperar).
2. **Chegada de `ACK(n)`** (íntegro): `base = n + 1`.
   - se `base == nextseqnum` (nada mais em voo) → **para** o timer;
   - senão → **reinicia** o timer (agora para o novo `base`).
3. **Timeout:** **reinicia** o timer e **reenvia todos** os pacotes de `base` até `nextseqnum − 1`.

> **Um único timer**, que "pertence" ao pacote `base` (o mais antigo sem ACK). Se o mais antigo for confirmado, o timer passa a valer para o próximo mais antigo.

### 6.2.2 O receptor — uma regra, quase sem memória
O receptor guarda **uma única variável**: `expectedseqnum` (o número que ele espera).
- Chega um pacote **íntegro com `seq == expectedseqnum`** → **entrega** à aplicação, envia `ACK(expectedseqnum)` e faz `expectedseqnum++`.
- **Qualquer outro caso** (fora de ordem, corrompido) → **descarta** e **reenvia o `ACK` do último pacote recebido em ordem** (`ACK(expectedseqnum − 1)`).

**Por que descartar os fora de ordem?** Simplicidade: o receptor não precisa de **buffer** nem de lógica de reordenação. O preço é que esses pacotes (que chegaram bem!) terão de ser **reenviados**.
**Por que reenviar o ACK do último em ordem?** Para dizer ao remetente "**ainda estou esperando o próximo**" — é o ACK **duplicado** (útil como sinal e porque pode substituir um ACK perdido).

### 6.2.3 Por que só um timer e por que o remetente "ignora" ACKs repetidos
- Como os ACKs são cumulativos e o recuo vai sempre ao `base`, basta cronometrar o **mais antigo**. Tudo que veio depois será reenviado junto de qualquer modo.
- ACKs repetidos (`ACK(1)` de novo) não trazem informação nova: `base = n+1` não muda. O remetente só reage no **timeout** (o GBN "puro" não faz *fast retransmit*; o **TCP** acrescenta isso).

### 6.2.4 Passo a passo — **Cenário 1: um pacote de dados se perde** (N = 4; pacotes 0–7; o pacote 2 se perde)
Estado inicial: remetente `base=0, nextseqnum=0`; receptor `expectedseqnum=0`.

| Passo | Quem | O que acontece | Remetente (`base`/`next`) | Receptor (`expected`) |
|---|---|---|---|---|
| 1 | Rem. | envia pkt0 (liga timer), pkt1, pkt2, pkt3 → janela cheia | 0 / 4 | 0 |
| 2 | Rede | **pkt2 se perde** | | |
| 3 | Rec. | pkt0 ok → entrega, **ACK0** | | 1 |
| 4 | Rec. | pkt1 ok → entrega, **ACK1** | | 2 |
| 5 | Rec. | pkt3 chega, mas espera 2 → **descarta**, envia **ACK1** | | 2 |
| 6 | Rem. | recebe ACK0 → `base=1`; janela livre → **envia pkt4**; timer reiniciado | 1 / 5 | |
| 7 | Rem. | recebe ACK1 → `base=2`; **envia pkt5**; timer reiniciado (agora p/ pkt2) | 2 / 6 | |
| 8 | Rec. | pkt4 chega → descarta → **ACK1**; pkt5 chega → descarta → **ACK1** | | 2 |
| 9 | Rem. | recebe ACK1 (do pkt3), ACK1 (pkt4), ACK1 (pkt5): **n = 1 → base = 2** (nada muda) → ignora. Janela [2..5] cheia → **espera** | 2 / 6 | |
| 10 | Rem. | **TIMEOUT** do pkt2 → reenvia **pkt2, pkt3, pkt4, pkt5** e reinicia o timer | 2 / 6 | |
| 11 | Rec. | pkt2 ok → ACK2; pkt3 → ACK3; pkt4 → ACK4; pkt5 → ACK5 (todos em ordem) | | 6 |
| 12 | Rem. | ACK2 → base=3 …ACK5 → base=6; timer parado se não há mais em voo; segue com pkt6, pkt7 | 6 / … | |

**Resultado:** só o pkt2 se perdeu, mas houve **4 retransmissões** (2,3,4,5). Pacotes 3, 4, 5 **chegaram corretamente** e foram jogados fora pelo receptor → **desperdício**.

### 6.2.5 **Cenário 2: um ACK se perde** (o cumulativo "cobre")
N = 4; pkt0..pkt3 chegam ao receptor. Os ACKs: `ACK0` **perdido**, `ACK1` **perdido**, `ACK2` **chega**.
- Remetente: recebe ACK2 → `base = 3` (confirma 0, 1, 2 de uma vez). O timer é reiniciado para o pkt3. **Nada é retransmitido.** O ACK é cumulativo, então perder ACKs "antigos" não tem custo **se um posterior chegar**.

### 6.2.6 **Cenário 3: todos os ACKs se perdem**
N = 4; pkt0..pkt3 chegam; ACK0..ACK3 se perdem. **Timeout** → o remetente reenvia **0,1,2,3**. O receptor (agora com `expected = 4`) recebe pacotes **duplicados** (seq < expected) → **descarta** cada um e reenvia **`ACK3`** (o último em ordem). O remetente recebe `ACK3` → `base = 4`.
> Observe: o receptor **nunca entrega duas vezes** ao aplicativo; o número de sequência impede.

### 6.2.7 **Cenário 4: timeout prematuro**
O timer estoura antes de os ACKs chegarem → o remetente reenvia a janela inteira desnecessariamente; o receptor descarta as cópias e re‑ACKa; **correto, mas gasta banda**.

### 6.2.8 Resumo do GBN
| ✔ Vantagens | ✘ Desvantagens |
|---|---|
| Receptor **simplíssimo** (sem buffer, 1 variável) | **Desperdício**: reenvia pacotes que já chegaram |
| 1 timer só | Em links com muitas perdas a vazão despenca (cada perda reenvia N pacotes) |
| ACK cumulativo tolera perda de ACKs | Não tem como reagir antes do timeout (puro) |

---

## 6.3 Selective Repeat (SR)

**Nome:** retransmite **seletivamente** — só os pacotes que realmente se perderam.
Para conseguir isso, o SR "paga" com mais memória e mais lógica: **buffer no receptor**, **ACK individual** e **um timer por pacote**.

### 6.3.1 O remetente — três eventos
1. **Dados da aplicação:** se o próximo número está **dentro da janela** `[base, base + N − 1]`, envia o pacote e **liga um timer só dele**.
2. **Timeout do pacote n:** **reenvia só o pacote n** e reinicia o timer dele.
3. **Chegada de `ACK(n)`** com `n` em `[base, base + N − 1]`: **marca n como recebido** ("confirmado").
   - Se `n == base`: **desliza a janela** para o **próximo pacote ainda não confirmado** (pode pular vários, se os seguintes já estavam marcados).
   - Se `n > base`: apenas marca; a janela **não anda** (há um "buraco" no `base`).

### 6.3.2 O receptor — três faixas de números
O receptor tem **sua própria janela** `[rcv_base, rcv_base + N − 1]` (os números que ele aceita) e **buffer**.

| Chega o pacote `n` | O que o receptor faz | Por quê |
|---|---|---|
| **A) `n` dentro de `[rcv_base, rcv_base+N−1]`** | envia **`ACK(n)`** (sempre). Se **fora de ordem** (`n > rcv_base`): **guarda no buffer**. Se **`n == rcv_base`**: **entrega** à aplicação esse e todos os **consecutivos já guardados**, e **desliza** a janela | aceita qualquer pacote útil; entrega só em ordem |
| **B) `n` em `[rcv_base−N, rcv_base−1]`** (já entregue antes) | **reenvia `ACK(n)`** (e não entrega de novo) | o ACK anterior **pode ter se perdido**; sem esse re‑ACK o remetente jamais confirmaria `n` e a janela dele **travaria** |
| **C) qualquer outro** | **ignora** | não é nem esperado nem duplicata recente |

**Exemplo do porquê da faixa B:** o remetente enviou pkt1; o receptor entregou e mandou ACK1, mas **ACK1 se perdeu**. O timer do pkt1 estoura e o remetente reenvia pkt1. Quando ele chega, o receptor **já passou** por ele (`rcv_base` agora é maior). Se o receptor ignorasse, o remetente reenviaria **para sempre**. Por isso responde **`ACK1`** de novo.

### 6.3.3 Passo a passo — **Cenário 1: um pacote de dados se perde** (mesmo caso do GBN)
N = 4; pacote 2 se perde.

| Passo | Quem | O que acontece | Remetente | Receptor |
|---|---|---|---|---|
| 1 | Rem. | envia pkt0, pkt1, pkt2, pkt3, cada um com **seu timer** | base=0, janela [0..3] | rcv_base=0 |
| 2 | Rede | **pkt2 se perde** | | |
| 3 | Rec. | pkt0 → entrega, **ACK0**; pkt1 → entrega, **ACK1**; `rcv_base = 2` | | 2 |
| 4 | Rec. | pkt3 está na janela [2..5] mas é **fora de ordem** → **guarda**, envia **ACK3** | | 2 (buffer: 3) |
| 5 | Rem. | ACK0 → marca 0, `base=1`, **envia pkt4**; ACK1 → marca 1, `base=2`, **envia pkt5**; ACK3 → **marca 3** (base **não** anda) | base=2, janela [2..5] | |
| 6 | Rec. | pkt4 → guarda, **ACK4**; pkt5 → guarda, **ACK5** | | 2 (buffer: 3,4,5) |
| 7 | Rem. | ACK4, ACK5 → marca 4 e 5. Janela [2..5] **cheia** → espera | | |
| 8 | Rem. | **TIMEOUT só do pkt2** → reenvia **apenas o pkt2** | | |
| 9 | Rec. | pkt2 == rcv_base → **entrega 2, 3, 4, 5** (os guardados); `rcv_base = 6`; **ACK2** | | 6 |
| 10 | Rem. | ACK2 → marca 2; como é o `base`, **desliza até o primeiro não confirmado** → pula 3, 4, 5 (já marcados) → **`base = 6`** | base=6 | |

**Resultado:** **1 retransmissão** (o pkt2). Os pacotes 3, 4, 5 **não** foram reenviados porque o receptor os **guardou** e o remetente **sabia** (ACKs individuais) que eles tinham chegado.

### 6.3.4 **Cenário 2: um ACK se perde** (aqui o SR é menos "tolerante" que o GBN)
N = 4; pkt0..pkt3 chegam. **ACK1 se perde**; ACK0, ACK2, ACK3 chegam.
- Remetente: marca 0 (`base=1`); marca 2 e 3 (a janela **não anda**, porque o `base`=1 não foi confirmado).
- **Timer do pkt1 estoura** → reenvia **só o pkt1**.
- Receptor: `rcv_base` já é 4; o pkt1 está em `[rcv_base−N, rcv_base−1] = [0..3]` → **faixa B**: **não entrega de novo**, reenvia **`ACK1`**.
- Remetente: marca 1 → é o `base` → desliza até 4.
**Custo:** 1 retransmissão. (No GBN, o `ACK2` teria coberto o `ACK1`, sem retransmissão alguma. Cada protocolo tem seu ponto forte.)

### 6.3.5 **Cenário 3: dois pacotes se perdem** (N = 4; perdem‑se pkt1 e pkt3)
Receptor: pkt0 → ACK0 (entrega); pkt2 → guarda, ACK2; (pkt1 e pkt3 perdidos). Remetente: marca 0 e 2; base = 1. **Dois timers independentes** estouram (pkt1 e pkt3) → **dois reenvios** (só eles). Receptor: pkt1 → entrega 1 e 2 (guardado) → `rcv_base=3`; pkt3 → entrega 3 (e os seguintes que já estiverem guardados). Retransmissões: **2** (o mínimo possível).

### 6.3.6 Resumo do SR
| ✔ Vantagens | ✘ Desvantagens |
|---|---|
| **Mínimo de retransmissões** | Receptor com **buffer** e lógica de janela |
| Remetente sabe **exatamente** o que chegou | **Um timer por pacote** (mais custo) |
| Eficiente em links ruidosos | Perder um ACK **pode** causar retransmissão (não há cumulatividade) |

---

## 6.4 O "dilema da janela" — por que N não pode ser qualquer valor

Os números de sequência são **finitos** e **reciclados** (ex.: com 2 bits temos 0,1,2,3,0,1,2,3,…). Se a janela for grande demais, o receptor **não consegue distinguir** um pacote **novo** de uma **retransmissão antiga** com o mesmo número.

### 6.4.1 SR com N grande demais (o exemplo do slide)
Espaço 0–3 (4 números), **N = 3**.
1. Remetente envia 0, 1, 2. Receptor recebe os três e **entrega**; sua janela passa a ser **[3, 0, 1]**.
2. **Todos os ACKs se perdem.**
3. Timeout: o remetente reenvia o **pkt 0 (antigo)**.
4. O receptor vê "0": está **dentro** da janela [3, 0, 1] → **aceita como pacote novo!** → a aplicação recebe dado **duplicado/errado**.
**Regra do SR:** `N ≤ (tamanho do espaço de números) / 2`. Com 4 números: N ≤ 2 → a janela do receptor [2,3] e a antiga [0,1] **não se sobrepõem**.

### 6.4.2 GBN: por que `N ≤ 2ᵏ − 1`
Espaço 0–3 (k = 2), **N = 4 (errado)**:
1. Remetente envia 0, 1, 2, 3; o receptor recebe tudo e passa a esperar **o 0** (próximo ciclo). **Todos os ACKs se perdem.**
2. Timeout → o remetente reenvia **0** (antigo).
3. O receptor **espera** o 0 → **aceita como novo!** ✘.
Com **N = 3** (= 2ᵏ − 1) isso não ocorre. No GBN o receptor só tem **1** número "válido" por vez, por isso a restrição é mais frouxa que a do SR.

| Protocolo | Limite da janela (espaço de numeração = M) |
|---|---|
| Bit alternante | N = 1 (M = 2) |
| **GBN** | **N ≤ M − 1** (M = 2ᵏ) |
| **SR** | **N ≤ M / 2** |

---

## 6.5 Comparação direta (mesmo cenário: pkt2 perdido, N = 4, pkts 0–5)

| | **GBN** | **SR** |
|---|---|---|
| Receptor recebe 3, 4, 5 (fora de ordem) | **descarta**; responde `ACK1` a cada um | **guarda**; responde `ACK3`, `ACK4`, `ACK5` |
| Remetente sabe que 3,4,5 chegaram? | **não** (só vê `ACK1` repetido) | **sim** (ACKs individuais) |
| Quem dispara a retransmissão | **timer único** (base = pkt2) | **timer do pkt2** |
| Pacotes reenviados | **2, 3, 4, 5** (4) | **2** (1) |
| ACKs que o remetente recebe depois | ACK2, ACK3, ACK4, ACK5 | ACK2 (e o `base` salta para 6) |
| Memória no receptor | quase nenhuma | buffer + janela |

**Como o TCP se encaixa** (para o §7): ACK **cumulativo** como o GBN, **um único timer**, mas no timeout reenvia **só um segmento** (como o SR), e o receptor real **guarda** os fora de ordem (e pode usar **SACK**). O TCP é um **híbrido**.

---

## 6.6 Como resolver uma questão de "trace" de GBN/SR (método)

1. **Anote o estado inicial:** N, `base`, `nextseqnum` (remetente); `expectedseqnum` (GBN) ou `rcv_base` (SR) e o buffer (SR).
2. **Processe os eventos na ordem do tempo** (envios, chegadas, perdas, timeouts). Para cada **chegada ao receptor** decida: GBN → "é o esperado? entrego+ACK; senão descarta + re‑ACK do último". SR → "está em qual faixa (A/B/C)?".
3. Para cada **chegada de ACK ao remetente**: GBN → `base = n+1`, mova a janela, reinicie/pare o timer. SR → marque `n`; se `n == base`, deslize até o primeiro não marcado.
4. **Só no timeout** (ou conforme o enunciado) decida o que reenviar: GBN → **toda a janela** (`base`..`next−1`); SR → **só o pacote do timer**.
5. **Conte** o que o enunciado pedir (retransmissões, ACKs, estado final).

---

## 6.7 Exercícios resolvidos

**E1. (ACK perdido no GBN)** N = 3, pacotes 0..5. O ACK0 se perde; os demais chegam. Há retransmissão?
**R:** Não. `ACK1` é cumulativo (confirma 0 e 1): `base = 2`. Nenhum timeout de 0 ocorre, pois o timer é reiniciado quando o `base` avança.

**E2. (Pacote perdido, contagem)** N = 4, pacotes 0..7, o pkt 1 se perde (sem outras perdas; os ACKs chegam). Quantos pacotes o remetente reenvia no **GBN** e no **SR**?
**R:** Enviados antes do timeout: 0,1,2,3 e (após ACK0) 4. **GBN:** timeout do pkt1 → reenvia **1,2,3,4** (4). **SR:** reenvia **só o 1** (1).

**E3. (Dois pacotes perdidos no SR)** N = 4, perdem‑se pkt1 e pkt3. Quantas retransmissões? **R:** 2 (um timer para cada; cada pacote perdido é reenviado uma única vez). No GBN, o timeout do pkt1 reenviaria **toda a janela a partir do 1** (1, 2, 3, 4…), isto é, 3 ou mais pacotes só para recuperar esses dois.

**E4. (Qual protocolo?)** Um receptor responde: `ACK0, ACK1, ACK1, ACK1, ACK1`. E outro: `ACK0, ACK1, ACK3, ACK4, ACK5`. Quais são?
**R:** O 1º = **GBN** (re‑ACK do último em ordem; pacotes descartados). O 2º = **SR** (ACKs individuais; o 2 está faltando mas 3,4,5 foram aceitos e guardados).

**E5. (ACK fora da janela)** *(lista de revisão, Q2 a e b)* Mostre que é possível, em SR e GBN, o remetente receber um ACK fora da janela corrente.
**R:** N = 3: envia 1,2,3; o receptor responde ACK1,2,3; os ACKs demoram e o timer estoura → o remetente **reenvia 1,2,3**; o receptor reenvia ACK1,2,3 (duplicatas); chegam os ACKs da 1ª rodada → janela vai a {4,5,6}; depois chegam os da 2ª rodada → referem‑se a 1,2,3 → **fora da janela**. Vale para GBN e SR.

**E6. (Janela 1)** Mostre que, com N = 1, GBN, SR e bit alternante são iguais.
**R:** Um pacote em voo, um timer, ACK de um pacote, timeout reenvia esse pacote; o receptor só aceita o esperado e re‑ACKa duplicatas; 0/1 bastam (SR: M ≥ 2N = 2; GBN: N ≤ M−1 = 1).

**E7. (Tamanho máximo da janela)** Seq de **3 bits** (M = 8). Qual o maior N no GBN? E no SR? **R:** GBN: **7**. SR: **4**.

**E8. (Janela para saturar o enlace)** `R = 100 Mbps`, `L = 1250 B (10 000 bits)`, `RTT = 40 ms`. Qual N satura o enlace? **R:** `L/R = 0,1 ms`; `N ≈ (RTT + L/R)/(L/R) = 40,1/0,1 ≈ 401` pacotes. Com `N = 40`, `U ≈ 40·0,1/40,1 ≈ 10 %`.

**E9. (Timer único no GBN)** Por que o GBN usa um único timer? **R:** Porque o recuo é sempre ao pacote mais antigo sem ACK (`base`); tudo que veio depois será reenviado junto, então basta cronometrar o `base`.

**E10. (Por que o SR precisa reenviar ACK de pacotes já entregues?)** **R:** Porque o ACK anterior pode ter sido perdido; sem o re‑ACK, o remetente reenviaria indefinidamente e a janela dele não avançaria (faixa B).

---

## 6.8 Perguntas de prova sobre este tema — respostas curtas prontas

- **Diferença entre GBN e SR?** → ACK cumulativo × individual; 1 timer × 1 por pacote; receptor sem buffer (descarta) × com buffer; retransmite a janela × só o perdido.
- **Por que o SR é melhor em links com perda?** → retransmite só o perdido.
- **Por que o GBN é mais simples?** → receptor sem buffer, só `expectedseqnum`, 1 timer.
- **O que é ACK cumulativo?** → `ACK(n)` confirma todos os pacotes até n.
- **O que o receptor GBN faz com um pacote fora de ordem?** → descarta e reenvia o ACK do último em ordem.
- **O que o receptor SR faz?** → ACK individual; guarda se fora de ordem; entrega em ordem; re‑ACK de pacotes já entregues.
- **Qual o limite de janela em cada um?** → GBN: `2ᵏ−1`; SR: `2ᵏ/2` (metade do espaço).
- **Por que numeração de 0/1 não basta com pipelining?** → vários pacotes em voo geram ambiguidade (§6.4).
- **Bit alternante = GBN/SR com N=1?** → sim, E6.

---

# 7. TCP: ACKs, números de sequência e timers

O TCP é o rdt "de verdade": pipelining + ACK cumulativo + **um timer**, mais detalhes práticos. Ele mistura ideias: ACK **cumulativo** (como GBN), mas retransmite **um segmento só** (como SR) e o receptor normalmente **guarda** os fora de ordem (e usa **SACK**, *além dos slides*).

## 7.1 O TCP numera **bytes**, não pacotes
- **Número de sequência (Seq)** do segmento = número do **primeiro byte** de dados que ele carrega.
- Os bytes vão sendo numerados em sequência a partir de um **ISN** (número inicial escolhido aleatoriamente no handshake).
- Um segmento com `Seq=1000` e 500 bytes carrega os bytes **1000 a 1499**. O **próximo** segmento (se em ordem) tem `Seq=1500`.

**Regras para memorizar:**
```
Seq do próximo segmento (em ordem)  = Seq atual + nº de bytes de dados
Tamanho do segmento                 = Seq_seguinte − Seq_atual
```

## 7.2 O número de ACK = **próximo byte que o receptor espera**
- `ACK = x` significa: "recebi, **em ordem**, todos os bytes **até x−1**; **estou esperando o byte x**".
- É **cumulativo**: um único ACK confirma tudo antes dele.
- **Não** é "o último byte recebido". É o último **+1**.
- Em ordem: `ACK = Seq recebido + nº de bytes` do segmento recebido.

> **Cuidado clássico:** o campo ACK de um segmento A→B refere-se aos bytes que **B enviou a A**. Ele **não** é `Seq+len` do próprio segmento de A. Por isso, "Seq=38 com 4 bytes ⇒ ACK=42 no mesmo segmento" é **FALSO**; **42** é o ACK que **B** manda de volta.

## 7.3 Piggybacking e ACK "puro"
Um segmento pode levar **dados e ACK ao mesmo tempo** (*piggybacking* — "carona"): ex. Telnet: o usuário digita `C` (A→B: Seq=42, ACK=79); o servidor devolve eco e confirma no mesmo segmento (Seq=79, ACK=43, dado='C'). Se o receptor **não tem dados** para mandar, manda um **segmento só de ACK** (sem payload).

## 7.4 Quando o receptor envia ACK (regras RFC 1122/2581)
| Evento no receptor | Ação |
|---|---|
| Segmento **em ordem**, tudo anterior já confirmado | **ACK atrasado**: espera até **500 ms** pelo próximo; se não vier, envia ACK |
| Segmento **em ordem**, havendo outro esperando ACK | **um único ACK cumulativo imediato** (cobre os dois) |
| Segmento **fora de ordem** (maior que o esperado → "buraco") | **ACK duplicado imediato**, com o número do byte que **ainda falta** |
| Segmento que **preenche** o buraco (total ou parcial) | ACK **imediato** |
**Por que o dup ACK é imediato?** Porque ele é um **sinal** ao remetente: "algo faltou!". Esperar 500 ms desperdiçaria o sinal.

## 7.5 O remetente: eventos e timer
O remetente tem **um único timer** (para o segmento **mais antigo** ainda sem ACK). Variáveis: `SendBase` (menor byte não confirmado), `NextSeqNum` (próximo byte a enviar).
1. **Dados da aplicação:** cria segmento com `Seq = NextSeqNum`; `NextSeqNum += len`; se o timer não está rodando, **liga**.
2. **Timeout:** retransmite **só** o segmento não confirmado de **menor Seq** e reinicia o timer (e dobra o intervalo — *backoff*).
3. **ACK com valor y:** se `y > SendBase` → `SendBase = y`; se ainda há pendentes, **reinicia** o timer; senão para. Se `y == SendBase` → é **ACK duplicado** (contador +1); com **3** duplicados → **fast retransmit**.

## 7.6 Como o TCP escolhe o timeout (RTT)
- **SampleRTT:** tempo entre enviar um segmento e chegar o ACK dele. (**Karn:** ignora amostras de segmentos **retransmitidos**, pois é ambíguo a qual envio o ACK pertence.)
- `EstimatedRTT = 0,875·EstimatedRTT + 0,125·SampleRTT`
- `DevRTT = 0,75·DevRTT + 0,25·|SampleRTT − EstimatedRTT|`
- `TimeoutInterval = EstimatedRTT + 4·DevRTT`
- **Timeout real ⇒ dobra** o intervalo (*backoff exponencial*) até chegar ACK novo.
**Exemplo:** `Est=100`, `Dev=20`, `Sample=180` ms → `Dev' = 0,75·20 + 0,25·80 = 35`; `Est' = 0,875·100 + 0,125·180 = 110`; `Timeout = 110 + 4·35 = 250 ms`.
**Dilema:** timeout curto → retransmissão à toa; longo → reage devagar a perdas reais.

---

# 8. TCP: **todos os cenários de problema** (com números)

Convenção: A envia dados, B responde. `Seq=100,20B` = segmento que começa no byte 100 e carrega 20 bytes (bytes 100–119).

### Cenário 1 — Normal
```
A ──Seq=1000,500B──►  B: em ordem → ACK=1500 (pode ser atrasado até 500 ms)
A ◄──ACK=1500──
```

### Cenário 2 — Segmento de dados **perdido**, sem mais nada em voo
```
A ──Seq=1000,500B──X                (perdido)
   ... timer estoura ...
A ──Seq=1000,500B──►  (retransmissão) → B: ACK=1500
```
A reação: **timeout** → retransmite só o mais antigo; (congestionamento: `ssthresh=cwnd/2`, `cwnd=1`).

### Cenário 3 — Segmento perdido **com outros segmentos depois** → ACKs duplicados e **Fast Retransmit**
A envia 5 segmentos de 100 B: `Seq=1000, 1100, 1200, 1300, 1400`. O de `1100` se perde.
```
A ──Seq=1000,100B──►  B: ACK=1100  (novo ACK)
A ──Seq=1100,100B──X
A ──Seq=1200,100B──►  B: fora de ordem (esperava 1100) → ACK=1100 (dup 1)
A ──Seq=1300,100B──►  B: ACK=1100 (dup 2)
A ──Seq=1400,100B──►  B: ACK=1100 (dup 3)
A: recebeu 3 duplicados (4 ACKs iguais) → RETRANSMITE Seq=1100 antes do timeout
A ──Seq=1100,100B──►  B: agora tem 1100..1499 → ACK=1500 (cumulativo!)
```
**Detalhes que caem:**
- O **1º** ACK=1100 é o normal (confirma o 1000); os **3 seguintes** são os **duplicados**.
- B **guarda** 1200–1499 (buffer) — por isso o ACK final salta para **1500**, não 1200.
- Por que **3** e não 1? **Reordenação** de rede pode gerar 1–2 duplicados sem perda real; o 3º é forte indício.
- Reação de congestionamento (Reno): `ssthresh = cwnd/2`, `cwnd = ssthresh`, segue em congestion avoidance (vs. timeout, onde `cwnd=1`).

### Cenário 4 — **ACK perdido**, mas o ACK seguinte **cobre** (cumulativo)
```
A ──Seq=92,8B──►     B: ACK=100   ──X (perdido)
A ──Seq=100,20B──►   B: ACK=120   ──────► chega antes do timeout
A: ACK=120 > SendBase(92) → tudo até 119 confirmado. NENHUMA retransmissão.
```
Moral: **ACK cumulativo torna a perda de um ACK inofensiva** se um posterior chegar a tempo.

### Cenário 5 — **ACK perdido** e nada o cobre
```
A ──Seq=92,8B──►     B: ACK=100   ──X (perdido)
   ... timeout ...
A ──Seq=92,8B──►     B: já tinha → DUPLICATA: descarta e reenvia ACK=100
A ◄──ACK=100──       A: SendBase=100
```
O TCP descarta a duplicata pelo **número de sequência** (B espera 100; recebeu 92 < 100).

### Cenário 6 — **Timeout prematuro**
```
A ──Seq=92,8B──►
A ──Seq=100,20B──►
   ... timeout do seg 92 estoura (ACK ainda a caminho) ...
A ──Seq=92,8B──►     (retransmissão desnecessária)
A ◄──ACK=100──       A: SendBase=100 (reinicia timer)
A ◄──ACK=120──       A: SendBase=120 (confirma tudo)
B recebe a duplicata de 92: descarta e re-ACK=120
A ◄──ACK=120──       (duplicado; ignorado)
```
Consequência: **tráfego inútil**, mas **correto**. (Solução: timeout adaptativo, § 7.6.)

### Cenário 7 — **Fora de ordem sem perda** (reordenação)
```
Segmentos 1000, 1100, 1200 saem; chegam na ordem 1000, 1200, 1100.
B: ACK=1100 ; ACK=1100 (dup, 1200 chegou antes) ; ao chegar 1100 → ACK=1300 (preencheu o buraco)
```
Só **1 duplicado** → não dispara fast retransmit (precisa de 3). Tudo se resolve sozinho.

### Cenário 8 — **Segmento corrompido**
O checksum TCP falha no receptor → o segmento é **descartado sem aviso** (sem NAK no TCP). Para o remetente é **idêntico a uma perda** → Cenário 2 ou 3.

### Cenário 9 — **Duplicata criada pela rede**
Chega o mesmo segmento duas vezes. B vê `Seq` menor que o esperado (já recebido) → descarta e re‑ACKa.

### Cenário 10 — **Receptor lento** (controle de fluxo)
B anuncia `rwnd` pequeno nos ACKs; quando o buffer enche, `rwnd=0`. A **para** e manda **segmentos de 1 byte** de sondagem; ao ler dados, B anuncia `rwnd>0` e A retoma. Sem isso, um ACK "abre janela" perdido travaria a conexão.

### Cenário 11 — **Perda de SYN / SYN‑ACK** *(além dos slides)*
Também retransmitidos por timeout (o SYN é tratado como dado com número de sequência). O servidor só aloca estado definitivo ao receber o 3º segmento do handshake.

### O diagrama típico de prova (P15 Q8d / TT Q1d)
*A envia 127(70 B) e 197(50 B); 1º ACK perdido; 2º ACK chega depois do timeout do 1º.*
```
A ──Seq=127,70B──►   B: ACK=197   ──X
A ──Seq=197,50B──►   B: ACK=247   ───────►(chega após o timeout)
   timeout do seg 127 → A ──Seq=127,70B──► (retransmissão)
A ◄──ACK=247──  (SendBase=247)
B recebe duplicata de 127 → ACK=247 (A ignora)
```
Desenhe: segmentos (127,70), (197,50), retransmissão (127,70); ACKs 197 (perdido), 247, 247.
*(Se o ACK=247 chegasse **antes** do timeout, não haveria retransmissão — Cenário 4.)*

---

# 9. Fluxo e congestionamento vistos pelos ACKs

O ACK não carrega só "confirmação": ele **alimenta** duas janelas que limitam o remetente — **`rwnd`** (fluxo; protege o receptor) e **`cwnd`** (congestionamento; protege a rede). O remetente nunca pode ter em voo mais que **`min(cwnd, rwnd)`**.

## 9.1 Controle de fluxo (`rwnd`) — em cada ACK
- `rwnd = RcvBuffer − (LastByteRcvd − LastByteRead)` = **espaço livre** no buffer do receptor.
- O receptor o coloca no cabeçalho de **todo** segmento (inclusive ACKs).
- O remetente garante `LastByteSent − LastByteAcked ≤ rwnd`.
- Aplicação lenta → buffer enche → `rwnd` cai → `rwnd = 0` → remetente para e **sonda com 1 byte**.
- **Consequência:** bytes sem ACK ≤ `rwnd` ≤ buffer (afirmação **V** nas provas); `rwnd` **varia** (afirmação "rwnd nunca muda" é **F**).

---

## 9.2 Controle de congestionamento — a explicação completa

### 9.2.0 O problema e a ideia (em linguagem simples)
Imagine uma **rodovia** (a rede) por onde passam **vários caminhões** (conexões TCP). Cada motorista (remetente) **não vê a estrada inteira**, só vê se **os recibos voltam** (ACKs) e se **voltam no tempo normal**. Se todos acelerarem ao máximo, a estrada **congestiona**: forma‑se fila nos roteadores (**atraso**) e, com a fila cheia, pacotes são **descartados** (**perda**). Pior: as retransmissões **aumentam a carga** e geram **mais perda** (colapso).

**O IP não avisa nada** ("melhor esforço"). Logo, **cada remetente TCP precisa descobrir sozinho** quanto pode enviar, e **ajustar** isso continuamente:
- **Subir** a taxa enquanto tudo vai bem (para aproveitar a banda);
- **Descer** rápido quando percebe sinais de congestionamento (para aliviar a rede);
- e fazer isso de um jeito que **várias conexões dividam o enlace de forma justa**.

O mecanismo que faz isso é o **controle de congestionamento do TCP**, baseado em **uma janela que cresce e encolhe**: a **`cwnd`**.

### 9.2.1 As variáveis — o que cada uma **é**, quem controla e quando muda

| Variável | O que significa (em português claro) | Quem a calcula | Valor inicial | Quando muda |
|---|---|---|---|---|
| **MSS** | **Maior pedaço de dados** de um segmento (a "unidade" em que se conta a janela). Ex.: 1460 bytes | fixo na conexão | — | não muda |
| **`cwnd`** (*congestion window*, janela de congestionamento) | **Quantos bytes o remetente pode ter "no ar" (enviados e sem ACK)** segundo a **sua estimativa de quanto a rede aguenta** | o **remetente** (sozinho) | **1 MSS** | **a cada ACK** (cresce) e **a cada perda** (encolhe) |
| **`ssthresh`** (*slow start threshold*, limiar) | **Ponto de mudança de estratégia**: abaixo dele cresce‑se rápido (exponencial); acima, devagar (linear). É a **"memória" do TCP**: guarda **metade** da janela em que **houve problema** da última vez, como a marca de "até aqui era seguro" | o **remetente** | **grande** (arbitrário: não limita no começo) | **só na perda**: `ssthresh = cwnd/2` |
| **`rwnd`** (*receive window*) | espaço livre no buffer do **receptor** | o **receptor** (avisa no cabeçalho) | espaço do buffer | a cada segmento recebido do outro lado |
| **Janela efetiva** | **o que o remetente realmente pode ter em voo** | — | — | `min(cwnd, rwnd)` |
| **Contador de ACKs duplicados** (`dupACKcount`) | quantos ACKs **repetidos** (mesmo número) chegaram seguidos | o remetente | 0 | +1 a cada ACK duplicado; **zera** com ACK novo; **3** dispara *fast retransmit* |
| **Fase/estado** | em qual "modo" o TCP está: **Slow Start**, **Congestion Avoidance** (e **Fast Recovery** no Reno) | o remetente | Slow Start | veja a máquina em §9.2.7 |
| **RTO / timer** | tempo máximo de espera por um ACK antes de declarar "perda grave" | o remetente | — | recalculado por `EstimatedRTT + 4·DevRTT`; **dobra** em timeout |

**Como ler `cwnd`:** é medida em **bytes** ou, mais comumente nas provas, em **número de MSS** ("`cwnd = 8` quer dizer 8 segmentos de tamanho máximo").
**Como ler `ssthresh`:** é um **número com a mesma unidade** de `cwnd`. Comparar `cwnd` com `ssthresh` decide a **fase**.

### 9.2.2 Por que usar uma **janela** (e como ela vira "taxa")
O remetente só pode **enviar um novo segmento quando sobra espaço** na janela, isto é, quando algum ACK volta liberando espaço. Isso cria o **"relógio de ACKs"**: **a chegada dos ACKs "puxa" novos envios**, o que **auto‑regula** o ritmo à velocidade com que a rede realmente entrega.

**Taxa de envio aproximada:**
```
taxa ≈ cwnd / RTT      (bytes por segundo)
```
Exemplo: `cwnd = 10 MSS`, `MSS = 1460 B`, `RTT = 100 ms` → 10·1460 B por 0,1 s = **146 000 B/s ≈ 1,17 Mbps**.
→ Para **dobrar a taxa**, dobra‑se `cwnd` (com o RTT igual). Por isso **mexer na `cwnd` = mexer na velocidade**.

### 9.2.3 Como o remetente "enxerga" a rede: três sinais (semáforo)

| Sinal | O que o remetente observa | Interpretação | Gravidade |
|---|---|---|---|
| 🟢 **ACKs novos chegando normalmente** | a janela anda, tudo confirmado | rede com folga → pode **aumentar** | — |
| 🟡 **3 ACKs duplicados** | um segmento sumiu, **mas os seguintes chegaram** (por isso o receptor repete o ACK) | a rede **ainda entrega**; congestionamento **leve** | moderada |
| 🔴 **Timeout** | **nenhum ACK** voltou no tempo | quase nada passa; congestionamento **severo** | grave |

> O IP não diz "estou congestionado". O TCP **conclui** isso pela **perda** (timeout ou ACKs duplicados). (Atraso crescente também é indício, mas os slides usam a perda.)

### 9.2.4 Fase 1 — **Slow Start** (partida lenta)

**Situação:** a conexão acabou de começar (ou acabou de sofrer um timeout). O TCP **não sabe** quanto a rede suporta. Começar timidamente é seguro; mas crescer **de um em um** demoraria horas. Solução: **crescer exponencialmente** até achar o limite.

**Regras:**
- `cwnd = 1 MSS` no início.
- **A cada ACK novo recebido: `cwnd += 1 MSS`.**
- Permanece nessa fase **enquanto `cwnd < ssthresh`**.

**Por que isso "dobra a cada RTT"?** Em cada rodada (1 RTT) o remetente envia `cwnd` segmentos e recebe `cwnd` ACKs; como **cada ACK soma 1 MSS**, no fim da rodada `cwnd` **dobrou**:
```
Rodada 1 (cwnd=1):  envia 1 segmento  → chega 1 ACK  → cwnd = 2
Rodada 2 (cwnd=2):  envia 2 segmentos → chegam 2 ACKs → cwnd = 4
Rodada 3 (cwnd=4):  envia 4 segmentos → chegam 4 ACKs → cwnd = 8
Rodada 4 (cwnd=8):  envia 8 segmentos → chegam 8 ACKs → cwnd = 16   ← exponencial
```
**"Paradoxo do nome":** é chamada de **lenta** porque **começa de 1**; mas o crescimento é **muito rápido** (1, 2, 4, 8, 16…).

**Como termina:** (1) `cwnd` **atinge/ultrapassa `ssthresh`** → passa para Congestion Avoidance (na prática, o crescimento é **limitado a `ssthresh`**: se faltarem 3 para o limiar e a regra daria +8, para‑se em `ssthresh`); (2) ocorre **perda** → reação da §9.2.6.

### 9.2.5 Fase 2 — **Congestion Avoidance** (prevenção de congestionamento)

**Situação:** `cwnd ≥ ssthresh`. Estamos **perto** do ponto onde antes deu problema; arriscar dobrar seria perigoso. Então **cresce‑se com cuidado**: **+1 MSS por RTT** (linear), "sondando" a banda.

**Regra por ACK:** `cwnd += MSS · (MSS / cwnd)` (isto é, cada ACK soma uma **fração** de MSS).
**Por que dá +1 MSS por RTT?** Numa rodada chegam `cwnd/MSS` ACKs; cada um soma `MSS²/cwnd`; o total é `(cwnd/MSS)·(MSS²/cwnd) = MSS`.
Exemplo: `cwnd = 10 MSS` → cada ACK soma **0,1 MSS**; os 10 ACKs da rodada somam **1 MSS** → `cwnd = 11`.

**Resultado (aumento aditivo — o "AI" do AIMD):**
```
Rodada: cwnd = 10 → 11 → 12 → 13 → ...    (+1 por RTT)
```
Dura **até aparecer um sinal 🟡 ou 🔴** (perda).

### 9.2.6 O que acontece quando há perda — **as variáveis mudando**

**Regra de ouro:** `ssthresh = cwnd/2`, onde `cwnd` é **o valor no momento da perda** (**não** metade do `ssthresh` anterior).
Depois, **conforme o tipo de perda**:

| Evento | `ssthresh` | `cwnd` | Fase seguinte | Também |
|---|---|---|---|---|
| 🟡 **3 ACKs duplicados** (**Reno**) | `cwnd/2` | **`ssthresh`** (corta pela metade) | **Congestion Avoidance** (linear) | **fast retransmit**: reenvia o segmento perdido já; "fast recovery" |
| 🔴 **Timeout** | `cwnd/2` | **1 MSS** | **Slow Start** (volta a exponencial) | retransmite o mais antigo; **RTO dobra** (backoff); zera `dupACKcount` |
| 🟡/🔴 **Qualquer perda — Tahoe** | `cwnd/2` | **1 MSS** | **Slow Start** | (versão antiga: não distingue) |

**Por que `cwnd/2`?** É a **redução multiplicativa** ("MD" do AIMD): **metade** é um corte **forte o bastante** para **esvaziar as filas** dos roteadores rapidamente, mas **não** tão brutal quanto zerar. O `ssthresh` guarda essa metade como **"o valor que parecia seguro"**.
**Por que 3 dups é tratado mais suave que timeout?** Com 3 ACKs duplicados **ainda chegam segmentos ao destino** (ACKs estão voltando) → a rede **funciona, só está sobrecarregada**. Timeout = **nada voltou** → **muito mais grave** → recomeça de 1 e usa **slow start**.

> **Detalhe (além dos slides):** no livro/RFC, o *fast recovery* usa `cwnd = ssthresh + 3·MSS` e infla `cwnd` +1 MSS por ACK duplicado adicional, voltando a `ssthresh` quando chega o ACK novo. **Os slides simplificam: `cwnd = ssthresh`.** Use o dos slides na prova.

### 9.2.7 A máquina de estados completa (resumo de tudo)

| Estado | Evento | Ação nas variáveis | Próximo estado |
|---|---|---|---|
| **Slow Start** | ACK novo | `cwnd += MSS`; `dupACKcount = 0`; envia o que a janela permitir | SS |
| | `cwnd ≥ ssthresh` | — | **Congestion Avoidance** |
| | ACK duplicado | `dupACKcount++` | SS |
| | **3 dups** | `ssthresh = cwnd/2`; `cwnd = ssthresh`; retransmite o perdido | **CA** (Reno) |
| | **Timeout** | `ssthresh = cwnd/2`; `cwnd = 1 MSS`; retransmite; `dupACKcount = 0` | SS |
| **Congestion Avoidance** | ACK novo | `cwnd += MSS·(MSS/cwnd)` (≈ +1 MSS/RTT) | CA |
| | ACK duplicado | `dupACKcount++` | CA |
| | **3 dups** | `ssthresh = cwnd/2`; `cwnd = ssthresh`; retransmite | CA |
| | **Timeout** | `ssthresh = cwnd/2`; `cwnd = 1 MSS`; retransmite | **SS** |

### 9.2.8 Exemplo completo — as variáveis se movendo no tempo
Parâmetros: `ssthresh` inicial = **16**; unidades em MSS; um valor por RTT (cwnd **no início** da rodada).

| RTT | `cwnd` | `ssthresh` | Fase | Evento |
|---|---|---|---|---|
| 0 | 1 | 16 | SS | início |
| 1 | 2 | 16 | SS | |
| 2 | 4 | 16 | SS | |
| 3 | 8 | 16 | SS | |
| 4 | **16** | 16 | SS→**CA** | `cwnd` atinge ssthresh |
| 5 | 17 | 16 | CA | +1 por RTT |
| 6 | 18 | 16 | CA | |
| 7 | 19 | 16 | CA | |
| 8 | **20** | 16 | CA | **3 ACKs duplicados** na rodada |
| 9 | **10** | **10** | CA | `ssthresh = 20/2 = 10`; `cwnd = 10` (Reno) |
| 10 | 11 | 10 | CA | |
| 11 | 12 | 10 | CA | |
| 12 | 13 | 10 | CA | |
| 13 | **14** | 10 | CA | **TIMEOUT** |
| 14 | **1** | **7** | SS | `ssthresh = 14/2 = 7`; `cwnd = 1` |
| 15 | 2 | 7 | SS | |
| 16 | 4 | 7 | SS | |
| 17 | **7** | 7 | SS→CA | SS não passa de ssthresh (+8 viraria 8, limita a 7) |
| 18 | 8 | 7 | CA | volta ao +1 por RTT |

**Desenho do "dente de serra"** (cwnd ao longo do tempo):
```
cwnd:  1 → 2 → 4 → 8 → 16 ↗ 17 → 18 → 19 → 20 ↘ 10 ↗ 11 → 12 → 13 → 14 ↘ 1 → 2 → 4 → 7 ↗ 8
fase:  └── SS (exponencial) ──┘ └──── CA (+1/RTT) ────┘ 3dups └──── CA (+1/RTT) ────┘ TO └─ SS ─┘ CA
```
*(Leia da esquerda para a direita, um valor por RTT: subida exponencial, subida linear, **corte pela metade** (3 dups), subida linear, **queda a 1** (timeout), exponencial até o `ssthresh` e linear de novo — o "dente de serra".)*
**Se fosse TCP Tahoe** na perda do RTT 8 (cwnd = 20): `ssthresh = 10`, `cwnd = 1` → 1, 2, 4, 8, 10(limite), 11, 12… — **muito mais lento** que o Reno (que voltou direto a 10).

### 9.2.9 Por que isso **preserva a rede** (o argumento do AIMD)

1. **Aumento aditivo (devagar):** o remetente **sonda** a banda sem causar choques; só passa do limite por pouco e **quando passa, os pacotes extras são os que se perdem**.
2. **Redução multiplicativa (rápida):** ao primeiro sinal de perda, **corta pela metade**, aliviando rápido as filas. (Se recuasse devagar, o congestionamento persistiria e **todos** perderiam pacotes.)
3. **Sem coordenação central:** cada conexão aplica a mesma regra e a rede **se equilibra**.
4. **Evita o colapso por congestionamento** (os 3 "custos" do slide A6: retransmissões adicionais, cópias desnecessárias e capacidade desperdiçada nos saltos anteriores).

**Justiça (fairness) com números:** duas conexões dividindo um enlace de capacidade 12. Começam **desiguais** (A=8, B=2).
| Passo | A | B | Soma | Evento |
|---|---|---|---|---|
| 1 | 8 | 2 | 10 | ok |
| 2 | 9 | 3 | 12 | ok (+1 cada) |
| 3 | 10 | 4 | 14 | **> 12 → perda**: ambas ÷2 |
| 4 | 5 | 2 | 7 | |
| 5 | 6 | 3 | 9 | |
| 6 | 7 | 4 | 11 | |
| 7 | 8 | 5 | 13 | **perda** → ÷2 |
| 8 | 4 | 2,5 | 6,5 | |
A **diferença** entre A e B caiu de **6 → 3 → 1,5 → …**: **cada corte pela metade reduz a diferença pela metade**, enquanto o aumento aditivo (+1 para ambas) **não** a aumenta. Por isso as conexões **convergem** para taxas **iguais** (e a soma oscila em torno da capacidade).
**Burla (slide A6 s.18):** UDP não faz AIMD (não recua) e **conexões TCP em paralelo** (11 novas contra 9 existentes → 11/20 da banda) **roubam** parte da justiça.

### 9.2.10 Interação com o controle de fluxo
Janela efetiva = **`min(cwnd, rwnd)`**.
- `cwnd = 20`, `rwnd = 8` → o remetente pode ter **8** em voo (**o receptor** é o limite).
- `cwnd = 6`, `rwnd = 50` → pode ter **6** (**a rede** é o limite).
Quem for menor **manda**. (O mesmo ACK traz a informação para as duas janelas: o ACK novo faz `cwnd` crescer e traz o `rwnd` atualizado.)

### 9.2.11 Efeitos sobre a vazão
- **Vazão instantânea:** `cwnd/RTT`.
- **Vazão média em regime (AIMD, sem slow start):** a janela oscila entre `W/2` e `W`; a média é **`0,75·W/RTT`** (W = janela no momento da perda).
  Exemplo: `W = 40 MSS`, `MSS = 1500 B`, `RTT = 100 ms`: `0,75·40·1500 B·8 / 0,1 s = 3,6 Mbps`.
- **Em função da perda L (Mathis):** **`vazão ≈ 1,22·MSS / (RTT·√L)`**. Perda ×4 → vazão ÷2 (por causa da √); RTT maior → vazão menor (cada +1 MSS leva 1 RTT).
- *(além dos slides)* Conexões com RTT longo crescem mais devagar (+1 por RTT) e acabam com **menos** banda que as de RTT curto — por isso o **CUBIC** (A6 s.19–21), que depende do **tempo** desde a última perda e não do RTT, é mais justo; o **BBR** não usa perda, estima banda e RTT mínimo (BDP).

### 9.2.12 Tahoe × Reno (e o que vem depois)
| | **Tahoe** | **Reno** |
|---|---|---|
| Timeout | `cwnd=1`, SS | `cwnd=1`, SS |
| 3 ACKs duplicados | `cwnd=1`, SS | `cwnd=ssthresh`, **CA** (fast recovery) |
| Resultado | recuperação lenta (volta a 1) | recuperação rápida |
Padrões atuais: **CUBIC** (Linux/Windows; corte ×0,7) e **BBR** (Google).

### 9.2.13 Exercícios resolvidos

**E1.** `ssthresh = 8` inicial. Liste `cwnd` nos RTTs 0–6, sem perdas. **R:** 1, 2, 4, **8** (atinge ssthresh → CA), 9, 10, 11.

**E2.** Com `cwnd = 24` ocorrem 3 ACKs duplicados (Reno). Quais os novos `ssthresh` e `cwnd` e a fase? **R:** `ssthresh = 12`, `cwnd = 12`, **CA**.

**E3.** Com `cwnd = 24` ocorre timeout. **R:** `ssthresh = 12`, `cwnd = 1`, **SS**; depois 1, 2, 4, 8, **12** (limitado), 13, …

**E4.** Quantos RTTs para a `cwnd` ir de 1 a 64 só em slow start? **R:** dobra por RTT → 1→2→4→8→16→32→64: **6 RTTs**.

**E5.** Uma sequência de `cwnd` é 1, 2, 4, 8, 16, 17, 18. Em que fase estava no fim? Qual o `ssthresh`? **R:** CA; `ssthresh` = 16 (a mudança de exponencial para linear ocorre em 16).

**E6.** Verdadeiro ou falso: "No timeout, o `ssthresh` é metade do `ssthresh` anterior." **R:** **F**: é metade do **`cwnd`** no momento da perda.

**E7.** Taxa com `cwnd = 20 MSS`, `MSS = 1000 B`, `RTT = 50 ms`: **R:** `20·1000·8 / 0,05 = 3,2 Mbps`.

**E8.** `rwnd = 10 MSS`, `cwnd = 30 MSS`. Quanto pode estar em voo? **R:** `min(30,10) = 10 MSS` (o receptor limita).

**E9.** Mathis: perda sobe de 1% para 4%. **R:** vazão cai à **metade**.

**E10.** Vazão média com `W = 32 MSS`, `RTT = 80 ms`, `MSS = 1250 B`. **R:** `0,75·32·1250·8/0,08 = 3 Mbps`.

**E11. (Pegadinha)** Por que o TCP **não** volta a 1 em 3 ACKs duplicados no Reno? **R:** porque os ACKs duplicados provam que a rede **ainda entrega** segmentos; só a metade da janela basta para aliviar.

**E12. (TT Q6)** Remetente ocioso entre t1 e t2: reaproveitar `cwnd` e `ssthresh`? **R:** vantagem: retoma rápido; desvantagem: a rede pode ter mudado e a rajada causa perdas; alternativa: **manter `ssthresh`, reiniciar `cwnd` (1 MSS) e usar slow start**.

### 9.2.14 Resposta‑modelo para a prova (congestionamento)
> O controle de congestionamento do TCP evita que o remetente sobrecarregue a **rede** (roteadores). Como o IP não dá feedback, o remetente **infere** o congestionamento pela **perda** (timeout ou 3 ACKs duplicados). Mantém uma janela `cwnd`, que limita os bytes em voo (junto com `rwnd`: janela efetiva = min), e um limiar `ssthresh`. A conexão começa em **slow start** (`cwnd = 1 MSS`, +1 MSS por ACK → dobra a cada RTT) até `cwnd` atingir `ssthresh`, quando entra em **congestion avoidance** (+1 MSS por RTT, aumento aditivo). Em **3 ACKs duplicados** faz fast retransmit, `ssthresh = cwnd/2` e `cwnd = ssthresh` (continua em CA); em **timeout**, `ssthresh = cwnd/2`, `cwnd = 1 MSS` e volta ao slow start. Esse comportamento (AIMD, "dente de serra") faz as conexões convergirem para uma divisão justa da banda.

### 9.2.15 Checklist
- [ ] Sei dizer o que são `cwnd`, `ssthresh`, `rwnd`, MSS e como se combinam.
- [ ] Sei os 3 sinais (ACKs normais, 3 dups, timeout) e o que cada um muda.
- [ ] Faço uma tabela de `cwnd` por RTT com perdas de cada tipo.
- [ ] Explico por que SS dobra e CA soma 1 por RTT.
- [ ] Explico por que `cwnd/2` e por que o timeout é pior que 3 dups.
- [ ] Explico o dente de serra e a justiça do AIMD.

---

### 9.2.16 Como **ler um gráfico de `cwnd`** (questão de prova recente)

O gráfico mostra a `cwnd` (eixo vertical, em segmentos) a cada **rodada de transmissão** (eixo horizontal, ≈ 1 RTT). Toda pergunta sobre ele se resolve reconhecendo **quatro "assinaturas"**:

| O que você vê | O que significa | Por quê |
|---|---|---|
| Curva **subindo cada vez mais rápido** (1, 2, 4, 8, 16…) | **Slow Start** | `cwnd` dobra a cada RTT |
| Reta **subindo de 1 em 1** | **Congestion Avoidance** | +1 MSS por RTT |
| **Queda até ≈ 1** e depois **curva exponencial** de novo | **Timeout** | `cwnd = 1` e volta ao slow start |
| **Queda até ≈ metade** e continua **subindo linearmente** (sem passar por 1) | **3 ACKs duplicados** (fast retransmit/recovery) | `cwnd ≈ ssthresh` e segue em CA |
| Ponto onde a exponencial vira reta | `cwnd` **atingiu o `ssthresh`** | o valor de `cwnd` ali = `ssthresh` |

**Regras para as perguntas típicas**
1. **Períodos de SS e de CA:** liste os intervalos de rodadas onde a curva é exponencial (SS) e linear (CA).
2. **Qual mecanismo detectou a perda em uma rodada?** Olhe **para onde a `cwnd` caiu**: **a ≈ 1 → timeout; à metade (e segue linear) → 3 ACKs duplicados.** *Não é o "tamanho da queda" que decide, e sim se ela chega a 1.*
3. **`ssthresh` após uma perda** = **metade da `cwnd` imediatamente antes da queda**. Ex.: perdeu com `cwnd = 42` → `ssthresh = 21`. Esse valor **permanece** até a próxima perda.
4. **O `ssthresh` muda ao longo do gráfico?** **Só nas perdas** (e o valor inicial pode ser lido onde o slow start termina). **Não** cresce em SS nem em CA.
5. **Nova perda por 3 ACKs duplicados com `cwnd = X`:** `ssthresh = X/2` e `cwnd = X/2` (slides; no livro, `X/2 + 3`); segue em **CA**. **Nova perda por timeout:** `ssthresh = X/2`, `cwnd = 1`, **slow start**.

**Exemplo completo (PR1 Q8; valores aproximados):**
| Rodadas | Observação | Conclusão |
|---|---|---|
| 1 → 6 | 1, 2, 4, 8, 16, **32** | **Slow Start**; `ssthresh` inicial = 32 |
| 6 → 16 | 33, 34, … , **≈ 42** | **Congestion Avoidance** |
| **16** | cai a **≈ 24** (aprox. metade) e **sobe linearmente** | **3 ACKs duplicados**; `ssthresh = 42/2 = 21` |
| 17 → 22 | 24, 25, … , **≈ 29** | **Congestion Avoidance** (`ssthresh = 21`) |
| **22 → 23** | cai a **1** | **Timeout**; `ssthresh = 29/2 ≈ 14–15` |
| 23 → 26 | 1, 2, 4, **8** | **Slow Start** |
| fim da **26** | `cwnd ≈ 8`, chegam 3 ACKs duplicados | `ssthresh = 4`, `cwnd = 4` (slides) → **CA** |
**Erros que o aluno cometeu (e como evitar):**
- Disse que a perda da 16 foi **timeout** "porque a `cwnd` diminuiu bastante" → **errado**: caiu à **metade**, não a 1, e seguiu linear.
- Disse que o `ssthresh` "duplica em slow start e sobe 1 a 1 em CA" → **errado**: isso é a `cwnd`; o `ssthresh` só muda **na perda**.
- Na perda por 3 dups com `cwnd = 8`, **dobrou** (16) em vez de **dividir** (4).

**Treino:** (1) cwnd 1→…→16 e cai a 8: tipo de perda? (**3 dups**; `ssthresh = 8`.) (2) cwnd 20 cai a 1: tipo? (**timeout**; `ssthresh = 10`.) (3) após o item 2, até onde a `cwnd` cresce exponencialmente? (**até 10**, depois linear.)

## 9.3 Fluxo × congestionamento (a pergunta de todas as provas)
| | Fluxo | Congestionamento |
|---|---|---|
| Protege | o **receptor** (buffer) | a **rede** (roteadores) |
| Variável | `rwnd` | `cwnd` (+ `ssthresh`) |
| Quem calcula/informa | **receptor** avisa (explícito, no cabeçalho) | **remetente** infere (perda/ACKs duplicados/timeout) |
| Escopo | fim‑a‑fim remetente↔receptor | remetente↔rede |
| Sinal | campo `rwnd` | timeout / 3 dups |
| Mecanismo | janela anunciada; sonda de 1 byte se zero | SS, CA, fast retransmit/recovery (AIMD) |
| Janela efetiva | `min(cwnd, rwnd)` | |

---

# 10. Tabela‑mestra: problema → detecção → reação

| Problema | Quem detecta | Como detecta | Reação | Mecanismo |
|---|---|---|---|---|
| Dado corrompido | receptor | checksum falha | descarta (≈ perda) | checksum |
| Dado perdido (último/único em voo) | remetente | **timeout** | retransmite o mais antigo; `cwnd=1` | timer |
| Dado perdido (há segmentos depois) | remetente | **3 ACKs duplicados** | **fast retransmit**; `cwnd=ssthresh` | ACK dup |
| ACK perdido, ACK seguinte chega | — | ACK cumulativo cobre | **nada** | ACK cumulativo |
| ACK perdido, nada cobre | remetente | timeout | retransmite; receptor descarta duplicata e re‑ACK | timer + seq |
| Timeout prematuro | (remetente erra) | ACK chega depois | duplicata inofensiva | seq |
| Fora de ordem | receptor | seq maior que o esperado | **ACK dup**; guarda | ACK dup/buffer |
| Duplicata | receptor | seq já recebido | descarta; re‑ACK | seq |
| Receptor sobrecarregado | receptor | buffer cheio | `rwnd` menor / 0; sonda de 1 byte | controle de fluxo |
| Rede congestionada | remetente | perda | reduz `cwnd` (AIMD) | controle de congestionamento |
| Pedido de conexão atrasado/antigo | servidor | 3º passo não vem | não consolida a conexão | handshake de 3 vias |

---

# 11. Como a prova pergunta isso — e como resolver

## 11.1 Tipos de questão de transporte nas provas
1. **Conceituais curtas:** objetivo do transporte, por que UDP existe, por que seq e timers, por que dois protocolos, 1 × 2 sockets, demux UDP.
2. **V/F** do TCP (cinco afirmações recorrentes).
3. **Cálculo de seq/ACK** e **diagrama de tempo** com ACK perdido.
4. **Explicações longas:** bit alternante/GBN/SR; fluxo × congestionamento; slow start × CA; TCP em linhas gerais.
5. **Lista de revisão:** V/F sobre ACK fora da janela e equivalência com janela 1.

## 11.2 Método para resolver cálculos de seq/ACK (passo a passo)
1. Escreva o "último byte já recebido em ordem" (ex.: 126).
2. O 1º segmento começa em `126+1`. Anote `Seq`, `len` e `Seq+len` (próximo seq).
3. ACK em ordem = `Seq+len` do último segmento recebido em ordem.
4. Se um chega **fora de ordem**: ACK = **o byte que ainda falta** (repetido).
5. Portas/IPs **invertidos** na volta.

## 11.3 Exercícios resolvidos

**E1 (P15 Q8).** B recebeu até 126. A envia 70 B (Seq=127) e 50 B.
- Seq₂ = 127+70 = **197**; ACK₁ = **197**; ACK₂ = **247**; se o 2º chega antes do 1º: **127**. Portas: origem 302, destino 80 (ida); 80→302 (volta).

**E2 (TT Q4).** Seq 1400, 1900, 2000. Tamanhos: 1900−1400 = **500**; 2000−1900 = **100**; o 3º é **indeterminado** (L). ACKs: **1900**, **2000**, **2000+L**.

**E3 (P13 Q9).** Seq 90 e 110. 1º tem **20 B**. Se só o 2º chega, ACK = **90** (dup).

**E4 (fast retransmit).** A envia 100 B em Seq=500, 600, 700, 800, 900; o de 600 se perde. B envia: ACK=600, **ACK=600, ACK=600, ACK=600** (os 3 dups vêm dos segmentos 700, 800, 900). Ao 3º dup, A retransmite Seq=600; B passa a ACK=**1000**.

**E5 (GBN, N=3).** Pacotes 0..5. ACK0 se perde, ACK1 e ACK2 chegam. **Resposta:** como ACK1 é cumulativo, cobre o 0 → nada é retransmitido; `base` = 2 após ACK1 e = 3 após ACK2.

**E6 (GBN × SR, mesmo cenário).** N=4, perde-se o pacote 1. GBN reenvia **1,2,3,4** (e eventualmente os que foram enviados na janela); SR reenvia **só o 1**. Receptor GBN: descarta 2,3,4 e responde ACK0 (re-ACK do último em ordem); SR: guarda 2,3,4 e responde ACK2, ACK3, ACK4.

**E7 (timeout).** `Est=80 ms`, `Dev=10 ms`, nova amostra 120 ms: `Dev'=0,75·10+0,25·40=17,5`; `Est'=0,875·80+0,125·120=85`; `Timeout=85+70=155 ms`.

**E8 (flow control).** `RcvBuffer=8000`, app leu tudo até o byte 3000, mas o TCP já recebeu até o 6000 (3000 bytes no buffer): `rwnd = 8000−3000 = 5000`. A tem 2000 B em voo → pode enviar mais 3000.

**E9 (stop‑and‑wait).** L=12000 b, R=100 Mbps, RTT=20 ms: `L/R=0,12 ms`; `U=0,12/20,12≈0,6 %`. Com janela de N=50: `U≈ 50·0,6% ≈ 30 %`.

**E10 (ACK ≠ Seq+len do mesmo segmento).** "A envia Seq=38, 4 B; o ACK nesse segmento é 42?" **Falso**; é o próximo byte esperado **de B**. 42 é o ACK que B enviaria.

**E11 (rdt 3.0 – cenário "ACK perdido").** Descrever: pkt1 chega e é entregue; ACK1 se perde; timer; reenvio; receptor percebe duplicata pelo bit de seq (espera 0), descarta, re‑ACK1; remetente avança.

**E12 (fluxo × congestionamento).** Use a tabela § 9.3 + § 9.2.

## 11.4 Texto‑modelo: "por que precisamos de seq e timers no rdt?"
Números de sequência permitem ao receptor distinguir um pacote novo de uma retransmissão (descartar duplicatas e reordenar); temporizadores permitem ao remetente detectar a perda de pacotes ou de ACKs — que não geram nenhum sinal — e retransmitir.

## 11.5 Texto‑modelo: "como o TCP trata erros/perdas?"
Cada byte é numerado; o receptor devolve ACKs cumulativos com o próximo byte esperado. Se um segmento é corrompido, o checksum faz o receptor descartá‑lo. O remetente mantém um timer para o segmento mais antigo sem ACK; no timeout, retransmite esse segmento e dobra o intervalo (calculado por `EstimatedRTT + 4·DevRTT`). Se chegam 3 ACKs duplicados, retransmite imediatamente (fast retransmit). Segmentos duplicados são descartados pelo número de sequência, e fora de ordem geram ACK duplicado. Em paralelo, `rwnd` impede estourar o buffer do receptor e `cwnd` reduz a taxa quando há perda.

---

# 12. Checklist final e armadilhas

**Você domina se consegue, sem consultar:**
- [ ] Listar os problemas do canal e o mecanismo que resolve cada um (§4, §10).
- [ ] Desenhar os 4 cenários do bit alternante (§5.5).
- [ ] Desenhar GBN e SR com o pacote 2 perdido e contar as retransmissões (§6).
- [ ] Explicar por que ACK no GBN é cumulativo e no SR individual — e as consequências.
- [ ] Calcular Seq/ACK e desenhar o diagrama com ACK perdido (§8, §11).
- [ ] Explicar **3 ACKs duplicados** (por que 3; o que o TCP faz; diferença para timeout).
- [ ] Dizer, para cada V/F, o porquê (ACK≠Seq+len; rwnd varia; ssthresh=cwnd/2).
- [ ] Escrever a diferença fluxo × congestionamento.

**Armadilhas:**
- ACK é **próximo byte esperado**, não "último recebido".
- ACK não é `Seq+len` **do mesmo segmento**; refere-se à direção oposta.
- No timeout o TCP retransmite **um segmento** (não a janela, como o GBN).
- 3 dup ACKs = 4 ACKs iguais no total (o 1º é o "normal").
- ACK duplicado ≠ erro do receptor: é o **sinal** que o receptor usa para dizer "falta o byte x".
- GBN: **cumulativo + sem buffer**. SR: **individual + buffer + timer por pacote**.
- `ssthresh = cwnd/2` (do momento da perda), não metade do ssthresh anterior.
