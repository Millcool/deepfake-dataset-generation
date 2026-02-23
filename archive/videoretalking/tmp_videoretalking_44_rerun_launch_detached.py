import subprocess
run_dir='/var/lib/ilanmironov@edu.hse.ru/video-retalking/batch_runs/gen1000_vret2_15s_20260216_105732'
repo='/var/lib/ilanmironov@edu.hse.ru/video-retalking'
cmd = f'cd {repo} && setsid nohup bash {run_dir}/launch.sh > {run_dir}/logs/main_launch_rerun.log 2>&1 < /dev/null & echo $! > {run_dir}/status/main_launch_rerun.pid'
p = subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
print(p.stdout)
print('RC', p.returncode)
