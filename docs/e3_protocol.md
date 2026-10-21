# E3 protocol

E3 asks whether CA3's ability to complete a partial pattern helps end to end once the cue that reaches CA3 comes from a perforant path learned in one presentation, instead of from a network trained by backpropagation. This file quotes the sources for the perforant path's wiring, states its learning rule, counts its free parameters, and lists each choice. The choices went into code and tests before the reported runs. Three were chosen on background-alphabet drawings, as items 18 to 20 describe.

## Terms

- **EC**, the entorhinal cortex, feeds the hippocampus. In this model a drawing's EC code is the frozen vision network's output: 20,449 numbers, all zero or positive. On background drawings about 1,270 of them (6.2%) are above zero.
- **DG**, the dentate gyrus, gives each drawing a new sparse pattern: k of 225 cells on. E3 runs with k = 5 (2.2%, the nearest whole number to the 2% of granule cells active in the rat) and checks k = 10 (4.4%, AHA's value).
- **CA3** is the hippocampal field whose cells connect back to each other. It stores DG's patterns with a local rule, covariance or clipped binary synapses (E1), and recalls by **settling**: from a starting state, each step turns on the k cells with the most recurrent input, until the state stops changing. Settling from a pattern with cells missing, so that it ends on the full stored pattern, is **pattern completion**.
- **PR** is AHA's path from EC into CA3: a two-layer network trained by backpropagation, 60 steps per study set, to output each drawing's DG pattern. Its output is CA3's cue in every earlier experiment.
- The **perforant path** is the projection from EC layer II to CA3 in the brain. Its synapses are weak, numerous and associatively modifiable. The **mossy fibres** from DG to CA3 are few, strong, and drive CA3's pattern during learning.
- **CA1** returns the memory to EC. E3 uses E4's CA1: one-shot behavioural timescale synaptic plasticity (BTSP) on CA3-to-CA1 synapses and a Hebbian return to EC. **PM** is AHA's CA1, trained by backpropagation to rebuild the drawing's pixels; it runs as a reference.
- **k-winners-take-all (k-WTA)** keeps the k most driven cells on and turns the rest off. It stands in for feedback inhibition, as in E1.
- **E%-max** is a proposed form of feedback inhibition in which the cells whose excitation lies within E% of the most excited cell fire before inhibition shuts the rest down (de Almeida, Idiart and Lisman, 2009, *J Neurosci* 29:7497, doi 10.1523/JNEUROSCI.6044-08.2009). Unlike k-WTA, it can leave fewer than k cells on.
- **Matching directions.** Each stage is scored by normalised minimum mean squared error between states. **Test-to-study**: each test drawing's state picks the nearest studied state, the way a cue retrieves a memory. **Study-to-test**: each studied state picks the nearest test state, AHA's direction.
- **Load** is the number of drawings studied at once.

## Sources for the perforant path

| Source | What it says |
|---|---|
| Treves and Rolls 1992, *Hippocampus* 2:189, doi 10.1002/hipo.450020209, abstract | "The synapses of the first system need to be strong (but not associatively modifiable) in order to force, during learning, the CA3 cells into a pattern of activity [...] It is proposed that the mossy fiber system performs this function. A second system, with a large number of associatively modifiable synapses on each receiving cell, is needed in order to relay a signal specific enough to initiate the retrieval process. This may be identified, we propose, with the perforant path input to CA3." |
| Treves and Rolls 1992, p. 190 | "it has been calculated that each CA3 pyramidal cell may receive up to 3750 PP synapses in the rat (Amaral et al., 1990), possibly from as many different cells in entorhinal cortex." The same page gives "about 12,000" recurrent synapses and at most 46 mossy fibre inputs per CA3 cell. |
| Arellano and Rakic 2026, *Hippocampus* 36:e70070, doi 10.1002/hipo.70070 | About 108,000 neurons in rat EC layer II. |

Dividing the two counts gives the share of EC layer II cells that one CA3 cell hears from: 3,750 / 108,000 = 3.47%. The two numbers come from different rat strains and studies, so the share is an estimate.

## Choices

### Wiring

1. **In-degree.** Each CA3 cell connects to a fixed random set of EC units: 3.47% of the 20,449, rounded half up, so 710 units per cell. Scaling keeps the measured share, not the measured count. The model's EC is a vision code with about 91 units per CA3 cell, where the rat has about 0.5 EC layer II cells per CA3 cell (108,000 against 210,000), so keeping 3,750 inputs per cell would mean 18% of EC.
2. **Draw.** Each cell's 710 partners are distinct, drawn once per model seed from a generator derived from that seed, separate from every other part's random numbers. Every CA3 cell has exactly 710 inputs (a test checks it).
3. **Sign.** Perforant synapses are excitatory. Clipped binary weights are 0 or 1. Covariance weights take either sign, which breaks Dale's principle in the same way as E1's covariance rule in CA3; E2 is where inhibitory cells take over the negative part.

### Learning, one presentation per drawing

4. **What is paired.** During study, DG's pattern for a drawing is the CA3 pattern y (k cells on). The mossy fibres impose it, so the perforant path learns the pairing of the drawing's EC code x with y. Nothing learns at recall.
5. **Clipped binary rule** (Willshaw, Buneman and Longuet-Higgins 1969, as in E1). On every connected synapse, W_ij becomes min(1, W_ij + y_i b_j), where b_j = 1 when EC unit j is active. Active means x_j > 0, or x_j above that unit's mean over the background drawings (item 18).
6. **Covariance rule** (as in E1, with graded input). On every connected synapse, W_ij grows by (y_i − k/n)(x_j − x̄_j), where n = 225 and x̄ is the mean EC code over one drawing of each of the 964 background characters, the same mean E4 uses for CA1's plateaus.
7. **Start.** Every perforant weight is 0 at the start of each study set. A hand-worked example of both rules is in `tests/test_perforant.py`.

### Recall

8. **Drive.** Each CA3 cell sums its perforant input: h_i = Σ_j W_ij r_j, with r = b for clipped binary synapses and r = x, the raw rate, for the covariance rule.
9. **Normalised drive** (item 19). Optionally, h_i is divided by the cell's total active input Σ_j C_ij r_j, where C marks its 710 connections. In an incompletely connected net, cells differ in how many active inputs they happen to receive (Buckingham and Willshaw 1993, *Network* 4:441, doi 10.1088/0954-898X_4_4_003); dividing removes that difference.
10. **Cue.** k-WTA on the drive keeps the k most driven cells. With E%-max (item 20), only those among them with h_i ≥ max h − E |max h| stay on, so the cue can have fewer than k cells and never more. Both are stand-ins for inhibition.
11. **Settling from the cue.** CA3 settles from the cue as given (E1c's partial start): the first state is k-WTA(W × cue). Settling uses the CA3 rule that matches the perforant rule: covariance with covariance, clipped binary with clipped binary. Up to 70 steps, no persistent EC input (cue weight 0, as in E1).

### Arms

12. **Seven arms from one study.** Each (seed, run) studies once: DG, both CA3 rules, PR (60 backpropagation steps, unchanged), both perforant paths, BTSP CA1 and PM. Every test drawing is then recalled through:

    | Arm | CA3 input | Settling |
    |---|---|---|
    | PR, no settling | PR's k most active cells | none |
    | PR, covariance | PR's output | covariance CA3, from PR's top k (E1) |
    | PR, clipped binary | PR's output | clipped binary CA3, from PR's top k |
    | Perforant, covariance, no settling | covariance perforant cue | none |
    | Perforant, covariance | covariance perforant cue | covariance CA3, from the cue |
    | Perforant, clipped binary, no settling | clipped binary perforant cue | none |
    | Perforant, clipped binary | clipped binary perforant cue | clipped binary CA3, from the cue |

13. **Same parts, same weights.** Every part before the perforant path starts from the weights it has in E1d's and E4's runs. A slow test checks that the PR arms repeat E1d's and E4's seed-0 scores on Lake's runs exactly, at the CA3, CA1 and PM stages.
14. **The no-settling arms** pass the cue on unchanged, so a perforant cue with fewer than k cells reaches CA1 with fewer than k cells.

### CA1

15. **BTSP CA1 at the human ratio.** 2,118 CA1 cells (225 × 16 million / 1.7 million), plateau share 0.005, plateau drive measured against the background mean EC code, as chosen in E4. The CA1 stage scores the EC code CA1 returns.
16. **Tie-breaking.** BTSP breaks ties in CA1 with a random jitter. Its random generator returns to its state after study before each arm, so every arm sees the same jitter.
17. **PM as a reference.** AHA's CA1, trained as in AHA, runs on every arm's CA3 state and is scored in pixel space.

### Settings chosen on background alphabets

18. **Clipped binary presynaptic activity:** above zero, or above the unit's background mean.
19. **Normalised drive:** yes or no, for each rule.
20. **E%-max:** none (plain k-WTA), 0.1, 0.2, 0.3 or 0.5, for each rule.

    The grid has 20 clipped binary and 10 covariance settings. The rule, fixed before the runs: for each perforant rule, the setting with the highest mean CA3-stage accuracy over 8 conditions (the 20 background validation runs, clean; the 20 background instance runs, clean and at occlusion and noise 0.3, 0.5 and 0.7), both matching directions, and the settling and no-settling arms weighted equally, seeds 0 to 4, at k = 5. Ties go to the simpler setting: k-WTA before E%-max, raw drive before normalised, above zero before above the mean. Weighting both arms equally keeps the choice from favouring either side of prediction 2. The 4.4% check reuses the settings chosen at 2%.

### Free parameters of the perforant path

| Parameter | Source | Value |
|---|---|---|
| Connection share | Treves and Rolls 1992; Arellano and Rakic 2026 | 3,750 / 108,000 = 3.47%, 710 inputs |
| Clipped binary presynaptic activity | chosen on background drawings | item 18 |
| Normalised drive, yes or no | chosen on background drawings | item 19, per rule |
| E%-max | chosen on background drawings | item 20, per rule |
| Cells in the cue at most | DG's k | 5 (or 10) |
| Covariance CA3 baseline | E1's rule | k / n |
| Covariance EC baseline | structural, E4's background mean | mean EC code |
| Starting weight | structural | 0 |
| Clipped binary ceiling | structural | 1 |
| One presentation, certain change | structural | each drawing learned once |

Three values were chosen on data, all on background alphabets. `modules.perforant_parameters()` holds the same list, and a test checks it.

### Tasks

21. **Lake's 20 runs.** 10 seeds, normalised matching, both directions, every arm, at the CA3, CA1 and PM stages.
22. **Instance task.** E1b's instance runs from the evaluation alphabets: 20 drawings of one character, studied once, recalled from the same drawings clean and under occlusion and noise at 0.3, 0.5 and 0.7, corruption seed 0, 10 seeds. Each run studies once and recalls every level of both kinds.
23. **Load.** E1c's end-to-end runs: 20, 50, 100 and 200 drawings of different evaluation characters studied at once, about 400 drawings per seed in runs of that size, recalled from the same drawings clean and under occlusion and noise at 0.3, 0.5 and 0.7, 5 seeds.
24. **Check first.** Lake-style validation runs and instance runs from the background alphabets, 5 seeds, with the chosen settings, before any evaluation run.
25. **Activity.** k = 5 for items 21 to 24. Items 21 and 22 rerun at k = 10.
26. **Order and machine.** Apple's MPS backend for the vision network, PR and PM, as in E1d and E4; perforant path and BTSP on the CPU. At most two runs at once.

### Measures

27. **Accuracy** of every arm at the CA3, CA1 and PM stages in both directions, plus the vision code and PR's raw output as references.
28. **Cue quality.** For each arm: the share of the right stored pattern's k cells on in the cue and in the final state, cells on outside it (over k), cells on in the cue, and whether the ideal lookup (the stored pattern sharing the most active cells, ties scored 1 over the number tied) picks the right pattern from the cue and from the final state.
29. **Exact recall.** The final CA3 state equals the right stored pattern.
30. **Settling's effect.** Each settling arm minus its no-settling arm, per seed, so the spread over seeds sits beside the mean.
31. **Run time** per file.

## Predictions

Written before any E3 run:

1. The perforant cue is weaker than PR's: without settling, accuracy on both tasks falls below the PR model's.
2. With the perforant path, settling helps end to end: on the instance task, scored test-to-study, settling beats no settling by at least 5 points at some corruption level below capacity.
3. On Lake's runs, the fully local model scores below the PR model; the gap is the cost of removing backpropagation from the hippocampal pathway.
4. CA1-stage accuracy stays within 3 points of the CA3 stage.

## Not done

32. **Persistent EC input during settling.** Treves and Rolls's scheme lets the perforant input keep driving CA3 while it settles. E3 keeps E1's cue weight of 0 so that settling is the only change between arms.
33. **Measured count instead of share.** Keeping 3,750 inputs per CA3 cell (18% of the model's EC) is E2's question, together with the other wiring densities.

## Added after the runs

34. **Full connectivity, a diagnostic.** After phases A to E, one run on the background validation runs (5 seeds, the chosen settings) connects every CA3 cell to all 20,449 EC units, to separate the cost of sparse wiring from the cost of the one-shot rule on new drawings. It changes no reported setting and touches no evaluation alphabet. File: `results/e3_classification_background_225_5_share1.json`.
