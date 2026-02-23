import subprocess
ROOT = "/var/lib/ilanmironov@edu.hse.ru/musetalk/workspace/datasets/MuseTalk_FFpp_vox2"
OUT = f"{ROOT}/outputs/results"
LOG = f"{ROOT}/logs/gen_1000.log"
PIDFILE = f"{ROOT}/.gen_1000.pid"

script = f"""
set -e
ROOT='{ROOT}'
OUT='{OUT}'
LOG='{LOG}'
PIDFILE='{PIDFILE}'

echo "PIDFILE:"; ls -la "$PIDFILE" || true
if [ -f "$PIDFILE" ]; then
  PID=$(cat "$PIDFILE" || true)
  echo "PID=$PID"
  ps -p "$PID" -o pid,etime,cmd || true
fi

echo "OUT_MP4_COUNT="; find "$OUT/v15" -maxdepth 1 -type f -iname '*.mp4' 2>/dev/null | wc -l || true

echo "LOG_TAIL:"; tail -n 40 "$LOG" || true
"""

p = subprocess.run(["bash","-lc", script], capture_output=True, text=True)
print(p.stdout)
print(p.stderr)
print('exit', p.returncode)