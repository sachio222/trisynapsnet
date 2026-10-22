#!/usr/bin/env bash
# E9: DG drives CA3 at recall as well as at storage (docs/e9_protocol.md).
#
# Every run recalls each list under four conditions from the same study:
# E8c's model, the EC-on control, and DG at recall at 1.9 and 17.1 units,
# one result file per condition.
#
# Phase K: a check that the code runs: one background list, one seed, every
#          arm and condition, written under results/logs/ and scored by
#          nothing.
# Phase A: background alphabets, 128 drawings, every arm, seeds 0 to 9 (the
#          same lists and wiring as E8b's and E8c's calibration runs); then
#          scripts/make_e9_table.py --calibrate writes the thresholds and
#          runs the reproduction checks (E8c's model equals E8c's background
#          signals and thresholds; starting-state signals equal in every
#          condition). The phase fails if a check fails.
# Phase C: evaluation alphabets, 128 drawings, every arm, seeds 200 to 209;
#          refuses to start unless the phase-A checks passed; scored once by
#          scripts/make_e9_table.py.
#
# Usage: scripts/run_e9.sh [K|A|C]
#   PYTHON=/path/to/python picks the interpreter.
# Every run writes its files after each seed and picks up after the last
# finished seed when started again.
# Set TSN_AHA4 (or AHA4) when aha4 does not sit next to this repo.

set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PYTHON:-python}
PHASE=${1:?phase K, A or C}
mkdir -p results/logs
if [ -n "${AHA4:-}" ]; then export TSN_AHA4="$AHA4"; fi

run_one() {
    local name=$1
    shift
    echo "run ${name} ($(date +%H:%M:%S))"
    if "$PY" -m trisynapsnet.eval.dgrecall run "$@" >> "results/logs/${name}.log" 2>&1; then
        echo "done ${name} ($(date +%H:%M:%S))"
    else
        echo "FAILED ${name} ($(date +%H:%M:%S)), see results/logs/${name}.log"
        return 1
    fi
}

case $PHASE in
K)
    run_one e9_check --split background --seeds 1 --lists 1 --out results/logs/e9_check
    ;;
A)
    run_one e9_background_n128_d1 --split background --load 128 \
        --out results/e9_background_n128_d1
    "$PY" scripts/make_e9_table.py --calibrate
    ;;
C)
    if [ ! -f results/e9_calibration.json ]; then
        echo "calibrate first (phase A)" >&2
        exit 1
    fi
    if ! "$PY" scripts/make_e9_table.py --check; then
        echo "the reproduction checks did not pass; the evaluation run does not start" >&2
        exit 1
    fi
    run_one e9_evaluation_n128_d1 --split evaluation --first-seed 200 --load 128 \
        --out results/e9_evaluation_n128_d1
    "$PY" scripts/make_e9_table.py
    ;;
*)
    echo "Unknown phase $PHASE" >&2
    exit 1
    ;;
esac
