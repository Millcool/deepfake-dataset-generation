import subprocess

def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)

repo='/var/lib/ilanmironov@edu.hse.ru/hallo2'
# locate util functions
sh(f"cd {repo} && (command -v rg >/dev/null 2>&1 && rg -n \"def tensor_to_video_batch|def merge_videos\" -S hallo/utils/util.py) || true")
sh(f"cd {repo} && sed -n '1,260p' hallo/utils/util.py")