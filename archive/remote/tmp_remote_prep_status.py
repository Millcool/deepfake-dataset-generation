import os, subprocess
ROOT = "/var/lib/ilanmironov@edu.hse.ru/musetalk/workspace/datasets/MuseTalk_FFpp_vox2"
script = f"""
set -e
ROOT='{ROOT}'
echo "ROOT=$ROOT"
ls -la "$ROOT" | head -n 50 || true

echo "DONE_FILE="; ls -la "$ROOT/.prepare_1000.done" || true

echo "PID_FILE="; ls -la "$ROOT/.prepare_1000.pid" || true
if [ -f "$ROOT/.prepare_1000.pid" ]; then
  PID=$(cat "$ROOT/.prepare_1000.pid" || true)
  echo "PID=$PID"
  ps -p "$PID" -o pid,etime,cmd || true
fi

echo "COPIED_VIDEOS="; find "$ROOT/inputs/videos" -maxdepth 1 -type f -iname '*.mp4' 2>/dev/null | wc -l || true

echo "COPIED_AUD_M4A="; find "$ROOT/inputs/audio_m4a" -type f -iname '*.m4a' 2>/dev/null | wc -l || true

echo "MADE_AUD_WAV="; find "$ROOT/inputs/audio_wav" -maxdepth 1 -type f -iname '*.wav' 2>/dev/null | wc -l || true

echo "LOG_TAIL:"; tail -n 40 "$ROOT/logs/prepare_1000.log" || true
"""

p = subprocess.run(["bash","-lc", script], capture_output=True, text=True)
print(p.stdout)
print(p.stderr)
print('exit', p.returncode)