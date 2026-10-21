#!/usr/bin/env bash
# E8: similar-lure recognition, load, interference and virtual lesions.
#
# Phase A: background alphabets. Calibration runs (load 20, every arm, 10
#          seeds); then scripts/make_e8_table.py --calibrate writes the
#          thresholds and lure-bin edges to results/e8_calibration.json.
# Phase B: background check runs at loads 50, 100, 200 and with 2 and 4
#          drawings per character, the arms that share the intact study.
# Phase C: evaluation alphabets, load 20, every arm, 10 seeds.
# Phase D: evaluation alphabets, loads 50, 100, 200 and 2 and 4 drawings
#          per character.
#
# Usage: scripts/run_e8.sh [A|B|C|D|status]
#   PYTHON=/path/to/python picks the interpreter; JOBS=2 runs two at once.
# Every run writes its file after each seed and picks up after the last
# finished seed when started again.
# Set TSN_AHA4 (or AHA4) when aha4 does not sit next to this repo.

set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PYTHON:-python}
PHASE=${1:?phase A, B, C, D or status}
JOBS=${JOBS:-1}
mkdir -p results/logs
if [ -n "${AHA4:-}" ]; then export TSN_AHA4="$AHA4"; fi
export PY
SHARED="intact no_recurrent no_ca3 vc_baseline"

run_one() {
    local name=$1
    shift
    echo "run ${name} ($(date +%H:%M:%S))"
    "$PY" -m trisynapsnet.eval.behaviour "$@" --out "results/${name}.json" \
        >> "results/logs/${name}.log" 2>&1 && echo "done ${name} ($(date +%H:%M:%S))" \
        || echo "FAILED ${name} ($(date +%H:%M:%S)), see results/logs/${name}.log"
}
export -f run_one

parallel() {
    xargs -P "$JOBS" -L 1 bash -c 'eval run_one "$@"' _
}

variants() {
    # variants <split>: the load and interference runs of one split.
    for load in 50 100 200; do
        echo "e8_$1_n${load}_d1 --split $1 --load ${load} --arms ${SHARED}"
    done
    for d in 2 4; do
        echo "e8_$1_n20_d${d} --split $1 --load 20 --per-char ${d} --arms ${SHARED}"
    done
}

case $PHASE in
status)
    for f in results/e8_*_n*_d*.json; do
        [ -f "$f" ] && "$PY" -c "import json,sys; r=json.load(open(sys.argv[1])); print(sys.argv[1], r['seeds_done'])" "$f"
    done
    ;;
A)
    echo "e8_background_n20_d1 --split background --load 20" | parallel
    ;;
B)
    variants background | parallel
    ;;
C)
    echo "e8_evaluation_n20_d1 --split evaluation --load 20" | parallel
    ;;
D)
    variants evaluation | parallel
    ;;
*)
    echo "Unknown phase $PHASE" >&2
    exit 1
    ;;
esac
