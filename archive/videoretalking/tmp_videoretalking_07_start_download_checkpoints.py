import subprocess


def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash", "-lc", cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)


repo = "/var/lib/ilanmironov@edu.hse.ru/video-retalking"
venv = ".venv_videoretalking_20260215_210503"
gdrive_folder = "https://drive.google.com/drive/folders/18rhjMpxK8LVVxf7PI6XwOidt8Vouv_H0"

cmd = f"""
set -euo pipefail
cd {repo}
mkdir -p logs checkpoints

nohup bash -lc 'set -euo pipefail;
  echo START $(date -Is);
  source {venv}/bin/activate;
  python -V;
  pip -V;
  pip install -U gdown;
  # Download official pretrained models into ./checkpoints
  gdown --folder "{gdrive_folder}" -O checkpoints;
  echo DONE $(date -Is);
' > logs/checkpoints_download.log 2>&1 < /dev/null &

echo $! > logs/checkpoints_download.pid
echo LOG logs/checkpoints_download.log
echo PID $(cat logs/checkpoints_download.pid)
"""

sh(cmd)

