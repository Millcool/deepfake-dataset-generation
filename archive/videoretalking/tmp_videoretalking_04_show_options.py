import subprocess


def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash", "-lc", cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)


repo = "/var/lib/ilanmironov@edu.hse.ru/video-retalking"

sh(
    f"cd {repo} && "
    "(command -v rg >/dev/null 2>&1 && rg -n \"def options\\(\" -S utils/inference_utils.py) "
    "|| (grep -n \"def options\" utils/inference_utils.py || true)"
)
sh(f"cd {repo} && echo '=== utils/inference_utils.py options() ===' && sed -n '1,140p' utils/inference_utils.py")
