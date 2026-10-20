"""Tests for the E1b table builder in scripts/make_e1b_table.py."""

import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "make_e1b_table.py"
spec = importlib.util.spec_from_file_location("make_e1b_table", SCRIPT)
table = importlib.util.module_from_spec(spec)
spec.loader.exec_module(table)


def fake_result(path, rule, iters, kind, pc_by_level, task="instance", runs="official",
                match="study-to-test"):
    """A results file shaped like evaluate.py's, with two seeds."""
    levels = []
    for level, pcs in pc_by_level.items():
        acc = {stage: [0.5, 0.5] for stage in ("pixels", "vc", "pr", "pm")}
        acc["pc"] = pcs
        levels.append({
            "corruption": kind, "level": level,
            "summary": {s: {"mean": sum(v) / 2, "std": 0.0} for s, v in acc.items()},
            "recall_loss": {"mean": 0.01, "std": 0.0},
            "per_seed": {"level": level, "accuracy": acc, "recall_loss": [0.01, 0.01]},
        })
    record = {"args": {"task": task, "runs": runs, "seeds": 2, "match": match},
              "config": {"ca3_rule": rule, "ca3_iters": iters}, "levels": levels}
    path.write_text(json.dumps(record))


def test_load_names_the_no_settling_control_none(tmp_path):
    fake_result(tmp_path / "e1b_a.json", "covariance", 0, "noise", {0.0: [0.6, 0.7]})
    fake_result(tmp_path / "e1b_b.json", "willshaw", 70, "noise", {0.0: [0.5, 0.5]})
    rows = table.load(tmp_path)
    assert {r["option"] for r in rows} == {"none", "willshaw"}
    assert rows[0]["task"] == "instance" and rows[0]["kind"] == "noise"


def test_settling_gap_is_paired_by_seed(tmp_path):
    fake_result(tmp_path / "e1b_none.json", "covariance", 0, "occlusion",
                {0.0: [0.5, 0.6], 0.5: [0.2, 0.3]})
    fake_result(tmp_path / "e1b_cov.json", "covariance", 70, "occlusion",
                {0.0: [0.4, 0.6], 0.5: [0.3, 0.5]})
    rows = table.load(tmp_path)
    gaps = table.settling_gaps(rows, "instance", "official", "occlusion", "covariance")
    assert [g["level"] for g in gaps] == [0.0, 0.5]
    assert gaps[0]["mean"] == pytest.approx(-0.05)
    assert gaps[1]["mean"] == pytest.approx(0.15)
    assert gaps[1]["wins"] == 2 and gaps[0]["wins"] == 0


def test_matching_directions_stay_apart(tmp_path):
    fake_result(tmp_path / "e1b_none.json", "covariance", 0, "noise", {0.0: [0.5, 0.5]})
    fake_result(tmp_path / "e1b_none_tts.json", "covariance", 0, "noise", {0.0: [0.9, 0.9]},
                match="test-to-study")
    rows = table.load(tmp_path)
    sts = table.find(rows, "instance", "official", "noise", "none")
    tts = table.find(rows, "instance", "official", "noise", "none", match="test-to-study")
    assert sts["levels"][0.0]["summary"]["pc"]["mean"] == 0.5
    assert tts["levels"][0.0]["summary"]["pc"]["mean"] == 0.9
