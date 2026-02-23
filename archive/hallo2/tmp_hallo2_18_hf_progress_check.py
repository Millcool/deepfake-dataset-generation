import subprocess

def sh(cmd: str):
    print(f"\n$ {cmd}")
    p=subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)

repo='/var/lib/ilanmironov@edu.hse.ru/hallo2'
sh(f"cd {repo} && ls -la logs/hf_download_20260215_135646.log && tail -n 3 logs/hf_download_20260215_135646.log | sed -e 's/\x1b/<ESC>/g'")
sh(f"cd {repo} && find pretrained_models -maxdepth 3 -type f 2>/dev/null | wc -l || true")
sh(f"cd {repo} && du -sh pretrained_models 2>/dev/null || true")
sh(f"cd {repo} && ls -la pretrained_models/stable-diffusion-v1-5/unet 2>/dev/null || true")