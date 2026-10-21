"""E8: task builder, decision rule, scores, lure bins and lesions."""

import math

import pytest
import torch
from torch import nn

from trisynapsnet.eval import behaviour as bh
from trisynapsnet.model import modules
from trisynapsnet.model.aha import AHA, AHAConfig


def sparse_codes(n, dim, active, seed=0):
    g = torch.Generator().manual_seed(seed)
    codes = torch.zeros(n, dim)
    for i in range(n):
        idx = torch.randperm(dim, generator=g)[:active]
        codes[i, idx] = torch.rand(active, generator=g) + 0.1
    return codes


def fake_codes(n_characters=12, drawers=20, dim=300, seed=0):
    """A Codes object over synthetic drawings: drawers of one character
    share most of their active units."""
    g = torch.Generator().manual_seed(seed)
    rows = []
    for c in range(n_characters):
        base = sparse_codes(1, dim, 30, seed=seed * 100 + c)[0]
        for d in range(drawers):
            row = base.clone()
            flip = torch.randperm(dim, generator=g)[:6]
            row[flip] = torch.rand(6, generator=g) * (torch.rand(6, generator=g) > 0.5)
            rows.append(row)
    dense = torch.stack(rows)
    parts = [bh.to_sparse(dense[:100]), bh.to_sparse(dense[100:])]
    return bh.Codes(bh.from_parts(parts, dim, [["a", str(c)] for c in range(n_characters)],
                                  drawers)), dense


# ------------------------------------------------------------ vision codes

def test_sparse_cache_gives_back_the_dense_codes():
    codes, dense = fake_codes()
    idx = [0, 5, 119, 120, 239]
    assert torch.equal(codes.dense(idx), dense[idx])
    assert codes.index(3, 1) == 60 and codes.index(3, 20) == 79
    assert codes.n_characters == 12


# ------------------------------------------------------------ the task

def test_list_has_repeats_lures_and_foils_in_mst_proportions():
    lst = bh.build_list(200, 20, 1, torch.Generator().manual_seed(1))
    study, test, types, paired = lst["study"], lst["test"], lst["types"], lst["paired"]
    assert study.shape == (20, 2) and test.shape == (30, 2)
    assert (types == 0).sum() == 10 and (types == 1).sum() == 10 and (types == 2).sum() == 10
    studied = {tuple(x) for x in study.tolist()}
    studied_chars = set(study[:, 0].tolist())
    assert len(studied_chars) == 20
    # Each studied drawing is tested once, as a repeat or as the source of a lure.
    assert sorted(paired[types < 2].tolist()) == list(range(20))
    for t, (c, d), p in zip(types.tolist(), test.tolist(), paired.tolist()):
        if t == 0:
            assert (c, d) == tuple(study[p].tolist())
        elif t == 1:
            assert c == study[p, 0].item() and (c, d) not in studied
        else:
            assert p == -1 and c not in studied_chars
    # Foils are distinct characters.
    assert len(set(test[types == 2, 0].tolist())) == 10
    again = bh.build_list(200, 20, 1, torch.Generator().manual_seed(1))
    assert torch.equal(again["test"], test)
    other = bh.build_list(200, 20, 1, torch.Generator().manual_seed(2))
    assert not torch.equal(other["test"], test)


def test_list_with_several_drawings_per_character():
    lst = bh.build_list(200, 20, 4, torch.Generator().manual_seed(0))
    study, test, types = lst["study"], lst["test"], lst["types"]
    chars = study[:, 0]
    assert len(set(chars.tolist())) == 5
    for c in set(chars.tolist()):
        drawers = study[chars == c, 1].tolist()
        assert len(drawers) == 4 == len(set(drawers))
    lure_rows = test[types == 1]
    in_list = {tuple(x) for x in study.tolist()}
    assert all(tuple(x) not in in_list for x in lure_rows.tolist())
    # Two lures of one character come from two different drawers.
    assert len({tuple(x) for x in lure_rows.tolist()}) == len(lure_rows)
    with pytest.raises(ValueError):
        bh.build_list(200, 21, 1, torch.Generator())
    with pytest.raises(ValueError):
        bh.build_list(20, 20, 1, torch.Generator())


def test_lure_similarity_is_the_cosine_with_the_paired_drawing():
    study = torch.tensor([[1.0, 0.0], [0.0, 1.0]])
    test = torch.tensor([[1.0, 1.0], [0.0, 2.0], [3.0, 0.0]])
    sim = bh.lure_similarity(test, study, torch.tensor([0, 1, -1]))
    assert sim[0].item() == pytest.approx(1 / math.sqrt(2))
    assert sim[1].item() == pytest.approx(1.0)
    assert math.isnan(sim[2].item())


def test_cosine_of_an_empty_return_is_zero():
    x = torch.tensor([[1.0, 2.0], [1.0, 0.0]])
    r = torch.tensor([[0.0, 0.0], [2.0, 0.0]])
    assert bh.cosine_rows(x, r).tolist() == [0.0, 1.0]


# ------------------------------------------------------------ decisions

def test_thresholds_reach_the_rates_on_a_continuous_signal():
    repeats = torch.linspace(0.5, 1.0, 1000)
    foils = torch.linspace(0.0, 0.6, 1000)
    thr = bh.calibrate(repeats, foils, 0.812, 0.820)
    assert thr["feasible"]
    r = bh.rates(torch.cat([repeats, foils]),
                 torch.cat([torch.zeros(1000), torch.full((1000,), 2)]).long(), thr)
    assert r["repeat"]["old"] == pytest.approx(0.812, abs=1e-9)
    assert r["foil"]["new"] == pytest.approx(0.820, abs=1e-9)
    assert sum(r["repeat"].values()) == pytest.approx(1.0)


def test_thresholds_split_ties_to_reach_the_rate():
    # 90% of repeats sit at exactly 1.0, as the vision-code baseline's do.
    repeats = torch.tensor([1.0] * 90 + [0.5] * 10)
    theta, q = bh.threshold_for(repeats, 0.812, above=True)
    assert theta == 1.0 and q == pytest.approx(0.812 / 0.9)
    thr = {"old": theta, "q_old": q, "new": 0.2, "q_new": 0.0}
    p = bh.respond(repeats, thr)
    assert p[:, 0].mean().item() == pytest.approx(0.812)
    assert torch.allclose(p.sum(dim=1), torch.ones(100, dtype=torch.float64))
    foils = torch.tensor([0.0] * 50 + [0.3] * 50)
    theta_n, q_n = bh.threshold_for(foils, 0.82, above=False)
    assert theta_n == pytest.approx(0.3) and q_n == pytest.approx(0.64)


def test_old_takes_precedence_and_infeasible_thresholds_are_flagged():
    thr = bh.calibrate(torch.tensor([0.2, 0.3]), torch.tensor([0.5, 0.9]), 0.5, 0.5)
    assert not thr["feasible"]
    p = bh.respond(torch.tensor([0.9]), {"old": 0.5, "q_old": 0.0, "new": 0.95, "q_new": 0.0})
    assert p.tolist() == [[1.0, 0.0, 0.0]]


def test_ldi_and_rec_by_hand():
    # Three repeats, three lures, three foils; old above 0.8, new below 0.4.
    signal = torch.tensor([0.9, 0.95, 0.5, 0.85, 0.6, 0.3, 0.1, 0.5, 0.9])
    types = torch.tensor([0, 0, 0, 1, 1, 1, 2, 2, 2])
    thr = {"old": 0.8, "q_old": 0.0, "new": 0.4, "q_new": 0.0}
    r = bh.rates(signal, types, thr)
    assert r["repeat"] == pytest.approx({"old": 2 / 3, "similar": 1 / 3, "new": 0.0})
    assert r["lure"] == pytest.approx({"old": 1 / 3, "similar": 1 / 3, "new": 1 / 3})
    assert r["foil"] == pytest.approx({"old": 1 / 3, "similar": 1 / 3, "new": 1 / 3})
    assert bh.ldi(r) == pytest.approx(0.0)
    assert bh.rec(r) == pytest.approx(1 / 3)


def test_young_adult_scores_from_the_published_table():
    # Stark and colleagues 2013, Table 2, ages 20 to 39.
    r = {"repeat": {"old": 0.812}, "lure": {"similar": 0.476},
         "foil": {"old": 0.026, "similar": 0.116}}
    assert bh.ldi(r) == pytest.approx(0.360)
    assert bh.rec(r) == pytest.approx(0.786)


# ------------------------------------------------------------ lure bins

def test_bin_one_holds_the_most_similar_lures():
    sim = torch.arange(100, dtype=torch.float64) / 100
    edges = bh.bin_edges(sim)
    assert len(edges) == 4
    bins = bh.bin_of(sim, edges)
    assert bins[-1] == 1 and bins[0] == 5
    counts = [(bins == b).sum().item() for b in range(1, 6)]
    assert all(19 <= c <= 21 for c in counts)
    assert bh.bin_of(torch.tensor([float("nan")]), edges).item() == 0


def test_ldi_by_bin_by_hand():
    signal = torch.tensor([0.6, 0.6, 0.9, 0.9, 0.6, 0.1])
    types = torch.tensor([1, 1, 1, 1, 2, 2])
    bins = torch.tensor([5, 5, 1, 1, 0, 0])
    thr = {"old": 0.8, "q_old": 0.0, "new": 0.4, "q_new": 0.0}
    out = bh.ldi_by_bin(signal, types, bins, thr, n_bins=5)
    assert out[0] == pytest.approx(-0.5)  # bin 1 lures are all old
    assert out[4] == pytest.approx(0.5)
    assert math.isnan(out[2])


# ------------------------------------------------------------ the model

class DummyVC(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.dim = dim
        self.w = nn.Parameter(torch.zeros(1))

    def output_dim(self, image_size=52):
        return self.dim


def test_dg_and_ca1_match_e3s_model_for_the_same_seed():
    dim = 400
    config = AHAConfig(ca3_rule="covariance", dg_units=225, dg_k=5, ca1_rule="btsp",
                       ca1_units=2118, ca1_plateau_share=0.005)
    aha = AHA(DummyVC(dim), config)
    aha.ca1_baseline = torch.zeros(dim)
    aha.reset(seed=1003)
    dg = bh.build_dg(dim, 1003)
    assert torch.equal(dg.fc1.weight, aha.dg.fc1.weight)
    mem = bh.Memory(sparse_codes(6, dim, 30), 1003, torch.zeros(dim))
    assert torch.equal(mem.ca1.C, aha.ca1.C)
    assert mem.ca1.m == aha.ca1.m == 11
    pp = modules.PerforantPath(dim, 225, 5, "willshaw", seed=1003)
    assert torch.equal(mem.pp.C, pp.C)
    assert mem.pp.normalise and mem.pp.emax == 0.3


def test_thinning_keeps_a_share_of_each_cells_connections_nested():
    pp = modules.PerforantPath(20449, 225, 5, "willshaw", seed=7)
    half = bh.thin(pp.C, 0.5, 7)
    quarter = bh.thin(pp.C, 0.25, 7)
    assert torch.all(half.sum(dim=1) == 355)
    assert torch.all(quarter.sum(dim=1) == 178)
    assert not torch.any(half & ~pp.C)
    assert not torch.any(quarter & ~half)


def test_without_dg_similar_drawings_get_the_same_pattern():
    C = torch.rand(225, 400, generator=torch.Generator().manual_seed(0)) < 0.2
    codes = sparse_codes(2, 400, 40, seed=3)
    near = codes[0:1] * 1.02
    pats = bh.pp_patterns(C, torch.cat([codes, near]), 5)
    assert torch.all(pats.sum(dim=1) == 5)
    assert torch.equal(pats[0], pats[2])
    assert not torch.equal(pats[0], pats[1])


def test_lesions_change_only_their_part():
    dim, seed = 600, 11
    study = sparse_codes(8, dim, 40, seed=5)
    base = torch.zeros(dim)
    intact = bh.Memory(study, seed, base)
    no_dg = bh.Memory(study, seed, base, lesion="no_dg")
    thin = bh.Memory(study, seed, base, lesion="pp_keep0.5")
    half = bh.Memory(study, seed, base, lesion="ca1_half")
    assert torch.equal(no_dg.stored, bh.pp_patterns(intact.pp.C, study, 5))
    assert not torch.equal(no_dg.stored, intact.stored)
    assert torch.equal(thin.stored, intact.stored)
    assert torch.all(thin.pp.C.sum(dim=1) == math.floor(0.5 * intact.pp.in_degree + 0.5))
    assert half.ca1.units == 1059 and half.ca1.m == 5
    assert torch.equal(half.stored, intact.stored)


def test_recall_arms_on_studied_and_new_codes():
    dim, seed = 600, 2
    study = sparse_codes(8, dim, 40, seed=9)
    mem = bh.Memory(study, seed, torch.zeros(dim))
    foils = sparse_codes(4, dim, 40, seed=99)
    arms = ["intact", "no_recurrent", "no_ca3", "vc_baseline"]
    rep, states = mem.recall(study, arms)
    new, _ = mem.recall(foils, arms)
    # A studied code comes back nearly exactly; the vision-code baseline
    # finds it itself.
    assert torch.all(rep["intact"] > 0.95)
    assert torch.allclose(rep["vc_baseline"], torch.ones(8))
    assert rep["intact"].mean() > new["intact"].mean()
    assert rep["no_ca3"].mean() > new["no_ca3"].mean()
    # Settled studied cues are exactly their stored patterns.
    desc = bh.ca3_description(*states["intact"], mem.stored, torch.arange(8))
    assert desc["exact_paired"] == [1] * 8
    # Without recurrent connections the cue goes to CA1 unchanged.
    cue, final = states["no_recurrent"]
    assert torch.equal(cue, final)
    # The same CA3 state gives the same returned code every call.
    assert torch.equal(mem.returned(states["intact"][1]), mem.returned(states["intact"][1]))


def test_ca3_description_by_hand():
    stored = torch.tensor([[1., 1., 0., 0.], [0., 0., 1., 1.]])
    final = torch.tensor([[1., 1., 0., 0.], [1., 1., 0., 0.], [0., 1., 1., 0.]])
    cue = torch.tensor([[1., 0., 0., 0.], [1., 1., 0., 0.], [0., 1., 1., 0.]])
    d = bh.ca3_description(cue, final, stored, torch.tensor([0, 1, -1]))
    assert d["cue_cells"] == [1, 2, 2]
    assert d["exact_paired"] == [1, 0, 0]
    assert d["exact_any"] == [1, 1, 0]


def test_run_list_scores_every_arm():
    codes, _ = fake_codes(n_characters=40, dim=600)
    lst = bh.build_list(codes.n_characters, 10, 1, torch.Generator().manual_seed(4))
    out = bh.run_list(codes, lst, 3, torch.zeros(600), list(bh.ARMS))
    assert set(out["signal"]) == set(bh.ARMS)
    assert all(len(v) == 15 for v in out["signal"].values())
    assert set(out["ca3"]) == set(bh.CA3_ARMS)
    sim = torch.tensor(out["similarity"])
    assert torch.isnan(sim[lst["types"] == 2]).all()
    assert not torch.isnan(sim[lst["types"] < 2]).any()
    # Repeats are identical to their studied drawing.
    assert torch.allclose(sim[lst["types"] == 0], torch.ones(5))
