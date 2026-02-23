import subprocess
run_dir='/var/lib/ilanmironov@edu.hse.ru/video-retalking/batch_runs/gen1000_vret2_15s_20260216_105732'

def sh(cmd):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)

sh(f'tail -n 120 {run_dir}/logs/worker0.log || true')
sh(f'tail -n 120 {run_dir}/logs/worker1.log || true')
sh(f'nvidia-smi --query-compute-apps=gpu_uuid,pid,process_name,used_memory --format=csv,noheader || true')
