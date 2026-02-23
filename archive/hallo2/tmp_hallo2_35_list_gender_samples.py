import subprocess

def sh(cmd:str):
  print(f"\n$ {cmd}")
  p=subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  print(p.stdout)

base='/var/lib/ilanmironov@edu.hse.ru/shared/datasets/FaceForensics++_C23/Gender_divided'
sh(f"ls -1 {base}/male | sort | head -n 20")
sh(f"ls -1 {base}/female | sort | head -n 20")