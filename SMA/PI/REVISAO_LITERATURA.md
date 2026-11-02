# Variar a implementação da cifra em FPGA + revisão de literatura

Complemento de [ESTUDO_VALIDADE.md](ESTUDO_VALIDADE.md) e [PLANEJAMENTO.md](PLANEJAMENTO.md).

> **Como esta revisão foi feita e o que ela NÃO é.** Foram ~15 buscas web (modo estendido) e leitura de 2 artigos pelo texto da página. O resto vem de **resumos e trechos de resultados de busca**. Por isso há uma coluna "evidência" nas tabelas: *lido* (abri a página), *resumo* (só abstract/snippet), *patente*, *não verificado*. **Não é revisão sistemática.** Nada aqui substitui ler os PDFs antes de citar.

---

## Parte 0 — Atualização após ler 4 PDFs (14/10/2026)

Lidos na íntegra (texto extraído dos PDFs em `Artigos/`): **RFTC** (DAC 2019), **Kian et al.** (DPR + mascaramento dinâmico, IEEE 2020), **Vipin & Fahmy** (ACM CSUR 2018, trechos relevantes) e **Cho et al.** (survey de MTD, trechos relevantes). Isso **corrige** itens da versão anterior:

| Antes eu escrevi | O que o PDF diz | Efeito |
|------------------|-----------------|--------|
| RFTC usa DPR e "~219 mil frequências" | RFTC **não faz reconfiguração parcial de bitstream**: reconfigura dinamicamente o **gerenciador de clock (MMCM)** via porta DRP. São **3.072 frequências** (3×1.024) e **67.584 tempos de conclusão distintos**. O "219 mil" veio de um snippet de busca e estava errado | Corrigido na tabela §1.4 |
| Kian et al. "overhead desprezível" | Overhead é só afirmado no resumo; o corpo não traz tabela de área/tempo. O experimento usa só **XOR/XNOR** como funções de máscara | Evidência mais fraca do que parecia |

### 0.1 O que cada PDF contribui de concreto

**RFTC (Jayasinghe, Ignjatovic, Parameswaran, UNSW, DAC 2019): é o dado mais útil para o grupo.**
- **Mecanismo:** AES executa cada rodada com uma entre M saídas de clock, e o conjunto de frequências é trocado reconfigurando MMCMs enquanto outro MMCM segue clocando. As frequências são escolhidas no projeto para **evitar tempos de conclusão repetidos**, porque picos de tempos iguais vazam a chave.
- **Plataforma:** SASEBO-GIII, Kintex-7 325T, AES de 10 ciclos, 12–48 MHz, osciloscópio Agilent DSO-X 2012A.
- **Atacantes testados:** CPA, e três pré-processamentos feitos contra atrasos aleatórios: **DTW, PCA, FFT**. Mais **TVLA** (limite ±4,5).
- **Linha de base:** AES sem proteção cai com ~2.000 traços (FFT-CPA: ~8.000).
- **Resultado por configuração** (RFTC(M, P), M = saídas de clock usadas, P = nº de frequências por saída):

| Configuração | O que quebrou o ataque |
|--------------|------------------------|
| RFTC(1, 4) | CPA e PCA-CPA em ~700 mil; DTW-CPA < 200 mil; FFT-CPA ~800 mil |
| RFTC(1, 16) a (1, 64) | DTW-CPA < 200 mil; FFT-CPA ainda quebra (1,16) em ~800 mil |
| RFTC(1, 256) | DTW-CPA em ~800 mil |
| RFTC(1, 1024) | nenhum ataque revelou a chave em 1 milhão |
| RFTC(2, 4) e (2, 16) | DTW-CPA revela; os outros não |
| RFTC(3, qualquer P) | **nenhum ataque revelou a chave em 4 milhões de traços** |

- **Custo de RFTC(3, 1024):** tempo **1,72x**, potência **1,48x** (estimada pelo XPower), área **1,3x**, **20 Block RAMs**. Reconfiguração de MMCM: **34 µs** no Kintex-7, permitindo ~82 criptografias no intervalo.
- **Limites declarados pelos autores:** M > 3 não roteou no Xilinx ISE 14.7; **não testaram** Rapid Alignment Method nem **Sliding-Window CPA** (deixados como trabalho futuro); resultados de 4 milhões de traços são "omitidos por falta de espaço"; o TVLA de configurações com M = 1 **passa de ±4,5** (vaza).
- **Importante para vocês:** a escolha da frequência é feita por **gerador de números aleatórios**, não por decisão de agente. A aleatoriedade é por criptografia, em escala de nanossegundos.

**Kian, Hosseintalaee, Jahanian (Shahid Beheshti, IEEE 2020):**
- **Ideia:** mudar a função de máscara (XOR ↔ XNOR) por DPR a cada execução do AES, para quebrar a premissa do ataque de segunda ordem de Oswald et al. Zynq-7020 (Z-Turn), osciloscópio GDS-2304A.
- **Resultado:** sem proteção, CPA em ~1 milhão de traços; protegido, **sem correlação significativa com 38 milhões de traços**. Para segunda ordem, o número mínimo de traços estimado pela fórmula de Mangard sobe de 661 (máscara fixa) para ~5.600 a ~30.700 (cinco execuções dinâmicas).
- **Fraquezas:** o ataque de 2ª ordem é avaliado por **modelo ideal e fórmula**, não por ataque real; só duas funções; sem tabela de overhead; o texto traz resíduos de modelo ("component, formatting, style" nas palavras-chave). Tratar como **prova de conceito**.
- **O mais valioso nele é a seção de trabalhos relacionados**, que dá a linha do tempo do campo (ver §0.2). Atenção: ela faz críticas aos colegas ("não mostraram prova" sobre SPREAD e sobre Dessouky & Sadeghi). São críticas **do autor**, não consenso.

**Vipin & Fahmy (ACM CSUR 2018):**
- DPR é muito estudada, mas **pouco usada em sistemas implantados**; adoção travada por ferramentas, granularidade de regiões e tempo de reconfiguração.
- **Tempo de reconfiguração:** FPGAs modernos levam **de vários milissegundos a segundos**, conforme interface, tamanho do bitstream e armazenamento. O ICAP suporta até **400 MB/s** (32 bits a 100 MHz), mas controladores reais ficam bem abaixo (4,6–10,1 MB/s em alguns casos relatados).
- Há citação de PR para funções criptográficas, mas como **economia de área** (reuso de região), não como contramedida.
- Implicação: **trocar bitstream lógico é decisão lenta (ms–s)**; trocar clock via DRP é rápido (µs). Isso define a escala de tempo de cada tipo de agente.

**Cho et al. (IEEE COMST 2020, survey de MTD):**
- Dá a taxonomia: MTD por **shuffling, diversidade e redundância** (o "como mover").
- Apontam como lacunas, nas palavras do survey: **MTD adaptativo ainda é imaturo** (quando disparar depende de detecção ou aprendizado do defensor); **MTD leve e distribuído** para ambientes com recurso restrito e decisão totalmente autônoma é raro; a classificação não captura **"quando mover" e "o que mover"**; e é preciso medir **segurança, performabilidade e custo econômico** juntos.
- A maioria das validações é **simulação ou modelo analítico**; poucas usam emulação ou testbed real.
- Teoria de jogos domina as abordagens; há também otimização genética e aprendizado.
- **Domínios cobertos pelo survey:** redes corporativas, IoT, sistemas ciberfísicos, SDN e web em nuvem. **Hardware/FPGA e canal lateral físico não aparecem como domínio.** (Conferi pelas seções; não é garantia de que nenhum trabalho citado trate disso.)

### 0.2 Estado da arte: linha do tempo (com base nos PDFs lidos)

Fonte da linha 2008–2019: seção de trabalhos relacionados de Kian et al. (portanto **segunda mão**; conferir cada um).

| Ano | Trabalho | Ideia | Observação |
|-----|----------|-------|------------|
| 2008 | Mentens, Gierlichs, Verbauwhede, CHES 2008 | **Primeiro** uso de DPR contra análise de potência: realocar sub-operações da cifra no tecido do FPGA, gerando jitter temporal | Segundo Kian et al., esse desalinhamento pode ser superado com filtros de alinhamento |
| 2011 | Güneysu & Moradi, CHES 2011 | Contramedidas genéricas para dispositivos reconfiguráveis | Citado como referência dos filtros de alinhamento |
| 2015 | Sasdrich, Moradi, Mischke, Güneysu, HOST 2015 | Divide as S-boxes em duas com mapeamentos aleatórios, usando CFGLUT (Spartan-6) | Crítica de Kian: custo de recursos alto para S-box grande (AES) e vazamento em lógica combinacional |
| 2016 | Dessouky & Sadeghi, pôster ACM WiSec | Muda tamanho e nº de recursos de um gerador de ruído gaussiano por DPR conforme potência estimada por oscilador em anel | **Primeiro caso de controle em malha fechada** (potência estimada → ação). Kian: sem prova |
| 2017 | Bete, Saqib, Patel, Robucci, Plusquellic, HOST 2017 (**SPREAD**) | Instâncias diferentes de cada componente, trocadas a cada execução | Kian: sem prova |
| 2019 | Hettwer et al., DATE 2019 | Mesma RTL com **placement e routing diferentes** por configuração | Kian: primeira rodada pode continuar vulnerável |
| 2019 | **RFTC**, DAC 2019 | Clock aleatório de alta cardinalidade via MMCM | **Avaliação mais completa que li**: 4 ataques + TVLA + custos |
| 2020 | Kian et al. | Função de máscara trocada por DPR | Prova de conceito |
| 2021 | (Springer, netlist randomization e implementation diversity) | Netlists alternativos por reconfiguração | **Não li** |
| 2025 | Bommana et al., *Sci. Rep.* | CNN detecta + DPR reage | **Lido antes**; só SPA, qualitativo |

**Tendências que dá para afirmar:**
1. **Passou de "tempo aleatório" para "diversidade" e "mascaramento dinâmico"**, porque desalinhamento isolado é desfeito por alinhamento (DTW/PCA/FFT). RFTC responde isso aumentando muito a cardinalidade.
2. **A avaliação ficou mais rigorosa** (RFTC testa quatro ataques e TVLA), mas outros trabalhos continuam sem prova.
3. **Quase tudo é estático ou aleatório.** O único controle em malha fechada antigo é o de Dessouky & Sadeghi (2016) e o recente é Bommana (2025). **Nenhum dos lidos usa agentes, coordenação entre zonas nem decisão com custo.**
4. **Ataques que podem desfazer parte disso** (não lidos, do meu conhecimento, a verificar): sliding-window CPA e ataques com redes neurais convolucionais contra contramedidas de jitter (por exemplo, Cagli et al., CHES 2017). O próprio RFTC deixa sliding-window como trabalho futuro.

### 0.3 Viabilidade, depois de ler

**Veredito: ainda é viável, com escopo mais estreito e uma hipótese que pode falhar.**

**A favor**
- **A lacuna ficou mais bem fundamentada.** Cho et al. dizem explicitamente que MTD adaptativo é imaturo, que falta MTD leve e distribuído e que o desempenho deve ser medido em segurança, performabilidade e custo. Nenhum dos trabalhos de FPGA lidos tem agentes, coordenação ou decisão com custo. (Isto vale para o que **li**; falta a busca booleana.)
- **Dá para montar o espaço de ações do agente com dados reais.** RFTC fornece configurações com segurança e custo medidos: por exemplo, RFTC(1,4) quebra com ~700 mil traços (CPA) e custa menos; RFTC(3,1024) resiste a 4 milhões e custa 1,72x em tempo, 1,48x em potência e 1,3x em área. Isso é um **catálogo parametrizado de ações** para um agente baseado em utilidade, sem inventar números.
- **O custo de reconfiguração tem referência:** 34 µs para MMCM (RFTC) e ms–s para bitstream (Vipin & Fahmy).

**Contra, e riscos reais**
1. **O agente não pode decidir por criptografia.** RFTC escolhe a frequência por RNG a cada execução, em nanossegundos. Um agente só pode atuar numa **escala mais lenta**: quais parâmetros (M, P, faixa de frequência) usar, quando escalar, quanto orçamento cada zona recebe. A camada de agentes é **supervisória**, e o texto do PI/A2 precisa dizer isso.
2. **A hipótese central pode falhar.** Se "sempre RFTC(3,1024)" custa 1,72x de tempo e 1,48x de potência, uma política fixa no máximo é simples. O agente só compensa se houver **restrição de orçamento compartilhado**, **ameaça intermitente** ou **custo que varia por zona**. É preciso medir contra a linha de base "sempre máximo". Um resultado negativo seria válido para o A2, mas é um risco.
3. **Quem é o atacante?** Análise de potência exige acesso físico ou, em FPGA multi-tenant, sensores remotos de tensão. O cenário mais defensável para agentes que reagem a ameaça é **FPGA compartilhado/multi-tenant**, não um dispositivo isolado. Detectar "ataque em andamento" é difícil (o CNN de Bommana só foi testado com SPA).
4. **Ataques fora do que foi testado.** RFTC deixou sliding-window para trabalho futuro. Qualquer resultado de simulação vale contra o atacante modelado.
5. **Sem placa, tudo é modelo.** Dá para simular CPA e calibrar com os números do RFTC, mas é simulação.
6. **Lacuna não confirmada.** Até a busca booleana (§2.4) ser feita, "ninguém fez" não pode ir para nenhuma entrega.

**Formulação que o estado da arte sustenta**
> "Camada multiagente supervisória, distribuída e sensível a custo, que seleciona e escalona configurações de contramedida contra canal lateral (parametrizadas a partir de RFTC) em zonas de um FPGA, sob orçamento compartilhado de potência, área e vazão."

**Para o PI (prazo 30/10):** nada disso bloqueia. O que muda é o PEAS (medidas de desempenho com os custos acima) e os agentes (Zone Agent supervisório, Resource Manager, Threat Monitor, Attacker). O Walker com 2 targets continua obrigatório.

**Ainda vale baixar (em ordem):** Mentens et al. (CHES 2008), Güneysu & Moradi (CHES 2011), Sasdrich et al. (HOST 2015), Bete et al. / SPREAD (HOST 2017), Hettwer et al. (DATE 2019), Dessouky & Sadeghi (2016), os dois capítulos Springer de 2021 e Cagli et al. (CHES 2017, CNN contra jitter).

---

## Parte 1 — Como funciona "variar a implementação da cifra" contra ataques físicos

### 1.1 O problema que isso resolve: ataque de canal lateral por consumo de energia

Um circuito digital consome energia **dependendo dos dados que processa**. Quando o chip cifra, o consumo em cada instante carrega uma pista fraca sobre valores internos, que dependem da **chave**. O atacante não quebra a matemática do AES. Ele **mede** o chip.

Ataque típico (CPA, análise de potência por correlação), em linguagem simples:

1. O atacante manda cifrar muitos textos conhecidos e **grava a curva de consumo** de cada execução (um *traço*).
2. Para cada palpite de um byte da chave (256 possibilidades), calcula o que o consumo *deveria* ser se o palpite estivesse certo (modelo, como número de bits em 1 na saída da S-box).
3. Correlaciona o previsto com o medido. **O palpite certo é o que correlaciona mais.**
4. Repete byte a byte. Cada byte vira um problema pequeno.

Por que isso funciona: o atacante precisa que **o mesmo ponto do traço signifique a mesma coisa em todas as medições**. Cada medição é ruidosa, então ele compensa com **muitos traços**. O número de traços necessário para descobrir a chave é a métrica padrão de resistência (*measurements/traces to disclosure*).

### 1.2 A defesa de "variar a implementação"

Há duas famílias clássicas de contramedidas:

| Família | Ideia | Exemplo |
|---------|-------|---------|
| **Masking (mascaramento)** | Aleatorizar os valores intermediários, de forma que o consumo não dependa do valor real | Dividir cada valor em "partes" aleatórias |
| **Hiding (esconder)** | Tornar o consumo menos dependente do dado ou **desalinhar/ruidificar** os traços | Atrasos aleatórios, variar o clock, duplicar lógica, variar a implementação |

"Variar a implementação" é **hiding dinâmico**. A cifra continua a mesma (AES continua AES, mesma entrada gera mesma saída), mas **o circuito físico que a calcula muda ao longo do tempo**. Para o atacante, isso significa:

- O **mesmo ponto no traço** deixa de corresponder à mesma operação → os traços ficam desalinhados.
- O **modelo de vazamento** que ele assumiu deixa de valer, porque o consumo de cada versão do circuito é um pouco diferente.
- Ele precisa de **muito mais traços** ou de pré-processamento para alinhar, ou não consegue.

Isso **não elimina** o vazamento. Só aumenta o custo do ataque.

### 1.3 Por que o FPGA é o lugar natural para isso

Em ASIC o circuito é fixo. No FPGA, a **reconfiguração parcial dinâmica (DPR)** troca o conteúdo de uma região em tempo de execução, sem parar o resto. Dá para ter um catálogo de variantes do mesmo bloco e **trocar** entre elas, como se o chip tivesse várias "caras".

### 1.4 As variantes encontradas na literatura

| Técnica | O que muda no hardware | Fonte | Evidência |
|---------|-----------------------|-------|-----------|
| **Troca de S-box (SPREAD)** | Várias versões da S-box do AES, com atrasos diferentes; troca aleatória durante a cifragem | Patente US 11863304 / pedido 20240089079; teses da UNM | patente + resumo de tese |
| **Divisão aleatória da S-box (Sasdrich et al.)** | No PRESENT, divide a S-box em duas partes com registrador no meio, com a divisão alterada a cada execução do bloco | "Achieving side-channel protection with dynamic logic reconfiguration on modern FPGAs" | resumo |
| **Frequência de clock aleatória (RFTC)** | Muda a frequência do núcleo de cifra reconfigurando o **MMCM** (gerenciador de clock, não o bitstream lógico); 3.072 frequências, 67.584 tempos de conclusão | DAC 2019, [doi 10.1145/3316781.3317899](https://doi.org/10.1145/3316781.3317899) (código: GitHub `dnjayasinghe/RFTC`) | **lido** (ver §0.1) |
| **Randomização de netlist** | Troca netlists alternativas em tempo de execução; relatam aumento de resistência de ~12,6x em um ZYNQ UltraScale+ | Springer, [978-3-030-79025-7_12](https://link.springer.com/chapter/10.1007/978-3-030-79025-7_12) e `_13` | resumo; **página bloqueada, não confirmei** |
| **Mascaramento com função trocada em tempo de execução** | Troca a função de máscara via DPR; resistência à DPA de 1ª ordem e melhora na de 2ª, overhead "desprezível" | IEEE, [Protecting the FPGA IPs against Higher-order SCA using DPR](https://ieeexplore.ieee.org/iel7/9203792/9211850/09211862.pdf) | resumo |
| **Lógica "cola" aleatória** | Substitui lógica extra por DPR a cada 1 ms para mascarar variação de potência | Sci. Rep. 2025, [PMC12012193](https://pmc.ncbi.nlm.nih.gov/articles/PMC12012193/) | **lido** (ver §1.6) |

### 1.5 Limites conhecidos (importantes para não superestimar)

- **Alinhamento de traços derrota parte disso.** Para clock aleatório, há trabalho mostrando que processamento de alinhamento ainda permite CPA (Tian, Shoufan, Stoettinger, Huss, 2012), e que **janela deslizante** pode amplificar a correlação mesmo com jitter ([arXiv 2307.13834](https://arxiv.org/pdf/2307.13834) e trabalhos relacionados; citados em resultado de busca).
- **A robustez depende de hiperparâmetros pouco entendidos.** Galli et al. (Politecnico di Milano, [arXiv 2409.01881](https://www.arxiv.org/pdf/2409.01881)) estudam variabilidade em tempo de execução com medições reais e dizem que uma análise em profundidade dos hiperparâmetros ainda falta.
- **Randomização geralmente eleva o nº de traços, não zera o vazamento.** Ataques de ordem superior ainda podem funcionar contra alguns esquemas. A recomendação usual é combinar DPR com masking.
- **Falta de benchmark comum.** Os ganhos reportados usam ataques, dispositivos e limiares diferentes e quase sempre vêm dos próprios autores. Não são comparáveis entre si.
- **Custo da reconfiguração.** Latência e confiança no bitstream novo (autenticação) são problemas reais (ver §3.5).

### 1.6 Atenção: um dos artigos mais "novos" é fraco

O artigo de 2025 que combina deep learning e DPR (Bommana et al., *Scientific Reports* 15:13745) é o mais próximo da ideia de **detecção → resposta**. Pela leitura da página, porém:

- avalia **só SPA** (análise simples de potência); DPA/timing/EM são citados como possíveis, **não testados**;
- as três contramedidas (clock gating, frequência dinâmica, lógica aleatória) têm resultado **qualitativo**: "o atacante não conseguiu extrair a chave";
- **não reporta traços até divulgação, overhead nem tempo de reconfiguração**;
- detecção: acurácia 0,97 e "20 ciclos" até a mitigação, mas faltam dados de treino, divisão treino/teste e como uma saída de 10 classes vira decisão binária;
- os autores dizem que não buscam o melhor modelo nem a melhor metodologia DPR.

**Use como precedente da arquitetura (monitor + resposta), não como prova de eficácia.**

### 1.7 Como isso conversa com SMA (o que torna a linha interessante)

A técnica em si é engenharia de hardware. O **SMA entra na decisão de quando e como variar**, e é aí que há espaço:

| Decisão | Por que é problema de agente | Literatura de apoio |
|---------|------------------------------|---------------------|
| Quando reconfigurar | Reconfigurar custa tempo e vazão; reconfigurar pouco enfraquece a defesa | Modelos de timing de MTD como jogo de Stackelberg ([arXiv 1905.13293](https://arxiv.org/pdf/1905.13293)); custo de migração dependente do estado atual e do próximo ([arXiv 2002.10390](https://arxiv.org/pdf/2002.10390)) |
| Qual variante/combinação usar | Espaço de combinações, com custo máximo permitido | RL para combinar contramedidas de hiding com limite de custo (Rijsdijk, Wu, Perin, [IACR ePrint 2021/526](https://eprint.iacr.org/2021/526)) |
| Reconfigurar todas as zonas ao mesmo tempo? | Estoura energia/vazão; coordenação descentralizada | Jogo do sprinting (Fan, Zahedi, Lee, ASPLOS 2016), o artigo do Jean |
| Como saber que há ataque | Observação parcial, ruidosa | CNN sobre traço do Sysmon (Bommana et al.) |

Esse é o ponto: o grupo **pode manter o tema SMA + FPGA** e trocar o objeto da decisão de "qual cifra" para **"qual configuração de contramedida física, quando e em qual zona"**. É uma linha mais bem sustentada que a troca livre de algoritmo.

---

## Parte 2 — Revisão de literatura: a ideia tem respaldo?

### 2.1 Respaldo por "pilar" da ideia

| Pilar | Respaldo | Força | Observação |
|-------|----------|-------|-----------|
| **A.** Trocar a implementação de um bloco cripto em FPGA via DPR contra canal lateral | Vários trabalhos (SPREAD, RFTC, netlist randomization, masking dinâmico) | **Médio-forte**, mas pouca replicação independente | Resultados em geral dos próprios autores; limites de alinhamento documentados |
| **B.** Trocar de algoritmo em hardware reconfigurável (agilidade) | DREDS (AES-128 ↔ 3DES via DPR, 2019, ~30% menos lógica que estático); MISTY1/KASUMI reconfigurável; SPECK/SIMON com DPR (IEEE Access 2020) | **Médio** | Mostra viabilidade; é mais motivado por economia de área e atualização do que por segurança |
| **C.** Escolher cifra/política adaptativamente por ameaça com aprendizado | Q-learning em WSN (2025), RL para seleção quântica-segura (IEEE Access), framework híbrido IoT (2025) | **Médio** | Quase tudo **software/IoT**, simulado, **agente único** |
| **D.** Atacante e defensor como agentes que aprendem (MARL/jogo) | CyMARL, MTD como jogo de Markov com WoLF-BSS-Q (*Entropy* 2023), Stackelberg MTD, survey MARL em cibersegurança (arXiv 2505.19837), artigo do Emerson | **Forte para a teoria**, fraco para cripto/hardware | Aplicado a **redes**, não a canal lateral nem a hardware |
| **E.** Agentes rodando em FPGA | Arquitetura BDI híbrida hardware/software (patente), "Applying multi agent techniques to reconfigurable systems" (2004), JADE + FPGA para UAVs, Agent-on-Chip, o artigo do Felipe | **Fraco-médio** | Antigos ou de nicho; BDI em hardware reconfigurável é raro |
| **F.** Agentes cooperando para segurança em hardware | PACA (agentes cooperativos por FPGA em nuvem, 2020) | **Fraco** (um trabalho) | Resposta é migração de tarefas, sem aprendizado |
| **G.** Monitoramento e resposta no chip | SoCINT; sensores de vazamento no chip (Sonar et al. 2016); Bommana 2025 | **Médio** | É o loop "detectar → reagir" |
| **H.** **A combinação** (agentes coordenados no chip decidindo contramedidas físicas/criptográficas adaptativamente) | **Não encontrei** | — | Provável lacuna, **mas ver §2.4** |

### 2.2 Trabalhos mais relevantes, com o que dá para afirmar de cada um

| Trabalho | Contribuição | Evidência | Uso no projeto |
|----------|-------------|-----------|----------------|
| Abbas et al., *Dijlah J. Eng. Sci.* 2026 (artigo do Emerson) | MARL com Defense, Key Mgmt e Attacker, A3C, 4 cenários | **lido** (pelo grupo) | Modelo de agentes e avaliação. Resultados são de **simulação** |
| Fan, Zahedi, Lee, ASPLOS 2016 (artigo do Jean) | Jogo de decisão descentralizada com recurso compartilhado e equilíbrio | **lido** (pelo grupo) | Orçamento e coordenação |
| Zhou et al., IEEE TPDS 2022 (artigo do Felipe) | HMAS em FPGA para roteamento | **lido** (pelo grupo) | Precedente de SMA em FPGA; tema (BCI) é distante |
| Bommana et al., *Sci. Rep.* 2025 | CNN + DPR contra SPA | **lido** (§1.6) | Arquitetura detecção→resposta; evidência fraca |
| Rijsdijk, Wu, Perin, IACR ePrint 2021/526 | RL para combinar contramedidas de hiding sob custo máximo | resumo | **Mais próximo** de "agente escolhe configuração de defesa" |
| Feng, Zheng et al.; Li & Zheng; Li, Shen & Zheng (Stackelberg + MTD) | Modelagem de quando/para onde trocar, com custo de troca | resumo | Base formal para a política de reconfiguração |
| DREDS (Wang et al., 2019) | AES-128 ↔ 3DES por DPR | resumo de busca | Viabilidade de trocar algoritmo |
| Vipin & Fahmy, *ACM Comput. Surv.* 2018 | Survey de reconfiguração em FPGA | resumo | Fundamentação de DPR |
| Cho et al., *IEEE Commun. Surv. Tutor.* 2020 | Survey de MTD | resumo | Limites de avaliação de MTD |
| PACA (UCC, 2020) | Agentes cooperativos por FPGA | resumo | **Precedente direto de SMA + FPGA + segurança** |

### 2.3 Segurança do próprio mecanismo de reconfiguração

Um ponto que o grupo não deve esquecer: **DPR cria uma superfície de ataque.** Um bitstream carregado depois pode sobrescrever partes que o fabricante protegeu. Os padrões encontrados:

- **Autenticar toda imagem de reconfiguração** (a criptografia sozinha não impede bitstream errado ou malicioso; AES-GCM é usado para cifrar e autenticar).
- Vincular chaves ao dispositivo (PUF, chaves em fuse).
- Proteger contra reordenação/remoção de blocos do bitstream.
- A documentação da Intel (Stratix 10) exige que a autenticação de bitstream PR seja pré-requisito para a criptografia e que a chave de autenticação seja a mesma entre base e PR (página marcada como substituída por versão mais nova, conferir).
- Projeto Fraunhofer AISEC (`leakres_updatable_SoC`, Zedboard/Zynq-7000) combina AEAD resistente a vazamento, PUF e DPR: protótipo de pesquisa.

Isso reforça a recomendação do estudo anterior: **catálogo fechado de variantes pré-assinadas**, nunca bitstreams arbitrários.

### 2.4 Sobre a "lacuna": o que posso e não posso afirmar

**Posso afirmar:** nas buscas feitas, nenhum resultado combinava ao mesmo tempo (i) vários agentes autônomos, (ii) rodando ou modelados no chip, (iii) decidindo coordenadamente contramedidas criptográficas/físicas, (iv) de forma adaptativa. Cada peça existe separada.

**Não posso afirmar:** que **ninguém fez**. Razões:
1. As buscas são abrangentes mas rasas; muitos resultados eram só resumos.
2. As bases de maior cobertura para o tema (IEEE Xplore, ACM DL, Scopus, Web of Science) não foram consultadas com sintaxe booleana.
3. Houve páginas bloqueadas (Springer, MDPI) e um título que **não consegui localizar** (ver abaixo).
4. O termo certo pode ser outro. Em hardware, "agente" costuma aparecer como "controller", "runtime manager", "self-adaptive", "autonomic computing".

**Busca recomendada antes de afirmar originalidade** (fazer no Scopus/IEEE/ACM):

```
("multi-agent" OR "multiagent" OR "agent-based") AND (FPGA OR "reconfigurable") AND ("side-channel" OR "cryptograph*" OR "moving target")
("self-adaptive" OR "autonomic") AND "partial reconfiguration" AND ("side-channel" OR "security")
("moving target defense") AND ("dynamic partial reconfiguration") AND ("reinforcement learning" OR "game")
("crypto-agility" OR "cryptographic agility") AND (FPGA OR hardware) AND ("reinforcement learning" OR "adaptive")
```

Registrar a *string*, a base, a data e o nº de resultados. Isso vira uma subseção honesta de metodologia no A2.

### 2.5 Itens que NÃO consegui verificar (não citar sem conferir)

- "Crypto-Agile FPGA Architecture with Single-Cycle Switching for OFDM-Based Vehicular Networks" (MDPI): apareceu em um resultado de busca com um resumo, mas a página retornou 403 e uma busca pelo título exato **não achou a publicação**. Tratar como **não verificado**.
- O fator "~12,6x" da randomização de netlist: só vi no resumo de busca; a página da Springer não abriu.
- Números do RFTC (traços, ataques): só o conceito foi confirmado.
- A afirmação de que "migração de VM em MTD mais piora que melhora a segurança": autoria não confirmada.
- SPREAD: a fonte principal que vi é **patente** (descreve o método, não prova que funciona) e teses; procurar o artigo revisado por pares.

---

## Parte 3 — Veredito sobre "variar a implementação" como direção

| Critério | Avaliação |
|----------|-----------|
| Respaldo técnico | **Bom**: família real de contramedidas, com protótipos em FPGA |
| Respaldo de que "funciona sempre" | **Limitado**: ganhos sobem o custo do ataque, não eliminam, e há ataques conhecidos que desfazem parte (alinhamento) |
| Encaixe em SMA | **Bom, se** o agente decidir *quando/como/onde* variar, com custo de troca e orçamento (não se for só "trocar aleatoriamente") |
| Viabilidade no semestre | **Média**: sem placa e sem medição de potência, só dá para **modelar** |
| Originalidade | **Promissora** (lacuna aparente), **a confirmar** com a busca da §2.4 |
| Risco | Prometer segurança física sem poder medir |

### Como fazer isso sem placa nem osciloscópio

Dá para **simular o ataque**:
1. Gerar **traços sintéticos** (modelo clássico: consumo ∝ número de bits em 1 do valor intermediário + ruído gaussiano).
2. Implementar **CPA** em Python/NumPy e medir **traços até recuperar o byte da chave**.
3. Representar cada variante do circuito como um **deslocamento/ganho/ruído diferente** do modelo de vazamento, e a troca como mudança de variante a cada N execuções.
4. Os agentes escolhem variante e período; a métrica é **traços-até-divulgação** contra custo de reconfiguração.

Com isso, o grupo mede algo **real dentro do modelo**, sem inventar números de hardware, e declara a limitação (resultado é de simulação). Existem ferramentas e bancos de traços públicos para ataque a canal lateral (por exemplo, o ecossistema ChipWhisperer); conferir antes de usar.

---

## Parte 4 — Impacto no PI e no resto do projeto

**O que muda no PEAS (se o grupo adotar essa direção):**
- **Performance:** traços-até-divulgação (no modelo), custo de reconfiguração, vazão durante a troca, energia.
- **Actuators:** selecionar variante do bloco, ajustar frequência, solicitar troca, isolar zona.
- **Sensors:** estimativa de ameaça (anomalia no consumo), estado da reconfiguração, orçamento.
- **Environment:** continua parcialmente observável, estocástico, dinâmico, multiagente.

**O que não muda:** Walker com 2 targets e o resto do checklist do PI.

**Para o A2:** "SMA para decisão de reconfiguração de contramedidas de canal lateral em FPGA, avaliado por simulação de CPA com custo de reconfiguração" é uma contribuição concreta e testável.

### Decisões para o grupo
- [ ] Adotar "variação de implementação/contramedida" como objeto da decisão dos agentes (recomendado) ou manter "troca de algoritmo"?
- [ ] Manter também a troca de algoritmo como segunda dimensão (catálogo restrito) ou cortar para focar?
- [ ] Alguém fará a busca booleana da §2.4 (Scopus/IEEE/ACM) e registrará as strings?

---

## Fontes consultadas (resultados de busca; conferir antes de citar)

- [Bommana et al., Sci. Rep. 2025 — DPR + deep learning (PMC12012193)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12012193/)
- [Rijsdijk, Wu, Perin — RL-based design of side-channel countermeasures (ePrint 2021/526)](https://eprint.iacr.org/2021/526)
- [Protecting FPGA IPs against higher-order SCA using DPR (IEEE)](https://ieeexplore.ieee.org/iel7/9203792/9211850/09211862.pdf)
- [RFTC (DAC 2019)](https://doi.org/10.1145/3316781.3317899)
- [Increasing side-channel resistance by netlist randomization (Springer)](https://link.springer.com/chapter/10.1007/978-3-030-79025-7_12)
- [Moving target and implementation diversity countermeasures (ACM/Springer)](https://dl.acm.org/doi/10.1007/978-3-030-79025-7_13)
- [Achieving side-channel protection with dynamic logic reconfiguration on modern FPGAs](https://www.researchgate.net/publication/283230144_Achieving_side-channel_protection_with_dynamic_logic_reconfiguration_on_modern_FPGAS)
- [Patente SPREAD US 11863304](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11863304)
- [Galli et al., run-time variability e SCA em FPGA (arXiv 2409.01881)](https://www.arxiv.org/pdf/2409.01881)
- [Duplicated randomized clock SCA countermeasure (arXiv 2307.13834)](https://arxiv.org/pdf/2307.13834)
- [Stackelberg MTD: timing (arXiv 1905.13293)](https://arxiv.org/pdf/1905.13293)
- [Spatial-temporal MTD, Markov Stackelberg (arXiv 2002.10390)](https://arxiv.org/pdf/2002.10390)
- [MARL em Bayesian Stackelberg Markov games para MTD (arXiv 2007.10457)](https://arxiv.org/pdf/2007.10457)
- [MTD como jogo de Markov multiagente (Entropy 2023)](https://www.mdpi.com/1099-4300/25/4/605)
- [MARL em cibersegurança (arXiv 2505.19837)](https://arxiv.org/abs/2505.19837)
- [CyMARL (arXiv 2310.05939)](https://arxiv.org/pdf/2310.05939)
- [Hybrid framework IoT adaptativo (PMC13075269)](https://pmc.ncbi.nlm.nih.gov/articles/PMC13075269/)
- [MISTY1/KASUMI reconfiguráveis (PMC10538736)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10538736/)
- [Applying multi agent techniques to reconfigurable systems (ScienceDirect)](https://www.sciencedirect.com/science/article/abs/pii/S0965997804000729)
- [JADE + FPGA para UAVs (Springer)](https://link.springer.com/chapter/10.1007/978-3-319-90023-0_2)
- [PACA / agentes cooperativos em FPGA (UCC)](https://research.ucc.ie/en/publications/a-multi-agent-co-operative-model-to-facilitate-criticality-based/)
- [Fraunhofer AISEC leakres_updatable_SoC](https://github.com/Fraunhofer-AISEC/leakres_updatable_SoC)
- [Intel Quartus — PR bitstream encryption](https://intel.com/content/www/us/en/docs/programmable/683834/23-2/pr-bitstream-encryption-designs.html)
