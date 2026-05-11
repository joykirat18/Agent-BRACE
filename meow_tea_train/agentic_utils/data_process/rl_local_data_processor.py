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
import json
import argparse
import pandas as pd
import glob
import tarfile
from datasets import Dataset
from meow_tea_train.agentic_utils.data_mapping.rl_data_mapping import textworld_make_map_fn

# Map split names to instance subdirectory names (e.g. "validation" -> "valid")
SPLIT_TO_INSTANCE_SUBDIR = {
    "train": "train",
    "validation": "valid",
    "test": "test",
}


def extract_instances_files(instances_dir):
    """Extract all tar.gz files in the instances directory (and subdirs)."""
    print(f"Looking for tar files in: {instances_dir}")
    tar_files = glob.glob(os.path.join(instances_dir, "**", "*.tar.gz"), recursive=True)
    if not tar_files:
        tar_files = glob.glob(os.path.join(instances_dir, "*.tar.gz"))
    if not tar_files:
        print("No tar.gz files found, skipping extraction")
        return
    print(f"Found {len(tar_files)} tar files")
    for tar_file in tar_files:
        if os.path.isfile(tar_file):
            extract_dir = os.path.dirname(tar_file)
            print(f"Extracting {os.path.basename(tar_file)}...")
            with tarfile.open(tar_file, "r:gz") as tar:
                tar.extractall(path=extract_dir)
            print(f"Deleting {os.path.basename(tar_file)}...")
            os.remove(tar_file)


def get_instances_dir_for_split(instances_dir, split, instances_dir_structure):
    """Get the instances directory for a given split."""
    if instances_dir_structure == "flat":
        return os.path.abspath(instances_dir)
    elif instances_dir_structure == "split":
        subdir = SPLIT_TO_INSTANCE_SUBDIR.get(split, split)
        return os.path.abspath(os.path.join(instances_dir, subdir))
    else:
        raise ValueError(f"Unknown instances_dir_structure: {instances_dir_structure}")


def process_rl_data(
    env_name,
    dataset_id,
    instances_dir,
    data_dir,
    out_dir,
    reward_method,
    thinking_variant,
    instances_dir_structure="flat",
):
    """Process RL training data from local jsonl files and save as parquet."""
    print(f"Processing RL data for {env_name}...")

    datasets = {}
    for split in ["train", "validation", "test"]:
        filepath = os.path.join(data_dir, f"{split}.jsonl")
        if not os.path.exists(filepath):
            print(f"Skipping {split}: {filepath} not found")
            continue
        with open(filepath, "r") as f:
            data = [json.loads(line) for line in f]
        if not data:
            print(f"Skipping {split}: no data in {filepath}")
            continue
        datasets[split] = Dataset.from_pandas(pd.DataFrame(data))
        print(f"Loaded {split}: {len(datasets[split])} examples from {filepath}")

    if not datasets:
        raise FileNotFoundError(
            f"No jsonl files found in {data_dir}. Expected train.jsonl, validation.jsonl, test.jsonl"
        )

    # Apply task-specific mapping with split-specific instances_dir
    if env_name in ["textworld", "alfworld"]:
        for split in datasets:
            split_instances_dir = get_instances_dir_for_split(
                instances_dir, split, instances_dir_structure
            )
            map_fn = textworld_make_map_fn(
                split, split_instances_dir, dataset_id, reward_method, 
                thinking_variant
            )
            datasets[split] = datasets[split].map(function=map_fn, with_indices=True)
    else:
        raise NotImplementedError(f"Environment {env_name} not implemented")

    # Save as parquet
    os.makedirs(out_dir, exist_ok=True)
    for split, dataset in datasets.items():
        output_path = os.path.join(out_dir, f"{split}.parquet")
        dataset.to_parquet(output_path)
        print(f"Saved {split} dataset to {output_path}")

    if "train" in datasets:
        print("Sample from train dataset:", datasets["train"][0])


def main():
    parser = argparse.ArgumentParser(
        description="Process local multiturn RL data (train, validation, test) into parquet format."
    )
    parser.add_argument("--env_name", type=str, required=True, choices=["textworld", "alfworld"])
    parser.add_argument(
        "--data_dir",
        type=str,
        required=True,
        help="Directory containing train.jsonl, validation.jsonl, test.jsonl",
    )
    parser.add_argument(
        "--instances_dir",
        type=str,
        required=True,
        help="Directory containing instance files (.z8 or .tw-pddl). Use instances_dir_structure for layout.",
    )
    parser.add_argument(
        "--instances_dir_structure",
        type=str,
        default="split",
        choices=["flat", "split"],
        help="flat: all instances in one dir. split: instances in train/, valid/, test/ subdirs (e.g. cooking-mixed).",
    )
    parser.add_argument(
        "--out_dir",
        type=str,
        default="local/train_parquet",
        help="Output directory for parquet files.",
    )
    parser.add_argument(
        "--dataset_id",
        type=str,
        default="local",
        help="Dataset identifier for data_source (e.g. cooking_mixed).",
    )
    parser.add_argument(
        "--reward_method",
        type=str,
        default="single",
        choices=["dense", "single"],
    )
    parser.add_argument(
        "--extract_tars",
        action="store_true",
        help="Extract .tar.gz files in instances_dir before processing.",
    )
    parser.add_argument(
        "--thinking_variant",
        type=str,
        default="direct",
        choices=["direct", "step-by-step", "belief_state", "memory_belief_state", "goal_memory_belief_state", "goal_memory_history_summary", "goal_memory_freeform_bdi", "MEM1"],
        help="direct: always use direct action. step-by-step: use thinking or dynamic selection. belief_state: always use belief_state + action.",
    )
    args = parser.parse_args()

    if args.extract_tars:
        extract_instances_files(args.instances_dir)

    process_rl_data(
        env_name=args.env_name,
        dataset_id=args.dataset_id,
        instances_dir=args.instances_dir,
        data_dir=args.data_dir,
        out_dir=args.out_dir,
        reward_method=args.reward_method,
        thinking_variant=args.thinking_variant,
        instances_dir_structure=args.instances_dir_structure,
    )


if __name__ == "__main__":
    main()