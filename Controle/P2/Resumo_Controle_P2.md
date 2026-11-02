# Resumo P2: Sistemas de Controle A (ELN77A)

Prof. Ronaldo Guisso (UTFPR). Cobre `Slides/` da P2: **Aulas 10 a 14** e o `Relatório 04`. Os exercícios e exemplos dos slides estão resolvidos em [Exercicios_dos_Slides_P2.md](Exercicios_dos_Slides_P2.md); o passo a passo para resolver questões está em [Tutorial_Controle_P2.md](Tutorial_Controle_P2.md); o gabarito do Relatório 04 está em [Gabarito_Relatorio04.md](Gabarito_Relatorio04.md).

> Marcas: **(Aula N, p.X)** = slide da Aula N, página X do PDF. **🧩** = conteúdo que a prova provavelmente cobra mas **não está** nos slides da pasta (conferir com o caderno).
> Limitação: li o texto dos slides e conferi algumas páginas em imagem. Os gráficos dos slides (respostas ao degrau, root locus) eu **recalculei** e conferi os números com os dos slides.

A P1 (função de transferência, 1ª e 2ª ordem, erro, Routh, lugar das raízes) é pré-requisito: [Resumo_Controle_P1.md](../P1/Resumo_Controle_P1.md).

## Índice

1. [Polos dominantes e resíduos (Aula 10)](#s1)
2. [Efeito de adicionar polos e zeros (Aula 10)](#s2)
3. [Compensação: série e por realimentação, diretrizes (Aula 10)](#s3)
4. [Compensador por atraso de fase, LAG (Aula 10)](#s4)
5. [Compensador por avanço de fase, LEAD (Aula 10)](#s5)
6. [Diagrama de Bode (Aula 11)](#s6)
7. [Controladores P, PI, PD, PID: efeitos (Aula 12)](#s7)
8. [Projeto do controlador PD (Aula 13)](#s8)
9. [Projeto do controlador PI (Aula 14)](#s9)
10. [PID e Ziegler-Nichols 🧩 (Relatório 04)](#s10)
11. [Fórmulas para a prova](#s11)

---

<a id="s1"></a>
## 1. Polos dominantes e resíduos (Aula 10, p.2 a 7)

**Ideia:** em um sistema de ordem alta, **alguns polos comandam a resposta** (os dominantes) e os outros pouco importam. Isso permite aproximar um sistema de 3ª ordem por um de 2ª.

A resposta ao degrau de `T(s)` com polos simples é uma soma de exponenciais, uma por polo. Expandindo em frações parciais:

`T(s) = r₁/(s − p₁) + r₂/(s − p₂) + … + q(s)`

Cada `rᵢ` é o **resíduo** do polo `pᵢ`: ele mede **quanto aquele polo contribui** para a resposta. A dominância depende de **duas coisas**:

1. **A relação entre as partes reais dos polos.**
2. **O valor dos resíduos** (que dependem dos polos e dos zeros).

**Regras do slide:**

- Se a relação das partes reais for **maior que 5** e **não houver zeros próximos**, os polos **mais próximos do eixo jω** são dominantes no transiente.
- Os polos dominantes podem ser um **par complexo conjugado**.
- Um **polo e um zero muito próximos** se **cancelam**.
- Um polo **longe da origem** tem resíduo pequeno: sua contribuição no transiente é desprezível.
- Com polos dominantes e compensação, sistemas de ordem maior se comportam como de **1ª ou 2ª ordem**.

**Exemplo do slide (p.3 a 5), verificado numericamente:**

| Sistema | Polos | Resíduos (módulo) | Conclusão |
|---|---|---|---|
| `T₃ = 2/((s+1+j)(s+1−j))` | −1 ± j | 1 e 1 | 2ª ordem: ωn = √2, ζ = 0,707 |
| `T₁ = 40/((s+20)(s²+2s+2))` | −20 e −1 ± j | **0,11** (polo −20) e 1,05 (complexos) | o polo −20 é **desprezível**: T₁ ≈ T₃ (relação 20/1 = 20 > 5) |
| `T₂ = 3/((s+1,5)(s²+2s+2))` | −1,5 e −1 ± j | **2,4** (polo −1,5) e 1,34 | o polo −1,5 **não** é desprezível: relação só 1,5, e o resíduo é maior que o dos complexos |

**Exemplo de resposta ao degrau (p.6):** `G = 40/((s+20)(s+2)(s+1)) = 0,117/(s+20) − 2,222/(s+2) + 2,105/(s+1)`. Então

`y(t) = 0,006(1 − e^(−20t)) − 1,111(1 − e^(−2t)) + 2,105(1 − e^(−t))`

(o termo do polo −20 vale só 0,006: desprezível).

**Relembrando 2ª ordem (Aula 10, p.8 a 10; vem da P1):** ωn constante = círculo; ζ constante = reta radial; `Re = −ζωn` constante = ts constante; `ωd` constante = tp constante.

<a id="s2"></a>
## 2. Efeito de adicionar polos e zeros em malha aberta (Aula 10, p.11 e 12)

| Adição | O lugar das raízes | Estabilidade relativa | Tempo de acomodação |
|---|---|---|---|
| **Polo** | desloca para a **direita** | **diminui** | **aumenta** (mais lento) |
| **Zero** | desloca para a **esquerda** | **aumenta** | **diminui** (mais rápido) |

Exemplo do slide: `G = K/((s+1)(s+2)(s+3))` versus `G = K(s+2,5)/((s+1)(s+2)(s+3))` (com um zero): o zero "puxa" o lugar para a esquerda.

<a id="s3"></a>
## 3. Compensação: projetar pelo lugar das raízes (Aula 10, p.13 a 16)

**Motivação (p.13 e 14):** em `G = K/((s+1)(s+2)(s+3))`, com **K = 18**, a malha fechada tem polos −4,75 e **−0,63 ± j2,16** (ζ = 0,28, overshoot 40 %), e a resposta termina em 0,75 (erro 25 %).

- Queremos, por exemplo, **diminuir o tempo de subida mantendo o overshoot**, ou **diminuir o erro**.
- **Pode ser impossível só variando K** (o lugar não passa pelos polos desejados). Então adiciona-se um **compensador**.

**Estruturas (p.15):**

- **Série (cascata):** `X → Gc(s) → G(s) → Y` (compensador antes da planta).
- **Por realimentação (paralelo):** o compensador `Hc(s)` fica no ramo de realimentação.

**Diretrizes (p.16):**

1. O compensador é projetado **inserindo polos e zeros**.
2. O sistema deve ser **causal**: nº de polos ≥ nº de zeros.
3. Se o compensador tem um polo e um zero **afastados**, ele **altera** o lugar das raízes.
4. Se o polo e o zero ficam **muito próximos**, **quase não alteram** o lugar: (a) as contribuições angulares têm sinais opostos e se anulam; (b) os módulos são quase iguais e se cancelam.

<a id="s4"></a>
## 4. Compensador por atraso de fase, LAG (Aula 10, p.17 a 22)

```
Gc(s) = Kc · (s + 1/T) / (s + 1/(αT)),    α > 1
```
- **Polo mais próximo da origem que o zero** (o polo `−1/(αT)` está mais perto de 0 que o zero `−1/T`).
- Polo e zero ficam **perto da origem e perto um do outro**: **não alteram** muito o lugar das raízes.
- **Uso:** alterar o **ganho** do sistema (principalmente o **ganho DC**) sem mexer muito no lugar das raízes, para **diminuir o erro em regime permanente**. **Custo:** reduz a velocidade de resposta.

**Ganho DC e erro (p.18):**

- Ganho DC de malha aberta: `K = Gc(0)·G(0) = Kc·α·G(0)` (porque `Gc(0) = Kc·(1/T)/(1/(αT)) = Kc·α`).
- Erro ao degrau unitário: **`e(∞) = 1/(1 + Gc(0)·G(0)) = 1/(1 + Kc·α·G(0))`**.

**Exemplo do slide (p.19 a 22), verificado:** `G = K(s+8)/((s+3)(s+2)(s+1))`, `G(0) = 4K/3`, e `Gc = Kc (s+1/10)/(s+1/100)` (T = α = 10).

| Caso | Cálculo | Erro |
|---|---|---|
| Sem compensação, K = 1 | `1/(1 + 4/3)` | **0,428** |
| Sem compensação, K = 28 (perto do ganho limite K ≈ 30) | `1/(1 + 4·28/3)` | **0,026** |
| Com LAG, Kc = 1, K = 1 | `1/(1 + 10·4/3)` | **0,07** |
| Com LAG, Kc = 5, K = 1 | `1/(1 + 50·4/3)` | **0,015** |

Ou seja: sem LAG, para chegar a erro baixo seria preciso K ≈ 28, quase no limite de estabilidade. Com LAG, **K = 1 e Kc = 5** dão um erro ainda menor, sem perder estabilidade. (Ganho limite: `K ≈ 30` pelo Routh.)

<a id="s5"></a>
## 5. Compensador por avanço de fase, LEAD (Aula 10, p.23 a 27)

```
Gc(s) = Kc · (s + 1/T) / (s + 1/(αT)),    0 < α < 1
```
- **Zero mais próximo da origem que o polo**; ambos **longe da origem**.
- O polo é colocado **bem à esquerda** dos polos da planta, para **não ser dominante**.
- **Uso:** **alterar o lugar das raízes** e **criar polos de malha fechada que o lugar original não tem**.

**Exemplo do slide (p.24 a 27):** `G = K/((s+3)(s+2))`. Quer-se polos dominantes em **s = −4 ± j4**, o que não é possível só aumentando K (o lugar de `K/((s+2)(s+3))` é uma reta vertical em −2,5).

**Método (condição de fase):**

1. Ponto desejado `s₀ = −4 + j4`. Ângulos (anti-horário, zeros +, polos −):
   - polo −2: `180° − tan⁻¹(4/2) = 116,57°`
   - polo −3: `180° − tan⁻¹(4/1) = 104,04°`
2. **Arbitrar o zero do controlador.** 1ª tentativa: zero em −4. A fase exige um polo em **−7,42** (muito perto dos da planta, pode dominar). 2ª tentativa: **zero em −5**, ângulo do zero `75,96°`. A condição de fase `θz − 116,57° − 104,04° − θp = −180°` dá `θp = 35,35°`, e então o polo em
   `p = 4 + 4/tan(35,35°) = 9,63`.
3. **Parâmetros:** `z = 1/T = 5 → T = 0,2`; `p = 1/(αT) = 9,63 → α = 1/(0,2·9,63) = 0,52`.
4. **Ganho (condição de módulo):** `Kc·K = |s₀+2|·|s₀+3|·|s₀+9,63| / |s₀+5| = 30,9`. Haverá polo em `−4 ± j4` quando `KcK = 30,9`.
5. Função de malha aberta: `Gc·G = Kc·K (s+5)/((s+9,63)(s+3)(s+2))`.

<a id="s6"></a>
## 6. Diagrama de Bode (Aula 11)

**O que é:** dois gráficos da resposta em frequência `G(jω)`: **ganho (magnitude, em dB)** e **fase (graus)**, ambos em função de ω (escala logarítmica). Vem da transformada de Fourier (`s = jω`): a de Laplace é para `s = σ + jω`, e a de Fourier só olha o eixo imaginário.

**Forma de Bode** (cada fator escrito para ser 1 em ω → 0):

```
G(jω) = Kb · Π(1 + jω/zᵢ) / [ (jω)^R · Π(1 + jω/pq) ]      (zᵢ, pq ≠ 0)
Kb = K · Π zᵢ / Π pq            (ganho de Bode)
```
Se não há polos nem zeros na origem, `Kb = G(0)` (ganho estático, ou ganho DC). **O Bode é a soma dos gráficos de cada fator.**

**Componentes (Aula 11):**

| Fator | Magnitude (dB) | Inclinação | Fase |
|---|---|---|---|
| **Constante** `Kb` | `20·log|Kb|` (reta) | 0 | 0° se `Kb > 0`; −180° se `Kb < 0` |
| **Polo na origem** `1/(jω)^R` | `−20R·log ω` | **−20R dB/década** | **−90R°** |
| **Zero na origem** `(jω)^T` | `+20T·log ω` | **+20T dB/década** | **+90T°** |
| **Polo real** em `−p`: `1/(1 + jω/p)` | assíntotas: 0 dB para ω ≪ p; `−20·log(ω/p)` para ω ≫ p | **−20 dB/déc** a partir de ω = p (frequência de corte) | 0° até 0,2p; **−45° em p**; −90° a partir de 5p (erro máx. 11,3°) |
| **Zero real** em `−z`: `1 + jω/z` | 0 dB e depois `+20·log(ω/z)` | **+20 dB/déc** a partir de ω = z | 0° → **+45° em z** → +90° |
| **Zero no semiplano direito** (+z) | **mesma magnitude** do zero em −z | +20 dB/déc | **0° → −45° → −90°** (fase oposta) |
| **Polos complexos** `1/(s²/ωn² + 2ζs/ωn + 1)` | `−10·log[(1 − ω²/ωn²)² + 4ζ²ω²/ωn²]`; pico na **frequência de ressonância** | **−40 dB/déc** depois de ωn | `−tan⁻¹[ (2ζ·ω/ωn) / (1 − ω²/ωn²) ]` (0° → −90° em ωn → −180°) |

Se há **N polos (ou zeros) múltiplos**, multiplique o módulo (em dB) e a inclinação por N.

**Exemplo do slide, resolvido em [Exercicios_dos_Slides_P2.md](Exercicios_dos_Slides_P2.md):** `G = 40 s²(s+10)/(s³(s+20)(s²+2s+2))`, com `Kb = 40·10/(20·2) = 10 → 20 dB`, 3 polos e 2 zeros na origem, zero em −10, polo em −20 e um par complexo com `ωn = √2` e `ζ = 1/√2`.

**No MATLAB (slides):**
```matlab
[num,den] = zp2tf([0 0 -10]', [0 0 0 -20 -1-1i -1+1i], 40);   % zeros, polos, ganho (colunas)
G = tf(num,den);
bode(G); grid;
```
(O apóstrofo `'` transpõe o vetor.)

<a id="s7"></a>
## 7. Controladores P, PI, PD, PID: efeitos (Aula 12)

Estrutura: `X → (−) → E → C(s) → M → G(s) → Y`. O controlador `C(s)` age sobre o erro `E = X − Y`.

### P (proporcional), `C(s) = Kp`  (p.2 a 5)
- Saída: `m(t) = Kp·e(t)`.
- **Não altera o lugar das raízes** (só muda os ganhos limites).
- Aumentando Kp (degrau): tempo de subida **menor**; **aumenta o overshoot**; **não aumenta a ordem**; **diminui o erro estacionário**.
- Erro: `E(s)/X(s) = 1/(1 + Kp·G(s))`.
- Exemplo (p.3 e 5): `G = 1/((s+1)(s+2)(s+3))`, com Kp = 1 (sem compensação), 2, 5, 20: a resposta fica mais rápida, o valor final sobe, e o overshoot aumenta.

### PI (proporcional-integral), `C(s) = Kp + Ki/s = Kp (s + Ki/Kp)/s`  (p.6 a 9)
- Adiciona **um polo na origem** e **um zero em −Ki/Kp**.
- **Aumenta a ordem**; deixa a saída **mais oscilatória**; em alguns casos **mais lenta**.
- O polo na origem **atrai o lugar das raízes para perto do eixo jω**: **diminui a estabilidade relativa**.
- **Erro estacionário nulo para entrada degrau.**
- Aumentando Ki: **aumenta o overshoot** e **aumenta o ts**.

### PD (proporcional-derivativo), `C(s) = Kp + Kd·s = Kd (s + Kp/Kd)`  (p.10 e 11)
- Adiciona **um zero em −Kp/Kd**; age no erro **mais cedo** (antecipa).
- **Amplifica o ruído.**
- Aumentando Kd: **diminui o overshoot** e **diminui o ts**; **sem impacto significativo** no erro estacionário (só impede variações bruscas).
- Exemplo (p.11): `G = 1/(s² + 0,5s)`: Kp = 1 com Kd = 0 (sem compensação), 0,5 e 1: o overshoot cai (≈ 44 % → 19 % → 8 %).

### PID  (p.12 e 13)
`C(s) = Kp + Ki/s + Kd·s = Kd (s² + (Kp/Kd)s + Ki/Kd)/s`: **um polo na origem e dois zeros** (geralmente reais e iguais).

| Aumentando | Overshoot | Tempo de acomodação | Erro estacionário |
|---|---|---|---|
| **Kp** | aumenta | pouco impacto | diminui |
| **Ki** | aumenta | aumenta | **anula** |
| **Kd** | **diminui** | **diminui** | sem impacto |

### Quando usar (p.14)

| Controlador | Uso |
|---|---|
| **P** | melhora o regime estacionário mas piora o transitório; leva sistema instável à estabilidade variando o ganho; bastante limitado |
| **PD** | transitório ruim e regime estacionário bom; **raramente usado** porque amplifica ruído |
| **PI** | quando se deseja **erro zero** em regime estacionário |
| **PID** | melhora **transitório e regime estacionário** |

**PI e PID são os mais usados na indústria.**

<a id="s8"></a>
## 8. Projeto do controlador PD (Aula 13)

**Especificações (p.2):** usa-se o **modelo de 2ª ordem** como referência. A **região desejável** para os polos de malha fechada é a interseção de: (a) `ζ ≥ ζmin` (cone: reta a `cos⁻¹(ζmin)` do eixo real negativo) e (b) `ζωn ≥ (ζωn)min` (à esquerda de uma reta vertical).

- `Mp = e^(−πζ/√(1−ζ²))` → **ζmin**: `ζmin = −ln(Mp)/√(π² + ln²(Mp))`.
- `ts = 4/(ζωn)` (critério 2 %) → **(ζωn)min = 4/ts**; então `ωn = (ζωn)min/ζmin` e `ωd = ωn·√(1−ζ²)`.
- Polos dominantes desejados: **`s₀ = −(ζωn)min ± jωd`**.

**Limitação física (p.8):** um derivador puro não existe (o ganho tende a infinito em altas frequências). Na prática, adiciona-se **um polo** que limita o ganho: `C(s) = Kp + Kd·s → (Kp + Kd·s)/(1 + s/a)`, por exemplo `C(s) = (s+2)/(1+s/10)`.

**Passos do projeto (p.9), `C(s) = Kd (s + z)`, com `z = Kp/Kd` real:**

1. Traduzir as especificações em uma **localização dos polos dominantes** de malha fechada.
2. Verificar se o objetivo **não** pode ser atingido só com um controlador **proporcional**.
3. Se o PD é necessário, **localizar o zero** de modo que a **condição de ângulo** seja satisfeita.
4. Calcular o **ganho total** pela **condição de módulo**.
5. Calcular a **constante de erro estacionário**.
6. Se a constante não for adequada, tentar outro controlador.
7. **Simular**; se não for satisfatório, fazer **ajuste fino** (Kd e z).

**Exemplo do slide (p.10 a 17):** `G = 2/s²`, Mp ≤ 20 %, ts ≤ 4 s.

- ζmin = 0,46; (ζωn)min = 1; ωn = 1/0,46 = 2,174; ωd = 1,93 → **polos em −1 ± j1,93**.
- Fase: os dois polos em 0 dão `2 × 117,4° = 234,8°`; `θz = 234,8° − 180° = 54,8°`; `z = 1 + 1,93/tan(54,8°) = 2,36`.
- Módulo: `2Kd·|s₀+2,36|/|s₀|² = 1` → **Kd = 1**, `Kp = z·Kd = 2,36`. Então `C = 2,36 + s`.
- Simulação: **Mp = 32 %, ts = 3,5 s** (não atende o Mp) → **ajuste fino**: `Kd = 2,58`, `Kp = 2,36 × 2,58 = 6,08`, `C = 2,58s + 6,08`: **Mp < 20 %, ts < 4 s**. ✔ (verifiquei: Mp = 19,7 %, ts = 1,4 s.)
- Erro: `e(∞) = lim s·(1/s)·1/(1 + CG) = 0` (a planta já tem 2 integradores).

**Implementação com amplificadores operacionais (p.16 a 19):**

- `C(s) = 2,58(s + 2,36) = 6,089(0,424s + 1)` (forma "Kp(1 + Td s)").
- **Integrador inversor:** `Vo/Vin = −1/(RCs)`. Dois integradores em cascata (inversores) dão `G = 2/s²` (com `R₁C₁ = 1` e `R₂C₂ = 0,5`).
- **Somador/subtrator** com resistores iguais: `Vo = Vin1 − Vin2` (comparador do laço).

<a id="s9"></a>
## 9. Projeto do controlador PI (Aula 14)

**Uso:** **zerar o erro estacionário**, mas **piora o transiente**. `C(s) = Kp + Ki/s = Kp (s + z)/s`, com `z = Ki/Kp` real.

**Passos (p.2):**

1. Especificações → **polos dominantes**.
2. Verificar se **só P** não resolve.
3. Colocar o **polo na origem** e localizar o **zero** de modo que a **condição de ângulo** seja satisfeita.
4. Ganho total pela **condição de módulo**.
5. **Simular**; ajuste fino de Kp e z se necessário.

**Exemplo do slide (p.3 a 10):** `G = 1/(s+12)`, Mp ≤ 10 %, erro zero, ts ≤ 0,5 s.

- ζmin = 0,59; (ζωn)min = 4/0,5 = 8; ωn = 8/0,59 = 13,56; ωd = 10,9 → **polos em −8 ± j10,9**.
- Fase: ângulo do polo 0: `180° − tan⁻¹(10,9/8) = 126,3°`; do polo −12: `tan⁻¹(10,9/4) = 69,8°` (medido a partir do eixo, fase do polo em −12 vista do ponto); `θz = 126,3° + 69,8° − 180° = 16,1°` → `z = 8 + 10,9/tan(16,1°) = 45,7`.
- Módulo: `Kp·|s₀+45,7|/(|s₀|·|s₀+12|) = 1` → **Kp = 4**, `Ki = z·Kp = 182,6`. `C = 4 + 182,6/s`.
- Simulação: **Mp ≈ 10,5 % (> 10 %)**, ts < 0,5 s → **ajuste fino**: reduzir **Kp para 0,8·4 = 3,2**, mantendo z: **Ki = 45,7 × 3,2 = 146,2**. `C = 3,2 + 146,2/s`: **Mp < 10 %, ts < 0,5 s**. ✔ (verifiquei: Mp = 8,2 %, ts = 0,47 s.)
- Malha fechada: `T = 3,2(s + 45,7)/((s + 7,6 − j9,4)(s + 7,6 + j9,4))`.

**Truque do ajuste fino (dos dois exemplos):** mantém `z` e **reescala o ganho** (`Kd` sobe no PD, `Kp` desce no PI), porque o zero do controlador **aumenta o overshoot** em relação ao 2º grau puro previsto. (Não é universal: na Q2 do Relatório 04 o que resolve é aproximar o zero da origem; veja [Gabarito_Relatorio04.md](Gabarito_Relatorio04.md).)

<a id="s10"></a>
## 10. PID e Ziegler-Nichols 🧩 (Relatório 04, Q3)

Os slides da pasta **não trazem o método Ziegler-Nichols**; a Q3 do Relatório 04 o pede. Resumo do método de **malha fechada** (oscilação sustentada):

1. Com `Ki = Kd = 0` (só P), **aumente Kp** até a saída **oscilar de forma sustentada** (polos em ±jω). Esse ganho é o **ganho crítico `Ku`**, e o período da oscilação é **`Pu = 2π/ωu`**.
2. **Analiticamente:** o `Ku` é o ganho que zera a linha s¹ do **Routh** do polinômio característico, e `ωu` vem da **equação auxiliar** (linha s²). É igual ao **cruzamento com jω do lugar das raízes** (passo 6 da P1).
3. Tabela de sintonia ZN (malha fechada):

| Controlador | Kp | Ti | Td |
|---|---|---|---|
| P | 0,5·Ku | – | – |
| PI | 0,45·Ku | Pu/1,2 | – |
| **PID** | **0,6·Ku** | **Pu/2** | **Pu/8** |

4. Ganhos da forma dos slides `C(s) = Kp + Ki/s + Kd·s`: **`Ki = Kp/Ti`** e **`Kd = Kp·Td`**.
5. ZN dá uma resposta **agressiva** (overshoot grande, típico 40 a 60 %). Faça **ajuste fino** com a tabela de efeitos da [seção 7](#s7): reduzir Kp, aumentar Kd, reduzir Ki.

Resolvido em [Gabarito_Relatorio04.md](Gabarito_Relatorio04.md).

<a id="s11"></a>
## 11. Fórmulas para a prova

```
Especificações (2ª ordem):  ζmin = -ln(Mp)/sqrt(π² + ln²(Mp))      (Mp em fração; ex.: 15% → 0,517)
                            σ = ζωn = 4/ts (2%)    ωn = σ/ζ      ωd = ωn·sqrt(1-ζ²)
                            polos dominantes desejados:  s0 = -σ ± jωd
Condição de fase:           ∠C(s0)G(s0) = ±180°   (zeros +, polos -; ângulos anti-horários)
Condição de módulo:         |C(s0)G(s0)| = 1
PD:  C = Kd(s+z)           θz = (soma dos ângulos dos polos de G) - 180°
                           z = σ + ωd/tan(θz)      Kd = ∏|s0-pk| / (K_G·|s0+z|)      Kp = z·Kd
PI:  C = Kp(s+z)/s         mesma conta com o polo extra em 0 (some o ângulo do polo na origem)
                           Kp = ∏|s0-pk| / (K_G·|s0+z|)      Ki = z·Kp
PID: C = Kp + Ki/s + Kd·s  ZN: Kp=0,6Ku  Ti=Pu/2  Td=Pu/8   Ki=Kp/Ti   Kd=Kp·Td    Pu = 2π/ωu
LAG: Gc=Kc(s+1/T)/(s+1/(αT)), α>1     e(∞) = 1/(1 + Kc·α·G(0))
LEAD: mesma forma, 0<α<1             z = 1/T, p = 1/(αT); fase pelo ponto s0; Kc·K pelo módulo
Bode: |G|dB = 20log|Kb| ± 20R·log ω ± ...; polo real: -20 dB/déc em ω=p; zero real: +20 dB/déc em ω=z
      fase: ±45° em p/z, ±90° a partir de 5p/5z; polos complexos: -40 dB/déc depois de ωn
```
