"""E8's table script: scoring a result file and the prediction checks."""

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "make_e8_table.py"


def load_script():
    spec = importlib.util.spec_from_file_location("make_e8_table", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fake_record():
    # Per seed: 2 repeats, 2 lures, 2 foils.
    def seed(shift):
        return {"types": [0, 0, 1, 1, 2, 2], "similarity": [1.0, 1.0, 0.7, 0.4, None, None],
                "signal": {"intact": [0.99, 0.95, 0.8, 0.3, 0.2, 0.6 + shift],
                           "vc_baseline": [1.0, 1.0, 0.7, 0.4, 0.3, 0.35]},
                "ca3": {"intact": {"cue_cells": [5] * 6, "exact_paired": [1, 1, 1, 0, 0, 0],
                                   "exact_any": [1, 1, 1, 0, 1, 0]}}}
    return {"args": {"arms": ["intact", "vc_baseline"]},
            "per_seed": {"0": seed(0.0), "1": seed(0.3)}}


def test_scores_use_the_intact_thresholds_and_bins():
    m = load_script()
    cal = {"thresholds": {"intact": {"old": 0.9, "q_old": 0.0, "new": 0.5, "q_new": 0.0},
                          "vc_baseline": {"old": 1.0, "q_old": 1.0, "new": 0.32, "q_new": 0.0}},
           "bin_edges": [0.45, 0.5, 0.6, 0.65]}
    s = m.score_record(fake_record(), cal)
    intact = s["intact"]
    # Seed 0: lures 0.8 (similar) and 0.3 (new); foils 0.2 (new), 0.6 (similar).
    # Seed 1: second foil 0.9 sits at the old threshold, not above it, so similar.
    assert intact["rates lure similar"]["values"] == [0.5, 0.5]
    assert intact["rates foil similar"]["values"] == [0.5, 0.5]
    assert intact["ldi"]["mean"] == pytest.approx(0.0)
    assert intact["rec"]["mean"] == pytest.approx(1.0)
    # The 0.7 lure is in L1, the 0.4 lure in L5.
    assert intact["sim_bins 1"]["mean"] == pytest.approx(1.0)
    assert intact["sim_bins 5"]["mean"] == pytest.approx(0.0)
    assert intact["ca3 lure_exact"]["mean"] == pytest.approx(0.5)
    assert intact["ca3 foil_any"]["mean"] == pytest.approx(0.5)
    # The baseline keeps its own thresholds: every repeat old.
    assert s["vc_baseline"]["rates repeat old"]["mean"] == pytest.approx(1.0)
    # No hippocampus: everything new.
    assert s["no_hippocampus"]["rates repeat new"]["mean"] == 1.0
    assert s["no_hippocampus"]["ldi"]["mean"] == 0.0


def test_young_adult_numbers_match_the_published_table():
    m = load_script()
    assert m.YOUNG["repeat"]["old"] - m.YOUNG["foil"]["old"] == pytest.approx(0.786)
    assert m.YOUNG["lure"]["similar"] - m.YOUNG["foil"]["similar"] == pytest.approx(0.360)
