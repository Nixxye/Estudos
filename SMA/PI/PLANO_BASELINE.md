# Plano de implementação: sistema estático sem proteção + ataque (baseline)

Objetivo inicial do grupo: ter **um alvo simples, estático e sem proteção**, quebrar a chave dele em simulação e medir o quanto custa. Esse resultado é a **linha de base** contra a qual toda defesa, variante e política de agentes será comparada depois.

Escopo: tudo roda **no computador**, sobre um modelo simulado do nosso próprio alvo. Não há dispositivo real nem terceiros envolvidos.

> Este plano **não entra no PI** (30/10). Serve ao PF. Dar um limite de tempo para não competir com PEAS, Prometheus e o Walker.

---

## 1. Critério de sucesso

1. O alvo cifra corretamente: reproduz o vetor de teste do FIPS-197 (Apêndice C.1: chave `000102…0f`, texto `00112233…ff`, cifra `69c4e0d86a7b0430d8cdb78070b4c55a`).
2. O ataque recupera **os 16 bytes da chave** a partir de traços simulados, e o resultado confere com a chave usada.
3. Existe uma curva **taxa de sucesso × número de traços** e um valor de **traços até divulgação** para a condição base, com repetições suficientes.
4. Controles negativos falham como esperado (ver §6).
5. O código está organizado para receber defesas depois sem reescrever o ataque.

---

## 2. Ambiente (estado atual da máquina)

Verificado agora:

| Item | Estado |
|------|--------|
| Python 3.13 e NumPy 2.5 | instalados |
| matplotlib 3.11 | instalado |
| SciPy, pycryptodome, cocotb | **não** instalados |
| iverilog, verilator, yosys, ghdl, gtkwave, vivado | **não** instalados |

Consequência: o **Estágio A** (todo em Python) pode começar já. O **Estágio B** (alvo em Verilog) exige instalar um simulador.

Instalações opcionais para o Estágio A:
```bash
pip install scipy pycryptodome
```
(SciPy ajuda no teste t; pycryptodome serve de referência independente do AES. Dá para dispensar os dois.)

---

## 3. Alvo escolhido

**AES-128 iterativo de uma rodada por ciclo**, que é o tipo de núcleo que os artigos atacam (o RFTC usa um AES de 10 ciclos).

- O estado fica num **registrador de 128 bits** atualizado a cada ciclo.
- **Fonte de vazamento:** transições dos bits desse registrador (distância de Hamming entre o valor antigo e o novo), que é o modelo padrão para registradores.
- **Chave fixa e secreta** no alvo. O atacante conhece o algoritmo, escolhe/observa os textos de entrada e vê o texto cifrado e o traço.

Por que a última rodada: na última rodada não há MixColumns, então o atacante testa 256 palpites por byte da **última chave de rodada (K10)**, usando o texto cifrado. Recuperada K10, inverte-se o escalonamento de chave e obtém-se a chave mestra.

---

## 4. Estágio A: tudo em Python

### A0. Preparação
- Criar `PI/simulacao/baseline/` com os módulos abaixo.
- Fixar uma semente aleatória para reprodutibilidade, mas rodar várias sementes nos experimentos.

### A1. `aes_target.py`: o alvo
- AES-128 completo (expansão de chave, 10 rodadas), escrito de forma que **exponha o valor do registrador de estado a cada ciclo** (ciclo 0 a 10).
- **Teste obrigatório:** o vetor FIPS-197. Se falhar, não prosseguir.
- Teste extra: comparar com pycryptodome em milhares de entradas aleatórias, se instalado.

### A2. `leakage.py`: gerador de traços
Para cada cifragem:
- Calcular, por ciclo, `HD(estado_anterior, estado_novo)` (128 bits).
- Montar o traço: uma amostra por ciclo (ou algumas por ciclo, com formato de pulso, se quiser mais realismo).
- Somar **ruído gaussiano** com desvio `sigma` e, opcionalmente, um deslocamento constante e **quantização** (para imitar o conversor do osciloscópio).
- Parâmetros expostos: `sigma`, `amostras_por_ciclo`, `quantizacao`, `modelo` (HD ou HW).
- Saída: matriz de traços `(N, amostras)`, textos de entrada e textos cifrados, salvos em `.npz`.

Observação importante: a simulação não tem ruído natural. O ruído é escolhido por nós, então os números absolutos de traços dependem de `sigma`. Calibrar `sigma` para que o baseline caia em algo da ordem de milhares de traços (o RFTC reporta ~2.000 para o AES sem proteção em placa real) e **registrar o valor escolhido**.

### A3. `cpa.py`: o ataque
- Para cada byte `j` de K10 e cada palpite `g` (0 a 255):
  - calcular o valor do byte do estado antes da última rodada: `InvSBox(c[j] XOR g)`;
  - hipótese de consumo: `HD` entre esse byte (na posição correspondente após ShiftRows) e o byte do texto cifrado;
  - correlação de Pearson com cada amostra do traço.
- Escolher o palpite de maior `|correlação|`.
- Juntar os 16 bytes em K10, **inverter o escalonamento** e produzir a chave mestra candidata.
- Implementação vetorizada em NumPy (como na demo atual), para rodar em segundos.

### A4. `metrics.py`: avaliação
- **Taxa de sucesso (SR)** em função de N: repetir o ataque (por exemplo, 100 vezes) com conjuntos de traços diferentes e contar quantas vezes a chave inteira foi recuperada.
- **Traços até divulgação:** menor N com SR ≥ 0,9.
- **Classificação (key rank / guessing entropy)** por byte: posição do palpite correto na lista ordenada. Mostra progresso mesmo antes da recuperação completa.
- **TVLA (fixo contra aleatório):** dois conjuntos (texto fixo e textos aleatórios), teste t de Welch por amostra, limite ±4,5. No alvo sem proteção deve **vazar** claramente.

### A5. Experimentos
| Experimento | Pergunta |
|-------------|----------|
| E1. Caso base | Quantos traços recuperam a chave completa? |
| E2. Variar `sigma` (por exemplo, 0,5; 1; 2; 4; 8) | Como o ruído escala o custo do ataque? |
| E3. Modelo certo contra errado (HD contra HW) | Quanto custa errar o modelo do atacante? |
| E4. Última rodada contra primeira rodada | Qual alvo é mais barato? |
| E5. Quantização (por exemplo, 8 bits contra 4) | O que a resolução do osciloscópio faz? |
| E6. TVLA | O vazamento é detectado com poucos traços? |

Gerar gráficos com matplotlib: SR × N, classificação × N, mapa de correlação por amostra.

### A6. Controles negativos (devem falhar)
- **Chave aleatória diferente** da do alvo: o ataque não pode "acertar" mais do que o acaso.
- **Traços embaralhados** (associação texto-traço quebrada): a correlação deve cair a ruído.
- **Ruído enorme** (`sigma` muito alto) com N pequeno: SR deve ficar perto de zero.
Se algum controle "acertar", há bug de vazamento de informação no código (por exemplo, usar a chave certa no cálculo da hipótese).

### A7. Formato para reuso
Salvar cada conjunto de traços com seus metadados (`sigma`, modelo, semente, nº de traços, configuração do alvo) em `.npz`. Assim, o laboratório de ataque futuro lê os mesmos arquivos para qualquer defesa.

---

## 5. Estágio B (opcional): alvo em Verilog

Só depois do Estágio A funcionando.

1. **Instalar** um simulador. Opções:
   - **Icarus Verilog** (mais simples no Windows; dizem existir pacote para MSYS2/MinGW, `pacman`, e instalador próprio. **Confirmar**).
   - **Verilator** (mais rápido, instalação mais trabalhosa no Windows; costuma ser usado via WSL).
2. Obter ou escrever um **núcleo AES iterativo** em Verilog, de licença livre e conferida.
3. Escrever um **testbench** que: aplica N textos aleatórios, com chave fixa, e grava **VCD** (ou a contagem de transições por ciclo) para cada cifragem.
4. Converter VCD em traços com **TOFU** (ferramenta citada na revisão; verificar disponibilidade do código) ou com script próprio de distância de Hamming por ciclo, e adicionar ruído como no A2.
5. **Reusar o `cpa.py` e o `metrics.py` do Estágio A, sem alterar**, e comparar resultados com o alvo em Python (devem ser qualitativamente iguais para o registrador de estado).

Cuidados: simulação RTL só vê transições de registradores, sem glitches. Para glitches é preciso nível de porta com atrasos (Vogls, ou Vivado com SDF). Fica fora do baseline.

---

## 6. Estrutura de pastas sugerida

```
PI/simulacao/
├── cpa_demo.py                 # demo simples já existente (1 byte, 1ª rodada)
└── baseline/
    ├── aes_target.py
    ├── leakage.py
    ├── cpa.py
    ├── metrics.py
    ├── run_experiments.py      # E1 a E6, salva resultados e gráficos
    ├── tests/
    │   ├── test_aes_fips197.py
    │   └── test_negative_controls.py
    └── data/                   # .npz gerados (não versionar os grandes)
```

---

## 7. Critérios de aceitação por etapa

| Etapa | Passa quando |
|-------|--------------|
| A1 | Vetor FIPS-197 correto (e igualdade com referência independente, se disponível) |
| A2 | Traços reproduzíveis dada a semente; formato `.npz` documentado |
| A3 | Recupera K10 inteira e a chave mestra para `sigma` baixo e N grande |
| A4 | Curva SR × N monótona (em média); TVLA acusa vazamento acima de 4,5 |
| A5 | Resultados fazem sentido (mais ruído exige mais traços; modelo errado piora) |
| A6 | Todos os controles negativos falham como esperado |
| B (opcional) | Alvo Verilog concorda qualitativamente com o alvo Python |

---

## 8. Riscos e armadilhas

- **Vazamento de informação no código:** usar a chave real ao calcular a hipótese. O controle negativo "chave diferente" serve para pegar isso.
- **Calibração arbitrária de `sigma`:** dizer sempre que os números absolutos dependem dele; comparar variantes só em termos relativos.
- **Modelo de vazamento simplificado:** HD de um registrador é um modelo, não a física do chip.
- **Resultados não conferíveis:** sem placa, não há validação em silício. Declarar a limitação.
- **Escopo:** parar no Estágio A se o tempo apertar. Ele já entrega o que o grupo precisa para o próximo passo.

---

## 9. O que vem depois (ligação com o projeto)

1. Adicionar **jitter** (desalinhamento) ao gerador e um **atacante que realinha**, como na demo.
2. Criar **variantes** com custos diferentes (cada uma com parâmetros de vazamento próprios), calibradas com os dados do RFTC.
3. Gerar a **tabela de variantes** (traços até divulgação × custo) que os agentes MASPY consultam.
4. Comparar a política dos agentes com as linhas de base de [REVISAO_LITERATURA.md](REVISAO_LITERATURA.md).
