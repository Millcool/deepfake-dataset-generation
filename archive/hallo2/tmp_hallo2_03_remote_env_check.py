import subprocess

def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)

sh("which python; python -V; python -c 'import sys; print(sys.executable); print(sys.version)'")
sh("which pip; pip -V || true")
sh("nvidia-smi | sed -n '1,60p'")
sh("nvcc --version || true")
sh("df -h /var/lib/private/ilanmironov@edu.hse.ru | sed -n '1,20p'")
sh("gcc --version | head -n 2 || true")