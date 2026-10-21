# E1d results

E1d asks whether CA3's capacity per cell stops falling as the network grows once DG and
CA3 codes are as sparse as measured. It reruns E1c's CA3 test with the share of active
cells as a parameter. The protocol is `docs/e1d_protocol.md` and the numbers come from
`results/e1d_*.json`. Built by `scripts/make_e1d_table.py`.

Exact recall means CA3's final state is exactly the right stored pattern. The **50% load**
is the number of stored patterns at which mean exact recall falls through 50%, read between
the two tested loads around it on a log scale. Divided by the cell count it gives the
**load per cell**, shown in brackets. For the covariance rule and clipped binary synapses it
comes from clean cues. For the pseudo-inverse rule it comes from cues missing 40% of their
cells, because clean cues stay exact up to the cell count. "Above" means recall never fell
below 50% at the loads tested.

## Active cells at each share and size

The log-scaled code has k = round(c × log2 n) active cells with c = 2.0069, so that
k = 20 (2%) at 1,000 cells. At 1,000 cells the 2% and log-scaled codes are the same and run once.

| Share active | 225 cells | 1,000 cells | 4,000 cells | 16,000 cells |
|---|---|---|---|---|
| 4.4% (AHA) | 10 (4.44%) | 44 (4.40%) | 178 (4.45%) | 711 (4.44%) |
| 2% (rat DG) | 5 (2.22%) | 20 (2.00%) | 80 (2.00%) | 320 (2.00%) |
| 1% | 3 (1.33%), raised to 3 | 10 (1.00%) | 40 (1.00%) | 160 (1.00%) |
| log-scaled | 16 (7.11%) | 20 (2.00%) | 24 (0.60%) | 28 (0.17%) |

## Random patterns: 50% load and load per cell

Seeds: 10 at 225 cells, 10 at 1,000 cells, 5 at 4,000 cells, 1/2/4/5 at 16,000 cells.

### Pseudo-inverse, cues missing 40% of their cells

| Share active | 225 cells | 1,000 cells | 4,000 cells | 16,000 cells |
|---|---|---|---|---|
| 4.4% (AHA) | k = 10: 111 (0.49) | k = 44: 388 (0.39) | k = 178: 1,539 (0.38) | k = 711: 3,762 (0.24) |
| 2% (rat DG) | k = 5: 104 (0.46) | k = 20: 437 (0.44) | k = 80: 1,675 (0.42) | k = 320: 5,410 (0.34) |
| 1% | k = 3: 108 (0.48) | k = 10: 449 (0.45) | k = 40: 1,774 (0.44) | k = 160: 6,432 (0.40) |
| log-scaled | k = 16: 114 (0.51) | k = 20: 437 (0.44) | k = 24: 1,778 (0.44) | n/a |

### Covariance, clean cues

| Share active | 225 cells | 1,000 cells | 4,000 cells | 16,000 cells |
|---|---|---|---|---|
| 4.4% (AHA) | k = 10: 252 (1.12) | k = 44: 794 (0.79) | k = 178: 2,386 (0.60) | k = 711: 7,813 (0.49) |
| 2% (rat DG) | k = 5: 435 (1.93) | k = 20: 1,816 (1.82) | k = 80: 5,635 (1.41) | k = 320: 17,331 (1.08) |
| 1% | k = 3: 630 (2.80) | k = 10: 3,611 (3.61) | k = 40: 11,874 (2.97) | n/a |
| log-scaled | k = 16: 157 (0.70) | k = 20: 1,816 (1.82) | k = 24: 20,549 (5.14) | k = 28: 232,927 (14.56) |

### Clipped binary, clean cues

| Share active | 225 cells | 1,000 cells | 4,000 cells | 16,000 cells |
|---|---|---|---|---|
| 4.4% (AHA) | k = 10: 281 (1.25) | k = 44: 777 (0.78) | k = 178: 1,222 (0.31) | k = 711: 1,727 (0.11) |
| 2% (rat DG) | k = 5: 449 (2.00) | k = 20: 2,365 (2.37) | k = 80: 4,037 (1.01) | k = 320: 8,211 (0.51) |
| 1% | k = 3: 323 (1.43) | k = 10: 4,789 (4.79) | k = 40: 12,503 (3.13) | n/a |
| log-scaled | k = 16: 165 (0.73) | k = 20: 2,365 (2.37) | k = 24: 25,451 (6.36) | k = 28: 376,462 (23.53) |

### Covariance, cues missing 40% of their cells

| Share active | 225 cells | 1,000 cells | 4,000 cells | 16,000 cells |
|---|---|---|---|---|
| 4.4% (AHA) | k = 10: 185 (0.82) | k = 44: 737 (0.74) | k = 178: 2,337 (0.58) | k = 711: 7,729 (0.48) |
| 2% (rat DG) | k = 5: 236 (1.05) | k = 20: 1,596 (1.60) | k = 80: 5,454 (1.36) | k = 320: 17,156 (1.07) |
| 1% | k = 3: 171 (0.76) | k = 10: 2,517 (2.52) | k = 40: 11,366 (2.84) | n/a |
| log-scaled | k = 16: 128 (0.57) | k = 20: 1,596 (1.60) | k = 24: 17,962 (4.49) | k = 28: 218,460 (13.65) |

### Clipped binary, cues missing 40% of their cells

| Share active | 225 cells | 1,000 cells | 4,000 cells | 16,000 cells |
|---|---|---|---|---|
| 4.4% (AHA) | k = 10: 189 (0.84) | k = 44: 604 (0.60) | k = 178: 1,218 (0.30) | k = 711: 1,726 (0.11) |
| 2% (rat DG) | k = 5: 161 (0.72) | k = 20: 1,763 (1.76) | k = 80: 3,873 (0.97) | k = 320: 7,765 (0.49) |
| 1% | k = 3: 41 (0.18) | k = 10: 2,920 (2.92) | k = 40: 12,240 (3.06) | n/a |
| log-scaled | k = 16: 124 (0.55) | k = 20: 1,763 (1.76) | k = 24: 24,186 (6.05) | k = 28: 244,949 (15.31) |

## Drawings, evaluation alphabets: 50% load and load per cell

Seeds: 10 at 225 cells, 10 at 1,000 cells, 5 at 4,000 cells.

### Pseudo-inverse, cues missing 40% of their cells

| Share active | 225 cells | 1,000 cells | 4,000 cells |
|---|---|---|---|
| 4.4% (AHA) | k = 10: 106 (0.47) | k = 44: 375 (0.37) | k = 178: above 659 (≥ 0.16) |
| 2% (rat DG) | k = 5: 100 (0.44) | k = 20: 378 (0.38) | k = 80: above 659 (≥ 0.16) |
| 1% | k = 3: 95 (0.42) | k = 10: 339 (0.34) | k = 40: above 659 (≥ 0.16) |
| log-scaled | k = 16: 109 (0.48) | k = 20: 378 (0.38) | k = 24: above 659 (≥ 0.16) |

### Covariance, clean cues

| Share active | 225 cells | 1,000 cells | 4,000 cells |
|---|---|---|---|
| 4.4% (AHA) | k = 10: 185 (0.82) | k = 44: 337 (0.34) | k = 178: 380 (0.10) |
| 2% (rat DG) | k = 5: 284 (1.26) | k = 20: 658 (0.66) | k = 80: above 659 (≥ 0.16) |
| 1% | k = 3: 346 (1.54) | k = 10: above 659 (≥ 0.66) | k = 40: above 659 (≥ 0.16) |
| log-scaled | k = 16: 116 (0.52) | k = 20: 658 (0.66) | k = 24: above 659 (≥ 0.16) |

### Clipped binary, clean cues

| Share active | 225 cells | 1,000 cells | 4,000 cells |
|---|---|---|---|
| 4.4% (AHA) | k = 10: 236 (1.05) | k = 44: 542 (0.54) | k = 178: above 659 (≥ 0.16) |
| 2% (rat DG) | k = 5: 313 (1.39) | k = 20: above 659 (≥ 0.66) | k = 80: above 659 (≥ 0.16) |
| 1% | k = 3: 219 (0.97) | k = 10: above 659 (≥ 0.66) | k = 40: above 659 (≥ 0.16) |
| log-scaled | k = 16: 136 (0.61) | k = 20: above 659 (≥ 0.66) | k = 24: above 659 (≥ 0.16) |

### Covariance, cues missing 40% of their cells

| Share active | 225 cells | 1,000 cells | 4,000 cells |
|---|---|---|---|
| 4.4% (AHA) | k = 10: 140 (0.62) | k = 44: 312 (0.31) | k = 178: 376 (0.09) |
| 2% (rat DG) | k = 5: 170 (0.76) | k = 20: 572 (0.57) | k = 80: above 659 (≥ 0.16) |
| 1% | k = 3: 148 (0.66) | k = 10: above 659 (≥ 0.66) | k = 40: above 659 (≥ 0.16) |
| log-scaled | k = 16: 98 (0.43) | k = 20: 572 (0.57) | k = 24: above 659 (≥ 0.16) |

### Clipped binary, cues missing 40% of their cells

| Share active | 225 cells | 1,000 cells | 4,000 cells |
|---|---|---|---|
| 4.4% (AHA) | k = 10: 163 (0.72) | k = 44: 446 (0.45) | k = 178: above 659 (≥ 0.16) |
| 2% (rat DG) | k = 5: 135 (0.60) | k = 20: above 659 (≥ 0.66) | k = 80: above 659 (≥ 0.16) |
| 1% | k = 3: 53 (0.23) | k = 10: above 659 (≥ 0.66) | k = 40: above 659 (≥ 0.16) |
| log-scaled | k = 16: 115 (0.51) | k = 20: above 659 (≥ 0.66) | k = 24: above 659 (≥ 0.16) |

## Drawings, background alphabets: 50% load and load per cell

Seeds: 5 at 225 cells, 5 at 1,000 cells, 5 at 4,000 cells.

### Pseudo-inverse, cues missing 40% of their cells

| Share active | 225 cells | 1,000 cells | 4,000 cells |
|---|---|---|---|
| 4.4% (AHA) | k = 10: 107 (0.48) | k = 44: 378 (0.38) | k = 178: above 964 (≥ 0.24) |
| 2% (rat DG) | k = 5: 105 (0.47) | k = 20: 380 (0.38) | k = 80: above 964 (≥ 0.24) |
| 1% | k = 3: 99 (0.44) | k = 10: 352 (0.35) | k = 40: above 964 (≥ 0.24) |
| log-scaled | k = 16: 107 (0.48) | k = 20: 380 (0.38) | k = 24: 941 (0.24) |

### Covariance, clean cues

| Share active | 225 cells | 1,000 cells | 4,000 cells |
|---|---|---|---|
| 4.4% (AHA) | k = 10: 193 (0.86) | k = 44: 345 (0.34) | k = 178: 385 (0.10) |
| 2% (rat DG) | k = 5: 287 (1.27) | k = 20: 683 (0.68) | k = 80: 854 (0.21) |
| 1% | k = 3: 342 (1.52) | k = 10: 955 (0.95) | k = 40: above 964 (≥ 0.24) |
| log-scaled | k = 16: 121 (0.54) | k = 20: 683 (0.68) | k = 24: above 964 (≥ 0.24) |

### Clipped binary, clean cues

| Share active | 225 cells | 1,000 cells | 4,000 cells |
|---|---|---|---|
| 4.4% (AHA) | k = 10: 240 (1.07) | k = 44: 569 (0.57) | k = 178: 915 (0.23) |
| 2% (rat DG) | k = 5: 337 (1.50) | k = 20: above 964 (≥ 0.96) | k = 80: above 964 (≥ 0.24) |
| 1% | k = 3: 228 (1.01) | k = 10: above 964 (≥ 0.96) | k = 40: above 964 (≥ 0.24) |
| log-scaled | k = 16: 141 (0.63) | k = 20: above 964 (≥ 0.96) | k = 24: above 964 (≥ 0.24) |

### Covariance, cues missing 40% of their cells

| Share active | 225 cells | 1,000 cells | 4,000 cells |
|---|---|---|---|
| 4.4% (AHA) | k = 10: 146 (0.65) | k = 44: 320 (0.32) | k = 178: 381 (0.10) |
| 2% (rat DG) | k = 5: 179 (0.79) | k = 20: 603 (0.60) | k = 80: 833 (0.21) |
| 1% | k = 3: 150 (0.66) | k = 10: 721 (0.72) | k = 40: above 964 (≥ 0.24) |
| log-scaled | k = 16: 100 (0.45) | k = 20: 603 (0.60) | k = 24: above 964 (≥ 0.24) |

### Clipped binary, cues missing 40% of their cells

| Share active | 225 cells | 1,000 cells | 4,000 cells |
|---|---|---|---|
| 4.4% (AHA) | k = 10: 166 (0.74) | k = 44: 472 (0.47) | k = 178: 845 (0.21) |
| 2% (rat DG) | k = 5: 141 (0.63) | k = 20: above 964 (≥ 0.96) | k = 80: above 964 (≥ 0.24) |
| 1% | k = 3: 54 (0.24) | k = 10: above 964 (≥ 0.96) | k = 40: above 964 (≥ 0.24) |
| log-scaled | k = 16: 118 (0.52) | k = 20: above 964 (≥ 0.96) | k = 24: above 964 (≥ 0.24) |

## E1d's 4.4% runs against E1c's

Random patterns, the same patterns, cues and seeds as E1c. E1d reads the 50% load from
a finer grid of loads, and computes the covariance weights exactly rather than summing
them in float32.

| Cells | Rule | Condition | E1c | E1d |
|---|---|---|---|---|
| 225 | Pseudo-inverse | 40% removed | 111 (0.49) | 111 (0.49) |
| 225 | Covariance | clean | 252 (1.12) | 252 (1.12) |
| 225 | Clipped binary | clean | 281 (1.25) | 281 (1.25) |
| 1,000 | Pseudo-inverse | 40% removed | 327 (0.33) | 388 (0.39) |
| 1,000 | Covariance | clean | 795 (0.79) | 794 (0.79) |
| 1,000 | Clipped binary | clean | 777 (0.78) | 777 (0.78) |
| 4,000 | Pseudo-inverse | 40% removed | 1,539 (0.38) | 1,539 (0.38) |
| 4,000 | Covariance | clean | 2,386 (0.60) | 2,386 (0.60) |
| 4,000 | Clipped binary | clean | 1,222 (0.31) | 1,222 (0.31) |

## How unevenly DG uses its cells: drawings, evaluation alphabets

CV is the standard deviation over the mean of how many stored patterns each cell
is in, at the highest load: every character the alphabets hold. The random column
uses random patterns with the same cells, active cells and load. Means over seeds.

| Cells | Share active | Load | DG drawings CV | Random patterns CV | Ratio |
|---|---|---|---|---|---|
| 225 | 4.4% (AHA) (k = 10) | 659 | 0.469 | 0.180 | 2.60 |
| 225 | 2% (rat DG) (k = 5) | 659 | 0.596 | 0.254 | 2.35 |
| 225 | 1% (k = 3) | 659 | 0.766 | 0.335 | 2.29 |
| 225 | log-scaled (k = 16) | 659 | 0.441 | 0.139 | 3.18 |
| 1,000 | 4.4% (AHA) (k = 44) | 659 | 0.461 | 0.182 | 2.53 |
| 1,000 | 2% (rat DG) (k = 20) | 659 | 0.616 | 0.271 | 2.27 |
| 1,000 | 1% (k = 10) | 659 | 0.869 | 0.386 | 2.25 |
| 4,000 | 4.4% (AHA) (k = 178) | 659 | 0.459 | 0.179 | 2.56 |
| 4,000 | 2% (rat DG) (k = 80) | 659 | 0.615 | 0.273 | 2.25 |
| 4,000 | 1% (k = 40) | 659 | 0.869 | 0.384 | 2.26 |
| 4,000 | log-scaled (k = 24) | 659 | 1.115 | 0.500 | 2.23 |

## How unevenly DG uses its cells: drawings, background alphabets

CV is the standard deviation over the mean of how many stored patterns each cell
is in, at the highest load: every character the alphabets hold. The random column
uses random patterns with the same cells, active cells and load. Means over seeds.

| Cells | Share active | Load | DG drawings CV | Random patterns CV | Ratio |
|---|---|---|---|---|---|
| 225 | 4.4% (AHA) (k = 10) | 964 | 0.442 | 0.149 | 2.97 |
| 225 | 2% (rat DG) (k = 5) | 964 | 0.561 | 0.210 | 2.67 |
| 225 | 1% (k = 3) | 964 | 0.724 | 0.276 | 2.63 |
| 225 | log-scaled (k = 16) | 964 | 0.415 | 0.114 | 3.63 |
| 1,000 | 4.4% (AHA) (k = 44) | 964 | 0.432 | 0.151 | 2.86 |
| 1,000 | 2% (rat DG) (k = 20) | 964 | 0.578 | 0.226 | 2.55 |
| 1,000 | 1% (k = 10) | 964 | 0.819 | 0.317 | 2.59 |
| 4,000 | 4.4% (AHA) (k = 178) | 964 | 0.431 | 0.149 | 2.90 |
| 4,000 | 2% (rat DG) (k = 80) | 964 | 0.579 | 0.227 | 2.55 |
| 4,000 | 1% (k = 40) | 964 | 0.824 | 0.319 | 2.59 |
| 4,000 | log-scaled (k = 24) | 964 | 1.059 | 0.410 | 2.58 |

## Completion from partial cues, 20 patterns, random patterns

Percent: exact recall, then the share of the right pattern's cells on in the raw
cue and in the settled state.

| Cells | Share active | Rule | 20% removed: exact, overlap cue → settled | 40% removed: exact, overlap cue → settled | 60% removed: exact, overlap cue → settled | 80% removed: exact, overlap cue → settled |
|---|---|---|---|---|---|---|
| 225 | 4.4% (AHA) (k = 10) | Pseudo-inverse | 99.5, 80 → 100 | 98.0, 60 → 98 | 18.0, 40 → 18 | 0.0, 20 → 0 |
| 225 | 4.4% (AHA) (k = 10) | Covariance | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 98.0, 20 → 99 |
| 225 | 4.4% (AHA) (k = 10) | Clipped binary | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 98.0, 20 → 99 |
| 225 | 2% (rat DG) (k = 5) | Pseudo-inverse | 100.0, 80 → 100 | 92.0, 60 → 92 | 28.0, 40 → 28 | 0.0, 20 → 0 |
| 225 | 2% (rat DG) (k = 5) | Covariance | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 79.0, 20 → 85 |
| 225 | 2% (rat DG) (k = 5) | Clipped binary | 100.0, 80 → 100 | 99.0, 60 → 100 | 92.5, 40 → 97 | 76.0, 20 → 85 |
| 225 | 1% (k = 3) | Pseudo-inverse | 96.5, 67 → 97 | 97.0, 67 → 97 | 19.0, 33 → 20 | 17.0, 33 → 18 |
| 225 | 1% (k = 3) | Covariance | 99.5, 67 → 100 | 100.0, 67 → 100 | 88.0, 33 → 92 | 85.5, 33 → 91 |
| 225 | 1% (k = 3) | Clipped binary | 66.5, 67 → 86 | 69.0, 67 → 87 | 49.5, 33 → 73 | 49.5, 33 → 72 |
| 225 | log-scaled (k = 16) | Pseudo-inverse | 99.0, 81 → 100 | 97.0, 62 → 100 | 8.0, 38 → 8 | 0.0, 19 → 0 |
| 225 | log-scaled (k = 16) | Covariance | 100.0, 81 → 100 | 100.0, 62 → 100 | 100.0, 38 → 100 | 99.5, 19 → 100 |
| 225 | log-scaled (k = 16) | Clipped binary | 100.0, 81 → 100 | 100.0, 62 → 100 | 100.0, 38 → 100 | 99.5, 19 → 100 |
| 1,000 | 4.4% (AHA) (k = 44) | Pseudo-inverse | 99.0, 80 → 100 | 98.5, 59 → 100 | 11.0, 41 → 12 | 0.0, 20 → 0 |
| 1,000 | 4.4% (AHA) (k = 44) | Covariance | 100.0, 80 → 100 | 100.0, 59 → 100 | 100.0, 41 → 100 | 100.0, 20 → 100 |
| 1,000 | 4.4% (AHA) (k = 44) | Clipped binary | 100.0, 80 → 100 | 100.0, 59 → 100 | 100.0, 41 → 100 | 100.0, 20 → 100 |
| 1,000 | 2% (rat DG) (k = 20) | Pseudo-inverse | 99.5, 80 → 100 | 99.5, 60 → 100 | 14.0, 40 → 16 | 0.0, 20 → 0 |
| 1,000 | 2% (rat DG) (k = 20) | Covariance | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 1,000 | 2% (rat DG) (k = 20) | Clipped binary | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 1,000 | 1% (k = 10) | Pseudo-inverse | 100.0, 80 → 100 | 98.0, 60 → 98 | 19.0, 40 → 19 | 0.0, 20 → 0 |
| 1,000 | 1% (k = 10) | Covariance | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 99.5, 20 → 100 |
| 1,000 | 1% (k = 10) | Clipped binary | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 99.5, 20 → 100 |
| 4,000 | 4.4% (AHA) (k = 178) | Pseudo-inverse | 95.0, 80 → 100 | 87.0, 60 → 100 | 0.0, 40 → 0 | 0.0, 20 → 0 |
| 4,000 | 4.4% (AHA) (k = 178) | Covariance | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 4,000 | 4.4% (AHA) (k = 178) | Clipped binary | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 4,000 | 2% (rat DG) (k = 80) | Pseudo-inverse | 99.0, 80 → 100 | 95.0, 60 → 100 | 2.0, 40 → 3 | 0.0, 20 → 0 |
| 4,000 | 2% (rat DG) (k = 80) | Covariance | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 4,000 | 2% (rat DG) (k = 80) | Clipped binary | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 4,000 | 1% (k = 40) | Pseudo-inverse | 98.0, 80 → 100 | 96.0, 60 → 100 | 4.0, 40 → 4 | 0.0, 20 → 0 |
| 4,000 | 1% (k = 40) | Covariance | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 4,000 | 1% (k = 40) | Clipped binary | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 4,000 | log-scaled (k = 24) | Pseudo-inverse | 100.0, 79 → 100 | 99.0, 58 → 99 | 21.0, 42 → 23 | 0.0, 21 → 0 |
| 4,000 | log-scaled (k = 24) | Covariance | 100.0, 79 → 100 | 100.0, 58 → 100 | 100.0, 42 → 100 | 100.0, 21 → 100 |
| 4,000 | log-scaled (k = 24) | Clipped binary | 100.0, 79 → 100 | 100.0, 58 → 100 | 100.0, 42 → 100 | 100.0, 21 → 100 |
| 16,000 | 4.4% (AHA) (k = 711) | Pseudo-inverse | 83.0, 80 → 100 | 60.0, 60 → 100 | 0.0, 40 → 0 | 0.0, 20 → 0 |
| 16,000 | 4.4% (AHA) (k = 711) | Covariance | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 16,000 | 4.4% (AHA) (k = 711) | Clipped binary | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 16,000 | 2% (rat DG) (k = 320) | Pseudo-inverse | 93.7, 80 → 100 | 83.7, 60 → 100 | 0.0, 40 → 0 | 0.0, 20 → 0 |
| 16,000 | 2% (rat DG) (k = 320) | Covariance | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 16,000 | 2% (rat DG) (k = 320) | Clipped binary | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 16,000 | 1% (k = 160) | Pseudo-inverse | 97.5, 80 → 100 | 97.5, 60 → 100 | 0.0, 40 → 0 | 0.0, 20 → 0 |
| 16,000 | log-scaled (k = 28) | Covariance | 100.0, 79 → 100 | 100.0, 61 → 100 | 100.0, 39 → 100 | 100.0, 21 → 100 |
| 16,000 | log-scaled (k = 28) | Clipped binary | 100.0, 79 → 100 | 100.0, 61 → 100 | 100.0, 39 → 100 | 100.0, 21 → 100 |

## Completion from partial cues, 20 patterns, drawings, evaluation alphabets

Percent: exact recall, then the share of the right pattern's cells on in the raw
cue and in the settled state.

| Cells | Share active | Rule | 20% removed: exact, overlap cue → settled | 40% removed: exact, overlap cue → settled | 60% removed: exact, overlap cue → settled | 80% removed: exact, overlap cue → settled |
|---|---|---|---|---|---|---|
| 225 | 4.4% (AHA) (k = 10) | Pseudo-inverse | 99.5, 80 → 100 | 97.0, 60 → 97 | 11.0, 40 → 11 | 0.0, 20 → 0 |
| 225 | 4.4% (AHA) (k = 10) | Covariance | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 99.5, 20 → 100 |
| 225 | 4.4% (AHA) (k = 10) | Clipped binary | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 99.0, 20 → 99 |
| 225 | 2% (rat DG) (k = 5) | Pseudo-inverse | 100.0, 80 → 100 | 91.0, 60 → 91 | 25.5, 40 → 26 | 0.0, 20 → 0 |
| 225 | 2% (rat DG) (k = 5) | Covariance | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 95.0, 20 → 96 |
| 225 | 2% (rat DG) (k = 5) | Clipped binary | 100.0, 80 → 100 | 100.0, 60 → 100 | 99.5, 40 → 100 | 94.5, 20 → 96 |
| 225 | 1% (k = 3) | Pseudo-inverse | 91.0, 67 → 91 | 91.5, 67 → 91 | 21.0, 33 → 21 | 21.5, 33 → 22 |
| 225 | 1% (k = 3) | Covariance | 100.0, 67 → 100 | 100.0, 67 → 100 | 99.0, 33 → 99 | 99.5, 33 → 100 |
| 225 | 1% (k = 3) | Clipped binary | 99.0, 67 → 100 | 98.5, 67 → 99 | 74.5, 33 → 86 | 74.0, 33 → 84 |
| 225 | log-scaled (k = 16) | Pseudo-inverse | 99.0, 81 → 100 | 99.0, 62 → 100 | 4.0, 38 → 4 | 0.0, 19 → 0 |
| 225 | log-scaled (k = 16) | Covariance | 100.0, 81 → 100 | 100.0, 62 → 100 | 100.0, 38 → 100 | 100.0, 19 → 100 |
| 225 | log-scaled (k = 16) | Clipped binary | 100.0, 81 → 100 | 100.0, 62 → 100 | 100.0, 38 → 100 | 99.5, 19 → 100 |
| 1,000 | 4.4% (AHA) (k = 44) | Pseudo-inverse | 99.5, 80 → 100 | 99.0, 59 → 100 | 1.0, 41 → 2 | 0.0, 20 → 0 |
| 1,000 | 4.4% (AHA) (k = 44) | Covariance | 100.0, 80 → 100 | 100.0, 59 → 100 | 100.0, 41 → 100 | 100.0, 20 → 100 |
| 1,000 | 4.4% (AHA) (k = 44) | Clipped binary | 100.0, 80 → 100 | 100.0, 59 → 100 | 100.0, 41 → 100 | 100.0, 20 → 100 |
| 1,000 | 2% (rat DG) (k = 20) | Pseudo-inverse | 100.0, 80 → 100 | 99.0, 60 → 99 | 10.0, 40 → 10 | 0.0, 20 → 0 |
| 1,000 | 2% (rat DG) (k = 20) | Covariance | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 1,000 | 2% (rat DG) (k = 20) | Clipped binary | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 1,000 | 1% (k = 10) | Pseudo-inverse | 100.0, 80 → 100 | 96.0, 60 → 97 | 18.0, 40 → 19 | 0.0, 20 → 0 |
| 1,000 | 1% (k = 10) | Covariance | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 1,000 | 1% (k = 10) | Clipped binary | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 4,000 | 4.4% (AHA) (k = 178) | Pseudo-inverse | 94.0, 80 → 100 | 89.0, 60 → 100 | 0.0, 40 → 0 | 0.0, 20 → 0 |
| 4,000 | 4.4% (AHA) (k = 178) | Covariance | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 4,000 | 4.4% (AHA) (k = 178) | Clipped binary | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 4,000 | 2% (rat DG) (k = 80) | Pseudo-inverse | 99.0, 80 → 100 | 97.0, 60 → 100 | 0.0, 40 → 0 | 0.0, 20 → 0 |
| 4,000 | 2% (rat DG) (k = 80) | Covariance | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 4,000 | 2% (rat DG) (k = 80) | Clipped binary | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 4,000 | 1% (k = 40) | Pseudo-inverse | 99.0, 80 → 100 | 96.0, 60 → 100 | 3.0, 40 → 4 | 0.0, 20 → 0 |
| 4,000 | 1% (k = 40) | Covariance | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 4,000 | 1% (k = 40) | Clipped binary | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 4,000 | log-scaled (k = 24) | Pseudo-inverse | 99.0, 79 → 100 | 98.0, 58 → 98 | 13.0, 42 → 14 | 0.0, 21 → 0 |
| 4,000 | log-scaled (k = 24) | Covariance | 100.0, 79 → 100 | 100.0, 58 → 100 | 100.0, 42 → 100 | 100.0, 21 → 100 |
| 4,000 | log-scaled (k = 24) | Clipped binary | 100.0, 79 → 100 | 100.0, 58 → 100 | 100.0, 42 → 100 | 100.0, 21 → 100 |

## Completion from partial cues, 100 patterns, random patterns

Percent: exact recall, then the share of the right pattern's cells on in the raw
cue and in the settled state.

| Cells | Share active | Rule | 20% removed: exact, overlap cue → settled | 40% removed: exact, overlap cue → settled | 60% removed: exact, overlap cue → settled | 80% removed: exact, overlap cue → settled |
|---|---|---|---|---|---|---|
| 225 | 4.4% (AHA) (k = 10) | Pseudo-inverse | 94.2, 80 → 99 | 66.6, 60 → 95 | 0.0, 40 → 8 | 0.0, 20 → 1 |
| 225 | 4.4% (AHA) (k = 10) | Covariance | 97.4, 80 → 100 | 95.4, 60 → 99 | 91.5, 40 → 98 | 70.9, 20 → 82 |
| 225 | 4.4% (AHA) (k = 10) | Clipped binary | 99.3, 80 → 100 | 99.0, 60 → 100 | 96.9, 40 → 99 | 70.6, 20 → 81 |
| 225 | 2% (rat DG) (k = 5) | Pseudo-inverse | 91.1, 80 → 98 | 55.6, 60 → 87 | 1.5, 40 → 16 | 0.0, 20 → 2 |
| 225 | 2% (rat DG) (k = 5) | Covariance | 96.9, 80 → 99 | 90.6, 60 → 97 | 74.9, 40 → 89 | 32.8, 20 → 54 |
| 225 | 2% (rat DG) (k = 5) | Clipped binary | 95.2, 80 → 99 | 78.4, 60 → 92 | 54.7, 40 → 79 | 23.4, 20 → 48 |
| 225 | 1% (k = 3) | Pseudo-inverse | 58.5, 67 → 85 | 58.5, 67 → 85 | 1.8, 33 → 17 | 1.2, 33 → 17 |
| 225 | 1% (k = 3) | Covariance | 93.2, 67 → 97 | 93.5, 67 → 97 | 27.1, 33 → 58 | 28.0, 33 → 58 |
| 225 | 1% (k = 3) | Clipped binary | 16.3, 67 → 57 | 14.7, 67 → 58 | 4.3, 33 → 37 | 4.4, 33 → 36 |
| 225 | log-scaled (k = 16) | Pseudo-inverse | 97.2, 81 → 100 | 74.3, 62 → 98 | 0.0, 38 → 4 | 0.0, 19 → 0 |
| 225 | log-scaled (k = 16) | Covariance | 84.4, 81 → 99 | 79.2, 62 → 98 | 74.0, 38 → 96 | 45.4, 19 → 75 |
| 225 | log-scaled (k = 16) | Clipped binary | 96.0, 81 → 100 | 92.8, 62 → 99 | 77.1, 38 → 95 | 31.0, 19 → 61 |
| 1,000 | 4.4% (AHA) (k = 44) | Pseudo-inverse | 98.8, 80 → 100 | 97.5, 59 → 100 | 0.2, 41 → 0 | 0.0, 20 → 0 |
| 1,000 | 4.4% (AHA) (k = 44) | Covariance | 100.0, 80 → 100 | 100.0, 59 → 100 | 100.0, 41 → 100 | 100.0, 20 → 100 |
| 1,000 | 4.4% (AHA) (k = 44) | Clipped binary | 100.0, 80 → 100 | 100.0, 59 → 100 | 100.0, 41 → 100 | 100.0, 20 → 100 |
| 1,000 | 2% (rat DG) (k = 20) | Pseudo-inverse | 99.9, 80 → 100 | 98.8, 60 → 100 | 1.0, 40 → 1 | 0.0, 20 → 0 |
| 1,000 | 2% (rat DG) (k = 20) | Covariance | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 1,000 | 2% (rat DG) (k = 20) | Clipped binary | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 1,000 | 1% (k = 10) | Pseudo-inverse | 99.5, 80 → 100 | 94.6, 60 → 96 | 6.1, 40 → 6 | 0.0, 20 → 0 |
| 1,000 | 1% (k = 10) | Covariance | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 99.7, 20 → 100 |
| 1,000 | 1% (k = 10) | Clipped binary | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 99.6, 20 → 100 |
| 4,000 | 4.4% (AHA) (k = 178) | Pseudo-inverse | 95.6, 80 → 100 | 89.0, 60 → 100 | 0.0, 40 → 0 | 0.0, 20 → 0 |
| 4,000 | 4.4% (AHA) (k = 178) | Covariance | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 4,000 | 4.4% (AHA) (k = 178) | Clipped binary | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 4,000 | 2% (rat DG) (k = 80) | Pseudo-inverse | 98.4, 80 → 100 | 96.0, 60 → 100 | 0.0, 40 → 0 | 0.0, 20 → 0 |
| 4,000 | 2% (rat DG) (k = 80) | Covariance | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 4,000 | 2% (rat DG) (k = 80) | Clipped binary | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 4,000 | 1% (k = 40) | Pseudo-inverse | 98.4, 80 → 100 | 97.6, 60 → 100 | 0.0, 40 → 0 | 0.0, 20 → 0 |
| 4,000 | 1% (k = 40) | Covariance | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 4,000 | 1% (k = 40) | Clipped binary | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 4,000 | log-scaled (k = 24) | Pseudo-inverse | 99.4, 79 → 100 | 96.2, 58 → 98 | 2.6, 42 → 3 | 0.0, 21 → 0 |
| 4,000 | log-scaled (k = 24) | Covariance | 100.0, 79 → 100 | 100.0, 58 → 100 | 100.0, 42 → 100 | 100.0, 21 → 100 |
| 4,000 | log-scaled (k = 24) | Clipped binary | 100.0, 79 → 100 | 100.0, 58 → 100 | 100.0, 42 → 100 | 100.0, 21 → 100 |
| 16,000 | 4.4% (AHA) (k = 711) | Pseudo-inverse | 84.0, 80 → 100 | 69.0, 60 → 100 | 0.0, 40 → 0 | 0.0, 20 → 0 |
| 16,000 | 4.4% (AHA) (k = 711) | Covariance | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 16,000 | 4.4% (AHA) (k = 711) | Clipped binary | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 16,000 | 2% (rat DG) (k = 320) | Pseudo-inverse | 92.0, 80 → 100 | 85.0, 60 → 100 | 0.0, 40 → 0 | 0.0, 20 → 0 |
| 16,000 | 2% (rat DG) (k = 320) | Covariance | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 16,000 | 2% (rat DG) (k = 320) | Clipped binary | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 16,000 | 1% (k = 160) | Pseudo-inverse | 95.0, 80 → 100 | 90.5, 60 → 100 | 0.0, 40 → 0 | 0.0, 20 → 0 |
| 16,000 | log-scaled (k = 28) | Covariance | 100.0, 79 → 100 | 100.0, 61 → 100 | 100.0, 39 → 100 | 100.0, 21 → 100 |
| 16,000 | log-scaled (k = 28) | Clipped binary | 100.0, 79 → 100 | 100.0, 61 → 100 | 100.0, 39 → 100 | 100.0, 21 → 100 |

## Completion from partial cues, 100 patterns, drawings, evaluation alphabets

Percent: exact recall, then the share of the right pattern's cells on in the raw
cue and in the settled state.

| Cells | Share active | Rule | 20% removed: exact, overlap cue → settled | 40% removed: exact, overlap cue → settled | 60% removed: exact, overlap cue → settled | 80% removed: exact, overlap cue → settled |
|---|---|---|---|---|---|---|
| 225 | 4.4% (AHA) (k = 10) | Pseudo-inverse | 94.6, 80 → 99 | 57.6, 60 → 91 | 0.0, 40 → 10 | 0.0, 20 → 1 |
| 225 | 4.4% (AHA) (k = 10) | Covariance | 89.8, 80 → 97 | 84.1, 60 → 96 | 76.9, 40 → 91 | 51.4, 20 → 70 |
| 225 | 4.4% (AHA) (k = 10) | Clipped binary | 99.2, 80 → 100 | 97.7, 60 → 100 | 92.9, 40 → 98 | 61.9, 20 → 77 |
| 225 | 2% (rat DG) (k = 5) | Pseudo-inverse | 88.6, 80 → 98 | 49.8, 60 → 84 | 1.1, 40 → 18 | 0.0, 20 → 3 |
| 225 | 2% (rat DG) (k = 5) | Covariance | 94.5, 80 → 98 | 87.4, 60 → 96 | 69.8, 40 → 86 | 32.8, 20 → 52 |
| 225 | 2% (rat DG) (k = 5) | Clipped binary | 93.2, 80 → 98 | 74.0, 60 → 90 | 51.8, 40 → 77 | 21.3, 20 → 47 |
| 225 | 1% (k = 3) | Pseudo-inverse | 46.4, 67 → 81 | 44.2, 67 → 80 | 0.9, 33 → 22 | 0.5, 33 → 21 |
| 225 | 1% (k = 3) | Covariance | 90.3, 67 → 96 | 90.5, 67 → 96 | 27.7, 33 → 57 | 27.5, 33 → 56 |
| 225 | 1% (k = 3) | Clipped binary | 13.4, 67 → 56 | 14.2, 67 → 56 | 4.3, 33 → 37 | 3.7, 33 → 37 |
| 225 | log-scaled (k = 16) | Pseudo-inverse | 96.3, 81 → 100 | 63.7, 62 → 96 | 0.0, 38 → 7 | 0.0, 19 → 1 |
| 225 | log-scaled (k = 16) | Covariance | 52.6, 81 → 87 | 47.6, 62 → 84 | 35.7, 38 → 73 | 19.3, 19 → 53 |
| 225 | log-scaled (k = 16) | Clipped binary | 83.5, 81 → 98 | 71.2, 62 → 95 | 46.0, 38 → 82 | 17.5, 19 → 50 |
| 1,000 | 4.4% (AHA) (k = 44) | Pseudo-inverse | 99.0, 80 → 100 | 98.1, 59 → 100 | 0.0, 41 → 0 | 0.0, 20 → 0 |
| 1,000 | 4.4% (AHA) (k = 44) | Covariance | 100.0, 80 → 100 | 100.0, 59 → 100 | 100.0, 41 → 100 | 100.0, 20 → 100 |
| 1,000 | 4.4% (AHA) (k = 44) | Clipped binary | 100.0, 80 → 100 | 100.0, 59 → 100 | 100.0, 41 → 100 | 100.0, 20 → 100 |
| 1,000 | 2% (rat DG) (k = 20) | Pseudo-inverse | 99.9, 80 → 100 | 98.8, 60 → 99 | 1.0, 40 → 1 | 0.0, 20 → 0 |
| 1,000 | 2% (rat DG) (k = 20) | Covariance | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 1,000 | 2% (rat DG) (k = 20) | Clipped binary | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 1,000 | 1% (k = 10) | Pseudo-inverse | 99.7, 80 → 100 | 95.8, 60 → 96 | 6.3, 40 → 7 | 0.0, 20 → 0 |
| 1,000 | 1% (k = 10) | Covariance | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 99.1, 20 → 99 |
| 1,000 | 1% (k = 10) | Clipped binary | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 99.2, 20 → 99 |
| 4,000 | 4.4% (AHA) (k = 178) | Pseudo-inverse | 95.0, 80 → 100 | 90.4, 60 → 100 | 0.0, 40 → 0 | 0.0, 20 → 0 |
| 4,000 | 4.4% (AHA) (k = 178) | Covariance | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 4,000 | 4.4% (AHA) (k = 178) | Clipped binary | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 4,000 | 2% (rat DG) (k = 80) | Pseudo-inverse | 98.4, 80 → 100 | 97.2, 60 → 100 | 0.0, 40 → 0 | 0.0, 20 → 0 |
| 4,000 | 2% (rat DG) (k = 80) | Covariance | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 4,000 | 2% (rat DG) (k = 80) | Clipped binary | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 4,000 | 1% (k = 40) | Pseudo-inverse | 98.8, 80 → 100 | 98.4, 60 → 100 | 0.0, 40 → 0 | 0.0, 20 → 0 |
| 4,000 | 1% (k = 40) | Covariance | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 4,000 | 1% (k = 40) | Clipped binary | 100.0, 80 → 100 | 100.0, 60 → 100 | 100.0, 40 → 100 | 100.0, 20 → 100 |
| 4,000 | log-scaled (k = 24) | Pseudo-inverse | 100.0, 79 → 100 | 97.6, 58 → 99 | 5.4, 42 → 5 | 0.0, 21 → 0 |
| 4,000 | log-scaled (k = 24) | Covariance | 100.0, 79 → 100 | 100.0, 58 → 100 | 100.0, 42 → 100 | 100.0, 21 → 100 |
| 4,000 | log-scaled (k = 24) | Clipped binary | 100.0, 79 → 100 | 100.0, 58 → 100 | 100.0, 42 → 100 | 100.0, 21 → 100 |

## Settling steps and fixed points, random patterns

Steps that changed the state (for the pseudo-inverse, the last step that flipped a
cell), and the share of cues whose final state is a fixed point. Loads 20 and 100,
and the first tested load past the 50% load.

| Cells | Share active | Rule | Load | Steps, clean | Fixed point, clean | Steps, 40% removed | Fixed point, 40% removed |
|---|---|---|---|---|---|---|---|
| 225 | 4.4% (AHA) | Pseudo-inverse | 20 | 0.0 | 100.0 | 24.0 | 99.5 |
| 225 | 4.4% (AHA) | Pseudo-inverse | 100 | 0.0 | 100.0 | 48.2 | 78.2 |
| 225 | 4.4% (AHA) | Pseudo-inverse | 150 (past 50%) | 0.0 | 100.0 | 14.8 | 92.0 |
| 225 | 4.4% (AHA) | Covariance | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 225 | 4.4% (AHA) | Covariance | 100 | 0.6 | 99.1 | 4.1 | 95.9 |
| 225 | 4.4% (AHA) | Covariance | 300 (past 50%) | 38.5 | 45.8 | 57.8 | 18.6 |
| 225 | 4.4% (AHA) | Clipped binary | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 225 | 4.4% (AHA) | Clipped binary | 100 | 0.1 | 99.8 | 2.0 | 99.0 |
| 225 | 4.4% (AHA) | Clipped binary | 300 (past 50%) | 42.1 | 39.9 | 69.8 | 0.3 |
| 225 | 2% (rat DG) | Pseudo-inverse | 20 | 0.0 | 100.0 | 19.4 | 99.5 |
| 225 | 2% (rat DG) | Pseudo-inverse | 100 | 0.0 | 100.0 | 34.7 | 88.0 |
| 225 | 2% (rat DG) | Pseudo-inverse | 150 (past 50%) | 0.0 | 100.0 | 9.0 | 95.9 |
| 225 | 2% (rat DG) | Covariance | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 225 | 2% (rat DG) | Covariance | 100 | 0.6 | 99.2 | 6.7 | 92.0 |
| 225 | 2% (rat DG) | Covariance | 500 (past 50%) | 38.8 | 45.0 | 64.6 | 8.0 |
| 225 | 2% (rat DG) | Clipped binary | 20 | 0.0 | 100.0 | 1.7 | 99.0 |
| 225 | 2% (rat DG) | Clipped binary | 100 | 0.5 | 99.3 | 15.7 | 79.4 |
| 225 | 2% (rat DG) | Clipped binary | 500 (past 50%) | 42.5 | 39.3 | 69.9 | 0.1 |
| 225 | 1% | Pseudo-inverse | 20 | 0.0 | 100.0 | 13.0 | 100.0 |
| 225 | 1% | Pseudo-inverse | 100 | 0.0 | 100.0 | 17.1 | 94.9 |
| 225 | 1% | Pseudo-inverse | 150 (past 50%) | 0.0 | 100.0 | 4.3 | 98.9 |
| 225 | 1% | Covariance | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 225 | 1% | Covariance | 100 | 0.8 | 98.9 | 4.3 | 95.3 |
| 225 | 1% | Covariance | 700 (past 50%) | 34.8 | 50.6 | 62.0 | 11.6 |
| 225 | 1% | Clipped binary | 20 | 0.0 | 100.0 | 19.7 | 73.0 |
| 225 | 1% | Clipped binary | 100 | 5.1 | 92.7 | 57.9 | 17.6 |
| 225 | 1% | Clipped binary | 500 (past 50%) | 51.7 | 26.2 | 69.9 | 0.1 |
| 225 | log-scaled | Pseudo-inverse | 20 | 0.0 | 100.0 | 27.6 | 97.0 |
| 225 | log-scaled | Pseudo-inverse | 100 | 0.0 | 100.0 | 51.5 | 76.8 |
| 225 | log-scaled | Pseudo-inverse | 150 (past 50%) | 0.0 | 100.0 | 25.8 | 84.8 |
| 225 | log-scaled | Covariance | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 225 | log-scaled | Covariance | 100 | 3.8 | 94.6 | 10.5 | 87.2 |
| 225 | log-scaled | Covariance | 200 (past 50%) | 37.5 | 47.8 | 53.5 | 25.6 |
| 225 | log-scaled | Clipped binary | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 225 | log-scaled | Clipped binary | 100 | 2.2 | 96.9 | 7.2 | 91.9 |
| 225 | log-scaled | Clipped binary | 200 (past 50%) | 63.1 | 9.8 | 70.0 | 0.0 |
| 1,000 | 4.4% (AHA) | Pseudo-inverse | 20 | 0.0 | 100.0 | 35.3 | 98.5 |
| 1,000 | 4.4% (AHA) | Pseudo-inverse | 100 | 0.0 | 100.0 | 37.1 | 97.5 |
| 1,000 | 4.4% (AHA) | Pseudo-inverse | 500 (past 50%) | 0.0 | 100.0 | 66.1 | 13.0 |
| 1,000 | 4.4% (AHA) | Covariance | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 1,000 | 4.4% (AHA) | Covariance | 100 | 0.0 | 100.0 | 1.0 | 100.0 |
| 1,000 | 4.4% (AHA) | Covariance | 1,000 (past 50%) | 36.2 | 49.4 | 49.3 | 31.6 |
| 1,000 | 4.4% (AHA) | Clipped binary | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 1,000 | 4.4% (AHA) | Clipped binary | 100 | 0.0 | 100.0 | 1.0 | 100.0 |
| 1,000 | 4.4% (AHA) | Clipped binary | 1,000 (past 50%) | 70.0 | 0.0 | 70.0 | 0.0 |
| 1,000 | 2% (rat DG) | Pseudo-inverse | 20 | 0.0 | 100.0 | 29.8 | 99.5 |
| 1,000 | 2% (rat DG) | Pseudo-inverse | 100 | 0.0 | 100.0 | 29.7 | 99.1 |
| 1,000 | 2% (rat DG) | Pseudo-inverse | 500 (past 50%) | 0.0 | 100.0 | 60.5 | 45.4 |
| 1,000 | 2% (rat DG) | Covariance | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 1,000 | 2% (rat DG) | Covariance | 100 | 0.0 | 100.0 | 1.0 | 100.0 |
| 1,000 | 2% (rat DG) | Covariance | 2,000 (past 50%) | 33.3 | 53.1 | 51.4 | 28.1 |
| 1,000 | 2% (rat DG) | Clipped binary | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 1,000 | 2% (rat DG) | Clipped binary | 100 | 0.0 | 100.0 | 1.0 | 100.0 |
| 1,000 | 2% (rat DG) | Clipped binary | 3,000 (past 50%) | 70.0 | 0.0 | 70.0 | 0.0 |
| 1,000 | 1% | Pseudo-inverse | 20 | 0.0 | 100.0 | 23.0 | 99.5 |
| 1,000 | 1% | Pseudo-inverse | 100 | 0.0 | 100.0 | 24.9 | 98.2 |
| 1,000 | 1% | Pseudo-inverse | 500 (past 50%) | 0.0 | 100.0 | 51.5 | 66.8 |
| 1,000 | 1% | Covariance | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 1,000 | 1% | Covariance | 100 | 0.0 | 100.0 | 1.0 | 100.0 |
| 1,000 | 1% | Covariance | 5,000 (past 50%) | 58.3 | 17.0 | 68.7 | 1.9 |
| 1,000 | 1% | Clipped binary | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 1,000 | 1% | Clipped binary | 100 | 0.0 | 100.0 | 1.0 | 100.0 |
| 1,000 | 1% | Clipped binary | 5,000 (past 50%) | 38.5 | 45.0 | 70.0 | 0.0 |
| 4,000 | 4.4% (AHA) | Pseudo-inverse | 20 | 0.0 | 100.0 | 48.4 | 87.0 |
| 4,000 | 4.4% (AHA) | Pseudo-inverse | 100 | 0.0 | 100.0 | 48.6 | 89.0 |
| 4,000 | 4.4% (AHA) | Pseudo-inverse | 2,000 (past 50%) | 0.0 | 100.0 | 69.1 | 0.1 |
| 4,000 | 4.4% (AHA) | Covariance | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 4,000 | 4.4% (AHA) | Covariance | 100 | 0.0 | 100.0 | 1.0 | 100.0 |
| 4,000 | 4.4% (AHA) | Covariance | 3,000 (past 50%) | 27.1 | 62.8 | 30.8 | 59.4 |
| 4,000 | 4.4% (AHA) | Clipped binary | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 4,000 | 4.4% (AHA) | Clipped binary | 100 | 0.0 | 100.0 | 1.0 | 100.0 |
| 4,000 | 4.4% (AHA) | Clipped binary | 1,500 (past 50%) | 70.0 | 0.0 | 70.0 | 0.0 |
| 4,000 | 2% (rat DG) | Pseudo-inverse | 20 | 0.0 | 100.0 | 42.5 | 95.0 |
| 4,000 | 2% (rat DG) | Pseudo-inverse | 100 | 0.0 | 100.0 | 43.6 | 96.0 |
| 4,000 | 2% (rat DG) | Pseudo-inverse | 2,000 (past 50%) | 0.0 | 100.0 | 67.3 | 7.9 |
| 4,000 | 2% (rat DG) | Covariance | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 4,000 | 2% (rat DG) | Covariance | 100 | 0.0 | 100.0 | 1.0 | 100.0 |
| 4,000 | 2% (rat DG) | Covariance | 7,000 (past 50%) | 33.3 | 53.7 | 40.6 | 44.9 |
| 4,000 | 2% (rat DG) | Clipped binary | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 4,000 | 2% (rat DG) | Clipped binary | 100 | 0.0 | 100.0 | 1.0 | 100.0 |
| 4,000 | 2% (rat DG) | Clipped binary | 5,000 (past 50%) | 61.8 | 11.7 | 70.0 | 0.0 |
| 4,000 | 1% | Pseudo-inverse | 20 | 0.0 | 100.0 | 36.4 | 96.0 |
| 4,000 | 1% | Pseudo-inverse | 100 | 0.0 | 100.0 | 35.0 | 97.6 |
| 4,000 | 1% | Pseudo-inverse | 2,000 (past 50%) | 0.0 | 100.0 | 64.5 | 28.0 |
| 4,000 | 1% | Covariance | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 4,000 | 1% | Covariance | 100 | 0.0 | 100.0 | 1.0 | 100.0 |
| 4,000 | 1% | Covariance | 15,000 (past 50%) | 44.5 | 37.3 | 56.3 | 21.1 |
| 4,000 | 1% | Clipped binary | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 4,000 | 1% | Clipped binary | 100 | 0.0 | 100.0 | 1.0 | 100.0 |
| 4,000 | 1% | Clipped binary | 15,000 (past 50%) | 64.2 | 8.3 | 70.0 | 0.0 |
| 4,000 | log-scaled | Pseudo-inverse | 20 | 0.0 | 100.0 | 30.9 | 100.0 |
| 4,000 | log-scaled | Pseudo-inverse | 100 | 0.0 | 100.0 | 32.0 | 98.0 |
| 4,000 | log-scaled | Pseudo-inverse | 2,000 (past 50%) | 0.0 | 100.0 | 63.4 | 30.9 |
| 4,000 | log-scaled | Covariance | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 4,000 | log-scaled | Covariance | 100 | 0.0 | 100.0 | 1.0 | 100.0 |
| 4,000 | log-scaled | Covariance | 30,000 (past 50%) | 61.1 | 13.2 | 69.2 | 1.2 |
| 4,000 | log-scaled | Clipped binary | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 4,000 | log-scaled | Clipped binary | 100 | 0.0 | 100.0 | 1.0 | 100.0 |
| 4,000 | log-scaled | Clipped binary | 30,000 (past 50%) | 58.7 | 16.2 | 70.0 | 0.0 |
| 16,000 | 4.4% (AHA) | Pseudo-inverse | 20 | 0.0 | 100.0 | 58.3 | 60.0 |
| 16,000 | 4.4% (AHA) | Pseudo-inverse | 100 | 0.0 | 100.0 | 59.5 | 69.0 |
| 16,000 | 4.4% (AHA) | Pseudo-inverse | 5,000 (past 50%) | 0.0 | 100.0 | 64.7 | 33.4 |
| 16,000 | 4.4% (AHA) | Covariance | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 16,000 | 4.4% (AHA) | Covariance | 100 | 0.0 | 100.0 | 1.0 | 100.0 |
| 16,000 | 4.4% (AHA) | Covariance | 10,000 (past 50%) | 24.1 | 67.3 | 25.7 | 67.1 |
| 16,000 | 4.4% (AHA) | Clipped binary | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 16,000 | 4.4% (AHA) | Clipped binary | 100 | 0.0 | 100.0 | 1.0 | 100.0 |
| 16,000 | 4.4% (AHA) | Clipped binary | 2,000 (past 50%) | 70.0 | 0.0 | 70.0 | 0.0 |
| 16,000 | 2% (rat DG) | Pseudo-inverse | 20 | 0.0 | 100.0 | 54.4 | 83.7 |
| 16,000 | 2% (rat DG) | Pseudo-inverse | 100 | 0.0 | 100.0 | 54.3 | 85.0 |
| 16,000 | 2% (rat DG) | Pseudo-inverse | 7,000 (past 50%) | 0.0 | 100.0 | 66.7 | 12.4 |
| 16,000 | 2% (rat DG) | Covariance | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 16,000 | 2% (rat DG) | Covariance | 100 | 0.0 | 100.0 | 1.0 | 100.0 |
| 16,000 | 2% (rat DG) | Covariance | 20,000 (past 50%) | 15.7 | 78.8 | 17.6 | 78.5 |
| 16,000 | 2% (rat DG) | Clipped binary | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 16,000 | 2% (rat DG) | Clipped binary | 100 | 0.0 | 100.0 | 1.0 | 100.0 |
| 16,000 | 2% (rat DG) | Clipped binary | 10,000 (past 50%) | 70.0 | 0.0 | 70.0 | 0.0 |
| 16,000 | 1% | Pseudo-inverse | 20 | 0.0 | 100.0 | 49.2 | 97.5 |
| 16,000 | 1% | Pseudo-inverse | 100 | 0.0 | 100.0 | 48.4 | 90.5 |
| 16,000 | 1% | Pseudo-inverse | 7,000 (past 50%) | 0.0 | 100.0 | 63.9 | 40.7 |
| 16,000 | log-scaled | Covariance | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 16,000 | log-scaled | Covariance | 100 | 0.0 | 100.0 | 1.0 | 100.0 |
| 16,000 | log-scaled | Covariance | 300,000 (past 50%) | 52.6 | 25.5 | 65.5 | 7.0 |
| 16,000 | log-scaled | Clipped binary | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 16,000 | log-scaled | Clipped binary | 100 | 0.0 | 100.0 | 1.0 | 100.0 |
| 16,000 | log-scaled | Clipped binary | 500,000 (past 50%) | 70.0 | 0.0 | 70.0 | 0.0 |

## Settling steps and fixed points, drawings, evaluation alphabets

Steps that changed the state (for the pseudo-inverse, the last step that flipped a
cell), and the share of cues whose final state is a fixed point. Loads 20 and 100,
and the first tested load past the 50% load.

| Cells | Share active | Rule | Load | Steps, clean | Fixed point, clean | Steps, 40% removed | Fixed point, 40% removed |
|---|---|---|---|---|---|---|---|
| 225 | 4.4% (AHA) | Pseudo-inverse | 20 | 0.0 | 100.0 | 23.2 | 100.0 |
| 225 | 4.4% (AHA) | Pseudo-inverse | 100 | 0.0 | 100.0 | 47.6 | 75.2 |
| 225 | 4.4% (AHA) | Pseudo-inverse | 150 (past 50%) | 0.0 | 100.0 | 12.7 | 93.6 |
| 225 | 4.4% (AHA) | Covariance | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 225 | 4.4% (AHA) | Covariance | 100 | 2.6 | 96.4 | 9.1 | 89.0 |
| 225 | 4.4% (AHA) | Covariance | 200 (past 50%) | 31.8 | 55.4 | 48.6 | 32.3 |
| 225 | 4.4% (AHA) | Clipped binary | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 225 | 4.4% (AHA) | Clipped binary | 100 | 0.4 | 99.4 | 3.1 | 97.5 |
| 225 | 4.4% (AHA) | Clipped binary | 300 (past 50%) | 57.4 | 18.1 | 69.0 | 1.5 |
| 225 | 2% (rat DG) | Pseudo-inverse | 20 | 0.0 | 100.0 | 15.6 | 100.0 |
| 225 | 2% (rat DG) | Pseudo-inverse | 100 | 0.0 | 100.0 | 33.4 | 89.8 |
| 225 | 2% (rat DG) | Covariance | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 225 | 2% (rat DG) | Covariance | 100 | 1.1 | 98.5 | 8.7 | 89.2 |
| 225 | 2% (rat DG) | Covariance | 300 (past 50%) | 31.4 | 55.7 | 56.5 | 20.1 |
| 225 | 2% (rat DG) | Clipped binary | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 225 | 2% (rat DG) | Clipped binary | 100 | 0.8 | 98.8 | 17.9 | 76.1 |
| 225 | 2% (rat DG) | Clipped binary | 500 (past 50%) | 61.4 | 12.2 | 69.9 | 0.1 |
| 225 | 1% | Pseudo-inverse | 20 | 0.0 | 100.0 | 12.8 | 100.0 |
| 225 | 1% | Pseudo-inverse | 100 | 0.0 | 100.0 | 13.5 | 96.4 |
| 225 | 1% | Covariance | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 225 | 1% | Covariance | 100 | 1.1 | 98.5 | 4.8 | 94.5 |
| 225 | 1% | Covariance | 500 (past 50%) | 45.5 | 35.3 | 63.8 | 9.1 |
| 225 | 1% | Clipped binary | 20 | 0.0 | 100.0 | 2.0 | 98.5 |
| 225 | 1% | Clipped binary | 100 | 6.7 | 90.5 | 58.4 | 16.9 |
| 225 | 1% | Clipped binary | 300 (past 50%) | 45.7 | 34.8 | 69.4 | 0.9 |
| 225 | log-scaled | Pseudo-inverse | 20 | 0.0 | 100.0 | 26.7 | 99.0 |
| 225 | log-scaled | Pseudo-inverse | 100 | 0.0 | 100.0 | 52.5 | 74.6 |
| 225 | log-scaled | Pseudo-inverse | 150 (past 50%) | 0.0 | 100.0 | 20.7 | 87.6 |
| 225 | log-scaled | Covariance | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 225 | log-scaled | Covariance | 100 | 12.7 | 82.6 | 24.8 | 67.2 |
| 225 | log-scaled | Covariance | 150 (past 50%) | 38.7 | 46.9 | 47.0 | 35.9 |
| 225 | log-scaled | Clipped binary | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 225 | log-scaled | Clipped binary | 100 | 7.7 | 89.0 | 21.7 | 70.7 |
| 225 | log-scaled | Clipped binary | 150 (past 50%) | 46.4 | 33.7 | 64.2 | 8.5 |
| 1,000 | 4.4% (AHA) | Pseudo-inverse | 20 | 0.0 | 100.0 | 37.6 | 99.0 |
| 1,000 | 4.4% (AHA) | Pseudo-inverse | 100 | 0.0 | 100.0 | 37.7 | 98.1 |
| 1,000 | 4.4% (AHA) | Pseudo-inverse | 500 (past 50%) | 0.0 | 100.0 | 64.2 | 17.2 |
| 1,000 | 4.4% (AHA) | Covariance | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 1,000 | 4.4% (AHA) | Covariance | 100 | 0.0 | 100.0 | 1.0 | 100.0 |
| 1,000 | 4.4% (AHA) | Covariance | 500 (past 50%) | 50.7 | 31.1 | 52.6 | 29.1 |
| 1,000 | 4.4% (AHA) | Clipped binary | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 1,000 | 4.4% (AHA) | Clipped binary | 100 | 0.0 | 100.0 | 1.0 | 100.0 |
| 1,000 | 4.4% (AHA) | Clipped binary | 659 (past 50%) | 59.1 | 15.6 | 66.9 | 4.6 |
| 1,000 | 2% (rat DG) | Pseudo-inverse | 20 | 0.0 | 100.0 | 29.2 | 99.5 |
| 1,000 | 2% (rat DG) | Pseudo-inverse | 100 | 0.0 | 100.0 | 30.0 | 99.4 |
| 1,000 | 2% (rat DG) | Pseudo-inverse | 500 (past 50%) | 0.0 | 100.0 | 47.6 | 59.0 |
| 1,000 | 2% (rat DG) | Covariance | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 1,000 | 2% (rat DG) | Covariance | 100 | 0.0 | 100.0 | 1.0 | 100.0 |
| 1,000 | 2% (rat DG) | Covariance | 659 (past 50%) | 27.5 | 61.7 | 39.0 | 46.6 |
| 1,000 | 2% (rat DG) | Clipped binary | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 1,000 | 2% (rat DG) | Clipped binary | 100 | 0.0 | 100.0 | 1.0 | 100.0 |
| 1,000 | 1% | Pseudo-inverse | 20 | 0.0 | 100.0 | 23.6 | 99.0 |
| 1,000 | 1% | Pseudo-inverse | 100 | 0.0 | 100.0 | 24.8 | 99.3 |
| 1,000 | 1% | Pseudo-inverse | 500 (past 50%) | 0.0 | 100.0 | 18.2 | 92.0 |
| 1,000 | 1% | Covariance | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 1,000 | 1% | Covariance | 100 | 0.0 | 100.0 | 1.0 | 100.0 |
| 1,000 | 1% | Clipped binary | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 1,000 | 1% | Clipped binary | 100 | 0.0 | 100.0 | 1.0 | 100.0 |
| 4,000 | 4.4% (AHA) | Pseudo-inverse | 20 | 0.0 | 100.0 | 48.7 | 89.0 |
| 4,000 | 4.4% (AHA) | Pseudo-inverse | 100 | 0.0 | 100.0 | 49.3 | 90.4 |
| 4,000 | 4.4% (AHA) | Covariance | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 4,000 | 4.4% (AHA) | Covariance | 100 | 0.0 | 100.0 | 1.0 | 100.0 |
| 4,000 | 4.4% (AHA) | Covariance | 500 (past 50%) | 41.0 | 47.9 | 42.7 | 46.0 |
| 4,000 | 4.4% (AHA) | Clipped binary | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 4,000 | 4.4% (AHA) | Clipped binary | 100 | 0.0 | 100.0 | 1.0 | 100.0 |
| 4,000 | 2% (rat DG) | Pseudo-inverse | 20 | 0.0 | 100.0 | 40.7 | 97.0 |
| 4,000 | 2% (rat DG) | Pseudo-inverse | 100 | 0.0 | 100.0 | 42.2 | 97.2 |
| 4,000 | 2% (rat DG) | Covariance | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 4,000 | 2% (rat DG) | Covariance | 100 | 0.0 | 100.0 | 1.0 | 100.0 |
| 4,000 | 2% (rat DG) | Clipped binary | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 4,000 | 2% (rat DG) | Clipped binary | 100 | 0.0 | 100.0 | 1.0 | 100.0 |
| 4,000 | 1% | Pseudo-inverse | 20 | 0.0 | 100.0 | 35.7 | 96.0 |
| 4,000 | 1% | Pseudo-inverse | 100 | 0.0 | 100.0 | 36.0 | 98.6 |
| 4,000 | 1% | Covariance | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 4,000 | 1% | Covariance | 100 | 0.0 | 100.0 | 1.0 | 100.0 |
| 4,000 | 1% | Clipped binary | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 4,000 | 1% | Clipped binary | 100 | 0.0 | 100.0 | 1.0 | 100.0 |
| 4,000 | log-scaled | Pseudo-inverse | 20 | 0.0 | 100.0 | 31.8 | 100.0 |
| 4,000 | log-scaled | Pseudo-inverse | 100 | 0.0 | 100.0 | 32.2 | 99.0 |
| 4,000 | log-scaled | Covariance | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 4,000 | log-scaled | Covariance | 100 | 0.0 | 100.0 | 1.0 | 100.0 |
| 4,000 | log-scaled | Clipped binary | 20 | 0.0 | 100.0 | 1.0 | 100.0 |
| 4,000 | log-scaled | Clipped binary | 100 | 0.0 | 100.0 | 1.0 | 100.0 |

## End to end, Lake's runs and evaluation-alphabet instance runs, matched study-to-test

CA3 accuracy in percent, mean over seeds, at 225 cells: 10 active (4.4%, from
E1 and E1b's files) against 5 active (2%, this run). No settling passes PR's k
most active cells straight on.

| Task | Corruption | Covariance 4.4% → 2% | Clipped binary 4.4% → 2% | No settling 4.4% → 2% |
|---|---|---|---|---|
| Classification | none | 53.8 → 57.2 (+3.5) | 54.2 → 57.4 (+3.2) | 64.3 → 61.0 (-3.3) |
| Instance | occlusion 0 | 100.0 → 100.0 (+0.0) | 100.0 → 100.0 (+0.0) | 100.0 → 100.0 (+0.0) |
| Instance | occlusion 0.3 | 96.5 → 96.7 (+0.2) | 96.5 → 96.7 (+0.2) | 98.0 → 97.3 (-0.8) |
| Instance | occlusion 0.5 | 71.9 → 71.4 (-0.6) | 72.6 → 71.4 (-1.3) | 82.6 → 75.5 (-7.1) |
| Instance | noise 0 | 100.0 → 100.0 (+0.0) | 100.0 → 100.0 (+0.0) | 100.0 → 100.0 (+0.0) |
| Instance | noise 0.3 | 40.7 → 39.8 (-0.9) | 40.6 → 39.9 (-0.7) | 58.3 → 47.8 (-10.6) |
| Instance | noise 0.5 | 10.4 → 9.0 (-1.5) | 10.6 → 9.1 (-1.5) | 17.8 → 12.2 (-5.6) |

Every stage at 2%, clean drawings:

| Task | Option | VC | PR | PC | PM |
|---|---|---|---|---|---|
| Classification | Covariance | 63.0 | 72.5 | 57.2 | 58.4 |
| Classification | Clipped binary | 63.0 | 72.5 | 57.4 | 58.4 |
| Classification | No settling | 63.0 | 72.5 | 61.0 | 61.8 |
| Instance | Covariance | 100.0 | 100.0 | 100.0 | 100.0 |
| Instance | Clipped binary | 100.0 | 100.0 | 100.0 | 100.0 |
| Instance | No settling | 100.0 | 100.0 | 100.0 | 100.0 |

## End to end, Lake's runs and evaluation-alphabet instance runs, matched test-to-study

CA3 accuracy in percent, mean over seeds, at 225 cells: 10 active (4.4%, from
E1 and E1b's files) against 5 active (2%, this run). No settling passes PR's k
most active cells straight on.

| Task | Corruption | Covariance 4.4% → 2% | Clipped binary 4.4% → 2% | No settling 4.4% → 2% |
|---|---|---|---|---|
| Classification | none | 62.7 → 65.9 (+3.3) | 62.7 → 65.8 (+3.1) | 62.8 → 65.9 (+3.1) |
| Instance | occlusion 0 | 100.0 → 100.0 (+0.0) | 100.0 → 100.0 (+0.0) | 100.0 → 100.0 (+0.0) |
| Instance | occlusion 0.3 | 97.5 → 97.4 (-0.1) | 97.5 → 97.3 (-0.1) | 97.5 → 97.4 (-0.1) |
| Instance | occlusion 0.5 | 78.2 → 78.2 (+0.0) | 78.5 → 78.0 (-0.5) | 78.3 → 78.1 (-0.2) |
| Instance | noise 0 | 100.0 → 100.0 (+0.0) | 100.0 → 100.0 (+0.0) | 100.0 → 100.0 (+0.0) |
| Instance | noise 0.3 | 48.9 → 49.1 (+0.3) | 48.6 → 48.8 (+0.1) | 48.7 → 48.8 (+0.1) |
| Instance | noise 0.5 | 14.9 → 14.8 (-0.1) | 14.9 → 14.5 (-0.4) | 15.3 → 14.5 (-0.8) |

Every stage at 2%, clean drawings:

| Task | Option | VC | PR | PC | PM |
|---|---|---|---|---|---|
| Classification | Covariance | 67.3 | 65.0 | 65.9 | 66.0 |
| Classification | Clipped binary | 67.3 | 65.0 | 65.8 | 65.8 |
| Classification | No settling | 67.3 | 65.0 | 65.9 | 66.0 |
| Instance | Covariance | 100.0 | 100.0 | 100.0 | 100.0 |
| Instance | Clipped binary | 100.0 | 100.0 | 100.0 | 100.0 |
| Instance | No settling | 100.0 | 100.0 | 100.0 | 100.0 |

## End to end, background-alphabet validation runs, matched study-to-test

CA3 accuracy in percent, mean over seeds, at 225 cells: 10 active (4.4%, from
E1 and E1b's files) against 5 active (2%, this run). No settling passes PR's k
most active cells straight on.

| Task | Corruption | Covariance 4.4% → 2% | Clipped binary 4.4% → 2% | No settling 4.4% → 2% |
|---|---|---|---|---|
| Classification | none | 60.6 → 59.4 (-1.2) | 61.0 → 59.5 (-1.5) | 68.8 → 63.2 (-5.7) |
| Instance | occlusion 0 | 100.0 → 100.0 (+0.0) | 100.0 → 100.0 (+0.0) | 100.0 → 100.0 (+0.0) |
| Instance | occlusion 0.3 | 95.5 → 95.2 (-0.3) | 95.1 → 95.4 (+0.3) | 98.0 → 97.1 (-0.9) |
| Instance | occlusion 0.5 | 67.4 → 67.6 (+0.2) | 67.7 → 67.9 (+0.2) | 75.9 → 71.1 (-4.8) |
| Instance | noise 0 | 100.0 → 100.0 (+0.0) | 100.0 → 100.0 (+0.0) | 100.0 → 100.0 (+0.0) |
| Instance | noise 0.3 | 30.6 → 31.4 (+0.8) | 31.1 → 31.1 (-0.0) | 44.3 → 37.1 (-7.2) |
| Instance | noise 0.5 | 11.9 → 10.5 (-1.4) | 11.8 → 10.3 (-1.5) | 17.1 → 12.2 (-4.9) |

Every stage at 2%, clean drawings:

| Task | Option | VC | PR | PC | PM |
|---|---|---|---|---|---|
| Classification | Covariance | 69.5 | 76.6 | 59.4 | 62.0 |
| Classification | Clipped binary | 69.5 | 76.6 | 59.5 | 61.8 |
| Classification | No settling | 69.5 | 76.6 | 63.2 | 65.0 |
| Instance | Covariance | 100.0 | 100.0 | 100.0 | 100.0 |
| Instance | Clipped binary | 100.0 | 100.0 | 100.0 | 100.0 |
| Instance | No settling | 100.0 | 100.0 | 100.0 | 100.0 |

## Exact recall against load, random patterns, 225 cells

Percent of cues, mean over seeds: clean cues for the local rules, 40% removed for
the pseudo-inverse.

| Load | 4.4% (AHA) k = 10 Pseudo-inverse | 4.4% (AHA) k = 10 Covariance | 4.4% (AHA) k = 10 Clipped binary | 2% (rat DG) k = 5 Pseudo-inverse | 2% (rat DG) k = 5 Covariance | 2% (rat DG) k = 5 Clipped binary | 1% k = 3 Pseudo-inverse | 1% k = 3 Covariance | 1% k = 3 Clipped binary | log-scaled k = 16 Pseudo-inverse | log-scaled k = 16 Covariance | log-scaled k = 16 Clipped binary |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 98.0 | 100.0 | 100.0 | 92.0 | 100.0 | 100.0 | 97.0 | 100.0 | 99.5 | 97.0 | 100.0 | 100.0 |
| 30 | 97.0 | 100.0 | 100.0 | 90.0 | 100.0 | 100.0 | 95.0 | 100.0 | 99.0 | 99.7 | 100.0 | 100.0 |
| 50 | 98.0 | 99.8 | 100.0 | 89.8 | 100.0 | 99.8 | 91.6 | 99.8 | 98.2 | 99.8 | 99.8 | 100.0 |
| 70 | 94.6 | 100.0 | 100.0 | 85.7 | 100.0 | 99.9 | 83.6 | 99.6 | 95.4 | 96.1 | 98.7 | 100.0 |
| 100 | 66.6 | 99.2 | 99.9 | 55.6 | 99.3 | 99.1 | 58.5 | 98.4 | 91.7 | 74.3 | 91.6 | 98.4 |
| 150 | 0.2 | 92.3 | 97.9 | 2.5 | 97.9 | 98.7 | 13.1 | 95.3 | 85.0 | 0.0 | 55.5 | 68.8 |
| 200 | n/a | 74.8 | 91.2 | n/a | 94.6 | 95.7 | 0.9 | 92.4 | 76.0 | n/a | 22.8 | 10.7 |
| 300 | n/a | 31.4 | 42.2 | n/a | 81.2 | 84.0 | n/a | 81.3 | 54.6 | n/a | 2.3 | 0.0 |
| 500 | n/a | 3.6 | 0.0 | n/a | 38.3 | 41.1 | n/a | 65.0 | 22.5 | n/a | n/a | n/a |
| 700 | n/a | n/a | n/a | n/a | 14.8 | 7.5 | n/a | 43.1 | 8.3 | n/a | n/a | n/a |
| 1,000 | n/a | n/a | n/a | n/a | 5.1 | 0.3 | n/a | 23.8 | 1.6 | n/a | n/a | n/a |
| 1,500 | n/a | n/a | n/a | n/a | 1.9 | n/a | n/a | 11.8 | n/a | n/a | n/a | n/a |
| 2,000 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | 7.3 | n/a | n/a | n/a | n/a |
| 3,000 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | 4.0 | n/a | n/a | n/a | n/a |

## Exact recall against load, random patterns, 1,000 cells

Percent of cues, mean over seeds: clean cues for the local rules, 40% removed for
the pseudo-inverse.

| Load | 4.4% (AHA) k = 44 Pseudo-inverse | 4.4% (AHA) k = 44 Covariance | 4.4% (AHA) k = 44 Clipped binary | 2% (rat DG) k = 20 Pseudo-inverse | 2% (rat DG) k = 20 Covariance | 2% (rat DG) k = 20 Clipped binary | 1% k = 10 Pseudo-inverse | 1% k = 10 Covariance | 1% k = 10 Clipped binary |
|---|---|---|---|---|---|---|---|---|---|
| 20 | 98.5 | 100.0 | 100.0 | 99.5 | 100.0 | 100.0 | 98.0 | 100.0 | 100.0 |
| 30 | 97.3 | 100.0 | 100.0 | 98.0 | 100.0 | 100.0 | 97.0 | 100.0 | 100.0 |
| 50 | 97.2 | 100.0 | 100.0 | 97.4 | 100.0 | 100.0 | 95.8 | 100.0 | 100.0 |
| 70 | 97.6 | 100.0 | 100.0 | 97.6 | 100.0 | 100.0 | 95.0 | 100.0 | 100.0 |
| 100 | 97.5 | 100.0 | 100.0 | 98.8 | 100.0 | 100.0 | 94.6 | 100.0 | 100.0 |
| 150 | 96.5 | 100.0 | 100.0 | 97.9 | 100.0 | 100.0 | 96.4 | 100.0 | 100.0 |
| 200 | 96.7 | 100.0 | 100.0 | 98.1 | 100.0 | 100.0 | 96.2 | 100.0 | 100.0 |
| 300 | 90.9 | 100.0 | 100.0 | 95.8 | 100.0 | 100.0 | 95.7 | 100.0 | 100.0 |
| 500 | 9.6 | 96.7 | 99.7 | 33.8 | 100.0 | 100.0 | 37.9 | 100.0 | 100.0 |
| 700 | 0.0 | 69.8 | 70.7 | 0.0 | 99.9 | 100.0 | 0.0 | 100.0 | 100.0 |
| 1,000 | n/a | 14.0 | 0.0 | n/a | 98.5 | 100.0 | n/a | 100.0 | 100.0 |
| 1,500 | n/a | 0.0 | n/a | n/a | 78.9 | 99.6 | n/a | 99.7 | 100.0 |
| 2,000 | n/a | n/a | n/a | n/a | 35.4 | 85.3 | n/a | 97.5 | 99.9 |
| 3,000 | n/a | n/a | n/a | n/a | 2.4 | 0.0 | n/a | 71.7 | 97.7 |
| 5,000 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | 11.8 | 45.6 |
| 7,000 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | 1.8 | 0.1 |

## Exact recall against load, random patterns, 4,000 cells

Percent of cues, mean over seeds: clean cues for the local rules, 40% removed for
the pseudo-inverse.

| Load | 4.4% (AHA) k = 178 Pseudo-inverse | 4.4% (AHA) k = 178 Covariance | 4.4% (AHA) k = 178 Clipped binary | 2% (rat DG) k = 80 Pseudo-inverse | 2% (rat DG) k = 80 Covariance | 2% (rat DG) k = 80 Clipped binary | 1% k = 40 Pseudo-inverse | 1% k = 40 Covariance | 1% k = 40 Clipped binary | log-scaled k = 24 Pseudo-inverse | log-scaled k = 24 Covariance | log-scaled k = 24 Clipped binary |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 87.0 | 100.0 | 100.0 | 95.0 | 100.0 | 100.0 | 96.0 | 100.0 | 100.0 | 99.0 | 100.0 | 100.0 |
| 30 | 91.3 | 100.0 | 100.0 | 94.0 | 100.0 | 100.0 | 98.7 | 100.0 | 100.0 | 98.7 | 100.0 | 100.0 |
| 50 | 92.0 | 100.0 | 100.0 | 97.6 | 100.0 | 100.0 | 97.2 | 100.0 | 100.0 | 98.0 | 100.0 | 100.0 |
| 70 | 94.0 | 100.0 | 100.0 | 96.3 | 100.0 | 100.0 | 96.9 | 100.0 | 100.0 | 97.4 | 100.0 | 100.0 |
| 100 | 89.0 | 100.0 | 100.0 | 96.0 | 100.0 | 100.0 | 97.6 | 100.0 | 100.0 | 96.2 | 100.0 | 100.0 |
| 150 | 91.5 | 100.0 | 100.0 | 96.4 | 100.0 | 100.0 | 96.8 | 100.0 | 100.0 | 97.1 | 100.0 | 100.0 |
| 200 | 87.2 | 100.0 | 100.0 | 94.4 | 100.0 | 100.0 | 98.9 | 100.0 | 100.0 | 96.4 | 100.0 | 100.0 |
| 300 | 90.0 | 100.0 | 100.0 | 94.3 | 100.0 | 100.0 | 98.1 | 100.0 | 100.0 | 96.7 | 100.0 | 100.0 |
| 500 | 88.8 | 100.0 | 100.0 | 97.1 | 100.0 | 100.0 | 97.8 | 100.0 | 100.0 | 98.2 | 100.0 | 100.0 |
| 700 | 88.5 | 100.0 | 100.0 | 93.8 | 100.0 | 100.0 | 97.1 | 100.0 | 100.0 | 97.5 | 100.0 | 100.0 |
| 1,000 | 84.5 | 100.0 | 99.0 | 90.8 | 100.0 | 100.0 | 97.0 | 100.0 | 100.0 | 96.6 | 100.0 | 100.0 |
| 1,500 | 54.9 | 98.9 | 0.0 | 77.0 | 100.0 | 100.0 | 87.4 | 100.0 | 100.0 | 90.6 | 100.0 | 100.0 |
| 2,000 | 0.1 | 82.3 | n/a | 6.6 | 100.0 | 100.0 | 23.3 | 100.0 | 100.0 | 21.9 | 100.0 | 100.0 |
| 3,000 | n/a | 8.0 | n/a | 0.0 | 99.9 | 100.0 | 0.0 | 100.0 | 100.0 | 0.0 | 100.0 | 100.0 |
| 5,000 | n/a | 0.0 | n/a | n/a | 72.8 | 14.0 | n/a | 100.0 | 100.0 | n/a | 100.0 | 100.0 |
| 7,000 | n/a | n/a | n/a | n/a | 8.6 | 0.0 | n/a | 99.3 | 100.0 | n/a | 100.0 | 100.0 |
| 10,000 | n/a | n/a | n/a | n/a | 0.0 | n/a | n/a | 79.4 | 99.7 | n/a | 99.8 | 100.0 |
| 15,000 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | 10.0 | 9.5 | n/a | 90.9 | 100.0 |
| 20,000 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | 0.3 | 0.0 | n/a | 53.4 | 99.4 |
| 30,000 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | 2.5 | 16.3 |
| 50,000 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | 0.0 |

## Exact recall against load, random patterns, 16,000 cells

Percent of cues, mean over seeds: clean cues for the local rules, 40% removed for
the pseudo-inverse.

| Load | 4.4% (AHA) k = 711 Pseudo-inverse | 4.4% (AHA) k = 711 Covariance | 4.4% (AHA) k = 711 Clipped binary | 2% (rat DG) k = 320 Pseudo-inverse | 2% (rat DG) k = 320 Covariance | 2% (rat DG) k = 320 Clipped binary | 1% k = 160 Pseudo-inverse | log-scaled k = 28 Covariance | log-scaled k = 28 Clipped binary |
|---|---|---|---|---|---|---|---|---|---|
| 20 | 60.0 | 100.0 | 100.0 | 83.7 | 100.0 | 100.0 | 97.5 | 100.0 | 100.0 |
| 30 | 71.3 | 100.0 | 100.0 | 85.8 | 100.0 | 100.0 | 86.7 | 100.0 | 100.0 |
| 50 | 63.2 | 100.0 | 100.0 | 80.0 | 100.0 | 100.0 | 93.0 | 100.0 | 100.0 |
| 70 | 66.0 | 100.0 | 100.0 | 80.0 | 100.0 | 100.0 | 89.3 | 100.0 | 100.0 |
| 100 | 69.0 | 100.0 | 100.0 | 85.0 | 100.0 | 100.0 | 90.5 | 100.0 | 100.0 |
| 150 | 64.3 | 100.0 | 100.0 | 81.5 | 100.0 | 100.0 | 93.7 | 100.0 | 100.0 |
| 200 | 68.1 | 100.0 | 100.0 | 79.1 | 100.0 | 100.0 | 92.3 | 100.0 | 100.0 |
| 300 | 67.8 | 100.0 | 100.0 | 80.9 | 100.0 | 100.0 | 93.0 | 100.0 | 100.0 |
| 500 | 65.6 | 100.0 | 100.0 | 80.8 | 100.0 | 100.0 | 91.5 | 100.0 | 100.0 |
| 700 | 65.5 | 100.0 | 100.0 | 83.0 | 100.0 | 100.0 | 92.8 | 100.0 | 100.0 |
| 1,000 | 60.8 | 100.0 | 100.0 | 82.1 | 100.0 | 100.0 | 89.7 | 100.0 | 100.0 |
| 1,500 | 62.3 | 100.0 | 98.2 | 83.4 | 100.0 | 100.0 | 92.3 | 100.0 | 100.0 |
| 2,000 | 66.5 | 100.0 | 0.0 | 80.5 | 100.0 | 100.0 | 93.0 | 100.0 | 100.0 |
| 3,000 | 63.2 | 100.0 | n/a | 78.5 | 100.0 | 100.0 | 85.8 | 100.0 | 100.0 |
| 5,000 | 33.4 | 99.4 | n/a | 61.5 | 100.0 | 100.0 | 80.5 | 100.0 | 100.0 |
| 7,000 | 0.5 | 72.0 | n/a | 12.4 | 100.0 | 90.5 | 39.7 | 100.0 | 100.0 |
| 10,000 | n/a | 0.6 | n/a | 0.0 | 99.9 | 0.0 | 0.0 | 100.0 | 100.0 |
| 15,000 | n/a | n/a | n/a | n/a | 86.0 | n/a | n/a | 100.0 | 100.0 |
| 20,000 | n/a | n/a | n/a | n/a | 14.3 | n/a | n/a | 100.0 | 100.0 |
| 30,000 | n/a | n/a | n/a | n/a | 0.0 | n/a | n/a | 100.0 | 100.0 |
| 50,000 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | 100.0 | 100.0 |
| 70,000 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | 100.0 | 100.0 |
| 100,000 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | 100.0 | 100.0 |
| 150,000 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | 100.0 | 100.0 |
| 200,000 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | 76.5 | 100.0 |
| 300,000 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | 6.0 | 90.0 |
| 500,000 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | 0.0 | 0.0 |

## Exact recall against load, drawings, evaluation alphabets, 225 cells

Percent of cues, mean over seeds: clean cues for the local rules, 40% removed for
the pseudo-inverse.

| Load | 4.4% (AHA) k = 10 Pseudo-inverse | 4.4% (AHA) k = 10 Covariance | 4.4% (AHA) k = 10 Clipped binary | 2% (rat DG) k = 5 Pseudo-inverse | 2% (rat DG) k = 5 Covariance | 2% (rat DG) k = 5 Clipped binary | 1% k = 3 Pseudo-inverse | 1% k = 3 Covariance | 1% k = 3 Clipped binary | log-scaled k = 16 Pseudo-inverse | log-scaled k = 16 Covariance | log-scaled k = 16 Clipped binary |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 97.0 | 100.0 | 100.0 | 91.0 | 100.0 | 100.0 | 91.5 | 100.0 | 100.0 | 99.0 | 100.0 | 100.0 |
| 30 | 95.3 | 100.0 | 100.0 | 87.3 | 100.0 | 100.0 | 89.7 | 100.0 | 100.0 | 98.7 | 100.0 | 100.0 |
| 50 | 95.2 | 100.0 | 100.0 | 87.4 | 99.8 | 99.6 | 93.0 | 100.0 | 99.2 | 99.0 | 99.4 | 100.0 |
| 70 | 92.6 | 99.3 | 100.0 | 88.3 | 99.4 | 99.1 | 85.7 | 100.0 | 96.1 | 97.0 | 93.1 | 99.9 |
| 100 | 57.6 | 95.5 | 99.6 | 49.8 | 98.3 | 98.8 | 44.2 | 96.8 | 88.4 | 63.7 | 67.4 | 91.4 |
| 150 | 0.1 | 71.5 | 93.7 | 1.3 | 91.7 | 95.4 | 3.9 | 90.4 | 72.3 | 0.0 | 21.2 | 37.2 |
| 200 | 0.0 | 42.1 | 71.3 | 0.0 | 78.3 | 86.6 | 0.8 | 81.2 | 55.3 | 0.0 | 5.9 | 6.5 |
| 300 | n/a | 10.9 | 19.0 | n/a | 45.6 | 53.4 | n/a | 59.5 | 31.0 | n/a | 0.3 | 0.1 |
| 500 | n/a | 1.0 | 0.6 | n/a | 13.4 | 12.4 | n/a | 25.8 | 10.6 | n/a | 0.0 | 0.0 |
| 659 | n/a | 0.2 | 0.0 | n/a | 5.8 | 4.0 | n/a | 15.7 | 7.8 | n/a | 0.0 | 0.0 |

## Exact recall against load, drawings, evaluation alphabets, 1,000 cells

Percent of cues, mean over seeds: clean cues for the local rules, 40% removed for
the pseudo-inverse.

| Load | 4.4% (AHA) k = 44 Pseudo-inverse | 4.4% (AHA) k = 44 Covariance | 4.4% (AHA) k = 44 Clipped binary | 2% (rat DG) k = 20 Pseudo-inverse | 2% (rat DG) k = 20 Covariance | 2% (rat DG) k = 20 Clipped binary | 1% k = 10 Pseudo-inverse | 1% k = 10 Covariance | 1% k = 10 Clipped binary |
|---|---|---|---|---|---|---|---|---|---|
| 20 | 99.0 | 100.0 | 100.0 | 99.0 | 100.0 | 100.0 | 96.0 | 100.0 | 100.0 |
| 30 | 96.7 | 100.0 | 100.0 | 99.0 | 100.0 | 100.0 | 95.3 | 100.0 | 100.0 |
| 50 | 97.8 | 100.0 | 100.0 | 97.0 | 100.0 | 100.0 | 94.6 | 100.0 | 100.0 |
| 70 | 96.9 | 100.0 | 100.0 | 96.9 | 100.0 | 100.0 | 94.7 | 100.0 | 100.0 |
| 100 | 98.1 | 100.0 | 100.0 | 98.8 | 100.0 | 100.0 | 95.8 | 100.0 | 100.0 |
| 150 | 97.7 | 99.9 | 100.0 | 98.1 | 100.0 | 100.0 | 96.1 | 100.0 | 100.0 |
| 200 | 93.6 | 95.6 | 100.0 | 97.1 | 100.0 | 100.0 | 95.0 | 100.0 | 100.0 |
| 300 | 88.1 | 62.0 | 99.6 | 90.0 | 99.2 | 100.0 | 65.6 | 99.9 | 100.0 |
| 500 | 0.4 | 8.7 | 63.8 | 1.6 | 79.1 | 99.9 | 0.8 | 94.9 | 99.9 |
| 659 | 0.0 | 1.1 | 17.1 | 0.0 | 49.9 | 99.0 | 0.0 | 79.1 | 99.1 |

## Exact recall against load, drawings, evaluation alphabets, 4,000 cells

Percent of cues, mean over seeds: clean cues for the local rules, 40% removed for
the pseudo-inverse.

| Load | 4.4% (AHA) k = 178 Pseudo-inverse | 4.4% (AHA) k = 178 Covariance | 4.4% (AHA) k = 178 Clipped binary | 2% (rat DG) k = 80 Pseudo-inverse | 2% (rat DG) k = 80 Covariance | 2% (rat DG) k = 80 Clipped binary | 1% k = 40 Pseudo-inverse | 1% k = 40 Covariance | 1% k = 40 Clipped binary | log-scaled k = 24 Pseudo-inverse | log-scaled k = 24 Covariance | log-scaled k = 24 Clipped binary |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 89.0 | 100.0 | 100.0 | 97.0 | 100.0 | 100.0 | 96.0 | 100.0 | 100.0 | 98.0 | 100.0 | 100.0 |
| 30 | 92.0 | 100.0 | 100.0 | 98.7 | 100.0 | 100.0 | 96.7 | 100.0 | 100.0 | 99.3 | 100.0 | 100.0 |
| 50 | 92.4 | 100.0 | 100.0 | 90.8 | 100.0 | 100.0 | 98.4 | 100.0 | 100.0 | 97.6 | 100.0 | 100.0 |
| 70 | 89.7 | 100.0 | 100.0 | 96.3 | 100.0 | 100.0 | 97.4 | 100.0 | 100.0 | 97.1 | 100.0 | 100.0 |
| 100 | 90.4 | 100.0 | 100.0 | 97.2 | 100.0 | 100.0 | 98.4 | 100.0 | 100.0 | 97.6 | 100.0 | 100.0 |
| 150 | 89.1 | 99.9 | 100.0 | 98.3 | 100.0 | 100.0 | 98.0 | 100.0 | 100.0 | 96.9 | 100.0 | 100.0 |
| 200 | 89.2 | 99.0 | 100.0 | 95.6 | 100.0 | 100.0 | 97.2 | 100.0 | 100.0 | 96.3 | 100.0 | 100.0 |
| 300 | 89.2 | 78.5 | 100.0 | 95.8 | 100.0 | 100.0 | 98.3 | 100.0 | 100.0 | 96.7 | 100.0 | 100.0 |
| 500 | 87.4 | 17.1 | 99.9 | 94.8 | 96.3 | 100.0 | 97.5 | 100.0 | 100.0 | 96.2 | 100.0 | 100.0 |
| 659 | 86.8 | 3.8 | 94.3 | 90.6 | 81.6 | 100.0 | 95.7 | 99.2 | 100.0 | 92.0 | 99.6 | 100.0 |

## Run time

Wall-clock minutes per seed on one machine, 3 threads per process.

| Source | Cells | k | Rule | Seeds | Highest load | Minutes per seed |
|---|---|---|---|---|---|---|
| Drawings, background alphabets | 225 | 3 | Covariance | 5 | 964 | 0.0 |
| Drawings, background alphabets | 225 | 3 | Pseudo-inverse | 5 | 200 | 0.0 |
| Drawings, background alphabets | 225 | 3 | Clipped binary | 5 | 964 | 0.0 |
| Drawings, background alphabets | 225 | 5 | Covariance | 5 | 964 | 0.0 |
| Drawings, background alphabets | 225 | 5 | Pseudo-inverse | 5 | 200 | 0.0 |
| Drawings, background alphabets | 225 | 5 | Clipped binary | 5 | 964 | 0.0 |
| Drawings, background alphabets | 225 | 10 | Covariance | 5 | 964 | 0.0 |
| Drawings, background alphabets | 225 | 10 | Pseudo-inverse | 5 | 200 | 0.0 |
| Drawings, background alphabets | 225 | 10 | Clipped binary | 5 | 964 | 0.0 |
| Drawings, background alphabets | 225 | 16 | Covariance | 5 | 964 | 0.0 |
| Drawings, background alphabets | 225 | 16 | Pseudo-inverse | 5 | 200 | 0.0 |
| Drawings, background alphabets | 225 | 16 | Clipped binary | 5 | 964 | 0.0 |
| Drawings, background alphabets | 1,000 | 10 | Covariance | 5 | 964 | 0.1 |
| Drawings, background alphabets | 1,000 | 10 | Pseudo-inverse | 5 | 964 | 0.1 |
| Drawings, background alphabets | 1,000 | 10 | Clipped binary | 5 | 964 | 0.1 |
| Drawings, background alphabets | 1,000 | 20 | Covariance | 5 | 964 | 0.1 |
| Drawings, background alphabets | 1,000 | 20 | Pseudo-inverse | 5 | 964 | 0.1 |
| Drawings, background alphabets | 1,000 | 20 | Clipped binary | 5 | 964 | 0.1 |
| Drawings, background alphabets | 1,000 | 44 | Covariance | 5 | 964 | 0.1 |
| Drawings, background alphabets | 1,000 | 44 | Pseudo-inverse | 5 | 964 | 0.1 |
| Drawings, background alphabets | 1,000 | 44 | Clipped binary | 5 | 964 | 0.1 |
| Drawings, background alphabets | 4,000 | 24 | Covariance | 5 | 964 | 0.4 |
| Drawings, background alphabets | 4,000 | 24 | Pseudo-inverse | 5 | 964 | 0.3 |
| Drawings, background alphabets | 4,000 | 24 | Clipped binary | 5 | 964 | 0.1 |
| Drawings, background alphabets | 4,000 | 40 | Covariance | 5 | 964 | 0.4 |
| Drawings, background alphabets | 4,000 | 40 | Pseudo-inverse | 5 | 964 | 0.4 |
| Drawings, background alphabets | 4,000 | 40 | Clipped binary | 5 | 964 | 0.1 |
| Drawings, background alphabets | 4,000 | 80 | Covariance | 5 | 964 | 0.6 |
| Drawings, background alphabets | 4,000 | 80 | Pseudo-inverse | 5 | 964 | 0.4 |
| Drawings, background alphabets | 4,000 | 80 | Clipped binary | 5 | 964 | 0.2 |
| Drawings, background alphabets | 4,000 | 178 | Covariance | 5 | 964 | 0.7 |
| Drawings, background alphabets | 4,000 | 178 | Pseudo-inverse | 5 | 964 | 0.3 |
| Drawings, background alphabets | 4,000 | 178 | Clipped binary | 5 | 964 | 0.5 |
| Drawings, evaluation alphabets | 225 | 3 | Covariance | 10 | 659 | 0.0 |
| Drawings, evaluation alphabets | 225 | 3 | Pseudo-inverse | 10 | 200 | 0.0 |
| Drawings, evaluation alphabets | 225 | 3 | Clipped binary | 10 | 659 | 0.0 |
| Drawings, evaluation alphabets | 225 | 5 | Covariance | 10 | 659 | 0.0 |
| Drawings, evaluation alphabets | 225 | 5 | Pseudo-inverse | 10 | 200 | 0.0 |
| Drawings, evaluation alphabets | 225 | 5 | Clipped binary | 10 | 659 | 0.0 |
| Drawings, evaluation alphabets | 225 | 10 | Covariance | 10 | 659 | 0.0 |
| Drawings, evaluation alphabets | 225 | 10 | Pseudo-inverse | 10 | 200 | 0.0 |
| Drawings, evaluation alphabets | 225 | 10 | Clipped binary | 10 | 659 | 0.0 |
| Drawings, evaluation alphabets | 225 | 16 | Covariance | 10 | 659 | 0.0 |
| Drawings, evaluation alphabets | 225 | 16 | Pseudo-inverse | 10 | 200 | 0.0 |
| Drawings, evaluation alphabets | 225 | 16 | Clipped binary | 10 | 659 | 0.0 |
| Drawings, evaluation alphabets | 1,000 | 10 | Covariance | 10 | 659 | 0.1 |
| Drawings, evaluation alphabets | 1,000 | 10 | Pseudo-inverse | 10 | 659 | 0.1 |
| Drawings, evaluation alphabets | 1,000 | 10 | Clipped binary | 10 | 659 | 0.1 |
| Drawings, evaluation alphabets | 1,000 | 20 | Covariance | 10 | 659 | 0.1 |
| Drawings, evaluation alphabets | 1,000 | 20 | Pseudo-inverse | 10 | 659 | 0.1 |
| Drawings, evaluation alphabets | 1,000 | 20 | Clipped binary | 10 | 659 | 0.1 |
| Drawings, evaluation alphabets | 1,000 | 44 | Covariance | 10 | 659 | 0.1 |
| Drawings, evaluation alphabets | 1,000 | 44 | Pseudo-inverse | 10 | 659 | 0.1 |
| Drawings, evaluation alphabets | 1,000 | 44 | Clipped binary | 10 | 659 | 0.1 |
| Drawings, evaluation alphabets | 4,000 | 24 | Covariance | 5 | 659 | 0.4 |
| Drawings, evaluation alphabets | 4,000 | 24 | Pseudo-inverse | 5 | 659 | 0.3 |
| Drawings, evaluation alphabets | 4,000 | 24 | Clipped binary | 5 | 659 | 0.1 |
| Drawings, evaluation alphabets | 4,000 | 40 | Covariance | 5 | 659 | 0.2 |
| Drawings, evaluation alphabets | 4,000 | 40 | Pseudo-inverse | 5 | 659 | 0.4 |
| Drawings, evaluation alphabets | 4,000 | 40 | Clipped binary | 5 | 659 | 0.1 |
| Drawings, evaluation alphabets | 4,000 | 80 | Covariance | 5 | 659 | 0.5 |
| Drawings, evaluation alphabets | 4,000 | 80 | Pseudo-inverse | 5 | 659 | 0.4 |
| Drawings, evaluation alphabets | 4,000 | 80 | Clipped binary | 5 | 659 | 0.1 |
| Drawings, evaluation alphabets | 4,000 | 178 | Covariance | 5 | 659 | 0.6 |
| Drawings, evaluation alphabets | 4,000 | 178 | Pseudo-inverse | 5 | 659 | 0.3 |
| Drawings, evaluation alphabets | 4,000 | 178 | Clipped binary | 5 | 659 | 0.4 |
| Random patterns | 225 | 3 | Covariance | 10 | 3,000 | 0.0 |
| Random patterns | 225 | 3 | Pseudo-inverse | 10 | 200 | 0.0 |
| Random patterns | 225 | 3 | Clipped binary | 10 | 1,000 | 0.0 |
| Random patterns | 225 | 5 | Covariance | 10 | 1,500 | 0.0 |
| Random patterns | 225 | 5 | Pseudo-inverse | 10 | 150 | 0.0 |
| Random patterns | 225 | 5 | Clipped binary | 10 | 1,000 | 0.0 |
| Random patterns | 225 | 10 | Covariance | 10 | 500 | 0.0 |
| Random patterns | 225 | 10 | Pseudo-inverse | 10 | 150 | 0.0 |
| Random patterns | 225 | 10 | Clipped binary | 10 | 500 | 0.0 |
| Random patterns | 225 | 16 | Covariance | 10 | 300 | 0.0 |
| Random patterns | 225 | 16 | Pseudo-inverse | 10 | 150 | 0.0 |
| Random patterns | 225 | 16 | Clipped binary | 10 | 300 | 0.0 |
| Random patterns | 1,000 | 10 | Covariance | 10 | 7,000 | 0.2 |
| Random patterns | 1,000 | 10 | Pseudo-inverse | 10 | 700 | 0.0 |
| Random patterns | 1,000 | 10 | Clipped binary | 10 | 7,000 | 0.2 |
| Random patterns | 1,000 | 20 | Covariance | 10 | 3,000 | 0.2 |
| Random patterns | 1,000 | 20 | Pseudo-inverse | 10 | 700 | 0.1 |
| Random patterns | 1,000 | 20 | Clipped binary | 10 | 3,000 | 0.1 |
| Random patterns | 1,000 | 44 | Covariance | 10 | 1,500 | 0.1 |
| Random patterns | 1,000 | 44 | Pseudo-inverse | 10 | 700 | 0.1 |
| Random patterns | 1,000 | 44 | Clipped binary | 10 | 1,000 | 0.1 |
| Random patterns | 4,000 | 24 | Covariance | 5 | 30,000 | 0.8 |
| Random patterns | 4,000 | 24 | Pseudo-inverse | 5 | 3,000 | 1.0 |
| Random patterns | 4,000 | 24 | Clipped binary | 5 | 50,000 | 0.8 |
| Random patterns | 4,000 | 40 | Covariance | 5 | 20,000 | 0.9 |
| Random patterns | 4,000 | 40 | Pseudo-inverse | 5 | 3,000 | 1.0 |
| Random patterns | 4,000 | 40 | Clipped binary | 5 | 20,000 | 0.6 |
| Random patterns | 4,000 | 80 | Covariance | 5 | 10,000 | 0.7 |
| Random patterns | 4,000 | 80 | Pseudo-inverse | 5 | 3,000 | 1.0 |
| Random patterns | 4,000 | 80 | Clipped binary | 5 | 7,000 | 0.4 |
| Random patterns | 4,000 | 178 | Covariance | 5 | 5,000 | 0.7 |
| Random patterns | 4,000 | 178 | Pseudo-inverse | 5 | 2,000 | 0.3 |
| Random patterns | 4,000 | 178 | Clipped binary | 5 | 1,500 | 0.3 |
| Random patterns | 16,000 | 28 | Covariance | 1 | 500,000 | 21.1 |
| Random patterns | 16,000 | 28 | Clipped binary | 1 | 500,000 | 21.0 |
| Random patterns | 16,000 | 160 | Pseudo-inverse | 2 | 10,000 | 44.6 |
| Random patterns | 16,000 | 320 | Covariance | 5 | 30,000 | 5.6 |
| Random patterns | 16,000 | 320 | Pseudo-inverse | 4 | 10,000 | 34.4 |
| Random patterns | 16,000 | 320 | Clipped binary | 5 | 10,000 | 3.0 |
| Random patterns | 16,000 | 711 | Covariance | 5 | 10,000 | 3.6 |
| Random patterns | 16,000 | 711 | Pseudo-inverse | 5 | 7,000 | 11.6 |
| Random patterns | 16,000 | 711 | Clipped binary | 5 | 2,000 | 3.6 |

## Notes

- 1% of 225 cells is under 3 cells, so this run uses 3.
- Random patterns, Pseudo-inverse at 16,000 cells with 160 active stopped early, with 2 seeds: the pseudo-inverse at this size filled the machine's memory (protocol item 14a).
- Random patterns, Pseudo-inverse at 16,000 cells with 320 active stopped early, with 4 seeds: the pseudo-inverse at this size filled the machine's memory (protocol item 14a).
