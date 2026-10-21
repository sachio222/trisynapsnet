"""E4: CA1 on its own, returning EC codes from CA3 patterns, against load.

E1c found that CA1, AHA's PM, limits recall above about 50 drawings: its
error floor rises with load even when CA3 hands it the exact stored
pattern. E4 replaces PM with a CA1 that learns each drawing in one
presentation by behavioural timescale synaptic plasticity (BTSP), and
returns the drawing's EC code, the vision network's 20,449 numbers,
through a Hebbian CA1-to-EC projection (modules.CA1BTSP).

The harness skips the vision network's training and PR, like E1c's CA3
harness (ca3space.py). For each seed it takes one drawing each of N
different characters, makes DG's pattern for each, and lets every CA1 arm
learn the N (pattern, EC code) pairs:

    btsp_<ratio>         CA1BTSP at a CA1:CA3 cell ratio, one presentation
                         each
    backprop_ec          PM's network and training (60 Adam steps, L2
                         penalty 4e-4) with the EC code as the target
    backprop_ec_scaled   the same, with the EC code scaled up so its size
                         matches the pixels' (background alphabets), so the
                         L2 penalty weighs as much as it does for PM
    backprop_ec_nol2     the same without the L2 penalty
    pm_pixels            AHA's PM as trained in E1c, rebuilding pixels, for
                         reference; scored in pixel space
    pm_pixels_nol2       the same without the L2 penalty
    mean                 no memory: the mean stored EC code for every cue

Then each arm gets CA3 states and returns a code:

    exact                     the stored pattern itself
    cue <r> <s>               a damaged copy, as E1c damages it (share r of
                              active cells removed, strays numbering s x k
                              added), passed straight on
    <rule> <r> <s> settled    the damaged copy after CA3 settles with the
                              covariance rule or clipped binary synapses

Scores, per cue: cosine similarity between the returned code and the right
drawing's EC code, and identification, whether the stored EC code nearest
the returned one (by cosine) is the right drawing, with ties scoring 1 over
the number tied. Every choice is in docs/e4_protocol.md.

Example:
    python -m trisynapsnet.eval.ca1space --split background --units 225 --seeds 5 \
        --shares 0.005 0.01 0.02 0.05
"""

import argparse
import json
import platform
import statistics
import time
from pathlib import Path

import torch
import torch.nn.functional as F

from trisynapsnet.data import omniglot
from trisynapsnet.eval import ca3space
from trisynapsnet.model import modules

REPO = Path(__file__).resolve().parents[2]

LOADS = (20, 50, 100, 200, 500)
# CA1 cells per CA3 cell. Human: 16 million CA1 against 1.7 million CA3
# pyramidal cells; rat: 350,000 against 210,000 (see docs/e4_protocol.md).
RATIOS = {"human": 16e6 / 1.7e6, "rat": 350e3 / 210e3}
CA3_RULES = ("covariance", "willshaw")
CONDITIONS = ca3space.CONDITIONS
MAX_CUES = ca3space.MAX_CUES
# AHA's PM settings (paper Table 3), as in E1c.
CA1_HIDDEN, CA1_LR, CA1_L2, CA1_STEPS = ca3space.CA1_HIDDEN, ca3space.CA1_LR, \
    ca3space.CA1_L2, ca3space.CA1_STEPS
IMAGE_SIZE = ca3space.IMAGE_SIZE


def ca1_units(n, ratio):
    return int(round(n * RATIOS[ratio]))


def active_cells(n, share):
    """Active DG and CA3 cells for a share: E1c's table at 4.4%, else rounded."""
    if abs(share - 0.044) < 1e-9 and n in ca3space.SIZES:
        return ca3space.SIZES[n]
    return max(1, int(round(share * n)))


def identify(out, refs, target):
    """Identification credit per row: the nearest ref by cosine is the target.

    Ties, such as a returned code of all zeros, score 1 over the number tied
    when the target is among them.
    """
    sims = F.normalize(out.float(), dim=1) @ F.normalize(refs.float(), dim=1).T
    best = sims.max(dim=1, keepdim=True).values
    tied = sims >= best - 1e-6
    rows = torch.arange(out.shape[0])
    return tied[rows, target].float() / tied.sum(dim=1).float()


def cosine(out, refs, target):
    return F.cosine_similarity(out.float(), refs[target].float(), dim=1, eps=1e-12)


def train_backprop(net, X, Y, seed_steps=CA1_STEPS, l2=CA1_L2):
    """PM's training: Adam, learning rate 0.01, L2 4e-4, full-batch steps."""
    opt = torch.optim.Adam(net.parameters(), lr=CA1_LR, weight_decay=l2)
    with torch.enable_grad():
        for _ in range(seed_steps):
            loss = F.mse_loss(net(X), Y)
            opt.zero_grad()
            loss.backward()
            opt.step()
    return net.eval()


def build_arms(X, E, images, n, seed_parts, shares, ratios, plateau_source="ec3",
               baseline=None, ec_scale=1.0):
    """Trains every CA1 arm on the stored pairs. Returns ({name: callable},
    {name: seconds to learn}, {name: presentations or steps}).

    baseline is the EC3 baseline for CA1BTSP (None for raw drive), and
    ec_scale multiplies the EC target of backprop_ec_scaled.
    """
    arms, seconds, cost = {}, {}, {}
    for ratio in ratios:
        for share in shares:
            name = "btsp_{}".format(ratio) if len(shares) == 1 else "btsp_{}_{:g}".format(ratio, share)
            start = time.time()
            ca1 = modules.CA1BTSP(n, E.shape[1], ca1_units(n, ratio), plateau_share=share,
                                  seed=ca3space.derive("btsp", ratio, *seed_parts),
                                  plateau_source=plateau_source, ec3_baseline=baseline)
            ca1.store(X, E)
            seconds[name] = time.time() - start
            cost[name] = {"presentations": X.shape[0], "units": ca1.units, "plateau_cells": ca1.m}
            arms[name] = ca1

    # Every backpropagation arm starts from the same weights as E1c's CA1.
    for name, scale, l2 in (("backprop_ec", 1.0, CA1_L2), ("backprop_ec_scaled", ec_scale, CA1_L2),
                            ("backprop_ec_nol2", 1.0, 0.0)):
        torch.manual_seed(ca3space.derive("ca1", *seed_parts))
        start = time.time()
        net = train_backprop(modules.CA1ToEC(n, E.shape[1], CA1_HIDDEN), X, E * scale, l2=l2)
        seconds[name] = time.time() - start
        cost[name] = {"steps": CA1_STEPS, "hidden": CA1_HIDDEN, "l2": l2, "target_scale": scale}
        arms[name] = lambda s, net=net: net(s)

    if images is not None:
        for name, l2 in (("pm_pixels", CA1_L2), ("pm_pixels_nol2", 0.0)):
            torch.manual_seed(ca3space.derive("ca1", *seed_parts))
            start = time.time()
            pm = train_backprop(modules.CA1(n, IMAGE_SIZE ** 2, CA1_HIDDEN, IMAGE_SIZE), X,
                                images, l2=l2)
            seconds[name] = time.time() - start
            cost[name] = {"steps": CA1_STEPS, "hidden": CA1_HIDDEN, "l2": l2}
            arms[name] = lambda s, pm=pm: pm(s).flatten(1)

    mean = E.mean(dim=0, keepdim=True)
    arms["mean"] = lambda s, mean=mean: mean.expand(s.shape[0], -1)
    return arms, seconds, cost


def cue_inputs(X, seed_parts, rules=CA3_RULES, conditions=CONDITIONS, max_cues=MAX_CUES):
    """The CA3 states each arm receives, with the stored pattern each came from.

    Returns ({input name: (cues, n) 0/1 states}, targets, {input name:
    CA3 exact-recall share}). Cues and damage repeat E1c's draws for the
    same seed parts.
    """
    p, n = X.shape
    k = int(X[0].sum().item())
    pick = ca3space.generator("cues", *seed_parts)
    target = torch.randperm(p, generator=pick)[:max_cues] if p > max_cues else torch.arange(p)
    inputs = {"exact": X[target]}
    exact = {}
    cues = {}
    for r, s in conditions:
        if r == 0 and s == 0:
            continue
        cue = ca3space.damage(X[target], r, s, ca3space.generator("damage", r, s, *seed_parts))
        cues[(r, s)] = cue
        inputs["cue {:g} {:g}".format(r, s)] = cue
    for rule in rules:
        ca3 = ca3space.build_ca3(rule, n, k)
        ca3.train(X, method=rule)
        for (r, s), cue in cues.items():
            state = ca3.update(cue)
            name = "{} {:g} {:g} settled".format(rule, r, s)
            inputs[name] = state
            exact[name] = (state > 0).eq(X[target] > 0).all(dim=1).float().mean().item()
    return inputs, target, exact


@torch.no_grad()
def run_load(X, E, images, n, seed_parts, shares, ratios, rules=CA3_RULES,
             conditions=CONDITIONS, plateau_source="ec3", baseline=None, ec_scale=1.0):
    """Every score for one stored set: {arm: {input: {"cos", "ident"}}}."""
    arms, seconds, cost = build_arms(X, E, images, n, seed_parts, shares, ratios,
                                     plateau_source, baseline, ec_scale)
    inputs, target, ca3_exact = cue_inputs(X, seed_parts, rules, conditions)
    scores = {}
    for name, arm in arms.items():
        pixels = name.startswith("pm_pixels")
        refs = images.flatten(1) if pixels else E
        scores[name] = {}
        for inp, states in inputs.items():
            out = arm(states)
            scores[name][inp] = {"cos": cosine(out, refs, target).mean().item(),
                                 "ident": identify(out, refs, target).mean().item()}
            if pixels:
                scores[name][inp]["mse"] = ((out - refs[target]) ** 2).mean().item()
    return {"scores": scores, "seconds": seconds, "cost": cost, "ca3_exact": ca3_exact,
            "cues": len(target)}


def load_split(split, cache_dir=None, data_dir=None, checkpoint=None, device="auto"):
    """One drawing per character of a split and its vision code, cached as
    in E1c (ca3space.encoded_characters), from cache_dir if given."""
    if cache_dir is not None:
        path = Path(cache_dir) / "e1c_vc_{}_draw0.pt".format(split)
        if path.is_file():
            return torch.load(path)
    if data_dir is not None:
        from trisynapsnet.utils import resolve_device
        from trisynapsnet.model.aha import load_vc
        images, info = omniglot.load_characters(root=data_dir, split=split, seed=0)
        dev = resolve_device(device)
        vc = load_vc(checkpoint or omniglot.DEFAULT_CHECKPOINT, device=dev)
        with torch.no_grad():
            codes = torch.cat([vc(b.to(dev), k=4).cpu() for b in images.split(200)])
        return {"images": images, "vc": codes, "info": info}
    return ca3space.encoded_characters(split, device, checkpoint=checkpoint)


def background_reference(cache_dir=None, data_dir=None, checkpoint=None):
    """Two numbers from the background alphabets, never the evaluation ones.

    Returns (mean EC code, scale): the mean vision code over one drawing of
    each background character, CA1BTSP's EC3 baseline; and the ratio of the
    pixels' root mean square to the EC codes', which sizes the EC target of
    backprop_ec_scaled.
    """
    bg = load_split("background", cache_dir, data_dir, checkpoint)
    scale = (bg["images"].pow(2).mean().sqrt() / bg["vc"].pow(2).mean().sqrt()).item()
    return bg["vc"].mean(dim=0), scale


def summarise(values):
    return {"mean": statistics.mean(values),
            "std": statistics.stdev(values) if len(values) > 1 else 0.0,
            "min": min(values), "max": max(values)}


def build_parser():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--split", default="evaluation", choices=["evaluation", "background"])
    p.add_argument("--units", type=int, default=225, help="DG and CA3 cells")
    p.add_argument("--active-share", type=float, default=0.044,
                   help="share of DG and CA3 cells active; 0.044 is AHA's")
    p.add_argument("--shares", type=float, nargs="+", default=[0.005],
                   help="CA1 plateau shares; several make one BTSP arm each")
    p.add_argument("--ratios", nargs="+", default=list(RATIOS), choices=list(RATIOS))
    p.add_argument("--plateaus", default="ec3", choices=list(modules.PLATEAU_SOURCES))
    p.add_argument("--ec3-baseline", default="background-mean", choices=["background-mean", "none"],
                   help="measure each CA1 cell's plateau drive against its drive from the mean "
                        "background EC code, or use the raw drive")
    p.add_argument("--loads", type=int, nargs="+", default=list(LOADS))
    p.add_argument("--rules", nargs="+", default=list(CA3_RULES), choices=list(CA3_RULES))
    p.add_argument("--seeds", type=int, default=10)
    p.add_argument("--first-seed", type=int, default=0)
    p.add_argument("--no-pixels", action="store_true", help="skip the pm_pixels reference arm")
    p.add_argument("--threads", type=int, default=2)
    p.add_argument("--cache-dir", default=None,
                   help="folder holding E1c's cached vision codes; data/cache by default")
    p.add_argument("--data-dir", default=None, help="Omniglot folder, if codes must be made")
    p.add_argument("--checkpoint", default=None, help="vision network, if codes must be made")
    p.add_argument("--out", default=None)
    return p


def default_out(args, k):
    tag = "_".join("{:g}".format(s) for s in args.shares)
    name = "e4_ca1_{}_{}_{}_q{}".format(args.split, args.units, k, tag)
    if args.plateaus != "ec3":
        name += "_{}plateaus".format(args.plateaus)
    if args.ec3_baseline == "none":
        name += "_raw"
    if args.active_share != 0.044:
        name += "_a{:g}".format(args.active_share)
    return REPO / "results" / (name + ".json")


def main(argv=None):
    args = build_parser().parse_args(argv)
    torch.set_num_threads(args.threads)
    n = args.units
    k = active_cells(n, args.active_share)
    data = load_split(args.split, args.cache_dir, args.data_dir, args.checkpoint)
    mean_code, ec_scale = background_reference(args.cache_dir, args.data_dir, args.checkpoint)
    baseline = mean_code if args.ec3_baseline == "background-mean" else None
    available = data["vc"].shape[0]
    loads = sorted({min(load, available) for load in args.loads})
    seeds = list(range(args.first_seed, args.first_seed + args.seeds))

    start = time.time()
    per_seed = {}
    for seed in seeds:
        pool, order = ca3space.drawing_patterns(data["vc"], n, k, seed)
        E_all, img_all = data["vc"][order], data["images"][order]
        for load in loads:
            parts = ("drawings", args.split, n, k, load, seed)
            res = run_load(pool[:load], E_all[:load], None if args.no_pixels else img_all[:load],
                           n, parts, args.shares, args.ratios, args.rules,
                           plateau_source=args.plateaus, baseline=baseline, ec_scale=ec_scale)
            per_seed.setdefault(load, []).append(res)
            line = "seed {:>2} load {:>4} ".format(seed, load) + "  ".join(
                "{} {:.2f}/{:.2f}".format(a, s["exact"]["ident"], s["exact"]["cos"])
                for a, s in res["scores"].items())
            print(line + "  ({:.0f} s)".format(time.time() - start), flush=True)

    rows = []
    for load in loads:
        results = per_seed[load]
        arms = results[0]["scores"]
        row = {"load": load, "cues": results[0]["cues"], "arms": {}, "seconds": {},
               "cost": results[0]["cost"], "ca3_exact": {}}
        for arm, inputs in arms.items():
            row["arms"][arm] = {}
            for inp, metrics in inputs.items():
                row["arms"][arm][inp] = {m: {"per_seed": [r["scores"][arm][inp][m] for r in results]}
                                         for m in metrics}
                for m, v in row["arms"][arm][inp].items():
                    v["summary"] = summarise(v["per_seed"])
        for arm in results[0]["seconds"]:
            row["seconds"][arm] = summarise([r["seconds"][arm] for r in results])
        for inp in results[0]["ca3_exact"]:
            row["ca3_exact"][inp] = summarise([r["ca3_exact"][inp] for r in results])
        rows.append(row)

    record = {
        "experiment": "e4_ca1space",
        "split": args.split,
        "units": n,
        "k": k,
        "active_share": args.active_share,
        "ca1_units": {r: ca1_units(n, r) for r in args.ratios},
        "plateau_shares": args.shares,
        "plateau_source": args.plateaus,
        "ec3_baseline": args.ec3_baseline,
        "backprop_ec_scale": ec_scale,
        "btsp_parameters": modules.btsp_parameters(),
        "connect": 0.6,
        "gate": 0.5,
        "ca3_rules": args.rules,
        "conditions": [list(c) for c in CONDITIONS],
        "loads": loads,
        "characters_available": available,
        "seeds": seeds,
        "backprop": {"hidden": CA1_HIDDEN, "lr": CA1_LR, "l2": CA1_L2, "steps": CA1_STEPS},
        "cache_dir": None if args.cache_dir is None else omniglot.portable(args.cache_dir),
        "seconds": time.time() - start,
        "machine": platform.platform(),
        "torch": torch.__version__,
        "rows": rows,
    }
    out = Path(args.out) if args.out else default_out(args, k)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, indent=1))
    print("Wrote {}".format(omniglot.portable(out)))


if __name__ == "__main__":
    main()
