import subprocess
ROOT = "/var/lib/ilanmironov@edu.hse.ru/musetalk/workspace/datasets/MuseTalk_FFpp_vox2"
REPO = "/var/lib/ilanmironov@edu.hse.ru/musetalk"
CFG = f"{ROOT}/metadata/inference_1000.yaml"
OUT = f"{ROOT}/outputs/results"
LOG = f"{ROOT}/logs/gen_1000.log"
PIDFILE = f"{ROOT}/.gen_1000.pid"

script = f"""
set -e
REPO='{REPO}'
ROOT='{ROOT}'
CFG='{CFG}'
OUT='{OUT}'
LOG='{LOG}'
PIDFILE='{PIDFILE}'

mkdir -p "$OUT" "$ROOT/logs"

# Run in background. Use physical GPU1 via CUDA_VISIBLE_DEVICES.
nohup bash -lc "
  set -e
  export CUDA_VISIBLE_DEVICES=1
  export MPLBACKEND=Agg
  source /var/lib/ilanmironov@edu.hse.ru/venvs/musetalk/bin/activate
  cd '$REPO'
  python -m scripts.inference \
    --inference_config '$CFG' \
    --result_dir '$OUT' \
    --unet_model_path models/musetalkV15/unet.pth \
    --unet_config models/musetalkV15/musetalk.json \
    --version v15 \
    --gpu_id 0 \
    --use_float16 \
    --batch_size 8 \
    --use_saved_coord \
    --saved_coord
" > "$LOG" 2>&1 &

echo $! > "$PIDFILE"
echo "STARTED_PID=$(cat $PIDFILE)"
echo "LOG=$LOG"
"""

p = subprocess.run(["bash","-lc", script], capture_output=True, text=True)
print(p.stdout)
print(p.stderr)
print('exit', p.returncode)