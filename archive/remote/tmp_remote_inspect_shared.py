import subprocess
script = r"""
set -e
VID_DIR=/var/lib/ilanmironov@edu.hse.ru/shared/datasets/Wav2Lip_FFpp_vox2/real_videos
AUD_DIR=/var/lib/ilanmironov@edu.hse.ru/shared/datasets/Wav2Lip_FFpp_vox2/real_audio

echo "--- vid ls -la head ---"
ls -la "$VID_DIR" | head -n 15 || true

echo "--- vid file types sample ---"
for f in 000.mp4 001.mp4 002.mp4; do
  p="$VID_DIR/$f"
  echo "PATH=$p"
  if [ -e "$p" ]; then
    stat -c "mode=%F perm=%A size=%s" "$p" || true
    if [ -L "$p" ]; then
      echo -n "readlink-> "; readlink "$p" || true
    fi
  else
    echo "MISSING"
  fi
done

echo "--- counts including symlinks ---"
if [ -d "$VID_DIR" ]; then
  echo -n "VIDEOS_FILES_OR_LINKS="; find "$VID_DIR" -maxdepth 1 \( -type f -o -type l \) | wc -l
  echo -n "VIDEOS_MP4_FILES_OR_LINKS="; find "$VID_DIR" -maxdepth 1 \( -type f -o -type l \) -iname '*.mp4' | wc -l
fi

if [ -d "$AUD_DIR" ]; then
  echo "--- audio tree sample ---"
  find "$AUD_DIR" -maxdepth 3 -type d | head -n 10 || true
  echo "--- audio file sample ---"
  find "$AUD_DIR" -type f \( -iname '*.m4a' -o -iname '*.wav' \) | head -n 10 || true
  echo "--- audio link sample ---"
  find "$AUD_DIR" -type l | head -n 10 || true
  echo -n "AUD_FILES_OR_LINKS="; find "$AUD_DIR" \( -type f -o -type l \) | wc -l
  echo -n "AUD_M4A_FILES_OR_LINKS="; find "$AUD_DIR" \( -type f -o -type l \) -iname '*.m4a' | wc -l
  echo -n "AUD_WAV_FILES_OR_LINKS="; find "$AUD_DIR" \( -type f -o -type l \) -iname '*.wav' | wc -l
fi
"""

p = subprocess.run(["bash","-lc", script], capture_output=True, text=True)
print(p.stdout)
print(p.stderr)
print("exit", p.returncode)