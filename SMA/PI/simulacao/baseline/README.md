# Baseline: alvo estático sem proteção + ataque (simulação)

Alvo: AES-128 iterativo (uma rodada por ciclo), chave fixa, **sem nenhuma contramedida**.
Fonte de vazamento modelada: distância de Hamming do registrador de estado de 128 bits,
mais ruído gaussiano `sigma` (o registrador é zerado entre cifragens).

- **Alvo A (Python):** `aes_target.py`, `leakage.py`, `cpa.py`, `metrics.py`, `run_experiments.py`
- **Alvo B (VHDL):** `../vhdl/` (`aes_sbox_pkg.vhd` gerado, `aes_pkg.vhd`, `aes_iter.vhd`, `tb_aes.vhd`)
  simulado em GHDL por `vhdl_flow.py`, com o **mesmo** ataque sobre os estados vindos do VHDL.

## Como rodar

```bash
cd PI/simulacao/baseline
python -m unittest discover -s tests -v      # AES (FIPS-197) e controles negativos
python run_experiments.py                    # alvo A, ~2,5 min (use --fast para ~40 s)
python vhdl_flow.py --n 2000 --validate-only # compila o VHDL e compara com o Python
python vhdl_flow.py --n 20000 --sigma 10     # ataque sobre os estados do VHDL
```

GHDL 6.0.0 (backend mcode) foi instalado com `winget install ghdl.ghdl.ucrt64.mcode --source winget`.
Se `ghdl` não estiver no PATH da sua sessão, abra um novo terminal ou defina a variável `GHDL`
com o caminho do `ghdl.exe` (em `%LOCALAPPDATA%\Microsoft\WinGet\Packages\...\bin`).
Não use `python -I` com estes scripts (o modo isolado impede importar os módulos locais).

## Resultados (seed 2026, `sigma` = 10 no caso base)

Taxa de sucesso = fração das repetições em que a **chave inteira** foi recuperada.
TTD90 = menor N da grade com taxa ≥ 0,9. Grade: 50, 100, 200, 400, 800, 1600, 3200, 6400.

| Experimento | TTD90 | Observação |
|-------------|-------|------------|
| E1 base (última rodada, HD, σ=10) | **3.200** | 0,85 em 1.600 e 1,0 em 3.200 (40 repetições) |
| E2 σ = 0 | 800 | mesmo sem ruído, o resto do registrador vira "ruído algorítmico" |
| E2 σ = 5 | 1.600 | |
| E2 σ = 10 | 3.200 | |
| E2 σ = 20 | > 3.200 (0,8 em 6.400) | |
| E3 modelo errado (HW no lugar de HD) | nunca (0 em 6.400) | o modelo do atacante importa muito |
| E4 carga inicial (recupera K0 direto) | 6.400 | mais caro que a última rodada |
| E5 quantização 8 / 4 / 2 bits | 3.200 / 3.200 / 6.400 | 2 bits já atrapalha |
| E6 TVLA fixo contra aleatório | máx \|t\| = 92,7 | limite de 4,5: vazamento evidente |
| Alvo B (VHDL), σ=10 | 3.200 | estados do VHDL idênticos aos do Python em todos os ciclos |

Classificação média do byte correto (E1): 70 com 50 traços, 1,4 com 800, 0 a partir de 1.600.

## O que está validado

- AES: vetores do FIPS-197 (C.1 e A.1) e inversão do escalonamento de chave.
- Controles negativos (todos falham como esperado): traços embaralhados, ruído enorme com poucos
  traços, traços de outra chave, ciclo errado, TVLA nulo (aleatório contra aleatório).
- VHDL: o texto cifrado do vetor FIPS-197 sai correto e **os 11 estados de 20.000 cifragens
  coincidem byte a byte com o modelo Python**.

## Ressalvas (leia antes de citar números)

1. **Poucas repetições.** Com 40 repetições a taxa em N = 1.600 saiu 0,85; uma checagem com 300
   repetições deu ≈ 0,66 (alvo A) e ≈ 0,68 (conjunto do VHDL). Trate os valores de sucesso
   intermediários como ±0,1, e o TTD90 como "entre 1.600 e 3.200". A grade é grossa (dobra a cada passo).
2. **`sigma` é arbitrário.** Foi escolhido para que o baseline caia com alguns milhares de traços,
   ordem de grandeza do AES sem proteção reportado no RFTC (≈ 2.000 em placa real). Não é calibração
   exata. Só comparações relativas entre variantes são robustas.
3. **O alvo B não acrescenta fidelidade física.** Como o modelo é a distância de Hamming do
   registrador, os traços do VHDL e do Python são idênticos. O B valida o hardware descrito e o
   fluxo VHDL → estados → traços → ataque. Glitches e atrasos de roteamento exigem simulação de
   nível de porta com temporização (fora deste baseline).
4. **O atacante sabe em que ciclo atacar** (ciclo 10 para a última rodada, 0 para a carga inicial).
   Na prática o TVLA/SPA localizaria esse instante.
5. **O pool do VHDL é reaproveitado entre repetições** (subconjuntos sorteados de 20.000 cifragens),
   então as repetições do B não são totalmente independentes.
6. Os resultados valem para este modelo de vazamento e este atacante (CPA, sem alinhamento).
