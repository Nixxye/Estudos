"""U-Net pequena para segmentar vermes (fundo vs verme)."""
import torch
import torch.nn as nn
import torch.nn.functional as F


def block(i, o):
    return nn.Sequential(
        nn.Conv2d(i, o, 3, padding=1), nn.BatchNorm2d(o), nn.ReLU(inplace=True),
        nn.Conv2d(o, o, 3, padding=1), nn.BatchNorm2d(o), nn.ReLU(inplace=True),
    )


class UNet(nn.Module):
    def __init__(self, c=(16, 32, 64, 128)):
        super().__init__()
        self.enc = nn.ModuleList([block(1, c[0]), block(c[0], c[1]), block(c[1], c[2])])
        self.mid = block(c[2], c[3])
        self.up = nn.ModuleList([nn.ConvTranspose2d(c[3], c[2], 2, 2), nn.ConvTranspose2d(c[2], c[1], 2, 2),
                                 nn.ConvTranspose2d(c[1], c[0], 2, 2)])
        self.dec = nn.ModuleList([block(c[2] * 2, c[2]), block(c[1] * 2, c[1]), block(c[0] * 2, c[0])])
        self.out = nn.Conv2d(c[0], 1, 1)

    def forward(self, x):
        skips = []
        for e in self.enc:
            x = e(x)
            skips.append(x)
            x = F.max_pool2d(x, 2)
        x = self.mid(x)
        for up, dec, s in zip(self.up, self.dec, reversed(skips)):
            x = dec(torch.cat([up(x), s], 1))
        return self.out(x)  # logits


def to_tensor(gray_u8, device):
    return (torch.from_numpy(gray_u8).float().div(255).sub(0.58).div(0.2))[None, None].to(device)
