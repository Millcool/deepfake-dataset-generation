import subprocess
script = r"""
set -e
LOG=/var/lib/ilanmironov@edu.hse.ru/musetalk/workspace/datasets/MuseTalk_FFpp_vox2/logs/gen_1000_named.log
ls -la $LOG || true
tail -n 80 $LOG || true
"""
p = subprocess.run(["bash","-lc",script], capture_output=True, text=True)
print(p.stdout)
print(p.stderr)
print('exit', p.returncode)