Quick Installation Guide
========================


Requirements
------------
* **Python** >= 3.10
* **CUDA** >= 12.6

We support **vLLM** (version >= 0.8.4) for rollout generation and **FSDP** for SFT and RL training.

Install from Docker (Recommended)
---------------------------------
The following steps will help you quickly set up the **meow-tea-taro** package using Docker.

1. **Launch a Docker Container**

   Start by creating and running a Docker container with GPU support (make sure you have `NVIDIA Docker <https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html>`_ installed):

   .. code-block:: bash

      docker create --runtime=nvidia --gpus all --net=host --shm-size="10g" --cap-add=SYS_ADMIN -v .:/workspace --name meow-tea-taro <image:tag> sleep infinity
      docker start meow-tea-taro
      docker exec -it meow-tea-taro bash

   
   Replace ``<image:tag>`` with the desired Docker image.

   The stable Docker image with the minimum requirements (vLLM, FSDP) for meow-tea-taro is: ``hiyouga/verl:ngc-th2.6.0-cu126-vllm0.8.4-flashinfer0.2.2-cxx11abi0``.

   Feel free to use other images that support vLLM and FSDP from the `verl documentation <https://verl.readthedocs.io/en/latest/start/install.html#application-image>`_.

2. **Clone the Repository**

   Inside the container, clone the latest meow-tea-taro repository:

   .. code-block:: bash

      git clone [ANONYMIZED_URL]
      cd meow-tea-taro

3. **Install in Editable Mode**

   We recommend installing the package and its dependencies using pip in editable mode.

   The meow-tea-taro package provides **an easily adaptable agentic framework where you can build your own agentic tasks and train multi-turn RL upon it**. This command installs ``meow-tea-taro`` in a way that reflects code changes immediately and makes your adaptations importable across the codebase.

   .. code-block:: bash

      pip install -e .


**You're all set!**  
You can now run tutorials and training scripts as described in the subsequent documentation sections.

