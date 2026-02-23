import subprocess

script = r"""
set -euo pipefail
REPO=/var/lib/ilanmironov@edu.hse.ru/musetalk
rm -f $REPO/.preview_exit
LOG=$REPO/preview_generation_gpu1.log
CMD='export MPLBACKEND=Agg; source /var/lib/ilanmironov@edu.hse.ru/venvs/musetalk/bin/activate; cd /var/lib/ilanmironov@edu.hse.ru/musetalk; python -m scripts.inference --inference_config configs/inference/preview_user.yaml --result_dir results/preview --unet_model_path models/musetalkV15/unet.pth --unet_config models/musetalkV15/musetalk.json --version v15 --gpu_id 1 --use_float16 --batch_size 8; echo $? > /var/lib/ilanmironov@edu.hse.ru/musetalk/.preview_exit'
nohup bash -lc "$CMD" > "$LOG" 2>&1 &
echo "preview_pid=$!"
echo "preview_log=$LOG"
"""

p = subprocess.run(["bash", "-lc", script], capture_output=True, text=True)
print(p.stdout)
print(p.stderr)
print("exit", p.returncode)
