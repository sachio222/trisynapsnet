"""E3's tables and the choice of perforant settings.

--select reads phase A's grid files (background alphabets only) and prints,
for each perforant rule, the setting with the highest mean CA3-stage
accuracy over 8 conditions (the clean validation runs; the instance runs
clean and at occlusion and noise 0.3, 0.5 and 0.7), both matching
directions, and the settling and no-settling arms weighted equally. Ties
go to the simpler setting: k-WTA before E%-max, raw drive before
normalised, active above zero before above the mean.

Without --select it writes results/e3.md from the phase B to E files.
"""

import argparse
import json
import statistics
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from trisynapsnet.eval import perforant  # noqa: E402

RESULTS = REPO / "results"
DIRECTIONS = ("study-to-test", "test-to-study")
GRID_FILES = ("e3_grid_classification_background_225_5", "e3_grid_instance_background_225_5")


def load(name):
    path = RESULTS / (name + ".json")
    return json.loads(path.read_text()) if path.is_file() else None


def mean(values):
    return statistics.mean(values)


def simplicity(name, spec):
    rule, kw = spec
    emax_rank = perforant.EMAX_GRID.index(kw["emax"])
    return (emax_rank, kw["normalise"], kw["presynaptic"] != "positive")


def grid_scores():
    """{setting: (score, {condition: score})} from phase A."""
    records = [load(n) for n in GRID_FILES]
    if any(r is None for r in records):
        raise SystemExit("Phase A files missing: {}".format(", ".join(GRID_FILES)))
    for r in records:
        if not r["complete"] or len(r["seeds_done"]) < 5:
            raise SystemExit("Phase A not finished: seeds {}".format(r["seeds_done"]))
    grid = perforant.grid_settings()
    out = {}
    for name in grid:
        conditions = {}
        for r in records:
            for lv, store in zip(r["levels"], r["per_seed"]):
                label = "{} {} {:g}".format(r["args"]["task"], lv["kind"], lv["level"])
                vals = [mean(store["{} {} {}".format(name, arm, d)])
                        for arm in ("none", "settle") for d in DIRECTIONS]
                conditions[label] = mean(vals)
        out[name] = (mean(conditions.values()), conditions)
    return grid, out


def flags(rule, kw):
    tag = "wil" if rule == "willshaw" else "cov"
    parts = []
    if rule == "willshaw" and kw["presynaptic"] != "positive":
        parts.append("--wil-presynaptic {}".format(kw["presynaptic"]))
    if kw["normalise"]:
        parts.append("--{}-normalise".format(tag))
    if kw["emax"] is not None:
        parts.append("--{}-emax {:g}".format(tag, kw["emax"]))
    return " ".join(parts)


def select():
    grid, scores = grid_scores()
    lines = ["| Setting | Score | " + " | ".join(next(iter(scores.values()))[1]) + " |"]
    lines.append("|" + "---|" * (2 + len(next(iter(scores.values()))[1])))
    chosen = {}
    for rule in ("willshaw", "covariance"):
        names = [n for n in grid if grid[n][0] == rule]
        best = max(names, key=lambda n: (round(scores[n][0], 10), [-x for x in simplicity(n, grid[n])]))
        chosen[rule] = best
        for n in sorted(names, key=lambda n: -scores[n][0]):
            row = [n + (" (chosen)" if n == best else ""), "{:.4f}".format(scores[n][0])]
            row += ["{:.3f}".format(v) for v in scores[n][1].values()]
            lines.append("| " + " | ".join(row) + " |")
    print("\n".join(lines))
    print()
    print('WIL="{}" COV="{}"'.format(flags(*grid[chosen["willshaw"]]), flags(*grid[chosen["covariance"]])))
    return chosen


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--select", action="store_true")
    args = p.parse_args(argv)
    if args.select:
        select()
        return
    raise SystemExit("Tables come after the runs.")


if __name__ == "__main__":
    main()
