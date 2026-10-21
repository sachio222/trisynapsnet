"""Builds E1d's tables and figures from results/e1d_*.json.

Writes results/e1d.md and these figures:

    figures/e1d_capacity_per_cell.pdf   the load where exact recall falls to
                                        50%, per cell, against cell count,
                                        for each share of active cells and
                                        rule; random patterns and drawings
    figures/e1d_exact_recall.pdf        exact recall from clean cues against
                                        load, each size, rule and share
    figures/e1d_completion_<load>.pdf   exact recall and overlap gained by
                                        settling against the share of cells
                                        removed, at 20 and 100 patterns

Example:
    python scripts/make_e1d_table.py
"""

import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"

import sys  # noqa: E402
sys.path.insert(0, str(ROOT))
from trisynapsnet.eval.sparsecodes import LOG_C, SPARSITIES, active_cells  # noqa: E402

RULES = ("pinverse", "covariance", "willshaw")
LABELS = {"pinverse": "Pseudo-inverse", "covariance": "Covariance", "willshaw": "Clipped binary",
          "none": "No settling"}
SIZES = (225, 1000, 4000, 16000)
SPARSITY_NAMES = {"4.4": "4.4% (AHA)", "2": "2% (rat DG)", "1": "1%", "log": "log-scaled"}
SOURCES = ("random", "drawings_evaluation", "drawings_background")
SOURCE_NAMES = {"random": "Random patterns", "drawings_evaluation": "Drawings, evaluation alphabets",
                "drawings_background": "Drawings, background alphabets"}
# Sequential shades, sparsest darkest, and the dataviz palette's rule colours as in E1c.
SPARSITY_COLOURS = {"4.4": "#9ec5f0", "2": "#4d8fdb", "1": "#1a4f91", "log": "#eb6834"}
SPARSITY_MARKERS = {"4.4": "o", "2": "s", "1": "^", "log": "D"}
RULE_COLOURS = {"covariance": "#eb6834", "willshaw": "#1baf7a", "none": "#eda100"}
CLEAN, HALF = (0.0, 0.0), (0.4, 0.0)
REMOVALS = (0.2, 0.4, 0.6, 0.8)
COMPLETION_LOADS = (20, 100)


# ---------- loading ----------

def load_ca3(results_dir=RESULTS):
    """{(source, rule, units, k): entry} from the E1d CA3 harness."""
    out = {}
    for path in sorted(Path(results_dir).glob("e1d_ca3_*.json")):
        r = json.loads(path.read_text())
        source = r["source"] if r["source"] == "random" else "drawings_" + r["split"]
        out[(source, r["rule"], r["units"], r["k"])] = {
            "file": path.name, "record": r,
            "rows": {(row["load"], row["remove"], row["add"]): row for row in r["rows"]}}
    return out


def entry_for(ca3, source, rule, units, sparsity):
    return ca3.get((source, rule, units, active_cells(units, sparsity)[0]))


def mean(values):
    return statistics.mean(values)


def sd(values):
    return statistics.stdev(values) if len(values) > 1 else 0.0


def metric(entry, load, cond, name):
    if entry is None:
        return None
    row = entry["rows"].get((load, cond[0], cond[1]))
    if row is None or name not in row["per_seed"]:
        return None
    return row["per_seed"][name]


def loads_of(entry):
    return sorted({key[0] for key in entry["rows"]}) if entry else []


def pct(values, digits=1):
    if values is None:
        return "n/a"
    return "{:.{}f}".format(100 * mean(values), digits)


# ---------- capacity ----------

def half_load(entry, cond):
    """Load where mean exact recall first falls through 50%, read between
    the two tested loads around it on a log scale.

    Returns (value, kind): kind "at" for a crossing, "above" when recall
    never falls below 50% (value is the highest load), "below" when it
    starts below (value is the lowest load), or (None, None) without data.
    """
    prev = None
    loads = [n for n in loads_of(entry) if metric(entry, n, cond, "exact") is not None]
    if not loads:
        return None, None
    for load in loads:
        m = mean(metric(entry, load, cond, "exact"))
        if m < 0.5:
            if prev is None:
                return load, "below"
            l0, m0 = prev
            t = (m0 - 0.5) / (m0 - m)
            return math.exp(math.log(l0) + t * (math.log(load) - math.log(l0))), "at"
        prev = (load, m)
    return loads[-1], "above"


def capacity_cond(rule):
    """The condition each rule's headline capacity uses: clean cues for the
    local rules; 40% removed for the pseudo-inverse, whose clean cues stay
    exact up to the cell count."""
    return HALF if rule == "pinverse" else CLEAN


def format_half(value, kind, units):
    if kind is None:
        return "n/a"
    if kind == "below":
        return "below {:,}".format(value)
    if kind == "above":
        return "above {:,} (≥ {:.2f})".format(value, value / units)
    return "{:,.0f} ({:.2f})".format(value, value / units)


def capacity_table(ca3, source, rule, cond):
    present = [n for n in SIZES if any(entry_for(ca3, source, rule, n, s) for s in SPARSITIES)]
    if not present:
        return []
    lines = ["| Share active | " + " | ".join("{:,} cells".format(n) for n in present) + " |",
             "|---|" + "---|" * len(present)]
    for s in SPARSITIES:
        row = [SPARSITY_NAMES[s]]
        for n in present:
            e = entry_for(ca3, source, rule, n, s)
            k = active_cells(n, s)[0]
            value, kind = half_load(e, cond)
            row.append("k = {}: {}".format(k, format_half(value, kind, n)) if e else "n/a")
        lines.append("| " + " | ".join(row) + " |")
    return lines


def per_cell(ca3, source, rule, units, sparsity, cond=None):
    e = entry_for(ca3, source, rule, units, sparsity)
    value, kind = half_load(e, cond or capacity_cond(rule))
    if kind is None:
        return None, None
    return value / units, kind


# ---------- other tables ----------

def codes_table():
    lines = ["| Share active | " + " | ".join("{:,} cells".format(n) for n in SIZES) + " |",
             "|---|" + "---|" * len(SIZES)]
    for s in SPARSITIES:
        row = [SPARSITY_NAMES[s]]
        for n in SIZES:
            k, raised = active_cells(n, s)
            row.append("{} ({:.2f}%){}".format(k, 100 * k / n, ", raised to 3" if raised else ""))
        lines.append("| " + " | ".join(row) + " |")
    return lines


def completion_table(ca3, source, load):
    lines = ["| Cells | Share active | Rule | " + " | ".join(
        "{:.0%} removed: exact, overlap cue → settled".format(r) for r in REMOVALS) + " |",
        "|---|---|---|" + "---|" * len(REMOVALS)]
    for n in SIZES:
        for s in SPARSITIES:
            k = active_cells(n, s)[0]
            if s == "log" and active_cells(n, "2")[0] == k:
                continue
            for rule in RULES:
                e = entry_for(ca3, source, rule, n, s)
                if e is None or metric(e, load, CLEAN, "exact") is None:
                    continue
                row = ["{:,}".format(n), "{} (k = {})".format(SPARSITY_NAMES[s], k), LABELS[rule]]
                for r in REMOVALS:
                    cond = (r, 0.0)
                    row.append("{}, {} → {}".format(pct(metric(e, load, cond, "exact")),
                                                    pct(metric(e, load, cond, "overlap_cue"), 0),
                                                    pct(metric(e, load, cond, "overlap_final"), 0)))
                lines.append("| " + " | ".join(row) + " |")
    return lines


def unevenness_table(ca3, source):
    """DG's cell-use CV at the highest load against random patterns."""
    lines = ["| Cells | Share active | Load | DG drawings CV | Random patterns CV | Ratio |",
             "|---|---|---|---|---|---|"]
    for n in SIZES:
        for s in SPARSITIES:
            k = active_cells(n, s)[0]
            if s == "log" and active_cells(n, "2")[0] == k:
                continue
            e = None
            for rule in ("willshaw", "covariance", "pinverse"):
                e = e or entry_for(ca3, source, rule, n, s)
            if e is None:
                continue
            load = max(loads_of(e))
            row = e["rows"][(load, 0.0, 0.0)]
            dg, rnd = row["usage_cv"], row["random_usage_cv"]
            lines.append("| {:,} | {} (k = {}) | {:,} | {:.3f} | {:.3f} | {:.2f} |".format(
                n, SPARSITY_NAMES[s], k, load, mean(dg), mean(rnd), mean(dg) / mean(rnd)))
    return lines


def settling_table(ca3, source):
    lines = ["| Cells | Share active | Rule | Load | Steps, clean | Fixed point, clean | "
             "Steps, 40% removed | Fixed point, 40% removed |", "|---|---|---|---|---|---|---|---|"]
    for n in SIZES:
        for s in SPARSITIES:
            k = active_cells(n, s)[0]
            if s == "log" and active_cells(n, "2")[0] == k:
                continue
            for rule in RULES:
                e = entry_for(ca3, source, rule, n, s)
                if e is None:
                    continue
                value, kind = half_load(e, capacity_cond(rule))
                picks = [load for load in COMPLETION_LOADS if load in loads_of(e)]
                if kind == "at":
                    above = [load for load in loads_of(e) if load >= value]
                    if above and above[0] not in picks:
                        picks.append(above[0])
                for load in picks:
                    cells = []
                    for cond in (CLEAN, HALF):
                        it, fx = metric(e, load, cond, "iterations"), metric(e, load, cond, "fixed")
                        cells += ["{:.1f}".format(mean(it)), pct(fx)]
                    tag = " (past 50%)" if load not in COMPLETION_LOADS else ""
                    lines.append("| {:,} | {} | {} | {:,}{} | ".format(
                        n, SPARSITY_NAMES[s], LABELS[rule], load, tag) + " | ".join(cells) + " |")
    return lines


def exact_table(ca3, source, units):
    present = [(s, r) for s in SPARSITIES for r in RULES if entry_for(ca3, source, r, units, s)
               and not (s == "log" and active_cells(units, "2")[0] == active_cells(units, s)[0])]
    if not present:
        return []
    loads = sorted({n for s, r in present for n in loads_of(entry_for(ca3, source, r, units, s))})
    lines = ["| Load | " + " | ".join("{} k = {} {}".format(
        SPARSITY_NAMES[s], active_cells(units, s)[0], LABELS[r]) for s, r in present) + " |",
        "|---|" + "---|" * len(present)]
    for load in loads:
        row = ["{:,}".format(load)]
        for s, r in present:
            e = entry_for(ca3, source, r, units, s)
            row.append(pct(metric(e, load, capacity_cond(r), "exact")))
        lines.append("| " + " | ".join(row) + " |")
    return lines


def rerun_table(ca3, results_dir=RESULTS):
    """E1d's 4.4% runs against E1c's, random patterns, same patterns and cues."""
    lines = ["| Cells | Rule | Condition | E1c | E1d |", "|---|---|---|---|---|"]
    found = False
    for n, k in ((225, 10), (1000, 44), (4000, 178)):
        for rule in RULES:
            path = Path(results_dir) / "e1c_ca3_random_{}_{}_{}.json".format(rule, n, k)
            e = ca3.get(("random", rule, n, k))
            if not path.is_file() or e is None:
                continue
            r = json.loads(path.read_text())
            old = {"file": path.name, "record": r,
                   "rows": {(row["load"], row["remove"], row["add"]): row for row in r["rows"]
                            if not (rule == "pinverse" and row["load"] >= n)}}
            cond = capacity_cond(rule)
            a, b = half_load(old, cond), half_load(e, cond)
            tag = "40% removed" if cond == HALF else "clean"
            lines.append("| {:,} | {} | {} | {} | {} |".format(
                n, LABELS[rule], tag, format_half(a[0], a[1], n), format_half(b[0], b[1], n)))
            found = True
    return lines if found else []


def times_table(ca3):
    lines = ["| Source | Cells | k | Rule | Seeds | Highest load | Minutes per seed |",
             "|---|---|---|---|---|---|---|"]
    for key in sorted(ca3, key=lambda key: (key[0], key[2], key[3], key[1])):
        source, rule, n, k = key
        r = ca3[key]["record"]
        lines.append("| {} | {:,} | {} | {} | {} | {:,} | {:.1f} |".format(
            SOURCE_NAMES[source], n, k, LABELS[rule], len(r["seeds"]), max(r["loads"]),
            mean(r["seconds_per_seed"]) / 60))
    return lines


# ---------- end to end ----------

E2E_OPTIONS = (("covariance", ""), ("willshaw", ""), ("covariance", "_it0"))


def option_label(rule, suffix):
    return LABELS["none"] if suffix else LABELS[rule]


def e2e_value(path, level, stage="pc"):
    """(mean, per-seed list) of one stage's accuracy at one corruption level."""
    if not path.is_file():
        return None
    r = json.loads(path.read_text())
    if "levels" not in r:
        # E1's files hold one clean level at the top.
        return r["per_seed"]["accuracy"][stage] if level == 0 else None
    for lv in r["levels"]:
        if abs(lv["level"] - level) < 1e-9:
            return lv["per_seed"]["accuracy"][stage]
    return None


def e2e_paths(task, runs, rule, suffix, kind, match, results_dir=RESULTS):
    tts = "_tts" if match == "test-to-study" else ""
    new = "e1d_e2e_{}_{}_{}_225_5{}{}{}.json".format(
        task, runs, rule, suffix, "" if kind == "none" else "_" + kind, tts)
    if task == "classification" and runs == "background":
        # E1's validation runs, scored study-to-test only.
        old = "bio_e1_background_{}_225_10{}.json".format(rule, suffix) if not tts else "none"
    elif task == "classification":
        # E1b's classification files hold the clean level of each sweep.
        old = "e1b_classification_{}_{}_225_10{}_noise{}.json".format(runs, rule, suffix, tts)
    else:
        old = "e1b_instance_{}_{}_225_10{}_{}{}.json".format(runs, rule, suffix, kind, tts)
    return Path(results_dir) / old, Path(results_dir) / new


def e2e_table(runs, match, results_dir=RESULTS):
    tasks = [("classification", "none", 0.0)] + [
        ("instance", kind, level) for kind in ("occlusion", "noise") for level in (0.0, 0.3, 0.5)]
    lines = ["| Task | Corruption | " + " | ".join(
        "{} 4.4% → 2%".format(option_label(r, s)) for r, s in E2E_OPTIONS) + " |",
        "|---|---|" + "---|" * len(E2E_OPTIONS)]
    found = False
    for task, kind, level in tasks:
        row = [task.capitalize(), "none" if kind == "none" else "{} {:g}".format(kind, level)]
        for rule, suffix in E2E_OPTIONS:
            old, new = e2e_paths(task, runs, rule, suffix, kind, match, results_dir)
            a, b = e2e_value(old, level), e2e_value(new, level)
            if a is None or b is None:
                row.append("n/a")
                continue
            found = True
            row.append("{:.1f} → {:.1f} ({:+.1f})".format(100 * mean(a), 100 * mean(b),
                                                         100 * (mean(b) - mean(a))))
        lines.append("| " + " | ".join(row) + " |")
    return lines if found else []


def e2e_stage_table(runs, match, results_dir=RESULTS):
    """Every stage at 2%, clean classification and the instance task at 0."""
    stages = ("vc", "pr", "pc", "pm")
    lines = ["| Task | Option | " + " | ".join(s.upper() for s in stages) + " |",
             "|---|---|" + "---|" * len(stages)]
    found = False
    for task, kind in (("classification", "none"), ("instance", "occlusion")):
        for rule, suffix in E2E_OPTIONS:
            _, new = e2e_paths(task, runs, rule, suffix, kind, match, results_dir)
            vals = [e2e_value(new, 0.0, s) for s in stages]
            if any(v is None for v in vals):
                continue
            found = True
            lines.append("| {} | {} | ".format(task.capitalize(), option_label(rule, suffix)) +
                         " | ".join("{:.1f}".format(100 * mean(v)) for v in vals) + " |")
    return lines if found else []


# ---------- markdown ----------

def seeds_line(ca3, source):
    seeds = {}
    for key, e in ca3.items():
        if key[0] == source:
            seeds.setdefault(key[2], set()).add(len(e["record"]["seeds"]))
    return ", ".join("{} at {:,} cells".format("/".join(str(s) for s in sorted(v)), n)
                     for n, v in sorted(seeds.items()))


def write_markdown(ca3, out=RESULTS / "e1d.md", results_dir=RESULTS):
    L = ["# E1d results", "",
         "E1d asks whether CA3's capacity per cell stops falling as the network grows once DG and",
         "CA3 codes are as sparse as measured. It reruns E1c's CA3 test with the share of active",
         "cells as a parameter. The protocol is `docs/e1d_protocol.md` and the numbers come from",
         "`results/e1d_*.json`. Built by `scripts/make_e1d_table.py`.", "",
         "Exact recall means CA3's final state is exactly the right stored pattern. The **50% load**",
         "is the number of stored patterns at which mean exact recall falls through 50%, read between",
         "the two tested loads around it on a log scale. Divided by the cell count it gives the",
         "**load per cell**, shown in brackets. For the covariance rule and clipped binary synapses it",
         "comes from clean cues. For the pseudo-inverse rule it comes from cues missing 40% of their",
         "cells, because clean cues stay exact up to the cell count. \"Above\" means recall never fell",
         "below 50% at the loads tested.", "",
         "## Active cells at each share and size", "",
         "The log-scaled code has k = round(c × log2 n) active cells with c = {:.4f}, so that".format(LOG_C),
         "k = 20 (2%) at 1,000 cells. At 1,000 cells the 2% and log-scaled codes are the same and run once.",
         ""] + codes_table() + [""]

    for source in SOURCES:
        if not any(key[0] == source for key in ca3):
            continue
        L += ["## {}: 50% load and load per cell".format(SOURCE_NAMES[source]), "",
              "Seeds: {}.".format(seeds_line(ca3, source)), ""]
        for rule in RULES:
            cond = capacity_cond(rule)
            tag = "cues missing 40% of their cells" if cond == HALF else "clean cues"
            table = capacity_table(ca3, source, rule, cond)
            if table:
                L += ["### {}, {}".format(LABELS[rule], tag), ""] + table + [""]
        for rule in ("covariance", "willshaw"):
            table = capacity_table(ca3, source, rule, HALF)
            if table:
                L += ["### {}, cues missing 40% of their cells".format(LABELS[rule]), ""] + table + [""]

    rerun = rerun_table(ca3, results_dir)
    if rerun:
        L += ["## E1d's 4.4% runs against E1c's", "",
              "Random patterns, the same patterns, cues and seeds as E1c. E1d reads the 50% load from",
              "a finer grid of loads, and computes the covariance weights exactly rather than summing",
              "them in float32.", ""] + rerun + [""]

    for source in ("drawings_evaluation", "drawings_background"):
        if any(key[0] == source for key in ca3):
            L += ["## How unevenly DG uses its cells: {}".format(SOURCE_NAMES[source].lower()), "",
                  "CV is the standard deviation over the mean of how many stored patterns each cell",
                  "is in, at the highest load: every character the alphabets hold. The random column",
                  "uses random patterns with the same cells, active cells and load. Means over seeds.",
                  ""] + unevenness_table(ca3, source) + [""]

    for load in COMPLETION_LOADS:
        for source in ("random", "drawings_evaluation"):
            table = completion_table(ca3, source, load)
            if len(table) > 2:
                L += ["## Completion from partial cues, {} patterns, {}".format(
                    load, SOURCE_NAMES[source].lower()), "",
                    "Percent: exact recall, then the share of the right pattern's cells on in the raw",
                    "cue and in the settled state.", ""] + table + [""]

    for source in ("random", "drawings_evaluation"):
        if any(key[0] == source for key in ca3):
            L += ["## Settling steps and fixed points, {}".format(SOURCE_NAMES[source].lower()), "",
                  "Steps that changed the state (for the pseudo-inverse, the last step that flipped a",
                  "cell), and the share of cues whose final state is a fixed point. Loads 20 and 100,",
                  "and the first tested load past the 50% load.", ""] + settling_table(ca3, source) + [""]

    for runs, title in (("official", "Lake's runs and evaluation-alphabet instance runs"),
                        ("background", "background-alphabet validation runs")):
        for match in ("study-to-test", "test-to-study"):
            table = e2e_table(runs, match, results_dir)
            if table:
                L += ["## End to end, {}, matched {}".format(title, match), "",
                      "CA3 accuracy in percent, mean over seeds, at 225 cells: 10 active (4.4%, from",
                      "E1 and E1b's files) against 5 active (2%, this run). No settling passes PR's k",
                      "most active cells straight on.", ""] + table + [""]
                stages = e2e_stage_table(runs, match, results_dir)
                if stages:
                    L += ["Every stage at 2%, clean drawings:", ""] + stages + [""]

    for source in ("random", "drawings_evaluation"):
        for n in SIZES:
            table = exact_table(ca3, source, n)
            if table:
                L += ["## Exact recall against load, {}, {:,} cells".format(
                    SOURCE_NAMES[source].lower(), n), "",
                    "Percent of cues, mean over seeds: clean cues for the local rules, 40% removed for",
                    "the pseudo-inverse.", ""] + table + [""]

    if ca3:
        L += ["## Run time", "", "Wall-clock minutes per seed on one machine, 3 threads per process.",
              ""] + times_table(ca3) + [""]
    notes = sorted({note for e in ca3.values() for note in e["record"]["notes"]
                    if "identity" not in note and "characters" not in note})
    for key in sorted(ca3, key=lambda key: (key[0], key[2], key[3], key[1])):
        r = ca3[key]["record"]
        if key[1] == "pinverse" and not r.get("complete", True):
            notes.append("{}, {} at {:,} cells with {} active stopped early, with {} seed{}: the "
                         "pseudo-inverse at this size filled the machine's memory (protocol item "
                         "14a).".format(SOURCE_NAMES[key[0]], LABELS[key[1]], key[2], key[3],
                                        len(r["seeds"]), "" if len(r["seeds"]) == 1 else "s"))
    if notes:
        L += ["## Notes", ""] + ["- " + n for n in notes] + [""]
    Path(out).write_text("\n".join(L))
    return out


# ---------- figures ----------

def _style(ax):
    ax.grid(True, color="#e6e6e3", lw=0.6)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.tick_params(labelsize=8)


def plot_capacity(ca3, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    sources = [s for s in ("random", "drawings_evaluation") if any(k[0] == s for k in ca3)]
    if not sources:
        return None
    fig, axes = plt.subplots(len(sources), 3, figsize=(13, 3.8 * len(sources)),
                             constrained_layout=True, squeeze=False)
    for i, source in enumerate(sources):
        for j, rule in enumerate(RULES):
            ax = axes[i][j]
            for s in SPARSITIES:
                xs, ys, open_x, open_y = [], [], [], []
                for n in SIZES:
                    v, kind = per_cell(ca3, source, rule, n, s)
                    if v is None or kind == "below":
                        continue
                    if kind == "above":
                        open_x.append(n)
                        open_y.append(v)
                    else:
                        xs.append(n)
                        ys.append(v)
                ax.plot(xs, ys, "-", color=SPARSITY_COLOURS[s], marker=SPARSITY_MARKERS[s],
                        ms=5, lw=1.8, label=SPARSITY_NAMES[s])
                if open_x:
                    ax.plot(open_x, open_y, linestyle="none", marker="^", ms=9, mfc="white",
                            mec=SPARSITY_COLOURS[s])
            from matplotlib.ticker import FuncFormatter, LogLocator, NullLocator
            ax.set_xscale("log")
            ax.set_yscale("log")
            sizes = [n for n in SIZES if source == "random" or n < 16000]
            ax.set_xticks(sizes)
            ax.set_xticklabels(["{:,}".format(n) for n in sizes], fontsize=8)
            ax.xaxis.set_minor_locator(NullLocator())
            ax.yaxis.set_major_locator(LogLocator(subs=(1.0, 2.0, 5.0)))
            ax.yaxis.set_minor_locator(NullLocator())
            ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: "{:g}".format(y)))
            tag = "40% removed" if rule == "pinverse" else "clean cues"
            ax.set_title("{}: {}, {}".format(SOURCE_NAMES[source], LABELS[rule], tag),
                         fontsize=9, loc="left")
            ax.set_xlabel("Cells in DG and CA3", fontsize=8)
            ax.set_ylabel("50% exact-recall load per cell", fontsize=8)
            _style(ax)
        axes[i][0].legend(fontsize=7, frameon=False)
    fig.suptitle("Load per cell at which exact recall falls to 50%, means over seeds. Open "
                 "triangles: recall stayed above 50% at every character available, a lower bound.",
                 fontsize=10)
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    plt.close(fig)
    return out


def plot_exact(ca3, out, source="random"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    sizes = [n for n in SIZES if any(k[0] == source and k[2] == n for k in ca3)]
    if not sizes:
        return None
    fig, axes = plt.subplots(len(RULES), len(sizes), figsize=(3.4 * len(sizes), 9),
                             constrained_layout=True, squeeze=False)
    for i, rule in enumerate(RULES):
        cond = capacity_cond(rule)
        for j, n in enumerate(sizes):
            ax = axes[i][j]
            for s in SPARSITIES:
                e = entry_for(ca3, source, rule, n, s)
                if e is None:
                    continue
                loads = [x for x in loads_of(e) if metric(e, x, cond, "exact") is not None]
                m = [100 * mean(metric(e, x, cond, "exact")) for x in loads]
                ax.plot(loads, m, "-", color=SPARSITY_COLOURS[s], marker=SPARSITY_MARKERS[s],
                        ms=3, lw=1.5, label="{}, k = {}".format(SPARSITY_NAMES[s], e["record"]["k"]))
            ax.axhline(50, color="#b5b5b0", lw=0.8)
            ax.set_xscale("log")
            ax.set_ylim(-2, 102)
            ax.set_title("{}, {:,} cells".format(LABELS[rule], n), fontsize=9, loc="left")
            ax.set_xlabel("Stored patterns (load)", fontsize=8)
            ax.set_ylabel("Exact recall (%), {}".format(
                "40% removed" if cond == HALF else "clean"), fontsize=8)
            _style(ax)
            ax.legend(fontsize=6, frameon=False, loc="lower left")
    fig.suptitle("{}: exact recall against load, means over seeds".format(SOURCE_NAMES[source]),
                 fontsize=10)
    fig.savefig(out)
    plt.close(fig)
    return out


def plot_completion(ca3, load, out, source="random"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    sizes = [n for n in SIZES if any(k[0] == source and k[2] == n for k in ca3)]
    if not sizes:
        return None
    fig, axes = plt.subplots(2 * len(RULES), len(sizes), figsize=(3.4 * len(sizes), 15),
                             constrained_layout=True, squeeze=False)
    xs = (0.0,) + REMOVALS
    for i, rule in enumerate(RULES):
        for j, n in enumerate(sizes):
            top, bottom = axes[2 * i][j], axes[2 * i + 1][j]
            for s in SPARSITIES:
                e = entry_for(ca3, source, rule, n, s)
                if e is None or metric(e, load, CLEAN, "exact") is None:
                    continue
                ex = [100 * mean(metric(e, load, (r, 0.0), "exact")) for r in xs]
                gain = [100 * (mean(metric(e, load, (r, 0.0), "overlap_final")) -
                               mean(metric(e, load, (r, 0.0), "overlap_cue"))) for r in xs]
                label = "{}, k = {}".format(SPARSITY_NAMES[s], e["record"]["k"])
                pct_x = [100 * r for r in xs]
                top.plot(pct_x, ex, "-", color=SPARSITY_COLOURS[s], marker=SPARSITY_MARKERS[s],
                         ms=3, lw=1.5, label=label)
                bottom.plot(pct_x, gain, "-", color=SPARSITY_COLOURS[s],
                            marker=SPARSITY_MARKERS[s], ms=3, lw=1.5, label=label)
            top.set_ylim(-2, 102)
            top.set_title("{}, {:,} cells: exact recall".format(LABELS[rule], n), fontsize=8, loc="left")
            bottom.set_title("{}, {:,} cells: overlap gained".format(LABELS[rule], n),
                             fontsize=8, loc="left")
            top.set_ylabel("Exact recall (%)", fontsize=8)
            bottom.set_ylabel("Settled minus cue overlap (points)", fontsize=8)
            bottom.set_xlabel("Cells removed from the cue (%)", fontsize=8)
            for ax in (top, bottom):
                _style(ax)
            top.legend(fontsize=6, frameon=False, loc="lower left")
    fig.suptitle("{}: completion from partial cues at {} stored patterns, means over seeds".format(
        SOURCE_NAMES[source], load), fontsize=10)
    fig.savefig(out)
    plt.close(fig)
    return out


def main():
    ca3 = load_ca3()
    print("Wrote {}".format(write_markdown(ca3).relative_to(ROOT)))
    outs = [plot_capacity(ca3, FIGURES / "e1d_capacity_per_cell.pdf"),
            plot_exact(ca3, FIGURES / "e1d_exact_recall.pdf")]
    outs += [plot_completion(ca3, load, FIGURES / "e1d_completion_{}.pdf".format(load))
             for load in COMPLETION_LOADS]
    for out in outs:
        if out:
            print("Wrote {}".format(Path(out).relative_to(ROOT)))


if __name__ == "__main__":
    main()
