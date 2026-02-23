import subprocess


def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash", "-lc", cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)


repo = "/var/lib/ilanmironov@edu.hse.ru/video-retalking"

sh(f"cd {repo} && echo '=== inference.py head ===' && sed -n '1,80p' inference.py")
sh(f"cd {repo} && echo '=== inference.py tail ===' && tail -n 120 inference.py")

