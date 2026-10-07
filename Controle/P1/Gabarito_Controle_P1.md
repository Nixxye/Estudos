# Gabarito comentado: Listas 01 e 02 (Controle A, P1)

Cada questão aplica **os passos do tutorial** ([Tutorial_Controle_P1.md](Tutorial_Controle_P1.md)); a teoria está em [Resumo_Controle_P1.md](Resumo_Controle_P1.md). Conferência no MATLAB: [guia_P1_matlab.m](guia_P1_matlab.m).

**Correspondência entre as listas** (mesmos diagramas):

| Lista 01 | Lista 02 |
|---|---|
| Q1 | Q1(d) |
| Q2 | Q2 |
| Q3 | Q3 |
| Q4, Q5 | (só na Lista 01) |
| (não existe) | Q1(a), (b), (c) |

Convenção usada: **cada somador vira uma equação**, sinais como no diagrama.

Índice: [L2-Q1(a)](#q1a) · [L2-Q1(b)](#q1b) · [L2-Q1(c)](#q1c) · [L1-Q1 = L2-Q1(d)](#q1d) · [Q2](#q2) · [Q3](#q3) · [L1-Q4](#q4) · [L1-Q5](#q5)

---

<a id="q1a"></a>
## L2-Q1(a): `C/R = (G + H1)/(1 + G·H2)`

**Diagrama:** R entra no somador 1 (+R, −sinal de H2). A saída do somador 1 (que chamo de **E**) se ramifica para dois blocos em paralelo: G (no meio) e H1 (em cima). A saída de G alimenta H2 (realimentação, ponto de ramificação **depois de G, antes do somador final**) e o somador final (+). H1 também entra no somador final (+).

**Passo 1: nomear os sinais.** E = saída do somador 1; C = saída do somador final.

**Passo 2: equação de cada somador.**
- Somador 1: `E = R − H2·G·E`  (H2 lê a saída de G, que vale `G·E`)
- Somador final: `C = G·E + H1·E`

**Passo 3: isolar E.** `E(1 + G·H2) = R` → `E = R/(1 + G·H2)`

**Passo 4: substituir.** `C = (G + H1)·E = (G + H1)·R/(1 + G·H2)`

**Resposta:** `C(s)/R(s) = (G + H1)/(1 + G·H2)` ✓ (igual à solução da lista).

Pelas regras (caminho 2): `G` e `H1` estão em **paralelo** → `G + H1`? Não diretamente, porque H2 só lê G. Por isso o caminho 1 é mais seguro aqui. (Truque: mover o ponto de ramificação de H2 para depois do somador final exigiria dividir por `(G+H1)/G`, o que complica.)

**Erro comum:** usar `(G+H1)/(1+(G+H1)H2)`. Não vale porque H2 lê a saída de G, não C.

---

<a id="q1b"></a>
## L2-Q1(b): `C/R = G1·G2 + G2 + 1`

**Diagrama (sem realimentação):** R vai a G1 e também direto (por um ramo inferior) ao somador 1 e ao somador 2. Somador 1 (+ G1·R, + R) gera X; X passa por G2 e entra no somador 2, que soma também R diretamente.

**Passo 1:** sinais X e C.

**Passo 2: equações.**
- Somador 1: `X = G1·R + R = (G1 + 1)·R`
- Somador 2: `C = G2·X + R`

**Passo 3: substituir X.** `C = G2(G1 + 1)R + R = (G1G2 + G2 + 1)·R`

**Resposta:** `C/R = G1·G2 + G2 + 1` ✓. (Sem laço de realimentação, então não há denominador.)

Leitura por caminhos: há três caminhos de R até C: `G1·G2`, `G2` (pelo ramo direto até o somador 1) e `1` (ramo inferior até o somador 2), e a resposta é a soma dos três.

---

<a id="q1c"></a>
## L2-Q1(c): `C/R = (G1 + G2)/(1 + (G1 + G2)(G3 − G4))`

**Diagrama:** R − (realimentação) = E; E vai a G1 e G2 em paralelo, cuja soma é C. A realimentação usa G3 e G4 lendo C; o somador da realimentação tem **+G3** e **−G4**, e o resultado F entra com sinal − no somador de entrada.

**Passo 1: sinais.** E = erro, F = sinal de realimentação.

**Passo 2: equações.**
- Realimentação: `F = G3·C − G4·C = (G3 − G4)·C`
- Somador de entrada: `E = R − F`
- Saída: `C = (G1 + G2)·E`  (dois blocos em paralelo somando)

**Passo 3: substituir.** `C = (G1 + G2)(R − (G3 − G4)C)`
→ `C[1 + (G1+G2)(G3−G4)] = (G1+G2)R`

**Resposta:** `C/R = (G1+G2)/(1 + (G1+G2)(G3−G4))` ✓.

Pelas regras (caminho 2): (1) paralelo G1//G2 = `G1+G2`; (2) paralelo G3 e G4 com sinais = `G3−G4`; (3) feedback `G/(1+GH)` com `G = G1+G2`, `H = G3−G4`.

---

<a id="q1d"></a>
## L1-Q1 = L2-Q1(d): `C/R = (1 + G1)·G2/(1 + G2(H1 − H2))`

**Diagrama:** R vai (a) ao somador 1 (com −F) e (b) por G1 ao somador 2. O somador 2 soma `E` (saída do somador 1) e `G1·R`. A saída do somador 2 passa por G2 e é C. A realimentação: H1 (+) e H2 (−) lendo C, num somador que gera F, que entra com − no somador 1.

**Passo 1: sinais.** F (realimentação), E (saída do somador 1), U (saída do somador 2).

**Passo 2: equações.**
- `F = H1·C − H2·C`
- `E = R − F`
- `U = E + G1·R`
- `C = G2·U`

**Passo 3: substituir.**
`U = R − (H1−H2)C + G1·R = (1 + G1)R − (H1−H2)C`
`C = G2·U = G2(1+G1)R − G2(H1−H2)C`

**Passo 4: isolar.** `C[1 + G2(H1−H2)] = G2(1+G1)R`

**Resposta:** `C/R = (1+G1)·G2/(1 + G2(H1−H2))` ✓.

Pelas regras (caminho 2): o somador 2 fica **dentro** do laço, e G1 entra direto de R. Movendo G1 para antes do somador (como no exemplo *feed-forward* da Aula 5) ou notando que o ramo `R → (1 + G1)` alimenta o laço, tira-se o fator `(1+G1)` na frente e resta o laço `G2` com `H = H1−H2`: `(1+G1)·G2/(1 + G2(H1−H2))`.

---

<a id="q2"></a>
## L1-Q2 = L2-Q2: `C = (Gc·Gp·R + D)/(1 + Gc·Gp)`

**Diagrama:** R − C = E → Gc → Gp → somador (+D) → C, e C realimenta unitariamente.

**Passo 1: sinais.** E = erro. C = saída (depois do somador da perturbação).

**Passo 2: equações.**
- `E = R − C`
- `C = Gc·Gp·E + D`  (D entra depois de Gp)

**Passo 3: substituir.** `C = Gc·Gp(R − C) + D = Gc·Gp·R − Gc·Gp·C + D`
→ `C(1 + Gc·Gp) = Gc·Gp·R + D`

**Resposta:** `C(s) = [Gc(s)Gp(s)·R(s) + D(s)]/(1 + Gc(s)Gp(s))` ✓.

**Conferência por superposição (caminho da Aula 5):**
- D = 0: `C/R = GcGp/(1+GcGp)`.
- R = 0: `C/D = 1/(1+GcGp)`; a perturbação é dividida por `1 + GcGp`, e por isso a malha fechada **reduz** o efeito de D quando `GcGp` é grande.
- Soma: `C = GcGp/(1+GcGp)·R + 1/(1+GcGp)·D` ✓.

---

<a id="q3"></a>
## L1-Q3 = L2-Q3: `Eo/Ei = (R2C2·s + 1)/((R1C2 + R2C2)·s + 1 + C2/C1)`

**Circuito:** entrada `ei` aplicada em série R1–C1; no nó de saída sai R2–C2 para o terra; `eo` é a tensão sobre o ramo R2–C2 (sem carga na saída).

**Passo 1: impedâncias em Laplace.** Capacitor = `1/(sC)`.
- `Z1 = R1 + 1/(sC1) = (R1C1·s + 1)/(C1·s)` (braço série)
- `Z2 = R2 + 1/(sC2) = (R2C2·s + 1)/(C2·s)` (braço da saída)

**Passo 2: divisor de tensão** (sem carga, mesma corrente nos dois braços): `Eo/Ei = Z2/(Z1 + Z2)`.

**Passo 3: montar a fração.** Denominador comum `C1C2·s`:
- `Z2 = C1(R2C2·s+1)/(C1C2·s)`
- `Z1 + Z2 = [C2(R1C1·s+1) + C1(R2C2·s+1)]/(C1C2·s)`

**Passo 4: dividir (o fator `1/(C1C2·s)` cancela).**
`Eo/Ei = C1(R2C2·s+1)/[R1C1C2·s + C2 + R2C1C2·s + C1]`
`= C1(R2C2·s+1)/[C1(R1C2 + R2C2)·s + C1 + C2]`

**Passo 5: dividir numerador e denominador por C1.**

**Resposta:** `Eo/Ei = (R2C2·s + 1)/((R1C2 + R2C2)·s + 1 + C2/C1)` ✓.

**Conferência (sanidade):** em DC (s → 0) os capacitores abrem e sobra o divisor capacitivo: `Eo/Ei = 1/(1 + C2/C1) = C1/(C1 + C2)` ✓. Em altas frequências (s → ∞) os capacitores viram curtos e sobra o divisor resistivo: `R2/(R1+R2)` (razão dos coeficientes em s) ✓.

---

<a id="q4"></a>
## L1-Q4: e(∞) para degrau unitário

**Sistema:** realimentação unitária, `G(s) = 100/((s+1)(s+10))`, `X = 1/s`.

**Passo 1: estabilidade.** Malha fechada: `1 + G = 0` → `(s+1)(s+10) + 100 = s² + 11s + 110`. Coeficientes todos positivos, ordem 2 → **estável**.

**Passo 2: tipo.** Não há `s` puro no denominador → **tipo 0**. Realimentação unitária.

**Passo 3: entrada.** Degrau.

**Passo 4: constante (método da tabela).**
`Kp = lim(s→0) G(s) = 100/(1·10) = 10`
`e(∞) = 1/(1 + Kp) = 1/11 ≈ 0,09`

**Passo 5: método direto (confirmação).**
`E(s) = X(s)/(1+G(s))`, `e(∞) = lim(s→0) s·(1/s)·1/(1+G) = 1/(1+G(0)) = 1/(1+10) = 1/11`

**Resposta:** **e(∞) = 1/11 ≈ 0,0909** (é o "erro = 0,09" do slide da Aula 4).

---

<a id="q5"></a>
## L1-Q5: e(∞) para rampa, sistema com integrador

**Sistema:** realimentação unitária, `G(s) = 100/((s+1)(s+10)) · 1/s = 100/(s(s+1)(s+10))`, `X = 1/s²`.

**Passo 1: estabilidade.** Malha fechada: `s(s+1)(s+10) + 100 = s³ + 11s² + 10s + 100`.
Routh:

| | | |
|---|---|---|
| s³ | 1 | 10 |
| s² | 11 | 100 |
| s¹ | (11·10 − 1·100)/11 = 10/11 ≈ 0,91 | 0 |
| s⁰ | 100 | |

Primeira coluna toda positiva → **estável** (por pouco: o `0,91` é pequeno, então a resposta é bem oscilatória).

**Passo 2: tipo.** Um `s` no denominador → **tipo 1**.

**Passo 3: entrada.** Rampa `X = 1/s²`.

**Passo 4: constante (tabela).**
`Kv = lim(s→0) s·G(s) = 100/(1·10) = 10`
`e(∞) = 1/Kv = 0,1`

**Passo 5: direto.**
`e(∞) = lim(s→0) s·(1/s²)/(1+G) = lim 1/(s + s·G(s)) = 1/(0 + Kv) = 1/10`

**Resposta:** **e(∞) = 0,1.**

**Comparação com a Q4 (comentário do professor):** o integrador zera o erro ao **degrau** (tipo 1), mas o sistema fica mais oscilatório e com **maior tempo de acomodação**. Sem o integrador (tipo 0), a rampa daria erro **infinito**.

> Observação: nos slides da Aula 4 o cálculo intermediário da rampa aparece como `10/102`; o valor correto é `10/100 = 1/10`, coerente com o `e(∞) = 1/Kv` que o próprio slide mostra.

---

## Resumo das respostas

| Questão | Resposta |
|---|---|
| L2-Q1(a) | `(G + H1)/(1 + G·H2)` |
| L2-Q1(b) | `G1·G2 + G2 + 1` |
| L2-Q1(c) | `(G1+G2)/(1 + (G1+G2)(G3−G4))` |
| L1-Q1 = L2-Q1(d) | `(1+G1)G2/(1 + G2(H1−H2))` |
| L1-Q2 = L2-Q2 | `C = (Gc·Gp·R + D)/(1 + Gc·Gp)` |
| L1-Q3 = L2-Q3 | `(R2C2·s+1)/((R1C2+R2C2)s + 1 + C2/C1)` |
| L1-Q4 | `e(∞) = 1/11 ≈ 0,09` |
| L1-Q5 | `e(∞) = 0,1` |
