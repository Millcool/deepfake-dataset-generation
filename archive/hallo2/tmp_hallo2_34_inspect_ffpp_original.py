import subprocess

def sh(cmd:str):
  print(f"\n$ {cmd}")
  p=subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  print(p.stdout)

base='/var/lib/ilanmironov@edu.hse.ru/shared/datasets/FaceForensics++_C23/Original'
sh(f"ls -la {base} | sed -n '1,120p' || true")
sh(f"find {base} -maxdepth 2 -type f -name '*.mp4' | head -n 30 || true")
sh(f"find {base} -maxdepth 2 -type f -name '*.mp4' | wc -l || true")