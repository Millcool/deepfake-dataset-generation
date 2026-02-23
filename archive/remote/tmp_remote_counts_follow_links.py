import subprocess
script = r"""
set -e
VID_DIR=/var/lib/ilanmironov@edu.hse.ru/shared/datasets/Wav2Lip_FFpp_vox2/real_videos
AUD_DIR=/var/lib/ilanmironov@edu.hse.ru/shared/datasets/Wav2Lip_FFpp_vox2/real_audio

echo -n "VID_DIR_REAL="; readlink -f "$VID_DIR" || true
echo -n "AUD_DIR_REAL="; readlink -f "$AUD_DIR" || true

echo -n "VIDEOS_MP4_COUNT="; find -L "$VID_DIR" -maxdepth 1 -type f -iname '*.mp4' | wc -l

echo -n "AUDIOS_M4A_COUNT="; find -L "$AUD_DIR" -type f -iname '*.m4a' | wc -l

echo "AUDIO_SAMPLE="; find -L "$AUD_DIR" -type f -iname '*.m4a' | head -n 5
"""

p = subprocess.run(["bash","-lc", script], capture_output=True, text=True)
print(p.stdout)
print(p.stderr)
print("exit", p.returncode)