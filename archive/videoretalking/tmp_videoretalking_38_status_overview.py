import subprocess

def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash", "-lc", cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)

repo='/var/lib/ilanmironov@edu.hse.ru/video-retalking'
sh(f'echo REPO={repo}; [ -d {repo} ] && echo EXISTS || echo MISSING')
sh(f'cd {repo} && pwd && ls -la | sed -n "1,200p"')
sh(f'cd {repo} && ls -la logs 2>/dev/null | sed -n "1,200p" || true')
sh(f'cd {repo} && find . -maxdepth 3 -type d -name "batch_runs" -o -name "preview_runs" | sed -n "1,200p"')
sh(f'ps -eo pid,etime,cmd | grep -E "video-retalking|inference.py" | grep -v grep | sed -n "1,200p" || true')
