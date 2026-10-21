"""E1d runs DG and CA3 with as few as 3 active cells. These tests check that
k-winners-take-all, DG's inhibition and knockout, damage and every CA3
rule still behave at that size."""

import pytest
import torch

from trisynapsnet.eval import ca3space
from trisynapsnet.model import modules
from trisynapsnet.model.aha import AHA, AHAConfig


@pytest.mark.parametrize("k", [3, 4, 5])
def test_kwta_keeps_exactly_k_even_with_ties(k):
    x = torch.zeros(4, 225)
    x[0, :10] = 1.0               # ten-way tie for k places
    x[1] = torch.rand(225)
    x[2, 7] = 5.0                 # one clear winner, the rest tied at zero
    x[3] = -torch.rand(225)       # every input negative
    out = modules.kwta(x, k)
    assert torch.all(out.sum(dim=1) == k)
    assert set(out.unique().tolist()) == {0.0, 1.0}
    assert out[0, :10].sum() == k
    assert out[2, 7] == 1.0
    assert torch.equal(out[1].nonzero().flatten().sort().values,
                       x[1].topk(k).indices.sort().values)


@pytest.mark.parametrize("n,k", [(225, 3), (225, 5), (1000, 10), (4000, 24)])
def test_dg_gives_k_cells_and_inhibition_spreads_them(n, k):
    torch.manual_seed(0)
    dg = modules.DG(64, n, k)
    weights = dg.fc1.weight
    assert abs((weights == 0).float().mean().item() - 0.25) < 0.02
    dg.reset()
    vc = torch.rand(60, 64, generator=torch.Generator().manual_seed(1))
    X = dg(vc)
    assert torch.all(X.sum(dim=1) == k)
    # A cell that just fired sits out the next drawing.
    assert ((X[:-1] * X[1:]).sum(dim=1) == 0).all()
    # Without inhibition the same drawing always gives the same cells, and
    # with it a repeat lands on new cells.
    dg.reset()
    again = dg(vc[:1].repeat(3, 1))
    assert (again[0] * again[1]).sum() == 0


def test_damage_at_three_cells_rounds_shares_half_up():
    X = ca3space.random_patterns(40, 225, 3, torch.Generator().manual_seed(0))
    expected = {0.2: 1, 0.4: 1, 0.6: 2, 0.8: 2}
    for share, removed in expected.items():
        cue = ca3space.damage(X, share, 0.0, torch.Generator().manual_seed(2))
        assert torch.all(((X > 0) & (cue == 0)).sum(dim=1) == removed)
    strays = {0.25: 1, 0.5: 2, 1.0: 3}
    for share, added in strays.items():
        cue = ca3space.damage(X, 0.0, share, torch.Generator().manual_seed(3))
        assert torch.all(((X == 0) & (cue > 0)).sum(dim=1) == added)


@pytest.mark.parametrize("rule", ca3space.RULES)
@pytest.mark.parametrize("n,k", [(225, 3), (225, 5), (1000, 10)])
def test_every_rule_recalls_a_light_load_at_small_k(rule, n, k):
    X = ca3space.random_patterns(20, n, k, torch.Generator().manual_seed(0))
    rows = ca3space.run_load(rule, X, ("small k", n, k))
    clean = rows[0]["scores"]
    assert clean["exact"] == 1.0 and clean["fixed"] == 1.0 and clean["on_stored"] == 1.0
    assert clean["active_final"] == k


@pytest.mark.parametrize("rule", modules.LOCAL_RULES)
def test_local_rules_complete_a_single_remaining_cell(rule):
    # At k = 3, removing 60% leaves one cell. With few patterns stored, that
    # cell's partners are the rest of its pattern.
    X = ca3space.random_patterns(10, 225, 3, torch.Generator().manual_seed(4))
    if (X.sum(dim=0) > 1).any():
        X = X[:5]
    ca3 = ca3space.build_ca3(rule, 225, 3)
    ca3.train(X, method=rule)
    cue = ca3space.damage(X, 0.6, 0.0, torch.Generator().manual_seed(5))
    assert torch.all(cue.sum(dim=1) == 1)
    state, _ = ca3.settle(cue)
    assert torch.equal(state, X)


@pytest.mark.parametrize("rule", ["covariance", "willshaw", "pinverse"])
def test_full_model_runs_at_small_k(rule):
    torch.manual_seed(0)
    vc = modules.EC(interest_filter=False)
    aha = AHA(vc, AHAConfig(ca3_rule=rule, dg_k=5, pr_hidden=32, study_steps=3),
              device=torch.device("cpu"))
    aha.reset(seed=0)
    g = torch.Generator().manual_seed(0)
    images = (torch.rand(20, 1, 52, 52, generator=g) > 0.9).float()
    study = aha.study(images)
    assert torch.all(study["dg"].sum(dim=1) == 5)
    recall = aha.recall(images)
    assert torch.all((recall["pc"] > 0).sum(dim=1) <= 225)
    if rule != "pinverse":
        assert torch.all((recall["pc"] > 0).sum(dim=1) == 5)
