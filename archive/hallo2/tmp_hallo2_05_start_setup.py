import subprocess, datetime

def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)

repo = "/var/lib/ilanmironov@edu.hse.ru/hallo2"
ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
log = f"logs/setup_env_{ts}.log"
cmd = f"cd {repo} && mkdir -p logs && ( "+ \
      "set -euo pipefail; " + \
      "echo START $(date -Is); " + \
      "python3 -m venv .venv_hallo2 || true; " + \
      "./.venv_hallo2/bin/python -m pip install --upgrade pip setuptools wheel; " + \
      "./.venv_hallo2/bin/python -m pip install torch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cu118; " + \
      "./.venv_hallo2/bin/python -m pip install -r requirements.txt; " + \
      "./.venv_hallo2/bin/python -m pip freeze > logs/pip_freeze_{ts}.txt; " + \
      "echo DONE $(date -Is)" + \
      ") > {log} 2>&1 & echo $! > logs/setup_env.pid; echo {log}"
sh(cmd)
sh(f"cd {repo} && tail -n 30 {log} || true")