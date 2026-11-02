# Resumo da rodada noturna

Cifragens por variante: 5000. Janelas: [1, 11]. Métrica de potência: corrente dinâmica Vccint (A).

## Força do vazamento e ataque, por variante e hipótese

| variante | hipótese | janela | ρ médio do palpite certo | ρ mínimo | bytes certos (todas as cifragens) | N estimado (ρ médio) | N estimado (ρ mín.) | TTD90 (grade) |
|---|---|---|---|---|---|---|---|---|
| base | reg_load | 1 | +0.088 | +0.039 | 7/16 | 3569 | 17831 | None |
| base | sbox_load | 1 | +0.184 | +0.099 | 16/16 | 805 | 2782 | 1600 |
| base | reg_last | 11 | +0.047 | -0.016 | 1/16 | 12570 | 27661921999673 | None |
| base | sbox_last | 11 | +0.174 | +0.114 | 15/16 | 898 | 2129 | None |
| explore | reg_load | 1 | +0.088 | +0.039 | 7/16 | 3569 | 17831 | None |
| explore | sbox_load | 1 | +0.184 | +0.099 | 16/16 | 805 | 2782 | 1600 |
| explore | reg_last | 11 | +0.047 | -0.016 | 1/16 | 12570 | 27661921999673 | None |
| explore | sbox_last | 11 | +0.174 | +0.114 | 15/16 | 898 | 2129 | None |
| quick | reg_load | 1 | +0.089 | +0.046 | 10/16 | 3455 | 13089 | None |
| quick | sbox_load | 1 | +0.188 | +0.106 | 16/16 | 771 | 2439 | 3200 |
| quick | reg_last | 11 | +0.049 | -0.018 | 2/16 | 11394 | 27661921999673 | None |
| quick | sbox_last | 11 | +0.166 | +0.091 | 15/16 | 984 | 3337 | None |
| nobram | reg_load | 1 | +0.210 | +0.130 | 16/16 | 613 | 1632 | None |
| nobram | sbox_load | 1 | +0.105 | +0.080 | 16/16 | 2508 | 4275 | None |
| nobram | reg_last | 11 | +0.200 | +0.121 | 16/16 | 677 | 1861 | 1600 |
| nobram | sbox_last | 11 | +0.074 | +0.035 | 10/16 | 5031 | 22138 | None |

## Variação da corrente entre cifragens (mesma janela)

| variante | janela | média (mA) | desvio (µA) | valores distintos |
|---|---|---|---|---|
| base | 1 | 51.576 | 1246.1 | 3066 |
| base | 11 | 50.935 | 1193.1 | 3011 |
| explore | 1 | 51.576 | 1246.1 | 3066 |
| explore | 11 | 50.935 | 1193.1 | 3011 |
| quick | 1 | 52.231 | 1215.1 | 3059 |
| quick | 11 | 47.725 | 1111.7 | 2903 |
| nobram | 1 | 60.754 | 2130.8 | 3694 |
| nobram | 11 | 72.939 | 2054.5 | 3730 |

## Correlação entre variantes nas mesmas cifragens

| par | correlação |
|---|---|
| base x explore (janela 1) | +1.000 |
| base x quick (janela 1) | +0.921 |
| base x nobram (janela 1) | +0.551 |
| explore x quick (janela 1) | +0.921 |
| explore x nobram (janela 1) | +0.551 |
| nobram x quick (janela 1) | +0.547 |
| base x explore (janela 11) | +1.000 |
| base x quick (janela 11) | +0.888 |
| base x nobram (janela 11) | +0.432 |
| explore x quick (janela 11) | +0.888 |
| explore x nobram (janela 11) | +0.432 |
| nobram x quick (janela 11) | +0.430 |

## Curvas (taxa de sucesso da chave inteira por N e bytes certos médios)

- **base / reg_load**: N=100: 0.00 (0.9/16), N=200: 0.00 (1.3/16), N=400: 0.00 (1.3/16), N=800: 0.00 (2.0/16), N=1600: 0.00 (3.4/16), N=3200: 0.00 (4.7/16)
- **base / sbox_load**: N=100: 0.00 (3.4/16), N=200: 0.00 (6.4/16), N=400: 0.00 (11.6/16), N=800: 0.30 (14.8/16), N=1600: 0.90 (15.9/16), N=3200: 1.00 (16.0/16)
- **base / reg_last**: N=100: 0.00 (1.1/16), N=200: 0.00 (1.0/16), N=400: 0.00 (1.2/16), N=800: 0.00 (1.1/16), N=1600: 0.00 (1.1/16), N=3200: 0.00 (1.3/16)
- **base / sbox_last**: N=100: 0.00 (1.6/16), N=200: 0.00 (3.1/16), N=400: 0.00 (5.5/16), N=800: 0.00 (10.8/16), N=1600: 0.10 (13.6/16), N=3200: 0.35 (15.3/16)
- **explore / reg_load**: N=100: 0.00 (1.0/16), N=200: 0.00 (1.2/16), N=400: 0.00 (1.6/16), N=800: 0.00 (2.2/16), N=1600: 0.00 (2.5/16), N=3200: 0.00 (4.6/16)
- **explore / sbox_load**: N=100: 0.00 (3.0/16), N=200: 0.00 (6.2/16), N=400: 0.00 (11.3/16), N=800: 0.20 (14.7/16), N=1600: 0.95 (15.9/16), N=3200: 1.00 (16.0/16)
- **explore / reg_last**: N=100: 0.00 (1.1/16), N=200: 0.00 (1.1/16), N=400: 0.00 (1.1/16), N=800: 0.00 (1.2/16), N=1600: 0.00 (1.2/16), N=3200: 0.00 (1.5/16)
- **explore / sbox_last**: N=100: 0.00 (0.6/16), N=200: 0.00 (3.3/16), N=400: 0.00 (5.8/16), N=800: 0.00 (9.1/16), N=1600: 0.00 (13.2/16), N=3200: 0.35 (15.3/16)
- **quick / reg_load**: N=100: 0.00 (0.9/16), N=200: 0.00 (1.4/16), N=400: 0.00 (1.4/16), N=800: 0.00 (2.0/16), N=1600: 0.00 (3.1/16), N=3200: 0.00 (5.0/16)
- **quick / sbox_load**: N=100: 0.00 (3.2/16), N=200: 0.00 (7.4/16), N=400: 0.00 (12.1/16), N=800: 0.30 (14.9/16), N=1600: 0.80 (15.8/16), N=3200: 1.00 (16.0/16)
- **quick / reg_last**: N=100: 0.00 (1.2/16), N=200: 0.00 (1.1/16), N=400: 0.00 (1.2/16), N=800: 0.00 (1.2/16), N=1600: 0.00 (1.6/16), N=3200: 0.00 (1.9/16)
- **quick / sbox_last**: N=100: 0.00 (1.2/16), N=200: 0.00 (3.1/16), N=400: 0.00 (5.1/16), N=800: 0.00 (9.3/16), N=1600: 0.00 (12.6/16), N=3200: 0.20 (14.5/16)
- **nobram / reg_load**: N=100: 0.00 (2.1/16), N=200: 0.00 (4.4/16), N=400: 0.00 (8.8/16), N=800: 0.00 (12.7/16), N=1600: 0.20 (14.6/16), N=3200: 0.65 (15.7/16)
- **nobram / sbox_load**: N=100: 0.00 (0.7/16), N=200: 0.00 (1.4/16), N=400: 0.00 (3.0/16), N=800: 0.00 (6.3/16), N=1600: 0.00 (11.3/16), N=3200: 0.30 (15.0/16)
- **nobram / reg_last**: N=100: 0.00 (3.4/16), N=200: 0.00 (8.1/16), N=400: 0.05 (13.1/16), N=800: 0.65 (15.7/16), N=1600: 1.00 (16.0/16), N=3200: 1.00 (16.0/16)
- **nobram / sbox_last**: N=100: 0.00 (0.1/16), N=200: 0.00 (0.6/16), N=400: 0.00 (1.0/16), N=800: 0.00 (2.0/16), N=1600: 0.00 (4.0/16), N=3200: 0.00 (6.7/16)

Leitura: ρ é a correlação do palpite certo; 'N estimado' usa N ≈ 3 + 8·(z/ln((1+ρ)/(1−ρ)))² com z = 3,719 e vale só como ordem de grandeza (hipótese gaussiana).
Todos os resultados vêm da estimativa de potência do Vivado (SAIF da simulação temporizada), não de medição física.
