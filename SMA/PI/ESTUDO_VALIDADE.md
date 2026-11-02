# Estudo de validade da ideia — SMA + criptografia dinâmica em FPGA

Complemento do [PLANEJAMENTO.md](PLANEJAMENTO.md). Escrito para quem **nunca estudou cibersegurança**: primeiro o básico necessário, depois o veredito.

> **Limite deste estudo:** foi feito com buscas web rápidas (resumos de resultados), sem ler os artigos completos. As afirmações abaixo sobre "o que existe na literatura" valem como mapa inicial, **não como revisão sistemática**. Antes de escrever "ninguém fez isso" em qualquer entrega, façam busca real no Scopus/IEEE/ACM.

---

## 1. Veredito curto

**A ideia é válida como projeto de SMA e tem partes cientificamente defensáveis, mas a forma como está formulada ("a criptografia muda sozinha entre áreas") tem um ponto fraco de segurança que precisa ser reformulado.**

| Pergunta | Resposta |
|----------|----------|
| É viável para a disciplina (PI/PF/A2)? | **Sim.** Tem agentes, ambiente, comunicação, negociação, decisão sob incerteza e um adversário. É um bom domínio SMA. |
| "Trocar a cifra o tempo todo" torna o sistema mais seguro? | **Não por si só.** Esse é o ponto frágil. Ver §3. |
| Existem pedaços com respaldo na literatura? | **Sim:** trocar implementação de cifra em FPGA para resistir a ataques físicos, escolha adaptativa de cifra por aprendizado por reforço, e agilidade criptográfica em geral. |
| É original? | **Parece haver uma lacuna** na combinação "agentes coordenando entre si no chip a escolha da cifra" — mas não confirmado (ver limite acima). |
| Vale como artigo (A2)? | Sim, **se** o ganho for medido contra uma linha de base e o modelo de ameaça for explícito. |

A recomendação é **manter o tema, mudar a narrativa**: de "cifra aleatória muda sozinha" para **"política adaptativa e coordenada de escolha de cifra sob restrição de recursos e nível de ameaça"**. Detalhes no §6.

---

## 2. Cibersegurança em 10 minutos (o mínimo para avaliar a ideia)

### 2.1 Os três objetivos
- **Confidencialidade:** só quem deve lê, lê (cifra).
- **Integridade:** ninguém altera sem ser detectado.
- **Autenticidade:** sei com quem estou falando.

Cifras modernas (como AES) fazem isso muito bem **se bem implementadas e com chaves protegidas**. Na prática, quase ninguém quebra o AES matematicamente. Ataques reais vão para outro lugar: chaves vazadas, implementação com falha, configuração errada, ataques físicos.

### 2.2 Modelo de ameaça: a pergunta que decide tudo
Antes de dizer que uma defesa "é boa", pergunta-se: **contra quem, com que capacidade, atacando o quê?** Uma defesa só tem sentido relativa a um atacante. Exemplos relevantes para vocês:

| Atacante | Pode fazer | Cifra trocando ajuda? |
|----------|------------|------------------------|
| **Rede/interceptador** que lê tráfego entre zonas | Observar e tentar quebrar o texto cifrado | Pouco. AES/ChaCha20 já são fortes; trocar não adiciona muito |
| **Atacante de canal lateral** (mede consumo de energia, tempo, emissões do chip) | Extrair a chave observando *como* o hardware cifra | **Sim, é onde há respaldo**: variar a implementação dificulta a correlação |
| **Zona comprometida** (um bloco malicioso/trojan dentro do FPGA) | Ler o que passa por ela | Parcial: limita o dano se cada par de zonas usa chave própria |
| **Atacante ativo na negociação** | Forçar uso de cifra fraca | **A troca dinâmica *piora* o cenário**: cria essa superfície (ver §3) |

### 2.3 Termos que vão aparecer
- **Canal lateral (side-channel):** vazamento por consumo, tempo, calor, e não pela matemática. Famosos: DPA/CPA (análise de potência diferencial/por correlação).
- **Agilidade criptográfica (crypto-agility):** poder trocar algoritmos sem refazer o sistema. Motivação principal real: **migrar para criptografia pós-quântica** e substituir algoritmos que um dia são quebrados.
- **Moving Target Defense (MTD):** mudar continuamente aspectos do sistema para o atacante não ter alvo estável.
- **Downgrade attack:** forçar duas partes a escolherem uma cifra mais fraca na negociação.
- **Trojan de hardware:** circuito malicioso escondido em um chip/IP de terceiros.
- **Multi-tenant FPGA:** vários usuários/blocos de confiança diferente no mesmo FPGA (ex.: FPGA na nuvem).
- **DPR:** reconfigurar uma parte do FPGA em tempo de execução, sem parar o resto.

---

## 3. O ponto fraco da ideia (e por que não invalida o projeto)

### 3.1 "Mudar de cifra" cria problemas que o sistema estático não tem

A literatura de agilidade criptográfica é clara em um ponto: **flexibilidade é também superfície de ataque.**

- Quando duas partes **negociam** a cifra, um atacante ativo pode tentar forçar a mais fraca (downgrade). Isso apareceu em protocolos reais, como versões antigas do SSL e até do TLS. Há inclusive pouca formalização sobre a segurança de negociação em protocolos modernos ([Bhargavan et al., IACR ePrint 2016/072](https://eprint.iacr.org/2016/072.pdf)).
- O RFC 7696 (guia do IETF sobre agilidade de algoritmos) já avisa que ela adiciona complexidade e oportunidade de ataque ([arXiv 1909.07353](https://arxiv.org/pdf/1909.07353), que cita também a opinião de Paul Kocher de que agilidade traz complexidade com consequências imprevisíveis).
- Segundo a Wikipedia, uma alternativa recomendada é **limitar bastante as escolhas disponíveis**, em vez de maximizá-las ([Cryptographic agility](https://en.wikipedia.org/wiki/Cryptographic_agility)).
- Condições que viabilizam downgrade: mensagens de negociação **sem autenticação**, lógica de *fallback* que aceita algoritmos antigos, e escolha **não amarrada ao handshake**. Mitigação: proteger criptograficamente a negociação.

Ou seja, **um SMA em que agentes "decidem livremente" a cifra é, ingenuamente, mais perigoso que um sistema fixo com AES-256.** Isso precisa estar *dentro* do modelo, não escondido.

### 3.2 "Mudar sempre" não é, em geral, comprovadamente melhor (MTD)

MTD é uma área real e ativa, mas **medir sua eficácia é difícil**. A pesquisa de Cho et al. ([Toward Proactive, Adaptive Defense: A Survey on Moving Target Defense, arXiv 1909.08092](https://arxiv.org/pdf/1909.08092)) destaca que a avaliação de **custo** das técnicas MTD costuma ser melhor feita que a de **eficácia**. Um estudo de opinião de especialistas citado ali (Farris e Cybenko) concluiu que as técnicas mais custo-efetivas são de randomização de layout de endereços ou de conjunto de instruções, e a pior é randomização de rede. Também há relato de que migração de máquina virtual, MTD muito proposto, mais piora do que melhora a segurança (autoria dessa afirmação **não confirmada** nos resultados).

Lição: se vocês disserem "nosso MTD aumenta a segurança" sem medir contra uma linha de base, qualquer avaliador de segurança vai desconfiar.

### 3.3 O que NÃO é problema
- Trocar cifra **não é bobagem**: há motivos reais (pós-quântico, algoritmo quebrado, ataques físicos).
- A ideia de agentes autônomos decidirem sob incerteza e custo **é exatamente o que SMA estuda**.

---

## 4. O que já existe na literatura (mapa inicial)

Resultados de busca rápida; **conferir cada item antes de citar**.

### 4.1 Trocar a implementação da cifra em FPGA para resistir a ataques físicos
- **SPREAD**: usa DPR para trocar componentes do AES (variantes de S-box com atrasos diferentes), reduzindo correlações nos traços de potência e dificultando DPA/CPA. Há tese da UNM com resultados em hardware reais mostrando maior resistência à CPA ([UNM ETD 623](https://digitalrepository.unm.edu/ece_etds/623), [UNM ETD 558](https://digitalrepository.unm.edu/ece_etds/558); ver também [par.nsf.gov](https://par.nsf.gov//servlets/purl/10170135)).
- **ReCoFused** (Ustaoglu, Schmitz, Große, Drechsler, SN Applied Sciences, 2020): reconfiguração parcial para contramedidas de alvo móvel em FPGA (só vi a citação).
- Observação: esses trabalhos trocam **implementações do mesmo algoritmo**, não algoritmos diferentes.

### 4.2 Agilidade criptográfica em FPGA (trocar algoritmos de fato)
- Artigo da **IEEE Access (jan/2020)**: FPGAs dão suporte a *crypto agility*, upload e modificação de algoritmo; propõe projetos com DPR para **SPECK e SIMON** em dispositivos embarcados ([DOAJ](https://doaj.org/article/2871286705fc46e399045045078f1fac)).
- **Vipin e Fahmy, ACM Computing Surveys, 2018** — survey geral de reconfiguração em FPGA; diz que DPR é muito estudada, mas pouco usada em sistemas implantados ([DOI 10.1145/3193827](https://doi.org/10.1145/3193827)).
- Um TCC da TU Crete identifica barreira prática: o tempo de reconfiguração pode ser alto demais para tempo real ([TUC](https://dspace.library.tuc.gr/handle/123456789/1087)).
- Lacunas apontadas pela própria busca: autenticação/integridade dos bitstreams novos, armazenamento, e troca sem interromper o serviço.

### 4.3 Escolha adaptativa de cifra por aprendizado por reforço
- **Q-learning para criptografia adaptativa em redes de sensores** (Sensors, 2025): detector de anomalia classifica ameaça (baixa/moderada/alta) e o RL escolhe a política de cifragem, equilibrando energia e segurança. Resultados **simulados**: -30,5% de energia, 92,5% de entrega, 94% de mitigação ([PMC11990953](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11990953/)).
- **RL para seleção de criptografia adaptativa, pós-quântica, em ambientes inteligentes** (IEEE Access, Noetzold et al.): MDP, middleware com negociação e fallback ([ISCTE](https://repositorio.iscte-iul.pt/handle/10071/37011)).
- Ambos parecem **agente único**, e nenhum trata de cifras leves com restrição por dispositivo.
- O **artigo do Emerson** (Abbas et al.) é multiagente (Defense, Key Mgmt, Attacker, A3C). Atenção: o ambiente dele é **simulado** com AES/RSA/ECC, e os números de latência e overhead dele são de simulação — não são medições em hardware.

### 4.4 Agentes e segurança em hardware/FPGA
- **PACA** (agentes cooperativos por FPGA em nuvem, 2020): monitoram desempenho, migram tarefas entre pares ao detectar anomalia, tentam distinguir falha do tecido vs. bitstream. É coordenação multiagente em FPGA, mas a resposta é migração de tarefa, não aprendizado ([UCC](https://research.ucc.ie/en/publications/a-multi-agent-co-operative-model-to-facilitate-criticality-based/)).
- **SoCINT**: detecção de intrusão em tempo de execução em SoC multicore com IPs de terceiros ([CPS-VO](https://archive.cps-vo.org/node/71539)).
- **Sensores de leakage no chip**: alerta quando o vazamento passa de um limiar e dispara contramedidas ([Sonar et al., ePrint 2016/182](https://eprint.iacr.org/2016/182)).
- Defesas em FPGA multi-tenant: DPReDO (UNH, 2025), localização de ataque de tensão (EPFL).

### 4.5 Referência normativa de agilidade
- **NIST CSWP 39** — *Considerations for Achieving Crypto Agility* (versão de dezembro/2025, com atualização em 06/2026). Agilidade como capacidade que envolve **projeto técnico, processos operacionais, governança e limites de hardware**, não como "um interruptor" ([NIST CSRC](https://csrc.nist.gov/pubs/cswp/39/upd1/considerations-for-achieving-crypto-agility/final)). **Ler o PDF primário** para citar corretamente.

### 4.6 A lacuna aparente
Nas buscas, **não encontrei** trabalho com *agentes rodando no chip, coordenando-se entre si, escolhendo contramedidas criptográficas de forma adaptativa*. Cada peça existe separada (monitor + resposta, DPR para MTD, RL para escolha de cifra, agentes cooperativos em FPGA). **A combinação parece pouco explorada**, o que é bom para originalidade, mas pode ser sinal de busca incompleta. **Verificar com busca de verdade.**

---

## 5. Avaliação honesta das partes da ideia

| Parte | Defensável? | Observação |
|-------|-------------|-----------|
| Agentes por zona decidindo localmente | **Sim** | Casa com SMA; custo de comunicação e consenso são problemas reais |
| Escolher cifra conforme **nível de ameaça** | **Sim** | Tem trabalho prévio (Q-learning em WSN, RL pós-quântico) |
| Escolher cifra conforme **custo/orçamento** (energia, área, latência) | **Sim, forte** | É o argumento mais sólido; combina com o sprinting game do Jean |
| Variar a **implementação** contra canal lateral | **Sim, com base experimental** | SPREAD/ReCoFused. Mas exige hardware/medição de potência para provar |
| Trocar a **chave** com frequência | **Sim** | Limita janela de exposição; prática padrão de segurança |
| Trocar **algoritmo** aleatoriamente "para confundir" | **Fraco** | Sem ganho comprovado, com custo e novos riscos |
| Atacante que aprende (co-evolução) | **Sim para avaliação** | Cuidado: avaliar contra o atacante que *vocês* programaram é circular; ver §7 |
| Reconfiguração real do FPGA a cada troca | **Viável, mas custosa** | Latência de DPR; confiar no bitstream novo é outro problema |
| LLM/RLM no loop | **Fraco para o chip** | Não cabe em tempo real no FPGA; só como analista offline |

---

## 6. Como reformular para ficar forte

### 6.1 Narrativa proposta
> "Um sistema multiagente de **agilidade criptográfica adaptativa** em FPGA: cada zona escolhe, sob um orçamento compartilhado de recursos e um nível de ameaça estimado, entre um **catálogo restrito e pré-aprovado** de cifras, negociando a troca com os vizinhos por um protocolo **autenticado**, sem coordenador central."

Mudanças em relação à versão original:
1. **Catálogo pequeno e fixo** (só cifras consideradas seguras). Reduz o risco de downgrade e segue a recomendação de limitar escolhas.
2. **Negociação autenticada** como requisito explícito do protocolo entre agentes (não apenas "propose/accept").
3. **Piso mínimo de segurança** que nenhum agente pode violar, mesmo sob pressão de custo.
4. **O motivo da troca é declarado:** (a) ameaça elevada → cifra/chaves mais fortes, (b) pressão de recursos → cifra mais barata **dentro do piso**, (c) suspeita de canal lateral → variar implementação, (d) comprometimento de zona → isolar e rotacionar chaves.
5. **Avaliação contra linha de base:** (i) sistema estático (sempre AES), (ii) troca aleatória, (iii) política adaptativa. O ganho precisa aparecer em alguma métrica.

### 6.2 O que isso vira em SMA (conexão com a disciplina)
- **Negociação** entre agentes (contract-net/propose-accept) com falhas e mensagens adversárias.
- **Teoria dos jogos:** zonas disputando orçamento (Jean) e jogo defensor × atacante (Emerson).
- **Raciocínio prático (BDI):** deliberar (qual cifra, por quê) e planejar (como trocar sem derrubar o serviço), conforme a aula de 09/10.
- **Observabilidade parcial:** o agente não vê o atacante, só indícios.

---

## 7. Armadilhas ao validar

1. **Avaliação circular:** vencer um atacante programado por vocês só mostra que a política vence aquele atacante. Usar vários atacantes, incluindo um fixo/simples e um aleatório, e declarar a limitação.
2. **Números de simulação ≠ hardware.** O artigo do Emerson é simulado, então não importem as latências dele como se fossem de FPGA. Citem como "reportado em simulação".
3. **Não inventar segurança.** Afirmar "aumenta a segurança em X%" só se a métrica e o atacante estiverem definidos. Prefiram métricas operacionais honestas: tempo até comprometer no modelo, custo de recurso, nº de trocas, disponibilidade durante a troca.
4. **Não implementar criptografia própria.** Se houver código, usem implementações padrão de AES/ChaCha20/Ascon. O foco é a **decisão dos agentes**, não a cifra.
5. **Declarar o modelo de ameaça** em uma seção própria, mesmo curta. É o que diferencia projeto de segurança de projeto "enfeitado de segurança".

---

## 8. Plano de estudo (para quem está começando)

Ordem sugerida, ~1 a 2 semanas em paralelo ao PI.

| # | Tema | Meta | Como |
|---|------|------|------|
| 1 | Fundamentos: confidencialidade, integridade, autenticidade; cifra simétrica vs. assimétrica; chaves | Entender o §2 sem consultar | Capítulos introdutórios de um livro-texto de segurança (ex.: Stallings, *Cryptography and Network Security*) ou curso introdutório online |
| 2 | Modelo de ameaça | Saber descrever atacante, capacidade e alvo | Escrever o modelo de ameaça do projeto em 1 página |
| 3 | Canal lateral (DPA/CPA) | Entender por que variar implementação ajuda | Ler a introdução de um artigo do SPREAD e da tese da UNM |
| 4 | Crypto-agility e downgrade | Entender os riscos de negociar | Ler o resumo do [NIST CSWP 39](https://csrc.nist.gov/pubs/cswp/39/upd1/considerations-for-achieving-crypto-agility/final) e o artigo de downgrade ([ePrint 2016/072](https://eprint.iacr.org/2016/072.pdf)) |
| 5 | MTD | Saber suas promessas e limites de avaliação | Seções de introdução e de métricas do [survey de Cho et al.](https://arxiv.org/pdf/1909.08092) |
| 6 | FPGA/DPR | Saber o que é possível e o custo de trocar | [Vipin e Fahmy 2018](https://doi.org/10.1145/3193827) (seleção de seções) |
| 7 | Agentes + segurança | Ver como agentes são usados em segurança | Artigo do Emerson (já com o grupo), PACA, Q-learning em WSN |

### Perguntas de autoteste (se você responde, está pronto)
1. Por que o AES não é "quebrado" e mesmo assim sistemas com AES são invadidos?
2. Contra qual atacante trocar de cifra ajuda? Contra qual **atrapalha**?
3. O que é um downgrade attack e como a negociação autenticada o evita?
4. Qual a diferença entre trocar de **algoritmo** e trocar de **implementação**?
5. Por que o custo de uma troca (reconfiguração) precisa entrar na decisão do agente?
6. Como você mediria se a política adaptativa é melhor que "sempre AES"?

---

## 9. Experimentos de validação (viáveis no PF)

Hipóteses testáveis em simulação (nível A/B do planejamento):

| Hipótese | Experimento | Métrica |
|----------|-------------|---------|
| H1: A política adaptativa gasta menos recurso que "sempre a cifra mais forte" sem reduzir a segurança abaixo do piso | Mesmo cenário, 3 políticas | Energia/latência acumuladas; violações do piso |
| H2: Negociação autenticada impede downgrade que a negociação simples permite | Atacante de downgrade contra os dois protocolos | Nº de downgrades bem-sucedidos |
| H3: Sob orçamento compartilhado, decisão descentralizada evita estouro que a decisão gananciosa causa (efeito "disjuntor") | Muitas zonas, orçamento limitado | Nº de estouros; vazão total |
| H4: Rotação de chave reativa a ameaça reduz o dano de uma zona comprometida | Zona comprometida em instante aleatório | Mensagens expostas |

Se alguma hipótese não se confirmar, isso é **resultado válido** para o A2, desde que reportado honestamente.

---

## 10. Perguntas para levar à professora ou a alguém de segurança

1. Para o escopo de SMA, é aceitável tratar a camada criptográfica como **modelo abstrato** (cifras com custo/segurança parametrizados), sem implementar criptografia?
2. Há alguém no Instituto/UTFPR de segurança ou arquitetura de computadores que possa revisar o **modelo de ameaça** em 30 minutos? Isso eleva muito a credibilidade do trabalho.
3. O grupo tem acesso a uma placa FPGA e a algum equipamento de medição? Se não, assumir nível A/B e declarar a limitação.

---

## 11. Resumo para o grupo decidir

- **Manter** o tema. Ele é aceitável e tem espaço de contribuição.
- **Trocar a narrativa** de "cifra muda sozinha" para "agilidade criptográfica adaptativa, coordenada e sob restrição de recursos".
- **Colocar o risco no modelo:** catálogo restrito, piso de segurança, negociação autenticada.
- **Provar contra linha de base**, não só mostrar que funciona.
- **Para o PI**, nada disso muda o que precisa ser entregue (PEAS, agentes, Prometheus, Walker). Essa reformulação entra como **justificativa e ameaças** no PDF e como **eixo do PF/A2**.
