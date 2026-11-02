# Aula 10: Exercício: mapa de polos e zeros e resposta ao degrau de T₁, T₂, T₃

**Origem:** `Exercicios_P2.pdf` págs. 4 a 6 (Aula 10, slides 3, 4 e 5). É o único item que o slide chama de "Exercício".

## Enunciado

Faça o mapa de polos e zeros e a resposta ao degrau dos 3 sistemas:

- `T₁(s) = 40 / ((s+20)(s+1+j)(s+1−j))`
- `T₂(s) = 3 / ((s+1,5)(s+1+j)(s+1−j))`
- `T₃(s) = 2 / ((s+1+j)(s+1−j))`

## Resolução (passo a passo, no estilo do professor)

**Passo 1: polos e zeros.** Nenhum dos três tem zeros (numerador constante). Os polos saem direto dos fatores do denominador (`s + a` dá polo em `−a`):

| | Polos |
|---|---|
| `T₃` | −1 ± j |
| `T₁` | −1 ± j **e −20** |
| `T₂` | −1 ± j **e −1,5** |

![Mapa de polos e resposta ao degrau](img/aula10_exercicio.png)

**Passo 2: valor final da resposta ao degrau** (teorema do valor final, `T(0)`):

- `T₁(0) = 40/(20·2) = 1`
- `T₂(0) = 3/(1,5·2) = 1`
- `T₃(0) = 2/2 = 1`

Os três terminam em **1**. (O fator `(s+1+j)(s+1−j) = s² + 2s + 2` vale 2 em s = 0.)

**Passo 3: frações parciais** (`[r,p,k] = residue(num,den)` no MATLAB; os resíduos são os do slide):

| | Resíduo do polo real | Resíduos do par complexo |
|---|---|---|
| `T₁` | **0,1105** (polo −20) | −0,0552 ∓ j1,0497 (módulo 1,051) |
| `T₂` | **2,4** (polo −1,5) | −1,2 ∓ j0,6 (módulo 1,342) |
| `T₃` | não tem | ∓ j1 (módulo 1) |

**Passo 4: aplicar a regra de dominância** (slides 4 e 5). Um polo é desprezível quando:

1. Está **pelo menos 5 vezes mais longe do eixo jω** que os dominantes, e
2. Tem **resíduo pequeno** em relação aos dos dominantes.

| | Relação das partes reais | Resíduo do polo real × complexos | Conclusão |
|---|---|---|---|
| `T₁` | 20/1 = **20 > 5** | **0,11 ≪ 1,05** | o polo −20 **não domina**: `T₁ ≈ T₃` |
| `T₂` | 1,5/1 = **1,5 < 5** | **2,4 > 1,34** | o polo −1,5 **domina/compete**: `T₂` **não** se comporta como 2ª ordem |

**Passo 5: resposta ao degrau** (confirmada por simulação):

| Sistema | Overshoot | ts (2 %) | Leitura |
|---|---|---|---|
| `T₃` (ωn = √2, ζ = 0,707) | 4,3 % | ≈ 4,2 s | 2ª ordem padrão |
| `T₁` | 4,3 % | ≈ 4,3 s | **quase idêntica a T₃** (polo −20 desprezível) |
| `T₂` | 1,7 % | ≈ 3,3 s | polo −1,5 dominante: mais lenta no início e sem overshoot relevante |

## Resposta

`T₁` se comporta como `T₃` (3ª ordem aproximada por 2ª pelos polos dominantes −1 ± j). `T₂` tem polo real próximo e resíduo grande, então **não** pode ser aproximada por 2ª ordem.

**Frase do slide (p.4):** "A F.T. de terceira ordem `T₁(s)` se comporta como a de segunda `T₃(s)` devido aos polos dominantes."

## MATLAB

```matlab
clear all
clc
T1 = tf(40, conv([1 20], [1 2 2]));
T2 = tf(3, conv([1 1.5], [1 2 2]));
T3 = tf(2, [1 2 2]);
figure(1); pzmap(T1, T2, T3); grid;
figure(2); step(T1, T2, T3); grid;
[r, p, k] = residue(40, conv([1 20], [1 2 2]))   % resíduos de T1
```

*(MATLAB não foi rodado aqui; os números foram conferidos com Python/scipy.)*
