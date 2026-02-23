import subprocess

def sh(cmd:str):
  print(f"\n$ {cmd}")
  p=subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  print(p.stdout)

# Stop latest smoke inference if still running.
cmd=r'''
set -euo pipefail
repo=/var/lib/ilanmironov@edu.hse.ru/hallo2
pidfile=$(ls -t $repo/logs/smoke_infer_*.pid 2>/dev/null | head -n 1 || true)
if [ -z "$pidfile" ]; then
  echo "NO_SMOKE_PIDFILE"
  exit 0
fi
pid=$(cat "$pidfile" || true)
echo "SMOKE_PIDFILE $pidfile"
echo "SMOKE_PARENT_PID $pid"
if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
  echo "SMOKE_RUNNING stopping..."
  # kill child processes first
  kids=$(pgrep -P "$pid" || true)
  if [ -n "$kids" ]; then
    echo "SMOKE_CHILD_PIDS $kids"
    kill $kids || true
  fi
  kill "$pid" || true
  sleep 1
fi
# best-effort kill remaining inference_long from this repo
pgrep -af "hallo2/scripts/inference_long.py" || true
'''
sh(cmd)
sh('nvidia-smi | sed -n "1,120p"')