import glob
import argparse
import os
import shutil


def main(args):
    find_dir = os.path.join(args.data_dir, args.split, "**", "*.tw-pddl")
    pddl_files = glob.glob(find_dir, recursive=True)

    for i in range(len(pddl_files)):
        file = pddl_files[i]
        shutil.move(file, os.path.join(args.out_dir, f"alfworld_{args.split}_{i+1}.tw-pddl"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process alfworld tasks.")
    parser.add_argument("--data_dir", type=str, required=True, help="Data directory for raw alfworld data.")
    parser.add_argument("--split", type=str, required=True, choices=["train", "valid_seen", "valid_train", "valid_unseen"], help="The data split of alfworld.")
    parser.add_argument("--out_dir", type=str, required=True, help="Output directory for processed alfworld games.")
    
    args = parser.parse_args()
    main(args)
