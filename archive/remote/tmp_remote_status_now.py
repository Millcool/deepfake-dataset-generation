import subprocess
script = r"""
set -e
ROOT=/var/lib/ilanmironov@edu.hse.ru/musetalk/workspace/datasets/MuseTalk_FFpp_vox2
OUT=$ROOT/outputs/results/v15
LOG1=$ROOT/logs/gen_1000_named_restart.log
LOG2=$ROOT/logs/gen_1000_named.log

echo -n "MP4_COUNT="; find "$OUT" -maxdepth 1 -type f -name '*.mp4' | wc -l
pgrep -af "python -m scripts.inference" || true

echo "LOG1="; ls -la "$LOG1" 2>/dev/null || true
echo "LOG2="; ls -la "$LOG2" 2>/dev/null || true

echo "TAIL1:"; tail -n 20 "$LOG1" 2>/dev/null || true
echo "TAIL2:"; tail -n 20 "$LOG2" 2>/dev/null || true
"""
p = subprocess.run(["bash","-lc", script], capture_output=True, text=True)
print(p.stdout)
print(p.stderr)
print('exit', p.returncode)