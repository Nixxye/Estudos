# Tutorial: como resolver as questões das listas (do jeito do professor Guisso)

Cobre **Lista 01**, **Lista 02**, **Relatório 1** (final dos slides da Aula 6) e **Relatório 2** (lugar das raízes). Teoria em [Resumo_Controle_P1.md](Resumo_Controle_P1.md); respostas passo a passo em [Gabarito_Controle_P1.md](Gabarito_Controle_P1.md) e [Gabarito_Relatorio2_Controle.md](Gabarito_Relatorio2_Controle.md); MATLAB em [guia_P1_matlab.m](guia_P1_matlab.m).

## Índice

0. [Qual receita usar? (decisão rápida)](#s0)
1. [Regras do professor](#s1)
2. [A. Simplificar diagrama de blocos](#a)
3. [B. Circuitos → função de transferência (RC, RLC, amp-op)](#b)
4. [C. Erro em regime permanente](#c)
5. [D. 1ª e 2ª ordem: projeto e análise](#d)
6. [E. Estabilidade por Routh-Hurwitz (inclusive faixa de K)](#e)
7. [F. Lugar das raízes](#f)
8. [G. Exemplos resolvidos do Relatório 1](#g)
9. [H. Conferência no MATLAB](#h)
10. [I. Erros que mais custam pontos](#i)
11. [Checklist final](#chk)

<a id="s0"></a>
## 0. Qual receita usar?

| O enunciado pede... | Receita |
|---|---|
| "função de transferência de malha fechada C/R" de um diagrama; "simplifique o diagrama" | [A](#a) (e [G, Q2](#g)) |
| "C(s) em função de R(s) e D(s)" (duas entradas) | [A](#a) (superposição) |
| "função de transferência Eo/Ei do circuito" | [B](#b) |
| "e(∞) para degrau/rampa/parábola" | [C](#c) |
| "fator de amortecimento", "overshoot", "tempo de acomodação/subida/pico", "encontre C (ou R, L) para..." | [D](#d) |
| "faixa de K para estabilidade", "o sistema é estável?", "quantos polos no semiplano direito?" | [E](#e) |
| "esboce o lugar das raízes", "assíntotas", "ponto de saída", "cruzamento no eixo imaginário", "K no ponto s₀" | [F](#f) |
| "confirme no MATLAB" | [H](#h) |

<a id="s1"></a>
## 1. Regras do professor

1. **Tudo vem de `T = G/(1+GH)`** (realimentação negativa). Em diagramas: numerador = produto do ramo direto; denominador = 1 + produto ao redor do laço.
2. **Maiúsculas = Laplace, minúsculas = tempo.** Função de transferência sempre com **condições iniciais nulas**.
3. **A estabilidade vem do denominador de malha fechada** (`1 + GH`), nunca do numerador.
4. **Erro em regime só existe se o sistema for estável** (verifique antes).
5. **Polos e zeros de MALHA ABERTA** é o que se marca no lugar das raízes.
6. **Escreva a resposta fatorada e limpa** (como na "Solução" da Lista 02) e **confira no MATLAB** quando o enunciado pedir.

---

<a id="a"></a>
## A. Simplificar diagrama de blocos

### Caminho 1: uma equação por somador (mais seguro)

1. **Dê nome a cada sinal** na saída de cada somador/bloco (E, F, U, X...).
2. **Uma equação por somador**, com os sinais do diagrama. Atenção a **onde cada H lê o sinal** (saída final C, ou saída de um bloco interno).
3. **Equação da saída** (último bloco).
4. **Substitua** até sobrar só a saída e as entradas.
5. **Isole** C/R. Com duas entradas (R e D): isole C e deixe `C = (...)R + (...)D`, ou use superposição (zere uma por vez).
6. **Fatore** e compare com os "limites" (ex.: sem H, sem laço).

### Caminho 2: regras da Aula 5

1. Blocos em **série** → multiplique. Em **paralelo** (mesmo ponto de partida, somam no mesmo somador) → some (com os sinais do somador).
2. **Laço mais interno** → `G/(1+GH)`.
3. Se nada se encaixa, **mova somador ou ponto de ramificação** (tabela do Resumo §3): somador para depois do bloco G multiplica o que entra por G; somador para antes divide por G; ramificação para depois de G leva 1/G no ramo; ramificação para antes leva G.
4. Repita de dentro para fora.

### Método de Mason (atalho, se o professor aceitar)

`T = Σ(caminho direto × (1 − laços que não o tocam)) / (1 − Σ ganhos de laço)`. Com realimentação negativa o ganho do laço é **negativo**, então o denominador fica `1 + (produto do laço)`. Serve para conferir o resultado do caminho 1.

### Quando há duas entradas

`C = T_R·R + T_D·D`. `T_R`: zere D. `T_D`: zere R. Uma perturbação que entra **depois** do bloco da planta é dividida por `1 + GcGp` (a malha fechada a reduz).

### Padrões recorrentes

| Padrão | Resultado |
|---|---|
| Ramo direto `G`, H lê C | `G/(1+GH)` |
| H lê a saída de **um bloco interno** (não de C) | escreva equações; **não** aplique a fórmula direto |
| Dois blocos em paralelo no ramo direto | `(G1+G2)` no lugar de `G` |
| Dois blocos de realimentação em paralelo com sinais + e − | `H = H1 − H2` (o sinal do somador vale) |
| Ramo que sai de R e entra num somador depois do somador do laço | `(1 + G1)` multiplicando (feed-forward) |
| Sem laço de realimentação | `T` = soma dos caminhos (ex.: `G1G2 + G2 + 1`) |

Exemplos resolvidos: [Gabarito_Controle_P1.md](Gabarito_Controle_P1.md) (Lista 01 Q1, Q2 e Lista 02 Q1 a-d) e [G, Q2](#g).

---

<a id="b"></a>
## B. Circuitos → função de transferência

### B.1 Circuitos passivos (R, L, C)

1. **Componentes em Laplace:** R → `R`; L → `sL`; C → `1/(sC)`. Fontes: `Ei(s)`.
2. **Identifique a topologia:** braços em série e em paralelo.
3. **Divisor de tensão** (saída sem carga): `Eo/Ei = Z_saída/(Z_total)`.
   Se houver um divisor de corrente ou malhas, escreva **lei das malhas/nós** em Laplace e isole.
4. **Simplifique:** escreva cada Z como fração, cancele fatores comuns (`s`), remova frações dentro de frações.
5. **Forma padrão:** `numerador(s)/denominador(s)`.
6. **Sanidade:** em `s → 0` (DC): capacitor aberto, indutor em curto. Em `s → ∞`: capacitor curto, indutor aberto. O resultado precisa concordar.

Exemplos: L1-Q3 (R1-C1 série, braço R2-C2 → `Z2/(Z1+Z2)`); RLC série (Relatório 1 Q1):
`Vc/Vi = (1/sC)/(R + sL + 1/sC) = (1/LC)/(s² + (R/L)s + 1/LC)`.

### B.2 Circuitos com amplificador operacional

1. **Identifique a configuração.** Inversor: `Vo/Vi = −Z_f/Z_in`, onde `Z_in` é a impedância **entre a entrada e o terminal −** e `Z_f` a **de realimentação** (saída ao terminal −). O terminal + está no terra.
2. **Escreva Z_in e Z_f em Laplace** (cada um é série/paralelo de R e C).
3. **Substitua e simplifique.**
4. **Vários estágios em cascata: multiplique** as funções de cada estágio (ideal: um estágio não carrega o anterior).
5. Exemplo de integrador: `Z_in = R`, `Z_f = 1/(sC)` → `−1/(RCs)`. Exemplo de filtro: `Z_in = R + 1/(sC1)`, `Z_f = 1/(sCf)` → `−(C1/Cf)/(RC1 s + 1)`.

Exemplo numérico completo: [G, Q3](#g).

---

<a id="c"></a>
## C. Erro em regime permanente

### C.0 O que é, e quando faz sentido

- **Erro** = diferença entre o que você queria (a referência `x(t)`) e o que o sistema entrega (`y(t)`): `e(t) = x(t) − y(t)`.
- **Erro em regime permanente** `e(∞)` = o que sobra do erro depois que o transitório acabou, isto é, para `t → ∞`.
- Só existe se o sistema for **estável**. Se os polos de malha fechada tiverem parte real positiva, `y(t)` explode, e as fórmulas abaixo dão um número que **não significa nada**.
- Nos slides da Aula 4 o sistema sempre tem **realimentação unitária** (`H = 1`), então `E = X − Y` é o sinal que entra em G.

### C.1 De onde vêm as fórmulas (entenda uma vez, depois use a tabela)

1. Com realimentação unitária: `Y = G·E` e `E = X − Y`. Logo `E = X − G·E`, isto é, **`E(s) = X(s)/(1 + G(s))`**.
2. **Teorema do valor final:** `e(∞) = lim(s→0) s·E(s)`. (Só vale se `E(s)` for estável.)
3. Juntando: **`e(∞) = lim(s→0) s·X(s)/(1 + G(s))`**. É a fórmula-mãe; tudo abaixo é caso particular.
4. Entradas de teste: degrau `X = 1/s`, rampa `X = 1/s²`, parábola `X = 1/s³`.
   - Degrau: `e(∞) = lim 1/(1+G) = 1/(1 + G(0))` → define **Kp = G(0)**.
   - Rampa: `e(∞) = lim 1/(s + sG) = 1/(lim sG)` → define **Kv = lim s·G**.
   - Parábola: `e(∞) = lim 1/(s² + s²G) = 1/(lim s²G)` → define **Ka = lim s²·G**.

### C.2 Tipo do sistema (quantos integradores)

**Tipo N = número de polos em `s = 0` de G(s) em malha aberta** (número de `s` puros no denominador). **N não é a ordem** do sistema.

Para ler também o **K** (ganho estático), leve G à forma das constantes de tempo, com cada fator valendo 1 em `s = 0`:

```
G(s) = K (Ta·s+1)(Tb·s+1)... / [ sᴺ (T1·s+1)(T2·s+1)... ]
```
Como fazer: em cada fator `(s + a)` com `a ≠ 0`, coloque `a` em evidência: `(s + a) = a(s/a + 1)`.

| G(s) | Forma padrão | Tipo | K |
|---|---|---|---|
| `100/((s+1)(s+10))` | `10 / ((s+1)(0,1s+1))` | 0 | 10 |
| `100/(s(s+1)(s+10))` | `10 / (s(s+1)(0,1s+1))` | 1 | 10 |
| `10(s+2)/(s²(s+10))` | `2(0,5s+1) / (s²(0,1s+1))` | 2 | 2 |

(O `K` da forma padrão é exatamente `Kp`, `Kv` ou `Ka`, conforme o tipo.)

### C.3 Constantes de erro e tabela (realimentação unitária)

| Constante | Fórmula | O que mede |
|---|---|---|
| **Kp** (posição) | `lim(s→0) G(s)` | erro ao degrau |
| **Kv** (velocidade) | `lim(s→0) s·G(s)` | erro à rampa |
| **Ka** (aceleração) | `lim(s→0) s²·G(s)` | erro à parábola |

| Tipo | Degrau (`x = 1`) | Rampa (`x = t`) | Parábola (`x = t²/2`) |
|---|---|---|---|
| **0** | `1/(1+Kp)` | ∞ | ∞ |
| **1** | 0 | `1/Kv` | ∞ |
| **2** | 0 | 0 | `1/Ka` |

**Como ler a tabela:** cada integrador "empurra" o sistema para seguir o tipo de sinal seguinte. Tipo 0 acompanha degrau com um erro fixo; tipo 1 acompanha degrau sem erro e rampa com erro fixo; tipo 2, rampa sem erro e parábola com erro fixo. A célula "∞" significa que o erro cresce sem limite.

### C.4 Receita passo a passo

1. **Monte a malha fechada** e confira se é **estável** (ordem 2: coeficientes positivos; ordem ≥ 3: Routh). Se não for, **pare**: e(∞) não existe.
2. **Identifique se a realimentação é unitária.** Se sim, siga adiante; se `H ≠ 1`, vá para [C.6](#c6).
3. **Conte o tipo N** e escreva G na forma padrão ([C.2](#c)); leia K.
4. **Identifique a entrada** (degrau, rampa ou parábola) e sua **amplitude** `A` (`x = A·degrau` dá erro `A` vezes maior).
5. **Use a tabela:** calcule a constante certa (Kp, Kv ou Ka) com `s → 0` e substitua.
6. **Confirme pelo método direto** (mostra o raciocínio do professor): `e(∞) = lim s·X(s)/(1 + G(s))`.
7. **Comente:** se o erro for 0 ou ∞, a tabela já diz; se for finito, dê o valor.

### C.5 Exemplos

**Ex. 1 (L1-Q4): degrau, tipo 0.** `G = 100/((s+1)(s+10))`.
1. Malha fechada: `s² + 11s + 110`, coeficientes positivos → **estável**.
2. Unitária, tipo 0, `K = 10`.
3. `Kp = G(0) = 100/(1·10) = 10`.
4. `e(∞) = 1/(1+Kp) = 1/11 ≈ 0,09`.
5. Direto: `lim s·(1/s)/(1+G) = 1/(1+10)`.

**Ex. 2 (L1-Q5): rampa, tipo 1.** `G = 100/(s(s+1)(s+10))`.
1. Malha fechada: `s³ + 11s² + 10s + 100`. Routh: linha s¹ = `(110 − 100)/11 = 0,91 > 0` → **estável**.
2. Tipo 1, `Kv = lim sG = 100/(1·10) = 10`.
3. `e(∞) = 1/Kv = 0,1`.
4. Observação: para o **degrau** o erro é 0, e para a **parábola** seria ∞.

**Ex. 3: mesma G do Ex. 1 com rampa.** Tipo 0 → `Kv = lim s·G = 0` → `e(∞) = 1/0 = ∞`. O erro cresce com o tempo: o sistema não consegue seguir uma rampa.

**Ex. 4: tipo 2, parábola.** `G = 10(s+2)/(s²(s+10))`.
1. Malha fechada: `s³ + 10s² + 10s + 20`. Routh: s¹ = `(100 − 20)/10 = 8 > 0`, s⁰ = 20 → **estável**.
2. `Ka = lim s²·G = 10·2/10 = 2`.
3. `e(∞) = 1/Ka = 0,5`. (Degrau e rampa dariam 0.)

**Ex. 5: entrada combinada (superposição).** `x(t) = 3 + 2t` em `G = 100/(s(s+1)(s+10))`.
- Parte degrau de amplitude 3: erro = 0 (tipo 1).
- Parte rampa de inclinação 2: erro = `2/Kv = 0,2`.
- **Total: e(∞) = 0,2.** Some os erros de cada parcela.

**Ex. 6: armadilha, sistema instável.** `G = 10/(s(s+1)(s+2))`. A conta "ingênua" dá `Kv = 5` e `e(∞) = 0,2`. Mas a malha fechada é `s³ + 3s² + 2s + 10`, e a linha s¹ = `(6 − 10)/3 < 0` → **instável**. O erro de regime **não existe**. Sempre teste a estabilidade antes.

### C.6 Quando a realimentação NÃO é unitária (`H ≠ 1`) <a id="c6"></a>

Aí `E = X − Y` (erro verdadeiro) e o sinal que entra no ramo direto (`E = X − H·Y`) deixam de ser iguais. **Use a definição do enunciado**; na dúvida, calcule o erro `X − Y`.

1. `T = G/(1 + GH)` e `Y = T·X`.
2. **Erro verdadeiro:** `E(s) = X(s)(1 − T(s))`, `e(∞) = lim s·X·(1 − T)`.
3. **Sinal de atuação** (saída do somador): `E_a(s) = X/(1 + GH)`, `e_a(∞) = lim s·X/(1 + GH)`.

Exemplo: `G = 10/(s+1)`, `H = 2`, degrau.
- `T = 10/(s + 21)` (estável), `T(0) = 10/21`.
- Erro verdadeiro: `e(∞) = 1 − 10/21 = 11/21 ≈ 0,52`.
- Sinal de atuação: `1/(1+GH(0)) = 1/(1+20) = 1/21 ≈ 0,048`.

Os dois valores diferem; por isso o enunciado precisa dizer qual. A tabela de Kp/Kv/Ka **só vale diretamente com `H = 1`**. (Se `H` for constante `kh`, dá para usar `G' = kh·G` e lembrar que o erro verdadeiro inclui o fator `1/kh`.)

### C.7 Interpretação (pergunta de prova)

- **Aumentar K** aumenta Kp/Kv/Ka e **reduz** o erro finito; mas piora a estabilidade e a oscilação.
- **Adicionar um integrador** (tipo +1) zera o erro do sinal anterior, mas **aumenta a chance de instabilidade** e o **tempo de acomodação** (comparação dos slides: erro 0,09 com menor tempo de acomodação × erro zero com tempo maior).
- **1ª ordem com realimentação unitária** (`1/(Ts)` no ramo direto): degrau → 0; rampa → `e(∞) = T`.

### C.8 Confirmar no MATLAB

```matlab
G  = tf(100,[1 11 10 0]);        % tipo 1
T  = feedback(G,1);
isstable(T)                       % 1) estável?
Kv = dcgain(tf([1 0],1)*G)        % 2) Kv = lim s*G  (use limit simbólico se preferir)
t = linspace(0,50,2000); r = t;   % rampa
y = lsim(T,r,t); e_final = r(end) - y(end)   % ~ 0,1
```
Com Symbolic Math: `syms s; limit(s*(1/s^2)/(1+100/(s*(s+1)*(s+10))), s, 0)` → `1/10`.

Resolvidos: L1-Q4 e L1-Q5 em [Gabarito_Controle_P1.md](Gabarito_Controle_P1.md).

---

<a id="d"></a>
## D. 1ª e 2ª ordem: análise e projeto

### D.1 Sistema de 1ª ordem `1/(Ts+1)`
- `y(t) = 1 − e^(−t/T)` (degrau). Valor em `t = T`: **63,2 %**. `ts(2%) ≈ 4T`, `ts(5%) ≈ 3T`.
- **Identificar T** a partir do gráfico: tempo em que a saída chega a 63,2 % do valor final.

### D.2 Sistema de 2ª ordem padrão `ωn²/(s² + 2ζωn s + ωn²)`

**Análise (dado T(s), ache as especificações):**
1. Compare o denominador com `s² + 2ζωn s + ωn²` → **ωn = √(termo constante)**, **ζ = (coef. de s)/(2ωn)**. (Se o numerador não for `ωn²`, o ganho estático muda, e ζ e ωn continuam vindo do denominador.)
2. `ωd = ωn√(1−ζ²)`; polos `−ζωn ± jωd`.
3. **Mp = e^(−πζ/√(1−ζ²))**, **tp = π/ωd**, **ts(2%) = 4/(ζωn)** (1 %: 4,6/ζωn; 5 %: 3/ζωn).
4. **tr (0-100 %) = (π − β)/ωd**, `β = tan⁻¹(√(1−ζ²)/ζ)`. (tr 10-90 %: `(1,76ζ³ − 0,417ζ² + 1,039ζ + 1)/ωn`.)

**Projeto (dadas as especificações, ache os parâmetros):**
1. **Overshoot → ζ:** `ζ = −ln(Mp)/√(π² + ln²(Mp))` (Mp em fração). Ex.: 15 % → **ζ = 0,517**. Overshoot aceitável 4 a 25 % ↔ 0,4 < ζ < 0,7.
2. **ts → ωn:** `ωn = 4/(ζ·ts)` (2 %).
3. **Componentes:** compare com a forma do circuito (ex.: RLC: `ωn² = 1/LC`, `2ζωn = R/L`).
4. **Confira** se os componentes fixos (ex.: R) são compatíveis com os dois parâmetros; se sobrar um grau de liberdade, o enunciado manda escolher.

**Efeito dos parâmetros:**
- Mp depende **só de ζ**.
- Para RLC série com saída no capacitor: `ζ = (R/2)√(C/L)`, `ζωn = R/(2L)`. **Aumentar R**: aumenta ζ (menos overshoot), **diminui ts** (`ts = 8L/R`, no subamortecido), e aumenta tr/tp (resposta mais "lenta" na subida). Passando de ζ = 1, o polo lento domina e a resposta fica lenta de novo.
- **Polos no plano s:** ωn constante = círculos; ζ constante = retas pela origem; parte real constante = ts constante; parte imaginária constante = tp constante.

**Identificação pelo gráfico:** de Mp medido tira-se ζ; de tp tira-se ωd (e então ωn).

---

<a id="e"></a>
## E. Estabilidade por Routh-Hurwitz

### E.1 Estável ou não? (polinômio numérico)
1. **Polinômio característico:** denominador de malha fechada (`1 + GH = 0` multiplicado por tudo).
2. **Remova raízes nulas** (fatore `s`). Conferir coeficientes: algum zero/negativo com outros positivos → **instável**.
3. **Tabela:** linha sⁿ = coeficientes de índice par; linha sⁿ⁻¹ = índice ímpar. Cada elemento novo vem de um "determinante" das duas linhas de cima dividido pelo pivô (1º elemento da linha imediatamente acima):
   `b1 = (a1·a2 − a0·a3)/a1`, `b2 = (a1·a4 − a0·a5)/a1`; na linha seguinte `c1 = (b1·a3 − a1·b2)/b1` etc. Pode multiplicar/dividir uma linha por número **positivo**.
4. **1ª coluna toda positiva** = estável. **Nº de mudanças de sinal = nº de polos no semiplano direito.**

### E.2 Faixa de K (ou de um parâmetro k)
1. **Ponha K no polinômio característico** (Q1 do Relatório 2: a incógnita `k` aparece no termo constante; na Lista de Root Locus, `1 + K·G·H = 0` → `A(s) + K·B(s) = 0`).
2. **Monte a tabela** com K literal (as contas ficam em função de K).
3. **Imponha cada elemento da 1ª coluna > 0** → uma desigualdade por linha.
4. **Interseção** de todas as desigualdades = faixa estável. Fique atento a denominadores que mudam de sinal (ex.: `k(4−k)/(2−k)`: analise o sinal da fração).
5. **Bordas:** K onde um elemento zera = sistema marginal (polos em jω ou na origem). Se zerou a linha s⁰ → polo em s=0; se zerou a linha s¹ → use a **equação auxiliar (linha s²)** para achar ±jω.
6. **Conferência numérica** (MATLAB): `roots(...)` para um K dentro e um fora da faixa.

### E.3 Casos especiais
| Caso | Como resolver |
|---|---|
| Zero na 1ª coluna, resto da linha ≠ 0 | `s = 1/x`; ou multiplicar por `(s+1)`; ou trocar o 0 por ε→0⁺ e fazer o limite |
| Linha inteira de zeros | equação auxiliar da linha anterior → derivar → usar os coeficientes → continuar; as raízes da auxiliar também são raízes do sistema |
| Vários coeficientes nulos no polinômio | aplicar normalmente |

Resolvido: Relatório 2 Q1 (`0 < k < 1`) em [Gabarito_Relatorio2_Controle.md](Gabarito_Relatorio2_Controle.md).

---

<a id="f"></a>
## F. Lugar das raízes

> **Guia completo de desenho e leitura:** [Tutorial_Desenhar_e_Ler_Lugar_das_Raizes.md](Tutorial_Desenhar_e_Ler_Lugar_das_Raizes.md) (como desenhar a partir dos pontos, e como interpretar o gráfico: K, polos, estabilidade, ζ, ωn, tipo de resposta).

### F.0 A ideia em uma frase

Você tem um sistema com um **ganho K ajustável** e quer saber **onde ficam os polos de malha fechada quando K vai de 0 a +∞**. O **lugar das raízes** é o desenho dessas trajetórias no plano s. Com ele você vê, sem resolver o polinômio para cada K: **para quais K o sistema é estável**, **quando oscila** e **quanto vale K para um amortecimento desejado**.

### F.1 Por que funciona (o mínimo de teoria)

- Malha fechada: `T = K·G/(1 + K·G·H)`. Os polos de T são as raízes de **`1 + K·G(s)·H(s) = 0`** (equação característica), isto é, `K·G·H = −1`.
- Como `K·G·H` é um número complexo, para valer `−1` precisa cumprir duas condições ao mesmo tempo:
  - **Fase:** `∠G·H(s) = (2n+1)·180°` (ângulo de ±180°, ±540°...).
  - **Ganho:** `K·|G·H(s)| = 1`, isto é, **`K = 1/|G·H(s)|`**.
- Em cada ponto `s`, a **fase** diz se o ponto está no lugar; e o **ganho** diz a que **K** ele corresponde.
- **Ângulo e distância via vetores:** cada fator `(s + a)` é o vetor que vai do ponto `−a` (zero ou polo) até `s`. Seu módulo é a distância e sua fase é o ângulo desse vetor, medido a partir do eixo real, **sentido anti-horário**.
  - `fase total = Σ ângulos dos zeros − Σ ângulos dos polos`
  - `K = (produto das distâncias aos polos)/(produto das distâncias aos zeros)`
- Todas as regras do esboço (eixo real, assíntotas, ângulos de partida) são só consequências da condição de fase.

### F.2 Antes de começar: arrume a equação

1. Escreva **`G(s)·H(s)` de malha aberta** (multiplique o ramo direto pelo de realimentação).
2. Leve à forma **`K·B(s)/A(s)`**, com **B = numerador** (zeros) e **A = denominador** (polos), ambos **mônicos** (coeficiente do termo de maior grau = 1) e **K ≥ 0**. O ganho K é o parâmetro que varia.
3. Se o ganho aparece como `2K` (Rel. 2, Q3), tudo continua valendo; só lembre que o valor lido é de `2K`, ou absorva o 2 em `K`.
4. Se aparecer um fator como `(s − 1)`, o zero/polo é em **+1** (semiplano direito).
5. **Realimentação positiva** 🧩: a equação vira `1 − K·G·H = 0`. Veja as mudanças em [F.8](#f8).

### F.3 Os 7 passos do esboço (com o porquê de cada um)

**Passo 1: marque polos (x) e zeros (o) de malha aberta** no plano s. `n` = nº de polos, `m` = nº de zeros (finitos). Polos múltiplos: marque com o número ao lado.

**Passo 2: eixo real.** O lugar existe nos pontos do eixo real que têm **número ÍMPAR de polos + zeros reais à direita** (contando multiplicidades; 0 é par).
- *Por quê:* cada polo/zero real à direita de `s` contribui com 180° de fase; um número par soma múltiplo de 360° (não vale), um ímpar soma 180° (vale). Polos complexos conjugados se anulam em fase.
- *Como fazer:* ande da direita para a esquerda ao longo do eixo e vá contando. Marque os trechos "ímpares".

**Passo 3: começo, fim e número de ramos.**
- Nº de ramos = nº de polos `n`.
- Cada ramo **começa em um polo** (K = 0) e **termina em um zero** (K → ∞).
- `m` ramos terminam nos zeros finitos; **`n − m` ramos vão ao infinito**.

**Passo 4: assíntotas** (se `n > m`). Os `n − m` ramos que vão ao infinito seguem retas:
- **Ponto de encontro no eixo real:** `σa = (Σ polos − Σ zeros)/(n − m)`
- **Ângulos:** `θa = (2k+1)·180°/(n − m)`, `k = 0, 1, …, n−m−1`
  - `n−m = 1` → 180°
  - `n−m = 2` → 90°, 270°
  - `n−m = 3` → 60°, 180°, 300°
  - `n−m = 4` → 45°, 135°, 225°, 315°
- *Por quê:* para `|s|` muito grande, `G·H ≈ 1/sⁿ⁻ᵐ` e a fase vira `−(n−m)·∠s`.
- Use **somente as partes reais** dos polos/zeros ao somar (as complexas conjugadas se somam).

**Passo 5: pontos de saída e entrada no eixo real.**
- **Saída:** onde dois ramos **se desprendem** do eixo real e entram no plano complexo (entre **dois polos** adjacentes no lugar).
- **Entrada:** onde ramos **voltam** ao eixo real (entre **dois zeros** adjacentes, ou entre um zero e o infinito).
- **Cálculo:** de `1 + K·B/A = 0` vem `K = −A/B`. Os pontos de saída/entrada são os extremos de K(s): `dK/ds = 0`, isto é,
  **`A'(s)·B(s) − A(s)·B'(s) = 0`**.
- **Filtre as raízes:** só valem as que caem num **trecho do eixo real que pertence ao lugar** (passo 2). As demais são descartadas.
- **K no ponto:** `K = −A(s₀)/B(s₀)` (deve dar positivo).
- Entre um polo e um zero adjacentes pode não existir ponto de saída/entrada.

**Passo 6: cruzamento com o eixo imaginário** (onde o sistema passa a oscilar sem amortecimento).
1. Monte o polinômio característico com K: `A(s) + K·B(s) = 0`.
2. Faça a tabela de **Routh** com K literal.
3. O **K limite** é o que zera a linha **s¹** (ou a linha s⁰: nesse caso o cruzamento é na origem).
4. Substitua esse K na **equação auxiliar** (linha s²) e resolva: `s = ±jω`.
5. Se a linha s¹ não zera para nenhum K > 0, o lugar **não cruza** o eixo jω (exceto possivelmente na origem).

**Passo 7: ângulos de partida e chegada** (só se houver polos ou zeros **complexos** ou **polos múltiplos**; não afeta a faixa de K, só o formato do desenho).
- **Partida de um polo complexo:** `θp = 180° + Σ ângulos dos zeros − Σ ângulos dos outros polos` (**ignora o próprio polo**).
- **Chegada a um zero complexo:** `θz = 180° − Σφ(GH)`, com `Σφ(GH) = Σ ângulos dos outros zeros − Σ ângulos dos polos` (**ignora o próprio zero**).
- Ângulos sempre **medidos no sentido anti-horário a partir do eixo real positivo**, do polo/zero até o ponto.
- **Polo múltiplo (ordem q):** `q·θ = 180°·(2k+1) + Σφ(zeros) − Σφ(outros polos)`, com `k = 0, 1, …, q−1`. Os ângulos φ são dos vetores que vão de cada zero/outro polo **até o polo em estudo**. Serve para saber **em que direção saem os q ramos** (um por valor de k).
  - *Exemplo (Rel. 2 Q4, polo duplo em −2, zero em +1, polo em −1):* os dois vetores (de +1 e de −1 até −2) apontam para a esquerda, φ = 180° cada. `Σφ(zeros) − Σφ(outros polos) = 180° − 180° = 0°`. `2θ = 180°(2k+1)` → **θ = 90° e 270°**: os dois ramos saem **na vertical**, um para cima e outro para baixo.
- O lugar é **simétrico** em relação ao eixo real: o ângulo do conjugado é o negativo.

**Depois dos 7 passos: desenhe.** Veja [F.3.1](#f31), com a construção passo a passo e as regras para ligar os ramos.

### F.3.1 Como desenhar depois de ter os pontos <a id="f31"></a>

Você já tem a lista: polos e zeros, trechos do eixo real, assíntotas, ponto de saída/entrada, cruzamentos com jω (e ângulos de partida, se houver complexos). Agora é **juntar tudo num desenho**. Pense em **montar um quebra-cabeça**: primeiro as peças fixas, depois as curvas que ligam as peças.

**Veja a construção inteira, passo a passo, com dois exemplos:**

- Exemplo da Aula 8 (mais legível): ![Construção Aula 8](img/rl_aula8_passos.png)
- Relatório 2 Q2 (polo no semiplano direito): ![Construção Rel2 Q2](img/rl_q2_passos.png)

#### Passo D1: monte a folha

1. **Eixos:** desenhe o eixo real (horizontal) e o imaginário (vertical). Use a **mesma escala nos dois** (um quadradinho = 1 em x e em y), senão os ângulos das assíntotas (60°, 90°...) ficam errados.
2. **Alcance:** vá do zero/polo mais à esquerda até um pouco além do mais à direita, e na vertical **até cobrir o cruzamento com jω** (± valor do passo 6) e um pouco mais. Se for desenhar à mão, deixe o eixo imaginário com espaço de pelo menos ±(1,5 × o maior cruzamento).
3. **Marque as graduações** só onde há algo importante (polos, zeros, σa, ponto de saída, cruzamento).

#### Passo D2: desenhe as peças fixas (com lápis, depois você refaz com caneta)

| O que | Como desenhar |
|---|---|
| **Polos** | `x` no eixo real (ou no ponto complexo). Polo duplo: `x` com um "2" ao lado. |
| **Zeros** | `o` no ponto. |
| **Trechos do eixo real** | **Linha grossa** nos trechos que o passo 2 mostrou (número ímpar à direita). Fora deles **não** tem lugar. |
| **Assíntotas** | Parta de `σa` no eixo real e trace retas **tracejadas** com os ângulos de `θa`. Estenda até a borda do desenho. |
| **Ponto de saída/entrada** | Ponto no eixo real, com o valor (ex.: `−0,4976`, `K = 1,46`). |
| **Cruzamentos com jω** | Pontos no eixo imaginário (`±jω`) com o K correspondente. |
| **Zona estável** | Sombreie ou escreva "estável" no semiplano esquerdo. |

Neste ponto você tem **um esqueleto com todos os pontos pelos quais o lugar passa**. Falta só ligar.

#### Passo D3: ligue os ramos (as regras de ouro)

**Regra geral:** **cada ramo parte de um polo (K = 0) e chega a um zero (K → ∞) ou vai ao infinito** pela assíntota. Use esta tabela para decidir **como** cada ramo se move:

| Situação | Como desenhar |
|---|---|
| **Polo → zero**, os dois ligados por um trecho válido do eixo real | Segue **reto pelo eixo real** até o zero. (Ex.: polo −3 → zero −2.) |
| **Polo vai ao infinito sobre o eixo real** (trecho válido sem zeros à esquerda) | Segue pelo eixo real para a esquerda (ou direita) e fica **colado na assíntota de 180° (ou 0°)**. (Ex.: polo −4 → −∞.) |
| **Dois polos adjacentes com trecho válido entre eles** | Os dois ramos **caminham um em direção ao outro** pelo eixo real, **se encontram no ponto de saída** e **saem do eixo na vertical (±90°)**. (Ex.: polos 0 e −1.) |
| **Ramos no plano complexo** (depois do ponto de saída) | Curve-os: eles **sobem e descem simetricamente**, passam **pelos pontos de cruzamento com jω** (se houver) e **vão se aproximando das assíntotas** (sem tocá-las, no limite). |
| **Polo complexo** | Sai do polo no ângulo de partida `θp` do passo 7 e depois segue as regras acima. |
| **Polo duplo** | Os dois ramos saem **na vertical** (±90°) do polo duplo e se afastam para os lados. |
| **Ponto de entrada** | Os ramos chegam ao eixo real pela vertical (±90°) e se separam: um vai ao zero, o outro ao infinito. |

**Como saber para onde cada ramo vai:**
1. Marque cada polo e conte quantos ramos saem dele (um por polo; polo duplo = 2).
2. Cada trecho válido do eixo real é percorrido por **um** ramo (ou dois, que se encontram).
3. Os ramos que sobrarem (sem zero à vista) vão para as **assíntotas**, na ordem em que aparecem (de cima para baixo, o ramo que sai pelo ponto de saída vai para a assíntota de cima, e o simétrico para a de baixo).
4. O número de ramos que vão ao infinito tem de ser **`n − m`** e o número de assíntotas também.

#### Passo D4: trace as curvas (o formato da curva)

1. **Comece nos pontos conhecidos.** Passe a curva exatamente pelo ponto de saída, pelos cruzamentos com jω e pelo ângulo de partida. Entre dois pontos, a curva é **suave** (sem cantos).
2. **No ponto de saída:** a curva sai **perpendicular** ao eixo real.
3. **No cruzamento com jω:** a curva atravessa o eixo imaginário **inclinada** (não precisa ser perpendicular).
4. **Longe da origem:** a curva **se aproxima da assíntota**, sem cruzá-la (na maioria dos casos) e **ficando do lado de onde veio**.
5. **Simetria:** desenhe a metade de cima e **espelhe** a de baixo em relação ao eixo real.
6. **Ramos nunca se cruzam** (só se encontram nos pontos de saída/entrada).

#### Passo D5: marque setas e valores de K

1. **Setas** no sentido em que **K cresce** (do polo para o zero/infinito).
2. Escreva **o K** nos pontos notáveis: `K = 0` nos polos, `K = 1,46` no ponto de saída, `K = 41` no cruzamento com jω.
3. Indique a **faixa de K estável** (a parte do lugar no semiplano esquerdo).

#### Passo D6: confira (antes de entregar)

| Conferência | O que olhar |
|---|---|
| Nº de ramos | igual ao nº de polos `n` |
| Ramos no infinito | exatamente `n − m` |
| Eixo real | só nos trechos ímpares (nada nos pares) |
| Simetria | a metade de cima é espelho da de baixo |
| Assíntotas | `n − m` retas, ângulos e `σa` corretos |
| Pontos | ponto de saída **dentro** de um trecho válido; cruzamento com jω **bate com o Routh** |
| Soma dos polos | com `n − m ≥ 2`, a soma dos polos de malha fechada **não muda** com K (ex.: soma = −8 na Aula 8: confira em um K qualquer, `p₁ + p₂ + p₃ + p₄ = −8`) |
| MATLAB | `rlocus(G*H)` deve ter o mesmo formato (mesmos trechos e pontos) |

#### Erros comuns ao desenhar

1. **Escalas diferentes** em x e y (assíntotas ficam com ângulo errado).
2. Desenhar lugar em trecho **par** do eixo real.
3. Fazer a curva **cortar o eixo real fora do ponto de saída** ou ramos se cruzarem.
4. Esquecer a **simetria** ou desenhar só metade.
5. **Assíntota** partindo da origem em vez de `σa`.
6. Esquecer de indicar o **K** nos pontos e a **faixa estável**.

#### Exemplos que você já tem prontos (compare com o seu)

- Aula 8: [img/rl_aula8_passos.png](img/rl_aula8_passos.png) (K = 41 e saída em −0,4976).
- Rel. 2 Q2: [img/rl_q2_passos.png](img/rl_q2_passos.png) e o desenho final [img/rl_q2.png](img/rl_q2.png).
- Rel. 2 Q3: [img/rl_q3.png](img/rl_q3.png).
- Rel. 2 Q4: [img/rl_q4.png](img/rl_q4.png).

### F.4 Exemplo completo 1: `G·H = K(s+2)/(s(s+1)(s+3)(s+4))` (Aula 8)

1. **Polos:** 0, −1, −3, −4. **Zero:** −2. `n = 4`, `m = 1`.
2. **Eixo real:** (−1, 0): 1 à direita ✔. (−2, −1): 2 ✘. (−3, −2): 3 ✔. (−4, −3): 4 ✘. (−∞, −4): 5 ✔.
3. **Ramos:** 4. Um termina em −2; **3** vão ao infinito.
4. **Assíntotas:** `σa = (0−1−3−4 − (−2))/3 = −6/3 = −2`; `θa = (2k+1)180°/3 = 60°, 180°, 300°`.
5. **Saída:** `A = s⁴+8s³+19s²+12s`, `B = s+2`:
   `A'B − AB' = 3s⁴ + 24s³ + 67s² + 76s + 24 = 0` → raízes `−3,50`, `−2 ± j0,77`, **`−0,4976`**. Só `−0,4976` está no lugar (entre os polos 0 e −1). `K = 1,4584`.
6. **Cruzamento com jω:** `s⁴ + 8s³ + 19s² + (12+K)s + 2K = 0`. Routh:
   - s²: `(140−K)/8`; s¹: `(1680 − K²)/(140−K)`; s⁰: `2K`.
   - s¹ = 0 → `K = √1680 ≈ 41`; auxiliar `(140−41)s² + 16·41 = 99s² + 656 = 0` → **s = ±j2,574**.
   - s⁰ = 0 → K = 0 (a origem, onde o polo em 0 começa).
7. **Faixa estável:** `0 < K < 41`.
8. **Desenho:** os ramos de 0 e −1 se encontram em −0,4976 e saem para o plano complexo, cruzando jω em ±j2,574 (K = 41) e seguindo em 60° e 300°; o ramo de −3 vai ao zero −2; o ramo de −4 vai a −∞ (180°).

### F.5 Exemplo completo 2 (polos complexos): `G·H = K(s+2)/(s²+2s+2)`

1. **Polos:** `−1 ± j`. **Zero:** −2. `n = 2`, `m = 1`.
2. **Eixo real:** à esquerda de −2 há 1 zero à direita ✔ → (−∞, −2] pertence ao lugar. (Os polos complexos não contam.)
3. **Ramos:** 2; um termina em −2, o outro vai ao infinito (`n−m = 1`).
4. **Assíntota:** ângulo 180° (ao longo do eixo real negativo).
5. **Ângulo de partida do polo `p1 = −1 + j`:**
   - zero −2 até `p1`: vetor `(+1, +1)` → **45°**.
   - outro polo `p2 = −1 − j` até `p1`: vetor `(0, +2)` → **90°**.
   - `θp1 = 180° + 45° − 90° = 135°`. Pela simetria, `θp2 = 225° (= −135°)`.
6. **Ponto de entrada:** `A'B − AB' = (2s+2)(s+2) − (s²+2s+2) = s² + 4s + 2 = 0` → `s = −2 ± √2` = −0,586 ou **−3,414**. Só **−3,414** está no lugar (à esquerda de −2). `K = −A/B = 6,83/1,414 ≈ 4,83`. Os ramos complexos curvam-se e voltam ao eixo real em −3,414: um vai ao zero −2 e o outro a −∞.
7. **Jω:** `s² + (2+K)s + (2+2K)`: todos os coeficientes positivos para K > 0, então **sempre estável**; não há cruzamento.

### F.6 Exemplo completo 3 (Relatório 2 Q3): `G·H = 2K/((s−1)(s+2))`

1. Polos `+1`, `−2`; `n = 2`, `m = 0`.
2. Eixo real: entre −2 e +1 (1 polo à direita) ✔.
3. Assíntotas: `σa = (1−2)/2 = −0,5`, `θ = 90°, 270°`.
4. Saída: `A = s²+s−2`, `B = 2`: `A'B − AB' = 2(2s+1) = 0` → `s = −0,5` ✔, `2K = 2,25` → `K = 1,125`.
5. Jω: `s² + s + (2K − 2)`; `s⁰ = 2K−2 = 0` → `K = 1` (cruza a **origem**), sem cruzamento em ±jω.
6. Estável para `K > 1`.

Resolvido em detalhe: [Gabarito_Relatorio2_Controle.md](Gabarito_Relatorio2_Controle.md) (Q2, Q3 e Q4).

### F.7 Como usar o lugar das raízes (o que as perguntas pedem)

**a) Faixa de K estável.** Trechos do lugar no semiplano esquerdo. Os limites vêm do passo 6 (K que cruza jω) e do passo 2/6 (K que cruza a origem). Ex.: Rel. 2 Q2: `24 < K < 42`.

**b) K para um polo desejado `s₀`:** `K = (produto das distâncias aos polos)/(produto das distâncias aos zeros)` calculadas até `s₀`, ou `K = −A(s₀)/B(s₀)` (na prática, igual).

**c) K para um amortecimento ζ dado.**
1. Desenhe a reta do lugar com ângulo `φ = cos⁻¹(ζ)` a partir do eixo real negativo (`ζ` constante = reta radial).
2. O ponto onde ela cruza o lugar é o polo `s₀`.
3. Calcule K em `s₀`.
Exemplo (Aula 7, câmera): `GH = K/(s(s+10))`; polos 0 e −10; `n−m = 2` → `σa = −5`, vertical; saída em `s = −5` (K = 25).
Para `ζ = 0,5`: `φ = 60°`, o ponto em `Re = −5` é `s₀ = −5 ± j8,66`. `K = |s₀|·|s₀+10| = 10 × 10 = 100`. Conferência: `s² + 10s + 100` → `ωn = 10`, `ζ = 10/(2·10) = 0,5` ✔.

**d) Classificar a resposta pelo trecho do lugar** (2ª ordem): polos reais distintos = superamortecido; polo duplo (ponto de saída) = criticamente amortecido; complexos = subamortecido; no eixo jω = oscilatório (marginal).

**e) Efeito de adicionar polos/zeros:** polos puxam o lugar para a direita (menos estável); zeros puxam para a esquerda (mais estável).

### F.8 Situações especiais <a id="f8"></a>

| Situação | O que acontece / como tratar |
|---|---|
| **Polo em +a (instável em malha aberta)** | K = 0 já é instável; só fica estável a partir de um K mínimo (Rel. 2 Q2: `K > 24`). A faixa estável é `K_min < K < K_max`. |
| **Zero em +a (fase não mínima)** | Um ramo termina nesse zero no semiplano direito; para K grande o sistema fica instável (Rel. 2 Q4: `K < 4`). |
| **Polo duplo** | Os dois ramos saem **na vertical** (±90°, com ajuste dos outros polos/zeros); `s = polo duplo` é raiz de `A'B − AB'`. |
| **n − m = 2** | Soma dos polos de malha fechada **constante** (= soma dos polos de malha aberta) para qualquer K: boa conferência. |
| **n − m ≥ 3** | Sempre há ramos indo ao semiplano direito para K grande (assíntotas com ângulos de 60° ou mais da vertical). |
| **Feedback positivo** 🧩 | Equação `1 − K·G·H = 0`. Muda: eixo real com número **PAR** à direita (0 é par); assíntotas `θ = 2k·180°/(n−m)`; condição de fase `2k·180°`. No MATLAB: `rlocus(-G*H)`. As curvas contínuas são de realimentação negativa e as tracejadas de positiva (slide da Aula 9). |

### F.9 Conferência no MATLAB

```matlab
G = tf(1,[1 1 0]);  H = tf([1 2],[1 7 12]);   % ramos direto e de realimentação
A = G*H;                                      % malha aberta
rlocus(A); axis([-6 1 -3 3]); grid on          % grid mostra retas de zeta e circulos de wn
[K,p] = rlocfind(A)                            % clica no ponto e lê K e polos
% feedback positivo:  rlocus(-A)
```
Compare no gráfico: trechos do eixo real, assíntotas, ponto de saída e cruzamento com jω. Para conferir um K específico: `pole(feedback(K*A,1))`.

### F.10 Erros comuns no lugar das raízes

1. Marcar polos/zeros de **malha fechada** (o lugar usa os de **malha aberta**).
2. Esquecer polos/zeros no **semiplano direito** (`(s−1)` é +1, não −1).
3. Contar o número de polos+zeros **à esquerda** em vez de à **direita** no passo 2.
4. **Aceitar ponto de saída fora do lugar real** (ex.: raiz de `A'B−AB'` em trecho par).
5. Somar na `σa` os polos complexos como se fossem reais (use a soma das partes reais).
6. Esquecer a **simetria** em relação ao eixo real.
7. Não conferir com Routh: o cruzamento com jω sai do Routh, não de adivinhar o desenho.
8. Esquecer o fator no ganho (`2K`, `K/10`...), que muda o valor de K lido, mas não o desenho.

---

<a id="g"></a>
## G. Exemplos resolvidos do Relatório 1 (slides da Aula 6)

### G.1 Q1: circuito RLC (R = 50 Ω, L = 100 mH, saída no capacitor)

Pedem: C e T(s) para **Mp = 15 %** e **ts(2 %) = 16,3 ms**; gráfico; tr (0-100 %); efeito de R.

1. **Função de transferência do circuito (B.1):** `T(s) = (1/LC)/(s² + (R/L)s + 1/LC)`, com `R/L = 500`.
2. **Overshoot → ζ:** `ln 0,15 = −1,897` → `ζ = 1,897/√(π² + 1,897²) = 0,517`.
3. **ts → ωn:** `ωn = 4/(ζ·ts) = 4/(0,517 × 0,0163) = 474,7 rad/s`.
4. **C:** `ωn² = 1/(LC)` → `C = 1/(0,1 × 474,7²) = 44,4 µF`.
5. **T(s):** `T(s) = 2,25·10⁵/(s² + 500s + 2,25·10⁵)`.
6. **Conferir com R fixo:** `2ζωn = R/L = 500` → `ζ_real = 500/(2 × 474,6) = 0,527` → `Mp_real = 14,3 %`, `ts_real = 4/(ζωn) = 16 ms`. Praticamente as especificações (o R fixo dá o valor exato de ζωn, por isso 16 ms em vez de 16,3).
7. **Tempo de subida (0-100 %):** `ωd = ωn√(1−ζ²) = 403,4`; `β = tan⁻¹(√(1−ζ²)/ζ) = 58,2° = 1,016 rad`; `tr = (π − 1,016)/403,4 ≈ 5,3 ms`. (`tp = π/ωd = 7,8 ms`.)
8. **Efeito de R:** `ζ = (R/2)√(C/L)`: R = 25 Ω → ζ = 0,26 (oscila muito); R = 50 Ω → 0,53; R = 100 Ω → 1,05 (criticamente amortecido); R = 200 Ω → 2,1 (superamortecido, resposta lenta). No subamortecido `ts = 8L/R` cai com R, mas aumenta o tempo de subida.
9. **MATLAB:** `T = tf(2.25e5,[1 500 2.25e5]); step(T); stepinfo(T)`.

### G.2 Q2: diagrama com G, H, I, J, L

**Leitura do diagrama (ambíguo no slide):** o somador 1 (+X, −realimentação) alimenta **G**; a saída de G entra no somador 2 (+, e **−** vindo de H). O somador 2 alimenta **I**, cuja saída é o ponto **P**. De **P** saem: **J** (→ Y), **H** (volta ao somador 2 com sinal −) e uma entrada do somador 3 (+). Y passa por **L** e entra no somador 3 (+). A saída do somador 3 volta ao somador 1 com sinal −.
(No slide a seta de I aparece apontando para o somador 2, mas é a única leitura em que o somador 2 tem saída; confira com o diagrama do caderno.)

1. **Sinais:** `E1 = X − F` (somador 1), `W = G·E1 − H·P` (somador 2), `P = I·W`, `Y = J·P`, `F = P + L·Y` (somador 3).
2. **Laço interno (H):** `P = I(G·E1 − H·P)` → `P(1 + IH) = I·G·E1` → `P = IG·E1/(1+IH)`.
3. **Laço externo:** `F = P + L·J·P = P(1 + LJ)`; `E1 = X − P(1+LJ)`.
4. **Substituir:** `P(1+IH) = IG(X − P(1+LJ))` → `P[1 + IH + IG(1+LJ)] = IG·X`.
5. **Saída:** `Y = J·P`:

```
T(s) = Y/X = G·I·J / (1 + I·H + G·I + G·I·J·L)
```
6. **Conferência por Mason:** caminho direto `G·I·J`; laços (todos negativos): `−IH`, `−GI`, `−GIJL`; como todos se tocam, `T = GIJ/(1 + IH + GI + GIJL)` ✔.

### G.3 Q3: dois amp-ops em cascata, realimentação unitária

Estágio 1 (inversor): `Z_in = 20 kΩ + 1/(s·1 µF)`, `Z_f = 1/(s·100 nF)`.
Estágio 2 (inversor): `Z_in = 200 kΩ`, `Z_f = 1/(s·1 µF)`.

1. **Estágio 1:** `V1/Vi = −Z_f/Z_in = −(1/(s·100n))/((20k·1µ·s + 1)/(s·1µ)) = −(1µ/100n)/(0,02 s + 1) = −10/(0,02 s + 1)`.
2. **Estágio 2:** `Vo/V1 = −(1/(s·1µ))/200k = −1/(0,2 s)`.
3. **Cascata:** `G(s) = (−10/(0,02 s+1))·(−1/(0,2 s)) = 50/(s(0,02 s + 1)) = 2500/(s(s + 50))`.
4. **a) G(s) = 2500/(s(s+50))** (tipo 1).
5. **Malha fechada unitária:** `T = G/(1+G) = 2500/(s² + 50 s + 2500)`. Compare com `s² + 2ζωn s + ωn²`: **ωn = 50 rad/s**, **b) ζ = 50/(2·50) = 0,5**.
6. **c) Overshoot:** `Mp = e^(−π·0,5/√0,75) = e^(−1,814) = 16,3 %`.
7. **d) ts (2 %)** `= 4/(ζωn) = 4/25 = 0,16 s`.
8. Extras: `ωd = 43,3 rad/s`, `tp = π/ωd = 72,6 ms`; erro à rampa = `1/Kv = 1/50 = 0,02` (Kv = lim sG = 2500/50 = 50).
9. **e) MATLAB:** `G = tf(2500,[1 50 0]); T = feedback(G,1); step(T); stepinfo(T)`.

---

<a id="h"></a>
## H. Conferência no MATLAB

| Conferir | Comando |
|---|---|
| Malha fechada de um diagrama | `feedback(G,H)`, `series`, `parallel`; ou `syms` + `solve` (ver [guia_P1_matlab.m](guia_P1_matlab.m)) |
| Polos e zeros | `pole(T)`, `zero(T)`, `pzmap(T)`, `[z,p,k] = tf2zp(num,den)` |
| Estável? | `isstable(T)` ou `all(real(pole(T))<0)` |
| Resposta ao degrau / rampa | `step(T)`, `t = 0:0.01:10; lsim(T,t,t)` |
| Overshoot, tr, ts | `stepinfo(T)` |
| Erro estático | `dcgain(tf(1)/(1+G))` (degrau); `limit` simbólico para rampa |
| Raízes para um K | `roots(den + K*num)` (polinômios do mesmo tamanho) |
| Lugar das raízes | `rlocus(G*H); axis([...]); grid on` |
| K em um ponto clicado | `[K,p] = rlocfind(G*H)` |
| Feedback positivo | `rlocus(-G*H)` |

---

<a id="i"></a>
## I. Erros que mais custam pontos

1. **Diagramas:** aplicar `G/(1+GH)` sem ver onde H lê o sinal; esquecer o sinal do somador; usar `(G+H1)` quando H2 só lê G.
2. **Circuitos:** esquecer que o capacitor é `1/(sC)` (inverso), confundir `Z_f` com `Z_in`, esquecer o sinal − do inversor (em cascata de dois inversores o sinal some).
3. **Erro:** calcular sem checar estabilidade; usar `Kp` para rampa; esquecer que realimentação não unitária muda a fórmula.
4. **2ª ordem:** usar `ts = 4/ωn` (falta o ζ); esquecer que Mp vem em fração (× 100 para %); confundir ωn com ωd.
5. **Routh:** esquecer de remover raízes nulas; dividir/multiplicar a linha por número **negativo**; contar **mudanças de sinal** (não "números negativos") para polos no SPD; não olhar o sinal da fração na faixa de K.
6. **Root locus:** marcar polos de malha **fechada**; esquecer polos/zeros no semiplano direito (`(s−1)` é +1); **aceitar ponto de saída que não está no lugar**; esquecer a simetria.
7. **Unidades:** ms, µF, nF, kΩ. Converta antes.

<a id="chk"></a>
## Checklist final

- [ ] Identifiquei o tipo de questão (tabela do início) e segui os passos na ordem?
- [ ] Diagrama: equações por somador, sinais e "onde H lê"?
- [ ] Circuito: impedâncias em Laplace, divisor / `−Z_f/Z_in`, sanidade em DC e altas frequências?
- [ ] Erro: estável? tipo e entrada certos? Constante com `s → 0`?
- [ ] 2ª ordem: ζ e ωn do denominador; Mp, tp, ts (2 % = 4/ζωn), tr?
- [ ] Routh: 1ª coluna, sinais, casos especiais; faixa de K = interseção das desigualdades?
- [ ] Root locus: polos/zeros certos, eixo real (ímpar), assíntotas, saída válida, jω por Routh?
- [ ] Conferi no MATLAB quando pedido?
