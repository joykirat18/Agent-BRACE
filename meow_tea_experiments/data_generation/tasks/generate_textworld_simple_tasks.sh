#!/bin/bash
# Generate tw-simple TextWorld tasks with goal=detailed and rewards=balanced
# Train: 1000, Valid: 100, Test: 200
# Uses parallel jobs for faster generation
# Test split uses --test to draw from test distribution

tw_base_seed_train=10000
tw_base_seed_valid=20000
tw_base_seed_test=30000

# Number of parallel jobs (default: number of CPU cores)
max_parallel_jobs=${MAX_PARALLEL_JOBS:-$(nproc 2>/dev/null || echo 8)}

tasks_dir="textworld-task/simple-detailed-balanced"
mkdir -p ${tasks_dir}/train ${tasks_dir}/valid ${tasks_dir}/test

generate_one() {
    local split=$1
    local i=$2
    local base_seed=$3
    local output_subdir=${tasks_dir}/${split}

    seed=$((base_seed + i))

    # Use --test only for test split (draws from test distribution)
    test_flag=""
    [[ "$split" == "test" ]] && test_flag="--test"

    tw-make tw-simple \
        --rewards balanced \
        --goal detailed \
        $test_flag \
        --seed $seed \
        --format z8 \
        --output ${output_subdir}/simple_${seed}.z8 \
        --silent
}

generate_split() {
    local split=$1
    local count=$2
    local base_seed=$3

    echo "Generating ${split} set (${count} games) with ${max_parallel_jobs} parallel jobs..."

    for i in $(seq 1 $count)
    do
        # Limit concurrent jobs
        while (( $(jobs -r 2>/dev/null | wc -l) >= max_parallel_jobs )); do
            sleep 0.2
        done
        generate_one "$split" "$i" "$base_seed" &
    done
    wait
}

echo "Using ${max_parallel_jobs} parallel jobs"
echo "tw-simple: goal=detailed, rewards=balanced"
echo ""

generate_split train 1000 $tw_base_seed_train
generate_split valid 100 $tw_base_seed_valid
generate_split test 200 $tw_base_seed_test

echo ""
echo "Done. Output: ${tasks_dir}/"
