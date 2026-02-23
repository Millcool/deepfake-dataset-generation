import subprocess
script = r"""
set -e
VID_DIR=/var/lib/ilanmironov@edu.hse.ru/shared/datasets/Wav2Lip_FFpp_vox2/real_videos
AUD_DIR=/var/lib/ilanmironov@edu.hse.ru/shared/datasets/Wav2Lip_FFpp_vox2/real_audio

echo "PWD=$(pwd)"
echo "DISK:"; df -h /var/lib/ilanmironov@edu.hse.ru | tail -n 2

echo "VIDEOS_DIR=$VID_DIR"
if [ -d "$VID_DIR" ]; then
  echo -n "VIDEOS_COUNT="; find "$VID_DIR" -maxdepth 1 -type f \( -iname '*.mp4' -o -iname '*.mov' -o -iname '*.mkv' \) | wc -l
  echo "VIDEOS_SAMPLE="; ls -1 "$VID_DIR" | head -n 5
else
  echo "MISSING_VIDEOS_DIR"
fi

echo "AUDIOS_DIR=$AUD_DIR"
if [ -d "$AUD_DIR" ]; then
  echo -n "AUDIOS_M4A_COUNT="; find "$AUD_DIR" -type f -iname '*.m4a' | wc -l
  echo -n "AUDIOS_WAV_COUNT="; find "$AUD_DIR" -type f -iname '*.wav' | wc -l
  echo "AUDIOS_SAMPLE="; find "$AUD_DIR" -type f \( -iname '*.m4a' -o -iname '*.wav' \) | head -n 5
else
  echo "MISSING_AUDIOS_DIR"
fi
"""

p = subprocess.run(["bash","-lc", script], capture_output=True, text=True)
print(p.stdout)
print(p.stderr)
print("exit", p.returncode)