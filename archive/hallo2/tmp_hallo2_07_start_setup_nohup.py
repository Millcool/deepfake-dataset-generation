import subprocess, datetime

def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)

repo = "/var/lib/ilanmironov@edu.hse.ru/hallo2"
ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
venv = f".venv_hallo2_{ts}"
log = f"logs/setup_env_{ts}.log"
pidfile = f"logs/setup_env_{ts}.pid"

cmd = f"""
cd {repo}
mkdir -p logs

nohup bash -lc 'set -euo pipefail; \
  echo START $(date -Is); \
  python3 -m venv {venv}; \
  ./{venv}/bin/python -m pip install --upgrade pip setuptools wheel; \
  ./{venv}/bin/python -m pip install torch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cu118; \
  ./{venv}/bin/python -m pip install -r requirements.txt; \
  ./{venv}/bin/python -m pip freeze > logs/pip_freeze_{ts}.txt; \
  echo DONE $(date -Is)' \
  > {log} 2>&1 < /dev/null &

echo $! > {pidfile}
echo VENV {venv}
echo LOG {log}
echo PIDFILE {pidfile}
ps -p $(cat {pidfile}) -o pid,etime,cmd || true
"""

sh(cmd)
sh(f"cd {repo} && tail -n 20 {log} || true")