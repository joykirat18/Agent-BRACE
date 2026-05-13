# [Agent-BRACE: Decoupling Beliefs from Actions in Long-Horizon Tasks via Verbalized State Uncertainty](https://arxiv.org/abs/2605.11436)

[![Paper](https://img.shields.io/badge/Paper-arXiv-red)](https://arxiv.org/abs/2605.11436)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[Joykirat Singh](https://joykirat18.github.io/) | [Zaid Khan](https://zaidkhan.me/) | [Archiki Prasad](https://archiki.github.io/) | [Justin Chih-Yao Chen](https://dinobby.github.io/) | [Akshay Nambi](https://www.microsoft.com/en-us/research/people/akshayn/) | [Hyunji Lee](https://amy-hyunji.github.io/) | [Elias Stengel-Eskin](https://esteng.github.io/) | [Mohit Bansal](https://www.cs.unc.edu/~mbansal/)

## Overview
This repository contains the implementation of Agent-BRACE (Agent Belief state Representation via Abstraction and Confidence Estimation), a method that decouples an LLM agent into a belief state model and a policy model, jointly optimized via reinforcement learning.

![Overview of Agent-BRACE](/assets/image.png)
The agent is decomposed into a belief state model $f_\phi$ and a policy model $\pi_\theta$, jointly optimized via PPO (dual training). At each step $t$, $f_\phi$ consumes the goal $G$, previous belief $b_{t}$, and new observation $o_{t+1}$ to produce an updated belief $b_{t+1}$ with WEPs-based certainty labels (Belief State Update). The policy $\pi_\theta$ then selects an action $a_t$ conditioned on $(G, b_{t+1}, o_{t+1})$ rather than the full history $\mathcal{H}_t$ (Action Selection). The belief model is trained with a composite reward $R^{\text{belief}}$, while the policy model is trained with a binary environment reward $R^{\text{env}}$.

---

## Installation

The codebase is built on top of [meow-tea-taro](https://github.com/pearls-lab/meow-tea-taro).

```bash
conda create -n agentic-rl python=3.10
conda activate agentic-rl

# Install vLLM first (GPU-specific build)
pip install vllm==0.8.5

# Install the package and remaining dependencies
pip install -e .
pip install -r requirements.txt
```

---

## Dataset Generation

The training pipeline requires two datasets: a **RL parquet dataset** (environment trajectories) and a **belief-state JSONL dataset** (GPT-labeled belief states used to pre-train the belief model via SFT before joint PPO training).

### Step 1 — Generate RL parquet data

Parquet generation has three sub-steps: generate game instance files, replay walkthroughs into JSONL, then convert JSONL to parquet. Pre-built parquet datasets for all environments are already provided in the `data-*-parquet/` directories and can be used directly — only follow these steps if you want to regenerate them.

#### 1a — Generate TextWorld game instances (`.z8` files)

Each task variant has its own generation script. Run from `meow_tea_experiments/data_generation/tasks/`:

```bash
# Quest (train: easy configs, val/test: harder configs)
sh meow_tea_experiments/data_generation/tasks/generate_textworld_basic_tasks.sh

# Cooking
sh meow_tea_experiments/data_generation/tasks/generate_textworld_cooking_tasks.sh

# Treasure Hunter
sh meow_tea_experiments/data_generation/tasks/generate_textworld_treasure_tasks.sh
```

Each script generates 1000 train / 100 validation / 200 test `.z8` game files into `textworld-task/<variant>-mixed/{train,valid,test}/`. Train instances use easier difficulty configs; validation and test use harder unseen configs to test generalization.


#### 1b — Replay walkthroughs into JSONL

For each split, replay gold walkthrough actions through the environment to produce JSONL trajectory files:

```bash
# Example: TextWorld basic-mixed (Quest)
python meow_tea_experiments/data_generation/generate_multiturn_data.py \
    --env_name textworld \
    --instance_dir meow_tea_experiments/data_generation/tasks/textworld-task/basic-mixed/train \
    --instance_id_range 10001 11000 \
    --task_prefix basic \
    --out_dir meow_tea_experiments/data_generation/textworld-basic-post-processing \
    --train_type ppo \
    --split train

python meow_tea_experiments/data_generation/generate_multiturn_data.py \
    --env_name textworld \
    --instance_dir meow_tea_experiments/data_generation/tasks/textworld-task/basic-mixed/valid \
    --instance_id_range 20001 20100 \
    --task_prefix basic \
    --out_dir meow_tea_experiments/data_generation/textworld-basic-post-processing \
    --train_type ppo \
    --split validation

python meow_tea_experiments/data_generation/generate_multiturn_data.py \
    --env_name textworld \
    --instance_dir meow_tea_experiments/data_generation/tasks/textworld-task/basic-mixed/test \
    --instance_id_range 30001 30200 \
    --task_prefix basic \
    --out_dir meow_tea_experiments/data_generation/textworld-basic-post-processing \
    --train_type ppo \
    --split test
```

Repeat with equivalent paths for `treasure-mixed` and `cooking-mixed`.

#### 1c — Convert JSONL to parquet

Convert the JSONL trajectory files into the parquet format expected by the RL trainer. The `--instances_dir_structure split` flag tells the processor that game files live in `train/`, `valid/`, `test/` subdirectories:

```bash
python -m meow_tea_train.agentic_utils.data_process.rl_local_data_processor \
    --env_name textworld \
    --data_dir meow_tea_experiments/data_generation/textworld-basic-post-processing \
    --instances_dir meow_tea_experiments/data_generation/tasks/textworld-task/basic-mixed \
    --instances_dir_structure split \
    --out_dir data-basic-parquet/ \
    --dataset_id basic_mixed \
    --reward_method single \
    --thinking_variant direct
```

Key arguments:

| Argument | Description |
|---|---|
| `--data_dir` | Directory containing `train.jsonl`, `validation.jsonl`, `test.jsonl` from step 1b |
| `--instances_dir` | Root of the game instance tree (with `train/`, `valid/`, `test/` subdirs) |
| `--instances_dir_structure` | `split` (subdirs per split) or `flat` (all instances in one dir) |
| `--out_dir` | Output directory; receives `train.parquet`, `validation.parquet`, `test.parquet` |
| `--dataset_id` | Identifier embedded in the parquet (e.g. `basic_mixed`, `cooking_mixed`, `treasure_mixed`) |
| `--thinking_variant` | Prompt format: `direct`, `MEM1`, `belief_state`, `goal_memory_freeform_bdi`, etc. |

### Step 2 — Generate belief-state dataset

This step calls an Azure OpenAI model (GPT-4.1-mini) to produce natural-language belief states for each step of gold and random trajectories. The output is a JSONL file used to SFT the belief model.

Set your Azure credentials:

```bash
export AZURE_OPENAI_API_KEY=<your-key>
export AZURE_OPENAI_ENDPOINT=<your-endpoint>
```

**TextWorld:**

```bash
python3 -m meow_tea_experiments.data_generation.generate_belief_state_dataset \
    --parquet_path      data-basic-parquet/train.parquet \
    --output_path       local/belief_dataset/train_belief.jsonl \
    --azure_api_version 2024-12-01-preview \
    --gpt_model         gpt-5.4-mini \
    --n_random_trajs    3 \
    --max_random_steps  15 \
    --random_seed_base  42 \
    --max_workers       8
```

### Step 3 — Fine-tune the belief model (SFT)

Train a Qwen2.5/3 model to predict belief states from the JSONL produced in Step 2. This SFT checkpoint is used as the belief model initialization before joint PPO training.

```bash
# Single or multi-GPU (auto-detected)
TRAIN_JSONL=local/belief_dataset/train_belief.jsonl \
OUTPUT_DIR=local/checkpoints/belief-sft-qwen3b \
sh recipes/finetune_belief_qwen25_3b.sh
```

After fine-tuning, merge the LoRA adapter into a standalone HF model:

```bash
python3 meow_tea_experiments/scripts/merge_lora_to_hf.py \
    --base_model   Qwen/Qwen2.5-3B-Instruct \
    --lora_path    local/checkpoints/belief-sft-qwen3b/checkpoint-final \
    --output_path  local/checkpoints/belief-merged
```

The merged checkpoint path is then passed to the PPO training recipe as the belief model.

---

## Training

All training is driven by `meow_tea_train.verl.trainer.main_ppo` with Hydra CLI overrides. Recipe scripts in `recipes/` encode all settings used in the reported experiments.

**GPU layout (3× A100 required for joint training):**

| GPU | Role |
|---|---|
| 0, 1 | Policy model — vLLM tensor-parallel rollout + FSDP PPO update |
| 2 | Belief model — vLLM inference subprocess + HF PPO update between rollouts |

> The trainer's `n_gpus_per_node` is set to 2 (not 3) because GPU 2 is reserved for the belief model and must not be counted in the PPO world size. `RAY_EXPERIMENTAL_NOSET_CUDA_VISIBLE_DEVICES=1` lets all workers still see GPUs 0–2.

### Prerequisites

1. A merged belief-model checkpoint from the SFT step (see [Dataset Generation](#dataset-generation)):
   ```bash
   export BELIEF_LM_TRAIN_PATH=/path/to/local/checkpoints/belief-merged
   ```

2. (Optional) WandB for experiment tracking:
   ```bash
   export WANDB_API_KEY='YOUR_WANDB_API_KEY'   # set to 'None' to disable
   ```

### Step 1 — Start the LLM reward judge

The reward is computed by a vLLM-served judge model (Qwen3-30B-A3B) that scores agent responses. Launch it on a spare GPU before starting training:

```bash
sh recipes/hostVLLM.sh
```

This starts an OpenAI-compatible server on port **8005** using `CUDA_VISIBLE_DEVICES=3`. The training recipe queries it for belief-state quality rewards.

### Step 2 — Run joint PPO training

**TextWorld (basic/cooking/treasure):**

```bash
sh recipes/textworld_basic_ppo_decouple_joint_belief_vllm.sh
```

Edit the `PROJECT CONFIG` block at the top of any recipe before running:

```bash
project_name="my-project"
experiment_name="my-run-name"
```

For TextWorld task variants, override `data.train_files` / `data.val_files` in the recipe to point to the appropriate `data-*-parquet/` directory.

### Baseline and ablation recipes

| Recipe | Description |
|---|---|
| `recipes/textworld_basic_ppo_direct.sh` | Direct action policy (no belief state) |
| `recipes/textworld_basic_ppo_react.sh` | ReAct-style chain-of-thought baseline |
| `recipes/textworld_basic_ppo_decouple_joint_belief_vllm.sh` | **AGENT-BRACE** (joint decoupled training) |

### Serving the belief model externally (optional)

Instead of running the belief model in-process on GPU 2, you can serve it via a separate vLLM OpenAI-compatible API and point the training recipe at it. This is useful if you want to share the belief server across multiple training runs.

```bash
# Merge LoRA first (if not already done)
ADAPTER_PATH=local/checkpoints/belief-sft-qwen3b/final_model \
OUTPUT_PATH=local/checkpoints/belief-sft-qwen3b/merged_model \
sh recipes/merge_belief_state_lora.sh

# Serve on port 8001 (GPU 0,1 by default)
MODEL_PATH=local/checkpoints/belief-sft-qwen3b/merged_model \
PORT=8001 \
sh recipes/serve_belief_state_model.sh
```

Then in the training recipe, replace the in-process belief config with:

```bash
belief_state_model_url="http://localhost:8001"
belief_state_model_name="belief-state"
```

---

## Evaluation

Evaluation runs a trained checkpoint on the test split using the same agentic rollout loop. Each training recipe has a corresponding `eval_*.sh`:

```bash
# TextWorld — evaluates a specific task and checkpoint version
TASK=basic VERSION=v1 \
BELIEF_LM_TRAIN_PATH=/path/to/belief-merged \
sh recipes/eval_textworld_basic_ppo_decouple_joint_belief_vllm.sh
```

| Env var | Default | Description |
|---|---|---|
| `TASK` | `basic` | TextWorld task split: `basic`, `cooking`, or `treasure` |
| `VERSION` | `v1` | Result directory suffix (prevents overwriting prior eval runs) |
| `BELIEF_LM_TRAIN_PATH` | — | Path to merged belief-model checkpoint |

Results are written as one `.jsonl` file per checkpoint step under `local/val_results/` (training) or `local/eval_val_results-*/` (evaluation). **Success rate** is the fraction of episodes with `reward == 1`.

---

## Repository Structure

```
.
├── meow_tea_train/                  # Core training framework
│   ├── agentic_menu/                # Per-environment agent implementations
│   │   ├── sync_textworld/          # TextWorld env + belief-state logic
│   │   ├── async_sweagent/          # SWE-agent async env wrapper
│   │   └── build_your_own/          # Template for adding new environments
│   ├── agentic_utils/               # Shared training utilities
│   │   ├── data_process/            # RL and SFT parquet data processors
│   │   ├── data_mapping/            # Prompt/response formatters per env
│   │   ├── reward_manager/          # Verified reward computation
│   │   └── rollout/                 # vLLM-based synchronous agentic rollout
│   ├── verl/                        # RL training engine (PPO/GRPO/RLOO)
│   │   └── trainer/                 # main_ppo.py entry point + Hydra configs
│   └── scripts/                     # process_rl_data.sh / process_sft_data.sh
├── meow_tea_gym/                    # Gym wrappers (SWE-agent integration)
├── meow_tea_experiments/            # Offline experiment tooling
│   ├── data_generation/             # Belief-state JSONL generators + parquet builders
│   └── scripts/                     # SFT fine-tuning + LoRA merge scripts
├── recipes/                         # Validated end-to-end training/eval configs (.sh)
├── examples/                        # Minimal quick-start scripts per environment
│   ├── textworld/                   # TextWorld PPO/SFT examples
│   └── swegym/                      # SWE-agent gym examples
├── scripts/                         # Analysis and result-counting utilities
├── analysis_figure/                 # Plotting scripts for paper figures
├── data-basic-parquet/              # TextWorld basic — train/val/test parquet
├── data-cooking-parquet/            # TextWorld cooking — train/val/test parquet
├── data-treasure-parquet/           # TextWorld treasure — train/val/test parquet
├── data-alfworld-parquet/           # AlfWorld — train/val/test parquet
├── data-*-parquet-MEM1/             # MEM1 thinking variant datasets
├── data-*-parquet-thinking/         # Extended thinking variant datasets
├── docs/                            # Sphinx documentation source
├── pyproject.toml                   # Package metadata
└── requirements.txt                 # Full pinned dependency list
```

---

## Citation

If you use AGENT-BRACE in your work, please cite:

```bibtex
@misc{singh2026agentbracedecouplingbeliefsactions,
      title={Agent-BRACE: Decoupling Beliefs from Actions in Long-Horizon Tasks via Verbalized State Uncertainty}, 
      author={Joykirat Singh and Zaid Khan and Archiki Prasad and Justin Chih-Yao Chen and Akshay Nambi and Hyunji Lee and Elias Stengel-Eskin and Mohit Bansal},
      year={2026},
      eprint={2605.11436},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2605.11436}, 
}
```
