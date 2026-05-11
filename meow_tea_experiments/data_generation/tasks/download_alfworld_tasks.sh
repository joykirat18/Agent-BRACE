ALFWORLD_DOWNLOAD_URL="https://github.com/alfworld/alfworld/releases/download/0.4.2/json_2.1.3_tw-pddl.zip"
tasks_dir=/home/user/textworld-RL/meow_tea_experiments/data_generation/tasks/alfworld-task

wget $ALFWORLD_DOWNLOAD_URL -O $tasks_dir/alfworld_data.zip 
unzip $tasks_dir/alfworld_data.zip -d $tasks_dir
rm -rf $tasks_dir/alfworld_data.zip

python3 -m meow_tea_experiments.data_generation.utils.process_alfworld_tasks \
    --data_dir $tasks_dir/json_2.1.1 \
    --split train \
    --out_dir $tasks_dir

python3 -m meow_tea_experiments.data_generation.utils.process_alfworld_tasks \
    --data_dir $tasks_dir/json_2.1.1 \
    --split valid_seen \
    --out_dir $tasks_dir

python3 -m meow_tea_experiments.data_generation.utils.process_alfworld_tasks \
    --data_dir $tasks_dir/json_2.1.1 \
    --split valid_unseen \
    --out_dir $tasks_dir

rm -rf $TASKS_DIR/json_2.1.1