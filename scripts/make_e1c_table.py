"""Builds E1c's tables and figures from results/e1c_*.json.

Writes results/e1c.md and these figures:

    figures/e1c_exact_recall.pdf      exact recall against load, each rule
                                      and size, from clean cues and from
                                      cues missing 40% of their cells
    figures/e1c_overlap_gain_<n>.pdf  overlap gained by settling against
                                      the share of cells removed, at
                                      several loads, n cells
    figures/e1c_ca1_error.pdf         CA1's reconstruction error from the
                                      settled state and from the raw cue
    figures/e1c_end_to_end.pdf        the full model: settling against no
                                      settling at each load and corruption

Lines are means over seeds and shading is one standard deviation.

Example:
    python scripts/make_e1c_table.py
"""

import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"

RULES = ("pinverse", "covariance", "willshaw")
LABELS = {"pinverse": "Pseudo-inverse", "covariance": "Covariance",
          "willshaw": "Clipped binary", "none": "No settling", "lookup": "Ideal lookup"}
SIZES = ((225, 10), (1000, 44), (4000, 178))
SOURCES = ("random", "drawings_evaluation", "drawings_background")
SOURCE_NAMES = {"random": "Random patterns", "drawings_evaluation": "Drawings, evaluation alphabets",
                "drawings_background": "Drawings, background alphabets"}
# Categorical slots 1 to 4 of the dataviz reference palette, light mode, as in E1b.
COLOURS = {"pinverse": "#2a78d6", "covariance": "#eb6834", "willshaw": "#1baf7a",
           "none": "#eda100", "lookup": "#3d3d3a"}
MARKERS = {"pinverse": "o", "covariance": "s", "willshaw": "^", "none": "D", "lookup": "x"}
LOAD_SHADES = ("#9ec5f0", "#5a9be3", "#2a78d6", "#1a4f91", "#0c2a52", "#000000")
REMOVALS = (0.0, 0.2, 0.4, 0.6, 0.8)
CLEAN, HALF = (0.0, 0.0), (0.4, 0.0)
# The planned loads. Random patterns also run at added loads near where
# each rule fails; drawings cap at the characters available.
STANDARD = (20, 50, 100, 200, 500, 1000)
STANDARD_MAX = 1000


def load_ca3(results_dir=RESULTS):
    """{(source, rule, units): {(load, remove, add): row}} from the CA3 harness."""
    out = {}
    for path in sorted(Path(results_dir).glob("e1c_ca3_*.json")):
        r = json.loads(path.read_text())
        source = r["source"] if r["source"] == "random" else "drawings_" + r["split"]
        out[(source, r["rule"], r["units"])] = {
            "file": path.name, "record": r,
            "rows": {(row["load"], row["remove"], row["add"]): row for row in r["rows"]}}
    return out


def load_e2e(results_dir=RESULTS):
    """{(rule, load, kind): record} from the end-to-end runs, evaluation split."""
    out = {}
    for path in sorted(Path(results_dir).glob("e1c_e2e_evaluation_*.json")):
        r = json.loads(path.read_text())
        out[(r["rule"], r["load"], r["kind"])] = r
    return out


def mean(values):
    return statistics.mean(values)


def sd(values):
    return statistics.stdev(values) if len(values) > 1 else 0.0


def cell(ca3, source, rule, units, load, cond, metric):
    entry = ca3.get((source, rule, units))
    if entry is None:
        return None
    row = entry["rows"].get((load, cond[0], cond[1]))
    return None if row is None else row["per_seed"].get(metric)


def pct(values, digits=1):
    if values is None:
        return "–"
    return "{:.{d}f}".format(100 * mean(values), d=digits)


def pct_sd(values):
    if values is None:
        return "–"
    return "{:.1f} ± {:.1f}".format(100 * mean(values), 100 * sd(values))


def loads_for(ca3, source, units):
    loads = set()
    for rule in RULES:
        entry = ca3.get((source, rule, units))
        if entry:
            loads |= {key[0] for key in entry["rows"]}
    return sorted(loads)


def capacity_loads(ca3, source, rule, units):
    """Loads that count toward capacity. For the pseudo-inverse, loads of n
    or more are left out: its weights are then the identity matrix and every
    state is a fixed point, so a clean cue is recalled without completion."""
    loads = loads_for(ca3, source, units)
    return [n for n in loads if n < units] if rule == "pinverse" else loads


def capacity(ca3, source, rule, units, cond, bar=0.95):
    """The largest load reached with exact recall at or above the bar at
    every smaller tested load, or None."""
    best = None
    for load in capacity_loads(ca3, source, rule, units):
        v = cell(ca3, source, rule, units, load, cond, "exact")
        if v is None:
            continue
        if mean(v) >= bar:
            best = load
        else:
            break
    return best


def exact_table(ca3, source):
    lines = ["| cells, on | load | " + " | ".join(
        "{} clean".format(LABELS[r]) for r in RULES) + " | " + " | ".join(
        "{} 40% removed".format(LABELS[r]) for r in RULES) + " | Ideal lookup 40% removed |",
        "|---|---|" + "---|" * 7]
    for units, k in SIZES:
        for load in loads_for(ca3, source, units):
            tag = "" if load in STANDARD or source != "random" else " (added)"
            row = ["{:,}, {}".format(units, k), "{:,}{}".format(load, tag)]
            row += [pct(cell(ca3, source, r, units, load, CLEAN, "exact")) for r in RULES]
            row += [pct(cell(ca3, source, r, units, load, HALF, "exact")) for r in RULES]
            lookups = [cell(ca3, source, r, units, load, HALF, "ident_cue") for r in RULES]
            lookups = [v for v in lookups if v is not None]
            row.append(pct(lookups[0]) if lookups else "–")
            lines.append("| " + " | ".join(row) + " |")
    return lines


def half_load(ca3, source, rule, units, cond):
    """Load at which exact recall first falls through 50%, interpolated on a
    log scale between the two tested loads around it. Returns None when
    recall never falls below 50%, and 0 when it starts below."""
    import math
    prev = None
    for load in capacity_loads(ca3, source, rule, units):
        v = cell(ca3, source, rule, units, load, cond, "exact")
        if v is None:
            continue
        m = mean(v)
        if m < 0.5:
            if prev is None:
                return 0
            (l0, m0) = prev
            t = (m0 - 0.5) / (m0 - m)
            return math.exp(math.log(l0) + t * (math.log(load) - math.log(l0)))
        prev = (load, m)
    return None


def half_table(ca3, source):
    lines = ["| cells, on | " + " | ".join(
        "{} clean | {} 40% removed".format(LABELS[r], LABELS[r]) for r in RULES) + " |",
        "|---|" + "---|" * 6]
    for units, k in SIZES:
        if not loads_for(ca3, source, units):
            continue
        row = ["{:,}, {}".format(units, k)]
        for r in RULES:
            for cond in (CLEAN, HALF):
                if (source, r, units) not in ca3:
                    row.append("–")
                    continue
                h = half_load(ca3, source, r, units, cond)
                if h is None:
                    row.append("above {:,}".format(max(capacity_loads(ca3, source, r, units))))
                elif h == 0:
                    row.append("below {:,}".format(loads_for(ca3, source, units)[0]))
                else:
                    row.append("{:,.0f} ({:.2f} per cell)".format(h, h / units))
        lines.append("| " + " | ".join(row) + " |")
    return lines


def capacity_table(ca3, source):
    lines = ["| cells, on | " + " | ".join(
        "{} clean | {} 40% removed".format(LABELS[r], LABELS[r]) for r in RULES) + " |",
        "|---|" + "---|" * 6]
    for units, k in SIZES:
        if not loads_for(ca3, source, units):
            continue
        row = ["{:,}, {}".format(units, k)]
        for r in RULES:
            for cond in (CLEAN, HALF):
                if (source, r, units) not in ca3:
                    row.append("–")
                    continue
                c = capacity(ca3, source, r, units, cond)
                top = max(capacity_loads(ca3, source, r, units))
                if c is None:
                    row.append("below {}".format(loads_for(ca3, source, units)[0]))
                elif c == top:
                    row.append("{:,} or more ({:.2f} per cell)".format(c, c / units))
                else:
                    row.append("{:,} ({:.2f} per cell)".format(c, c / units))
        lines.append("| " + " | ".join(row) + " |")
    return lines


def damage_table(ca3, source, units, rule, loads):
    """Overlap with the right pattern, raw cue and settled, under each damage."""
    entry = ca3.get((source, rule, units))
    if entry is None:
        return []
    conds = sorted({(key[1], key[2]) for key in entry["rows"]}, key=lambda c: (c[1] > 0, c))
    lines = ["| removed | stray added | " + " | ".join(
        "load {:,}: cue → settled (exact, lookup cue, lookup settled)".format(n) for n in loads) + " |",
        "|---|---|" + "---|" * len(loads)]
    for cond in conds:
        row = ["{:.0%}".format(cond[0]), "{:.0%}".format(cond[1])]
        for n in loads:
            oc = cell(ca3, source, rule, units, n, cond, "overlap_cue")
            of = cell(ca3, source, rule, units, n, cond, "overlap_final")
            ex = cell(ca3, source, rule, units, n, cond, "exact")
            lk = cell(ca3, source, rule, units, n, cond, "ident_cue")
            if oc is None:
                row.append("–")
                continue
            sc = cell(ca3, source, rule, units, n, cond, "stray_cue")
            sf = cell(ca3, source, rule, units, n, cond, "stray_final")
            text = "{} → {}".format(pct(oc, 0), pct(of, 0))
            if cond[1] > 0:
                text += " [stray {} → {}]".format(pct(sc, 0), pct(sf, 0))
            lf = cell(ca3, source, rule, units, n, cond, "ident_final")
            text += " ({}, {}, {})".format(pct(ex, 0), pct(lk, 0), pct(lf, 0))
            row.append(text)
        lines.append("| " + " | ".join(row) + " |")
    return lines


def ca1_table(ca3, rule, loads, source="drawings_evaluation", units=225):
    entry = ca3.get((source, rule, units))
    if entry is None:
        return []
    conds = sorted({(key[1], key[2]) for key in entry["rows"]}, key=lambda c: (c[1] > 0, c))
    lines = ["| removed | stray added | " + " | ".join(
        "load {:,}: cue, settled, lookup, perfect, mean drawing".format(n) for n in loads) + " |",
        "|---|---|" + "---|" * len(loads)]
    for cond in conds:
        row = ["{:.0%}".format(cond[0]), "{:.0%}".format(cond[1])]
        for n in loads:
            vals = [cell(ca3, source, rule, units, n, cond, m)
                    for m in ("ca1_cue", "ca1_final", "ca1_lookup", "ca1_target", "ca1_mean")]
            if vals[0] is None:
                row.append("–")
            else:
                row.append(", ".join("–" if v is None else "{:.4f}".format(mean(v))
                                     for v in vals))
        lines.append("| " + " | ".join(row) + " |")
    return lines


def e2e_table(e2e, kind, direction):
    lines = ["| load | level | VC | PR | " + " | ".join(
        "{} settled | {} gap".format(LABELS[r], LABELS[r]) for r in RULES) + " | No settling |",
        "|---|---|---|---|" + "---|" * 7]
    for load in (20, 100, 200):
        recs = {r: e2e.get((r, load, kind)) for r in RULES}
        ref = next((v for v in recs.values() if v), None)
        if ref is None:
            continue
        for j, lv in enumerate(ref["levels"]):
            ps = lv["per_seed"]
            row = [str(load), "{:g}".format(lv["level"]),
                   pct(ps["vc " + direction]), pct(ps["pr " + direction])]
            for r in RULES:
                rec = recs[r]
                if rec is None:
                    row += ["–", "–"]
                    continue
                p = rec["levels"][j]["per_seed"]
                gap = [a - b for a, b in zip(p["pc " + direction], p["pc_none " + direction])]
                wins = sum(g > 0 for g in gap)
                row += [pct_sd(p["pc " + direction]),
                        "{:+.1f} ({}/{})".format(100 * mean(gap), wins, len(gap))]
            row.append(pct_sd(ps["pc_none " + direction]))
            lines.append("| " + " | ".join(row) + " |")
    return lines


def e2e_ca3_table(e2e, kind):
    lines = ["| load | level | PR top cells overlap | " + " | ".join(
        "{} settled overlap, exact".format(LABELS[r]) for r in RULES) +
        " | Covariance from PR as given, test-to-study | Recall-loss no settling | " +
        " | ".join("Recall-loss {}".format(LABELS[r]) for r in RULES) + " |",
        "|---|---|---|" + "---|" * 3 + "---|---|" + "---|" * 3]
    for load in (20, 100, 200):
        recs = {r: e2e.get((r, load, kind)) for r in RULES}
        cov = recs.get("covariance")
        if cov is None:
            continue
        for j, lv in enumerate(cov["levels"]):
            ps = lv["per_seed"]
            row = [str(load), "{:g}".format(lv["level"]), pct(ps["overlap_start"])]
            for r in RULES:
                rec = recs[r]
                if rec is None:
                    row.append("–")
                    continue
                p = rec["levels"][j]["per_seed"]
                row.append("{}, {}".format(pct(p["overlap_final"]), pct(p["exact"])))
            row.append(pct(ps.get("pc_cue test-to-study")))
            row.append("{:.4f}".format(mean(ps["recall_loss_none"])))
            for r in RULES:
                rec = recs[r]
                row.append("–" if rec is None else
                           "{:.4f}".format(mean(rec["levels"][j]["per_seed"]["recall_loss"])))
            lines.append("| " + " | ".join(row) + " |")
    return lines


def seeds_note(ca3, source):
    parts = []
    for units, _ in SIZES:
        for r in RULES:
            entry = ca3.get((source, r, units))
            if entry:
                parts.append((units, len(entry["record"]["seeds"])))
                break
    return ", ".join("{} seeds at {:,} cells".format(s, u) for u, s in parts)


def notes(ca3, source):
    """Notes on loads the cell count or the alphabets limit, from the records."""
    out, available = [], None
    sizes = []
    for (src, rule, units), entry in sorted(ca3.items(), key=lambda kv: kv[0][2]):
        if src != source:
            continue
        available = available or entry["record"].get("characters_available")
        if rule == "pinverse" and max(entry["record"]["loads"]) >= units and units not in sizes:
            sizes.append(units)
    if available:
        out.append("The alphabets hold {:,} characters, so the largest load uses all {:,}, one "
                   "drawing each.".format(available, available))
    if sizes:
        out.append("For the pseudo-inverse, loads of n or more (here {}) make its weights the "
                   "identity matrix: every state is a fixed point, so a clean cue counts as exact "
                   "recall without any completion. Capacity below leaves those loads out.".format(
                       ", ".join("{:,} at {:,} cells".format(u, u) for u in sizes)))
    return out


def write_markdown(ca3, e2e, out=RESULTS / "e1c.md"):
    L = []
    L += ["# E1c: CA3 recall without a list of memories", "",
          "A nearest-memory lookup compares a cue with a list of every stored memory and picks",
          "the one sharing the most active cells. For a cue with random damage it is the best",
          "decoder possible, so it is the ceiling here. CA3 holds no list: it settles from the",
          "cue through its recurrent weights. These tables measure how close settling comes to",
          "that ceiling as the number of stored memories (the load) grows, and whether the",
          "settled pattern lets CA1 rebuild the drawing better than the raw cue does.", "",
          "Terms used below:", "",
          "- **Exact recall:** CA3's final state has exactly the right stored pattern's cells on",
          "  and no others. No list is consulted.",
          "- **Overlap:** the share of the right pattern's k active cells that are on, for the raw",
          "  cue or for the final state. **Stray:** cells on outside the right pattern, over k.",
          "- **Ideal lookup:** the stored pattern sharing the most cells with the raw cue is the",
          "  right one. Ties count as 1 over the number tied.",
          "- **Clean cue:** the stored pattern itself. **40% removed:** 40% of its k cells",
          "  switched off at random.",
          "- **Rules:** pseudo-inverse is AHA's rule, run on −1/+1 patterns with AHA's tanh",
          "  settling. Covariance and clipped binary synapses are the local rules from E1, with",
          "  k-winners-take-all settling that starts from the cue as given.",
          "- **CA1 error:** mean squared error between CA1's reconstruction and the clean drawing.",
          "", "Every choice is listed in `docs/e1c_protocol.md`. Made by `scripts/make_e1c_table.py`.",
          ""]

    for source in ("random", "drawings_evaluation"):
        if not any(k[0] == source for k in ca3):
            continue
        L += ["## {}: exact recall against load".format(SOURCE_NAMES[source]), "",
              "Percent of cues, mean over seeds ({}).".format(seeds_note(ca3, source)), ""]
        L += exact_table(ca3, source) + [""]
        for note in notes(ca3, source):
            L += ["- " + note]
        L += ["", "Largest load at which exact recall stays at or above 95% at every tested",
              "load up to it, and that load per cell:", ""]
        L += capacity_table(ca3, source) + [""]
        L += ["Load at which exact recall falls to 50%, interpolated on a log scale between",
              "the two tested loads around it, and that load per cell:", ""]
        L += half_table(ca3, source) + [""]

    for source in ("random", "drawings_evaluation"):
        for units, _ in SIZES:
            loads = [n for n in loads_for(ca3, source, units) if n <= STANDARD_MAX]
            if not loads:
                continue
            show = [n for n in loads if n in (20, 100, 200, 500, 659, 964, 1000)]
            L += ["## {}, {:,} cells: completion under damage".format(SOURCE_NAMES[source], units),
                  "", "Each cell: overlap of raw cue → overlap of settled state, in percent; for",
                  "stray-cell damage, stray share of raw cue → settled; then exact recall, the",
                  "ideal lookup from the raw cue and the same lookup from the settled state, in",
                  "percent.", ""]
            for rule in RULES:
                rows = damage_table(ca3, source, units, rule, show)
                if rows:
                    L += ["### {}".format(LABELS[rule]), ""] + rows + [""]

    if any(k[0] == "drawings_evaluation" and k[2] == 225 for k in ca3):
        loads = loads_for(ca3, "drawings_evaluation", 225)
        L += ["## CA1 reconstruction from the settled state and from the raw cue", "",
              "Drawings from the evaluation alphabets, 225 cells. CA1 is trained on the stored",
              "patterns as AHA trains it. Each cell lists CA1 error from the raw cue, from the",
              "settled state, from the pattern the ideal lookup picks, and from the right stored",
              "pattern itself (the floor), then the error of the mean stored drawing, the best",
              "guess with no memory at all. Lower is better.", ""]
        for rule in RULES:
            rows = ca1_table(ca3, rule, loads)
            if rows:
                L += ["### {}".format(LABELS[rule]), ""] + rows + [""]

    if any(k[0] == "drawings_background" for k in ca3):
        L += ["## Check: background-alphabet drawings", "",
              "The same harness on DG patterns of background-alphabet drawings, 5 seeds. No",
              "setting was chosen from these runs.", ""]
        L += exact_table(ca3, "drawings_background") + [""]
        for note in notes(ca3, "drawings_background"):
            L += ["- " + note]
        L += [""]

    if e2e:
        L += ["## End to end: the full model at higher loads", "",
              "The model studies N drawings, one each of N characters from the evaluation",
              "alphabets, then recalls each from an occluded or noisy copy. 5 seeds; each seed",
              "studies about 400 drawings in runs of N. Settled is CA3 accuracy with settling;",
              "gap is settled minus no settling in points, paired by seed, with the seeds where",
              "settling scored higher in brackets. No settling passes PR's 10 most active cells",
              "straight on.", ""]
        for kind in ("occlusion", "noise"):
            for direction in ("test-to-study", "study-to-test"):
                rows = e2e_table(e2e, kind, direction)
                if len(rows) > 2:
                    L += ["### {}, matched {}".format(kind.capitalize(), direction), ""] + rows + [""]
            rows = e2e_ca3_table(e2e, kind)
            if len(rows) > 2:
                L += ["### {}: CA3 states and recall-loss".format(kind.capitalize()), "",
                      "PR top cells overlap is the share of the right stored pattern's 10 cells",
                      "among PR's 10 most active cells, which is where settling starts. Settled",
                      "overlap and exact recall follow, then test-to-study accuracy when the",
                      "covariance rule settles from the PR output as given. Recall-loss is CA1's",
                      "error against the clean drawing.", ""] + rows + [""]

    Path(out).write_text("\n".join(L))
    return out


def _style(ax):
    ax.grid(True, color="#e6e6e3", lw=0.6)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.tick_params(labelsize=8)


def _band(ax, x, values, colour, label, marker=None, style="-"):
    m = [mean(v) for v in values]
    s = [sd(v) for v in values]
    ax.plot(x, m, style, color=colour, lw=1.8, marker=marker, ms=4, label=label)
    ax.fill_between(x, [a - b for a, b in zip(m, s)], [a + b for a, b in zip(m, s)],
                    color=colour, alpha=0.15, lw=0)


def plot_exact(ca3, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    sources = [s for s in ("random", "drawings_evaluation") if any(k[0] == s for k in ca3)]
    if not sources:
        return None
    fig, axes = plt.subplots(len(sources), 3, figsize=(13, 3.6 * len(sources)),
                             constrained_layout=True, squeeze=False)
    for i, source in enumerate(sources):
        for j, (units, k) in enumerate(SIZES):
            ax = axes[i][j]
            for rule in RULES:
                loads = [n for n in loads_for(ca3, source, units)
                         if cell(ca3, source, rule, units, n, CLEAN, "exact") is not None]
                if not loads:
                    continue
                for cond, style, tag in ((CLEAN, "-", "clean"), (HALF, "--", "40% removed")):
                    _band(ax, loads, [[100 * v for v in cell(ca3, source, rule, units, n, cond,
                                                             "exact")] for n in loads],
                          COLOURS[rule], "{}, {}".format(LABELS[rule], tag), MARKERS[rule], style)
            loads = loads_for(ca3, source, units)
            if loads:
                vals = []
                for n in loads:
                    v = None
                    for rule in RULES:
                        v = v or cell(ca3, source, rule, units, n, HALF, "ident_cue")
                    vals.append([100 * x for x in v])
                _band(ax, loads, vals, COLOURS["lookup"], "Ideal lookup, 40% removed",
                      MARKERS["lookup"], ":")
                ax.axvline(units, color="#b5b5b0", lw=0.8)
            ax.set_xscale("log")
            if loads:
                from matplotlib.ticker import NullLocator
                ax.set_xticks(loads)
                ax.set_xticklabels(["{:,}".format(n) for n in loads], rotation=45, fontsize=7)
                ax.xaxis.set_minor_locator(NullLocator())
            ax.set_ylim(-2, 102)
            ax.set_title("{}, {:,} cells, {} on".format(SOURCE_NAMES[source], units, k),
                         fontsize=9, loc="left")
            ax.set_xlabel("Stored patterns (load); grey line: load = cells, where the pseudo-inverse weights become the identity", fontsize=7)
            ax.set_ylabel("Exact recall (%)", fontsize=8)
            _style(ax)
    axes[0][0].legend(fontsize=6.5, frameon=False, loc="lower left")
    fig.suptitle("Exact recall against load: clean cues (solid) and cues missing 40% of their "
                 "cells (dashed), mean ± 1 std over seeds", fontsize=10)
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    plt.close(fig)
    return out


def plot_overlap_gain(ca3, units, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    sources = [s for s in ("random", "drawings_evaluation") if (s, "covariance", units) in ca3]
    if not sources:
        return None
    fig, axes = plt.subplots(len(sources), 3, figsize=(13, 3.4 * len(sources)),
                             constrained_layout=True, squeeze=False)
    for i, source in enumerate(sources):
        loads = [n for n in loads_for(ca3, source, units) if n <= STANDARD_MAX]
        for j, rule in enumerate(RULES):
            ax = axes[i][j]
            for shade, n in zip(LOAD_SHADES, loads):
                vals = []
                for r in REMOVALS:
                    oc = cell(ca3, source, rule, units, n, (r, 0.0), "overlap_cue")
                    of = cell(ca3, source, rule, units, n, (r, 0.0), "overlap_final")
                    vals.append(None if oc is None else [100 * (b - a) for a, b in zip(oc, of)])
                if None in vals:
                    continue
                _band(ax, [100 * r for r in REMOVALS], vals, shade, "load {:,}".format(n), "o")
            ax.axhline(0, color="#b5b5b0", lw=0.8)
            ax.set_title("{}: {}".format(SOURCE_NAMES[source], LABELS[rule]), fontsize=9, loc="left")
            ax.set_xlabel("Share of the pattern's cells removed (%)", fontsize=8)
            ax.set_ylabel("Overlap gained by settling (points)", fontsize=8)
            _style(ax)
        axes[i][0].legend(fontsize=7, frameon=False)
    fig.suptitle("Overlap with the right memory, settled minus raw cue, {:,} cells, "
                 "mean ± 1 std over seeds".format(units), fontsize=10)
    fig.savefig(out)
    plt.close(fig)
    return out


def plot_ca1(ca3, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    source, units = "drawings_evaluation", 225
    if (source, "covariance", units) not in ca3:
        return None
    loads = [n for n in loads_for(ca3, source, units) if n in (20, 100, 200, 659)]
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.6), constrained_layout=True)
    for ax, rule in zip(axes, RULES):
        for shade, n in zip(LOAD_SHADES[1::2] + LOAD_SHADES[:1], loads):
            for metric, style, tag in (("ca1_cue", "--", "raw cue"), ("ca1_final", "-", "settled")):
                vals = [cell(ca3, source, rule, units, n, (r, 0.0), metric) for r in REMOVALS]
                if None in vals:
                    continue
                _band(ax, [100 * r for r in REMOVALS], vals, shade,
                      "load {:,}, {}".format(n, tag), "o", style)
        ax.set_title("{}".format(LABELS[rule]), fontsize=9, loc="left")
        ax.set_xlabel("Share of the pattern's cells removed (%)", fontsize=8)
        ax.set_ylabel("CA1 error against the clean drawing (MSE)", fontsize=8)
        _style(ax)
    axes[0].legend(fontsize=6.5, frameon=False)
    fig.suptitle("CA1 reconstruction from the settled state (solid) and the raw cue (dashed), "
                 "evaluation-alphabet drawings, 225 cells", fontsize=10)
    fig.savefig(out)
    plt.close(fig)
    return out


def plot_e2e(e2e, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    if not e2e:
        return None
    fig, axes = plt.subplots(2, 3, figsize=(13, 7), constrained_layout=True)
    for i, kind in enumerate(("occlusion", "noise")):
        for j, load in enumerate((20, 100, 200)):
            ax = axes[i][j]
            ref = None
            for rule in RULES:
                rec = e2e.get((rule, load, kind))
                if rec is None:
                    continue
                ref = rec
                x = [lv["level"] for lv in rec["levels"]]
                _band(ax, x, [[100 * v for v in lv["per_seed"]["pc test-to-study"]]
                              for lv in rec["levels"]], COLOURS[rule], LABELS[rule], MARKERS[rule])
            if ref is None:
                continue
            x = [lv["level"] for lv in ref["levels"]]
            _band(ax, x, [[100 * v for v in lv["per_seed"]["pc_none test-to-study"]]
                          for lv in ref["levels"]], COLOURS["none"], LABELS["none"],
                  MARKERS["none"], "--")
            _band(ax, x, [[100 * v for v in lv["per_seed"]["pr test-to-study"]]
                          for lv in ref["levels"]], "#8a8a85", "PR", None, ":")
            ax.set_ylim(0, 102)
            ax.set_title("{}, {} drawings studied".format(kind.capitalize(), load),
                         fontsize=9, loc="left")
            ax.set_xlabel("Circle diameter over image side" if kind == "occlusion"
                          else "Share of pixels replaced", fontsize=8)
            ax.set_ylabel("CA3 accuracy, test-to-study (%)", fontsize=8)
            _style(ax)
    axes[0][0].legend(fontsize=7, frameon=False)
    fig.suptitle("Full model at higher loads: settling against no settling, "
                 "mean ± 1 std over 5 seeds", fontsize=10)
    fig.savefig(out)
    plt.close(fig)
    return out


def main():
    ca3, e2e = load_ca3(), load_e2e()
    print("Wrote {}".format(write_markdown(ca3, e2e).relative_to(ROOT)))
    outs = [plot_exact(ca3, FIGURES / "e1c_exact_recall.pdf")]
    outs += [plot_overlap_gain(ca3, units, FIGURES / "e1c_overlap_gain_{}.pdf".format(units))
             for units, _ in SIZES]
    outs += [plot_ca1(ca3, FIGURES / "e1c_ca1_error.pdf"), plot_e2e(e2e, FIGURES / "e1c_end_to_end.pdf")]
    for out in outs:
        if out:
            print("Wrote {}".format(Path(out).relative_to(ROOT)))


if __name__ == "__main__":
    main()
