import subprocess
p = subprocess.run(["bash","-lc","pgrep -af \"scripts.inference --inference_config configs/inference/preview_user.yaml\" || true"], capture_output=True, text=True)
print(p.stdout)
print('exit', p.returncode)