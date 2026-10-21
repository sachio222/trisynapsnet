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


def v(name, key, level=0, scale=100):
    """Mean over seeds of one key in one file, in percent by default."""
    rec = load(name)
    return scale * statistics.mean(rec["per_seed"][level][key])


def diff(name, a, b, stage, d, level):
    """Mean settling-minus-no-settling and how many seeds it helps."""
    st = load(name)["per_seed"][level]
    xs = [100 * (x - y) for x, y in zip(st["{} {} {}".format(a, stage, d)],
                                       st["{} {} {}".format(b, stage, d)])]
    return statistics.mean(xs), sum(x > 0 for x in xs), len(xs)


def level_index(name, kind, level):
    for i, lv in enumerate(load(name)["levels"]):
        if lv["kind"] == kind and abs(lv["level"] - level) < 1e-9:
            return i
    raise KeyError((kind, level))


def best_effect(name, stage, d, pairs=(("pp_cov", "pp_cov_none"), ("pp_wil", "pp_wil_none"))):
    best = (-1e9, None)
    for a, b in pairs:
        for i, lv in enumerate(load(name)["levels"]):
            m, pos, n = diff(name, a, b, stage, d, i)
            if m > best[0]:
                best = (m, (RULE_LABEL[a], level_label(lv), pos, n))
    return best


def max_gap(name, arms):
    worst = 0.0
    for store in load(name)["per_seed"]:
        for arm in arms:
            for d in DIRECTIONS:
                g = 100 * (statistics.mean(store["{} ca1 {}".format(arm, d)])
                           - statistics.mean(store["{} ca3 {}".format(arm, d)]))
                worst = g if abs(g) > abs(worst) else worst
    return worst


RULE_LABEL = {"pp_cov": "covariance perforant path", "pp_wil": "clipped binary perforant path"}

ALL_FILES = (list(GRID_FILES) + [
    "e3_classification_background_225_5", "e3_instance_background_225_5",
    "e3_classification_official_225_5", "e3_instance_official_225_5"] +
    ["e3_load_official_n{}_225_5".format(n) for n in (20, 50, 100, 200)] +
    ["e3_classification_official_225_10", "e3_instance_official_225_10",
     "e3_classification_background_225_5_share1"])


def build():
    L5, I5 = "e3_classification_official_225_5", "e3_instance_official_225_5"
    L10, I10 = "e3_classification_official_225_10", "e3_instance_official_225_10"
    missing = [n for n in ALL_FILES if load(n) is None or not load(n)["complete"]]
    if missing:
        raise SystemExit("Unfinished: {}".format(", ".join(missing)))
    tts, stt = "test-to-study", "study-to-test"
    o3, o5, n3 = (level_index(I5, "occlusion", 0.3), level_index(I5, "occlusion", 0.5),
                  level_index(I5, "noise", 0.3))
    loads = {n: load("e3_load_official_n{}_225_5".format(n)) for n in (20, 50, 100, 200)}
    ca3_best = best_effect(I5, "ca3", tts)
    ca1_best = best_effect(I5, "ca1", tts)
    settle_arms = ("pr_none", "pr_cov", "pr_wil", "pp_cov", "pp_wil")
    gap_settle = max([max_gap(n, settle_arms) for n in (L5, I5)], key=abs)
    gap_none = max([max_gap(n, ("pp_cov_none", "pp_wil_none")) for n in (L5, I5)], key=abs)
    gap_pr10 = max_gap(I10, ("pr_none",))
    stt_cost = min(diff(I5, a, b, "ca3", stt, i)[0] for a, b in PAIRS[:2]
                   for i in range(len(load(I5)["levels"])))
    S1 = "e3_classification_background_225_5_share1"
    SB = "e3_classification_background_225_5"
    eff = lambda n, a, b, st, i: diff(n, a, b, st, tts, i)
    hrs = hours(ALL_FILES)

    f = {}
    f["prc"], f["prt"] = v(L5, "pr_cov ca1 " + stt), v(L5, "pr_cov ca1 " + tts)
    f["ppc"], f["ppt"] = v(L5, "pp_wil ca1 " + stt), v(L5, "pp_wil ca1 " + tts)
    f["ppcc"], f["ppct"] = v(L5, "pp_cov ca1 " + stt), v(L5, "pp_cov ca1 " + tts)
    f["look_w"], f["look_c"] = v(L5, "pp_wil_none ident_cue"), v(L5, "pp_cov_none ident_cue")
    f["vc_s"], f["vc_t"] = v(L5, "vc " + stt), v(L5, "vc " + tts)
    f["prn_s"], f["prn_t"] = v(L5, "pr_none ca3 " + stt), v(L5, "pr_none ca3 " + tts)
    f["wn_s"], f["wn_t"] = v(L5, "pp_wil_none ca3 " + stt), v(L5, "pp_wil_none ca3 " + tts)
    f["cn_s"], f["cn_t"] = v(L5, "pp_cov_none ca3 " + stt), v(L5, "pp_cov_none ca3 " + tts)
    f["i_wn0"], f["i_pr0"] = v(I5, "pp_wil_none ca3 " + tts, 0), v(I5, "pr_none ca3 " + tts, 0)
    f["i_wn3"], f["i_pr3"] = v(I5, "pp_wil_none ca3 " + tts, o3), v(I5, "pr_none ca3 " + tts, o3)
    f["i_wn5"], f["i_pr5"] = v(I5, "pp_wil_none ca3 " + tts, o5), v(I5, "pr_none ca3 " + tts, o5)
    f["is_wn5"], f["is_pr5"] = v(I5, "pp_wil_none ca3 " + stt, o5), v(I5, "pr_none ca3 " + stt, o5)
    f["i_wnn"], f["i_cnn"], f["i_prn"] = (v(I5, "pp_wil_none ca3 " + tts, n3),
                                          v(I5, "pp_cov_none ca3 " + tts, n3),
                                          v(I5, "pr_none ca3 " + tts, n3))
    f["cue_w0"], f["cue_c0"] = v(I5, "pp_wil_none overlap_cue", 0), v(I5, "pp_cov_none overlap_cue", 0)
    f["cue_w3"], f["fin_w3"] = v(I5, "pp_wil_none overlap_cue", o3), v(I5, "pp_wil overlap_final", o3)
    f["ex_w3n"], f["ex_w3"] = v(I5, "pp_wil_none exact", o3), v(I5, "pp_wil exact", o3)
    f["cue_prn"], f["cue_wn"] = v(I5, "pr_none overlap_cue", n3), v(I5, "pp_wil_none overlap_cue", n3)
    f["c0"], f["c3"] = eff(I5, "pp_cov", "pp_cov_none", "ca1", 0), eff(I5, "pp_cov", "pp_cov_none", "ca1", o3)
    f["w3"], f["w5"] = eff(I5, "pp_wil", "pp_wil_none", "ca1", o3), eff(I5, "pp_wil", "pp_wil_none", "ca1", o5)
    f["w3_ca1n"], f["w3_ca3n"] = v(I5, "pp_wil_none ca1 " + tts, o3), v(I5, "pp_wil_none ca3 " + tts, o3)
    f["w3_ca1"] = v(I5, "pp_wil ca1 " + tts, o3)
    f["prc1"] = max(eff(I5, a, "pr_none", "ca1", i)[0] for a in ("pr_cov", "pr_wil")
                    for i in range(len(load(I5)["levels"])))
    f["ex_load"] = [v("e3_load_official_n{}_225_5".format(n), "pp_wil exact", 0) for n in (20, 50, 100, 200)]
    f["ld"] = {n: [diff("e3_load_official_n{}_225_5".format(n), a, b, "ca1", tts, i)[0]
                   for a, b in PAIRS[:2] for i, lv in enumerate(loads[n]["levels"])
                   if lv["kind"] in ("none", "occlusion")] for n in loads}
    f["l10c"], f["l10w"], f["l10p"] = (v(L10, "pp_cov ca3 " + tts), v(L10, "pp_wil ca3 " + tts),
                                       v(L10, "pr_cov ca3 " + tts))
    f["l5c"], f["l5w"] = v(L5, "pp_cov ca3 " + tts), v(L5, "pp_wil ca3 " + tts)
    f["i10"] = best_effect(I10, "ca1", tts)
    f["s1"] = max(v(S1, "pp_cov ca3 " + tts), v(S1, "pp_wil ca3 " + tts))
    f["sb"] = max(v(SB, "pp_cov ca3 " + tts), v(SB, "pp_wil ca3 " + tts))
    f["sbp"] = v(SB, "pr_cov ca3 " + tts)

    def e(t):
        return "{:+.1f} points ({} of {} seeds)".format(t[0], t[1], t[2])

    up = [max(f["ld"][n]) for n in (20, 50, 100, 200)]
    lines = []
    w = lines.append
    w("# E3 results")
    w("")
    w("E3 replaces PR, the path from entorhinal cortex (EC) into CA3 that AHA trains by "
      "backpropagation, with a perforant path that learns each drawing in one presentation, and asks "
      "whether CA3's settling then helps end to end. The protocol, with every choice, source and free "
      "parameter, is `docs/e3_protocol.md`; the numbers come from `results/e3_*.json`. Built by "
      "`scripts/make_e3_table.py`.")
    w("")
    w("**Main result.** With the perforant path, CA3's settling turns a partial cue into the exact stored "
      "pattern, and BTSP CA1 then returns the right drawing's EC code far more often: on the instance "
      "task, matched test-to-study, settling adds up to {:+.1f} points at the CA1 stage ({}, {} drawings, higher in {} of {} "
      "seeds). Scored at CA3 itself it adds at most {:+.1f} points, because matching a CA3 state against "
      "the stored patterns already finds the nearest memory. The fully local model recognises a new "
      "drawing of a studied character far less often than the PR model: {:.1f}% against {:.1f}% on "
      "Lake's runs at the CA1 stage, matched test-to-study.".format(
          ca1_best[0], ca1_best[1][0], ca1_best[1][1], ca1_best[1][2], ca1_best[1][3],
          ca3_best[0], f["ppt"], f["prt"]))
    w("")
    w("## Terms")
    w("")
    w("- **DG**, the dentate gyrus, gives each drawing a sparse pattern; CA3 stores it. Here 5 of 225 "
      "cells are on (2%), with 10 (4.4%, AHA's value) as a check.")
    w("- **Settling**: CA3 updates its cells from their recurrent input, keeping the k most driven, until "
      "the state stops changing. Settling from a cue with missing or wrong cells onto the full stored "
      "pattern is **pattern completion**.")
    w("- **Perforant path**: EC to CA3. Each CA3 cell hears from 710 of the 20,449 EC units (3,750 "
      "synapses per rat CA3 cell over 108,000 rat EC layer II cells), and the synapses learn the EC code "
      "against the CA3 pattern DG imposes, with clipped binary synapses or the covariance rule. Its drive "
      "picks the cue cells.")
    w("- **No settling** passes the cue straight on to CA1.")
    w("- **CA3 stage, CA1 stage, PM stage**: which state is matched. CA1 is E4's one-shot BTSP CA1 "
      "(2,118 cells), which returns an EC code; PM is AHA's CA1, trained to rebuild pixels, as a reference.")
    w("- **Test-to-study (T→S)**: each test drawing's state picks the nearest studied state, the way a cue "
      "retrieves a memory. **Study-to-test (S→T)**: each studied state picks the nearest test state, "
      "AHA's direction. Values are means over seeds ± one standard deviation, in percent.")
    w("- **Right cells in cue**: the share of the right stored pattern's k cells that the cue has on. "
      "**Exact recall**: the final CA3 state equals the right stored pattern.")
    w("")
    w("## Predictions")
    w("")
    w("| Prediction, written before the runs | Outcome |")
    w("|---|---|")
    w("| 1. The perforant cue is weaker than PR's: without settling, accuracy on both tasks falls below "
      "the PR model's. | **Partly held.** On Lake's runs, CA3 stage: {:.1f}% and {:.1f}% (clipped binary, "
      "covariance) against {:.1f}% for PR without settling, S→T; {:.1f}% and {:.1f}% against {:.1f}%, "
      "T→S. Under noise 0.3 on the instance task: {:.1f}% and {:.1f}% against {:.1f}%, T→S. It failed for "
      "clean and lightly occluded drawings: the clipped binary cue matches PR on clean drawings ({:.1f}% "
      "against {:.1f}%, T→S) and on occlusion 0.5 matched S→T ({:.1f}% against {:.1f}%). |".format(
          f["wn_s"], f["cn_s"], f["prn_s"], f["wn_t"], f["cn_t"], f["prn_t"], f["i_wnn"], f["i_cnn"],
          f["i_prn"], f["i_wn0"], f["i_pr0"], f["is_wn5"], f["is_pr5"]))
    w("| 2. With the perforant path, settling helps end to end: on the instance task, scored "
      "test-to-study, settling beats no settling by at least 5 points at some corruption level below "
      "capacity. | **Held at the CA1 stage, the end of the pipeline; failed at the CA3 stage.** CA1: "
      "covariance {} clean and {} at occlusion 0.3; clipped binary {} at occlusion 0.3 and {} at 0.5. "
      "CA3: at most {:+.1f} points. |".format(e(f["c0"]), e(f["c3"]), e(f["w3"]), e(f["w5"]), ca3_best[0]))
    w("| 3. On Lake's runs, the fully local model scores below the PR model. | **Held.** CA1 stage: "
      "{:.1f}% S→T and {:.1f}% T→S for the perforant path with clipped binary synapses and settling, "
      "{:.1f}% and {:.1f}% with the covariance rule, against {:.1f}% and {:.1f}% for PR with covariance "
      "settling. |".format(f["ppc"], f["ppt"], f["ppcc"], f["ppct"], f["prc"], f["prt"]))
    w("| 4. CA1-stage accuracy stays within 3 points of the CA3 stage. | **Held for every arm that "
      "settles and for PR; failed for perforant cues passed on without settling.** Largest gap {:+.1f} "
      "points for the first group and {:+.1f} for the second, at 2% active. At 4.4%, PR without settling "
      "also falls {:.1f} points below CA3 on the instance task. |".format(gap_settle, gap_none, -gap_pr10))
    w("")
    w("## What the numbers show")
    w("")
    w("- **The perforant cue finds the exact studied drawing but rarely a new drawing of it.** On the "
      "instance task the clipped binary cue holds {:.1f}% of the right pattern's cells for clean drawings "
      "(covariance {:.1f}%). On Lake's runs, where the test drawing is by another person, the stored "
      "pattern nearest the cue is the right one for {:.1f}% (clipped binary) and {:.1f}% (covariance) of "
      "drawings, against {:.1f}% and {:.1f}% for the whole vision code matched directly.".format(
          f["cue_w0"], f["cue_c0"], f["look_w"], f["look_c"], f["vc_s"], f["vc_t"]))
    w("- **Settling completes the perforant cue, and CA1 needs the completed pattern.** At occlusion 0.3 "
      "the clipped binary cue holds {:.1f}% of the right cells and is exact for {:.1f}% of drawings; "
      "after settling, {:.1f}% and {:.1f}%. Matched at CA3, the partial cue already points to the right "
      "memory ({:.1f}% T→S), but CA1 reading it returns the right code for only {:.1f}%; from the settled "
      "state, {:.1f}%. With PR's cue, which is already a full pattern near the right memory, settling "
      "adds at most {:+.1f} points at CA1.".format(
          f["cue_w3"], f["ex_w3n"], f["fin_w3"], f["ex_w3"], f["w3_ca3n"], f["w3_ca1n"], f["w3_ca1"],
          f["prc1"]))
    w("- **The gain needs CA3 below capacity.** In the load runs, settling's largest CA1 gain T→S on "
      "clean and occluded drawings is {:+.1f}, {:+.1f}, {:+.1f} and {:+.1f} points at 20, 50, 100 and 200 "
      "drawings. Exact recall of clean drawings after clipped binary settling falls from {:.1f}% to "
      "{:.1f}%, {:.1f}% and {:.1f}%.".format(*up, *f["ex_load"]))
    w("- **Matched study-to-test, settling costs up to {:.1f} points at CA3** for the perforant arms. "
      "Settled states of different test drawings coincide, and a studied drawing searching among them "
      "meets ties, as in E1b.".format(-stt_cost))
    w("- **Noise defeats the perforant cue sooner than PR.** At noise 0.3 on the instance task the "
      "clipped binary cue holds {:.1f}% of the right cells, PR's top cells {:.1f}%.".format(
          f["cue_wn"], f["cue_prn"]))
    w("- **More active cells do not rescue new drawings.** At 4.4% the perforant arms reach {:.1f}% "
      "(covariance) and {:.1f}% (clipped binary) on Lake's runs at CA3, T→S, against {:.1f}% and {:.1f}% "
      "at 2%; PR with covariance settling reaches {:.1f}%. Settling's CA1 gain on the instance task "
      "holds: {:+.1f} points ({}, {}).".format(
          f["l10c"], f["l10w"], f["l5c"], f["l5w"], f["l10p"], f["i10"][0], f["i10"][1][0],
          f["i10"][1][1]))
    w("- **Sparse wiring explains part of the gap on new drawings.** On the background validation runs, "
      "connecting every CA3 cell to all 20,449 EC units (a diagnostic added after the runs) lifts the "
      "best perforant arm from {:.1f}% to {:.1f}% at CA3, T→S; PR reaches {:.1f}%.".format(
          f["sb"], f["s1"], f["sbp"]))
    w("")
    w("## Lake's runs, 2% active ({})".format(seeds_note(load(L5))))
    w("")
    w(stage_table(load(L5)))
    w("")
    w("Cue and final state against the right stored pattern:")
    w("")
    w(cue_table(load(L5)))
    w("")
    w("## Instance task, 2% active ({})".format(seeds_note(load(I5))))
    w("")
    for stage, title in (("ca3", "CA3"), ("ca1", "CA1")):
        for d in (tts, stt):
            w("### {} stage, {}".format(title, d))
            w("")
            w(level_table(load(I5), stage, d))
            w("")
    w("### Settling minus no settling")
    w("")
    w("Mean over seeds in points, [lowest, highest] seed, and seeds where settling scored higher.")
    w("")
    for stage, title in (("ca1", "CA1"), ("ca3", "CA3")):
        for d in (tts, stt):
            w("{} stage, {}:".format(title, d))
            w("")
            w(effect_table(load(I5), stage, d))
            w("")
    w("### Cue quality")
    w("")
    for i in (0, o3, o5, n3):
        w("{}:".format(level_label(load(I5)["levels"][i]).capitalize()))
        w("")
        w(cue_table(load(I5), i))
        w("")
    w("## Load: many drawings of different characters, 2% active (5 seeds)")
    w("")
    w("E1c's end-to-end runs: N drawings of different evaluation characters studied at once and recalled "
      "from corrupted copies of the same drawings.")
    w("")
    arms = ("pr_none", "pr_cov", "pp_cov_none", "pp_cov", "pp_wil_none", "pp_wil")
    for kind in ("occlusion", "noise"):
        w("### {}, CA1 stage, test-to-study".format(kind.capitalize()))
        w("")
        w(load_table(loads, "ca1", tts, arms, kind))
        w("")
        w("### {}, settling minus no settling, test-to-study".format(kind.capitalize()))
        w("")
        w("CA1 stage:")
        w("")
        w(load_effect_table(loads, "ca1", tts, kind))
        w("")
        w("CA3 stage:")
        w("")
        w(load_effect_table(loads, "ca3", tts, kind))
        w("")
        w("### {}, exact recall".format(kind.capitalize()))
        w("")
        w(load_metric_table(loads, "exact", arms, kind))
        w("")
    w("CA3-stage accuracy and the share of right cells in each cue at every load are in the result files.")
    w("")
    w("## 4.4% active, the check ({})".format(seeds_note(load(L10))))
    w("")
    w("Lake's runs:")
    w("")
    w(stage_table(load(L10)))
    w("")
    w("Instance task, CA1 stage, test-to-study:")
    w("")
    w(level_table(load(I10), "ca1", tts))
    w("")
    w("Settling minus no settling, CA1 stage, test-to-study:")
    w("")
    w(effect_table(load(I10), "ca1", tts))
    w("")
    w("## CA1 minus CA3")
    w("")
    w("Largest gap per arm over levels and both directions, in points.")
    w("")
    w(gap_table({"Lake's runs, 2%": load(L5), "Instance, 2%": load(I5), "Lake's runs, 4.4%": load(L10),
                 "Instance, 4.4%": load(I10)}))
    w("")
    w("## Perforant settings chosen on background alphabets")
    w("")
    grid, scores = grid_scores()
    chosen = {}
    for rule in ("willshaw", "covariance"):
        names = [n for n in grid if grid[n][0] == rule]
        chosen[rule] = max(names, key=lambda n: (round(scores[n][0], 10),
                                                 [-x for x in simplicity(n, grid[n])]))
    w("Score: mean CA3-stage accuracy over the clean validation runs and the instance runs clean and at "
      "occlusion and noise 0.3, 0.5 and 0.7, both directions, settling and no settling weighted equally, "
      "5 seeds. Chosen: `{}` for clipped binary synapses ({:.4f}) and `{}` for the covariance rule "
      "({:.4f}). Setting names give the rule, then for clipped binary whether an EC unit counts as active "
      "above zero (pos) or above its background mean (mean), then raw or normalised drive, then plain "
      "k-WTA or the E%-max share. For clipped binary synapses, E%-max 0.3 beat plain k-WTA by {:.4f}, a "
      "tie in practice. The full grid is in `results/e3_selection.md`.".format(
          chosen["willshaw"], scores[chosen["willshaw"]][0], chosen["covariance"],
          scores[chosen["covariance"]][0],
          scores[chosen["willshaw"]][0] - scores["wil_pos_norm_kwta"][0]))
    w("")
    w("## Run time")
    w("")
    w("All E3 runs together took {:.0f} minutes of process time, at most two at once, on Apple's MPS "
      "backend with the perforant path and BTSP on the CPU.".format(60 * hrs))
    w("")
    (RESULTS / "e3.md").write_text("\n".join(lines))
    print("Wrote results/e3.md")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--select", action="store_true")
    p.add_argument("--dump", action="store_true", help="print every table whose files exist")
    p.add_argument("--k", type=int, default=5, help="active cells of the files --dump reads")
    args = p.parse_args(argv)
    if args.select:
        select()
        return
    if args.dump:
        print(dump(args.k))
        return
    build()


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
