"""E3's two example figures: Omniglot and the tasks, and single recalls.

Reruns the reported E3 model on the evaluation drawings and writes, in
figures/e3_examples/, PNG tiles, examples.json, and fig_tasks.tex and
fig_recall.tex, which lay the tiles out. Build each .tex with tectonic or
any LaTeX that has tgtermes; the papers' Figures 2 and 4 are those PDFs.

fig_tasks
    Lake's run 1, study drawings and the test drawings by another person,
    each test drawing under the study drawing it matches; instance run 1,
    all 20 drawings of one character; one test copy at every corruption
    level E3 reports, made by the same call the runs use.

fig_recall
    All 400 test copies of the 20 instance runs at occlusion 0.5 are
    recalled and sorted into four outcomes (right or wrong with the cue
    passed straight through, right or wrong after attractor dynamics);
    one copy is drawn from each outcome with random.Random(SEED), never
    chosen by eye, and the counts go into examples.json. Each copy goes
    through the clipped binary perforant path with the cue passed straight
    through and with CA3's attractor dynamics, exactly as
    perforant.study_and_score does for seed 0: the model seed for instance
    run i is i, and the corruption draw uses run number i. CA1's returned
    EC code is matched test-to-study to the studied drawings' codes; AHA's
    CA1 (PM) redraws pixels from the same CA3 state.

Example:
    python scripts/make_e3_examples.py
    cd figures/e3_examples && tectonic fig_tasks.tex && tectonic fig_recall.tex
"""


import argparse
import json
import random
import sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from trisynapsnet.data import corrupt, omniglot  # noqa: E402
from trisynapsnet.eval import ca1space, oneshot, perforant  # noqa: E402
from trisynapsnet.model.aha import AHA, AHAConfig, load_vc  # noqa: E402
from trisynapsnet.utils import resolve_device  # noqa: E402

SEED = 0            # the draw of examples
LEVEL = 0.5
SCALE = 4           # pixels per drawing pixel in a tile
CELL = 14           # pixels per CA3 cell in a grid tile
COLOURS = {         # off, right cell on, right cell missing, stray cell on
    0: (255, 255, 255), 1: (31, 78, 158), 2: (170, 199, 238), 3: (224, 123, 0)}


def drawing_tile(x, path):
    """A drawing as ink on paper: ink 1 is black."""
    a = x.detach().cpu().float().clamp(0, 1).squeeze().numpy()
    img = Image.fromarray(((1.0 - a) * 255).astype(np.uint8), mode="L")
    img = img.resize((a.shape[1] * SCALE, a.shape[0] * SCALE), Image.NEAREST)
    img.save(path)


def grid_tile(state, right, path, side=15, gap=2):
    """CA3's 225 cells as a 15 x 15 grid, coloured against the right pattern."""
    on = state.detach().cpu().flatten() > 0
    target = right.detach().cpu().flatten() > 0
    codes = torch.zeros_like(on, dtype=torch.long)
    codes[on & target] = 1
    codes[~on & target] = 2
    codes[on & ~target] = 3
    size = side * CELL + (side + 1) * gap
    img = Image.new("RGB", (size, size), (214, 218, 224))
    px = img.load()
    for i, c in enumerate(codes.tolist()):
        r, col = divmod(i, side)
        x0, y0 = gap + col * (CELL + gap), gap + r * (CELL + gap)
        for dx in range(CELL):
            for dy in range(CELL):
                px[x0 + dx, y0 + dy] = COLOURS[c]
    img.save(path)
    return {"right_on": int((on & target).sum()), "missing": int((~on & target).sum()),
            "stray": int((on & ~target).sum())}


HEAD = r"""\documentclass[border=4pt]{standalone}
\usepackage[T1]{fontenc}
\usepackage{tgtermes}
\usepackage{graphicx}
\usepackage{array}
\usepackage{xcolor}
\definecolor{right}{RGB}{31,78,158}
\definecolor{missing}{RGB}{170,199,238}
\definecolor{stray}{RGB}{224,123,0}
\setlength{\tabcolsep}{1.6pt}
\renewcommand{\arraystretch}{1.0}
\begin{document}
\begin{minipage}{7in}
\footnotesize
"""


def tile(name, width):
    return r"\parbox[c]{{{0}in}}{{\includegraphics[width={0}in]{{tiles/{1}.png}}}}".format(width, name)


def row(label, names, width, label_width):
    cells = [tile(n, width) for n in names]
    return r"\parbox[c]{%sin}{\raggedleft %s} & " % (label_width, label) + " & ".join(cells) + r" \\"


def tasks(META, out_dir):
    w, lw = 0.46, 0.95
    lines = [HEAD, r"\begin{tabular}{@{}r" + "c" * 10 + "@{}}"]
    lines.append(r"\multicolumn{11}{@{}l}{\textbf{A}\enspace One of Lake's runs: 20 characters studied once, and a new drawing of each by another person}\\[2pt]")
    for half in (0, 10):
        lines.append(row("Studied", ["lake_study_{:02d}".format(j) for j in range(half, half + 10)], w, lw))
        lines.append(row("Test, new drawer", ["lake_test_{:02d}".format(j) for j in range(half, half + 10)], w, lw) + r"[4pt]")
    info = META["instance_run_1"]
    alphabet = info["alphabet"].replace("_", " ")
    lines.append(r"\multicolumn{11}{@{}l}{\textbf{B}\enspace One instance run: all 20 drawings of one %s character, each by a different person}\\[2pt]" % alphabet)
    lines.append(row("Studied", ["inst_study_{:02d}".format(j) for j in range(10)], w, lw))
    lines.append(row("", ["inst_study_{:02d}".format(j) for j in range(10, 20)], w, lw) + r"[4pt]")
    lines.append(r"\end{tabular}")
    lines.append(r"\par\medskip")
    w2 = 0.62
    names = ["corrupt_clean"] + ["corrupt_occlusion_{:g}".format(x) for x in (0.3, 0.5, 0.7)] + \
            ["corrupt_noise_{:g}".format(x) for x in (0.3, 0.5, 0.7)]
    labels = ["Clean", "Occlusion 0.3", "Occlusion 0.5", "Occlusion 0.7", "Noise 0.3", "Noise 0.5", "Noise 0.7"]
    lines.append(r"\begin{tabular}{@{}" + "c" * 7 + "@{}}")
    lines.append(r"\multicolumn{7}{@{}l}{\textbf{C}\enspace One test copy from run B at each corruption level}\\[2pt]")
    lines.append(" & ".join(tile(n, w2) for n in names) + r" \\")
    lines.append(" & ".join(labels) + r" \\")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{minipage}")
    lines.append(r"\end{document}")
    (out_dir / "fig_tasks.tex").write_text("\n".join(lines) + "\n")


def recall(META, out_dir):
    w, lw = 0.62, 1.05
    total = META["copies"]
    lines = [HEAD, r"\begin{tabular}{@{}r" + "c" * 8 + "@{}}"]
    lines.append(r" & & & \multicolumn{3}{c}{Cue passed straight through} & \multicolumn{3}{c}{After attractor dynamics}\\")
    lines.append(r"\cmidrule{4-6}\cmidrule{7-9}" if False else "")
    head = ["", "Studied\\\\drawing", "Test copy,\\\\occlusion 0.5", "CA3 state\\\\(the cue)", "CA1's\\\\match",
            "AHA's CA1\\\\redraws", "CA3 state", "CA1's\\\\match", "AHA's CA1\\\\redraws"]
    lines.append(" & ".join(r"\parbox[b]{%sin}{\centering %s}" % (w + 0.04, h) if h else "" for h in head) + r" \\[2pt]")
    for n, ex in enumerate(META["examples"]):
        name = ex["outcome"][0].upper() + ex["outcome"][1:]
        label = r"%s\\(%d of %d)" % (name, META["counts"][ex["outcome"]], total)
        cells = [tile("ex{}_studied".format(n), w), tile("ex{}_copy".format(n), w)]
        marks = ["", "", ""]
        for tag in ("none", "settled"):
            mark = r"\textcolor{right}{right}" if ex[tag]["right"] else r"\textcolor{stray}{wrong}"
            cells += [tile("ex{}_ca3_{}".format(n, tag), w), tile("ex{}_ca1_{}".format(n, tag), w),
                      tile("ex{}_pm_{}".format(n, tag), w)]
            marks += ["", mark, ""]
        lines.append(r"\parbox[c]{%sin}{\raggedleft %s} & " % (lw, label) + " & ".join(cells) + r" \\")
        lines.append(" & ".join(marks) + r" \\[3pt]")
    lines.append(r"\end{tabular}")
    lines.append(r"\par\smallskip")
    lines.append(r"CA3 cells:\enspace \textcolor{right}{\rule{6pt}{6pt}} right cell on\quad "
                 r"\textcolor{missing}{\rule{6pt}{6pt}} right cell off\quad "
                 r"\textcolor{stray}{\rule{6pt}{6pt}} stray cell on")
    lines.append(r"\end{minipage}")
    lines.append(r"\end{document}")
    (out_dir / "fig_recall.tex").write_text("\n".join(x for x in lines if x) + "\n")


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--checkpoint", default=str(omniglot.DEFAULT_CHECKPOINT))
    p.add_argument("--data-dir", default=str(omniglot.DEFAULT_DATA))
    p.add_argument("--eval-data-dir", default=str(omniglot.LOCAL_DATA))
    p.add_argument("--out", default=str(REPO / "figures" / "e3_examples"))
    args = p.parse_args()
    out_dir = Path(args.out)
    tiles = out_dir / "tiles"
    tiles.mkdir(parents=True, exist_ok=True)
    torch.set_num_threads(2)
    meta = {"seed": SEED, "level": LEVEL}

    # ---- data and tasks
    lake = omniglot.load_runs(args.data_dir, 52, True)[0]
    for j in range(20):
        drawing_tile(lake["study"][j], tiles / "lake_study_{:02d}.png".format(j))
        test = int((lake["labels"] == j).nonzero()[0])
        drawing_tile(lake["recall"][test], tiles / "lake_test_{:02d}.png".format(j))
    runs = omniglot.load_instance_runs(args.eval_data_dir, 52, True, seed=0, split="evaluation")
    for j in range(20):
        drawing_tile(runs[0]["study"][j], tiles / "inst_study_{:02d}.png".format(j))
    meta["instance_run_1"] = runs[0]["info"]
    copy = runs[0]["recall"]
    drawing_tile(copy[0], tiles / "corrupt_clean.png")
    for kind in corrupt.KINDS:
        for level in perforant.LEVELS:
            out = corrupt.corrupt(copy, kind, level, 0, 0)
            drawing_tile(out[0], tiles / "corrupt_{}_{:g}.png".format(kind, level))

    # ---- one recall, step by step
    device = resolve_device("auto")
    config = AHAConfig(ca3_rule="covariance", dg_units=225, dg_k=5, ca1_rule="btsp",
                       ca1_units=2118, ca1_plateau_share=0.005)
    baseline = ca1space.background_reference()[0]
    aha = AHA(load_vc(args.checkpoint, device=device),
              config, device=device)
    aha.ca1_baseline = baseline
    aha.cache_vc(True)
    settings = json.loads((REPO / "results" / "e3_instance_official_225_5.json").read_text())["settings"]
    settings = {rule: dict(kw, share=perforant.modules.PP_SHARE) for rule, kw in settings.items()}
    meta["settings"] = settings
    meta["device"] = str(device)

    # Every copy of every instance run at this level, then one copy drawn at
    # random from each outcome: right or wrong with the cue passed straight
    # through, right or wrong after attractor dynamics.
    records, kept = [], {}
    for r, run in enumerate(runs):
        aha.reset(seed=r)
        st = aha.study(run["study"])
        ca1_state = aha.ca1.generator.get_state()
        stored = st["pc"]
        perforant.train_pm(aha, stored, st["pixels"])
        ca3s = perforant.build_ca3s(aha, stored)
        pps = perforant.build_pps(aha, st["vc"], stored, settings, baseline, r)
        test = corrupt.corrupt(run["recall"], "occlusion", LEVEL, 0, r)
        vc = aha.encode(test)
        _, states = perforant.arm_states(aha, ca3s, pps, vc)
        out = {}
        for arm, tag in (("pp_wil_none", "none"), ("pp_wil", "settled")):
            final = states[arm][1]
            aha.ca1.generator.set_state(ca1_state)
            with torch.no_grad():
                ca1 = aha.ca1_out(final)
                pm = aha.pm(final)
            out[tag] = {"final": final.cpu(), "pm": pm.cpu(),
                        "match": oneshot.min_mse_match(st["pm"], ca1, normalise=True).cpu()}
        kept[r] = {"stored": stored.cpu(), "pixels": st["pixels"].cpu(), "test": test.cpu(), **out}
        for j in range(20):
            label = int(run["labels"][j])
            records.append((r, j, label, bool(out["none"]["match"][j] == label),
                            bool(out["settled"]["match"][j] == label)))
    outcomes = {"both right": (True, True), "fixed by attractor dynamics": (False, True),
                "broken by attractor dynamics": (True, False), "both wrong": (False, False)}
    counts = {name: sum(1 for rec in records if rec[3:] == key) for name, key in outcomes.items()}
    meta["counts"] = counts
    meta["copies"] = len(records)
    rng = random.Random(SEED)
    examples = []
    for n, (name, key) in enumerate(outcomes.items()):
        r, j, label, _, _ = rng.choice([rec for rec in records if rec[3:] == key])
        k = kept[r]
        right = k["stored"][label]
        ex = {"outcome": name, "run": r + 1, "copy": j + 1, "label": label}
        drawing_tile(k["pixels"][label], tiles / "ex{}_studied.png".format(n))
        drawing_tile(k["test"][j], tiles / "ex{}_copy.png".format(n))
        for tag in ("none", "settled"):
            match = int(k[tag]["match"][j])
            ex[tag] = {"matched": match, "right": match == label,
                       "cells": grid_tile(k[tag]["final"][j], right,
                                          tiles / "ex{}_ca3_{}.png".format(n, tag))}
            drawing_tile(k["pixels"][match], tiles / "ex{}_ca1_{}.png".format(n, tag))
            drawing_tile(k[tag]["pm"][j], tiles / "ex{}_pm_{}.png".format(n, tag))
        examples.append(ex)
        print(name, ex, flush=True)
    print("counts", counts, "of", len(records), flush=True)
    meta["examples"] = examples
    (out_dir / "examples.json").write_text(json.dumps(meta, indent=1))
    tasks(meta, out_dir)
    recall(meta, out_dir)
    print("Wrote {}".format(omniglot.portable(out_dir)), flush=True)


if __name__ == "__main__":
    main()
