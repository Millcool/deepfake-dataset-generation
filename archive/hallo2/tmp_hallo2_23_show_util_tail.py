import subprocess

def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)

repo='/var/lib/ilanmironov@edu.hse.ru/hallo2'
# show the region containing tensor_to_video_batch and merge_videos
sh(f"cd {repo} && (command -v rg >/dev/null 2>&1 && rg -n \"tensor_to_video_batch\" hallo/utils/util.py | head) || true")
sh(f"cd {repo} && (command -v rg >/dev/null 2>&1 && rg -n \"merge_videos\" hallo/utils/util.py | head) || true")
sh(f"cd {repo} && sed -n '260,460p' hallo/utils/util.py")
sh(f"cd {repo} && sed -n '460,620p' hallo/utils/util.py")