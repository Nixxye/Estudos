# Temas importantes da P1 — com a fonte de cada um

Este arquivo cruza **três coisas**: (1) o que se repete nas **provas e listas**; (2) o que os **slides destacam** (caixas "Regra de Ouro", "Conceito‑Chave", "Ponto Chave", "Nota", "Erro Clássico", "Dilema", "A Grande Lição", "Veredito"…); (3) o que o **Wireshark Lab** cobra.
Para cada tema: **explicação** + **de onde veio** (ex.: *P13 Q8 · PO14 Q6 · Slide A5 s.23*).

> Teoria completa: [Resumo_P1_Redes.md](Resumo_P1_Redes.md) · Respostas das provas: [Gabarito_P1_Redes.md](Gabarito_P1_Redes.md) · Fluxo ponta a ponta: [Fluxo_Completo_Rede.md](Fluxo_Completo_Rede.md).
> Números de slide são **aproximados** (±1), tirados da paginação "n/total" dos PDFs.

---

## 0. Legenda das fontes

| Sigla | Arquivo |
|---|---|
| **P13** | Prova 1 — 20/12/2013 (`provas/prova1-2013.pdf`) |
| **PO14** | Prova oral — 25/08/2014 (`provas/provaOral2014.pdf`) |
| **P15** | 2ª avaliação — **1º semestre** de 2015 (`provas/prova2-2015.pdf`) |
| **P15b** | 2ª avaliação — **2º semestre** de 2015 (`provas/prova2-2o2015.docx`) — **prova nova** |
| **LP** (= **P18**) | Lista de questões de provas anteriores (`provas/Lista de questões…pdf`). O arquivo **`provas/provas2018.pdf`** traz **exatamente as mesmas 13 questões** ("Questões de provas passadas"); por isso tudo o que está marcado **LP** vale também como **P18**. Quer dizer que esta lista ainda circulava como material de revisão em **2018**. |
| **PR1** | **Prova recente (fotos)**: P1 corrigida à mão, questões 1–8 (TCP × UDP, P2P, porta, threads, congestionamento, fluxo, rwnd × cwnd, gráfico de `cwnd`). Sem data; as notas e correções nas margens ajudam a inferir o gabarito. |
| **PR2** | **Prova recente (relato + manuscrito)**: temas relatados (SPF/DKIM/DMARC, piggybacking, DNS raiz iterativo, C‑S × P2P, ACK, V/F) + folha manuscrita com as questões 5, 6 e 7 (`P1-redes.pdf`). |
| **LR** | Lista de exercícios (revisão) — rdt (`Lista de exercícios (revisão).pdf`) |
| **TT** | Tarefa: questões TCP (`questoes-TCP.pdf`) |
| **WS** | Wireshark Lab TCP v8.0 |
| **A1…A6** | Slides: A1 Introdução · A2 Aplicação/HTTP · A3 SMTP/DNS/P2P/Sockets · A4 Transporte (UDP, rdt, GBN/SR) · A5 TCP · A6 Congestionamento (+ `aula4-a`, `aula4-d` = versões antigas de transporte/congestionamento) |
| "Q8", "s.23" | número da questão / do slide |

---

## 1. Placar: o que mais cai

Marque ✔ nas fontes onde o tema aparece. **Quanto mais ✔ nas provas, mais certo de cair.**

| # | Tema | P13 | PO14 | P15 | **P15b** | LP = P18 | LR | TT | WS | Slides que destacam |
|---|---|---|---|---|---|---|---|---|---|---|
| T1 | IP + porta identifica processo | Q1 | Q1 | Q3 | | Q10 | | | | A2 s.10 |
| T2 | Cliente × servidor | | | Q2 | | Q9 | | | | A2 s.9 |
| T3 | Apps ↔ protocolos ↔ TCP/UDP | Q3 | Q2 | Q1, Q4 | **Q1** | Q6 | | | | A2 s.16, A4 s.5 |
| T4 | Por que TCP **e** UDP; por que UDP existe | | | Q4 | **Q3** | Q3, Q4, Q8 | | | | A2 s.15, A4 s.5/12–13 |
| T5 | Sockets: UDP 1 × TCP 2 (n+1 sockets, mesma porta); servidor antes | Q5, Q6 | Q3, Q4 | Q5 | | Q5 | | | | A3 s.49, A4 s.9–11 |
| T6 | Demultiplexação (UDP × TCP), portas invertidas | Q7 | | Q5, Q6 | **Q5b** | Q13 | | | | A4 s.8–11 |
| T7 | HTTP (funcionamento, persistente) | Q4 | Q9 | | | Q11 | | | | A2 s.19–30 |
| T8 | DNS | | Q10 | | | Q12 | | | | A3 s.19–29 |
| T9 | rdt: bit alternante, GBN, SR; seq e timers | Q11 | | | **Q2** | Q7 | **todo** | | | A4 s.16–39 |
| T10 | TCP em linhas gerais; handshake | Q2 | Q5 | | | | | | Q4–Q5 | A5 s.3–5, 27–31 |
| T11 | **Cálculo de seq/ACK**, diagrama com ACK perdido | Q9 | | Q8 | **Q5** | | | **Q1, Q4** | Q6–Q8 | A5 s.6–9, 17–21 |
| T12 | **V/F do TCP** (rwnd, SampleRTT, ACK, ssthresh) | Q8 | | Q7 | **Q4** | | | Q3 | | A5 s.4, 10–12, 25; A6 s.12–13 |
| T13 | **Controle de fluxo** | Q10 | Q6 | Q9 | **Q6** | | | Q2, Q5 | Q9 | A5 s.23–26 |
| T14 | **Controle de congestionamento** (SS, CA, perdas) | Q10, Q12 | Q7, Q8 | Q9 | **Q6, Q7** | | | Q5, Q6 | Q13 | A6 s.11–14 |
| T15 | RTT, EstimatedRTT, Timeout | Q8 (V/F) | | Q7d | | | | Q3 | Q7 | A5 s.10–13 |
| T16 | Handshaking: objetivo | Q2 | | | | | | | | A5 s.27–29 |
| T17 | Objetivo do protocolo de **aplicação** e do de **transporte** | | | | | Q1, Q2 | | | | A2 s.12; A4 s.4 |
| T18 | Por que **seq** e **timers** no rdt | Q11 | | | **Q2** | Q7 | **LR** | | | A4 s.20–25 |
| T19 | UDP para o desenvolvedor (por que escolher UDP) | | | Q4 | **Q3** | Q4, Q8 | | | | A4 s.12–13 |
| T20 | **Slow start × rwnd** (slow start controla `cwnd`, não `rwnd`) | | | | **Q4e** | | | | | A6 s.12; A5 s.4 |
| T21 | TCP **ocioso** (reusar `cwnd`/`ssthresh`?) | | | | **Q7** | | | **Q6** | | A6 s.12–13 |

**O que a prova de 2018 acrescenta:** `provas2018.pdf` é a **mesma lista de 13 questões** (a coluna **LP = P18**). Não traz tema novo, mas **confirma que, em 2018, o professor continuava cobrando/recomendando estes temas**: objetivo dos protocolos de aplicação e de transporte, por que TCP e UDP, por que o UDP existe, sockets (1 × 2, n+1), seq e timers no rdt, UDP × TCP para o desenvolvedor, cliente × servidor, IP+porta, HTTP, DNS e o demux UDP. Os mesmos temas se repetem de 2013 a 2018 → **são os de maior retorno de estudo**.

**O que a prova de 2º semestre de 2015 (P15b) acrescenta:** é uma **recombinação de perguntas já conhecidas**, o que mostra o padrão de montagem do professor:
- **Q1, Q2, Q3** vêm quase literalmente da lista (LP Q6, Q7, Q8; aqui com "3 aplicações").
- **Q4 (V/F, 2 pts):** quatro itens idênticos aos da P15 Q7 (ACK sem dados, `rwnd` varia, bytes não reconhecidos ≤ buffer, seq 40 + 4 B ⇒ ACK 44) e **um item novo**: *"o slow start controla o tamanho do `rwnd`"* → **Falso** (controla a `cwnd`). O item do SampleRTT **não** aparece desta vez.
- **Q5:** os **mesmos números** da P15 Q8 (127, 70 e 50 B; ACKs 197 e 247; 127 se invertido) — só mudam as **portas** (3022 → 1234).
- **Q6** = fluxo × congestionamento "incluindo todas as fases" (igual a TT Q5). **Q7** = TCP ocioso (igual a TT Q6).
Ou seja, **todas as perguntas desta prova já estavam nas listas e provas anteriores** — reforça que estudar os temas T3, T4, T9/T18, T11, T12, T13, T14 e T21 cobre praticamente tudo.

### Placar das provas recentes (PR1 e PR2)
| Tema | PR1 (fotos) | PR2 (relato/manuscrito) |
|---|---|---|
| T22 Características TCP × UDP (classificar 0/1) | **Q1** (10 itens) | — |
| T23 TCP × UDP em P2P (V/F) | **Q2** | — |
| T24 Função da porta | **Q3** | — |
| T25 Multithreading em servidores | **Q4** | — |
| T26 SPF / DKIM / DMARC | — | **associação** |
| T27 Piggybacking | — | **V/F** |
| T28 Ler gráfico de `cwnd` | **Q8** (2 pts) | — |
| T29 `rwnd` × `cwnd` (qual limita) | **Q5 (item 4), Q7** | — |
| T30 Cliente‑servidor × P2P (cálculo/argumento) | — | **15 000 "gigas", 1000 clientes** |
| T31 DNS: raiz iterativa | — | **questão escrita** |
| T11 ACK a partir de seq e bytes | — | **questão clássica** (500 B a partir de 1000 → ACK 1500) |
| T12 V/F do TCP (várias) | **Q5, Q6** | **V/F clássicos** |
| T13 Controle de fluxo | **Q6** | (no item do ACK) |
| T14 Controle de congestionamento | **Q5, Q8** | — |

**O que as provas recentes mostram**
1. **Mudança de estilo:** mais **múltipla escolha e V/F** (afirmações para julgar) e **leitura de gráfico**, além das discursivas curtas (DNS, P2P, ACK). Os **conceitos são os mesmos** de 2013–2018.
2. **Cuidado com a redação:** "reduz o limiar pela metade" (PR1 Q5 item 3) é **verdadeiro** quando se refere ao **`cwnd` no momento da perda**; "metade do **seu valor anterior**" (P13 Q8e) é **falso**. **Leia a frase inteira.**
3. **`cwnd` e `rwnd` são independentes** (PR1 Q5 item 4 é **falso**); a janela efetiva é o **mínimo** (PR1 Q7).
4. **`rwnd = 0` ⇒ transmissor para** (PR1 Q6 item 4, **V**), mesmo havendo sondas de 1 byte.
5. **Timeout × 3 ACKs duplicados no gráfico** (PR1 Q8.2a): queda **grande** não é timeout; **timeout = volta a 1** e reinicia o slow start.
6. **O `ssthresh` só muda nas perdas** (PR1 Q8.3); nunca "duplica" em slow start (isso é a `cwnd`).
7. Questões dissertativas recentes: **DNS** (raiz iterativa + cache), **C‑S × P2P** (fórmulas) e **ACK** (+ controle de fluxo) — todas já preparadas (**Parte J** do Gabarito).

**Leitura rápida:** os temas **T11–T14** (seq/ACK, V/F do TCP, fluxo, congestionamento) aparecem em *todas* as provas e na tarefa — são o coração da P1. **T1, T3, T5** (identificação de processo, apps vs transporte, sockets) são a "parte de teoria curta" que se repete quase literalmente.

---

## 2. Os temas, um por um

### T1. O que identifica um processo em outro host? — **IP + porta**
- **Explicação:** o IP (32 bits em IPv4) leva o pacote ao **host**; a porta (16 bits, 0–65535) leva ao **processo/socket** no host. Só o IP não basta porque uma máquina roda vários serviços. Identificador completo: `<IP : porta>`. Portas conhecidas: HTTP 80, HTTPS 443, DNS 53, SSH 22, SMTP 25, IMAP 143, FTP 21, DHCP 67/68.
- **Referências:** **P13 Q1 · PO14 Q1 · P15 Q3 · LP Q10** (a pergunta idêntica em 4 fontes!). **Slide A2 s.10** ("Identificador Completo do Processo").
- **Dica de nota:** cite as duas camadas (rede: IP; transporte: porta) e as faixas de porta (well‑known 0–1023, registradas, dinâmicas).

### T2. Cliente × servidor
- **Explicação:** **cliente** = processo que **inicia** a comunicação; **servidor** = processo que **espera** ser contatado. O papel é **por sessão**, não pela máquina (em P2P o mesmo processo é cliente e servidor).
- **Referências:** **P15 Q2 · LP Q9**. **Slide A2 s.9** (Nota Arquitetural: papéis dinâmicos em P2P).

### T3. Aplicações, protocolos e transporte (TCP ou UDP?)
- **Explicação:** HTTP, FTP, SMTP, POP3, IMAP → **TCP** (não toleram perda, querem ordem; elásticas; portas liberadas em firewall). DNS, VoIP, streaming, jogos → tipicamente **UDP**. Listas de "3 a 5 aplicações não proprietárias": Web–HTTP, e‑mail–SMTP/POP3/IMAP, DNS–DNS, arquivos–FTP, acesso remoto–SSH, P2P–BitTorrent. *Aberto* = especificado por RFC (HTTP, SMTP, DNS); *proprietário* = fechado (Skype original, WhatsApp).
- **Referências:** **P13 Q3 · PO14 Q2** (pergunta idêntica), **P15 Q1** (listar 5 apps), **LP Q6** (listar 3), **P15 Q4** (transação rápida → UDP). **Slide A2 s.16** (tabela de mapeamento) e **s.12–14** (requisitos: perda, temporização, vazão, segurança).
- **Armadilha:** o slide A2 s.13 frisa que a Internet é **best‑effort**: nem TCP nem UDP garantem atraso máximo nem vazão mínima.

### T4. Por que existem TCP e UDP? Por que o UDP existe se há o IP?
- **Explicação:** TCP = confiável/ordenado/controle de fluxo e congestionamento (Web, e‑mail, arquivos). UDP = sem conexão, 8 B de cabeçalho, sem retransmissão/controle de taxa → baixa latência (voz, streaming ao vivo, jogos, DNS). O UDP acrescenta ao IP **multiplexação por portas** e **checksum**; sem isso o IP não sabe a qual processo entregar. **Motivos para escolher UDP:** sem handshake, sem estado no servidor, sem controle de congestionamento, cabeçalho pequeno, controle fino sobre *quando/o que* enviar.
- **Referências:** **LP Q3, Q4, Q8 · P15 Q4**. **Slide A4 s.5** (TCP × UDP), **s.12–13** ("Por que usar o UDP?"), **A2 s.15**.
- **Contexto moderno** (slide, não caiu em prova): QUIC/HTTP‑3 roda sobre UDP (**A4 s.12; A6 s.23–28**).

### T5. Sockets: UDP 1 × TCP 2 (n+1 **sockets**, mesma porta do servidor); servidor precisa subir antes
- **Explicação:**
  - **UDP:** um socket só, identificado por (IP, porta destino); atende qualquer cliente. O cliente pode rodar antes do servidor (o datagrama só se perde).
  - **TCP:** **socket de boas‑vindas** (`listen`) + **um socket de conexão por cliente** (criado pelo `accept`). Com n conexões ⇒ **n+1**. Todos usam a **mesma porta** do servidor; diferenciam‑se pela quádrupla. O servidor precisa estar rodando **antes** para o `connect()` (SYN) ter quem aceite.
- **Referências:** **P13 Q5, Q6 · PO14 Q3, Q4** (idênticas às da P13) **· LP Q5 · P15 Q5**. **Slide A3 s.49** ("Welcome Socket é a porta de entrada da loja; Connection Socket é o vendedor exclusivo"), **A3 s.43–51** (fluxos UDP/TCP e código Python), **A4 s.9–11**.

### T6. Demultiplexação e inversão de portas
- **Explicação:** UDP demux por **(IP destino, porta destino)** — origens diferentes caem no **mesmo socket**, e a aplicação lê a origem com `recvfrom()` (**LP Q13**). TCP demux pela **quádrupla** (IP/porta origem + IP/porta destino) → um socket por conexão, mesmo com porta de servidor igual (**P15 Q5**). Na resposta, **origem e destino se invertem**: A→B (x→y) ⇒ B→A (y→x) (**P13 Q7**; **P15 Q6** com a Fig. 3.5: B→C, 80→7532 e 80→26145; B→A, 80→26145; IPs B→C, B→A).
- **Referências:** **LP Q13 · P15 Q5, Q6 · P13 Q7**. **Slides A4 s.8–11** (UDP × TCP, tabela comparativa, exemplo de 3 sockets na porta 80), **A3 s.49** (identificação pela quádrupla). Os PPT antigos (`aula4-a`) têm os mesmos exemplos com portas 6428/9157/5775.

### T7. HTTP (funcionamento, persistente, pipelining)
- **Explicação:** requisição/resposta sobre TCP (80); texto ASCII; linha de requisição (método, URL, versão) + cabeçalhos + linha em branco + corpo; resposta com linha de status (200, 301, 304, 400, 404, 500, 505). **Stateless** (estado via cookies). Não persistente = **2 RTT + T_trans por objeto**; persistente = reutiliza a conexão; **com pipelining** (default HTTP/1.1) manda GETs em lote; sem pipelining 1 RTT por objeto. HTML + 10 imagens: **22 / 12 / 3 RTT**. Cache web + GET condicional (`If-Modified-Since` → 304).
- **Referências:** **PO14 Q9 · LP Q11 ("Como funciona o protocolo HTTP") · P13 Q4** (persistente com × sem paralelismo; qual o HTTP/1.1 usa). **Slides:** A2 s.19–21 (stateless, "Vantagem Fundamental da Persistência: evita o slow start a cada objeto"), s.22–24 (2·RTT; 22·RTT; pipelining e **HoL**), s.25–26 (formato com `\r\n`), s.30 (status), s.32–34 (cookies), s.35–38 (cache; exemplo 1,2 s; GET condicional), s.39–48 (HTTP/1.0 → 3).
- **Destaque dos slides:** s.24 "Limitação: bloqueio HoL"; s.48 "**Ponto Chave:** o HTTP/2 resolveu o bloqueio na camada de aplicação, mas o HTTP/3 foi necessário para resolver o bloqueio no transporte".

### T8. DNS
- **Explicação:** traduz nome ↔ IP; banco **distribuído e hierárquico** (Raiz → TLD → Autoritativo) + **DNS local** (recursivo, com cache/TTL). Host→local = **recursiva**; local→hierarquia = **iterativa**. Registros A, NS, CNAME, MX, TXT; mensagens sobre **UDP/53** (cabeçalho com ID, flags QR/AA/RD/RA, contadores). Por que não centralizar: SPOF, tráfego, distância, manutenção.
- **Referências:** **PO14 Q10 · LP Q12 ("Explique o funcionamento do DNS")**. **Slides A3 s.19–29** — destaque: s.20 (serviços: aliasing, MX, distribuição de carga + "Por que não centralizar?"), s.21 (árvore), s.24 ("o DNS local é quem trabalha"), s.25–26 (iterativa × recursiva; **raiz/TLD desativam recursão por segurança e carga**), s.27 (**"cache é o herói da performance"**, TTL), s.28 (RR), s.29 (mensagem).

### T9. Transferência confiável (rdt): bit alternante, GBN, SR; seq e timers
- **Explicação:** progressão rdt 1.0 → 2.0 (ACK/NAK + checksum) → 2.1 (nº de seq 0/1 porque ACK/NAK podem se corromper) → 2.2 (sem NAK, ACK com seq) → 3.0 (**timer** p/ perdas = bit alternante). Stop‑and‑wait tem utilização minúscula (`U = (L/R)/(RTT+L/R)` ≈ 0,027 %). **GBN:** janela N, ACK cumulativo, 1 timer, retransmite a janela toda, receptor descarta fora de ordem. **SR:** ACK individual, timer por pacote, buffer no receptor, retransmite só o perdido; janela ≤ metade do espaço de numeração. Com janela 1, bit alternante = GBN = SR; em GBN e SR o remetente **pode** receber ACK fora da janela.
- **Referências:** **LR (toda: Q1 pesquisa + Q2 a–d V/F) · P13 Q11 · LP Q7** (por que seq e timers). **Slides A4 s.16–39**; destaques: **s.20 "O Problema Oculto do RDT 2.0: e se o ACK/NAK também for corrompido?"**; **s.28 desempenho do 3.0**; **s.31–33 GBN**; **s.34–36 SR**; **s.37 "Dilema da Janela"**; **s.38 comparativo GBN × SR**; **s.39 resumo da evolução**.

### T10. TCP em linhas gerais, handshake e fechamento
- **Explicação:** orientado a conexão, ponto a ponto, fluxo de bytes confiável e ordenado, full duplex, pipelining; handshake de 3 vias (SYN, SYN+ACK, ACK) — evita conexão meio‑aberta; fechamento com FIN/ACK em cada sentido (TIME_WAIT 2·MSL). "Handshaking protocol": combinar/inicializar estado antes de enviar dados.
- **Referências:** **PO14 Q5 ("Explique em linhas gerais o funcionamento do TCP") · P13 Q2 (objetivo do handshaking) · WS Q4–Q5** (SYN e SYN‑ACK no trace). **Slides A5 s.3–5** (características; "Janela efetiva = min(rwnd, cwnd)"), **s.27–29** ("Falha das 2 vias: a alocação prematura de estado"), **s.30–31** (fechamento), **s.32** (resumo).

### T11. ⭐ Números de sequência e ACK — as contas
- **Explicação:** `Seq` = nº do **primeiro byte** do segmento; `ACK` = **próximo byte esperado** (cumulativo); em ordem: `ACK = Seq + len`; `len = Seq_seguinte − Seq_atual`; 2º segmento fora de ordem ⇒ **ACK duplicado** do byte que falta; portas invertidas na volta; ACK perdido coberto por ACK cumulativo posterior.
  Resultados que você deve saber de cabeça:
  | Questão | Resultado |
  |---|---|
  | P13 Q9 (seq 90 e 110) | 1º segmento = **20 B**; ACK com 1º perdido = **90** |
  | P15 Q8 (127, 70 e 50 B) | seq₂ = **197**; ACK₁ = **197**; 2º antes do 1º ⇒ **127**; ACK₂ = 247 |
  | TT Q1 (127, 80 e 40 B) | seq₂ = **207**; ACK₁ = 207; 2º antes ⇒ **127**; ACK₂ = 247 |
  | TT Q4 (1400, 1900, 2000) | **500 B**, **100 B**, ACKs **1900, 2000, 2000+L** |
  | Diagrama (P15 Q8d, TT Q1d) | seg1, seg2, ACK₁ perdido, timeout, retransmissão do seg1, ACK₂ cumulativo, ACK duplicado |
- **Referências:** **P13 Q9 · P15 Q8 · TT Q1, Q4 · WS Q6–Q8**. **Slides A5 s.6** (nº de seq e ACKs; "ISN aleatório"), **s.7** (exemplo com perda), **s.9** (Telnet/piggybacking), **s.17–19** (ACK perdido, timeout prematuro, **vantagem do ACK cumulativo**), **s.20** (regras de geração de ACK).

### T12. ⭐ Verdadeiro/Falso do TCP (as 5 afirmações recorrentes)
As mesmas cinco aparecem em **P13 Q8**, **TT Q3** e (com pequena variação) **P15 Q7**:

| Afirmação | Gabarito | Por quê (curto) | Fontes |
|---|---|---|---|
| Bytes não reconhecidos ≤ buffer de recepção | **V** | `LastByteSent − LastByteAcked ≤ rwnd ≤ RcvBuffer` | P13 Q8a · TT Q3a · P15 Q7c · **P15b Q4c** · A5 s.25 |
| Segmento TCP tem campo para RcvWindow | **V** | `rwnd`, 16 bits, no cabeçalho | P13 Q8b · TT Q3b · A5 s.5 |
| Último SampleRTT = 1 s ⇒ Timeout ≥ 1 s | **V** (⚠️ prova no Gabarito, P13 Q8c) | `Timeout = E' + 3D + |1−E| ≥ 1` | P13 Q8c · TT Q3c · P15 Q7d · A5 s.10–12 |
| Seq 38 + 4 B ⇒ ACK do mesmo segmento = 42 | **F** | ACK refere‑se à outra direção; 42 é o ACK de B ao receber | P13 Q8d · TT Q3d · P15 Q7e · **P15b Q4d** · A5 s.6 |
| Timeout ⇒ threshold = metade do **valor anterior** | **F** | `ssthresh = cwnd/2` (cwnd no momento da perda), `cwnd = 1` | P13 Q8e · TT Q3e · A6 s.13 |
| (só P15 Q7a) B sem dados não manda ACK | **F** | manda ACK só‑de‑ACK | P15 Q7a · **P15b Q4a** · A5 s.20 |
| (só P15 Q7b) rwnd nunca muda | **F** | `rwnd = RcvBuffer − dados no buffer` | P15 Q7b · **P15b Q4b** · A5 s.25 |

### T13. ⭐ Controle de fluxo
- **Explicação:** protege o **receptor** (buffer). Receptor calcula `rwnd = RcvBuffer − (LastByteRcvd − LastByteRead)` e o põe no cabeçalho de **todo** segmento; remetente mantém bytes em voo ≤ rwnd; `rwnd = 0` ⇒ sondas de 1 byte. Serviço **fim‑a‑fim**.
- **Caso numérico (TT Q2):** enlace 100 Mbps, app em A escreve a 120 Mbps, app em B lê a 50 Mbps → o buffer de B enche, `rwnd` → 0, A é freada para ≈ **50 Mbps**.
- **Referências:** **PO14 Q6 · P13 Q10 · P15 Q9 (2 pts) · TT Q2, Q5 · WS Q9** (menor rwnd = 5840 B; nunca freia o remetente). **Slides A5 s.23–26**; destaque: s.26 "**Freio**: se o buffer lotar, rwnd = 0; o remetente suspende o envio e manda apenas pacotes de sondagem (1 byte)". Também **A5 s.4**: "Controle de Fluxo (Protege o Receptor)" × "Controle de Congestionamento (Protege a Rede)".

### T14. ⭐ Controle de congestionamento (SS, CA, reações a perda)
- **Explicação:** AIMD (+1 MSS/RTT; ÷2 na perda); `cwnd` e `ssthresh`; **Slow Start** (`cwnd=1`, +1 por ACK ⇒ dobra por RTT, exponencial) → **Congestion Avoidance** (+1 MSS/RTT, linear) quando `cwnd ≥ ssthresh`; **3 dups** ⇒ `ssthresh=cwnd/2`, `cwnd=ssthresh` (Reno, fast recovery); **timeout** ⇒ `ssthresh=cwnd/2`, `cwnd=1`, volta ao SS; Tahoe zera em qualquer perda. Janela efetiva = `min(cwnd, rwnd)`. Fluxo × congestionamento: quem protege o quê, quem calcula, como sabe.
- **TT Q6 (ocioso entre t1 e t2):** reutilizar `cwnd`/`ssthresh` → vantagem: retoma rápido; desvantagem: rede pode ter mudado, rajada causa perdas; alternativa: manter `ssthresh` e reiniciar `cwnd` pequeno (slow start).
- **Referências:** **PO14 Q7, Q8 · P13 Q10, Q12 · P15 Q9 · TT Q5, Q6 · WS Q13** (Stevens: SS e CA no gráfico). **Slides A6 s.11–14** (AIMD s.11, **Partida Lenta s.12** — "o paradoxo do nome: crescimento exponencial", **Reação a perdas s.13**, **Tahoe × Reno s.14**); s.2–10 princípios e os **3 custos** do congestionamento; s.15–16 vazão (0,75 W/RTT; **Mathis 1,22·MSS/(RTT√L): "a raiz quadrada é fatal"**); s.17–18 justiça e burla (UDP, conexões paralelas); s.19–21 CUBIC/BBR; s.23–28 QUIC.

### T15. RTT, EstimatedRTT, TimeoutInterval
- **Explicação:** `EstimatedRTT = 0,875·Est + 0,125·Sample`; `DevRTT = 0,75·Dev + 0,25·|Sample−Est|`; `Timeout = Est + 4·Dev`; **Karn** ignora amostras de retransmissões; **backoff exponencial** dobra o timeout em timeout real. Fast retransmit com **3 dups** ("pequenas reordenações geram 1–2 dups").
- **Referências:** **P13 Q8c · TT Q3c · P15 Q7d · WS Q7** (calcular EstimatedRTT dos 6 primeiros segmentos). **Slides A5 s.10–13** (destaque: s.10 "Algoritmo de Karn", s.12 "Recuo Exponencial"), **s.21** (por que 3 ACKs?).

### T16. Handshaking e "por que 3 vias"
- Ver T10. **P13 Q2 · A5 s.27–29**.

### T20. "O slow start controla o tamanho do `rwnd`" (V/F novo da P15b)
- **Explicação:** **Falso.** O slow start é uma fase do **controle de congestionamento** e controla a **`cwnd`** (janela de congestionamento, calculada pelo **remetente**). O **`rwnd`** é do **controle de fluxo**, calculado pelo **receptor** (`RcvBuffer − dados no buffer`) e anunciado no cabeçalho. Eles se combinam em `min(cwnd, rwnd)`, mas são independentes: o slow start nunca altera o `rwnd`.
- **Referências:** **P15b Q4 (item e)**. **Slides A5 s.4** ("Controle de Fluxo (protege o receptor) × Controle de Congestionamento (protege a rede)"), **A6 s.12** (slow start dobra a `cwnd`).

### T21. TCP ocioso entre t1 e t2: reutilizar `cwnd` e `ssthresh`?
- **Explicação:** **Vantagem:** se a rede não mudou, a conexão retoma a taxa alta imediatamente. **Desvantagem:** depois de um longo silêncio a rede pode ter mudado e os ACKs que "cronometram" o envio pararam; enviar de uma vez uma janela grande gera uma **rajada** que pode causar congestionamento e perdas. **Alternativa:** manter o `ssthresh` (memória da capacidade) e **reiniciar `cwnd` pequeno** (1 MSS ou janela inicial), fazendo slow start até o `ssthresh` e depois congestion avoidance.
- **Referências:** **P15b Q7 · TT Q6**. Slides **A6 s.12–13**.

---

### T22. Características de **TCP × UDP** (classificar itens em 0/1)
- **Explicação:** a prova recente traz **10 afirmações em pares** (handshake, confiabilidade, controle de fluxo/congestionamento, stream × datagrama, integridade × latência). **TCP:** 3 vias, seq/ACK, `rwnd` e `cwnd`, **fluxo de bytes** (sem fronteiras), e‑mail/HTTP/FTP. **UDP:** sem conexão, best‑effort, **aplicação cuida de tudo**, **preserva fronteiras** (1 `sendto` = 1 datagrama), DNS/streaming/jogos.
- **Referências:** **PR1 Q1**. Slides **A2 s.15–16**, **A4 s.5, s.12–13**, **A5 s.3**, **A3 s.50** (TCP não preserva fronteiras). Gabarito **Parte I, Q1**.

### T23. **TCP × UDP em P2P** (V/F)
- **Explicação:** **BitTorrent** → **TCP** (integridade dos blocos sem reimplementar retransmissão). **Tempo real** → **UDP** (latência > entrega total). **TCP em P2P** tem overhead de conexão/congestionamento e **atrapalha a travessia de NAT**. **UDP não tem controle de fluxo integrado** (isso é do TCP).
- **Referências:** **PR1 Q2**. Slides **A3 s.8, s.37** (conexões TCP entre peers; desafio NAT). Gabarito **Parte I, Q2**.

### T24. **Função da porta**
- **Explicação:** identificar o **processo/socket** de destino no host (o IP identifica o host). Base da multiplexação/demultiplexação.
- **Referências:** **PR1 Q3** (+ T1). Slides **A2 s.10**, **A4 s.6**. Gabarito **Parte I, Q3**.

### T25. **Multithreading em servidores** (TCP e UDP)
- **Explicação:** TCP: thread principal em `accept()` + **uma thread por conexão**. UDP: um socket, threads processam datagramas em paralelo (fila). O objetivo é **responsividade e paralelismo**, **não** garantir ordem (isso é do TCP no kernel).
- **Referências:** **PR1 Q4**. Slides **A3 s.49–51** (welcoming × connection socket), **A4 s.11** (servidores concorrentes). Gabarito **Parte I, Q4**.

### T26. **SPF, DKIM e DMARC**
- **Explicação:** **SPF** = lista de IPs/servidores autorizados (TXT no DNS); **DKIM** = assinatura digital, chave pública no DNS (integridade); **DMARC** = política (none/quarantine/reject) com base em SPF+DKIM. Mnemônico: **S**ervidores · **D**igital · **D**ecisão.
- **Referências:** **PR2 (associação SPF/DKIM/DMARC)**. Slides **A3 s.17–18**. Gabarito **Parte J, J1**.

### T27. **Piggybacking**
- **Explicação:** ACK **de carona** num segmento de dados do sentido contrário. **Não é obrigatório**: sem dados, o TCP manda **ACK puro**. Não existe no UDP. Pode se beneficiar do **ACK atrasado** (até 500 ms).
- **Referências:** **PR2 (V/F)**, **P15 Q7a, P15b Q4a** (ACK sem dados). Slides **A5 s.9** (Telnet), **s.20**. Gabarito **Parte J, J2**.

### T28. **Ler o gráfico de `cwnd`** (Reno)
- **Explicação:** subida **exponencial** = slow start; **linear** = CA; **queda a 1** = **timeout**; **queda à metade** (sem voltar a 1) = **3 ACKs duplicados**; `ssthresh = cwnd/2` da `cwnd` **antes** da queda e **só muda nas perdas**; slow start termina quando `cwnd` atinge `ssthresh`. Na PR1: SS 1–6 e 23–26; CA 6–16 e 17–22; perda na 16 = 3 dups; `ssthresh` na 18 = 21; perda na 22 = timeout; fim da 26 com 3 dups ⇒ `ssthresh = 4`, `cwnd = 4`.
- **Referências:** **PR1 Q8** (2 pts; erros mais comuns: confundir queda grande com timeout; achar que `ssthresh` cresce; **dobrar** em vez de dividir). Slides **A6 s.11–14**. Gabarito **Parte I, Q8**; Transporte_do_Zero **§9.2.16**.

### T29. **`rwnd` × `cwnd`: qual limita e para quê**
- **Explicação:** janela efetiva = **`min(cwnd, rwnd)`**; o **menor** limita. `cwnd` → evita **congestionar a rede**; `rwnd` → evita **estourar o buffer do receptor**. A `cwnd` **não** é limitada pela `rwnd` (são independentes). Ex.: rwnd = 32, cwnd = 22 ⇒ **22**, limitado pela **`cwnd`** (congestionamento).
- **Referências:** **PR1 Q5 (item 4: F), Q7**. Slides **A5 s.4**. Gabarito **Parte I, Q5/Q7**.

### T30. **Cliente‑servidor × P2P (por que um colapsa e o outro escala)**
- **Explicação:** `D_cs = max{N·F/u_s, F/d_min}` cresce **linearmente com N**; `D_p2p = max{F/u_s, F/d_min, N·F/(u_s+Σuᵢ)}` **estabiliza** (cada peer traz oferta). Exemplo: F = 15 Gb, N = 1000: **138,8 h × 12,6 h**; F = 15 GB: **1111 h × 101 h** (atenção a GB × Gb).
- **Referências:** **PR2 (15 000 "gigas" para 1000 clientes)**. Slides **A3 s.32–35** ("Veredito da Escalabilidade"). Gabarito **Parte J, J4**.

### T31. **DNS: iterativo na raiz**
- **Explicação:** a raiz **não resolve** (recursão desativada); **devolve referência** ao TLD; o **DNS local** faz as consultas seguintes (TLD → autoritativo) e usa **cache/TTL**. Motivo: carga mundial e DDoS.
- **Referências:** **PR2 (escrita)**; reforça **PO14 Q10 · LP Q12**. Slides **A3 s.22, s.25–27**. Gabarito **Parte J, J3**; DNS_a_Fundo §7.

---

## 3. Destaques dos slides (caixas e frases que o professor sublinha)

Cada item abaixo é uma caixa ou frase de destaque dos slides. Para cada um você encontra: **o que o slide diz**, **explicação passo a passo** (com exemplo, quando ajuda) e **por que importa / onde cai**. Os itens estão na ordem dos slides. Marcador **[T#]** = ligação com o tema da seção 2.

---

### A1 — Introdução

**s.5–6 · Comutação de circuitos × comutação de pacotes**
- *O que diz:* circuitos não escalam bem para o tráfego da Internet, que vem em rajadas com longos silêncios; pacotes usam multiplexação estatística.
- *Explicação:* na comutação de **circuitos** (telefone antigo), antes de falar a rede **reserva** uma fatia do enlace só para você (por frequência — FDM — ou por tempo — TDM). Se você fica calado, a fatia fica **ociosa** e ninguém mais a usa. Na comutação de **pacotes**, não há reserva: os dados são cortados em pacotes que usam o enlace **quando precisam**, e o enlace é compartilhado "por demanda" (multiplexação estatística). Como a maioria dos usuários só transmite de vez em quando, muitos cabem no mesmo enlace.
- *Exemplo do slide:* enlace de 1 Mbps; cada usuário usa 100 kbps, mas só está ativo 10% do tempo. Circuitos: reserva 100 kbps para cada → só **10 usuários** (1 Mbps ÷ 100 kbps). Pacotes: cabem **35 usuários** e a chance de mais de 10 estarem ativos juntos é ≈ 0,0004 (quase nunca há perda).
- *Custo dos pacotes:* se muitos transmitem ao mesmo tempo, forma‑se **fila** e, com buffer cheio, ocorre **perda**.
- *Por que importa:* é a base de por que a Internet tem filas, atrasos e perdas — o que mais tarde justifica o controle de congestionamento do TCP.

**s.10 · "Conceito‑Chave": meio dedicado × compartilhado**
- *O que diz:* nas redes de acesso, o meio pode ser **dedicado** (só seu) ou **compartilhado** (dividido com vizinhos).
- *Explicação:* **DSL** (par de cobre até a central) e **FTTH** (fibra) são dedicados: a capacidade do seu último trecho não depende do que o vizinho faz. **Cabo (HFC)**, **Wi‑Fi** e **celular** são compartilhados: vários nós disputam o mesmo canal, então a taxa que você obtém **varia** com o número de usuários ativos.
- *Por que importa:* explica por que a velocidade contratada "varia" e conecta com o conceito de gargalo (s.34).

**s.13 · Definição de protocolo**
- *O que diz:* um protocolo define o **formato** e a **ordem** das mensagens trocadas **e as ações** tomadas ao enviar/receber.
- *Explicação:* pense na conversa humana: formato = idioma e estrutura da frase ("Bom dia!"); ordem = quem fala primeiro e a resposta esperada; ação = o que você faz ao ouvir ("Que horas são?" → olhar o relógio e responder). Em rede: o TCP define o formato do segmento, a ordem SYN → SYN+ACK → ACK e a ação "ao receber SYN, responder com SYN+ACK".
- *Por que importa:* toda pergunta do tipo "o que é/qual o objetivo de um protocolo X" (LP Q1, P13 Q2) se responde com esses três elementos.

**s.16 · Por que organizar em camadas**
- *O que diz:* camadas dão **estrutura explícita** e **modularidade/encapsulamento**.
- *Explicação:* o sistema é complexo demais para um bloco único. Dividindo em camadas, cada uma oferece um **serviço** à de cima e usa o serviço da de baixo, sem precisar saber como ele é feito por dentro. Assim, trocar o meio físico (cobre → fibra) **não altera** o HTTP nem o TCP. Analogia do slide: mudar o procedimento de embarque no portão não muda a rota do voo.
- *Por que importa:* sustenta toda a lógica da disciplina (cada camada tem seu cabeçalho, seu endereço e sua responsabilidade).

**s.19–20 · Camadas 5 e 6 do OSI "foram para a aplicação"**
- *O que diz:* na pilha TCP/IP (5 camadas) os serviços de **Sessão** e **Apresentação** existem, mas ficam no **código da aplicação**.
- *Explicação:* Apresentação = como o dado é representado (UTF‑8, JSON, compressão, criptografia/TLS). Sessão = diálogo e estado (cookies, JWT, retomar de onde parou). Hoje isso é feito por bibliotecas dentro do programa, não por protocolos fixos do sistema operacional. *Trade‑off:* menos overhead e mais liberdade, mas mais responsabilidade para o programador.
- *Ligação:* o `.encode()/.decode()` do código Python de sockets (A3 s.44) é a "camada de apresentação" feita na aplicação.

**s.21 · "Regra prática": nunca transmita memória bruta**
- *O que diz:* os dados na rede devem ser **canônicos**, independentes de CPU, compilador e alinhamento.
- *Explicação:* dois problemas. (1) **Endianness**: x86 guarda `0x1A2B3C4D` com o byte menos significativo primeiro (little‑endian); a rede usa big‑endian (*network byte order*). Se você mandar o inteiro "cru", o outro lado lê `0x4D3C2B1A`. Solução: `htons()/htonl()` ao enviar e `ntohs()/ntohl()` ao receber. (2) **Padding**: compiladores inserem bytes de enchimento em `struct`s de formas diferentes, então os deslocamentos divergem entre máquinas. Solução: serializar campo a campo (JSON, Protobuf…).

**s.22 · Encapsulamento**
- *O que diz:* cada camada trata o que vem de cima como dados puros e acrescenta seu cabeçalho.
- *Explicação (de cima para baixo):* Mensagem (aplicação) → + cabeçalho de transporte `Ht` (portas, seq) = **Segmento** → + cabeçalho de rede `Hn` (IPs) = **Datagrama** → + cabeçalho e rodapé de enlace `Hl … Tl` (MACs, CRC) = **Quadro** → vira **bits**. O receptor faz o caminho inverso (desencapsulamento), cada camada removendo o seu cabeçalho.
- *Exemplo:* um `GET /index.html` vira `Eth | IP | TCP | HTTP | FCS`.
- *Por que importa:* os nomes das PDUs (mensagem/segmento/datagrama/quadro) e o que há em cada cabeçalho aparecem em perguntas conceituais.

**s.32–33 · Os 4 atrasos e o "Erro Clássico"**
- *O que diz:* `d_nodal = d_proc + d_fila + d_trans + d_prop`; **não confunda transmissão com propagação**.
- *Explicação de cada atraso:*
  - **d_proc** (processamento): checar erros de bit e consultar a tabela de roteamento — microssegundos.
  - **d_fila** (enfileiramento): esperar sua vez de ser transmitido; varia e cresce com o congestionamento.
  - **d_trans = L/R**: tempo para **empurrar todos os bits** do pacote no enlace. Depende do **tamanho L** e da **taxa R**; **não depende da distância**.
  - **d_prop = d/s**: tempo para **um bit viajar** pelo meio (s ≈ 2×10⁸ m/s na fibra). Depende da **distância**; **não depende do tamanho** do pacote.
- *Exemplo do slide:* L = 1000 bits, R = 1 Mbps → d_trans = 1 ms. Enlace de 100 km na fibra → d_prop = 100 000 / 2×10⁸ = 0,5 ms. O primeiro bit chega ao destino **antes** de o último bit sair da origem ("o trem ainda está saindo da estação").
- *Por que importa:* é o erro mais comum em cálculo de atraso. Também aparece indiretamente no cálculo de utilização do stop‑and‑wait (A4 s.28): `L/R` é o tempo de transmissão.

**s.34 · Vazão = gargalo**
- *O que diz:* vazão fim‑a‑fim = **min** das taxas dos enlaces do caminho.
- *Explicação:* é como um cano: o trecho mais estreito limita o fluxo todo. Se a fonte tem 1 Gbps, o meio do caminho 100 Mbps e o seu acesso 20 Mbps, você recebe **20 Mbps**. Com 10 conexões dividindo um enlace de 10 Mbps, cada uma fica com ≈ 1 Mbps.
- *Ligação:* é o mesmo raciocínio do controle de congestionamento (A6) e do exercício do enlace de 100 Mbps com leitor de 50 Mbps (TT Q2).

**s.36 · Traceroute**
- *O que diz:* cada linha = um roteador do caminho; `* * *` = ele não respondeu.
- *Explicação:* o `traceroute` envia sondas e mede o tempo de ida e volta até cada roteador do caminho (3 sondas por salto → 3 tempos por linha). `* * *` significa que aquele roteador não respondeu (filtro ou perda), mas o pacote **seguiu** mesmo assim. Serve para ver rota e onde o atraso cresce.

**s.39 · A Internet sob ataque**
- *O que diz:* malware/botnets, DoS/DDoS, packet sniffing, IP spoofing.
- *Explicação:* **botnet** = máquinas infectadas controladas por um atacante; **DDoS** = muitas origens inundam o alvo até esgotar seus recursos; **sniffing** = capturar pacotes que passam (é o que o Wireshark faz; perigoso em Wi‑Fi aberto); **spoofing** = forjar o IP de origem. *Consequência:* o HTTP em texto claro é legível por um sniffer; o HTTPS (TLS) protege.

---

### A2 — Aplicação e HTTP

**s.5 · Princípio fim‑a‑fim: núcleo simples, borda inteligente [T3]**
- *Explicação:* os programas de rede rodam **só nos hosts** (borda). Os roteadores do meio não entendem HTTP nem e‑mail: apenas encaminham pacotes (camadas 1–3). Vantagem: para criar um serviço novo (HTTP, BitTorrent, WebRTC) basta instalar software nas pontas; não é preciso mexer na rede inteira.

**s.9 · Nota arquitetural: papéis dinâmicos [T2]**
- *Explicação:* "cliente" e "servidor" são papéis **por sessão**, não tipos de máquina. No BitTorrent o mesmo processo é **cliente** ao baixar um bloco de um par e **servidor** ao enviar outro bloco a um par diferente. Em Web/e‑mail os papéis são fixos na prática (servidor sempre ligado, IP fixo).

**s.10 · Identificador do processo = IP : porta [T1]**
- *Explicação:* a rede usa **duas chaves em dois níveis**. O **IP** (camada de rede) aponta o computador. A **porta** (camada de transporte, 16 bits) aponta o programa dentro dele. Analogia: IP = endereço do prédio; porta = número do apartamento. A tabela do slide traz as portas conhecidas (HTTP 80, HTTPS 443, DNS 53, SSH 22, SMTP 25, IMAP 143, FTP 21, DHCP 67/68).

**s.12 · Aplicação ≠ protocolo; aberto × proprietário [T3]**
- *Explicação:* "A Web é a aplicação distribuída; o HTTP é o protocolo aberto que a viabiliza". Protocolo **aberto** = especificado em RFC pela IETF (HTTP, SMTP, DNS), qualquer fabricante implementa e interopera. **Proprietário** = especificação fechada de uma empresa (Skype original, WhatsApp), sem garantia de interoperar com terceiros. Um protocolo de aplicação define tipos de mensagem, sintaxe, semântica e regras de diálogo.

**s.13–14 · Requisitos da aplicação para o transporte [T3/T4]**
- *Explicação:* quatro dimensões.
  1. **Perda:** transferência de arquivos, e‑mail e Web **não toleram** perda; áudio/vídeo ao vivo **toleram** pequenas perdas.
  2. **Temporização (atraso/jitter):** jogos e telefonia IP precisam de baixo atraso; e‑mail e download não.
  3. **Vazão:** *sensível* (precisa de taxa mínima, ex.: vídeo HD) × *elástica* (usa o que tiver, ex.: arquivo, e‑mail).
  4. **Segurança:** confidencialidade, integridade, autenticação (TLS).
- *Aviso do slide:* a Internet é **best‑effort** — nem TCP nem UDP garantem atraso máximo nem vazão mínima.
- *Por que importa:* é o argumento para escolher TCP ou UDP (P15 Q4, LP Q8).

**s.16 · Mapeamento aplicação → protocolo → transporte [T3]**
- *Explicação:* e‑mail (SMTP), acesso remoto (SSH/Telnet) e Web (HTTP) usam **TCP**; DNS usa **UDP**; streaming usa TCP (DASH/HLS) ou UDP (RTP); VoIP usa **UDP** (ou TCP). *Por que TCP:* integridade estrita e portas 80/443 liberadas em firewalls. *Por que UDP/QUIC:* sem atraso de retransmissão (voz/vídeo ao vivo) e sem o custo de vários RTTs de handshake.

**s.20–21 · HTTP stateless; "Vantagem Fundamental da Persistência" [T7]**
- *Stateless:* o servidor processa cada requisição **isoladamente**, sem lembrar das anteriores. Vantagens: **escalabilidade** (não guarda contexto de milhões de clientes) e **tolerância a falhas** (se reiniciar, não há nada para reconstruir).
- *Persistência:* mantém a conexão TCP aberta para vários objetos. A "vantagem fundamental" é **evitar o handshake e o slow start a cada objeto** — a conexão já está "aquecida" (janela de congestionamento já crescida).

**s.22 · Modelo de tempo: `2·RTT + T_trans` [T7]**
- *Explicação:* para buscar **um** objeto sem conexão aberta: **1 RTT** para o handshake TCP (SYN → SYN+ACK) + **1 RTT** para a requisição e a chegada do primeiro byte da resposta + o tempo de transmissão do objeto (`L/R`).

**s.23 · HTTP não persistente: 22 RTT para 11 objetos [T7]**
- *Explicação:* HTML + 10 imagens = 11 objetos; cada um custa 2 RTT (nova conexão a cada vez, em sequência) → **22 RTT + 11·T_trans**. Além disso: 11 conexões criadas e destruídas (consome estado no SO) e o slow start recomeça em cada uma (a rede nunca chega à capacidade máxima). Mitigação: abrir 5–8 conexões em paralelo (reduz o tempo percebido, mas aumenta a carga).

**s.24 · Persistente com pipelining e o bloqueio HoL [T7]**
- *Explicação:* o cliente envia **vários GET em lote**, sem esperar cada resposta; só 1 RTT para todas as imagens (total ≈ 3 RTT, contra 12 sem pipelining). **Limitação (HoL — Head‑of‑Line):** as respostas devem voltar **na mesma ordem** dos pedidos (FIFO). Se a resposta nº 1 for lenta, as seguintes ficam travadas atrás dela — como uma fila de supermercado com um cliente demorado na frente.

**s.25–26 · Formato da mensagem de requisição [T7]**
- *Explicação:* `método sp URL sp versão cr lf` (linha de requisição) → linhas `nome: valor cr lf` (cabeçalhos) → **linha em branco** (`cr lf` sozinho) que avisa "acabaram os cabeçalhos" → corpo (vazio no GET; no POST leva os dados). `sp` = espaço obrigatório; `cr lf` = fim de linha. Por isso, no telnet, é preciso apertar Enter **duas vezes**.

**s.27 · Aviso de privacidade: GET × POST [T7]**
- *Explicação:* no **GET** os parâmetros vão na URL (`/busca?termo=redes`), ficam visíveis na barra de endereços, no histórico e nos logs de roteadores/servidores — **nunca use para senha**. No **POST** os dados vão no **corpo** da mensagem; a URL fica limpa.

**s.31 · Nota: telnet funciona na porta 80, não na 443**
- *Explicação:* como o HTTP é texto, dá para "ser o navegador" digitando `telnet host 80` e a requisição à mão. Em HTTPS (porta 443) isso falha, porque o servidor espera antes o handshake de criptografia TLS, que o telnet não faz.

**s.32–34 · Cookies [T7]**
- *Explicação:* o HTTP é stateless, então o estado é mantido **fora do protocolo**. Quatro componentes: (1) cabeçalho `Set-Cookie: 1678` na resposta; (2) o navegador guarda o ID em disco; (3) nas visitas seguintes envia `Cookie: 1678`; (4) o servidor consulta seu banco de dados com esse ID e restaura a sessão (login, carrinho). *Privacidade:* cookies de terceiros permitem cruzar o ID com cadastros e rastrear seu comportamento entre sites (daí a LGPD).

**s.35–37 · Web cache e "A Grande Lição" [T7]**
- *Explicação:* o proxy fica perto dos clientes; **hit** = responde direto; **miss** = busca na origem, guarda e entrega. *Exemplo numérico do slide:* LAN de 10 Gbps, link de acesso de 100 Mbps, 100 objetos/s de 1 Mb. **Sem cache:** 100 × 1 Mb = 100 Mbps = **100 % de uso** do link → fila cresce sem parar (atraso de minutos). **Com 40 % de hits:** só 60 req/s vão à Internet → 60 Mbps = **60 %** de uso → fila esvazia; atraso médio = 0,4 × 0 + 0,6 × 2 s = **1,2 s**. *A Grande Lição:* o proxy resolveu o gargalo **sem comprar um link mais rápido**.

**s.38 · GET condicional [T7]**
- *Explicação:* para saber se a cópia do cache ainda é boa, o cache pergunta com `If-Modified-Since: <data>`. Se o arquivo **não mudou**, o servidor responde `304 Not Modified` com **corpo vazio** (economiza banda); se **mudou**, responde `200 OK` com o novo arquivo.

**s.39–48 · Evolução HTTP/1.0 → 3 e o "Ponto Chave" [T7]**
- *Explicação:* o limite físico (velocidade da luz) não muda, então a evolução reduz **idas e voltas (RTT)**. HTTP/1.0: uma conexão por objeto. HTTP/1.1: persistente + pipelining, mas com HoL na aplicação. HTTP/2: **binário**, quebra as mensagens em *frames* de *streams* e os **multiplexa** numa única conexão TCP → acaba o HoL da aplicação; porém, se o TCP perde **um** pacote, ele segura **todos** os streams até a retransmissão (HoL do transporte). HTTP/3: troca TCP por **QUIC sobre UDP**, com TLS 1.3 embutido, 1 RTT de handshake (0 RTT em reconexão) e streams independentes → perda em um stream não atrapalha os outros.
- ***Ponto Chave (s.48):*** *o HTTP/2 resolveu o bloqueio na camada de aplicação, mas o HTTP/3 foi necessário para resolver o bloqueio no transporte.*

---

### A3 — SMTP, DNS, P2P e Sockets

**s.6 · SMTP: entrega direta, TCP/25**
- *Explicação:* o servidor de e‑mail de origem abre uma conexão TCP direto com o servidor de destino (sem intermediários de aplicação). Três fases: apresentação (`HELO`), transferência (`MAIL FROM`, `RCPT TO`, `DATA`…), encerramento (`QUIT`). Comandos em texto e respostas numéricas (`250 OK`, `354`).

**s.9 · SMTP (push) × HTTP (pull); ASCII de 7 bits e MIME**
- *Explicação:* **HTTP é pull**: o cliente puxa; cada objeto vem em uma resposta separada. **SMTP é push**: o remetente empurra; vários objetos (texto + anexos) vão agrupados numa **única mensagem multipart**. O SMTP clássico só aceita **ASCII de 7 bits**, então anexos binários e acentos precisam do **MIME**, que converte para texto (Base64).

**s.10 · "Regra de Ouro": cabeçalho e corpo separados por linha em branco; envelope × mensagem**
- *Explicação:* o **envelope** (`MAIL FROM`, `RCPT TO`) é usado só pelos servidores para entregar; o usuário não o vê. A **mensagem** (RFC 5322) tem cabeçalho (`From`, `To`, `Subject`) e corpo, separados **obrigatoriamente por uma linha em branco**. Distinguir os dois importa para segurança: o `From:` que você vê pode ser diferente do `MAIL FROM` real (base do spoofing).

**s.13–15 · POP3 × IMAP × Webmail**
- *POP3:* filosofia "baixar e apagar"; três fases (autorização `user/pass` → transação `list/retr/dele` → atualização `quit`, quando o servidor apaga o que foi marcado); sem bom suporte a vários dispositivos.
- *IMAP:* filosofia "sincronizar"; mensagens e pastas ficam no servidor, que memoriza o estado (lida, respondida, apagada) → o notebook e o celular veem a mesma coisa; é **stateful** e permite baixar só cabeçalhos.
- *Webmail:* o navegador é o agente de usuário e fala HTTP; o servidor web traduz para SMTP/IMAP por trás.

**s.17–18 · Spoofing e SPF + DKIM + DMARC**
- *Explicação:* o SMTP original não verifica se o IP que envia tem autorização para falar em nome do domínio. Defesas via **DNS**: **SPF** (registro TXT lista os IPs autorizados), **DKIM** (assinatura digital; a chave pública fica no DNS e prova que o conteúdo não foi alterado), **DMARC** (política: *none* / *quarantine* / *reject* conforme o resultado de SPF e DKIM).

**s.20 · DNS: serviços agregados e "por que não centralizar" [T8]**
- *Explicação:* além de traduzir nome → IP: **host aliasing** (um nome canônico, vários apelidos, via CNAME), **mail server aliasing** (registro MX diz onde entregar o e‑mail do domínio), **distribuição de carga** (um nome → vários IPs em rodízio). Centralizar seria catastrófico: **ponto único de falha**, **volume de tráfego** (bilhões de consultas), **latência geográfica** e **impossibilidade de manutenção** de bilhões de registros num só lugar.

**s.21–23 · Hierarquia: raiz, TLD, autoritativo [T8]**
- *Explicação:* a autoridade é **delegada de cima para baixo**. A **raiz** só sabe indicar o servidor do TLD (`.br`, `.com`); o **TLD** só sabe indicar o autoritativo da organização; o **autoritativo** tem o mapeamento real (nome → IP). A raiz tem 13 identificadores lógicos (A–M), mas cada um é uma rede **anycast** com mais de 1600 instâncias espalhadas; se uma cai ou sofre DDoS, o roteamento (BGP) leva o tráfego à instância mais próxima.

**s.24–26 · DNS local, iterativa × recursiva [T8]**
- *DNS local:* resolvedor do ISP/campus; **não** faz parte da hierarquia oficial; o endereço dele chega ao seu dispositivo por DHCP.
- *Iterativa:* o servidor consultado **não resolve**; responde com uma **referência** ("pergunte ao servidor X"). Quem corre atrás é o solicitante (aqui, o DNS local): ele pergunta à raiz, depois ao TLD, depois ao autoritativo. "Os servidores de topo apenas indicam o caminho."
- *Recursiva:* o servidor consultado **assume** a busca e age como cliente do próximo nível. O host usa isso com o DNS local (faz uma pergunta simples e espera a resposta pronta). **Risco:** sobrecarrega o topo e facilita DDoS; por isso raiz e TLDs geralmente **desativam** a recursão.

**s.27 · "O cache é o herói da performance" [T8]**
- *Explicação:* depois que o DNS local aprende um mapeamento, guarda; as próximas consultas são respondidas na hora, e raiz/TLD quase nunca são consultados. O **TTL** (definido pelo dono do domínio) é o prazo de validade: expirado, a entrada é descartada, para evitar IPs desatualizados. O cache DNS do seu PC pode ser visto com `ipconfig /displaydns`.

**s.28–29 · Registros e mensagem DNS [T8]**
- *Registros (Name, Value, Type, TTL):* A (hostname → IPv4); NS (domínio → servidor autoritativo); CNAME (apelido → nome canônico); MX (domínio → servidor de e‑mail); TXT (texto: SPF/DKIM).
- *Mensagem:* consulta e resposta têm o mesmo formato; o **ID de 16 bits** casa resposta com pergunta; flags **QR** (0 consulta/1 resposta), **AA** (resposta autoritativa), **RD/RA** (recursão desejada/disponível); contadores e seções (Questões, Respostas, Autoridade, Adicionais). Roda sobre **UDP/53**.

**s.32–35 · Cliente‑servidor × P2P: as fórmulas e o "Veredito"**
- *Variáveis:* F = tamanho do arquivo; N = nº de clientes; u_s = upload do servidor; d_min = download do cliente mais lento; uᵢ = upload do peer i.
- *Cliente‑servidor:* `D_cs ≥ max{ N·F/u_s , F/d_min }`. O servidor precisa enviar **N cópias inteiras**: tempo `N·F/u_s` cresce **linearmente com N**.
- *P2P:* `D_p2p ≥ max{ F/u_s , F/d_min , N·F/(u_s + Σuᵢ) }`. O servidor envia ao menos **uma** cópia; o pior cliente limita por `F/d_min`; e o 3º termo mostra que, **quanto mais peers entram, mais upload total** (Σuᵢ cresce junto com N) → o tempo **estabiliza**.
- *Exemplo (F = 15 Gb, u_s = 30 Mbps, d = 2 Mbps, u = 0,3 Mbps):* N = 10 → ambos 2,1 h (o gargalo é o download do cliente); N = 1000 → cliente‑servidor **138,8 h** (≈ 6 dias) × P2P **12,6 h**.
- ***Veredito (s.35):*** *em distribuição em massa, a arquitetura P2P é a única solução viável.* (Mas Netflix/Spotify usam cliente‑servidor + CDN para controlar direitos autorais e qualidade.)

**s.36–38 · BitTorrent: vocabulário, regra de ouro, rarest first, tit‑for‑tat**
- *Vocabulário:* **torrent** = arquivo de metadados (hashes + endereço do tracker); **tracker** = "páginas amarelas": lista IPs, **não** guarda o arquivo; **chunk** = pedaço (~256 KB); **swarm** = o grupo de peers trocando chunks.
- *Ciclo de vida:* Alice baixa o `.torrent` num site comum → contata o tracker → recebe IPs → abre conexões TCP e troca chunks. Ao completar, vira **seeder** (altruísta) ou **leecher** que sai (egoísta).
- *Regra de ouro:* enquanto baixa um chunk, ela **faz upload** dele a outro peer.
- ***Rarest first:*** pede primeiro os chunks **mais raros** do enxame — para que sumam menos se o dono original sair.
- ***Tit‑for‑tat:*** mede quem lhe envia mais rápido e só envia (*unchoke*) para os **4 melhores**; quem não contribui fica *choked* (estrangulado).

**s.43–46 · "Segredo" do socket UDP**
- *Explicação:* no UDP não há conexão, então **cada `sendto` precisa levar IP e porta de destino**. O servidor faz `bind` numa porta fixa e `recvfrom`; o `recvfrom` devolve **os dados e a tupla `(IP, porta)` do remetente**. Com essa tupla ele sabe para onde responder (`sendto(..., addr)`). O servidor UDP é *stateless* — não guarda sessão.

**s.47–51 · Sockets TCP: welcoming × connection [T5]**
- *Explicação:* o servidor cria o **socket de boas‑vindas** (`socket → bind → listen`), que só "atende o interfone". `accept()` **bloqueia** até alguém conectar; quando o handshake termina, devolve um **novo socket de conexão** dedicado àquele cliente. A conversa acontece nesse socket (`recv/send`); `conn.close()` fecha só aquele, e o welcoming segue ouvindo. O SO distingue os sockets de conexão pela **quádrupla**. `listen(N)` = tamanho da fila de pedidos pendentes.
- *Cliente:* `connect()` dispara o handshake de 3 vias; depois `send()` não precisa de endereço (o socket já está ligado ao servidor).

**s.50 · TCP não preserva fronteiras de mensagem**
- *Explicação:* o TCP entrega um **fluxo contínuo de bytes**; duas chamadas `send()` podem chegar como um único `recv()` (ou uma `send` ser quebrada em duas `recv`). Por isso a **aplicação** precisa delimitar suas mensagens (ex.: `Content-Length` do HTTP, a linha em branco, o `.` do SMTP).

**s.52 · Quatro decisões de projeto de protocolo**
- *Explicação:* (1) **Estado:** stateful (IMAP, FTP) × stateless (HTTP, DNS). (2) **Transporte:** confiável (TCP) × tolerante a perdas (UDP). (3) **Canal de controle:** in‑band (HTTP, SMTP — controle e dados na mesma conexão) × out‑of‑band (FTP — um canal para comandos, outro para dados). (4) **Paradigma:** cliente‑servidor × P2P.

---

### A4 — Transporte (UDP, rdt, GBN, SR)

**s.4 · Analogia das casas [T4]**
- *Explicação:* 12 crianças da casa A trocam cartas com 12 da casa B. As **crianças** = processos; **cartas** = mensagens; **casas** = hosts (IPs). **Ana e Pedro** (os irmãos que juntam e distribuem as cartas dentro de cada casa) = camada de **transporte** (multiplexam ao enviar, demultiplexam ao receber). Os **Correios** = camada de **rede** (levam lotes de cartas de casa a casa, sem olhar os nomes das crianças). Moral: transporte = **processo‑a‑processo**; rede = **host‑a‑host**. E o transporte pode **melhorar** o serviço do correio (por exemplo, garantir entrega), mas não pode exceder o que a rede entrega (vazão).

**s.6 · Portas e multiplexação [T6]**
- *Explicação:* **mux** (emissor): junta dados de vários sockets, anexa porta de origem/destino. **Demux** (receptor): usa as portas do cabeçalho para entregar ao socket correto. Faixas: 0–1023 bem conhecidas, 1024–49151 registradas, 49152–65535 efêmeras (o cliente recebe uma delas para a conexão).

**s.8–11 · Demux UDP × TCP e o "efeito funil" [T6]**
- *UDP:* socket indexado por **(IP destino, porta destino)**. Clientes diferentes que mandam para a mesma porta caem no **mesmo socket** (**efeito funil**); o SO ignora a origem ao entregar; a aplicação lê a origem pelo `recvfrom()`.
- *TCP:* socket indexado pela **quádrupla** (IP origem, porta origem, IP destino, porta destino) — os 4 valores são usados juntos. Cada conexão aceita pelo `accept()` ganha seu próprio socket, com buffers e números de sequência exclusivos.
- *Exemplo do slide (servidor B, porta 80):* (A,9157,B,80) → socket 1; (C,5775,B,80) → socket 2; (C,9157,B,80) → socket 3. Note que sockets 1 e 3 têm a **mesma porta de cliente** (9157), mas **IPs diferentes**, logo são sockets diferentes.

**s.12–13 · UDP: o que é e por que usar [T4]**
- *Explicação:* "sem frescuras": sem conexão, melhor esforço, sem ordem, stateless. Cabeçalho **8 bytes**: porta origem, porta destino, comprimento, checksum (16 bits cada). Motivos para usar: **sem handshake** (latência de início zero), **sem estado** no servidor, **sem controle de congestionamento** (a aplicação dita o ritmo), cabeçalho compacto. Usos: DNS, SNMP, VoIP, streaming ao vivo, jogos, IoT, e hoje o **QUIC/HTTP‑3**.

**s.14–15 · Checksum da Internet (com exemplo) e o princípio fim‑a‑fim**
- *Emissor:* trata o conteúdo como **palavras de 16 bits**, soma tudo; se a soma passar de 16 bits (*carry‑out*), o excedente é somado de volta no bit menos significativo (**wraparound**); depois **inverte todos os bits** (complemento de 1) e grava no campo checksum.
- *Receptor:* soma tudo, **incluindo** o checksum recebido; se o resultado for `1111 1111 1111 1111`, está íntegro; qualquer bit 0 → erro.
- *Exemplo do slide:* `1110011001100110 + 1101010101010101 = 1 1011101110111011`; soma o 17º bit de volta → `1011101110111100`; inverte → **`0100010001000011`** (checksum). Receptor: `1011101110111100 + 0100010001000011 = 1111111111111111` ✔.
- *Limites:* só **detecta** (não corrige nem pede retransmissão); erros que se compensam podem passar despercebidos.
- *Princípio fim‑a‑fim:* mesmo que o enlace tenha CRC, a verificação no transporte é necessária, pois erros podem ocorrer na memória de um roteador, fora do alcance do CRC do enlace.

**s.18–27 · rdt 1.0 → 3.0 (a linha de raciocínio) [T9]**
- *1.0:* canal perfeito → nada a fazer. *2.0:* canal com erros de bit → **checksum + ACK/NAK + retransmissão** (ARQ). Protocolo "pare‑e‑espere".
- *Problema oculto do 2.0 (s.20):* **e se o próprio ACK/NAK se corromper?** O remetente não sabe o que o receptor recebeu; a única saída segura é retransmitir. Mas aí o receptor pode receber **o mesmo dado duas vezes** sem saber se é novo ou repetido. **Solução (2.1): número de sequência (0 ou 1)** no pacote — o receptor descarta duplicata.
- *2.2:* elimina o NAK: o receptor manda ACK **com o nº de seq do último pacote correto**; um **ACK duplicado** faz o mesmo papel do NAK (o remetente retransmite).
- *3.0 (s.25–27):* acrescenta **temporizador** para tratar **perdas** (de pacote ou de ACK). Cenários: sem perda; pacote perdido (timeout → reenvia); ACK perdido (reenvia; receptor reconhece a duplicata pelo seq e só repete o ACK); timeout prematuro (gera duplicata, ACKs duplicados).

**s.28 · Desempenho do rdt 3.0**
- *Explicação:* o pare‑e‑espere deixa o remetente **ocioso** esperando o ACK. Utilização `U = (L/R) / (RTT + L/R)`. Exemplo: enlace 1 Gbps, RTT 30 ms, pacote de 1 KB (8000 bits): `L/R = 8 µs` → `U = 0,008 ms / 30,008 ms ≈ 0,00027` (0,027 %). Ou seja, o protocolo limita o enlace, e não o contrário.

**s.29 · Pipelining**
- *Explicação:* enviar **vários pacotes sem esperar ACK**. Com N pacotes em voo, `U = N·(L/R) / (RTT + L/R)` — cresce linearmente com N. Consequências: números de sequência em faixa maior e **buffers** no remetente (e às vezes no receptor).

**s.30–33 · Go‑Back‑N (GBN)**
- *Janela N:* o remetente pode ter até N pacotes enviados e ainda não confirmados. `base` = mais antigo sem ACK; `nextseqnum` = próximo a enviar. **Um só timer** (do pacote `base`).
- *ACK cumulativo:* `ACK(n)` = "recebi tudo até n em ordem" → `base = n + 1`.
- *Timeout:* reenvia **todos** os pacotes de `base` até `nextseqnum − 1` (daí "volta N").
- *Receptor:* só aceita o pacote `expectedseqnum`; qualquer outro é **descartado** e ele reenvia o ACK do último em ordem. **Não usa buffer.**
- *Exemplo do slide (s.33):* pacotes 0–5, o 2 se perde. O receptor responde ACK0, ACK1, e **ACK1 repetido** para cada um de 3, 4 e 5 (descartados). O remetente ignora os ACKs repetidos e espera o timeout do pacote 2, quando reenvia **2, 3, 4, 5** (desperdício).

**s.34–36 · Selective Repeat (SR)**
- *Explicação:* ACK **individual**, **timer por pacote**, **buffer** no receptor para os fora de ordem. Mesmo exemplo: o receptor confirma 3, 4 e 5 individualmente e os **guarda**; no timeout reenvia **só o pacote 2**; ao chegar o 2, entrega 2, 3, 4, 5 em ordem.
- *Regras do receptor:* pacote em `[rcv_base, rcv_base+N−1]` → ACK(n) e bufferiza/entrega; pacote em `[rcv_base−N, rcv_base−1]` (já entregue) → **reenvia ACK(n)** (o ACK anterior pode ter se perdido; sem isso o remetente nunca avança); fora disso, ignora.

**s.37 · "Dilema da janela" do SR**
- *Explicação:* o tamanho da janela deve ser **no máximo metade do espaço de numeração**. Exemplo do slide: números 0–3 (4 números), N = 3. O remetente manda 0, 1, 2; o receptor aceita e passa a esperar a janela [3, 0, 1]. Todos os ACKs se perdem. O remetente dá timeout e reenvia o **pacote 0 antigo**. O receptor vê "0", que está na sua nova janela, e o **aceita como dado novo** → erro. Com N = 2 (metade de 4) isso não acontece.

**s.38 · Comparativo GBN × SR**
- GBN: ACK cumulativo, 1 timer, sem buffer no receptor, retransmite a janela toda, simples, bom para pouca perda. SR: ACK individual, timer por pacote, com buffer, retransmite só o perdido, complexo, bom para links ruidosos.

---

### A5 — TCP

**s.3–4 · Características e janela efetiva [T10]**
- *Explicação:* **ponto a ponto** (um emissor, um receptor; sem multicast); **fluxo de bytes** confiável e em ordem (a aplicação não vê fronteiras de mensagem); **pipelining**; **full duplex** (dados nos dois sentidos ao mesmo tempo); **orientado a conexão** (handshake inicializa buffers e variáveis; o estado fica **só nos hosts**, não nos roteadores); **MSS** = máximo de bytes de dados por segmento.
- *Duas proteções:* **fluxo** (`rwnd`, protege o receptor) e **congestionamento** (`cwnd`, protege a rede). O remetente respeita **`min(rwnd, cwnd)`**.

**s.6 · Números de sequência e ACK [T11]**
- *Seq:* número do **primeiro byte** de dados do segmento; o TCP numera **bytes**, não segmentos. O primeiro número (ISN) é aleatório (segurança).
- *ACK:* número do **próximo byte que o receptor espera**; é **cumulativo** (confirma tudo que veio em ordem).
- *Exemplo:* A envia `Seq = 0` com 1000 bytes → B responde `ACK = 1000`.
- *Fora de ordem:* a RFC não manda descartar nem guardar; hoje se guarda e usa a opção **SACK** para pedir só os "buracos".

**s.9 · Piggybacking (cenário Telnet)**
- *Explicação:* o usuário digita `C` (1 byte): A envia `Seq=42, ACK=79`. O servidor recebe, faz o **eco** de `C` e **confirma** no mesmo segmento: `Seq=79, ACK=43, dado='C'`. O ACK vai "de carona" no segmento de dados, sem gastar um segmento vazio. A matemática do ACK: 42 + 1 byte = 43.

**s.10–12 · RTT, Karn, EWMA, timeout e backoff [T15]**
- *Problema:* o timeout de retransmissão não pode ser fixo — o RTT varia. Muito curto → retransmissão à toa; muito longo → reage devagar à perda real.
- *SampleRTT:* tempo medido entre enviar um segmento e receber seu ACK. ***Algoritmo de Karn:*** ignora amostras de segmentos **retransmitidos**, pois não dá para saber se o ACK é do envio original (atrasado) ou da retransmissão.
- *Média suavizada (EWMA):* `EstimatedRTT = (1−α)·EstimatedRTT + α·SampleRTT`, α = 0,125 — picos isolados não bagunçam a estimativa.
- *Margem:* `DevRTT = (1−β)·DevRTT + β·|SampleRTT − EstimatedRTT|`, β = 0,25 mede o quão "nervosa" está a rede.
- *Timeout final:* `TimeoutInterval = EstimatedRTT + 4·DevRTT`.
- ***Backoff exponencial:*** quando ocorre um timeout **real**, o intervalo é **dobrado**; as fórmulas só voltam quando chegam ACKs novos.

**s.14–16 · Confiabilidade no TCP: três eventos do remetente**
- *Explicação:* (1) **Dados da aplicação:** cria segmento com `Seq = NextSeqNum`, avança `NextSeqNum`, liga o timer se ele não estiver rodando. (2) **Timeout:** retransmite **apenas** o segmento não confirmado de menor seq e reinicia o timer. (3) **ACK com valor y:** se `y > SendBase`, atualiza `SendBase = y` e reinicia o timer se ainda houver pendentes. Usa **um único timer**, para o segmento mais antigo sem ACK.

**s.17–19 · ACK perdido, timeout prematuro, ACK cumulativo [T11]**
- *ACK perdido:* A envia `Seq=92, 8 B`; o `ACK=100` se perde; dá timeout; A reenvia `Seq=92`; B descarta a duplicata e reenvia `ACK=100`.
- *Timeout prematuro:* o timeout dispara **antes** de o ACK chegar; A reenvia `Seq=92` à toa; B recebe duplicata e re‑confirma. Gera tráfego inútil.
- *Vantagem do ACK cumulativo:* A envia `Seq=92, 8 B` e `Seq=100, 20 B`; o `ACK=100` se perde, mas o `ACK=120` chega **antes do timeout**. Como `120 > SendBase (92)`, A entende que **tudo até 119 chegou** → **nenhuma retransmissão**. O ACK posterior "cobre" o perdido.

**s.20 · Regras de geração de ACK [T11/T12]**
- *Explicação (receptor):*

  | Evento | Ação |
  |---|---|
  | Chegou em ordem, tudo anterior já confirmado | **ACK atrasado**: espera até 500 ms pelo próximo segmento; se não vier, envia ACK |
  | Chegou em ordem, e há outro segmento esperando ACK | envia **um único ACK cumulativo imediato** para os dois |
  | Chegou fora de ordem (maior que o esperado, há lacuna) | **ACK duplicado imediato** com o número do próximo byte esperado |
  | Chegou e preenche a lacuna (parcial ou total) | ACK imediato |

- *Ligação:* explica por que o receptor sem dados para enviar ainda manda ACKs (P15 Q7a) e por que o Wireshark mostra, às vezes, um ACK a cada 2 segmentos (WS Q11).

**s.21 · Fast Retransmit e "por que 3 ACKs?" [T14/T15]**
- *Explicação:* o timeout do TCP costuma ser longo. Quando um segmento se perde, cada segmento seguinte que chega gera um **ACK duplicado**. Quando o remetente recebe **3 ACKs duplicados** (4 ACKs iguais no total), ele conclui que o segmento seguinte foi perdido e o **retransmite antes do timeout**.
- *Por que 3?* Pequenas **reordenações** da rede podem gerar 1 ou 2 duplicados sem perda real; o terceiro é forte indício de perda.

**s.23–26 · Controle de fluxo [T13]**
- *Explicação:* o receptor tem um buffer `RcvBuffer`. A aplicação pode ler mais devagar do que o TCP entrega. O receptor calcula `rwnd = RcvBuffer − [dados na fila]` e o **escreve no cabeçalho de cada segmento**. O remetente garante `LastByteSent − LastByteAcked ≤ rwnd`.
- ***Freio:*** se o buffer lotar, `rwnd = 0`; o remetente **para**, mas continua mandando **segmentos de 1 byte** periodicamente para provocar um novo `rwnd` (senão a conexão travaria quando o buffer esvaziasse).
- *Analogia do slide:* supercomputador mandando dados a um celular antigo; o celular responde "buffer quase cheio" via `rwnd`.

**s.27–29 · Por que o handshake de 2 vias falha [T10]**
- *Explicação:* com 2 vias (`req_conn(x)` → `acc_conn(x)`), o servidor aloca recursos assim que recebe o pedido. Problema: um pedido **antigo e atrasado** (de um cliente que já desistiu) chega depois; o servidor o aceita e cria uma **conexão meio‑aberta (half‑open)**, gastando memória à toa — ou aceita duas vezes (conexão duplicada). Falta um **terceiro passo** em que o cliente diga "sim, ainda quero".
- *3 vias:* `SYN (seq=x)` → `SYN+ACK (seq=y, ack=x+1)` → `ACK (ack=y+1)`. O servidor só considera a conexão **estabelecida (ESTAB)** após o 3º passo — prova de "vivacidade" do cliente. Também sincroniza os números de sequência iniciais dos dois lados.

**s.30–31 · Fechamento [T10]**
- *Explicação:* cada lado fecha **a sua parte** independentemente: envia `FIN=1`; o outro responde `ACK`. Depois do FIN, o host **não pode mais enviar** dados, mas **ainda pode receber**. O ACK e o FIN do segundo lado podem ir juntos. O lado que fecha por último passa por `TIME_WAIT` (2·MSL) antes de `CLOSED`.

---

### A6 — Controle de congestionamento

**s.2 · Definição: congestionamento ≠ controle de fluxo [T13/T14]**
- *Explicação:* "muitas fontes enviando muitos dados rápido demais para a rede manipular". Sinais: **perda de pacotes** (buffers de roteador estouram) e **longos atrasos** (filas). Diferença para o fluxo: o fluxo protege o **receptor**; o congestionamento protege a **rede no meio**.

**s.3–10 · Cenários I–III e os 3 custos**
- *Cenário I (buffers infinitos):* vazão máxima por conexão = R/2 (dois fluxos dividem R); mas o **atraso tende ao infinito** quando a carga se aproxima da capacidade.
- *Cenário II (buffers finitos + retransmissão):* a carga oferecida à rede (λ'in = dados originais + retransmissões) passa a ser maior que a da aplicação. **Custo 1:** para obter uma vazão útil, o transmissor precisa trabalhar mais (retransmitir os pacotes perdidos). **Custo 2:** **timeouts prematuros** geram cópias desnecessárias do mesmo pacote, que gastam banda e reduzem a vazão útil máxima.
- *Cenário III (4 fontes, vários saltos):* quando uma fonte fica agressiva, ocupa o buffer do roteador R2; os pacotes do outro fluxo chegam à fila cheia e são descartados → a vazão útil desse fluxo vai a **~0** (colapso por congestionamento). **Custo 3:** quando um pacote é descartado **no meio** do caminho, toda a capacidade gasta nos saltos anteriores foi **desperdiçada**.

**s.11 · AIMD**
- *Explicação:* como o IP não avisa de congestionamento, o TCP usa a **perda** como sinal. **Aumento aditivo:** +1 MSS por RTT sem perdas (vai sondando banda). **Redução multiplicativa:** corta `cwnd` pela metade ao detectar perda. O gráfico forma um "**dente de serra**". Taxa ≈ `cwnd / RTT` bytes/s.

**s.12 · Partida lenta e o "paradoxo do nome" [T14]**
- *Explicação:* a conexão começa sem saber a capacidade da rede. `cwnd = 1 MSS`. **A cada ACK recebido, `cwnd` +1 MSS**: com 1 pacote em voo chega 1 ACK → `cwnd = 2`; mandando 2, chegam 2 ACKs → `cwnd = 4`; depois 8… ou seja, a janela **dobra a cada RTT** (crescimento exponencial). O "paradoxo": chama‑se "lenta" porque **começa de 1**, mas o crescimento é rápido.

**s.13 · `ssthresh` e reação a perdas [T12/T14]**
- *Explicação:* `ssthresh` é o limiar que marca a mudança de estratégia. `cwnd < ssthresh` → **slow start** (exponencial); `cwnd ≥ ssthresh` → **congestion avoidance** (linear, +1 MSS por RTT).
  - **Timeout** (congestionamento severo): `ssthresh = cwnd/2`, `cwnd = 1 MSS` → volta ao slow start.
  - **3 ACKs duplicados** (congestionamento leve — a rede ainda entrega algo): `ssthresh = cwnd/2`, `cwnd = ssthresh` (corta pela metade) → segue em congestion avoidance.
- *Pegadinha (P13 Q8e, TT Q3e):* `ssthresh` passa a ser **metade do `cwnd` no momento da perda**, e **não** "metade do ssthresh anterior".

**s.14 · Tahoe × Reno**
- *Explicação:* **Tahoe** (mais antigo) não distingue o tipo de perda: qualquer perda (timeout ou 3 dups) → `cwnd = 1 MSS` e reinicia o slow start (derruba a vazão). **Reno** introduz a **recuperação rápida (fast recovery)**: timeout → `cwnd = 1`; **3 dups** → `cwnd` cai só pela metade (`ssthresh`) e continua em prevenção linear.

**s.15–16 · Vazão do TCP e a equação de Mathis**
- *Vazão média:* o `cwnd` varia entre `W/2` e `W` linearmente, então a média é **`0,75·W/RTT`** (W = janela no momento da perda).
- *Em função da perda L:* **`Vazão ≈ 1,22·MSS / (RTT·√L)`**. O `√L` no denominador é "fatal": se a perda passa de 1 % para 4 % (×4), a raiz vira ×2 e a **vazão cai pela metade**. O RTT também limita a banda.

**s.17 · Justiça do TCP**
- *Explicação:* duas conexões TCP que dividem um gargalo convergem para a **mesma taxa**, sem se comunicarem. O aumento aditivo move o estado "em paralelo" à reta de justiça; a redução multiplicativa o move **em direção à origem**; o zigue‑zague converge para o ponto onde a **soma das taxas = capacidade** e as **taxas são iguais**.

**s.18 · Burlando a justiça**
- *Explicação:* (1) **UDP** não tem AIMD: não recua nas perdas, então "atropela" as conexões TCP, que recuam. (2) **Conexões TCP em paralelo:** se 9 conexões dividem o link (R/9 cada) e um usuário abre 11 novas, ele fica com **11/20** da banda — mais da metade do gargalo. Navegadores e gerenciadores de download fazem isso.

**s.19–21 · CUBIC e BBR**
- *CUBIC* (padrão Linux/Windows): `W(t) = C·(t−K)³ + Wmax`; cresce rápido para recuperar, **estabiliza perto do último limite** (Wmax); na perda corta **×0,7** (não ×0,5); depende do tempo desde a última perda, não do RTT (mais justo entre RTTs diferentes).
- *BBR* (Google): **não usa perda**. Estima continuamente a banda do gargalo (BtlBw) e o RTT mínimo (RTprop) e opera no **BDP = BtlBw × RTprop** (máxima vazão com mínimo atraso), evitando *bufferbloat*.

**s.23–28 · QUIC**
- *Explicação:* roda **sobre UDP**, implementado na aplicação; herda a lógica de erros e congestionamento do TCP; **handshake de transporte + TLS 1.3 em 1 RTT** (0‑RTT em reconexão); **streams independentes** (uma perda num stream **não** bloqueia os outros → fim do HoL); **migração de conexão** (usa um *Connection ID*, não IP+porta, então trocar Wi‑Fi por 5G não derruba a conexão). Padronizado nas RFCs 9000–9002 e 9114 (HTTP/3).

---

## 4. Itens do Wireshark Lab que "viram" pergunta de prova
| Questão do lab | Reaparece como | Onde estudar |
|---|---|---|
| Q1–Q3 (IP e porta de cliente/servidor) | T1/T6 | A2 s.10; A4 s.8–10 |
| Q4–Q5 (SYN, SYN‑ACK, ACK = ISN+1) | T10 | A5 s.29 |
| Q6–Q8 (seq/len dos 6 primeiros segmentos) | T11 | A5 s.6 |
| Q7 (EstimatedRTT) | T15 | A5 s.10–12 |
| Q9 (rwnd mínimo; receptor freia o remetente?) | T13 | A5 s.23–26 |
| Q10–Q11 (retransmissões; ACK a cada 2 segmentos) | T11/T14 | A5 s.20–21 |
| Q12 (vazão) | A6 s.15 | |
| Q13 (SS e CA no gráfico Stevens) | T14 | A6 s.12–13 |

---

## 5. Estratégia de estudo (por retorno de nota)

1. **Dia 1 — "pontos certos":** T1, T2, T3, T4, T5, T6 (teoria curta e repetitiva). Escreva cada resposta de cabeça em 3–5 linhas.
2. **Dia 2 — "contas":** T11 (seq/ACK, diagramas), T15 (RTT), T9 (checksum, U do stop‑and‑wait, GBN×SR no papel). Refaça P13 Q9, P15 Q8, TT Q1/Q4.
3. **Dia 3 — "TCP completo":** T12 (as cinco V/F), T13, T14, T10. Escreva a tabela fluxo × congestionamento do zero e uma tabela de `cwnd` por RTT (Resumo §8.4).
4. **Dia 4 — "narrativas":** T7 (HTTP) e T8 (DNS) como textos de 1 página; depois leia o [Fluxo_Completo_Rede.md](Fluxo_Completo_Rede.md) para ver tudo encadeado.
5. **Véspera:** releia a seção 1 (placar) e a seção 3 (destaques de slides); refaça as 5 V/F e a pergunta "fluxo × congestionamento" sem consulta.

> Sinal de alerta: se você não consegue explicar **sem olhar** (a) a diferença entre `rwnd` e `cwnd`, (b) por que o servidor TCP tem n+1 sockets, (c) por que `ACK ≠ Seq + len` do mesmo segmento, ainda não está pronto — essas três são as mais cobradas.
