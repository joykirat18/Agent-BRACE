#!/bin/bash
# Generate cooking tasks with mixed difficulty across train/valid/test splits
# Train: 1000, Valid: 100, Test: 200
# Uses parallel jobs for faster generation

tw_base_seed_train=10000
tw_base_seed_valid=20000
tw_base_seed_test=30000

# Number of parallel jobs (default: number of CPU cores)
max_parallel_jobs=${MAX_PARALLEL_JOBS:-$(nproc 2>/dev/null || echo 8)}

tasks_dir="textworld-task/cooking-mixed"
mkdir -p ${tasks_dir}/train ${tasks_dir}/valid ${tasks_dir}/test

# Difficulty presets: "recipe:take:go:flags" (flags: o=open, c=cook, t=cut, d=drop)
# Train: easier only (for generalization test - model sees only easier tasks)
train_configs=(
    "3:3:9:oc"         # Medium-hard: 9 rooms, 3 ingredients, open+cook
    "4:4:6:oct"        # Hard: 6 rooms, 4 ingredients, open+cook+cut
    "4:4:6:octd"       # Hard: 6 rooms, 4 ingredients, limited inventory
    "4:4:9:oct"        # Very hard: 9 rooms, 4 ingredients, open+cook+cut
)
# Validation & Test: harder problems (more ingredients, 9+ rooms, all mechanics)
eval_configs=(
    "4:4:9:octd"       # Very hard: 9 rooms + limited inventory
    "5:5:9:octd"       # Very hard: 9 rooms, 5 ingredients + limited inventory
    "4:4:12:oct"       # Very hard: 12 rooms, 4 ingredients
    "4:4:12:octd"      # Very hard: 12 rooms + limited inventory
    "5:5:12:octd"      # Max: 12 rooms, 5 ingredients + limited inventory (recipe max is 5)
)

generate_one() {
    local split=$1
    local i=$2
    local base_seed=$3
    local config=$4
    local output_subdir=${tasks_dir}/${split}

    IFS=':' read -r recipe take go flags <<< "$config"

    seed=$((base_seed + i))
    recipe_seed=$((base_seed + i + 100000))

    flags_args=""
    [[ "$flags" == *"o"* ]] && flags_args="$flags_args --open"
    [[ "$flags" == *"c"* ]] && flags_args="$flags_args --cook"
    [[ "$flags" == *"t"* ]] && flags_args="$flags_args --cut"
    [[ "$flags" == *"d"* ]] && flags_args="$flags_args --drop"

    tw-make tw-cooking \
        --recipe $recipe \
        --take $take \
        --go $go \
        $flags_args \
        --recipe-seed $recipe_seed \
        --split $split \
        --seed $seed \
        --format z8 \
        --output ${output_subdir}/cooking_${seed}.z8 \
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
