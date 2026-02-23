import subprocess


def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash", "-lc", cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)


repo = "/var/lib/ilanmironov@edu.hse.ru/video-retalking"
run = "preview_20260215_221353_vret2"
male = f"{repo}/preview_runs/{run}/outputs/male_094.mp4"
female = f"{repo}/preview_runs/{run}/outputs/female_005.mp4"

sh(f"ls -la {male} {female} || true")
sh(
    f"command -v ffprobe >/dev/null 2>&1 && ffprobe -v error -show_entries format=duration,size -of default=nw=1:nk=1 {male} || true"
)
sh(
    f"command -v ffprobe >/dev/null 2>&1 && ffprobe -v error -show_entries format=duration,size -of default=nw=1:nk=1 {female} || true"
)
sh(
    f"command -v ffprobe >/dev/null 2>&1 && ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,width,height,r_frame_rate -of default=nw=1 {male} || true"
)
sh(
    f"command -v ffprobe >/dev/null 2>&1 && ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,width,height,r_frame_rate -of default=nw=1 {female} || true"
)

print("MALE_OUT", male)
print("FEMALE_OUT", female)

