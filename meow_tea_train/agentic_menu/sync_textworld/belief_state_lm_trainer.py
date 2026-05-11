# Copyright 2025 Anonymous Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
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

"""
BeliefStateLMTrainer — trains a separate belief-state language model jointly
with the RL policy.

Architecture
------------
The belief-state model is a *separate* LM from the policy model.  During each
rollout batch it:
  1. Generates belief states given (goal, prev_belief_state, current_obs).
     Inference uses **vLLM** when ``belief_vllm_engine`` is set (fast batched
     generation). With policy TP>1, use a **subprocess** belief engine
     (``BeliefVLLMSubprocessClient``) so each process has its own vLLM parallel
     state. Otherwise HuggingFace sampling is used when vLLM is disabled.
  2. After the batch completes, receives a reward signal and undergoes gradient
     updates via the same registered VERL policy loss as the actor
     (HF CausalLM; default ``vanilla`` PPO).  The belief vLLM engine is then
     reloaded from the updated HF weights so the next rollout stays consistent.

Rewards
-------
  r_total = alpha * r_state_tracking + (1 - alpha) * r_discounted_task

  r_state_tracking : F1(belief, obs), optionally mixed with F1(belief, prev+obs)
                     when training uses a non-zero ``transition_weight`` and a
                     prior belief — rewards sequential state tracking.
  r_discounted_task: gamma^(T-k) * final_task_reward, propagated from the
                     policy's terminal correctness signal.

Training
--------
Rollouts sample tokens (stochastic policy) and store ``old_log_probs``.  Advantages
are sequence-level normalised returns broadcast to every response token.  The
update uses dual-clip PPO with ``clip_ratio`` / ``clip_ratio_c`` matching the
usual VERL actor settings.
"""

from __future__ import annotations

import gc
import logging
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import torch
import torch.nn.functional as F
from omegaconf import OmegaConf

import torch.nn as nn
from verl.trainer.ppo.core_algos import (
    get_policy_loss_fn,
    compute_gae_advantage_return,
    compute_value_loss,
    kl_penalty,
    agg_loss,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# State-tracking reward helper (module-level, reusable)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# LLM-based belief-state reward helpers
# ---------------------------------------------------------------------------

# Prompt for state-tracking reward: evaluates how well the new belief state
# incorporates information from the latest observation while correctly updating
# from the prior belief state.
_STATE_TRACKING_REWARD_PROMPT = """\
You are evaluating a belief-state update in a text-based game.

=== PREVIOUS BELIEF STATE ===
{prev_belief}

=== NEW OBSERVATION ===
{new_obs}

=== NEW BELIEF STATE ===
{new_belief}

STEP 1 — Identify (brief, one line each):
  NEW facts: list each distinct fact the observation reveals (e.g. "player moved to kitchen", "door is open")
  MISSING:   which of those NEW facts are absent or wrong in the new belief state
  STALE:     which prior beliefs does the observation contradict that were left unchanged

STEP 2 — Count (integers):
  N_new     = number of NEW facts correctly captured
  N_missing = number of NEW facts missing or wrong
  N_stale   = number of stale/contradicted priors left unchanged
  N_total   = total claims in the new belief state

STEP 3 — Compute:
  If N_total = 0: score = 0.0
  Else:
    coverage  = N_new / max(1, N_new + N_missing)
    staleness = N_stale / N_total
    score     = coverage * (1.0 - staleness)
    Clamp to [0.00, 1.00].

End with exactly:
<score>X.XX</score>
where X.XX is a decimal in [0.00, 1.00].
"""

# Prompt step 1 for state-correctness reward: extract verifiable claims.
_STATE_CORRECTNESS_EXTRACT_PROMPT = """\
You are analysing a belief state from a text-based game.

=== BELIEF STATE ===
{belief_state}

TASK — Extract every specific factual claim from the belief state.
List each claim on its own line using this exact format:
  CLAIM: <subject> | <predicate> | <certainty-label>

Examples:
  CLAIM: player location | in the kitchen | certain
  CLAIM: key | on the table in the library | probable
  CLAIM: east exit from kitchen | leads to hallway | almost certain
  CLAIM: chest | open | possible

List ALL claims now (one per line):
"""

# Prompt step 2 for state-correctness reward: verify claims against ground truth.
_STATE_CORRECTNESS_VERIFY_PROMPT = """\
You are verifying factual claims from a belief state against the TRUE game world state.

=== TRUE GAME WORLD STATE (ground truth) ===
{raw_state}

=== CLAIMS TO VERIFY ===
{claims}

INSTRUCTIONS
------------
For each claim decide:
  CORRECT          — The underlying fact is true AND the certainty label is appropriate.
  INCORRECT        — The underlying fact is false (label does not matter).
  PARTIALLY_CORRECT — The fact is true but the certainty label is badly miscalibrated \
(e.g., marked "certain" for something only "probable" is supported by evidence, or "unknown" \
for something directly observable in the true state).
  UNVERIFIABLE     — The ground truth does not contain enough information to confirm or \
deny the claim.

Count:
  N_verifiable     = CORRECT + INCORRECT + PARTIALLY_CORRECT
  N_fully_correct  = CORRECT
  N_partial        = PARTIALLY_CORRECT

score = (N_fully_correct + 0.5 * N_partial) / N_verifiable
(treat N_verifiable == 0 as score = 0.0)

Provide a brief per-claim verdict, then end with exactly:
<score>X.XX</score>
where X.XX is a decimal in [0.00, 1.00].
"""


def _call_reward_model(
    prompt: str,
    reward_model_url: str,
    reward_model_name: str,
    max_tokens: int = 512,
) -> str:
    """Single blocking call to an OpenAI-compatible reward model (vLLM)."""
    from openai import OpenAI
    client = OpenAI(base_url=f"{reward_model_url}/v1", api_key="EMPTY")
    response = client.chat.completions.create(
        model=reward_model_name,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.0,
    )
    return response.choices[0].message.content or ""


def _parse_score_tag(text: str, default: float = 0.0) -> float:
    """Extract the float from the last <score>X.XX</score> tag in *text*."""
    matches = re.findall(r"<score>\s*([0-9]*\.?[0-9]+)\s*</score>", text, re.IGNORECASE)
    if matches:
        try:
            return min(1.0, max(0.0, float(matches[-1])))
        except ValueError:
            pass
    return default


def compute_lm_state_tracking_reward(
    prev_belief: str,
    new_obs: str,
    new_belief: str,
    reward_model_url: str,
    reward_model_name: str,
) -> float:
    """LLM-based state-tracking reward (single call).

    Evaluates how well *new_belief* tracks state changes from *prev_belief*
    given *new_obs*.  Returns a score in [0, 1].
    """
    if not new_belief.strip():
        return 0.0
    try:
        prompt = _STATE_TRACKING_REWARD_PROMPT.format(
            prev_belief=prev_belief.strip() or "(no previous belief state)",
            new_obs=new_obs.strip() or "(no observation)",
            new_belief=new_belief.strip(),
        )
        # State-tracking output: brief STEP 1 analysis + counts + <score> tag.
        response = _call_reward_model(
            prompt, reward_model_url, reward_model_name, max_tokens=512
        )
        return _parse_score_tag(response)
    except Exception as e:
        logger.warning("[BeliefReward] state_tracking LLM call failed: %s", e)
        return 0.0


def compute_lm_state_correctness_reward(
    belief_state: str,
    raw_env_state: str,
    reward_model_url: str,
    reward_model_name: str,
) -> float:
    """LLM-based state-correctness reward (two-step call).

    Step 1: extract all verifiable claims from *belief_state*.
    Step 2: verify each claim against *raw_env_state* (ground truth).
    Returns a score in [0, 1].
    """
    if not belief_state.strip() or not raw_env_state.strip():
        return 0.0
    try:
        # Step 1 — extract claims.
        # Output is ~25 CLAIM lines at ~12 tokens each ≈ 300 tokens; 384 is enough.
        step1_prompt = _STATE_CORRECTNESS_EXTRACT_PROMPT.format(
            belief_state=belief_state.strip(),
        )
        claims_text = _call_reward_model(
            step1_prompt, reward_model_url, reward_model_name, max_tokens=1024
        )
        if not claims_text.strip():
            return 0.0
        # Step 2 — verify against ground truth.
        # Output is ~25 one-line verdicts + <score> tag ≈ 350 tokens; 512 is enough.
        step2_prompt = _STATE_CORRECTNESS_VERIFY_PROMPT.format(
            raw_state=raw_env_state.strip(),
            claims=claims_text.strip(),
        )
        response = _call_reward_model(
            step2_prompt, reward_model_url, reward_model_name, max_tokens=1024
        )
        return _parse_score_tag(response)
    except Exception as e:
        logger.warning("[BeliefReward] state_correctness LLM call failed: %s", e)
        return 0.0


def batch_compute_belief_rewards(
    items: list,  # list of (prev_belief, new_obs, new_belief, raw_env_state)
    reward_model_url: str,
    reward_model_name: str,
    max_workers: int = 50,
) -> list:  # list of (state_tracking_r, state_correctness_r, diversity_r)
    """Concurrently compute all belief-state rewards for a batch of steps.

    Parameters
    ----------
    items : list of 4-tuples (prev_belief, new_obs, new_belief, raw_env_state)
    reward_model_url : str
    reward_model_name : str
    max_workers : int
        Maximum number of concurrent HTTP threads (for the two LLM calls).

    Returns
    -------
    list of (state_tracking_r: float, state_correctness_r: float, diversity_r: float)
    in the same order as *items*.  diversity_r is computed rule-based (no LLM call).
    """
    from concurrent.futures import ThreadPoolExecutor

    n = len(items)
    if n == 0:
        return []

    def _compute_one(args):
        prev_bs, new_obs, new_bs, raw_state = args
        st_r = compute_lm_state_tracking_reward(
            prev_bs, new_obs, new_bs, reward_model_url, reward_model_name
        )
        sc_r = compute_lm_state_correctness_reward(
            new_bs, raw_state, reward_model_url, reward_model_name
        )
        div_r = compute_diversity_reward(new_bs)
        return st_r, sc_r, div_r

    with ThreadPoolExecutor(max_workers=min(n * 2, max_workers)) as executor:
        results = list(executor.map(_compute_one, items))
    return results


def compute_single_belief_rewards(
    prev_belief: str,
    new_obs: str,
    new_belief: str,
    raw_env_state: str,
    reward_model_url: str,
    reward_model_name: str,
) -> Tuple[float, float, float]:
    """Compute belief-state rewards for a single step.

    Designed to be submitted to a ``ThreadPoolExecutor`` so the HTTP
    round-trips run in the background while the rollout loop continues.
    The two LLM calls (state tracking and state correctness) run
    concurrently via a small inner thread pool.

    Returns (state_tracking_r, state_correctness_r, diversity_r).
    """
    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=2) as pool:
        fut_st = pool.submit(
            compute_lm_state_tracking_reward,
            prev_belief, new_obs, new_belief, reward_model_url, reward_model_name,
        )
        fut_sc = pool.submit(
            compute_lm_state_correctness_reward,
            new_belief, raw_env_state, reward_model_url, reward_model_name,
        )
        st_r = fut_st.result()
        sc_r = fut_sc.result()
    div_r = compute_diversity_reward(new_belief)
    return st_r, sc_r, div_r


# ---------------------------------------------------------------------------
# Format-compliance reward (rule-based, no LLM call)
# ---------------------------------------------------------------------------
# Ordered from most specific to least so substring matching is unambiguous.
# "ruled out" must come before "certain" to avoid partial-match errors.
# "unknown" is intentionally excluded — the belief prompt forbids it.
_CERTAINTY_KEYWORDS_ORDERED = [
    "almost certain", "ruled out", "confirmed", "certain", "probable",
    "possible", "unlikely", "doubtful",
]
_CERTAINTY_KEYWORDS = frozenset(_CERTAINTY_KEYWORDS_ORDERED)

# Canonical label groups (confirmed == certain).
_CERTAINTY_CANONICAL = {
    "almost certain": "almost_certain",
    "ruled out":      "ruled_out",
    "confirmed":      "certain",
    "certain":        "certain",
    "probable":       "probable",
    "possible":       "possible",
    "unlikely":       "unlikely",
    "doubtful":       "doubtful",
}
# All distinct canonical certainty levels (used to normalise diversity entropy).
_CERTAINTY_CANONICAL_VALUES = frozenset(_CERTAINTY_CANONICAL.values())  # 7 levels

# Minimum bullets for full count_ratio credit.
_MIN_BULLETS = 8

# Maximum bullets before a length penalty kicks in.
_MAX_BULLETS = 20

# Minimum distinct certainty levels required before diversity_score is capped at 1.
# 3 out of 7 levels is the threshold — easy to exceed with meaningful content.
_MIN_DISTINCT_LEVELS = 3


def compute_format_compliance_score(belief_state: str) -> float:
    """Fast, rule-based format compliance gate. Returns a score in [0, 1].

    Four multiplicative criteria — all must be satisfied for a high gate score:

      1. count_ratio     — fraction of _MIN_BULLETS present (capped at 1.0).
                           Plain prose with zero "- " bullets scores 0, killing all reward.
      2. certainty_ratio — fraction of bullets that contain any certainty keyword.
      3. dedup_ratio     — unique bullets / total bullets.
                           Collapses toward 0 when the model repeats the same fact.
      4. length_penalty  — 1.0 if len(bullets) <= _MAX_BULLETS, else _MAX_BULLETS / len(bullets).
                           Discourages padding with excessive bullets beyond the cap.

    Applied as a *multiplier* on total_reward so that a belief state that drops the
    required bullet + certainty-label format cannot reward-hack its way to a high score.
    Uncertainty diversity is measured separately in compute_diversity_reward().
    """
    if not belief_state.strip():
        return 0.0

    bullets = [
        line.strip()
        for line in belief_state.splitlines()
        if line.strip().startswith("-")
    ]
    if not bullets:
        return 0.0

    count_ratio = min(1.0, len(bullets) / _MIN_BULLETS)

    matched_labels: list[str] = []
    for b in bullets:
        b_lower = b.lower()
        for kw in _CERTAINTY_KEYWORDS_ORDERED:
            if kw in b_lower:
                matched_labels.append(_CERTAINTY_CANONICAL[kw])
                break

    certainty_ratio = len(matched_labels) / len(bullets)

    dedup_ratio = len({b.lower() for b in bullets}) / len(bullets)

    length_penalty = 1.0 if len(bullets) <= _MAX_BULLETS else _MAX_BULLETS / len(bullets)

    return count_ratio * certainty_ratio * dedup_ratio * length_penalty


def compute_diversity_reward(belief_state: str) -> float:
    """Shannon-entropy diversity reward over the certainty-marker distribution.

    Returns a score in [0, 1]:
      0.0 — all bullets carry the same certainty label, or no labelled bullets.
      1.0 — markers are spread as uniformly as possible across all 7 canonical levels.

    Entropy is normalised by log(min(n_labelled_bullets, n_canonical_levels)) so
    that a belief state with fewer bullets than the number of levels is not unfairly
    penalised for the theoretical maximum it cannot reach.
    """
    import math
    from collections import Counter

    bullets = [
        line.strip()
        for line in belief_state.splitlines()
        if line.strip().startswith("-")
    ]
    if not bullets:
        return 0.0

    counts: Counter = Counter()
    for b in bullets:
        b_lower = b.lower()
        for kw in _CERTAINTY_KEYWORDS_ORDERED:
            if kw in b_lower:
                counts[_CERTAINTY_CANONICAL[kw]] += 1
                break

    if not counts:
        return 0.0

    total = sum(counts.values())
    probs = [c / total for c in counts.values()]
    entropy = -sum(p * math.log(p) for p in probs)

    # Normalise: theoretical max is log(k) where k = min(labelled bullets, distinct levels).
    n_possible = min(total, len(_CERTAINTY_CANONICAL_VALUES))
    max_entropy = math.log(n_possible) if n_possible > 1 else 1.0

    return min(1.0, entropy / max_entropy)


# ---------------------------------------------------------------------------
# Token-level F1 reward helper (kept for reference / fallback)
# ---------------------------------------------------------------------------

_STOPWORDS = frozenset({
    "the", "a", "an", "is", "are", "was", "were", "you", "i", "it",
    "to", "and", "or", "of", "in", "on", "at", "for", "with", "this",
    "that", "there", "be", "have", "do", "not", "as", "by", "from",
    "its", "it's", "no", "so", "but", "if", "my", "your", "has", "had",
})


def _token_set_f1(belief_state: str, reference: str) -> float:
    """Token-level F1 between belief_state and reference (stopwords removed)."""
    if not belief_state.strip() or not reference.strip():
        return 0.0
    bs_toks = {t for t in belief_state.lower().split()
               if t not in _STOPWORDS and len(t) > 2}
    ref_toks = {t for t in reference.lower().split()
                if t not in _STOPWORDS and len(t) > 2}
    if not bs_toks or not ref_toks:
        return 0.0
    common = bs_toks & ref_toks
    precision = len(common) / len(bs_toks)
    recall = len(common) / len(ref_toks)
    if precision + recall == 0:
        return 0.0
    return 2.0 * precision * recall / (precision + recall)


def compute_state_tracking_reward(
    belief_state: str,
    obs: str,
    previous_belief_state: str = "",
    transition_weight: float = 0.0,
) -> float:
    """Token-level alignment of the new belief with obs and (optionally) the transition from prior belief.

    With ``transition_weight`` in (0, 1] and a non-empty ``previous_belief_state``,
    returns a convex combination of F1(belief, obs) and F1(belief, prev + obs).
    With ``transition_weight`` == 0 or no prior belief, reduces to F1(belief, obs).
    """
    f_obs = _token_set_f1(belief_state, obs)
    prev = previous_belief_state.strip()
    tw = max(0.0, min(1.0, float(transition_weight)))
    if tw <= 0.0 or not prev:
        return f_obs
    ref_transition = f"{previous_belief_state} {obs}"
    f_tr = _token_set_f1(belief_state, ref_transition)
    return (1.0 - tw) * f_obs + tw * f_tr


# ---------------------------------------------------------------------------
# Value model (critic) — same init as actor, adds a linear value head
# ---------------------------------------------------------------------------

class _BeliefValueModel(nn.Module):
    """Wraps AutoModelForCausalLM and attaches a token-level linear value head.

    Initialized from the same checkpoint as the actor so both start from an
    identical base.  The value head itself is zero-initialized for a stable
    starting estimate of ~0.
    """

    def __init__(self, model_path: str, dtype=torch.bfloat16):
        super().__init__()
        from transformers import AutoModelForCausalLM

        lm = AutoModelForCausalLM.from_pretrained(
            model_path, torch_dtype=dtype, trust_remote_code=True
        )
        self.lm = lm
        self.value_head = nn.Linear(lm.config.hidden_size, 1, bias=False)
        nn.init.zeros_(self.value_head.weight)

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        """Returns token-level scalar values, shape ``(batch, seq_len)``."""
        out = self.lm(input_ids, output_hidden_states=True)
        hidden = out.hidden_states[-1].float()  # (batch, seq_len, hidden_size) — cast to fp32
        return self.value_head(hidden).squeeze(-1)  # (batch, seq_len)


# ---------------------------------------------------------------------------
# Training data container
# ---------------------------------------------------------------------------

class BeliefStateTrainingStep:
    """Holds data for one belief-state generation step used in training.

    Four equally-weighted reward components (each in [0, 1], max combined = 1.0):
      state_tracking_r    — LLM-as-judge: how well belief tracks the prev→obs transition
      state_correctness_r — LLM-as-judge: how accurately belief reflects the true env state
      diversity_r         — rule-based: Shannon entropy over certainty-marker distribution
      discounted_task_r   — gamma^(T-k) * final_task_reward

    format_compliance_r   — rule-based multiplier [0, 1]: applied to the combined score
                            so that dropping the bullet+certainty-label format zeroes out
                            all reward signal (anti-reward-hacking gate).
    """
    __slots__ = (
        "prompt_ids",             # list[int] — tokenised prompt (user turn)
        "response_ids",           # list[int] — tokenised response (belief state)
        "old_token_log_probs",    # list[float] — log π_old per response token (PPO)
        "state_tracking_r",       # float — LLM-based state-tracking quality [0, 1]
        "state_correctness_r",    # float — LLM-based correctness vs ground truth [0, 1]
        "diversity_r",            # float — entropy-based certainty diversity [0, 1]
        "discounted_task_r",      # float — gamma^(T-k) * final_reward [0, 1]
        "format_compliance_r",    # float — rule-based format gate [0, 1]
        "alpha",                  # float — kept for logging / legacy compatibility
    )

    def __init__(
        self,
        prompt_ids: List[int],
        response_ids: List[int],
        state_tracking_r: float,
        discounted_task_r: float,
        alpha: float,
        old_token_log_probs: Optional[List[float]] = None,
        state_correctness_r: float = 0.0,
        format_compliance_r: float = 1.0,
        diversity_r: float = 0.0,
    ):
        self.prompt_ids = prompt_ids
        self.response_ids = response_ids
        self.old_token_log_probs = old_token_log_probs or []
        self.state_tracking_r = state_tracking_r
        self.state_correctness_r = state_correctness_r
        self.diversity_r = diversity_r
        self.discounted_task_r = discounted_task_r
        self.format_compliance_r = format_compliance_r
        self.alpha = alpha

    @property
    def total_reward(self) -> float:
        """Equal 1/4 weighting across four reward components, gated by format.

        format_compliance_r acts as a multiplier: a belief state that drops the
        required bullet+certainty-label structure scores 0 regardless of content quality.
        Each component is in [0, 1], so the combined maximum is 1.0.
        """
        return (
            self.state_tracking_r
            + self.state_correctness_r
            + self.diversity_r
            + self.discounted_task_r
        ) / 4.0 * self.format_compliance_r


# ---------------------------------------------------------------------------
# Trainer
# ---------------------------------------------------------------------------

class BeliefStateLMTrainer:
    """
    Belief-state LM: **vLLM** for rollout generation (optional) and **HuggingFace**
    CausalLM for PPO gradient steps, mirroring the hybrid actor / vLLM rollout split.

    Parameters
    ----------
    model_path : str
        Path to (or HF repo of) the pretrained belief-state model.
    tokenizer : transformers.PreTrainedTokenizerBase
        Shared tokenizer (must match the model's vocab).
    belief_vllm_engine : optional vLLM ``LLM`` instance
        When set, ``generate_batch`` uses vLLM (batched).  After each ``update``,
        the engine is rebuilt from HF weights via ``belief_vllm_rebuild_from_path``.
    belief_vllm_rebuild_from_path : optional callable
        ``(weights_dir: str) -> LLM`` used to recreate in-process belief vLLM.
        Not used for subprocess clients (reload uses ``belief_vllm_subprocess_llm_kwargs``).
    belief_vllm_subprocess_llm_kwargs : optional dict
        Keyword args for vLLM ``LLM`` in the child (excluding ``model``), required
        to ``reload`` after PPO when using ``BeliefVLLMSubprocessClient``.
    device : torch.device | str
        Device to load the HF trainable model onto.
    lr : float
        Learning rate for AdamW.
    max_gen_tokens : int
        Hard cap on belief-state output length during inference.
    gradient_clip : float
        Gradient clipping norm for the update step.
    ppo_clip_ratio : float
        PPO ε (clip range), same role as ``actor.ppo.clip_ratio`` in VERL.
    ppo_clip_ratio_low / ppo_clip_ratio_high : float | None
        Optional asymmetric clip; default None uses ``ppo_clip_ratio`` for both.
    ppo_policy_loss_mode : str
        VERL registry name, e.g. ``vanilla`` (same as typical actor PPO).
    ppo_clip_ratio_c : float
        Dual-clip lower ratio bound for negative advantages.
    gen_temperature : float
        Softmax temperature when sampling belief tokens during rollout.
    loss_agg_mode : str
        Passed to VERL ``agg_loss`` (e.g. ``token-mean``).
    ppo_task_reward_only : bool
        If True, PPO uses only ``discounted_task_r`` as the scalar and terminal
        token reward (ablation: no ``total_reward`` mix of LLM / diversity /
        format terms).
    """

    def __init__(
        self,
        model_path: str,
        tokenizer,
        device,
        lr: float = 1e-5,
        max_gen_tokens: int = 512,
        gradient_clip: float = 1.0,
        belief_vllm_engine: Any = None,
        belief_vllm_rebuild_from_path: Optional[Callable[[str], Any]] = None,
        belief_vllm_subprocess_llm_kwargs: Optional[Dict[str, Any]] = None,
        ppo_clip_ratio: float = 0.2,
        ppo_clip_ratio_low: Optional[float] = None,
        ppo_clip_ratio_high: Optional[float] = None,
        ppo_clip_ratio_c: float = 3.0,
        ppo_policy_loss_mode: str = "vanilla",
        ppo_mini_batch_size: int = 8,
        gen_temperature: float = 1.0,
        loss_agg_mode: str = "token-mean",
        use_value_function: bool = True,
        value_lr: float = 1e-5,
        value_clip_range: float = 0.5,
        gae_gamma: float = 1.0,
        gae_lambda: float = 0.95,
        ppo_task_reward_only: bool = False,
        use_kl_loss: bool = False,
        kl_loss_coef: float = 0.001,
        kl_loss_type: str = "low_var_kl",
    ):
        from transformers import AutoModelForCausalLM

        self.tokenizer = tokenizer
        self.device = torch.device(device) if isinstance(device, str) else device
        self._belief_vllm = belief_vllm_engine
        self._belief_vllm_rebuild = belief_vllm_rebuild_from_path
        self._belief_vllm_sync_dir: Optional[str] = None
        self._belief_model_path = model_path
        self._belief_vllm_active_path = model_path
        self._belief_subprocess_kw: Optional[Dict[str, Any]] = None
        if belief_vllm_subprocess_llm_kwargs is not None:
            self._belief_subprocess_kw = dict(belief_vllm_subprocess_llm_kwargs)
        is_sub = bool(
            self._belief_vllm is not None
            and getattr(self._belief_vllm, "_is_subprocess_client", False)
        )
        if self._belief_vllm is not None:
            if is_sub:
                if self._belief_subprocess_kw is None:
                    raise ValueError(
                        "belief_vllm_subprocess_llm_kwargs is required for subprocess belief vLLM"
                    )
            elif self._belief_vllm_rebuild is None:
                raise ValueError(
                    "belief_vllm_engine requires belief_vllm_rebuild_from_path to reload after PPO"
                )
        self.max_gen_tokens = max_gen_tokens
        self.gradient_clip = gradient_clip
        self.ppo_clip_ratio = ppo_clip_ratio
        self.ppo_clip_ratio_low = ppo_clip_ratio_low
        self.ppo_clip_ratio_high = ppo_clip_ratio_high
        self.ppo_clip_ratio_c = ppo_clip_ratio_c
        self.ppo_policy_loss_mode = ppo_policy_loss_mode
        self.ppo_mini_batch_size = max(1, ppo_mini_batch_size)
        self.gen_temperature = max(gen_temperature, 1e-6)
        self.loss_agg_mode = loss_agg_mode
        self._ppo_loss_fn = get_policy_loss_fn(ppo_policy_loss_mode)
        self.ppo_task_reward_only = bool(ppo_task_reward_only)
        if self.ppo_task_reward_only:
            logger.info(
                "[BeliefStateLMTrainer] Ablation: PPO reward = discounted_task_r only "
                "(no LLM / diversity / format-combined reward)."
            )
        self.use_kl_loss = bool(use_kl_loss)
        self.kl_loss_coef = float(kl_loss_coef)
        self.kl_loss_type = str(kl_loss_type)

        logger.info("[BeliefStateLMTrainer] Loading model from %s …", model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.bfloat16,
            trust_remote_code=True,
        )
        if is_sub:
            self.model = self.model.to(torch.device("cpu"))
            logger.info(
                "[BeliefStateLMTrainer] HF belief model on CPU during rollouts "
                "(subprocess vLLM uses the belief GPU)."
            )
        else:
            self.model = self.model.to(self.device)
        self.model.train()

        self.optimizer = torch.optim.AdamW(self.model.parameters(), lr=lr)
        logger.info("[BeliefStateLMTrainer] Model loaded (%d params).",
                    sum(p.numel() for p in self.model.parameters()))

        # Frozen reference model for KL-to-reference penalty (anchors the belief
        # LM to its initial distribution so PPO cannot collapse it). Shares the
        # same device placement rules as the trainable model.
        self.ref_model: Optional[nn.Module] = None
        if self.use_kl_loss:
            logger.info(
                "[BeliefStateLMTrainer] Loading frozen ref model from %s (kl_coef=%.4g, type=%s) …",
                model_path, self.kl_loss_coef, self.kl_loss_type,
            )
            self.ref_model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.bfloat16,
                trust_remote_code=True,
            )
            for p in self.ref_model.parameters():
                p.requires_grad_(False)
            self.ref_model.eval()
            if is_sub:
                self.ref_model = self.ref_model.to(torch.device("cpu"))
            else:
                self.ref_model = self.ref_model.to(self.device)

        # ---- Value model (critic) ----
        self.use_value_function = use_value_function
        self.value_clip_range = value_clip_range
        self.gae_gamma = gae_gamma
        self.gae_lambda = gae_lambda
        self.value_model: Optional[_BeliefValueModel] = None
        self.value_optimizer: Optional[torch.optim.AdamW] = None

        if use_value_function:
            logger.info("[BeliefStateLMTrainer] Loading value model from %s …", model_path)
            self.value_model = _BeliefValueModel(model_path, dtype=torch.bfloat16)
            if is_sub:
                self.value_model = self.value_model.to(torch.device("cpu"))
            else:
                self.value_model = self.value_model.to(self.device)
            self.value_model.train()
            self.value_optimizer = torch.optim.AdamW(
                self.value_model.parameters(), lr=value_lr
            )
            logger.info(
                "[BeliefStateLMTrainer] Value model loaded (%d params).",
                sum(p.numel() for p in self.value_model.parameters()),
            )

        if self._belief_vllm is not None:
            logger.info(
                "[BeliefStateLMTrainer] Rollout generation uses %s.",
                "subprocess vLLM" if is_sub else "vLLM engine",
            )

    def _move_optimizer_state(self, device) -> None:
        """Move AdamW moment buffers to ``device`` alongside the model.

        ``model.to(device)`` moves parameters but leaves optimizer state tensors
        (m, v) on their original device.  Call this every time the model is
        moved to keep all tensors co-located and to fully release the old device.
        Handles both the actor optimizer and the value optimizer.
        """
        for opt in [self.optimizer, self.value_optimizer]:
            if opt is None:
                continue
            for state in opt.state.values():
                for k, v in state.items():
                    if isinstance(v, torch.Tensor):
                        state[k] = v.to(device)

    def _ppo_actor_config(self) -> Any:
        """OmegaConf struct compatible with ``compute_policy_loss_vanilla``."""
        low = self.ppo_clip_ratio_low
        high = self.ppo_clip_ratio_high
        return OmegaConf.create(
            {
                "clip_ratio": self.ppo_clip_ratio,
                "clip_ratio_low": low if low is not None else self.ppo_clip_ratio,
                "clip_ratio_high": high if high is not None else self.ppo_clip_ratio,
                "clip_ratio_c": self.ppo_clip_ratio_c,
            }
        )

    def _extract_logprob_for_token(self, step_logprobs: Any, token_id: int) -> float:
        if not step_logprobs or not isinstance(step_logprobs, dict):
            return 0.0
        lp = step_logprobs.get(int(token_id))
        if lp is None:
            return 0.0
        return float(getattr(lp, "logprob", lp))

    def _generate_batch_vllm(
        self,
        prompts: List[str],
    ) -> Tuple[List[str], List[List[int]], List[List[int]], List[List[float]]]:
        from vllm import SamplingParams
        from vllm.inputs.data import TokensPrompt

        belief_texts: List[str] = []
        prompt_ids_batch: List[List[int]] = []
        response_ids_batch: List[List[int]] = []
        old_log_probs_batch: List[List[float]] = []

        eos_id = self.tokenizer.eos_token_id
        sp_kwargs: Dict[str, Any] = {
            "temperature": self.gen_temperature,
            "max_tokens": self.max_gen_tokens,
            "top_p": 1.0,
            "logprobs": 1,
            "detokenize": True,
        }
        if eos_id is not None:
            sp_kwargs["stop_token_ids"] = [eos_id]
        sp = SamplingParams(**sp_kwargs)

        tokens_in: List[TokensPrompt] = []
        p_ids_list: List[List[int]] = []
        for prompt_text in prompts:
            messages = [{"role": "user", "content": prompt_text}]
            p_ids = self.tokenizer.apply_chat_template(
                messages,
                tokenize=True,
                add_generation_prompt=True,
            )
            p_ids_list.append(p_ids)
            tokens_in.append(TokensPrompt(prompt_token_ids=p_ids))

        outputs = self._belief_vllm.generate(tokens_in, sampling_params=sp)

        for p_ids, out in zip(p_ids_list, outputs):
            seq = out.outputs[0]
            r_ids = [int(t) for t in seq.token_ids]
            old_lps: List[float] = []
            sub_lps = getattr(seq, "sampled_token_logprobs", None)
            if sub_lps is not None:
                old_lps = [float(x) for x in sub_lps]
            elif getattr(seq, "logprobs", None) is not None:
                lp_seq = seq.logprobs
                for j, tid in enumerate(r_ids):
                    step_lp = lp_seq[j] if j < len(lp_seq) else None
                    old_lps.append(
                        self._extract_logprob_for_token(step_lp, tid)
                    )
            else:
                old_lps = [0.0] * len(r_ids)

            raw = seq.text if getattr(seq, "text", None) else self.tokenizer.decode(
                r_ids, skip_special_tokens=True
            )
            match = re.search(
                r"<belief_state>(.*?)</belief_state>",
                raw, re.DOTALL | re.IGNORECASE
            )
            belief_texts.append(match.group(1).strip() if match else raw.strip())
            prompt_ids_batch.append(p_ids)
            response_ids_batch.append(r_ids)
            old_log_probs_batch.append(old_lps)

        return (
            belief_texts,
            prompt_ids_batch,
            response_ids_batch,
            old_log_probs_batch,
        )

    def reload_belief_vllm_from_dir(self, weights_dir: str) -> None:
        """Point belief vLLM at on-disk HF weights (used after PPO sync and resume)."""
        if self._belief_vllm is None:
            return
        if getattr(self._belief_vllm, "_is_subprocess_client", False):
            assert self._belief_subprocess_kw is not None
            self._belief_vllm.reload(weights_dir, dict(self._belief_subprocess_kw))
            self._belief_vllm_active_path = weights_dir
            logger.info("[BeliefStateLMTrainer] Subprocess belief vLLM reloaded from %s", weights_dir)
            return
        if self._belief_vllm_rebuild is None:
            return
        del self._belief_vllm
        self._belief_vllm = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        self._belief_vllm = self._belief_vllm_rebuild(weights_dir)
        logger.info("[BeliefStateLMTrainer] Belief vLLM reloaded from %s", weights_dir)

    def _sync_belief_vllm_from_hf(self) -> None:
        """Reload belief vLLM from HF weights after a PPO step."""
        if self._belief_vllm is None:
            return
        if self._belief_vllm_sync_dir is None:
            import os
            # Prefer RAM-backed /dev/shm to avoid slow disk I/O (this runs every rollout batch,
            # writing ~6 GB of model weights; RAM-backed saves are ~10x faster than HDD/SSD).
            ram_dir = "/dev/shm/belief_vllm_hf_sync"
            if os.path.isdir("/dev/shm"):
                os.makedirs(ram_dir, exist_ok=True)
                self._belief_vllm_sync_dir = ram_dir
            else:
                self._belief_vllm_sync_dir = tempfile.mkdtemp(prefix="belief_vllm_hf_sync_")
        sync_path = self._belief_vllm_sync_dir
        self.model.save_pretrained(sync_path)
        self.tokenizer.save_pretrained(sync_path)
        self.reload_belief_vllm_from_dir(sync_path)

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------

    def generate_batch(
        self,
        prompts: List[str],
    ) -> Tuple[List[str], List[List[int]], List[List[int]], List[List[float]]]:
        """Sample belief states and record ``log π_old`` per generated token (for PPO).

        Parameters
        ----------
        prompts : list[str]
            Each element is the user-turn text built by
            ``_build_belief_state_user_prompt``.

        Returns
        -------
        belief_texts : list[str]
            Extracted content between <belief_state>…</belief_state> tags
            (or the raw output if tags are absent).
        prompt_ids_batch : list[list[int]]
            Tokenised prompt ids for each example (needed for training).
        response_ids_batch : list[list[int]]
            Tokenised response ids for each example (needed for training).
        old_log_probs_batch : list[list[float]]
            Log-probability of each sampled token under the pre-update policy.
        """
        _be = "vllm" if self._belief_vllm is not None else "hf"
        print(
            f"[BELIEF_GEN] BeliefStateLMTrainer.generate_batch n={len(prompts)} backend={_be}",
            flush=True,
        )
        if self._belief_vllm is not None:
            if getattr(self._belief_vllm, "_is_subprocess_client", False):
                assert self._belief_subprocess_kw is not None
                self._belief_vllm.ensure_loaded(
                    self._belief_vllm_active_path, dict(self._belief_subprocess_kw)
                )
                if self.model.device.type != "cpu":
                    self.model.cpu()
                    gc.collect()
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
            return self._generate_batch_vllm(prompts)

        self.model.eval()
        belief_texts: List[str] = []
        prompt_ids_batch: List[List[int]] = []
        response_ids_batch: List[List[int]] = []
        old_log_probs_batch: List[List[float]] = []

        eos_id = self.tokenizer.eos_token_id

        with torch.no_grad():
            for prompt_text in prompts:
                messages = [{"role": "user", "content": prompt_text}]
                p_ids = self.tokenizer.apply_chat_template(
                    messages,
                    tokenize=True,
                    add_generation_prompt=True,
                )
                input_ids = torch.tensor([p_ids], dtype=torch.long, device=self.device)
                r_ids: List[int] = []
                old_lps: List[float] = []

                for _ in range(self.max_gen_tokens):
                    out = self.model(input_ids)
                    logits = (out.logits[:, -1, :].float() / self.gen_temperature)
                    dist = torch.distributions.Categorical(logits=logits)
                    next_tok = dist.sample()
                    old_lps.append(float(dist.log_prob(next_tok).item()))
                    tid = int(next_tok.item())
                    r_ids.append(tid)
                    input_ids = torch.cat(
                        [input_ids, next_tok.view(1, 1)], dim=1
                    )
                    if eos_id is not None and tid == eos_id:
                        break

                raw = self.tokenizer.decode(r_ids, skip_special_tokens=True)
                match = re.search(
                    r"<belief_state>(.*?)</belief_state>",
                    raw, re.DOTALL | re.IGNORECASE
                )
                belief_texts.append(match.group(1).strip() if match else raw.strip())
                prompt_ids_batch.append(p_ids)
                response_ids_batch.append(r_ids)
                old_log_probs_batch.append(old_lps)

        self.model.train()
        return (
            belief_texts,
            prompt_ids_batch,
            response_ids_batch,
            old_log_probs_batch,
        )

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def update(
        self,
        training_steps: List[BeliefStateTrainingStep],
        n_update_steps: int = 1,
    ) -> Dict[str, float]:
        """Run PPO (clipped surrogate) on the collected belief-state rollouts.

        Parameters
        ----------
        training_steps : list[BeliefStateTrainingStep]
            Collected belief-state generation data with rewards and old log-probs.
        n_update_steps : int
            Number of PPO passes over the same rollout batch (epochs).

        Returns
        -------
        dict with keys: loss, mean_reward, n_samples, ppo_kl, pg_clipfrac,
            vf_loss, vf_clipfrac
        """
        if not training_steps:
            logger.debug("[BeliefStateLMTrainer] No training data; skipping update.")
            return {
                "loss": 0.0,
                "mean_reward": 0.0,
                "n_samples": 0,
                "ppo_kl": 0.0,
                "pg_clipfrac": 0.0,
                "vf_loss": 0.0,
                "vf_clipfrac": 0.0,
                "kl_loss": 0.0,
                "kl_coef": self.kl_loss_coef if self.use_kl_loss else 0.0,
            }

        valid_steps: List[BeliefStateTrainingStep] = []
        for s in training_steps:
            if (
                s.response_ids
                and len(s.old_token_log_probs) == len(s.response_ids)
            ):
                valid_steps.append(s)

        if not valid_steps:
            logger.warning(
                "[BeliefStateLMTrainer] No steps with aligned old log-probs; skipping."
            )
            return {
                "loss": 0.0,
                "mean_reward": 0.0,
                "n_samples": 0,
                "ppo_kl": 0.0,
                "pg_clipfrac": 0.0,
                "vf_loss": 0.0,
                "vf_clipfrac": 0.0,
                "kl_loss": 0.0,
                "kl_coef": self.kl_loss_coef if self.use_kl_loss else 0.0,
            }

        is_sub = (
            self._belief_vllm is not None
            and getattr(self._belief_vllm, "_is_subprocess_client", False)
        )
        if is_sub:
            self._belief_vllm.park()
            self.model.to(self.device)
            if self.value_model is not None:
                self.value_model.to(self.device)
            if self.ref_model is not None:
                self.ref_model.to(self.device)
            self._move_optimizer_state(self.device)

        # Gradient checkpointing trades activations for recompute → reduces peak
        # GPU memory during the backward pass (important when model + optimizer
        # must co-reside on the same single GPU as the subprocess CUDA context).
        _gc_enabled = False
        if hasattr(self.model, "gradient_checkpointing_enable"):
            self.model.gradient_checkpointing_enable(
                gradient_checkpointing_kwargs={"use_reentrant": False}
            )
            _gc_enabled = True

        import random as _random

        def _scalar_ppo_reward(s: BeliefStateTrainingStep) -> float:
            return float(s.discounted_task_r) if self.ppo_task_reward_only else float(
                s.total_reward
            )

        rewards = torch.tensor(
            [_scalar_ppo_reward(s) for s in valid_steps], dtype=torch.float32
        )
        mean_r = rewards.mean().item()

        max_r_len = max(len(s.response_ids) for s in valid_steps)
        B = len(valid_steps)

        # Build padded old log-prob and response-mask tensors (both actors share these)
        old_lp = torch.zeros(B, max_r_len, device=self.device, dtype=torch.float32)
        resp_mask = torch.zeros(B, max_r_len, device=self.device, dtype=torch.float32)
        for i, s in enumerate(valid_steps):
            L = len(s.response_ids)
            old_lp[i, :L] = torch.tensor(
                s.old_token_log_probs, device=self.device, dtype=torch.float32
            )
            resp_mask[i, :L] = 1.0

        # ------------------------------------------------------------------ #
        # Advantage estimation                                                 #
        # ------------------------------------------------------------------ #
        if self.use_value_function and self.value_model is not None:
            # --- GAE: compute old token-level values with no gradient ---
            self.value_model.eval()
            old_values = torch.zeros(B, max_r_len, device=self.device, dtype=torch.float32)
            with torch.no_grad():
                for i, s in enumerate(valid_steps):
                    full_ids = s.prompt_ids + s.response_ids
                    full_tensor = torch.tensor(
                        [full_ids], dtype=torch.long, device=self.device
                    )
                    vals = self.value_model(full_tensor)[0]  # (seq_len,)
                    resp_start = len(s.prompt_ids)
                    L = len(s.response_ids)
                    old_values[i, :L] = vals[resp_start : resp_start + L].float()
            self.value_model.train()

            # Token-level rewards: outcome reward placed at the final response token
            token_rewards = torch.zeros(B, max_r_len, device=self.device, dtype=torch.float32)
            for i, s in enumerate(valid_steps):
                L = len(s.response_ids)
                if L > 0:
                    token_rewards[i, L - 1] = _scalar_ppo_reward(s)

            # GAE advantages and returns (masked_whiten applied inside)
            adv, returns = compute_gae_advantage_return(
                token_level_rewards=token_rewards,
                values=old_values,
                response_mask=resp_mask,
                gamma=self.gae_gamma,
                lam=self.gae_lambda,
            )
        else:
            # Fallback: normalised sequence-level returns broadcast to tokens
            bsz = len(valid_steps)
            if bsz < 2:
                norm_r = torch.zeros(bsz, dtype=torch.float32)
            else:
                std_r = rewards.std(unbiased=False).item()
                norm_r = (
                    torch.zeros_like(rewards)
                    if std_r < 1e-8
                    else (rewards - mean_r) / (std_r + 1e-8)
                )
            adv = norm_r.to(self.device).unsqueeze(1).expand(B, max_r_len)
            returns = None
            old_values = None

        # ------------------------------------------------------------------ #
        # Ref log-prob precompute (KL-to-reference)                            #
        # Done once, before the PPO epochs, so the ref model can be moved to  #
        # CPU during the memory-heavy actor update (actor + AdamW + grads +   #
        # activations already saturate a single belief GPU for 4B-class       #
        # models; keeping ref resident alongside OOMs after a few steps).     #
        # ------------------------------------------------------------------ #
        ref_lp: Optional[torch.Tensor] = None
        if self.use_kl_loss and self.ref_model is not None:
            self.ref_model.to(self.device)
            self.ref_model.eval()
            ref_lp = torch.zeros(B, max_r_len, device=self.device, dtype=torch.float32)
            with torch.no_grad():
                for i, s in enumerate(valid_steps):
                    full_ids = s.prompt_ids + s.response_ids
                    if len(full_ids) < 2:
                        continue
                    full_tensor = torch.tensor(
                        [full_ids], dtype=torch.long, device=self.device
                    )
                    ref_logits = self.ref_model(full_tensor).logits[0, :-1, :].float()
                    labels = full_tensor[0, 1:]
                    ref_log_probs = F.log_softmax(ref_logits, dim=-1)
                    ref_token_lp = ref_log_probs[
                        torch.arange(len(labels), device=self.device), labels
                    ]
                    resp_start = len(s.prompt_ids) - 1
                    L = len(s.response_ids)
                    ref_lp[i, :L] = ref_token_lp[resp_start : resp_start + L]
            # Free ref model GPU memory before actor epochs.
            self.ref_model.cpu()
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

        # ------------------------------------------------------------------ #
        # PPO epochs                                                           #
        # ------------------------------------------------------------------ #
        total_loss = 0.0
        last_kl = 0.0
        last_clip = 0.0
        last_vf_loss = 0.0
        last_vf_clip = 0.0
        last_kl_loss = 0.0
        self.model.train()

        for _ in range(n_update_steps):
            perm = list(range(B))
            _random.shuffle(perm)

            epoch_loss = 0.0
            epoch_kl = 0.0
            epoch_clip = 0.0
            epoch_vf_loss = 0.0
            epoch_vf_clip = 0.0
            epoch_kl_loss = 0.0
            n_mini_batches = 0

            for mb_start in range(0, B, self.ppo_mini_batch_size):
                mb_indices = perm[mb_start : mb_start + self.ppo_mini_batch_size]
                n_mb = len(mb_indices)

                # ---- Critic update (before actor, mirrors veRL ordering) ----
                if self.use_value_function and self.value_model is not None:
                    assert returns is not None and old_values is not None
                    self.value_optimizer.zero_grad()
                    mb_vf_loss = 0.0
                    mb_vf_clip = 0.0
                    n_valid_vf = 0
                    for i in mb_indices:
                        s = valid_steps[i]
                        full_ids = s.prompt_ids + s.response_ids
                        if len(full_ids) < 2:
                            continue
                        full_tensor = torch.tensor(
                            [full_ids], dtype=torch.long, device=self.device
                        )
                        new_vals = self.value_model(full_tensor)[0]  # (seq_len,)
                        resp_start = len(s.prompt_ids)
                        L = len(s.response_ids)
                        new_vals_i = F.pad(
                            new_vals[resp_start : resp_start + L].float(),
                            (0, max_r_len - L),
                        ).unsqueeze(0)  # [1, max_r_len]
                        vf_loss_i, vf_clip_i = compute_value_loss(
                            vpreds=new_vals_i,
                            returns=returns[i : i + 1],
                            values=old_values[i : i + 1],
                            response_mask=resp_mask[i : i + 1],
                            cliprange_value=self.value_clip_range,
                            loss_agg_mode=self.loss_agg_mode,
                        )
                        (vf_loss_i / n_mb).backward()
                        mb_vf_loss += float(vf_loss_i.detach().item())
                        mb_vf_clip += (
                            float(vf_clip_i.detach().item())
                            if isinstance(vf_clip_i, torch.Tensor)
                            else float(vf_clip_i)
                        )
                        n_valid_vf += 1
                    if n_valid_vf > 0:
                        torch.nn.utils.clip_grad_norm_(
                            self.value_model.parameters(), self.gradient_clip
                        )
                        self.value_optimizer.step()
                        epoch_vf_loss += mb_vf_loss / n_valid_vf
                        epoch_vf_clip += mb_vf_clip / n_valid_vf

                # ---- Actor update ----
                self.optimizer.zero_grad()
                mb_loss = 0.0
                mb_kl = 0.0
                mb_clip = 0.0
                mb_kl_loss = 0.0
                n_valid_mb = 0

                for i in mb_indices:
                    step = valid_steps[i]
                    full_ids = step.prompt_ids + step.response_ids
                    if len(full_ids) < 2:
                        continue
                    full_tensor = torch.tensor(
                        [full_ids], dtype=torch.long, device=self.device
                    )
                    outputs = self.model(full_tensor)
                    logits = outputs.logits[0, :-1, :].float()
                    labels = full_tensor[0, 1:]
                    log_probs = F.log_softmax(logits, dim=-1)
                    token_lp = log_probs[
                        torch.arange(len(labels), device=self.device), labels
                    ]
                    resp_start = len(step.prompt_ids) - 1
                    L = len(step.response_ids)
                    new_lp_i = F.pad(
                        token_lp[resp_start : resp_start + L], (0, max_r_len - L)
                    ).unsqueeze(0)  # [1, max_r_len]
                    old_lp_i = old_lp[i : i + 1]    # [1, max_r_len], no grad
                    adv_i    = adv[i : i + 1]        # [1, max_r_len], no grad
                    mask_i   = resp_mask[i : i + 1]  # [1, max_r_len], no grad

                    pg_loss_i, pg_clipfrac_i, ppo_kl_i, _ = self._ppo_loss_fn(
                        old_lp_i, new_lp_i, adv_i, mask_i,
                        self.loss_agg_mode, self._ppo_actor_config(), None,
                    )
                    loss_i = pg_loss_i
                    if self.use_kl_loss and ref_lp is not None:
                        ref_lp_i = ref_lp[i : i + 1]  # [1, max_r_len], no grad
                        kld = kl_penalty(
                            logprob=new_lp_i, ref_logprob=ref_lp_i, kl_penalty=self.kl_loss_type
                        )
                        kl_loss_i = agg_loss(
                            loss_mat=kld, loss_mask=mask_i, loss_agg_mode=self.loss_agg_mode
                        )
                        loss_i = loss_i + kl_loss_i * self.kl_loss_coef
                        mb_kl_loss += float(kl_loss_i.detach().item())

                    (loss_i / n_mb).backward()
                    mb_loss += float(pg_loss_i.detach().item())
                    mb_kl   += float(ppo_kl_i.detach().item())
                    mb_clip += float(pg_clipfrac_i.detach().item())
                    n_valid_mb += 1

                if n_valid_mb == 0:
                    continue
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.gradient_clip)
                self.optimizer.step()

                epoch_loss    += mb_loss    / n_valid_mb
                epoch_kl      += mb_kl      / n_valid_mb
                epoch_clip    += mb_clip    / n_valid_mb
                epoch_kl_loss += mb_kl_loss / n_valid_mb
                n_mini_batches += 1

            if n_mini_batches > 0:
                total_loss    += epoch_loss    / n_mini_batches
                last_kl        = epoch_kl      / n_mini_batches
                last_clip      = epoch_clip    / n_mini_batches
                last_vf_loss   = epoch_vf_loss / n_mini_batches
                last_vf_clip   = epoch_vf_clip / n_mini_batches
                last_kl_loss   = epoch_kl_loss / n_mini_batches

        avg_loss = total_loss / max(n_update_steps, 1)
        logger.info(
            "[BeliefStateLMTrainer] PPO update: loss=%.4f vf_loss=%.4f mean_reward=%.4f "
            "n=%d ppo_kl=%.4f clipfrac=%.4f vf_clipfrac=%.4f kl_loss=%.4f kl_coef=%.4g",
            avg_loss,
            last_vf_loss,
            mean_r,
            len(valid_steps),
            last_kl,
            last_clip,
            last_vf_clip,
            last_kl_loss,
            self.kl_loss_coef if self.use_kl_loss else 0.0,
        )
        # For subprocess vLLM: move HF model AND optimizer states off the belief GPU
        # *before* asking the subprocess to reload vLLM on that same GPU.
        if _gc_enabled and hasattr(self.model, "gradient_checkpointing_disable"):
            self.model.gradient_checkpointing_disable()

        if is_sub:
            self.model.cpu()
            if self.value_model is not None:
                self.value_model.cpu()
            if self.ref_model is not None:
                self.ref_model.cpu()
            self._move_optimizer_state(torch.device("cpu"))
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        self._sync_belief_vllm_from_hf()
        return {
            "loss": avg_loss,
            "mean_reward": mean_r,
            "n_samples": len(valid_steps),
            "ppo_kl": last_kl,
            "pg_clipfrac": last_clip,
            "vf_loss": last_vf_loss,
            "vf_clipfrac": last_vf_clip,
            "kl_loss": last_kl_loss,
            "kl_coef": self.kl_loss_coef if self.use_kl_loss else 0.0,
        }

    # ------------------------------------------------------------------
    # Checkpoint
    # ------------------------------------------------------------------

    def save_training_checkpoint(self, output_dir: str) -> None:
        """Save HF weights + AdamW state for trainer resume. Does not reload vLLM."""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        training = self.model.training
        self.model.save_pretrained(output_dir)
        self.model.train(training)
        self.tokenizer.save_pretrained(output_dir)
        torch.save(self.optimizer.state_dict(), os.path.join(output_dir, "optimizer.pt"))
        if self.value_model is not None and self.value_optimizer is not None:
            torch.save(
                self.value_model.state_dict(),
                os.path.join(output_dir, "value_model.pt"),
            )
            torch.save(
                self.value_optimizer.state_dict(),
                os.path.join(output_dir, "value_optimizer.pt"),
            )
        logger.info("[BeliefStateLMTrainer] Training checkpoint saved to %s", output_dir)

    def load_training_checkpoint(self, input_dir: str) -> None:
        """Load HF weights + optimizer; reload belief vLLM from ``input_dir``."""
        from transformers import AutoModelForCausalLM

        input_dir = os.path.abspath(input_dir)
        if not os.path.isdir(input_dir):
            logger.warning("[BeliefStateLMTrainer] Missing checkpoint dir %s", input_dir)
            return

        is_sub = (
            self._belief_vllm is not None
            and getattr(self._belief_vllm, "_is_subprocess_client", False)
        )
        prev_lr = self.optimizer.param_groups[0]["lr"]
        loaded = AutoModelForCausalLM.from_pretrained(
            input_dir,
            torch_dtype=torch.bfloat16,
            trust_remote_code=True,
        )
        if is_sub:
            loaded = loaded.to(torch.device("cpu"))
        else:
            loaded = loaded.to(self.device)
        self.model = loaded
        self.model.train()

        opt_path = os.path.join(input_dir, "optimizer.pt")
        if os.path.isfile(opt_path):
            try:
                opt_state = torch.load(opt_path, map_location="cpu", weights_only=True)
            except TypeError:
                opt_state = torch.load(opt_path, map_location="cpu")
            lr = opt_state.get("param_groups", [{}])[0].get("lr", prev_lr)
            self.optimizer = torch.optim.AdamW(self.model.parameters(), lr=lr)
            self.optimizer.load_state_dict(opt_state)
            self._move_optimizer_state(
                torch.device("cpu") if is_sub else self.device
            )
        else:
            logger.warning(
                "[BeliefStateLMTrainer] No optimizer.pt in %s; using fresh AdamW (lr=%s).",
                input_dir,
                prev_lr,
            )
            self.optimizer = torch.optim.AdamW(self.model.parameters(), lr=prev_lr)

        # ---- Restore value model and its optimizer ----
        if self.value_model is not None and self.value_optimizer is not None:
            vm_path = os.path.join(input_dir, "value_model.pt")
            if os.path.isfile(vm_path):
                try:
                    vm_state = torch.load(vm_path, map_location="cpu", weights_only=True)
                except TypeError:
                    vm_state = torch.load(vm_path, map_location="cpu")
                self.value_model.load_state_dict(vm_state)
                target_device = torch.device("cpu") if is_sub else self.device
                self.value_model.to(target_device)
                self.value_model.train()
            vo_path = os.path.join(input_dir, "value_optimizer.pt")
            if os.path.isfile(vo_path):
                try:
                    vo_state = torch.load(vo_path, map_location="cpu", weights_only=True)
                except TypeError:
                    vo_state = torch.load(vo_path, map_location="cpu")
                prev_vlr = self.value_optimizer.param_groups[0]["lr"]
                self.value_optimizer = torch.optim.AdamW(
                    self.value_model.parameters(), lr=prev_vlr
                )
                self.value_optimizer.load_state_dict(vo_state)
                self._move_optimizer_state(
                    torch.device("cpu") if is_sub else self.device
                )

        self._belief_vllm_active_path = input_dir
        self.reload_belief_vllm_from_dir(input_dir)
        logger.info("[BeliefStateLMTrainer] Loaded training checkpoint from %s", input_dir)

    def save(self, output_dir: str) -> None:
        """Save model + tokenizer to ``output_dir``."""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        logger.info("[BeliefStateLMTrainer] Saved to %s", output_dir)
        if self._belief_vllm is not None and getattr(
            self._belief_vllm, "_is_subprocess_client", False
        ):
            assert self._belief_subprocess_kw is not None
            self._belief_vllm.reload(output_dir, dict(self._belief_subprocess_kw))
            self._belief_vllm_active_path = output_dir
            return
        if self._belief_vllm is not None and self._belief_vllm_rebuild is not None:
            del self._belief_vllm
            self._belief_vllm = None
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            self._belief_vllm = self._belief_vllm_rebuild(output_dir)
