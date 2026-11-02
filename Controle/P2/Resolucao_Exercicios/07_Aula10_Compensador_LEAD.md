# Aula 10: Exemplo: compensador por avanço de fase (LEAD)

**Origem:** `Exercicios_P2.pdf` págs. 13 a 16 (Aula 10, slides 24, 25, 26 e 27).

## Enunciado

Dado `G(s) = K / ((s+3)(s+2))`, com realimentação unitária, projete um compensador LEAD

`Gc(s) = Kc (s + 1/T)/(s + 1/(αT))`, com `0 < α < 1`,

de modo que os **polos dominantes de malha fechada** fiquem em `s = −4 ± j4`.

## Resolução

**Passo 1: por que só o ganho não resolve.** O lugar das raízes de `K/((s+2)(s+3))` é uma **reta vertical em σ = −2,5**. Ela nunca passa por −4 ± j4, então aumentar K não basta: falta ângulo, e é isso que o LEAD fornece.

**Passo 2: ângulos dos polos da planta até `s₀ = −4 + j4`** (anti-horário, contados a partir do eixo real positivo):

- polo −2: o vetor `s₀ + 2 = −2 + j4` tem ângulo `180° − tan⁻¹(4/2) = 116,57°`
- polo −3: o vetor `s₀ + 3 = −1 + j4` tem ângulo `180° − tan⁻¹(4/1) = 104,04°`

**Passo 3: condição de fase.** Zero e polo do compensador precisam fechar `θz − θp − 116,57° − 104,04° = −180°`. O professor **escolhe o zero** e calcula o polo.

**1ª tentativa, zero em −4** (ângulo `90°`, vetor vertical):

`θp = 90° − 104,04° − 116,57° + 180° = 49,39°` → `p = 4 + 4/tan(49,39°) = 7,42`.

O polo em −7,42 fica **perto** dos polos da planta (−2 e −3) e poderia competir como dominante. Refaz.

**2ª tentativa, zero em −5** (ângulo `tan⁻¹(4/1) = 75,96°`):

`θp = 75,96° − 104,04° − 116,57° + 180° = 35,35°`; `tan(35,35°) = 0,71` → **`p = 4 + 4/0,71 = 9,63`**.

Agora o polo está bem à esquerda dos da planta e não domina.

**Passo 4: parâmetros do compensador** (`Gc = Kc (s+5)/(s+9,63)`):

- `1/T = 5` → `T = 0,2`
- `1/(αT) = 9,63` → `α = 1/(0,2·9,63) = 0,52`, e `0 < α < 1` confirma que é **LEAD**.

**Passo 5: condição de módulo** em `s₀`:

`Kc·K = |s₀+2|·|s₀+3|·|s₀+9,63| / |s₀+5| = (4,472 · 4,123 · 6,906) / 4,123 = 30,9`

(`|s₀+2| = |−2+j4| = 4,472`; `|s₀+3| = |−1+j4| = 4,123`; `|s₀+9,63| = |5,63+j4| = 6,906`; `|s₀+5| = |1+j4| = 4,123`.)

## Resposta

`Gc(s) = Kc (s+5)/(s+9,63)`, com **`Kc·K = 30,9`** e **`α = 0,52`**. Malha aberta `Gc·G = Kc·K (s+5)/((s+9,63)(s+3)(s+2))`. O lugar das raízes passa por **−4 ± j4** quando `Kc·K = 30,9`.

**Por que o zero em −5 e não em −4?** O polo do compensador tem de ficar **bem à esquerda** dos polos da planta para **não ser dominante**: −7,42 era perto demais; −9,63 é melhor. O zero é escolha livre, e o professor testa até o polo cair longe.

## Conferência

Ângulos e módulos recalculados com numpy: `[116,57°; 104,04°; 90°; 75,96°]` para os fatores `s₀+2`, `s₀+3`, `s₀+4`, `s₀+5`. O produto dos módulos reproduz **30,9**. Com `Kc·K = 30,9`, os polos de malha fechada são `−4 ± j4` (dominantes) e um polo real em `−6,63`, que fica perto do zero em −5 e pouco atrapalha.

## MATLAB (forma do slide)

```matlab
clear all
clc
G  = tf(1, conv([1 3],[1 2]));
Gc = tf([1 5], [1 9.63]);
rlocus(Gc*G); grid;           % passa por -4 +- j4
K = 30.9;
step(feedback(K*Gc*G, 1)); grid;
```
