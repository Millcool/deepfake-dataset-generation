import subprocess

def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)

pid="2950964"
sh(f"ps -p {pid} -o pid,etime,cmd || true")
sh(f"pgrep -P {pid} -a || true")

