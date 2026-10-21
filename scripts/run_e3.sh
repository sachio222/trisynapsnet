#!/usr/bin/env bash
# E3: a one-shot perforant path in place of PR.
#
# Phase A: background alphabets only. Score every perforant setting at the
#          CA3 stage (--grid) on the background validation runs and the
#          background instance runs, 5 seeds. scripts/make_e3_table.py
#          --select reads them and prints the settings the later phases take.
# Phase B: the full harness on the same background runs, 5 seeds, with the
#          chosen settings: the check before any evaluation run.
# Phase C: Lake's 20 runs and the evaluation instance task, 10 seeds, 2%.
# Phase D: E1c's end-to-end load runs, 20 to 200 drawings, 5 seeds, 2%.
# Phase E: Lake's runs and the instance task at 4.4%, 10 seeds, the check.
#
# Usage: WIL="..." COV="..." scripts/run_e3.sh [A|B|C|D|E|status]
#   status lists every E3 result file with its finished seeds and what remains.
#   PYTHON=/path/to/python picks the interpreter; JOBS=2 runs two at once.
#   WIL and COV hold the chosen settings as harness flags, e.g.
#   WIL="--wil-presynaptic above-mean --wil-emax 0.2" COV="--cov-normalise".
# Every run writes its file after each seed and picks up after the last
# finished seed when started again, so the script can be stopped and rerun.
# Set TSN_AHA4 (or AHA4) when aha4 does not sit next to this repo.

set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PYTHON:-python}
PHASE=${1:?phase A, B, C, D or E}
JOBS=${JOBS:-1}
CACHE=${CACHE:-data/cache}
WIL=${WIL:-}
COV=${COV:-}
mkdir -p results/logs
if [ -n "${AHA4:-}" ]; then export TSN_AHA4="$AHA4"; fi
export PY CACHE

run_one() {
    # run_one <name> <args...>
    local name=$1
    shift
    echo "run ${name} ($(date +%H:%M:%S))"
    "$PY" -m trisynapsnet.eval.perforant --cache-dir "$CACHE" "$@" --out "results/${name}.json" \
        >> "results/logs/${name}.log" 2>&1 && echo "done ${name} ($(date +%H:%M:%S))" \
        || echo "FAILED ${name} ($(date +%H:%M:%S)), see results/logs/${name}.log"
}
export -f run_one

parallel() {
    xargs -P "$JOBS" -L 1 bash -c 'eval run_one "$@"' _
}

need_settings() {
    if [ -z "$WIL" ] && [ -z "$COV" ]; then
        echo "Set WIL and COV from phase A first (scripts/make_e3_table.py --select)." >&2
        exit 1
    fi
}

case $PHASE in
status)
    "$PY" - <<'PYEOF'
import json, pathlib
plan = {"A": [("e3_grid_classification_background_225_5", 5), ("e3_grid_instance_background_225_5", 5)],
        "B": [("e3_classification_background_225_5", 5), ("e3_instance_background_225_5", 5)],
        "C": [("e3_classification_official_225_5", 10), ("e3_instance_official_225_5", 10)],
        "D": [("e3_load_official_n{}_225_5".format(n), 5) for n in (20, 50, 100, 200)],
        "E": [("e3_classification_official_225_10", 10), ("e3_instance_official_225_10", 10)]}
for phase, files in plan.items():
    for name, want in files:
        path = pathlib.Path("results") / (name + ".json")
        done = json.loads(path.read_text())["seeds_done"] if path.is_file() else []
        left = [s for s in range(want) if s not in done]
        print("{} {:<45} done {:>2}/{:<2} remaining seeds {}".format(
            phase, name, len(done), want, left if left else "none"))
PYEOF
    ;;
A)
    {
        echo "e3_grid_classification_background_225_5 --grid --task classification --runs background --seeds 5"
        echo "e3_grid_instance_background_225_5 --grid --task instance --runs background --seeds 5"
    } | parallel
    ;;
B)
    need_settings
    {
        echo "e3_classification_background_225_5 --task classification --runs background --seeds 5 $WIL $COV"
        echo "e3_instance_background_225_5 --task instance --runs background --seeds 5 $WIL $COV"
    } | parallel
    ;;
C)
    need_settings
    {
        echo "e3_classification_official_225_5 --task classification --seeds 10 $WIL $COV"
        echo "e3_instance_official_225_5 --task instance --seeds 10 $WIL $COV"
    } | parallel
    ;;
D)
    need_settings
    for load in 20 50 100 200; do
        echo "e3_load_official_n${load}_225_5 --task load --load ${load} --seeds 5 $WIL $COV"
    done | parallel
    ;;
E)
    need_settings
    {
        echo "e3_classification_official_225_10 --task classification --seeds 10 --dg-k 10 $WIL $COV"
        echo "e3_instance_official_225_10 --task instance --seeds 10 --dg-k 10 $WIL $COV"
    } | parallel
    ;;
*)
    echo "Unknown phase $PHASE" >&2
    exit 1
    ;;
esac
