import os
import subprocess
from pathlib import Path


def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash", "-lc", cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)
    return p.returncode


base = "/var/lib/ilanmironov@edu.hse.ru"
repo = f"{base}/video-retalking"

sh("whoami; hostname; pwd")
sh(f"ls -la {base} | sed -n '1,200p'")

if os.path.exists(repo):
    sh(f"cd {repo} && git status --porcelain=v1 || true")
    sh(f"cd {repo} && git log -1 --oneline || true")
else:
    sh(f"cd {base} && git clone https://github.com/OpenTalker/video-retalking.git video-retalking")

readme = None
for name in ["README.md", "readme.md", "README.MD"]:
    p = Path(repo) / name
    if p.exists():
        readme = str(p)
        break

if not readme:
    print("README not found in repo root")
else:
    sh(f"sed -n '1,260p' {readme}")

