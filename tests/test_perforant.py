"""E3: the one-shot perforant path from EC to CA3."""

import pytest
import torch

from trisynapsnet.model import modules
from trisynapsnet.model.modules import PerforantPath


def test_in_degree_comes_from_the_measured_ratio():
    # Treves and Rolls 1992: up to 3,750 perforant-path synapses per rat CA3
    # cell; Arellano and Rakic 2026: 108,000 EC layer II cells.
    assert modules.PP_SHARE == pytest.approx(3750 / 108000)
    pp = PerforantPath(ec_dim=20449, n=225, k=5, rule="willshaw", seed=3)
    assert pp.in_degree == round(3750 / 108000 * 20449) == 710
    per_cell = pp.C.sum(dim=1)
    assert torch.all(per_cell == 710)
    # Fixed by the seed, different between cells and between seeds.
    again = PerforantPath(ec_dim=20449, n=225, k=5, rule="willshaw", seed=3)
    other = PerforantPath(ec_dim=20449, n=225, k=5, rule="willshaw", seed=4)
    assert torch.equal(pp.C, again.C)
    assert not torch.equal(pp.C, other.C)
    assert not torch.equal(pp.C[0], pp.C[1])


def test_in_degree_never_exceeds_the_inputs():
    pp = PerforantPath(ec_dim=10, n=4, k=2, rule="willshaw", share=0.25, seed=0)
    # Half rounds up, as every count in E1c and E1d does.
    assert pp.in_degree == 3
    full = PerforantPath(ec_dim=10, n=4, k=2, rule="willshaw", share=1.0, seed=0)
    assert torch.all(full.C)


def hand_example(rule, **kwargs):
    """Two EC units per CA3 cell, chosen by hand, and two stored drawings."""
    C = torch.tensor([[1, 1, 0, 0],
                      [0, 1, 1, 0],
                      [0, 0, 1, 1]], dtype=torch.bool)
    pp = PerforantPath(ec_dim=4, n=3, k=1, rule=rule, connections=C, **kwargs)
    E = torch.tensor([[0.5, 0.0, 0.2, 0.0],
                      [0.0, 0.3, 0.0, 0.4]])
    Y = torch.tensor([[1., 0., 0.],
                      [0., 0., 1.]])
    return pp, E, Y


def test_clipped_binary_rule_by_hand():
    pp, E, Y = hand_example("willshaw")
    pp.store(E, Y)
    # Presynaptic active means above zero. Drawing 0 has EC units 0 and 2
    # on and puts CA3 cell 0 on; cell 0 sees units 0 and 1, so only (0, 0)
    # turns on. Drawing 1 has units 1 and 3 on and cell 2 on; cell 2 sees
    # units 2 and 3, so (2, 3) turns on.
    expected = torch.tensor([[1., 0., 0., 0.],
                             [0., 0., 0., 0.],
                             [0., 0., 0., 1.]])
    assert torch.equal(pp.W, expected)
    # Storing the same pair again leaves every weight at most 1.
    pp.store(E, Y)
    assert torch.equal(pp.W, expected)
    # Recall drive counts potentiated synapses from active EC units.
    assert torch.equal(pp.drive(E), torch.tensor([[1., 0., 0.], [0., 0., 1.]]))


def test_clipped_binary_above_mean_presynaptic_by_hand():
    baseline = torch.tensor([0.6, 0.1, 0.1, 0.1])
    pp, E, Y = hand_example("willshaw", presynaptic="above-mean", baseline=baseline)
    pp.store(E, Y)
    # Unit 0 at 0.5 is below its mean 0.6, so drawing 0 only has unit 2
    # active, which cell 0 does not see: no synapse of cell 0 turns on.
    expected = torch.tensor([[0., 0., 0., 0.],
                             [0., 0., 0., 0.],
                             [0., 0., 0., 1.]])
    assert torch.equal(pp.W, expected)


def test_covariance_rule_by_hand():
    baseline = torch.tensor([0.1, 0.1, 0.1, 0.1])
    pp, E, Y = hand_example("covariance", baseline=baseline)
    pp.store(E, Y)
    a = 1 / 3  # k / n
    D = E - baseline
    full = (Y - a).T @ D
    expected = full * pp.C.float()
    assert torch.allclose(pp.W, expected)
    # Spot check one synapse by hand: cell 0, unit 0.
    by_hand = (1 - a) * (0.5 - 0.1) + (0 - a) * (0.0 - 0.1)
    assert pp.W[0, 0].item() == pytest.approx(by_hand)
    # Unconnected synapses stay at zero.
    assert pp.W[0, 2].item() == 0.0
    # Recall drive uses the raw, never negative, EC rates.
    assert torch.allclose(pp.drive(E), E @ pp.W.T)


def test_covariance_needs_a_baseline():
    with pytest.raises(ValueError):
        PerforantPath(ec_dim=4, n=3, k=1, rule="covariance")


def test_normalised_drive_divides_by_each_cells_active_input():
    pp, E, Y = hand_example("willshaw", normalise=True)
    pp.store(E, Y)
    # Cell 0 sees units 0 and 1; drawing 0 has only unit 0 of those on.
    d = pp.drive(E)
    assert d[0, 0].item() == pytest.approx(1.0)
    # A cell with no active input gets drive 0, not a division by zero.
    assert torch.isfinite(d).all()


def test_top_k_cue_has_k_cells():
    torch.manual_seed(0)
    pp = PerforantPath(ec_dim=50, n=20, k=4, rule="willshaw", share=0.5, seed=1)
    E = (torch.rand(6, 50) < 0.3).float()
    Y = modules.kwta(torch.rand(6, 20), 4)
    pp.store(E, Y)
    cue = pp.cue(E)
    assert torch.all(cue.sum(dim=1) == 4)
    assert torch.all((cue == 0) | (cue == 1))


def test_emax_threshold_can_give_fewer_than_k_cells():
    pp = PerforantPath(ec_dim=4, n=6, k=3, rule="willshaw", share=1.0, emax=0.2)
    drive = torch.tensor([[10., 9., 5., 4., 0., 0.],
                          [10., 10., 10., 10., 1., 0.]])
    cue = pp.select(drive)
    # Row 0: within 20% of the maximum means at least 8: cells 0 and 1.
    assert cue[0].tolist() == [1., 1., 0., 0., 0., 0.]
    # Row 1: four cells tie at the maximum; the cap keeps exactly k.
    assert cue[1].sum().item() == 3
    assert cue[1, 4].item() == 0 and cue[1, 5].item() == 0
    # Without emax the same drive gives k cells.
    plain = PerforantPath(ec_dim=4, n=6, k=3, rule="willshaw", share=1.0)
    assert torch.all(plain.select(drive).sum(dim=1) == 3)


def test_emax_works_for_negative_drive():
    pp = PerforantPath(ec_dim=4, n=4, k=2, rule="willshaw", share=1.0, emax=0.5)
    drive = torch.tensor([[-1.0, -1.4, -3.0, -10.0]])
    # Threshold max - E |max| = -1.5: cells 0 and 1.
    assert pp.select(drive)[0].tolist() == [1., 1., 0., 0.]


def test_partial_cue_settles_onto_the_stored_pattern():
    # A cue with fewer than k cells reaches CA3 as it is (start="cue") and
    # the recurrent weights complete it.
    n, k = 225, 5
    g = torch.Generator().manual_seed(0)
    X = torch.stack([modules.kwta(torch.rand(1, n, generator=g), k)[0] for _ in range(8)])
    for rule in ("covariance", "willshaw"):
        ca3 = modules.CA3(n, k=k, start="cue")
        ca3.train(X, rule)
        partial = X.clone()
        for row in partial:
            on = row.nonzero().flatten()
            row[on[:2]] = 0.0  # 3 of 5 cells left
        assert torch.all(partial.sum(dim=1) == 3)
        settled = ca3.update(partial)
        assert torch.equal(settled, X), rule


def test_parameter_list_counts_every_free_setting():
    params = modules.perforant_parameters()
    names = [p["name"] for p in params]
    assert len(names) == len(set(names))
    assert {"connection_share", "presynaptic", "normalise", "emax"} <= set(names)
    for p in params:
        assert p["source"] in ("chosen", "taken", "structural")
    chosen = [p["name"] for p in params if p["source"] == "chosen"]
    assert sorted(chosen) == ["emax", "normalise", "presynaptic"]
