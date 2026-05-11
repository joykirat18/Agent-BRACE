#!/bin/bash
# Generate TextWorld Treasure Hunter tasks with mixed difficulty across train/valid/test splits
# Train: 1000, Valid: 100, Test: 200
# Uses parallel jobs for faster generation
# Difficulty is controlled by --level (1=easiest .. 30=hardest); see: tw-make tw-treasure_hunter --help

tw_base_seed_train=10000
tw_base_seed_valid=20000
tw_base_seed_test=30000

# Parallel tw-make + Inform7 compiles are heavy; default caps at 16 (override with MAX_PARALLEL_JOBS).
if [[ -n "${MAX_PARALLEL_JOBS:-}" ]]; then
    max_parallel_jobs=$MAX_PARALLEL_JOBS
else
    _np=$(nproc 2>/dev/null || echo 8)
    if (( _np > 16 )); then
        max_parallel_jobs=16
    else
        max_parallel_jobs=$_np
    fi
fi
# Treasure Hunter sometimes cannot place a quest for a given map/seed; bump --seed until it succeeds.
max_seed_tries=${TW_MAKE_MAX_TRIES:-10}

tasks_dir="textworld-task/treasure-mixed"
mkdir -p ${tasks_dir}/train ${tasks_dir}/valid ${tasks_dir}/test

# Train: easy band (levels 1–8). Skip 9–10: quest length 5 in 5-room easy maps fails for many seeds.
train_levels=(
    1 2 4 6 8
)
# Validation & Test: higher levels
eval_levels=(
    14 16 18 20 22 25 28 30
)

_cleanup_tw_make_artifacts() {
    local z8_path=$1
    local base="${z8_path%.z8}"
    rm -f "$z8_path" "$base.json" "$base.ni" "${base}_overview.png" 2>/dev/null
}

# Hide Python tracebacks on failed attempts unless TW_MAKE_VERBOSE is set.
_tw_make_quiet() {
    if [[ -n "${TW_MAKE_VERBOSE:-}" ]]; then
        tw-make "$@"
    else
        tw-make "$@" 2>/dev/null
    fi
}

generate_one() {
    local split=$1
    local i=$2
    local base_seed=$3
    local level=$4
    local output_subdir=${tasks_dir}/${split}

    local canonical_seed=$((base_seed + i))
    local out_z8=${output_subdir}/treasure_${canonical_seed}.z8
    local ntry=0

    while (( ntry < max_seed_tries )); do
        local try_seed=$((canonical_seed + ntry))
        if _tw_make_quiet tw-treasure_hunter \
            --level "$level" \
            --seed "$try_seed" \
            --format z8 \
            --output "$out_z8" \
            --silent \
            -f; then
            return 0
        fi
        _cleanup_tw_make_artifacts "$out_z8"
        ((ntry++))
    done
    echo "ERROR: could not generate ${out_z8} (level=${level}) after ${max_seed_tries} seed offsets; try raising TW_MAKE_MAX_TRIES or lowering level" >&2
    return 1
}

generate_split() {
    local split=$1
    local count=$2
    local base_seed=$3

    if [[ "$split" == "train" ]]; then
        levels=("${train_levels[@]}")
    else
        levels=("${eval_levels[@]}")
    fi
    num_levels=${#levels[@]}

    echo "Generating ${split} set (${count} games, ${num_levels} difficulty levels) with ${max_parallel_jobs} parallel jobs..."

    for i in $(seq 1 $count)
    do
        while (( $(jobs -r 2>/dev/null | wc -l) >= max_parallel_jobs )); do
            sleep 0.2
        done
        level_idx=$(( (i - 1) % num_levels ))
        level=${levels[$level_idx]}
        generate_one "$split" "$i" "$base_seed" "$level" &
    done
    wait
}

echo "Using ${max_parallel_jobs} parallel jobs"
echo ""

# generate_split train 1000 $tw_base_seed_train
generate_split valid 100 $tw_base_seed_valid
generate_split test 200 $tw_base_seed_test

echo ""
echo "Done. Output: ${tasks_dir}/"
