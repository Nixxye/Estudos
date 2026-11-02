# Análise dos resultados da rodada noturna (22/10/2026)

Fonte dos números: `simulacao/vivado/overnight/RESUMO.md` e `results_overnight.json`, relatórios de cada compilação em `simulacao/vivado/runs/<variante>/` e o relatório geral em [RELATORIO_FINAL.md](RELATORIO_FINAL.md). Todos os valores vêm da **estimativa de potência do Vivado 2025.2** aplicada à simulação temporizada (SAIF por janela de 10 ns), **não de medição física**. O objetivo desta análise é avaliar o **vazamento do projeto e o efeito de cada variante de implementação**, para dimensionar as defesas.

## 1. O que rodou

| Variante | Compilação | Resultado da rodada |
|---|---|---|
| `base` | diretivas padrão | OK, 4.999 cifragens |
| `explore` | `Explore` em posicionamento, roteamento e otimização física | OK, 4.999 cifragens |
| `aggressive` | `AggressiveExplore` nas três etapas | **FALHOU em `opt_design`** (erro `Synth 20-411`, mensagem vazia). A falha ocorreu **antes** de qualquer diretiva de posicionamento, então **não foi causada pela diretiva**. Causa não investigada. **Sem dados** |
| `quick` | `Quick` em posicionamento e roteamento | OK, 4.999 cifragens |
| `nobram` | `synth_design -max_bram 0` (S-box em LUTs) | OK, 4.999 cifragens |

Verificação funcional: nas 4 variantes concluídas, os estados do registrador gravados na simulação temporizada **coincidem com o modelo Python em todos os ciclos e em todas as cifragens**. Os 17 testes automáticos passam.

## 2. Custo de cada compilação (relatórios do Vivado, clock de 10 ns, XC7Z020)

| Variante | LUTs | FFs | BRAM (tiles) | WNS (ns) | Potência total (W) | Dinâmica (W) |
|---|---|---|---|---|---|---|
| base | 748 | 278 | 4,5 | +1,93 | 0,154 | 0,051 |
| explore | 748 | 278 | 4,5 | +1,93 | 0,154 | 0,051 |
| quick | 753 | 278 | 4,5 | +1,21 | 0,155 | 0,051 |
| nobram | 1.251 | 422 | 0 | +3,29 | 0,149 | 0,045 |

- `explore` tem **custo e traços idênticos** aos de `base` (correlação 1,000 entre as correntes em todas as 4.999 cifragens). As diretivas foram aplicadas (conferido no log), mas **geraram o mesmo posicionamento e roteamento**. (Os arquivos SDF têm hashes diferentes só pela data gravada no cabeçalho.)
- `quick` muda pouco o circuito (+5 LUTs, WNS menor em 0,7 ns).
- `nobram` custa **+67% de LUTs e +52% de FFs**, elimina a BRAM e tem **melhor folga de temporização**.
- A potência dessa tabela é vetorless (sem atividade de simulação). Só serve como custo relativo.

## 3. Força do vazamento por variante e hipótese

Correlação média do palpite **certo** sobre os 16 bytes (todas as cifragens). A incerteza da média é de cerca de **±0,0035** (erro-padrão aproximado, assumindo bytes independentes). `N est.` usa a fórmula gaussiana N ≈ 3 + 8·(3,719/ln((1+ρ)/(1−ρ)))².

| Variante | `reg_load` (K0, janela 1) | `sbox_load` (K0, janela 1) | `reg_last` (K10, janela 11) | `sbox_last` (K10, janela 11) |
|---|---|---|---|---|
| base | 0,088 | **0,184** | 0,047 | **0,174** |
| explore | 0,088 | 0,184 | 0,047 | 0,174 |
| quick | 0,089 | **0,188** | 0,049 | 0,166 |
| nobram | **0,210** | 0,105 | **0,200** | 0,074 |

Hipóteses: `reg_*` = distância de Hamming do registrador de estado; `sbox_*` = transição da saída combinacional da S-box (`sbox_load`: SB(0)=0x63 → SB(pt⊕k); `sbox_last`: SB(s9) → SB(ct)).

### Resultado empírico (subconjuntos sorteados, 20 por N)

| Variante e hipótese | Chave inteira com N = 800 / 1.600 / 3.200 |
|---|---|
| base, `sbox_load` | 0,30 / **0,90** / 1,00 |
| base, `sbox_last` | 0,00 / 0,10 / 0,35 (15,3 de 16 bytes em N = 3.200) |
| quick, `sbox_load` | 0,30 / 0,80 / 1,00 |
| nobram, `reg_last` | 0,65 / **1,00** / 1,00 |
| nobram, `reg_load` | 0,00 / 0,20 / 0,65 |
| base e explore, `reg_*` | 0 em todos os N (menos de 5 bytes certos em média em N = 3.200) |

## 4. Interpretação

1. **O vazamento forte da base está na lógica combinacional da S-box, não no registrador.** Nas três variantes com BRAM, as hipóteses `sbox_*` têm ρ ≈ 0,17 a 0,19, contra 0,05 a 0,09 das hipóteses de registrador. Isso confirma, com 5.000 cifragens e três compilações, o achado do lote inicial de 499. O modelo simples do baseline (só o registrador) **não representa** a estimativa do Vivado.
2. **Diretivas de compilação quase não mudam o vazamento.** `quick` difere de `base` em ρ por no máximo 0,008 (0,184 para 0,188 em `sbox_load`; 0,174 para 0,166 em `sbox_last`), da ordem de 1 a 2 erros-padrão da diferença, ou seja, **sem efeito demonstrável**. `explore` é idêntico à base. Os traços de `quick` e `base` têm correlação de 0,89 a 0,92, então não são iguais, mas a **força** do vazamento permanece.
3. **Trocar a implementação da S-box (`nobram`) muda ONDE o vazamento aparece, não o quanto.** Com a S-box em LUTs, as hipóteses de registrador passam a ser as fortes (ρ ≈ 0,20 a 0,21) e as de S-box as fracas (0,07 a 0,10). O melhor ρ da `nobram` (0,210) é **maior** que o da base (0,184), uma diferença de cerca de 7 erros-padrão. Pela fórmula, N estimado cai de ≈ 805–898 para ≈ 613–677, e empiricamente a chave inteira cai com N = 1.600 em `reg_last` (taxa 1,00). **Para um atacante que use a hipótese certa, a `nobram` não é mais segura e custa 67% mais LUTs.**
4. **A correlação entre as correntes de variantes diferentes mostra o quanto os traços diferem:** base e quick 0,89 a 0,92; base e nobram 0,43 a 0,55. Isso sugere que **variar a implementação da S-box muda muito mais o traço do que variar apenas a compilação**. Por si só, essa correlação não mede nenhum efeito de segurança.
5. **A estimativa gaussiana por ρ médio é otimista.** Para `base/sbox_last`, ela dá N ≈ 898, mas empiricamente a chave inteira só aparece em 35% das tentativas com N = 3.200. A estimativa pelo ρ do **pior byte** (ρ mín. = 0,114 → N ≈ 2.129) fica mais próxima. Use o pior byte ou a curva empírica.
6. **A janela da carga (`sbox_load`) é um pouco mais forte que a da última rodada (`sbox_last`):** 0,184 contra 0,174 na base, e a chave inteira cai com N = 1.600 contra mais de 3.200.

## 5. Consequências para o projeto

- **Energia do baseline:** o modelo sintético (distância de Hamming do registrador) deve ser substituído pelas **tabelas derivadas do Vivado** para qualquer comparação de defesas. O σ do baseline sintético é arbitrário e não é comparável com esses números.
- **Catálogo de variantes:**
  - Diretivas de compilação como fonte de diversidade têm **efeito não demonstrado** neste projeto (uma alternativa distinta, `quick`, ρ praticamente igual).
  - A variante de implementação (BRAM contra LUTs) **desloca** o vazamento e custa área. Só gera defesa se o atacante não souber qual hipótese usar, o que **não foi testado**.
- **Hipótese a testar na etapa seguinte (defensiva):** o efeito de alternar entre implementações sobre um atacante que não sabe qual está ativa. A correlação de 0,43 a 0,55 entre `base` e `nobram` é um indício, não um resultado.
- **Custo das defesas:** a tabela da seção 2 já dá a coluna de custo (LUTs, FFs, WNS) para a tabela S1 do plano.

## 6. Limites e pendências

- **Potência é estimativa do Vivado**; a corrente do trilho da BRAM (`Vccbram`) é **constante** no modelo, então o consumo da BRAM não depende dos dados.
- **Um único projeto** (AES iterativo pequeno, 748 LUTs) e **uma família de FPGA**.
- **Hipóteses `sbox_*` foram formuladas depois de ver o primeiro lote** (499 cifragens), mas se confirmaram nas quatro variantes concluídas e mudaram de forma coerente na `nobram`.
- **`aggressive` sem dados**: falha em `opt_design` a investigar.
- **Compilações realmente distintas** ainda faltam (só `quick` difere de `base`). Restrições de posição ou variantes de RTL são o caminho natural.
- **Intervalos:** os erros-padrão acima são aproximados. A curva empírica usa 20 subconjuntos por N, que não são independentes entre si (todos saem do mesmo conjunto de 4.999 cifragens).
- **Nada foi medido em hardware**; o ruído de medição não está modelado.
