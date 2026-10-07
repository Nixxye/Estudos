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

*rdt = reliable data transfer.* Notação: **FSM** (máquina de estados) com `evento / ação`. Interface: `rdt_send()` (app → protocolo), `udt_send()` (protocolo → rede), `rdt_rcv()` (rede → protocolo), `deliver_data()` (protocolo → app).

## 5.1 rdt 1.0 — canal perfeito
Sem erros, sem perdas. Remetente: pega dado, faz pacote, envia. Receptor: recebe, extrai, entrega. **Um estado só.** Nada de ACK.

## 5.2 rdt 2.0 — canal com erros de bit
**Novos mecanismos:** (1) **detecção de erro** (checksum); (2) **feedback** do receptor: **ACK** ("recebi bem") e **NAK** ("veio com erro, repita"); (3) **retransmissão** (ARQ).
- Remetente (estado "esperar ACK/NAK"): se **NAK** → reenvia o pacote; se **ACK** → volta a esperar dado da aplicação.
- É "**pare‑e‑espere**" (*stop‑and‑wait*): envia **um** pacote e espera a resposta antes do próximo.

**A falha:** e se o **ACK/NAK** chegar corrompido? O remetente não sabe se o receptor recebeu. Se retransmite, o receptor pode receber **o mesmo dado duas vezes** sem saber que é repetido (P4 → P5).

## 5.3 rdt 2.1 — número de sequência
**Solução:** o remetente numera os pacotes: **0 ou 1** (um bit basta no pare‑e‑espere). O receptor tem dois estados (espera 0 / espera 1):
- Pacote com o número esperado e íntegro → entrega, ACK.
- **Pacote com o número "errado" (duplicata)** → **descarta** e reenvia o ACK.
- Corrompido → NAK.
Remetente: ACK/NAK corrompido (ou NAK) → reenvia.

## 5.4 rdt 2.2 — sem NAK
Elimina NAK: o receptor manda **ACK com o número do último pacote recebido corretamente**. Se o remetente recebe **ACK duplicado** (ACK do pacote anterior de novo), entende que o pacote atual **não** chegou bem → retransmite.
> **Esta é a origem do "ACK duplicado como sinal de problema"** — o mesmo princípio vai reaparecer no TCP (fast retransmit) e no GBN.

## 5.5 rdt 3.0 — canal com erros **e perdas** = *bit alternante*
Falta resolver P2/P3: se o pacote ou o ACK **sumir**, ninguém manda nada e todos esperam para sempre. **Solução: temporizador (timer).**
- Remetente: envia o pacote, **liga o timer**. Se o ACK correto chega → **para o timer** e passa ao próximo (alternando o bit). Se o **timer estoura** → **reenvia** o pacote e reinicia o timer.
- ACK corrompido ou com número errado: na FSM do Kurose o remetente **ignora** e deixa o timer resolver (no fim, também retransmite).
- Receptor: igual ao 2.2 (ACK com o número do último pacote bom; duplicata → descarta e re‑ACK).

### Os 4 cenários do bit alternante (saiba desenhar)
**① Sem perda**
```
Rem.                 Dest.
 pkt0 ─────────────►        entrega, ACK0
 ◄───────────── ACK0
 pkt1 ─────────────►        entrega, ACK1
 ◄───────────── ACK1
```
**② Pacote perdido**
```
 pkt1 ───────X                (perdido)
   ... timer estoura ...
 pkt1 ─────────────►        entrega, ACK1   (retransmissão)
 ◄───────────── ACK1
```
**③ ACK perdido** (o dado **chegou**)
```
 pkt1 ─────────────►        entrega, ACK1
 X◄──────────── ACK1          (perdido)
   ... timer estoura ...
 pkt1 ─────────────►        é DUPLICATA (esperava seq 0): descarta e re-ACK1
 ◄───────────── ACK1
```
O **número de sequência** é o que impede a aplicação receber o dado duas vezes.
**④ Timeout prematuro** (timer curto demais)
```
 pkt1 ─────────────►        entrega, ACK1 (ainda a caminho)
   ... timer estoura antes do ACK chegar ...
 pkt1 ─────────────►        duplicata: descarta, re-ACK1
 ◄───────────── ACK1 (1º)   remetente avança (envia pkt0)
 ◄───────────── ACK1 (2º)   ACK duplicado: ignorado
```

## 5.6 O desempenho do pare‑e‑espere
Utilização do remetente: `U = (L/R) / (RTT + L/R)`.
Exemplo: R = 1 Gbps, L = 8000 bits, RTT = 30 ms → `L/R = 8 µs` → `U = 0,008 / 30,008 ≈ 0,00027 = 0,027 %`. O enlace fica quase todo parado esperando ACK. **Solução: pipelining.**

---

# 6. Pipelining: Go‑Back‑N e Selective Repeat

**Pipelining:** enviar **vários pacotes** sem esperar o ACK de cada um. Com N pacotes em voo, `U = N·(L/R)/(RTT + L/R)`. Exige: números de sequência maiores e **buffers**. Duas famílias: **GBN** e **SR**. A diferença está em **como o ACK é interpretado** e **o que se retransmite**.

## 6.1 Go‑Back‑N (GBN)
**Remetente:** janela de tamanho **N**; `base` = pacote mais antigo sem ACK; `nextseqnum` = próximo a enviar. Pode ter até N pacotes em voo.
- **Um único timer** — do pacote `base`.
- **ACK cumulativo:** `ACK(n)` significa "**recebi todos até n, em ordem**". Ao recebê‑lo: `base = n + 1`. Se ainda há pendentes → reinicia o timer; se não → para.
- **Timeout:** reenvia **todos** os pacotes de `base` até `nextseqnum − 1` ("volta N").
**Receptor:** só aceita o pacote **esperado** (`expectedseqnum`). Qualquer outro (fora de ordem) é **descartado** e ele **reenvia o ACK do último pacote em ordem**. **Sem buffer.**

### Exemplo A — um pacote de dados perdido (N = 4, pacotes 0–7, o 2 se perde)
```
Rem.                                   Dest.
 pkt0 ──►                              ok  → ACK0
 pkt1 ──►                              ok  → ACK1
 pkt2 ──X                              (perdido)
 pkt3 ──►                              esperava 2 → DESCARTA → ACK1
 ◄── ACK0   base=1  → envia pkt4
 ◄── ACK1   base=2  → envia pkt5
 pkt4 ──►                              descarta → ACK1
 pkt5 ──►                              descarta → ACK1
 ◄── ACK1 (dup) ◄── ACK1 (dup) ◄── ACK1 (dup)   (ignorados, base continua 2)
 ... TIMEOUT do pkt2 ...
 pkt2 ──► pkt3 ──► pkt4 ──► pkt5 ──►   (reenvia a janela inteira)
                                       ok → ACK2, ACK3, ACK4, ACK5
```
Foram **4 retransmissões** (2,3,4,5) apesar de só o 2 ter se perdido → "desperdício".

### Exemplo B — um ACK perdido (cumulativo "cobre")
Remetente envia 0,1,2,3; todos chegam. ACK0 e ACK1 se perdem, mas **ACK2 chega** → como é cumulativo, `base = 3`: confirma 0,1,2 de uma vez. **Nada é retransmitido.**
Se **todos** os ACKs se perdem: timeout → reenvia 0,1,2,3 → o receptor (esperando 4) **descarta** cada um e responde `ACK3` → o remetente avança `base = 4`.

## 6.2 Selective Repeat (SR)
**Remetente:** janela N; **um timer por pacote**; marca como "confirmado" cada pacote cujo **ACK individual** chega. Só desliza a janela quando o pacote `base` é confirmado (até o próximo ainda não confirmado).
- **Timeout(n):** reenvia **apenas n**.
**Receptor:** janela própria `[rcv_base, rcv_base+N−1]`, **com buffer**:
- pacote **dentro** da janela → **ACK(n)** (individual); se fora de ordem, **guarda**; se for o `rcv_base`, entrega (junto com os já guardados consecutivos) e desliza.
- pacote **antes** da janela (`[rcv_base−N, rcv_base−1]`, já entregue) → **reenvia ACK(n)** (o ACK anterior pode ter se perdido — sem isso o remetente nunca avançaria).
- outros → ignora.

### Exemplo — mesmo cenário (pacote 2 perdido, N = 4)
```
 pkt0..3 enviados; 2 perdido
 Dest.: ACK0, ACK1, (2 não chega), pkt3 → GUARDA, ACK3
 Rem.: ACK0→base=1 (envia 4) ; ACK1→base=2 (envia 5) ; ACK3 → marca 3, base fica em 2
 Dest.: pkt4 guarda ACK4 ; pkt5 guarda ACK5
 ... timer do pkt2 estoura ...
 Rem. reenvia SÓ pkt2
 Dest.: recebe 2 → entrega 2,3,4,5 em ordem ; ACK2
 Rem.: ACK2 → como 3,4,5 já estavam marcados, base pula para 6
```
**1 retransmissão** contra 4 no GBN.
**ACK perdido no SR:** o timer daquele pacote estoura → reenvia só ele → receptor vê pacote já entregue → **re‑ACK** → remetente marca.

## 6.3 Comparação
| | **Bit alternante** | **GBN** | **SR** |
|---|---|---|---|
| Janela remetente / receptor | 1 / 1 | N / 1 | N / N |
| Significado do ACK | do pacote (individual) | **cumulativo** (≤ n) | **individual** |
| Timers | 1 | **1** | **1 por pacote** |
| Buffer no receptor | não | **não** (descarta) | **sim** |
| Retransmite no timeout | o pacote | **janela toda** | **só o pacote** |
| Complexidade | mínima | baixa | alta |

## 6.4 Dois fatos que a lista de revisão cobra
1. **Bit alternante = GBN com N=1 = SR com N=1.** Com janela 1, não há diferença.
2. **GBN e SR podem receber ACK de pacote fora da janela corrente.** Cenário: remetente (N=3) envia 1,2,3; ACKs demoram; timeout → reenvia 1,2,3; receptor re‑ACKa; chegam os ACKs 1ª rodada (janela passa para 4,5,6); depois chegam os da 2ª rodada, referentes a 1,2,3 — **fora** da janela.
3. **Janela do SR ≤ metade do espaço de numeração** (senão o receptor confunde retransmissão do pacote 0 antigo com o 0 novo). GBN: N ≤ 2ᵏ − 1.

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

O ACK não carrega só "confirmação": carrega também a **janela do receptor**.

## 9.1 Controle de fluxo (`rwnd`) — em cada ACK
- `rwnd = RcvBuffer − (LastByteRcvd − LastByteRead)` (espaço livre no buffer do receptor).
- O receptor o coloca no cabeçalho de **todo** segmento (inclusive ACKs).
- O remetente garante `LastByteSent − LastByteAcked ≤ rwnd`.
- Aplicação lenta → buffer enche → `rwnd` cai → `rwnd=0` → remetente para e sonda com 1 byte.
- **Consequência:** bytes sem ACK ≤ `rwnd` ≤ buffer (afirmação **V** nas provas); `rwnd` **varia** (afirmação "rwnd nunca muda" é **F**).

## 9.2 Controle de congestionamento (`cwnd`) — decidido pelo que acontece com os ACKs
O remetente **observa os ACKs** (ou a falta deles) para inferir a rede:
| O que o remetente observa | Interpretação | Reação (Reno) |
|---|---|---|
| ACKs novos chegando normalmente | rede ok | **SS** (cwnd +1 MSS por ACK → dobra por RTT) até `ssthresh`, depois **CA** (+1 MSS/RTT) |
| **3 ACKs duplicados** | perda **leve** (a rede ainda entrega algo) | fast retransmit; `ssthresh=cwnd/2`; `cwnd=ssthresh`; segue em CA |
| **Timeout** (nenhum ACK) | perda **severa** | `ssthresh=cwnd/2`; **`cwnd=1 MSS`**; volta ao **SS** |
Janela efetiva do remetente: **`min(cwnd, rwnd)`**. (Tahoe: qualquer perda → `cwnd=1`.)

**Exemplo numérico de cwnd (ssthresh inicial = 8):** RTT0..: 1, 2, 4, 8 (chegou no ssthresh), 9, 10, 11, 12 (CA). Perda com `cwnd=12`:
- 3 dups (Reno): `ssthresh=6`, `cwnd=6` → 6, 7, 8…
- Timeout: `ssthresh=6`, `cwnd=1` → 1, 2, 4, **6** (SS não passa do ssthresh), 7, 8…

## 9.3 Fluxo × congestionamento (a pergunta de todas as provas)
| | Fluxo | Congestionamento |
|---|---|---|
| Protege | o **receptor** | a **rede** |
| Variável | `rwnd` | `cwnd` |
| Quem calcula/informa | **receptor** avisa (explícito, no cabeçalho) | **remetente** infere (perda/ACKs duplicados/timeout) |
| Escopo | fim‑a‑fim remetente↔receptor | remetente↔rede |

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
