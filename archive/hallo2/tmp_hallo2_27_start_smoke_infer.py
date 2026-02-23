import subprocess, datetime

def sh(cmd: str):
  print(f"\n$ {cmd}")
  p=subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  print(p.stdout)

repo='/var/lib/ilanmironov@edu.hse.ru/hallo2'
venv='.venv_hallo2_20260215_133957'
ts=datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')
smoke_cfg=f'configs/inference/smoke_{ts}.yaml'
out_dir=f'output_long/smoke_{ts}'
log=f'logs/smoke_infer_{ts}.log'
pidfile=f'logs/smoke_infer_{ts}.pid'

cmd=f"""
cd {repo}
mkdir -p logs {out_dir}

cp configs/inference/long.yaml {smoke_cfg}
# Override output directory for this run only.
sed -i "s|^save_path: .*|save_path: ./{out_dir}/|" {smoke_cfg}

nohup bash -lc 'set -euo pipefail; \
  echo START $(date -Is); \
  export CUDA_VISIBLE_DEVICES=1; \
  export PYTHONUNBUFFERED=1; \
  ./{venv}/bin/python scripts/inference_long.py \
    --config {smoke_cfg} \
    --source_image examples/reference_images/1.jpg \
    --driving_audio examples/driving_audios/1.wav \
    --audio_ckpt_dir pretrained_models/hallo2 \
    --pose_weight 1.0 --face_weight 1.0 --lip_weight 1.0 \
    --face_expand_ratio 1.2 \
    ; \
  echo DONE $(date -Is)' \
  > {log} 2>&1 < /dev/null &

echo $! > {pidfile}
echo OUTDIR {out_dir}
echo CFG {smoke_cfg}
echo LOG {log}
echo PIDFILE {pidfile}
ps -p $(cat {pidfile}) -o pid,etime,cmd || true
"""

sh(cmd)