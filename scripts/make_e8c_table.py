"""Builds E8c's calibration, scores and tables from results/e8c_*.json.

    python scripts/make_e8c_table.py --calibrate   thresholds from the
                                                   background run only
    python scripts/make_e8c_table.py               scores and tables

--calibrate reads results/e8c_background_n128_d1.json and writes
results/e8c_calibration.json: for each readout (R1, CA1 comparator; R2,
self-support of CA3's settled state; R3, recurrent support of CA3's
starting state; R3s, self-support of the starting state) and each arm, the
two thresholds that give young adults' p(old | repeat) 0.812 and
p(new | foil) 0.820 on the background lists at 128 drawings; and, for the
intact model and the thinned perforant paths, the two thresholds that give
adults 60 to 74 years old their p(old | repeat) 0.822 and p(new | foil)
0.734 (Stark and colleagues 2013, Table 2). It also checks that R1 and R2
on the background lists equal E8b's (results/e8b_background_n128_d1.json),
since the model and the lists are E8b's.

The default run scores results/e8c_evaluation_n128_d1.json (lists built
only from evaluation drawings E8b's 128-drawing evaluation lists never
used, seeds 100 to 109) and writes results/e8c_scores.json and the tables
in results/e8c.md below the line "## Tables" (text above it is kept). Each
prediction is scored as docs/e8c_protocol.md fixes it.

Values are means over seeds; the numbers after ± are one standard
deviation over seeds. Scoring, response rates and tables reuse
scripts/make_e8b_table.py.
"""

import argparse
import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import torch  # noqa: E402

from trisynapsnet.eval import behaviour as bh  # noqa: E402


def _load_e8b():
    spec = importlib.util.spec_from_file_location("make_e8b_table",
                                                  REPO / "scripts" / "make_e8b_table.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


E8B = _load_e8b()
RESULTS = REPO / "results"
CALIBRATION = RESULTS / "e8c_calibration.json"
SCORES = RESULTS / "e8c_scores.json"
TABLES = RESULTS / "e8c.md"
E8B_BACKGROUND = RESULTS / "e8b_background_n128_d1.json"
BACKGROUND = RESULTS / "e8c_background_n128_d1.json"
EVALUATION = RESULTS / "e8c_evaluation_n128_d1.json"

YOUNG_TARGETS = (0.812, 0.820)   # Stark and colleagues 2013, Table 2, ages 20 to 39
OLDER_TARGETS = (0.822, 0.734)   # same table, ages 60 to 74
OLDER_OLD_LURE = 0.546
READOUTS = ("r1", "r2", "r3", "r3s")
READOUT_NAMES = {"r1": "R1 (CA1 comparator)", "r2": "R2 (self-support of the settled state)",
                 "r3": "R3 (recurrent support of the starting state)",
                 "r3s": "R3s (self-support of the starting state)"}
# Readouts that read CA3's recurrent synapses: no signal without them.
CA3_READOUTS = ("r2", "r3", "r3s")
NO_SIGNAL = ("no_recurrent", "no_ca3")
OLDER_ARMS = ("intact", "pp_keep0.75", "pp_keep0.5", "pp_keep0.25")
PP_ARMS = ("pp_keep0.75", "pp_keep0.5", "pp_keep0.25")
ARMS = E8B.LESION_ARMS
SETS = E8B.SETS
mean = E8B.mean


def has_signal(readout, arm):
    return not (readout in CA3_READOUTS and arm in NO_SIGNAL)


def thresholds(record, readout, arm, targets):
    types = torch.tensor(E8B.pooled(record, "types"))
    s = E8B.floats(E8B.pooled(record, None, readout, arm))
    return bh.calibrate(s[types == 0], s[types == 2], *targets)


def reproduction_check(record, reference):
    """Largest absolute difference between E8c's and E8b's R1 and R2 signals
    on the same background lists, per readout; None without E8b's file."""
    if reference is None:
        return None
    out = {}
    for r in ("r1", "r2"):
        worst = 0.0
        for seed, items in record["per_seed"].items():
            ref = reference["per_seed"].get(seed)
            if ref is None:
                return {"error": "seed {} missing from E8b's file".format(seed)}
            for arm, values in items["signal"][r].items():
                a, b = torch.tensor(values), torch.tensor(ref["signal"][r][arm])
                if a.shape != b.shape:
                    return {"error": "{} {} lengths differ".format(r, arm)}
                worst = max(worst, (a - b).abs().max().item())
        out[r] = worst
    return out


def calibrate(record, reference=None, edges=None):
    out = {"source": "results/{}".format(BACKGROUND.name), "seeds": record["seeds_done"],
           "targets": {"young": YOUNG_TARGETS, "older": OLDER_TARGETS},
           "thresholds": {r: {} for r in READOUTS}, "older": {r: {} for r in READOUTS},
           "bin_edges": edges, "reproduces_e8b": reproduction_check(record, reference)}
    for r in READOUTS:
        for arm in record["args"]["arms"]:
            if not has_signal(r, arm):
                continue
            out["thresholds"][r][arm] = thresholds(record, r, arm, YOUNG_TARGETS)
            if arm in OLDER_ARMS:
                out["older"][r][arm] = thresholds(record, r, arm, OLDER_TARGETS)
    return out


def thresholds_for(cal, readout, arm, mode):
    """fixed: the intact model's young-adult thresholds (the baseline keeps
    its own); own: the arm's own young-adult thresholds; older: the arm's
    own older-adult thresholds."""
    if mode == "older":
        return cal["older"][readout][arm]
    thr = cal["thresholds"][readout]
    if arm == "vc_baseline" or (mode == "own" and arm in thr):
        return thr[arm]
    return thr["intact"]


def score_record(record, cal, readout, which, mode="fixed"):
    out = {}
    for arm in record["args"]["arms"]:
        if mode != "fixed" and not has_signal(readout, arm):
            continue
        if mode == "older" and arm not in OLDER_ARMS:
            continue
        thr = thresholds_for(cal, readout, arm, mode)
        per_seed = [E8B.flatten(E8B.seed_scores(record["per_seed"][s], readout, arm, thr,
                                                cal["bin_edges"], which))
                    for s in sorted(record["per_seed"], key=int)]
        out[arm] = {k: E8B.summarise([p[k] for p in per_seed]) for k in per_seed[0]}
    if mode == "fixed":
        flat = E8B.flatten(E8B.no_hippocampus())
        out["no_hippocampus"] = {k: E8B.summarise([v] * len(record["per_seed"]))
                                 for k, v in flat.items()}
    return out


def levels(s, key):
    return [mean(s, "{} {}".format(key, b)) for b in range(1, 6)]


def fmt(values):
    return ", ".join("{:.3f}".format(x) for x in values)


def predictions(cal, fixed, older, e8b_scores=None):
    """Each prediction, scored as docs/e8c_protocol.md fixes it: means over
    seeds on the held-out evaluation lists at 128 drawings, closer lures,
    R3, intact model, fixed thresholds, unless a line says otherwise."""
    out = []
    thr = cal["thresholds"]["r3"]["intact"]
    out.append(("1", bool(thr["feasible"]),
                "R3 thresholds on background lists: θ_old {:.4f}, θ_new {:.4f} ({})".format(
                    thr["old"], thr["new"], "room for similar" if thr["feasible"]
                    else "θ_new above θ_old, no room for similar")))
    for which in ("close", "drawer"):
        s = fixed[("r3", which)]["intact"]
        old, ldi = levels(s, "old_bins"), levels(s, "ldi_bins")
        a = E8B.monotone(old, falling_with_level=True)
        b = E8B.monotone(ldi, falling_with_level=False)
        label = "closer lures, scored" if which == "close" else "other-drawer lures, reported"
        out.append(("2a ({})".format(label), a,
                    "p(old | lure) by level, most to least similar: {} ({})".format(
                        fmt(old), "falls" if a else "does not fall")))
        out.append(("2b ({})".format(label), not b,
                    "LDI by level, most to least similar: {} ({})".format(
                        fmt(ldi), "rises toward less similar lures, the human direction" if b
                        else "does not rise toward less similar lures")))
    s = fixed[("r3", "close")]["intact"]
    p_old = mean(s, "rates lure old")
    out.append(("3", p_old < E8B.YOUNG_OLD_LURE - 0.15,
                "p(old | lure) {:.3f} against young adults' 0.403".format(p_old)))
    p_new = mean(s, "rates lure new")
    out.append(("3b", p_new > 0.30,
                "p(new | lure) {:.3f} against young adults' 0.083".format(p_new)))
    rec = mean(fixed[("r3", "drawer")]["intact"], "rec")
    out.append(("4", abs(rec - E8B.YOUNG_REC) <= 0.10,
                "REC {:.3f} against young adults' 0.786".format(rec)))
    c = fixed[("r3", "close")]
    o_int, l_int, r_int = (mean(c["intact"], k) for k in ("rates lure old", "ldi", "rec"))
    out.append(("5a", mean(c["no_recurrent"], "rates lure old") == 0
                and mean(c["no_recurrent"], "rec") == 0,
                "without recurrent connections: p(old | lure) {:.3f}, REC {:.3f} (no R3 signal by "
                "construction)".format(mean(c["no_recurrent"], "rates lure old"),
                                       mean(c["no_recurrent"], "rec"))))
    o_dg, l_dg = mean(c["no_dg"], "rates lure old"), mean(c["no_dg"], "ldi")
    out.append(("5b", o_dg > o_int and l_dg < l_int,
                "without DG: p(old | lure) {:.3f} against intact {:.3f}; LDI {:.3f} against "
                "{:.3f}".format(o_dg, o_int, l_dg, l_int)))
    prev_o, prev_r = o_int, r_int
    for arm in PP_ARMS:
        o, r = mean(c[arm], "rates lure old"), mean(c[arm], "rec")
        out.append(("5c ({}% kept)".format(int(float(arm[len("pp_keep"):]) * 100)),
                    o <= prev_o and r <= prev_r,
                    "p(old | lure) {:.3f}, REC {:.3f}; next stronger path {:.3f}, {:.3f}".format(
                        o, r, prev_o, prev_r)))
        prev_o, prev_r = o, r
    if older:
        oc = older[("r3", "close")]
        base = mean(oc["intact"], "rates lure old")
        for arm in PP_ARMS:
            o = mean(oc[arm], "rates lure old")
            out.append(("6 ({}% kept)".format(int(float(arm[len("pp_keep"):]) * 100)), o > base,
                        "older adults' criteria: p(old | lure) {:.3f} against intact {:.3f} with "
                        "the same criteria; adults 60 to 74: 0.546; by level {}".format(
                            o, base, fmt(levels(oc[arm], "old_bins")))))
    if e8b_scores:
        lines, held = [], True
        for (r, which, key), ref in e8b_scores.items():
            v = mean(fixed[(r, which)]["intact"], key)
            ok = abs(v - ref) <= 0.05
            held = held and ok
            lines.append("{} {} {}: {:.3f} against E8b's {:.3f}".format(r, which, key, v, ref))
        out.append(("7", held, "; ".join(lines)))
    return out


# E8b's evaluation values (results/e8b.md, intact model, 128 drawings, fixed
# thresholds) that prediction 7 compares with: the same model and readouts
# on lists from the held-out pool should land within 0.05 of them.
E8B_EVALUATION = {("r1", "drawer", "rec"): 0.724, ("r1", "close", "ldi"): 0.006,
                  ("r1", "close", "rates lure old"): 0.024,
                  ("r2", "close", "rates lure old"): 0.396, ("r2", "drawer", "rec"): 0.432}


def tables(cal, fixed, own, older, preds):
    lines = ["## Tables", "",
             "Built by `scripts/make_e8c_table.py` from `results/e8c_*.json`, with the thresholds "
             "in `results/e8c_calibration.json`. Evaluation lists use only evaluation drawings "
             "that E8b's 128-drawing evaluation lists never used, seeds 100 to 109. Means over "
             "seeds ± one standard deviation; rates in percent.", ""]
    rep = cal.get("reproduces_e8b")
    if rep:
        lines += ["R1 and R2 on the background lists against E8b's: largest absolute difference "
                  + ", ".join("{} {}".format(k, v) for k, v in rep.items()) + ".", ""]
    lines += ["### Calibration on background alphabets, 128 drawings", "",
              "| Readout | Arm | Criteria | θ_old | θ_new | Room for similar |",
              "|---|---|---|---|---|---|"]
    for r in READOUTS:
        for group, label in (("thresholds", "young adults"), ("older", "adults 60 to 74")):
            for arm, t in cal[group][r].items():
                lines.append("| {} | {} | {} | {:.4f} (tie share {:.3f}) | {:.4f} (tie share "
                             "{:.3f}) | {} |".format(READOUT_NAMES[r], E8B.ARM_NAMES[arm], label,
                                                     t["old"], t["q_old"], t["new"], t["q_new"],
                                                     "yes" if t["feasible"] else "no"))
    lines += ["", "### Predictions, scored as the protocol fixes", "",
              "| Prediction | Held | Numbers |", "|---|---|---|"]
    lines += ["| {} | {} | {} |".format(k, "yes" if h else "no", t.replace("|", "\\|"))
              for k, h, t in preds]
    humans = [("Young adults, 20 to 39", E8B.YOUNG), ("Adults 60 to 74", E8B.OLDER)]
    for r in READOUTS:
        for which in SETS:
            s = fixed[(r, which)]
            lines += ["", "### {}, {}, fixed thresholds".format(READOUT_NAMES[r],
                                                              E8B.SET_NAMES[which]), "",
                      E8B.score_table(s, ARMS, which), "", "Response rates:", "",
                      E8B.response_table(s, ARMS, humans), "", "p(old | lure) by level:", "",
                      E8B.rate_by_level_table(s, ARMS, which, "old_bins"), "",
                      "p(similar | lure) by level:", "",
                      E8B.rate_by_level_table(s, ARMS, which, "sim_bins")]
    for r in READOUTS:
        lines += ["", "### Each arm with its own thresholds, {}, closer lures (secondary)".format(
            READOUT_NAMES[r]), "", E8B.score_table(own[(r, "close")], ARMS, "close", human=False)]
    for r in READOUTS:
        for which in SETS:
            s = older[(r, which)]
            lines += ["", "### Older adults' criteria, {}, {}".format(READOUT_NAMES[r],
                                                                     E8B.SET_NAMES[which]), "",
                      E8B.response_table(s, OLDER_ARMS, humans), "", "p(old | lure) by level:", "",
                      E8B.rate_by_level_table(s, OLDER_ARMS, which, "old_bins")]
    return "\n".join(lines) + "\n"


def score_all(record, cal):
    fixed = {(r, w): score_record(record, cal, r, w) for r in READOUTS for w in SETS}
    own = {(r, w): score_record(record, cal, r, w, "own") for r in READOUTS for w in SETS}
    older = {(r, w): score_record(record, cal, r, w, "older") for r in READOUTS for w in SETS}
    return fixed, own, older


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--calibrate", action="store_true")
    args = p.parse_args()
    if args.calibrate:
        record = json.loads(BACKGROUND.read_text())
        if not record["complete"]:
            raise SystemExit("{} is incomplete".format(BACKGROUND.name))
        ref = json.loads(E8B_BACKGROUND.read_text()) if E8B_BACKGROUND.is_file() else None
        edges = json.loads(E8B.E8_CALIBRATION.read_text())["bin_edges"]
        cal = calibrate(record, ref, edges)
        CALIBRATION.write_text(json.dumps(cal, indent=1))
        print(json.dumps({r: {a: (t["old"], t["new"], t["feasible"]) for a, t in v.items()}
                          for r, v in cal["thresholds"].items()}, indent=1))
        print("reproduces E8b:", cal["reproduces_e8b"])
        return
    cal = json.loads(CALIBRATION.read_text())
    record = json.loads(EVALUATION.read_text())
    if not record["complete"]:
        raise SystemExit("{} is incomplete".format(EVALUATION.name))
    fixed, own, older = score_all(record, cal)
    preds = predictions(cal, fixed, older, E8B_EVALUATION)
    SCORES.write_text(json.dumps({
        "fixed": {"{} {}".format(*k): v for k, v in fixed.items()},
        "own": {"{} {}".format(*k): v for k, v in own.items()},
        "older": {"{} {}".format(*k): v for k, v in older.items()},
        "predictions": [{"prediction": k, "held": h, "numbers": t} for k, h, t in preds]}))
    head = TABLES.read_text().split("## Tables")[0] if TABLES.is_file() else "# E8c results\n\n"
    TABLES.write_text(head + tables(cal, fixed, own, older, preds))
    print("Wrote {}, {}".format(TABLES.relative_to(REPO), SCORES.relative_to(REPO)))


if __name__ == "__main__":
    main()
