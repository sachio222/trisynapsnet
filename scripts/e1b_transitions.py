"""Where CA3 settling sends each corrupted cue, item by item.

E1b scores matching study-to-test, the paper's direction: each study
drawing looks for its partner among the 20 test states. This script asks
the same question the other way, test-to-study, which is what a memory
does when cued: each test drawing's CA3 state is matched to the nearest of
the 20 stored patterns.

It studies each run once with a local CA3 rule, then recalls each
corrupted test drawing twice, with settling (70 steps at most) and without
(the 10 most active PR cells). Per level it reports:

    test-to-study accuracy with and without settling,
    the share of test drawings only one arm gets right,
    how often settling ends exactly on the right stored pattern, and
    how often, in study-to-test matching of settled states, a study
    drawing finds two or more test states tied at the lowest MSE. Tied
    states are identical copies of one stored pattern.

Writes results/e1b_transitions.md.

Example:
    python scripts/e1b_transitions.py --seeds 10
"""

import argparse
from pathlib import Path

import torch

from trisynapsnet.data import corrupt, omniglot
from trisynapsnet.eval import oneshot
from trisynapsnet.model.aha import AHA, AHAConfig, load_vc
from trisynapsnet.utils import resolve_device

ROOT = Path(__file__).resolve().parents[1]
COLUMNS = ("settling right", "no settling right", "only settling right",
           "only no settling right", "settles exactly on right memory",
           "study items with tied test states")


def tally(stored, plain, settled, labels):
    """Counts for one run and level, in COLUMNS order, out of 20 items."""
    hit_plain = oneshot.min_mse_match(stored, plain, True) == labels
    hit_settled = oneshot.min_mse_match(stored, settled, True) == labels
    exact = (settled[:, None, :] == stored[None, :, :]).all(dim=2).cpu()
    on_right = exact[torch.arange(len(labels)), labels]
    mse = oneshot.mse_matrix(stored, settled, True)   # test rows, study columns
    tied = (mse == mse.min(dim=0, keepdim=True).values).sum(dim=0) > 1
    return torch.tensor([hit_settled.sum(), hit_plain.sum(), (hit_settled & ~hit_plain).sum(),
                         (hit_plain & ~hit_settled).sum(), on_right.sum(), tied.sum()],
                        dtype=torch.float)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--seeds", type=int, default=10)
    p.add_argument("--rule", default="covariance", choices=["covariance", "willshaw"])
    p.add_argument("--device", default="auto")
    p.add_argument("--out", default=str(ROOT / "results" / "e1b_transitions.md"))
    args = p.parse_args(argv)

    device = resolve_device(args.device)
    vc = load_vc(omniglot.DEFAULT_CHECKPOINT, device=device)
    lines = ["# E1b: settling item by item, test-to-study",
             "",
             "CA3 rule: {}. Evaluation-set runs, {} seeds, corruption seed 0. Each row "
             "gives percent of test drawings (first five columns) or of study drawings "
             "(last column), pooled over runs and seeds. Made by scripts/e1b_transitions.py."
             .format(args.rule, args.seeds), ""]

    for task in ("instance", "classification"):
        runs = (omniglot.load_instance_runs(seed=0) if task == "instance"
                else omniglot.load_runs())
        aha = AHA(vc, AHAConfig(ca3_rule=args.rule), device=device)
        aha.cache_vc(True)
        keys = [("none", 0.0)] + [(kind, level) for kind in corrupt.KINDS
                                  for level in corrupt.PAPER_LEVELS[1:]]
        tests = {(kind, level): [r["recall"] if kind == "none" else
                                 corrupt.corrupt(r["recall"], kind, level, 0, i)
                                 for i, r in enumerate(runs)] for kind, level in keys}
        counts = {key: torch.zeros(len(COLUMNS)) for key in keys}
        for seed in range(args.seeds):
            for i, run in enumerate(runs):
                aha.reset(seed=seed * 1000 + i)
                stored = aha.study(run["study"])["pc"]
                for key in keys:
                    pr = aha.pr(aha.encode(tests[key][i]))
                    aha.ca3.n_iter = 0
                    plain = aha.ca3.update(pr)
                    aha.ca3.n_iter = aha.cfg.ca3_iters
                    settled = aha.ca3.update(pr)
                    counts[key] += tally(stored, plain, settled, run["labels"].cpu())
            print("{} seed {} done".format(task, seed), flush=True)

        lines += ["## {} task".format(task.capitalize()), "",
                  "| corruption | level | " + " | ".join(COLUMNS) + " |",
                  "|---|---|" + "---|" * len(COLUMNS)]
        total = args.seeds * len(runs) * 20
        for (kind, level), c in counts.items():
            lines.append("| {} | {:g} | ".format(kind, level) + " | ".join(
                "{:.1f}".format(100 * x / total) for x in c.tolist()) + " |")
        lines.append("")

    Path(args.out).write_text("\n".join(lines))
    print("Wrote {}".format(args.out))


if __name__ == "__main__":
    main()
