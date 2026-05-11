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

import os
import logging
from omegaconf import DictConfig
from vllm import SamplingParams
from omegaconf import OmegaConf

from verl import DataProto
from verl.single_controller.ray.base import RayWorkerGroup
import logging
import os
import pickle
import socket
import threading
from contextlib import contextmanager
from copy import deepcopy
from types import MethodType
from typing import Any, Dict, List, Union

import numpy as np
from torch.distributed.device_mesh import DeviceMesh
import zmq
from filelock import FileLock
from omegaconf import DictConfig, OmegaConf
from tensordict import TensorDict
from vllm import LLM, SamplingParams
from vllm.distributed import parallel_state as vllm_ps

from verl import DataProto
from verl.workers.config import HFModelConfig, RolloutConfig
from verl.utils.profiler import GPUMemoryLogger
from verl.workers.rollout.base import BaseRollout
from verl.workers.rollout.vllm_rollout.vllm_rollout_spmd import vLLMRollout

logger = logging.getLogger(__file__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class vLLMSyncAgenticRollout(vLLMRollout):
    """
    A synchronous rollout class that wraps vLLMRollout but replaces the generation logic with a multi-turn agentic interaction.

    It inherits vLLMRollout in verl/workers/rollout/vllm_rollout/vllm_rollout_spmd.py
    Only the `generate_sequences` function is overridden.

    When thinking_variant == "latent_belief_state", a LatentBeliefInjector is installed
    on the vLLM model's embed_tokens layer so that <belief_X> placeholder tokens in the
    prompt are replaced at runtime with projected diffusion belief vectors.
    The DiffusionWorldModel and BeliefProjector are updated every
    diffusion_update_steps gradient steps using LatentBeliefTrainer.
    """
    def __init__(
        self,
        config: RolloutConfig,
        model_config: HFModelConfig,
        device_mesh: DeviceMesh,
    ):
        if not getattr(config, "agentic", None):
            raise ValueError("config.agentic required for vLLMSyncAgenticRollout.")
        self.agentic_config = OmegaConf.create(config.agentic)
        env_cfg = self.agentic_config.environment

        self._latent_belief_pool = None
        self._latent_injector = None
        self._latent_trainer = None
        self._rollout_count = 0
        self._belief_state_lm_trainer = None
        # True when subprocess belief vLLM + policy TP > 1: agent loop must barrier
        # at each belief-generation checkpoint so all TP ranks call llm.generate() together.
        self._belief_use_tp_barrier = False

        is_latent = (
            env_cfg.get("thinking_variant") == "latent_belief_state"
            or env_cfg.get("use_diffusion_belief", False)
        )

        super().__init__(config, model_config, device_mesh)
        self.config = config

        if is_latent:
            self._init_latent_belief(env_cfg)
        elif env_cfg.get("belief_lm_train_path"):
            self._init_joint_belief_lm(env_cfg)

    def _init_latent_belief(self, env_cfg) -> None:
        """Initialize latent belief pool, injector, and trainer (lazy, called once)."""
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../.."))

        from diffusion_belief.latent_belief_manager import LatentBeliefManagerPool
        from diffusion_belief.latent_injection import LatentBeliefInjector
        from diffusion_belief.latent_belief_trainer import LatentBeliefTrainer

        diffusion_path = env_cfg.get("diffusion_model_path", "")
        if not diffusion_path:
            raise ValueError(
                "agentic.environment.diffusion_model_path must be set "
                "when thinking_variant=latent_belief_state"
            )

        n_diffusion_steps = int(env_cfg.get("diffusion_steps", 20))
        cfg_scale = float(env_cfg.get("diffusion_cfg_scale", 1.5))
        n_belief_tokens = int(env_cfg.get("n_belief_tokens", 4))
        belief_dim = 768

        print(f"[vLLMSyncAgenticRollout] Initializing latent belief pool from {diffusion_path}")
        self._latent_belief_pool = LatentBeliefManagerPool(
            diffusion_path=diffusion_path,
            n_diffusion_steps=n_diffusion_steps,
            cfg_scale=cfg_scale,
        )

        print("[vLLMSyncAgenticRollout] Patching vLLM embed_tokens with LatentBeliefInjector")
        self._latent_injector = LatentBeliefInjector.from_vllm(
            llm=self.inference_engine,
            tokenizer=self.tokenizer,
            n_belief_tokens=n_belief_tokens,
            belief_dim=belief_dim,
        )

        lr = float(env_cfg.get("diffusion_lr", 1e-4))
        self._latent_trainer = LatentBeliefTrainer(
            diffusion_path=diffusion_path,
            projector=self._latent_injector.projector,
            lr=lr,
            projector_lr=lr,
            n_diffusion_steps=n_diffusion_steps,
            cfg_scale=cfg_scale,
        )
        self._diffusion_update_steps = int(env_cfg.get("diffusion_update_steps", 50))
        print("[vLLMSyncAgenticRollout] Latent belief state initialized.")

    def _create_belief_vllm_engine(self, model_path: str, env_cfg) -> Any:
        """Second vLLM engine for belief-state generation (TP=1 on ``belief_lm_cuda_device``)."""
        from vllm import LLM

        dev_idx = int(env_cfg.get("belief_lm_cuda_device", 0))
        max_mlen = int(env_cfg.get("belief_lm_vllm_max_model_len", 8192))
        max_tok = int(env_cfg.get("belief_lm_vllm_max_num_batched_tokens", 8192))
        load_fmt = env_cfg.get("belief_lm_vllm_load_format", "auto")
        if load_fmt is None:
            load_fmt = "auto"
        kwargs = dict(
            model=model_path,
            tensor_parallel_size=1,
            dtype=str(self.config.dtype),
            trust_remote_code=True,
            gpu_memory_utilization=float(
                env_cfg.get("belief_lm_vllm_gpu_memory_utilization", 0.45)
            ),
            enforce_eager=True,
            max_model_len=max_mlen,
            max_num_batched_tokens=max_tok,
            disable_custom_all_reduce=True,
            skip_tokenizer_init=False,
            load_format=str(load_fmt),
            seed=int(env_cfg.get("belief_lm_vllm_seed", 0)),
        )
        try:
            return LLM(**kwargs, tensor_parallel_device_ids=[dev_idx])
        except TypeError as e:
            logger.warning(
                "tensor_parallel_device_ids not supported for belief vLLM (%s); "
                "using default device layout.",
                e,
            )
            return LLM(**kwargs)

    def _init_joint_belief_lm(self, env_cfg) -> None:
        """HF belief LM for PPO + optional vLLM engine for fast batched rollouts."""
        import torch
        from transformers import AutoTokenizer

        from meow_tea_train.agentic_menu.sync_textworld.belief_state_lm_trainer import (
            BeliefStateLMTrainer,
        )

        path = env_cfg.get("belief_lm_train_path", "")
        if not path:
            return
        dev_idx = int(env_cfg.get("belief_lm_cuda_device", 0))
        if torch.cuda.is_available():
            n = torch.cuda.device_count()
            if dev_idx < 0 or dev_idx >= n:
                raise ValueError(
                    f"belief_lm_cuda_device={dev_idx} invalid for {n} visible CUDA device(s)"
                )
            device = torch.device(f"cuda:{dev_idx}")
        else:
            device = torch.device("cpu")
        if env_cfg.get("belief_state_model_url"):
            logger.warning(
                "belief_lm_train_path is set; using in-process belief LM — "
                "belief_state_model_url is ignored for rollouts."
            )
        use_vllm = bool(env_cfg.get("belief_lm_use_vllm_inference", True))
        if use_vllm and not torch.cuda.is_available():
            logger.warning("CUDA unavailable; belief inference falls back to HuggingFace.")
            use_vllm = False

        policy_tp = int(self.config.get("tensor_model_parallel_size", 1) or 1)
        use_sub_raw = env_cfg.get("belief_lm_vllm_use_subprocess", None)
        if use_sub_raw is None:
            use_subprocess = bool(use_vllm and policy_tp > 1)
        else:
            use_subprocess = bool(use_sub_raw)

        if use_vllm and policy_tp > 1 and not use_subprocess:
            logger.warning(
                "belief_lm_use_vllm_inference with policy tensor_model_parallel_size=%d > 1 needs "
                "belief_lm_vllm_use_subprocess=true (separate process). Using HuggingFace for belief.",
                policy_tp,
            )
            use_vllm = False
            use_subprocess = False

        # Each tensor-parallel rollout rank constructs its own rollout; without this, every rank
        # spawns a belief vLLM subprocess on the same belief GPU → duplicate weights + KV cache OOM.
        belief_vllm_tp_leader = True
        if use_vllm and use_subprocess:
            try:
                from vllm.distributed.parallel_state import get_tensor_model_parallel_rank

                belief_vllm_tp_leader = int(get_tensor_model_parallel_rank()) == 0
            except Exception:
                belief_vllm_tp_leader = True

        # When subprocess belief is used with TP > 1, all TP ranks must synchronize at
        # every belief-generation checkpoint inside TextWorldAgent so that they all call
        # policy llm.generate() at the same time (TP requires collective participation).
        # Set this flag on BOTH leader and non-leader before potentially returning early.
        self._belief_use_tp_barrier = bool(use_vllm and use_subprocess and policy_tp > 1)

        if use_vllm and use_subprocess and not belief_vllm_tp_leader:
            # Non-TP-leader rank: skip belief trainer entirely.
            # Previously this rank fell back to slow HF-CPU inference, which caused a
            # TP deadlock: rank 0 (fast subprocess) would call policy llm.generate()
            # while rank 1 (slow CPU) was still generating belief states.
            # Now rank 1 has no trainer (belief generation is a no-op) and relies on the
            # dist.barrier() in the agent loop to wait for rank 0 before each policy step.
            logger.warning(
                "[vLLMSyncAgenticRollout] TP rank >0: belief trainer suppressed "
                "(rank 0 subprocess vLLM collects all belief data). "
                "Agent loop will barrier-sync with rank 0 at each belief checkpoint."
            )
            self._belief_state_lm_trainer = None
            return

        def rebuild_belief_vllm(mpath: str) -> Any:
            return self._create_belief_vllm_engine(mpath, env_cfg)

        def _belief_subprocess_llm_kwargs() -> dict:
            load_fmt = env_cfg.get("belief_lm_vllm_load_format", "auto")
            if load_fmt is None:
                load_fmt = "auto"
            # Subprocess owns the whole belief GPU — default high utilization so KV cache can allocate.
            kw: dict = dict(
                tensor_parallel_size=1,
                dtype=str(self.config.dtype),
                trust_remote_code=True,
                gpu_memory_utilization=float(
                    env_cfg.get("belief_lm_vllm_gpu_memory_utilization", 0.90)
                ),
                enforce_eager=True,
                max_model_len=int(env_cfg.get("belief_lm_vllm_max_model_len", 8192)),
                max_num_batched_tokens=int(
                    env_cfg.get("belief_lm_vllm_max_num_batched_tokens", 8192)
                ),
                disable_custom_all_reduce=True,
                skip_tokenizer_init=False,
                load_format=str(load_fmt),
                seed=int(env_cfg.get("belief_lm_vllm_seed", 0)),
            )
            mns = env_cfg.get("belief_lm_vllm_max_num_seqs", None)
            if mns is not None:
                kw["max_num_seqs"] = int(mns)
            return kw

        belief_engine = None
        subprocess_kw = None
        rebuild_fn = None
        if use_vllm and use_subprocess:
            from meow_tea_train.agentic_menu.sync_textworld.belief_vllm_subprocess import (
                BeliefVLLMSubprocessClient,
            )

            bdev = int(env_cfg.get("belief_lm_cuda_device", 0))
            subprocess_kw = _belief_subprocess_llm_kwargs()
            belief_engine = BeliefVLLMSubprocessClient.start(
                model_path=path,
                cuda_visible_device_index=bdev,
                llm_kwargs=subprocess_kw,
            )
            inference_tag = "subprocess vLLM"
        elif use_vllm:
            belief_engine = rebuild_belief_vllm(path)
            rebuild_fn = rebuild_belief_vllm
            inference_tag = "in-process vLLM"
        else:
            inference_tag = "HF"

        print(
            f"[vLLMSyncAgenticRollout] Joint belief LM from {path} on {device} "
            f"(inference={inference_tag})"
        )
        btok = AutoTokenizer.from_pretrained(path, trust_remote_code=True)
        cr_lo = env_cfg.get("belief_lm_clip_ratio_low", None)
        cr_hi = env_cfg.get("belief_lm_clip_ratio_high", None)
        self._belief_state_lm_trainer = BeliefStateLMTrainer(
            model_path=path,
            tokenizer=btok,
            device=device,
            lr=float(env_cfg.get("belief_lm_lr", 1e-5)),
            max_gen_tokens=int(env_cfg.get("belief_lm_max_gen_tokens", 512)),
            gradient_clip=float(env_cfg.get("belief_lm_gradient_clip", 1.0)),
            belief_vllm_engine=belief_engine,
            belief_vllm_rebuild_from_path=rebuild_fn,
            belief_vllm_subprocess_llm_kwargs=subprocess_kw,
            ppo_clip_ratio=float(env_cfg.get("belief_lm_clip_ratio", 0.2)),
            ppo_clip_ratio_low=float(cr_lo) if cr_lo is not None else None,
            ppo_clip_ratio_high=float(cr_hi) if cr_hi is not None else None,
            ppo_clip_ratio_c=float(env_cfg.get("belief_lm_clip_ratio_c", 3.0)),
            ppo_policy_loss_mode=str(
                env_cfg.get("belief_lm_ppo_policy_loss_mode", "vanilla")
            ),
            ppo_mini_batch_size=int(env_cfg.get("belief_lm_ppo_mini_batch_size", 8)),
            gen_temperature=float(env_cfg.get("belief_lm_gen_temperature", 1.0)),
            loss_agg_mode=str(env_cfg.get("belief_lm_loss_agg_mode", "token-mean")),
            use_value_function=bool(env_cfg.get("belief_lm_use_value_function", True)),
            value_lr=float(env_cfg.get("belief_lm_value_lr", 1e-5)),
            value_clip_range=float(env_cfg.get("belief_lm_value_clip_range", 0.5)),
            gae_gamma=float(env_cfg.get("belief_lm_gae_gamma", 1.0)),
            gae_lambda=float(env_cfg.get("belief_lm_gae_lambda", 0.95)),
            ppo_task_reward_only=bool(
                env_cfg.get("belief_lm_task_reward_only", False)
            ),
            use_kl_loss=bool(env_cfg.get("belief_lm_use_kl_loss", False)),
            kl_loss_coef=float(env_cfg.get("belief_lm_kl_loss_coef", 0.001)),
            kl_loss_type=str(env_cfg.get("belief_lm_kl_loss_type", "low_var_kl")),
        )

    def _maybe_update_world_model(self) -> None:
        """
        After every rollout batch, update the diffusion model + projector on the
        collected trajectories. Reloads the updated diffusion model into the pool
        so future belief samples use the improved model.
        """
        if self._latent_trainer is None or self._latent_belief_pool is None:
            return

        trajectories = self._latent_belief_pool.collect_all_trajectories()
        if not trajectories:
            return

        metrics = self._latent_trainer.update(
            trajectories,
            n_steps=self._diffusion_update_steps,
        )
        print(
            f"[LatentBeliefTrainer] diffusion_loss={metrics['diffusion_loss']:.4f} "
            f"projector_loss={metrics['projector_loss']:.4f} "
            f"n_samples={metrics['n_samples']}"
        )

        # Reload the updated diffusion model into the pool
        self._latent_belief_pool.reload_diffusion(self._latent_trainer.diffusion_path)

    def generate_sequences(self, prompts: DataProto, **kwargs) -> DataProto:
        """
        Generate sequences using multi-turn agentic interaction.
        Override the parent's generate_sequences method.
        """
        env_name = self.agentic_config.environment.name.lower()
        thinking_variant = self.agentic_config.environment.thinking_variant

        if env_name in ["textworld", "alfworld"]:
            print(
                f"[AGENT_ROLLOUT] generate_sequences env={env_name} thinking_variant={thinking_variant}",
                flush=True,
            )
            if thinking_variant == "latent_belief_state" and self._latent_belief_pool is not None:
                from meow_tea_train.agentic_menu.sync_textworld.latent_belief_agent import (
                    LatentBeliefTextWorldAgent,
                )
                agent = LatentBeliefTextWorldAgent(
                    env=env_name,
                    prompts=prompts,
                    inference_engine=self.inference_engine,
                    sampling_params=self.sampling_params,
                    tokenizer=self.tokenizer,
                    max_iter=self.agentic_config.environment.max_iter,
                    n_traj=self.agentic_config.environment.n_traj,
                    max_prompt_len=self.config.prompt_length,
                    max_response_len=self.config.response_length,
                    use_belief_state=self.agentic_config.environment.use_belief_state,
                    use_dynamic_thinking=self.agentic_config.environment.use_dynamic_thinking,
                    use_intermediate_reward=self.agentic_config.environment.get(
                        "use_intermediate_reward", False
                    ),
                    thinking_variant=thinking_variant,
                    state_tracking_model=self.agentic_config.environment.state_tracking_model,
                    decouple_trajectory=self.agentic_config.environment.get(
                        "decouple_trajectory", False
                    ),
                    discount_gamma=self.agentic_config.environment.get("discount_gamma", 0.9),
                    latent_belief_pool=self._latent_belief_pool,
                    latent_injector=self._latent_injector,
                )
                result = agent.run()

                # Update world model on trajectories from this batch
                self._rollout_count += 1
                if not prompts.meta_info.get("validate", False):
                    self._maybe_update_world_model()

                return result
            else:
                from meow_tea_train.agentic_menu.sync_textworld.agent import TextWorldAgent
                agent = TextWorldAgent(
                    env=env_name,
                    prompts=prompts,
                    inference_engine=self.inference_engine,
                    sampling_params=self.sampling_params,
                    tokenizer=self.tokenizer,
                    max_iter=self.agentic_config.environment.max_iter,
                    n_traj=self.agentic_config.environment.n_traj,
                    max_prompt_len=self.config.prompt_length,
                    max_response_len=self.config.response_length,
                    use_belief_state=self.agentic_config.environment.use_belief_state,
                    use_dynamic_thinking=self.agentic_config.environment.use_dynamic_thinking,
                    use_intermediate_reward=self.agentic_config.environment.use_intermediate_reward,
                    thinking_variant=thinking_variant,
                    state_tracking_model=self.agentic_config.environment.state_tracking_model,
                    decouple_trajectory=self.agentic_config.environment.get(
                        "decouple_trajectory", False
                    ),
                    discount_gamma=self.agentic_config.environment.get("discount_gamma", 0.9),
                    belief_state_model_url=self.agentic_config.environment.get(
                        "belief_state_model_url", None
                    ),
                    belief_state_model_name=self.agentic_config.environment.get(
                        "belief_state_model_name", None
                    ),
                    belief_state_trainer=self._belief_state_lm_trainer,
                    belief_alpha=float(
                        self.agentic_config.environment.get("belief_alpha", 0.5)
                    ),
                    belief_discount_gamma=float(
                        self.agentic_config.environment.get(
                            "belief_discount_gamma", 0.9
                        )
                    ),
                    belief_transition_weight=float(
                        self.agentic_config.environment.get(
                            "belief_transition_weight", 0.5
                        )
                    ),
                    belief_lm_n_update_steps=int(
                        self.agentic_config.environment.get(
                            "belief_lm_n_update_steps", 1
                        )
                    ),
                    belief_reward_model_url=self.agentic_config.environment.get(
                        "belief_reward_model_url", "http://localhost:8005"
                    ),
                    belief_reward_model_name=self.agentic_config.environment.get(
                        "belief_reward_model_name",
                        "Qwen/Qwen3-30B-A3B-Instruct-2507",
                    ),
                    belief_use_tp_barrier=self._belief_use_tp_barrier,
                    belief_lm_task_reward_only=bool(
                        self.agentic_config.environment.get(
                            "belief_lm_task_reward_only", False
                        )
                    ),
                )
                return agent.run()
        else:
            raise NotImplementedError(f"Environment {env_name} not supported in vLLMSyncAgenticRollout.")