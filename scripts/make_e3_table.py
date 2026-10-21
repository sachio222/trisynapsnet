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


ARM_NAMES = {
    "pr_none": "PR, no settling",
    "pr_cov": "PR, covariance CA3",
    "pr_wil": "PR, clipped binary CA3",
    "pp_cov_none": "Perforant, covariance, no settling",
    "pp_cov": "Perforant, covariance, settling",
    "pp_wil_none": "Perforant, clipped binary, no settling",
    "pp_wil": "Perforant, clipped binary, settling",
}
SHORT = {"study-to-test": "S→T", "test-to-study": "T→S"}
PAIRS = (("pp_cov", "pp_cov_none"), ("pp_wil", "pp_wil_none"), ("pr_cov", "pr_none"),
         ("pr_wil", "pr_none"))


def pct(store, key):
    v = store[key]
    m = statistics.mean(v)
    sd = statistics.stdev(v) if len(v) > 1 else 0.0
    return "{:.1f} ± {:.1f}".format(100 * m, 100 * sd)


def level_label(lv):
    return "clean" if lv["kind"] == "none" else "{} {:g}".format(lv["kind"], lv["level"])


def seeds_note(rec):
    n = len(rec["seeds_done"])
    return "{} seeds{}".format(n, "" if rec["complete"] else ", unfinished")


def stage_table(rec, level=0, arms=tuple(ARM_NAMES)):
    """Every arm at every stage, both directions, one level."""
    store = rec["per_seed"][level]
    cols = [(st, d) for st in ("ca3", "ca1", "pm") for d in DIRECTIONS]
    head = ["Arm"] + ["{} {}".format({"ca3": "CA3", "ca1": "CA1", "pm": "PM"}[st], SHORT[d])
                      for st, d in cols]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for d_ref in (("vc", "Vision code alone"), ("pr", "PR output, before CA3")):
        row = [d_ref[1]] + ["" for _ in cols]
        for i, (st, d) in enumerate(cols):
            if st == "ca3":
                row[i + 1] = pct(store, "{} {}".format(d_ref[0], d))
        lines.append("| " + " | ".join(row) + " |")
    for arm in arms:
        row = [ARM_NAMES[arm]] + [pct(store, "{} {} {}".format(arm, st, d)) for st, d in cols]
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def level_table(rec, stage, direction, arms=tuple(ARM_NAMES)):
    """Every arm at every level, one stage and direction."""
    labels = [level_label(lv) for lv in rec["levels"]]
    lines = ["| Arm | " + " | ".join(labels) + " |", "|" + "---|" * (1 + len(labels))]
    for arm in arms:
        row = [ARM_NAMES[arm]] + [pct(store, "{} {} {}".format(arm, stage, direction))
                                  for store in rec["per_seed"]]
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def effect_table(rec, stage="ca3", direction="test-to-study"):
    """Settling minus no settling, per seed: mean, range, seeds where it helps."""
    labels = [level_label(lv) for lv in rec["levels"]]
    lines = ["| Pair | " + " | ".join(labels) + " |", "|" + "---|" * (1 + len(labels))]
    for a, b in PAIRS:
        row = ["{} minus no settling".format(ARM_NAMES[a])]
        for store in rec["per_seed"]:
            diffs = [100 * (x - y) for x, y in zip(store["{} {} {}".format(a, stage, direction)],
                                                  store["{} {} {}".format(b, stage, direction)])]
            row.append("{:+.1f} [{:+.1f}, {:+.1f}] {}/{}".format(
                statistics.mean(diffs), min(diffs), max(diffs), sum(x > 0 for x in diffs),
                len(diffs)))
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def cue_table(rec, level=0, arms=tuple(ARM_NAMES)):
    """Cue and final-state quality against the right stored pattern."""
    store = rec["per_seed"][level]
    metrics = (("active_cue", "Cells in cue", 1), ("overlap_cue", "Right cells in cue", 100),
               ("stray_cue", "Stray cells in cue", 100), ("ident_cue", "Lookup from cue", 100),
               ("overlap_final", "Right cells, final", 100),
               ("stray_final", "Stray cells, final", 100), ("exact", "Exact recall", 100))
    lines = ["| Arm | " + " | ".join(m[1] for m in metrics) + " |",
             "|" + "---|" * (1 + len(metrics))]
    for arm in arms:
        row = [ARM_NAMES[arm]]
        for key, _, scale in metrics:
            v = statistics.mean(store["{} {}".format(arm, key)])
            row.append("{:.2f}".format(v) if scale == 1 else "{:.1f}".format(scale * v))
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def load_table(records, stage, direction, arms, kind):
    """One row per load and arm, columns the clean level and one corruption kind."""
    first = next(r for r in records.values() if r)
    idx = [i for i, lv in enumerate(first["levels"]) if lv["kind"] in ("none", kind)]
    labels = [level_label(first["levels"][i]) for i in idx]
    lines = ["| Load | Arm | " + " | ".join(labels) + " |", "|" + "---|" * (2 + len(labels))]
    for load_n, rec in records.items():
        if rec is None:
            lines.append("| {} | not run | ".format(load_n) + " | ".join("" for _ in labels) + " |")
            continue
        for arm in arms:
            row = [str(load_n), ARM_NAMES[arm]] + [
                pct(rec["per_seed"][i], "{} {} {}".format(arm, stage, direction)) for i in idx]
            lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def load_effect_table(records, stage, direction, kind, pairs=PAIRS[:3]):
    """Settling minus no settling per load: mean over seeds, seeds where it helps."""
    first = next(r for r in records.values() if r)
    idx = [i for i, lv in enumerate(first["levels"]) if lv["kind"] in ("none", kind)]
    labels = [level_label(first["levels"][i]) for i in idx]
    lines = ["| Load | Pair | " + " | ".join(labels) + " |", "|" + "---|" * (2 + len(labels))]
    for load_n, rec in records.items():
        if rec is None:
            continue
        for a, b in pairs:
            row = [str(load_n), ARM_NAMES[a]]
            for i in idx:
                store = rec["per_seed"][i]
                diffs = [100 * (x - y) for x, y in zip(store["{} {} {}".format(a, stage, direction)],
                                                      store["{} {} {}".format(b, stage, direction)])]
                row.append("{:+.1f} ({}/{})".format(statistics.mean(diffs),
                                                    sum(x > 0 for x in diffs), len(diffs)))
            lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def load_metric_table(records, metric, arms, kind):
    first = next(r for r in records.values() if r)
    idx = [i for i, lv in enumerate(first["levels"]) if lv["kind"] in ("none", kind)]
    labels = [level_label(first["levels"][i]) for i in idx]
    lines = ["| Load | Arm | " + " | ".join(labels) + " |", "|" + "---|" * (2 + len(labels))]
    for load_n, rec in records.items():
        if rec is None:
            continue
        for arm in arms:
            row = [str(load_n), ARM_NAMES[arm]] + [
                "{:.1f}".format(100 * statistics.mean(rec["per_seed"][i]["{} {}".format(arm, metric)]))
                for i in idx]
            lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def ca1_gap(rec):
    """Largest |CA1 - CA3| over arms, levels and directions, in points."""
    worst = (0.0, None)
    for lv, store in zip(rec["levels"], rec["per_seed"]):
        for arm in ARM_NAMES:
            for d in DIRECTIONS:
                g = 100 * (statistics.mean(store["{} ca1 {}".format(arm, d)])
                           - statistics.mean(store["{} ca3 {}".format(arm, d)]))
                if abs(g) > abs(worst[0]):
                    worst = (g, (level_label(lv), arm, d))
    return worst


def gap_table(recs):
    """CA1 minus CA3 for each arm: the largest gap over levels and directions."""
    lines = ["| Arm | " + " | ".join(recs) + " |", "|" + "---|" * (1 + len(recs))]
    for arm in ARM_NAMES:
        row = [ARM_NAMES[arm]]
        for rec in recs.values():
            worst = 0.0
            for store in rec["per_seed"]:
                for d in DIRECTIONS:
                    g = 100 * (statistics.mean(store["{} ca1 {}".format(arm, d)])
                               - statistics.mean(store["{} ca3 {}".format(arm, d)]))
                    worst = g if abs(g) > abs(worst) else worst
            row.append("{:+.1f}".format(worst))
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def hours(names):
    total = sum(load(n)["seconds"] for n in names if load(n))
    return total / 3600


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--select", action="store_true")
    p.add_argument("--dump", action="store_true", help="print every table whose files exist")
    args = p.parse_args(argv)
    if args.select:
        select()
        return
    if args.dump:
        print(dump())
        return
    raise SystemExit("Tables come after the runs.")


def dump(k=5):
    """Every table whose result files exist, for reading during the runs."""
    out = []
    for runs in ("background", "official"):
        rec = load("e3_classification_{}_225_{}".format(runs, k))
        if rec:
            out += ["## Classification, {} runs ({})".format(runs, seeds_note(rec)), "",
                    stage_table(rec), "", cue_table(rec), ""]
        rec = load("e3_instance_{}_225_{}".format(runs, k))
        if rec:
            out += ["## Instance, {} ({})".format(runs, seeds_note(rec))]
            for d in DIRECTIONS:
                for stage in ("ca3", "ca1"):
                    out += ["", "{} {}".format(stage, d), "", level_table(rec, stage, d)]
            out += ["", "Settling effect, CA3, test-to-study", "", effect_table(rec), "",
                    "Settling effect, CA3, study-to-test", "", effect_table(rec, "ca3", "study-to-test"),
                    "", "Settling effect, CA1, test-to-study", "", effect_table(rec, "ca1"),
                    "", "Settling effect, CA1, study-to-test", "", effect_table(rec, "ca1", "study-to-test")]
            for i, lv in enumerate(rec["levels"]):
                out += ["", "Cue quality, " + level_label(lv), "", cue_table(rec, i)]
            out += ["", "CA1 gap {}".format(ca1_gap(rec)), ""]
    recs = {name: load(name) for name in ("e3_classification_official_225_{}".format(k),
                                          "e3_instance_official_225_{}".format(k))}
    recs = {n: r for n, r in recs.items() if r}
    if recs:
        out += ["## Largest CA1 minus CA3 gap per arm", "", gap_table(recs), ""]
    loads = {n: load("e3_load_official_n{}_225_{}".format(n, k)) for n in (20, 50, 100, 200)}
    if any(loads.values()):
        arms = ("pr_none", "pr_cov", "pp_cov_none", "pp_cov", "pp_wil_none", "pp_wil")
        for kind in ("occlusion", "noise"):
            for d in DIRECTIONS:
                out += ["## Load, CA3, {} {}".format(kind, d), "",
                        load_table(loads, "ca3", d, arms, kind), ""]
            for d in DIRECTIONS:
                out += ["## Load, CA1, {} {}".format(kind, d), "",
                        load_table(loads, "ca1", d, arms, kind), ""]
            for stage in ("ca3", "ca1"):
                out += ["## Load, settling effect, {}, {} test-to-study".format(stage, kind), "",
                        load_effect_table(loads, stage, "test-to-study", kind), ""]
            out += ["## Load, exact recall, {}".format(kind), "",
                    load_metric_table(loads, "exact", arms, kind), "",
                    "## Load, right cells in cue, {}".format(kind), "",
                    load_metric_table(loads, "overlap_cue", arms, kind), ""]
    return "\n".join(out)


if __name__ == "__main__":
    main()
