import subprocess

def sh(cmd:str):
    print(f"\n$ {cmd}")
    p=subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)

repo='/var/lib/ilanmironov@edu.hse.ru/hallo2'
venv='.venv_hallo2_20260215_133957'
run='preview_20260215_141828'

cmd=f"""
set -euo pipefail
cd {repo}

mkdir -p preview_runs/{run}/configs preview_runs/{run}/outputs/male preview_runs/{run}/outputs/female logs

# Create per-run configs (reduce steps for speed)
cp configs/inference/long.yaml preview_runs/{run}/configs/male.yaml
cp configs/inference/long.yaml preview_runs/{run}/configs/female.yaml

# Override paths + output roots
sed -i "s|^source_image: .*|source_image: ./preview_runs/{run}/inputs/images/094.jpg|" preview_runs/{run}/configs/male.yaml
sed -i "s|^driving_audio: .*|driving_audio: ./preview_runs/{run}/inputs/audios/094.wav|" preview_runs/{run}/configs/male.yaml
sed -i "s|^save_path: .*|save_path: ./preview_runs/{run}/outputs/male/|" preview_runs/{run}/configs/male.yaml
sed -i "s|^inference_steps: .*|inference_steps: 20|" preview_runs/{run}/configs/male.yaml

sed -i "s|^source_image: .*|source_image: ./preview_runs/{run}/inputs/images/005.jpg|" preview_runs/{run}/configs/female.yaml
sed -i "s|^driving_audio: .*|driving_audio: ./preview_runs/{run}/inputs/audios/005.wav|" preview_runs/{run}/configs/female.yaml
sed -i "s|^save_path: .*|save_path: ./preview_runs/{run}/outputs/female/|" preview_runs/{run}/configs/female.yaml
sed -i "s|^inference_steps: .*|inference_steps: 20|" preview_runs/{run}/configs/female.yaml

# Start both runs on free GPUs
nohup bash -lc 'set -euo pipefail; \
  echo START $(date -Is); \
  export CUDA_VISIBLE_DEVICES=2; export MPLBACKEND=Agg; export PYTHONUNBUFFERED=1; \
  ./{venv}/bin/python scripts/inference_long.py --config preview_runs/{run}/configs/male.yaml --audio_ckpt_dir pretrained_models/hallo2; \
  echo DONE $(date -Is)' > logs/preview_male_{run}.log 2>&1 < /dev/null &

echo $! > logs/preview_male_{run}.pid

nohup bash -lc 'set -euo pipefail; \
  echo START $(date -Is); \
  export CUDA_VISIBLE_DEVICES=3; export MPLBACKEND=Agg; export PYTHONUNBUFFERED=1; \
  ./{venv}/bin/python scripts/inference_long.py --config preview_runs/{run}/configs/female.yaml --audio_ckpt_dir pretrained_models/hallo2; \
  echo DONE $(date -Is)' > logs/preview_female_{run}.log 2>&1 < /dev/null &

echo $! > logs/preview_female_{run}.pid

echo RUN {run}
echo MALE_PID $(cat logs/preview_male_{run}.pid)
echo FEMALE_PID $(cat logs/preview_female_{run}.pid)
"""

sh(cmd)
sh('nvidia-smi | sed -n "1,120p"')