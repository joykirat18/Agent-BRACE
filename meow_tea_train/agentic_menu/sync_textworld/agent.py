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


from typing import List, Tuple, Dict, Optional, Any
import os
import re
import time
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Finetuned belief-state model prompt template.
# IMPORTANT: Must stay aligned with
#   meow_tea_experiments/scripts/finetune_belief_state_sft.py  (_USER_PROMPT_TEMPLATE)
# ---------------------------------------------------------------------------
_FINETUNED_BELIEF_STATE_PROMPT_TEMPLATE = """\
You are playing a text-based game. Given the goal, your previous belief state, \
and the current observation, produce an updated belief state capturing what you \
know and how confidently you know it.

Goal:
{goal}

Previous belief state:
{previous_belief_state}

Current observation:
{current_obs}

Output ONLY a belief state within <belief_state> </belief_state> tags.

━━━ STRICT RULES ━━━
Your belief state MUST NOT contain:
- Any next action, plan, or intention.
- Forward-looking phrases: "I will", "I should", "my next step", "I plan to", etc.
- Any recommendation about which command to execute.
ONLY record what you have already observed or can directly infer from past observations.

━━━ UPDATE RULES ━━━
- If the current observation CONFIRMS a previous bullet → upgrade it to "confirmed".
- If the current observation CONTRADICTS a previous bullet → replace it immediately.
- If you visit a room and do NOT observe object X there → downgrade X's location bullet to "ruled out".
- Never carry forward a stale bullet that conflicts with a direct observation.

━━━ CERTAINTY SCALE ━━━
Every bullet MUST contain exactly one of these markers, used naturally in the sentence:

  confirmed / certain   → directly observed this turn
  almost certain        → observed previously, no contradicting evidence since
  probable              → inferred from goal structure or strong pattern
  possible              → no visit yet, some contextual reason to believe
  unlikely              → visited nearby rooms, no supporting evidence found
  doubtful              → contradicting evidence exists
  ruled out             → directly observed to be false this turn

Never use "unknown" — if you have no evidence, write "possible" and note it \
reflects no evidence either way.

━━━ MANDATORY COVERAGE ━━━
You MUST cover each of these in at least one bullet:
  - Current location
  - Each known exit and where it leads
  - Each goal-relevant object: its location and state
  - Your inventory
  - Progress toward each sub-goal

━━━ FORMAT ━━━
- One bullet per distinct fact, starting with "- ".
- Every bullet contains exactly one certainty marker from the scale above.
- No JSON, no percentages, no key-value pairs.

Examples:
- It is confirmed that I am in the kitchen.
- The east exit almost certainly leads to the hallway based on prior exploration.
- The key is probably still in the living room where I last saw it.
- It is possible the chest in the bedroom contains the goal item, though I have not visited.
- The couch is ruled out from the bedroom — I visited and did not observe it there.
- It is doubtful the garden door is unlocked given every other door here has been locked.
- It is confirmed that I am carrying only the brass key.\
"""

import torch
import numpy as np
from tensordict import TensorDict

from vllm.inputs.data import TokensPrompt
from verl import DataProto
from .env import TextWorldEnvBase
from ..base.agent import BaseAgent
from vllm import SamplingParams
from .belief_state_lm_trainer import (
    BeliefStateTrainingStep,
    batch_compute_belief_rewards,
    compute_single_belief_rewards,
    compute_format_compliance_score,
)

class TextWorldAgent(BaseAgent) :
    """
    An instance of textworld agent that interacts with the textworld env.
    """
    def __init__(
        self,
        env,
        prompts: DataProto,
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
        belief_state_model_url=None,
        belief_state_model_name=None,
        # Joint belief-state trainer (separate model, trained alongside the policy).
        # When set, belief states are generated by this trainer instead of the HTTP API,
        # and training data is collected for post-rollout gradient updates.
        belief_state_trainer=None,
        belief_alpha: float = 0.5,
        belief_discount_gamma: float = 0.9,
        belief_transition_weight: float = 0.5,
        belief_lm_n_update_steps: int = 1,
        belief_use_tp_barrier: bool = False,
        # URL / model-name for the external LLM used to score belief states.
        # When None, deferred batch_compute_belief_rewards is skipped and
        # state_tracking_r / state_correctness_r stay at their initial 0.0.
        belief_reward_model_url: Optional[str] = "http://localhost:8005",
        belief_reward_model_name: str = "Qwen/Qwen3-30B-A3B-Instruct-2507",
        # Ablation: train belief LM with discounted task return only (no LLM rewards).
        belief_lm_task_reward_only: bool = False,
    ):
        self.env = env
        self.device = prompts.batch["input_ids"].device
        self.inference_engine = inference_engine
        self.sampling_params = sampling_params
        self.tokenizer = tokenizer
        self.max_iter = max_iter
        self.n_traj = n_traj
        self.max_prompt_len = max_prompt_len
        self.max_response_len = max_response_len
        self.use_belief_state = use_belief_state
        self.eos_token_id = tokenizer.eos_token_id
        self.pad_token_id = tokenizer.pad_token_id
        self.sep_token_id = tokenizer.eos_token_id
        self.sep_token = tokenizer.convert_ids_to_tokens(self.sep_token_id)
        self.use_dynamic_thinking = use_dynamic_thinking
        self.use_intermediate_reward = use_intermediate_reward
        self.thinking_variant = thinking_variant
        self.state_tracking_model = state_tracking_model
        self.decouple_trajectory = decouple_trajectory
        self.discount_gamma = discount_gamma
        # Finetuned belief-state model (hosted on a separate vLLM server).
        # When set, belief states are generated by this model after each env step
        # instead of being generated by the main policy.  Requires decouple_trajectory=True.
        self.belief_state_model_url = belief_state_model_url
        self.belief_state_model_name = belief_state_model_name or "belief-state"
        if belief_state_model_url and not decouple_trajectory:
            logger.warning(
                "belief_state_model_url is set but decouple_trajectory=False; "
                "the finetuned belief-state model will NOT be used."
            )
        # Joint belief-state trainer (separate model, trained alongside the policy).
        self.belief_state_trainer = belief_state_trainer
        self.belief_alpha = belief_alpha
        self.belief_discount_gamma = belief_discount_gamma
        self.belief_transition_weight = belief_transition_weight
        self.belief_lm_n_update_steps = belief_lm_n_update_steps
        self.belief_use_tp_barrier = belief_use_tp_barrier
        self.belief_reward_model_url = belief_reward_model_url
        self.belief_reward_model_name = belief_reward_model_name
        self.belief_lm_task_reward_only = bool(belief_lm_task_reward_only)
        if belief_state_trainer is not None and not decouple_trajectory:
            logger.warning(
                "belief_state_trainer is set but decouple_trajectory=False; "
                "joint belief training will NOT be active."
            )
        # Collected training data for the belief-state model; populated during run()
        # and consumed by the rollout worker after run() returns.
        self.belief_state_training_steps: List = []
        # Repeat input batch according to n_traj, the actual batch size = bs * n_traj
        self.input_batch = prompts.repeat(repeat_times=self.n_traj, interleave=True)
        self.batch_size = self.input_batch.batch["input_ids"].size(0)

        # Extract instance env info from data ground truth
        self.instance_dir = self.input_batch[0].non_tensor_batch["extra_info"]["instance_path"]
        self.instance_id_batch = [self.input_batch[i].non_tensor_batch["extra_info"]["instance_file"] for i in range(self.batch_size)]

        if self.thinking_variant in ("symbolic_belief_state", "symbolic_belief_state_periodic"):
            self.belief_state_suffix = """Output your symbolic belief state as JSON within <belief_state> </belief_state> tags, then output the final action within <action> </action> tags.

The JSON MUST follow this exact schema:
{
  "map": {
    "<room>": {"<direction>": "<connected_room>"}
  },
  "items": {
    "<item_name>": {
      "loc_dist":   {"<room_or_unknown>": <probability 0.0-1.0>, ...},
      "state_dist": {"<open|closed|held|unknown|...>": <probability 0.0-1.0>, ...}
    }
  },
  "inventory": ["<item>"],
  "objective": "<current active step from How to Win>",
  "gap": "<specific missing fact or item blocking progress>",
  "plan": "<next action>"
}

Rules:
- loc_dist values MUST sum to 1.0. A room already searched and found empty MUST have probability 0.0.
- state_dist values MUST sum to 1.0.
- Use "unknown" as a catch-all key for unobserved possibilities."""

        elif self.thinking_variant == "memory_belief_state":
            self.belief_state_suffix = """\n\nOutput your belief state within <belief_state> </belief_state> tags, then think step by step inside <thinking> </thinking> tags, then output the final action within <action> </action> tags.

In the belief state, describe in natural language what you know about the current world state — where you are, what rooms and connections you have found, what objects you have seen and their states, and which goal steps are complete. Capture uncertainty directly in your words: use terms like "certain", "likely", "probable", "possibly", "uncertain", "unlikely", or "unknown" to reflect how confident you are about each fact."""

        elif self.thinking_variant == "goal_memory_belief_state":
            self.belief_state_suffix = """\n\nUsing the goal description above, your previous belief state (if any), and the current observation, construct an updated belief state and take the next action.

Output your updated belief state within <belief_state> </belief_state> tags, then output the final action within <action> </action> tags.

In the belief state, describe in natural language what you know about the current world state — where you are, what rooms and connections you have found, what objects you have seen and their states, and which goal steps are complete. Capture uncertainty directly in your words: use terms like "certain", "likely", "probable", "possibly", "uncertain", "unlikely", or "unknown" to reflect how confident you are about each fact."""

        elif self.thinking_variant == "goal_memory_history_summary":
            self.belief_state_suffix = """\n\nUsing the goal description above, your previous belief state (if any), and the current observation, summarize what you have observed so far, then take the next action.

Output a factual summary of your past observations within <belief_state> </belief_state> tags, then output the final action within <action> </action> tags.

Write the summary as natural flowing text. Record only confirmed facts from what you have already seen and done — where you are, which rooms and connections you have visited, what objects you have observed and in what state, which actions you took and what happened, and which goal steps are already complete. Do not include plans, guesses, or anything you have not directly observed."""

        elif self.thinking_variant == "goal_memory_freeform_bdi":
            self.belief_state_suffix = """\n\nUsing the goal description above, your previous belief state (if any), and the current observation, update your understanding and take the next action.

When describing uncertainty about any object, location, or outcome, use one of the following words — chosen to reflect how confident you are:
  - "certain" or "confirmed": you have directly observed this to be true.
  - "almost certain": very strong evidence, would be very surprised if wrong.
  - "probable": more likely true than not, based on what you have seen.
  - "possible": could go either way; some evidence for it, some against.
  - "unlikely": more evidence against it than for it, but cannot rule it out.
  - "doubtful": little reason to believe it; would be surprised if true.
  - "unknown": no evidence either way; you have not explored or observed enough to say.

Use these words naturally in sentences (e.g. "the key is probably in the kitchen", "it is unlikely the chest is locked", "the east exit is confirmed to lead to the hallway").

Your response MUST follow this exact format — all three sections as plain text headings inside one belief_state block:

<belief_state>
BELIEFS: [Summarize what you have confirmed from observations — current location, rooms and connections visited, objects seen and their states, which goal steps are complete. For each object or location you have not directly observed, state your uncertainty using the scale above (e.g. "the candle is probably in the bedroom", "it is unknown whether the drawer is locked"). If you tried an action and it failed, record that explicitly.]

DESIRES: [State which goal step you are currently working on, why earlier steps are considered done, and what concrete condition must be true to complete the current step.]

INTENTIONS: [State what is blocking your progress. Identify the next action from the admissible commands list that best advances your goal. Reason about what you expect to happen — use the uncertainty scale to describe how confident you are in the outcome (e.g. "going east will probably lead to the garden", "picking up the box will almost certainly satisfy the goal"). If your last action had no effect, do NOT repeat it — choose a different action.]
</belief_state>
<action>[your action here — must be one of the admissible commands]</action>

Do not create separate XML tags for BELIEFS, DESIRES, or INTENTIONS. Do not use JSON or numerical probability scores. Express all confidence and uncertainty using the natural language scale defined above."""

        elif self.thinking_variant == "belief_state":
            self.belief_state_suffix = """\n\nOutput your belief state within <belief_state> </belief_state> tags, then output the final action within <action> </action> tags.

A belief state is your recursive mental map. To maintain consistency, you MUST follow this thought process:
1. REVIEW: Look at your PREVIOUS BELIEF STATE and the LAST ACTION taken.
2. EVALUATE: Did the last action succeed? How did it change the environment or your location?
3. UPDATE: Generate the CURRENT BELIEF STATE using this schema:

- LAST ACTION RESULT: (e.g., "Moved East successfully" or "Tried to open chest, but it was locked").
- LOCATION: Your current room.
- WORLD MAP: Persistent map of rooms and their cardinal connections.
- INVENTORY: Items currently held.
- GOAL TRACKER: The specific step from the "Winning Strategy" you are currently working on.
- OBJECT STATUS: Known state/location of goal objects (e.g., Chest, Latchkey, Gateway).
- MISSING INFO: Specific knowledge required to complete the current goal step."""
        else:
            # step-by-step with dynamic thinking: use belief_state for direct+belief_state variant
            self.belief_state_suffix = """\n\nOutput your belief state within <belief_state> </belief_state> tags, then output the final action within <action> </action> tags.

A belief state is your recursive mental map. To maintain consistency, you MUST follow this thought process:
1. REVIEW: Look at your PREVIOUS BELIEF STATE and the LAST ACTION taken.
2. EVALUATE: Did the last action succeed? How did it change the environment or your location?
3. UPDATE: Generate the CURRENT BELIEF STATE using this schema:

- LAST ACTION RESULT: (e.g., "Moved East successfully" or "Tried to open chest, but it was locked").
- LOCATION: Your current room.
- WORLD MAP: Persistent map of rooms and their cardinal connections.
- INVENTORY: Items currently held.
- GOAL TRACKER: The specific step from the "Winning Strategy" you are currently working on.
- OBJECT STATUS: Known state/location of goal objects (e.g., Chest, Latchkey, Gateway).
- MISSING INFO: Specific knowledge required to complete the current goal step."""

    def _extract_action_from_output(self, output_str: str) -> str:
        """
        Extract action text from model output. Only accepts content between
        <action> and </action>; content must be non-empty.
        """
        if not output_str or not output_str.strip():
            return "No action found"
        match = re.search(r"<action>(.*?)</action>", output_str, re.DOTALL | re.IGNORECASE)
        if match:
            action = match.group(1).strip()
            if action:
                return action
        return "No action found"

    def _extract_belief_state_from_output(self, output_str: str) -> str:
        """
        Extract belief state text from model output. Only accepts content between
        <belief_state> and </belief_state>; may be empty.
        """
        if not output_str or not output_str.strip():
            return ""
        match = re.search(r"<belief_state>(.*?)</belief_state>", output_str, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""

    # ------------------------------------------------------------------
    # Finetuned belief-state model helpers
    # ------------------------------------------------------------------

    def _build_belief_state_user_prompt(
        self,
        goal: str,
        previous_belief_state: str,
        current_obs: str,
    ) -> str:
        """Build the user prompt for the finetuned belief-state model.

        Must match the template used during SFT training
        (meow_tea_experiments/scripts/finetune_belief_state_sft.py):
        goal + previous_belief_state + current_obs.
        """
        prev_belief_str = (
            previous_belief_state.strip()
            if previous_belief_state.strip()
            else "(none — this is the first observation)"
        )
        return _FINETUNED_BELIEF_STATE_PROMPT_TEMPLATE.format(
            goal=goal.strip(),
            previous_belief_state=prev_belief_str,
            current_obs=current_obs.strip(),
        )

    def _extract_obs_and_actions_for_belief_state(
        self,
        idx: int,
        prompt_str_batch: List[str],
        all_states_batch: List[List[str]],
        all_actions_batch: List[List[str]],
        current_obs: str,
    ) -> Tuple[str, List[str], List[str]]:
        """Extract (goal, observations, actions) for the finetuned belief-state model.

        Called after Phase-1 env interaction at step k, so:
          all_actions_batch[idx]  has k+1 entries (includes current step's action)
          all_states_batch[idx]   has k+1 entries (initial + k previous-step obs strings)
          current_obs             is the new env observation after the current action

        Returns observations of length k+2 and actions of length k+1 so that
        len(observations) == len(actions) + 1.
        """
        initial_prompt = prompt_str_batch[idx]
        goal = (
            initial_prompt.split("current state:")[0].rstrip()
            if "current state:" in initial_prompt
            else initial_prompt
        )

        observations: List[str] = []
        # obs_0: embedded in the initial prompt
        if "current state:" in initial_prompt:
            obs_0 = initial_prompt.split("current state:")[1].split("\n\n")[0].strip()
            observations.append(obs_0)

        # obs_1 .. obs_k: from Phase-3 entries in all_states_batch (skip index 0)
        for state_str in all_states_batch[idx][1:]:
            if "current state:" in state_str:
                obs = state_str.split("current state:")[1].split("\n\n")[0].strip()
                observations.append(obs)

        # current observation: the env response to this step's action
        observations.append(current_obs)

        # Actions: extract just the command string from each full model output
        actions = [self._extract_action_from_output(out) for out in all_actions_batch[idx]]

        return goal, observations, actions

    def _call_finetuned_belief_state_model(
        self,
        goal: str,
        previous_belief_state: str,
        current_obs: str,
    ) -> str:
        """Call the finetuned belief-state model via OpenAI-compatible API (vLLM).

        Inputs match the SFT training distribution: goal + previous_belief_state + current_obs.
        Returns the extracted belief-state content (without XML tags), or '' on failure.
        """
        try:
            from openai import OpenAI  # vLLM exposes an OpenAI-compatible server
            user_content = self._build_belief_state_user_prompt(goal, previous_belief_state, current_obs)
            client = OpenAI(
                base_url=f"{self.belief_state_model_url}/v1",
                api_key="EMPTY",
            )
            response = client.chat.completions.create(
                model=self.belief_state_model_name,
                messages=[{"role": "user", "content": user_content}],
                max_tokens=1024,
                temperature=0.0,
            )
            content = response.choices[0].message.content or ""
            match = re.search(r"<belief_state>(.*?)</belief_state>", content, re.DOTALL | re.IGNORECASE)
            return match.group(1).strip() if match else content.strip()
        except Exception as e:
            logger.warning("Finetuned belief-state model call failed: %s", e)
            return ""

    def _batch_call_belief_state_model(
        self,
        requests: List[Tuple[str, str, str]],
    ) -> List[str]:
        """Concurrently call the finetuned belief-state model for a batch.

        Args:
            requests: list of (goal, previous_belief_state, current_obs) tuples
        Returns:
            list of belief-state strings in the same order as requests
        """
        if requests:
            print(
                f"[BELIEF_GEN] HTTP belief-state model n_requests={len(requests)}",
                flush=True,
            )
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=min(len(requests), 16)) as executor:
            futures = [
                executor.submit(self._call_finetuned_belief_state_model, goal, prev_bs, obs)
                for (goal, prev_bs, obs) in requests
            ]
            return [f.result() for f in futures]

    def _finalize_belief_state_training(self, final_reward_batch: List[float]) -> Dict[str, float]:
        """Assign discounted task rewards to belief steps and run one belief LM update.

        Returns scalar metrics for logging (e.g. wandb under belief_actor/* and belief_critic/*).
        """
        if self.input_batch.meta_info.get("validate", False):
            return {}
        if self.belief_state_trainer is None or not self.belief_state_training_steps:
            return {}
        mapping = getattr(self, "_bs_step_traj_map", None)
        if not mapping:
            return {}
        max_k_by_traj: Dict[int, int] = {}
        for _step_i, traj_idx, k in mapping:
            max_k_by_traj[traj_idx] = max(max_k_by_traj.get(traj_idx, k), k)
        gamma = self.belief_discount_gamma
        for step_idx, traj_idx, k in mapping:
            T = max_k_by_traj[traj_idx]
            R = float(final_reward_batch[traj_idx])
            self.belief_state_training_steps[step_idx].discounted_task_r = (
                R
            )
        steps = self.belief_state_training_steps
        n_bs = len(steps)
        mean_st  = float(np.mean([s.state_tracking_r    for s in steps])) if n_bs else 0.0
        mean_sc  = float(np.mean([s.state_correctness_r  for s in steps])) if n_bs else 0.0
        mean_div = float(np.mean([s.diversity_r          for s in steps])) if n_bs else 0.0
        mean_dt  = float(np.mean([s.discounted_task_r    for s in steps])) if n_bs else 0.0
        mean_fmt = float(np.mean([s.format_compliance_r  for s in steps])) if n_bs else 0.0
        if self.belief_lm_task_reward_only:
            mean_tot = mean_dt
        else:
            mean_tot = float(np.mean([s.total_reward for s in steps])) if n_bs else 0.0

        metrics = self.belief_state_trainer.update(
            self.belief_state_training_steps,
            n_update_steps=self.belief_lm_n_update_steps,
        )
        logger.info(
            "[TextWorldAgent] Belief LM PPO: loss=%.4f mean_reward=%.4f n=%d "
            "ppo_kl=%.4f clipfrac=%.4f",
            metrics.get("loss", 0.0),
            metrics.get("mean_reward", 0.0),
            metrics.get("n_samples", 0),
            metrics.get("ppo_kl", 0.0),
            metrics.get("pg_clipfrac", 0.0),
        )
        return {
            "belief_critic/mean_state_tracking_reward": mean_st,
            "belief_critic/mean_state_correctness_reward": mean_sc,
            "belief_critic/mean_diversity_reward": mean_div,
            "belief_critic/mean_discounted_task_reward": mean_dt,
            "belief_critic/mean_format_compliance": mean_fmt,
            "belief_critic/mean_total_reward": mean_tot,
            "belief_actor/loss": float(metrics.get("loss", 0.0)),
            "belief_actor/mean_reward": float(metrics.get("mean_reward", 0.0)),
            "belief_actor/ppo_kl": float(metrics.get("ppo_kl", 0.0)),
            "belief_actor/pg_clipfrac": float(metrics.get("pg_clipfrac", 0.0)),
            "belief_actor/n_samples": float(metrics.get("n_samples", 0)),
            "belief_actor/kl_loss": float(metrics.get("kl_loss", 0.0)),
            "belief_actor/kl_coef": float(metrics.get("kl_coef", 0.0)),
        }

    def _has_correct_format(self, output_str: str, is_thinking: bool, is_belief_state: bool = False) -> bool:
        """
        Check if output has correct format.
        - Thinking: <thinking>...</thinking> and <action>...</action> with non-empty content.
        - Direct: <action>...</action> with non-empty content, no <thinking>.
        - Belief state: <belief_state>...</belief_state> and <action>...</action> with non-empty action.
        """
        if not output_str or not output_str.strip():
            return False
        action_match = re.search(r"<action>(.*?)</action>", output_str, re.DOTALL | re.IGNORECASE)
        action_content_nonempty = action_match and bool(action_match.group(1).strip())
        if not action_content_nonempty:
            return False
        if is_belief_state:
            belief_match = re.search(r"<belief_state>(.*?)</belief_state>", output_str, re.DOTALL | re.IGNORECASE)
            return belief_match is not None
        if is_thinking:
            thinking_match = re.search(r"<thinking>(.*?)</thinking>", output_str, re.DOTALL | re.IGNORECASE)
            return thinking_match is not None
        else:
            thinking_match = re.search(r"<thinking>(.*?)</thinking>", output_str, re.DOTALL | re.IGNORECASE)
            belief_match = re.search(r"<belief_state>(.*?)</belief_state>", output_str, re.DOTALL | re.IGNORECASE)
            return thinking_match is None and belief_match is None

    @contextmanager
    def update_sampling_params(self, **kwargs):
        """Temporarily update sampling params, then roll back to previous values."""
        old_sampling_params_args = {}
        if kwargs:
            for key, value in kwargs.items():
                if hasattr(self.sampling_params, key):
                    old_value = getattr(self.sampling_params, key)
                    old_sampling_params_args[key] = old_value
                    setattr(self.sampling_params, key, value)
        yield
        for key, value in old_sampling_params_args.items():
            setattr(self.sampling_params, key, value)

    def _compute_step_forecasting_reward(
        self,
        goal: str,
        observations: List[str],
        actions: List[str],
        target_observation: str,
    ) -> float:
        """
        Compute length-normalized log-probability of o_{t+1} given context (step forecasting reward).

        Uses instruct/chat format for the model:
            User: <instruction with goal, history, and "Predict the next observation:">
            Assistant: <o_{t+1}> (target; we compute log P(o_{t+1} | context))

        Returns: r_t = (1 / |o_{t+1}|) * log P(o_{t+1} | context)
        """
        import re
        goal = goal.split("current state:")[0].strip()
        if not target_observation.strip():
            return 0.0

        # Build instruction content (goal + history; target is NOT included)
        lines = [
            "You are playing a text-based game. Given the goal and the history of observations and actions, predict the next observation that the environment will return.",
            "",
            "Goal: " + goal.strip(),
            "",
            "History:",
        ]
        for obs, act in zip(observations, actions, strict=True):
            lines.append("Observation: " + obs.strip())
            action_str = self._extract_action_from_output(act)
            if action_str == "No action found":
                action_str = act.strip()
            lines.append("Action: " + action_str)
        lines.append("")
        lines.append("Predict the next observation:")
        instruction_content = "\n".join(lines)

        # Use chat template for instruct models: user = instruction, assistant = target
        context_messages = [{"role": "user", "content": instruction_content}]
        full_messages = [
            {"role": "user", "content": instruction_content},
            {"role": "assistant", "content": target_observation},
        ]
        context_tokens = self.tokenizer.apply_chat_template(
            context_messages, add_generation_prompt=True, tokenize=True, add_special_tokens=True
        )
        full_tokens = self.tokenizer.apply_chat_template(
            full_messages, add_generation_prompt=False, tokenize=True, add_special_tokens=True
        )
        # Ensure list of ints (apply_chat_template may return tensor/ndarray)
        if hasattr(context_tokens, "tolist"):
            context_tokens = context_tokens.tolist()
            if context_tokens and isinstance(context_tokens[0], list):
                context_tokens = context_tokens[0]
        if hasattr(full_tokens, "tolist"):
            full_tokens = full_tokens.tolist()
            if full_tokens and isinstance(full_tokens[0], list):
                full_tokens = full_tokens[0]
        target_tokens = full_tokens[len(context_tokens) :]
        if len(target_tokens) == 0:
            return 0.0

        # Score via vLLM: pass full sequence, get prompt_logprobs, sum over target positions
        # try:
        score_params = SamplingParams(max_tokens=1, prompt_logprobs=1)
        outputs = self.inference_engine.generate(
            prompts=[TokensPrompt(prompt_token_ids=full_tokens)],
            sampling_params=score_params,
            use_tqdm=False,
        )
        prompt_logprobs = getattr(outputs[0], "prompt_logprobs", None) or (
            outputs[0].outputs[0].prompt_logprobs if outputs[0].outputs else None
        )
        if prompt_logprobs is None:
            return 0.0

        # Extract logprobs for target token positions (context_len to context_len+len(target)-1)
        # prompt_logprobs[i] = logprob of token at position i; first is often None
        log_prob_sum = 0.0
        for k in range(len(target_tokens)):
            pos = len(context_tokens) + k
            if pos < len(prompt_logprobs) and prompt_logprobs[pos] is not None:
                tok_id = target_tokens[k]
                lp_dict = prompt_logprobs[pos]
                if isinstance(lp_dict, dict) and tok_id in lp_dict:
                    log_prob_sum += lp_dict[tok_id].logprob
                elif hasattr(lp_dict, "get") and lp_dict.get(tok_id):
                    log_prob_sum += lp_dict[tok_id].logprob
        # except Exception:
        #     return 0.0

        return float(log_prob_sum) / len(target_tokens)

    def _compute_belief_state_structure_reward(self, output_str: str) -> float:
        """
        Extract belief state from <belief_state> </belief_state> and check if the
        structured schema is followed (LAST ACTION RESULT, LOCATION, WORLD MAP,
        INVENTORY, GOAL TRACKER, OBJECT STATUS, MISSING INFO).
        Returns a score in [0, 1] based on how many required fields are present.
        """
        belief_state_str = self._extract_belief_state_from_output(output_str)
        if not belief_state_str or not belief_state_str.strip():
            return 0.0

        belief_lower = belief_state_str.lower().strip()
        # Required schema fields from the structured belief state prompt
        required_fields = [
            "last action result",
            "location",
            "world map",
            "inventory",
            "goal tracker",
            "object status",
            "missing info",
        ]
        present = sum(1 for field in required_fields if field in belief_lower)
        frac = present / len(required_fields) if required_fields else 0.0
        return frac  # [0, 1] - caller scales to 0.5 when used

    def _compute_symbolic_belief_state_structure_reward(self, output_str: str) -> float:
        """
        Reward for the symbolic JSON belief state with probabilistic distributions.

        Scoring (max 1.0):
          0.40  parse bonus   — belief state is valid JSON and a dict
          0.30  key bonus     — fraction of required top-level keys present
          0.30  dist bonus    — for each item, check loc_dist and state_dist:
                                  * all values in [0, 1]
                                  * values sum to ≈ 1.0 (tolerance 0.05)
                                average across all items, split equally over both dists

        Returns score in [0, 1].
        """
        import json

        belief_state_str = self._extract_belief_state_from_output(output_str)
        if not belief_state_str or not belief_state_str.strip():
            return 0.0

        try:
            parsed = json.loads(belief_state_str.strip())
        except (json.JSONDecodeError, ValueError):
            return 0.0
        if not isinstance(parsed, dict):
            return 0.0

        parse_bonus = 0.40

        required_keys = ["map", "items", "inventory", "objective", "gap", "plan"]
        present = sum(1 for k in required_keys if k in parsed)
        key_bonus = 0.30 * (present / len(required_keys))

        def _dist_valid(d: dict) -> float:
            """Return 1.0 if d is a valid probability distribution, partial otherwise."""
            if not isinstance(d, dict) or len(d) == 0:
                return 0.0
            vals = list(d.values())
            numeric_vals = [v for v in vals if isinstance(v, (int, float))]
            all_in_range = len(numeric_vals) == len(vals) and all(0.0 <= v <= 1.0 for v in numeric_vals)
            sums_to_one = all_in_range and abs(sum(numeric_vals) - 1.0) <= 0.05
            return (0.5 if all_in_range else 0.0) + (0.5 if sums_to_one else 0.0)

        items = parsed.get("items", {})
        dist_bonus = 0.0
        if isinstance(items, dict) and len(items) > 0:
            item_scores = []
            for item_val in items.values():
                if not isinstance(item_val, dict):
                    item_scores.append(0.0)
                    continue
                loc_score   = _dist_valid(item_val.get("loc_dist", {}))
                state_score = _dist_valid(item_val.get("state_dist", {}))
                item_scores.append((loc_score + state_score) / 2.0)
            dist_bonus = 0.30 * (sum(item_scores) / len(item_scores))

        return parse_bonus + key_bonus + dist_bonus

    def _compute_memory_belief_state_structure_reward(self, output_str: str) -> float:
        """
        Score the BDI belief state on two equally-weighted axes (each contributes
        up to 0.5, combined total in [0, 1]):

        1. Section presence (weight 0.5): fraction of the 8 required labeled sections
           that are present — BELIEFS:, [MAP]:, [OBJECTS]:, DESIRES:, [OBJECTIVE]:,
           INTENTIONS:, [GAP]:, [PLAN]:.

        2. Uncertainty quality in [OBJECTS]: (weight 0.5): counts confidence
           percentages strictly between 0 % and 100 %, giving full credit at 3+
           intermediate values (mirrors _compute_freeform_bdi_uncertainty_reward).
             - 0 intermediate values → 0.0
             - 1 intermediate value  → 0.33
             - 2 intermediate values → 0.67
             - 3+ intermediate values → 1.0
        """
        belief_state_str = self._extract_belief_state_from_output(output_str)
        if not belief_state_str or not belief_state_str.strip():
            return 0.0

        belief_lower = belief_state_str.lower()

        # --- 1. Section presence ---
        required_fields = [
            "beliefs:",
            "[map]:",
            "[objects]:",
            "desires:",
            "[objective]:",
            "intentions:",
            "[gap]:",
            "[plan]:",
        ]
        present = sum(1 for field in required_fields if field in belief_lower)
        section_frac = present / len(required_fields)

        # --- 2. Uncertainty quality: intermediate % values in [OBJECTS] ---
        # Extract text from [OBJECTS]: up to the next known section header.
        objects_match = re.search(
            r"\[objects\]:(.*?)(?=\[map\]:|\[objective\]:|\[gap\]:|\[plan\]:"
            r"|desires:|intentions:|$)",
            belief_lower,
            re.DOTALL,
        )
        objects_text = objects_match.group(1) if objects_match else ""
        percentages = [int(m) for m in re.findall(r"\b(\d{1,3})%", objects_text)]
        intermediate = sum(1 for p in percentages if 0 < p < 100)
        # Full credit at 3+ intermediate values; mirrors _compute_freeform_bdi_uncertainty_reward.
        uncertainty_quality = min(1.0, intermediate / 3)

        return 0.5 * section_frac + 0.5 * uncertainty_quality

    def _compute_history_summary_belief_state_structure_reward(self, output_str: str) -> float:
        """
        Check whether the history-summary belief state (goal_memory_history_summary variant)
        contains the four key content categories:
          location/room, object/item, goal/progress, next/plan/action
        Returns a score in [0, 1] based on the fraction of categories present.
        """
        belief_state_str = self._extract_belief_state_from_output(output_str)
        if not belief_state_str or not belief_state_str.strip():
            return 0.0

        belief_lower = belief_state_str.lower()
        # Reward factual recall categories only; no planning/uncertainty keywords
        category_keywords = [
            ["location", "room", "i am in", "i'm in", "visited", "travelled", "moved"],
            ["object", "item", "found", "observed", "picked up", "key", "chest", "door", "container"],
            ["action", "took", "tried", "opened", "went", "examined", "dropped", "taken"],
            ["goal", "completed", "done", "achieved", "collected", "unlocked", "placed"],
        ]
        present = sum(
            1 for keywords in category_keywords
            if any(kw in belief_lower for kw in keywords)
        )
        return present / len(category_keywords)

    def _compute_freeform_bdi_structure_reward(self, output_str: str) -> float:
        """
        Check whether the free-form BDI belief state contains the three required
        section headers: BELIEFS:, DESIRES:, INTENTIONS:.
        Returns a score in [0, 1] based on the fraction of sections present.
        """
        belief_state_str = self._extract_belief_state_from_output(output_str)
        if not belief_state_str or not belief_state_str.strip():
            return 0.0

        belief_lower = belief_state_str.lower()
        required_fields = ["beliefs:", "desires:", "intentions:"]
        present = sum(1 for field in required_fields if field in belief_lower)
        return present / len(required_fields)

    # Ordered from most to least certain, mirroring the prompt's Likert scale.
    _UNCERTAINTY_PATTERNS = [
        r"\bconfirmed\b",
        r"\balmost certain\b",
        r"(?<!un)\bcertain\b",   # "certain" but not inside "uncertain"
        r"\bprobably\b|\bprobable\b",
        r"\blikely\b",
        r"\bpossibly\b|\bpossible\b",
        r"\bunlikely\b",
        r"\bdoubtful\b",
        r"\bunknown\b",
    ]

    def _compute_freeform_bdi_uncertainty_reward(self, output_str: str) -> float:
        """
        Reward the model for applying the natural-language uncertainty scale
        (certain/confirmed → almost certain → probable → possible →
         unlikely → doubtful → unknown) when describing objects in BELIEFS.

        Score in [0, 1]:
          0.0  — no uncertainty language found in the BELIEFS section.
          0.33 — one distinct uncertainty level used.
          0.67 — two distinct uncertainty levels used.
          1.0  — three or more distinct uncertainty levels used
                 (signals the model is actively differentiating per object).
        """
        belief_state_str = self._extract_belief_state_from_output(output_str)
        if not belief_state_str or not belief_state_str.strip():
            return 0.0

        # Prefer the BELIEFS subsection; fall back to the whole belief state.
        beliefs_match = re.search(
            r"BELIEFS:(.*?)(?:DESIRES:|INTENTIONS:|$)",
            belief_state_str,
            re.DOTALL | re.IGNORECASE,
        )
        text = beliefs_match.group(1) if beliefs_match else belief_state_str
        text_lower = text.lower()

        matched = sum(
            1 for pattern in self._UNCERTAINTY_PATTERNS
            if re.search(pattern, text_lower)
        )
        # Full credit at 3+ distinct levels to encourage per-object differentiation.
        return min(1.0, matched / 3)

    def _compute_nl_belief_state_uncertainty_reward(self, output_str: str) -> float:
        """
        Reward for the memory_belief_state variant, whose <belief_state> is pure
        natural language with no section headers.

        Searches the entire <belief_state> content for natural-language uncertainty
        words (certain, likely, probable, possibly, uncertain, unlikely, unknown, …).

        Score in [0, 1]:
          0.0  — no uncertainty language found.
          0.33 — one distinct uncertainty level used.
          0.67 — two distinct uncertainty levels used.
          1.0  — three or more distinct uncertainty levels used.
        """
        belief_state_str = self._extract_belief_state_from_output(output_str)
        if not belief_state_str or not belief_state_str.strip():
            return 0.0

        text_lower = belief_state_str.lower()
        matched = sum(
            1 for pattern in self._UNCERTAINTY_PATTERNS
            if re.search(pattern, text_lower)
        )
        return min(1.0, matched / 3)

    def _compute_action_confidence(
        self,
        output_str: str,
        token_ids: List[int],
        logprobs: Optional[List[Optional[Dict[int, Any]]]],
    ) -> float:
        """
        Compute mean confidence (probability) of tokens within <action> </action>.
        Converts logprob to probability via exp(logprob) and averages over all action tokens.
        Returns 0.0 if no action found or no logprobs; otherwise in (0, 1].
        """
        if not logprobs or len(logprobs) != len(token_ids):
            return 0.0
        action_match = re.search(r"<action>(.*?)</action>", output_str, re.DOTALL | re.IGNORECASE)
        if not action_match:
            return 0.0
        if action_match.group(1).strip() == "":
            return 0.0
        full_decoded = self.tokenizer.decode(token_ids, skip_special_tokens=True)
        action_start_marker = "<action>"
        action_end_marker = "</action>"
        start_idx = full_decoded.lower().find(action_start_marker.lower())
        end_idx = full_decoded.lower().find(action_end_marker.lower())
        if start_idx == -1 or end_idx == -1:
            return 0.0
        content_start = start_idx + len(action_start_marker)
        content_end = end_idx
        cumul_len = 0
        action_token_indices = []
        for i, tid in enumerate(token_ids):
            tok_str = self.tokenizer.decode([tid], skip_special_tokens=True)
            tok_len = len(tok_str)
            if cumul_len + tok_len > content_start and cumul_len < content_end:
                if tok_str.strip():  # exclude whitespace and newline-only tokens
                    action_token_indices.append(i)
            cumul_len += tok_len
        if not action_token_indices:
            return 0.0
        confidence_sum = 0.0
        # breakpoint()
        for i in action_token_indices:
            if i < len(logprobs) and logprobs[i] is not None:
                lp_dict = logprobs[i]
                tid = token_ids[i]
                lp_val = lp_dict.get(tid) if hasattr(lp_dict, "get") else (lp_dict[tid] if tid in lp_dict else None)
                if lp_val is not None:
                    logprob = lp_val.logprob if hasattr(lp_val, "logprob") else float(lp_val)
                    confidence_sum += np.exp(logprob)  # convert logprob to probability
        return float(confidence_sum) / len(action_token_indices) if action_token_indices else 0.0

    def _build_dual_prompt_messages(
        self, messages_batch: List[List[Dict]], selected_idx: List[int]
    ) -> Tuple[List[List[Dict]], List[List[Dict]]]:
        """
        Build two message batches: one with thinking prompt, one with direct action prompt.
        For each active instance, create both variants of the last user message.
        """
        thinking_suffix = "\n\nLet's think step by step inside the <thinking> </thinking> tags and output the final action within <action> </action> tags."
        direct_suffix = "\n\nOutput the final action directly within <action> </action> tags."
        messages_thinking = []
        messages_direct = []
        for idx in selected_idx:
            messages = messages_batch[idx]
            last_user = messages[-1]["content"]
            # Strip existing instruction suffix to get base (goal + current state)
            for suffix in [thinking_suffix, direct_suffix]:
                if suffix in last_user:
                    base = last_user.split(suffix)[0].strip()
                    break
            else:
                base = last_user.rstrip()
            thinking_content = base + thinking_suffix
            direct_content = base + direct_suffix
            msg_thinking = messages[:-1] + [{"role": "user", "content": thinking_content}]
            msg_direct = messages[:-1] + [{"role": "user", "content": direct_content}]
            messages_thinking.append(msg_thinking)
            messages_direct.append(msg_direct)
        return messages_thinking, messages_direct

    def _build_triple_prompt_messages(
        self,
        messages_batch: List[List[Dict]],
        selected_idx: List[int],
    ) -> Tuple[List[List[Dict]], List[List[Dict]], List[List[Dict]]]:
        """
        Build three message batches: thinking, direct, and belief_state prompts.
        Used when both use_dynamic_thinking and use_belief_state are True.
        Belief state is generated by main policy from conversation context (no past history template).
        """
        thinking_suffix = "\n\nLet's think step by step inside the <thinking> </thinking> tags and output the final action within <action> </action> tags."
        direct_suffix = "\n\nOutput the final action directly within <action> </action> tags."
        belief_state_suffix_short = "\n\nOutput your belief state within <belief_state> </belief_state> tags, then output the final action within <action> </action> tags."
        messages_thinking = []
        messages_direct = []
        messages_belief_state = []
        for i, idx in enumerate(selected_idx):
            messages = messages_batch[idx]
            last_user = messages[-1]["content"]
            # Strip existing instruction suffix to get base
            for suffix in [thinking_suffix, direct_suffix, belief_state_suffix_short, self.belief_state_suffix.strip()]:
                if suffix in last_user:
                    base = last_user.split(suffix)[0].strip()
                    break
            else:
                base = last_user.rstrip()
            thinking_content = base + thinking_suffix
            direct_content = base + direct_suffix
            belief_state_content = base + self.belief_state_suffix
            msg_thinking = messages[:-1] + [{"role": "user", "content": thinking_content}]
            msg_direct = messages[:-1] + [{"role": "user", "content": direct_content}]
            msg_belief_state = messages[:-1] + [{"role": "user", "content": belief_state_content}]
            messages_thinking.append(msg_thinking)
            messages_direct.append(msg_direct)
            messages_belief_state.append(msg_belief_state)
        return messages_thinking, messages_direct, messages_belief_state

    def _build_direct_belief_state_prompt_messages(
        self,
        messages_batch: List[List[Dict]],
        selected_idx: List[int],
    ) -> Tuple[List[List[Dict]], List[List[Dict]]]:
        """
        Build two message batches: direct and belief_state prompts.
        Used when use_dynamic_thinking is True - only direct and belief_state (no thinking).
        """
        direct_suffix = "\n\nOutput the final action directly within <action> </action> tags."
        belief_state_suffix_short = "\n\nOutput your belief state within <belief_state> </belief_state> tags, then output the final action within <action> </action> tags."
        messages_direct = []
        messages_belief_state = []
        for i, idx in enumerate(selected_idx):
            messages = messages_batch[idx]
            last_user = messages[-1]["content"]
            for suffix in [direct_suffix, belief_state_suffix_short, self.belief_state_suffix.strip()]:
                if suffix in last_user:
                    base = last_user.split(suffix)[0].strip()
                    break
            else:
                base = last_user.rstrip()
            direct_content = base + direct_suffix
            belief_state_content = base + self.belief_state_suffix
            msg_direct = messages[:-1] + [{"role": "user", "content": direct_content}]
            msg_belief_state = messages[:-1] + [{"role": "user", "content": belief_state_content}]
            messages_direct.append(msg_direct)
            messages_belief_state.append(msg_belief_state)
        return messages_direct, messages_belief_state

    def load_env(self, instance_dir: str, instance_id: str) -> TextWorldEnvBase:
        if self.env == "textworld":
            from .env import TextWorldEnv
            instance_env = TextWorldEnv(instance_file=os.path.join(instance_dir, f"{instance_id}.z8"))
        elif self.env == "alfworld":
            from .env import AlfWorldEnv
            instance_env = AlfWorldEnv(instance_file=os.path.join(instance_dir, f"{instance_id}.tw-pddl"))
        else:
            raise NotImplementedError(f"Environment {self.env} not supported in TextWorldAgent.")
        return instance_env
        

    def interact(self, instance_env: TextWorldEnvBase, action: str) -> Tuple[str, bool, float, TextWorldEnvBase]:
        """
        A one-step interaction with the current instance environment.

        Args:
            instance_env (TextWorldEnvBase): the textworld environment instance
            action (str): the action to take at this step
        Returns:
            next_obs (str): the next observation after taking the action
            has_won (bool): whether the game has been won
            reward (float): the reward obtained from taking the action
            instance_env (TextWorldEnvBase): the updated instance environment
        """
        next_obs, has_won, reward = instance_env.one_step(command=action)
        return next_obs, has_won, reward, instance_env

    def _build_fresh_step_context(
        self,
        idx: int,
        prompt_str_batch: List[str],
        all_belief_states_batch: List[List[str]],
        all_states_batch: List[List[str]],
    ) -> List[Dict]:
        """Build a fresh single-message context for decoupled trajectory mode (step k >= 1).

        The context contains:
          - game description (initial prompt minus its "current state:" section)
          - previous belief state (last extracted belief state, if any)
          - current observation with appropriate instruction suffix

        The prompt-building methods (_build_triple_prompt_messages etc.) will strip the
        trailing suffix and replace it with the correct variant for the current step.
        """
        initial_prompt = prompt_str_batch[idx]
        # Extract the game description (everything before "current state:")
        if "current state:" in initial_prompt:
            game_description = initial_prompt.split("current state:")[0].rstrip()
        else:
            game_description = initial_prompt

        # Current observation with suffix (appended at the end of the previous Phase 3)
        curr_obs_with_suffix = all_states_batch[idx][-1]

        prev_bs = all_belief_states_batch[idx][-1] if all_belief_states_batch[idx] else ""
        if prev_bs:
            user_content = (
                game_description + "\n\n"
                + "Belief state:\n" + prev_bs + "\n\n"
                + curr_obs_with_suffix
            )
        else:
            user_content = game_description + "\n\n" + curr_obs_with_suffix

        return [{"role": "user", "content": user_content}]

    def _build_initial_step_context(
        self,
        idx: int,
        prompt_str_batch: List[str],
        all_belief_states_batch: List[List[str]],
    ) -> List[Dict]:
        """Build a fresh single-message context for step k=0 when using the finetuned belief-state model.

        Equivalent to _build_fresh_step_context but for the very first step, where
        all_states_batch has only the original initial prompt (no Phase-3 entries yet).
        The initial prompt is split into game-description + obs-with-suffix so the
        belief state can be injected between them, matching the k>0 format exactly.
        """
        initial_prompt = prompt_str_batch[idx]
        if "current state:" in initial_prompt:
            game_description = initial_prompt.split("current state:")[0].rstrip()
            # Preserve the original obs + instruction suffix as-is
            curr_obs_with_suffix = "current state:" + initial_prompt.split("current state:", 1)[1]
        else:
            game_description = initial_prompt
            curr_obs_with_suffix = initial_prompt

        initial_bs = all_belief_states_batch[idx][-1] if all_belief_states_batch[idx] else ""

        if initial_bs:
            user_content = (
                game_description + "\n\n"
                + "Belief state:\n" + initial_bs + "\n\n"
                + curr_obs_with_suffix
            )
        else:
            user_content = initial_prompt  # no belief state available; leave prompt unchanged

        return [{"role": "user", "content": user_content}]

    def run(self) -> DataProto:
        """
        The main function of generating multiturn rollouts by interacting with the textworld environments.

        Returns:
            A DataProto with the following fields:
            Tensor batch:
            - prompts: [bsz, prompt_length], prompt token ids from dataset.
            - responses: [bsz, response_length], output token ids including both env and agent responses
            - response_mask: [bsz, response_length], 1 for agent tokens, 0 for env tokens.
            - input_ids: [bsz, prompt_length + response_length], whole sequence token ids, including prompt tokens and response tokens.
            - attention_mask: [bsz, prompt_length + response_length], 0 for padding tokens, 1 for other tokens.
            - position_ids: [bsz, prompt_length + response_length], incremental position ids.

            Non-tensor batch:
            - sep_token_positions: 1D object ndarray, int indices of sep token ids in responses
            - final_rewards: 1D float ndarray, float values of 1.0/0 indicating game success status
            - interm_rewards: 1D object ndarray, list of float values of intermediate rewards per action
            - max_total_rewards: 1D float ndarray, float values of maximum total rewards for each instance
            - raw_response_text: 1D object ndarray, action only sequence, for eval purpose

        """
        messages_batch = [messages for messages in self.input_batch.non_tensor_batch["raw_prompt"]] 
        assert all(len(messages) == 1 for messages in messages_batch)
        # the initial message should be the following format: [{"role": "user", "content": ""}]
        # save the first user prompt
        prompt_str_batch = [messages[0]["content"] for messages in messages_batch] 
        # save the list of actions taken so far
        all_actions_batch = [[] for _ in range(self.batch_size)] 
        # save the list of env states observed so far
        all_states_batch = [[prompt_str_batch[i]] for i in range(self.batch_size)]
        # save the active status of each instance in the batch
        # active status: True if the instance is still active, False if the instance has stopped
        active_batch_idx = [True for _ in range(self.batch_size)]
        # save the final reward (1.0/0.0) for each instance
        final_reward_batch = [0.0 for _ in range(self.batch_size)] 
        # save the intermediate reward for each action taken so far
        interm_reward_batch = [[] for _ in range(self.batch_size)]
        # save the accumulated reward for each instance
        # accumulated reward: used in dense reward mode, sum of previous intermediate rewards
        accumulated_reward_batch = [0.0 for _ in range(self.batch_size)]
        # save the environment pddl instance for each batch
        instance_env_batch = [self.load_env(self.instance_dir, self.instance_id_batch[i]) for i in range(self.batch_size)] 
        # save the list of belief states observed so far
        all_belief_states_batch = [[] for _ in range(self.batch_size)]

        # Decoupled trajectory mode: per-step fresh contexts and responses for step-level DataProto
        # step_fresh_contexts_batch[i][k] = fresh 1-message context used at step k for trajectory i
        # step_responses_batch_text[i][k]  = raw model output at step k for trajectory i
        step_fresh_contexts_batch = [[] for _ in range(self.batch_size)]
        step_responses_batch_text = [[] for _ in range(self.batch_size)]

        # Reset per-rollout belief-state training data collection
        self.belief_state_training_steps = []
        self._bs_step_traj_map = []
        # Background LLM reward computation: each belief step's reward HTTP
        # calls are submitted to a thread pool immediately when the belief state
        # is generated, so they overlap with subsequent rollout iterations.
        # Results are collected at the end of run() before belief PPO.
        # Each entry: (step_idx, Future[(st_r, div_r)])
        self._reward_futures: List[Tuple[int, Any]] = []
        _need_llm_rewards = bool(
            self.belief_reward_model_url
            and not self.belief_lm_task_reward_only
            and self.belief_state_trainer is not None
            and self.decouple_trajectory
        )
        if _need_llm_rewards:
            from concurrent.futures import ThreadPoolExecutor
            self._reward_executor = ThreadPoolExecutor(max_workers=50)
        else:
            self._reward_executor = None

        # Pre-loop: generate initial belief states (k=0, no prior belief state).
        # When belief_state_trainer is set, use the trainer (joint training mode).
        # Otherwise fall back to the external HTTP server (static model mode).
        _use_trainer = self.belief_state_trainer is not None and self.decouple_trajectory
        _use_server  = (not _use_trainer) and self.belief_state_model_url and self.decouple_trajectory

        if _use_trainer or _use_server:
            init_bs_requests: List[Tuple[int, str, str, str]] = []
            for idx in range(self.batch_size):
                initial_prompt = prompt_str_batch[idx]
                try:
                    goal = (
                        initial_prompt.split("current state:")[0].rstrip()
                        if "current state:" in initial_prompt
                        else initial_prompt
                    )
                    obs_0 = (
                        initial_prompt.split("current state:")[1].split("\n\n")[0].strip()
                        if "current state:" in initial_prompt
                        else ""
                    )
                    if obs_0:
                        init_bs_requests.append((idx, goal, "", obs_0))
                except Exception as e:
                    logger.warning("Could not build initial belief-state request for idx=%d: %s", idx, e)

            if init_bs_requests:
                print(
                    f"[BELIEF_GEN] initial (pre-policy-loop) n={len(init_bs_requests)} "
                    f"trainer={_use_trainer}",
                    flush=True,
                )
                if _use_trainer:
                    # Joint training mode: use the separate trainable belief-state model
                    prompts_text = [
                        self._build_belief_state_user_prompt(g, p, o)
                        for (_, g, p, o) in init_bs_requests
                    ]
                    (
                        belief_texts,
                        prompt_ids_list,
                        response_ids_list,
                        old_lps_list,
                    ) = self.belief_state_trainer.generate_batch(prompts_text)
                    # discounted_task_r assigned in _finalize_belief_state_training
                    _init_prompt_ids = {
                        idx: (p_ids, r_ids, olp)
                        for (idx, _, _, _), p_ids, r_ids, olp
                        in zip(
                            init_bs_requests,
                            prompt_ids_list,
                            response_ids_list,
                            old_lps_list,
                        )
                    }
                else:
                    # Static server mode: call HTTP API
                    belief_texts = self._batch_call_belief_state_model(
                        [(g, p, o) for (_, g, p, o) in init_bs_requests]
                    )
                    _init_prompt_ids = {}

                for i_req, (idx, _, _, obs_str) in enumerate(init_bs_requests):
                    bs = belief_texts[i_req]
                    if bs:
                        all_belief_states_batch[idx].append(bs)
                        if _use_trainer and idx in _init_prompt_ids:
                            p_ids, r_ids, olp = _init_prompt_ids[idx]
                            step_idx = len(self.belief_state_training_steps)
                            self.belief_state_training_steps.append(
                                BeliefStateTrainingStep(
                                    prompt_ids=p_ids,
                                    response_ids=r_ids,
                                    state_tracking_r=0.0,   # filled after loop
                                    state_correctness_r=0.0, # filled after loop
                                    discounted_task_r=0.0,  # filled after episode
                                    alpha=self.belief_alpha,
                                    old_token_log_probs=olp,
                                    format_compliance_r=compute_format_compliance_score(bs),
                                )
                            )
                            self._bs_step_traj_map.append((step_idx, idx, 0))
                            # Fire off LLM reward computation in background
                            # immediately so it overlaps with rollout iterations.
                            if self._reward_executor is not None:
                                raw_env = instance_env_batch[idx].get_raw_state_facts_str()
                                future = self._reward_executor.submit(
                                    compute_single_belief_rewards,
                                    "", obs_str, bs, raw_env,
                                    self.belief_reward_model_url,
                                    self.belief_reward_model_name,
                                )
                                self._reward_futures.append((step_idx, future))

        # Synchronize all TP ranks after pre-loop belief generation.
        # TP rank 0 (subprocess vLLM) may take several seconds; non-leader ranks
        # have no trainer and finish instantly.  The barrier ensures both ranks
        # call policy llm.generate() together for the first iteration.
        if self.belief_use_tp_barrier and torch.distributed.is_initialized():
            torch.distributed.barrier()
            # Broadcast belief states from rank 0 so all TP ranks build identical
            # fresh contexts (decouple mode injects prev belief state into the prompt).
            # Without this, rank 0 prompts include belief text but rank 1 prompts don't,
            # causing different inputs to the shared vLLM engine → TP deadlock.
            obj_list = [all_belief_states_batch]
            torch.distributed.broadcast_object_list(obj_list, src=0)
            all_belief_states_batch = obj_list[0]

        global_step = self.input_batch.meta_info.get("global_steps", 0)
        warmup_steps = 25
        in_warmup = global_step < warmup_steps

        print(f"in_warmup: {in_warmup}")

        # Start multi-turn rollouts in batches
        from tqdm import tqdm
        # Track which prompt type is used (for debugging and next turn)
        # "thinking" | "direct" | "belief_state" - reflects actual prompt type per variant
        if self.thinking_variant in ("belief_state", "memory_belief_state", "symbolic_belief_state", "goal_memory_belief_state", "goal_memory_history_summary", "goal_memory_freeform_bdi"):
            default_prompt_type = "belief_state"
        elif self.thinking_variant == "symbolic_belief_state_periodic":
            default_prompt_type = "thinking"
        elif self.thinking_variant == "direct":
            default_prompt_type = "direct"
        elif self.use_dynamic_thinking and self.thinking_variant == "step-by-step":
            default_prompt_type = "direct"  # dynamic thinking: only direct and belief_state
        else:
            default_prompt_type = "thinking"
        prompt_type_for_next_batch = {i: default_prompt_type for i in range(self.batch_size)}
        for k in range(self.max_iter):
            # Store winning prompt content so conversation history matches output (input = prompt that produced output)
            winning_message_content_by_idx = {}
            # Select active instances (instances that stop early) from batch at each turn
            selected_idx = np.where(active_batch_idx)[0].tolist()

            # Act: run prompts, pick higher confidence output, use that for current step
            # Decoupled trajectory: temporarily replace each active instance's full chat history
            # with a fresh 2-message context (game description + prev belief state + current obs)
            # so that generation does not depend on the accumulated conversation history.
            # All existing prompt-building helpers work unchanged since they strip/re-add suffixes.
            saved_messages_for_decouple: Dict[int, List[Dict]] = {}
            if self.decouple_trajectory:
                for idx in selected_idx:
                    saved_messages_for_decouple[idx] = messages_batch[idx]
                    if k == 0:
                        messages_batch[idx] = self._build_initial_step_context(
                            idx, prompt_str_batch, all_belief_states_batch
                        )
                    else:
                        messages_batch[idx] = self._build_fresh_step_context(
                            idx, prompt_str_batch, all_belief_states_batch, all_states_batch
                        )

            # Build active_messages_batch AFTER any fresh-context substitution so the
            # default single-inference branch always sees the up-to-date context.
            active_messages_batch = [messages_batch[idx] for idx in selected_idx]

            is_first_step = k == 0
            if self.use_dynamic_thinking and self.thinking_variant == "step-by-step" and is_first_step:
                # First step: use direct prompt only (no thinking, no dynamic selection)
                messages_direct, _ = self._build_direct_belief_state_prompt_messages(
                    messages_batch, selected_idx,
                )
                output_str_batch, valid_output_batch_idx = self.batch_generate(messages_direct)
                for i, idx in enumerate(selected_idx):
                    prompt_type_for_next_batch[idx] = "direct"
                    winning_message_content_by_idx[idx] = messages_direct[i][-1]["content"]
            elif self.use_dynamic_thinking and self.thinking_variant in ("step-by-step", "step-by-step-dynamic") and not is_first_step:
                # Dynamic thinking: only direct and belief_state (no thinking). Skip on first step.
                messages_direct, messages_belief_state = self._build_direct_belief_state_prompt_messages(
                    messages_batch, selected_idx,
                )
                n_active = len(selected_idx)
                if in_warmup:
                    # Warmup: randomly pick direct or belief_state per instance
                    choices = ["direct", "belief_state"]
                    prompt_type_per_instance = [np.random.choice(choices) for _ in range(n_active)]
                    warmup_messages = []
                    for i in range(n_active):
                        pt = prompt_type_per_instance[i]
                        if pt == "direct":
                            warmup_messages.append(messages_direct[i])
                        else:
                            warmup_messages.append(messages_belief_state[i])
                    output_str_batch, valid_output_batch_idx = self.batch_generate(warmup_messages)
                    for i in range(n_active):
                        idx = selected_idx[i]
                        prompt_type_for_next_batch[idx] = prompt_type_per_instance[i]
                        pt = prompt_type_per_instance[i]
                        if pt == "direct":
                            winning_message_content_by_idx[idx] = messages_direct[i][-1]["content"]
                        else:
                            winning_message_content_by_idx[idx] = messages_belief_state[i][-1]["content"]
                else:
                    print(f"Calculating confidence for {len(selected_idx)} instances")
                    combined_messages = messages_direct + messages_belief_state
                    (
                        combined_output_str,
                        combined_valid_idx,
                        combined_logprobs,
                        combined_token_ids,
                    ) = self.batch_generate_with_logprobs(combined_messages)
                    output_str_batch = []
                    valid_output_batch_idx = []
                    for i in range(n_active):
                        idx = selected_idx[i]
                        out_direct = combined_output_str[i]
                        out_belief = combined_output_str[i + n_active]
                        valid_direct = combined_valid_idx[i]
                        valid_belief = combined_valid_idx[i + n_active]
                        logprobs_direct = combined_logprobs[i] if combined_logprobs else None
                        logprobs_belief = combined_logprobs[i + n_active] if combined_logprobs else None
                        token_ids_direct = combined_token_ids[i] if combined_token_ids else []
                        token_ids_belief = combined_token_ids[i + n_active] if combined_token_ids else []
                        format_ok_direct = self._has_correct_format(out_direct, is_thinking=False, is_belief_state=False)
                        format_ok_belief = self._has_correct_format(out_belief, is_thinking=False, is_belief_state=True)
                        conf_direct = (
                            self._compute_action_confidence(out_direct, token_ids_direct, logprobs_direct)
                            if format_ok_direct else 0.0
                        )
                        conf_belief = (
                            self._compute_action_confidence(out_belief, token_ids_belief, logprobs_belief)
                            if format_ok_belief else 0.0
                        )
                        # Pick highest confidence among valid outputs
                        candidates = [
                            (conf_direct, "direct", out_direct, valid_direct, messages_direct[i][-1]["content"]),
                            (conf_belief, "belief_state", out_belief, valid_belief, messages_belief_state[i][-1]["content"]),
                        ]
                        candidates.sort(key=lambda x: (x[0], x[3]), reverse=True)  # sort by conf desc, then valid first
                        best = candidates[0]
                        output_str_batch.append(best[2])
                        valid_output_batch_idx.append(best[3])
                        prompt_type_for_next_batch[idx] = best[1]
                        winning_message_content_by_idx[idx] = best[4]
            elif self.thinking_variant in ("belief_state", "memory_belief_state", "symbolic_belief_state", "goal_memory_belief_state", "goal_memory_history_summary", "goal_memory_freeform_bdi"):
                # Always use belief_state prompt
                _, _, messages_belief_state = self._build_triple_prompt_messages(
                    messages_batch, selected_idx,
                )
                output_str_batch, valid_output_batch_idx = self.batch_generate(messages_belief_state)
                for i, idx in enumerate(selected_idx):
                    prompt_type_for_next_batch[idx] = "belief_state"
                    winning_message_content_by_idx[idx] = messages_belief_state[i][-1]["content"]
            elif self.thinking_variant == "symbolic_belief_state_periodic":
                # Every 3rd step (k % 3 == 2): forced symbolic belief state.
                # Other steps: step-by-step thinking always; when use_dynamic_thinking=True,
                # confidence-based selection between thinking and symbolic belief state.
                messages_thinking, _, messages_belief_state = self._build_triple_prompt_messages(
                    messages_batch, selected_idx,
                )
                n_active = len(selected_idx)
                use_belief_this_step = (k % 3 == 2)
                if use_belief_this_step:
                    output_str_batch, valid_output_batch_idx = self.batch_generate(messages_belief_state)
                    for i, idx in enumerate(selected_idx):
                        prompt_type_for_next_batch[idx] = "belief_state"
                        winning_message_content_by_idx[idx] = messages_belief_state[i][-1]["content"]
                elif self.use_dynamic_thinking:
                    if in_warmup:
                        choices = ["thinking", "belief_state"]
                        prompt_type_per_instance = [np.random.choice(choices) for _ in range(n_active)]
                        warmup_messages = [
                            messages_belief_state[i] if prompt_type_per_instance[i] == "belief_state"
                            else messages_thinking[i]
                            for i in range(n_active)
                        ]
                        output_str_batch, valid_output_batch_idx = self.batch_generate(warmup_messages)
                        for i in range(n_active):
                            idx = selected_idx[i]
                            prompt_type_for_next_batch[idx] = prompt_type_per_instance[i]
                            winning_message_content_by_idx[idx] = warmup_messages[i][-1]["content"]
                    else:
                        print(f"Calculating confidence for {len(selected_idx)} instances")
                        combined_messages = messages_thinking + messages_belief_state
                        (
                            combined_output_str,
                            combined_valid_idx,
                            combined_logprobs,
                            combined_token_ids,
                        ) = self.batch_generate_with_logprobs(combined_messages)
                        output_str_batch = []
                        valid_output_batch_idx = []
                        for i in range(n_active):
                            idx = selected_idx[i]
                            out_thinking = combined_output_str[i]
                            out_belief = combined_output_str[i + n_active]
                            valid_thinking = combined_valid_idx[i]
                            valid_belief = combined_valid_idx[i + n_active]
                            logprobs_thinking = combined_logprobs[i] if combined_logprobs else None
                            logprobs_belief = combined_logprobs[i + n_active] if combined_logprobs else None
                            token_ids_thinking = combined_token_ids[i] if combined_token_ids else []
                            token_ids_belief = combined_token_ids[i + n_active] if combined_token_ids else []
                            format_ok_thinking = self._has_correct_format(out_thinking, is_thinking=True, is_belief_state=False)
                            format_ok_belief = self._has_correct_format(out_belief, is_thinking=False, is_belief_state=True)
                            conf_thinking = (
                                self._compute_action_confidence(out_thinking, token_ids_thinking, logprobs_thinking)
                                if format_ok_thinking else 0.0
                            )
                            conf_belief = (
                                self._compute_action_confidence(out_belief, token_ids_belief, logprobs_belief)
                                if format_ok_belief else 0.0
                            )
                            candidates = [
                                (conf_thinking, "thinking", out_thinking, valid_thinking, messages_thinking[i][-1]["content"]),
                                (conf_belief, "belief_state", out_belief, valid_belief, messages_belief_state[i][-1]["content"]),
                            ]
                            candidates.sort(key=lambda x: (x[0], x[3]), reverse=True)
                            best = candidates[0]
                            output_str_batch.append(best[2])
                            valid_output_batch_idx.append(best[3])
                            prompt_type_for_next_batch[idx] = best[1]
                            winning_message_content_by_idx[idx] = best[4]
                else:
                    # use_dynamic_thinking=False on non-3rd steps: step-by-step only
                    output_str_batch, valid_output_batch_idx = self.batch_generate(messages_thinking)
                    for i, idx in enumerate(selected_idx):
                        prompt_type_for_next_batch[idx] = "thinking"
                        winning_message_content_by_idx[idx] = messages_thinking[i][-1]["content"]
            else:
                # direct or step-by-step (without dynamic thinking): single inference
                output_str_batch, valid_output_batch_idx = self.batch_generate(active_messages_batch)
                pt = "direct" if self.thinking_variant == "direct" else "thinking"
                for i, idx in enumerate(selected_idx):
                    prompt_type_for_next_batch[idx] = pt
                    winning_message_content_by_idx[idx] = active_messages_batch[i][-1]["content"]

            # --- Decoupled trajectory bookkeeping ---
            # Record the actual prompt context used at this step (before restoring the full history)
            # so that convert_result_to_step_dataproto can build per-step training instances.
            if self.decouple_trajectory:
                for i, idx in enumerate(selected_idx):
                    if valid_output_batch_idx[i]:
                        ctx_content = winning_message_content_by_idx.get(
                            idx, messages_batch[idx][-1]["content"]
                        )
                        step_fresh_contexts_batch[idx].append(
                            [{"role": "user", "content": ctx_content}]
                        )

            # Restore full chat history after generation (modified for all k in decouple mode)
            for idx, saved in saved_messages_for_decouple.items():
                messages_batch[idx] = saved

            # Phase 1: Run env interactions
            env_results = {}
            action_found_no_thinking_by_idx = {}
            action_found_no_belief_state_by_idx = {}

            for i in range(len(selected_idx)):
                if not valid_output_batch_idx[i]:
                    active_batch_idx[selected_idx[i]] = False
                    continue

                all_actions_batch[selected_idx[i]].append(output_str_batch[i])
                action_only_str = self._extract_action_from_output(output_str_batch[i])
                idx = selected_idx[i]

                # Get prompt that produced this output (for format check)
                prompt_content = winning_message_content_by_idx.get(idx, messages_batch[idx][-1]["content"])
                is_thinking_prompt = "Let's think step by step" in prompt_content
                is_belief_state_prompt = (
                    "Output your belief state within <belief_state>" in prompt_content
                    or "Output the updated belief state within <belief_state>" in prompt_content
                    or "Output your updated BDI model within <belief_state>" in prompt_content
                    or "Output your symbolic belief state as JSON within <belief_state>" in prompt_content
                    or "Output a factual summary of your past observations within <belief_state>" in prompt_content
                    or "Do not create separate XML tags for BELIEFS, DESIRES, or INTENTIONS" in prompt_content
                )
                format_ok = self._has_correct_format(
                    output_str_batch[i], is_thinking_prompt, is_belief_state=is_belief_state_prompt
                )
                action_found_no_thinking = (
                    action_only_str != "No action found"
                    and is_thinking_prompt
                    and not format_ok
                )
                action_found_no_belief_state = (
                    action_only_str != "No action found"
                    and is_belief_state_prompt
                    and not format_ok
                )

                if action_found_no_thinking:
                    # Reject output: don't advance env, show error (same pattern as "No action found")
                    action_found_no_thinking_by_idx[idx] = True
                    action_found_no_belief_state_by_idx[idx] = False
                    env_results[idx] = (
                        "Your response did not include thinking. Thinking is required. Please provide your reasoning in <thinking> </thinking> tags before the action.",
                        False,
                        0.0,
                        action_only_str,
                    )
                elif action_found_no_belief_state:
                    action_found_no_thinking_by_idx[idx] = False
                    action_found_no_belief_state_by_idx[idx] = True
                    env_results[idx] = (
                        "Your response did not include a belief state. A belief state is required. Please provide your belief state within <belief_state> </belief_state> tags before the action.",
                        False,
                        0.0,
                        action_only_str,
                    )
                else:
                    action_found_no_thinking_by_idx[idx] = False
                    action_found_no_belief_state_by_idx[idx] = False
                    next_obs, has_won, reward, next_instance_env = self.interact(
                        instance_env=instance_env_batch[idx], action=action_only_str
                    )
                    instance_env_batch[idx] = next_instance_env
                    env_results[idx] = (next_obs, has_won, reward, action_only_str)

                if action_only_str == "No action found":
                    env_results[idx] = ("No action found within <action> </action> tags", has_won, reward, action_only_str)
                elif action_only_str != "No action found" and not action_found_no_thinking_by_idx.get(idx, False) and not action_found_no_belief_state_by_idx.get(idx, False):
                    pass  # env advanced successfully

            n_selected = len(selected_idx)
            n_invalid_output = sum(1 for v in valid_output_batch_idx if not v)
            n_format_fail_thinking = sum(1 for v in action_found_no_thinking_by_idx.values() if v)
            n_format_fail_belief = sum(1 for v in action_found_no_belief_state_by_idx.values() if v)
            n_no_action = sum(
                1 for i in range(n_selected)
                if valid_output_batch_idx[i]
                and env_results.get(selected_idx[i], (None, None, None, None))[3] == "No action found"
            )
            n_env_step = n_selected - n_invalid_output - n_format_fail_thinking - n_format_fail_belief - n_no_action
            print(
                f"[PHASE1] k={k} selected={n_selected} env_step={n_env_step} "
                f"invalid_output={n_invalid_output} "
                f"format_fail_thinking={n_format_fail_thinking} "
                f"format_fail_belief={n_format_fail_belief} "
                f"no_action={n_no_action}",
                flush=True,
            )

            # Phase 2a: Belief state - from main policy only (when belief_state option won).
            # Skipped when a finetuned belief-state model is configured (Phase 2b handles it).
            belief_states_by_idx = {}
            if not (self.belief_state_model_url and self.decouple_trajectory):
                for i in range(len(selected_idx)):
                    idx = selected_idx[i]
                    if not valid_output_batch_idx[i]:
                        continue
                    prompt_type = prompt_type_for_next_batch.get(idx, "thinking")
                    if prompt_type == "belief_state":
                        agent_belief = self._extract_belief_state_from_output(output_str_batch[i])
                        belief_states_by_idx[idx] = agent_belief
                        all_belief_states_batch[idx].append(agent_belief)

            # Phase 2b: Belief state generation after each env step.
            # Uses goal + previous predicted belief state + current observation,
            # matching the SFT training distribution.
            # - Joint training mode (belief_state_trainer set): use the trainable model,
            #   collect training data (prompt_ids, response_ids, state_tracking_reward).
            # - Static server mode (belief_state_model_url set): call the HTTP API.
            _phase2b_use_trainer = self.belief_state_trainer is not None and self.decouple_trajectory
            _phase2b_use_server  = (not _phase2b_use_trainer) and self.belief_state_model_url and self.decouple_trajectory

            if _phase2b_use_trainer or _phase2b_use_server:
                bs_requests: List[Tuple[int, str, str, str]] = []
                for i in range(len(selected_idx)):
                    idx = selected_idx[i]
                    if not valid_output_batch_idx[i]:
                        continue
                    # Skip steps where the env did not actually advance
                    if (
                        action_found_no_thinking_by_idx.get(idx, False)
                        or action_found_no_belief_state_by_idx.get(idx, False)
                    ):
                        continue
                    next_obs_bs, _, _, action_for_bs = env_results.get(idx, (None, None, None, None))
                    if next_obs_bs is None or action_for_bs == "No action found":
                        continue
                    try:
                        initial_prompt = prompt_str_batch[idx]
                        goal = (
                            initial_prompt.split("current state:")[0].rstrip()
                            if "current state:" in initial_prompt
                            else initial_prompt
                        )
                        # Use the most recent predicted belief state as the previous belief state
                        prev_bs = all_belief_states_batch[idx][-1] if all_belief_states_batch[idx] else ""
                        bs_requests.append((idx, goal, prev_bs, next_obs_bs))
                    except Exception as e:
                        logger.warning(
                            "Could not build belief-state request for idx=%d: %s", idx, e
                        )

                if bs_requests:
                    print(
                        f"[BELIEF_GEN] after env step turn_k={k} n={len(bs_requests)} "
                        f"trainer={_phase2b_use_trainer}",
                        flush=True,
                    )
                    if _phase2b_use_trainer:
                        prompts_text = [
                            self._build_belief_state_user_prompt(g, p, o)
                            for (_, g, p, o) in bs_requests
                        ]
                        (
                            belief_texts,
                            prompt_ids_list,
                            response_ids_list,
                            old_lps_list,
                        ) = self.belief_state_trainer.generate_batch(prompts_text)

                        for (idx, g, p, obs_str), bs, p_ids, r_ids, olp in zip(
                            bs_requests,
                            belief_texts,
                            prompt_ids_list,
                            response_ids_list,
                            old_lps_list,
                        ):
                            if bs:
                                all_belief_states_batch[idx].append(bs)
                                step_idx = len(self.belief_state_training_steps)
                                self.belief_state_training_steps.append(
                                    BeliefStateTrainingStep(
                                        prompt_ids=p_ids,
                                        response_ids=r_ids,
                                        state_tracking_r=0.0,   # filled after loop
                                        state_correctness_r=0.0, # filled after loop
                                        discounted_task_r=0.0,  # filled after episode
                                        alpha=self.belief_alpha,
                                        old_token_log_probs=olp,
                                        format_compliance_r=compute_format_compliance_score(bs),
                                    )
                                )
                                self._bs_step_traj_map.append((step_idx, idx, k))
                                # Fire off LLM reward computation in background
                                # immediately so it overlaps with rollout iterations.
                                if self._reward_executor is not None:
                                    raw_env = instance_env_batch[idx].get_raw_state_facts_str()
                                    future = self._reward_executor.submit(
                                        compute_single_belief_rewards,
                                        p, obs_str, bs, raw_env,
                                        self.belief_reward_model_url,
                                        self.belief_reward_model_name,
                                    )
                                    self._reward_futures.append((step_idx, future))
                    else:
                        belief_texts = self._batch_call_belief_state_model(
                            [(g, p, o) for (_, g, p, o) in bs_requests]
                        )
                        for (idx, _, _, _), bs in zip(bs_requests, belief_texts):
                            if bs:
                                all_belief_states_batch[idx].append(bs)

            # Synchronize all TP ranks after Phase-2b belief generation so they all
            # reach the next policy llm.generate() call simultaneously.
            # Called every loop iteration on both TP leader (after actual generation)
            # and non-leader (immediately, since it has no trainer).
            if self.belief_use_tp_barrier and torch.distributed.is_initialized():
                torch.distributed.barrier()
                # Broadcast updated belief states from rank 0 to all TP ranks so that
                # _build_fresh_step_context (decouple mode) builds identical prompts on
                # every rank.  Rank 0 has the latest belief state; rank 1 has none.
                obj_list = [all_belief_states_batch]
                torch.distributed.broadcast_object_list(obj_list, src=0)
                all_belief_states_batch = obj_list[0]

            # Phase 3: Update all data structures
            for i in range(len(selected_idx)):
                if not valid_output_batch_idx[i]:
                    continue
                idx = selected_idx[i]
                next_obs, has_won, reward, action_only_str = env_results[idx]

                # Always use the raw environment observation for the next turn's "current state"
                # so the agent sees proper env feedback (not its own belief state)
                final_obs = next_obs

                # direct: never use thinking. step-by-step: use confidence-based selection when use_dynamic_thinking.
                # When action_found_no_thinking or action_found_no_belief_state: force the required prompt for retry.
                prompt_type = prompt_type_for_next_batch.get(idx, "thinking")
                if action_found_no_thinking_by_idx.get(idx, False):
                    use_thinking_prompt = True  # retry with thinking required
                    use_belief_state_prompt = False
                elif action_found_no_belief_state_by_idx.get(idx, False):
                    use_thinking_prompt = False
                    use_belief_state_prompt = True  # retry with belief_state required
                elif self.thinking_variant == "direct":
                    use_thinking_prompt = False
                    use_belief_state_prompt = False
                elif self.thinking_variant in ("belief_state", "memory_belief_state", "symbolic_belief_state", "goal_memory_belief_state", "goal_memory_history_summary", "goal_memory_freeform_bdi"):
                    use_thinking_prompt = False
                    use_belief_state_prompt = True
                elif self.thinking_variant == "symbolic_belief_state_periodic":
                    next_is_forced_belief = (k + 1) % 3 == 2
                    if next_is_forced_belief:
                        use_thinking_prompt = False
                        use_belief_state_prompt = True
                    elif self.use_dynamic_thinking:
                        use_thinking_prompt = prompt_type == "thinking"
                        use_belief_state_prompt = prompt_type == "belief_state"
                    else:
                        use_thinking_prompt = True
                        use_belief_state_prompt = False
                elif self.thinking_variant == "step-by-step":
                    if self.use_dynamic_thinking:
                        use_thinking_prompt = prompt_type == "thinking"
                        use_belief_state_prompt = prompt_type == "belief_state"
                    else:
                        use_thinking_prompt = True
                        use_belief_state_prompt = False
                else:
                    use_thinking_prompt = False
                    use_belief_state_prompt = False

                print(f"prompt_type: {prompt_type}")
                # Check format for reward (format_ok_prev: output matched prompt's expected format).
                # Read the winning prompt content directly — do NOT read from messages_batch[-1]
                # because in decouple mode the full conversation history has been restored and its
                # last message is the *previous* step's observation string, not the prompt that
                # produced this output.
                input_text = winning_message_content_by_idx.get(idx, messages_batch[idx][-1]["content"])
                output_text = all_actions_batch[idx][-1]
                is_thinking_prompt_prev = "Let's think step by step" in input_text
                is_belief_state_prompt_prev = (
                    "Output your belief state within <belief_state>" in input_text
                    or "Output the updated belief state within <belief_state>" in input_text
                    or "Output your updated BDI model within <belief_state>" in input_text
                    or "Output your symbolic belief state as JSON within <belief_state>" in input_text
                    or "Output a factual summary of your past observations within <belief_state>" in input_text
                    or "Do not create separate XML tags for BELIEFS, DESIRES, or INTENTIONS" in input_text
                )
                format_ok_prev = self._has_correct_format(
                    output_text, is_thinking_prompt_prev, is_belief_state=is_belief_state_prompt_prev
                )

                if use_thinking_prompt:
                    all_states_batch[idx].append(
                        f"current state: {final_obs}" + "\n\n"
                        + "Let's think step by step inside the <thinking> </thinking> tags and output the final action within <action> </action> tags."
                    )
                elif use_belief_state_prompt:
                    all_states_batch[idx].append(f"current state: {final_obs}" + self.belief_state_suffix)
                else:
                    all_states_batch[idx].append(f"current state: {final_obs}" + "\n\nOutput the final action directly within <action> </action> tags.")

                # In decouple mode the conversation history is never used for generation
                # (each step uses a fresh per-step context via _build_fresh_step_context).
                # Skip the extension to avoid unbounded memory growth and history corruption.
                if not self.decouple_trajectory:
                    messages_batch[idx].extend([
                        {"role": "assistant", "content": all_actions_batch[idx][-1]},
                        {"role": "user", "content": all_states_batch[idx][-1]}
                    ])

                intermediate_reward = 0.0

                # Max 0.5 in both cases: direct = format only; belief_state = format + structure balanced
                if is_belief_state_prompt_prev:
                    if self.thinking_variant in ("symbolic_belief_state", "symbolic_belief_state_periodic"):
                        # structure_frac already encodes parse+key+dist in [0,1]; scale to 0.5
                        structure_frac = self._compute_symbolic_belief_state_structure_reward(output_text)
                        format_contrib = 0.25 if format_ok_prev else 0.0
                        structure_contrib = 0.25 * structure_frac
                        intermediate_reward = format_contrib + structure_contrib  # max 0.5
                    elif self.thinking_variant == "memory_belief_state":
                        has_bs = bool(re.search(r"<belief_state>(.*?)</belief_state>", output_text, re.DOTALL | re.IGNORECASE))
                        has_thinking = bool(re.search(r"<thinking>(.*?)</thinking>", output_text, re.DOTALL | re.IGNORECASE))
                        has_action = bool(re.search(r"<action>(.+?)</action>", output_text, re.DOTALL | re.IGNORECASE))
                        full_format = has_bs and has_thinking and has_action
                        uncertainty_frac = self._compute_nl_belief_state_uncertainty_reward(output_text)
                        format_contrib = 0.25 if full_format else 0.0
                        uncertainty_contrib = 0.25 * uncertainty_frac
                        intermediate_reward = format_contrib + uncertainty_contrib  # max 0.5
                    elif self.thinking_variant == "goal_memory_belief_state":
                        structure_frac = self._compute_nl_belief_state_uncertainty_reward(output_text)
                        format_contrib = 0.25 if format_ok_prev else 0.0
                        structure_contrib = 0.25 * structure_frac
                        intermediate_reward = format_contrib + structure_contrib  # max 0.5
                    elif self.thinking_variant == "goal_memory_history_summary":
                        intermediate_reward = 0.5 if format_ok_prev else 0.0
                    elif self.thinking_variant == "goal_memory_freeform_bdi":
                        structure_frac = self._compute_freeform_bdi_structure_reward(output_text)
                        uncertainty_frac = self._compute_freeform_bdi_uncertainty_reward(output_text)
                        format_contrib = 0.20 if format_ok_prev else 0.0      # max 0.20
                        structure_contrib = 0.15 * structure_frac              # max 0.15
                        uncertainty_contrib = 0.15 * uncertainty_frac          # max 0.15
                        intermediate_reward = format_contrib + structure_contrib + uncertainty_contrib  # max 0.50
                    else:
                        structure_frac = self._compute_belief_state_structure_reward(output_text)
                        format_contrib = 0.25 if format_ok_prev else 0.0
                        structure_contrib = 0.25 * structure_frac
                        intermediate_reward = format_contrib + structure_contrib  # max 0.5
                else:
                    intermediate_reward = 0.5 if format_ok_prev else 0.0  # direct: format only, max 0.5

                if self.use_intermediate_reward:
                    # interm_reward_batch[idx].append(reward - accumulated_reward_batch[idx])
                    # Extract observations from state history for log-probability of next observation
                    observations = []
                    if "current state:" in prompt_str_batch[idx]:
                        try:
                            o_0 = prompt_str_batch[idx].split("current state:")[1].split("\n\n")[0].strip()
                            observations.append(o_0)
                        except (IndexError, AttributeError):
                            pass
                    for state_str in all_states_batch[idx][1:-1]:
                        if "current state: " in state_str:
                            obs = state_str.split("current state: ")[1].split("\n\n")[0].strip()
                            observations.append(obs)
                    # Ensure len(observations) == len(actions) for zip(..., strict=True)
                    assert len(observations) == len(all_actions_batch[idx]), "Length of observations and actions must match"

                    interm_reward = self._compute_step_forecasting_reward(
                        goal=prompt_str_batch[idx],
                        observations=observations,
                        actions=[a for a in all_actions_batch[idx]],
                        target_observation=next_obs,
                    )

                    intermediate_reward += interm_reward
                else:
                    intermediate_reward += 0
                
                interm_reward_batch[idx].append(intermediate_reward)

                # Store raw model output for this step (for step-level DataProto in decouple mode)
                if self.decouple_trajectory:
                    step_responses_batch_text[idx].append(all_actions_batch[idx][-1])

                accumulated_reward_batch[idx] = reward

                if has_won:
                    active_batch_idx[idx] = False
                    # For ALFWorld: reward is 1.0 on win, 0.0 on timeout (both set done=True).
                    # For TextWorld: reward is 1.0 on win (done only fires on win).
                    final_reward_batch[idx] = 1.0
                else:
                    # In decouple mode the full conversation history (messages_batch[idx])
                    # is never used for generation — only the fresh per-step context is.
                    # Check the context that will actually be fed to the model next turn.
                    if self.decouple_trajectory:
                        check_messages = self._build_fresh_step_context(
                            idx, prompt_str_batch, all_belief_states_batch, all_states_batch
                        )
                    else:
                        check_messages = messages_batch[idx]
                    if self._exceeds_prompt_length(check_messages):
                        print(f"Instance {idx} exceeds prompt length")
                        active_batch_idx[idx] = False
            
        # Get total rewards for each instance
        max_total_rewards_batch = [
            instance_env_batch[i].get_total_rewards()
            for i in range(self.batch_size)
        ]

        # ── Collect background LLM reward results ─────────────────────────────
        # Reward HTTP calls were fired off during the loop; now wait for any
        # that haven't finished yet and assign the results.  Most should already
        # be done since they ran in parallel with subsequent rollout iterations.
        _is_validate = self.input_batch.meta_info.get("validate", False)
        if self._reward_futures and not _is_validate:
            print(
                f"[BELIEF_REWARD] collecting {len(self._reward_futures)} "
                f"background LLM reward results",
                flush=True,
            )
            for step_idx, future in self._reward_futures:
                try:
                    st_r, sc_r, div_r = future.result()
                    self.belief_state_training_steps[step_idx].state_tracking_r = st_r
                    self.belief_state_training_steps[step_idx].state_correctness_r = sc_r
                    self.belief_state_training_steps[step_idx].diversity_r = div_r
                except Exception as e:
                    logger.warning("[BELIEF_REWARD] failed for step %d: %s", step_idx, e)
        if self._reward_executor is not None:
            self._reward_executor.shutdown(wait=False)
            self._reward_executor = None
        # ─────────────────────────────────────────────────────────────────────

        belief_rollout_metrics = self._finalize_belief_state_training(final_reward_batch)
        belief_meta = (
            {"metrics": belief_rollout_metrics} if belief_rollout_metrics else {}
        )

        # Sync all TP ranks after belief PPO update.
        # Rank 0 (belief trainer) may take minutes; rank 1 (no trainer) exits
        # _finalize_belief_state_training immediately. Without this barrier,
        # rank 1 proceeds to fsdp_workers.py's reduce_timing() / trainer_mode()
        # NCCL collectives before rank 0 is ready, causing a 600s watchdog timeout.
        if self.belief_use_tp_barrier and torch.distributed.is_initialized():
            torch.distributed.barrier()

        if self.decouple_trajectory:
            # Expand rollout into per-step training instances. Each step becomes a
            # separate DataProto row with a fresh (prev_belief + curr_obs) prompt.
            result_tensor_batch, result_non_tensor_batch, step_to_traj_map = (
                self.convert_result_to_step_dataproto(
                    step_fresh_contexts_batch=step_fresh_contexts_batch,
                    step_responses_batch_text=step_responses_batch_text,
                    final_reward_batch=final_reward_batch,
                    interm_reward_batch=interm_reward_batch,
                    max_total_rewards_batch=max_total_rewards_batch,
                )
            )
            # Replicate scalar non-tensor fields from input_batch to match expanded batch size
            non_tensor_batch = {}
            for key, v in self.input_batch.non_tensor_batch.items():
                non_tensor_batch[key] = np.array(
                    [v[traj_idx] for traj_idx in step_to_traj_map], dtype=object
                )
            for key, v in result_non_tensor_batch.items():
                non_tensor_batch[key] = v
            total_steps = len(step_to_traj_map)
            tensor_batch = TensorDict(result_tensor_batch, batch_size=total_steps)
            return DataProto(
                batch=tensor_batch,
                non_tensor_batch=non_tensor_batch,
                meta_info=belief_meta,
            )
        else:
            result_tensor_batch, result_non_tensor_batch = self.convert_result_to_dataproto(
                messages_batch=messages_batch,
                final_reward_batch=final_reward_batch,
                interm_reward_batch=interm_reward_batch,
                max_total_rewards_batch=max_total_rewards_batch,
            )
            non_tensor_batch = self.input_batch.non_tensor_batch
            for k, v in result_non_tensor_batch.items():
                non_tensor_batch[k] = v
            tensor_batch = TensorDict(result_tensor_batch, batch_size=self.batch_size)
            return DataProto(
                batch=tensor_batch,
                non_tensor_batch=non_tensor_batch,
                meta_info=belief_meta,
            )


    def batch_generate(self, messages_batch: List[List[Dict]]) -> Tuple[List[str], List[bool]]:
        """
        Call vLLM generate in batches. 
        Given a batch of chat messages so far, returns a batch of the latest assistant message string, and the batch indices of invalid output (action missing sep token)
        Note: sep_token is removed from output.

        Args:
            messages_batch (List[List[Dict]]): a batch of chat messages so far
        Returns:
            output_str_batch (List[str]): a batch of generated assistant message strings
            valid_output_batch_idx (List[bool]): a batch of bool indicating if the output contains sep_token
        """
        _t0 = time.monotonic()
        _rank_s = ""
        try:
            if torch.distributed.is_initialized():
                _rank_s = f" dist_rank={torch.distributed.get_rank()}"
        except Exception:
            pass
        _mt = getattr(self.sampling_params, "max_tokens", None)
        print(
            f"[POLICY_GEN] main policy vLLM.generate start n_prompts={len(messages_batch)} "
            f"max_new_tokens={_mt}{_rank_s}",
            flush=True,
        )
        # Apply chat template to batch of messages
        tokens_prompt_batch = []
        _prompt_lens: List[int] = []
        for messages in messages_batch:
            input_tokens = self.tokenizer.apply_chat_template(
                messages, tokenize=True, add_generation_prompt=True, return_tensor="pt"
            )
            if hasattr(input_tokens, "shape"):
                _prompt_lens.append(int(input_tokens.shape[-1]))
            else:
                _prompt_lens.append(len(input_tokens))
            tokens_prompt_batch.append(TokensPrompt(prompt_token_ids=input_tokens))

        outputs = self.inference_engine.generate(
            prompts=tokens_prompt_batch,
            sampling_params=self.sampling_params
        )
        _dt = time.monotonic() - _t0
        _pmn = min(_prompt_lens) if _prompt_lens else 0
        _pmx = max(_prompt_lens) if _prompt_lens else 0
        print(
            f"[POLICY_GEN] main policy vLLM.generate done in {_dt:.2f}s "
            f"n_prompts={len(messages_batch)} prompt_tok min={_pmn} max={_pmx}{_rank_s}",
            flush=True,
        )

        output_ids_batch = [output.outputs[0].token_ids for output in outputs]
        # Use finish_reason instead of token-ID matching: models with multiple EOS tokens
        # (e.g. Phi-4-mini has both <|end|> and <|endoftext|>) may stop on a token that
        # differs from tokenizer.eos_token_id, causing _has_sep_token to always return False.
        valid_action_batch_idx = [output.outputs[0].finish_reason == "stop" for output in outputs]

        output_str_batch = []
        for i, (output_ids, has_sep) in enumerate(zip(output_ids_batch, valid_action_batch_idx)):
            if has_sep:
                output_str = self.tokenizer.decode(output_ids, skip_special_tokens=True)
                output_str_batch.append(output_str)
            else:
                output_str_batch.append("")

        return output_str_batch, valid_action_batch_idx

    def batch_generate_with_logprobs(
        self, messages_batch: List[List[Dict]]
    ) -> Tuple[List[str], List[bool], List[Optional[List[Optional[Dict[int, Any]]]]], List[List[int]]]:
        """
        Same as batch_generate but returns logprobs and token_ids per output for confidence scoring.
        logprobs_batch[i][j] = dict mapping token_id -> Logprob at position j for output i.
        """
        _t0 = time.monotonic()
        _rank_s = ""
        try:
            if torch.distributed.is_initialized():
                _rank_s = f" dist_rank={torch.distributed.get_rank()}"
        except Exception:
            pass
        _mt = getattr(self.sampling_params, "max_tokens", None)
        print(
            f"[POLICY_GEN] main policy vLLM.generate (with_logprobs) start "
            f"n_prompts={len(messages_batch)} max_new_tokens={_mt}{_rank_s}",
            flush=True,
        )
        tokens_prompt_batch = []
        _prompt_lens: List[int] = []
        for messages in messages_batch:
            input_tokens = self.tokenizer.apply_chat_template(
                messages, tokenize=True, add_generation_prompt=True, return_tensor="pt"
            )
            if hasattr(input_tokens, "shape"):
                _prompt_lens.append(int(input_tokens.shape[-1]))
            else:
                _prompt_lens.append(len(input_tokens))
            tokens_prompt_batch.append(TokensPrompt(prompt_token_ids=input_tokens))

        with self.update_sampling_params(logprobs=1):
            outputs = self.inference_engine.generate(
                prompts=tokens_prompt_batch,
                sampling_params=self.sampling_params,
            )
        _dt = time.monotonic() - _t0
        _pmn = min(_prompt_lens) if _prompt_lens else 0
        _pmx = max(_prompt_lens) if _prompt_lens else 0
        print(
            f"[POLICY_GEN] main policy vLLM.generate (with_logprobs) done in {_dt:.2f}s "
            f"n_prompts={len(messages_batch)} prompt_tok min={_pmn} max={_pmx}{_rank_s}",
            flush=True,
        )

        output_ids_batch = [list(output.outputs[0].token_ids) for output in outputs]
        valid_action_batch_idx = [output.outputs[0].finish_reason == "stop" for output in outputs]

        output_str_batch = []
        logprobs_batch = []
        for i, (output_ids, has_sep) in enumerate(zip(output_ids_batch, valid_action_batch_idx)):
            if has_sep:
                output_str = self.tokenizer.decode(output_ids, skip_special_tokens=True)
                output_str_batch.append(output_str)
            else:
                output_str_batch.append("")
            raw_logprobs = getattr(outputs[i].outputs[0], "logprobs", None)
            if raw_logprobs is not None:
                logprobs_batch.append(raw_logprobs)
            else:
                logprobs_batch.append(None)

        return output_str_batch, valid_action_batch_idx, logprobs_batch, output_ids_batch

    def convert_result_to_dataproto(self, messages_batch: List[List[Dict]], final_reward_batch: List[float], interm_reward_batch: List[List[float]], max_total_rewards_batch: List[float]) -> Tuple[Dict, Dict]:
        """
        Convert the rollout result to DataProto format.

        Args:
            messages_batch (List[List[Dict]]): a batch of chat messages after rollout
            final_reward_batch (List[float]): final score (0.0/1.0) for each instance
            interm_reward_batch (List[List[float]]): intermediate reward per action such as [0, 0.2, 0.1, 0, 0.5, ...] for each instance
            max_total_rewards_batch (List[float]): maximum total rewards for each instance

        Returns:
            Tensor batch:
            - prompts: [bsz, prompt_length], prompt token ids from dataset.
            - responses: [bsz, response_length], output token ids including both env and agent responses
            - response_mask: [bsz, response_length], 1 for agent tokens, 0 for env tokens.
            - input_ids: [bsz, prompt_length + response_length], whole sequence token ids, including prompt tokens
              and response tokens.
            - attention_mask: [bsz, prompt_length + response_length], 0 for padding tokens, 1 for other tokens.
            - position_ids: [bsz, prompt_length + response_length], incremental position ids.

            Non-tensor batch:
            - sep_token_positions: 1D object ndarray, int indices of sep token ids in responses
            - final_rewards: 1D float ndarray, float values of 1.0/0.0 indicating game winning status
            - interm_rewards: 1D object ndarray, list of float values of intermediate rewards per action
            - max_total_rewards: 1D float ndarray, float values of maximum total rewards for each instance
            - raw_response_text: 1D object ndarray, action only sequence, for eval purpose
        """
        # prompt: left pad + response: right pad
        # attention_mask: [0,0,0,0,1,1,1,1, | 1,1,1,0,0,0,0,0]
        # position_ids:   [0,0,0,0,0,1,2,3, | 4,5,6,7,8,9,10,11]
        prompt_ids = torch.full((self.batch_size, self.max_prompt_len), self.pad_token_id, dtype=torch.long, device=self.device)
        response_ids = torch.full((self.batch_size, self.max_response_len), self.pad_token_id, dtype=torch.long, device=self.device)
        total_len = self.max_prompt_len + self.max_response_len
        input_ids = torch.full((self.batch_size, total_len), self.pad_token_id, dtype=torch.long, device=self.device)
        loss_mask = torch.zeros((self.batch_size, self.max_response_len), dtype=torch.long, device=self.device)
        attention_mask = torch.zeros((self.batch_size, total_len), dtype=torch.long, device=self.device)
        position_ids = torch.zeros((self.batch_size, total_len), dtype=torch.long, device=self.device)

        sep_token_positions = [[] for _ in range(self.batch_size)]
        final_rewards = final_reward_batch
        interm_rewards = interm_reward_batch
        max_total_rewards = max_total_rewards_batch
        raw_response_text = ["" for _ in range(self.batch_size)]

        for i in range(self.batch_size):
            assert len(messages_batch[i]) % 2 == 1 # Should be "user...assistant...user......user"
            # Construct prompt_ids from the first user message
            prompt_tokens = self.tokenizer.apply_chat_template(
                messages_batch[i][:1], tokenize=True, add_generation_prompt=True
            )
            # Truncate prompt ids
            if len(prompt_tokens) > self.max_prompt_len:
                prompt_tokens = prompt_tokens[:self.max_prompt_len]
            # Add left padding to prompt ids
            prompt_ids[i, (self.max_prompt_len - len(prompt_tokens)):] = torch.tensor(prompt_tokens) 

            # Construct response_ids from subsequent user messages throughout the interaction
            response_tokens = []
            # index positions of sep tokens in response_ids  
            sep_tokens: List[int] = []  
            response_loss_mask = []
            response_text = ""
            for k in range(len(messages_batch[i]) // 2):
                # Append action tokens
                turn_action_tokens = self.tokenizer.encode(messages_batch[i][2*k+1]["content"], add_special_tokens=False)
                response_tokens.extend(turn_action_tokens)
                # Append sep token index and sep token id
                sep_tokens.append(len(response_tokens))
                response_tokens.append(self.sep_token_id)
                # Create response loss mask, 1 for agent tokens, 0 for env tokens
                # Response loss mask should include sep token
                response_loss_mask.extend([1] * (len(turn_action_tokens) + 1)) 
                response_text += messages_batch[i][2*k+1]["content"] + self.sep_token
                # Append env responses (user messages), excluded from loss
                turn_env_text = self._truncate_system_template(
                    self.tokenizer.apply_chat_template(
                        [messages_batch[i][2*k+2]], tokenize=False, add_generation_prompt=True
                    )
                )
                # Append env tokens
                turn_env_tokens = self.tokenizer.encode(turn_env_text, add_special_tokens=True)
                response_tokens.extend(turn_env_tokens)
                # Create response loss mask, 1 for agent tokens, 0 for env tokens
                response_loss_mask.extend([0] * len(turn_env_tokens))

            # Truncate response ids
            if len(response_tokens) > self.max_response_len:
                response_tokens = response_tokens[:self.max_response_len]
                # Truncate response_loss_mask in parallel
                response_loss_mask = response_loss_mask[:self.max_response_len] 
            # Add right padding to response ids
            response_ids[i, :len(response_tokens)] = torch.tensor(response_tokens)

            # Construct input_ids from prompt_ids and response_ids
            input_ids[i, :self.max_prompt_len] = prompt_ids[i]
            input_ids[i, self.max_prompt_len:total_len] = response_ids[i]

            # Truncate loss mask
            assert len(response_loss_mask) == len(response_tokens)
            if len(response_loss_mask) > self.max_response_len:
                response_loss_mask = response_loss_mask[:self.max_response_len]
            loss_mask[i, :len(response_loss_mask)] = torch.tensor(response_loss_mask)

            # Construct attention mask and position ids
            attention_mask[i, (self.max_prompt_len - len(prompt_ids)):self.max_prompt_len] = 1  # Prompt actual tokens
            attention_mask[i, self.max_prompt_len:(self.max_prompt_len + len(response_tokens))] = 1  # Response actual tokens
            
            position_ids[i, (self.max_prompt_len - len(prompt_ids)):self.max_prompt_len] = torch.arange(len(prompt_ids))
            response_positions = torch.arange(len(prompt_ids), len(prompt_ids) + self.max_response_len)
            position_ids[i, self.max_prompt_len:] = response_positions

            # Add to non tensor batch info list
            sep_token_positions[i] = sep_tokens
            raw_response_text[i] = response_text

        # Formatting result
        tensor_batch = {
            "prompts": prompt_ids,
            "responses": response_ids,
            "response_mask": loss_mask, # this is the loss mask applied to any policy-related loss and updates
            "input_ids": input_ids,  # here input_ids become the whole sentences
            "attention_mask": attention_mask,
            "position_ids": position_ids,
        }

        non_tensor_batch = {
            "sep_token_positions": self._create_consistent_object_array(sep_token_positions),
            "final_rewards": np.array(final_rewards),
            "interm_rewards": self._create_consistent_object_array(interm_rewards),
            "max_total_rewards": np.array(max_total_rewards),
            "raw_response_text": self._create_consistent_object_array(raw_response_text)
        }
        
        return tensor_batch, non_tensor_batch

    def convert_result_to_step_dataproto(
        self,
        step_fresh_contexts_batch: List[List[List[Dict]]],
        step_responses_batch_text: List[List[str]],
        final_reward_batch: List[float],
        interm_reward_batch: List[List[float]],
        max_total_rewards_batch: List[float],
    ) -> Tuple[Dict, Dict, List[int]]:
        """
        Convert step-level rollout results to DataProto format for decoupled trajectory training.

        Instead of one DataProto row per full trajectory, each valid step becomes its own row:
          - prompt  : fresh context (game description + previous belief state + current obs)
          - response: raw model output for this step (belief_state + action) + SEP token
          - reward  : intermediate reward + final game reward (only on the last step)

        This allows the policy to learn action prediction conditioned solely on the compressed
        belief state and current observation rather than on the accumulated chat history.

        Args:
            step_fresh_contexts_batch: step_fresh_contexts_batch[i][k] = 1-message list used at
                step k for trajectory i (the prompt after suffix substitution).
            step_responses_batch_text: step_responses_batch_text[i][k] = raw model output string
                at step k for trajectory i.
            final_reward_batch: final game outcome (0.0 / 1.0) per trajectory.
            interm_reward_batch: intermediate reward per step per trajectory.
            max_total_rewards_batch: maximum possible reward per trajectory.

        Returns:
            (tensor_batch, non_tensor_batch, step_to_traj_map) where step_to_traj_map[row]
            gives the source trajectory index so callers can expand non-tensor fields.
        """
        # --- Flatten per-trajectory steps into a single list -------------------------
        step_to_traj_map: List[int] = []
        all_contexts:        List[List[Dict]] = []
        all_responses:       List[str]        = []
        all_final_rewards:   List[float]      = []
        all_interm_rewards:  List[List[float]] = []
        all_max_total:       List[float]      = []

        for i in range(self.batch_size):
            n_steps = len(step_responses_batch_text[i])
            T = n_steps - 1  # index of last step (0-based)
            for k in range(n_steps):
                step_to_traj_map.append(i)
                all_contexts.append(step_fresh_contexts_batch[i][k])
                all_responses.append(step_responses_batch_text[i][k])
                step_interm = interm_reward_batch[i][k] if k < len(interm_reward_batch[i]) else 0.0

                if k == T:
                    # Last step: full correctness reward lives in final_rewards (1.0 or 0.0).
                    # Format reward alone in interm_rewards.
                    # The last step's total (format[T] + final_reward) is always ≥ 1.0 on a win,
                    # while non-last totals are capped by the discounted signal (< 1.0) + format.
                    all_final_rewards.append(final_reward_batch[i])
                    all_interm_rewards.append([step_interm])
                else:
                    # Non-last steps: discounted correctness signal folded into interm_rewards
                    # so that final_rewards stays 0.0.  This guarantees final_rewards[T] > 0 =
                    # final_rewards[k<T] for any winning trajectory, making the last step's reward
                    # always the dominant one.
                    # γ^(T-k) × final_reward  (=0 on a loss, so non-last interm stays format-only)
                    discounted_signal = (self.discount_gamma ** (T - k)) * final_reward_batch[i]
                    all_final_rewards.append(0.0)
                    all_interm_rewards.append([step_interm + discounted_signal])

                all_max_total.append(max_total_rewards_batch[i])

        total_steps = len(all_contexts)

        # Handle edge case: no valid steps produced
        if total_steps == 0:
            empty_t = {
                "prompts":       torch.zeros((0, self.max_prompt_len),  dtype=torch.long, device=self.device),
                "responses":     torch.zeros((0, self.max_response_len), dtype=torch.long, device=self.device),
                "response_mask": torch.zeros((0, self.max_response_len), dtype=torch.long, device=self.device),
                "input_ids":     torch.zeros((0, self.max_prompt_len + self.max_response_len), dtype=torch.long, device=self.device),
                "attention_mask":torch.zeros((0, self.max_prompt_len + self.max_response_len), dtype=torch.long, device=self.device),
                "position_ids":  torch.zeros((0, self.max_prompt_len + self.max_response_len), dtype=torch.long, device=self.device),
            }
            empty_nt = {
                "sep_token_positions": self._create_consistent_object_array([]),
                "final_rewards":       np.array([]),
                "interm_rewards":      self._create_consistent_object_array([]),
                "max_total_rewards":   np.array([]),
                "raw_response_text":   self._create_consistent_object_array([]),
            }
            return empty_t, empty_nt, []

        # --- Allocate tensors --------------------------------------------------------
        total_len = self.max_prompt_len + self.max_response_len
        prompt_ids    = torch.full((total_steps, self.max_prompt_len),  self.pad_token_id, dtype=torch.long, device=self.device)
        response_ids  = torch.full((total_steps, self.max_response_len), self.pad_token_id, dtype=torch.long, device=self.device)
        input_ids     = torch.full((total_steps, total_len),            self.pad_token_id, dtype=torch.long, device=self.device)
        loss_mask     = torch.zeros((total_steps, self.max_response_len), dtype=torch.long, device=self.device)
        attention_mask = torch.zeros((total_steps, total_len),           dtype=torch.long, device=self.device)
        position_ids  = torch.zeros((total_steps, total_len),            dtype=torch.long, device=self.device)

        sep_token_positions = [[] for _ in range(total_steps)]
        raw_response_text   = ["" for _ in range(total_steps)]

        # --- Fill tensors row-by-row -------------------------------------------------
        for row in range(total_steps):
            ctx       = all_contexts[row]   # list with 1 user message dict
            resp_text = all_responses[row]

            # Tokenise fresh context as the prompt (left-padded)
            prompt_tokens = self.tokenizer.apply_chat_template(
                ctx, tokenize=True, add_generation_prompt=True
            )
            if len(prompt_tokens) > self.max_prompt_len:
                prompt_tokens = prompt_tokens[:self.max_prompt_len]
            n_prompt = len(prompt_tokens)
            prompt_ids[row, (self.max_prompt_len - n_prompt):] = torch.tensor(
                prompt_tokens, dtype=torch.long
            )

            # Tokenise response: model output + SEP token (right-padded)
            resp_tokens = self.tokenizer.encode(resp_text, add_special_tokens=False)
            resp_tokens = resp_tokens + [self.sep_token_id]
            if len(resp_tokens) > self.max_response_len:
                resp_tokens = resp_tokens[:self.max_response_len]
            n_resp = len(resp_tokens)
            response_ids[row, :n_resp] = torch.tensor(resp_tokens, dtype=torch.long)
            loss_mask[row, :n_resp]    = 1  # whole response is agent output

            # Construct input_ids
            input_ids[row, :self.max_prompt_len]          = prompt_ids[row]
            input_ids[row, self.max_prompt_len:total_len] = response_ids[row]

            # Attention mask: prompt non-pad tokens + response non-pad tokens
            attention_mask[row, (self.max_prompt_len - n_prompt):self.max_prompt_len] = 1
            attention_mask[row, self.max_prompt_len:(self.max_prompt_len + n_resp)]   = 1

            # Position ids: prompt tokens followed by response tokens
            position_ids[row, (self.max_prompt_len - n_prompt):self.max_prompt_len] = torch.arange(n_prompt)
            response_positions = torch.arange(n_prompt, n_prompt + self.max_response_len)
            position_ids[row, self.max_prompt_len:] = response_positions

            # SEP token sits at the last position of the (non-padded) response
            sep_token_positions[row] = [n_resp - 1]
            raw_response_text[row]   = resp_text + self.sep_token

        # --- Package results ---------------------------------------------------------
        tensor_batch = {
            "prompts":       prompt_ids,
            "responses":     response_ids,
            "response_mask": loss_mask,
            "input_ids":     input_ids,
            "attention_mask": attention_mask,
            "position_ids":  position_ids,
        }
        non_tensor_batch = {
            "sep_token_positions": self._create_consistent_object_array(sep_token_positions),
            "final_rewards":       np.array(all_final_rewards),
            "interm_rewards":      self._create_consistent_object_array(all_interm_rewards),
            "max_total_rewards":   np.array(all_max_total),
            "raw_response_text":   self._create_consistent_object_array(raw_response_text),
        }
        return tensor_batch, non_tensor_batch, step_to_traj_map
