# E8 sources

E8 compares the model with people on a recognition test built to separate memory for an exact item from memory for a similar one. This file lists the human findings E8 compares against, each checked on Crossref (title, authors, journal, volume, pages) and read in the publisher's or PubMed Central's full text where one was open. Quotes are exact. Where a source gives a finding without numbers, or where its numbers sit only in a figure, this file says so, and E8 uses no number from it.

## The task

The **Mnemonic Similarity Task** (MST) has two phases. A person first sees a series of everyday objects. Then, in a test phase, they see three kinds of pictures: **repeats** (the same picture again; some sources call them targets), **lures** (a similar picture of the same kind of object, never shown) and **foils** (new objects). For each one they answer old, similar or new.

Two scores come from the answers:

- **Lure discrimination index (LDI)** = p(similar | lure) − p(similar | foil). It measures how often a person tells a similar picture from the one they saw, corrected for how often they say similar to anything.
- **Recognition score (REC)** = p(old | repeat) − p(old | foil): hits minus false alarms, the usual measure of recognition memory.

Lures are sorted into five **lure bins** by how similar they are to the studied picture, from L1 (most similar) to L5 (least similar).

**Pattern separation** is the storing of similar experiences as distinct, non-overlapping patterns; **pattern completion** is the filling-in of a stored pattern from a partial or degraded cue. The MST's lure trials are designed to depend on pattern separation.

## Sources and what E8 takes from each

### Stark, Yassa, Lacy and Stark 2013

*A task to assess behavioral pattern separation (BPS) in humans: Data from healthy aging and mild cognitive impairment.* Neuropsychologia 51:2442-2449. doi 10.1016/j.neuropsychologia.2012.12.014. PMID 23313292, PMC3675184.

- Scores, Methods: the BPS score is "the difference between the rate of "Similar" responses given to the lure items minus "Similar" responses given to the foils". Results: the recognition score is "the percent of targets endorsed as "Old" minus the percent of foils endorsed as "Old"". The BPS score is the LDI under its later name.
- Young adults: "20–39 years of age (N = 26, mean age = 26.9, 10 Males)".
- Table 2, response rates in percent, mean (SD):

| Group | Old to repeat | Similar to repeat | New to repeat | Old to lure | Similar to lure | New to lure | Old to foil | Similar to foil | New to foil |
|---|---|---|---|---|---|---|---|---|---|
| 20 to 39 (N = 26) | 81.2 (8.8) | 11.7 (6.2) | 4.1 (3.8) | 40.3 (14.5) | 47.6 (15.4) | 8.3 (8.0) | 2.6 (2.8) | 11.6 (6.4) | 82.0 (8.4) |
| 40 to 59 (N = 20) | 81.6 (12.8) | 10.4 (6.6) | 4.3 (4.5) | 48.2 (16.0) | 39.2 (16.0) | 8.1 (7.2) | 2.9 (3.7) | 15.7 (11.7) | 76.1 (15.4) |
| 60 to 74 (N = 29) | 82.2 (9.1) | 7.6 (5.3) | 5.3 (3.9) | 54.6 (17.2) | 23.6 (14.9) | 12.3 (11.1) | 4.8 (4.9) | 12.3 (11.1) | 73.4 (18.8) |
| 75 to 89 (N = 18) | 80.0 (10.6) | 7.0 (6.9) | 9.2 (7.6) | 59.4 (14.8) | 22.5 (18.6) | 13.6 (9.9) | 6.6 (6.5) | 10.9 (11.7) | 76.6 (14.0) |
| Mild cognitive impairment (N = 11) | 75.9 (21.2) | 8.7 (12.4) | 16.0 (12.3) | 64.9 (18.5) | 12.5 (11.6) | 22.7 (13.8) | 15.9 (12.9) | 8.7 (10.8) | 75.4 (14.0) |

- The text gives no LDI or REC for the young group (Figure 2 plots them). Computed from Table 2 group means: young LDI = 47.6 − 11.6 = 36.0 points, REC = 81.2 − 2.6 = 78.6 points. Ages 60 to 74: LDI 11.3, REC 77.4. Mild cognitive impairment: LDI 3.8, REC 60.0. A difference of group means equals the mean of individual differences, so these match the scores the paper plots.
- Lure bins: lures run from "the more mnemonically similar lures in lure bin 1 (L1)" to "the least mnemonically similar lure items in lure bin 5 (L5)", set by "the probability of producing false alarms to the lures (calling them "old") for each lure item using a large, independent population of young participants". The paper gives no rates per bin for young adults; it notes that "the normative procedure used will virtually ensure a linear trend in younger individuals".

**E8 uses**: the young adults' p(old | repeat) = 0.812 and p(new | foil) = 0.820 to set the model's two decision thresholds; their LDI (0.360), REC (0.786), p(old | lure) (0.403) and the 60 to 74 group's values as comparisons.

### Stark, Kirwan and Stark 2019

*Mnemonic Similarity Task: A Tool for Assessing Hippocampal Integrity.* Trends in Cognitive Sciences 23:938-951. doi 10.1016/j.tics.2019.08.003. PMID 31597601, PMC6991464.

- Section "MST: Design and Measures": LDI is "the probability of giving a "Similar" response to the lure items minus the probability of giving" a "Similar" response to the foils, "to account for any bias the participant may have in using the "Similar" response overall". The same section's main text, after Box 2, defines "a traditional "corrected recognition memory" (REC) score" as hits minus false alarms.
- Lure bins: "items in Lure Bin 1 are highly similar and elicit false alarms quite often" while "those in Lure Bin 5 are far more dissimilar and have very few false alarms".
- Lesions: "lure discrimination performance is impaired in amnesic patients with damage limited to the hippocampus" while recognition is intact; "a rare patient with damage limited to the dentate gyrus showed selective impairments on discrimination of similar lures" (citing Baker and colleagues 2016); "Similar results have been reported for patients with CA1 specific lesions" (citing Hanert and colleagues 2019).
- Ageing: "the integrity of the perforant path, connecting the EC to the hippocampus, deteriorates with age", and "aging leads to reduced input to the DG via the perforant path".
- The review states no numbers per lure bin. Figure 2F plots 1 − p(old) per bin for older adults (unimpaired and impaired) and people with mild cognitive impairment, with no curve for young adults.

**E8 uses**: the definitions, the direction of the lure-bin effect (more similar lures, more false alarms, lower discrimination), and the direction of each lesion finding.

### Yassa and Stark 2011

*Pattern separation in the hippocampus.* Trends in Neurosciences 34:515-525. doi 10.1016/j.tins.2011.06.006. PMID 21788086, PMC3183227.

- Introduction: pattern separation is the process "whereby similar representations are stored in a distinct, non-overlapping (orthogonalized) fashion"; pattern completion is "the process by which incomplete or degraded representations are filled-in based on previously stored representations".
- Human fMRI studies: "Only the DG/CA3 region showed activity consistent with strong pattern separation", and "CA3 and DG cannot be dissociated in fMRI studies" (Figure 4 legend).
- Neurocognitive ageing: "perforant path integrity was diminished with age in humans".
- No behavioural numbers for young adults.

**E8 uses**: the definitions and the link between lure discrimination and DG and CA3.

### Baker and colleagues 2016

Baker, Vieweg, Gao, Gilboa, Wolbers, Black and Rosenbaum. *The Human Dentate Gyrus Plays a Necessary Role in Discriminating New Memories.* Current Biology 26:2629-2634. doi 10.1016/j.cub.2016.07.081. PMID 27666968.

- Summary (Europe PMC record): "Here, we report the rare case of BL, a 54-year-old man with bilateral ischemic lesions to the hippocampus [24] primarily affecting the dentate gyrus."
- Results and Discussion (full text, Cell Press open archive), against 20 controls: BL was "similar to that of controls in correctly identifying targets (t(19) = -0.24, p = 0.82)" and foils (t(19) = -0.98, p = 0.34), "performed significantly worse than controls in identifying lures (t(19) = -2.50, p = 0.02)", and "BL's LDI score was close to zero" (t = -2.18; p = 0.04). His response rates appear only in Figure 1, so none is used.
- Experimental Procedures: his lesions "are limited to the dentate gyrus and a portion of CA3".

**E8 uses**: the direction only. Removing DG should lower LDI and leave REC near normal.

### Kirwan and colleagues 2012

Kirwan, Hartshorn, Stark, Goodrich-Hunsaker, Hopkins and Stark. *Pattern separation deficits following damage to the hippocampus.* Neuropsychologia 50:2408-2414. doi 10.1016/j.neuropsychologia.2012.06.011. PMID 22732491, PMC3411917.

- Patients (Section 2.1; Table 1 gives their age, education and test scores): three people with bilateral hippocampal damage after anoxia or brain injury, with hippocampal volume reduced by 33%, 44% and 42%; 11 age-matched controls.
- Baseline old/new test (Figure 2A, Section 3): corrected recognition 0.81 (SD 0.08) for patients, 0.87 (0.09) for controls, t(12) = 0.83, p = 0.42.
- Old/similar/new test (Figure 2B, Section 3): pattern separation index 0.10 (0.07) for patients, 0.37 (0.15) for controls, t(12) = 3.18, p < 0.01.
- Table 2, the same test, both stimulus types: old to repeats 0.62 (patients) and 0.77 (controls); old to lures 0.38 and 0.37; similar to lures 0.38 and 0.49; old to foils 0.22 and 0.21. From these, REC on this test is 0.40 for patients and 0.56 for controls.
- Results (Section 3): "contrary to our second prediction, patients did not respond "old" to similar stimuli more often than control participants" (corrected "old" scores did not differ), and patients gave more "new" responses to lures than controls (t(12) = 4.75, p < 0.001).

**E8 uses**: patients' LDI 0.10 against controls' 0.37, recognition near normal on the old/new test, and p(old | lure) unchanged, as the comparison for removing the whole hippocampus.

### Yassa, Muftuler and Stark 2010

*Ultrahigh-resolution microstructural diffusion tensor imaging reveals perforant path degradation in aged humans in vivo.* PNAS 107:12687-12691. doi 10.1073/pnas.1002113107. PMID 20616040, PMC2906542.

- Abstract: "We report direct evidence of age-related PP degradation in humans in vivo. We find no evidence of such loss in a control pathway, the alveus". "The extent of PP degradation correlated with performance on a word-list learning task sensitive to hippocampal deficits."
- Results (full text): the age difference in perforant-path integrity is reported as "a significant group difference in the area under the curve (AUC)" (t = 2.53, P = 0.01; Fig. 3A). No size of the loss in humans is stated, so none is used.

### Yassa, Mattfeld, Stark and Stark 2011

*Age-related memory deficits linked to circuit-specific disruptions in the hippocampus.* PNAS 108:8873-8878. doi 10.1073/pnas.1101567108. PMID 21555581, PMC3102362.

- Five lure bins, "L1 being the most similar lures and L5 being the least similar", from "similarity ratings derived from a large normative study conducted in our laboratory".
- Figure 4C: "a positive relationship between perforant path integrity in older adults and their separation bias", r = 0.73, P < 0.05, n = 11.
- Behavioural rates appear only in Figure S1.

**E8 uses**: the direction. A thinner perforant path goes with worse lure discrimination in older adults. The model's thinning levels are not taken from any measured loss, since no source states one in humans.

### Hanert, Pedersen and Bartsch 2019

*Transient hippocampal CA1 lesions in humans impair pattern separation performance.* Hippocampus 29:736-747. doi 10.1002/hipo.23073. PMID 30706576.

- Abstract: "we examined 14 patients with an acute transient global amnesia (TGA), a rare self-limiting dysfunction of the hippocampal system showing specific lesions to CA1." "Patients in the acute phase showed a profound deficit in pattern separation (p < .05) as well as recognition memory (p < .001) that recovered during follow-up."
- The full text was not readable here, so no rates are used.

**E8 uses**: the direction. A CA1 lesion lowers both LDI and REC.

## Not found

- **LDI by lure bin for young adults.** No source gives young adults' rates per bin as numbers. Stark and colleagues 2013 (Figure 3C) plot 1 − p(old) per bin for each healthy age group; Stark and colleagues 2019 (Figure 2F) plot 1 − p(old) per bin for older adults and people with mild cognitive impairment only; Yassa and colleagues 2011 (Figure S1) plot older adults' overall rates, with no bins; Lacy and colleagues 2011 (Learning & Memory 18:15-18, doi 10.1101/lm.1971111, Supplemental Figure 1B) plot 1 − p(old) for each lure pair, the ranking that defines the bins. E8's figures therefore carry no human curve, and the comparison is the direction: discrimination rises from L1 to L5.
- **Patient BL's rates** appear only in Baker and colleagues' Figure 1. **The size of perforant-path loss with age** in humans is not stated by Yassa and colleagues 2010. **Rates in transient global amnesia** (Hanert and colleagues 2019): full text not readable here.
