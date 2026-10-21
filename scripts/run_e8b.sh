#!/usr/bin/env bash
# E8b: recall-based recognition, a hippocampus at human proportions, and
# closer lures (docs/e8b_protocol.md).
#
# Phase L: closer-lure levels from background drawings
#          (results/e8b_lure_levels.json).
# Phase A: background alphabets, 128 drawings, every arm, 10 seeds; then
# Phase B: background loads 20, 50, 100, 200, 256 and 2 and 4 drawings per
#          character at 128, the arms that share the intact study; then
#          scripts/make_e8b_table.py --calibrate writes the thresholds.
# Phase C: evaluation alphabets, 128 drawings, every arm.
# Phase D: evaluation loads and interference.
#
# Usage: scripts/run_e8b.sh [L|A|B|C|D|status]
#   PYTHON=/path/to/python picks the interpreter; JOBS=2 runs two at once.
# Every run writes its file after each seed and picks up after the last
# finished seed when started again.
# Set TSN_AHA4 (or AHA4) when aha4 does not sit next to this repo.

set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PYTHON:-python}
PHASE=${1:?phase L, A, B, C, D or status}
JOBS=${JOBS:-1}
mkdir -p results/logs
if [ -n "${AHA4:-}" ]; then export TSN_AHA4="$AHA4"; fi
export PY
SHARED="intact no_recurrent no_ca3 vc_baseline"

run_one() {
    local name=$1
    shift
    echo "run ${name} ($(date +%H:%M:%S))"
    "$PY" -m trisynapsnet.eval.recognition run "$@" --out "results/${name}.json" \
        >> "results/logs/${name}.log" 2>&1 && echo "done ${name} ($(date +%H:%M:%S))" \
        || echo "FAILED ${name} ($(date +%H:%M:%S)), see results/logs/${name}.log"
}
export -f run_one

parallel() {
    xargs -P "$JOBS" -L 1 bash -c 'eval run_one "$@"' _
}

variants() {
    # variants <split>: the load and interference runs of one split.
    for load in 20 50 100 200 256; do
        echo "e8b_$1_n${load}_d1 --split $1 --load ${load} --arms ${SHARED}"
    done
    for d in 2 4; do
        echo "e8b_$1_n128_d${d} --split $1 --load 128 --per-char ${d} --arms ${SHARED}"
    done
}

case $PHASE in
status)
    for f in results/e8b_*_n*_d*.json; do
        [ -f "$f" ] && "$PY" -c "import json,sys; r=json.load(open(sys.argv[1])); print(sys.argv[1], r['seeds_done'])" "$f"
    done
    ;;
L)
    "$PY" -m trisynapsnet.eval.recognition levels >> results/logs/e8b_levels.log 2>&1
    ;;
A)
    echo "e8b_background_n128_d1 --split background --load 128" | parallel
    ;;
B)
    variants background | parallel
    ;;
C)
    echo "e8b_evaluation_n128_d1 --split evaluation --load 128" | parallel
    ;;
D)
    variants evaluation | parallel
    ;;
*)
    echo "Unknown phase $PHASE" >&2
    exit 1
    ;;
esac
