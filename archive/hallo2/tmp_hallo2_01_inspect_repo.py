import subprocess, textwrap

def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)
    return p.returncode

repo = "/var/lib/ilanmironov@edu.hse.ru/hallo2"
sh(f"cd {repo} && ls -la | sed -n '1,200p'")
sh(f"cd {repo} && ls -la scripts configs examples | sed -n '1,200p'")
sh(f"cd {repo} && sed -n '1,220p' requirements.txt")
sh(f"cd {repo} && find configs/inference -maxdepth 1 -type f -name '*.yaml' -print | sort")
sh(f"cd {repo} && sed -n '1,220p' configs/inference/long.yaml")
sh(f"cd {repo} && sed -n '1,220p' scripts/inference_long.py")
sh("nvidia-smi -L || true")
sh("ffmpeg -version | head -n 5 || true")
sh("conda --version || true")