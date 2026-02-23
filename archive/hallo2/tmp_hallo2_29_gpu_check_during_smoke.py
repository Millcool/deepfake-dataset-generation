import subprocess

def sh(cmd: str):
  print(f"\n$ {cmd}")
  p=subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  print(p.stdout)

sh("nvidia-smi | sed -n '1,120p'")