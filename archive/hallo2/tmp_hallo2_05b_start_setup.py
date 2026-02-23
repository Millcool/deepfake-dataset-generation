import subprocess, datetime

def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)
    return p.returncode

repo = "/var/lib/ilanmironov@edu.hse.ru/hallo2"
ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
log = f"logs/setup_env_{ts}.log"

cmd = f"""
cd {repo}
mkdir -p logs

# If a setup is already running, don't start a second one.
if [ -f logs/setup_env.pid ] && kill -0 $(cat logs/setup_env.pid) 2>/dev/null; then
  echo RUNNING_PID $(cat logs/setup_env.pid)
  ls -la logs/setup_env*.log | tail -n 5 || true
  exit 0
fi

(
  set -euo pipefail
  echo START $(date -Is)
  python3 -m venv .venv_hallo2
  ./.venv_hallo2/bin/python -m pip install --upgrade pip setuptools wheel
  ./.venv_hallo2/bin/python -m pip install torch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cu118
  ./.venv_hallo2/bin/python -m pip install -r requirements.txt
  ./.venv_hallo2/bin/python -m pip freeze > logs/pip_freeze_{ts}.txt
  echo DONE $(date -Is)
) > {log} 2>&1 &

echo $! > logs/setup_env.pid
echo LOG {log}
"""

sh(cmd)
# quick peek
sh(f"cd {repo} && tail -n 20 {log} || true")