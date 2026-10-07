# Redes de Computadores 1 — Resumo para a P1

> Baseado nos slides A1–A6 (+ aula4-a e aula4-d) e no padrão das provas anteriores (2013, 2014 oral, 2015).
> Escopo assumido: **Introdução → Aplicação → Transporte (UDP, rdt, TCP, congestionamento)**.
> Legenda de prioridade: 🔥 cai muito em prova · ⭐ importante · (sem marca) cultura/apoio.

---

## Mapa da matéria

| Aula | Tema | Peso na prova |
|---|---|---|
| A1 | Introdução: Internet, comutação, atrasos, camadas | ⭐ (base) |
| A2 | Aplicação: arquiteturas, portas, HTTP, cookies, cache | 🔥 |
| A3 | SMTP/e-mail, DNS, P2P/BitTorrent, sockets | 🔥 (DNS), ⭐ |
| A4 | Transporte: mux/demux, UDP, rdt 1.0–3.0, GBN, SR | 🔥 |
| A5 | TCP: segmento, seq/ACK, RTT, fluxo, conexão | 🔥🔥 |
| A6 | Controle de congestionamento (AIMD, SS, CA, Reno) | 🔥🔥 |

As 3 provas antigas repetem as mesmas perguntas: **IP+porta, TCP vs UDP, sockets (1 vs 2), V/F do TCP, seq/ACK numérico, fluxo vs congestionamento, slow start vs CA, HTTP, DNS**. Domine essas.

---

# 1. Introdução (A1)

## 1.1 Componentes da Internet
- **Borda (edge):** hosts/sistemas finais (clientes, servidores, IoT).
- **Redes de acesso:** DSL, cabo (HFC), FTTH, Wi-Fi, 4G/5G, satélite. *Dedicado* (DSL, FTTH) × *compartilhado* (cabo, Wi-Fi, celular).
- **Núcleo (core):** malha de roteadores/switches; hierarquia de ISPs: **Tier-1** (peering gratuito entre si) → Tier-2 regionais → Tier-3 acesso; **IXP** = ponto de troca de tráfego; redes de conteúdo (Google) fazem bypass.
- **Protocolo** = define **formato**, **ordem** das mensagens e **ações** tomadas ao enviar/receber.
- Padronização: **IETF (RFCs)** — camadas altas (RFC 791 IP, 793 TCP, 9110 HTTP); **IEEE** — enlace/física (802.3 Ethernet, 802.11 Wi-Fi).

## 1.2 Comutação
| | Circuitos (FDM/TDM) | Pacotes |
|---|---|---|
| Recurso | reservado fim-a-fim (call setup) | sob demanda, **multiplexação estatística** |
| Desempenho | garantido, sem fila | filas, atraso variável, **perda** se buffer cheio |
| Rajadas | ineficiente (ocioso) | eficiente |
- Pacotes usam **store-and-forward**: o roteador recebe o pacote inteiro (L bits) antes de retransmitir.
- Exemplo clássico: link 1 Mbps, usuário 100 kbps ativo 10% do tempo → circuitos: 10 usuários; pacotes: ~35 usuários com P(>10 ativos) ≈ 0,0004.

## 1.3 Os 4 atrasos nodais 🔥
```
d_nodal = d_proc + d_fila + d_trans + d_prop
d_trans = L / R      (L = bits do pacote, R = taxa do enlace)   → NÃO depende da distância
d_prop  = d / s      (d = distância, s ≈ 2×10⁸ m/s em fibra)     → NÃO depende do tamanho do pacote
```
- **Intensidade de tráfego** `La/R` → 1 ⇒ atraso de fila → ∞; > 1 ⇒ perda.
- **Vazão (throughput)** fim-a-fim = `min{R1, R2, …, RN}` (gargalo).
- Ferramentas: `ping` (conectividade/RTT), `traceroute` (rota e atraso por salto; `* * *` = não respondeu), Wireshark (sniffer).

## 1.4 Camadas e encapsulamento
Pilha Internet (5 camadas) × OSI (7):

| Camada | PDU | Protocolos | Endereço |
|---|---|---|---|
| Aplicação (OSI 5-6-7) | Mensagem | HTTP, DNS, SMTP, FTP, SSH | — |
| Transporte | **Segmento** | TCP, UDP | **Porta** |
| Rede | **Datagrama** | IP, ICMP, BGP | **IP** |
| Enlace | **Quadro** | Ethernet, Wi-Fi | MAC |
| Física | Bit | — | — |

- **Encapsulamento:** cada camada adiciona seu cabeçalho: `Hl | Hn | Ht | Mensagem | Tl`.
- Sessão e Apresentação (OSI) **foram para a aplicação** (TLS, JSON/serialização, cookies/JWT).
- Regra prática: nunca mande memória bruta pela rede → *endianness* (`htons/htonl`, ordem de rede = big-endian) e *padding* ⇒ serialização.
- **Princípio fim-a-fim:** núcleo simples (só encaminha), inteligência nas bordas.

## 1.5 Segurança (Kurose §1.6)
Malware/botnets, **DoS/DDoS**, **packet sniffing**, **IP spoofing**. HTTP em texto claro é legível por sniffer; HTTPS (TLS) protege.

---

# 2. Camada de Aplicação (A2)

## 2.1 Arquiteturas 🔥
| | Cliente-Servidor | P2P |
|---|---|---|
| Servidor | sempre ligado, IP fixo, data center | não há servidor central |
| Clientes | não conversam entre si, IP dinâmico | pares são cliente **e** servidor |
| Escala | servidor é gargalo/SPOF | **auto-escalável** |
| Problemas | balanceamento de carga | churn, NAT, segurança |
| Exemplos | Web, e-mail | BitTorrent |

- **Cliente** = processo que **inicia** a comunicação; **servidor** = processo que **espera ser contatado**. Papéis são por sessão, não por máquina.
- Processos se comunicam por mensagens via **socket** (a "porta" entre app e transporte).

## 2.2 Endereçamento de processos 🔥
**Identificador do processo = (Endereço IP : Número de porta)**
- IP (32 bits IPv4 / 128 IPv6) identifica o **host** (camada de rede). Porta (16 bits, 0–65535) identifica o **processo/socket** (transporte).
- Portas: 0–1023 *well-known* (IANA), 1024–49151 registradas, 49152–65535 dinâmicas/efêmeras (clientes).
- **Decorar:** HTTP 80 · HTTPS 443 · DNS 53 · SSH 22 · FTP 21 (controle) · SMTP 25/587 · IMAP 143 · POP3 110 · DHCP 67/68.

## 2.3 O que a aplicação exige do transporte
1. **Perdas:** tolerante (áudio/vídeo) × intolerante (arquivos, e-mail, web).
2. **Temporização:** sensível a atraso (jogos, VoIP) × insensível.
3. **Vazão:** sensível (mínimo de taxa) × **elástica** (usa o que tiver).
4. **Segurança:** confidencialidade, integridade, autenticação (TLS).
- Internet oferece **melhor esforço**: nenhuma garantia de atraso nem de vazão mínima.

| Aplicação | Protocolo | Transporte |
|---|---|---|
| Web | HTTP | TCP (HTTP/3: QUIC/UDP) |
| E-mail | SMTP, POP3, IMAP | TCP |
| Transferência de arquivos | FTP, SFTP | TCP |
| Acesso remoto | SSH, Telnet | TCP |
| DNS | DNS | UDP (53) |
| Streaming | DASH, HLS | TCP (ou UDP) |
| VoIP | SIP, RTP | UDP (ou TCP) |

**Por que as apps de texto/arquivo usam TCP:** não toleram perda de bytes, e portas 80/443 passam por firewalls.
**TLS/SSL:** roda na aplicação, sobre TCP; dá confidencialidade (cifra simétrica), integridade (MAC), autenticação (certificado X.509).

## 2.4 HTTP 🔥🔥
- Protocolo da Web, **requisição/resposta**, sobre **TCP (porta 80)**; **stateless** (não guarda histórico → escalável e tolerante a falhas).
- Página = arquivo base HTML + objetos referenciados (cada um com URL `esquema://host/caminho`).

### Conexões
| Versão | Conexão | Comportamento |
|---|---|---|
| HTTP/1.0 (1996) | **não persistente** | 1 objeto por conexão TCP: **2 RTT + T_trans por objeto** |
| HTTP/1.1 (1997) | **persistente** (default), com **pipelining** | reusa a conexão; envia vários GET sem esperar resposta |
| HTTP/2 (2015) | persistente, binário, **multiplexação** de streams, HPACK | acaba o HoL **da aplicação** |
| HTTP/3 (2022) | **QUIC sobre UDP**, TLS 1.3 embutido | acaba o HoL **do transporte**; handshake 1-RTT / 0-RTT |

**Cálculos de tempo:**
- 1 objeto não persistente: `2·RTT + T_trans` (1 RTT handshake TCP + 1 RTT requisição/1º byte).
- HTML + 10 imagens, **não persistente sequencial:** `11 × (2·RTT) = 22·RTT + 11·T_trans`.
- **Persistente sem pipelining:** 1 RTT p/ handshake + 1 RTT por objeto.
- **Persistente com pipelining:** ~1 RTT de handshake + 1 RTT p/ o HTML + **~1 RTT p/ todas as imagens**.
- Navegadores mitigavam abrindo 5–8 conexões TCP em paralelo (custo: mais carga/ congestionamento).
- **Persistente sem paralelismo:** cliente só manda a próxima requisição após receber a resposta anterior. **Com paralelismo (pipelining):** manda as requisições em lote; **HTTP/1.1 usa a com pipelining.**
- **HoL blocking:** respostas do pipelining voltam em ordem FIFO; um objeto lento trava os outros.

### Formato das mensagens
```
Requisição:                          Resposta:
GET /index.html HTTP/1.1\r\n         HTTP/1.1 200 OK\r\n
Host: www.site.com\r\n               Date: ...\r\n
User-Agent: ...\r\n                  Server: Apache\r\n
Connection: keep-alive\r\n           Content-Length: 2652\r\n
\r\n  ← linha em branco              Content-Type: text/html\r\n
[corpo: vazio no GET, dados no POST] \r\n
                                     [dados do objeto]
```
- **Métodos:** GET, POST (dados no corpo), HEAD (só cabeçalhos), PUT (upload), DELETE. GET envia parâmetros na URL (`?a=b`) — nunca usar para senha.
- **Status:** 200 OK · 301 Moved Permanently (`Location`) · 304 Not Modified · 400 Bad Request · 404 Not Found · 500 Internal Server Error · 505 HTTP Version Not Supported.

### Cookies (estado sobre HTTP stateless)
4 componentes: (1) `Set-Cookie: id` na resposta; (2) `Cookie: id` nas requisições seguintes; (3) arquivo de cookies no navegador; (4) BD no servidor. Usos: login, carrinho, recomendações. Risco: rastreamento (cookies de terceiros) → LGPD.

### Web Cache / Proxy
- Proxy age como **servidor** para o cliente e **cliente** para a origem. **Hit:** responde local; **Miss:** busca na origem, guarda cópia.
- Benefícios: menor tempo de resposta, menos tráfego no link de acesso (caro), alivia origem.
- **GET condicional:** `If-Modified-Since: <data>` → servidor responde **304 Not Modified** (corpo vazio) ou 200 + novo objeto.
- Exemplo: LAN 10 Gbps, acesso 100 Mbps, 100 obj/s × 1 Mb, RTT internet 2 s. Sem cache: acesso a 100% (colapso). Com hit rate 40%: 60 req/s → 60% de uso; atraso = 0,4·0 + 0,6·2 = **1,2 s**.

### Telnet manual
`telnet gaia.cs.umass.edu 80` → digitar `GET ... HTTP/1.1`, `Host: ...`, Enter **duas vezes**.

---

# 3. E-mail, DNS, P2P e Sockets (A3)

## 3.1 E-mail
- Componentes: **Agente de Usuário (UA)**, **servidor de correio** (caixa postal + fila de saída), protocolos.
- **SMTP** (TCP 25/587, RFC 5321): **PUSH** — servidor de origem conecta **direto** ao servidor de destino. Texto ASCII 7 bits. 3 fases: apresentação (HELO) → transferência → encerramento (QUIT). O servidor é cliente SMTP ao enviar e servidor SMTP ao receber.
- Diálogo: `HELO` · `MAIL FROM:` · `RCPT TO:` · `DATA` · (corpo) · `.` sozinho numa linha · `QUIT`. Respostas: 220, 250, 354, 221.
- **Envelope** (MAIL FROM/RCPT TO — usado pelos servidores) × **Mensagem** (RFC 5322: cabeçalhos `From/To/Subject` + **linha em branco** + corpo).
- **MIME** (`Content-Type`, `Content-Transfer-Encoding: base64`, `boundary`) permite anexos binários e acentos sobre ASCII de 7 bits.
- **Acesso (PULL):** **POP3** (baixar e apagar; fases: autorização → transação [`list/retr/dele`] → atualização [`quit`]); **IMAP** (mensagens e pastas ficam no servidor, sincroniza vários dispositivos, stateful, pode baixar só cabeçalhos); **Webmail** (HTTP; o servidor web traduz para SMTP/IMAP).
- **HTTP × SMTP:** HTTP é *pull* (cliente puxa), cada objeto em sua resposta; SMTP é *push*, vários objetos numa única mensagem multipart.
- Anti-spoofing (via DNS/TXT): **SPF** (IP autorizado), **DKIM** (assinatura), **DMARC** (política: none/quarantine/reject).

## 3.2 DNS 🔥🔥
**Função:** traduzir nome ↔ IP. Serviços adicionais: **host aliasing** (CNAME), **mail server aliasing** (MX), **distribuição de carga** (vários IPs, round-robin).
**Por que não centralizar:** ponto único de falha, volume de tráfego, distância, manutenção.

**Hierarquia distribuída (árvore):**
1. **Raiz (13 identificadores A–M, anycast, >1600 instâncias)** → aponta para o TLD.
2. **TLD** (.com, .org, .br, .edu) → aponta para o autoritativo.
3. **Autoritativo** (da organização, ex. utfpr.edu.br) → dá o IP final.
4. **Servidor DNS local** (do ISP/campus, obtido via DHCP): **resolvedor recursivo** que faz o trabalho pelo host; não faz parte da hierarquia oficial. Tem **cache**.

**Consultas:**
- **Iterativa:** o servidor consultado responde com uma **referência** ("pergunte àquele"). O DNS local é quem percorre Raiz → TLD → Autoritativo (8 mensagens: host→local; local→raiz; local→TLD; local→autoritativo; respostas).
- **Recursiva:** o servidor consultado **assume** a busca, agindo como cliente do próximo nível; sobrecarrega o topo (por isso raiz/TLD geralmente desativam).
- **Cache + TTL:** mapeamentos guardados até o TTL expirar; evita consultar raiz/TLD. Risco: *DNS poisoning*.

**Registros (Name, Value, Type, TTL):**
| Type | Name | Value |
|---|---|---|
| **A** | hostname | IPv4 |
| **NS** | domínio | hostname do servidor autoritativo |
| **CNAME** | apelido | nome canônico |
| **MX** | domínio | nome do servidor de e-mail |
| **TXT** | — | texto (SPF/DKIM) |

**Mensagem DNS:** roda sobre **UDP/53**; cabeçalho 12 bytes: ID (16 b, casa pergunta/resposta), flags (QR 0=consulta/1=resposta, AA autoritativa, RD/RA recursão), contadores (perguntas, respostas, autoridade, adicionais) + seções Questões / Respostas / Autoridade / Adicionais.
**Registro de domínio:** registrar (Registro.br) insere no TLD os RRs NS e A (glue) do seu autoritativo; o registro A do NS quebra a dependência circular.

## 3.3 P2P e BitTorrent 🔥
**Tempo de distribuição de um arquivo de F bits para N clientes** (`u_s` upload do servidor, `d_min` download do pior cliente, `u_i` upload do peer i):
```
Cliente-servidor:  D_cs  ≥ max{ N·F / u_s ,  F / d_min }          → cresce linear com N
P2P:               D_p2p ≥ max{ F / u_s ,  F / d_min ,  N·F / (u_s + Σ u_i) }   → estabiliza
```
Exemplo (F = 15 Gb, u_s = 30 Mbps, d = 2 Mbps, u = 0,3 Mbps): N=1000 → C-S **138,8 h**, P2P **12,6 h**; N=10 → ambos 2,1 h (gargalo é o download).

**BitTorrent:** *torrent* (metadados: hashes + URL do tracker) · *tracker* (só lista IPs, não guarda arquivo) · *chunks* (~256 KB) · *swarm* (enxame). Peer novo chega com 0 chunks, pede IPs ao tracker, abre conexões TCP. Ao baixar um chunk já faz upload dele.
- **Rarest first:** pede primeiro os chunks mais raros.
- **Tit-for-tat:** envia (unchoke) para os 4 vizinhos que mais enviam; *leechers* egoístas ficam estrangulados (choked). Depois de completo: *seeder* (altruísta) ou *leecher* (sai).

## 3.4 Sockets 🔥
**Socket** = interface entre processo (espaço do usuário) e transporte (kernel). Acima: controle do programador; abaixo: SO.

| | UDP (`SOCK_DGRAM`) | TCP (`SOCK_STREAM`) |
|---|---|---|
| Conexão | nenhuma | handshake 3 vias |
| Unidade | datagramas independentes | **fluxo de bytes** (sem fronteiras de mensagem) |
| Servidor | `socket → bind → recvfrom/sendto` | `socket → bind → listen → accept → recv/send → close` |
| Cliente | `socket → sendto → recvfrom → close` | `socket → connect → send/recv → close` |
| Endereço | IP+porta em **cada** `sendto`; `recvfrom` devolve origem | fixado no `connect` |
| Sockets no servidor | **1** | **welcoming** (listen) **+ 1 de conexão por cliente** (criado pelo `accept`) |

- TCP: servidor precisa estar rodando **antes** (senão o `connect`/SYN falha); UDP: cliente pode rodar antes (datagrama só se perde).
- `listen(N)` = tamanho da fila de conexões pendentes. `bind(('',porta))` escuta em todas as interfaces. `.encode()/.decode()` = "apresentação".
- Decisões de projeto de protocolo: **stateful × stateless**, **confiável × tolerante a perda**, sinalização **in-band × out-of-band** (FTP usa dois canais), **C-S × P2P**.

---

# 4. Camada de Transporte (A4)

## 4.1 Conceito
- Transporte = comunicação lógica **processo-a-processo**; rede = **host-a-host** (analogia: Ana/Pedro entregam as cartas dentro da casa; Correios levam entre as casas).
- Emissor: quebra mensagens em segmentos; receptor: remonta e entrega ao socket certo.
- **TCP:** orientado a conexão, confiável, ordenado, controle de fluxo e de congestionamento. **UDP:** sem conexão, melhor esforço, sem ordem.
- Nenhum dos dois garante atraso máximo nem vazão mínima.

## 4.2 Multiplexação / demultiplexação 🔥🔥
- **Mux (emissor):** junta dados de vários sockets, anexa porta origem/destino. **Demux (receptor):** usa os cabeçalhos para entregar ao socket correto.
- **UDP** — socket identificado por **(IP destino, porta destino)**. Origens diferentes com mesmo destino → **mesmo socket** (efeito funil). O processo descobre quem enviou pela **origem** devolvida por `recvfrom()`.
- **TCP** — socket identificado pela **quádrupla (IP origem, porta origem, IP destino, porta destino)**. Cada conexão = socket dedicado. Duas conexões do mesmo servidor porta 80 com clientes distintos → sockets distintos, ambos na porta 80.
  - Ex.: (A,9157,B,80), (C,5775,B,80), (C,9157,B,80) → 3 sockets.
  - HTTP não persistente ⇒ novo socket a cada requisição.
- Resposta do servidor inverte: origem ↔ destino. (Se cliente→servidor é x→y, servidor→cliente é y→x.)

## 4.3 UDP (RFC 768) 🔥
- Cabeçalho de **8 bytes**: porta origem (16) | porta destino (16) | comprimento (16) | checksum (16) + dados. (TCP: 20–60 bytes.)
- **Por que existe?** Sem handshake (sem atraso de início), sem estado de conexão no servidor, cabeçalho pequeno, sem controle de congestionamento (a app dita a taxa), controle mais fino de *quando* e *o quê* enviar.
- Usos: DNS, SNMP, streaming/VoIP/jogos, IoT, QUIC/HTTP/3. Confiabilidade, se necessária, é feita **na aplicação**.
- **Checksum da Internet (soma em complemento de 1):**
  1. Trata cabeçalho + pseudo-cabeçalho IP + dados como palavras de 16 bits; soma com **wraparound** (carry-out volta somando no bit menos significativo); **inverte todos os bits**.
  2. Receptor soma tudo **incluindo** o checksum: deve dar `1111 1111 1111 1111`; se houver algum 0 → erro.
  - Exemplo: `1110011001100110 + 1101010101010101 = 1 1011101110111011` → +carry → `1011101110111100` → NOT → **`0100010001000011`**.
  - Só **detecta** (não corrige), e pode falhar com erros compensatórios.

## 4.4 Transferência confiável (rdt) 🔥🔥
Objetivo: serviço confiável (sem perda/erro/duplicata/desordem) sobre canal não confiável. FSMs `evento / ação`. Primitivas: `rdt_send`, `udt_send`, `rdt_rcv`, `deliver_data`.

| Versão | Canal | Problema resolvido | Mecanismo novo |
|---|---|---|---|
| **1.0** | perfeito | — | enviar/receber direto |
| **2.0** | erros de bit | bits trocados | **checksum + ACK/NAK + retransmissão** (ARQ), *stop-and-wait* |
| **2.1** | ACK/NAK corrompido | duplicatas | **nº de sequência (0/1)** |
| **2.2** | idem | eliminar NAK | **ACK com nº de sequência**; ACK duplicado = NAK |
| **3.0** | erros **e perda** | perda de pacote/ACK | **temporizador** (timeout → retransmite) |

- **rdt 3.0 = bit alternante (alternating-bit)**: seq 0/1 + timer. Cenários: sem perda; pacote perdido (timeout → reenvia); ACK perdido (reenvia, receptor descarta duplicata e re-ACK); timeout prematuro (duplicatas ignoradas).
- **Por que seq e timers?** Seq → detectar duplicatas e ordem; timers → detectar perda.
- **Desempenho do stop-and-wait:** `U_sender = (L/R) / (RTT + L/R)`. Ex.: 1 Gbps, RTT 30 ms, L = 8000 b → L/R = 8 µs → U ≈ **0,00027**. Terrível.
- **Pipelining:** N pacotes em voo → `U = N·(L/R) / (RTT + L/R)`. Exige faixa maior de nº de seq e buffers.

### Go-Back-N (GBN) 🔥
- **Janela do emissor** N (autorizados + enviados sem ACK). Variáveis: `base`, `nextseqnum`. **Um único timer** (do pacote mais antigo).
- **ACK cumulativo:** `ACK(n)` = tudo até n recebido em ordem → `base = n+1`.
- **Timeout:** retransmite **todos** os pacotes da janela (`base … nextseqnum−1`).
- **Receptor:** só aceita o pacote `expectedseqnum`; **descarta** fora de ordem e reenvia o ACK do último em ordem. **Sem buffer.** Simples, mas desperdiça banda em links com erros.
- Ex.: pacotes 0–5, o 2 se perde: receptor manda ACK 0, ACK 1, e depois ACK 1 para cada um de 3,4,5 (descartados); timeout → reenvia 2,3,4,5.

### Selective Repeat (SR) 🔥
- **ACK individual** por pacote; **timer por pacote**; **receptor com buffer** (janela própria de recepção) para fora de ordem.
- Emissor: timeout(n) → reenvia **só n**; ao receber ACK(n) marca n; se n == base, desliza até o próximo não confirmado.
- Receptor: pacote em `[rcv_base, rcv_base+N−1]` → ACK(n), bufferiza, entrega em ordem e desliza. Pacote em `[rcv_base−N, rcv_base−1]` → **reenvia ACK(n)** (obrigatório, senão o emissor não avança). Outros: ignora.
- **Dilema da janela:** tamanho da janela ≤ **metade** do espaço de numeração (senão o receptor confunde retransmissão com pacote novo). Ex.: seq 0–3 com N = 3 dá ambiguidade.

| | GBN | SR |
|---|---|---|
| ACK | cumulativo | individual |
| Timer | 1 | 1 por pacote |
| Buffer no receptor | não (descarta) | sim |
| Retransmissão | janela toda | só o perdido |
| Complexidade | baixa | alta |
| Ideal para | pouca perda | links ruidosos |

### Casos-limite (lista de revisão)
- **Em GBN e SR o emissor PODE receber ACK de pacote fora de sua janela** (ACKs duplicados/atrasados de retransmissões).
- **Bit alternante ≡ SR com janelas de tamanho 1 ≡ GBN com janelas de tamanho 1.**

---

# 5. TCP (A5) 🔥🔥

## 5.1 Características
Ponto a ponto (sem multicast/broadcast) · **fluxo de bytes** confiável e ordenado (sem fronteiras de mensagem) · pipelining · **full duplex** · orientado a conexão (estado só nos hosts, não nos roteadores) · **MSS** = máx. dados da aplicação por segmento · tem **controle de fluxo (rwnd)** e **de congestionamento (cwnd)**; janela efetiva = **min(rwnd, cwnd)**.

## 5.2 Segmento TCP
```
| Porta origem (16)        | Porta destino (16)         |
| Número de sequência (32)                              |
| Número de reconhecimento / ACK (32)                   |
| HeadLen | Res | U A P R S F | Janela de recepção rwnd (16) |
| Checksum (16)            | Ponteiro urgente (16)      |
| Opções (0–40 B)                                       |
| Dados                                                 |
```
Cabeçalho mínimo **20 B** (HeadLen em palavras de 32 bits: 5 → 20 B). Flags: **SYN/FIN** (abrir/fechar), **ACK** (campo ACK válido), **RST** (rejeitar/abortar). O **campo rwnd existe no cabeçalho**.

## 5.3 Números de sequência e ACKs 🔥🔥
- **Seq** = nº do **primeiro byte** de dados do segmento (contagem por **bytes**, não por segmento). ISN escolhido aleatoriamente.
- **ACK** = nº do **próximo byte esperado** do outro lado; **cumulativo**.
- Regra de ouro: `ACK = Seq_recebido + nº_bytes_de_dados` **se chegou em ordem**.
- **Piggybacking:** o ACK vai embutido no segmento de dados de volta (Telnet: Seq=42,ACK=79 'C' → servidor Seq=79,ACK=43 'C' eco).
- **ACK do segmento NÃO é necessariamente Seq+len do mesmo segmento**: o campo ACK de A→B refere-se aos dados de B→A.
- **Fora de ordem:** segmento chega antes do esperado → receptor manda **ACK duplicado** do byte que ainda espera. Hoje: buffer + **SACK**.
- **Tamanho de segmento** = diferença entre seq consecutivos (seq 90 → 110 ⇒ 20 bytes).

### Geração de ACK (RFC 1122/2581)
| Evento no receptor | Ação |
|---|---|
| Em ordem, tudo anterior confirmado | **ACK atrasado**: espera até 500 ms pelo próximo |
| Em ordem, outro segmento aguardando ACK | **ACK cumulativo imediato** (um só) |
| Fora de ordem (lacuna) | **ACK duplicado imediato** |
| Preenche lacuna | ACK imediato |
Se o receptor não tem dados para enviar, manda **segmentos só de ACK** (pure ACK).

## 5.4 RTT e Timeout 🔥🔥
```
EstimatedRTT = (1−α)·EstimatedRTT + α·SampleRTT        α = 0,125
DevRTT       = (1−β)·DevRTT + β·|SampleRTT − EstimatedRTT|   β = 0,25
TimeoutInterval = EstimatedRTT + 4·DevRTT
```
- **SampleRTT:** tempo entre enviar e receber o ACK. **Algoritmo de Karn:** ignora SampleRTT de segmentos retransmitidos (ambiguidade).
- Timeout muito curto → retransmissões desnecessárias; muito longo → reação lenta.
- **Backoff exponencial:** em timeout real, o intervalo é **dobrado**.

## 5.5 Transferência confiável no TCP
- Pipelining, **ACKs cumulativos**, **um único timer** (segmento mais antigo não confirmado).
- Remetente: dados da app → cria segmento (`seq = NextSeqNum`), liga o timer; **timeout** → retransmite **só o mais antigo** e reinicia o timer; **ACK y** com `y > SendBase` → `SendBase = y`, reinicia timer se ainda há pendentes.
- Cenários: ACK perdido (retransmite por timeout); timeout prematuro (duplicata); **ACK cumulativo** cobre ACK perdido anterior.
- **Fast Retransmit:** **3 ACKs duplicados** (4 ACKs iguais no total) → reenvia o segmento perdido **antes** do timeout.
  Por que 3? 1–2 dups podem ser só reordenação.

## 5.6 Controle de fluxo 🔥🔥
**Objetivo:** o remetente não estourar o **buffer do receptor** (receptor lento × remetente rápido). Serviço **fim-a-fim**.
```
rwnd = RcvBuffer − [LastByteRcvd − LastByteRead]
Remetente garante:  LastByteSent − LastByteAcked ≤ rwnd
```
- Receptor anuncia `rwnd` em **todo** segmento (campo do cabeçalho). `rwnd` **varia** ao longo da conexão.
- Se `rwnd = 0` o remetente envia **segmentos de 1 byte** (sondagem) para não travar.
- Consequência: bytes não reconhecidos **não excedem** o tamanho do buffer de recepção.

## 5.7 Gerência de conexão
- **Handshake de 2 vias falha:** atrasos/retransmissões → **conexão meio aberta (half-open)** e duplicatas, servidor aloca estado à toa.
- **3-way handshake:**
  1. Cliente → `SYN=1, Seq=x`
  2. Servidor → `SYN=1, ACK=1, Seq=y, ACK=x+1` (SYN-ACK)
  3. Cliente → `ACK=1, Seq=x+1, ACK=y+1` (já pode levar dados)
  Sincroniza ISNs; servidor só aloca estado definitivo (ESTAB) após o 3º passo.
- **Fechamento (4 vias):** cada lado envia `FIN` e recebe `ACK` independentemente. Estados: FIN_WAIT_1/2, CLOSE_WAIT, LAST_ACK, **TIME_WAIT (2·MSL)**, CLOSED. Após FIN o host não envia mais, mas ainda recebe.

---

# 6. Controle de Congestionamento (A6) 🔥🔥

## 6.1 Princípios
**Congestionamento** = "muitas fontes enviando muitos dados rápido demais para a rede suportar". **Diferente de controle de fluxo!** Sintomas: **perda** (buffers estourados) e **longos atrasos** (filas).

| Cenário | Conclusão / custo |
|---|---|
| I — buffers infinitos | vazão máx. `R/2`; atraso → ∞ perto da capacidade |
| II — buffers finitos + retransmissão | **Custo 1:** trabalho extra (retransmissões) para manter a vazão útil. **Custo 2:** retransmissões desnecessárias (timeout prematuro) desperdiçam banda |
| III — 4 fontes, multi-salto | **Custo 3 / colapso:** pacote descartado no meio do caminho desperdiça toda a capacidade dos saltos anteriores; vazão útil → 0 |

- **IP não dá feedback explícito**; o TCP faz **controle fim-a-fim** inferindo congestionamento por **perda** (timeout / 3 dups).

## 6.2 AIMD
- **Aumento Aditivo:** +1 MSS por RTT sem perda (sondagem de banda).
- **Redução Multiplicativa:** corta `cwnd` pela metade na perda.
- Gráfico em **dente de serra**. Taxa ≈ `cwnd / RTT` bytes/s.

## 6.3 Fases do TCP (Reno) 🔥🔥
| Fase | Condição | Crescimento |
|---|---|---|
| **Slow Start (partida lenta)** | `cwnd < ssthresh`; começa com `cwnd = 1 MSS` | **+1 MSS por ACK ⇒ dobra a cada RTT** (1, 2, 4, 8…, exponencial) |
| **Congestion Avoidance (prevenção)** | `cwnd ≥ ssthresh` | **+1 MSS por RTT** (≈ `MSS·MSS/cwnd` por ACK), linear |

**Reação a perdas:**
| Evento | ssthresh | cwnd | Fase seguinte |
|---|---|---|---|
| **Timeout** (congestionamento severo) | `cwnd/2` | **1 MSS** | Slow Start |
| **3 ACKs duplicados** (leve) — Reno | `cwnd/2` | `ssthresh` (*Fast Recovery*; no livro: ssthresh+3) | Congestion Avoidance |
| **Qualquer perda — Tahoe** | `cwnd/2` | 1 MSS | Slow Start |

Pontos-chave:
- `ssthresh` passa a ser **metade do `cwnd` no momento da perda** (não "metade do ssthresh anterior").
- Com 3 dups a rede ainda entrega alguma coisa → Reno não zera a janela. **Fast Retransmit** reenvia o segmento perdido logo.
- A taxa efetiva é limitada por **min(cwnd, rwnd)**.
- Diferença SS × CA: **SS = exponencial (dobra/RTT), CA = linear (+1 MSS/RTT)**; transição quando `cwnd` atinge `ssthresh`.

### Como resolver exercício de sequência de cwnd
Monte uma tabela por RTT: SS: 1→2→4→8…, limitando em `ssthresh` (se passaria, pare em ssthresh); depois +1 por RTT. Na perda aplique a tabela acima.

## 6.4 Vazão do TCP
- Média em regime (AIMD, ignorando SS): **`0,75·W/RTT`** (W = janela no momento da perda; varia entre W/2 e W).
- Em função da perda **L** (Mathis): **`Vazão ≈ 1,22·MSS / (RTT·√L)`**. Como é raiz: perda 4× maior ⇒ vazão **½**.

## 6.5 Justiça
AIMD converge para **partilha igual** entre conexões que dividem um gargalo (zigue-zague até a interseção capacidade total × reta de igualdade). **Burla:** UDP (sem controle) "atropela" TCP; **conexões TCP paralelas** (11 novas contra 9 existentes ⇒ 11/20 da banda).

## 6.6 Além do Reno e QUIC
- **CUBIC** (padrão Linux/Windows): janela em função **cúbica do tempo** desde a última perda, independe do RTT; corta ×0,7 (não 0,5).
- **BBR** (Google): **não usa perda**; modela `BtlBw` (banda do gargalo) e `RTprop` (RTT mínimo), opera no **BDP = BtlBw × RTprop**; evita *bufferbloat*.
- **QUIC** (RFC 9000–9002, HTTP/3 = RFC 9114): roda sobre **UDP** na aplicação; handshake transporte+TLS 1.3 em **1 RTT** (0-RTT em reconexão); **streams independentes** (sem HoL blocking); **migração de conexão** (Connection ID, troca Wi-Fi↔5G).
- Outros: SCTP, DCCP, MPTCP. TCP fingerprinting (TTL inicial, janela, opções).

---

# 7. Mini-comparativos (para revisar na véspera)

### TCP × UDP
| | TCP | UDP |
|---|---|---|
| Conexão | handshake 3 vias | nenhuma |
| Confiabilidade/ordem | sim (ACK, seq, retransmissão) | não |
| Controle de fluxo/congestionamento | sim | não |
| Cabeçalho | 20–60 B | 8 B |
| Demux | quádrupla | (IP dest, porta dest) |
| Usos | Web, e-mail, FTP, SSH | DNS, VoIP, streaming, jogos, QUIC |

### Controle de fluxo × congestionamento
| | **Fluxo** | **Congestionamento** |
|---|---|---|
| Protege | o **receptor** (buffer) | a **rede** (roteadores) |
| Variável | **rwnd** (informada pelo receptor) | **cwnd** (inferida pelo remetente) |
| Sinal | campo `rwnd` no cabeçalho | perda (timeout / 3 dups) |
| Escopo | fim-a-fim remetente↔receptor | remetente↔rede |
| Mecanismo | janela anunciada, sondagem de 1 byte se 0 | SS, CA, Fast Retransmit/Recovery, AIMD |
| Janela efetiva | `min(rwnd, cwnd)` | |

### Não-persistente × Persistente (HTTP)
Não persistente: 1 objeto/conexão, 2·RTT/objeto, slow start a cada objeto. Persistente: mantém conexão (keep-alive); com pipelining, requisições em lote (~1 RTT para todos os objetos), mas com HoL.

### Fórmulas essenciais
```
d_trans = L/R        d_prop = d/s        d_nodal = proc + fila + trans + prop
Tempo HTTP 1 obj (não pers.) = 2·RTT + T_trans
U_stop-and-wait = (L/R)/(RTT + L/R)        U_pipeline = N·(L/R)/(RTT + L/R)
EstRTT' = 0,875·EstRTT + 0,125·Sample
DevRTT' = 0,75·DevRTT + 0,25·|Sample − EstRTT|
Timeout = EstRTT + 4·DevRTT
rwnd = RcvBuffer − dados_no_buffer ;  unacked ≤ min(rwnd, cwnd)
ACK = Seq + len (em ordem) ; len = Seq_seguinte − Seq_atual
D_cs = max(NF/u_s, F/d_min) ; D_p2p = max(F/u_s, F/d_min, NF/(u_s+Σu_i))
Vazão TCP ≈ 0,75 W/RTT ≈ 1,22 MSS/(RTT√L)
```

### Checklist de "pegadinhas" clássicas
- TCP server "precisa de 2 portas": na verdade **2 tipos de sockets** (welcoming + conexão); n clientes ⇒ **n+1 sockets** (todos na mesma porta do servidor, distinguidos pela quádrupla).
- Resposta do servidor: **origem e destino invertidos** (IP e porta).
- ACK ≠ Seq+len do mesmo segmento; é o próximo byte esperado da outra direção.
- Segmento que chega fora de ordem ⇒ ACK **duplicado** do que falta.
- ssthresh = **cwnd/2** na perda; timeout → cwnd = 1; 3 dups (Reno) → cwnd = ssthresh.
- rwnd **muda**; bytes em voo ≤ rwnd ≤ buffer.
- UDP: tudo para a mesma porta cai no **mesmo socket**, mesmo de hosts diferentes.
- HTTP/1.1 = persistente **com pipelining**; HTTP é **stateless** (cookies mantêm o estado).
- DNS: consulta local→raiz→TLD→autoritativo é **iterativa**; host→DNS local é **recursiva**.

---

# 8. Exemplos resolvidos (passo a passo)

> Os gabaritos apontam para estes exemplos. Refaça-os no papel sem olhar.

## 8.1 Seq / ACK — a regra e um exemplo completo
**Regra:** `Seq` = número do 1º byte de dados do segmento. O receptor responde com `ACK = próximo byte que ele espera` (cumulativo).
Se B já tem os bytes até 126, A envia:

| Segmento | Seq | Bytes | Último byte | Próximo seq |
|---|---|---|---|---|
| 1 | 127 | 70 | 196 | **197** |
| 2 | 197 | 50 | 246 | **247** |

- Chegam em ordem: ACK do 1º = **197**, ACK do 2º = **247**.
- Seg 2 chega antes do seg 1: B ainda espera o byte 127 → **ACK = 127** (duplicado).
- Para achar o tamanho: `len = Seq_seguinte − Seq_atual`.
- As **portas se invertem** na volta: A→B (302 → 80); B→A (80 → 302).

## 8.2 Linha do tempo com ACK perdido (tipo "Desenhe o diagrama")
```
A                                   B
|-- Seq=127, 70B ------------------>|  B: tem até 196 → ACK=197
|-- Seq=197, 50B ------------------>|  B: tem até 246 → ACK=247
|      X<------ ACK=197 (perdido) --|
|<----------------- ACK=247 --------|
```
- Se `ACK=247` chega **antes** do timeout do seg 1: como é **cumulativo**, A entende que 127–246 chegaram → **nenhuma retransmissão**.
- Se o timeout do seg 1 vence **antes** de `ACK=247` chegar: A retransmite `Seq=127, 70B`; B já tem esses bytes → descarta a duplicata e reenvia `ACK=247`; A ignora (não é novo, `247 = SendBase`).
- O enunciado "o segundo ACK chega **após** o timeout do primeiro" corresponde ao 2º caso.

## 8.3 EstimatedRTT / DevRTT / Timeout (com números)
α = 0,125, β = 0,25. Estado inicial: `Est = 100 ms`, `Dev = 20 ms`. Chega `Sample = 180 ms`:
```
Dev'  = 0,75·20 + 0,25·|180 − 100| = 15 + 20   = 35 ms   (usa o Est ANTIGO)
Est'  = 0,875·100 + 0,125·180      = 87,5+22,5 = 110 ms
Timeout = 110 + 4·35 = 250 ms
```
Se o Sample = Est, o Dev diminui; se há timeout real, o intervalo é **dobrado** (backoff), até chegar um ACK novo.

## 8.4 Evolução da cwnd (Reno) — tabela por RTT
ssthresh inicial = 8 MSS:

| RTT | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| cwnd | 1 | 2 | 4 | 8 | 9 | 10 | 11 |
| fase | SS | SS | SS | chegou em ssthresh | CA | CA | CA |

**Perda com cwnd = 12:**
- **3 ACKs duplicados (Reno):** `ssthresh = 6`, `cwnd = 6` → 6, 7, 8, … (CA, linear). Tahoe: `cwnd = 1` → 1, 2, 4, 6 (limitado pelo ssthresh), 7, …
- **Timeout:** `ssthresh = 6`, `cwnd = 1` → 1, 2, 4, **6** (no SS não passa do ssthresh), 7, 8, …
Truque: no SS o crescimento é "dobra, mas pare no ssthresh"; depois +1 por RTT.

## 8.5 Controle de fluxo com números
`RcvBuffer = 4000 B`. A aplicação ainda não leu 1000 B → `rwnd = 3000`. Se A já tem 2000 B em voo (enviados, sem ACK), pode mandar mais **1000 B** (`LastByteSent − LastByteAcked ≤ rwnd`). Se a app só lê 50 Mbps e o link entrega 100 Mbps, o buffer enche → rwnd → 0 → A manda sondas de 1 byte e, em regime, sua taxa útil cai para ~50 Mbps.

## 8.6 Tempo de carregamento HTTP — HTML + 10 imagens (RTT dado, T_trans desprezível)
| Modo | Contas | Total |
|---|---|---|
| Não persistente, sequencial | 11 objetos × (1 RTT TCP + 1 RTT req/resp) | **22 RTT** |
| Persistente **sem** pipelining | 1 (TCP) + 1 (HTML) + 10 × 1 (imagens, uma por vez) | **12 RTT** |
| Persistente **com** pipelining | 1 (TCP) + 1 (HTML) + 1 (10 GETs em lote) | **3 RTT** |
Não persistente com *n* conexões paralelas: o 1º objeto custa 2 RTT; os 10 restantes são divididos em grupos de *n*, cada grupo custa 2 RTT.

## 8.7 GBN × SR no mesmo cenário (janela 4, pacotes 0–5, o pacote 2 se perde)
**GBN:** receptor: ACK0, ACK1; recebe 3,4,5 fora de ordem → descarta e manda `ACK1` três vezes. Emissor ignora (não é seletivo) até o **timeout do pacote 2** → reenvia **2,3,4,5** (4 pacotes). Receptor: ACK2…ACK5.
**SR:** receptor: ACK0, ACK1, **ACK3, ACK4, ACK5** (individuais) e **guarda 3,4,5 no buffer**. Timeout do 2 → reenvia **só o 2** (1 pacote). Receptor entrega 2,3,4,5 em ordem e envia ACK2.
Conclusão: com perdas, SR economiza retransmissões; GBN é mais simples.

## 8.8 Janela de SR e espaço de numeração (por que N ≤ metade)
Seq 0–3 (4 números), N = 3. Emissor manda 0,1,2; receptor aceita e passa a esperar `[3,0,1]`. Todos os ACKs se perdem. Timeout → emissor reenvia o **0 antigo**. O receptor vê "0" dentro da janela `[3,0,1]` e o **aceita como pacote novo** → dado duplicado/errado. Com N = 2 (metade de 4) não há ambiguidade.

## 8.9 Eficiência do stop-and-wait e do pipeline
`L = 8000 b`, `R = 1 Gbps` → `L/R = 8 µs`; `RTT = 30 ms`.
`U = 8 µs / (30 ms + 8 µs) ≈ 0,027 %`. Com N = 3000 pacotes em voo, `U ≈ 3000 × 0,027% ≈ 80 %` (linear em N até saturar).

## 8.10 Mux/Demux — qual socket recebe? (exercício típico)
Servidor B porta 80; conexões: (A,9157), (C,5775), (C,9157).
- TCP → 3 sockets, um por **quádrupla** `(IP_o, porta_o, B, 80)`.
- UDP (porta 5529 em C) com pacotes de A:4567 e B:8912 → **1 socket**; o app lê a origem em `recvfrom`.

## 8.11 Troca de papéis no DNS (contagem de mensagens)
Host pergunta ao DNS local (**1**, recursiva). DNS local → raiz (**2**) → resposta com TLD (**3**) → TLD (**4**) → resposta com autoritativo (**5**) → autoritativo (**6**) → resposta com o IP (**7**) → DNS local responde ao host (**8**). Com o nome em cache no DNS local, são só 2 mensagens (1 e 8). Com o TLD em cache, pula-se a raiz.
