"""Tests for E4's CA1: one-shot learning by BTSP, and the Hebbian return to EC.

BTSP is behavioural timescale synaptic plasticity. A plateau potential in a
CA1 cell changes every synapse from a CA3 cell active within a window of
seconds around it. The binary form here is Wu and Maass's (2025, Eq. 1):
with probability 0.5, an active synapse at weight 0 goes to 1 and an
active synapse at weight 1 goes to 0. CA1 then returns the memory to
entorhinal cortex (EC) through synapses that grow with the product of CA1
and EC activity.
"""

import pytest
import torch

from trisynapsnet.model import modules
from trisynapsnet.model.aha import AHA, AHAConfig


def small_ca1(units=3, n_in=4, ec_dim=5, share=1 / 3, connect=1.0, gate=1.0, seed=0):
    return modules.CA1BTSP(n_in, ec_dim, units, plateau_share=share, connect=connect,
                           gate=gate, seed=seed)


def test_btsp_flips_only_active_synapses_of_plateau_cells():
    """Hand-checked example with the gate always open.

    Cell 0 has a plateau. Inputs 0 and 1 are active. Its synapse from input
    0 was at 0 and goes to 1 (potentiation). Its synapse from input 1 was at
    1 and goes to 0 (depression). Inactive inputs and cells without a
    plateau keep their weights.
    """
    ca1 = small_ca1()
    ca1.W = torch.tensor([[0., 1., 0., 1.],
                          [0., 1., 1., 0.],
                          [1., 0., 0., 0.]])
    x = torch.tensor([1., 1., 0., 0.])
    plateau = torch.tensor([1., 0., 0.])
    ca1.btsp(x, plateau)
    assert torch.equal(ca1.W, torch.tensor([[1., 0., 0., 1.],
                                            [0., 1., 1., 0.],
                                            [1., 0., 0., 0.]]))


def test_btsp_skips_synapses_that_do_not_exist():
    ca1 = small_ca1()
    ca1.C = torch.tensor([[True, False, True, True]] * 3)
    ca1.W = torch.zeros(3, 4)
    ca1.btsp(torch.tensor([1., 1., 0., 0.]), torch.tensor([1., 1., 0.]))
    assert torch.equal(ca1.W, torch.tensor([[1., 0., 0., 0.],
                                            [1., 0., 0., 0.],
                                            [0., 0., 0., 0.]]))


def test_btsp_gate_opens_for_about_half_of_eligible_synapses():
    ca1 = modules.CA1BTSP(200, 5, 300, plateau_share=0.5, connect=1.0, gate=0.5, seed=1)
    x = torch.zeros(200)
    x[:100] = 1.0
    plateau = torch.zeros(300)
    plateau[:150] = 1.0
    ca1.btsp(x, plateau)
    changed = ca1.W[:150, :100].mean().item()
    assert 0.45 < changed < 0.55
    # Nothing outside the plateau cells' active synapses changed.
    assert ca1.W[150:].sum() == 0 and ca1.W[:, 100:].sum() == 0
    # A second presentation flips about half again: weights at 1 go to 0.
    before = ca1.W.clone()
    ca1.btsp(x, plateau)
    went_down = ((before == 1) & (ca1.W == 0))[:150, :100].sum().item()
    went_up = ((before == 0) & (ca1.W == 1))[:150, :100].sum().item()
    assert went_down > 0 and went_up > 0


def test_connection_probability_sets_share_of_synapses():
    ca1 = modules.CA1BTSP(225, 5, 2000, plateau_share=0.01, connect=0.6, seed=0)
    assert abs(ca1.C.float().mean().item() - 0.6) < 0.01
    assert torch.all(ca1.W == 0)


def test_plateaus_go_to_the_cells_with_most_ec3_drive():
    ca1 = small_ca1(units=4, share=0.5)
    assert ca1.m == 2
    drive = torch.tensor([[0.1, 0.9, 0.3, 0.8], [0.7, 0.0, 0.6, 0.1]])
    assert torch.equal(ca1.plateaus_from_drive(drive),
                       torch.tensor([[0., 1., 0., 1.], [1., 0., 1., 0.]]))


def test_ec3_drive_is_a_fixed_positive_projection():
    ca1 = modules.CA1BTSP(10, 50, 40, plateau_share=0.1, seed=3)
    E = torch.rand(6, 50)
    d1, d2 = ca1.drive(E), ca1.drive(E)
    assert torch.equal(d1, d2)
    other = modules.CA1BTSP(10, 50, 40, plateau_share=0.1, seed=4)
    assert not torch.equal(d1, other.drive(E))
    # Linear in the EC code, with weights in [0, 1).
    assert torch.allclose(ca1.drive(2 * E), 2 * d1, atol=1e-5)
    unit = torch.eye(50)
    P = ca1.drive(unit)
    assert P.min() >= 0 and P.max() < 1


def test_ec3_baseline_is_subtracted_before_the_projection():
    E = torch.rand(6, 50)
    base = torch.rand(50)
    plain = modules.CA1BTSP(10, 50, 40, plateau_share=0.1, seed=3)
    centred = modules.CA1BTSP(10, 50, 40, plateau_share=0.1, seed=3, ec3_baseline=base)
    assert torch.allclose(centred.drive(E), plain.drive(E - base), atol=1e-5)
    # Same projection: the baseline only shifts each cell by its own mean drive.
    assert torch.allclose(centred.drive(E), plain.drive(E) - plain.drive(base[None]), atol=1e-4)


def test_random_plateaus_ignore_the_ec_code():
    ca1 = modules.CA1BTSP(10, 50, 40, plateau_share=0.1, seed=3, plateau_source="random")
    E = torch.rand(6, 50)
    a, b = ca1.plateaus(E), ca1.plateaus(2 * E + 1)
    assert torch.equal(a, b) and torch.all(a.sum(dim=1) == 4)
    with pytest.raises(ValueError):
        modules.CA1BTSP(10, 50, 40, plateau_source="dopamine")


def test_hebbian_return_sums_ca1_times_ec_products():
    """Hand-checked: R = sum over drawings of outer(CA1 trace, EC code)."""
    ca1 = small_ca1(units=3, ec_dim=2)
    ca1.T = torch.tensor([[1., 0., 0.], [1., 1., 0.]])
    ca1.E = torch.tensor([[0.5, 0.0], [0.0, 2.0]])
    assert torch.equal(ca1.return_weights(), torch.tensor([[0.5, 2.0], [0.0, 2.0], [0.0, 0.0]]))
    # CA1 activity [0, 1, 0] returns row 1 of R.
    assert torch.equal(ca1.reinstate(torch.tensor([[0., 1., 0.]])), torch.tensor([[0.0, 2.0]]))


def test_respond_keeps_m_cells_and_breaks_ties_at_random():
    ca1 = modules.CA1BTSP(6, 3, 100, plateau_share=0.05, connect=1.0, seed=0)
    ca1.W[:10, :3] = 1.0           # cells 0-9 get 3 from the cue below
    ca1.W[10:40, :2] = 1.0         # cells 10-39 get 2
    x = torch.tensor([[1., 1., 1., 0., 0., 0.]])
    a = ca1.respond(x)
    assert a.sum().item() == 5
    assert a[0, :10].sum().item() == 5
    # With only 2 cue cells on, 40 cells tie at the top, and the 5 winners
    # vary from call to call.
    x2 = torch.tensor([[1., 1., 0., 0., 0., 0.]])
    picks = {tuple(ca1.respond(x2).nonzero()[:, 1].tolist()) for _ in range(5)}
    assert len(picks) > 1
    assert all(max(p) < 40 for p in picks)


def test_store_learns_each_drawing_in_one_presentation():
    g = torch.Generator().manual_seed(0)
    n, k, p = 225, 10, 20
    X = torch.zeros(p, n).scatter(1, torch.rand(p, n, generator=g).argsort(1)[:, :k], 1.0)
    E = torch.rand(p, 300, generator=g) * (torch.rand(p, 300, generator=g) < 0.1)
    ca1 = modules.CA1BTSP(n, 300, 2000, plateau_share=0.01, seed=0)
    ca1.store(X, E)
    assert ca1.T.shape == (p, 2000) and torch.all(ca1.T.sum(dim=1) == ca1.m)
    out = ca1(X)
    cos = torch.nn.functional.cosine_similarity(out, E, dim=1)
    sims = torch.nn.functional.normalize(out, dim=1) @ torch.nn.functional.normalize(E, dim=1).T
    assert (sims.argmax(dim=1) == torch.arange(p)).float().mean() >= 0.95
    assert cos.mean() > 0.5
    # Weights stay binary.
    assert set(ca1.W.unique().tolist()) <= {0.0, 1.0}


def test_store_is_repeatable_from_the_seed():
    g = torch.Generator().manual_seed(1)
    X = (torch.rand(8, 50, generator=g) < 0.2).float()
    E = torch.rand(8, 30, generator=g)
    a = modules.CA1BTSP(50, 30, 200, plateau_share=0.05, seed=7)
    b = modules.CA1BTSP(50, 30, 200, plateau_share=0.05, seed=7)
    a.store(X, E)
    b.store(X, E)
    assert torch.equal(a.W, b.W) and torch.equal(a.T, b.T)
    assert torch.equal(a(X), b(X))


def test_free_parameters_are_counted():
    params = modules.btsp_parameters()
    names = [p["name"] for p in params]
    assert len(names) == len(set(names))
    chosen = [p["name"] for p in params if p["source"] == "chosen"]
    taken = [p["name"] for p in params if p["source"] == "taken"]
    assert chosen == ["plateau_share", "ec3_baseline"]
    assert set(taken) == {"connect", "gate", "initial_weight", "ca1_units"}
    for p in params:
        assert p["source"] in ("chosen", "taken", "structural")
        assert p["why"]
    assert len(params) == 10


def test_backprop_baseline_returns_ec_codes():
    net = modules.CA1ToEC(225, 20449, 100)
    out = net(torch.zeros(4, 225))
    assert out.shape == (4, 20449)


def test_btsp_needs_the_background_baseline():
    cfg = AHAConfig(image_size=8, ca1_rule="btsp", ca1_units=300, pr_hidden=20)
    aha = AHA(_VC(), cfg)
    with pytest.raises(ValueError):
        aha.reset(seed=0)
    aha.ca1_baseline = torch.zeros(64)
    aha.reset(seed=0)
    assert aha.ca1.ec3_baseline is not None


def test_default_config_keeps_aha_ca1():
    cfg = AHAConfig()
    assert cfg.ca1_rule == "pm"
    with pytest.raises(ValueError):
        AHAConfig(ca1_rule="nope").check()


class _VC(torch.nn.Module):
    """A stand-in vision network: flattens 8x8 images into 64 numbers."""

    def forward(self, x, k=4):
        return x.flatten(1).clamp_min(0)

    def output_dim(self, image_size):
        return image_size ** 2


@pytest.mark.parametrize("rule", ["btsp", "backprop_ec"])
def test_aha_with_ec_ca1_returns_ec_codes(rule):
    cfg = AHAConfig(image_size=8, ca3_rule="covariance", ca1_rule=rule, ca1_units=300,
                    ca1_plateau_share=0.02, study_steps=5, pr_hidden=20)
    aha = AHA(_VC(), cfg)
    aha.ca1_baseline = torch.full((64,), 0.3)
    aha.reset(seed=0)
    images = (torch.rand(5, 1, 8, 8, generator=torch.Generator().manual_seed(0)) < 0.3).float()
    study = aha.study(images)
    assert study["pm"].shape == (5, 64)
    recall = aha.recall(images)
    assert recall["pm"].shape == (5, 64)


def test_ec_ca1_leaves_ca3_and_pr_unchanged():
    """Swapping CA1 must not change any earlier stage, so CA3-stage scores
    stay comparable across CA1 rules."""
    images = (torch.rand(5, 1, 8, 8, generator=torch.Generator().manual_seed(0)) < 0.3).float()
    out = {}
    for rule in ("pm", "btsp", "backprop_ec"):
        cfg = AHAConfig(image_size=8, ca3_rule="covariance", ca1_rule=rule, ca1_units=300,
                        ca1_plateau_share=0.02, study_steps=5, pr_hidden=20)
        aha = AHA(_VC(), cfg)
        aha.ca1_baseline = torch.full((64,), 0.3)
        aha.reset(seed=0)
        aha.study(images)
        out[rule] = aha.recall(images)
    for rule in ("btsp", "backprop_ec"):
        assert torch.equal(out[rule]["pr"], out["pm"]["pr"])
        assert torch.equal(out[rule]["pc"], out["pm"]["pc"])
