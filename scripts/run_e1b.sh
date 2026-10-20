#!/usr/bin/env bash
# E1b: does CA3 settling help recall the same drawing from a corrupted cue?
#
# Every CA3 option is scored on two tasks, each under occlusion and under
# noise at AHA's 11 levels (none, 0.1 to 0.9, and 0.98). One call covers a
# whole sweep: each (seed, run) studies once and recalls every level.
#
#   pinverse     AHA's rule, 70 settling steps
#   covariance   local rule, k-WTA settling
#   willshaw     local rule, k-WTA settling
#   none         no settling: CA3 passes on the 10 most active PR cells
#                (covariance storage with --ca3-iters 0)
#
# Phase A: instance runs built from the background alphabets, 5 seeds, as a
# check before the evaluation alphabets. No setting is chosen from it.
# Phase B: the headline. Instance runs from the evaluation alphabets and
# Lake's 20 runs, 10 seeds.
# Phase C: Phase B again, matching test-to-study: each test drawing's state
# is matched to the nearest studied state, as a cued memory would be. Files
# end in _tts.
#
# Usage: scripts/run_e1b.sh [A|B|C|all]   (PYTHON=/path/to/python to pick one)
# A result file that already exists is kept, so the script can resume.
# Logs go to results/logs/.

set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PYTHON:-python}
PHASE=${1:-all}
mkdir -p results/logs

LEVELS="0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 0.98"
OPTIONS="pinverse:70 covariance:70 willshaw:70 covariance:0"

run() {
    # run <task> <runs> <seeds> <rule> <settling steps> <corruption> [match]
    local task=$1 runs=$2 seeds=$3 rule=$4 iters=$5 kind=$6 match=${7:-study-to-test}
    local name="e1b_${task}_${runs}_${rule}_225_10"
    if [ "$iters" != "70" ]; then name="${name}_it${iters}"; fi
    name="${name}_${kind}"
    if [ "$match" = "test-to-study" ]; then name="${name}_tts"; fi
    if [ -f "results/${name}.json" ]; then
        echo "keep results/${name}.json"
        return
    fi
    echo "run ${name} ($(date +%H:%M:%S))"
    # shellcheck disable=SC2086
    "$PY" -m trisynapsnet.eval.evaluate --normalise --task "$task" --runs "$runs" --seeds "$seeds" \
        --ca3-rule "$rule" --ca3-iters "$iters" --"$kind" $LEVELS --match "$match" \
        --out "results/${name}.json" > "results/logs/${name}.log" 2>&1
    grep -E "^Took" "results/logs/${name}.log"
}

sweep() {
    # sweep <task> <runs> <seeds> [match]
    for kind in occlusion noise; do
        for option in $OPTIONS; do
            run "$1" "$2" "$3" "${option%:*}" "${option#*:}" "$kind" "${4:-study-to-test}"
        done
    done
}

if [ "$PHASE" = "A" ] || [ "$PHASE" = "all" ]; then
    sweep instance background 5
fi
if [ "$PHASE" = "B" ] || [ "$PHASE" = "all" ]; then
    sweep instance official 10
    sweep classification official 10
fi
if [ "$PHASE" = "C" ] || [ "$PHASE" = "all" ]; then
    sweep instance official 10 test-to-study
    sweep classification official 10 test-to-study
fi

"$PY" scripts/make_e1b_table.py > /dev/null
echo "Wrote results/e1b.md and figures/e1b_*.pdf"
