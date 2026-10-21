"""E8b: the recall-based readout, the scaled model, closer lures and
per-load recalibration."""

import importlib.util
import math
from pathlib import Path

import pytest
import torch

from trisynapsnet.eval import behaviour as bh
from trisynapsnet.eval import recognition as rc
from trisynapsnet.model import modules

from test_behaviour import fake_codes, sparse_codes

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "make_e8b_table.py"


def load_script():
    spec = importlib.util.spec_from_file_location("make_e8b_table", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ------------------------------------------------------------ R2's signal

def test_self_support_by_hand():
    # Cells 0-2 store one pattern, cells 2-4 another (clipped binary).
    W = torch.zeros(6, 6)
    for pat in ([0, 1, 2], [2, 3, 4]):
        for i in pat:
            for j in pat:
                if i != j:
                    W[i, j] = 1.0
    states = torch.zeros(4, 6)
    states[0, [0, 1, 2]] = 1   # a stored pattern
    states[1, [0, 1, 3]] = 1   # a mixture
    states[2, [5]] = 1         # a cell with no potentiated input
    states[3, [0, 1]] = 1      # part of a stored pattern
    s = rc.self_support(W, states)
    # Pattern A: inputs onto 0, 1 come only from A (2 each); onto 2 from
    # 0, 1, 3, 4 (4), of which 2 inside: (2 + 2 + 2) / (2 + 2 + 4).
    assert s[0].item() == pytest.approx(6 / 8)
    # Mixture {0, 1, 3}: inside 0<->1 only (2); total onto 0, 1, 3: 2 + 2 + 2.
    assert s[1].item() == pytest.approx(2 / 6)
    assert s[2].item() == 0.0
    assert s[3].item() == pytest.approx(2 / 4)


def test_self_support_is_one_for_an_isolated_stored_pattern():
    ca3 = modules.CA3(50, k=5, start="cue")
    pats = torch.zeros(3, 50)
    pats[0, :5] = 1
    pats[1, 10:15] = 1
    pats[2, 20:25] = 1
    ca3.train(pats, "willshaw")
    assert torch.allclose(rc.self_support(ca3.W, pats), torch.ones(3))


def test_self_support_never_reads_the_stored_list():
    # The same weights and state give the same signal whatever list is
    # passed around: the function takes only W and the state.
    import inspect
    assert list(inspect.signature(rc.self_support).parameters) == ["W", "states"]


def test_nearest_overlap_is_a_list_lookup_logged_beside_r2():
    stored = torch.tensor([[1., 1., 1., 0., 0., 0.], [0., 0., 0., 1., 1., 1.]])
    states = torch.tensor([[1., 1., 0., 1., 0., 0.], [0., 0., 0., 1., 1., 1.]])
    assert rc.nearest_overlap(states, stored).tolist() == pytest.approx([2 / 3, 1.0])


# ------------------------------------------------------------ the scaled model

def test_scaled_model_keeps_human_proportions_and_e1d_sparsity():
    cfg = rc.scaled_model(1000)
    assert (cfg["dg_units"], cfg["ca3_units"], cfg["ca1_units"]) == (15000, 1700, 16000)
    assert cfg["dg_k"] == 300 and cfg["ca3_k"] == 34
    assert cfg["mossy_in_degree"] == 280
    # Everything else is E3's model as E8 ran it.
    for key in ("dg_gamma", "dg_knockout", "ca3_iters", "pp_presynaptic", "pp_normalise",
                "pp_emax", "ca1_plateau_share", "ca1_connect", "ca1_gate"):
        assert cfg[key] == bh.MODEL[key]
    rat = rc.scaled_model(100, rc.RAT_CELLS)
    assert (rat["dg_units"], rat["ca3_units"], rat["ca1_units"]) == (10000, 2100, 3500)


def test_perforant_wiring_in_blocks_matches_perforant_path():
    pp = modules.PerforantPath(3000, 300, 6, "willshaw", seed=17)
    C = rc.wire_perforant(300, 3000, 17, block=37)
    assert torch.equal(C, pp.C)
    assert torch.all(C.sum(dim=1) == pp.in_degree)


def test_stream_dg_gives_k_cells_and_is_fixed_by_the_seed():
    codes = sparse_codes(12, 500, 40, seed=1)
    dg = rc.StreamDG(500, 300, 6, seed=4, block=64)
    a = dg(codes)
    assert torch.all(a.sum(dim=1) == 6)
    assert torch.equal(a, rc.StreamDG(500, 300, 6, seed=4, block=64)(codes))
    # Blocks change nothing but memory.
    W = torch.cat([dg.weights(s, min(s + 64, 300)) for s in range(0, 300, 64)])
    assert torch.allclose(dg.drive(codes), codes @ W.T, atol=1e-5)
    # About a quarter of weights knocked out, the rest within Xavier's bound.
    assert abs((W == 0).float().mean().item() - 0.25) < 0.01
    assert W.abs().max().item() <= math.sqrt(6 / 800)
    assert not torch.equal(a, rc.StreamDG(500, 300, 6, seed=5, block=64)(codes))


def test_mossy_fibres_give_each_ca3_cell_its_dg_inputs():
    mf = rc.MossyFibres(1000, 210, 46, seed=3)
    assert mf.idx.shape == (210, 46)
    assert all(len(set(row)) == 46 for row in mf.idx.tolist())
    assert torch.all((mf.w >= 0) & (mf.w < 1))
    dg = torch.zeros(2, 1000)
    dg[0, :20] = 1
    dg[1, 500:520] = 1
    pats = mf.patterns(dg, 4)
    assert torch.all(pats.sum(dim=1) == 4)
    # A CA3 cell with no active DG input has no drive.
    drive = mf.drive(dg)
    has_input = torch.isin(mf.idx, torch.arange(20)).any(dim=1)
    assert torch.all(drive[0, ~has_input] == 0)
    assert torch.all(drive[0, has_input] > 0)


def test_sparse_btsp_is_the_same_rule():
    X = torch.zeros(5, 40)
    for t in range(5):
        X[t, t * 3:t * 3 + 4] = 1
    E = sparse_codes(5, 200, 20, seed=2)
    # With every gate open the rule is deterministic: identical weights and traces.
    a = modules.CA1BTSP(40, 200, 300, 0.02, 0.6, 1.0, seed=9)
    b = rc.CA1Sparse(40, 200, 300, 0.02, 0.6, 1.0, seed=9)
    ta, tb = a.store(X, E), b.store(X, E)
    assert torch.equal(a.W, b.W) and torch.equal(ta, tb)
    assert torch.equal(a(X), b(X))
    # With gate 0.5, only plateau x active synapses change, about half of them.
    c = rc.CA1Sparse(40, 200, 2000, 0.05, 1.0, 0.5, seed=1)
    plateau = c.plateaus(E[:1])[0]
    c.btsp(X[0], plateau)
    eligible = (plateau > 0)[:, None] & (X[0] > 0)[None, :]
    assert torch.all(c.W[~eligible] == 0)
    share = c.W[eligible].mean().item()
    assert 0.4 < share < 0.6


def test_scaled_memory_recalls_studied_drawings_and_lesions_change_their_part():
    dim, seed = 2000, 5
    cfg = rc.scaled_model(4000)  # DG 3,750, CA3 425, CA1 4,000
    study = sparse_codes(10, dim, 80, seed=7)
    shared = rc.Study(study, seed, cfg)
    assert torch.all(shared.ca3_patterns.sum(dim=1) == cfg["ca3_k"])
    base = torch.zeros(dim)
    mem = rc.Memory(study, seed, base, cfg, shared)
    sig, states = mem.recall(study, list(rc.SHARED_ARMS))
    # Repeats settle on their own stored pattern; R2 sees a strong attractor.
    d = mem.describe(states["intact"], torch.arange(10))
    assert sum(d["exact_paired"]) >= 9
    assert sig["r2"]["intact"].mean() > 0.5
    # No recurrent synapses or no CA3: nothing for R2 to read.
    assert torch.all(sig["r2"]["no_recurrent"] == 0) and torch.all(sig["r2"]["no_ca3"] == 0)
    assert torch.equal(sig["r1"]["vc_baseline"], sig["r2"]["vc_baseline"])
    thin = rc.Memory(study, seed, base, cfg, shared, lesion="pp_keep0.5")
    assert torch.equal(thin.stored, mem.stored)
    assert torch.all(thin.pp.C.sum(dim=1) == math.floor(0.5 * shared.C[0].sum().item() + 0.5))
    # Plateaus computed once per list are exactly the ones CA1 would compute.
    fresh = rc.CA1Sparse(cfg["ca3_units"], dim, cfg["ca1_units"], cfg["ca1_plateau_share"],
                         cfg["ca1_connect"], cfg["ca1_gate"], seed=seed, ec3_baseline=base)
    fresh.store(mem.stored > 0, study)
    assert torch.equal(fresh.W, mem.ca1.W)
    nodg = rc.Memory(study, seed, base, cfg, shared, lesion="no_dg")
    assert torch.equal(nodg.stored, bh.pp_patterns(shared.C, study, cfg["ca3_k"]))


def test_run_list_gives_both_readouts_for_every_arm_and_closer_lures():
    codes, _ = fake_codes(n_characters=40, dim=600)
    lst = bh.build_list(codes.n_characters, 10, 1, torch.Generator().manual_seed(4))
    cfg = rc.scaled_model(8000)  # DG 1,875, CA3 212, CA1 2,000
    src = lst["paired"][lst["types"] == 1]
    study = codes.dense([codes.index(c, d) for c, d in lst["study"].tolist()])
    close = (torch.cat([study[src]] * 5), torch.arange(1, 6).repeat_interleave(len(src)),
             torch.cat([src] * 5))
    out = rc.run_list(codes, lst, 3, torch.zeros(600), list(rc.ARMS), cfg, close=close)
    n = 15 + 25
    for r in rc.READOUTS:
        assert set(out["signal"][r]) == set(rc.ARMS)
        assert all(len(v) == n for v in out["signal"][r].values())
    assert set(out["ca3"]) == set(rc.CA3_ARMS)
    assert out["types"].count(3) == 25 and out["level"][-1] == 5
    sim = torch.tensor(out["similarity"])
    # Undistorted "closer lures" here are the studied drawings themselves.
    assert torch.allclose(sim[15:], torch.ones(25))
    # A closer lure identical to its studied drawing gets that drawing's signals.
    r2 = torch.tensor(out["signal"]["r2"]["intact"])
    paired = torch.tensor(out["paired"])
    for i in range(15, 20):
        same = (torch.tensor(out["types"])[:15] == 1) & (paired[:15] == paired[i])
        assert same.any()
    assert r2[15:].min() >= 0 and r2[15:].max() <= 1
    assert set(out["ca3"]["intact"]) >= {"nearest_overlap", "cue_support", "exact_paired"}


# ------------------------------------------------------------ closer lures

def test_distortion_at_zero_is_the_drawing_and_grows_with_magnitude():
    img = torch.zeros(3, 1, 52, 52)
    img[:, 0, 20:32, 25:27] = 1
    img[:, 0, 25:27, 18:34] = 1
    img = torch.stack([bh.omniglot.centre_of_mass(i) for i in img])
    g = torch.Generator().manual_seed(0)
    draws = rc.distortion_draws(3, g)
    assert torch.allclose(draws["field"].pow(2).mean(dim=(1, 2, 3)), torch.ones(3), atol=1e-4)
    assert torch.equal(rc.distort(img, draws, 0.0), img)
    flat = img.flatten(1)
    cos = [bh.cosine_rows(rc.distort(img, draws, m).flatten(1), flat).mean().item()
           for m in (0.25, 1.0, 3.0)]
    assert 1.0 > cos[0] > cos[1] > cos[2]
    # Same draws give the same distortion.
    assert torch.equal(rc.distort(img, draws, 1.0), rc.distort(img, draws, 1.0))


def test_level_targets_span_e8s_closest_lures_to_repeats():
    t = rc.level_targets(0.6)
    assert t == pytest.approx([0.96, 0.88, 0.80, 0.72, 0.64])
    assert all(0.6 < x < 1 for x in t)


# ------------------------------------------------------------ recalibration

def test_per_load_recalibration_reaches_the_rates_at_every_load():
    tb = load_script()
    g = torch.Generator().manual_seed(0)
    by_load = {}
    for load, shift in ((20, 0.0), (128, -0.2)):
        types = torch.tensor([0] * 500 + [1] * 500 + [2] * 500)
        sig = torch.cat([torch.rand(500, generator=g) * 0.2 + 0.8 + shift,
                         torch.rand(500, generator=g) * 0.5 + 0.3,
                         torch.rand(500, generator=g) * 0.5 + shift])
        by_load[load] = (sig, types)
    thr = tb.recalibrate_by_load(by_load, 0.812, 0.820)
    assert set(thr) == {20, 128}
    assert thr[20]["old"] != thr[128]["old"]
    for load, (sig, types) in by_load.items():
        r = bh.rates(sig, types, thr[load])
        assert r["repeat"]["old"] == pytest.approx(0.812, abs=1e-9)
        assert r["foil"]["new"] == pytest.approx(0.820, abs=1e-9)


def test_field_smoothing_matches_the_2d_gaussian():
    field = torch.rand(3, 2, 30, 30, generator=torch.Generator().manual_seed(1))
    size = 25
    kernel = modules.gaussian_kernel(size, 4.0)[None, None].repeat(2, 1, 1, 1)
    full = torch.nn.functional.conv2d(field, kernel, padding=size // 2, groups=2)
    assert torch.allclose(rc.smooth_fields(field, 4.0), full, atol=1e-5)


def test_ca3_description_matches_e8s():
    g = torch.Generator().manual_seed(3)
    stored = (torch.rand(6, 40, generator=g) < 0.15).float()
    final = torch.cat([stored[[0, 2]], (torch.rand(3, 40, generator=g) < 0.15).float(),
                       stored[[4]]])
    final[2, :] = stored[1]
    final[2, stored[1].argmax()] = 0
    cue = (torch.rand(6, 40, generator=g) < 0.1).float()
    paired = torch.tensor([0, 1, 1, -1, 3, 5])
    assert rc.ca3_description(cue, final, stored, paired) == \
        bh.ca3_description(cue, final, stored, paired)


def test_mossy_drive_in_blocks_is_the_weighted_sum():
    mf = rc.MossyFibres(300, 70, 20, seed=1)
    D = (torch.rand(5, 300, generator=torch.Generator().manual_seed(2)) < 0.05).float()
    M = torch.zeros(70, 300)
    M.scatter_(1, mf.idx, mf.w)
    assert torch.allclose(mf.drive(D, block=16), D @ M.T, atol=1e-6)


def test_in_place_perforant_storage_gives_the_same_weights():
    E = sparse_codes(6, 400, 40, seed=4)
    Y = torch.zeros(6, 60)
    for t in range(6):
        Y[t, t * 5:t * 5 + 3] = 1
    a = modules.PerforantPath(400, 60, 3, "willshaw", seed=2)
    b = rc.Perforant(400, 60, 3, "willshaw", seed=2)
    a.store(E[:3], Y[:3]); a.store(E[3:], Y[3:])
    b.store(E[:3], Y[:3]); b.store(E[3:], Y[3:])
    assert torch.equal(a.W, b.W)
    assert torch.equal(a.cue(E), b.cue(E))


def test_lure_sets_share_repeats_and_foils():
    tb = load_script()
    items = {"types": [0, 1, 2, 3, 3], "level": [0, 0, 0, 1, 5],
             "similarity": [1.0, 0.7, None, 0.95, 0.7]}
    types, bins, keep = tb.lure_set(items, "drawer", [0.46, 0.54, 0.6, 0.66])
    assert keep.tolist() == [True, True, True, False, False]
    assert bins[1].item() == 1
    types, bins, keep = tb.lure_set(items, "close", [0.46, 0.54, 0.6, 0.66])
    assert keep.tolist() == [True, False, True, True, True]
    assert types[keep].tolist() == [0, 2, 1, 1] and bins[keep][2:].tolist() == [1, 5]


def test_level_monotone_rule():
    tb = load_script()
    assert tb.monotone([0.5, 0.4, 0.42, 0.2, 0.1], falling_with_level=True)
    assert not tb.monotone([0.5, 0.4, 0.5, 0.2, 0.1], falling_with_level=True)
    assert tb.monotone([0.1, 0.2, 0.18, 0.3, 0.4], falling_with_level=False)


def fake_record():
    """Two seeds; per seed 2 repeats, 2 lures, 2 foils and 10 closer lures."""
    def seed(shift):
        types = [0, 0, 1, 1, 2, 2] + [3] * 10
        level = [0] * 6 + [1, 1, 2, 2, 3, 3, 4, 4, 5, 5]
        r1 = [0.99, 0.98, 0.6, 0.4, 0.2, 0.1] + [0.97, 0.96, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4,
                                                 0.3, 0.2]
        r1 = [v - shift for v in r1]
        sig = {"r1": {a: list(r1) for a in ("intact", "no_recurrent", "vc_baseline")},
               "r2": {"intact": list(r1), "no_recurrent": [0.0] * 16,
                      "vc_baseline": list(r1)}}
        ca3 = {"exact_paired": [1, 1, 1, 0, 0, 0] + [1] * 4 + [0] * 6,
               "exact_any": [1] * 16, "cue_cells": [3] * 16,
               "nearest_overlap": [1.0] * 16, "cue_support": [0.5] * 16}
        return {"types": types, "level": level,
                "similarity": [1, 1, 0.7, 0.5, None, None] + [0.9] * 10,
                "signal": sig, "ca3": {"intact": ca3, "no_recurrent": ca3}}
    return {"args": {"arms": ["intact", "no_recurrent", "vc_baseline"]},
            "per_seed": {"0": seed(0.0), "1": seed(0.01)}}


def test_scoring_a_record_with_both_readouts_and_lure_sets():
    tb = load_script()
    rec = fake_record()
    thr = {"old": 0.95, "q_old": 0.0, "new": 0.35, "q_new": 0.0, "feasible": True}
    cal = {"thresholds": {"r1": {"intact": thr, "vc_baseline": thr},
                          "r2": {"intact": thr, "vc_baseline": thr}},
           "by_load": {"r1": {}, "r2": {}}, "bin_edges": [0.46, 0.54, 0.6, 0.66]}
    close = tb.score_record(rec, cal, "r2", "close")
    s = close["intact"]
    # Closer lures C1 (0.97, 0.96) are old; C5 (0.3, 0.2) new.
    assert s["old_bins 1"]["mean"] == pytest.approx(0.75)
    assert s["old_bins 5"]["mean"] == 0.0
    assert s["ca3 lure_exact"]["mean"] == pytest.approx(0.4)
    assert s["rec"]["mean"] == pytest.approx(1.0)
    # No R2 signal: every item new.
    assert close["no_recurrent"]["rates repeat new"]["mean"] == 1.0
    drawer = tb.score_record(rec, cal, "r1", "drawer")
    assert drawer["intact"]["rates lure similar"]["mean"] == pytest.approx(1.0)
    assert drawer["intact"]["ca3 lure_exact"]["mean"] == pytest.approx(0.5)


def test_plateaus_shared_for_study_and_test_codes_match_ca1s_own():
    dim, seed = 500, 3
    cfg = rc.scaled_model(8000)
    study = sparse_codes(6, dim, 40, seed=1)
    test = sparse_codes(9, dim, 40, seed=2)
    shared = rc.Study(study, seed, cfg)
    shared.share_plateaus(test, torch.zeros(dim), cfg, seed)
    ca1 = rc.CA1Sparse(cfg["ca3_units"], dim, cfg["ca1_units"], cfg["ca1_plateau_share"],
                       cfg["ca1_connect"], cfg["ca1_gate"], seed=seed, ec3_baseline=torch.zeros(dim))
    assert torch.equal(shared.plateaus, ca1.plateaus(study))
    assert torch.equal(shared.test_plateaus, ca1.plateaus(test))
    mem = rc.Memory(study, seed, torch.zeros(dim), cfg, shared)
    sig, _ = mem.recall(test, ["no_ca3"])
    expect = bh.cosine_rows(test, mem.ca1.reinstate(ca1.plateaus(test)))
    assert torch.allclose(sig["r1"]["no_ca3"], expect)
