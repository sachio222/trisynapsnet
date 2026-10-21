"""Tests for E4's CA1 harness: identification, cues and every CA1 arm.

The harness stores N drawings' DG patterns and EC codes in each CA1 arm,
feeds back exact, damaged and settled CA3 states, and scores the returned
code against the right drawing's.
"""

import json
from pathlib import Path

import pytest
import torch

from trisynapsnet.eval import ca1space, ca3space

REPO = Path(__file__).resolve().parents[1]


def test_identify_scores_nearest_by_cosine_and_splits_ties():
    refs = torch.tensor([[1., 0.], [0., 1.], [1., 1.]])
    out = torch.tensor([[2., 0.1], [0., 0.], [0.1, 3.]])
    credit = ca1space.identify(out, refs, torch.tensor([0, 1, 2]))
    assert credit[0] == 1.0
    assert credit[1] == pytest.approx(1 / 3)    # all-zero output ties everything
    assert credit[2] == 0.0


def test_ca1_sizes_follow_the_measured_ratios():
    assert ca1space.ca1_units(225, "human") == 2118
    assert ca1space.ca1_units(225, "rat") == 375
    assert ca1space.ca1_units(1000, "human") == 9412
    assert ca1space.ca1_units(1000, "rat") == 1667


def test_active_cells_is_a_parameter():
    assert ca1space.active_cells(225, 0.044) == 10
    assert ca1space.active_cells(1000, 0.044) == 44
    assert ca1space.active_cells(1000, 0.02) == 20
    assert ca1space.active_cells(225, 0.02) == 4


def _toy(p=30, n=225, k=10, d=400):
    g = torch.Generator().manual_seed(0)
    X = ca3space.random_patterns(p, n, k, g)
    E = torch.rand(p, d, generator=g) * (torch.rand(p, d, generator=g) < 0.1)
    images = (torch.rand(p, 1, 52, 52, generator=g) < 0.1).float()
    return X, E, images


def test_run_load_scores_every_arm_and_input():
    X, E, images = _toy()
    res = ca1space.run_load(X, E, images, 225, ("toy", 0), [0.005], ["human", "rat"],
                            baseline=E.mean(dim=0), ec_scale=10.0)
    arms = set(res["scores"])
    assert arms == {"btsp_human", "btsp_rat", "backprop_ec", "backprop_ec_scaled",
                    "backprop_ec_nol2", "pm_pixels", "pm_pixels_nol2", "mean"}
    inputs = set(res["scores"]["btsp_human"])
    assert "exact" in inputs and "cue 0.4 0" in inputs and "covariance 0.4 0 settled" in inputs
    assert len(inputs) == 1 + 8 + 2 * 8
    for arm in arms:
        for inp in inputs:
            s = res["scores"][arm][inp]
            assert 0.0 <= s["ident"] <= 1.0 and -1.0 <= s["cos"] <= 1.0 + 1e-6
    # Below CA3's capacity the settled states are the stored patterns.
    assert res["ca3_exact"]["covariance 0.4 0 settled"] == 1.0
    assert res["cost"]["btsp_human"]["presentations"] == 30
    # BTSP returns the right drawing from its exact pattern at this load.
    assert res["scores"]["btsp_human"]["exact"]["ident"] > 0.9
    # The no-memory arm is at chance.
    assert res["scores"]["mean"]["exact"]["ident"] == pytest.approx(1 / 30)


def test_pm_pixels_is_e1cs_ca1():
    X, E, images = _toy()
    parts = ("toy", 0)
    arms, _, _ = ca1space.build_arms(X, E, images, 225, parts, [0.005], ["rat"])
    pm = ca3space.train_ca1(X, images, ca3space.derive("ca1", *parts))
    with torch.no_grad():
        assert torch.equal(arms["pm_pixels"](X), pm(X).flatten(1))


@pytest.mark.skipif(not (REPO / "data" / "cache" / "e1c_vc_evaluation_draw0.pt").is_file(),
                    reason="needs E1c's cached evaluation vision codes")
def test_pm_pixels_reproduces_e1c_ca1_floor():
    """E1c's CA1 error from the exact stored pattern, 20 drawings, seed 0."""
    stored = json.loads((REPO / "results" / "e1c_ca3_drawings_evaluation_covariance_225_10.json")
                        .read_text())
    row = [r for r in stored["rows"] if r["load"] == 20 and r["remove"] == 0 and r["add"] == 0][0]
    expected = row["per_seed"]["ca1_target"][0]
    data = ca1space.load_split("evaluation", REPO / "data" / "cache")
    pool, order = ca3space.drawing_patterns(data["vc"], 225, 10, 0)
    parts = ("drawings", "evaluation", 225, 10, 20, 0)
    res = ca1space.run_load(pool[:20], data["vc"][order][:20], data["images"][order][:20], 225,
                            parts, [0.005], ["rat"], rules=("covariance",))
    assert res["scores"]["pm_pixels"]["exact"]["mse"] == pytest.approx(expected, rel=1e-4)
