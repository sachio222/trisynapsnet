"""E3: a one-shot perforant path in place of PR, every arm from one study.

E1b and E1c found CA3's completion idle in AHA's layout, because PR, the
EC-to-CA3 network trained by backpropagation, hands CA3 a full pattern
near the right memory. E3 replaces PR with the perforant path, learned in
one presentation while DG imposes the CA3 pattern (modules.PerforantPath),
and asks whether settling then helps end to end.

Each (seed, run) studies once. The model learns:
    DG       the stored CA3 pattern for each drawing, as before
    CA3      covariance and clipped binary weights from those patterns
    PR       60 backpropagation steps, unchanged (the comparison)
    PP       one perforant path per rule, clipped binary and covariance
    CA1      one-shot BTSP at the human CA1-to-CA3 ratio (E4)
    PM       AHA's CA1, rebuilding pixels, as a reference
Then every test drawing is recalled through seven arms:
    pr_none       PR's k most active cells, no settling
    pr_cov        PR, then CA3 settles (covariance), start from PR's top k
    pr_wil        the same with clipped binary CA3
    pp_cov_none   the covariance perforant cue, no settling
    pp_cov        that cue, then covariance CA3 settles from it as given
    pp_wil_none   the clipped binary perforant cue, no settling
    pp_wil        that cue, then clipped binary CA3 settles from it
Each arm's CA3 state goes through the same BTSP CA1 and the same PM. Every
stage is scored by normalised minimum-MSE matching in both directions.
BTSP breaks ties with a random jitter; its generator goes back to its
state after study before each arm, so every arm sees the same jitter.

Tasks:
    classification  Lake's 20 runs (--runs official) or 20 background
                    validation runs (--runs background)
    instance        AHA's instance task: clean, occlusion and noise at
                    every --levels, all from one study per run
    load            E1c's end-to-end runs: --load drawings of different
                    characters, the same drawings corrupted

--grid scores CA3 only, for choosing the perforant settings on background
alphabets: no PR, CA1 or PM, and one cue per setting in the grid.

The result file is written after every seed and a rerun picks up after
the last finished seed.

Example:
    python -m trisynapsnet.eval.perforant --task classification --seeds 10
    python -m trisynapsnet.eval.perforant --task load --load 100 --seeds 5
"""

import argparse
import itertools
import json
import math
import platform
import time
from dataclasses import asdict
from pathlib import Path

import torch
import torch.nn.functional as F

from trisynapsnet.data import corrupt, omniglot
from trisynapsnet.eval import ca3space, oneshot
from trisynapsnet.model import modules
from trisynapsnet.model.aha import AHA, AHAConfig, load_vc
from trisynapsnet.utils import resolve_device

REPO = Path(__file__).resolve().parents[2]
DIRECTIONS = oneshot.DIRECTIONS
RULE_TAGS = {"cov": "covariance", "wil": "willshaw"}
ARMS = ("pr_none", "pr_cov", "pr_wil", "pp_cov_none", "pp_cov", "pp_wil_none", "pp_wil")
STAGES = ("ca3", "ca1", "pm")
CA3_METRICS = ("exact", "overlap_cue", "overlap_final", "stray_cue", "stray_final",
               "ident_cue", "ident_final", "active_cue", "active_final")
LEVELS = (0.3, 0.5, 0.7)
ITEMS_PER_SEED = 400
EMAX_GRID = (None, 0.1, 0.2, 0.3, 0.5)
# A partial result file resumes only when these arguments match.
RESUME_KEYS = ("task", "runs", "load", "levels", "kinds", "first_seed", "runs_seed",
               "corruption_seed", "dg_k", "dg_units", "ca1_units", "ca1_plateau_share",
               "wil_presynaptic", "wil_normalise", "wil_emax", "cov_normalise", "cov_emax", "grid")


def runs_per_seed(load):
    return max(1, math.ceil(ITEMS_PER_SEED / load))


def default_settings():
    """Perforant settings before any choice: k-WTA, raw drive, active above zero."""
    return {"willshaw": {"presynaptic": "positive", "normalise": False, "emax": None},
            "covariance": {"presynaptic": "positive", "normalise": False, "emax": None}}


def grid_settings():
    """Every perforant setting --grid scores, keyed by a short name."""
    out = {}
    for pre, norm, emax in itertools.product(modules.PP_PRESYNAPTIC, (False, True), EMAX_GRID):
        out[setting_name("willshaw", pre, norm, emax)] = (
            "willshaw", {"presynaptic": pre, "normalise": norm, "emax": emax})
    for norm, emax in itertools.product((False, True), EMAX_GRID):
        out[setting_name("covariance", "positive", norm, emax)] = (
            "covariance", {"presynaptic": "positive", "normalise": norm, "emax": emax})
    return out


def setting_name(rule, pre, norm, emax):
    tag = "wil" if rule == "willshaw" else "cov"
    parts = [tag]
    if rule == "willshaw":
        parts.append("pos" if pre == "positive" else "mean")
    parts.append("norm" if norm else "raw")
    parts.append("kwta" if emax is None else "e{:g}".format(emax))
    return "_".join(parts)


def train_pm(aha, stored, images):
    """AHA's CA1 (PM), trained exactly as AHA.study trains it."""
    for _ in range(aha.cfg.study_steps):
        loss = F.mse_loss(aha.pm(stored), images)
        aha.pm_opt.zero_grad()
        loss.backward()
        aha.pm_opt.step()


def build_ca3s(aha, stored):
    """Both local CA3 rules on the same stored patterns. AHA's own CA3 is one."""
    cfg = aha.cfg
    ca3s = {cfg.ca3_rule: aha.ca3}
    for rule in modules.LOCAL_RULES:
        if rule not in ca3s:
            ca3 = modules.CA3(cfg.dg_units, k=cfg.dg_k, n_iter=cfg.ca3_iters,
                              cue_weight=cfg.ca3_cue_weight, start=cfg.ca3_start)
            ca3.train(stored, rule)
            ca3s[rule] = ca3
    return ca3s


def settle(ca3, cue, start):
    saved = ca3.start
    ca3.start = start
    try:
        return ca3.update(cue)
    finally:
        ca3.start = saved


def build_pps(aha, vc, stored, settings, baseline, seed):
    pps = {}
    for rule, kwargs in settings.items():
        pp = modules.PerforantPath(aha.in_dim, aha.cfg.dg_units, aha.cfg.dg_k, rule, seed=seed,
                                   baseline=baseline, **kwargs)
        pp.store(vc, stored)
        pps[rule] = pp
    return pps


@torch.no_grad()
def arm_states(aha, ca3s, pps, vc):
    """Start and final CA3 state of every arm for EC codes vc."""
    k = aha.cfg.dg_k
    pr = aha.pr(vc)
    out = {"pr_none": (modules.kwta(pr, k),) * 2}
    for tag, rule in RULE_TAGS.items():
        out["pr_" + tag] = (out["pr_none"][0], settle(ca3s[rule], pr, "kwta"))
        cue = pps[rule].cue(vc).to(pr.device)
        out["pp_{}_none".format(tag)] = (cue, cue)
        out["pp_" + tag] = (cue, settle(ca3s[rule], cue, "cue"))
    return pr, out


def ca3_metrics(start, final, stored, labels):
    s = ca3space.score(start.cpu() > 0, final.cpu() > 0, stored.cpu(), labels.cpu())
    out = {name: s[name].mean().item() for name in CA3_METRICS if name in s}
    out["active_cue"] = (start.cpu() > 0).sum(dim=1).float().mean().item()
    return out


@torch.no_grad()
def score_states(refs, states, labels, extra=None):
    """Accuracy of every stage of every arm in both directions, plus extras."""
    out = {}
    for arm, by_stage in states.items():
        for stage, state in by_stage.items():
            for d in DIRECTIONS:
                out["{} {} {}".format(arm, stage, d)] = oneshot.run_accuracy(
                    refs[stage], state, labels, d, normalise=True)
    out.update(extra or {})
    return out


def study_and_score(aha, study_images, tests, labels, seed, settings, baseline, arms=ARMS):
    """One (seed, run): study once, then score every test version.

    tests is a list of test-drawing batches, one per level. Returns one
    flat dict of scores per level.
    """
    aha.reset(seed=seed)
    st = aha.study(study_images)
    ca1_state = aha.ca1.generator.get_state()
    stored = st["pc"]
    train_pm(aha, stored, st["pixels"])
    with torch.no_grad():
        refs = {"ca3": stored, "ca1": st["pm"], "pm": aha.pm(stored)}
    ca3s = build_ca3s(aha, stored)
    pps = build_pps(aha, st["vc"], stored, settings, baseline, seed)

    results = []
    for images in tests:
        vc = aha.encode(images)
        pr, states = arm_states(aha, ca3s, pps, vc)
        staged, extra = {}, {}
        for arm in arms:
            start, final = states[arm]
            aha.ca1.generator.set_state(ca1_state)
            with torch.no_grad():
                staged[arm] = {"ca3": final, "ca1": aha.ca1_out(final), "pm": aha.pm(final)}
            for name, value in ca3_metrics(start, final, stored, labels).items():
                extra["{} {}".format(arm, name)] = value
        for d in DIRECTIONS:
            extra["vc {}".format(d)] = oneshot.run_accuracy(st["vc"], vc, labels, d, normalise=True)
            extra["pr {}".format(d)] = oneshot.run_accuracy(st["pr"], pr, labels, d, normalise=True)
        results.append(score_states(refs, staged, labels, extra))
    return results


@torch.no_grad()
def grid_score(aha, study_images, tests, labels, seed, baseline, grid):
    """CA3-stage scores of every perforant setting in grid, for choosing one."""
    aha.reset(seed=seed)
    vc = aha.encode(study_images)
    stored = aha.dg(vc)
    ca3s = build_ca3s(aha, stored)
    stores = {}
    for name, (rule, kwargs) in grid.items():
        key = (rule, kwargs["presynaptic"])
        if key not in stores:
            pp = modules.PerforantPath(aha.in_dim, aha.cfg.dg_units, aha.cfg.dg_k, rule, seed=seed,
                                       baseline=baseline, presynaptic=kwargs["presynaptic"])
            pp.store(vc, stored)
            stores[key] = pp
    results = []
    for images in tests:
        tvc = aha.encode(images)
        drives = {}
        out = {}
        for name, (rule, kwargs) in grid.items():
            pp = stores[(rule, kwargs["presynaptic"])]
            pp.normalise, pp.emax = kwargs["normalise"], kwargs["emax"]
            dkey = (rule, kwargs["presynaptic"], kwargs["normalise"])
            if dkey not in drives:
                drives[dkey] = pp.drive(tvc)
            cue = pp.select(drives[dkey]).to(stored.device)
            for arm, final in (("none", cue), ("settle", settle(ca3s[rule], cue, "cue"))):
                for d in DIRECTIONS:
                    out["{} {} {}".format(name, arm, d)] = oneshot.run_accuracy(
                        stored, final, labels, d, normalise=True)
                for metric, value in ca3_metrics(cue, final, stored, labels).items():
                    out["{} {} {}".format(name, arm, metric)] = value
        results.append(out)
    return results


def build_parser():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--task", default="classification", choices=["classification", "instance", "load"])
    p.add_argument("--runs", default="official", choices=["official", "background"],
                   help="evaluation runs (Lake's, evaluation alphabets) or background-alphabet runs")
    p.add_argument("--load", type=int, default=20, help="--task load: drawings studied at once")
    p.add_argument("--levels", type=float, nargs="+", default=list(LEVELS),
                   help="occlusion and noise levels besides clean drawings, instance and load")
    p.add_argument("--kinds", nargs="+", default=list(corrupt.KINDS), choices=list(corrupt.KINDS))
    p.add_argument("--seeds", type=int, default=10)
    p.add_argument("--first-seed", type=int, default=0)
    p.add_argument("--runs-seed", type=int, default=0)
    p.add_argument("--corruption-seed", type=int, default=0)
    p.add_argument("--dg-k", type=int, default=5, help="active DG and CA3 cells; 5 of 225 is 2%%")
    p.add_argument("--dg-units", type=int, default=225)
    p.add_argument("--ca1-units", type=int, default=2118)
    p.add_argument("--ca1-plateau-share", type=float, default=0.005)
    for tag in ("wil", "cov"):
        p.add_argument("--{}-presynaptic".format(tag), default="positive",
                       choices=list(modules.PP_PRESYNAPTIC))
        p.add_argument("--{}-normalise".format(tag), action="store_true")
        p.add_argument("--{}-emax".format(tag), type=float, default=None)
    p.add_argument("--grid", action="store_true", help="score every perforant setting, CA3 only")
    p.add_argument("--device", default="auto")
    p.add_argument("--threads", type=int, default=2)
    p.add_argument("--checkpoint", default=str(omniglot.DEFAULT_CHECKPOINT))
    p.add_argument("--data-dir", default=str(omniglot.DEFAULT_DATA))
    p.add_argument("--eval-data-dir", default=str(omniglot.LOCAL_DATA))
    p.add_argument("--cache-dir", default=None, help="E1c's cached vision codes")
    p.add_argument("--out", default=None)
    return p


def settings_from(args):
    return {
        "willshaw": {"presynaptic": args.wil_presynaptic, "normalise": args.wil_normalise,
                     "emax": args.wil_emax},
        "covariance": {"presynaptic": "positive", "normalise": args.cov_normalise,
                       "emax": args.cov_emax},
    }


def default_out(args):
    name = "e3_{}_{}".format("grid" if args.grid else args.task, args.runs)
    if args.task == "load":
        name += "_n{}".format(args.load)
    name += "_{}_{}".format(args.dg_units, args.dg_k)
    return REPO / "results" / (name + ".json")


def level_list(args):
    """(kind, level) pairs scored from one study: clean first."""
    if args.task == "classification":
        return [("none", 0.0)]
    return [("none", 0.0)] + [(kind, level) for kind in args.kinds for level in args.levels]


def load_runs(args, image_size=52):
    if args.task == "instance":
        split, root = (("evaluation", args.eval_data_dir) if args.runs == "official"
                       else ("background", args.data_dir))
        return omniglot.load_instance_runs(root, image_size, True, seed=args.runs_seed, split=split)
    if args.runs == "official":
        return omniglot.load_runs(args.data_dir, image_size, True)
    return omniglot.load_background_runs(args.data_dir, image_size, True, seed=args.runs_seed)


def corrupt_tests(images, levels, corruption_seed, run_seed):
    return [images if kind == "none" else corrupt.corrupt(images, kind, level, corruption_seed,
                                                          run_seed)
            for kind, level in levels]


def recorded_args(args):
    recorded = dict(vars(args))
    for key in ("checkpoint", "data_dir", "eval_data_dir", "out", "cache_dir"):
        if recorded.get(key) is not None:
            recorded[key] = omniglot.portable(recorded[key])
    return recorded


def summarise(values):
    return ca3space.summarise(values)


def main(argv=None):
    args = build_parser().parse_args(argv)
    torch.set_num_threads(args.threads)
    device = resolve_device(args.device)
    out = Path(args.out) if args.out else default_out(args)
    levels = level_list(args)
    seeds = list(range(args.first_seed, args.first_seed + args.seeds))

    record = None
    if out.is_file():
        record = json.loads(out.read_text())
        mismatch = [key for key in RESUME_KEYS
                    if record["args"].get(key) != recorded_args(args).get(key)]
        if mismatch:
            raise SystemExit("{} was made with other settings ({}); move it or pass --out".format(
                omniglot.portable(out), ", ".join(mismatch)))
        if set(seeds) <= set(record["seeds_done"]):
            print("Every seed is done already: {}".format(omniglot.portable(out)))
            return record
    done = set(record["seeds_done"]) if record else set()
    per_seed = record["per_seed"] if record else [dict() for _ in levels]

    config = AHAConfig(ca3_rule="covariance", dg_units=args.dg_units, dg_k=args.dg_k,
                       ca1_rule="btsp", ca1_units=args.ca1_units,
                       ca1_plateau_share=args.ca1_plateau_share)
    from trisynapsnet.eval import ca1space
    baseline = ca1space.background_reference(args.cache_dir)[0]
    vc_net = load_vc(args.checkpoint, device=device)
    aha = AHA(vc_net, config, device=device)
    aha.ca1_baseline = baseline
    aha.cache_vc(True)
    settings = settings_from(args)
    grid = grid_settings() if args.grid else None

    fixed_runs = None
    if args.task != "load":
        fixed_runs = load_runs(args)
        fixed_tests = [corrupt_tests(run["recall"], levels, args.corruption_seed, i)
                       for i, run in enumerate(fixed_runs)]
    else:
        characters = ca3space.encoded_characters("evaluation" if args.runs == "official"
                                                 else "background", args.device)
        from trisynapsnet.eval import endtoend

    print("Device {}. E3 {} {}, {} levels, seeds {}, {} of {} cells on; done {}.".format(
        device, args.task, args.runs, len(levels), seeds, args.dg_k, args.dg_units,
        sorted(done)), flush=True)
    start = time.time()
    run_info = record.get("characters", []) if record else []
    for seed in seeds:
        if seed in done:
            continue
        if fixed_runs is not None:
            runs, tests = fixed_runs, fixed_tests
        else:
            runs = [endtoend.build_run(characters["images"], args.load, seed, r)
                    for r in range(runs_per_seed(args.load))]
            run_info.append([run["characters"] for run in runs])
            tests = [corrupt_tests(run["recall"], levels, args.corruption_seed, seed * 1000 + r)
                     for r, run in enumerate(runs)]
        sums = [dict() for _ in levels]
        for i, run in enumerate(runs):
            if args.grid:
                scores = grid_score(aha, run["study"], tests[i], run["labels"], seed * 1000 + i,
                                    baseline, grid)
            else:
                scores = study_and_score(aha, run["study"], tests[i], run["labels"],
                                         seed * 1000 + i, settings, baseline)
            for j, s in enumerate(scores):
                for key, value in s.items():
                    sums[j][key] = sums[j].get(key, 0.0) + value / len(runs)
        for store, means in zip(per_seed, sums):
            for key, value in means.items():
                store.setdefault(key, []).append(value)
        done.add(seed)
        if fixed_runs is None:
            aha._vc_cache.clear()
        if args.grid:
            line = "seed {} done".format(seed)
        else:
            line = "seed {} ".format(seed) + "  ".join(
                "{}:{:g} pr_cov {:.1%} pp_cov {:.1%} pp_cov_none {:.1%}".format(
                    kind, level, s["pr_cov ca3 test-to-study"], s["pp_cov ca3 test-to-study"],
                    s["pp_cov_none ca3 test-to-study"])
                for (kind, level), s in zip(levels, sums))
        print(line + "  ({:.0f} s)".format(time.time() - start), flush=True)

        record = {
            "experiment": "e3_grid" if args.grid else "e3",
            "args": recorded_args(args),
            "config": asdict(config),
            "settings": None if args.grid else settings,
            "grid": {name: [rule, kw] for name, (rule, kw) in grid.items()} if grid else None,
            "in_degree": modules._round_half_up(modules.PP_SHARE * aha.in_dim),
            "connection_share": modules.PP_SHARE,
            "levels": [{"kind": kind, "level": level} for kind, level in levels],
            "matching": "normalised minimum MSE",
            "seeds_done": sorted(done),
            "per_seed": per_seed,
            "summary": [{key: summarise(v) for key, v in store.items()} for store in per_seed],
            "complete": done >= set(seeds),
            "device": str(device),
            "machine": platform.platform(),
            "torch": torch.__version__,
            "seconds": (record or {}).get("seconds", 0.0) + time.time() - start,
        }
        start = time.time()
        if fixed_runs is not None and args.task == "instance":
            record["instance_runs"] = [run["info"] for run in fixed_runs]
        if run_info:
            record["characters"] = run_info
        out.parent.mkdir(parents=True, exist_ok=True)
        tmp = out.with_suffix(".tmp")
        tmp.write_text(json.dumps(record))
        tmp.replace(out)
    print("Wrote {}".format(omniglot.portable(out)), flush=True)
    return record


if __name__ == "__main__":
    main()
