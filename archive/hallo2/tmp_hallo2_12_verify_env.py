import subprocess

def sh(cmd: str):
    print(f"\n$ {cmd}")
    p=subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)

repo='/var/lib/ilanmironov@edu.hse.ru/hallo2'
venv='.venv_hallo2_20260215_133957'
sh(f"cd {repo} && ls -d {venv} {venv}/bin/python logs/pip_freeze_20260215_133957.txt | sed -n '1,200p'")
sh(f"cd {repo} && ./{venv}/bin/python -c \"import torch; print('torch', torch.__version__); print('cuda', torch.version.cuda); print('is_available', torch.cuda.is_available()); print('device_count', torch.cuda.device_count())\"")
sh(f"cd {repo} && ./{venv}/bin/python -c \"import diffusers, transformers; print('diffusers', diffusers.__version__); print('transformers', transformers.__version__)\"")