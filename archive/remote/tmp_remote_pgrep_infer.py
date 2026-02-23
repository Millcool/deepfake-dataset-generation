import subprocess
script = r"""
pgrep -af "python -m scripts.inference" || true
"""
p = subprocess.run(["bash","-lc",script], capture_output=True, text=True)
print(p.stdout)
print('exit', p.returncode)