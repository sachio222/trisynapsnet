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

## Layout

```
trisynapsnet/model/modules.py   brain-region parts, including the CA3 rules
trisynapsnet/model/aha.py       the parts wired together
trisynapsnet/data/omniglot.py   Lake's runs, the validation runs and the instance runs
trisynapsnet/data/corrupt.py    occlusion and noise for test drawings
trisynapsnet/eval/oneshot.py    one-shot scoring and diagnostics
trisynapsnet/eval/evaluate.py   command line for one setting
scripts/                        E1 and E1b drivers, table and figure builders
docs/                           E1b's protocol
```

Code adapted from aha4 says so at the top of each file.

## License

MIT. See LICENSE.
