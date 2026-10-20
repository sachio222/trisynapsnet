# Adapted from github.com/sachio222/aha4 (MIT), evaluate.py at 446d6db.
# New here: the local CA3 rules, DG and CA3 size, cue weight, validation
# runs, and per-seed diagnostics in the output.
"""Scores the model on one-shot Omniglot runs, once per seed.

In each run the model studies 20 drawings, recalls 20 drawings of the same
characters by another person, and gets scored by minimum-MSE matching at
each stage:

    pixels  raw images, a floor to compare against
    vc      the frozen vision network alone
    pr      PR(EC-CA3) output
    pc      CA3 after it settles
    pm      CA1's image reconstruction

--runs official scores Lake's 20 runs. --runs background scores 20
validation runs built from the background alphabets, for choosing
settings without touching Lake's runs.

Seeds set the hippocampal parts only. The vision network comes from the
checkpoint, so the vc and pixels scores are the same on every seed.

Example:
    python -m fh.eval.evaluate --runs background --ca3-rule covariance --seeds 5 --normalise
"""

import argparse
import json
import platform
import statistics
from dataclasses import asdict
from pathlib import Path

import torch

from fh.data import omniglot
from fh.eval import oneshot
from fh.model import modules
from fh.model.aha import AHA, AHAConfig, load_vc
from fh.utils import resolve_device, set_seed

REPO = Path(__file__).resolve().parents[2]

# AHA's paper size: 10 of 225 DG cells on, and 20 cells updated per step.
PAPER_UNITS, PAPER_UPDATE = 225, 20


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--checkpoint", default=str(omniglot.DEFAULT_CHECKPOINT),
                   help="pretrained vision network, aha4's by default")
    p.add_argument("--data-dir", default=str(omniglot.DEFAULT_DATA),
                   help="Omniglot folder, aha4's by default")
    p.add_argument("--runs", default="official", choices=["official", "background"],
                   help="Lake's 20 runs, or 20 validation runs from the background alphabets")
    p.add_argument("--runs-seed", type=int, default=0,
                   help="which validation runs to build, separate from the model seed")
    p.add_argument("--device", default="auto", help="auto, cpu, mps or cuda")
    p.add_argument("--seeds", type=int, default=10, help="how many seeds to repeat over")
    p.add_argument("--first-seed", type=int, default=0)
    p.add_argument("--ca3-rule", default="pinverse", choices=modules.CA3_RULES)
    p.add_argument("--dg-units", type=int, default=PAPER_UNITS, help="DG and CA3 cells")
    p.add_argument("--dg-k", type=int, default=10, help="cells on in DG and CA3")
    p.add_argument("--ca3-cue-weight", type=float, default=0.0,
                   help="how strongly the cue keeps driving CA3 during recall (local rules)")
    p.add_argument("--ca3-iters", type=int, default=70, help="CA3 settling steps")
    p.add_argument("--ca3-update", type=int, default=None,
                   help="cells updated per step for bipolar rules; by default 20 per 225 cells")
    p.add_argument("--study-steps", type=int, default=60)
    p.add_argument("--match", default=oneshot.DIRECTIONS[0], choices=oneshot.DIRECTIONS)
    p.add_argument("--normalise", action="store_true",
                   help="L2-normalise every stage's vectors before MSE matching")
    p.add_argument("--normalise-input", action="store_true",
                   help="L2-normalise the VC output before it feeds DG and PR")
    p.add_argument("--out", default=None,
                   help="output JSON; by default results/bio_e1_<runs>_<rule>_<units>_<k>[_cw<w>].json")
    return p.parse_args(argv)


def build_config(args):
    """The model config for a set of parsed arguments.

    Bipolar rules update a fixed number of cells per step. A bigger network
    updates the same share by default, so every size settles over the same
    number of sweeps through its cells.
    """
    update = args.ca3_update
    if update is None:
        update = round(PAPER_UPDATE * args.dg_units / PAPER_UNITS)
    return AHAConfig(ca3_rule=args.ca3_rule, study_steps=args.study_steps,
                     normalise_input=args.normalise_input, dg_units=args.dg_units,
                     dg_k=args.dg_k, ca3_cue_weight=args.ca3_cue_weight,
                     ca3_iters=args.ca3_iters, ca3_update=update)


def default_out(args):
    name = "bio_e1_{}_{}_{}_{}".format(args.runs, args.ca3_rule, args.dg_units, args.dg_k)
    if args.ca3_cue_weight:
        name += "_cw{:g}".format(args.ca3_cue_weight)
    return REPO / "results" / (name + ".json")


def summarise(values):
    return {"mean": statistics.mean(values),
            "std": statistics.stdev(values) if len(values) > 1 else 0.0,
            "min": min(values), "max": max(values)}


def load(args, config):
    centre = True
    if args.runs == "official":
        return omniglot.load_runs(args.data_dir, config.image_size, centre)
    return omniglot.load_background_runs(args.data_dir, config.image_size, centre,
                                         seed=args.runs_seed)


def main(argv=None):
    args = parse_args(argv)
    device = resolve_device(args.device)
    set_seed(args.first_seed)
    config = build_config(args)
    runs = load(args, config)

    print("Device: {}. {} {} runs x {} seeds. CA3 {}, {} cells, {} on, cue weight {:g}.".format(
        device, len(runs), args.runs, args.seeds, config.ca3_rule, config.dg_units,
        config.dg_k, config.ca3_cue_weight), flush=True)

    vc = load_vc(args.checkpoint, device=device)
    aha = AHA(vc, config, device=device)
    aha.cache_vc(True)
    seeds = range(args.first_seed, args.first_seed + args.seeds)
    result = oneshot.evaluate(aha, runs, seeds, direction=args.match,
                              normalise=args.normalise, diagnostics=True,
                              log=lambda line: print(line, flush=True))

    summary = {stage: summarise(acc) for stage, acc in result["accuracy"].items()}
    diagnostics = {name: summarise(v) for name, v in result["diagnostics"].items()}

    print("\nOne-shot accuracy, mean over {} seeds".format(args.seeds))
    for stage, s in summary.items():
        print("{:<8}{:>8.1%}  ± {:.1%}".format(stage, s["mean"], s["std"]))
    print("CA3 self-recall exact {:.1%}, overlap {:.2f}; DG overlap same {:.2f}, diff {:.2f}".format(
        diagnostics["self_recall_exact"]["mean"], diagnostics["self_recall_overlap"]["mean"],
        diagnostics["dg_same"]["mean"], diagnostics["dg_diff"]["mean"]))
    print("Took {:.0f} s".format(result["seconds"]))

    out = Path(args.out) if args.out else default_out(args)
    out.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "args": vars(args),
        "config": asdict(config),
        "coding_level": config.dg_k / config.dg_units,
        "device": str(device),
        "machine": platform.platform(),
        "torch": torch.__version__,
        "summary": summary,
        "diagnostics": diagnostics,
        "seconds": result["seconds"],
        "per_seed": result,
    }
    if args.runs == "background":
        record["validation_runs"] = [run["info"] for run in runs]
    out.write_text(json.dumps(record, indent=2))
    print("Wrote {}".format(out))


if __name__ == "__main__":
    main()
