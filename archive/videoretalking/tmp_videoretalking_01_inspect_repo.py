import subprocess


def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash", "-lc", cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)
    return p.returncode


repo = "/var/lib/ilanmironov@edu.hse.ru/video-retalking"

sh(f"cd {repo} && ls -la | sed -n '1,200p'")
sh(f"cd {repo} && (test -f requirements.txt && sed -n '1,200p' requirements.txt) || true")
sh(f"cd {repo} && (test -f inference.py && sed -n '1,260p' inference.py) || true")
sh(
    f"cd {repo} && (command -v rg >/dev/null 2>&1 && rg -n \"argparse|--face|--audio|--outfile|--exp_img|--up_face|checkpoints\" -S inference.py) || true"
)

