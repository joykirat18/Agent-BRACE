#!/bin/bash
set -euo pipefail

# Configuration variables
env_name="alfworld"
task_prefix="text_based"
instance_id_start=1
instance_id_end=3553
hf_data_repo="[ANONYMIZED_HF_DATASET]"
hf_instances_dir="$env_name/$task_prefix/instances"
hf_train_data_dir="$env_name/$task_prefix/multiturn_rl_data/all_data"
local_instances_dir="local/$hf_instances_dir"
local_train_data_dir="local/$hf_train_data_dir"
local_parquet_dir="local/train_parquet"
reward_method="single"

echo "Processing multiturn RL data for tasks ${env_name}-${task_prefix} ${instance_id_start}-${instance_id_end}"

# Process everything with all configuration variables
python3 -m meow_tea_train.agentic_utils.data_process.rl_data_processor \
    --env_name "$env_name" \
    --task_prefix "$task_prefix" \
    --instance_id_range "$instance_id_start" "$instance_id_end" \
    --hf_data_repo "$hf_data_repo" \
    --hf_instances_dir "$hf_instances_dir" \
    --hf_train_data_dir "$hf_train_data_dir" \
    --local_instances_dir "$local_instances_dir" \
    --local_train_data_dir "$local_train_data_dir" \
    --local_parquet_dir "$local_parquet_dir" \
    --reward_method "$reward_method"

echo "Processing complete!"