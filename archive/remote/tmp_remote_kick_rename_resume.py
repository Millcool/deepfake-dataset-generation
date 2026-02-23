import subprocess
script = r"""
set -e
python3 /var/lib/ilanmironov@edu.hse.ru/musetalk/workspace/datasets/MuseTalk_FFpp_vox2/rename_resume.py || true
"""
p = subprocess.run(["bash","-lc", script], capture_output=True, text=True)
print(p.stdout)
print(p.stderr)
print('exit', p.returncode)