import subprocess
script = r"""
set -e
ROOT=/var/lib/ilanmironov@edu.hse.ru/musetalk/workspace/datasets/MuseTalk_FFpp_vox2
OUT=$ROOT/outputs/results/v15
LOG=$ROOT/logs/gen_1000.log
PIDFILE=$ROOT/.gen_1000.pid

PID=""; [ -f "$PIDFILE" ] && PID=$(cat "$PIDFILE" || true)
[ -n "$PID" ] && ps -p "$PID" -o pid,etime,cmd || true

DONE=$(find "$OUT" -maxdepth 1 -type f -name 'fake_*.mp4' 2>/dev/null | wc -l || true)
echo "DONE=$DONE"
echo "LEFT=$((1000-DONE))"
ls -1t "$OUT"/fake_*.mp4 2>/dev/null | head -n 1 | xargs -r stat -c 'NEWEST=%n MTIME=%y SIZE=%s' || true

tail -n 10 "$LOG" || true
"""

p = subprocess.run(["bash","-lc", script], capture_output=True, text=True)
print(p.stdout)
print(p.stderr)
print('exit', p.returncode)