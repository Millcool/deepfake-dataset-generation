import subprocess

REPO = "/var/lib/ilanmironov@edu.hse.ru/musetalk"
ROOT = f"{REPO}/workspace/datasets/MuseTalk_FFpp_vox2"
OUTDIR = f"{ROOT}/outputs/results/v15"
MANIFEST = f"{ROOT}/metadata/manifest_1000.csv"
MANIFEST_NAMED = f"{ROOT}/metadata/manifest_1000_named.csv"
YAML_REMAIN = f"{ROOT}/metadata/inference_1000_named_remaining.yaml"
LOG = f"{ROOT}/logs/gen_1000_named.log"
PIDFILE_OLD = f"{ROOT}/.gen_1000.pid"
PIDFILE_NEW = f"{ROOT}/.gen_1000_named.pid"

bash = f"""
set -e
REPO='{REPO}'
ROOT='{ROOT}'
OUTDIR='{OUTDIR}'
MANIFEST='{MANIFEST}'
MANIFEST_NAMED='{MANIFEST_NAMED}'
YAML_REMAIN='{YAML_REMAIN}'
LOG='{LOG}'
PIDFILE_OLD='{PIDFILE_OLD}'
PIDFILE_NEW='{PIDFILE_NEW}'

# Stop the old generation process (best-effort).
if [ -f "$PIDFILE_OLD" ]; then
  PID=$(cat "$PIDFILE_OLD" || true)
  if [ -n "$PID" ] && ps -p "$PID" >/dev/null 2>&1; then
    echo "STOPPING_OLD_PID=$PID"
    kill -TERM "$PID" || true
    sleep 2
    ps -p "$PID" >/dev/null 2>&1 && sleep 2 || true
    ps -p "$PID" >/dev/null 2>&1 && echo "OLD_STILL_RUNNING" || echo "OLD_STOPPED"
  fi
fi

python3 - <<'PY'
import csv
import os
from datetime import datetime

REPO = "/var/lib/ilanmironov@edu.hse.ru/musetalk"
ROOT = f"{REPO}/workspace/datasets/MuseTalk_FFpp_vox2"
OUTDIR = f"{ROOT}/outputs/results/v15"
MANIFEST = f"{ROOT}/metadata/manifest_1000.csv"
MANIFEST_NAMED = f"{ROOT}/metadata/manifest_1000_named.csv"
YAML_REMAIN = f"{ROOT}/metadata/inference_1000_named_remaining.yaml"

os.makedirs(os.path.dirname(MANIFEST_NAMED), exist_ok=True)

rows = []
with open(MANIFEST, 'r', encoding='utf-8', newline='') as f:
    r = csv.DictReader(f)
    for row in r:
        rows.append(row)

renamed = 0
already_named = 0
missing = 0
conflicts = 0

for row in rows:
    idx = int(row['idx'])
    video_file = row['video_file']
    video_name = os.path.splitext(video_file)[0]

    rel = row['audio_src_rel'].replace('\\', '/')
    parts = [p for p in rel.split('/') if p]
    if len(parts) < 3:
        clip_name = os.path.splitext(os.path.basename(rel))[0]
    else:
        person, yt, clipfile = parts[0], parts[1], parts[-1]
        clip_id = os.path.splitext(clipfile)[0]
        clip_name = f"{person}_{yt}_{clip_id}"

    new_name = f"{video_name}_{clip_name}.mp4"
    row['result_name'] = new_name

    src = os.path.join(OUTDIR, f"fake_{idx:04d}.mp4")
    dst = os.path.join(OUTDIR, new_name)

    if os.path.exists(dst):
        already_named += 1
        if os.path.exists(src):
            conflicts += 1
        continue

    if os.path.exists(src):
        os.rename(src, dst)
        renamed += 1
    else:
        missing += 1

# Write named manifest copy (do not overwrite original).
with open(MANIFEST_NAMED, 'w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    for row in rows:
        w.writerow(row)

# Build remaining inference YAML (only tasks whose expected output does not yet exist).
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
        f.write(f"task_{idx:04d}:\n")
        f.write(f"  video_path: \"{video_path}\"\n")
        f.write(f"  audio_path: \"{audio_path}\"\n")
        f.write(f"  result_name: \"{out_name}\"\n\n")

print('RENAMED', renamed)
print('ALREADY_NAMED', already_named)
print('CONFLICTS_SRC_AND_DST', conflicts)
print('MISSING_SRC_FAKE', missing)
print('REMAIN_TASKS', len(remain))
print('MANIFEST_NAMED', MANIFEST_NAMED)
print('YAML_REMAIN', YAML_REMAIN)

with open(os.path.join(ROOT, 'metadata', 'rename_resume_report.txt'), 'w', encoding='utf-8') as f:
    f.write(datetime.utcnow().isoformat()+'Z\n')
    f.write(f"renamed={renamed}\n")
    f.write(f"already_named={already_named}\n")
    f.write(f"conflicts={conflicts}\n")
    f.write(f"missing_src_fake={missing}\n")
    f.write(f"remain_tasks={len(remain)}\n")
PY

REMAIN=$(python3 - <<'PY'
import yaml, sys
p = "'"$YAML_REMAIN"'"
try:
    import os
    print(sum(1 for line in open(p,'r',encoding='utf-8') if line.startswith('task_')))
except Exception:
    print(0)
PY
)

echo "REMAIN_TASKS_DETECTED=$REMAIN"

# Relaunch generation for remaining tasks.
if [ "$REMAIN" != "0" ]; then
  nohup bash -lc "
    set -e
    export CUDA_VISIBLE_DEVICES=1
    export MPLBACKEND=Agg
    source /var/lib/ilanmironov@edu.hse.ru/venvs/musetalk/bin/activate
    cd '$REPO'
    python -m scripts.inference \
      --inference_config '$YAML_REMAIN' \
      --result_dir '$ROOT/outputs/results' \
      --unet_model_path models/musetalkV15/unet.pth \
      --unet_config models/musetalkV15/musetalk.json \
      --version v15 \
      --gpu_id 0 \
      --use_float16 \
      --batch_size 8 \
      --use_saved_coord \
      --saved_coord
  " > "$LOG" 2>&1 &
  echo $! > "$PIDFILE_NEW"
  echo "STARTED_NEW_PID=$(cat $PIDFILE_NEW)"
  echo "NEW_LOG=$LOG"
else
  echo "NOT_RELAUNCHING_NO_REMAIN"
fi
"""

p = subprocess.run(["bash", "-lc", bash], capture_output=True, text=True)
print(p.stdout)
print(p.stderr)
print('exit', p.returncode)