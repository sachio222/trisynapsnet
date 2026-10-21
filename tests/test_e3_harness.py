"""E3's harness: the PR arms repeat the earlier pipeline exactly."""

import json
import os
from pathlib import Path

import pytest
import torch

from trisynapsnet.eval import oneshot, perforant
from trisynapsnet.model import modules
from trisynapsnet.model.aha import AHA, AHAConfig

REPO = Path(__file__).resolve().parents[1]


def synthetic_runs(n_runs=2, size=8, seed=0):
    g = torch.Generator().manual_seed(seed)
    runs = []
    for _ in range(n_runs):
        study = (torch.rand(size, 1, 52, 52, generator=g) < 0.08).float()
        labels = torch.randperm(size, generator=g)
        recall = study[labels].clone()
        recall[:, :, :10] = 0.0  # a different "drawing": the top rows wiped
        runs.append({"study": study, "recall": recall, "labels": labels})
    return runs


def model(ca1_rule, baseline):
    torch.manual_seed(0)
    vc = modules.EC().eval()
    cfg = AHAConfig(ca3_rule="covariance", dg_k=5, ca1_rule=ca1_rule, study_steps=5,
                    ca1_units=200, ca1_plateau_share=0.02)
    aha = AHA(vc, cfg)
    aha.ca1_baseline = baseline
    return aha


def test_pr_arms_repeat_evaluate():
    runs = synthetic_runs()
    baseline = torch.rand(20449) * 0.01
    seeds = [0, 1]

    # The earlier pipeline: evaluate.py's scoring, with settling and without.
    reference = {}
    for name, iters, ca1 in (("settle", 70, "btsp"), ("none", 0, "btsp"), ("pm", 70, "pm")):
        aha = model(ca1, baseline)
        aha.cfg.ca3_iters = iters
        res = oneshot.evaluate(aha, runs, seeds, normalise=True, also=("test-to-study",))
        reference[name] = res["accuracy"]

    aha = model("btsp", baseline)
    settings = perforant.default_settings()
    got = {}
    for seed in seeds:
        for i, run in enumerate(runs):
            s = perforant.study_and_score(aha, run["study"], [run["recall"]], run["labels"],
                                          seed * 1000 + i, settings, baseline)[0]
            for key, value in s.items():
                got.setdefault(key, []).append(value)
    mean = {key: [sum(v[j:j + len(runs)]) / len(runs) for j in range(0, len(v), len(runs))]
            for key, v in got.items()}

    for d, suffix in (("study-to-test", ""), ("test-to-study", " test-to-study")):
        assert mean["pr_cov ca3 " + d] == pytest.approx(reference["settle"]["pc" + suffix])
        assert mean["pr_cov ca1 " + d] == pytest.approx(reference["settle"]["pm" + suffix])
        assert mean["pr_none ca3 " + d] == pytest.approx(reference["none"]["pc" + suffix])
        assert mean["pr_none ca1 " + d] == pytest.approx(reference["none"]["pm" + suffix])
        assert mean["pr_cov pm " + d] == pytest.approx(reference["pm"]["pm" + suffix])
        assert mean["pr " + d] == pytest.approx(reference["settle"]["pr" + suffix])


def test_every_arm_and_stage_is_scored():
    runs = synthetic_runs(n_runs=1)
    baseline = torch.rand(20449) * 0.01
    aha = model("btsp", baseline)
    s = perforant.study_and_score(aha, runs[0]["study"], [runs[0]["recall"]] * 2,
                                  runs[0]["labels"], 0, perforant.default_settings(), baseline)
    assert len(s) == 2
    for arm in perforant.ARMS:
        for stage in perforant.STAGES:
            for d in perforant.DIRECTIONS:
                assert 0.0 <= s[0]["{} {} {}".format(arm, stage, d)] <= 1.0
        assert s[0][arm + " active_cue"] <= 5
    # No settling passes the cue on unchanged.
    assert s[0]["pp_cov_none overlap_cue"] == s[0]["pp_cov_none overlap_final"]


def test_grid_names_are_unique_and_complete():
    grid = perforant.grid_settings()
    assert len(grid) == 2 * 2 * 5 + 2 * 5
    assert "wil_pos_raw_kwta" in grid and "cov_norm_e0.2" in grid


def test_driver_resumes_after_the_last_finished_seed(tmp_path, monkeypatch):
    calls = []

    def fake_study(aha, study, tests, labels, seed, settings, baseline, arms=perforant.ARMS):
        calls.append(seed)
        return [{"pr_cov ca3 test-to-study": 0.5, "pp_cov ca3 test-to-study": 0.4,
                 "pp_cov_none ca3 test-to-study": 0.3} for _ in tests]

    runs = synthetic_runs(n_runs=2)
    monkeypatch.setattr(perforant, "study_and_score", fake_study)
    monkeypatch.setattr(perforant, "load_runs", lambda args: runs)
    monkeypatch.setattr(perforant, "load_vc", lambda *a, **k: modules.EC().eval())
    from trisynapsnet.eval import ca1space
    monkeypatch.setattr(ca1space, "background_reference", lambda *a, **k: (torch.zeros(20449), 1.0))
    out = tmp_path / "e3.json"
    perforant.main(["--seeds", "1", "--device", "cpu", "--out", str(out)])
    assert calls == [0, 1]
    record = json.loads(out.read_text())
    assert record["seeds_done"] == [0] and record["complete"]
    # Asking for two seeds runs only the second.
    perforant.main(["--seeds", "2", "--device", "cpu", "--out", str(out)])
    assert calls == [0, 1, 1000, 1001]
    record = json.loads(out.read_text())
    assert record["seeds_done"] == [0, 1]
    assert record["per_seed"][0]["pr_cov ca3 test-to-study"] == [0.5, 0.5]
    assert "/Users/" not in out.read_text()


@pytest.fixture(scope="module")
def first_seed(tmp_path_factory):
    """Seed 0 of Lake's runs through the E3 harness at 5 and 10 active cells."""
    out = {}

    def run(k):
        if k not in out:
            path = tmp_path_factory.mktemp("e3") / "repro_{}.json".format(k)
            perforant.main(["--task", "classification", "--seeds", "1", "--dg-k", str(k),
                            "--out", str(path)])
            out[k] = json.loads(path.read_text())["per_seed"][0]
        return out[k]
    return run


@pytest.mark.skipif(os.environ.get("TSN_SLOW") != "1", reason="minutes on MPS; set TSN_SLOW=1")
@pytest.mark.skipif(not torch.backends.mps.is_available(), reason="earlier runs used MPS")
@pytest.mark.parametrize("name,k,arm,stage,key", [
    ("e1d_e2e_classification_official_covariance_225_5", 5, "pr_cov", "ca3", "pc"),
    ("e1d_e2e_classification_official_covariance_225_5_it0", 5, "pr_none", "ca3", "pc"),
    ("e1d_e2e_classification_official_covariance_225_5", 5, "pr_cov", "pm", "pm"),
    ("e4_classification_official_covariance_225_10_btsp_human", 10, "pr_cov", "ca1", "pm"),
    ("e4_classification_official_covariance_225_10_btsp_human", 10, "pr_cov", "ca3", "pc"),
])
def test_defaults_reproduce_earlier_numbers(first_seed, name, k, arm, stage, key):
    path = REPO / "results" / (name + ".json")
    if not path.is_file():
        pytest.skip("missing {}".format(path.name))
    want = json.loads(path.read_text())["per_seed"]["accuracy"][key][0]
    got = first_seed(k)["{} {} study-to-test".format(arm, stage)][0]
    assert got == pytest.approx(want, abs=1e-9)


def test_driver_refuses_to_resume_with_other_settings(tmp_path, monkeypatch):
    out = tmp_path / "e3.json"
    args = perforant.build_parser().parse_args(["--out", str(out), "--dg-k", "10"])
    out.write_text(json.dumps({"args": perforant.recorded_args(args), "seeds_done": [0]}))
    with pytest.raises(SystemExit):
        perforant.main(["--out", str(out), "--dg-k", "5", "--device", "cpu"])


def test_grid_scores_every_setting_without_study():
    runs = synthetic_runs(n_runs=1)
    baseline = torch.rand(20449) * 0.01
    aha = model("btsp", baseline)
    grid = perforant.grid_settings()
    s = perforant.grid_score(aha, runs[0]["study"], [runs[0]["recall"]], runs[0]["labels"], 0,
                             baseline, grid)[0]
    for name in grid:
        for arm in ("none", "settle"):
            for d in perforant.DIRECTIONS:
                assert 0.0 <= s["{} {} {}".format(name, arm, d)] <= 1.0
    # Settings that differ only in recall share stored weights, so k-WTA cues
    # with raw drive agree between the grid and the full harness.
    full = perforant.study_and_score(aha, runs[0]["study"], [runs[0]["recall"]],
                                     runs[0]["labels"], 0, perforant.default_settings(),
                                     baseline)[0]
    for d in perforant.DIRECTIONS:
        assert s["cov_raw_kwta none " + d] == full["pp_cov_none ca3 " + d]
        assert s["wil_pos_raw_kwta settle " + d] == full["pp_wil ca3 " + d]


def test_share_option_reaches_the_perforant_path():
    args = perforant.build_parser().parse_args(["--pp-share", "1"])
    settings = perforant.settings_from(args)
    pp = modules.PerforantPath(20449, 225, 5, "willshaw", **settings["willshaw"])
    assert pp.in_degree == 20449
    default = perforant.settings_from(perforant.build_parser().parse_args([]))
    pp = modules.PerforantPath(20449, 225, 5, "willshaw", **default["willshaw"])
    assert pp.in_degree == 710
