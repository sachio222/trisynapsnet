# E8b protocol

People who study a series of pictures and later see a similar new one often call it old: in young adults, 40.3% of such lures (Stark and colleagues 2013, Table 2). The usual account is that the hippocampus completes the lure to the stored memory of the studied picture, so the memory comes back and feels familiar. E8 gave the fully local hippocampus the same test, built from Omniglot drawings, and it never called a lure old. E8b asks why, with three changes, each made for a reason in the biology and none for a score: a readout that judges from what CA3 recalls, a hippocampus sized by human anatomy, and lures as close to the studied item as the human task's. No learning rule changes. This file states every change, every setting with where it comes from, the runs and the predictions. It was committed before any run. The human task's list and lure construction, with quotes, are in `docs/e8b_sources.md`; the human rates and lesion findings are in `docs/e8_sources.md`.

## Terms

- **Mnemonic Similarity Task (MST)**. A person studies pictures once, then sees **repeats** (the same picture), **lures** (a similar picture never shown) and **foils** (new pictures), and answers old, similar or new for each (Stark and colleagues 2013).
- **Lure discrimination index (LDI)** = p(similar | lure) − p(similar | foil). **Recognition score (REC)** = p(old | repeat) − p(old | foil). Young adults: LDI 0.360, REC 0.786, p(old | lure) 0.403 (Stark and colleagues 2013, Table 2).
- **Pattern completion**: a recurrent network such as CA3, given part of a stored pattern, fills in the rest. **Attractor**: a state the network settles into and then holds; each stored pattern is one.
- **EC code**. The model's entorhinal input for a drawing: the frozen vision network's output, 20,449 numbers, zero or positive.
- **The model** is E8's fully local hippocampus (E3's model): DG imposes a sparse pattern on CA3 at study; CA3 stores it with **clipped binary synapses** (a synapse turns on once its two cells fire together); the **perforant path** from EC to CA3 learns each drawing's EC code against its CA3 pattern in one presentation; at test the perforant path's drive picks a cue, CA3 **settles** (each step keeps the most driven cells, until the state stops changing), and **CA1**, which learned in one presentation by behavioural timescale synaptic plasticity (BTSP), returns an EC code. Every setting not named below is E3's (`docs/e3_protocol.md`, `docs/e8_protocol.md`).
- **Cosine** of two codes: their dot product over the product of their lengths.

## Change 1: a recall-based readout (R2)

1. **R1**, E8's readout, is kept: the cosine between the test drawing's EC code and the EC code CA1 returns. CA1 acts as a comparator between what is recalled and what arrives.
2. **R2** judges from CA3 alone. CA3 settles from the perforant cue as before. With A the cells active in the settled state and W[i, j] the recurrent synapse from cell i onto cell j, R2's signal is

   self-support = (sum over j in A, i in A of W[i, j]) / (sum over j in A, over every CA3 cell i, of W[i, j]),

   the share of the active cells' potentiated recurrent input that comes from other active cells, 0 if the active cells have no potentiated input. A state that is a stored memory draws its active cells' support from inside itself; a mixture of memories, or a state the cue scattered, draws less. Old when the state holds itself up strongly, similar when weakly, new when it does not. Each term is a quantity a cell has: the synaptic input it receives from the cells now firing, and the summed strength of its potentiated synapses.
3. **Why this readout.** In the account of lure errors that the MST was built to test, a lure that is completed to the studied memory brings that memory back and is called old (Yassa and Stark 2011). R2 reads completion directly from CA3, where it happens.
4. **No list of memories.** R2 never compares the state with the stored patterns. Beside it, each item logs the largest share of the settled state's cells shared with any one stored pattern (a list lookup), and whether the state is exactly the paired drawing's pattern or any stored pattern, only to show what R2 tracks.
5. **Lesions under R2.** Without CA3's recurrent synapses, or without CA3, there is nothing for R2 to read: its signal is 0 for every item, and every item is called new. Each test item also logs the cue's own self-support through the intact recurrent synapses, as a diagnostic of how much settling adds; it is never scored as a readout.
6. **The vision-code baseline** decides from the largest cosine between the test code and any studied code, as in E8, and gets its own thresholds. It is the same under both readouts.

## Change 2: a hippocampus sized by human anatomy

7. **Human proportions.** DG, CA3 and CA1 keep the human cell counts' ratios, 15 million granule cells and 16 million CA1 pyramidal cells (West and Gundersen 1990) to 1.7 million CA3 pyramidal cells (Watson and colleagues 2025, CA3 without CA2), scaled down together by one denominator: DG 15,000,000 / D, CA3 1,700,000 / D, CA1 16,000,000 / D cells, rounded.
8. **EC is not scaled with them.** Human EC layer II has about 1.0 million neurons (West and Slomianka 1998), so at human proportions CA1 would need 16 cells for every EC unit. EC here is the vision network's output, 20,449 units, fixed by the frozen vision network; keeping EC in the ratio would need about 327,000 CA1 cells and 35,000 CA3 cells, far beyond the memory limit (item 10). So EC stays at 20,449 units and the human ratios apply to DG, CA3 and CA1 only. This is a deviation from the rule that EC, DG, CA3 and CA1 keep human ratios, and the closest faithful option the memory limit allows.
9. **Active cells.** 2% of DG cells and 2% of CA3 cells are active for each drawing, E1d's default (rat DG, Ramirez-Amaya and colleagues 2013; no human measurement exists): k = 2% of the cell count, rounded half up.
10. **The size.** D is the smallest value on the grid 2,000, 1,000, 750, 500, 400 (the largest network) whose memory probe stays under 3.6 GB peak resident memory, 90% of the 4 GB limit per process. The probe builds one list of 256 drawings, the largest load, with every arm and the closer lures, and records only peak memory and time; it computes no score (`python -m trisynapsnet.eval.recognition probe`, `results/e8b_probe.json`). Probe results:

    | D | DG cells | CA3 cells | CA1 cells | Peak memory | Seconds for one list |
    |---|---|---|---|---|---|
    | 2,000 | 7,500 | 850 | 8,000 | 1.64 GB | 18 |
    | 1,000 | 15,000 | 1,700 | 16,000 | 2.08 GB | 33 |
    | 750 | 20,000 | 2,267 | 21,333 | 2.52 GB | 44 |
    | 500 | 30,000 | 3,400 | 32,000 | 3.53 GB | 67 |
    | 400 | 37,500 | 4,250 | 40,000 | 4.48 GB | 73 |

    So D = 500: DG 30,000 cells with 600 active, CA3 3,400 with 68 active, CA1 32,000, of which 160 get a plateau for each drawing (E3's plateau share, 0.5%). That is about 15 times E8's CA3 (225 cells) and 15 times its CA1 (2,118). The size is fixed here and not changed for any result.
11. **Mossy fibres.** DG now has more cells than CA3, so DG's pattern reaches CA3 through the mossy fibres. Each CA3 cell gets 280 DG inputs, the human figure derived by Watson and colleagues (2025), chosen at random from the seed, each with its own fixed weight uniform in [0, 1). At study, the 2% of CA3 cells with the most mossy drive from DG's pattern form the stored pattern (k-winners-take-all, the stand-in for feedback inhibition used throughout the model). A scaled-down network cannot keep both the count and the probability: the human probability, 280 of 15 million, would leave each CA3 cell less than one DG input, so the count is kept. The weights never change. In E8, DG's output was itself the CA3 pattern; this is a new structural part, with no learning.
12. **DG and the perforant path.** DG is built as before (fixed random weights from every EC unit, 25% knocked out, the k most driven cells fire, cells that just fired are inhibited for the next drawings), drawn in blocks from the seed and dropped after use, so its random numbers differ from E8's though their distribution is the same. Each CA3 cell keeps its perforant connection share of 3.47% of EC units (710 of 20,449), E3's value. Perforant learning, cue selection, CA3's rule and settling, and BTSP CA1 are E3's, unchanged. BTSP draws its random gate only for synapses that can change (the plateau cells' synapses from active CA3 cells), the same rule with fewer random draws.
13. **Rat proportions** (1,000,000 : 210,000 : 350,000; Arellano and Rakic 2026) are not run: human proportions fit under the memory limit.

## Change 3: the human list length and closer lures

14. **List length.** People study 128 pictures and are tested on 64 repeats, 64 lures and 64 foils (Stark and colleagues 2013, Methods). The main list is 128 drawings of 128 different characters, half returning as repeats, half as the source of a lure, and 64 foils, E8's mix.
15. **Other-drawer lures**, E8's set: another person's drawing of a studied character, sorted into bins L1 (most similar) to L5 by the cosine between its EC code and its studied drawing's, with E8's bin edges (`results/e8_calibration.json`, set on background lures).
16. **Closer lures**, the second set: the studied drawing itself, distorted. Each distortion combines a random affine change and a smooth elastic displacement, all scaled by one magnitude m: rotation u₁ · m · 15°, isotropic scale 1 + u₂ · m · 0.15, shear u₃ · m · 0.15, with u uniform in [−1, 1], plus a random displacement field smoothed by a Gaussian of 4 pixels and scaled to m · 2 pixels root mean square, on the 52 by 52 image; the drawing is then re-centred as every drawing is, and encoded by the vision network. These shape settings were chosen once, before any run, and are not tuned.
17. **Five levels.** For each lure source, one random draw is scaled to five magnitudes, so the five closer lures of a drawing differ only in how far they are distorted. Target similarity for level Cj is the midpoint of the j-th of five equal steps from E8's closest-lure edge (the lower edge of L1, cosine 0.6634) up to 1, an exact repeat: C1 0.9663, C2 0.8990, C3 0.8317, C4 0.7644, C5 0.6971. Each level's magnitude is set by bisection so the median cosine between distorted and undistorted EC codes, over 1,000 background drawings with a fixed seed, meets its target (`python -m trisynapsnet.eval.recognition levels`, `results/e8b_lure_levels.json`). The levels are set after this file is committed and before any model run, from background drawings and the vision network alone.
18. **Test items.** Every list is tested with its 64 repeats, 64 foils, 64 other-drawer lures and 320 closer lures (five per lure source). The model does not learn at test, so items do not affect each other. Each lure set is scored against the same repeats and foils.

## Loads, interference and seeds

19. **Seeds and lists.** 10 seeds; each seed runs about 1,000 studied drawings: lists per seed = ⌈1,000 / load⌉ (8 at 128). List i of seed s draws its characters, people and distortions from generators fixed by (split, load, drawings per character, s, i); the model's random wiring comes from seed 1,000 s + i, as in E8.
20. **Load curve.** Loads 20, 50, 100, 128, 200 and 256, one drawing per character, with the arms that share the intact study (intact, no CA3 recurrent connections, no CA3, the vision-code baseline).
21. **Interference.** At 128 drawings, 2 and 4 drawings of each character by different people (64 and 32 characters), the same four arms. An other-drawer lure then resembles several studied drawings.
22. **Lesions**, at 128 drawings with both lure sets, as in E8 (`docs/e8_protocol.md`, items 15 to 20): no CA3 recurrent connections; no CA3 (CA1 driven by its direct EC input); no DG (the perforant path's own drive picks each drawing's CA3 pattern); the perforant path thinned to 75%, 50% and 25% of each CA3 cell's connections; no hippocampus (every item new, no run). E8's half-CA1 lesion is not in E8b's list and is not run.

## Decision rule and calibration

23. **Two thresholds per readout**, θ_old ≥ θ_new: signal above θ_old, old; below θ_new, new; between, similar; a signal exactly at a threshold takes that answer with a fixed probability, so tied signals can still meet a target rate. Scores use each item's answer probabilities.
24. **Two targets.** Young adults answered old to 81.2% of repeats and new to 82.0% of foils (Stark and colleagues 2013, Table 2, N = 26).
25. **Calibration.** On the background alphabets at 128 drawings, pooled over seeds, for each readout: θ_old so the intact model's p(old | repeat) is 0.812, θ_new so its p(new | foil) is 0.820. Nothing is fitted to p(old | lure), LDI, the similarity curve, any lesion or any other load. If θ_new comes out above θ_old, there is no room for similar; this is reported.
26. **Fixed thresholds** for every arm, load and interference condition (the main score): the intact model's, from item 25. The baseline keeps its own.
27. **Secondary scores.** Each lesion with its own thresholds from its background runs (not for the arms with no R2 signal under R2), and each load and interference condition with the intact model's thresholds set again on background runs at that condition, since a person's criterion adapts to the list.
28. **Evaluation alphabets** are scored once, with these thresholds, after every background run is done.

## Measures

29. Per readout, lure set and arm: response rates for repeats, lures and foils; LDI, REC and p(old | lure); LDI, p(old | lure) and p(similar | lure) by bin or level. Means over the 10 seeds with standard deviations, and for each lesion the number of seeds in which its effect holds.
30. CA3 state: cue size; share of repeats and lures that settle exactly onto the paired studied pattern, by bin or level; share of foils that settle exactly onto some stored pattern; p(old | lure) under R2 for lures that did and did not settle onto the studied pattern; the logged nearest-pattern overlap and the cue's self-support.
31. Human comparisons: young adults and adults 60 to 74 (Stark and colleagues 2013, Table 2) and the lesion directions in `docs/e8_sources.md`. No source states human rates per lure bin in its text, so figures carry only the young adults' overall values.

## Free parameters

| Parameter | Value | Chosen or measured, on what data |
|---|---|---|
| p(old \| repeat), p(new \| foil) targets | 0.812, 0.820 | measured, young adults (Stark and colleagues 2013, Table 2) |
| θ_old, θ_new for R1 and for R2 (and tie shares) | from item 25 | fitted to the two targets on background runs at 128 drawings |
| Baseline thresholds | from item 25 | fitted the same way |
| R2 signal | self-support of the settled state | structural (item 2) |
| DG : CA3 : CA1 cells | 15,000,000 : 1,700,000 : 16,000,000 | measured, human (West and Gundersen 1990; Watson and colleagues 2025) |
| Scale denominator D | 500 | set by the memory probe (item 10), not by any score |
| EC units | 20,449 | fixed by the frozen vision network; not at human ratio (item 8) |
| Active share, DG and CA3 | 2% | E1d's default, rat DG measurement |
| DG inputs per CA3 cell | 280 | derived for humans (Watson and colleagues 2025); count kept, not probability |
| Mossy weights | fixed, uniform in [0, 1) | structural (item 11) |
| Perforant connection share | 3.47% | E3's, rat (Treves and Rolls 1992; Arellano and Rakic 2026) |
| List length and test mix | 128; 64 repeats, 64 lures, 64 foils | measured, the MST (Stark and colleagues 2013) |
| Distortion shape | rotation 15°, scale 0.15, shear 0.15, elastic 2 px (σ 4 px) per unit magnitude | chosen before any run, not tuned |
| Closer-lure level targets | midpoints from 0.6634 to 1 | structural (item 17), E8's L1 edge |
| Closer-lure magnitudes | from item 17 | measured on background drawings to meet the targets |
| Other-drawer bin edges | E8's | measured on background lures in E8 |
| Loads, interference | 20 to 256; 2 and 4 per character | chosen |
| Perforant path kept | 75%, 50%, 25% | chosen, as in E8 |
| Model otherwise | E3's | perforant path: 10 free parameters, 3 chosen on background alphabets (`docs/e3_protocol.md`); BTSP CA1: 10, 2 chosen on background drawings (`docs/e4_protocol.md`) |

Four thresholds are fitted for the model, two per readout, all on background alphabets. No value is chosen on the evaluation alphabets.

## Order

32. Tests for the R2 signal, the scaled model's construction, the closer lures and per-load recalibration (`tests/test_recognition.py`) pass, and every earlier test still passes, before any run.
33. Memory probe (item 10), then this file is committed.
34. Closer-lure levels from background drawings (item 17).
35. Background runs: 128 drawings with every arm; loads 20, 50, 100, 200, 256 and 2 and 4 drawings per character with the four shared arms. Then thresholds (`scripts/make_e8b_table.py --calibrate`, `results/e8b_calibration.json`).
36. Evaluation runs, the same conditions, each scored once.
37. At most two runs at once, each under 4 GB resident, with a watchdog that stops every run if free memory falls below 20% or a run passes 4 GB.

## Predictions

Written in the plan before any E8b run, copied here verbatim:

- Under R2, p(old | lure) equals roughly the share of lures that settle onto their studied pattern, rises with lure similarity, and lands within 0.15 of young adults' 0.403 on the closer-lure set at the human list length, with no parameter fitted to it.
- Under R2, LDI falls as lures grow more similar (the human direction); under R1 it keeps rising, as in E8.
- At the new size, REC at the human list length is at least 0.6 under both readouts.
- Removing CA3's recurrent connections drops p(old | lure) under R2 by at least half; removing DG raises it.
- Thinning the perforant path lowers p(old | lure) under R2, since E8 found fewer lures settle onto the studied pattern when it is thinned. This would run against the ageing account, in which older adults call more lures old.
- With four drawings per character, the intact model's LDI beats the vision-code baseline under at least one readout.

How each is scored, fixed before any run, on means over seeds on the evaluation alphabets at 128 drawings with fixed thresholds:

1. Held if, on the closer-lure set under R2 for the intact model, all three hold: p(old | lure) is within 0.10 of the share of closer lures that settle exactly onto their studied pattern; p(old | lure) at C1 is above C5 and no step from one level to the next less similar one raises it by more than 0.05; and p(old | lure) is within 0.15 of 0.403.
2. Held if, on the closer-lure set, R2's LDI at C5 is above C1 with no step toward less similar lures lowering it by more than 0.05, and R1's LDI at C1 is above C5. The same test on the other-drawer bins L1 to L5 is reported beside it.
3. Held if the intact model's REC is at least 0.6 under R1 and under R2.
4. Held if, on the closer-lure set under R2, the intact model's p(old | lure) is above 0, the no-recurrent arm's is at most half of it, and the no-DG arm's is above it. Without recurrent synapses R2 has no signal (item 5), so the first half holds by construction whenever the intact model calls any lure old; this is stated with the result.
5. Held at a thinning level if, on the closer-lure set under R2, p(old | lure) is below the intact model's. Reported at each of the three levels.
6. Held if, with 4 drawings per character, the intact model's LDI on other-drawer lures is above the vision-code baseline's under R1 or under R2.
