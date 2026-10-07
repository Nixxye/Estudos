# O fluxo completo de uma comunicação na Internet
### Do clique no navegador até a página na tela — de onde cada mensagem sai, por onde passa e quem a interpreta

> **Para que serve este arquivo:** juntar tudo o que a disciplina viu (Introdução → Aplicação → Transporte) numa **única história contínua**. Primeiro o panorama (§1–2); depois cada etapa com zoom nas minúcias (§3); depois as variantes (§4) e as tabelas de consulta rápida (§5).
> **Convenção:** ✅ = visto na disciplina (detalhado) · 🔎 = **existe**, mas ainda não foi visto — só citado, para você saber onde ele se encaixa.
> Teoria completa de cada peça: [Resumo_P1_Redes.md](Resumo_P1_Redes.md). Exemplos numéricos: Resumo §8.

---

# 1. O cenário que vamos seguir

Você está num notebook, no Wi‑Fi do campus, e digita no navegador:

```
http://www.utfpr.edu.br/index.html
```

Personagens (valores inventados, só para ilustrar):

| Quem | Papel | Endereço IP | Porta |
|---|---|---|---|
| **Notebook** | cliente (navegador = cliente HTTP) | `10.0.0.5` | efêmera, ex. **52114** |
| **DNS local** | resolvedor recursivo do campus | `10.0.0.2` | **53** (UDP) |
| **Roteador do campus** | primeiro salto (gateway) | `10.0.0.1` | — |
| **Servidor Web** | servidor HTTP da UTFPR | `200.134.18.157` | **80** (TCP) |
| Servidores **Raiz / TLD .br / Autoritativo** | hierarquia DNS | vários | **53** (UDP) |

> Lembrete essencial: **cliente** é quem toma a iniciativa; **servidor** é quem espera. O notebook é cliente do DNS e cliente do HTTP. O DNS local é *servidor* para o notebook e *cliente* para a raiz/TLD/autoritativo. (Resumo §2.1)

---

# 2. O panorama em uma página

```
 NOTEBOOK (cliente)                                                         SERVIDOR WEB
 ┌────────────────────┐                                              ┌────────────────────┐
 │ ① Navegador: URL   │                                              │ ⑦ Processo HTTP    │
 │ ② Pergunta DNS ────┼──UDP/53──► DNS LOCAL ──► Raiz ► TLD ► Autor. │   lê GET, monta    │
 │    recebe IP ◄─────┼──────────  (cache, TTL)   (iterativo)        │   resposta 200 OK  │
 │ ③ socket TCP       │                                              │         ▲          │
 │    connect()  ─────┼──SYN──────────────────────────────────────►  │ ⑥ socket de conexão│
 │               ◄────┼──SYN+ACK──────────────────────────────────── │   (accept)         │
 │               ─────┼──ACK──────────────────────────────────────►  │   demux pela       │
 │ ④ HTTP GET    ─────┼──segmentos TCP───►ROTEADORES (núcleo)───────►│   quádrupla        │
 │ ⑧ recebe resposta◄─┼──segmentos TCP (ACKs, rwnd, cwnd)◄───────────┤ ⑦ envia resposta   │
 │ ⑨ renderiza; pede  │                                              │                    │
 │   imagens/CSS…     │                                              │                    │
 │ ⑩ FIN/ACK (ou keep-│                                              │                    │
 │   alive)           │                                              │                    │
 └────────────────────┘                                              └────────────────────┘
        ▲   Em cada seta: Aplicação → Transporte → Rede → Enlace → Física (envio),
        └── e o caminho inverso no receptor. Roteadores só olham até a camada de REDE.
```

**As 10 etapas, em uma linha cada**

| # | Etapa | Quem fala com quem | Protocolo / camada | RTTs gastos |
|---|---|---|---|---|
| 0 | Preparo da rede do host | notebook ↔ rede local | 🔎 DHCP, ARP, Wi‑Fi | (já feito antes) |
| 1 | Usuário digita a URL | usuário → navegador | Aplicação | 0 |
| 2 | Descobrir o IP do servidor | notebook ↔ DNS local ↔ hierarquia | **DNS / UDP 53** ✅ | ~1 (cache vazio: mais, só no DNS local) |
| 3 | Abrir a conexão | notebook ↔ servidor | **TCP handshake** ✅ | **1** |
| 4 | Enviar a requisição | notebook → servidor | **HTTP** sobre TCP ✅ | — |
| 5 | Atravessar a rede | roteadores no meio | IP, enlace 🔎 (+ atrasos ✅) | metade do RTT cada sentido |
| 6 | Chegar ao processo certo | SO do servidor → processo | **Demux TCP (quádrupla)** ✅ | — |
| 7 | Servidor processa e responde | servidor | HTTP ✅ | — |
| 8 | Resposta de volta, com controle | servidor → notebook | **TCP: ACK, rwnd, cwnd** ✅ | **1** (até o 1º byte) |
| 9 | Renderizar e buscar mais objetos | notebook ↔ servidor | HTTP persistente/pipelining ✅ | 1 por rodada |
| 10 | Encerrar | ambos | **TCP FIN/ACK** ✅ | — |

**Custo mínimo de tempo (primeira página, sem cache):** `DNS + 1 RTT (handshake) + 1 RTT (GET/1º byte) + T_trans` — é a fórmula `2·RTT + T_trans` do HTTP não persistente, mais o DNS. (Resumo §2.4)

---

# 3. Passo a passo com zoom nas minúcias

## Etapa 0 — Antes de tudo: o notebook já "entrou na rede" 🔎
Isto **não** foi estudado em detalhe, mas é o que dá ao notebook o que ele precisa:
- **DHCP** 🔎 (portas 67/68): entrega ao host seu **IP**, a **máscara/gateway** e o **endereço do DNS local**. *(O slide de DNS cita: "o endereço do servidor DNS local é fornecido via DHCP".)*
- **Wi‑Fi (IEEE 802.11)** 🔎: meio **compartilhado**, camada de enlace/física (✅ citado em Redes de acesso, A1).
- **ARP** 🔎: descobre o **MAC** do gateway a partir do IP dele.
Sem isso o notebook não tem IP de origem, não sabe quem é o DNS e não sabe para onde mandar pacotes "para fora".

---

## Etapa 1 — O usuário digita a URL (camada de aplicação) ✅
**Onde:** dentro do navegador, no notebook (espaço do usuário).
**O que acontece:**
1. O navegador **divide a URL**: `esquema = http`, `host = www.utfpr.edu.br`, `caminho = /index.html`. (A URL tem a forma `esquema://host/caminho`.)
2. Consulta o que já sabe localmente: **cache do navegador** (objeto ainda válido?) e **cookies** desse site (para anexar `Cookie: id` se houver). Se o objeto está em cache, pode fazer um **GET condicional** (`If-Modified-Since`) e receber `304 Not Modified` depois.
3. Decide a porta: `http` → **80** (`https` → 443).
4. Para falar com o servidor precisa de **IP**, não de nome → vai para o DNS.

**Particularidades**
- O navegador é só uma **aplicação**; o **HTTP é o protocolo** que ela fala (aplicação ≠ protocolo de aplicação). (Resumo §2.1)
- Quem inicia = **cliente**. O processo do navegador é o processo cliente.
- Nada de rede foi usado ainda.

---

## Etapa 2 — Descobrir o IP: DNS ✅
**De onde sai / para onde vai:** do notebook (`10.0.0.5:porta efêmera`) para o **DNS local** (`10.0.0.2:53`), por **UDP**.

### 2.1 Quem é consultado primeiro (e por quê)
O sistema operacional tem um pequeno **cache DNS local** (a slide cita `ipconfig /displaydns`). Se não há o nome, o host pergunta ao **servidor DNS local** (configurado via DHCP). Essa consulta é **recursiva**: o host quer a resposta pronta e não quer percorrer a hierarquia.

### 2.2 A mensagem DNS
- Formato único para consulta e resposta: **ID (16 bits)** que "casa" a resposta com a pergunta; **flags** (QR=0 consulta/1 resposta; RD recursão desejada; RA recursão disponível; AA resposta autoritativa); contadores; seções *Questões / Respostas / Autoridade / Adicionais*.
- Viaja sobre **UDP, porta 53**: sem handshake, 1 pacote de ida e 1 de volta (transação rápida). Se a resposta se perder, **a aplicação** (o resolvedor) reenvia por timeout — o UDP não faz nada.

### 2.3 O que o DNS local faz se não tem em cache (iterativo)
```
Notebook ──(1) "IP de www.utfpr.edu.br?" ─────────────────► DNS local        (recursiva)
DNS local ─(2) ─────────────────────────────────────────────► RAIZ
DNS local ◄(3) "pergunte ao TLD .br (NS/A)" ────────────────  RAIZ           (referência)
DNS local ─(4) ─────────────────────────────────────────────► TLD .br
DNS local ◄(5) "pergunte ao autoritativo de utfpr.edu.br" ──  TLD .br
DNS local ─(6) ─────────────────────────────────────────────► AUTORITATIVO
DNS local ◄(7) A www.utfpr.edu.br = 200.134.18.157, TTL ───── AUTORITATIVO
Notebook ◄─(8) 200.134.18.157 ────────────────────────────── DNS local
```
- 8 mensagens com cache vazio; **2** se o DNS local já tem o nome; entre elas, se tem o TLD em cache, pula a raiz.
- **Cache + TTL:** o DNS local guarda o resultado até o TTL expirar (definido pelo dono do domínio).
- **Registros:** A (nome→IPv4), NS (domínio→servidor autoritativo), CNAME (apelido→nome canônico; se `www` for CNAME, há mais uma resolução), MX (e-mail), TXT.
- Um mesmo nome pode devolver **vários IPs** (distribuição de carga).

### 2.4 Resultado e custo
O notebook agora tem `200.134.18.157`. Tempo gasto: ~1 RTT até o DNS local se estiver em cache; mais alguns RTTs (entre DNS local e hierarquia) se não estiver.

**Particularidades**
- O DNS usa **UDP** porque a troca é curta (transação de 1 pacote) — vantagem de latência sem handshake.
- **Segurança:** DNS poisoning (cache envenenado); contramedidas citadas no e‑mail (SPF/DKIM usam registros TXT).
- A hierarquia: Raiz (13 identificadores A–M, *anycast*) → TLD → Autoritativo. O DNS local **não** é da hierarquia oficial.

---

## Etapa 3 — Abrir a conexão TCP (handshake de 3 vias) ✅
**Pré-requisito:** o programa precisa de um **socket**.

### 3.1 Criação do socket (lado cliente)
```python
client = socket(AF_INET, SOCK_STREAM)   # TCP, IPv4
client.connect(('200.134.18.157', 80))  # dispara o handshake
```
- O sistema operacional escolhe uma **porta efêmera** de origem (49152–65535), ex. **52114**.
- A conexão passa a ser identificada pela **quádrupla**: `(10.0.0.5, 52114, 200.134.18.157, 80)`.

### 3.2 O handshake (1 RTT)
```
Notebook (10.0.0.5:52114)                      Servidor (200.134.18.157:80)
   |── SYN=1, Seq=x ───────────────────────────►|   servidor: socket de BOAS-VINDAS (listen)
   |◄─ SYN=1, ACK=1, Seq=y, ACK=x+1 ────────────|
   |── ACK=1, Seq=x+1, ACK=y+1 ─────────────────►|   servidor aloca estado definitivo (ESTAB)
```
- **x e y** = números de sequência iniciais (ISN), aleatórios.
- Por que 3 vias e não 2? Com 2 vias, um pedido antigo atrasado criaria conexão **meio-aberta** (recursos alocados à toa). O 3º passo prova que o cliente ainda quer a conexão.
- O 3º segmento já pode carregar dados.
- No servidor: o **socket de boas-vindas** só atende pedidos; o `accept()` devolve um **socket de conexão novo e dedicado** ao notebook.

**Particularidades**
- Estado da conexão existe **somente nos dois hosts**, nunca nos roteadores.
- Para o TCP funcionar, o **servidor precisa estar rodando antes** (senão o SYN não é aceito).
- Cada segmento já carrega o campo **rwnd** (janela anunciada) e opções (MSS, SACK, window scaling).

---

## Etapa 4 — Montar e enviar a requisição HTTP ✅

### 4.1 O que a aplicação entrega ao TCP
Uma **sequência de bytes** de texto ASCII (o TCP não preserva "fronteiras de mensagem"):
```
GET /index.html HTTP/1.1\r\n
Host: www.utfpr.edu.br\r\n
User-Agent: ...\r\n
Connection: keep-alive\r\n
Cookie: 1678\r\n          ← se houver cookie
\r\n
```

### 4.2 O que o TCP faz com esses bytes
1. Numera cada byte: se o 1º byte desta requisição é `x+1`, o segmento leva `Seq = x+1`.
2. Corta em segmentos de até **MSS** bytes (requisição curta → 1 segmento).
3. Monta o **cabeçalho TCP** (20–60 B): porta origem 52114 | porta destino 80 | Seq | ACK | flags (ACK=1) | **rwnd** | checksum.
4. Limita o que pode estar "em voo" por **min(cwnd, rwnd)**. Em conexão nova, `cwnd` começa em 1 MSS (**slow start**).
5. **Liga o timer** do segmento mais antigo sem ACK; `TimeoutInterval = EstimatedRTT + 4·DevRTT` (valor inicial conservador, já que o handshake deu a 1ª amostra de RTT).

### 4.3 Encapsulamento camada por camada (no notebook)
```
APLICAÇÃO   [ GET /index.html HTTP/1.1 ... ]                         → mensagem
TRANSPORTE  [ TCP: 52114→80, Seq, ACK, rwnd ][ mensagem ]            → segmento
REDE        [ IP: 10.0.0.5 → 200.134.18.157, TTL ][ segmento ]       → datagrama
ENLACE      [ Wi-Fi/Ethernet: MAC notebook → MAC do GATEWAY ][ datagrama ][ FCS/CRC ] → quadro
FÍSICA      bits como sinais de rádio
```
- Camada de **rede** 🔎: o **IP de destino é o do servidor**, mas o quadro vai para o **MAC do gateway** (o servidor não está na rede local). O host não sabe o caminho inteiro, só sabe "isto não é daqui; entregue ao gateway".
- Camada de **enlace** ✅/🔎: MAC e CRC para o salto **local**.

**Particularidades**
- Cada camada trata o que recebe de cima como **dados puros** e acrescenta seu cabeçalho (encapsulamento). Cada cabeçalho tem o endereço relevante para sua camada: **porta** (transporte), **IP** (rede), **MAC** (enlace).
- **Quem é o par?** Cada camada "conversa" logicamente com a **mesma camada** do outro lado: o TCP do notebook com o TCP do servidor (processo a processo), o IP do notebook com o IP de cada roteador.

---

## Etapa 5 — Atravessar a rede (os saltos) ✅ (atrasos) / 🔎 (roteamento)

### 5.1 O que acontece em cada roteador
```
quadro chega → remove cabeçalho de enlace → lê o IP DESTINO → consulta tabela de rotas 🔎
             → decrementa TTL 🔎 → escolhe interface de saída → põe NOVO cabeçalho de enlace
             → enfileira na saída → transmite
```
- O roteador **só olha até a camada de rede** (IP). Não abre o TCP, não vê o HTTP. É o princípio da **inteligência na borda / núcleo simples**.
- **Os endereços que mudam e os que não mudam:**

| Campo | Muda a cada salto? |
|---|---|
| IP origem / IP destino | **Não** (fim-a-fim) — (fora NAT 🔎) |
| Porta origem / destino, Seq, ACK | **Não** (só os hosts leem) |
| MAC origem / destino | **Sim** — a cada enlace |
| TTL | **Sim** — diminui 1 a cada roteador |

### 5.2 Os 4 atrasos em cada nó ✅
```
d_nodal = d_proc + d_fila + d_trans + d_prop
```
- **d_proc:** verificar cabeçalho/erros, consultar a rota (μs).
- **d_fila:** esperar na fila de saída (variável; sobe com o congestionamento; buffer cheio ⇒ **perda**).
- **d_trans = L/R:** empurrar os L bits no enlace de taxa R (**store-and-forward**: o roteador só retransmite depois de receber o pacote inteiro).
- **d_prop = d/s:** o sinal viajar pelo meio (fibra ≈ 2×10⁸ m/s).

### 5.3 A estrutura por onde o pacote passa ✅
Rede de acesso (Wi‑Fi do campus) → roteador do campus → **ISP regional** (ex.: **RNP**, Tier‑2) → **Tier‑1** (peering entre eles) → ISP do destino → servidor. **IXP** = pontos de troca de tráfego. Redes de conteúdo (Google) fazem *bypass*. Com `traceroute` você vê os saltos (cada linha = 1 roteador; `* * *` = não respondeu).

### 5.4 O que pode dar errado no caminho (e quem corrige)
| Problema | Quem percebe | Correção |
|---|---|---|
| Bit corrompido | CRC no enlace; **checksum TCP** no destino | descarte → o TCP retransmite |
| Pacote perdido (fila cheia) | remetente TCP (timeout / 3 dups) | retransmissão + **redução de cwnd** |
| Pacote fora de ordem | receptor TCP | ACK duplicado; reordena no buffer |
| Pacote duplicado | receptor TCP | descarta pelo Seq |
| Atraso grande | RTT medido | timeout adaptativo |

> O IP **não garante nada** (melhor esforço). Toda a "confiabilidade" vem do **TCP nas pontas**.

### 5.5 Roteamento entre redes 🔎
Como os roteadores montam suas tabelas (OSPF dentro de uma rede; **BGP** entre ISPs) e como o IP é endereçado/sub-dividido (máscara, sub-redes, CIDR) **ainda não foram vistos** — a disciplina só os cita ao dizer que a camada de rede "roteia e endereça datagramas".

---

## Etapa 6 — Chegar ao processo certo no servidor: demultiplexação ✅

**Cadeia no servidor (de baixo para cima):**
```
FÍSICA: bits → ENLACE: confere CRC, vê que o MAC é dele, remove o cabeçalho
→ REDE: vê IP destino = ele mesmo, remove o cabeçalho IP; campo "protocolo = 6" → TCP 🔎
→ TRANSPORTE (TCP): confere checksum; faz DEMUX pela QUÁDRUPLA
```
**Demux TCP.** O SO procura um socket com
`(IP origem 10.0.0.5, porta origem 52114, IP destino 200.134.18.157, porta destino 80)`.
- Se for um segmento `SYN`: o alvo é o **socket de boas-vindas** (porta 80, `listen`).
- Se a conexão já existe: vai para o **socket de conexão dedicado** criado pelo `accept()`.
- Se vierem requisições de **outro cliente** (outra origem), irão para **outro socket**, mesmo com a porta 80 igual.

> Para comparação, em **UDP** o demux usaria só `(IP destino, porta destino)`: vários clientes caem **no mesmo socket** e a aplicação lê a origem pelo `recvfrom()`. (Resumo §4.2)

**O TCP do servidor:**
1. Confere o **Seq** (é o byte esperado?). Se sim, coloca os bytes no buffer do socket e gera **ACK** (`ACK = Seq + len`), normalmente **atrasado** até 500 ms ou imediato se há outro segmento pendente; se for fora de ordem → **ACK duplicado imediato**.
2. Atualiza o **rwnd** que anunciará: `RcvBuffer − dados ainda não lidos`.
3. O processo do servidor Web (que está em `recv()`) lê os bytes.

---

## Etapa 7 — O servidor processa e monta a resposta ✅
O processo HTTP (Apache/Nginx; um socket por conexão — thread, processo ou laço de eventos) faz:
1. **Parser** da requisição: método, URL, versão, cabeçalhos, cookie.
2. Localiza o objeto (`/index.html`) ou executa um programa (PHP + banco). Se houve `If-Modified-Since` e não mudou → `304 Not Modified` sem corpo.
3. Monta a **resposta**:
```
HTTP/1.1 200 OK\r\n
Date: ...\r\n  Server: Apache\r\n  Last-Modified: ...\r\n
Content-Length: 2652\r\n  Content-Type: text/html\r\n
Set-Cookie: 1678\r\n          ← primeira visita
\r\n
[2652 bytes de HTML]
```
- Códigos possíveis: 200, 301 (+`Location`), 304, 400, 404, 500, 505.
- Pelo fato de o HTTP ser **stateless**, o servidor não "lembra" a requisição anterior; se há cookie, ele consulta seu banco de dados para recuperar a sessão.

**Particularidades**
- O HTTP não implementa ACKs nem retransmissões — **delega ao TCP**.
- O servidor pode estar atrás de um **proxy/cache** (se ele interceptar, responde sem incomodar o servidor de origem — "hit").

---

## Etapa 8 — A resposta volta (e aí entram fluxo e congestionamento) ✅

### 8.1 O trajeto de volta
Mesma estrutura, **origem e destino invertidos**:
```
TCP: porta origem 80 → porta destino 52114
IP : 200.134.18.157 → 10.0.0.5
Enlace: novos MACs a cada salto
```
O caminho de ida **não precisa ser o mesmo** da volta.

### 8.2 Quanto o servidor pode enviar de uma vez? `min(cwnd, rwnd)`
A resposta de 2652 B + cabeçalhos cabe em 2 segmentos (MSS ≈ 1460 B), mas o **TCP não despeja nada sem olhar duas janelas**:

| Janela | Quem calcula | Protege | Valor inicial |
|---|---|---|---|
| **rwnd** | o **notebook** (receptor), no cabeçalho de **cada** segmento | o buffer do receptor (**controle de fluxo**) | espaço livre do `RcvBuffer` |
| **cwnd** | o **servidor** (remetente), por inferência | a rede (**controle de congestionamento**) | **1 MSS** (slow start) |

- **Slow start:** `cwnd` +1 MSS a cada ACK ⇒ dobra a cada RTT (1, 2, 4, 8…). Por isso uma resposta grande leva **vários RTTs** mesmo com banda de sobra. (Em HTTP não persistente, isso recomeça a cada objeto.)
- **Congestion avoidance** quando `cwnd ≥ ssthresh`: +1 MSS por RTT.
- **rwnd = 0:** o servidor para e sonda com 1 byte.

### 8.3 Cada segmento de dados e o ACK correspondente
```
Servidor                                                Notebook
 |── Seq=y+1, 1460 B (dados HTTP) ───────────────────────►|  em ordem: ACK atrasado/cumulativo
 |── Seq=y+1461, 1192 B ─────────────────────────────────►|  em ordem + outro pendente: ACK imediato
 |◄─ ACK = y+2653, rwnd = ... ────────────────────────────|
```
- `ACK` = próximo byte esperado (cumulativo); pode ir de carona (**piggybacking**) em dados do cliente, ou segmento só de ACK.

### 8.4 Se algo falha
| Evento | Reação do TCP (servidor = remetente) |
|---|---|
| Segmento perdido, os seguintes chegam | notebook envia **ACK duplicado** do byte faltante; **3 dups ⇒ fast retransmit**; `ssthresh = cwnd/2`, `cwnd = ssthresh` (Reno) |
| Nada chega (ou todos os ACKs somem) | **timeout** ⇒ retransmite o mais antigo, `ssthresh = cwnd/2`, `cwnd = 1`, **dobra o timeout** (backoff) |
| ACK perdido | ACK cumulativo seguinte cobre; senão, retransmite por timeout (duplicata é descartada pelo receptor) |
| Timeout prematuro | retransmissão desnecessária; receptor descarta duplicata |
| Receptor lento | `rwnd` cai até 0 |

O **timeout** é calculado continuamente: `EstimatedRTT = 0,875·Est + 0,125·Sample`, `DevRTT = 0,75·Dev + 0,25·|Sample − Est|`, `Timeout = Est + 4·Dev`. **Karn:** ignora amostras de segmentos retransmitidos.

---

## Etapa 9 — O notebook entrega à aplicação e continua ✅
1. O TCP do notebook **reordena** os bytes (usa o Seq) e entrega ao navegador o fluxo contínuo (o navegador usa `Content-Length` para saber onde acabou a resposta).
2. O navegador lê status + cabeçalhos; **guarda o cookie** (`Set-Cookie`); **armazena em cache** o objeto.
3. Ao processar o HTML, descobre **N objetos referenciados** (imagens, CSS, JS). Cada um tem sua URL (talvez em outro servidor → novo DNS + nova conexão).
4. Estratégias de busca:

| Modo | Como | Custo (HTML + 10 imagens) |
|---|---|---|
| HTTP/1.0 não persistente | 1 objeto por conexão TCP (handshake + slow start novamente) | 22 RTT |
| HTTP/1.1 persistente sem pipelining | reusa a conexão, um GET por vez | ≈ 12 RTT |
| HTTP/1.1 persistente com pipelining | GETs em lote; respostas em ordem (**HoL**) | ≈ 3 RTT |
| Conexões paralelas (navegador) | 5–8 conexões ao mesmo tempo | menos RTTs, mais carga na rede |
| HTTP/2 | multiplexa streams numa conexão TCP | sem HoL da aplicação |
| HTTP/3 (QUIC/UDP) | streams independentes; TLS 1.3 embutido; 1‑RTT / 0‑RTT | sem HoL do transporte |

---

## Etapa 10 — Encerramento ✅
- **Persistente:** a conexão fica aberta (keep‑alive) até timeout/`Connection: close`.
- **Fechamento TCP:** cada lado envia `FIN` e recebe `ACK` independentemente (4 segmentos, ou 3 se o ACK e o FIN do segundo lado vão juntos). Quem fecha por último fica em `TIME_WAIT` (2·MSL) e depois `CLOSED`.
- O socket de conexão no servidor é liberado; o **socket de boas‑vindas segue** esperando novos clientes.

---

# 4. Variantes do mesmo fluxo (o que muda)

## 4.1 Aplicação sobre **UDP** (ex.: o próprio DNS, VoIP) ✅
```
cliente: socket(SOCK_DGRAM) → sendto(IP, porta) ─► servidor: bind → recvfrom (recebe dados + origem) → sendto(origem)
```
- **Sem** handshake, sem Seq/ACK, sem controle de fluxo/congestionamento, sem retransmissão automática.
- Cabeçalho de 8 B (portas, comprimento, checksum).
- O servidor tem **1 socket** para todos; a aplicação lê a origem.
- Confiabilidade, se houver, é implementada **pela aplicação** (ex.: reenviar a consulta DNS se não houver resposta).

## 4.2 **E‑mail** (SMTP + acesso) ✅
```
UA da Alice ──SMTP(push)──► servidor da Alice ──SMTP/TCP 25──► servidor do Bob ◄──IMAP/POP3(pull)── UA do Bob
```
- O **servidor de origem fala direto com o de destino** (sem intermediários de aplicação); por isso, antes, o servidor da Alice usa o **DNS (registro MX)** para achar o servidor de e‑mail do Bob.
- Fases SMTP: apresentação (`HELO`) → `MAIL FROM`/`RCPT TO`/`DATA`/`.` → `QUIT`; ASCII de 7 bits + **MIME** para anexos.
- Se o destino está fora do ar, o servidor mantém a mensagem na **fila** e retenta.
- Leitura: POP3 (baixa e apaga), IMAP (sincroniza), Webmail (HTTP, o servidor web traduz).
- SPF/DKIM/DMARC (consultas DNS TXT) contra spoofing.

## 4.3 **P2P / BitTorrent** ✅
```
peer ─HTTP─► site (obtém .torrent) ─► tracker (lista de IPs) ─► conexões TCP diretas com outros peers (cliente E servidor)
```
- Sem servidor central de dados; *rarest first*, *tit‑for‑tat*.
- Dificuldade: IPs dinâmicos e **NAT** 🔎.

## 4.4 **Web cache / CDN / proxy no caminho** ✅
O navegador pode falar com um **proxy** em vez de com a origem: *hit* ⇒ resposta local (reduz atraso e carga no link de acesso); *miss* ⇒ o proxy vira cliente da origem e repete as etapas 2–9 por conta própria.

## 4.5 **HTTPS / TLS** ✅ (conceito) / 🔎 (detalhes)
Entre as etapas 3 e 4 entra o **handshake TLS** (autenticação por certificado X.509, chaves, cifra simétrica). TLS roda **na aplicação** sobre TCP e usa a porta 443. Com HTTP/3, o TLS 1.3 vai embutido no handshake do QUIC (1 RTT).

---

# 5. Tabelas de consulta rápida

## 5.1 "Quem lê o quê" — o destino de cada cabeçalho
| Cabeçalho | Quem **escreve** | Quem **lê** | Roteadores leem? |
|---|---|---|---|
| Mensagem HTTP/DNS/SMTP | aplicação do remetente | aplicação do destinatário | **Não** |
| TCP/UDP (portas, seq, ack, rwnd, checksum) | transporte do remetente | transporte do destinatário | **Não** |
| IP (origem, destino, TTL, protocolo) | rede do remetente | **cada roteador** + rede do destinatário | **Sim** |
| Enlace (MAC, CRC) | enlace de cada salto | enlace do salto seguinte | Só no enlace local |

## 5.2 "Quem decide o quê" — onde está a inteligência
| Decisão | Quem decide | Camada |
|---|---|---|
| Qual servidor/URL buscar | navegador | Aplicação |
| Qual IP corresponde ao nome | DNS (local + hierarquia) | Aplicação |
| TCP ou UDP; porta | programador (escolhe `SOCK_STREAM`/`SOCK_DGRAM`) | Aplicação/API |
| Retransmitir, janela, timeout, ordem | **TCP nos hosts** | Transporte |
| Quanto enviar de uma vez | `min(cwnd, rwnd)` | Transporte |
| Por onde o pacote vai | roteadores (tabelas de rota) 🔎 | Rede |
| Quem entrega no meio físico | enlace/física | Enlace |

## 5.3 Particularidades por etapa (cola de uma linha)
| Etapa | O que não pode esquecer |
|---|---|
| DNS | recursiva host→local, iterativa local→hierarquia; UDP/53; cache+TTL |
| Handshake | 3 vias evitam half‑open; servidor deve estar rodando; 1 RTT |
| Requisição | texto ASCII; linha em branco termina cabeçalhos; GET sem corpo |
| Encapsulamento | porta (transporte) · IP (rede) · MAC (enlace) |
| Roteadores | só até IP; IP fixo, MAC muda; store‑and‑forward; 4 atrasos |
| Demux | TCP = quádrupla (socket por conexão); UDP = (IP,porta) destino |
| Resposta | portas e IPs invertidos; ACK = próximo byte; status line |
| Fluxo | `rwnd` do receptor; sondas de 1 byte se zero |
| Congestionamento | `cwnd` do remetente; SS → CA; 3 dups × timeout |
| Fechamento | FIN/ACK em cada sentido; TIME_WAIT |

## 5.4 Linha do tempo do caso completo (cache vazio, HTTP/1.1, sem pipelining)
```
t=0        Usuário digita URL
t≈RTT_dns  IP obtido (DNS)
+1 RTT     Handshake TCP concluído (SYN → SYN+ACK → ACK)
+1 RTT     GET enviado → 1º byte da resposta chega (HTML)
+T_trans   Último byte do HTML (L/R)  [+ slow start: mais RTTs se a resposta for grande]
+1 RTT     por objeto adicional (ou ≈ 1 RTT para todos com pipelining)
fim        FIN/ACK (se a conexão não for mantida)
```

---

# 6. O que ainda NÃO foi visto (apenas existe) 🔎

| Tema | Onde se encaixa no fluxo | Em uma frase |
|---|---|---|
| **Camada de rede / IP** (endereçamento, sub-redes, CIDR) | Etapas 4–6 | Define o endereço do host e como o datagrama é encaminhado de ponta a ponta |
| **Roteamento** (OSPF, BGP, tabelas de rotas) | Etapa 5 | Como os roteadores decidem a "próxima interface" |
| **ICMP** | `ping`/`traceroute` | Mensagens de erro/controle da camada de rede (TTL expirado, etc.) |
| **NAT** | Entre o campus e a Internet | Troca IP/porta privados por públicos; atrapalha P2P |
| **DHCP** | Etapa 0 | Dá IP, gateway e DNS local ao host |
| **ARP** | Etapa 4 | Descobre o MAC a partir do IP no mesmo enlace |
| **Camada de enlace** (Ethernet, Wi‑Fi, CRC, switches, VLAN) | Etapa 4–5 | Entrega do quadro de um nó ao vizinho direto |
| **Camada física** | Etapa 4 | Codificação de bits no meio |
| **TLS em detalhes** | Entre 3 e 4 | Certificados, trocas de chaves, cifras |
| **Segurança de rede** (firewalls, VPN, IPsec) | Etapa 5 | Filtros e túneis no caminho |
| **Multicast/broadcast, IPv6** | Rede | Endereçamento/difusão |
| **Redes sem fio e móveis** (Wi‑Fi MAC, celular) | Etapa 0/4 | Acesso compartilhado, mobilidade |

Todos esses vão preencher a "caixa preta" entre o **segmento TCP saindo do notebook** e o **segmento TCP chegando ao servidor** — exatamente o buraco que, por enquanto, aparece nos diagramas como "roteadores (núcleo)".

---

# 7. Checklist para testar se você entendeu o fluxo
1. Em cada etapa, diga: **quem** envia, **para quem**, **qual protocolo**, **qual porta** e **qual cabeçalho** foi acrescentado.
2. Por que o DNS usa UDP e o HTTP usa TCP? O que muda no custo em RTTs?
3. O que identifica o socket do servidor no demux TCP? E no UDP?
4. Por que o servidor tem dois tipos de socket? E por que precisa subir antes?
5. O que os roteadores leem e o que nunca leem?
6. Que endereços mudam salto a salto e quais não?
7. Quantos RTTs para HTML + 10 imagens em cada modo HTTP?
8. Qual a diferença entre `rwnd` e `cwnd`: quem calcula, quem informa, que problema resolve?
9. O que o remetente faz num timeout? E em 3 ACKs duplicados?
10. Em qual momento o cookie é criado, guardado e reenviado?
