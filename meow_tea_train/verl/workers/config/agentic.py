# Copyright 2025 Anonymous Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
#
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from dataclasses import dataclass, field
from typing import Optional

from verl.base_config import BaseConfig

__all__ = [
    "AgenticEnvironmentConfig",
    "AgenticAgentConfig",
    "AgenticRewardConfig",
    "AgenticAgentLoopConfig",
]

# NOTE from meow-tea: These are basic configurations for agentic environment, agent and reward.
# You can extend these configs or create your own config class to add more parameters as needed.
@dataclass
class AgenticEnvironmentConfig(BaseConfig):
    name: str = None
    is_multiturn: bool = True
    is_async: bool = False
    max_iter: int = 10
    n_traj: int = 1
    use_belief_state: bool = False
    use_dynamic_thinking: bool = False
    use_intermediate_reward: bool = False
    thinking_variant: str = "direct"
    state_tracking_model: str = "Qwen/Qwen3-30B-A3B-Instruct-2507"
    decouple_trajectory: bool = False
    use_dynamic_thinking: bool = False
    use_intermediate_reward: bool = False
    thinking_variant: str = "direct"
    state_tracking_model: str = "Qwen/Qwen3-30B-A3B-Instruct-2507"
    decouple_trajectory: bool = False
    # Finetuned belief-state model (separate vLLM server, OpenAI-compatible API).
    # Set belief_state_model_url to the server base URL (e.g. "http://localhost:8001").
    # When set, the model generates belief states instead of the main policy.
    # Requires decouple_trajectory=True and thinking_variant="direct" (or "step-by-step").
    belief_state_model_url: Optional[str] = None
    belief_state_model_name: Optional[str] = None
    belief_state_model_url: Optional[str] = None
    belief_state_model_name: Optional[str] = None
    # Joint belief-state LM (HF in-process; PPO via same VERL policy loss registry as the actor).
    # When set, overrides static HTTP inference from belief_state_model_url for belief generation.
    belief_lm_train_path: Optional[str] = None
    belief_lm_lr: float = 1e-5
    belief_lm_max_gen_tokens: int = 512
    belief_lm_gradient_clip: float = 1.0
    belief_lm_n_update_steps: int = 1
    belief_alpha: float = 0.5
    belief_discount_gamma: float = 0.9
    # If True, belief LM PPO uses only discounted_task_r (skips LLM judge rewards for training).
    belief_lm_task_reward_only: bool = False
    # KL-to-reference regularizer on the belief LM (anchors it to the initial belief policy).
    belief_lm_use_kl_loss: bool = False
    belief_lm_kl_loss_coef: float = 0.001
    belief_lm_kl_loss_type: str = "low_var_kl"
    belief_transition_weight: float = 0.5
    belief_lm_cuda_device: int = 0
    belief_lm_clip_ratio: float = 0.2
    belief_lm_clip_ratio_low: Optional[float] = None
    belief_lm_clip_ratio_high: Optional[float] = None
    belief_lm_clip_ratio_c: float = 3.0
    belief_lm_ppo_policy_loss_mode: str = "vanilla"
    belief_lm_ppo_mini_batch_size: int = 8
    belief_lm_gen_temperature: float = 1.0
    belief_lm_loss_agg_mode: str = "token-mean"
    belief_lm_use_value_function: bool = True
    belief_lm_value_lr: float = 1e-5
    belief_lm_value_clip_range: float = 0.5
    belief_lm_gae_gamma: float = 1.0
    belief_lm_gae_lambda: float = 0.95
    # Belief-PPO batch balancing (sparse-reward safeguards for low-success envs like ALFWorld).
    #   min_positive_trajectories: skip belief update when fewer than N trajectories have
    #     task_reward > 0 in the batch. Prevents learning from pure-noise advantages.
    #   neg_to_pos_ratio: keep all steps from positive-reward trajectories; subsample steps
    #     from zero-reward trajectories to at most ratio * n_pos_steps.
    #     0 = train only on positive trajectories. <0 = disable balancing (keep all).
    belief_lm_min_positive_trajectories: int = 1
    belief_lm_neg_to_pos_ratio: float = 3.0
    # Weight on LLM-judge state_tracking_r in total_reward.
    # 0 = disabled, 1 = equal weight with discounted_task_r (default — brings the
    # LLM judge back into the mix), >1 = emphasise state tracking over sparse task reward.
    belief_lm_state_tracking_weight: float = 1.0
    belief_lm_use_vllm_inference: bool = True
    belief_lm_vllm_use_subprocess: Optional[bool] = None
    belief_lm_vllm_max_model_len: int = 8192
    belief_lm_vllm_max_num_batched_tokens: int = 8192
    belief_lm_vllm_max_num_seqs: Optional[int] = None
    belief_lm_vllm_gpu_memory_utilization: float = 0.45
    belief_lm_vllm_load_format: Optional[str] = "auto"
    belief_lm_vllm_seed: int = 0
    # OpenAI-compatible server for LLM-as-judge belief rewards (state tracking + correctness).
    # Set to null to disable and keep state_tracking_r / state_correctness_r at 0.0 for those terms.
    belief_reward_model_url: Optional[str] = "http://localhost:8005"
    belief_reward_model_name: str = "Qwen/Qwen3-30B-A3B-Instruct-2507"
    # Per-turn cap on policy generation tokens. When set, overrides rollout.response_length
    # (which is the whole-trajectory cap) for each individual vLLM.generate call in
    # multi-turn rollouts. Prevents long <thinking> chains from consuming the full budget
    # on turn 1 and keeps per-turn wall time bounded.
    max_tokens_per_turn: Optional[int] = None
    # Latent diffusion belief state config
    use_diffusion_belief: bool = False
    diffusion_model_path: str = ""
    diffusion_steps: int = 20
    diffusion_cfg_scale: float = 1.5
    n_belief_tokens: int = 4
    diffusion_update_steps: int = 50
    diffusion_lr: float = 1e-4

    def __post_init__(self):
        """Validate the environment config"""
        print(f"AgenticEnvironmentConfig: {self.name}")
        assert self.name in ["textworld", "alfworld", "swegym", "custom"], (
            "name must be one of ['textworld', 'alfworld', 'swegym', 'custom']"
        )

@dataclass
class AgenticAgentConfig(BaseConfig):
    use_think: bool = False
    use_tool: bool = False
    use_memory: bool = False


@dataclass
class AgenticRewardConfig(BaseConfig):
    density: str = "single"
    type: str = "verified"

    def __post_init__(self):
        """Validate the reward config"""
        assert self.density in ["single", "dense"], "density must be one of ['single', 'dense']"
        assert self.type in ["verified", "learned"], "type must be one of ['verified', 'learned']"


@dataclass
class SWEAgentKwargs:
    """Configuration for SWE-agent specific parameters"""
    trajs_save_dir: Optional[str] = None
    sweagent_config_path: Optional[str] = None


@dataclass
class AgenticAgentLoopConfig(BaseConfig):
    type: Optional[str] = None
    kwargs: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.type == "async_software":
            # Use object.__setattr__ for frozen dataclass
            object.__setattr__(self, 'kwargs', SWEAgentKwargs(**self.kwargs))
        elif self.type is None:
            pass
        else:
            raise ValueError(f"Unsupported agent loop type: {self.type}")
