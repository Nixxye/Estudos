# Aula 10: Exemplo: compensador por atraso de fase (LAG)

**Origem:** `Exercicios_P2.pdf` págs. 9 a 12 (Aula 10, slides 19, 20, 21 e 22).

## Enunciado

Dado o sistema `G(s) = K(s+8) / ((s+3)(s+2)(s+1))`, com realimentação unitária, reduza o **erro estacionário ao degrau** usando um compensador LAG

`Gc(s) = Kc (s + 1/T) / (s + 1/(αT))`, com `T = α = 10`, isto é, `Gc(s) = Kc (s + 0,1)/(s + 0,01)`.

Compare as respostas ao degrau **sem** e **com** compensação.

## Resolução

**Passo 1: ganho DC da planta.** `G(0) = K·8/(3·2·1) = 4K/3`.

**Passo 2: ganho DC do compensador.** `Gc(0) = Kc·(0,1/0,01) = 10·Kc`, ou seja, `Kc·α`. Essa é a ideia do LAG: **multiplica o ganho DC por α** sem mexer no resto do lugar das raízes, porque o par polo-zero (−0,01 e −0,1) fica colado na origem.

**Passo 3: erro ao degrau** (teorema do valor final, realimentação unitária):

`e(∞) = 1 / (1 + Gc(0)·G(0))`

**Passo 4: ganho limite por Routh (planta sem compensador).**

Polinômio característico de `1 + G(s) = 0`:

`(s+3)(s+2)(s+1) + K(s+8) = s³ + 6s² + (11+K)s + (6+8K)`

(`(s+3)(s+2)(s+1) = s³ + 6s² + 11s + 6` e `K(s+8) = Ks + 8K`.)

**Tabela de Routh:**

| Linha | 1ª coluna | 2ª coluna |
|---|---|---|
| s³ | 1 | 11 + K |
| s² | 6 | 6 + 8K |
| s¹ | `b₁` | 0 |
| s⁰ | 6 + 8K | |

Cálculo de `b₁` (1º elemento da linha s² × 2º da linha s³, menos 1º da s³ × 2º da s², tudo dividido pelo 1º da linha s²):

`b₁ = [6·(11+K) − 1·(6+8K)] / 6 = (66 + 6K − 6 − 8K)/6 = (60 − 2K)/6 = 10 − K/3`

**Condições (toda a 1ª coluna positiva):**

- `1 > 0` e `6 > 0`: sempre.
- s¹: `10 − K/3 > 0` → **K < 30**.
- s⁰: `6 + 8K > 0` → `K > −0,75`, e como K > 0 já vale.

Logo o sistema é estável para **0 < K < 30**, e o **ganho limite é K = 30** (a linha s¹ zera).

**Frequência de oscilação em K = 30** (equação auxiliar, tirada da linha **s²**, a de cima da linha zerada):

`6s² + (6 + 8·30) = 0` → `6s² + 246 = 0` → `s² = −41` → **s = ± j6,40**

É por isso que em K = 28 os polos ficam em ≈ `−0,03 ± j6,2` (quase em jω, resposta muito oscilatória).

**Passo 4b: Routh com o compensador** (confere que o LAG não estraga a estabilidade). Seja `q = Kc·K`. Com `Gc = Kc(s+0,1)/(s+0,01)`, a equação característica é `(s+3)(s+2)(s+1)(s+0,01) + q(s+8)(s+0,1) = 0`:

`s⁴ + 6,01s³ + (11,06 + q)s² + (6,11 + 8,1q)s + (0,06 + 0,8q) = 0`

Exemplo numérico, **K = 1 e Kc = 5** (`q = 5`):

| Linha | 1ª coluna | 2ª coluna | 3ª coluna |
|---|---|---|---|
| s⁴ | 1 | 16,06 | 4,06 |
| s³ | 6,01 | 46,61 | 0 |
| s² | 8,30 | 4,06 | |
| s¹ | 43,67 | 0 | |
| s⁰ | 4,06 | | |

(`s² : (6,01·16,06 − 46,61)/6,01 = 8,30`; `s¹ : (8,30·46,61 − 6,01·4,06)/8,30 = 43,67`.)

A 1ª coluna é toda positiva, então o sistema **é estável com Kc = 5**. O limite de `q` com o LAG sai de zerar `s¹`: `q ≈ 27,2` (um pouco menor que 30; o polo extra tira um pouco da margem). Então com K = 1 qualquer `Kc < 27` é estável, e a escolha Kc = 5 do slide está bem longe do limite.

**Passo 5: quatro casos.**

| Caso | Conta | e(∞) | Comentário |
|---|---|---|---|
| Sem LAG, K = 1 | `1/(1 + 4/3) = 3/7` | **0,429** | valor final = 4/7 = 0,571 |
| Sem LAG, K = 28 | `1/(1 + 4·28/3) = 3/115` | **0,026** | K quase no limite 30: muito oscilatória (polos em ≈ −0,03 ± j6,2) |
| Com LAG, Kc = 1, K = 1 | `1/(1 + 10·4/3) = 3/43` | **0,070** | ganho DC ×10 |
| Com LAG, **Kc = 5**, K = 1 | `1/(1 + 50·4/3) = 3/203` | **0,015** | erro menor que o de K = 28, **sem** chegar perto da instabilidade |

**Passo 6: lugar das raízes** (slide 22). Com o LAG, o lugar é **praticamente o mesmo** do original, porque o polo e o zero do compensador estão perto da origem e quase se cancelam. Só um ramo extra curto aparece entre −0,1 e −0,01.

## Resposta

O LAG de `T = α = 10` multiplica o ganho DC por 10 e reduz o erro de 0,429 (K = 1) para 0,070 (Kc = 1) e 0,015 (Kc = 5), **sem mover os polos dominantes**. O custo é uma resposta **mais lenta** (o polo em −0,01 cria uma cauda lenta).

## Conferência

Valores de `e(∞)` conferidos pelos ganhos DC (cálculo direto e simulação). O valor final sem LAG com K = 1 é `4/7`.

## MATLAB (forma do slide)

```matlab
clear all
clc
K = 1; Kc = 5;
G  = tf(K*[1 8], conv(conv([1 3],[1 2]),[1 1]));
Gc = tf(Kc*[1 0.1], [1 0.01]);
T1 = feedback(G, 1);          % sem compensação
T2 = feedback(Gc*G, 1);       % com LAG
step(T1, T2); grid;
figure; rlocus(G); figure; rlocus(Gc*G);
```
