# TrisynapsNet

Jacob Krajewski, 2026.

TrisynapsNet is named for the hippocampus's trisynaptic circuit, the loop from entorhinal cortex through the dentate gyrus and CA3 to CA1 that this model rebuilds.

This project builds an algorithm that learns from one example, using only circuitry and learning rules that have a counterpart in the brain. It starts from the layout of AHA and replaces one part at a time.

**AHA**, the Artificial Hippocampal Algorithm (Kowadlo, Ahmed and Rawlinson, [arXiv 1909.10340](https://arxiv.org/abs/1909.10340)), is a model of the hippocampus, the brain region that stores a new experience after one exposure. It is tested on Omniglot, a set of 1,623 handwritten characters from 50 alphabets. In each of Lake's 20 test runs, the model sees 20 characters once, then has to match 20 new drawings of them by a different person. Chance is 5%. Our reproduction of AHA lives in [aha4](https://github.com/sachio222/aha4). This project reuses aha4's frozen vision network and its copy of Omniglot, and it never changes aha4.

## Rules

Every part names its brain region and cell type. Every connection and learning rule follows these rules, or is labelled a stand-in:

- Each cell is excitatory or inhibitory, never both (Dale's principle).
- Connections are sparse, at the density measured for that pathway.
- Each synapse has its own weight. No weights are shared between positions.
- Firing rates are never negative.
- Cell counts keep the ratios measured in humans, scaled down, and use rodent values only where no human measurement exists.
- Learning rules are local: a synapse changes using only the activity of the two cells it connects, plus a signal the brain broadcasts widely, such as dopamine.

## AHA's parts

| Part | Brain region | What it does |
|---|---|---|
| VC | Visual cortex up to entorhinal cortex (EC) | Turns a drawing into a sparse code of pen-stroke features. Pretrained in aha4, then frozen. |
| DG | Dentate gyrus | Gives each drawing a new sparse pattern, 10 of 225 cells on, so similar drawings get different patterns. |
| CA3 | CA3, whose cells connect back to each other | Stores those patterns and settles a partial cue onto the closest stored one. |
| PR | The direct path from EC into CA3 | Learns to turn a drawing's vision code into its stored pattern, so a new drawing can find an old memory. |
| PM | CA1 | Learns to turn a stored pattern back into the drawing. |

## E1: a local learning rule in CA3

AHA's CA3 stores patterns with the pseudo-inverse rule, which computes every weight at once from all stored patterns. No synapse can do that. In aha4, switching CA3 to Hebbian learning, where a synapse strengthens when the cells on both sides fire together, dropped CA3's accuracy from 61.6% to 5.8%.

E1 tests whether that drop comes from locality or from how the patterns were stored. AHA's Hebbian rule turns each 0/1 DG pattern into -1/+1, so every pattern shares about 205 values of -1, and the weights mostly store that common part. E1 adds two local rules made for sparse 0/1 patterns:

- **Covariance rule** (Tsodyks and Feigel'man, 1988). A synapse grows when both cells fire and shrinks when only one does, like long-term potentiation and depression.
- **Clipped binary synapses** (Willshaw, Buneman and Longuet-Higgins, 1969). Each synapse is off until its two cells fire together, then on.

Recall keeps the k most driven cells at each step, k-winners-take-all, in place of feedback inhibition from interneurons. E1 also runs DG and CA3 at 225, 1,000 and 4,000 cells, at AHA's 4.4% of cells active and at 1%.

E1 keeps CA3's dense weight matrix and uses k-winners-take-all, both labelled stand-ins, so the learning rule is the only change. Experiment E2 adds real wiring and inhibitory cells.

Settings are chosen on 20 validation runs built from Omniglot's 30 background alphabets the same way as Lake's runs, so Lake's runs are scored only once at the end.

### E1 results

A local rule recovers CA3 from the collapse, but recurrent settling still costs accuracy. On Lake's 20 runs, 10 seeds, with normalised matching:

| CA3 | Cells, active | CA3 accuracy |
|---|---|---|
| Pseudo-inverse, AHA's rule | 225, 10 | 61.5% |
| Bipolar Hebbian, AHA's option | 225, 10 | 5.8% |
| Covariance | 225, 10 | 53.8% |
| Covariance | 1,000, 44 | 54.8% |
| Clipped binary synapses | 225, 10 | 54.2% |
| Clipped binary synapses | 1,000, 44 | 54.7% |
| No settling: the 10 most active PR cells | 225, 10 | 64.3% |

Cued with a studied drawing, CA3 with either local rule settles on exactly that drawing's stored pattern every time. With bipolar Hebbian it never does. So the collapse came from storing sparse patterns as -1/+1. Locality alone did not cause it.

The local rules still score about 7 points below the pseudo-inverse rule. Passing on the 10 most active PR cells without any settling scores 64.3%, above every rule that settles, so CA3's settling pulls some new drawings into the wrong memory. Letting the PR cue keep driving CA3 while it settles helps for the same reason: on the validation runs at 1,000 cells, CA3 accuracy rose from 61.4% to 67.8% at cue weight 1, and no settling at all scored 72.3%. At that weight the cue is about 25 times stronger than the recurrent input from the covariance weights, so most of the gain comes from settling less. Larger DG and CA3 moved CA3 accuracy by about a point. Every number is in `results/bio_e1.md`. E1b below traces the settling gap to tied scores between identical settled states.

## E1b: settling on a corrupted copy

E1 tested recognising a new drawing of a known character, and settling hurt. CA3 is meant for a different job: bringing back the same experience from a damaged cue. E1b tests that job with AHA's one-shot instance task. The model studies all 20 drawings of one character, then has to find each one again among the same 20, after the test copies are corrupted. Occlusion paints a circle of paper colour over the drawing, sized as a share of the image side. Noise replaces a share of the pixels with random grey levels. Lake's classification runs get the same corruption. Each corruption runs at 11 levels from none to 0.98, on the evaluation alphabets, 10 seeds, at AHA's size (225 cells, 10 on). The paper's protocol, and each choice it leaves open, are in `docs/e1b_protocol.md`.

The prediction, written before the runs: on the instance task, CA3 with settling beats the no-settling control under corruption, and the gap grows with corruption. On classification, no settling stays ahead.

### E1b results

The prediction failed on the instance task and held on classification. Matched the way the paper matches, no settling CA3 rule beat the no-settling control by more than 0.6 points at any corruption level on either task. On the instance task the gap first grows with corruption, then shrinks as every stage falls to chance. CA3 accuracy, in percent:

| Instance task | VC | PR | Pseudo-inverse | Covariance | Clipped binary | No settling |
|---|---|---|---|---|---|---|
| Occlusion 0.3 | 94.7 | 98.7 | 98.0 | 96.5 | 96.5 | 98.0 |
| Occlusion 0.5 | 63.5 | 86.1 | 79.6 | 71.9 | 72.6 | 82.6 |
| Occlusion 0.7 | 30.8 | 46.2 | 34.4 | 31.2 | 31.7 | 40.2 |
| Noise 0.1 | 93.0 | 95.0 | 89.2 | 83.9 | 84.1 | 91.8 |
| Noise 0.2 | 72.3 | 87.0 | 74.7 | 67.0 | 67.0 | 80.9 |
| Noise 0.3 | 43.8 | 66.8 | 46.8 | 40.7 | 40.6 | 58.3 |

| Classification task | VC | PR | Pseudo-inverse | Covariance | Clipped binary | No settling |
|---|---|---|---|---|---|---|
| Clean | 63.0 | 70.6 | 61.5 | 53.8 | 54.2 | 64.3 |
| Occlusion 0.5 | 35.3 | 43.2 | 34.7 | 31.6 | 31.4 | 37.8 |
| Noise 0.3 | 35.5 | 50.4 | 30.5 | 27.4 | 27.8 | 40.5 |

Paired by seed, the local rules trail no settling by up to 13.0 points under occlusion (at 0.6) and 17.7 under noise (at 0.3). They scored higher in no seed at any level from occlusion 0.2 to 0.9 or noise 0.1 to 0.6. The pseudo-inverse rule trails by up to 5.9 and 11.5 points. The background-alphabet instance runs show the same pattern.

Settling also failed to sharpen what CA1 rebuilds. Recall-loss is the mean squared error between CA1's reconstruction and the clean study drawing. The local rules and no settling share one CA1, and no settling gives equal or lower recall-loss at every level: 0.0251 against 0.0299 for the covariance rule at noise 0.4 on the instance task.

Matching direction explains the gap. AHA's paper scores study-to-test: each study drawing picks the nearest of the 20 test states. A cued memory works the other way: each test state picks the nearest stored pattern. Scored that way, the local rules and no settling differ by at most 0.4 points at every level of both tasks, with no consistent winner. With the covariance rule, settling ends on a stored pattern, almost always the one the nearest-pattern readout picks anyway: the two choose different memories for at most 2.6% of test drawings. Settling repeats a clean-up the readout already does. The study-to-test loss comes from collapse: when two corrupted drawings settle onto the same stored pattern, their states are identical, and a study drawing sees a tie between them. At occlusion 0.5, 25% of study drawings face such a tie. This also accounts for E1's settling gap: on clean classification matched test-to-study, the covariance rule scores 62.7% and no settling 62.8%. The pseudo-inverse rule does lose accuracy when scored this way, up to 9.6 points at noise 0.4.

Two more results stood out:

- The frozen vision network limits robustness to noise. On the instance task, raw pixels still match 99.7% at noise 0.4 while VC falls to 25.5%. The hippocampal stages start from VC's code and cannot recover what it drops.
- Matched study-to-test, PR, the direct path from EC to CA3, scores highest of the model's stages at every corruption level. Matched test-to-study, VC scores highest at most levels, and PR falls below it: 63.2% against VC's 67.3% on clean classification.

Every number is in `results/e1b.md`, the item-by-item counts are in `results/e1b_transitions.md`, and the figures are `figures/e1b_<task>_<corruption>.pdf`, with `_tts` for test-to-study matching.

## E1c: recall without a list of memories

E1b found that CA3's settling picks almost exactly the memory a nearest-memory lookup picks. That lookup compares the cue with a list of every stored memory and takes the one sharing the most active cells. For a cue with random damage it is the best decoder possible, so CA3 cannot beat it. The brain keeps no such list. E1c measures how close CA3 comes to that ideal lookup without one, as the number of stored memories (the load) grows and as cues lose more of their cells, and whether the pattern CA3 settles on helps CA1 rebuild the drawing.

The main test runs CA3 on its own, without the vision network or PR. CA3 stores N patterns, receives damaged copies of them as cues, and settles. The patterns are random, with exactly k of n cells on, or DG's patterns for one drawing each of N different Omniglot characters. Damage removes a share of a pattern's active cells, adds stray cells, or both. So that CA3 can start from a pattern with fewer than k cells, the local rules gained an option to begin settling from the cue as given. The default still begins from the cue's k most active cells, and E1b's stored scores repeat exactly with it. CA3 runs at 225, 1,000 and 4,000 cells with 4.4% on. A second test runs the full model: it studies 20, 100 or 200 drawings at once and recalls each from an occluded or noisy copy. Every choice is in `docs/e1c_protocol.md`.

The predictions, written before the runs:

1. At low load CA3 recalls exactly and matches the ideal lookup. Exact recall falls as load grows. The pseudo-inverse rule holds until the load nears the number of cells, then fails. The covariance rule holds longer than clipped binary synapses.
2. Larger networks hold proportionally more memories.
3. From partial cues, settling raises overlap with the right memory and lowers CA1's reconstruction error, with gains growing as more cells are removed, until load makes recall fail.
4. End to end, the gain from settling appears only where PR's output is partial or noisy.

### E1c results

**Exact recall** means CA3's final state is exactly the right stored pattern, with no list consulted. With random patterns at 225 cells, in percent, 10 seeds:

| Load | Pseudo-inverse, clean cue | Pseudo-inverse, 40% of cells removed | Covariance, clean | Covariance, 40% removed | Clipped binary, clean | Clipped binary, 40% removed | Ideal lookup, 40% removed |
|---|---|---|---|---|---|---|---|
| 20 | 100 | 98.0 | 100 | 100 | 100 | 100 | 100 |
| 100 | 100 | 66.6 | 99.2 | 95.1 | 99.9 | 99.0 | 100 |
| 150 | 100 | 0.2 | 92.1 | 74.3 | 97.9 | 85.7 | 100 |
| 200 | 100 | 0.0 | 74.8 | 40.8 | 91.2 | 41.4 | 100 |
| 300 | 100 | 0.0 | 31.4 | 6.2 | 42.2 | 0.3 | 100 |

The load at which exact recall from clean cues falls to 50%, read between tested loads on a log scale:

| Patterns | Cells | Covariance | Clipped binary | Pseudo-inverse, 40% removed |
|---|---|---|---|---|
| Random | 225 | 252 | 281 | 111 |
| Random | 1,000 | 795 | 777 | 327 |
| Random | 4,000 | 2,386 | 1,222 | 1,539 |
| Drawings | 225 | 180 | 264 | 110 |
| Drawings | 1,000 | 323 | 542 | 307 |
| Drawings | 4,000 | 346 | above 659 | above 659 |

The evaluation alphabets hold 659 characters, so drawings stop at that load.

- **Prediction 1 held for the local rules and partly failed for the pseudo-inverse rule.** At 20 memories, both local rules recall exactly from every damage tested, at every size, and score the same as the ideal lookup, even with 80% of the cells removed. The pseudo-inverse rule loses cues with 60% or more of their cells removed at every load: its state falls toward all cells off, with 11% exact recall at 60% removed and 0% at 80% for 20 drawings at 225 cells. With 40% removed it fails at a third to a half of the cell count, well before the load nears it. Clean cues stay exact up to the cell count only because every stored pattern is a fixed point of its weights. Clipped binary synapses held more memories than the covariance rule on drawings at every size and on random patterns at 225 cells. The covariance rule held more on random patterns at 4,000 cells.
- **Prediction 2 failed.** Larger networks hold more memories but fewer per cell. For the covariance rule on random patterns, the 50% load per cell falls from 1.12 to 0.79 to 0.60 across the three sizes, and for clipped binary synapses from 1.25 to 0.78 to 0.31.
- **Prediction 3 held for the local rules.** With 20 drawings stored, settling restores 99% to 100% of the pattern from cues missing up to 80% of their cells. CA1's error falls from 0.0157 to 0.0046 with 40% of cells removed and from 0.0344 to 0.0046 with 80% removed, so the gain grows with damage. At 200 drawings, past capacity, settling adds little overlap or loses some. For the pseudo-inverse rule the gain holds up to 40% removed and reverses beyond it.
- **Prediction 4 failed.** End to end, no settling rule beat passing PR's 10 most active cells straight on by more than 0.7 points at any load or corruption. Where PR's output was partial, settling did not complete it: at 20 drawings and occlusion 0.7, PR's top cells hold 53.5% of the right pattern and the settled state 54.6%. At 200 drawings CA3 is past its capacity for drawings, and the local rules lose up to 35 points, and 23 points even on clean drawings.

These results also stood out:

- **CA1 limits reconstruction above about 50 drawings.** AHA trains CA1 for 60 steps. CA1's error when given the exact stored pattern rises from 0.0046 at 20 drawings to 0.0226 at 50 and 0.0363 at 100. Predicting the mean stored drawing for every item, with no memory at all, scores about 0.044.
- **DG's drawing patterns are harder to store than random ones.** DG uses some cells much more often than others: the spread in how often each cell fires is about 2.5 times that of random patterns. The covariance rule suffers most, holding 346 drawings at 4,000 cells against 2,386 random patterns.
- **The pseudo-inverse rule at 4,000 cells stops short of a few cues.** Each of its 70 steps updates 356 random cells of 4,000, so any one cell goes unvisited with probability 0.15%. A cue needing about 71 cells switched back on then keeps at least one unchanged in about 10% of cases. That matches the 11% to 16% of cues with 40% removed that end one cell short at every load up to 1,000.

The ideal lookup identifies the right memory for almost every damaged cue tested, at every load. Below capacity, CA3 matches it without a list, and the pattern it fills in helps CA1, when CA3 receives a damaged copy of a stored pattern directly. In the full model, PR's output for a damaged drawing mixes missing cells with wrong ones, and settling added nothing at any load tested.

Every number is in `results/e1c.md`, and the figures are `figures/e1c_*.pdf`.

## Install

Clone this repo next to aha4, so that `../aha4/checkpoints/vc_pretrained.pth.tar` and `../aha4/data` exist. aha4's `evaluate.py` downloads the data on its first run.

```
git clone https://github.com/sachio222/aha4
git clone https://github.com/sachio222/trisynapsnet
cd trisynapsnet
```

```
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest
```

Pass `--checkpoint` and `--data-dir` to point somewhere else. E1b's instance runs need Omniglot's evaluation alphabets, which aha4 does not keep. The first instance run downloads them to `./data`, checks the archive's SHA-256, and unpacks them there. Pass `--eval-data-dir` to use another folder.

## Run E1

One setting:

```
python -m trisynapsnet.eval.evaluate --runs background --ca3-rule covariance --seeds 5 --normalise
```

The whole experiment, then the table in `results/bio_e1.md`:

```
PYTHON=.venv/bin/python scripts/run_bio_e1.sh
```

Each result is a JSON file in `results/` with every setting, per-seed scores and two diagnostics: whether CA3 settles back on a studied pattern when cued with that drawing, and how many DG cells two drawings of the same character share.

## Run E1b

One sweep, the instance task under noise at four levels:

```
python -m trisynapsnet.eval.evaluate --task instance --noise 0 0.3 0.6 0.9 --ca3-rule covariance --normalise
```

Each (seed, run) studies once and recalls every level. `--corruption-seed` fixes every circle and noisy pixel. The output JSON holds accuracy and recall-loss for each level.

The whole experiment, then `results/e1b.md` and the figures:

```
PYTHON=.venv/bin/python scripts/run_e1b.sh
PYTHON=.venv/bin/python scripts/e1b_transitions.py
```

## Run E1c

CA3 on its own, one rule and size, every load and damage:

```
python -m trisynapsnet.eval.ca3space --source random --units 1000 --rule covariance --seeds 10
python -m trisynapsnet.eval.ca3space --source drawings --split evaluation --units 225 --rule willshaw
```

The first drawings run encodes one drawing of every character once and keeps the codes in `data/cache`. The full model at a higher load:

```
python -m trisynapsnet.eval.endtoend --load 100 --kind occlusion --seeds 5
```

The whole experiment, then `results/e1c.md` and the figures:

```
PYTHON=.venv/bin/python scripts/run_e1c.sh
```

## Layout

```
trisynapsnet/model/modules.py   brain-region parts, including the CA3 rules
trisynapsnet/model/aha.py       the parts wired together
trisynapsnet/data/omniglot.py   Lake's runs, the validation runs and the instance runs
trisynapsnet/data/corrupt.py    occlusion and noise for test drawings
trisynapsnet/eval/oneshot.py    one-shot scoring and diagnostics
trisynapsnet/eval/evaluate.py   command line for one setting
trisynapsnet/eval/ca3space.py   E1c: CA3 on its own, cued with damaged patterns
trisynapsnet/eval/endtoend.py   E1c: the full model studying many drawings at once
scripts/                        E1, E1b and E1c drivers, table and figure builders
docs/                           E1b's and E1c's protocols
```

Code adapted from aha4 says so at the top of each file.

## License

MIT. See LICENSE.
