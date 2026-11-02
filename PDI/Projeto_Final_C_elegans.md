# Projeto Final de PDI — Identificação e rastreamento de *C. elegans* em vídeo

Disciplina: IF69D-S11 / OPEET014-OPEL — Processamento Digital de Imagens (UTFPR, Profs. Gamba e Borba)
Peso: **50% da nota final**

---

## 1. Especificações do trabalho (transcrição)

Desenvolvimento (inventar ou entender), implementação (programar e testar), documentação (relatório) e apresentação (explicar com slides e demonstrar) de um algoritmo de processamento de imagem.

### Requisitos
1. Em dupla ou individual.
2. Entregar relatório em **PDF** conforme o modelo do post (LaTeX ou docx). Conciso, sugestão de **4 páginas**. Manter os tópicos do modelo. Preferir explicação detalhada do algoritmo e dos resultados. Mostrar exemplos de resultados de **cada etapa** do algoritmo e avaliações quantitativas ou qualitativas.
3. Entregar os arquivos da implementação, imagens/vídeos para teste e instruções de uso.
4. Entregar os slides da apresentação.
5. Apresentação de no máximo **18 min** (slides + demonstração funcionando).

### Instruções para a apresentação
1. Objetivo claro; exemplos de resultados de cada etapa; avaliações quantitativas ou qualitativas.
2. Dominar o assunto; detalhes técnicos claros e fluentes.
3. Exemplos e resultados claros.
4. Pouco texto: bullets e figuras. **Slides devem ser feitos pelo aluno, não por IA.**
5. Demonstração: algoritmo rodando e resultados sendo gerados ao vivo.
6. Máximo 18 min no total.

### Entrega
- Um `.zip` com tudo (código, imagens/vídeos de teste, instruções, slides, relatório) em **link público** para download; inserir o link no tópico "Entrega" do post.
- Link e material públicos: se exigir pedido de acesso, **não será processado**.

### Datas
- Apresentações: **24.nov, 01.dez e 08.dez de 2026**.
- Quem apresentar em 24.nov ou 01.dez pode entregar o relatório até 08.dez e recebe uma prévia dos professores (saber se terá de reapresentar na recuperação).
- **Reserva de data e de tema: planilhas compartilhadas, por ordem de chegada** (quem preencher antes leva).
  - Datas: https://docs.google.com/spreadsheets/d/1oA3n21i9GCc47tDpzOuq4duwpqmyLuqCUN3KuW-iqSA/edit?usp=sharing
  - Temas: https://docs.google.com/spreadsheets/d/1fs8Nan9M1mUme1OpaNyalrKH6cvaYsTCuyzYrB-SbYc/edit?usp=sharing

> Ação imediata: conferir na planilha de temas se existe tema compatível (ou se é permitido tema livre) e reservar nome + data antes que acabem.

---

## 2. Objetivo proposto

Dado um vídeo de uma placa (ou campo de microscópio) com vários *C. elegans*, **detectar e separar cada verme, atribuir um ID persistente e reconstruir a trajetória individual** ao longo do tempo, com métricas de movimento (distância, velocidade, área coberta).

Pipeline em quatro blocos:

```
Vídeo -> [1] Pré-processamento -> [2] Segmentação -> [3] Separação de indivíduos -> [4] Rastreamento -> trajetórias + métricas
```

---

## 3. Estudo: o que pode ser feito

### 3.1 Por que o problema é bom para PDI
- Verme escuro/translúcido sobre fundo claro (campo claro) ou claro sobre fundo escuro (fluorescência): contraste simples, ideal para limiarização.
- Câmera e fundo estáticos: dá para usar subtração de fundo.
- A dificuldade real e interessante: **vermes que se tocam, cruzam ou se enrolam** (um blob com 2+ vermes) e a **forma muito deformável** (o centroide oscila e a área varia).

### 3.2 Mapeamento com o conteúdo da disciplina

| Etapa | Técnica | Aula |
|---|---|---|
| Conversão e ajuste | RGB para cinza, normalização, contraste/histograma | 01c, 03, 10 |
| Remover ruído e ranhuras do ágar | Filtro de média/gaussiano/mediana, filtros adaptativos | 04, 05 |
| Correção de iluminação irregular | Filtragem no domínio da frequência (passa-alta/homomórfico) ou subtração de fundo por mediana temporal | 07 |
| Segmentação | Limiar global (Otsu) e **adaptativo** | 08 |
| Limpeza da máscara | Morfologia: abertura, fechamento, preenchimento de buracos | 08/09 |
| Separar vermes | Rotulagem de componentes conexos, transformada de distância, esqueletização | 08/09 |
| Bordas/contorno | Sobel, Canny | 06 |
| Qualidade/avaliação | PSNR/SSIM (para efeito dos filtros), IoU/Dice na segmentação | 05 |
| Cor (se vídeo colorido ou fluorescente) | HSV, canal verde da GFP | 09, 10 |

Isso cobre bem "implementação própria", que é o que a disciplina valoriza. Sugestão: implementar à mão (NumPy) as etapas centrais (filtros, Otsu, morfologia, rotulagem) e usar bibliotecas só para I/O e para comparar resultados.

### 3.3 Algoritmos por bloco

**Bloco 1: pré-processamento**
- Fundo estimado como **mediana temporal** de N quadros (vermes se movem, então somem na mediana). Primeiro plano = |quadro − fundo|.
- Alternativa quando houver pouco movimento: fundo por filtro passa-baixa muito largo ou *top-hat* morfológico.
- Suavização gaussiana/mediana leve.

**Bloco 2: segmentação**
- Otsu no quadro diferença ou no quadro corrigido; testar limiar adaptativo (Aula 08) em regiões com iluminação desigual.
- Abertura (remove ruído) + fechamento (liga o verme quebrado por reflexo) + remoção de componentes pequenos por área.

**Bloco 3: separação de indivíduos (núcleo do projeto)**
1. Rotular componentes conexos: cada componente isolado é um verme.
2. Componentes com área/comprimento anômalo (aprox. maior que 1,5× a área mediana) são tratados como **aglomerado**.
3. Para aglomerados, opções em ordem de complexidade:
   - **Transformada de distância + máximos locais + watershed** (clássico, funciona para vermes cruzando em X, ruim para vermes paralelos colados). Watershed não está nos slides, então precisa ser estudado; é um bom ponto de "entender e implementar".
   - **Esqueletização + análise de ramos**: esqueleto de cada verme é uma curva; cruzamentos aparecem como pontos de bifurcação. Dá também comprimento e postura (curvatura).
   - **Predição pelo quadro anterior**: usar a posição/forma anterior de cada verme para dividir o aglomerado (ex.: k-means nos pixels do blob com k = número de vermes esperados, inicializado nas posições previstas).
4. Durante o aglomerado, aceitar perda temporária de identidade e recuperar ao separar (ver trade-off em 3.5).

**Bloco 4: rastreamento**
- Descritor por verme: centroide, área, orientação, comprimento do esqueleto.
- **Associação quadro a quadro**: matriz de custos (distância entre centroides previstos e detecções) resolvida pelo **algoritmo húngaro** (`scipy.optimize.linear_sum_assignment`). Custo pode incluir diferença de área/orientação.
- Predição simples de velocidade constante ou **filtro de Kalman** (opcional, ponto de aprofundamento).
- Gestão de trilhas: criar (detecção sem par), manter por K quadros sem detecção, encerrar.
- Saída: trajetória (x, y, t) por ID, desenhada sobre o vídeo com rastro colorido.

**Métricas de movimento (valor biológico, bom para a demo)**
- Distância total, velocidade média/instantânea, deslocamento líquido, proporção parado/em movimento, área do campo explorada, frequência de ondulação (curvatura do esqueleto ao longo do tempo; aqui a Fourier da Aula 07 entra naturalmente).

### 3.4 Dados para teste (a verificar antes de decidir)

Lembrança de memória, sem checagem online; **confirmar existência, licença e formato**:
- **BBBC010** (Broad Bioimage Benchmark Collection): imagens de *C. elegans* vivos/mortos, com máscaras de referência por verme. Muito bom para avaliar a **segmentação/separação** (imagens estáticas, não vídeo).
- **Open Worm Movement Database / Tierpsy / WormTracker**: vídeos de rastreamento de verme único; úteis para validar trajetória e esqueleto.
- Vídeos públicos de múltiplos vermes em placa (YouTube/Wikimedia/artigos com dados abertos).
- **Vídeo próprio ou de laboratório**: se algum colega/professor da UTFPR tem acesso a lupa + câmera, é o melhor cenário.
- **Vídeo sintético (plano B robusto)**: simular N vermes como curvas senoidais deformáveis (cadeia de segmentos) sobre fundo com ruído, com colisões programadas. Vantagem enorme: **gabarito perfeito de posição e ID**, o que permite avaliação quantitativa limpa. Recomendo combinar: sintético para métricas + real para demonstração.

### 3.5 Avaliação (exigência do relatório e da apresentação)

- **Segmentação**: IoU / Dice por verme contra máscaras manuais (ou da BBBC010).
- **Detecção**: precisão, recall, F1 (contagem de vermes por quadro vs. gabarito).
- **Rastreamento**: nº de trocas de ID (ID switches), fragmentações de trilha, fração de quadros com ID correto (MOTA/IDF1 simplificados), erro médio de posição.
- **Ablações** (ótimo para o relatório): com/sem subtração de fundo; Otsu vs. adaptativo; com/sem watershed; com/sem predição de movimento. Mostrar o ganho de cada etapa com a figura da etapa.
- **Casos difíceis** mostrados honestamente: cruzamento, enrolamento, verme parado (some na subtração de fundo!), vermes saindo do campo.

### 3.6 Riscos e armadilhas

- **Verme parado some na diferença com fundo** se o fundo for estimado só pelo movimento. Mitigar: fundo estático obtido de um quadro/placa vazia, ou limiar direto na intensidade em vez de diferença.
- **Reflexos e bolhas na placa** viram falsos positivos; filtrar por área, alongamento e excentricidade.
- **Enrolamento do verme** (espiral) gera blob compacto que parece "sujeira".
- **Dependência de bibliotecas**: o projeto é de PDI, então a banca tende a valorizar o que foi implementado e entendido. Usar OpenCV/scikit-image para tudo pode render menos nota que implementar as etapas-chave.
- **Escopo**: rastrear N vermes com identidade perfeita após colisões é problema de pesquisa. Definir como meta "ID correto exceto durante colisões, com recuperação posterior" é realista.

### 3.7 Ambiente

Instalado nesta máquina: Python com `numpy`, `scipy`, `matplotlib`, `pillow`. **Não instalados**: `opencv-python`, `scikit-image`. Para ler/escrever vídeo, `opencv-python` ou `imageio[ffmpeg]` resolve (`pip install`). A demo ao vivo pode ser um script que lê um vídeo, mostra as etapas lado a lado e gera o vídeo com IDs e rastros.

---

## 4. Níveis de ambição (escolher um)

| Nível | Conteúdo | Risco |
|---|---|---|
| **Mínimo viável** | Fundo por mediana + Otsu + morfologia + rotulagem + associação por vizinho mais próximo; vermes separados só quando não se tocam | Baixo |
| **Recomendado** | Mínimo + húngaro com predição + separação de aglomerados por distância/watershed + esqueleto + métricas de movimento + avaliação com vídeo sintético e BBBC010 | Médio |
| **Ambicioso** | Recomendado + Kalman + resolução de identidade pós-colisão por forma/histórico + análise de postura/ondulação em frequência | Alto |

---

## 5. Cronograma sugerido (hoje: 31.out; primeira data de apresentação: 24.nov)

1. **Já**: reservar tema e data nas planilhas; decidir dupla ou individual.
2. **Semana 1 (até ~07.nov)**: conseguir/gerar dados; baseline Otsu + morfologia + rotulagem; vídeo sintético com gabarito.
3. **Semana 2 (até ~14.nov)**: rastreamento (húngaro), métricas, separação de aglomerados.
4. **Semana 3 (até ~21.nov)**: avaliação quantitativa, ablações, figuras de cada etapa, script de demo estável (testar com vídeo que nunca viu).
5. **Apresentação**: ensaiar para caber em 18 min (sugestão: ~10 min slides + ~5 min demo + folga). Slides feitos por você, com figuras das etapas.
6. **Relatório (4 páginas)** e `.zip` público (conferir o link em janela anônima). Se apresentar em 24.nov ou 01.dez, o relatório pode ir até 08.dez.

## 6. Estrutura de pasta sugerida para a entrega

```
projeto_celegans/
  README.md            # instruções de uso (instalar, rodar demo)
  src/                 # preprocess.py, segment.py, separate.py, track.py, metrics.py, demo.py
  data/                # vídeos/imagens de teste (leves)
  results/             # figuras por etapa, vídeo com trajetórias, tabelas de métricas
  relatorio.pdf
  slides.pdf
```

## 7. Próximos passos que posso fazer

- Gerar o simulador de vídeo sintético com gabarito.
- Implementar o baseline (fundo, Otsu, morfologia, rotulagem, húngaro) e rodar nas imagens.
- Montar o esqueleto do relatório no modelo LaTeX/docx (quando você tiver o modelo do post).
