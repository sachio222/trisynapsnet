# E8c results

Young adults who study a series of pictures once and later see a similar new one call it old 40.3% of the time on the Mnemonic Similarity Task (Stark and colleagues 2013, Table 2), and the more similar the lure, the more often they do (Stark, Kirwan and Stark 2019). In E8b the fully local hippocampus, at human proportions and with lures as close as the human task's, did not answer like people under either readout: attractor dynamics carried every test cue, foils included, onto some stored pattern, so the final state no longer told the item types apart. One logged quantity did: the support that CA3's starting state, before any attractor step, gets from its own recurrent synapses. Models of familiarity read a signal of this kind, the energy of the presented pattern in a recurrent network, before any retrieval step (Bogacz, Brown and Giraud-Carrier 2001; Cortes and colleagues 2010). E8c asks whether a familiarity signal read from CA3's starting state makes people's recognition errors. It changes the readout and nothing in the circuit. The protocol, with every setting and its reason, is `docs/e8c_protocol.md`, committed before any run; the sources, with quotes and locations, are in `docs/e8c_sources.md`. Every number below comes from `results/e8c_*.json` through `scripts/make_e8c_table.py`; medians and CA3 state come from `results/e8c_scores.json`, which the same script writes.

**Setup.** The model is E8b's, unchanged: DG, CA3 and CA1 at human proportions scaled down 500 times (30,000, 3,400 and 32,000 cells, 2% active), a one-shot perforant path with clipped binary synapses, CA3 with clipped binary recurrent synapses, and a one-shot CA1. When a test drawing arrives, its EC code drives CA3 through the perforant path, and the 68 most driven CA3 cells fire. That is CA3's starting state, before any recurrent step. Attractor dynamics then run from it: in each round the 68 cells with the most recurrent input from the cells now active fire next, until the state stops changing. Reaching a stored pattern from a partial or distorted cue this way is pattern completion.

- **R3, the new readout,** is the share of the starting state's cell pairs whose recurrent synapse is potentiated: the mean recurrent input each active cell receives from the other active cells, as a share of the most it could receive. It equals the starting state's energy with the sign reversed, divided by a constant. It is computed from the synapses and the cells now firing, before any attractor step, never consults a list of stored patterns, and has no free setting. Old when R3 is high, similar when it is middling, new when it is low.
- **R3 is a stand-in.** The familiarity models that support this calculation place it in perirhinal cortex, not the hippocampus, and the sources read place the hippocampus's own novelty signal in CA1, after recall (`docs/e8c_sources.md`). The model has no perirhinal cortex, and CA3 is its only recurrent network, so R3 applies that calculation to CA3's recurrent synapses. No source read identifies a population that reads CA3's first recurrent pass.
- **R3s**, reported beside it, is E8b's self-support formula applied to the starting state: within-state recurrent input divided by all potentiated recurrent input onto the active cells. E8b logged it as cue self-support, and it is the quantity that suggested E8c. E8b's two readouts are kept: the CA1 comparator (**R1**, the cosine between the test drawing's EC code and the code CA1 returns) and self-support of CA3's final state (**R2**).
- **Test set.** The starting-state idea came from E8b's evaluation results, so E8c is scored on drawings that did not suggest it. E8b's 128-drawing evaluation lists used 10,476 of the 13,180 evaluation drawings; the other 2,704 form the held-out pool, and 619 characters have two held-out drawings, one to study and one to distort into a lure. Seeds 100 to 109 give new lists, wiring and distortions. The pool's limits: its drawings come from the same 20 alphabets and the same 20 drawers as E8b's, and every one of them appeared in some other E8b evaluation condition (loads 20 to 256, two or four drawings per character), where the starting state's support was logged but never summarised. It is a different sample of the same population.
- **Lists.** The model studies 128 drawings of different characters once and is tested on 64 repeats, 64 foils and two lure sets: another person's drawing of a studied character (other-drawer lures, bins L1 to L5) and the studied drawing itself distorted at five levels (closer lures, C1 most similar to C5 least).
- **Calibration.** Each readout has two thresholds, set on background alphabets at 128 drawings so that the intact model calls 81.2% of repeats old and 82.0% of foils new, young adults' rates. Every lesion uses the intact model's thresholds; the vision-code baseline keeps its own. For the ageing test, the intact model and the three thinned perforant paths each also get thresholds set to adults 60 to 74's rates, 82.2% of repeats old and 73.4% of foils new (same table). Nothing is fitted to p(old | lure), LDI, the similarity curve or any lesion effect.
- **Reproduction check.** The background lists and wiring are rebuilt exactly as E8b's, so R1 and R2 there must equal E8b's background signals. They do: the largest absolute difference is 0.0 for R1 and 0.0 for R2.

**Main result.** R3 leaves room for a similar answer where R2 did not: its old threshold (0.8003) sits above its new threshold (0.2946) at young adults' rates. On closer lures the intact model under R3 recognises studied drawings nearly as well as young adults (REC 0.760 against 0.786) and tells closer lures from foils somewhat better (LDI 0.415 against 0.360), but it calls no lure old (p(old | lure) 0.000 against 0.403). It calls 56.0% of closer lures similar and 44.0% new, where people answer 47.6% similar and 8.3% new. LDI falls as closer lures grow less similar, from 0.498 at C1 to 0.352 at C5: R3 answers similar more often to closer lures, but it calls no lure old at any level, so the error people make, false old answers that rise with similarity, is absent. On other-drawer lures LDI is 0.045 and R3 calls 81.0% of lures new. Without DG, R3 calls almost every lure old (0.999 of closer lures, 0.844 of other-drawer lures) and more foils old than repeats (REC −0.198). People's 40.3% lies between the intact model (0%) and the model without DG (near 100%); that is an observation from the two arms, not a fitted claim. Of the scored predictions, 2a failed, 6 held for two of three thinned paths, and the rest held, several of them because the protocol predicted that R3 would miss people in exactly these ways.

## Terms

- **LDI**, the lure discrimination index: p(similar | lure) − p(similar | foil). **REC**, the recognition score: p(old | repeat) − p(old | foil). Young adults score LDI 0.360 and REC 0.786 and call 40.3% of lures old; adults 60 to 74 call 54.6% old (Stark and colleagues 2013, Table 2).
- **Starting state**: the 68 CA3 cells the perforant path's drive picks for a test drawing, before any recurrent step.
- **Attractor dynamics and pattern completion**: from the starting state, CA3 runs in rounds; in each round the 68 cells with the most recurrent input from the cells now active fire next, until the state stops changing. A state that holds itself this way is an attractor, and each stored pattern is one. Reaching the studied drawing's pattern from a partial or distorted cue is pattern completion.
- **R1**, the CA1 comparator; **R2**, self-support of CA3's final state; **R3**, recurrent support of the starting state; **R3s**, self-support of the starting state. Each turns its signal into old, similar or new with two thresholds, θ_old ≥ θ_new: above θ_old old, below θ_new new, between them similar. When the targets put θ_new above θ_old, the thresholds cross, and the readout never answers similar.
- **Fixed thresholds**: every arm uses the intact model's young-adult thresholds; each arm's own thresholds are a secondary score. **Older adults' criteria**: thresholds set to adults 60 to 74's two rates, for the intact model and the thinned perforant paths only.
- **Vision-code baseline**: decides from the largest cosine between the test drawing's vision code and any studied drawing's, with no hippocampus. It has no CA3, so R2, R3 and R3s do not apply to it; its rows repeat unchanged under every readout in the tables.

The main condition is the held-out evaluation lists at 128 drawings, closer lures, R3, intact model, fixed young-adult thresholds. Values are means over seeds 100 to 109; each seed runs 8 lists, about 1,000 studied drawings.

## Predictions

Written before any run and given here in short; the exact wording, and how each is scored, are in `docs/e8c_protocol.md`. Every row of the scored table is listed, held or not.

| Prediction | Outcome |
|---|---|
| 1. R3's thresholds leave room for similar at both young-adult rates. | **Held.** θ_old 0.8003, θ_new 0.2946 on background lists. R2's thresholds cross again (0.2662 below 0.2761), as in E8b. |
| 2a. p(old \| lure) rises with lure similarity (closer lures, scored). | **Failed.** p(old \| lure) is 0.000 at every level, C1 to C5. |
| 2b. LDI does not rise toward less similar lures, unlike people's (closer lures, scored). | **Held.** LDI falls from 0.498 at C1 through 0.455, 0.397 and 0.374 to 0.352 at C5, the reverse of people's curve. |
| 2a on other-drawer lures (reported beside it). | **Not met.** p(old \| lure) is 0.000 in every bin, L1 to L5. |
| 2b on other-drawer lures (reported beside it). | **Not met.** LDI 0.032, 0.030, 0.066, 0.058 and 0.034 from L1 to L5. By the protocol's test this rises toward less similar lures, the human direction, because L5 is 0.002 above L1 and no step falls by more than 0.05; the five bins lie within 0.036 of one another, less than one standard deviation over seeds in each bin (0.038 to 0.057). |
| 3. p(old \| lure) falls more than 0.15 below young adults' 0.403. | **Held.** 0.000. |
| 3b. p(new \| lure) is above 0.30. | **Held.** 0.440, against young adults' 0.083. |
| 4. REC is within 0.10 of young adults' 0.786. | **Held.** 0.760. |
| 5a. Without CA3's recurrent connections every item is new. | **Held, by construction**, since R3 reads recurrent synapses: p(old \| lure) 0.000, REC 0.000. |
| 5b. Without DG, p(old \| lure) is above the intact model's and LDI below it. | **Held.** p(old \| lure) 0.999 against 0.000; LDI −0.145 against 0.415. REC is −0.198. |
| 5c. Thinning lowers p(old \| lure) and REC at each step: 75% kept against intact. | **Held.** REC 0.595 against 0.760. p(old \| lure) is 0.000 in both, so that half holds only because neither arm calls a lure old. |
| 5c: 50% kept against 75%. | **Held.** REC 0.289 against 0.595; p(old \| lure) 0.000 in both. |
| 5c: 25% kept against 50%. | **Held.** REC 0.007 against 0.289; p(old \| lure) 0.000 in both. |
| 6. Under older adults' criteria, each thinned path calls more lures old than the intact model under the same criteria: 75% kept. | **Failed.** 0.000 against 0.000 (adults 60 to 74: 0.546); 0.000 at every level. |
| 6: 50% kept. | **Held.** 0.016 against 0.000; by level 0.041, 0.022, 0.010, 0.005 and 0.004 from C1 to C5, far below adults 60 to 74's 0.546. |
| 6: 25% kept. | **Held.** 0.993 against 0.000; by level 0.993, 0.993, 0.993, 0.992 and 0.994, with no similarity gradient. This arm's older-adult thresholds cross (θ_old 0.1427, θ_new 0.1804), so it never answers similar, and it calls 62.0% of foils old, where adults 60 to 74 call 4.8%. |
| 7. R1 and R2 on the held-out pool repeat E8b's evaluation values within 0.05. | **Held.** R1: REC 0.728 (E8b 0.724), closer-lure LDI −0.007 (0.006), closer-lure p(old \| lure) 0.023 (0.024). R2: closer-lure p(old \| lure) 0.384 (0.396), REC 0.449 (0.432). |

R3s has no prediction of its own; its numbers are below.

**Where thresholds cross.** At young adults' rates, R3's thresholds cross only for the model without DG (θ_old 0.7300, θ_new 0.9008) and the perforant path at 25% kept (0.1449, 0.1892), both secondary scores; R3s's cross only at 25% kept. R2's cross for the intact model and for every lesion arm calibrated on its own, as in E8b, and R1's for the model without DG.

## What the numbers show

- **The starting-state signal holds on drawings that did not suggest it.** The starting state's self-support (R3s's signal) has median 0.234 for repeats, 0.052 for closer lures and 0.049 for foils, against E8b's 0.233, 0.052 and 0.049. R3's medians are 0.959 for repeats, 0.298 for closer lures, 0.270 for other-drawer lures and 0.267 for foils.
- **R3 calls no lure old because lures start far below the old threshold.** The median closer lure's R3 (0.298) is closer to the median foil's (0.267) than to θ_old (0.8003), so lures fall between the thresholds or below θ_new: 56.0% similar and 44.0% new. Attractor dynamics, which run after R3 is read, still end every cue on some stored pattern (logged only); 17.5% of closer lures end on their studied pattern, from 32.9% at C1 to 7.3% at C5, against E8b's 18.0%.
- **R3 treats other-drawer lures almost as foils.** Their median R3 is 0.270 against 0.267 for foils; it calls 19.0% of them similar and 81.0% new, against 14.5% similar and 85.5% new for foils. LDI is 0.045, against R1's 0.127 on the same lures.
- **Without DG, every starting state looks familiar.** CA3 then stores the perforant path's own patterns, which overlap, and the median R3 is 0.848 for repeats, 0.927 for closer lures and 0.883 for foils. With the intact model's thresholds R3 calls 65.6% of repeats, 99.9% of closer lures, 84.4% of other-drawer lures and 85.3% of foils old. With its own thresholds the model's thresholds cross, and it calls every closer lure old (1.000, REC −0.107).
- **Thinning the perforant path lowers recognition and never raises false old answers under young adults' criteria.** REC falls to 0.595, 0.289 and 0.007 with 75%, 50% and 25% of connections kept, as repeats' median R3 falls to 0.866, 0.586 and 0.196; at 25% kept, 74.0% of repeats are called new. No arm calls a lure old, and closer-lure LDI falls to 0.265, 0.065 and 0.001. With each arm's own thresholds, the 75% and 50% arms keep REC near intact (0.760 and 0.762) with closer-lure LDI 0.458 and 0.522; the 25% arm's thresholds cross, and it calls 99.2% of closer lures old.
- **Under older adults' criteria, thinning goes from no lures old to nearly all.** The intact model and the 75% arm still call no lure old. The 50% arm calls 1.6% old, most at C1 (4.1%). The 25% arm calls 99.3% of closer lures old at every level and 62.0% of foils old. Adults 60 to 74 call 54.6% of lures and 4.8% of foils old, so neither the 50% nor the 25% arm shows the older-adult pattern. In people the age gap is smallest for the most similar lures (Yassa, Lacy and colleagues 2011); in the 50% arm the gain over the intact model is largest for the most similar lures.
- **R3s follows R3, more weakly.** On closer lures: LDI 0.233, REC 0.762, p(old \| lure) 0.000, 40.4% of lures similar and 59.6% new; LDI falls from 0.335 at C1 to 0.162 at C5. On other-drawer lures LDI is 0.058. Without DG, nearly every R3s value lies between the intact model's thresholds (medians 0.103, 0.081 and 0.082 for repeats, closer lures and foils, against θ_old 0.2048 and θ_new 0.0520), so it calls nearly every item similar (99.2% of repeats, every lure and foil; REC 0.008). Under older adults' criteria its 25% arm calls 97.6% of closer lures and 44.9% of foils old.
- **The vision code alone also never calls a lure old.** R3 does not apply to it: it decides from vision-code cosines with its own thresholds, the same under every readout. Its old threshold is a cosine of 1.0000, an exact repeat, so no lure can reach it. It calls 93.6% of closer lures similar (LDI 0.749, from 0.786 at C1 to 0.661 at C5) and scores LDI 0.193 on other-drawer lures, REC 0.811. On closer lures it discriminates better than the intact model under R3 (0.415) and better than people (0.360).
- **R1 and R2 repeat E8b on the new drawings.** R1: REC 0.728, closer-lure LDI −0.007, 2.3% of closer lures old, other-drawer LDI 0.127. R2: thresholds crossed, so it never answers similar; it calls 38.4% of closer lures and 34.9% of foils old, REC 0.449.

## What it means

Read before attractor dynamics run, the recurrent support of CA3's starting state separates repeats from lures and foils on drawings that did not suggest the idea, so R3 recognises studied drawings nearly as well as young adults (REC 0.760 against 0.786) and, unlike the final-state readout, answers similar. It does not make people's error. After DG's pattern separation, a lure's starting state holds too few potentiated pairs to reach the old threshold, so R3 calls no lure old at any similarity level, where young adults call 40.3% old, and it calls more than five times as many lures new as people do (44.0% against 8.3%). Its closer-lure LDI of 0.415 is near people's 0.360, but it falls as lures grow less similar, the reverse of people's curve, and on other-drawer lures R3 treats lures almost as foils (LDI 0.045), much as CA3 and DG activity treats lures in human imaging (Bakker and colleagues 2008). Removing DG reverses the error: the stored patterns overlap, every starting state looks familiar, and R3 calls 99.9% of closer lures old and more foils old than repeats. People's 40.3% lies between these two arms, an observation from the arms and not a fitted result. Thinning the perforant path, the stand-in for entorhinal input loss with age, lowers recognition rather than raising false old answers under young adults' criteria; under older adults' criteria it moves from no lures old to nearly all, with no similarity gradient and 62.0% of foils old, which is not the older-adult pattern either. Two limits bound all of this. R3 is a stand-in: the literature supports the calculation but places it in perirhinal cortex, which the model does not have. And the held-out drawings share their alphabets and drawers with E8b's, so the test is a new sample of the same population, not a new population.

## Run record

The protocol was committed before any run. A one-list background run checked that the code ran (44 seconds, written under `results/logs/`, never scored). The background run (seeds 0 to 9) took about 46 minutes and gave the thresholds and the reproduction check; the evaluation run (seeds 100 to 109) took about 46 minutes, one after the other, each under 3.7 GB resident, and was scored once. Neither run was restarted.

## Tables

Built by `scripts/make_e8c_table.py` from `results/e8c_*.json`, with the thresholds in `results/e8c_calibration.json`. Evaluation lists use only evaluation drawings that E8b's 128-drawing evaluation lists never used, seeds 100 to 109. Means over seeds ± one standard deviation; rates in percent.

R1 and R2 on the background lists against E8b's: largest absolute difference r1 0.0, r2 0.0.

### Calibration on background alphabets, 128 drawings

| Readout | Arm | Criteria | θ_old | θ_new | Room for similar |
|---|---|---|---|---|---|
| R1 (CA1 comparator) | Intact | young adults | 0.9449 (tie share 0.440) | 0.5735 (tie share 0.700) | yes |
| R1 (CA1 comparator) | No CA3 recurrent connections | young adults | 0.9432 (tie share 0.440) | 0.6446 (tie share 0.400) | yes |
| R1 (CA1 comparator) | No CA3 (EC to CA1 only) | young adults | 0.9450 (tie share 0.440) | 0.7198 (tie share 0.400) | yes |
| R1 (CA1 comparator) | Vision code alone (baseline) | young adults | 1.0000 (tie share 0.529) | 0.6253 (tie share 0.400) | yes |
| R1 (CA1 comparator) | No DG | young adults | 0.6021 (tie share 0.440) | 0.6093 (tie share 0.400) | no |
| R1 (CA1 comparator) | Perforant path, 75% kept | young adults | 0.9449 (tie share 0.440) | 0.5686 (tie share 0.400) | yes |
| R1 (CA1 comparator) | Perforant path, 50% kept | young adults | 0.9448 (tie share 0.440) | 0.5610 (tie share 0.400) | yes |
| R1 (CA1 comparator) | Perforant path, 25% kept | young adults | 0.9385 (tie share 0.440) | 0.5395 (tie share 0.400) | yes |
| R1 (CA1 comparator) | Intact | adults 60 to 74 | 0.9438 (tie share 0.640) | 0.5420 (tie share 0.080) | yes |
| R1 (CA1 comparator) | Perforant path, 75% kept | adults 60 to 74 | 0.9437 (tie share 0.640) | 0.5373 (tie share 0.080) | yes |
| R1 (CA1 comparator) | Perforant path, 50% kept | adults 60 to 74 | 0.9437 (tie share 0.640) | 0.5283 (tie share 0.080) | yes |
| R1 (CA1 comparator) | Perforant path, 25% kept | adults 60 to 74 | 0.9359 (tie share 0.640) | 0.5061 (tie share 0.080) | yes |
| R2 (self-support of the settled state) | Intact | young adults | 0.2662 (tie share 0.220) | 0.2761 (tie share 0.467) | no |
| R2 (self-support of the settled state) | Vision code alone (baseline) | young adults | 1.0000 (tie share 0.529) | 0.6253 (tie share 0.400) | yes |
| R2 (self-support of the settled state) | No DG | young adults | 0.0811 (tie share 0.440) | 0.0820 (tie share 0.400) | no |
| R2 (self-support of the settled state) | Perforant path, 75% kept | young adults | 0.2661 (tie share 0.813) | 0.2752 (tie share 0.133) | no |
| R2 (self-support of the settled state) | Perforant path, 50% kept | young adults | 0.2658 (tie share 0.480) | 0.2749 (tie share 0.133) | no |
| R2 (self-support of the settled state) | Perforant path, 25% kept | young adults | 0.2634 (tie share 0.720) | 0.2739 (tie share 0.700) | no |
| R2 (self-support of the settled state) | Intact | adults 60 to 74 | 0.2657 (tie share 0.640) | 0.2716 (tie share 0.513) | no |
| R2 (self-support of the settled state) | Perforant path, 75% kept | adults 60 to 74 | 0.2655 (tie share 0.320) | 0.2710 (tie share 0.770) | no |
| R2 (self-support of the settled state) | Perforant path, 50% kept | adults 60 to 74 | 0.2651 (tie share 0.640) | 0.2707 (tie share 0.080) | no |
| R2 (self-support of the settled state) | Perforant path, 25% kept | adults 60 to 74 | 0.2628 (tie share 0.820) | 0.2696 (tie share 0.027) | no |
| R3 (recurrent support of the starting state) | Intact | young adults | 0.8003 (tie share 0.220) | 0.2946 (tie share 0.836) | yes |
| R3 (recurrent support of the starting state) | Vision code alone (baseline) | young adults | 1.0000 (tie share 0.529) | 0.6253 (tie share 0.400) | yes |
| R3 (recurrent support of the starting state) | No DG | young adults | 0.7300 (tie share 0.440) | 0.9008 (tie share 0.318) | no |
| R3 (recurrent support of the starting state) | Perforant path, 75% kept | young adults | 0.6023 (tie share 0.220) | 0.2766 (tie share 0.736) | yes |
| R3 (recurrent support of the starting state) | Perforant path, 50% kept | young adults | 0.3262 (tie share 0.440) | 0.2480 (tie share 0.756) | yes |
| R3 (recurrent support of the starting state) | Perforant path, 25% kept | young adults | 0.1449 (tie share 0.870) | 0.1892 (tie share 0.470) | no |
| R3 (recurrent support of the starting state) | Intact | adults 60 to 74 | 0.7858 (tie share 0.728) | 0.2871 (tie share 0.973) | yes |
| R3 (recurrent support of the starting state) | Perforant path, 75% kept | adults 60 to 74 | 0.5860 (tie share 0.213) | 0.2691 (tie share 0.474) | yes |
| R3 (recurrent support of the starting state) | Perforant path, 50% kept | adults 60 to 74 | 0.3143 (tie share 0.213) | 0.2406 (tie share 0.692) | yes |
| R3 (recurrent support of the starting state) | Perforant path, 25% kept | adults 60 to 74 | 0.1427 (tie share 0.264) | 0.1804 (tie share 0.623) | no |
| R3s (self-support of the starting state) | Intact | young adults | 0.2048 (tie share 0.220) | 0.0520 (tie share 0.400) | yes |
| R3s (self-support of the starting state) | Vision code alone (baseline) | young adults | 1.0000 (tie share 0.529) | 0.6253 (tie share 0.400) | yes |
| R3s (self-support of the starting state) | No DG | young adults | 0.0877 (tie share 0.720) | 0.0817 (tie share 0.400) | yes |
| R3s (self-support of the starting state) | Perforant path, 75% kept | young adults | 0.1466 (tie share 0.440) | 0.0501 (tie share 0.700) | yes |
| R3s (self-support of the starting state) | Perforant path, 50% kept | young adults | 0.0769 (tie share 0.440) | 0.0469 (tie share 0.400) | yes |
| R3s (self-support of the starting state) | Perforant path, 25% kept | young adults | 0.0364 (tie share 0.440) | 0.0402 (tie share 0.400) | no |
| R3s (self-support of the starting state) | Intact | adults 60 to 74 | 0.2017 (tie share 0.640) | 0.0510 (tie share 0.540) | yes |
| R3s (self-support of the starting state) | Perforant path, 75% kept | adults 60 to 74 | 0.1417 (tie share 0.640) | 0.0491 (tie share 0.040) | yes |
| R3s (self-support of the starting state) | Perforant path, 50% kept | adults 60 to 74 | 0.0734 (tie share 0.640) | 0.0459 (tie share 0.040) | yes |
| R3s (self-support of the starting state) | Perforant path, 25% kept | adults 60 to 74 | 0.0360 (tie share 0.640) | 0.0391 (tie share 0.080) | no |

### Predictions, scored as the protocol fixes

| Prediction | Held | Numbers |
|---|---|---|
| 1 | yes | R3 thresholds on background lists: θ_old 0.8003, θ_new 0.2946 (room for similar) |
| 2a (closer lures, scored) | no | p(old \| lure) by level, most to least similar: 0.000, 0.000, 0.000, 0.000, 0.000 (does not fall) |
| 2b (closer lures, scored) | yes | LDI by level, most to least similar: 0.498, 0.455, 0.397, 0.374, 0.352 (does not rise toward less similar lures) |
| 2a (other-drawer lures, reported) | no | p(old \| lure) by level, most to least similar: 0.000, 0.000, 0.000, 0.000, 0.000 (does not fall) |
| 2b (other-drawer lures, reported) | no | LDI by level, most to least similar: 0.032, 0.030, 0.066, 0.058, 0.034 (rises toward less similar lures, the human direction) |
| 3 | yes | p(old \| lure) 0.000 against young adults' 0.403 |
| 3b | yes | p(new \| lure) 0.440 against young adults' 0.083 |
| 4 | yes | REC 0.760 against young adults' 0.786 |
| 5a | yes | without recurrent connections: p(old \| lure) 0.000, REC 0.000 (no R3 signal by construction) |
| 5b | yes | without DG: p(old \| lure) 0.999 against intact 0.000; LDI -0.145 against 0.415 |
| 5c (75% kept) | yes | p(old \| lure) 0.000, REC 0.595; next stronger path 0.000, 0.760 |
| 5c (50% kept) | yes | p(old \| lure) 0.000, REC 0.289; next stronger path 0.000, 0.595 |
| 5c (25% kept) | yes | p(old \| lure) 0.000, REC 0.007; next stronger path 0.000, 0.289 |
| 6 (75% kept) | no | older adults' criteria: p(old \| lure) 0.000 against intact 0.000 with the same criteria; adults 60 to 74: 0.546; by level 0.000, 0.000, 0.000, 0.000, 0.000 |
| 6 (50% kept) | yes | older adults' criteria: p(old \| lure) 0.016 against intact 0.000 with the same criteria; adults 60 to 74: 0.546; by level 0.041, 0.022, 0.010, 0.005, 0.004 |
| 6 (25% kept) | yes | older adults' criteria: p(old \| lure) 0.993 against intact 0.000 with the same criteria; adults 60 to 74: 0.546; by level 0.993, 0.993, 0.993, 0.992, 0.994 |
| 7 | yes | r1 drawer rec: 0.728 against E8b's 0.724; r1 close ldi: -0.007 against E8b's 0.006; r1 close rates lure old: 0.023 against E8b's 0.024; r2 close rates lure old: 0.384 against E8b's 0.396; r2 drawer rec: 0.449 against E8b's 0.432 |

### R1 (CA1 comparator), other-drawer lures, bins L1 to L5, fixed thresholds

| Arm | LDI | REC | p(old \| lure) | LDI L1 | LDI L2 | LDI L3 | LDI L4 | LDI L5 |
|---|---|---|---|---|---|---|---|---|
| Young adults (Stark and colleagues 2013) | 0.360 | 0.786 | 0.403 | not in text | not in text | not in text | not in text | not in text |
| Intact | 0.127 ± 0.023 | 0.728 ± 0.020 | 0.000 ± 0.000 | 0.286 ± 0.061 | 0.226 ± 0.051 | 0.172 ± 0.030 | 0.029 ± 0.054 | -0.066 ± 0.034 |
| No CA3 recurrent connections | 0.085 ± 0.034 | 0.701 ± 0.021 | 0.000 ± 0.000 | 0.188 ± 0.040 | 0.179 ± 0.041 | 0.143 ± 0.059 | 0.040 ± 0.071 | -0.118 ± 0.036 |
| No CA3 (EC to CA1 only) | 0.053 ± 0.026 | 0.730 ± 0.020 | 0.000 ± 0.000 | 0.144 ± 0.018 | 0.120 ± 0.031 | 0.100 ± 0.033 | 0.023 ± 0.044 | -0.118 ± 0.031 |
| No DG | 0.025 ± 0.022 | 0.327 ± 0.022 | 0.000 ± 0.000 | 0.153 ± 0.042 | 0.085 ± 0.034 | 0.045 ± 0.059 | -0.010 ± 0.051 | -0.132 ± 0.042 |
| Perforant path, 75% kept | 0.114 ± 0.022 | 0.728 ± 0.019 | 0.000 ± 0.000 | 0.285 ± 0.048 | 0.195 ± 0.058 | 0.145 ± 0.043 | 0.039 ± 0.048 | -0.077 ± 0.045 |
| Perforant path, 50% kept | 0.106 ± 0.024 | 0.726 ± 0.018 | 0.000 ± 0.000 | 0.245 ± 0.061 | 0.189 ± 0.074 | 0.142 ± 0.030 | 0.034 ± 0.046 | -0.068 ± 0.042 |
| Perforant path, 25% kept | 0.066 ± 0.016 | 0.681 ± 0.024 | 0.000 ± 0.000 | 0.140 ± 0.050 | 0.134 ± 0.054 | 0.080 ± 0.032 | 0.028 ± 0.035 | -0.047 ± 0.028 |
| Vision code alone (baseline) | 0.193 ± 0.026 | 0.811 ± 0.010 | 0.000 ± 0.000 | 0.814 ± 0.019 | 0.382 ± 0.049 | -0.020 ± 0.032 | -0.043 ± 0.037 | -0.074 ± 0.052 |
| No hippocampus | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |

Response rates:

| Arm | old to repeat | similar to repeat | new to repeat | old to lure | similar to lure | new to lure | old to foil | similar to foil | new to foil |
|---|---|---|---|---|---|---|---|---|---|
| Young adults, 20 to 39 | 81.2 | 11.7 | 4.1 | 40.3 | 47.6 | 8.3 | 2.6 | 11.6 | 82.0 |
| Adults 60 to 74 | 82.2 | 7.6 | 5.3 | 54.6 | 23.6 | 12.3 | 4.8 | 12.3 | 73.4 |
| Intact | 72.8 ± 2.0 | 26.9 ± 1.9 | 0.3 ± 0.3 | 0.0 ± 0.0 | 35.5 ± 1.5 | 64.5 ± 1.5 | 0.0 ± 0.0 | 22.8 ± 2.2 | 77.2 ± 2.2 |
| No CA3 recurrent connections | 70.1 ± 2.1 | 29.5 ± 2.0 | 0.4 ± 0.3 | 0.0 ± 0.0 | 68.1 ± 2.9 | 31.9 ± 2.9 | 0.0 ± 0.0 | 59.5 ± 1.8 | 40.5 ± 1.8 |
| No CA3 (EC to CA1 only) | 73.0 ± 2.0 | 27.0 ± 2.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 89.9 ± 1.7 | 10.1 ± 1.7 | 0.0 ± 0.0 | 84.6 ± 1.8 | 15.4 ± 1.8 |
| No DG | 32.7 ± 2.2 | 52.3 ± 2.4 | 15.0 ± 1.9 | 0.0 ± 0.0 | 43.5 ± 2.0 | 56.5 ± 2.0 | 0.0 ± 0.0 | 41.0 ± 1.4 | 59.0 ± 1.4 |
| Perforant path, 75% kept | 72.8 ± 1.9 | 26.7 ± 1.9 | 0.5 ± 0.2 | 0.0 ± 0.0 | 33.0 ± 1.7 | 67.0 ± 1.7 | 0.0 ± 0.0 | 21.5 ± 1.7 | 78.5 ± 1.7 |
| Perforant path, 50% kept | 72.6 ± 1.8 | 25.6 ± 1.8 | 1.8 ± 0.5 | 0.0 ± 0.0 | 30.2 ± 1.5 | 69.8 ± 1.5 | 0.0 ± 0.0 | 19.6 ± 1.4 | 80.4 ± 1.4 |
| Perforant path, 25% kept | 68.1 ± 2.4 | 21.8 ± 2.2 | 10.1 ± 1.1 | 0.0 ± 0.0 | 21.6 ± 0.8 | 78.4 ± 0.8 | 0.0 ± 0.0 | 15.0 ± 1.3 | 85.0 ± 1.3 |
| Vision code alone (baseline) | 81.1 ± 1.0 | 18.9 ± 1.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 37.9 ± 1.7 | 62.1 ± 1.7 | 0.0 ± 0.0 | 18.6 ± 1.9 | 81.4 ± 1.9 |
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
| Intact | 51.4 ± 5.7 | 45.4 ± 4.9 | 40.0 ± 2.2 | 25.7 ± 5.1 | 16.2 ± 3.2 |
| No CA3 recurrent connections | 78.4 ± 3.7 | 77.5 ± 3.6 | 73.9 ± 5.3 | 63.5 ± 6.9 | 47.7 ± 3.1 |
| No CA3 (EC to CA1 only) | 99.0 ± 1.0 | 96.6 ± 1.8 | 94.6 ± 1.8 | 86.9 ± 3.4 | 72.9 ± 3.8 |
| No DG | 56.2 ± 3.8 | 49.5 ± 3.3 | 45.4 ± 5.1 | 40.0 ± 5.2 | 27.8 ± 4.6 |
| Perforant path, 75% kept | 50.0 ± 4.5 | 41.0 ± 5.5 | 36.0 ± 3.6 | 25.4 ± 5.1 | 13.8 ± 3.6 |
| Perforant path, 50% kept | 44.2 ± 5.6 | 38.5 ± 6.5 | 33.8 ± 2.9 | 23.0 ± 5.0 | 12.8 ± 3.5 |
| Perforant path, 25% kept | 28.9 ± 4.3 | 28.4 ± 5.1 | 23.0 ± 3.2 | 17.7 ± 3.1 | 10.3 ± 2.8 |
| Vision code alone (baseline) | 100.0 ± 0.0 | 56.8 ± 4.2 | 16.6 ± 2.8 | 14.3 ± 3.0 | 11.3 ± 3.6 |
| No hippocampus | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |

### R1 (CA1 comparator), closer lures, levels C1 to C5, fixed thresholds

| Arm | LDI | REC | p(old \| lure) | LDI C1 | LDI C2 | LDI C3 | LDI C4 | LDI C5 |
|---|---|---|---|---|---|---|---|---|
| Young adults (Stark and colleagues 2013) | 0.360 | 0.786 | 0.403 | not in text | not in text | not in text | not in text | not in text |
| Intact | -0.007 ± 0.028 | 0.728 ± 0.020 | 0.023 ± 0.002 | 0.049 ± 0.030 | 0.072 ± 0.031 | 0.000 ± 0.033 | -0.053 ± 0.032 | -0.101 ± 0.030 |
| No CA3 recurrent connections | 0.109 ± 0.030 | 0.701 ± 0.021 | 0.000 ± 0.000 | 0.200 ± 0.034 | 0.167 ± 0.034 | 0.121 ± 0.030 | 0.075 ± 0.029 | -0.016 ± 0.030 |
| No CA3 (EC to CA1 only) | 0.119 ± 0.018 | 0.730 ± 0.020 | 0.027 ± 0.004 | 0.020 ± 0.026 | 0.150 ± 0.018 | 0.151 ± 0.018 | 0.146 ± 0.018 | 0.126 ± 0.019 |
| No DG | 0.105 ± 0.030 | 0.327 ± 0.022 | 0.000 ± 0.000 | 0.101 ± 0.036 | 0.115 ± 0.031 | 0.129 ± 0.030 | 0.117 ± 0.030 | 0.063 ± 0.029 |
| Perforant path, 75% kept | -0.000 ± 0.025 | 0.728 ± 0.019 | 0.022 ± 0.002 | 0.053 ± 0.022 | 0.068 ± 0.028 | 0.004 ± 0.029 | -0.036 ± 0.034 | -0.089 ± 0.022 |
| Perforant path, 50% kept | 0.008 ± 0.020 | 0.726 ± 0.018 | 0.021 ± 0.003 | 0.055 ± 0.022 | 0.076 ± 0.023 | 0.010 ± 0.024 | -0.031 ± 0.028 | -0.070 ± 0.023 |
| Perforant path, 25% kept | 0.037 ± 0.016 | 0.681 ± 0.024 | 0.016 ± 0.002 | 0.070 ± 0.019 | 0.091 ± 0.027 | 0.046 ± 0.023 | 0.002 ± 0.025 | -0.025 ± 0.019 |
| Vision code alone (baseline) | 0.749 ± 0.023 | 0.811 ± 0.010 | 0.000 ± 0.000 | 0.786 ± 0.021 | 0.778 ± 0.020 | 0.764 ± 0.020 | 0.759 ± 0.022 | 0.661 ± 0.031 |
| No hippocampus | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |

Response rates:

| Arm | old to repeat | similar to repeat | new to repeat | old to lure | similar to lure | new to lure | old to foil | similar to foil | new to foil |
|---|---|---|---|---|---|---|---|---|---|
| Young adults, 20 to 39 | 81.2 | 11.7 | 4.1 | 40.3 | 47.6 | 8.3 | 2.6 | 11.6 | 82.0 |
| Adults 60 to 74 | 82.2 | 7.6 | 5.3 | 54.6 | 23.6 | 12.3 | 4.8 | 12.3 | 73.4 |
| Intact | 72.8 ± 2.0 | 26.9 ± 1.9 | 0.3 ± 0.3 | 2.3 ± 0.2 | 22.1 ± 2.2 | 75.6 ± 2.3 | 0.0 ± 0.0 | 22.8 ± 2.2 | 77.2 ± 2.2 |
| No CA3 recurrent connections | 70.1 ± 2.1 | 29.5 ± 2.0 | 0.4 ± 0.3 | 0.0 ± 0.0 | 70.5 ± 2.2 | 29.5 ± 2.2 | 0.0 ± 0.0 | 59.5 ± 1.8 | 40.5 ± 1.8 |
| No CA3 (EC to CA1 only) | 73.0 ± 2.0 | 27.0 ± 2.0 | 0.0 ± 0.0 | 2.7 ± 0.4 | 96.5 ± 0.4 | 0.9 ± 0.2 | 0.0 ± 0.0 | 84.6 ± 1.8 | 15.4 ± 1.8 |
| No DG | 32.7 ± 2.2 | 52.3 ± 2.4 | 15.0 ± 1.9 | 0.0 ± 0.0 | 51.5 ± 2.2 | 48.5 ± 2.2 | 0.0 ± 0.0 | 41.0 ± 1.4 | 59.0 ± 1.4 |
| Perforant path, 75% kept | 72.8 ± 1.9 | 26.7 ± 1.9 | 0.5 ± 0.2 | 2.2 ± 0.2 | 21.5 ± 2.0 | 76.3 ± 2.1 | 0.0 ± 0.0 | 21.5 ± 1.7 | 78.5 ± 1.7 |
| Perforant path, 50% kept | 72.6 ± 1.8 | 25.6 ± 1.8 | 1.8 ± 0.5 | 2.1 ± 0.3 | 20.4 ± 1.9 | 77.5 ± 2.0 | 0.0 ± 0.0 | 19.6 ± 1.4 | 80.4 ± 1.4 |
| Perforant path, 25% kept | 68.1 ± 2.4 | 21.8 ± 2.2 | 10.1 ± 1.1 | 1.6 ± 0.2 | 18.6 ± 1.2 | 79.8 ± 1.2 | 0.0 ± 0.0 | 15.0 ± 1.3 | 85.0 ± 1.3 |
| Vision code alone (baseline) | 81.1 ± 1.0 | 18.9 ± 1.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 93.6 ± 0.7 | 6.4 ± 0.7 | 0.0 ± 0.0 | 18.6 ± 1.9 | 81.4 ± 1.9 |
| No hippocampus | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 |

p(old | lure) by level:

| Arm | C1 | C2 | C3 | C4 | C5 |
|---|---|---|---|---|---|
| Intact | 10.9 ± 1.2 | 0.4 ± 0.3 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No CA3 recurrent connections | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No CA3 (EC to CA1 only) | 13.2 ± 1.9 | 0.1 ± 0.1 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No DG | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 75% kept | 10.7 ± 1.2 | 0.4 ± 0.3 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 50% kept | 10.0 ± 1.4 | 0.4 ± 0.3 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 25% kept | 7.8 ± 0.9 | 0.2 ± 0.2 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Vision code alone (baseline) | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No hippocampus | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |

p(similar | lure) by level:

| Arm | C1 | C2 | C3 | C4 | C5 |
|---|---|---|---|---|---|
| Intact | 27.7 ± 2.6 | 29.9 ± 3.1 | 22.8 ± 2.6 | 17.5 ± 2.5 | 12.7 ± 2.1 |
| No CA3 recurrent connections | 79.5 ± 2.7 | 76.2 ± 2.8 | 71.7 ± 2.5 | 67.0 ± 2.0 | 57.9 ± 2.2 |
| No CA3 (EC to CA1 only) | 86.6 ± 1.9 | 99.6 ± 0.3 | 99.7 ± 0.2 | 99.3 ± 0.3 | 97.2 ± 0.5 |
| No DG | 51.1 ± 3.0 | 52.5 ± 2.3 | 53.8 ± 2.3 | 52.7 ± 2.2 | 47.2 ± 2.1 |
| Perforant path, 75% kept | 26.9 ± 2.1 | 28.3 ± 2.5 | 21.9 ± 2.6 | 17.9 ± 2.7 | 12.6 ± 1.5 |
| Perforant path, 50% kept | 25.1 ± 2.1 | 27.3 ± 2.5 | 20.6 ± 2.4 | 16.6 ± 2.3 | 12.6 ± 2.1 |
| Perforant path, 25% kept | 22.0 ± 2.3 | 24.1 ± 2.1 | 19.5 ± 2.1 | 15.2 ± 1.8 | 12.5 ± 1.5 |
| Vision code alone (baseline) | 97.2 ± 0.7 | 96.4 ± 0.5 | 95.1 ± 0.6 | 94.5 ± 1.1 | 84.7 ± 1.5 |
| No hippocampus | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |

### R2 (self-support of the settled state), other-drawer lures, bins L1 to L5, fixed thresholds

| Arm | LDI | REC | p(old \| lure) | LDI L1 | LDI L2 | LDI L3 | LDI L4 | LDI L5 |
|---|---|---|---|---|---|---|---|---|
| Young adults (Stark and colleagues 2013) | 0.360 | 0.786 | 0.403 | not in text | not in text | not in text | not in text | not in text |
| Intact | 0.000 ± 0.000 | 0.449 ± 0.023 | 0.393 ± 0.028 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| No CA3 recurrent connections | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| No CA3 (EC to CA1 only) | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| No DG | 0.000 ± 0.000 | 0.002 ± 0.002 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| Perforant path, 75% kept | 0.000 ± 0.000 | 0.452 ± 0.036 | 0.382 ± 0.032 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| Perforant path, 50% kept | 0.000 ± 0.000 | 0.458 ± 0.027 | 0.364 ± 0.034 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| Perforant path, 25% kept | 0.000 ± 0.000 | 0.425 ± 0.040 | 0.341 ± 0.040 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| Vision code alone (baseline) | 0.193 ± 0.026 | 0.811 ± 0.010 | 0.000 ± 0.000 | 0.814 ± 0.019 | 0.382 ± 0.049 | -0.020 ± 0.032 | -0.043 ± 0.037 | -0.074 ± 0.052 |
| No hippocampus | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |

Response rates:

| Arm | old to repeat | similar to repeat | new to repeat | old to lure | similar to lure | new to lure | old to foil | similar to foil | new to foil |
|---|---|---|---|---|---|---|---|---|---|
| Young adults, 20 to 39 | 81.2 | 11.7 | 4.1 | 40.3 | 47.6 | 8.3 | 2.6 | 11.6 | 82.0 |
| Adults 60 to 74 | 82.2 | 7.6 | 5.3 | 54.6 | 23.6 | 12.3 | 4.8 | 12.3 | 73.4 |
| Intact | 79.7 ± 3.2 | 0.0 ± 0.0 | 20.3 ± 3.2 | 39.3 ± 2.8 | 0.0 ± 0.0 | 60.7 ± 2.8 | 34.9 ± 4.2 | 0.0 ± 0.0 | 65.1 ± 4.2 |
| No CA3 recurrent connections | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 |
| No CA3 (EC to CA1 only) | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 |
| No DG | 0.2 ± 0.2 | 0.0 ± 0.0 | 99.8 ± 0.2 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 |
| Perforant path, 75% kept | 79.6 ± 3.3 | 0.0 ± 0.0 | 20.4 ± 3.3 | 38.2 ± 3.2 | 0.0 ± 0.0 | 61.8 ± 3.2 | 34.4 ± 4.2 | 0.0 ± 0.0 | 65.6 ± 4.2 |
| Perforant path, 50% kept | 78.9 ± 3.1 | 0.0 ± 0.0 | 21.1 ± 3.1 | 36.4 ± 3.4 | 0.0 ± 0.0 | 63.6 ± 3.4 | 33.1 ± 4.4 | 0.0 ± 0.0 | 66.9 ± 4.4 |
| Perforant path, 25% kept | 73.1 ± 3.6 | 0.0 ± 0.0 | 26.9 ± 3.6 | 34.1 ± 4.0 | 0.0 ± 0.0 | 65.9 ± 4.0 | 30.6 ± 4.0 | 0.0 ± 0.0 | 69.4 ± 4.0 |
| Vision code alone (baseline) | 81.1 ± 1.0 | 18.9 ± 1.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 37.9 ± 1.7 | 62.1 ± 1.7 | 0.0 ± 0.0 | 18.6 ± 1.9 | 81.4 ± 1.9 |
| No hippocampus | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 |

p(old | lure) by level:

| Arm | L1 | L2 | L3 | L4 | L5 |
|---|---|---|---|---|---|
| Intact | 41.6 ± 5.7 | 37.9 ± 4.9 | 40.8 ± 5.7 | 40.1 ± 4.3 | 36.1 ± 4.5 |
| No CA3 recurrent connections | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No CA3 (EC to CA1 only) | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No DG | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 75% kept | 39.3 ± 6.1 | 38.2 ± 5.3 | 39.1 ± 4.9 | 37.6 ± 3.3 | 36.6 ± 4.7 |
| Perforant path, 50% kept | 35.2 ± 5.3 | 35.9 ± 4.6 | 38.0 ± 4.4 | 37.0 ± 7.7 | 35.9 ± 4.6 |
| Perforant path, 25% kept | 33.5 ± 5.9 | 34.6 ± 4.3 | 32.0 ± 5.7 | 36.7 ± 6.7 | 33.8 ± 5.9 |
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
| Vision code alone (baseline) | 100.0 ± 0.0 | 56.8 ± 4.2 | 16.6 ± 2.8 | 14.3 ± 3.0 | 11.3 ± 3.6 |
| No hippocampus | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |

### R2 (self-support of the settled state), closer lures, levels C1 to C5, fixed thresholds

| Arm | LDI | REC | p(old \| lure) | LDI C1 | LDI C2 | LDI C3 | LDI C4 | LDI C5 |
|---|---|---|---|---|---|---|---|---|
| Young adults (Stark and colleagues 2013) | 0.360 | 0.786 | 0.403 | not in text | not in text | not in text | not in text | not in text |
| Intact | 0.000 ± 0.000 | 0.449 ± 0.023 | 0.384 ± 0.049 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| No CA3 recurrent connections | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| No CA3 (EC to CA1 only) | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| No DG | 0.000 ± 0.000 | 0.002 ± 0.002 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| Perforant path, 75% kept | 0.000 ± 0.000 | 0.452 ± 0.036 | 0.377 ± 0.058 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| Perforant path, 50% kept | 0.000 ± 0.000 | 0.458 ± 0.027 | 0.368 ± 0.062 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| Perforant path, 25% kept | 0.000 ± 0.000 | 0.425 ± 0.040 | 0.341 ± 0.049 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| Vision code alone (baseline) | 0.749 ± 0.023 | 0.811 ± 0.010 | 0.000 ± 0.000 | 0.786 ± 0.021 | 0.778 ± 0.020 | 0.764 ± 0.020 | 0.759 ± 0.022 | 0.661 ± 0.031 |
| No hippocampus | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |

Response rates:

| Arm | old to repeat | similar to repeat | new to repeat | old to lure | similar to lure | new to lure | old to foil | similar to foil | new to foil |
|---|---|---|---|---|---|---|---|---|---|
| Young adults, 20 to 39 | 81.2 | 11.7 | 4.1 | 40.3 | 47.6 | 8.3 | 2.6 | 11.6 | 82.0 |
| Adults 60 to 74 | 82.2 | 7.6 | 5.3 | 54.6 | 23.6 | 12.3 | 4.8 | 12.3 | 73.4 |
| Intact | 79.7 ± 3.2 | 0.0 ± 0.0 | 20.3 ± 3.2 | 38.4 ± 4.9 | 0.0 ± 0.0 | 61.6 ± 4.9 | 34.9 ± 4.2 | 0.0 ± 0.0 | 65.1 ± 4.2 |
| No CA3 recurrent connections | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 |
| No CA3 (EC to CA1 only) | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 |
| No DG | 0.2 ± 0.2 | 0.0 ± 0.0 | 99.8 ± 0.2 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 |
| Perforant path, 75% kept | 79.6 ± 3.3 | 0.0 ± 0.0 | 20.4 ± 3.3 | 37.7 ± 5.8 | 0.0 ± 0.0 | 62.3 ± 5.8 | 34.4 ± 4.2 | 0.0 ± 0.0 | 65.6 ± 4.2 |
| Perforant path, 50% kept | 78.9 ± 3.1 | 0.0 ± 0.0 | 21.1 ± 3.1 | 36.8 ± 6.2 | 0.0 ± 0.0 | 63.2 ± 6.2 | 33.1 ± 4.4 | 0.0 ± 0.0 | 66.9 ± 4.4 |
| Perforant path, 25% kept | 73.1 ± 3.6 | 0.0 ± 0.0 | 26.9 ± 3.6 | 34.1 ± 4.9 | 0.0 ± 0.0 | 65.9 ± 4.9 | 30.6 ± 4.0 | 0.0 ± 0.0 | 69.4 ± 4.0 |
| Vision code alone (baseline) | 81.1 ± 1.0 | 18.9 ± 1.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 93.6 ± 0.7 | 6.4 ± 0.7 | 0.0 ± 0.0 | 18.6 ± 1.9 | 81.4 ± 1.9 |
| No hippocampus | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 |

p(old | lure) by level:

| Arm | C1 | C2 | C3 | C4 | C5 |
|---|---|---|---|---|---|
| Intact | 44.4 ± 4.7 | 40.3 ± 5.0 | 36.6 ± 5.4 | 35.5 ± 5.0 | 35.0 ± 5.5 |
| No CA3 recurrent connections | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No CA3 (EC to CA1 only) | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No DG | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 75% kept | 43.8 ± 4.6 | 39.5 ± 5.7 | 36.3 ± 7.0 | 34.5 ± 6.6 | 34.5 ± 6.4 |
| Perforant path, 50% kept | 43.3 ± 5.3 | 38.4 ± 6.1 | 35.6 ± 6.8 | 33.7 ± 6.3 | 32.9 ± 7.0 |
| Perforant path, 25% kept | 38.7 ± 5.4 | 35.2 ± 5.8 | 32.3 ± 5.1 | 32.2 ± 4.6 | 32.1 ± 5.2 |
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
| Vision code alone (baseline) | 97.2 ± 0.7 | 96.4 ± 0.5 | 95.1 ± 0.6 | 94.5 ± 1.1 | 84.7 ± 1.5 |
| No hippocampus | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |

### R3 (recurrent support of the starting state), other-drawer lures, bins L1 to L5, fixed thresholds

| Arm | LDI | REC | p(old \| lure) | LDI L1 | LDI L2 | LDI L3 | LDI L4 | LDI L5 |
|---|---|---|---|---|---|---|---|---|
| Young adults (Stark and colleagues 2013) | 0.360 | 0.786 | 0.403 | not in text | not in text | not in text | not in text | not in text |
| Intact | 0.045 ± 0.018 | 0.760 ± 0.012 | 0.000 ± 0.000 | 0.032 ± 0.038 | 0.030 ± 0.057 | 0.066 ± 0.043 | 0.058 ± 0.054 | 0.034 ± 0.044 |
| No CA3 recurrent connections | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| No CA3 (EC to CA1 only) | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| No DG | 0.010 ± 0.018 | -0.198 ± 0.026 | 0.844 ± 0.013 | 0.110 ± 0.054 | 0.027 ± 0.044 | -0.022 ± 0.021 | -0.023 ± 0.026 | -0.029 ± 0.028 |
| Perforant path, 75% kept | 0.031 ± 0.013 | 0.595 ± 0.018 | 0.000 ± 0.000 | 0.017 ± 0.023 | 0.032 ± 0.023 | 0.036 ± 0.025 | 0.044 ± 0.027 | 0.024 ± 0.029 |
| Perforant path, 50% kept | 0.006 ± 0.005 | 0.289 ± 0.013 | 0.000 ± 0.000 | -0.000 ± 0.005 | 0.009 ± 0.017 | 0.011 ± 0.011 | 0.007 ± 0.009 | 0.002 ± 0.010 |
| Perforant path, 25% kept | 0.000 ± 0.000 | 0.007 ± 0.004 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| Vision code alone (baseline) | 0.193 ± 0.026 | 0.811 ± 0.010 | 0.000 ± 0.000 | 0.814 ± 0.019 | 0.382 ± 0.049 | -0.020 ± 0.032 | -0.043 ± 0.037 | -0.074 ± 0.052 |
| No hippocampus | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |

Response rates:

| Arm | old to repeat | similar to repeat | new to repeat | old to lure | similar to lure | new to lure | old to foil | similar to foil | new to foil |
|---|---|---|---|---|---|---|---|---|---|
| Young adults, 20 to 39 | 81.2 | 11.7 | 4.1 | 40.3 | 47.6 | 8.3 | 2.6 | 11.6 | 82.0 |
| Adults 60 to 74 | 82.2 | 7.6 | 5.3 | 54.6 | 23.6 | 12.3 | 4.8 | 12.3 | 73.4 |
| Intact | 76.0 ± 1.2 | 20.9 ± 1.3 | 3.2 ± 0.8 | 0.0 ± 0.0 | 19.0 ± 3.5 | 81.0 ± 3.5 | 0.0 ± 0.0 | 14.5 ± 2.5 | 85.5 ± 2.5 |
| No CA3 recurrent connections | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 |
| No CA3 (EC to CA1 only) | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 |
| No DG | 65.6 ± 1.9 | 34.4 ± 1.9 | 0.0 ± 0.1 | 84.4 ± 1.3 | 15.6 ± 1.3 | 0.0 ± 0.0 | 85.3 ± 1.3 | 14.7 ± 1.3 | 0.0 ± 0.0 |
| Perforant path, 75% kept | 59.5 ± 1.8 | 33.1 ± 2.0 | 7.4 ± 1.2 | 0.0 ± 0.0 | 6.7 ± 1.6 | 93.3 ± 1.6 | 0.0 ± 0.0 | 3.6 ± 0.9 | 96.4 ± 0.9 |
| Perforant path, 50% kept | 28.9 ± 1.3 | 50.9 ± 2.2 | 20.2 ± 1.3 | 0.0 ± 0.0 | 0.9 ± 0.6 | 99.1 ± 0.6 | 0.0 ± 0.0 | 0.3 ± 0.2 | 99.7 ± 0.2 |
| Perforant path, 25% kept | 0.7 ± 0.4 | 25.3 ± 1.8 | 74.0 ± 1.8 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 |
| Vision code alone (baseline) | 81.1 ± 1.0 | 18.9 ± 1.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 37.9 ± 1.7 | 62.1 ± 1.7 | 0.0 ± 0.0 | 18.6 ± 1.9 | 81.4 ± 1.9 |
| No hippocampus | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 |

p(old | lure) by level:

| Arm | L1 | L2 | L3 | L4 | L5 |
|---|---|---|---|---|---|
| Intact | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No CA3 recurrent connections | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No CA3 (EC to CA1 only) | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No DG | 74.3 ± 5.7 | 82.7 ± 3.6 | 87.6 ± 2.0 | 87.6 ± 2.4 | 88.2 ± 2.1 |
| Perforant path, 75% kept | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 50% kept | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 25% kept | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Vision code alone (baseline) | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No hippocampus | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |

p(similar | lure) by level:

| Arm | L1 | L2 | L3 | L4 | L5 |
|---|---|---|---|---|---|
| Intact | 17.7 ± 3.6 | 17.5 ± 7.1 | 21.0 ± 4.9 | 20.2 ± 6.3 | 17.9 ± 5.2 |
| No CA3 recurrent connections | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No CA3 (EC to CA1 only) | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No DG | 25.7 ± 5.7 | 17.3 ± 3.6 | 12.4 ± 2.0 | 12.4 ± 2.4 | 11.8 ± 2.1 |
| Perforant path, 75% kept | 5.3 ± 2.2 | 6.8 ± 2.3 | 7.2 ± 2.7 | 8.0 ± 2.8 | 6.0 ± 3.3 |
| Perforant path, 50% kept | 0.2 ± 0.5 | 1.2 ± 1.7 | 1.4 ± 1.2 | 0.9 ± 0.8 | 0.5 ± 1.1 |
| Perforant path, 25% kept | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Vision code alone (baseline) | 100.0 ± 0.0 | 56.8 ± 4.2 | 16.6 ± 2.8 | 14.3 ± 3.0 | 11.3 ± 3.6 |
| No hippocampus | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |

### R3 (recurrent support of the starting state), closer lures, levels C1 to C5, fixed thresholds

| Arm | LDI | REC | p(old \| lure) | LDI C1 | LDI C2 | LDI C3 | LDI C4 | LDI C5 |
|---|---|---|---|---|---|---|---|---|
| Young adults (Stark and colleagues 2013) | 0.360 | 0.786 | 0.403 | not in text | not in text | not in text | not in text | not in text |
| Intact | 0.415 ± 0.042 | 0.760 ± 0.012 | 0.000 ± 0.000 | 0.498 ± 0.047 | 0.455 ± 0.046 | 0.397 ± 0.040 | 0.374 ± 0.046 | 0.352 ± 0.042 |
| No CA3 recurrent connections | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| No CA3 (EC to CA1 only) | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| No DG | -0.145 ± 0.013 | -0.198 ± 0.026 | 0.999 ± 0.001 | -0.145 ± 0.013 | -0.145 ± 0.014 | -0.146 ± 0.013 | -0.145 ± 0.012 | -0.145 ± 0.013 |
| Perforant path, 75% kept | 0.265 ± 0.057 | 0.595 ± 0.018 | 0.000 ± 0.000 | 0.360 ± 0.056 | 0.312 ± 0.052 | 0.243 ± 0.062 | 0.205 ± 0.057 | 0.204 ± 0.065 |
| Perforant path, 50% kept | 0.065 ± 0.020 | 0.289 ± 0.013 | 0.000 ± 0.000 | 0.121 ± 0.031 | 0.082 ± 0.023 | 0.052 ± 0.021 | 0.035 ± 0.015 | 0.036 ± 0.017 |
| Perforant path, 25% kept | 0.001 ± 0.001 | 0.007 ± 0.004 | 0.000 ± 0.000 | 0.005 ± 0.003 | 0.001 ± 0.001 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| Vision code alone (baseline) | 0.749 ± 0.023 | 0.811 ± 0.010 | 0.000 ± 0.000 | 0.786 ± 0.021 | 0.778 ± 0.020 | 0.764 ± 0.020 | 0.759 ± 0.022 | 0.661 ± 0.031 |
| No hippocampus | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |

Response rates:

| Arm | old to repeat | similar to repeat | new to repeat | old to lure | similar to lure | new to lure | old to foil | similar to foil | new to foil |
|---|---|---|---|---|---|---|---|---|---|
| Young adults, 20 to 39 | 81.2 | 11.7 | 4.1 | 40.3 | 47.6 | 8.3 | 2.6 | 11.6 | 82.0 |
| Adults 60 to 74 | 82.2 | 7.6 | 5.3 | 54.6 | 23.6 | 12.3 | 4.8 | 12.3 | 73.4 |
| Intact | 76.0 ± 1.2 | 20.9 ± 1.3 | 3.2 ± 0.8 | 0.0 ± 0.0 | 56.0 ± 6.0 | 44.0 ± 6.0 | 0.0 ± 0.0 | 14.5 ± 2.5 | 85.5 ± 2.5 |
| No CA3 recurrent connections | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 |
| No CA3 (EC to CA1 only) | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 |
| No DG | 65.6 ± 1.9 | 34.4 ± 1.9 | 0.0 ± 0.1 | 99.9 ± 0.1 | 0.1 ± 0.1 | 0.0 ± 0.0 | 85.3 ± 1.3 | 14.7 ± 1.3 | 0.0 ± 0.0 |
| Perforant path, 75% kept | 59.5 ± 1.8 | 33.1 ± 2.0 | 7.4 ± 1.2 | 0.0 ± 0.0 | 30.1 ± 6.0 | 69.9 ± 6.0 | 0.0 ± 0.0 | 3.6 ± 0.9 | 96.4 ± 0.9 |
| Perforant path, 50% kept | 28.9 ± 1.3 | 50.9 ± 2.2 | 20.2 ± 1.3 | 0.0 ± 0.0 | 6.8 ± 2.0 | 93.2 ± 2.0 | 0.0 ± 0.0 | 0.3 ± 0.2 | 99.7 ± 0.2 |
| Perforant path, 25% kept | 0.7 ± 0.4 | 25.3 ± 1.8 | 74.0 ± 1.8 | 0.0 ± 0.0 | 0.1 ± 0.1 | 99.9 ± 0.1 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 |
| Vision code alone (baseline) | 81.1 ± 1.0 | 18.9 ± 1.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 93.6 ± 0.7 | 6.4 ± 0.7 | 0.0 ± 0.0 | 18.6 ± 1.9 | 81.4 ± 1.9 |
| No hippocampus | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 |

p(old | lure) by level:

| Arm | C1 | C2 | C3 | C4 | C5 |
|---|---|---|---|---|---|
| Intact | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No CA3 recurrent connections | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No CA3 (EC to CA1 only) | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No DG | 99.9 ± 0.1 | 99.9 ± 0.2 | 99.9 ± 0.1 | 99.8 ± 0.2 | 99.8 ± 0.2 |
| Perforant path, 75% kept | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 50% kept | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 25% kept | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Vision code alone (baseline) | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No hippocampus | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |

p(similar | lure) by level:

| Arm | C1 | C2 | C3 | C4 | C5 |
|---|---|---|---|---|---|
| Intact | 64.3 ± 6.3 | 60.0 ± 6.4 | 54.2 ± 5.9 | 51.8 ± 6.1 | 49.7 ± 5.7 |
| No CA3 recurrent connections | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No CA3 (EC to CA1 only) | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No DG | 0.1 ± 0.1 | 0.1 ± 0.2 | 0.1 ± 0.1 | 0.2 ± 0.2 | 0.2 ± 0.2 |
| Perforant path, 75% kept | 39.6 ± 6.0 | 34.8 ± 5.6 | 27.9 ± 6.5 | 24.1 ± 6.0 | 23.9 ± 6.8 |
| Perforant path, 50% kept | 12.4 ± 3.1 | 8.5 ± 2.3 | 5.5 ± 2.1 | 3.7 ± 1.6 | 3.8 ± 1.7 |
| Perforant path, 25% kept | 0.5 ± 0.3 | 0.1 ± 0.1 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Vision code alone (baseline) | 97.2 ± 0.7 | 96.4 ± 0.5 | 95.1 ± 0.6 | 94.5 ± 1.1 | 84.7 ± 1.5 |
| No hippocampus | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |

### R3s (self-support of the starting state), other-drawer lures, bins L1 to L5, fixed thresholds

| Arm | LDI | REC | p(old \| lure) | LDI L1 | LDI L2 | LDI L3 | LDI L4 | LDI L5 |
|---|---|---|---|---|---|---|---|---|
| Young adults (Stark and colleagues 2013) | 0.360 | 0.786 | 0.403 | not in text | not in text | not in text | not in text | not in text |
| Intact | 0.058 ± 0.025 | 0.762 ± 0.012 | 0.000 ± 0.000 | 0.044 ± 0.041 | 0.052 ± 0.047 | 0.071 ± 0.044 | 0.074 ± 0.053 | 0.040 ± 0.049 |
| No CA3 recurrent connections | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| No CA3 (EC to CA1 only) | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| No DG | 0.000 ± 0.000 | 0.008 ± 0.003 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| Perforant path, 75% kept | 0.043 ± 0.015 | 0.602 ± 0.018 | 0.000 ± 0.000 | 0.032 ± 0.030 | 0.037 ± 0.038 | 0.041 ± 0.035 | 0.067 ± 0.038 | 0.031 ± 0.022 |
| Perforant path, 50% kept | 0.024 ± 0.006 | 0.307 ± 0.014 | 0.000 ± 0.000 | 0.020 ± 0.018 | 0.022 ± 0.024 | 0.027 ± 0.021 | 0.029 ± 0.019 | 0.019 ± 0.018 |
| Perforant path, 25% kept | 0.001 ± 0.003 | 0.012 ± 0.008 | 0.000 ± 0.000 | -0.000 ± 0.001 | 0.002 ± 0.006 | 0.002 ± 0.005 | 0.002 ± 0.005 | -0.000 ± 0.001 |
| Vision code alone (baseline) | 0.193 ± 0.026 | 0.811 ± 0.010 | 0.000 ± 0.000 | 0.814 ± 0.019 | 0.382 ± 0.049 | -0.020 ± 0.032 | -0.043 ± 0.037 | -0.074 ± 0.052 |
| No hippocampus | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |

Response rates:

| Arm | old to repeat | similar to repeat | new to repeat | old to lure | similar to lure | new to lure | old to foil | similar to foil | new to foil |
|---|---|---|---|---|---|---|---|---|---|
| Young adults, 20 to 39 | 81.2 | 11.7 | 4.1 | 40.3 | 47.6 | 8.3 | 2.6 | 11.6 | 82.0 |
| Adults 60 to 74 | 82.2 | 7.6 | 5.3 | 54.6 | 23.6 | 12.3 | 4.8 | 12.3 | 73.4 |
| Intact | 76.2 ± 1.2 | 22.2 ± 1.4 | 1.6 ± 0.3 | 0.0 ± 0.0 | 22.9 ± 1.9 | 77.1 ± 1.9 | 0.0 ± 0.0 | 17.1 ± 1.7 | 82.9 ± 1.7 |
| No CA3 recurrent connections | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 |
| No CA3 (EC to CA1 only) | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 |
| No DG | 0.8 ± 0.3 | 99.2 ± 0.3 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 75% kept | 60.2 ± 1.8 | 35.9 ± 1.9 | 3.9 ± 1.0 | 0.0 ± 0.0 | 11.5 ± 1.7 | 88.5 ± 1.7 | 0.0 ± 0.0 | 7.2 ± 0.6 | 92.8 ± 0.6 |
| Perforant path, 50% kept | 30.7 ± 1.4 | 57.2 ± 1.9 | 12.1 ± 1.2 | 0.0 ± 0.0 | 3.8 ± 0.7 | 96.2 ± 0.7 | 0.0 ± 0.0 | 1.5 ± 0.5 | 98.5 ± 0.5 |
| Perforant path, 25% kept | 1.2 ± 0.8 | 42.8 ± 2.3 | 56.0 ± 2.4 | 0.0 ± 0.0 | 0.2 ± 0.2 | 99.8 ± 0.2 | 0.0 ± 0.0 | 0.0 ± 0.1 | 100.0 ± 0.1 |
| Vision code alone (baseline) | 81.1 ± 1.0 | 18.9 ± 1.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 37.9 ± 1.7 | 62.1 ± 1.7 | 0.0 ± 0.0 | 18.6 ± 1.9 | 81.4 ± 1.9 |
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
| Intact | 21.4 ± 3.4 | 22.3 ± 5.1 | 24.2 ± 3.8 | 24.5 ± 4.8 | 21.1 ± 4.5 |
| No CA3 recurrent connections | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No CA3 (EC to CA1 only) | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No DG | 100.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 |
| Perforant path, 75% kept | 10.4 ± 3.1 | 10.9 ± 3.8 | 11.3 ± 3.9 | 13.9 ± 3.6 | 10.3 ± 2.4 |
| Perforant path, 50% kept | 3.5 ± 1.8 | 3.7 ± 2.2 | 4.1 ± 2.2 | 4.3 ± 1.8 | 3.3 ± 2.1 |
| Perforant path, 25% kept | 0.0 ± 0.0 | 0.3 ± 0.6 | 0.3 ± 0.5 | 0.3 ± 0.5 | 0.0 ± 0.0 |
| Vision code alone (baseline) | 100.0 ± 0.0 | 56.8 ± 4.2 | 16.6 ± 2.8 | 14.3 ± 3.0 | 11.3 ± 3.6 |
| No hippocampus | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |

### R3s (self-support of the starting state), closer lures, levels C1 to C5, fixed thresholds

| Arm | LDI | REC | p(old \| lure) | LDI C1 | LDI C2 | LDI C3 | LDI C4 | LDI C5 |
|---|---|---|---|---|---|---|---|---|
| Young adults (Stark and colleagues 2013) | 0.360 | 0.786 | 0.403 | not in text | not in text | not in text | not in text | not in text |
| Intact | 0.233 ± 0.045 | 0.762 ± 0.012 | 0.000 ± 0.000 | 0.335 ± 0.047 | 0.285 ± 0.042 | 0.205 ± 0.051 | 0.178 ± 0.051 | 0.162 ± 0.049 |
| No CA3 recurrent connections | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| No CA3 (EC to CA1 only) | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| No DG | 0.000 ± 0.000 | 0.008 ± 0.003 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| Perforant path, 75% kept | 0.165 ± 0.031 | 0.602 ± 0.018 | 0.000 ± 0.000 | 0.275 ± 0.035 | 0.204 ± 0.027 | 0.146 ± 0.034 | 0.105 ± 0.031 | 0.099 ± 0.037 |
| Perforant path, 50% kept | 0.072 ± 0.015 | 0.307 ± 0.014 | 0.000 ± 0.000 | 0.139 ± 0.021 | 0.092 ± 0.019 | 0.054 ± 0.018 | 0.037 ± 0.012 | 0.037 ± 0.014 |
| Perforant path, 25% kept | 0.009 ± 0.002 | 0.012 ± 0.008 | 0.000 ± 0.000 | 0.025 ± 0.005 | 0.013 ± 0.006 | 0.005 ± 0.002 | 0.002 ± 0.002 | 0.001 ± 0.001 |
| Vision code alone (baseline) | 0.749 ± 0.023 | 0.811 ± 0.010 | 0.000 ± 0.000 | 0.786 ± 0.021 | 0.778 ± 0.020 | 0.764 ± 0.020 | 0.759 ± 0.022 | 0.661 ± 0.031 |
| No hippocampus | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |

Response rates:

| Arm | old to repeat | similar to repeat | new to repeat | old to lure | similar to lure | new to lure | old to foil | similar to foil | new to foil |
|---|---|---|---|---|---|---|---|---|---|
| Young adults, 20 to 39 | 81.2 | 11.7 | 4.1 | 40.3 | 47.6 | 8.3 | 2.6 | 11.6 | 82.0 |
| Adults 60 to 74 | 82.2 | 7.6 | 5.3 | 54.6 | 23.6 | 12.3 | 4.8 | 12.3 | 73.4 |
| Intact | 76.2 ± 1.2 | 22.2 ± 1.4 | 1.6 ± 0.3 | 0.0 ± 0.0 | 40.4 ± 4.2 | 59.6 ± 4.2 | 0.0 ± 0.0 | 17.1 ± 1.7 | 82.9 ± 1.7 |
| No CA3 recurrent connections | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 |
| No CA3 (EC to CA1 only) | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 |
| No DG | 0.8 ± 0.3 | 99.2 ± 0.3 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 75% kept | 60.2 ± 1.8 | 35.9 ± 1.9 | 3.9 ± 1.0 | 0.0 ± 0.0 | 23.8 ± 3.4 | 76.2 ± 3.4 | 0.0 ± 0.0 | 7.2 ± 0.6 | 92.8 ± 0.6 |
| Perforant path, 50% kept | 30.7 ± 1.4 | 57.2 ± 1.9 | 12.1 ± 1.2 | 0.0 ± 0.0 | 8.7 ± 1.4 | 91.3 ± 1.4 | 0.0 ± 0.0 | 1.5 ± 0.5 | 98.5 ± 0.5 |
| Perforant path, 25% kept | 1.2 ± 0.8 | 42.8 ± 2.3 | 56.0 ± 2.4 | 0.0 ± 0.0 | 1.0 ± 0.2 | 99.0 ± 0.2 | 0.0 ± 0.0 | 0.0 ± 0.1 | 100.0 ± 0.1 |
| Vision code alone (baseline) | 81.1 ± 1.0 | 18.9 ± 1.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 93.6 ± 0.7 | 6.4 ± 0.7 | 0.0 ± 0.0 | 18.6 ± 1.9 | 81.4 ± 1.9 |
| No hippocampus | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 |

p(old | lure) by level:

| Arm | C1 | C2 | C3 | C4 | C5 |
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

| Arm | C1 | C2 | C3 | C4 | C5 |
|---|---|---|---|---|---|
| Intact | 50.6 ± 4.2 | 45.6 ± 3.9 | 37.6 ± 5.0 | 34.9 ± 4.6 | 33.3 ± 4.7 |
| No CA3 recurrent connections | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No CA3 (EC to CA1 only) | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| No DG | 100.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 |
| Perforant path, 75% kept | 34.7 ± 3.8 | 27.6 ± 3.0 | 21.8 ± 3.8 | 17.7 ± 3.4 | 17.1 ± 4.0 |
| Perforant path, 50% kept | 15.4 ± 2.2 | 10.7 ± 1.9 | 6.9 ± 1.6 | 5.2 ± 1.0 | 5.2 ± 1.4 |
| Perforant path, 25% kept | 2.6 ± 0.5 | 1.3 ± 0.6 | 0.5 ± 0.2 | 0.3 ± 0.2 | 0.2 ± 0.2 |
| Vision code alone (baseline) | 97.2 ± 0.7 | 96.4 ± 0.5 | 95.1 ± 0.6 | 94.5 ± 1.1 | 84.7 ± 1.5 |
| No hippocampus | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |

### Each arm with its own thresholds, R1 (CA1 comparator), closer lures (secondary)

| Arm | LDI | REC | p(old \| lure) | LDI C1 | LDI C2 | LDI C3 | LDI C4 | LDI C5 |
|---|---|---|---|---|---|---|---|---|
| Intact | -0.007 ± 0.028 | 0.728 ± 0.020 | 0.023 ± 0.002 | 0.049 ± 0.030 | 0.072 ± 0.031 | 0.000 ± 0.033 | -0.053 ± 0.032 | -0.101 ± 0.030 |
| No CA3 recurrent connections | 0.075 ± 0.029 | 0.721 ± 0.022 | 0.000 ± 0.000 | 0.238 ± 0.037 | 0.142 ± 0.033 | 0.066 ± 0.027 | -0.001 ± 0.031 | -0.071 ± 0.030 |
| No CA3 (EC to CA1 only) | 0.538 ± 0.019 | 0.729 ± 0.020 | 0.027 ± 0.004 | 0.613 ± 0.017 | 0.720 ± 0.020 | 0.646 ± 0.023 | 0.479 ± 0.032 | 0.230 ± 0.023 |
| No DG | 0.000 ± 0.000 | 0.508 ± 0.020 | 0.386 ± 0.017 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| Perforant path, 75% kept | -0.009 ± 0.026 | 0.728 ± 0.019 | 0.022 ± 0.002 | 0.045 ± 0.025 | 0.059 ± 0.028 | -0.004 ± 0.031 | -0.045 ± 0.035 | -0.100 ± 0.023 |
| Perforant path, 50% kept | -0.011 ± 0.021 | 0.727 ± 0.018 | 0.021 ± 0.003 | 0.033 ± 0.022 | 0.056 ± 0.021 | -0.008 ± 0.029 | -0.046 ± 0.027 | -0.091 ± 0.023 |
| Perforant path, 25% kept | 0.003 ± 0.017 | 0.751 ± 0.023 | 0.021 ± 0.003 | 0.014 ± 0.020 | 0.054 ± 0.027 | 0.021 ± 0.023 | -0.021 ± 0.030 | -0.055 ± 0.018 |
| Vision code alone (baseline) | 0.749 ± 0.023 | 0.811 ± 0.010 | 0.000 ± 0.000 | 0.786 ± 0.021 | 0.778 ± 0.020 | 0.764 ± 0.020 | 0.759 ± 0.022 | 0.661 ± 0.031 |

### Each arm with its own thresholds, R2 (self-support of the settled state), closer lures (secondary)

| Arm | LDI | REC | p(old \| lure) | LDI C1 | LDI C2 | LDI C3 | LDI C4 | LDI C5 |
|---|---|---|---|---|---|---|---|---|
| Intact | 0.000 ± 0.000 | 0.449 ± 0.023 | 0.384 ± 0.049 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| No DG | 0.000 ± 0.000 | 0.404 ± 0.060 | 0.291 ± 0.089 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| Perforant path, 75% kept | 0.000 ± 0.000 | 0.451 ± 0.037 | 0.383 ± 0.058 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| Perforant path, 50% kept | 0.000 ± 0.000 | 0.458 ± 0.028 | 0.378 ± 0.062 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| Perforant path, 25% kept | 0.000 ± 0.000 | 0.405 ± 0.051 | 0.409 ± 0.056 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| Vision code alone (baseline) | 0.749 ± 0.023 | 0.811 ± 0.010 | 0.000 ± 0.000 | 0.786 ± 0.021 | 0.778 ± 0.020 | 0.764 ± 0.020 | 0.759 ± 0.022 | 0.661 ± 0.031 |

### Each arm with its own thresholds, R3 (recurrent support of the starting state), closer lures (secondary)

| Arm | LDI | REC | p(old \| lure) | LDI C1 | LDI C2 | LDI C3 | LDI C4 | LDI C5 |
|---|---|---|---|---|---|---|---|---|
| Intact | 0.415 ± 0.042 | 0.760 ± 0.012 | 0.000 ± 0.000 | 0.498 ± 0.047 | 0.455 ± 0.046 | 0.397 ± 0.040 | 0.374 ± 0.046 | 0.352 ± 0.042 |
| No DG | 0.000 ± 0.000 | -0.107 ± 0.019 | 1.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| Perforant path, 75% kept | 0.458 ± 0.046 | 0.760 ± 0.013 | 0.000 ± 0.000 | 0.533 ± 0.041 | 0.498 ± 0.045 | 0.439 ± 0.048 | 0.418 ± 0.052 | 0.401 ± 0.051 |
| Perforant path, 50% kept | 0.522 ± 0.041 | 0.762 ± 0.012 | 0.010 ± 0.002 | 0.573 ± 0.037 | 0.561 ± 0.049 | 0.507 ± 0.045 | 0.488 ± 0.044 | 0.483 ± 0.045 |
| Perforant path, 25% kept | 0.000 ± 0.000 | 0.156 ± 0.028 | 0.992 ± 0.002 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| Vision code alone (baseline) | 0.749 ± 0.023 | 0.811 ± 0.010 | 0.000 ± 0.000 | 0.786 ± 0.021 | 0.778 ± 0.020 | 0.764 ± 0.020 | 0.759 ± 0.022 | 0.661 ± 0.031 |

### Each arm with its own thresholds, R3s (self-support of the starting state), closer lures (secondary)

| Arm | LDI | REC | p(old \| lure) | LDI C1 | LDI C2 | LDI C3 | LDI C4 | LDI C5 |
|---|---|---|---|---|---|---|---|---|
| Intact | 0.233 ± 0.045 | 0.762 ± 0.012 | 0.000 ± 0.000 | 0.335 ± 0.047 | 0.285 ± 0.042 | 0.205 ± 0.051 | 0.178 ± 0.051 | 0.162 ± 0.049 |
| No DG | -0.233 ± 0.028 | 0.785 ± 0.011 | 0.000 ± 0.000 | -0.223 ± 0.031 | -0.238 ± 0.030 | -0.226 ± 0.034 | -0.237 ± 0.025 | -0.242 ± 0.032 |
| Perforant path, 75% kept | 0.292 ± 0.047 | 0.762 ± 0.010 | 0.000 ± 0.000 | 0.395 ± 0.041 | 0.339 ± 0.042 | 0.274 ± 0.051 | 0.232 ± 0.060 | 0.221 ± 0.054 |
| Perforant path, 50% kept | 0.392 ± 0.043 | 0.758 ± 0.010 | 0.001 ± 0.001 | 0.486 ± 0.048 | 0.439 ± 0.041 | 0.372 ± 0.053 | 0.336 ± 0.044 | 0.328 ± 0.041 |
| Perforant path, 25% kept | 0.000 ± 0.000 | 0.342 ± 0.040 | 0.970 ± 0.004 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| Vision code alone (baseline) | 0.749 ± 0.023 | 0.811 ± 0.010 | 0.000 ± 0.000 | 0.786 ± 0.021 | 0.778 ± 0.020 | 0.764 ± 0.020 | 0.759 ± 0.022 | 0.661 ± 0.031 |

### Older adults' criteria, R1 (CA1 comparator), other-drawer lures, bins L1 to L5

| Arm | old to repeat | similar to repeat | new to repeat | old to lure | similar to lure | new to lure | old to foil | similar to foil | new to foil |
|---|---|---|---|---|---|---|---|---|---|
| Young adults, 20 to 39 | 81.2 | 11.7 | 4.1 | 40.3 | 47.6 | 8.3 | 2.6 | 11.6 | 82.0 |
| Adults 60 to 74 | 82.2 | 7.6 | 5.3 | 54.6 | 23.6 | 12.3 | 4.8 | 12.3 | 73.4 |
| Intact | 74.4 ± 2.1 | 25.3 ± 2.1 | 0.3 ± 0.3 | 0.0 ± 0.0 | 45.7 ± 1.3 | 54.3 ± 1.3 | 0.0 ± 0.0 | 32.8 ± 2.3 | 67.2 ± 2.3 |
| Perforant path, 75% kept | 74.4 ± 2.1 | 25.2 ± 2.1 | 0.4 ± 0.2 | 0.0 ± 0.0 | 44.4 ± 2.1 | 55.6 ± 2.1 | 0.0 ± 0.0 | 33.5 ± 1.3 | 66.5 ± 1.3 |
| Perforant path, 50% kept | 74.3 ± 2.0 | 24.0 ± 1.8 | 1.7 ± 0.6 | 0.0 ± 0.0 | 44.4 ± 1.5 | 55.6 ± 1.5 | 0.0 ± 0.0 | 33.2 ± 2.0 | 66.8 ± 2.0 |
| Perforant path, 25% kept | 77.2 ± 2.2 | 14.8 ± 2.0 | 8.0 ± 1.5 | 0.0 ± 0.0 | 41.1 ± 2.2 | 58.9 ± 2.2 | 0.0 ± 0.0 | 34.6 ± 1.8 | 65.4 ± 1.8 |

p(old | lure) by level:

| Arm | L1 | L2 | L3 | L4 | L5 |
|---|---|---|---|---|---|
| Intact | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 75% kept | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 50% kept | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 25% kept | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |

### Older adults' criteria, R1 (CA1 comparator), closer lures, levels C1 to C5

| Arm | old to repeat | similar to repeat | new to repeat | old to lure | similar to lure | new to lure | old to foil | similar to foil | new to foil |
|---|---|---|---|---|---|---|---|---|---|
| Young adults, 20 to 39 | 81.2 | 11.7 | 4.1 | 40.3 | 47.6 | 8.3 | 2.6 | 11.6 | 82.0 |
| Adults 60 to 74 | 82.2 | 7.6 | 5.3 | 54.6 | 23.6 | 12.3 | 4.8 | 12.3 | 73.4 |
| Intact | 74.4 ± 2.1 | 25.3 ± 2.1 | 0.3 ± 0.3 | 2.4 ± 0.3 | 26.7 ± 2.8 | 70.9 ± 2.9 | 0.0 ± 0.0 | 32.8 ± 2.3 | 67.2 ± 2.3 |
| Perforant path, 75% kept | 74.4 ± 2.1 | 25.2 ± 2.1 | 0.4 ± 0.2 | 2.3 ± 0.2 | 27.3 ± 2.8 | 70.4 ± 2.8 | 0.0 ± 0.0 | 33.5 ± 1.3 | 66.5 ± 1.3 |
| Perforant path, 50% kept | 74.3 ± 2.0 | 24.0 ± 1.8 | 1.7 ± 0.6 | 2.2 ± 0.3 | 28.5 ± 2.8 | 69.3 ± 2.9 | 0.0 ± 0.0 | 33.2 ± 2.0 | 66.8 ± 2.0 |
| Perforant path, 25% kept | 77.2 ± 2.2 | 14.8 ± 2.0 | 8.0 ± 1.5 | 2.3 ± 0.2 | 32.5 ± 1.8 | 65.2 ± 1.8 | 0.0 ± 0.0 | 34.6 ± 1.8 | 65.4 ± 1.8 |

p(old | lure) by level:

| Arm | C1 | C2 | C3 | C4 | C5 |
|---|---|---|---|---|---|
| Intact | 11.5 ± 1.2 | 0.4 ± 0.3 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 75% kept | 11.3 ± 1.1 | 0.4 ± 0.3 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 50% kept | 10.6 ± 1.4 | 0.4 ± 0.3 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 25% kept | 10.7 ± 1.0 | 0.7 ± 0.4 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |

### Older adults' criteria, R2 (self-support of the settled state), other-drawer lures, bins L1 to L5

| Arm | old to repeat | similar to repeat | new to repeat | old to lure | similar to lure | new to lure | old to foil | similar to foil | new to foil |
|---|---|---|---|---|---|---|---|---|---|
| Young adults, 20 to 39 | 81.2 | 11.7 | 4.1 | 40.3 | 47.6 | 8.3 | 2.6 | 11.6 | 82.0 |
| Adults 60 to 74 | 82.2 | 7.6 | 5.3 | 54.6 | 23.6 | 12.3 | 4.8 | 12.3 | 73.4 |
| Intact | 80.6 ± 3.3 | 0.0 ± 0.0 | 19.4 ± 3.3 | 40.2 ± 3.1 | 0.0 ± 0.0 | 59.8 ± 3.1 | 36.0 ± 4.6 | 0.0 ± 0.0 | 64.0 ± 4.6 |
| Perforant path, 75% kept | 80.9 ± 3.3 | 0.0 ± 0.0 | 19.1 ± 3.3 | 39.6 ± 3.8 | 0.0 ± 0.0 | 60.4 ± 3.8 | 35.8 ± 4.8 | 0.0 ± 0.0 | 64.2 ± 4.8 |
| Perforant path, 50% kept | 80.9 ± 3.1 | 0.0 ± 0.0 | 19.1 ± 3.1 | 38.7 ± 4.5 | 0.0 ± 0.0 | 61.3 ± 4.5 | 35.3 ± 4.9 | 0.0 ± 0.0 | 64.7 ± 4.9 |
| Perforant path, 25% kept | 79.3 ± 2.9 | 0.0 ± 0.0 | 20.7 ± 2.9 | 43.0 ± 4.2 | 0.0 ± 0.0 | 57.0 ± 4.2 | 39.1 ± 5.0 | 0.0 ± 0.0 | 60.9 ± 5.0 |

p(old | lure) by level:

| Arm | L1 | L2 | L3 | L4 | L5 |
|---|---|---|---|---|---|
| Intact | 43.0 ± 5.6 | 38.4 ± 4.8 | 41.5 ± 6.5 | 40.9 ± 4.4 | 37.3 ± 5.2 |
| Perforant path, 75% kept | 41.2 ± 6.3 | 39.4 ± 5.7 | 40.5 ± 5.6 | 38.7 ± 4.0 | 38.5 ± 4.7 |
| Perforant path, 50% kept | 37.7 ± 6.5 | 37.5 ± 5.7 | 40.6 ± 4.7 | 38.6 ± 8.1 | 38.5 ± 5.8 |
| Perforant path, 25% kept | 42.3 ± 5.2 | 43.5 ± 5.7 | 41.2 ± 5.7 | 45.4 ± 4.5 | 42.5 ± 6.8 |

### Older adults' criteria, R2 (self-support of the settled state), closer lures, levels C1 to C5

| Arm | old to repeat | similar to repeat | new to repeat | old to lure | similar to lure | new to lure | old to foil | similar to foil | new to foil |
|---|---|---|---|---|---|---|---|---|---|
| Young adults, 20 to 39 | 81.2 | 11.7 | 4.1 | 40.3 | 47.6 | 8.3 | 2.6 | 11.6 | 82.0 |
| Adults 60 to 74 | 82.2 | 7.6 | 5.3 | 54.6 | 23.6 | 12.3 | 4.8 | 12.3 | 73.4 |
| Intact | 80.6 ± 3.3 | 0.0 ± 0.0 | 19.4 ± 3.3 | 40.0 ± 5.0 | 0.0 ± 0.0 | 60.0 ± 5.0 | 36.0 ± 4.6 | 0.0 ± 0.0 | 64.0 ± 4.6 |
| Perforant path, 75% kept | 80.9 ± 3.3 | 0.0 ± 0.0 | 19.1 ± 3.3 | 39.6 ± 5.8 | 0.0 ± 0.0 | 60.4 ± 5.8 | 35.8 ± 4.8 | 0.0 ± 0.0 | 64.2 ± 4.8 |
| Perforant path, 50% kept | 80.9 ± 3.1 | 0.0 ± 0.0 | 19.1 ± 3.1 | 39.1 ± 6.2 | 0.0 ± 0.0 | 60.9 ± 6.2 | 35.3 ± 4.9 | 0.0 ± 0.0 | 64.7 ± 4.9 |
| Perforant path, 25% kept | 79.3 ± 2.9 | 0.0 ± 0.0 | 20.7 ± 2.9 | 42.6 ± 5.5 | 0.0 ± 0.0 | 57.4 ± 5.5 | 39.1 ± 5.0 | 0.0 ± 0.0 | 60.9 ± 5.0 |

p(old | lure) by level:

| Arm | C1 | C2 | C3 | C4 | C5 |
|---|---|---|---|---|---|
| Intact | 45.9 ± 4.8 | 41.8 ± 5.1 | 38.3 ± 5.3 | 37.0 ± 5.1 | 36.8 ± 5.6 |
| Perforant path, 75% kept | 45.5 ± 4.7 | 41.2 ± 5.8 | 38.4 ± 7.0 | 36.3 ± 6.7 | 36.4 ± 6.7 |
| Perforant path, 50% kept | 45.5 ± 5.2 | 40.5 ± 6.1 | 38.1 ± 7.1 | 36.2 ± 6.3 | 35.3 ± 7.1 |
| Perforant path, 25% kept | 46.9 ± 6.1 | 43.4 ± 5.9 | 41.2 ± 5.1 | 40.9 ± 5.4 | 40.5 ± 6.0 |

### Older adults' criteria, R3 (recurrent support of the starting state), other-drawer lures, bins L1 to L5

| Arm | old to repeat | similar to repeat | new to repeat | old to lure | similar to lure | new to lure | old to foil | similar to foil | new to foil |
|---|---|---|---|---|---|---|---|---|---|
| Young adults, 20 to 39 | 81.2 | 11.7 | 4.1 | 40.3 | 47.6 | 8.3 | 2.6 | 11.6 | 82.0 |
| Adults 60 to 74 | 82.2 | 7.6 | 5.3 | 54.6 | 23.6 | 12.3 | 4.8 | 12.3 | 73.4 |
| Intact | 77.2 ± 1.0 | 19.8 ± 1.1 | 3.0 ± 0.6 | 0.0 ± 0.0 | 26.0 ± 4.1 | 74.0 ± 4.1 | 0.0 ± 0.0 | 22.2 ± 2.8 | 77.8 ± 2.8 |
| Perforant path, 75% kept | 77.3 ± 1.2 | 16.6 ± 1.2 | 6.1 ± 1.2 | 0.0 ± 0.0 | 24.2 ± 3.2 | 75.8 ± 3.2 | 0.0 ± 0.0 | 21.2 ± 2.6 | 78.8 ± 2.6 |
| Perforant path, 50% kept | 77.4 ± 1.2 | 8.2 ± 1.1 | 14.5 ± 1.3 | 0.3 ± 0.2 | 23.0 ± 3.3 | 76.7 ± 3.4 | 0.0 ± 0.1 | 21.1 ± 2.6 | 78.9 ± 2.6 |
| Perforant path, 25% kept | 76.0 ± 2.4 | 0.0 ± 0.0 | 24.0 ± 2.4 | 62.4 ± 2.7 | 0.0 ± 0.0 | 37.6 ± 2.7 | 62.0 ± 3.4 | 0.0 ± 0.0 | 38.0 ± 3.4 |

p(old | lure) by level:

| Arm | L1 | L2 | L3 | L4 | L5 |
|---|---|---|---|---|---|
| Intact | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 75% kept | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 50% kept | 0.1 ± 0.4 | 0.5 ± 0.7 | 0.3 ± 0.5 | 0.5 ± 0.6 | 0.1 ± 0.3 |
| Perforant path, 25% kept | 49.9 ± 5.2 | 61.3 ± 8.8 | 66.3 ± 3.0 | 66.6 ± 4.3 | 65.9 ± 4.3 |

### Older adults' criteria, R3 (recurrent support of the starting state), closer lures, levels C1 to C5

| Arm | old to repeat | similar to repeat | new to repeat | old to lure | similar to lure | new to lure | old to foil | similar to foil | new to foil |
|---|---|---|---|---|---|---|---|---|---|
| Young adults, 20 to 39 | 81.2 | 11.7 | 4.1 | 40.3 | 47.6 | 8.3 | 2.6 | 11.6 | 82.0 |
| Adults 60 to 74 | 82.2 | 7.6 | 5.3 | 54.6 | 23.6 | 12.3 | 4.8 | 12.3 | 73.4 |
| Intact | 77.2 ± 1.0 | 19.8 ± 1.1 | 3.0 ± 0.6 | 0.0 ± 0.0 | 68.5 ± 4.8 | 31.5 ± 4.8 | 0.0 ± 0.0 | 22.2 ± 2.8 | 77.8 ± 2.8 |
| Perforant path, 75% kept | 77.3 ± 1.2 | 16.6 ± 1.2 | 6.1 ± 1.2 | 0.0 ± 0.0 | 71.5 ± 5.2 | 28.5 ± 5.2 | 0.0 ± 0.0 | 21.2 ± 2.6 | 78.8 ± 2.6 |
| Perforant path, 50% kept | 77.4 ± 1.2 | 8.2 ± 1.1 | 14.5 ± 1.3 | 1.6 ± 0.5 | 75.5 ± 3.8 | 22.9 ± 4.1 | 0.0 ± 0.1 | 21.1 ± 2.6 | 78.9 ± 2.6 |
| Perforant path, 25% kept | 76.0 ± 2.4 | 0.0 ± 0.0 | 24.0 ± 2.4 | 99.3 ± 0.2 | 0.0 ± 0.0 | 0.7 ± 0.2 | 62.0 ± 3.4 | 0.0 ± 0.0 | 38.0 ± 3.4 |

p(old | lure) by level:

| Arm | C1 | C2 | C3 | C4 | C5 |
|---|---|---|---|---|---|
| Intact | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 75% kept | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 50% kept | 4.1 ± 1.0 | 2.2 ± 0.7 | 1.0 ± 0.5 | 0.5 ± 0.4 | 0.4 ± 0.4 |
| Perforant path, 25% kept | 99.3 ± 0.4 | 99.3 ± 0.2 | 99.3 ± 0.3 | 99.2 ± 0.4 | 99.4 ± 0.5 |

### Older adults' criteria, R3s (self-support of the starting state), other-drawer lures, bins L1 to L5

| Arm | old to repeat | similar to repeat | new to repeat | old to lure | similar to lure | new to lure | old to foil | similar to foil | new to foil |
|---|---|---|---|---|---|---|---|---|---|
| Young adults, 20 to 39 | 81.2 | 11.7 | 4.1 | 40.3 | 47.6 | 8.3 | 2.6 | 11.6 | 82.0 |
| Adults 60 to 74 | 82.2 | 7.6 | 5.3 | 54.6 | 23.6 | 12.3 | 4.8 | 12.3 | 73.4 |
| Intact | 77.0 ± 1.0 | 21.5 ± 1.1 | 1.5 ± 0.3 | 0.0 ± 0.0 | 30.3 ± 2.3 | 69.7 ± 2.3 | 0.0 ± 0.0 | 24.1 ± 1.5 | 75.9 ± 1.5 |
| Perforant path, 75% kept | 77.6 ± 1.1 | 19.0 ± 1.0 | 3.4 ± 0.7 | 0.0 ± 0.0 | 27.0 ± 1.7 | 73.0 ± 1.7 | 0.0 ± 0.0 | 22.3 ± 2.3 | 77.7 ± 2.3 |
| Perforant path, 50% kept | 77.5 ± 1.1 | 13.6 ± 1.2 | 8.9 ± 1.2 | 0.1 ± 0.1 | 26.2 ± 2.4 | 73.7 ± 2.4 | 0.0 ± 0.0 | 22.0 ± 2.4 | 78.0 ± 2.4 |
| Perforant path, 25% kept | 76.8 ± 2.0 | 0.0 ± 0.0 | 23.2 ± 2.0 | 45.2 ± 2.8 | 0.0 ± 0.0 | 54.8 ± 2.8 | 44.9 ± 3.4 | 0.0 ± 0.0 | 55.1 ± 3.4 |

p(old | lure) by level:

| Arm | L1 | L2 | L3 | L4 | L5 |
|---|---|---|---|---|---|
| Intact | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 75% kept | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 50% kept | 0.0 ± 0.0 | 0.1 ± 0.3 | 0.2 ± 0.4 | 0.1 ± 0.3 | 0.0 ± 0.0 |
| Perforant path, 25% kept | 34.4 ± 4.9 | 43.2 ± 6.9 | 47.4 ± 3.6 | 50.2 ± 3.6 | 49.4 ± 5.1 |

### Older adults' criteria, R3s (self-support of the starting state), closer lures, levels C1 to C5

| Arm | old to repeat | similar to repeat | new to repeat | old to lure | similar to lure | new to lure | old to foil | similar to foil | new to foil |
|---|---|---|---|---|---|---|---|---|---|
| Young adults, 20 to 39 | 81.2 | 11.7 | 4.1 | 40.3 | 47.6 | 8.3 | 2.6 | 11.6 | 82.0 |
| Adults 60 to 74 | 82.2 | 7.6 | 5.3 | 54.6 | 23.6 | 12.3 | 4.8 | 12.3 | 73.4 |
| Intact | 77.0 ± 1.0 | 21.5 ± 1.1 | 1.5 ± 0.3 | 0.0 ± 0.0 | 53.7 ± 4.1 | 46.3 ± 4.1 | 0.0 ± 0.0 | 24.1 ± 1.5 | 75.9 ± 1.5 |
| Perforant path, 75% kept | 77.6 ± 1.1 | 19.0 ± 1.0 | 3.4 ± 0.7 | 0.0 ± 0.0 | 57.4 ± 4.1 | 42.6 ± 4.1 | 0.0 ± 0.0 | 22.3 ± 2.3 | 77.7 ± 2.3 |
| Perforant path, 50% kept | 77.5 ± 1.1 | 13.6 ± 1.2 | 8.9 ± 1.2 | 0.1 ± 0.1 | 67.7 ± 3.7 | 32.2 ± 3.6 | 0.0 ± 0.0 | 22.0 ± 2.4 | 78.0 ± 2.4 |
| Perforant path, 25% kept | 76.8 ± 2.0 | 0.0 ± 0.0 | 23.2 ± 2.0 | 97.6 ± 0.4 | 0.0 ± 0.0 | 2.4 ± 0.4 | 44.9 ± 3.4 | 0.0 ± 0.0 | 55.1 ± 3.4 |

p(old | lure) by level:

| Arm | C1 | C2 | C3 | C4 | C5 |
|---|---|---|---|---|---|
| Intact | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 75% kept | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 50% kept | 0.4 ± 0.4 | 0.1 ± 0.2 | 0.1 ± 0.1 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| Perforant path, 25% kept | 98.1 ± 0.5 | 97.9 ± 0.4 | 97.3 ± 0.6 | 97.1 ± 0.8 | 97.5 ± 1.1 |
