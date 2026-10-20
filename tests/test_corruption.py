"""Tests for the test-image corruption in E1b.

AHA's paper (Section 3.2) corrupts drawings two ways. Occlusion covers a
randomly placed circle that lies completely inside the image, sized as a
diameter over the image side. Noise replaces a share of the pixels, given
as a fraction of the image area, with random intensities from a uniform
distribution.
"""

import math

import pytest
import torch

from trisynapsnet.data import corrupt

SIZE = 52


def blank(n=8, value=0.0):
    return torch.full((n, 1, SIZE, SIZE), value)


@pytest.mark.parametrize("diameter", [0.1, 0.3, 0.5, 0.7, 0.9, 0.98])
@pytest.mark.parametrize("seed", range(5))
def test_occlusion_circle_lies_inside_the_frame_at_full_diameter(diameter, seed):
    g = torch.Generator().manual_seed(seed)
    masks = corrupt.circle_masks(16, SIZE, diameter, g)
    d = diameter * SIZE
    for mask in masks:
        rows = mask.any(dim=1).nonzero().flatten()
        cols = mask.any(dim=0).nonzero().flatten()
        # A circle cut off by an edge would be narrower than its diameter.
        for span in (rows.max() - rows.min() + 1, cols.max() - cols.min() + 1):
            assert d - 1.5 <= span.item() <= d + 1.5
        area = math.pi * (d / 2) ** 2
        assert abs(mask.sum().item() - area) <= 0.05 * area + 2 * d


def test_each_drawing_gets_its_own_circle():
    g = torch.Generator().manual_seed(0)
    masks = corrupt.circle_masks(8, SIZE, 0.3, g)
    assert len({tuple(m.flatten().nonzero().flatten()[:5].tolist()) for m in masks}) > 1


def test_occlusion_paints_paper_over_the_circle_and_leaves_the_rest():
    images = blank(value=1.0)
    out = corrupt.corrupt(images, "occlusion", 0.4, seed=0, run=0)
    covered = out == 0.0
    d = 0.4 * SIZE
    assert torch.all((out == 0.0) | (out == 1.0))
    assert torch.allclose(covered.flatten(1).sum(dim=1).float(),
                          torch.full((8,), math.pi * (d / 2) ** 2), rtol=0.1)


@pytest.mark.parametrize("fraction", [0.1, 0.3, 0.55, 0.9, 0.98])
def test_noise_replaces_exactly_the_requested_share_of_pixels(fraction):
    # 2.0 is outside [0, 1), so every replaced pixel changes.
    images = blank(value=2.0)
    out = corrupt.corrupt(images, "noise", fraction, seed=3, run=1)
    changed = (out != 2.0).flatten(1).sum(dim=1)
    assert torch.all(changed == round(fraction * SIZE * SIZE))
    new = out[out != 2.0]
    assert new.min() >= 0.0 and new.max() < 1.0


@pytest.mark.parametrize("kind", corrupt.KINDS)
def test_level_zero_leaves_the_drawings_alone(kind):
    images = torch.rand(4, 1, SIZE, SIZE)
    assert torch.equal(corrupt.corrupt(images, kind, 0.0, seed=0, run=0), images)


@pytest.mark.parametrize("kind", corrupt.KINDS)
def test_corruption_repeats_from_its_seed_and_never_edits_the_input(kind):
    images = torch.rand(4, 1, SIZE, SIZE)
    before = images.clone()
    a = corrupt.corrupt(images, kind, 0.5, seed=7, run=2)
    b = corrupt.corrupt(images, kind, 0.5, seed=7, run=2)
    c = corrupt.corrupt(images, kind, 0.5, seed=8, run=2)
    d = corrupt.corrupt(images, kind, 0.5, seed=7, run=3)
    assert torch.equal(a, b)
    assert not torch.equal(a, c)
    assert not torch.equal(a, d)
    assert torch.equal(images, before)


def test_unknown_kind_and_bad_levels_are_refused():
    images = blank()
    with pytest.raises(ValueError):
        corrupt.corrupt(images, "blur", 0.5, seed=0, run=0)
    for level in (-0.1, 1.0):
        with pytest.raises(ValueError):
            corrupt.corrupt(images, "noise", level, seed=0, run=0)


def test_paper_levels_run_from_none_to_just_below_98_percent():
    levels = corrupt.PAPER_LEVELS
    assert levels[0] == 0.0 and levels[-1] == 0.98
    assert len(levels) == 11
    assert all(a < b for a, b in zip(levels, levels[1:]))
