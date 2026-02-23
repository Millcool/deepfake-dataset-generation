import subprocess

def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)

repo="/var/lib/ilanmironov@edu.hse.ru/video-retalking"
run="preview_20260215_221353_vret2"
sh(f"cd {repo} && ffmpeg -y -v warning -t 4 -i preview_runs/{run}/inputs/videos/005.mp4 -an -c:v libx264 -preset veryfast -crf 20 preview_runs/{run}/inputs/videos/005_4s.mp4; echo RET=$?; ls -la preview_runs/{run}/inputs/videos | sed -n '1,120p'")

