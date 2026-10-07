# Redes 1 — Gabarito comentado (P1)

Cobre **todos** os arquivos de `Exercícios/`: lista de revisão (rdt), lista de provas anteriores, Prova 1 (2013), Prova oral (2014), 2ª avaliação (2015), Tarefa TCP e Wireshark Lab.

## Como estudar com este arquivo
Cada questão tem a mesma estrutura:
- **O que a questão testa** — o conceito por trás.
- **Raciocínio** — como chegar na resposta, passo a passo.
- **Resposta para escrever na prova** — texto pronto, no nível de detalhe que vale nota.
- **Erros comuns** — onde se perde ponto.
- **Estude:** — seção do [Resumo](Resumo_P1_Redes.md) com a teoria (ex.: *Resumo §5.6*). Os exemplos numéricos estão no *Resumo §8*.

As perguntas **abertas que se repetem** (HTTP, DNS, TCP, fluxo × congestionamento, slow start × CA, bit alternante/GBN/SR) estão desenvolvidas por inteiro na **Parte A**. Nas questões, a resposta-de-prova é reescrita lá; a Parte A é onde você aprende o assunto a fundo.

> ⚠️ Não há gabarito oficial do professor. Onde há mais de uma leitura possível, está sinalizado.

## Índice
- Parte A — Respostas desenvolvidas (A1 HTTP · A2 DNS · A3 TCP · A4 Fluxo × Congestionamento · A5 Slow start × CA · A6 rdt/GBN/SR · A7 IP+porta · A8 TCP × UDP · A9 Sockets TCP/UDP)
- Parte B — Lista de revisão (rdt)
- Parte C — Lista de questões de provas anteriores
- Parte D — Prova 1 (20/12/2013)
- Parte E — Prova oral (25/08/2014)
- Parte F — 2ª avaliação (2015)
- Parte G — Tarefa TCP
- Parte H — Wireshark Lab TCP

---

# PARTE A — Respostas desenvolvidas

## A1. Como funciona o HTTP *(Resumo §2.4)*

**Ideia central.** O HTTP é o protocolo da *aplicação Web*. Ele define **o formato, a ordem e as ações** das mensagens trocadas entre um **cliente** (navegador) e um **servidor Web**. Ele **não** cuida de entrega confiável: delega isso ao **TCP**.

**Passo a passo de uma visita a `http://www.site.com/pasta/foto.jpg`:**
1. **URL:** `esquema://host/caminho`. O navegador separa o host (`www.site.com`) do caminho (`/pasta/foto.jpg`).
2. **DNS:** descobre o IP do host (A2).
3. **TCP:** abre conexão com o IP, porta **80** (443 em HTTPS) — handshake de 3 vias (1 RTT).
4. **Requisição** (texto ASCII):
   ```
   GET /pasta/foto.jpg HTTP/1.1\r\n      ← linha de requisição: método, URL, versão
   Host: www.site.com\r\n                 ← linhas de cabeçalho (nome: valor)
   User-Agent: Firefox\r\n
   Connection: keep-alive\r\n
   \r\n                                   ← linha em branco = fim dos cabeçalhos
   [corpo: vazio no GET; no POST vão os dados do formulário]
   ```
5. **Resposta:**
   ```
   HTTP/1.1 200 OK\r\n                    ← linha de status: versão, código, frase
   Date / Server / Last-Modified / Content-Length / Content-Type
   \r\n
   [bytes do objeto]
   ```
6. Uma página = **HTML base + objetos** (imagens, CSS, JS), cada um com sua URL e sua própria requisição/resposta.

**Métodos:** GET (pede objeto; parâmetros vão na URL após `?`), POST (dados no corpo — uploads, senhas), HEAD (só cabeçalhos; usado para ver se link está quebrado), PUT (envia objeto), DELETE (apaga).
**Status:** 2xx sucesso (200 OK) · 3xx redirecionamento (301 Moved Permanently com `Location`, 304 Not Modified) · 4xx erro do cliente (400 Bad Request, 404 Not Found) · 5xx erro do servidor (500, 505 versão não suportada).

**Stateless.** O servidor **não guarda memória** das requisições anteriores. Vantagens: escalabilidade (não aloca memória por cliente) e tolerância a falhas (se reiniciar, nada a reconstruir). Para login/carrinho usa-se **cookie**: o servidor responde `Set-Cookie: 1678`; o navegador guarda e envia `Cookie: 1678` nas próximas requisições; o servidor consulta seu banco com esse ID. *O HTTP continua sem estado; quem guarda o estado é a aplicação.*

**Conexões e desempenho** (RTT = tempo de ida e volta):
- **Não persistente (HTTP/1.0):** 1 objeto por conexão TCP → `2·RTT + T_trans` por objeto (1 RTT do handshake + 1 RTT da requisição) e *slow start* recomeça a cada objeto. Página com HTML + 10 imagens = **22 RTT** (+ 11 T_trans).
- **Persistente sem pipelining (HTTP/1.1):** conexão fica aberta; 1 RTT por objeto → ≈ **12 RTT**.
- **Persistente com pipelining (default HTTP/1.1):** vários GET em lote → ≈ **3 RTT**.
- HTTP/2: binário, **multiplexa** vários streams numa só conexão TCP (fim do HoL da aplicação). HTTP/3: roda sobre **QUIC/UDP** (fim do HoL do transporte; TLS 1.3 embutido).
- **HoL (Head-of-Line) blocking:** uma resposta lenta/perdida trava as que vêm atrás na fila.

**Web cache (proxy).** Fica perto dos clientes; é *servidor* para o cliente e *cliente* para a origem. Hit → responde local; miss → busca, guarda e entrega. Reduz atraso, tráfego no link de acesso e carga na origem. **GET condicional:** `If-Modified-Since: data` → servidor responde `304 Not Modified` (sem corpo) se não mudou.

**Resposta para escrever na prova (síntese):** o HTTP é o protocolo de camada de aplicação da Web, no modelo cliente-servidor requisição/resposta, que roda sobre TCP (porta 80). O cliente abre uma conexão TCP, envia uma requisição em texto (linha de requisição com método/URL/versão, cabeçalhos, linha em branco, corpo opcional) e o servidor responde com linha de status, cabeçalhos e o objeto. É stateless; estado via cookies. A conexão pode ser não persistente (HTTP/1.0, um objeto por conexão) ou persistente (HTTP/1.1, com pipelining). Caches web e GET condicional reduzem atraso e tráfego.
**Erros comuns:** dizer que HTTP usa UDP (só o HTTP/3, via QUIC); dizer que HTTP guarda estado; esquecer que há handshake TCP antes da requisição.

---

## A2. Como funciona o DNS *(Resumo §3.2)*

**Problema.** Humanos lembram `www.utfpr.edu.br`; roteadores usam IP (`200.134.18.157`). O DNS faz o mapeamento nome ↔ IP. Também fornece **aliasing** (CNAME), **servidor de e-mail** (MX) e **distribuição de carga** (um nome → vários IPs, em rodízio).

**Por que não um servidor único?** (1) ponto único de falha; (2) volume de consultas de bilhões de usuários; (3) distância (latência); (4) impossível manter bilhões de registros num só lugar. Solução: **banco distribuído e hierárquico**.

**Os servidores:**
| Nível | Papel |
|---|---|
| **Raiz** (13 identificadores A–M, cada um é uma rede *anycast* com >1600 instâncias) | sabe quem são os servidores TLD |
| **TLD** (.com, .org, .br, .edu…) | sabe quem é o autoritativo de cada domínio abaixo dele |
| **Autoritativo** (da organização) | tem os mapeamentos reais (nome → IP) |
| **DNS local** (do ISP/campus; endereço vem por DHCP) | *não* é da hierarquia oficial; atende o host, tem **cache**, e percorre a hierarquia por ele |

**Resolvendo `www.utfpr.edu.br` (cache vazio):**
1. Host → DNS local: "qual o IP?" (**consulta recursiva**: o host quer a resposta pronta).
2. DNS local → **raiz**: raiz responde "pergunte ao TLD `.br`" (**iterativa**: só uma referência).
3. DNS local → **TLD .br**: responde "pergunte ao autoritativo da utfpr.edu.br".
4. DNS local → **autoritativo**: responde com o **IP**.
5. DNS local guarda em cache e responde ao host. (8 mensagens; com cache, 2.)

**Iterativa × recursiva.** Iterativa: "não sei, mas pergunte a X" — a carga fica no solicitante. Recursiva: o servidor consultado assume a tarefa e consulta os próximos por conta própria — sobrecarrega o topo (por isso raiz/TLD em geral não aceitam recursão).

**Cache e TTL.** Cada registro tem um *Time To Live* definido pelo dono do domínio; até expirar, o mapeamento é reutilizado (raiz e TLD quase nunca são consultados). Risco: *DNS poisoning* (cache envenenado).

**Registros de recurso (Name, Value, Type, TTL):** **A** (nome→IPv4) · **NS** (domínio→hostname do autoritativo) · **CNAME** (apelido→nome canônico) · **MX** (domínio→servidor de e-mail) · **TXT** (texto; SPF/DKIM).
**Mensagem:** consulta e resposta têm o mesmo formato (ID de 16 bits que casa pergunta/resposta, flags QR/AA/RD/RA, contadores e seções Questões/Respostas/Autoridade/Adicionais), sobre **UDP porta 53**.

**Resposta para escrever na prova (síntese):** o DNS traduz nomes em IPs usando uma base distribuída e hierárquica (raiz, TLD, autoritativos), mais servidores DNS locais com cache. O host pergunta ao DNS local, que, se não tiver em cache, consulta de forma iterativa a raiz (obtém o TLD), o TLD (obtém o autoritativo) e o autoritativo (obtém o IP) e devolve ao host. Registros A, NS, CNAME, MX; mensagens sobre UDP/53; cache com TTL.
**Erros comuns:** dizer que o host consulta a raiz diretamente; esquecer o DNS local; dizer que DNS usa TCP por padrão (é UDP/53).

---

## A3. Funcionamento geral do TCP *(Resumo §5)*

O IP entrega pacotes "no melhor esforço" (pode perder, duplicar, reordenar). O TCP, **só nos hosts**, transforma isso num **fluxo de bytes confiável, ordenado, bidirecional**.

**1. Conexão.** *Handshake de 3 vias*: cliente → `SYN, seq=x`; servidor → `SYN+ACK, seq=y, ack=x+1`; cliente → `ACK, ack=y+1` (pode já levar dados). Sincroniza os números de sequência iniciais e só no 3º passo o servidor consolida o estado (o de 2 vias falha por conexões meio-abertas). Encerramento: cada lado envia `FIN` e recebe `ACK`; o lado que fecha por último fica em `TIME_WAIT` (2·MSL).

**2. Confiabilidade.**
- Cada **byte** é numerado. `Seq` = nº do 1º byte do segmento. `ACK` = nº do **próximo byte esperado** (cumulativo).
- Remetente: **pipelining** (vários segmentos em voo) e **um único timer** para o segmento mais antigo sem ACK.
- Retransmissão por **timeout** (só o mais antigo) ou por **3 ACKs duplicados** (*fast retransmit*, antes do timeout).
- `TimeoutInterval = EstimatedRTT + 4·DevRTT`; em timeout o intervalo dobra.
- Receptor: ACK atrasado (≤500 ms) para segmento em ordem; ACK imediato para fora de ordem (duplicado); ACK cumulativo.

**3. Controle de fluxo:** `rwnd` (A4). **4. Controle de congestionamento:** `cwnd` (A4/A5). Remetente envia no máximo `min(cwnd, rwnd)`.

**5. Detalhes:** segmento tem cabeçalho de 20–60 B (portas, seq, ack, flags SYN/ACK/FIN/RST, rwnd, checksum); MSS = máx. de dados por segmento; full duplex; ponto-a-ponto (sem multicast).

**Resposta para escrever na prova (síntese):** TCP é orientado a conexão (handshake de 3 vias), confiável e ordenado: numera bytes, usa ACKs cumulativos, timer e retransmissão (timeout ou 3 dups), com timeout adaptativo; faz controle de fluxo (rwnd) e de congestionamento (cwnd: slow start, congestion avoidance, fast retransmit/recovery); fecha com FIN/ACK em cada sentido.

---

## A4. Controle de fluxo × controle de congestionamento *(Resumo §5.6, §6, §7)*

**Duas ideias diferentes que o TCP usa ao mesmo tempo:**

| | Controle de **fluxo** | Controle de **congestionamento** |
|---|---|---|
| **Problema** | remetente rápido × **aplicação receptora lenta** → estouro do buffer do receptor | muitas fontes × **roteadores no meio** → filas cheias, atrasos, perdas |
| **Protege** | o **receptor** | a **rede** |
| **Escopo** | fim-a-fim (um par remetente–receptor) | remetente ↔ rede (todos compartilham) |
| **Janela** | `rwnd` | `cwnd` |
| **Quem calcula** | **receptor**, e **avisa** explicitamente no cabeçalho | **remetente**, **infere** (perda por timeout ou 3 dups) |

### Controle de fluxo em detalhe
1. O receptor tem um buffer `RcvBuffer`. Os dados chegam da rede e ficam lá até a *aplicação* ler.
2. Se a app lê devagar, o buffer enche. O receptor calcula o espaço livre:
   `rwnd = RcvBuffer − (LastByteRcvd − LastByteRead)`
3. Ele escreve `rwnd` no campo "janela de recepção" de **todo** segmento que envia (inclusive os ACKs).
4. O remetente obedece: `LastByteSent − LastByteAcked ≤ rwnd` (bytes em voo ≤ espaço anunciado).
5. Buffer cheio → `rwnd = 0` → remetente para; mas continua mandando **segmentos de 1 byte** de sondagem para receber um `rwnd` novo (senão a conexão travaria quando o buffer esvaziasse).
Consequência: bytes não reconhecidos **nunca excedem o buffer do receptor**; e `rwnd` **varia** durante a conexão.

### Controle de congestionamento em detalhe
**Por que existe:** sem ele, retransmissões aumentam a carga, causam mais perda (colapso). Custos do congestionamento: (1) filas longas; (2) retransmissões para manter a vazão útil; (3) retransmissões desnecessárias (timeout prematuro); (4) pacote descartado no meio desperdiça o trabalho dos saltos anteriores → vazão útil pode cair a ~0.
O IP não avisa nada, então o TCP **usa a perda como sinal**.
**Estratégia AIMD:** aumento aditivo (+1 MSS por RTT sem perda) e redução multiplicativa (metade da janela na perda) → gráfico em **dente de serra**. Taxa ≈ `cwnd/RTT`.
**Variáveis:** `cwnd` (janela de congestionamento), `ssthresh` (limiar).
**Fases e eventos (Reno):**
1. **Slow start:** `cwnd = 1 MSS`; +1 MSS por ACK ⇒ dobra a cada RTT, até `cwnd ≥ ssthresh`.
2. **Congestion avoidance:** +1 MSS por RTT (linear).
3. **3 ACKs duplicados** (rede ainda entrega algo → congestionamento leve): `ssthresh = cwnd/2`, `cwnd = ssthresh` (**fast recovery**), retransmite o segmento perdido (**fast retransmit**), continua em CA.
4. **Timeout** (grave): `ssthresh = cwnd/2`, `cwnd = 1 MSS`, volta ao slow start.
5. *Tahoe* (mais antigo): qualquer perda → `cwnd = 1`.
**Janela efetiva:** `min(cwnd, rwnd)`. Exemplo numérico: Resumo §8.4.
**Justiça:** AIMD faz conexões que dividem um gargalo convergirem para partes iguais; UDP e conexões paralelas "burlam" isso.

**Resposta para escrever na prova (síntese):** *Fluxo*: evita que o remetente sobrecarregue o buffer do receptor; o receptor anuncia `rwnd = RcvBuffer − dados no buffer` em cada segmento e o remetente mantém bytes não reconhecidos ≤ rwnd; com rwnd=0 manda sondas de 1 byte. *Congestionamento*: evita sobrecarregar a rede; o remetente mantém `cwnd` e `ssthresh`, inicia em slow start (dobra por RTT), passa a congestion avoidance (+1 MSS/RTT) ao atingir ssthresh; em 3 dups corta ssthresh=cwnd/2 e cwnd=ssthresh (Reno); em timeout ssthresh=cwnd/2 e cwnd=1. Envia no máximo min(cwnd, rwnd).
**Erros comuns:** misturar `rwnd` e `cwnd`; dizer que o receptor controla o congestionamento; esquecer que fluxo é fim-a-fim e congestionamento envolve a rede.

---

## A5. Slow start × Congestion avoidance *(Resumo §6.3, §8.4)*

| | **Slow Start (partida lenta)** | **Congestion Avoidance (prevenção)** |
|---|---|---|
| Quando | início da conexão; após **timeout**; enquanto `cwnd < ssthresh` | quando `cwnd ≥ ssthresh` |
| `cwnd` inicial | 1 MSS | o valor ao entrar |
| Regra | +1 MSS **por ACK recebido** | +1 MSS **por RTT** (≈ MSS²/cwnd por ACK) |
| Efeito | **dobra a cada RTT**: 1, 2, 4, 8… (**exponencial**) | cresce 1 por RTT: 8, 9, 10… (**linear**) |
| Objetivo | descobrir rápido a banda disponível | sondar com cuidado perto do limite |
| Por que "lenta"? | porque começa com 1 segmento (crescimento é rápido) | — |

**Raciocínio:** no início não se conhece a capacidade; crescer linearmente levaria muito tempo, então cresce-se exponencialmente. Mas perto do ponto onde houve perda anterior (`ssthresh`) o risco de estourar é alto, então passa-se a crescer devagar (linear). `ssthresh` é atualizado para **metade do `cwnd` no momento da perda**.

**Resposta para escrever na prova:** no slow start o TCP começa com cwnd=1 MSS e aumenta 1 MSS a cada ACK, o que dobra a janela a cada RTT (crescimento exponencial) até cwnd atingir o ssthresh; então entra em congestion avoidance, onde cwnd cresce 1 MSS por RTT (linear), sondando a banda com cuidado. Perda por timeout: ssthresh=cwnd/2, cwnd=1 e volta ao slow start; por 3 dups: cwnd=ssthresh=cwnd/2 e continua em CA.

---

## A6. Bit alternante, Go-Back-N e Repetição Seletiva *(Resumo §4.4, §8.7, §8.8)*

**Contexto.** Queremos entrega confiável sobre canal que corrompe, perde e (às vezes) reordena. Mecanismos: **checksum** (erro de bit), **ACK**, **nº de sequência** (duplicatas/ordem), **timer** (perda), **janela** (desempenho).

### Bit alternante (rdt 3.0, "pare-e-espere")
- Emissor: envia pacote com `seq ∈ {0,1}`, **liga o timer** e **espera** o ACK com o mesmo número.
- ACK correto → desliga timer, alterna o bit, aceita novo dado da aplicação.
- ACK corrompido, ACK do bit errado ou **timeout** → reenvia o mesmo pacote.
- Receptor: pacote esperado → entrega e manda `ACK(seq)`; duplicata (bit trocado) → descarta e reenvia o ACK do último correto; corrompido → ACK do último correto.
- Cenários: perda de pacote (timeout), perda de ACK (retransmissão, receptor descarta a duplicata), timeout prematuro (ACK duplicado ignorado).
- Problema: baixa utilização. `U = (L/R)/(RTT + L/R)`; ex.: 1 Gbps, RTT 30 ms, 1 KB ⇒ ≈ 0,027 %.

### Go-Back-N (GBN) — janela deslizante, ACK cumulativo
- Emissor pode ter até **N** pacotes não confirmados. `base` = mais antigo sem ACK; `nextseqnum` = próximo.
- **Um timer** (do `base`). `ACK(n)` confirma **tudo até n** → `base = n+1`; se há pendentes, reinicia o timer.
- **Timeout:** reenvia **todos** os de `base` até `nextseqnum−1` ("volta N").
- Receptor: só aceita o pacote `expectedseqnum`; qualquer outro é **descartado** e reenvia-se o ACK do último em ordem. **Sem buffer.**
- Prós: simples. Contras: desperdício quando há perdas.

### Repetição Seletiva (SR)
- Janela N também no **receptor**; **ACK individual**; **timer por pacote**; **buffer** no receptor.
- Timeout(n) → reenvia **só n**. ACK(n) → marca n; se n=`base`, desliza até o próximo não confirmado.
- Receptor: pacote em `[rcv_base, rcv_base+N−1]` → ACK(n); se fora de ordem, guarda; se em ordem, entrega (e os consecutivos já guardados) e desliza. Em `[rcv_base−N, rcv_base−1]` → **reenvia ACK(n)** (o ACK anterior pode ter se perdido). Fora disso, ignora.
- Restrição: **N ≤ metade do espaço de numeração** (§8.8).

### Comparação
| | Bit alternante | GBN | SR |
|---|---|---|---|
| Janela (emissor / receptor) | 1 / 1 | N / 1 | N / N |
| ACK | individual | cumulativo | individual |
| Timers | 1 | 1 | 1 por pacote |
| Buffer no receptor | não | não | sim |
| Retransmite | o pacote | janela toda | só o perdido |

**Resposta para escrever na prova:** (use os três parágrafos acima, 3–5 linhas cada, com o exemplo da perda do pacote 2 de §8.7).

---

## A7. O que identifica um processo em outro host *(Resumo §2.2)*
**IP + número de porta.** O IP (32 bits em IPv4) leva o pacote ao **host** certo (camada de rede); a porta (16 bits, 0–65535) leva ao **processo/socket** certo dentro dele (camada de transporte). Só o IP não basta porque um host executa vários serviços ao mesmo tempo. Portas bem conhecidas: HTTP 80, HTTPS 443, DNS 53, SMTP 25, SSH 22, FTP 21.

## A8. TCP × UDP — por que dois protocolos *(Resumo §4, §7)*
- **TCP:** orientado a conexão, confiável, ordenado, controle de fluxo e congestionamento. Para quem **não tolera perda** (Web, e-mail, arquivos).
- **UDP:** sem conexão, sem retransmissão/ordem/controle de taxa, 8 B de cabeçalho. Para quem quer **baixa latência**, **tolera perdas** (VoIP, streaming, jogos), ou faz pouquíssimas trocas (DNS), ou implementa a própria confiabilidade (QUIC).
- Um único protocolo obrigaria todos a pagar o custo do TCP (atraso do handshake, retransmissões que atrasam voz ao vivo, redução de taxa por congestionamento) ou ninguém teria confiabilidade pronta. Ter os dois deixa a aplicação escolher o compromisso.

## A9. Sockets TCP × UDP *(Resumo §3.4, §4.2)*
- **UDP:** `socket → bind(porta) → recvfrom` (recebe dados **e** IP/porta de origem) `→ sendto(origem)`. Um socket só atende todos os clientes; cada datagrama é independente.
- **TCP:** servidor: `socket → bind → listen → accept` (bloqueia; ao chegar um cliente devolve **novo socket** de conexão) `→ recv/send → close`. Cliente: `socket → connect` (dispara o handshake) `→ send/recv → close`.
- Por isso o servidor TCP tem **welcoming socket + um socket por conexão** (n clientes ⇒ **n+1 sockets**, todos na mesma porta do servidor e distinguidos pela quádrupla). O servidor TCP precisa subir **antes**; no UDP o cliente pode subir antes.

---

# PARTE B — Lista de exercícios (revisão): rdt

### Questão 1 — Pesquisar e descrever Bit Alternante, GBN e Repetição Seletiva
**O que testa:** domínio dos mecanismos de rdt e suas diferenças.
**Resposta:** descrição completa em **A6**, incluindo a tabela comparativa. Para estudar, siga a evolução rdt 1.0 → 3.0 (Resumo §4.4): 1.0 canal perfeito → 2.0 erros de bit (checksum + ACK/NAK) → 2.1 ACK/NAK corrompidos (nº de seq 0/1) → 2.2 sem NAK (ACK com nº de seq) → 3.0 perdas (timer) → pipelining (GBN/SR) para melhorar a utilização.
**Erro comum:** descrever GBN com ACKs individuais (são **cumulativos**) ou SR com timer único (é **um por pacote**).

### Questão 2 — Verdadeiro ou Falso (justifique nos dois casos)

#### a) SR: o remetente pode receber ACK de um pacote fora de sua janela? → **VERDADEIRO**
**Raciocínio.** A janela do remetente só anda para frente quando chegam ACKs. ACKs são mensagens que viajam pela rede e podem ser atrasados; além disso o receptor *reenvia* ACK para duplicatas. Logo um ACK velho pode chegar depois que a janela já passou dele.
**Cenário (N = 3).**
1. t0: emissor envia 1, 2, 3. Janela = {1,2,3}.
2. t1: receptor recebe e envia ACK 1, 2, 3 (e desliza sua janela).
3. t2: os ACKs demoram; o **timer estoura**: emissor reenvia 1, 2, 3.
4. t3: o receptor recebe as duplicatas (estão em `[rcv_base−N, rcv_base−1]`) e **reenvia ACK 1, 2, 3** (obrigatório em SR).
5. t4: chegam os ACKs da 1ª rodada → janela do emissor passa para {4,5,6}.
6. t5: chegam os ACKs da 2ª rodada (1, 2, 3): **referem-se a pacotes anteriores à janela** {4,5,6}.
**Resposta:** Verdadeiro; ACKs atrasados/duplicados de retransmissões podem chegar depois que a janela deslizou.

#### b) GBN: idem → **VERDADEIRO**
Mesmo cenário: o receptor GBN reenvia o ACK do último pacote em ordem sempre que recebe duplicatas/pacotes fora de ordem; esses ACKs cumulativos atrasados chegam com número menor que `base` — fora da janela.

#### c) Bit alternante = SR com janelas de tamanho 1? → **VERDADEIRO**
**Raciocínio, ponto a ponto.** Com N = 1 no SR: o emissor envia 1 pacote e espera o ACK **desse** pacote (ACK individual); há 1 timer (um só pacote em voo); timeout reenvia aquele pacote; o receptor aceita apenas o pacote esperado, entrega, ACK; duplicata → reenvia ACK. Numeração: o espaço mínimo exigido é 2N = 2 números → **0 e 1**. É exatamente o rdt 3.0.

#### d) Bit alternante = GBN com janelas de tamanho 1? → **VERDADEIRO**
Com N = 1 no GBN: 1 pacote em voo, 1 timer, ACK cumulativo = ACK do único pacote, timeout reenvia "toda a janela" = 1 pacote; receptor descarta o que não é o esperado e reenvia o último ACK. Numeração: 2^k−1 ≥ N → 1 bit basta. Também é o bit alternante.
**Moral:** com janela 1 as três estratégias coincidem; as diferenças só aparecem com N > 1.

---

# PARTE C — Lista de questões de provas anteriores

### Q1. Objetivo de um protocolo de camada de aplicação
**Testa:** distinguir *aplicação* de *protocolo de aplicação*.
**Resposta:** define **como processos de aplicação** em hosts diferentes **se comunicam**: (i) os **tipos de mensagem** (requisição, resposta); (ii) a **sintaxe** (campos e delimitadores); (iii) a **semântica** (significado dos campos); (iv) as **regras** de quando/como enviar e responder. Usa os serviços da camada de transporte por meio de sockets. Pode ser aberto (RFC: HTTP, SMTP, DNS) ou proprietário. **Exemplo:** a Web é a *aplicação*; HTTP é o *protocolo* dela.
**Estude:** Resumo §2.1–2.3.

### Q2. Objetivo de um protocolo de transporte
**Resposta:** fornecer **comunicação lógica entre processos** (não entre hosts — isso é a camada de rede). No emissor: divide a mensagem em segmentos e passa à rede; no receptor: remonta e entrega ao socket certo (**multiplexação/demultiplexação por portas**). Dependendo do protocolo, acrescenta confiabilidade, ordenação, controle de fluxo e de congestionamento (TCP) ou só detecção de erro e portas (UDP). **Analogia:** Ana e Pedro (transporte) distribuem cartas entre as crianças de cada casa; o correio (rede) leva as cartas entre as casas.
**Estude:** Resumo §4.1.

### Q3. Por que dois protocolos de transporte (TCP e UDP)?
**Resposta completa:** **A8**. Resumo para prova: aplicações têm requisitos opostos. Web/e-mail/arquivos precisam de entrega confiável e ordenada (TCP). VoIP, streaming ao vivo, jogos e DNS preferem baixa latência e toleram perda (UDP), pois retransmitir atrasa e o handshake/controle de congestionamento do TCP são indesejáveis. Dois protocolos permitem escolher.

### Q4. Por que o UDP existe? Não bastava a aplicação mandar pacotes IP direto?
**Raciocínio.** O IP leva o pacote **ao host**, mas não diz **a qual processo** entregar, nem verifica a integridade do dado.
**Resposta:** sem o UDP não haveria **multiplexação/demultiplexação por portas** nem **checksum** de transporte. O UDP acrescenta só isso (8 bytes) e mantém as vantagens: sem handshake (menor atraso), sem estado de conexão (servidor atende mais clientes), sem controle de congestionamento (a aplicação decide a taxa), cabeçalho pequeno. Também permite construir confiabilidade na aplicação (ex.: QUIC).

### Q5. Servidor UDP precisa de uma porta; servidor TCP, de duas. Por quê? E com n conexões?
**Raciocínio.**
- UDP é sem conexão: **um único socket**, identificado por (IP destino, porta destino), recebe de qualquer cliente.
- TCP: o servidor cria um **socket de boas-vindas** (fica em `listen()` na porta conhecida) apenas para *aceitar* pedidos de conexão. Quando chega um cliente, o `accept()` cria um **segundo socket**, dedicado àquele cliente. É daí que vem o "dois".
**Resposta:** UDP: 1. TCP: 2 (boas-vindas + conexão). Com **n** conexões simultâneas de n hosts diferentes: **n + 1** (1 de boas-vindas + n de conexão).
⚠️ **Observação técnica:** no sentido estrito de *número de porta*, todos esses sockets usam a **mesma porta do servidor** (ex.: 80); eles se diferenciam pela quádrupla (IP origem, porta origem, IP destino, porta destino). A pergunta usa "portas" querendo dizer *sockets*; escreva **n+1 sockets** e inclua a observação.
**Erro comum:** responder "2n" ou "n" (esquecendo o socket de boas-vindas).
**Estude:** Resumo §3.4, §4.2; A9.

### Q6. Três aplicações de Internet não proprietárias e seus protocolos
**Resposta:** Web — **HTTP**; correio eletrônico — **SMTP** (envio/transferência entre servidores) e **POP3/IMAP** (leitura); tradução de nomes — **DNS**. Outras válidas: transferência de arquivos — FTP; login remoto seguro — SSH; compartilhamento P2P — BitTorrent; streaming — DASH/HLS; VoIP — SIP/RTP. *Não proprietário* = especificação aberta (RFC) — ao contrário de Skype original/WhatsApp.
**Estude:** Resumo §2.3.

### Q7. Por que, nos protocolos rdt, precisamos de números de sequência e temporizadores?
**Raciocínio.** Cada defeito do canal exige um mecanismo:
- **Pacote/ACK corrompido** → checksum + retransmissão. Mas retransmitir após *ACK* corrompido cria **duplicata** no receptor, que não sabe se é dado novo ou repetido → **nº de sequência** (0/1 já bastam no pare-e-espere; mais números com janelas).
- **Pacote ou ACK perdido** → ninguém avisa nada; o remetente esperaria para sempre → **temporizador**: se o ACK não chega a tempo, retransmite.
**Resposta:** números de sequência permitem ao receptor distinguir dado novo de retransmissão (descartar duplicatas, reordenar); temporizadores permitem ao remetente detectar perda de pacotes/ACKs e retransmitir.
**Estude:** Resumo §4.4.

### Q8. Por que um desenvolvedor escolheria UDP em vez de TCP?
**Resposta:** (1) **sem handshake** → sem atraso de início (transação de 1 RTT); (2) **sem retransmissão**: em voz/vídeo ao vivo um pacote atrasado perde a utilidade e retransmitir só atrapalha; (3) **sem controle de congestionamento** → a aplicação controla sua taxa mínima/constante; (4) **sem estado de conexão** → servidor atende muito mais clientes; (5) **cabeçalho menor** (8 B vs 20+). Exemplos: DNS, VoIP, streaming, jogos, IoT. Se precisar, implementa confiabilidade na própria aplicação.
**Contrapartida:** UDP pode "atropelar" conexões TCP (injustiça) e não garante nada.

### Q9. Num par de processos, quem é cliente e quem é servidor?
**Resposta:** **cliente** = o processo que **toma a iniciativa** de iniciar a comunicação (abre a conexão/envia a primeira mensagem). **Servidor** = o processo que **espera ser contatado**. O papel é por *sessão*, não pela máquina (em P2P o mesmo processo é cliente ao baixar e servidor ao enviar).

### Q10. Que informação um processo usa para identificar outro processo em outro host?
**Resposta:** **A7** — endereço IP do host + número de porta do processo.

### Q11. Como funciona o HTTP? → **A1**
### Q12. Explique o funcionamento do DNS → **A2**

### Q13. Processo no host C com socket UDP porta 5529; A e B enviam segmentos UDP à porta 5529. Mesmo socket? Como C sabe que vêm de hosts diferentes?
**Raciocínio.** O demux de um socket UDP usa só **(IP destino, porta destino)**; os dois segmentos têm o mesmo destino (C:5529).
**Resposta:** **Sim**, ambos vão para o **mesmo socket**. O processo em C distingue os remetentes pelos campos de **origem** do segmento: **IP de origem** (A ou B) e **porta de origem**. Em Python isso aparece no `addr` devolvido por `recvfrom()`, que também serve para responder.
**Contraste TCP:** lá o socket é identificado pela quádrupla, então seriam sockets diferentes.
**Estude:** Resumo §4.2, §8.10.

---

# PARTE D — Prova 1 (20/12/2013)

### 1. (0,5) Informação que identifica um processo em outro hospedeiro → **A7**.

### 2. (1,0) Objetivo de um protocolo de apresentação (handshaking)
**O que testa:** por que protocolos de conexão fazem uma fase inicial.
**Raciocínio.** Antes de trocar dados, os dois lados precisam: saber que o outro existe e quer falar; combinar parâmetros; inicializar estado (números de sequência iniciais, buffers, janelas). Sem isso, pedidos atrasados criam conexões fantasma.
**Resposta:** estabelecer a conexão e **sincronizar o estado** entre cliente e servidor antes da transferência de dados: confirmar que ambos estão ativos e dispostos a comunicar, e combinar/inicializar variáveis (nºs de sequência iniciais, buffers, tamanhos de janela). No TCP é o **handshake de 3 vias** — `SYN` (cliente, seq=x) → `SYN+ACK` (servidor, seq=y, ack=x+1) → `ACK` (cliente, ack=y+1). Com 2 vias haveria conexões meio-abertas e duplicadas por segmentos atrasados; o 3º passo é a prova de "ainda estou aqui". Num protocolo de aplicação como o SMTP, o equivalente é a fase de apresentação (`HELO`).
**Estude:** Resumo §5.7.

### 3. (1,0) HTTP, FTP, SMTP, POP3, IMAP: TCP ou UDP? Por quê?
**Resposta:** todos rodam sobre **TCP**. São aplicações **intolerantes a perda** (uma página, arquivo ou e-mail com bytes faltando é inutilizável), que exigem entrega **ordenada e completa**; são **elásticas** quanto à vazão e **insensíveis a atraso**, então o TCP (confirmações, retransmissão, controle de fluxo/congestionamento) é ideal. Além disso os servidores usam portas conhecidas (80/443, 21, 25, 110, 143) liberadas em firewalls. **Estude:** Resumo §2.3.

### 4. (0,5) HTTP persistente com paralelismo × sem paralelismo; qual o HTTP/1.1 usa?
**Raciocínio.** As duas mantêm a conexão TCP aberta (ao contrário do não persistente). A diferença é *quando* o cliente envia as requisições seguintes.
- **Sem paralelismo (sem pipelining):** nova requisição só **após receber** a resposta anterior → **1 RTT por objeto**.
- **Com paralelismo (pipelining):** o cliente envia as requisições **em sequência, sem esperar** as respostas (assim que acha as referências no HTML) → ~**1 RTT** para todos os objetos.
- Exemplo (HTML + 10 imagens): sem pipelining ≈ 12 RTT; com pipelining ≈ 3 RTT (Resumo §8.6).
**Resposta:** a persistente **com paralelismo (pipelining)** é a usada por padrão no **HTTP/1.1**.
**Observação:** o pipelining tem *HoL blocking* (respostas na ordem das requisições), resolvido no HTTP/2 por multiplexação.

### 5. (1,0) Servidor UDP com uma porta × servidor TCP com duas → **Parte C, Q5** (UDP: 1 socket; TCP: boas-vindas + conexão; n conexões ⇒ n+1).

### 6. (0,5) Por que o servidor TCP deve rodar antes do cliente? E no UDP, o cliente pode rodar antes?
**Raciocínio.** Compare o que cada cliente faz primeiro.
- **TCP:** o cliente executa `connect()`, que envia um `SYN`. Quem responde? O **socket de boas-vindas** do servidor (criado com `bind/listen`). Se o servidor não estiver rodando, ninguém responde o SYN (ou o SO devolve `RST`) → a conexão falha e o cliente recebe erro. Logo o servidor precisa estar **escutando antes**.
- **UDP:** não há conexão nem handshake. O cliente cria o socket e faz `sendto(IP, porta)`; só precisa conhecer o endereço do servidor. Se o servidor ainda não estiver escutando, o datagrama simplesmente é perdido — mas o programa cliente pode ser executado antes sem erro de conexão.
**Estude:** Resumo §3.4, A9.

### 7. (0,5) A→B usa porta origem x e destino y. Portas de B→A?
**Resposta:** origem **y** e destino **x** — as portas se invertem, pois a resposta vai para a porta efêmera do cliente (x) a partir da porta do servidor (y). **Estude:** Resumo §8.1.

### 8. (1,0) Verdadeiro ou falso

**(a) "Os bytes não reconhecidos que A envia não podem exceder o tamanho do buffer de recepção." → VERDADEIRO.**
*Raciocínio:* o controle de fluxo impõe `LastByteSent − LastByteAcked ≤ rwnd`. E `rwnd = RcvBuffer − (dados que já estão no buffer) ≤ RcvBuffer`. Logo, os bytes em voo nunca superam o buffer do receptor.

**(b) "O segmento TCP tem um campo para RcvWindow." → VERDADEIRO.**
É o campo de 16 bits "janela de recepção" (`rwnd`), no cabeçalho, onde o receptor anuncia seu espaço livre (controle de fluxo).

**(c) "Último SampleRTT = 1 s ⇒ TimeoutInterval ≥ 1 s." → VERDADEIRO** (⚠️ ver nota).
*Raciocínio (prova matemática).* Com α = 1/8, β = 1/4. Sejam E e D o EstimatedRTT e DevRTT **antes** da amostra de 1 s.
`E' = 0,875·E + 0,125·1`; `D' = 0,75·D + 0,25·|1 − E|`; `Timeout = E' + 4·D' = E' + 3D + |1 − E|`.
- Se **E ≤ 1**: `Timeout = 0,875E + 0,125 + 3D + 1 − E = 1,125 − 0,125E + 3D ≥ 1,125 − 0,125 = 1`.
- Se **E > 1**: `Timeout = 0,875E + 0,125 + 3D + E − 1 = 1,875E − 0,875 + 3D > 1`.
Nos dois casos ≥ 1 s. (A "intuição": a margem de 4·DevRTT cresce justamente quando a amostra foge da média.)
⚠️ *Nota:* professores às vezes marcam "falso" pensando que o timeout depende de média e desvio, não só da última amostra. Se a sua turma usou essa lógica, justifique assim: "depende do histórico". A conta acima mostra que, com as fórmulas do curso, o resultado é sempre ≥ 1 s.

**(d) "Seq 38 com 4 bytes de dados ⇒ ACK do mesmo segmento é necessariamente 42." → FALSO.**
*Raciocínio:* o campo ACK de um segmento A→B confirma os dados que **B enviou a A** (é o próximo byte esperado *de B*). Não tem relação com `seq + len` do próprio segmento. O **42** é o ACK que **B enviaria** para A ao receber esse segmento (38 + 4).

**(e) "Timeout no remetente ⇒ threshold = metade do seu valor anterior." → FALSO.**
*Raciocínio:* no timeout `ssthresh = cwnd/2` — metade da **janela de congestionamento no momento da perda** — e `cwnd = 1 MSS`. Não é metade do threshold anterior (só coincidiria se cwnd = 2·ssthresh_antigo, o que é acaso).
**Estude:** Resumo §5.4, §5.6, §6.3.

### 9. (1,0) Seq 90 e 110
**a)** `110 − 90 =` **20 bytes** (o seq do 2º é o seq do 1º + tamanho do 1º).
**b)** Primeiro perdido, só o segundo chega: B tem 0 bytes novos em ordem; continua esperando o byte 90 ⇒ **ACK = 90** (ACK duplicado). O segmento 110 fica no buffer de B (ou é descartado, conforme a implementação).
**Estude:** Resumo §5.3, §8.1.

### 10. (1,0) Diferença entre controle de fluxo e de congestionamento; explique os dois em detalhes → **A4**.

### 11. (1,0) Explique: a) bit alternante, b) Go-Back-N, c) Repetição Seletiva → **A6**.

### 12. (1,0) Slow start × Congestion avoidance → **A5**.

---

# PARTE E — Prova oral (25/08/2014)

Perguntas orais: responda em **2–3 min**, com estrutura (definição → mecanismo → exemplo/numérico).

1. **Identificação de processo:** **A7**.
2. **Aplicações sobre TCP ou UDP?** **Prova 2013, Q3** — todas TCP, porque não toleram perda e precisam de ordem/confiabilidade.
3. **Servidor UDP 1 porta × TCP 2:** **Parte C, Q5** (n+1).
4. **Servidor TCP antes do cliente / UDP não:** **Prova 2013, Q6**.
5. **Funcionamento do TCP em linhas gerais:** **A3**. *Roteiro oral:* conexão (3-way) → numeração de bytes/ACK cumulativo → timer e retransmissão (timeout, 3 dups) → fluxo (rwnd) → congestionamento (cwnd) → fechamento (FIN).
6. **Controle de fluxo no TCP:** **A4**, parte "Controle de fluxo em detalhe". *Roteiro:* problema (buffer do receptor) → rwnd = RcvBuffer − dados → vai no cabeçalho → remetente limita bytes em voo → rwnd=0 e sondas de 1 byte.
7. **Controle de congestionamento no TCP:** **A4**, parte "Controle de congestionamento em detalhe". *Roteiro:* problema → sinal (perda) → AIMD/dente de serra → SS, CA, 3 dups (Reno), timeout.
8. **Slow start e congestion avoidance:** **A5**.
9. **HTTP:** **A1**.
10. **DNS:** **A2**.

---

# PARTE F — 2ª avaliação (1º semestre 2015)

### 1. (1,0) 5 aplicações não proprietárias e protocolos
**Resposta:** Web — HTTP; e-mail — SMTP (e POP3/IMAP para leitura); resolução de nomes — DNS; transferência de arquivos — FTP; acesso remoto seguro — SSH. (Também: P2P — BitTorrent; streaming — DASH/HLS; VoIP — SIP/RTP.)

### 2. (1,0) Cliente × servidor → **Parte C, Q9**.
### 3. (1,0) Identificação de processo → **A7**.

### 4. (1,0) Transação de cliente remoto a servidor "o mais rápido possível": UDP ou TCP? Por quê?
**Raciocínio.** Conte os RTTs.
- TCP: 1 RTT só para o handshake (SYN/SYN-ACK) **antes** de enviar o primeiro byte; depois a requisição/resposta (+1 RTT) ⇒ ≥ 2 RTT.
- UDP: envia a requisição **imediatamente** e recebe a resposta ⇒ ~1 RTT.
**Resposta:** **UDP** — não tem handshake, então a transação começa e termina mais rápido. Custo: a aplicação deve lidar com perdas (timeout + reenvio), como faz o DNS.

### 5. (1,0) Servidor Web em C:80 com conexões persistentes; requisições de A e B. Mesmo socket? Ambos têm porta 80?
**Raciocínio.** Servidor TCP: o socket de boas-vindas só aceita; para **cada** cliente o `accept()` cria um socket de conexão. O demux usa a **quádrupla**; A e B têm IP (e porta) de origem diferentes ⇒ sockets diferentes.
**Resposta:**
- **Não** passam pelo mesmo socket: são **dois sockets de conexão distintos**, um por cliente.
- **Sim**, os dois têm a **porta 80** do lado do servidor — o que os diferencia não é a porta, e sim o par (IP/porta origem) do cliente na quádrupla.
- Com conexão **persistente**, todas as requisições de um **mesmo cliente** usam o mesmo socket (no HTTP não persistente seria um socket novo por requisição).

### 6. (1,0) Figura 3.5 (servidor Web B; cliente C com portas 7532 e 26145; cliente A com porta 26145)
**Raciocínio.** Na resposta, **troca** origem e destino do pedido: o servidor responde da sua porta 80 para a porta/IP do cliente que perguntou. As duas conexões com porta de cliente 26145 (C e A) são diferenciadas pelos IPs.
| Segmento de volta | Porta origem | Porta destino | IP origem (datagrama) | IP destino (datagrama) |
|---|---|---|---|---|
| B → C (conexão 1) | 80 | 7532 | B | C |
| B → C (conexão 2) | 80 | 26145 | B | C |
| B → A | 80 | 26145 | B | A |

### 7. (1,0) Verdadeiro ou falso (justifique se for falso)

**a) "B não tem dados para A, portanto B não enviará confirmações" → FALSO.** O ACK não precisa ir "de carona" (*piggybacking*) num segmento de dados. Sem dados para enviar, B manda **segmentos só de ACK** (sem payload): ACK atrasado em até 500 ms, ou um ACK cumulativo para cada 2 segmentos em ordem, ou imediato para fora de ordem.

**b) "O tamanho do rwnd nunca muda" → FALSO.** `rwnd = RcvBuffer − dados no buffer` varia conforme a aplicação lê o buffer (de `RcvBuffer` até 0), e é reanunciado em cada segmento. (Exemplo: Resumo §8.5.)

**c) "Bytes não reconhecidos de A não podem exceder o buffer de recepção" → VERDADEIRO.** Controle de fluxo: `LastByteSent − LastByteAcked ≤ rwnd ≤ RcvBuffer`.

**d) "Último SampleRTT = 1 s ⇒ TimeoutInterval ≥ 1 s" → VERDADEIRO** (⚠️). Demonstração completa na **Prova 2013, Q8(c)**: `Timeout = E' + 3D + |1−E|` e ≥ 1 em ambos os casos E ≤ 1 e E > 1. *Se for esperada resposta "falso", o argumento é "depende de EstimatedRTT e DevRTT", mas matematicamente é ≥ 1.*

**e) "Seq 40 + 4 bytes ⇒ ACK do mesmo segmento é 44" → FALSO.** O ACK do segmento A→B confirma dados de B→A. 44 é o ACK que **B** enviaria de volta (40 + 4).

### 8. (1,0) B recebeu até o byte 126; A envia seg 1 (seq 127, 70 B, porta origem 302, destino 80) e seg 2 (50 B)
**Raciocínio-base:** `próximo seq = seq + tamanho`; `ACK = próximo byte esperado`. (Tabela em Resumo §8.1.)
**a)** Seg 2: **seq = 127 + 70 = 197**; porta origem **302**; porta destino **80** (mesma conexão).
**b)** ACK do 1º (chega antes do 2º): **ACK = 197** (B passa a esperar o byte 197); porta origem **80**; porta destino **302** (inverte).
**c)** Se o 2º chega antes do 1º: B ainda espera o 127 ⇒ **ACK = 127** (duplicado, sinaliza a lacuna).
**d)** Diagrama — chegam em ordem; **1º ACK perdido**; 2º ACK chega **depois** do timeout do 1º segmento:
```
   Host A                                          Host B
     |--- Seq=127, 70 bytes ------------------------>|  B tem até 196 → ACK=197
     |--- Seq=197, 50 bytes ------------------------>|  B tem até 246 → ACK=247
     |      X <----------- ACK=197 -----------------|  (PERDIDO)
  TIMEOUT do seg 1 (ACK=247 ainda a caminho)         |
     |--- Seq=127, 70 bytes  (retransmissão) ------>|
     |<----------------- ACK=247 --------------------|  (o ACK do seg 2 chega; é cumulativo:
     |  A: SendBase=247 → tudo confirmado            |   confirma 127–246, timer cancelado)
     |                                               |  B recebe a duplicata (127–196):
     |<----------------- ACK=247 --------------------|  descarta e reenvia ACK=247
     |  A ignora (ACK duplicado, nada novo)          |
```
**Lista do que desenhar:** segmentos (127, 70 B), (197, 50 B), retransmissão (127, 70 B); ACKs 197 (perdido), 247 e 247 (reação à duplicata). Ideia-chave: **ACK cumulativo** — o ACK 247 "cobre" o ACK 197 perdido.
**Estude:** Resumo §5.3, §5.5, §8.2.

### 9. (2,0) Fluxo × congestionamento do TCP, detalhado → **A4** (com SS/CA em **A5**).
*Dica para valer 2 pontos:* tabela comparativa + fluxo (fórmula do rwnd, sondas) + congestionamento (cwnd, ssthresh, SS, CA, 3 dups, timeout, min(cwnd, rwnd)).

---

# PARTE G — Tarefa: questões TCP

### Q1 — B recebeu até 126; A envia 80 B (seq 127; porta origem 302, destino 80) e 40 B
**a)** Seg 2: **seq = 127 + 80 = 207**; porta origem **302**; destino **80**.
**b)** ACK do 1º (chega antes): **207**; porta origem **80**; destino **302**.
**c)** 2º chega antes do 1º: B continua esperando o byte 127 ⇒ **ACK = 127**. (Esse ACK duplicado é o que dispara o fast retransmit quando se acumulam 3.)
**d)** Diagrama (1º ACK perdido; 2º ACK chega após o timeout do 1º):
```
   Host A                                          Host B
     |--- Seq=127, 80 bytes ------------------------>|  ACK=207
     |--- Seq=207, 40 bytes ------------------------>|  ACK=247
     |      X <----------- ACK=207 -----------------|  (perdido)
  TIMEOUT seg 1                                      |
     |--- Seq=127, 80 bytes (retrans.) ------------->|
     |<----------------- ACK=247 --------------------|  (chega; cumulativo; A: SendBase=247)
     |<----------------- ACK=247 --------------------|  (resposta à duplicata; A ignora)
```
Segmentos: (127, 80 B), (207, 40 B), (127, 80 B); ACKs: 207 (perdido), 247, 247.

### Q2 — Enlace 100 Mbps; A escreve no socket a até 120 Mbps; B lê o buffer a 50 Mbps. Efeito do controle de fluxo?
**Raciocínio, em etapas.**
1. O enlace entrega até 100 Mbps ao TCP de B, mas a aplicação em B só consome 50 Mbps. O excedente se acumula no **buffer de recepção**.
2. `rwnd = RcvBuffer − dados no buffer` vai **diminuindo** e é informado a A nos ACKs.
3. Quando `rwnd` chega a 0, A tem de **parar** (só sondas de 1 byte). Cada vez que B lê dados, `rwnd` sobe e A pode enviar mais.
4. Em regime, A só consegue enviar o equivalente ao que B drena: **≈ 50 Mbps** (e não 100 nem 120).
5. Os 70 Mbps que a aplicação em A tentaria enviar além disso ficam retidos no **buffer de envio** de A, bloqueando o `send()` da aplicação. Sem controle de fluxo o buffer de B estouraria, causando perdas e retransmissões inúteis.
**Resposta:** o controle de fluxo regula A para a velocidade de leitura de B (~50 Mbps); o enlace de 100 Mbps fica subutilizado e a aplicação em A é desacelerada. **Estude:** Resumo §5.6, §8.5.

### Q3 — Verdadeiro/falso com justificativa
Mesmas cinco afirmações da Prova 2013 Q8. Resumo:
1. **V** — `LastByteSent − LastByteAcked ≤ rwnd ≤ RcvBuffer`.
2. **V** — campo `rwnd` de 16 bits no cabeçalho TCP.
3. **V** ⚠️ — demonstração em Prova 2013 Q8(c). (Se considerada falsa: depende do histórico de E e D.)
4. **F** — o ACK do segmento refere-se aos dados na direção oposta; 42 é o ACK de B ao receber esse segmento.
5. **F** — `ssthresh = cwnd/2` (cwnd no instante da perda), não metade do ssthresh anterior; e `cwnd = 1 MSS`.

### Q4 — A envia 3 segmentos seq 1400, 1900, 2000. Quantos dados cada? Qual o ACK de cada?
**Raciocínio.** O tamanho do segmento é a diferença entre o seq dele e o do próximo; o ACK é o seq do próximo byte esperado (o início do segmento seguinte) quando chegam em ordem.
| Segmento | Seq | Bytes | ACK que o reconhece |
|---|---|---|---|
| 1 | 1400 | 1900 − 1400 = **500** | **1900** |
| 2 | 1900 | 2000 − 1900 = **100** | **2000** |
| 3 | 2000 | **não dá para saber** (não há um 4º seq) | **2000 + L** (L = tamanho do 3º) |
Se o 1º se perdesse, o ACK ao receber o 2º ou o 3º seria **1400** (duplicado).

### Q5 — Fluxo × congestionamento, em detalhes, incluindo todas as fases → **A4** + **A5**
"Todas as fases" = slow start → congestion avoidance → (3 dups) fast retransmit/fast recovery → (timeout) volta ao slow start com `cwnd=1`. Cite Tahoe × Reno.

### Q6 — Remetente fica ocioso em t1 e volta em t2. Vantagens/desvantagens de reutilizar cwnd e ssthresh de t1? Alternativa?
**Raciocínio.** `cwnd` e `ssthresh` são "o que o TCP sabia da rede em t1". Depois de um longo silêncio:
- **Vantagem de reutilizar:** se a rede é a mesma, retoma **na hora** a taxa alta, sem passar pelo slow start (mais vazão, menos latência no recomeço).
- **Desvantagem:** a rede pode ter **mudado** (mais tráfego, outro caminho, banda menor); e, como o fluxo de ACKs parou, não há mais "relógio". Enviar de uma vez uma janela grande produz uma **rajada** que pode causar **congestionamento e perdas** (para si e para os outros).
- **Alternativa recomendada:** manter o **`ssthresh`** (memória da capacidade estimada) mas **reiniciar `cwnd` com valor pequeno** (1 MSS ou janela inicial) e fazer slow start até o ssthresh, depois congestion avoidance — "slow-start restart after idle" (RFC 5681/2861). Assim re-sonda a rede com segurança e ainda sobe rápido, pois o slow start é exponencial.

---

# PARTE H — Wireshark Lab: TCP v8.0

O lab usa o trace **`tcp-ethereal-trace-1`** (150 KB de *Alice no País das Maravilhas* enviados por **HTTP POST** a `gaia.cs.umass.edu`). O arquivo não está na pasta; abaixo: **método** (o que olhar no Wireshark e por quê) e **valores do trace padrão**. ⚠️ Os números abaixo são os do trace público conhecido — confirme no seu arquivo (e no seu próprio trace os números serão outros, mas o método é o mesmo).

**Preparação:** filtro `tcp`; para ver segmentos TCP em vez de HTTP, *Analyze → Enabled Protocols* desmarque HTTP. Para ver números absolutos, *Edit → Preferences → Protocols → TCP* desmarque "relative sequence numbers" (por padrão o Wireshark mostra seq **relativo**, 0 = SYN).

| # | Pergunta | Como achar e interpretar | Valor (trace padrão) |
|---|---|---|---|
| 1 | IP e porta do cliente | Selecione um segmento do POST/dados → Internet Protocol (Src) e TCP (Src Port). É a porta **efêmera** do cliente. | **192.168.1.102**, porta **1161** |
| 2 | IP e porta do servidor | Mesmo segmento, campos Destination / Dst Port. Servidor Web = porta 80. | **128.119.245.12**, porta **80** |
| 3 | (seu trace) IP/porta | Idem, no seu arquivo; porta de origem alta (49152–65535 em geral) | — |
| 4 | Seq do SYN e o que o identifica | 1º segmento da conexão. Flags: **SYN = 1, ACK = 0**. Seq = ISN do cliente (relativo 0). | seq **0** |
| 5 | Seq do SYN-ACK, valor do ACK, como foi determinado, identificação | Servidor tem seu próprio ISN (y). `ACK = ISN_cliente + 1` (o servidor confirma "recebi seu SYN, espero o byte x+1"). Flags: **SYN = 1 e ACK = 1**. | seq 0 (relativo), ACK **1** |
| 6 | Seq do segmento com o POST | Procure "POST" no painel de bytes (o 1º segmento de dados). | seq relativo **1** |
| 7 | Seis primeiros segmentos: seq, instantes, RTT, EstimatedRTT | Para cada segmento: `t_envio`; ACK correspondente é o que tem `ack = seq + len`; `RTT = t_ack − t_envio`. `Est₁ = RTT₁`; depois `Est = 0,875·Est + 0,125·RTT`. Gráfico: *Statistics → TCP Stream Graph → Round Trip Time*. | seqs **1, 566, 2026, 3486, 4946, 6406**; RTT ≈ 0,0275 · 0,0356 · 0,0701 · 0,1144 · 0,1399 · 0,1896 s; Est ≈ 0,0275 · 0,0285 · 0,0337 · 0,0438 · 0,0558 · 0,0725 s |
| 8 | Tamanho dos 6 primeiros segmentos | Campo *TCP Segment Len*. O 1º contém o cabeçalho HTTP do POST (menor); os demais enchem o MSS (1460 = 1500 de MTU Ethernet − 40 de cabeçalhos IP+TCP). | **565**, 1460, 1460, 1460, 1460, 1460 B |
| 9 | Menor `rwnd` anunciado; o receptor limita o remetente? | Veja o campo *Window size* nos segmentos **vindos do servidor**; o mínimo costuma estar no 1º ACK. Se a janela anunciada é sempre maior que os bytes em voo, o controle de fluxo não freia. | mínimo **5840 B**; **não** limita (a janela cresce) |
| 10 | Há retransmissões? | No gráfico Time-Sequence (Stevens) uma retransmissão aparece como seq que **volta** no tempo; ou use o filtro `tcp.analysis.retransmission`; ou compare seq no tempo — se cresce sempre, não há. | **não há** |
| 11 | Quanto o receptor reconhece por ACK? ACK a cada dois segmentos? | Diferença entre ACKs consecutivos: 1460 B é um segmento; **2920 B** (2×1460) indica um ACK para dois segmentos — ACK atrasado (Tabela 3.2 do livro). | tipicamente 1460; há casos de 2920 |
| 12 | Vazão da conexão | `vazão = bytes transferidos / tempo`. Bytes = (seq do último ACK) − (seq do 1º byte); tempo = t(último ACK) − t(1º segmento). | ≈ 164 KB ÷ ≈ 5,5 s ≈ **30 KB/s** (≈ 0,24 Mbps) |
| 13 | Slow start × congestion avoidance no gráfico Stevens | **Slow start:** no início, a quantidade de segmentos por *rajada* (degrau) dobra a cada RTT → curva convexa (exponencial). **Congestion avoidance:** depois o crescimento é aproximadamente linear (+1 segmento por RTT). Diferenças do ideal: ACKs atrasados fazem o SS crescer menos que 2×; o formato "degraus" é afetado pela taxa do link de acesso; o MSS/segmento nem sempre é cheio; e a fase de CA é irregular/ruidosa; o `ssthresh` não aparece no trace. | SS nos ~primeiros 0,3 s, depois CA |
| 14 | Repetir 7–13 no seu trace | mesmo método | — |

---

# Apêndice — Conferência rápida das contas

- **2015 Q8:** 127+70 = **197**; ACK₁ = 197; 197+50 = **247**; 2º antes do 1º ⇒ **127**.
- **Tarefa TCP Q1:** 127+80 = **207**; 207+40 = **247**.
- **2013 Q9:** 110−90 = **20 B**; ACK = **90**.
- **Tarefa TCP Q4:** **500 B**, **100 B**; ACKs **1900**, **2000**, **2000+L**.
- **Stop-and-wait:** 8 µs ÷ 30,008 ms ≈ **0,027 %**.
- **HTML + 10 imagens:** não persistente **22 RTT**; persistente s/ pipeline **12**; c/ pipeline **3**.
- **Cache:** 0,4·0 + 0,6·2 = **1,2 s**.
