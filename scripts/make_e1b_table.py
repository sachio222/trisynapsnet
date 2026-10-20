"""Builds E1b's tables and figures from results/e1b_*.json.

Writes results/e1b.md and, for the evaluation-set runs, one figure per task
and corruption: figures/e1b_<task>_<corruption>.pdf for study-to-test
matching and figures/e1b_<task>_<corruption>_tts.pdf for test-to-study
matching, where those runs exist. Each figure has three
panels against the corruption level: CA3 accuracy for each CA3 option with
VC and PR for reference, CA1 accuracy for each option, and recall-loss.
Lines are the mean over seeds and the shading is one standard deviation.

Example:
    python scripts/make_e1b_table.py
"""

import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"

OPTIONS = ("pinverse", "covariance", "willshaw", "none")
SETTLING = ("pinverse", "covariance", "willshaw")
LABELS = {"pinverse": "Pseudo-inverse", "covariance": "Covariance",
          "willshaw": "Clipped binary", "none": "No settling"}
TASKS = ("instance", "classification")
KINDS = ("occlusion", "noise")
# Categorical slots 1 to 4 of the dataviz reference palette, light mode.
COLOURS = {"pinverse": "#2a78d6", "covariance": "#eb6834", "willshaw": "#1baf7a",
           "none": "#eda100"}
MARKERS = {"pinverse": "o", "covariance": "s", "willshaw": "^", "none": "D"}


def load(results_dir=RESULTS):
    """One row per results file, with every level's per-seed scores."""
    rows = []
    for path in sorted(Path(results_dir).glob("e1b_*.json")):
        r = json.loads(path.read_text())
        c = r["config"]
        rows.append({
            "file": path.name, "task": r["args"]["task"], "runs": r["args"]["runs"],
            "seeds": r["args"]["seeds"], "match": r["args"].get("match", "study-to-test"),
            "option": "none" if c["ca3_iters"] == 0 else c["ca3_rule"],
            "kind": r["levels"][0]["corruption"],
            "levels": {lv["level"]: lv for lv in r["levels"]},
        })
    return rows


def find(rows, task, runs, kind, option, match="study-to-test"):
    for row in rows:
        if (row["task"], row["runs"], row["kind"], row["option"], row["match"]) == \
                (task, runs, kind, option, match):
            return row
    return None


def settling_gaps(rows, task, runs, kind, option, match="study-to-test"):
    """CA3 accuracy with settling minus without, paired by seed, per level.

    Both arms see the same runs, corrupted drawings and seeds, so each
    seed's difference is a fair pair. Returns the mean and standard
    deviation of the per-seed differences and how many seeds settling won.
    """
    a = find(rows, task, runs, kind, option, match)
    b = find(rows, task, runs, kind, "none", match)
    gaps = []
    for level in sorted(a["levels"]):
        x = a["levels"][level]["per_seed"]["accuracy"]["pc"]
        y = b["levels"][level]["per_seed"]["accuracy"]["pc"]
        diff = [p - q for p, q in zip(x, y)]
        gaps.append({"level": level, "mean": statistics.mean(diff),
                     "std": statistics.stdev(diff) if len(diff) > 1 else 0.0,
                     "wins": sum(d > 0 for d in diff), "n": len(diff)})
    return gaps


def pct(s):
    return "{:.1f} ± {:.1f}".format(100 * s["mean"], 100 * s["std"])


def accuracy_table(rows, task, runs, kind, match):
    """Accuracy by level: pixels, VC, PR, then CA3 and CA1 for each option."""
    present = [o for o in OPTIONS if find(rows, task, runs, kind, o, match)]
    ref = find(rows, task, runs, kind, present[0], match)
    head = (["level", "pixels", "VC", "PR"] + ["PC {}".format(LABELS[o]) for o in present]
            + ["PM {}".format(LABELS[o]) for o in present])
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for level in sorted(ref["levels"]):
        s = ref["levels"][level]["summary"]
        cells = ["{:g}".format(level), pct(s["pixels"]), pct(s["vc"]), pct(s["pr"])]
        for stage in ("pc", "pm"):
            for o in present:
                row = find(rows, task, runs, kind, o, match)
                cells.append(pct(row["levels"][level]["summary"][stage]))
        lines.append("| " + " | ".join(cells) + " |")
    return lines


def gap_table(rows, task, runs, kind, match):
    present = [o for o in SETTLING if find(rows, task, runs, kind, o, match)]
    if not find(rows, task, runs, kind, "none", match) or not present:
        return []
    gaps = {o: settling_gaps(rows, task, runs, kind, o, match) for o in present}
    head = ["level"] + ["{} minus none".format(LABELS[o]) for o in present]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for i, g in enumerate(gaps[present[0]]):
        cells = ["{:g}".format(g["level"])]
        for o in present:
            x = gaps[o][i]
            cells.append("{:+.1f} ± {:.1f} ({}/{})".format(
                100 * x["mean"], 100 * x["std"], x["wins"], x["n"]))
        lines.append("| " + " | ".join(cells) + " |")
    return lines


def loss_table(rows, task, runs, kind, match):
    present = [o for o in OPTIONS if find(rows, task, runs, kind, o, match)]
    head = ["level"] + [LABELS[o] for o in present]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for level in sorted(find(rows, task, runs, kind, present[0], match)["levels"]):
        cells = ["{:g}".format(level)]
        for o in present:
            s = find(rows, task, runs, kind, o, match)["levels"][level]["recall_loss"]
            cells.append("{:.4f} ± {:.4f}".format(s["mean"], s["std"]))
        lines.append("| " + " | ".join(cells) + " |")
    return lines


INTRO = """# E1b: CA3 settling on corrupted test drawings

Accuracy is one-shot matching in percent, mean ± standard deviation across
seeds, with normalised study-to-test matching at AHA's paper size (225 DG
and CA3 cells, 10 on). Only the test drawings are corrupted. Occlusion
levels are a circle's diameter over the image side; noise levels are the
share of pixels replaced with random intensities. The protocol and every
choice the paper leaves open are in `docs/e1b_protocol.md`.

The instance task studies the 20 drawings of one character and must find
each one again among the same 20, now corrupted. The classification task
is Lake's 20 runs: find a different person's drawing of each character.
Chance is 5% on both.

CA3 options: the pseudo-inverse rule (AHA's), the covariance rule and
clipped binary synapses (local rules with k-winners-take-all), and no
settling, where CA3 passes on the 10 most active cells of the PR output.
VC and PR do not depend on the CA3 option. PM is CA1's image
reconstruction. Recall-loss is the mean squared error between the
reconstruction and the clean study drawing it should be.

Settling gap tables give CA3 accuracy with settling minus no settling, in
points, paired by seed, with the number of seeds where settling scored
higher in brackets.
"""

SECTIONS = (
    ("official", "study-to-test", "Evaluation set: instance runs and Lake's runs, 10 seeds"),
    ("background", "study-to-test", "Background alphabets: instance runs, 5 seeds (check only)"),
    ("official", "test-to-study",
     "Evaluation set, matched test-to-study: each test state finds its nearest studied state"),
)


def write_markdown(rows, out=RESULTS / "e1b.md"):
    lines = [INTRO]
    for runs, match, title in SECTIONS:
        if not any(r["runs"] == runs and r["match"] == match for r in rows):
            continue
        lines += ["## " + title, ""]
        for task in TASKS:
            for kind in KINDS:
                if not any(find(rows, task, runs, kind, o, match) for o in OPTIONS):
                    continue
                name = "{} task, {}".format(task.capitalize(), kind)
                if match != "study-to-test":
                    name += ", {}".format(match)
                lines += ["### " + name, "", "Accuracy:", ""]
                lines += accuracy_table(rows, task, runs, kind, match) + [""]
                gaps = gap_table(rows, task, runs, kind, match)
                if gaps:
                    lines += ["Settling gap at PC:", ""] + gaps + [""]
                lines += ["Recall-loss:", ""] + loss_table(rows, task, runs, kind, match) + [""]
    Path(out).write_text("\n".join(lines))
    return out


def plot(rows, task, runs, kind, out, match="study-to-test"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    present = [o for o in OPTIONS if find(rows, task, runs, kind, o, match)]
    if not present:
        return None
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8), constrained_layout=True)
    ref = find(rows, task, runs, kind, present[0], match)
    levels = sorted(ref["levels"])

    def band(ax, values, colour, label, marker=None, style="-"):
        mean = [statistics.mean(v) for v in values]
        std = [statistics.stdev(v) if len(v) > 1 else 0.0 for v in values]
        ax.plot(levels, mean, style, color=colour, lw=2, marker=marker, ms=5, label=label)
        ax.fill_between(levels, [m - s for m, s in zip(mean, std)],
                        [m + s for m, s in zip(mean, std)], color=colour, alpha=0.18, lw=0)

    def acc(row, stage):
        return [[100 * a for a in row["levels"][lv]["per_seed"]["accuracy"][stage]]
                for lv in levels]

    band(axes[0], acc(ref, "vc"), "#8a8a85", "VC", style="--")
    band(axes[0], acc(ref, "pr"), "#3d3d3a", "PR", style=":")
    for o in present:
        row = find(rows, task, runs, kind, o, match)
        band(axes[0], acc(row, "pc"), COLOURS[o], "PC " + LABELS[o], MARKERS[o])
        band(axes[1], acc(row, "pm"), COLOURS[o], "PM " + LABELS[o], MARKERS[o])
        band(axes[2], [row["levels"][lv]["per_seed"]["recall_loss"] for lv in levels],
             COLOURS[o], LABELS[o], MARKERS[o])

    xlabel = ("Occlusion: circle diameter over image side" if kind == "occlusion"
              else "Noise: share of pixels replaced")
    titles = ("CA3 (PC) accuracy, with VC and PR", "CA1 (PM) accuracy", "Recall-loss")
    for ax, title in zip(axes, titles):
        ax.set_title(title, fontsize=10, loc="left")
        ax.set_xlabel(xlabel, fontsize=9)
        ax.grid(True, color="#e6e6e3", lw=0.6)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.tick_params(labelsize=8)
    for ax in axes[:2]:
        ax.set_ylabel("Accuracy (%)", fontsize=9)
        ax.set_ylim(0, 102)
        ax.axhline(5, color="#b5b5b0", lw=0.8)
        ax.legend(fontsize=7, frameon=False)
    axes[2].set_ylabel("MSE against the clean study drawing", fontsize=9)
    axes[2].legend(fontsize=7, frameon=False)
    task_name = "One-shot instance-classification" if task == "instance" else \
        "One-shot classification (Lake's runs)"
    fig.suptitle("{} under {}, matched {}, mean ± 1 std over seeds".format(
        task_name, kind, match), fontsize=11)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    plt.close(fig)
    return out


def main():
    rows = load()
    print("Wrote {}".format(write_markdown(rows)))
    for match, suffix in (("study-to-test", ""), ("test-to-study", "_tts")):
        for task in TASKS:
            for kind in KINDS:
                out = plot(rows, task, "official", kind,
                           FIGURES / "e1b_{}_{}{}.pdf".format(task, kind, suffix), match)
                if out:
                    print("Wrote {}".format(out))


if __name__ == "__main__":
    main()
