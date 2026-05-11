Quick Start: Training Multi-turn PPO on TextWorld tasks
=======================================================

This guide walks you through training a multi-turn PPO agent on TextWorld tasks using the example script ``meow-tea-taro/examples/textworld/run_ppo_qwen-1.5b.sh``.

Prepare Environment Instances and Training Data
-------------------------------------------------

We share the pre-generated **environment instances** and **multi-turn RL datasets** used in our experiments in the HuggingFace repo: `[ANONYMIZED_HF_DATASET] <https://huggingface.co/datasets/[ANONYMIZED_HF_DATASET]/tree/main>`_. 

.. tip::
   Want to create custom environments and datasets? See our data generation pipeline guide at **!!placeholder!!**

To specify the environment, task, and data you would like to use, configure the following parameters in ``run_ppo_qwen-1.5b.sh``:

.. code-block:: bash

    # DATA/TASK CONFIG
    env_name="textworld" 
    task_prefix="w2-o3-q4"
    instance_id_start=50001
    instance_id_end=51000
    hf_data_repo="[ANONYMIZED_HF_DATASET]"
    hf_instances_dir="textworld/w2-o3-q4/instances"
    hf_train_data_dir="textworld/w2-o3-q4/multiturn_rl_data/1000_train_data"
    local_instances_dir="local/$hf_instances_dir"
    local_train_data_dir="local/$hf_train_data_dir"
    local_parquet_dir="local/train_parquet"
    reward_method="single"

Configuration breakdown
~~~~~~~~~~~~~~~~~~~~~~~~

* **Environment**: ``textworld`` - The task environment
* **Task**: ``w2-o3-q4`` - Task difficulty specification (world size 2, object size 3, quest length 4)
* **Instance range**: 50001-51000 - Uses 1000 unique game instances
* **Training data size**: 1000 rollouts for PPO training
* **Reward method/density**: ``single`` - The task only supports giving a reward at the game end.

After downloading from HuggingFace, your local directory structure will look like:
::

    local/
    └── textworld/
        └── w2-o3-q4/
            ├── instances/
            │   ├── w2-o3-q4_1.z8
            │   ├── w2-o3-q4_2.z8
            │   └── ...
            └── multiturn_rl_data/
                └── 1000_train_data/
                    └── train.jsonl
                    ├── validation.jsonl
                    └── test.jsonl

Game Instances (``*.z8`` files)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Files in the ``instances/`` directory are `TextWorld game files <https://textworld.readthedocs.io/en/stable/notes/framework.html>`_ in PDDL format.

These files are executable during multi-turn rollout, allowing the agent to interact with the environment dynamically.


Training Data (``*.jsonl``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Each line in ``*.jsonl`` is a JSON object representing one training example. An example includes the initial task prompts, the correct actions (responses) separated by the end-of-sequence token, and some meta information

Here's an example entry from ``test.jsonl``:

.. code-block:: json

    {
      "prompt": "You are an expert TextWorld game solver. Your goal is to generate the best next action that will lead to winning the game.\n\nEnd your output sequence with an action starting with a verb. Example: open box.\n\nHere is how to win the game:\nHey, thanks for coming over to the TextWorld today, there is something I need you to do for me. First thing I need you to do is to move south. Then, venture east. And then, make an attempt to go to the north. With that over with, recover the top hat from the shelf within the attic. And if you do that, you're the winner!\n\nHere is your interactions so far:\ncurrent state: You are now in the sauna.\nYou are in a sauna. A typical one.\nThere is an unblocked exit to the east. There is an exit to the north. Don't worry, it is unguarded. You don't like doors? Why not try going south, that entranceway is unblocked.\nYou are carrying nothing.\n\nyour action: ",
      "response": "go south<|im_end|>go east<|im_end|>go north<|im_end|>take top hat from shelf<|im_end|>",
      "task_prefix": "w2-o3-q4",
      "instance_id": 45
    }



Configure Training Parameters and Launch training
-------------------------------------------------

Now you're ready to configure the training parameters and launch agentic multi-turn RL training.

Step 1: Configure Base Models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specify the base model for both actor and critic networks. If you don't have custom pretrained models, set only the ``base_model`` field with a HuggingFace model path:

.. code-block:: bash

    # MODEL CONFIG
    hf_actor_repo_id=""
    hf_actor_model_path=""
    hf_critic_repo_id=""
    hf_critic_model_path=""
    actor_model_path=local/model/actor
    critic_model_path=local/model/critic
    base_model="Qwen/Qwen2.5-1.5B-Instruct"

.. tip::
   Leave the HuggingFace repository fields empty unless you're loading custom pretrained models. The ``base_model`` will be used to initialize both actor and critic.


Step 2: Configure Agentic Rollout
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These settings control how the agent interacts with the environment during rollout:

.. code-block:: bash

    # AGENTIC CONFIG
    # env_name=... # from previous configuration
    is_multiturn=True
    is_async=False
    max_iter=8
    reward_density=$reward_method
    reward_type="verified"
    reward_manager="agentic_verified"  # Fixed for now
    rollout_name="vllm_agentic"        # Fixed for now

**Key parameters:**

* ``max_iter``: Maximum number of agent-environment interactions per episode

* ``reward_type``: Set to ``"verified"`` because we use a reward function that checks whether the agent successfully completes the game

* ``is_multiturn``: Enable multi-turn interaction mode (required for agentic tasks)

Step 3: Configure PPO Hyperparameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tune the PPO training algorithm parameters:

.. code-block:: bash

    # ALGORITHM CONFIG
    adv_estimator=gae
    gamma=1.0

    use_kl_loss=False         # Whether to use KL loss in objective (True for GRPO)
    use_kl_in_reward=True     # Whether to use KL divergence in reward calculation (True for PPO)
    kl_coef=0.01 
    clip_ratio=0.2

.. note::
   Feel free to experiment with different ``clip_ratio`` and ``kl_coef`` values to balance exploration and stability.


Step 4: Configure Training Details
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Set the training loop parameters, batch sizes, and model constraints:

.. code-block:: bash

    # TRAINING CONFIG
    rollout_temp=0.7           # vLLM temperature during online rollout
    val_rollout_temp=0.4       # Lower temperature for validation (more deterministic)
    train_batch_size=256
    ppo_mini_batch_size=256
    max_num_batched_tokens=8192
    gpu_memory_utilization=0.8
    max_prompt_length=3072
    max_response_length=3072
    actor_lr=1e-6
    critic_lr=1e-5
    nnodes=1
    num_epochs=40
    save_freq=40               # Save checkpoint every N steps
    test_freq=5                # Run validation every N steps

**Sequence length considerations:**

The typical prompt length for TextWorld tasks in our experiments is around 4K tokens, and ``max_prompt_length=3072`` and ``max_response_length=3072`` are sufficient for iterations < 12.

**Checkpoint and validation frequency:**

* ``save_freq``: Checkpoints are saved every X steps (not epochs)
* ``test_freq``: Validation runs every X steps


Step 5: Configure Logging and Model Saving (Optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Enable WandB logging and automatic HuggingFace uploads for experiment tracking and checkpoint recovery:

.. code-block:: bash

    # PROJECT CONFIG
    project_name=""             # WandB project name
    experiment_name=""          # WandB experiment name
    save_hf_repo_id=""          # HF repo ID to save trained models (leave empty to disable)
    resume_wandb_logs=True      # Resume WandB logs if experiment_name exists

.. important::
   **Highly recommended for long training runs!** Saving intermediate checkpoints to HuggingFace allows you to resume training from any point if interrupted.


Launch Training
---------------

**You're all set!** Start training with:

.. code-block:: bash

    bash examples/textworld/run_ppo_qwen-1.5b.sh

**Expected runtime:** On 8x H100 GPUs, training completes in approximately **45 minutes**.
