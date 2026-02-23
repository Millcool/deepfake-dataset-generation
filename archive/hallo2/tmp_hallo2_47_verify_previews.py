import subprocess

def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash", "-lc", cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)

repo = "/var/lib/ilanmironov@edu.hse.ru/hallo2"
run = "preview_20260215_141828"

male = f"{repo}/preview_runs/{run}/outputs/male/094/merge_video.mp4"
female = f"{repo}/preview_runs/{run}/outputs/female/005/merge_video.mp4"

sh(f"ls -la {repo}/preview_runs/{run}/outputs/male/094 || true")
sh(f"ls -la {repo}/preview_runs/{run}/outputs/female/005 || true")

sh(
    "command -v ffprobe >/dev/null 2>&1 && "
    f"ffprobe -v error -show_entries format=duration,size -of default=nw=1:nk=1 {male} || true"
)
sh(
    "command -v ffprobe >/dev/null 2>&1 && "
    f"ffprobe -v error -show_entries format=duration,size -of default=nw=1:nk=1 {female} || true"
)

sh(
    "command -v ffprobe >/dev/null 2>&1 && "
    f"ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,width,height,r_frame_rate -of default=nw=1 {male} || true"
)
sh(
    "command -v ffprobe >/dev/null 2>&1 && "
    f"ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,width,height,r_frame_rate -of default=nw=1 {female} || true"
)

print("MALE_OUT", male)
print("FEMALE_OUT", female)
