"""Tests for E1c's CA3 harness: patterns, damage, the ideal lookup and scoring.

The harness stores patterns in CA3, cues it with damaged copies and scores
how close settling comes to an ideal nearest-memory lookup, which compares
the cue with a list of every stored pattern.
"""

import pytest
import torch

from trisynapsnet.eval import ca3space


def test_count_rounds_half_up():
    assert ca3space.count(0.25, 10) == 3
    assert ca3space.count(0.2, 44) == 9
    assert ca3space.count(0.6, 44) == 26
    assert ca3space.count(0.8, 178) == 142
    assert ca3space.count(0.5, 10) == 5
    assert ca3space.count(0.0, 10) == 0


@pytest.mark.parametrize("n,k", [(225, 10), (1000, 44)])
def test_random_patterns_have_exactly_k_cells_on(n, k):
    X = ca3space.random_patterns(300, n, k, torch.Generator().manual_seed(0))
    assert X.shape == (300, n)
    assert set(X.unique().tolist()) == {0.0, 1.0}
    assert torch.all(X.sum(dim=1) == k)
    again = ca3space.random_patterns(300, n, k, torch.Generator().manual_seed(0))
    other = ca3space.random_patterns(300, n, k, torch.Generator().manual_seed(1))
    assert torch.equal(X, again)
    assert not torch.equal(X, other)
    # Each cell is on about as often as any other.
    assert X.mean(dim=0).max() < 5 * k / n


@pytest.mark.parametrize("remove,add", [(0.0, 0.0), (0.2, 0.0), (0.8, 0.0), (0.0, 0.25),
                                        (0.0, 1.0), (0.4, 0.5)])
@pytest.mark.parametrize("n,k", [(225, 10), (4000, 178)])
def test_damage_removes_and_adds_exact_counts(remove, add, n, k):
    X = ca3space.random_patterns(50, n, k, torch.Generator().manual_seed(0))
    before = X.clone()
    cue = ca3space.damage(X, remove, add, torch.Generator().manual_seed(1))
    assert torch.equal(X, before)
    on, cued = X > 0, cue > 0
    kept = (on & cued).sum(dim=1)
    stray = (~on & cued).sum(dim=1)
    assert torch.all(kept == k - ca3space.count(remove, k))
    assert torch.all(stray == ca3space.count(add, k))
    assert set(cue.unique().tolist()) <= {0.0, 1.0}
    if remove and add == 0:
        # Rows get their own draws, not one shared set of removed cells.
        assert len({tuple((on[i] & ~cued[i]).nonzero().flatten().tolist())
                    for i in range(50)}) > 1


def test_damage_refuses_patterns_of_mixed_size():
    X = torch.zeros(2, 10)
    X[0, :3] = 1.0
    X[1, :4] = 1.0
    with pytest.raises(ValueError):
        ca3space.damage(X, 0.2, 0.0, torch.Generator().manual_seed(0))


# Three stored patterns with 3 of 9 cells on, no cells shared.
A, B, C = [0, 1, 2], [3, 4, 5], [6, 7, 8]


def three_patterns():
    X = torch.zeros(3, 9)
    for i, cells in enumerate((A, B, C)):
        X[i, cells] = 1.0
    return X


def on(*cells):
    row = torch.zeros(9, dtype=torch.bool)
    row[list(cells)] = True
    return row


def test_lookup_splits_ties_evenly():
    X = three_patterns()
    cues = torch.stack([on(0, 1), on(0, 3), on(0, 3, 6), on(), on(4, 5)])
    target = torch.tensor([0, 0, 0, 0, 0])
    credit, nearest = ca3space.lookup(cues, X, target)
    # Unique nearest and right; tied with one other; tied with two others;
    # no cell on, so all three tie; unique nearest but wrong.
    assert credit.tolist() == pytest.approx([1.0, 0.5, 1 / 3, 1 / 3, 0.0])
    assert nearest[0].item() == 0 and nearest[4].item() == 1


def test_score_on_a_hand_built_example():
    X = three_patterns()
    cue = torch.stack([on(0, 1), on(0, 1, 2, 4), on(0, 3), on(6)])
    final = torch.stack([on(0, 1, 2), on(0, 1, 2), on(3, 4, 5), on(1, 2, 7)])
    target = torch.tensor([0, 0, 0, 2])
    s = ca3space.score(cue, final, X, target)
    # Row 0: two of A's cells cue A, and CA3 completes it exactly.
    # Row 1: all of A plus one stray cell; CA3 drops the stray.
    # Row 2: a cue tied between A and B; CA3 settles on B, the wrong memory.
    # Row 3: one cell of C; CA3 ends on a mixture that is no stored pattern.
    assert s["exact"].tolist() == [1.0, 1.0, 0.0, 0.0]
    assert s["overlap_cue"].tolist() == pytest.approx([2 / 3, 1.0, 1 / 3, 1 / 3])
    assert s["overlap_final"].tolist() == pytest.approx([1.0, 1.0, 0.0, 1 / 3])
    assert s["stray_cue"].tolist() == pytest.approx([0.0, 1 / 3, 1 / 3, 0.0])
    assert s["stray_final"].tolist() == pytest.approx([0.0, 0.0, 1.0, 2 / 3])
    assert s["ident_cue"].tolist() == pytest.approx([1.0, 1.0, 0.5, 1.0])
    assert s["ident_final"].tolist() == pytest.approx([1.0, 1.0, 0.0, 0.0])
    assert s["on_stored"].tolist() == [1.0, 1.0, 1.0, 0.0]
    assert s["active_final"].tolist() == [3.0, 3.0, 3.0, 3.0]


def test_covariance_completes_the_hand_built_example():
    X = three_patterns()
    ca3 = ca3space.build_ca3("covariance", 9, 3)
    ca3.train(X, method="covariance")
    cue = torch.zeros(3, 9)
    cue[0, [0, 1]] = 1.0        # two cells of A
    cue[1, [3, 4, 5, 8]] = 1.0  # B with a stray cell from C
    cue[2, [7]] = 1.0           # one cell of C
    state, info = ca3.settle(cue)
    assert torch.equal(state, X)
    assert info["fixed"].all()


@pytest.mark.parametrize("rule", ca3space.RULES)
def test_run_load_recalls_a_light_load_exactly(rule):
    X = ca3space.random_patterns(20, 225, 10, torch.Generator().manual_seed(0))
    rows = ca3space.run_load(rule, X, ("test", 0))
    assert [(r["remove"], r["add"]) for r in rows] == list(ca3space.CONDITIONS)
    clean = rows[0]["scores"]
    assert clean["exact"] == 1.0 and clean["ident_cue"] == 1.0 and clean["fixed"] == 1.0
    assert set(clean) == set(ca3space.METRICS)
    half = [r for r in rows if (r["remove"], r["add"]) == (0.4, 0.0)][0]["scores"]
    assert half["overlap_cue"] == pytest.approx(0.6)
    assert half["overlap_final"] >= 0.95


def test_run_load_pairs_cues_across_rules_and_samples_large_loads():
    X = ca3space.random_patterns(300, 225, 10, torch.Generator().manual_seed(0))
    a = ca3space.run_load("covariance", X, ("test", 1))
    b = ca3space.run_load("willshaw", X, ("test", 1))
    assert a[0]["cues"] == ca3space.MAX_CUES
    # The raw cues are the same for every rule.
    for ra, rb in zip(a, b):
        assert ra["scores"]["overlap_cue"] == rb["scores"]["overlap_cue"]
        assert ra["scores"]["ident_cue"] == rb["scores"]["ident_cue"]


def test_run_load_scores_ca1_when_given_drawings():
    g = torch.Generator().manual_seed(0)
    X = ca3space.random_patterns(20, 225, 10, g)
    images = (torch.rand(20, 1, 52, 52, generator=g) > 0.9).float()
    rows = ca3space.run_load("covariance", X, ("test", 2), images=images)
    s = rows[0]["scores"]
    assert set(ca3space.CA1_METRICS) <= set(s)
    # Undamaged cues settle on the stored pattern, so every CA1 input is
    # the stored pattern itself.
    assert s["ca1_final"] == pytest.approx(s["ca1_target"])
    assert s["ca1_cue"] == pytest.approx(s["ca1_target"])


def test_drawing_patterns_follow_dg():
    g = torch.Generator().manual_seed(0)
    vc = torch.rand(30, 64, generator=g)
    X, order = ca3space.drawing_patterns(vc, 225, 10, seed=0)
    assert X.shape == (30, 225)
    assert torch.all(X.sum(dim=1) == 10)
    assert sorted(order.tolist()) == list(range(30))
    again, order2 = ca3space.drawing_patterns(vc, 225, 10, seed=0)
    assert torch.equal(X, again) and torch.equal(order, order2)
    # Refractory inhibition keeps consecutive drawings off each other's cells.
    assert ((X[:-1] * X[1:]).sum(dim=1) == 0).all()


def test_default_output_names():
    p = ca3space.build_parser()
    args = p.parse_args(["--source", "drawings", "--rule", "pinverse", "--units", "1000"])
    args.k = 44
    assert ca3space.default_out(args).name == "e1c_ca3_drawings_evaluation_pinverse_1000_44.json"
    args = p.parse_args(["--source", "random", "--rule", "willshaw"])
    args.k = 10
    assert ca3space.default_out(args).name == "e1c_ca3_random_willshaw_225_10.json"


def test_load_characters_gives_one_drawing_of_every_character(tmp_path):
    from trisynapsnet.data import omniglot
    from tests.test_e1b import fake_alphabets
    root = fake_alphabets(tmp_path, alphabets=2, characters=15)
    images, info = omniglot.load_characters(root, split="evaluation", seed=0)
    assert images.shape == (30, 1, 52, 52)
    assert len({(i["alphabet"], i["character"]) for i in info}) == 30
    assert all(1 <= i["drawer"] <= 20 for i in info)
    again, info2 = omniglot.load_characters(root, split="evaluation", seed=0)
    _, info3 = omniglot.load_characters(root, split="evaluation", seed=1)
    assert info == info2 and torch.equal(images, again)
    assert [i["drawer"] for i in info] != [i["drawer"] for i in info3]
