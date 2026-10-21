"""Builds E8's calibration, tables and figures from results/e8_*.json.

    python scripts/make_e8_table.py --calibrate   thresholds and lure-bin
                                                  edges from the background
                                                  calibration runs only
    python scripts/make_e8_table.py               scores, tables in
                                                  results/e8.md, figures

--calibrate reads results/e8_background_n20_d1.json and writes
results/e8_calibration.json: for every arm, the two thresholds that give
young adults' p(old | repeat) and p(new | foil) on the background lists,
and the quintile edges of the background lures' similarity. The intact
model's thresholds are applied to every arm; each arm's own thresholds are
the secondary check (protocol items 11, 13 and 14), and the vision-code
baseline always uses its own.

The default run scores every e8 result file with those thresholds and
writes results/e8_scores.json, the tables in results/e8.md below the line
"## Tables" (text above it is kept), and the figures:
    figures/e8_ldi_by_bin.pdf   LDI by lure bin, every arm, evaluation
    figures/e8_load.pdf         LDI and REC against load, evaluation

Values are means over seeds; shading and the numbers after ± are one
standard deviation over seeds.
"""

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from trisynapsnet.eval import behaviour as bh  # noqa: E402

RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
CALIBRATION = RESULTS / "e8_calibration.json"
SCORES = RESULTS / "e8_scores.json"

# Stark, Yassa, Lacy and Stark 2013, Table 2, ages 20 to 39 (N = 26).
YOUNG = {"repeat": {"old": 0.812, "similar": 0.117, "new": 0.041},
         "lure": {"old": 0.403, "similar": 0.476, "new": 0.083},
         "foil": {"old": 0.026, "similar": 0.116, "new": 0.820}}
# Same table, ages 60 to 74 (N = 29).
OLDER = {"repeat": {"old": 0.822, "similar": 0.076, "new": 0.053},
         "lure": {"old": 0.546, "similar": 0.236, "new": 0.123},
         "foil": {"old": 0.048, "similar": 0.123, "new": 0.734}}
# Kirwan and colleagues 2012, Section 3 and Table 2.
KIRWAN = {"patients_ldi": 0.10, "controls_ldi": 0.37, "patients_old_new_rec": 0.81,
          "controls_old_new_rec": 0.87, "patients_old_lure": 0.38, "controls_old_lure": 0.37}

ARM_NAMES = {
    "intact": "Intact",
    "no_recurrent": "No CA3 recurrent connections",
    "no_ca3": "No CA3 (EC to CA1 only)",
    "no_dg": "No DG",
    "pp_keep0.75": "Perforant path, 75% kept",
    "pp_keep0.5": "Perforant path, 50% kept",
    "pp_keep0.25": "Perforant path, 25% kept",
    "ca1_half": "Half of CA1",
    "vc_baseline": "Vision code alone (baseline)",
    "no_hippocampus": "No hippocampus",
}
LOADS = (20, 50, 100, 200)
PER_CHAR = (1, 2, 4)


def name(split, load, d):
    return "e8_{}_n{}_d{}".format(split, load, d)


def load_file(split, load, d):
    path = RESULTS / (name(split, load, d) + ".json")
    return json.loads(path.read_text()) if path.is_file() else None


def floats(values):
    return torch.tensor([float("nan") if v is None else v for v in values], dtype=torch.float64)


def pooled(record, key, arm=None):
    out = []
    for seed in sorted(record["per_seed"], key=int):
        items = record["per_seed"][seed]
        out += items["signal"][arm] if arm else items[key]
    return out


# ---------------------------------------------------------------- calibration

def calibrate():
    record = load_file("background", 20, 1)
    if record is None or not record["complete"]:
        raise SystemExit("results/e8_background_n20_d1.json is missing or incomplete")
    types = torch.tensor(pooled(record, "types"))
    out = {"source": "results/e8_background_n20_d1.json", "seeds": record["seeds_done"],
           "targets": {"p_old_repeat": YOUNG["repeat"]["old"], "p_new_foil": YOUNG["foil"]["new"]},
           "thresholds": {}}
    for arm in record["args"]["arms"]:
        s = floats(pooled(record, None, arm))
        out["thresholds"][arm] = bh.calibrate(s[types == 0], s[types == 2],
                                              YOUNG["repeat"]["old"], YOUNG["foil"]["new"])
    sim = floats(pooled(record, "similarity"))
    out["bin_edges"] = bh.bin_edges(sim[types == 1])
    CALIBRATION.write_text(json.dumps(out, indent=1))
    for arm, thr in out["thresholds"].items():
        print("{:14s} old {:.4f} (q {:.3f})  new {:.4f} (q {:.3f})  feasible {}".format(
            arm, thr["old"], thr["q_old"], thr["new"], thr["q_new"], thr["feasible"]))
    print("bin edges", ["{:.4f}".format(e) for e in out["bin_edges"]])
    return out


# ---------------------------------------------------------------- scoring

def thresholds_for(cal, arm, own=False):
    if arm == "vc_baseline" or own:
        return cal["thresholds"][arm]
    return cal["thresholds"]["intact"]


def lure_rate(signal, types, thr, mask, answer):
    """p(answer | lure) among lures where mask is true; nan when there are none."""
    r = bh.rates(signal, types, thr, mask=mask)["lure"]
    return float("nan") if r is None else r[answer]


def seed_scores(items, arm, thr, edges):
    types = torch.tensor(items["types"])
    s = floats(items["signal"][arm])
    sim = floats(items["similarity"])
    bins = bh.bin_of(sim, edges)
    r = bh.rates(s, types, thr)
    out = {"rates": r, "ldi": bh.ldi(r), "rec": bh.rec(r),
           "ldi_bins": bh.ldi_by_bin(s, types, bins, thr),
           "sim_bins": [lure_rate(s, types, thr, bins == b, "similar") for b in range(1, 6)],
           "old_bins": [lure_rate(s, types, thr, bins == b, "old") for b in range(1, 6)]}
    ca3 = items.get("ca3", {}).get(arm)
    if ca3:
        ep = torch.tensor(ca3["exact_paired"]).double()
        ea = torch.tensor(ca3["exact_any"]).double()
        out["ca3"] = {"repeat_exact": ep[types == 0].mean().item(),
                      "lure_exact": ep[types == 1].mean().item(),
                      "foil_any": ea[types == 2].mean().item(),
                      "cue_cells": torch.tensor(ca3["cue_cells"]).double().mean().item(),
                      "lure_exact_bins": [ep[(types == 1) & (bins == b)].mean().item()
                                          for b in range(1, 6)]}
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


def score_record(record, cal, own=False):
    """{arm: {flat key: summary over seeds}} for one result file."""
    out = {}
    for arm in record["args"]["arms"]:
        per_seed = [flatten(seed_scores(record["per_seed"][s], arm, thresholds_for(cal, arm, own),
                                        cal["bin_edges"]))
                    for s in sorted(record["per_seed"], key=int)]
        out[arm] = {key: summarise([p[key] for p in per_seed]) for key in per_seed[0]}
    flat = flatten(no_hippocampus())
    out["no_hippocampus"] = {key: summarise([v] * len(record["per_seed"])) for key, v in flat.items()}
    return out


# ---------------------------------------------------------------- tables

def pct(summary, digits=1):
    m = summary["mean"]
    if isinstance(m, float) and math.isnan(m):
        return ""
    return "{:.{d}f} ± {:.{d}f}".format(100 * m, 100 * summary["std"], d=digits)


def num(summary, digits=3):
    m = summary["mean"]
    if isinstance(m, float) and math.isnan(m):
        return ""
    return "{:.{d}f} ± {:.{d}f}".format(m, summary["std"], d=digits)


def seeds_where(a, b, test):
    pairs = list(zip(a["values"], b["values"]))
    return sum(1 for x, y in pairs if test(x, y)), len(pairs)


def response_table(scores, arms, human=None):
    rows = ["| Arm | " + " | ".join("{} to {}".format(resp, t) for t in bh.TYPES
                                     for resp in ("old", "similar", "new")) + " |",
            "|---|" + "---|" * 9]
    if human:
        for label, h in human:
            rows.append("| {} | ".format(label) + " | ".join(
                "{:.1f}".format(100 * h[t][r]) for t in bh.TYPES
                for r in ("old", "similar", "new")) + " |")
    for arm in arms:
        if arm not in scores:
            continue
        s = scores[arm]
        rows.append("| {} | ".format(ARM_NAMES[arm]) + " | ".join(
            pct(s["rates {} {}".format(t, r)]) for t in bh.TYPES
            for r in ("old", "similar", "new")) + " |")
    return "\n".join(rows)


def score_table(scores, arms, human=True):
    rows = ["| Arm | LDI | REC | p(old \\| lure) | " + " | ".join(
        "LDI L{}".format(b) for b in range(1, 6)) + " |", "|---|" + "---|" * 8]
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


def ca3_table(scores, arms):
    rows = ["| Arm | Cue cells | Repeats settling on their pattern | Lures settling on the "
            "studied drawing's pattern | Foils settling on a stored pattern | " + " | ".join(
                "Lures on studied pattern, L{}".format(b) for b in range(1, 6)) + " |",
            "|---|" + "---|" * 9]
    for arm in arms:
        if arm not in scores or "ca3 cue_cells" not in scores[arm]:
            continue
        s = scores[arm]
        rows.append("| {} | {} | {} | {} | {} | ".format(
            ARM_NAMES[arm], num(s["ca3 cue_cells"], 2), pct(s["ca3 repeat_exact"]),
            pct(s["ca3 lure_exact"]), pct(s["ca3 foil_any"]))
            + " | ".join(pct(s["ca3 lure_exact_bins {}".format(b)]) for b in range(1, 6)) + " |")
    return "\n".join(rows)


def condition_table(all_scores, split, conditions, arms):
    rows = ["| Condition | Arm | LDI | REC | p(old \\| repeat) | p(similar \\| lure) | "
            "p(old \\| lure) | p(old \\| foil) | Lures on studied pattern |",
            "|---|---|---|---|---|---|---|---|---|"]
    for label, key in conditions:
        scores = all_scores.get(key)
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


def predictions(ev, loads):
    s = ev
    intact, base, nodg = s["intact"], s["vc_baseline"], s["no_dg"]
    out = []
    bins = [intact["ldi_bins {}".format(b)]["mean"] for b in range(1, 6)]
    steps = [bins[i + 1] - bins[i] for i in range(4)]
    rec = intact["rec"]["mean"]
    p1 = bins[4] > bins[0] and min(steps) >= -0.05 and abs(rec - 0.786) <= 0.10
    out.append(("1", p1, "LDI L1 to L5: {}; smallest step {:+.3f}; REC {:.3f} against 0.786".format(
        ", ".join("{:.3f}".format(b) for b in bins), min(steps), rec)))
    diffs = [intact["ldi_bins {}".format(b)]["mean"] - base["ldi_bins {}".format(b)]["mean"]
             for b in (2, 3, 4)]
    p2 = statistics.mean(diffs) >= 0.10
    out.append(("2", p2, "intact minus baseline LDI at L2 to L4: {} (mean {:+.3f})".format(
        ", ".join("{:+.3f}".format(d) for d in diffs), statistics.mean(diffs))))
    d_ldi = intact["ldi"]["mean"] - nodg["ldi"]["mean"]
    d_rec = intact["rec"]["mean"] - nodg["rec"]["mean"]
    out.append(("3", d_ldi > d_rec, "LDI falls by {:.3f}, REC by {:.3f}".format(d_ldi, d_rec)))
    for keep in ("0.75", "0.5", "0.25"):
        t = s["pp_keep" + keep]
        held = (t["ldi"]["mean"] < intact["ldi"]["mean"]
                and abs(t["rec"]["mean"] - rec) <= 0.05
                and t["rates lure old"]["mean"] > intact["rates lure old"]["mean"])
        out.append(("4 ({}% kept)".format(int(float(keep) * 100)), held,
                    "LDI {:.3f} (intact {:.3f}); REC {:.3f} (intact {:.3f}); p(old | lure) {:.3f} "
                    "(intact {:.3f}); lures settling on the studied pattern {:.1%} (intact {:.1%})"
                    .format(t["ldi"]["mean"], intact["ldi"]["mean"], t["rec"]["mean"], rec,
                            t["rates lure old"]["mean"], intact["rates lure old"]["mean"],
                            t["ca3 lure_exact"]["mean"], intact["ca3 lure_exact"]["mean"])))
    nr = s["no_recurrent"]
    out.append(("5", nr["rates lure old"]["mean"] < intact["rates lure old"]["mean"],
                "p(old | lure) {:.3f} without recurrent connections, {:.3f} intact".format(
                    nr["rates lure old"]["mean"], intact["rates lure old"]["mean"])))
    if 20 in loads and 200 in loads:
        a, b = loads[20]["intact"], loads[200]["intact"]
        dl, dr = a["ldi"]["mean"] - b["ldi"]["mean"], a["rec"]["mean"] - b["rec"]["mean"]
        out.append(("6", dl > dr, "from 20 to 200 drawings LDI falls by {:.3f}, REC by {:.3f}".format(
            dl, dr)))
    return out


# ---------------------------------------------------------------- figures

def figures(ev, loads):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    FIGURES.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 4.6))
    x = list(range(1, 6))
    for arm in ("intact", "no_recurrent", "no_ca3", "no_dg", "pp_keep0.5", "pp_keep0.25",
                "ca1_half", "vc_baseline"):
        if arm not in ev:
            continue
        m = [ev[arm]["ldi_bins {}".format(b)]["mean"] for b in x]
        sd = [ev[arm]["ldi_bins {}".format(b)]["std"] for b in x]
        style = {"vc_baseline": "--", "intact": "-"}.get(arm, ":")
        line, = ax.plot(x, m, style, marker="o", ms=3, label=ARM_NAMES[arm],
                        lw=2 if arm == "intact" else 1.2)
        ax.fill_between(x, [a - b for a, b in zip(m, sd)], [a + b for a, b in zip(m, sd)],
                        color=line.get_color(), alpha=0.12)
    ax.axhline(0.360, color="k", lw=0.8, ls="-.", label="Young adults, all lures (0.360)")
    ax.set_xticks(x)
    ax.set_xticklabels(["L1\nmost similar", "L2", "L3", "L4", "L5\nleast similar"])
    ax.set_ylabel("LDI = p(similar | lure) − p(similar | foil)")
    ax.set_title("Lure discrimination by similarity bin, evaluation alphabets, 20 drawings")
    ax.legend(fontsize=7, loc="upper left")
    fig.tight_layout()
    fig.savefig(FIGURES / "e8_ldi_by_bin.pdf")
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8), sharex=True)
    have = sorted(loads)
    for arm in ("intact", "no_recurrent", "no_ca3", "vc_baseline"):
        for ax, key in zip(axes, ("ldi", "rec")):
            m = [loads[n][arm][key]["mean"] for n in have]
            sd = [loads[n][arm][key]["std"] for n in have]
            line, = ax.plot(have, m, "--" if arm == "vc_baseline" else "-", marker="o", ms=3,
                            label=ARM_NAMES[arm])
            ax.fill_between(have, [a - b for a, b in zip(m, sd)], [a + b for a, b in zip(m, sd)],
                            color=line.get_color(), alpha=0.12)
    axes[0].axhline(0.360, color="k", lw=0.8, ls="-.", label="Young adults")
    axes[1].axhline(0.786, color="k", lw=0.8, ls="-.", label="Young adults")
    for ax, label in zip(axes, ("LDI", "REC")):
        ax.set_xscale("log")
        ax.set_xticks(have)
        ax.set_xticklabels([str(n) for n in have])
        ax.set_xlabel("Drawings studied per list")
        ax.set_ylabel(label)
    axes[0].legend(fontsize=7)
    fig.suptitle("Evaluation alphabets, one drawing per character")
    fig.tight_layout()
    fig.savefig(FIGURES / "e8_load.pdf")
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
    all_scores, own_scores = {}, {}
    for split in bh.SPLITS:
        for load in LOADS:
            for d in PER_CHAR:
                record = load_file(split, load, d)
                if record is None:
                    continue
                key = name(split, load, d)
                all_scores[key] = score_record(record, cal)
                if load == 20 and d == 1:
                    own_scores[key] = score_record(record, cal, own=True)
    SCORES.write_text(json.dumps({"calibration": cal, "fixed": all_scores,
                                  "own_thresholds": own_scores}))

    lesion_arms = ("intact", "no_recurrent", "no_ca3", "no_dg", "pp_keep0.75", "pp_keep0.5",
                   "pp_keep0.25", "ca1_half", "vc_baseline", "no_hippocampus")
    parts = ["## Tables", "",
             "Built by `scripts/make_e8_table.py` from `results/e8_*.json`, with the thresholds and "
             "lure-bin edges in `results/e8_calibration.json`. Means over seeds ± one standard "
             "deviation; rates in percent.", ""]
    thr = cal["thresholds"]
    parts += ["### Calibration on background alphabets", "",
              "| Arm | θ_old | θ_new | Room for similar |", "|---|---|---|---|"]
    for arm in ("intact", "vc_baseline") + tuple(a for a in thr if a not in ("intact", "vc_baseline")):
        if arm in thr:
            parts.append("| {} | {:.4f} | {:.4f} | {} |".format(
                ARM_NAMES[arm], thr[arm]["old"], thr[arm]["new"], "yes" if thr[arm]["feasible"] else "no"))
    parts += ["", "Lure-bin edges (cosine with the studied drawing's EC code), L1 above the first: "
              + ", ".join("{:.4f}".format(e) for e in reversed(cal["bin_edges"])) + ".", ""]

    ev = all_scores.get(name("evaluation", 20, 1))
    bg = all_scores.get(name("background", 20, 1))
    loads = {n: all_scores[name("evaluation", n, 1)] for n in LOADS
             if name("evaluation", n, 1) in all_scores}
    if ev:
        parts += ["### Predictions, scored as the protocol fixes", "", "| Prediction | Held | Numbers |",
                  "|---|---|---|"]
        for label, held, text in predictions(ev, loads):
            parts.append("| {} | {} | {} |".format(label, "yes" if held else "no", text))
        parts += ["", "### Evaluation alphabets, 20 drawings, fixed thresholds", "",
                  score_table(ev, lesion_arms), "", "Response rates:", "",
                  response_table(ev, lesion_arms, [("Young adults, 20 to 39", YOUNG),
                                                   ("Adults 60 to 74", OLDER)]), "",
                  "p(similar | lure) by lure bin:", "",
                  "| Arm | " + " | ".join("L{}".format(b) for b in range(1, 6)) + " |",
                  "|---|" + "---|" * 5]
        for arm in lesion_arms:
            if arm in ev:
                parts.append("| {} | ".format(ARM_NAMES[arm]) + " | ".join(
                    pct(ev[arm]["sim_bins {}".format(b)]) for b in range(1, 6)) + " |")
        parts += ["", "CA3 state:", "", ca3_table(ev, lesion_arms), ""]
        own = own_scores.get(name("evaluation", 20, 1))
        if own:
            parts += ["### Evaluation alphabets, 20 drawings, each arm with its own thresholds", "",
                      "The secondary check: each lesion scored with thresholds recalibrated on its "
                      "own background runs.", "", score_table(own, lesion_arms, human=False), ""]
        parts += ["### Seeds in which each lesion effect holds, fixed thresholds", "",
                  "| Lesion | LDI below intact | REC below intact |", "|---|---|---|"]
        for arm in lesion_arms[1:-1]:
            if arm in ev:
                a, b = seeds_where(ev[arm]["ldi"], ev["intact"]["ldi"], lambda x, y: x < y)
                c, d = seeds_where(ev[arm]["rec"], ev["intact"]["rec"], lambda x, y: x < y)
                parts.append("| {} | {} of {} | {} of {} |".format(ARM_NAMES[arm], a, b, c, d))
        parts.append("")
    conds_eval = ([("{} drawings".format(n), name("evaluation", n, 1)) for n in LOADS]
                  + [("20 drawings, {} per character".format(d), name("evaluation", 20, d))
                     for d in (2, 4)])
    parts += ["### Load and interference, evaluation alphabets, fixed thresholds", "",
              condition_table(all_scores, "evaluation", conds_eval,
                              ("intact", "no_recurrent", "no_ca3", "vc_baseline")), ""]
    if bg:
        parts += ["### Background alphabets, 20 drawings (calibration runs)", "",
                  score_table(bg, lesion_arms, human=False), ""]
    conds_bg = ([("{} drawings".format(n), name("background", n, 1)) for n in LOADS]
                + [("20 drawings, {} per character".format(d), name("background", 20, d))
                   for d in (2, 4)])
    parts += ["### Load and interference, background alphabets (checks)", "",
              condition_table(all_scores, "background", conds_bg,
                              ("intact", "no_recurrent", "no_ca3", "vc_baseline")), ""]
    seconds = []
    for split in bh.SPLITS:
        for load in LOADS:
            for d in PER_CHAR:
                r = load_file(split, load, d)
                if r:
                    seconds.append("{}: {:.0f} s".format(name(split, load, d), r["seconds"]))
    parts += ["Run time per file: " + "; ".join(seconds) + ".", ""]

    md = RESULTS / "e8.md"
    head = ""
    if md.is_file():
        text = md.read_text()
        head = text.split("## Tables")[0] if "## Tables" in text else text + "\n"
    md.write_text(head + "\n".join(parts))
    if ev and loads:
        figures(ev, loads)
    print("Wrote results/e8.md, results/e8_scores.json and figures")


if __name__ == "__main__":
    main()
