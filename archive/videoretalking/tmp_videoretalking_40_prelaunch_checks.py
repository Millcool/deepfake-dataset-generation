import subprocess

def sh(cmd):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)

repo='/var/lib/ilanmironov@edu.hse.ru/video-retalking'
venv=f'{repo}/.venv_videoretalking_20260215_210503'
sh(f'cd {repo} && pwd')
sh(f'cd {repo} && {venv}/bin/python -V')
sh('nvidia-smi --query-gpu=index,name,memory.total,memory.free --format=csv,noheader || true')
sh('df -h /var/lib/ilanmironov@edu.hse.ru | tail -n 3')
sh('ffmpeg -version | head -n 2')
