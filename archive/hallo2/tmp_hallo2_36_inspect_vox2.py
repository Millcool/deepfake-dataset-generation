import subprocess

def sh(cmd:str):
  print(f"\n$ {cmd}")
  p=subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  print(p.stdout)

vox='/var/lib/ilanmironov@edu.hse.ru/shared/datasets/vox2_test_aac'
sh(f"ls -1 {vox} | head -n 10")
sh(f"first=$(ls -1 {vox} | head -n 1); echo FIRST $first; ls -1 {vox}/$first | head -n 10")
sh(f"first=$(ls -1 {vox} | head -n 1); clip=$(ls -1 {vox}/$first | head -n 1); echo CLIP $clip; ls -1 {vox}/$first/$clip | head -n 10")