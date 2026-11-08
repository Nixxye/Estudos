# Exercícios e exemplos dos slides da P2, resolvidos

A última prova teve questões **iguais às da lista e dos slides**, então aqui estão **todos os exercícios e exemplos numéricos dos slides da P2** (Aulas 10, 12, 13, 14 e 15), com enunciado, onde está, resolução e conferência. Os da lista (Relatório 04) estão em [Gabarito_Relatorio04.md](Gabarito_Relatorio04.md). Teoria: [Resumo_Controle_P2.md](Resumo_Controle_P2.md). Passos: [Tutorial_Controle_P2.md](Tutorial_Controle_P2.md).

## Resultado da busca nos slides

| Slide | Tem exercício? | O que é | Onde está aqui |
|---|---|---|---|
| **Aula 10, p.3** | **Sim, explícito** ("Exercício") | mapa de polos e zeros + resposta ao degrau de T₁, T₂, T₃ | [§1](#e1) |
| Aula 10, p.4 a 7 | exemplo resolvido | polos dominantes, resíduos, resposta ao degrau `40/((s+20)(s+2)(s+1))` | [§1](#e1), [§2](#e2) |
| Aula 10, p.13 e 14 | exemplo (motivação) | `G = K/((s+1)(s+2)(s+3))` com K = 18 | [§3](#e3) |
| Aula 10, p.19 a 22 | exemplo resolvido | compensador **LAG** em `K(s+8)/((s+3)(s+2)(s+1))` | [§4](#e4) |
| Aula 10, p.24 a 27 | exemplo resolvido | compensador **LEAD** em `K/((s+3)(s+2))` | [§5](#e5) |
| Aula 12, p.3 a 11 | exemplos (só gráficos) | efeito de P, PI, PD | [§6](#e7) |
| **Aula 13** | exemplo resolvido completo | projeto de **PD** em `2/s²` | [§7](#e8) |
| **Aula 14** | exemplo resolvido completo | projeto de **PI** em `1/(s+12)` | [§8](#e9) |
| **Aula 15** | exemplos resolvidos | sintonia de **PID** por tabelas: ZN (curva de reação e ganho limite), CHR, Tyreus-Luyben | [§9](#e10) |

Só um é chamado de "Exercício" no slide (Aula 10, p.3); os outros são "Exemplo", e é onde costuma estar o que cai na prova (principalmente os projetos PD e PI das Aulas 13 e 14 e o LAG/LEAD da Aula 10).

---

<a id="e1"></a>
## 1. Aula 10 (p.3): "Exercício": mapa de polos e zeros e resposta ao degrau de T₁, T₂, T₃

**Enunciado:** faça o mapa de polos e zeros e a resposta ao degrau dos 3 sistemas:

- `T₁(s) = 40/((s+20)(s+1+j)(s+1−j))`
- `T₂(s) = 3/((s+1,5)(s+1+j)(s+1−j))`
- `T₃(s) = 2/((s+1+j)(s+1−j))`

**Resolução:**

1. **Mapa de polos e zeros.** Nenhum tem zeros. Polos:
   - `T₃`: −1 ± j.
   - `T₁`: −1 ± j e **−20**.
   - `T₂`: −1 ± j e **−1,5**.

![Exercício da Aula 10](img/aula10_exercicio.png)

2. **Ganho DC** (`T(0)`): `T₁ = 40/(20·2) = 1`, `T₂ = 3/(1,5·2) = 1`, `T₃ = 2/2 = 1`. Todos terminam em **1** (a mesma altura final).

3. **Frações parciais e resíduos** (valores do slide, conferidos com `residue`):

| | Resíduo do polo real | Resíduo dos complexos (módulo) |
|---|---|---|
| `T₁` | **0,1105** (polo −20) | 1,0512 |
| `T₂` | **2,4** (polo −1,5) | 1,3416 |

   - `T₁ = 0,1105/(s+20) − (0,0552 − j1,0497)/(s+1+j) − (0,0552 + j1,0497)/(s+1−j)`
   - `T₂ = 2,4/(s+1,5) − (1,2 + j0,6)/(s+1+j) − (1,2 − j0,6)/(s+1−j)`

4. **Dominância:**
   - `T₁`: relação das partes reais `20/1 = 20 > 5` e resíduo do polo real **0,11 ≪ 1,05**. O polo −20 **não domina**: `T₁` se comporta como **`T₃`** (2ª ordem com ωn = √2, ζ = 0,707).
   - `T₂`: relação `1,5/1 = 1,5` (< 5) e resíduo do polo real **2,4 > 1,34**. O polo real **domina ou compete**, então **`T₂` não é 2ª ordem**: a resposta fica mais lenta e **sem overshoot** relevante (a figura mostra).

5. **Resposta ao degrau** (conferida numericamente):

| Sistema | Overshoot | Tempo de acomodação (2 %) | Observação |
|---|---|---|---|
| `T₃` | 4,3 % (ζ = 0,707) | ≈ 4,2 s | 2ª ordem padrão |
| `T₁` | 4,3 % | ≈ 4,3 s | **quase idêntico a T₃** |
| `T₂` | 1,7 % | ≈ 3,3 s | polo −1,5 domina; não é 2ª ordem |

**Frase da conclusão (slide p.4):** "A F.T. de terceira ordem `T₁(s)` se comporta como a de segunda `T₃(s)` devido aos polos dominantes."

---

<a id="e2"></a>
## 2. Aula 10 (p.6 e 7): resposta ao degrau de `G = 40/((s+20)(s+2)(s+1))`

**Dado:** `G(s) = 40/(s³ + 23s² + 62s + 40)`.

**Resolução (frações parciais, `residue`):**

`G(s) = 0,117/(s+20) − 2,222/(s+2) + 2,105/(s+1)`

Transformada inversa: `L⁻¹{1/(s+a)} = e^(−at)`, e, para o degrau, `L⁻¹{1/(s(s+a))} = (1 − e^(−at))/a`. Então:

`g(t) = 0,117e^(−20t) − 2,222e^(−2t) + 2,105e^(−t)`

`y(t) = 0,117/20·(1 − e^(−20t)) − 2,222/2·(1 − e^(−2t)) + 2,105/1·(1 − e^(−t))`

**`y(t) = 0,006(1 − e^(−20t)) − 1,111(1 − e^(−2t)) + 2,105(1 − e^(−t))`**

Conferência: valor final `0,006 − 1,111 + 2,105 = 1,000` ✓ (= `G(0) = 40/40`).

**Leitura:** o termo do polo −20 vale só **0,006** (desprezível); a resposta é comandada pelos polos −1 e −2.

---

<a id="e3"></a>
## 3. Aula 10 (p.13 e 14): `G = K/((s+1)(s+2)(s+3))` com K = 18

**Dado:** malha fechada para K = 18: `T = 18/((s+4,75)(s+0,63−j2,16)(s+0,63+j2,16))`.

**Verificação:** polinômio característico `(s+1)(s+2)(s+3) + 18 = s³ + 6s² + 11s + 24`, com raízes **−4,75** e **−0,63 ± j2,16** ✓.

**Leituras do slide:**

- Valor final `18/(6 + 18) = 0,75` (**erro 25 %** ao degrau).
- Pólos complexos com `ζ = 0,28` e overshoot ≈ 40 % (informação do cursor do MATLAB na p.14).
- Objetivos que não saem só com K: **reduzir o tempo de subida mantendo o overshoot** (polos mais afastados na mesma reta de ζ) e **diminuir o erro**.
- **"Pode não ser possível obter os resultados desejados apenas variando o ganho"**: é a motivação dos compensadores (LAG e LEAD).

---

<a id="e4"></a>
## 4. Aula 10 (p.17 a 22): compensador LAG

**Dado:** `G(s) = K(s+8)/((s+3)(s+2)(s+1))`. Compensador `Gc = Kc (s+1/T)/(s+1/(αT))` com `T = α = 10`:

`Gc(s) = Kc (s + 1/10)/(s + 1/100)`

**Resolução:**

1. **`G(0)`:** `G(0) = 8K/6 = 4K/3`.
2. **Ganho DC do compensador:** `Gc(0) = Kc·(0,1/0,01) = 10·Kc` (= `Kc·α`).
3. **Erro ao degrau (teorema do valor final):** `e(∞) = 1/(1 + Gc(0)G(0))`.
4. **Ganho limite** (sem compensador): polinômio `s³ + 6s² + (11+K)s + (6+8K)`; Routh: `6(11+K) = 6 + 8K` → **K = 30**.

**Resultados (conferidos):**

| Caso | Cálculo | e(∞) | Observação |
|---|---|---|---|
| Sem LAG, K = 1 | `1/(1 + 4/3) = 3/7` | **0,428** | |
| Sem LAG, K = 28 | `1/(1 + 4·28/3) = 3/115` | **0,026** | K quase no limite (30): resposta muito oscilatória (polo em −0,02 ± j6,26 no gráfico) |
| Com LAG, Kc = 1, K = 1 | `1/(1 + 10·4/3) = 3/43` | **0,07** | |
| Com LAG, **Kc = 5**, K = 1 | `1/(1 + 50·4/3) = 3/203` | **0,015** | erro menor que o de K = 28, **sem** chegar perto do limite |

**Conclusão (slide p.22):** o lugar das raízes com o LAG é **praticamente o mesmo** do original (polo e zero perto da origem se cancelam), mas o **ganho DC aumenta 10 vezes** e o erro cai, **ao custo de uma resposta mais lenta**.

---

<a id="e5"></a>
## 5. Aula 10 (p.23 a 27): compensador LEAD

**Dado:** `G(s) = K/((s+3)(s+2))`. **Objetivo:** criar polos dominantes em `s = −4 ± j4`. **Problema:** o lugar das raízes de `K/((s+2)(s+3))` é uma reta vertical em −2,5, então **só aumentar K não leva a −4 ± j4**.

**Resolução (o professor arbitra o zero, calcula o polo):**

1. Ângulos até `s₀ = −4 + j4` (anti-horário):
   - polo −2: `180° − tan⁻¹(4/2) = 116,57°`
   - polo −3: `180° − tan⁻¹(4/1) = 104,04°`
2. **1ª tentativa, zero em −4:** ângulo do zero `90°`. `θp = 90° − 104,04° − 116,57° + 180° = 49,39°` → `p = 4 + 4/tan(49,39°) = 4 + 4/1,17 = 7,42`. O polo em −7,42 está **perto dos polos da planta** (pode dominar). Tenta outro zero.
3. **2ª tentativa, zero em −5:** ângulo do zero `tan⁻¹(4/1) = 75,96°`. `θp = 75,96° − 104,04° − 116,57° + 180° = 35,35°`; `tan(35,35°) = 0,71` → **`p = 4 + 4/0,71 = 9,63`**.
4. **Parâmetros do compensador:** `Gc = Kc (s+5)/(s+9,63)`:
   - `1/T = 5` → `T = 0,2`;
   - `1/(αT) = 9,63` → `α = 1/(0,2·9,63) = 0,52` (**0 < α < 1**: LEAD ✔).
5. **Ganho (módulo em `s₀`):**
   `Kc·K = |s₀+2|·|s₀+3|·|s₀+9,63| / |s₀+5| = 4,472 · 4,123 · 6,906 / 4,123 = 30,9`.
6. **Malha aberta:** `Gc·G = Kc·K (s+5)/((s+9,63)(s+3)(s+2))`. O lugar das raízes passa por `−4 ± j4` quando **`Kc·K = 30,9`**.

**Por que o zero em −5 e não em −4?** O polo do compensador precisa ficar **bem à esquerda** dos polos da planta (−2, −3) para **não ser dominante**: −7,42 era perto demais; −9,63 é melhor.

---

<a id="e7"></a>
## 6. Aula 12 (p.3 a 11): efeito de P, PI, PD (exemplos dos slides, recalculados)

Os slides mostram só os **gráficos**; abaixo estão os números (conferidos por simulação) e os gráficos refeitos.

![Exemplos da Aula 12](img/aula12_exemplos.png)

### 7.1 P: `G = 1/((s+1)(s+2)(s+3))`, `C = Kp`

| Kp | Valor final `Kp/(6+Kp)` | Erro estacionário | Overshoot | Polos dominantes |
|---|---|---|---|---|
| 1 (sem compensação) | 0,143 | 0,857 | ≈ 0 % | −1,34 ± j0,56 |
| 2 | 0,25 | 0,75 | 1 % | −1,24 ± j0,86 |
| 5 | 0,455 | 0,545 | 7 % | −1,05 ± j1,31 |
| 20 | 0,769 | 0,231 | **39 %** | −0,58 ± j2,24 |

**Efeitos confirmados:** o tempo de subida cai; o overshoot cresce; o erro diminui (mas **não zera**); a ordem não muda.

### 7.2 PI: mesma planta, `C = Kp + Ki/s`

| Kp | Ki | Overshoot | ts (2 %) | Erro |
|---|---|---|---|---|
| 3 | 2 | 0 % (lento) | ≈ 11 s | **0** |
| 1 | 2 | 2,6 % | ≈ 10 s | **0** |
| 1 | 4 | **26,6 %** | ≈ 15 s | **0** |

**Efeitos confirmados:** o erro vai a **zero** (polo em 0), mas aumentar **Ki** aumenta o overshoot e o ts (Kp = 1: Ki 2 → 4); sistema de 4ª ordem.

### 7.3 PD: `G = 1/(s² + 0,5s)`, `C = Kp + Kd s`

| Kp | Kd | Overshoot | ts (2 %) |
|---|---|---|---|
| 1 | 0 (sem compensação) | **44 %** | ≈ 14 s |
| 1 | 0,5 | 19 % | ≈ 7,7 s |
| 1 | 1 | **7,9 %** | ≈ 5,1 s |

**Efeito confirmado:** aumentar **Kd diminui overshoot e ts**.

---

<a id="e8"></a>
## 7. Aula 13: projeto do PD (exemplo completo)

**Enunciado:** `G = 2/s²`, Mp máx. 20 %, ts (2 %) máx. 4 s, controlador PD.

**Resolução (passos da Aula 13):**

1. **Polos dominantes.** `ζmin`: `0,2 = e^(−πζ/√(1−ζ²))` → `ζmin = 0,46`. `ts = 4/(ζωn) = 4` → `(ζωn)min = 1` → `ωn = 1/0,46 = 2,174`; `ωd = 2,174·√(1 − 0,46²) = 1,93`. **Polos: −1 ± j1,93.**
2. **P basta?** Fase em `s₀ = −1 + j1,93`: dois polos em 0 dão `2 × 117,4° = 234,8°`, então a fase de `K·G(s₀)` é `−234,8° ≠ −180°` (sobram 54,8°). `s₀` **não pertence** ao lugar de `K·2/s²` (o eixo imaginário). **Não**: PD necessário.
3. **Condição de fase:** `C·G = 2Kd(s+z)/s²`. Ângulo de cada polo em 0 até `−1 + j1,93`: `180° − tan⁻¹(1,93/1) = 117,4°`. A soma é `2 × 117,4° = 234,8°`.
   `θz − 234,8° = −180°` → `θz = 54,8°`.
   `tan(54,8°) = 1,93/(z − 1) = 1,418` → `z − 1 = 1,36` → **`z = 2,36`**.
4. **Condição de módulo:** `2Kd·|s₀+2,36| / |s₀|² = 1`:
   `|s₀+2,36| = √(1,36² + 1,93²) = 2,36`; `|s₀|² = 1 + 3,72 = 4,72` → `Kd = 4,72/(2·2,36) = 1`. Logo **`Kd = 1`**, **`Kp = z·Kd = 2,36`**, `C = 2,36 + s`.
5. **Simulação:** **Mp = 32 %**, ts = 3,5 s (✔ conferido: 32,2 % e 3,50 s): **não atende o overshoot**.
6. **Ajuste fino:** mantém `z = 2,36` e sobe o ganho: **`Kd = 2,58`**, **`Kp = 6,08`**, `C = 2,58(s + 2,36) = 2,58s + 6,08`. Resultado: **Mp < 20 %**, **ts < 4 s** ✔ (conferido: 19,7 % e 1,4 s).
7. **Erro estacionário (degrau):** `e(∞) = lim s·(1/s)·1/(1 + CG) = lim s²/(s² + 5,16s + 12,18) = 0`. A planta já tem dois integradores (tipo 2).
8. **Malha fechada:** `T = 5,16(s+2,36)/(s² + 5,16s + 12,18) = 5,15(s+2,36)/((s+2,58−j2,35)(s+2,58+j2,35))`.

![PD e PI dos slides](img/aula13_14_exemplos.png)

**Implementação com amplificadores operacionais:**

- `C(s) = 2,58(s + 2,36) = 6,089(0,424s + 1)` (forma `Kp(1 + Td s)` com `Kp = 6,089` e `Td = 0,424 s`).
- Integrador inversor: `Vo/Vin = −1/(RCs)`. Dois integradores inversores em cascata dão `G = 2/s²` (com `R₁C₁ = 1` e `R₂C₂ = 0,5`).
- Somador/subtrator com resistores iguais: `Vo = Vin1 − Vin2` (forma o erro `X − Y`).

---

<a id="e9"></a>
## 8. Aula 14: projeto do PI (exemplo completo)

**Enunciado:** `G = 1/(s+12)`, Mp máx. 10 %, **erro zero** ao degrau, ts (2 %) máx. 0,5 s, controlador PI.

**Resolução (passos da Aula 14):**

1. **Polos dominantes.** `ζmin`: `0,1 = e^(−πζ/√(1−ζ²))` → `ζmin = 0,59`. `ts = 4/(ζωn) = 0,5` → `(ζωn)min = 8` → `ωn = 8/0,59 = 13,56`; `ωd = 13,56·√(1−0,59²) = 10,9`. **Polos: −8 ± j10,9.**
2. **P basta?** Fase em `s₀ = −8 + j10,9`: o polo em −12 dá `tan⁻¹(10,9/4) = 69,8°`, então a fase de `K·G(s₀)` é `−69,8° ≠ −180°` (faltam 110,2°). `s₀` **não pertence** ao lugar (só o eixo real), e com P o erro seria `1/(1 + Kp/12) ≠ 0`. **Não**: PI necessário.
3. **Condição de fase.** `C·G = Kp(s+z)/(s(s+12))`. Ângulos até `−8 + j10,9`:
   - polo em 0: `180° − tan⁻¹(10,9/8) = 126,3°`
   - polo em −12: `tan⁻¹(10,9/4) = 69,8°`
   `θz − 126,3° − 69,8° = −180°` → `θz = 16,1°`
   `tan(16,1°) = 10,9/(z − 8) = 0,289` → **`z = 8 + 10,9/0,289 = 45,7`**.
4. **Condição de módulo:** `Kp·|s₀+45,7| / (|s₀|·|s₀+12|) = 1`:
   `|s₀| = 13,5`; `|s₀+12| = |4 + j10,9| = 11,6`; `|s₀+45,7| = |37,7 + j10,9| = 39,2`.
   **`Kp = 13,5·11,6/39,2 = 4`**, **`Ki = z·Kp = 182,6`**. `C = 4 + 182,6/s`.
5. **Simulação:** **Mp ≈ 10,5 % (> 10 %)**, ts < 0,5 s: precisa de **ajuste fino**.
6. **Ajuste fino:** reduz o ganho: `Kp = 0,8·4 = 3,2` e **`Ki = z·Kp = 45,7 × 3,2 = 146,2`**. `C = 3,2 + 146,2/s`. Resultado: **Mp < 10 %**, **ts < 0,5 s** ✔ (conferido: 8,2 % e 0,47 s).
7. **Malha fechada (projeto original):** `T = 4(s + 45,7)/((s+8−j10,9)(s+8+j10,9))`; **(final)** `T = 3,2(s+45,7)/((s+7,6−j9,4)(s+7,6+j9,4))`.

**Erro:** o PI tem um polo em 0, então a malha é tipo 1: erro ao degrau **zero** ✔.

---

<a id="e10"></a>
## 9. Aula 15: sintonia de PID (ZN, Cohen-Coon, CHR, Tyreus-Luyben)

Resolução completa, com as tabelas, as contas e os gráficos, em [Resolucao_Exercicios/11_Aula15_Sintonia_PID.md](Resolucao_Exercicios/11_Aula15_Sintonia_PID.md). Resultados dos exemplos dos slides:

| Exemplo | Planta | Controlador resultante | Simulação |
|---|---|---|---|
| ZN curva de reação, PID (slides 7 e 8) | `2/(s²+3s+2)`, `K = 1`, `L = 0,2`, `T = 2` | `Kp = 12`, `Ki = 30`, `Kd = 1,2` | Mp ≈ 43 % |
| ZN curva de reação, PI (slides 9 e 10) | mesma | `Kp = 9`, `Ki = 13,5` | Mp ≈ 58 % |
| ZN curva de reação, P (slides 11 e 12) | mesma | `Kp = 10` | Mp ≈ 35 %, erro 9 % |
| CHR 20 %, PID (slides 16 e 17) | mesma | `Kp = 9,5`, `Ki = 3,4`, `Kd = 0,89` | Mp ≈ 12 % |
| ZN ganho limite, PID (slides 19 a 24) | `1/(s(s+1)(s+5))` | `Kcr = 30`, `Tcr = 2,8 s`; `Kp = 18`, `Ki = 12,8`, `Kd = 6,3` | Mp ≈ 62 % |
| Tyreus-Luyben, PID (slides 25 e 26) | mesma | `Kp = 13,6`, `Ki = 2,2`, `Kd = 6` | Mp ≈ 28 % |

---

## Como estudar esta lista

1. Refaça cada resolução **sem olhar**, usando os passos do [tutorial](Tutorial_Controle_P2.md).
2. Confira os números principais: **z = 2,36; Kd = 1; Kd = 2,58 (PD)** e **z = 45,7; Kp = 4; Kp = 3,2; Ki = 146,2 (PI)**.
3. No LAG, saiba calcular `e(∞)` pelos 4 casos; no LEAD, saiba **por que o zero em −5** e **p = 9,63, α = 0,52, Kc·K = 30,9**.
4. Nos métodos de sintonia (Aula 15), saiba as tabelas do **ZN** (ganho limite e curva de reação) e fazer o **Routh para `Kcr` e `Tcr`** à mão.
