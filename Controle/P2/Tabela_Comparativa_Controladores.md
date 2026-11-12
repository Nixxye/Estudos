# Tabela comparativa: P, PI, PD, PID, Avanço e Atraso

## 1. O que cada controlador adiciona ao lugar das raízes

| Controlador | C(s) | Polos que adiciona | Zeros que adiciona | Onde fica o zero |
|---|---|---|---|---|
| **P** | Kp | nenhum | nenhum | não tem |
| **PI** | Kp + Ki/s = Kp(s + Ki/Kp)/s | **1 em s = 0** | **1** | −Ki/Kp |
| **PD** | Kp + Kd·s = Kd(s + Kp/Kd) | nenhum (ideal) | **1** | −Kp/Kd |
| **PID** | Kp + Ki/s + Kd·s = (Kd·s² + Kp·s + Ki)/s | **1 em s = 0** | **2** (raízes de Kd·s² + Kp·s + Ki) | raízes do numerador |
| **Avanço (LEAD)** | (s + z)/(s + p), com 0 < α < 1 | 1 (real, longe da origem) | 1 | **mais perto** da origem que o polo |
| **Atraso (LAG)** | (s + z)/(s + p), com α > 1 | 1 (real, perto da origem) | 1 | **mais longe** da origem que o polo |

## 2. Para que serve e o que muda na resposta

| Controlador | Efeito principal | Efeito no erro estacionário | Efeito na resposta transitória | Problema / cuidado |
|---|---|---|---|---|
| **P** | muda só o ganho: o polo anda sobre o lugar já existente | reduz o erro, não zera | só anda sobre as raízes que a planta já tem | não leva o polo a pontos fora do lugar original |
| **PI** | zera o erro ao degrau (sobe o tipo em 1) | **zera** (tipo + 1) | o polo em 0 puxa o lugar para a direita (mais lento, mais oscilação); o zero compensa | o zero **aumenta o overshoot**; precisa ajuste fino |
| **PD** | puxa o lugar para a esquerda: mais amortecimento, menor ts | não muda (não altera o tipo) | melhora Mp e ts | amplifica ruído; derivador puro não existe fisicamente (filtro com polo a ≥ 10z) |
| **PID** | junta as duas coisas | zera (como o PI) | melhora (como o PD) | três ganhos para ajustar; sintonia por Ziegler-Nichols dá overshoot alto |
| **Avanço** | aproxima o PD, sem ganho infinito em alta frequência | pouco | melhora Mp e ts | |
| **Atraso** | aproxima o PI, sem polo exato em 0 | melhora (Kp, Kv ou Ka maior) | quase não mexe nos polos dominantes | resposta mais lenta se mal escolhido |

## 3. O que vem direto e o que precisa ser calculado (o método dos exercícios)

| | **PD** (Q1) | **PI** (Q2) | **PID** (Q3, Ziegler-Nichols) |
|---|---|---|---|
| Alvo s₀ | **sim**: σ = 4/ts, ζ pelo Mp, ωd | **sim**, igual | **não precisa**: usa só Ku e Pu |
| Zero | **calculado** pela condição de ângulo: θz = Σθpolos − 180° | **calculado** pela condição de ângulo; o **polo em 0 entra na soma** dos ângulos | já vem da tabela (Ti, Td) |
| Ganho | **calculado** pela condição de módulo: Kd = ∏\|s₀ − pk\| / (K_G·\|s₀ + z\|) | **calculado** pela condição de módulo (o polo em 0 entra no produto) | já vem da tabela: Kp = 0,6·Ku |
| Os outros ganhos | **direto**: Kp = z·Kd | **direto**: Ki = z·Kp | **direto**: Ki = Kp/Ti, Kd = Kp·Td |
| Entrada do método | planta e especificações | planta e especificações | Ku (Routh) e Pu = 2π/ωu (equação auxiliar) |
| Precisa de Routh? | não | não | **sim** (Ku e ωu) |
| Precisa ajuste fino? | sim (levemente) | sim (o zero eleva o Mp) | sim (Mp de ~59 % antes do ajuste) |

## 4. Resultado numérico de cada questão

| | Projeto pelo método | Depois do ajuste fino |
|---|---|---|
| **Q1 PD** | z = 13,94; Kd = 27,94; Kp = 389,2 → Mp 14,5 %, ts 1,013 s | Kd = 28, Kp = 364 → Mp 12,1 %, ts 0,77 s |
| **Q2 PI** | z = 15,26; Kp = 4; Ki = 61 → Mp 17,7 %, ts 0,37 s | Kp = 5, Ki = 30 → Mp 3,75 %, ts 0,454 s |
| **Q3 PID** | Ku = 96, Pu = 0,811 s; Kp = 57,6, Ki = 142, Kd = 5,84 → Mp 59 % | Kp = 45, Ki = 60, Kd = 16 → Mp 8,6 %, ts 2,15 s |

## 5. Regra para decidir qual usar

| Se o problema pede... | Use |
|---|---|
| só ajustar a rapidez/amortecimento, erro já aceitável | **PD** (ou avanço) |
| erro estacionário zero, resposta não precisa ser rápida | **PI** (ou atraso) |
| erro zero e boa resposta transitória | **PID** |
| planta de 1ª ordem e polos desejados complexos | **PI ou PID** (P não chega ao alvo, o lugar fica no eixo real) |

## 6. Passo a passo para projetar qualquer controlador

O projeto por lugar das raízes (Aulas 13 e 14, Relatório 04, LEAD e LAG da Aula 10) segue **a mesma sequência de 7 etapas**. As etapas **1, 2, 5 e 6 são iguais** para todos. As etapas **3, 4 e 7 mudam** conforme o controlador, e cada uma tem sua seção abaixo. O PID por tabelas (Ziegler-Nichols, Aula 15) tem outro caminho e vem separado.

| Etapa | O que se faz | Igual para todos? |
|---|---|---|
| 1 | Traduzir Mp e ts em polos dominantes `s₀` | **sim** |
| 2 | Verificar se só P resolve (fase em `s₀`) | **sim** |
| 3 | Escolher o controlador e achar a **posição do zero** (ou dos parâmetros) | **muda** |
| 4 | Calcular o **ganho** (condição de módulo) | **muda** |
| 5 | Calcular o erro estacionário | **sim** |
| 6 | Simular a resposta ao degrau | **sim** |
| 7 | **Ajuste fino**, se Mp ou ts não atenderam | **muda** |

### 6.1 Etapas iguais para todos

**Etapa 1: polos dominantes desejados.**

- `ζmin = −ln(Mp)/√(π² + ln²(Mp))` (com Mp em fração; 15 % → 0,517).
- `σ = ζωn = 4/ts` (2 %), `ωn = σ/ζmin`, `ωd = ωn√(1 − ζ²)`.
- **`s₀ = −σ ± jωd`**. Exemplo da Aula 13: `Mp = 20 %`, `ts = 4 s` → `s₀ = −1 ± j1,93`.

**Etapa 2: só P resolve?** Some os ângulos dos polos de `G` até `s₀` (cada vetor sai do polo e **chega** em `s₀`):

`∠G(s₀) = Σ(ângulos dos zeros) − Σ(ângulos dos polos)`

- Se der **±180°**, `s₀` está no lugar das raízes: P pode bastar. Calcule `Kp = 1/|G(s₀)|` e vá à etapa 5.
- Se **não**, `s₀` não pertence ao lugar: precisa de zero (PD) ou de polo em 0 + zero (PI). Exemplos: Aula 13, `−234,8° ≠ −180°`; Aula 14, `−69,8° ≠ −180°`.
- **P também precisa passar no erro** (etapa 5): na Q2, P cumpre Mp e ts, mas deixa 50 % de erro.

**Etapa 5: erro estacionário.** `E(s) = X(s)/(1 + C(s)G(s))` e `e(∞) = lim s·E(s)`. Pelo **tipo** de `C·G` (polos em `s = 0`): tipo 0 dá `e = 1/(1 + Kp)` ao degrau; tipo ≥ 1 dá 0. O PI e o PID sobem o tipo em 1. Se o erro for inaceitável, troque de controlador.

**Etapa 6: simular.** `T = feedback(C*G,1); step(T)`. Observe Mp, ts e o valor final.

### 6.2 Controlador P (etapas 3, 4 e 7)

- **Etapa 3:** não há zero a escolher. `C = Kp`.
- **Etapa 4:** `Kp = 1/|G(s₀)|` (o ganho que leva o polo ao ponto, se ele está no lugar).
- **Etapa 7:** mexer só no `Kp`. O polo anda sobre o lugar da planta, e Mp e ts variam juntos (mais `Kp`: menos ts, mais Mp).
- **Cuidado:** só funciona se a fase em `s₀` for ±180° e o erro for aceitável.

### 6.3 Controlador PD: `C = Kd(s + z)`, `z = Kp/Kd` (Aula 13, Q1)

- **Etapa 3: zero pela fase.** `θz = Σθpolos de G − 180°`, e `z = σ + ωd/tan θz`. (Aula 13: `Σθpolos = 234,8°`, `θz = 54,8°`, `z = 2,36`.) O zero do PD está em `−z`, então a parte horizontal do vetor até `s₀` é `z − σ`.
- **Etapa 4: ganho `Kd` pelo módulo.** `Kd = ∏|s₀ − pk| / (K_G · |s₀ + z|)`, onde `K_G` é o ganho da planta (em `2/s²` vale 2). Depois **`Kp = z·Kd`**. (Aula 13: `Kd = 4,72/(2·2,36) = 1`, `Kp = 2,36`.)
- **Etapa 7: ajuste fino.** O zero aumenta o overshoot além do previsto pelo par dominante (Aula 13: 32 % em vez de 20 %). **Mantenha `z` e aumente o ganho** (Aula 13: `Kd = 2,58`, `Kp = 6,08`, Mp 19,7 %), ou mova o zero.
- **Erro:** o PD **não** muda o tipo; zero só se a planta já tiver integrador.
- **Prático:** o derivador puro não existe; usa-se `(Kp + Kd·s)/(1 + s/a)`, com polo `a ≥ 10z`.

### 6.4 Controlador PI: `C = Kp(s + z)/s`, `z = Ki/Kp` (Aula 14, Q2)

- **Etapa 3: zero pela fase, com o polo em 0 na soma.** Some os ângulos dos polos de `G` **e** o do polo em 0 do PI; `θz = Σ − 180°`; `z = σ + ωd/tan θz`. (Aula 14: `126,3° + 69,8°`, `θz = 16,1°`, `z = 45,7`.)
- **Etapa 4: ganho `Kp` pelo módulo**, com o polo em 0 como mais uma distância no numerador: `Kp = |s₀|·∏|s₀ − pk| / (K_G · |s₀ + z|)`. Depois **`Ki = z·Kp`**. (Aula 14: `Kp = 13,5·11,6/39,2 = 4`, `Ki = 182,6`.)
- **Etapa 7: ajuste fino.** O zero e o polo em 0 aumentam o overshoot. **Reduzir o ganho** (Aula 14: `Kp = 3,2`, `Ki = 146,2`) ou **aproximar o zero da origem** (Q2: `Kp = 5`, `Ki = 30`). Não há receita única: teste por simulação.
- **Erro:** o PI zera o erro ao degrau (sobe o tipo em 1). É a razão de usá-lo.

### 6.5 Controlador PID por ganho limite (Ziegler-Nichols, Aula 15, Q3)

**Não passa pelas etapas 1 a 4:** não há alvo `s₀`. Em vez disso:

- **Etapa 3 (medir):** só P (`Ki = Kd = 0`). Polinômio característico `A(s) + K·B(s) = 0`; **Routh com `K` literal**: o ganho `Kcr` zera a linha s¹; a equação auxiliar (linha s²) dá `ωcr`; `Tcr = 2π/ωcr`. (Q3: `Kcr = 96`, `Tcr = 0,811 s`.)
- **Etapa 4 (tabela):** `Kp = 0,6·Kcr`, `Ti = 0,5·Tcr`, `Td = Tcr/8`; depois `Ki = Kp/Ti` e `Kd = Kp·Td`. (Q3: `57,6`, `142`, `5,84`.)
- **Etapa 7: ajuste fino.** O ZN dá overshoot alto (os slides dizem ζ ≈ 0,21, Mp ≈ 50,9 %). Use a tabela de efeitos: reduzir `Kp`, aumentar `Kd`, reduzir `Ki` (Q3: `45`, `60`, `16`, Mp 8,6 %).
- **Alternativa mais estável:** Tyreus-Luyben, `Kp = Kcr/2,2`, `Ti = 2,2·Tcr`, `Td = Tcr/6,3`.

### 6.6 Controlador PID por curva de reação (Aula 15)

- **Etapa 3 (medir):** degrau na planta em malha aberta; na curva em S, tangente no ponto de maior derivada → `K` (valor final), `L` (tempo morto), `T` (constante de tempo). Adequado para `0,1 ≤ L/T ≤ 0,3`.
- **Etapa 4 (tabela):** ZN: `Kp = 1,2T/(K·L)`, `Ti = 2L`, `Td = 0,5L`; `Ki = Kp/Ti`, `Kd = Kp·Td`. (Aula 15: `K = 1`, `L = 0,2`, `T = 2` → `12`, `30`, `1,2`.) Outras tabelas: Cohen-Coon (`L/T` alto) e CHR (Mp 0 % ou 20 %).
- **Etapa 7:** como em 6.5.

### 6.7 Compensador por avanço de fase, LEAD: `Gc = Kc(s + z)/(s + p)`, `0 < α < 1` (Aula 10)

- **Etapa 3: arbitra-se o zero e calcula-se o polo.** `θp = θz − Σθpolos de G + 180°`, e `p = σ + ωd/tan θp`. Se `p` cair perto dos polos da planta, ele pode dominar: **mude o zero** e refaça. (Aula 10: zero em −4 deu `p = 7,42` (perto demais); zero em −5 deu **`p = 9,63`**.)
- **Etapa 4: ganho pelo módulo.** `Kc·K = ∏|s₀ − pk| · |s₀ + p| / |s₀ + z|` (aqui `|s₀ + p|` entra no numerador, porque `p` é polo). (Aula 10: `Kc·K = 30,9`.) Parâmetros: `T = 1/z`, `α = z/p = 0,52`.
- **Etapa 7:** mudar o zero e recalcular o polo.

### 6.8 Compensador por atraso de fase, LAG: `Gc = Kc(s + 1/T)/(s + 1/(αT))`, `α > 1` (Aula 10)

Objetivo: **só reduzir o erro**, sem mexer nos polos dominantes. Não há alvo `s₀`.

- **Etapa 3 (escolher `α` e `T`):** o slide dá `T = α = 10`. Critério (🧩, lógica de projeto, não está nos slides): `α` pelo erro desejado, `Kc·α·G(0) = 1/e_d − 1`; `T` grande, para o par polo-zero (`−1/T` e `−1/(αT)`) ficar bem perto da origem.
- **Etapa 4:** o ganho entra na própria fórmula do erro: `e(∞) = 1/(1 + Kc·α·G(0))`. (Aula 10: `Kc = 5`, `K = 1` → `e = 3/203 = 0,015`.)
- **Etapa 7:** confira a estabilidade por **Routh** com o compensador (o limite de `Kc·K` cai de 30 para ≈ 27,2) e o custo, uma resposta mais lenta.

### 6.9 Resumo: o que muda em cada etapa

| Etapa | P | PD | PI | PID (tabelas) | LEAD | LAG |
|---|---|---|---|---|---|---|
| 1 (alvo `s₀`) | sim | sim | sim | **não** | sim | **não** |
| 3 | nenhuma | zero pela fase | zero pela fase (+ polo em 0) | **medir** `Kcr`, `Tcr` (ou `K`, `L`, `T`) | zero arbitrado, polo pela fase | escolher `α`, `T` |
| 4 | `Kp = 1/|G(s₀)|` | `Kd` pelo módulo; `Kp = z·Kd` | `Kp` pelo módulo; `Ki = z·Kp` | **tabela** | `Kc·K` pelo módulo | pelo erro |
| 5 (erro) | `1/(1 + Kp)` | igual ao da planta | **zero** | **zero** | igual ao da planta | reduzido |
| 7 (ajuste) | mexer em `Kp` | `Kd` ou `z` | `Kp` e `z` | `Kp`↓, `Kd`↑, `Ki`↓ | mudar o zero | Routh |

> Tudo aqui vem do que foi aplicado nas questões e nos slides das Aulas 10, 12, 13, 14 e 15. A classificação de avanço e atraso usa a convenção padrão (confira com o α dos seus slides da Aula 10). O Ziegler-Nichols está na Aula 15.
