import subprocess

def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash", "-lc", cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)

repo="/var/lib/ilanmironov@edu.hse.ru/video-retalking"
sh(f"cd {repo} && (command -v rg >/dev/null 2>&1 && rg -n \"basicsr\" -S . | head -n 80) || (grep -RIn \"basicsr\" . | head -n 80) || true")
