"""Builds E8b's calibration, tables and figures from results/e8b_*.json.

    python scripts/make_e8b_table.py --calibrate   thresholds from the
                                                   background runs only
    python scripts/make_e8b_table.py               scores, tables in
                                                   results/e8b.md, figures

--calibrate reads the background result files and writes
results/e8b_calibration.json: for each readout (R1, the comparator; R2,
CA3's self-support) and each arm, the two thresholds that give young
adults' p(old | repeat) and p(new | foil) on the background lists at the
human list length (128 drawings); and, for the intact model and the
vision-code baseline, the same two thresholds set again at every other
load (per-load recalibration, the secondary score). E8's lure-bin edges
are reused for the other-drawer lures.

The default run scores every e8b result file and writes
results/e8b_scores.json, the tables in results/e8b.md below the line
"## Tables" (text above it is kept), and the figures:
    figures/e8b_ldi_by_level.pdf   LDI by lure level, both lure sets, both
                                   readouts, every arm
    figures/e8b_old_by_level.pdf   p(old | lure) by level, both readouts
    figures/e8b_load.pdf           LDI and REC against load, both readouts,
                                   fixed and per-load thresholds

Two lure sets share each list's repeats and foils: "drawer" lures are
another person's drawing of a studied character (E8's set, binned L1 to
L5 by vision-code similarity with E8's edges), "closer" lures are the
studied drawing itself, distorted at five levels C1 (most similar) to C5.

Values are means over seeds; the numbers after ± are one standard
deviation over seeds.
"""

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import torch  # noqa: E402

from trisynapsnet.eval import behaviour as bh  # noqa: E402

RESULTS = REPO / "results"
FIGURES = REPO / "figures"
CALIBRATION = RESULTS / "e8b_calibration.json"
SCORES = RESULTS / "e8b_scores.json"
E8_CALIBRATION = RESULTS / "e8_calibration.json"
LEVELS = RESULTS / "e8b_lure_levels.json"

P_OLD_REPEAT, P_NEW_FOIL = 0.812, 0.820
# Stark, Yassa, Lacy and Stark 2013, Table 2, ages 20 to 39 (N = 26).
YOUNG = {"repeat": {"old": 0.812, "similar": 0.117, "new": 0.041},
         "lure": {"old": 0.403, "similar": 0.476, "new": 0.083},
         "foil": {"old": 0.026, "similar": 0.116, "new": 0.820}}
YOUNG_LDI, YOUNG_REC, YOUNG_OLD_LURE = 0.360, 0.786, 0.403
# Same table, ages 60 to 74 (N = 29).
OLDER = {"repeat": {"old": 0.822, "similar": 0.076, "new": 0.053},
         "lure": {"old": 0.546, "similar": 0.236, "new": 0.123},
         "foil": {"old": 0.048, "similar": 0.123, "new": 0.734}}

HUMAN_LOAD = 128
LOADS = (20, 50, 100, 128, 200, 256)
PER_CHAR = (1, 2, 4)
READOUTS = ("r1", "r2")
READOUT_NAMES = {"r1": "R1 (CA1 comparator)", "r2": "R2 (CA3 self-support)"}
SETS = ("drawer", "close")
SET_NAMES = {"drawer": "other-drawer lures, bins L1 to L5",
             "close": "closer lures, levels C1 to C5"}
ARM_NAMES = {
    "intact": "Intact",
    "no_recurrent": "No CA3 recurrent connections",
    "no_ca3": "No CA3 (EC to CA1 only)",
    "no_dg": "No DG",
    "pp_keep0.75": "Perforant path, 75% kept",
    "pp_keep0.5": "Perforant path, 50% kept",
    "pp_keep0.25": "Perforant path, 25% kept",
    "vc_baseline": "Vision code alone (baseline)",
    "no_hippocampus": "No hippocampus",
}
LESION_ARMS = ("intact", "no_recurrent", "no_ca3", "no_dg", "pp_keep0.75", "pp_keep0.5",
               "pp_keep0.25", "vc_baseline", "no_hippocampus")
SHARED = ("intact", "no_recurrent", "no_ca3", "vc_baseline")
# Arms with no R2 signal: no recurrent synapses, or no CA3.
NO_R2 = ("no_recurrent", "no_ca3")


def name(split, load, d):
    return "e8b_{}_n{}_d{}".format(split, load, d)


def load_file(split, load, d):
    path = RESULTS / (name(split, load, d) + ".json")
    return json.loads(path.read_text()) if path.is_file() else None


def floats(values):
    return torch.tensor([float("nan") if v is None else v for v in values], dtype=torch.float64)


def pooled(record, key, readout=None, arm=None):
    out = []
    for seed in sorted(record["per_seed"], key=int):
        items = record["per_seed"][seed]
        out += items["signal"][readout][arm] if arm else items[key]
    return out


# ---------------------------------------------------------------- calibration

def recalibrate_by_load(by_load, p_old_repeat=P_OLD_REPEAT, p_new_foil=P_NEW_FOIL):
    """Thresholds set again at each load: {load: (signal, types)} -> {load: thresholds}.

    The secondary score: a person's criterion adapts to the list, so each
    load gets thresholds that give young adults' two rates on background
    runs at that load.
    """
    out = {}
    for load, (signal, types) in by_load.items():
        signal, types = torch.as_tensor(signal), torch.as_tensor(types)
        out[load] = bh.calibrate(signal[types == 0], signal[types == 2], p_old_repeat, p_new_foil)
    return out


def arm_thresholds(record, readout, arm):
    types = torch.tensor(pooled(record, "types"))
    s = floats(pooled(record, None, readout, arm))
    return bh.calibrate(s[types == 0], s[types == 2], P_OLD_REPEAT, P_NEW_FOIL)


def calibrate():
    main = load_file("background", HUMAN_LOAD, 1)
    if main is None or not main["complete"]:
        raise SystemExit("results/{}.json is missing or incomplete".format(
            name("background", HUMAN_LOAD, 1)))
    out = {"source": "results/{}.json".format(name("background", HUMAN_LOAD, 1)),
           "seeds": main["seeds_done"],
           "targets": {"p_old_repeat": P_OLD_REPEAT, "p_new_foil": P_NEW_FOIL},
           "thresholds": {r: {} for r in READOUTS}, "by_load": {r: {} for r in READOUTS},
           "bin_edges": json.loads(E8_CALIBRATION.read_text())["bin_edges"]}
    for r in READOUTS:
        for arm in main["args"]["arms"]:
            if r == "r2" and arm in NO_R2:
                continue
            out["thresholds"][r][arm] = arm_thresholds(main, r, arm)
        for load in LOADS:
            for d in PER_CHAR:
                rec = load_file("background", load, d)
                if rec is None or (load, d) == (HUMAN_LOAD, 1):
                    continue
                key = "n{}_d{}".format(load, d)
                out["by_load"][r][key] = {arm: arm_thresholds(rec, r, arm)
                                          for arm in ("intact", "vc_baseline")}
    CALIBRATION.write_text(json.dumps(out, indent=1))
    for r in READOUTS:
        for arm, thr in out["thresholds"][r].items():
            print("{} {:14s} old {:.4f} (q {:.3f})  new {:.4f} (q {:.3f})  feasible {}".format(
                r, arm, thr["old"], thr["q_old"], thr["new"], thr["q_new"], thr["feasible"]))
    return out


# ---------------------------------------------------------------- scoring

def thresholds_for(cal, readout, arm, mode="fixed", condition=None):
    """mode fixed: the intact model's thresholds at 128 drawings (the
    baseline keeps its own); own: the arm's own; load: the intact model's
    (or baseline's) thresholds set at this condition."""
    thr = cal["thresholds"][readout]
    if mode == "load" and condition in cal["by_load"][readout]:
        by = cal["by_load"][readout][condition]
        return by["vc_baseline"] if arm == "vc_baseline" else by["intact"]
    if arm == "vc_baseline" or (mode == "own" and arm in thr):
        return thr[arm]
    return thr["intact"]


def lure_set(items, which, edges):
    """(types, bins, keep) for one lure set: drawer lures keep types 0-2 and
    take E8's bins; closer lures become type 1 and take their level."""
    types = torch.tensor(items["types"])
    if which == "drawer":
        keep = types < 3
        bins = bh.bin_of(floats(items["similarity"]), edges)
    else:
        keep = types != 1
        types = torch.where(types == 3, torch.ones_like(types), types)
        bins = torch.tensor(items["level"])
    return types, bins, keep


def nanmean(x):
    x = x[~torch.isnan(x)] if x.is_floating_point() else x
    return x.double().mean().item() if len(x) else float("nan")


def seed_scores(items, readout, arm, thr, edges, which):
    types, bins, keep = lure_set(items, which, edges)
    s = floats(items["signal"][readout][arm])
    types, bins, s = types[keep], bins[keep], s[keep]
    r = bh.rates(s, types, thr)
    p = bh.respond(s, thr)
    out = {"rates": r, "ldi": bh.ldi(r), "rec": bh.rec(r),
           "ldi_bins": bh.ldi_by_bin(s, types, bins, thr),
           "sim_bins": [nanmean(p[(types == 1) & (bins == b), 1]) for b in range(1, 6)],
           "old_bins": [nanmean(p[(types == 1) & (bins == b), 0]) for b in range(1, 6)],
           "median": {t: nanmean(s[types == i].median().reshape(1)) if (types == i).any()
                      else float("nan") for i, t in enumerate(("repeat", "lure", "foil"))}}
    ca3 = items.get("ca3", {}).get(arm)
    if ca3:
        ep = torch.tensor(ca3["exact_paired"])[keep].double()
        ea = torch.tensor(ca3["exact_any"])[keep].double()
        no = floats(ca3["nearest_overlap"])[keep]
        cs = floats(ca3["cue_support"])[keep]
        lures = types == 1
        out["ca3"] = {"repeat_exact": nanmean(ep[types == 0]), "lure_exact": nanmean(ep[lures]),
                      "foil_any": nanmean(ea[types == 2]),
                      "cue_cells": nanmean(torch.tensor(ca3["cue_cells"])[keep].double()),
                      "lure_exact_bins": [nanmean(ep[lures & (bins == b)]) for b in range(1, 6)],
                      "overlap": {t: nanmean(no[types == i])
                                  for i, t in enumerate(("repeat", "lure", "foil"))},
                      "cue_support": {t: nanmean(cs[types == i])
                                      for i, t in enumerate(("repeat", "lure", "foil"))},
                      # p(old | lure) among lures that did and did not settle
                      # onto the studied drawing's pattern.
                      "old_if_exact": nanmean(p[lures & (ep == 1), 0]),
                      "old_if_not": nanmean(p[lures & (ep == 0), 0])}
    return out


def no_hippocampus(n_bins=5):
    zero = {"old": 0.0, "similar": 0.0, "new": 1.0}
    return {"rates": {t: dict(zero) for t in bh.TYPES}, "ldi": 0.0, "rec": 0.0,
            "ldi_bins": [0.0] * n_bins, "sim_bins": [0.0] * n_bins, "old_bins": [0.0] * n_bins}


def flatten(score, prefix=""):
    out = {}
    for key, value in score.items():
        if isinstance(value, dict):
            out.update(flatten(value, prefix + key + " "))
        elif isinstance(value, list):
            for i, v in enumerate(value):
                out["{}{} {}".format(prefix, key, i + 1)] = v
        else:
            out[prefix + key] = value
    return out


def summarise(values):
    vals = [v for v in values if not (isinstance(v, float) and math.isnan(v))]
    if not vals:
        return {"mean": float("nan"), "std": float("nan"), "values": values}
    return {"mean": statistics.mean(vals), "std": statistics.stdev(vals) if len(vals) > 1 else 0.0,
            "values": values}


def score_record(record, cal, readout, which, mode="fixed", condition=None):
    """{arm: {flat key: summary over seeds}} for one file, readout and lure set."""
    out = {}
    for arm in record["args"]["arms"]:
        if mode == "own" and readout == "r2" and arm in NO_R2:
            continue
        thr = thresholds_for(cal, readout, arm, mode, condition)
        per_seed = [flatten(seed_scores(record["per_seed"][s], readout, arm, thr,
                                        cal["bin_edges"], which))
                    for s in sorted(record["per_seed"], key=int)]
        out[arm] = {key: summarise([p[key] for p in per_seed]) for key in per_seed[0]}
    flat = flatten(no_hippocampus())
    out["no_hippocampus"] = {key: summarise([v] * len(record["per_seed"])) for key, v in flat.items()}
    return out


# ---------------------------------------------------------------- tables

def pct(summary, digits=1):
    m = summary["mean"] if summary else float("nan")
    if isinstance(m, float) and math.isnan(m):
        return ""
    return "{:.{d}f} ± {:.{d}f}".format(100 * m, 100 * summary["std"], d=digits)


def num(summary, digits=3):
    m = summary["mean"] if summary else float("nan")
    if isinstance(m, float) and math.isnan(m):
        return ""
    return "{:.{d}f} ± {:.{d}f}".format(m, summary["std"], d=digits)


def mean(s, key):
    return s[key]["mean"]


def seeds_where(a, b, test):
    pairs = list(zip(a["values"], b["values"]))
    return sum(1 for x, y in pairs if test(x, y)), len(pairs)


def bin_label(which, b):
    return ("L{}" if which == "drawer" else "C{}").format(b)


def score_table(scores, arms, which, human=True):
    rows = ["| Arm | LDI | REC | p(old \\| lure) | " + " | ".join(
        "LDI {}".format(bin_label(which, b)) for b in range(1, 6)) + " |", "|---|" + "---|" * 8]
    if human:
        rows.append("| Young adults (Stark and colleagues 2013) | 0.360 | 0.786 | 0.403 |"
                    + " not in text |" * 5)
    for arm in arms:
        if arm not in scores:
            continue
        s = scores[arm]
        rows.append("| {} | {} | {} | {} | ".format(
            ARM_NAMES[arm], num(s["ldi"]), num(s["rec"]), num(s["rates lure old"]))
            + " | ".join(num(s["ldi_bins {}".format(b)]) for b in range(1, 6)) + " |")
    return "\n".join(rows)


def rate_by_level_table(scores, arms, which, key):
    rows = ["| Arm | " + " | ".join(bin_label(which, b) for b in range(1, 6)) + " |",
            "|---|" + "---|" * 5]
    for arm in arms:
        if arm in scores:
            rows.append("| {} | ".format(ARM_NAMES[arm]) + " | ".join(
                pct(scores[arm]["{} {}".format(key, b)]) for b in range(1, 6)) + " |")
    return "\n".join(rows)


def response_table(scores, arms, human=None):
    rows = ["| Arm | " + " | ".join("{} to {}".format(resp, t) for t in bh.TYPES
                                     for resp in ("old", "similar", "new")) + " |",
            "|---|" + "---|" * 9]
    for label, h in human or []:
        rows.append("| {} | ".format(label) + " | ".join(
            "{:.1f}".format(100 * h[t][r]) for t in bh.TYPES for r in ("old", "similar", "new"))
            + " |")
    for arm in arms:
        if arm in scores:
            s = scores[arm]
            rows.append("| {} | ".format(ARM_NAMES[arm]) + " | ".join(
                pct(s["rates {} {}".format(t, r)]) for t in bh.TYPES
                for r in ("old", "similar", "new")) + " |")
    return "\n".join(rows)


def ca3_table(scores, arms, which):
    rows = ["| Arm | Cue cells | Repeats on their pattern | Lures on the studied pattern | "
            "Foils on a stored pattern | " + " | ".join(
                "Lures on studied pattern, {}".format(bin_label(which, b)) for b in range(1, 6))
            + " | Nearest-pattern overlap, repeats / lures / foils (logged only) |",
            "|---|" + "---|" * 10]
    for arm in arms:
        if arm not in scores or "ca3 cue_cells" not in scores[arm]:
            continue
        s = scores[arm]
        rows.append("| {} | {} | {} | {} | {} | ".format(
            ARM_NAMES[arm], num(s["ca3 cue_cells"], 2), pct(s["ca3 repeat_exact"]),
            pct(s["ca3 lure_exact"]), pct(s["ca3 foil_any"]))
            + " | ".join(pct(s["ca3 lure_exact_bins {}".format(b)]) for b in range(1, 6))
            + " | {} / {} / {} |".format(*("{:.3f}".format(mean(s, "ca3 overlap " + t))
                                          for t in ("repeat", "lure", "foil"))))
    return "\n".join(rows)


def condition_table(all_scores, conditions, arms, readout, which, mode):
    rows = ["| Condition | Arm | LDI | REC | p(old \\| repeat) | p(similar \\| lure) | "
            "p(old \\| lure) | p(old \\| foil) | Lures on studied pattern |",
            "|---|---|---|---|---|---|---|---|---|"]
    for label, key in conditions:
        scores = all_scores.get((key, readout, which, mode))
        if not scores:
            continue
        for arm in arms:
            if arm not in scores:
                continue
            s = scores[arm]
            rows.append("| {} | {} | {} | {} | {} | {} | {} | {} | {} |".format(
                label, ARM_NAMES[arm], num(s["ldi"]), num(s["rec"]), pct(s["rates repeat old"]),
                pct(s["rates lure similar"]), pct(s["rates lure old"]), pct(s["rates foil old"]),
                pct(s["ca3 lure_exact"]) if "ca3 lure_exact" in s else ""))
    return "\n".join(rows)


def monotone(values, falling_with_level, tol=0.05):
    """values by level 1 (most similar) to 5; falling_with_level: level 1
    above level 5 and no step to a less similar level rises by more than tol;
    otherwise the mirror image."""
    steps = [values[i + 1] - values[i] for i in range(len(values) - 1)]
    if falling_with_level:
        return values[0] > values[-1] and max(steps) <= tol
    return values[-1] > values[0] and min(steps) >= -tol


def predictions(main, d4):
    """Each prediction, scored as docs/e8b_protocol.md fixes it, on means
    over seeds at 128 drawings with fixed thresholds."""
    out = []
    r2c, r2d = main[("r2", "close")], main[("r2", "drawer")]
    r1c, r1d = main[("r1", "close")], main[("r1", "drawer")]
    i2 = r2c["intact"]
    old = [mean(i2, "old_bins {}".format(b)) for b in range(1, 6)]
    settle = mean(i2, "ca3 lure_exact")
    p_old = mean(i2, "rates lure old")
    a = abs(p_old - settle) <= 0.10
    b = monotone(old, falling_with_level=True)
    c = abs(p_old - YOUNG_OLD_LURE) <= 0.15
    out.append(("1", a and b and c,
                "closer lures, R2: p(old | lure) {:.3f} against {:.3f} settling onto the studied "
                "pattern ({}); by level C1 to C5 {} ({}); against young adults' 0.403 ({})".format(
                    p_old, settle, "within 0.10" if a else "not within 0.10",
                    ", ".join("{:.3f}".format(x) for x in old), "falls" if b else "does not fall",
                    "within 0.15" if c else "not within 0.15")))
    for which, r2s, r1s in (("close", r2c, r1c), ("drawer", r2d, r1d)):
        l2 = [mean(r2s["intact"], "ldi_bins {}".format(k)) for k in range(1, 6)]
        l1 = [mean(r1s["intact"], "ldi_bins {}".format(k)) for k in range(1, 6)]
        h2 = monotone(l2, falling_with_level=False)
        h1 = l1[0] > l1[-1]
        out.append(("2 ({})".format("closer lures, scored" if which == "close"
                                    else "other-drawer lures, reported"),
                    h2 and h1,
                    "R2 LDI {} to {}: {} ({}); R1: {} ({})".format(
                        bin_label(which, 1), bin_label(which, 5),
                        ", ".join("{:.3f}".format(x) for x in l2),
                        "rises toward less similar lures" if h2 else "not the human direction",
                        ", ".join("{:.3f}".format(x) for x in l1),
                        "highest at the most similar" if h1 else "not highest at the most similar")))
    rec1, rec2 = mean(r1d["intact"], "rec"), mean(r2d["intact"], "rec")
    out.append(("3", rec1 >= 0.6 and rec2 >= 0.6,
                "REC {:.3f} (R1) and {:.3f} (R2)".format(rec1, rec2)))
    o_int = mean(i2, "rates lure old")
    o_nr = mean(r2c["no_recurrent"], "rates lure old")
    o_dg = mean(r2c["no_dg"], "rates lure old")
    held4 = o_int > 0 and o_nr <= 0.5 * o_int and o_dg > o_int
    out.append(("4", held4, "closer lures, R2: p(old | lure) intact {:.3f}, without recurrent "
                "connections {:.3f} (no R2 signal by construction), without DG {:.3f}".format(
                    o_int, o_nr, o_dg)))
    for keep in ("0.75", "0.5", "0.25"):
        t = mean(r2c["pp_keep" + keep], "rates lure old")
        out.append(("5 ({}% kept)".format(int(float(keep) * 100)), t < o_int,
                    "closer lures, R2: p(old | lure) {:.3f} against intact {:.3f}; lures settling "
                    "on the studied pattern {:.1%} against {:.1%}".format(
                        t, o_int, mean(r2c["pp_keep" + keep], "ca3 lure_exact"), settle)))
    if d4:
        l = {r: mean(d4[(r, "drawer")]["intact"], "ldi") for r in READOUTS}
        base = mean(d4[("r1", "drawer")]["vc_baseline"], "ldi")
        out.append(("6", max(l.values()) > base,
                    "4 drawings per character, other-drawer lures: intact LDI {:.3f} (R1), {:.3f} "
                    "(R2); vision code alone {:.3f}".format(l["r1"], l["r2"], base)))
    return out


# ---------------------------------------------------------------- figures

def figures(main, loads, loads_own):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker

    FIGURES.mkdir(exist_ok=True)
    arms = ("intact", "no_recurrent", "no_ca3", "no_dg", "pp_keep0.75", "pp_keep0.5",
            "pp_keep0.25", "vc_baseline")
    x = list(range(1, 6))
    for key, fname, ylabel, human in (
            ("ldi_bins", "e8b_ldi_by_level.pdf", "LDI = p(similar | lure) − p(similar | foil)",
             (YOUNG_LDI, "Young adults, all lures (0.360)")),
            ("old_bins", "e8b_old_by_level.pdf", "p(old | lure)",
             (YOUNG_OLD_LURE, "Young adults, all lures (0.403)"))):
        fig, axes = plt.subplots(2, 2, figsize=(11, 7.5), sharey=True)
        for i, r in enumerate(READOUTS):
            for j, which in enumerate(SETS):
                ax = axes[i][j]
                sc = main[(r, which)]
                for arm in arms:
                    if arm not in sc or (r == "r2" and arm in NO_R2 and key == "ldi_bins"
                                         and False):
                        continue
                    m = [sc[arm]["{} {}".format(key, b)]["mean"] for b in x]
                    sd = [sc[arm]["{} {}".format(key, b)]["std"] for b in x]
                    style = {"vc_baseline": "--", "intact": "-"}.get(arm, ":")
                    line, = ax.plot(x, m, style, marker="o", ms=3, label=ARM_NAMES[arm],
                                    lw=2 if arm == "intact" else 1.2)
                    ax.fill_between(x, [a - b for a, b in zip(m, sd)],
                                    [a + b for a, b in zip(m, sd)], color=line.get_color(),
                                    alpha=0.12)
                ax.axhline(human[0], color="k", lw=0.8, ls="-.", label=human[1])
                ax.set_xticks(x)
                ax.set_xticklabels([bin_label(which, 1) + "\nmost similar", bin_label(which, 2),
                                    bin_label(which, 3), bin_label(which, 4),
                                    bin_label(which, 5) + "\nleast similar"])
                ax.set_title("{}, {}".format(READOUT_NAMES[r], SET_NAMES[which]), fontsize=9)
                if j == 0:
                    ax.set_ylabel(ylabel)
        axes[0][1].legend(fontsize=7, loc="upper left", bbox_to_anchor=(1.01, 1.0))
        fig.suptitle("Evaluation alphabets, 128 drawings, fixed thresholds", fontsize=10)
        fig.tight_layout()
        fig.savefig(FIGURES / fname)
        plt.close(fig)

    have = sorted(loads)
    if not have:
        return
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), sharex=True)
    for i, r in enumerate(READOUTS):
        for j, key in enumerate(("ldi", "rec")):
            ax = axes[i][j]
            for arm, mode, src, style in (("intact", "fixed", loads, "-"),
                                          ("intact", "per-load", loads_own, "-."),
                                          ("vc_baseline", "fixed", loads, "--")):
                pts = [n for n in have if n in src and arm in src[n][r]]
                m = [src[n][r][arm][key]["mean"] for n in pts]
                sd = [src[n][r][arm][key]["std"] for n in pts]
                line, = ax.plot(pts, m, style, marker="o", ms=3,
                                label="{}, {} thresholds".format(ARM_NAMES[arm], mode))
                ax.fill_between(pts, [a - b for a, b in zip(m, sd)],
                                [a + b for a, b in zip(m, sd)], color=line.get_color(), alpha=0.12)
            ax.axhline(YOUNG_LDI if key == "ldi" else YOUNG_REC, color="k", lw=0.8, ls=":",
                       label="Young adults at 128")
            ax.axvline(HUMAN_LOAD, color="grey", lw=0.6)
            ax.set_xscale("log")
            ax.set_xticks(have)
            ax.set_xticklabels([str(n) for n in have])
            ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
            ax.set_title("{}: {}".format(READOUT_NAMES[r], key.upper()), fontsize=9)
            if i == 1:
                ax.set_xlabel("Drawings studied per list")
    axes[0][0].legend(fontsize=7)
    fig.suptitle("Evaluation alphabets, other-drawer lures, one drawing per character",
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(FIGURES / "e8b_load.pdf")
    plt.close(fig)


# ---------------------------------------------------------------- main

def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--calibrate", action="store_true")
    args = p.parse_args()
    if args.calibrate:
        calibrate()
        return
    cal = json.loads(CALIBRATION.read_text())
    all_scores = {}
    files = {}
    for split in bh.SPLITS:
        for load in LOADS:
            for d in PER_CHAR:
                record = load_file(split, load, d)
                if record is None:
                    continue
                key = name(split, load, d)
                files[key] = record
                cond = "n{}_d{}".format(load, d)
                for r in READOUTS:
                    for which in SETS:
                        all_scores[(key, r, which, "fixed")] = score_record(record, cal, r, which)
                        if (load, d) == (HUMAN_LOAD, 1):
                            all_scores[(key, r, which, "own")] = score_record(
                                record, cal, r, which, "own")
                        else:
                            all_scores[(key, r, which, "load")] = score_record(
                                record, cal, r, which, "load", cond)
    SCORES.write_text(json.dumps({"calibration": cal, "scores": {
        " ".join(k): v for k, v in all_scores.items()}}))

    def get(split, load, d, r, which, mode="fixed"):
        return all_scores.get((name(split, load, d), r, which, mode))

    ev_key = name("evaluation", HUMAN_LOAD, 1)
    main_ev = {(r, w): get("evaluation", HUMAN_LOAD, 1, r, w) for r in READOUTS for w in SETS}
    have_main = all(v for v in main_ev.values())
    d4 = {(r, w): get("evaluation", HUMAN_LOAD, 4, r, w) for r in READOUTS for w in SETS}
    d4 = d4 if all(d4.values()) else None

    parts = ["## Tables", "",
             "Built by `scripts/make_e8b_table.py` from `results/e8b_*.json`, with the thresholds "
             "in `results/e8b_calibration.json` and the closer-lure levels in "
             "`results/e8b_lure_levels.json`. Means over seeds ± one standard deviation; rates in "
             "percent. Fixed thresholds: the intact model's, set at 128 drawings on background "
             "alphabets, for every arm and condition (the vision-code baseline keeps its own).", ""]
    parts += ["### Calibration on background alphabets, 128 drawings", "",
              "| Readout | Arm | θ_old | θ_new | Room for similar |", "|---|---|---|---|---|"]
    for r in READOUTS:
        for arm, thr in cal["thresholds"][r].items():
            parts.append("| {} | {} | {:.4f} (tie share {:.3f}) | {:.4f} (tie share {:.3f}) | {} |"
                         .format(READOUT_NAMES[r], ARM_NAMES[arm], thr["old"], thr["q_old"],
                                 thr["new"], thr["q_new"], "yes" if thr["feasible"] else "no"))
    parts += ["", "Per-load thresholds, intact model:", "",
              "| Readout | Condition | θ_old | θ_new |", "|---|---|---|---|"]
    for r in READOUTS:
        for cond, by in sorted(cal["by_load"][r].items(),
                               key=lambda kv: (int(kv[0].split("_")[0][1:]), kv[0])):
            parts.append("| {} | {} | {:.4f} | {:.4f} |".format(
                READOUT_NAMES[r], cond.replace("n", "").replace("_d", " drawings, per character "),
                by["intact"]["old"], by["intact"]["new"]))
    if LEVELS.is_file():
        lv = json.loads(LEVELS.read_text())
        parts += ["", "Closer-lure levels (background drawings, median vision-code cosine with the "
                  "undistorted drawing): " + "; ".join(
                      "C{} magnitude {:.3f}, target {:.3f}, reached {:.3f}".format(
                          i + 1, x["magnitude"], x["target"], x["median_cosine"])
                      for i, x in enumerate(lv["levels"])) + ".", ""]

    if have_main:
        parts += ["### Predictions, scored as the protocol fixes", "",
                  "| Prediction | Held | Numbers |", "|---|---|---|"]
        for label, held, text in predictions(main_ev, d4):
            parts.append("| {} | {} | {} |".format(label, "yes" if held else "no", text))
        parts.append("")
        for r in READOUTS:
            for which in SETS:
                sc = main_ev[(r, which)]
                parts += ["### Evaluation alphabets, 128 drawings, {}, {}, fixed thresholds".format(
                    READOUT_NAMES[r], SET_NAMES[which]), "",
                    score_table(sc, LESION_ARMS, which), "", "Response rates:", "",
                    response_table(sc, LESION_ARMS, [("Young adults, 20 to 39", YOUNG),
                                                     ("Adults 60 to 74", OLDER)]), "",
                    "p(old | lure) by level:", "", rate_by_level_table(sc, LESION_ARMS, which,
                                                                       "old_bins"), "",
                    "p(similar | lure) by level:", "",
                    rate_by_level_table(sc, LESION_ARMS, which, "sim_bins"), ""]
                if r == "r2":
                    parts += ["CA3 state:", "", ca3_table(sc, LESION_ARMS, which), ""]
        for r in READOUTS:
            own = all_scores.get((ev_key, r, "close", "own"))
            if own:
                parts += ["### Each arm with its own thresholds, {}, closer lures (secondary)".format(
                    READOUT_NAMES[r]), "", score_table(own, LESION_ARMS, "close", human=False), ""]
        parts += ["### What R2 tracks, intact model, evaluation alphabets, 128 drawings", "",
                  "| Lure set | Lures on studied pattern | p(old \\| lure) if on it | p(old \\| lure) "
                  "otherwise | R2 median, repeats / lures / foils | Nearest-pattern overlap, "
                  "repeats / lures / foils (logged only) | Cue self-support, repeats / lures / "
                  "foils |", "|---|---|---|---|---|---|---|"]
        for which in SETS:
            s = main_ev[("r2", which)]["intact"]
            parts.append("| {} | {} | {} | {} | {} | {} | {} |".format(
                SET_NAMES[which], pct(s["ca3 lure_exact"]), pct(s["ca3 old_if_exact"]),
                pct(s["ca3 old_if_not"]),
                " / ".join("{:.3f}".format(mean(s, "median " + t))
                           for t in ("repeat", "lure", "foil")),
                " / ".join("{:.3f}".format(mean(s, "ca3 overlap " + t))
                           for t in ("repeat", "lure", "foil")),
                " / ".join("{:.3f}".format(mean(s, "ca3 cue_support " + t))
                           for t in ("repeat", "lure", "foil"))))
        parts += ["", "### Seeds in which each lesion effect holds, closer lures, fixed thresholds",
                  "", "| Lesion | Readout | LDI below intact | REC below intact | "
                  "p(old \\| lure) below intact |", "|---|---|---|---|---|"]
        for r in READOUTS:
            sc = main_ev[(r, "close")]
            for arm in LESION_ARMS[1:-1]:
                if arm in sc:
                    cells = [seeds_where(sc[arm][k], sc["intact"][k], lambda x, y: x < y)
                             for k in ("ldi", "rec", "rates lure old")]
                    parts.append("| {} | {} | {} |".format(
                        ARM_NAMES[arm], READOUT_NAMES[r],
                        " | ".join("{} of {}".format(*c) for c in cells)))
        parts.append("")

    conds = ([("{} drawings".format(n), name("evaluation", n, 1)) for n in LOADS]
             + [("128 drawings, {} per character".format(d), name("evaluation", HUMAN_LOAD, d))
                for d in (2, 4)])
    conds_bg = [(lab, k.replace("evaluation", "background")) for lab, k in conds]
    for r in READOUTS:
        for which in SETS:
            parts += ["### Load and interference, evaluation alphabets, {}, {}, fixed "
                      "thresholds".format(READOUT_NAMES[r], SET_NAMES[which]), "",
                      condition_table(all_scores, conds, SHARED, r, which, "fixed"), ""]
            parts += ["### Load and interference, evaluation alphabets, {}, {}, thresholds set "
                      "again at each condition (secondary)".format(READOUT_NAMES[r],
                                                                  SET_NAMES[which]), "",
                      condition_table(all_scores, conds, ("intact", "vc_baseline"), r, which,
                                      "load"), ""]
    for r in READOUTS:
        bg = get("background", HUMAN_LOAD, 1, r, "close")
        if bg:
            parts += ["### Background alphabets, 128 drawings (calibration runs), {}, closer "
                      "lures".format(READOUT_NAMES[r]), "",
                      score_table(bg, LESION_ARMS, "close", human=False), ""]
        parts += ["### Load and interference, background alphabets (checks), {}, other-drawer "
                  "lures".format(READOUT_NAMES[r]), "",
                  condition_table(all_scores, conds_bg, SHARED, r, "drawer", "fixed"), ""]
    seconds = ["{}: {:.0f} s, peak {:.2f} GB".format(k, v["seconds"], v.get("peak_rss_gb", 0))
               for k, v in files.items()]
    parts += ["Run time and peak memory per file: " + "; ".join(seconds) + ".", ""]

    md = RESULTS / "e8b.md"
    head = ""
    if md.is_file():
        text = md.read_text()
        head = text.split("## Tables")[0] if "## Tables" in text else text + "\n"
    md.write_text(head + "\n".join(parts))
    if have_main:
        loads = {}
        loads_own = {}
        for n in LOADS:
            fixed = {r: get("evaluation", n, 1, r, "drawer") for r in READOUTS}
            if all(fixed.values()):
                loads[n] = fixed
                mode = "fixed" if n == HUMAN_LOAD else "load"
                loads_own[n] = {r: get("evaluation", n, 1, r, "drawer", mode) for r in READOUTS}
        figures(main_ev, loads, loads_own)
    print("Wrote results/e8b.md, results/e8b_scores.json and figures")


if __name__ == "__main__":
    main()
