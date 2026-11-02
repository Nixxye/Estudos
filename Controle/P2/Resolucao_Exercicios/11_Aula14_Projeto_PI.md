# Aula 14: Exemplo completo de projeto de PI (G = 1/(s+12))

**Origem:** `Exercicios_P2.pdf` págs. 50 a 57 (Aula 14, slides 3 a 10). É o modelo exato para a Q2 do Relatório 04.

## Enunciado

Deseja-se que o sistema `G(s) = 1/(s+12)`, com realimentação unitária, tenha **Mp ≤ 10 %**, **erro nulo** ao degrau e **ts (2 %) ≤ 0,5 s**. Projete um controlador **PI** `C(s) = Kp + Ki/s`.

## Resolução (os passos da Aula 14)

**Passo 1: polos dominantes desejados** (slide 4).

- Overshoot: `0,1 = e^(−πζ/√(1−ζ²))` → **`ζmin = 0,59`**.
- Acomodação: `ts = 4/(ζωn) = 0,5` → **`(ζωn)min = 8`**, então `ωn = 8/0,59 = 13,56`.
- `ωd = 13,56·√(1 − 0,59²) = 10,9`.
- Polos desejados: **`s₀ = −8 ± j10,9`**.

**Passo 2: só P resolve?** Planta de 1ª ordem com P só tem **polo real** (nunca o par complexo −8 ± j10,9); e com P o erro seria `1/(1 + Kp/12) ≠ 0`. **PI necessário** (o polo em 0 zera o erro).

**Passo 3: condição de fase** (slides 5 e 6). `C·G = Kp(s+z)/(s(s+12))`. Ângulos até `s₀ = −8 + j10,9`:

- polo em 0: `180° − tan⁻¹(10,9/8) = 126,3°`
- polo em −12: `tan⁻¹(10,9/4) = 69,8°`
- Condição `θz − 126,3° − 69,8° = −180°` → **`θz = 16,1°`**.
- `tan(16,1°) = 10,9/(z − 8) = 0,289` → `z − 8 = 37,7` → **`z = 45,7`**.

**Passo 4: condição de módulo.** `|C·G| = 1` em `s₀`:

- `|s₀| = |−8 + j10,9| = 13,5`
- `|s₀ + 12| = |4 + j10,9| = 11,6`
- `|s₀ + 45,7| = |37,7 + j10,9| = 39,2`
- **`Kp = |s₀|·|s₀+12|/|s₀+z| = 13,5·11,6/39,2 = 4`**
- **`Ki = z·Kp = 45,7·4 ≈ 182,6`** (o slide traz 182,6; arredondando `45,7·4 = 182,8`).

`C(s) = 4 + 182,6/s`. Malha fechada: `T = 4(s + 45,7)/((s+8−j10,9)(s+8+j10,9))`.

**Passo 5: testar** (slide 8). Simulação: **Mp ≈ 10,5 % (> 10 %)**, ts < 0,5 s. Precisa de **ajuste fino**.

**Ajuste fino** (slide 9): reduz o ganho e **mantém o zero** (`z = 45,7`):

- `Kp = 0,8·4 = 3,2` e **`Ki = z·Kp = 45,7·3,2 = 146,2`**.
- `C(s) = 3,2 + 146,2/s`.
- Simulação: **Mp = 8,2 % (< 10 %)** e **ts = 0,47 s (< 0,5 s)** ✔.

**Malha fechada final** (slide 10): `T = 3,2(s + 45,7)/((s+7,6−j9,4)(s+7,6+j9,4))`.

**Erro:** o PI tem polo em 0, então a malha é **tipo 1**: erro ao degrau **zero** ✔.

## Resposta

`C(s) = 3,2 + 146,2/s`: Mp = 8,2 %, ts = 0,47 s, erro ao degrau 0.

> **Atenção, diferença para a Q1 e a Aula 13:** aqui o ajuste fino **reduz** o ganho (porque o zero em −45,7 está longe e o Mp passa só um pouco). Na Q2 do Relatório 04 o caminho foi outro (mover o zero). Não existe receita única; a ideia é testar `Kp` e `z` por simulação ([02_Rel04_Q2_PI.md](02_Rel04_Q2_PI.md)).

## Conferência (simulação)

| Caso | Mp | ts (2 %) |
|---|---|---|
| Projeto: Kp = 4, Ki = 182,6 | 10,5 % | 0,415 s |
| Ajuste: Kp = 3,2, Ki = 146,2 | 8,24 % | 0,472 s |

Polos do projeto original: raízes de `s² + 16s + 182,8` = **−8 ± j10,9** ✔; do ajuste: `s² + 15,2s + 146,2` = **−7,6 ± j9,4** ✔.

## MATLAB

```matlab
clear all
clc
G = tf(1, [1 12]);
C = tf([3.2 146.2], [1 0]);          % 3,2 + 146,2/s
T = feedback(C*G, 1);
step(T); grid;
rlocus(tf([1 45.7],[1 0])*G); grid;  % passa por -8 +- j10.9
```
