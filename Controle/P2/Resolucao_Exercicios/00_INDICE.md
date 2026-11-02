# Resolução dos exercícios da P2 (Controle A, ELN77A)

Uma resolução por exercício do [Exercicios_P2.pdf](../Exercicios_P2.pdf), **na mesma ordem do PDF**. Cada arquivo traz: origem (página do PDF e slide), enunciado, resolução passo a passo **pelo método do professor**, resposta, conferência e MATLAB.

Todos os números foram conferidos com Python (numpy/scipy). **O MATLAB não foi rodado**; os códigos seguem o formato dos slides.

## Ordem do PDF → arquivo

| Págs. do PDF | Origem | Exercício | Resolução |
|---|---|---|---|
| 2 e 3 | Relatório 04, Q1 | PD: G = 2/(s(s+12)(s+9)), Mp ≤ 15 %, ts ≤ 1 s | [01_Rel04_Q1_PD.md](01_Rel04_Q1_PD.md) |
| 2 e 3 | Relatório 04, Q2 | PI: G = 3/(s+4), Mp ≤ 10 %, ts ≤ 0,5 s | [02_Rel04_Q2_PI.md](02_Rel04_Q2_PI.md) |
| 3 | Relatório 04, Q3 | PID por Ziegler-Nichols, G = 10/(s(s+10)(s+6)) | [03_Rel04_Q3_PID.md](03_Rel04_Q3_PID.md) |
| 4 a 6 | Aula 10, slides 3 a 5 | Exercício: T₁, T₂, T₃ (polos dominantes) | [04_Aula10_Exercicio_T1_T2_T3.md](04_Aula10_Exercicio_T1_T2_T3.md) |
| 7 e 8 | Aula 10, slides 6 e 7 | Resposta ao degrau de 40/((s+20)(s+2)(s+1)) | [05_Aula10_Resposta_ao_degrau_G40.md](05_Aula10_Resposta_ao_degrau_G40.md) |
| 9 a 12 | Aula 10, slides 19 a 22 | Compensador LAG | [06_Aula10_Compensador_LAG.md](06_Aula10_Compensador_LAG.md) |
| 13 a 16 | Aula 10, slides 24 a 27 | Compensador LEAD | [07_Aula10_Compensador_LEAD.md](07_Aula10_Compensador_LEAD.md) |
| 17 a 30 | Aula 11, slides 7 a 20 | Bode (dois exemplos + elementos) | [08_Aula11_Bode.md](08_Aula11_Bode.md) |
| 31 a 35 | Aula 12, slides 3 a 11 | Efeito de P, PI e PD | [09_Aula12_Efeito_de_P_PI_PD.md](09_Aula12_Efeito_de_P_PI_PD.md) |
| 36 a 49 | Aula 13, slides 6 a 19 | Projeto de PD (G = 2/s²) + AmpOps | [10_Aula13_Projeto_PD_e_AmpOps.md](10_Aula13_Projeto_PD_e_AmpOps.md) |
| 50 a 57 | Aula 14, slides 3 a 10 | Projeto de PI (G = 1/(s+12)) | [11_Aula14_Projeto_PI.md](11_Aula14_Projeto_PI.md) |

## Arquivos extras (copiados da pasta P2)

| Arquivo | O que é |
|---|---|
| [12_Bode_Passo_a_Passo.md](12_Bode_Passo_a_Passo.md) | Receita em 8 passos para qualquer Bode, com o exemplo `4/(s(s+1)(s+2)(s+3))` resolvido e a figura |
| [Rel04_Resumo_das_3_questoes_com_MATLAB.md](Rel04_Resumo_das_3_questoes_com_MATLAB.md) | As três questões do Relatório 04 em formato compacto, com o código MATLAB de cada uma |
| [Slides_Consolidado_todos_os_exercicios.md](Slides_Consolidado_todos_os_exercicios.md) | Versão antiga: todos os exercícios dos slides num só arquivo (inclui Aula 10, slides 13 e 14, que não estão no PDF) |
| `img/` | Figuras usadas pelos arquivos |

Material de apoio que ficou na pasta P2: [Resumo](../Resumo_Controle_P2.md), [Tutorial completo](../Tutorial_Controle_P2_Completo.md), [Formulário](../Formulario_P2.pdf) e [Tabela comparativa dos controladores](../Tabela_Comparativa_Controladores.md).

## Receita comum dos projetos (Q1, Q2, Aula 13, Aula 14)

1. **Alvo:** `σ = 4/ts`, `ζmin` pelo Mp, `ωn = σ/ζ`, `ωd = ωn·√(1−ζ²)` → `s₀ = −σ ± jωd`.
2. **Só P resolve?** Se o lugar das raízes sem controlador não passa por `s₀`, precisa de zero (PD) ou de polo em 0 + zero (PI).
3. **Fase:** `θz = Σθpolos − 180°` (o polo em 0 do PI entra na soma). Dá a posição do zero `z`.
4. **Módulo:** ganho = produto das distâncias de `s₀` aos polos ÷ (distância ao zero × ganho da planta).
5. **Simular e ajustar:** o zero costuma aumentar o overshoot; o ajuste fino mexe em `z` e no ganho.
