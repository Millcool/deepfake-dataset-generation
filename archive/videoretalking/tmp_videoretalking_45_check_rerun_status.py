import subprocess
run_dir='/var/lib/ilanmironov@edu.hse.ru/video-retalking/batch_runs/gen1000_vret2_15s_20260216_105732'

def sh(cmd):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)

sh(f'ls -la {run_dir}/status | sed -n "1,200p"')
sh(f'cat {run_dir}/status/main_launch_rerun.pid 2>/dev/null || true')
sh(f'PID=$(cat {run_dir}/status/main_launch_rerun.pid 2>/dev/null || true); [ -n "$PID" ] && ps -p "$PID" -o pid,etime,cmd || true')
sh(f'tail -n 120 {run_dir}/logs/main_launch_rerun.log || true')
sh(f'tail -n 120 {run_dir}/logs/prepare.log || true')
sh(f'for p in $(cat {run_dir}/status/worker0.pid 2>/dev/null) $(cat {run_dir}/status/worker1.pid 2>/dev/null); do ps -p "$p" -o pid,etime,cmd; done || true')
sh(f'find {run_dir}/outputs -maxdepth 1 -type f -name "fake_*.mp4" | wc -l')
