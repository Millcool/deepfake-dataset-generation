import subprocess

def sh(cmd: str):
  print(f"\n$ {cmd}")
  p=subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  print(p.stdout)

# Identify a couple of source videos and extract first frames for male/female selection.
# We'll pick first 20 real videos, then run insightface genderage on the extracted frames.
cmd = r'''
set -euo pipefail
repo=/var/lib/ilanmironov@edu.hse.ru/hallo2
ffpp=/var/lib/ilanmironov@edu.hse.ru/shared/datasets/FaceForensics++_C23

# Guess real videos directory
if [ -d "$ffpp/original_sequences/youtube/c23/videos" ]; then
  vids="$ffpp/original_sequences/youtube/c23/videos"
elif [ -d "$ffpp/original_sequences/youtube/c23" ]; then
  vids="$ffpp/original_sequences/youtube/c23"
elif [ -d "$ffpp/original_sequences/youtube/videos" ]; then
  vids="$ffpp/original_sequences/youtube/videos"
else
  echo "FFPP_LAYOUT_UNKNOWN"; ls -la "$ffpp" | head
  exit 0
fi

echo "VIDS_DIR $vids"

work="$repo/data_preview"
mkdir -p "$work/frames"

# Take 30 videos deterministically
ls "$vids" | grep -E '\\.(mp4|avi)$' | sort | head -n 30 > "$work/vid_list.txt"

# Extract one frame per video
while read -r v; do
  base="${v%.*}"
  out="$work/frames/${base}.jpg"
  if [ -f "$out" ]; then
    continue
  fi
  ffmpeg -hide_banner -loglevel error -y -i "$vids/$v" -frames:v 1 "$out" || true
done < "$work/vid_list.txt"

echo "frames_count $(ls -1 "$work/frames" | wc -l)"
'''
sh(cmd)