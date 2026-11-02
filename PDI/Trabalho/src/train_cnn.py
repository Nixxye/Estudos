"""Treina a U-Net no CSB-1 (todas as sequencias, exceto a de teste)."""
import os
import sys
import time

import numpy as np
import torch
import torch.nn.functional as F

import common as C
from cnn import UNet, to_tensor

STEP = 3          # usa 1 a cada 3 quadros (quadros vizinhos sao quase identicos)
ITERS = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
CROP, BATCH = 256, 16
dev = "cuda"


def build_cache():
    path = os.path.join(C.CACHE, "train.npz")
    if os.path.exists(path):
        d = np.load(path)
        return d["x"], d["y"]
    os.makedirs(C.CACHE, exist_ok=True)
    xs, ys = [], []
    for s in C.sequences():
        if s == C.TEST_SEQ:
            continue
        for k in range(0, C.n_frames(s), STEP):
            g = C.load_gt(s, k)
            if g is None:
                continue
            xs.append(C.load_frame(s, k)); ys.append(g)
        print("cache", s, len(xs), flush=True)
    x, y = np.stack(xs), np.stack(ys)
    np.savez(path, x=x, y=y)
    return x, y


def batch(x, y):
    xb, yb = [], []
    for _ in range(BATCH):
        i = np.random.randint(len(x))
        H, W = x[i].shape
        if np.random.rand() < 0.8 and y[i].any():      # centra num pixel de verme
            ys_, xs_ = np.nonzero(y[i]); j = np.random.randint(len(ys_))
            r = np.clip(ys_[j] - CROP // 2 + np.random.randint(-80, 80), 0, H - CROP)
            c = np.clip(xs_[j] - CROP // 2 + np.random.randint(-80, 80), 0, W - CROP)
        else:
            r, c = np.random.randint(0, H - CROP), np.random.randint(0, W - CROP)
        a, b = x[i][r:r + CROP, c:c + CROP], y[i][r:r + CROP, c:c + CROP]
        k = np.random.randint(4); a, b = np.rot90(a, k), np.rot90(b, k)
        if np.random.rand() < .5: a, b = a[:, ::-1], b[:, ::-1]
        a = np.clip(a.astype(np.float32) * np.random.uniform(.85, 1.15) + np.random.uniform(-12, 12), 0, 255)
        xb.append((a / 255 - 0.58) / 0.2); yb.append(b.astype(np.float32))
    return (torch.from_numpy(np.stack(xb))[:, None].float().to(dev),
            torch.from_numpy(np.stack(yb))[:, None].to(dev))


def loss_fn(lo, y):
    p = torch.sigmoid(lo)
    dice = 1 - (2 * (p * y).sum() + 1) / (p.sum() + y.sum() + 1)
    return F.binary_cross_entropy_with_logits(lo, y, pos_weight=torch.tensor(5., device=dev)) + dice


if __name__ == "__main__":
    x, y = build_cache()
    print("quadros de treino:", len(x), flush=True)
    net = UNet().to(dev)
    opt = torch.optim.AdamW(net.parameters(), 2e-3, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, 2e-3, total_steps=ITERS)
    t0, run = time.time(), 0
    for it in range(1, ITERS + 1):
        xb, yb = batch(x, y)
        with torch.autocast("cuda", dtype=torch.bfloat16):
            lo = net(xb)
        l = loss_fn(lo.float(), yb)
        opt.zero_grad(); l.backward(); opt.step(); sched.step()
        run = 0.98 * run + 0.02 * l.item() if run else l.item()
        if it % 200 == 0:
            print(f"it {it}/{ITERS} loss {run:.3f} ({time.time() - t0:.0f}s)", flush=True)
    os.makedirs(C.CACHE, exist_ok=True)
    torch.save(net.state_dict(), os.path.join(C.CACHE, "unet.pt"))
    print("modelo salvo", flush=True)
