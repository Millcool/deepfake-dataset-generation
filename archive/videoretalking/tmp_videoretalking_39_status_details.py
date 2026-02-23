import subprocess

def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)

repo='/var/lib/ilanmironov@edu.hse.ru/video-retalking'
sh(f'cd {repo} && find . -maxdepth 5 -type f -name "*.mp4" | sed -n "1,200p"')
sh(f'cd {repo} && find . -maxdepth 6 -type f -name "*.mp4" | wc -l')
sh(f'cd {repo} && grep -R -n "gen_1000\|batch\|1000" logs 2>/dev/null | sed -n "1,120p" || true')
sh(f'cd {repo} && ls -la preview_runs/preview_20260215_221353_vret2/outputs 2>/dev/null | sed -n "1,80p" || true')
