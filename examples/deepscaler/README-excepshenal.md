## Quickstart

```bash
sudo apt-get update && sudo apt install python3-pip && pip install huggingface_hub

git clone https://github.com/excepshenal/verl.git
cd verl
python3 scripts/download_model.py --local_dir ~/models/ds-r1-distill-qwen-1.5b
cd ..
rm -rf verl

pip uninstall huggingface_hub
```

START HERE?

```bash
git clone --recurse-submodules https://github.com/excepshenal/rllm.git
cd rllm
git switch dshen-deepscaler

# Build the Docker image
docker build -t rllm .

# Create and start the container
docker create --runtime=nvidia --gpus all --ipc=host --net=host --cap-add=SYS_ADMIN -v .:/workspace/rllm -v /tmp:/tmp -v ~/models:/models --name rllm-container rllm sleep infinity
docker start rllm-container

# Enter the container
docker exec -it rllm-container bash
```

```bash
cd rllm
python3 verl/scripts/download_model.py
python3 verl/scripts/download_model.py --hf_repo sfairXC/FsfairX-LLaMA3-RM-v0.1 --local_dir /models/FsfairX-LLaMA3-RM-v0.1
python3 examples/deepscaler/prepare_math_data.py
```

Edit `rllm/trainer/verl/ray_runtime_env.py` to pass your `WANDB_API_KEY` to Ray:

```bash
# Look for "env_vars" under PPO_RAY_RUNTIME_ENV and add "WANDB_API_KEY": "<your_wandb_api_key>"
vim rllm/trainer/verl/ray_runtime_env.py
```

```bash
ray start --head

bash examples/deepscaler/train_deepscaler_8k.sh

# modify MODEL_PATH to the 8k checkpoint path before running the script.
bash examples/deepscaler/train_deepscaler_16k.sh

# modify MODEL_PATH to the 16k checkpoint path before running the script
bash examples/deepscaler/train_deepscaler_24k.sh
```