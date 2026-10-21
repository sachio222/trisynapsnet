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
    files = {"background mean": "e4_select_background_225_centred",
             "raw": "e4_select_background_225_raw"}
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
                "{:.3f}".format(s) for s in scores) + " |")
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


def stage_scores(name):
    """{(level): {(stage): mean}} from an evaluate.py result file."""
    rec = load(name)
    if rec is None:
        return None
    return {lv["level"]: {st: v["mean"] for st, v in lv["summary"].items()} for lv in rec["levels"]}


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
        for match, tag in (("study-to-test", ""), ("test-to-study", "_tts")):
            sc = stage_scores("e4_{}_official_covariance_225_10_{}{}{}".format(task, arm, sfx, tag))
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
    colours = {"btsp_human": "#2a78d6", "btsp_rat": "#5a9be3", "backprop_ec": "#eb6834",
               "backprop_ec_scaled": "#f2a07c", "backprop_ec_nol2": "#a33f15",
               "pm_pixels": "#1baf7a", "pm_pixels_nol2": "#0f6e4c", "mean": "#3d3d3a"}
    loads = list(rows)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
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
        ax.set_xlabel("Drawings stored")
        ax.set_title(label)
        ax.grid(alpha=0.3)
    axes[0].legend(fontsize=7, loc="lower left")
    fig.tight_layout()
    path.parent.mkdir(exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def plot_partial(rows, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
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
        ax.set_xlabel("Drawings stored")
        ax.set_title(ARM_NAMES[arm])
        ax.grid(alpha=0.3)
    axes[0].set_ylabel("Identification")
    axes[0].legend(fontsize=7, loc="lower left")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


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
        lines += load_table(rows, arms, "ident", "Identification against load, percent", note)
        lines += load_table(rows, arms, "cos", "Cosine similarity against load",
                            "Same runs. Cosine between the returned code and the right drawing's.")
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
