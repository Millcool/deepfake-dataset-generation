import subprocess

def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)

pid="2950397"
sh(f"ps -p {pid} -o pid,etime,cmd || true")
sh(f"pgrep -P {pid} -a || true")
sh("ls -la /var/lib/ilanmironov@edu.hse.ru/video-retalking/preview_runs/preview_20260215_220900_vret/inputs/videos | sed -n '1,120p' || true")

