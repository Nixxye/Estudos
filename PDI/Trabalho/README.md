# Teste rápido: PDI vs CNN em vídeo de C. elegans (CSB-1)

Ambiente (já criado em `.venv`): torch (cu128), opencv-python, scipy, numpy, pillow.

```
cd src
..\.venv\Scripts\python train_cnn.py 3000   # treina a U-Net (~3 min na RTX 5070 Ti) -> cache/unet.pt
..\.venv\Scripts\python player.py           # abre o player (sequência de teste 24_2_1_1)
..\.venv\Scripts\python player.py 24_0_1_1 8   # outra sequência, 8 fps
```

Teclas do player: espaço pausa/continua, `d` próximo quadro, `a` anterior, `w`/`s` ±25 quadros, `+`/`-` velocidade, `t` mostra/esconde as trilhas, `r` reinicia, `q` sai.

- `common.py`: dados, pós-processamento (abertura, rotulagem), rastreador (algoritmo húngaro), Dice.
- `pdi.py`: fundo por mediana temporal, gaussiano, Otsu.
- `cnn.py` / `train_cnn.py`: U-Net pequena treinada nas 9 sequências de treino; a sequência `24_2_1_1` fica só para teste.
- `player.py`: os 3 painéis (original | PDI | CNN) com contorno, ID e trajetória.
