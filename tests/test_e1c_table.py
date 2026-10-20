"""Tests for the E1c table builder in scripts/make_e1c_table.py."""

import importlib.util
import json
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "make_e1c_table.py"
spec = importlib.util.spec_from_file_location("make_e1c_table", SCRIPT)
table = importlib.util.module_from_spec(spec)
spec.loader.exec_module(table)


def fake_ca3(path, rule, units, k, exact_by_load, source="random", split=None):
    """A harness results file with two seeds and two damage conditions."""
    rows = []
    for load, (clean, half) in exact_by_load.items():
        for (remove, add), exact in (((0.0, 0.0), clean), ((0.4, 0.0), half)):
            per_seed = {"exact": [exact, exact], "overlap_cue": [1 - remove] * 2,
                        "overlap_final": [1.0, 1.0], "stray_cue": [0.0, 0.0],
                        "stray_final": [0.0, 0.0], "ident_cue": [1.0, 1.0],
                        "ident_final": [1.0, 1.0], "on_stored": [1.0, 1.0],
                        "active_final": [k, k], "iterations": [1, 1], "fixed": [1, 1]}
            rows.append({"load": load, "remove": remove, "add": add, "cues": 20,
                         "duplicates": [0, 0], "per_seed": per_seed})
    record = {"source": source, "split": split, "rule": rule, "units": units, "k": k,
              "seeds": [0, 1], "notes": ["a note"], "rows": rows}
    path.write_text(json.dumps(record))


def test_capacity_is_the_last_load_before_recall_drops(tmp_path):
    fake_ca3(tmp_path / "e1c_ca3_random_covariance_225_10.json", "covariance", 225, 10,
             {20: (1.0, 1.0), 50: (0.97, 0.9), 100: (0.5, 0.2), 200: (0.99, 0.0)})
    ca3 = table.load_ca3(tmp_path)
    assert table.capacity(ca3, "random", "covariance", 225, table.CLEAN) == 50
    assert table.capacity(ca3, "random", "covariance", 225, table.HALF) == 20


def test_markdown_has_the_headline_sections_and_no_absolute_paths(tmp_path):
    fake_ca3(tmp_path / "e1c_ca3_random_covariance_225_10.json", "covariance", 225, 10,
             {20: (1.0, 1.0), 100: (0.5, 0.2)})
    fake_ca3(tmp_path / "e1c_ca3_random_pinverse_1000_44.json", "pinverse", 1000, 44,
             {20: (1.0, 1.0), 2000: (1.0, 0.0)})
    out = table.write_markdown(table.load_ca3(tmp_path), {}, tmp_path / "e1c.md")
    text = out.read_text()
    assert "## Random patterns: exact recall against load" in text
    assert "2,000 (extension)" in text
    assert "| 225, 10 | 20 | – | 100.0 |" in text
    assert "/Users/" not in text and str(tmp_path) not in text
