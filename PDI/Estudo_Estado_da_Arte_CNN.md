# Estado da arte: identificar e rastrear *C. elegans* em vídeo (e plano com CNN)

Pesquisa feita em 31.out.2026 com buscas na web. Os resultados vêm de resumos de busca e de uma leitura do artigo WormSwin; **não li os demais artigos na íntegra**. Números marcados com (*) vêm de resumos e devem ser conferidos no artigo antes de citar no relatório.

---

## 1. Como o problema é resolvido hoje

### 1.1 Linha clássica (PDI + rastreamento): sem rede neural
Pipeline típico: subtração de fundo, limiar, morfologia, componentes conexos, esqueleto, associação quadro a quadro.

| Ferramenta | Ideia | Limite relatado |
|---|---|---|
| **Multi-Worm Tracker (MWT)**, Swierczek et al. 2011 | Rastreia muitos vermes em tempo real numa placa | Perde a identidade nas colisões; quanto mais animais, mais rápido isso ocorre |
| **WALDO** (Sci. Rep. 2016) | Repara trilhas quebradas por colisões e erros de subtração de fundo | Em teste com 10 vermes por 3 h, o MWT gerou 1.750 trilhas; WALDO reporta remover ~90% das interrupções (*) |
| **Tierpsy Tracker** | Esqueletização/postura de verme isolado em alta resolução | Falha em vermes enrolados e sobrepostos; é preciso só para vermes isolados (*) |
| Multi-tracker com esqueleto modificado (2021) e *network flow* com esqueleto (2024) | Segmentam vermes em contato por esqueletização e otimizam a identidade na colisão | Colisão é descrita como um dos maiores desafios; MOTA reportado entre 0,86 e 0,92 (*) |

Resumo: o que os slides da disciplina cobrem (Aula 08) é o núcleo dessas ferramentas. **O ponto fraco comum é o contato entre vermes.** Várias ferramentas simplesmente descartam o trecho em que vermes se tocam.

### 1.2 Linha com deep learning

| Trabalho | Abordagem | Observações |
|---|---|---|
| **WormSwin** (Sci. Rep. 2023) | Segmentação de instâncias: Hybrid Task Cascade com backbone Swin-L | Ver detalhes na seção 2 |
| **Deep-Worm-Tracker** | Detecção + StrongSORT para manter identidade | Afirma rastrear muitos organismos sobrepostos (*) |
| **WormYOLO** (Sci. Rep. 2025) | Detecção/segmentação baseada em YOLO para posturas sobrepostas | Ganho de 24,1% em mAP0.5:0.95 sobre Deep-Worm-Tracker no conjunto de acasalamento, muito sobreposto (*); falhas em cenas muito densas |
| **YOLOv8 + ByteTrack** (PLOS Comp. Biol. 2025) | Detecção com perda modificada para vermes pequenos e sobrepostos + rastreador | Reporta robustez a oclusão (*) |
| **Deep-Pose-Tracker** | Pose multi-verme com ByteTrack/Bot-SORT | Degrada sob oclusão severa ou aglomeração (*) |
| **DeepTangle / DeepTangleCrawl** | Caixas para muitos vermes; splines da linha central para o verme isolado, permitindo detectar durante auto-sobreposição | Trilhas mais longas e com menos lacunas que o Tierpsy; usou dados do Tierpsy + anotação manual dos casos difíceis (*) |
| **Bilayer Segmentation-Recombination Network** (arXiv 2024) | Segmenta vermes sobrepostos em duas camadas e recombina | Argumenta que a maioria dos trabalhos ignora as regiões ocluídas |
| Omnipose | Feito para bactérias; testado em vermes | Limite com sobreposição em imagem 2D (*) |

Padrão: detecção/segmentação por rede **mais** um rastreador genérico de visão computacional (SORT, ByteTrack, StrongSORT), em vez de lógica específica de verme.

---

## 2. Detalhes do WormSwin (leitura do artigo)
Fonte: [WormSwin, Sci. Rep. 2023 (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10328995/).

- **Dados**: CSB-1 (56 vídeos de ~1,5 min, 912×736, dos quais **10 anotados**, >60.500 máscaras de verme); **sintético** (10.000 imagens de treino e 1.000 de teste; vermes recortados do CSB-1 colados em fundos, 20% sobrepostos); BBBC010 (50 imagens para ajuste fino); conjunto de acasalamento (1 vídeo de 10 min, 50 quadros anotados, >3.900 posturas).
- **Modelo**: HTC com Swin-L (ImageNet-21K). Treino em 4× V100 32 GB, ~19 h, 36 épocas.
- **Resultados**: no CSB-1, AP0.50 = 0,990, mas mAP@0.5:0.95 de máscara = 0,585. Em vermes sobrepostos, AP0.50 = 0,975 e mAP de máscara 0,527. No BBBC010, mAP de máscara 0,622; sob a métrica DSB, 0,536 contra 0,727 do PatchPerPix.
- **Limitações declaradas**: bordas imprecisas (para um verme de ~500 px, erro de borda chega a ~30% dos pixels); AP cai em IoU alto; **sem ajuste fino generaliza mal** (BBBC010); o rastreamento é só uma heurística de IoU; **informação temporal** é apontada como o principal avanço futuro para sobreposição.

Lição prática: acertar *onde há um verme* é fácil (AP0.50 ~0,99); o difícil é a **máscara precisa e a separação na sobreposição**.

---

## 3. Problemas e limitações recorrentes (resumo)

1. **Sobreposição/contato**: o maior problema, na linha clássica e na de DL.
2. **Enrolamento e auto-sobreposição**: o verme vira um blob compacto sem esqueleto bem definido.
3. **Anotação cara**: máscara por verme em cenas densas; trabalhos usam anotação parcial (10 de 56 vídeos), imagens sintéticas ou dados do Tierpsy + correção manual.
4. **Generalização entre laboratórios**: mudança de câmera, iluminação, resolução, idade do verme e tipo de placa derruba o desempenho; ajuste fino com poucas imagens é recomendado.
5. **Precisão da borda** versus detecção: bom AP0.50, mas mAP em IoU alto bem menor.
6. **Rastreamento genérico perde identidade** em colisões; trabalhos futuros apontam o uso de informação temporal e forma.
7. **Poucos conjuntos públicos totalmente anotados** (relatado em um dos artigos).
8. **Custo computacional**: modelos grandes (Swin-L, 4 GPUs) não são viáveis para uso em laboratório simples; YOLO é bem mais leve.
9. **Métricas inconsistentes** entre artigos (DSB vs. COCO), o que dificulta comparar números.

---

## 4. Conjuntos de dados e recursos a verificar

| Recurso | O que é | Status |
|---|---|---|
| **BBBC010** | 100 imagens de campo claro (e 100 GFP, conforme WormSwin) de vermes vivos/mortos, uma máscara por verme | Confirmado nas buscas; é imagem estática, não vídeo |
| **Dados do WormSwin** (CSB-1 anotado, sintético, acasalamento) | Vídeos e máscaras | Há repositório ([bozeklab/worm-swin](https://github.com/bozeklab/worm-swin)) e registros no Zenodo; **verificar o que está público e a licença** |
| Pesos pré-treinados do WormSwin | Treino em sintético servindo de pré-treino | Citado no Zenodo (*) |
| **Tierpsy / Open Worm Movement Database** | Vídeos de verme isolado | Útil para esqueleto/postura, pouco para multi-verme |
| **Vídeo próprio** | Lupa + câmera, se houver acesso | Melhor para a demo e para testar generalização |

---

## 5. Como usar CNN, e como unir PDI e Deep Learning

### 5.1 Opções de modelo (do mais simples ao mais complexo)

| # | Abordagem | Saída | Prós | Contras |
|---|---|---|---|---|
| A | **U-Net** de segmentação semântica (verme vs. fundo) + separação clássica (rotulagem, distância/watershed, esqueleto) | Máscara binária | Simples, treina com poucas imagens, mantém PDI no pipeline (bom para a disciplina) | Não separa vermes encostados sozinha |
| B | U-Net com 2–3 classes (fundo / corpo / **fronteira ou cruzamento**) | Máscara com contornos | Ajuda a separar contatos, como se faz em núcleos celulares | Precisa de rótulos de fronteira |
| C | **YOLOv8-seg** (instâncias) + **ByteTrack** | Máscara e ID por verme | Pipeline de ponta a ponta, rápido, rastreamento pronto | Sobreposição forte continua difícil; menos "PDI próprio" |
| D | **YOLO-pose** ou rede de keypoints/linha central (estilo DeepTangle) | Esqueleto por verme | Resolve oclusão melhor; dá postura | Anotação de keypoints é trabalhosa |
| E | Segmentação de instâncias com ViT (estilo WormSwin) | Máscaras por instância | Estado da arte | Pesado, exige GPU grande |
| F | Modelo com **entrada temporal** (vários quadros, ou propagação da máscara anterior) | Instâncias consistentes no tempo | Ataca o problema principal | Mais complexo, pouca prática pronta |

### 5.2 Divisão sugerida entre os dois trabalhos

**PDI (nov/dez 2026): mais simples, sem treino pesado**
- Pipeline clássico: fundo, Otsu/adaptativo, morfologia, rotulagem, esqueleto, húngaro.
- Avaliar com vídeo sintético + BBBC010.
- *Opcional e barato*: uma **U-Net pequena (opção A)** treinada em imagens sintéticas/BBBC010, usada só para gerar a máscara em lugar do limiar. Comparar "Otsu vs. U-Net" fica como um resultado forte no relatório, sem tomar o tempo do projeto. Só inclua se o baseline clássico estiver pronto.

**Deep Learning (fev/2027): projeto completo**
- Reaproveitar do PDI: gerador de vídeo sintético com gabarito, código de avaliação, rastreador, métricas de movimento.
- Treinar e comparar **A/B (U-Net) vs. C (YOLOv8-seg + ByteTrack)**; se der tempo, **F** (informação temporal) como contribuição própria.
- Usar o baseline clássico do PDI como **linha de base** do trabalho de DL (comparação honesta: onde a rede ganha? só nos contatos?).
- Pergunta de pesquisa sugerida: *"Quanto uma CNN melhora a separação de vermes em contato e a preservação de ID, em comparação com o pipeline clássico?"*

Isso evita duplicar trabalho: o PDI entrega o baseline e o gerador de dados, e o DL entrega a rede e a análise.

### 5.3 Dados e treino
- **Sintético com gabarito perfeito** (recortar vermes de imagens reais e colar sobre fundos com sobreposição controlada, como no WormSwin; ou simular vermes por curvas deformáveis). Cuidado com a diferença entre sintético e real (*domain gap*): medir sempre em dados reais.
- **Aumento de dados**: rotação, espelho, brilho/contraste (Aulas 03/10), ruído, desfoque.
- **Perdas** para segmentação com classe rara: Dice, BCE ponderada.
- **Métricas**: IoU/Dice por pixel; AP (COCO) por instância; para rastreamento, trocas de ID e MOTA/IDF1.
- **Hardware**: verificar se há GPU local (não consultei). Sem GPU, usar Google Colab/Kaggle; U-Net pequena e YOLOv8n/s treinam bem nesses ambientes.

### 5.4 Riscos
- Poucos dados reais anotados: anotar 20–50 quadros bem escolhidos (incluindo contatos) já ajuda; ferramentas de rotulagem semi-automática reduzem o custo.
- Sintético demais: a rede acerta no sintético e falha no real. Misturar ou fazer ajuste fino com poucas imagens reais.
- Comparar com métricas diferentes das dos artigos: declarar qual métrica usou.
- Escopo do DL: rastrear com identidade perfeita em colisão é pesquisa aberta; definir meta realista (por exemplo, menos trocas de ID que o baseline clássico).

---

## 6. Perguntas em aberto (para decidir depois)
- Qual o formato do vídeo-alvo: campo claro ou fluorescência, resolução, taxa de quadros, quantos vermes?
- Há GPU disponível? Qual o limite de tempo de treino?
- Dá para obter vídeo real próprio ou só dados públicos?
- O professor de DL aceita reutilizar o pipeline do PDI como linha de base? (Vale combinar com ambos os professores, para não parecer duplicação de trabalho.)

---

## Fontes
- [WormSwin: instance segmentation of *C. elegans* using vision transformer (Sci. Rep. 2023)](https://www.nature.com/articles/s41598-023-38213-7), lido via [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10328995/)
- [WormYOLO / segmentação de posturas complexas e fenotipagem (Sci. Rep. 2025)](https://www.nature.com/articles/s41598-025-93533-0)
- [Deep-Worm-Tracker (preprint)](https://www.researchgate.net/publication/362824173_Deep-Worm-Tracker_Deep_Learning_Methods_for_Accurate_Detection_and_Tracking_for_Behavioral_Studies_in_C_elegans)
- [Deep-Pose-Tracker (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC13545221/)
- [Automated *C. elegans* behavior analysis via deep learning-based detection and tracking (PLOS Comp. Biol.)](https://journals.plos.org/ploscompbiol/article?id=10.1371%2Fjournal.pcbi.1013707)
- [Bilayer Segmentation-Recombination Network (arXiv 2411.17557)](https://arxiv.org/pdf/2411.17557)
- [Modelo de rede neural para rastreamento em condições difíceis (DeepTangleCrawl, PMC)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12360645/)
- [Multi-Tracker com esqueleto modificado (PMC, 2021)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8402443/)
- [Network flow + esqueleto para múltiplos vermes (PMC, 2024)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11821056/)
- [WALDO (Sci. Rep. 2016)](https://link.springer.com/article/10.1038/srep34859)
- [Multi-Worm Tracker (Swierczek et al., PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3128206)
- [PatchPerPix (arXiv 2001.07626)](https://arxiv.org/pdf/2001.07626)
- [Código do WormSwin](https://github.com/bozeklab/worm-swin)
