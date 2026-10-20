"""Tests for the local learning rules in CA3 and the validation runs.

AHA's CA3 stores patterns with the pseudo-inverse rule, which needs the
whole weight matrix at once. The covariance rule (Tsodyks and Feigel'man
1988) and Willshaw's binary synapses (Willshaw et al. 1969) only use the two
neurons on each side of a synapse. Both store sparse 0/1 patterns and recall
with k-winners-take-all (k-WTA), a stand-in for feedback inhibition.
"""

import pytest
import torch

from fh.data import omniglot
from fh.eval import evaluate, oneshot
from fh.model import modules
from fh.model.aha import AHA, AHAConfig

N, K, P = 225, 10, 20


def sparse_patterns_and_shifted_cues(n=N, k=K, p=P, moved=3, seed=0):
    """p random patterns with k of n units on, and a cue for each with
    `moved` of its active units switched off and the same number of
    inactive units switched on."""
    g = torch.Generator().manual_seed(seed)
    X = torch.zeros(p, n)
    cue = torch.zeros(p, n)
    for i in range(p):
        perm = torch.randperm(n, generator=g)
        X[i, perm[:k]] = 1.0
        cue[i, perm[:k - moved]] = 1.0
        cue[i, perm[k:k + moved]] = 1.0
    return X, cue


def exact_and_overlap(state, X, k=K):
    on, stored = state > 0, X > 0
    exact = (on == stored).all(dim=1).float().mean().item()
    overlap = ((on & stored).sum(dim=1).float() / k).mean().item()
    return exact, overlap


def test_kwta_keeps_exactly_k_active():
    torch.manual_seed(0)
    x = torch.rand(7, 225)
    out = modules.kwta(x, 10)
    assert torch.all(out.sum(dim=1) == 10)
    assert set(out.unique().tolist()) <= {0.0, 1.0}
    # The winners are the k largest inputs.
    assert torch.equal(out.bool(), x >= x.topk(10, dim=1).values[:, -1:])


@pytest.mark.parametrize("rule", ["covariance", "willshaw"])
def test_local_rule_recalls_sparse_patterns_from_shifted_cues(rule):
    X, cue = sparse_patterns_and_shifted_cues()
    ca3 = modules.CA3(N, k=K)
    ca3.train(X, method=rule)
    out = ca3.update(cue)
    assert torch.all(out.sum(dim=1) == K)
    exact, overlap = exact_and_overlap(out, X)
    assert exact >= 0.95
    assert overlap >= 0.99


def test_bipolar_hebbian_fails_on_the_same_task():
    # The existing Hebbian rule on -1/+1 copies of the same patterns. Every
    # pattern shares about 205 minus-ones, so the weights mostly store that
    # common part and the net falls into the all-off state.
    X, cue = sparse_patterns_and_shifted_cues()
    ca3 = modules.CA3(N)
    ca3.train(modules.condition_memorise(X), method="hebbian")
    out = ca3.update(modules.condition_memorise(cue), generator=torch.Generator().manual_seed(0))
    exact, overlap = exact_and_overlap(out, X)
    assert exact <= 0.2
    assert overlap <= 0.5


def test_covariance_weights_match_the_formula():
    X, _ = sparse_patterns_and_shifted_cues()
    ca3 = modules.CA3(N, k=K)
    ca3.train(X, method="covariance")
    a = K / N
    W = (X - a).T @ (X - a) / N
    W.fill_diagonal_(0)
    assert torch.allclose(ca3.W, W, atol=1e-6)


def test_willshaw_weights_are_binary_with_zero_diagonal():
    X, _ = sparse_patterns_and_shifted_cues()
    ca3 = modules.CA3(N, k=K)
    ca3.train(X, method="willshaw")
    assert set(ca3.W.unique().tolist()) == {0.0, 1.0}
    assert torch.all(ca3.W.diagonal() == 0)
    assert ca3.W[X[0].bool()][:, X[0].bool()].sum() == K * (K - 1)


def test_local_rules_refuse_bipolar_patterns():
    X, _ = sparse_patterns_and_shifted_cues()
    ca3 = modules.CA3(N, k=K)
    with pytest.raises(ValueError):
        ca3.train(modules.condition_memorise(X), method="covariance")


def test_cue_weight_holds_recall_near_a_strong_cue():
    # With a huge cue weight the recurrent input can't outvote the cue, so
    # the settled state is the k-WTA of the cue itself.
    X, cue = sparse_patterns_and_shifted_cues()
    ca3 = modules.CA3(N, k=K, cue_weight=1000.0)
    ca3.train(X, method="covariance")
    assert torch.equal(ca3.update(cue), modules.kwta(cue, K))


def _random_images(seed):
    g = torch.Generator().manual_seed(seed)
    return (torch.rand(20, 1, 52, 52, generator=g) > 0.9).float()


@pytest.mark.parametrize("rule", ["covariance", "willshaw"])
def test_aha_with_a_local_rule_stores_dg_and_recalls_k_sparse_states(rule):
    torch.manual_seed(0)
    images = _random_images(0)
    vc = modules.EC(interest_filter=False)
    aha = AHA(vc, AHAConfig(ca3_rule=rule), device=torch.device("cpu"))
    aha.reset(seed=0)
    study = aha.study(images)
    assert torch.equal(study["pc"], study["dg"])
    recall = aha.recall(images)
    assert torch.all(recall["pc"].sum(dim=1) == aha.cfg.dg_k)
    labels = torch.arange(20)
    assert oneshot.run_accuracy(study["pc"], recall["pc"], labels) >= 0.9

    self_recall = aha.self_recall(study)
    assert self_recall["exact"] >= 0.9
    assert 0.9 <= self_recall["overlap"] <= 1.0


def test_dg_overlap_is_one_for_identical_drawings_without_inhibition():
    torch.manual_seed(0)
    images = _random_images(0)
    vc = modules.EC(interest_filter=False)
    aha = AHA(vc, AHAConfig(pr_hidden=64, study_steps=2), device=torch.device("cpu"))
    aha.reset(seed=0)
    study = aha.study(images)
    recall = aha.recall(images)
    overlap = aha.dg_overlap(study, recall, torch.arange(20))
    assert overlap["same"] == pytest.approx(1.0)
    assert 0.0 <= overlap["diff"] < 0.5
    assert set(overlap) >= {"same", "diff", "same_inhibited", "diff_inhibited"}


# The pinverse and hebbian paths must give the same numbers as before the
# local rules went in. These sums came from aha4 at 446d6db on the CPU.
FINGERPRINT = {
    "pinverse": (-4100.0, -4446.38623046875, 4105.78125),
    "hebbian": (-4100.0, -4500.0, 4149.685546875),
}


@pytest.mark.parametrize("rule", ["pinverse", "hebbian"])
def test_bipolar_rules_give_the_same_numbers_as_before(rule):
    torch.manual_seed(0)
    images = (torch.rand(20, 1, 52, 52) > 0.9).float()
    recall_images = (torch.rand(20, 1, 52, 52) > 0.9).float()
    vc = modules.EC(interest_filter=False)
    aha = AHA(vc, AHAConfig(ca3_rule=rule, pr_hidden=64, study_steps=5),
              device=torch.device("cpu"))
    aha.reset(seed=3)
    study = aha.study(images)
    recall = aha.recall(recall_images)
    study_pc, recall_pc, recall_pm = FINGERPRINT[rule]
    assert study["pc"].sum().item() == study_pc
    assert recall["pc"].sum().item() == pytest.approx(recall_pc, rel=1e-6)
    assert recall["pm"].sum().item() == pytest.approx(recall_pm, rel=1e-6)


needs_background = pytest.mark.skipif(
    not (omniglot.DEFAULT_DATA / "omniglot-py" / "images_background").is_dir(),
    reason="Omniglot background set not downloaded")


@needs_background
def test_validation_runs_follow_lakes_structure():
    runs = omniglot.load_background_runs(seed=0)
    assert len(runs) == 20
    alphabets = []
    for run in runs:
        assert run["study"].shape == (20, 1, 52, 52)
        assert run["recall"].shape == (20, 1, 52, 52)
        assert sorted(run["labels"].tolist()) == list(range(20))
        info = run["info"]
        alphabets.append(info["alphabet"])
        assert len(set(info["characters"])) == 20
        assert info["study_drawer"] != info["test_drawer"]
    # Each run comes from its own alphabet.
    assert len(set(alphabets)) == 20


@needs_background
def test_validation_runs_repeat_from_a_seed():
    a = omniglot.load_background_runs(seed=0)
    b = omniglot.load_background_runs(seed=0)
    c = omniglot.load_background_runs(seed=1)
    assert [r["info"] for r in a] == [r["info"] for r in b]
    assert torch.equal(a[0]["study"], b[0]["study"])
    assert [r["info"] for r in a] != [r["info"] for r in c]


def test_evaluate_accepts_the_new_options():
    args = evaluate.parse_args([
        "--ca3-rule", "willshaw", "--dg-units", "1000", "--dg-k", "44",
        "--ca3-cue-weight", "0.5", "--ca3-iters", "30", "--runs", "background"])
    config = evaluate.build_config(args)
    assert (config.ca3_rule, config.dg_units, config.dg_k) == ("willshaw", 1000, 44)
    assert (config.ca3_cue_weight, config.ca3_iters) == (0.5, 30)
    # Bipolar rules update 20 of 225 neurons a step. Bigger nets update the
    # same share, so each settles over the same number of sweeps.
    assert config.ca3_update == round(20 * 1000 / 225)
    assert evaluate.build_config(evaluate.parse_args([])).ca3_update == 20
