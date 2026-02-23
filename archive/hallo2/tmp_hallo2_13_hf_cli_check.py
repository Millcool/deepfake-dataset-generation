import subprocess

def sh(cmd: str):
    print(f"\n$ {cmd}")
    p=subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)

repo='/var/lib/ilanmironov@edu.hse.ru/hallo2'
venv='.venv_hallo2_20260215_133957'
sh(f"cd {repo} && ./{venv}/bin/python -c \"import huggingface_hub; print('huggingface_hub', huggingface_hub.__version__)\"")
sh(f"cd {repo} && ./{venv}/bin/huggingface-cli --version || true")