import datetime
import subprocess


def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash", "-lc", cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)


repo = "/var/lib/ilanmironov@edu.hse.ru/video-retalking"
venv = ".venv_videoretalking_20260215_210503"
ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
out = f"results/smoke5_{ts}.mp4"
log = f"logs/smoke5_{ts}.log"
pidfile = f"logs/smoke5_{ts}.pid"

cmd = f"""
set -euo pipefail
cd {repo}
mkdir -p logs results

nohup bash -lc 'set -euo pipefail;
  echo START $(date -Is);
  export CUDA_VISIBLE_DEVICES=2;
  export MPLBACKEND=Agg;
  export GPEN_ENABLE_JIT_EXT=0;
  source {venv}/bin/activate;
  python inference.py --face examples/face/1.mp4 --audio examples/audio/1.wav --outfile {out};
  echo DONE $(date -Is);
' > {log} 2>&1 < /dev/null &

echo $! > {pidfile}
echo OUT {out}
echo LOG {log}
echo PID $(cat {pidfile})
"""

sh(cmd)

