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

**Passo 4: ganho limite da planta** (Routh). Polinômio característico `(s+3)(s+2)(s+1) + K(s+8) = s³ + 6s² + (11+K)s + (6+8K)`. Na linha s¹: `6(11+K) = 6 + 8K` → **K = 30**. Acima de 30 o sistema fica instável.

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
