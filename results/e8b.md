# E8b results

People who study a series of pictures and later see a similar new one often call it old: young adults do so for 40.3% of such lures on the Mnemonic Similarity Task (Stark and colleagues 2013, Table 2). The usual account is pattern completion: the hippocampus rebuilds the stored memory of the studied picture from the lure, so the studied picture comes back to mind and the lure feels familiar. In E8 the fully local hippocampus never called a lure old. E8b asks why, with three changes, each made for a reason in the biology: a second readout that judges from what CA3 recalls, a hippocampus sized by human cell counts, and lures as close to the studied drawing as the human task's. No learning rule changes. The protocol, with every setting and its source, is `docs/e8b_protocol.md`; the human task's list and lures are in `docs/e8b_sources.md`, and the human rates and lesion findings in `docs/e8_sources.md`. Every number below comes from `results/e8b_*.json` through `scripts/make_e8b_table.py`.

**Setup.** The model is E8's: a perforant path with clipped binary synapses picks a cue in CA3, CA3's recurrent connections carry it to a final state, and a one-shot CA1 returns an EC code. Its cell counts now keep the human ratios, scaled down 500 times: DG 30,000 cells, CA3 3,400 (68 active for each drawing) and CA1 32,000, about 15 times E8's CA3 and CA1. EC stays at the vision code's 20,449 units, below the human ratio, because the vision network fixes it. The model studies 128 drawings of different characters once, the human task's list length, and is tested on 64 repeats, 64 foils and two sets of lures: another person's drawing of a studied character (other-drawer lures, E8's set, bins L1 to L5) and the studied drawing itself distorted at five levels (closer lures, C1 to C5, with median vision-code cosines of 0.966 down to 0.697 against the undistorted drawing). Each readout has two thresholds, set on background alphabets so that the intact model calls 81.2% of repeats old and 82.0% of foils new, young adults' rates. Evaluation alphabets were scored once.

**Main result.** At the human list length, with lures as close as the human task's, neither readout answers like people, and one of six predictions held. The CA1 comparator (R1) keeps recognition near people's (REC 0.724 against 0.786) but calls 2.4% of closer lures old against people's 40.3%, and calls closer lures similar no more often than foils (LDI 0.006 against 0.360). CA3 self-support (R2) calls 39.6% of closer lures old, close to people, but its two thresholds cross on the background runs, so it never answers similar and also calls 35.5% of foils old, where people call 2.6%. Attractor dynamics carry every test cue, foils included, onto a stored pattern, so the final state's self-support differs little between repeats (median 0.278) and foils (0.261). The larger network does hold recognition at 128 drawings; E8's network, with 225 CA3 cells, had REC 0.062 at 50.

## Terms

- **LDI**, the lure discrimination index: p(similar | lure) − p(similar | foil). **REC**, the recognition score: p(old | repeat) − p(old | foil). Young adults score LDI 0.360 and REC 0.786 and call 40.3% of lures old (Stark and colleagues 2013, Table 2).
- **Attractor dynamics and pattern completion.** At test the perforant path's drive from EC picks 68 CA3 cells, the cue or starting state. CA3 then runs in rounds: in each round the 68 cells with the most recurrent input from the cells now active fire next, until the state stops changing. A state that holds itself this way is an attractor, and each stored pattern is one. Reaching the studied drawing's stored pattern from a partial or distorted cue this way is pattern completion.
- **R1, the CA1 comparator** (E8's readout): the cosine between the test drawing's EC code and the EC code CA1 returns from CA3's final state. Above θ_old the model answers old, below θ_new new, between them similar.
- **R2, CA3 self-support**: of all the potentiated recurrent input onto the cells active in CA3's final state, the share that comes from other active cells. A stored pattern draws most of its support from inside itself; a mixture of patterns draws less. Old when the share is high, similar when it is middling, new when it is low. R2 never consults the list of stored patterns.
- **Cue self-support**: the same share computed on the starting state, before attractor dynamics. Logged for every test item, never used to decide.
- **Nearest-pattern overlap**: the largest share of the final state's cells held in common with any one stored pattern. It needs the list of stored patterns, so it is logged only.
- **Ending on the studied pattern**: CA3's final state is exactly the stored pattern of the drawing a lure was made from.
- **Fixed thresholds**: every lesion, load and interference condition uses the intact model's thresholds from 128 background drawings; the vision-code baseline keeps its own. Each arm's own thresholds, and thresholds set again at each load, are secondary checks.
- **Vision-code baseline**: decides from the largest cosine between the test drawing's vision code and any studied drawing's, with no hippocampus.

The main condition is the evaluation alphabets at 128 drawings with fixed thresholds. Values are means over 10 seeds; each seed runs about 1,000 studied drawings.

## Predictions

Written in the plan before any run and given here in short; the exact wording, and how each is scored, are in `docs/e8b_protocol.md`, both fixed before any run. Scored on closer lures unless stated.

| Prediction | Outcome |
|---|---|
| 1. Under R2, p(old \| lure) roughly equals the share of lures that end on their studied pattern, rises with lure similarity, and comes within 0.15 of young adults' 0.403 on closer lures. | **Failed.** p(old \| lure) is 0.396, against 18.0% of closer lures ending on their studied pattern, more than 0.10 apart. The other two parts hold: p(old \| lure) falls from 0.461 at C1 to 0.361 at C5, and 0.396 is within 0.15 of 0.403. That closeness comes from R2's crossed thresholds (below): R2 calls 39.6% of closer lures and 35.5% of foils old, where people call 40.3% and 2.6%. |
| 2. Under R2, LDI falls as lures grow more similar, the human direction; under R1 it keeps rising, as in E8. | **Failed.** R2 never answers similar, so its LDI is 0.000 at every level and bin. R1's half held: LDI 0.062 at C1 against −0.086 at C5 (highest at C2, 0.084), and 0.305 at L1 against −0.097 at L5 on other-drawer lures. |
| 3. REC at 128 drawings is at least 0.6 under both readouts. | **Failed.** R1 0.724 held; R2 0.432. |
| 4. Removing CA3's recurrent connections drops p(old \| lure) under R2 by at least half; removing DG raises it. | **Failed.** Without recurrent connections R2 has no signal, so p(old \| lure) is 0.000, a half that holds by construction. Without DG it is also 0.000, below intact (0.396), not above: no lure or foil ends on a stored pattern, and R2 calls almost every item new (REC 0.001). |
| 5. Thinning the perforant path lowers p(old \| lure) under R2. | **Held at all three levels.** 0.393, 0.380 and 0.354 with 75%, 50% and 25% of connections kept, against 0.396 intact (lower in 5, 8 and 8 of 10 seeds), and fewer lures end on their studied pattern: 16.6%, 15.5% and 11.9% against 18.0%. Old answers to foils fall too (34.6%, 33.0% and 31.4% against 35.5%). Older adults call more lures old than young adults (54.6% against 40.3% at ages 60 to 74), so this runs against the ageing pattern, as the prediction stated. |
| 6. With four drawings per character, the intact model's LDI beats the vision-code baseline under at least one readout. | **Failed.** On other-drawer lures R1 scores 0.326 and R2 0.000, against 0.494 for the vision code. |

**R2's thresholds cross.** On the background runs at 128 drawings, the repeat target puts R2's θ_old at 0.2662 and the foil target puts θ_new at 0.2761, above it. The decision rule checks old first, so R2 works as a single threshold: old above 0.2662, new below, never similar. The foil target is then not met; on background foils R2 calls 39.8% old. The protocol said a crossing would be reported but not how answers should then be assigned. Nothing was changed after the crossing was seen, and every R2 number here uses the thresholds as calibrated. Thresholds also cross for R1 without DG and for every lesion arm calibrated on its own under R2; both are secondary scores.

## What the numbers show

- **Attractor dynamics carry every cue onto a stored pattern, and most lures onto the wrong one.** Repeats end on their own pattern 99.7% of the time, and every foil and every lure ends on some stored pattern (nearest-pattern overlap 1.000 for repeats, lures and foils, in every seed). Only 18.0% of closer lures end on their studied pattern, from 33.9% at C1 to 7.5% at C5; every other lure ends on another studied drawing's pattern. For other-drawer lures the share is 17.8%.
- **R1 calls few lures old and hardly tells closer lures from foils.** CA1 returns the code of whichever drawing CA3 ends on, so most closer lures are compared with an unrelated drawing: R1 calls 74.3% of them new, 23.2% similar and 2.4% old, against 77.3% new and 22.7% similar for foils. Almost all of its old answers to lures come at C1 (11.7%, against 0.5% at C2). On other-drawer lures R1 does better, LDI 0.121, again highest for the most similar bin (0.305 at L1), as in E8.
- **R2's signal differs little between repeats, lures and foils.** The final state's median self-support is 0.278 for repeats, 0.262 for closer lures and 0.261 for foils. Closer lures that end on their studied pattern are called old 69.2% of the time, other closer lures 33.1%, foils 35.5% and repeats 78.7%.
- **The starting state separates repeats from everything else.** Cue self-support is 0.233 for repeats, 0.052 for closer lures, 0.049 for other-drawer lures and 0.049 for foils. It was logged as a diagnostic, not scored as a readout. Deciding from it now would choose a readout after seeing evaluation data, so testing it needs a new experiment with its own protocol, written before any run, and a test set it has not seen; that experiment, E8c, is being designed.
- **The vision code alone discriminates closer lures far better than people.** LDI 0.768 against 0.360. Its old threshold sits at a cosine of 1.0000, an exact repeat, and its new threshold at 0.6253, below the median cosine of the least similar closer level (0.697), so it calls 93.9% of closer lures similar and none old. On other-drawer lures it scores 0.235, above the intact model's 0.121.
- **Without DG, recognition halves.** REC falls to 0.351 under R1: repeats end on their own pattern only 53.0% of the time, and the model calls half of them similar (49.6%). Removing CA3's recurrent connections or all of CA3 leaves REC near intact (0.700 and 0.726). With fixed thresholds all three lesions raise LDI on closer lures above intact (0.102, 0.115 and 0.103 against 0.006, lower than intact in 0 of 10 seeds), because they call more lures and more foils similar (foils 58.5%, 85.0% and 40.1% against 22.7%).
- **Thinning the perforant path changes R1 little.** REC 0.722, 0.719 and 0.676 and closer-lure LDI 0.005, 0.027 and 0.042 with 75%, 50% and 25% kept, against 0.724 and 0.006 intact. Adults aged 60 to 74 score LDI 0.113 and REC 0.774.
- **Recognition holds up to the human list length and falls past it.** With the thresholds set at 128 drawings, R1's REC is 1.000 at 20 drawings, 0.995 at 50, 0.890 at 100, 0.724 at 128, 0.182 at 200 and 0.031 at 256. With thresholds set again at each load, it stays between 0.718 and 0.782 from 20 to 256 drawings. LDI on other-drawer lures falls with load, from 0.309 at 20 drawings to 0.045 at 256. R2's signal shrinks as the list grows (its θ_old, set at each load, falls from 0.7153 at 20 drawings to 0.1565 at 256), so with the 128-drawing thresholds it calls nearly every item old up to 100 drawings and every item new at 200 and 256.
- **More drawings per character raise discrimination, and the vision code gains more.** With 2 and 4 drawings per character, R1's LDI on other-drawer lures rises from 0.121 to 0.221 and 0.326, the vision code's from 0.235 to 0.349 and 0.494. On closer lures R1 scores 0.041 and 0.073.

## What it means

Neither readout reproduces how people treat a similar lure, at the human list length, at human proportions and with lures as close as the human task's. In this circuit attractor dynamics end every cue on some stored pattern, foils included, and for 82% of closer lures that pattern belongs to another studied drawing. So the CA1 comparator, which sees whichever drawing CA3 ends on, calls most closer lures new and calls them similar no more often than foils (LDI 0.006). CA3's self-support in the final state cannot act as a recall signal here, because every final state is a stored pattern and every stored pattern supports itself about equally (median 0.278 for repeats, 0.261 for foils); its p(old | lure) of 0.396 sits near people's 0.403 only because its thresholds cross, which turns it into a one-threshold rule that also calls 35.5% of foils old. The starting state still carries what the final state loses: the cue's self-support is 0.233 for repeats and about 0.05 for lures and foils. That number was logged, not used to decide, and whether it can serve as a recognition signal is a question for a new experiment with its own protocol and a clean test set. The larger network did fix one problem E8 found: recognition now holds at the human list length (REC 0.724) and falls only past it.

## Run record

Each evaluation condition was scored once. The first launch of the main evaluation run (128 drawings, every arm) stopped at 13:35, seven seconds after it started and before any seed ran, because a second job was unpacking the evaluation alphabets into the same folder at the same moment. It was relaunched unchanged at 13:37 and completed. A fix to the unpacking step, with a test, is being made on the next branch.

## Tables

Built by `scripts/make_e8b_table.py` from `results/e8b_*.json`, with the thresholds in `results/e8b_calibration.json` and the closer-lure levels in `results/e8b_lure_levels.json`. Means over seeds ± one standard deviation; rates in percent. Fixed thresholds: the intact model's, set at 128 drawings on background alphabets, for every arm and condition (the vision-code baseline keeps its own).

### Calibration on background alphabets, 128 drawings

| Readout | Arm | θ_old | θ_new | Room for similar |
|---|---|---|---|---|
| R1 (CA1 comparator) | Intact | 0.9449 (tie share 0.440) | 0.5735 (tie share 0.700) | yes |
| R1 (CA1 comparator) | No CA3 recurrent connections | 0.9432 (tie share 0.440) | 0.6446 (tie share 0.400) | yes |
| R1 (CA1 comparator) | No CA3 (EC to CA1 only) | 0.9450 (tie share 0.440) | 0.7198 (tie share 0.400) | yes |
| R1 (CA1 comparator) | Vision code alone (baseline) | 1.0000 (tie share 0.529) | 0.6253 (tie share 0.400) | yes |
| R1 (CA1 comparator) | No DG | 0.6021 (tie share 0.440) | 0.6093 (tie share 0.400) | no |
| R1 (CA1 comparator) | Perforant path, 75% kept | 0.9449 (tie share 0.440) | 0.5686 (tie share 0.400) | yes |
| R1 (CA1 comparator) | Perforant path, 50% kept | 0.9448 (tie share 0.440) | 0.5610 (tie share 0.400) | yes |
| R1 (CA1 comparator) | Perforant path, 25% kept | 0.9385 (tie share 0.440) | 0.5395 (tie share 0.400) | yes |
| R2 (CA3 self-support) | Intact | 0.2662 (tie share 0.220) | 0.2761 (tie share 0.467) | no |
| R2 (CA3 self-support) | Vision code alone (baseline) | 1.0000 (tie share 0.529) | 0.6253 (tie share 0.400) | yes |
| R2 (CA3 self-support) | No DG | 0.0811 (tie share 0.440) | 0.0820 (tie share 0.400) | no |
| R2 (CA3 self-support) | Perforant path, 75% kept | 0.2661 (tie share 0.813) | 0.2752 (tie share 0.133) | no |
| R2 (CA3 self-support) | Perforant path, 50% kept | 0.2658 (tie share 0.480) | 0.2749 (tie share 0.133) | no |
| R2 (CA3 self-support) | Perforant path, 25% kept | 0.2634 (tie share 0.720) | 0.2739 (tie share 0.700) | no |

Per-load thresholds, intact model:

| Readout | Condition | θ_old | θ_new |
|---|---|---|---|
| R1 (CA1 comparator) | 20 drawings, per character 1 | 0.9955 | 0.4967 |
| R1 (CA1 comparator) | 50 drawings, per character 1 | 0.9837 | 0.5365 |
| R1 (CA1 comparator) | 100 drawings, per character 1 | 0.9577 | 0.5659 |
| R1 (CA1 comparator) | 128 drawings, per character 2 | 0.9408 | 0.5720 |
| R1 (CA1 comparator) | 128 drawings, per character 4 | 0.9359 | 0.5686 |
| R1 (CA1 comparator) | 200 drawings, per character 1 | 0.9092 | 0.5752 |
| R1 (CA1 comparator) | 256 drawings, per character 1 | 0.8829 | 0.5756 |
| R2 (CA3 self-support) | 20 drawings, per character 1 | 0.7153 | 0.7667 |
| R2 (CA3 self-support) | 50 drawings, per character 1 | 0.4865 | 0.5154 |
| R2 (CA3 self-support) | 100 drawings, per character 1 | 0.3178 | 0.3307 |
| R2 (CA3 self-support) | 128 drawings, per character 2 | 0.2670 | 0.2765 |
| R2 (CA3 self-support) | 128 drawings, per character 4 | 0.2672 | 0.2758 |
| R2 (CA3 self-support) | 200 drawings, per character 1 | 0.1900 | 0.1922 |
| R2 (CA3 self-support) | 256 drawings, per character 1 | 0.1565 | 0.1570 |

Closer-lure levels (background drawings, median vision-code cosine with the undistorted drawing): C1 magnitude 0.006, target 0.966, reached 0.966; C2 magnitude 0.038, target 0.899, reached 0.899; C3 magnitude 0.112, target 0.832, reached 0.832; C4 magnitude 0.340, target 0.764, reached 0.764; C5 magnitude 0.535, target 0.697, reached 0.697.

### Predictions, scored as the protocol fixes

| Prediction | Held | Numbers |
|---|---|---|
| 1 | no | closer lures, R2: p(old | lure) 0.396 against 0.180 settling onto the studied pattern (not within 0.10); by level C1 to C5 0.461, 0.419, 0.373, 0.364, 0.361 (falls); against young adults' 0.403 (within 0.15) |
| 2 (closer lures, scored) | no | R2 LDI C1 to C5: 0.000, 0.000, 0.000, 0.000, 0.000 (not the human direction); R1: 0.062, 0.084, 0.005, -0.036, -0.086 (highest at the most similar) |
| 2 (other-drawer lures, reported) | no | R2 LDI L1 to L5: 0.000, 0.000, 0.000, 0.000, 0.000 (not the human direction); R1: 0.305, 0.216, 0.165, 0.011, -0.097 (highest at the most similar) |
| 3 | no | REC 0.724 (R1) and 0.432 (R2) |
| 4 | no | closer lures, R2: p(old | lure) intact 0.396, without recurrent connections 0.000 (no R2 signal by construction), without DG 0.000 |
| 5 (75% kept) | yes | closer lures, R2: p(old | lure) 0.393 against intact 0.396; lures settling on the studied pattern 16.6% against 18.0% |
| 5 (50% kept) | yes | closer lures, R2: p(old | lure) 0.380 against intact 0.396; lures settling on the studied pattern 15.5% against 18.0% |
| 5 (25% kept) | yes | closer lures, R2: p(old | lure) 0.354 against intact 0.396; lures settling on the studied pattern 11.9% against 18.0% |
| 6 | no | 4 drawings per character, other-drawer lures: intact LDI 0.326 (R1), 0.000 (R2); vision code alone 0.494 |

### Evaluation alphabets, 128 drawings, R1 (CA1 comparator), other-drawer lures, bins L1 to L5, fixed thresholds

| Arm | LDI | REC | p(old \| lure) | LDI L1 | LDI L2 | LDI L3 | LDI L4 | LDI L5 |
|---|---|---|---|---|---|---|---|---|
| Young adults (Stark and colleagues 2013) | 0.360 | 0.786 | 0.403 | not in text | not in text | not in text | not in text | not in text |
| Intact | 0.121 ± 0.029 | 0.724 ± 0.017 | 0.000 ± 0.000 | 0.305 ± 0.057 | 0.216 ± 0.053 | 0.165 ± 0.051 | 0.011 ± 0.052 | -0.097 ± 0.039 |
| No CA3 recurrent connections | 0.082 ± 0.041 | 0.700 ± 0.019 | 0.000 ± 0.000 | 0.212 ± 0.050 | 0.167 ± 0.065 | 0.141 ± 0.046 | 0.018 ± 0.056 | -0.143 ± 0.064 |
| No CA3 (EC to CA1 only) | 0.056 ± 0.020 | 0.726 ± 0.018 | 0.000 ± 0.000 | 0.144 ± 0.025 | 0.113 ± 0.026 | 0.088 ± 0.036 | 0.026 ± 0.034 | -0.099 ± 0.041 |
| No DG | 0.024 ± 0.037 | 0.351 ± 0.022 | 0.000 ± 0.000 | 0.106 ± 0.064 | 0.116 ± 0.048 | 0.042 ± 0.055 | -0.020 ± 0.027 | -0.140 ± 0.069 |
| Perforant path, 75% kept | 0.107 ± 0.026 | 0.722 ± 0.017 | 0.000 ± 0.000 | 0.274 ± 0.061 | 0.187 ± 0.054 | 0.148 ± 0.045 | 0.011 ± 0.058 | -0.095 ± 0.024 |
| Perforant path, 50% kept | 0.103 ± 0.023 | 0.719 ± 0.018 | 0.000 ± 0.000 | 0.242 ± 0.046 | 0.186 ± 0.051 | 0.141 ± 0.037 | 0.019 ± 0.057 | -0.078 ± 0.036 |
| Perforant path, 25% kept | 0.055 ± 0.033 | 0.676 ± 0.018 | 0.000 ± 0.000 | 0.156 ± 0.041 | 0.107 ± 0.052 | 0.077 ± 0.045 | -0.006 ± 0.061 | -0.059 ± 0.037 |
| Vision code alone (baseline) | 0.235 ± 0.023 | 0.804 ± 0.015 | 0.000 ± 0.000 | 0.829 ± 0.016 | 0.467 ± 0.046 | -0.019 ± 0.027 | -0.025 ± 0.037 | -0.043 ± 0.038 |
| No hippocampus | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |

Response rates:

| Arm | old to repeat | similar to repeat | new to repeat | old to lure | similar to lure | new to lure | old to foil | similar to foil | new to foil |
|---|---|---|---|---|---|---|---|---|---|
| Young adults, 20 to 39 | 81.2 | 11.7 | 4.1 | 40.3 | 47.6 | 8.3 | 2.6 | 11.6 | 82.0 |
| Adults 60 to 74 | 82.2 | 7.6 | 5.3 | 54.6 | 23.6 | 12.3 | 4.8 | 12.3 | 73.4 |
| Intact | 72.4 ± 1.7 | 27.4 ± 1.7 | 0.3 ± 0.2 | 0.0 ± 0.0 | 34.8 ± 2.5 | 65.2 ± 2.5 | 0.0 ± 0.0 | 22.7 ± 1.5 | 77.3 ± 1.5 |
| No CA3 recurrent connections | 70.0 ± 1.9 | 29.5 ± 1.9 | 0.5 ± 0.4 | 0.0 ± 0.0 | 66.7 ± 2.2 | 33.3 ± 2.2 | 0.0 ± 0.0 | 58.5 ± 2.8 | 41.5 ± 2.8 |
| No CA3 (EC to CA1 only) | 72.6 ± 1.8 | 27.4 ± 1.8 | 0.0 ± 0.0 | 0.0 ± 0.0 | 90.6 ± 1.4 | 9.4 ± 1.4 | 0.0 ± 0.0 | 85.0 ± 1.8 | 15.0 ± 1.8 |
| No DG | 35.1 ± 2.2 | 49.6 ± 2.5 | 15.3 ± 1.9 | 0.0 ± 0.0 | 42.5 ± 2.9 | 57.5 ± 2.9 | 0.0 ± 0.0 | 40.1 ± 3.0 | 59.9 ± 3.0 |
| Perforant path, 75% kept | 72.2 ± 1.7 | 27.1 ± 1.8 | 0.6 ± 0.3 | 0.0 ± 0.0 | 32.5 ± 2.8 | 67.5 ± 2.8 | 0.0 ± 0.0 | 21.8 ± 1.1 | 78.2 ± 1.1 |
| Perforant path, 50% kept | 71.9 ± 1.8 | 26.2 ± 1.9 | 1.9 ± 0.7 | 0.0 ± 0.0 | 29.5 ± 2.3 | 70.5 ± 2.3 | 0.0 ± 0.0 | 19.2 ± 1.0 | 80.8 ± 1.0 |
| Perforant path, 25% kept | 67.6 ± 1.8 | 21.0 ± 1.6 | 11.3 ± 1.0 | 0.0 ± 0.0 | 20.6 ± 2.6 | 79.4 ± 2.6 | 0.0 ± 0.0 | 15.0 ± 1.7 | 85.0 ± 1.7 |
| Vision code alone (baseline) | 80.4 ± 1.5 | 19.6 ± 1.5 | 0.0 ± 0.0 | 0.0 ± 0.0 | 40.5 ± 2.1 | 59.5 ± 2.1 | 0.0 ± 0.0 | 17.1 ± 1.6 | 82.9 ± 1.6 |
| No hippocampus | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 |

p(old | lure) by level:

| Arm | L1 | L2 | L3 | L4 | L5 |
|---|---|---|---|---|---|
| Intact | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No CA3 recurrent connections | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No CA3 (EC to CA1 only) | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No DG | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 75% kept | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 50% kept | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 25% kept | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Vision code alone (baseline) | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No hippocampus | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |

p(similar | lure) by level:

| Arm | L1 | L2 | L3 | L4 | L5 |
|---|---|---|---|---|---|
| Intact | 53.2 ± 5.7 | 44.3 ± 4.3 | 39.1 ± 4.8 | 23.8 ± 5.6 | 13.0 ± 3.5 |
| No CA3 recurrent connections | 79.7 ± 5.0 | 75.2 ± 5.3 | 72.6 ± 4.0 | 60.3 ± 3.8 | 44.2 ± 5.3 |
| No CA3 (EC to CA1 only) | 99.4 ± 0.9 | 96.2 ± 1.7 | 93.8 ± 3.7 | 87.6 ± 2.9 | 75.1 ± 4.4 |
| No DG | 50.7 ± 5.8 | 51.8 ± 5.0 | 44.3 ± 4.7 | 38.1 ± 3.7 | 26.1 ± 5.8 |
| Perforant path, 75% kept | 49.2 ± 5.6 | 40.5 ± 5.7 | 36.6 ± 4.6 | 22.9 ± 6.0 | 12.3 ± 2.6 |
| Perforant path, 50% kept | 43.3 ± 4.2 | 37.8 ± 4.8 | 33.2 ± 4.0 | 21.1 ± 6.0 | 11.3 ± 3.7 |
| Perforant path, 25% kept | 30.7 ± 3.8 | 25.8 ± 5.6 | 22.7 ± 3.3 | 14.5 ± 5.4 | 9.2 ± 3.2 |
| Vision code alone (baseline) | 100.0 ± 0.0 | 63.7 ± 5.5 | 15.1 ± 2.1 | 14.6 ± 2.9 | 12.7 ± 3.6 |
| No hippocampus | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |

### Evaluation alphabets, 128 drawings, R1 (CA1 comparator), closer lures, levels C1 to C5, fixed thresholds

| Arm | LDI | REC | p(old \| lure) | LDI C1 | LDI C2 | LDI C3 | LDI C4 | LDI C5 |
|---|---|---|---|---|---|---|---|---|
| Young adults (Stark and colleagues 2013) | 0.360 | 0.786 | 0.403 | not in text | not in text | not in text | not in text | not in text |
| Intact | 0.006 ± 0.023 | 0.724 ± 0.017 | 0.024 ± 0.003 | 0.062 ± 0.028 | 0.084 ± 0.028 | 0.005 ± 0.031 | -0.036 ± 0.020 | -0.086 ± 0.020 |
| No CA3 recurrent connections | 0.102 ± 0.030 | 0.700 ± 0.019 | 0.000 ± 0.000 | 0.193 ± 0.035 | 0.158 ± 0.032 | 0.112 ± 0.024 | 0.067 ± 0.034 | -0.019 ± 0.035 |
| No CA3 (EC to CA1 only) | 0.115 ± 0.018 | 0.726 ± 0.018 | 0.026 ± 0.003 | 0.021 ± 0.022 | 0.146 ± 0.018 | 0.146 ± 0.018 | 0.143 ± 0.018 | 0.118 ± 0.019 |
| No DG | 0.103 ± 0.030 | 0.351 ± 0.022 | 0.000 ± 0.000 | 0.091 ± 0.029 | 0.108 ± 0.027 | 0.126 ± 0.036 | 0.123 ± 0.032 | 0.069 ± 0.035 |
| Perforant path, 75% kept | 0.005 ± 0.021 | 0.722 ± 0.017 | 0.023 ± 0.003 | 0.064 ± 0.031 | 0.076 ± 0.033 | 0.004 ± 0.025 | -0.040 ± 0.018 | -0.077 ± 0.020 |
| Perforant path, 50% kept | 0.027 ± 0.018 | 0.719 ± 0.018 | 0.021 ± 0.003 | 0.082 ± 0.022 | 0.099 ± 0.024 | 0.026 ± 0.020 | -0.020 ± 0.023 | -0.053 ± 0.019 |
| Perforant path, 25% kept | 0.042 ± 0.026 | 0.676 ± 0.018 | 0.016 ± 0.003 | 0.087 ± 0.028 | 0.100 ± 0.028 | 0.036 ± 0.038 | 0.014 ± 0.030 | -0.024 ± 0.026 |
| Vision code alone (baseline) | 0.768 ± 0.020 | 0.804 ± 0.015 | 0.000 ± 0.000 | 0.806 ± 0.018 | 0.798 ± 0.021 | 0.785 ± 0.021 | 0.772 ± 0.021 | 0.681 ± 0.025 |
| No hippocampus | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |

Response rates:

| Arm | old to repeat | similar to repeat | new to repeat | old to lure | similar to lure | new to lure | old to foil | similar to foil | new to foil |
|---|---|---|---|---|---|---|---|---|---|
| Young adults, 20 to 39 | 81.2 | 11.7 | 4.1 | 40.3 | 47.6 | 8.3 | 2.6 | 11.6 | 82.0 |
| Adults 60 to 74 | 82.2 | 7.6 | 5.3 | 54.6 | 23.6 | 12.3 | 4.8 | 12.3 | 73.4 |
| Intact | 72.4 ± 1.7 | 27.4 ± 1.7 | 0.3 ± 0.2 | 2.4 ± 0.3 | 23.2 ± 1.0 | 74.3 ± 1.1 | 0.0 ± 0.0 | 22.7 ± 1.5 | 77.3 ± 1.5 |
| No CA3 recurrent connections | 70.0 ± 1.9 | 29.5 ± 1.9 | 0.5 ± 0.4 | 0.0 ± 0.0 | 68.7 ± 1.5 | 31.3 ± 1.5 | 0.0 ± 0.0 | 58.5 ± 2.8 | 41.5 ± 2.8 |
| No CA3 (EC to CA1 only) | 72.6 ± 1.8 | 27.4 ± 1.8 | 0.0 ± 0.0 | 2.6 ± 0.3 | 96.4 ± 0.4 | 1.0 ± 0.2 | 0.0 ± 0.0 | 85.0 ± 1.8 | 15.0 ± 1.8 |
| No DG | 35.1 ± 2.2 | 49.6 ± 2.5 | 15.3 ± 1.9 | 0.0 ± 0.0 | 50.5 ± 1.9 | 49.5 ± 1.9 | 0.0 ± 0.0 | 40.1 ± 3.0 | 59.9 ± 3.0 |
| Perforant path, 75% kept | 72.2 ± 1.7 | 27.1 ± 1.8 | 0.6 ± 0.3 | 2.3 ± 0.3 | 22.3 ± 1.3 | 75.4 ± 1.4 | 0.0 ± 0.0 | 21.8 ± 1.1 | 78.2 ± 1.1 |
| Perforant path, 50% kept | 71.9 ± 1.8 | 26.2 ± 1.9 | 1.9 ± 0.7 | 2.1 ± 0.3 | 21.8 ± 1.2 | 76.0 ± 1.3 | 0.0 ± 0.0 | 19.2 ± 1.0 | 80.8 ± 1.0 |
| Perforant path, 25% kept | 67.6 ± 1.8 | 21.0 ± 1.6 | 11.3 ± 1.0 | 1.6 ± 0.3 | 19.3 ± 1.4 | 79.1 ± 1.4 | 0.0 ± 0.0 | 15.0 ± 1.7 | 85.0 ± 1.7 |
| Vision code alone (baseline) | 80.4 ± 1.5 | 19.6 ± 1.5 | 0.0 ± 0.0 | 0.0 ± 0.0 | 93.9 ± 0.8 | 6.1 ± 0.8 | 0.0 ± 0.0 | 17.1 ± 1.6 | 82.9 ± 1.6 |
| No hippocampus | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 |

p(old | lure) by level:

| Arm | C1 | C2 | C3 | C4 | C5 |
|---|---|---|---|---|---|
| Intact | 11.7 ± 1.5 | 0.5 ± 0.3 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No CA3 recurrent connections | 0.0 ± 0.1 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No CA3 (EC to CA1 only) | 12.8 ± 1.4 | 0.2 ± 0.2 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No DG | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 75% kept | 11.0 ± 1.4 | 0.4 ± 0.3 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 50% kept | 10.4 ± 1.7 | 0.4 ± 0.3 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 25% kept | 7.9 ± 1.3 | 0.4 ± 0.3 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Vision code alone (baseline) | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No hippocampus | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |

p(similar | lure) by level:

| Arm | C1 | C2 | C3 | C4 | C5 |
|---|---|---|---|---|---|
| Intact | 28.9 ± 1.6 | 31.0 ± 1.8 | 23.2 ± 1.9 | 19.0 ± 0.8 | 14.1 ± 1.1 |
| No CA3 recurrent connections | 77.8 ± 1.9 | 74.3 ± 2.5 | 69.7 ± 1.8 | 65.2 ± 1.8 | 56.6 ± 1.8 |
| No CA3 (EC to CA1 only) | 87.0 ± 1.3 | 99.6 ± 0.3 | 99.6 ± 0.4 | 99.2 ± 0.3 | 96.8 ± 0.7 |
| No DG | 49.3 ± 1.6 | 50.9 ± 2.1 | 52.7 ± 2.9 | 52.4 ± 1.9 | 47.1 ± 2.1 |
| Perforant path, 75% kept | 28.2 ± 2.3 | 29.4 ± 2.8 | 22.2 ± 1.9 | 17.8 ± 1.0 | 14.1 ± 1.6 |
| Perforant path, 50% kept | 27.3 ± 1.6 | 29.0 ± 2.2 | 21.7 ± 1.4 | 17.2 ± 1.7 | 13.9 ± 1.6 |
| Perforant path, 25% kept | 23.7 ± 2.3 | 25.0 ± 2.2 | 18.6 ± 2.4 | 16.5 ± 1.5 | 12.6 ± 1.7 |
| Vision code alone (baseline) | 97.7 ± 0.7 | 96.9 ± 0.9 | 95.5 ± 1.0 | 94.2 ± 0.8 | 85.2 ± 1.7 |
| No hippocampus | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |

### Evaluation alphabets, 128 drawings, R2 (CA3 self-support), other-drawer lures, bins L1 to L5, fixed thresholds

| Arm | LDI | REC | p(old \| lure) | LDI L1 | LDI L2 | LDI L3 | LDI L4 | LDI L5 |
|---|---|---|---|---|---|---|---|---|
| Young adults (Stark and colleagues 2013) | 0.360 | 0.786 | 0.403 | not in text | not in text | not in text | not in text | not in text |
| Intact | 0.000 ± 0.000 | 0.432 ± 0.037 | 0.405 ± 0.043 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| No CA3 recurrent connections | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| No CA3 (EC to CA1 only) | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| No DG | 0.000 ± 0.000 | 0.001 ± 0.001 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| Perforant path, 75% kept | 0.000 ± 0.000 | 0.438 ± 0.051 | 0.394 ± 0.050 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| Perforant path, 50% kept | 0.000 ± 0.000 | 0.447 ± 0.052 | 0.364 ± 0.050 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| Perforant path, 25% kept | 0.000 ± 0.000 | 0.403 ± 0.055 | 0.347 ± 0.045 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| Vision code alone (baseline) | 0.235 ± 0.023 | 0.804 ± 0.015 | 0.000 ± 0.000 | 0.829 ± 0.016 | 0.467 ± 0.046 | -0.019 ± 0.027 | -0.025 ± 0.037 | -0.043 ± 0.038 |
| No hippocampus | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |

Response rates:

| Arm | old to repeat | similar to repeat | new to repeat | old to lure | similar to lure | new to lure | old to foil | similar to foil | new to foil |
|---|---|---|---|---|---|---|---|---|---|
| Young adults, 20 to 39 | 81.2 | 11.7 | 4.1 | 40.3 | 47.6 | 8.3 | 2.6 | 11.6 | 82.0 |
| Adults 60 to 74 | 82.2 | 7.6 | 5.3 | 54.6 | 23.6 | 12.3 | 4.8 | 12.3 | 73.4 |
| Intact | 78.7 ± 2.7 | 0.0 ± 0.0 | 21.3 ± 2.7 | 40.5 ± 4.3 | 0.0 ± 0.0 | 59.5 ± 4.3 | 35.5 ± 3.9 | 0.0 ± 0.0 | 64.5 ± 3.9 |
| No CA3 recurrent connections | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 |
| No CA3 (EC to CA1 only) | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 |
| No DG | 0.1 ± 0.1 | 0.0 ± 0.0 | 99.9 ± 0.1 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 |
| Perforant path, 75% kept | 78.4 ± 2.9 | 0.0 ± 0.0 | 21.6 ± 2.9 | 39.4 ± 5.0 | 0.0 ± 0.0 | 60.6 ± 5.0 | 34.6 ± 5.4 | 0.0 ± 0.0 | 65.4 ± 5.4 |
| Perforant path, 50% kept | 77.6 ± 2.9 | 0.0 ± 0.0 | 22.4 ± 2.9 | 36.4 ± 5.0 | 0.0 ± 0.0 | 63.6 ± 5.0 | 33.0 ± 5.4 | 0.0 ± 0.0 | 67.0 ± 5.4 |
| Perforant path, 25% kept | 71.7 ± 3.0 | 0.0 ± 0.0 | 28.3 ± 3.0 | 34.7 ± 4.5 | 0.0 ± 0.0 | 65.3 ± 4.5 | 31.4 ± 5.5 | 0.0 ± 0.0 | 68.6 ± 5.5 |
| Vision code alone (baseline) | 80.4 ± 1.5 | 19.6 ± 1.5 | 0.0 ± 0.0 | 0.0 ± 0.0 | 40.5 ± 2.1 | 59.5 ± 2.1 | 0.0 ± 0.0 | 17.1 ± 1.6 | 82.9 ± 1.6 |
| No hippocampus | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 |

p(old | lure) by level:

| Arm | L1 | L2 | L3 | L4 | L5 |
|---|---|---|---|---|---|
| Intact | 43.7 ± 5.6 | 39.9 ± 5.8 | 41.1 ± 6.5 | 39.1 ± 4.3 | 39.1 ± 9.1 |
| No CA3 recurrent connections | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No CA3 (EC to CA1 only) | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No DG | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 75% kept | 42.2 ± 8.3 | 38.8 ± 6.6 | 39.5 ± 5.4 | 37.2 ± 5.2 | 39.8 ± 8.9 |
| Perforant path, 50% kept | 38.8 ± 6.0 | 35.5 ± 6.3 | 37.4 ± 4.2 | 35.3 ± 6.1 | 35.8 ± 7.3 |
| Perforant path, 25% kept | 35.7 ± 4.9 | 32.5 ± 5.2 | 36.5 ± 6.2 | 34.8 ± 6.7 | 33.8 ± 5.4 |
| Vision code alone (baseline) | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No hippocampus | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |

p(similar | lure) by level:

| Arm | L1 | L2 | L3 | L4 | L5 |
|---|---|---|---|---|---|
| Intact | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No CA3 recurrent connections | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No CA3 (EC to CA1 only) | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No DG | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 75% kept | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 50% kept | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 25% kept | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Vision code alone (baseline) | 100.0 ± 0.0 | 63.7 ± 5.5 | 15.1 ± 2.1 | 14.6 ± 2.9 | 12.7 ± 3.6 |
| No hippocampus | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |

CA3 state:

| Arm | Cue cells | Repeats on their pattern | Lures on the studied pattern | Foils on a stored pattern | Lures on studied pattern, L1 | Lures on studied pattern, L2 | Lures on studied pattern, L3 | Lures on studied pattern, L4 | Lures on studied pattern, L5 | Nearest-pattern overlap, repeats / lures / foils (logged only) |
|---|---|---|---|---|---|---|---|---|---|---|
| Intact | 68.00 ± 0.00 | 99.7 ± 0.2 | 17.8 ± 1.5 | 100.0 ± 0.0 | 30.6 ± 3.9 | 20.4 ± 3.7 | 16.8 ± 3.6 | 13.7 ± 2.9 | 7.8 ± 2.1 | 1.000 / 1.000 / 1.000 |
| No CA3 recurrent connections | 68.00 ± 0.00 | 37.6 ± 2.9 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.899 / 0.174 / 0.162 |
| No DG | 68.00 ± 0.00 | 53.0 ± 2.7 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.740 / 0.416 / 0.415 |
| Perforant path, 75% kept | 68.00 ± 0.00 | 99.3 ± 0.3 | 16.2 ± 2.1 | 100.0 ± 0.0 | 26.7 ± 4.4 | 17.7 ± 3.5 | 16.4 ± 4.5 | 12.5 ± 3.2 | 7.7 ± 3.0 | 1.000 / 1.000 / 1.000 |
| Perforant path, 50% kept | 68.00 ± 0.00 | 97.9 ± 0.7 | 13.8 ± 1.3 | 100.0 ± 0.0 | 22.1 ± 1.9 | 16.4 ± 3.0 | 13.8 ± 4.4 | 10.5 ± 2.0 | 6.8 ± 2.4 | 1.000 / 1.000 / 1.000 |
| Perforant path, 25% kept | 68.00 ± 0.00 | 87.0 ± 0.9 | 7.4 ± 1.2 | 100.0 ± 0.0 | 12.4 ± 3.7 | 8.0 ± 2.9 | 7.7 ± 1.9 | 5.6 ± 2.7 | 3.3 ± 2.0 | 1.000 / 1.000 / 1.000 |

### Evaluation alphabets, 128 drawings, R2 (CA3 self-support), closer lures, levels C1 to C5, fixed thresholds

| Arm | LDI | REC | p(old \| lure) | LDI C1 | LDI C2 | LDI C3 | LDI C4 | LDI C5 |
|---|---|---|---|---|---|---|---|---|
| Young adults (Stark and colleagues 2013) | 0.360 | 0.786 | 0.403 | not in text | not in text | not in text | not in text | not in text |
| Intact | 0.000 ± 0.000 | 0.432 ± 0.037 | 0.396 ± 0.069 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| No CA3 recurrent connections | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| No CA3 (EC to CA1 only) | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| No DG | 0.000 ± 0.000 | 0.001 ± 0.001 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| Perforant path, 75% kept | 0.000 ± 0.000 | 0.438 ± 0.051 | 0.393 ± 0.060 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| Perforant path, 50% kept | 0.000 ± 0.000 | 0.447 ± 0.052 | 0.380 ± 0.071 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| Perforant path, 25% kept | 0.000 ± 0.000 | 0.403 ± 0.055 | 0.354 ± 0.061 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| Vision code alone (baseline) | 0.768 ± 0.020 | 0.804 ± 0.015 | 0.000 ± 0.000 | 0.806 ± 0.018 | 0.798 ± 0.021 | 0.785 ± 0.021 | 0.772 ± 0.021 | 0.681 ± 0.025 |
| No hippocampus | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |

Response rates:

| Arm | old to repeat | similar to repeat | new to repeat | old to lure | similar to lure | new to lure | old to foil | similar to foil | new to foil |
|---|---|---|---|---|---|---|---|---|---|
| Young adults, 20 to 39 | 81.2 | 11.7 | 4.1 | 40.3 | 47.6 | 8.3 | 2.6 | 11.6 | 82.0 |
| Adults 60 to 74 | 82.2 | 7.6 | 5.3 | 54.6 | 23.6 | 12.3 | 4.8 | 12.3 | 73.4 |
| Intact | 78.7 ± 2.7 | 0.0 ± 0.0 | 21.3 ± 2.7 | 39.6 ± 6.9 | 0.0 ± 0.0 | 60.4 ± 6.9 | 35.5 ± 3.9 | 0.0 ± 0.0 | 64.5 ± 3.9 |
| No CA3 recurrent connections | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 |
| No CA3 (EC to CA1 only) | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 |
| No DG | 0.1 ± 0.1 | 0.0 ± 0.0 | 99.9 ± 0.1 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 |
| Perforant path, 75% kept | 78.4 ± 2.9 | 0.0 ± 0.0 | 21.6 ± 2.9 | 39.3 ± 6.0 | 0.0 ± 0.0 | 60.7 ± 6.0 | 34.6 ± 5.4 | 0.0 ± 0.0 | 65.4 ± 5.4 |
| Perforant path, 50% kept | 77.6 ± 2.9 | 0.0 ± 0.0 | 22.4 ± 2.9 | 38.0 ± 7.1 | 0.0 ± 0.0 | 62.0 ± 7.1 | 33.0 ± 5.4 | 0.0 ± 0.0 | 67.0 ± 5.4 |
| Perforant path, 25% kept | 71.7 ± 3.0 | 0.0 ± 0.0 | 28.3 ± 3.0 | 35.4 ± 6.1 | 0.0 ± 0.0 | 64.6 ± 6.1 | 31.4 ± 5.5 | 0.0 ± 0.0 | 68.6 ± 5.5 |
| Vision code alone (baseline) | 80.4 ± 1.5 | 19.6 ± 1.5 | 0.0 ± 0.0 | 0.0 ± 0.0 | 93.9 ± 0.8 | 6.1 ± 0.8 | 0.0 ± 0.0 | 17.1 ± 1.6 | 82.9 ± 1.6 |
| No hippocampus | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 |

p(old | lure) by level:

| Arm | C1 | C2 | C3 | C4 | C5 |
|---|---|---|---|---|---|
| Intact | 46.1 ± 5.7 | 41.9 ± 6.6 | 37.3 ± 7.6 | 36.4 ± 7.6 | 36.1 ± 7.8 |
| No CA3 recurrent connections | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No CA3 (EC to CA1 only) | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No DG | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 75% kept | 45.1 ± 6.0 | 40.5 ± 6.2 | 37.3 ± 5.7 | 37.3 ± 6.8 | 36.4 ± 6.4 |
| Perforant path, 50% kept | 43.8 ± 6.7 | 40.4 ± 7.4 | 35.9 ± 7.0 | 35.4 ± 6.8 | 34.5 ± 8.2 |
| Perforant path, 25% kept | 40.2 ± 6.4 | 36.9 ± 6.5 | 33.5 ± 5.9 | 33.4 ± 6.8 | 33.1 ± 5.8 |
| Vision code alone (baseline) | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No hippocampus | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |

p(similar | lure) by level:

| Arm | C1 | C2 | C3 | C4 | C5 |
|---|---|---|---|---|---|
| Intact | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No CA3 recurrent connections | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No CA3 (EC to CA1 only) | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No DG | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 75% kept | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 50% kept | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 25% kept | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Vision code alone (baseline) | 97.7 ± 0.7 | 96.9 ± 0.9 | 95.5 ± 1.0 | 94.2 ± 0.8 | 85.2 ± 1.7 |
| No hippocampus | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |

CA3 state:

| Arm | Cue cells | Repeats on their pattern | Lures on the studied pattern | Foils on a stored pattern | Lures on studied pattern, C1 | Lures on studied pattern, C2 | Lures on studied pattern, C3 | Lures on studied pattern, C4 | Lures on studied pattern, C5 | Nearest-pattern overlap, repeats / lures / foils (logged only) |
|---|---|---|---|---|---|---|---|---|---|---|
| Intact | 68.00 ± 0.00 | 99.7 ± 0.2 | 18.0 ± 1.4 | 100.0 ± 0.0 | 33.9 ± 2.2 | 23.8 ± 2.1 | 14.7 ± 2.0 | 10.0 ± 1.3 | 7.5 ± 0.7 | 1.000 / 1.000 / 1.000 |
| No CA3 recurrent connections | 68.00 ± 0.00 | 37.6 ± 2.9 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.899 / 0.175 / 0.162 |
| No DG | 68.00 ± 0.00 | 53.0 ± 2.7 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.740 / 0.415 / 0.415 |
| Perforant path, 75% kept | 68.00 ± 0.00 | 99.3 ± 0.3 | 16.6 ± 1.2 | 100.0 ± 0.0 | 32.0 ± 2.2 | 21.9 ± 2.1 | 13.4 ± 1.8 | 8.9 ± 0.9 | 6.9 ± 1.5 | 1.000 / 1.000 / 1.000 |
| Perforant path, 50% kept | 68.00 ± 0.00 | 97.9 ± 0.7 | 15.5 ± 1.5 | 100.0 ± 0.0 | 29.9 ± 2.4 | 20.7 ± 2.0 | 12.5 ± 1.8 | 8.1 ± 1.6 | 6.4 ± 1.3 | 1.000 / 1.000 / 1.000 |
| Perforant path, 25% kept | 68.00 ± 0.00 | 87.0 ± 0.9 | 11.9 ± 1.3 | 100.0 ± 0.0 | 22.8 ± 2.0 | 16.4 ± 1.8 | 9.0 ± 1.8 | 6.6 ± 1.2 | 4.8 ± 1.2 | 1.000 / 1.000 / 1.000 |

### Each arm with its own thresholds, R1 (CA1 comparator), closer lures (secondary)

| Arm | LDI | REC | p(old \| lure) | LDI C1 | LDI C2 | LDI C3 | LDI C4 | LDI C5 |
|---|---|---|---|---|---|---|---|---|
| Intact | 0.006 ± 0.023 | 0.724 ± 0.017 | 0.024 ± 0.003 | 0.062 ± 0.028 | 0.084 ± 0.028 | 0.005 ± 0.031 | -0.036 ± 0.020 | -0.086 ± 0.020 |
| No CA3 recurrent connections | 0.068 ± 0.031 | 0.720 ± 0.019 | 0.000 ± 0.000 | 0.229 ± 0.036 | 0.140 ± 0.039 | 0.051 ± 0.034 | 0.000 ± 0.031 | -0.079 ± 0.031 |
| No CA3 (EC to CA1 only) | 0.535 ± 0.027 | 0.725 ± 0.018 | 0.026 ± 0.003 | 0.618 ± 0.031 | 0.723 ± 0.023 | 0.643 ± 0.030 | 0.473 ± 0.029 | 0.219 ± 0.029 |
| No DG | 0.000 ± 0.000 | 0.508 ± 0.023 | 0.382 ± 0.010 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| Perforant path, 75% kept | -0.003 ± 0.022 | 0.722 ± 0.017 | 0.023 ± 0.003 | 0.055 ± 0.033 | 0.068 ± 0.033 | -0.005 ± 0.026 | -0.048 ± 0.021 | -0.084 ± 0.021 |
| Perforant path, 50% kept | 0.009 ± 0.021 | 0.720 ± 0.018 | 0.021 ± 0.003 | 0.062 ± 0.021 | 0.079 ± 0.026 | 0.009 ± 0.028 | -0.034 ± 0.027 | -0.071 ± 0.021 |
| Perforant path, 25% kept | 0.013 ± 0.029 | 0.741 ± 0.017 | 0.022 ± 0.004 | 0.032 ± 0.024 | 0.070 ± 0.034 | 0.014 ± 0.040 | -0.004 ± 0.033 | -0.047 ± 0.038 |
| Vision code alone (baseline) | 0.768 ± 0.020 | 0.804 ± 0.015 | 0.000 ± 0.000 | 0.806 ± 0.018 | 0.798 ± 0.021 | 0.785 ± 0.021 | 0.772 ± 0.021 | 0.681 ± 0.025 |
| No hippocampus | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |

### Each arm with its own thresholds, R2 (CA3 self-support), closer lures (secondary)

| Arm | LDI | REC | p(old \| lure) | LDI C1 | LDI C2 | LDI C3 | LDI C4 | LDI C5 |
|---|---|---|---|---|---|---|---|---|
| Intact | 0.000 ± 0.000 | 0.432 ± 0.037 | 0.396 ± 0.069 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| No DG | 0.000 ± 0.000 | 0.382 ± 0.083 | 0.309 ± 0.118 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| Perforant path, 75% kept | 0.000 ± 0.000 | 0.437 ± 0.051 | 0.395 ± 0.060 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| Perforant path, 50% kept | 0.000 ± 0.000 | 0.445 ± 0.054 | 0.389 ± 0.070 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| Perforant path, 25% kept | 0.000 ± 0.000 | 0.383 ± 0.054 | 0.433 ± 0.065 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| Vision code alone (baseline) | 0.768 ± 0.020 | 0.804 ± 0.015 | 0.000 ± 0.000 | 0.806 ± 0.018 | 0.798 ± 0.021 | 0.785 ± 0.021 | 0.772 ± 0.021 | 0.681 ± 0.025 |
| No hippocampus | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |

### What R2 tracks, intact model, evaluation alphabets, 128 drawings

| Lure set | Lures on studied pattern | p(old \| lure) if on it | p(old \| lure) otherwise | R2 median, repeats / lures / foils | Nearest-pattern overlap, repeats / lures / foils (logged only) | Cue self-support, repeats / lures / foils |
|---|---|---|---|---|---|---|
| other-drawer lures, bins L1 to L5 | 17.8 ± 1.5 | 68.6 ± 6.1 | 34.4 ± 4.7 | 0.278 / 0.263 / 0.261 | 1.000 / 1.000 / 1.000 | 0.233 / 0.049 / 0.049 |
| closer lures, levels C1 to C5 | 18.0 ± 1.4 | 69.2 ± 4.7 | 33.1 ± 7.4 | 0.278 / 0.262 / 0.261 | 1.000 / 1.000 / 1.000 | 0.233 / 0.052 / 0.049 |

### Seeds in which each lesion effect holds, closer lures, fixed thresholds

| Lesion | Readout | LDI below intact | REC below intact | p(old \| lure) below intact |
|---|---|---|---|---|
| No CA3 recurrent connections | R1 (CA1 comparator) | 0 of 10 | 10 of 10 | 10 of 10 |
| No CA3 (EC to CA1 only) | R1 (CA1 comparator) | 0 of 10 | 0 of 10 | 3 of 10 |
| No DG | R1 (CA1 comparator) | 0 of 10 | 10 of 10 | 10 of 10 |
| Perforant path, 75% kept | R1 (CA1 comparator) | 5 of 10 | 5 of 10 | 8 of 10 |
| Perforant path, 50% kept | R1 (CA1 comparator) | 1 of 10 | 10 of 10 | 9 of 10 |
| Perforant path, 25% kept | R1 (CA1 comparator) | 1 of 10 | 10 of 10 | 10 of 10 |
| Vision code alone (baseline) | R1 (CA1 comparator) | 0 of 10 | 0 of 10 | 10 of 10 |
| No CA3 recurrent connections | R2 (CA3 self-support) | 0 of 10 | 10 of 10 | 10 of 10 |
| No CA3 (EC to CA1 only) | R2 (CA3 self-support) | 0 of 10 | 10 of 10 | 10 of 10 |
| No DG | R2 (CA3 self-support) | 0 of 10 | 10 of 10 | 10 of 10 |
| Perforant path, 75% kept | R2 (CA3 self-support) | 0 of 10 | 4 of 10 | 5 of 10 |
| Perforant path, 50% kept | R2 (CA3 self-support) | 0 of 10 | 3 of 10 | 8 of 10 |
| Perforant path, 25% kept | R2 (CA3 self-support) | 0 of 10 | 8 of 10 | 8 of 10 |
| Vision code alone (baseline) | R2 (CA3 self-support) | 0 of 10 | 0 of 10 | 10 of 10 |

### Load and interference, evaluation alphabets, R1 (CA1 comparator), other-drawer lures, bins L1 to L5, fixed thresholds

| Condition | Arm | LDI | REC | p(old \| repeat) | p(similar \| lure) | p(old \| lure) | p(old \| foil) | Lures on studied pattern |
|---|---|---|---|---|---|---|---|---|
| 20 drawings | Intact | 0.309 ± 0.028 | 1.000 ± 0.000 | 100.0 ± 0.0 | 37.6 ± 2.4 | 0.0 ± 0.0 | 0.0 ± 0.0 | 51.4 ± 2.5 |
| 20 drawings | No CA3 recurrent connections | 0.321 ± 0.026 | 1.000 ± 0.001 | 100.0 ± 0.1 | 62.8 ± 1.9 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 20 drawings | No CA3 (EC to CA1 only) | 0.286 ± 0.030 | 1.000 ± 0.000 | 100.0 ± 0.0 | 83.3 ± 1.7 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 20 drawings | Vision code alone (baseline) | 0.277 ± 0.017 | 1.000 ± 0.000 | 100.0 ± 0.0 | 31.1 ± 1.6 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 50 drawings | Intact | 0.229 ± 0.026 | 0.995 ± 0.003 | 99.5 ± 0.3 | 36.5 ± 2.5 | 0.0 ± 0.0 | 0.0 ± 0.0 | 36.1 ± 2.6 |
| 50 drawings | No CA3 recurrent connections | 0.180 ± 0.020 | 0.992 ± 0.005 | 99.2 ± 0.5 | 71.9 ± 1.7 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 50 drawings | No CA3 (EC to CA1 only) | 0.127 ± 0.014 | 0.995 ± 0.004 | 99.5 ± 0.4 | 87.8 ± 1.2 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 50 drawings | Vision code alone (baseline) | 0.255 ± 0.024 | 0.799 ± 0.011 | 79.9 ± 1.1 | 33.8 ± 2.1 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 100 drawings | Intact | 0.156 ± 0.019 | 0.890 ± 0.016 | 89.0 ± 1.6 | 35.7 ± 2.5 | 0.0 ± 0.0 | 0.0 ± 0.0 | 22.7 ± 1.9 |
| 100 drawings | No CA3 recurrent connections | 0.096 ± 0.021 | 0.875 ± 0.016 | 87.5 ± 1.6 | 69.6 ± 1.4 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 100 drawings | No CA3 (EC to CA1 only) | 0.060 ± 0.024 | 0.890 ± 0.016 | 89.0 ± 1.6 | 90.3 ± 1.3 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 100 drawings | Vision code alone (baseline) | 0.234 ± 0.031 | 0.811 ± 0.013 | 81.1 ± 1.3 | 37.7 ± 2.4 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings | Intact | 0.121 ± 0.029 | 0.724 ± 0.017 | 72.4 ± 1.7 | 34.8 ± 2.5 | 0.0 ± 0.0 | 0.0 ± 0.0 | 17.8 ± 1.5 |
| 128 drawings | No CA3 recurrent connections | 0.082 ± 0.041 | 0.700 ± 0.019 | 70.0 ± 1.9 | 66.7 ± 2.2 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 128 drawings | No CA3 (EC to CA1 only) | 0.056 ± 0.020 | 0.726 ± 0.018 | 72.6 ± 1.8 | 90.6 ± 1.4 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings | Vision code alone (baseline) | 0.235 ± 0.023 | 0.804 ± 0.015 | 80.4 ± 1.5 | 40.5 ± 2.1 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 200 drawings | Intact | 0.073 ± 0.030 | 0.182 ± 0.017 | 18.2 ± 1.7 | 33.8 ± 3.9 | 0.0 ± 0.0 | 0.0 ± 0.0 | 9.8 ± 1.5 |
| 200 drawings | No CA3 recurrent connections | 0.050 ± 0.037 | 0.146 ± 0.013 | 14.6 ± 1.3 | 61.6 ± 2.5 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 200 drawings | No CA3 (EC to CA1 only) | 0.045 ± 0.030 | 0.192 ± 0.018 | 19.2 ± 1.8 | 91.1 ± 1.5 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 200 drawings | Vision code alone (baseline) | 0.183 ± 0.023 | 0.806 ± 0.014 | 80.6 ± 1.4 | 43.1 ± 2.2 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 256 drawings | Intact | 0.045 ± 0.040 | 0.031 ± 0.008 | 3.1 ± 0.8 | 32.7 ± 3.2 | 0.0 ± 0.0 | 0.0 ± 0.0 | 5.8 ± 1.5 |
| 256 drawings | No CA3 recurrent connections | 0.038 ± 0.019 | 0.012 ± 0.003 | 1.2 ± 0.3 | 57.8 ± 1.6 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 256 drawings | No CA3 (EC to CA1 only) | 0.035 ± 0.017 | 0.038 ± 0.009 | 3.8 ± 0.9 | 90.6 ± 0.9 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 256 drawings | Vision code alone (baseline) | 0.176 ± 0.031 | 0.800 ± 0.013 | 80.0 ± 1.3 | 45.6 ± 2.6 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings, 2 per character | Intact | 0.221 ± 0.036 | 0.704 ± 0.032 | 70.4 ± 3.2 | 43.1 ± 3.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 15.3 ± 0.9 |
| 128 drawings, 2 per character | No CA3 recurrent connections | 0.161 ± 0.026 | 0.678 ± 0.033 | 67.8 ± 3.3 | 72.3 ± 2.6 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 128 drawings, 2 per character | No CA3 (EC to CA1 only) | 0.114 ± 0.025 | 0.707 ± 0.031 | 70.7 ± 3.1 | 93.5 ± 0.9 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings, 2 per character | Vision code alone (baseline) | 0.349 ± 0.027 | 0.800 ± 0.011 | 80.0 ± 1.1 | 51.6 ± 2.4 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings, 4 per character | Intact | 0.326 ± 0.033 | 0.645 ± 0.035 | 64.5 ± 3.5 | 53.0 ± 2.3 | 0.0 ± 0.0 | 0.0 ± 0.0 | 11.3 ± 0.8 |
| 128 drawings, 4 per character | No CA3 recurrent connections | 0.228 ± 0.025 | 0.609 ± 0.035 | 60.9 ± 3.5 | 77.2 ± 1.8 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 128 drawings, 4 per character | No CA3 (EC to CA1 only) | 0.133 ± 0.021 | 0.650 ± 0.033 | 65.0 ± 3.3 | 95.1 ± 1.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings, 4 per character | Vision code alone (baseline) | 0.494 ± 0.020 | 0.798 ± 0.012 | 79.8 ± 1.2 | 64.4 ± 2.4 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |

### Load and interference, evaluation alphabets, R1 (CA1 comparator), other-drawer lures, bins L1 to L5, thresholds set again at each condition (secondary)

| Condition | Arm | LDI | REC | p(old \| repeat) | p(similar \| lure) | p(old \| lure) | p(old \| foil) | Lures on studied pattern |
|---|---|---|---|---|---|---|---|---|
| 20 drawings | Intact | 0.353 ± 0.027 | 0.782 ± 0.016 | 78.2 ± 1.6 | 58.0 ± 2.3 | 0.0 ± 0.0 | 0.0 ± 0.0 | 51.4 ± 2.5 |
| 20 drawings | Vision code alone (baseline) | 0.422 ± 0.031 | 0.813 ± 0.001 | 81.3 ± 0.1 | 65.8 ± 1.7 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 50 drawings | Intact | 0.240 ± 0.036 | 0.756 ± 0.015 | 75.6 ± 1.5 | 46.8 ± 2.4 | 0.0 ± 0.0 | 0.0 ± 0.0 | 36.1 ± 2.6 |
| 50 drawings | Vision code alone (baseline) | 0.323 ± 0.020 | 0.808 ± 0.010 | 80.8 ± 1.0 | 54.3 ± 2.2 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 100 drawings | Intact | 0.148 ± 0.022 | 0.763 ± 0.021 | 76.3 ± 2.1 | 37.3 ± 2.4 | 0.0 ± 0.0 | 0.0 ± 0.0 | 22.7 ± 1.9 |
| 100 drawings | Vision code alone (baseline) | 0.252 ± 0.033 | 0.811 ± 0.013 | 81.1 ± 1.3 | 42.4 ± 2.7 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 200 drawings | Intact | 0.074 ± 0.032 | 0.718 ± 0.022 | 71.8 ± 2.2 | 33.2 ± 4.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 9.8 ± 1.5 |
| 200 drawings | Vision code alone (baseline) | 0.179 ± 0.024 | 0.807 ± 0.014 | 80.7 ± 1.4 | 36.6 ± 2.6 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 256 drawings | Intact | 0.048 ± 0.040 | 0.737 ± 0.032 | 73.7 ± 3.2 | 31.9 ± 3.2 | 0.0 ± 0.0 | 0.0 ± 0.0 | 5.8 ± 1.5 |
| 256 drawings | Vision code alone (baseline) | 0.159 ± 0.015 | 0.805 ± 0.012 | 80.5 ± 1.2 | 33.0 ± 1.1 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings, 2 per character | Intact | 0.221 ± 0.036 | 0.759 ± 0.027 | 75.9 ± 2.7 | 43.4 ± 3.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 15.3 ± 0.9 |
| 128 drawings, 2 per character | Vision code alone (baseline) | 0.354 ± 0.029 | 0.808 ± 0.010 | 80.8 ± 1.0 | 53.4 ± 2.6 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings, 4 per character | Intact | 0.324 ± 0.034 | 0.779 ± 0.032 | 77.9 ± 3.2 | 54.3 ± 2.3 | 0.0 ± 0.0 | 0.0 ± 0.0 | 11.3 ± 0.8 |
| 128 drawings, 4 per character | Vision code alone (baseline) | 0.501 ± 0.019 | 0.807 ± 0.011 | 80.7 ± 1.1 | 68.2 ± 2.4 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |

### Load and interference, evaluation alphabets, R1 (CA1 comparator), closer lures, levels C1 to C5, fixed thresholds

| Condition | Arm | LDI | REC | p(old \| repeat) | p(similar \| lure) | p(old \| lure) | p(old \| foil) | Lures on studied pattern |
|---|---|---|---|---|---|---|---|---|
| 20 drawings | Intact | 0.337 ± 0.017 | 1.000 ± 0.000 | 100.0 ± 0.0 | 40.4 ± 1.3 | 12.2 ± 0.5 | 0.0 ± 0.0 | 52.3 ± 1.8 |
| 20 drawings | No CA3 recurrent connections | 0.335 ± 0.019 | 1.000 ± 0.001 | 100.0 ± 0.1 | 64.2 ± 1.8 | 6.9 ± 0.6 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 20 drawings | No CA3 (EC to CA1 only) | 0.283 ± 0.027 | 1.000 ± 0.000 | 100.0 ± 0.0 | 83.1 ± 0.7 | 16.4 ± 0.6 | 0.0 ± 0.0 |  |
| 20 drawings | Vision code alone (baseline) | 0.897 ± 0.009 | 1.000 ± 0.000 | 100.0 ± 0.0 | 93.1 ± 0.7 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 50 drawings | Intact | 0.149 ± 0.013 | 0.995 ± 0.003 | 99.5 ± 0.3 | 28.6 ± 1.6 | 9.0 ± 0.6 | 0.0 ± 0.0 | 35.6 ± 1.6 |
| 50 drawings | No CA3 recurrent connections | 0.159 ± 0.022 | 0.992 ± 0.005 | 99.2 ± 0.5 | 69.8 ± 2.8 | 1.4 ± 0.2 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 50 drawings | No CA3 (EC to CA1 only) | 0.119 ± 0.015 | 0.995 ± 0.004 | 99.5 ± 0.4 | 87.1 ± 0.7 | 12.4 ± 0.7 | 0.0 ± 0.0 |  |
| 50 drawings | Vision code alone (baseline) | 0.848 ± 0.013 | 0.799 ± 0.011 | 79.9 ± 1.1 | 93.2 ± 0.9 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 100 drawings | Intact | 0.026 ± 0.019 | 0.890 ± 0.016 | 89.0 ± 1.6 | 22.6 ± 1.4 | 4.2 ± 0.4 | 0.0 ± 0.0 | 21.6 ± 1.6 |
| 100 drawings | No CA3 recurrent connections | 0.104 ± 0.028 | 0.875 ± 0.016 | 87.5 ± 1.6 | 70.4 ± 2.1 | 0.1 ± 0.1 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 100 drawings | No CA3 (EC to CA1 only) | 0.097 ± 0.020 | 0.890 ± 0.016 | 89.0 ± 1.6 | 94.1 ± 0.5 | 5.1 ± 0.5 | 0.0 ± 0.0 |  |
| 100 drawings | Vision code alone (baseline) | 0.793 ± 0.013 | 0.811 ± 0.013 | 81.1 ± 1.3 | 93.6 ± 0.7 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings | Intact | 0.006 ± 0.023 | 0.724 ± 0.017 | 72.4 ± 1.7 | 23.2 ± 1.0 | 2.4 ± 0.3 | 0.0 ± 0.0 | 18.0 ± 1.4 |
| 128 drawings | No CA3 recurrent connections | 0.102 ± 0.030 | 0.700 ± 0.019 | 70.0 ± 1.9 | 68.7 ± 1.5 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 128 drawings | No CA3 (EC to CA1 only) | 0.115 ± 0.018 | 0.726 ± 0.018 | 72.6 ± 1.8 | 96.4 ± 0.4 | 2.6 ± 0.3 | 0.0 ± 0.0 |  |
| 128 drawings | Vision code alone (baseline) | 0.768 ± 0.020 | 0.804 ± 0.015 | 80.4 ± 1.5 | 93.9 ± 0.8 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 200 drawings | Intact | -0.009 ± 0.033 | 0.182 ± 0.017 | 18.2 ± 1.7 | 25.5 ± 2.4 | 0.1 ± 0.1 | 0.0 ± 0.0 | 10.4 ± 1.1 |
| 200 drawings | No CA3 recurrent connections | 0.088 ± 0.025 | 0.146 ± 0.013 | 14.6 ± 1.3 | 65.3 ± 1.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 200 drawings | No CA3 (EC to CA1 only) | 0.117 ± 0.015 | 0.192 ± 0.018 | 19.2 ± 1.8 | 98.3 ± 0.3 | 0.2 ± 0.1 | 0.0 ± 0.0 |  |
| 200 drawings | Vision code alone (baseline) | 0.690 ± 0.016 | 0.806 ± 0.014 | 80.6 ± 1.4 | 93.8 ± 1.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 256 drawings | Intact | -0.006 ± 0.020 | 0.031 ± 0.008 | 3.1 ± 0.8 | 27.5 ± 2.3 | 0.0 ± 0.0 | 0.0 ± 0.0 | 6.3 ± 0.9 |
| 256 drawings | No CA3 recurrent connections | 0.076 ± 0.029 | 0.012 ± 0.003 | 1.2 ± 0.3 | 61.6 ± 1.8 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 256 drawings | No CA3 (EC to CA1 only) | 0.108 ± 0.013 | 0.038 ± 0.009 | 3.8 ± 0.9 | 98.0 ± 0.3 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 256 drawings | Vision code alone (baseline) | 0.664 ± 0.018 | 0.800 ± 0.013 | 80.0 ± 1.3 | 94.5 ± 0.8 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings, 2 per character | Intact | 0.041 ± 0.020 | 0.704 ± 0.032 | 70.4 ± 3.2 | 25.1 ± 2.2 | 2.1 ± 0.2 | 0.0 ± 0.0 | 17.9 ± 1.4 |
| 128 drawings, 2 per character | No CA3 recurrent connections | 0.139 ± 0.029 | 0.678 ± 0.033 | 67.8 ± 3.3 | 70.1 ± 1.5 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 128 drawings, 2 per character | No CA3 (EC to CA1 only) | 0.147 ± 0.023 | 0.707 ± 0.031 | 70.7 ± 3.1 | 96.8 ± 0.3 | 2.4 ± 0.3 | 0.0 ± 0.0 |  |
| 128 drawings, 2 per character | Vision code alone (baseline) | 0.776 ± 0.017 | 0.800 ± 0.011 | 80.0 ± 1.1 | 94.3 ± 0.6 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings, 4 per character | Intact | 0.073 ± 0.024 | 0.645 ± 0.035 | 64.5 ± 3.5 | 27.8 ± 1.8 | 1.7 ± 0.3 | 0.0 ± 0.0 | 17.1 ± 1.2 |
| 128 drawings, 4 per character | No CA3 recurrent connections | 0.165 ± 0.037 | 0.609 ± 0.035 | 60.9 ± 3.5 | 70.9 ± 3.3 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 128 drawings, 4 per character | No CA3 (EC to CA1 only) | 0.158 ± 0.021 | 0.650 ± 0.033 | 65.0 ± 3.3 | 97.6 ± 0.3 | 2.0 ± 0.3 | 0.0 ± 0.0 |  |
| 128 drawings, 4 per character | Vision code alone (baseline) | 0.805 ± 0.022 | 0.798 ± 0.012 | 79.8 ± 1.2 | 95.6 ± 0.8 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |

### Load and interference, evaluation alphabets, R1 (CA1 comparator), closer lures, levels C1 to C5, thresholds set again at each condition (secondary)

| Condition | Arm | LDI | REC | p(old \| repeat) | p(similar \| lure) | p(old \| lure) | p(old \| foil) | Lures on studied pattern |
|---|---|---|---|---|---|---|---|---|
| 20 drawings | Intact | 0.321 ± 0.022 | 0.782 ± 0.016 | 78.2 ± 1.6 | 54.7 ± 1.8 | 1.2 ± 0.1 | 0.0 ± 0.0 | 52.3 ± 1.8 |
| 20 drawings | Vision code alone (baseline) | 0.748 ± 0.023 | 0.813 ± 0.001 | 81.3 ± 0.1 | 98.3 ± 0.6 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 50 drawings | Intact | 0.151 ± 0.018 | 0.756 ± 0.015 | 75.6 ± 1.5 | 37.9 ± 2.2 | 1.9 ± 0.2 | 0.0 ± 0.0 | 35.6 ± 1.6 |
| 50 drawings | Vision code alone (baseline) | 0.747 ± 0.019 | 0.808 ± 0.010 | 80.8 ± 1.0 | 96.7 ± 0.7 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 100 drawings | Intact | 0.027 ± 0.012 | 0.763 ± 0.021 | 76.3 ± 2.1 | 25.2 ± 1.4 | 2.4 ± 0.3 | 0.0 ± 0.0 | 21.6 ± 1.6 |
| 100 drawings | Vision code alone (baseline) | 0.772 ± 0.015 | 0.811 ± 0.013 | 81.1 ± 1.3 | 94.4 ± 0.8 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 200 drawings | Intact | -0.024 ± 0.033 | 0.718 ± 0.022 | 71.8 ± 2.2 | 23.4 ± 2.3 | 2.0 ± 0.3 | 0.0 ± 0.0 | 10.4 ± 1.1 |
| 200 drawings | Vision code alone (baseline) | 0.735 ± 0.020 | 0.807 ± 0.014 | 80.7 ± 1.4 | 92.3 ± 1.1 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 256 drawings | Intact | -0.016 ± 0.021 | 0.737 ± 0.032 | 73.7 ± 3.2 | 25.5 ± 2.4 | 1.3 ± 0.3 | 0.0 ± 0.0 | 6.3 ± 0.9 |
| 256 drawings | Vision code alone (baseline) | 0.745 ± 0.021 | 0.805 ± 0.012 | 80.5 ± 1.2 | 91.6 ± 1.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings, 2 per character | Intact | 0.035 ± 0.020 | 0.759 ± 0.027 | 75.9 ± 2.7 | 24.9 ± 2.2 | 2.5 ± 0.2 | 0.0 ± 0.0 | 17.9 ± 1.4 |
| 128 drawings, 2 per character | Vision code alone (baseline) | 0.767 ± 0.019 | 0.808 ± 0.010 | 80.8 ± 1.0 | 94.7 ± 0.6 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings, 4 per character | Intact | 0.054 ± 0.024 | 0.779 ± 0.032 | 77.9 ± 3.2 | 27.4 ± 1.8 | 2.9 ± 0.4 | 0.0 ± 0.0 | 17.1 ± 1.2 |
| 128 drawings, 4 per character | Vision code alone (baseline) | 0.783 ± 0.025 | 0.807 ± 0.011 | 80.7 ± 1.1 | 96.4 ± 0.8 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |

### Load and interference, evaluation alphabets, R2 (CA3 self-support), other-drawer lures, bins L1 to L5, fixed thresholds

| Condition | Arm | LDI | REC | p(old \| repeat) | p(similar \| lure) | p(old \| lure) | p(old \| foil) | Lures on studied pattern |
|---|---|---|---|---|---|---|---|---|
| 20 drawings | Intact | 0.000 ± 0.000 | 0.000 ± 0.001 | 100.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.1 | 51.4 ± 2.5 |
| 20 drawings | No CA3 recurrent connections | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 20 drawings | No CA3 (EC to CA1 only) | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 20 drawings | Vision code alone (baseline) | 0.277 ± 0.017 | 1.000 ± 0.000 | 100.0 ± 0.0 | 31.1 ± 1.6 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 50 drawings | Intact | 0.000 ± 0.000 | 0.000 ± 0.000 | 100.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 36.1 ± 2.6 |
| 50 drawings | No CA3 recurrent connections | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 50 drawings | No CA3 (EC to CA1 only) | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 50 drawings | Vision code alone (baseline) | 0.255 ± 0.024 | 0.799 ± 0.011 | 79.9 ± 1.1 | 33.8 ± 2.1 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 100 drawings | Intact | 0.000 ± 0.000 | 0.007 ± 0.014 | 100.0 ± 0.0 | 0.0 ± 0.0 | 99.5 ± 1.0 | 99.3 ± 1.4 | 22.7 ± 1.9 |
| 100 drawings | No CA3 recurrent connections | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 100 drawings | No CA3 (EC to CA1 only) | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 100 drawings | Vision code alone (baseline) | 0.234 ± 0.031 | 0.811 ± 0.013 | 81.1 ± 1.3 | 37.7 ± 2.4 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings | Intact | 0.000 ± 0.000 | 0.432 ± 0.037 | 78.7 ± 2.7 | 0.0 ± 0.0 | 40.5 ± 4.3 | 35.5 ± 3.9 | 17.8 ± 1.5 |
| 128 drawings | No CA3 recurrent connections | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 128 drawings | No CA3 (EC to CA1 only) | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings | Vision code alone (baseline) | 0.235 ± 0.023 | 0.804 ± 0.015 | 80.4 ± 1.5 | 40.5 ± 2.1 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 200 drawings | Intact | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 9.8 ± 1.5 |
| 200 drawings | No CA3 recurrent connections | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 200 drawings | No CA3 (EC to CA1 only) | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 200 drawings | Vision code alone (baseline) | 0.183 ± 0.023 | 0.806 ± 0.014 | 80.6 ± 1.4 | 43.1 ± 2.2 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 256 drawings | Intact | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 5.8 ± 1.5 |
| 256 drawings | No CA3 recurrent connections | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 256 drawings | No CA3 (EC to CA1 only) | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 256 drawings | Vision code alone (baseline) | 0.176 ± 0.031 | 0.800 ± 0.013 | 80.0 ± 1.3 | 45.6 ± 2.6 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings, 2 per character | Intact | 0.000 ± 0.000 | 0.452 ± 0.044 | 79.3 ± 2.4 | 0.0 ± 0.0 | 41.4 ± 4.6 | 34.0 ± 5.4 | 15.3 ± 0.9 |
| 128 drawings, 2 per character | No CA3 recurrent connections | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 128 drawings, 2 per character | No CA3 (EC to CA1 only) | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings, 2 per character | Vision code alone (baseline) | 0.349 ± 0.027 | 0.800 ± 0.011 | 80.0 ± 1.1 | 51.6 ± 2.4 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings, 4 per character | Intact | 0.000 ± 0.000 | 0.431 ± 0.040 | 79.6 ± 2.4 | 0.0 ± 0.0 | 47.3 ± 6.9 | 36.5 ± 4.5 | 11.3 ± 0.8 |
| 128 drawings, 4 per character | No CA3 recurrent connections | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 128 drawings, 4 per character | No CA3 (EC to CA1 only) | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings, 4 per character | Vision code alone (baseline) | 0.494 ± 0.020 | 0.798 ± 0.012 | 79.8 ± 1.2 | 64.4 ± 2.4 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |

### Load and interference, evaluation alphabets, R2 (CA3 self-support), other-drawer lures, bins L1 to L5, thresholds set again at each condition (secondary)

| Condition | Arm | LDI | REC | p(old \| repeat) | p(similar \| lure) | p(old \| lure) | p(old \| foil) | Lures on studied pattern |
|---|---|---|---|---|---|---|---|---|
| 20 drawings | Intact | 0.000 ± 0.000 | 0.172 ± 0.036 | 80.8 ± 2.4 | 0.0 ± 0.0 | 68.6 ± 2.2 | 63.6 ± 2.9 | 51.4 ± 2.5 |
| 20 drawings | Vision code alone (baseline) | 0.422 ± 0.031 | 0.813 ± 0.001 | 81.3 ± 0.1 | 65.8 ± 1.7 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 50 drawings | Intact | 0.000 ± 0.000 | 0.268 ± 0.040 | 79.2 ± 1.6 | 0.0 ± 0.0 | 59.0 ± 2.4 | 52.4 ± 4.4 | 36.1 ± 2.6 |
| 50 drawings | Vision code alone (baseline) | 0.323 ± 0.020 | 0.808 ± 0.010 | 80.8 ± 1.0 | 54.3 ± 2.2 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 100 drawings | Intact | 0.000 ± 0.000 | 0.434 ± 0.029 | 77.9 ± 2.5 | 0.0 ± 0.0 | 40.6 ± 3.3 | 34.6 ± 4.4 | 22.7 ± 1.9 |
| 100 drawings | Vision code alone (baseline) | 0.252 ± 0.033 | 0.811 ± 0.013 | 81.1 ± 1.3 | 42.4 ± 2.7 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 200 drawings | Intact | 0.000 ± 0.000 | 0.553 ± 0.037 | 78.6 ± 2.2 | 0.0 ± 0.0 | 27.1 ± 5.0 | 23.3 ± 4.0 | 9.8 ± 1.5 |
| 200 drawings | Vision code alone (baseline) | 0.179 ± 0.024 | 0.807 ± 0.014 | 80.7 ± 1.4 | 36.6 ± 2.6 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 256 drawings | Intact | 0.000 ± 0.000 | 0.617 ± 0.039 | 76.9 ± 2.3 | 0.0 ± 0.0 | 16.0 ± 4.3 | 15.2 ± 4.4 | 5.8 ± 1.5 |
| 256 drawings | Vision code alone (baseline) | 0.159 ± 0.015 | 0.805 ± 0.012 | 80.5 ± 1.2 | 33.0 ± 1.1 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings, 2 per character | Intact | 0.000 ± 0.000 | 0.454 ± 0.044 | 77.6 ± 2.5 | 0.0 ± 0.0 | 39.5 ± 4.8 | 32.2 ± 5.3 | 15.3 ± 0.9 |
| 128 drawings, 2 per character | Vision code alone (baseline) | 0.354 ± 0.029 | 0.808 ± 0.010 | 80.8 ± 1.0 | 53.4 ± 2.6 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings, 4 per character | Intact | 0.000 ± 0.000 | 0.438 ± 0.035 | 78.0 ± 2.3 | 0.0 ± 0.0 | 44.9 ± 6.6 | 34.2 ± 4.0 | 11.3 ± 0.8 |
| 128 drawings, 4 per character | Vision code alone (baseline) | 0.501 ± 0.019 | 0.807 ± 0.011 | 80.7 ± 1.1 | 68.2 ± 2.4 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |

### Load and interference, evaluation alphabets, R2 (CA3 self-support), closer lures, levels C1 to C5, fixed thresholds

| Condition | Arm | LDI | REC | p(old \| repeat) | p(similar \| lure) | p(old \| lure) | p(old \| foil) | Lures on studied pattern |
|---|---|---|---|---|---|---|---|---|
| 20 drawings | Intact | 0.000 ± 0.000 | 0.000 ± 0.001 | 100.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.1 | 52.3 ± 1.8 |
| 20 drawings | No CA3 recurrent connections | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 20 drawings | No CA3 (EC to CA1 only) | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 20 drawings | Vision code alone (baseline) | 0.897 ± 0.009 | 1.000 ± 0.000 | 100.0 ± 0.0 | 93.1 ± 0.7 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 50 drawings | Intact | 0.000 ± 0.000 | 0.000 ± 0.000 | 100.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 35.6 ± 1.6 |
| 50 drawings | No CA3 recurrent connections | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 50 drawings | No CA3 (EC to CA1 only) | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 50 drawings | Vision code alone (baseline) | 0.848 ± 0.013 | 0.799 ± 0.011 | 79.9 ± 1.1 | 93.2 ± 0.9 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 100 drawings | Intact | 0.000 ± 0.000 | 0.007 ± 0.014 | 100.0 ± 0.0 | 0.0 ± 0.0 | 99.6 ± 0.9 | 99.3 ± 1.4 | 21.6 ± 1.6 |
| 100 drawings | No CA3 recurrent connections | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 100 drawings | No CA3 (EC to CA1 only) | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 100 drawings | Vision code alone (baseline) | 0.793 ± 0.013 | 0.811 ± 0.013 | 81.1 ± 1.3 | 93.6 ± 0.7 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings | Intact | 0.000 ± 0.000 | 0.432 ± 0.037 | 78.7 ± 2.7 | 0.0 ± 0.0 | 39.6 ± 6.9 | 35.5 ± 3.9 | 18.0 ± 1.4 |
| 128 drawings | No CA3 recurrent connections | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 128 drawings | No CA3 (EC to CA1 only) | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings | Vision code alone (baseline) | 0.768 ± 0.020 | 0.804 ± 0.015 | 80.4 ± 1.5 | 93.9 ± 0.8 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 200 drawings | Intact | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 10.4 ± 1.1 |
| 200 drawings | No CA3 recurrent connections | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 200 drawings | No CA3 (EC to CA1 only) | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 200 drawings | Vision code alone (baseline) | 0.690 ± 0.016 | 0.806 ± 0.014 | 80.6 ± 1.4 | 93.8 ± 1.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 256 drawings | Intact | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 6.3 ± 0.9 |
| 256 drawings | No CA3 recurrent connections | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 256 drawings | No CA3 (EC to CA1 only) | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 256 drawings | Vision code alone (baseline) | 0.664 ± 0.018 | 0.800 ± 0.013 | 80.0 ± 1.3 | 94.5 ± 0.8 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings, 2 per character | Intact | 0.000 ± 0.000 | 0.452 ± 0.044 | 79.3 ± 2.4 | 0.0 ± 0.0 | 38.4 ± 7.0 | 34.0 ± 5.4 | 17.9 ± 1.4 |
| 128 drawings, 2 per character | No CA3 recurrent connections | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 128 drawings, 2 per character | No CA3 (EC to CA1 only) | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings, 2 per character | Vision code alone (baseline) | 0.776 ± 0.017 | 0.800 ± 0.011 | 80.0 ± 1.1 | 94.3 ± 0.6 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings, 4 per character | Intact | 0.000 ± 0.000 | 0.431 ± 0.040 | 79.6 ± 2.4 | 0.0 ± 0.0 | 40.8 ± 3.2 | 36.5 ± 4.5 | 17.1 ± 1.2 |
| 128 drawings, 4 per character | No CA3 recurrent connections | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 128 drawings, 4 per character | No CA3 (EC to CA1 only) | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings, 4 per character | Vision code alone (baseline) | 0.805 ± 0.022 | 0.798 ± 0.012 | 79.8 ± 1.2 | 95.6 ± 0.8 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |

### Load and interference, evaluation alphabets, R2 (CA3 self-support), closer lures, levels C1 to C5, thresholds set again at each condition (secondary)

| Condition | Arm | LDI | REC | p(old \| repeat) | p(similar \| lure) | p(old \| lure) | p(old \| foil) | Lures on studied pattern |
|---|---|---|---|---|---|---|---|---|
| 20 drawings | Intact | 0.000 ± 0.000 | 0.172 ± 0.036 | 80.8 ± 2.4 | 0.0 ± 0.0 | 65.9 ± 3.4 | 63.6 ± 2.9 | 52.3 ± 1.8 |
| 20 drawings | Vision code alone (baseline) | 0.748 ± 0.023 | 0.813 ± 0.001 | 81.3 ± 0.1 | 98.3 ± 0.6 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 50 drawings | Intact | 0.000 ± 0.000 | 0.268 ± 0.040 | 79.2 ± 1.6 | 0.0 ± 0.0 | 57.1 ± 1.6 | 52.4 ± 4.4 | 35.6 ± 1.6 |
| 50 drawings | Vision code alone (baseline) | 0.747 ± 0.019 | 0.808 ± 0.010 | 80.8 ± 1.0 | 96.7 ± 0.7 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 100 drawings | Intact | 0.000 ± 0.000 | 0.434 ± 0.029 | 77.9 ± 2.5 | 0.0 ± 0.0 | 38.4 ± 4.4 | 34.6 ± 4.4 | 21.6 ± 1.6 |
| 100 drawings | Vision code alone (baseline) | 0.772 ± 0.015 | 0.811 ± 0.013 | 81.1 ± 1.3 | 94.4 ± 0.8 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 200 drawings | Intact | 0.000 ± 0.000 | 0.553 ± 0.037 | 78.6 ± 2.2 | 0.0 ± 0.0 | 26.9 ± 5.8 | 23.3 ± 4.0 | 10.4 ± 1.1 |
| 200 drawings | Vision code alone (baseline) | 0.735 ± 0.020 | 0.807 ± 0.014 | 80.7 ± 1.4 | 92.3 ± 1.1 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 256 drawings | Intact | 0.000 ± 0.000 | 0.617 ± 0.039 | 76.9 ± 2.3 | 0.0 ± 0.0 | 15.9 ± 5.3 | 15.2 ± 4.4 | 6.3 ± 0.9 |
| 256 drawings | Vision code alone (baseline) | 0.745 ± 0.021 | 0.805 ± 0.012 | 80.5 ± 1.2 | 91.6 ± 1.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings, 2 per character | Intact | 0.000 ± 0.000 | 0.454 ± 0.044 | 77.6 ± 2.5 | 0.0 ± 0.0 | 35.9 ± 8.0 | 32.2 ± 5.3 | 17.9 ± 1.4 |
| 128 drawings, 2 per character | Vision code alone (baseline) | 0.767 ± 0.019 | 0.808 ± 0.010 | 80.8 ± 1.0 | 94.7 ± 0.6 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings, 4 per character | Intact | 0.000 ± 0.000 | 0.438 ± 0.035 | 78.0 ± 2.3 | 0.0 ± 0.0 | 37.7 ± 3.9 | 34.2 ± 4.0 | 17.1 ± 1.2 |
| 128 drawings, 4 per character | Vision code alone (baseline) | 0.783 ± 0.025 | 0.807 ± 0.011 | 80.7 ± 1.1 | 96.4 ± 0.8 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |

### Background alphabets, 128 drawings (calibration runs), R1 (CA1 comparator), closer lures

| Arm | LDI | REC | p(old \| lure) | LDI C1 | LDI C2 | LDI C3 | LDI C4 | LDI C5 |
|---|---|---|---|---|---|---|---|---|
| Intact | 0.075 ± 0.020 | 0.812 ± 0.015 | 0.028 ± 0.004 | 0.152 ± 0.022 | 0.161 ± 0.019 | 0.080 ± 0.029 | 0.011 ± 0.027 | -0.031 ± 0.031 |
| No CA3 recurrent connections | 0.123 ± 0.036 | 0.798 ± 0.017 | 0.000 ± 0.000 | 0.247 ± 0.031 | 0.190 ± 0.037 | 0.130 ± 0.037 | 0.071 ± 0.042 | -0.023 ± 0.045 |
| No CA3 (EC to CA1 only) | 0.147 ± 0.017 | 0.813 ± 0.016 | 0.027 ± 0.003 | 0.054 ± 0.024 | 0.181 ± 0.018 | 0.177 ± 0.019 | 0.173 ± 0.017 | 0.149 ± 0.016 |
| No DG | 0.089 ± 0.023 | 0.478 ± 0.030 | 0.000 ± 0.000 | 0.089 ± 0.024 | 0.097 ± 0.025 | 0.104 ± 0.026 | 0.100 ± 0.018 | 0.054 ± 0.031 |
| Perforant path, 75% kept | 0.074 ± 0.016 | 0.812 ± 0.015 | 0.027 ± 0.003 | 0.143 ± 0.015 | 0.166 ± 0.016 | 0.077 ± 0.018 | 0.009 ± 0.026 | -0.027 ± 0.029 |
| Perforant path, 50% kept | 0.075 ± 0.019 | 0.811 ± 0.016 | 0.026 ± 0.003 | 0.145 ± 0.028 | 0.155 ± 0.030 | 0.077 ± 0.020 | 0.018 ± 0.023 | -0.018 ± 0.023 |
| Perforant path, 25% kept | 0.069 ± 0.012 | 0.773 ± 0.018 | 0.020 ± 0.003 | 0.115 ± 0.020 | 0.133 ± 0.017 | 0.072 ± 0.021 | 0.027 ± 0.014 | -0.004 ± 0.017 |
| Vision code alone (baseline) | 0.741 ± 0.016 | 0.812 ± 0.013 | 0.000 ± 0.000 | 0.791 ± 0.018 | 0.777 ± 0.018 | 0.756 ± 0.016 | 0.745 ± 0.015 | 0.638 ± 0.019 |
| No hippocampus | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |

### Load and interference, background alphabets (checks), R1 (CA1 comparator), other-drawer lures

| Condition | Arm | LDI | REC | p(old \| repeat) | p(similar \| lure) | p(old \| lure) | p(old \| foil) | Lures on studied pattern |
|---|---|---|---|---|---|---|---|---|
| 20 drawings | Intact | 0.337 ± 0.019 | 1.000 ± 0.001 | 100.0 ± 0.1 | 39.9 ± 1.6 | 0.0 ± 0.1 | 0.0 ± 0.0 | 59.0 ± 1.3 |
| 20 drawings | No CA3 recurrent connections | 0.356 ± 0.030 | 1.000 ± 0.001 | 100.0 ± 0.1 | 58.4 ± 2.2 | 0.0 ± 0.1 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 20 drawings | No CA3 (EC to CA1 only) | 0.351 ± 0.023 | 1.000 ± 0.001 | 100.0 ± 0.1 | 79.1 ± 1.8 | 0.0 ± 0.1 | 0.0 ± 0.0 |  |
| 20 drawings | Vision code alone (baseline) | 0.286 ± 0.014 | 0.999 ± 0.001 | 99.9 ± 0.1 | 32.6 ± 1.4 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 50 drawings | Intact | 0.266 ± 0.029 | 0.988 ± 0.005 | 98.8 ± 0.5 | 37.5 ± 2.2 | 0.0 ± 0.0 | 0.0 ± 0.0 | 41.3 ± 2.9 |
| 50 drawings | No CA3 recurrent connections | 0.229 ± 0.025 | 0.987 ± 0.005 | 98.7 ± 0.5 | 66.9 ± 1.5 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 50 drawings | No CA3 (EC to CA1 only) | 0.154 ± 0.024 | 0.988 ± 0.005 | 98.8 ± 0.5 | 84.4 ± 1.2 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 50 drawings | Vision code alone (baseline) | 0.263 ± 0.032 | 0.803 ± 0.013 | 80.3 ± 1.3 | 34.3 ± 3.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 100 drawings | Intact | 0.198 ± 0.011 | 0.906 ± 0.009 | 90.6 ± 0.9 | 36.0 ± 1.7 | 0.0 ± 0.0 | 0.0 ± 0.0 | 27.2 ± 1.5 |
| 100 drawings | No CA3 recurrent connections | 0.159 ± 0.030 | 0.894 ± 0.009 | 89.4 ± 0.9 | 63.2 ± 2.6 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 100 drawings | No CA3 (EC to CA1 only) | 0.090 ± 0.030 | 0.906 ± 0.009 | 90.6 ± 0.9 | 86.9 ± 1.7 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 100 drawings | Vision code alone (baseline) | 0.233 ± 0.023 | 0.813 ± 0.011 | 81.3 ± 1.1 | 38.6 ± 3.1 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings | Intact | 0.149 ± 0.028 | 0.812 ± 0.015 | 81.2 ± 1.5 | 32.9 ± 2.3 | 0.0 ± 0.0 | 0.0 ± 0.0 | 20.9 ± 2.0 |
| 128 drawings | No CA3 recurrent connections | 0.109 ± 0.031 | 0.798 ± 0.017 | 79.8 ± 1.7 | 60.1 ± 1.4 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 128 drawings | No CA3 (EC to CA1 only) | 0.069 ± 0.018 | 0.813 ± 0.016 | 81.3 ± 1.6 | 87.6 ± 1.4 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings | Vision code alone (baseline) | 0.215 ± 0.031 | 0.812 ± 0.013 | 81.2 ± 1.3 | 39.5 ± 1.8 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 200 drawings | Intact | 0.089 ± 0.029 | 0.227 ± 0.025 | 22.7 ± 2.5 | 27.4 ± 2.6 | 0.0 ± 0.0 | 0.0 ± 0.0 | 10.9 ± 1.8 |
| 200 drawings | No CA3 recurrent connections | 0.065 ± 0.031 | 0.173 ± 0.022 | 17.3 ± 2.2 | 51.2 ± 1.8 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 200 drawings | No CA3 (EC to CA1 only) | 0.038 ± 0.027 | 0.235 ± 0.026 | 23.5 ± 2.6 | 87.5 ± 1.2 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 200 drawings | Vision code alone (baseline) | 0.214 ± 0.024 | 0.811 ± 0.008 | 81.1 ± 0.8 | 44.3 ± 2.2 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 256 drawings | Intact | 0.059 ± 0.024 | 0.033 ± 0.008 | 3.3 ± 0.8 | 24.4 ± 1.2 | 0.0 ± 0.0 | 0.0 ± 0.0 | 6.9 ± 1.4 |
| 256 drawings | No CA3 recurrent connections | 0.028 ± 0.036 | 0.010 ± 0.004 | 1.0 ± 0.4 | 47.4 ± 2.4 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 256 drawings | No CA3 (EC to CA1 only) | 0.037 ± 0.016 | 0.036 ± 0.009 | 3.6 ± 0.9 | 87.8 ± 0.9 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 256 drawings | Vision code alone (baseline) | 0.182 ± 0.022 | 0.807 ± 0.009 | 80.7 ± 0.9 | 45.9 ± 2.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings, 2 per character | Intact | 0.243 ± 0.027 | 0.766 ± 0.020 | 76.6 ± 2.0 | 42.0 ± 3.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 16.5 ± 1.4 |
| 128 drawings, 2 per character | No CA3 recurrent connections | 0.189 ± 0.021 | 0.746 ± 0.019 | 74.6 ± 1.9 | 65.4 ± 2.4 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 128 drawings, 2 per character | No CA3 (EC to CA1 only) | 0.114 ± 0.022 | 0.769 ± 0.020 | 76.9 ± 2.0 | 89.8 ± 1.4 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings, 2 per character | Vision code alone (baseline) | 0.348 ± 0.031 | 0.804 ± 0.009 | 80.4 ± 0.9 | 51.6 ± 2.3 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings, 4 per character | Intact | 0.378 ± 0.027 | 0.693 ± 0.024 | 69.3 ± 2.4 | 54.6 ± 2.8 | 0.0 ± 0.0 | 0.0 ± 0.0 | 12.1 ± 2.1 |
| 128 drawings, 4 per character | No CA3 recurrent connections | 0.318 ± 0.026 | 0.668 ± 0.026 | 66.8 ± 2.6 | 73.1 ± 2.3 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 128 drawings, 4 per character | No CA3 (EC to CA1 only) | 0.188 ± 0.026 | 0.697 ± 0.024 | 69.7 ± 2.4 | 93.5 ± 0.9 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings, 4 per character | Vision code alone (baseline) | 0.520 ± 0.026 | 0.803 ± 0.008 | 80.3 ± 0.8 | 67.2 ± 2.2 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |

### Background alphabets, 128 drawings (calibration runs), R2 (CA3 self-support), closer lures

| Arm | LDI | REC | p(old \| lure) | LDI C1 | LDI C2 | LDI C3 | LDI C4 | LDI C5 |
|---|---|---|---|---|---|---|---|---|
| Intact | 0.000 ± 0.000 | 0.414 ± 0.022 | 0.402 ± 0.040 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| No CA3 recurrent connections | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| No CA3 (EC to CA1 only) | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| No DG | 0.000 ± 0.000 | 0.000 ± 0.001 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| Perforant path, 75% kept | 0.000 ± 0.000 | 0.428 ± 0.026 | 0.394 ± 0.044 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| Perforant path, 50% kept | 0.000 ± 0.000 | 0.433 ± 0.023 | 0.376 ± 0.038 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| Perforant path, 25% kept | 0.000 ± 0.000 | 0.412 ± 0.036 | 0.354 ± 0.044 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| Vision code alone (baseline) | 0.741 ± 0.016 | 0.812 ± 0.013 | 0.000 ± 0.000 | 0.791 ± 0.018 | 0.777 ± 0.018 | 0.756 ± 0.016 | 0.745 ± 0.015 | 0.638 ± 0.019 |
| No hippocampus | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |

### Load and interference, background alphabets (checks), R2 (CA3 self-support), other-drawer lures

| Condition | Arm | LDI | REC | p(old \| repeat) | p(similar \| lure) | p(old \| lure) | p(old \| foil) | Lures on studied pattern |
|---|---|---|---|---|---|---|---|---|
| 20 drawings | Intact | 0.000 ± 0.000 | 0.000 ± 0.001 | 100.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.1 | 59.0 ± 1.3 |
| 20 drawings | No CA3 recurrent connections | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 20 drawings | No CA3 (EC to CA1 only) | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 20 drawings | Vision code alone (baseline) | 0.286 ± 0.014 | 0.999 ± 0.001 | 99.9 ± 0.1 | 32.6 ± 1.4 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 50 drawings | Intact | 0.000 ± 0.000 | 0.000 ± 0.000 | 100.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 41.3 ± 2.9 |
| 50 drawings | No CA3 recurrent connections | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 50 drawings | No CA3 (EC to CA1 only) | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 50 drawings | Vision code alone (baseline) | 0.263 ± 0.032 | 0.803 ± 0.013 | 80.3 ± 1.3 | 34.3 ± 3.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 100 drawings | Intact | 0.000 ± 0.000 | 0.000 ± 0.000 | 100.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 27.2 ± 1.5 |
| 100 drawings | No CA3 recurrent connections | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 100 drawings | No CA3 (EC to CA1 only) | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 100 drawings | Vision code alone (baseline) | 0.233 ± 0.023 | 0.813 ± 0.011 | 81.3 ± 1.1 | 38.6 ± 3.1 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings | Intact | 0.000 ± 0.000 | 0.414 ± 0.022 | 81.2 ± 1.7 | 0.0 ± 0.0 | 45.5 ± 3.7 | 39.8 ± 3.2 | 20.9 ± 2.0 |
| 128 drawings | No CA3 recurrent connections | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 128 drawings | No CA3 (EC to CA1 only) | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings | Vision code alone (baseline) | 0.215 ± 0.031 | 0.812 ± 0.013 | 81.2 ± 1.3 | 39.5 ± 1.8 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 200 drawings | Intact | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 10.9 ± 1.8 |
| 200 drawings | No CA3 recurrent connections | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 200 drawings | No CA3 (EC to CA1 only) | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 200 drawings | Vision code alone (baseline) | 0.214 ± 0.024 | 0.811 ± 0.008 | 81.1 ± 0.8 | 44.3 ± 2.2 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 256 drawings | Intact | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 6.9 ± 1.4 |
| 256 drawings | No CA3 recurrent connections | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 256 drawings | No CA3 (EC to CA1 only) | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 256 drawings | Vision code alone (baseline) | 0.182 ± 0.022 | 0.807 ± 0.009 | 80.7 ± 0.9 | 45.9 ± 2.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings, 2 per character | Intact | 0.000 ± 0.000 | 0.421 ± 0.054 | 82.8 ± 1.2 | 0.0 ± 0.0 | 49.0 ± 3.8 | 40.7 ± 5.4 | 16.5 ± 1.4 |
| 128 drawings, 2 per character | No CA3 recurrent connections | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 128 drawings, 2 per character | No CA3 (EC to CA1 only) | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings, 2 per character | Vision code alone (baseline) | 0.348 ± 0.031 | 0.804 ± 0.009 | 80.4 ± 0.9 | 51.6 ± 2.3 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings, 4 per character | Intact | 0.000 ± 0.000 | 0.437 ± 0.055 | 82.8 ± 2.6 | 0.0 ± 0.0 | 52.6 ± 4.1 | 39.1 ± 6.7 | 12.1 ± 2.1 |
| 128 drawings, 4 per character | No CA3 recurrent connections | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| 128 drawings, 4 per character | No CA3 (EC to CA1 only) | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |
| 128 drawings, 4 per character | Vision code alone (baseline) | 0.520 ± 0.026 | 0.803 ± 0.008 | 80.3 ± 0.8 | 67.2 ± 2.2 | 0.0 ± 0.0 | 0.0 ± 0.0 |  |

Run time and peak memory per file: e8b_background_n20_d1: 3711 s, peak 3.26 GB; e8b_background_n50_d1: 2242 s, peak 2.76 GB; e8b_background_n100_d1: 1610 s, peak 2.89 GB; e8b_background_n128_d1: 2577 s, peak 3.56 GB; e8b_background_n128_d2: 1489 s, peak 3.10 GB; e8b_background_n128_d4: 1267 s, peak 3.10 GB; e8b_background_n200_d1: 1271 s, peak 3.42 GB; e8b_background_n256_d1: 1264 s, peak 3.98 GB; e8b_evaluation_n20_d1: 4707 s, peak 3.45 GB; e8b_evaluation_n50_d1: 2451 s, peak 2.75 GB; e8b_evaluation_n100_d1: 1345 s, peak 2.76 GB; e8b_evaluation_n128_d1: 3128 s, peak 3.51 GB; e8b_evaluation_n128_d2: 1518 s, peak 3.02 GB; e8b_evaluation_n128_d4: 1597 s, peak 3.02 GB; e8b_evaluation_n200_d1: 1038 s, peak 3.39 GB; e8b_evaluation_n256_d1: 1145 s, peak 3.74 GB.
