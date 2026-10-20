"""Tests for E1d's harness: CA3 at sparser codes and larger loads.

The harness repeats E1c's CA3 test (trisynapsnet/eval/ca3space.py) with
the share of active cells as a parameter. It keeps patterns as lists of
active cells and stores them as pair counts, so it reaches loads E1c's
dense code could not. Every score must match E1c's code where both run.
"""

import json
import math

import pytest
import torch

from trisynapsnet.eval import ca3space, sparsecodes


def test_active_cells_for_each_share():
    k = sparsecodes.active_cells
    assert [k(n, "4.4")[0] for n in (225, 1000, 4000, 16000)] == [10, 44, 178, 711]
    assert [k(n, "2")[0] for n in (225, 1000, 4000, 16000)] == [5, 20, 80, 320]
    assert [k(n, "1")[0] for n in (225, 1000, 4000, 16000)] == [3, 10, 40, 160]
    assert [k(n, "log")[0] for n in (225, 1000, 4000, 16000)] == [16, 20, 24, 28]
    # 1% of 225 is 2.25 cells; the floor of 3 raises it and says so.
    assert k(225, "1") == (3, True)
    assert k(1000, "1") == (10, False)
    assert sparsecodes.LOG_C == pytest.approx(20 / math.log2(1000))


def test_load_grid_steps_by_at_most_two_thirds():
    grid = sparsecodes.GRID
    assert grid[0] == 20 and grid[-1] == 1_000_000
    assert all(b / a <= 5 / 3 + 1e-9 for a, b in zip(grid, grid[1:]))
    # E1c's loads are all on it.
    assert {20, 50, 100, 150, 200, 300, 500, 700, 1000, 1500, 2000, 3000, 5000,
            10000} <= set(grid)


@pytest.mark.parametrize("n,k", [(225, 10), (1000, 20)])
def test_random_pool_matches_e1c_patterns_in_any_chunks(n, k):
    pool = sparsecodes.RandomPool(n, k, seed=3, chunk_rows=7)
    first = pool.take(30)
    more = pool.take(123)
    dense = ca3space.random_patterns(123, n, k, ca3space.generator("random", n, k, 3))
    assert torch.equal(sparsecodes.dense(more, n), dense)
    assert torch.equal(more[:30], first)


def test_pair_counts_give_e1c_weights():
    n, k = 300, 6
    X = ca3space.random_patterns(500, n, k, torch.Generator().manual_seed(0))
    idx = X.topk(k, dim=1).indices
    counts = sparsecodes.PairCounts(n, chunk_rows=64)
    counts.add(idx[:123])
    counts.add(idx[123:])
    for rule in ("covariance", "willshaw"):
        ca3 = ca3space.build_ca3(rule, n, k)
        ca3.train(X, method=rule)
        W = sparsecodes.weights(counts, rule, k)
        if rule == "willshaw":
            assert torch.equal(W, ca3.W)
        else:
            assert torch.allclose(W, ca3.W, atol=1e-7, rtol=1e-5)


def test_nearest_matches_e1c_lookup_and_stored_check():
    n, k = 120, 5
    g = torch.Generator().manual_seed(1)
    X = ca3space.random_patterns(60, n, k, g)
    X[7] = X[3]  # a duplicate, so ties happen
    idx = X.topk(k, dim=1).indices
    target = torch.tensor([3, 7, 10, 20, 59, 0])
    on = ca3space.damage(X[target], 0.4, 0.4, g) > 0
    on[5] = X[0] > 0               # exactly a stored pattern
    final = X[target] > 0
    final[2, :] = False
    final[2, :k] = True            # some other pattern, maybe not stored
    expected = ca3space.score(on, final, X, target)
    got = sparsecodes.score(on, final, X[target], idx, target, chunk_rows=13)
    assert set(got) == set(expected)
    for name in expected:
        assert torch.allclose(got[name], expected[name]), name


@pytest.mark.parametrize("rule", ca3space.RULES)
@pytest.mark.parametrize("p", [20, 300])
def test_run_load_repeats_e1c_scores(rule, p):
    n, k = 225, 10
    X = ca3space.random_patterns(p, n, k, torch.Generator().manual_seed(2))
    parts = ("random", "-", n, k, p, 0)
    old = ca3space.run_load(rule, X, parts)
    idx = X.topk(k, dim=1).indices
    counts = None
    if rule != "pinverse":
        counts = sparsecodes.PairCounts(n)
        counts.add(idx)
    new = sparsecodes.run_load(rule, idx, n, k, parts, counts=counts)
    assert [(r["remove"], r["add"], r["cues"]) for r in new] == \
        [(r["remove"], r["add"], r["cues"]) for r in old]
    # The covariance weights come out exact here, in float64, where E1c
    # summed them in float32: they differ by about 1e-7. Cells whose pair
    # counts match then tie exactly in k-WTA, where E1c's rounding broke
    # the tie. Past capacity (300 patterns, 36% exact recall) that changes
    # the outcome for up to 3% of cues; below capacity, nothing changes.
    tol = 0.05 if rule == "covariance" and p > 100 else 1e-6
    for a, b in zip(old, new):
        for name, value in a["scores"].items():
            assert b["scores"][name] == pytest.approx(value, abs=tol, rel=tol), (name, a["remove"], a["add"])


def test_usage_cv_of_even_and_uneven_patterns():
    idx = torch.tensor([[0, 1], [2, 3], [0, 1], [2, 3]])
    assert sparsecodes.usage_cv(idx, 4) == pytest.approx(0.0)
    idx = torch.tensor([[0, 1], [0, 2], [0, 3], [0, 1]])
    counts = torch.tensor([4.0, 2.0, 1.0, 1.0])
    assert sparsecodes.usage_cv(idx, 4) == pytest.approx(
        (counts.std(unbiased=False) / counts.mean()).item())


def test_stop_rule():
    def rows(clean, half):
        return [{"remove": 0.0, "add": 0.0, "scores": {"exact": clean}},
                {"remove": 0.4, "add": 0.0, "scores": {"exact": half}}]
    stop = sparsecodes.should_stop
    assert not stop("covariance", 50, rows(0.0, 0.0))      # always run through 100
    assert stop("covariance", 150, rows(0.04, 0.0))
    assert not stop("covariance", 150, rows(0.06, 0.0))
    assert stop("pinverse", 150, rows(1.0, 0.04))
    assert not stop("pinverse", 150, rows(1.0, 0.5))


def test_candidate_loads():
    loads = sparsecodes.candidate_loads
    assert loads("random", "covariance", 225, None)[:3] == [20, 30, 50]
    # The pseudo-inverse stops below the cell count, where its weights
    # become the identity.
    assert max(loads("random", "pinverse", 225, None)) == 200
    # Drawings stop at the characters available, and include that load.
    assert loads("drawings", "willshaw", 1000, 659)[-2:] == [500, 659]
    assert loads("drawings", "pinverse", 225, 659)[-1] == 200


def test_main_writes_a_resumable_record(tmp_path):
    out = tmp_path / "e1d.json"
    argv = ["--source", "random", "--rule", "willshaw", "--units", "225", "--sparsity", "2",
            "--loads", "20", "50", "--out", str(out)]
    sparsecodes.main(argv + ["--seeds", "1"])
    partial = json.loads(out.read_text())
    assert partial["seeds"] == [0] and partial["k"] == 5 and partial["sparsity"] == "2"
    sparsecodes.main(argv + ["--seeds", "2"])
    full = json.loads(out.read_text())
    assert full["seeds"] == [0, 1] and full["complete"]
    assert full["loads"] == [20, 50]
    row = full["rows"][0]
    assert row["load"] == 20 and len(row["per_seed"]["exact"]) == 2
    # Seed 0's numbers did not change when seed 1 was added.
    assert row["per_seed"]["exact"][0] == partial["rows"][0]["per_seed"]["exact"][0]
    assert len(row["usage_cv"]) == 2 and len(row["duplicates"]) == 2
    assert "/Users/" not in out.read_text()


def test_main_picks_loads_on_the_first_seed_and_keeps_them(tmp_path):
    out = tmp_path / "e1d.json"
    sparsecodes.main(["--source", "random", "--rule", "covariance", "--units", "225",
                      "--sparsity", "4.4", "--seeds", "2", "--max-load", "700",
                      "--out", str(out)])
    r = json.loads(out.read_text())
    clean = [row for row in r["rows"] if row["remove"] == 0 and row["add"] == 0]
    assert [row["load"] for row in clean] == r["loads"]
    assert r["loads"][0] == 20 and 100 in r["loads"]
    # E1c: covariance at 225 cells falls to 3.5% exact recall by load 500.
    assert r["loads"][-1] <= 700
    assert all(len(row["per_seed"]["exact"]) == 2 for row in r["rows"])


def test_main_runs_drawings_up_to_the_characters_available(tmp_path, monkeypatch):
    g = torch.Generator().manual_seed(0)
    fake = {"vc": torch.rand(70, 64, generator=g), "images": torch.zeros(70, 1, 52, 52)}
    monkeypatch.setattr(ca3space, "encoded_characters", lambda *a, **kw: fake)
    out = tmp_path / "drawings.json"
    sparsecodes.main(["--source", "drawings", "--split", "background", "--rule", "willshaw",
                      "--units", "225", "--sparsity", "log", "--seeds", "2", "--out", str(out)])
    r = json.loads(out.read_text())
    assert r["k"] == 16 and r["characters_available"] == 70
    assert r["loads"] == [20, 30, 50, 70]
    row = r["rows"][0]
    assert len(row["random_usage_cv"]) == 2 and len(row["usage_cv"]) == 2
    # DG's patterns follow E1c's: the same seed gives the same stored set.
    X, _ = ca3space.drawing_patterns(fake["vc"], 225, 16, 0)
    assert row["usage_cv"][0] == pytest.approx(
        sparsecodes.usage_cv(X[:20].topk(16, dim=1).indices, 225))
