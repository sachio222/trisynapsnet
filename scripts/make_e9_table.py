"""Builds E9's calibration, checks, scores and tables from results/e9_*.json.

    python scripts/make_e9_table.py --calibrate   thresholds and the
                                                  reproduction checks, from
                                                  the background run only
    python scripts/make_e9_table.py --check       exits 1 unless the checks
                                                  in the calibration passed
    python scripts/make_e9_table.py               scores and tables

E9 (docs/e9_protocol.md) recalls each list under four conditions: E8c's
model (e8c), entorhinal input kept on during attractor dynamics (ec), and
EC input plus DG input through the mossy fibres at 1.9 and 17.1 units
(dg1.9, dg17.1). Each condition has its own result file,
results/e9_<split>_n128_d1_<condition>.json.

--calibrate reads the background files and writes results/e9_calibration.json:
for each condition, readout (R1, CA1 comparator; R2, final-state support;
R3, starting-state familiarity; R3s, the starting state's self-support)
and arm, the two thresholds that give young adults' p(old | repeat) 0.812
and p(new | foil) 0.820 on background lists, and for the intact model and
the thinned perforant paths the thresholds for adults 60 to 74 (0.822,
0.734; Stark and colleagues 2013, Table 2). It runs the protocol's item-19
checks: (a) every readout and arm under E8c's model equals E8c's background
signals (results/e8c_background_n128_d1.json); (b) E8c's model's young-adult
thresholds equal E8c's (results/e8c_calibration.json); (c) R3 and R3s are
the same in every condition. "passed" is true only if every difference is 0;
otherwise --calibrate and --check exit 1, and scripts/run_e9.sh stops before
the evaluation run.

The default run scores the evaluation files (seeds 200 to 209) and writes
results/e9_scores.json and the tables in results/e9.md below the line
"## Tables" (text above it is kept). Each prediction is scored as
docs/e9_protocol.md fixes it. Values are means over seeds; the numbers
after ± are one standard deviation over seeds. Scoring, response rates and
tables reuse scripts/make_e8b_table.py and scripts/make_e8c_table.py.
"""

import argparse
import importlib.util
import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import torch  # noqa: E402


def _load(name):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / "{}.py".format(name))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


E8C = _load("make_e8c_table")
E8B = E8C.E8B
RESULTS = REPO / "results"
CALIBRATION = RESULTS / "e9_calibration.json"
SCORES = RESULTS / "e9_scores.json"
TABLES = RESULTS / "e9.md"
E8C_BACKGROUND = RESULTS / "e8c_background_n128_d1.json"
E8C_CALIBRATION = RESULTS / "e8c_calibration.json"
CONDITIONS = ("e8c", "ec", "dg1.9", "dg17.1")
CONDITION_NAMES = {"e8c": "E8c's model (recurrent input only)",
                   "ec": "EC-on control (recurrent + EC)",
                   "dg1.9": "DG at recall, 1.9 units (recurrent + EC + mossy)",
                   "dg17.1": "DG at recall, 17.1 units (recurrent + EC + mossy)"}
MAIN, CONTROL, LOW = "dg17.1", "ec", "dg1.9"
READOUTS = E8C.READOUTS
READOUT_NAMES = {"r1": "R1 (CA1 comparator)", "r2": "R2 (final-state support)",
                 "r3": "R3 (starting-state familiarity)",
                 "r3s": "R3s (self-support of the starting state)"}
YOUNG_TARGETS, OLDER_TARGETS = E8C.YOUNG_TARGETS, E8C.OLDER_TARGETS
YOUNG_OLD_LURE, OLDER_OLD_LURE = 0.403, 0.546
OLDER_ARMS, PP_ARMS = E8C.OLDER_ARMS, E8C.PP_ARMS
ARMS = E8B.LESION_ARMS
SETS = E8B.SETS
mean = E8B.mean
# E8c's evaluation values (results/e8c.md, intact model, closer lures unless
# "drawer", fixed thresholds) that prediction 5 compares with.
E8C_EVALUATION = {("r3", "close", "rec"): 0.760, ("r3", "close", "ldi"): 0.415,
                  ("r3", "close", "rates lure old"): 0.0, ("r1", "drawer", "rec"): 0.728,
                  ("r2", "close", "rates lure old"): 0.384}
TYPE_NAMES = {0: "repeats", 1: "other-drawer lures", 2: "foils", 3: "closer lures"}


def path(split, condition):
    return RESULTS / "e9_{}_n128_d1_{}.json".format(split, condition)


def load_split(split, conditions=CONDITIONS):
    records = {}
    for c in conditions:
        rec = json.loads(path(split, c).read_text())
        if not rec["complete"]:
            raise SystemExit("{} is incomplete".format(path(split, c).name))
        records[c] = rec
    return records


# ---------------------------------------------------------------- checks

def max_difference(a, b, readouts=READOUTS):
    """Largest absolute difference between two records' signals, per readout,
    over every seed and arm both have; an "error" entry if they do not match
    in seeds, arms or lengths."""
    out = {}
    for r in readouts:
        worst = 0.0
        for seed, items in a["per_seed"].items():
            ref = b["per_seed"].get(seed)
            if ref is None:
                return {"error": "seed {} missing".format(seed)}
            for arm, values in items["signal"][r].items():
                if arm not in ref["signal"][r]:
                    return {"error": "{} {} missing".format(r, arm)}
                x, y = torch.tensor(values), torch.tensor(ref["signal"][r][arm])
                if x.shape != y.shape:
                    return {"error": "{} {} lengths differ".format(r, arm)}
                worst = max(worst, (x - y).abs().max().item())
        out[r] = worst
    return out


def threshold_difference(mine, ref):
    """Largest absolute difference between two calibrations' young-adult
    thresholds and tie shares, over every readout and arm in ref."""
    worst = 0.0
    for r, by_arm in ref["thresholds"].items():
        for arm, t in by_arm.items():
            if arm not in mine.get(r, {}):
                return float("inf")
            worst = max(worst, *(abs(mine[r][arm][k] - t[k]) for k in ("old", "new", "q_old",
                                                                       "q_new")))
    return worst


def starting_state_difference(records):
    """Largest absolute difference in R3 and R3s between any condition and
    E8c's model, per readout."""
    out = {}
    base = records["e8c"]
    for c, rec in records.items():
        if c == "e8c":
            continue
        d = max_difference(rec, base, ("r3", "r3s"))
        if "error" in d:
            return d
        for r, v in d.items():
            out[r] = max(out.get(r, 0.0), v)
    return out


def checks(records, e8c_background, e8c_calibration, cal):
    out = {"e8c_signals": max_difference(records["e8c"], e8c_background)
           if e8c_background is not None else {"error": "E8c's background file is missing"},
           "e8c_thresholds": threshold_difference(cal["conditions"]["e8c"]["thresholds"],
                                                  e8c_calibration)
           if e8c_calibration is not None else float("inf"),
           "starting_state": starting_state_difference(records)}
    ok = all(v == 0 for v in out["e8c_signals"].values() if not isinstance(v, str))
    ok = ok and "error" not in out["e8c_signals"] and "error" not in out["starting_state"]
    ok = ok and out["e8c_thresholds"] == 0
    ok = ok and all(v == 0 for v in out["starting_state"].values())
    out["passed"] = bool(ok)
    return out


# ---------------------------------------------------------------- calibration

def calibrate(records, e8c_background=None, e8c_calibration=None, edges=None):
    cal = {"source": {c: "results/{}".format(path("background", c).name) for c in records},
           "targets": {"young": YOUNG_TARGETS, "older": OLDER_TARGETS}, "bin_edges": edges,
           "conditions": {}}
    for c, rec in records.items():
        thr = {r: {} for r in READOUTS}
        older = {r: {} for r in READOUTS}
        for r in READOUTS:
            for arm in rec["args"]["arms"]:
                if not E8C.has_signal(r, arm):
                    continue
                thr[r][arm] = E8C.thresholds(rec, r, arm, YOUNG_TARGETS)
                if arm in OLDER_ARMS:
                    older[r][arm] = E8C.thresholds(rec, r, arm, OLDER_TARGETS)
        cal["conditions"][c] = {"thresholds": thr, "older": older}
    cal["checks"] = checks(records, e8c_background, e8c_calibration, cal)
    return cal


def condition_cal(cal, c):
    return {"thresholds": cal["conditions"][c]["thresholds"],
            "older": cal["conditions"][c]["older"], "bin_edges": cal["bin_edges"]}


# ---------------------------------------------------------------- scoring

def score_all(records, cal):
    """{condition: (fixed, own, older)}, each {(readout, set): {arm: summary}}."""
    out = {}
    for c, rec in records.items():
        cc = condition_cal(cal, c)
        out[c] = tuple({(r, w): E8C.score_record(rec, cc, r, w, mode) for r in READOUTS
                        for w in SETS} for mode in ("fixed", "own", "older"))
    return out


def nanmean(values):
    vals = [v for v in values if not (isinstance(v, float) and math.isnan(v))]
    return sum(vals) / len(vals) if vals else float("nan")


def per_seed_share(record, arm, field, select):
    """Per seed: the mean of a logged CA3 field over the items `select` picks
    (select(types, level, paired) -> bool mask)."""
    out = []
    for s in sorted(record["per_seed"], key=int):
        items = record["per_seed"][s]
        ca3 = items["ca3"].get(arm)
        if not ca3 or field not in ca3:
            out.append(float("nan"))
            continue
        types = torch.tensor(items["types"])
        level = torch.tensor(items["level"])
        paired = torch.tensor(items["paired"])
        m = select(types, level, paired)
        v = torch.tensor(ca3[field], dtype=torch.float64)[m]
        out.append(v.mean().item() if len(v) else float("nan"))
    return out


def is_type(t):
    return lambda types, level, paired: types == t


def ca3_summary(record, arm="intact"):
    """The logged CA3 quantities, per seed and as means over seeds (protocol
    item 30). Every value reads the stored list or the logs, never a
    readout."""
    rows = {}
    rows["repeats on their own pattern"] = per_seed_share(record, arm, "exact_paired", is_type(0))
    for t in (0, 3, 1, 2):
        rows["{} on any stored pattern".format(TYPE_NAMES[t])] = per_seed_share(
            record, arm, "exact_any", is_type(t))
    for lv in range(1, 6):
        rows["closer lures C{} on their studied pattern".format(lv)] = per_seed_share(
            record, arm, "exact_paired", lambda ty, le, pa, lv=lv: (ty == 3) & (le == lv))
    for t in (0, 3, 2):
        rows["rounds, {}".format(TYPE_NAMES[t])] = per_seed_share(record, arm, "rounds",
                                                                  is_type(t))
    fixed = per_seed_share(record, arm, "fixed", lambda ty, le, pa: ty >= 0)
    rows["items without a fixed point"] = [1 - v for v in fixed]
    for t in (0, 3, 2):
        rows["final state's share in DG's own pattern, {}".format(TYPE_NAMES[t])] = \
            per_seed_share(record, arm, "dg_follow", is_type(t))
    # Repeats on their own pattern by study position (eighths of the list):
    # the frozen DG record inhibits the last drawings studied most.
    load = record["args"]["load"]
    step = max(1, load // 8)
    for b in range(0, load, step):
        rows["repeats on their own pattern, studied {} to {}".format(b + 1, b + step)] = \
            per_seed_share(record, arm, "exact_paired",
                           lambda ty, le, pa, b=b: (ty == 0) & (pa >= b) & (pa < b + step))
    return {k: {"mean": nanmean(v), "values": v} for k, v in rows.items()}


def dg_overlap_summary(record):
    """Logged only: the share of each repeat's and lure's DG response shared
    with its studied drawing's DG pattern, mean over items then seeds."""
    out = {}
    for t in (0, 3, 1):
        vals = []
        for s in sorted(record["per_seed"], key=int):
            items = record["per_seed"][s]
            if "dg_paired_overlap" not in items:
                continue
            types = torch.tensor(items["types"])
            v = torch.tensor(items["dg_paired_overlap"], dtype=torch.float64)[types == t]
            vals.append(v.mean().item() if len(v) else float("nan"))
        out[TYPE_NAMES[t]] = nanmean(vals)
    return out


def sign_test(diffs):
    """(seeds with a positive difference, seeds with a negative one,
    two-sided sign-test p over the non-zero differences)."""
    pos = sum(d > 0 for d in diffs)
    neg = sum(d < 0 for d in diffs)
    n = pos + neg
    if n == 0:
        return pos, neg, 1.0
    k = min(pos, neg)
    p = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return pos, neg, min(1.0, 2 * p)


def seed_values(s, key):
    return s[key]["values"]


def levels(s, key):
    return [mean(s, "{} {}".format(key, b)) for b in range(1, 6)]


def fmt(values):
    return ", ".join("{:.3f}".format(x) for x in values)


def verdict(alternative, null):
    if alternative:
        return "supported"
    if null:
        return "falsified"
    return "weakened"


def h1(records, condition):
    dg = ca3_summary(records[condition])
    ctrl = ca3_summary(records[CONTROL])
    key = "foils on any stored pattern"
    f_dg, f_ctrl = dg[key]["mean"], ctrl[key]["mean"]
    diffs = [a - b for a, b in zip(ctrl[key]["values"], dg[key]["values"])]
    pos, neg, p = sign_test(diffs)
    alt = f_ctrl - f_dg > 0.10
    null = abs(f_dg - f_ctrl) <= 0.10
    rep = dg["repeats on their own pattern"]["mean"]
    text = ("foils ending on a stored pattern {:.3f} against the control's {:.3f} (fall "
            "{:.3f}; {} of {} seeds lower, sign test p = {:.3g}); expected below one half: {}; "
            "repeats on their own pattern {:.3f} (expected at least 0.95: {})").format(
                f_dg, f_ctrl, f_ctrl - f_dg, pos, len(diffs), p,
                "yes" if f_dg < 0.5 else "no", rep, "yes" if rep >= 0.95 else "no")
    return verdict(alt, null), text


def h2(fixed, which="close"):
    lines, alt_any, null_all = [], False, True
    for r in READOUTS:
        s = fixed[(r, which)]["intact"]
        p_old, p_foil = mean(s, "rates lure old"), mean(s, "rates foil old")
        old = levels(s, "old_bins")
        falls = E8B.monotone(old, falling_with_level=True)
        alt = abs(p_old - YOUNG_OLD_LURE) <= 0.15 and falls and p_foil <= 0.10
        alt_any = alt_any or alt
        null_all = null_all and p_old < YOUNG_OLD_LURE - 0.15
        lines.append("{}: p(old | lure) {:.3f}, by level {}{}, p(old | foil) {:.3f}".format(
            r.upper(), p_old, fmt(old), " (falls)" if falls else "", p_foil))
    return verdict(alt_any, null_all), "; ".join(lines)


def h3(cal, condition):
    t = cal["conditions"][condition]["thresholds"]["r2"]["intact"]
    others = []
    for c in ("ec", "e8c"):
        u = cal["conditions"][c]["thresholds"]["r2"]["intact"]
        others.append("{} {:.4f} / {:.4f} ({})".format(c, u["old"], u["new"],
                                                       "room" if u["feasible"] else "crossed"))
    return (verdict(t["feasible"], not t["feasible"]),
            "R2 θ_old {:.4f}, θ_new {:.4f} ({}); {}".format(
                t["old"], t["new"], "room for similar" if t["feasible"] else "thresholds cross",
                "; ".join(others)))


def predictions(records, cal, scores):
    """Each prediction, scored as docs/e9_protocol.md fixes it."""
    out = []
    for c, label in ((MAIN, ""), (LOW, " (1.9 units, reported)")):
        fixed = scores[c][0]
        v, t = h1(records, c)
        out.append(("H1" + label, v, t))
        v, t = h2(fixed, "close")
        out.append(("H2" + label, v, t))
        v, t = h2(fixed, "drawer")
        out.append(("H2, other-drawer lures" + label, v, t))
        v, t = h3(cal, c)
        out.append(("H3" + label, v, t))
    diff = starting_state_difference(records)
    ok = "error" not in diff and all(x == 0 for x in diff.values())
    out.append(("4", "held" if ok else "failed",
                "largest difference from E8c's model: " + ", ".join(
                    "{} {}".format(k, v) for k, v in diff.items())))
    lines, held = [], True
    e8c_fixed = scores["e8c"][0]
    for (r, which, key), ref in E8C_EVALUATION.items():
        v = mean(e8c_fixed[(r, which)]["intact"], key)
        held = held and abs(v - ref) <= 0.05
        lines.append("{} {} {}: {:.3f} against E8c's {:.3f}".format(r.upper(), which, key, v, ref))
    out.append(("5", "held" if held else "failed", "; ".join(lines)))
    c = scores[MAIN][0]
    parts, held = [], True
    for r in ("r2", "r3"):
        o_int, o_dg = (mean(c[(r, "close")][a], "rates lure old") for a in ("intact", "no_dg"))
        diffs = [a - b for a, b in zip(seed_values(c[(r, "close")]["no_dg"], "rates lure old"),
                                       seed_values(c[(r, "close")]["intact"], "rates lure old"))]
        pos, neg, p = sign_test(diffs)
        held = held and o_dg > o_int
        parts.append("{}: without DG {:.3f} against intact {:.3f} ({} of {} seeds higher, p = "
                     "{:.3g})".format(r.upper(), o_dg, o_int, pos, len(diffs), p))
    out.append(("6", "held" if held else "failed", "; ".join(parts)))
    held, parts = True, []
    for cond in CONDITIONS:
        f = scores[cond][0]
        for r in ("r2", "r3", "r3s"):
            s = f[(r, "close")]["no_recurrent"]
            new = [mean(s, "rates {} new".format(t)) for t in ("repeat", "lure", "foil")]
            held = held and all(x == 1 for x in new)
        parts.append(cond)
    out.append(("7", "held" if held else "failed",
                "every item new under R2, R3 and R3s without recurrent synapses in " + ", ".join(
                    parts) if held else "some item not new without recurrent synapses"))
    rec = {r: [mean(c[(r, "close")][a], "rec") for a in ("intact",) + PP_ARMS]
           for r in ("r1", "r2", "r3")}
    r3_falls = all(rec["r3"][i + 1] <= rec["r3"][i] for i in range(3))
    final_kept = all(abs(rec[r][i] - rec[r][0]) < 0.10 for r in ("r1", "r2") for i in (1, 2, 3))
    out.append(("8", "held" if (r3_falls and final_kept) else "failed",
                "REC intact, 75%, 50%, 25% kept: R3 {}; R1 {}; R2 {}".format(
                    fmt(rec["r3"]), fmt(rec["r1"]), fmt(rec["r2"]))))
    older = scores[MAIN][2]
    hits, parts = [], []
    for r in READOUTS:
        for arm in PP_ARMS:
            s = older[(r, "close")].get(arm)
            if s is None:
                continue
            o, f = mean(s, "rates lure old"), mean(s, "rates foil old")
            parts.append("{} {}: {:.3f} lures, {:.3f} foils old".format(r.upper(), arm, o, f))
            if abs(o - OLDER_OLD_LURE) <= 0.15 and f <= 0.10:
                hits.append("{} {}".format(r.upper(), arm))
    out.append(("9", "held" if not hits else "failed",
                ("older adults' criteria, against 0.546: " + "; ".join(parts))
                + ("" if not hits else "; the older-adult error under " + ", ".join(hits))))
    return out


# ---------------------------------------------------------------- tables

def summary_cell(s, digits=3):
    return "n/a" if s is None or math.isnan(s) else "{:.{}f}".format(s, digits)


def tables(cal, scores, ca3, dg_overlap, preds):
    lines = ["## Tables", "",
             "Built by `scripts/make_e9_table.py` from `results/e9_*.json`, with the thresholds in "
             "`results/e9_calibration.json`. Evaluation lists from every evaluation drawing, seeds "
             "200 to 209. Means over seeds ± one standard deviation; rates in percent.", ""]
    ch = cal["checks"]
    lines += ["Reproduction checks on background lists (protocol item 19): E8c's model against "
              "E8c's signals, largest absolute difference " + json.dumps(ch["e8c_signals"])
              + "; against E8c's thresholds " + str(ch["e8c_thresholds"]) + "; R3 and R3s across "
              "conditions " + json.dumps(ch["starting_state"]) + "; passed: "
              + str(ch["passed"]) + ".", ""]
    lines += ["### Predictions, scored as the protocol fixes", "",
              "| Prediction | Outcome | Numbers |", "|---|---|---|"]
    lines += ["| {} | {} | {} |".format(k, v, t.replace("|", "\\|")) for k, v, t in preds]
    lines += ["", "### Calibration on background alphabets, 128 drawings", "",
              "| Condition | Readout | Arm | Criteria | θ_old | θ_new | Room for similar |",
              "|---|---|---|---|---|---|---|"]
    for c in CONDITIONS:
        for r in READOUTS:
            for group, label in (("thresholds", "young adults"), ("older", "adults 60 to 74")):
                for arm, t in cal["conditions"][c][group][r].items():
                    lines.append("| {} | {} | {} | {} | {:.4f} (tie share {:.3f}) | {:.4f} (tie "
                                 "share {:.3f}) | {} |".format(
                                     c, READOUT_NAMES[r], E8B.ARM_NAMES[arm], label, t["old"],
                                     t["q_old"], t["new"], t["q_new"],
                                     "yes" if t["feasible"] else "no"))
    lines += ["", "### Where attractor dynamics end, intact model (logged, never used to decide)",
              "", "| Quantity | " + " | ".join(CONDITIONS) + " |",
              "|---|" + "---|" * len(CONDITIONS)]
    keys = list(ca3[MAIN].keys())
    for k in keys:
        lines.append("| {} | ".format(k) + " | ".join(
            summary_cell(ca3[c].get(k, {}).get("mean", float("nan"))) for c in CONDITIONS) + " |")
    lines += ["", "DG response shared with the studied drawing's DG pattern (logged): " + ", ".join(
        "{} {:.3f}".format(k, v) for k, v in dg_overlap.items()) + ".", ""]
    humans = [("Young adults, 20 to 39", E8B.YOUNG), ("Adults 60 to 74", E8B.OLDER)]
    for c in CONDITIONS:
        fixed, own, older = scores[c]
        lines += ["", "## {}".format(CONDITION_NAMES[c])]
        for r in READOUTS:
            for which in SETS:
                s = fixed[(r, which)]
                lines += ["", "### {}, {}, {}, fixed thresholds".format(
                    c, READOUT_NAMES[r], E8B.SET_NAMES[which]), "",
                    E8B.score_table(s, ARMS, which), "", "Response rates:", "",
                    E8B.response_table(s, ARMS, humans), "", "p(old | lure) by level:", "",
                    E8B.rate_by_level_table(s, ARMS, which, "old_bins"), "",
                    "p(similar | lure) by level:", "",
                    E8B.rate_by_level_table(s, ARMS, which, "sim_bins")]
        for r in READOUTS:
            lines += ["", "### {}, each arm with its own thresholds, {}, closer lures "
                      "(secondary)".format(c, READOUT_NAMES[r]), "",
                      E8B.score_table(own[(r, "close")], ARMS, "close", human=False)]
        for r in READOUTS:
            s = older[(r, "close")]
            lines += ["", "### {}, older adults' criteria, {}, closer lures".format(
                c, READOUT_NAMES[r]), "", E8B.response_table(s, OLDER_ARMS, humans), "",
                "p(old | lure) by level:", "",
                E8B.rate_by_level_table(s, OLDER_ARMS, "close", "old_bins")]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- main

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--calibrate", action="store_true")
    p.add_argument("--check", action="store_true")
    args = p.parse_args(argv)
    if args.check:
        cal = json.loads(CALIBRATION.read_text())
        print(json.dumps(cal["checks"]))
        if not cal["checks"]["passed"]:
            raise SystemExit("item-19 checks failed; the evaluation run must not start")
        return
    if args.calibrate:
        records = load_split("background")
        ref = json.loads(E8C_BACKGROUND.read_text()) if E8C_BACKGROUND.is_file() else None
        ref_cal = json.loads(E8C_CALIBRATION.read_text()) if E8C_CALIBRATION.is_file() else None
        edges = json.loads(E8B.E8_CALIBRATION.read_text())["bin_edges"]
        cal = calibrate(records, ref, ref_cal, edges)
        CALIBRATION.write_text(json.dumps(cal, indent=1))
        for c in CONDITIONS:
            print(c, json.dumps({r: {a: (round(t["old"], 4), round(t["new"], 4), t["feasible"])
                                     for a, t in v.items() if a == "intact"}
                                 for r, v in cal["conditions"][c]["thresholds"].items()}))
        print("checks:", json.dumps(cal["checks"]))
        if not cal["checks"]["passed"]:
            raise SystemExit("item-19 checks failed; see results/e9_calibration.json")
        return
    cal = json.loads(CALIBRATION.read_text())
    if not cal["checks"]["passed"]:
        raise SystemExit("item-19 checks failed; nothing is scored")
    records = load_split("evaluation")
    scores = score_all(records, cal)
    ca3 = {c: ca3_summary(records[c]) for c in CONDITIONS if c != "e8c"}
    ca3["e8c"] = ca3_summary(records["e8c"])
    dg_overlap = dg_overlap_summary(records[MAIN])
    preds = predictions(records, cal, scores)
    SCORES.write_text(json.dumps({
        "fixed": {c: {"{} {}".format(*k): v for k, v in scores[c][0].items()} for c in scores},
        "own": {c: {"{} {}".format(*k): v for k, v in scores[c][1].items()} for c in scores},
        "older": {c: {"{} {}".format(*k): v for k, v in scores[c][2].items()} for c in scores},
        "ca3": ca3, "dg_overlap": dg_overlap,
        "predictions": [{"prediction": k, "outcome": v, "numbers": t} for k, v, t in preds]}))
    head = TABLES.read_text().split("## Tables")[0] if TABLES.is_file() else "# E9 results\n\n"
    TABLES.write_text(head + tables(cal, scores, ca3, dg_overlap, preds))
    print("Wrote {}, {}".format(TABLES.relative_to(REPO), SCORES.relative_to(REPO)))


if __name__ == "__main__":
    main()
