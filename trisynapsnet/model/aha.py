# Adapted from github.com/sachio222/aha4 (MIT), model/aha.py at 446d6db.
# New here: routing for the local CA3 rules, the cue weight, and the
# self-recall and DG overlap diagnostics.
"""The full model: a frozen vision network feeding a resettable hippocampus.

The wiring follows AHA (Kowadlo, Ahmed and Rawlinson 2019, Figure 4). One
evaluation step goes like this:
  1. Study: show a small set of drawings once. The hippocampus learns them.
     The vision network stays frozen.
  2. Recall: show new drawings. For each one, the model should bring back
     the matching study drawing.
  3. Reset: wipe the hippocampus, weights and optimizer state, before the
     next set.

AHA's hyperparameters (paper Table 3) are the defaults in AHAConfig.
"""

from dataclasses import dataclass

import torch
import torch.nn.functional as F

from trisynapsnet.model import modules


@dataclass
class AHAConfig:
    image_size: int = 52
    vc_k: int = 4               # active filters per position at inference
    normalise_input: bool = False  # L2-normalise the VC output before the hippocampus

    dg_units: int = 225         # DG and CA3 size
    dg_k: int = 10              # active DG units per drawing, and active CA3 cells
    dg_gamma: float = 0.95      # inhibition decay per drawing
    dg_knockout: float = 0.25   # share of DG input weights set to zero

    ca3_rule: str = "pinverse"  # pinverse, hebbian, covariance or willshaw
    ca3_gain: float = 2.7       # tanh gain, bipolar rules
    ca3_update: int = 20        # neurons updated per step, bipolar rules
    ca3_iters: int = 70         # settling steps (the most for local rules)
    ca3_cue_weight: float = 0.0  # how strongly the cue keeps driving CA3, local rules

    pr_hidden: int = 1000
    pr_lr: float = 0.01
    pr_l2: float = 2.5e-5
    pr_cue_gain: float = 10.0   # gamma in AHA's Appendix A.2

    pm_hidden: int = 100
    pm_lr: float = 0.01
    pm_l2: float = 4e-4

    study_steps: int = 60       # optimizer steps on the one study batch

    @property
    def local_rule(self):
        return self.ca3_rule in modules.LOCAL_RULES


def load_vc(checkpoint, interest_filter=True, device="cpu"):
    """Builds the inference vision network and loads its pretrained filters."""
    vc = modules.EC(interest_filter=interest_filter)
    state = torch.load(checkpoint, map_location="cpu")
    vc.load_pretrained(state["state_dict"])
    return vc.to(device).eval()


def _overlap(a, b, k):
    """Shared active units between every row of a and every row of b, over k."""
    return ((a.float() @ b.float().T) / k).cpu()


def _same_and_diff(overlap, labels):
    """Mean overlap of matching pairs and of all other pairs.

    overlap[i, j] compares study item i with recall item j, and recall item
    j shows the character of study item labels[j].
    """
    same = torch.zeros_like(overlap, dtype=torch.bool)
    same[labels, torch.arange(len(labels))] = True
    return overlap[same].mean().item(), overlap[~same].mean().item()


class AHA():
    """A frozen VC(EC) feeding a resettable hippocampus.

    Data flow:

        study:  image -> VC -> DG -> CA3 stores DG pattern
                         VC -> PR learns to output the DG pattern
                               CA1 learns stored pattern -> image
        recall: image -> VC -> PR -> cue -> CA3 settles -> CA1 -> image

    With a bipolar CA3 rule, CA3 stores DG's pattern turned into -1/+1, and
    the PR output is reshaped into a -1/+1 cue first (AHA's Appendix A).
    With a local rule, CA3 stores DG's 0/1 pattern as it is, and the PR
    output is the cue.

    study() and recall() return every internal state, so each stage can be
    scored the way the paper does.
    """

    def __init__(self, vc, config=None, device=torch.device("cpu")):
        self.cfg = config or AHAConfig()
        self.device = torch.device(device)
        self.vc = vc.to(self.device).eval()
        for p in self.vc.parameters():
            p.requires_grad_(False)
        self.in_dim = self.vc.output_dim(self.cfg.image_size)
        self._vc_cache = None

    def reset(self, seed=0):
        """Builds a fresh hippocampus. Every run starts from new random weights."""
        cfg = self.cfg
        torch.manual_seed(seed)
        self.generator = torch.Generator().manual_seed(seed)

        self.dg = modules.DG(self.in_dim, cfg.dg_units, cfg.dg_k,
                             cfg.dg_gamma, cfg.dg_knockout).to(self.device)
        self.ca3 = modules.CA3(cfg.dg_units, cfg.ca3_gain, cfg.ca3_update, cfg.ca3_iters,
                               k=cfg.dg_k, cue_weight=cfg.ca3_cue_weight)
        self.pr = modules.ECToCA3(self.in_dim, cfg.dg_units, cfg.pr_hidden).to(self.device)
        self.pm = modules.CA1(cfg.dg_units, cfg.image_size**2, cfg.pm_hidden,
                              cfg.image_size).to(self.device)

        # Adam's weight_decay adds an L2 penalty to the gradient, which is the
        # paper's L2 regularisation.
        self.pr_opt = torch.optim.Adam(self.pr.parameters(), lr=cfg.pr_lr, weight_decay=cfg.pr_l2)
        self.pm_opt = torch.optim.Adam(self.pm.parameters(), lr=cfg.pm_lr, weight_decay=cfg.pm_l2)

    def cache_vc(self, on=True):
        """Keeps each batch's vision code after the first time it is seen.

        The vision network is frozen and gives the same output for the same
        images, so an evaluation that repeats the same runs over many seeds
        only needs to encode each run once. The cache is keyed by the
        tensor's identity, so it only helps when the same image tensors come
        back, as they do in the one-shot runs.
        """
        self._vc_cache = {} if on else None

    @torch.no_grad()
    def encode(self, images):
        """The VC output that every hippocampal part sees.

        With normalise_input, each drawing's vector is divided by its L2
        norm first, as in the AHA authors' later code (Cerenaut/pt-aha).
        """
        key = id(images)
        if self._vc_cache is not None and key in self._vc_cache:
            cached, vc = self._vc_cache[key]
            if cached is images:
                return vc
        vc = self.vc(images.to(self.device), k=self.cfg.vc_k)
        vc = F.normalize(vc, dim=1) if self.cfg.normalise_input else vc
        if self._vc_cache is not None:
            self._vc_cache[key] = (images, vc)
        return vc

    def study(self, images):
        """Memorises a batch of drawings in one exposure."""
        vc = self.encode(images)
        images = images.to(self.device)

        with torch.no_grad():
            dg = self.dg(vc)
            stored = dg if self.cfg.local_rule else modules.condition_memorise(dg)
        self.ca3.train(stored, self.cfg.ca3_rule)

        # PR learns to map each vision code to its DG pattern. The DG pattern
        # is an internally made label, so no outside labels are used.
        for _ in range(self.cfg.study_steps):
            loss = F.binary_cross_entropy_with_logits(self.pr.logits(vc), dg)
            self.pr_opt.zero_grad()
            loss.backward()
            self.pr_opt.step()

        # CA1 learns to turn each stored CA3 pattern back into its drawing.
        for _ in range(self.cfg.study_steps):
            loss = F.mse_loss(self.pm(stored), images)
            self.pm_opt.zero_grad()
            loss.backward()
            self.pm_opt.step()

        with torch.no_grad():
            return {"pixels": images, "vc": vc, "dg": dg, "pr": self.pr(vc),
                    "pc": stored, "pm": self.pm(stored)}

    def cue(self, pr):
        """The CA3 cue for a batch of PR outputs."""
        if self.cfg.local_rule:
            return pr
        return modules.condition_recall(pr, self.cfg.dg_k, self.cfg.pr_cue_gain)

    @torch.no_grad()
    def recall(self, images):
        """Brings back a memory for each drawing, without learning."""
        vc = self.encode(images)
        images = images.to(self.device)
        pr = self.pr(vc)
        pc = self.ca3.update(self.cue(pr), generator=self.generator)
        return {"pixels": images, "vc": vc, "pr": pr, "pc": pc, "pm": self.pm(pc)}

    @torch.no_grad()
    def self_recall(self, study):
        """Cues CA3 with each study drawing's own PR output after study.

        A cell counts as on when its state is above zero, which works for
        both the 0/1 and the -1/+1 rules. Returns:
            exact: share of drawings whose settled state has exactly the
                stored pattern's cells on and no others.
            overlap: mean share of the stored pattern's k cells that are on.
            active: mean number of cells on after settling.

        Call it after recall(): the bipolar rules draw from the same random
        generator, so calling it first would change recall's results.
        """
        settled = self.ca3.update(self.cue(study["pr"]), generator=self.generator)
        on, stored = settled > 0, study["pc"] > 0
        return {
            "exact": (on == stored).all(dim=1).float().mean().item(),
            "overlap": ((on & stored).sum(dim=1).float() / self.cfg.dg_k).mean().item(),
            "active": on.sum(dim=1).float().mean().item(),
        }

    @torch.no_grad()
    def dg_overlap(self, study, recall, labels):
        """How many DG cells a study drawing and a recall drawing share.

        The overlap of two codes is shared active cells over k. Pairs that
        show the same character are compared with pairs that show different
        characters. Measured twice:
            same, diff: DG's random projection and top k alone, without the
                refractory inhibition, so the codes depend only on the
                drawings.
            same_inhibited, diff_inhibited: DG as it runs in the model, with
                inhibition starting fresh for the study batch and again for
                the recall batch. The study codes are the stored ones.
        """
        k = self.cfg.dg_k
        labels = labels.cpu()

        def plain(vc):
            return modules.get_top_k(self.dg.fc1(vc), k, "binary", 1, 1)

        same, diff = _same_and_diff(_overlap(plain(study["vc"]), plain(recall["vc"]), k), labels)

        saved = self.dg.phi.inhibition
        self.dg.reset()
        s = self.dg(study["vc"])
        self.dg.reset()
        r = self.dg(recall["vc"])
        self.dg.phi.inhibition = saved
        same_i, diff_i = _same_and_diff(_overlap(s, r, k), labels)

        return {"same": same, "diff": diff, "same_inhibited": same_i, "diff_inhibited": diff_i}
