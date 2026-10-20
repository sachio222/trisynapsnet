"""Occlusion and noise for test drawings, as in AHA's robustness tests.

AHA's paper (Kowadlo, Ahmed and Rawlinson, arXiv 1909.10340v5, Section
3.2) corrupts drawings two ways:

    occlusion   "randomly placed circles, completely contained within the
                image", sized as "diameter as a fraction of image side
                length".
    noise       "replacing a proportion of the pixels with a random
                intensity value drawn from a uniform distribution", sized
                as "a fraction of image area".

Choices where the paper is silent, all listed in docs/e1b_protocol.md:

  * One circle per drawing. The paper's Figure 7b caption reads "With
    occlusion (circle, diameter=0.3)".
  * The circle is painted with paper, intensity 0 once ink is 1, so it
    removes strokes. The paper says occlusion can remove "important
    topological features".
  * The circle's centre is uniform over every position that keeps the
    whole circle inside the frame. A pixel is covered when its centre lies
    inside the circle.
  * Noise replaces exactly round(fraction x pixels) pixels per drawing,
    picked without repeats, each with a new intensity uniform in [0, 1).
  * Corruption works on the 52 x 52 drawing the model sees, after
    resizing, inverting and centring.
  * Every drawing gets its own circle or pixels. The random draw comes
    from the corruption seed, the run number, the kind and the level
    alone, so the same call always gives the same drawings.
"""

import hashlib

import torch

KINDS = ("occlusion", "noise")

# None, then 10 steps to "almost complete corruption". The paper caps the
# top level "at just below 98% corruption" and shows 0.3, 0.6 and 0.9.
PAPER_LEVELS = (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.98)

# Paper intensity once drawings are inverted so ink is 1.
PAPER = 0.0


def generator(seed, run, kind, level):
    """A random generator fixed by the corruption seed, run, kind and level."""
    key = "{}:{:.6f}:{}:{}".format(kind, level, seed, run).encode()
    return torch.Generator().manual_seed(int(hashlib.sha256(key).hexdigest()[:15], 16))


def circle_masks(n, size, diameter, generator):
    """n boolean (size, size) masks, each one circle inside the frame.

    The diameter is a fraction of the side. The centre is uniform over all
    positions that keep the whole circle in the frame.
    """
    r = diameter * size / 2
    centres = r + torch.rand(n, 2, generator=generator) * (size - 2 * r)
    pixel = torch.arange(size, dtype=torch.float32) + 0.5
    dy = pixel[None, :, None] - centres[:, 0, None, None]
    dx = pixel[None, None, :] - centres[:, 1, None, None]
    return dy ** 2 + dx ** 2 <= r ** 2


def occlude(images, diameter, generator):
    """Paints one paper-coloured circle over each drawing in (N, 1, H, W)."""
    n, _, h, w = images.shape
    if h != w:
        raise ValueError("Occlusion expects square drawings")
    masks = circle_masks(n, h, diameter, generator)[:, None]
    return images.masked_fill(masks.to(images.device), PAPER)


def add_noise(images, fraction, generator):
    """Replaces round(fraction x pixels) pixels of each drawing with
    intensities uniform in [0, 1)."""
    n = images.shape[0]
    flat = images.reshape(n, -1).clone()
    count = round(fraction * flat.shape[1])
    for i in range(n):
        idx = torch.randperm(flat.shape[1], generator=generator)[:count]
        flat[i, idx.to(flat.device)] = torch.rand(count, generator=generator).to(flat)
    return flat.view_as(images)


def corrupt(images, kind, level, seed, run):
    """A corrupted copy of a batch of drawings. The input is never changed.

    Args:
        images: (N, 1, H, W) drawings, ink 1 and paper 0.
        kind: "occlusion" or "noise".
        level: circle diameter over the side, or share of pixels, in [0, 1).
        seed: the corruption seed.
        run: the run number, so each run gets its own draw.
    """
    if kind not in KINDS:
        raise ValueError("kind must be one of {}".format(KINDS))
    if not 0.0 <= level < 1.0:
        raise ValueError("level must be in [0, 1), got {}".format(level))
    if level == 0.0:
        return images.clone()
    g = generator(seed, run, kind, level)
    if kind == "occlusion":
        return occlude(images, level, g)
    return add_noise(images, level, g)
