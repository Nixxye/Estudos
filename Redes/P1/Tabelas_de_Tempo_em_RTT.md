# Tabelas de tempo em RTT — tudo o que vale lembrar

> **Para que serve:** comparar, lado a lado, **quanto custa (em RTTs)** cada mecanismo da disciplina: handshake, DNS, HTTP em cada versão, transações UDP × TCP, recuperação de perdas, slow start, janelas deslizantes etc.
> **Premissas (valem em todas as tabelas, salvo aviso):** RTT constante; **T_trans desprezível** (objeto pequeno; ver §9 para incluí‑lo); sem perdas; sem TLS; o cliente já conhece o IP do servidor (DNS tratado à parte em §3).
> **Legenda:** (slide) = vem dos slides · *(além dos slides)* = valor típico para você entender, mas fora do que é cobrado.
> Complementos: [Resumo_P1_Redes.md §2.4, §8.6](Resumo_P1_Redes.md) · [DNS_a_Fundo.md §13](DNS_a_Fundo.md) · [Transporte_do_Zero.md](Transporte_do_Zero.md).

---

## 0. Definição e regra de ouro

- **RTT (Round‑Trip Time):** tempo para um pacote pequeno ir do cliente ao servidor **e voltar** (propagação + filas + processamento).
- **Uma ida ou uma volta ≈ RTT/2.**
- **1 RTT = "uma pergunta e sua resposta".** Quase todo "custo em RTT" é contar **quantas perguntas‑e‑respostas em série** o protocolo exige antes de o dado chegar.
- **Tempo total = (nº de RTTs em série) × RTT + T_trans** (T_trans = L/R, tempo de empurrar os bits).
- O que roda **em paralelo** (pipelining, multiplexação, conexões paralelas) **não soma**.

---

## 1. Custo de **abrir** uma comunicação (RTTs antes do 1º byte de dados)

| Protocolo / situação | RTTs até poder enviar o 1º dado | Observação |
|---|---|---|
| **UDP** | **0** | sem handshake: manda o dado no primeiro datagrama (slide A4 s.12–13) |
| **TCP** | **1** | handshake de 3 vias (SYN → SYN+ACK → ACK); o 3º segmento já pode levar dados (A5 s.29) |
| **TCP + TLS** (2 handshakes em série) | **2 a 3** | TCP 1 + TLS 1 (TLS 1.3) ou 2 (TLS 1.2) *(além dos slides)* — o slide A6 s.25 mostra apenas "2 handshakes em série" |
| **QUIC (HTTP/3), 1ª conexão** | **1** | transporte + segurança num único handshake (A6 s.25) |
| **QUIC, reconexão (0‑RTT)** | **0** | dados no primeiro pacote (A6 s.28) |
| **SMTP** (sobre TCP) | **1** + banner | TCP 1; o servidor já manda `220` ao conectar |

**Fechar** (TCP, FIN/ACK em cada sentido): ≈ **1 RTT** por direção; normalmente não atrasa a aplicação (em seguida há `TIME_WAIT` de 2·MSL, que não bloqueia o usuário).

---

## 2. Uma **transação** (pergunta e resposta, sem conexão aproveitada)

| Cenário | RTTs | Por quê |
|---|---|---|
| **UDP** (ex.: DNS) | **1** | envia a consulta e recebe a resposta |
| **TCP — 1 objeto** (HTTP/1.0) | **2** (+ T_trans) | 1 RTT do handshake + 1 RTT da requisição/resposta (A2 s.22) |
| TCP — transação em conexão **já aberta** | **1** | só requisição/resposta |
| **Cliente remoto, "o mais rápido possível"** (P15 Q4) | UDP = 1; TCP = 2 | por isso a resposta da prova é **UDP** |
| **GET condicional → 304** (cache) | **1** (até a origem) | `If-Modified-Since` e resposta sem corpo, economizando banda, não RTT (A2 s.38) |

**Fórmula do slide:** `Tempo (1 objeto não persistente) = 2·RTT + T_trans`.

---

## 3. **DNS** (em RTTs para o nome ser resolvido)

Cada **par pergunta/resposta** com um servidor custa **1 RTT até aquele servidor**. O host só fala com o **DNS local** (RTT_h); o DNS local percorre a hierarquia (RTT_raiz, RTT_TLD, RTT_aut).

| Estado do cache do DNS local | Mensagens | Tempo (soma de RTTs) |
|---|---|---|
| **A do nome em cache** | 2 | **RTT_h** |
| Só o **NS do autoritativo** em cache | 4 | RTT_h + RTT_aut |
| Só o **NS do TLD** em cache | 6 | RTT_h + RTT_TLD + RTT_aut |
| **Cache vazio** | 8 | RTT_h + RTT_raiz + RTT_TLD + RTT_aut |

Exemplo: RTT_h = 5 ms; raiz 40; TLD 30; aut 20 → cache vazio = 5+40+30+20 = **95 ms**; só A em cache = **5 ms**.

**Depois do DNS**, o acesso ao site soma (HTTP, objeto único): `DNS + RTT₀ (TCP) + RTT₀ (GET) = DNS + 2·RTT₀ + T_trans`.
*(Se o DNS visita servidores com RTT₁…RTTₙ: `ΣRTTᵢ + 2·RTT₀ + T_trans`.)*

---

## 4. **HTTP**: página com 1 HTML + *n* objetos (comparação central)

**Premissa:** o cliente já tem o IP; sem TLS; T_trans desprezível; as requisições dos objetos só podem ser feitas **depois** de receber o HTML.

| Modo | Fórmula (RTTs) | n = 10 | Como contar |
|---|---|---|---|
| **HTTP/1.0 — não persistente, sequencial** | **2·(n+1)** | **22** | cada objeto: 1 (TCP) + 1 (GET) (A2 s.23) |
| **Não persistente com *k* conexões paralelas** *(típico dos navegadores)* | 2 + 2·⌈n/k⌉ | k=5: **6** | HTML (2 RTT) + os n objetos em grupos de k, cada grupo 2 RTT |
| **HTTP/1.1 — persistente, SEM pipelining** | **2 + n** | **12** | 1 (TCP) + 1 (HTML) + 1 por objeto, um de cada vez |
| **HTTP/1.1 — persistente, COM pipelining** | **2 + 1 = 3** | **3** | 1 (TCP) + 1 (HTML) + **1 para todos** os GETs em lote (A2 s.24) |
| **HTTP/2** (multiplexação, 1 conexão TCP) | ≈ **3** | **3** | igual ao pipelining, **sem o bloqueio HoL da aplicação** (A2 s.41–44) |
| **HTTP/3 (QUIC), 1ª visita** | ≈ **3** | **3** | handshake 1 (já com segurança) + HTML 1 + objetos 1; **sem HoL** (A2 s.44–48) |
| **HTTP/3, reconexão 0‑RTT** | ≈ **2** | **2** | 0 + HTML 1 + objetos 1 |
| *Ressalva (além dos slides)* | HTTP/2 sobre TLS e TCP: +1 a +2 RTT de TLS | | |

**Leitura rápida:** 22 → 12 → 3 mostra o ganho de **persistência** (−10 RTT) e depois de **pipelining/multiplexação** (−9 RTT). A evolução HTTP/1.0 → 3 existe para **reduzir RTTs**: "a velocidade da luz é um limite; só dá para reduzir o número de idas e voltas".

**Influência do T_trans:** não persistente soma `(n+1)·T_trans`; persistente soma `T_trans` por objeto (em sequência) — mas só o T_trans do **último** bit conta se os objetos são enviados em fluxo contínuo.

---

## 5. **Cache** web (proxy)

| Evento | Tempo | Observação |
|---|---|---|
| **Hit** (objeto no proxy) | ≈ **RTT_cliente↔proxy** (LAN, ≈ 0) | não usa o link de acesso (A2 s.35–37) |
| **Miss** | RTT_cliente↔proxy + **tempo até a origem** (2·RTT_origem para não persistente) | o proxy vira cliente da origem |
| **Atraso médio** | `h · atraso_hit + (1−h) · atraso_miss` | exemplo do slide: 0,4·0 + 0,6·2 s = **1,2 s** |
| **GET condicional** | 1 RTT (cliente↔origem) | resposta **304** não carrega o objeto |

---

## 6. **Confiabilidade** (rdt) — tempo de entrega em RTTs

### 6.1 Pare‑e‑espere (bit alternante) × pipelining
Para enviar **n pacotes** (T_trans desprezível):

| Protocolo | Tempo ≈ | Exemplo n = 100 |
|---|---|---|
| **Bit alternante (stop‑and‑wait)** | **n · RTT** | 100 RTT |
| **Janela N (GBN/SR), sem perdas** | **⌈n / N⌉ · RTT** | N = 10 → **10 RTT**; N = 50 → 2 RTT |
| Utilização do remetente | `U = (L/R)/(RTT + L/R)` → com N: `U = N·(L/R)/(RTT + L/R)` | N para 100 %: `≈ (RTT + L/R)/(L/R)` (ex.: 3751 no slide) |

### 6.2 Custo de **uma perda** (o que muda quando algo falha)
Sem perda, um pacote custa **1 RTT** (envio + ACK). Com perda:

| Cenário | Tempo adicional | Total para entregar 1 pacote |
|---|---|---|
| **Pacote perdido** (bit alternante) | espera o **timeout** `T` | `T + 1 RTT` (T > RTT) |
| **ACK perdido** (bit alternante) | espera o timeout `T` | `T + 1 RTT` |
| **Timeout prematuro** (T < RTT) | retransmissão inútil | 1 RTT (+ duplicata) |
| **GBN**: pacote perdido no meio | espera `T`, **reenvia a janela** | `T` + 1 RTT; mais tráfego (N pacotes) |
| **SR**: pacote perdido no meio | espera `T` (timer do pacote), **reenvia 1** | `T` + 1 RTT; tráfego mínimo |
| **GBN/SR com ACK perdido coberto por ACK posterior** (GBN) | **0** | sem custo (cumulativo) |

**Regra:** o timeout `T` é **maior que 1 RTT** (precisa dar tempo ao ACK) → toda perda custa **pelo menos um timeout**, que é o grande vilão do tempo.

---

## 7. **TCP**: detecção e recuperação de perdas (em tempo)

| Evento | Quando o remetente percebe | Tempo de recuperação ≈ |
|---|---|---|
| **Timeout** (RTO) | quando o timer vence: `TimeoutInterval = EstimatedRTT + 4·DevRTT` (> 1 RTT) | **RTO + ~1 RTT** (reenvio + ACK); em timeouts **repetidos** o intervalo **dobra** (2×, 4×, …: *backoff*) |
| **3 ACKs duplicados (fast retransmit)** | ≈ **1 RTT** após enviar o segmento perdido (os duplicados voltam enquanto o timer ainda corre) | **~1 RTT + 0,5 RTT** (reenvio chega) → bem menor que o RTO |
| **ACK atrasado** (receptor) | até **500 ms** (não é RTT; é um limite de tempo fixo) | um ACK pode demorar até 0,5 s se não houver 2º segmento |
| **Sonda de janela zero** (`rwnd = 0`) | a cada intervalo; cada sonda custa **1 RTT** para saber se `rwnd > 0` | o remetente fica parado até uma resposta com `rwnd > 0` |
| **Perda de ACK coberta por ACK posterior** | — | **0** (cumulativo) |

**Por que fast retransmit vale a pena:** recupera em ≈ 1–1,5 RTT, sem esperar o RTO (que pode ser dezenas ou centenas de ms a segundos).

---

## 8. **Congestionamento**: quanto tempo (em RTTs) para crescer e recuperar

### 8.1 Slow start (dobra a cada RTT)
`cwnd` ao início da rodada *k* = **2ᵏ⁻¹** MSS (rodada 1: 1 MSS). Segmentos acumulados após *k* rodadas = **2ᵏ − 1**.

| Rodada (RTT nº) | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 10 |
|---|---|---|---|---|---|---|---|---|---|
| `cwnd` (MSS) | 1 | 2 | 4 | 8 | 16 | 32 | 64 | 128 | 512 |
| Segmentos enviados no total | 1 | 3 | 7 | 15 | 31 | 63 | 127 | 255 | 1023 |

**Quantas rodadas para enviar *S* segmentos só com slow start (sem limite de rwnd/rede)?** `⌈log₂(S + 1)⌉` RTTs. Ex.: S = 100 → 7 rodadas.
**Custo de um download HTTP não persistente de *S* segmentos (só slow start, sem perdas, sem limite de `rwnd`):** ≈ **1 RTT (handshake TCP) + ⌈log₂(S+1)⌉ rodadas** (a 1ª rodada já inclui o GET e o 1º segmento). Ex.: S = 15 → 1 + 4 = **5 RTT**; com a conexão persistente já "aquecida" (cwnd alta), as rodadas diminuem.
> Isso explica por que a **persistência** (A2 s.21) vale: evita recomeçar o slow start a cada objeto.

### 8.2 Congestion avoidance (+1 MSS por RTT)
`cwnd` após *k* RTTs = `cwnd₀ + k`. Para ir de `W/2` até `W`: **W/2 RTTs**.

### 8.3 Recuperação depois de uma perda (cwnd = W no momento da perda)
| Evento | Nova `cwnd` | RTTs para voltar a ≈ W |
|---|---|---|
| **3 ACKs duplicados (Reno)** | `W/2` (CA) | **W/2** RTTs (linear: +1 por RTT) |
| **Timeout** | **1** (e ssthresh = W/2) | slow start até W/2: **⌈log₂(W/2)⌉** RTTs; depois CA: **W/2** RTTs → **bem mais lento** |
| **Tahoe (qualquer perda)** | 1 | idem timeout |
Exemplo (W = 32): 3 dups → 16 → 32 em **16 RTTs**; timeout → 1 → 16 em **4 RTTs** (SS) → 32 em **16 RTTs** (CA) = **20 RTTs**.

---

## 9. **T_trans** entra na conta — como combinar com RTT

`T_trans = L/R`. Para um objeto de tamanho L num enlace de taxa R:
- **HTTP 1 objeto não persistente:** `2·RTT + L/R`.
- **Objeto grande com slow start:** `2·RTT + (rodadas de SS)·RTT + L/R`, aproximadamente (se a janela não for limitada por `rwnd`).
- **Pipeline de n pacotes:** `RTT + n·(L/R)` (o último ACK chega 1 RTT depois do último pacote enviado).
- **Pare‑e‑espere de n pacotes:** `n·(RTT + L/R)`.

---

## 10. **E‑mail** (SMTP/POP3) em RTTs *(contagem típica; além dos slides)*

Cada comando com sua resposta = **1 RTT**.
| Sessão | RTTs |
|---|---|
| **SMTP** (TCP 1 + `HELO` 1 + `MAIL FROM` 1 + `RCPT TO` 1 + `DATA` 1 + corpo+`.` 1 + `QUIT` 1) | **≈ 7** |
| **POP3** (TCP 1 + `user` 1 + `pass` 1 + `list` 1 + `retr` n + `dele` n + `quit` 1) | **≈ 5 + 2n** |
**Antes disso:** o servidor de origem faz **MX + A** (≈ 2 consultas DNS, com cache em muitos casos).

---

## 11. **P2P e arquivos** (não são RTT, mas comparáveis em ordem de grandeza)

| | Fórmula | Exemplo (F = 15 Gb; u_s = 30 Mbps; d_min = 2 Mbps; u = 0,3 Mbps; N = 1000) |
|---|---|---|
| Cliente‑servidor | `max{N·F/u_s , F/d_min}` | **138,8 h** |
| P2P | `max{F/u_s , F/d_min , N·F/(u_s+Σuᵢ)}` | **12,6 h** |
Aqui o gargalo é **banda**, não latência: RTT é irrelevante comparado a horas.

---

## 12. Tabela‑resumo "decore isto"

| # | O que | Custo em RTT |
|---|---|---|
| 1 | UDP: início | **0** |
| 2 | TCP: handshake | **1** |
| 3 | Transação UDP (DNS) | **1** |
| 4 | Transação TCP (1 objeto, HTTP/1.0) | **2** (+T_trans) |
| 5 | HTML + 10 imagens, **não persistente** | **22** |
| 6 | HTML + 10 imagens, persistente **sem** pipelining | **12** |
| 7 | HTML + 10 imagens, persistente **com** pipelining | **3** |
| 8 | HTTP/2 | ≈ **3** (sem HoL de aplicação) |
| 9 | HTTP/3 (QUIC) | ≈ **3** (1ª visita) · **2** (0‑RTT) |
| 10 | DNS, cache vazio / só A em cache | RTT_h+RTT_raiz+RTT_TLD+RTT_aut / **RTT_h** |
| 11 | Bit alternante, n pacotes | **n · RTT** |
| 12 | Janela N, n pacotes | **⌈n/N⌉ · RTT** |
| 13 | Uma perda (bit alternante/GBN/SR) | **+ 1 timeout** (> 1 RTT) |
| 14 | Fast retransmit | **≈ 1–1,5 RTT** (vs. RTO) |
| 15 | Slow start: *S* segmentos | **⌈log₂(S+1)⌉** RTT |
| 16 | Recuperar após 3 dups | **W/2** RTT (linear) |
| 17 | Recuperar após timeout | **⌈log₂(W/2)⌉ + W/2** RTT |
| 18 | Timeout repetido | 2×, 4×, … (backoff) |
| 19 | Sonda `rwnd=0` | **1 RTT** por sonda |
| 20 | Stop‑and‑wait: utilização | `(L/R)/(RTT + L/R)` ≈ **0,027 %** (exemplo) |

---

## 13. Exercício integrador (use as tabelas)

**Enunciado:** O usuário abre `http://www.exemplo.br/` com HTML + 8 imagens, **mesmo servidor**. RTT_h (host→DNS local) = 4 ms; RTT_raiz = 40, RTT_TLD = 30, RTT_aut = 20 ms (cache **vazio**); RTT₀ (servidor web) = 50 ms; T_trans desprezível. Calcule o tempo até a página completa em: (a) HTTP/1.0 sequencial, (b) HTTP/1.1 persistente sem pipelining, (c) HTTP/1.1 com pipelining.

**Resolução:**
- **DNS (uma vez, cache vazio):** 4 + 40 + 30 + 20 = **94 ms**.
- **(a)** objetos = 1 + 8 = 9 → `2·9 = 18 RTT₀ = 18·50 = 900 ms` → **994 ms**.
- **(b)** `2 + 8 = 10 RTT₀ = 500 ms` → **594 ms**.
- **(c)** `2 + 1 = 3 RTT₀ = 150 ms` → **244 ms**.
- Diferença (a)→(c): 750 ms só pela evolução do HTTP.
*(Se o DNS estivesse em cache: tempos caem 90 ms, restando 4 ms de RTT_h.)*

---

## 14. Perguntas de prova que estas tabelas respondem
- "Quantos RTTs para carregar uma página com *n* objetos em HTTP não persistente / persistente / com pipelining?" → §4.
- "Por que a persistência melhora o desempenho?" → evita 1 RTT de handshake por objeto **e** o slow start (§4, §8.1).
- "Por que usar UDP para uma transação rápida?" → 1 RTT × 2 RTT (§2).
- "Quanto tempo para resolver um nome?" → §3.
- "Qual a vantagem do fast retransmit?" → ≈ 1–1,5 RTT × RTO (§7).
- "Por que o stop‑and‑wait é ineficiente?" → n·RTT (§6.1).
