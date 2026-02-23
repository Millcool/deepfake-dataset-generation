import subprocess
ROOT = "/var/lib/ilanmironov@edu.hse.ru/musetalk/workspace/datasets/MuseTalk_FFpp_vox2"
OUT = f"{ROOT}/outputs/results/v15"
LOG = f"{ROOT}/logs/gen_1000.log"
PIDFILE = f"{ROOT}/.gen_1000.pid"

script = f"""
set -e
OUT='{OUT}'
LOG='{LOG}'
PIDFILE='{PIDFILE}'

PID=""
if [ -f "$PIDFILE" ]; then PID=$(cat "$PIDFILE" || true); fi

echo "PID=$PID"
if [ -n "$PID" ]; then
  ps -p "$PID" -o pid,etime,cmd || true
fi

COUNT=$(find "$OUT" -maxdepth 1 -type f -name 'fake_*.mp4' 2>/dev/null | wc -l || true)
LAST=$(ls -1t "$OUT"/fake_*.mp4 2>/dev/null | head -n 1 || true)

echo "DONE=$COUNT"
echo "LEFT=$((1000-COUNT))"
if [ -n "$LAST" ]; then
  echo -n "LAST_FILE="; echo "$LAST"
  stat -c 'LAST_MTIME=%y LAST_SIZE=%s' "$LAST" || true
fi

echo "LOG_TAIL:"; tail -n 30 "$LOG" || true
"""

p = subprocess.run(["bash","-lc", script], capture_output=True, text=True)
print(p.stdout)
print(p.stderr)
print('exit', p.returncode)