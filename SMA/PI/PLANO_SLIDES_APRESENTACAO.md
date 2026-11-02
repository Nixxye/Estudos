# Plano de slides — Apresentação do PI (10 min, 4 pessoas)

Baseado no PDF `SMA - PI.pdf` (PP + PEAS + Prometheus + interação já escritos) e no protótipo MASPY (`aes_dpr_prototype/`). ~10 slides, **~60-70 s por slide**, com folga de ~30 s no total para perguntas/transição. Ajuste os nomes dos responsáveis — usei a divisão de tarefas do checklist (Jean: ambiente/Walker/protótipo; Thiago: Prometheus; Felipe e Thiago: PEAS/tipos; Emerson: Walker/protótipo).

**Regra de ouro para 10 min:** nada de ler as tabelas PEAS na íntegra. O PDF completo já existe — os slides mostram só os pontos que sustentam a fala. Quem assistir que leia os detalhes no PDF.

---

## Divisão sugerida (2,5 min por pessoa)

| Quem | Slides | Tempo |
|---|---|---|
| **Felipe** | 1–3 (abertura, contexto, objetivo) | ~2 min |
| **Thiago** | 4–5 (cenário/catálogo, Prometheus) | ~2,5 min |
| **Emerson** | 6–7 (tipos de agente, protocolo de interação) | ~2 min |
| **Jean** | 8–10 (ambiente Vivado, protótipo/Walker, limitações e fechamento) | ~2,5–3 min |

Redistribuam como quiserem — o que importa é a soma ficar em 10 min e cada um falar só do que apresentou/implementou.

---

## Slide 1 — Capa (10 s)
- Título do projeto: **SMA para reconfiguração parcial de um AES-128 contra análise de potência (CPA)**
- Disciplina, grupo (4 nomes), data
- *Sem falar muito aqui — só situar.*

## Slide 2 — O problema, em 3 frases (40 s)
- AES é seguro **matematicamente**, mas o circuito vaza energia dependente dos dados (canal lateral)
- CPA: testa 256 palpites por byte, reduz 2¹²⁸ para 16×256
- **Agravante em FPGA compartilhada:** ataque remoto, só com a própria lógica do chip, já demonstrado em nuvem (Amazon EC2 F1) — sem precisar tocar no hardware
- *Nota de apresentação:* se alguém perguntar "quão sério é isso", mencionar que o grupo já simulou e recuperou uma chave (slide 9).

## Slide 3 — Objetivo (30 s)
- Propor um **SMA** que gerencie **quando**, **qual setor** e **para qual módulo** reconfigurar um AES-128 dividido em setores
- Meta: manter a resistência ao CPA com **menor custo de reconfiguração** que trocar sempre, ou só reagir de um jeito fixo ao detectar ataque

## Slide 4 — Cenário (50 s)
- FPGA com AES-128 em **N setores** (estágios do circuito)
- Cada setor tem um **catálogo fechado** de módulos — mesma função, vazamento diferente (ex.: S-box em memória vs. em lógica)
- Troca em tempo de execução via **bitstream parcial pela ICAP** (1 reconfiguração por vez)
- Adversário faz parte do ambiente: acumula traços e aplica CPA
- *Dica visual: usar um esquema simples (setores em fileira, um "catálogo" ao lado de cada um).*

## Slide 5 — Modelagem Prometheus (40 s)
- Mostrar o **diagrama de visão geral** (percepts → Trigger → sinal → Escolha → trocarmodulo; setores → melhor troca → Escolha)
- Falar só a ideia: **2 níveis** — decisão (Trigger + Escolha) e setores
- *Esse é o slide mais visual — deixar o diagrama carregar o peso, falar pouco.*

## Slide 6 — Os 3 tipos de agente (50 s)
Uma linha por agente, sem ler o PEAS inteiro:
- **Agente Trigger** — baseado em objetivos: garantir que nenhum setor fique exposto além do limite; decide **quando**
- **Agente de Escolha** — baseado em utilidade: escolhe **qual** setor trocar, dentro do orçamento e da ICAP única
- **Agentes de Setor** (um por setor) — baseados em utilidade: decidem **para qual módulo**, com a fórmula `U = w₁·ganho_segurança − w₂·custo_reconfig − w₃·custo_operação`
- *Se sobrar tempo, mostrar a fórmula; se não, só citar que existe.*

## Slide 7 — Como eles conversam (40 s)
- Protocolo inspirado no **Contract Net**, mas **propostas sempre atualizadas** (setores não esperam anúncio) — reação mais rápida
- 5 passos resumidos em 1 frase cada: setor propõe → Escolha guarda a melhor → Trigger dispara sinal → Escolha executa a troca pela ICAP → ambiente atualiza e o ciclo reinicia
- *Usar o mesmo diagrama do Prometheus ou um fluxograma simples; não reler os 5 passos do PDF palavra por palavra.*

## Slide 8 — Ambiente de simulação: Vivado (50 s)
- O ambiente **não é abstrato**: vem de simulação real no Vivado (Zynq-7020)
- Energia estimada ciclo a ciclo a partir da atividade do circuito simulado
- **Resultado preliminar:** AES sem proteção, chave recuperada com **~1.600 mensagens cifradas** via CPA
- Esses números (custo de reconfiguração, área, tempo) é que alimentam o catálogo dos setores
- *Esse é o gancho que conecta o trabalho de simulação (Jean) com o SMA — vale destacar que não é hipotético.*

## Slide 9 — Protótipo em MASPY (40 s)
- Mostrar o protótipo (`aes_dpr_prototype/`): Trigger, Escolha e 2 Agentes de Setor já implementados e rodando
- Se der tempo/for estável: **rodar ao vivo** ou mostrar um print do log (`listener_log=True`) com uma troca acontecendo
- Deixar claro: **ambiente e parâmetros ainda são simulados** — não há conexão com Vivado/CPA/ICAP reais nesta versão
- *Ter um vídeo/print gravado como plano B, para não depender de live demo em 10 min.*

## Slide 10 — Limitações e próximos passos (30 s)
- O que falta: ligar o catálogo aos dados reais do Vivado, política de aprendizado/ajuste dos pesos, mais setores
- Isso vira o **Projeto Final**
- Agradecimentos / perguntas

---

## Checklist antes de apresentar
- [ ] Cronometrar um ensaio real — 10 min é curto, cortar texto dos slides para bullets curtos
- [ ] Ter o diagrama Prometheus em alta resolução (o `.drawio` já existe, exportar como PNG/PDF antes)
- [ ] Decidir: demo ao vivo do MASPY ou só vídeo/print (recomendo ter o print pronto mesmo que tente ao vivo)
- [ ] Cada um treinar só o próprio trecho cronometrado, não o texto inteiro
