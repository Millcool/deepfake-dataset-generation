import subprocess

def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash", "-lc", cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)

orig='/var/lib/ilanmironov@edu.hse.ru/shared/datasets/FaceForensics++_C23/Original'
sh(f'ls -la {orig} | sed -n "1,40p"')
sh(f'ls -1 {orig} | head -n 20')
sh(f'ls -1 {orig} | tail -n 20')
