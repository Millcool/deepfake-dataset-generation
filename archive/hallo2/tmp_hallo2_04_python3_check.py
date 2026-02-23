import subprocess

def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)

sh("which python3; python3 -V; python3 -c 'import sys; print(sys.executable); print(sys.version)' ")
sh("python3 -m venv --help | head -n 5")