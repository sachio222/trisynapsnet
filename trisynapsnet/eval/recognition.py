"""E8b: recall-based recognition, a CA3 sized by rat anatomy, and closer lures.

E8 gave the fully local hippocampus a test built like the Mnemonic
Similarity Task (Stark and colleagues 2013): it studies a list of drawings
once, then sees repeats, lures and foils and answers old, similar or new.
It never called a lure old. E8b changes three things, each for a reason in
the biology, and keeps every learning rule:

1. A second readout, R2, beside E8's comparator readout, R1. R1 compares the
   test drawing's EC code with the EC code CA1 returns. R2 reads CA3 alone:
   how strongly CA3's settled state holds itself up through its own
   recurrent synapses, the share of the active cells' potentiated recurrent
   input that comes from the other active cells. A state that is a stored
   memory gets all of its active cells' support from inside itself; a state
   that is not gets less. R2 never compares the state with a list of stored
   memories. The list-based overlap with the nearest stored pattern is
   written beside it, only as a check on what R2 tracks.
2. DG, CA3 and CA1 at human proportions (15 million : 1.7 million : 16
   million cells; West and Gundersen 1990, Watson and colleagues 2025),
   scaled down together. EC stays the vision network's 20,449 units: at
   human proportions EC would need about 30 times fewer cells than CA1, and
   no size that fits in memory keeps it. DG is now larger than CA3, so DG's
   pattern reaches CA3 through mossy fibres: each CA3 cell gets 280 DG
   inputs (human, derived by Watson and colleagues 2025), each with its own
   fixed positive weight, and the 2% most driven CA3 cells form the stored
   pattern.
3. A second lure set: the studied drawing itself, distorted by a small
   random affine change and a smooth elastic displacement, at five levels
   whose vision-code similarity spans the range between E8's closest lures
   and an exact repeat. The levels are set on background alphabets
   (`levels`).

Commands:
    python -m trisynapsnet.eval.recognition probe --denominators 100 50
    python -m trisynapsnet.eval.recognition levels
    python -m trisynapsnet.eval.recognition run --split background --load 128

Results go to results/e8b_*.json; scripts/make_e8b_table.py scores them.
"""

import argparse
import hashlib
import json
import math
import platform
import resource
import subprocess
import sys
import time
from pathlib import Path

import torch
import torch.nn.functional as F

from trisynapsnet.data import omniglot
from trisynapsnet.eval import behaviour as bh
from trisynapsnet.eval import ca1space, ca3space
from trisynapsnet.model import modules

REPO = bh.REPO
RESULTS = REPO / "results"

# Human cell counts: DG granule cells and CA1 pyramidal cells (West and
# Gundersen 1990), CA3 pyramidal cells without CA2 (Watson and colleagues
# 2025). The model keeps their proportions.
HUMAN_CELLS = {"dg": 15_000_000, "ca3": 1_700_000, "ca1": 16_000_000}
# Rat counts (Arellano and Rakic 2026), for reference and checks only.
RAT_CELLS = {"dg": 1_000_000, "ca3": 210_000, "ca1": 350_000}
# DG inputs per human CA3 cell, about 280, derived by Watson and colleagues
# (2025). The count is kept at every scale: the human connection
# probability (280 of 15 million) would leave a scaled-down CA3 cell with
# less than one DG input.
MOSSY_IN_DEGREE = 280
# Share of DG and CA3 cells active for a drawing, E1d's default (rat DG, 2%).
ACTIVE_SHARE = 0.02
# Study-list length of the Mnemonic Similarity Task (Stark and colleagues
# 2013): 128 studied pictures, then 64 repeats, 64 lures and 64 foils.
HUMAN_LOAD = 128

SHARED_ARMS = ("intact", "no_recurrent", "no_ca3", "vc_baseline")
PP_KEEP = bh.PP_KEEP
STUDY_ARMS = ("no_dg",) + tuple("pp_keep{:g}".format(f) for f in PP_KEEP)
ARMS = SHARED_ARMS + STUDY_ARMS
CA3_ARMS = ("intact", "no_recurrent", "no_dg") + tuple("pp_keep{:g}".format(f) for f in PP_KEEP)
READOUTS = ("r1", "r2")
# Item types: 0 repeat, 1 lure (another person's drawing), 2 foil,
# 3 closer lure (the studied drawing, distorted).
TYPES = ("repeat", "lure", "foil", "close")
N_LEVELS = 5
STUDIED_PER_SEED = bh.STUDIED_PER_SEED
RESUME_KEYS = ("split", "load", "per_char", "lists", "arms", "first_seed", "denominator", "close")

# The distortion family for closer lures, at magnitude 1. One magnitude m
# scales every part; the five levels' magnitudes come from `levels`.
DISTORTION = {"rotation_deg": 15.0, "scale": 0.15, "shear": 0.15,
              "elastic_px": 2.0, "elastic_sigma_px": 4.0, "image_size": 52}


def derive(*parts):
    key = ":".join(str(p) for p in parts).encode()
    return int(hashlib.sha256(key).hexdigest()[:15], 16)


def half_up(x):
    return int(math.floor(x + 0.5))


# ---------------------------------------------------------------- the model

def scaled_model(denominator, cells=HUMAN_CELLS):
    """Every setting of the model at 1/denominator of the human DG, CA3 and CA1.

    Everything except the three sizes, the two active-cell counts and the
    mossy fibres is E3's model as E8 ran it (behaviour.MODEL).
    """
    dg = half_up(cells["dg"] / denominator)
    ca3 = half_up(cells["ca3"] / denominator)
    ca1 = half_up(cells["ca1"] / denominator)
    base = dict(bh.MODEL)
    for key in ("dg_units", "dg_k", "ca1_units"):
        base.pop(key)
    return {"denominator": denominator, "dg_units": dg, "dg_k": half_up(ACTIVE_SHARE * dg),
            "ca3_units": ca3, "ca3_k": half_up(ACTIVE_SHARE * ca3), "ca1_units": ca1,
            "mossy_in_degree": MOSSY_IN_DEGREE, **base}


class StreamDG():
    """DG as AHA builds it, made in blocks of cells from the seed and never kept.

    The same layer as modules.DG: every granule cell gets a fixed random
    weight from every EC unit, uniform in +-sqrt(6 / (EC units + cells))
    (Xavier), with a share `knockout` of them set to zero; the k most driven
    cells fire, and cells that just fired are inhibited for the next
    drawings (gamma). A block of weights is drawn from a generator fixed by
    (seed, first cell), used, and dropped, so a large DG costs no memory, as
    CA1BTSP does with its EC3 projection.
    """

    def __init__(self, in_dim, units, k, gamma=0.95, knockout=0.25, seed=0, block=512):
        self.in_dim, self.units, self.k = in_dim, units, k
        self.gamma, self.knockout, self.seed, self.block = gamma, knockout, seed, block
        self.bound = math.sqrt(6.0 / (in_dim + units))

    def weights(self, start, stop):
        # One uniform per synapse: below knockout the synapse is removed;
        # otherwise its rescaled value gives a weight uniform in +-bound.
        g = torch.Generator().manual_seed(derive("e8b dg", self.seed, start))
        u = torch.rand(stop - start, self.in_dim, generator=g)
        keep = u >= self.knockout
        W = ((u - self.knockout) / (1 - self.knockout) * 2 - 1) * self.bound
        return W * keep

    def drive(self, X):
        X = X.detach().float().cpu()
        out = torch.empty(X.shape[0], self.units)
        for start in range(0, self.units, self.block):
            stop = min(start + self.block, self.units)
            out[:, start:stop] = X @ self.weights(start, stop).T
        return out

    def __call__(self, X):
        Z = self.drive(X)
        phi = modules.InhibitionMask(self.units, self.gamma)
        out = torch.zeros_like(Z)
        for i in range(Z.shape[0]):
            s = modules.get_top_k(Z[i:i + 1] * phi(), self.k, "binary", 1, 1)
            phi.update(s)
            out[i] = s[0]
        return out


class MossyFibres():
    """Mossy fibres from DG granule cells to CA3 pyramidal cells.

    Each CA3 cell gets in_degree distinct DG inputs, chosen at random from
    the seed, each with its own fixed weight uniform in [0, 1). During
    study, the k CA3 cells with the most mossy drive from DG's pattern form
    the stored pattern (k-winners-take-all, the stand-in for feedback
    inhibition used everywhere in the model). The weights never change.
    """

    def __init__(self, n_dg, n_ca3, in_degree=MOSSY_IN_DEGREE, seed=0, block=256):
        if in_degree > n_dg:
            raise ValueError("in_degree exceeds the DG cells")
        self.n_dg, self.n_ca3, self.in_degree = n_dg, n_ca3, in_degree
        g = torch.Generator().manual_seed(derive("e8b mossy", seed))
        idx = []
        for start in range(0, n_ca3, block):
            rows = min(block, n_ca3 - start)
            idx.append(torch.rand(rows, n_dg, generator=g).topk(in_degree, dim=1).indices)
        self.idx = torch.cat(idx)
        self.w = torch.rand(n_ca3, in_degree, generator=g)

    def drive(self, D, block=64):
        """Summed mossy input to every CA3 cell, (drawings, n_ca3), a block
        of CA3 cells at a time."""
        D = (D.detach().cpu() > 0).float()
        out = torch.empty(D.shape[0], self.n_ca3)
        for start in range(0, self.n_ca3, block):
            stop = min(start + block, self.n_ca3)
            out[:, start:stop] = (D[:, self.idx[start:stop]] * self.w[start:stop]).sum(dim=2)
        return out

    def patterns(self, D, k):
        return modules.kwta(self.drive(D), k)


def wire_perforant(n, ec_dim, seed, share=modules.PP_SHARE, block=256):
    """PerforantPath's wiring for (n, ec_dim, seed), drawn in blocks of cells.

    Identical to modules.PerforantPath(ec_dim, n, ...)._wire(), which draws
    one (n, ec_dim) matrix of uniforms at once; a CPU generator gives the
    same numbers in blocks, and this keeps the memory small.
    """
    in_degree = min(ec_dim, max(1, half_up(share * ec_dim)))
    g = torch.Generator().manual_seed(derive("perforant", seed, "wiring"))
    C = torch.zeros(n, ec_dim, dtype=torch.bool)
    for start in range(0, n, block):
        stop = min(start + block, n)
        # The in_degree smallest uniforms: the same set argsort()[:, :in_degree] picks.
        idx = torch.rand(stop - start, ec_dim, generator=g).topk(in_degree, dim=1,
                                                                largest=False).indices
        C[start:stop].scatter_(1, idx, True)
    return C


class Perforant(modules.PerforantPath):
    """PerforantPath with clipped binary storage done in place: the same
    weights, with fewer full-size temporaries."""

    def store(self, E, Y):
        if self.rule != "willshaw":
            return super().store(E, Y)
        Y = (Y.detach().cpu() > 0).float()
        self.W.add_(Y.T @ self.active(E))
        self.W.mul_(self.C)
        self.W.clamp_(max=1.0)
        return self.W


class CA1Sparse(modules.CA1BTSP):
    """CA1BTSP with the same rule, drawing random numbers only where a synapse can change.

    Wu and Maass's Eq. 1 changes a synapse only if its CA1 cell has a
    plateau and its CA3 cell is active, and then with probability gate.
    CA1BTSP draws a gate for every synapse; this draws one for each synapse
    in the (plateau cells x active CA3 cells) block, which is the same rule
    with fewer draws. Weights stay zero outside the connection mask, so
    respond() skips the mask.
    """

    def btsp(self, x, plateau):
        rows = (plateau > 0).nonzero().flatten()
        cols = (x > 0).nonzero().flatten()
        if len(rows) == 0 or len(cols) == 0:
            return self.W
        r, c = rows[:, None], cols[None, :]
        eligible = self.C[r, c]
        if self.gate < 1:
            eligible &= torch.rand(len(rows), len(cols), generator=self.generator) < self.gate
        block = self.W[r, c]
        self.W[r, c] = torch.where(eligible, 1.0 - block, block)
        return self.W

    given_plateaus = None

    def plateaus(self, E):
        """The EC3 plateaus, or ones computed once for the same EC codes and
        handed in (every arm of a list shares CA1's EC3 projection)."""
        if self.given_plateaus is not None and self.given_plateaus.shape[0] == E.shape[0]:
            return self.given_plateaus
        return super().plateaus(E)

    def respond(self, X):
        X = (X.detach().cpu() > 0).float()
        h = X @ self.W.T
        jitter = 0.5 * torch.rand(h.shape, generator=self.generator)
        return modules.kwta(h + jitter, self.m)


def self_support(W, states):
    """R2's signal: the share of the active cells' recurrent input that comes
    from other active cells.

    W[i, j] is the synapse from CA3 cell i onto cell j (cell j's input is
    sum_i s_i W[i, j]). For each state, with A its active cells:
        sum over j in A of sum over i in A of W[i, j]
        ---------------------------------------------
        sum over j in A of sum over all i of W[i, j]
    1 when every potentiated synapse onto the active cells comes from inside
    the state; 0 when the active cells have no potentiated input at all.
    """
    A = (states > 0).float()
    within = ((A @ W) * A).sum(dim=1)
    total = (A * W.sum(dim=0)[None, :]).sum(dim=1)
    return torch.where(total > 0, within / total.clamp_min(1e-12), torch.zeros_like(total))


def nearest_overlap(states, stored):
    """Logged check only, never a decision: the largest share of a state's
    active cells shared with any one stored pattern (a list lookup)."""
    A = (states > 0).float()
    S = (stored > 0).float()
    on = A.sum(dim=1).clamp_min(1)
    return (A @ S.T).max(dim=1).values / on


def ca3_description(cue, final, stored, paired):
    """behaviour.ca3_description by overlap counts, without its
    (items x stored x cells) comparison: two 0/1 states are equal when
    their overlap equals both their sizes."""
    A, S = (final > 0).float(), (stored > 0).float()
    ov = A @ S.T
    same = (ov == A.sum(dim=1, keepdim=True)) & (ov == S.sum(dim=1)[None, :])
    exact_paired = torch.zeros(len(paired), dtype=torch.bool)
    has = paired >= 0
    exact_paired[has] = same[has, paired[has]]
    return {"cue_cells": (cue > 0).sum(dim=1).tolist(),
            "exact_paired": exact_paired.int().tolist(),
            "exact_any": same.any(dim=1).int().tolist()}


class Study():
    """What every arm of one list shares: DG's patterns, the mossy fibres'
    CA3 patterns and the perforant path's wiring."""

    def __init__(self, study_codes, seed, cfg):
        in_dim = study_codes.shape[1]
        self.study_codes = study_codes
        dg = StreamDG(in_dim, cfg["dg_units"], cfg["dg_k"], cfg["dg_gamma"], cfg["dg_knockout"],
                      seed=seed)
        self.dg_patterns = dg(study_codes)
        self.mossy = MossyFibres(cfg["dg_units"], cfg["ca3_units"], cfg["mossy_in_degree"], seed)
        self.ca3_patterns = self.mossy.patterns(self.dg_patterns, cfg["ca3_k"])
        self.C = wire_perforant(cfg["ca3_units"], in_dim, seed)
        self.plateaus = None
        self.test_plateaus = None

    def share_plateaus(self, test_codes, baseline, cfg, seed):
        """CA1's EC3 plateaus for the study and test codes, from one pass of
        the projection (every arm of a list has the same CA1 projection)."""
        ca1 = CA1Sparse(cfg["ca3_units"], self.study_codes.shape[1], cfg["ca1_units"],
                        cfg["ca1_plateau_share"], cfg["ca1_connect"], cfg["ca1_gate"], seed=seed,
                        ec3_baseline=baseline)
        both = ca1.plateaus(torch.cat([self.study_codes, test_codes.float()]))
        n = self.study_codes.shape[0]
        self.plateaus, self.test_plateaus = both[:n], both[n:]


class Memory():
    """One study list through the scaled hippocampus, with an optional lesion."""

    def __init__(self, study_codes, seed, baseline, cfg, shared, lesion=None):
        n, k, in_dim = cfg["ca3_units"], cfg["ca3_k"], study_codes.shape[1]
        self.cfg, self.seed, self.lesion, self.study_codes = cfg, seed, lesion, study_codes
        self.shared = shared
        C = shared.C
        if lesion is not None and lesion.startswith("pp_keep"):
            C = bh.thin(shared.C, float(lesion[len("pp_keep"):]), seed)
        self.pp = Perforant(in_dim, n, k, "willshaw", seed=seed,
                            presynaptic=cfg["pp_presynaptic"],
                            normalise=cfg["pp_normalise"], emax=cfg["pp_emax"],
                            connections=C)
        if lesion == "no_dg":
            stored = bh.pp_patterns(shared.C, study_codes, k)
        else:
            stored = shared.ca3_patterns
        self.stored = stored
        self.ca3 = modules.CA3(n, n_iter=cfg["ca3_iters"], k=k, start="cue")
        self.ca3.train(stored, "willshaw")
        self.pp.store(study_codes, stored)
        self.ca1 = CA1Sparse(n, in_dim, cfg["ca1_units"], cfg["ca1_plateau_share"],
                             cfg["ca1_connect"], cfg["ca1_gate"], seed=seed, ec3_baseline=baseline)
        if shared.plateaus is None:
            shared.plateaus = self.ca1.plateaus(study_codes)
        self.ca1.given_plateaus = shared.plateaus
        self.ca1.store(stored > 0, study_codes)
        self.ca1.given_plateaus = None
        self.ca1_state = self.ca1.generator.get_state()

    def returned(self, ca3_state):
        self.ca1.generator.set_state(self.ca1_state)
        return self.ca1(ca3_state)

    @torch.no_grad()
    def recall(self, codes, arms):
        """Both readouts' signals for each arm, and the CA3 description."""
        cue = self.pp.cue(codes)
        settled = self.ca3.update(cue)
        zeros = torch.zeros(codes.shape[0])
        sig = {"r1": {}, "r2": {}}
        ca3 = {}
        for arm in arms:
            if arm in ("intact", "no_dg") or arm.startswith("pp_keep"):
                sig["r1"][arm] = bh.cosine_rows(codes, self.returned(settled))
                sig["r2"][arm] = self_support(self.ca3.W, settled)
                state = (cue, settled)
            elif arm == "no_recurrent":
                # No recurrent synapses: the cue goes to CA1, and there is
                # nothing for R2 to read.
                sig["r1"][arm] = bh.cosine_rows(codes, self.returned(cue))
                sig["r2"][arm] = zeros.clone()
                state = (cue, cue)
            elif arm == "no_ca3":
                pl = self.shared.test_plateaus
                if pl is None or pl.shape[0] != codes.shape[0]:
                    pl = self.ca1.plateaus(codes)
                sig["r1"][arm] = bh.cosine_rows(codes, self.ca1.reinstate(pl))
                sig["r2"][arm] = zeros.clone()
                state = None
            elif arm == "vc_baseline":
                sims = F.normalize(codes, dim=1) @ F.normalize(self.study_codes, dim=1).T
                sig["r1"][arm] = sims.max(dim=1).values
                sig["r2"][arm] = sig["r1"][arm].clone()
                state = None
            else:
                raise ValueError("unknown arm {}".format(arm))
            if state is not None:
                ca3[arm] = state
        return sig, ca3

    def describe(self, state, paired):
        """Per item: cue cells, exact landing on the paired or any stored
        pattern, the logged list overlap, and the cue's own self-support
        through the stored weights (diagnostic)."""
        cue, final = state
        d = ca3_description(cue, final, self.stored, paired)
        d["nearest_overlap"] = nearest_overlap(final, self.stored).tolist()
        d["cue_support"] = self_support(self.ca3.W, cue).tolist()
        return d


# ---------------------------------------------------------------- closer lures

def smooth_fields(field, sigma):
    """Gaussian blur of each displacement channel, as a row pass then a
    column pass (the same result as the 2D kernel, in far less memory)."""
    size = int(2 * math.ceil(3 * sigma) + 1)
    ax = torch.arange(size, dtype=field.dtype) - (size - 1) / 2
    g = torch.exp(-ax ** 2 / (2 * sigma ** 2))
    g = g / g.sum()
    n, c, h, w = field.shape
    x = field.reshape(n * c, 1, h, w)
    x = F.conv2d(x, g.view(1, 1, -1, 1), padding=(size // 2, 0))
    x = F.conv2d(x, g.view(1, 1, 1, -1), padding=(0, size // 2))
    return x.reshape(n, c, h, w)


def distortion_draws(n, generator, size=DISTORTION["image_size"],
                     sigma=DISTORTION["elastic_sigma_px"]):
    """The random part of n distortions, drawn once and scaled by magnitude
    later: three uniforms in [-1, 1] (rotation, scale, shear) and a smooth
    random displacement field with root mean square 1 pixel."""
    u = torch.rand(n, 3, generator=generator) * 2 - 1
    field = torch.rand(n, 2, size, size, generator=generator) * 2 - 1
    field = smooth_fields(field, sigma)
    rms = field.pow(2).mean(dim=(1, 2, 3), keepdim=True).sqrt().clamp_min(1e-12)
    return {"u": u, "field": field / rms}


def distort(images, draws, m, params=DISTORTION):
    """Images (n, 1, H, W), ink 1, distorted at magnitude m, then re-centred.

    At magnitude m: rotation u0 m 15 degrees, isotropic scale 1 + u1 m 0.15,
    shear u2 m 0.15, plus the displacement field times m 2 pixels (root mean
    square). Bilinear sampling with blank fill; centre of ink moved
    mid-frame as every Omniglot drawing is (omniglot.centre_of_mass).
    """
    if m == 0:
        return images.clone()
    n, _, h, w = images.shape
    u = draws["u"]
    ang = torch.deg2rad(u[:, 0] * m * params["rotation_deg"])
    s = 1 + u[:, 1] * m * params["scale"]
    sh = u[:, 2] * m * params["shear"]
    cos, sin = torch.cos(ang), torch.sin(ang)
    theta = torch.zeros(n, 2, 3)
    theta[:, 0, 0] = s * cos
    theta[:, 0, 1] = s * (sh * cos - sin)
    theta[:, 1, 0] = s * sin
    theta[:, 1, 1] = s * (sh * sin + cos)
    grid = F.affine_grid(theta, [n, 1, h, w], align_corners=False)
    disp = draws["field"].permute(0, 2, 3, 1) * m * params["elastic_px"] * 2.0 / h
    out = F.grid_sample(images, grid + disp, mode="bilinear", padding_mode="zeros",
                        align_corners=False)
    return torch.stack([omniglot.centre_of_mass(o) for o in out])


def level_targets(closest_edge, n_levels=N_LEVELS):
    """Target vision-code cosines for the closer-lure levels: the midpoints
    of n_levels equal steps from E8's closest-lure edge up to 1 (an exact
    repeat). Level 1 is the most similar."""
    step = (1.0 - closest_edge) / n_levels
    return [1.0 - (j + 0.5) * step for j in range(n_levels)]


class Encoder():
    """The frozen vision network on the CPU, and the drawings of a split."""

    def __init__(self, split, checkpoint=None, threads=None):
        from trisynapsnet.model.aha import load_vc
        self.files, _ = bh.drawing_files(split)
        self.vc = load_vc(checkpoint or omniglot.DEFAULT_CHECKPOINT, device="cpu")
        self.load = omniglot._loader(52, True)

    def images(self, idx):
        return torch.stack([self.load(self.files[i]) for i in idx])

    @torch.no_grad()
    def encode(self, images, batch=1):
        return torch.cat([self.vc(images[a:a + batch], k=4) for a in range(0, len(images), batch)])


def closer_lures(encoder, codes, lst, magnitudes, generator):
    """The closer-lure items of one list: each lure's studied drawing,
    distorted at every level with one draw scaled by the level's magnitude.

    Returns codes (levels x lures, dim), level (1 = most similar), paired.
    """
    sources = lst["paired"][lst["types"] == 1]
    idx = [codes.index(c, d) for c, d in lst["study"][sources].tolist()]
    images = encoder.images(idx)
    draws = distortion_draws(len(idx), generator)
    out, level, paired = [], [], []
    for j, m in enumerate(magnitudes):
        out.append(encoder.encode(distort(images, draws, m)))
        level += [j + 1] * len(idx)
        paired += sources.tolist()
    return torch.cat(out), torch.tensor(level), torch.tensor(paired)


# ---------------------------------------------------------------- one list

def run_list(codes, lst, seed, baseline, arms, cfg, close=None):
    """Both readouts for every arm on one list; lesion arms study again.

    close: optional (codes, level, paired) of closer lures, appended to the
    test items as type 3.
    """
    study = codes.dense([codes.index(c, d) for c, d in lst["study"].tolist()])
    test = codes.dense([codes.index(c, d) for c, d in lst["test"].tolist()])
    types, paired = lst["types"].clone(), lst["paired"].clone()
    level = torch.zeros(len(types), dtype=torch.long)
    if close is not None:
        ccodes, clevel, cpaired = close
        test = torch.cat([test, ccodes.float()])
        types = torch.cat([types, torch.full((len(clevel),), 3, dtype=types.dtype)])
        paired = torch.cat([paired, cpaired])
        level = torch.cat([level, clevel])
    out = {"signal": {r: {} for r in READOUTS}, "ca3": {}, "types": types.tolist(),
           "paired": paired.tolist(), "level": level.tolist()}
    shared = Study(study, seed, cfg)
    shared.share_plateaus(test, baseline, cfg, seed)
    groups = ([(None, [a for a in arms if a in SHARED_ARMS])]
              if any(a in SHARED_ARMS for a in arms) else [])
    groups += [(a, [a]) for a in arms if a in STUDY_ARMS]
    for lesion, group in groups:
        mem = Memory(study, seed, baseline, cfg, shared, lesion=lesion)
        sig, states = mem.recall(test, group)
        for arm in group:
            for r in READOUTS:
                out["signal"][r][arm] = sig[r][arm].tolist()
            if arm in states and arm in CA3_ARMS:
                out["ca3"][arm] = mem.describe(states[arm], paired)
        del mem
    out["similarity"] = bh.lure_similarity(test, study, paired).tolist()
    return out


# ---------------------------------------------------------------- commands

def peak_rss_gb():
    """This process's peak resident memory, in GB (macOS reports bytes)."""
    r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return r / 1e9 if sys.platform == "darwin" else r * 1024 / 1e9


def probe_one(denominator, split="background", load=256, threads=2):
    """Builds and recalls one list at load with every arm and closer lures,
    and reports only peak memory and time; no score is computed."""
    torch.set_num_threads(threads)
    cfg = scaled_model(denominator)
    codes = bh.Codes(bh.encode_split(split))
    baseline = ca1space.background_reference(str(bh.CACHE))[0]
    encoder = Encoder(split)
    lst = bh.build_list(codes.n_characters, load, 1, ca3space.generator("e8b probe", load))
    start = time.time()
    close = closer_lures(encoder, codes, lst, [0.5, 1.0, 1.5, 2.0, 2.5],
                         ca3space.generator("e8b probe distort", load))
    run_list(codes, lst, 0, baseline, list(ARMS), cfg, close=close)
    return {"denominator": denominator, "config": cfg, "load": load,
            "seconds": time.time() - start, "peak_rss_gb": peak_rss_gb()}


def cmd_probe(args):
    """Each size in a fresh process, so each peak is its own."""
    out = []
    for d in args.denominators:
        res = subprocess.run([sys.executable, "-m", "trisynapsnet.eval.recognition", "probe-one",
                              "--denominator", str(d), "--load", str(args.load),
                              "--threads", str(args.threads)],
                             capture_output=True, text=True)
        if res.returncode != 0:
            rec = {"denominator": d, "failed": res.stderr[-2000:]}
        else:
            rec = json.loads(res.stdout.strip().splitlines()[-1])
        print(json.dumps({k: v for k, v in rec.items() if k != "config"}), flush=True)
        out.append(rec)
    path = Path(args.out) if args.out else RESULTS / "e8b_probe.json"
    path.write_text(json.dumps({"experiment": "e8b probe", "load": args.load,
                                "threads": args.threads, "machine": platform.platform(),
                                "torch": torch.__version__, "runs": out}, indent=1))
    print("Wrote {}".format(omniglot.portable(path)))


def cmd_levels(args):
    """Magnitudes of the five closer-lure levels, from background drawings only."""
    torch.set_num_threads(args.threads)
    calib = json.loads((RESULTS / "e8_calibration.json").read_text())
    # E8's lure-bin edges, ascending; the highest is the lower edge of L1,
    # E8's closest lures.
    closest = max(calib["bin_edges"])
    targets = level_targets(closest)
    codes = bh.Codes(bh.encode_split("background"))
    encoder = Encoder("background")
    g = ca3space.generator("e8b levels", args.drawings)
    idx = torch.randperm(codes.n_characters * codes.drawers, generator=g)[:args.drawings].tolist()
    images = encoder.images(idx)
    draws = distortion_draws(len(idx), g)
    ref = codes.dense(idx)

    def median_cos(m):
        return bh.cosine_rows(encoder.encode(distort(images, draws, m)), ref).median().item()

    identity = median_cos(0.0)
    grid = {}
    levels = []
    for target in targets:
        lo, hi = 0.0, args.max_magnitude
        if median_cos(hi) > target:
            levels.append({"target": target, "magnitude": hi, "median_cosine": median_cos(hi),
                           "reached": False})
            continue
        for _ in range(args.steps):
            mid = (lo + hi) / 2
            c = median_cos(mid)
            grid[round(mid, 6)] = c
            if c > target:
                lo = mid
            else:
                hi = mid
        m = (lo + hi) / 2
        levels.append({"target": target, "magnitude": m, "median_cosine": median_cos(m),
                       "reached": True})
        print(json.dumps(levels[-1]), flush=True)
    rec = {"experiment": "e8b levels", "split": "background", "drawings": args.drawings,
           "closest_edge": closest, "targets": targets, "distortion": DISTORTION,
           "identity_median_cosine": identity, "levels": levels,
           "machine": platform.platform(), "torch": torch.__version__}
    path = RESULTS / "e8b_lure_levels.json"
    path.write_text(json.dumps(rec, indent=1))
    print("Wrote {}".format(omniglot.portable(path)))


def default_out(args):
    return RESULTS / "e8b_{}_n{}_d{}.json".format(args.split, args.load, args.per_char)


def cmd_run(args):
    torch.set_num_threads(args.threads)
    if args.lists is None:
        args.lists = bh.lists_per_seed(args.load)
    cfg = scaled_model(args.denominator)
    out = Path(args.out) if args.out else default_out(args)
    seeds = list(range(args.first_seed, args.first_seed + args.seeds))
    recorded = bh.recorded_args(args)
    recorded.pop("func", None)
    record = None
    if out.is_file():
        record = json.loads(out.read_text())
        mismatch = [k for k in RESUME_KEYS if record["args"].get(k) != recorded.get(k)]
        if mismatch:
            raise SystemExit("{} was made with other settings ({})".format(
                omniglot.portable(out), ", ".join(mismatch)))
        if set(seeds) <= set(record["seeds_done"]):
            print("Every seed is done already: {}".format(omniglot.portable(out)))
            return record
    done = set(record["seeds_done"]) if record else set()
    per_seed = record["per_seed"] if record else {}
    codes = bh.Codes(bh.encode_split(args.split))
    baseline = ca1space.background_reference(str(bh.CACHE))[0]
    magnitudes = None
    encoder = None
    if args.close:
        lv = json.loads((RESULTS / "e8b_lure_levels.json").read_text())
        magnitudes = [x["magnitude"] for x in lv["levels"]]
        encoder = Encoder(args.split, args.checkpoint)
    print("E8b {} load {} per character {}, {} lists per seed, seeds {}, arms {}, model 1/{} "
          "(DG {}, CA3 {}, CA1 {}); done {}".format(
              args.split, args.load, args.per_char, args.lists, seeds, " ".join(args.arms),
              args.denominator, cfg["dg_units"], cfg["ca3_units"], cfg["ca1_units"],
              sorted(done)), flush=True)
    start = time.time()
    for seed in seeds:
        if seed in done:
            continue
        items = {"types": [], "paired": [], "level": [], "test": [], "similarity": [],
                 "signal": {r: {a: [] for a in args.arms} for r in READOUTS}, "ca3": {}}
        for i in range(args.lists):
            lst = bh.build_list(codes.n_characters, args.load, args.per_char,
                                ca3space.generator("e8 list", args.split, args.load,
                                                   args.per_char, seed, i))
            close = None
            if args.close:
                close = closer_lures(encoder, codes, lst, magnitudes,
                                     ca3space.generator("e8b distort", args.split, args.load,
                                                        args.per_char, seed, i))
            res = run_list(codes, lst, seed * 1000 + i, baseline, args.arms, cfg, close=close)
            n_main = len(lst["types"])
            for key in ("types", "paired", "level"):
                items[key] += res[key]
            items["test"] += lst["test"].tolist() + [[-1, -1]] * (len(res["types"]) - n_main)
            items["similarity"] += bh.round_list(res["similarity"])
            for r in READOUTS:
                for arm in args.arms:
                    items["signal"][r][arm] += bh.round_list(res["signal"][r][arm])
            for arm, d in res["ca3"].items():
                slot = items["ca3"].setdefault(arm, {k: [] for k in d})
                for k, v in d.items():
                    slot[k] += bh.round_list(v) if isinstance(v[0], float) else v
        per_seed[str(seed)] = items
        done.add(seed)
        print("seed {} done ({:.0f} s, peak {:.2f} GB)".format(
            seed, time.time() - start, peak_rss_gb()), flush=True)
        record = {"experiment": "e8b", "args": recorded, "model": cfg,
                  "types": list(TYPES), "readouts": list(READOUTS),
                  "lure_magnitudes": magnitudes, "seeds_done": sorted(done),
                  "per_seed": per_seed, "complete": done >= set(seeds),
                  "machine": platform.platform(), "torch": torch.__version__,
                  "seconds": (record or {}).get("seconds", 0.0) + time.time() - start,
                  "peak_rss_gb": max((record or {}).get("peak_rss_gb", 0.0), peak_rss_gb())}
        start = time.time()
        out.parent.mkdir(parents=True, exist_ok=True)
        tmp = out.with_suffix(".tmp")
        tmp.write_text(json.dumps(record))
        tmp.replace(out)
    print("Wrote {}".format(omniglot.portable(out)), flush=True)
    return record


# Fixed in docs/e8b_protocol.md from the memory probe, before any run.
DENOMINATOR = 500


def build_parser():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="command", required=True)
    pr = sub.add_parser("probe", help="peak memory and time per size, no scores")
    pr.add_argument("--denominators", type=int, nargs="+", default=[2000, 1000, 750, 500, 400])
    pr.add_argument("--load", type=int, default=256)
    pr.add_argument("--threads", type=int, default=2)
    pr.add_argument("--out", default=None)
    pr.set_defaults(func=cmd_probe)
    po = sub.add_parser("probe-one")
    po.add_argument("--denominator", type=int, required=True)
    po.add_argument("--load", type=int, default=256)
    po.add_argument("--threads", type=int, default=2)
    po.set_defaults(func=lambda a: print(json.dumps(probe_one(a.denominator, load=a.load,
                                                              threads=a.threads))))
    lv = sub.add_parser("levels", help="closer-lure magnitudes from background drawings")
    lv.add_argument("--drawings", type=int, default=1000)
    lv.add_argument("--steps", type=int, default=18)
    lv.add_argument("--max-magnitude", type=float, default=6.0)
    lv.add_argument("--threads", type=int, default=4)
    lv.set_defaults(func=cmd_levels)
    r = sub.add_parser("run", help="one condition, every seed")
    r.add_argument("--split", default="evaluation", choices=list(bh.SPLITS))
    r.add_argument("--load", type=int, default=HUMAN_LOAD)
    r.add_argument("--per-char", type=int, default=1)
    r.add_argument("--lists", type=int, default=None)
    r.add_argument("--arms", nargs="+", default=list(ARMS), choices=list(ARMS))
    r.add_argument("--seeds", type=int, default=10)
    r.add_argument("--first-seed", type=int, default=0)
    r.add_argument("--threads", type=int, default=2)
    r.add_argument("--denominator", type=int, default=DENOMINATOR)
    r.add_argument("--no-close", dest="close", action="store_false",
                   help="skip the closer-lure set")
    r.add_argument("--checkpoint", default=str(omniglot.DEFAULT_CHECKPOINT))
    r.add_argument("--cache-dir", default=str(bh.CACHE))
    r.add_argument("--out", default=None)
    r.set_defaults(func=cmd_run)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    main()
