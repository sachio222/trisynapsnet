#!/usr/bin/env bash
# E1: local learning rules in CA3.
#
# Phase A picks settings on 20 validation runs built from the background
# alphabets, 5 seeds each. Phase B scores Lake's 20 official runs once, 10
# seeds each, with settings chosen in Phase A only.
#
# A result file that already exists is kept, so the script can resume.
# Logs go to results/logs/.
#
# Usage: scripts/run_bio_e1.sh   (PYTHON=/path/to/python to pick an interpreter)

set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PYTHON:-python}
mkdir -p results/logs

SIZES="225:10 1000:44 4000:178 1000:10 4000:40"

run() {
    # run <runs> <seeds> <rule> <units> <k> <cue weight> [settling steps]
    local runs=$1 seeds=$2 rule=$3 units=$4 k=$5 cw=$6 iters=${7:-70}
    local name="bio_e1_${runs}_${rule}_${units}_${k}"
    if [ "$cw" != "0" ]; then name="${name}_cw${cw}"; fi
    if [ "$iters" != "70" ]; then name="${name}_it${iters}"; fi
    if [ -f "results/${name}.json" ]; then
        echo "keep results/${name}.json"
        return
    fi
    echo "run ${name}"
    "$PY" -m fh.eval.evaluate --normalise --runs "$runs" --seeds "$seeds" \
        --ca3-rule "$rule" --dg-units "$units" --dg-k "$k" --ca3-cue-weight "$cw" \
        --ca3-iters "$iters" --out "results/${name}.json" > "results/logs/${name}.log" 2>&1
    tail -n 9 "results/logs/${name}.log"
}

# Phase A: every rule at every size, no cue during settling.
for rule in pinverse hebbian covariance willshaw; do
    for size in $SIZES; do
        run background 5 "$rule" "${size%:*}" "${size#*:}" 0
    done
done

# Phase A: the best local rule at its best size, with the cue kept on.
read -r best units k <<< "$("$PY" scripts/make_e1_table.py --best-local)"
for cw in 0.5 1; do
    run background 5 "$best" "$units" "$k" "$cw"
done

# Phase A control: CA3 stores as usual but never settles, so its output is
# the k most active cells of the PR output. This shows what the recurrent
# settling adds, and it is the limit of a very large cue weight.
for rule in covariance willshaw; do
    run background 5 "$rule" 225 10 0 0
done
run background 5 "$best" "$units" "$k" 0 0

# Phase B: AHA's own setting as the control, then each local rule at the
# paper's size and at its best Phase A size.
run official 10 pinverse 225 10 0
run official 10 hebbian 225 10 0
run official 10 covariance 225 10 0 0
for rule in covariance willshaw; do
    run official 10 "$rule" 225 10 0
    read -r units k <<< "$("$PY" scripts/make_e1_table.py --best-size "$rule")"
    run official 10 "$rule" "$units" "$k" 0
done

"$PY" scripts/make_e1_table.py > /dev/null
echo "Wrote results/bio_e1.md"
