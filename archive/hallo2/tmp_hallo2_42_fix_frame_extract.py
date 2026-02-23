import subprocess

def sh(cmd:str):
  print(f"\n$ {cmd}")
  p=subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  print(p.stdout)

repo='/var/lib/ilanmironov@edu.hse.ru/hallo2'
run='preview_20260215_141828'

cmd=f"""
set -euo pipefail
cd {repo}

# Re-extract frames with simpler quoting
ffmpeg -hide_banner -loglevel error -y -i preview_runs/{run}/inputs/094.mp4 -frames:v 1 \
  -vf "crop=min(iw\,ih):min(iw\,ih):(iw-min(iw\,ih))/2:(ih-min(iw\,ih))/2,scale=512:512" \
  preview_runs/{run}/inputs/images/094.jpg

ffmpeg -hide_banner -loglevel error -y -i preview_runs/{run}/inputs/005.mp4 -frames:v 1 \
  -vf "crop=min(iw\,ih):min(iw\,ih):(iw-min(iw\,ih))/2:(ih-min(iw\,ih))/2,scale=512:512" \
  preview_runs/{run}/inputs/images/005.jpg

ls -la preview_runs/{run}/inputs/images
"""
sh(cmd)