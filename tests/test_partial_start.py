"""Tests for settling from a partial pattern, added for E1c.

Until E1c, CA3's local rules always began settling from the k most active
cells of the cue, so the first state was a full-size pattern even when the
cue held fewer than k active cells. With start="cue", CA3 begins from the
cue as given: the first update is kWTA(W cue + cue_weight cue), and later
updates run as before. The default stays start="kwta", so E1 and E1b
repeat exactly.
"""

import json
import os

import pytest
import torch

from trisynapsnet.data import omniglot
from trisynapsnet.eval import evaluate
from trisynapsnet.model import modules
from trisynapsnet.model.aha import AHA, AHAConfig

N, K, P = 225, 10, 20


def patterns(n=N, k=K, p=P, seed=0):
    g = torch.Generator().manual_seed(seed)
    X = torch.zeros(p, n)
    for i in range(p):
        X[i, torch.randperm(n, generator=g)[:k]] = 1.0
    return X


def old_settle(ca3, cue):
    """The local-rule settling loop exactly as it was before E1c."""
    state = modules.kwta(cue, ca3.k)
    for _ in range(ca3.n_iter):
        new = modules.kwta(state @ ca3.W + ca3.cue_weight * cue, ca3.k)
        if torch.equal(new, state):
            break
        state = new
    return state


def test_default_start_is_the_cue_winners():
    assert modules.CA3(N).start == "kwta"
    assert AHAConfig().ca3_start == "kwta"
    with pytest.raises(ValueError):
        modules.CA3(N, start="nonsense")


@pytest.mark.parametrize("rule", ["covariance", "willshaw"])
@pytest.mark.parametrize("cue_weight", [0.0, 0.5])
def test_default_settling_is_unchanged(rule, cue_weight):
    X = patterns()
    g = torch.Generator().manual_seed(1)
    cue = torch.rand(P, N, generator=g)
    ca3 = modules.CA3(N, k=K, cue_weight=cue_weight)
    ca3.train(X, method=rule)
    assert torch.equal(ca3.update(cue), old_settle(ca3, cue))


@pytest.mark.parametrize("cue_weight", [0.0, 0.7])
def test_cue_start_first_update_uses_the_cue_as_given(cue_weight):
    X = patterns()
    # Keep 4 of each pattern's 10 cells: fewer than k.
    cue = X.clone()
    for i in range(P):
        on = X[i].nonzero().flatten()
        cue[i, on[4:]] = 0.0
    ca3 = modules.CA3(N, k=K, n_iter=1, cue_weight=cue_weight, start="cue")
    ca3.train(X, method="covariance")
    expected = modules.kwta(cue @ ca3.W + cue_weight * cue, K)
    assert torch.equal(ca3.update(cue), expected)


def test_cue_start_with_no_steps_returns_the_cue():
    X = patterns()
    cue = X[:3].clone()
    cue[:, :] = 0.0
    cue[0, 5] = 1.0
    ca3 = modules.CA3(N, k=K, n_iter=0, start="cue")
    ca3.train(X, method="willshaw")
    assert torch.equal(ca3.update(cue), cue)


@pytest.mark.parametrize("rule", ["covariance", "willshaw"])
def test_cue_start_completes_half_patterns(rule):
    X = patterns()
    cue = X.clone()
    for i in range(P):
        cue[i, X[i].nonzero().flatten()[:5]] = 0.0
    ca3 = modules.CA3(N, k=K, start="cue")
    ca3.train(X, method=rule)
    assert torch.equal(ca3.update(cue), X)


def test_settle_reports_steps_and_fixed_points_for_local_rules():
    X = patterns()
    ca3 = modules.CA3(N, k=K, start="cue")
    ca3.train(X, method="covariance")
    state, info = ca3.settle(X)
    # A stored pattern is already a fixed point: no step changes it.
    assert torch.equal(state, X)
    assert info["iterations"].tolist() == [0] * P
    assert info["fixed"].all()

    cue = X.clone()
    cue[:, :] = 0.0
    cue[torch.arange(P), X.argmax(dim=1)] = 1.0     # one cell of each pattern
    state, info = ca3.settle(cue)
    assert (info["iterations"] >= 1).all()
    # settle() and update() agree.
    assert torch.equal(state, ca3.update(cue))


def test_settle_marks_rows_still_moving_as_not_fixed():
    X = patterns()
    ca3 = modules.CA3(N, k=K, n_iter=1, start="cue")
    ca3.train(X, method="covariance")
    cue = X.clone()
    cue[:, :] = 0.0
    cue[torch.arange(P), X.argmax(dim=1)] = 1.0
    _, info = ca3.settle(cue)
    # One step from one cell always changes the state, and there is no
    # step left to show it has stopped.
    assert not info["fixed"].any()
    assert info["iterations"].tolist() == [1] * P


def test_bipolar_settle_matches_update_and_finds_stored_patterns_fixed():
    X = modules.condition_memorise(patterns())
    ca3 = modules.CA3(N)
    ca3.train(X, method="pinverse")
    a, info = ca3.settle(X, generator=torch.Generator().manual_seed(0))
    b = ca3.update(X, generator=torch.Generator().manual_seed(0))
    assert torch.equal(a, b)
    assert torch.equal(a > 0, X > 0)
    assert info["fixed"].all()
    assert info["iterations"].tolist() == [0] * P


def test_aha_passes_the_start_option_to_ca3():
    torch.manual_seed(0)
    vc = modules.EC(interest_filter=False)
    aha = AHA(vc, AHAConfig(ca3_rule="covariance", ca3_start="cue", pr_hidden=16,
                            study_steps=1), device=torch.device("cpu"))
    aha.reset(seed=0)
    assert aha.ca3.start == "cue"


# E1b ran on Apple's MPS backend. Its stored per-seed scores repeat there
# exactly, so with the default start the model must give them again.
E1B_FILE = "results/e1b_instance_official_covariance_225_10_noise.json"


@pytest.mark.skipif(os.environ.get("TSN_SLOW") != "1",
                    reason="takes about half a minute; set TSN_SLOW=1")
@pytest.mark.skipif(not torch.backends.mps.is_available(),
                    reason="E1b's stored numbers came from the MPS backend")
@pytest.mark.skipif(not (omniglot.LOCAL_DATA / "omniglot-py" / "images_evaluation").is_dir(),
                    reason="Omniglot evaluation alphabets not downloaded")
def test_defaults_reproduce_e1b(tmp_path):
    out = tmp_path / "e1b.json"
    evaluate.main(["--normalise", "--task", "instance", "--runs", "official", "--seeds", "1",
                   "--ca3-rule", "covariance", "--noise", "0.3", "--device", "mps",
                   "--out", str(out)])
    new = json.loads(out.read_text())
    old = json.loads((evaluate.REPO / E1B_FILE).read_text())
    level = [lv for lv in old["levels"] if lv["level"] == 0.3][0]["per_seed"]
    assert new["per_seed"]["accuracy"]["pc"][0] == level["accuracy"]["pc"][0]
    assert new["per_seed"]["accuracy"]["pm"][0] == level["accuracy"]["pm"][0]
    assert new["per_seed"]["recall_loss"][0] == level["recall_loss"][0]
