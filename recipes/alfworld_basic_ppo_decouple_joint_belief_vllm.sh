set -x
export HYDRA_FULL_ERROR=1

# =============================================================================
# TextWorld PPO — decoupled trajectories + joint belief LM (vLLM rollout + HF PPO)
# Based on: recipes/textworld_basic_ppo_decouple_trajectory_structured.sh
#
# GPU layout (3 visible devices: 0,1,2 after CUDA_VISIBLE_DEVICES):
#   - Policy:  vLLM tensor parallel on logical GPUs 0 and 1
#   - Belief:  logical GPU 2 — HF PPO on cuda:2 during update; subprocess vLLM uses CUDA_VISIBLE_DEVICES=2
#
# trainer.n_gpus_per_node is the Ray / torch.distributed world size (FSDP + vLLM SPMD ranks).
# Policy uses 2 GPUs -> set it to 2 (not 3). A third physical GPU is only for belief; it must
# NOT inflate world_size or PPO will normalize batches by 3 (e.g. 16//3=5).
# RAY_EXPERIMENTAL_NOSET_CUDA_VISIBLE_DEVICES lets each worker still see 0,1,2 so TP device ids
# and belief_lm_cuda_device work while Ray only schedules 2 GPU bundles for training ranks.
#
# Prerequisites:
#   - Merged HF weights for the belief model at BELIEF_LM_TRAIN_PATH (same format as SFT export).
#   - Train parquet paths (adjust data.train_files / data.val_files below).
# =============================================================================

# DATA/TASK CONFIG (optional overrides)
# export HF_HOME="..."
# export RAY_TMPDIR="..."

# Three GPUs: policy TP on 0,1; belief vLLM subprocess on 2 (HF belief trains on cuda:2 between rollouts).
export CUDA_VISIBLE_DEVICES=0,1,2
export RAY_EXPERIMENTAL_NOSET_CUDA_VISIBLE_DEVICES=1

WANDB_API_KEY="${WANDB_API_KEY:-None}"
if [ "$WANDB_API_KEY" != "None" ] && [ -n "$WANDB_API_KEY" ]; then
    export WANDB_DIR='local/wandb'
    mkdir -p "$WANDB_DIR"
    mkdir -p "$WANDB_DIR/wandb"
    chmod -R u+w "$WANDB_DIR"
    chmod -R u+w "$WANDB_DIR/wandb"
    wandb login --relogin "$WANDB_API_KEY"
fi

env_name="alfworld"
reward_method="single"

# MODEL CONFIG
hf_actor_repo_id=""
hf_actor_model_path=""
hf_critic_repo_id=""
hf_critic_model_path=""
actor_model_path=local/model/actor
critic_model_path=local/model/critic
base_model="Qwen/Qwen3-4B-Instruct-2507"

# Joint belief LM: local or HF path to full merged belief-state checkpoint (not LoRA-only).
BELIEF_LM_TRAIN_PATH="${BELIEF_LM_TRAIN_PATH:-/home/user/textworld-RL/local/checkpoints/alfworld-belief-sft-qwen3b/merged_model}"

# AGENTIC CONFIG
is_multiturn=True
is_async=False
max_iter=50
reward_density=$reward_method
reward_type="verified"
reward_manager="agentic_verified"
rollout_name="vllm_agentic"
rollout_mode=$( [ "$is_async" = "True" ] && echo "async" || echo "sync" )

# ALGORITHM CONFIG
adv_estimator=gae
gamma=1.0
use_kl_loss=False
use_kl_in_reward=True
kl_coef=0.01
clip_ratio=0.2

# TRAINING CONFIG
rollout_temp=0.7
val_rollout_temp=0.4
# Normalized per-rank mini = (ppo_mini_batch_size * rollout.n) // trainer.n_gpus_per_node (see fsdp_workers).
# With n_gpus_per_node=2 and rollout.n=1: 16//2=8, compatible with ppo_micro_batch_size_per_gpu=4.
train_batch_size=16
ppo_mini_batch_size=16
ppo_micro_batch_size_per_gpu=4
max_num_batched_tokens=12000
gpu_memory_utilization=0.55
# Belief subprocess owns GPU 2 alone; use most VRAM for weights + KV (vLLM may OOM if too low).
belief_lm_vllm_gpu_memory_utilization=0.55
max_prompt_length=6000
max_response_length=6000
ppo_max_token_len_per_gpu=12000
actor_lr=1e-6
critic_lr=1e-5
nnodes=1
num_epochs=0
save_freq=10
test_freq=50
use_belief_state=True
use_dynamic_thinking=False
decouple_trajectory=True
thinking_variant="step-by-step"

# In-process joint belief: do NOT use external belief_state_model_url.
belief_state_model_url=null
belief_state_model_name=null

# Belief PPO / rewards (align clip with policy unless you override)
belief_alpha=0.5
belief_discount_gamma=0.9
belief_transition_weight=0.5
belief_lm_n_update_steps=1
belief_lm_ppo_mini_batch_size=4
belief_lm_lr=1e-5
# Disable value function (critic) to cut GPU-2 memory by ~24 GB during PPO update.
# The actor model + AdamW alone are ~24 GB; the value model doubles that → OOM.
belief_lm_use_value_function=False
# KL-to-reference penalty on belief LM: anchors π_belief to its initial
# distribution so PPO cannot collapse it. Loads a frozen ref copy on GPU 2
# during the update (be mindful of VRAM — ref adds ~ one model size).
belief_lm_use_kl_loss=False
belief_lm_kl_loss_coef=0.001
belief_lm_kl_loss_type="low_var_kl"
belief_lm_cuda_device=2
belief_lm_use_vllm_inference=True
# Required for policy TP=2: belief vLLM runs in a spawn subprocess on belief_lm_cuda_device
# (only tensor-parallel rank 0; other ranks use HF belief on CPU to avoid two engines on GPU 2).
belief_lm_vllm_use_subprocess=True
belief_lm_max_gen_tokens=2000
belief_lm_vllm_max_model_len=6096
belief_lm_vllm_max_num_batched_tokens=6096

# Per-turn cap on policy generation: prevents long <thinking> chains from consuming the
# full max_response_length budget on a single turn. 1024 tokens is enough for any reasonable
# thinking + action on ALFWorld; rollout aggregate is still bounded by max_response_length.
max_tokens_per_turn=1024

# PROJECT CONFIG
project_name="alfworld-Qwen-4B-Instruct-2507"
experiment_name="alfworld-ppo-decouple-joint-belief-vllm-Qwen-4B-Instruct-2507-finetuned-4-rewards-v4-step-by-step"
save_hf_repo_id=""
resume_wandb_logs=True

# Policy vLLM tensor parallel: logical GPUs 0 and 1.
POLICY_TP_SIZE=2

# Step 1: Process RL data (optional; uncomment if needed)
# python3 -m meow_tea_train.agentic_utils.data_process.rl_data_processor ...

# Step 2: Load models
echo "Loading models..."
if [ -n "$hf_actor_repo_id" ]; then
    if [ -z "$hf_actor_model_path" ]; then
        hf download "$hf_actor_repo_id" --local-dir "$actor_model_path"
    else
        hf download "$hf_actor_repo_id" --include="${hf_actor_model_path}/*" --local-dir "$actor_model_path"
        mv "$actor_model_path/$hf_actor_model_path"/* "$actor_model_path/"
        rm -rf "$actor_model_path/$hf_actor_model_path"
        rm -rf "$actor_model_path/.cache"
    fi
else
    actor_model_path=$base_model
fi

if [ -n "$hf_critic_repo_id" ]; then
    if [ -z "$hf_critic_model_path" ]; then
        hf download "$hf_critic_repo_id" --local-dir "$critic_model_path"
    else
        hf download "$hf_critic_repo_id" --include="${hf_critic_model_path}/*" --local-dir "$critic_model_path"
        mv "$critic_model_path/$hf_critic_model_path"/* "$critic_model_path/"
        rm -rf "$critic_model_path/$hf_critic_model_path"
        rm -rf "$critic_model_path/.cache"
    fi
else
    critic_model_path=$base_model
fi

if [ ! -d "$BELIEF_LM_TRAIN_PATH" ] && [[ "$BELIEF_LM_TRAIN_PATH" != *"/"* ]]; then
    echo "WARNING: BELIEF_LM_TRAIN_PATH=$BELIEF_LM_TRAIN_PATH is not a directory; if it is an HF id, ensure it is reachable." >&2
fi

# Step 3: Run training
echo "Starting RL training (joint belief vLLM + decouple trajectory)..."

python3 -m meow_tea_train.verl.trainer.main_ppo \
    data.train_files="../data-alfworld-parquet-thinking/train.parquet" \
    data.val_files="../data-alfworld-parquet-thinking/validation.parquet" \
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
    agentic.environment.use_belief_state=$use_belief_state \
    agentic.environment.use_dynamic_thinking=$use_dynamic_thinking \
    agentic.environment.thinking_variant=$thinking_variant \
    agentic.environment.decouple_trajectory=$decouple_trajectory \
    agentic.environment.belief_state_model_url=$belief_state_model_url \
    agentic.environment.belief_state_model_name=$belief_state_model_name \
    agentic.environment.belief_lm_train_path=$BELIEF_LM_TRAIN_PATH \
    agentic.environment.belief_lm_cuda_device=$belief_lm_cuda_device \
    agentic.environment.belief_lm_use_vllm_inference=$belief_lm_use_vllm_inference \
    agentic.environment.belief_lm_vllm_use_subprocess=$belief_lm_vllm_use_subprocess \
    agentic.environment.belief_lm_vllm_gpu_memory_utilization=$belief_lm_vllm_gpu_memory_utilization \
    agentic.environment.belief_lm_vllm_max_model_len=$belief_lm_vllm_max_model_len \
    agentic.environment.belief_lm_vllm_max_num_batched_tokens=$belief_lm_vllm_max_num_batched_tokens \
    agentic.environment.belief_lm_vllm_max_num_seqs=16 \
    agentic.environment.belief_lm_max_gen_tokens=$belief_lm_max_gen_tokens \
    agentic.environment.belief_lm_lr=$belief_lm_lr \
    agentic.environment.belief_lm_n_update_steps=$belief_lm_n_update_steps \
    +agentic.environment.belief_lm_ppo_mini_batch_size=$belief_lm_ppo_mini_batch_size \
    agentic.environment.belief_lm_use_value_function=$belief_lm_use_value_function \
    agentic.environment.belief_lm_use_kl_loss=$belief_lm_use_kl_loss \
    agentic.environment.belief_lm_kl_loss_coef=$belief_lm_kl_loss_coef \
    agentic.environment.belief_lm_kl_loss_type=$belief_lm_kl_loss_type \
    +actor_rollout_ref.rollout.agentic.environment.belief_lm_min_positive_trajectories=1 \
    +actor_rollout_ref.rollout.agentic.environment.belief_lm_neg_to_pos_ratio=1.0 \
    agentic.environment.belief_alpha=$belief_alpha \
    agentic.environment.belief_discount_gamma=$belief_discount_gamma \
    agentic.environment.belief_transition_weight=$belief_transition_weight \
    agentic.environment.belief_lm_clip_ratio=$clip_ratio \
    agentic.environment.belief_lm_clip_ratio_c=3.0 \
    agentic.environment.belief_lm_ppo_policy_loss_mode=vanilla \
    agentic.environment.max_tokens_per_turn=$max_tokens_per_turn \
    agentic.reward.density=$reward_density \
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
    actor_rollout_ref.rollout.agentic='${agentic}' \
    actor_rollout_ref.rollout.temperature=$rollout_temp \
    actor_rollout_ref.rollout.tensor_model_parallel_size=$POLICY_TP_SIZE \
    'actor_rollout_ref.rollout.tensor_parallel_cuda_device_ids=[0,1]' \
    actor_rollout_ref.rollout.gpu_memory_utilization=$gpu_memory_utilization \
    actor_rollout_ref.rollout.n=1 \
    actor_rollout_ref.rollout.max_num_batched_tokens=$max_num_batched_tokens \
    actor_rollout_ref.rollout.val_kwargs.temperature=$val_rollout_temp \
    actor_rollout_ref.rollout.val_kwargs.n=1 \
    actor_rollout_ref.nccl_timeout=7200 \
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
    trainer.validation_data_dir="local/val_results_alfworld_Qwen-4B-Instruct-2507-decouple-joint-belief-vllm-4-rewards-v4-step-by-step" \
    +trainer.train_data_dir="local/train_results_alfworld_Qwen-4B-Instruct-2507-decouple-joint-belief-vllm-4-rewards-v4-step-by-step" \
    +trainer.train_data_save_freq=1 \
    trainer.nnodes=$nnodes \
    trainer.n_gpus_per_node=2 \
    trainer.val_before_train=True \
    trainer.hf_kwargs.save_hf_repo_id=$save_hf_repo_id \
    trainer.hf_kwargs.resume_wandb_logs=$resume_wandb_logs \
    trainer.resume_mode=auto \
    trainer.save_freq=$save_freq \
    trainer.test_freq=$test_freq \
    trainer.total_epochs=$num_epochs "$@"
