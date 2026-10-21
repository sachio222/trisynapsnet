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

- **Prediction 1 held for the local rules and partly failed for the pseudo-inverse rule.** At 20 memories, both local rules recall exactly from every damage tested, at every size, and score the same as the ideal lookup, even with 80% of the cells removed. The pseudo-inverse rule loses cues with 60% or more of their cells removed at every load: its state falls toward all cells off, with 11% exact recall at 60% removed and 0% at 80% for 20 drawings at 225 cells. With 40% removed it fails at a third to a half of the cell count, well before the load nears it. Clean cues stay exact up to the cell count only because every stored pattern is a fixed point of its weights. Clipped binary synapses held more memories than the covariance rule on drawings at every size and on random patterns at 225 cells. The covariance rule held more on random patterns at 4,000 cells (2,386 against 1,222); at 1,000 cells the two are close (795 against 777 with clean cues, 737 against 604 with 40% of cells removed).
- **Prediction 2 failed.** Larger networks hold more memories but fewer per cell. For the covariance rule on random patterns, the 50% load per cell falls from 1.12 to 0.79 to 0.60 across the three sizes, and for clipped binary synapses from 1.25 to 0.78 to 0.31.
- **Prediction 3 held for the local rules.** With 20 drawings stored, settling restores 99% to 100% of the pattern from cues missing up to 80% of their cells. CA1's error falls from 0.0157 to 0.0046 with 40% of cells removed and from 0.0344 to 0.0046 with 80% removed, so the gain grows with damage. At 200 drawings, past capacity, settling adds little overlap or loses some. For the pseudo-inverse rule the gain holds up to 40% removed and reverses beyond it.
- **Prediction 4 failed.** End to end, no settling rule beat passing PR's 10 most active cells straight on by more than 0.7 points at any load or corruption. Where PR's output was partial, settling did not complete it: at 20 drawings and occlusion 0.7, PR's top cells hold 53.5% of the right pattern and the settled state 54.6%. At 200 drawings CA3 is past its capacity for drawings, and the local rules lose up to 35 points, and 23 points even on clean drawings.

These results also stood out:

- **CA1 limits reconstruction above about 50 drawings.** AHA trains CA1 for 60 steps. CA1's error when given the exact stored pattern rises from 0.0046 at 20 drawings to 0.0226 at 50 and 0.0363 at 100. Predicting the mean stored drawing for every item, with no memory at all, scores about 0.044.
- **DG's drawing patterns are harder to store than random ones.** DG's codes for drawings overlap far more than random patterns do: drawings of different characters in one alphabet share 15 to 17% of their active cells, against 4.4% for random patterns (`results/bio_e1.md`). The covariance rule suffers most, holding 346 drawings at 4,000 cells against 2,386 random patterns.
- **The pseudo-inverse rule at 4,000 cells stops short of a few cues.** Each of its 70 steps updates 356 random cells of 4,000, so any one cell goes unvisited with probability 0.15%. A cue needing about 71 cells switched back on then keeps at least one unchanged in about 10% of cases. That matches the 7.6% to 15.5% of cues with 40% removed that miss exact recall at every load up to 1,000, each by about one cell.

The ideal lookup identifies the right memory for almost every damaged cue tested, at every load. Below capacity, CA3 matches it without a list, and the pattern it fills in helps CA1, when CA3 receives a damaged copy of a stored pattern directly. In the full model, PR's output for a damaged drawing mixes missing cells with wrong ones, and settling added nothing at any load tested.

Every number is in `results/e1c.md`, and the figures are `figures/e1c_*.pdf`.

## E1d: sparser codes

E1c ran DG and CA3 with 4.4% of their cells active, AHA's share, at every size, and found that the number of patterns CA3 holds per cell falls as the network grows. Theory for sparse associative memories expects that when the share of active cells stays fixed. It expects capacity per cell to hold or grow only when the number of active cells, k, grows about with the logarithm of the cell count, n. In rat dentate gyrus about 2% of granule cells are active; no human measurement exists. E1d asks whether CA3's capacity per cell stops falling with size once codes are that sparse.

E1d reruns E1c's test of CA3 on its own with four shares of active cells in DG and CA3: 4.4%, 2%, 1%, and a log-scaled code, k = round(2.007 × log2 n), which puts 20 cells on at 1,000 cells (2%), 24 at 4,000 and 28 at 16,000. At 225 cells, 2% rounds to 5 active cells, 1% is raised to the floor of 3, and the log-scaled code has 16, denser than AHA's 10. CA3 runs at 225, 1,000 and 4,000 cells with random patterns and with DG's patterns for drawings, and at 16,000 cells with random patterns. Loads climb a grid, each a factor of at most 5/3 above the last, until exact recall falls below 5%. The **50% load** is the load where exact recall falls through 50%, read between the two tested loads around it; over n it gives the **load per cell**. Damage, cues, rules and scoring are E1c's. At 4.4% the runs store E1c's own random patterns and give E1c's 50% loads, except where the finer grid reads one more closely (388 against 327 for the pseudo-inverse rule at 1,000 cells). A second test reruns E1's and E1b's full-model runs at 225 cells with 5 active. Every choice is in `docs/e1d_protocol.md`.

The predictions, written before the runs:

1. Capacity per cell rises as codes get sparser, at every size.
2. With log-scaled codes, capacity per cell holds or grows with size, instead of falling as in E1c.
3. Clipped binary synapses gain the most from sparser codes; at the sparsest codes they beat the covariance rule.
4. DG's codes for drawings stay more uneven than random patterns at every sparsity, so drawings stay below random patterns in capacity.
5. One-shot classification and instance accuracy change by less than 3 points, since PR, not CA3, sets them.

### E1d results

With the log-scaled code, capacity per cell grows with size for both local rules, and nearly triples with every fourfold rise in cells beyond 1,000. At any fixed share it still falls. Load per cell at 50% exact recall from clean cues, random patterns:

| Share active | Rule | 225 cells | 1,000 cells | 4,000 cells | 16,000 cells |
|---|---|---|---|---|---|
| 4.4% | Covariance | 1.12 | 0.79 | 0.60 | 0.49 |
| 4.4% | Clipped binary | 1.25 | 0.78 | 0.31 | 0.11 |
| 2% | Covariance | 1.93 | 1.82 | 1.41 | 1.08 |
| 2% | Clipped binary | 2.00 | 2.37 | 1.01 | 0.51 |
| 1% | Covariance | 2.80 | 3.61 | 2.97 | not run |
| 1% | Clipped binary | 1.43 | 4.79 | 3.13 | not run |
| Log-scaled | Covariance | 0.70 | 1.82 | 5.14 | 14.6 |
| Log-scaled | Clipped binary | 0.73 | 2.37 | 6.36 | 23.5 |

At 16,000 cells the log-scaled code holds 232,927 patterns with the covariance rule and 376,462 with clipped binary synapses, against 7,813 and 1,727 at 4.4%. Those two runs have one seed each; elsewhere the 50% loads of single seeds lie within 6% of their mean.

- **Prediction 1 held for the covariance rule and partly failed for the other two.** The covariance rule gains at every size from 4.4% to 2% to 1%: from 0.60 to 1.41 to 2.97 per cell at 4,000 cells. Clipped binary synapses gain at 1,000 cells and above, but at 225 cells 3 active cells hold fewer patterns than 5 (1.43 against 2.00 per cell). The pseudo-inverse rule, scored from cues missing 40% of their cells, barely moves at 225 and 1,000 cells (0.46 to 0.51 per cell) and gains modestly at 4,000 (0.38 to 0.44) and 16,000 cells (0.24 at 4.4%, 0.34 at 2%, 0.40 at 1%).
- **Prediction 2 held for the local rules.** Covariance goes 0.70, 1.82, 5.14, 14.6 per cell from 225 to 16,000 cells, and clipped binary synapses 0.73, 2.37, 6.36, 23.5. The pseudo-inverse rule stays flat at 0.51, 0.44 and 0.44 up to 4,000 cells. Fixed shares keep falling: at 2%, covariance drops from 1.93 to 1.08 per cell and clipped binary synapses from 2.37 at 1,000 cells to 0.51 at 16,000.
- **Prediction 3 held from 1,000 cells up and failed at 225.** From 4.4% to 1% at 4,000 cells, clipped binary synapses gain tenfold (0.31 to 3.13) and the covariance rule fivefold (0.60 to 2.97). At the sparsest codes clipped binary synapses lead: 6.36 against 5.14 per cell at 4,000 cells with the log-scaled code, 23.5 against 14.6 at 16,000, and 4.79 against 3.61 at 1% of 1,000. At 225 cells with 3 active cells they fall well behind (1.43 against 2.80), and from a cue missing 40% of its cells they recall only 69% of 20 stored patterns exactly.
- **Prediction 4 held for the local rules.** DG's cell use on evaluation-alphabet drawings is 2.2 to 3.2 times as uneven as random patterns at every share and size, measured as the spread over the mean of how many stored drawings each cell joins. Wherever a drawing run fell below 50% exact recall within the 659 characters available, it held fewer patterns than random ones: 380 against 2,386 for covariance at 4.4% of 4,000 cells, 313 against 449 for clipped binary synapses at 2% of 225. Many sparse runs on drawings never fell below 50%, so there the comparison stays open. The pseudo-inverse rule holds about as many drawings as random patterns (106 against 111 at 225 cells).
- **Prediction 5 partly failed.** At 2%, the settling rules' CA3 accuracy on Lake's runs rose by 3.1 to 3.5 points, just past the 3-point bound, in both matching directions: covariance from 53.8% to 57.2% matched study-to-test, and from 62.7% to 65.9% test-to-study. PR rose less, from 70.6% to 72.5% study-to-test. On the instance task under occlusion and noise up to 0.5 the settling rules moved by 1.5 points or less. Passing PR's k most active cells on without settling lost up to 10.6 points matched study-to-test (58.3% to 47.8% at noise 0.3), because 5 cells carry less than 10, but matched test-to-study it stayed within 0.8 points on the instance task and gained 3.1 on Lake's runs. On the background-alphabet validation runs, classification moved the other way, by -1.2 and -1.5 points.

These results also stood out:

- **The pseudo-inverse rule at 16,000 cells misses cells it never updates.** At 4.4% only 65% of cues missing 40% of their cells come back exactly, even with 20 patterns stored. Each of its 70 steps updates 1,422 random cells of 16,000, so a cell goes unvisited with probability 0.15%, and a cue needing 284 cells switched back on keeps at least one unchanged in about 35% of cases. Sparser codes need fewer cells switched on, which explains part of that rule's gain at 16,000 cells.
- **The pseudo-inverse rule at 16,000 cells did not finish.** Each load needs the pseudo-inverse of a load-by-16,000 matrix, and with two such runs at once the machine ran out of memory. Its 2% and 1% values use 4 and 2 seeds; the log-scaled code was not run. A later attempt at the remaining local-rule runs at 16,000 cells stopped on swap growth, so the 1% runs there are missing.

Summed over runs, with up to three running at once on one machine, the CA3 runs took 8.7 hours, 6.8 of them at 16,000 cells (about 21 minutes per seed for the log-scaled code), and the full-model runs 2.7 hours. Every number is in `results/e1d.md`, and the figures are `figures/e1d_*.pdf`.

## E4: one-shot learning in CA1

CA1 is the hippocampal field after CA3. In the brain it sends the memory back to entorhinal cortex (EC), the cortex that feeds the hippocampus. In AHA, the part called PM plays CA1: a small network trained by backpropagation, 60 optimiser steps over the study set, to rebuild a drawing's pixels from its stored CA3 pattern, a procedure with no known counterpart in the brain. E1c also found that PM's error from the exact stored pattern rises from 0.0046 at 20 drawings to 0.0363 at 100, which looked like a limit on how many drawings CA1 can hold.

E4 replaces PM with a CA1 that learns each drawing in one presentation, using a rule measured in CA1 neurons. That rule is behavioural timescale synaptic plasticity (BTSP). A plateau potential, a long calcium spike in a CA1 cell's dendrites, changes every synapse from a CA3 cell that was active within a few seconds of it, in a single trial (Bittner and colleagues, 2017). The change depends on the synapse's present weight: weak synapses strengthen and strong ones weaken (Milstein and colleagues, 2021). Plateaus are set off by input from EC layer III (Grienberger and Magee, 2022). Wu and Maass (2025) reduced the rule to on/off synapses: when a CA3 input is active near a plateau, the synapse flips with probability 0.5, from off to on or from on to off. E4 uses that rule as published.

In E4's CA1, each drawing's EC code, the frozen vision network's 20,449 numbers, decides which CA1 cells get a plateau. Their synapses from the drawing's active CA3 cells then flip as the rule says. CA1 sends the memory back to EC through synapses that grow with the product of CA1 and EC activity, learned in the same presentation. At recall, a CA3 state drives CA1, the most driven CA1 cells fire, and they return an EC code. CA1 runs at two sizes from measured cell counts: 2,118 cells, the human ratio of CA1 to CA3 cells applied to AHA's 225 CA3 cells, and 375 cells, the rat ratio.

The returned EC code is scored by identification: the stored EC code closest to it, by cosine similarity, should be the right drawing's. Chance is 1 over the number stored. The comparison network, named before the runs, is PM's network and training with the EC code as its target instead of pixels. The rule has 10 settings. Two were chosen on Omniglot's background alphabets: the share of CA1 cells that get a plateau per drawing (0.005 at 2,118 cells, the measured value, and 0.01 at 375), and measuring each cell's plateau drive against its drive from the mean background EC code, a stand-in for feedforward inhibition. Every choice and the quoted rule are in `docs/e4_protocol.md`.

The predictions, written before the runs:

1. At 20 drawings, BTSP CA1 identifies the right drawing as often as the comparison network, within 3 points, after one presentation.
2. Past 50 drawings BTSP holds up better: higher identification at 100 and 200 drawings.
3. With CA3 completing partial cues, BTSP CA1's output from a partial cue approaches its output from the exact pattern, below CA3's capacity.
4. On Lake's runs, accuracy at the CA1 stage stays within 3 points of the CA3 stage.

### E4 results

The planned comparison network learns nothing. EC codes are about 19 times smaller than pixels, so PM's L2 penalty, which pulls every weight toward zero, outweighs the error signal, and the network returns nearly the same code for every drawing. It identifies 5.0% at 20 drawings, chance. Predictions 1 and 2 against it say nothing about BTSP. Two variants of it were run: one without the L2 penalty, the informative comparison, and one with the EC target scaled up 19.3 times, as a check.

Identification from the exact stored CA3 pattern, in percent, evaluation alphabets, 225 CA3 cells, 10 seeds:

| Drawings stored | BTSP, 2,118 cells | BTSP, 375 cells | Backprop into EC as planned | Backprop into EC, no L2 penalty | Backprop into EC, target scaled |
|---|---|---|---|---|---|
| 20 | 99.0 | 97.0 | 5.0 | 100.0 | 41.0 |
| 50 | 98.6 | 92.0 | 2.0 | 99.8 | 2.6 |
| 100 | 94.8 | 72.4 | 1.0 | 81.4 | 1.0 |
| 200 | 65.1 | 35.3 | 0.5 | 34.8 | 0.5 |
| 500 | 5.3 | 3.5 | 0.3 | 3.6 | 0.3 |

- **Prediction 1.** Against the planned network it failed in the letter, since BTSP is about 94 points ahead, not within 3. Against the network without the L2 penalty it held: 99.0 against 100.0 at 2,118 cells, and 97.0 against 100.0 at 375 cells, exactly 3 points. Against the scaled target it failed, with BTSP far ahead of its 41.0.
- **Prediction 2.** Against the planned network it held, uninformatively. Against the network without the L2 penalty it held at 2,118 cells, 94.8 and 65.1 against 81.4 and 34.8 at 100 and 200 drawings, and failed at 375 cells, 72.4 against 81.4 at 100 drawings and level at 200. Against the scaled target it held at both sizes.
- **Prediction 3 held.** At 2,118 cells and 20 drawings, BTSP identifies 99.0% from the exact pattern, and 99.5% and 99.0% from cues missing 40% and 80% of their active cells once CA3 settles them with the covariance rule, against 96.5% and 89.0% from the raw cues. At 50 drawings settling still restores 98.6% from 40% removed. As CA3 nears its capacity the gap opens with CA3's exact recall, and at 200 drawings settling hurts. The completion is CA3's: the network without the L2 penalty gains the same way.
- **Prediction 4 held.** On Lake's runs the CA1 stage stays within 2.1 points of CA3 at both sizes and in both matching directions: 55.8% against 53.8% at 2,118 cells matched AHA's way.

Three more results stood out:

- **PM's rising error comes from its L2 penalty, not from CA1's capacity.** With E1c's drawings, seeds and starting weights, PM repeats E1c's errors exactly (0.0046, 0.0226 and 0.0363 at 20, 50 and 100 drawings) and identifies 13.8% of drawings at 100. The same network and the same 60 steps without the L2 penalty reach errors of 0.0006, 0.0012 and 0.0020, and identify 99.5% of drawings even at 500. It still learns by backpropagation over many steps, which BTSP does not need.
- **BTSP gains most from a larger CA3.** At 1,000 CA3 cells with 44 active, BTSP with 9,412 CA1 cells identifies 99.3% at 200 drawings and 39.7% at 500. The network without the L2 penalty identifies 3.7% and 0.2%.
- **The rat-sized CA1 struggles with alike drawings.** On the instance task, where all 20 drawings show one character, 375-cell BTSP falls up to 7.1 points below CA3, with only 4 plateau cells per drawing. At 2,118 cells it stays within 1.4 points.

BTSP stores 20 drawings in about 1 second on the CPU, one presentation each, against about 2.3 seconds for the backpropagation networks' 60 steps. At 500 drawings the 2,118-cell BTSP CA1 takes 10.1 seconds against 8.2, so one presentation is not always faster in wall time. Every number is in `results/e4.md`, and the figures are `figures/e4_identification.pdf` and `figures/e4_partial.pdf`.

## E3: a perforant path learned in one shot

E1b and E1c found that CA3's settling never helps end to end in AHA's layout: PR hands CA3 a full pattern already near the right memory, so nothing is left to complete. In the brain, CA3 gets two inputs from the cortex. The mossy fibres from DG are few and strong, and Treves and Rolls (1992) proposed that they force a new pattern onto CA3 cells during learning. The perforant path from EC layer II is many weak synapses that change when the cells on both sides fire together, and they proposed that it starts recall. E3 replaces PR with such a perforant path, which removes the last backpropagation from the hippocampal pathway, and asks whether settling then helps.

Each CA3 cell connects to a fixed random 710 of the 20,449 EC units. That is the share of rat EC layer II cells one rat CA3 cell hears from, 3,750 synapses (Treves and Rolls, 1992) over 108,000 cells (Arellano and Rakic, 2026), applied to the model's EC. During study, while DG's pattern holds CA3, each synapse learns in one presentation, with clipped binary synapses (a synapse turns on when its EC unit and its CA3 cell are active together) or with the covariance rule. At recall the perforant input alone picks the cue: the k most driven CA3 cells, or, with an E%-max threshold, only those within a set share of the most driven cell, so a cue can have fewer than k cells. E%-max is a form of feedback inhibition proposed by de Almeida, Idiart and Lisman (2009). CA3 then settles from the cue, or the cue goes straight on, and E4's one-shot CA1 returns an EC code. Three settings were chosen on Omniglot's background alphabets: normalised input and E%-max 0.3 for clipped binary synapses, and normalised input with the plain k most driven cells for the covariance rule. DG and CA3 run with 5 of 225 cells active (2%, E1d's setting), and with 10 (4.4%) as a check. Every choice and source is in `docs/e3_protocol.md`.

The predictions, written before the runs:

1. The perforant cue is weaker than PR's: without settling, accuracy on both tasks falls below the PR model's.
2. With the perforant path, settling helps end to end: on the instance task, scored test-to-study, settling beats no settling by at least 5 points at some corruption level below capacity.
3. On Lake's runs, the fully local model scores below the PR model.
4. CA1-stage accuracy stays within 3 points of the CA3 stage.

### E3 results

With the perforant path, settling helps once CA1 reads its result. On the instance task, matched test-to-study, CA1 returns the right drawing's code this often, in percent, 10 seeds:

| CA3 input | Settling | Clean | Occlusion 0.3 | Occlusion 0.5 | Occlusion 0.7 | Noise 0.3 |
|---|---|---|---|---|---|---|
| Perforant, covariance | none | 35.4 | 29.2 | 20.6 | 13.5 | 11.2 |
| Perforant, covariance | yes | 53.6 | 45.3 | 31.9 | 19.7 | 16.5 |
| Perforant, clipped binary | none | 98.8 | 80.0 | 43.7 | 16.9 | 8.7 |
| Perforant, clipped binary | yes | 99.1 | 91.7 | 61.1 | 25.8 | 10.9 |
| PR | none | 99.2 | 96.3 | 76.0 | 35.2 | 46.3 |
| PR | covariance | 99.2 | 96.6 | 77.7 | 36.5 | 48.9 |

On Lake's runs, CA1 stage, the fully local model with clipped binary synapses scores 25.6% matched study-to-test and 29.8% test-to-study, against 58.7% and 65.8% for PR with covariance settling.

- **Prediction 1 partly held.** On Lake's runs the perforant cue without settling scores 37.7% (clipped binary) and 33.5% (covariance) at CA3 matched study-to-test, against 61.0% for PR's top cells; under noise 0.3 on the instance task, 10.4% and 15.7% against 48.8% test-to-study. On clean and lightly occluded drawings of the instance task the clipped binary cue matches PR: 99.9% against 100.0% clean, and 76.1% against 75.5% at occlusion 0.5 matched study-to-test.
- **Prediction 2 held at the CA1 stage and failed at the CA3 stage.** Settling lifts CA1 by 18.2 points on clean drawings with the covariance rule and by 17.4 points at occlusion 0.5 with clipped binary synapses, higher in all 10 seeds. Scored at CA3 itself it adds at most 1.4 points. Matching a CA3 state against the stored patterns already finds the nearest memory, so the partial cue scores well there. CA1 reading the same partial cue returns the right code far less often (80.0% against 93.0% at occlusion 0.3), and the settled pattern restores it (91.7%).
- **Prediction 3 held.** The fully local model trails PR by 33 to 38 points on Lake's runs at CA1, in both matching directions and with either rule.
- **Prediction 4 held for every arm that settles and for PR, and failed for perforant cues passed on without settling.** The settling arms and PR stay within 2.8 points of CA3. Unsettled perforant cues lose up to 20.1 points at CA1, the same weakness settling repairs.

These results also stood out:

- **The perforant path stores the drawing, not the character.** On the instance task the clipped binary cue holds 99.5% of the right pattern's cells for clean drawings. On Lake's runs, where a different person drew the test character, the stored pattern nearest the cue is the right one for 30.2% of drawings, against 67.3% for the whole vision code matched directly. Connecting each CA3 cell to every EC unit, a diagnostic added after the runs on background alphabets, lifts the best perforant arm from 39.0% to 49.6% there, against 68.3% for PR, so sparse wiring explains part of that gap and one-shot learning the rest.
- **The gain needs CA3 below capacity.** In E1c's load runs, settling's largest gain at CA1 on clean and occluded drawings is 15.3 and 17.4 points at 20 and 50 drawings, 6.4 at 100, and none at 200, where exact recall of clean drawings after clipped binary settling has fallen to 47.1%.
- **Pixel noise defeats the perforant cue sooner than PR.** At noise 0.3 the clipped binary cue holds 11.1% of the right cells, PR's top cells 49.2%.
- **More active cells change little.** At 4.4% the perforant arms score 26.7% to 30.6% on Lake's runs at CA3 matched test-to-study, and settling still lifts CA1 by up to 15.4 points on the instance task.

All E3 runs took 62 minutes of process time, at most two at once. Every number is in `results/e3.md`.

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

## Run E1d

CA3 on its own at one share of active cells, one rule and size, climbing the load grid:

```
python -m trisynapsnet.eval.sparsecodes --source random --units 4000 --sparsity log --rule willshaw --seeds 5
python -m trisynapsnet.eval.sparsecodes --source drawings --split evaluation --units 1000 --sparsity 2 --rule covariance
```

`--sparsity` takes 4.4, 2, 1 or log. A partial result file resumes from its last finished seed. The whole experiment, then `results/e1d.md` and the figures:

```
PYTHON=.venv/bin/python JOBS=2 scripts/run_e1d.sh
```

Run phase C, 16,000 cells, with `JOBS=1`: each process holds two 16,000 by 16,000 matrices. When aha4 does not sit next to this repo, as in a git worktree, set `TSN_AHA4` to its folder.

## Run E4

CA1 on its own, every CA1 arm, one CA1 size:

```
python -m trisynapsnet.eval.ca1space --split evaluation --units 225 --ratios human --shares 0.005 --seeds 10
```

It reads the vision codes E1c cached in `data/cache`; pass `--cache-dir` to use another folder. `--active-share` sets the share of active DG and CA3 cells. Lake's runs with one-shot CA1:

```
python -m trisynapsnet.eval.evaluate --ca3-rule covariance --normalise --ca1-rule btsp \
    --ca1-units 2118 --ca1-plateau-share 0.005 --also-match test-to-study
```

The whole experiment, then `results/e4.md` and the figures. Phase A, on background alphabets, picks the plateau shares that the later phases take:

```
PYTHON=.venv/bin/python scripts/run_e4.sh A
PYTHON=.venv/bin/python SHARE_HUMAN=0.005 SHARE_RAT=0.01 scripts/run_e4.sh B   # then C, D and E
python scripts/make_e4_table.py
```

Set `TSN_AHA4` to aha4's folder when it does not sit next to this repo, as in a git worktree.

## Run E3

Every arm from one study, on Lake's runs or at one load:

```
python -m trisynapsnet.eval.perforant --task classification --seeds 10 --wil-normalise --wil-emax 0.3 --cov-normalise
python -m trisynapsnet.eval.perforant --task load --load 100 --seeds 5 --wil-normalise --wil-emax 0.3 --cov-normalise
```

A result file is written after every seed, and a rerun picks up after the last finished seed. The whole experiment, then `results/e3.md`. Phase A, on background alphabets, picks the perforant settings the later phases take:

```
PYTHON=.venv/bin/python scripts/run_e3.sh A
python scripts/make_e3_table.py --select
PYTHON=.venv/bin/python WIL="--wil-normalise --wil-emax 0.3" COV="--cov-normalise" JOBS=2 scripts/run_e3.sh B   # then C, D and E
PYTHON=.venv/bin/python scripts/run_e3.sh status
python scripts/make_e3_table.py
```

## Layout

```
trisynapsnet/model/modules.py   brain-region parts, including the CA3 rules, the perforant path and one-shot CA1
trisynapsnet/model/aha.py       the parts wired together
trisynapsnet/data/omniglot.py   Lake's runs, the validation runs and the instance runs
trisynapsnet/data/corrupt.py    occlusion and noise for test drawings
trisynapsnet/eval/oneshot.py    one-shot scoring and diagnostics
trisynapsnet/eval/evaluate.py   command line for one setting
trisynapsnet/eval/ca3space.py   E1c: CA3 on its own, cued with damaged patterns
trisynapsnet/eval/endtoend.py   E1c: the full model studying many drawings at once
trisynapsnet/eval/sparsecodes.py  E1d: E1c's CA3 test at sparser codes and larger loads
trisynapsnet/eval/ca1space.py   E4: CA1 on its own, returning EC codes against load
trisynapsnet/eval/perforant.py  E3: every arm, PR or perforant path, with and without settling
scripts/                        E1 to E1d, E3 and E4 drivers, table and figure builders
docs/                           E1b's, E1c's, E1d's, E3's and E4's protocols
```

Code adapted from aha4 says so at the top of each file.

## License

MIT. See LICENSE.
