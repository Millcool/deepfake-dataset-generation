import subprocess


def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash", "-lc", cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)


repo = "/var/lib/ilanmironov@edu.hse.ru/video-retalking"

sh(f"cd {repo} && echo '=== requirements.txt ===' && sed -n '1,120p' requirements.txt")
sh(
    f"cd {repo} && echo '=== inference.py argparse snippet ===' && "
    "(command -v rg >/dev/null 2>&1 && rg -n \"ArgumentParser|add_argument\\(\" inference.py | head -n 160) "
    "|| (grep -nE \"ArgumentParser|add_argument\\(\" inference.py | head -n 160)"
)
sh(
    f"cd {repo} && echo '=== inference.py checkpoints usage ===' && "
    "(command -v rg >/dev/null 2>&1 && rg -n \"checkpoints|gfpgan|realesrgan|wav2lip|dlib|face_alignment|GFPGAN\" -S inference.py | head -n 200) "
    "|| true"
)
