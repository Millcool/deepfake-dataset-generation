import subprocess

def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash", "-lc", cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)

base='/var/lib/ilanmironov@edu.hse.ru/shared/datasets/FaceForensics++_C23'
sh(f'ls -la {base} | sed -n "1,200p"')
sh(f'find {base} -maxdepth 3 -type d | sed -n "1,200p"')
sh(f'find {base} -maxdepth 5 -type f -name "*.mp4" | head -n 20')
