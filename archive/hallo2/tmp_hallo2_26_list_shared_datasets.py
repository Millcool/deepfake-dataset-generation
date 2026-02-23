import subprocess

def sh(cmd: str):
  print(f"\n$ {cmd}")
  p=subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  print(p.stdout)

sh("ls -la /var/lib/ilanmironov@edu.hse.ru/shared/datasets | sed -n '1,200p' || true")