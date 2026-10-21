"""E8: a behavioural benchmark, similar-lure recognition with virtual lesions.

The Mnemonic Similarity Task (Stark and colleagues 2013) shows people a
series of pictures once, then tests them with repeats (the same picture),
lures (a similar picture never shown) and foils (new pictures), and asks
old, similar or new. E8 builds the same test from Omniglot's drawings:

    repeat  a studied drawing, shown again
    lure    another person's drawing of a studied character
    foil    a drawing of a character that was not studied

The model studies a list of drawings once, as in E3: DG imposes each
drawing's CA3 pattern, CA3 stores it with clipped binary synapses, the
perforant path learns the drawing's EC code against that pattern, and BTSP
CA1 learns to return the EC code. At test, the perforant path cues CA3, CA3
settles, and CA1 returns an EC code. The decision signal is the cosine
between the test drawing's EC code and the code CA1 returns (CA1 as a
comparator); two thresholds turn it into old, similar or new. This module
writes every item's signal; scripts/make_e8_table.py sets the thresholds on
background alphabets and scores the evaluation alphabets.

Arms that share one study:
    intact          perforant cue, CA3 settles, CA1 returns
    no_recurrent    CA3's recurrent connections removed: the cue goes
                    straight to CA1
    no_ca3          CA3 removed: CA1 is driven by its direct EC input, the
                    same fixed projection that sets its plateaus
    vc_baseline     no hippocampus: the largest cosine between the test
                    code and any studied code
Arms that need their own study:
    no_dg           DG removed: the perforant path's own drive, through its
                    fixed connections with equal weights, picks each
                    drawing's CA3 pattern
    pp_keep<f>      perforant path thinned: each CA3 cell keeps a share f of
                    its 710 EC connections, before study
    ca1_half        half of CA1's cells removed
Removing the whole hippocampus leaves no returned code, so every item is
called new; it needs no run.

Vision codes for every drawing of a split are encoded once and cached in
data/cache, which git ignores.

Example:
    python -m trisynapsnet.eval.behaviour --split background --seeds 10
    python -m trisynapsnet.eval.behaviour --split evaluation --load 100 --arms intact
"""

import argparse
import json
import math
import platform
import time
from pathlib import Path

import torch
import torch.nn.functional as F

from trisynapsnet.data import omniglot
from trisynapsnet.eval import ca1space, ca3space
from trisynapsnet.model import modules

REPO = Path(__file__).resolve().parents[2]
CACHE = REPO / "data" / "cache"
SPLITS = ("background", "evaluation")
TYPES = ("repeat", "lure", "foil")
SHARED_ARMS = ("intact", "no_recurrent", "no_ca3", "vc_baseline")
PP_KEEP = (0.75, 0.5, 0.25)
STUDY_ARMS = ("no_dg",) + tuple("pp_keep{:g}".format(f) for f in PP_KEEP) + ("ca1_half",)
ARMS = SHARED_ARMS + STUDY_ARMS
# Arms whose CA3 state is worth describing: the settled state, or the cue.
CA3_ARMS = ("intact", "no_recurrent", "no_dg") + tuple("pp_keep{:g}".format(f) for f in PP_KEEP)
STUDIED_PER_SEED = 1000

# The model, as E3 left it (docs/e3_protocol.md): 225 DG and CA3 cells,
# 5 on (2%); perforant path with clipped binary synapses, presynaptic
# activity above zero, normalised drive, E%-max 0.3 (E3 item 35); CA3
# with clipped binary synapses settling from the cue; BTSP CA1 with 2,118
# cells (human CA1-to-CA3 ratio), plateau share 0.005.
MODEL = {"dg_units": 225, "dg_k": 5, "dg_gamma": 0.95, "dg_knockout": 0.25,
         "ca3_iters": 70, "pp_presynaptic": "positive", "pp_normalise": True, "pp_emax": 0.3,
         "ca1_units": 2118, "ca1_plateau_share": 0.005, "ca1_connect": 0.6, "ca1_gate": 0.5}
RESUME_KEYS = ("split", "load", "per_char", "lists", "arms", "first_seed")


# ---------------------------------------------------------------- vision codes

def cache_path(split):
    return CACHE / "e8_vc_{}.pt".format(split)


def drawing_files(split, root=None):
    """Every drawing of a split, sorted by (alphabet, character), drawers 1 to 20.

    Drawing i is character i // 20 by drawer i % 20 + 1.
    """
    if root is None:
        root = omniglot.DEFAULT_DATA if split == "background" else omniglot.LOCAL_DATA
    folder = omniglot.download_alphabets(split, root)
    files, info = [], []
    characters = sorted((a.name, c.name) for a in folder.iterdir() if a.is_dir()
                        for c in a.iterdir() if c.is_dir())
    for alphabet, character in characters:
        by_drawer = {int(p.stem.split("_")[1]): p
                     for p in (folder / alphabet / character).glob("*_*.png")}
        if sorted(by_drawer) != list(range(1, omniglot.N_DRAWERS + 1)):
            raise FileNotFoundError("Expected drawers 1 to 20 in {}/{}".format(alphabet, character))
        for d in range(1, omniglot.N_DRAWERS + 1):
            files.append(by_drawer[d])
        info.append([alphabet, character])
    return files, info


def to_sparse(dense):
    """Rows of codes as (counts, col, val): non-zero entries per row, their
    columns (int16) and values."""
    rows = [row.nonzero().flatten() for row in dense]
    counts = torch.tensor([len(r) for r in rows], dtype=torch.long)
    col = torch.cat(rows).to(torch.int16)
    val = torch.cat([dense[i, r] for i, r in enumerate(rows)])
    return counts, col, val


def from_parts(parts, dim, characters, drawers=omniglot.N_DRAWERS):
    """The cache dict from to_sparse() parts, in order."""
    counts = torch.cat([p[0] for p in parts])
    crow = torch.cat([torch.zeros(1, dtype=torch.long), counts.cumsum(0)])
    return {"crow": crow, "col": torch.cat([p[1] for p in parts]),
            "val": torch.cat([p[2] for p in parts]), "dim": dim,
            "characters": characters, "drawers": drawers}


def encode_split(split, device="auto", checkpoint=None, root=None, batch=200):
    """Vision codes of every drawing in a split, cached sparse."""
    path = cache_path(split)
    if path.is_file():
        return torch.load(path)
    from trisynapsnet.model.aha import load_vc
    from trisynapsnet.utils import resolve_device
    files, info = drawing_files(split, root)
    dev = resolve_device(device)
    vc = load_vc(checkpoint or omniglot.DEFAULT_CHECKPOINT, device=dev)
    load = omniglot._loader(52, True)
    parts = []
    with torch.no_grad():
        for start in range(0, len(files), batch):
            images = torch.stack([load(f) for f in files[start:start + batch]])
            parts.append(to_sparse(vc(images.to(dev), k=4).cpu()))
    data = from_parts(parts, vc.output_dim(52), info)
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(data, path)
    return data


class Codes():
    """Vision codes of a split, made dense a few rows at a time."""

    def __init__(self, data):
        self.crow, self.col, self.val = data["crow"], data["col"].long(), data["val"]
        self.dim, self.drawers = data["dim"], data["drawers"]
        self.n_characters = len(data["characters"])
        self.characters = data["characters"]

    def index(self, character, drawer):
        """Drawing index of a character (0-based) by a drawer (1 to 20)."""
        return character * self.drawers + drawer - 1

    def dense(self, idx):
        idx = torch.as_tensor(idx, dtype=torch.long).flatten()
        out = torch.zeros(len(idx), self.dim)
        for row, i in enumerate(idx.tolist()):
            a, b = self.crow[i].item(), self.crow[i + 1].item()
            out[row, self.col[a:b]] = self.val[a:b]
        return out


# ---------------------------------------------------------------- the task

def build_list(n_characters, load, per_char, gen, drawers=omniglot.N_DRAWERS):
    """One study list and its test, as character and drawer numbers.

    load drawings are studied: load / per_char characters, per_char
    drawings each by different drawers. Half the studied drawings, chosen
    at random, come back as repeats; for each of the other half, a drawing
    of the same character by a drawer not in the list comes as a lure.
    load / 2 characters never studied come as foils, one drawing each by a
    random drawer. Every draw comes from gen.

    Returns a dict:
        study       (load, 2) [character, drawer] of each studied drawing
        test        (1.5 load, 2) [character, drawer] of each test drawing
        types       (1.5 load,) 0 repeat, 1 lure, 2 foil
        paired      (1.5 load,) index of the studied drawing a repeat or
                    lure comes from, -1 for foils
    """
    if load % 2 or load % per_char:
        raise ValueError("load must be even and a multiple of per_char")
    n_chars = load // per_char
    if per_char + per_char > drawers:
        raise ValueError("per_char leaves no drawer for lures")
    if n_chars + load // 2 > n_characters:
        raise ValueError("not enough characters for this load")
    perm = torch.randperm(n_characters, generator=gen)
    studied, foil_chars = perm[:n_chars], perm[n_chars:n_chars + load // 2]
    study, spare = [], {}
    for c in studied.tolist():
        order = (torch.randperm(drawers, generator=gen) + 1).tolist()
        study += [[c, d] for d in order[:per_char]]
        spare[c] = order[per_char:]
    halves = torch.randperm(load, generator=gen)
    repeats, lures = sorted(halves[:load // 2].tolist()), sorted(halves[load // 2:].tolist())
    test, types, paired = [], [], []
    for i in repeats:
        test.append(list(study[i]))
        types.append(0)
        paired.append(i)
    for i in lures:
        c = study[i][0]
        test.append([c, spare[c].pop(0)])
        types.append(1)
        paired.append(i)
    foil_drawers = torch.randint(1, drawers + 1, (len(foil_chars),), generator=gen).tolist()
    for c, d in zip(foil_chars.tolist(), foil_drawers):
        test.append([c, d])
        types.append(2)
        paired.append(-1)
    return {"study": torch.tensor(study), "test": torch.tensor(test),
            "types": torch.tensor(types), "paired": torch.tensor(paired)}


def list_generator(split, load, per_char, seed, index):
    return ca3space.generator("e8 list", split, load, per_char, seed, index)


def cosine_rows(x, r):
    """Cosine of each row of x with the same row of r; 0 where r is all zero."""
    nr, nx = r.norm(dim=1), x.norm(dim=1)
    s = (x * r).sum(dim=1) / (nx * nr).clamp_min(1e-12)
    return torch.where(nr > 0, s, torch.zeros_like(s))


def lure_similarity(test_codes, study_codes, paired):
    """Cosine between each test code and its paired studied code (nan for foils)."""
    out = torch.full((len(paired),), float("nan"))
    has = paired >= 0
    out[has] = cosine_rows(test_codes[has], study_codes[paired[has]])
    return out


# ---------------------------------------------------------------- decisions

def threshold_for(signal, rate, above=True):
    """(theta, q) so that P(s > theta) + q P(s = theta) = rate (above), or
    P(s < theta) + q P(s = theta) = rate (below).

    Ties at theta take the response with probability q, so a signal with
    repeated values can still reach the rate exactly.
    """
    s = torch.as_tensor(signal, dtype=torch.float64).flatten()
    if above:
        s = -s
    values = torch.unique(s)  # ascending
    n = len(s)
    for v in values.tolist():
        below = (s < v).sum().item() / n
        at = (s == v).sum().item() / n
        if below + at >= rate - 1e-12:
            q = (rate - below) / at if at > 0 else 0.0
            return (-v if above else v), min(max(q, 0.0), 1.0)
    v = values[-1].item()
    return (-v if above else v), 1.0


def calibrate(repeat_signal, foil_signal, p_old_repeat, p_new_foil):
    """Old threshold from repeats, new threshold from foils."""
    old, q_old = threshold_for(repeat_signal, p_old_repeat, above=True)
    new, q_new = threshold_for(foil_signal, p_new_foil, above=False)
    return {"old": old, "q_old": q_old, "new": new, "q_new": q_new,
            "feasible": new <= old}


def respond(signal, thr):
    """Probability of each answer for each item: (items, 3) old, similar, new."""
    s = torch.as_tensor(signal, dtype=torch.float64).flatten()
    p_old = (s > thr["old"]).double() + thr["q_old"] * (s == thr["old"]).double()
    p_new_rest = (s < thr["new"]).double() + thr["q_new"] * (s == thr["new"]).double()
    p_new = (1.0 - p_old) * p_new_rest
    return torch.stack([p_old, 1.0 - p_old - p_new, p_new], dim=1)


def rates(signal, types, thr, mask=None):
    """Response rates by item type: {type: {old, similar, new}}."""
    p = respond(signal, thr)
    types = torch.as_tensor(types).flatten()
    out = {}
    for t, name in enumerate(TYPES):
        sel = types == t
        if mask is not None:
            sel &= torch.as_tensor(mask).flatten()
        if sel.sum() == 0:
            out[name] = None
            continue
        m = p[sel].mean(dim=0)
        out[name] = {"old": m[0].item(), "similar": m[1].item(), "new": m[2].item()}
    return out


def ldi(r):
    """Lure discrimination index: p(similar | lure) - p(similar | foil)."""
    return r["lure"]["similar"] - r["foil"]["similar"]


def rec(r):
    """Recognition score: p(old | repeat) - p(old | foil)."""
    return r["repeat"]["old"] - r["foil"]["old"]


def bin_edges(similarity, n_bins=5):
    """Inner edges splitting lure similarities into n_bins equal-count bins."""
    s = torch.as_tensor(similarity, dtype=torch.float64)
    s = s[~torch.isnan(s)]
    qs = torch.linspace(0, 1, n_bins + 1, dtype=torch.float64)[1:-1]
    return torch.quantile(s, qs).tolist()


def bin_of(similarity, edges):
    """Lure bin 1 (most similar) to len(edges) + 1 (least); 0 for nan."""
    s = torch.as_tensor(similarity, dtype=torch.float64)
    upper = torch.bucketize(s, torch.tensor(edges, dtype=torch.float64), right=True)
    out = len(edges) + 1 - upper
    return torch.where(torch.isnan(s), torch.zeros_like(out), out)


def ldi_by_bin(signal, types, bins, thr, n_bins=5):
    """LDI for lures in each bin, against all foils."""
    p = respond(signal, thr)
    types, bins = torch.as_tensor(types).flatten(), torch.as_tensor(bins).flatten()
    foil_sim = p[types == 2, 1].mean().item()
    out = []
    for b in range(1, n_bins + 1):
        sel = (types == 1) & (bins == b)
        out.append(p[sel, 1].mean().item() - foil_sim if sel.any() else float("nan"))
    return out


# ---------------------------------------------------------------- the model

def thin(connections, keep, seed):
    """Keep round(keep x in-degree) of each CA3 cell's EC connections.

    Each connection gets one random rank from the seed, so a smaller keep
    removes a superset of what a larger keep removes.
    """
    C = connections.bool()
    g = ca3space.generator("e8 thin", seed)
    rank = torch.rand(C.shape, generator=g)
    rank[~C] = 2.0
    out = torch.zeros_like(C)
    for i in range(C.shape[0]):
        n_keep = int(math.floor(keep * C[i].sum().item() + 0.5))
        out[i, rank[i].argsort()[:n_keep]] = True
    return out


def pp_patterns(connections, codes, k):
    """CA3 patterns with DG removed: k-WTA of the perforant drive through
    every connected synapse at equal weight, from the raw EC rates."""
    return modules.kwta(codes @ connections.float().T, k)


def build_dg(in_dim, seed, cfg=MODEL):
    """DG exactly as AHA.reset(seed) builds it: the first draw after the seed."""
    torch.manual_seed(seed)
    dg = modules.DG(in_dim, cfg["dg_units"], cfg["dg_k"], cfg["dg_gamma"], cfg["dg_knockout"])
    dg.reset()
    return dg


class Memory():
    """One study set through the hippocampus, with an optional lesion."""

    def __init__(self, study_codes, seed, baseline, lesion=None, cfg=MODEL):
        self.cfg, self.seed, self.lesion = cfg, seed, lesion
        n, k, in_dim = cfg["dg_units"], cfg["dg_k"], study_codes.shape[1]
        self.study_codes = study_codes
        pp = modules.PerforantPath(in_dim, n, k, "willshaw", seed=seed,
                                   presynaptic=cfg["pp_presynaptic"],
                                   normalise=cfg["pp_normalise"], emax=cfg["pp_emax"])
        if lesion is not None and lesion.startswith("pp_keep"):
            keep = float(lesion[len("pp_keep"):])
            pp = modules.PerforantPath(in_dim, n, k, "willshaw", seed=seed,
                                       presynaptic=cfg["pp_presynaptic"],
                                       normalise=cfg["pp_normalise"], emax=cfg["pp_emax"],
                                       connections=thin(pp.C, keep, seed))
        self.pp = pp
        dg = build_dg(in_dim, seed, cfg)
        with torch.no_grad():
            if lesion == "no_dg":
                stored = pp_patterns(pp.C, study_codes, k)
            else:
                stored = dg(study_codes)
        self.stored = stored
        self.ca3 = modules.CA3(n, n_iter=cfg["ca3_iters"], k=k, start="cue")
        self.ca3.train(stored, "willshaw")
        pp.store(study_codes, stored)
        units = cfg["ca1_units"] // 2 if lesion == "ca1_half" else cfg["ca1_units"]
        self.ca1 = modules.CA1BTSP(n, in_dim, units, cfg["ca1_plateau_share"],
                                   cfg["ca1_connect"], cfg["ca1_gate"], seed=seed,
                                   ec3_baseline=baseline)
        self.ca1.store(stored > 0, study_codes)
        self.ca1_state = self.ca1.generator.get_state()

    def returned(self, ca3_state):
        """EC code CA1 returns for CA3 states, same jitter for every call."""
        self.ca1.generator.set_state(self.ca1_state)
        return self.ca1(ca3_state)

    @torch.no_grad()
    def recall(self, codes, arms):
        """Decision signal of each arm, and CA3 states, for test codes."""
        cue = self.pp.cue(codes)
        settled = self.ca3.update(cue)
        signals, states = {}, {}
        for arm in arms:
            if arm in ("intact", "no_dg") or arm.startswith("pp_keep") or arm == "ca1_half":
                signals[arm] = cosine_rows(codes, self.returned(settled))
                states[arm] = (cue, settled)
            elif arm == "no_recurrent":
                signals[arm] = cosine_rows(codes, self.returned(cue))
                states[arm] = (cue, cue)
            elif arm == "no_ca3":
                signals[arm] = cosine_rows(codes, self.ca1.reinstate(self.ca1.plateaus(codes)))
            elif arm == "vc_baseline":
                sims = F.normalize(codes, dim=1) @ F.normalize(self.study_codes, dim=1).T
                signals[arm] = sims.max(dim=1).values
            else:
                raise ValueError("unknown arm {}".format(arm))
        return signals, states


def ca3_description(cue, final, stored, paired):
    """Per test item: cue cells, and whether the final state is exactly the
    paired studied drawing's pattern or exactly any stored pattern."""
    on, ref = final > 0, stored > 0
    same = (on[:, None, :] == ref[None, :, :]).all(dim=2)  # (items, stored)
    exact_any = same.any(dim=1)
    exact_paired = torch.zeros(len(paired), dtype=torch.bool)
    has = paired >= 0
    exact_paired[has] = same[has, paired[has]]
    return {"cue_cells": (cue > 0).sum(dim=1).tolist(),
            "exact_paired": exact_paired.int().tolist(), "exact_any": exact_any.int().tolist()}


def run_list(codes, lst, seed, baseline, arms):
    """Every arm's signal for one list; lesion arms study again."""
    study = codes.dense([codes.index(c, d) for c, d in lst["study"].tolist()])
    test = codes.dense([codes.index(c, d) for c, d in lst["test"].tolist()])
    out = {"signal": {}, "ca3": {}}
    shared = [a for a in arms if a in SHARED_ARMS]
    groups = ([(None, shared)] if shared else []) + [(a, [a]) for a in arms if a in STUDY_ARMS]
    for lesion, group in groups:
        mem = Memory(study, seed, baseline, lesion=lesion)
        signals, states = mem.recall(test, group)
        for arm in group:
            out["signal"][arm] = signals[arm].tolist()
            if arm in states and arm in CA3_ARMS:
                out["ca3"][arm] = ca3_description(*states[arm], mem.stored, lst["paired"])
    out["similarity"] = lure_similarity(test, study, lst["paired"]).tolist()
    # The largest cosine between a lure and any studied drawing of its character.
    same_char = (lst["test"][:, 0:1] == lst["study"][None, :, 0])
    sims = F.normalize(test, dim=1) @ F.normalize(study, dim=1).T
    best = torch.where(same_char, sims, torch.full_like(sims, -2.0)).max(dim=1).values
    out["similarity_best"] = torch.where(lst["types"] == 2, torch.full_like(best, float("nan")),
                                         best).tolist()
    return out


# ---------------------------------------------------------------- the runner

def lists_per_seed(load):
    return max(1, math.ceil(STUDIED_PER_SEED / load))


def build_parser():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--split", default="evaluation", choices=list(SPLITS))
    p.add_argument("--load", type=int, default=20, help="drawings studied per list")
    p.add_argument("--per-char", type=int, default=1, help="studied drawings per character")
    p.add_argument("--lists", type=int, default=None,
                   help="lists per seed; default about 1,000 studied drawings")
    p.add_argument("--arms", nargs="+", default=list(ARMS), choices=list(ARMS))
    p.add_argument("--seeds", type=int, default=10)
    p.add_argument("--first-seed", type=int, default=0)
    p.add_argument("--threads", type=int, default=2)
    p.add_argument("--device", default="auto", help="for encoding the vision codes once")
    p.add_argument("--checkpoint", default=str(omniglot.DEFAULT_CHECKPOINT))
    p.add_argument("--cache-dir", default=str(CACHE))
    p.add_argument("--out", default=None)
    return p


def default_out(args):
    return REPO / "results" / "e8_{}_n{}_d{}.json".format(args.split, args.load, args.per_char)


def recorded_args(args):
    out = dict(vars(args))
    for key in ("checkpoint", "cache_dir", "out"):
        if out.get(key) is not None:
            out[key] = omniglot.portable(out[key])
    return out


def round_list(values, places=6):
    return [None if (isinstance(v, float) and math.isnan(v)) else round(v, places) for v in values]


def main(argv=None):
    args = build_parser().parse_args(argv)
    torch.set_num_threads(args.threads)
    if args.lists is None:
        args.lists = lists_per_seed(args.load)
    out = Path(args.out) if args.out else default_out(args)
    seeds = list(range(args.first_seed, args.first_seed + args.seeds))
    record = None
    if out.is_file():
        record = json.loads(out.read_text())
        mismatch = [key for key in RESUME_KEYS
                    if record["args"].get(key) != recorded_args(args).get(key)]
        if mismatch:
            raise SystemExit("{} was made with other settings ({})".format(
                omniglot.portable(out), ", ".join(mismatch)))
        if set(seeds) <= set(record["seeds_done"]):
            print("Every seed is done already: {}".format(omniglot.portable(out)))
            return record
    done = set(record["seeds_done"]) if record else set()
    per_seed = record["per_seed"] if record else {}

    codes = Codes(encode_split(args.split, args.device, args.checkpoint))
    baseline = ca1space.background_reference(args.cache_dir)[0]
    print("E8 {} load {} per character {}, {} lists per seed, seeds {}, arms {}; done {}".format(
        args.split, args.load, args.per_char, args.lists, seeds, " ".join(args.arms),
        sorted(done)), flush=True)
    start = time.time()
    for seed in seeds:
        if seed in done:
            continue
        items = {"types": [], "paired": [], "similarity": [], "similarity_best": [],
                 "test": [], "signal": {a: [] for a in args.arms},
                 "ca3": {a: {"cue_cells": [], "exact_paired": [], "exact_any": []}
                         for a in args.arms if a in CA3_ARMS}}
        for i in range(args.lists):
            lst = build_list(codes.n_characters, args.load, args.per_char,
                             list_generator(args.split, args.load, args.per_char, seed, i))
            res = run_list(codes, lst, seed * 1000 + i, baseline, args.arms)
            items["types"] += lst["types"].tolist()
            items["paired"] += lst["paired"].tolist()
            items["test"] += lst["test"].tolist()
            items["similarity"] += round_list(res["similarity"])
            items["similarity_best"] += round_list(res["similarity_best"])
            for arm in args.arms:
                items["signal"][arm] += round_list(res["signal"][arm])
                if arm in items["ca3"]:
                    for key in items["ca3"][arm]:
                        items["ca3"][arm][key] += res["ca3"][arm][key]
        per_seed[str(seed)] = items
        done.add(seed)
        print("seed {} done ({:.0f} s)".format(seed, time.time() - start), flush=True)
        record = {
            "experiment": "e8",
            "args": recorded_args(args),
            "model": MODEL,
            "types": list(TYPES),
            "seeds_done": sorted(done),
            "per_seed": per_seed,
            "complete": done >= set(seeds),
            "machine": platform.platform(),
            "torch": torch.__version__,
            "seconds": (record or {}).get("seconds", 0.0) + time.time() - start,
        }
        start = time.time()
        out.parent.mkdir(parents=True, exist_ok=True)
        tmp = out.with_suffix(".tmp")
        tmp.write_text(json.dumps(record))
        tmp.replace(out)
    print("Wrote {}".format(omniglot.portable(out)), flush=True)
    return record


if __name__ == "__main__":
    main()
