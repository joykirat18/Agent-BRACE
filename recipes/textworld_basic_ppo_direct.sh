set -x
export HYDRA_FULL_ERROR=1

# DATA/TASK CONFIG
# export HF_HOME="/home/user/.cache/huggingface"
# export UV_CACHE_DIR="/home/user/.cache/uv"
# export RAY_TMPDIR="/home/user/tmp_ray"
# export HUGGINGFACE_TOKEN='YOUR_HUGGINGFACE_TOKEN'
# export HF_TOKEN='YOUR_HUGGINGFACE_TOKEN'

export CUDA_VISIBLE_DEVICES=0,1,2,3

WANDB_API_KEY='YOUR_WANDB_API_KEY'
if [ "$WANDB_API_KEY" != "None" ]; then
    export WANDB_DIR='local/wandb'
    mkdir -p $WANDB_DIR
    mkdir -p $WANDB_DIR/wandb
    chmod -R u+w $WANDB_DIR
    chmod -R u+w $WANDB_DIR/wandb
    wandb login --relogin $WANDB_API_KEY
fi
# DATA/TASK CONFIG
env_name="textworld"
# task_prefix="basic"
# instance_id_start=50001
# instance_id_end=55000
# hf_data_repo="[ANONYMIZED_HF_DATASET]"
# hf_instances_dir="$env_name/$task_prefix/instances"
# hf_train_data_dir="$env_name/$task_prefix/multiturn_rl_data/5000_train_data"
# local_instances_dir="local/$hf_instances_dir"
# local_train_data_dir="local/$hf_train_data_dir"
# local_parquet_dir="local/train_parquet"
reward_method="single"

# MODEL CONFIG
hf_actor_repo_id=""
hf_actor_model_path=""
hf_critic_repo_id=""
hf_critic_model_path=""
actor_model_path=local/model/actor
critic_model_path=local/model/critic
base_model="microsoft/Phi-4-mini-instruct"

# AGENTIC CONFIG
# env_name=... # from above
is_multiturn=True
is_async=False
max_iter=15
reward_density=$reward_method
reward_type="verified"
reward_manager="agentic_verified"
rollout_name="vllm_agentic"
rollout_mode=$( [ "$is_async" = "True" ] && echo "async" || echo "sync" ) # Set 'async' if is_async=True, else 'sync'.

# ALGORITHM CONFIG
adv_estimator=gae
gamma=1.0

use_kl_loss=False # Whether to use KL loss in objective. True for GRPO.
use_kl_in_reward=True # Whether to use KL divergence in reward calculation.
kl_coef=0.01
clip_ratio=0.2

# TRAINING CONFIG
rollout_temp=0.7
val_rollout_temp=0.4
train_batch_size=16
ppo_mini_batch_size=16
ppo_micro_batch_size_per_gpu=4
max_num_batched_tokens=20000
gpu_memory_utilization=0.65
max_prompt_length=8000
max_response_length=8000
ppo_max_token_len_per_gpu=20000
actor_lr=1e-6
critic_lr=1e-5
nnodes=1
num_epochs=50
save_freq=50 # per steps
test_freq=25 # per steps
use_belief_state=False
use_dynamic_thinking=False
thinking_variant="direct"

# PROJECT CONFIG
project_name="textworld-phi-4-mini-instruct" # TODO (optional). WandB project name.
experiment_name="basic-ppo-phi-4-mini-instruct-direct" # TODO (optional). WandB experiment name.
save_hf_repo_id="your-hf-repo-id" # TODO (optional). HF repo id to save the trained model. If empty, do not save.
resume_wandb_logs=True # TODO (optional, default=True). Whether to resume WandB logs if "experiment_name" exists.


# Step 1: Process RL data
# echo "Processing multiturn RL data for tasks ${env_name}-${task_prefix} ${task_id_start}-${task_id_end}"
# python3 -m meow_tea_train.agentic_utils.data_process.rl_data_processor \
#     --env_name "$env_name" \
#     --task_prefix "$task_prefix" \
#     --instance_id_range "$instance_id_start" "$instance_id_end" \
#     --hf_data_repo "$hf_data_repo" \
#     --hf_instances_dir "$hf_instances_dir" \
#     --hf_train_data_dir "$hf_train_data_dir" \
#     --local_instances_dir "$local_instances_dir" \
#     --local_train_data_dir "$local_train_data_dir" \
#     --local_parquet_dir "$local_parquet_dir" \
#     --reward_method "$reward_method"

# Step 2: Load models
echo "Loading models..."
# Check if actor model is specified
if [ -n "$hf_actor_repo_id" ]; then
    # If specified, download from HF path if available
    if [ -z "$hf_actor_model_path" ]; then
        # Download entire repo if path is empty/None
        hf download $hf_actor_repo_id --local-dir $actor_model_path
    else
        # Download specific path and flatten
        hf download $hf_actor_repo_id --include="${hf_actor_model_path}/*" --local-dir $actor_model_path
        mv $actor_model_path/$hf_actor_model_path/* $actor_model_path/
        rm -rf $actor_model_path/$hf_actor_model_path
        rm -rf $actor_model_path/.cache
    fi
else
    # Otherwise, use base model (from HF)
    actor_model_path=$base_model
fi

# Check if critic model is specified
if [ -n "$hf_critic_repo_id" ]; then
    # If specified, download from HF path if available
    if [ -z "$hf_critic_model_path" ]; then
        # Download entire repo if path is empty/None
        hf download $hf_critic_repo_id --local-dir $critic_model_path
    else
        # Download specific path and flatten
        hf download $hf_critic_repo_id --include="${hf_critic_model_path}/*" --local-dir $critic_model_path
        mv $critic_model_path/$hf_critic_model_path/* $critic_model_path/
        rm -rf $critic_model_path/$hf_critic_model_path
        rm -rf $critic_model_path/.cache
    fi
else
    # Otherwise, use base model (from HF)
    critic_model_path=$base_model
fi

# Step 3: Run training
echo "Starting RL training..."

python3 -m meow_tea_train.verl.trainer.main_ppo \
    data.train_files="../data-basic-parquet/train.parquet" \
    data.val_files="../data-basic-parquet/test.parquet" \
    data.return_raw_chat=True \
    data.max_prompt_length=$max_prompt_length \
    data.max_response_length=$max_response_length \
    data.train_batch_size=$train_batch_size \
    data.val_batch_size=$train_batch_size \
    algorithm.adv_estimator=$adv_estimator \
    algorithm.gamma=$gamma \
    algorithm.use_kl_in_reward=$use_kl_in_reward \
    algorithm.kl_ctrl.kl_coef=$kl_coef \
    agentic.environment.name=$env_name \
    agentic.environment.is_multiturn=$is_multiturn \
    agentic.environment.is_async=$is_async \
    agentic.environment.max_iter=$max_iter \
    agentic.environment.use_belief_state=$use_belief_state \
    agentic.environment.use_dynamic_thinking=$use_dynamic_thinking \
    agentic.reward.density=$reward_density \
    agentic.environment.thinking_variant=$thinking_variant \
    agentic.reward.type=$reward_type \
    actor_rollout_ref.model.path=$actor_model_path \
    actor_rollout_ref.model.use_remove_padding=True \
    actor_rollout_ref.model.enable_gradient_checkpointing=True \
    actor_rollout_ref.model.use_fused_kernels=False \
    actor_rollout_ref.actor.use_torch_compile=True \
    actor_rollout_ref.actor.ppo_mini_batch_size=$ppo_mini_batch_size \
    actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=$ppo_micro_batch_size_per_gpu \
    actor_rollout_ref.actor.ppo_max_token_len_per_gpu=$ppo_max_token_len_per_gpu \
    actor_rollout_ref.actor.use_dynamic_bsz=True \
    actor_rollout_ref.actor.entropy_coeff=0.0 \
    actor_rollout_ref.actor.use_kl_loss=$use_kl_loss \
    actor_rollout_ref.actor.optim.lr=$actor_lr \
    actor_rollout_ref.actor.clip_ratio=$clip_ratio \
    actor_rollout_ref.rollout.name=$rollout_name \
    actor_rollout_ref.rollout.mode=$rollout_mode \
    +actor_rollout_ref.rollout.agentic='${agentic}' \
    actor_rollout_ref.rollout.temperature=$rollout_temp \
    actor_rollout_ref.rollout.tensor_model_parallel_size=1 \
    actor_rollout_ref.rollout.gpu_memory_utilization=$gpu_memory_utilization \
    actor_rollout_ref.rollout.n=1 \
    actor_rollout_ref.rollout.max_num_batched_tokens=$max_num_batched_tokens \
    actor_rollout_ref.rollout.val_kwargs.temperature=$val_rollout_temp \
    actor_rollout_ref.rollout.val_kwargs.n=1 \
    critic.optim.lr=$critic_lr \
    critic.model.path=$critic_model_path \
    critic.model.use_remove_padding=True \
    critic.model.enable_gradient_checkpointing=True \
    critic.ppo_micro_batch_size_per_gpu=$ppo_micro_batch_size_per_gpu \
    critic.use_dynamic_bsz=True \
    reward_model.reward_manager=$reward_manager \
    trainer.critic_warmup=0 \
    trainer.logger=['console','wandb'] \
    trainer.project_name=$project_name \
    trainer.experiment_name=$experiment_name \
    trainer.validation_data_dir="local/val_results_basic_direct_phi_4_mini_instruct" \
    trainer.nnodes=$nnodes \
    trainer.n_gpus_per_node=4 \
    trainer.val_before_train=False \
    trainer.hf_kwargs.save_hf_repo_id=$save_hf_repo_id \
    trainer.hf_kwargs.resume_wandb_logs=$resume_wandb_logs \
    trainer.resume_mode=auto \
    trainer.save_freq=$save_freq \
    trainer.test_freq=$test_freq \
    trainer.total_epochs=$num_epochs $@