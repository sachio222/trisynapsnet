# E1: local learning rules in CA3

Accuracy is one-shot classification in percent, mean ± standard deviation across seeds, with normalised study-to-test matching. Self-recall is the share of study drawings whose own PR output settles CA3 on exactly the stored pattern, with the mean share of stored cells recovered in brackets. DG overlap is shared active DG cells over k, without refractory inhibition, for a study and test drawing of the same character and of different characters. CA3 steps is the most settling steps allowed; local rules stop early once the state stops changing, and 0 means CA3 passes on the k most active cells of the PR output.

## Phase A: validation runs from the background alphabets, 5 seeds

| runs | rule | units | k | coding level | cue weight | CA3 steps | VC | PR | PC | PM | self-recall exact (overlap) | DG overlap same / diff | seconds |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| background | pinverse | 225 | 10 | 4.4% | 0 | 70 | 69.5 ± 0.0 | 75.9 ± 1.1 | 65.2 ± 1.5 | 67.1 ± 2.0 | 100.0% (1.00) | 0.29 / 0.15 | 90 |
| background | pinverse | 1000 | 44 | 4.4% | 0 | 70 | 69.5 ± 0.0 | 77.1 ± 0.8 | 66.0 ± 0.6 | 59.8 ± 1.7 | 100.0% (1.00) | 0.29 / 0.15 | 114 |
| background | pinverse | 4000 | 178 | 4.5% | 0 | 70 | 69.5 ± 0.0 | 78.6 ± 0.4 | 66.2 ± 1.0 | 60.1 ± 1.2 | 100.0% (1.00) | 0.29 / 0.15 | 192 |
| background | pinverse | 1000 | 10 | 1.0% | 0 | 70 | 69.5 ± 0.0 | 77.9 ± 0.5 | 64.7 ± 0.6 | 60.6 ± 1.2 | 100.0% (1.00) | 0.18 / 0.07 | 109 |
| background | pinverse | 4000 | 40 | 1.0% | 0 | 70 | 69.5 ± 0.0 | 77.8 ± 0.4 | 63.6 ± 1.5 | 52.8 ± 1.6 | 100.0% (1.00) | 0.19 / 0.07 | 190 |
| background | hebbian | 225 | 10 | 4.4% | 0 | 70 | 69.5 ± 0.0 | 75.9 ± 1.1 | 6.1 ± 0.3 | 6.3 ± 0.3 | 0.0% (0.00) | 0.29 / 0.15 | 87 |
| background | hebbian | 1000 | 44 | 4.4% | 0 | 70 | 69.5 ± 0.0 | 77.1 ± 0.8 | 8.2 ± 0.7 | 6.8 ± 0.7 | 0.0% (0.00) | 0.29 / 0.15 | 90 |
| background | hebbian | 4000 | 178 | 4.5% | 0 | 70 | 69.5 ± 0.0 | 78.6 ± 0.4 | 10.1 ± 1.3 | 5.8 ± 0.3 | 0.0% (0.00) | 0.29 / 0.15 | 155 |
| background | hebbian | 1000 | 10 | 1.0% | 0 | 70 | 69.5 ± 0.0 | 77.9 ± 0.5 | 6.0 ± 0.4 | 5.8 ± 0.6 | 0.0% (0.00) | 0.18 / 0.07 | 90 |
| background | hebbian | 4000 | 40 | 1.0% | 0 | 70 | 69.5 ± 0.0 | 77.8 ± 0.4 | 5.9 ± 0.5 | 5.0 ± 0.4 | 0.0% (0.00) | 0.19 / 0.07 | 156 |
| background | covariance | 225 | 10 | 4.4% | 0 | 70 | 69.5 ± 0.0 | 75.9 ± 1.1 | 60.6 ± 1.1 | 62.2 ± 1.2 | 100.0% (1.00) | 0.29 / 0.15 | 69 |
| background | covariance | 225 | 10 | 4.4% | 0 | 0 | 69.5 ± 0.0 | 75.9 ± 1.1 | 68.8 ± 1.9 | 70.2 ± 2.4 | 100.0% (1.00) | 0.29 / 0.15 | 68 |
| background | covariance | 1000 | 44 | 4.4% | 0 | 70 | 69.5 ± 0.0 | 77.1 ± 0.8 | 61.4 ± 0.5 | 62.2 ± 0.4 | 100.0% (1.00) | 0.29 / 0.15 | 84 |
| background | covariance | 1000 | 44 | 4.4% | 0 | 0 | 69.5 ± 0.0 | 77.1 ± 0.8 | 72.3 ± 1.0 | 72.0 ± 1.2 | 100.0% (1.00) | 0.29 / 0.15 | 84 |
| background | covariance | 1000 | 44 | 4.4% | 0.5 | 70 | 69.5 ± 0.0 | 77.1 ± 0.8 | 65.7 ± 1.5 | 65.1 ± 1.1 | 100.0% (1.00) | 0.29 / 0.15 | 89 |
| background | covariance | 1000 | 44 | 4.4% | 1 | 70 | 69.5 ± 0.0 | 77.1 ± 0.8 | 67.8 ± 1.4 | 67.0 ± 0.9 | 100.0% (1.00) | 0.29 / 0.15 | 89 |
| background | covariance | 4000 | 178 | 4.5% | 0 | 70 | 69.5 ± 0.0 | 78.6 ± 0.4 | 60.8 ± 1.4 | 61.4 ± 0.6 | 100.0% (1.00) | 0.29 / 0.15 | 146 |
| background | covariance | 1000 | 10 | 1.0% | 0 | 70 | 69.5 ± 0.0 | 77.9 ± 0.5 | 59.8 ± 0.9 | 62.5 ± 1.5 | 100.0% (1.00) | 0.18 / 0.07 | 85 |
| background | covariance | 4000 | 40 | 1.0% | 0 | 70 | 69.5 ± 0.0 | 77.8 ± 0.4 | 59.7 ± 0.7 | 62.1 ± 0.7 | 100.0% (1.00) | 0.19 / 0.07 | 146 |
| background | willshaw | 225 | 10 | 4.4% | 0 | 70 | 69.5 ± 0.0 | 75.9 ± 1.1 | 61.0 ± 1.2 | 62.4 ± 1.1 | 100.0% (1.00) | 0.29 / 0.15 | 69 |
| background | willshaw | 225 | 10 | 4.4% | 0 | 0 | 69.5 ± 0.0 | 75.9 ± 1.1 | 68.8 ± 1.9 | 70.2 ± 2.4 | 100.0% (1.00) | 0.29 / 0.15 | 68 |
| background | willshaw | 1000 | 44 | 4.4% | 0 | 70 | 69.5 ± 0.0 | 77.1 ± 0.8 | 61.3 ± 0.5 | 62.1 ± 0.4 | 100.0% (1.00) | 0.29 / 0.15 | 84 |
| background | willshaw | 4000 | 178 | 4.5% | 0 | 70 | 69.5 ± 0.0 | 78.6 ± 0.4 | 60.7 ± 1.2 | 61.2 ± 0.6 | 100.0% (1.00) | 0.29 / 0.15 | 146 |
| background | willshaw | 1000 | 10 | 1.0% | 0 | 70 | 69.5 ± 0.0 | 77.9 ± 0.5 | 59.8 ± 0.9 | 62.5 ± 1.5 | 100.0% (1.00) | 0.18 / 0.07 | 85 |
| background | willshaw | 4000 | 40 | 1.0% | 0 | 70 | 69.5 ± 0.0 | 77.8 ± 0.4 | 59.7 ± 0.7 | 62.1 ± 0.7 | 100.0% (1.00) | 0.19 / 0.07 | 146 |

## Phase B: Lake's 20 official runs, 10 seeds

| runs | rule | units | k | coding level | cue weight | CA3 steps | VC | PR | PC | PM | self-recall exact (overlap) | DG overlap same / diff | seconds |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| official | pinverse | 225 | 10 | 4.4% | 0 | 70 | 63.0 ± 0.0 | 70.6 ± 1.4 | 61.5 ± 0.7 | 62.5 ± 1.1 | 100.0% (1.00) | 0.28 / 0.17 | 150 |
| official | hebbian | 225 | 10 | 4.4% | 0 | 70 | 63.0 ± 0.0 | 70.6 ± 1.4 | 5.8 ± 0.5 | 5.9 ± 0.7 | 0.0% (0.00) | 0.28 / 0.17 | 149 |
| official | covariance | 225 | 10 | 4.4% | 0 | 70 | 63.0 ± 0.0 | 70.6 ± 1.4 | 53.8 ± 1.3 | 54.8 ± 1.4 | 100.0% (1.00) | 0.28 / 0.17 | 137 |
| official | covariance | 225 | 10 | 4.4% | 0 | 0 | 63.0 ± 0.0 | 70.6 ± 1.4 | 64.3 ± 1.0 | 64.1 ± 1.4 | 100.0% (1.00) | 0.28 / 0.17 | 136 |
| official | covariance | 1000 | 44 | 4.4% | 0 | 70 | 63.0 ± 0.0 | 73.3 ± 0.8 | 54.8 ± 1.3 | 56.3 ± 1.3 | 100.0% (1.00) | 0.29 / 0.17 | 167 |
| official | willshaw | 225 | 10 | 4.4% | 0 | 70 | 63.0 ± 0.0 | 70.6 ± 1.4 | 54.2 ± 0.9 | 55.2 ± 1.0 | 100.0% (1.00) | 0.28 / 0.17 | 139 |
| official | willshaw | 1000 | 44 | 4.4% | 0 | 70 | 63.0 ± 0.0 | 73.3 ± 0.8 | 54.7 ± 1.1 | 56.2 ± 1.1 | 100.0% (1.00) | 0.29 / 0.17 | 167 |
