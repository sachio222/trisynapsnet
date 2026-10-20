# E1b protocol

E1b scores every CA3 option on corrupted test drawings, following AHA's robustness tests (Kowadlo, Ahmed and Rawlinson, arXiv 1909.10340v5, Sections 3.2 and 3.3, Figures 5 and 6). This file quotes what the paper says and lists each choice made where it says nothing. The choices went into code and tests before the first E1b run and stay fixed.

## What the paper specifies

| Topic | Paper text |
|---|---|
| Instance task | "the train character exemplar must be matched with the exact same exemplar amongst a set of 20 distractor exemplars of the same character class." |
| Instance runs | "In each run, the character class and exemplars are selected by randomly sampling without repeats from the 'evaluation' set." |
| Presentation | "instead of presenting 1 test character at a time, all 20 are presented simultaneously." |
| Occlusion | "Occlusion is achieved with randomly placed circles, completely contained within the image." Figure 5: "Occlusion diameter as a fraction of image side length". |
| Noise | "Noise is introduced by replacing a proportion of the pixels with a random intensity value drawn from a uniform distribution." Figure 5: "noise is expressed as a fraction of image area." |
| Levels | "from none, to almost complete corruption, in 10 increments. The highest level is capped at just below 98% corruption". |
| Seeds | "Every test is repeated with 10 random seeds." |
| Recall-loss | "the MSE difference between the original train image and a recalled image in grounded, observational form." |
| Both tasks | Figures 5a and 5b show one-shot classification under occlusion and noise; 5c and 5d show instance-classification. |

## Choices where the paper is silent

1. **Levels.** 0, 0.1, 0.2, ..., 0.9, then 0.98: none plus 10 steps, with the last capped just below 98%. The paper's appendix figures show 0.6 as "high" and 0.9 as "extreme", which fit this spacing. Every level runs, so no grid was cut.
2. **One circle per drawing.** Figure 7b's caption reads "With occlusion (circle, diameter=0.3)".
3. **Occluder colour.** The circle is painted with paper colour, intensity 0 once ink is 1, so it removes strokes. The paper says occlusion "increases the likelihood of suddenly removing important topological features".
4. **Circle placement.** The centre is uniform over every position that keeps the whole circle inside the frame. A pixel is covered when its centre lies inside the circle. At diameter 0.98 one circle covers about 75% of the image, the most any single contained circle can.
5. **Noise count.** Exactly round(level x 2,704) pixels per drawing are replaced, picked without repeats, each with an intensity uniform in [0, 1).
6. **Resolution.** Corruption applies to the 52 x 52 drawing the model sees, after resizing, inverting and centring. The paper's model input is 52 x 52 (Figure 13).
7. **What gets corrupted.** Test drawings only. Study drawings stay clean, and recall-loss compares with the clean study drawing.
8. **Instance runs.** 20 runs, matching Lake's 20. Each run draws one character, without repeats across runs, from all 659 characters of the 20 evaluation alphabets. Omniglot has exactly 20 drawings of each character, one per drawer, so the study set is all 20 in a shuffled drawer order and the test set is the same 20 drawings in another shuffled order. The paper's "20 distractor exemplars" reads here as the 20 candidates, one of them the target.
9. **Run draw.** The instance runs come from run seed 0 and stay the same for every model seed, as Lake's runs do.
10. **Corruption draw.** Each drawing's circle or noisy pixels come from corruption seed 0, the run number, the kind and the level, and stay the same for every model seed and every CA3 option. Every CA3 option therefore sees identical drawings, so differences between options pair by seed.
11. **One study, many levels.** Each (seed, run) studies the clean drawings once, then recalls every corruption level. Recall never learns, and bipolar settling's random generator is reset to its post-study state before each level, so a level scores exactly as it would alone.
12. **Matching.** As in E1: minimum mean squared error, study-to-test, every vector L2-normalised first.
13. **Model.** As in E1: shipped VC checkpoint from aha4, DG and CA3 at 225 cells with 10 on, 70 settling steps at most.
14. **No-settling control.** Covariance storage with zero settling steps: CA3 passes on the 10 most active PR cells. E1 showed this control gives identical scores under either local rule, so it runs once.
15. **Background-alphabet instance runs.** The same construction from the 30 background alphabets, 5 seeds. E1b chooses no setting, so these runs serve as a check that the evaluation-set pattern repeats on other characters.
