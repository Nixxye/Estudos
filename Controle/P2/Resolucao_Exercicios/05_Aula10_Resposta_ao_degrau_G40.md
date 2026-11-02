# Aula 10: Exemplo: resposta ao degrau de G = 40 / ((s+20)(s+2)(s+1))

**Origem:** `Exercicios_P2.pdf` págs. 7 e 8 (Aula 10, slides 6 e 7).

## Enunciado

Calcule a resposta ao degrau unitário de

`G(s) = 40 / ((s+20)(s+2)(s+1)) = 40 / (s³ + 23s² + 62s + 40)`

## Resolução

**Passo 1: frações parciais.** Como os polos são reais e distintos:

`G(s) = A/(s+20) + B/(s+2) + C/(s+1)`

Cada resíduo é `A = lim (s+20)·G(s)` (cobrir o fator e calcular no polo):

- `A = 40/((−20+2)(−20+1)) = 40/((−18)(−19)) = 0,117`
- `B = 40/((−2+20)(−2+1)) = 40/(18·(−1)) = −2,222`
- `C = 40/((−1+20)(−1+2)) = 40/(19·1) = 2,105`

`G(s) = 0,117/(s+20) − 2,222/(s+2) + 2,105/(s+1)`

**Passo 2: entrada degrau.** `Y(s) = G(s)/s`. Cada termo vira `K/(s(s+a))`, cuja inversa é `(K/a)(1 − e^(−at))`:

`y(t) = (0,117/20)(1 − e^(−20t)) − (2,222/2)(1 − e^(−2t)) + (2,105/1)(1 − e^(−t))`

## Resposta

**`y(t) = 0,006(1 − e^(−20t)) − 1,111(1 − e^(−2t)) + 2,105(1 − e^(−t))`**

## Conferência

- **Valor final:** `0,006 − 1,111 + 2,105 = 1,000`. Bate com `G(0) = 40/40 = 1`.
- **Dominância:** o termo do polo −20 vale só **0,006** (desprezível). A resposta é comandada pelos polos −1 e −2, e o polo −1 domina o final.
- **Resíduos:** conferidos com `signal.residue`, resultado `[2,105; −2,222; 0,117]` para polos `[−1; −2; −20]`.

## MATLAB

```matlab
num = 40; den = conv(conv([1 20], [1 2]), [1 1]);
[r, p, k] = residue(num, den)
G = tf(num, den);
step(G); grid;
```
