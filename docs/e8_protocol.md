# E8 protocol

E8 tests the model on the recognition task people do in the clinic, rather than on classification. People who study a series of pictures and are then shown similar new pictures can usually tell them apart, and that ability depends on the hippocampus's dentate gyrus (DG) and CA3. E8 builds the same test from Omniglot drawings, sets the model's two decision thresholds so that its answers to exact repeats and to new items match young adults', and then asks whether its answers to similar items, and the effect of removing each part, match what people and patients do. This file states the task, the decision rule, every lesion, the free parameters and the predictions. It was committed before any evaluation-alphabet run. The human numbers and quotes come from `docs/e8_sources.md`.

## Terms

- **Mnemonic Similarity Task (MST)**. A person studies a series of pictures, then sees **repeats** (the same picture), **lures** (a similar picture never shown) and **foils** (new pictures), and answers old, similar or new for each (Stark and colleagues 2013).
- **Lure discrimination index (LDI)** = p(similar | lure) − p(similar | foil). **Recognition score (REC)** = p(old | repeat) − p(old | foil). Young adults score LDI 0.360 and REC 0.786 (Stark and colleagues 2013, Table 2).
- **Lure bins**. People's lures are sorted into five bins, L1 most similar to the studied picture and L5 least.
- **EC code**. The model's entorhinal input for a drawing: the frozen vision network's output, 20,449 numbers, zero or positive.
- **The model** is E3's fully local hippocampus, unchanged. DG gives each studied drawing a pattern of 5 active cells out of 225 (2%). CA3 stores it with **clipped binary synapses** (a synapse turns on once both its cells fire together). The **perforant path**, the projection from EC to CA3, gives each CA3 cell 710 of the 20,449 EC units and learns each drawing's EC code against its CA3 pattern in one presentation. At test the perforant path's drive picks a cue of at most 5 CA3 cells, and CA3 **settles**: each step keeps the 5 cells with the most recurrent input, until the state stops changing. **CA1** learns in one presentation by behavioural timescale synaptic plasticity (BTSP) on 2,118 cells and returns an EC code. Every setting is E3's, listed in `docs/e3_protocol.md`.
- **Cosine** of two codes: their dot product over the product of their lengths, 1 for codes pointing the same way.

## Task

1. **Drawings.** Omniglot's 1,623 characters were each drawn once by 20 people. Evaluation runs use the 20 evaluation alphabets (659 characters); calibration and checks use the 30 background alphabets (964 characters). Every drawing's EC code is computed once and cached.
2. **One list.** The model studies `load` drawings once: `load / d` characters drawn at random from the split, `d` drawings of each by different people (d = 1 except in the interference runs). Half the studied drawings, chosen at random, come back as **repeats**: the same drawing. For each of the other half, a drawing of the same character by a person whose drawing of it was not studied comes back as a **lure**. `load / 2` characters that were not studied come as **foils**, each drawn by a random person. So a list of 20 has 30 test drawings: 10 of each kind.
3. **Lists and seeds.** 10 seeds. Each seed runs about 1,000 studied drawings: 50 lists at load 20, 20 at 50, 10 at 100, 5 at 200. List i of seed s draws its characters and people from a generator fixed by (split, load, d, s, i); the model's random wiring comes from seed 1,000 s + i, as in E3.
4. **Lure bins.** Each lure's similarity is the cosine between its EC code and the EC code of the studied drawing it pairs with. Five bins with equal counts are set by the quintiles of that similarity over all lures of the background calibration runs (item 12), and the same edges are used for the evaluation alphabets. L1 holds the most similar lures. This is a stand-in: people's bins come from how often a large group of young adults called each lure old, a behavioural measure; these come from the vision network's code.
5. **Interference.** At load 20, lists with d = 2 (10 characters, 2 drawings each) and d = 4 (5 characters, 4 each). A lure then resembles d studied drawings.
6. **Load.** Loads 20, 50, 100 and 200 at d = 1.

## Decision rule

7. **Signal.** The test drawing's EC code x goes through the model: perforant cue, CA3 settling, CA1, returned EC code r. The signal is cos(x, r), 0 when r is all zero. High means the memory CA1 brings back matches what is in front of the model. This treats CA1 as a comparator between what is recalled and what arrives from EC, the role the plan gives it.
8. **Answers.** With two thresholds θ_old ≥ θ_new: signal above θ_old, old; below θ_new, new; between, similar. A signal exactly at a threshold takes that answer with a fixed probability q (item 11), so a signal with repeated values can still meet a target rate; the scores use each item's answer probabilities, so no random draw enters.
9. **No CA3 signal.** The rule reads only CA1's return. On a background pilot (one seed, 10 lists), CA3 settled exactly onto some stored pattern for 96% of foils as well as for every repeat, so whether CA3 reached a stored pattern carries almost no old-or-new information, and the perforant drive into CA3 already shapes what CA1 returns.
10. **Two targets.** Young adults answered old to 81.2% of repeats and new to 82.0% of foils (Stark and colleagues 2013, Table 2, N = 26).
11. **Calibration.** On the background calibration runs (item 12), pooled over seeds: θ_old (and its q) so that the intact model's p(old | repeat) is 0.812, and θ_new (and its q) so that its p(new | foil) is 0.820. If θ_new came out above θ_old, there would be no room for similar; this is checked and reported.
12. **Background calibration runs.** Load 20, d = 1, 50 lists, 10 seeds, every arm, from the background alphabets.
13. **Fixed thresholds for every arm and condition.** The intact thresholds are applied to every lesion, every load and every interference condition. A patient or a lesioned model does not get new thresholds, so each lesion's change in LDI, REC and every rate is a prediction, not a fit. As a secondary check, each lesion is also scored with thresholds recalibrated on its own background runs.
14. **The vision-code baseline** decides from the vision network's codes alone, with no hippocampus: its signal is the largest cosine between the test code and any studied code, and it gets its own two thresholds, set on the background runs the same way. It stands in for a cortical familiarity signal and, unlike the hippocampus, keeps a list of every studied code.

Known before any evaluation run: on the background pilot, the most similar lure reached a cosine of 0.77 with its studied drawing, while θ_old sat near 0.96, so no lure was called old, in any arm. Predictions 4 and 5 below turn on p(old | lure). If it stays at 0 on the evaluation alphabets, they are reported as failed, and the CA3 measure in item 24, how often a lure settles exactly onto the studied drawing's pattern, is reported beside them as the closest measure of the mechanism they name.

## Lesions

Each lesion removes one part. Lesions 15 to 18 share the intact model's study; lesions 19 to 21 study again with the part removed.

15. **No CA3 recurrent connections** (no settling). The perforant cue goes straight to CA1.
16. **No CA3.** CA1 gets no CA3 input. It is driven instead by its direct input from EC, the fixed projection that sets its plateaus during study (the m = 11 most driven cells), and returns the EC code its learned return synapses give. In the brain this is the direct path from EC layer III to CA1.
17. **No hippocampus.** No code comes back, the signal is 0, and every item is called new: every rate of old and similar is 0, and LDI and REC are 0. It needs no run. People with hippocampal damage keep their cortex, so the vision-code baseline (item 14), not this lesion, is the comparison for Kirwan and colleagues' patients.
18. **The vision-code baseline**, item 14.
19. **No DG.** With no mossy fibres, the perforant path drives storage: each studied drawing's CA3 pattern is the 5 CA3 cells with the most perforant drive through all their 710 connections at equal weight, from the raw EC rates. The perforant path then learns that pattern, CA3 stores it and CA1 learns it, as in the intact model. Similar drawings now get similar CA3 patterns.
20. **Thinned perforant path.** Before study, each CA3 cell keeps 75%, 50% or 25% of its 710 EC connections (533, 355 and 178), chosen at random from the seed; a smaller share removes a superset of a larger one. No measured size of the age-related loss could be read in the sources, so the three levels span a range.
21. **Half of CA1.** CA1 with 1,059 cells instead of 2,118, the plateau share unchanged, so 5 cells plateau per drawing. This lesion is not in the plan's list; it is added for the CA1 finding of Hanert and colleagues 2019, and it carries no prediction.

## Measures

22. **Response table**: p(old), p(similar) and p(new) for repeats, lures and foils, per arm.
23. **LDI and REC** per arm, overall and by lure bin, per condition. Means over the 10 seeds, with the standard deviation over seeds, and for each comparison the number of seeds in which it holds.
24. **CA3 state**: the share of repeats and lures whose settled state is exactly the stored pattern of the drawing they pair with, the share of foils that settle exactly onto some stored pattern, and the cue's size.
25. **Human comparisons**: young adults (Stark and colleagues 2013, Table 2), ages 60 to 74 from the same table for the thinned perforant path, Kirwan and colleagues 2012 for the vision-code baseline, and the directions in `docs/e8_sources.md` for DG and CA1 lesions. People's rates per lure bin could not be found in any source's text, so figures carry no human curve per bin, only the young adults' overall LDI.

## Free parameters

| Parameter | Value | Chosen or measured, on what data |
|---|---|---|
| p(old \| repeat) target | 0.812 | measured, young adults (Stark and colleagues 2013, Table 2) |
| p(new \| foil) target | 0.820 | measured, same table |
| θ_old, θ_new (and tie shares) | from item 11 | fitted to the two targets on background runs |
| Baseline θ_old, θ_new | from item 14 | fitted to the two targets on background runs |
| Signal | cosine of input and returned EC code | structural (item 7) |
| Lure similarity | cosine of EC codes | structural (item 4) |
| Lure bin edges | quintiles | measured on background lures |
| Number of bins | 5 | taken from the MST |
| List length | 20 for the main task | chosen: the size of Lake's runs and E3's tests; the MST's lists are longer, and the load runs cover longer lists |
| Test mix | equal repeats, lures, foils | chosen |
| Perforant path kept | 75%, 50%, 25% | chosen: no measured loss available |
| DG removed, starting perforant weights | equal on every connection | structural (item 19) |
| CA1 halved | 1,059 cells | chosen |
| Model | E3's, unchanged | the perforant path's 10 free parameters, 3 chosen on background alphabets (`docs/e3_protocol.md`); BTSP CA1's 10, 2 chosen on background drawings (`docs/e4_protocol.md`) |

Two thresholds are fitted for the model, both on background alphabets. No value is chosen on the evaluation alphabets.

## Order

26. Tests for the task builder, decision rule, scores, bins and each lesion (`tests/test_behaviour.py`) pass before any run.
27. Background calibration runs (item 12); thresholds and bin edges written to `results/e8_calibration.json`.
28. Background check runs at loads 50 to 200 and d = 2, 4, to see that nothing breaks before the evaluation runs.
29. Evaluation runs, each scored once: main task with every arm; loads 50, 100, 200; d = 2 and 4. Load and interference runs use the arms that share the intact study (items 15, 16, 18).
30. At most two runs at once, each under 4 GB resident, with a watchdog that stops a run if free memory falls below 20%.

## Predictions

Written in the plan before any E8 run, copied here verbatim:

- Intact model: LDI falls as lures grow more similar, while REC stays high, as in people.
- The hippocampus adds lure discrimination: at the middle similarity bins, the intact model's LDI beats the vision-code baseline by at least 0.10.
- Removing DG lowers LDI by more than it lowers REC.
- Thinning the perforant path lowers LDI while REC stays near intact, because a weaker cue lets CA3 settle a lure onto the studied drawing; p(old | lure) rises.
- Removing CA3's recurrent connections lowers p(old | lure).
- LDI falls with load faster than REC.

How each is scored, fixed before the evaluation runs, on means over seeds at load 20, d = 1, with fixed thresholds:

1. Held if LDI in L5 is above LDI in L1, no step from one bin to the next less similar one lowers LDI by more than 0.05, and REC is within 0.10 of young adults' 0.786.
2. Held if the intact model's LDI minus the baseline's LDI, averaged over L2, L3 and L4, is at least 0.10.
3. Held if the intact model's LDI minus the DG-removed model's LDI is larger than the same difference in REC.
4. Held at a thinning level if LDI falls below the intact model's, REC stays within 0.05 of it, and p(old | lure) rises above it. Reported at each of the three levels.
5. Held if p(old | lure) without CA3's recurrent connections is below the intact model's.
6. Held if the intact model's LDI at load 20 minus LDI at load 200 is larger than the same difference in REC.
