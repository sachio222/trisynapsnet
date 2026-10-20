"""E1c end to end: many drawings studied at once, recalled from corrupted copies.

The full model studies N drawings, one each of N different characters, in
one exposure. It then sees every drawing again, corrupted by occlusion or
noise as in E1b, and must bring back the memory of that very drawing. This
is AHA's instance task at a higher load: E1b studied 20 drawings, E1c
studies 20, 100 and 200.

Each test is scored with settling and with the no-settling control, which
passes the k most active PR cells straight on, both through the same CA1.
Matching runs in both directions:

    test-to-study  each test state picks the nearest studied state, the
                   way a cue retrieves a memory.
    study-to-test  each studied state picks the nearest test state, AHA's
                   direction.

CA3 measures follow the CA3 harness (trisynapsnet/eval/ca3space.py): exact
recall, overlap with the right stored pattern before and after settling,
and the ideal nearest-memory lookup.

Example:
    python -m trisynapsnet.eval.endtoend --load 100 --kind occlusion --seeds 5
"""

import argparse
import json
import math
import platform
import time
from dataclasses import asdict
from pathlib import Path

import torch

from trisynapsnet.data import corrupt, omniglot
from trisynapsnet.eval import ca3space, oneshot
from trisynapsnet.model import modules
from trisynapsnet.model.aha import AHA, AHAConfig, load_vc
from trisynapsnet.utils import resolve_device

REPO = Path(__file__).resolve().parents[2]
RULES = ("pinverse", "covariance", "willshaw")
LOADS = (20, 100, 200)
LEVELS = (0.0, 0.3, 0.5, 0.7)
# Each seed studies about this many drawings in all, split into runs of N.
ITEMS_PER_SEED = 400

# Stages scored by matching. "_none" is the no-settling control and "_cue"
# settles from the PR output as given (start="cue", local rules only).
STAGES = ("vc", "pr", "pc", "pc_none", "pc_cue", "pm", "pm_none", "pm_cue")
DIRECTIONS = oneshot.DIRECTIONS
CA3_METRICS = ("exact", "overlap_start", "overlap_final", "ident_start", "ident_final",
               "on_stored")
LOSSES = ("recall_loss", "recall_loss_none", "recall_loss_cue")


def runs_per_seed(load):
    return max(1, math.ceil(ITEMS_PER_SEED / load))


def build_run(images, load, seed, run):
    """One run: N characters' drawings to study, and the same drawings again
    in a shuffled order to test, with labels pointing at each one's study
    index."""
    chars = torch.randperm(images.shape[0], generator=ca3space.generator(
        "e2e chars", load, seed, run))[:load]
    labels = torch.randperm(load, generator=ca3space.generator("e2e order", load, seed, run))
    study = images[chars].clone()
    return {"study": study, "recall": study[labels].clone(), "labels": labels,
            "characters": chars.tolist()}


@torch.no_grad()
def score_level(aha, study, recall, labels, cue_recall):
    """Every E1c score for one recall of one run, as a flat dict."""
    k = aha.cfg.dg_k
    labels = labels.cpu()
    stored = study["dg"].cpu()
    start = modules.kwta(recall["pr"], k)
    control = start if aha.cfg.local_rule else modules.condition_memorise(start)
    states = {"vc": recall["vc"], "pr": recall["pr"], "pc": recall["pc"], "pc_none": control,
              "pm": recall["pm"], "pm_none": aha.pm(control)}
    if cue_recall is not None:
        states["pc_cue"], states["pm_cue"] = cue_recall, aha.pm(cue_recall)

    out = {}
    for stage, state in states.items():
        reference = study["pm"] if stage.startswith("pm") else study[stage.split("_")[0]]
        for direction in DIRECTIONS:
            out["{} {}".format(stage, direction)] = oneshot.run_accuracy(
                reference, state, labels, direction, normalise=True)

    final_on = recall["pc"].cpu() > 0
    s = ca3space.score(start.cpu() > 0, final_on, stored, labels)
    out.update({
        "exact": s["exact"].mean().item(),
        "overlap_start": s["overlap_cue"].mean().item(),
        "overlap_final": s["overlap_final"].mean().item(),
        "ident_start": s["ident_cue"].mean().item(),
        "ident_final": s["ident_final"].mean().item(),
        "on_stored": s["on_stored"].mean().item(),
    })
    pixels = study["pixels"]
    out["recall_loss"] = oneshot.recall_loss(recall["pm"], pixels, labels)
    out["recall_loss_none"] = oneshot.recall_loss(states["pm_none"], pixels, labels)
    if cue_recall is not None:
        out["recall_loss_cue"] = oneshot.recall_loss(states["pm_cue"], pixels, labels)
    return out


def evaluate_rule(aha, runs, levels, seed):
    """Means over runs of every score, one dict per level, for one seed."""
    sums = [dict() for _ in levels]
    for i, run in enumerate(runs):
        aha.reset(seed=seed * 1000 + i)
        study = aha.study(run["study"])
        after = aha.generator.get_state()
        for j, (_, tests) in enumerate(levels):
            aha.generator.set_state(after)
            recall = aha.recall(tests[i])
            cue_recall = None
            if aha.cfg.local_rule:
                aha.ca3.start = "cue"
                cue_recall = aha.ca3.update(aha.cue(recall["pr"]))
                aha.ca3.start = aha.cfg.ca3_start
            for name, value in score_level(aha, study, recall, run["labels"], cue_recall).items():
                sums[j][name] = sums[j].get(name, 0.0) + value / len(runs)
    return sums


def build_parser():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--load", type=int, required=True, help="drawings studied at once")
    p.add_argument("--kind", required=True, choices=corrupt.KINDS)
    p.add_argument("--levels", type=float, nargs="+", default=list(LEVELS))
    p.add_argument("--rules", nargs="+", default=list(RULES), choices=RULES)
    p.add_argument("--split", default="evaluation", choices=["evaluation", "background"])
    p.add_argument("--seeds", type=int, default=5)
    p.add_argument("--first-seed", type=int, default=0)
    p.add_argument("--corruption-seed", type=int, default=0)
    p.add_argument("--device", default="auto")
    p.add_argument("--checkpoint", default=str(omniglot.DEFAULT_CHECKPOINT))
    p.add_argument("--out-dir", default=str(REPO / "results"))
    return p


def out_path(out_dir, split, rule, load, kind):
    return Path(out_dir) / "e1c_e2e_{}_{}_225_10_n{}_{}.json".format(split, rule, load, kind)


def main(argv=None):
    args = build_parser().parse_args(argv)
    device = resolve_device(args.device)
    rules = [r for r in args.rules
             if not out_path(args.out_dir, args.split, r, args.load, args.kind).is_file()]
    if not rules:
        print("Every result file exists already.")
        return

    data = ca3space.encoded_characters(args.split, args.device)
    images = data["images"]
    vc = load_vc(args.checkpoint, device=device)
    models = {}
    for rule in rules:
        models[rule] = AHA(vc, AHAConfig(ca3_rule=rule), device=device)
        models[rule].cache_vc(True)
    # One cache serves every rule: the vision network is frozen.
    shared_cache = {}
    for aha in models.values():
        aha._vc_cache = shared_cache

    n_runs = runs_per_seed(args.load)
    seeds = list(range(args.first_seed, args.first_seed + args.seeds))
    per_seed = {rule: [dict() for _ in args.levels] for rule in rules}
    start = time.time()
    print("Device: {}. Load {}, {} runs a seed, {} at {}, rules {}.".format(
        device, args.load, n_runs, args.kind, args.levels, ", ".join(rules)), flush=True)

    run_info = []
    for seed in seeds:
        runs = [build_run(images, args.load, seed, r) for r in range(n_runs)]
        run_info.append([run["characters"] for run in runs])
        levels = [(level, [corrupt.corrupt(run["recall"], args.kind, level, args.corruption_seed,
                                           seed * 1000 + r) for r, run in enumerate(runs)])
                  for level in args.levels]
        for rule in rules:
            sums = evaluate_rule(models[rule], runs, levels, seed)
            for store, means in zip(per_seed[rule], sums):
                for name, value in means.items():
                    store.setdefault(name, []).append(value)
            line = "seed {} {:<10} ".format(seed, rule) + "  ".join(
                "{:g}: pc {:.1%} none {:.1%}".format(level, s["pc test-to-study"],
                                                     s["pc_none test-to-study"])
                for level, s in zip(args.levels, sums))
            print(line + "  ({:.0f} s)".format(time.time() - start), flush=True)
        shared_cache.clear()

    for rule in rules:
        aha = models[rule]
        record = {
            "experiment": "e1c_end_to_end",
            "rule": rule,
            "split": args.split,
            "load": args.load,
            "kind": args.kind,
            "runs_per_seed": n_runs,
            "seeds": seeds,
            "corruption_seed": args.corruption_seed,
            "config": asdict(aha.cfg),
            "matching": "normalised minimum MSE",
            "device": str(device),
            "machine": platform.platform(),
            "torch": torch.__version__,
            "seconds": time.time() - start,
            "levels": [{"level": level, "per_seed": values,
                        "summary": {name: ca3space.summarise(v) for name, v in values.items()}}
                       for level, values in zip(args.levels, per_seed[rule])],
            "characters": run_info,
        }
        path = out_path(args.out_dir, args.split, rule, args.load, args.kind)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record, indent=2))
        print("Wrote {}".format(path.name))


if __name__ == "__main__":
    main()
