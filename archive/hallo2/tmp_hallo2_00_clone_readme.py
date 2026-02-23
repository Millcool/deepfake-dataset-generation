import os, subprocess, pathlib, sys

def sh(cmd: str, cwd: str | None = None):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash","-lc",cmd], cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)
    return p.returncode

base = "/var/lib/ilanmironov@edu.hse.ru"
repo = f"{base}/hallo2"

sh("whoami; hostname; pwd")
sh(f"ls -la {base} | sed -n '1,200p'")

if os.path.exists(repo):
    sh(f"cd {repo} && git status --porcelain=v1 && git rev-parse --abbrev-ref HEAD && git log -1 --oneline")
else:
    sh(f"cd {base} && git clone --recurse-submodules https://github.com/fudan-generative-vision/hallo2.git hallo2")

readme = None
for name in ["README.md","readme.md","README.MD"]:
    p = pathlib.Path(repo) / name
    if p.exists():
        readme = str(p)
        break

if not readme:
    print("README not found in repo root")
    sys.exit(0)

sh(f"sed -n '1,220p' {readme}")