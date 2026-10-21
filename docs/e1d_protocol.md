# E1d protocol

E1d asks whether CA3's capacity per cell stops falling as the network grows once DG and CA3 codes are as sparse as measured. This file lists every choice E1d makes. The choices went into code and tests before the reported runs, except items 14a and 14b, which changed during them.

## Terms

- **DG**, the dentate gyrus, gives each drawing a new sparse pattern: k active cells out of n.
- **CA3** is the hippocampal field whose cells connect back to each other. It stores DG's patterns and recalls by settling: it updates its cells from their recurrent input until the state stops changing.
- **Share active** is k over n, the fraction of DG and CA3 cells on in each pattern. AHA, the model this project starts from, uses 10 of 225 cells, 4.4%.
- **Load** is the number of patterns stored at once.
- **Exact recall** means CA3's final state is exactly the right stored pattern.
- **50% load** is the load at which mean exact recall falls through 50%. **Load per cell** is the 50% load over n.
- **Ideal lookup** compares a cue with a list of every stored pattern and picks the one sharing the most active cells.
- **k-winners-take-all (kWTA)** keeps the k most driven cells on and turns the rest off, standing in for feedback inhibition.
- **CV**, the coefficient of variation, is a standard deviation over a mean.

## Why the share of active cells

E1c ran CA3 at 4.4% active at 225, 1,000 and 4,000 cells. The load per cell at 50% exact recall fell with size: from 1.12 to 0.60 for the covariance rule and from 1.25 to 0.31 for clipped binary synapses, on random patterns. Theory for sparse associative memories (Willshaw and colleagues, 1969; Tsodyks and Feigel'man, 1988) expects capacity per cell to fall at a fixed share active, and to hold or grow when k grows about with the logarithm of n. Rat DG runs at about 2% of granule cells active (Ramirez-Amaya and colleagues, 2013). No human measurement exists.

## What changes and what stays

1. **Only the share active changes,** in DG and CA3 together. Everything else is E1c's: patterns, damage conditions, cue sampling, rules, settling, scores and seeds (`docs/e1c_protocol.md`, items 1 to 25).
2. **Shares.** 4.4% (k = 10 of 225, AHA), 2% (rat DG), 1%, and log-scaled: k = round(c × log2 n) with c = 20 / log2(1,000) = 2.0069, so that k = 20, 2%, at 1,000 cells. Every share rounds half up, as E1c's damage counts do.
3. **Smallest k.** Any share giving fewer than 3 active cells is raised to 3. Only 1% of 225 cells (2.25) is raised.
4. **Active cells used:**

   | Share | 225 cells | 1,000 cells | 4,000 cells | 16,000 cells |
   |---|---|---|---|---|
   | 4.4% | 10 | 44 | 178 | 711 |
   | 2% | 5 (2.2%) | 20 | 80 | 320 |
   | 1% | 3 (1.3%, raised) | 10 | 40 | 160 |
   | log-scaled | 16 (7.1%) | 20 | 24 | 28 |

   At 1,000 cells the 2% and log-scaled codes are the same and run once.
5. **Small k.** Tests check that kWTA keeps exactly k cells with ties, that DG gives exactly k cells with its 25% knockout and refractory inhibition, that damage counts round as stated, and that every CA3 rule recalls a light load exactly at k = 3 and 5 (`tests/test_small_k.py`). At k = 3, damage shares quantise: removing 20% or 40% removes 1 cell, removing 60% or 80% removes 2; stray shares 0.25, 0.5 and 1.0 add 1, 2 and 3 cells.

## CA3 on its own

6. **Sizes.** 225, 1,000 and 4,000 cells for random patterns and drawings; 16,000 cells for random patterns only. DG at 16,000 cells would need a 20,449 by 16,000 weight matrix, and random patterns answer the size question on their own.
7. **Patterns.** Random patterns with exactly k of n cells on, drawn from the same random stream as E1c, so the 4.4% runs store E1c's patterns. DG's patterns for one drawing each of N characters, as in E1c, from the same frozen vision codes.
8. **Characters available.** 659 in the evaluation alphabets and 964 in the background alphabets. Drawings run every grid load below that number, then that number.
9. **Load grid.** 20, 30, 50, 70, then 1, 1.5, 2, 3, 5 and 7 times each power of ten up to 1,000,000. Neighbouring loads differ by at most a factor of 5/3. Every load E1c ran is on the grid.
10. **Stop rule, random patterns.** The first seed climbs the grid and stops after the first load of at least 100 where exact recall falls below 5%: from clean cues for the local rules, and from cues missing 40% of their cells for the pseudo-inverse. Every other seed runs the same loads. Loads 20 and 100 always run.
11. **Pseudo-inverse loads stay below n.** At n or more patterns its weights are the identity matrix and every state is a fixed point (E1c item 10), so those loads say nothing about recall and cost the most to compute.
12. **Storage at scale.** Patterns are kept as lists of active cells. The local rules store a running count of how often each pair of cells fired together, and each load adds only its new patterns. Clipped binary weights from these counts equal E1c's exactly. Covariance weights are computed in float64 from the counts, where E1c summed them in float32; they differ by about 10⁻⁷. Cells whose counts match then tie exactly in kWTA, where E1c's rounding broke the tie. Past capacity this changes the outcome for up to 3% of cues; below capacity nothing changes (`tests/test_sparsecodes.py`).
13. **Ideal lookup at scale.** Compared a chunk of stored patterns at a time, with the same tie rule as E1c.
14. **Seeds.** Random patterns: 10 at 225 and 1,000 cells, 5 at 4,000 and 16,000 cells. Evaluation drawings: 10 at 225 and 1,000 cells, 5 at 4,000. Background drawings: 5 at every size, as the check before the evaluation alphabets.
14a. **Changed during the run: the pseudo-inverse at 16,000 cells.** Each load needs the pseudo-inverse of a load-by-16,000 matrix in float64, up to 10,000 by 16,000, and two of these runs at once, beside other jobs on the machine, filled its memory and swap. They were stopped and are not rerun. What finished stays in the results and is labelled: 5 seeds at 4.4%, 4 at 2%, 2 at 1%, none for the log-scaled code. The driver now runs the pseudo-inverse up to 4,000 cells only.
14b. **Changed during the run: seeds for the local rules at 16,000 cells.** 5 seeds at 4.4% and 2%. The 1% and log-scaled runs went on after the stop, one process at a time, with 3 seeds to bound run time (about 20 minutes per seed for the log-scaled code). The first seed of the log-scaled runs comes from a timing pilot made with the same code and seed.
15. **Not measured here.** CA1's reconstruction error, which E1c covered at 4.4% and which depends on CA1's own capacity more than CA3's.

## Measures

16. **50% load and load per cell,** for each share, size, rule and source, interpolated on a log scale between the two tested loads around 50%. From clean cues for the local rules and from cues missing 40% of their cells for the pseudo-inverse, whose clean cues stay exact up to n. The local rules are also reported at 40% removed.
17. **Completion** at loads 20 and 100: exact recall and the share of the right pattern's cells on, in the raw cue and in the settled state, for each removed share.
18. **DG's unevenness of cell use.** For each load, the CV of how many stored patterns each cell is in. For drawings, the same CV for random patterns with the same n, k and load sits beside it. Reported at the highest load.
19. **Settling steps and fixed points,** as E1c item 25.
20. **Run time** per seed, from each result file.

## End to end

21. **Setting.** 225 cells with 5 active, 2% rounded half up (2.2%), fixed before any end-to-end run. This size keeps every other part as in E1 and E1b, so the 4.4% numbers in `results/bio_e1.md` and `results/e1b.md` compare directly.
22. **Options.** Covariance, clipped binary synapses, and no settling (covariance storage with 0 settling steps, which passes PR's 5 most active cells straight on).
23. **Classification.** E1's protocol: Lake's 20 runs, 10 seeds, normalised minimum-MSE matching, scored study-to-test (AHA's direction) and test-to-study (E1b's).
24. **Instance task.** E1b's protocol: occlusion and noise at 0, 0.3 and 0.5, 10 seeds, corruption seed 0, both matching directions.
25. **Check first.** The same runs on background-alphabet validation runs, 5 seeds. Lake's runs and the evaluation-alphabet instance runs are scored once, after.
26. **Comparison.** Against the 4.4% files from E1 and E1b with the same option, task, corruption and matching direction.

## Predictions

Written before any E1d run:

1. Capacity per cell rises as codes get sparser, at every size.
2. With log-scaled codes, capacity per cell holds or grows with size, instead of falling as in E1c.
3. Clipped binary synapses gain the most from sparser codes; at the sparsest codes they beat the covariance rule.
4. DG's codes for drawings stay more uneven than random patterns at every sparsity, so drawings stay below random patterns in capacity.
5. One-shot classification and instance accuracy change by less than 3 points, since PR, not CA3, sets them.
