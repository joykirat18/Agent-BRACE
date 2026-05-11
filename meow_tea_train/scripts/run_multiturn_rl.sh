set -x
export HYDRA_FULL_ERROR=1

# DATA/TASK CONFIG
env_name="" # TODO (required). Choose from ['textworld', 'alfworld']
task_prefix="" # TODO (required). Choose from ['w2-o3-q4', 'w4-o6-q8', 'tw_dense', 'alfworld', etc.]
instance_id_start=-1 # TODO (required, start inclusive). The range of instance ids to process.
instance_id_end=-1 # TODO (required, end inclusive)
hf_data_repo="" # TODO (required). HF dataset repo id.
hf_instances_dir="" # TODO (required). Directory in the HF dataset repo containing instance(game) files.
hf_train_data_dir="" # TODO (required). Directory in the HF dataset repo containing ppo data files.
local_instances_dir="local/$hf_instances_dir" #  Local directory to save instance(game) files. Should be same as hf_instances_dir.
local_train_data_dir="local/$hf_train_data_dir" # Local directory to save ppo data files. Should be same as hf_train_data_dir.
local_parquet_dir="local/train_parquet"
reward_method="" # TODO (required). Same as "reward_density". Choose from ['single', 'dense']

# MODEL CONFIG
hf_actor_repo_id="" # TODO (optional). HF repo id for actor model. If empty, use base_model.
hf_actor_model_path="" # TODO (optional). Path in the HF repo for actor model. If empty, download entire repo.
hf_critic_repo_id="" # TODO (optional). HF repo id for critic model. If empty, use base_model.
hf_critic_model_path="" # TODO (optional). Path in the HF repo for critic model. If empty, download entire repo.
actor_model_path=local/model/actor
critic_model_path=local/model/critic
base_model="" # TODO (required). Base model to use if hf_actor_repo_id or hf_critic_repo_id is empty.

# AGENTIC CONFIG
# env_name=... # from above
is_multiturn=True # Always set True for running multi-turn agentic RL tasks.
is_async=False # TODO (optional, default=False). Whether to use async environment.
max_iter=-1 # TODO (optional, default=10). Max iterations per episode.
reward_density=$reward_method # Same as reward_method above. Choose from ['single', 'dense']
reward_type="verified" # TODO (optional, default='verified'). Choose from ['verified', 'learned']. Select 'verified' if using 'verified' rewards from a function. Select 'learned' if using learned rewards from a reward model/LLM-as-a-judge.
reward_manager="agentic_verified" # TODO (optional, default='agentic_verified'). Choose from ['agentic_verified', 'agentic_learned']. Should be consistent with reward_type.
rollout_name="vllm_agentic" # Always use 'vllm_agentic' for multi-turn agentic RL tasks.
rollout_mode=$( [ "$is_async" = "True" ] && echo "async" || echo "sync" ) # Set 'async' if is_async=True, else 'sync'.

# ALGORITHM CONFIG
adv_estimator=gae # TODO (required). Advantage estimator. Choose from ['gae', 'rloo', 'grpo'].
gamma=1.0 # TODO (optional, default=1.0). Discount factor.
# ... add additional algorithm config if needed
# Some example algorithm config parameters:
use_kl_loss=False # Whether to use KL loss in objective. True for GRPO. Usage: actor_rollout_ref.actor.use_kl_loss=$use_kl_loss
kl_loss_coef=0.01 # Coefficient for KL loss. Only used if use_kl_loss is True. Usage: actor_rollout_ref.actor.kl_loss_coef=$kl_loss_coef
use_kl_in_reward=True # Whether to use KL divergence in reward calculation. True for PPO with KL penalty. Usage: algorithm.use_kl_in_reward=$use_kl_in_reward
kl_coef=0.01 # Coefficient for KL loss/reward. Only used if use_kl_in_reward is True. Usage: algorithm.kl_ctrl.kl_coef=$kl_coef
clip_ratio=0.2

# TRAINING CONFIG
rollout_temp=0.7 # TODO (optional, default=0.7). Temperature for rollout sampling.
val_rollout_temp=0.4 # TODO (optional, default=0.4). Temperature for validation rollout sampling.
train_batch_size=256 # TODO.
ppo_mini_batch_size=256 # TODO.
max_num_batched_tokens=8192 # TODO (optional, default=8192). Max num tokens to batch in vLLM. Increase if GPU memory allows. Also make sure prompt + response length <= max_num_batched_tokens.
gpu_memory_utilization=0.75 # TODO (optional). Fraction of GPU memory to use for vLLM.
max_prompt_length=3072 # TODO (required). Max prompt length for model input.
max_response_length=3072 # TODO (required). Max response length for model output.
actor_lr=1e-6 # TODO (optional, default=1e-6). Learning rate for actor model.
critic_lr=1e-5  # TODO (optional, default=1e-5). Learning rate for critic model.
nnodes=1
num_epochs=-1 # TODO. 
save_freq=-1 # TODO. Save model and upload to "save_hf_repo_id" every N steps.
test_freq=-1 # TODO. Test model every N steps.

# PROJECT CONFIG
project_name="" # TODO (optional). WandB project name.
experiment_name="" # TODO (optional). WandB experiment name.
save_hf_repo_id="" # TODO (optional). HF repo id to save the trained model. If empty, do not save.
resume_wandb_logs=True # TODO (optional, default=True). Whether to resume WandB logs if "experiment_name" exists.


# Step 1: Process RL data
echo "Processing multiturn RL data for tasks ${env_name}-${task_prefix} ${instance_id_start}-${instance_id_end}"
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
    data.train_files="$local_parquet_dir/train.parquet" \
    data.val_files="$local_parquet_dir/validation.parquet" \
    data.return_raw_chat=True \
    data.max_prompt_length=$max_prompt_length \
    data.max_response_length=$max_response_length \
    data.train_batch_size=$train_batch_size \
    algorithm.adv_estimator=$adv_estimator \
    algorithm.gamma=$gamma \
    algorithm.use_kl_in_reward=$use_kl_in_reward \
    algorithm.kl_ctrl.kl_coef=$kl_coef \
    agentic.environment.name=$env_name \
    agentic.environment.is_multiturn=$is_multiturn \
    agentic.environment.is_async=$is_async \
    agentic.environment.max_iter=$max_iter \
    agentic.reward.density=$reward_density \
    agentic.reward.type=$reward_type \
    actor_rollout_ref.model.path=$actor_model_path \
    actor_rollout_ref.model.use_remove_padding=True \
    actor_rollout_ref.model.enable_gradient_checkpointing=True \
    actor_rollout_ref.model.use_fused_kernels=False \
    actor_rollout_ref.actor.use_torch_compile=True \
    actor_rollout_ref.actor.ppo_mini_batch_size=$ppo_mini_batch_size \
    actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=32 \
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
    critic.optim.lr=$critic_lr \
    critic.model.path=$critic_model_path \
    critic.model.use_remove_padding=True \
    critic.model.enable_gradient_checkpointing=True \
    critic.ppo_micro_batch_size_per_gpu=32 \
    critic.use_dynamic_bsz=True \
    reward_model.reward_manager=$reward_manager \
    trainer.critic_warmup=0 \
    trainer.logger=['console','wandb'] \
    trainer.project_name=$project_name \
    trainer.experiment_name=$experiment_name \
    trainer.validation_data_dir="local/val_results" \
    trainer.nnodes=$nnodes \
    trainer.n_gpus_per_node=8 \
    trainer.val_before_train=True \
    trainer.hf_kwargs.save_hf_repo_id=$save_hf_repo_id \
    trainer.hf_kwargs.resume_wandb_logs=$resume_wandb_logs \
    trainer.resume_mode=auto \
    trainer.save_freq=$save_freq \
    trainer.test_freq=$test_freq \
    trainer.total_epochs=$num_epochs $@