"""Tests for where data lives and how result files name it.

Result files record paths relative to the repo, written as if aha4 sits
next to it (../aha4/...), so no file holds a path from one machine.
"""

import importlib
import json

from trisynapsnet.data import omniglot
from trisynapsnet.eval import evaluate


def test_portable_paths_are_relative_to_the_repo():
    assert omniglot.portable(omniglot.LOCAL_DATA) == "data"
    assert omniglot.portable(omniglot.REPO / "results" / "x.json") == "results/x.json"
    assert omniglot.portable(omniglot.DEFAULT_CHECKPOINT) == \
        "../aha4/checkpoints/vc_pretrained.pth.tar"
    assert omniglot.portable(omniglot.DEFAULT_DATA) == "../aha4/data"
    assert omniglot.portable("results/x.json") == "results/x.json"


def test_aha4_can_live_anywhere(tmp_path, monkeypatch):
    elsewhere = tmp_path / "somewhere" / "aha4"
    monkeypatch.setenv("TSN_AHA4", str(elsewhere))
    moved = importlib.reload(omniglot)
    try:
        assert moved.DEFAULT_DATA == elsewhere / "data"
        assert moved.DEFAULT_CHECKPOINT == elsewhere / "checkpoints" / "vc_pretrained.pth.tar"
        # Recorded as the standard layout, not this machine's folder.
        assert moved.portable(moved.DEFAULT_CHECKPOINT) == \
            "../aha4/checkpoints/vc_pretrained.pth.tar"
        assert moved.portable(elsewhere / "data" / "omniglot-runs") == "../aha4/data/omniglot-runs"
    finally:
        monkeypatch.delenv("TSN_AHA4")
        importlib.reload(omniglot)


def test_evaluate_records_no_absolute_paths(tmp_path):
    args = evaluate.parse_args(["--out", str(omniglot.REPO / "results" / "y.json")])
    recorded = evaluate.recorded_args(args)
    assert recorded["checkpoint"] == "../aha4/checkpoints/vc_pretrained.pth.tar"
    assert recorded["data_dir"] == "../aha4/data"
    assert recorded["eval_data_dir"] == "data"
    assert recorded["out"] == "results/y.json"
    text = json.dumps(recorded)
    assert str(omniglot.REPO) not in text and "/Users/" not in text
