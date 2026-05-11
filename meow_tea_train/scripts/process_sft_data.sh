set -x

env_name="alfworld"
task_prefix="text_based"
hf_data_repo="[ANONYMIZED_HF_DATASET]"
hf_train_data_dir="$env_name/$task_prefix/multiturn_sft_data/100_data"
local_train_data_dir="local/${hf_train_data_dir}"
local_parquet_dir="local/train_parquet"

mkdir -p $local_parquet_dir

echo "Processing multiturn SFT data for tasks ${env_name}-${task_prefix}"

python3 -m meow_tea_train.agentic_utils.data_process.sft_data_processor \
    --hf_data_repo $hf_data_repo \
    --hf_train_data_dir $hf_train_data_dir \
    --local_train_data_dir $local_train_data_dir \
    --local_parquet_dir $local_parquet_dir \