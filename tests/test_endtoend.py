"""Tests for E1c's end-to-end runs: many drawings studied, corrupted copies recalled."""

import pytest
import torch

from trisynapsnet.data import corrupt
from trisynapsnet.eval import endtoend
from trisynapsnet.model import modules
from trisynapsnet.model.aha import AHA, AHAConfig


def test_runs_per_seed_keep_about_400_items():
    assert [endtoend.runs_per_seed(n) for n in (20, 100, 200)] == [20, 4, 2]


def test_build_run_tests_the_same_drawings_in_another_order():
    images = torch.rand(50, 1, 52, 52)
    run = endtoend.build_run(images, 20, seed=0, run=3)
    assert run["study"].shape == (20, 1, 52, 52)
    assert sorted(run["labels"].tolist()) == list(range(20))
    assert torch.equal(run["recall"], run["study"][run["labels"]])
    assert len(set(run["characters"])) == 20
    for i, c in enumerate(run["characters"]):
        assert torch.equal(run["study"][i], images[c])
    again = endtoend.build_run(images, 20, seed=0, run=3)
    other = endtoend.build_run(images, 20, seed=0, run=4)
    assert again["characters"] == run["characters"]
    assert other["characters"] != run["characters"]


def _tiny(rule):
    torch.manual_seed(0)
    vc = modules.EC(interest_filter=False)
    return AHA(vc, AHAConfig(ca3_rule=rule, pr_hidden=64, study_steps=20),
               device=torch.device("cpu"))


@pytest.mark.parametrize("rule", ["pinverse", "covariance"])
def test_evaluate_rule_scores_every_stage_both_ways(rule):
    g = torch.Generator().manual_seed(0)
    images = (torch.rand(30, 1, 52, 52, generator=g) > 0.9).float()
    runs = [endtoend.build_run(images, 10, seed=0, run=r) for r in range(2)]
    levels = [(level, [corrupt.corrupt(run["recall"], "noise", level, 0, r)
                       for r, run in enumerate(runs)]) for level in (0.0, 0.5)]
    out = endtoend.evaluate_rule(_tiny(rule), runs, levels, seed=0)
    assert len(out) == 2
    stages = endtoend.STAGES if rule == "covariance" else \
        [s for s in endtoend.STAGES if not s.endswith("_cue")]
    for scores in out:
        for stage in stages:
            for direction in endtoend.DIRECTIONS:
                assert 0.0 <= scores["{} {}".format(stage, direction)] <= 1.0
        for name in endtoend.CA3_METRICS:
            assert 0.0 <= scores[name] <= 1.0
        assert scores["recall_loss"] > 0 and scores["recall_loss_none"] > 0
    assert ("pc_cue test-to-study" in out[0]) == (rule == "covariance")
    # Clean drawings: PR's top cells already are the stored pattern for
    # most items, and a local rule leaves a stored pattern where it is.
    if rule == "covariance":
        assert out[0]["overlap_start"] > 0.5


def test_out_path_names():
    assert endtoend.out_path("results", "evaluation", "willshaw", 100, "noise").name == \
        "e1c_e2e_evaluation_willshaw_225_10_n100_noise.json"
