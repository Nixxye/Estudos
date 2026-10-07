# DNS a fundo — do conceito às mensagens, passo a passo

> **Objetivo:** entender o DNS bem o bastante para (1) explicá‑lo em uma prova oral ou escrita, (2) contar mensagens e tempos em exercícios, (3) interpretar registros e mensagens, e (4) saber *por que* cada decisão de projeto foi tomada.
> Fonte principal: slides **A3 s.19–30** + exercícios (**PO14 Q10, LP Q12**). O que vai **além dos slides** está marcado com *(além dos slides)* — serve para você entender melhor, mas não é cobrado.
> Complementos: [Resumo_P1_Redes.md §3.2](Resumo_P1_Redes.md) · [Fluxo_Completo_Rede.md](Fluxo_Completo_Rede.md) (Etapa 2) · [Gabarito_P1_Redes.md A2](Gabarito_P1_Redes.md).

## Índice
1. O problema e a ideia
2. Os nomes: como são estruturados
3. Quem são os servidores (e o que cada um sabe)
4. Registros de recurso (RR): o "conteúdo" do DNS
5. A mensagem DNS (formato e flags)
6. A resolução passo a passo — com o conteúdo de cada mensagem
7. Iterativa × recursiva (a fundo)
8. Cache e TTL (a fundo)
9. DNS sobre qual transporte e por quê
10. Como um domínio entra no DNS (registro e delegação)
11. Aliasing, balanceamento e e‑mail
12. Segurança
13. DNS dentro de outros fluxos (HTTP, SMTP)
14. Ferramentas práticas
15. Exercícios resolvidos
16. Respostas‑modelo para a prova
17. Checklist e armadilhas

---

# 1. O problema e a ideia

Pessoas gostam de nomes (`www.utfpr.edu.br`). Roteadores e o TCP/IP precisam de **endereços IP** (`200.134.18.157` em IPv4, 32 bits; ou `2001:db8:85a3::8a2e:370:7334` em IPv6, 128 bits). O **DNS (Domain Name System)** é o serviço que **traduz nome ↔ IP**.

Duas visões do mesmo sistema:
- **Para o usuário:** uma **tabela telefônica** de nomes e endereços.
- **Para a engenharia:** um **banco de dados distribuído e hierárquico**, implementado por muitos servidores, que usa um **protocolo de camada de aplicação** (mensagens sobre **UDP, porta 53**) para consultas.

> **Importante:** o DNS é um serviço **da camada de aplicação**, usado por *outras* aplicações (navegador, e‑mail…), mas **não** é usado diretamente pelo usuário. Ele roda nas "bordas" (nos hosts e servidores), nunca nos roteadores.

## 1.1 Serviços que o DNS oferece
| Serviço | O que é | Registro usado |
|---|---|---|
| **Tradução nome → IP** | o básico | A (e AAAA para IPv6) |
| **Host aliasing** | um host tem um **nome canônico** e vários **apelidos** | CNAME |
| **Mail server aliasing** | descobrir qual servidor recebe o e‑mail do domínio | MX |
| **Distribuição de carga** | um nome → **vários IPs** (os servidores respondem em rodízio) | vários A |
| **Suporte à segurança de e‑mail** | guarda SPF/DKIM | TXT |

## 1.2 Por que **não** um servidor único?
Um servidor central seria catastrófico:
1. **Ponto único de falha** — se cai, a Internet "some".
2. **Volume de tráfego** — bilhões de consultas simultâneas.
3. **Latência** — um servidor em outro continente seria lento para a maioria.
4. **Manutenção** — impossível manter bilhões de registros num só lugar.
**Solução:** *distribuir* (muitos servidores) e organizar em *hierarquia* (cada um cuida de uma parte e sabe indicar quem cuida do resto).

---

# 2. Os nomes: como são estruturados

Um nome DNS é lido **da direita para a esquerda**, do mais genérico para o mais específico:

```
www . utfpr . edu . br .
 │      │      │     │   └─ raiz (o ponto final, normalmente omitido)
 │      │      │     └───── TLD (top-level domain): .br
 │      │      └─────────── domínio de 2º nível: edu (dentro de .br)
 │      └────────────────── domínio da organização: utfpr
 └───────────────────────── host (nome da máquina/serviço): www
```
- Cada pedaço entre pontos é um **rótulo (label)**.
- O nome completo, com ponto final, é o **FQDN** (*fully qualified domain name*).
- A **árvore** do DNS tem a **raiz** no topo, **TLDs** abaixo, e assim por diante. Cada nó é gerido pela entidade que "possui" aquele pedaço do nome.

**TLDs:** genéricos (`.com`, `.net`, `.org`, `.edu`, `.gov`) e de país (`.br`, `.ar`, `.jp`). No Brasil o **Registro.br** opera o `.br`.

> **Domínio × zona** *(além dos slides)*: **domínio** é um ramo da árvore (ex.: tudo sob `utfpr.edu.br`). **Zona** é a parte desse ramo que **um conjunto de servidores administra diretamente**; a organização pode **delegar** sub‑ramos (`ppgca.utfpr.edu.br`) a outros servidores. É assim que a administração se distribui.

---

# 3. Quem são os servidores (e o que cada um sabe)

## 3.1 O quadro geral
```
                     ┌─────────────┐
                     │ Servidores  │   sabem: quem cuida de cada TLD
                     │    RAIZ     │   (13 identificadores A–M, anycast, >1600 instâncias)
                     └──────┬──────┘
         ┌───────────┬──────┴──────┬───────────┐
   ┌─────┴─────┐ ┌───┴─────┐ ┌─────┴────┐        sabem: quem cuida de cada domínio
   │ TLD .com  │ │ TLD .br │ │ TLD .org │        abaixo deles (ex.: utfpr.edu.br)
   └─────┬─────┘ └────┬────┘ └──────────┘
         │       ┌────┴─────────────┐
         │  ┌────┴────────┐  ┌──────┴───────┐
         │  │ AUTORITATIVO│  │ AUTORITATIVO │   sabem: o mapeamento REAL
         │  │ utfpr.edu.br│  │ outro.com.br │   (nome → IP) das máquinas da organização
         │  └─────────────┘  └──────────────┘
         └─ AUTORITATIVO amazon.com
```
Mais **fora da hierarquia**: o **servidor DNS local**.

## 3.2 Cada papel
| Servidor | O que sabe / faz | Como responde ao DNS local |
|---|---|---|
| **Raiz** | só indica o **TLD** certo (`.br`, `.com`…) | "Pergunte aos servidores do TLD `.br`" (**referência**) |
| **TLD** | só indica o **autoritativo** da organização | "Pergunte aos servidores de `utfpr.edu.br`" (**referência**) |
| **Autoritativo** | tem os **registros reais** do domínio (A, MX, CNAME…); a organização o administra (ou terceiriza: AWS Route 53, Cloudflare) | **A resposta final** (ex.: o IP), com a flag **AA** |
| **DNS local** (do ISP, campus, empresa; também chamado *resolvedor recursivo*/*default name server*) | **não** pertence à hierarquia oficial; recebe a pergunta do host, **consulta a hierarquia por ele**, guarda em **cache** e devolve a resposta | responde ao host |

**Raiz — detalhe dos slides:** são **13 identificadores lógicos** (letras A a M), mas cada um é uma **rede anycast** com mais de 1600 instâncias físicas. Se uma instância cai ou sofre DDoS, o roteamento (**BGP**) leva o tráfego automaticamente à próxima mais próxima — **resiliência**.

**DNS local:** normalmente o endereço dele chega ao seu dispositivo **automaticamente por DHCP** quando você entra na rede. Você pode também configurar manualmente (ex.: 8.8.8.8 do Google, 1.1.1.1 da Cloudflare).

## 3.3 Quem é *cliente* e quem é *servidor* aqui?
- O **navegador** (via o *resolvedor* do sistema operacional) é **cliente** do DNS local.
- O **DNS local** é **servidor** para o host e **cliente** da raiz, TLD e autoritativo.
- (Lembrete: cliente = quem inicia.)

---

# 4. Registros de recurso (RR): o "conteúdo" do DNS

Cada fato guardado no DNS é um **Resource Record** com quatro campos:

```
( Name , Value , Type , TTL )
```
O significado de `Name` e `Value` **depende do `Type`**. Os tipos dos slides:

| Type | Name | Value | Para quê | Exemplo |
|---|---|---|---|---|
| **A** | hostname | **endereço IPv4** | mapeamento nome → IP | `(www.utfpr.edu.br, 200.134.18.157, A, 86400)` |
| **NS** | **domínio** | **hostname do servidor autoritativo** desse domínio | **delegação** ("quem manda neste domínio") | `(utfpr.edu.br, dns1.utfpr.edu.br, NS, 86400)` |
| **CNAME** | **apelido** (alias) | **nome canônico** (real) | um nome aponta para outro | `(www.utfpr.edu.br, portal.utfpr.edu.br, CNAME, 3600)` |
| **MX** | domínio | **nome do servidor de e‑mail** do domínio | para onde entregar e‑mail `@dominio` | `(utfpr.edu.br, mail.utfpr.edu.br, MX, 86400)` |
| **TXT** | domínio | texto livre | **SPF/DKIM** (segurança de e‑mail) | `(utfpr.edu.br, "v=spf1 ip4:200.134.0.0/16 -all", TXT, 3600)` |

*(além dos slides)*: **AAAA** (nome → IPv6), **SOA** (dados administrativos da zona), **PTR** (IP → nome, "DNS reverso"). O MX real tem também uma **preferência** (número menor = preferido).

## 4.1 Por que a NS aponta para um *hostname* e não para um IP? (a "dependência circular")
Se o NS de `utfpr.edu.br` for `dns1.utfpr.edu.br`, para achar o IP de `dns1.utfpr.edu.br` seria preciso perguntar a… `utfpr.edu.br` — um círculo! A solução (slide 30): o **TLD também guarda o registro A do servidor autoritativo** (`(dns1.utfpr.edu.br, 200.x.x.x, A)`) — chamado de **glue record** *(termo além dos slides)*. Assim, a referência que o TLD devolve já inclui o **IP** do próximo servidor, quebrando o círculo.

## 4.2 CNAME na prática
`www.utfpr.edu.br` pode ser **apelido** de `portal.utfpr.edu.br`. O resolvedor, ao ver o CNAME, faz **mais uma resolução** para o nome canônico até chegar a um **A**. Vantagem: a organização pode **trocar o IP/servidor** sem mudar o nome que o usuário conhece.

## 4.3 Um "arquivo de zona" simplificado (visualização)
```
; zona utfpr.edu.br  (no servidor autoritativo)
utfpr.edu.br.        86400  NS     dns1.utfpr.edu.br.
utfpr.edu.br.        86400  NS     dns2.utfpr.edu.br.
dns1.utfpr.edu.br.   86400  A      200.134.0.10
portal.utfpr.edu.br. 86400  A      200.134.18.157
www.utfpr.edu.br.     3600  CNAME  portal.utfpr.edu.br.
utfpr.edu.br.        86400  MX     mail.utfpr.edu.br.
utfpr.edu.br.         3600  TXT    "v=spf1 ... -all"
```

---

# 5. A mensagem DNS (formato e flags)

Consulta e resposta usam **o mesmo formato** (simplicidade). Roda sobre **UDP/53**.

```
 0                    15 16                   31
┌──────────────────────┬────────────────────────┐
│  Identificação (ID)  │  Flags                 │  ← cabeçalho: 12 bytes
├──────────────────────┼────────────────────────┤
│ Nº de perguntas      │ Nº de respostas        │
├──────────────────────┼────────────────────────┤
│ Nº de RRs autoridade │ Nº de RRs adicionais   │
├──────────────────────┴────────────────────────┤
│ Seção de QUESTÕES  (Nome, Tipo, Classe)       │ ← o que se pergunta
├───────────────────────────────────────────────┤
│ Seção de RESPOSTAS (RRs)                      │ ← respostas à pergunta
├───────────────────────────────────────────────┤
│ Seção de AUTORIDADE (RRs)                     │ ← servidores autoritativos / referências (NS)
├───────────────────────────────────────────────┤
│ Seção de INFORMAÇÕES ADICIONAIS (RRs)         │ ← ajuda extra (ex.: IP do servidor citado em NS)
└───────────────────────────────────────────────┘
```

## 5.1 Campos
- **ID (16 bits):** um número escolhido pelo **cliente** e **copiado na resposta**. É assim que o cliente **casa a resposta com a pergunta** (várias consultas ao mesmo tempo sobre UDP, sem conexão!).
- **Contadores:** quantos RRs há em cada uma das 4 seções.
- **Flags (16 bits)** — as importantes dos slides:
  | Flag | Significado |
  |---|---|
  | **QR** | 0 = **consulta**, 1 = **resposta** |
  | **AA** | 1 = a resposta veio de um servidor **autoritativo** |
  | **RD** | **recursão desejada** (o cliente pede que o servidor resolva por ele) |
  | **RA** | **recursão disponível** (o servidor diz que oferece recursão) |
  *(além dos slides)*: **TC** (resposta truncada → refazer por TCP), **RCODE** (código de resposta: 0 sem erro, **3 = NXDOMAIN**, nome não existe).

## 5.2 O que vai em cada seção (por que existem 4)
- **Questões:** repete a pergunta (nome, tipo `A`/`MX`…, classe `IN`).
- **Respostas:** os RRs que **respondem** à pergunta (ex.: o registro A).
- **Autoridade:** os RRs que dizem **quais servidores são autoritativos** (NS) — usada em **referências**: "não sei, pergunte a estes".
- **Adicionais:** informações úteis que o servidor já sabe e que **economizam outra consulta** (ex.: o registro A dos servidores citados nos NS — o "glue").

---

# 6. A resolução passo a passo — com o conteúdo de cada mensagem

**Cenário:** o notebook (`10.0.0.5`) quer o IP de `www.utfpr.edu.br`. O DNS local é `10.0.0.2`. **Cache totalmente vazio.**

```
Notebook ──(1)──► DNS local ──(2)──► RAIZ
                       ▲  ◄──(3)────┘
                       │──(4)──► TLD .br
                       │  ◄──(5)────┘
                       │──(6)──► AUTORITATIVO (utfpr.edu.br)
                       │  ◄──(7)────┘
Notebook ◄──(8)── DNS local
```

| # | De → Para | Tipo | Conteúdo |
|---|---|---|---|
| **1** | Notebook → DNS local | consulta **recursiva** | `QR=0, RD=1`; Questão: `www.utfpr.edu.br, tipo A` |
| **2** | DNS local → Raiz | consulta (iterativa) | `QR=0`; Questão: `www.utfpr.edu.br, A` |
| **3** | Raiz → DNS local | **referência** | `QR=1`; Resposta: *vazia*; **Autoridade:** `NS` dos servidores do TLD `.br`; **Adicionais:** os `A` desses servidores |
| **4** | DNS local → TLD `.br` | consulta | mesma questão |
| **5** | TLD `.br` → DNS local | **referência** | **Autoridade:** `NS` de `utfpr.edu.br` (`dns1.utfpr.edu.br`); **Adicionais:** `A` de `dns1.utfpr.edu.br` (glue) |
| **6** | DNS local → Autoritativo | consulta | mesma questão |
| **7** | Autoritativo → DNS local | **resposta final** | `QR=1, **AA=1**`; **Resposta:** `(www.utfpr.edu.br, 200.134.18.157, A, TTL)` |
| **8** | DNS local → Notebook | resposta | `QR=1, RD=1, **RA=1**, AA=0` (DNS local não é autoritativo!); **Resposta:** o mesmo A |

**Pontos para guardar**
- O **ID** da mensagem 1 volta na 8. Nas 2–7 o DNS local usa **IDs próprios** nas suas consultas.
- As **referências** (3 e 5) não trazem a resposta; trazem **quem perguntar em seguida**.
- A resposta **8** vem com **AA=0** (resposta de **cache/recursiva**, não autoritativa); só a **7** tem **AA=1**.
- **8 mensagens** com cache vazio. O host só **fala com o DNS local** (mensagens 1 e 8); o resto acontece **entre o DNS local e a hierarquia**.
- No mundo real *(além dos slides)* pode haver **mais um nível** (ex.: `.br` → `edu.br` → `utfpr.edu.br`), com mais uma referência. Os slides simplificam em 3 níveis.

## 6.1 Resolução com CNAME
Se `www.utfpr.edu.br` é **CNAME** de `portal.utfpr.edu.br`: o autoritativo responde com `CNAME` (e, frequentemente, já com o `A` do canônico, se for da mesma zona). Se o canônico estiver **em outro domínio**, o DNS local precisa **reiniciar** a resolução para o novo nome (mais mensagens).

## 6.2 Resolução para e‑mail (MX)
Para entregar e‑mail para `bob@utfpr.edu.br`, o servidor de e‑mail da Alice pergunta **tipo MX** de `utfpr.edu.br` → recebe `mail.utfpr.edu.br` → pergunta **tipo A** de `mail.utfpr.edu.br` → só então abre a conexão **SMTP (TCP 25)** com esse IP.

---

# 7. Iterativa × recursiva (a fundo)

A diferença é **quem faz o trabalho de percorrer a hierarquia**.

## 7.1 Consulta **iterativa**
O servidor consultado **não resolve**: devolve uma **referência** ("não sei, mas pergunte a X"). Quem recebe a referência **faz a próxima pergunta**.
```
DNS local ──► Raiz        "quem é www.utfpr.edu.br?"
DNS local ◄── Raiz        "não sei; pergunte ao TLD .br (IP ...)"
DNS local ──► TLD .br     ...
DNS local ◄── TLD .br     "não sei; pergunte ao autoritativo (IP ...)"
DNS local ──► Autoritativo
DNS local ◄── Autoritativo "É 200.134.18.157"
```
**Quem trabalha?** O **DNS local**. Os servidores de topo "apenas indicam o caminho" → **pouco processamento global**.

## 7.2 Consulta **recursiva**
O servidor consultado **assume a missão** de achar a resposta e age como **cliente do próximo nível**.
```
Host ──1──► DNS local ──2──► Raiz ──3──► TLD ──4──► Autoritativo
Host ◄──8── DNS local ◄──7── Raiz ◄──6── TLD ◄──5── Autoritativo
```
- **Vantagem:** o cliente faz **uma única pergunta simples**.
- **Desvantagem:** transfere a carga de processamento para o **topo da árvore** e facilita **DDoS** — **por isso a maioria dos servidores raiz e TLD desativa a recursão**.

## 7.3 Como se combinam no mundo real
- **Host → DNS local:** **recursiva** (flag `RD=1`) — o host quer a resposta pronta.
- **DNS local → raiz/TLD/autoritativo:** **iterativa** — o DNS local faz o trabalho.
- É o caso normal e o que a prova espera. Teoricamente todas poderiam ser recursivas (a slide 26 mostra), mas na prática não são.

## 7.4 Tabela comparativa
| | Iterativa | Recursiva |
|---|---|---|
| Resposta do servidor | **referência** ao próximo | **resposta final** |
| Quem percorre a hierarquia | o **solicitante** | o **servidor consultado** |
| Carga no topo | **baixa** | **alta** |
| Risco | — | DDoS / sobrecarga |
| Onde se usa | DNS local ↔ hierarquia | host ↔ DNS local |
| Flag | `RD=0` (nas consultas à hierarquia) | `RD=1` (do host) e `RA=1` (resposta) |

---

# 8. Cache e TTL (a fundo)

## 8.1 Ideia
Cada vez que o DNS local descobre algo, **guarda a resposta** por um tempo. Consultas futuras são respondidas **na hora**, sem tocar a hierarquia. "O cache é o herói da performance."

## 8.2 O que se guarda
- O **registro A** final (`www.utfpr.edu.br → IP`).
- Também as **referências** aprendidas: o **NS do TLD `.br`** e o **NS de `utfpr.edu.br`** — assim, uma consulta a **outro** nome do mesmo domínio **pula a raiz e o TLD**.
- *(além dos slides)*: respostas **negativas** ("o nome não existe", NXDOMAIN) também podem ser guardadas.

## 8.3 TTL (Time To Live)
- Valor, em **segundos**, definido pelo **dono do domínio** no registro (ex.: `86400` = 1 dia; `3600` = 1 hora).
- Enquanto o TTL não expira, o cache pode usar a entrada; **expirou → descartada** → próxima consulta refaz a busca.
- **Trade‑off do TTL:** **longo** = menos carga, mas mudanças de IP demoram a propagar (clientes veem o IP antigo); **curto** = mudanças rápidas, mas mais consultas e mais latência.
- Em um mesmo cache podem coexistir TTLs diferentes: o do **A** (curto) e o dos **NS** (longo).

## 8.4 O que o cache faz com o número de mensagens
| Estado do cache do DNS local | Mensagens necessárias | Quem é consultado |
|---|---|---|
| **A do nome em cache** (TTL válido) | **2** (host↔local) | ninguém na hierarquia |
| Sem o A, mas **NS do autoritativo em cache** | 2 + **2** (local↔autoritativo) = **4** | só o autoritativo |
| Sem A e sem NS do autoritativo, mas **NS do TLD `.br` em cache** | 2 + 2 + 2 = **6** | TLD → autoritativo |
| **Cache vazio** | 2 + 2 + 2 + 2 = **8** | raiz → TLD → autoritativo |

*(Cada "par" = 1 pergunta + 1 resposta.)*

## 8.5 O cache do próprio host
O sistema operacional também guarda respostas recentes (cache do resolvedor local). No Windows: `ipconfig /displaydns` (ver) e `ipconfig /flushdns` (limpar); no macOS: `sudo dscacheutil -cachedump`.

---

# 9. DNS sobre qual transporte e por quê

- **UDP, porta 53** (nos slides). Motivos:
  - A troca é **curta**: **1 pergunta + 1 resposta**, cabem em 1 datagrama cada.
  - **Sem handshake** → **1 RTT** por consulta (com TCP seriam 2).
  - **Servidores atendem milhões de clientes**: sem estado de conexão.
- **Confiabilidade?** O UDP não garante nada, então **o próprio cliente resolve**: se a resposta não chega, **reenvia por timeout**; o **ID** casa respostas com perguntas (e permite ignorar respostas duplicadas/atrasadas).
- *(além dos slides)*: se a resposta for grande demais, o servidor marca a flag **TC** (truncada) e o cliente **refaz a consulta por TCP**; **transferências de zona** entre servidores também usam TCP.
- Mensagens DNS **não** passam por HTTP.

---

# 10. Como um domínio entra no DNS (registro e delegação)

Para colocar `utfpr.edu.br` no ar (slide 30):
1. **Passo 1 — Registro:** você contrata/registra o nome numa entidade **registradora** (ex.: **Registro.br**), informando o **nome e o IP** dos seus servidores autoritativos (**primário e secundário**).
2. **Passo 2 — Inserção no TLD:** o registrador insere no **servidor TLD (`.br`)** os RRs de **delegação**:
   ```
   (utfpr.edu.br,      dns1.utfpr.edu.br, NS, 86400)
   (dns1.utfpr.edu.br, 200.x.x.x,         A,  86400)    ← o "glue" que quebra a dependência circular
   ```
3. **Passo 3 — Configuração local:** no **seu** servidor autoritativo você cria os **mapeamentos finais**:
   ```
   (www.utfpr.edu.br, 200.y.y.y,        A,  86400)
   (utfpr.edu.br,     mail.utfpr.edu.br, MX, 86400)
   ```
**Resultado:** o TLD **aponta** para o seu servidor (delegação); o seu servidor **guarda** o IP real. Essa é a cadeia que a resolução percorre.
**"Propagação":** depois de mudar um registro, os caches pelo mundo só enxergam o novo valor **quando o TTL antigo expira**.
*(além dos slides)*: empresas podem **terceirizar** os autoritativos (AWS Route 53, Cloudflare).

---

# 11. Aliasing, balanceamento e e‑mail

## 11.1 Distribuição de carga (round‑robin)
Um nome mapeado para **vários IPs**:
```
google.com → 1.1.1.1 ; 1.1.1.2 ; 1.1.1.3
```
O servidor autoritativo devolve a **lista** e **gira a ordem** a cada consulta. Clientes diferentes tendem a usar IPs diferentes → o tráfego se distribui entre réplicas.

## 11.2 Host aliasing
`www` é só um apelido (CNAME) para o nome real. Permite trocar a máquina sem alterar o nome divulgado.

## 11.3 Mail server aliasing
O endereço `bob@utfpr.edu.br` não diz em qual máquina está o e‑mail; o **MX** do domínio aponta o servidor. O servidor da Alice: **MX → A → SMTP/TCP 25**.

---

# 12. Segurança

- **DNS poisoning (envenenamento de cache):** o atacante faz o DNS local **guardar um registro falso** (ex.: `banco.com → IP do atacante`). Todos os usuários desse DNS local vão ao site falso até o TTL expirar. Dificuldade para o atacante: acertar o **ID de 16 bits** da consulta *(além dos slides: contramedidas — aleatorizar porta de origem, DNSSEC com assinaturas)*.
- **DDoS contra raiz/TLD:** por isso existe **anycast** (resiliência) e a **desativação da recursão** nos servidores de topo.
- **Spoofing de e‑mail e DNS como solução:** o servidor de destino consulta registros **TXT** no DNS: **SPF** (quais IPs podem enviar por aquele domínio), **DKIM** (chave pública para validar a assinatura do e‑mail), **DMARC** (política: *none/quarantine/reject*). Aqui o DNS é a **infraestrutura pública de verificação**.
- **Privacidade** *(além dos slides)*: o DNS comum viaja em **texto claro** — quem observa a rede vê quais nomes você consulta.

---

# 13. DNS dentro de outros fluxos

## 13.1 Abrindo um site (HTTP)
`DNS → TCP (1 RTT) → HTTP GET (1 RTT) → resposta`.
**Fórmula clássica:** se para resolver o nome o DNS local visita servidores com RTTs `RTT₁ … RTTₙ`, e o servidor web está a `RTT₀`:
```
Tempo até o objeto base = RTT₁ + RTT₂ + … + RTTₙ   (DNS)
                         + RTT₀                     (handshake TCP)
                         + RTT₀ + T_trans           (GET e resposta)
                         = ΣRTTᵢ + 2·RTT₀ + T_trans
```
(Com um nº de objetos adicionais, soma‑se conforme o modo HTTP: não persistente → +2·RTT₀ por objeto; persistente sem pipelining → +RTT₀ por objeto; com pipelining → ≈ +RTT₀ no total.)

## 13.2 E‑mail (SMTP)
Já descrito em § 6.2: **MX → A → SMTP**.

## 13.3 Todo cliente de aplicação
Qualquer programa que usa um **nome** (`connect("www.site.com", 80)`) chama o **resolvedor** do sistema, que faz a consulta ao DNS local **antes** de abrir o socket.

---

# 14. Ferramentas práticas

```bash
# Consulta simples (tipo A por padrão)
nslookup www.utfpr.edu.br
# Escolhendo o tipo
nslookup -type=MX utfpr.edu.br
nslookup -type=NS utfpr.edu.br
nslookup -type=CNAME www.utfpr.edu.br
# Mais detalhado
dig www.utfpr.edu.br           # mostra as seções, flags (qr, rd, ra, aa) e TTL
dig +trace www.utfpr.edu.br    # mostra a descida raiz → TLD → autoritativo
# Cache do host (Windows)
ipconfig /displaydns
ipconfig /flushdns
```
Em `dig` procure: `flags: qr rd ra` (resposta recursiva do DNS local, **sem `aa`**), `;; ANSWER SECTION:` (os RRs com TTL), `;; AUTHORITY SECTION:` (NS) e `;; ADDITIONAL SECTION:` (glue). No `dig +trace` cada bloco é uma **referência**.

---

# 15. Exercícios resolvidos

**E1. Contar mensagens.** Cache vazio, DNS local obtém o IP de `www.utfpr.edu.br`. Quantas mensagens no total (inclusive host)?
**R:** 8 (host→local; local→raiz; raiz→local; local→TLD; TLD→local; local→autoritativo; autoritativo→local; local→host). Só 2 envolvem o host.

**E2. Mesmo caso, tudo recursivo.** Quantas mensagens?
**R:** também 8 (4 pedidos descendo + 4 respostas subindo), mas com padrão diferente: host→local→raiz→TLD→autoritativo e volta. A diferença é **quem trabalha** (o topo da árvore).

**E3. Cache.** Logo depois, outro host do campus pede `www.utfpr.edu.br`.
**R:** **2** mensagens (o A está em cache, TTL válido).

**E4. Cache parcial.** Passado o TTL do A, mas o NS do autoritativo ainda está em cache (TTL maior): o host pede `www.utfpr.edu.br`.
**R:** **4** mensagens: host→local, local→autoritativo, autoritativo→local, local→host (não passa por raiz nem TLD).

**E5. Tempo (Kurose).** Um usuário clica numa URL; o DNS local contacta 3 servidores com RTTs de 20, 30 e 50 ms; o servidor web tem RTT₀ = 40 ms; T_trans desprezível; HTML sem objetos.
**R:** DNS = 20+30+50 = 100 ms (⚠️ mais o RTT host↔DNS local, se pedido); TCP = 40 ms; GET = 40 ms ⇒ **180 ms**.
**E5b.** Mesma página com **8 imagens**, HTTP não persistente sequencial: + 8 × 2 × 40 = 640 ⇒ **820 ms**. Persistente com pipelining: + 40 ⇒ **220 ms**. (O DNS só ocorre uma vez se o servidor das imagens é o mesmo, por causa do cache.)

**E6. Interpretar registros.** Dados: `(utfpr.edu.br, mail.utfpr.edu.br, MX)`, `(mail.utfpr.edu.br, 200.134.5.5, A)`, `(www.utfpr.edu.br, portal.utfpr.edu.br, CNAME)`, `(portal.utfpr.edu.br, 200.134.18.157, A)`.
- Para enviar e‑mail a `bob@utfpr.edu.br`: MX → `mail.utfpr.edu.br` → A → **200.134.5.5** → SMTP/TCP 25.
- Para abrir `www.utfpr.edu.br`: CNAME → `portal.utfpr.edu.br` → A → **200.134.18.157**.

**E7. Flags.** Uma resposta com `QR=1, AA=1` vem de…? **R:** de um servidor **autoritativo**. E `QR=1, RD=1, RA=1, AA=0` vem de… **R:** de um **DNS local recursivo** (resposta de cache ou obtida em nome do cliente).

**E8. TTL.** A tem TTL de 600 s; às 10:00 o DNS local resolve e guarda. Às 10:05 outro host pergunta. Às 10:15 outro.
**R:** 10:05 → **cache** (2 mensagens); 10:15 → **expirou** (TTL 600 s = 10 min) → refaz a busca (4–8 mensagens, conforme o cache de NS).

**E9. Por que UDP?** **R:** troca curta de uma pergunta/uma resposta; sem handshake (menor latência); sem estado; confiabilidade resolvida por **timeout e reenvio** do cliente.

**E10. Para que serve o ID?** **R:** o cliente envia várias consultas por UDP (sem conexão); o ID de 16 bits casa cada resposta com sua pergunta.

---

# 16. Respostas‑modelo para a prova

## 16.1 "Explique o funcionamento do DNS." (PO14 Q10 · LP Q12)
> O DNS traduz nomes de host em endereços IP (e oferece aliasing de hosts e de servidores de e‑mail, e distribuição de carga). É um banco de dados distribuído e hierárquico: **servidores raiz**, que indicam os **servidores TLD** (.com, .br…), que indicam os **servidores autoritativos** de cada organização, que guardam os mapeamentos reais. Além disso, cada provedor/campus tem um **servidor DNS local**, que recebe a consulta do host (consulta **recursiva**) e, se não tiver a resposta em cache, consulta de forma **iterativa** a raiz, o TLD e o autoritativo, até obter o IP; devolve‑o ao host e o guarda em **cache** por um tempo **TTL**. As informações ficam em **registros de recurso** (Nome, Valor, Tipo, TTL): A (nome→IP), NS (domínio→servidor autoritativo), CNAME (apelido→nome canônico), MX (domínio→servidor de e‑mail). As mensagens de consulta e resposta têm o mesmo formato (ID, flags, contadores e seções) e usam **UDP na porta 53**.

## 16.2 Perguntas curtas que podem aparecer
- **Por que não usar um único servidor?** — SPOF, tráfego, distância, manutenção.
- **Diferença entre consulta iterativa e recursiva?** — § 7.4.
- **Qual a função do servidor DNS local?** — resolvedor recursivo: atende o host, percorre a hierarquia, mantém cache.
- **O que é TTL?** — validade do registro em cache, definida pelo dono do domínio.
- **Para que servem os registros NS, A, CNAME, MX, TXT?** — § 4.
- **DNS usa TCP ou UDP? Por quê?** — UDP/53; § 9.
- **Como o DNS ajuda a combater spoofing de e‑mail?** — TXT com SPF/DKIM/DMARC.
- **O que é um servidor autoritativo? E a flag AA?** — o que tem os registros reais; AA=1 indica resposta autoritativa.

---

# 17. Checklist e armadilhas

**Você domina se consegue, sem consultar:**
- [ ] Desenhar as 8 mensagens da resolução e dizer o que cada uma contém (referência × resposta final).
- [ ] Dizer, para cada servidor (raiz, TLD, autoritativo, local), **o que sabe** e **como responde**.
- [ ] Explicar iterativa × recursiva e **quem** usa cada uma.
- [ ] Contar mensagens com diferentes estados de cache (8/6/4/2).
- [ ] Explicar o papel do **TTL** e do **ID**.
- [ ] Dar um exemplo de cada registro (A, NS, CNAME, MX, TXT).
- [ ] Explicar a dependência circular do NS e o registro A do servidor de nomes no TLD.
- [ ] Calcular o tempo de abrir uma página incluindo o DNS.

**Armadilhas:**
- O **host não** percorre a hierarquia: só fala com o **DNS local**.
- O **DNS local não faz parte** da hierarquia oficial.
- Raiz e TLD **não resolvem**: **indicam** (referência).
- **AA=1 só** em respostas de servidor **autoritativo**.
- Com a resposta em cache, **não há** consulta à hierarquia.
- DNS usa **UDP/53** (e o próprio cliente trata timeouts/retransmissões).
- **CNAME aponta para um nome** (não para IP); **A aponta para IP**; **NS aponta para um nome de servidor**; **MX aponta para um nome de servidor de e‑mail**.
