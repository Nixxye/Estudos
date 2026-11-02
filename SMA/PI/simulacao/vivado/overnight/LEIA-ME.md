# Rodada noturna (Vivado 2025.2): como lançar e o que esperar

## Lançar (Git Bash, a partir de `PI/simulacao/vivado`)
```bash
cd /c/Users/cjean/Desktop/Estudos/SMA/PI/simulacao/vivado
nohup bash overnight/run_overnight.sh 5000 1,11 > overnight/nohup.out 2>&1 &
```
Argumentos opcionais: nº de cifragens (padrão 5000), janelas de potência (padrão `1,11`: carga e última rodada) e arquivo de variantes (padrão `overnight/variants.conf`).

## O que ele faz, sem interação
Para cada linha de `variants.conf` (base, explore, aggressive, quick, nobram):
1. sintetiza e implementa o `aes_iter` para o XC7Z020 com a diretiva da linha e exporta netlist temporizado + SDF;
2. simula `N` cifragens (mesmos plaintexts em todas as variantes) no xsim com os atrasos, gravando um SAIF por janela escolhida;
3. calcula a potência de cada janela com `read_saif` + `report_power` (XML, resolução de µA);
4. apaga os SAIF (economiza disco);
5. no fim, roda a análise (CPA com 4 hipóteses, bootstrap, comparação entre variantes).

## Duração estimada
Cerca de 40 min de potência por variante (≈ 10.000 janelas × 0,24 s), mais a implementação (1 a 6 min) e a simulação (≈ 3 min). **Total esperado: 3,5 a 4,5 horas.** Disco: ≈ 2 GB temporários por variante (106 GB livres no C:).

## Onde olhar de manhã
- `overnight/RESUMO.md`: tabelas e curvas; `overnight/results_overnight.json` e `overnight/overnight.png`.
- `overnight/logs_<data>/run.log`: linha do tempo; `status.txt`: OK ou FALHA por variante; um log por etapa.
- Dados brutos: `sim_<variante>_5000/power.csv` (colunas enc, win, vccint_dyn_A, vccint_total_A, vccbram_dyn_A).

## Retomar ou refazer só a análise
- **Retomar:** rode o mesmo comando. Etapas já prontas (netlist e `power.csv` completos) são puladas.
- **Só a análise:** `cd ../baseline && python analyze_overnight.py 5000 1,11 "$(pwd)/../vivado/overnight/variants.conf"`

## Cuidados
- O computador **não pode suspender** durante a rodada (Configurações > Sistema > Energia). Deixe o Windows ligado na tomada.
- Não abra o Vivado em outra janela rodando os mesmos arquivos.
- Os resultados vêm da **estimativa de potência do Vivado**, não de medição.
