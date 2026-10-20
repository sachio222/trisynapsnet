"""Builds E1's summary table from results/bio_e1_*.json.

Writes results/bio_e1.md with one table for the validation runs (Phase A)
and one for Lake's runs (Phase B). It also answers the two questions the
driver script asks between phases: which local rule and size does best at
the CA3 stage on the validation runs, and which size does best for a given
rule.

Example:
    python scripts/make_e1_table.py
    python scripts/make_e1_table.py --best-local
    python scripts/make_e1_table.py --best-size covariance
"""

import argparse
import json
from pathlib import Path

RESULTS = Path(__file__).resolve().parents[1] / "results"
LOCAL_RULES = ("covariance", "willshaw")
RULE_ORDER = ("pinverse", "hebbian", "covariance", "willshaw")
SIZE_ORDER = ((225, 10), (1000, 44), (4000, 178), (1000, 10), (4000, 40))


def load(results_dir=RESULTS):
    rows = []
    for path in sorted(Path(results_dir).glob("bio_e1_*.json")):
        r = json.loads(path.read_text())
        c = r["config"]
        rows.append({
            "file": path.name, "runs": r["args"]["runs"], "rule": c["ca3_rule"],
            "units": c["dg_units"], "k": c["dg_k"], "cue_weight": c["ca3_cue_weight"],
            "iters": c["ca3_iters"],
            "seeds": r["args"]["seeds"], "summary": r["summary"],
            "diagnostics": r["diagnostics"], "seconds": r["seconds"],
        })

    def order(row):
        size = (row["units"], row["k"])
        return (row["runs"] != "background", RULE_ORDER.index(row["rule"]),
                SIZE_ORDER.index(size) if size in SIZE_ORDER else 99, row["cue_weight"],
                -row["iters"])
    return sorted(rows, key=order)


def pc(row):
    return row["summary"]["pc"]["mean"]


def best_local(rows):
    """The local rule and size with the highest CA3 accuracy on validation
    runs, cue weight 0. Ties go to the smaller network."""
    pool = [r for r in rows if r["runs"] == "background" and r["rule"] in LOCAL_RULES
            and r["cue_weight"] == 0 and r["iters"] == 70]
    return max(pool, key=lambda r: (pc(r), -r["units"]))


def best_size(rows, rule):
    pool = [r for r in rows if r["runs"] == "background" and r["rule"] == rule
            and r["cue_weight"] == 0 and r["iters"] == 70]
    return max(pool, key=lambda r: (pc(r), -r["units"]))


def acc(row, stage):
    s = row["summary"][stage]
    return "{:.1f} ± {:.1f}".format(100 * s["mean"], 100 * s["std"])


def table(rows):
    lines = ["| runs | rule | units | k | coding level | cue weight | CA3 steps | VC | PR | PC | PM "
             "| self-recall exact (overlap) | DG overlap same / diff | seconds |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        d = r["diagnostics"]
        lines.append("| {} | {} | {} | {} | {:.1%} | {:g} | {} | {} | {} | {} | {} "
                     "| {:.1%} ({:.2f}) | {:.2f} / {:.2f} | {:.0f} |".format(
                         r["runs"], r["rule"], r["units"], r["k"], r["k"] / r["units"],
                         r["cue_weight"], r["iters"], acc(r, "vc"), acc(r, "pr"), acc(r, "pc"), acc(r, "pm"),
                         d["self_recall_exact"]["mean"], d["self_recall_overlap"]["mean"],
                         d["dg_same"]["mean"], d["dg_diff"]["mean"], r["seconds"]))
    return "\n".join(lines)


def build(rows):
    background = [r for r in rows if r["runs"] == "background"]
    official = [r for r in rows if r["runs"] == "official"]
    parts = ["# E1: local learning rules in CA3", "",
             "Accuracy is one-shot classification in percent, mean ± standard deviation "
             "across seeds, with normalised study-to-test matching. Self-recall is the share "
             "of study drawings whose own PR output settles CA3 on exactly the stored "
             "pattern, with the mean share of stored cells recovered in brackets. DG overlap "
             "is shared active DG cells over k, without refractory inhibition, for a study "
             "and test drawing of the same character and of different characters. CA3 steps is the most settling steps allowed; local rules stop "
             "early once the state stops changing, and 0 means CA3 passes on the k most active "
             "cells of the PR output.", ""]
    if background:
        parts += ["## Phase A: validation runs from the background alphabets, {} seeds".format(
            background[0]["seeds"]), "", table(background), ""]
    if official:
        parts += ["## Phase B: Lake's 20 official runs, {} seeds".format(official[0]["seeds"]),
                  "", table(official), ""]
    return "\n".join(parts)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--best-local", action="store_true",
                   help='print "rule units k" for the best local rule and size')
    p.add_argument("--best-size", metavar="RULE", help='print "units k" for this rule')
    p.add_argument("--results", default=str(RESULTS))
    args = p.parse_args(argv)
    rows = load(args.results)

    if args.best_local:
        r = best_local(rows)
        print(r["rule"], r["units"], r["k"])
    elif args.best_size:
        r = best_size(rows, args.best_size)
        print(r["units"], r["k"])
    else:
        md = build(rows)
        out = Path(args.results) / "bio_e1.md"
        out.write_text(md)
        print(md)
        print("Wrote {}".format(out))


if __name__ == "__main__":
    main()
