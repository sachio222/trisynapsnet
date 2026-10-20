#!/usr/bin/env bash
# E1c: how close does CA3 come to an ideal nearest-memory lookup without a
# list of memories, and does settling help CA1 rebuild the drawing?
#
# Phase A: CA3 on its own with random patterns at 225, 1,000 and 4,000
#          cells, and with DG patterns of background-alphabet drawings at
#          225 and 1,000 cells as a check before the evaluation alphabets.
# Phase B: CA3 on its own with DG patterns of evaluation-alphabet drawings,
#          the reported run.
# Phase C: the full model end to end on evaluation-alphabet drawings: study
#          20, 100 or 200 at once, recall occluded and noisy copies.
#
# Every CA3 rule runs: pinverse (AHA's), covariance and willshaw (local).
# Seeds: 10 at 225 and 1,000 cells, 5 at 4,000 cells and end to end.
#
# Usage: scripts/run_e1c.sh [A|B|C|all]   (PYTHON=/path/to/python to pick one)
# A result file that already exists is kept, so the script can resume.
# Logs go to results/logs/.

set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PYTHON:-python}
PHASE=${1:-all}
mkdir -p results/logs

RULES="pinverse covariance willshaw"
LOADS="20 50 100 200 500 1000"
# Random patterns only: higher loads at the larger sizes, to find where
# each rule fails there. Labelled as an extension in the table.
EXTRA_LOADS="2000 5000 10000"

seeds_for() { if [ "$1" = "4000" ]; then echo 5; else echo 10; fi; }
k_for() { case $1 in 225) echo 10;; 1000) echo 44;; 4000) echo 178;; esac; }

ca3() {
    # ca3 <source> <split> <units> <rule> <seeds> <loads...>
    local source=$1 split=$2 units=$3 rule=$4 seeds=$5
    shift 5
    local k tag name
    k=$(k_for "$units")
    if [ "$source" = "random" ]; then tag=random; else tag="drawings_${split}"; fi
    name="e1c_ca3_${tag}_${rule}_${units}_${k}"
    if [ -f "results/${name}.json" ]; then
        echo "keep results/${name}.json"
        return
    fi
    echo "run ${name} ($(date +%H:%M:%S))"
    "$PY" -m trisynapsnet.eval.ca3space --source "$source" --split "$split" --units "$units" \
        --k "$k" --rule "$rule" --seeds "$seeds" --loads "$@" \
        --out "results/${name}.json" > "results/logs/${name}.log" 2>&1
}

if [ "$PHASE" = "A" ] || [ "$PHASE" = "all" ]; then
    for units in 225 1000 4000; do
        for rule in $RULES; do
            # shellcheck disable=SC2086
            if [ "$units" = "225" ]; then
                ca3 random evaluation "$units" "$rule" "$(seeds_for "$units")" $LOADS
            else
                ca3 random evaluation "$units" "$rule" "$(seeds_for "$units")" $LOADS $EXTRA_LOADS
            fi
        done
    done
    for units in 225 1000; do
        for rule in $RULES; do
            # shellcheck disable=SC2086
            ca3 drawings background "$units" "$rule" 5 $LOADS
        done
    done
fi

if [ "$PHASE" = "B" ] || [ "$PHASE" = "all" ]; then
    for units in 225 1000 4000; do
        for rule in $RULES; do
            # shellcheck disable=SC2086
            ca3 drawings evaluation "$units" "$rule" "$(seeds_for "$units")" $LOADS
        done
    done
fi

if [ "$PHASE" = "C" ] || [ "$PHASE" = "all" ]; then
    for load in 20 100 200; do
        for kind in occlusion noise; do
            name="e1c_e2e_evaluation_n${load}_${kind}"
            echo "run ${name} ($(date +%H:%M:%S))"
            # shellcheck disable=SC2086
            "$PY" -m trisynapsnet.eval.endtoend --load "$load" --kind "$kind" --seeds 5 \
                --rules $RULES > "results/logs/${name}.log" 2>&1
        done
    done
fi

if [ "$PHASE" = "all" ]; then
    "$PY" scripts/make_e1c_table.py > /dev/null
    echo "Wrote results/e1c.md and figures/e1c_*.pdf"
fi
