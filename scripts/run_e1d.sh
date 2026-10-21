#!/usr/bin/env bash
# E1d: does CA3's capacity per cell stop falling with network size once DG
# and CA3 codes are as sparse as measured?
#
# Shares of active cells in DG and CA3: 4.4 (AHA), 2 (rat dentate gyrus),
# 1, and log (k = round(c log2 n), k = 20 at 1,000 cells). At 1,000 cells
# the 2% and log codes are the same, k = 20, and run once.
#
# Phase A: CA3 on its own with random patterns at 225, 1,000 and 4,000
#          cells, and with DG patterns of background-alphabet drawings, the
#          check before the evaluation alphabets.
# Phase B: CA3 on its own with DG patterns of evaluation-alphabet drawings,
#          the reported run.
# Phase C: random patterns at 16,000 cells, local rules only. Run it with
#          JOBS=1: each process holds two 16,000 by 16,000 matrices.
# Phase D: the full model at 225 cells with 5 of them active (2%, rounded
#          half up), on validation runs from the background alphabets:
#          Lake-style classification and the instance task under occlusion
#          and noise. The check before Lake's runs.
# Phase E: Phase D's runs on Lake's 20 runs and the evaluation-alphabet
#          instance runs, scored once.
#
# Every CA3 rule runs in phases A to C: pinverse (AHA's), covariance and
# willshaw (local). Phases D and E run covariance, willshaw and no settling
# (covariance storage with 0 settling steps), matched both ways.
#
# Usage: scripts/run_e1d.sh [A|B|C|D|E|all]
#   PYTHON=/path/to/python   interpreter
#   JOBS=3                   processes at once
#   TSN_AHA4=/path/to/aha4   when aha4 does not sit next to this repo
# A finished result file is kept and a partial one resumes from its last
# finished seed, so the script can be stopped and run again. Logs go to
# results/logs/.

set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PYTHON:-python}
JOBS=${JOBS:-3}
PHASE=${1:-all}
mkdir -p results/logs
export PYTHONDONTWRITEBYTECODE=1

RULES="pinverse covariance willshaw"
SPARSITIES="4.4 2 1 log"

k_for() {
    "$PY" -c "from trisynapsnet.eval.sparsecodes import active_cells; print(active_cells($1, '$2')[0])"
}

seeds_for() {
    # seeds_for <source> <units> <sparsity>
    case "$1:$2:$3" in
        background:*) echo 5;;
        *:225:*|*:1000:*) echo 10;;
        *:4000:*) echo 5;;
        # 1% and log-scaled ran after the memory stop, with 3 seeds to
        # bound run time.
        *:16000:1|*:16000:log) echo 3;;
        *:16000:*) echo 5;;
    esac
}

# One line per CA3 job: <source> <split> <units> <rule> <sparsity> <seeds>.
# Jobs that share (units, k) are listed once.
ca3_jobs() {
    local source=$1 split=$2 units
    shift 2
    for units in "$@"; do
        local seen=""
        for sparsity in $SPARSITIES; do
            local k
            k=$(k_for "$units" "$sparsity")
            case " $seen " in *" $k "*) continue;; esac
            seen="$seen $k"
            local tag=$split
            if [ "$source" = "random" ]; then tag=random; fi
            for rule in $RULES; do
                # The pseudo-inverse of a load-by-16,000 matrix ran the
                # machine out of memory; it runs up to 4,000 cells only.
                if [ "$rule" = "pinverse" ] && [ "$units" -gt 4000 ]; then continue; fi
                echo "$source $split $units $rule $sparsity $(seeds_for "$tag" "$units" "$sparsity")"
            done
        done
    done
}

run_ca3() {
    # run_ca3 <source> <split> <units> <rule> <sparsity> <seeds>
    local source=$1 split=$2 units=$3 rule=$4 sparsity=$5 seeds=$6 k tag name
    k=$(k_for "$units" "$sparsity")
    if [ "$source" = "random" ]; then tag=random; else tag="drawings_${split}"; fi
    name="e1d_ca3_${tag}_${rule}_${units}_${k}"
    echo "run ${name} ($(date +%H:%M:%S))"
    "$PY" -m trisynapsnet.eval.sparsecodes --source "$source" --split "$split" --units "$units" \
        --rule "$rule" --sparsity "$sparsity" --seeds "$seeds" \
        --out "results/${name}.json" >> "results/logs/${name}.log" 2>&1
    echo "done ${name} ($(date +%H:%M:%S))"
}
export -f run_ca3 k_for
export PY

parallel_ca3() {
    xargs -P "$JOBS" -L 1 bash -c 'run_ca3 "$@"' _
}

# The full model: one evaluate.py run per file.
run_e2e() {
    # run_e2e <task> <runs> <seeds> <option> <corruption> <match>
    local task=$1 runs=$2 seeds=$3 option=$4 kind=$5 match=$6
    local rule=${option%:*} iters=${option#*:}
    local name="e1d_e2e_${task}_${runs}_${rule}_225_5"
    if [ "$iters" != "70" ]; then name="${name}_it${iters}"; fi
    if [ "$kind" != "none" ]; then name="${name}_${kind}"; fi
    if [ "$match" = "test-to-study" ]; then name="${name}_tts"; fi
    if [ -f "results/${name}.json" ]; then
        echo "keep results/${name}.json"
        return
    fi
    local levels=()
    if [ "$kind" != "none" ]; then levels=("--${kind}" 0 0.3 0.5); fi
    echo "run ${name} ($(date +%H:%M:%S))"
    "$PY" -m trisynapsnet.eval.evaluate --normalise --task "$task" --runs "$runs" \
        --seeds "$seeds" --ca3-rule "$rule" --ca3-iters "$iters" --dg-units 225 --dg-k 5 \
        ${levels[@]+"${levels[@]}"} --match "$match" --out "results/${name}.json" \
        > "results/logs/${name}.log" 2>&1
    echo "done ${name} ($(date +%H:%M:%S))"
}
export -f run_e2e

e2e_jobs() {
    # e2e_jobs <runs> <seeds>
    for match in study-to-test test-to-study; do
        for option in covariance:70 willshaw:70 covariance:0; do
            echo "classification $1 $2 $option none $match"
            for kind in occlusion noise; do
                echo "instance $1 $2 $option $kind $match"
            done
        done
    done
}

parallel_e2e() {
    xargs -P "$JOBS" -L 1 bash -c 'run_e2e "$@"' _
}

if [ "$PHASE" = "A" ] || [ "$PHASE" = "all" ]; then
    ca3_jobs random evaluation 225 1000 4000 | parallel_ca3
    ca3_jobs drawings background 225 1000 4000 | parallel_ca3
fi
if [ "$PHASE" = "B" ] || [ "$PHASE" = "all" ]; then
    ca3_jobs drawings evaluation 225 1000 4000 | parallel_ca3
fi
if [ "$PHASE" = "C" ] || [ "$PHASE" = "all" ]; then
    ca3_jobs random evaluation 16000 | parallel_ca3
fi
if [ "$PHASE" = "D" ] || [ "$PHASE" = "all" ]; then
    e2e_jobs background 5 | parallel_e2e
fi
if [ "$PHASE" = "E" ] || [ "$PHASE" = "all" ]; then
    e2e_jobs official 10 | parallel_e2e
fi
if [ "$PHASE" = "all" ]; then
    "$PY" scripts/make_e1d_table.py > /dev/null
    echo "Wrote results/e1d.md and figures/e1d_*.pdf"
fi
