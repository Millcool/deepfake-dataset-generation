import subprocess


def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash", "-lc", cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)


ffpp_m = "/var/lib/ilanmironov@edu.hse.ru/shared/datasets/FaceForensics++_C23/Gender_divided/male/094.mp4"
ffpp_f = "/var/lib/ilanmironov@edu.hse.ru/shared/datasets/FaceForensics++_C23/Gender_divided/female/005.mp4"
orig_094 = "/var/lib/ilanmironov@edu.hse.ru/shared/datasets/FaceForensics++_C23/Original/094.mp4"
orig_005 = "/var/lib/ilanmironov@edu.hse.ru/shared/datasets/FaceForensics++_C23/Original/005.mp4"

for p in [ffpp_m, ffpp_f, orig_094, orig_005]:
    sh(
        "command -v ffprobe >/dev/null 2>&1 && "
        f"echo {p} && ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 {p} || true"
    )

