"""Tests for E1b: instance runs and scoring the same study at many
corruption levels.

AHA's one-shot instance-classification task (paper Section 3.2) studies 20
drawings of one character and must match each with the very same drawing
among all 20 at test time.
"""

import numpy as np
import pytest
import torch
from PIL import Image

from fh.data import corrupt, omniglot
from fh.eval import evaluate, oneshot
from fh.model import modules
from fh.model.aha import AHA, AHAConfig


def fake_alphabets(root, split="evaluation", alphabets=2, characters=15):
    """A tiny Omniglot folder: random 105x105 drawings by 20 drawers each."""
    rng = np.random.default_rng(0)
    folder = root / "omniglot-py" / "images_{}".format(split)
    image_id = 0
    for a in range(alphabets):
        for c in range(characters):
            char_dir = folder / "Alphabet{}".format(a) / "character{:02d}".format(c + 1)
            char_dir.mkdir(parents=True)
            image_id += 1
            for drawer in range(1, omniglot.N_DRAWERS + 1):
                pixels = (rng.random((105, 105)) > 0.05).astype(np.uint8) * 255
                Image.fromarray(pixels, mode="L").save(
                    char_dir / "{:04d}_{:02d}.png".format(image_id, drawer))
    return root


def test_instance_runs_match_each_drawing_with_itself(tmp_path):
    root = fake_alphabets(tmp_path)
    runs = omniglot.load_instance_runs(root, split="evaluation", seed=0)
    assert len(runs) == 20
    seen = set()
    for run in runs:
        assert run["study"].shape == (20, 1, 52, 52)
        labels = run["labels"]
        assert sorted(labels.tolist()) == list(range(20))
        # Each test item is the exact study drawing its label points at.
        assert torch.equal(run["recall"], run["study"][labels])
        info = run["info"]
        assert sorted(info["drawers"]) == list(range(1, 21))
        seen.add((info["alphabet"], info["character"]))
    # Characters are drawn without repeats.
    assert len(seen) == 20


def test_instance_runs_repeat_from_a_seed(tmp_path):
    root = fake_alphabets(tmp_path)
    a = omniglot.load_instance_runs(root, split="evaluation", seed=0)
    b = omniglot.load_instance_runs(root, split="evaluation", seed=0)
    c = omniglot.load_instance_runs(root, split="evaluation", seed=1)
    assert [r["info"] for r in a] == [r["info"] for r in b]
    assert torch.equal(a[3]["study"], b[3]["study"])
    assert [r["info"] for r in a] != [r["info"] for r in c]


def test_instance_runs_build_from_the_background_alphabets_too(tmp_path):
    root = fake_alphabets(tmp_path, split="background")
    runs = omniglot.load_instance_runs(root, split="background", seed=0)
    assert len(runs) == 20
    assert all(r["info"]["split"] == "background" for r in runs)


def test_instance_runs_refuse_a_split_with_too_few_characters(tmp_path):
    root = fake_alphabets(tmp_path, alphabets=1, characters=5)
    with pytest.raises(ValueError):
        omniglot.load_instance_runs(root, split="evaluation", seed=0)


def test_evaluate_accepts_the_e1b_options():
    args = evaluate.parse_args([
        "--task", "instance", "--occlusion", "0", "0.1", "0.98",
        "--corruption-seed", "4", "--ca3-rule", "covariance", "--ca3-iters", "0"])
    assert args.task == "instance"
    assert evaluate.corruption_levels(args) == ("occlusion", [0.0, 0.1, 0.98])
    assert args.corruption_seed == 4
    assert evaluate.default_out(args).name == \
        "e1b_instance_official_covariance_225_10_it0_occlusion.json"

    noise = evaluate.parse_args(["--noise", "0.5"])
    assert evaluate.corruption_levels(noise) == ("noise", [0.5])
    assert evaluate.default_out(noise).name == \
        "e1b_classification_official_pinverse_225_10_noise.json"

    clean = evaluate.parse_args([])
    assert clean.task == "classification"
    assert evaluate.corruption_levels(clean) == ("none", [0.0])
    # A clean classification run keeps E1's file name.
    assert evaluate.default_out(clean).name == "bio_e1_official_pinverse_225_10.json"


def test_evaluate_refuses_noise_and_occlusion_together():
    args = evaluate.parse_args(["--noise", "0.1", "--occlusion", "0.2"])
    with pytest.raises(SystemExit):
        evaluate.corruption_levels(args)


def _tiny_runs(n_runs=2, seed=0):
    g = torch.Generator().manual_seed(seed)
    runs = []
    for _ in range(n_runs):
        study = (torch.rand(20, 1, 52, 52, generator=g) > 0.9).float()
        order = torch.randperm(20, generator=g)
        runs.append({"study": study, "recall": study[order].clone(), "labels": order})
    return runs


def _tiny_aha(rule):
    # The untrained vision network draws its filters from the global seed.
    torch.manual_seed(0)
    vc = modules.EC(interest_filter=False)
    return AHA(vc, AHAConfig(ca3_rule=rule, pr_hidden=64, study_steps=3),
               device=torch.device("cpu"))


def _levels(runs, kind, values):
    return [(level, [corrupt.corrupt(r["recall"], kind, level, seed=0, run=i)
                     for i, r in enumerate(runs)]) for level in values]


@pytest.mark.parametrize("rule", ["pinverse", "covariance"])
def test_scoring_many_levels_matches_scoring_each_alone(rule):
    runs = _tiny_runs()
    levels = _levels(runs, "noise", [0.0, 0.5])
    quiet = dict(seeds=[0, 1], normalise=True, diagnostics=True, log=lambda line: None)

    together = oneshot.evaluate_levels(_tiny_aha(rule), runs, levels, **quiet)
    flipped = oneshot.evaluate_levels(_tiny_aha(rule), runs, levels[::-1], **quiet)
    plain = oneshot.evaluate(_tiny_aha(rule), runs, **quiet)

    assert [r["level"] for r in together] == [0.0, 0.5]
    # The level order never changes a score, even with bipolar settling,
    # which draws random cells.
    for a, b in zip(together, flipped[::-1]):
        assert a["accuracy"] == b["accuracy"]
        assert a["recall_loss"] == b["recall_loss"]
    # The clean level is exactly the plain one-shot evaluation.
    assert together[0]["accuracy"] == plain["accuracy"]
    assert together[0]["recall_loss"] == plain["recall_loss"]
    assert together[0]["diagnostics"] == plain["diagnostics"]


def test_recall_loss_compares_with_the_clean_study_drawing():
    runs = _tiny_runs(n_runs=1)
    levels = _levels(runs, "occlusion", [0.0, 0.9])
    result = oneshot.evaluate_levels(_tiny_aha("covariance"), runs, levels, seeds=[0],
                                     log=lambda line: None)
    for r in result:
        assert len(r["recall_loss"]) == 1 and r["recall_loss"][0] > 0
    # Pixels of a heavily occluded test drawing are far from the study
    # drawing, so the pixel stage must score below the clean level.
    assert result[1]["accuracy"]["pixels"][0] <= result[0]["accuracy"]["pixels"][0]


needs_evaluation = pytest.mark.skipif(
    not (omniglot.LOCAL_DATA / "omniglot-py" / "images_evaluation").is_dir(),
    reason="Omniglot evaluation alphabets not downloaded")


@needs_evaluation
def test_official_instance_runs_come_from_the_evaluation_alphabets():
    runs = omniglot.load_instance_runs(seed=0)
    assert len(runs) == 20
    assert len({(r["info"]["alphabet"], r["info"]["character"]) for r in runs}) == 20
    for run in runs:
        assert run["info"]["split"] == "evaluation"
        assert torch.equal(run["recall"], run["study"][run["labels"]])
