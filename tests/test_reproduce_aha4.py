"""Checks that AHA's own setting still gives aha4's numbers.

E1 compares the local CA3 rules against AHA's pseudo-inverse rule, so the
pseudo-inverse path has to be the one aha4 measured.
"""

import os

import pytest
import torch

from trisynapsnet.data import omniglot
from trisynapsnet.eval import oneshot
from trisynapsnet.model.aha import AHA, AHAConfig, load_vc

# aha4 results/cpu_seed0.json: Lake's 20 runs, seed 0, CPU, study-to-test,
# raw-scale matching, pseudo-inverse CA3 at 225 cells with 10 on.
AHA4_CPU_SEED0 = {"pixels": 0.4425, "vc": 0.5225, "pr": 0.66, "pc": 0.62, "pm": 0.6225}

have_aha4 = omniglot.DEFAULT_CHECKPOINT.is_file() and \
    (omniglot.DEFAULT_DATA / "omniglot-runs" / "run20").is_dir()


@pytest.mark.skipif(not have_aha4, reason="aha4 checkpoint or runs not found")
@pytest.mark.skipif(os.environ.get("TSN_SLOW") != "1",
                    reason="takes a minute or two on the CPU; set TSN_SLOW=1")
def test_pinverse_reproduces_aha4_on_lakes_runs():
    runs = omniglot.load_runs()
    vc = load_vc(omniglot.DEFAULT_CHECKPOINT, device="cpu")
    aha = AHA(vc, AHAConfig(), device=torch.device("cpu"))
    result = oneshot.evaluate(aha, runs, [0], log=lambda line: None)
    for stage, expected in AHA4_CPU_SEED0.items():
        assert result["accuracy"][stage][0] == pytest.approx(expected, abs=1e-6)
