# Tabela comparativa: P, PI, PD, PID, Avanço e Atraso

## 1. O que cada controlador adiciona ao lugar das raízes

| Controlador | C(s) | Polos que adiciona | Zeros que adiciona | Onde fica o zero |
|---|---|---|---|---|
| **P** | Kp | nenhum | nenhum | não tem |
| **PI** | Kp + Ki/s = Kp(s + Ki/Kp)/s | **1 em s = 0** | **1** | −Ki/Kp |
| **PD** | Kp + Kd·s = Kd(s + Kp/Kd) | nenhum (ideal) | **1** | −Kp/Kd |
| **PID** | Kp + Ki/s + Kd·s = (Kd·s² + Kp·s + Ki)/s | **1 em s = 0** | **2** (raízes de Kd·s² + Kp·s + Ki) | raízes do numerador |
| **Avanço (LEAD)** | (s + z)/(s + p), com 0 < α < 1 | 1 (real, longe da origem) | 1 | **mais perto** da origem que o polo |
| **Atraso (LAG)** | (s + z)/(s + p), com α > 1 | 1 (real, perto da origem) | 1 | **mais longe** da origem que o polo |

## 2. Para que serve e o que muda na resposta

| Controlador | Efeito principal | Efeito no erro estacionário | Efeito na resposta transitória | Problema / cuidado |
|---|---|---|---|---|
| **P** | muda só o ganho: o polo anda sobre o lugar já existente | reduz o erro, não zera | só anda sobre as raízes que a planta já tem | não leva o polo a pontos fora do lugar original |
| **PI** | zera o erro ao degrau (sobe o tipo em 1) | **zera** (tipo + 1) | o polo em 0 puxa o lugar para a direita (mais lento, mais oscilação); o zero compensa | o zero **aumenta o overshoot**; precisa ajuste fino |
| **PD** | puxa o lugar para a esquerda: mais amortecimento, menor ts | não muda (não altera o tipo) | melhora Mp e ts | amplifica ruído; derivador puro não existe fisicamente (filtro com polo a ≥ 10z) |
| **PID** | junta as duas coisas | zera (como o PI) | melhora (como o PD) | três ganhos para ajustar; sintonia por Ziegler-Nichols dá overshoot alto |
| **Avanço** | aproxima o PD, sem ganho infinito em alta frequência | pouco | melhora Mp e ts | |
| **Atraso** | aproxima o PI, sem polo exato em 0 | melhora (Kp, Kv ou Ka maior) | quase não mexe nos polos dominantes | resposta mais lenta se mal escolhido |

## 3. O que vem direto e o que precisa ser calculado (o método dos exercícios)

| | **PD** (Q1) | **PI** (Q2) | **PID** (Q3, Ziegler-Nichols) |
|---|---|---|---|
| Alvo s₀ | **sim**: σ = 4/ts, ζ pelo Mp, ωd | **sim**, igual | **não precisa**: usa só Ku e Pu |
| Zero | **calculado** pela condição de ângulo: θz = Σθpolos − 180° | **calculado** pela condição de ângulo; o **polo em 0 entra na soma** dos ângulos | já vem da tabela (Ti, Td) |
| Ganho | **calculado** pela condição de módulo: Kd = ∏\|s₀ − pk\| / (K_G·\|s₀ + z\|) | **calculado** pela condição de módulo (o polo em 0 entra no produto) | já vem da tabela: Kp = 0,6·Ku |
| Os outros ganhos | **direto**: Kp = z·Kd | **direto**: Ki = z·Kp | **direto**: Ki = Kp/Ti, Kd = Kp·Td |
| Entrada do método | planta e especificações | planta e especificações | Ku (Routh) e Pu = 2π/ωu (equação auxiliar) |
| Precisa de Routh? | não | não | **sim** (Ku e ωu) |
| Precisa ajuste fino? | sim (levemente) | sim (o zero eleva o Mp) | sim (Mp de ~59 % antes do ajuste) |

## 4. Resultado numérico de cada questão

| | Projeto pelo método | Depois do ajuste fino |
|---|---|---|
| **Q1 PD** | z = 13,94; Kd = 27,94; Kp = 389,2 → Mp 14,5 %, ts 1,013 s | Kd = 28, Kp = 364 → Mp 12,1 %, ts 0,77 s |
| **Q2 PI** | z = 15,26; Kp = 4; Ki = 61 → Mp 17,7 %, ts 0,37 s | Kp = 5, Ki = 30 → Mp 3,75 %, ts 0,454 s |
| **Q3 PID** | Ku = 96, Pu = 0,811 s; Kp = 57,6, Ki = 142, Kd = 5,84 → Mp 59 % | Kp = 45, Ki = 60, Kd = 16 → Mp 8,6 %, ts 2,15 s |

## 5. Regra para decidir qual usar

| Se o problema pede... | Use |
|---|---|
| só ajustar a rapidez/amortecimento, erro já aceitável | **PD** (ou avanço) |
| erro estacionário zero, resposta não precisa ser rápida | **PI** (ou atraso) |
| erro zero e boa resposta transitória | **PID** |
| planta de 1ª ordem e polos desejados complexos | **PI ou PID** (P não chega ao alvo, o lugar fica no eixo real) |

> Tudo aqui vem do que foi aplicado nas questões e nos slides das Aulas 10, 12, 13, 14 e 15. A classificação de avanço e atraso usa a convenção padrão (confira com o α dos seus slides da Aula 10). O Ziegler-Nichols está na Aula 15.
