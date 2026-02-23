import subprocess

def sh(cmd: str):
  print(f"\n$ {cmd}")
  p=subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  print(p.stdout)

base='/var/lib/ilanmironov@edu.hse.ru/shared/datasets/FaceForensics++_C23'
sh(f"ls -la {base} | sed -n '1,120p'")
sh(f"ls -la {base}/Gender_divided | sed -n '1,200p' || true")
sh(f"find {base}/Gender_divided -maxdepth 2 -type d | sed -n '1,200p' || true")
sh(f"find {base}/Gender_divided -maxdepth 3 -type f | head -n 40 || true")