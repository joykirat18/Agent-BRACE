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
from huggingface_hub import snapshot_download


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


def process_sft_data(data_dir, local_dir):
    """Process SFT training data and save as parquet files."""
    with open(os.path.join(data_dir, "train.json"), 'r') as f:
        train_dataset = json.load(f)
    with open(os.path.join(data_dir, "validation.json"), 'r') as f:
        val_dataset = json.load(f)
    with open(os.path.join(data_dir, "test.json"), 'r') as f:
        test_dataset = json.load(f)

    os.makedirs(local_dir, exist_ok=True)
    pd.DataFrame(train_dataset).to_parquet(os.path.join(local_dir, "train.parquet"))
    pd.DataFrame(val_dataset).to_parquet(os.path.join(local_dir, "validation.parquet"))
    pd.DataFrame(test_dataset).to_parquet(os.path.join(local_dir, "test.parquet"))


def main():
    parser = argparse.ArgumentParser(description="Process multiturn SFT data")
    parser.add_argument("--hf_data_repo", type=str, required=True)
    parser.add_argument("--hf_train_data_dir", type=str, default="multiturn_sft_data")
    parser.add_argument("--local_train_data_dir", type=str, default="local/multiturn_sft_data")
    parser.add_argument("--local_parquet_dir", type=str, default="local/train_parquet")

    args = parser.parse_args()
    
    # Step 1: Download data
    download_from_hf(args.hf_data_repo, "local", args.hf_train_data_dir, "dataset")

    # Step 2: Process SFT data
    process_sft_data(args.local_train_data_dir, args.local_parquet_dir)

    # Step 4: Cleanup
    cache_dir = "local/.cache/"
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
        print("Cleaned up cache directory")


if __name__ == "__main__":
    main()