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
import shutil
import glob
import tarfile
from datasets import Dataset
from huggingface_hub import snapshot_download
from meow_tea_train.agentic_utils.data_mapping.rl_data_mapping import textworld_make_map_fn


def download_from_hf(repo_id, local_dir, hf_target_folder, repo_type):
    """Download specific folder from HuggingFace repository."""
    print(f"Downloading {hf_target_folder} from {repo_id}...")
    snapshot_download(
        repo_id=repo_id,
        local_dir=local_dir,
        allow_patterns=[f"{hf_target_folder}/*"],
        token=os.environ.get("HF_TOKEN"),
        repo_type=repo_type
    )


def extract_instances_files(instances_dir):
    """Extract all tar.gz files in the instances directory."""
    print(f"Looking for tar files in: {instances_dir}")
    
    # List all tar.gz files
    tar_files = glob.glob(os.path.join(instances_dir, "*.tar.gz"))
    
    if not tar_files:
        print("No tar.gz files found")
        return
    
    print(f"Found {len(tar_files)} tar files")
    
    for tar_file in tar_files:
        if os.path.isfile(tar_file):
            print(f"Extracting {os.path.basename(tar_file)}...")
            with tarfile.open(tar_file, 'r:gz') as tar:
                tar.extractall(path=instances_dir)
            print(f"Deleting {os.path.basename(tar_file)}...")
            os.remove(tar_file)


def process_rl_data(env_name, dataset_id, instances_dir, data_dir, local_dir, reward_method, thinking_variant="direct"):
    """Process RL training data and save as parquet files."""
    print(f"Processing RL data for {env_name}...")

    # Load datasets
    datasets = {}
    for split in ["train", "validation", "test"]:
        filepath = os.path.join(data_dir, f"{split}.jsonl")
        with open(filepath, 'r') as f:
            data = [json.loads(line) for line in f]
        datasets[split] = Dataset.from_pandas(pd.DataFrame(data))

    # Apply task-specific mapping
    if env_name in ["textworld", "alfworld"]:
        for split in datasets:
            map_fn = textworld_make_map_fn(split, instances_dir, dataset_id, reward_method, thinking_variant)
            datasets[split] = datasets[split].map(function=map_fn, with_indices=True)
    else:
        raise NotImplementedError(f"Environment {env_name} not implemented")
    
    # Save as parquet
    os.makedirs(local_dir, exist_ok=True)
    for split, dataset in datasets.items():
        output_path = os.path.join(local_dir, f"{split}.parquet")
        dataset.to_parquet(output_path)
        print(f"Saved {split} dataset to {output_path}")
    
    print("Sample from train dataset:", datasets["train"][0])


def main():
    parser = argparse.ArgumentParser(description="Process multiturn RL data")
    parser.add_argument("--env_name", type=str, required=True)
    parser.add_argument("--task_prefix", type=str, required=True)
    parser.add_argument("--instance_id_range", type=int, nargs=2, required=True, metavar=("START", "END"), help="Instance ID range [start, end], inclusive.")
    parser.add_argument("--hf_data_repo", type=str, required=True)
    parser.add_argument("--hf_instances_dir", type=str, default="instances")
    parser.add_argument("--hf_train_data_dir", type=str, default="multiturn_rl_data")
    parser.add_argument("--local_instances_dir", type=str, default="local/instances")
    parser.add_argument("--local_train_data_dir", type=str, default="local/multiturn_rl_data")
    parser.add_argument("--local_parquet_dir", type=str, default="local/train_parquet")
    parser.add_argument("--reward_method", type=str, default="single",
                       choices=["dense", "single"])
    parser.add_argument("--thinking_variant", type=str, default="direct",
                       choices=["direct", "step-by-step", "belief_state", "memory_belief_state",
                                "goal_memory_belief_state", "goal_memory_history_summary",
                                "goal_memory_freeform_bdi", "MEM1"])

    args = parser.parse_args()

    # Create dataset ID
    dataset_id = f"{args.task_prefix}_{args.instance_id_range[0]}-{args.instance_id_range[1]}"

    # Step 1: Download data
    # download_from_hf(args.hf_data_repo, "local", args.hf_instances_dir, "dataset")
    # download_from_hf(args.hf_data_repo, "local", args.hf_train_data_dir, "dataset")

    # Step 2: Extract instance files (MUST be before processing RL data)
    extract_instances_files(args.local_instances_dir)

    # Step 3: Process RL data (requires extracted instance files)
    process_rl_data(args.env_name, dataset_id, args.local_instances_dir,
                    args.local_train_data_dir, args.local_parquet_dir, args.reward_method,
                    args.thinking_variant)
    
    # # Step 4: Cleanup
    cache_dir = "local/.cache/"
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
        print("Cleaned up cache directory")


if __name__ == "__main__":
    main()