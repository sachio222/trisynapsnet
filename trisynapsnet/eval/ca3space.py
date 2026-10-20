"""E1c: CA3 on its own, cued with damaged copies of the patterns it stores.

A nearest-memory lookup compares a cue with a list of every stored memory
and picks the closest. For a cue with random damage it is the best decoder
there is, so CA3 cannot beat it. The brain keeps no such list. E1c asks how
close CA3's settling comes to that lookup without one, as the number of
stored memories grows and as cues lose more of their cells, and whether
settling's filled-in pattern lets CA1 rebuild the drawing better than the
raw cue does.

The harness skips the vision network and PR. It stores N patterns in CA3,
cues CA3 with damaged copies of some of them, lets it settle and scores the
final state. Patterns come from two sources:

    random    N random 0/1 patterns with exactly k of n cells on.
    drawings  DG's patterns for N drawings, one drawing each of N
              different characters, made by DG as it runs in the model.

Damage removes a share of a pattern's k active cells, adds stray cells
numbering a share of k, or both. Every choice is listed in
docs/e1c_protocol.md.

Example:
    python -m trisynapsnet.eval.ca3space --source random --units 225 --k 10 \
        --rule covariance --seeds 10
"""

import argparse
import hashlib
import json
import math
import platform
import statistics
import time
from pathlib import Path

import torch
import torch.nn.functional as F

from trisynapsnet.data import omniglot
from trisynapsnet.model import modules
from trisynapsnet.model.aha import load_vc

REPO = Path(__file__).resolve().parents[2]
CACHE = REPO / "data" / "cache"

RULES = ("pinverse", "covariance", "willshaw")
SIZES = {225: 10, 1000: 44, 4000: 178}
LOADS = (20, 50, 100, 200, 500, 1000)
# (share of active cells removed, stray cells added as a share of k).
CONDITIONS = ((0.0, 0.0), (0.2, 0.0), (0.4, 0.0), (0.6, 0.0), (0.8, 0.0),
              (0.0, 0.25), (0.0, 0.5), (0.0, 1.0), (0.4, 0.5))
# Above this many stored patterns, a random sample of this many is cued.
MAX_CUES = 200

# AHA's settings (paper Table 3), as in E1 and E1b.
GAIN, ITERS, PAPER_UPDATE, PAPER_UNITS = 2.7, 70, 20, 225
IMAGE_SIZE = 52
CA1_HIDDEN, CA1_LR, CA1_L2, CA1_STEPS = 100, 0.01, 4e-4, 60

METRICS = ("exact", "overlap_cue", "overlap_final", "stray_cue", "stray_final",
           "ident_cue", "ident_final", "on_stored", "active_final", "iterations", "fixed")
CA1_METRICS = ("ca1_cue", "ca1_final", "ca1_lookup", "ca1_target")


def derive(*parts):
    """A seed fixed by any mix of names and numbers."""
    key = ":".join(str(p) for p in parts).encode()
    return int(hashlib.sha256(key).hexdigest()[:15], 16)


def generator(*parts):
    return torch.Generator().manual_seed(derive(*parts))


def count(fraction, k):
    """How many cells a share of k means: fraction x k, rounded half up."""
    return int(math.floor(fraction * k + 0.5))


def random_patterns(p, n, k, generator):
    """p random 0/1 patterns, each with exactly k of n cells on."""
    winners = torch.rand(p, n, generator=generator).argsort(dim=1)[:, :k]
    return torch.zeros(p, n).scatter(1, winners, 1.0)


def damage(X, remove, add, generator):
    """Damaged copies of 0/1 patterns X, shape (p, n), each with k cells on.

    Each copy loses count(remove, k) of its active cells, picked at random,
    and gains count(add, k) stray cells, picked at random from the cells
    the pattern has off. Every row gets its own draw.
    """
    k = int(X[0].sum().item())
    if not torch.all(X.sum(dim=1) == k):
        raise ValueError("Every pattern must have the same number of cells on")
    drop, extra = count(remove, k), count(add, k)
    if drop > k or extra > X.shape[1] - k:
        raise ValueError("Too much damage for a pattern with {} of {} cells on".format(
            k, X.shape[1]))
    keys = torch.rand(X.shape, generator=generator)
    cue = X.clone()
    on = X > 0
    if drop:
        idx = torch.where(on, keys, torch.full_like(keys, 2.0)).argsort(dim=1)[:, :drop]
        cue.scatter_(1, idx, 0.0)
    if extra:
        idx = torch.where(~on, keys, torch.full_like(keys, 2.0)).argsort(dim=1)[:, :extra]
        cue.scatter_(1, idx, 1.0)
    return cue


def lookup(on, X, target):
    """Ideal nearest-memory lookup, scored against the right memory.

    Picks the stored pattern sharing the most active cells with each row
    of `on`. Every stored pattern has k cells on, so this ranks the same as
    cosine similarity. When several patterns tie for nearest, the score is
    1 over the number tied if the right one is among them, the expected
    score of breaking the tie at random.

    Returns (credit per row, index of the first nearest pattern).
    """
    sims = on.float() @ X.float().T
    best = sims.max(dim=1, keepdim=True).values
    tied = sims == best
    rows = torch.arange(on.shape[0])
    credit = tied[rows, target].float() / tied.sum(dim=1).float()
    return credit, sims.argmax(dim=1)


def score(cue_on, final_on, X, target):
    """Per-cue scores of a settled CA3 state, before any averaging.

    Args:
        cue_on, final_on: (cues, n) bool, cells on in the raw cue and in
            CA3's final state (state above zero).
        X: (p, n) the stored 0/1 patterns, each with k cells on.
        target: (cues,) index of the stored pattern each cue came from.

    Returns a dict of (cues,) float tensors:
        exact          the final state is exactly the right pattern
        overlap_*      share of the right pattern's k cells that are on
        stray_*        cells on outside the right pattern, over k
        ident_*        ideal lookup from that state picks the right pattern
        on_stored      the final state is exactly some stored pattern
        active_final   cells on in the final state
    """
    Xb = X > 0
    k = Xb[0].sum().float()
    right = Xb[target]
    sims = final_on.float() @ X.float().T
    is_stored = (sims == k).any(dim=1) & (final_on.sum(dim=1).float() == k)
    return {
        "exact": (final_on == right).all(dim=1).float(),
        "overlap_cue": (cue_on & right).sum(dim=1).float() / k,
        "overlap_final": (final_on & right).sum(dim=1).float() / k,
        "stray_cue": (cue_on & ~right).sum(dim=1).float() / k,
        "stray_final": (final_on & ~right).sum(dim=1).float() / k,
        "ident_cue": lookup(cue_on, X, target)[0],
        "ident_final": lookup(final_on, X, target)[0],
        "on_stored": is_stored.float(),
        "active_final": final_on.sum(dim=1).float(),
    }


def build_ca3(rule, n, k):
    """CA3 as in E1 and E1b, with the local rules settling from the cue as given."""
    update = round(PAPER_UPDATE * n / PAPER_UNITS)
    return modules.CA3(n, GAIN, update, ITERS, k=k, cue_weight=0.0, start="cue")


def code(rule, X):
    """A 0/1 pattern in the code a rule stores: -1/+1 for the pseudo-inverse."""
    return modules.condition_memorise(X) if rule in modules.BIPOLAR_RULES else X


def train_ca1(stored, images, seed):
    """CA1 (AHA's PM) trained on the stored patterns as AHA trains it.

    The same layers, optimizer, learning rate, L2 penalty and 60 full-batch
    steps as AHA.study(), mapping each stored CA3 pattern to its drawing.
    """
    with torch.enable_grad():
        return _train_ca1(stored, images, seed)


def _train_ca1(stored, images, seed):
    torch.manual_seed(seed)
    pm = modules.CA1(stored.shape[1], IMAGE_SIZE ** 2, CA1_HIDDEN, IMAGE_SIZE)
    opt = torch.optim.Adam(pm.parameters(), lr=CA1_LR, weight_decay=CA1_L2)
    for _ in range(CA1_STEPS):
        loss = F.mse_loss(pm(stored), images)
        opt.zero_grad()
        loss.backward()
        opt.step()
    return pm.eval()


@torch.no_grad()
def ca1_error(pm, x, images):
    """Mean squared error of CA1's reconstruction from x, per row."""
    return ((pm(x) - images) ** 2).flatten(1).mean(dim=1)


@torch.no_grad()
def run_load(rule, X, seed_parts, images=None, conditions=CONDITIONS, max_cues=MAX_CUES):
    """Stores X in CA3, cues it under every damage condition and scores it.

    Args:
        rule: CA3 rule.
        X: (p, n) 0/1 patterns to store, each with k cells on.
        seed_parts: names and numbers that fix every random draw. Leave the
            rule out so every rule sees the same cues.
        images: (p, 1, H, W) drawings for X, to train and score CA1, or None.

    Returns a list with one dict per condition: the condition, the number
    of cues, and the mean of each score over the cues.
    """
    p, n = X.shape
    k = int(X[0].sum().item())
    ca3 = build_ca3(rule, n, k)
    ca3.train(code(rule, X), method=rule)

    pick = generator("cues", *seed_parts)
    target = (torch.randperm(p, generator=pick)[:max_cues] if p > max_cues
              else torch.arange(p))
    cues = torch.cat([damage(X[target], r, s, generator("damage", r, s, *seed_parts))
                      for r, s in conditions])
    targets = target.repeat(len(conditions))

    state, info = ca3.settle(code(rule, cues), generator=generator("settle", *seed_parts))
    scores = score(cues > 0, state > 0, X, targets)
    scores["iterations"] = info["iterations"].float()
    scores["fixed"] = info["fixed"].float()

    if images is not None:
        stored = code(rule, X)
        pm = train_ca1(stored, images, derive("ca1", *seed_parts))
        clean = images[targets]
        nearest = lookup(cues > 0, X, targets)[1]
        scores["ca1_cue"] = ca1_error(pm, code(rule, cues), clean)
        scores["ca1_final"] = ca1_error(pm, state, clean)
        scores["ca1_lookup"] = ca1_error(pm, stored[nearest], clean)
        scores["ca1_target"] = ca1_error(pm, stored[targets], clean)

    m = len(target)
    out = []
    for i, (r, s) in enumerate(conditions):
        rows = slice(i * m, (i + 1) * m)
        out.append({"remove": r, "add": s, "cues": m,
                    "scores": {name: v[rows].mean().item() for name, v in scores.items()}})
    return out


def encoded_characters(split, device="auto", draw_seed=0, checkpoint=None):
    """One drawing per character of a split and its vision code, cached.

    The vision network is frozen, so each split is encoded once and kept
    in data/cache, which git ignores.
    """
    path = CACHE / "e1c_vc_{}_draw{}.pt".format(split, draw_seed)
    if path.is_file():
        return torch.load(path)
    from trisynapsnet.utils import resolve_device
    images, info = omniglot.load_characters(split=split, seed=draw_seed)
    dev = resolve_device(device)
    vc = load_vc(checkpoint or omniglot.DEFAULT_CHECKPOINT, device=dev)
    codes = []
    with torch.no_grad():
        for batch in images.split(200):
            codes.append(vc(batch.to(dev), k=4).cpu())
    data = {"images": images, "vc": torch.cat(codes), "info": info}
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(data, path)
    return data


@torch.no_grad()
def drawing_patterns(vc, n, k, seed):
    """DG's patterns for every drawing, in a random order fixed by the seed.

    DG runs as in the model: random weights with 25% knocked out, top k,
    and refractory inhibition that carries from one drawing to the next
    and starts fresh for the batch. Its weights come from (n, seed). The
    first N patterns are the stored set at load N, so smaller loads are the
    start of larger ones.

    Returns (patterns, order): patterns[i] is DG's pattern for drawing
    order[i].
    """
    order = torch.randperm(vc.shape[0], generator=generator("order", seed))
    torch.manual_seed(derive("dg", n, seed))
    dg = modules.DG(vc.shape[1], n, k)
    dg.reset()
    return dg(vc[order]), order


def summarise(values):
    return {"mean": statistics.mean(values),
            "std": statistics.stdev(values) if len(values) > 1 else 0.0,
            "min": min(values), "max": max(values)}


def build_parser():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--source", required=True, choices=["random", "drawings"])
    p.add_argument("--split", default="evaluation", choices=["evaluation", "background"],
                   help="Omniglot alphabets for --source drawings")
    p.add_argument("--rule", required=True, choices=RULES)
    p.add_argument("--units", type=int, default=225, help="DG and CA3 cells")
    p.add_argument("--k", type=int, default=None, help="cells on; by default 4.4%% of units")
    p.add_argument("--loads", type=int, nargs="+", default=list(LOADS))
    p.add_argument("--seeds", type=int, default=10)
    p.add_argument("--first-seed", type=int, default=0)
    p.add_argument("--ca1", choices=["auto", "on", "off"], default="auto",
                   help="score CA1 reconstruction; auto means drawings at 225 cells")
    p.add_argument("--threads", type=int, default=3)
    p.add_argument("--device", default="auto", help="device for the one-off vision encoding")
    p.add_argument("--out", default=None)
    return p


def default_out(args):
    tag = args.source if args.source == "random" else "drawings_{}".format(args.split)
    return REPO / "results" / "e1c_ca3_{}_{}_{}_{}.json".format(tag, args.rule, args.units, args.k)


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.k is None:
        args.k = SIZES.get(args.units, round(0.044 * args.units))
    torch.set_num_threads(args.threads)
    n, k = args.units, args.k
    use_ca1 = args.ca1 == "on" or (args.ca1 == "auto" and args.source == "drawings" and n == 225)

    notes = []
    loads = sorted(set(args.loads))
    available = None
    if args.source == "drawings":
        data = encoded_characters(args.split, args.device)
        available = data["vc"].shape[0]
        if any(load > available for load in loads):
            notes.append("The {} alphabets hold {} characters, so loads above {} use all {}.".format(
                args.split, available, available, available))
            loads = sorted({min(load, available) for load in loads})
    if args.rule == "pinverse" and any(load >= n for load in loads):
        notes.append("At loads of {} or more the stored patterns span every direction, so "
                     "the pseudo-inverse weights are the identity matrix.".format(n))

    start = time.time()
    results = {load: None for load in loads}
    for seed in range(args.first_seed, args.first_seed + args.seeds):
        if args.source == "random":
            pool = random_patterns(max(loads), n, k, generator("random", n, k, seed))
            images = None
        else:
            pool, order = drawing_patterns(data["vc"], n, k, seed)
            images = data["images"][order]
        for load in loads:
            X = pool[:load]
            parts = (args.source, args.split if args.source == "drawings" else "-", n, k, load, seed)
            rows = run_load(args.rule, X, parts, images[:load] if use_ca1 else None)
            dup = load - torch.unique(X, dim=0).shape[0]
            if results[load] is None:
                results[load] = [{"remove": r["remove"], "add": r["add"], "cues": r["cues"],
                                  "per_seed": {m: [] for m in r["scores"]}} for r in rows]
                results[load].append({"duplicates": []})
            for res, row in zip(results[load], rows):
                for m, v in row["scores"].items():
                    res["per_seed"][m].append(v)
            results[load][-1]["duplicates"].append(dup)
            line = "seed {:>2} load {:>4}  exact {}  ({:.0f} s)".format(
                seed, load, " ".join("{:.2f}".format(r["scores"]["exact"]) for r in rows),
                time.time() - start)
            print(line, flush=True)

    out_rows = []
    for load in loads:
        dup = results[load].pop()["duplicates"]
        for res in results[load]:
            res["summary"] = {m: summarise(v) for m, v in res["per_seed"].items()}
            out_rows.append(dict(load=load, duplicates=dup, **res))

    record = {
        "experiment": "e1c_ca3space",
        "source": args.source,
        "split": args.split if args.source == "drawings" else None,
        "rule": args.rule,
        "units": n,
        "k": k,
        "loads": loads,
        "characters_available": available,
        "seeds": list(range(args.first_seed, args.first_seed + args.seeds)),
        "settings": {"gain": GAIN, "iterations": ITERS,
                     "bipolar_update": round(PAPER_UPDATE * n / PAPER_UNITS),
                     "cue_weight": 0.0, "start": "cue", "max_cues": MAX_CUES,
                     "ca1": use_ca1, "ca1_steps": CA1_STEPS, "draw_seed": 0},
        "notes": notes,
        "seconds": time.time() - start,
        "machine": platform.platform(),
        "torch": torch.__version__,
        "rows": out_rows,
    }
    out = Path(args.out) if args.out else default_out(args)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, indent=2))
    print("Wrote {}".format(out.relative_to(REPO) if out.is_relative_to(REPO) else out.name))


if __name__ == "__main__":
    main()
