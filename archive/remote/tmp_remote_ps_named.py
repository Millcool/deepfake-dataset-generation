import subprocess
script = r"""
set -e
ROOT=/var/lib/ilanmironov@edu.hse.ru/musetalk/workspace/datasets/MuseTalk_FFpp_vox2
PID=$(grep -E '^NEW_PID ' $ROOT/metadata/rename_resume_report.txt | awk '{print $2}' || true)
echo "PID=$PID"
if [ -n "$PID" ]; then
  ps -p "$PID" -o pid,etime,cmd || true
fi
"""
p = subprocess.run(["bash","-lc",script], capture_output=True, text=True)
print(p.stdout)
print(p.stderr)
print('exit', p.returncode)