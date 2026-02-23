import subprocess

script = r"""
set -e
python3 - <<'PY'
import csv
import os
import subprocess
from datetime import datetime

REPO = '/var/lib/ilanmironov@edu.hse.ru/musetalk'
ROOT = f'{REPO}/workspace/datasets/MuseTalk_FFpp_vox2'
OUTDIR = f'{ROOT}/outputs/results/v15'
MANIFEST = f'{ROOT}/metadata/manifest_1000_named.csv'
YAML_REMAIN = f'{ROOT}/metadata/inference_1000_named_remaining_restart.yaml'
LOG = f'{ROOT}/logs/gen_1000_named_restart.log'
PIDFILE = f'{ROOT}/.gen_1000_named.pid'
REPORT = f'{ROOT}/metadata/rename_resume_report.txt'

# Prevent duplicate launches.
pg = subprocess.run(
    ['bash', '-lc', 'pgrep -af "python -m scripts.inference" || true'],
    capture_output=True,
    text=True,
)
lines = [ln.strip() for ln in pg.stdout.splitlines() if ln.strip()]
active = [ln for ln in lines if 'scripts.inference' in ln and 'pgrep -af' not in ln]
if active:
    print('ALREADY_RUNNING', active[0])
    raise SystemExit(0)

rows = []
with open(MANIFEST, 'r', encoding='utf-8', newline='') as f:
    r = csv.DictReader(f)
    for row in r:
        rows.append(row)

remain = []
for row in rows:
    idx = int(row['idx'])
    out_name = row['result_name']
    out_path = os.path.join(OUTDIR, out_name)
    if os.path.exists(out_path):
        continue
    video_path = os.path.join(ROOT, 'inputs', 'videos', row['video_file'])
    audio_path = row['audio_wav']
    remain.append((idx, video_path, audio_path, out_name))

with open(YAML_REMAIN, 'w', encoding='utf-8') as f:
    for idx, video_path, audio_path, out_name in remain:
        f.write(f'task_{idx:04d}:\n')
        f.write(f'  video_path: "{video_path}"\n')
        f.write(f'  audio_path: "{audio_path}"\n')
        f.write(f'  result_name: "{out_name}"\n\n')

print('REMAIN_TASKS', len(remain))
if not remain:
    with open(REPORT, 'w', encoding='utf-8') as f:
        f.write(datetime.utcnow().isoformat() + 'Z\n')
        f.write('REMAIN_TASKS 0\n')
        f.write('STATUS COMPLETE\n')
    print('NOT_STARTED_ALREADY_COMPLETE')
    raise SystemExit(0)

os.makedirs(os.path.dirname(LOG), exist_ok=True)

cmd = (
    'set -e; '
    'export CUDA_VISIBLE_DEVICES=1; export MPLBACKEND=Agg; '
    'source /var/lib/ilanmironov@edu.hse.ru/venvs/musetalk/bin/activate; '
    f'cd {REPO}; '
    'nohup bash -lc "'
    f'python -m scripts.inference '
    f'--inference_config {YAML_REMAIN} '
    f'--result_dir {ROOT}/outputs/results '
    '--unet_model_path models/musetalkV15/unet.pth '
    '--unet_config models/musetalkV15/musetalk.json '
    '--version v15 --gpu_id 0 --use_float16 --batch_size 8 --use_saved_coord --saved_coord'
    f'" > {LOG} 2>&1 & echo $! > {PIDFILE}; cat {PIDFILE}'
)

p = subprocess.run(['bash', '-lc', cmd], capture_output=True, text=True)
new_pid = p.stdout.strip().splitlines()[-1] if p.stdout.strip() else ''

with open(REPORT, 'w', encoding='utf-8') as f:
    f.write(datetime.utcnow().isoformat() + 'Z\n')
    f.write(f'REMAIN_TASKS {len(remain)}\n')
    f.write(f'NEW_PID {new_pid}\n')
    f.write(f'NEW_LOG {LOG}\n')
    f.write('STATUS RUNNING\n')

print('STARTED_NEW_PID', new_pid)
print('NEW_LOG', LOG)
PY
"""

p = subprocess.run(["bash", "-lc", script], capture_output=True, text=True)
print(p.stdout)
print(p.stderr)
print("exit", p.returncode)
