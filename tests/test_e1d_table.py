"""Tests for the E1d table builder in scripts/make_e1d_table.py."""

import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "make_e1d_table.py"
spec = importlib.util.spec_from_file_location("make_e1d_table", SCRIPT)
table = importlib.util.module_from_spec(spec)
spec.loader.exec_module(table)


def fake(path, rule, units, k, exact_by_load, source="random", split=None, sparsity="2"):
    """A harness file with two seeds and two damage conditions."""
    rows = []
    for load, (clean, half) in exact_by_load.items():
        for (remove, add), exact in (((0.0, 0.0), clean), ((0.4, 0.0), half)):
            per_seed = {"exact": [exact, exact], "overlap_cue": [1 - remove] * 2,
                        "overlap_final": [1.0, 1.0], "iterations": [2, 2], "fixed": [1, 1]}
            row = {"load": load, "remove": remove, "add": add, "cues": 20,
                   "duplicates": [0, 0], "usage_cv": [0.4, 0.4], "per_seed": per_seed}
            if source == "drawings":
                row["random_usage_cv"] = [0.2, 0.2]
            rows.append(row)
    record = {"source": source, "split": split, "rule": rule, "units": units, "k": k,
              "sparsity": sparsity, "seeds": [0, 1], "seconds_per_seed": [60, 60],
              "notes": [], "rows": rows, "loads": sorted(exact_by_load)}
    path.write_text(json.dumps(record))


def test_half_load_interpolates_on_a_log_scale(tmp_path):
    fake(tmp_path / "e1d_ca3_random_willshaw_1000_20.json", "willshaw", 1000, 20,
         {100: (1.0, 1.0), 1000: (0.75, 0.5), 10000: (0.25, 0.0)})
    ca3 = table.load_ca3(tmp_path)
    e = table.entry_for(ca3, "random", "willshaw", 1000, "2")
    value, kind = table.half_load(e, table.CLEAN)
    assert kind == "at" and value == pytest.approx(10 ** 3.5)
    # The log-scaled code at 1,000 cells is the same file.
    assert table.entry_for(ca3, "random", "willshaw", 1000, "log") is e
    value, kind = table.half_load(e, table.HALF)
    assert kind == "at" and value == pytest.approx(1000)


def test_half_load_reports_bounds(tmp_path):
    fake(tmp_path / "a.json", "covariance", 225, 5, {20: (1.0, 1.0), 50: (0.9, 0.8)})
    entry = {"rows": {(row["load"], row["remove"], row["add"]): row
                      for row in json.loads((tmp_path / "a.json").read_text())["rows"]}}
    assert table.half_load(entry, table.CLEAN) == (50, "above")
    assert table.format_half(50, "above", 225) == "above 50 (≥ 0.22)"
    assert table.format_half(1000, "at", 1000) == "1,000 (1.00)"


def test_markdown_has_the_headline_sections_and_no_absolute_paths(tmp_path):
    fake(tmp_path / "e1d_ca3_random_willshaw_1000_20.json", "willshaw", 1000, 20,
         {20: (1.0, 1.0), 100: (1.0, 1.0), 1000: (0.75, 0.5), 10000: (0.25, 0.0)})
    fake(tmp_path / "e1d_ca3_random_pinverse_225_5.json", "pinverse", 225, 5,
         {20: (1.0, 1.0), 100: (1.0, 0.2)})
    fake(tmp_path / "e1d_ca3_drawings_evaluation_willshaw_225_5.json", "willshaw", 225, 5,
         {20: (1.0, 1.0), 100: (1.0, 1.0), 659: (0.9, 0.5)}, source="drawings", split="evaluation")
    ca3 = table.load_ca3(tmp_path)
    out = table.write_markdown(ca3, tmp_path / "e1d.md", results_dir=tmp_path)
    text = out.read_text()
    assert "## Random patterns: 50% load and load per cell" in text
    assert "k = 20: 3,162 (3.16)" in text
    assert "### Pseudo-inverse, cues missing 40% of their cells" in text
    assert "| 225 | 2% (rat DG) (k = 5) | 659 | 0.400 | 0.200 | 2.00 |" in text
    assert "/Users/" not in text and str(tmp_path) not in text
