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
Offline belief-state dataset generator using GPT-4.1-mini.

For each game instance in a train parquet file, this script generates:
  1. A GOLD trajectory  (walkthrough / optimal actions stored in parquet)
  2. N_RANDOM random trajectories (admissible-command sampling with seeded RNG)

At every step t of every trajectory, GPT-4.1-mini is called to produce an updated
natural-language belief state given: the goal, the previous belief state (empty at t=0),
and the current observation.  Each factual bullet MUST use exactly one certainty level \
from the same Likert-style scale as ``goal_memory_freeform_bdi`` in TextWorldAgent \
(certain/confirmed, almost certain, probable, possible, unlikely, doubtful, unknown).  \
Plans and next actions are forbidden (no leakage).

Output: one JSONL file where each line is one step of one trajectory:
{
    "instance_id":         str,
    "trajectory_source":   "goal" | "random",   # goal = walkthrough from parquet; random = seeded rollout
    "traj_type":           "goal" | "random",   # alias of trajectory_source (same values)
    "from_goal_trajectory": bool,               # True iff trajectory_source == "goal"
    "from_random_trajectory": bool,             # True iff trajectory_source == "random"
    "seed":                int | null,          # RNG seed for random trajectories only; null for goal
    "step":                int,
    "goal":                str,
    "previous_belief_state": str,           # belief state from step t-1 (empty string at t=0)
    "observations":        [obs_0, ..., obs_t],
    "actions":             [act_0, ..., act_{t-1}],
    "admissible_commands": [str, ...],      # commands available at step t
    "gpt_belief_state":    str,             # raw GPT text inside <belief_state>...</belief_state>
    "belief_state":        str,             # sanitised belief — action-leaking sentences removed
    "action_leaked":       bool,            # True if any forward-planning sentences were stripped
    "leaked_sentences":    [str, ...],      # sentences that were removed (for auditing)
    "gpt_full_response":   str              # full GPT response (for debugging / re-parsing)
}

Usage
-----
AZURE_OPENAI_API_KEY=<key> python3 -m meow_tea_experiments.data_generation.generate_belief_state_dataset \\
    --parquet_path      ../data-basic-parquet/train.parquet \\
    --output_path       local/belief_dataset/train_belief.jsonl \\
    --azure_endpoint    "[ANONYMIZED_AZURE_ENDPOINT]" \\
    --azure_api_version 2024-12-01-preview \\
    --gpt_model         gpt-5.4-mini \\
    --n_random_trajs    4 \\
    --max_random_steps  15 \\
    --random_seed_base  42
AZURE_OPENAI_API_KEY=<YOUR_AZURE_OPENAI_API_KEY> python3 -m meow_tea_experiments.data_generation.generate_belief_state_dataset     --parquet_path /home/user/textworld-RL/data-basic-parquet/train.parquet     --output_path       local/basic_2_wep_dataset/train_2_wep.jsonl     --azure_endpoint    "[ANONYMIZED_AZURE_ENDPOINT]"     --azure_api_version 2024-12-01-preview     --gpt_model         gpt-5.4-mini     --n_random_trajs    3     --max_random_steps  15     --random_seed_base  42
AZURE_OPENAI_API_KEY=<> python3 -m meow_tea_experiments.data_generation.generate_belief_state_dataset     --parquet_path /home/user/textworld-RL/data-basic-parquet/train.parquet     --output_path       local/basic_summary_dataset/train_summary.jsonl     --azure_endpoint    "[ANONYMIZED_AZURE_ENDPOINT]"     --azure_api_version 2024-12-01-preview     --gpt_model         gpt-5.4-mini     --n_random_trajs    3     --max_random_steps  15     --random_seed_base  42
AZURE_OPENAI_API_KEY=<> python3 -m meow_tea_experiments.data_generation.generate_belief_state_dataset     --parquet_path /home/user/textworld-RL/data-basic-parquet/train.parquet     --output_path       local/basic_summary_dataset/train_summary.jsonl     --azure_endpoint    "[ANONYMIZED_AZURE_ENDPOINT]"     --azure_api_version 2024-12-01-preview     --gpt_model         gpt-5.4-mini     --n_random_trajs    3     --max_random_steps  15     --random_seed_base  42

"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional

import pandas as pd
from tqdm import tqdm
from openai import AzureOpenAI

from meow_tea_train.agentic_menu.sync_textworld.env import TextWorldEnv, AlfWorldEnv

# tatsu (used by TextWorld's logic parser) is not thread-safe: it uses a
# module-level parser stack that raises IndexError under concurrent access.
# Serialize all TextWorldEnv usage behind this lock.  Env steps are fast so
# this does not meaningfully reduce throughput (GPT calls dominate).
_TW_LOCK = threading.Lock()

# File extension per environment
_INSTANCE_EXT: Dict[str, str] = {
    "textworld": ".z8",
    "alfworld": ".tw-pddl",
}


class _AlfWorldTrajEnv:
    """Minimal AlfWorld env wrapper that exposes admissible commands for
    random trajectory collection while keeping observations consistent with
    what AlfWorldEnv produces during training (raw feedback text).
    """

    def __init__(self, instance_file: str) -> None:
        import textworld
        from textworld.envs.wrappers import Filter
        from alfworld.agents.environment.alfred_tw_env import AlfredDemangler
        from textworld.agents import HumanAgent

        infos = textworld.EnvInfos(
            feedback=True,
            admissible_commands=True,
            won=True,
        )
        self._env = textworld.start(
            instance_file, infos, wrappers=[Filter, AlfredDemangler()]
        )
        agent = HumanAgent()
        agent.reset(self._env)
        _, info = self._env.reset()
        # Follow AlfWorldEnv convention: use info["feedback"] for init_state
        self.init_state: str = info["feedback"]
        self._admissible: List[str] = list(info.get("admissible_commands") or [])

    def one_step(self, command: str) -> tuple:
        try:
            result = self._env.step(command)
        except Exception:
            result = self._env.step("")
        # With Filter wrapper: (obs_text, score, done, info_dict)
        obs, score, done = result[0], result[1], result[2]
        info: dict = result[3] if len(result) > 3 else {}
        self._admissible = list(info.get("admissible_commands") or [])
        return obs, bool(done), float(score)

    def get_admissible_commands(self) -> List[str]:
        return self._admissible


def _make_traj_env(instance_file: str, env_name: str):
    """Return a trajectory env for *instance_file* matching *env_name*."""
    if env_name == "alfworld":
        return _AlfWorldTrajEnv(instance_file)
    return TextWorldEnv(instance_file=instance_file)


# ── Prompt templates ──────────────────────────────────────────────────────────

_SYSTEM_PROMPT = (
    "You are an expert TextWorld game solver reasoning about world state under uncertainty."
)

_BELIEF_PROMPT_TEMPLATE = """\
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

# SEP token used by the training pipeline to delimit actions in responses
_SEP_TOKEN = "<|im_end|>"


# ── Helpers ───────────────────────────────────────────────────────────────────

def extract_admissible_commands(obs: str) -> List[str]:
    """Pull the comma-separated admissible-commands list out of an observation."""
    match = re.search(r"Admissible commands:\s*(.+)$", obs, re.DOTALL)
    if not match:
        return []
    return [cmd.strip() for cmd in match.group(1).split(",") if cmd.strip()]


def extract_goal_from_prompt(prompt_text: str) -> str:
    """
    Strip the 'current state: ...' tail from the stored prompt to recover
    just the goal / task description.
    """
    if "current state:" in prompt_text:
        return prompt_text.split("current state:")[0].strip()
    return prompt_text.strip()


def parse_gold_actions(response_field: str) -> List[str]:
    """
    The parquet ``extra_info.response`` field stores gold actions joined by
    the SEP token ``<|im_end|>``.  Extract them as a plain list.
    """
    return [a.strip() for a in response_field.split(_SEP_TOKEN) if a.strip()]


# ── Action-leakage detection & sanitisation ───────────────────────────────────

# Phrases that signal the model is planning a next action rather than describing
# past observations.  Patterns are matched case-insensitively against each sentence.
_LEAKAGE_PATTERNS: List[str] = [
    r"\bI (will|should|must|need to|am going to|plan to|intend to)\b",
    r"\bmy next (step|action|move|plan)\b",
    r"\bnext[,]? I (will|should|need|plan|intend)\b",
    r"\bI (should|will|must) (try|go|take|open|pick|examine|look|drop|use|put)\b",
    r"\b(let me|I'll) (try|go|take|open|pick|examine|look|drop|use|put)\b",
    r"\bthe (best|next|right) (action|move|step|command)\b",
    r"\bI (need|want) to (go|take|open|pick|examine|look|drop|use|put)\b",
]

_LEAKAGE_RE = re.compile(
    "|".join(_LEAKAGE_PATTERNS),
    re.IGNORECASE,
)


def _split_sentences(text: str) -> List[str]:
    """Naively split text into sentences on '.', '!', '?' or newlines."""
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [p.strip() for p in parts if p.strip()]


def sanitise_belief_state(belief_text: str) -> Dict[str, Any]:
    """
    Detect and remove sentences that leak future action intent from a belief state.

    Returns:
        sanitised_belief — belief text with leaking sentences removed
        action_leaked    — True if any leakage was found (before removal)
        leaked_sentences — list of sentences that were removed
    """
    sentences = _split_sentences(belief_text)
    clean: List[str] = []
    leaked: List[str] = []

    for sent in sentences:
        if _LEAKAGE_RE.search(sent):
            leaked.append(sent)
        else:
            clean.append(sent)

    sanitised = " ".join(clean).strip()
    return {
        "sanitised_belief": sanitised,
        "action_leaked": len(leaked) > 0,
        "leaked_sentences": leaked,
    }


# ── Trajectory collectors ─────────────────────────────────────────────────────

def collect_gold_trajectory(
    instance_file: str,
    gold_actions: List[str],
    env_name: str = "textworld",
) -> List[str]:
    """
    Replay gold_actions in the env.

    Returns interleaved list: [obs_0, act_0, obs_1, act_1, ..., obs_T]
    Stops early if the game is won.
    """
    with _TW_LOCK:
        env = _make_traj_env(instance_file, env_name)
        trajectory: List[str] = [env.init_state]
        for action in gold_actions:
            next_obs, has_won, _ = env.one_step(action)
            trajectory.append(action)
            trajectory.append(next_obs)
            if has_won:
                break
    return trajectory


def collect_random_trajectory(
    instance_file: str,
    max_steps: int,
    seed: int,
    env_name: str = "textworld",
) -> List[str]:
    """
    Run the env for up to max_steps, sampling uniformly from admissible
    commands at each step using a seeded RNG.

    For textworld: admissible commands are parsed from the observation text.
    For alfworld: admissible commands are retrieved directly from the env.

    Returns interleaved list: [obs_0, act_0, obs_1, act_1, ..., obs_T]
    """
    rng = random.Random(seed)
    with _TW_LOCK:
        env = _make_traj_env(instance_file, env_name)
        trajectory: List[str] = [env.init_state]
        obs = env.init_state
        for _ in range(max_steps):
            if env_name == "alfworld":
                admissible = env.get_admissible_commands()
            else:
                admissible = extract_admissible_commands(obs)
            if not admissible:
                break
            action = rng.choice(admissible)
            next_obs, has_won, _ = env.one_step(action)
            trajectory.append(action)
            trajectory.append(next_obs)
            obs = next_obs
            if has_won:
                break
    return trajectory


# ── Belief-state prompt builder ───────────────────────────────────────────────

def build_belief_prompt(
    goal: str,
    previous_belief_state: str,
    current_obs: str,
) -> str:
    """
    Build the user prompt asking GPT to produce an updated belief state.

    previous_belief_state — belief state from the previous step (empty string if first step)
    current_obs           — the observation at the current step
    """
    prev_belief_str = (
        previous_belief_state.strip()
        if previous_belief_state.strip()
        else "(none — this is the first observation)"
    )
    return _BELIEF_PROMPT_TEMPLATE.format(
        goal=goal,
        previous_belief_state=prev_belief_str,
        current_obs=current_obs.strip(),
    )


# ── GPT call ──────────────────────────────────────────────────────────────────

def call_gpt_belief(
    client: AzureOpenAI,
    goal: str,
    previous_belief_state: str,
    current_obs: str,
    model: str,
    temperature: float,
    max_retries: int = 2,
) -> Dict[str, Any]:
    """
    Ask GPT-4.1-mini for an updated natural-language belief state.

    The belief state is produced incrementally: given the goal, the previous belief
    state (empty string at step 0), and the current observation, GPT generates an
    updated belief state.  Plain text inside <belief_state>...</belief_state>,
    using hedging words (certain / likely / possibly / unknown …) for uncertainty.

    Returns dict:
        gpt_belief_state  — raw natural-language text inside <belief_state>...</belief_state>
        belief_state      — sanitised belief state with action-leaking sentences removed
        action_leaked     — True if any leakage was detected and stripped
        leaked_sentences  — list of removed sentences (empty if no leakage)
        gpt_full_response — full model output string (useful for debugging)
    """
    user_prompt = build_belief_prompt(goal, previous_belief_state, current_obs)

    for attempt in range(max_retries + 1):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user",   "content": user_prompt},
                ],
                temperature=temperature,
                max_completion_tokens=512,
            )
            full_text: str = resp.choices[0].message.content or ""

            # Extract belief state block
            bs_match = re.search(
                r"<belief_state>(.*?)</belief_state>",
                full_text,
                re.DOTALL | re.IGNORECASE,
            )
            bs_text = bs_match.group(1).strip() if bs_match else ""

            # Detect and strip action-leaking sentences
            san = sanitise_belief_state(bs_text)

            return {
                "gpt_belief_state": bs_text,           # raw GPT output (for auditing)
                "belief_state": san["sanitised_belief"],  # clean version for training
                "action_leaked": san["action_leaked"],
                "leaked_sentences": san["leaked_sentences"],
                "gpt_full_response": full_text,
            }

        except Exception as exc:  # noqa: BLE001
            if attempt == max_retries:
                print(f"ERROR: {exc}")
                return {
                    "gpt_belief_state": "",
                    "belief_state": "",
                    "action_leaked": False,
                    "leaked_sentences": [],
                    "gpt_full_response": f"ERROR: {exc}",
                }

    # Should never reach here
    return {
        "gpt_belief_state": "",
        "belief_state": "",
        "action_leaked": False,
        "leaked_sentences": [],
        "gpt_full_response": "",
    }


# ── Per-instance processing ────────────────────────────────────────────────────

def _run_trajectory(
    traj: List[str],
    traj_source: str,
    seed: Optional[int],
    instance_id: str,
    goal: str,
    client: AzureOpenAI,
    gpt_model: str,
    gpt_temperature: float,
) -> List[Dict[str, Any]]:
    """
    Run GPT belief-state calls for a single pre-collected trajectory.

    Steps are processed sequentially because each step's belief state is
    conditioned on the previous step's output (belief state chaining).
    Safe to call from multiple threads simultaneously for different trajectories.
    """
    is_goal = traj_source == "goal"
    n_obs = (len(traj) + 1) // 2
    prev_belief = ""
    records: List[Dict[str, Any]] = []

    for t in range(n_obs):
        obs_t = traj[2 * t]
        admissible = extract_admissible_commands(obs_t)
        belief = call_gpt_belief(
            client, goal, prev_belief, obs_t, gpt_model, gpt_temperature
        )
        records.append({
            "instance_id":            instance_id,
            "trajectory_source":      traj_source,
            "traj_type":              traj_source,
            "from_goal_trajectory":   is_goal,
            "from_random_trajectory": not is_goal,
            "seed":                   seed,
            "step":                   t,
            "goal":                   goal,
            "previous_belief_state":  prev_belief,
            "observations":           [traj[2 * i] for i in range(t + 1)],
            "actions":                [traj[2 * i + 1] for i in range(t)],
            "admissible_commands":    admissible,
            **belief,
        })
        prev_belief = belief["belief_state"]

    return records


def process_instance(
    row: Dict[str, Any],
    client: AzureOpenAI,
    n_random_trajs: int,
    max_random_steps: int,
    random_seed_base: int,
    gpt_model: str,
    gpt_temperature: float,
    env_name: str = "textworld",
) -> List[Dict[str, Any]]:
    """
    Generate belief-state records for a single parquet row.

    Collects all trajectories first, then runs GPT calls for each trajectory
    in parallel (gold + random trajectories are independent).  Steps within
    each trajectory remain sequential due to belief-state chaining.

    Returns a flat list of step-level record dicts.
    """
    extra = row["extra_info"]
    instance_id: str = extra["instance_file"]
    ext = _INSTANCE_EXT.get(env_name, ".z8")
    instance_file: str = os.path.join(extra["instance_path"], instance_id + ext)
    goal: str = extract_goal_from_prompt(extra["prompt"])
    gold_actions = parse_gold_actions(extra["response"])

    # ── Collect trajectories (no API calls, fast) ─────────────────────────────
    # List of (traj, source, seed) tuples — all independent, process in parallel
    traj_specs: List[tuple] = []

    try:
        gold_traj = collect_gold_trajectory(instance_file, gold_actions, env_name=env_name)
        traj_specs.append((gold_traj, "goal", None))
    except Exception:  # noqa: BLE001
        print(f"[WARN] gold traj collection failed for {instance_id}:\n{traceback.format_exc()}")

    for k in range(n_random_trajs):
        seed = (random_seed_base + abs(hash(instance_id)) % 100_000 + k * 1_000) % (2**31)
        try:
            rand_traj = collect_random_trajectory(
                instance_file, max_random_steps, seed, env_name=env_name
            )
            traj_specs.append((rand_traj, "random", seed))
        except Exception:  # noqa: BLE001
            print(
                f"[WARN] random traj (seed={seed}) collection failed for {instance_id}:\n"
                f"{traceback.format_exc()}"
            )

    if not traj_specs:
        return []

    # ── Run GPT calls: trajectories in parallel, steps sequential within each ──
    def _submit(spec: tuple) -> List[Dict[str, Any]]:
        traj, source, seed = spec
        try:
            return _run_trajectory(traj, source, seed, instance_id, goal, client, gpt_model, gpt_temperature)
        except Exception:  # noqa: BLE001
            print(f"[WARN] GPT calls failed for {instance_id} ({source} seed={seed}):\n{traceback.format_exc()}")
            return []

    records: List[Dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=len(traj_specs)) as pool:
        for result in pool.map(_submit, traj_specs):
            records.extend(result)

    return records


# ── Main ──────────────────────────────────────────────────────────────────────

def main(args: argparse.Namespace) -> None:
    # ── Load parquet ──────────────────────────────────────────────────────────
    print(f"Loading parquet from {args.parquet_path} ...")
    df = pd.read_parquet(args.parquet_path)
    rows = df.to_dict("records")

    # Cap at max_instances if requested (0 = all)
    if args.max_instances > 0:
        rows = rows[: args.max_instances]
    print(f"Processing {len(rows)} instances")

    # ── Azure OpenAI client ───────────────────────────────────────────────────
    api_key = os.environ.get("AZURE_OPENAI_API_KEY") or args.azure_api_key
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT") or args.azure_endpoint
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION") or args.azure_api_version
    if not api_key:
        raise EnvironmentError(
            "Azure OpenAI key not found. Set AZURE_OPENAI_API_KEY or pass --azure_api_key."
        )
    if not endpoint:
        raise EnvironmentError(
            "Azure endpoint not found. Set AZURE_OPENAI_ENDPOINT or pass --azure_endpoint."
        )
    client = AzureOpenAI(
        api_key=api_key,
        azure_endpoint=endpoint,
        api_version=api_version,
    )

    # ── Output setup ─────────────────────────────────────────────────────────
    os.makedirs(os.path.dirname(os.path.abspath(args.output_path)), exist_ok=True)
    total_written = 0
    write_lock = threading.Lock()

    def _process_row(row: Dict[str, Any]) -> List[Dict[str, Any]]:
        return process_instance(
            row=row,
            client=client,
            n_random_trajs=args.n_random_trajs,
            max_random_steps=args.max_random_steps,
            random_seed_base=args.random_seed_base,
            gpt_model=args.gpt_model,
            gpt_temperature=args.gpt_temperature,
            env_name=args.env_name,
        )

    with open(args.output_path, "w", encoding="utf-8") as out_f:
        with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
            future_to_id = {executor.submit(_process_row, row): row["extra_info"]["instance_file"] for row in rows}
            for future in tqdm(as_completed(future_to_id), total=len(rows), desc="Instances"):
                inst_id = future_to_id[future]
                try:
                    step_records = future.result()
                    with write_lock:
                        for rec in step_records:
                            if rec.get("gpt_full_response", "").startswith("ERROR:"):
                                continue
                            out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                            total_written += 1
                        if total_written % 500 == 0:
                            out_f.flush()
                except Exception:  # noqa: BLE001
                    print(f"[ERROR] {inst_id}:\n{traceback.format_exc()}")

    print(f"\nDone.  Wrote {total_written} step records → {args.output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate offline belief-state dataset using Azure OpenAI (gpt-5.4-mini).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    # ── Environment ───────────────────────────────────────────────────────────
    parser.add_argument(
        "--env_name",
        type=str,
        default="textworld",
        choices=["textworld", "alfworld"],
        help=(
            "Game environment the parquet was produced from. "
            "Controls the instance file extension (.z8 for textworld, .tw-pddl for alfworld) "
            "and the trajectory-collection backend."
        ),
    )
    # ── I/O ───────────────────────────────────────────────────────────────────
    parser.add_argument(
        "--parquet_path",
        type=str,
        required=True,
        help="Path to train.parquet produced by rl_local_data_processor.py",
    )
    parser.add_argument(
        "--output_path",
        type=str,
        required=True,
        help="Output .jsonl path for the belief-state dataset",
    )
    # ── Azure OpenAI credentials (env vars take precedence if set) ────────────
    parser.add_argument(
        "--azure_endpoint",
        type=str,
        default="[ANONYMIZED_AZURE_ENDPOINT]",
        help=(
            "Azure OpenAI endpoint URL. "
            "Overridden by AZURE_OPENAI_ENDPOINT env var if set."
        ),
    )
    parser.add_argument(
        "--azure_api_key",
        type=str,
        default="",
        help=(
            "Azure OpenAI subscription key. "
            "Prefer setting AZURE_OPENAI_API_KEY env var instead of passing here."
        ),
    )
    parser.add_argument(
        "--azure_api_version",
        type=str,
        default="2024-12-01-preview",
        help=(
            "Azure OpenAI API version string. "
            "Overridden by AZURE_OPENAI_API_VERSION env var if set."
        ),
    )
    # ── Model / generation ────────────────────────────────────────────────────
    parser.add_argument(
        "--gpt_model",
        type=str,
        default="gpt-5.4-mini",
        help="Azure deployment name to use for belief-state generation",
    )
    parser.add_argument(
        "--gpt_temperature",
        type=float,
        default=0.3,
        help=(
            "Sampling temperature for GPT calls. "
            "0.3 gives slight diversity while staying close to the most likely belief state."
        ),
    )
    # ── Trajectory / diversity ────────────────────────────────────────────────
    parser.add_argument(
        "--n_random_trajs",
        type=int,
        default=3,
        help="Number of random (seeded) trajectories to generate per instance",
    )
    parser.add_argument(
        "--max_random_steps",
        type=int,
        default=15,
        help="Maximum number of steps for each random trajectory",
    )
    parser.add_argument(
        "--random_seed_base",
        type=int,
        default=42,
        help="Base integer used to derive per-instance random seeds",
    )
    parser.add_argument(
        "--max_instances",
        type=int,
        default=300,
        help="Cap the number of instances to process (0 = all). Useful for dry runs.",
    )
    parser.add_argument(
        "--max_workers",
        type=int,
        default=8,
        help=(
            "Number of instances to process in parallel. "
            "Each instance also runs its trajectories in parallel internally. "
            "Tune down if hitting API rate limits."
        ),
    )
    return parser.parse_args()


if __name__ == "__main__":
    main(parse_args())
