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


def textworld_make_map_fn(split, instances_dir, dataset_id, reward_method, thinking_variant):
    """
    Create a mapping function for processing TextWorld dataset examples.
    """
    
    def process_fn(example, idx):
        # breakpoint()
        goal_prompt = example["prompt"].split('Here is your interactions so far:\ncurrent state:')[0].strip()
        current_state = example['prompt'].split('Here is your interactions so far:\ncurrent state:')[1].replace('your action: ', '').strip()
        # breakpoint()
        if thinking_variant == "step-by-step":
            prompt = goal_prompt + "\n\ncurrent state: " + current_state + "\n\nLet's think step by step inside the <thinking> </thinking> tags and output the final action within <action> </action> tags."
        elif thinking_variant == "direct":
            prompt = goal_prompt + "\n\ncurrent state: " + current_state + "\n\nOutput the final action directly within <action> </action> tags."
        elif thinking_variant == "belief_state":
            prompt = goal_prompt + "\n\ncurrent state: " + current_state + """\n\nOutput your belief state within <belief_state> </belief_state> tags, then output the final action within <action> </action> tags.

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
        elif thinking_variant == "simple_belief_state":
            prompt = goal_prompt + "\n\ncurrent state: " + current_state + "\n\nOutput your belief state within <belief_state> </belief_state> tags, then output the final action within <action> </action> tags."
        elif thinking_variant == "memory_belief_state":
            prompt = goal_prompt + "\n\ncurrent state: " + current_state + """\n\nOutput your belief state within <belief_state> </belief_state> tags, then think step by step inside <thinking> </thinking> tags, then output the final action within <action> </action> tags.

In the belief state, describe in natural language what you know about the current world state — where you are, what rooms and connections you have found, what objects you have seen and their states, and which goal steps are complete. Capture uncertainty directly in your words: use terms like "certain", "likely", "probable", "possibly", "uncertain", "unlikely", or "unknown" to reflect how confident you are about each fact."""
        elif thinking_variant == "goal_memory_belief_state":
            prompt = goal_prompt + "\n\ncurrent state: " + current_state + """\n\nUsing the goal description above, your previous belief state (if any), and the current observation, construct an updated belief state and take the next action.

Output your updated belief state within <belief_state> </belief_state> tags, then output the final action within <action> </action> tags.

In the belief state, describe in natural language what you know about the current world state — where you are, what rooms and connections you have found, what objects you have seen and their states, and which goal steps are complete. Capture uncertainty directly in your words: use terms like "certain", "likely", "probable", "possibly", "uncertain", "unlikely", or "unknown" to reflect how confident you are about each fact."""
        elif thinking_variant == "goal_memory_history_summary":
            prompt = goal_prompt + "\n\ncurrent state: " + current_state + """\n\nUsing the goal description above, your previous belief state (if any), and the current observation, summarize what you have observed so far, then take the next action.

Output a factual summary of your past observations within <belief_state> </belief_state> tags, then output the final action within <action> </action> tags.

Write the summary as natural flowing text. Record only confirmed facts from what you have already seen and done — where you are, which rooms and connections you have visited, what objects you have observed and in what state, which actions you took and what happened, and which goal steps are already complete. Do not include plans, guesses, or anything you have not directly observed."""
        elif thinking_variant == "goal_memory_freeform_bdi":
            prompt = goal_prompt + "\n\ncurrent state: " + current_state + """\n\nUsing the goal description above, your previous belief state (if any), and the current observation, update your understanding and take the next action.

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
        elif thinking_variant == "MEM1":
            prompt = goal_prompt + """\n\nAt each step, you will receive the current state within <state></state>, the previous cumulative memory within <summary></summary> (except for the first step), and your last action within <answer></answer> (except for the first step). NEVER generate or modify the <state>; use it exactly as provided.

Respond strictly using the following format:
<thinking>...</thinking>
<summary>...</summary>
<answer>...</answer>

Guidelines:
- <thinking>: Clearly reason about relevant details and briefly plan your next step.
- <summary>: Maintain and update a concise, cumulative memory of all essential information by integrating current <state> with previous <summary>. This is your only persistent memory. It should serve as a growing internal monologue that accumulates useful observations, actions taken, and insights from all previous and current steps, while removing redundant or outdated details to stay focused on finding and buying the correct product.
- <answer>: Select your next action strictly from the Available Actions explicitly listed within the provided <state>. Use ONLY valid action formats like search[<keywords>] or click[<option>]. Click buy now when the right product is found and the buy now button is available.

Task begins with:\n<state>""" + current_state + """</state>\n"""
        else:
            raise ValueError(f"Invalid thinking variant: {thinking_variant}")
        data = {
            "data_source": f"textworld_{dataset_id}",
            "prompt": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "reward_model": {
                "style": "rule", 
                "ground_truth": f"{example['task_prefix']}_{example['instance_id']}"
            },
            "extra_info": {
                "split": split,
                "index": idx,
                "response": example["response"],
                "prompt": prompt,
                "instance_path": instances_dir,
                "instance_file": f"{example['task_prefix']}_{example['instance_id']}",
                "reward_method": reward_method
            },
        }
        return data

    return process_fn
