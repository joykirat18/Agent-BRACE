"""
LatentBeliefTextWorldAgent — TextWorldAgent subclass with latent diffusion belief injection.

Instead of producing a text belief state, the diffusion world model generates a 768-dim
continuous belief_vec that is injected into the LLM's embedding layer via LatentBeliefInjector.
The prompt for the 'latent_belief_state' thinking_variant uses the belief prefix string
(e.g. "<belief_0><belief_1><belief_2><belief_3>") at the start of the user turn content,
followed by the normal game observation and action instruction — no extra text description.

Usage:
    from diffusion_belief.latent_injection import LatentBeliefInjector
    from diffusion_belief.latent_belief_manager import LatentBeliefManagerPool
    from meow_tea_train.agentic_menu.sync_textworld.latent_belief_agent import LatentBeliefTextWorldAgent

    pool = LatentBeliefManagerPool(diffusion_path="checkpoints/diffusion")
    injector = LatentBeliefInjector.from_vllm(llm, tokenizer, n_belief_tokens=4, belief_dim=768,
                                               projector=projector)

    agent = LatentBeliefTextWorldAgent(
        ...standard TextWorldAgent args...,
        latent_belief_pool=pool,
        latent_injector=injector,
    )
    result = agent.run()
"""

from typing import List, Dict, Tuple, Optional

import torch

from .agent import TextWorldAgent
from vllm.inputs.data import TokensPrompt


class LatentBeliefTextWorldAgent(TextWorldAgent):
    """
    Extends TextWorldAgent to support latent (continuous) belief state injection.

    Two new constructor parameters:
        latent_belief_pool  — LatentBeliefManagerPool: manages per-episode diffusion belief
        latent_injector     — LatentBeliefInjector: patches embed_tokens and provides prefix

    When thinking_variant == "latent_belief_state":
        - The user turn content is prefixed with injector.get_prefix_string()
          (e.g. "<belief_0><belief_1><belief_2><belief_3>") at the very start.
        - No additional text description of the belief is appended; the signal is
          entirely contained in the projected embedding tokens.
        - Before each batch_generate call, belief_vec is retrieved from the pool
          and the generate call is wrapped with injector.set_belief(belief_vec).

    For other thinking_variant values, the agent behaves identically to TextWorldAgent.
    """

    def __init__(
        self,
        env,
        prompts,
        inference_engine,
        sampling_params,
        tokenizer,
        max_iter,
        n_traj,
        max_prompt_len,
        max_response_len,
        use_belief_state,
        use_dynamic_thinking,
        use_intermediate_reward,
        thinking_variant="direct",
        state_tracking_model="Qwen/Qwen3-30B-A3B-Instruct-2507",
        decouple_trajectory=False,
        discount_gamma=0.9,
        # Latent belief extensions
        latent_belief_pool=None,
        latent_injector=None,
    ):
        super().__init__(
            env=env,
            prompts=prompts,
            inference_engine=inference_engine,
            sampling_params=sampling_params,
            tokenizer=tokenizer,
            max_iter=max_iter,
            n_traj=n_traj,
            max_prompt_len=max_prompt_len,
            max_response_len=max_response_len,
            use_belief_state=use_belief_state,
            use_dynamic_thinking=use_dynamic_thinking,
            use_intermediate_reward=use_intermediate_reward,
            thinking_variant=thinking_variant,
            state_tracking_model=state_tracking_model,
            decouple_trajectory=decouple_trajectory,
            discount_gamma=discount_gamma,
        )
        self.latent_belief_pool = latent_belief_pool
        self.latent_injector = latent_injector

        # Per-batch-index tracking of the last extracted action (for belief step())
        self._prev_action_by_idx: Dict[int, Optional[str]] = {
            i: None for i in range(self.batch_size)
        }

    # ── Belief prefix helpers ─────────────────────────────────────────────────

    def _get_belief_prefix(self) -> str:
        """Return the belief token prefix string, or empty string if no injector."""
        if self.latent_injector is None:
            return ""
        return self.latent_injector.get_prefix_string()

    def _build_latent_belief_messages(
        self,
        messages_batch: List[List[Dict]],
        selected_idx: List[int],
        obs_texts: Dict[int, str],
    ) -> List[List[Dict]]:
        """
        Build messages for the latent_belief_state variant.

        The last user message content is prefixed with the belief token string.
        The instruction suffix asks directly for an action (no text belief state).
        """
        belief_prefix = self._get_belief_prefix()
        action_suffix = "\n\nOutput the final action within <action> </action> tags."
        result = []
        for idx in selected_idx:
            messages = messages_batch[idx]
            last_user = messages[-1]["content"]
            # Strip existing suffixes to get base observation content
            for suffix in [
                action_suffix,
                "\n\nLet's think step by step inside the <thinking> </thinking> tags and output the final action within <action> </action> tags.",
                self.belief_state_suffix,
            ]:
                if suffix in last_user:
                    base = last_user.split(suffix)[0].strip()
                    break
            else:
                base = last_user.rstrip()

            # Belief prefix goes at the very start of the user turn content
            new_content = belief_prefix + base + action_suffix
            result.append(messages[:-1] + [{"role": "user", "content": new_content}])
        return result

    # ── belief_vec retrieval ──────────────────────────────────────────────────

    def _get_belief_vecs_for_batch(
        self,
        selected_idx: List[int],
        obs_texts: Dict[int, str],
    ) -> Dict[int, Optional[torch.Tensor]]:
        """
        Call belief_manager.step() for each active instance and return
        a dict mapping batch_idx → belief_vec (or None on first step).
        """
        belief_vecs: Dict[int, Optional[torch.Tensor]] = {}
        if self.latent_belief_pool is None:
            for idx in selected_idx:
                belief_vecs[idx] = None
            return belief_vecs

        for idx in selected_idx:
            obs_text = obs_texts.get(idx, "")
            prev_action = self._prev_action_by_idx.get(idx, None)
            episode_id = str(idx)
            manager = self.latent_belief_pool.get(episode_id)
            bv = manager.step(obs_text, prev_action)
            belief_vecs[idx] = bv
        return belief_vecs

    # ── Patched batch_generate ─────────────────────────────────────────────────

    def batch_generate_with_latent_belief(
        self,
        messages_batch: List[List[Dict]],
        belief_vecs: Dict[int, Optional[torch.Tensor]],
        selected_idx: List[int],
    ) -> Tuple[List[str], List[bool]]:
        """
        Like batch_generate, but wraps the inference_engine.generate call with
        latent belief injection for each item.

        Because vLLM processes the full batch in a single call and set_belief
        only supports a single belief_vec at a time (for the common single-belief
        case), we detect whether all active instances share the same belief status:

        - If all belief_vecs are None → plain batch_generate (no injection).
        - If belief_vecs differ per instance → fall back to sequential generation,
          one call per instance (safe but slower).
        - If all belief_vecs are non-None and identical shape → use first belief_vec
          for the whole batch call (approximate; acceptable when batch is from the
          same rollout episode, not recommended for mixed episodes).

        For most TextWorld training setups the batch contains independent episodes
        so sequential generation is used when belief_vecs are non-None.
        """
        if self.latent_injector is None:
            return self.batch_generate(messages_batch)

        all_none = all(belief_vecs.get(idx) is None for idx in selected_idx)
        if all_none:
            return self.batch_generate(messages_batch)

        # Sequential generation: one call per instance with the correct belief_vec
        output_str_batch: List[str] = []
        valid_output_batch_idx: List[bool] = []

        for i, idx in enumerate(selected_idx):
            single_messages = [messages_batch[i]]
            bv = belief_vecs.get(idx, None)

            input_tokens = self.tokenizer.apply_chat_template(
                single_messages[0],
                tokenize=True,
                add_generation_prompt=True,
                return_tensor="pt",
            )
            tokens_prompt = [TokensPrompt(prompt_token_ids=input_tokens)]

            if bv is not None:
                with self.latent_injector.set_belief(bv):
                    outputs = self.inference_engine.generate(
                        prompts=tokens_prompt,
                        sampling_params=self.sampling_params,
                    )
            else:
                outputs = self.inference_engine.generate(
                    prompts=tokens_prompt,
                    sampling_params=self.sampling_params,
                )

            output_ids = [outputs[0].outputs[0].token_ids]
            valid = [outputs[0].outputs[0].finish_reason == "stop"]
            valid_output_batch_idx.append(valid[0])
            if valid[0]:
                output_str_batch.append(
                    self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
                )
            else:
                output_str_batch.append("")

        return output_str_batch, valid_output_batch_idx

    # ── Override run ───────────────────────────────────────────────────────────

    def run(self):
        """
        Run multi-turn rollouts with latent belief injection.

        For thinking_variant == "latent_belief_state":
          - Resets per-episode belief managers at the start of run().
          - At each step, extracts obs_text from the current user message, calls
            belief_manager.step() to get belief_vec, prefixes the prompt with the
            belief token string, and wraps generate with injector.set_belief().
          - Updates _prev_action_by_idx after each action is extracted.

        For all other thinking_variant values, delegates entirely to the parent
        class run() without any modification.
        """
        if self.thinking_variant != "latent_belief_state" or self.latent_belief_pool is None:
            return super().run()

        # ── Latent belief rollout path ─────────────────────────────────────────
        import os
        import re
        import numpy as np
        from tensordict import TensorDict
        from verl import DataProto

        messages_batch = [messages for messages in self.input_batch.non_tensor_batch["raw_prompt"]]
        assert all(len(messages) == 1 for messages in messages_batch)
        prompt_str_batch = [messages[0]["content"] for messages in messages_batch]
        all_actions_batch = [[] for _ in range(self.batch_size)]
        all_states_batch = [[prompt_str_batch[i]] for i in range(self.batch_size)]
        active_batch_idx = [True for _ in range(self.batch_size)]
        final_reward_batch = [0.0 for _ in range(self.batch_size)]
        interm_reward_batch = [[] for _ in range(self.batch_size)]
        accumulated_reward_batch = [0.0 for _ in range(self.batch_size)]
        instance_env_batch = [
            self.load_env(self.instance_dir, self.instance_id_batch[i])
            for i in range(self.batch_size)
        ]
        all_belief_states_batch = [[] for _ in range(self.batch_size)]
        step_fresh_contexts_batch = [[] for _ in range(self.batch_size)]
        step_responses_batch_text = [[] for _ in range(self.batch_size)]

        # Reset per-episode belief managers
        for i in range(self.batch_size):
            self.latent_belief_pool.reset(str(i))
        self._prev_action_by_idx = {i: None for i in range(self.batch_size)}

        global_step = self.input_batch.meta_info.get("global_steps", 0)

        action_suffix = "\n\nOutput the final action within <action> </action> tags."

        for k in range(self.max_iter):
            selected_idx = np.where(active_batch_idx)[0].tolist()
            if not selected_idx:
                break

            # Build obs_text dict: use the last entry in all_states_batch for each instance
            obs_texts: Dict[int, str] = {}
            for idx in selected_idx:
                raw = all_states_batch[idx][-1]
                # Strip "current state: " prefix if present
                if raw.startswith("current state:"):
                    obs_texts[idx] = raw[len("current state:"):].strip()
                else:
                    obs_texts[idx] = raw.strip()

            # Get belief vectors for this step
            belief_vecs = self._get_belief_vecs_for_batch(selected_idx, obs_texts)

            # Build latent belief messages (belief prefix + obs + action suffix)
            latent_messages = self._build_latent_belief_messages(
                messages_batch, selected_idx, obs_texts
            )

            # Generate with latent belief injection
            output_str_batch, valid_output_batch_idx = self.batch_generate_with_latent_belief(
                latent_messages, belief_vecs, selected_idx
            )

            winning_message_content_by_idx = {}
            for i, idx in enumerate(selected_idx):
                winning_message_content_by_idx[idx] = latent_messages[i][-1]["content"]

            # Decoupled trajectory bookkeeping
            if self.decouple_trajectory and k > 0:
                for i, idx in enumerate(selected_idx):
                    if valid_output_batch_idx[i]:
                        ctx_content = winning_message_content_by_idx.get(
                            idx, messages_batch[idx][-1]["content"]
                        )
                        step_fresh_contexts_batch[idx].append(
                            [{"role": "user", "content": ctx_content}]
                        )

            # Phase 1: run env interactions
            env_results = {}
            for i in range(len(selected_idx)):
                if not valid_output_batch_idx[i]:
                    active_batch_idx[selected_idx[i]] = False
                    continue

                idx = selected_idx[i]
                action_only_str = self._extract_action_from_output(output_str_batch[i])
                all_actions_batch[idx].append(output_str_batch[i])

                if action_only_str == "No action found":
                    env_results[idx] = (
                        "No action found within <action> </action> tags",
                        False,
                        0.0,
                        action_only_str,
                    )
                else:
                    next_obs, has_won, reward, next_instance_env = self.interact(
                        instance_env=instance_env_batch[idx], action=action_only_str
                    )
                    instance_env_batch[idx] = next_instance_env
                    env_results[idx] = (next_obs, has_won, reward, action_only_str)

            # Phase 2: update prev_action, messages, states
            for i in range(len(selected_idx)):
                if not valid_output_batch_idx[i]:
                    continue
                idx = selected_idx[i]
                next_obs, has_won, reward, action_only_str = env_results[idx]

                # Update prev_action for next step's belief manager call
                self._prev_action_by_idx[idx] = action_only_str

                interm_reward_batch[idx].append(reward)
                accumulated_reward_batch[idx] += reward

                if has_won:
                    final_reward_batch[idx] = 1.0
                    active_batch_idx[idx] = False

                # Append to step responses for decoupled mode
                if self.decouple_trajectory:
                    step_responses_batch_text[idx].append(output_str_batch[i])

                # Build next state string with belief prefix at start of user content
                belief_prefix = self._get_belief_prefix()
                next_state_str = f"current state: {next_obs}" + action_suffix
                all_states_batch[idx].append(next_state_str)

                # Update messages_batch for next turn
                assistant_msg = {"role": "assistant", "content": output_str_batch[i]}
                next_user_content = belief_prefix + next_state_str
                user_msg = {"role": "user", "content": next_user_content}
                messages_batch[idx] = messages_batch[idx] + [assistant_msg, user_msg]

                if action_only_str == "No action found":
                    active_batch_idx[idx] = False

        return self.convert_result_to_dataproto(
            messages_batch,
            final_reward_batch,
            interm_reward_batch,
            [1.0] * self.batch_size,
        )
