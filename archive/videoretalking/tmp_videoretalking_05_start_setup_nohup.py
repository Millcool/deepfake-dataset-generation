import datetime
import subprocess


def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash", "-lc", cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)


repo = "/var/lib/ilanmironov@edu.hse.ru/video-retalking"
ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
venv = f".venv_videoretalking_{ts}"
log = f"logs/setup_{ts}.log"
pidfile = f"logs/setup_{ts}.pid"

cmd = f"""
set -euo pipefail
cd {repo}
mkdir -p logs

nohup bash -lc 'set -euo pipefail;
  echo START $(date -Is);
  python3 -m venv {venv};
  source {venv}/bin/activate;
  python -V;
  pip -V;
  pip install -U pip setuptools wheel;
  # Torch build compatible with modern drivers (CUDA 12.x driver is OK for cu121 wheel).
  pip install --index-url https://download.pytorch.org/whl/cu121 torch==2.2.2 torchvision==0.17.2;
  pip install -r requirements.txt;
  # Inference-time deps not listed in requirements.txt
  pip install opencv-python==4.8.1.78 pillow==10.2.0 tqdm==4.66.2 scipy==1.10.1;
  echo DONE $(date -Is);
' > {log} 2>&1 < /dev/null &

echo $! > {pidfile}
echo VENV {venv}
echo LOG {log}
echo PIDFILE {pidfile}
ps -p $(cat {pidfile}) -o pid,etime,cmd || true
"""

sh(cmd)

