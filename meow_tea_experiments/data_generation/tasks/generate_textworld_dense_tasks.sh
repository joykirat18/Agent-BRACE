#!/bin/bash
# Script to generate dense reward TextWorld tasks
# Usage: bash meow_tea_experiments/data_generation/tasks/generate_textworld_dense_tasks.sh
tw_base_seed=$TW_BASE_SEED
tw_tasks_count=$TW_TASKS_COUNT
tw_dense_reward_type=$TW_DENSE_REWARD_TYPE
tasks_dir=$TASKS_DIR

for i in $(seq 1 $tw_tasks_count)
do
    tw-make tw-simple \
        --rewards $tw_dense_reward_type \
        --goal "detailed" \
        --seed $((tw_base_seed + i)) \
        --output ${tasks_dir}/tw_simple_$((tw_base_seed+i)).z8
done