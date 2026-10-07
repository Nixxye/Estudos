# Resumo P1: Sistemas de Controle A (ELN77A)

Prof. Ronaldo Guisso (UTFPR), 2025-2. Cobre `Slides/` (Aulas 1 a 9 e Introdução). Ligação com as listas em [Tutorial_Controle_P1.md](Tutorial_Controle_P1.md). O código MATLAB das listas está em [guia_P1_matlab.m](guia_P1_matlab.m).

> Limitação: extraí o texto dos slides. Na Aula 9 (`.pptx`) as fórmulas são imagens e não consegui lê-las; a parte de **feedback positivo** foi completada com o padrão da teoria (marcada com 🧩). Confira com o caderno.

## Índice

1. [Avaliação e visão geral](#s1)
2. [Função de transferência (Aula 1)](#s2)
3. [Diagramas de blocos (Aulas 1 e 5)](#s3)
4. [Sistemas de 1ª ordem (Aula 2)](#s4)
5. [Sistemas de 2ª ordem (Aula 2)](#s5)
6. [MATLAB (Aula 3)](#s6)
7. [Erro em regime permanente (Aula 4)](#s7)
8. [Estabilidade e Routh-Hurwitz (Aula 6)](#s8)
9. [Lugar das raízes: conceito (Aula 7)](#s9)
10. [Lugar das raízes: passos (Aulas 8 e 9)](#s10)
11. [Fórmulas para a prova](#s11)

---

<a id="s1"></a>
## 1. Avaliação e visão geral

- 3 provas teóricas (P1, P2, P3) de peso 3,0 cada, prova prática PP1 (peso 1,0). **Nota final = P1 + P2 + P3 + PP1.** Quem tiver menos de 6,0 faz a PREC (peso 3, substitui a pior prova).
- Software: **MATLAB**. Livros: Dorf & Bishop, Ogata, Nise.
- Conteúdo da P1: função de transferência e diagramas de blocos → 1ª e 2ª ordem → erro em regime → Routh-Hurwitz → lugar das raízes.

<a id="s2"></a>
## 2. Função de transferência (Aula 1)

- **G(s) = L{saída} / L{entrada} com todas as condições iniciais nulas.** Forma geral: `Y/X = (b0 sᵐ + … + bm)/(a0 sⁿ + … + an)`, n = **ordem** do sistema, m ≤ n.
- Convenção: **maiúsculas = domínio de Laplace, minúsculas = tempo.**
- `y(t) = x(t) * g(t)` (convolução). **g(t) = resposta ao impulso**; para entrada impulso unitário, `Y(s) = G(s)` (sistema linear invariante no tempo).
- **Polos** = raízes do denominador; **zeros** = raízes do numerador.

<a id="s3"></a>
## 3. Diagramas de blocos (Aulas 1 e 5)

**Elementos:** bloco G(s); **somador** (sinais + e −, pode ter vários); **ponto de ramificação** (o mesmo sinal vai para vários lugares).

**Malha fechada típica:** ramo direto G(s), ramo de realimentação H(s), sinal de erro E = X − B, B = H·Y.

| Definição | Fórmula |
|---|---|
| Malha aberta | `G(s)H(s) = B(s)/E(s)` |
| Ramo direto | `G(s) = Y(s)/E(s)` |
| **Malha fechada** | **`Y/X = G / (1 + G·H)`** (realimentação negativa) |

Dedução: `Y = G·E`, `E = X − H·Y` → `Y(1 + GH) = G·X`.

**Simplificações (Aula 5):**

| Regra | Como |
|---|---|
| Série (cascata) | multiplica: `G1·G2` |
| Paralelo | soma: `G1 + G2` (com sinais dos somadores) |
| Feedback | `G/(1 + GH)` (negativo) |
| Somador para **antes** do bloco G | o sinal que entra no somador passa a ser dividido por G (ou o bloco é duplicado) |
| Somador para **depois** do bloco G | o sinal que entra é multiplicado por G |
| Ponto de ramificação para antes do bloco | leva um bloco G no ramo |
| Ponto de ramificação para depois do bloco | leva um bloco 1/G no ramo |
| Rearranjar somadores | somadores adjacentes podem trocar de ordem |
| Bloco de realimentação para antes do somador | ajusta com 1/G |

Exemplo *feed-forward* (slides): mover G1 para antes do somador, rearranjar, fazer paralelo e feedback, e por fim a série.

**Mais de uma entrada:** use **superposição**. Zere uma entrada por vez, calcule a saída para cada uma, e some:
`Y = G2/(1+G1G2H) · N + G1G2/(1+G1G2H) · X` (o slide mostra ruído N e entrada X).

**Efeito da malha fechada:** reduz o efeito de ruído/perturbação (`1/(1+GH)`), diminui o ganho e **aumenta a largura de banda** (resposta mais rápida).

<a id="s4"></a>
## 4. Sistemas de 1ª ordem (Aula 2)

`Y/X = 1/(Ts + 1) = (1/T)/(s + 1/T)`, **T = constante de tempo**. Exemplo: RC série com saída no capacitor (divisor de tensão): `1/(RCs+1)`, **T = RC**. Um integrador `1/(Ts)` com realimentação unitária também dá `1/(Ts+1)`.

- **Resposta ao degrau unitário:** `y(t) = 1 − e^(−t/T)`.
- **Em t = T:** `y(T) = 1 − e⁻¹ = 0,632`. **Identificação:** no gráfico da resposta ao degrau, T é o tempo em que a saída chega a **63,2 %** do valor final.
- Erro ao degrau: `e(t) = e^(−t/T)` → `e(∞) = 0`. Erro à rampa: `e(t) = T(1 − e^(−t/T))` → **`e(∞) = T`**.

<a id="s5"></a>
## 5. Sistemas de 2ª ordem (Aula 2)

Forma padrão (realimentação unitária de `ωn²/(s(s+2ζωn))`):

```
T(s) = ωn² / (s² + 2ζωn·s + ωn²)
```
**ωn** = frequência natural; **ζ** = fator de amortecimento (*damping*).

**Polos:** `p = −ζωn ± j·ωd`, com **ωd = ωn·√(1−ζ²)** (frequência amortecida). Geometria no plano s: `ωn² = (ζωn)² + ωd²` (módulo do polo), e `ζ = (parte real negativa)/ωn` = cos do ângulo do polo com o eixo real negativo.

Exemplo dos slides: `25/(s²+6s+25)` → polos −3 ± j4 → ωn = 5, ζ = 3/5 = 0,6, ωd = 5·√(1−0,36) = 4.

**Classificação:** ζ = 0 oscilatório (polos no eixo jω); 0 < ζ < 1 **subamortecido** (complexos conjugados); ζ = 1 **criticamente amortecido** (polos reais iguais); ζ > 1 **superamortecido** (dois reais distintos).

**Resposta ao degrau (subamortecido):** `c(t) = 1 − e^(−ζωn t)[cos(ωd t) + (ζ/√(1−ζ²)) sen(ωd t)]`.

**Especificações do transiente:**

| Grandeza | Fórmula | Significado |
|---|---|---|
| tempo de atraso td | – | atinge 50 % do valor final |
| **tempo de subida tr (0–100 %)** | `tr = (π − β)/ωd`, `β = tan⁻¹(√(1−ζ²)/ζ)` | 0 a 100 % pela 1ª vez |
| tr (10–90 %) | `(1,76ζ³ − 0,417ζ² + 1,039ζ + 1)/ωn` | o mais usado |
| **tempo de pico tp** | `π/ωd = π/(ωn√(1−ζ²))` | 1º máximo |
| **overshoot Mp** | `Mp = e^(−πζ/√(1−ζ²))` (fração) | máximo acima do valor final |
| **tempo de acomodação ts** | 1 %: `4,6/(ζωn)`; **2 %: `4/(ζωn)`**; 5 %: `3/(ζωn)` | fica dentro da faixa |

- Degrau não unitário: `Mp% = (c(tp) − c(∞))/c(∞) · 100`.
- **Mp depende só de ζ.** Aceitável entre 25 % e 4 % → **0,4 < ζ < 0,7**. Com ωn fixo não dá para diminuir overshoot e tr ao mesmo tempo.
- **Mapa no plano s:** ωn constante = círculos; ζ constante = retas radiais; ts constante = reta vertical (parte real); ωd constante (tp constante) = reta horizontal.

<a id="s6"></a>
## 6. MATLAB (Aula 3)

| Objetivo | Comando |
|---|---|
| Criar G(s) | `G = tf([b0 … bm],[a0 … an])` (vetores de coeficientes em potências decrescentes de s) |
| Cascata / paralelo / feedback | `series(G1,G2)` = `G1*G2`; `parallel(G1,G2)` = `G1+G2`; **`feedback(G1,G2)`** = `G1/(1+G1*G2)` |
| Polos e zeros | `[z,p,k] = tf2zp(num,den)`; `[num,den] = zp2tf(z,p,k)` |
| Extrair coeficientes | `[num,den] = tfdata(H,'v')` |
| Frações parciais | `[r,p,q] = residue(num,den)` |
| Resposta ao impulso / degrau | `impulse(G,tf)`, `step(G,tf)` |
| Entrada qualquer | `t = linspace(0,50,1000); r = t; lsim(G,r,t)` (rampa `r=t`; parábola `r=(t.^2)/2`) |
| Mapa de polos e zeros | `pzmap(G)` |
| Lugar das raízes | `rlocus(G*H)`; `axis([xmin xmax ymin ymax])` |

<a id="s7"></a>
## 7. Erro em regime permanente (Aula 4)

**Erro:** diferença entre a referência e a variável controlada. Só faz sentido se o sistema for **estável**.

- **Teorema do valor final:** `f(∞) = lim(s→0) s·F(s)`. **Valor inicial:** `f(0⁺) = lim(s→∞) s·F(s)`.
- Realimentação **unitária**: `E(s) = X(s)/(1 + G(s))`, então **`e(∞) = lim(s→0) s·X(s)/(1+G(s))`**.

**Tipo do sistema** = número de **integradores (polos em s = 0)** de G(s) em malha aberta: `G = K(Ta s+1)…/(sᴺ (T1 s+1)…)`, N = tipo. Tipo maior: mais precisão, mas mais instabilidade. **N não é a ordem.**

**Constantes de erro estático** (medem G perto de s=0):

| Constante | Fórmula | Entrada |
|---|---|---|
| Posição Kp | `lim(s→0) G(s)` | degrau |
| Velocidade Kv | `lim(s→0) s·G(s)` | rampa |
| Aceleração Ka | `lim(s→0) s²·G(s)` | parábola |

**Tabela de erro estacionário:**

| Tipo | Degrau (x=1) | Rampa (x=t) | Parábola (x=t²/2) |
|---|---|---|---|
| 0 | `1/(1+Kp)` | ∞ | ∞ |
| 1 | 0 | `1/Kv` | ∞ |
| 2 | 0 | 0 | `1/Ka` |

**Exemplos dos slides (as Questões 4 e 5 da Lista 01):**
- `G = 100/((s+1)(s+10))` (tipo 0): `Kp = 100/10 = 10`, degrau: `e(∞) = 1/(1+10) = 1/11 ≈ 0,09`.
- Adicionando integrador: `G = 100/(s(s+1)(s+10))` (tipo 1, `Kv = 10`): degrau → 0; **rampa → 1/Kv = 0,1**.
- Integrador zera o erro ao degrau, mas aumenta o tempo de acomodação.

**Ganho estático (DC):** `T(0) = lim(s→0) T(s)` para T estável sem polos na origem.

<a id="s8"></a>
## 8. Estabilidade e Routh-Hurwitz (Aula 6)

**Estável (BIBO):** entrada limitada dá saída limitada. Entradas limitadas: impulso, degrau; ilimitadas: rampa, parábola. Oscilatório sem amortecimento (polos em jω) = "marginalmente estável" e tratado na disciplina como **instável**. **Estável ⇔ todos os polos de malha fechada no semiplano esquerdo.**

**Procedimento (polinômio característico A(s) = a0 sⁿ + … + an = 0):**

1. Iguale A(s) a 0 e **remova raízes nulas** (`s⁴+2s³+3s² → s²+2s+3`).
2. **Se algum coeficiente for zero ou negativo** havendo algum positivo, é **instável**. Todos positivos **não** garante estabilidade → passo 3.
3. **Monte a tabela:** linhas 1 e 2 com coeficientes alternados (índices pares e ímpares); as demais por
   `b1 = (a1·a2 − a0·a3)/a1`, `b2 = (a1·a4 − a0·a5)/a1`, `c1 = (b1·a3 − a1·b2)/b1` … até s⁰.
   Pode dividir/multiplicar uma linha por número **positivo** para simplificar.
4. **Estável ⇔ todos os elementos da 1ª coluna positivos.** O **nº de mudanças de sinal na 1ª coluna = nº de polos no semiplano direito.**

Exemplo (slide): `s⁴+2s³+3s²+4s+5`: linhas s⁴ [1 3 5], s³ [1 2] (dividida por 2), s² [1 5], s¹ [−3], s⁰ [5] → 2 mudanças de sinal → **2 polos no SPD, instável**.

**Casos especiais:**

| Caso | O que fazer |
|---|---|
| **1. Zero na 1ª coluna** (resto da linha não nulo) | (a) `s = 1/x` e refaça em x; (b) multiplique A(s) por `(s+1)` e refaça; (c) troque o 0 por **ε → 0⁺** e tire o limite. Mudança de sinal → instável. Se o sinal acima e abaixo de ε for igual → par de raízes imaginárias. |
| **2. Vários coeficientes nulos** no polinômio | Aplique o critério normalmente (pode haver polos em jω). |
| **3. Linha inteira de zeros** | Monte a **equação auxiliar** com a linha **anterior**, **derive**, use os coeficientes da derivada no lugar dos zeros e continue. As raízes da equação auxiliar são raízes do sistema (simétricas em relação à origem, ex.: ±j3). |

Exemplo caso 3: `s⁴+2s³+11s²+18s+18`: linha s² = [1 9] → auxiliar `s²+9=0`, derivada `2s = 0` → linha s¹ = [2] → 1ª coluna positiva; raízes `±j3` (marginal).

**Uso no lugar das raízes:** com o ganho K no polinômio, Routh dá o **K de limiar de estabilidade** (linha s¹ ou s⁰ zerando) e a **equação auxiliar** dá o cruzamento com o eixo jω.

<a id="s9"></a>
## 9. Lugar das raízes: conceito (Aula 7)

- Sistema `K·G(s)` com realimentação `H`: `T = K·G/(1 + K·G·H)`. **Os polos de T dependem de K.**
- **Lugar geométrico das raízes** = conjunto dos **polos de malha fechada quando K varia de 0 a +∞**. **Usamos polos e zeros de MALHA ABERTA para achar os de malha fechada.**
- Exemplo (câmera): `T = K/(s²+10s+K)`, ωn² = K: K=0 polos em 0 e −10; K=25 polo duplo −5 (criticamente amortecido); K>25 complexos −5 ± j√(K−25) (sempre estável).
- **Equação característica:** `1 + K·G(s)·H(s) = 0` ⇒ `K·G·H = −1`. Um ponto s₀ é polo de malha fechada se:
  - **Condição de fase:** `∠K·G(s₀)H(s₀) = (2n+1)·180°`;
  - **Condição de ganho:** `|K·G(s₀)H(s₀)| = 1` ⇒ **`K = 1/|G(s₀)H(s₀)|`**.
- **Vetores:** `(s + a)` é o vetor do zero/polo (em −a) até s. **Módulo** = distância; **fase** = ângulo medido no sentido **anti-horário** a partir do eixo real.
  - `M = (Π distâncias dos zeros a s₀)/(Π distâncias dos polos a s₀)`
  - `φ = Σ ângulos dos zeros − Σ ângulos dos polos`.

**Testar se s₀ é polo (Exemplos 1 e 2 dos slides):** `KG(s)H(s) = K(s+3)(s+4)/((s+1)(s+2))`.
1. Marque polos (−1, −2), zeros (−3, −4) e s₀.
2. Calcule os ângulos (zeros com +, polos com −). Ex.: s₀ = −2 + j3: φ = 56,31 + 71,57 − 90 − 108,43 = −70,55° ≠ (2n+1)180° → **não é polo**. s₀ = −2 + j√2/2 dá −180° → **é polo**.
3. Se passar na fase, `K = (d_polos)/(d_zeros)` (ex.: `K = 0,33`).

<a id="s10"></a>
## 10. Lugar das raízes: passos (Aulas 8 e 9)

Exemplo dos slides: `G·H = K(s+2)/(s(s+1)(s+3)(s+4))`, realimentação negativa, K ≥ 0.

| Passo | O que fazer | No exemplo |
|---|---|---|
| **1** | Marcar **polos (x) e zeros (o)** de `G·H` no plano s. | polos 0, −1, −3, −4; zero −2 |
| **2** | **Eixo real:** o lugar existe à **esquerda de um número ÍMPAR** de polos+zeros finitos (0 é par). | [−1, 0] e [−3, −2]; e (−∞, −4] fica à esquerda de 5 → ímpar; [−4,−3] par não |
| **3** | **Início e fim:** os ramos partem dos polos (K=0) e terminam nos zeros (K→∞). Nº de ramos = nº de polos n. m ramos vão a zeros finitos e **(n−m) vão ao infinito** por assíntotas. | n=4, m=1: 1 ramo termina em −2; 3 vão ao infinito |
| **4** | **Assíntotas:** cruzam o eixo real em `σa = (Σpolos − Σzeros)/(n−m)`; ângulos `θa = (2k+1)·180°/(n−m)`, k = 0,1,2… (para quando repetir). | σa = (−8+2)/3 = −2; ângulos 60°, 180°, 300° |
| **5** | **Ponto de saída/entrada no eixo real:** entre dois polos adjacentes há saída; entre dois zeros adjacentes há entrada. Resolver `A'(s)B(s) − A(s)B'(s) = 0` (com `1 + K·B/A = 0`); aceitar só as raízes que caem **no lugar do eixo real**. K no ponto: `K = 1/|G(s)H(s)|` (produto das distâncias aos polos / zeros). | `3s⁴+24s³+67s²+76s+24=0` → aceitar só s = −0,4976 (K = 1,4584) |
| **6** | **Cruzamento com o eixo jω** por **Routh**: monte a tabela com K no polinômio e ache o K que zera a linha s¹ (ou s⁰); use a **equação auxiliar** (linha s²) para achar `s = ±jω`. | K = 41, `99s² + 656 = 0` → s = ±j2,574. Também K=0 em s=0 |
| **7** | **Complexos:** ângulo de **partida** de um polo complexo `θp = 180° + Σφ(GH)` e de **chegada** a um zero complexo `θz = 180° − Σφ(GH)`, **ignorando a contribuição do próprio polo/zero**; zeros com +, polos com −. | polos −1 ± j, zero −2: em p1, φz = 45°, φp2 = 90° → θp1 = 180+45−90 = 135°; em p2 = 225° |
| Simetria | O lugar é **simétrico em relação ao eixo real.** | |

**No MATLAB:** `G=tf(...); H=tf(...); A=G*H; rlocus(A); axis([xmin xmax ymin ymax])`.

**Feedback positivo (Aula 9)** 🧩: a equação característica vira `1 − K·G·H = 0`. Complementar ao negativo (o lugar do positivo é o do negativo com as regras trocadas): eixo real com número **par** (0 é par) à direita; assíntotas `θ = 2k·180°/(n−m)`; condição de fase `2k·180°`. No MATLAB use **`A = -G*H`** (**não esqueça o sinal menos**). Nos gráficos, curva contínua = negativo; tracejada = positivo. Verifique estas regras com suas anotações, pois as fórmulas estão em imagem no `.pptx`.

<a id="s11"></a>
## 11. Fórmulas para a prova

```
Malha fechada:        T = G/(1+GH)        Erro (unitária):  E = X/(1+G)
1ª ordem:             y = 1 − e^(−t/T)    63,2 % em t=T      ts(2%) = 4T
2ª ordem:             ωn²/(s²+2ζωn s+ωn²)   ωd = ωn√(1−ζ²)   polos −ζωn ± jωd
                      Mp = exp(−πζ/√(1−ζ²))   tp = π/ωd   ts(2%) = 4/(ζωn)
                      tr(0-100%) = (π−β)/ωd,  β = atan(√(1−ζ²)/ζ)
Erros:                Kp=lim G; Kv=lim sG; Ka=lim s²G
Routh:                b1=(a1a2−a0a3)/a1 ; mudanças de sinal = polos no SPD
Root locus:           σa=(Σp−Σz)/(n−m); θa=(2k+1)180/(n−m); K=1/|GH|
                      partida 180+Σφ ; chegada 180−Σφ
```
