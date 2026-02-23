import subprocess, datetime

def sh(cmd: str):
    print(f"\n$ {cmd}")
    p=subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)

repo='/var/lib/ilanmironov@edu.hse.ru/hallo2'
venv='.venv_hallo2_20260215_133957'
ts=datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')
log=f'logs/hf_download_{ts}.log'
pidfile=f'logs/hf_download_{ts}.pid'

cmd=f"""
cd {repo}
mkdir -p logs .cache/huggingface

nohup bash -lc 'set -euo pipefail; \
  echo START $(date -Is); \
  export HF_HOME="{repo}/.cache/huggingface"; \
  ./{venv}/bin/huggingface-cli download fudan-generative-ai/hallo2 --local-dir ./pretrained_models --resume-download; \
  echo DONE $(date -Is)' \
  > {log} 2>&1 < /dev/null &

echo $! > {pidfile}
echo LOG {log}
echo PIDFILE {pidfile}
ps -p $(cat {pidfile}) -o pid,etime,cmd || true
"""

sh(cmd)