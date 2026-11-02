# Planejamento do Projeto Inicial (PI) — SMA 2026.2

**Tema do grupo:** sistema multiagente em FPGA em que a criptografia interna muda de forma autônoma entre áreas (zonas) do chip.
**Grupo:** Emerson, Felipe, Jean, Thiago.
**Hoje:** 14/10/2026 (quarta). **Entrega do PI:** 30/10/2026 às 23:59 (Moodle) **e** seminário no mesmo dia (30/10, sexta, 17:50).
**Valor:** PI = 20% da nota (`NF = A1*0.1 + PI*0.2 + PF*0.4 + A2*0.3`).

> Fontes: `Slides/4.1-Projeto Inicial-09-10-26.pdf`, `Slides/Ementa_SMA.pdf`, `Slides/3.SMA…` (MASPY/BDI), `Slides/4.SMA…` (raciocínio prático) e os 4 artigos do A1.

---

## 1. O que a professora pede (checklist do PI)

Entrega única em grupo, via Moodle, até **30/10 23:59**:

| # | Item | Formato | Origem |
|---|------|---------|--------|
| 1 | **Especificação PEAS** (Performance, Environment, Actuators, Sensors) + as 6 propriedades do ambiente | PDF | slide 4.1, pág. 3 |
| 2 | **Tipos de agentes** definidos (Simple Reflex, Reflex com estado, Goal-based, Utility-based, Learning) | PDF | slide 4.1, pág. 3 |
| 3 | **Modelagem Prometheus** (MOD) | PDF | slide 4.1; ementa pede "requisitos iniciais e finais" |
| 4 | **Implementação em MASPY** — *Walker com 2 targets* de valores diferentes, agentes competem pelo de maior valor | código-fonte | slide 4.1, pág. 3 |
| 5 | **Apresentação em seminário** | slides | ementa (30/10) |

As 6 propriedades do ambiente a classificar: observável (total/parcial), determinístico/estocástico, episódico/sequencial, estático/dinâmico, discreto/contínuo, agente único/multiagente.

### Ponto que precisa de decisão — como o tema encaixa no código obrigatório

O exemplo de PEAS da professora (OLT/BBU/RMA, rede de telecom) **não tem relação com o Walker**. Isso indica que **PEAS, tipos de agente e Prometheus são do nosso domínio**, enquanto o **código do PI é o Walker com 2 targets**. Essa é a minha leitura; **confirmar com a professora** (ver §9).

Estratégia recomendada (cobre as duas interpretações):

1. **Núcleo obrigatório:** Walker com 2 targets em MASPY, fiel ao enunciado.
2. **Camada temática (extra, se der tempo):** reaproveitar a mesma estrutura de grade como um "mapa de zonas do FPGA" (ver §5, nível MVP). Assim o código do PI já é o embrião do PF.

PEAS/Prometheus/tipos de agente **sempre** do domínio cripto-FPGA.

---

## 2. Entendendo a ideia: o que dá para fazer nessa linha

### 2.1 Em uma frase

Cada região do FPGA tem um agente que **escolhe, negocia e troca** o algoritmo e as chaves usados na comunicação entre regiões, reagindo a ameaças e a restrições de custo (energia, área, latência), sem controle central.

### 2.2 Conceitos que sustentam a ideia (termos para pesquisar)

- **Crypto-agility** — capacidade de trocar algoritmos/parâmetros sem redesenhar o sistema. É o nome "oficial" do que vocês querem.
- **Moving Target Defense (MTD)** — mudar continuamente a superfície de ataque para o atacante nunca ter um alvo estável. Aqui: alvo = algoritmo, chave, mapeamento zona↔cifra.
- **Reconfiguração parcial dinâmica (DPR) em FPGA** — trocar o bitstream de uma região enquanto o resto continua rodando. É o mecanismo de hardware que torna "trocar o núcleo de cifra em tempo de execução" fisicamente possível.
- **Segurança de FPGA multi-tenant / NoC segura** — zonas de confiança diferentes no mesmo chip, comunicação entre elas por interconexão (NoC/barramento).
- **Criptografia leve** (ex.: Ascon, padrão NIST de cripto leve) vs. **AES/ChaCha20** vs. **pós-quântica** (ex.: ML-KEM): são os candidatos naturais para o "catálogo" de cifras com trade-offs distintos.
- **MARL** (aprendizado por reforço multiagente) e **teoria dos jogos** para decisão descentralizada.

> Não citem nada daqui no PDF sem localizar e conferir a referência real. Os termos servem de palavra-chave para Scopus/IEEE/ACM.

### 2.3 Como cada artigo do A1 alimenta o projeto

| Artigo | Autor do grupo | O que aproveitar |
|--------|----------------|------------------|
| *An Agent-Based RL Framework for Dynamic Cryptographic Security* (Abbas et al., DJES 2026) | Emerson | **Papéis de agente prontos:** Defense Agent (escolhe algoritmo/tamanho de chave), Key Management Agent (rotação), Attacker Agent (adversário que co-evolui). Recompensas por papel, A3C, 4 cenários de ameaça, métricas (tempo até comprometimento, latência de cifra, frequência de rotação, overhead de CPU). **É a base do modelo de agentes e da avaliação.** |
| *The Computational Sprinting Game* (Fan, Zahedi, Lee, ASPLOS 2016) | Jean | **Recurso compartilhado + decisão estratégica:** cada agente decide localmente, a consequência é coletiva (o "disjuntor" cai). Mapeia direto para **orçamento global de energia/área/latência**: trocar para uma cifra cara em muitas zonas ao mesmo tempo estoura o orçamento. Dá o argumento de **equilíbrio descentralizado**. |
| *Heterogeneous MAS for BCI … Memristive Neuron Networks* (Zhou et al., IEEE TPDS 2022) | Felipe | **Precedente de SMA implementado em FPGA** (sub-agentes, portas de forwarding, memória no próprio chip). Serve de justificativa de viabilidade e de arquitetura (agente = bloco lógico). |
| *Recursive Language Models* (Zhang, Kraska, Khattab, MIT 2026) | Thiago | Menos direto. Uso plausível: **agente "analista" fora do FPGA** (offline) que lê logs/alertas longos e propõe políticas — não roda no chip. Decidir se entra ou fica só como trabalho relacionado. |

Observação honesta: a combinação SMA + FPGA tem **pouca literatura** (o Jean já percebeu isso ao escolher o artigo). Isso é ao mesmo tempo risco (poucas referências) e ponto positivo (contribuição original para o A2).

### 2.4 Pontos críticos que a banca/professora podem questionar

Vale já ter resposta preparada — e incorporar ao projeto:

1. **Trocar de algoritmo não é, por si só, mais seguro.** A justificativa precisa ser concreta: resistir a ataques de canal lateral/análise estatística (alvo móvel), limitar o dano de comprometimento de uma zona, ou adaptar custo ao nível de ameaça.
2. **Sincronização:** quem cifra e quem decifra precisam concordar na cifra e na chave. Exige **protocolo de negociação** entre agentes (isso é ótimo para SMA: contract-net, propose/accept, FIPA-like).
3. **Ataque de downgrade:** um adversário forçando a negociação para a cifra mais fraca. O catálogo só deve conter cifras aceitáveis, e a política precisa de piso mínimo.
4. **O próprio agente é superfície de ataque** (se for comprometido, escolhe a cifra errada). Mencionar como limitação/ameaça no modelo.
5. **Custo da troca:** reconfigurar uma região (DPR) tem latência e perde throughput. A decisão de trocar deve pesar esse custo — igual ao "esperar para esfriar" do sprinting game.
6. **Autonomia vs. segurança:** quanto da decisão é local e quanto passa por um coordenador? Definir explicitamente (sugestão em §4).

### 2.5 Direções possíveis (do mais simples ao mais ambicioso)

| Nível | O que é | Cabe no PI? | Cabe no PF? |
|-------|---------|-------------|-------------|
| **A. Simulação de alto nível em MASPY** | Zonas = agentes BDI; cifras = ações com custo/segurança parametrizados; atacante simulado; sem HDL | Sim (mínimo) | Sim (base garantida) |
| **B. A + modelo de custo realista** | Custos de latência/energia/área tirados de números publicados ou medidos de núcleos reais (AES, ChaCha20, Ascon) | Não | Sim (recomendado) |
| **C. B + validação em HDL** | Núcleos de cifra em Verilog/VHDL, simulados (Verilator/GHDL/cocotb ou Vivado) e agentes controlando por co-simulação | Não | Talvez |
| **D. Placa real com DPR** | Troca real de bitstream em runtime | Não | Só se o grupo já tiver placa e experiência |

**Recomendação:** garantir **A no PI**, mirar **B no PF**, tratar **C** como diferencial e **D** como fora do escopo. O PF exige "protótipo + código disponibilizado" e o A2 pede artigo de 8+ páginas; B entrega isso com risco controlado.

---

## 3. Rascunho de PEAS (partir daqui, refinar em grupo)

Agente-exemplo: **Zone Agent (ZA)** — agente de uma área do FPGA.

| Elemento | Proposta |
|----------|----------|
| **P**erformance | Segurança efetiva (tempo até comprometimento, taxa de ataques interceptados); latência e energia de cifra dentro do orçamento; throughput; nº e custo de trocas; disponibilidade da zona durante a troca. |
| **E**nvironment | Mapa de zonas do FPGA e interconexão; catálogo de cifras (custo, nível de segurança); orçamento global de energia/área; outros agentes; atacante. |
| **A**ctuators | Selecionar cifra/tamanho de chave; rotacionar chave; solicitar/aceitar troca de cifra a um vizinho; isolar zona; reconfigurar região; enviar alerta. |
| **S**ensors | Tráfego/volume por canal; alertas do monitor de ameaça; idade e uso da chave; consumo/temperatura locais; mensagens dos outros agentes; confirmações da negociação. |

Classificação do ambiente (a validar): **parcialmente observável** (não se vê o atacante nem o estado interno dos vizinhos), **estocástico**, **sequencial**, **dinâmico**, **discreto** (épocas/ciclos de decisão, catálogo finito), **multiagente** (cooperativo entre zonas + competitivo contra o atacante).

PEAS adicionais sugeridos (um por tipo de agente do §4): Threat Monitor, Key Manager, Attacker.

---

## 4. Rascunho de agentes e arquitetura

| Agente | Papel | Tipo (aula) | Origem |
|--------|-------|-------------|--------|
| **Zone Agent** (N instâncias) | Escolhe a cifra da zona; negocia com vizinhos; respeita orçamento | **Utility-based** (MVP) → **Learning** (PF) | Emerson (Defense) + Jean (decisão estratégica) |
| **Key Manager Agent** | Gera, distribui, rotaciona e revoga chaves | Goal-based / Reflex com estado | Emerson (Key Mgmt) |
| **Threat Monitor Agent** | Estima nível de ameaça por zona a partir de observações | Reflex com estado | Emerson (cenários) |
| **Resource Manager Agent** (opcional) | Mantém o orçamento global; sinaliza saturação | Goal-based | Jean (sprinting) |
| **Attacker Agent** | Ataca zonas/canais; só existe para avaliação | Learning / Reflex | Emerson (Attacker) |

Interações-chave (viram os protocolos do Prometheus):
- **Negociação de cifra** entre dois Zone Agents (propose → counter → accept/reject → confirm).
- **Pedido de chave** Zone → Key Manager; **notificação de rotação**.
- **Alerta de ameaça** Monitor → Zone(s).
- **Consulta de orçamento** Zone → Resource Manager.

Decisão de autonomia (proposta): decisão **local** de cada zona; coordenação **só** para (i) consenso entre pares na troca e (ii) respeitar o orçamento global. Sem coordenador central de política.

---

## 5. Plano da implementação em MASPY

### 5.1 Obrigatório (Walker com 2 targets)

Base: exemplo **2D-Navigation-Learn** do MASPY — https://github.com/laca-is/MASPY/tree/main/examples/2D-Navigation-Learn (wiki: https://github.com/laca-is/MASPY/wiki/Navigation-on-2D-Grid).

- [ ] Instalar MASPY, MASPY-GUI e Pygame; rodar o exemplo sem alterações.
- [ ] Entender: Walker (2 crenças `path_graph`/`wall_set`, 1 objetivo `move`, 2 planos: conhece/não conhece o target) e Map (percepções de target e posição, ação `move`).
- [ ] Adicionar **2 targets com valores diferentes**.
- [ ] Walkers **competem pelo target de maior valor** (decidir: escolha por utilidade = valor / distância? disputa quando dois miram o mesmo?). Documentar a regra.
- [ ] Mantêm a comunicação existente (troca de caminhos/paredes/target) e definir o que acontece com o target capturado.
- [ ] Métricas simples para o seminário: quem pegou qual target, passos, conflitos.

### 5.2 Camada temática (opcional, preferível)

Reinterpretar a grade como **mapa de zonas do FPGA**:
- Walker → mensagem/fluxo de dados cruzando zonas; "paredes" → zonas hostis ou links indisponíveis.
- Em vez de só caminhar, cada zona escolhe a cifra com que cobra o fluxo (custo vs. segurança), com um **Attacker Agent** simples.

Só começar se o núcleo 5.1 estiver rodando e entregável. Se não houver tempo, o seminário apresenta 5.1 + a arquitetura planejada para o PF.

---

## 6. Plano da modelagem Prometheus

Ferramenta: **Prometheus Design Tool (PDT)** (JAR standalone — procurar no GitHub, conforme slide) **ou** draw.io/Lucidchart/Miro. O resultado final vai para o PDF; se o PDT não rodar, desenhar no draw.io usando a notação Prometheus.

| Fase | Artefatos | Observação |
|------|-----------|------------|
| **Especificação do sistema** | Metas e submetas; cenários (ex.: "zona detecta ameaça e troca cifra com vizinho"); funcionalidades; percepts e ações; requisitos **iniciais e finais** | Os cenários vêm direto dos 4 cenários de ameaça do artigo do Emerson |
| **Projeto arquitetural** | Tipos de agente; **diagrama de acoplamento de dados**; protocolos de interação; **diagrama de visão geral do sistema** | Peça central do PDF |
| **Projeto detalhado** | Capacidades, planos, eventos, dados por agente (pelo menos Zone Agent completo) | Alinhar com crenças/objetivos/planos do MASPY |

Boa prática: manter **rastreabilidade**: meta → funcionalidade → agente → plano → trecho de código.

---

## 7. Cronograma (14/10 → 30/10)

Aulas: sexta 16/10, 23/10 e 30/10. Sugestão de marcos:

| Quando | Marco | Entregável interno |
|--------|-------|--------------------|
| **Qua 14 – Qui 15** | Reunião de kickoff; fechar decisões abertas (§8); enviar dúvidas à professora; criar repositório/pasta compartilhada | Decisões registradas; lista de dúvidas |
| **Sex 16** (aula) | Tirar dúvidas com a professora; ambiente MASPY de todos funcionando | Exemplo 2D-Navigation rodando em todas as máquinas |
| **17 – 19** | PEAS v1 + escolha dos tipos de agente + metas/cenários | Rascunho PEAS, lista de metas e cenários |
| **20 – 22** | Prometheus: arquitetura (agentes, protocolos, visão geral); em paralelo, Walker com 2 targets | Diagramas v1; Walker funcional |
| **Sex 23** (aula) | Checkpoint com o grupo: revisão cruzada de PEAS/Prometheus; mostrar Walker | Lista de correções |
| **24 – 26** | Prometheus detalhado; refino do código; (opcional) camada temática 5.2 | Diagramas v2; código comentado |
| **27 – 28** | Montar o **PDF** final (PEAS + tipos de agente + Prometheus + descrição do código); começar os slides | PDF v1 |
| **Qui 29** | Revisão final, ensaio do seminário, conferir tudo no checklist (§10) | PDF + código + slides finais |
| **Sex 30** | **Submeter no Moodle antes das 23:59** (ideal: de manhã) e apresentar | Submissão feita |

Folga proposital: o prazo de submissão e o seminário caem no mesmo dia. **Fechar tudo na quinta 29**.

---

## 8. Divisão de trabalho sugerida (ajustar entre vocês)

Sugestão baseada no artigo que cada um já conhece:

| Pessoa | Responsabilidade principal | Apoio |
|--------|---------------------------|-------|
| **Emerson** | PEAS e agentes de segurança (Defense/Key Mgmt/Attacker), cenários de ameaça | Prometheus |
| **Jean** | Modelo de custo/orçamento compartilhado (Resource Manager), decisão utilitária do Zone Agent | Slides do seminário |
| **Felipe** | Arquitetura em FPGA (mapa de zonas, DPR, viabilidade de hardware) e diagramas do projeto arquitetural | PDF |
| **Thiago** | Código MASPY (Walker + 2 targets) e infraestrutura do repositório | Cenários / testes |

Todos revisam o PDF. Uma pessoa é o **editor-chefe** do PDF final para padronizar linguagem e figuras.

### Decisões abertas para o grupo
- [ ] O RLM (artigo do Thiago) entra no projeto ou fica só como trabalho relacionado?
- [ ] Qual nível de ambição (A, B, C, D do §2.5) é o alvo do **PF**? Alguém tem placa FPGA e experiência com Vivado/Quartus?
- [ ] Quantas zonas e quantas cifras no catálogo? (sugestão: 4–6 zonas, 3 cifras)
- [ ] Documento em português ou inglês? (O A2 é preferencialmente em inglês; escrever o PI em português é aceitável, mas conferir.)
- [ ] Ferramenta de diagramação: PDT ou draw.io?

---

## 9. Dúvidas para levar à professora (sexta 16/10)

1. O **PEAS/Prometheus deve ser do nosso tema (FPGA/criptografia)**, enquanto o código do PI é o Walker com 2 targets? Ou o código também deve refletir o tema?
2. Qual o **tempo e formato do seminário** de 30/10?
3. Há **tamanho mínimo/máximo** ou template do PDF do PI?
4. Um sistema multiagente voltado a **hardware (FPGA)** é aceito como tema do PF, sendo a implementação uma simulação em MASPY (sem HDL)?
5. Aceita-se PDT ou diagramas feitos em draw.io para o Prometheus?
6. Como o Walker deve resolver a **competição** (quando dois agentes querem o mesmo target)?

---

## 10. Checklist final de entrega (30/10)

**PDF**
- [ ] Capa: disciplina, grupo, data, título
- [ ] Contexto e motivação (curto) + ligação com os artigos do A1
- [ ] **PEAS** completo + classificação das 6 propriedades do ambiente
- [ ] **Tipos de agente** definidos e justificados
- [ ] **Prometheus**: especificação (metas, cenários, percepts/ações, requisitos iniciais e finais), arquitetura (visão geral, acoplamento de dados, protocolos), projeto detalhado
- [ ] Descrição do código MASPY (como rodar, regra de competição pelos targets)
- [ ] Referências (só as verificadas)

**Código**
- [ ] Walker com 2 targets de valores diferentes, competição pelo maior valor
- [ ] Roda do zero seguindo um README curto (instalação do MASPY/Pygame)
- [ ] Comentado; sem arquivos desnecessários

**Moodle e seminário**
- [ ] Submissão feita no curso Sistemas Multiagentes (https://moodle.utfpr.edu.br/course/view.php?id=36307) antes de 30/10 23:59
- [ ] Slides prontos; ensaio feito; demo do Walker testada (e gravada, caso o ao vivo falhe)

---

## 11. O que vem depois (para não perder o fio)

| Entrega | Data | Peso | Conexão com o PI |
|---------|------|------|------------------|
| **PF** — Prometheus completo + UML, arquitetura de software, modelo de raciocínio dos agentes, protótipo | 04/12/26 | 40% | PI vira a base. Apresentar andamento durante o semestre vale nota (grupo que não apresenta perde 0,5 no PF) |
| **A2** — artigo em grupo, ≥8 páginas, LaTeX, preferencialmente em inglês | 11/12/26 | 30% | Contribuição esperada: arquitetura + avaliação do SMA de crypto-agility |

Um bom PI aqui economiza trabalho lá: PEAS vira seção de modelagem do artigo, protocolos viram seção de arquitetura e os cenários de ameaça viram a avaliação.

---

## 12. Riscos

| Risco | Mitigação |
|-------|-----------|
| Escopo FPGA grande demais para o semestre | Fixar nível A no PI e B no PF; HDL/placa só como extra |
| Pouca literatura SMA + FPGA | Usar os 4 artigos como pilares; buscar por *crypto-agility*, *moving target defense FPGA*, *dynamic partial reconfiguration security*, *multi-agent hardware* |
| Walker obrigatório "descolado" do tema | Reaproveitar a grade como mapa de zonas (§5.2) e explicar a ponte no seminário |
| PDT não funcionar (descontinuada) | Plano B: draw.io com notação Prometheus |
| Prazo e seminário no mesmo dia | Congelar versão na quinta 29 |
