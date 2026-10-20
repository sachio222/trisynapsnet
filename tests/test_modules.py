"""Tests for the parts copied from aha4 into fh/model/modules.py.

They are the aha4 tests that cover code this project kept, so a change here
can't quietly break what aha4 fixed.
"""

import pytest
import torch
import torch.nn.functional as F

from fh.model import modules

DEVICES = ["cpu"]
if torch.backends.mps.is_available():
    DEVICES.append("mps")
if torch.cuda.is_available():
    DEVICES.append("cuda")


def test_hopfield_mask_marks_only_top_k_as_plus_one():
    x = torch.tensor([[0.1, 0.5, 0.3, 0.2, 0.0]])
    out = modules.get_top_k(x, k=2, mask_type="hopfield", topk_dim=1, scatter_dim=1)
    assert out.tolist() == [[-1.0, 1.0, 1.0, -1.0, -1.0]]


def test_binary_mask_marks_top_k_as_one():
    x = torch.tensor([[0.1, 0.5, 0.3, 0.2, 0.0]])
    out = modules.get_top_k(x, k=2, mask_type="binary", topk_dim=1, scatter_dim=1)
    assert out.tolist() == [[0.0, 1.0, 1.0, 0.0, 0.0]]


def test_pinverse_rule_stores_patterns_as_fixed_points():
    torch.manual_seed(0)
    X = torch.sign(torch.randn(10, 64))
    X[X == 0] = 1.0
    ca3 = modules.CA3(64)
    ca3.train(X, method="pinverse")
    assert torch.allclose(X @ ca3.W, X, atol=1e-4)


def test_hopfield_energy_keeps_fractional_values():
    ca3 = modules.CA3(3)
    ca3.W = torch.tensor([[0.0, 0.5, 0.2], [0.5, 0.0, 0.1], [0.2, 0.1, 0.0]])
    state = torch.tensor([[0.3, -0.7, 0.9]])
    expected = -0.5 * (state @ ca3.W @ state.T).item()
    assert ca3.energy(state).flatten()[0].item() == pytest.approx(expected)


def test_inference_vc_code_does_not_depend_on_the_batch():
    torch.manual_seed(0)
    vc = modules.EC(interest_filter=False).eval()
    x = torch.rand(4, 1, 52, 52)
    with torch.no_grad():
        batch = vc(x, k=4)
        single = vc(x[:1], k=4)
    assert torch.allclose(batch[0], single[0], atol=1e-6)


def test_vc_output_size():
    assert modules.EC(interest_filter=False).output_dim(52) == 121 * 13 * 13 == 20449


def test_inhibition_mask_reset_restores_full_shape():
    mask = modules.InhibitionMask(dim=225)
    fired = torch.zeros(1, 225)
    fired[0, :10] = 1.0
    mask.update(fired)
    assert (mask()[0, :10] < 1).all()
    mask.reset()
    assert mask().shape == (1, 225)
    assert torch.all(mask() == 1)


def test_dg_gives_k_active_units_and_separates_repeated_inputs():
    torch.manual_seed(0)
    dg = modules.DG(D_in=50, D_out=225, k=10)
    x = torch.rand(1, 50).repeat(20, 1)
    with torch.no_grad():
        out = dg(x)
    assert torch.all(out.sum(dim=1) == 10)
    assert (out[0] * out[1]).sum().item() == 0


def test_hopfield_recall_completes_a_corrupted_pattern():
    torch.manual_seed(0)
    X = -torch.ones(20, 225)
    for i in range(20):
        X[i, torch.randperm(225)[:10]] = 1.0
    ca3 = modules.CA3(225)
    ca3.train(X)
    cue = X.clone()
    cue[:, :20] *= -1
    out = ca3.update(cue)
    assert torch.all(torch.sign(out) == X)


@pytest.mark.parametrize("device", DEVICES)
@pytest.mark.parametrize("rule", modules.CA3_RULES)
def test_ca3_trains_and_recalls_on_every_available_device(device, rule):
    torch.manual_seed(0)
    X = torch.zeros(5, 225)
    for i in range(5):
        X[i, torch.randperm(225)[:10]] = 1.0
    if rule in modules.BIPOLAR_RULES:
        X = modules.condition_memorise(X)
    X = X.to(device)
    ca3 = modules.CA3(225, k=10)
    ca3.train(X, method=rule)
    out = ca3.update(X)
    assert out.device.type == device
    if rule != "hebbian":
        assert torch.equal((out > 0).cpu(), (X > 0).cpu())


def _stroke_images(n=20, size=52):
    """Line drawings with plenty of blank page, made like the real inputs."""
    from torchvision.transforms.functional import resize

    from fh.data.omniglot import centre_of_mass

    torch.manual_seed(0)
    big = torch.zeros(n, 1, 105, 105)
    for i in range(n):
        r, c = torch.randint(25, 60, (2,)).tolist()
        big[i, 0, r:r + 3, c:c + 30] = 1.0
        big[i, 0, r - 10:r + 15, c + 8:c + 11] = 1.0
    small = resize(big, [size, size], antialias=True)
    return torch.stack([centre_of_mass(img) for img in small])


def test_interest_points_sit_on_or_next_to_ink():
    x = _stroke_images()
    mask = modules.InterestFilter().mask(x)
    near_ink = F.max_pool2d(x, 7, 1, 3) > 0
    assert mask.sum() > 0
    assert torch.all(mask[~near_ink] == 0)


@pytest.mark.parametrize("device", DEVICES)
def test_interest_mask_is_the_same_on_every_device(device):
    x = _stroke_images()
    f = modules.InterestFilter()
    on_cpu = f.mask(x)
    on_device = f.to(device).mask(x.to(device))
    assert torch.equal(on_device.cpu(), on_cpu)
