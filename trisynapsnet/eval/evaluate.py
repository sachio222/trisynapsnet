# Adapted from github.com/sachio222/aha4 (MIT), evaluate.py at 446d6db.
# New here: the local CA3 rules, DG and CA3 size, cue weight, validation
# runs, per-seed diagnostics in the output, and E1b's instance task and
# corrupted test drawings.
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

--task instance scores AHA's one-shot instance-classification task
instead: study 20 drawings of one character, then find each one again
among the same 20. --runs official builds these runs from the evaluation
alphabets, --runs background from the background alphabets.

--occlusion and --noise corrupt the test drawings, never the study
drawings, at one or more levels (see trisynapsnet/data/corrupt.py). Each (seed, run)
studies once and recalls every level, so one call covers a whole sweep.

Seeds set the hippocampal parts only. The vision network comes from the
checkpoint, so the vc and pixels scores are the same on every seed.

Example:
    python -m trisynapsnet.eval.evaluate --runs background --ca3-rule covariance --seeds 5 --normalise
    python -m trisynapsnet.eval.evaluate --task instance --noise 0 0.3 0.6 --normalise
"""

import argparse
import json
import platform
import statistics
from dataclasses import asdict
from pathlib import Path

import torch

from trisynapsnet.data import corrupt, omniglot
from trisynapsnet.eval import oneshot
from trisynapsnet.model import modules
from trisynapsnet.model.aha import AHA, AHAConfig, load_vc
from trisynapsnet.utils import resolve_device, set_seed

REPO = Path(__file__).resolve().parents[2]

# AHA's paper size: 10 of 225 DG cells on, and 20 cells updated per step.
PAPER_UNITS, PAPER_UPDATE = 225, 20


def build_parser():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--checkpoint", default=str(omniglot.DEFAULT_CHECKPOINT),
                   help="pretrained vision network, aha4's by default")
    p.add_argument("--data-dir", default=str(omniglot.DEFAULT_DATA),
                   help="Omniglot folder, aha4's by default")
    p.add_argument("--runs", default="official", choices=["official", "background"],
                   help="Lake's 20 runs, or 20 validation runs from the background alphabets")
    p.add_argument("--eval-data-dir", default=str(omniglot.LOCAL_DATA),
                   help="where the evaluation alphabets for --task instance live or download to")
    p.add_argument("--task", default="classification", choices=["classification", "instance"],
                   help="match each drawing's character (Lake), or the very drawing (AHA)")
    p.add_argument("--runs-seed", type=int, default=0,
                   help="which validation or instance runs to build, separate from the model seed")
    p.add_argument("--occlusion", type=float, nargs="+", default=[0.0],
                   help="circle diameters over the side, one or more, on test drawings")
    p.add_argument("--noise", type=float, nargs="+", default=[0.0],
                   help="shares of pixels replaced, one or more, on test drawings")
    p.add_argument("--corruption-seed", type=int, default=0,
                   help="fixes every circle and noisy pixel, separate from the model seed")
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
    p.add_argument("--also-match", nargs="*", default=[], choices=oneshot.DIRECTIONS,
                   help="more matching directions scored from the same states, as '<stage> <direction>'")
    p.add_argument("--normalise", action="store_true",
                   help="L2-normalise every stage's vectors before MSE matching")
    p.add_argument("--normalise-input", action="store_true",
                   help="L2-normalise the VC output before it feeds DG and PR")
    p.add_argument("--ca1-rule", default="pm", choices=["pm", "btsp", "backprop_ec"],
                   help="E4: AHA's CA1 (pixels), one-shot BTSP CA1, or PM's network with EC as target")
    p.add_argument("--ca1-units", type=int, default=2118, help="CA1 cells for --ca1-rule btsp")
    p.add_argument("--ca1-plateau-share", type=float, default=0.005,
                   help="share of CA1 cells that plateau per drawing, --ca1-rule btsp")
    p.add_argument("--ca1-ec3-baseline", default="background-mean",
                   choices=["background-mean", "none"], help="plateau drive baseline, --ca1-rule btsp")
    p.add_argument("--ca1-l2", type=float, default=4e-4, help="L2 penalty, --ca1-rule backprop_ec")
    p.add_argument("--cache-dir", default=None,
                   help="folder with E1c's cached vision codes, for the background mean EC code")
    p.add_argument("--out", default=None,
                   help="output JSON; by default results/bio_e1_<runs>_<rule>_<units>_<k>[_cw<w>][_it<n>].json,"
                        " or e1b_<task>_<runs>_..._<corruption>.json for E1b")
    return p


def parse_args(argv=None):
    return build_parser().parse_args(argv)


def corruption_levels(args):
    """The corruption kind and its levels, from --occlusion and --noise.

    Returns ("none", [0.0]) when neither is set. A sweep may include 0,
    the clean drawings. Occlusion and noise never mix in one call.
    """
    occlusion = any(level != 0 for level in args.occlusion)
    noise = any(level != 0 for level in args.noise)
    if occlusion and noise:
        build_parser().error("use --occlusion or --noise, not both")
    if occlusion:
        return "occlusion", list(args.occlusion)
    if noise:
        return "noise", list(args.noise)
    return "none", [0.0]


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
                     ca3_iters=args.ca3_iters, ca3_update=update,
                     ca1_rule=args.ca1_rule, ca1_units=args.ca1_units,
                     ca1_plateau_share=args.ca1_plateau_share,
                     ca1_ec3_baseline=args.ca1_ec3_baseline == "background-mean",
                     ca1_l2=args.ca1_l2)


def recorded_args(args):
    """The arguments as the result file records them, with every path
    made portable (see omniglot.portable)."""
    recorded = dict(vars(args))
    for key in ("checkpoint", "data_dir", "eval_data_dir", "out", "cache_dir"):
        if recorded.get(key) is not None:
            recorded[key] = omniglot.portable(recorded[key])
    return recorded


def recorded_args(args):
    """The arguments as the result file records them, with every path
    made portable (see omniglot.portable)."""
    recorded = dict(vars(args))
    for key in ("checkpoint", "data_dir", "eval_data_dir", "out"):
        if recorded.get(key) is not None:
            recorded[key] = omniglot.portable(recorded[key])
    return recorded


def default_out(args):
    """E1's name for a clean classification run, E1b's name otherwise."""
    kind, _ = corruption_levels(args)
    e1 = args.task == "classification" and kind == "none"
    prefix = "bio_e1" if e1 else "e1b_{}".format(args.task)
    name = "{}_{}_{}_{}_{}".format(prefix, args.runs, args.ca3_rule, args.dg_units, args.dg_k)
    if args.ca3_cue_weight:
        name += "_cw{:g}".format(args.ca3_cue_weight)
    if args.ca3_iters != 70:
        name += "_it{}".format(args.ca3_iters)
    if not e1:
        name += "_{}".format(kind)
    return REPO / "results" / (name + ".json")


def summarise(values):
    return {"mean": statistics.mean(values),
            "std": statistics.stdev(values) if len(values) > 1 else 0.0,
            "min": min(values), "max": max(values)}


def load(args, config):
    centre = True
    if args.task == "instance":
        split, root = (("evaluation", args.eval_data_dir) if args.runs == "official"
                       else ("background", args.data_dir))
        return omniglot.load_instance_runs(root, config.image_size, centre,
                                           seed=args.runs_seed, split=split)
    if args.runs == "official":
        return omniglot.load_runs(args.data_dir, config.image_size, centre)
    return omniglot.load_background_runs(args.data_dir, config.image_size, centre,
                                         seed=args.runs_seed)


def main(argv=None):
    args = parse_args(argv)
    device = resolve_device(args.device)
    set_seed(args.first_seed)
    config = build_config(args)
    kind, values = corruption_levels(args)
    runs = load(args, config)

    print("Device: {}. {} {} {} runs x {} seeds. CA3 {}, {} cells, {} on, cue weight {:g}.".format(
        device, len(runs), args.runs, args.task, args.seeds, config.ca3_rule, config.dg_units,
        config.dg_k, config.ca3_cue_weight), flush=True)
    if kind != "none":
        print("Test drawings: {} at {}, corruption seed {}.".format(
            kind, ", ".join("{:g}".format(v) for v in values), args.corruption_seed), flush=True)

    # Each level's corrupted drawings are built once and kept, so the VC
    # cache encodes them once for all seeds.
    levels = [(level, [run["recall"] if kind == "none" else
                       corrupt.corrupt(run["recall"], kind, level, args.corruption_seed, i)
                       for i, run in enumerate(runs)]) for level in values]

    vc = load_vc(args.checkpoint, device=device)
    aha = AHA(vc, config, device=device)
    if config.ca1_rule == "btsp" and config.ca1_ec3_baseline:
        from trisynapsnet.eval import ca1space
        aha.ca1_baseline = ca1space.background_reference(args.cache_dir)[0]
    aha.cache_vc(True)
    seeds = range(args.first_seed, args.first_seed + args.seeds)
    results = oneshot.evaluate_levels(aha, runs, levels, seeds, direction=args.match,
                                      normalise=args.normalise, diagnostics=True,
                                      log=lambda line: print(line, flush=True),
                                      also=tuple(args.also_match))

    records = []
    for result in results:
        summary = {stage: summarise(acc) for stage, acc in result["accuracy"].items()}
        diagnostics = {name: summarise(v) for name, v in result["diagnostics"].items()}
        records.append({"corruption": kind, "level": result["level"], "summary": summary,
                        "recall_loss": summarise(result["recall_loss"]),
                        "diagnostics": diagnostics, "per_seed": result})

        print("\n{} {:g}: one-shot accuracy, mean over {} seeds".format(
            kind, result["level"], args.seeds))
        for stage, s in summary.items():
            print("{:<8}{:>8.1%}  ± {:.1%}".format(stage, s["mean"], s["std"]))
        print("recall-loss {:.4f}".format(records[-1]["recall_loss"]["mean"]))
        print("CA3 self-recall exact {:.1%}, overlap {:.2f}; DG overlap same {:.2f}, diff {:.2f}".format(
            diagnostics["self_recall_exact"]["mean"], diagnostics["self_recall_overlap"]["mean"],
            diagnostics["dg_same"]["mean"], diagnostics["dg_diff"]["mean"]))
    seconds = results[0]["seconds"]
    print("Took {:.0f} s".format(seconds))

    out = Path(args.out) if args.out else default_out(args)
    out.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "args": recorded_args(args),
        "config": asdict(config),
        "coding_level": config.dg_k / config.dg_units,
        "device": str(device),
        "machine": platform.platform(),
        "torch": torch.__version__,
        "seconds": seconds,
        "levels": records,
    }
    # A single level keeps E1's layout at the top level too.
    if len(records) == 1:
        for key in ("summary", "recall_loss", "diagnostics", "per_seed"):
            record[key] = records[0][key]
    if args.task == "instance":
        record["instance_runs"] = [run["info"] for run in runs]
    elif args.runs == "background":
        record["validation_runs"] = [run["info"] for run in runs]
    out.write_text(json.dumps(record, indent=2))
    print("Wrote {}".format(omniglot.portable(out)))


if __name__ == "__main__":
    main()
