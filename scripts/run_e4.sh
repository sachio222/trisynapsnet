#!/usr/bin/env bash
# E4: one-shot CA1. Replace PM's backpropagation with BTSP on CA3-to-CA1
# synapses and a Hebbian return to EC, then compare with backpropagation in
# EC space.
#
# Phase A: background alphabets only. Pick the plateau share for each CA1
#          size and whether plateau drive is measured against the mean
#          background EC code (scripts/make_e4_table.py --select reads it).
# Phase B: CA1 on its own, evaluation alphabets, 225 CA3 cells, 10 seeds,
#          loads 20 to 500, both CA1 sizes.
# Phase C: the same at 1,000 CA3 cells, 5 seeds.
# Phase D: Lake's 20 runs, 10 seeds, both matching directions, CA3 with the
#          covariance rule, every CA1 arm.
# Phase E: the instance task at occlusion and noise 0, 0.3 and 0.5.
#
# Usage: scripts/run_e4.sh [A|B|C|D|E]   (PYTHON=/path/to/python to pick one)
# The plateau shares come from phase A: set SHARE_HUMAN and SHARE_RAT.
# Pass the vision network and data with AHA4=/path/to/aha4 and the cached
# vision codes with CACHE=/path/to/data/cache when they are not in the
# standard layout. A result file that already exists is kept.

set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PYTHON:-python}
PHASE=${1:?phase A, B, C, D or E}
SHARE_HUMAN=${SHARE_HUMAN:-}
SHARE_RAT=${SHARE_RAT:-}
CACHE=${CACHE:-data/cache}
THREADS=${THREADS:-2}
SHARES="0.0025 0.005 0.01 0.02 0.05"
mkdir -p results/logs
if [ -n "${AHA4:-}" ]; then export TSN_AHA4="$AHA4"; fi

need_shares() {
    if [ -z "$SHARE_HUMAN" ] || [ -z "$SHARE_RAT" ]; then
        echo "Set SHARE_HUMAN and SHARE_RAT from phase A first." >&2
        exit 1
    fi
}

ca1() {
    # ca1 <name> <args...>
    local name=$1
    shift
    if [ -f "results/${name}.json" ]; then echo "keep results/${name}.json"; return; fi
    echo "run ${name} ($(date +%H:%M:%S))"
    "$PY" -m trisynapsnet.eval.ca1space --cache-dir "$CACHE" --threads "$THREADS" "$@" \
        --out "results/${name}.json" > "results/logs/${name}.log" 2>&1
}

evaluate() {
    # evaluate <name> <args...>
    local name=$1
    shift
    if [ -f "results/${name}.json" ]; then echo "keep results/${name}.json"; return; fi
    echo "run ${name} ($(date +%H:%M:%S))"
    "$PY" -m trisynapsnet.eval.evaluate --ca3-rule covariance --normalise --seeds 10 \
        --cache-dir "$CACHE" "$@" --out "results/${name}.json" > "results/logs/${name}.log" 2>&1
}

case $PHASE in
A)
    # shellcheck disable=SC2086
    ca1 e4_ca1_background_225_10_q0.0025_0.005_0.01_0.02_0.05 --split background --seeds 5 --shares $SHARES --no-pixels
    # shellcheck disable=SC2086
    ca1 e4_ca1_background_225_10_q0.0025_0.005_0.01_0.02_0.05_raw --split background --seeds 5 --shares $SHARES --no-pixels \
        --ec3-baseline none
    ;;
B)
    need_shares
    ca1 e4_ca1_evaluation_225_human --split evaluation --seeds 10 --ratios human --shares "$SHARE_HUMAN"
    ca1 e4_ca1_evaluation_225_rat --split evaluation --seeds 10 --ratios rat --shares "$SHARE_RAT"
    ;;
C)
    need_shares
    ca1 e4_ca1_evaluation_1000_human --split evaluation --units 1000 --seeds 5 --ratios human \
        --shares "$SHARE_HUMAN" --no-pixels
    ca1 e4_ca1_evaluation_1000_rat --split evaluation --units 1000 --seeds 5 --ratios rat \
        --shares "$SHARE_RAT" --no-pixels
    ;;
D|E)
    need_shares
    if [ "$PHASE" = "D" ]; then
        TASKS="classification:none"
    else
        TASKS="instance:occlusion instance:noise"
    fi
    for task_kind in $TASKS; do
        task=${task_kind%%:*}
        kind=${task_kind##*:}
        corruption=()
        if [ "$kind" != "none" ]; then corruption=(--"$kind" 0 0.3 0.5); fi
        for match in study-to-test test-to-study; do
            tag=$([ "$match" = "test-to-study" ] && echo "_tts" || echo "")
            base="e4_${task}_official_covariance_225_10"
            sfx=$([ "$kind" != "none" ] && echo "_${kind}" || echo "")
            evaluate "${base}_pm${sfx}${tag}" --task "$task" --match "$match" ${corruption[@]+"${corruption[@]}"}
            evaluate "${base}_btsp_human${sfx}${tag}" --task "$task" --match "$match" \
                ${corruption[@]+"${corruption[@]}"} --ca1-rule btsp --ca1-units 2118 --ca1-plateau-share "$SHARE_HUMAN"
            evaluate "${base}_btsp_rat${sfx}${tag}" --task "$task" --match "$match" \
                ${corruption[@]+"${corruption[@]}"} --ca1-rule btsp --ca1-units 375 --ca1-plateau-share "$SHARE_RAT"
            evaluate "${base}_backprop_ec${sfx}${tag}" --task "$task" --match "$match" \
                ${corruption[@]+"${corruption[@]}"} --ca1-rule backprop_ec
            evaluate "${base}_backprop_ec_nol2${sfx}${tag}" --task "$task" --match "$match" \
                ${corruption[@]+"${corruption[@]}"} --ca1-rule backprop_ec --ca1-l2 0
        done
    done
    ;;
*)
    echo "Unknown phase $PHASE" >&2
    exit 1
    ;;
esac
