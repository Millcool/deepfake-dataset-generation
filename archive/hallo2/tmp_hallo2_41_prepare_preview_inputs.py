import subprocess, datetime

def sh(cmd:str):
  print(f"\n$ {cmd}")
  p=subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  print(p.stdout)

repo='/var/lib/ilanmironov@edu.hse.ru/hallo2'
ffpp_gender='/var/lib/ilanmironov@edu.hse.ru/shared/datasets/FaceForensics++_C23/Gender_divided'
vox='/var/lib/ilanmironov@edu.hse.ru/shared/datasets/vox2_test_aac'

ts=datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')
run=f'preview_{ts}'

male_i=94
female_i=5
male_mp4=f"{ffpp_gender}/male/{male_i:03}.mp4"
female_mp4=f"{ffpp_gender}/female/{female_i:03}.mp4"

cmd=f"""
set -euo pipefail
cd {repo}
mkdir -p preview_runs/{run}/inputs preview_runs/{run}/inputs/images preview_runs/{run}/inputs/audios preview_runs/{run}/outputs logs

# Copy target videos (read-only source; work only on repo-local copies)
cp -n {male_mp4} preview_runs/{run}/inputs/{male_i:03}.mp4
cp -n {female_mp4} preview_runs/{run}/inputs/{female_i:03}.mp4

# Extract centered square first frame
ffmpeg -hide_banner -loglevel error -y -i preview_runs/{run}/inputs/{male_i:03}.mp4 -frames:v 1 \
  -vf "crop='min(iw,ih)':'min(iw,ih)':(iw-min(iw,ih))/2:(ih-min(iw,ih))/2,scale=512:512" \
  preview_runs/{run}/inputs/images/{male_i:03}.jpg

ffmpeg -hide_banner -loglevel error -y -i preview_runs/{run}/inputs/{female_i:03}.mp4 -frames:v 1 \
  -vf "crop='min(iw,ih)':'min(iw,ih)':(iw-min(iw,ih))/2:(ih-min(iw,ih))/2,scale=512:512" \
  preview_runs/{run}/inputs/images/{female_i:03}.jpg

echo RUN {run}
echo MALE_I {male_i} {male_mp4}
echo FEMALE_I {female_i} {female_mp4}
"""
sh(cmd)

# Inspect vox2 layout quickly
sh(f"ls -1 {vox} | head -n 5")
sh(f"first=$(ls -1 {vox} | head -n 1); echo FIRST $first; ls -1 {vox}/$first | head -n 5")
sh(f"first=$(ls -1 {vox} | head -n 1); clip=$(ls -1 {vox}/$first | head -n 1); echo CLIP $clip; ls -1 {vox}/$first/$clip | head -n 5")