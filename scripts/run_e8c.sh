#!/usr/bin/env bash
# E8c: a familiarity signal read from CA3's starting state
# (docs/e8c_protocol.md).
#
# Phase P: size of the held-out evaluation pool, no model run.
# Phase K: a check that the code runs: one background list, one seed, every
#          arm, written to results/logs/e8c_check.json and scored by nothing.
# Phase A: background alphabets, 128 drawings, every arm, seeds 0 to 9 (the
#          same lists and wiring as E8b's calibration run); then
#          scripts/make_e8c_table.py --calibrate writes the thresholds and
#          checks R1 and R2 against E8b's background file.
# Phase C: evaluation alphabets, 128 drawings, every arm, seeds 100 to 109,
#          lists built only from drawings E8b's 128-drawing evaluation lists
#          never used; scored once by scripts/make_e8c_table.py.
#
# Usage: scripts/run_e8c.sh [P|K|A|C]
#   PYTHON=/path/to/python picks the interpreter.
# Every run writes its file after each seed and picks up after the last
# finished seed when started again.
# Set TSN_AHA4 (or AHA4) when aha4 does not sit next to this repo.

set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PYTHON:-python}
PHASE=${1:?phase P, K, A or C}
mkdir -p results/logs
if [ -n "${AHA4:-}" ]; then export TSN_AHA4="$AHA4"; fi

run_one() {
    local name=$1
    shift
    echo "run ${name} ($(date +%H:%M:%S))"
    if "$PY" -m trisynapsnet.eval.starting run "$@" >> "results/logs/${name}.log" 2>&1; then
        echo "done ${name} ($(date +%H:%M:%S))"
    else
        echo "FAILED ${name} ($(date +%H:%M:%S)), see results/logs/${name}.log"
        return 1
    fi
}

case $PHASE in
P)
    "$PY" -m trisynapsnet.eval.starting pool
    ;;
K)
    run_one e8c_check --split background --seeds 1 --lists 1 --out results/logs/e8c_check.json
    ;;
A)
    run_one e8c_background_n128_d1 --split background --load 128 \
        --out results/e8c_background_n128_d1.json
    "$PY" scripts/make_e8c_table.py --calibrate
    ;;
C)
    if [ ! -f results/e8c_calibration.json ]; then
        echo "calibrate first (phase A)" >&2
        exit 1
    fi
    run_one e8c_evaluation_n128_d1 --split evaluation --pool e8b-unused --first-seed 100 \
        --load 128 --out results/e8c_evaluation_n128_d1.json
    "$PY" scripts/make_e8c_table.py
    ;;
*)
    echo "Unknown phase $PHASE" >&2
    exit 1
    ;;
esac
