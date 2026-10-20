"""Tests for one-shot scoring and the official runs."""

import pytest
import torch

from trisynapsnet.data import omniglot
from trisynapsnet.eval import oneshot


def test_min_mse_match_picks_the_nearest_study_item():
    study = torch.tensor([[0.0, 0.0], [1.0, 1.0], [5.0, 5.0]])
    recall = torch.tensor([[4.0, 4.5], [0.2, -0.1]])
    assert oneshot.min_mse_match(study, recall).tolist() == [2, 0]


def test_identical_sets_in_shuffled_order_score_perfectly():
    torch.manual_seed(0)
    study = torch.rand(20, 1, 8, 8)
    order = torch.randperm(20)
    assert oneshot.run_accuracy(study, study[order], order) == 1.0
    assert oneshot.run_accuracy(study, study[order], torch.roll(order, 1)) == 0.0


def test_study_to_test_and_test_to_study_can_disagree():
    study = torch.tensor([[0.0], [1.0], [10.0]])
    test = torch.tensor([[0.4], [0.45], [9.0]])
    labels = torch.tensor([0, 1, 2])
    assert oneshot.run_accuracy(study, test, labels) == 1.0
    assert oneshot.run_accuracy(study, test, labels, "test-to-study") == pytest.approx(2 / 3)


def test_normalise_matches_on_direction_not_length():
    study = torch.tensor([[1.0, 0.0], [0.0, 10.0]])
    test = torch.tensor([[5.0, 0.0], [0.0, 1.0]])
    labels = torch.tensor([0, 1])
    assert oneshot.run_accuracy(study, test, labels) == 0.5
    assert oneshot.run_accuracy(study, test, labels, normalise=True) == 1.0


def test_parse_class_labels_maps_test_items_to_training_classes():
    lines = ["run01/test/item01.png run01/training/class08.png",
             "run01/test/item02.png run01/training/class09.png", ""]
    assert omniglot.parse_class_labels(lines) == [7, 8]


def test_centre_of_mass_moves_ink_to_the_middle():
    x = torch.zeros(1, 52, 52)
    x[0, 2:6, 40:44] = 1.0
    out = omniglot.centre_of_mass(x)
    ys = torch.arange(52.0)
    cy = (out[0].sum(dim=1) * ys).sum() / out.sum()
    cx = (out[0].sum(dim=0) * ys).sum() / out.sum()
    assert abs(cy.item() - 25.5) < 0.5 and abs(cx.item() - 25.5) < 0.5
