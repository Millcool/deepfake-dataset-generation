import subprocess

def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash", "-lc", cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)

repo = "/var/lib/ilanmironov@edu.hse.ru/video-retalking"
sh(f"cd {repo} && pwd && ls -la | sed -n '1,120p'")

