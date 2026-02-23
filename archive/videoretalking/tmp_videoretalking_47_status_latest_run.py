import subprocess

def sh(cmd):
    p = subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(f"\n$ {cmd}\n{p.stdout}")

repo='/var/lib/ilanmironov@edu.hse.ru/video-retalking'
sh(f'cd {repo} && ls -1 batch_runs | tail -n 10')
sh(f'cd {repo} && latest=$(ls -1dt batch_runs/* 2>/dev/null | head -n 1); echo LATEST_RUN=$latest; [ -n "$latest" ] && ls -la "$latest/status" | sed -n "1,200p"')
