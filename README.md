# faithful-hippocampus

Jacob Krajewski, 2026. Working name.

This project builds an algorithm that learns from one example, using only circuitry and learning rules that have a counterpart in the brain. It starts from the layout of AHA and replaces one part at a time.

**AHA**, the Artificial Hippocampal Algorithm (Kowadlo, Ahmed and Rawlinson, [arXiv 1909.10340](https://arxiv.org/abs/1909.10340)), is a model of the hippocampus, the brain region that stores a new experience after one exposure. It is tested on Omniglot, a set of 1,623 handwritten characters from 50 alphabets. In each of Lake's 20 test runs, the model sees 20 characters once, then has to match 20 new drawings of them by a different person. Chance is 5%. Our reproduction of AHA lives in [aha4](https://github.com/sachio222/aha4). This project reuses aha4's frozen vision network and its copy of Omniglot, and it never changes aha4.

## Rules

Every part names its brain region and cell type. Every connection and learning rule follows these rules, or is labelled a stand-in:

- Each cell is excitatory or inhibitory, never both (Dale's principle).
- Connections are sparse, at the density measured for that pathway.
- Each synapse has its own weight. No weights are shared between positions.
- Firing rates are never negative.
- Cell counts keep the ratios measured in the rat.
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

## Install

Clone this repo next to aha4, so that `../aha4/checkpoints/vc_pretrained.pth.tar` and `../aha4/data` exist. aha4's `evaluate.py` downloads the data on its first run.

```
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest
```

Pass `--checkpoint` and `--data-dir` to point somewhere else.

## Run E1

One setting:

```
python -m fh.eval.evaluate --runs background --ca3-rule covariance --seeds 5 --normalise
```

The whole experiment, then the table in `results/bio_e1.md`:

```
PYTHON=.venv/bin/python scripts/run_bio_e1.sh
```

Each result is a JSON file in `results/` with every setting, per-seed scores and two diagnostics: whether CA3 settles back on a studied pattern when cued with that drawing, and how many DG cells two drawings of the same character share.

## Layout

```
fh/model/modules.py   brain-region parts, including the CA3 rules
fh/model/aha.py       the parts wired together
fh/data/omniglot.py   Lake's runs and the validation runs
fh/eval/oneshot.py    one-shot scoring and diagnostics
fh/eval/evaluate.py   command line for one setting
scripts/              E1 driver and table builder
```

Code adapted from aha4 says so at the top of each file.

## License

MIT. See LICENSE.
