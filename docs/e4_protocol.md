# E4 protocol

E4 asks whether CA1 can learn each drawing in one presentation with a rule measured in CA1 neurons, and whether that removes the capacity limit E1c found in AHA's CA1. This file quotes the published rule E4 implements, counts every free parameter, and lists each choice. The choices went into code and tests before the evaluation runs. Two were chosen on background-alphabet drawings, as items 9 and 10 describe.

## Terms

- **EC** is the entorhinal cortex. In this model, a drawing's EC code is the frozen vision network's output, 20,449 numbers, all zero or positive.
- **DG** (dentate gyrus) gives each drawing a sparse pattern, 10 of 225 cells on. **CA3** stores DG's patterns and settles a damaged pattern back onto a stored one.
- **CA1** is the hippocampal field after CA3. Its job in the brain is to send the memory back to EC. In AHA, the part called PM plays CA1: a two-layer network trained by backpropagation, 60 steps of the Adam optimiser on the study set, to rebuild the drawing's pixels from its stored CA3 pattern.
- **Load** is the number of drawings stored at once.
- **BTSP**, behavioural timescale synaptic plasticity, is the one-trial plasticity found in CA1 pyramidal cells, described below.
- A **plateau potential** is a long dendritic calcium spike in a CA1 cell, lasting tens to hundreds of milliseconds.
- **k-winners-take-all** keeps the k most driven cells on and turns the rest off. It stands in for feedback inhibition, as in E1.

## The published rule

| Source | What it says |
|---|---|
| Bittner and colleagues 2017, *Science*, 10.1126/science.aan3846 | "Place fields could be produced in vivo in a single trial by potentiation of input that arrived seconds before and after complex spiking." |
| Milstein and colleagues 2021, *eLife*, 10.7554/eLife.73046 | "this anti-correlation actually results from a dependence on current synaptic weight such that weak inputs potentiate and strong inputs depress." Their Eq. 1: dW/dt = (W_max − W) k⁺ q⁺(ET·IS) − W k⁻ q⁻(ET·IS). |
| Grienberger and Magee 2022, *Nature*, 10.1038/s41586-022-05378-6 | "previous in vitro and in vivo work has shown that EC3 input regulates both the probability and duration of plateau potentials", and "learning-related changes in the hippocampus are produced by synaptic plasticity directed by an instructive signal from the EC3". |
| Wu and Maass 2025, *Nature Communications*, 10.1038/s41467-024-55563-6 | "When an input pattern x arrives within the time interval from -6 to 4s relative to the onset of a plateau potential in a neuron, its synaptic weights are increased with probability 0.5 (provided they are not yet at their maximal value of 1), and also decreased with probability 0.5 (provided they are not yet at their minimal value of 0)." Their Eq. 1: Δw_i = +1 if x_i = 1 and w_i = 0; −1 if x_i = 1 and w_i = 1; otherwise unchanged. Their theory applies it "independently for each synapse with a probability of 0.5." |

E4 implements Wu and Maass's binary rule, their Eq. 1, applied independently at each synapse. It is the binary limit of Milstein's weight-dependent rule: a weak synapse can only potentiate and a strong one can only depress. Milstein's continuous form was not run.

Wu and Maass also return the memory to the input layer through feedback synapses that learn in the same presentation: "if both the pre-and postsynaptic neuron of a feedback connection assume value 1, the synaptic weight of this feedback connection is incremented by 1". E4's return to EC follows that step without their ceiling of 1, because EC codes are graded.

## Choices

### CA1

1. **Cells.** CA1 runs at two sizes, each a measured ratio of CA1 to CA3 pyramidal cells applied to AHA's 225 CA3 cells: the human ratio, 16 million to 1.7 million (West and Gundersen 1990; Watson and colleagues 2025), gives 2,118 cells; the rat ratio, 350,000 to 210,000 (Arellano and Rakic 2026), gives 375. At 1,000 CA3 cells the same ratios give 9,412 and 1,667.
2. **CA3-to-CA1 synapses.** Each CA3 cell synapses on each CA1 cell with probability 0.6, Wu and Maass's value, drawn once per seed. Every weight starts at 0 and is 0 or 1. Rat anatomy suggests fewer: about 12,000 to 21,000 CA3 synapses per CA1 cell from 210,000 CA3 cells (Bezaire and colleagues 2016; Romani and colleagues 2024). E4 keeps the published value so the rule runs as published.
3. **Plateaus.** Each drawing's EC code drives every CA1 cell through fixed random weights, uniform between 0 and 1, one per EC unit and CA1 cell, drawn once per seed. The m most driven cells plateau, where m is the plateau share times the CA1 cell count, rounded, and at least 1. Taking the top m stands in for a plateau threshold.
4. **One presentation per drawing.** Drawings arrive one at a time in a fixed order. Each plateau's window covers its own drawing and none of its neighbours, as if drawings arrived more than 10 seconds apart.
5. **The update.** For each CA1 cell with a plateau, every synapse from an active CA3 cell flips (0 to 1, or 1 to 0) with probability 0.5, independently. Synapses from inactive CA3 cells, and every synapse of a cell without a plateau, keep their weights.
6. **Recall.** Each CA1 cell sums its input from active CA3 cells through its binary weights. k-winners-take-all keeps the m most driven cells. Sums are whole numbers, so ties are common; they are broken at random. Recall changes no weight.
7. **The return to EC.** Right after a drawing's BTSP update, CA1 responds to that drawing's CA3 pattern by the recall step in item 6. Each CA1-to-EC synapse then grows by its CA1 cell's activity times its EC unit's activity. Weights start at zero and have no ceiling. The returned code for any CA1 activity is that activity times these weights. Every connection from CA1 to EC exists, a dense stand-in.
8. **Inputs from CA3.** A CA3 cell counts as active when its state is above zero.
9. **Plateau drive baseline (chosen on background drawings).** Two forms of item 3 were compared: the raw drive, and each cell's drive measured against its drive from the mean EC code of the background alphabets (one drawing of each of their 964 characters). With raw drive, a few cells whose random weights favour the features common to every drawing plateau for most drawings. In one background check at 100 drawings and 2,118 cells, the busiest cell plateaued for 24 of the 100 drawings, against 4 when plateaus fall on random cells, and identification from the exact pattern fell from 95% to 33%. Over the selection runs of item 10, the background mean scored 0.586 against 0.387 for raw drive (each size at its best share, averaged over both sizes). The baseline stands in for feedforward inhibition that EC layer III input recruits along with its excitation of CA1 dendrites, which suppresses dendritic spikes (Milstein and colleagues 2015, *Neuron*, 10.1016/j.neuron.2015.08.025). The evaluation runs use the background mean.
10. **Plateau share (chosen on background drawings).** Wu and Maass report 0.005 as the measured value. At 375 cells that gives 2 plateau cells per drawing. The share was chosen separately for each CA1 size from 0.0025, 0.005, 0.01, 0.02 and 0.05. The rule, fixed before the runs: the highest identification averaged over loads 20, 50, 100, 200 and 500 and over 17 inputs (the exact stored pattern, and CA3's settled state under each of E1c's 8 damage conditions with each of the two local CA3 rules), on 964 background characters, seeds 0 to 4. Scores with the background-mean baseline:

    | CA1 cells | 0.0025 | 0.005 | 0.01 | 0.02 | 0.05 |
    |---|---|---|---|---|---|
    | 2,118 (human ratio) | 0.6286 | **0.6287** | 0.6012 | 0.5502 | 0.4031 |
    | 375 (rat ratio) | 0.4711 | 0.4823 | **0.5433** | 0.5214 | 0.3965 |

    At 2,118 cells the measured value, 0.005, wins by 0.0001 over 0.0025, a tie in practice; it gives 11 plateau cells per drawing. At 375 cells 0.01 wins, giving 4 plateau cells per drawing.

### Free parameters of BTSP CA1

| Parameter | Source | Value |
|---|---|---|
| Plateau share | chosen on background drawings | 0.005 at 2,118 cells, 0.01 at 375 |
| Plateau drive baseline, yes or no | chosen on background drawings | yes |
| CA3-to-CA1 connection probability | Wu and Maass 2025 | 0.6 |
| Chance an eligible synapse changes | Wu and Maass 2025 | 0.5 |
| Starting weight | Wu and Maass 2025 | 0 |
| CA1 cells per CA3 cell | human or rat cell counts | 9.41 or 1.67 |
| Window | structural | one drawing per plateau |
| EC-to-CA1 plateau weights | structural, stand-in | uniform in [0, 1) |
| Recall | structural, stand-in | k-winners-take-all, k = m |
| Return rule | structural | CA1 activity times EC activity |

Two values were chosen on data. The return rule's rate has no value to choose: every score is a cosine, which ignores scale. `modules.btsp_parameters()` holds the same list, and a test checks it.

### Baselines

11. **Backpropagation into EC.** PM's network (100 hidden units, leaky ReLU on both layers), PM's optimiser (Adam, learning rate 0.01, L2 penalty 4 × 10⁻⁴) and PM's 60 full-batch steps, with the drawing's EC code as the target instead of its pixels. It starts from the same weights as E1c's CA1 for each load and seed.
12. **Two variants of it.** EC codes are about 19 times smaller than pixels (root mean square 0.0126 against 0.243 on background drawings), so PM's L2 penalty outweighs the error signal and the network learns little. One variant multiplies the EC target by that ratio, 19.3, so the penalty weighs as much as it does for PM. The other drops the penalty. All three are reported.
13. **PM as in AHA.** PM trained on pixels exactly as E1c trains it, scored in pixel space, and the same without its L2 penalty. Its error from the exact pattern repeats E1c's numbers (a test checks seed 0 at 20 drawings).
14. **No memory.** The mean stored EC code, returned for every cue.

### CA1 on its own (`trisynapsnet/eval/ca1space.py`)

15. **Drawings.** One drawing of each of the 659 evaluation characters, the same drawing per character as E1c. Each seed shuffles the characters, and load N stores the first N. DG makes their patterns as in E1c.
16. **Sizes and loads.** 225 CA3 cells with 10 active (AHA's 4.4%), loads 20, 50, 100, 200 and 500, 10 seeds. 1,000 CA3 cells with 44 active, 5 seeds, without the pixel arms. The share of active DG and CA3 cells is a parameter (`--active-share`).
17. **Cues.** Every stored pattern up to 200, a random 200 above that, as in E1c. Each cue enters CA1 three ways: the exact stored pattern; E1c's damaged copy as it is; and that copy after CA3 settles with the covariance rule or with clipped binary synapses, starting from the cue as given (E1c's settling). The damage conditions and their random draws are E1c's.
18. **Scores.** Cosine similarity between the returned code and the right drawing's EC code. Identification: the stored EC code with the highest cosine to the returned code is the right drawing's; ties score 1 over the number tied. PM is scored the same way against the stored drawings' pixels.
19. **Cost.** Wall time to learn each stored set, on the CPU with 2 threads, and the count of presentations or optimiser steps.

### Lake's runs and the instance task (`trisynapsnet/eval/evaluate.py`)

20. **Model.** AHA with CA3 on the covariance rule at 225 cells, 10 active, settling as in E1, normalised matching, 10 seeds, Apple's MPS backend. Only CA1 changes; a test checks that PR and CA3 give identical states whichever CA1 runs.
21. **The CA1 stage.** With BTSP or backpropagation into EC, the CA1 stage holds the returned EC code, for study and test drawings alike, and matching runs on those codes. With PM it holds the rebuilt image, as before.
22. **Arms.** PM, BTSP at both sizes, backpropagation into EC, and the same without its L2 penalty.
23. **Matching.** Both directions, as in E1b: study-to-test, AHA's, where each study drawing picks its nearest test drawing; and test-to-study, where each test drawing picks its nearest stored one.
24. **Instance task.** E1b's instance runs from the evaluation alphabets, occlusion and noise at 0, 0.3 and 0.5, corruption seed 0.

### Not done

25. **Rendering.** The vision network's checkpoint holds its encoder filters and a decoder bias. Its decoder would invert the feature map before the interest filter and 4 × 4 max-pooling, and nothing inverts those two steps, so returned EC codes are not drawn as images. Scores stay in EC space.
