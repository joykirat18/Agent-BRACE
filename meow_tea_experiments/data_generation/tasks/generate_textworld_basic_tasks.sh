#!/bin/bash
# Generate basic/custom TextWorld tasks with mixed difficulty across train/valid/test splits
# Train: 1000, Valid: 100, Test: 200
# Uses parallel jobs for faster generation
# Config format: "world_size:nb_objects:quest_length"

tw_base_seed_train=10000
tw_base_seed_valid=20000
tw_base_seed_test=30000

# Number of parallel jobs (default: number of CPU cores)
max_parallel_jobs=${MAX_PARALLEL_JOBS:-$(nproc 2>/dev/null || echo 8)}

tasks_dir="textworld-task/basic-mixed"
mkdir -p ${tasks_dir}/train ${tasks_dir}/valid ${tasks_dir}/test

# Difficulty presets: "world_size:nb_objects:quest_length"
# Train: easier only (for generalization test - model sees only easier tasks)
train_configs=(
    "2:3:3"    # Easy: 2 rooms, 3 objects, 3-step quest
    "2:4:4"    # Easy: 2 rooms, 4 objects, 4-step quest
    "4:4:4"    # Medium: 4 rooms, 4 objects, 4-step quest
    "4:6:6"    # Medium-hard: 4 rooms, 6 objects, 6-step quest
)
# Validation & Test: include harder problems (max quest_length < 14)
eval_configs=(
    "6:6:8"     # Hard: 6 rooms, 6 objects, 8-step quest
    "6:8:10"    # Hard: 6 rooms, 8 objects, 10-step quest
    "8:8:12"    # Very hard: 8 rooms, 8 objects, 12-step quest
    "8:10:13"   # Very hard: 8 rooms, 10 objects, 13-step quest
    "8:12:13"   # Max: 8 rooms, 12 objects, 13-step quest (< 14)
)

generate_one() {
    local split=$1
    local i=$2
    local base_seed=$3
    local config=$4
    local output_subdir=${tasks_dir}/${split}

    IFS=':' read -r world_size nb_objects quest_length <<< "$config"

    seed=$((base_seed + i))

    tw-make custom \
        --world-size $world_size \
        --nb-objects $nb_objects \
        --quest-length $quest_length \
        --seed $seed \
        --format z8 \
        --output ${output_subdir}/basic_${seed}.z8 \
        --silent
}

generate_split() {
    local split=$1
    local count=$2
    local base_seed=$3

    # Use easier configs for train, harder configs for validation/test
    if [[ "$split" == "train" ]]; then
        configs=("${train_configs[@]}")
    else
        configs=("${eval_configs[@]}")
    fi
    num_configs=${#configs[@]}

    echo "Generating ${split} set (${count} games, ${num_configs} difficulty levels) with ${max_parallel_jobs} parallel jobs..."

    for i in $(seq 1 $count)
    do
        # Limit concurrent jobs
        while (( $(jobs -r 2>/dev/null | wc -l) >= max_parallel_jobs )); do
            sleep 0.2
        done
        config_idx=$(( (i - 1) % num_configs ))
        config=${configs[$config_idx]}
        generate_one "$split" "$i" "$base_seed" "$config" &
    done
    wait
}

echo "Using ${max_parallel_jobs} parallel jobs"
echo ""

generate_split train 1000 $tw_base_seed_train
generate_split valid 100 $tw_base_seed_valid
generate_split test 200 $tw_base_seed_test

echo ""
echo "Done. Output: ${tasks_dir}/"
