import subprocess

def sh(cmd: str):
  print(f"\n$ {cmd}")
  p=subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  print(p.stdout)

repo='/var/lib/ilanmironov@edu.hse.ru/hallo2'
sh(f"cd {repo} && (command -v rg >/dev/null 2>&1 && rg -n \"ArgumentParser\(|add_argument\(\" scripts/inference_long.py | head -n 80) || true")
sh(f"cd {repo} && tail -n 120 scripts/inference_long.py")