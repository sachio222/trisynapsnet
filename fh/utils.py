# Adapted from github.com/sachio222/aha4 (MIT), utils/utils.py at 446d6db.
"""Small helpers for devices and seeds."""

import random

import numpy as np
import torch


def resolve_device(name="auto"):
    """Turns "auto", "cpu", "mps" or "cuda" into a torch.device.

    "auto" picks CUDA if there is an NVIDIA GPU, then MPS (Apple Silicon),
    then CPU. Asking for a backend this machine doesn't have raises a
    RuntimeError up front instead of failing halfway through a run.
    """
    name = name.lower()
    if name == "auto":
        if torch.cuda.is_available():
            return torch.device("cuda")
        if torch.backends.mps.is_available():
            return torch.device("mps")
        return torch.device("cpu")
    if name.startswith("cuda") and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested but is not available here.")
    if name == "mps" and not torch.backends.mps.is_available():
        raise RuntimeError("MPS was requested but is not available here.")
    return torch.device(name)


def set_seed(seed):
    """Seeds Python, NumPy and PyTorch so runs repeat."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
