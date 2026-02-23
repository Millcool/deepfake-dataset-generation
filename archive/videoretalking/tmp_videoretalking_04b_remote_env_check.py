import subprocess


def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash", "-lc", cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)


sh("python3 --version || true")
sh("which python3 || true")
sh("nvidia-smi | sed -n '1,120p' || true")
sh("df -h /var/lib/private/ilanmironov@edu.hse.ru | sed -n '1,20p' || true")
sh("command -v conda >/dev/null 2>&1 && conda --version || echo 'conda: not found'")
sh("command -v cmake >/dev/null 2>&1 && cmake --version | head -n 2 || echo 'cmake: not found'")
sh("command -v gcc >/dev/null 2>&1 && gcc --version | head -n 1 || echo 'gcc: not found'")

