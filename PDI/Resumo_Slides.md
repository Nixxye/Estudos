# Resumo dos slides — Processamento Digital de Imagens (IF69D / OPEET014)

UTFPR Curitiba, Profs. Gamba e Borba, 2026/2. Os slides usam **MATLAB** (Image Processing Toolbox); abaixo vai o equivalente em Python quando útil para o projeto.

> Como usar: um bloco por aula, mais o campo "Relevância p/ C. elegans". Para acrescentar aulas novas, copie o **modelo no fim do arquivo** e cole acima da seção "Aulas futuras".
> Fonte: texto extraído dos PDFs em `Slides/`. As partes só em figura/fórmula (e as anotações manuscritas) podem não aparecer aqui. Os arquivos NAP (notas de prática MATLAB) não foram resumidos em detalhe, só listados.

---

## Índice

| Aula | Data | Tema | Arquivo |
|---|---|---|---|
| 01a | 18.ago | Onde PDI está hoje; história (raios-X, tomografia, TV) | `Aula_01a_...` |
| 01b | 18.ago | Sensores CMOS/Bayer, lentes, tipos de imagem | `Aula_01b_...` |
| 01c | 25.ago | Matriz imagem, vizinhança, distâncias, operações | `..._01c_...` |
| 02 | — | (só há o NAP_02; slides não estão na pasta) | `NAP_02` |
| 03 | 01.set | Transformações ponto-a-ponto e histograma | `..._Aula 03_...` |
| 04 | 15.set | Vizinhança: correlação, convolução, filtros lineares | `..._04_...` |
| 05 | 22.set | Filtros adaptativos (bilateral) e métricas de qualidade | `..._05_...` |
| 06 | 29.set | Detecção de bordas e transformada de Hough | `..._06_Parte_1/2` |
| 07 | 06.out | Domínio da frequência (Fourier) | `..._07_...` |
| 08 | 13.out | Segmentação: limiar, morfologia, esqueleto, rotulagem | `..._08_...` |
| 09a | 20.out | Imagens coloridas: fundamentos de cor e visão | `..._09a_...` |
| 10 | 27.out | Processamento de imagens coloridas | `..._10_...` |
| NAP 02–08 | — | Notas de aula e prática MATLAB | `*_NAP_*` |

---

## Aula 01a — Onde PDI está hoje
- Aplicações: Indústria 4.0 (inspeção de qualidade, classificação de frutas), satélites (Sentinel-2, 13 bandas), medicina, IA.
- Cadeia de visão computacional: cena → câmera → imagem → processamento → decisão.
- **Processamento de imagens** (imagem → imagem/características) vs. **visão computacional** (imagem → informação/decisão).
- PDI como pré-processamento para IA; três tarefas: **classificação** (o que há), **detecção** (o que e onde), **segmentação** (quais pixels de cada objeto).
- História: raios-X (Röntgen, 1895), limites da radiografia projetiva (soma de atenuações), tomografia (Radon 1917, Bracewell, Oldendorf, Hounsfield/Cormack, 1971), TV analógica → digital.
- **Relevância p/ C. elegans:** a divisão classificação/detecção/segmentação é exatamente o vocabulário da parte de CNN (ver estudo).

## Aula 01b — Aquisição
- Sensor CMOS, filtro de Bayer e demosaicing; importância da lente.
- Cálculo de distância focal a partir de campo de visão, distância de trabalho e tamanho do sensor (exemplo: FOV 16 cm, 40 cm, sensor 1/3").
- Tipos de imagem (binária, cinza, indexada, RGB); sistema de coordenadas; `imread`, `imshow`.
- **Relevância:** escolha de lente/resolução para ver o verme (~1 mm) com pixels suficientes; iluminação e compressão do vídeo afetam o ruído.

## Aula 01c — Matriz imagem e operações básicas
- Imagem como matriz (cinza, BW, RGB); acesso por índices.
- **Vizinhança**: 4, diagonal, 8 (3×3).
- **Distâncias**: euclidiana, city-block (D4), chessboard (D8); `bwdist` calcula a distância de cada pixel ao objeto mais próximo.
- Tipos de operação: pontuais, por vizinhança, globais, entre imagens. Autocontraste.
- **Relevância:** vizinhança-8 define conectividade na rotulagem; `bwdist` = transformada de distância (base do watershed).

## Aula 03 — Transformações ponto-a-ponto
- Linear `s = c·r + b` (c = contraste, b = brilho), **sigmoide**, **piecewise**, **gamma** `s = c·r^γ`, **logarítmica**, autocontraste (com saturação de 0,5–1%, `stretchlim`/`imadjust`).
- **Histograma** como distribuição de intensidades; contraste = espalhamento dos níveis.
- **Relevância:** normalizar contraste do vídeo antes de limiarizar; gamma para realçar vermes finos/translúcidos.

## Aula 04 — Processamento por vizinhança
- **Correlação** (kernel não invertido) vs. **convolução** (kernel invertido); `imfilter` usa correlação por padrão.
- Linearidade (aditividade + homogeneidade), invariância ao deslocamento (LSI).
- Passa-baixas: **média (box)** e **gaussiano** `h = exp(-(x²+y²)/2σ²)/2πσ²`, normalizado (ganho DC = 1). Tamanho do kernel ≈ `2·ceil(3σ)+1`. `imgaussfilt`.
- Passa-altas: **Laplaciano** (soma dos coeficientes = 0, amplifica ruído), **sharpening** `g = f − c·∇²f`, **unsharp masking** (original − suavizada).
- **Relevância:** gaussiano antes da limiarização reduz ruído/granulação do ágar.

## Aula 05 — Filtros adaptativos e qualidade
- Separabilidade de filtros lineares (menos custo).
- **Filtro bilateral**: peso = gaussiana espacial × gaussiana de intensidade; preserva bordas; não é LSI. σ_r pequeno preserva bordas, grande suaviza mais. `imbilatfilt`.
- Métricas: **MSE, PSNR, SSIM** (referência completa), **SNRL** (sem referência).
- **Relevância:** bilateral limpa o fundo sem borrar o contorno do verme; PSNR/SSIM para comparar pré-processamentos (e, no DL, comparar saídas).

## Aula 06 — Bordas e Hough
- Três níveis de processamento: **baixo** (imagem→imagem), **médio** (extração de atributos: bordas, regiões), **alto** (interpretação).
- Bordas = descontinuidades de intensidade. **Gradiente** (1ª derivada): diferença entre vizinhos, diferença central, máscaras horizontal/vertical, magnitude e direção; Sobel é o mais usado (Kirsch/compass é parecido).
- **2ª derivada**: Laplaciano, passagem por zero, **LoG** (suavização + Laplaciano), DoG aproxima o LoG.
- **Canny**: suavização, magnitude/direção do gradiente, supressão de não-máximos, limiarização com histerese.
- **Hough**: cada pixel branco vota numa curva no espaço (ρ, θ), `ρ = x cosθ + y sinθ`; picos = retas (`hough`, `houghpeaks`, `houghlines`).
- **Relevância:** Canny para contornos dos vermes; Hough pouco útil (vermes não são retos), mas a ideia de acumulador aparece em outros métodos.

## Aula 07 — Domínio da frequência
- FT mostra que frequências existem e quanto contribuem. Baixa frequência = iluminação suave; alta = bordas/textura.
- DFT 1D passo a passo (fasor, partes real e imaginária), significado do índice u, frequência de Nyquist, frequências negativas, `fftshift`; DFT 2D por linhas e depois colunas.
- Aplicações: filtragem passa-baixa/alta, **high-boost**, **filtro homomórfico** (corrige iluminação).
- **Relevância:** homomórfico/passa-alta para iluminação desigual da placa; FT da curvatura ao longo do tempo para achar a **frequência de ondulação** do verme.

## Aula 08 — Segmentação (a mais central para o projeto)
- Objetivo: separar objetos do fundo **e entre si** (exemplos: núcleos celulares, pílulas).
- **Limiar global** e **Otsu** (minimiza a variância intra-classe; `graythresh`/`imbinarize`).
- **Limiar adaptativo**: `T(x,y) ≈ μ(x,y)(1−k)`, `adaptthresh`; para iluminação não uniforme.
- **Morfologia binária**: elemento estruturante; **dilatação**, **erosão**, **abertura** (remove ruído sem crescer), **fechamento** (liga e preenche), open-close filter; tamanho do SE controla a intensidade.
- **Esqueletização**: por erosões/aberturas sucessivas (preserva espessura, não garante conectividade) ou por **afinamento** (`bwmorph(A,'skel',Inf)`, preserva conectividade, sensível a ruído).
- **Rotulagem (labeling)**: algoritmo union-find em duas passadas (propaga o menor rótulo, resolve colisões na 2ª passada).
- **Top-hat** em tons de cinza para uniformizar o fundo. Pipeline do slide: **Imagem → Top-hat → Limiarização → Morfologia → Labeling**.
- **Relevância:** esta aula é praticamente o baseline do projeto; esqueleto dá comprimento e postura do verme.

## Aula 09a — Imagens coloridas: fundamentos
- Newton (1672): o prisma decompõe a luz, não a cria. Distribuição espectral de potência (SPD); cor depende de luz, objeto e observador (fenômeno psicofísico).
- Teoria tricromática (Young–Helmholtz, Maxwell); cones S/M/L e bastonetes; cor = resposta relativa dos cones.
- (Parte final da aula, com modelos de cor e CIE, pode ter ficado em figuras; conferir no PDF.)
- **Relevância:** baixa para campo claro em tons de cinza; alta se o vídeo for colorido ou com fluorescência (GFP).

## Aula 10 — Processamento de imagens coloridas
- RGB → cinza: `gray = 0.299R + 0.587G + 0.114B`; modelos YUV/YIQ/YCbCr.
- **RGB → HSV** (H como ângulo, S, V = max(R,G,B)); V não é luminância.
- Realce de contraste colorido: equalizar RGB por canal muda as cores; equalizar **só V (HSV)** ou **só Y (YIQ)** preserva matiz e saturação. Medição: mudança média de matiz em graus nas regiões com S > 15%.
- sRGB é não linear; cuidado com RGB linear.
- **Relevância:** escolher o canal de melhor contraste do verme; HSV para segmentar por cor.

## NAP 02–08 (notas de aula e prática MATLAB)
Roteiros de laboratório que acompanham cada aula (arquivos de apoio como `whitecells4.png`, `rice.png`, scripts `.m`). Não resumidos aqui; boa fonte de exercícios de segmentação (NAP_08).

---

## Mapa rápido: técnica da disciplina → onde entra no projeto

| Técnica | Aula | Uso no projeto |
|---|---|---|
| Gaussiano, bilateral | 04, 05 | Suavizar sem apagar o contorno |
| Top-hat, homomórfico | 08, 07 | Corrigir iluminação |
| Otsu / adaptativo | 08 | Máscara de vermes |
| Abertura/fechamento | 08 | Limpar máscara |
| Rotulagem | 08 | Um rótulo por verme isolado |
| `bwdist`, esqueleto | 01c, 08 | Separar contatos, comprimento, postura |
| Canny/Sobel | 06 | Contornos |
| Fourier | 07 | Ondulação, filtros |
| PSNR/SSIM | 05 | Comparar pré-processamentos |

---

## Aulas futuras (espaço aberto)

<!-- Cole aqui as novas aulas, uma por bloco, acima do modelo. Atualize também o Índice no topo. -->

_(nenhuma aula adicionada ainda)_

### Modelo para nova aula

```markdown
## Aula XX — Título
- Data: dd.mês | Arquivo: `Slides/nome.pdf`
- Conceitos-chave:
  - ...
- Fórmulas/algoritmos:
  - ...
- Funções MATLAB / equivalente Python:
  - ...
- **Relevância p/ C. elegans:** ...
- Dúvidas / para revisar:
  - ...
```
