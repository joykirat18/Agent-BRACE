#!/bin/bash

# Config variables
ENV_NAME="textworld" # Options: alfworld, textworld
TASK_PREFIX="tw_dense" # Prefix for task files
TASKS_DIR="/root/data/tasks/$ENV_NAME/$TASK_PREFIX"
mkdir -p $TASKS_DIR

# Textworld tasks settings
TW_BASE_SEED=10000
TW_TASKS_COUNT=10
# If using basic tasks
TW_BASIC_WORLD_SIZE=2
TW_BASIC_NB_OBJECTS=3
TW_BASIC_QUEST_LENGTH=4
# If using dense reward tasks
TW_DENSE_REWARD_TYPE="dense"

export ENV_NAME TASKS_DIR TW_BASE_SEED TW_TASKS_COUNT
export TW_BASIC_WORLD_SIZE TW_BASIC_NB_OBJECTS TW_BASIC_QUEST_LENGTH
export TW_DENSE_REWARD_TYPE

# Check if required arguments are provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 <env> [type]"
    echo "  env: alfworld, textworld"
    echo "  type (for textworld): dense, basic"
    exit 1
fi

env=$1
type=${2:-basic}
echo "Generating tasks for environment: $env, type: $type"

SCRIPT_DIR="meow_tea_experiments/data_generation/tasks"

if [ "$env" == "textworld" ]; then
    if [ "$type" == "dense" ]; then
        echo "Generating dense reward TextWorld tasks..."
        bash $SCRIPT_DIR/generate_textworld_dense_tasks.sh
    elif [ "$type" == "basic" ]; then
        echo "Generating basic TextWorld tasks..."
        bash $SCRIPT_DIR/generate_textworld_basic_tasks.sh
    else
        echo "Unknown type for textworld: $type. Use 'dense' or 'basic'."
        exit 1
    fi
elif [ "$env" == "alfworld" ]; then
    echo "Downloading AlfWorld tasks..."
    bash $SCRIPT_DIR/download_alfworld_tasks.sh
else
    echo "Unknown environment: $env. Use 'alfworld' or 'textworld'."
    exit 1
fi

echo "Task generation completed!"