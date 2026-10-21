# Adapted from github.com/sachio222/aha4 (MIT), utils/oneshot.py at 446d6db.
# New here: per-seed diagnostics (CA3 self-recall and DG overlap).
"""Scoring for the one-shot Omniglot classification benchmark.

The benchmark comes from Lake, Salakhutdinov and Tenenbaum (2015). Each
run has 20 study drawings, one per character, all from one alphabet and
one person, and 20 test drawings of the same characters by a different
person. A model gets one look at the study set. Chance is 1 in 20.

As in the AHA paper (Section 3.1), matching is by minimum mean squared
error (MSE) between an internal state at study time and the same state at
recall time, averaged over the runs.

    direction   study-to-test (the default) has each study drawing look
                for its partner among the test drawings, as the paper
                describes on p8. test-to-study asks the opposite question.
    normalise   Divide every vector by its L2 norm before taking the MSE,
                so matching compares direction and ignores length.
"""

import statistics
import time

import torch
import torch.nn.functional as F

# Stages of the model you can score, in the order a drawing passes them.
STAGES = ("pixels", "vc", "pr", "pc", "pm")

# Matching directions. The first is the default.
DIRECTIONS = ("study-to-test", "test-to-study")

# Per-seed diagnostics that evaluate() can add, each a mean over runs.
DIAGNOSTICS = ("self_recall_exact", "self_recall_overlap", "self_recall_active",
               "dg_same", "dg_diff", "dg_same_inhibited", "dg_diff_inhibited")


def _flat(x, normalise=False):
    x = x.detach().flatten(1).float().cpu()
    return F.normalize(x, dim=1) if normalise else x


def mse_matrix(study, recall, normalise=False):
    """MSE between every recall item (rows) and every study item (columns)."""
    s, r = _flat(study, normalise), _flat(recall, normalise)
    return torch.cdist(r, s) ** 2 / s.shape[1]


def min_mse_match(study, recall, normalise=False):
    """For each recall item, the index of the study item with lowest MSE."""
    return mse_matrix(study, recall, normalise).argmin(dim=1)


def run_accuracy(study, recall, labels, direction=DIRECTIONS[0], normalise=False):
    """Share of items matched to their true partner.

    labels[j] is the study index that recall item j shows.
    """
    mse = mse_matrix(study, recall, normalise)
    labels = labels.cpu()
    if direction == "study-to-test":
        nearest = mse.argmin(dim=0)
        hits = labels[nearest] == torch.arange(mse.shape[1])
    elif direction == "test-to-study":
        hits = mse.argmin(dim=1) == labels
    else:
        raise ValueError("direction must be one of {}".format(DIRECTIONS))
    return hits.float().mean().item()


def recall_loss(reconstruction, study_images, labels):
    """MSE between each recalled image and the study drawing it should be.

    AHA paper Section 3.3 calls this recall-loss.
    """
    target = study_images.cpu()[labels.cpu()]
    return torch.mean((reconstruction.detach().cpu() - target) ** 2).item()


def run_diagnostics(aha, study, recall, labels):
    """CA3 self-recall and DG overlap for one run, as a flat dict."""
    sr = aha.self_recall(study)
    dg = aha.dg_overlap(study, recall, labels)
    return {"self_recall_exact": sr["exact"], "self_recall_overlap": sr["overlap"],
            "self_recall_active": sr["active"], "dg_same": dg["same"], "dg_diff": dg["diff"],
            "dg_same_inhibited": dg["same_inhibited"], "dg_diff_inhibited": dg["diff_inhibited"]}


def evaluate(aha, runs, seeds, stages=STAGES, direction=DIRECTIONS[0], normalise=False,
             diagnostics=False, log=print):
    """Runs every one-shot run once per seed and scores each stage.

    The hippocampus is reset before every run with a seed made from the seed
    and run number, so each (seed, run) pair repeats exactly on the CPU.
    Diagnostics run after recall, so they never change the scores.

    Returns a dict with per-seed mean accuracy for each stage, per-seed mean
    recall-loss, the wall time, and with diagnostics=True, per-seed means of
    each diagnostic.
    """
    levels = [(0.0, [run["recall"] for run in runs])]
    result = evaluate_levels(aha, runs, levels, seeds, stages, direction, normalise,
                             diagnostics, log)[0]
    del result["level"]
    return result


def evaluate_levels(aha, runs, levels, seeds, stages=STAGES, direction=DIRECTIONS[0],
                    normalise=False, diagnostics=False, log=print):
    """Scores one study against several versions of the test drawings.

    E1b corrupts the test drawings at many levels. The study set and the
    hippocampus it trains are the same at every level, so each (seed, run)
    studies once and then recalls each version in turn. Recall never
    learns. The random generator that bipolar settling draws from goes back
    to its state after study before each level, so a level scores the same
    whatever other levels run with it, and a lone clean level scores
    exactly as evaluate() does.

    Args:
        levels: list of (level, test drawings), where test drawings is a
            list with one (20, 1, H, W) tensor per run. Keep the same
            tensors across calls and the VC cache encodes each one once.

    Returns one dict per level, in the order given, shaped like evaluate()'s
    result plus the level.
    """
    start = time.time()
    out = [{"level": level, "accuracy": {stage: [] for stage in stages}, "recall_loss": [],
            "diagnostics": {name: [] for name in DIAGNOSTICS}} for level, _ in levels]

    for seed in seeds:
        per_run = [{"accuracy": {stage: [] for stage in stages}, "recall_loss": [],
                    "diagnostics": {name: [] for name in DIAGNOSTICS}} for _ in levels]
        for i, run in enumerate(runs):
            aha.reset(seed=seed * 1000 + i)
            study = aha.study(run["study"])
            after_study = aha.generator.get_state()
            for (_, tests), acc in zip(levels, per_run):
                aha.generator.set_state(after_study)
                recall = aha.recall(tests[i])
                for stage in stages:
                    acc["accuracy"][stage].append(run_accuracy(
                        study[stage], recall[stage], run["labels"], direction, normalise))
                # With E4's CA1 the "pm" stage is an EC code, so its loss is
                # taken against the study drawings' EC codes.
                target = run["study"] if recall["pm"].dim() == 4 else study["vc"]
                acc["recall_loss"].append(recall_loss(recall["pm"], target, run["labels"]))
                if diagnostics:
                    for name, value in run_diagnostics(aha, study, recall, run["labels"]).items():
                        acc["diagnostics"][name].append(value)

        for res, acc in zip(out, per_run):
            for stage in stages:
                res["accuracy"][stage].append(sum(acc["accuracy"][stage]) / len(runs))
            res["recall_loss"].append(sum(acc["recall_loss"]) / len(runs))
            line = "seed {:>3}  ".format(seed)
            if len(levels) > 1:
                line += "level {:<5g} ".format(res["level"])
            line += "  ".join("{} {:.1%}".format(stage, res["accuracy"][stage][-1])
                              for stage in stages)
            if diagnostics:
                for name in DIAGNOSTICS:
                    res["diagnostics"][name].append(statistics.mean(acc["diagnostics"][name]))
                line += "  self-recall {:.1%}  dg same {:.2f} diff {:.2f}".format(
                    res["diagnostics"]["self_recall_exact"][-1],
                    res["diagnostics"]["dg_same"][-1], res["diagnostics"]["dg_diff"][-1])
            log(line + "  ({:.0f} s)".format(time.time() - start))

    seconds = time.time() - start
    for res in out:
        res["seconds"] = seconds
        if not diagnostics:
            del res["diagnostics"]
    return out
