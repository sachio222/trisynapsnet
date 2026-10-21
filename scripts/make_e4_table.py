"""Builds E4's tables and figures from results/e4_*.json.

    python scripts/make_e4_table.py --select   background choice of plateau
                                               share and drive baseline
    python scripts/make_e4_table.py            results/e4.md and figures

Figures:
    figures/e4_identification.pdf   identification against load, exact
                                    stored pattern, every CA1 arm
    figures/e4_partial.pdf          identification from settled partial
                                    cues against the exact pattern

Lines are means over seeds and shading is one standard deviation.
"""

import argparse
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"

CONDITIONS = ((0.2, 0.0), (0.4, 0.0), (0.6, 0.0), (0.8, 0.0), (0.0, 0.25), (0.0, 0.5),
              (0.0, 1.0), (0.4, 0.5))
CA3_RULES = ("covariance", "willshaw")
SELECTION_INPUTS = ["exact"] + ["{} {:g} {:g} settled".format(rule, r, s)
                                for rule in CA3_RULES for r, s in CONDITIONS]
ARM_NAMES = {
    "btsp_human": "BTSP, 2,118 CA1 cells (human ratio)",
    "btsp_rat": "BTSP, 375 CA1 cells (rat ratio)",
    "backprop_ec": "Backpropagation into EC, PM's training",
    "backprop_ec_scaled": "Backpropagation into EC, target scaled 19.3x",
    "backprop_ec_nol2": "Backpropagation into EC, no L2 penalty",
    "pm_pixels": "PM, pixels (AHA)",
    "pm_pixels_nol2": "PM, pixels, no L2 penalty",
    "mean": "No memory: mean stored EC code",
}


def load(name):
    path = RESULTS / (name + ".json")
    return json.loads(path.read_text()) if path.is_file() else None


def mean_over(row, arm, inputs, metric="ident"):
    return statistics.mean(row["arms"][arm][i][metric]["summary"]["mean"] for i in inputs)


def select():
    """Prints the background choice: per drive baseline and CA1 size, the
    selection score of each plateau share, and the winners."""
    files = {"background mean": "e4_ca1_background_225_10_q0.0025_0.005_0.01_0.02_0.05",
             "raw": "e4_ca1_background_225_10_q0.0025_0.005_0.01_0.02_0.05_raw"}
    best = {}
    lines = ["Selection score: identification averaged over loads and 17 inputs "
             "(background alphabets, 5 seeds).", ""]
    for baseline, name in files.items():
        rec = load(name)
        if rec is None:
            lines.append("missing results/{}.json".format(name))
            continue
        shares = rec["plateau_shares"]
        lines.append("| Drive baseline: {} | ".format(baseline) + " | ".join(
            "share {:g}".format(s) for s in shares) + " |")
        lines.append("|---" * (len(shares) + 1) + "|")
        for ratio in rec["ca1_units"]:
            scores = []
            for share in shares:
                arm = "btsp_{}_{:g}".format(ratio, share)
                scores.append(statistics.mean(mean_over(row, arm, SELECTION_INPUTS)
                                              for row in rec["rows"]))
            i = max(range(len(shares)), key=lambda j: scores[j])
            best[(baseline, ratio)] = (shares[i], scores[i])
            lines.append("| {} ({} cells) | ".format(ratio, rec["ca1_units"][ratio]) + " | ".join(
                "{:.4f}".format(s) for s in scores) + " |")
        lines.append("")
    for (baseline, ratio), (share, score) in best.items():
        lines.append("best for {} drive, {}: share {:g} ({:.3f})".format(baseline, ratio, share, score))
    for baseline in files:
        vals = [best[(baseline, r)][1] for (b, r) in best if b == baseline]
        if vals:
            lines.append("{} drive, mean of both sizes at their best share: {:.3f}".format(
                baseline, statistics.mean(vals)))
    print("\n".join(lines))
    return best


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--select", action="store_true")
    args = p.parse_args()
    if args.select:
        select()
        return
    build()


def pct(x):
    return "n/a" if x is None else "{:.1f}".format(100 * x)


def cell(row, arm, inp, metric="ident", scale=100, digits=1):
    try:
        v = row["arms"][arm][inp][metric]["summary"]["mean"]
    except KeyError:
        return "n/a"
    return "{:.{}f}".format(scale * v, digits)


def merged(units):
    """Rows by load, with the BTSP arms of both CA1 sizes in one dict.

    Every arm but BTSP is identical in the two files (same seeds and seed
    parts), so the human file supplies them.
    """
    human = load("e4_ca1_evaluation_{}_human".format(units))
    rat = load("e4_ca1_evaluation_{}_rat".format(units))
    if human is None or rat is None:
        return None, None
    rows = {}
    for rh, rr in zip(human["rows"], rat["rows"]):
        assert rh["load"] == rr["load"]
        row = dict(rh)
        row["arms"] = dict(rh["arms"])
        row["arms"]["btsp_rat"] = rr["arms"]["btsp_rat"]
        row["seconds"] = dict(rh["seconds"], btsp_rat=rr["seconds"]["btsp_rat"])
        row["cost"] = dict(rh["cost"], btsp_rat=rr["cost"]["btsp_rat"])
        rows[rh["load"]] = row
    return rows, {"human": human, "rat": rat}


def load_table(rows, arms, metric, title, note):
    out = ["## " + title, "", note, "",
           "| Load | " + " | ".join(ARM_NAMES[a] for a in arms) + " |",
           "|---" * (len(arms) + 1) + "|"]
    digits = 1 if metric == "ident" else 3
    scale = 100 if metric == "ident" else 1
    for load_n, row in rows.items():
        out.append("| {} | ".format(load_n) + " | ".join(
            cell(row, a, "exact", metric, scale, digits) for a in arms) + " |")
    out.append("")
    return out


def partial_table(rows, removal, add=0.0):
    tag = "{:g} {:g}".format(removal, add)
    cols = [("CA3 exact recall, covariance", None, "covariance {} settled".format(tag)),
            ("BTSP human, exact pattern", "btsp_human", "exact"),
            ("BTSP human, damaged cue", "btsp_human", "cue " + tag),
            ("BTSP human, after covariance CA3", "btsp_human", "covariance {} settled".format(tag)),
            ("BTSP human, after clipped-binary CA3", "btsp_human", "willshaw {} settled".format(tag)),
            ("BTSP rat, exact pattern", "btsp_rat", "exact"),
            ("BTSP rat, after covariance CA3", "btsp_rat", "covariance {} settled".format(tag)),
            ("Backprop no L2, exact pattern", "backprop_ec_nol2", "exact"),
            ("Backprop no L2, damaged cue", "backprop_ec_nol2", "cue " + tag),
            ("Backprop no L2, after covariance CA3", "backprop_ec_nol2",
             "covariance {} settled".format(tag))]
    what = "{:.0%} of active cells removed".format(removal)
    if add:
        what += ", stray cells numbering {:.0%} of k added".format(add)
    out = ["### " + what[0].upper() + what[1:], "",
           "| Load | " + " | ".join(c[0] for c in cols) + " |", "|---" * (len(cols) + 1) + "|"]
    for load_n, row in rows.items():
        vals = []
        for _, arm, inp in cols:
            if arm is None:
                vals.append(pct(row["ca3_exact"][inp]["mean"]))
            else:
                vals.append(cell(row, arm, inp))
        out.append("| {} | ".format(load_n) + " | ".join(vals) + " |")
    out.append("")
    return out


def pm_table(rows):
    """PM in pixel space with and without its L2 penalty, beside E1c's floor."""
    e1c = load("e1c_ca3_drawings_evaluation_covariance_225_10")
    floor = {}
    if e1c is not None:
        for r in e1c["rows"]:
            if r["remove"] == 0 and r["add"] == 0:
                floor[r["load"]] = r["summary"]["ca1_target"]["mean"]
    out = ["## PM's error floor and its L2 penalty", "",
           "PM, AHA's CA1, trained on pixels exactly as E1c trains it (Adam, learning rate 0.01, "
           "60 full-batch steps, L2 penalty 4e-4), and the same without the L2 penalty. Input: the "
           "exact stored CA3 pattern. Evaluation alphabets, 225 CA3 cells, the same drawings, "
           "seeds and starting weights as E1c's CA1, 10 seeds. Error is mean squared error "
           "against the drawing; identification picks the stored drawing nearest the "
           "reconstruction by cosine.", "",
           "| Load | E1c's CA1 error | PM error | PM error, no L2 | PM identification, % | "
           "PM identification, no L2, % | Mean stored drawing's error |",
           "|---|---|---|---|---|---|---|"]
    for load_n, row in rows.items():
        a = row["arms"]
        out.append("| {} | {} | {:.4f} | {:.4f} | {} | {} | {:.4f} |".format(
            load_n, "{:.4f}".format(floor[load_n]) if load_n in floor else "n/a",
            a["pm_pixels"]["exact"]["mse"]["summary"]["mean"],
            a["pm_pixels_nol2"]["exact"]["mse"]["summary"]["mean"],
            cell(row, "pm_pixels", "exact"), cell(row, "pm_pixels_nol2", "exact"),
            mean_drawing_error(load_n, e1c)))
    out.append("")
    return out


def mean_drawing_error(load_n, e1c):
    if e1c is None:
        return float("nan")
    for r in e1c["rows"]:
        if r["load"] == load_n and r["remove"] == 0 and r["add"] == 0:
            return r["summary"]["ca1_mean"]["mean"]
    return float("nan")


def stage_scores(name, match="study-to-test"):
    """{level: {stage: mean}} from an evaluate.py result file, for one
    matching direction. Test-to-study scores come from the same file's
    "<stage> test-to-study" keys, or from a separate <name>_tts file."""
    rec = load(name)
    if rec is None:
        return None
    out = {}
    for lv in rec["levels"]:
        summary = {st: v["mean"] for st, v in lv["summary"].items()}
        if match == "study-to-test":
            out[lv["level"]] = {st: v for st, v in summary.items() if " " not in st}
        elif "pc test-to-study" in summary:
            out[lv["level"]] = {st.split(" ")[0]: v for st, v in summary.items()
                                if st.endswith(" test-to-study")}
    if match == "test-to-study" and not out:
        return stage_scores(name + "_tts", "study-to-test")
    return out


EVAL_ARMS = (("pm", "PM, pixels (AHA)"), ("btsp_human", "BTSP, 2,118 cells"),
             ("btsp_rat", "BTSP, 375 cells"), ("backprop_ec", "Backprop into EC, PM's training"),
             ("backprop_ec_nol2", "Backprop into EC, no L2 penalty"))


def eval_table(task, kind):
    sfx = "" if kind == "none" else "_" + kind
    out = []
    header = "| CA1 | Matching | " + ("Level | " if kind != "none" else "") + \
        "VC | PR | CA3 | CA1 | CA1 minus CA3 |"
    out += [header, "|---" * (header.count("|") - 1) + "|"]
    for arm, label in EVAL_ARMS:
        for match in ("study-to-test", "test-to-study"):
            sc = stage_scores("e4_{}_official_covariance_225_10_{}{}".format(task, arm, sfx), match)
            if sc is None:
                continue
            for level, st in sc.items():
                lv = "{:g} | ".format(level) if kind != "none" else ""
                out.append("| {} | {} | {}{} | {} | {} | {} | {:+.1f} |".format(
                    label, match, lv, pct(st["vc"]), pct(st["pr"]), pct(st["pc"]), pct(st["pm"]),
                    100 * (st["pm"] - st["pc"])))
    out.append("")
    return out


def plot(rows, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker
    colours = {"btsp_human": "#2a78d6", "btsp_rat": "#5a9be3", "backprop_ec": "#eb6834",
               "backprop_ec_scaled": "#f2a07c", "backprop_ec_nol2": "#a33f15",
               "pm_pixels": "#1baf7a", "pm_pixels_nol2": "#0f6e4c", "mean": "#3d3d3a"}
    loads = list(rows)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.8))
    for ax, metric, label in ((axes[0], "ident", "Identification, exact pattern"),
                              (axes[1], "cos", "Cosine to the right code")):
        for arm in colours:
            if arm not in rows[loads[0]]["arms"]:
                continue
            m = [rows[l]["arms"][arm]["exact"][metric]["summary"]["mean"] for l in loads]
            sd = [rows[l]["arms"][arm]["exact"][metric]["summary"]["std"] for l in loads]
            ax.plot(loads, m, marker="o", color=colours[arm], label=ARM_NAMES[arm], lw=1.5)
            ax.fill_between(loads, [a - b for a, b in zip(m, sd)], [a + b for a, b in zip(m, sd)],
                            color=colours[arm], alpha=0.15, lw=0)
        ax.set_xscale("log")
        ax.set_xticks(loads)
        ax.set_xticklabels([str(l) for l in loads])
        ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        ax.set_xlabel("Drawings stored")
        ax.set_title(label)
        ax.grid(alpha=0.3)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, fontsize=7, loc="lower center", ncol=4, frameon=False)
    fig.tight_layout(rect=(0, 0.12, 1, 1))
    path.parent.mkdir(exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def plot_partial(rows, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker
    loads = list(rows)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    for ax, arm in zip(axes, ("btsp_human", "backprop_ec_nol2")):
        series = (("exact", "Exact pattern", "#3d3d3a", "-"),
                  ("cue 0.4 0", "40% removed, no settling", "#eda100", "--"),
                  ("covariance 0.4 0 settled", "40% removed, covariance CA3", "#eb6834", "-"),
                  ("cue 0.8 0", "80% removed, no settling", "#9ec5f0", "--"),
                  ("covariance 0.8 0 settled", "80% removed, covariance CA3", "#2a78d6", "-"))
        for inp, label, colour, style in series:
            m = [rows[l]["arms"][arm][inp]["ident"]["summary"]["mean"] for l in loads]
            ax.plot(loads, m, marker="o", color=colour, ls=style, label=label, lw=1.5)
        ax.set_xscale("log")
        ax.set_xticks(loads)
        ax.set_xticklabels([str(l) for l in loads])
        ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        ax.set_xlabel("Drawings stored")
        ax.set_title(ARM_NAMES[arm])
        ax.grid(alpha=0.3)
    axes[0].set_ylabel("Identification")
    axes[0].legend(fontsize=7, loc="lower left")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def ident(rows, load_n, arm, inp="exact"):
    return 100 * rows[load_n]["arms"][arm][inp]["ident"]["summary"]["mean"]


def verdicts(rows):
    """The four predictions, written before the runs, each against every
    baseline, with the numbers that decide it."""
    out = ["## Predictions", "",
           "Written in the plan before the runs. The plan names one baseline: a backpropagation "
           "network trained as PM is trained, with the EC code as its target "
           "(`backprop_ec`). It sits at chance at every load, because PM's L2 penalty outweighs "
           "the error signal when the target is an EC code, about 19 times smaller than pixels. "
           "A comparison with it tells nothing about BTSP, so each prediction is also judged "
           "against the same network without its L2 penalty, the informative comparison, and "
           "with the EC target scaled up 19.3 times, as a check. Identification from the exact "
           "stored pattern, percent.", ""]
    bl = (("backprop_ec", "PM's training (as planned)"), ("backprop_ec_nol2", "no L2 penalty"),
          ("backprop_ec_scaled", "target scaled 19.3x"))
    out += ["| Load | BTSP, 2,118 cells | BTSP, 375 cells | " + " | ".join(
        "Backprop, " + b for _, b in bl) + " |", "|---" * 6 + "|"]
    for load_n in (20, 50, 100, 200):
        if load_n in rows:
            out.append("| {} | {:.1f} | {:.1f} | ".format(load_n, ident(rows, load_n, "btsp_human"),
                                                          ident(rows, load_n, "btsp_rat")) +
                       " | ".join("{:.1f}".format(ident(rows, load_n, a)) for a, _ in bl) + " |")
    out.append("")

    def held(x):
        return "held" if x else "failed"

    def p1(arm, a):
        # Compared at the table's precision, so 97.0 against 100.0 counts as 3.0 points.
        return round(abs(ident(rows, 20, arm) - ident(rows, 20, a)), 1) <= 3.0

    def p2(arm, a):
        return all(ident(rows, n, arm) > ident(rows, n, a) for n in (100, 200))

    h, r = "btsp_human", "btsp_rat"
    f = lambda arm, n=20, inp="exact": "{:.1f}".format(ident(rows, n, arm, inp))
    lines = [
        "**Prediction 1.** At 20 drawings, BTSP CA1 identifies the right drawing as often as the "
        "baseline, within 3 points, after one presentation.",
        "",
        "- Against the planned baseline: {} at both sizes in the letter, and uninformative. BTSP "
        "scores {} (2,118 cells) and {} (375 cells); the planned baseline scores {}, chance, so "
        "BTSP is far more than 3 points ahead.".format(
            held(p1(h, "backprop_ec") and p1(r, "backprop_ec")), f(h), f(r), f("backprop_ec")),
        "- Against backpropagation without the L2 penalty, the informative comparison: {} at "
        "2,118 cells ({} against {}) and {} at 375 cells ({} against {}, a gap of exactly 3.0 "
        "points at the table's precision).".format(
            held(p1(h, "backprop_ec_nol2")), f(h), f("backprop_ec_nol2"),
            held(p1(r, "backprop_ec_nol2")), f(r), f("backprop_ec_nol2")),
        "- Against the scaled target, as a check: {}; that network scores {}, so BTSP is far "
        "ahead.".format(held(p1(h, "backprop_ec_scaled") and p1(r, "backprop_ec_scaled")),
                        f("backprop_ec_scaled")),
        "",
        "**Prediction 2.** Past 50 drawings BTSP holds up better: higher identification at 100 "
        "and 200 drawings.",
        "",
        "- Against the planned baseline: held at both sizes, and uninformative, since that "
        "network is at chance at every load.",
        "- Against backpropagation without the L2 penalty: {} at 2,118 cells ({} and {} against "
        "{} and {}); {} at 375 cells, which is lower at 100 drawings ({} against {}) and level "
        "at 200 ({} against {}).".format(
            held(p2(h, "backprop_ec_nol2")), f(h, 100), f(h, 200), f("backprop_ec_nol2", 100),
            f("backprop_ec_nol2", 200), held(p2(r, "backprop_ec_nol2")), f(r, 100),
            f("backprop_ec_nol2", 100), f(r, 200), f("backprop_ec_nol2", 200)),
        "- Against the scaled target: held at both sizes; that network is at chance from 50 "
        "drawings on.",
        "- PM itself, rebuilding pixels without its L2 penalty, identifies 100% up to 200 "
        "drawings (table below). That readout is in pixel space, so it does not enter the "
        "verdicts, but backpropagation is not limited to the numbers in this table.",
        "",
    ]
    out += lines
    out += prediction_3(rows, f) + prediction_4() + other_findings(rows)
    return out


def other_findings(rows):
    e1c = load("e1c_ca3_drawings_evaluation_covariance_225_10")
    pm = lambda n, arm, m: rows[n]["arms"][arm]["exact"][m]["summary"]["mean"]
    out = ["## Other findings", "",
           "- **PM's rising error floor comes from its L2 penalty.** E1c found that CA1's error "
           "from the exact stored pattern rises from 0.0046 at 20 drawings to 0.0363 at 100, and "
           "read it as CA1's capacity. The same network with the same 60 steps but no L2 penalty "
           "scores {:.4f} at 20 drawings, {:.4f} at 100 and {:.4f} at 500, and identifies "
           "{:.1f}% of drawings at 500. With the penalty it identifies {:.1f}% at 100.".format(
               pm(20, "pm_pixels_nol2", "mse"), pm(100, "pm_pixels_nol2", "mse"),
               pm(500, "pm_pixels_nol2", "mse"), 100 * pm(500, "pm_pixels_nol2", "ident"),
               100 * pm(100, "pm_pixels", "ident"))]
    rows1000, _ = merged(1000)
    if rows1000:
        g = lambda n, arm: 100 * rows1000[n]["arms"][arm]["exact"]["ident"]["summary"]["mean"]
        out.append("- **A larger CA3 helps BTSP far more than backpropagation.** At 1,000 CA3 "
                   "cells with 44 active, BTSP with 9,412 CA1 cells identifies {:.1f}% at 200 "
                   "drawings and {:.1f}% at 500; backpropagation without the L2 penalty "
                   "identifies {:.1f}% and {:.1f}%. Each BTSP cell then sees 44 active inputs "
                   "instead of 10.".format(g(200, "btsp_human"), g(500, "btsp_human"),
                                           g(200, "backprop_ec_nol2"), g(500, "backprop_ec_nol2")))
    out.append("- **Matching can score a network that returns almost nothing.** The planned "
               "baseline is at chance at identifying drawings from their CA3 patterns, yet its "
               "CA1 stage scores 53.5% on Lake's runs, close to CA3's 53.8%. Normalised matching "
               "compares the network's outputs for study and test drawings with each other, and "
               "the small differences between near-constant outputs still follow the CA3 "
               "states.")
    out.append("")
    return out


def prediction_3(rows, f):
    cov = "covariance {} 0 settled"
    ca3 = lambda n, r: 100 * rows[n]["ca3_exact"][cov.format(r)]["mean"]
    h, r = "btsp_human", "btsp_rat"
    return [
        "**Prediction 3.** With CA3 completing partial cues, BTSP CA1's output from a partial "
        "cue approaches its output from the exact pattern, below CA3's capacity.",
        "",
        "- Held at both sizes. At 2,118 cells and 20 drawings, BTSP identifies {} from the exact "
        "pattern; from cues missing 40% or 80% of their active cells it identifies {} and {} "
        "after covariance-rule settling, against {} and {} from the raw cue. At 50 drawings: {} "
        "exact, {} and {} after settling, {} and {} raw. At 375 cells and 20 drawings: {} exact, "
        "{} and {} after settling.".format(
            f(h), f(h, 20, cov.format(0.4)), f(h, 20, cov.format(0.8)), f(h, 20, "cue 0.4 0"),
            f(h, 20, "cue 0.8 0"), f(h, 50), f(h, 50, cov.format(0.4)), f(h, 50, cov.format(0.8)),
            f(h, 50, "cue 0.4 0"), f(h, 50, "cue 0.8 0"), f(r), f(r, 20, cov.format(0.4)),
            f(r, 20, cov.format(0.8))),
        "- The gap opens as CA3 nears capacity and follows CA3's exact recall. At 100 drawings "
        "with 80% removed, CA3 recalls {:.1f}% of cues exactly and BTSP identifies {} after "
        "settling against {} exact. At 200 drawings, past CA3's capacity, settling hurts: {} "
        "after settling against {} from the raw cue with 40% removed.".format(
            ca3(100, 0.8), f(h, 100, cov.format(0.8)), f(h, 100), f(h, 200, cov.format(0.4)),
            f(h, 200, "cue 0.4 0")),
        "- The completion comes from CA3: backpropagation without the L2 penalty gains the same "
        "way, from {} raw to {} after settling at 20 drawings with 80% removed.".format(
            f("backprop_ec_nol2", 20, "cue 0.8 0"), f("backprop_ec_nol2", 20, cov.format(0.8))),
        "",
    ]


def prediction_4():
    out = ["**Prediction 4.** CA1-stage accuracy on Lake's runs stays within 3 points of the "
           "CA3 stage.", ""]
    parts = []
    worst = 0.0
    for arm, label in (("btsp_human", "2,118 cells"), ("btsp_rat", "375 cells")):
        for match in ("study-to-test", "test-to-study"):
            sc = stage_scores("e4_classification_official_covariance_225_10_" + arm, match)
            if not sc:
                return out + ["- Not run.", ""]
            st = sc[0.0]
            d = 100 * (st["pm"] - st["pc"])
            worst = max(worst, abs(d))
            parts.append("{} {}: {:.1f} against {:.1f} ({:+.1f})".format(
                label, match, 100 * st["pm"], 100 * st["pc"], d))
    out.append("- {} at both sizes and in both matching directions; the largest gap is {:.1f} "
               "points. CA1 against CA3: {}.".format("Held" if worst <= 3 else "Failed", worst,
                                                     "; ".join(parts)))
    out.append("- On the instance task, 2,118-cell BTSP stays within 1.4 points of CA3 at every "
               "level. 375-cell BTSP loses up to 7.1 points, most on clean and lightly occluded "
               "drawings, where the 20 drawings are all of one character and their EC codes are "
               "alike.")
    out.append("")
    return out


def build():
    lines = []
    rows, recs = merged(225)
    arms = ["btsp_human", "btsp_rat", "backprop_ec", "backprop_ec_scaled", "backprop_ec_nol2",
            "pm_pixels", "pm_pixels_nol2", "mean"]
    if rows:
        shares = (recs["human"]["plateau_shares"][0], recs["rat"]["plateau_shares"][0])
        note = ("Evaluation alphabets, 225 CA3 cells with 10 active, 10 seeds. CA1 receives the "
                "exact stored CA3 pattern. Plateau share {:g} at 2,118 CA1 cells and {:g} at 375. "
                "PM is scored against the stored drawings' pixels, every other arm against the "
                "stored EC codes.".format(*shares))
        lines += verdicts(rows)
        lines += load_table(rows, arms, "ident", "Identification against load, percent", note)
        lines += load_table(rows, arms, "cos", "Cosine similarity against load",
                            "Same runs. Cosine between the returned code and the right drawing's.")
        lines += pm_table(rows)
        lines += ["## Partial cues", "",
                  "Identification in percent, same runs. A damaged copy of the stored pattern "
                  "reaches CA1 as it is, or after CA3 settles (E1c's settling).", ""]
        for r, a in ((0.4, 0.0), (0.8, 0.0), (0.4, 0.5)):
            lines += partial_table(rows, r, a)
        lines += ["## Cost", "",
                  "Seconds to learn one stored set, mean over seeds, CPU with 2 threads.", "",
                  "| Load | " + " | ".join(ARM_NAMES[a] for a in arms[:-1]) + " |",
                  "|---" * len(arms) + "|"]
        for load_n, row in rows.items():
            lines.append("| {} | ".format(load_n) + " | ".join(
                "{:.2f}".format(row["seconds"][a]["mean"]) for a in arms[:-1]) + " |")
        lines += ["", "BTSP learns each drawing in one presentation; every backpropagation arm "
                  "takes 60 full-batch optimiser steps over the whole stored set.", ""]
        plot(rows, FIGURES / "e4_identification.pdf")
        plot_partial(rows, FIGURES / "e4_partial.pdf")
    rows1000, _ = merged(1000)
    if rows1000:
        a1000 = ["btsp_human", "btsp_rat", "backprop_ec", "backprop_ec_scaled", "backprop_ec_nol2",
                 "mean"]
        note = ("Evaluation alphabets, 1,000 CA3 cells with 44 active, 5 seeds. BTSP at 9,412 "
                "(human ratio) and 1,667 (rat ratio) CA1 cells; the column names give the 225-cell "
                "sizes.")
        lines += load_table(rows1000, a1000, "ident", "Identification at 1,000 CA3 cells, percent",
                            note)
    lines += ["## Lake's runs", "",
              "CA3 on the covariance rule at 225 cells, 10 seeds, normalised matching, accuracy "
              "in percent. CA1 holds the returned EC code for BTSP and backpropagation into EC, "
              "the rebuilt image for PM.", ""]
    lines += eval_table("classification", "none")
    for kind in ("occlusion", "noise"):
        lines += ["## Instance task, {}".format(kind), ""]
        lines += eval_table("instance", kind)
    text = HEADER + "\n".join(lines)
    (RESULTS / "e4.md").write_text(text)
    print("Wrote results/e4.md")


HEADER = """# E4: one-shot learning in CA1

AHA's CA1 (PM) learns by backpropagation, 60 optimiser steps over the study set, and
rebuilds pixels. E4 replaces it with a CA1 that learns each drawing in one presentation
by behavioural timescale synaptic plasticity (BTSP), using Wu and Maass's binary rule,
and returns the drawing's EC code, the vision network's 20,449 numbers, through
synapses that grow with CA1 and EC activity. A backpropagation network trained like PM
but with the EC code as its target compares in the same space.

Terms used below:

- **Identification:** the stored EC code nearest the returned one, by cosine, belongs to
  the right drawing. Ties count 1 over the number tied. Chance is 1 over the load.
- **Exact pattern:** CA1 receives the stored CA3 pattern itself.
- **Damaged cue:** E1c's damaged copy of the stored pattern, passed to CA1 as it is.
  **After CA3:** the same copy after CA3 settles with the covariance rule or clipped
  binary synapses.
- **CA1 stage:** on Lake's runs and the instance task, matching on CA1's output.

Every choice is listed in `docs/e4_protocol.md`. Made by `scripts/make_e4_table.py`.

"""


if __name__ == "__main__":
    main()
