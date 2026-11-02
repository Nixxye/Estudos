# Resumo: simulação de vazamento de energia em um AES sem proteção (FPGA)

Documento curto para o grupo. Explica a arquitetura da simulação, o que foi encontrado e, principalmente, **o que o resultado não prova**. Tudo aqui pode ser conferido e reproduzido — os comandos exatos estão na seção 5.

---

## 1. O que foi feito, em uma frase

Implementamos um núcleo AES-128 simples (sem nenhuma proteção) em um FPGA Zynq-7020, simulamos o consumo de energia dele com a própria ferramenta do fabricante (Vivado), e tentamos recuperar a chave secreta só olhando essa energia estimada e o texto cifrado — sem nunca "ver" a chave.

## 2. Arquitetura da simulação

```
Circuito (VHDL)                      AES-128 iterativo, 1 rodada/ciclo, SEM proteção
      │  Vivado: síntese + implementação (dispositivo real: XC7Z020)
      ▼
Netlist com atrasos reais (SDF)      inclui os atrasos de roteamento daquela compilação
      │  xsim (simulador do Vivado): simula N cifragens, chave fixa, textos aleatórios
      ▼
Atividade do circuito por janela     1 janela = 1 ciclo de clock (10 ns), gravada em SAIF
      │  Vivado: read_saif + report_power
      ▼
Corrente estimada por janela         arquivo .csv: 1 linha por (mensagem, janela)
      │  Python (NumPy)
      ▼
Ataque por correlação (CPA)          testa 256 palpites por byte da chave, usando
                                      SÓ o texto cifrado + a corrente estimada
```

Pontos-chave:
- **Nada foi medido fisicamente.** Não há placa nem osciloscópio neste projeto. A "corrente" vem de uma estimativa do Vivado baseada na atividade de comutação simulada.
- **O ataque nunca recebe a chave.** Ele só usa o texto cifrado (público) e a leitura de energia; a chave só é usada para gerar os dados de teste e para conferir se o palpite acertou.
- **5 compilações diferentes** do mesmo circuito foram testadas, para ver se mudar a implementação física muda o vazamento (ver seção 4.3).

## 3. Como o ataque funciona (resumo)

O AES-128 cifra em 10 rodadas. Na última rodada e na carga inicial, cada byte da chave afeta só um byte do texto — por isso o ataque quebra o problema de 128 bits em **16 subproblemas de 8 bits** (256 palpites cada), em vez de tentar 2¹²⁸ combinações.

Para cada palpite, o algoritmo prevê "quanto a energia deveria mudar" se aquele palpite estivesse certo, e compara com a energia realmente medida (correlação estatística). O palpite que mais se parece com a realidade é escolhido — mas isso só funciona com **centenas ou milhares de mensagens acumuladas**, porque o sinal é fraco e está misturado com ruído de atividade de outras partes do circuito.

## 4. Resultados

### 4.1 Validação funcional (a simulação está correta?)
Em todas as compilações testadas, os valores internos do circuito simulado (com atrasos reais) bateram **exatamente** com um modelo de referência em Python, ciclo a ciclo, em milhares de cifragens. Isso confirma que a simulação representa fielmente o hardware descrito.

### 4.2 A chave foi recuperada?
Sim, em algumas combinações, não em outras. Com um lote de 4.999 mensagens cifradas:

| Compilação | Hipótese de vazamento usada | Chave inteira recuperada? | Mensagens necessárias |
|---|---|:---:|---|
| base | saída da S-box, na carga da chave | **Sim** | ≈ 1.600 |
| quick | saída da S-box, na carga da chave | **Sim** | ≈ 3.200 |
| nobram | registrador, na última rodada | **Sim** | ≈ 1.600 |
| base, quick, explore | registrador (a suposição padrão de livro-texto) | **Não** | nunca melhor que o acaso |
| nobram | saída da S-box | **Não** | máx. 15 de 16 bytes, com quase 5.000 mensagens |

**Achado mais importante:** a hipótese "padrão" de livro-texto para hardware (o vazamento vem do registrador que guarda o estado) **falhou** na maioria dos casos. Funcionou só depois de testarmos outra hipótese — o vazamento vem da **lógica da S-box**, não do registrador. Isso só foi descoberto testando várias hipóteses contra os dados reais, não era óbvio de antemão.

### 4.3 Mudar a implementação ajuda a esconder o vazamento?
Testamos 5 compilações do mesmo circuito (diretivas diferentes de posicionamento/roteamento, e uma variante sem usar memória de bloco para a S-box):

- **Mudar só as diretivas de compilação** (`explore`, `quick`) teve efeito pequeno ou nulo — uma delas (`explore`) saiu **fisicamente idêntica** à compilação padrão.
- **Mudar a estrutura de verdade** (tirar a S-box da memória, variante `nobram`) mudou bastante **onde** o vazamento aparece — mas não tornou o ataque mais difícil. Na verdade, ficou mais fácil (menos mensagens necessárias), porque o vazamento ficou mais concentrado e mais fácil de modelar.
- Uma quinta compilação (`aggressive`) falhou na própria ferramenta e não gerou dados.

## 5. Como reproduzir (tudo com um comando)

```bash
cd PI/simulacao/baseline
python -m unittest discover -s tests -v        # 17 testes automatizados

cd ../vivado
bash overnight/run_overnight.sh 5000 1,11       # roda tudo: implementa, simula, mede, ataca

cd ../baseline
python build_report.py 5000                      # gera o relatório completo
```

Documentos completos, com todos os números e os scripts: `PI/RELATORIO_FINAL.md` e `PI/ANALISE_RESULTADOS.md`.

## 6. Limitações — o que este resultado NÃO prova

Esta é a parte mais importante para quem só vai ler o resumo.

1. **Não é medição física.** A "energia" é uma estimativa de software do Vivado, calculada a partir da atividade simulada. Não há ruído de instrumento, rede de alimentação real, nem efeitos analógicos — tudo isso existe em um chip de verdade e pode mudar o resultado para melhor ou para pior.
2. **As hipóteses de ataque que funcionaram foram encontradas olhando os dados**, não definidas antes do experimento. Isso é prática comum em segurança (testar vários modelos), mas significa que não houve uma previsão a priori confirmada — é um risco de "ajuste depois do fato" que precisa ser declarado.
3. **Só uma família de FPGA (Zynq-7000) e um circuito pequeno** (AES iterativo básico, ~750 a 1.250 LUTs). Os números não generalizam automaticamente para outros chips ou implementações.
4. **O ataque não tem como lidar com desalinhamento.** Hoje ele assume que sabe exatamente em que ciclo olhar (porque é simulação com tempo conhecido). Qualquer defesa que embaralhe o tempo (como clock aleatório) exigiria estender o ataque — isso não foi feito.
5. **As "variantes de compilação" testadas são poucas e limitadas.** Quatro delas mudam só diretivas da ferramenta (posicionamento/roteamento); só uma (`nobram`) muda a estrutura de verdade. Uma só está quebrada (`aggressive`, sem investigar). Não é uma amostra ampla de "formas de implementar o circuito".
6. **A reconfiguração parcial (trocar de implementação em tempo de execução) foi testada como mecanismo de ferramenta** (ver `RELATORIO_DFX.md`) — confirmamos que o Vivado gratuito consegue gerar e trocar bitstreams parciais — **mas não foi testado o efeito disso sobre o ataque**. Simular essa troca durante um ataque, incluindo o tempo e o possível ruído da própria reconfiguração, é um passo seguinte, ainda não feito, e tem uma limitação adicional: o Vivado não tem como medir o consumo da reconfiguração em si (é um mecanismo interno do chip, fora do nosso projeto), então essa parte só poderia ser modelada por suposição, não medida.
7. **Estatística com grade grossa.** Os tamanhos de lote testados (100, 200, 400, 800, 1.600, 3.200...) dobram a cada passo; os números de "traços necessários" são faixas, não valores exatos. As repetições usadas para estimar taxa de sucesso vêm do mesmo lote de 4.999 mensagens, não são totalmente independentes entre si.

## 7. Em uma frase para fechar

O experimento mostra que, **dentro deste modelo de simulação**, um AES sem proteção tem vazamento de energia explorável e que a defesa mais simples (só mudar diretivas de compilação) não resolve — mas nada disso foi validado em hardware real, e a conexão entre essa simulação e uma defesa de reconfiguração em tempo de execução ainda precisa ser construída e testada.
