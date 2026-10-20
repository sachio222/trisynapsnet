# E1b: settling item by item, test-to-study

CA3 rule: covariance. Evaluation-set runs, 10 seeds, corruption seed 0. Each row gives percent of test drawings (first five columns) or of study drawings (last column), pooled over runs and seeds. Made by scripts/e1b_transitions.py.

## Instance task

| corruption | level | settling right | no settling right | only settling right | only no settling right | settles exactly on right memory | study items with tied test states |
|---|---|---|---|---|---|---|---|
| none | 0 | 100.0 | 100.0 | 0.0 | 0.0 | 100.0 | 0.0 |
| occlusion | 0.1 | 99.9 | 99.9 | 0.0 | 0.0 | 99.9 | 0.1 |
| occlusion | 0.2 | 99.1 | 99.1 | 0.0 | 0.0 | 99.1 | 1.2 |
| occlusion | 0.3 | 97.5 | 97.5 | 0.1 | 0.1 | 97.5 | 3.4 |
| occlusion | 0.4 | 92.6 | 92.8 | 0.1 | 0.3 | 92.5 | 9.5 |
| occlusion | 0.5 | 78.2 | 78.3 | 0.4 | 0.5 | 78.2 | 25.1 |
| occlusion | 0.6 | 57.8 | 58.1 | 0.5 | 0.8 | 57.6 | 44.0 |
| occlusion | 0.7 | 37.1 | 37.5 | 0.5 | 0.9 | 37.0 | 55.8 |
| occlusion | 0.8 | 20.9 | 21.1 | 0.2 | 0.5 | 20.7 | 67.3 |
| occlusion | 0.9 | 10.7 | 10.6 | 0.4 | 0.3 | 10.5 | 80.7 |
| occlusion | 0.98 | 6.4 | 6.3 | 0.3 | 0.2 | 6.2 | 90.8 |
| noise | 0.1 | 87.8 | 88.0 | 0.2 | 0.3 | 87.8 | 16.1 |
| noise | 0.2 | 72.3 | 72.5 | 0.9 | 1.2 | 72.1 | 31.6 |
| noise | 0.3 | 48.9 | 48.7 | 1.2 | 1.0 | 48.6 | 53.2 |
| noise | 0.4 | 31.6 | 31.8 | 1.2 | 1.4 | 31.2 | 64.3 |
| noise | 0.5 | 14.9 | 15.3 | 0.6 | 0.9 | 14.8 | 74.2 |
| noise | 0.6 | 10.7 | 10.7 | 0.6 | 0.5 | 10.6 | 77.5 |
| noise | 0.7 | 6.4 | 6.2 | 0.6 | 0.4 | 6.2 | 81.1 |
| noise | 0.8 | 5.7 | 5.8 | 0.3 | 0.4 | 5.6 | 82.5 |
| noise | 0.9 | 5.2 | 5.3 | 0.2 | 0.3 | 5.1 | 84.1 |
| noise | 0.98 | 4.4 | 4.3 | 0.4 | 0.2 | 4.2 | 83.3 |

## Classification task

| corruption | level | settling right | no settling right | only settling right | only no settling right | settles exactly on right memory | study items with tied test states |
|---|---|---|---|---|---|---|---|
| none | 0 | 62.6 | 62.8 | 0.8 | 0.8 | 62.2 | 41.8 |
| occlusion | 0.1 | 62.5 | 62.6 | 0.8 | 0.8 | 62.1 | 41.8 |
| occlusion | 0.2 | 61.4 | 61.3 | 0.8 | 0.8 | 61.0 | 45.0 |
| occlusion | 0.3 | 57.8 | 57.5 | 0.8 | 0.6 | 57.4 | 44.2 |
| occlusion | 0.4 | 48.0 | 47.9 | 0.7 | 0.6 | 47.8 | 49.9 |
| occlusion | 0.5 | 39.0 | 39.0 | 0.8 | 0.8 | 38.8 | 51.9 |
| occlusion | 0.6 | 32.2 | 32.4 | 0.5 | 0.7 | 32.1 | 53.4 |
| occlusion | 0.7 | 19.7 | 19.7 | 0.3 | 0.2 | 19.6 | 59.1 |
| occlusion | 0.8 | 12.2 | 12.3 | 0.4 | 0.5 | 12.2 | 71.5 |
| occlusion | 0.9 | 6.6 | 6.6 | 0.4 | 0.4 | 6.5 | 85.8 |
| occlusion | 0.98 | 5.1 | 5.2 | 0.4 | 0.5 | 5.1 | 98.9 |
| noise | 0.1 | 59.4 | 59.3 | 1.1 | 1.0 | 59.1 | 44.0 |
| noise | 0.2 | 47.5 | 47.2 | 1.3 | 1.1 | 47.4 | 52.0 |
| noise | 0.3 | 34.3 | 34.6 | 1.1 | 1.4 | 34.1 | 59.0 |
| noise | 0.4 | 19.7 | 20.0 | 0.9 | 1.2 | 19.4 | 67.5 |
| noise | 0.5 | 10.9 | 11.3 | 0.6 | 0.9 | 10.8 | 75.8 |
| noise | 0.6 | 8.8 | 8.8 | 0.5 | 0.5 | 8.7 | 79.9 |
| noise | 0.7 | 7.4 | 7.2 | 0.6 | 0.5 | 7.3 | 84.2 |
| noise | 0.8 | 4.9 | 4.9 | 0.3 | 0.3 | 4.8 | 87.5 |
| noise | 0.9 | 5.5 | 5.5 | 0.2 | 0.2 | 5.5 | 88.8 |
| noise | 0.98 | 5.7 | 5.5 | 0.4 | 0.2 | 5.7 | 88.3 |
