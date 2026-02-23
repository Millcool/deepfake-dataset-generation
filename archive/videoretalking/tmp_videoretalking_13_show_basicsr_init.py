import subprocess

def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)

repo="/var/lib/ilanmironov@edu.hse.ru/video-retalking"
venv=".venv_videoretalking_20260215_210503"
bs=f"{repo}/{venv}/lib/python3.10/site-packages/basicsr"
sh(f"ls -la {bs} | sed -n '1,120p'")
sh(f"sed -n '1,120p' {bs}/__init__.py")

