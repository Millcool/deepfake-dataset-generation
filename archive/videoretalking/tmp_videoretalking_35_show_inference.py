import pathlib
import textwrap
import subprocess

def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)

repo='/var/lib/ilanmironov@edu.hse.ru/video-retalking'
sh(f'sed -n "1,260p" {repo}/inference.py')
