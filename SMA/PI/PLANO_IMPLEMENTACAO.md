# Plano de implementação: simulação de energia, ataque, algoritmo em estágios e configurações

Continua [PLANO_BASELINE.md](PLANO_BASELINE.md) (feito, ver [simulacao/baseline/README.md](simulacao/baseline/README.md)) e usa o que já existe: alvo A em Python, alvo B em VHDL (GHDL 6.0.0 instalado), CPA, TVLA e testes.

**Hoje é 21/10/2026.** O PI vence em **30/10** e este plano é do **PF (04/12)** e do **A2 (11/12)**. Recomendação: concluir PEAS, Prometheus e Walker primeiro e começar este plano em 31/10.

**Interpretação assumida do pedido.** "Nosso algoritmo em estágios" = a política de decisão do sistema multiagente, construída por etapas, da mais simples à completa. "Configurações diferentes para cada estágio" = conjuntos de parâmetros (catálogo de contramedidas, atacantes, orçamento, zonas) usados em cada etapa. Se a intenção era outra, ajustar as seções 4 e 5.

---

## 0. Decisões recomendadas (resumo)

| Item pedido | Recomendação |
|-------------|--------------|
| **Ambiente de simulação de energia** | **Motor heurístico multi-fonte em Python** (rápido, parametrizável), **validado e calibrado** com o alvo VHDL instrumentado (GHDL + VCD). Fidelidade de nível de porta e placa real ficam como extensão |
| **Heurística da curva de energia** | Soma ponderada de fontes (registrador de estado, registrador de chave, lógica combinacional), forma de pulso por ciclo, jitter, ruído e quantização. Cada contramedida é uma **transformação** do gerador |
| **Algoritmo de quebra** | Suíte de atacantes: CPA (feito), CPA com alinhamento ideal, CPA com integração por janela, DTW, FFT-CPA, TVLA. CPA **online** para milhões de traços |
| **Algoritmo em estágios** | S0 a S6 (§4), com **controlador central** como comparação desde cedo |
| **Configurações por estágio** | Arquivos de configuração versionados, com catálogo de contramedidas calibrado nos dados do RFTC (§5) |
| **Como validar o modelo** | **Análise de robustez:** repetir a comparação entre políticas variando os parâmetros do modelo. Se o ranking se mantém, a conclusão não depende da escolha arbitrária (§1.6) |

---

## 1. Simulação de energia: opções, escolha e como será feita

### 1.1 O que o simulador precisa entregar

1. Um **traço por cifragem** para cada configuração (variante, contramedida ligada ou desligada).
2. **Sensibilidade ao ataque**: as contramedidas precisam alterar os traços de forma que o CPA e seus pré-processamentos sintam (jitter, máscara, diversidade).
3. **Velocidade**: dezenas de milhões de traços no total (o RFTC reporta resistência a 4 milhões de traços; ver §3.2). Em Python vetorizado isso é viável, mas não com simulação de portas.
4. **Parametrizável e reproduzível** (semente, arquivo de configuração).
5. **Honesto sobre a validade**: números absolutos dependem de parâmetros escolhidos por nós.

### 1.2 Opções avaliadas

Estado atual da máquina, verificado: Python 3.13, NumPy, matplotlib e **GHDL 6.0.0** disponíveis. **Vivado e simuladores de Verilog não estão instalados.**

| # | Opção | Fidelidade | Esforço | Velocidade | Contramedidas que consegue representar | Veredito |
|---|-------|-----------|---------|-----------|----------------------------------------|----------|
| O1 | **Modelo sintético simples** (HD do registrador + ruído). *Já temos.* | Baixa | Nenhum | Muito alta | Só jitter simples | Ponto de partida, insuficiente sozinho |
| O2 | **Modelo heurístico multi-fonte** em Python (várias fontes de consumo, pulso por ciclo, jitter, máscara, ruído, ADC) | Média, **controlada por parâmetros** | Médio | Alta | Jitter/clock aleatório, mascaramento, diversidade, ruído extra, chave por zona | **Motor principal** |
| O3 | **RTL em VHDL (GHDL) → VCD → contagem de transições por grupo de sinais** | Média: vê registradores e sinais internos explícitos, **sem glitches** | Médio | Média (segundos para 20 mil cifragens) | Diversidade de S-box e mascaramento (com a ressalva de Bahrami et al.). **Não** representa clock aleatório | **Validação e calibração** de O2 |
| O4 | **Nível de porta com atrasos** (Vogls; ou Vivado com SDF) | Média-alta (glitches, atrasos) | Alto | Baixa-média | Diversidade de implementação, placement e roteamento | Extensão (PF avançado) |
| O5 | **Estimativa de potência do Vivado** (SAIF/XPE) | Estimativa de média, não de traço | Médio, **exige Vivado** | — | Dá **custo** (potência, área, Fmax), não vazamento | Só para a tabela de custos, se houver licença |
| O6 | **SPICE** | Alta | Muito alto | Muito baixa | Tudo, em princípio | Inviável para este projeto |
| O7 | **Placa real + osciloscópio** | Máxima | Muito alto (equipamento) | — | Tudo | Fora do escopo; mencionar como trabalho futuro |

Pontos da literatura que sustentam a decisão (já lidos, ver [SIMULACAO_VARIANTES.md](SIMULACAO_VARIANTES.md)):
- Contagem de transições concorda com SPICE em implementações **sem** mascaramento, mas **não** nas mascaradas (Bahrami et al., SECRYPT 2022). Em O3, o resultado para mascaramento deve ser tratado como **não conclusivo**.
- Em RTL não há glitches, e a pós-implementação desloca o vazamento cerca de meio ciclo (resultado de busca, não lido na íntegra).
- O clock aleatório do RFTC depende de efeitos analógicos do MMCM e **não é simulável em RTL**. Tem que ser **modelado estatisticamente**, o que só O2 faz.

**Escolha: O2 como motor + O3 para validar e calibrar o que for validável.** Justificativa: O2 é o único que cobre todas as contramedidas do projeto e é rápido o bastante para milhões de traços. O3 dá um **ponto de ancoragem independente** (contagens de transições reais do hardware descrito) e protege contra o risco de modelar uma fonte de vazamento que o hardware não tem.

### 1.3 Como a simulação de energia será feita (pipeline)

```
Configuração (YAML)
     |
     v
[L0] Fonte de atividade
     (a) algébrica em Python: estados do AES por ciclo (alvo A)   <- motor de produção
     (b) VHDL instrumentado + GHDL -> VCD -> transições por grupo <- validação
     |
     v
[L1] Heurística da curva: soma ponderada das fontes + forma de pulso por ciclo
     |
     v
[L2] Transformações das contramedidas: jitter/frequências, máscara, variante, ruído extra
     |
     v
[L3] Medição simulada: filtro passa-baixa, deslocamento/deriva, ruído, quantização
     |
     v
Traços (N, amostras)  ->  atacantes (CPA, DTW, ...)  ->  traços até divulgação
```

### 1.4 Heurística da curva de energia (detalhe)

Ver §2. Em resumo: o consumo no instante `t` é

```
P(t) = Σ_g  w_g · A_g(ciclo)  ⊗ pulso(t − t_ciclo)  +  offset  +  deriva(t)  +  ruído(t)
```

onde `A_g` é a atividade (nº de bits que mudam) do grupo `g`, `w_g` o peso do grupo e `⊗` a convolução com a forma do pulso.

### 1.5 Calibração (ancoragem em dados publicados)

O RFTC (lido) dá pontos de referência medidos em placa real (SASEBO-GIII, Kintex-7, AES de 10 ciclos):

| Configuração | Resultado reportado |
|--------------|---------------------|
| Sem proteção | CPA/PCA/DTW ≈ 2.000 traços; FFT-CPA ≈ 8.000 |
| RFTC(1, 4) | CPA e PCA ≈ 700 mil; DTW < 200 mil; FFT ≈ 800 mil |
| RFTC(1, 16) | CPA e PCA: não revelam em 1 milhão; DTW < 200 mil; FFT ≈ 800 mil |
| RFTC(1, 64) | DTW < 200 mil |
| RFTC(1, 256) | DTW ≈ 800 mil |
| RFTC(1, 1024) | nenhum revela em 1 milhão |
| RFTC(2, 4), (2, 16) | DTW revela; os demais não |
| RFTC(3, qualquer P) | nenhum ataque revela em **4 milhões** |

**Procedimento:**
1. Ajustar `σ` e os pesos para o baseline cair perto de 2.000 traços.
2. Implementar o gerador de frequências do RFTC (M saídas, P frequências, faixa de 12 a 48 MHz, uma frequência por rodada) e ajustar apenas os parâmetros de pulso e filtro até as **ordens de grandeza** da tabela acima aparecerem para CPA e DTW.
3. **Congelar** os parâmetros e registrar o que foi ajustado e contra o quê.

**Aviso:** é calibração de **ordem de grandeza** contra **um** artigo e **uma** plataforma. Não valida o modelo em geral. Dizer isso no texto.

### 1.6 Validação e robustez (o que torna o resultado defensável)

| Verificação | O que mostra |
|-------------|--------------|
| **V1.** Correlação entre o sinal de registrador do modelo e as transições do VCD (O3) | O modelo reproduz a atividade que o hardware descrito realmente tem |
| **V2.** Controles negativos (traços embaralhados, outra chave, ciclo errado, ruído enorme) | Não há vazamento escondido no código |
| **V3.** Reproduzir a ordem de grandeza do RFTC (§1.5) | Ancoragem em dado externo |
| **V4. Análise de robustez do ranking** | Repetir a comparação entre políticas (S1 a S5) com os parâmetros do modelo variando em faixas plausíveis (σ, pesos, forma do pulso, deriva). Se **o ranking das políticas não muda**, a conclusão não depende da escolha arbitrária |
| **V5.** Sensibilidade ao atacante | Repetir com atacantes diferentes (§3) |

V4 é o argumento mais forte disponível sem placa: em vez de afirmar que o modelo é fiel, mostrar que a **conclusão é insensível** a ele dentro de uma faixa declarada.

### 1.7 Limites declarados

- Sem placa, os traços são sintéticos. Nenhum número absoluto de traços vale para um chip real.
- O3 não tem glitches nem efeitos analógicos.
- O clock aleatório é modelo estatístico, não física.
- A calibração é contra um único artigo.

---

## 2. Heurística para a curva de energia

### 2.1 Fontes de consumo modeladas

| Grupo `g` | Atividade `A_g` | Peso inicial `w_g` | Origem | Validável em O3? |
|-----------|-----------------|--------------------|--------|------------------|
| Registrador de estado | HD do registrador de 128 bits | 1,0 | Já no baseline | Sim |
| Registrador de chave de rodada | HD de `rk_r` | 1,0 | O VHDL já tem `rk_r` | Sim |
| Saída de SubBytes | HD entre saídas consecutivas da S-box (sinal exposto no VHDL) | 0,3 a 1,0 (faixa) | Lógica combinacional | Sim, com VHDL instrumentado |
| Saída de MixColumns | idem | 0,3 a 1,0 (faixa) | idem | Sim |
| Glitches | fator multiplicativo sobre a combinacional (`1 + g`) | g de 0 a 1 | Literatura qualitativa | **Não** (RTL não vê) |
| Árvore de clock | constante por ciclo | fixo | — | — |
| Outros blocos do FPGA | processo autorregressivo (ruído colorido) | σ_outros | — | — |

**Dica de implementação:** expor as saídas de SubBytes e MixColumns como **sinais** no VHDL (hoje são variáveis dentro de um processo e **não aparecem** no VCD; verificado: o VCD atual mostra `state_r`, `rk_r`, `rnd`, mas não os valores intermediários).

### 2.2 Forma de onda

- **Amostras por ciclo:** `S` (por exemplo, 8), com pulso de subida rápida e decaimento (exponencial ou gaussiano), centrado a um atraso fixo dentro do ciclo.
- **Atraso por grupo:** registradores logo após a borda de clock, combinacional um pouco depois.
- **Filtro passa-baixa** que imita a banda do osciloscópio ou do sensor (shunt, sonda ou sensor interno têm bandas e ruídos diferentes).
- **Quantização** do conversor (já implementada: `quantize`).

### 2.3 Alternativas ao modelo de atividade (avaliadas)

| Modelo | Prós | Contras | Uso |
|--------|------|---------|-----|
| **Peso de Hamming (HW)** | Simples | Pior para registradores CMOS (confirmado: o ataque com HW falhou em todos os N testados) | Controle negativo |
| **Distância de Hamming (HD)** | Padrão para registradores; já validado | Pesos iguais por bit | **Base** |
| **HD com pesos por bit** | Mais realista | Parâmetros demais, difíceis de justificar sem dados | Variação para a análise de robustez |
| **Perfilado/aprendido** (modelo estocástico ou aprendizado) | Mais próximo de um chip real | Exige traços de referência reais | Fora do escopo |

### 2.4 Parâmetros livres (precisam ser registrados e variados na análise de robustez)

`σ_ruído`, `σ_outros`, pesos `w_g`, fator de glitch, forma e largura do pulso, banda do filtro, bits de quantização, amostras por ciclo, deriva de baixa frequência, jitter residual do clock.

---

## 3. Algoritmo de quebra

### 3.1 Atacantes a implementar

| Atacante | Status | Para que serve | Dificuldade |
|----------|--------|----------------|-------------|
| **CPA** (última rodada e carga inicial) | Feito | Linha de base | — |
| **CPA com alinhamento ideal** (conhece o deslocamento) | Falta (existe na demo antiga) | Pior caso: mostra o que jitter sozinho **não** protege | Baixa |
| **CPA com integração por janela** (soma de amostras em janela deslizante) | Falta | Ataque conhecido contra jitter; o RFTC não testou | Baixa |
| **DTW + CPA** (alinha cada traço a uma referência) | Falta | O RFTC o usa e ele é o mais forte contra clock aleatório de baixa cardinalidade | Média (custo O(n²) por traço) |
| **FFT + CPA** (trabalha no espectro) | Falta | Também testado no RFTC | Baixa |
| **PCA + CPA** | Opcional | Idem | Média |
| **TVLA** (fixo contra aleatório) | Feito | Detecção de vazamento barata | — |
| **Atacante ciente da variante / agnóstico** | Falta | Mede o valor de trocar de configuração | Média |
| **Atacante com perfilamento** | Fora do escopo | — | — |

### 3.2 Escala: milhões de traços

Para configurações fortes (RFTC(3, P) resiste a mais de 4 milhões), guardar todos os traços é inviável. Soluções:

1. **CPA online:** acumular somas (média, variância e covariância) em blocos de traços e calcular a correlação em pontos de verificação. Nenhum traço é guardado.
2. **Extrapolação por correlação:** estimar a correlação `ρ` do palpite certo e converter em número de traços pela fórmula usada na literatura, `N ≈ 3 + 8·(z / ln((1+ρ)/(1−ρ)))²` (Mangard; usada em Kian et al.), com `z = 3,719` para 99,99% de confiança. Vale como estimativa, **assumindo distribuição gaussiana**, e deve ser conferida com ataques diretos onde N for acessível.

### 3.3 Métricas

Taxa de sucesso (chave inteira), traços até divulgação, classificação média da chave, TVLA, e para o atacante com janela de tempo (S3 em diante) o **tempo até recuperar a chave** dado o ritmo de coleta.

### 3.4 Critérios de aceitação

- Contra o baseline, todos os atacantes recuperam a chave.
- Contra jitter, o CPA simples exige muito mais traços que o CPA com alinhamento ideal (replica o fenômeno do RFTC).
- Com M e P crescentes, DTW falha para configurações maiores, como no RFTC (ordem de grandeza).

---

## 4. Algoritmo em estágios

| Estágio | O que é | Agentes | Saída | Critério de saída |
|---------|---------|---------|-------|-------------------|
| **S0** | Alvo estático sem proteção | nenhum | Baseline de traços até divulgação | **Feito** |
| **S1** | **Catálogo de configurações estáticas**, cada uma sempre ligada | nenhum | **Tabela configuração → traços até divulgação → custo** e curva de Pareto | Tabela calibrada no RFTC (§1.5) |
| **S2** | **Políticas simples sem agentes:** sempre mínimo, sempre máximo, aleatória, periódica, limiar fixo | nenhum (regra) | Ranking sob atacantes e orçamentos | Resultados estáveis em 30 sementes |
| **S3** | **Agente único** (baseado em utilidade, com Threat Monitor) numa zona | Zone Agent, Threat Monitor, Attacker | Ganho sobre S2 quando a ameaça é intermitente | Documentado quando o agente vence e quando não vence |
| **S3b** | **Controlador central** com informação completa (referência) | 1 controlador | Limite de referência para S4 | Implementado antes de S4 |
| **S4** | **Multiagente:** N zonas, Resource Manager, **orçamento compartilhado** e **porta de reconfiguração única** (pedidos serializados) | N Zone Agents, Resource Manager, Threat Monitor, Attacker | Comparação S4 contra S3b e S2 | Medidas de mensagens, contenção e escala |
| **S5** | **Aprendizado** nos agentes (bandit ou Q-learning) e **atacante adaptativo** | idem | Política que se adapta a um atacante que reage | Análise de robustez V4 |
| **S6** (opcional) | Validação extra: variantes em VHDL (O3) ou nível de porta (O4); possível placa Zynq com agente em C | — | Verificação de que os custos e vazamentos do modelo são razoáveis | — |

Regras:
- Cada estágio **reaproveita** o gerador de traços e a tabela do S1, e só adiciona decisão.
- S3b entra antes de S4 porque, sem ele, a comparação do SMA fica só contra linhas de base fracas.
- A porta de reconfiguração única (S4) vem da literatura: o ICAP/PCAP é um recurso compartilhado, e isso cria um problema real de coordenação.

---

## 5. Configurações por estágio

### 5.1 Estrutura de arquivos

```
PI/simulacao/
├── config/
│   ├── energy.yaml          # parâmetros do gerador (§2), com faixas para a análise V4
│   ├── catalog.yaml         # catálogo de contramedidas C0..Cn (S1)
│   ├── attackers.yaml       # CPA, CPA alinhado, janela, DTW, FFT, adaptativo
│   ├── s2_policies.yaml
│   ├── s3_agent.yaml
│   ├── s4_system.yaml
│   └── s5_learning.yaml
├── energy/                  # gerador de traços (L0 a L3)
├── attack/                  # atacantes e métricas
├── agents/                  # S2 a S5 (MASPY ou Python)
└── experiments/             # scripts que leem a configuração e geram tabelas e gráficos
```

### 5.2 Conteúdo por estágio

**S1: catálogo (exemplo inicial, a ser calibrado).** Custos de tempo, potência e área vêm do RFTC para RFTC(3, 1024) (1,72x, 1,48x, 1,3x); os demais são **estimativas a medir** nos experimentos ou no Vivado.

| Id | Descrição | Parâmetros | Segurança (alvo da calibração) | Custo |
|----|-----------|------------|--------------------------------|-------|
| C0 | Sem proteção | — | ≈ 2.000 traços | 1,0 |
| C1 | RFTC(1, 4) | M=1, P=4 | ≈ 700 mil (CPA), < 200 mil (DTW) | a medir |
| C2 | RFTC(1, 64) | M=1, P=64 | DTW < 200 mil | a medir |
| C3 | RFTC(1, 1024) | M=1, P=1024 | > 1 milhão | a medir |
| C4 | RFTC(2, 16) | M=2, P=16 | DTW revela | a medir |
| C5 | RFTC(3, 1024) | M=3, P=1024 | > 4 milhões | 1,72x tempo, 1,48x potência, 1,3x área |
| C6 | Variante de S-box (diversidade) | variante `v` | a gerar em O3 | a medir |
| C7 | Mascaramento (função trocada) | tipo de máscara | **evitar conclusões numéricas** (limite de toggle count) | a medir |

**S2:** período de troca (por exemplo, a cada 1k, 10k ou 100k cifragens), probabilidade de troca e limiar de detecção.

**S3:** pesos da utilidade `λ_segurança` e `λ_custo`; ameaça: instante de início do atacante (cedo, tarde), intermitência e taxa de coleta de traços; ruído do Threat Monitor.

**S4:** nº de zonas (2, 4, 8); orçamento total de potência (por exemplo, 1,5x, 2x e 3x o baseline); tempo de reconfiguração de clock (~34 µs, do RFTC) contra bitstream (milissegundos a segundos, Vipin e Fahmy); política de arbitragem da porta única; custo da mensagem.

**S5:** taxa de aprendizado, exploração, horizonte, e tipos de atacante (estático, que persegue a configuração, que sabe a política).

### 5.3 Convenções de experimento

- **30 ou mais sementes** por célula da tabela de experimentos, com intervalos de confiança.
- Cada resultado registra o **hash da configuração** e a semente.
- Resultados negativos (política adaptativa não vence "sempre máximo") são reportados.

---

## 6. Cronograma sugerido (a partir de 31/10)

| Semana | Foco | Entrega |
|--------|------|---------|
| 31/10 – 06/11 | Gerador de energia O2 (L0 a L3) + VHDL instrumentado e V1 | Gerador configurável; verificação V1 e V2 |
| 07/11 – 13/11 | Atacantes (CPA alinhado, janela, DTW, FFT, CPA online) + calibração com o RFTC (V3) | Tabela S1 e curva de Pareto |
| 14/11 – 20/11 | S2 e S3 | Ranking de políticas simples e agente único |
| 21/11 – 27/11 | S3b e S4 (multiagente) + análise de robustez (V4) | Comparação multiagente contra central |
| 28/11 – 04/12 | Fechar resultados, S5 se houver tempo, preparar PF | Entrega e apresentação do PF (04/12) |
| 05/12 – 11/12 | Escrita do A2 | Artigo |

Durante o semestre, a apresentação de andamento do PF vale nota (grupo que não apresenta perde 0,5 no PF), então cada marco acima deve virar algo mostrável.

---

## 7. Riscos e decisões abertas

| Risco | Mitigação |
|-------|-----------|
| O modelo O2 é arbitrário | V4 (robustez do ranking), V1 e V3 como ancoragem, declarar limites |
| Calibrar com um único artigo | Declarar; tentar achar um segundo ponto de referência |
| DTW é lento | Limitar tamanho de traço e usar amostragem; implementar com NumPy |
| Milhões de traços | CPA online e extrapolação com a fórmula de correlação |
| A política adaptativa não vence "sempre máximo" | Reportar como resultado; explorar cenários com orçamento apertado |
| Escopo grande | Fixar S0 a S4 como mínimo; S5 e S6 como extras |
| PI concorrendo com isto | Começar o plano só em 31/10 |

**Decisões em aberto para o grupo:**
- [ ] A interpretação de "estágios" (§4) está correta?
- [ ] Adotar O2 como motor e O3 para validação, como recomendado?
- [ ] Incluir o mascaramento (C7) mesmo sabendo que a simulação por contagem de transições não o avalia bem?
- [ ] O grupo tem acesso a Vivado (licença) para medir área, Fmax e potência estimada por variante?
- [ ] Haverá placa Zynq para o estágio opcional S6?

---

## 8. Adendo (21/10/2026): decisão de usar nível de porta com atrasos (O4) para as variantes físicas

O grupo quer **várias implementações dos estágios da cifra** e **várias compilações do mesmo circuito** (mesma função, implementação física diferente). Isso é a técnica de **diversidade de implementação** (Hettwer et al., DATE 2019: mesma RTL, posicionamento e roteamento diferentes, trocados por reconfiguração parcial; os autores reportam, em Zynq UltraScale+, ganho de resistência de **pelo menos 2x**, segundo o resumo do DATE; não li o artigo). O motor O2 (heurístico) continua como motor de produção; O4 passa a gerar os **traços das variantes físicas**.

### 8.1 Eixos de variação (não confundir)

| Eixo | O que muda | Muda a função? | Efeito esperado no vazamento |
|------|-----------|----------------|-------------------------------|
| **Variante de RTL** (estrutura lógica de um estágio, por exemplo, S-box por tabela contra campo composto) | Portas e profundidade lógica | Não | Muda a lógica combinacional, os glitches e os atrasos |
| **Compilação** (mesma RTL, diretivas e restrições de posição diferentes) | Posicionamento, roteamento e atrasos | Não | Muda **quando** cada sinal comuta e os glitches. **Não muda** o valor dos registradores |

Como a distância de Hamming do registrador de estado é a mesma em qualquer compilação, **a diversidade física só pode atuar na parte combinacional e no tempo**. O efeito sobre o CPA tende a ser **modesto** (a ordem de 2x reportada, não ordens de grandeza como o clock aleatório do RFTC). Dimensionar a expectativa assim.

### 8.2 Caminho de ferramentas (verificado em buscas, não testado aqui)

- **A simulação com atrasos do Vivado é só em Verilog.** O netlist temporizado e o SDF são gerados em Verilog; para VHDL, a documentação oferece apenas simulação funcional pós-síntese e pós-implementação **sem SDF**.
- **O GHDL tem suporte a SDF muito limitado** (o manual o descreve como prova de conceito, subconjunto do SDF 2.1, sem nomes hierárquicos). **Não é um caminho confiável.**
- Portanto: **escrever o projeto em VHDL é aceitável** (o Vivado sintetiza VHDL), mas a **simulação temporizada** roda sobre o **netlist Verilog** gerado, no **xsim** (simulador do próprio Vivado) ou em outro simulador de Verilog com as bibliotecas da Xilinx. O testbench pode ser em Verilog (mais seguro) ou misto (a conferir).
- **Licença:** segundo a documentação AMD (UG909, 2025.2), a reconfiguração parcial (DFX) **não exige licença específica** em nenhuma edição do Vivado. **Dispositivos:** na edição gratuita (ML Standard) o UG973 lista um subconjunto de Zynq-7000 que **inclui o XC7Z020**; fontes de terceiros divergem. **Conferir a tabela da versão que for instalada.**
- Não há Vivado instalado nesta máquina. O grupo tem acesso institucional? Precisa ser confirmado.

### 8.3 Fluxo proposto para as variantes físicas

1. Definir o **módulo sob teste** (um estágio, por exemplo, a camada SubBytes ou uma rodada completa) com interface fixa.
2. Gerar **K compilações** do mesmo RTL variando diretivas de posicionamento e roteamento e restrições de posição (Pblock/LOC). Conferir as opções exatas de diretiva no Vivado instalado.
3. Para cada compilação, exportar **netlist Verilog temporizado + SDF** e simular com entradas aleatórias, gravando a atividade com carimbo de tempo (VCD ou SAIF).
4. Converter a atividade em **traço com resolução abaixo do ciclo** (pulsos ponderados, como em §2) e adicionar a medição simulada (§1.3, L3).
5. **Primeiro teste, barato:** as compilações produzem traços **distinguíveis**? (TVLA ou diferença de médias entre duas compilações com entradas iguais.) Se não, a diversidade física não terá efeito mensurável e vale parar aqui.
6. **Segundo teste:** CPA e atacantes da §3 contra cada compilação e contra a **mistura** delas (o atacante vê traços alternados). Comparar traços até divulgação.
7. Alimentar a **tabela S1** (§4) com as variantes e seus custos (área, Fmax e potência estimada do Vivado, por compilação).

### 8.4 Custos e riscos específicos

| Risco | Mitigação |
|-------|-----------|
| Efeito pequeno (2x) comparado a outras contramedidas | Tratar a diversidade física como **componente do catálogo**, não como defesa principal; combinar com chave por zona e outras |
| Cada compilação leva minutos, e a simulação com atrasos é lenta | Limitar K (por exemplo, 5 a 10) e o nº de cifragens por compilação; usar TVLA antes do CPA |
| Resultado depende do atacante mapear o modelo certo | Testar atacante ciente e agnóstico da variante (§3) |
| Atrasos são estimativas, não física | Declarar a limitação; V4 (robustez do ranking) continua valendo |
| Mascaramento continua não conclusivo com contagem de transições | Não tirar conclusões numéricas de C7 |
| Dependência do Vivado | Confirmar acesso antes de investir; plano B: variantes de RTL em O3 (GHDL) sem atrasos, só para a parte lógica |

### 8.5 Atualização (21/10/2026): disponibilidade e licença do Vivado

Fontes: AMD (UG909, 2026.1), resultados de busca, explicador de terceiros (bard0.com) e discussão do fórum EEVblog. **Nada foi instalado nem testado.**

- **Vivado 2026.1 (23/06/2026; 2026.1.1 em 10/09/2026)** trocou a edição Standard (sem licença) por camadas **Basic (gratuita), Core, Pro, Enterprise e Gold**.
- **Basic:** gratuita, mas exige **arquivo de licença gerado no site da AMD e renovado a cada 12 meses**. Cobre **todas as famílias 7 Series** (inclui Zynq-7000 e XC7Z020) segundo a tabela da AMD citada em buscas e no fórum. Não suporta versões menores (por exemplo, 2026.1.1) nem acesso a versões anteriores a 2026.1 (só Pro, Enterprise e Gold).
- **Limitações da Basic segundo o explicador de terceiros (a confirmar na tabela oficial):** simulação **xsim limitada** (o limite não foi especificado), sem relatórios de QoR, sem bitstreams criptografados e **sem DFX**.
- **DFX (reconfiguração parcial): fontes conflitam.** O UG909 (2026.1) diz que nenhum código de licença específico é necessário em todas as edições; o explicador de terceiros e um usuário do fórum dizem que a Basic não inclui DFX. **Não resolvido.** Para **simular** variantes, DFX não é necessário (só para trocar bitstreams em placa).
- **Sistema operacional:** fontes divergem sobre a Basic ser só para Windows; a máquina do grupo é Windows.
- **Versões antigas:** versões anteriores (como a 2025.2) usavam a edição Standard, que não exigia licença. Não consegui confirmar se ainda estão disponíveis para download sem conta ou licença.
- **Criar a conta e gerar a licença devem ser feitos por um membro do grupo**, não por mim.

**Alternativa de código aberto (não verificada):** Yosys + nextpnr, com binários para Windows 10/11 no OSS CAD Suite. A ideia é obter "compilações diferentes" variando a **semente** do posicionamento e simular o netlist com Icarus Verilog. **Não confirmei** as opções `--seed`, `--sdf` e a escrita de netlist pós-roteamento, nem se o Icarus vem no pacote do Windows. Os alvos são iCE40 e ECP5 (não Xilinx), então os resultados valem para **outra família de FPGA**.
