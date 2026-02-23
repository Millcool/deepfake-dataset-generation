import subprocess

def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)

repo = "/var/lib/ilanmironov@edu.hse.ru/hallo2"
sh(f"cd {repo} && (test -f logs/setup_env.pid && echo PID $(cat logs/setup_env.pid)) || echo NO_PID")
sh(f"cd {repo} && (test -f logs/setup_env.pid && ps -p $(cat logs/setup_env.pid) -o pid,etime,cmd || true)")
sh(f"cd {repo} && ls -lat logs/setup_env_*.log | head -n 3 || true")
sh(f"cd {repo} && latest=$(ls -t logs/setup_env_*.log 2>/dev/null | head -n 1); echo LATEST $latest; tail -n 40 $latest || true")