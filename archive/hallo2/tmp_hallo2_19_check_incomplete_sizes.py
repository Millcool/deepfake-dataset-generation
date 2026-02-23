import subprocess

def sh(cmd: str):
    print(f"\n$ {cmd}")
    p=subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)

repo='/var/lib/ilanmironov@edu.hse.ru/hallo2'
sh(f"cd {repo} && ls -la pretrained_models/.cache/huggingface/download/stable-diffusion-v1-5/unet 2>/dev/null | sed -n '1,120p' || true")
sh(f"cd {repo} && (find pretrained_models/.cache/huggingface/download/stable-diffusion-v1-5/unet -maxdepth 1 -type f -printf '%s %p\n' | sort -n | tail -n 10) 2>/dev/null || true")
sh(f"cd {repo} && du -sh pretrained_models/.cache/huggingface/download/stable-diffusion-v1-5/unet 2>/dev/null || true")