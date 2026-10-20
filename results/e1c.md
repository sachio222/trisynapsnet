# E1c: CA3 recall without a list of memories

A nearest-memory lookup compares a cue with a list of every stored memory and picks
the one sharing the most active cells. For a cue with random damage it is the best
decoder possible, so it is the ceiling here. CA3 holds no list: it settles from the
cue through its recurrent weights. These tables measure how close settling comes to
that ceiling as the number of stored memories (the load) grows, and whether the
settled pattern lets CA1 rebuild the drawing better than the raw cue does.

Terms used below:

- **Exact recall:** CA3's final state has exactly the right stored pattern's cells on
  and no others. No list is consulted.
- **Overlap:** the share of the right pattern's k active cells that are on, for the raw
  cue or for the final state. **Stray:** cells on outside the right pattern, over k.
- **Ideal lookup:** the stored pattern sharing the most cells with the raw cue is the
  right one. Ties count as 1 over the number tied.
- **Clean cue:** the stored pattern itself. **40% removed:** 40% of its k cells
  switched off at random.
- **Rules:** pseudo-inverse is AHA's rule, run on −1/+1 patterns with AHA's tanh
  settling. Covariance and clipped binary synapses are the local rules from E1, with
  k-winners-take-all settling that starts from the cue as given.
- **CA1 error:** mean squared error between CA1's reconstruction and the clean drawing.

Every choice is listed in `docs/e1c_protocol.md`. Made by `scripts/make_e1c_table.py`.

## Random patterns: exact recall against load

Percent of cues, mean over seeds (10 seeds at 225 cells, 10 seeds at 1,000 cells, 5 seeds at 4,000 cells).

| cells, on | load | Pseudo-inverse clean | Covariance clean | Clipped binary clean | Pseudo-inverse 40% removed | Covariance 40% removed | Clipped binary 40% removed | Ideal lookup 40% removed |
|---|---|---|---|---|---|---|---|---|
| 225, 10 | 20 | 100.0 | 100.0 | 100.0 | 98.0 | 100.0 | 100.0 | 100.0 |
| 225, 10 | 50 | 100.0 | 99.8 | 100.0 | 98.0 | 99.8 | 100.0 | 100.0 |
| 225, 10 | 100 | 100.0 | 99.2 | 99.9 | 66.6 | 95.1 | 99.0 | 100.0 |
| 225, 10 | 150 (added) | 100.0 | 92.1 | 97.9 | 0.2 | 74.3 | 85.7 | 100.0 |
| 225, 10 | 200 | 100.0 | 74.8 | 91.2 | 0.0 | 40.8 | 41.4 | 100.0 |
| 225, 10 | 300 (added) | 100.0 | 31.4 | 42.2 | 0.0 | 6.2 | 0.3 | 100.0 |
| 225, 10 | 500 | 100.0 | 3.5 | 0.0 | 0.0 | 0.2 | 0.0 | 100.0 |
| 225, 10 | 1,000 | 100.0 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 |
| 1,000, 44 | 20 | 100.0 | 100.0 | 100.0 | 98.5 | 100.0 | 100.0 | 100.0 |
| 1,000, 44 | 50 | 100.0 | 100.0 | 100.0 | 97.2 | 100.0 | 100.0 | 100.0 |
| 1,000, 44 | 100 | 100.0 | 100.0 | 100.0 | 97.5 | 100.0 | 100.0 | 100.0 |
| 1,000, 44 | 200 | 100.0 | 100.0 | 100.0 | 96.7 | 100.0 | 100.0 | 100.0 |
| 1,000, 44 | 500 | 100.0 | 96.7 | 99.7 | 9.6 | 94.4 | 99.4 | 100.0 |
| 1,000, 44 | 700 (added) | 100.0 | 69.8 | 70.7 | 0.0 | 57.5 | 11.8 | 100.0 |
| 1,000, 44 | 1,000 | 100.0 | 14.1 | 0.0 | 0.0 | 5.5 | 0.0 | 100.0 |
| 1,000, 44 | 1,500 (added) | 100.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 |
| 1,000, 44 | 2,000 (added) | 100.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 |
| 1,000, 44 | 5,000 (added) | 100.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 |
| 1,000, 44 | 10,000 (added) | 100.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 |
| 4,000, 178 | 20 | 100.0 | 100.0 | 100.0 | 87.0 | 100.0 | 100.0 | 100.0 |
| 4,000, 178 | 50 | 100.0 | 100.0 | 100.0 | 92.0 | 100.0 | 100.0 | 100.0 |
| 4,000, 178 | 100 | 100.0 | 100.0 | 100.0 | 89.0 | 100.0 | 100.0 | 100.0 |
| 4,000, 178 | 200 | 100.0 | 100.0 | 100.0 | 87.2 | 100.0 | 100.0 | 100.0 |
| 4,000, 178 | 500 | 100.0 | 100.0 | 100.0 | 88.8 | 100.0 | 100.0 | 100.0 |
| 4,000, 178 | 1,000 | 100.0 | 100.0 | 99.0 | 84.5 | 100.0 | 97.5 | 100.0 |
| 4,000, 178 | 1,500 (added) | 100.0 | 98.9 | 0.0 | 54.9 | 98.2 | 0.0 | 100.0 |
| 4,000, 178 | 2,000 (added) | 100.0 | 82.3 | 0.0 | 0.1 | 78.7 | 0.0 | 100.0 |
| 4,000, 178 | 3,000 (added) | 100.0 | 8.0 | 0.0 | 0.0 | 3.9 | 0.0 | 100.0 |
| 4,000, 178 | 5,000 (added) | 100.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 |
| 4,000, 178 | 10,000 (added) | 100.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 |

- For the pseudo-inverse, loads of n or more (here 225 at 225 cells, 1,000 at 1,000 cells, 4,000 at 4,000 cells) make its weights the identity matrix: every state is a fixed point, so a clean cue counts as exact recall without any completion. Capacity below leaves those loads out.

Largest load at which exact recall stays at or above 95% at every tested
load up to it, and that load per cell:

| cells, on | Pseudo-inverse clean | Pseudo-inverse 40% removed | Covariance clean | Covariance 40% removed | Clipped binary clean | Clipped binary 40% removed |
|---|---|---|---|---|---|---|
| 225, 10 | 200 or more (0.89 per cell) | 50 (0.22 per cell) | 100 (0.44 per cell) | 100 (0.44 per cell) | 150 (0.67 per cell) | 100 (0.44 per cell) |
| 1,000, 44 | 700 or more (0.70 per cell) | 200 (0.20 per cell) | 500 (0.50 per cell) | 200 (0.20 per cell) | 500 (0.50 per cell) | 500 (0.50 per cell) |
| 4,000, 178 | 3,000 or more (0.75 per cell) | below 20 | 1,500 (0.38 per cell) | 1,500 (0.38 per cell) | 1,000 (0.25 per cell) | 1,000 (0.25 per cell) |

Load at which exact recall falls to 50%, interpolated on a log scale between
the two tested loads around it, and that load per cell:

| cells, on | Pseudo-inverse clean | Pseudo-inverse 40% removed | Covariance clean | Covariance 40% removed | Clipped binary clean | Clipped binary 40% removed |
|---|---|---|---|---|---|---|
| 225, 10 | above 200 | 111 (0.49 per cell) | 252 (1.12 per cell) | 185 (0.82 per cell) | 281 (1.25 per cell) | 189 (0.84 per cell) |
| 1,000, 44 | above 700 | 327 (0.33 per cell) | 795 (0.79 per cell) | 737 (0.74 per cell) | 777 (0.78 per cell) | 604 (0.60 per cell) |
| 4,000, 178 | above 3,000 | 1,539 (0.38 per cell) | 2,386 (0.60 per cell) | 2,337 (0.58 per cell) | 1,222 (0.31 per cell) | 1,218 (0.30 per cell) |

## Drawings, evaluation alphabets: exact recall against load

Percent of cues, mean over seeds (10 seeds at 225 cells, 10 seeds at 1,000 cells, 5 seeds at 4,000 cells).

| cells, on | load | Pseudo-inverse clean | Covariance clean | Clipped binary clean | Pseudo-inverse 40% removed | Covariance 40% removed | Clipped binary 40% removed | Ideal lookup 40% removed |
|---|---|---|---|---|---|---|---|---|
| 225, 10 | 20 | 100.0 | 100.0 | 100.0 | 97.0 | 100.0 | 100.0 | 100.0 |
| 225, 10 | 50 | 100.0 | 100.0 | 100.0 | 95.2 | 100.0 | 100.0 | 100.0 |
| 225, 10 | 100 | 100.0 | 95.5 | 99.6 | 57.6 | 84.0 | 97.7 | 100.0 |
| 225, 10 | 200 | 100.0 | 41.9 | 71.3 | 0.0 | 15.7 | 18.9 | 100.0 |
| 225, 10 | 500 | 100.0 | 1.0 | 0.6 | 0.0 | 0.0 | 0.0 | 100.0 |
| 225, 10 | 659 | 100.0 | 0.2 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 |
| 1,000, 44 | 20 | 100.0 | 100.0 | 100.0 | 99.0 | 100.0 | 100.0 | 100.0 |
| 1,000, 44 | 50 | 100.0 | 100.0 | 100.0 | 97.8 | 100.0 | 100.0 | 100.0 |
| 1,000, 44 | 100 | 100.0 | 100.0 | 100.0 | 98.1 | 100.0 | 100.0 | 100.0 |
| 1,000, 44 | 200 | 100.0 | 95.6 | 100.0 | 93.6 | 94.2 | 100.0 | 100.0 |
| 1,000, 44 | 500 | 100.0 | 8.7 | 63.8 | 0.4 | 5.3 | 35.7 | 100.0 |
| 1,000, 44 | 659 | 100.0 | 1.1 | 17.1 | 0.0 | 0.2 | 4.6 | 100.0 |
| 4,000, 178 | 20 | 100.0 | 100.0 | 100.0 | 89.0 | 100.0 | 100.0 | 100.0 |
| 4,000, 178 | 50 | 100.0 | 100.0 | 100.0 | 92.4 | 100.0 | 100.0 | 100.0 |
| 4,000, 178 | 100 | 100.0 | 100.0 | 100.0 | 90.4 | 100.0 | 100.0 | 100.0 |
| 4,000, 178 | 200 | 100.0 | 99.0 | 100.0 | 89.2 | 98.7 | 100.0 | 100.0 |
| 4,000, 178 | 500 | 100.0 | 17.1 | 99.9 | 87.4 | 15.7 | 99.7 | 100.0 |
| 4,000, 178 | 659 | 100.0 | 3.8 | 94.3 | 86.8 | 2.9 | 88.8 | 100.0 |

- The alphabets hold 659 characters, so the largest load uses all 659, one drawing each.
- For the pseudo-inverse, loads of n or more (here 225 at 225 cells) make its weights the identity matrix: every state is a fixed point, so a clean cue counts as exact recall without any completion. Capacity below leaves those loads out.

Largest load at which exact recall stays at or above 95% at every tested
load up to it, and that load per cell:

| cells, on | Pseudo-inverse clean | Pseudo-inverse 40% removed | Covariance clean | Covariance 40% removed | Clipped binary clean | Clipped binary 40% removed |
|---|---|---|---|---|---|---|
| 225, 10 | 200 or more (0.89 per cell) | 50 (0.22 per cell) | 100 (0.44 per cell) | 50 (0.22 per cell) | 100 (0.44 per cell) | 100 (0.44 per cell) |
| 1,000, 44 | 659 or more (0.66 per cell) | 100 (0.10 per cell) | 200 (0.20 per cell) | 100 (0.10 per cell) | 200 (0.20 per cell) | 200 (0.20 per cell) |
| 4,000, 178 | 659 or more (0.16 per cell) | below 20 | 200 (0.05 per cell) | 200 (0.05 per cell) | 500 (0.12 per cell) | 500 (0.12 per cell) |

Load at which exact recall falls to 50%, interpolated on a log scale between
the two tested loads around it, and that load per cell:

| cells, on | Pseudo-inverse clean | Pseudo-inverse 40% removed | Covariance clean | Covariance 40% removed | Clipped binary clean | Clipped binary 40% removed |
|---|---|---|---|---|---|---|
| 225, 10 | above 200 | 110 (0.49 per cell) | 180 (0.80 per cell) | 141 (0.63 per cell) | 264 (1.17 per cell) | 152 (0.68 per cell) |
| 1,000, 44 | above 659 | 307 (0.31 per cell) | 323 (0.32 per cell) | 315 (0.32 per cell) | 542 (0.54 per cell) | 408 (0.41 per cell) |
| 4,000, 178 | above 659 | above 659 | 346 (0.09 per cell) | 342 (0.09 per cell) | above 659 | above 659 |

## Random patterns, 225 cells: completion under damage

Each cell: overlap of raw cue → overlap of settled state, in percent; for
stray-cell damage, stray share of raw cue → settled; then exact recall, the
ideal lookup from the raw cue and the same lookup from the settled state, in
percent.

### Pseudo-inverse

| removed | stray added | load 20: cue → settled (exact, lookup cue, lookup settled) | load 100: cue → settled (exact, lookup cue, lookup settled) | load 200: cue → settled (exact, lookup cue, lookup settled) | load 500: cue → settled (exact, lookup cue, lookup settled) | load 1,000: cue → settled (exact, lookup cue, lookup settled) |
|---|---|---|---|---|---|---|
| 0% | 0% | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) |
| 20% | 0% | 80 → 100 (99, 100, 100) | 80 → 99 (94, 100, 100) | 80 → 80 (0, 100, 100) | 80 → 80 (0, 100, 100) | 80 → 80 (0, 100, 100) |
| 40% | 0% | 60 → 98 (98, 100, 99) | 60 → 95 (67, 100, 100) | 60 → 60 (0, 100, 100) | 60 → 60 (0, 100, 100) | 60 → 60 (0, 100, 100) |
| 60% | 0% | 40 → 18 (18, 100, 23) | 40 → 8 (0, 100, 21) | 40 → 40 (0, 100, 100) | 40 → 40 (0, 100, 100) | 40 → 40 (0, 100, 100) |
| 80% | 0% | 20 → 0 (0, 98, 5) | 20 → 1 (0, 92, 2) | 20 → 20 (0, 84, 83) | 20 → 20 (0, 65, 65) | 20 → 20 (0, 47, 47) |
| 0% | 25% | 100 → 100 [stray 30 → 0] (99, 100, 100) | 100 → 100 [stray 30 → 0] (97, 100, 100) | 100 → 100 [stray 30 → 30] (0, 100, 100) | 100 → 100 [stray 30 → 30] (0, 100, 100) | 100 → 100 [stray 30 → 30] (0, 100, 100) |
| 0% | 50% | 100 → 100 [stray 50 → 0] (98, 100, 100) | 100 → 100 [stray 50 → 1] (94, 100, 100) | 100 → 100 [stray 50 → 49] (0, 100, 100) | 100 → 100 [stray 50 → 50] (0, 100, 100) | 100 → 100 [stray 50 → 50] (0, 100, 100) |
| 0% | 100% | 100 → 100 [stray 100 → 0] (99, 100, 100) | 100 → 100 [stray 100 → 2] (82, 100, 100) | 100 → 100 [stray 100 → 97] (0, 100, 100) | 100 → 100 [stray 100 → 100] (0, 100, 100) | 100 → 100 [stray 100 → 100] (0, 100, 100) |
| 40% | 50% | 60 → 98 [stray 50 → 0] (97, 100, 98) | 60 → 92 [stray 50 → 1] (54, 100, 100) | 60 → 60 [stray 50 → 49] (0, 100, 100) | 60 → 60 [stray 50 → 50] (0, 100, 100) | 60 → 60 [stray 50 → 50] (0, 100, 100) |

### Covariance

| removed | stray added | load 20: cue → settled (exact, lookup cue, lookup settled) | load 100: cue → settled (exact, lookup cue, lookup settled) | load 200: cue → settled (exact, lookup cue, lookup settled) | load 500: cue → settled (exact, lookup cue, lookup settled) | load 1,000: cue → settled (exact, lookup cue, lookup settled) |
|---|---|---|---|---|---|---|
| 0% | 0% | 100 → 100 (100, 100, 100) | 100 → 100 (99, 100, 100) | 100 → 95 (75, 100, 97) | 100 → 57 (4, 100, 65) | 100 → 46 (0, 100, 53) |
| 20% | 0% | 80 → 100 (100, 100, 100) | 80 → 100 (98, 100, 100) | 80 → 90 (54, 100, 94) | 80 → 53 (1, 100, 62) | 80 → 43 (0, 100, 48) |
| 40% | 0% | 60 → 100 (100, 100, 100) | 60 → 99 (95, 100, 100) | 60 → 84 (41, 100, 89) | 60 → 47 (0, 100, 53) | 60 → 39 (0, 100, 41) |
| 60% | 0% | 40 → 100 (100, 100, 100) | 40 → 97 (91, 100, 98) | 40 → 71 (25, 100, 75) | 40 → 38 (0, 100, 36) | 40 → 33 (0, 100, 27) |
| 80% | 0% | 20 → 99 (98, 98, 98) | 20 → 81 (70, 92, 78) | 20 → 41 (7, 84, 31) | 20 → 26 (0, 65, 10) | 20 → 23 (0, 47, 5) |
| 0% | 25% | 100 → 100 [stray 30 → 0] (100, 100, 100) | 100 → 100 [stray 30 → 0] (98, 100, 100) | 100 → 90 [stray 30 → 10] (54, 100, 95) | 100 → 52 [stray 30 → 48] (1, 100, 58) | 100 → 40 [stray 30 → 60] (0, 100, 40) |
| 0% | 50% | 100 → 100 [stray 50 → 0] (100, 100, 100) | 100 → 100 [stray 50 → 0] (97, 100, 100) | 100 → 88 [stray 50 → 12] (50, 100, 93) | 100 → 48 [stray 50 → 52] (0, 100, 52) | 100 → 37 [stray 50 → 63] (0, 100, 34) |
| 0% | 100% | 100 → 100 [stray 100 → 0] (100, 100, 100) | 100 → 100 [stray 100 → 0] (96, 100, 100) | 100 → 83 [stray 100 → 17] (40, 100, 87) | 100 → 42 [stray 100 → 58] (0, 100, 41) | 100 → 31 [stray 100 → 69] (0, 100, 25) |
| 40% | 50% | 60 → 100 [stray 50 → 0] (100, 100, 100) | 60 → 98 [stray 50 → 2] (91, 100, 98) | 60 → 66 [stray 50 → 34] (24, 100, 68) | 60 → 34 [stray 50 → 66] (0, 100, 28) | 60 → 27 [stray 50 → 73] (0, 100, 16) |

### Clipped binary

| removed | stray added | load 20: cue → settled (exact, lookup cue, lookup settled) | load 100: cue → settled (exact, lookup cue, lookup settled) | load 200: cue → settled (exact, lookup cue, lookup settled) | load 500: cue → settled (exact, lookup cue, lookup settled) | load 1,000: cue → settled (exact, lookup cue, lookup settled) |
|---|---|---|---|---|---|---|
| 0% | 0% | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) | 100 → 99 (91, 100, 100) | 100 → 31 (0, 100, 43) | 100 → 11 (0, 100, 2) |
| 20% | 0% | 80 → 100 (100, 100, 100) | 80 → 100 (99, 100, 100) | 80 → 94 (72, 100, 100) | 80 → 39 (0, 100, 57) | 80 → 10 (0, 100, 2) |
| 40% | 0% | 60 → 100 (100, 100, 100) | 60 → 100 (99, 100, 100) | 60 → 82 (41, 100, 96) | 60 → 43 (0, 100, 71) | 60 → 10 (0, 100, 1) |
| 60% | 0% | 40 → 100 (100, 100, 100) | 40 → 99 (97, 100, 100) | 40 → 60 (12, 100, 83) | 40 → 30 (0, 100, 40) | 40 → 10 (0, 100, 1) |
| 80% | 0% | 20 → 99 (98, 98, 98) | 20 → 81 (71, 92, 79) | 20 → 28 (1, 84, 22) | 20 → 17 (0, 65, 4) | 20 → 8 (0, 47, 0) |
| 0% | 25% | 100 → 100 [stray 30 → 0] (100, 100, 100) | 100 → 100 [stray 30 → 0] (99, 100, 100) | 100 → 90 [stray 30 → 10] (57, 100, 99) | 100 → 26 [stray 30 → 74] (0, 100, 28) | 100 → 10 [stray 30 → 90] (0, 100, 2) |
| 0% | 50% | 100 → 100 [stray 50 → 0] (100, 100, 100) | 100 → 100 [stray 50 → 0] (99, 100, 100) | 100 → 83 [stray 50 → 17] (42, 100, 96) | 100 → 22 [stray 50 → 78] (0, 100, 21) | 100 → 9 [stray 50 → 91] (0, 100, 1) |
| 0% | 100% | 100 → 100 [stray 100 → 0] (100, 100, 100) | 100 → 100 [stray 100 → 0] (98, 100, 100) | 100 → 59 [stray 100 → 41] (14, 100, 74) | 100 → 17 [stray 100 → 83] (0, 100, 10) | 100 → 8 [stray 100 → 92] (0, 100, 1) |
| 40% | 50% | 60 → 100 [stray 50 → 0] (100, 100, 100) | 60 → 97 [stray 50 → 3] (93, 100, 98) | 60 → 42 [stray 50 → 58] (4, 100, 52) | 60 → 20 [stray 50 → 80] (0, 100, 15) | 60 → 8 [stray 50 → 92] (0, 100, 1) |

## Random patterns, 1,000 cells: completion under damage

Each cell: overlap of raw cue → overlap of settled state, in percent; for
stray-cell damage, stray share of raw cue → settled; then exact recall, the
ideal lookup from the raw cue and the same lookup from the settled state, in
percent.

### Pseudo-inverse

| removed | stray added | load 20: cue → settled (exact, lookup cue, lookup settled) | load 100: cue → settled (exact, lookup cue, lookup settled) | load 200: cue → settled (exact, lookup cue, lookup settled) | load 500: cue → settled (exact, lookup cue, lookup settled) | load 1,000: cue → settled (exact, lookup cue, lookup settled) |
|---|---|---|---|---|---|---|
| 0% | 0% | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) |
| 20% | 0% | 80 → 100 (99, 100, 100) | 80 → 100 (99, 100, 100) | 80 → 100 (98, 100, 100) | 80 → 100 (89, 100, 100) | 80 → 80 (0, 100, 100) |
| 40% | 0% | 59 → 100 (98, 100, 100) | 59 → 100 (98, 100, 100) | 59 → 100 (97, 100, 100) | 59 → 91 (10, 100, 100) | 59 → 59 (0, 100, 100) |
| 60% | 0% | 41 → 12 (11, 100, 17) | 41 → 0 (0, 100, 2) | 41 → 0 (0, 100, 1) | 41 → 10 (0, 100, 72) | 41 → 41 (0, 100, 100) |
| 80% | 0% | 20 → 0 (0, 100, 5) | 20 → 0 (0, 100, 1) | 20 → 0 (0, 100, 1) | 20 → 0 (0, 100, 1) | 20 → 20 (0, 100, 100) |
| 0% | 25% | 100 → 100 [stray 25 → 0] (98, 100, 100) | 100 → 100 [stray 25 → 0] (99, 100, 100) | 100 → 100 [stray 25 → 0] (99, 100, 100) | 100 → 100 [stray 25 → 0] (92, 100, 100) | 100 → 100 [stray 25 → 25] (0, 100, 100) |
| 0% | 50% | 100 → 100 [stray 50 → 0] (98, 100, 100) | 100 → 100 [stray 50 → 0] (97, 100, 100) | 100 → 100 [stray 50 → 0] (97, 100, 100) | 100 → 100 [stray 50 → 0] (81, 100, 100) | 100 → 100 [stray 50 → 50] (0, 100, 100) |
| 0% | 100% | 100 → 100 [stray 100 → 0] (96, 100, 100) | 100 → 100 [stray 100 → 0] (93, 100, 100) | 100 → 100 [stray 100 → 0] (93, 100, 100) | 100 → 100 [stray 100 → 1] (55, 100, 100) | 100 → 100 [stray 100 → 100] (0, 100, 100) |
| 40% | 50% | 59 → 100 [stray 50 → 0] (98, 100, 100) | 59 → 100 [stray 50 → 0] (93, 100, 100) | 59 → 100 [stray 50 → 0] (93, 100, 100) | 59 → 89 [stray 50 → 1] (4, 100, 100) | 59 → 59 [stray 50 → 50] (0, 100, 100) |

### Covariance

| removed | stray added | load 20: cue → settled (exact, lookup cue, lookup settled) | load 100: cue → settled (exact, lookup cue, lookup settled) | load 200: cue → settled (exact, lookup cue, lookup settled) | load 500: cue → settled (exact, lookup cue, lookup settled) | load 1,000: cue → settled (exact, lookup cue, lookup settled) |
|---|---|---|---|---|---|---|
| 0% | 0% | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) | 100 → 100 (97, 100, 100) | 100 → 95 (14, 100, 100) |
| 20% | 0% | 80 → 100 (100, 100, 100) | 80 → 100 (100, 100, 100) | 80 → 100 (100, 100, 100) | 80 → 100 (95, 100, 100) | 80 → 93 (7, 100, 100) |
| 40% | 0% | 59 → 100 (100, 100, 100) | 59 → 100 (100, 100, 100) | 59 → 100 (100, 100, 100) | 59 → 100 (94, 100, 100) | 59 → 92 (6, 100, 100) |
| 60% | 0% | 41 → 100 (100, 100, 100) | 41 → 100 (100, 100, 100) | 41 → 100 (100, 100, 100) | 41 → 100 (94, 100, 100) | 41 → 89 (4, 100, 100) |
| 80% | 0% | 20 → 100 (100, 100, 100) | 20 → 100 (100, 100, 100) | 20 → 100 (100, 100, 100) | 20 → 100 (94, 100, 100) | 20 → 70 (2, 100, 93) |
| 0% | 25% | 100 → 100 [stray 25 → 0] (100, 100, 100) | 100 → 100 [stray 25 → 0] (100, 100, 100) | 100 → 100 [stray 25 → 0] (100, 100, 100) | 100 → 100 [stray 25 → 0] (95, 100, 100) | 100 → 94 [stray 25 → 6] (7, 100, 100) |
| 0% | 50% | 100 → 100 [stray 50 → 0] (100, 100, 100) | 100 → 100 [stray 50 → 0] (100, 100, 100) | 100 → 100 [stray 50 → 0] (100, 100, 100) | 100 → 100 [stray 50 → 0] (94, 100, 100) | 100 → 93 [stray 50 → 7] (6, 100, 100) |
| 0% | 100% | 100 → 100 [stray 100 → 0] (100, 100, 100) | 100 → 100 [stray 100 → 0] (100, 100, 100) | 100 → 100 [stray 100 → 0] (100, 100, 100) | 100 → 100 [stray 100 → 0] (94, 100, 100) | 100 → 92 [stray 100 → 8] (5, 100, 100) |
| 40% | 50% | 59 → 100 [stray 50 → 0] (100, 100, 100) | 59 → 100 [stray 50 → 0] (100, 100, 100) | 59 → 100 [stray 50 → 0] (100, 100, 100) | 59 → 100 [stray 50 → 0] (94, 100, 100) | 59 → 87 [stray 50 → 13] (4, 100, 100) |

### Clipped binary

| removed | stray added | load 20: cue → settled (exact, lookup cue, lookup settled) | load 100: cue → settled (exact, lookup cue, lookup settled) | load 200: cue → settled (exact, lookup cue, lookup settled) | load 500: cue → settled (exact, lookup cue, lookup settled) | load 1,000: cue → settled (exact, lookup cue, lookup settled) |
|---|---|---|---|---|---|---|
| 0% | 0% | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) | 100 → 28 (0, 100, 72) |
| 20% | 0% | 80 → 100 (100, 100, 100) | 80 → 100 (100, 100, 100) | 80 → 100 (100, 100, 100) | 80 → 100 (100, 100, 100) | 80 → 28 (0, 100, 71) |
| 40% | 0% | 59 → 100 (100, 100, 100) | 59 → 100 (100, 100, 100) | 59 → 100 (100, 100, 100) | 59 → 100 (99, 100, 100) | 59 → 34 (0, 100, 80) |
| 60% | 0% | 41 → 100 (100, 100, 100) | 41 → 100 (100, 100, 100) | 41 → 100 (100, 100, 100) | 41 → 100 (99, 100, 100) | 41 → 26 (0, 100, 72) |
| 80% | 0% | 20 → 100 (100, 100, 100) | 20 → 100 (100, 100, 100) | 20 → 100 (100, 100, 100) | 20 → 98 (95, 100, 100) | 20 → 15 (0, 100, 33) |
| 0% | 25% | 100 → 100 [stray 25 → 0] (100, 100, 100) | 100 → 100 [stray 25 → 0] (100, 100, 100) | 100 → 100 [stray 25 → 0] (100, 100, 100) | 100 → 100 [stray 25 → 0] (99, 100, 100) | 100 → 21 [stray 25 → 79] (0, 100, 57) |
| 0% | 50% | 100 → 100 [stray 50 → 0] (100, 100, 100) | 100 → 100 [stray 50 → 0] (100, 100, 100) | 100 → 100 [stray 50 → 0] (100, 100, 100) | 100 → 100 [stray 50 → 0] (99, 100, 100) | 100 → 15 [stray 50 → 85] (0, 100, 37) |
| 0% | 100% | 100 → 100 [stray 100 → 0] (100, 100, 100) | 100 → 100 [stray 100 → 0] (100, 100, 100) | 100 → 100 [stray 100 → 0] (100, 100, 100) | 100 → 96 [stray 100 → 4] (91, 100, 99) | 100 → 11 [stray 100 → 89] (0, 100, 15) |
| 40% | 50% | 59 → 100 [stray 50 → 0] (100, 100, 100) | 59 → 100 [stray 50 → 0] (100, 100, 100) | 59 → 100 [stray 50 → 0] (100, 100, 100) | 59 → 89 [stray 50 → 11] (81, 100, 97) | 59 → 13 [stray 50 → 87] (0, 100, 25) |

## Random patterns, 4,000 cells: completion under damage

Each cell: overlap of raw cue → overlap of settled state, in percent; for
stray-cell damage, stray share of raw cue → settled; then exact recall, the
ideal lookup from the raw cue and the same lookup from the settled state, in
percent.

### Pseudo-inverse

| removed | stray added | load 20: cue → settled (exact, lookup cue, lookup settled) | load 100: cue → settled (exact, lookup cue, lookup settled) | load 200: cue → settled (exact, lookup cue, lookup settled) | load 500: cue → settled (exact, lookup cue, lookup settled) | load 1,000: cue → settled (exact, lookup cue, lookup settled) |
|---|---|---|---|---|---|---|
| 0% | 0% | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) |
| 20% | 0% | 80 → 100 (95, 100, 100) | 80 → 100 (96, 100, 100) | 80 → 100 (93, 100, 100) | 80 → 100 (95, 100, 100) | 80 → 100 (95, 100, 100) |
| 40% | 0% | 60 → 100 (87, 100, 100) | 60 → 100 (89, 100, 100) | 60 → 100 (87, 100, 100) | 60 → 100 (89, 100, 100) | 60 → 100 (85, 100, 100) |
| 60% | 0% | 40 → 0 (0, 100, 10) | 40 → 0 (0, 100, 3) | 40 → 0 (0, 100, 3) | 40 → 0 (0, 100, 1) | 40 → 0 (0, 100, 1) |
| 80% | 0% | 20 → 0 (0, 100, 9) | 20 → 0 (0, 100, 2) | 20 → 0 (0, 100, 1) | 20 → 0 (0, 100, 0) | 20 → 0 (0, 100, 0) |
| 0% | 25% | 100 → 100 [stray 25 → 0] (95, 100, 100) | 100 → 100 [stray 25 → 0] (96, 100, 100) | 100 → 100 [stray 25 → 0] (91, 100, 100) | 100 → 100 [stray 25 → 0] (94, 100, 100) | 100 → 100 [stray 25 → 0] (94, 100, 100) |
| 0% | 50% | 100 → 100 [stray 50 → 0] (89, 100, 100) | 100 → 100 [stray 50 → 0] (90, 100, 100) | 100 → 100 [stray 50 → 0] (85, 100, 100) | 100 → 100 [stray 50 → 0] (89, 100, 100) | 100 → 100 [stray 50 → 0] (88, 100, 100) |
| 0% | 100% | 100 → 100 [stray 100 → 0] (75, 100, 100) | 100 → 100 [stray 100 → 0] (78, 100, 100) | 100 → 100 [stray 100 → 0] (75, 100, 100) | 100 → 100 [stray 100 → 0] (79, 100, 100) | 100 → 100 [stray 100 → 0] (79, 100, 100) |
| 40% | 50% | 60 → 100 [stray 50 → 0] (77, 100, 100) | 60 → 100 [stray 50 → 0] (83, 100, 100) | 60 → 100 [stray 50 → 0] (75, 100, 100) | 60 → 100 [stray 50 → 0] (78, 100, 100) | 60 → 100 [stray 50 → 0] (77, 100, 100) |

### Covariance

| removed | stray added | load 20: cue → settled (exact, lookup cue, lookup settled) | load 100: cue → settled (exact, lookup cue, lookup settled) | load 200: cue → settled (exact, lookup cue, lookup settled) | load 500: cue → settled (exact, lookup cue, lookup settled) | load 1,000: cue → settled (exact, lookup cue, lookup settled) |
|---|---|---|---|---|---|---|
| 0% | 0% | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) |
| 20% | 0% | 80 → 100 (100, 100, 100) | 80 → 100 (100, 100, 100) | 80 → 100 (100, 100, 100) | 80 → 100 (100, 100, 100) | 80 → 100 (100, 100, 100) |
| 40% | 0% | 60 → 100 (100, 100, 100) | 60 → 100 (100, 100, 100) | 60 → 100 (100, 100, 100) | 60 → 100 (100, 100, 100) | 60 → 100 (100, 100, 100) |
| 60% | 0% | 40 → 100 (100, 100, 100) | 40 → 100 (100, 100, 100) | 40 → 100 (100, 100, 100) | 40 → 100 (100, 100, 100) | 40 → 100 (100, 100, 100) |
| 80% | 0% | 20 → 100 (100, 100, 100) | 20 → 100 (100, 100, 100) | 20 → 100 (100, 100, 100) | 20 → 100 (100, 100, 100) | 20 → 100 (100, 100, 100) |
| 0% | 25% | 100 → 100 [stray 25 → 0] (100, 100, 100) | 100 → 100 [stray 25 → 0] (100, 100, 100) | 100 → 100 [stray 25 → 0] (100, 100, 100) | 100 → 100 [stray 25 → 0] (100, 100, 100) | 100 → 100 [stray 25 → 0] (100, 100, 100) |
| 0% | 50% | 100 → 100 [stray 50 → 0] (100, 100, 100) | 100 → 100 [stray 50 → 0] (100, 100, 100) | 100 → 100 [stray 50 → 0] (100, 100, 100) | 100 → 100 [stray 50 → 0] (100, 100, 100) | 100 → 100 [stray 50 → 0] (100, 100, 100) |
| 0% | 100% | 100 → 100 [stray 100 → 0] (100, 100, 100) | 100 → 100 [stray 100 → 0] (100, 100, 100) | 100 → 100 [stray 100 → 0] (100, 100, 100) | 100 → 100 [stray 100 → 0] (100, 100, 100) | 100 → 100 [stray 100 → 0] (100, 100, 100) |
| 40% | 50% | 60 → 100 [stray 50 → 0] (100, 100, 100) | 60 → 100 [stray 50 → 0] (100, 100, 100) | 60 → 100 [stray 50 → 0] (100, 100, 100) | 60 → 100 [stray 50 → 0] (100, 100, 100) | 60 → 100 [stray 50 → 0] (100, 100, 100) |

### Clipped binary

| removed | stray added | load 20: cue → settled (exact, lookup cue, lookup settled) | load 100: cue → settled (exact, lookup cue, lookup settled) | load 200: cue → settled (exact, lookup cue, lookup settled) | load 500: cue → settled (exact, lookup cue, lookup settled) | load 1,000: cue → settled (exact, lookup cue, lookup settled) |
|---|---|---|---|---|---|---|
| 0% | 0% | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) | 100 → 100 (99, 100, 100) |
| 20% | 0% | 80 → 100 (100, 100, 100) | 80 → 100 (100, 100, 100) | 80 → 100 (100, 100, 100) | 80 → 100 (100, 100, 100) | 80 → 100 (99, 100, 100) |
| 40% | 0% | 60 → 100 (100, 100, 100) | 60 → 100 (100, 100, 100) | 60 → 100 (100, 100, 100) | 60 → 100 (100, 100, 100) | 60 → 100 (98, 100, 100) |
| 60% | 0% | 40 → 100 (100, 100, 100) | 40 → 100 (100, 100, 100) | 40 → 100 (100, 100, 100) | 40 → 100 (100, 100, 100) | 40 → 100 (98, 100, 100) |
| 80% | 0% | 20 → 100 (100, 100, 100) | 20 → 100 (100, 100, 100) | 20 → 100 (100, 100, 100) | 20 → 100 (100, 100, 100) | 20 → 100 (97, 100, 100) |
| 0% | 25% | 100 → 100 [stray 25 → 0] (100, 100, 100) | 100 → 100 [stray 25 → 0] (100, 100, 100) | 100 → 100 [stray 25 → 0] (100, 100, 100) | 100 → 100 [stray 25 → 0] (100, 100, 100) | 100 → 100 [stray 25 → 0] (97, 100, 100) |
| 0% | 50% | 100 → 100 [stray 50 → 0] (100, 100, 100) | 100 → 100 [stray 50 → 0] (100, 100, 100) | 100 → 100 [stray 50 → 0] (100, 100, 100) | 100 → 100 [stray 50 → 0] (100, 100, 100) | 100 → 100 [stray 50 → 0] (97, 100, 100) |
| 0% | 100% | 100 → 100 [stray 100 → 0] (100, 100, 100) | 100 → 100 [stray 100 → 0] (100, 100, 100) | 100 → 100 [stray 100 → 0] (100, 100, 100) | 100 → 100 [stray 100 → 0] (100, 100, 100) | 100 → 26 [stray 100 → 74] (4, 100, 91) |
| 40% | 50% | 60 → 100 [stray 50 → 0] (100, 100, 100) | 60 → 100 [stray 50 → 0] (100, 100, 100) | 60 → 100 [stray 50 → 0] (100, 100, 100) | 60 → 100 [stray 50 → 0] (100, 100, 100) | 60 → 36 [stray 50 → 64] (15, 100, 93) |

## Drawings, evaluation alphabets, 225 cells: completion under damage

Each cell: overlap of raw cue → overlap of settled state, in percent; for
stray-cell damage, stray share of raw cue → settled; then exact recall, the
ideal lookup from the raw cue and the same lookup from the settled state, in
percent.

### Pseudo-inverse

| removed | stray added | load 20: cue → settled (exact, lookup cue, lookup settled) | load 100: cue → settled (exact, lookup cue, lookup settled) | load 200: cue → settled (exact, lookup cue, lookup settled) | load 500: cue → settled (exact, lookup cue, lookup settled) | load 659: cue → settled (exact, lookup cue, lookup settled) |
|---|---|---|---|---|---|---|
| 0% | 0% | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) |
| 20% | 0% | 80 → 100 (99, 100, 100) | 80 → 99 (95, 100, 100) | 80 → 80 (0, 100, 100) | 80 → 80 (0, 100, 100) | 80 → 80 (0, 100, 100) |
| 40% | 0% | 60 → 97 (97, 100, 97) | 60 → 91 (58, 100, 100) | 60 → 60 (0, 100, 100) | 60 → 60 (0, 100, 100) | 60 → 60 (0, 100, 100) |
| 60% | 0% | 40 → 11 (11, 100, 17) | 40 → 10 (0, 100, 25) | 40 → 40 (0, 100, 100) | 40 → 40 (0, 100, 100) | 40 → 40 (0, 100, 100) |
| 80% | 0% | 20 → 0 (0, 99, 5) | 20 → 1 (0, 88, 2) | 20 → 20 (0, 78, 78) | 20 → 20 (0, 56, 56) | 20 → 20 (0, 47, 47) |
| 0% | 25% | 100 → 100 [stray 30 → 0] (99, 100, 100) | 100 → 100 [stray 30 → 0] (96, 100, 100) | 100 → 100 [stray 30 → 29] (0, 100, 100) | 100 → 100 [stray 30 → 30] (0, 100, 100) | 100 → 100 [stray 30 → 30] (0, 100, 100) |
| 0% | 50% | 100 → 100 [stray 50 → 0] (99, 100, 100) | 100 → 100 [stray 50 → 1] (95, 100, 100) | 100 → 100 [stray 50 → 48] (0, 100, 100) | 100 → 100 [stray 50 → 50] (0, 100, 100) | 100 → 100 [stray 50 → 50] (0, 100, 100) |
| 0% | 100% | 100 → 100 [stray 100 → 0] (100, 100, 100) | 100 → 100 [stray 100 → 3] (79, 100, 100) | 100 → 100 [stray 100 → 96] (0, 100, 100) | 100 → 100 [stray 100 → 100] (0, 100, 100) | 100 → 100 [stray 100 → 100] (0, 100, 100) |
| 40% | 50% | 60 → 96 [stray 50 → 0] (94, 100, 96) | 60 → 90 [stray 50 → 1] (47, 100, 100) | 60 → 60 [stray 50 → 48] (0, 100, 100) | 60 → 60 [stray 50 → 50] (0, 100, 100) | 60 → 60 [stray 50 → 50] (0, 100, 100) |

### Covariance

| removed | stray added | load 20: cue → settled (exact, lookup cue, lookup settled) | load 100: cue → settled (exact, lookup cue, lookup settled) | load 200: cue → settled (exact, lookup cue, lookup settled) | load 500: cue → settled (exact, lookup cue, lookup settled) | load 659: cue → settled (exact, lookup cue, lookup settled) |
|---|---|---|---|---|---|---|
| 0% | 0% | 100 → 100 (100, 100, 100) | 100 → 99 (96, 100, 99) | 100 → 76 (42, 100, 73) | 100 → 30 (1, 100, 14) | 100 → 24 (0, 100, 8) |
| 20% | 0% | 80 → 100 (100, 100, 100) | 80 → 97 (90, 100, 97) | 80 → 68 (24, 100, 65) | 80 → 28 (0, 100, 12) | 80 → 22 (0, 100, 6) |
| 40% | 0% | 60 → 100 (100, 100, 100) | 60 → 96 (84, 100, 95) | 60 → 59 (16, 100, 53) | 60 → 25 (0, 100, 9) | 60 → 20 (0, 100, 5) |
| 60% | 0% | 40 → 100 (100, 100, 100) | 40 → 91 (77, 100, 90) | 40 → 48 (9, 100, 38) | 40 → 21 (0, 100, 5) | 40 → 18 (0, 100, 3) |
| 80% | 0% | 20 → 100 (99, 99, 100) | 20 → 69 (50, 88, 61) | 20 → 32 (4, 78, 17) | 20 → 17 (0, 56, 2) | 20 → 15 (0, 47, 1) |
| 0% | 25% | 100 → 100 [stray 30 → 0] (100, 100, 100) | 100 → 98 [stray 30 → 2] (91, 100, 98) | 100 → 69 [stray 30 → 31] (27, 100, 65) | 100 → 28 [stray 30 → 72] (0, 100, 12) | 100 → 22 [stray 30 → 78] (0, 100, 7) |
| 0% | 50% | 100 → 100 [stray 50 → 0] (100, 100, 100) | 100 → 97 [stray 50 → 3] (89, 100, 97) | 100 → 66 [stray 50 → 34] (22, 100, 62) | 100 → 26 [stray 50 → 74] (0, 100, 10) | 100 → 21 [stray 50 → 79] (0, 100, 6) |
| 0% | 100% | 100 → 100 [stray 100 → 0] (100, 100, 100) | 100 → 96 [stray 100 → 4] (86, 100, 97) | 100 → 60 [stray 100 → 40] (17, 100, 53) | 100 → 24 [stray 100 → 76] (0, 100, 8) | 100 → 20 [stray 100 → 80] (0, 100, 5) |
| 40% | 50% | 60 → 100 [stray 50 → 0] (100, 100, 100) | 60 → 91 [stray 50 → 9] (76, 100, 90) | 60 → 46 [stray 50 → 54] (8, 100, 36) | 60 → 21 [stray 50 → 79] (0, 100, 5) | 60 → 17 [stray 50 → 83] (0, 100, 3) |

### Clipped binary

| removed | stray added | load 20: cue → settled (exact, lookup cue, lookup settled) | load 100: cue → settled (exact, lookup cue, lookup settled) | load 200: cue → settled (exact, lookup cue, lookup settled) | load 500: cue → settled (exact, lookup cue, lookup settled) | load 659: cue → settled (exact, lookup cue, lookup settled) |
|---|---|---|---|---|---|---|
| 0% | 0% | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) | 100 → 92 (71, 100, 97) | 100 → 13 (1, 100, 5) | 100 → 11 (0, 100, 2) |
| 20% | 0% | 80 → 100 (100, 100, 100) | 80 → 100 (99, 100, 100) | 80 → 79 (43, 100, 90) | 80 → 15 (0, 100, 8) | 80 → 12 (0, 100, 3) |
| 40% | 0% | 60 → 100 (100, 100, 100) | 60 → 100 (98, 100, 100) | 60 → 62 (19, 100, 76) | 60 → 18 (0, 100, 15) | 60 → 12 (0, 100, 4) |
| 60% | 0% | 40 → 100 (100, 100, 100) | 40 → 98 (93, 100, 99) | 40 → 44 (5, 100, 52) | 40 → 16 (0, 100, 9) | 40 → 14 (0, 100, 4) |
| 80% | 0% | 20 → 99 (99, 99, 99) | 20 → 77 (62, 88, 74) | 20 → 23 (1, 78, 12) | 20 → 13 (0, 56, 1) | 20 → 14 (0, 47, 1) |
| 0% | 25% | 100 → 100 [stray 30 → 0] (100, 100, 100) | 100 → 100 [stray 30 → 0] (99, 100, 100) | 100 → 68 [stray 30 → 32] (25, 100, 82) | 100 → 10 [stray 30 → 90] (0, 100, 2) | 100 → 9 [stray 30 → 91] (0, 100, 1) |
| 0% | 50% | 100 → 100 [stray 50 → 0] (100, 100, 100) | 100 → 100 [stray 50 → 0] (98, 100, 100) | 100 → 55 [stray 50 → 45] (15, 100, 65) | 100 → 9 [stray 50 → 91] (0, 100, 1) | 100 → 9 [stray 50 → 91] (0, 100, 1) |
| 0% | 100% | 100 → 100 [stray 100 → 0] (100, 100, 100) | 100 → 99 [stray 100 → 1] (96, 100, 100) | 100 → 31 [stray 100 → 69] (2, 100, 28) | 100 → 8 [stray 100 → 92] (0, 100, 1) | 100 → 8 [stray 100 → 92] (0, 100, 0) |
| 40% | 50% | 60 → 100 [stray 50 → 0] (100, 100, 100) | 60 → 95 [stray 50 → 5] (88, 100, 97) | 60 → 27 [stray 50 → 73] (1, 100, 21) | 60 → 9 [stray 50 → 91] (0, 100, 1) | 60 → 8 [stray 50 → 92] (0, 100, 0) |

## Drawings, evaluation alphabets, 1,000 cells: completion under damage

Each cell: overlap of raw cue → overlap of settled state, in percent; for
stray-cell damage, stray share of raw cue → settled; then exact recall, the
ideal lookup from the raw cue and the same lookup from the settled state, in
percent.

### Pseudo-inverse

| removed | stray added | load 20: cue → settled (exact, lookup cue, lookup settled) | load 100: cue → settled (exact, lookup cue, lookup settled) | load 200: cue → settled (exact, lookup cue, lookup settled) | load 500: cue → settled (exact, lookup cue, lookup settled) | load 659: cue → settled (exact, lookup cue, lookup settled) |
|---|---|---|---|---|---|---|
| 0% | 0% | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) |
| 20% | 0% | 80 → 100 (99, 100, 100) | 80 → 100 (99, 100, 100) | 80 → 100 (99, 100, 100) | 80 → 98 (52, 100, 100) | 80 → 85 (0, 100, 100) |
| 40% | 0% | 59 → 100 (99, 100, 100) | 59 → 100 (98, 100, 100) | 59 → 100 (94, 100, 100) | 59 → 80 (0, 100, 100) | 59 → 61 (0, 100, 100) |
| 60% | 0% | 41 → 2 (1, 100, 7) | 41 → 0 (0, 100, 1) | 41 → 0 (0, 100, 1) | 41 → 21 (0, 100, 97) | 41 → 39 (0, 100, 100) |
| 80% | 0% | 20 → 0 (0, 100, 5) | 20 → 0 (0, 100, 1) | 20 → 0 (0, 100, 1) | 20 → 2 (0, 100, 12) | 20 → 15 (0, 100, 99) |
| 0% | 25% | 100 → 100 [stray 25 → 0] (98, 100, 100) | 100 → 100 [stray 25 → 0] (99, 100, 100) | 100 → 100 [stray 25 → 0] (98, 100, 100) | 100 → 100 [stray 25 → 1] (79, 100, 100) | 100 → 100 [stray 25 → 9] (0, 100, 100) |
| 0% | 50% | 100 → 100 [stray 50 → 0] (95, 100, 100) | 100 → 100 [stray 50 → 0] (98, 100, 100) | 100 → 100 [stray 50 → 0] (97, 100, 100) | 100 → 100 [stray 50 → 2] (55, 100, 100) | 100 → 100 [stray 50 → 21] (0, 100, 100) |
| 0% | 100% | 100 → 100 [stray 100 → 0] (95, 100, 100) | 100 → 100 [stray 100 → 0] (94, 100, 100) | 100 → 100 [stray 100 → 0] (94, 100, 100) | 100 → 100 [stray 100 → 5] (16, 100, 100) | 100 → 100 [stray 100 → 48] (0, 100, 100) |
| 40% | 50% | 59 → 100 [stray 50 → 0] (98, 100, 100) | 59 → 100 [stray 50 → 0] (96, 100, 100) | 59 → 100 [stray 50 → 0] (91, 100, 100) | 59 → 78 [stray 50 → 3] (0, 100, 100) | 59 → 62 [stray 50 → 22] (0, 100, 100) |

### Covariance

| removed | stray added | load 20: cue → settled (exact, lookup cue, lookup settled) | load 100: cue → settled (exact, lookup cue, lookup settled) | load 200: cue → settled (exact, lookup cue, lookup settled) | load 500: cue → settled (exact, lookup cue, lookup settled) | load 659: cue → settled (exact, lookup cue, lookup settled) |
|---|---|---|---|---|---|---|
| 0% | 0% | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) | 100 → 100 (96, 100, 100) | 100 → 32 (9, 100, 23) | 100 → 17 (1, 100, 6) |
| 20% | 0% | 80 → 100 (100, 100, 100) | 80 → 100 (100, 100, 100) | 80 → 100 (94, 100, 100) | 80 → 30 (5, 100, 21) | 80 → 16 (1, 100, 5) |
| 40% | 0% | 59 → 100 (100, 100, 100) | 59 → 100 (100, 100, 100) | 59 → 100 (94, 100, 100) | 59 → 28 (5, 100, 19) | 59 → 16 (0, 100, 4) |
| 60% | 0% | 41 → 100 (100, 100, 100) | 41 → 100 (100, 100, 100) | 41 → 100 (94, 100, 100) | 41 → 25 (4, 100, 15) | 41 → 14 (0, 100, 3) |
| 80% | 0% | 20 → 100 (100, 100, 100) | 20 → 100 (100, 100, 100) | 20 → 98 (92, 100, 99) | 20 → 18 (2, 100, 7) | 20 → 13 (0, 100, 2) |
| 0% | 25% | 100 → 100 [stray 25 → 0] (100, 100, 100) | 100 → 100 [stray 25 → 0] (100, 100, 100) | 100 → 100 [stray 25 → 0] (95, 100, 100) | 100 → 31 [stray 25 → 69] (6, 100, 21) | 100 → 16 [stray 25 → 84] (1, 100, 5) |
| 0% | 50% | 100 → 100 [stray 50 → 0] (100, 100, 100) | 100 → 100 [stray 50 → 0] (100, 100, 100) | 100 → 100 [stray 50 → 0] (95, 100, 100) | 100 → 29 [stray 50 → 71] (5, 100, 19) | 100 → 16 [stray 50 → 84] (0, 100, 5) |
| 0% | 100% | 100 → 100 [stray 100 → 0] (100, 100, 100) | 100 → 100 [stray 100 → 0] (100, 100, 100) | 100 → 100 [stray 100 → 0] (94, 100, 100) | 100 → 27 [stray 100 → 73] (5, 100, 17) | 100 → 15 [stray 100 → 85] (0, 100, 4) |
| 40% | 50% | 59 → 100 [stray 50 → 0] (100, 100, 100) | 59 → 100 [stray 50 → 0] (100, 100, 100) | 59 → 100 [stray 50 → 0] (93, 100, 100) | 59 → 22 [stray 50 → 78] (4, 100, 12) | 59 → 14 [stray 50 → 86] (0, 100, 3) |

### Clipped binary

| removed | stray added | load 20: cue → settled (exact, lookup cue, lookup settled) | load 100: cue → settled (exact, lookup cue, lookup settled) | load 200: cue → settled (exact, lookup cue, lookup settled) | load 500: cue → settled (exact, lookup cue, lookup settled) | load 659: cue → settled (exact, lookup cue, lookup settled) |
|---|---|---|---|---|---|---|
| 0% | 0% | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) | 100 → 93 (64, 100, 98) | 100 → 45 (17, 100, 55) |
| 20% | 0% | 80 → 100 (100, 100, 100) | 80 → 100 (100, 100, 100) | 80 → 100 (100, 100, 100) | 80 → 87 (48, 100, 94) | 80 → 36 (9, 100, 48) |
| 40% | 0% | 59 → 100 (100, 100, 100) | 59 → 100 (100, 100, 100) | 59 → 100 (100, 100, 100) | 59 → 76 (36, 100, 84) | 59 → 28 (5, 100, 39) |
| 60% | 0% | 41 → 100 (100, 100, 100) | 41 → 100 (100, 100, 100) | 41 → 100 (100, 100, 100) | 41 → 57 (25, 100, 65) | 41 → 21 (2, 100, 31) |
| 80% | 0% | 20 → 100 (100, 100, 100) | 20 → 100 (100, 100, 100) | 20 → 100 (100, 100, 100) | 20 → 27 (8, 100, 22) | 20 → 14 (0, 100, 10) |
| 0% | 25% | 100 → 100 [stray 25 → 0] (100, 100, 100) | 100 → 100 [stray 25 → 0] (100, 100, 100) | 100 → 100 [stray 25 → 0] (100, 100, 100) | 100 → 47 [stray 25 → 53] (18, 100, 52) | 100 → 14 [stray 25 → 86] (1, 100, 12) |
| 0% | 50% | 100 → 100 [stray 50 → 0] (100, 100, 100) | 100 → 100 [stray 50 → 0] (100, 100, 100) | 100 → 100 [stray 50 → 0] (100, 100, 100) | 100 → 18 [stray 50 → 82] (2, 100, 10) | 100 → 10 [stray 50 → 90] (0, 100, 3) |
| 0% | 100% | 100 → 100 [stray 100 → 0] (100, 100, 100) | 100 → 100 [stray 100 → 0] (100, 100, 100) | 100 → 100 [stray 100 → 0] (100, 100, 100) | 100 → 12 [stray 100 → 88] (0, 100, 2) | 100 → 8 [stray 100 → 92] (0, 100, 1) |
| 40% | 50% | 59 → 100 [stray 50 → 0] (100, 100, 100) | 59 → 100 [stray 50 → 0] (100, 100, 100) | 59 → 100 [stray 50 → 0] (100, 100, 100) | 59 → 12 [stray 50 → 88] (0, 100, 2) | 59 → 9 [stray 50 → 91] (0, 100, 1) |

## Drawings, evaluation alphabets, 4,000 cells: completion under damage

Each cell: overlap of raw cue → overlap of settled state, in percent; for
stray-cell damage, stray share of raw cue → settled; then exact recall, the
ideal lookup from the raw cue and the same lookup from the settled state, in
percent.

### Pseudo-inverse

| removed | stray added | load 20: cue → settled (exact, lookup cue, lookup settled) | load 100: cue → settled (exact, lookup cue, lookup settled) | load 200: cue → settled (exact, lookup cue, lookup settled) | load 500: cue → settled (exact, lookup cue, lookup settled) | load 659: cue → settled (exact, lookup cue, lookup settled) |
|---|---|---|---|---|---|---|
| 0% | 0% | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) |
| 20% | 0% | 80 → 100 (94, 100, 100) | 80 → 100 (95, 100, 100) | 80 → 100 (95, 100, 100) | 80 → 100 (95, 100, 100) | 80 → 100 (95, 100, 100) |
| 40% | 0% | 60 → 100 (89, 100, 100) | 60 → 100 (90, 100, 100) | 60 → 100 (89, 100, 100) | 60 → 100 (87, 100, 100) | 60 → 100 (87, 100, 100) |
| 60% | 0% | 40 → 0 (0, 100, 12) | 40 → 0 (0, 100, 3) | 40 → 0 (0, 100, 2) | 40 → 0 (0, 100, 1) | 40 → 0 (0, 100, 1) |
| 80% | 0% | 20 → 0 (0, 100, 10) | 20 → 0 (0, 100, 2) | 20 → 0 (0, 100, 1) | 20 → 0 (0, 100, 1) | 20 → 0 (0, 100, 0) |
| 0% | 25% | 100 → 100 [stray 25 → 0] (96, 100, 100) | 100 → 100 [stray 25 → 0] (95, 100, 100) | 100 → 100 [stray 25 → 0] (94, 100, 100) | 100 → 100 [stray 25 → 0] (92, 100, 100) | 100 → 100 [stray 25 → 0] (93, 100, 100) |
| 0% | 50% | 100 → 100 [stray 50 → 0] (90, 100, 100) | 100 → 100 [stray 50 → 0] (91, 100, 100) | 100 → 100 [stray 50 → 0] (87, 100, 100) | 100 → 100 [stray 50 → 0] (86, 100, 100) | 100 → 100 [stray 50 → 0] (88, 100, 100) |
| 0% | 100% | 100 → 100 [stray 100 → 0] (71, 100, 100) | 100 → 100 [stray 100 → 0] (81, 100, 100) | 100 → 100 [stray 100 → 0] (76, 100, 100) | 100 → 100 [stray 100 → 0] (73, 100, 100) | 100 → 100 [stray 100 → 0] (80, 100, 100) |
| 40% | 50% | 60 → 100 [stray 50 → 0] (83, 100, 100) | 60 → 100 [stray 50 → 0] (83, 100, 100) | 60 → 100 [stray 50 → 0] (76, 100, 100) | 60 → 100 [stray 50 → 0] (73, 100, 100) | 60 → 100 [stray 50 → 0] (73, 100, 100) |

### Covariance

| removed | stray added | load 20: cue → settled (exact, lookup cue, lookup settled) | load 100: cue → settled (exact, lookup cue, lookup settled) | load 200: cue → settled (exact, lookup cue, lookup settled) | load 500: cue → settled (exact, lookup cue, lookup settled) | load 659: cue → settled (exact, lookup cue, lookup settled) |
|---|---|---|---|---|---|---|
| 0% | 0% | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) | 100 → 100 (99, 100, 100) | 100 → 43 (17, 100, 37) | 100 → 22 (4, 100, 13) |
| 20% | 0% | 80 → 100 (100, 100, 100) | 80 → 100 (100, 100, 100) | 80 → 100 (99, 100, 100) | 80 → 43 (16, 100, 36) | 80 → 21 (3, 100, 12) |
| 40% | 0% | 60 → 100 (100, 100, 100) | 60 → 100 (100, 100, 100) | 60 → 100 (99, 100, 100) | 60 → 43 (16, 100, 36) | 60 → 20 (3, 100, 11) |
| 60% | 0% | 40 → 100 (100, 100, 100) | 40 → 100 (100, 100, 100) | 40 → 100 (99, 100, 100) | 40 → 41 (15, 100, 34) | 40 → 20 (3, 100, 10) |
| 80% | 0% | 20 → 100 (100, 100, 100) | 20 → 100 (100, 100, 100) | 20 → 100 (99, 100, 100) | 20 → 36 (14, 100, 29) | 20 → 18 (2, 100, 8) |
| 0% | 25% | 100 → 100 [stray 25 → 0] (100, 100, 100) | 100 → 100 [stray 25 → 0] (100, 100, 100) | 100 → 100 [stray 25 → 0] (99, 100, 100) | 100 → 43 [stray 25 → 57] (16, 100, 36) | 100 → 21 [stray 25 → 79] (3, 100, 12) |
| 0% | 50% | 100 → 100 [stray 50 → 0] (100, 100, 100) | 100 → 100 [stray 50 → 0] (100, 100, 100) | 100 → 100 [stray 50 → 0] (99, 100, 100) | 100 → 43 [stray 50 → 57] (16, 100, 36) | 100 → 21 [stray 50 → 79] (3, 100, 12) |
| 0% | 100% | 100 → 100 [stray 100 → 0] (100, 100, 100) | 100 → 100 [stray 100 → 0] (100, 100, 100) | 100 → 100 [stray 100 → 0] (99, 100, 100) | 100 → 42 [stray 100 → 58] (15, 100, 35) | 100 → 21 [stray 100 → 79] (3, 100, 11) |
| 40% | 50% | 60 → 100 [stray 50 → 0] (100, 100, 100) | 60 → 100 [stray 50 → 0] (100, 100, 100) | 60 → 100 [stray 50 → 0] (99, 100, 100) | 60 → 40 [stray 50 → 60] (15, 100, 33) | 60 → 19 [stray 50 → 81] (2, 100, 9) |

### Clipped binary

| removed | stray added | load 20: cue → settled (exact, lookup cue, lookup settled) | load 100: cue → settled (exact, lookup cue, lookup settled) | load 200: cue → settled (exact, lookup cue, lookup settled) | load 500: cue → settled (exact, lookup cue, lookup settled) | load 659: cue → settled (exact, lookup cue, lookup settled) |
|---|---|---|---|---|---|---|
| 0% | 0% | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) | 100 → 100 (100, 100, 100) | 100 → 100 (94, 100, 100) |
| 20% | 0% | 80 → 100 (100, 100, 100) | 80 → 100 (100, 100, 100) | 80 → 100 (100, 100, 100) | 80 → 100 (100, 100, 100) | 80 → 100 (91, 100, 100) |
| 40% | 0% | 60 → 100 (100, 100, 100) | 60 → 100 (100, 100, 100) | 60 → 100 (100, 100, 100) | 60 → 100 (100, 100, 100) | 60 → 100 (89, 100, 100) |
| 60% | 0% | 40 → 100 (100, 100, 100) | 40 → 100 (100, 100, 100) | 40 → 100 (100, 100, 100) | 40 → 100 (100, 100, 100) | 40 → 99 (87, 100, 100) |
| 80% | 0% | 20 → 100 (100, 100, 100) | 20 → 100 (100, 100, 100) | 20 → 100 (100, 100, 100) | 20 → 100 (99, 100, 100) | 20 → 98 (85, 100, 100) |
| 0% | 25% | 100 → 100 [stray 25 → 0] (100, 100, 100) | 100 → 100 [stray 25 → 0] (100, 100, 100) | 100 → 100 [stray 25 → 0] (100, 100, 100) | 100 → 100 [stray 25 → 0] (100, 100, 100) | 100 → 71 [stray 25 → 29] (57, 100, 76) |
| 0% | 50% | 100 → 100 [stray 50 → 0] (100, 100, 100) | 100 → 100 [stray 50 → 0] (100, 100, 100) | 100 → 100 [stray 50 → 0] (100, 100, 100) | 100 → 80 [stray 50 → 20] (71, 100, 80) | 100 → 13 [stray 50 → 87] (1, 100, 4) |
| 0% | 100% | 100 → 100 [stray 100 → 0] (100, 100, 100) | 100 → 100 [stray 100 → 0] (100, 100, 100) | 100 → 100 [stray 100 → 0] (100, 100, 100) | 100 → 10 [stray 100 → 90] (0, 100, 1) | 100 → 10 [stray 100 → 90] (0, 100, 1) |
| 40% | 50% | 60 → 100 [stray 50 → 0] (100, 100, 100) | 60 → 100 [stray 50 → 0] (100, 100, 100) | 60 → 100 [stray 50 → 0] (100, 100, 100) | 60 → 11 [stray 50 → 89] (0, 100, 1) | 60 → 10 [stray 50 → 90] (0, 100, 1) |

## CA1 reconstruction from the settled state and from the raw cue

Drawings from the evaluation alphabets, 225 cells. CA1 is trained on the stored
patterns as AHA trains it. Each cell lists CA1 error from the raw cue, from the
settled state, from the pattern the ideal lookup picks, and from the right stored
pattern itself (the floor), then the error of the mean stored drawing, the best
guess with no memory at all. Lower is better.

### Pseudo-inverse

| removed | stray added | load 20: cue, settled, lookup, perfect, mean drawing | load 50: cue, settled, lookup, perfect, mean drawing | load 100: cue, settled, lookup, perfect, mean drawing | load 200: cue, settled, lookup, perfect, mean drawing | load 500: cue, settled, lookup, perfect, mean drawing | load 659: cue, settled, lookup, perfect, mean drawing |
|---|---|---|---|---|---|---|---|
| 0% | 0% | 0.0020, 0.0021, 0.0020, 0.0020, 0.0434 | 0.0189, 0.0190, 0.0189, 0.0189, 0.0433 | 0.0331, 0.0331, 0.0331, 0.0331, 0.0437 | 0.0394, 0.0394, 0.0394, 0.0394, 0.0441 | 0.0417, 0.0417, 0.0417, 0.0417, 0.0441 | 0.0424, 0.0425, 0.0424, 0.0424, 0.0446 |
| 20% | 0% | 0.0055, 0.0022, 0.0020, 0.0020, 0.0434 | 0.0222, 0.0190, 0.0189, 0.0189, 0.0433 | 0.0347, 0.0332, 0.0331, 0.0331, 0.0437 | 0.0402, 0.0402, 0.0394, 0.0394, 0.0441 | 0.0421, 0.0421, 0.0417, 0.0417, 0.0441 | 0.0429, 0.0429, 0.0424, 0.0424, 0.0446 |
| 40% | 0% | 0.0115, 0.0034, 0.0020, 0.0020, 0.0434 | 0.0262, 0.0199, 0.0189, 0.0189, 0.0433 | 0.0367, 0.0338, 0.0331, 0.0331, 0.0437 | 0.0411, 0.0412, 0.0394, 0.0394, 0.0441 | 0.0426, 0.0426, 0.0417, 0.0417, 0.0441 | 0.0433, 0.0433, 0.0424, 0.0424, 0.0446 |
| 60% | 0% | 0.0199, 0.0397, 0.0020, 0.0020, 0.0434 | 0.0313, 0.0428, 0.0189, 0.0189, 0.0433 | 0.0390, 0.0429, 0.0331, 0.0331, 0.0437 | 0.0422, 0.0422, 0.0394, 0.0394, 0.0441 | 0.0432, 0.0432, 0.0417, 0.0417, 0.0441 | 0.0438, 0.0438, 0.0424, 0.0424, 0.0446 |
| 80% | 0% | 0.0309, 0.0443, 0.0020, 0.0020, 0.0434 | 0.0373, 0.0441, 0.0200, 0.0189, 0.0433 | 0.0415, 0.0441, 0.0344, 0.0331, 0.0437 | 0.0433, 0.0433, 0.0404, 0.0394, 0.0441 | 0.0438, 0.0438, 0.0426, 0.0417, 0.0441 | 0.0444, 0.0444, 0.0435, 0.0424, 0.0446 |
| 0% | 25% | 0.0029, 0.0021, 0.0020, 0.0020, 0.0434 | 0.0199, 0.0190, 0.0189, 0.0189, 0.0433 | 0.0336, 0.0331, 0.0331, 0.0331, 0.0437 | 0.0397, 0.0397, 0.0394, 0.0394, 0.0441 | 0.0418, 0.0418, 0.0417, 0.0417, 0.0441 | 0.0425, 0.0426, 0.0424, 0.0424, 0.0446 |
| 0% | 50% | 0.0034, 0.0021, 0.0020, 0.0020, 0.0434 | 0.0204, 0.0190, 0.0189, 0.0189, 0.0433 | 0.0339, 0.0331, 0.0331, 0.0331, 0.0437 | 0.0398, 0.0398, 0.0394, 0.0394, 0.0441 | 0.0419, 0.0419, 0.0417, 0.0417, 0.0441 | 0.0426, 0.0427, 0.0424, 0.0424, 0.0446 |
| 0% | 100% | 0.0047, 0.0021, 0.0020, 0.0020, 0.0434 | 0.0219, 0.0190, 0.0189, 0.0189, 0.0433 | 0.0347, 0.0332, 0.0331, 0.0331, 0.0437 | 0.0402, 0.0402, 0.0394, 0.0394, 0.0441 | 0.0422, 0.0422, 0.0417, 0.0417, 0.0441 | 0.0429, 0.0429, 0.0424, 0.0424, 0.0446 |
| 40% | 50% | 0.0138, 0.0042, 0.0020, 0.0020, 0.0434 | 0.0281, 0.0202, 0.0189, 0.0189, 0.0433 | 0.0375, 0.0340, 0.0331, 0.0331, 0.0437 | 0.0415, 0.0415, 0.0394, 0.0394, 0.0441 | 0.0429, 0.0429, 0.0417, 0.0417, 0.0441 | 0.0435, 0.0435, 0.0424, 0.0424, 0.0446 |

### Covariance

| removed | stray added | load 20: cue, settled, lookup, perfect, mean drawing | load 50: cue, settled, lookup, perfect, mean drawing | load 100: cue, settled, lookup, perfect, mean drawing | load 200: cue, settled, lookup, perfect, mean drawing | load 500: cue, settled, lookup, perfect, mean drawing | load 659: cue, settled, lookup, perfect, mean drawing |
|---|---|---|---|---|---|---|---|
| 0% | 0% | 0.0046, 0.0046, 0.0046, 0.0046, 0.0434 | 0.0226, 0.0226, 0.0226, 0.0226, 0.0433 | 0.0363, 0.0364, 0.0363, 0.0363, 0.0437 | 0.0413, 0.0418, 0.0413, 0.0413, 0.0441 | 0.0427, 0.0435, 0.0427, 0.0427, 0.0441 | 0.0434, 0.0442, 0.0434, 0.0434, 0.0446 |
| 20% | 0% | 0.0092, 0.0046, 0.0046, 0.0046, 0.0434 | 0.0261, 0.0226, 0.0226, 0.0226, 0.0433 | 0.0378, 0.0364, 0.0363, 0.0363, 0.0437 | 0.0420, 0.0420, 0.0413, 0.0413, 0.0441 | 0.0432, 0.0435, 0.0427, 0.0427, 0.0441 | 0.0439, 0.0443, 0.0434, 0.0434, 0.0446 |
| 40% | 0% | 0.0157, 0.0046, 0.0046, 0.0046, 0.0434 | 0.0300, 0.0226, 0.0226, 0.0226, 0.0433 | 0.0395, 0.0365, 0.0363, 0.0363, 0.0437 | 0.0429, 0.0423, 0.0413, 0.0413, 0.0441 | 0.0439, 0.0436, 0.0427, 0.0427, 0.0441 | 0.0445, 0.0443, 0.0434, 0.0434, 0.0446 |
| 60% | 0% | 0.0240, 0.0046, 0.0046, 0.0046, 0.0434 | 0.0347, 0.0226, 0.0226, 0.0226, 0.0433 | 0.0415, 0.0369, 0.0363, 0.0363, 0.0437 | 0.0440, 0.0426, 0.0413, 0.0413, 0.0441 | 0.0447, 0.0438, 0.0427, 0.0427, 0.0441 | 0.0452, 0.0445, 0.0434, 0.0434, 0.0446 |
| 80% | 0% | 0.0344, 0.0046, 0.0046, 0.0046, 0.0434 | 0.0399, 0.0239, 0.0234, 0.0226, 0.0433 | 0.0437, 0.0388, 0.0372, 0.0363, 0.0437 | 0.0453, 0.0434, 0.0418, 0.0413, 0.0441 | 0.0457, 0.0441, 0.0432, 0.0427, 0.0441 | 0.0462, 0.0446, 0.0439, 0.0434, 0.0446 |
| 0% | 25% | 0.0054, 0.0046, 0.0046, 0.0046, 0.0434 | 0.0233, 0.0226, 0.0226, 0.0226, 0.0433 | 0.0365, 0.0364, 0.0363, 0.0363, 0.0437 | 0.0414, 0.0420, 0.0413, 0.0413, 0.0441 | 0.0427, 0.0435, 0.0427, 0.0427, 0.0441 | 0.0434, 0.0443, 0.0434, 0.0434, 0.0446 |
| 0% | 50% | 0.0060, 0.0046, 0.0046, 0.0046, 0.0434 | 0.0237, 0.0226, 0.0226, 0.0226, 0.0433 | 0.0368, 0.0364, 0.0363, 0.0363, 0.0437 | 0.0415, 0.0421, 0.0413, 0.0413, 0.0441 | 0.0429, 0.0436, 0.0427, 0.0427, 0.0441 | 0.0435, 0.0442, 0.0434, 0.0434, 0.0446 |
| 0% | 100% | 0.0076, 0.0046, 0.0046, 0.0046, 0.0434 | 0.0253, 0.0226, 0.0226, 0.0226, 0.0433 | 0.0378, 0.0365, 0.0363, 0.0363, 0.0437 | 0.0424, 0.0423, 0.0413, 0.0413, 0.0441 | 0.0436, 0.0437, 0.0427, 0.0427, 0.0441 | 0.0443, 0.0443, 0.0434, 0.0434, 0.0446 |
| 40% | 50% | 0.0170, 0.0046, 0.0046, 0.0046, 0.0434 | 0.0307, 0.0226, 0.0226, 0.0226, 0.0433 | 0.0394, 0.0369, 0.0363, 0.0363, 0.0437 | 0.0426, 0.0428, 0.0413, 0.0413, 0.0441 | 0.0434, 0.0439, 0.0427, 0.0427, 0.0441 | 0.0440, 0.0446, 0.0434, 0.0434, 0.0446 |

### Clipped binary

| removed | stray added | load 20: cue, settled, lookup, perfect, mean drawing | load 50: cue, settled, lookup, perfect, mean drawing | load 100: cue, settled, lookup, perfect, mean drawing | load 200: cue, settled, lookup, perfect, mean drawing | load 500: cue, settled, lookup, perfect, mean drawing | load 659: cue, settled, lookup, perfect, mean drawing |
|---|---|---|---|---|---|---|---|
| 0% | 0% | 0.0046, 0.0046, 0.0046, 0.0046, 0.0434 | 0.0226, 0.0226, 0.0226, 0.0226, 0.0433 | 0.0363, 0.0363, 0.0363, 0.0363, 0.0437 | 0.0413, 0.0415, 0.0413, 0.0413, 0.0441 | 0.0427, 0.0441, 0.0427, 0.0427, 0.0441 | 0.0434, 0.0446, 0.0434, 0.0434, 0.0446 |
| 20% | 0% | 0.0092, 0.0046, 0.0046, 0.0046, 0.0434 | 0.0261, 0.0226, 0.0226, 0.0226, 0.0433 | 0.0378, 0.0363, 0.0363, 0.0363, 0.0437 | 0.0420, 0.0417, 0.0413, 0.0413, 0.0441 | 0.0432, 0.0441, 0.0427, 0.0427, 0.0441 | 0.0439, 0.0446, 0.0434, 0.0434, 0.0446 |
| 40% | 0% | 0.0157, 0.0046, 0.0046, 0.0046, 0.0434 | 0.0300, 0.0226, 0.0226, 0.0226, 0.0433 | 0.0395, 0.0363, 0.0363, 0.0363, 0.0437 | 0.0429, 0.0422, 0.0413, 0.0413, 0.0441 | 0.0439, 0.0440, 0.0427, 0.0427, 0.0441 | 0.0445, 0.0446, 0.0434, 0.0434, 0.0446 |
| 60% | 0% | 0.0240, 0.0046, 0.0046, 0.0046, 0.0434 | 0.0347, 0.0226, 0.0226, 0.0226, 0.0433 | 0.0415, 0.0364, 0.0363, 0.0363, 0.0437 | 0.0440, 0.0428, 0.0413, 0.0413, 0.0441 | 0.0447, 0.0440, 0.0427, 0.0427, 0.0441 | 0.0452, 0.0446, 0.0434, 0.0434, 0.0446 |
| 80% | 0% | 0.0344, 0.0048, 0.0046, 0.0046, 0.0434 | 0.0399, 0.0237, 0.0234, 0.0226, 0.0433 | 0.0437, 0.0381, 0.0372, 0.0363, 0.0437 | 0.0453, 0.0438, 0.0418, 0.0413, 0.0441 | 0.0457, 0.0441, 0.0432, 0.0427, 0.0441 | 0.0462, 0.0445, 0.0439, 0.0434, 0.0446 |
| 0% | 25% | 0.0054, 0.0046, 0.0046, 0.0046, 0.0434 | 0.0233, 0.0226, 0.0226, 0.0226, 0.0433 | 0.0365, 0.0363, 0.0363, 0.0363, 0.0437 | 0.0414, 0.0420, 0.0413, 0.0413, 0.0441 | 0.0427, 0.0442, 0.0427, 0.0427, 0.0441 | 0.0434, 0.0446, 0.0434, 0.0434, 0.0446 |
| 0% | 50% | 0.0060, 0.0046, 0.0046, 0.0046, 0.0434 | 0.0237, 0.0226, 0.0226, 0.0226, 0.0433 | 0.0368, 0.0363, 0.0363, 0.0363, 0.0437 | 0.0415, 0.0424, 0.0413, 0.0413, 0.0441 | 0.0429, 0.0442, 0.0427, 0.0427, 0.0441 | 0.0435, 0.0447, 0.0434, 0.0434, 0.0446 |
| 0% | 100% | 0.0076, 0.0046, 0.0046, 0.0046, 0.0434 | 0.0253, 0.0226, 0.0226, 0.0226, 0.0433 | 0.0378, 0.0364, 0.0363, 0.0363, 0.0437 | 0.0424, 0.0434, 0.0413, 0.0413, 0.0441 | 0.0436, 0.0443, 0.0427, 0.0427, 0.0441 | 0.0443, 0.0447, 0.0434, 0.0434, 0.0446 |
| 40% | 50% | 0.0170, 0.0046, 0.0046, 0.0046, 0.0434 | 0.0307, 0.0226, 0.0226, 0.0226, 0.0433 | 0.0394, 0.0366, 0.0363, 0.0363, 0.0437 | 0.0426, 0.0435, 0.0413, 0.0413, 0.0441 | 0.0434, 0.0442, 0.0427, 0.0427, 0.0441 | 0.0440, 0.0447, 0.0434, 0.0434, 0.0446 |

## Check: background-alphabet drawings

The same harness on DG patterns of background-alphabet drawings, 5 seeds. No
setting was chosen from these runs.

| cells, on | load | Pseudo-inverse clean | Covariance clean | Clipped binary clean | Pseudo-inverse 40% removed | Covariance 40% removed | Clipped binary 40% removed | Ideal lookup 40% removed |
|---|---|---|---|---|---|---|---|---|
| 225, 10 | 20 | 100.0 | 100.0 | 100.0 | 96.0 | 100.0 | 100.0 | 100.0 |
| 225, 10 | 50 | 100.0 | 100.0 | 100.0 | 96.8 | 100.0 | 100.0 | 100.0 |
| 225, 10 | 100 | 100.0 | 96.8 | 99.8 | 60.4 | 89.8 | 96.6 | 100.0 |
| 225, 10 | 200 | 100.0 | 46.3 | 74.4 | 0.0 | 17.7 | 21.3 | 100.0 |
| 225, 10 | 500 | 100.0 | 1.0 | 0.3 | 0.0 | 0.1 | 0.0 | 100.0 |
| 225, 10 | 964 | 100.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 |
| 1,000, 44 | 20 | 100.0 | 100.0 | 100.0 | 99.0 | 100.0 | 100.0 | 100.0 |
| 1,000, 44 | 50 | 100.0 | 100.0 | 100.0 | 96.4 | 100.0 | 100.0 | 100.0 |
| 1,000, 44 | 100 | 100.0 | 100.0 | 100.0 | 97.6 | 100.0 | 100.0 | 100.0 |
| 1,000, 44 | 200 | 100.0 | 95.2 | 100.0 | 96.6 | 92.8 | 100.0 | 100.0 |
| 1,000, 44 | 500 | 100.0 | 9.5 | 71.4 | 0.4 | 5.7 | 43.8 | 100.0 |
| 1,000, 44 | 964 | 100.0 | 0.0 | 0.6 | 0.0 | 0.0 | 0.0 | 100.0 |

- The alphabets hold 964 characters, so the largest load uses all 964, one drawing each.
- For the pseudo-inverse, loads of n or more (here 225 at 225 cells) make its weights the identity matrix: every state is a fixed point, so a clean cue counts as exact recall without any completion. Capacity below leaves those loads out.

## End to end: the full model at higher loads

The model studies N drawings, one each of N characters from the evaluation
alphabets, then recalls each from an occluded or noisy copy. 5 seeds; each seed
studies about 400 drawings in runs of N. Settled is CA3 accuracy with settling;
gap is settled minus no settling in points, paired by seed, with the seeds where
settling scored higher in brackets. No settling passes PR's 10 most active cells
straight on.

### Occlusion, matched test-to-study

| load | level | VC | PR | Pseudo-inverse settled | Pseudo-inverse gap | Covariance settled | Covariance gap | Clipped binary settled | Clipped binary gap | No settling |
|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 0 | 100.0 | 100.0 | 100.0 ± 0.0 | +0.0 (0/5) | 100.0 ± 0.0 | +0.0 (0/5) | 100.0 ± 0.0 | +0.0 (0/5) | 100.0 ± 0.0 |
| 20 | 0.3 | 99.5 | 99.3 | 99.3 ± 0.4 | +0.0 (1/5) | 99.2 ± 0.4 | -0.1 (0/5) | 99.3 ± 0.3 | +0.0 (0/5) | 99.3 ± 0.3 |
| 20 | 0.5 | 92.2 | 92.3 | 92.1 ± 1.1 | +0.1 (2/5) | 92.1 ± 1.4 | +0.0 (0/5) | 92.1 ± 1.4 | +0.0 (0/5) | 92.1 ± 1.4 |
| 20 | 0.7 | 52.4 | 53.4 | 49.9 ± 3.4 | -3.6 (0/5) | 53.4 ± 3.5 | -0.1 (1/5) | 53.6 ± 3.5 | +0.1 (3/5) | 53.5 ± 3.4 |
| 100 | 0 | 100.0 | 100.0 | 100.0 ± 0.0 | +0.0 (0/5) | 99.5 ± 0.4 | -0.5 (0/5) | 100.0 ± 0.0 | +0.0 (0/5) | 100.0 ± 0.0 |
| 100 | 0.3 | 99.5 | 98.2 | 97.8 ± 0.4 | +0.2 (3/5) | 94.6 ± 0.9 | -3.0 (0/5) | 96.9 ± 0.5 | -0.6 (0/5) | 97.6 ± 0.9 |
| 100 | 0.5 | 88.0 | 79.7 | 76.6 ± 2.1 | -0.4 (1/5) | 69.3 ± 2.0 | -7.8 (0/5) | 72.2 ± 2.6 | -4.8 (0/5) | 77.0 ± 1.6 |
| 100 | 0.7 | 37.9 | 27.2 | 22.6 ± 3.1 | -2.3 (0/5) | 20.8 ± 2.8 | -4.1 (0/5) | 21.5 ± 3.7 | -3.4 (0/5) | 24.9 ± 3.6 |
| 200 | 0 | 100.0 | 100.0 | 100.0 ± 0.0 | +0.0 (0/5) | 76.8 ± 3.3 | -23.2 (0/5) | 97.9 ± 1.1 | -2.1 (0/5) | 100.0 ± 0.0 |
| 200 | 0.3 | 99.3 | 97.8 | 96.6 ± 1.0 | +0.5 (4/5) | 62.5 ± 2.0 | -33.6 (0/5) | 81.4 ± 4.8 | -14.7 (0/5) | 96.1 ± 0.9 |
| 200 | 0.5 | 85.0 | 69.4 | 65.1 ± 3.8 | +0.7 (4/5) | 31.0 ± 2.3 | -33.4 (0/5) | 35.2 ± 2.9 | -29.1 (0/5) | 64.4 ± 2.8 |
| 200 | 0.7 | 30.7 | 16.4 | 15.4 ± 1.5 | -0.2 (1/5) | 7.0 ± 1.2 | -8.7 (0/5) | 6.4 ± 2.1 | -9.3 (0/5) | 15.7 ± 2.1 |

### Occlusion, matched study-to-test

| load | level | VC | PR | Pseudo-inverse settled | Pseudo-inverse gap | Covariance settled | Covariance gap | Clipped binary settled | Clipped binary gap | No settling |
|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 0 | 100.0 | 100.0 | 100.0 ± 0.0 | +0.0 (0/5) | 100.0 ± 0.0 | +0.0 (0/5) | 100.0 ± 0.0 | +0.0 (0/5) | 100.0 ± 0.0 |
| 20 | 0.3 | 99.4 | 99.9 | 99.4 ± 0.3 | +0.2 (4/5) | 98.9 ± 0.5 | -0.4 (0/5) | 99.0 ± 0.5 | -0.3 (0/5) | 99.2 ± 0.2 |
| 20 | 0.5 | 87.0 | 96.9 | 93.5 ± 1.2 | +0.3 (4/5) | 88.9 ± 2.3 | -4.4 (0/5) | 88.9 ± 2.3 | -4.4 (0/5) | 93.3 ± 1.0 |
| 20 | 0.7 | 22.8 | 60.2 | 51.9 ± 2.7 | -1.2 (1/5) | 44.4 ± 3.2 | -8.6 (0/5) | 44.6 ± 3.1 | -8.4 (0/5) | 53.0 ± 4.6 |
| 100 | 0 | 100.0 | 100.0 | 100.0 ± 0.0 | +0.0 (0/5) | 99.9 ± 0.1 | -0.1 (0/5) | 100.0 ± 0.0 | +0.0 (0/5) | 100.0 ± 0.0 |
| 100 | 0.3 | 98.3 | 99.2 | 99.0 ± 0.3 | +0.2 (2/5) | 94.7 ± 1.0 | -4.1 (0/5) | 96.8 ± 1.0 | -2.0 (0/5) | 98.8 ± 0.5 |
| 100 | 0.5 | 80.9 | 83.5 | 78.6 ± 2.4 | -2.7 (0/5) | 65.0 ± 1.9 | -16.3 (0/5) | 69.0 ± 2.0 | -12.3 (0/5) | 81.3 ± 2.3 |
| 100 | 0.7 | 10.5 | 34.3 | 22.1 ± 2.2 | -6.3 (0/5) | 16.4 ± 2.1 | -11.9 (0/5) | 18.4 ± 3.3 | -10.0 (0/5) | 28.4 ± 3.2 |
| 200 | 0 | 100.0 | 100.0 | 100.0 ± 0.0 | +0.0 (0/5) | 81.4 ± 4.4 | -18.6 (0/5) | 98.6 ± 0.8 | -1.4 (0/5) | 100.0 ± 0.0 |
| 200 | 0.3 | 98.2 | 98.4 | 98.1 ± 0.9 | +0.7 (3/5) | 66.7 ± 2.4 | -30.7 (0/5) | 83.7 ± 3.9 | -13.7 (0/5) | 97.4 ± 1.5 |
| 200 | 0.5 | 76.3 | 73.7 | 67.6 ± 3.4 | +0.1 (2/5) | 32.5 ± 2.7 | -35.0 (0/5) | 38.2 ± 3.6 | -29.3 (0/5) | 67.5 ± 3.1 |
| 200 | 0.7 | 7.5 | 25.0 | 15.0 ± 1.9 | -2.6 (0/5) | 5.9 ± 1.2 | -11.6 (0/5) | 7.2 ± 1.7 | -10.4 (0/5) | 17.6 ± 2.5 |

### Occlusion: CA3 states and recall-loss

PR top cells overlap is the share of the right stored pattern's 10 cells
among PR's 10 most active cells, which is where settling starts. Settled
overlap and exact recall follow, then test-to-study accuracy when the
covariance rule settles from the PR output as given. Recall-loss is CA1's
error against the clean drawing.

| load | level | PR top cells overlap | Pseudo-inverse settled overlap, exact | Covariance settled overlap, exact | Clipped binary settled overlap, exact | Covariance from PR as given, test-to-study | Recall-loss no settling | Recall-loss Pseudo-inverse | Recall-loss Covariance | Recall-loss Clipped binary |
|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 0 | 100.0 | 100.0, 100.0 | 100.0, 100.0 | 100.0, 100.0 | 100.0 | 0.0045 | 0.0023 | 0.0045 | 0.0045 |
| 20 | 0.3 | 99.1 | 99.4, 99.0 | 99.3, 99.2 | 99.3, 99.2 | 99.3 | 0.0049 | 0.0027 | 0.0048 | 0.0048 |
| 20 | 0.5 | 91.5 | 91.5, 90.3 | 92.3, 92.0 | 92.4, 92.1 | 92.0 | 0.0078 | 0.0064 | 0.0081 | 0.0080 |
| 20 | 0.7 | 53.5 | 47.5, 45.3 | 54.6, 53.3 | 54.8, 53.4 | 53.0 | 0.0254 | 0.0269 | 0.0279 | 0.0279 |
| 100 | 0 | 100.0 | 100.0, 100.0 | 99.2, 95.9 | 100.0, 99.8 | 99.1 | 0.0367 | 0.0340 | 0.0368 | 0.0367 |
| 100 | 0.3 | 94.1 | 97.6, 93.6 | 95.0, 89.7 | 97.0, 95.5 | 94.0 | 0.0369 | 0.0342 | 0.0370 | 0.0369 |
| 100 | 0.5 | 66.9 | 75.9, 60.4 | 72.4, 62.2 | 74.9, 68.0 | 66.8 | 0.0382 | 0.0361 | 0.0385 | 0.0382 |
| 100 | 0.7 | 26.2 | 27.4, 8.7 | 26.8, 17.5 | 27.7, 19.3 | 17.3 | 0.0413 | 0.0424 | 0.0422 | 0.0420 |
| 200 | 0 | 98.7 | 99.2, 92.1 | 78.3, 44.3 | 91.5, 67.6 | 71.8 | 0.0410 | 0.0390 | 0.0414 | 0.0412 |
| 200 | 0.3 | 86.0 | 88.2, 47.0 | 66.9, 30.2 | 74.2, 40.9 | 57.7 | 0.0411 | 0.0391 | 0.0417 | 0.0416 |
| 200 | 0.5 | 52.3 | 53.3, 5.3 | 39.9, 9.9 | 37.4, 10.4 | 29.7 | 0.0414 | 0.0400 | 0.0422 | 0.0424 |
| 200 | 0.7 | 19.9 | 21.0, 0.1 | 15.7, 2.2 | 14.1, 1.4 | 6.4 | 0.0424 | 0.0426 | 0.0431 | 0.0432 |

### Noise, matched test-to-study

| load | level | VC | PR | Pseudo-inverse settled | Pseudo-inverse gap | Covariance settled | Covariance gap | Clipped binary settled | Clipped binary gap | No settling |
|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 0 | 100.0 | 100.0 | 100.0 ± 0.0 | +0.0 (0/5) | 100.0 ± 0.0 | +0.0 (0/5) | 100.0 ± 0.0 | +0.0 (0/5) | 100.0 ± 0.0 |
| 20 | 0.3 | 91.7 | 81.4 | 73.7 ± 3.5 | -6.9 (0/5) | 80.9 ± 2.3 | +0.3 (2/5) | 80.6 ± 2.3 | -0.1 (1/5) | 80.7 ± 1.8 |
| 20 | 0.5 | 42.1 | 21.8 | 17.0 ± 1.5 | -5.3 (0/5) | 22.6 ± 3.3 | +0.3 (4/5) | 22.3 ± 3.1 | +0.0 (2/5) | 22.3 ± 3.2 |
| 20 | 0.7 | 12.4 | 6.8 | 7.1 ± 0.8 | -0.2 (3/5) | 7.2 ± 1.1 | -0.1 (2/5) | 7.2 ± 1.3 | -0.1 (0/5) | 7.3 ± 1.4 |
| 100 | 0 | 100.0 | 100.0 | 100.0 ± 0.0 | +0.0 (0/5) | 99.5 ± 0.4 | -0.5 (0/5) | 100.0 ± 0.0 | +0.0 (0/5) | 100.0 ± 0.0 |
| 100 | 0.3 | 81.5 | 46.0 | 35.3 ± 2.3 | -6.8 (0/5) | 30.1 ± 2.8 | -12.1 (0/5) | 33.1 ± 2.4 | -9.1 (0/5) | 42.1 ± 3.1 |
| 100 | 0.5 | 20.3 | 3.8 | 3.7 ± 1.1 | -2.2 (0/5) | 4.2 ± 1.1 | -1.7 (0/5) | 4.2 ± 0.6 | -1.7 (0/5) | 5.9 ± 1.3 |
| 100 | 0.7 | 2.9 | 1.5 | 1.8 ± 0.4 | -0.0 (3/5) | 1.6 ± 0.4 | -0.2 (1/5) | 1.7 ± 0.2 | -0.1 (2/5) | 1.8 ± 0.6 |
| 200 | 0 | 100.0 | 100.0 | 100.0 ± 0.0 | +0.0 (0/5) | 76.8 ± 3.3 | -23.2 (0/5) | 97.9 ± 1.1 | -2.1 (0/5) | 100.0 ± 0.0 |
| 200 | 0.3 | 74.5 | 21.4 | 25.9 ± 4.0 | -0.6 (2/5) | 7.8 ± 2.1 | -18.8 (0/5) | 8.1 ± 1.3 | -18.5 (0/5) | 26.6 ± 3.5 |
| 200 | 0.5 | 13.2 | 0.8 | 2.0 ± 1.0 | -0.7 (2/5) | 1.0 ± 0.5 | -1.7 (0/5) | 1.4 ± 0.5 | -1.4 (0/5) | 2.7 ± 0.9 |
| 200 | 0.7 | 1.3 | 0.5 | 0.6 ± 0.3 | -0.1 (0/5) | 0.8 ± 0.2 | +0.1 (3/5) | 0.6 ± 0.2 | -0.0 (2/5) | 0.7 ± 0.2 |

### Noise, matched study-to-test

| load | level | VC | PR | Pseudo-inverse settled | Pseudo-inverse gap | Covariance settled | Covariance gap | Clipped binary settled | Clipped binary gap | No settling |
|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 0 | 100.0 | 100.0 | 100.0 ± 0.0 | +0.0 (0/5) | 100.0 ± 0.0 | +0.0 (0/5) | 100.0 ± 0.0 | +0.0 (0/5) | 100.0 ± 0.0 |
| 20 | 0.3 | 86.9 | 96.4 | 80.8 ± 2.7 | -7.6 (0/5) | 75.6 ± 2.7 | -12.7 (0/5) | 75.6 ± 2.8 | -12.7 (0/5) | 88.3 ± 1.8 |
| 20 | 0.5 | 40.8 | 52.5 | 23.1 ± 2.6 | -7.0 (0/5) | 18.5 ± 3.3 | -11.6 (0/5) | 18.5 ± 3.6 | -11.6 (0/5) | 30.1 ± 3.5 |
| 20 | 0.7 | 13.5 | 16.3 | 8.1 ± 0.9 | -0.5 (2/5) | 5.9 ± 0.4 | -2.7 (0/5) | 5.8 ± 0.2 | -2.8 (0/5) | 8.6 ± 1.1 |
| 100 | 0 | 100.0 | 100.0 | 100.0 ± 0.0 | +0.0 (0/5) | 99.9 ± 0.1 | -0.1 (0/5) | 100.0 ± 0.0 | +0.0 (0/5) | 100.0 ± 0.0 |
| 100 | 0.3 | 70.9 | 67.3 | 36.5 ± 3.2 | -18.9 (0/5) | 27.8 ± 3.3 | -27.6 (0/5) | 30.1 ± 3.3 | -25.3 (0/5) | 55.4 ± 3.4 |
| 100 | 0.5 | 20.2 | 18.4 | 2.8 ± 0.7 | -6.4 (0/5) | 3.9 ± 0.9 | -5.3 (0/5) | 3.3 ± 0.7 | -5.9 (0/5) | 9.2 ± 0.9 |
| 100 | 0.7 | 5.5 | 3.6 | 1.3 ± 0.6 | -0.4 (2/5) | 1.4 ± 0.6 | -0.3 (2/5) | 1.1 ± 0.5 | -0.6 (1/5) | 1.7 ± 0.6 |
| 200 | 0 | 100.0 | 100.0 | 100.0 ± 0.0 | +0.0 (0/5) | 81.4 ± 4.4 | -18.6 (0/5) | 98.6 ± 0.8 | -1.4 (0/5) | 100.0 ± 0.0 |
| 200 | 0.3 | 64.0 | 50.8 | 24.7 ± 3.0 | -8.3 (0/5) | 8.4 ± 2.0 | -24.5 (0/5) | 9.7 ± 1.4 | -23.2 (0/5) | 33.0 ± 3.8 |
| 200 | 0.5 | 14.3 | 9.9 | 1.5 ± 0.6 | -2.0 (0/5) | 1.1 ± 0.5 | -2.3 (0/5) | 1.2 ± 0.3 | -2.2 (0/5) | 3.5 ± 1.0 |
| 200 | 0.7 | 2.7 | 1.9 | 0.6 ± 0.2 | -0.3 (1/5) | 0.6 ± 0.3 | -0.3 (1/5) | 0.4 ± 0.4 | -0.5 (0/5) | 0.9 ± 0.5 |

### Noise: CA3 states and recall-loss

PR top cells overlap is the share of the right stored pattern's 10 cells
among PR's 10 most active cells, which is where settling starts. Settled
overlap and exact recall follow, then test-to-study accuracy when the
covariance rule settles from the PR output as given. Recall-loss is CA1's
error against the clean drawing.

| load | level | PR top cells overlap | Pseudo-inverse settled overlap, exact | Covariance settled overlap, exact | Clipped binary settled overlap, exact | Covariance from PR as given, test-to-study | Recall-loss no settling | Recall-loss Pseudo-inverse | Recall-loss Covariance | Recall-loss Clipped binary |
|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 0 | 100.0 | 100.0, 100.0 | 100.0, 100.0 | 100.0, 100.0 | 100.0 | 0.0045 | 0.0023 | 0.0045 | 0.0045 |
| 20 | 0.3 | 77.5 | 69.2, 67.4 | 81.7, 80.7 | 81.4, 80.1 | 80.6 | 0.0134 | 0.0162 | 0.0140 | 0.0141 |
| 20 | 0.5 | 24.5 | 12.3, 10.1 | 24.4, 22.4 | 24.1, 22.0 | 23.0 | 0.0436 | 0.0466 | 0.0496 | 0.0499 |
| 20 | 0.7 | 9.9 | 5.1, 3.5 | 8.9, 7.2 | 8.9, 7.1 | 7.0 | 0.0548 | 0.0539 | 0.0610 | 0.0609 |
| 100 | 0 | 100.0 | 100.0, 100.0 | 99.2, 95.9 | 100.0, 99.8 | 99.1 | 0.0367 | 0.0340 | 0.0368 | 0.0367 |
| 100 | 0.3 | 38.7 | 37.2, 6.7 | 37.9, 23.6 | 40.3, 27.5 | 26.4 | 0.0398 | 0.0398 | 0.0411 | 0.0408 |
| 100 | 0.5 | 12.6 | 14.8, 0.0 | 10.8, 3.2 | 11.0, 3.0 | 4.4 | 0.0434 | 0.0458 | 0.0451 | 0.0448 |
| 100 | 0.7 | 6.8 | 13.1, 0.0 | 6.6, 1.1 | 7.2, 1.1 | 1.8 | 0.0450 | 0.0480 | 0.0464 | 0.0459 |
| 200 | 0 | 98.7 | 99.2, 92.1 | 78.3, 44.3 | 91.5, 67.6 | 71.8 | 0.0410 | 0.0390 | 0.0414 | 0.0412 |
| 200 | 0.3 | 28.8 | 28.8, 0.0 | 19.8, 1.8 | 16.8, 0.4 | 7.3 | 0.0419 | 0.0410 | 0.0429 | 0.0431 |
| 200 | 0.5 | 9.7 | 13.1, 0.0 | 9.0, 0.1 | 8.9, 0.0 | 1.6 | 0.0434 | 0.0443 | 0.0440 | 0.0438 |
| 200 | 0.7 | 5.6 | 10.7, 0.0 | 6.1, 0.1 | 7.2, 0.0 | 0.6 | 0.0444 | 0.0466 | 0.0448 | 0.0441 |
