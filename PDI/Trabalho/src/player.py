"""Player ao vivo: original | PDI | CNN, lado a lado, processando quadro a quadro.

Uso:  python player.py [sequencia] [fps]
Teclas: espaco = pausa/continua | d / a = proximo / anterior (pausado) | w / s = +25 / -25 quadros
        + / - = velocidade | t = mostra/esconde trilhas | r = reinicia | q ou ESC = sai
"""
import os
import sys
import time

import cv2
import numpy as np
import torch

import common as C
import pdi
from cnn import UNet, to_tensor

SCALE = 0.7
COLORS = [(255, 80, 80), (80, 255, 80), (80, 160, 255), (255, 220, 60), (255, 80, 255), (60, 255, 255)]


def detect(lab):
    """Centroides e pontas (esqueleto) de cada componente."""
    n = int(lab.max())
    return C.centroids(lab, n), C.skeleton_ends(lab, n)


def overlay(frame, lab, tracker, det, show_trails=True):
    """Desenha contorno, ID e trajetoria completa (ponta do verme) sobre o quadro."""
    img = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
    cents, ends = det
    ids = tracker.update(cents, ends)
    cnts, _ = cv2.findContours((lab > 0).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(img, cnts, -1, (0, 255, 255), 1)
    if show_trails:
        paths = [(i, t["trail"]) for i, t in tracker.tracks.items()] + tracker.finished
        for tid, trail in paths:
            pts = np.array([[q[1], q[0]] for q in trail], np.int32)
            if len(pts) > 1:
                cv2.polylines(img, [pts], False, COLORS[tid % len(COLORS)], 1, cv2.LINE_AA)
    for j, c in enumerate(cents):
        tid = ids[j]
        head = tracker.tracks[tid]["trail"][-1]
        cv2.circle(img, (int(head[1]), int(head[0])), 4, COLORS[tid % len(COLORS)], -1)
        cv2.putText(img, str(tid), (int(c[1]) + 6, int(c[0]) - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    COLORS[tid % len(COLORS)], 2)
    return img, len(cents)


def panel(img, txt):
    img = cv2.resize(img, None, fx=SCALE, fy=SCALE, interpolation=cv2.INTER_AREA)
    cv2.rectangle(img, (0, 0), (img.shape[1], 26), (0, 0, 0), -1)
    cv2.putText(img, txt, (6, 19), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    return img


class App:
    def __init__(self, seq):
        self.seq, self.total = seq, C.n_frames(seq)
        self.dev = "cuda" if torch.cuda.is_available() else "cpu"
        self.net = UNet().to(self.dev)
        self.net.load_state_dict(torch.load(os.path.join(C.CACHE, "unet.pt"), map_location=self.dev))
        self.net.eval()
        self.bg = pdi.estimate_background(seq)
        self.cache = {}  # k -> (det_pdi, det_cnn): permite refazer as trilhas sem reprocessar
        self.show_trails = True
        self.reset()

    def reset(self):
        self.t_pdi, self.t_cnn = C.Tracker(), C.Tracker()

    def cnn_mask(self, frame):
        with torch.no_grad(), torch.autocast(self.dev, dtype=torch.bfloat16, enabled=self.dev == "cuda"):
            p = torch.sigmoid(self.net(to_tensor(frame, self.dev)).float())[0, 0].cpu().numpy()
        return p > 0.5

    def process(self, k, draw=True):
        """Roda PDI e CNN no quadro k e atualiza os rastreadores. Retorna a imagem composta."""
        if k in self.cache and not draw:
            dp, dc = self.cache[k]
            self.t_pdi.update(*dp); self.t_cnn.update(*dc)
            return None
        frame = C.load_frame(self.seq, k)
        lab_p, _ = C.clean_and_label(pdi.segment(frame, self.bg))
        lab_c, _ = C.clean_and_label(self.cnn_mask(frame))
        if k not in self.cache:
            self.cache[k] = (detect(lab_p), detect(lab_c))
        dp, dc = self.cache[k]
        if not draw:
            self.t_pdi.update(*dp); self.t_cnn.update(*dc)
            return None
        gt = C.load_gt(self.seq, k)
        ip, np_ = overlay(frame, lab_p, self.t_pdi, dp, self.show_trails)
        ic, nc = overlay(frame, lab_c, self.t_cnn, dc, self.show_trails)
        gp = "" if gt is None else f" | Dice {C.dice(lab_p > 0, gt):.2f}"
        gc = "" if gt is None else f" | Dice {C.dice(lab_c > 0, gt):.2f}"
        orig = panel(cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR), f"Original | quadro {k}/{self.total - 1}")
        return np.hstack([orig, panel(ip, f"PDI (Otsu+morfologia) | vermes {np_}" + gp),
                          panel(ic, f"CNN (U-Net) | vermes {nc}" + gc)])

    def seek(self, k):
        """Vai para o quadro k refazendo as trilhas desde o inicio (usa as deteccoes em cache)."""
        k = int(np.clip(k, 0, self.total - 1))
        self.reset()
        for j in range(k):
            self.process(j, draw=False)
        return k


def main():
    seq = sys.argv[1] if len(sys.argv) > 1 else C.TEST_SEQ
    fps = float(sys.argv[2]) if len(sys.argv) > 2 else 10.0
    app = App(seq)
    win = f"CSB-1 {seq} - original | PDI | CNN"
    cv2.namedWindow(win, cv2.WINDOW_AUTOSIZE)
    k, paused, render = 0, False, True
    while True:
        t0 = time.time()
        if render:
            cv2.imshow(win, app.process(k))
            render = False
        wait = 30 if paused else max(1, int(1000 / fps - (time.time() - t0) * 1000))
        key = cv2.waitKey(wait) & 0xFF
        if key in (ord("q"), 27) or cv2.getWindowProperty(win, cv2.WND_PROP_VISIBLE) < 1:
            break
        if key == ord(" "):
            paused = not paused
        elif key in (ord("+"), ord("=")):
            fps = min(60, fps * 1.5)
        elif key == ord("-"):
            fps = max(1, fps / 1.5)
        elif key == ord("t"):
            app.show_trails, render = not app.show_trails, True
        elif key == ord("r"):
            k, render = app.seek(0), True
        elif key == ord("d"):
            paused, k, render = True, min(k + 1, app.total - 1), True
        elif key in (ord("a"), ord("w"), ord("s")):
            paused = True
            k, render = app.seek(k + {ord("a"): -1, ord("w"): 25, ord("s"): -25}[key]), True
        elif not paused:
            k, render = k + 1, True
            if k >= app.total:
                k = app.seek(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
