import subprocess

def sh(cmd:str):
    print(f"\n$ {cmd}")
    p=subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)

repo='/var/lib/ilanmironov@edu.hse.ru/hallo2'
sh(f"cd {repo} && ls -la pretrained_models/stable-diffusion-v1-5/unet | sed -n '1,50p' || true")