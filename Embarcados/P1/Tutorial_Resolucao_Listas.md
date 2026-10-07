# Tutorial: como resolver as questões das listas (do jeito do professor)

Cobre `exercicios_asm.pdf` (17 questões), `exercicio_primos.pdf` e `Exercício de MEF.txt`.

Cada **tipo** de questão tem uma receita curta em passos. Os exemplos vêm dos gabaritos ([Gabarito_Exercicios.md](Gabarito_Exercicios.md)), a teoria está no [Resumo_P1.md](Resumo_P1.md), e **[Tabela p.N]** é a página do `QRC0001_UAL.pdf` (a Tabela da prova).

## Regras do professor que valem para tudo

1. **Use a Tabela.** É o material permitido na prova. Procure a instrução nela antes de inventar.
2. **Convenção de registradores do enunciado:** siga o que ele der (x = R1, y = R2...). Rascunho: **R12** (e R0-R3 livres, se não forem parâmetros).
3. **"Menor número de instruções"**: use shift dentro do Operand2, `MLA/MLS`, `BFI/BFC/UBFX`, `IT`, pós/pré-indexado.
4. **"Não utilize instruções de salto"** significa `IT` + sufixo de condição (sem `B`).
5. **Sinal:** com sinal usa `GE LT GT LE`; sem sinal usa `HS LO HI LS`.
6. **Funções: AAPCS "rigorosamente"**: argumentos R0-R3, retorno R0, preserva R4-R11, retorna com `BX LR`. Se a função chama outra (`BL`), salve LR.
7. **Planeje antes de codificar** (algoritmo, depois tabela variável → registrador, depois código) e **comente cada linha**.
8. Prova **sem calculadora**: treine hexadecimal à mão.

## Mapa: tipos de questão → receita

| Tipo | Questões | Receita |
|---|---|---|
| A. Endereços e memória (aritmética de endereço) | 1, 11 | [A](#a) |
| B. Equações aritméticas | 2 | [B](#b) |
| C. `if / else` traduzido para assembly | 3, 4 | [C](#c) |
| D. Flags e resultado de instruções | 5 | [D](#d) |
| E. Contas em hexadecimal (shifts, máscaras) | 6 | [E](#e) |
| F. Manipulação de bits em registrador | 7 | [F](#f) |
| G. Laços (contar bits, strings) | 8, 10, 3c | [G](#g) |
| H. Variáveis / vetores na memória | 9, 12 | [H](#h) |
| I. Pilha (PUSH/POP) | 13, 14 | [I](#i) |
| J. Sub-rotinas (AAPCS) | 15, 16, primos | [J](#j) |
| K. Pseudo-instruções e disassembly | 17 | [K](#k) |
| L. Diagrama de estados (MEF/FSM) | MEF | [L](#l) |

---

<a id="a"></a>
## A. Endereços de memória (Q1 e Q11)

**Q1: endereço do n-ésimo elemento de um vetor**

1. Descubra o **tamanho do elemento** (word = 4 bytes, half = 2, byte = 1).
2. Fórmula: `endereço = base + tamanho × (n − 1)` (a 1ª posição é n = 1; índice 0 é `base + 0`).
3. Faça a conta **em hexa**: multiplicar por 4 é deslocar 2 bits (0x18 = 24 = 4×6).
4. Exemplo: 7º word, base 0x00420A0: `0x420A0 + 4×6 = 0x420A0 + 0x18 = 0x420B8`.

**Q11: modos de endereçamento.** Para cada instrução `LDR R0, ...` responda duas coisas: **de qual endereço lê** e **quanto vale R1 depois**. Use a tabela do professor [Tabela p.4]:

| Forma | Endereço usado | R1 depois |
|---|---|---|
| `[R1, #off]` | R1 + off | inalterado |
| `[R1, #off]!` (pré-indexado) | R1 + off | R1 + off |
| `[R1], #off` (pós-indexado) | R1 | R1 + off |
| `[R1, R4, LSL #n]` | R1 + (R4 << n) | inalterado (com `!`, atualizado) |

Passos: (1) veja se tem `!` ou se o `#off` está **fora** do colchete (pós-indexado). (2) Calcule o offset (`R4 LSL #3` = 8×8 = 0x40). (3) Confira as **Notas** da Tabela p.4: no Thumb-2, pós-indexado por **registrador** e shift maior que `LSL #3` **não existem**.

---

<a id="b"></a>
## B. Equações aritméticas (Q2)

Passo a passo:

1. **Fatore** a expressão para reduzir multiplicações: `2x+2y+2z = 2(x+y+z)`, `16·y³z³ = 16·(yz)³`.
2. **Troque multiplicação por constante por shift no Operand2** (some/subtraia com shift embutido):
   - `×5 = ADD Rd, Rn, Rn, LSL #2`; `×9 = ... LSL #3`; `×2ⁿ = LSL`.
   - `×10 = ×5 e depois LSL #1`.
3. **"Constante − variável"** → `RSB Rd, Rn, #cte` (`RSB R12, R12, #3` = 3 − R12).
4. **Nunca destrua x, y, z se ainda precisar deles.** Guarde parciais em **R12** (rascunho). O resultado final vai em R0.
5. Multiplicação: `MUL Rd, Rm, Rs`. Multiplica e soma: `MLA Rd,Rm,Rs,Rn` (Rn + Rm·Rs). Multiplica e subtrai: `MLS` (Rn − Rm·Rs).
6. Conte as instruções e veja se algum passo pode virar um shift dentro de outra.

Exemplo `5(x+y)`: `ADD R0,R1,R2` / `ADD R0,R0,R0,LSL #2` (2 instruções).

---

<a id="c"></a>
## C. Traduzir `if / else` (Q3 e Q4)

### Passo a passo (receita do IT)

1. **Compare:** `CMP Rx, #valor` (ou `TST` para testar bits). Isso só gera flags.
2. **Escolha a condição do ramo "então"** ([Tabela p.6]). Com sinal: `EQ NE GE LT GT LE`. Sem sinal: `HS LO HI LS`.
3. **Escreva o `IT`** ([Tabela p.3]): uma letra por instrução do bloco: **T** para o "então" (condição `cond`) e **E** para o "senão" (condição **inversa**). A 1ª letra é sempre T.
   - `IT EQ`, `ITE LT`, `ITT NE`...
4. **Escreva cada instrução com o sufixo da sua letra** (`ADDLT` no T, `MOVGE` no E).
5. Limite: **4 instruções** por bloco, sem `if` aninhado. Passou disso? Use desvios (`BLE fim`, `B fim`).

Inversas: EQ↔NE, GE↔LT, GT↔LE, HS↔LO, HI↔LS, MI↔PL.

Exemplos:

```
; if (x >= 5) x = 0;            ; if (x < 9) x++; else x = 0;
CMP   R1, #5                    CMP    R1, #9
IT    GE                        ITE    LT
MOVGE R1, #0                    ADDLT  R1, R1, #1
                                MOVGE  R1, #0
```

### Condições compostas (Q4a: OU de igualdades)

Só há **um** conjunto de flags, então teste em sequência, deixando o `CMP` dentro do IT:

```
MOV   R2, #0            ; y = 0 (sem S, não mexe nas flags)
CMP   R1, #0x20
ITT   NE                ; só continua testando se ainda for diferente
CMPNE R1, #0x22
CMPNE R1, #0x15
IT    EQ                ; EQ = algum bateu
MOVEQ R2, #1
```

### Faixas (Q4b/Q4c): `lo ≤ x ≤ hi` com uma comparação sem sinal

1. Calcule `x − lo` e compare (sem sinal) com `hi − lo`. Se x < lo, `x − lo` vira um número enorme e falha sozinho.
2. Para **duas faixas** (OU): teste a 1ª; se **fora** (`HI`), teste a 2ª dentro de `ITT HI`; ao final `LS` = dentro de alguma.

```
MOV   R2, #0
SUB   R3, R1, #lo1     ; hi1 - lo1 abaixo
CMP   R3, #(hi1-lo1)
ITT   HI
SUBHI R3, R1, #lo2     ; sem S: as flags HI continuam válidas
CMPHI R3, #(hi2-lo2)
IT    LS
MOVLS R2, #1
```
Só muda as constantes entre Q4b e Q4c. **Faça as subtrações de hexa à mão** (0x29−0x10 = 0x19; 0x5C−0x31 = 0x2B).

### Quando há salto liberado (`while`, if aninhado)

Regra: `CMP` + desvio com a condição **inversa** para pular o corpo. Laço com contador: `SUBS R1,R1,#1` / `BNE loop` (o `S` do `SUBS` já gera a flag, sem precisar de `CMP`).

Q3c pede "sem salto" com um laço que tem valores iniciais constantes: calcule o resultado à mão (5 × 10! = 0x0114DB00) e só carregue os valores finais com `MOVW/MOVT`.

---

<a id="d"></a>
## D. Flags N, Z, C, V (Q5)

Cada instrução `LDR R0,=...`/`LDR R1,=...` só prepara os valores. **Só a última (`ADDS`/`SUBS`) atualiza as flags.**

Passo a passo:

1. Escreva os dois operandos em **binário** (o bit 31 é o que importa; o resto só se preocupa se houver vai-um).
2. Calcule o resultado (`SUBS a,b` = `a − b`, feito como `a + NOT(b) + 1`).
3. **N** = bit 31 do resultado. **Z** = resultado é 0.
4. **C:**
   - `ADDS`: **vai-um** do bit 31 (soma sem sinal estourou 32 bits).
   - `SUBS`/`CMP`: **C = 1 quando NÃO há empréstimo** (a ≥ b sem sinal); C = 0 quando há. É o contrário do que se espera.
5. **V (overflow com sinal):**
   - soma: dois positivos deram negativo, ou dois negativos deram positivo;
   - subtração `a − b`: sinais de `a` e `b` diferentes e o resultado tem o sinal de `b`.
6. Preencha a linha da tabela e faça a **conferência**: `0 − 0` dá Z = 1, C = 1 (sem empréstimo).

Truque de memória: dois números de mesmo sinal, soma com sinal trocado = **V=1**; vai-um final = **C=1**.

---

<a id="e"></a>
## E. Contas em hexadecimal (Q6)

1. Converta para binário só o pedaço que importa. **Cada dígito hexa = 4 bits.**
2. `<< n`: some n zeros à direita e corte o que passar de 32 bits. Deslocar 4 bits = 1 dígito hexa; 8 bits = 2 dígitos; 16 = 4 dígitos.
3. `>> n`: descarte n bits à direita e complete com zeros à esquerda (lógico, para números sem sinal).
4. `& máscara`: mantenha só onde a máscara for 1. `| máscara`: force 1 onde a máscara for 1. `~x`: inverta todos os bits (F ↔ 0, A ↔ 5...).
5. Para `<< 2` de um valor que não é múltiplo de 4 bits, converta pra binário, mova, e reagrupe em 4.
6. Sempre **escreva o resultado com 8 dígitos** (0x000000BA).

Exemplo: `(0xBADDCAFE & ~0xFF00) | 0x4200` → `~0xFF00 = 0xFFFF00FF` → `0xBADD00FE` → `| 0x4200` → `0xBADD42FE`.

---

<a id="f"></a>
## F. Manipulação de bits em R0 (Q7)

Ferramentas ([Tabela p.2 e p.3]). Bit 0 = LSb.

| Objetivo | Instrução | Como montar a máscara |
|---|---|---|
| Limpar bits | `BIC R0,R0,#máscara` ou `BFC R0,#lsb,#larg` | 1 nos bits a limpar |
| Setar bits | `ORR R0,R0,#máscara` | 1 nos bits a setar |
| Inverter bits | `EOR R0,R0,#máscara` | 1 nos bits a inverter |
| Extrair campo | `UBFX Rd,Rn,#lsb,#larg` | |
| Inserir campo | `BFI Rd,Rn,#lsb,#larg` | copia os bits baixos de Rn |
| Espelhar bytes | `REV` | |

Passo a passo:

1. Numere os bits envolvidos (bits 4 a 7 → máscara `1111 0000` = `0xF0`).
2. Escolha a instrução da tabela acima.
3. **Confira se a constante é válida no Operand2** ([Tabela p.6]): um byte deslocado, ou padrões `0x00XY00XY`, `0xXY00XY00`, `0xXYXYXYXY`. `0xFF0000FF` **não** é válida. Nesse caso, faça em **2 instruções** (`BIC #0xFF` e `BIC #0xFF000000`) ou use `BFC`.
4. **Multiplicar sem MUL:** decomponha em ×5, ×2, ×4... (×100 = ×5, ×5, ×4). **Dividir por 2ⁿ:** `LSR` (`ASR` com sinal). **Resto por 2ⁿ:** `AND #(2ⁿ−1)`.
5. **Trocar bytes / substituir campos:** monte o valor pronto em um registrador de rascunho e use `BFI` (ex.: `MOV R1,#0x22` / `BFI R0,R1,#8,#8`).

---

<a id="g"></a>
## G. Laços: contar bits e percorrer strings (Q8, Q10)

Receita geral de laço em assembly:

1. **Planeje** com uma tabela: contador, ponteiro, valor lido, resultado, qual registrador é cada um.
2. **Inicialize** (contador = 0, ponteiro = endereço).
3. **Corpo:** leia o dado (`LDRB` para byte), teste a condição de parada.
4. **Atualize** contador/ponteiro.
5. **Desvie** de volta (`B loop` ou `BNE`) e **termine** no rótulo `fim`.
6. **Teste de mesa** com um caso pequeno e com o caso vazio (string "" ou R1 = 0).

**Contar bits 1 (Q8):** desloque para a direita e some o carry.

```
        MOV   R0, #0
conta   LSRS  R1, R1, #1      ; C = bit que saiu, Z = (R1 == 0)
        ADC   R0, R0, #0      ; R0 += C (sem S: não altera Z)
        BNE   conta
```

**Comprimento de string (Q10a):** `LDRB R2,[R1,R0]` / `CBZ R2,fim` / `ADD R0,R0,#1` / `B loop` (o terminador é `0x00`).

**Inverter string (Q10b):** com n = comprimento, percorra i de n−1 até 0 lendo `s[i]` e gravando em `dst++` (`STRB R4,[R3],#1`); ao final grave o `0x00`.

Dicas: `CBZ`/`CBNZ` não alteram flags e só saltam **para frente**; `SUBS` num laço já serve de teste.

---

<a id="h"></a>
## H. Variáveis e vetores na memória (Q9 e Q12)

Como o Cortex-M é load/store (RISC), a conta é sempre: **carrega, calcula, guarda.**

1. **Carregue o endereço base** em um registrador: `LDR R3, =0x40000000`.
2. **Variável:** `LDR Rx,[R3,#deslocamento]` (a=+0, b=+4, c=+8 porque cada uma é word).
3. **Calcule** só entre registradores.
4. **Grave** com `STR Rx,[R3,#deslocamento]`.
5. **Vetor de words:** `mat[k]` está em `base + 4k`:
   - índice **constante**: `LDR R0,[R5,#4*k]` (mat[7] → `#28`);
   - índice em **registrador**: `LDR R0,[R5,R1,LSL #2]`.
6. **`mat[i] = mat[10] + mat[j]`:** leia `i` e `j` da memória, leia `mat[10]` e `mat[j]`, some, grave em `[R5,R1,LSL #2]`.
7. Cuidado: se a variável *i* for reescrita, releia o valor antes de usá-lo como índice.

---

<a id="i"></a>
## I. Pilha: PUSH/POP (Q13 e Q14)

Regras (as três explicam todas as questões):

1. A pilha é **cheia e decrescente**: `PUSH` faz **SP ← SP − 4** por registrador e depois grava.
2. Numa lista, **o registrador de menor número vai para o menor endereço**, e **a ordem escrita é irrelevante** (`{R5,R4}` = `{R4,R5}`).
3. `POP` faz o inverso: menor registrador ← menor endereço, e SP sobe.

Passo a passo para resolver:

1. **Desenhe a memória** (endereços crescendo para cima), marcando SP inicial.
2. **Execute cada PUSH:** desça SP e escreva os valores (de R menor no endereço mais baixo).
3. **Execute cada POP:** leia do SP para os registradores e suba SP.
4. **Valores que ficam abaixo do SP** são lixo; só mostre-os como "(velho)".
5. Escreva o valor final de **cada** registrador pedido (R4, R5, R6), incluindo os que não mudaram.
6. **Q14** (`POP {PC}` com valor 0): o bit 0 do endereço deve ser 1 (Thumb). Com 0, o PC vai para um endereço inválido e ocorre falha (UsageFault, escalada para HardFault).

---

<a id="j"></a>
## J. Sub-rotinas AAPCS (Q15, Q16 e exercício dos primos)

Este é o tipo que o professor cobra com planejamento (prova 2022, Q3: 3a planejamento, 3b registradores, 3c código).

### Passo 1: Planejamento (3a)
Escreva o **algoritmo em passos** em português/pseudocódigo. Ex. primos: "para cada primo p da lista: r = iut − (iut/p)·p; se r = 0 retorne 0; ao acabar retorne 1".

### Passo 2: Tabela de alocação (3b)
Liste cada variável e o registrador, seguindo a AAPCS:

| Regra AAPCS | Consequência |
|---|---|
| Argumentos em R0-R3 (nesta ordem) | `iut→R0, primes→R1, np→R2` |
| Retorno em R0 | escreva o resultado em R0 no final |
| R0-R3, R12 são "rascunho" | pode destruir sem salvar |
| R4-R11 são preservados | se usar, `PUSH` na entrada e `POP` na saída |
| Se a função chama `BL`, LR é destruído | `PUSH {...,LR}` e `POP {...,PC}` |
| SP alinhado em 8 bytes | empilhe número **par** de registradores (`PUSH {R4,LR}`) |

Tente sempre resolver **só com R0-R3 e R12** (função "folha", sem PUSH/POP).

### Passo 3: Esqueleto da função (modelo do lab)

```
        PRESERVE8
        THUMB
        AREA    |.text|, CODE, READONLY, ALIGN=2
        EXPORT  nome
nome    PROC
        ; R0 = ..., R1 = ...   (comentar o mapeamento dos parâmetros)
        ...
        BX      LR
        ENDP
        END
```

### Passo 4: Corpo com o padrão de laço (seção G), fechando com `BX LR`.

### Passo 5: Idiomas úteis
- **Resto (módulo):** `r = a − (a/b)·b` → `UDIV R12,R0,R3` + `MLS R12,R12,R3,R0` (o enunciado ensina a fórmula; `MLS` faz mult+sub em 1).
- **Percorrer vetor de words:** `LDR R3,[R1],#4` (pós-indexado) e contador com `SUBS R2,R2,#1` / `BNE`.
- **√(x²+y²) (Q16):** `MUL R0,R0,R0` / `MLA R0,R1,R1,R0` / `BL SQRT`; como usa `BL`, salve LR: `PUSH {R4,LR}` ... `POP {R4,PC}`.
- **Proteja casos-limite** (np = 0 → `CBZ`).

### Passo 6: Teste de mesa
Simule com o exemplo do enunciado (`check_prime(6,{2,3,5},3)` = 0) e com um caso que retorna 1.

---

<a id="k"></a>
## K. Pseudo-instruções e disassembly (Q17)

1. Crie um projeto a partir do template do professor (`asm_minimum`) e escreva cada pseudo-instrução com **argumentos escolhidos para dar sequências diferentes**.
2. **Escolha de argumentos:** constante pequena (0x42), constante que só serve com `MVN` (0xFFFFFFFF), constante arbitrária (0x12345678), rótulo perto e rótulo longe (uma diretiva `SPACE 4096` no meio).
3. Compile e olhe **View → Disassembly** no Keil. Anote a coluna de instruções reais.
4. **Pergunta b:** a pseudo-instrução `LDR R0, =valor` (sinal `=`) carrega a **constante**; a real `LDR R0,[R1]` (colchetes) **lê a memória**.

Resultado esperado no Cortex-M4:

| Pseudo | Vira |
|---|---|
| `LDR R0,=0x42` | `MOV` (1 instrução) |
| `LDR R0,=0xFFFFFFFF` | `MVN` |
| `LDR R0,=0x12345678` | `LDR PC-relativo` + *literal pool* (ou MOVW/MOVT) |
| `MOV32` | sempre `MOVW`+`MOVT` |
| `NEG R0,R1` | `RSB R0,R1,#0` |
| `ADRL` | 1 ou 2 `ADD/SUB Rd,PC,#imm` |

---

<a id="l"></a>
## L. Diagrama de estados / MEF (exercício do git)

Siga o método do professor (slides 9 fsm). **Notação da transição: `evento [guarda] / ações`**, os três campos são opcionais.

1. **Identifique o sistema reativo** e o **objeto** que muda de estado (aqui: o arquivo).
2. **Liste os eventos externos** (os comandos: `git add`, `git commit`, `git restore`, `git rm`, `git merge`, editar).
3. **Liste os estados estáveis**: **substantivos ou particípios** (`NaoRastreado`, `Modificado`, `Preparado`, `Inalterado`, `EmConflito`).
4. **Desenhe o estado inicial** (bolinha preta) e o **final** (quando fizer sentido).
5. **Para cada estado, pergunte: "o que acontece se cada evento ocorrer aqui?"**. Esta é a **matriz Estado × Evento** do professor; preencha, e "–" quando o evento é ignorado.
6. **Transições:** escreva `evento [guarda] / ação` na seta (ex.: `git pull [remoto mudou] / atualiza conteúdo`).
7. **Use hierarquia:** um estado é **superestado OR** (só um subestado ativo) quando vários estados compartilham uma saída. Ex.: "Rastreado" agrupa todos, e `git rm --cached` sai dele de qualquer subestado.
8. **Use `entry/exit/do`** quando houver ações ao entrar/sair; **`after(T)`** para timeouts.
9. **Revise:** todo estado tem saída? Algum evento sem tratamento? Nomes são substantivos?

Codificação (se pedirem): três formas do slide: `switch(state)`, `switch(event)`, ou **matriz de ponteiros de função** `state = mee[state][event](state);`.

---

## Checklist final antes de entregar qualquer questão de assembly

- [ ] Usei os registradores que o enunciado mandou.
- [ ] Sinal certo (GE/LT... × HS/LO...)?
- [ ] Constantes imediatas válidas no Operand2?
- [ ] Menor número de instruções (shift no Operand2, MLA/MLS, IT)?
- [ ] "Sem salto" → só IT? Bloco IT com até 4 instruções?
- [ ] AAPCS: R4-R11 salvos se usados; LR salvo se houve `BL`; retorno em R0 com `BX LR`?
- [ ] Comentei cada linha e fiz teste de mesa com caso de borda?
