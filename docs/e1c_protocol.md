# E1c protocol

E1c asks how close CA3 comes to an ideal nearest-memory lookup when it has no list of memories, as the number of stored memories grows and as cues lose more of their cells, and whether the pattern CA3 settles on helps CA1 rebuild the drawing. This file lists every choice E1c makes. The choices went into code and tests before the reported runs and stay fixed, except two that items 9 and 26 mark as added after a first pass.

## Terms

- **CA3** is the hippocampal field whose cells connect back to each other. In this model it stores each memory as a pattern of k active cells out of n, and recalls by settling: it updates its cells from their recurrent input until the state stops changing.
- **DG**, the dentate gyrus, gives each drawing a new sparse pattern. CA3 stores DG's patterns.
- **CA1** learns to turn a stored CA3 pattern back into the drawing. AHA calls it PM.
- **PR** is the direct path from entorhinal cortex into CA3. It learns to turn a drawing's vision code into its stored pattern, and its output is CA3's cue in the full model.
- **Load** is the number of patterns stored at once.
- **Ideal lookup** compares a cue with a list of every stored pattern and picks the one sharing the most active cells. For a cue with random damage this is the best possible decoder, so it is the ceiling CA3 is measured against.
- **k-winners-take-all (kWTA)** keeps the k most driven cells on and turns the rest off. It stands in for feedback inhibition, as in E1.

## Two kinds of test

1. **CA3 on its own** (`trisynapsnet/eval/ca3space.py`). No vision network and no PR. CA3 stores N patterns, receives damaged copies of some of them as cues, settles, and the final state is scored.
2. **End to end** (`trisynapsnet/eval/endtoend.py`). The full model studies N drawings in one exposure and recalls each from an occluded or noisy copy, as in E1b's instance task.

## Choices for CA3 on its own

### Patterns

1. **Random patterns.** Each pattern has exactly k of n cells on, chosen uniformly. A seed draws one pool of patterns as large as the biggest load, and load N stores the first N, so each smaller load is the start of each larger one.
2. **Drawing patterns.** DG's patterns for one drawing each of N different characters. Each character's drawing comes from one of its 20 drawers, drawn at random once with draw seed 0, and stays the same for every model seed. Each model seed shuffles the characters, and load N stores DG's patterns for the first N in that order.
3. **DG as it runs in the model.** Random weights with 25% knocked out, top k, and refractory inhibition that decays by 0.95 per drawing and starts fresh for each stored set. DG's weights come from the cell count and the seed. The vision network is aha4's frozen checkpoint, and its output is not normalised, as in E1 and E1b.
4. **Characters available.** The evaluation alphabets hold 659 characters and the background alphabets 964. Loads above that use every character: 659 for the reported runs, 964 for the background check. No load uses two drawings of one character.
5. **Which alphabets.** The evaluation alphabets give the reported numbers. The background alphabets run as a check with 5 seeds. No setting was chosen from either set.
6. **Duplicates.** Two drawings could get the same DG pattern. Each result file counts duplicates per load and seed.

### Sizes and loads

7. **Sizes.** n = 225 cells with k = 10 on (AHA's size), 1,000 with 44 on, and 4,000 with 178 on. All three keep AHA's 4.4% of cells on.
8. **Loads.** 20, 50, 100, 200, 500 and 1,000 at every size.
9. **Added loads.** Random patterns also run at loads near where each rule fails: 150 and 300 at 225 cells; 700, 1,500, 2,000, 5,000 and 10,000 at 1,000 cells; 1,500, 2,000, 3,000, 5,000 and 10,000 at 4,000 cells. They were added after a first pass over the planned loads showed every rule failing between two planned loads, too far apart to compare sizes. Tables label them as added. Drawings use the planned loads only.
10. **Pseudo-inverse at loads of n or more.** Once the stored patterns span every direction, the pseudo-inverse weight matrix is the identity: every state is a fixed point and CA3 returns the cue unchanged. These loads still run. A clean cue then counts as exact recall without any completion.

### Cues and damage

11. **Which patterns are cued.** Every stored pattern up to a load of 200. Above 200, a random sample of 200 without repeats. The sample is the same for every damage condition and every rule.
12. **Damage counts.** Removing a share r of the k active cells switches off floor(r × k + 0.5) of them. Adding stray cells as a share s of k switches on floor(s × k + 0.5) cells that the pattern has off. Each cue gets its own random draw.
13. **Conditions.** Removed share 0, 0.2, 0.4, 0.6, 0.8 with no strays; stray share 0.25, 0.5, 1.0 with nothing removed; and removed 0.4 with stray 0.5 together.
14. **Pairing.** Patterns, cue sample and damage come from the source, split, size, load, seed and condition, never from the rule, so every rule sees identical cues.

### Rules and settling

15. **Local rules** (covariance and clipped binary synapses, from E1). CA3 stores the 0/1 patterns. Settling starts from the cue as given: the first state is kWTA(W × cue), and each later state is kWTA(W × state). E1 and E1b started from the cue's k most active cells instead; that stays the default elsewhere. Cue weight 0, as in E1's headline runs. Up to 70 synchronous steps, stopping when the state stops changing.
16. **Pseudo-inverse** (AHA's rule). CA3 stores each pattern as −1/+1 and settles with AHA's asynchronous tanh updates: gain 2.7, 70 steps, 20 cells per step per 225 cells (89 at 1,000 cells, 356 at 4,000). The cue reaches CA3 as the −1/+1 version of the damaged pattern: removed cells are −1 and stray cells are +1.
17. **How that cue was chosen.** AHA's own cue conditioning (its Appendix A.2, with gain equal to k so that a clean cue maps exactly to its stored pattern) was compared with the plain −1/+1 version on random patterns only: 3 seeds outside the reported ones, 20 and 100 patterns, 225 and 1,000 cells. With AHA's conditioning, exact recall was 0% whenever any cell was removed, at every load and size tried. With the plain version it was 93% to 99% with 20% or 40% removed at 20 patterns. The plain version is used.
18. **Cells on.** A cell counts as on when its state is above zero, for every rule.

### Measures, per size, rule, load, condition and seed

19. **Capacity.** Two summaries per rule and size: the largest load with exact recall at or above 95% at every tested load up to it, and the load where exact recall falls to 50%, interpolated on a log scale between the two tested loads around it. For the pseudo-inverse, loads of n or more are left out.
20. **Exact recall.** The final state has exactly the right pattern's cells on and no others. No list is consulted.
21. **Overlap.** Cells on in both the state and the right pattern, over k, for the raw cue and for the final state.
22. **Stray share.** Cells on outside the right pattern, over k, for the raw cue and for the final state.
23. **Ideal lookup.** The stored pattern sharing the most active cells with the raw cue. Every stored pattern has k cells on, so this ranks the same as cosine similarity. When several patterns tie, the cue scores 1 over the number tied if the right one is among them, the expected score of a random tie-break. The same lookup also runs on the final state.
24. **Settled on a stored pattern.** The final state equals some stored pattern, right or wrong.
25. **Settling steps and fixed points.** For the local rules: the number of steps that changed the state, and whether some step left it unchanged within 70. For the pseudo-inverse: the last step at which any cell changed sign, and whether one more update of every cell at once would flip no sign.
26. **CA1 error.** Drawings at 225 cells only, at every load. CA1 is trained on the stored patterns as AHA trains it: 100 hidden units, Adam at learning rate 0.01, L2 penalty 4 × 10⁻⁴, 60 full-batch steps, mapping each stored pattern (−1/+1 for the pseudo-inverse, 0/1 for the local rules) to its drawing. Its starting weights depend on load and seed, not on the rule. Error is the mean squared error against the clean drawing, from four inputs: the raw cue in the rule's code, the settled state, the pattern the ideal lookup picks (the first of any tie), and the right stored pattern itself, which gives CA1's floor. A fifth number, added after a first pass showed CA1's floor rising with load, the error of the mean stored drawing, is the best any reconstruction can do with no memory at all.
27. **Seeds.** 10 at 225 and 1,000 cells, 5 at 4,000 cells and for the background check.

## Choices for the end-to-end runs

28. **Model.** AHA's settings as in E1b: 225 DG and CA3 cells with 10 on, aha4's vision network, 60 study steps for PR and CA1, normalised minimum-MSE matching, Apple's MPS backend.
29. **Loads.** 20, 100 and 200 drawings studied at once.
30. **Runs.** Each seed studies about 400 drawings in runs of N: 20 runs at load 20, 4 at load 100, 2 at load 200. Each run draws N characters without repeats from all 659 evaluation characters, one drawing each, the same drawing per character as in the CA3 harness. Unlike Lake's runs, a run mixes alphabets.
31. **Test drawings.** The studied drawings again, in a shuffled order, corrupted with E1b's occlusion or noise code at 0, 0.3, 0.5 and 0.7, corruption seed 0, run number seed × 1,000 + run.
32. **Model seeds.** seed × 1,000 + run, as in E1b. Each run studies once and recalls every level.
33. **Settling.** The default start, PR's 10 most active cells, as in E1 and E1b.
34. **No-settling control.** PR's 10 most active cells passed straight on, through the same CA1. For the pseudo-inverse it is the −1/+1 version of those cells, through that rule's CA1.
35. **Settling from PR as given.** For the local rules only, a third arm settles from the whole PR output with the partial start of choice 15.
36. **Matching.** Both directions: test-to-study, where each test state picks the nearest studied state, the way a cue retrieves a memory; and study-to-test, AHA's direction.
37. **CA3 measures.** Exact recall, overlap of PR's 10 most active cells and of the settled state with the right stored pattern, and the ideal lookup, as defined above.
38. **Recall-loss.** CA1's error against the clean study drawing, with settling and without.
39. **Seeds.** 5.
