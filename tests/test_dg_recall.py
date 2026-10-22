"""E9: DG's response to the test drawing reaches CA3 through the mossy
fibres during attractor dynamics, with entorhinal input kept on; inputs in
units of one potentiated recurrent synapse."""

import pytest
import torch

from trisynapsnet.eval import behaviour as bh
from trisynapsnet.eval import dgrecall as dr
from trisynapsnet.eval import recognition as rc
from trisynapsnet.eval import starting as st
from trisynapsnet.model import modules

from test_behaviour import fake_codes, sparse_codes


# ------------------------------------------------------------ settings

def test_strengths_are_the_measured_ratios():
    assert dr.PERFORANT_UNITS == pytest.approx(0.34 / 0.56)
    assert dr.MOSSY_UNITS_MAIN == pytest.approx(9.6 / 0.56)
    assert dr.MOSSY_UNITS_LOW == pytest.approx(1.0 / 0.54)
    assert round(dr.MOSSY_UNITS_MAIN, 1) == 17.1 and round(dr.MOSSY_UNITS_LOW, 1) == 1.9
    assert round(dr.PERFORANT_UNITS, 2) == 0.61


def test_conditions_differ_only_in_the_input_during_attractor_dynamics():
    s = dr.SETTINGS
    assert s["e8c"] == {"ec": False, "mossy": None}
    assert s["ec"] == {"ec": True, "mossy": None}
    assert s["dg1.9"] == {"ec": True, "mossy": dr.MOSSY_UNITS_LOW}
    assert s["dg17.1"] == {"ec": True, "mossy": dr.MOSSY_UNITS_MAIN}


# ------------------------------------------------------------ DG at test

def test_end_of_study_record_is_streamdgs_mask_after_the_list():
    codes = sparse_codes(12, 300, 40, seed=1)
    dg = rc.StreamDG(300, 400, 8, gamma=0.95, knockout=0.25, seed=3)
    patterns = dg(codes)
    # The mask StreamDG holds after the list, rebuilt step by step.
    phi = modules.InhibitionMask(400, 0.95)
    Z = dg.drive(codes)
    for i in range(codes.shape[0]):
        s = modules.get_top_k(Z[i:i + 1] * phi(), 8, "binary", 1, 1)
        assert torch.equal(s[0], patterns[i])
        phi.update(s)
    assert torch.equal(dr.end_of_study_record(patterns, 0.95), phi())


def test_frozen_record_partly_inhibits_the_last_drawings_studied():
    patterns = torch.zeros(5, 10)
    for i in range(5):
        patterns[i, 2 * i:2 * i + 2] = 1
    mask = dr.end_of_study_record(patterns, 0.5)[0]
    # The last drawing's cells: inhibited 0.5 at its own step, mask 0.5;
    # the first drawing's cells: 0.5 ** 5 inhibition left.
    assert mask[8].item() == pytest.approx(0.5)
    assert mask[0].item() == pytest.approx(1 - 0.5 ** 5)
    assert torch.all(mask[2 * torch.arange(5)].diff() < 0)


def test_dg_response_without_a_record_repeats_the_study_pattern():
    codes = sparse_codes(6, 200, 30, seed=2)
    dg = rc.StreamDG(200, 300, 6, gamma=0.0, knockout=0.25, seed=4)
    patterns = dg(codes)
    mask = dr.end_of_study_record(patterns, 0.0)
    assert torch.all(mask == 1)
    assert torch.equal(dr.dg_response(dg, codes, mask), patterns)


def test_dg_response_does_not_depend_on_the_other_test_items():
    codes = sparse_codes(8, 200, 30, seed=5)
    dg = rc.StreamDG(200, 300, 6, seed=6)
    mask = dr.end_of_study_record(dg(codes[:4]), 0.95)
    both = dr.dg_response(dg, codes, mask)
    alone = torch.cat([dr.dg_response(dg, codes[i:i + 1], mask) for i in range(8)])
    assert torch.equal(both, alone)
    assert torch.all(both.sum(dim=1) == 6)


# ------------------------------------------------------------ input units

def test_mossy_units_rescale_the_mean_weight_and_keep_the_spread():
    mossy = rc.MossyFibres(500, 60, in_degree=20, seed=1)
    D = torch.zeros(1, 500)
    D[0, mossy.idx[0]] = 1          # every input of CA3 cell 0 active
    raw = mossy.drive(D)
    units = dr.mossy_units(mossy, raw, 17.0)
    scale = 17.0 / mossy.w.mean().item()
    assert units[0, 0].item() == pytest.approx(mossy.w[0].sum().item() * scale, rel=1e-5)
    assert torch.allclose(units, raw * scale)


def test_perforant_units_count_active_inputs_on_potentiated_synapses():
    pp = modules.PerforantPath(6, 3, 1, "willshaw", share=1.0)
    pp.W = torch.tensor([[1., 1, 0, 0, 0, 0], [0, 0, 1, 1, 1, 0], [0, 0, 0, 0, 0, 0]])
    E = torch.tensor([[0.5, 0.0, 0.2, 0.3, 0.0, 0.9]])
    out = dr.perforant_units(pp, E)
    # Cell 0: input 0 active on a potentiated synapse; cell 1: inputs 2 and 3;
    # cell 2: none (input 5 is active but its synapse is not potentiated).
    assert out[0].tolist() == pytest.approx([dr.PERFORANT_UNITS, 2 * dr.PERFORANT_UNITS, 0.0])


# ------------------------------------------------------------ attractor dynamics

def stored_ca3(n=120, k=10, n_pat=6, seed=0):
    g = torch.Generator().manual_seed(seed)
    pats = torch.zeros(n_pat, n)
    for p in range(n_pat):
        pats[p, torch.randperm(n, generator=g)[:k]] = 1
    ca3 = modules.CA3(n, n_iter=70, k=k, start="cue")
    ca3.train(pats, "willshaw")
    return ca3, pats


def test_without_external_input_the_dynamics_are_e8cs():
    ca3, pats = stored_ca3()
    g = torch.Generator().manual_seed(1)
    cues = torch.zeros(20, 120)
    for i in range(20):
        keep = pats[i % 6].nonzero().flatten()[:6]
        cues[i, keep] = 1
        cues[i, torch.randperm(120, generator=g)[:3]] = 1
    final, rounds, fixed = dr.attractor_dynamics(ca3.W, cues, 0, 10, 70)
    ref, info = ca3.settle(cues)
    assert torch.equal(final, ref)
    assert torch.equal(rounds, info["iterations"]) and torch.equal(fixed, info["fixed"])


def test_strong_external_input_decides_the_final_state():
    ca3, pats = stored_ca3()
    start = pats[:1].clone()               # starts exactly on stored pattern 0
    target = torch.zeros(1, 120)
    target[0, (pats.sum(dim=0) == 0).nonzero().flatten()[:10]] = 1   # cells no pattern uses
    weak, _, _ = dr.attractor_dynamics(ca3.W, start, 1.9 * target, 10, 70)
    strong, rounds, fixed = dr.attractor_dynamics(ca3.W, start, 96.0 * target, 10, 70)
    assert torch.equal(weak, pats[:1])     # 9 recurrent units beat 1.9
    assert torch.equal(strong, target)     # 96 units beat at most 9
    assert fixed.all() and rounds.item() == 1


def test_every_round_keeps_k_cells():
    ca3, pats = stored_ca3()
    start = torch.zeros(3, 120)
    start[:, :4] = 1                        # a starting state smaller than k
    ext = torch.rand(3, 120, generator=torch.Generator().manual_seed(2))
    final, _, _ = dr.attractor_dynamics(ca3.W, start, ext, 10, 70)
    assert torch.all(final.sum(dim=1) == 10)


# ------------------------------------------------------------ the runner

def small_list(n_characters=40, dim=600, load=10, seed=4):
    codes, _ = fake_codes(n_characters=n_characters, dim=dim)
    lst = bh.build_list(codes.n_characters, load, 1, torch.Generator().manual_seed(seed))
    study = codes.dense([codes.index(c, d) for c, d in lst["study"].tolist()])
    src = lst["paired"][lst["types"] == 1]
    close = (torch.cat([study[src]] * 5), torch.arange(1, 6).repeat_interleave(len(src)),
             torch.cat([src] * 5))
    return codes, lst, close


def test_e8c_condition_is_e8cs_runner_exactly():
    codes, lst, close = small_list()
    cfg = rc.scaled_model(8000)
    out = dr.run_list(codes, lst, 3, torch.zeros(600), list(rc.ARMS), cfg, close=close)
    ref = st.run_list(codes, lst, 3, torch.zeros(600), list(rc.ARMS), cfg, close=close)
    e8c = out["conditions"]["e8c"]
    assert e8c["signal"] == ref["signal"]
    assert e8c["ca3"] == ref["ca3"]
    for key in ("types", "paired", "level"):
        assert out[key] == ref[key]
    assert torch.equal(torch.tensor(out["similarity"]).isnan(), torch.tensor(ref["similarity"]).isnan())
    assert torch.allclose(torch.tensor(out["similarity"]).nan_to_num(),
                          torch.tensor(ref["similarity"]).nan_to_num())


def test_every_condition_keeps_the_starting_state():
    codes, lst, close = small_list()
    cfg = rc.scaled_model(8000)
    out = dr.run_list(codes, lst, 3, torch.zeros(600), list(rc.ARMS), cfg, close=close)
    base = out["conditions"]["e8c"]["signal"]
    for c in dr.CONDITIONS:
        sig = out["conditions"][c]["signal"]
        for r in ("r3", "r3s"):
            assert sig[r] == base[r]
        for r in st.READOUTS:
            assert set(sig[r]) == set(rc.ARMS)
            assert sig[r]["no_ca3"] == base[r]["no_ca3"]
            assert sig[r]["vc_baseline"] == base[r]["vc_baseline"]
        if c != "e8c":
            for r in ("r2", "r3", "r3s"):
                assert all(v == 0 for v in sig[r]["no_recurrent"])
            log = out["conditions"][c]["ca3"]["intact"]
            assert {"rounds", "fixed", "dg_follow", "exact_any", "exact_paired"} <= set(log)
            assert all(v == -1 for v in out["conditions"][c]["ca3"]["no_dg"]["dg_follow"])


def test_without_dg_every_dg_condition_equals_the_ec_control():
    codes, lst, close = small_list()
    cfg = rc.scaled_model(8000)
    out = dr.run_list(codes, lst, 3, torch.zeros(600), ["intact", "no_dg"], cfg, close=close)
    ec = out["conditions"]["ec"]
    for c in ("dg1.9", "dg17.1"):
        for r in st.READOUTS:
            assert out["conditions"][c]["signal"][r]["no_dg"] == ec["signal"][r]["no_dg"]


def test_main_strength_makes_ca3_follow_dg():
    codes, lst, close = small_list()
    cfg = rc.scaled_model(8000)
    out = dr.run_list(codes, lst, 3, torch.zeros(600), ["intact"], cfg, close=close)
    follow = {c: torch.tensor(out["conditions"][c]["ca3"]["intact"]["dg_follow"]).mean().item()
              for c in ("ec", "dg1.9", "dg17.1")}
    assert follow["dg17.1"] > follow["ec"]
    assert follow["dg17.1"] > 0.9


def test_dg_paired_overlap_is_logged_for_repeats_and_lures_only():
    codes, lst, close = small_list()
    cfg = rc.scaled_model(8000)
    out = dr.run_list(codes, lst, 3, torch.zeros(600), ["intact"], cfg, close=close)
    ov = torch.tensor(out["dg_paired_overlap"])
    types = torch.tensor(out["types"])
    assert torch.all(ov[types == 2] == -1)
    assert torch.all((ov[types != 2] >= 0) & (ov[types != 2] <= 1))


# ------------------------------------------------------------ the table script

def load_table_script():
    import importlib.util
    from pathlib import Path
    path = Path(__file__).resolve().parents[1] / "scripts" / "make_e9_table.py"
    spec = importlib.util.spec_from_file_location("make_e9_table", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def synthetic_condition(condition, seeds=(0, 1), n=40):
    """test_starting_state's synthetic record, with the fields E9 logs: foils
    end on a stored pattern in E8c's model and the EC-on control, rarely
    with DG at recall; repeats on their own pattern."""
    from test_starting_state import synthetic_record
    rec = synthetic_record(seeds=seeds, n=n)
    rec["args"]["load"] = n
    foil_any = {"e8c": 1, "ec": 1, "dg1.9": 1, "dg17.1": 0}[condition]
    for s, items in rec["per_seed"].items():
        types = items["types"]
        m = len(types)
        items["paired"] = [i % n if t != 2 else -1 for i, t in enumerate(types)]
        log = {"cue_cells": [68] * m, "nearest_overlap": [1.0] * m, "cue_support": [0.2] * m,
               "exact_paired": [1 if t == 0 else 0 for t in types],
               "exact_any": [1 if t != 2 else foil_any for t in types]}
        if condition != "e8c":
            log.update({"rounds": [2] * m, "fixed": [1] * m,
                        "dg_follow": [0.9 if condition == "dg17.1" else 0.1] * m})
        for arm in ("intact", "no_recurrent", "no_dg") + tuple(
                "pp_keep{:g}".format(f) for f in rc.PP_KEEP):
            items["ca3"][arm] = dict(log)
        items["dg_paired_overlap"] = [0.9 if t == 0 else (-1 if t == 2 else 0.3) for t in types]
    return rec


def synthetic_split():
    return {c: synthetic_condition(c) for c in dr.CONDITIONS}


def test_table_script_calibration_passes_when_e8cs_model_reproduces_e8c():
    tb = load_table_script()
    records = synthetic_split()
    ref = synthetic_condition("e8c")
    ref_cal = tb.E8C.calibrate(ref, None, None)
    cal = tb.calibrate(records, ref, ref_cal, [0.46, 0.54, 0.6, 0.66])
    assert cal["checks"]["passed"]
    assert cal["checks"]["e8c_thresholds"] == 0
    assert set(cal["conditions"]) == set(dr.CONDITIONS)
    assert cal["conditions"]["dg17.1"]["thresholds"]["r2"]["intact"]["feasible"]


def test_table_script_checks_catch_each_kind_of_difference():
    tb = load_table_script()
    edges = [0.46, 0.54, 0.6, 0.66]
    ref = synthetic_condition("e8c")
    ref_cal = tb.E8C.calibrate(ref, None, None)
    # (a) a changed signal under E8c's model
    records = synthetic_split()
    records["e8c"]["per_seed"]["1"]["signal"]["r1"]["intact"][5] += 0.01
    cal = tb.calibrate(records, ref, ref_cal, edges)
    assert not cal["checks"]["passed"]
    assert cal["checks"]["e8c_signals"]["r1"] == pytest.approx(0.01)
    # (c) a starting-state signal that differs between conditions
    records = synthetic_split()
    records["dg17.1"]["per_seed"]["0"]["signal"]["r3"]["intact"][2] += 0.5
    cal = tb.calibrate(records, ref, ref_cal, edges)
    assert not cal["checks"]["passed"]
    assert cal["checks"]["starting_state"]["r3"] == pytest.approx(0.5)
    # missing reference files fail the check
    cal = tb.calibrate(synthetic_split(), None, None, edges)
    assert not cal["checks"]["passed"]


def test_check_command_refuses_a_failed_calibration(tmp_path, monkeypatch):
    tb = load_table_script()
    f = tmp_path / "cal.json"
    monkeypatch.setattr(tb, "CALIBRATION", f)
    f.write_text('{"checks": {"passed": false}}')
    with pytest.raises(SystemExit):
        tb.main(["--check"])
    f.write_text('{"checks": {"passed": true}}')
    tb.main(["--check"])


def test_table_script_scores_every_prediction():
    tb = load_table_script()
    records = synthetic_split()
    ref = synthetic_condition("e8c")
    cal = tb.calibrate(records, ref, tb.E8C.calibrate(ref, None, None), [0.46, 0.54, 0.6, 0.66])
    scores = tb.score_all(records, cal)
    preds = tb.predictions(records, cal, scores)
    keys = [k for k, _, _ in preds]
    assert keys[:4] == ["H1", "H2", "H2, other-drawer lures", "H3"]
    assert {"4", "5", "6", "7", "8", "9"} <= set(keys)
    out = dict((k, v) for k, v, _ in preds)
    # Foils stop ending on stored patterns only with DG at 17.1 units.
    assert out["H1"] == "supported"
    assert out["H1 (1.9 units, reported)"] == "falsified"
    assert out["4"] == "held" and out["7"] == "held"
    ca3 = {c: tb.ca3_summary(records[c]) for c in dr.CONDITIONS}
    assert ca3["dg17.1"]["foils on any stored pattern"]["mean"] == 0
    assert ca3["ec"]["repeats on their own pattern"]["mean"] == 1
    text = tb.tables(cal, scores, ca3, tb.dg_overlap_summary(records["dg17.1"]), preds)
    assert text.startswith("## Tables") and "older adults' criteria" in text


def test_sign_test():
    tb = load_table_script()
    assert tb.sign_test([1, 1, 1, 1, 1, 1, 1, 1, 1, 1]) == (10, 0, pytest.approx(2 / 1024))
    assert tb.sign_test([0, 0]) == (0, 0, 1.0)
    pos, neg, p = tb.sign_test([1, -1, 1, -1])
    assert (pos, neg) == (2, 2) and p == 1.0
